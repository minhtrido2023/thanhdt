#!/usr/bin/env python3
"""Top-5-post-earnings sleeve — full-universe walk-forward PIT backtest.

Spec (frozen before any result was read):
  season s        = fiscal quarter; rebalance date D_s = first trading day >= q_end + 40 calendar days
                    (fixed rule; covers the p90 of Release_Date in EVERY season 2014Q1-2026Q2).
  signal          = formed on D_s close.
  execution       = close of the NEXT trading day (D_s+1). No look-ahead.
  pool at D_s     = universe_pit.in_universe
                    AND has a tav2_bq.ticker row at D_s
                    AND ticker not in BANNED
                    AND has released its report for season s by D_s
                    AND golden floor: ROE_Min3Y >= 0 AND CF_OA_3Y > 0 (missing = FAIL)
                    AND rating_asof(fa_ratings_8l, D_s) <= 3   (+ forensic-exclude overlay)
  value_score     = coverage-aware mean of within-pool percentile ranks of
                    ey = 1/PE, cfy = 1/PCF, ps = 1/PS.
                    A non-positive denominator earns pct 0 (no reward), NOT a neutral 0.5
                    (matches rating_8l.py's documented ey semantics). Missing = abstain.
  portfolio       = Top-5 by value_score, equal weight, held to the next rebalance.
  costs           = 0.1% per side on traded notional (CLAUDE.md convention).

Everything is point-in-time: PE/PCF come from tav2_bq.ticker at D_s (verified to step exactly on
Release_Date, raw-`Price` basis); PS is carried from its release-date value to D_s by the
price ratio PS_d = PS_rel * Price_d / Price_rel (validated against the PE control: 98.6% of
39,224 ticker-dates reproduce the stored daily PE to machine precision).
"""
import os, sys, json, bisect
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
W = "/home/trido/thanhdt/WorkingClaude"
DATA, OUT = os.path.join(HERE, "data"), os.path.join(HERE, "out")
CAPITAL = 1_000_000_000.0     # 1 tỷ, same as the fleet's NAV convention
TC = 0.001                    # 0.1% per side

BANNED = {"PC1","VVS","KSF","NKG","HSG","HVN","VJC","NVL","GEG","SBA",
          "DMC","IMP","TRA","TOS","VTP"}


# ------------------------------------------------------------------ data
def load():
    d = {}
    for k in ["px","fund","fin","universe_pit","ratings8l","dt5g","calendar"]:
        d[k] = pd.read_parquet(os.path.join(DATA, k + ".parquet"))
    for k, c in [("px","time"),("fund","time"),("fin","release_date"),
                 ("universe_pit","time"),("ratings8l","time"),("dt5g","time"),("calendar","time")]:
        d[k][c] = pd.to_datetime(d[k][c])
    d["seasons"] = pd.read_csv(os.path.join(DATA, "seasons.csv"))
    d["fin_rel"] = pd.read_parquet(os.path.join(DATA, "fin_rel.parquet"))
    d["fin_rel"]["release_date"] = pd.to_datetime(d["fin_rel"]["release_date"])
    return d


def rating_asof_map(rat):
    """Production idiom, copied from custom_basket.py: bisect on fa_ratings_8l + forensic overlay."""
    rat = rat.sort_values(["ticker","time"])
    by = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}
    forx = {}
    try:
        ff = pd.read_csv(os.path.join(W, "data", "forensic_flags.csv"))
        forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in ff.iterrows()
                if str(r["severity"]).strip() == "exclude"}
    except Exception as e:
        print(f"  [forensic] none ({e})")
    print(f"  [forensic exclude] {len(forx)} names: "
          f"{ {k: str(v.date()) for k, v in forx.items()} }")

    def f(tk, d):
        fd = forx.get(tk)
        if fd is not None and pd.Timestamp(d) >= fd:
            return 5.0
        e = by.get(tk)
        if not e:
            return np.nan
        i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
        return float(e[1][i]) if i >= 0 else np.nan
    return f


