#!/usr/bin/env python3
"""Selfcheck for deposit_rate_vn.macro_killswitch_a_status() (trading_rules.json
macro_kill_switches.A_sbv_rate_suspend, wired 2026-10-01). Fixtures hand-computed against the
LITERAL spec text in trading_rules.json, not against the implementation. Run under $DNA_PYEXE
and under `env -u TZ` per coding_guidelines §19/verify-before-done (no TZ dependency expected —
this uses pd.Timestamp.today().normalize() with an explicit asof override in every test, so the
host TZ should not matter; asserted explicitly below as a regression guard)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import deposit_rate_vn as dep

N = 0


def check(label, cond):
    global N
    N += 1
    assert cond, f"FAIL [{label}]"
    print(f"  ok: {label}")


print("=== macro_killswitch_a_status selfcheck ===")

# T1: known historical point strictly below threshold -> CLEAR, not armed, not stale.
r = dep.macro_killswitch_a_status(asof="2026-06-15")
check("T1 rate=6.8% (2026-06 anchor)", abs(r["rate"] - 0.068) < 1e-9)
check("T1 not armed", r["armed"] is False)
check("T1 not stale", r["stale"] is False)
check("T1 threshold=0.075", r["threshold"] == 0.075)
check("T1 reason mentions CLEAR", "CLEAR" in r["reason"])

# T2: known historical point strictly above threshold -> ARMED. Historical (explicit asof) calls
# must NOT be judged "stale" -- the 26 frozen DEPOSIT_EVENTS anchors are settled ground truth
# months apart by construction, not a live feed failing to refresh (this distinction is exactly
# what check_freshness defaults to False for an explicit asof; asserted explicitly here too).
r2 = dep.macro_killswitch_a_status(asof="2013-01-01")
check("T2 historical call not stale by default", r2["stale"] is False)
check("T2 rate=9.0% (2012-10 anchor)", abs(r2["rate"] - 0.09) < 1e-9)
check("T2 armed", r2["armed"] is True)
check("T2 reason mentions SUSPEND", "SUSPEND" in r2["reason"])

# T3: exact boundary (7.5%) must be CLEAR (spec says trigger is "> 0.075", strictly greater) --
# 2013-06-01 anchor is exactly 7.5%.
r3 = dep.macro_killswitch_a_status(asof="2013-09-01")
check("T3 boundary rate=7.5% exactly", abs(r3["rate"] - 0.075) < 1e-9)
check("T3 boundary NOT armed (strictly > required)", r3["armed"] is False)

# T4: current canonical anchor (2026-06-01 = 6.8%), asof far enough forward to be "fresh" by
# construction against that anchor's own effective_date (not the real clock).
r4 = dep.macro_killswitch_a_status(asof="2026-06-20")
check("T4 current-era rate=6.8%", abs(r4["rate"] - 0.068) < 1e-9)
check("T4 not armed at current level", r4["armed"] is False)

# T5: fail-closed on stale feed -- exercise the mechanism directly with check_freshness=True
# (the live/monitoring call shape; asof=None in production always implies this, but freezing
# "today" isn't needed to test the mechanism itself -- an explicit asof + explicit
# check_freshness=True tests the exact same code path deterministically).
last_anchor = dep.deposit_events_df()["time"].max()
stale_asof = last_anchor + pd.Timedelta(days=100)
r5 = dep.macro_killswitch_a_status(asof=stale_asof, stale_days_limit=45, check_freshness=True)
check("T5 stale -> armed=True (fail-closed)", r5["armed"] is True)
check("T5 stale flag set", r5["stale"] is True)
check("T5 reason mentions stale", "stale" in r5["reason"])
check("T5 age_days > limit", r5["age_days"] > 45)

# T5b: the SAME query without forcing check_freshness (i.e. default False for an explicit asof)
# must NOT be stale -- this is the exact regression this function's design fixes (2026-10-01):
# a historical/backtest-style asof must never be spuriously flagged stale by default.
r5b = dep.macro_killswitch_a_status(asof=stale_asof, stale_days_limit=45)
check("T5b historical default not stale", r5b["stale"] is False)
check("T5b historical default not armed by staleness", r5b["armed"] == (r5b["rate"] > 0.075))

# T6: fail-closed when there is NO data at/before asof at all (asof before the very first anchor)
# -- this path fires regardless of check_freshness (there is no rate to resolve at all).
r6 = dep.macro_killswitch_a_status(asof="2000-01-01")
check("T6 no-data -> armed=True (fail-closed)", r6["armed"] is True)
check("T6 no-data rate is None", r6["rate"] is None)
check("T6 no-data stale flag True", r6["stale"] is True)

# T7: just-under the staleness limit -> NOT stale (boundary exclusivity, age_days == limit passes).
r7 = dep.macro_killswitch_a_status(asof=last_anchor + pd.Timedelta(days=45), stale_days_limit=45,
                                    check_freshness=True)
check("T7 age==limit not stale (> required, not >=)", r7["stale"] is False)

# T7c: DEFAULT stale_days_limit is actually 45, not some other number -- omit the kwarg entirely
# (every other staleness test above passes stale_days_limit=45 explicitly, so none of them would
# catch the default itself silently drifting, e.g. to 999).
r7c = dep.macro_killswitch_a_status(asof=last_anchor + pd.Timedelta(days=50), check_freshness=True)
check("T7c default stale_days_limit=45 (50d old -> stale)", r7c["stale"] is True)

# T7b: append_deposit_rate.py-style CSV extension picked up and read as FRESH, not stale -- real
# repro of the production refresh path (a new anchor written to the CSV, then queried at a date
# shortly after it, must NOT be stale), replacing a tautological "call the function twice and
# compare to itself" check. Uses a temp CSV + monkeypatches dep._EVENTS_CSV so the real
# (gitignored) production file is never touched.
import tempfile
_tmpdir = tempfile.mkdtemp(prefix="depgate_selfcheck_")
_tmp_csv = os.path.join(_tmpdir, "deposit_rate_vn_events.csv")
_orig_csv_path = dep._EVENTS_CSV
try:
    with open(_tmp_csv, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-15,7.1,2026-09-15,manual_verify,selfcheck-fixture\n")
    dep._EVENTS_CSV = _tmp_csv
    r7b = dep.macro_killswitch_a_status(asof="2026-09-20", stale_days_limit=45, check_freshness=True)
    check("T7b new CSV anchor picked up (rate=7.1%)", abs(r7b["rate"] - 0.071) < 1e-9)
    check("T7b new CSV anchor fresh (5d old, not stale)", r7b["stale"] is False)
    check("T7b new CSV anchor not armed (7.1% <= 7.5%)", r7b["armed"] is False)
finally:
    dep._EVENTS_CSV = _orig_csv_path

# T9/T10: threshold-boundary fixtures that kill off-by-one-decimal mutants on THRESHOLD (0.075).
# A mutant using 0.07 instead of 0.075 would wrongly ARM at 7.2% (real anchor 2023-03-01..2023-06-01,
# strictly between 0.07 and 0.075) -- true threshold keeps this CLEAR.
r9 = dep.macro_killswitch_a_status(asof="2023-05-01")
check("T9 rate=7.2% (2023-03 anchor)", abs(r9["rate"] - 0.072) < 1e-9)
check("T9 not armed (kills 0.07-threshold mutant)", r9["armed"] is False)

# A mutant using 0.08 instead of 0.075 would wrongly stay CLEAR at 7.6% -- true threshold ARMS.
# No real anchor sits in (7.5, 8.0) exclusive, so inject one via a temp CSV (same mechanism as T7b).
# Must postdate the last FROZEN anchor (2026-06-01) -- deposit_events_df() only appends CSV rows
# strictly newer than that (append-only design), so an earlier injected date is silently dropped.
try:
    with open(_tmp_csv, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-18,7.6,2026-09-18,manual_verify,selfcheck-fixture\n")
    dep._EVENTS_CSV = _tmp_csv
    r10 = dep.macro_killswitch_a_status(asof="2026-09-19")
    check("T10 rate=7.6% (injected fixture)", abs(r10["rate"] - 0.076) < 1e-9)
    check("T10 armed (kills 0.08-threshold mutant)", r10["armed"] is True)
finally:
    dep._EVENTS_CSV = _orig_csv_path

# T11: rate-range sanity-fence guard -- a fraction-vs-percent typo (0.068 meaning 6.8%) must
# fail-closed (armed), not silently read as "0.07% <= 7.5% -> CLEAR".
try:
    with open(_tmp_csv, "w") as f:
        f.write("effective_date,deposit_rate,collected_date,source,note\n")
        f.write("2026-09-20,0.068,2026-09-20,manual_verify,selfcheck-typo-fixture\n")
    dep._EVENTS_CSV = _tmp_csv
    r11 = dep.macro_killswitch_a_status(asof="2026-09-21")
    check("T11 out-of-range rate -> armed (fail-closed)", r11["armed"] is True)
    check("T11 out-of-range rate -> stale (fail-closed)", r11["stale"] is True)
    check("T11 reason mentions rate_pct", "rate_pct" in r11["reason"])
finally:
    dep._EVENTS_CSV = _orig_csv_path

# T12: a CORRUPT CSV (unparseable -> pandas ParserError, NOT the narrow EmptyDataError/ValueError
# already handled inside deposit_events_df) must fail-closed via the function-level try/except,
# not propagate as an uncaught exception.
try:
    with open(_tmp_csv, "w") as f:
        f.write('effective_date,deposit_rate,collected_date,source,note\n')
        f.write('2026-09-15,7.1,2026-09-15,manual_verify,"unterminated quote never closed\n')
    dep._EVENTS_CSV = _tmp_csv
    r12 = dep.macro_killswitch_a_status(asof="2026-09-20")
    check("T12 corrupt CSV -> armed (fail-closed)", r12["armed"] is True)
    check("T12 corrupt CSV -> stale (fail-closed)", r12["stale"] is True)
    check("T12 corrupt CSV -> reason mentions error", r12["reason"].startswith("error:"))
finally:
    dep._EVENTS_CSV = _orig_csv_path
    import shutil
    shutil.rmtree(_tmpdir, ignore_errors=True)

# T8: TZ independence guard -- explicit asof means host TZ env var must not change the result.
r8a = dep.macro_killswitch_a_status(asof="2026-06-15")
os.environ.pop("TZ", None)
r8b = dep.macro_killswitch_a_status(asof="2026-06-15")
check("T8 TZ-independent (explicit asof)", r8a == r8b)

# --- Mutation-style manual checks: describe what SHOULD fail if the implementation regresses. ---
# M1: flipping the comparison to >= would make T3 (exact 7.5%) armed=True -- already asserted above.
# M2: dropping the stale check would make T5/T6 armed=False -- already asserted above.
# M3: using deposit_events_df() max() row instead of an asof-bounded slice would make T2
#     (queried at 2013-01-01, historical) return the CURRENT (2026) rate instead of 9.0% --
#     already caught by T2's exact-value assertion.
# M4/M5: THRESHOLD mutated to 0.07/0.08 -- caught by T9/T10.
# M6: removing the try/except -- caught by T12 (would raise instead of returning a dict).
# M7: removing the rate-range guard -- caught by T11.

print(f"\n=== {N} assertions PASS ===")
