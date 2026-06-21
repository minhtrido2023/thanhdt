#!/usr/bin/env python3
"""discover_sessions.py [--exclude name1,name2 ...]

Inventories every live Claude Code session on this account (from ~/.claude/sessions/<pid>.json,
the per-process session index) and registers each as an EXTERNAL fleet member in
mike/bus/registry/<label>.json — so Mike's fleet_status tracks them. Excluded names (e.g. `tri`,
the user's direct session) are skipped. External sessions are observe-only: Mike can see/brief them
but cannot inject KB or drive them (companion model).

Run from cron every 10 min; a session that dies stops being refreshed and ages to `dead` in 30 min.
"""
import sys, os, json, glob, datetime, re

HOME = os.path.expanduser("~")
SESS_DIR = os.path.join(HOME, ".claude", "sessions")
PROJ_DIR = os.path.join(HOME, ".claude", "projects")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DIR = os.path.join(ROOT, "bus", "registry")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def cmdline(pid):
    try:
        with open("/proc/%s/cmdline" % pid, "rb") as f:
            return f.read().decode("utf-8", "replace").split("\0")
    except Exception:
        return []


def label_and_type(parts, sess):
    """Derive a stable label + session type from argv and the session index."""
    args = [p for p in parts if p]
    for flag, typ in (("--remote-control", "remote-control"),
                      ("--resume", "resume"),
                      ("--name", "named")):
        if flag in args:
            i = args.index(flag)
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                return args[i + 1], typ
            return sess.get("name") or "?", typ
    return sess.get("name") or sess.get("sessionId", "?")[:8], sess.get("kind", "interactive")


def transcript_path(cwd, session_id):
    if not cwd or not session_id:
        return ""
    escaped = cwd.replace("/", "-")
    p = os.path.join(PROJ_DIR, escaped, session_id + ".jsonl")
    return p if os.path.exists(p) else ""


def safe(label):
    return re.sub(r"[^A-Za-z0-9_-]", "_", label) or "unknown"


def main():
    exclude = set()
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--exclude" and i + 1 < len(argv):
            exclude.update(x for x in argv[i + 1].replace(",", " ").split())
            i += 2
        else:
            i += 1

    os.makedirs(REG_DIR, exist_ok=True)
    seen = {}
    for fp in glob.glob(os.path.join(SESS_DIR, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                sess = json.load(f)
        except Exception:
            continue
        pid = sess.get("pid") or os.path.splitext(os.path.basename(fp))[0]
        if not alive(pid):
            continue
        parts = cmdline(pid)
        if not any("claude" in p for p in parts):
            continue
        label, typ = label_and_type(parts, sess)
        if label in exclude or sess.get("name") in exclude:
            continue
        lbl = safe(label)
        # de-dup if two live sessions share a label
        if lbl in seen:
            lbl = "%s_%s" % (lbl, pid)
        seen[lbl] = True

        cwd = sess.get("cwd", "")
        rec = {
            "agent_id": lbl,
            "kind": "external",
            "status": sess.get("status", "running"),
            "current_task": "%s · cwd=%s" % (typ, cwd or "?"),
            "last_heartbeat": now_iso(),
            "pid": pid,
            "session_type": typ,
            "session_id": sess.get("sessionId", ""),
            "cwd": cwd,
            "transcript": transcript_path(cwd, sess.get("sessionId", "")),
        }
        tmp = os.path.join(REG_DIR, ".%s.tmp" % lbl)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False)
        os.replace(tmp, os.path.join(REG_DIR, "%s.json" % lbl))
        print("registered external session: %-28s %-14s pid=%s" % (lbl, typ, pid))

    if not seen:
        print("no external sessions found")


if __name__ == "__main__":
    main()
