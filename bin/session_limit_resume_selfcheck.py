#!/usr/bin/env python3
"""Selfcheck: session_limit_resume.py hooks, limit_reset.py, resume_pending.py kind=session.
Runs entirely in a temp ROOT with stub notify/wake scripts — no Discord, no ccdb."""
import json, os, shutil, subprocess, sys, tempfile, time
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
    check(name, not os.path.exists(REC))
hook("stopfail", {"error": "server_error", "last_assistant_message": "resets 3pm (UTC)"})
check("other error skipped", not os.path.exists(REC))
hook("stopfail", limit("API Error: 429"))
check("no reset time skipped", not os.path.exists(REC))
r = subprocess.run([sys.executable, T + "/bin/session_limit_resume.py", "stopfail"], input="garbage",
                   env=dict(BASE, MIKE_ROOT=T, DISCORD_THREAD_ID="999"), capture_output=True, text=True, timeout=30)
check("bad payload never fails the hook", r.returncode == 0)


def poll():
    subprocess.run([sys.executable, T + "/bin/resume_pending.py"], env=BASE, timeout=60, capture_output=True)


stub("wake_thread.sh", 'printf "%%s|%%s|%%s\\n" "$1" "$3" "$WAKE_DEBOUNCE_S" >> %s/wake.log' % T)
stub("dispatch.sh", 'echo x >> %s/dispatch.log' % T)
hook("stopfail", limit())
poll()
check("not due -> no wake", os.path.exists(REC) and not os.path.exists(T + "/wake.log"))


def make_due():
    rec = json.load(open(REC))
    rec["resume_at"] = int(time.time()) - 1
    json.dump(rec, open(REC, "w"))


make_due()
poll()
log = open(T + "/wake.log").read().split("\n") if os.path.exists(T + "/wake.log") else [""]
check("due -> wake thread once, no dispatch", log[0].startswith("999|limit-999-") and log[0].endswith("|0")
      and len(log) == 2 and not os.path.exists(REC) and not os.path.exists(T + "/dispatch.log"))
poll()
check("second poll silent", len(open(T + "/wake.log").read().split("\n")) == 2)
stub("wake_thread.sh", "echo down >&2; exit 1")
hook("stopfail", limit())
make_due()
poll()
rec = json.load(open(REC)) if os.path.exists(REC) else {}
check("wake failure restores record", rec.get("dispatch_fail_count") == 1 and rec.get("resume_at", 0) > time.time())

cfg = json.load(open(os.path.join(HERE, "..", "agents", "Mike", ".claude", "settings.json")))["hooks"]
cmds = {k: [h["command"] for g in v for h in g["hooks"] if "session_limit_resume" in h["command"]] for k, v in cfg.items()}
check("settings: stopfail detached + matcher", cmds["StopFailure"][0].startswith("setsid -f ")
      and " stopfail" in cmds["StopFailure"][0] and cfg["StopFailure"][0]["matcher"] == "rate_limit")
check("settings: start/clear wired", cmds["UserPromptSubmit"][0].endswith(" start") and cmds["Stop"][0].endswith(" clear"))

shutil.rmtree(T)
print("FAILED: %d" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
