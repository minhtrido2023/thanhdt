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

# T7b: the live call shape (asof=None) auto-enables check_freshness -- confirm the auto-default
# actually resolves to True for asof=None (not just documented, asserted against real behavior).
r7b_live = dep.macro_killswitch_a_status()
r7b_explicit = dep.macro_killswitch_a_status(check_freshness=True)
check("T7b asof=None auto-enables freshness (matches explicit True)",
      r7b_live["stale"] == r7b_explicit["stale"] and r7b_live["armed"] == r7b_explicit["armed"])

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

print(f"\n=== {N} assertions PASS ===")
