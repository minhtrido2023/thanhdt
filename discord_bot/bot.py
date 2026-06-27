#!/usr/bin/env python3
"""Discord <-> Claude Code bridge.

Each Discord channel/thread/DM maps to its own persistent Claude Code session
running (headless, `claude -p`) in CONFIG['work_dir']. Only allowlisted Discord
user IDs are served. A message in a thread continues that thread's conversation.

Interaction model (ported from the Slack bot, adapted to Discord):
  decide-to-reply  ->  "thinking" placeholder w/ 🛑 Stop (refreshed in place
  ~every 2.5s with the latest activity + elapsed)  ->  stream Claude (collect
  activity + stats)  ->  edit placeholder into a STATUS LINE (heaviness, no
  answer; Stop removed)  +  post the ANSWER as a SEPARATE message (so it raises
  a notification — edits don't).
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path

import discord

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
STATE_PATH = HERE / "state.json"

TOKEN = CONFIG["discord_token"]
ALLOWED_USERS = {int(u) for u in CONFIG.get("allowed_user_ids", [])}
ALLOWED_CHANNELS = {int(c) for c in CONFIG.get("allowed_channel_ids", [])}  # empty = any
# Channels where a top-level message (no @mention needed) is auto-answered.
AUTO_ENGAGE = {int(c) for c in CONFIG.get("auto_engage_channel_ids", [])}
WORK_DIR = CONFIG.get("work_dir", "/home/trido/thanhdt")
PERMISSION_MODE = CONFIG.get("permission_mode", "bypassPermissions")
MODEL = CONFIG.get("model")  # optional, e.g. "claude-opus-4-8"
CLAUDE_BIN = CONFIG.get("claude_bin", "claude")
RUN_TIMEOUT = int(CONFIG.get("timeout_seconds", 900))
MAX_TURNS = CONFIG.get("max_turns")          # optional int cap on agentic turns
PROGRESS_EVERY = float(CONFIG.get("progress_refresh_seconds", 2.5))
# Discord's hard per-message cap is 2000 chars (NOT 3500 like Slack) — keep margin.
CHUNK = int(CONFIG.get("chunk_chars", 1900))
# Threads the bot opens auto-archive after this many minutes of inactivity
# (Discord allows 60, 1440, 4320, 10080).
THREAD_ARCHIVE_MIN = int(CONFIG.get("thread_archive_minutes", 1440))

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
_handled = set()           # message ids already processed (dedup guard)

def get_lock(cid):
    return locks.setdefault(cid, asyncio.Lock())

# ------------------------------------------------------------ formatting
def pretty_model(model):
    """'claude-opus-4-8' -> 'opus-4.8'; drops trailing yyyymmdd date token."""
    if not model:
        return None
    name = model.removeprefix("claude-")
    bits = name.split("-")
    if bits and bits[-1].isdigit() and len(bits[-1]) == 8:   # drop date
        bits = bits[:-1]
    if not bits:
        return model
    family, ver = bits[0], bits[1:]
    return f"{family}-{'.'.join(ver)}" if ver else family

def fmt_tok(n):
    if n is None:
        return None
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

def fmt_status(stats, elapsed_s, is_err, stopped):
    if stopped:
        head = f"🛑 stopped after {elapsed_s}s"
    elif is_err:
        head = f"⚠️ finished with error in {elapsed_s}s"
    else:
        head = f"✅ done in {elapsed_s}s"
    parts = [head]
    if stats.get("model"):
        parts.append(pretty_model(stats["model"]))
    if stats.get("turns"):
        parts.append(f"{stats['turns']} turns")
    if stats.get("tools"):
        parts.append(f"{stats['tools']} tool calls")
    ti, to = fmt_tok(stats.get("tok_in")), fmt_tok(stats.get("tok_out"))
    if ti and to:
        parts.append(f"{ti}→{to} tok")
    if stats.get("cost") is not None:
        parts.append(f"${stats['cost']:.2f}")
    return " · ".join(parts)

def first_line(txt, n=80):
    line = next((l for l in (txt or "").splitlines() if l.strip()), "")
    line = " ".join(line.split())
    return (line[:n] + "…") if len(line) > n else line

def brief_tool(name, inp):
    inp = inp if isinstance(inp, dict) else {}
    hint = ""
    for k in ("command", "file_path", "path", "pattern", "query", "url", "prompt"):
        if k in inp and inp[k]:
            hint = os.path.basename(str(inp[k])) if k in ("file_path", "path") else str(inp[k])
            break
    hint = " ".join(hint.split())[:50]
    return f"🔧 {name}({hint})" if hint else f"🔧 {name}"

# ------------------------------------------------------------ claude (streaming)
async def run_claude(prompt, session_id, on_progress=None, cancel=None):
    """Stream one headless turn.

    on_progress(text): called with the latest activity string as events arrive.
    cancel: object with .proc (set to the live subprocess) and .stopped (bool).
    Returns (session_id, reply_text, is_err, stats).
    """
    base = [CLAUDE_BIN, "-p", prompt,
            "--output-format", "stream-json", "--verbose",
            "--permission-mode", PERMISSION_MODE,
            "--add-dir", WORK_DIR]
    if MODEL:
        base += ["--model", MODEL]
    if MAX_TURNS:
        base += ["--max-turns", str(MAX_TURNS)]

    async def _emit(text):
        if on_progress:
            await on_progress(text)

    async def _invoke(cmd):
        stats = {"tools": 0, "model": MODEL, "turns": None, "cost": None,
                 "tok_in": None, "tok_out": None}
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=WORK_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        if cancel is not None:
            cancel.proc = proc
        sid, reply, is_err = session_id, None, False
        stderr_tail = b""
        stderr_task = asyncio.create_task(proc.stderr.read())
        try:
            while True:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=RUN_TIMEOUT)
                if not line:
                    break
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = ev.get("type")
                if t == "system" and ev.get("subtype") == "init":
                    stats["model"] = ev.get("model") or stats["model"]
                elif t == "assistant":
                    m = ev.get("message", {})
                    stats["model"] = m.get("model") or stats["model"]
                    for b in m.get("content", []):
                        bt = b.get("type")
                        if bt == "text" and b.get("text", "").strip():
                            await _emit(f"💬 {first_line(b['text'])}")
                        elif bt == "tool_use":
                            stats["tools"] += 1
                            await _emit(brief_tool(b.get("name", "tool"), b.get("input")))
                elif t == "result":
                    stats["turns"] = ev.get("num_turns")
                    stats["cost"] = ev.get("total_cost_usd")
                    u = ev.get("usage", {}) or {}
                    stats["tok_in"] = u.get("input_tokens")
                    stats["tok_out"] = u.get("output_tokens")
                    sid = ev.get("session_id", sid)
                    reply = ev.get("result", reply)
                    is_err = bool(ev.get("is_error"))
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            stderr_task.cancel()
            return None, "⏱️ Claude run timed out.", True, stats

        await proc.wait()
        try:
            stderr_tail = await stderr_task
        except asyncio.CancelledError:
            pass
        if reply is None:
            if cancel is not None and cancel.stopped:
                return sid, "🛑 Stopped.", True, stats
            msg = (stderr_tail.decode(errors="replace")[:800]).strip() or f"exit {proc.returncode}"
            return sid, f"⚠️ claude error: {msg}", True, stats
        return sid, reply, is_err, stats

    cmd = base + (["--resume", session_id] if session_id else [])
    sid, reply, err, stats = await _invoke(cmd)
    # retry fresh ONLY if the resume target is genuinely missing (not on usage
    # limits / overload / a user Stop, which must surface as-is).
    if err and session_id and not (cancel is not None and cancel.stopped):
        low = (reply or "").lower()
        if any(p in low for p in (
                "no conversation found", "conversation not found", "session not found",
                "no such session", "could not find session", "does not exist")):
            sid, reply, err, stats = await _invoke(base)
    return sid, reply, err, stats

# ------------------------------------------------------------ discord
def chunk(text, n=None):
    n = n or CHUNK
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

def thread_name(prompt, n=60):
    """Short, single-line title for an auto-created thread (Discord cap 100)."""
    name = " ".join((prompt or "").split())[:n].strip()
    return name or "Claude"

def strip_mention(content):
    """Remove the bot's @mention tokens from the message text."""
    if client.user is None:
        return content.strip()
    return (content
            .replace(f"<@{client.user.id}>", "")
            .replace(f"<@!{client.user.id}>", "")
            .strip())

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

