#!/usr/bin/env python3
"""Offline regression for the D1-D3 shadow-to-live rollout state."""
import os
import tempfile

from trading_bot import gdkhq_rollout
from trading_bot import price_frame as pf
from trading_bot.exdate_gate import apply_exdate_gate
from trading_bot.plan import PlannedOrder, TradePlan


def plan(date, ticker):
    return TradePlan(plan_date=date, signal_date=date, strategy="fixture",
                     strategy_version="1", state=2, state_name="NEUTRAL", nav_basis={},
                     orders=[PlannedOrder(f"BUY-{ticker}", ticker, "buy", 100, 20000)])


def check(name, condition):
    print(f"{'PASS' if condition else 'FAIL'} {name}")
    if not condition:
        raise AssertionError(name)


with tempfile.TemporaryDirectory() as td:
    state_path = os.path.join(td, "rollout.json")
    check("missing state defaults to shadow-pending", not gdkhq_rollout.enabled(state_path))
    trace_path = os.path.join(td, "trace.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        f.write("{}\n")
    state = gdkhq_rollout.mark_enabled(trace_path, "2026-08-17", state_path)
    check("successful trace marker enables rollout atomically",
          gdkhq_rollout.enabled(state_path) and state["approved_by"] == "user")

event = {"ticker": "BID", "event_code": "ISS", "exright_date": "2026-08-17",
         "event_status": "announced", "value_per_share": None,
         "exercise_ratio": 0.068433, "issue_method_name_vi": "Cổ phiếu thưởng"}
blocked, adjustments = apply_exdate_gate(
    plan("2026-08-17", "BID"), object(), "2026-08-17",
    events_map=pf.events_by_ticker_date([event]), resolver=gdkhq_rollout.pending_resolver)
check("pending rollout blocks only the event ticker",
      not blocked.orders and adjustments[0]["gate"] == "ROLLOUT_PENDING")

normal, adjustments = apply_exdate_gate(
    plan("2026-08-17", "FPT"), object(), "2026-08-17",
    events_map=pf.events_by_ticker_date([event]), resolver=gdkhq_rollout.pending_resolver)
check("pending rollout leaves normal tickers untouched",
      len(normal.orders) == 1 and adjustments[0]["action"] == "NO_EVENT")

print("OK — GDKHQ rollout state is fail-safe and ticker-scoped")
