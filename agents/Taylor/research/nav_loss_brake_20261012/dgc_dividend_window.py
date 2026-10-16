#!/usr/bin/env python3
"""Mục 1 vòng 3 — kiểm ngày cổ tức tiền DGC (GDKHQ 2026-09-14, trả 2026-09-25) có tạo BƯỚC NHẢY GIẢ
trên chuỗi NAV TỔNG của ZaloPay hay không. Chỉ ĐỌC dữ liệu thật; in bảng phiên 09-10 → 09-29:
dòng nav_history, giá đơn vị + biến động ngày của CHÍNH sổ monitor dùng, giá DGC (BQ Price = chưa
điều chỉnh), và monitor nói gì về phiên đó.
Dùng: python3 dgc_dividend_window.py [--from 2026-09-10 --to 2026-09-29]"""
import argparse
import csv
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "bin")))
import nav_loss_brake_monitor as m  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--account", default="ZaloPay")
ap.add_argument("--from", dest="lo", default="2026-09-10")
ap.add_argument("--to", dest="hi", default="2026-09-29")
args = ap.parse_args()
lo, hi = datetime.date.fromisoformat(args.lo), datetime.date.fromisoformat(args.hi)
ctx = m.Ctx(state_dir=os.path.join(HERE, "_no_state"),
            now=datetime.datetime(2026, 10, 12, 22, 5, tzinfo=m.ICT))
th, th_err = m.load_thresholds(ctx.rules_path)
no = m.load_profiles(ctx.secrets_path)[args.account]
chain = m.build_chain(ctx, args.account, ctx.now.date())
raw = {r["date"]: r for r in csv.DictReader(open(os.path.join(
    ctx.exec_dir, f"nav_history_{args.account}.csv"), encoding="utf-8"))}
px = {r["time"]: float(r["Price"]) for r in csv.DictReader(open(os.path.join(
    HERE, "bq_price_DGC_20260706_20261009.csv"), encoding="utf-8"))}
led = {r["date"]: r for r in chain["ledger"]}
dates = [d for d in sorted(led) if lo <= d <= hi]
print(f"{args.account} — NAV TỔNG quanh cổ tức tiền DGC (10.000 cp × 8.000đ; GDKHQ 14/09, trả 25/09)")
print(f"{'phiên':<11}{'NAV':>14}{'cổ phiếu':>14}{'tiền':>13}{'egg':>13}{'phải thu':>11} "
      f"{'ước tính':<8}{'giá ĐV':>10}{'ngày':>8}{'từ đỉnh':>9}{'DGC':>8}{'DGC ngày':>9}  monitor")
prev_px = None
for d in dates:
    r, x = led[d], raw[d.isoformat()]
    g = m.lever_guard(ctx, args.account, no, d, th["lever_package_id"], [], [])
    res = m.evaluate(ctx, args.account, d, chain, th, th_err, [], g)
    p = px.get(d.isoformat())
    verdict = " · ".join(f"{b}={res[b]['status']}" + ("(không đẩy)" if res[b].get("quiet") else "")
                         for b in m.BRAKES)
    dd = res["drawdown"].get("value")
    print(f"{d}  {float(x['nav']):>13,.0f}{float(x['mtm_stock']):>14,.0f}{float(x['cash']):>13,.0f}"
          f"{float(x['egg_assets']):>13,.0f}{float(x['cum_dividend_excl'] or 0):>11,.0f} "
          f"{(x['nav_is_estimate'] or '-'):<8}{r['unit_price']:>10,.2f}"
          f"{m.pct(res['daily'].get('value')):>8}{m.pct(dd):>9}"
          f"{(f'{p:,.0f}' if p else '-'):>8}"
          f"{(m.pct(p / prev_px - 1) if p and prev_px else '-'):>9}  {verdict}")
    prev_px = p or prev_px
moves = [(b, led[b]["unit_price"] / led[a]["unit_price"] - 1) for a, b in zip(dates, dates[1:])]
lo_m, hi_m = min(moves, key=lambda t: t[1]), max(moves, key=lambda t: t[1])
print(f"\nBiến động ngày trong cửa sổ (giá đơn vị, dòng-so-dòng): giảm mạnh nhất {m.pct(lo_m[1])} ngày "
      f"{lo_m[0]} · tăng mạnh nhất {m.pct(hi_m[1])} ngày {hi_m[0]} · ngưỡng phanh ngày {m.pct(th['daily'], 0)}.")
