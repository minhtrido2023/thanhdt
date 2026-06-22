#!/usr/bin/env python3
"""Config helper + preflight for the Discord ⇄ Claude bridge.

  ./venv/bin/python setup.py check                 # validate everything
  ./venv/bin/python setup.py set-token  <TOKEN>    # write the bot token
  ./venv/bin/python setup.py allow      <USER_ID>  # allowlist a Discord user id
  ./venv/bin/python setup.py show                  # print current config (token masked)
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"

def _load():
    return json.loads(CONFIG.read_text())

def _save(c):
    CONFIG.write_text(json.dumps(c, indent=2))

def _mask(tok: str) -> str:
    if not tok or tok.startswith("PASTE_"):
        return "(not set)"
    return f"{tok[:6]}…{tok[-4:]} (len {len(tok)})"

def cmd_set_token(args):
    if not args:
        sys.exit("usage: setup.py set-token <TOKEN>")
    c = _load()
    c["discord_token"] = args[0].strip()
    _save(c)
    print(f"✅ token set: {_mask(c['discord_token'])}")

def cmd_allow(args):
    if not args:
        sys.exit("usage: setup.py allow <USER_ID>")
    c = _load()
    ids = [str(u) for u in c.get("allowed_user_ids", [])]
    for uid in args:
        uid = uid.strip()
        if not uid.isdigit():
            sys.exit(f"✗ '{uid}' is not a numeric Discord user id")
        if uid not in ids:
            ids.append(uid)
    c["allowed_user_ids"] = ids
    _save(c)
    print(f"✅ allowed_user_ids = {ids}")

def cmd_show(_):
    c = _load()
    safe = dict(c)
    safe["discord_token"] = _mask(c.get("discord_token", ""))
    safe.pop("_notes", None)
    print(json.dumps(safe, indent=2))

def cmd_check(_):
    c = _load()
    ok = True

    def line(good, label, detail=""):
        nonlocal ok
        ok = ok and good
        print(f"  {'✅' if good else '❌'} {label}{(' — ' + detail) if detail else ''}")

    print("Preflight:")
    tok = c.get("discord_token", "")
    line(bool(tok) and not tok.startswith("PASTE_"), "discord_token", _mask(tok))

    users = c.get("allowed_user_ids", [])
    line(bool(users), "allowed_user_ids",
         f"{users}" if users else "EMPTY = deny-all (only !whoami works)")

    wd = c.get("work_dir", "")
    line(bool(wd) and Path(wd).is_dir(), "work_dir", wd)

    cb = c.get("claude_bin", "claude")
    resolved = cb if os.path.isabs(cb) and os.path.exists(cb) else shutil.which(cb)
    line(bool(resolved), "claude_bin", resolved or f"'{cb}' not found on PATH")

    try:
        import discord  # noqa: F401
        line(True, "discord.py", "importable")
    except ImportError:
        line(False, "discord.py", "not installed — run: ./venv/bin/pip install -r requirements.txt")

    print()
    if ok:
        print("All green. Start with:  ./venv/bin/python bot.py")
    elif tok and not tok.startswith("PASTE_") and not users:
        print("Token set but no allowlist yet. Start the bot, send '!whoami' in")
        print("Discord, then:  ./venv/bin/python setup.py allow <YOUR_USER_ID>")
    else:
        print("Fix the ❌ items above, then re-run:  ./venv/bin/python setup.py check")
    sys.exit(0 if ok else 1)

COMMANDS = {
    "check": cmd_check,
    "set-token": cmd_set_token,
    "allow": cmd_allow,
    "show": cmd_show,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
