#!/usr/bin/env python3
"""Selfcheck cho `order_book_shadow_probe.py`.

Bộ này tồn tại vì bản vá 2026-09-23 sửa đúng cái mà checkpoint đọc nhầm: markout coverage
thấp KHÔNG phải thiếu mẫu mà là probe đọc thiếu NGUỒN (`probe_ticks_*.csv`). Mỗi ca dưới
đây phải CHẾT nếu bản vá bị revert — xem chú thích từng ca.
"""
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "order_book_shadow_probe.py")
PASS = []


def run(root):
    env = dict(os.environ, ORDER_BOOK_WC_ROOT=root, ORDER_BOOK_START="2026-08-18")
    return subprocess.run([os.environ.get("PYEXE", "python3"), PROBE],
                          env=env, text=True, capture_output=True, check=True).stdout


def check(name, cond, detail=""):
    PASS.append((name, bool(cond)))
    if not cond:
        raise AssertionError(f"FAIL {name} :: {detail}")


def obs_rec(account, ticker="AAA", oid="C", spread_ticks=1.0, depth=500.0, rec="KEEP"):
    return {
        "schema_version": "orderbook_execution_v1", "policy_version": "spread_depth_v2",
        "trace_id": f"{account}:2026-08-18:P:{oid}", "account": account,
        "plan_date": "2026-08-18", "parent_id": "P", "child_oid": oid, "ticker": ticker,
        "side": "buy", "recorded_at": "2026-08-18T09:15:01", "snapshot_valid": True,
        "latency_snapshot_to_order_ms": 120, "baseline": {"price": 10000, "qty": 100},
        "shadow": {"recommendation": rec},
        "features": {"spread_ticks": spread_ticks, "touch_depth_ratio": depth},
    }


def write_journal(ex, account, rows):
    with open(os.path.join(ex, f"exec_{account}_2026-08-18_journal.csv"), "w", encoding="utf-8") as fh:
        fh.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
        for ts, ticker, oid, px in rows:
            fh.write(f"{ts},FILL,P,{ticker},buy,{oid},100,{px},100,CAPIT,,\n")


# ---------------------------------------------------------------- A. sổ trống
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    out = run(root)
    check("A1 N=0 khi chưa có quan sát", "N=0" in out and "WATCH" in out, out)

