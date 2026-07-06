# -*- coding: utf-8 -*-
"""converge_union_test.py — UNION (OR) variant of ConvergePort (job Taylor_20260706_114506).

Follow-up to the double-confirm ConvergePort work (job _093329 launch; _095725/_103815 full-book
REFUTE; _105156 capacity). User question: the double-confirm set (AlphaLens BUY  AND  8L golden)
is too thin (mean 3.9 names, 17% of days 0 names). Does switching AND -> OR (UNION) fix the
"too few deals" problem WITHOUT hurting risk-adjusted performance?

UNION definition (per Mike's dispatch, NO new conditions invented):
  member(name, t) = [ name in sector_lens Group-A  AND  sector-lens status(name,t)==BUY ]      (AlphaLens arm)
                 OR [ name in rating_8l.py BUY-NOW list at t ]                                   (Golden arm)
  where BUY-NOW is rating_8l.py's OWN pre-defined golden-cell screen (rating_8l.py L568-576):
       rating(as-of) <= 3  AND  liq_bn (=Trading_Value_1M_P50/1e9) >= 3.0
       AND  pb_z (=(PB-PB_MA5Y)/PB_SD5Y) <= -0.3  AND  NOT(ROE_Min3Y < 0)   [book-trustworthy guard]
  (NB: the dispatch's parenthetical said "ROE_Min5Y>=0"; the ACTUAL rating_8l.py BUY-NOW code uses the
   ROE_Min3Y<0 chronic-destroyer guard — L570-571. Per instruction "read the real BUY-NOW logic, do
   NOT redefine", the code's ROE_Min3Y guard is used. Noted in the finding.)

WHY THE FRACTIONAL PAPER-SIM (this file / converge_portfolio_backtest.py) AND NOT the fullharness
single-book replacement (converge_fullharness_test.py CONVERGE_BOOK):
  - The launched paper book + the headline "+5.0pp vs custom30V" both live in the fractional sim
    (registry: ConvergePort EW 23.86% vs custom30V 18.75%). That IS the frame of the user's question
    ("switch the paper design?").
  - The fullharness CONVERGE_BOOK frame (replace BOTH production books with one converge book) is
    ALREADY REFUTED (12.05% vs R3 28.05%) and uses a FIXED per-name weight WPN=0.11. Double-confirm
    breadth <=9 fits under 100%; UNION breadth is ~10-40 names/day -> fixed 0.11/name clips at cash
    exhaustion (ordering artifact), producing a meaningless number. The fractional sim (min(CAP,1/n)
    + parking, weights sum to 1.0) handles arbitrary breadth correctly and is SCALE-INVARIANT (proven
    job _105156: sim_nav carries no NAV/ADV term). So NAV=20B is irrelevant to the RETURN sim; it
    only matters for the ADV capacity overlay, computed separately below.
  - Same engine both sides (baseline / double-confirm / UNION) -> the A/B DELTA is the valid signal.

Everything else identical to converge_portfolio_backtest.py: custom30V parking (buy-and-hold drift),
DT5G-as-of state gates the sector-lens eval, T+1 execution, threads=1, self-check weights sum 1.0.
"""
import os, sys, json
import numpy as np, pandas as pd
import duckdb

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
CACHE = os.path.join(WORKDIR, "data", "bq_cache")
NAV_B = float(os.environ.get("NAV_TOTAL_B", "20"))            # for the ADV capacity overlay only

import converge_portfolio_backtest as cpb   # reuse EXACT loaders + double-confirm panel + metrics
from converge_portfolio_backtest import (WL, WL_TK, START, IS_END, OOS_START, CAP,
                                         metrics, windows, build_signal_panel)

LIQ_MIN = 3.0            # rating_8l.py L531 — bn VND/day investable floor
PBZ_BUY = -0.3           # rating_8l.py L569 BUY-NOW cheap-vs-own-history threshold
# rating_8l live always force-excludes these (banned / governance rating>=4) -> never in a real BUY-NOW list
BANNED = {"PC1","VVS","KSF","NKG","HSG","HVN","VJC","NVL","GEG","SBA","DMC","IMP","TRA","TOS","VTP"}


