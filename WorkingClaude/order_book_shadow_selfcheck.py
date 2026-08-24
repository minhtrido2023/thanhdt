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

    # G1 — khoá nối phải mang plan_date: probe dedup theo `trace_id` XUYÊN NGÀY, mà `o.id` do
    # plan sinh nên có thể lặp lại ngày hôm sau ⇒ thiếu ngày là mất mẫu lặng lẽ.
    assert all(r["trace_id"] == f"paper:2026-08-18:P:{oid}"
               for r, (oid, _, _) in zip(rows, cases)), [r["trace_id"] for r in rows]
    # G2 — cả 2 mức 1 được ghi để đọc lại được depth theo quy ước phía đối diện.
    f = rows[0]["features"]
    assert f["touch_side"] == "offer" and f["bid_qty"] == 1000 and f["ask_qty"] == 1000

    # G3 — CỬA SỔ TRIAL: plan_date TRƯỚC mốc bắt đầu ⇒ KHÔNG ghi thêm dòng nào. Đây là bất
    # biến, không phải giá trị đo tại một ngày: mốc lấy từ env như chính probe dùng.
    n_before = len(rows)
    ex.plan = SimpleNamespace(plan_date="2026-08-17")
    q = SimpleNamespace(l2_snapshot=snapshot(attempt, 10000, 10100, 1000), exchange="HOSE")
    ex._order_book_shadow(order, q, "EARLY", 1000, 10100, True, "hybrid", attempt)
    assert len(open(sink, encoding="utf-8").read().splitlines()) == n_before

    # G4 — cùng lệnh đó, hạ mốc bắt đầu bằng env ⇒ ghi bình thường (chứng minh G3 chặn vì
    # NGÀY chứ không phải vì một lỗi im lặng nào khác).
    os.environ["ORDER_BOOK_START"] = "2026-08-01"
    try:
        ex._order_book_shadow(order, q, "EARLY", 1000, 10100, True, "hybrid", attempt)
    finally:
        os.environ.pop("ORDER_BOOK_START", None)
    tail = json.loads(open(sink, encoding="utf-8").read().splitlines()[-1])
    assert len(open(sink, encoding="utf-8").read().splitlines()) == n_before + 1
    assert tail["trace_id"] == "paper:2026-08-17:P:EARLY"

# ================================================================ G5 — mối nối broker↔executor
# Đây là chỗ chương trình có thể chết LẶNG LẼ: `snapshot_valid` đòi `source_time_status=="ok"`,
# mà status đó do `DNSEBroker._l2_source_time()` parse trường `time` của feed. Feed đổi định dạng
# (hoặc bỏ trường) ⇒ MỌI quan sát thành invalid ⇒ probe in valid=0 mà không ai biết vì sao.
# Nên test đi qua ĐÚNG hàm của broker, với ĐỊNH DẠNG THẬT đo được từ DNSE ngày 2026-08-17:
#   GET /price/TV1/quotes/latest → quotes[0]["time"] == "2026-08-17 14:03:30.279"
# (dấu CÁCH, có mili-giây, không hậu tố múi giờ — KHÁC fixture cũ "2026-08-12T10:00:00").
import tempfile as _tf  # noqa: E402
from trading_bot.brokers import DNSEBroker  # noqa: E402
from trading_bot.vn_market import now_ict  # noqa: E402
from trading_bot.account_ids import SPACEX as SPACEX_ACCOUNT, ZALOPAY as ZALOPAY_ACCOUNT

with _tf.TemporaryDirectory() as tmp:
    os.environ["DNSE_L2_LOG_SEC"] = "0"
    sink = os.path.join(tmp, "shadow.jsonl")
    os.environ["ORDER_BOOK_TEST_SINK"] = sink
    b = DNSEBroker(account_id=SPACEX_ACCOUNT, label="SpaceX")
    b._raw_log = os.path.join(tmp, "dnse_raw_2099-01-01.jsonl")
    # Neo vào đồng hồ ICT ngay lúc chạy (KHÔNG hằng số ngày) — test phải đúng dưới `env -u TZ`
    # và không được tự mốc theo thời gian (§16 + §23 hệ luận 1).
    src = (now_ict().replace(tzinfo=None) - __import__("datetime").timedelta(milliseconds=200))
    qt = {"symbol": "TV1",
          "bid": [{"price": 20.2, "quantity": 300}],
          "offer": [{"price": 20.3, "quantity": 400}],
          "time": src.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}
    snap = b._log_l2("TV1", qt, {"symbol": "TV1", "matchPrice": 20300,
                                 "totalVolumeTraded": 39500})
    assert snap and snap["source_time_status"] == "ok", snap and snap.get("source_time_status")
    assert 0 <= snap["source_age_ms"] <= 5000, snap["source_age_ms"]

    ex.plan = SimpleNamespace(plan_date="2026-08-18")
    ex.orderbook_file = sink
    q = SimpleNamespace(l2_snapshot=snap, exchange="HOSE")
    ex._order_book_shadow(order, q, "E2E", 400, 20300, True, "hybrid",
                          int(__import__("time").time() * 1000))
    row = json.loads(open(sink, encoding="utf-8").read().splitlines()[-1])
    assert row["snapshot_valid"] is True, row
    assert row["features"]["bid"] == 20200.0 and row["features"]["ask"] == 20300.0
    os.environ.pop("DNSE_L2_LOG_SEC", None)

print("order_book_shadow_selfcheck: PASS (4 policy/fail-open + trace-key + trial-window + "
      "broker↔executor e2e với định dạng `time` THẬT của DNSE)")
