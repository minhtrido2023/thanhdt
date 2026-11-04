#!/usr/bin/env python3
"""Selfcheck đường bash khối TE của refresh_deposit_cctg_weekly.sh. Chạy: env -u TZ python3 te_weekly_bash_selfcheck.py
Trích ĐÚNG khối thật (từ '# --- TE cross-check' tới hết file) rồi chạy với PY + notify_thread.sh GIẢ trong tmpdir."""
import os, re, subprocess, sys, tempfile, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "refresh_deposit_cctg_weekly.sh")).read()
blk = src[src.index("# --- TE cross-check"):]
FAIL = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: FAIL.append(m)

tmp = tempfile.mkdtemp()
os.makedirs(f"{tmp}/mike/bin")
notif = f"{tmp}/notify.log"; args = f"{tmp}/py_args.log"; steps = f"{tmp}/steps.log"
open(f"{tmp}/mike/bin/notify_thread.sh", "w").write(f'#!/bin/bash\necho "$1" >> {notif}\n'); os.chmod(f"{tmp}/mike/bin/notify_thread.sh", 0o755)
fakepy = f"{tmp}/fakepy.sh"
open(fakepy, "w").write(f'#!/bin/bash\necho "$@" >> {args}\nexit ${{FAKE_TE_RC:-0}}\n'); os.chmod(fakepy, 0o755)

def run(te_rc, dry=0, trend_rc=0, sbv_rc=0):
    for f in (notif, args, steps, f"{tmp}/log"): 
        if os.path.exists(f): os.remove(f)
    # trend + sbv giả lập đã chạy TRƯỚC khối TE (steps.log chứng minh chúng không bị khối TE chặn khi TE crash)
    prelude = textwrap.dedent(f'''
        set -uo pipefail
        PY={fakepy}; WORKDIR_8L={tmp}; LOG={tmp}/log; DRY_RUN={dry}; TODAY=2026-11-05; DISPATCH_RC=0
        echo trend >> {steps}; TREND_RC={trend_rc}; echo sbv >> {steps}; SBV_RC={sbv_rc}
        cd {tmp}
    ''')
    env = {k: v for k, v in os.environ.items() if k != "TZ"}; env["FAKE_TE_RC"] = str(te_rc)
    r = subprocess.run(["bash", "-c", prelude + blk], env=env, capture_output=True, text=True)
    n = open(notif).read().count("🔴") if os.path.exists(notif) else 0
    a = open(args).read() if os.path.exists(args) else ""
    return r.returncode, n, a, open(steps).read()

rc, n, a, st = run(0)
ok(rc == 0 and n == 0 and "te_macro_crosscheck.py" in a and "--dry-run" not in a, f"1. TE_RC=0 ⇒ exit 0, không notify (rc={rc}, notify={n})")
rc, n, a, st = run(1)
ok(rc == 1 and n == 1, f"2. TE_RC=1 ⇒ exit 1 và đúng 1 notify 🔴 (rc={rc}, notify={n})")
ok(st.split() == ["trend", "sbv"], "3. bước trend + sbv đã chạy trước khối TE, TE crash không chặn chúng")
rc, n, a, st = run(124)
ok(rc == 1 and n == 1, f"4. TE timeout (rc 124) ⇒ exit 1 + 1 notify (rc={rc}, notify={n})")
rc, n, a, st = run(0, dry=1)
ok(rc == 0 and n == 0 and "--dry-run" in a, "5. --dry-run ⇒ truyền --dry-run, không notify")
rc, n, a, st = run(1, dry=1)
ok(rc == 1 and n == 0 and "--dry-run" in a, "6. --dry-run + TE crash ⇒ exit 1 nhưng KHÔNG notify")
rc, n, a, st = run(0, trend_rc=1)
ok(rc == 1 and n == 0, "7. trend lỗi, TE sạch ⇒ exit 1 (không bị TE che)")
ok(re.search(r'timeout 300 "\$PY" te_macro_crosscheck\.py', blk) is not None, "8. lời gọi TE bọc timeout 300")
print("TZ env =", os.environ.get("TZ"))
print("TẤT CẢ PASS" if not FAIL else f"FAIL {FAIL}")
sys.exit(1 if FAIL else 0)