def con():
    c = duckdb.connect(":memory:"); c.execute("SET threads=1"); return c


def build_buynow_panel(calendar):
    """Point-in-time rating_8l.py BUY-NOW membership over the FULL ticker_prune universe.
       Returns (members_by_date: dict date->set(ticker), all_names: sorted list)."""
    c = con()
    df = c.execute(f"""
        SELECT time, ticker, PB, PB_MA5Y, PB_SD5Y, ROE_Min3Y, Trading_Value_1M_P50
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE time >= '{START}'
          AND ticker IN (SELECT DISTINCT ticker FROM read_parquet('{CACHE}/ticker_prune.parquet')) """).df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    df["pb_z"] = (df["PB"] - df["PB_MA5Y"]) / df["PB_SD5Y"].replace(0, np.nan)
    df["liq_bn"] = df["Trading_Value_1M_P50"] / 1e9
    # pre-rating screen (vectorized): cheap-vs-own-history, liquid, book-trustworthy, not banned
    pre = df[(df["pb_z"] <= PBZ_BUY) & (df["liq_bn"] >= LIQ_MIN) &
             (~(df["ROE_Min3Y"] < 0)) & (~df["ticker"].isin(BANNED))].copy()
    # as-of rating gate (rating<=3), same rating source as the double-confirm methodology
    rat = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l_history.csv"))
    rat = rat[["ticker", "eff_date", "rating"]].copy()
    rat["eff_date"] = pd.to_datetime(rat["eff_date"])
    rat = rat.sort_values(["ticker", "eff_date"])
    pre = pre.sort_values(["ticker", "time"])
    merged = []
    for tk, g in pre.groupby("ticker", sort=False):
        rk = rat[rat["ticker"] == tk]
        if rk.empty:
            continue                                  # no rating history -> rating_8l wouldn't list it
        m = pd.merge_asof(g[["time", "ticker"]], rk[["eff_date", "rating"]],
                          left_on="time", right_on="eff_date", direction="backward")
        m = m[m["rating"] <= 3]
        if len(m):
            merged.append(m[["time", "ticker"]])
    buynow = pd.concat(merged, ignore_index=True) if merged else pd.DataFrame(columns=["time", "ticker"])
    cal_set = set(calendar)
    buynow = buynow[buynow["time"].isin(cal_set)]
    mem = {}
    for d, g in buynow.groupby("time"):
        mem[d] = set(g["ticker"])
    all_names = sorted(buynow["ticker"].unique())
    return mem, all_names, df


def build_union_membership(buy, buynow_mem, calendar, union_names):
    """Daily boolean membership DataFrame (calendar x union_names): sector-lens BUY (WL_TK) OR BUY-NOW."""
    M = pd.DataFrame(False, index=calendar, columns=union_names)
    # AlphaLens arm: sector-lens BUY on the 16 WL names
    for tk in WL_TK:
        if tk in M.columns and tk in buy.columns:
            M[tk] = M[tk] | buy[tk].reindex(calendar).fillna(False).values
    # Golden arm: BUY-NOW membership (full universe)
    for d in calendar:
        for tk in buynow_mem.get(d, ()):
            if tk in M.columns:
                M.at[d, tk] = True
    return M


def equal_weights(M, calendar, names):
    """Equal-weight active members min(CAP, 1/n), parking = 1 - sum. Symmetric to double-confirm."""
    W = pd.DataFrame(0.0, index=calendar, columns=names)
    park = pd.Series(1.0, index=calendar)
    for d in calendar:
        row = M.loc[d]
        active = [tk for tk in names if row[tk]]
        n = len(active)
        if n == 0:
            continue
        w = min(CAP, 1.0 / n)
        for tk in active:
            W.at[d, tk] = w
        park.loc[d] = max(0.0, 1.0 - w * n)
    return W, park


