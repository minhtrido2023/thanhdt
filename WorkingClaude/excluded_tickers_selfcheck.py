# -*- coding: utf-8 -*-
"""Regression self-check for per-account `excluded_tickers` (legacy/special-situation holdings
kept outside V2.4's automated rebalancing — added 2026-07-06 for the ZaloPay account's DGC
position, held under an active HOSE trading restriction + warning status).

Root need: onboarding an account whose broker-side positions predate bot management (e.g. an
existing DGC holding the user wants to keep for its own investment thesis, not have the bot
touch). Rather than a one-off hack, `excluded_tickers` is a general per-account config field
(trading_bot/config.py ACCOUNT_DEFAULTS) enforced in ONE place —
`trading_bot.plan.filter_excluded_tickers()`, called from `bot_execute.py` right after
`load_plan()` — so it works uniformly for any future account with this field set, regardless
of how its plan was generated (DollarBill's LLM-authored JSON, bot_prepare_plan.py's
templated strategy.build_plan(), or hand-edited).

Run: python excluded_tickers_selfcheck.py   (exit 0 = all pass)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import PlannedOrder, TradePlan, filter_excluded_tickers  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def make_plan(orders):
    return TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account="selfcheck", created_at="2099-01-01T00:00:00")


# A. No excluded_tickers configured (default []) -> plan passes through completely unchanged,
#    zero orders blocked (must not affect the other 5 live accounts with no exclusion list).
orders_a = [PlannedOrder(id="BUY-01", ticker="DGC", side="buy", qty=100, ref_price=48000),
            PlannedOrder(id="BUY-02", ticker="VPB", side="buy", qty=100, ref_price=27000)]
plan_a, blocked_a = filter_excluded_tickers(make_plan(list(orders_a)), [])
check("A1 empty excluded_tickers -> no orders blocked", blocked_a == [], detail=str(blocked_a))
check("A2 empty excluded_tickers -> plan.orders unchanged (both present)",
      {o.ticker for o in plan_a.orders} == {"DGC", "VPB"})

# B. excluded_tickers=None (field genuinely absent from an older account profile, matches
#    ACCOUNT_DEFAULTS.get(...) returning None rather than []) -> same as empty, no crash.
plan_b, blocked_b = filter_excluded_tickers(make_plan(list(orders_a)), None)
check("B1 excluded_tickers=None -> no crash, no orders blocked", blocked_b == [])

# C. excluded_tickers=["DGC"] -> DGC order removed, VPB order untouched (the exact ZaloPay case).
orders_c = [PlannedOrder(id="SELL-01", ticker="DGC", side="sell", qty=5000, ref_price=48000),
            PlannedOrder(id="BUY-01", ticker="VPB", side="buy", qty=200, ref_price=27000),
            PlannedOrder(id="BUY-02", ticker="VIB", side="buy", qty=300, ref_price=16000)]
plan_c, blocked_c = filter_excluded_tickers(make_plan(list(orders_c)), ["DGC"])
check("C1 DGC order removed", {o.ticker for o in blocked_c} == {"DGC"}, detail=str(blocked_c))
check("C2 remaining orders keep VPB+VIB, DGC gone",
      {o.ticker for o in plan_c.orders} == {"VPB", "VIB"}, detail=str([o.ticker for o in plan_c.orders]))
check("C3 order count matches (3 in -> 2 out, 1 blocked)",
      len(plan_c.orders) == 2 and len(blocked_c) == 1)

# D. ALL orders excluded (edge case: a plan somehow only targets excluded tickers) -> plan.orders
#    becomes empty, blocked list captures all of them — caller (bot_execute.py) must then hit its
#    existing "plan không có lệnh — bỏ qua" path, not crash on an empty-orders TradePlan.
orders_d = [PlannedOrder(id="SELL-01", ticker="DGC", side="sell", qty=1000, ref_price=48000)]
plan_d, blocked_d = filter_excluded_tickers(make_plan(list(orders_d)), ["DGC"])
check("D1 all-excluded plan ends with zero orders", plan_d.orders == [])
check("D2 all-excluded plan reports all as blocked", len(blocked_d) == 1)

# E. Case sensitivity / exact match only — "dgc" (lowercase) must NOT match "DGC" (tickers are
#    always uppercase on VN exchanges; a silent case-insensitive match could hide a config typo
#    instead of surfacing it, and a config typo here has real-money consequences the other way
#    too — an *intended* exclusion silently not applying).
plan_e, blocked_e = filter_excluded_tickers(make_plan([PlannedOrder(
    id="BUY-01", ticker="DGC", side="buy", qty=100, ref_price=48000)]), ["dgc"])
check("E1 exact-case match only — lowercase config does NOT silently match DGC",
      blocked_e == [], detail=str(blocked_e))

# F. Multiple excluded tickers on one plan (future multi-legacy-position account).
orders_f = [PlannedOrder(id=f"BUY-{i:02d}", ticker=t, side="buy", qty=100, ref_price=10000)
            for i, t in enumerate(["AAA", "BBB", "CCC", "DDD"])]
plan_f, blocked_f = filter_excluded_tickers(make_plan(list(orders_f)), ["AAA", "CCC"])
check("F1 multiple exclusions all applied",
      {o.ticker for o in blocked_f} == {"AAA", "CCC"}, detail=str(blocked_f))
check("F2 non-excluded tickers all survive",
      {o.ticker for o in plan_f.orders} == {"BBB", "DDD"})

print()
if fails:
    print(f"❌ {len(fails)} FAIL(s): {fails}")
    sys.exit(1)
print("✅ all excluded_tickers checks passed")
sys.exit(0)
