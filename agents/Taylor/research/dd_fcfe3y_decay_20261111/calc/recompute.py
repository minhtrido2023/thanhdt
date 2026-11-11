# -*- coding: utf-8 -*-
"""recompute.py — tính lại ĐỘC LẬP (scipy spearmanr + lstsq trên hạng, không dùng lib.py) vài ô của summary.json:
PIC V_dài (baseline), PIC CFO yield, PIC FCFE yield, PIC biến thể C4 — N24/N36, IS/OOS."""
import os, sys, json
import numpy as np, pandas as pd
from scipy.stats import rankdata
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, os.path.join(HERE, "..", "..", "dd_blend_20261111", "calc"))
import common as C
p = C.load(); E = pd.read_parquet(os.path.join(OUT, "ext.parquet")).reindex(range(len(p)))
S = json.load(open(os.path.join(OUT, "summary.json")))
MC0 = p.MC0.values; VL = p.V_l3.values; VS = p.V_s.values
M0 = (p.rating <= 3).values & np.isfinite(MC0) & (VL > 0) & (VS > 0)
rev = E[["Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3"]].sum(axis=1, min_count=4).values
DA = E.EBITDA_P0.values - E.EBITM_P0.values * rev; DA = np.where(DA > 0, DA, np.nan)
CFO3 = p.cfoa3.values / 3; CPX3 = -p.cfinv3.values / 3
V4 = np.where((p.cfoa3.values > 0) & (CFO3 - np.minimum(CPX3, DA) > 0),
              C.dcf(CFO3 - np.minimum(CPX3, DA), p.g_exp.values, p.g_T.values, p.r.values), np.nan)


def pic(x, ctrl, y, q, mask):
    out = {}
    for qq in np.unique(q[mask]):
        k = mask & (q == qq) & np.isfinite(x) & np.isfinite(ctrl) & np.isfinite(y)
        if k.sum() < 20:
            continue
        Z = np.c_[rankdata(x[k]), rankdata(ctrl[k])]; Z = (Z - Z.mean(0)) / Z.std(0)
        yz = rankdata(y[k]); yz = (yz - yz.mean()) / yz.std()
        out[qq] = np.linalg.lstsq(np.c_[np.ones(k.sum()), Z], yz, rcond=None)[0][1]
    return out


chk = []
for N in (24, 36):
    y = np.log(p[f"TR{N}"].values); y[~p[f"full{N}"].values] = np.nan
    xs = np.log(VS / MC0)
    for sp, ym in (("IS", p.yr.values <= 2019), ("OOS", p.yr.values >= 2020)):
        for nm, x, mk, key in (("PIC:xl", np.log(VL / MC0), M0, ("Q2", "M0", "PIC:xl")),
                               ("PIC:cfoy", np.log(CFO3 / MC0), M0, ("Q2", "M0", "PIC:cfoy")),
                               ("PIC:fy", np.log((CFO3 - CPX3) / MC0), M0, ("Q2", "M0", "PIC:fy")),
                               ("PIC:C4", np.log(V4 / MC0), M0 & np.isfinite(V4), None)):
            v = pic(x, xs, y, p.q.values, mk & ym)
            mine = float(np.mean(list(v.values())))
            if key:
                ref = S["Q2"][str(N)][key[1]][sp][key[2]]["pt"]
            else:
                ref = S["Q3"]["C4_cfo3_minus_min_capex_DA"][str(N)][sp]["PIC_c"]["pt"]
            chk.append({"N": N, "split": sp, "stat": nm, "indep": round(mine, 4), "summary": round(ref, 4),
                        "abs_dev": abs(mine - ref)})
df = pd.DataFrame(chk); print(df.to_string())
assert df.abs_dev.max() < 2e-3, "recompute lệch"
df.to_csv(os.path.join(OUT, "recompute.csv"), index=False); print("RECOMPUTE PASS max dev", df.abs_dev.max())
