#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yearly_attribution.py — vì sao NAV lệch theo NĂM, khi rổ chỉ lệch vài bps?

Vòng review 2 (job Taylor_20260927_052432). AB_R3.md vòng 1 quy 2021 −3pp cho "rebal 2021-11-05 là
rebal đổi weight nặng nhất" — SAI CƠ CHẾ (quant-skeptic bắt): rebal ĐÓ là rebal của RỔ (publish),
còn con số theo năm là của NAV hai book. Script này tách ra bằng chính ledger của 2 chân:
  (1) lợi nhuận theo năm của TỪNG BOOK (`nav_bal_ref`, `nav_lag_ref`) — book nào thực sự lệch;
  (2) NGÀY REBAL của allocator trong mỗi chân — nếu lệch ngày thì con số năm là path-dependence,
      không phải cỡ lệch weight của rổ.
  usage: yearly_attribution.py <ledger_control.csv> <ledger_new.csv>
"""
import sys

import pandas as pd

def load(p):
    d = pd.read_csv(p, low_memory=False)
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    return d

def yearly(nav):
    """Lợi nhuận theo NĂM LỊCH của một chuỗi NAV (giá trị cuối năm / giá trị cuối năm trước)."""
    s = nav.dropna()
    eoy = s.groupby(s.index.year).last()
    first = s.iloc[0]
    prev = pd.Series([first] + list(eoy.values[:-1]), index=eoy.index)
    return (eoy / prev - 1.0) * 100

def series(d, col):
    x = d[d[col].notna()][["ymd", col]].dropna()
    x = x.groupby("ymd")[col].last()
    return x

def main():
    ctl, new = load(sys.argv[1]), load(sys.argv[2])
    print(f"{'năm':<6}{'BAL ctl':>10}{'BAL new':>10}{'Δ':>8}   {'LAG ctl':>10}{'LAG new':>10}{'Δ':>8}"
          f"   {'NAV ctl':>10}{'NAV new':>10}{'Δ':>8}")
    tab = {}
    for name, col in (("BAL", "nav_bal_ref"), ("LAG", "nav_lag_ref"), ("NAV", "combined_nav")):
        tab[name] = (yearly(series(ctl, col)), yearly(series(new, col)))
    yrs = sorted(set(tab["NAV"][0].index) | set(tab["NAV"][1].index))
    for y in yrs:
        row = f"{y:<6}"
        for name in ("BAL", "LAG", "NAV"):
            a, b = tab[name]
            va, vb = a.get(y, float('nan')), b.get(y, float('nan'))
            row += f"{va:>+10.2f}{vb:>+10.2f}{vb - va:>+8.2f}   "
        print(row)
    for name in ("BAL", "LAG", "NAV"):
        a, b = tab[name]
        d = (b - a).abs().dropna()
        print(f"  max |Δ| {name}: {d.max():.2f}pp (năm {d.idxmax()})")

    # (2) ngày rebal của allocator — path dependence
    for label, d in (("control", ctl), ("new", new)):
        r = d[d["rebal_cost"].notna() & (d["rebal_cost"] != 0)]
        days = sorted(r["ymd"].dropna().dt.date.unique())
        print(f"\n{label}: {len(days)} ngày có rebal_cost != 0; 2021: "
              f"{[str(x) for x in days if str(x).startswith('2021')]}")
    a = set(ctl[ctl["rebal_cost"].notna() & (ctl["rebal_cost"] != 0)]["ymd"].dropna().dt.date)
    b = set(new[new["rebal_cost"].notna() & (new["rebal_cost"] != 0)]["ymd"].dropna().dt.date)
    print(f"\nngày rebal CHỈ control: {sorted(str(x) for x in a - b)}")
    print(f"ngày rebal CHỈ new    : {sorted(str(x) for x in b - a)}")

if __name__ == "__main__":
    main()
