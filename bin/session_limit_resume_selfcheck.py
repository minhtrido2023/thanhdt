#!/usr/bin/env python3
"""Selfcheck: session_limit_resume.py hooks, limit_reset.py, resume_pending.py kind=session.
Runs entirely in a temp ROOT with stub notify/wake scripts — no Discord, no ccdb."""
import http.server, json, os, shutil, subprocess, sys, tempfile, threading, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


T = tempfile.mkdtemp(prefix="slr_")
os.makedirs(T + "/bin")
for f in ("session_limit_resume.py", "limit_reset.py", "resume_pending.py"):
    shutil.copy(os.path.join(HERE, f), T + "/bin/" + f)


def stub(name, body):
    p = T + "/bin/" + name
    with open(p, "w") as f:
        f.write("#!/bin/sh\n" + body + "\n")
    os.chmod(p, 0o755)


stub("notify_thread.sh", 'echo "$1" >> %s/notify.log' % T)
stub("notify.sh", ":")
REC = T + "/bus/pending_resumes/session_999.json"
CNT = T + "/state/session_resume/999"
BASE = {k: v for k, v in os.environ.items() if k not in ("JOB_ID", "DISCORD_THREAD_ID", "MIKE_ROOT")}


def hook(mode, payload, thread="999", **extra):
    env = dict(BASE, MIKE_ROOT=T, **extra)
    if thread:
        env["DISCORD_THREAD_ID"] = thread
    return subprocess.run([sys.executable, T + "/bin/session_limit_resume.py", mode],
                          input=json.dumps(payload), env=env, capture_output=True, text=True, timeout=30)


def limit(msg="You've hit your 5-hour limit · resets 3:30am (Asia/Ho_Chi_Minh)"):
    return {"error": "rate_limit", "last_assistant_message": msg}


# --- expected reset computed independently of the module
tz = ZoneInfo("Asia/Ho_Chi_Minh")
now = datetime.now(tz)
exp = now.replace(hour=3, minute=30, second=0, microsecond=0)
if exp <= now:
    exp += timedelta(days=1)
EXP = int(exp.timestamp())

sys.path.insert(0, T + "/bin")
from limit_reset import reset_epoch  # noqa: E402

check("parse ICT", reset_epoch("resets 3:30am (Asia/Ho_Chi_Minh)") == EXP)
u = datetime.now(ZoneInfo("UTC"))
e = u.replace(hour=15, minute=0, second=0, microsecond=0)
if e <= u:
    e += timedelta(days=1)
check("parse UTC no minutes", reset_epoch("hit your limit · resets 3pm (UTC)") == int(e.timestamp()))
d = datetime.now(tz) + timedelta(days=3)
w = reset_epoch("weekly limit · resets %s %d, 5pm (Asia/Ho_Chi_Minh)" % (d.strftime("%b"), d.day))
check("parse weekly dated", w == int(d.replace(hour=17, minute=0, second=0, microsecond=0).timestamp()))
check("parse none", reset_epoch("429 too many requests") is None)


def at(*a):
    return datetime(*a, tzinfo=tz)


def got(text, now):
    r = reset_epoch(text, now)
    return datetime.fromtimestamp(r, tz) if r else None


n0 = at(2026, 11, 26, 14, 0)
check("parse 12am = midnight", got("resets 12am (Asia/Ho_Chi_Minh)", n0) == at(2026, 11, 27, 0, 0))
check("parse 12pm = noon", got("resets 12pm (Asia/Ho_Chi_Minh)", n0) == at(2026, 11, 27, 12, 0))
check("parse beyond 8 days rejected", got("resets Dec 20, 5pm", n0) is None)
check("parse year rollover", got("resets Jan 1, 5pm", at(2026, 12, 30, 9, 0)) == at(2027, 1, 1, 17, 0))
check("parse unknown tz -> ICT", got("resets 5pm (Mars/Base)", n0) == at(2026, 11, 26, 17, 0))
check("parse latest of several", got("resets 3pm ... resets 6pm ... resets 4pm", n0) == at(2026, 11, 26, 18, 0))

r = hook("stopfail", limit())
rec = json.load(open(REC)) if os.path.exists(REC) else {}
check("stopfail writes record", r.returncode == 0 and rec.get("resume_at") == EXP + 600
      and rec.get("kind") == "session" and rec.get("thread_id") == "999")
check("stopfail notifies", "TỰ chạy tiếp" in open(T + "/notify.log").read())
hook("start", {"prompt": "hello"})
check("user turn drops record+counter", not os.path.exists(REC) and not os.path.exists(CNT))
hook("stopfail", limit())
hook("clear", {})
check("success drops record+counter", not os.path.exists(REC) and not os.path.exists(CNT))

for i in range(1, 4):
    hook("stopfail", limit())
    ok = os.path.exists(REC) and open(CNT).read() == str(i)
    hook("start", {"prompt": rec.get("prompt", "")})  # our own wake: counter survives
    check("auto-resume attempt %d" % i, ok and not os.path.exists(REC) and os.path.exists(CNT))
hook("stopfail", limit())
check("4th consecutive stops", not os.path.exists(REC) and "DỪNG" in open(T + "/notify.log").read())
hook("clear", {})

for name, kw in (("headless job skipped", {"extra": {"JOB_ID": "x"}}), ("no thread skipped", {"thread": ""})):
    hook("stopfail", limit(), thread=kw.get("thread", "999"), **kw.get("extra", {}))
    pend = T + "/bus/pending_resumes"
    check(name, not (os.path.isdir(pend) and os.listdir(pend)))
