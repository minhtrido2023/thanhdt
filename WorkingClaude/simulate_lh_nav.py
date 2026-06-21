#!/usr/bin/env python3
"""
simulate_lh_nav.py
==================
Long-hold FA portfolio backtest. Equal-weight A-tier (or A+B) picks from fa_ratings_lh,
quarterly rebalance, configurable hold horizon.

Inputs:  fa_ratings_lh.csv, prices_lh.csv, vnindex_lh.csv
Output:  NAV series, trades log, summary metrics
Entry:   run_lh(...) returns dict of metrics + nav series
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from datetime import datetime

# --- I/O cache ---
_CACHE = {}
def load_data():
    if "ratings" not in _CACHE:
        r = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
        # When Release_Date missing, fallback = quarter end + 60 days (typical VN report deadline)
        r["effective_release"] = r["Release_Date"].fillna(r["time"] + pd.Timedelta(days=60))
        _CACHE["ratings"] = r
    if "prices" not in _CACHE:
        p = pd.read_csv("data/prices_lh.csv", parse_dates=["time"])
        _CACHE["prices"] = p
    if "vnindex" not in _CACHE:
        v = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
        v = v[v["Close"] > 100].sort_values("time").reset_index(drop=True)
        _CACHE["vnindex"] = v
    return _CACHE["ratings"], _CACHE["prices"], _CACHE["vnindex"]

# --- Quarter helpers ---
def quarter_to_int(q):  # "2014Q1" -> 20141
    return int(q[:4])*10 + int(q[-1])

def add_quarters(q_int, n):  # 20141 + 3 = 20144
    y, qn = divmod(q_int, 10)
    total = y*4 + (qn-1) + n
    ny, nqn = divmod(total, 4)
    return ny*10 + nqn + 1

# --- Metrics ---
def compute_metrics(nav_series, start_dt, end_dt):
    nav = nav_series.dropna()
    if len(nav) < 30:
        return {k: np.nan for k in ["CAGR","Sharpe","MaxDD","Calmar","DDdur_d"]}
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0: return {k: np.nan for k in ["CAGR","Sharpe","MaxDD","Calmar","DDdur_d"]}
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/years) - 1
    daily_ret = nav.pct_change().dropna()
    if daily_ret.std() > 0:
        sessions_per_year = len(daily_ret) / years
        sharpe = daily_ret.mean() / daily_ret.std() * np.sqrt(sessions_per_year)
    else: sharpe = 0
    cummax = nav.cummax(); dd = nav/cummax - 1; mdd = dd.min()
    in_dd = dd < -0.001; dd_dur = 0; cur = 0
    for v in in_dd.values:
        if v: cur += 1; dd_dur = max(dd_dur, cur)
        else: cur = 0
    calmar = cagr / abs(mdd) if mdd < 0 else np.inf
    return {"CAGR":cagr,"Sharpe":sharpe,"MaxDD":mdd,"Calmar":calmar,"DDdur_d":dd_dur}

# --- Core simulator ---
def run_lh(
    hold_quarters=4,            # 1, 2, 4, 8
    n_positions=10,
    tier_set=("A",),
    incl_sub="all",             # "all" | "excl_reit" | "excl_all_re"
    rebal_lag_days=30,
    start="2014-04-01",         # ~3 months in to wait for first Release_Date
    end=None,
    init_nav=50e9,
    slippage_in=0.001,
    slippage_out=0.0015,
    tax_sale=0.001,
    liq_cap=0.20,               # max 20% ADV/day
    max_fill_days=5,
    deposit_rate=0.01,          # 1% annual on idle cash
    refresh_mode="staggered",   # "staggered" | "lumpy" | "hybrid_init" (lumpy first rebal, staggered after)
    crisis_gate=False,          # if True: skip new buys when 5-state == 1 (CRISIS)
    trail_pct=None,             # if set (e.g. 0.30), exit position when price drops X% from intra-hold peak
    ta_filter=None,             # dict with optional: ma200_gate (Close > MA200 × thresh), ret6m_min, ret1y_min
    growth_exclude=None,        # dict with optional: np_yoy_min, np_growth_floor (excludes from new buys)
    verbose=False,
):
    ratings, prices, vnindex = load_data()
    if end is None: end = prices["time"].max().strftime("%Y-%m-%d")
    start_dt = pd.Timestamp(start); end_dt = pd.Timestamp(end)

    # Load 5-state for crisis gate (smoothed state)
    # AND-gate (smoothed AND raw) tested but worse 12y (CAGR 10.05% vs 11.53% smoothed-only)
    # — accept smoothing lag, lose some Q3 cohort in rare CRISIS-lag windows
    state_lookup = None
    if crisis_gate:
        import os
        if os.path.exists("data/vnindex_5state.csv"):
            st = pd.read_csv("data/vnindex_5state.csv", parse_dates=["time"]).sort_values("time")
            state_lookup = st.set_index("time")["state"].reindex(
                pd.date_range(st["time"].min(), st["time"].max(), freq="D")).ffill()
        else:
            print("WARN: vnindex_5state.csv not found, crisis_gate disabled")
            crisis_gate = False

    # Sector filter
    if incl_sub == "excl_reit":
        ratings = ratings[~ratings["sub"].isin(["REIT"])]
    elif incl_sub == "excl_all_re":
        ratings = ratings[~ratings["sub"].isin(["REIT","REIT_RES"])]
    ratings = ratings[ratings["tier"].isin(tier_set)].copy()

    # Build per-quarter pick lists - sorted by score desc within sub-sector blend
    ratings = ratings.sort_values(["quarter","score"], ascending=[True, False])
    picks_by_quarter = {q: g[["ticker","score","sub","Volume_3M_P50","effective_release"]].to_dict("records")
                        for q, g in ratings.groupby("quarter")}

    # Build price lookup
    px = prices.set_index(["ticker","time"]).sort_index()
    px_close = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first")
    px_close = px_close.sort_index().ffill()
    trading_days = px_close.index
    adv_lookup = prices.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first")
    adv_lookup = adv_lookup.sort_index().ffill()

    # Pre-compute TA indicators if needed
    ma200 = ma50 = ret_6m = ret_1y = None
    if ta_filter is not None:
        ma200 = px_close.rolling(200, min_periods=100).mean()
        ma50 = px_close.rolling(50, min_periods=30).mean()
        ret_6m = px_close.pct_change(125)  # ~6M
        ret_1y = px_close.pct_change(252)  # ~1Y

    # Optional growth-exclude lookup from ratings_meta
    growth_lookup = None
    if growth_exclude is not None:
        # Build lookup: (ticker, quarter) -> np_yoy growth
        # Compute NP_TTM and growth from raw ratings file (need to re-pull from BQ)
        try:
            growth_df = pd.read_csv("data/research_peg_decel_panel.csv", usecols=["ticker","quarter","NP_growth_yoy"])
            growth_lookup = {(r["ticker"], r["quarter"]): r["NP_growth_yoy"] for _, r in growth_df.iterrows()}
        except FileNotFoundError:
            print("WARN: growth panel not found; disabling growth_exclude")
            growth_exclude = None

    def next_trading_day(d):
        idx = trading_days.searchsorted(d, side="left")
        if idx >= len(trading_days): return None
        return trading_days[idx]

    # Rebalance schedule: for each quarter Q, buy on effective_release + lag_days
    quarters_sorted = sorted(picks_by_quarter.keys())
    rebal_dates = []
    for q in quarters_sorted:
        rels = [p["effective_release"] for p in picks_by_quarter[q] if pd.notna(p["effective_release"])]
        if not rels: continue
        # use median release date for quarter (different tickers report on different days)
        rel_med = pd.Series(rels).median()
        buy_date = rel_med + pd.Timedelta(days=rebal_lag_days)
        td = next_trading_day(buy_date)
        if td is not None and start_dt <= td <= end_dt:
            rebal_dates.append((q, td))

    # Portfolio state
    cash = init_nav
    positions = {}  # ticker -> dict(shares, buy_dt, expiry_quarter)
    nav_history = []  # (date, nav)
    trades = []  # log

    # Daily walk
    all_dates = trading_days[(trading_days >= start_dt) & (trading_days <= end_dt)]
    rebal_map = dict(rebal_dates)
    rebal_dates_set = set(rebal_map.values())

    daily_cash_rate = (1 + deposit_rate) ** (1/365.25) - 1

    for dt in all_dates:
        # 1) Accrue interest on cash
        cash *= (1 + daily_cash_rate)

        # 2) Check rebal
        if dt in rebal_dates_set:
            q_now = [q for q,d in rebal_dates if d == dt][0]
            q_now_int = quarter_to_int(q_now)

            # 2a) Sell expired
            to_sell = []
            for tk, pos in positions.items():
                if quarter_to_int(pos["expiry_quarter"]) <= q_now_int:
                    to_sell.append(tk)
            for tk in to_sell:
                pos = positions[tk]
                if tk not in px_close.columns: continue
                p = px_close.at[dt, tk]
                if pd.isna(p): continue
                gross = pos["shares"] * p * (1 - slippage_out)
                net = gross * (1 - tax_sale)
                cash += net
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","shares":pos["shares"],"px":p,"net":net,"q":q_now})
                del positions[tk]

            # CRISIS gate: skip new buys if state == 1 today; expired sells still happen
            skip_buys = False
            if crisis_gate and state_lookup is not None:
                cur_state = state_lookup.get(pd.Timestamp(dt.date()), 3)
                if cur_state == 1:
                    skip_buys = True

            # 2b) Buy new picks - staggered: cap at n_positions/hold_quarters per rebal
            picks = [] if skip_buys else picks_by_quarter[q_now]
            current_tickers = set(positions.keys())
            slots_total_open = n_positions - len(positions)
            if refresh_mode == "staggered":
                max_buys_this_rebal = max(1, int(np.ceil(n_positions / hold_quarters)))
                slots_open = min(slots_total_open, max_buys_this_rebal)
            elif refresh_mode == "hybrid_init":
                # First rebal: fill all (lumpy). After: staggered cap.
                if len(positions) == 0 and len(trades) == 0:
                    # First-ever rebal — lumpy fill
                    slots_open = slots_total_open
                else:
                    max_buys_this_rebal = max(1, int(np.ceil(n_positions / hold_quarters)))
                    slots_open = min(slots_total_open, max_buys_this_rebal)
            else:  # lumpy: fill any open slots
                slots_open = slots_total_open
            new_buys = []
            for p in picks:
                if slots_open <= 0: break
                tk = p["ticker"]
                if tk in current_tickers: continue
                if tk not in px_close.columns: continue
                px_today = px_close.at[dt, tk]
                if pd.isna(px_today) or px_today <= 0: continue

                # TA momentum filter
                if ta_filter is not None:
                    if "ma200_thresh" in ta_filter and ma200 is not None:
                        ma_v = ma200.at[dt, tk] if tk in ma200.columns else np.nan
                        if pd.notna(ma_v) and px_today < ma_v * ta_filter["ma200_thresh"]:
                            continue
                    if "ret6m_min" in ta_filter and ret_6m is not None:
                        r6 = ret_6m.at[dt, tk] if tk in ret_6m.columns else np.nan
                        if pd.notna(r6) and r6 < ta_filter["ret6m_min"]:
                            continue
                    if "ret1y_min" in ta_filter and ret_1y is not None:
                        r1 = ret_1y.at[dt, tk] if tk in ret_1y.columns else np.nan
                        if pd.notna(r1) and r1 < ta_filter["ret1y_min"]:
                            continue
                    if "ma50_thresh" in ta_filter and ma50 is not None:
                        m50 = ma50.at[dt, tk] if tk in ma50.columns else np.nan
                        if pd.notna(m50) and px_today < m50 * ta_filter["ma50_thresh"]:
                            continue

                # Growth exclude filter
                if growth_exclude is not None and growth_lookup is not None:
                    g = growth_lookup.get((tk, q_now), None)
                    if g is not None:
                        if "np_yoy_min" in growth_exclude and g < growth_exclude["np_yoy_min"]:
                            continue

                new_buys.append((tk, px_today, p))
                slots_open -= 1

            if new_buys:
                # Equal-weight allocation: each position targets NAV / n_positions (fixed)
                # This avoids over-concentration in early-cohort positions during ramp
                nav_pre = cash + sum(pos["shares"] * (px_close.at[dt, tk_pos] if tk_pos in px_close.columns and pd.notna(px_close.at[dt, tk_pos]) else 0)
                                      for tk_pos, pos in positions.items())
                target_per_pos = (nav_pre / n_positions) * 0.99  # 1% buffer

                for tk, px_today, info in new_buys:
                    adv_today = adv_lookup.at[dt, tk] if tk in adv_lookup.columns else np.nan
                    if pd.isna(adv_today) or adv_today <= 0: adv_today = 1e6
                    # Liq cap: max 20% ADV * 5 days * Close VND
                    max_position_vnd = liq_cap * adv_today * max_fill_days * px_today
                    alloc = min(target_per_pos, max_position_vnd)
                    if alloc < 1e6: continue  # too small
                    eff_px = px_today * (1 + slippage_in)
                    shares = alloc / eff_px
                    cost = shares * eff_px
                    if cost > cash: continue
                    cash -= cost
                    expiry_q = add_quarters(q_now_int, hold_quarters)
                    expiry_str = f"{expiry_q//10}Q{expiry_q%10}"
                    positions[tk] = {"shares":shares, "buy_dt":dt, "expiry_quarter":expiry_str,
                                      "cost":cost, "peak_px":px_today}
                    trades.append({"dt":dt,"ticker":tk,"side":"BUY","shares":shares,"px":px_today,"net":-cost,"q":q_now})

        # 2.5) Trailing stop check: update peak, exit if drawdown > trail_pct
        if trail_pct is not None and len(positions) > 0:
            trail_exits = []
            for tk, pos in positions.items():
                if tk not in px_close.columns: continue
                p_today = px_close.at[dt, tk]
                if pd.isna(p_today): continue
                # Update peak
                if p_today > pos["peak_px"]: pos["peak_px"] = p_today
                # Check trail
                if p_today < pos["peak_px"] * (1 - trail_pct):
                    trail_exits.append((tk, p_today))
            for tk, p_today in trail_exits:
                pos = positions[tk]
                gross = pos["shares"] * p_today * (1 - slippage_out)
                net = gross * (1 - tax_sale)
                cash += net
                trades.append({"dt":dt,"ticker":tk,"side":"TRAIL_STOP","shares":pos["shares"],"px":p_today,"net":net,"q":"trail"})
                del positions[tk]

        # 3) Mark to market
        mtm = 0
        for tk, pos in positions.items():
            if tk in px_close.columns:
                p = px_close.at[dt, tk]
                if pd.notna(p): mtm += pos["shares"] * p
        nav = cash + mtm
        nav_history.append((dt, nav, cash, mtm, len(positions)))

    nav_df = pd.DataFrame(nav_history, columns=["date","nav","cash","equity","n_pos"]).set_index("date")
    metrics = compute_metrics(nav_df["nav"], start_dt, end_dt)
    metrics["n_trades"] = len(trades)
    metrics["avg_n_pos"] = nav_df["n_pos"].mean()

    if verbose:
        print(f"\nRun: hold={hold_quarters}Q n={n_positions} tier={tier_set} sub={incl_sub}")
        for k,v in metrics.items():
            if isinstance(v, float):
                print(f"  {k:>12}: {v:+.4f}" if abs(v)<10 else f"  {k:>12}: {v:.1f}")
            else:
                print(f"  {k:>12}: {v}")

    return {"metrics":metrics, "nav":nav_df, "trades":pd.DataFrame(trades)}

# --- VNINDEX B&H benchmark ---
def run_vnindex_bh(start="2014-04-01", end=None, init_nav=50e9):
    _, _, vn = load_data()
    if end is None: end = vn["time"].max().strftime("%Y-%m-%d")
    s = vn[(vn["time"]>=start) & (vn["time"]<=end)].sort_values("time").set_index("time")["Close"]
    nav = init_nav * s / s.iloc[0]
    return {"metrics": compute_metrics(nav, pd.Timestamp(start), pd.Timestamp(end)), "nav": nav}

if __name__ == "__main__":
    # Quick smoke test
    res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A",), verbose=True)
    bh = run_vnindex_bh()
    print("\nVNINDEX B&H:", bh["metrics"])
