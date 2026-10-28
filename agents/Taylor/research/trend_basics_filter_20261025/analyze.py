"""Xu hướng liên tục T1-T10 + tương tác value lọc lệnh LAG/BAL — theo PREREG.md (không tune).
Chạy: $DNA_PYEXE analyze.py → trend{,_pin1M}.csv, results.csv, interact_desc.csv, corr.csv, selfcheck.txt"""
import glob, os
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
R0 = f"{ROOT}/mike/agents/Taylor/research"
POS = f"{R0}/ta_trend_entry_filter_20261025/positions{{}}.csv"
FEAT = f"{R0}/lag_bal_discriminators_20261025/features{{}}.csv"
LEDGERS = {"": f"{ROOT}/data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz",
           "_pin1M": glob.glob(f"{ROOT}/data/pinned_ledgers/*R3-park0-pin1M*a6ba34d8*.csv.gz")[0]}
PX = f"{ROOT}/data/bq_cache_asof20260729_postrestate/ticker"
IS_END, B, SEED, NMIN, MINPP = 2019, 5000, 20261025, 100, 0.02
BOOKS = ["LAG", "BAL"]
IND = [("rs60", 1), ("rs120", 1), ("adx14", 1), ("di_spread", 1), ("d_ma50", 1), ("d_ma200", 1), ("slope_ma200", 1),
       ("hhhl", 1), ("up60", 1), ("r2s60", 1), ("pos52", 1), ("atr_ratio", -1), ("dd120", 1), ("vol_tr", 1), ("knife", -1)]
INTER = [("LAG", "ey", "ALL"), ("BAL", "ey", "ALL"), ("BAL", "ebitda_y", "NF")]
TREND_I = ["rs120", "d_ma200", "knife"]

# ---------------------------------------------------------------- giá + chỉ báo
tks = set(pd.read_csv(POS.format("")).ticker) | set(pd.read_csv(POS.format("_pin1M")).ticker)
raw = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "High", "Low", "Close", "Volume"]) for f in sorted(glob.glob(f"{PX}/*.parquet"))])
raw = raw[raw.ticker.isin(tks | {"VNINDEX"})]
raw["time"] = pd.to_datetime(raw.time).astype("datetime64[ns]")
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
vni = raw[raw.ticker == "VNINDEX"].set_index("time").Close.astype(float)
raw = raw[raw.ticker != "VNINDEX"]


def ind(gp):
    gp = gp.reset_index(drop=True)
    h, l, c, v = (gp[k].astype(float) for k in ["High", "Low", "Close", "Volume"])
    vn = gp.time.map(vni).astype(float)
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1, skipna=False)
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0)); mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0))
    pdm[up.isna()] = np.nan; mdm[up.isna()] = np.nan
    ew = lambda s: s.ewm(alpha=1 / 14, adjust=False).mean()
    atr14 = ew(tr)
    pdi, mdi = 100 * ew(pdm) / atr14, 100 * ew(mdm) / atr14
    adx = ew(100 * (pdi - mdi).abs() / (pdi + mdi))
    warm = pd.Series(np.arange(len(gp)) >= 50)
    ma50, ma200 = c.rolling(50).mean(), c.rolling(200).mean()
    lc = np.log(c)
    r = lc.rolling(60).corr(pd.Series(np.arange(len(gp), dtype=float)))
    out = pd.DataFrame({
        "time": gp.time, "ticker": gp.ticker,
        "rs60": lc - lc.shift(60) - (np.log(vn) - np.log(vn.shift(60))),
        "rs120": lc - lc.shift(120) - (np.log(vn) - np.log(vn.shift(120))),
        "adx14": adx.where(warm), "di_spread": (pdi - mdi).where(warm),
        "d_ma50": c / ma50 - 1, "d_ma200": c / ma200 - 1, "slope_ma200": ma200 / ma200.shift(20) - 1,
        "up60": (c > pc).astype(float).where(pc.notna()).rolling(60).mean(),
        "r2s60": r * r.abs(),
        "pos52": (c - l.rolling(252).min()) / (h.rolling(252).max() - l.rolling(252).min()),
        "atr_ratio": tr.rolling(20).mean() / tr.rolling(100).mean(),
        "dd120": c / c.rolling(120).max() - 1,
        "vol_tr": np.log(v.rolling(20).mean() / v.rolling(100).mean()).where(c > c.shift(20)),
        "knife": ((c < ma200) & (ma200 < ma200.shift(20))).astype(float).where(ma200.shift(20).notna()),
        "row": np.arange(len(gp)),
    })
    return out


