# -*- coding: utf-8 -*-
"""c_models2.py — 18 biến thể khai ở PRELOCK V2 §1 + null N0/EP/BP. Cột lv_<tên> = log(V/P) = log(V_total/MC).
In: ../out/panel2.parquet, ../out/engine_A2.parquet. Out: ../out/vp2.parquet, ../out/models_fit.json (trọng số/META fit trên IS)."""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out")
R = 0.1225; GT = 0.055; H = 10
FIN_ROUTES = ["BANK", "INSURANCE", "SECURITIES"]

def rim_vb(roe_n, r, gT, ret, kappa):
    """V/B: ROE đi tuyến tính từ roe_n về r + kappa·(roe_n − r) trong 10 năm; terminal RI tăng gT (như D0 vòng 1)."""
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)

def ddm_vb(roe_n, p, r, gT):
    B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    g1 = np.clip(roe_n * (1 - p), 0, 0.15)
    for t in range(1, H + 1):
        g_t = gT + (g1 - gT) * (H - t) / (H - 1.0); g_t = np.minimum(g_t, np.maximum(roe_n, 0))
        pv += (roe_n - g_t) * B / (1 + r) ** t             # cổ tức năm t = LN − phần giữ lại để tăng vốn chủ g_t
        B = B * (1 + g_t)
    d11 = np.where(roe_n > gT, (roe_n - gT) * B, p * roe_n * B)
    return pv + d11 / (r - gT) / (1 + r) ** H

pan = pd.read_parquet(os.path.join(OUT, "panel2.parquet")).sort_values(["ticker", "ym"]).reset_index(drop=True)
pan["mi"] = pd.PeriodIndex(pan.ym, freq="M").year * 12 + pd.PeriodIndex(pan.ym, freq="M").month
E = pan.E.where(pan.E > 0).values; mc = pan.mc.values; lmc = np.log(mc)
roe = pan.roe.clip(-0.3, 0.5).values; tc = pan.roe_tc5.clip(-0.1, 0.4).values
ret = (1 - pan.payout.fillna(0.3)).clip(0.1, 1.0).values
isfin = pan.route.isin(FIN_ROUTES).values
L = {}
# ---- null/đối chứng ----
pan["ep"] = pan.np_ttm / pan.mc; pan["bp"] = pan.E / pan.mc; pan["sp"] = pan.rev_ttm / pan.mc
ev = pan.mc + pan.debt.fillna(0) - pan.cash.fillna(0); pan["ev"] = ev
g = pan.groupby("ticker")
pan["lv_N0"] = np.log(g.Close.transform(lambda x: x.shift(1).rolling(60, min_periods=24).median()) / pan.Close)
# ---- 3. D0, 4. D0J, 5. D0B ----
vb0 = rim_vb(tc, R, GT, ret, 0.4); L["D0"] = np.log(vb0 * E) - lmc
w = np.where(pan.jump_k.values >= 2, 0.75 * np.minimum(1.0, pan.jump_k.values / 4.0), 0.0)
rn_j = np.clip(tc + w * (np.clip(roe, -0.1, 0.5) - tc), -0.1, 0.5)
L["D0J"] = np.log(rim_vb(rn_j, R, GT, ret, 0.4) * E) - lmc
kap = np.where(pan.route.values == "BANK", 0.7, 0.4)
vbB = rim_vb(rn_j, R, GT, ret, kap); L["D0B"] = np.log(vbB * E) - lmc
# ---- 6. DDM ----
p = pan.payout.clip(0.05, 1.0).values
elig = (pan.div_cnt20.values >= 16) & (rn_j > 0.01) & np.isfinite(p)
L["DDM"] = np.where(elig, np.log(np.maximum(ddm_vb(np.maximum(rn_j, 0.011), np.nan_to_num(p, nan=0.3), R, GT), 1e-6) * E) - lmc, np.nan)
# ---- 7. EPV ----
e_norm = (pan.rev_ttm * pan.npm_med5).values
gg = np.minimum(GT, rn_j * ret)
okv = (~isfin) & (e_norm > 0) & (rn_j > gg + 0.005) & np.isfinite(E)
with np.errstate(all="ignore"):
    L["EPV"] = np.where(okv, np.log(e_norm * (1 - gg / rn_j) / (R - gg)) - lmc, np.nan)
