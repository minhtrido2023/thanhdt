# -*- coding: utf-8 -*-
"""common.py — dựng V_ngắn / V_dài / V(w) + metric K3n, β, chạm từ panel (PRELOCK.md). Không dùng giá
làm đầu vào V; giá (MC0, TR, MCN) chỉ là nhãn chấm."""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
SEED = 20261111
HZ = (12, 24, 36, 60)
WGRID = np.round(np.arange(0, 1.01, 0.1), 2)
Y = 5  # EXPLICIT_YEARS engine


def dcf(base_ni, g, gT, r, b1=0.0, bT=0.0):
    """2 giai đoạn như D._fv_per_share (đơn vị VND). b1/bT = tỉ lệ tái đầu tư (0 cho cơ sở FCFE)."""
    pv = np.zeros_like(base_ni, dtype=float)
    for y in range(1, Y + 1):
        pv += base_ni * (1 + g) ** y * (1 - b1) / (1 + r) ** y
    tv = base_ni * (1 + g) ** Y * (1 + gT) * (1 - bT) / (r - gT)
    return pv + tv / (1 + r) ** Y


def group_icb(c):
    if c is None or not np.isfinite(c):
        return "khac"
    c = int(c)
    if 8600 <= c < 8700: return "BDS"
    if c in (2357, 2353) or 2350 <= c < 2360: return "XD_VLXD"
    if c < 2000: return "taiNguyen_chuKy"
    if 3000 <= c < 4000 or 5300 <= c < 5400: return "tieuDung_banLe"
    if 9000 <= c < 10000: return "congNghe"
    if 7000 <= c < 8000: return "tienIch"
    if 2000 <= c < 3000: return "congNghiep"
    return "khac"


def load(fiin_only=False):
    p = pd.read_parquet(os.path.join(OUT, "panel.parquet")).reset_index(drop=True)
    an = [json.loads(s) for s in p.annual_np]
    p["NI_norm"] = [np.median(a[:3]) if len(a) else np.nan for a in an]
    s3 = np.array([np.sum(a[:3]) if len(a) >= 3 else np.nan for a in an])
    p["q1"] = np.where(s3 > 0, np.clip(p.cfoa3 / s3, 0, 1), np.nan)
    cv = np.array([np.std(a[:5]) / np.mean(a[:5]) if len(a) >= 3 and np.mean(a[:5]) > 0 else np.nan for a in an])
    p["q2"] = np.where(np.isfinite(cv), 1 - np.clip(cv, 0, 1), np.nan)
    roe = p.roe3y.where(p.roe3y.notna(), p.roe_ttm)
    p["roe"] = roe
    ok_s = (p.NI_norm > 0) & (roe > 0)
    b1 = np.clip(p.g_exp / roe, 0, 1); bT = np.clip(p.g_T / roe, 0, 1)
    p["V_s"] = np.where(ok_s, dcf(p.NI_norm.values, p.g_exp.values, p.g_T.values, p.r.values, b1.values, bT.values), np.nan)
    p.loc[~(p.V_s > 0), "V_s"] = np.nan
    base3 = (p.cfoa3 + p.cfinv3) / 3; base5 = (p.cfoa5 + p.cfinv5) / 5
    v3 = dcf(base3.values, p.g_exp.values, p.g_T.values, p.r.values)
    m = p.eng_ok.values
    dev = np.nanmax(np.abs(v3[m] / p.V_l3.values[m] - 1))
    assert dev < 1e-9, f"control V_l3 lệch engine {dev}"
    gate5 = (p.cfoa3 > 0) & (base5 > 0) & p.osh_fin.gt(0)
    p["V_l5"] = np.where(gate5, dcf(base5.values, p.g_exp.values, p.g_T.values, p.r.values), np.nan)
    p["mc_src"] = np.where(p.MC0_fiin.notna(), "fiin", np.where(p.MC0_fb.notna(), "fb", "none"))
    p["MC0"] = p.MC0_fiin.where(p.MC0_fiin.notna(), p.MC0_fb)
    if fiin_only:
        p.loc[p.mc_src != "fiin", "MC0"] = np.nan
    p["yr"] = p["asof"].dt.year
    p["q"] = p["asof"].dt.to_period("Q").astype(str)
    p["grp"] = [group_icb(x) for x in p.icb]
    # chỉ số dòng cùng mã tại as-of ≈ t+N (cho K3u)
    key = {(t, a.to_period("Q")): i for i, (t, a) in enumerate(zip(p.ticker, p["asof"]))}
    for N in HZ:
        p[f"iN{N}"] = [key.get((t, (a + pd.DateOffset(months=N)).to_period("Q")), -1) for t, a in zip(p.ticker, p["asof"])]
    p.attrs["ctrl_dev_V_l3"] = float(dev)
    return p


