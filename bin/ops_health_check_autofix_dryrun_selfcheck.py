#!/usr/bin/env python3
"""ops_health_check.sh: job autofix (Wags_*/Winston_*) mặc định DRY-RUN. Trích ĐÚNG khối `case JOB_ID` rồi chạy bằng bash."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "ops_health_check.sh")).read()
m = re.search(r'case "\$\{JOB_ID:-\}" in.*?\nesac\n', src, re.S)
if not m:
    print("FAIL không tìm thấy khối case JOB_ID trong ops_health_check.sh"); sys.exit(1)
block = m.group(0)
fails = 0
def dry(job, ovr):
    env = {"PATH": os.environ["PATH"]}
    if job is not None: env["JOB_ID"] = job
    if ovr is not None: env["OPS_HEALTH_DRY_RUN"] = ovr
    return subprocess.run(["bash", "-c", block + '\necho "$DRY_RUN"'], env=env, capture_output=True, text=True).stdout.strip()
def chk(name, got, want):
    global fails
    ok = got == want; fails += (not ok); print(("PASS " if ok else "FAIL ") + name + ("" if ok else f" got={got} want={want}"))
chk("cron (không JOB_ID) ⇒ live 0", dry(None, None), "0")
chk("Wags_* ⇒ DRY 1", dry("Wags_20261001_054510", None), "1")
chk("Winston_* ⇒ DRY 1", dry("Winston_20261001_000001", None), "1")
chk("Taylor_* ⇒ live 0", dry("Taylor_20261001_000001", None), "0")
chk("Wags_* + OPS_HEALTH_DRY_RUN=0 ⇒ ép live 0", dry("Wags_1", "0"), "0")
chk("cron + OPS_HEALTH_DRY_RUN=1 ⇒ 1", dry(None, "1"), "1")
print(f"{'FAIL' if fails else 'ALL PASS'} ({fails} fail)"); sys.exit(1 if fails else 0)
