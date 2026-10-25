"""Chỉ báo fundamental phân biệt lệnh tốt/xấu trong LAG/BAL — theo PREREG.md (không tune).
Chạy: $DNA_PYEXE analyze.py → features{,_pin1M}.csv, results.csv, tertiles.csv, loo.csv, corr.csv, describe.csv, selfcheck.txt"""
import glob, os
import numpy as np, pandas as pd

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
PREV = f"{ROOT}/mike/agents/Taylor/research/ta_trend_entry_filter_20261025"
LEDGERS = {"": f"{ROOT}/data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz",
           "_pin1M": glob.glob(f"{ROOT}/data/pinned_ledgers/*R3-park0-pin1M*a6ba34d8*.csv.gz")[0]}
CACHE = f"{ROOT}/data/bq_cache_asof20260729_postrestate"
IS_END, B, SEED, NMIN, MINPP = 2019, 5000, 20261025, 100, 0.02
BOOKS = ["LAG", "BAL"]
# (tên, phạm vi ALL/NF, hướng kỳ vọng)
IND = [("payout1Y", "ALL", 1), ("payout3Y", "ALL", 1), ("DY", "ALL", 1), ("div3y", "ALL", 1), ("div_chg", "ALL", 1),
       ("cfo_np", "NF", 1), ("accrual", "NF", -1), ("gpm", "NF", 1), ("d_gpm", "NF", 1), ("roe", "ALL", 1), ("d_roa", "ALL", 1),
       ("de", "NF", -1), ("nd_ebitda", "NF", -1), ("inv_rev", "NF", -1), ("ar_rev", "NF", -1),
       ("rev_yoy", "ALL", 1), ("np_yoy", "ALL", 1), ("np_accel", "ALL", 1),
       ("ey", "ALL", 1), ("by", "ALL", 1), ("cfy", "NF", 1), ("ebitda_y", "NF", 1), ("adv", "ALL", -1),
       ("gap", "ALL", -1), ("react", "ALL", 1)]

# ---------------------------------------------------------------- fundamentals PIT
FC = ["ticker", "time", "quarter", "ID_Release", "Release_Date", "NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4", "NP_P5", "NP_P6", "NP_P7",
      "Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3", "Revenue_YoY_P0", "GPM_P0", "GPM_P4", "ROA_P0", "ROA_P4", "ROE_Trailing",
      "CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3", "totalAsset_P0", "Debt_Eq_P0", "StDebt_P0", "LtDebt_P0", "Cash_P0", "EBITDA_P0",
      "Inventory_P0", "AR_P0", "OShares", "Dividend_1Y", "Dividend_3Y", "Dividend_Min3Y"]
fin = pd.read_parquet(f"{CACHE}/ticker_financial.parquet", columns=FC)
fin["time"] = pd.to_datetime(fin.time)
rel = pd.to_datetime(fin.Release_Date)
fin["eff"] = np.where(rel.notna(), np.maximum(fin.time, rel), fin.time + pd.Timedelta(days=11)).astype("datetime64[ns]")
fin["qn"] = fin.quarter.str[:4].astype(int) * 4 + fin.quarter.str[-1].astype(int)
fin = fin.sort_values(["eff", "ID_Release"]).drop_duplicates(["ticker", "eff"], keep="last")

L0 = pd.read_csv(LEDGERS[""], low_memory=False, usecols=["record_type", "ymd", "state"])
D0 = L0[L0.record_type == "DAILY"].copy(); D0["ymd"] = pd.to_datetime(D0.ymd)
cal = pd.DatetimeIndex(D0.ymd.sort_values().unique())
state_at = D0.drop_duplicates("ymd").set_index("ymd").state


def load_pos(tag):
    p = pd.read_csv(f"{PREV}/positions{tag}.csv", parse_dates=["entry_date", "exit_date", "signal_date"])
    return p


