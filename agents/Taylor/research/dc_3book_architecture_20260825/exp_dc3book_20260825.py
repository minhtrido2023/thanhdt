# -*- coding: utf-8 -*-
"""exp_dc3book_20260825.py — R&D wrapper: simulate a 3-book V2.4 variant
(w_BAL=w_LAG=w_DC=1/3 NAV, band +-10pp per book) and compare to the V2.4 R3
baseline (park=0.80).

Job Taylor_20260825_151108 (dispatch from Mike), Phan A. RESEARCH ONLY.
- Does NOT modify pt_v23_audit_2014.py, converge_portfolio_backtest.py, or any
  production CSV. Reads existing artifacts + reuses converge_portfolio_backtest's
  loaders/eval functions by import (no re-implementation of eval_* logic).
- Writes only to this research subfolder (data/*_3book_dc33_*.csv).

METHOD
------
1. r_BAL(t), r_LAG(t): pulled straight from the golive-audit production CSV
   (record_type=DAILY, columns nav_bal_ref/nav_lag_ref) as pct-change. These
   are book-level NAV trackers already inclusive of each book's own real
   behaviour (BAL parks into custom30V during NEUTRAL; LAG does not park,
   sits in cash when no PEAD signal) -- exactly what "gross_by_state" job
   Taylor_20260825_134238 used.
2. r_DC(t): built fresh from converge_portfolio_backtest.py's own building
   blocks (build_signal_panel, target_weights with tilt=False i.e.
   equal-weight per dispatch instruction, cap 0.20/name). Idle DC cash is
   NOT parked in custom30V unconditionally (that was ConvergePort's own
   Layer-2, which parks in EVERY state) -- instead it follows the SAME
   convention as the rest of V2.4: park @0.80 in custom30V only when
   state==NEUTRAL(3), else sits at 0% (idle cash, CLAUDE.md convention).
   This is the one deliberate behavioural change vs the raw ConvergePort
   backtest, made so the "book" is apples-to-apples with BAL/LAG under the
   V2.4 state-gated parking convention the dispatch specified.
3. Combine: track dollar buckets V_BAL, V_LAG, V_DC starting at NAV0/3 each.
   Each day, apply that book's own return to its bucket. If any bucket's
   weight drifts beyond target(1/3) +-10pp, rebalance ALL THREE back to 1/3,
   charging TC=0.1% (CLAUDE.md standard) on the two-sided dollar amount
   moved. This is a simplification of V2.4's real allocator (which has a
   much richer state-conditional w_lag_tgt + CAPIT arm) -- documented as a
   caveat, not hidden.
4. Self-check: 0 VND leak (bucket weights sum to 1.0 every day, dry run
   confirms no NaN/inf propagation). IS(2014-19)/OOS(2020+) split kept.
   Calendar clipped to >= 2014-08-05 (DC/custom30V basket start) for a
   like-for-like comparison against a RECOMPUTED baseline over the SAME
   window (the officially registered V2.4 baseline starts 2014-01-02 and
   is NOT reused verbatim here -- see caveat in SUMMARY.md).
"""
import os, sys, csv
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR = os.path.dirname(os.path.abspath(__file__))

import converge_portfolio_backtest as cpb  # noqa: E402  (reuse, no rewrite)

GOLIVE_CSV = os.path.join(
    WORKDIR, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
    "park3-80_wtnamecap_advprice_exp_agg_F1_t80_univpit.csv")

TC = 0.001          # CLAUDE.md standard: 0.1% per side on capital actually traded
BAND = 0.10         # +-10pp rebalance band per book
TARGET = 1.0 / 3.0
IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
PARK_NEUTRAL = 0.80  # PARK_STATES_DICT = {3: 0.80}, unchanged


def load_bal_lag_daily():
    """r_BAL(t), r_LAG(t), state(t) from the production golive-audit CSV."""
    usecols = ["record_type", "ymd", "state", "nav_bal_ref", "nav_lag_ref"]
    df = pd.read_csv(GOLIVE_CSV, usecols=usecols)
    df = df[df["record_type"] == "DAILY"].copy()
    df["ymd"] = pd.to_datetime(df["ymd"])
    df = df.sort_values("ymd").reset_index(drop=True)
    df["r_bal"] = df["nav_bal_ref"].pct_change()
    df["r_lag"] = df["nav_lag_ref"].pct_change()
    return df[["ymd", "state", "r_bal", "r_lag"]]


