#!/usr/bin/env python3
"""
simulate_lh_v2.py
=================
LH-system v2 — Dynamic trend-following + FA quality.

Differences from v1 (simulate_lh_nav.py):
  - NO time-stop (4Q hold removed)
  - Entry filters: FA score top 30% sub-sector + Close > MA200 + 12M ret > 0
  - Hold conditions: FA score top 70% AND no exit signal
  - Exit triggers (OR logic):
    1. FA score drops below top 70% in 2 consecutive quarters
    2. Trend break: Close < MA200 AND Close < MA50 for 5 consecutive days
    3. Trailing stop: -25% from peak (after position has +20% gain)
    4. CRISIS lock: state==1 AND position has ≥30% gain
  - Re-entry blacklist: 1 quarter (90 days)
  - Lumpy initial deploy (10 positions at first rebal)
  - Replace exited positions immediately at next quarter (or sooner if cash builds up)
"""
import warnings; warnings.filterwarnings("ignore")
import os
import numpy as np, pandas as pd
from datetime import datetime

_CACHE = {}

def load_data():
    if "ratings" not in _CACHE:
        r = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
        r["effective_release"] = r["Release_Date"].fillna(r["time"] + pd.Timedelta(days=60))
        _CACHE["ratings"] = r
    if "prices" not in _CACHE:
        p = pd.read_csv("prices_lh.csv", parse_dates=["time"])
        _CACHE["prices"] = p
    if "vnindex" not in _CACHE:
        v = pd.read_csv("vnindex_lh.csv", parse_dates=["time"])
        v = v[v["Close"] > 100].sort_values("time").reset_index(drop=True)
        _CACHE["vnindex"] = v
    return _CACHE["ratings"], _CACHE["prices"], _CACHE["vnindex"]

def quarter_to_int(q): return int(q[:4])*10 + int(q[-1])
def add_quarters(q_int, n):
    y, qn = divmod(q_int, 10)
    total = y*4 + (qn-1) + n
    ny, nqn = divmod(total, 4)
    return ny*10 + nqn + 1

def compute_metrics(nav_series, start_dt, end_dt):
    nav = nav_series.dropna()
    if len(nav) < 30:
        return {k: np.nan for k in ["CAGR","Sharpe","MaxDD","Calmar","DDdur_d"]}
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0: return {k: np.nan for k in ["CAGR","Sharpe","MaxDD","Calmar","DDdur_d"]}
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/years) - 1
    daily_ret = nav.pct_change().dropna()
    sharpe = daily_ret.mean()/daily_ret.std()*np.sqrt(len(daily_ret)/years) if daily_ret.std() > 0 else 0
    cummax = nav.cummax(); dd = nav/cummax - 1; mdd = dd.min()
    in_dd = dd < -0.001; dd_dur = 0; cur = 0
    for v in in_dd.values:
        if v: cur += 1; dd_dur = max(dd_dur, cur)
        else: cur = 0
    calmar = cagr/abs(mdd) if mdd < 0 else np.inf
    return {"CAGR":cagr,"Sharpe":sharpe,"MaxDD":mdd,"Calmar":calmar,"DDdur_d":dd_dur}

