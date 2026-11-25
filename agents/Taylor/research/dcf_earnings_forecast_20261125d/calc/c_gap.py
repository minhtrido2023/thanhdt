# -*- coding: utf-8 -*-
"""c_gap.py — PRELOCK §3 (B). gap = log(V_D0/MC_rel) tại K (MC_rel = giá thô × N cùng ngày công bố; KHÔNG dùng mc tháng của panel).
In: ../out/events.parquet, ../out/fc.parquet, data/bq_cache/ticker, universe_pit. Out: ../out/B_*.csv, ../out/gapev.parquet"""
import os, json
import numpy as np, pandas as pd, duckdb
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out"); WC = "/home/trido/thanhdt/WorkingClaude"
SEED = 20261125; B = 2000
ev = pd.read_parquet(os.path.join(OUT, "events.parquet"))
ev = ev[ev.iuK & ev.hist8 & (ev.E > 0) & ev.era.isin(["IS", "OOS"]) & ev.V_D0.notna() & (ev.MC_rel > 0)].copy()
ev["qps"] = ev.qp.astype(str)
fc = pd.read_parquet(os.path.join(OUT, "fc.parquet"))
# ---- sai số đã lộ (origin q-1, h=1) & tương lai (origin q, h=1..4) ----
f1 = fc[fc.h == 1][["ticker", "qp", "e_ENS", "e_D0imp", "e_SRW"]].copy()
f1["qi"] = pd.PeriodIndex(f1.qp, freq="Q").year * 4 + pd.PeriodIndex(f1.qp, freq="Q").quarter
ev["qi"] = ev.qp.dt.year * 4 + ev.qp.dt.quarter
lag = {}
for L in range(1, 5):   # sai số quý q-L+1 lộ tại K_{q-L+1}: origin q-L
    t = f1[["ticker", "qi", "e_ENS", "e_D0imp", "e_SRW"]].copy(); t["qi"] += L
    t.columns = ["ticker", "qi", f"eps_l{L}", f"u_l{L}", f"sue_l{L}"]; ev = ev.merge(t, on=["ticker", "qi"], how="left")