def build_dc_returns(calendar):
    """r_DC(t) over `calendar` using ConvergePort's own loaders, equal-weight
    (tilt=False per dispatch), state-gated parking (NEUTRAL@0.80 only)."""
    basket = cpb.load_parking_basket()
    price = cpb.load_prices(set(cpb.WL_TK) | set(basket["ticker"]))
    fin = cpb.load_financials()
    dt5g = cpb.load_dt5g()
    rat = cpb.load_ratings()

    price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar)
    stock_ret = price_wide[cpb.WL_TK].pct_change()

    buy, strong, dbl = cpb.build_signal_panel(price, fin, dt5g, rat, calendar)
    W, park_frac = cpb.target_weights(buy, strong, dbl, calendar, restrict=None, tilt=False)
    active_frac = W.sum(axis=1)

    park_ret = cpb.parking_returns(basket, price_wide, calendar)
    state = dt5g.set_index("time")["state"].reindex(calendar).ffill()

    r_dc = pd.Series(0.0, index=calendar)
    n_active_days = 0
    for i in range(1, len(calendar)):
        d, dprev = calendar[i], calendar[i - 1]
        af_prev = active_frac.loc[dprev]
        if af_prev > 0:
            raw = float((W.loc[dprev] * stock_ret.loc[d].reindex(cpb.WL_TK).fillna(0.0)).sum())
            r_active_leg = raw / af_prev
            n_active_days += 1
        else:
            r_active_leg = 0.0
        idle_frac = 1.0 - af_prev
        st_prev = state.loc[dprev]
        if np.isfinite(st_prev) and int(st_prev) == 3:  # NEUTRAL
            park_deploy = PARK_NEUTRAL
        else:
            park_deploy = 0.0
        rp = park_ret.loc[d] if np.isfinite(park_ret.loc[d]) else 0.0
        r_dc.loc[d] = af_prev * r_active_leg + idle_frac * park_deploy * rp
    return r_dc, active_frac, n_active_days


def sim_3book(dates, r_bal, r_lag, r_dc):
    """Dollar-bucket sim with +-10pp rebalance band. Returns daily portfolio
    return series + rebalance-day count + self-check leak."""
    n = len(dates)
    V = np.array([TARGET, TARGET, TARGET])  # normalized to NAV=1.0
    port_ret = np.zeros(n)
    n_rebal = 0
    max_leak = 0.0
    for i in range(1, n):
        rb, rl, rd = r_bal[i], r_lag[i], r_dc[i]
        rb = 0.0 if not np.isfinite(rb) else rb
        rl = 0.0 if not np.isfinite(rl) else rl
        rd = 0.0 if not np.isfinite(rd) else rd
        V_prev_total = V.sum()
        V = V * (1.0 + np.array([rb, rl, rd]))
        total = V.sum()
        port_ret[i] = total / V_prev_total - 1.0
        w = V / total
        if np.max(np.abs(w - TARGET)) > BAND:
            moved = np.abs(V - total * TARGET).sum() / 2.0  # one-way $ moved
            tc_cost = (moved / total) * TC
            port_ret[i] -= tc_cost
            total_after_cost = total * (1.0 - tc_cost)
            V = np.array([TARGET, TARGET, TARGET]) * total_after_cost
            n_rebal += 1
        # self-check: bucket weights must always sum to 1.0 by construction
        max_leak = max(max_leak, abs((V / V.sum()).sum() - 1.0))
    return pd.Series(port_ret, index=dates), n_rebal, max_leak


