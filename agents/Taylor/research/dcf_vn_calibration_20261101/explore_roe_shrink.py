# -*- coding: utf-8 -*-
"""HẬU NGHIỆM (không có trong PREREG, đếm thêm 2 trial): shrink theo chất lượng ROE5Y.
(1) độ chính xác Σ NP 5 năm theo tam phân ROE với s∈{0,.5,1}; (2) IC của s = 0,5 nếu ROE5Y≥20% (top) else 0."""
import os
import numpy as np
import pandas as pd
from common import DATA, OUT, month_close, add_fwd, ic_by_date, ic_summary
import engine as E
P = print
ri = pd.read_parquet(os.path.join(DATA, "row_inputs.parquet"))
pan = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
finflag = pan.groupby("ticker").is_fin.last()
fy = ri[ri.quarter.str.endswith("Q4")].copy()
fy["fy"] = fy.quarter.str[:4].astype(int)
fy = fy[~fy.ticker.map(finflag).fillna(True).astype(bool)].drop_duplicates(["ticker", "fy"], keep="last")
gT = 0.055
fy["gc"] = np.clip(np.where(fy.g_raw.isna(), gT, fy.g_raw), -0.02, 0.2)
K = 5
real = np.column_stack([fy.merge(fy[["ticker", "fy", "ttm_np"]].assign(fy=fy.fy - j), on=["ticker", "fy"], how="left",
                                 suffixes=("", "_r")).ttm_np_r.values for j in range(1, K + 1)])
ok = (fy.ttm_np > 0).values & np.isfinite(real).all(1) & (fy.fy >= 2009).values & (fy.fy + K <= 2025).values & (real.sum(1) > 0)
roe = fy.ROE5Y.values
roe = roe / 100 if np.nanmedian(np.abs(roe)) > 1 else roe
grp = np.where(roe >= 0.20, "ROE≥20%", np.where(roe >= 0.10, "ROE 10-20%", "ROE<10%"))
for s in (0, 0.5, 1):
    ge = gT + s * (fy.gc.values - gT)
    fc = (fy.ttm_np.values[:, None] * np.cumprod(np.full((len(fy), K), 1) + ge[:, None], axis=1)).sum(1)
    e = np.log(real.sum(1) / fc)
    out = {g: (round(float(np.median(np.abs(e[ok & (grp == g)]))), 3), round(float(np.median(e[ok & (grp == g)])), 3), int((ok & (grp == g)).sum())) for g in ("ROE<10%", "ROE 10-20%", "ROE≥20%")}
    P(f"s={s}: (MAE, bias, n) K=5 theo ROE5Y:", out)
p = pan.copy()
mc, me = month_close()
p = add_fwd(p, mc, me)
roe_p = p.ROE5Y / 100 if p.ROE5Y.abs().median() > 1 else p.ROE5Y
for name, shr in (("s cond ROE≥20%→0.5 else 0", np.where(roe_p >= 0.20, 0.5, 0.0)), ("s cond ROE≥20%→1 else 0", np.where(roe_p >= 0.20, 1.0, 0.0)),
                  ("V0", 0.5), ("s=0", 0.0)):
    fv, _ = E.current_fv(p, shrink=shr)
    q = p.assign(fv=fv)
    q = q[np.isfinite(q.fv) & (q.Price > 0)]
    q["mos"] = (q.fv - q.Price) / q.fv
    s12 = ic_summary(ic_by_date(q, "mos", "fwd12"), 12)
    P(f"{name}: IC12 {s12['ic']:.4f} IS {s12['ic_is']:.4f} OOS {s12['ic_oos']:.4f} t {s12['t_nw']:.2f}  medPFV {np.exp(q.assign(l=np.log(q.Price/q.fv)).groupby('t').l.median().mean()):.3f}")
