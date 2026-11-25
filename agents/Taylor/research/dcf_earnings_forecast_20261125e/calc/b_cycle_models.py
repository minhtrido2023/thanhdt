# -*- coding: utf-8 -*-
"""b_cycle_models.py — PRELOCK_J4 §2–§3. Chỉ báo pha ngành LOO (S1..S4, ICB4, ≥5 peer, PIT) + fit P1/M1..M5 trên IS → lv_P1, lv_M1..lv_M5.
In: ../out_panel/vp2.parquet (V3.2), ../in/icb_pit_20251231.csv, ../../dcf_earnings_forecast_20261125d/out_CY/cyc_features.parquet (grp, chỉ để tách CYC/REST báo cáo).
Out: ../out_{ALL,CYC,REST}/vp2.parquet, ../out_ALL/fit.json, ../out_ALL/sig_rows.parquet"""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..")
R = 0.1225; GT = 0.055; H = 10; MINPEER = 5
def rim_vb(roe_n, r, gT, ret, kappa):          # chép nguyên văn ../../dcf_earnings_forecast_20261125d/calc/g_cycle_update.py
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)
vp = pd.read_parquet(os.path.join(D, "out_panel", "vp2.parquet"))
assert (vp.known <= vp.time).all(), "PIT violation"
icb = pd.read_csv(os.path.join(D, "in", "icb_pit_20251231.csv")).dropna(); icb["icb"] = icb.icb.astype(int)
vp = vp.merge(icb, on="ticker", how="left")
LOG = {"icb_cover_rows": float(vp.icb.notna().mean())}
# ---- 1. chỉ báo riêng từng mã theo quý (lịch sử chỉ gồm quý known trước) ----
vp["capr"] = vp.capex_ttm.abs() / vp.rev_ttm.where(vp.rev_ttm > 0)
Q = vp.sort_values(["ticker", "known", "time"]).drop_duplicates(["ticker", "quarter"])[["ticker", "quarter", "known", "roe", "roe_tc5", "gpm", "cashcycle", "capr"]].copy()
Q = Q.sort_values(["ticker", "known"]).reset_index(drop=True)
for c, k in (("gpm", "x2"), ("cashcycle", "x3"), ("capr", "x4")):
    med = Q.groupby("ticker")[c].transform(lambda s: s.shift(1).rolling(20, min_periods=8).median())
    Q[k] = Q[c] - med
Q["x3"] = -Q.x3
Q["x1"] = Q.roe - Q.roe_tc5
vp = vp.merge(Q[["ticker", "quarter", "x1", "x2", "x3", "x4"]], on=["ticker", "quarter"], how="left")
# ---- 2. trung vị LOO theo (ym, icb) ----
def loo_median(v):
    n = len(v); out = np.full(n, np.nan); ok = np.isfinite(v)
    if ok.sum() - 1 < MINPEER:
        # mã không có giá trị vẫn có thể có ≥5 peer
        if ok.sum() >= MINPEER:
            out[~ok] = np.median(v[ok])
        return out
    vv = v[ok]; m = len(vv); M = np.tile(vv, (m, 1)); np.fill_diagonal(M, np.nan)
    out[ok] = np.nanmedian(M, axis=1); out[~ok] = np.median(vv)
    return out
vp = vp.sort_values(["ym", "icb", "ticker"]).reset_index(drop=True)
for k in ("x1", "x2", "x3", "x4"):
    s = np.full(len(vp), np.nan)
    for _, idx in vp[vp.icb.notna()].groupby(["ym", "icb"]).indices.items():
        s[idx] = loo_median(vp[k].values[idx])
    vp["S" + k[1]] = s
    vp["R" + k[1]] = vp.groupby("ym")["S" + k[1]].rank(pct=True) - 0.5          # hạng phần trăm cross-section tháng
    LOG[f"S{k[1]}_cover_in_univ_2014p"] = float(vp["S" + k[1]].notna()[vp.in_universe & (vp.ym.astype(str) >= "2014-01")].mean())
# ---- 3. fit IS ----
tc_all = vp.roe_tc5.clip(-0.1, 0.4)
vp["g"] = (vp.roe - tc_all).clip(-0.3, 0.3)
qi = pd.PeriodIndex(vp.quarter, freq="Q"); vp["qn"] = qi.year * 4 + qi.quarter
Qr = vp.drop_duplicates(["ticker", "quarter"])[["ticker", "qn", "roe", "known"]]
fut = {}
for h in (4, 8):
    f = Qr.assign(qn=Qr.qn - h).rename(columns={"roe": f"roe_f{h}", "known": f"known_f{h}"})
    fut[h] = f[["ticker", "qn", f"roe_f{h}", f"known_f{h}"]]
first = vp.sort_values("time").drop_duplicates(["ticker", "quarter"]).copy()
for h in (4, 8):
    first = first.merge(fut[h], on=["ticker", "qn"], how="left")
first["y"] = ((first.roe_f4 + first.roe_f8) / 2 - first.roe_tc5.clip(-0.1, 0.4)).clip(-0.3, 0.3)
kn = first.known.dt.year
fit = first[first.in_universe & kn.between(2014, 2019) & (first.known_f4 < "2020-01-01") & (first.known_f8 < "2020-01-01") & first.y.notna() & first.g.notna()].copy()
LOG["n_fit_rows"] = int(len(fit)); LOG["n_fit_tickers"] = int(fit.ticker.nunique())
def ols(X, y):
    b = np.linalg.solve(X.T @ X, X.T @ y); return b
