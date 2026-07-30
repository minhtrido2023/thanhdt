#!/usr/bin/env python3
"""recap_prev.py <cwd> <current_session_id> [n] [explicit_prev_session_id]

Prints a short recap of THIS agent's previous session so a restarted agent continues its
own thread instead of starting blank.

Default mode (3 args): the last n user/assistant turns of the most recent OTHER transcript
in the agent's project dir. Only safe for child agents whose cwd is under mike/agents/<id>/
AND whose cwd only ever holds sequential one-shot sessions (true for every headless-only
agent) — there "most recent other transcript" == that agent's previous session.

Explicit mode (4th arg given, non-empty): skip the mtime guess entirely and recap exactly
that session id's transcript. For cwds shared between a live daemon and headless dispatches
(Mike is the only current case — see hooks/session_start.sh's live_session_ptr.txt) the
mtime guess can pick up a same-directory headless dispatch's transcript instead of the
daemon's own prior turns; the caller tracks "my own last session id" explicitly and passes
it here instead of trusting mtime ordering.

For shared cwds (external/retrofit sessions) with neither mode applicable, transcript
identity is ambiguous → prints nothing. Always exits 0; any problem → silent (the hook must
never break a session start).
"""
import sys, os, json, glob

PROJ = os.path.join(os.path.expanduser("~"), ".claude", "projects")


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    out = []
    if isinstance(c, list):
        for b in c:
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t == "text":
                out.append(b.get("text", ""))
            elif t == "tool_use":
                out.append("[tool:%s]" % b.get("name", "?"))
    return " ".join(x for x in out if x).strip()


def main():
    if len(sys.argv) < 3:
        return
    cwd, cur = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    explicit_sid = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
    if explicit_sid:
        explicit_sid = os.path.basename(explicit_sid)  # defense-in-depth; caller passes our own ids
        if explicit_sid == cur:                         # never recap our own current transcript
            return
    if "/mike/agents/" not in cwd:          # only stable 1:1 child cwds
        return

    pdir = os.path.join(PROJ, cwd.replace("/", "-"))
    if explicit_sid:
        prev = os.path.join(pdir, explicit_sid + ".jsonl")
        if not os.path.isfile(prev):
            return
    else:
        files = [f for f in glob.glob(os.path.join(pdir, "*.jsonl"))
                 if os.path.basename(f) != cur + ".jsonl"]
        if not files:
            return
        prev = max(files, key=os.path.getmtime)

    msgs = []
    try:
        with open(prev, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("type") in ("user", "assistant") and isinstance(e.get("message"), dict):
                    txt = text_of(e["message"])
                    if txt:
                        msgs.append((e["type"], txt))
    except Exception:
        return
    if not msgs:
        return

    print("[Phiên TRƯỚC của bạn vừa làm tới đây — tiếp tục mạch này, ĐỪNG bắt đầu lại từ đầu. "
          "Tri thức bền đã ở phần KB ở trên; đây là mạch hội thoại/việc đang dở:]")
    for role, txt in msgs[-n:]:
        txt = " ".join(txt.split())
        if len(txt) > 500:
            txt = txt[:500] + " …"
        print("[%s] %s" % (role, txt))


if __name__ == "__main__":
    main()