ev["eps"] = ev.eps_l1; ev["u"] = 4 * ev.u_l1; ev["sue"] = ev.sue_l1
ev["ceps"] = ev[[f"eps_l{L}" for L in range(1, 5)]].sum(axis=1, min_count=4)
ev["cu"] = 4 * ev[[f"u_l{L}" for L in range(1, 5)]].sum(axis=1, min_count=4)
fut = fc.pivot_table(index=["ticker", "qp"], columns="h", values=["e_ENS", "e_D0imp"]); fut.columns = [f"{a}_h{b}" for a, b in fut.columns]; fut = fut.reset_index()
fut["eps4"] = fut[[f"e_ENS_h{h}" for h in range(1, 5)]].sum(axis=1, min_count=4); fut["u4"] = fut[[f"e_D0imp_h{h}" for h in range(1, 5)]].sum(axis=1, min_count=4)
fut["eps1f"] = fut.e_ENS_h1
ev = ev.merge(fut[["ticker", "qp", "eps4", "u4", "eps1f"]].rename(columns={"qp": "qps"}), on=["ticker", "qps"], how="left")
ev["gap"] = np.log(ev.V_D0 / ev.MC_rel); ev["ep"] = ev.np_ttm / ev.MC_rel; ev["bp"] = ev.E / ev.MC_rel; ev["lsize"] = np.log(ev.MC_rel)
# [J3 vá skeptic (1)] null KHÔNG GIÁ, KHÔNG MÔ HÌNH: nroe = −ROE_ttm; nlv = log vb(tc5) − log vb(ROE_ttm) (cùng rim_vb của D0)
def rim_vb(roe_n, r=0.1225, gT=0.055, ret=None, kappa=0.4, H=10):          # chép nguyên văn d_update.py
    roe_lr = r + kappa * (roe_n - r); B = np.ones_like(roe_n); pv = np.zeros_like(roe_n)
    for t in range(1, H + 1):
        roe_t = roe_n + (roe_lr - roe_n) * t / 10.0
        g_raw = np.clip(roe_t * ret, 0, 0.15); g_t = gT + (g_raw - gT) * (H - t) / (H - 1.0)
        g_t = np.minimum(g_t, np.maximum(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B = B * (1 + g_t)
    g_term = np.minimum(gT, np.maximum(roe_lr, 0.0))
    return np.maximum(1 + pv + (roe_lr - r) * B / (r - g_term) / (1 + r) ** H, 0.2)
ev["roe_ttm"] = ev.np_ttm / ev.E; ev["nroe"] = -ev.roe_ttm
_ret = (1 - ev.payout.fillna(0.3)).clip(0.1, 1.0).values
ev["nlv"] = np.log(rim_vb(ev.roe_tc5.clip(-0.1, 0.4).values, ret=_ret)) - np.log(rim_vb(ev.roe_ttm.clip(-0.1, 0.5).values, ret=_ret))
# ---- giá ngày (Close điều chỉnh) ----
c = duckdb.connect()
px = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') WHERE Close > 0 AND time >= '2012-01-01'").df()
px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
uni = c.execute(f"SELECT ticker, CAST(time AS DATE) AS time FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df(); uni["time"] = pd.to_datetime(uni.time)
px["lr"] = px.groupby("ticker").Close.transform(lambda s: np.log(s).diff())
mk = px.merge(uni.assign(iu=True), on=["ticker", "time"], how="inner")
mk = mk[mk.lr.abs() < 0.25].groupby("time").lr.mean()                     # EW universe, bỏ bước nhảy lỗi dữ liệu
cal = pd.DatetimeIndex(sorted(px.time.unique())); M = mk.reindex(cal).fillna(0).cumsum()
px["lp"] = np.log(px.Close)
P = px.pivot(index="time", columns="ticker", values="lp").reindex(cal).ffill(limit=5)
def at(tk, idx):
    ok = (idx >= 0) & (idx < len(cal)) & tk.isin(P.columns).values
    out = np.full(len(tk), np.nan); cols = P.columns.get_indexer(tk[ok]); out[ok] = P.values[idx[ok], cols]; return out
def idx_ge(d):   # phiên đầu tiên ≥ d
    return np.searchsorted(cal.values, d.values.astype("datetime64[ns]"), side="left")
ev = ev.reset_index(drop=True)
i0 = idx_ge(ev.K) + 1                                                    # vào phiên sau K (đóng cửa phiên K+1)
ka = ev.KA1.where(ev.KA1.notna(), pd.NaT); hasA = ka.notna().values
ia = np.where(hasA, idx_ge(ka.fillna(pd.Timestamp("2100-01-01"))), -1)
tk = ev.ticker
def radj(a, b):
    ok = (a >= 0) & (b > a) & (b < len(cal))
    r = at(tk, np.where(ok, b, -1)) - at(tk, np.where(ok, a, -1)); m = np.full(len(a), np.nan)
    m[ok] = M.values[b[ok]] - M.values[a[ok]]
    return np.where(ok, r - m, np.nan)
ev["r_pre"] = radj(i0, ia - 2); ev["r_ann"] = radj(ia - 2, ia + 2); ev["n_pre"] = np.where(hasA, ia - 2 - i0, np.nan)
ev["mom"] = at(tk, i0 - 22) - at(tk, i0 - 253)
ev.to_parquet(os.path.join(OUT, "gapev.parquet"))

def sp(a, b):
    return np.corrcoef(pd.Series(a).rank().values, pd.Series(b).rank().values)[0, 1]
def resid(df, x, ctrls):
    X = np.column_stack([np.ones(len(df))] + [df[cc].rank().values for cc in ctrls]); y = df[x].rank().values
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
def ic_series(d, x, y, ctrls=None, absx=False, absy=False):
    out = []
    for q, s in d.groupby("qps"):
        cols = [x, y] + (ctrls or []); s = s[np.isfinite(s[cols]).all(axis=1)]
        if len(s) < 30:
            continue
        xv = s[x].abs() if absx else s[x]; yv = s[y].abs() if absy else s[y]
        if ctrls:
            s2 = s.assign(_x=xv); xv = resid(s2, "_x", ctrls)
        out.append((q, int(s.yr.iloc[0]), sp(xv, yv), len(s)))
    return pd.DataFrame(out, columns=["q", "yr", "ic", "n"])
def boot(icd, seed=SEED, lo=2.5, hi=97.5):
    if len(icd) == 0:
        return np.nan, np.nan, np.nan
    ys = icd.yr.unique(); rng = np.random.RandomState(seed); by = {y: icd.ic[icd.yr == y].values for y in ys}
    res = np.array([np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)])
    PV[0] = float(min(1.0, 2 * min((res <= 0).mean(), (res >= 0).mean())))     # p bootstrap 2 phía (J3: cho BH)
    return float(icd.ic.mean()), float(np.percentile(res, lo)), float(np.percentile(res, hi))
PV = [np.nan]
def bootdiff(a, b, seed=SEED):
    m = a.merge(b, on=["q", "yr"], suffixes=("_a", "_b")); m["ic"] = m.ic_a - m.ic_b
    return boot(m[["q", "yr", "ic"]].assign(n=0), seed)
CT = ["ep", "lsize", "roe_tc5", "mom"]
tests = [("B1", "gap", "cu", None, False, False), ("B1", "gap", "ceps", None, False, False), ("B1abs", "gap", "ceps", None, True, True), ("B1abs", "gap", "cu", None, True, True),
         ("B1_ctrlEP", "gap", "cu", ["ep"], False, False), ("B1_ctrl4", "gap", "cu", CT, False, False),
         ("B2", "gap", "eps4", None, False, False), ("B2", "gap", "u4", None, False, False), ("B2", "gap", "eps1f", None, False, False),
         ("B2_ctrl4", "gap", "eps4", CT, False, False), ("B2_ctrl4", "gap", "u4", CT, False, False),
         ("B2null", "ep", "eps4", None, False, False), ("B2null", "bp", "eps4", None, False, False), ("B2null", "ep", "u4", None, False, False), ("B2null", "bp", "u4", None, False, False),
         ("B3", "gap", "r_pre", None, False, False), ("B3", "gap", "r_ann", None, False, False), ("B3_ctrl4", "gap", "r_pre", CT, False, False), ("B3_ctrl4", "gap", "r_ann", CT, False, False),
         ("B3null", "ep", "r_pre", None, False, False), ("B3null", "ep", "r_ann", None, False, False), ("B3null", "bp", "r_pre", None, False, False), ("B3null", "bp", "r_ann", None, False, False),
         ("B3sue", "sue", "r_ann", None, False, False), ("B3sue", "eps", "r_ann", None, False, False),
         # [J3] null không giá + phần IC TĂNG THÊM của gap trên null (gap phần dư hạng sau null)
         ("B1null", "nroe", "cu", None, False, False), ("B1null", "nlv", "cu", None, False, False),
         ("B1null_ctrl4", "nroe", "cu", CT, False, False), ("B1null_ctrl4", "nlv", "cu", CT, False, False),
         ("B1inc", "gap", "cu", ["nroe"], False, False), ("B1inc", "gap", "cu", ["nlv"], False, False), ("B1inc", "gap", "cu", ["nroe", "nlv"], False, False),
         ("B1inc_ctrl4", "gap", "cu", CT + ["nroe"], False, False), ("B1inc_ctrl4", "gap", "cu", CT + ["nlv"], False, False),
         ("B2null", "nroe", "u4", None, False, False), ("B2null", "nlv", "u4", None, False, False),
         ("B2inc", "gap", "u4", ["nroe"], False, False), ("B2inc", "gap", "u4", ["nlv"], False, False), ("B2inc_ctrl4", "gap", "u4", CT + ["nroe"], False, False),
         ("B2null", "nroe", "eps4", None, False, False), ("B2inc", "gap", "eps4", ["nroe"], False, False),
         ("B3null", "nroe", "r_pre", None, False, False), ("B3inc", "gap", "r_pre", ["nroe"], False, False), ("B3inc", "gap", "r_pre", ["ep", "nroe"], False, False)]
res = []; SER = {}
for era in ("IS", "OOS"):
    d = ev[ev.era == era]
    for tag, x, y, ct, ax, ay in tests:
        s = ic_series(d, x, y, ct, ax, ay); SER[(era, tag, x, y)] = s
        m, lo, hi = boot(s)
        res.append({"era": era, "test": tag, "x": ("|" + x + "|") if ax else x, "y": ("|" + y + "|") if ay else y, "ctrl": ",".join(ct) if ct else "", "IC": m, "ci95_lo": lo, "ci95_hi": hi,
                    "n_q": len(s), "n_yr": int(s.yr.nunique()) if len(s) else 0, "n_ev_mean": float(s.n.mean()) if len(s) else np.nan, "p_boot": PV[0],
                    "R2rank_q_mean": float((s.ic ** 2).mean()) if len(s) else np.nan, "n_pos_yr": int((s.groupby("yr").ic.mean() > 0).sum()) if len(s) else 0})
    for y in ("eps4", "u4", "r_pre", "r_ann"):
        m, lo, hi = bootdiff(SER[(era, "B2" if y in ("eps4", "u4") else "B3", "gap", y)], SER[(era, "B2null" if y in ("eps4", "u4") else "B3null", "ep", y)])
        res.append({"era": era, "test": "dIC_gap_minus_EP", "x": "gap-ep", "y": y, "ctrl": "", "IC": m, "ci95_lo": lo, "ci95_hi": hi})
    for nul in ("nroe", "nlv"):   # [J3] ΔIC(gap − null không giá) cho B1 (cu) và B2 (u4); âm = gap mạnh hơn (cùng chiều âm)
        for tg, y in (("B1", "cu"), ("B2", "u4")):
            m, lo, hi = bootdiff(SER[(era, tg, "gap", y)], SER[(era, tg + "null", nul, y)])
            res.append({"era": era, "test": f"dIC_gap_minus_{nul}", "x": f"gap-{nul}", "y": y, "ctrl": "", "IC": m, "ci95_lo": lo, "ci95_hi": hi})
    # tập trung quanh công bố: IC/phiên (khai PRELOCK) + chênh tercile trên−dưới /phiên (bổ sung)
    npre = float(d.n_pre.median()); nann = 4.0
    a = SER[(era, "B3", "gap", "r_pre")].copy(); b = SER[(era, "B3", "gap", "r_ann")].copy()
    a["ic"] = a.ic / npre; b["ic"] = b.ic / nann
    m, lo, hi = bootdiff(b, a)
    res.append({"era": era, "test": "B3_conc_ICperSession_ann_minus_pre", "x": "gap", "y": f"n_pre_med={npre:.0f}", "ctrl": "", "IC": m, "ci95_lo": lo, "ci95_hi": hi})
    sp_rows = []
    for q, s in d.groupby("qps"):
        s = s[np.isfinite(s[["gap", "r_pre", "r_ann"]]).all(axis=1)]
        if len(s) < 30:
            continue
        t = pd.qcut(s.gap.rank(method="first"), 3, labels=False)
        sp_rows.append((q, int(s.yr.iloc[0]), (s.r_pre[t == 2].mean() - s.r_pre[t == 0].mean()) / max(npre, 1), (s.r_ann[t == 2].mean() - s.r_ann[t == 0].mean()) / nann))
    spd = pd.DataFrame(sp_rows, columns=["q", "yr", "pre", "ann"])
    for col in ("pre", "ann"):
        m, lo, hi = boot(spd.rename(columns={col: "ic"})[["q", "yr", "ic"]])
        res.append({"era": era, "test": "B3_T3minusT1_bp_per_session", "x": "gap", "y": col, "ctrl": "", "IC": m * 1e4, "ci95_lo": lo * 1e4, "ci95_hi": hi * 1e4, "n_q": len(spd)})
R = pd.DataFrame(res)
# [J3 vá skeptic (5)] hiệu chỉnh đa kiểm định: BH theo era trên mọi test có p_boot (p bootstrap rời rạc, sàn 1/B)
for era in ("IS", "OOS"):
    mm = (R.era == era) & R.p_boot.notna(); p = R.loc[mm, "p_boot"].clip(lower=1.0 / B).values; o = np.argsort(p); n = len(p)
    q = np.empty(n); q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]; R.loc[mm, "q_BH"] = np.minimum(q, 1)
    R.loc[mm, "n_tests_era"] = n
R.to_csv(os.path.join(OUT, "B_results.csv"), index=False)
# mô tả: gap theo tercile cu (OOS+IS)
ds = []
for era in ("IS", "OOS"):
    d = ev[(ev.era == era) & ev.cu.notna()].copy(); d["cu_t"] = d.groupby("qps").cu.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["cu_thap", "cu_giua", "cu_cao"]))
    ds.append(d.groupby("cu_t", observed=True).agg(n=("gap", "size"), gap_med=("gap", "median"), ep_med=("ep", "median"), cu_med=("cu", "median")).assign(era=era).reset_index())
pd.concat(ds).to_csv(os.path.join(OUT, "B_gap_by_cu.csv"), index=False)
json.dump({"n_events_B": {e: int((ev.era == e).sum()) for e in ("IS", "OOS")}, "cu_coverage": {e: float(ev[ev.era == e].cu.notna().mean()) for e in ("IS", "OOS")},
           "gap_median": {e: float(ev[ev.era == e].gap.median()) for e in ("IS", "OOS")}}, open(os.path.join(OUT, "B_meta.json"), "w"), indent=1)
pd.set_option("display.width", 250)
print(R.round(4).to_string(index=False)); print(pd.concat(ds).round(3).to_string(index=False))
