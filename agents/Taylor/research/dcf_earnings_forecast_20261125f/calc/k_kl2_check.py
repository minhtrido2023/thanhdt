# -*- coding: utf-8 -*-
"""k_kl2_check.py — J3.1 (sửa chữ KL2): đo lại độ lớn "gap báo trước u4" sau kiểm soát ĐỦ (4 kiểm soát + nlv; + cả nroe) — test skeptic J3 đã chạy, J3 chưa báo.
Hàm ic_series/resid/boot chép NGUYÊN VĂN c_gap.py (J3). In: ../../dcf_earnings_forecast_20261125d/out_J3/gapev.parquet (không phụ thuộc mc panel). Out: ../out_delta/kl2_u4_ctrl.csv"""
import os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); J3 = os.path.join(HERE, "..", "..", "dcf_earnings_forecast_20261125d"); O = os.path.join(HERE, "..", "out_delta"); os.makedirs(O, exist_ok=True)
SEED = 20261125; B = 2000
def sp(a, b):
    return np.corrcoef(pd.Series(a).rank().values, pd.Series(b).rank().values)[0, 1]
def resid(df, x, ctrls):
    X = np.column_stack([np.ones(len(df))] + [df[cc].rank().values for cc in ctrls]); y = df[x].rank().values
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
def ic_series(d, x, y, ctrls=None):
    out = []
    for q, s in d.groupby("qps"):
        cols = [x, y] + (ctrls or []); s = s[np.isfinite(s[cols]).all(axis=1)]
        if len(s) < 30:
            continue
        xv = s[x]
        if ctrls:
            xv = resid(s.assign(_x=xv), "_x", ctrls)
        out.append((q, int(s.yr.iloc[0]), sp(xv, s[y]), len(s)))
    return pd.DataFrame(out, columns=["q", "yr", "ic", "n"])
def boot(icd, seed=SEED):
    ys = icd.yr.unique(); rng = np.random.RandomState(seed); by = {y: icd.ic[icd.yr == y].values for y in ys}
    res = np.array([np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)])
    return float(icd.ic.mean()), float(np.percentile(res, 2.5)), float(np.percentile(res, 97.5))
ev = pd.read_parquet(os.path.join(J3, "out_J3", "gapev.parquet"))
CT = ["ep", "lsize", "roe_tc5", "mom"]; rows = []
for era in ("IS", "OOS"):
    d = ev[ev.era == era]
    for nm, ct in (("ctrl4+nroe (J3 KL2)", CT + ["nroe"]), ("nlv", ["nlv"]), ("ctrl4+nlv", CT + ["nlv"]), ("ctrl4+nroe+nlv", CT + ["nroe", "nlv"])):
        s = ic_series(d, "gap", "u4", ct); m, lo, hi = boot(s)
        rows.append({"era": era, "ctrl": nm, "IC": round(m, 4), "ci95_lo": round(lo, 4), "ci95_hi": round(hi, 4), "n_q": len(s), "n_pos_yr": int((s.groupby("yr").ic.mean() > 0).sum()), "n_yr": int(s.yr.nunique())})
r = pd.DataFrame(rows); r.to_csv(os.path.join(O, "kl2_u4_ctrl.csv"), index=False); print(r.to_string(index=False))
