#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe-plan generator cho account PAPER `main` — evidence harness, KHÔNG phải chiến lược.

Mục đích duy nhất: đảm bảo executor chạy phiên paper `main` MỖI ngày giao dịch với lệnh
thật sự được work trên quote thật, để 2 chương trình paper tích lũy evidence:
  - EXTREME-regime gate (extreme_regime_enabled=true, chỉ paper main): zero false-trigger
  - vol-scale buy chase-cap (chase_cap_vol_scale_enabled=true, chỉ paper main): wiring trên quote thật
(Mirror plan live SpaceX không dùng được làm nguồn: ngày HOLD = 0 lệnh = 0 evidence;
mirror v23 paper book cũng không: nguồn pt_v22 stale từ 2026-06-25. Xem job
Taylor_20260707_071130.)

Plan mỗi ngày: SELL toàn bộ vị thế paper đang giữ (churn — tạo evidence sell-path +
fill-timing SELL window) + BUY ~30M VND mỗi mã trong basket 6 mã thanh khoản cao
(evidence buy-path: chase-cap, EXTREME buy-pause, fill-timing BUY window).
Giá tham chiếu = close mới nhất từ BQ cache (như plan thật: ref = close ngày signal).

PAPER-ONLY: chỉ ghi plan_main_<date>.json; account main mode=paper (PaperBroker),
không có đường nào chạm tiền thật. Không ghi đè plan đã tồn tại (trừ --force).

Usage: paper_main_probe_plan.py [--date YYYY-MM-DD] [--force] [--dry]
"""
import argparse
import datetime as dt
import json
import os
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC_ROOT)
os.environ.setdefault("TZ", "Asia/Ho_Chi_Minh")

from trading_bot.plan import TradePlan, PlannedOrder  # noqa: E402

PAPER_STATE = os.path.join(WC_ROOT, "secrets", "bot_paper_account.json")  # PAPER_STATE_FILE (label main, legacy path)
CACHE_PARQUET = os.path.join(WC_ROOT, "data", "bq_cache", "ticker_1m.parquet")
BASKET = ["FPT", "MBB", "ACB", "HDB", "VNM", "HPG"]  # thanh khoản cao, không mã nào trong BANNED list
BUY_VALUE_VND = 30_000_000  # mỗi mã; 6 mã ~180M trên NAV paper 1B


def latest_closes(tickers):
    """{ticker: close} + ngày signal (max time) từ BQ cache parquet."""
    import duckdb
    con = duckdb.connect()
    con.execute("PRAGMA threads=1")
    inlist = ",".join(f"'{t}'" for t in tickers)
    rows = con.execute(
        f"SELECT ticker, time, Close FROM '{CACHE_PARQUET}' WHERE ticker IN ({inlist}) "
        f"QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC)=1").fetchall()
    px = {r[0]: float(r[2]) for r in rows if r[2]}
    sig = max((r[1] for r in rows), default=None)
    return px, (str(sig)[:10] if sig else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="plan date YYYY-MM-DD (mặc định hôm nay ICT)")
    ap.add_argument("--force", action="store_true", help="ghi đè plan đã tồn tại")
    ap.add_argument("--dry", action="store_true", help="chỉ in, không ghi file")
    args = ap.parse_args()

    plan_date = args.date or dt.date.today().isoformat()
    if dt.date.fromisoformat(plan_date).weekday() >= 5:
        print(f"[probe-plan] {plan_date} là cuối tuần — bỏ qua.")
        return 0

    held = {}
    if os.path.exists(PAPER_STATE):
        with open(PAPER_STATE, encoding="utf-8") as f:
            held = {s: int(q) for s, q in json.load(f).get("positions", {}).items() if q > 0}

    px, signal_date = latest_closes(sorted(set(BASKET) | set(held)))
    if not px:
        print(f"[probe-plan] ❌ không đọc được giá từ {CACHE_PARQUET} — không ghi plan.")
        return 1

    orders, notes = [], []
    for i, t in enumerate(sorted(held)):
        if t not in px:
            notes.append(f"SELL {t} bỏ qua — thiếu giá trong BQ cache")
            continue
        orders.append(PlannedOrder(id=f"SELL-{t}-{i:02d}", ticker=t, side="sell",
                                   qty=held[t], ref_price=px[t], book="PROBE",
                                   play_type="churn", priority=1,
                                   note="probe harness: thoát vị thế hôm qua"))
    for i, t in enumerate(BASKET):
        if t not in px:
            notes.append(f"BUY {t} bỏ qua — thiếu giá trong BQ cache")
            continue
        qty = int(BUY_VALUE_VND / px[t] // 100) * 100
        if qty < 100:
            notes.append(f"BUY {t} bỏ qua — qty<1 lô tại giá {px[t]:,.0f}")
            continue
        orders.append(PlannedOrder(id=f"BUY-{t}-{i:02d}", ticker=t, side="buy",
                                   qty=qty, ref_price=px[t], book="PROBE",
                                   play_type="churn", priority=5,
                                   note="probe harness: evidence buy-path"))

    plan = TradePlan(plan_date=plan_date, signal_date=signal_date or plan_date,
                     strategy="paper_probe", strategy_version="1.0",
                     state=-1, state_name="PROBE", account="main",
                     nav_basis={"account_nav": 1_000_000_000, "paper_nav": 0, "scale": 0},
                     orders=orders,
                     notes=["PAPER PROBE HARNESS — evidence cho EXTREME gate + vol-scale "
                            "chase-cap, KHÔNG phải khuyến nghị/chiến lược."] + notes)
    print(plan.summary())
    if args.dry:
        print("(dry — không ghi file)")
        return 0
    if os.path.exists(plan.path()) and not args.force:
        print(f"[probe-plan] plan đã tồn tại, không ghi đè: {plan.path()} (dùng --force nếu cần)")
        return 0
    path = plan.save()
    print(f"[probe-plan] ✅ đã ghi {path} ({len(orders)} lệnh)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
