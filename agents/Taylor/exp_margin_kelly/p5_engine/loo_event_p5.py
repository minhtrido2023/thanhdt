#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LEAVE-ONE-EVENT-OUT tang ENGINE (BUOC D, job Taylor_20260803_101341).

Ly do phai co: p3 §4.2 da chung minh LOO theo NAM la AO ANH trong mot he compounding — mot su kien
lai som lam moi nam sau do "co ve" dong gop, nen bo 1 nam khong bao gio lo ra su that "1 dot ganh het".
Chi LOO theo SU KIEN moi tra loi duoc. Doi chieu: cau2_engine_decomp.py cho thay >50% dCAGR o f=1,3
roi NGOAI cua so nam giu — dau hieu dien hinh cua "lai som roi compound", tuc phai kiem bang LOO su kien.

Ngoai ra kiem tra INERT: chan INERT_f13 (knob CAPIT_LEVER_LOO KHONG dat) phai tai lap E125_f13 TUYET DOI,
chung minh hunk moi them la byte-inert khi tat — dieu kien de moi chan LOO ben tren dang tin.

Chay: $DNA_PYEXE loo_event_p5.py
"""
import glob
import os

import numpy as np
import pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data/"
HERE = os.path.dirname(os.path.abspath(__file__))
# chi so su kien -> nhan (chi so theo engine, xem dong [capit-size ... E<i> ...])
EV = {0: "2014-05-08 (IS, dot dau, vay 25,9% NAV)",
      12: "2023-10-30 (OOS, vay tuyet doi lon nhat 88,7B)",
      14: "2024-08-05 (OOS, r_i am -0,53%)",
      16: "2025-10-20 (OOS, r_i +33,8%)",
      17: "2026-03-09 (OOS, gan cuoi mau)"}


def nav(tag):
    g = [p for p in sorted(glob.glob(DATA + f"*exp_{tag}_univpit*.csv"))
         if not p.endswith(("_borrowledger.csv", "_leveraudit.csv"))]
    if not g:
        return None
    df = pd.read_csv(g[0], low_memory=False)
    d = df.dropna(subset=["combined_nav"]).copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    s = d.groupby("ymd")["combined_nav"].last().sort_index()
    return s[s > 0]


def cagr(s, a=None, b=None):
    if a:
        s = s[(s.index >= a) & (s.index <= b)]
    y = (s.index[-1] - s.index[0]).days / 365.25
    return 100 * ((s.iloc[-1] / s.iloc[0]) ** (1 / y) - 1)


def mdd(s):
    return 100 * (s / s.cummax() - 1).min()


ctl, full, inert = nav("D0_control"), nav("E125_f13"), nav("INERT_f13")

print("=" * 112)
print("KIEM TRA INERT — hunk CAPIT_LEVER_LOO phai VO HAI khi khong dat")
print("=" * 112)
if inert is None or full is None:
    print("  thieu chan INERT_f13 hoac E125_f13")
else:
    idx = full.index.intersection(inert.index)
    dmax = float(np.abs(full.reindex(idx).values - inert.reindex(idx).values).max())
    print(f"  E125_f13 (truoc khi them knob) vs INERT_f13 (sau khi them, knob TAT)")
    print(f"  CAGR {cagr(full):.6f}% vs {cagr(inert):.6f}%   |   NAV cuoi "
          f"{full.iloc[-1]/1e9:.6f}B vs {inert.iloc[-1]/1e9:.6f}B")
    print(f"  sai lech NAV tuyet doi lon nhat tren {len(idx)} phien = {dmax:,.2f} VND  -> "
          f"{'INERT DUNG' if dmax < 1.0 else '*** KHONG INERT — moi ket qua LOO ben duoi VO GIA TRI ***'}")

print("\n" + "=" * 112)
print("LEAVE-ONE-EVENT-OUT — bo don bay o DUNG 1 su kien (cac su kien khac giu nguyen f=1,3 @12,5%)")
print("=" * 112)
d_full = cagr(full) - cagr(ctl)
dO_full = (cagr(full, "2020-01-01", "2026-12-31") - cagr(ctl, "2020-01-01", "2026-12-31"))
print(f"  Chan day du  : dCAGR {d_full:+.4f}pp   dOOS {dO_full:+.4f}pp   MaxDD {mdd(full):.3f}%")
print(f"{'bo su kien':<44}{'dCAGR':>10}{'% edge mat':>12}{'dOOS':>10}{'MaxDD':>10}   ket luan")
rows = []
for i, lbl in EV.items():
    s = nav(f"L13e{i}")
    if s is None:
        print(f"  E{i}: thieu chan"); continue
    d = cagr(s) - cagr(ctl)
    lost = (d_full - d) / d_full * 100 if d_full else float("nan")
    dO = cagr(s, "2020-01-01", "2026-12-31") - cagr(ctl, "2020-01-01", "2026-12-31")
    verdict = "***GANH >=50% EDGE***" if lost >= 50 else ("dong gop lon" if lost >= 25 else "phan tan, lanh manh")
    print(f"  E{i:<2} {lbl:<40}{d:>9.4f}pp{lost:>11.1f}%{dO:>9.4f}pp{mdd(s):>9.3f}%   {verdict}")
    rows.append({"event": i, "label": lbl, "dCAGR": d, "pct_edge_lost": lost,
                 "dOOS": dO, "MaxDD": mdd(s)})
R = pd.DataFrame(rows)
R.to_csv(os.path.join(HERE, "loo_event_p5.csv"), index=False)
if len(R):
    w = R.loc[R["pct_edge_lost"].idxmax()]
    print(f"\n  Su kien ganh nang nhat: E{int(w['event'])} {w['label']} = {w['pct_edge_lost']:.1f}% tong edge")
    print(f"  -> {'RUI RO: 1 dot ganh phan lon edge (giong bay p3 §4.2)' if w['pct_edge_lost'] >= 50 else 'edge PHAN TAN qua nhieu dot — khong phai ao anh 1-su-kien'}")
print("\n-> loo_event_p5.csv")
