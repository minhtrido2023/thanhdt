# -*- coding: utf-8 -*-
"""e_cdiff.py — PRELOCK §4: ΔIC36 cặp (biến thể − D0, và − EP) theo ngày as-of, CI khối năm (95% và 99,17% Bonferroni 3); PBO CSCV trên IC36 năm 2014–2023.
In: ../out_C/ic_year2_C.csv, ../out_C/metrics2_C.csv. Out: ../out_C/C_diff.csv, ../out_C/C_pbo.json"""
import os, json, itertools
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OC = os.environ.get("OC_DIR") or os.path.join(HERE, "..", "out_C"); SEED = 20261125; B = 2000
icy = pd.read_csv(os.path.join(OC, "ic_year2_C.csv")); icy = icy[icy.scope == "ALL"]
T_IS1 = None
met = pd.read_csv(os.path.join(OC, "metrics2_C.csv"))
piv = icy.pivot_table(index=["t", "year"], columns="model", values="ic36").reset_index()
# era theo t: dùng năm (IS 2014–2019, OOS 2020–2023)
piv["era"] = np.where(piv.year <= 2019, "IS", "OOS")
rows = []
for era in ("IS", "OOS"):
    d = piv[piv.era == era]
    for v in [m for m in os.environ.get("VARIANTS", "C1,C2,C3").split(",")]:
        for ref in ("D0", "EP"):
            x = d[["year", v, ref]].dropna(); x["df"] = x[v] - x[ref]; ys = x.year.unique(); rng = np.random.RandomState(SEED)
            by = {y: x.df[x.year == y].values for y in ys}
            res = np.array([np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)])
            rows.append({"era": era, "variant": v, "ref": ref, "dIC36": float(x.df.mean()), "ci95": [float(np.percentile(res, 2.5)), float(np.percentile(res, 97.5))],
                         "ci9917": [float(np.percentile(res, 0.415)), float(np.percentile(res, 99.585))], "n_dates": int(len(x)), "n_years": int(len(ys)),
                         # [J3 vá skeptic (3)] sign-count theo năm thay CI khối-năm suy biến (4 khối OOS)
                         "n_years_pos": int((x.groupby("year").df.mean() > 0).sum()), "by_year": {int(k): round(float(v), 4) for k, v in x.groupby("year").df.mean().items()}})
D = pd.DataFrame(rows); D.to_csv(os.path.join(OC, "C_diff.csv"), index=False)
# PBO (CSCV) trên ma trận IC36 theo năm × cấu hình {D0,C1,C2,C3}
Y = piv.groupby("year")[["D0"] + os.environ.get("VARIANTS", "C1,C2,C3").split(",")].mean().dropna(); yrs = list(Y.index); S = len(yrs); half = S // 2; lam = []
for comb in itertools.combinations(range(S), half):
    tr = list(comb); te = [i for i in range(S) if i not in comb]
    best = Y.iloc[tr].mean().idxmax(); rk = Y.iloc[te].mean().rank()[best] / (Y.shape[1] + 1)
    lam.append(np.log(rk / (1 - rk)))
pbo = float(np.mean(np.array(lam) <= 0))
json.dump({"years": [int(y) for y in yrs], "n_splits": len(lam), "PBO": pbo, "IC36_by_year": Y.round(4).to_dict()}, open(os.path.join(OC, "C_pbo.json"), "w"), indent=1)
pd.set_option("display.width", 200); print(D.to_string(index=False)); print("PBO", pbo, "years", yrs); print(Y.round(3))