def pct_lens(x):
    """Within-pool percentile of a yield lens. NaN abstains; non-positive denominator -> 0.0."""
    v = pd.Series(np.where(x > 0, 1.0 / x, np.nan), index=x.index)
    p = v.rank(pct=True)
    p = p.where(~((x <= 0) & x.notna()), 0.0)   # present but non-positive -> no reward
    return p


# ------------------------------------------------------------------ selection
def build_selection(d, n_top=5, lenses=("ey","cfy","ps"), require_reported=True):
    px, fund, fin = d["px"], d["fund"], d["fin"]
    uni, cal = d["universe_pit"], d["calendar"]["time"].sort_values().reset_index(drop=True)
    rat_f = rating_asof_map(d["ratings8l"])

    # price at each release date, for carrying PS forward
    pr = px.merge(fin[["ticker","release_date"]].drop_duplicates(),
                  left_on=["ticker","time"], right_on=["ticker","release_date"])
    pr = pr[["ticker","release_date","Price"]].rename(columns={"Price":"Price_rel"})
    finp = fin.merge(pr, on=["ticker","release_date"], how="left").sort_values("release_date")

    # release calendar: has this ticker published season s by D_s?
    rel = d["fin_rel"][["ticker","quarter","release_date"]].dropna()

    uni_by_date = {t: set(g["ticker"]) for t, g in uni.groupby("time")}
    seasons = d["seasons"]
    recs, pools = [], []
    for _, s in seasons.iterrows():
        D = pd.Timestamp(s["rebal"])
        f = fund[fund["time"] == D].copy()
        if f.empty:
            continue
        f = f[f["ticker"].isin(uni_by_date.get(D, set()))]
        f = f[~f["ticker"].isin(BANNED)]
        # PIT fundamentals as-of D (release-date keyed)
        f = f.sort_values("time")
        f = pd.merge_asof(f, finp, left_on="time", right_on="release_date",
                          by="ticker", direction="backward")
        if require_reported:
            r = rel[rel["quarter"] == s["season"]]
            ok = set(r.loc[r["release_date"] <= D, "ticker"])
            f = f[f["ticker"].isin(ok)]
        # golden floor (missing = fail)
        f = f[(f["ROE_Min3Y"] >= 0) & (f["CF_OA_3Y"] > 0)]
        # 8L rating gate
        f["rating"] = [rat_f(t, D) for t in f["ticker"]]
        f = f[f["rating"] <= 3]
        if f.empty:
            continue
        # value lenses, PIT
        f["PS"] = f["PS_rel"] * f["Price"] / f["Price_rel"]
        f["ey_p"]  = pct_lens(f["PE"])
        f["cfy_p"] = pct_lens(f["PCF"])
        f["ps_p"]  = pct_lens(f["PS"])
        cols = {"ey":"ey_p","cfy":"cfy_p","ps":"ps_p"}
        use = [cols[l] for l in lenses]
        f["value_score"] = f[use].mean(axis=1, skipna=True)
        f = f.dropna(subset=["value_score"])
        f = f.sort_values(["value_score","ticker"], ascending=[False, True])
        f["rank"] = np.arange(1, len(f) + 1)
        f["season"] = s["season"]; f["rebal"] = D; f["pool_n"] = len(f)
        pools.append(f[["season","rebal","ticker","ICB_Code","rating","PE","PCF","PS",
                        "ey_p","cfy_p","ps_p","value_score","rank","pool_n"]])
        recs.append(f.head(n_top).assign(season=s["season"], rebal=D))
    sel = pd.concat(recs, ignore_index=True)
    pool = pd.concat(pools, ignore_index=True)
    return sel, pool


# ------------------------------------------------------------------ prices
def price_frame(px):
    p = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last")
    return p.sort_index()


def next_td(cal, d, k=1):
    i = cal.searchsorted(pd.Timestamp(d), side="left")
    j = i + k
    return cal[j] if 0 <= j < len(cal) else None