def build(pos, daily, closes):
    pos = pos.sort_values("signal_date").copy()
    pos["signal_date"] = pos.signal_date.astype("datetime64[ns]")
    x = pd.merge_asof(pos, fin.sort_values("eff"), left_on="signal_date", right_on="eff", by="ticker", direction="backward")
    # dòng 4 quý trước, cũng phải đã hiệu lực ≤ signal
    prev = fin[["ticker", "qn", "eff", "Dividend_1Y"]].rename(columns={"eff": "eff4", "Dividend_1Y": "div1y_4"})
    prev = prev.sort_values("eff4").drop_duplicates(["ticker", "qn"], keep="first")
    x["qn4"] = x.qn - 4
    x = x.merge(prev, left_on=["ticker", "qn4"], right_on=["ticker", "qn"], how="left", suffixes=("", "_p"))
    x.loc[~(x.eff4 <= x.signal_date), "div1y_4"] = np.nan
    x = x.sort_values("signal_date")
    x = pd.merge_asof(x, daily.rename(columns={"time": "px_date"}), left_on="signal_date", right_on="px_date", by="ticker", direction="backward")
    np_ttm = x[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(1, min_count=4)
    np_8 = x[[f"NP_P{i}" for i in range(8)]].sum(1, min_count=8)
    rev = x[["Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3"]].sum(1, min_count=4)
    cfo = x[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(1, min_count=4)
    pos_ = lambda s: s.where(s > 0)
    inv = lambda s: np.where(s > 0, 1 / s, np.where(s.notna(), 0.0, np.nan))
    f = pd.DataFrame(index=x.index)
    f["payout1Y"] = x.Dividend_1Y * x.OShares / pos_(np_ttm)
    f["payout3Y"] = (x.Dividend_3Y / 3) * x.OShares / pos_(np_8 / 2)
    f["DY"] = x.Dividend_1Y / x.Price
    f["div3y"] = np.where(x.Dividend_Min3Y.notna(), (x.Dividend_Min3Y > 0).astype(float), np.nan)
    f["div_chg"] = x.Dividend_1Y / pos_(x.div1y_4) - 1
    f["cfo_np"] = cfo / pos_(np_ttm)
    f["accrual"] = (np_ttm - cfo) / pos_(x.totalAsset_P0)
    f["gpm"] = x.GPM_P0
    f["d_gpm"] = x.GPM_P0 - x.GPM_P4
    f["roe"] = x.ROE_Trailing
    f["d_roa"] = x.ROA_P0 - x.ROA_P4
    f["de"] = x.Debt_Eq_P0
    f["nd_ebitda"] = (x.StDebt_P0 + x.LtDebt_P0 - x.Cash_P0) / pos_(4 * x.EBITDA_P0)
    f["inv_rev"] = x.Inventory_P0 / pos_(rev)
    f["ar_rev"] = x.AR_P0 / pos_(rev)
    f["rev_yoy"] = x.Revenue_YoY_P0
    f["np_yoy"] = x.NP_P0 / pos_(x.NP_P4) - 1
    f["np_accel"] = x.NP_P0 / pos_(x.NP_P4) - x.NP_P1 / pos_(x.NP_P5)
    f["ey"], f["by"], f["cfy"], f["ebitda_y"] = inv(x.PE), inv(x.PB), inv(x.PCF), inv(x.EVEB)
    f["adv"] = np.log(pos_(x.Volume_3M_P50 * x.Price))
    s0 = cal.searchsorted(x.eff.values)  # phiên đầu tiên ≥ ngày hiệu lực
    ie = cal.searchsorted(x.entry_date.values)
    f["gap"] = np.where(x.eff.notna(), ie - s0, np.nan)
    rc = []
    for tk, s, sig in zip(x.ticker, s0, x.signal_date):
        if s < 1 or s + 1 >= len(cal) or cal[s + 1] > sig or tk not in closes:
            rc.append(np.nan); continue
        c = closes[tk]
        a, b = c.asof(cal[s - 1]), c.asof(cal[s + 1])
        rc.append(b / a - 1 if a and a > 0 else np.nan)
    f["react"] = rc
    icb = x.ICB_Code // 100
    x["G"] = np.select([icb == 83, icb.isin([85, 87]), icb == 86, icb.notna()], ["BANK", "FINO", "RE", "NONFIN"], "NA")
    x["state"] = [state_at.get(d, np.nan) for d in x.signal_date]
    x["season"] = x.quarter.str[-2:]
    keep = ["holding_id", "book", "ticker", "entry_date", "exit_date", "signal_date", "ret", "pnl", "contrib_bp", "abandoned", "mtm", "n_sell",
            "year", "ym", "G", "ICB_Code", "quarter", "eff", "state", "season", "PE"]
    return pd.concat([x[keep], f], axis=1).sort_values(["book", "entry_date", "holding_id"]).reset_index(drop=True)


tks = set(pd.read_csv(f"{PREV}/positions.csv").ticker) | set(pd.read_csv(f"{PREV}/positions_pin1M.csv").ticker)
raw = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close", "Price", "PE", "PB", "PCF", "EVEB", "Volume_3M_P50", "ICB_Code"])
                 for f in sorted(glob.glob(f"{CACHE}/ticker/*.parquet"))])
