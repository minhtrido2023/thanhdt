#!/usr/bin/env python3
"""is_serving.py <agent_id>

Exit 0 if the agent is ACTUALLY serving a live session, 1 if not. This is the reliable
liveness oracle for a remote-control fleet agent — stronger than `systemctl is-active`,
which only proves the host PROCESS is alive (a host can be "Ready" yet never register a
session = the zombie state that killed Mafee, invisible to systemd).

"Serving" = Claude Code has a session record under ~/.claude/sessions/*.json whose pid is
alive and whose cwd is this agent's dir (…/mike/agents/<id>). That record is what
discover_sessions uses and what a healthy idle agent keeps; a dead/unpaired host has none.

Always decides quickly and never raises (a monitor must not crash). Unknown → exit 1.
"""
import sys, os, json, glob, re

SESS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "sessions")


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def main():
    if len(sys.argv) < 2:
        sys.exit(2)
    agent = sys.argv[1]
    want = re.compile(r"/mike/agents/%s/?$" % re.escape(agent))
    for fp in glob.glob(os.path.join(SESS_DIR, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                sess = json.load(f)
        except Exception:
            continue
        cwd = sess.get("cwd", "") or ""
        if not want.search(cwd):
            continue
        pid = sess.get("pid") or os.path.splitext(os.path.basename(fp))[0]
        if alive(pid):
            sys.exit(0)          # found a live session for this agent → serving
    sys.exit(1)                  # no live session record → not serving


if __name__ == "__main__":
    main()
