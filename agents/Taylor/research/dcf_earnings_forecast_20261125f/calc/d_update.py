# -*- coding: utf-8 -*-
"""[J3.1: chép nguyên văn từ ..._20261125d/calc; chạy với SNAP_DIR=in (panel V3.2)] d_update.py — PRELOCK §4 (C). Biến thể C1/C2/C3 chỉ đổi roe_n của rim_vb (D0). PIT: roe_n tại quý q chỉ dùng u đã lộ tại ≤ K_q.
In: ../out/events.parquet, ../in_snapshot/vp2.parquet. Out: ../out_C/vp2.parquet (snapshot + lv_C1..C3) → chạy d_metrics2.py (code V3, không sửa) với OUT_DIR=../out_C."""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out"); OC = os.environ.get("OC_DIR") or os.path.join(HERE, "..", "out_C"); SNAP = os.environ.get("SNAP_DIR") or os.path.join(HERE, "..", "in_snapshot")
os.makedirs(OC, exist_ok=True)
R = 0.1225; GT = 0.055; H = 10
def rim_vb(roe_n, r, gT, ret, kappa):          # chép nguyên văn từ dcf_vn_redesign_20261125c/calc/c_models2.py
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)

ev = pd.read_parquet(os.path.join(OUT, "events.parquet")).sort_values(["ticker", "qi"]).reset_index(drop=True)
ev = ev[ev.E.notna()].copy()                    # mọi quý có định giá (không chỉ mẫu iuK) để phủ panel tháng
g = ev.groupby("ticker")
# u_q = 4·A_q/E_{q−1} − tc_{q−1}; cần quý liền trước đúng (qi−1)
prv = ev[["ticker", "qi", "E", "roe_tc5"]].copy(); prv["qi"] += 1; prv.columns = ["ticker", "qi", "E_prev", "tc_prev"]
ev = ev.merge(prv, on=["ticker", "qi"], how="left")
ev["u"] = np.where(ev.E_prev > 0, 4 * ev.NP_P0 / ev.E_prev - ev.tc_prev, np.nan)
ev["u"] = ev.u.clip(-0.5, 0.5)                  # chặn ca E_prev rất nhỏ
def rmean(s, w, minp):
    return s.rolling(w, min_periods=minp).mean()
ev = ev.sort_values(["ticker", "qi"]).reset_index(drop=True)
ev["u4"] = ev.groupby("ticker").u.transform(lambda s: rmean(s, 4, 2))
ev["u8"] = ev.groupby("ticker").u.transform(lambda s: rmean(s, 8, 1)); ev["n8"] = ev.groupby("ticker").u.transform(lambda s: s.notna().astype(float).rolling(8, min_periods=1).sum())
# C3: ENS 4 quý tới từ dòng q (công thức b_forecast.py)
NP = ev[[f"NP_P{k}" for k in range(8)]].values; RV = ev[[f"Revenue_P{k}" for k in range(8)]].values; E = ev.E.values
ttm = NP[:, :4].sum(1); drift = (NP[:, :4] - NP[:, 4:]).mean(1)
with np.errstate(all="ignore"):
    gg = np.clip(RV[:, :4].sum(1) / RV[:, 4:].sum(1) - 1, -0.5, 0.5); mm = np.clip(ttm / RV[:, :4].sum(1), -0.5, 0.5)
rho = ttm / E; rbar = ev.roe_tc5.values; S4 = np.zeros(len(ev))
for h in (1, 2, 3, 4):
    f = np.nanmedian(np.vstack([NP[:, 4 - h] + drift, RV[:, 4 - h] * (1 + gg) * mm, E * (rbar + 0.65 ** (h / 4) * (rho - rbar)) / 4]), axis=0)
    S4 = S4 + f