raw = raw[raw.ticker.isin(tks)]
raw["time"] = pd.to_datetime(raw.time).astype("datetime64[ns]")
raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
closes = {tk: g.set_index("time").Close.astype(float) for tk, g in raw.groupby("ticker")}
daily = raw.drop(columns="Close").sort_values("time")


# ---------------------------------------------------------------- stats
def month_arr(df, cols):
    g = df.groupby("ym")
    return np.array([g[c].sum().values for c in cols]).T


def boot_idx(M):
    return np.random.default_rng(SEED).integers(0, M, (B, M))


def pval(ds):
    ds = ds[~np.isnan(ds)]
    return max(2 * min((ds <= 0).mean(), (ds >= 0).mean()), 1 / B)


def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)
    q = np.empty(n); q[o] = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.minimum(q, 1)


def prep(sub, name, scope):
    s = sub[sub[name].notna()].copy()
    if scope == "NF":
        s = s[s.G == "NONFIN"]
    else:
        s = s[s.G != "NA"]
    if name == "div3y":
        s["pr"] = s[name]
        s["T"] = np.where(s[name] > 0, 3, 1)
    else:
        s["pr"] = s.groupby("G")[name].rank(pct=True)
        s["T"] = np.where(s.pr <= 1 / 3, 1, np.where(s.pr <= 2 / 3, 2, 3))
    return s


def dterc(s):
    return s.loc[s["T"] == 3, "ret"].mean() - s.loc[s["T"] == 1, "ret"].mean()


