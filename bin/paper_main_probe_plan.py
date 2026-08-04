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

⚠️ NETTING (sửa 2026-08-04, job Taylor_20260804_094514): `net_offsetting_orders()` trong
`trading_bot/plan.py` (LIVE ở bot_execute.py từ commit ab20a77, 2026-07-27) gộp MỌI cặp
lệnh ngược chiều CÙNG MÃ trong 1 plan thành 1 lệnh net = Σbuy − Σsell; net==0 → KHÔNG
lệnh nào ra broker. Bản cũ mua ĐÚNG 30M/mã mỗi ngày nên qty mua hôm nay ≈ qty bán hôm qua
(cùng lô 100) → net 0 cả 6 mã → 0 lệnh thật từ 2026-07-28, evidence 3 chương trình đóng
băng 8 ngày. KHÔNG sửa đường code production (netting là hành vi đúng cho plan thật); thay
vào đó probe cố ý ĐỔI GIÁ TRỊ MUA theo THỨ (`BUY_VALUE_FACTOR`) để mỗi mã luôn còn một
phần dư net thật ra broker, + backstop lệch 1 lô khi qty trùng khít. Vẫn SELL+BUY cả 6 mã
mỗi ngày (churn full-basket không đổi) — chỉ phần dư mới chạm broker, đúng thiết kế netting.

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

# Hệ số giá trị mua theo THỨ (0=T2 … 4=T6) — xem cảnh báo NETTING ở docstring.
# 5 giá trị ĐÔI MỘT KHÁC NHAU ⇒ hai phiên giao dịch liên tiếp (kể cả T6→T2, kể cả sau nghỉ
# lễ lệch thứ) luôn có giá trị mục tiêu lệch ≥0,15×30M = 4,5M/mã ⇒ net qty ≥1 lô. Chuỗi
# chọn sao cho có 3 ngày net BUY (T2/T4/T6) + 2 ngày net SELL (T3/T5) mỗi tuần: buy-path
# (chase-cap, EXTREME buy-pause) và sell-path đều có cửa sổ đều đặn. Dải 21–30M/mã ⇒ giữ
# nguyên bậc ~30M/mã như thiết kế gốc.
BUY_VALUE_FACTOR = {0: 1.00, 1: 0.75, 2: 0.90, 3: 0.70, 4: 0.85}


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


def build_plan(plan_date, held, px, signal_date):
    """Dựng TradePlan probe cho 1 ngày. Tách khỏi main() để selfcheck gọi được không cần BQ/IO.

    held = {ticker: qty đang giữ}, px = {ticker: ref_price}.
    """
    weekday = dt.date.fromisoformat(plan_date).weekday()
    factor = BUY_VALUE_FACTOR[weekday]
    target_vnd = BUY_VALUE_VND * factor

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
        # Làm tròn về lô GẦN NHẤT (không phải floor): với mã giá cao 1 lô ≈ 7M VND, floor ở
        # hệ số thấp cắt tới −30% giá trị mục tiêu (FPT @73,2k: 21M → 200cp = 14,6M) làm lệch
        # bậc ~30M/mã của thiết kế probe. Nearest giữ sai số ≤ nửa lô.
        qty = int(round(target_vnd / px[t] / 100)) * 100
        if qty < 100:
            notes.append(f"BUY {t} bỏ qua — qty<1 lô tại giá {px[t]:,.0f}")
            continue
        # Backstop chống net_offsetting_orders() gộp về 0: nếu qty mua hôm nay trùng KHÍT qty
        # đang giữ (giá chạy đúng chỗ bù lại hệ số, hoặc 2 phiên liên tiếp cùng THỨ sau kỳ nghỉ
        # dài), lệch 1 lô để luôn còn ≥1 lô net thật ra broker.
        if qty == held.get(t, 0):
            qty += 100
            notes.append(f"BUY {t} +1 lô (backstop netting: qty trùng vị thế đang giữ {held[t]:,})")
        orders.append(PlannedOrder(id=f"BUY-{t}-{i:02d}", ticker=t, side="buy",
                                   qty=qty, ref_price=px[t], book="PROBE",
                                   play_type="churn", priority=5,
                                   note="probe harness: evidence buy-path"))

    return TradePlan(
        plan_date=plan_date, signal_date=signal_date or plan_date,
        strategy="paper_probe", strategy_version="1.1",
        state=-1, state_name="PROBE", account="main",
        nav_basis={"account_nav": 1_000_000_000, "paper_nav": 0, "scale": 0},
        orders=orders,
        notes=["PAPER PROBE HARNESS — evidence cho EXTREME gate + vol-scale "
               "chase-cap, KHÔNG phải khuyến nghị/chiến lược.",
               f"BUY target {target_vnd:,.0f}đ/mã (factor {factor:.2f}, thứ {weekday + 2}) — "
               f"cố ý lệch giá trị theo ngày để net_offsetting_orders() không gộp về 0 lệnh."]
        + notes)


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

    plan = build_plan(plan_date, held, px, signal_date)
    orders = plan.orders
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