IDF = pd.concat([ind(gp) for _, gp in raw.groupby("ticker", sort=False)], ignore_index=True).sort_values("time")
HL = {tk: (g.High.astype(float).values, g.Low.astype(float).values) for tk, g in raw.groupby("ticker")}
PIV = {}
for tk, (h, l) in HL.items():
    hs, ls = pd.Series(h), pd.Series(l)
    ph = (hs == hs.rolling(7, center=True).max()).values
    pl = (ls == ls.rolling(7, center=True).min()).values
    PIV[tk] = (np.flatnonzero(ph), np.flatnonzero(pl))


def hhhl(tk, t):
    h, l = HL[tk]; ph, pl = PIV[tk]
    if t < 122:
        return np.nan
    sc = 0
    for idx, arr in [(ph, h), (pl, l)]:
        conf = idx[idx <= t - 3]
        win = np.flatnonzero(conf > t - 120)
        for j in win:
            if j == 0:
                continue
            a, b = arr[conf[j]], arr[conf[j - 1]]
            sc += 1 if a > b else (-1 if a < b else 0)
    return sc


def load(tag):
    p = pd.read_csv(POS.format(tag), parse_dates=["entry_date", "exit_date", "signal_date"])
    p = p[~p.abandoned & ~p.mtm & (p.n_sell > 0)].copy()
    f = pd.read_csv(FEAT.format(tag))[["holding_id", "G", "ey", "ebitda_y"]]
    p = p.merge(f, on="holding_id", how="left", validate="1:1")
    p["signal_date"] = p.signal_date.astype("datetime64[ns]")
    p = pd.merge_asof(p.sort_values("signal_date"), IDF.rename(columns={"time": "ind_date"}), left_on="signal_date",
                      right_on="ind_date", by="ticker", direction="backward")
    p["hhhl"] = [hhhl(tk, int(r)) if r == r else np.nan for tk, r in zip(p.ticker, p.row)]
    p["qtr"] = p.entry_date.dt.to_period("Q").astype(str)
    return p.sort_values(["book", "entry_date", "holding_id"]).reset_index(drop=True)


# ---------------------------------------------------------------- thống kê
def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = np.empty(n); q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.minimum(q, 1)


def pval(ds):
    ds = ds[~np.isnan(ds)]
    return max(2 * min((ds <= 0).mean(), (ds >= 0).mean()), 1 / B)


def boot_d(s, hi, lo, cl):
    """p bootstrap cụm cho mean(ret|hi) − mean(ret|lo)."""
    k = pd.DataFrame({"c": s[cl].values, "a": s.ret.values * hi, "b": hi.astype(float), "e": s.ret.values * lo, "f": lo.astype(float)})
    A = k.groupby("c")[["a", "b", "e", "f"]].sum().values
    S = A[np.random.default_rng(SEED).integers(0, len(A), (B, len(A)))].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        dd = S[:, 0] / S[:, 1] - S[:, 2] / S[:, 3]
    return pval(dd), np.nanpercentile(dd, [2.5, 97.5])


