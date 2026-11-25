# -*- coding: utf-8 -*-
"""[J3.1: chép từ ..._20261125d/calc, chỉ đổi đường dẫn out_CY; out_J3C = panel V3.2] g_cycle_update.py — PRELOCK_J3_CYCLE §4 (C'). In: ../out_J3C/vp2.parquet (V3.1 + lv_C1..C3 route PIT), ../out_CY/cyc_features.parquet.
Out: ../out_CYC_{ALL,CYC,REST}/vp2.parquet (+ lv_C4, lv_C5; CYC/REST = che in_universe theo nhóm) → d_metrics2.py V3.1."""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); DJ3 = os.path.join(HERE, "..", "..", "dcf_earnings_forecast_20261125d")   # J3.1: out_CY (đặc trưng chu kỳ, không phụ thuộc mc) lấy từ J3
R = 0.1225; GT = 0.055; H = 10
def rim_vb(roe_n, r, gT, ret, kappa):          # chép nguyên văn d_update.py
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)
vp = pd.read_parquet(os.path.join(D, "out_J3C", "vp2.parquet"))
cf = pd.read_parquet(os.path.join(DJ3, "out_CY", "cyc_features.parquet"))[["ticker", "quarter", "tc8", "rho", "phi", "grp"]].drop_duplicates(["ticker", "quarter"])
vp = vp.merge(cf, on=["ticker", "quarter"], how="left")
tc = vp.roe_tc5.clip(-0.1, 0.4).values; ret = (1 - vp.payout.fillna(0.3)).clip(0.1, 1.0).values
Ep = vp.E.where(vp.E > 0).values; lmc = np.log(vp.mc.values); iu = vp.in_universe.values
c4 = np.where(np.isfinite(vp.tc8.values), vp.tc8.values, tc)
c5 = np.where(np.isfinite(vp.rho.values), tc + vp.phi.fillna(0.65).values * (np.clip(vp.rho.values, -1, 1) - tc), tc)
LOG = {}
for nm, rn in (("C4", c4), ("C5", c5)):
    rn = np.clip(rn, -0.1, 0.5); vp["lv_" + nm] = np.log(rim_vb(rn, R, GT, ret, 0.4) * Ep) - lmc
    LOG[nm] = {"share_changed_vs_D0_in_univ": float((np.abs(vp["lv_" + nm] - vp.lv_D0) > 1e-9)[iu].mean()), "median_roe_n_minus_tc_in_univ": float(np.nanmedian((rn - tc)[iu])),
               "median_dlv_in_univ": float(np.nanmedian((vp["lv_" + nm] - vp.lv_D0)[iu]))}
d0 = np.log(rim_vb(tc, R, GT, ret, 0.4) * Ep) - lmc; LOG["D0_recompute_maxabs"] = float(np.nanmax(np.abs(d0 - vp.lv_D0.values)))
cyc = vp.grp.isin(["COMM", "CYC_HI"]).values
LOG["share_in_univ_rows_CYC"] = float(cyc[iu].mean()); LOG["grp_in_univ"] = vp.grp[iu].fillna("none").value_counts().to_dict()
for tag, mask in (("ALL", np.ones(len(vp), bool)), ("CYC", cyc), ("REST", ~cyc)):
    o = os.path.join(D, f"out_CYC_{tag}"); os.makedirs(o, exist_ok=True)
    v = vp.copy(); v["in_universe"] = iu & mask
    v.drop(columns=["tc8", "rho", "phi", "grp"]).to_parquet(os.path.join(o, "vp2.parquet"))
    LOG[f"n_univ_rows_{tag}"] = int((iu & mask).sum())
json.dump(LOG, open(os.path.join(D, "out_CYC_ALL", "C_build_cycle.json"), "w"), indent=1); print(json.dumps(LOG, indent=1))
