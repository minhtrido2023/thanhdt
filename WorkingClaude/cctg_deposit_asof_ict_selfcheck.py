#!/usr/bin/env python3
"""Selfcheck: asof=None must mean TODAY in ICT (Asia/Ho_Chi_Minh), not the host process TZ
(coding_guidelines §16; code_quality_2026-10-11 finding #2, bus cq-2026-10-11-hard-boundary).
Covers the 4 default-asof call sites: cctg_rate_vn.current_cctg_rate, and deposit_rate_vn
.macro_killswitch_a_status / current_deposit_rate / effective_deposit_rate.

Each case runs a child process under a foreign TZ with synthetic events dated ICT-today -1/0/+1
and asserts asof=None picks the ICT-today row. TZ=Etc/GMT+12 (UTC-12) disagrees with ICT on the date
when ICT hour < 19; TZ=Pacific/Kiritimati (UTC+14) when ICT hour >= 17 -- together they cover all
24h, so at least one leg is red on the old code at any run time. Run under $DNA_PYEXE."""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))

CHILD = r'''
import json, sys
sys.path.insert(0, %(here)r)
import pandas as pd
import cctg_rate_vn as cctg
import deposit_rate_vn as dep
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
d = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
ds = [pd.Timestamp(d - timedelta(days=1)), pd.Timestamp(d), pd.Timestamp(d + timedelta(days=1))]
dep.deposit_events_df = lambda: pd.DataFrame({"time": ds, "deposit_rate": [5.0, 6.0, 7.0]})
cctg.cctg_events_df = lambda: pd.DataFrame({"time": ds, "cctg_rate": [5.5, 6.5, 7.5]})
out = {"ict_today": str(d)}
r, ld = cctg.current_cctg_rate()
out["cctg"] = [r, str(ld.date())]
out["dep_rate"] = dep.current_deposit_rate()
out["effective"] = dep.effective_deposit_rate()["last_update"]
out["killswitch"] = dep.macro_killswitch_a_status()["last_update"]
print(json.dumps(out))
''' % {"here": HERE}

N = 0
FAILS = []


def check(label, cond):
    global N
    N += 1
    if not cond:
        FAILS.append(label)
    print(f"  {'ok' if cond else 'FAIL'}: {label}")


def run(tz):
    env = dict(os.environ)
    if tz is None:
        env.pop("TZ", None)
    else:
        env["TZ"] = tz
    p = subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True)
    assert p.returncode == 0, f"child rc={p.returncode}\n{p.stderr}"
    return json.loads(p.stdout.strip().splitlines()[-1])


now_ict = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
print(f"=== asof=None anchors to ICT selfcheck (ICT now {now_ict:%Y-%m-%d %H:%M}) ===")
for tz in (None, "UTC", "Etc/GMT+12", "Pacific/Kiritimati"):
    o = run(tz)
    t = o["ict_today"]
    tag = tz or "unset"
    check(f"[{tag}] current_cctg_rate picks ICT-today row {t}", o["cctg"] == [6.5, t])
    check(f"[{tag}] current_deposit_rate picks ICT-today row (6.0)", o["dep_rate"] == 6.0)
    check(f"[{tag}] effective_deposit_rate last_update == {t}", o["effective"] == t)
    check(f"[{tag}] macro_killswitch_a_status last_update == {t}", o["killswitch"] == t)
if FAILS:
    print(f"{len(FAILS)}/{N} CHECKS FAILED")
    sys.exit(1)
print(f"ALL {N} CHECKS PASSED")
