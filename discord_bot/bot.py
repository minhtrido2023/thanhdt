#!/usr/bin/env python3
"""Discord <-> Claude Code bridge.

Each Discord channel/thread/DM maps to its own persistent Claude Code session
running (headless, `claude -p`) in CONFIG['work_dir']. Only allowlisted Discord
user IDs are served. A message in a thread continues that thread's conversation.

Flow:  discord msg -> bot -> `claude -p --resume <sid>` -> .result -> discord
"""
import asyncio
import json
import os
from pathlib import Path

import discord

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
STATE_PATH = HERE / "state.json"

TOKEN = CONFIG["discord_token"]
ALLOWED_USERS = {int(u) for u in CONFIG.get("allowed_user_ids", [])}
ALLOWED_CHANNELS = {int(c) for c in CONFIG.get("allowed_channel_ids", [])}  # empty = any
WORK_DIR = CONFIG.get("work_dir", "/home/trido/thanhdt")
PERMISSION_MODE = CONFIG.get("permission_mode", "bypassPermissions")
MODEL = CONFIG.get("model")  # optional, e.g. "claude-opus-4-8"
CLAUDE_BIN = CONFIG.get("claude_bin", "claude")
RUN_TIMEOUT = int(CONFIG.get("timeout_seconds", 900))
MAX_TURNS = CONFIG.get("max_turns")          # optional int cap on agentic turns
REQUIRE_MENTION = bool(CONFIG.get("require_mention", False))

# ------------------------------------------------------------ state
def load_state():
    try:
        return json.loads(STATE_PATH.read_text())
    except FileNotFoundError:
        return {}

def save_state(s):
    STATE_PATH.write_text(json.dumps(s, indent=2))

state = load_state()       # {channel_id(str): claude_session_id}
locks = {}                 # channel_id(str): asyncio.Lock  (serialize per channel)

def get_lock(cid):
    return locks.setdefault(cid, asyncio.Lock())

# ------------------------------------------------------------ claude
async def run_claude(prompt, session_id):
    """Run one headless turn. Returns (session_id, reply_text)."""
    base = [CLAUDE_BIN, "-p", prompt,
            "--output-format", "json",
            "--permission-mode", PERMISSION_MODE,
            "--add-dir", WORK_DIR]
    if MODEL:
        base += ["--model", MODEL]
    if MAX_TURNS:
        base += ["--max-turns", str(MAX_TURNS)]

    async def _invoke(cmd):
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=WORK_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=RUN_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return None, "⏱️ Claude run timed out.", True
        if not out:
            msg = (err.decode(errors="replace")[:800]).strip() or f"exit {proc.returncode}"
            return session_id, f"⚠️ claude error: {msg}", True
        try:
            data = json.loads(out.decode(errors="replace"))
        except json.JSONDecodeError:
            return session_id, f"⚠️ unparseable output: {out.decode(errors='replace')[:600]}", True
        return data.get("session_id", session_id), data.get("result", "(no output)"), bool(data.get("is_error"))

    cmd = base + (["--resume", session_id] if session_id else [])
    sid, reply, err = await _invoke(cmd)
    # retry fresh ONLY if the resume target is genuinely missing (not on usage
    # limits / overload / other errors, which must surface to the user as-is).
    if err and session_id:
        low = reply.lower()
        missing = any(p in low for p in (
            "no conversation found", "conversation not found", "session not found",
            "no such session", "could not find session", "does not exist"))
        if missing:
            sid, reply, err = await _invoke(base)
    return sid, reply

# ------------------------------------------------------------ discord
def chunk(text, n=1900):
    text = text or "(no output)"
    out = []
    while len(text) > n:
        cut = text.rfind("\n", 0, n)
        if cut < n // 2:
            cut = n
        out.append(text[:cut])
        text = text[cut:]
    if text.strip():
        out.append(text)
    return out

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[bridge] online as {client.user} | work_dir={WORK_DIR} | "
          f"mode={PERMISSION_MODE} | allowed_users={sorted(ALLOWED_USERS) or 'NONE (deny-all)'}",
          flush=True)

@client.event
async def on_message(msg):
    if msg.author.bot or (client.user and msg.author.id == client.user.id):
        return
    content = (msg.content or "").strip()

    # bootstrap helper: always available so you can discover your IDs
    if content == "!whoami":
        await msg.channel.send(f"user_id: `{msg.author.id}` · channel_id: `{msg.channel.id}`")
        return

    # access control (empty allowlist = deny all)
    if msg.author.id not in ALLOWED_USERS:
        return
    if ALLOWED_CHANNELS and msg.channel.id not in ALLOWED_CHANNELS:
        return

    # optional: require an @mention in busy channels
    mentioned = client.user in msg.mentions
    if REQUIRE_MENTION and not mentioned:
        return
    if mentioned:
        content = content.replace(client.user.mention, "").replace(f"<@!{client.user.id}>", "").strip()
    if not content:
        return

    cid = str(msg.channel.id)
    if content in ("!reset", "!new"):
        state.pop(cid, None)
        save_state(state)
        await msg.channel.send("🔄 Session reset — next message starts a fresh Claude conversation.")
        return
    if content in ("!help", "!commands"):
        await msg.channel.send("I bridge this channel to Claude Code on the server.\n"
                               "`!reset` new session · `!whoami` show IDs · each thread = its own session.")
        return

    lock = get_lock(cid)
    if lock.locked():
        try:
            await msg.add_reaction("⏳")
        except discord.HTTPException:
            pass
    async with lock:
        async with msg.channel.typing():
            sid, reply = await run_claude(content, state.get(cid))
        if sid:
            state[cid] = sid
            save_state(state)
        for part in chunk(reply):
            await msg.channel.send(part)

if __name__ == "__main__":
    if not TOKEN or TOKEN.startswith("PASTE_"):
        raise SystemExit("Set discord_token in config.json first.")
    client.run(TOKEN)