# ---- 1. A_pit, 2. A_RI ----
A = pd.read_parquet(os.path.join(OUT, "engine_A2.parquet"))
pan = pan.merge(A[["ticker", "ym", "ok", "FV_total", "g_exp", "g_T", "r", "np3"]].rename(columns={"ok": "A_ok", "r": "A_r"}), on=["ticker", "ym"], how="left")
bavg = pan[["E_1y", "E_3y"]].mean(axis=1).fillna(pan.E)
ri = pan.np3 - pan.A_r * bavg
gx = pan.g_exp; gt_ = pan.g_T; r_ = pan.A_r
pvri = sum(ri * (1 + gx) ** y / (1 + r_) ** y for y in range(1, 6))
tvri = ri * (1 + gx) ** 5 * (1 + gt_) / (r_ - gt_) / (1 + r_) ** 5
v_ri = np.maximum(pan.E + pvri + tvri, 0.2 * pan.E.clip(lower=0))
ok = pan.A_ok.fillna(False).astype(bool) & (pan.FV_total > 0)
pan["_lva"] = np.where(ok, np.log(pan.FV_total.where(pan.FV_total > 0)), np.nan)
pan["_lvr"] = np.where(ok & (v_ri > 0), np.log(v_ri.where(v_ri > 0)), np.nan)
for src, name in (("_lva", "A_pit"), ("_lvr", "A_RI")):                      # V giữ cố định trong quý (tối đa 2 tháng), P trượt
    L[name] = (pan.groupby("ticker")[src].ffill(limit=2) - np.log(pan.mc)).values
# ---- 8. MULT (bội số ngành, trung vị 60 tháng trước) ----
with np.errstate(all="ignore"):
    M = {"pe": np.log(mc / (tc * E)), "pb": np.log(mc / E), "ps": np.where(isfin, np.nan, np.log(mc / pan.rev_ttm.where(pan.rev_ttm > 0).values)),
         "ee": np.where(isfin, np.nan, np.log(ev.where(ev > 0).values / pan.ebit_ttm.where(pan.ebit_ttm > 0).values)),
         "pd": np.log(mc / pan.div_ttm.where(pan.div_ttm > 0).values)}
for k in M:
    M[k] = np.where(np.isfinite(M[k]), M[k], np.nan); pan["m_" + k] = M[k]
iu = pan.in_universe.values
mult_est = []
for k in ("pe", "pb", "ps", "ee"):
    d = pan.loc[iu, ["mi", "route", "m_" + k]].dropna()
    rm = d.groupby(["mi", "route"])["m_" + k].agg(["median", "count"]).reset_index()
    mm = d.groupby("mi")["m_" + k].median().rename("mkt")
    rm = rm.merge(mm, on="mi"); rm["v"] = np.where(rm["count"] >= 8, rm["median"], rm.mkt)
    piv = rm.pivot(index="mi", columns="route", values="v").reindex(range(pan.mi.min(), pan.mi.max() + 1))
    piv = piv.apply(lambda s: s.fillna(mm.reindex(piv.index)))
    tr = piv.shift(1).rolling(60, min_periods=24).mean().stack().rename("mult").reset_index()
    x = pan[["mi", "route"]].merge(tr, on=["mi", "route"], how="left").mult.values
    if k == "pe":
        v = np.exp(x) * tc * E
    elif k == "pb":
        v = np.exp(x) * E
    elif k == "ps":
        v = np.where(isfin, np.nan, np.exp(x) * pan.rev_ttm.values)
    else:
        v = np.where(isfin, np.nan, np.exp(x) * pan.ebit_ttm.values - pan.debt.fillna(0).values + pan.cash.fillna(0).values)
    with np.errstate(all="ignore"):
        mult_est.append(np.where(v > 0, np.log(v), np.nan) - lmc)
me_ = np.vstack(mult_est); cnt = np.isfinite(me_).sum(0)
with np.errstate(all="ignore"):
    L["MULT"] = np.where(cnt >= 2, np.nanmedian(me_, axis=0), np.nan)