def boot_reg(s, x, cl):
    """ret ~ 1 + x + pr_ey; trả (hệ số x, p cụm)."""
    ok = ~np.isnan(x) & s.ey_pr.notna().values
    t = s[ok]; X = np.column_stack([np.ones(ok.sum()), x[ok], t.ey_pr.values]); y = t.ret.values
    if len(t) < 20 or np.linalg.matrix_rank(X) < 3:
        return np.nan, np.nan
    b = np.linalg.lstsq(X, y, rcond=None)[0][1]
    um, inv = np.unique(t[cl].values, return_inverse=True)
    XX = np.zeros((len(um), 3, 3)); XY = np.zeros((len(um), 3))
    np.add.at(XX, inv, np.einsum("ni,nj->nij", X, X)); np.add.at(XY, inv, X * y[:, None])
    idx = np.random.default_rng(SEED).integers(0, len(um), (B, len(um)))
    SX, SY = XX[idx].sum(1), XY[idx].sum(1)
    good = np.abs(np.linalg.det(SX)) > 1e-12
    bb = np.full(B, np.nan); bb[good] = np.linalg.solve(SX[good], SY[good][..., None])[:, 1, 0]
    return b, pval(bb)


def grp_rank(s, col, keys):
    """phân vị trong nhóm keys; (G,year) có <6 vị thế gộp về (OTHER,year) — Sửa đổi S1."""
    if "G" in keys:
        n = s.groupby(["G", "year"])[col].transform("count")
        gg = s.G.where(n >= 6, "OTHER")
        return s.assign(_g=gg).groupby(["_g", "year"])[col].rank(pct=True)
    return s.groupby(keys)[col].rank(pct=True) if keys else s[col].rank(pct=True)


def groups(s, name, mode):
    """trả (hi, lo) mask cho họ chính; mode 'full' hoặc 'year'."""
    if name == "knife":
        return (s.knife == 1).values, (s.knife == 0).values
    pr = grp_rank(s, name, ["G", "year"]) if mode == "year" else s[name].rank(pct=True)
    return (pr > 2 / 3).values, (pr <= 1 / 3).values


def igroups(s, tr, mode):
    """trong ô value cao: (good, bad)."""
    if tr == "knife":
        return (s.knife == 0).values, (s.knife == 1).values
    if tr == "d_ma200":
        return (s.d_ma200 > 0).values, (s.d_ma200 <= 0).values
    med = s.groupby("year").rs120.transform("median") if mode == "year" else s.rs120.median()
    return (s.rs120 > med).values, (s.rs120 <= med).values


def value_top(sub, vname, scope, mode):
    s = sub[sub[vname].notna() & (sub.G != "NA")]
    if scope == "NF":
        s = s[s.G == "NONFIN"]
    pr = grp_rank(s, vname, ["G", "year"]) if mode == "year" else s.groupby("G")[vname].rank(pct=True)
    return s.assign(vpr=pr)


def dmean(s, hi, lo):
    return s.ret.values[hi].mean() - s.ret.values[lo].mean() if hi.any() and lo.any() else np.nan


def cell(s, gfun, full=True):
    """s đã lọc NaN chỉ báo; gfun(s, mode) → (hi, lo)."""
    hi, lo = gfun(s, "full")
    r = {"N_hi": int(hi.sum()), "N_lo": int(lo.sum()), "Nm": s.ym.nunique(), "Nq": s.qtr.nunique(),
         "Nq_hi": s[hi].qtr.nunique(), "Nq_lo": s[lo].qtr.nunique(),
         "ret_hi": s.ret.values[hi].mean(), "ret_lo": s.ret.values[lo].mean(),
         "med_hi": np.median(s.ret.values[hi]) if hi.any() else np.nan, "med_lo": np.median(s.ret.values[lo]) if lo.any() else np.nan}
    r["d"] = dmean(s, hi, lo)
    for nm, m in [("IS", (s.year <= IS_END).values), ("OOS", (s.year > IS_END).values)]:
        r[f"d_{nm}"], r[f"N_{nm}"] = dmean(s[m], *gfun(s[m], "full")), int(m.sum())
    m = ~s.year.isin([2020, 2021]).values
    r["d_no2021"] = dmean(s[m], *gfun(s[m], "full"))
    m = (s.ret <= s.ret.quantile(0.98)).values
    r["d_trim2"] = dmean(s[m], *gfun(s[m], "full"))
    if not full:
        return r
    r["p_m"], _ = boot_d(s, hi, lo, "ym")
    r["p_q"], (r["ci_lo"], r["ci_hi"]) = boot_d(s, hi, lo, "qtr")
    hy, ly = gfun(s, "year")
    r["d_y"] = dmean(s, hy, ly)
    r["p_y"], _ = boot_d(s, hy, ly, "qtr")
    return r