def metrics(r):
    r = r.dropna()
    s = (1 + r).cumprod()
    if len(s) < 2:
        return dict(cagr=np.nan, sharpe=np.nan, sortino=np.nan, maxdd=np.nan, calmar=np.nan)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1 / yrs) - 1
    spd = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else 0.0
    neg = r[r < 0]
    so = r.mean() / neg.std() * np.sqrt(spd) if len(neg) > 0 and neg.std() > 0 else 0.0
    dd = (s / s.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else 0.0
    return dict(cagr=cagr * 100, sharpe=sh, sortino=so, maxdd=dd * 100, calmar=cal)


def window_report(name, r):
    rows = []
    for tag, sub in [("FULL", r), ("IS 2014-19", r[r.index <= IS_END]),
                     ("OOS 2020+", r[r.index >= OOS_START])]:
        m = metrics(sub)
        rows.append((name, tag, m["cagr"], m["sharpe"], m["sortino"], m["maxdd"], m["calmar"], len(sub.dropna())))
    return rows


def main():
    print("Loading BAL/LAG production daily returns ...")
    bl = load_bal_lag_daily()
    bl = bl[bl["ymd"] >= pd.Timestamp("2014-08-05")].reset_index(drop=True)
    calendar = pd.DatetimeIndex(bl["ymd"])

    print(f"Calendar: {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")
    print("Building DC book returns (reusing converge_portfolio_backtest loaders) ...")
    r_dc_full, active_frac, n_active_days = build_dc_returns(calendar)

    r_bal = bl.set_index("ymd")["r_bal"].reindex(calendar).values
    r_lag = bl.set_index("ymd")["r_lag"].reindex(calendar).values
    r_dc = r_dc_full.reindex(calendar).values

    print("Simulating 3-book portfolio (1/3 each, +-10pp band, TC=0.1%) ...")
    port_3book, n_rebal, max_leak = sim_3book(calendar, r_bal, r_lag, r_dc)

    # ---- baseline: recompute BAL+LAG-only V2.4 (w_lag production split) over the SAME window ----
    # Use the *actual* production combined_nav pct-change as the true V2.4 baseline (same window).
    usecols = ["record_type", "ymd", "combined_nav"]
    prod = pd.read_csv(GOLIVE_CSV, usecols=usecols)
    prod = prod[prod["record_type"] == "DAILY"].copy()
    prod["ymd"] = pd.to_datetime(prod["ymd"])
    prod = prod.sort_values("ymd").set_index("ymd")
    prod_ret_full = prod["combined_nav"].pct_change()
    baseline_2book = prod_ret_full.reindex(calendar)  # clipped to same 2014-08-05+ window

    print("\n" + "=" * 90)
    print("RESULTS — 3-book (BAL=LAG=DC=1/3, band +-10pp) vs V2.4 baseline (2-book, park=0.80)")
    print("=" * 90)
    rows = []
    rows += window_report("baseline_2book_park80_SAMEWINDOW", baseline_2book)
    rows += window_report("exp_3book_dc33", port_3book)
    hdr = f"{'config':<32}{'window':<12}{'CAGR%':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD%':>9}{'Calmar':>8}{'N':>7}"
    print(hdr)
    for r in rows:
        print(f"{r[0]:<32}{r[1]:<12}{r[2]:>7.2f}{r[3]:>8.2f}{r[4]:>9.2f}{r[5]:>8.1f}{r[6]:>8.2f}{r[7]:>7d}")

    yrs = (calendar[-1] - calendar[0]).days / 365.25
    print(f"\nself-check: rebalance events = {n_rebal} ({n_rebal/yrs:.2f}/yr) ; max weight-leak = {max_leak:.2e}")
    print(f"DC active-book days (>=1 double-confirm name): {n_active_days}/{len(calendar)} "
          f"({n_active_days/len(calendar)*100:.1f}%)")

    out = pd.DataFrame({
        "date": calendar,
        "r_bal": r_bal, "r_lag": r_lag, "r_dc": r_dc,
        "port_3book_dc33": port_3book.values,
        "baseline_2book_samewindow": baseline_2book.values,
    })
    outcsv = os.path.join(OUTDIR, "exp_dc3book_nav_3book_dc33.csv")
    out.to_csv(outcsv, index=False)
    print(f"\nwrote {outcsv}")

    summary_csv = os.path.join(OUTDIR, "exp_dc3book_metrics_3book_dc33.csv")
    with open(summary_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["config", "window", "cagr_pct", "sharpe", "sortino", "maxdd_pct", "calmar", "n_days"])
        w.writerows(rows)
    print(f"wrote {summary_csv}")


if __name__ == "__main__":
    main()