hook("stopfail", {"error": "server_error", "last_assistant_message": "resets 3pm (UTC)"})
check("other error skipped", not os.path.exists(REC))
hook("stopfail", limit("API Error: 429"))
check("no reset time skipped", not os.path.exists(REC))
check("no reset time is announced", "KHÔNG tự chạy tiếp" in open(T + "/notify.log").read())
r = subprocess.run([sys.executable, T + "/bin/session_limit_resume.py", "stopfail"], input="garbage",
                   env=dict(BASE, MIKE_ROOT=T, DISCORD_THREAD_ID="999"), capture_output=True, text=True, timeout=30)
check("bad payload never fails the hook", r.returncode == 0)


API = {"sessions": [], "tasks": [], "deleted": []}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, obj):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_GET(self):
        self.reply({"sessions": API["sessions"]} if "sessions" in self.path else {"tasks": API["tasks"]})

    def do_DELETE(self):
        API["deleted"].append(self.path)
        self.reply({})


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
PEND = T + "/bus/pending_resumes"
CHK = PEND + "/wake_check_999.json"
PENV = dict(BASE, CCDB_API_URL="http://127.0.0.1:%d" % srv.server_port, MIKE_UNARCHIVE_WAIT_S="0")


def poll():
    subprocess.run([sys.executable, T + "/bin/resume_pending.py"], env=PENV, timeout=60, capture_output=True)


def read(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def lines(name):
    return open(T + "/" + name).read().splitlines() if os.path.exists(T + "/" + name) else []


def make_due(path=REC):
    rec = json.load(open(path))
    rec["resume_at"] = int(time.time()) - 1
    json.dump(rec, open(path, "w"))


def reset_state():
    shutil.rmtree(PEND, ignore_errors=True)
    for f in ("wake.log", "order.log"):
        if os.path.exists(T + "/" + f):
            os.remove(T + "/" + f)
    hook("clear", {})


OK_WAKE = 'printf "%%s|%%s|%%s\\n" "$1" "$3" "$WAKE_DEBOUNCE_S" >> %s/wake.log; echo wake >> %s/order.log' % (T, T)
stub("wake_thread.sh", OK_WAKE)
stub("notify_thread.sh", 'echo "$1" >> %s/notify.log; echo notify >> %s/order.log' % (T, T))
stub("dispatch.sh", 'echo x >> %s/dispatch.log' % T)

reset_state()
hook("stopfail", limit())
os.remove(T + "/order.log")
poll()
check("not due -> no wake", os.path.exists(REC) and not lines("wake.log"))
API["sessions"] = [{"thread_id": 999, "state": "running"}]
make_due()
poll()
check("running thread -> deferred", read(REC).get("resume_at", 0) > time.time() and not lines("wake.log")
      and "dispatch_fail_count" not in read(REC))
API["sessions"] = [{"thread_id": 999, "state": "idle"}]
make_due()
poll()
w = lines("wake.log")
check("due -> wake once, no dispatch", len(w) == 1 and w[0].startswith("999|limit-999-") and w[0].endswith("|0")
      and not os.path.exists(REC) and not lines("dispatch.log"))
check("thread unarchived (notify) before wake", lines("order.log") == ["notify", "wake"])
name = read(CHK).get("task_name", "")
check("wake check queued", name == "dispatch-wake-" + w[0].split("|")[1])
poll()
check("second poll silent", len(lines("wake.log")) == 1)
make_due(CHK)
poll()
check("consumed wake -> nothing deleted", not API["deleted"] and not os.path.exists(CHK))

reset_state()
hook("stopfail", limit())
make_due()
poll()
API["tasks"] = [{"id": 7, "name": read(CHK)["task_name"]}]
make_due(CHK)
poll()
check("stuck wake -> task deleted + announced", API["deleted"] == ["/api/tasks/7"]
      and "KHÔNG chạy" in open(T + "/notify.log").read())

reset_state()
stub("wake_thread.sh", "echo down >&2; exit 1")
hook("stopfail", limit())
make_due()
poll()
check("wake failure restores record", read(REC).get("dispatch_fail_count") == 1
      and read(REC).get("resume_at", 0) > time.time() and not os.path.exists(CHK))
reset_state()
stub("wake_thread.sh", OK_WAKE)
hook("stopfail", limit())
os.chmod(T + "/bin/wake_thread.sh", 0o644)  # PermissionError inside fire()
make_due()
poll()
check("exception restores record", read(REC).get("dispatch_fail_count") == 1)

reset_state()
os.chmod(T + "/bin/wake_thread.sh", 0o755)
hook("stopfail", limit())
hook("stopfail", limit(), thread="1000")
make_due()
make_due(PEND + "/session_1000.json")
poll()
check("one session wake per tick", len(lines("wake.log")) == 1)
poll()
check("the other wakes next tick", len(lines("wake.log")) == 2)
srv.shutdown()

cfg = json.load(open(os.path.join(HERE, "..", "agents", "Mike", ".claude", "settings.json")))["hooks"]
cmds = {k: [h["command"] for g in v for h in g["hooks"] if "session_limit_resume" in h["command"]] for k, v in cfg.items()}
check("settings: stopfail detached + matcher", cmds["StopFailure"][0].startswith("setsid -f ")
      and " stopfail" in cmds["StopFailure"][0] and cfg["StopFailure"][0]["matcher"] == "rate_limit")
check("settings: start/clear wired", cmds["UserPromptSubmit"][0].endswith(" start") and cmds["Stop"][0].endswith(" clear"))

shutil.rmtree(T)
print("FAILED: %d" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