class StopView(discord.ui.View):
    """A single 🛑 Stop button that kills the running claude subprocess.

    Only allowlisted users may stop. Lives as long as the run (timeout=None);
    the run code removes it (view=None) once finished.
    """
    def __init__(self, cancel):
        super().__init__(timeout=None)
        self.cancel = cancel

    @discord.ui.button(label="Stop", emoji="🛑", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in ALLOWED_USERS:
            await interaction.response.send_message("Not allowed.", ephemeral=True)
            return
        self.cancel.stopped = True
        proc = getattr(self.cancel, "proc", None)
        if proc is not None and proc.returncode is None:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
        button.disabled = True
        await interaction.response.edit_message(view=self)

@client.event
async def on_ready():
    print(f"[bridge] online as {client.user} | work_dir={WORK_DIR} | "
          f"mode={PERMISSION_MODE} | allowed_users={sorted(ALLOWED_USERS) or 'NONE (deny-all)'}",
          flush=True)

@client.event
async def on_message(msg):
    if msg.author.bot or (client.user and msg.author.id == client.user.id):
        return
    if msg.id in _handled:                      # dedup guard
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

    is_dm = msg.guild is None
    is_thread = isinstance(msg.channel, discord.Thread)
    mentioned = client.user in msg.mentions
    # An "engaged" thread is one we already hold a session for — continue it
    # without requiring a fresh @mention.
    engaged_thread = is_thread and str(msg.channel.id) in state
    auto_engage = (not is_thread) and (msg.channel.id in AUTO_ENGAGE)

    # TRIGGER MATRIX: DM always · @mention always · engaged thread · auto-engage
    # channel. Otherwise (incl. a message tagging someone else) -> ignore.
    if not (is_dm or mentioned or engaged_thread or auto_engage):
        return

    if mentioned:
        content = strip_mention(content)
    if not content:
        await msg.channel.send("👋 Tag me with a request, e.g. `@me what changed in git today?`")
        return

    # ---- ops command: restart the bot process (allowlisted users only) ----
    # Detached + delayed so THIS reply posts before the bot that posts it is
    # replaced. start_new_session=True puts restart.sh in its own session, so the
    # pkill it issues against the python bot can't take restart.sh down with it.
    if content == "!restart":
        await msg.channel.send("♻️ Restarting in ~20s — this reply posts first, "
                               "then the bot process is replaced. Back shortly.")
        subprocess.Popen(
            [str(HERE / "restart.sh"), "--delay", "20"],
            cwd=str(HERE),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
        return

    _handled.add(msg.id)
    if len(_handled) > 2000:
        _handled.clear()

    # Where the reply goes:
    #   • DM             -> the DM channel
    #   • inside a thread -> that same thread
    #   • in a channel    -> a NEW thread anchored to the user's message
    if is_dm or is_thread:
        target = msg.channel
    else:
        try:
            target = await msg.create_thread(
                name=thread_name(content),
                auto_archive_duration=THREAD_ARCHIVE_MIN,
            )
        except discord.Forbidden:
            await msg.channel.send(
                "⚠️ I need **Create Public Threads** and **Send Messages in Threads** "
                "to answer in a thread. Grant those to my role (Server Settings → Roles), "
                "or tag me inside an existing thread."
            )
            return
        except discord.HTTPException as e:
            await msg.channel.send(f"⚠️ couldn't create a thread: {e}")
            return

    cid = str(target.id)
    if content in ("!reset", "!new"):
        state.pop(cid, None)
        save_state(state)
        await target.send("🔄 Session reset — next message starts a fresh Claude conversation.")
        return
    if content in ("!help", "!commands"):
        await target.send("Tag me with a request. In a channel I reply in a new thread; "
                          "in a thread I continue it.\n"
                          "🛑 Stop cancels a run · `!reset` new session · `!restart` "
                          "restart bot · `!whoami` show IDs.")
        return

    lock = get_lock(cid)
    if lock.locked():
        try:
            await msg.add_reaction("⏳")
        except discord.HTTPException:
            pass
    async with lock:
        await _serve(msg, target, cid, content, is_thread)

async def _serve(msg, target, cid, content, is_thread):
    """Placeholder (live progress + Stop) -> stream -> status line + answer."""
    loop = asyncio.get_event_loop()
    cancel = type("C", (), {"proc": None, "stopped": False})()
    view = StopView(cancel)
    activity = {"text": "thinking…"}

    async def on_progress(text):
        activity["text"] = text

    placeholder = await target.send("🤔 thinking…", view=view)
    started = loop.time()

    async def refresher():
        while True:
            await asyncio.sleep(PROGRESS_EVERY)
            elapsed = int(loop.time() - started)
            try:
                await placeholder.edit(content=f"🤔 {activity['text']}  ·  {elapsed}s", view=view)
            except discord.HTTPException:
                pass

    refresh_task = asyncio.create_task(refresher())
    try:
        sid, reply, is_err, stats = await run_claude(content, state.get(cid), on_progress, cancel)
    finally:
        refresh_task.cancel()

    if sid:
        state[cid] = sid
        save_state(state)

    elapsed = int(loop.time() - started)
    # Placeholder -> fixed STATUS LINE (heaviness, no answer; Stop removed).
    try:
        await placeholder.edit(content=fmt_status(stats, elapsed, is_err, cancel.stopped), view=None)
    except discord.HTTPException:
        pass

    # ANSWER as a SEPARATE message (raises a notification; edits don't).
    for i, part in enumerate(chunk(reply)):
        if i == 0 and is_thread:
            await target.send(part, reference=msg, mention_author=False)
        else:
            await target.send(part)

if __name__ == "__main__":
    if not TOKEN or TOKEN.startswith("PASTE_"):
        raise SystemExit("Set discord_token in config.json first.")
    client.run(TOKEN)