def sim_nav_cols(active_W, park_frac, stock_ret, park_ret, calendar, names, tc):
    """T+1 fractional sim over an arbitrary column set (generalizes cpb.sim_nav which hardcodes WL_TK)."""
    port = pd.Series(0.0, index=calendar); turn = pd.Series(0.0, index=calendar)
    prev_w = pd.Series(0.0, index=names); prev_park = 1.0
    for i, d in enumerate(calendar):
        if i == 0:
            prev_w = active_W.loc[d].copy(); prev_park = park_frac.loc[d]; continue
        r_active = float((prev_w * stock_ret.loc[d].reindex(names).fillna(0.0)).sum())
        pr = park_ret.loc[d]
        r_park = prev_park * (pr if np.isfinite(pr) else 0.0)
        cur_w = active_W.loc[d]; cur_park = park_frac.loc[d]
        t = float((cur_w - prev_w).abs().sum() + abs(cur_park - prev_park)) / 2.0
        port.loc[d] = r_active + r_park - t * tc
        turn.loc[d] = t
        prev_w = cur_w.copy(); prev_park = cur_park
    return port, turn


def report(name, r):
    print(f"\n### {name}")
    print(f"  {'window':<18}{'CAGR':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD':>9}{'Calmar':>8}")
    rows = {}
    for tag, rr in windows(r):
        c, sh, so, dd, cal = metrics(rr)
        print(f"  {tag:<18}{c:>7.2f}%{sh:>8.2f}{so:>9.2f}{dd:>8.1f}%{cal:>8.2f}")
        rows[tag] = dict(cagr=c, sharpe=sh, sortino=so, maxdd=dd, calmar=cal)
    return rows


def breadth_stats(M, calendar, label):
    cnt = M.loc[calendar].sum(axis=1)
    active_days = int((cnt > 0).sum()); n = len(calendar)
    empty = n - active_days
    mean_when = float(cnt[cnt > 0].mean()) if active_days else 0.0
    print(f"  [{label}] breadth: mean-when-active {mean_when:.1f}, median-when-active "
          f"{float(cnt[cnt>0].median()) if active_days else 0:.0f}, max {int(cnt.max())}, "
          f"empty days {empty}/{n} ({100*empty/n:.1f}%), active {active_days}/{n} ({100*active_days/n:.1f}%)")
    return dict(mean_when_active=mean_when, max=int(cnt.max()), empty_days=empty,
                total_days=n, empty_pct=round(100*empty/n, 1))


