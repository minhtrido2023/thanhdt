#!/usr/bin/env python3
"""Order-book shadow v1: policy/logging thuần, fail-open khi snapshot không hợp lệ."""
import json
import os
import tempfile
from types import SimpleNamespace

os.environ["MIKE_BOT_TEST_MODE"] = "1"
from trading_bot.executor import Executor  # noqa: E402


def snapshot(attempt, bid, ask, depth, valid=True):
    return {
        "schema_version": "orderbook_l2_v1", "symbol": "AAA",
        "captured_epoch_ms": attempt - 100, "source_time_status": "ok" if valid else "missing",
        "source_age_ms": 100 if valid else None,
        "price_unit": "VND", "quantity_unit": "shares",
        "bids": [{"price": bid, "quantity": depth}],
        "offers": [{"price": ask, "quantity": depth}],
    }


with tempfile.TemporaryDirectory() as tmp:
    sink = os.path.join(tmp, "shadow.jsonl")
    os.environ["ORDER_BOOK_TEST_SINK"] = sink
    ex = object.__new__(Executor)
    ex.cfg = {
        "order_book_shadow_enabled": True, "order_book_snapshot_max_age_ms": 5000,
        "order_book_shadow_policy_version": "spread_depth_v1",
        "order_book_reduce_spread_ticks": 2, "order_book_defer_spread_ticks": 4,
        "order_book_reduce_depth_ratio": 1, "order_book_defer_depth_ratio": 0.5,
    }
    ex.label = "paper"
    ex.plan = SimpleNamespace(plan_date="2026-08-18")
    ex.orderbook_file = sink
    order = SimpleNamespace(id="P", ticker="AAA", side="buy", book="CAPIT")
    attempt = 2_000_000
    cases = [
        ("K", snapshot(attempt, 10000, 10100, 1000), "KEEP"),
        ("R", snapshot(attempt, 10000, 10200, 500), "REDUCE"),
        ("D", snapshot(attempt, 10000, 10400, 100), "DEFER"),
        ("I", snapshot(attempt, 10000, 10400, 100, valid=False), "KEEP"),
    ]
    for oid, snap, _ in cases:
        q = SimpleNamespace(l2_snapshot=snap, exchange="HOSE")
        assert ex._order_book_shadow(order, q, oid, 1000, 10100, True, "hybrid", attempt) is None
    rows = [json.loads(x) for x in open(sink, encoding="utf-8")]
    assert [r["shadow"]["recommendation"] for r in rows] == [x[2] for x in cases]
    assert rows[1]["shadow"]["qty"] == 500 and rows[2]["shadow"]["qty"] == 0
    assert rows[3]["snapshot_valid"] is False
    assert all(r["behavior_contract"] == "LOG_ONLY_NO_BROKER_PATH" for r in rows)

print("order_book_shadow_selfcheck: PASS (4 policy/fail-open scenarios)")