ev["roe_c3"] = np.clip(S4 / E, -0.1, 0.5)
ev.loc[~(ev.hist8 & (E > 0)), "roe_c3"] = np.nan
q = ev[["ticker", "quarter", "u4", "u8", "n8", "roe_c3"]]
vp = pd.read_parquet(os.path.join(SNAP, "vp2.parquet"))
vp = vp.merge(q, on=["ticker", "quarter"], how="left")
# [J3 vá skeptic (4)] route PIT: nhãn route của bản rating 8L gần nhất ≤ time (merge_asof); trước bản đầu (2014-06) ⇒ không có route ⇒ co về trung vị TOÀN universe tại ym
import duckdb
rat = duckdb.connect().execute("SELECT ticker, CAST(time AS DATE) AS rt, route AS route_pit FROM read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["rt"] = pd.to_datetime(rat.rt).astype(vp.time.dtype)
vp = pd.merge_asof(vp.sort_values("time"), rat.sort_values("rt"), left_on="time", right_on="rt", by="ticker", direction="backward")
if os.environ.get("ROUTE_STATIC") == "1":
    vp["route_pit"] = vp.route                  # tái lập J2
iu = vp.in_universe.values
ur = vp[iu].groupby(["ym", "route_pit"]).u8.median().rename("u_route").reset_index()
up = vp[iu].groupby("ym").u8.median().rename("u_pool").reset_index()
vp = vp.merge(ur, on=["ym", "route_pit"], how="left").merge(up, on="ym", how="left")
vp["u_route"] = vp.u_route.where(vp.route_pit.notna(), vp.u_pool)
LOG = {"route_pit_share_na_in_univ": float(vp.route_pit[vp.in_universe].isna().mean()), "route_pit_ne_static_in_univ": float((vp.route_pit != vp.route)[vp.in_universe & vp.route_pit.notna()].mean())}
vp = vp.sort_values(["ticker", "time"]).reset_index(drop=True)
tc = vp.roe_tc5.clip(-0.1, 0.4).values; ret = (1 - vp.payout.fillna(0.3)).clip(0.1, 1.0).values
Ep = vp.E.where(vp.E > 0).values; lmc = np.log(vp.mc.values)
iu = vp.in_universe.values
n8 = vp.n8.fillna(0).values
c1 = np.where(np.isfinite(vp.u4.values), tc + 0.5 * vp.u4.values, tc)
ubar = np.where(np.isfinite(vp.u8.values), vp.u8.values, 0.0); urt = np.where(np.isfinite(vp.u_route.values), vp.u_route.values, 0.0)
c2 = tc + 0.5 * (n8 / (n8 + 4) * ubar + 4 / (n8 + 4) * urt)
c3 = np.where(np.isfinite(vp.roe_c3.values), vp.roe_c3.values, tc)
for nm, rn in (("C1", c1), ("C2", c2), ("C3", c3)):
    rn = np.clip(rn, -0.1, 0.5)
    vp["lv_" + nm] = np.log(rim_vb(rn, R, GT, ret, 0.4) * Ep) - lmc
    LOG[nm] = {"share_changed_vs_D0_in_univ": float((np.abs(vp["lv_" + nm] - vp.lv_D0) > 1e-9)[iu].mean()),
               "median_dlv_in_univ": float((vp["lv_" + nm] - vp.lv_D0)[iu].median()), "median_roe_n_minus_tc_in_univ": float(np.nanmedian((rn - tc)[iu]))}
# kiểm tái lập D0 (cùng công thức, roe_n = tc) ⇒ phải khớp lv_D0 snapshot
d0 = np.log(rim_vb(tc, R, GT, ret, 0.4) * Ep) - lmc
LOG["D0_recompute_maxabs"] = float(np.nanmax(np.abs(d0 - vp.lv_D0.values)))
LOG["u_median_in_univ_annual_ROEpts"] = float(np.nanmedian(vp.u4.values[iu]))
vp.to_parquet(os.path.join(OC, "vp2.parquet"))
json.dump(LOG, open(os.path.join(OC, "C_build.json"), "w"), indent=1)
print(json.dumps(LOG, indent=1))
