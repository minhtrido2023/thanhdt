# -*- coding: utf-8 -*-
"""Việc 4: CI bootstrap (khối theo NĂM gốc dự báo) cho chênh MAE K=5 (trung vị |log(Σ thực/Σ dự)| NP) s=0 vs s=0,5.
Dựng lại đúng growth.py (b): gT=5,5%, N=5 hiện tại vs s=0; panel fy>=2009 & fy+K<=2025."""
import os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "dcf_vn_calibration_20261101", "data")
pan = pd.read_parquet(os.path.join(OLD, "panel_monthly.parquet"))
ri = pd.read_parquet(os.path.join(OLD, "row_inputs.parquet"))
finflag = pan.groupby("ticker").is_fin.last()
fy = ri[ri.quarter.str.endswith("Q4")].copy()
fy["fy"] = fy.quarter.str[:4].astype(int)
fy = fy[~fy.ticker.map(finflag).fillna(True).astype(bool)]
fy = fy.sort_values(["ticker", "fy"]).drop_duplicates(["ticker", "fy"], keep="last")
fy = fy[fy.fy >= 2005]
gT = 0.055
F = fy[["ticker", "fy", "ttm_np", "g_raw"]].copy()
F["g_c"] = np.clip(np.where(F.g_raw.isna(), gT, F.g_raw), -0.02, 0.20)
res = {}
for K in (3, 5):
    real = np.column_stack([F.merge(fy[["ticker", "fy", "ttm_np"]].assign(fy=fy.fy - j), on=["ticker", "fy"], how="left",
                                    suffixes=("", "_r")).ttm_np_r.values for j in range(1, K + 1)])
    ok = (F.ttm_np > 0) & np.isfinite(real).all(1) & (F.fy >= 2009) & (F.fy + K <= 2025)
    rs = real.sum(1)
    mm = (ok & (rs > 0)).values
    errs = {}
    for name, s in (("s0", 0.0), ("s05", 0.5)):
        ge = gT + s * (F.g_c.values - gT)
        cum = np.cumprod(1 + np.repeat(ge[:, None], K, axis=1), axis=1)
        fc = (F.ttm_np.values[:, None] * cum).sum(1)
        errs[name] = np.abs(np.log(rs[mm] / fc[mm]))
    yrs = F.fy.values[mm]
    res[K] = (errs, yrs)
    print(f"K={K}: n={mm.sum()}  MAE s0={np.median(errs['s0']):.4f}  s0.5={np.median(errs['s05']):.4f}  Δ={np.median(errs['s0'])-np.median(errs['s05']):+.4f}")
rng = np.random.default_rng(20261102)
out = []
for K in (3, 5):
    errs, yrs = res[K]
    uy = np.unique(yrs)
    idx = {y: np.where(yrs == y)[0] for y in uy}
    d = []
    for _ in range(5000):
        pick = rng.choice(uy, len(uy), replace=True)
        ii = np.concatenate([idx[y] for y in pick])
        d.append(np.median(errs["s0"][ii]) - np.median(errs["s05"][ii]))
    d = np.array(d)
    # Δ theo từng năm (mặt phẳng đồng thuận): s0 thắng bao nhiêu năm
    per_year = [np.median(errs["s0"][idx[y]]) - np.median(errs["s05"][idx[y]]) for y in uy]
    # cặp theo dòng: Δ|e| trung bình (nhạy hơn trung vị)
    dr = errs["s0"] - errs["s05"]
    bm = np.array([dr[np.concatenate([idx[y] for y in rng.choice(uy, len(uy), replace=True)])].mean() for _ in range(5000)])
    r = {"K": K, "n": len(yrs), "n_years": len(uy), "MAE_s0": np.median(errs["s0"]), "MAE_s05": np.median(errs["s05"]),
         "delta_median": np.median(errs["s0"]) - np.median(errs["s05"]), "ci_lo": np.percentile(d, 2.5), "ci_hi": np.percentile(d, 97.5),
         "years_s0_better": int(sum(x < 0 for x in per_year)), "paired_mean_d": dr.mean(),
         "paired_ci_lo": np.percentile(bm, 2.5), "paired_ci_hi": np.percentile(bm, 97.5)}
    out.append(r)
    print(r)
pd.DataFrame(out).to_csv(os.path.join(HERE, "out", "boot_mae_k.csv"), index=False)
