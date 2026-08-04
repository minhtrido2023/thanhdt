#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: probe-plan paper `main` phải SỐNG SÓT qua net_offsetting_orders().

Bug đang sửa (job Taylor_20260804_094514): `mike/bin/paper_main_probe_plan.py` bản cũ mua
ĐÚNG 30M VND/mã mỗi ngày, nên qty mua hôm nay = qty bán hôm qua (cùng lô 100) → hàm LIVE
`trading_bot.plan.net_offsetting_orders()` gộp về net=0 → **0 lệnh thật ra broker** từ
2026-07-28; evidence của EXTREME-regime gate / vol-scale chase-cap / fill-timing đóng băng.

Kiểm 6 việc, KHÔNG chạm production `trading_bot/plan.py` và KHÔNG ghi plan file nào:
  1. REGRESSION — tái hiện bản cũ (giá trị mua cố định) collapse về 0 lệnh.
  2. Bản mới: 5 phiên liên tiếp, MỌI mã trong basket còn ≥1 lệnh net thật mỗi ngày.
  3. Vẫn churn full-basket: mỗi ngày plan THÔ có đủ SELL+BUY cả 6 mã (trước khi net).
  4. Cả buy-path lẫn sell-path có cửa sổ trong tuần (≥1 ngày net BUY, ≥1 ngày net SELL).
  5. Backstop lệch-1-lô: qty mua trùng khít vị thế → vẫn ra lệnh (2 phiên liên tiếp cùng
     THỨ sau kỳ nghỉ dài; và giá chạy đúng chỗ bù lại hệ số).
  6. Giá trị mua giữ bậc ~30M/mã (21–30M), không lệch khỏi thiết kế probe gốc.