def run(P, full=True):
    P = P.copy()
    P["ey_pr"] = np.nan
    for bk in BOOKS:
        m = (P.book == bk) & (P.G != "NA") & P.ey.notna()
        P.loc[m, "ey_pr"] = P[m].groupby("G").ey.rank(pct=True)
    rows = []
    for bk in BOOKS:
        sub = P[P.book == bk]
        for name, sgn in IND:
            s = sub[sub[name].notna()].reset_index(drop=True)
            r = {"fam": "main", "book": bk, "ind": name, "exp": sgn, "N": len(s)}
            r.update(cell(s, lambda x, mode, n=name: groups(x, n, mode), full))
            if name != "knife":
                r["rho"] = s[name].corr(s.ret, method="spearman")
            if full:
                x = s.knife.values.astype(float) if name == "knife" else s[name].rank(pct=True).values
                r["b_ctrl"], r["p_ctrl"] = boot_reg(s, x, "qtr")
                r["rho_ey"] = s[name].corr(s.ey, method="spearman")
            rows.append(r)
    for bk, vname, scope in INTER:
        sub = P[P.book == bk]
        for tr in TREND_I:
            base = sub[sub[tr].notna()]
            vt = value_top(base, vname, scope, "full")
            s = vt[vt.vpr > 2 / 3].reset_index(drop=True)
            r = {"fam": "inter", "book": bk, "ind": f"{vname}_top×{tr}", "exp": 1, "N": len(s)}
            r.update(cell(s, lambda x, mode, tr=tr: igroups(x, tr, "full"), full=False))
            if full:
                hi, lo = igroups(s, tr, "full")
                r["p_m"], _ = boot_d(s, hi, lo, "ym")
                r["p_q"], (r["ci_lo"], r["ci_hi"]) = boot_d(s, hi, lo, "qtr")
                vy = value_top(base, vname, scope, "year")
                sy = vy[vy.vpr > 2 / 3].reset_index(drop=True)
                hy, ly = igroups(sy, tr, "year")
                r["d_y"], r["N_y"] = dmean(sy, hy, ly), len(sy)
                r["p_y"], _ = boot_d(sy, hy, ly, "qtr")
                r["b_ctrl"], r["p_ctrl"] = boot_reg(s, hi.astype(float), "qtr")
                lowv = vt[vt.vpr <= 1 / 3]
                r["ret_valtop_all"], r["ret_val_low"], r["N_val_low"] = s.ret.mean(), lowv.ret.mean(), len(lowv)
            rows.append(r)
    return P, pd.DataFrame(rows)


P0, P1 = load(""), load("_pin1M")
for tag, P in [("", P0), ("_pin1M", P1)]:
    P.to_csv(f"{OUT}/trend{tag}.csv", index=False, float_format="%.10g")
P0e, R = run(P0)
_, R1 = run(P1, full=False)
R["q"] = bh(R.p_q)
R["q_month"] = bh(R.p_m)
R = R.merge(R1[["fam", "book", "ind", "d", "N"]].rename(columns={"d": "d_pin1M", "N": "N_pin1M"}), on=["fam", "book", "ind"])
e = R.exp
R["thieu_mau"] = (R.N_hi < NMIN) | (R.N_lo < NMIN)
R["pass"] = ((np.sign(R.d) == e) & (R.d.abs() >= MINPP) & (R.q < 0.10) & (R.p_y < 0.10) & (np.sign(R.d_y) == e)
             & (np.sign(R.d_IS) == e) & (np.sign(R.d_OOS) == e) & (np.sign(R.d_no2021) == e) & (np.sign(R.d_trim2) == e)
             & (np.sign(R.d_pin1M) == e) & (R.d_pin1M.abs() >= MINPP) & (np.sign(R.b_ctrl) == e) & (R.p_ctrl < 0.10) & ~R.thieu_mau)