# ------------------------------------------------------------------ NAV engine (VND book)
def simulate(sel, P, cal, seasons, capital=CAPITAL, tc=TC):
    """Single-thread VND book. Buy/sell at the close of the trading day AFTER the signal date.
    Returns (nav daily series, trade log, identity check dict)."""
    rebals = [pd.Timestamp(x) for x in seasons["rebal"]]
    execs = [next_td(cal, r, 1) for r in rebals]
    pairs = [(s, e) for s, e in zip(seasons["season"], execs) if e is not None]
    cash, shares = capital, {}
    fees_total = 0.0
    nav_rows, trades = [], []
    exec_dates = {e: s for s, e in pairs}
    start = pairs[0][1]
    days = cal[(cal >= start)]
    last_px = {}
    for d in days:
        row = P.loc[d] if d in P.index else None
        if row is not None:
            for t in list(shares) + list(last_px):
                v = row.get(t, np.nan)
                if pd.notna(v):
                    last_px[t] = float(v)
        if d in exec_dates:
            season = exec_dates[d]
            tgt = sel[sel["season"] == season]["ticker"].tolist()
            # mark to market with prices available at d
            for t in set(list(shares) + tgt):
                v = P.at[d, t] if (d in P.index and t in P.columns) else np.nan
                if pd.notna(v):
                    last_px[t] = float(v)
            nav = cash + sum(sh * last_px.get(t, 0.0) for t, sh in shares.items())
            tgt = [t for t in tgt if last_px.get(t)]           # need a price to trade
            w = (nav / len(tgt)) if tgt else 0.0
            new_sh = {t: w / last_px[t] for t in tgt}
            for t in set(list(shares) + list(new_sh)):
                d_sh = new_sh.get(t, 0.0) - shares.get(t, 0.0)
                if abs(d_sh) < 1e-12:
                    continue
                px_t = last_px[t]
                notional = d_sh * px_t
                fee = abs(notional) * tc
                cash -= notional + fee
                fees_total += fee
                trades.append({"date": d, "season": season, "ticker": t,
                               "d_shares": d_sh, "price": px_t, "notional": notional, "fee": fee})
            shares = {t: s for t, s in new_sh.items() if abs(s) > 1e-12}
        mkt = sum(sh * last_px.get(t, 0.0) for t, sh in shares.items())
        nav_rows.append({"time": d, "nav": cash + mkt, "cash": cash, "mkt": mkt})
    nav = pd.DataFrame(nav_rows).set_index("time")["nav"]
    tr = pd.DataFrame(trades)
    # identity: cash = capital - sum(notional) - sum(fee)
    cash_id = capital - tr["notional"].sum() - tr["fee"].sum() - cash
    mkt_end = sum(sh * last_px.get(t, 0.0) for t, sh in shares.items())
    nav_id = (cash + mkt_end) - nav.iloc[-1]
    return nav, tr, {"cash_identity_err_vnd": float(cash_id),
                     "nav_identity_err_vnd": float(nav_id),
                     "fees_total_vnd": float(fees_total),
                     "turnover_notional_vnd": float(tr["notional"].abs().sum())}


def metrics(nav, freq=252):
    r = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    sd = r.std(ddof=1) * np.sqrt(freq)
    dn = r[r < 0].std(ddof=1) * np.sqrt(freq)
    sharpe = (r.mean() * freq) / sd if sd > 0 else np.nan
    sortino = (r.mean() * freq) / dn if dn and dn > 0 else np.nan
    dd = nav / nav.cummax() - 1
    mdd = dd.min()
    return {"years": round(yrs, 2), "final_nav_vnd": float(nav.iloc[-1]),
            "CAGR": float(cagr), "Sharpe": float(sharpe), "Sortino": float(sortino),
            "MaxDD": float(mdd), "Calmar": float(cagr / abs(mdd)) if mdd < 0 else np.nan,
            "vol_ann": float(sd)}


# ------------------------------------------------------------------ event-level returns
def fwd_ret(P, cal, t, d0, d1):
    """Total return of t between two trading dates. P MUST be the forward-filled close matrix,
    so a halted/late-listed name carries its last known close instead of vanishing."""
    if t not in P.columns:
        return np.nan
    try:
        a, b = P.at[d0, t], P.at[d1, t]
    except KeyError:
        return np.nan
    if not (np.isfinite(a) and np.isfinite(b)) or a <= 0:
        return np.nan
    return b / a - 1


