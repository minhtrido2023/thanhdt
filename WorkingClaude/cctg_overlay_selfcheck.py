#!/usr/bin/env python3
"""Selfcheck for the CCTG overlay wired 2026-10-01 (user directive): cctg_rate_vn.py,
deposit_rate_vn.effective_deposit_rate()/effective_deposit_events_df(), and the CCTG overlay
inside macro_killswitch_a_status(). Run under $DNA_PYEXE and under `env -u TZ` /
Pacific/Kiritimati / America/New_York (coding_guidelines §16/§19) -- every test below uses an
explicit asof, so host TZ should not matter; asserted explicitly in T_tz."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import cctg_rate_vn as cctg
import deposit_rate_vn as dep

N = 0


def check(label, cond):
    global N
    N += 1
    assert cond, f"FAIL [{label}]"
    print(f"  ok: {label}")


print("=== cctg_rate_vn + effective_deposit_rate overlay selfcheck ===")

# T1: no CCTG observation before the first anchor (2026-09-30) -> None, not an error, not a guess.
r1_pct, r1_date = cctg.current_cctg_rate(asof="2026-09-29")
check("T1 pre-anchor asof -> rate is None", r1_pct is None)
check("T1 pre-anchor asof -> date is None", r1_date is None)

# T2: on/after the anchor -> the frozen 7.5% value.
r2_pct, r2_date = cctg.current_cctg_rate(asof="2026-10-01")
check("T2 post-anchor rate=7.5%", abs(r2_pct - 7.5) < 1e-9)
check("T2 post-anchor date=2026-09-30", str(r2_date.date()) == "2026-09-30")

# T3: macro_killswitch_a_status before CCTG existed -> rate_source == big4_12m (byte-identical to
# pre-CCTG behavior); uses a real frozen Big-4 anchor (2023-03-01..2023-06-01 = 7.2%).
r3 = dep.macro_killswitch_a_status(asof="2023-05-01")
check("T3 pre-CCTG call: rate_source=big4_12m", r3["rate_source"] == "big4_12m")
check("T3 pre-CCTG call: rate unchanged (7.2%)", abs(r3["rate"] - 0.072) < 1e-9)

# T4: CCTG wins when fresh and higher than Big-4 -- inject a fresh, LOW Big-4 anchor (postdating
# the last frozen 2026-06-01 anchor, same append-only mechanism as macro_killswitch_a_selfcheck.py)
# so Big-4 alone would read CLEAR, then confirm CCTG's 7.5% becomes the driver.
_tmpdir = tempfile.mkdtemp(prefix="cctg_selfcheck_")
_tmp_dep_csv = os.path.join(_tmpdir, "deposit_rate_vn_events.csv")
_orig_dep_csv = dep._EVENTS_CSV
try:
    with open(_tmp_dep_csv, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-20,6.5,2026-09-20,manual_verify,selfcheck-fixture\n")
    dep._EVENTS_CSV = _tmp_dep_csv
    r4 = dep.macro_killswitch_a_status(asof="2026-10-01", check_freshness=True)
    check("T4 CCTG wins: rate=7.5%", abs(r4["rate"] - 0.075) < 1e-9)
    check("T4 CCTG wins: rate_source starts with cctg_6m", r4["rate_source"].startswith("cctg_6m"))
    check("T4 CCTG wins: not armed (7.5% <= 7.5% strict)", r4["armed"] is False)

    r4b = dep.effective_deposit_rate(asof="2026-10-01", check_freshness=True)
    check("T4b effective_deposit_rate agrees: rate_pct=7.5", abs(r4b["rate_pct"] - 7.5) < 1e-9)
    check("T4b effective_deposit_rate agrees: source=cctg", r4b["rate_source"].startswith("cctg_6m"))
    check("T4b effective_deposit_rate: big4_rate_pct=6.5 preserved", abs(r4b["big4_rate_pct"] - 6.5) < 1e-9)
    check("T4b effective_deposit_rate: cctg_rate_pct=7.5 preserved", abs(r4b["cctg_rate_pct"] - 7.5) < 1e-9)

    # T5: CCTG present but STALE (asof far enough past the single CCTG anchor) -> Big-4 wins even
    # though CCTG's raw value (7.5%) is higher than Big-4's fresh fixture (6.5%).
    r5 = dep.macro_killswitch_a_status(asof="2026-11-20", check_freshness=True)
    check("T5 stale CCTG excluded: rate_source=big4_12m", r5["rate_source"] == "big4_12m")
    check("T5 stale CCTG excluded: rate=6.5% (not 7.5%)", abs(r5["rate"] - 0.065) < 1e-9)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    shutil.rmtree(_tmpdir, ignore_errors=True)

# T6: CCTG lower than Big-4 -> Big-4 still wins (never silently replaces a higher Big-4 reading).
# Real anchor: 2012-10-01 Big-4 = 9.0%, well above CCTG's 7.5% -- but CCTG has no data that far
# back anyway (T1 covers the "no data" path); this covers the "has data but it's lower" path via
# a controlled CSV fixture co-located at a post-CCTG-anchor date.
_tmp_dep_csv2 = os.path.join(tempfile.mkdtemp(prefix="cctg_selfcheck2_"), "deposit_rate_vn_events.csv")
try:
    with open(_tmp_dep_csv2, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-25,8.0,2026-09-25,manual_verify,selfcheck-fixture-high\n")
    dep._EVENTS_CSV = _tmp_dep_csv2
    r6 = dep.macro_killswitch_a_status(asof="2026-10-01", check_freshness=True)
    check("T6 Big-4 (8.0%) > CCTG (7.5%): rate_source=big4_12m", r6["rate_source"] == "big4_12m")
    check("T6 Big-4 (8.0%) > CCTG (7.5%): rate=8.0%, armed", abs(r6["rate"] - 0.08) < 1e-9 and r6["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_dep_csv
    shutil.rmtree(os.path.dirname(_tmp_dep_csv2), ignore_errors=True)

# T7: effective_deposit_events_df() shape + pre-anchor byte-identity with deposit_events_df().
full = dep.effective_deposit_events_df()
base = dep.deposit_events_df()
check("T7 effective_deposit_events_df columns", list(full.columns) == ["time", "deposit_rate"])
pre_anchor_full = full[full["time"] < "2026-09-30"].reset_index(drop=True)
pre_anchor_base = base[base["time"] < "2026-09-30"].reset_index(drop=True)
check("T7 pre-anchor rows byte-identical to deposit_events_df()",
      pre_anchor_full.equals(pre_anchor_base))

# T8: the CCTG anchor date itself must appear as its own row (union-of-breakpoints design) --
# a naive "merge CCTG onto Big-4's existing row dates" would be a no-op here, since Big-4's last
# row (2026-06-01) predates CCTG's first anchor (2026-09-30) and a backward-only merge would never
# land on it (this exact bug was caught and fixed before shipping, 2026-10-01).
check("T8 CCTG anchor date present as its own row",
      (full["time"] == pd.Timestamp("2026-09-30")).any())
check("T8 CCTG anchor row value = 7.5 (max(6.8, 7.5))",
      abs(full.loc[full["time"] == pd.Timestamp("2026-09-30"), "deposit_rate"].iloc[0] - 7.5) < 1e-9)

# T9: downstream as-of lookup (the exact pattern value_radar.py's load_series() uses: merge a
# daily trading-day panel backward onto this step series) must surface 7.5% for ANY day on/after
# the CCTG anchor, not just the anchor day itself.
day = pd.DataFrame({"time": [pd.Timestamp("2026-10-01")]})
r9 = pd.merge_asof(day, full.sort_values("time"), on="time", direction="backward")
check("T9 downstream as-of lookup on 2026-10-01 -> 7.5%",
      abs(r9["deposit_rate"].iloc[0] - 7.5) < 1e-9)

# T_tz: TZ independence guard (explicit asof throughout).
r_tz_a = dep.macro_killswitch_a_status(asof="2026-10-01")
os.environ.pop("TZ", None)
r_tz_b = dep.macro_killswitch_a_status(asof="2026-10-01")
check("T_tz TZ-independent", r_tz_a == r_tz_b)

print(f"\n=== {N} assertions PASS ===")