def stats(sub, name, scope, do_boot=True):
    s = prep(sub, name, scope)
    r = {"N": len(s), "Nm": s.ym.nunique(), "N_T1": int((s["T"] == 1).sum()), "N_T3": int((s["T"] == 3).sum()),
         "ret_T1": s.loc[s["T"] == 1, "ret"].mean(), "ret_T2": s.loc[s["T"] == 2, "ret"].mean(), "ret_T3": s.loc[s["T"] == 3, "ret"].mean()}
    r["d"] = dterc(s)
    for nm, m in [("IS", s.year <= IS_END), ("OOS", s.year > IS_END)]:
        r[f"d_{nm}"], r[f"N_{nm}"] = dterc(s[m]), int(m.sum())
    r["d_no2021"] = dterc(s[s.year != 2021])
    cut = s.ret.quantile(0.98)
    r["d_trim2"] = dterc(s[s.ret <= cut])
    s["ry"] = s.ret.rank()
    r["rho"] = s[["pr", "ry"]].corr().iloc[0, 1]
    if not do_boot:
        return r, s
    s["t3"], s["t1"] = (s["T"] == 3).astype(float), (s["T"] == 1).astype(float)
    s["rt3"], s["rt1"] = s.ret * s.t3, s.ret * s.t1
    s["one"], s["xy"], s["xx"], s["yy"] = 1.0, s.pr * s.ry, s.pr ** 2, s.ry ** 2
    A = month_arr(s, ["rt3", "t3", "rt1", "t1", "one", "pr", "ry", "xy", "xx", "yy"])
    idx = boot_idx(len(A)); S = A[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        dd = S[:, 0] / S[:, 1] - S[:, 2] / S[:, 3]
        n, sx, sy, sxy, sxx, syy = S[:, 4], S[:, 5], S[:, 6], S[:, 7], S[:, 8], S[:, 9]
        rr = (n * sxy - sx * sy) / np.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
    r["p_d"], r["p_rho"] = pval(dd), pval(rr)
    r["ci_lo"], r["ci_hi"] = np.nanpercentile(dd, [2.5, 97.5])
    # kiểm soát value: ret ~ 1 + pr + pr_ey  (pr_ey = phân vị ey trong G, cùng mẫu)
    if name != "ey":
        e = s["ey_pr"].values
        ok = ~np.isnan(e)
        t = s[ok].copy()
        X = np.column_stack([np.ones(len(t)), t.pr, t.ey_pr]); y = t.ret.values
        r["b_x_ctrl_ey"] = np.linalg.lstsq(X, y, rcond=None)[0][1]
        ms = t.ym.values; um, inv_ = np.unique(ms, return_inverse=True)
        XX = np.zeros((len(um), 3, 3)); XY = np.zeros((len(um), 3))
        np.add.at(XX, inv_, np.einsum("ni,nj->nij", X, X)); np.add.at(XY, inv_, X * y[:, None])
        ib = boot_idx(len(um)); bx = []
        for row in ib:
            try:
                bx.append(np.linalg.solve(XX[row].sum(0), XY[row].sum(0))[1])
            except np.linalg.LinAlgError:
                bx.append(np.nan)
        r["p_ctrl_ey"] = pval(np.array(bx))
        r["rho_with_ey"] = t[["pr", "ey_pr"]].corr(method="spearman").iloc[0, 1]
    return r, s


def run(F):
    main = F[~F.abandoned & ~F.mtm & (F.n_sell > 0)].copy()
    main["ey_pr"] = np.nan
    for bk in BOOKS:
        m = (main.book == bk) & (main.G != "NA")
        main.loc[m, "ey_pr"] = main[m].groupby("G").ey.rank(pct=True)
    rows, terts, loos = [], [], []
    for bk in BOOKS:
        sub = main[main.book == bk]
        for name, scope, sgn in IND:
            r, s = stats(sub, name, scope)
            r.update({"book": bk, "ind": name, "scope": scope, "exp": sgn})
            rows.append(r)
            for T in [1, 2, 3]:
                st = s[s["T"] == T]
                terts.append({"book": bk, "ind": name, "T": T, "N": len(st), "Nm": st.ym.nunique(), "ret_mean": st.ret.mean(),
                              "ret_med": st.ret.median(), "x_min": st[name].min(), "x_med": st[name].median(), "x_max": st[name].max(),
                              "ret_IS": st[st.year <= IS_END].ret.mean(), "ret_OOS": st[st.year > IS_END].ret.mean()})
            for yv in sorted(s.year.unique()):
                loos.append({"book": bk, "ind": name, "drop_year": yv, "d": dterc(s[s.year != yv])})
    return main, pd.DataFrame(rows), pd.DataFrame(terts), pd.DataFrame(loos)


feats, res = {}, {}
for tag in LEDGERS:
    F = build(load_pos(tag), daily, closes)
    F.to_csv(f"{OUT}/features{tag}.csv", index=False, float_format="%.10g")
    feats[tag] = F
    res[tag] = run(F)

main, R, T, LOO = res[""]
R1 = res["_pin1M"][1]
R["q_d"] = bh(np.r_[R.p_d, R.p_rho])[:len(R)]
R["q_rho"] = bh(np.r_[R.p_d, R.p_rho])[len(R):]
R = R.merge(R1[["book", "ind", "d", "N"]].rename(columns={"d": "d_pin1M", "N": "N_pin1M"}), on=["book", "ind"])
lo = LOO.groupby(["book", "ind"]).d.agg(loo_min="min", loo_max="max").reset_index()
R = R.merge(lo, on=["book", "ind"])
e = R.exp
R["thieu_mau"] = (R.N_T1 < NMIN / 3) | (R.N_T3 < NMIN / 3) | (R.N < NMIN)
R["pass"] = ((np.sign(R.d) == e) & (R.d.abs() >= MINPP) & (np.sign(R.d_IS) == e) & (np.sign(R.d_OOS) == e)
             & (R.q_d < 0.10) & (np.sign(R.rho) == e) & (np.sign(R.d_no2021) == e) & (np.sign(R.d_trim2) == e)
             & (np.sign(R.d_pin1M) == e) & (R.d_pin1M.abs() >= MINPP) & ~R.thieu_mau)
cols = ["book", "ind", "scope", "exp", "N", "Nm", "N_T1", "N_T3", "ret_T1", "ret_T3", "d", "d_IS", "N_IS", "d_OOS", "N_OOS", "rho",
        "p_d", "q_d", "p_rho", "q_rho", "ci_lo", "ci_hi", "d_no2021", "d_trim2", "loo_min", "loo_max", "d_pin1M",
        "b_x_ctrl_ey", "p_ctrl_ey", "rho_with_ey", "thieu_mau", "pass"]
R[cols].to_csv(f"{OUT}/results.csv", index=False, float_format="%.6g")
T.to_csv(f"{OUT}/tertiles.csv", index=False, float_format="%.6g")
LOO.to_csv(f"{OUT}/loo.csv", index=False, float_format="%.6g")

# tương quan giữa các chỉ báo (phân vị trong G) theo book
cr = []
for bk in BOOKS:
    sub = main[main.book == bk]
    P = pd.DataFrame({n: prep(sub, n, sc).pr for n, sc, _ in IND})
    c = P.corr(method="spearman", min_periods=60)
    c.insert(0, "ind", c.index); c.insert(0, "book", bk)
    cr.append(c)
pd.concat(cr).to_csv(f"{OUT}/corr.csv", index=False, float_format="%.3f")

# mô tả: state engine, mùa vụ, nhóm ngành
dsc = []
for bk in BOOKS:
    sub = main[main.book == bk]
    for k in ["state", "season", "G"]:
        for v, g in sub.groupby(k):
            dsc.append({"book": bk, "var": k, "val": v, "N": len(g), "Nm": g.ym.nunique(), "ret_mean": g.ret.mean(), "ret_med": g.ret.median()})
pd.DataFrame(dsc).to_csv(f"{OUT}/describe.csv", index=False, float_format="%.6g")

# ---------------------------------------------------------------- selfcheck
lines = []
for tag, path in LEDGERS.items():
    L = pd.read_csv(path, low_memory=False, usecols=["record_type", "book", "action", "buy_amount", "sell_amount", "fee"])
    tx = L[(L.record_type == "TX") & L.book.isin(BOOKS)]
    for bk in BOOKS:
        t = tx[tx.book == bk]
        b = t.action == "buy"
        cash = (t.sell_amount[~b] - t.fee[~b]).sum() - (t.buy_amount[b] + t.fee[b]).sum()
        lines.append(f"[{tag or 'pin0'}] {bk}: sum pnl positions={feats[tag][feats[tag].book == bk].pnl.sum():.4f} ; TX cash={cash:.4f}")
for tag in LEDGERS:
    m = feats[tag]; mm = m[~m.abandoned & ~m.mtm & (m.n_sell > 0)]
    lines.append(f"[{tag or 'pin0'}] main N LAG={int((mm.book == 'LAG').sum())} BAL={int((mm.book == 'BAL').sum())} ; G counts={mm.G.value_counts().to_dict()}")
    lines.append(f"[{tag or 'pin0'}] fin row missing={int(mm.eff.isna().sum())} ; eff>signal (PIT viol)={int((pd.to_datetime(mm.eff) > mm.signal_date).sum())}")
open(f"{OUT}/selfcheck.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
pd.set_option("display.width", 300)
print(R[["book", "ind", "exp", "N", "Nm", "ret_T1", "ret_T3", "d", "d_IS", "d_OOS", "rho", "p_d", "q_d", "d_no2021", "d_trim2", "d_pin1M", "b_x_ctrl_ey", "p_ctrl_ey", "pass"]].to_string())
