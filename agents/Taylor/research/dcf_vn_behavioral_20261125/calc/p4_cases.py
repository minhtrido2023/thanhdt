# -*- coding: utf-8 -*-
"""p4_cases.py — ca kiểm khoá trước (VNM 2015, VCS 2015, DGC 2016, HPG 2019) + 12 dòng ngẫu nhiên (seed 20261125) + tương quan đặc trưng.
Out: ../out/cases.csv, ../out/feat_corr.csv, ../out/inventory_cover.csv"""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
WC = "/home/trido/thanhdt/WorkingClaude"; V3 = f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c"
P12 = pd.read_parquet(f"{OUT}/pilot_pred_h12.parquet"); P24 = pd.read_parquet(f"{OUT}/pilot_pred_h24.parquet")
ft = pd.read_parquet(f"{OUT}/feat.parquet")
pan = pd.read_parquet(f"{V3}/out_F/vp2.parquet", columns=["ticker", "ym", "in_universe", "Close", "lv_ENS2", "lv_L2_ENS2", "ep", "fwd12_h50", "fwd24_h50"])
M = P12[["ticker", "ym", "era", "mu", "p_F", "p_F0", "beh", "ydm"]].rename(columns={"p_F": "pF12", "p_F0": "pF0_12", "ydm": "ydm12", "mu": "mu12", "beh": "beh12"})
M = M.merge(P24[["ticker", "ym", "p_F", "ydm"]].rename(columns={"p_F": "pF24", "ydm": "ydm24"}), on=["ticker", "ym"], how="left")
M = M.merge(pan, on=["ticker", "ym"]).merge(ft[["ticker", "ym", "hi52", "cgo", "mom", "rev1"]], on=["ticker", "ym"])
M["tam_noi_tai"] = M.Close * np.exp(M.lv_ENS2); M["tam_tc_12"] = M.Close * np.exp(M.mu12 + M.pF12); M["gia_12_thuc"] = M.Close * np.exp(M.fwd12_h50)
M["luc_keo"] = M.lv_ENS2 - (M.mu12 + M.pF12)
keep = ["ticker", "ym", "era", "Close", "tam_noi_tai", "tam_tc_12", "gia_12_thuc", "lv_ENS2", "luc_keo", "hi52", "cgo", "mom", "pF12", "pF0_12", "ydm12", "pF24", "ydm24", "fwd12_h50", "fwd24_h50"]
case = [("VNM", "2015-06"), ("VNM", "2015-12"), ("VNM", "2017-12"), ("VCS", "2015-06"), ("VCS", "2015-12"), ("DGC", "2016-06"), ("DGC", "2016-12"), ("HPG", "2019-06"), ("HPG", "2019-12")]
C = pd.concat([M[(M.ticker == t) & (M.ym == y)] for t, y in case]); C["loai"] = "khoa_truoc"
R = M.sample(12, random_state=20261125); R["loai"] = "ngau_nhien"
pd.concat([C, R])[["loai"] + keep].round(4).to_csv(f"{OUT}/cases.csv", index=False)
print(pd.concat([C, R])[["loai"] + keep].round(3).to_string())
d = pan[pan.in_universe].merge(ft, on=["ticker", "ym"]); cols = ["hi52", "cgo", "mom", "rev1", "ep", "lv_ENS2", "lv_L2_ENS2", "max21", "n_up60", "n_dn60", "to60"]
r = d[cols + ["ym"]].copy()
for c_ in cols: r[c_] = r.groupby("ym")[c_].rank(pct=True)
cm = r[r.ym >= "2014-01"][cols].corr(); cm.round(3).to_csv(f"{OUT}/feat_corr.csv"); print(cm.round(2).to_string())
d["y"] = d.ym.str[:4]; cov = d.groupby("y")[cols].agg(lambda s: s.notna().mean()).round(3); cov["n"] = d.groupby("y").size(); cov.to_csv(f"{OUT}/inventory_cover.csv"); print(cov.to_string())
# sai số mức giá: |log(giá thực 12T / tâm)| trung vị theo era
for era in ("IS", "OOS"):
    e = M[M.era == era]; print(era, "median|log err| RW", round(np.abs(e.fwd12_h50).median(), 4), "tam_tc", round(np.abs(e.fwd12_h50 - e.mu12 - e.pF12).median(), 4), "tam_noi_tai", round(np.abs(e.fwd12_h50 - e.lv_ENS2).median(), 4), "n", len(e))
