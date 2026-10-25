#!/usr/bin/env python3
"""Selfcheck cho prevention (b) retro 2026-10-24: dispatch.sh --bg phải in cảnh báo
"CHƯA đặt ScheduleWakeup" (cơ học, không chặn). Tĩnh + chạy helper thật, không phát job.
  python3 bin/dispatch_wakeup_hint_selfcheck.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HINT = os.path.join(HERE, "dispatch_wakeup_hint.py")
DISPATCH = os.path.join(HERE, "dispatch.sh")
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def run(args, env_extra=None):
    env = dict(os.environ)
    env.pop("DISPATCH_NO_DEPENDENT_STEP", None)
    env.pop("MIKE_WAKEUP_HINT", None)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, HINT] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def wired_in_bg_branch(text):
    """Lệnh gọi helper phải nằm trong nhánh `--bg` (từ `if [ "$bg" = "--bg" ]` tới `else` cùng cấp
    cột 0), đẩy ra stderr và không chặn (`|| true`)."""
    m = re.search(r'^if \[ "\$bg" = "--bg" \]; then\n(.*?)^else\n', text, re.S | re.M)
    if not m:
        return False, "không tìm thấy nhánh --bg"
    lines = [l for l in m.group(1).splitlines() if "dispatch_wakeup_hint.py" in l and not l.lstrip().startswith("#")]
    if len(lines) != 1:
        return False, f"{len(lines)} lệnh gọi"
    l = lines[0]
    return (">&2" in l and "|| true" in l), l.strip()


rc, out = run(["--job", "Taylor_X_1", "--delay", "300", "--from", "Mike"])
check("hint: rc=0", rc == 0)
check("hint: có 'CHƯA đặt ScheduleWakeup' + job id", "CHƯA đặt ScheduleWakeup" in out and "Taylor_X_1" in out, out)
check("hint: dùng delay gợi ý", "~300s" in out, out)
rc, out = run(["--job", "J", "--delay", ""])
check("hint: delay rỗng ⇒ rơi về ladder mặc định", rc == 0 and "~240-270s" in out, out)
rc, out = run(["--job", "J"], {"DISPATCH_NO_DEPENDENT_STEP": "1"})
check("hint: opt-out DISPATCH_NO_DEPENDENT_STEP=1 ⇒ im", rc == 0 and out == "", out)
rc, out = run(["--job", "J"], {"MIKE_WAKEUP_HINT": "off"})
check("hint: MIKE_WAKEUP_HINT=off ⇒ im", rc == 0 and out == "", out)
rc, out = run([])
check("hint: thiếu --job ⇒ không crash dispatch (rc=0)", rc == 0)

src = open(DISPATCH, encoding="utf-8").read()
ok, d = wired_in_bg_branch(src)
check("dispatch.sh: gọi helper đúng 1 lần trong nhánh --bg, >&2, || true", ok, d)
# mutation: bỏ lệnh gọi ⇒ detector phải bắt; chuyển sang nhánh sync ⇒ bắt
mut = "\n".join(l for l in src.splitlines() if "dispatch_wakeup_hint.py" not in l or l.lstrip().startswith("#"))
check("mutation: bỏ lệnh gọi ⇒ detector đỏ", not wired_in_bg_branch(mut)[0])
mut2 = src.replace("|| true\n  echo \"$pid\" > \"$ROOT/logs/.dispatch_", "\n  echo \"$pid\" > \"$ROOT/logs/.dispatch_") \
    if False else src.replace('--from "$from" >&2 || true', '--from "$from" >&2')
check("mutation: bỏ '|| true' (có thể chặn dispatch) ⇒ detector đỏ", not wired_in_bg_branch(mut2)[0])
r = subprocess.run(["bash", "-n", DISPATCH], capture_output=True, text=True)
check("dispatch.sh: bash -n sạch", r.returncode == 0, r.stderr[:200])

print("\nALL PASS" if not fails else f"\n{len(fails)} FAIL: {fails}")
sys.exit(1 if fails else 0)
