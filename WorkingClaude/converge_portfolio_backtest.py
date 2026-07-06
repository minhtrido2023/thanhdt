# -*- coding: utf-8 -*-
"""converge_portfolio_backtest.py — walk-forward backtest of "ConvergePort": a 2-layer paper
portfolio at the intersection of AlphaLens (per-name valuation lens) and Golden/Strong (8L
rating <= 2), i.e. the DOUBLE-CONFIRM set from sector_lens_monitor.py.

Job Taylor_20260706_093329 (dispatch from Mike; user approved direction). RESEARCH ONLY —
touches no production trading file (custom30V / BAL / LAG / rating_8l.py unchanged). If it
launches, it launches as a PAPER book (data/converge_portfolio_paper.json), not real money.

STRATEGY (2-layer, like V2.4):
  LAYER 1 — active "converge" book = names in DOUBLE-CONFIRM at t:
      sector-lens(name, t) == BUY  AND  as-of 8L rating(name, t) <= 2.
    The sector-lens BUY is decided by the EXACT eval_* functions imported from
    sector_lens_monitor (no re-implementation) evaluated point-in-time (price-current PE/PB/EVEB
    from `ticker` that day; fundamentals as-of the latest ticker_financial Release_Date <= t;
    DT5G state as-of t for the securities gate). Weight per name:
      raw_i = 1.5 if buy_mode==STRONG else 1.0 ;  share_i = raw_i / sum(raw)
      w_i   = min(0.20, share_i) ;  active_frac = sum(w_i) ;  parking = 1 - active_frac
    (The 20% cap makes a THIN double-confirm set park more — fewer confirmations = less
    conviction = more mechanical parking. This is my explicit reading of Mike's sketch, which
    left the active/parking split implicit; rule 5 "idle cash parks" requires parking>0 when the
    set is small, and only a per-NAV cap produces that. Documented in the framework doc.)
  LAYER 2 — idle cash parks in custom30V (published basket tav2_bq.custom30v_8l: yieldcombo top-30,
    cap 0.10, quarterly rebal), exactly the V2.4 NEUTRAL parking vehicle.

BASELINE = "custom30V thuần" = 100% parking basket (the thing ConvergePort must not lose to).

WALK-FORWARD: FULL 2014-08 -> now, IS 2014-2019, OOS 2020 -> now. Self-check: daily weights sum
to 1.0 (0 VND leak). Point-in-time throughout (no look-ahead: rating by eff_date, financials by
Release_Date, DT5G/price by t; T+1 execution — weights from t-1 earn return t).
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd
import duckdb

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
CACHE = os.path.join(WORKDIR, "data", "bq_cache")

# import the EXACT live sector-lens evaluators (no rewrite) --------------------------------
import sector_lens_monitor as slm

WL = slm.NAMES                                   # [(ticker, sector, key), ...] — the Group-A watchlist
WL_TK = [n[0] for n in WL]
START = "2014-08-05"                             # custom30V parking basket effective start
IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
CAP = 0.20
STRONG_TILT = 1.5

# financial fields the eval_* fns read from `f` (as-of Release_Date) -----------------------
FIN_COLS = ["PE_MA1Y", "PB_MA1Y", "PE_MA5Y", "ROE5Y", "ROIC5Y", "ROE_Trailing", "ROE3Y",
            "ROE_Min3Y", "IntCov_P0", "CF_OA_3Y", "Debt_Eq_P0", "NP_P0", "NP_P4",
            "GPM_P0", "GPM_P1", "GPM_P2", "GPM_P3", "GPM_P4", "GPM_P5", "GPM_P6", "GPM_P7"]
# price-current multiples the eval_* fns read from `v` (daily ticker row) ------------------
VAL_COLS = ["PE", "PB", "EVEB", "PE_MA5Y"]


def con():
    c = duckdb.connect(":memory:"); c.execute("SET threads=1"); return c


def load_prices(tickers):
    """Wide daily Close panel (date x ticker) for the given names, >= START."""
    c = con()
    q = ",".join(f"'{t}'" for t in sorted(set(tickers)))
    df = c.execute(f"""
        SELECT time, ticker, Close, PE, PB, EVEB, PE_MA5Y
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE ticker IN ({q}) AND time >= '{START}'
        ORDER BY time, ticker""").df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    return df


def load_financials():
    c = con()
    q = ",".join(f"'{t}'" for t in WL_TK)
    cols = ",".join(FIN_COLS)
    df = c.execute(f"""
        SELECT ticker, Release_Date, quarter, {cols}
        FROM read_parquet('{CACHE}/ticker_financial.parquet')
        WHERE ticker IN ({q}) AND Release_Date IS NOT NULL
        ORDER BY ticker, Release_Date""").df()
    c.close()
    df["Release_Date"] = pd.to_datetime(df["Release_Date"])
    return df


def load_dt5g():
    c = con()
    df = c.execute(f"SELECT time, state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') ORDER BY time").df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    return df


def load_ratings():
    r = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l_history.csv"))
    r = r[r["ticker"].isin(WL_TK)][["ticker", "eff_date", "rating"]].copy()
    r["eff_date"] = pd.to_datetime(r["eff_date"])
    return r.sort_values(["ticker", "eff_date"])


def load_parking_basket():
    c = con()
    df = c.execute(f"""
        SELECT rebal_date, ticker, weight FROM read_parquet('{CACHE}/custom30v_8l.parquet')
        ORDER BY rebal_date, ticker""").df()
    c.close()
    df["rebal_date"] = pd.to_datetime(df["rebal_date"])
    return df


# ---------------------------------------------------------------------------------------
# Build the daily point-in-time DOUBLE-CONFIRM panel using the live eval_* functions.
# ---------------------------------------------------------------------------------------
def build_signal_panel(price, fin, dt5g, rat, calendar):
    """Return two DataFrames indexed by `calendar` (dates) x WL_TK:
       buy[name]  = True if sector-lens BUY that day, strong[name] = True if buy_mode STRONG,
       dbl[name]  = True if BUY AND rating<=2 (double-confirm)."""
    calendar = pd.DatetimeIndex(calendar).as_unit("ns")
    fin = fin.copy(); fin["Release_Date"] = fin["Release_Date"].astype("datetime64[ns]")
    rat = rat.copy(); rat["eff_date"] = rat["eff_date"].astype("datetime64[ns]")
    dt5g = dt5g.set_index("time")["state"].reindex(calendar).ffill()
    buy = pd.DataFrame(False, index=calendar, columns=WL_TK)
    strong = pd.DataFrame(False, index=calendar, columns=WL_TK)
    dbl = pd.DataFrame(False, index=calendar, columns=WL_TK)

    for tk, sector, key in WL:
        pk = price[price["ticker"] == tk].set_index("time").sort_index()
        if pk.empty:
            continue
        pk = pk[~pk.index.duplicated(keep="last")].reindex(calendar)  # daily, no ffill on price
        # as-of financials (Release_Date <= date)
        fk = fin[fin["ticker"] == tk].sort_values("Release_Date")
        if fk.empty:
            continue
        fk_asof = pd.merge_asof(pd.DataFrame({"time": calendar}), fk,
                                left_on="time", right_on="Release_Date", direction="backward")
        fk_asof = fk_asof.set_index("time")
        # as-of rating (eff_date <= date)
        rk = rat[rat["ticker"] == tk].sort_values("eff_date")
        if rk.empty:
            rating_series = pd.Series(np.nan, index=calendar)
        else:
            rmerge = pd.merge_asof(pd.DataFrame({"time": calendar}), rk,
                                   left_on="time", right_on="eff_date", direction="backward")
            rating_series = rmerge.set_index("time")["rating"]

        for d in calendar:
            prow = pk.loc[d]
            if not np.isfinite(slm._f(prow.get("Close"))):
                continue                                   # no price that day -> not evaluable
            v = {cc: prow.get(cc) for cc in VAL_COLS}
            f = {cc: fk_asof.loc[d].get(cc) for cc in FIN_COLS}
            f["PE_MA5Y"] = v.get("PE_MA5Y")                # dhg reads PE_MA5Y off v; fin also has it
            r = _eval(key, tk, v, f, int(dt5g.loc[d]) if np.isfinite(dt5g.loc[d]) else 3)
            if r["status"] == "BUY":
                buy.at[d, tk] = True
                if r["mode"] == "STRONG":
                    strong.at[d, tk] = True
                rt = rating_series.loc[d]
                if np.isfinite(slm._f(rt)) and int(rt) <= 2:
                    dbl.at[d, tk] = True
    return buy, strong, dbl


def _eval(key, tk, v, f, state):
    st = {"state": state, "time": None}
    if key == "bank":  return slm.eval_bank(tk, v, f)
    if key == "fpt":   return slm.eval_fpt(tk, v, f)
    if key == "sec":   return slm.eval_sec(tk, v, f, st)
    if key == "ctr":   return slm.eval_ctr(tk, v, f)
    if key == "msh":   return slm.eval_msh(tk, v, f)
    if key == "dhg":   return slm.eval_dhg(tk, v, f)
    if key == "pvt":   return slm.eval_pvt(tk, v, f)
    if key == "hah":   return slm.eval_hah(tk, v, f)
    if key == "dbc":   return slm.eval_dbc(tk, v, f, np.nan, False)   # no historical hog-feed feed
    return dict(status="EXCLUDED", mode="")


# ---------------------------------------------------------------------------------------
# Parking basket (custom30V) daily NAV — buy-and-hold drift within each quarterly period.
# ---------------------------------------------------------------------------------------
def parking_returns(basket, price_wide, calendar):
    ret = price_wide.pct_change()
    rebals = sorted(basket["rebal_date"].unique())
    park = pd.Series(0.0, index=calendar)
    holdings = None                                        # name -> value
    reb_idx = 0
    for i, d in enumerate(calendar):
        # apply any rebals effective on/before d that we haven't applied yet
        while reb_idx < len(rebals) and rebals[reb_idx] <= d:
            mem = basket[basket["rebal_date"] == rebals[reb_idx]]
            w = mem.set_index("ticker")["weight"]
            w = w[w.index.isin(price_wide.columns)]
            holdings = (w / w.sum()).to_dict()
            reb_idx += 1
        if holdings is None or i == 0:
            continue
        r = ret.loc[d]
        num = 0.0; den = 0.0
        newh = {}
        for tk, val in holdings.items():
            rt = r.get(tk)
            rt = rt if np.isfinite(rt) else 0.0
            nv = val * (1 + rt)
            num += val * rt; den += val
            newh[tk] = nv
        park.loc[d] = num / den if den > 0 else 0.0
        # renormalize drifted holdings so weights track value
        holdings = newh
    return park


# ---------------------------------------------------------------------------------------
# Target-weight builder + NAV sim.
# ---------------------------------------------------------------------------------------
def target_weights(buy, strong, dbl, calendar, restrict=None, tilt=True):
    """Daily active weights (DataFrame date x WL_TK) + parking fraction Series.
       restrict: optional set of names allowed in the active book (for static AlphaLens A/B)."""
    W = pd.DataFrame(0.0, index=calendar, columns=WL_TK)
    park = pd.Series(1.0, index=calendar)
    for d in calendar:
        names = [tk for tk in WL_TK if dbl.at[d, tk] and (restrict is None or tk in restrict)]
        if not names:
            continue
        raw = np.array([STRONG_TILT if (tilt and strong.at[d, tk]) else 1.0 for tk in names])
        share = raw / raw.sum()
        w = np.minimum(CAP, share)
        for tk, wi in zip(names, w):
            W.at[d, tk] = wi
        park.loc[d] = max(0.0, 1.0 - w.sum())
    return W, park


def sim_nav(active_W, park_frac, stock_ret, park_ret, calendar, tc):
    """T+1 execution: weights at t-1 earn return t. Returns daily net return Series + turnover."""
    port = pd.Series(0.0, index=calendar)
    turn = pd.Series(0.0, index=calendar)
    prev_w = pd.Series(0.0, index=WL_TK); prev_park = 1.0
    for i, d in enumerate(calendar):
        if i == 0:
            prev_w = active_W.loc[d].copy(); prev_park = park_frac.loc[d]; continue
        r_active = float((prev_w * stock_ret.loc[d].reindex(WL_TK).fillna(0.0)).sum())
        r_park = prev_park * (park_ret.loc[d] if np.isfinite(park_ret.loc[d]) else 0.0)
        cur_w = active_W.loc[d]; cur_park = park_frac.loc[d]
        t = float((cur_w - prev_w).abs().sum() + abs(cur_park - prev_park)) / 2.0
        port.loc[d] = r_active + r_park - t * tc
        turn.loc[d] = t
        prev_w = cur_w.copy(); prev_park = cur_park
    return port, turn


def metrics(r):
    r = r.dropna()
    s = (1 + r).cumprod()
    if len(s) < 2:
        return (np.nan,) * 5
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1 / yrs) - 1
    spd = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else 0
    so = r.mean() / r[r < 0].std() * np.sqrt(spd) if (r < 0).any() and r[r < 0].std() > 0 else 0
    dd = (s / s.cummax() - 1).min()
    cal = (cagr) / abs(dd) if dd < 0 else 0
    return cagr * 100, sh, so, dd * 100, cal


def windows(r):
    return [("FULL 2014-08→now", r),
            ("IS 2014-2019", r[r.index <= IS_END]),
            ("OOS 2020→now", r[r.index >= OOS_START])]


def report(name, r):
    print(f"\n### {name}")
    print(f"  {'window':<18}{'CAGR':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD':>9}{'Calmar':>8}")
    for tag, rr in windows(r):
        c, sh, so, dd, cal = metrics(rr)
        print(f"  {tag:<18}{c:>7.2f}%{sh:>8.2f}{so:>9.2f}{dd:>8.1f}%{cal:>8.2f}")


def main():
    print("Loading caches ...")
    basket = load_parking_basket()
    price = load_prices(set(WL_TK) | set(basket["ticker"]))
    fin = load_financials()
    dt5g = load_dt5g()
    rat = load_ratings()

    calendar = pd.DatetimeIndex(sorted(price["time"].unique()))
    calendar = calendar[calendar >= pd.Timestamp(START)]
    price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar)
    stock_ret = price_wide[WL_TK].pct_change()

    print(f"Calendar {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")
    print("Building point-in-time double-confirm panel (live eval_* fns) ...")
    buy, strong, dbl = build_signal_panel(price, fin, dt5g, rat, calendar)
    print(f"  double-confirm name-days: {int(dbl.values.sum())}; "
          f"days with >=1 double-confirm: {int((dbl.sum(axis=1) > 0).sum())}/{len(calendar)}")
    dc_counts = dbl.sum(axis=1)
    print(f"  active-set size when active: mean {dc_counts[dc_counts>0].mean():.1f}, "
          f"max {int(dc_counts.max())}")

    park_ret = parking_returns(basket, price_wide, calendar)

    # ---- self-check: parking is the baseline (100% parking, no active) ----
    zeros_W = pd.DataFrame(0.0, index=calendar, columns=WL_TK)
    ones_park = pd.Series(1.0, index=calendar)
    base_ret, _ = sim_nav(zeros_W, ones_park, stock_ret, park_ret, calendar, tc=0.001)
    # baseline turnover only from quarterly basket internal rebal -> approximate as park_ret already net?
    # We report baseline as pure parking index (custom30V thuen) with the same TC treatment (no active moves).

    configs = {}
    for label, restrict, tilt in [
            ("ConvergePort (tilt 1.5x STRONG)", None, True),
            ("ConvergePort (equal-weight)", None, False),
            ("AlphaLens-static (FPT/ACB/MBB/HDB only, tilt)", {"FPT", "ACB", "MBB", "HDB"}, True)]:
        W, pf = target_weights(buy, strong, dbl, calendar, restrict=restrict, tilt=tilt)
        configs[label] = (W, pf)

    TC = 0.001
    print("\n" + "=" * 78)
    print(f"WALK-FORWARD RESULTS (TC={TC:.1%} per unit turnover, T+1 execution, threads=1)")
    print("=" * 78)
    report("custom30V thuần (100% parking) — BASELINE", base_ret)

    results = {"baseline": base_ret}
    turnovers = {}
    for label, (W, pf) in configs.items():
        r, turn = sim_nav(W, pf, stock_ret, park_ret, calendar, tc=TC)
        results[label] = r
        turnovers[label] = turn
        report(label, r)
        # self-check weights sum to 1
        wsum = (W.sum(axis=1) + pf)
        leak = float((wsum - 1.0).abs().max())
        ann_turn = turn.sum() / ((calendar[-1] - calendar[0]).days / 365.25)
        print(f"  self-check weight-sum max|dev-from-1| = {leak:.2e} (0 VND leak OK if ~0)")
        print(f"  annualized one-way turnover = {ann_turn:.2f}x/yr")

    # ---- TC sensitivity on the primary config ----
    print("\n" + "=" * 78)
    print("TC SENSITIVITY — ConvergePort (tilt) FULL-period CAGR at TC in {0.1,0.2,0.3}%")
    print("=" * 78)
    W, pf = configs["ConvergePort (tilt 1.5x STRONG)"]
    for tc in (0.001, 0.002, 0.003):
        r, _ = sim_nav(W, pf, stock_ret, park_ret, calendar, tc=tc)
        c, sh, so, dd, cal = metrics(r)
        print(f"  TC={tc:.1%}: CAGR {c:.2f}%  Sharpe {sh:.2f}  MaxDD {dd:.1f}%  Calmar {cal:.2f}")

    # ---- deltas vs baseline (FULL) ----
    print("\n" + "=" * 78)
    print("DELTA vs custom30V thuần (FULL-period, TC=0.1%)")
    print("=" * 78)
    bc = metrics(base_ret)
    for label in configs:
        cc = metrics(results[label])
        print(f"  {label:<46} dCAGR {cc[0]-bc[0]:+.2f}pp  dSharpe {cc[1]-bc[1]:+.2f}  "
              f"dCalmar {cc[4]-bc[4]:+.2f}  dMaxDD {cc[3]-bc[3]:+.1f}pp")

    # persist NAV series for audit / DSR
    out = pd.DataFrame({"date": calendar})
    out["baseline_ret"] = base_ret.values
    for label, (W, pf) in configs.items():
        out[label] = results[label].values
    out.to_csv(os.path.join(WORKDIR, "data", "converge_portfolio_backtest_nav.csv"), index=False)
    print("\nwrote data/converge_portfolio_backtest_nav.csv")

    # today's live double-confirm set (for the paper launch)
    last = calendar[-1]
    live = [tk for tk in WL_TK if dbl.at[last, tk]]
    live_modes = {tk: ("STRONG" if strong.at[last, tk] else "ACCUMULATE") for tk in live}
    print(f"\nLatest ({last.date()}) double-confirm set: {live_modes}")


if __name__ == "__main__":
    main()