# ---- 9–11. HED (hồi quy hedonic log P/B, gộp 60 tháng trước) ----
routes = [r for r in sorted(pan.route.unique()) if r != "COMPOUNDER"]
def hed(extra_liq, freeze_mi=None):
    X = pd.DataFrame({"c": 1.0, "tc": tc, "roe": np.clip(roe, -0.3, 0.5), "loss": (pan.np_ttm.values < 0).astype(float), "revg": pan.revg.fillna(0).values,
                      "po": pan.payout.fillna(0.3).clip(0, 1).values, "lev": (pan.debt.fillna(0) / pan.E.where(pan.E > 0)).clip(0, 3).values,
                      "sd": pan.roe_sd5.fillna(pan.roe_sd5.median()).values, "le": np.log(E)})
    if extra_liq:
        X["ltv"] = np.log(pan.tv.where(pan.tv > 0)).fillna(np.log(pan.tv.where(pan.tv > 0)).median()).values
    for r in routes:
        X["r_" + r] = (pan.route.values == r).astype(float)
    y = M["pb"]; Xv = X.values; good = np.isfinite(Xv).all(1) & np.isfinite(y)
    fit = good & iu; mi = pan.mi.values; lo, hi = mi.min(), mi.max(); p_ = Xv.shape[1]
    xtx = np.zeros((hi - lo + 2, p_, p_)); xty = np.zeros((hi - lo + 2, p_)); nm = np.zeros(hi - lo + 2)
    for m in np.unique(mi[fit]):
        s = fit & (mi == m); a = Xv[s]; yy = np.clip(y[s], np.nanpercentile(y[s], 1), np.nanpercentile(y[s], 99))
        xtx[m - lo] = a.T @ a; xty[m - lo] = a.T @ yy; nm[m - lo] = 1
    pred = np.full(len(pan), np.nan); betas = {}
    for m in range(lo, hi + 1):
        mm_ = min(m, freeze_mi) if freeze_mi else m
        a0 = max(0, mm_ - lo - 60); a1 = mm_ - lo                      # tháng mm_−60 .. mm_−1
        if nm[a0:a1].sum() < 24:
            continue
        b = np.linalg.lstsq(xtx[a0:a1].sum(0) + 1e-6 * np.eye(p_), xty[a0:a1].sum(0), rcond=None)[0]; betas[m] = b
        s = good & (mi == m); pred[s] = Xv[s] @ b
    return pred - y, X.columns.tolist(), betas
FRZ = 2020 * 12 + 1
L["HEDf"], hcols, hb = hed(False, FRZ); L["HEDr"], _, _ = hed(False); L["HEDL"], _, _ = hed(True)
# ---- 12. REL (bội số lịch sử của chính mã) ----
rel = []
for k in ("pe", "pb", "ps", "ee", "pd"):
    med = pan.groupby("ticker")["m_" + k].transform(lambda x: x.shift(1).rolling(60, min_periods=24).median())
    rel.append((med - pan["m_" + k]).values)
rel = np.vstack(rel)
with np.errstate(all="ignore"):
    L["REL"] = np.where(np.isfinite(rel).sum(0) >= 2, np.nanmedian(rel, axis=0), np.nan)
for k, v in L.items():
    pan["lv_" + k] = np.where(np.isfinite(v), v, np.nan)
# ---- 13. G1 và premium riêng ----
def own_prem(col):
    return pan.groupby("ticker")[col].transform(lambda x: x.shift(1).rolling(60, min_periods=24).median())
pan["lv_G1"] = pan.lv_D0 - own_prem("lv_D0")
# ---- 14–17. tổ hợp ----
def ens(cols, minn=1):
    a = pan[cols].values; n = np.isfinite(a).sum(1)
    with np.errstate(all="ignore"):
        med = np.where(n >= minn, np.nanmedian(a, axis=1), np.nan)
        q25 = np.nanpercentile(a, 25, axis=1); q75 = np.nanpercentile(a, 75, axis=1); sd = np.where(n >= 3, np.nanstd(a, axis=1), np.nan)
    return med, q25, q75, sd, n
