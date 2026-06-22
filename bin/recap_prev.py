#!/usr/bin/env python3
"""recap_prev.py <cwd> <current_session_id> [n]

Prints a short recap of THIS agent's previous session — the last n user/assistant turns
of the most recent OTHER transcript in the agent's project dir — so a restarted agent
continues its own thread instead of starting blank.

Only for child agents whose cwd is under mike/agents/<id>/ (there the project dir maps 1:1
to one logical agent, so "most recent other transcript" == that agent's previous session).
For shared cwds (external/retrofit sessions) transcript identity is ambiguous → prints
nothing. Always exits 0; any problem → silent (the hook must never break a session start).
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
    if "/mike/agents/" not in cwd:          # only stable 1:1 child cwds
        return

    pdir = os.path.join(PROJ, cwd.replace("/", "-"))
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
