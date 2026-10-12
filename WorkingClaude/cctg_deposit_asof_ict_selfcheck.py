#!/usr/bin/env python3
"""Selfcheck: asof=None must mean TODAY in ICT (Asia/Ho_Chi_Minh), not the host process TZ
(coding_guidelines §16; code_quality_2026-10-11 finding #2, bus cq-2026-10-11-hard-boundary).
Covers the 4 default-asof call sites: cctg_rate_vn.current_cctg_rate, and deposit_rate_vn
.macro_killswitch_a_status / current_deposit_rate / effective_deposit_rate.

Two independent proofs:
 (1) "Not the process TZ": each case runs a child under a foreign TZ with synthetic events dated
     ICT-today -1/0/+1. TZ=Etc/GMT+12 (UTC-12) disagrees with ICT on the date when ICT hour < 19;
     TZ=Pacific/Kiritimati (UTC+14) when ICT hour >= 17 -- together they cover all 24h, so at
     least one leg is red on a today()-style regression at any run time.
 (2) "Anchored to ICT (UTC+7), not some other fixed zone": pd.Timestamp.now is pinned at the two
     instants straddling ICT midnight to the minute (2026-10-11 16:59Z -> want 10-11; 17:00Z ->
     want 10-12). Any fixed zone with offset != +7:00 gives the wrong date at one of them (UTC,
     Asia/Tokyo, Asia/Yangon +6:30, UTC-naive), whatever the wall-clock time of the run. A zone
     with the same offset (Asia/Bangkok, +7, no DST) is behaviourally identical and passes --
     correct, not a gap. Run under $DNA_PYEXE."""
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

PINNED = r'''
import json, sys
sys.path.insert(0, %(here)r)
import pandas as pd
import cctg_rate_vn as cctg
import deposit_rate_vn as dep
ds = pd.to_datetime(["2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13"])
dep.deposit_events_df = lambda: pd.DataFrame({"time": ds, "deposit_rate": [4.0, 5.0, 6.0, 7.0]})
cctg.cctg_events_df = lambda: pd.DataFrame({"time": ds, "cctg_rate": [4.5, 5.5, 6.5, 7.5]})
by_rate = {4.0: "2026-10-10", 5.0: "2026-10-11", 6.0: "2026-10-12", 7.0: "2026-10-13"}
out = {}
for inst in ("2026-10-11 16:59", "2026-10-11 17:00"):
    def _now(tz=None, _i=inst):
        t = pd.Timestamp(_i, tz="UTC")
        return t.tz_convert(tz) if tz is not None else t.tz_localize(None)
    pd.Timestamp.now = staticmethod(_now)
    out[inst] = {"cctg": str(cctg.current_cctg_rate()[1].date()),
                 "dep": by_rate[dep.current_deposit_rate()],
                 "effective": dep.effective_deposit_rate()["last_update"],
                 "killswitch": dep.macro_killswitch_a_status()["last_update"]}
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


def run(tz, code=None):
    env = dict(os.environ)
    if tz is None:
        env.pop("TZ", None)
    else:
        env["TZ"] = tz
    p = subprocess.run([sys.executable, "-c", code or CHILD], env=env, capture_output=True, text=True)
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
# fixed-instant legs: 23:59 ICT (10-11) and 00:00 ICT (10-12); TZ-independent, run under 2 TZs anyway
for tz in (None, "Etc/GMT+12"):
    o = run(tz, PINNED)
    tag = tz or "unset"
    for inst, want in (("2026-10-11 16:59", "2026-10-11"), ("2026-10-11 17:00", "2026-10-12")):
        for site, got in o[inst].items():
            check(f"[pinned {inst}Z, TZ={tag}] {site} -> ICT date {want}", got == want)
if FAILS:
    print(f"{len(FAILS)}/{N} CHECKS FAILED")
    sys.exit(1)
print(f"ALL {N} CHECKS PASSED")