def main():
    print("Loading caches ...")
    basket = cpb.load_parking_basket()
    fin = cpb.load_financials(); dt5g = cpb.load_dt5g(); rat = cpb.load_ratings()

    # --- calendar from WL+basket prices (same basis as cpb.main), then BUY-NOW panel ---
    price0 = cpb.load_prices(set(WL_TK) | set(basket["ticker"]))
    calendar = pd.DatetimeIndex(sorted(price0["time"].unique()))
    calendar = calendar[calendar >= pd.Timestamp(START)]
    print(f"Calendar {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")

    print("Building point-in-time double-confirm panel (live eval_* fns) ...")
    buy, strong, dbl = build_signal_panel(price0, fin, dt5g, rat, calendar)

    print("Building point-in-time BUY-NOW panel (full ticker_prune universe) ...")
    buynow_mem, buynow_names, _ = build_buynow_panel(calendar)
    print(f"  BUY-NOW distinct names ever: {len(buynow_names)}")

    union_names = sorted(set(WL_TK) | set(buynow_names))
    print(f"  UNION universe size (WL 16 U BUY-NOW): {len(union_names)} names")

    # prices/returns for ALL union names + basket
    price = cpb.load_prices(set(union_names) | set(basket["ticker"]))
    price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar)
    park_ret = cpb.parking_returns(basket, price_wide, calendar)

    # ---- memberships ----
    union_M = build_union_membership(buy, buynow_mem, calendar, union_names)
    # double-confirm membership (dbl) mapped onto union columns for identical-sim comparison
    dc_M = pd.DataFrame(False, index=calendar, columns=union_names)
    for tk in WL_TK:
        if tk in dc_M.columns:
            dc_M[tk] = dbl[tk].reindex(calendar).fillna(False).values
    # BUY-NOW-only membership (golden arm alone, for decomposition)
    bn_M = pd.DataFrame(False, index=calendar, columns=union_names)
    for d in calendar:
        for tk in buynow_mem.get(d, ()):
            if tk in bn_M.columns:
                bn_M.at[d, tk] = True

    print("\n" + "=" * 78 + "\nBREADTH / EMPTY-DAYS\n" + "=" * 78)
    br_dc = breadth_stats(dc_M, calendar, "double-confirm (AND)")
    br_bn = breadth_stats(bn_M, calendar, "BUY-NOW golden arm (alone)")
    br_un = breadth_stats(union_M, calendar, "UNION (OR)")

    stock_ret = price_wide[union_names].pct_change()
    TC = 0.001

    # ---- baseline: 100% custom30V parking ----
    zeros_W = pd.DataFrame(0.0, index=calendar, columns=union_names)
    ones_park = pd.Series(1.0, index=calendar)
    base_ret, _ = sim_nav_cols(zeros_W, ones_park, stock_ret, park_ret, calendar, union_names, tc=TC)

    # ---- double-confirm equal-weight (recomputed here, same engine) ----
    dcW, dcP = equal_weights(dc_M, calendar, union_names)
    dc_ret, dc_turn = sim_nav_cols(dcW, dcP, stock_ret, park_ret, calendar, union_names, tc=TC)

    # ---- UNION equal-weight ----
    unW, unP = equal_weights(union_M, calendar, union_names)
    un_ret, un_turn = sim_nav_cols(unW, unP, stock_ret, park_ret, calendar, union_names, tc=TC)

    print("\n" + "=" * 78)
    print(f"WALK-FORWARD (TC={TC:.1%}/unit turnover, T+1 exec, threads=1, NAV-agnostic fractional sim)")
    print("=" * 78)
    R = {}
    R["baseline"]      = report("custom30V thuần (100% parking) — BASELINE", base_ret)
    R["double_confirm"]= report("ConvergePort DOUBLE-CONFIRM (AND, equal-weight)", dc_ret)
    R["union"]         = report("ConvergePort UNION (OR, equal-weight)", un_ret)

    # self-checks (0 VND leak)
    for lbl, (W, P) in [("double-confirm", (dcW, dcP)), ("UNION", (unW, unP))]:
        leak = float(((W.sum(axis=1) + P) - 1.0).abs().max())
        print(f"  self-check {lbl} weight-sum max|dev-1| = {leak:.2e}")
    yrs = (calendar[-1] - calendar[0]).days / 365.25
    print(f"  annualized one-way turnover: double-confirm {dc_turn.sum()/yrs:.2f}x/yr, "
          f"UNION {un_turn.sum()/yrs:.2f}x/yr")

    # deltas vs baseline
    print("\n" + "=" * 78 + "\nDELTA vs custom30V thuần (FULL, TC=0.1%)\n" + "=" * 78)
    b = R["baseline"]["FULL 2014-08→now"]
    for lbl in ("double_confirm", "union"):
        f = R[lbl]["FULL 2014-08→now"]
        print(f"  {lbl:<16} dCAGR {f['cagr']-b['cagr']:+.2f}pp  dSharpe {f['sharpe']-b['sharpe']:+.2f}  "
              f"dCalmar {f['calmar']-b['calmar']:+.2f}  dMaxDD {f['maxdd']-b['maxdd']:+.1f}pp")

    # ---- TC sensitivity on UNION ----
    print("\n" + "=" * 78 + "\nTC SENSITIVITY — UNION FULL CAGR\n" + "=" * 78)
    for tc in (0.001, 0.002, 0.003):
        r, _ = sim_nav_cols(unW, unP, stock_ret, park_ret, calendar, union_names, tc=tc)
        c, sh, so, dd, cal = metrics(r)
        print(f"  TC={tc:.1%}: CAGR {c:.2f}%  Sharpe {sh:.2f}  MaxDD {dd:.1f}%  Calmar {cal:.2f}")

    # ---- CAPACITY OVERLAY @ NAV_B (ADV, live-day UNION set) ----
    print("\n" + "=" * 78 + f"\nCAPACITY @ NAV={NAV_B:.0f}B — UNION live-day set (20%-ADV build-days)\n" + "=" * 78)
    last = calendar[-1]
    live_union = sorted([tk for tk in union_names if union_M.at[last, tk]])
    n_live = len(live_union)
    w_live = min(CAP, 1.0 / n_live) if n_live else 0.0
    c = con()
    cutoff = (calendar[-1] - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
    advq = c.execute(f"""
        SELECT ticker, MEDIAN(Volume_3M_P50*Price) AS adv60
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE ticker IN ({','.join(f"'{t}'" for t in live_union) if live_union else "''"})
          AND CAST(time AS DATE) >= DATE '{cutoff}'
        GROUP BY ticker""").df()
    c.close()
    adv = dict(zip(advq["ticker"], advq["adv60"]))
    print(f"  live UNION set ({last.date()}): {n_live} names, per-name weight {w_live:.3f} "
          f"-> per-name notional {w_live*NAV_B:.3f}B")
    rowsc = []
    for tk in live_union:
        a = adv.get(tk, np.nan)
        db = (w_live * NAV_B * 1e9) / (0.20 * a) if a and np.isfinite(a) and a > 0 else np.inf
        rowsc.append((tk, a/1e9 if np.isfinite(a) else np.nan, db))
    rowsc.sort(key=lambda x: -(x[2] if np.isfinite(x[2]) else 1e9))
    print(f"  {'ticker':<8}{'ADV60_B':>10}{'build_days':>12}  flag")
    worst = 0
    for tk, a_b, db in rowsc[:12]:
        flag = "OK" if db <= 1 else ("WATCH" if db <= 3 else "BREACH")
        worst = max(worst, db if np.isfinite(db) else worst)
        print(f"  {tk:<8}{a_b:>10.2f}{db:>12.2f}  {flag}")
    nb = sum(1 for _,_,db in rowsc if db > 3); nw = sum(1 for _,_,db in rowsc if 1 < db <= 3)
    print(f"  summary @ {NAV_B:.0f}B: {nb} BREACH, {nw} WATCH, {n_live-nb-nw} OK (of {n_live} live names); "
          f"worst build-days {worst:.2f}")

    # ---- persist NAV series + summary json ----
    out = pd.DataFrame({"date": calendar, "baseline_ret": base_ret.values,
                        "double_confirm_ret": dc_ret.values, "union_ret": un_ret.values})
    out.to_csv(os.path.join(WORKDIR, "data", "converge_union_test_nav.csv"), index=False)
    summ = dict(nav_b=NAV_B, calendar=[str(calendar[0].date()), str(calendar[-1].date())],
                sessions=len(calendar), union_universe=len(union_names),
                breadth=dict(double_confirm=br_dc, buynow_arm=br_bn, union=br_un),
                metrics=R, capacity=dict(live_set=live_union, n_live=n_live,
                                         per_name_weight=round(w_live, 4), breach=nb, watch=nw,
                                         worst_build_days=round(float(worst), 2)))
    with open(os.path.join(WORKDIR, "data", "converge_union_test_summary.json"), "w") as fh:
        json.dump(summ, fh, indent=2, default=str)
    print("\nwrote data/converge_union_test_nav.csv + data/converge_union_test_summary.json")
    print(f"\nLive UNION set {last.date()} ({n_live}): {', '.join(live_union)}")
    live_dc = sorted([tk for tk in union_names if dc_M.at[last, tk]])
    print(f"Live double-confirm set {last.date()} ({len(live_dc)}): {', '.join(live_dc) or '(none)'}")


if __name__ == "__main__":
    main()
