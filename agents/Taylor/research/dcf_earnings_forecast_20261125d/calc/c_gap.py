# -*- coding: utf-8 -*-
"""c_gap.py — PRELOCK §3 (B). gap = log(V_D0/MC_rel) tại K (MC_rel = giá thô × N cùng ngày công bố; KHÔNG dùng mc tháng của panel).
In: ../out/events.parquet, ../out/fc.parquet, data/bq_cache/ticker, universe_pit. Out: ../out/B_*.csv, ../out/gapev.parquet"""
import os, json
import numpy as np, pandas as pd, duckdb
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out"); WC = "/home/trido/thanhdt/WorkingClaude"
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
    res = [np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)]
    return float(icd.ic.mean()), float(np.percentile(res, lo)), float(np.percentile(res, hi))
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
         ("B3sue", "sue", "r_ann", None, False, False), ("B3sue", "eps", "r_ann", None, False, False)]
res = []; SER = {}
for era in ("IS", "OOS"):
    d = ev[ev.era == era]
    for tag, x, y, ct, ax, ay in tests:
        s = ic_series(d, x, y, ct, ax, ay); SER[(era, tag, x, y)] = s
        m, lo, hi = boot(s)
        res.append({"era": era, "test": tag, "x": ("|" + x + "|") if ax else x, "y": ("|" + y + "|") if ay else y, "ctrl": ",".join(ct) if ct else "", "IC": m, "ci95_lo": lo, "ci95_hi": hi,
                    "n_q": len(s), "n_yr": int(s.yr.nunique()) if len(s) else 0, "n_ev_mean": float(s.n.mean()) if len(s) else np.nan})
    for y in ("eps4", "u4", "r_pre", "r_ann"):
        m, lo, hi = bootdiff(SER[(era, "B2" if y in ("eps4", "u4") else "B3", "gap", y)], SER[(era, "B2null" if y in ("eps4", "u4") else "B3null", "ep", y)])
        res.append({"era": era, "test": "dIC_gap_minus_EP", "x": "gap-ep", "y": y, "ctrl": "", "IC": m, "ci95_lo": lo, "ci95_hi": hi})
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
R = pd.DataFrame(res); R.to_csv(os.path.join(OUT, "B_results.csv"), index=False)
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