assert len(R) == 39, len(R)  # PREREG S0: 15×2 + 9
R.to_csv(f"{OUT}/results.csv", index=False, float_format="%.6g")

# tương quan Spearman giữa chỉ báo và với ey (mô tả)
cr = []
for bk in BOOKS:
    c = P0e[P0e.book == bk][[n for n, _ in IND] + ["ey"]].corr(method="spearman", min_periods=60)
    c.insert(0, "ind", c.index); c.insert(0, "book", bk); cr.append(c)
pd.concat(cr).to_csv(f"{OUT}/corr.csv", index=False, float_format="%.3f")

# mô tả value-tertile × xu hướng (ret TB, N) cho 3 cặp tương tác
dsc = []
for bk, vname, scope in INTER:
    sub = P0e[P0e.book == bk]
    for tr in TREND_I:
        vt = value_top(sub[sub[tr].notna()], vname, scope, "full")
        vt["VT"] = np.where(vt.vpr <= 1 / 3, 1, np.where(vt.vpr <= 2 / 3, 2, 3))
        for T, g in vt.groupby("VT"):
            gd, bd = igroups(g, tr, "full")
            dsc.append({"book": bk, "value": vname, "trend": tr, "VT": T, "N": len(g), "ret_all": g.ret.mean(),
                        "N_good": int(gd.sum()), "ret_good": g.ret.values[gd].mean() if gd.any() else np.nan,
                        "N_bad": int(bd.sum()), "ret_bad": g.ret.values[bd].mean() if bd.any() else np.nan})
pd.DataFrame(dsc).to_csv(f"{OUT}/interact_desc.csv", index=False, float_format="%.6g")

# ---------------------------------------------------------------- selfcheck
lines = []
for tag, path in LEDGERS.items():
    L = pd.read_csv(path, low_memory=False, usecols=["record_type", "book", "action", "buy_amount", "sell_amount", "fee"])
    tx = L[(L.record_type == "TX") & L.book.isin(BOOKS)]
    allp = pd.read_csv(POS.format(tag))
    for bk in BOOKS:
        t = tx[tx.book == bk]; b = t.action == "buy"
        cash = (t.sell_amount[~b] - t.fee[~b]).sum() - (t.buy_amount[b] + t.fee[b]).sum()
        lines.append(f"[{tag or 'pin0'}] {bk}: sum pnl ALL positions={allp[allp.book == bk].pnl.sum():.4f} ; TX cash={cash:.4f}")
for tag, P in [("pin0", P0), ("pin1M", P1)]:
    lines.append(f"[{tag}] main N LAG={int((P.book == 'LAG').sum())} BAL={int((P.book == 'BAL').sum())} ; ind_date>signal (PIT viol)={int((P.ind_date > P.signal_date).sum())} ; no ind row={int(P.ind_date.isna().sum())}")
    lines.append(f"[{tag}] NaN per ind: " + ", ".join(f"{n}={int(P[n].isna().sum())}" for n, _ in IND))
open(f"{OUT}/selfcheck.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
pd.set_option("display.width", 320)
print(R[["fam", "book", "ind", "exp", "N_hi", "N_lo", "Nq", "ret_hi", "ret_lo", "d", "d_IS", "d_OOS", "p_m", "p_q", "q", "d_y", "p_y",
         "d_no2021", "d_trim2", "d_pin1M", "b_ctrl", "p_ctrl", "thieu_mau", "pass"]].to_string())
