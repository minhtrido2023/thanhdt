#!/usr/bin/env python3
"""Offline regression for the D1-D3 shadow-to-live rollout state."""
import json
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
    acceptance_path = os.path.join(td, "acceptance.json")
    report_path = os.path.join(td, "acceptance.md")
    check("missing state defaults to shadow-pending", not gdkhq_rollout.enabled(state_path))
    trace_path = os.path.join(td, "trace.json")
    trace = {
        "passed": True,
        "watch": ["BID"],
        "accounts": [{"label": "SpaceX", "ok": True, "frames": {}, "plan_adjustments": []}],
        "calendar_missing": [],
    }
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False)
    report_path, acceptance = gdkhq_rollout.write_acceptance_report(
        trace, "PASS selfcheck", "2026-08-17", trace_path,
        report_path=report_path, state_path=acceptance_path)
    check("PASS trace luôn có report + acceptance PENDING_ACCEPTANCE",
          os.path.isfile(report_path)
          and acceptance["acceptance_status"] == "PENDING_ACCEPTANCE"
          and acceptance["trace_passed"] is True)
    check("PASS trace chưa nghiệm thu ⇒ live vẫn chưa bật",
          not gdkhq_rollout.enabled(state_path))
    state = gdkhq_rollout.record_shadow_pass(
        trace_path, "2026-08-17", state_path,
        report_path=report_path, acceptance_path=acceptance_path)
    check("shadow PASS marker ghi PENDING_ACCEPTANCE, không bật live",
          state["status"] == "shadow_passed"
          and state["acceptance_status"] == "PENDING_ACCEPTANCE"
          and not gdkhq_rollout.enabled(state_path))
    signed = gdkhq_rollout.accept_shadow("2026-08-17", "user",
                                         path=acceptance_path,
                                         rollout_path=state_path)
    check("nghiệm thu PASS chuyển marker sang ENABLED",
          signed["acceptance_status"] == "ACCEPTED"
          and gdkhq_rollout.enabled(state_path)
          and gdkhq_rollout.read_state(state_path)["status"] == "enabled"
          and gdkhq_rollout.read_state(state_path)["accepted_by"] == "user")

    try:
        gdkhq_rollout.accept_shadow("2026-08-17", "user",
                                    path=os.path.join(td, "no_rollout.json"),
                                    rollout_path=os.path.join(td, "missing.json"))
        raise AssertionError("accept_shadow phải từ chối khi chưa có marker shadow PASS")
    except ValueError:
        pass

    fail_path = os.path.join(td, "fail.json")
    fail_trace = dict(trace, passed=False, accounts=[{"label": "SpaceX", "ok": False,
                                                      "error": "BrokerError: timeout",
                                                      "frames": {}, "plan_adjustments": []}])
    _, failed = gdkhq_rollout.write_acceptance_report(
        fail_trace, "FAIL selfcheck", "2026-08-17", fail_path,
        report_path=os.path.join(td, "fail.md"), state_path=os.path.join(td, "fail_acceptance.json"))
    check("FAIL trace là FAILED_REVIEW_REQUIRED, không phải pending bỏ qua",
          failed["acceptance_status"] == "FAILED_REVIEW_REQUIRED"
          and failed["errors"])
    try:
        gdkhq_rollout.accept_shadow("2026-08-17", "user",
                                    path=os.path.join(td, "fail_acceptance.json"),
                                    rollout_path=state_path)
        raise AssertionError("accept_shadow phải từ chối trace FAIL")
    except ValueError:
        pass
    try:
        gdkhq_rollout.record_shadow_pass(fail_path, "2026-08-17", state_path)
        raise AssertionError("record_shadow_pass phải từ chối khi thiếu report_path")
    except ValueError:
        pass
    try:
        gdkhq_rollout.record_shadow_pass(fail_path, "2026-08-17", state_path,
                                         report_path=os.path.join(td, "fail.md"),
                                         acceptance_path=os.path.join(td, "fail_acceptance.json"))
        raise AssertionError("record_shadow_pass phải từ chối trace FAIL")
    except ValueError:
        pass

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
