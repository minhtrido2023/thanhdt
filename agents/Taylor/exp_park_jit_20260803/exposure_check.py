"""Do TY TRONG CO PHIEU THUC TE tung cau hinh (job Taylor_20260804_012953).

Vi sao can: CAGR/MaxDD la HE QUA; cai user thuc su chon la "giu bao nhieu beta co phieu".
Bang nay do truc tiep tu so mo phong (bal/lag _stocks_ref + _etf_ref chia combined_nav),
khong suy dien tu ket qua. Chi doc CSV da sinh — khong chay lai engine.
"""
import os

import numpy as np
import pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/data"
B = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg"
LEGS = [
    ("A0/Conservative(0.70)", f"{B}_wtnamecap_advprice_exp_agg_A0_gate_univpit.csv"),
    ("F1 (0.80)",             f"{B}_park3-80_wtnamecap_advprice_exp_agg_F1_t80_univpit.csv"),
    ("F2 (0.85)",             f"{B}_park3-85_wtnamecap_advprice_exp_agg_F2_t85_univpit.csv"),
    ("F3 (0.90)",             f"{B}_park3-90_wtnamecap_advprice_exp_agg_F3_t90_univpit.csv"),
    ("G2 (band 6%)",          f"{B}_wtnamecap_advprice_exp_agg_G2_b06_univpit.csv"),
    ("E LIVE",                f"{B}_wtnamecap_advprice_exp_v3_E_both_off_univpit.csv"),
]

print(f"{'Cau hinh':24s} {'eq%tb':>7s} {'eq%p95':>7s} {'park%tb':>8s} {'cash%tb':>8s} "
      f"{'eq% 2022':>9s} {'eq% 2021':>9s}")
for lab, f in LEGS:
    d = pd.read_csv(os.path.join(D, f), low_memory=False)
    d = d[d["combined_nav"].notna() & d["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    g = d.dropna(subset=["ymd"]).groupby("ymd").last()
    nav = g["combined_nav"].astype(float)
    stk = (g["bal_stocks_ref"].fillna(0) + g["lag_stocks_ref"].fillna(0)).astype(float)
    etf = (g["bal_etf_ref"].fillna(0) + g["lag_etf_ref"].fillna(0)).astype(float)
    csh = (g["bal_cash_ref"].fillna(0) + g["lag_cash_ref"].fillna(0)).astype(float)
    eq, pk, ch = (stk + etf) / nav, etf / nav, csh / nav
    print(f"{lab:24s} {eq.mean()*100:>6.1f}% {np.percentile(eq,95)*100:>6.1f}% "
          f"{pk.mean()*100:>7.1f}% {ch.mean()*100:>7.1f}% "
          f"{eq[eq.index.year==2022].mean()*100:>8.1f}% {eq[eq.index.year==2021].mean()*100:>8.1f}%")
