# -*- coding: utf-8 -*-
"""[J3.1: chép nguyên văn từ ..._20261125d/calc; chạy với SNAP_DIR=in (panel V3.2)] h_dsr.py — PRELOCK_J3_CYCLE §4: DSR (Bailey–López de Prado) trên chuỗi ΔIC36 theo năm 2014–2023 (biến thể − D0), N thử = 7; + D0 − EP theo năm.
In: ../out_CYC_{ALL,CYC,REST}/ic_year2_C.csv. Out: ../out_CYC_ALL/dsr_cycle.json"""
import os, json
import numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); NTRIAL = 7; EG = 0.5772156649
res = {}
for t in ("ALL", "CYC", "REST"):
    icy = pd.read_csv(os.path.join(D, f"out_CYC_{t}", "ic_year2_C.csv")); icy = icy[icy.scope == "ALL"]
    Y = icy.pivot_table(index=["t", "year"], columns="model", values="ic36").reset_index().groupby("year")[["D0", "C2", "C4", "C5", "EP"]].mean()
    Y = Y.loc[2014:2023]; out = {}
    for v, ref in (("C2", "D0"), ("C4", "D0"), ("C5", "D0"), ("D0", "EP"), ("C4", "EP")):
        x = (Y[v] - Y[ref]).dropna().values; T = len(x); sr = x.mean() / x.std(ddof=1)
        # SR kỳ vọng tối đa của N thử dưới H0 (phương sai SR ≈ 1/T)
        sr0 = np.sqrt(1.0 / T) * ((1 - EG) * norm.ppf(1 - 1.0 / NTRIAL) + EG * norm.ppf(1 - 1.0 / (NTRIAL * np.e)))
        g3, g4 = skew(x), kurtosis(x, fisher=False)
        dsr = norm.cdf((sr - sr0) * np.sqrt(T - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
        out[f"{v}-{ref}"] = {"T_years": T, "mean": round(float(x.mean()), 4), "SR_year": round(float(sr), 3), "SR0": round(float(sr0), 3), "DSR": round(float(dsr), 3),
                             "years_pos": int((x > 0).sum()), "by_year": {int(k): round(float(val), 4) for k, val in (Y[v] - Y[ref]).items()}}
    res[t] = out
json.dump(res, open(os.path.join(D, "out_CYC_ALL", "dsr_cycle.json"), "w"), indent=1); print(json.dumps(res, indent=1))