Fp = {}
Fp["P1"] = ols(fit[["g"]].values, fit.y.values)
f1 = fit[fit.S1.notna()]; Fp["M1"] = ols(np.c_[f1.S1.clip(-0.3, 0.3), f1.g - f1.S1.clip(-0.3, 0.3)], f1.y.values)
for nm, rk in (("M2", "R2"), ("M3", "R3"), ("M4", "R4"), ("M5", "R1")):
    fk = fit[fit[rk].notna()]; Fp[nm] = ols(np.c_[fk.g, fk[rk] * fk.g], fk.y.values); LOG[f"n_fit_{nm}"] = int(len(fk))
LOG["n_fit_M1"] = int(len(f1)); LOG["coef"] = {k: [round(float(x), 4) for x in v] for k, v in Fp.items()}
# ---- 4. roe_n + lv ----
tc = tc_all.values; g = vp.g.values; ret = (1 - vp.payout.fillna(0.3)).clip(0.1, 1.0).values
Ep = vp.E.where(vp.E > 0).values; lmc = np.log(vp.mc.values)
g0 = np.nan_to_num(g)
phi1 = np.clip(Fp["P1"][0], 0, 1); RN = {"P1": tc + phi1 * g0}
S1c = vp.S1.clip(-0.3, 0.3).values
RN["M1"] = np.where(np.isfinite(S1c), tc + np.clip(Fp["M1"][0], 0, 1) * np.nan_to_num(S1c) + np.clip(Fp["M1"][1], 0, 1) * (g0 - np.nan_to_num(S1c)), RN["P1"])
for nm, rk in (("M2", "R2"), ("M3", "R3"), ("M4", "R4"), ("M5", "R1")):
    r_ = vp[rk].values; ph = np.clip(Fp[nm][0] + Fp[nm][1] * np.nan_to_num(r_), 0, 1)
    RN[nm] = np.where(np.isfinite(r_), tc + ph * g0, RN["P1"])
vp["lv_D0_chk"] = np.log(rim_vb(tc, R, GT, ret, 0.4) * Ep) - lmc
LOG["D0_recompute_maxabs"] = float(np.nanmax(np.abs(vp.lv_D0_chk - vp.lv_D0)))
iu = vp.in_universe.values & (vp.ym.astype(str) >= "2014-01").values
for nm, rn in RN.items():
    rn = np.clip(rn, -0.1, 0.5); vp["lv_" + nm] = np.log(rim_vb(rn, R, GT, ret, 0.4) * Ep) - lmc
    vp["roen_" + nm] = rn
    LOG[f"{nm}_median_dlv_vs_D0_in_univ"] = float(np.nanmedian((vp["lv_" + nm] - vp.lv_D0)[iu]))
# ---- 5. phụ: R² OOS dự báo y (quý known 2020+) ----
fo = first.merge(vp[["ticker", "quarter", "time"] + [f"roen_{k}" for k in RN]], on=["ticker", "quarter", "time"], how="left")
oo = fo[fo.in_universe & (fo.known.dt.year >= 2020) & fo.y.notna()]
ytrue = oo.y.values + oo.roe_tc5.clip(-0.1, 0.4).values
LOG["R2_oos_future_roe"] = {"n": int(len(oo)), "D0": float(1 - np.mean((ytrue - oo.roe_tc5.clip(-0.1, 0.4)) ** 2) / np.var(ytrue))}
for k in RN:
    LOG["R2_oos_future_roe"][k] = float(1 - np.mean((ytrue - oo[f"roen_{k}"]) ** 2) / np.var(ytrue))
# ---- 6. xuất ----
cf = pd.read_parquet(os.path.join(D, "..", "dcf_earnings_forecast_20261125d", "out_CY", "cyc_features.parquet"))[["ticker", "quarter", "grp"]].drop_duplicates(["ticker", "quarter"])
vp = vp.merge(cf, on=["ticker", "quarter"], how="left"); cyc = vp.grp.isin(["COMM", "CYC_HI"]).values; iu_all = vp.in_universe.values
vp[["ticker", "ym", "time", "quarter", "known", "icb", "in_universe", "x1", "x2", "x3", "x4", "S1", "S2", "S3", "S4", "g"]].to_parquet(os.path.join(D, "out_panel", "sig_rows.parquet"))
drop = ["icb", "capr", "x1", "x2", "x3", "x4", "S1", "S2", "S3", "S4", "R1", "R2", "R3", "R4", "g", "qn", "lv_D0_chk", "grp"] + [f"roen_{k}" for k in RN]
for tag, mask in (("ALL", np.ones(len(vp), bool)), ("CYC", cyc), ("REST", ~cyc)):
    o = os.path.join(D, f"out_{tag}"); os.makedirs(o, exist_ok=True)
    v = vp.drop(columns=drop).copy(); v["in_universe"] = iu_all & mask; v.to_parquet(os.path.join(o, "vp2.parquet"))
    LOG[f"n_univ_rows_{tag}"] = int((iu_all & mask).sum())
json.dump(LOG, open(os.path.join(D, "out_ALL", "fit.json"), "w"), indent=1); print(json.dumps(LOG, indent=1))