def blend(p, w, Vl, kind="A"):
    Vs = p.V_s.values
    w = np.asarray(w, float)
    if kind == "G":
        return np.exp(w * np.log(Vs) + (1 - w) * np.log(Vl))
    return w * Vs + (1 - w) * Vl


def metrics(p, V, mask, N):
    """K3n_N, β_N, chạm khi V<MC0, mức, phân tán — trên dòng mask & full_N (trừ mức/phân tán)."""
    MC0 = p.MC0.values
    ok = mask & np.isfinite(V) & (V > 0) & np.isfinite(MC0)
    x0 = np.log(V[ok] / MC0[ok])
    o = {"n": int(ok.sum()), "medVP": float(np.exp(np.median(x0))) if ok.any() else np.nan,
         "iqr": float(np.subtract(*np.percentile(x0, [75, 25]))) if ok.any() else np.nan}
    k = ok & p[f"full{N}"].values
    if k.sum() < 30:
        return o
    r = p.r.values[k]; TR = p[f"TR{N}"].values[k]
    g0 = np.abs(np.log(MC0[k] / V[k]))
    gN = np.abs(np.log(MC0[k] * TR / (V[k] * (1 + r) ** (N / 12))))
    o["nN"] = int(k.sum()); o["K3n"] = float(np.median(gN) / np.median(g0))
    o["beta"] = float(np.polyfit(np.log(V[k] / MC0[k]), np.log(TR), 1)[0])
    t = MC0[k] * p[f"minTR{N}"].values[k] <= V[k]
    need = V[k] < MC0[k]
    o["touch"] = float(t.mean()); o["touch_VltP"] = float(t[need].mean()) if need.any() else np.nan
    o["frac_VltP"] = float(need.mean())
    iN = p[f"iN{N}"].values
    ku = k & (iN >= 0)
    if ku.sum() > 30:
        VN = np.where(ku, V[np.where(iN >= 0, iN, 0)], np.nan)
        MCN = p[f"MCN{N}"].values
        ku = ku & np.isfinite(VN) & (VN > 0) & np.isfinite(MCN)
        if ku.sum() > 30:
            o["K3u"] = float(np.median(np.abs(np.log(MCN[ku] / VN[ku]))) / np.median(np.abs(np.log(MC0[ku] / V[ku]))))
            o["nU"] = int(ku.sum())
    return o


def k3n_vec(MC0, V, TR, r, N):
    g0 = np.abs(np.log(MC0 / V)); gN = np.abs(np.log(MC0 * TR / (V * (1 + r) ** (N / 12))))
    return g0, gN


def boot_k3n(p, Vs_list, mask, N, cluster="ticker", B=1000, seed=SEED):
    """Bootstrap cụm cho K3n của nhiều V (cùng dòng) ⇒ trả mảng (B, len(Vs_list)) để lấy CI và Δ cặp."""
    MC0 = p.MC0.values
    ok = mask & p[f"full{N}"].values & np.isfinite(MC0)
    for V in Vs_list:
        ok &= np.isfinite(V) & (V > 0)
    idx = np.where(ok)[0]
    G = [k3n_vec(MC0[idx], V[idx], p[f"TR{N}"].values[idx], p.r.values[idx], N) for V in Vs_list]
    cl = p[cluster].values[idx]
    groups = list(pd.Series(np.arange(len(idx))).groupby(cl).indices.values())
    rng = np.random.default_rng(seed)
    out = np.empty((B, len(Vs_list)))
    for b in range(B):
        s = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        for j, (g0, gN) in enumerate(G):
            out[b, j] = np.median(gN[s]) / np.median(g0[s])
    point = np.array([np.median(gN) / np.median(g0) for g0, gN in G])
    return point, out, len(idx), len(groups)


def ci(a):
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
