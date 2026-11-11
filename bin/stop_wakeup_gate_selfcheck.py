#!/usr/bin/env python3
"""Selfcheck hooks/stop.sh G2 (transcript-based ScheduleWakeup gate). Chay: python3 bin/stop_wakeup_gate_selfcheck.py
Moi ca dung transcript tong hop + chay hook that (id truyen $1). Cac ca 'phai chan' la mutation
guard: neu G2 bi go, ca 1 do. Cac ca 'khong chan' bao ve khoi chan nham."""
import json, os, subprocess, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "stop.sh")

def user(text): return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}}
def tool_result(): return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]}}
def bash(cmd): return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "b", "name": "Bash", "input": {"command": cmd}}]}}
def wake(): return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "w", "name": "ScheduleWakeup", "input": {}}]}}
def qop(): return {"type": "queue-operation", "operation": "enqueue"}
def text(t): return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": t}]}}

BG = 'bin/dispatch.sh Taylor "lam viec" --bg'
tasks = {"tasks": []}
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b = json.dumps(tasks).encode(); self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
srv = HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
API = f"http://127.0.0.1:{srv.server_port}/api/tasks"
DEAD = "http://127.0.0.1:9/api/tasks"

def run(recs, agent="Mike", active=False, api=API, tid="111", path_ok=True):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.jsonl")
        with open(p, "w") as f:
            for r in recs: f.write(json.dumps(r) + "\n")
        payload = json.dumps({"session_id": "s", "cwd": d, "transcript_path": p if path_ok else d + "/nope", "stop_hook_active": active})
        env = dict(os.environ, DISCORD_THREAD_ID=tid, WAGS_STOP_TASKS_API=api, MIKE_EXCLUDE="none")
        env.pop("MIKE_SKIP", None)
        r = subprocess.run(["bash", HOOK, agent], input=payload, capture_output=True, text=True, env=env, timeout=60)
    return r.returncode, ('"block"' in r.stdout)

CASES = [
    ("1 bg, khong wakeup -> CHAN", [user("hi"), bash(BG), tool_result(), text("xong")], {}, True),
    ("2 bg + ScheduleWakeup -> khong chan", [user("hi"), bash(BG), tool_result(), wake()], {}, False),
    ("3 bg --no-followup -> khong chan", [user("hi"), bash(BG + " --no-followup"), tool_result()], {}, False),
    ("4 khong dispatch -> khong chan", [user("hi"), bash("ls"), tool_result()], {}, False),
    ("5 stop_hook_active -> khong chan", [user("hi"), bash(BG)], {"active": True}, False),
    ("6 agent khac Mike -> khong chan", [user("hi"), bash(BG)], {"agent": "Wags"}, False),
    ("7 wakeup pending cho thread -> khong chan", [user("hi"), bash(BG)], {"pending": True}, False),
    ("8 transcript khong doc duoc -> fail-open", [user("hi"), bash(BG)], {"path_ok": False}, False),
    ("9 bg o luot TRUOC, luot nay sach -> khong chan", [user("a"), bash(BG), tool_result(), text("x"), user("b"), bash("ls"), tool_result()], {}, False),
    ("10 chi NHAC toi dispatch --bg trong tham so khac -> khong chan", [user("hi"), bash('bin/notify_thread.sh 1 "dung dispatch.sh X --bg nhe"'), tool_result()], {}, False),
    ("11 khong co DISCORD_THREAD_ID (phien khong thread) van chan", [user("hi"), bash(BG)], {"tid": ""}, True),
    ("12 API pending khong truy cap duoc -> fail-open, khong chan", [user("hi"), bash(BG)], {"api": DEAD}, False),
    ("14 queue-operation GIUA bg va wakeup (cung luot) -> khong chan [ca MISS 10/11]", [user("hi"), bash(BG), tool_result(), qop(), tool_result(), wake(), text("ok"), qop()], {}, False),
    ("15 queue-operation SAU wakeup -> khong chan (khong cat doi luot)", [user("hi"), bash(BG), wake(), qop(), qop()], {}, False),
    ("13 heredoc prompt noi ve --bg, dispatch that khong bg -> khong chan", [user("hi"), bash("bin/dispatch.sh Taylor \"$(cat <<'P'\nlam gi do --bg\nP\n)\""), tool_result()], {}, False),
]
bad = 0
# audit: queue-op giua luot khong duoc cat doi luot (dung audit that qua TRANSCRIPTS override)
sys.path.insert(0, os.path.join(ROOT, "bin")); import wakeup_audit as wa
with tempfile.TemporaryDirectory() as d:
    with open(os.path.join(d, "s.jsonl"), "w") as f:
        for r in [user("hi"), dict(bash(BG), timestamp="2026-11-10T08:20:00Z"), qop(), wake(), text("x")]:
            f.write(json.dumps(r) + "\n")
    wa.TRANSCRIPTS = os.path.join(d, "*.jsonl")
    t = wa.scan_turns("2026-11-01")
    ok = len(t) == 1 and t[0]["wake"]
    bad += not ok; print(("PASS" if ok else "FAIL"), "A1 audit: queue-op khong cat doi luot (bg+wake cung luot = OK)", len(t))
for name, recs, kw, want in CASES:
    tasks["tasks"] = [{"enabled": 1, "one_shot": 1, "thread_id": "111"}] if kw.pop("pending", False) else []
    rc, blocked = run(recs, **kw)
    ok = rc == 0 and blocked == want
    bad += not ok
    print(("PASS" if ok else "FAIL"), name, f"(rc={rc} blocked={blocked})")
print("TZ=%s" % os.environ.get("TZ", "-"), "->", "ALL PASS" if not bad else f"{bad} FAIL")
sys.exit(1 if bad else 0)