def season_events(sel, pool, d, P, n_top=5):
    """Per-season event table: sleeve return, VNINDEX benchmark, ICB sector benchmark,
    at 3 horizons (to next rebalance, +21td, +63td)."""
    cal = d["calendar"]["time"].sort_values().reset_index(drop=True)
    seasons = d["seasons"].copy()
    seasons["exec"] = [next_td(cal, r, 1) for r in seasons["rebal"]]
    uni = d["universe_pit"]
    uni_by_date = {t: set(g["ticker"]) for t, g in uni.groupby("time")}
    icb = d["fund"][["ticker","time","ICB_Code"]]
    icb_by_date = {t: dict(zip(g["ticker"], g["ICB_Code"])) for t, g in icb.groupby("time")}

    rows = []
    for i, s in seasons.iterrows():
        e0 = s["exec"]
        if e0 is None:
            continue
        nxt = seasons["exec"].iloc[i + 1] if i + 1 < len(seasons) else None
        horizons = {"to_next": nxt,
                    "h21": next_td(cal, e0, 21),
                    "h63": next_td(cal, e0, 63)}
        names = sel[sel["season"] == s["season"]]["ticker"].tolist()
        if not names:
            continue
        D = pd.Timestamp(s["rebal"])
        icb_map = icb_by_date.get(D, {})
        univ = uni_by_date.get(D, set())
        for hname, e1 in horizons.items():
            if e1 is None or e1 > P.index.max():
                continue
            rs = [fwd_ret(P, cal, t, e0, e1) for t in names]
            rs = [x for x in rs if np.isfinite(x)]
            if not rs:
                continue
            sleeve = float(np.mean(rs))
            vni = fwd_ret(P, cal, "VNINDEX", e0, e1)
            # sector benchmark: EW of same-ICB in_universe peers, excluding the held name
            sect = []
            for t in names:
                c = icb_map.get(t)
                if c is None or not np.isfinite(c):
                    continue
                peers = [u for u in univ if icb_map.get(u) == c and u != t and u not in BANNED]
                pr = [fwd_ret(P, cal, u, e0, e1) for u in peers]
                pr = [x for x in pr if np.isfinite(x)]
                if len(pr) >= 3:
                    sect.append(float(np.mean(pr)))
            sec = float(np.mean(sect)) if sect else np.nan
            rows.append({"season": s["season"], "rebal": D, "exec": e0, "horizon": hname,
                         "end": e1, "n_names": len(rs), "sleeve_ret": sleeve,
                         "vni_ret": vni, "sector_ret": sec,
                         "exc_vni": sleeve - vni if np.isfinite(vni) else np.nan,
                         "exc_sector": sleeve - sec if np.isfinite(sec) else np.nan,
                         "pool_n": int(pool[pool["season"] == s["season"]]["pool_n"].iloc[0])})
    return pd.DataFrame(rows)


def regimes(d, ev):
    dt = d["dt5g"].sort_values("time")
    NAME = {0:"CRISIS",1:"BEAR",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}
    sys.path.insert(0, W)
    import value_radar as vr
    vrs = vr.load_series(update=False)[["time","score","label"]].sort_values("time")
    e = ev.sort_values("rebal")
    e = pd.merge_asof(e, dt, left_on="rebal", right_on="time", direction="backward")
    e = pd.merge_asof(e, vrs, left_on="rebal", right_on="time", direction="backward",
                      suffixes=("","_vr"))
    return e


def stats_block(x):
    x = np.asarray([v for v in x if np.isfinite(v)], dtype=float)
    n = len(x)
    if n == 0:
        return {"n":0}
    m, sd = x.mean(), x.std(ddof=1) if n > 1 else np.nan
    t = m / (sd / np.sqrt(n)) if n > 1 and sd > 0 else np.nan
    rng = np.random.default_rng(20260818)
    bs = rng.choice(x, size=(10000, n), replace=True).mean(axis=1)
    return {"n": n, "mean": float(m), "median": float(np.median(x)),
            "win_rate": float((x > 0).mean()), "t": float(t) if np.isfinite(t) else None,
            "ci5": float(np.percentile(bs, 5)), "ci95": float(np.percentile(bs, 95))}
