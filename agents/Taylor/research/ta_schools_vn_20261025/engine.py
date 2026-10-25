"""TA schools VN — engine. Theo PREREG.md (không tune). Chạy: $DNA_PYEXE engine.py
Ghi: panel_events.parquet (sự kiện), results.csv (1 dòng / cấu hình x horizon)."""
import glob, os, sys
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
HZ = [5, 10, 20, 40]
COST = 0.00394
ADV_MIN = 1e9
START = pd.Timestamp("2014-01-01")
IS_END = 2019
B = 5000

# ---------------------------------------------------------------- load
cols = ["time", "ticker", "Open", "High", "Low", "Close", "Volume", "Price"]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
raw["time"] = pd.to_datetime(raw["time"])
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"]).reset_index(drop=True)
vni = raw[raw.ticker == "VNINDEX"].set_index("time").sort_index()
raw = raw[raw.ticker != "VNINDEX"]
u = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/universe_pit/*.parquet"))])
u["time"] = pd.to_datetime(u["time"])
u = u.drop_duplicates(["time", "ticker"])
raw = raw.merge(u, on=["time", "ticker"], how="left")
raw["in_universe"] = raw["in_universe"].fillna(False).astype(bool)
print("rows", len(raw), "tickers", raw.ticker.nunique(), "last", raw.time.max().date())

# VNINDEX forward returns by date
vR = pd.DataFrame(index=vni.index)
for h in HZ:
    vR[f"V{h}"] = vni["Close"].shift(-h) / vni["Open"].shift(-1) - 1
vR = vR.reset_index()

SIGS = ["A1", "A2", "A3"]
for pat in ["ENG", "HAM", "MST"]:
    for ctx in ["unc", "dt"]:
        for vv in ["any", "vol"]:
            SIGS.append(f"B_{pat}_{ctx}_{vv}")
SIGS += ["C1", "C2a", "C2b", "C3", "C4", "D1", "D2", "E1", "E2", "E3", "F2", "F3"]


def cooldown(flag, gap=10):
    idx = np.flatnonzero(flag)
    out = np.zeros(len(flag), dtype=bool)
    last = -10**9
    for i in idx:
        if i - last > gap:
            out[i] = True
            last = i
    return out


def per_ticker(g):
    g = g.reset_index(drop=True)
    o, h, l, c, v, p = (g[k].astype(float) for k in ["Open", "High", "Low", "Close", "Volume", "Price"])
    d = g["time"]
    res = pd.DataFrame({"time": d, "ticker": g["ticker"], "in_universe": g["in_universe"]})
    rng = h - l
    ok = (rng > 0) & (o > 0) & (c > 0) & (l > 0) & (v > 0)
    V20 = v.shift(1).rolling(20).mean()
    S20 = rng.shift(1).rolling(20).mean()
    vr = v / V20
    pos = (c - l) / rng
    body = (c - o).abs()
    adv = (p * v).rolling(20).mean()
    res["adv"] = adv
    ret = c.pct_change()
    bad = (ret.abs() > 0.5).astype(int)
    cs = bad.cumsum()
    bad25 = (cs - cs.shift(26)).fillna(0) > 0
    ratio = c / p
    corp = ((ratio.pct_change().abs() > 0.03)).astype(int)
    cc = corp.cumsum()
    corp25 = (cc - cc.shift(26)).fillna(0) > 0
    # forward returns
    ent_gap = (d.shift(-1) - d).dt.days
    for hh in HZ:
        R = c.shift(-hh) / o.shift(-1) - 1
        okw = (ent_gap <= 5) & ((d.shift(-hh) - d).dt.days <= 1.7 * hh + 10) & ((cs.shift(-hh) - cs) == 0)
        res[f"R{hh}"] = R.where(okw)
    MA20, MA50 = c.rolling(20).mean(), c.rolling(50).mean()
    f2state = (c > MA50) & (MA50 > MA50.shift(10))
    res["f2state"] = f2state.fillna(False)
    S = {}
    # A Ichimoku
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    ssa = ((ten + kij) / 2).shift(26)
    ssb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top = np.maximum(ssa, ssb)
    a1 = (c.shift(1) <= top.shift(1)) & (c > top)
    S["A1"] = a1
    S["A2"] = (ten.shift(1) <= kij.shift(1)) & (ten > kij) & (c > top)
    S["A3"] = a1 & (ten > kij) & (c > c.shift(26))
    # B candles
    rngok = rng >= 0.5 * S20
    eng = (c.shift(1) < o.shift(1)) & (c > o) & (o <= c.shift(1)) & (c >= o.shift(1)) & (body > body.shift(1)) & rngok
    ham = ((np.minimum(o, c) - l) >= 2 * body) & ((h - np.maximum(o, c)) <= 0.1 * rng) & rngok
    rng2, body2, o2, c2 = rng.shift(2), body.shift(2), o.shift(2), c.shift(2)
    mst = (c2 < o2) & (body2 >= 0.6 * rng2) & (body.shift(1) <= 0.3 * body2) & (np.maximum(o, c).shift(1) < c2) & (c > o) & (c > (o2 + c2) / 2) & rngok
    c1 = c.shift(1)
    minL60, maxH60 = l.rolling(60).min().shift(1), h.rolling(60).max().shift(1)
    ctx = (c1 < MA20.shift(1)) & (((c1 - minL60) / (maxH60 - minL60)) <= 0.2)
    for nm, sg in [("ENG", eng), ("HAM", ham), ("MST", mst)]:
        for cn, cm in [("unc", True), ("dt", ctx)]:
            for vn, vm in [("any", True), ("vol", vr > 1.5)]:
                S[f"B_{nm}_{cn}_{vn}"] = sg & cm & vm
    # C VSA
    downrun = (c.shift(1) / c.shift(6) - 1) <= -0.05
    C1 = (vr > 2) & (rng >= 1.2 * S20) & (pos >= 0.5) & downrun
    ns = (vr < 0.7) & (c < o) & (rng <= 0.8 * S20)
    S["C1"] = C1
    S["C2a"] = ns
    S["C2b"] = ns & (c > MA50)
    S["C3"] = (h > h.shift(1).rolling(20).max()) & (pos <= 0.3) & (vr > 1.5) & (rng >= 1.0 * S20)
    c1_recent = C1.shift(1).fillna(False).astype(int).rolling(20).max() > 0
    S["C4"] = (vr < 0.7) & (rng <= 0.8 * S20) & (l <= l.shift(1).rolling(10).min()) & (pos >= 0.5) & c1_recent
    # D Darvas
    dtop = h.shift(1).rolling(20).max()
    stable = h.shift(1).rolling(3).max() < dtop
    brk = (c > dtop) & (c.shift(1) <= dtop.shift(1)) & stable
    S["D1"] = brk & (vr > 1.5)
    S["D2"] = brk
    # E money flow
    mfm = ((c - l) - (h - c)) / rng
    cmf = (mfm * v).rolling(20).sum() / v.rolling(20).sum()
    S["E1"] = (cmf.shift(1) <= 0) & (cmf > 0)
    obv = (np.sign(c.diff()).fillna(0) * v).cumsum()
    S["E2"] = (obv > obv.shift(1).rolling(60).max()) & (c <= c.shift(1).rolling(60).max())
    tp = (h + l + c) / 3
    mf = tp * v
    up = mf.where(tp > tp.shift(1), 0).rolling(14).sum()
    dn = mf.where(tp < tp.shift(1), 0).rolling(14).sum()
    mfi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    S["E3"] = (mfi.shift(1) < 20) & (mfi >= 20)
    # F refs
    S["F2"] = f2state & ~f2state.shift(1).fillna(False).astype(bool)
    S["F3"] = (c > c.shift(1).rolling(252).max()) & (vr > 1.5)
    elig = ok & (adv >= ADV_MIN) & g["in_universe"] & ~bad25 & ~corp25 & (d >= START)
    for k in SIGS:
        f = S[k].fillna(False).to_numpy(dtype=bool) & elig.to_numpy(dtype=bool)
        res[k] = cooldown(f)
    return res


parts = [per_ticker(g) for _, g in raw.groupby("ticker", sort=False)]
P = pd.concat(parts, ignore_index=True)
P = P.merge(vR, on="time", how="left")
P["year"] = P.time.dt.year
P["ym"] = P.time.dt.year * 100 + P.time.dt.month
print("panel", P.shape)

# ---------------------------------------------------------------- controls
P["ctrl"] = P.in_universe & (P.adv >= ADV_MIN) & (P.time >= START)
sub = P.loc[P.ctrl, ["time", "adv"]]
rk = sub.groupby("time")["adv"].rank(pct=True, method="first")
P["tert"] = -1
P.loc[P.ctrl, "tert"] = np.minimum((rk * 3).apply(np.ceil) - 1, 2).astype(int)
for hh in HZ:
    R = P[f"R{hh}"]
    m = P.ctrl & R.notna()
    key = [P.time, P.tert]
    Rm = R.where(m)
    S1 = Rm.groupby(key).transform("sum")
    n1 = m.astype(int).groupby(key).transform("sum")
    ctrl1 = (S1 - Rm) / (n1 - 1)
    ctrl1 = ctrl1.where(m & (n1 >= 10))
    m2 = m & P.f2state
    R2 = R.where(m2)
    S2 = R2.groupby(key).transform("sum")
    n2 = m2.astype(int).groupby(key).transform("sum")
    selfc = m2.astype(int)
    ctrl2 = (S2 - R2.fillna(0)) / (n2 - selfc)
    ctrl2 = ctrl2.where(m & ((n2 - selfc) >= 5))
    P[f"X1_{hh}"] = R - ctrl1
    P[f"X2_{hh}"] = R - ctrl2
    P[f"XV_{hh}"] = R - P[f"V{hh}"] - COST
    P[f"N_{hh}"] = R - COST

# ---------------------------------------------------------------- stats
rng_b = np.random.default_rng(20261025)


def boot_p(vals, ym):
    df = pd.DataFrame({"v": vals, "m": ym})
    gsum = df.groupby("m").v.agg(["sum", "count"])
    s, n = gsum["sum"].to_numpy(), gsum["count"].to_numpy()
    M = len(s)
    if M < 3:
        return np.nan, np.nan, np.nan
    idx = rng_b.integers(0, M, (B, M))
    bm = s[idx].sum(1) / n[idx].sum(1)
    p = 2 * min((bm <= 0).mean(), (bm >= 0).mean())
    return min(max(p, 1.0 / B), 1.0), np.percentile(bm, 2.5), np.percentile(bm, 97.5)


EXPECT = {k: (-1 if k == "C3" else 1) for k in SIGS}
rows = []
for k in SIGS:
    ev = P[P[k]]
    for hh in HZ:
        e = ev[ev[f"X1_{hh}"].notna()]
        r = dict(sig=k, h=hh, N=len(e), N_days=e.time.nunique(), N_tm=e.groupby(["ticker", "ym"]).ngroups, N_months=e.ym.nunique(),
                 N_tickers=e.ticker.nunique())
        r["sufficient"] = bool(r["N"] >= 100 and r["N_months"] >= 24)
        if len(e):
            nt = e[f"N_{hh}"]
            r["hit_net"] = float((nt > 0).mean()); r["med_net"] = float(nt.median())
            r["med_exF1"] = float(e[f"X1_{hh}"].median()); r["mean_exF1"] = float(e[f"X1_{hh}"].mean())
            r["mean_exVNI"] = float(e[f"XV_{hh}"].mean()); r["med_exVNI"] = float(e[f"XV_{hh}"].median())
            isr, oosr = e[e.year <= IS_END], e[e.year > IS_END]
            r["N_IS"], r["N_OOS"] = len(isr), len(oosr)
            r["exF1_IS"] = float(isr[f"X1_{hh}"].mean()) if len(isr) else np.nan
            r["exF1_OOS"] = float(oosr[f"X1_{hh}"].mean()) if len(oosr) else np.nan
            r["p_F1"], r["ci_lo"], r["ci_hi"] = boot_p(e[f"X1_{hh}"].to_numpy(), e.ym.to_numpy())
            e2 = e[e[f"X2_{hh}"].notna()]
            r["N_F2c"] = len(e2)
            r["mean_exF2"] = float(e2[f"X2_{hh}"].mean()) if len(e2) else np.nan
            r["exF2_IS"] = float(e2[e2.year <= IS_END][f"X2_{hh}"].mean()) if (e2.year <= IS_END).any() else np.nan
            r["exF2_OOS"] = float(e2[e2.year > IS_END][f"X2_{hh}"].mean()) if (e2.year > IS_END).any() else np.nan
            r["p_F2"] = boot_p(e2[f"X2_{hh}"].to_numpy(), e2.ym.to_numpy())[0] if len(e2) > 20 else np.nan
            ysum = e.groupby("year")[f"X1_{hh}"].agg(["sum", "count"])
            tot = ysum["sum"].sum()
            loyo = [(tot - ysum.loc[y, "sum"]) / (len(e) - ysum.loc[y, "count"]) for y in ysum.index if len(e) > ysum.loc[y, "count"]]
            r["loyo_min"], r["loyo_max"] = (min(loyo), max(loyo)) if loyo else (np.nan, np.nan)
            top2 = ysum["sum"].abs().sort_values(ascending=False).head(2).sum()
            r["top2_share"] = float(top2 / ysum["sum"].abs().sum()) if len(ysum) else np.nan
        rows.append(r)
Rz = pd.DataFrame(rows)


def bh(p, q=0.10):
    p = pd.Series(p)
    m = p.notna()
    out = pd.Series(np.nan, index=p.index)
    pv = p[m].sort_values()
    n = len(pv)
    adj = (pv * n / (np.arange(1, n + 1))).iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    out[adj.index] = adj
    return out


suf = Rz.sufficient
Rz["q_F1"] = np.nan; Rz["q_F2"] = np.nan
Rz.loc[suf, "q_F1"] = bh(Rz.loc[suf, "p_F1"]).to_numpy()
Rz.loc[suf, "q_F2"] = bh(Rz.loc[suf, "p_F2"]).to_numpy()
Rz["n_trials"] = len(Rz); Rz["n_tested_in_BH"] = int(suf.sum())
Rz["expect"] = Rz.sig.map(EXPECT)


def verdict(r):
    if r.h != 20: return ""
    if not r.sufficient: return "KHONG_DU_MAU"
    s = r.expect
    a = np.sign(r.exF1_IS) == s and np.sign(r.exF1_OOS) == s
    b = r.q_F1 < 0.10 and np.sign(r.mean_exF1) == s
    d = (np.sign(r.loyo_min) == s and np.sign(r.loyo_max) == s) and r.top2_share < 0.60
    e = np.sign(r.mean_exVNI) == s
    if not (a and b and d and e): return "KHONG_QUA"
    f2 = np.sign(r.exF2_IS) == s and np.sign(r.exF2_OOS) == s and r.q_F2 < 0.10 and np.sign(r.mean_exF2) == s
    return "CO_BANG_CHUNG+VUOT_XU_HUONG" if f2 else "CO_BANG_CHUNG(F1)_khong_vuot_F2"


Rz["verdict_h20"] = Rz.apply(verdict, axis=1)
Rz.to_csv(f"{OUT}/results.csv", index=False)
keep = ["time", "ticker", "year", "ym", "adv", "tert"] + [f"{p}{h}" for p in ["R", "V", "X1_", "X2_", "XV_", "N_"] for h in HZ] + SIGS
P.loc[P[SIGS].any(axis=1), keep].to_parquet(f"{OUT}/panel_events.parquet")
print(Rz[Rz.h == 20][["sig", "N", "N_days", "N_months", "sufficient", "exF1_IS", "exF1_OOS", "mean_exF1", "p_F1", "q_F1", "mean_exF2", "q_F2", "verdict_h20"]].to_string())
