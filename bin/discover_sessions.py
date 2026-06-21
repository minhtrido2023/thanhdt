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


def latest_ai_title(tp):
    """The human-readable title Claude Code shows in its desktop 'Recents' list.

    It lives in the transcript as `{"type":"ai-title","aiTitle":"..."}` lines and is
    rewritten as the conversation evolves, so the LAST one is the current title.
    Returns None on any problem (missing file, parse error, no ai-title yet)."""
    if not tp or not os.path.exists(tp):
        return None
    title = None
    try:
        with open(tp, encoding="utf-8") as f:
            for line in f:
                if '"ai-title"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("type") == "ai-title" and e.get("aiTitle"):
                    title = e["aiTitle"]
    except Exception:
        return None
    return title


def safe(label):
    return re.sub(r"[^A-Za-z0-9_-]", "_", label) or "unknown"


def resolve(session_id):
    """session_id -> friendly label (same logic as registration). For retrofit hooks."""
    if not session_id:
        return ""
    for fp in glob.glob(os.path.join(SESS_DIR, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                sess = json.load(f)
        except Exception:
            continue
        if sess.get("sessionId") == session_id:
            pid = sess.get("pid") or os.path.splitext(os.path.basename(fp))[0]
            label, _ = label_and_type(cmdline(pid), sess)
            return safe(label)
    return ""


def main():
    argv = sys.argv[1:]
    if "--resolve" in argv:
        j = argv.index("--resolve")
        print(resolve(argv[j + 1] if j + 1 < len(argv) else ""))
        return

    exclude = set()
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
        cwd0 = sess.get("cwd", "")
        # A session running under mike/agents/<id>/ IS that child — label by <id>, kind=child.
        m = re.search(r"/mike/agents/([^/]+)/?$", cwd0)
        kind = "child" if m else "external"
        if m:
            label = m.group(1)
        if label in exclude or sess.get("name") in exclude:
            continue
        lbl = safe(label)
        # de-dup if two live sessions share a label
        if lbl in seen:
            lbl = "%s_%s" % (lbl, pid)
        seen[lbl] = True

        cwd = cwd0
        tp = transcript_path(cwd, sess.get("sessionId", ""))
        # `title` = the name the user sees in Claude Code desktop, so Mike's reports line
        # up with that UI. Named/remote/resume/child sessions are launched WITH a name and
        # the desktop shows it (the ai-title is ignored for them); anonymous interactive
        # sessions show their generated ai-title instead.
        title = sess.get("name")
        if not title and (typ in ("remote-control", "resume", "named") or kind == "child"):
            title = label
        if not title:
            title = latest_ai_title(tp)
        if not title:
            title = label
        rec = {
            "agent_id": lbl,
            "kind": kind,
            "title": title,
            "status": sess.get("status", "running"),
            "current_task": "%s · cwd=%s" % (typ, cwd or "?"),
            "last_heartbeat": now_iso(),
            "pid": pid,
            "session_type": typ,
            "session_id": sess.get("sessionId", ""),
            "cwd": cwd,
            "transcript": tp,
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
