# -*- coding: utf-8 -*-
"""A/B report — S2 dip-cross (ab_dip) vs blind-cross (ab_cross) trên paper fills.

  python bot_ab_report.py              # toàn bộ lịch sử fills
  python bot_ab_report.py --days 10    # chỉ N ngày gần nhất

So sánh từng cell (date, ticker, side) có fill ở CẢ HAI account:
  save_bps = (vwap_cross − vwap_dip)/vwap_cross × 1e4 × (+1 mua / −1 bán)
  → dương = dip-cross khớp giá tốt hơn. Backtest kỳ vọng ~ +2–3.5bps/side.
Cảnh báo lệch khối lượng (dip fill thiếu = chi phí ẩn không hiện trong giá).
Nguồn: data/bot_paper_ab_cross.json / bot_paper_ab_dip.json (fills của PaperBroker).
Output: data/exec_ab_history.csv (append-dedup theo date+ticker+side).
"""
import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "data", "exec_ab_history.csv")


def load_fills(label):
    path = os.path.join(WD, "data", f"bot_paper_{label}.json")
    if not os.path.exists(path):
        sys.exit(f"❌ chưa có {path} — account {label} chưa chạy phiên nào")
    fills = json.load(open(path, encoding="utf-8")).get("fills", [])
    if not fills:
        return pd.DataFrame(columns=["date", "symbol", "side", "qty", "price"])
    df = pd.DataFrame(fills)
    df["date"] = df["ts"].str[:10]
    return df


def vwap_cells(df):
    """→ index (date,symbol,side): vwap, qty, value."""
    df = df.assign(value=df["qty"] * df["price"])
    g = df.groupby(["date", "symbol", "side"]).agg(
        qty=("qty", "sum"), value=("value", "sum"))
    g["vwap"] = g["value"] / g["qty"]
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None, help="chỉ N ngày gần nhất")
    args = ap.parse_args()

    a = vwap_cells(load_fills("ab_cross"))
    b = vwap_cells(load_fills("ab_dip"))
    m = a.join(b, lsuffix="_cross", rsuffix="_dip", how="outer")

    if args.days:
        dates = sorted({d for d, _, _ in m.index})[-args.days:]
        m = m[m.index.get_level_values(0).isin(dates)]

    both = m.dropna(subset=["vwap_cross", "vwap_dip"]).reset_index()
    if both.empty:
        print("Chưa có cell (date,ticker,side) nào fill ở cả hai account.")
        only = m[m["vwap_cross"].isna() | m["vwap_dip"].isna()]
        if len(only):
            print(f"({len(only)} cell mới chỉ fill 1 bên — chờ thêm phiên)")
        return

    sgn = both["side"].map({"buy": 1, "sell": -1})
    both["save_bps"] = sgn * (both["vwap_cross"] - both["vwap_dip"]) \
        / both["vwap_cross"] * 1e4
    both["qty_gap_pct"] = 100 * (both["qty_dip"] - both["qty_cross"]) \
        / both["qty_cross"]

    print(f"===== A/B dip-cross vs blind-cross — {both['date'].nunique()} ngày, "
          f"{len(both)} cell =====")
    w = both["value_cross"]
    print(f"save_bps:  mean {both['save_bps'].mean():+.2f} | "
          f"value-weighted {(both['save_bps']*w).sum()/w.sum():+.2f} | "
          f"median {both['save_bps'].median():+.2f} | "
          f"win {(100*(both['save_bps']>0).mean()):.0f}%")
    for s, g in both.groupby("side"):
        print(f"  {s:4s}: mean {g['save_bps'].mean():+.2f} bps  (n={len(g)})")
    gap = both[both["qty_gap_pct"].abs() > 5]
    if len(gap):
        print(f"⚠ {len(gap)} cell lệch KL >5% (dip fill thiếu/thừa) — giá chưa kể "
              f"chi phí cơ hội phần thiếu:")
        print(gap[["date", "symbol", "side", "qty_cross", "qty_dip",
                   "qty_gap_pct"]].to_string(index=False))

    print("\n----- theo ngày -----")
    day = both.groupby("date").apply(
        lambda g: pd.Series({"save_bps": (g["save_bps"]*g["value_cross"]).sum()
                             / g["value_cross"].sum(), "cells": len(g)}),
        include_groups=False)
    print(day.to_string(float_format=lambda x: f"{x:+.2f}"))

    print("\n----- chi tiết cell -----")
    cols = ["date", "symbol", "side", "vwap_cross", "vwap_dip", "save_bps"]
    print(both[cols].to_string(index=False,
          float_format=lambda x: f"{x:,.1f}"))

    # append-dedup lịch sử
    hist = both[["date", "symbol", "side", "vwap_cross", "vwap_dip",
                 "qty_cross", "qty_dip", "save_bps"]]
    if os.path.exists(OUT):
        old = pd.read_csv(OUT, dtype={"date": str})
        hist = pd.concat([old, hist]).drop_duplicates(
            ["date", "symbol", "side"], keep="last")
    hist.sort_values(["date", "symbol", "side"]).to_csv(OUT, index=False)
    print(f"\n→ lịch sử: {OUT} ({len(hist)} cell). "
          f"Đủ ~3-4 tuần thì kết luận (kỳ vọng +2-3.5bps, t>2).")


if __name__ == "__main__":
    main()