def run_lh_v2(
    n_positions=10,
    score_top_pct_entry=0.30,    # entry: top 30% by score within sub-sector
    score_top_pct_hold=0.70,     # hold while top 70%
    fa_drop_consecutive_q=2,     # require 2Q consecutive below threshold to exit
    trend_break_days=5,          # consecutive days for trend break
    trail_pct=0.25,              # trailing stop after gain trigger
    trail_activation=0.20,       # activate trail after +20% gain
    crisis_lock_gain=0.30,       # lock profit if CRISIS + gain >= 30%
    re_entry_blacklist_days=90,  # 1 quarter blacklist after exit
    require_ma200=True,          # entry: Close > MA200
    require_12m_ret_pos=True,    # entry: 12M return > 0
    crisis_gate=True,            # skip entries when state == 1
    rebal_lag_days=30,
    start="2014-04-01", end=None,
    init_nav=50e9,
    slippage_in=0.001, slippage_out=0.0015, tax_sale=0.001,
    liq_cap=0.20, max_fill_days=5,
    deposit_rate=0.01,
    verbose=False,
):
    ratings, prices, vnindex = load_data()
    if end is None: end = prices["time"].max().strftime("%Y-%m-%d")
    start_dt = pd.Timestamp(start); end_dt = pd.Timestamp(end)

    # Load 5-state
    state_lookup = None
    if crisis_gate:
        if os.path.exists("vnindex_5state.csv"):
            st = pd.read_csv("vnindex_5state.csv", parse_dates=["time"]).sort_values("time")
            state_lookup = st.set_index("time")["state"].reindex(
                pd.date_range(st["time"].min(), st["time"].max(), freq="D")).ffill()

    # FA score thresholds per (quarter, sub) for entry/hold
    # Compute pct rank within (quarter, sub) — already in `pct` column
    if "pct" not in ratings.columns:
        ratings["pct"] = ratings.groupby(["quarter","sub"])["score"].rank(pct=True)
    rt = ratings.copy()

    # Per-ticker, per-quarter pct lookup
    pct_lookup = {(r["ticker"], r["quarter"]): r["pct"] for _, r in rt.iterrows()}
    sub_lookup = {r["ticker"]: r["sub"] for _, r in rt.iterrows()}
    score_lookup = {(r["ticker"], r["quarter"]): r["score"] for _, r in rt.iterrows()}

    # Universe of all tickers with ratings
    all_tickers = sorted(rt["ticker"].unique())

    # Price + TA lookup
    px_close = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
    adv_lookup = prices.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill()
    ma200 = px_close.rolling(200, min_periods=100).mean()
    ma50 = px_close.rolling(50, min_periods=30).mean()
    ret_12m = px_close.pct_change(252)
    trading_days = px_close.index

    def next_trading_day(d):
        idx = trading_days.searchsorted(d, side="left")
        return trading_days[idx] if idx < len(trading_days) else None

    # Build quarterly rebal schedule from rating quarters
    quarters_sorted = sorted(rt["quarter"].unique())
    rebal_dates = []
    for q in quarters_sorted:
        rels = rt[rt["quarter"]==q]["effective_release"].dropna()
        if len(rels) == 0: continue
        rel_med = rels.median()
        buy_date = rel_med + pd.Timedelta(days=rebal_lag_days)
        td = next_trading_day(buy_date)
        if td is not None and start_dt <= td <= end_dt:
            rebal_dates.append((q, td))
    rebal_map = {d: q for q, d in rebal_dates}
    rebal_set = set(rebal_map.keys())

    # Portfolio state
    cash = init_nav
    positions = {}  # ticker -> {entry_dt, entry_px, shares, cost, peak_px, fa_drop_count, last_q_checked}
    nav_history = []
    trades = []
    blacklist = {}  # ticker -> blacklist_until_date

    daily_cash_rate = (1 + deposit_rate) ** (1/365.25) - 1
    all_dates = trading_days[(trading_days >= start_dt) & (trading_days <= end_dt)]

    # Pre-compute trend-break consecutive counter per ticker
    # Will compute online per position

    for dt in all_dates:
        cash *= (1 + daily_cash_rate)

        # 1) Update per-position trackers + check exit conditions DAILY
        positions_to_exit = []
        for tk, pos in positions.items():
            if tk not in px_close.columns: continue
            p_today = px_close.at[dt, tk]
            if pd.isna(p_today): continue
            # Update peak
            if p_today > pos["peak_px"]: pos["peak_px"] = p_today
            gain = (p_today / pos["entry_px"]) - 1

            exit_reason = None

            # Trigger 3: Trailing stop (after gain >20%)
            if pos["peak_px"] / pos["entry_px"] - 1 >= trail_activation:
                if p_today < pos["peak_px"] * (1 - trail_pct):
                    exit_reason = "TRAIL_STOP"

            # Trigger 2: Trend break (Close < MA200 AND Close < MA50 for 5 days)
            if exit_reason is None and tk in ma200.columns:
                ma200_v = ma200.at[dt, tk]; ma50_v = ma50.at[dt, tk]
                if pd.notna(ma200_v) and pd.notna(ma50_v):
                    if p_today < ma200_v and p_today < ma50_v:
                        pos["trend_break_count"] = pos.get("trend_break_count", 0) + 1
                        if pos["trend_break_count"] >= trend_break_days:
                            exit_reason = "TREND_BREAK"
                    else:
                        pos["trend_break_count"] = 0

            # Trigger 4: CRISIS lock-profit
            if exit_reason is None and crisis_gate and state_lookup is not None:
                cur_state = state_lookup.get(pd.Timestamp(dt.date()), 3)
                if cur_state == 1 and gain >= crisis_lock_gain:
                    exit_reason = "CRISIS_LOCK"

            if exit_reason:
                positions_to_exit.append((tk, p_today, exit_reason))

        # Execute exits
        for tk, p_today, reason in positions_to_exit:
            pos = positions[tk]
            gross = pos["shares"] * p_today * (1 - slippage_out)
            net = gross * (1 - tax_sale)
            cash += net
            trades.append({"dt":dt, "ticker":tk, "side":reason, "shares":pos["shares"],
                            "px":p_today, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"]})
            blacklist[tk] = dt + pd.Timedelta(days=re_entry_blacklist_days)
            del positions[tk]

        # 2) At rebal date: check FA degradation + add new picks
        if dt in rebal_set:
            q_now = rebal_map[dt]

            # Trigger 1: FA degradation check for existing positions
            fa_exits = []
            for tk, pos in positions.items():
                pct = pct_lookup.get((tk, q_now), None)
                if pct is None or pct < score_top_pct_hold:
                    pos["fa_drop_count"] = pos.get("fa_drop_count", 0) + 1
                    if pos["fa_drop_count"] >= fa_drop_consecutive_q:
                        fa_exits.append(tk)
                else:
                    pos["fa_drop_count"] = 0
            for tk in fa_exits:
                pos = positions[tk]
                if tk not in px_close.columns: continue
                p_today = px_close.at[dt, tk]
                if pd.isna(p_today): continue
                gross = pos["shares"] * p_today * (1 - slippage_out)
                net = gross * (1 - tax_sale)
                cash += net
                trades.append({"dt":dt, "ticker":tk, "side":"FA_DROP", "shares":pos["shares"],
                                "px":p_today, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"]})
                blacklist[tk] = dt + pd.Timedelta(days=re_entry_blacklist_days)
                del positions[tk]

            # Get candidate picks for this quarter (top score_top_pct_entry per sub)
            q_picks = rt[(rt["quarter"]==q_now) & (rt["pct"] >= 1 - score_top_pct_entry)]
            q_picks = q_picks.sort_values("score", ascending=False)

            # CRISIS gate: skip new buys if state==1
            skip_buys = False
            if crisis_gate and state_lookup is not None:
                cur_state = state_lookup.get(pd.Timestamp(dt.date()), 3)
                if cur_state == 1:
                    skip_buys = True

            if not skip_buys:
                current_tickers = set(positions.keys())
                slots_open = n_positions - len(positions)
                nav_now = cash + sum(pos["shares"] * (px_close.at[dt, tk_pos] if tk_pos in px_close.columns and pd.notna(px_close.at[dt, tk_pos]) else 0)
                                      for tk_pos, pos in positions.items())
                target_per_pos = (nav_now / n_positions) * 0.99

                new_buys = []
                for _, row in q_picks.iterrows():
                    if slots_open <= 0: break
                    tk = row["ticker"]
                    if tk in current_tickers: continue
                    # Blacklist check
                    if tk in blacklist and blacklist[tk] > dt: continue
                    if tk not in px_close.columns: continue
                    px_today = px_close.at[dt, tk]
                    if pd.isna(px_today) or px_today <= 0: continue

                    # Entry filter: Close > MA200
                    if require_ma200 and tk in ma200.columns:
                        ma200_v = ma200.at[dt, tk]
                        if pd.notna(ma200_v) and px_today < ma200_v: continue

                    # Entry filter: 12M return > 0
                    if require_12m_ret_pos and tk in ret_12m.columns:
                        r12 = ret_12m.at[dt, tk]
                        if pd.notna(r12) and r12 < 0: continue

                    new_buys.append((tk, px_today))
                    slots_open -= 1

                # Execute buys
                for tk, px_today in new_buys:
                    adv_today = adv_lookup.at[dt, tk] if tk in adv_lookup.columns else np.nan
                    if pd.isna(adv_today) or adv_today <= 0: adv_today = 1e6
                    max_pos_vnd = liq_cap * adv_today * max_fill_days * px_today
                    alloc = min(target_per_pos, max_pos_vnd)
                    if alloc < 1e6: continue
                    eff_px = px_today * (1 + slippage_in)
                    shares = alloc / eff_px
                    cost = shares * eff_px
                    if cost > cash: continue
                    cash -= cost
                    positions[tk] = {"entry_dt":dt, "entry_px":px_today, "shares":shares,
                                      "cost":cost, "peak_px":px_today, "fa_drop_count":0,
                                      "trend_break_count":0}
                    trades.append({"dt":dt, "ticker":tk, "side":"BUY", "shares":shares,
                                    "px":px_today, "net":-cost, "entry_dt":dt, "entry_px":px_today})

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
        print(f"\nLH v2c: CAGR={metrics['CAGR']*100:.2f}%, Sharpe={metrics['Sharpe']:.2f}, "
              f"DD={metrics['MaxDD']*100:.2f}%, avg_pos={metrics['avg_n_pos']:.2f}, n_trades={len(trades)}")

    return {"metrics":metrics, "nav":nav_df, "trades":pd.DataFrame(trades)}


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

    print("=== LH v2c: Dynamic trend-following + FA ===")
    res = run_lh_v2(verbose=True, init_nav=50e9)

    # Slice metrics
    nav = res["nav"]["nav"]
    for label, ws, we in [("FULL", "2014-04-01", "2026-05-13"),
                            ("OOS_2024+", "2024-01-01", "2026-05-13"),
                            ("Y2022", "2022-01-01", "2022-12-31"),
                            ("Q1_2026", "2025-12-30", "2026-03-30")]:
        s = nav[(nav.index >= ws) & (nav.index <= we)]
        if len(s) < 30: continue
        m = compute_metrics(50e9 * s/s.iloc[0], pd.Timestamp(ws), pd.Timestamp(we))
        print(f"  {label:<10}: CAGR={m['CAGR']*100:+.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['MaxDD']*100:+.2f}%")

    # Exit reason breakdown
    tr = res["trades"]
    print(f"\nExit reasons:")
    print(tr["side"].value_counts().to_string())

    # 5-ticker lifecycle
    print("\n=== 5-TICKER LIFECYCLE ===")
    CASES = ["VCS","DGC","VNM","FPT","MWG"]
    prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])
    for tk in CASES:
        p = prices[prices["ticker"]==tk].sort_values("time")
        peak_dt = p.loc[p["Close"].idxmax(), "time"]
        peak_px = p["Close"].max()
        tk_tr = tr[tr["ticker"]==tk].sort_values("dt")
        if len(tk_tr) == 0:
            print(f"\n{tk}: not picked")
            continue
        print(f"\n{tk} (peak {peak_px:.0f} on {peak_dt.date()}):")
        for _, t in tk_tr.iterrows():
            offset = (t["dt"] - peak_dt).days
            print(f"  {t['dt'].strftime('%Y-%m-%d')}  {t['side']:<12}{t['px']:>8.0f}  (peak{offset:+d}d)")