Chạy: python3 paper_probe_netting_selfcheck.py     (thêm `env -u TZ` để kiểm TZ-độc lập)
"""
import datetime as dt
import importlib.util
import os
import sys

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)

from trading_bot.plan import net_offsetting_orders  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "paper_main_probe_plan", os.path.join(WC_ROOT, "mike", "bin", "paper_main_probe_plan.py"))
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)

# Giá thật gần nhất của basket (snapshot 2026-08-04 từ secrets/bot_paper_account.json +
# BQ cache) — chỉ dùng làm điểm xuất phát, selfcheck không đọc BQ.
BASE_PX = {"FPT": 73_200.0, "MBB": 25_700.0, "ACB": 22_450.0,
           "HDB": 27_300.0, "VNM": 71_500.0, "HPG": 23_100.0}
DAYS = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"]  # T2..T6
DRIFT = [1.000, 1.007, 0.994, 1.012, 0.998]  # biến động giá ngày-qua-ngày, xác định

fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


def net_of(plan):
    """{ticker: (side, qty)} sau khi qua net_offsetting_orders() — lệnh THẬT ra broker."""
    netted, _adj = net_offsetting_orders(plan)
    return {o.ticker: (o.side, o.qty) for o in netted.orders}


def build_old_style(plan_date, held, px):
    """Tái hiện bản CŨ: mua cố định BUY_VALUE_VND, không hệ số theo thứ, không backstop."""
    plan = probe.build_plan(plan_date, held, px, plan_date)
    for o in plan.orders:      # ép về đúng công thức cũ: floor-lô, 30M cố định, không backstop
        if o.side == "buy":
            o.qty = int(probe.BUY_VALUE_VND / px[o.ticker] // 100) * 100
    return plan


def positions_after(held, netted):
    """Vị thế sau phiên = held + Σbuy − Σsell (paper broker khớp đủ lệnh net)."""
    out = dict(held)
    for t, (side, qty) in netted.items():
        out[t] = out.get(t, 0) + (qty if side == "buy" else -qty)
    return {t: q for t, q in out.items() if q > 0}


print(f"=== paper_probe_netting_selfcheck (TZ={os.environ.get('TZ', '<unset>')}) ===\n")

# --- 1. REGRESSION: bản cũ collapse về 0 lệnh -------------------------------------------
print("[1] Regression — bản CŨ (mua cố định 30M/mã) sau netting:")
held = {t: int(30_000_000 / p // 100) * 100 for t, p in BASE_PX.items()}
old_plan = build_old_style(DAYS[1], held, BASE_PX)
old_netted = net_of(old_plan)
check(len(old_netted) == 0,
      f"bản cũ: {len(old_netted)} lệnh ra broker (kỳ vọng 0 — đúng bug đang sửa)")

# --- 2/3/4/6. Bản mới, 5 phiên liên tiếp ------------------------------------------------
print("\n[2-4,6] Bản MỚI — 5 phiên liên tiếp T2→T6:")
held = {"FPT": 400, "MBB": 1200, "ACB": 1300, "HDB": 1100, "VNM": 400, "HPG": 1300}
px = dict(BASE_PX)
sides_seen, all_days_ok, value_ok = set(), True, True
for d, drift in zip(DAYS, DRIFT):
    px = {t: round(p * drift, -1) for t, p in px.items()}
    plan = probe.build_plan(d, held, px, d)

    raw_sell = {o.ticker for o in plan.orders if o.side == "sell"}
    raw_buy = {o.ticker for o in plan.orders if o.side == "buy"}
    churn_ok = raw_buy == set(probe.BASKET) and raw_sell >= set(held)
    target = probe.BUY_VALUE_VND * probe.BUY_VALUE_FACTOR[dt.date.fromisoformat(d).weekday()]
    for o in plan.orders:                                     # [6] bậc giá trị mua
        # sai số cho phép = nửa lô (làm tròn lô gần nhất) + 1 lô nếu backstop đã cộng thêm
        tol = o.ref_price * 100 * 1.5
        if o.side == "buy" and abs(o.qty * o.ref_price - target) > tol:
            value_ok = False
            print(f"      ↳ [6] {o.ticker} mua {o.qty * o.ref_price / 1e6:,.1f}M vs "
                  f"target {target / 1e6:,.1f}M (tol {tol / 1e6:,.1f}M)")

    netted = net_of(plan)
    missing = [t for t in probe.BASKET if netted.get(t, (None, 0))[1] <= 0]
    sides_seen.update(s for s, _ in netted.values())
    wd = dt.date.fromisoformat(d).weekday()
    detail = ", ".join(f"{t}:{s[0].upper()}{q}" for t, (s, q) in sorted(netted.items()))
    vnd = sum(q * px[t] for t, (_s, q) in netted.items())
    print(f"    {d} (thứ {wd + 2}, factor {probe.BUY_VALUE_FACTOR[wd]:.2f}) → "
          f"{len(netted)} lệnh net / {vnd / 1e6:,.1f}M VND  [{detail}]")
    if missing or not churn_ok:
        all_days_ok = False
        print(f"      ↳ thiếu lệnh: {missing} | churn full-basket: {churn_ok}")
    held = positions_after(held, netted)

check(all_days_ok, "mọi phiên: cả 6 mã còn ≥1 lệnh net thật + plan thô vẫn SELL+BUY đủ basket")
check({"buy", "sell"} <= sides_seen, f"có cả net BUY và net SELL trong tuần (thấy: {sorted(sides_seen)})")
check(value_ok, "mọi lệnh BUY bám target 21–30M/mã trong sai số làm tròn lô (giữ bậc ~30M gốc)")

# --- 5. Backstop lệch-1-lô ---------------------------------------------------------------
print("\n[5] Backstop khi qty mua trùng khít vị thế đang giữ:")
# (a) hai phiên liên tiếp CÙNG THỨ (kỳ nghỉ dài) → cùng factor, giá không đổi
d = "2026-08-04"                                              # thứ Ba
f = probe.BUY_VALUE_FACTOR[dt.date.fromisoformat(d).weekday()]
held_a = {t: int(30_000_000 * f / p // 100) * 100 for t, p in BASE_PX.items()}
net_a = net_of(probe.build_plan(d, held_a, BASE_PX, d))
check(len(net_a) == len(probe.BASKET) and all(q > 0 for _s, q in net_a.values()),
      f"cùng THỨ + giá không đổi: {len(net_a)}/{len(probe.BASKET)} mã vẫn có lệnh net")

# (b) giá chạy đúng chỗ bù lại hệ số (T2 factor 1.00 sau T6 factor 0.85)
d2, f2 = "2026-08-03", probe.BUY_VALUE_FACTOR[0]
px_b = {t: p * (f2 / probe.BUY_VALUE_FACTOR[4]) for t, p in BASE_PX.items()}
held_b = {t: int(30_000_000 * probe.BUY_VALUE_FACTOR[4] / p // 100) * 100
          for t, p in BASE_PX.items()}
net_b = net_of(probe.build_plan(d2, held_b, px_b, d2))
check(len(net_b) == len(probe.BASKET) and all(q > 0 for _s, q in net_b.values()),
      f"giá bù đúng hệ số: {len(net_b)}/{len(probe.BASKET)} mã vẫn có lệnh net")

# --- kết luận ---------------------------------------------------------------------------
print("\n=== " + ("✅ PASS — tất cả check đạt" if not fails
                  else f"❌ FAIL — {len(fails)} check hỏng: {fails}") + " ===")
sys.exit(1 if fails else 0)