C1 = ["lv_D0B", "lv_DDM", "lv_EPV"]; C2 = C1 + ["lv_MULT", "lv_HEDf"]
pan["lv_ENS1"], _, _, _, pan["n_ENS1"] = ens(C1)
pan["lv_ENS2"], pan["zlo_ENS2"], pan["zhi_ENS2"], pan["sd_ENS2"], pan["n_ENS2"] = ens(C2)
# nhãn dùng cho fit IS: lợi suất vượt trội 36T so rổ EW lập tại as-of (kịch bản chính H = −50%)
u = pan.in_universe & (pan.ym >= "2014-01")
bm = np.log(pan[u].assign(x=np.exp(pan.fwd36_h50)).groupby("ym").x.mean())
pan["ex36"] = pan.fwd36_h50 - pan.ym.map(bm)
IS = u & (pan.ym <= "2019-12") & pd.PeriodIndex(pan.ym, freq="M").month.isin([3, 6, 9, 12])
def ic(df, col, minn=30):
    v = [g[[col, "ex36"]].dropna().corr(method="spearman").iloc[0, 1] for _, g in df.groupby("ym") if g[[col, "ex36"]].dropna().shape[0] >= minn]
    return float(np.nanmean(v)) if v else np.nan
ics = {cname: ic(pan[IS], cname) for cname in C2}
wts = {k: max(v, 0) if np.isfinite(v) else 0 for k, v in ics.items()}
a = pan[C2].values; ww = np.array([wts[k] for k in C2]); msk = np.isfinite(a)
with np.errstate(all="ignore"):
    pan["lv_ENS1w"] = np.nansum(np.where(msk, a, 0) * ww, axis=1) / (msk * ww).sum(1)
pan.loc[(msk * ww).sum(1) <= 0, "lv_ENS1w"] = np.nan
meta = {}; pan["lv_META"] = pan.lv_ENS2
for rt, gdf in pan[IS].groupby("route"):
    nn = gdf.groupby("ym").size().mean(); base = ic(gdf, "lv_ENS2", 8)
    cand = {cname: ic(gdf, cname, 8) for cname in C2}; cand["lv_ENS2"] = base
    best = max(C2, key=lambda k: -9 if not np.isfinite(cand[k]) else cand[k])
    pick = best if (nn >= 8 and np.isfinite(cand[best]) and np.isfinite(base) and cand[best] - base >= 0.03) else "lv_ENS2"
    meta[rt] = {"n_avg": round(float(nn), 1), "ic_ENS2": None if not np.isfinite(base) else round(base, 3), "pick": pick, "ic_pick": None if not np.isfinite(cand.get(pick, np.nan)) else round(cand[pick], 3)}
    if pick != "lv_ENS2":
        s = pan.route == rt; pan.loc[s, "lv_META"] = pan.loc[s, pick].fillna(pan.loc[s, "lv_ENS2"])
# ---- 18. L2 = Lớp 1 × premium riêng (tính sẵn cho mọi ứng viên; chỉ bản được chọn ở §5 mới được báo là L2) ----
for base in ("ENS1", "ENS2", "D0B", "D0J", "HEDf", "MULT", "META", "ENS1w"):
    pan[f"lv_L2_{base}"] = pan[f"lv_{base}"] - own_prem(f"lv_{base}")
json.dump({"ic36_IS_components": ics, "weights_ENS1w": wts, "meta": meta, "hed_cols": hcols,
           "hed_beta_frozen_2019-12": dict(zip(hcols, [round(float(x), 4) for x in hb.get(FRZ, [])]))}, open(os.path.join(OUT, "models_fit.json"), "w"), ensure_ascii=False, indent=1)
pan.drop(columns=["_lva", "_lvr"]).to_parquet(os.path.join(OUT, "vp2.parquet"))
cols = [c for c in pan.columns if c.startswith("lv_")]
print(pan[u][cols].describe(percentiles=[.25, .5, .75]).T[["count", "25%", "50%", "75%"]].round(3).to_string())
print(json.dumps({"ic36_IS": ics, "meta": meta}, ensure_ascii=False))
