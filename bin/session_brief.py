#!/usr/bin/env python3
"""session_brief.py <session_label> [n_messages]

Prints a short, read-only summary of what a session is doing, from its transcript
(.jsonl). Resolves the label via mike/bus/registry/<label>.json (written by
discover_sessions.py) to find the transcript path, then shows the last few
user/assistant text turns. Mike uses this to answer "what is session X doing?"
without that session having to cooperate.
"""
import sys, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_DIR = os.path.join(ROOT, "bus", "registry")


def text_of(msg):
    """Extract plain text from an Anthropic-format message content."""
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
            elif t == "tool_result":
                out.append("[tool_result]")
    return " ".join(x for x in out if x).strip()


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: session_brief.py <session_label> [n_messages]\n")
        sys.exit(2)
    label = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    reg = os.path.join(REG_DIR, "%s.json" % label)
    if not os.path.exists(reg):
        sys.stderr.write("unknown session '%s' (run discover_sessions.py first). "
                         "Registry: %s\n" % (label, REG_DIR))
        sys.exit(1)
    with open(reg, encoding="utf-8") as f:
        rec = json.load(f)

    tp = rec.get("transcript", "")
    print("=== %s (%s) ===" % (label, rec.get("session_type", rec.get("kind", "?"))))
    print("status=%s  pid=%s  cwd=%s" % (rec.get("status", "?"), rec.get("pid", "?"), rec.get("cwd", "?")))
    if not tp or not os.path.exists(tp):
        print("(no transcript available)")
        return

    msgs = []
    try:
        with open(tp, encoding="utf-8") as f:
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
    except Exception as ex:
        print("(error reading transcript: %s)" % ex)
        return

    print("--- last %d turns of %d ---" % (min(n, len(msgs)), len(msgs)))
    for role, txt in msgs[-n:]:
        txt = " ".join(txt.split())
        if len(txt) > 500:
            txt = txt[:500] + " …"
        print("[%s] %s" % (role, txt))


if __name__ == "__main__":
    main()
