"""Trade-subtraction approximator for the BAL monthly gate (placebo engine) — job Taylor_20261110_053025.

gated_BAL_nav(t) ~= blind_BAL_nav(t) - sum_{holdings h whose FIRST buy falls on a blocked session} cumPnL_h(t)
cumPnL_h(t) = shares_h(t)*Close(t) + cumulative cash flows of h (sells - buys - fees).
Ignores: freed cash/slots re-used by other entries (that is the approximation error, measured vs the full
engine on the real variants) and carry on freed cash (pin0% = 0).
Combined NAV: daily r_c = w_bal(t-1) r_bal + (1-w_bal(t-1)) r_lag with BLIND allocator weights.

Self-check: removing nothing must reproduce blind nav_bal_ref (reconstruction residual reported).
"""
import os, sys, json
import numpy as np, pandas as pd, duckdb

WC = "/home/trido/thanhdt/WorkingClaude"
LEDGER = WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp_p0_off_univpit.csv"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = HERE + "/approx_cache.pkl"


def load(ledger=LEDGER, book="BAL"):
    d = pd.read_csv(ledger, low_memory=False)
    daily = d[d.record_type == "DAILY"].copy()
    daily["ymd"] = pd.to_datetime(daily["ymd"])
    daily = daily.sort_values("ymd").set_index("ymd")
    tx = d[(d.record_type == "TX") & (d.book == book)].copy()
    tx["ymd"] = pd.to_datetime(tx["ymd"])
    tx = tx[~tx["ticker"].astype(str).str.startswith("CUSTOM")]   # park ETF (0 at park0) excluded
    tks = sorted(tx["ticker"].unique())
    con = duckdb.connect()
    px = con.execute(f"""SELECT time, ticker, Close FROM read_parquet('{WC}/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
                         WHERE ticker IN ({','.join("'"+t+"'" for t in tks)}) AND time >= '2013-12-01'""").df()
    px["time"] = pd.to_datetime(px["time"])
    P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").reindex(daily.index).ffill()
    dates = daily.index
    # per-holding cumulative P&L matrix (dates x holdings)
    hold = {}
    for hid, g in tx.groupby("holding_id"):
        tk = g["ticker"].iloc[0]
        sh = g.assign(s=np.where(g.action == "buy", g.shares, -g.shares)).groupby("ymd")["s"].sum()
        cf = g.assign(c=g.sell_amount.fillna(0) - g.buy_amount.fillna(0) - g.fee.fillna(0)).groupby("ymd")["c"].sum()
        sh = sh.reindex(dates).fillna(0).cumsum().clip(lower=0)
        cf = cf.reindex(dates).fillna(0).cumsum()
        pnl = sh * P[tk].fillna(0) + cf
        first = g.loc[g.action == "buy", "ymd"].min()
        hold[hid] = (first, g["play_type"].iloc[0], pnl.values)
    hids = list(hold)
    M = np.column_stack([hold[h][2] for h in hids])
    first = pd.Series([hold[h][0] for h in hids], index=hids)
    ptype = pd.Series([hold[h][1] for h in hids], index=hids)
    return daily, M, first, ptype


def get():
    if os.path.exists(CACHE):
        return pd.read_pickle(CACHE)
    obj = load()
    pd.to_pickle(obj, CACHE)
    return obj


def metrics(nav, dates):
    nav = pd.Series(np.asarray(nav, float), index=dates)
    yrs = (dates[-1] - dates[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(len(r) / yrs)  # Sharpe lịch (n_returns/yrs)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr, sharpe=sh, maxdd=dd, calmar=cagr / -dd if dd < 0 else np.nan)


def gated(daily, M, first, ptype, block_dates, exempt_capit=False):
    bset = set(pd.to_datetime(block_dates))
    rm = first.isin(bset).values
    if exempt_capit:
        rm &= ~ptype.astype(str).str.startswith("CAPIT").values
    bal = daily["nav_bal_ref"].values - (M[:, rm].sum(axis=1) if rm.any() else 0)
    return bal, int(rm.sum())


def combine(daily, bal):
    rb = np.r_[0, bal[1:] / bal[:-1] - 1]
    lag = daily["nav_lag_ref"].values
    rl = np.r_[0, lag[1:] / lag[:-1] - 1]
    cb = daily["cap_bal"].values; cn = daily["combined_nav"].values
    w = np.r_[cb[0] / cn[0], (cb / cn)[:-1]]
    rc = w * rb + (1 - w) * rl
    return cn[0] * np.cumprod(1 + rc)


if __name__ == "__main__":
    daily, M, first, ptype = get()
    blind_rec = daily["nav_bal_ref"].iloc[0] + M.sum(axis=1)
    res = daily["nav_bal_ref"].values - blind_rec
    print(f"holdings={M.shape[1]} | reconstruction residual blind BAL: max|.|={np.abs(res).max()/1e9:.4f}B "
          f"final={res[-1]/1e9:.4f}B (of {daily['nav_bal_ref'].iloc[-1]/1e9:.2f}B)")
    comb0 = combine(daily, daily["nav_bal_ref"].values)
    print("combined-approx(blind) vs ledger: final", comb0[-1] / 1e9, daily["combined_nav"].iloc[-1] / 1e9)
    print("blind BAL", metrics(daily["nav_bal_ref"].values, daily.index))
    print("blind combined ledger", metrics(daily["combined_nav"].values, daily.index))