# -------------------------------------- B. nguồn L2 (dnse_raw) — hành vi CŨ giữ nguyên
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    with open(os.path.join(ex, "orderbook_shadow_A_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs_rec("A")) + "\n")
    write_journal(ex, "A", [("2026-08-18T09:15:30", "AAA", "C", 10000)])
    with open(os.path.join(ex, "dnse_raw_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        for minute, mid in ((2, 9900), (6, 10100), (16, 9800)):
            fh.write(json.dumps({"ts": f"2026-08-18T09:{15+minute:02d}:01", "kind": "quote_l2",
                                 "account_label": "A", "payload": {"symbol": "AAA",
                                 "bids": [{"price": mid - 50}], "offers": [{"price": mid + 50}]}}) + "\n")
    out = run(root)
    check("B1 đếm quan sát/fill", "N=1" in out and "valid=1" in out and "fill-linked children=1/1" in out, out)
    check("B2 markout đủ 3 mốc từ L2", "1m=1/1" in out and "5m=1/1" in out and "15m=1/1" in out, out)
    # Chết nếu `markout_series()` không còn báo basis, hoặc rơi nhầm sang `last`.
    check("B3 basis = mid khi CÓ L2", "basis mid=1 last=0 none=0" in out, out)
    check("B4 telemetry PASS", "telemetry schema/freshness: PASS" in out, out)

# ------ C. CA CỦA BẢN VÁ: không có L2, chỉ có probe_ticks → phải markout được
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    with open(os.path.join(ex, "orderbook_shadow_main_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs_rec("main")) + "\n")
    write_journal(ex, "main", [("2026-08-18T09:15:30", "AAA", "C", 10000)])
    # KHÔNG có dnse_raw — đúng thực tế paper main (broker=phs không ghi quote_l2).
    with open(os.path.join(ex, "probe_ticks_main_2026-08-18.csv"), "w", encoding="utf-8") as fh:
        fh.write("ts,account,ticker,last\n")
        for minute, px in ((2, 9900), (6, 10100), (16, 9800)):
            fh.write(f"2026-08-18T09:{15+minute:02d}:01,main,AAA,{px}\n")
    out = run(root)
    # ⇒ Revert `load_ticks()`/`markout_series()` là ca này rơi về 0/1 và chết.
    check("C1 markout dựng được từ probe_ticks khi KHÔNG có L2",
          "1m=1/1" in out and "5m=1/1" in out and "15m=1/1" in out, out)
    check("C2 basis = last (không tự nhận là mid)", "basis mid=0 last=1 none=0" in out, out)
    check("C3 tầng PROBE được tách riêng", "[PROBE] N=1" in out, out)
    mk = os.path.join(ex, "orderbook_markout.jsonl")
    check("C4 sinh artifact markout", os.path.exists(mk), mk)
    rec = json.loads(open(mk, encoding="utf-8").read().splitlines()[0])
    check("C5 artifact nối bằng trace_id", rec["trace_id"] == "main:2026-08-18:P:C", rec)
    check("C6 artifact ghi schema riêng, KHÔNG mạo danh orderbook_execution_v1",
          rec["schema_version"] == "orderbook_markout_v1", rec)
    check("C7 artifact ghi basis + stratum",
          rec["markout_basis"] == "last" and rec["stratum"] == "PROBE", rec)
    # BUY khớp 10.000, 1' sau 9.900 ⇒ adverse +100bps (dương = bất lợi).
    check("C8 dấu markout đúng quy ước (dương = adverse)",
          abs(rec["markout_1m_bps"] - 100.0) < 0.01, rec)

# ---- D. account test KHÔNG được lọt vào chuỗi giá (cùng luật với load_observations)
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    with open(os.path.join(ex, "orderbook_shadow_main_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs_rec("main")) + "\n")
    write_journal(ex, "main", [("2026-08-18T09:15:30", "AAA", "C", 10000)])
    with open(os.path.join(ex, "probe_ticks_selfcheck-x_2026-08-18.csv"), "w", encoding="utf-8") as fh:
        fh.write("ts,account,ticker,last\n")
        fh.write("2026-08-18T09:17:01,selfcheck-x,AAA,9900\n")
    out = run(root)
    check("D1 bỏ qua probe_ticks của account test", "1m=0/1" in out, out)
    check("D2 basis=none khi không còn chuỗi nào", "basis mid=0 last=0 none=1" in out, out)
    # D3 gọi THẲNG `load_ticks()`: ở D1/D2 khoá (selfcheck-x, AAA) vốn đã không khớp quan sát
    # (account "main") nên ca đó qua được KỂ CẢ khi bỏ lọc — xác nhận bằng mutation. Lọc
    # phải theo CỘT `account`, không theo tên file, nên phải kiểm ngay tại hàm.
    import importlib.util
    spec = importlib.util.spec_from_file_location("_probe", PROBE)
    mod = importlib.util.module_from_spec(spec)
    os.environ["ORDER_BOOK_WC_ROOT"] = root
    spec.loader.exec_module(mod)
    keys = mod.load_ticks({"2026-08-18"})
    check("D3 load_ticks() LOẠI account test ngay tại nguồn",
          ("selfcheck-x", "AAA") not in keys, sorted(keys))
    # Cùng file, thêm 1 dòng account THẬT: lọc phải theo dòng, không loại cả file.
    with open(os.path.join(ex, "probe_ticks_selfcheck-x_2026-08-18.csv"), "a", encoding="utf-8") as fh:
        fh.write("2026-08-18T09:17:01,main,AAA,9900\n")
    keys = mod.load_ticks({"2026-08-18"})
    check("D4 lọc theo DÒNG, không loại cả file",
          ("main", "AAA") in keys and ("selfcheck-x", "AAA") not in keys, sorted(keys))

# ---- D'. cửa sổ 90s là TRẦN, không phải "điểm kế tiếp bất kỳ"
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    with open(os.path.join(ex, "orderbook_shadow_main_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs_rec("main")) + "\n")
    write_journal(ex, "main", [("2026-08-18T09:15:30", "AAA", "C", 10000)])
    with open(os.path.join(ex, "probe_ticks_main_2026-08-18.csv"), "w", encoding="utf-8") as fh:
        fh.write("ts,account,ticker,last\n")
        # Điểm DUY NHẤT nằm ở fill+40'. Không mốc nào (1/5/15') được nhận nó: markout tại
        # 1 phút mà lấy giá 40 phút sau thì con số bps là của một sự kiện khác. Chuỗi
        # `last` cadence 60s giờ phủ 93% mẫu ⇒ đây là ca thật, không phải giả định.
        fh.write("2026-08-18T09:55:30,main,AAA,9900\n")
    out = run(root)
    check("D5 tick ngoài cửa sổ 90s KHÔNG được nhận",
          "1m=0/1" in out and "5m=0/1" in out and "15m=0/1" in out, out)

# ---------------- E. tách tầng PROBE vs REAL (gộp chung là lỗi đọc của checkpoint 09-23)
with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    with open(os.path.join(ex, "orderbook_shadow_main_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        for i in range(3):
            fh.write(json.dumps(obs_rec("main", oid=f"C{i}", depth=800.0)) + "\n")
    with open(os.path.join(ex, "orderbook_shadow_SpaceX_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs_rec("SpaceX", oid="R0", depth=1.5, rec="REDUCE")) + "\n")
    out = run(root)
    check("E1 PROBE giữ nguyên KEEP, khác-baseline 0%",
          "[PROBE] N=3 · policy KEEP=3 REDUCE=0 DEFER=0 · khác-baseline=0.0%" in out, out)
    check("E2 REAL tách riêng và ĐO ĐƯỢC độ lệch baseline",
          "[REAL] N=1 · policy KEEP=0 REDUCE=1 DEFER=0 · khác-baseline=100.0%" in out, out)
    check("E3 báo cáo touch_depth_ratio median theo tầng",
          "median=800.0x" in out and "median=1.5x" in out, out)

print(f"order_book_shadow_probe_selfcheck: {len(PASS)}/{len(PASS)} PASS "
      f"({len([p for p in PASS if p[1]])} ok, 0 FAIL) — 5 kịch bản A-E")
