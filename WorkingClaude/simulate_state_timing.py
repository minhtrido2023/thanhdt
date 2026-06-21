# -*- coding: utf-8 -*-
"""
simulate_state_timing.py
========================
Standalone VNINDEX market timing simulation.

Given a 5-state series (CSV with columns: time, state),
simulate a 1B VND portfolio that tracks the VNINDEX index with
state-dependent equity allocation:
  CRISIS(1): 0%   BEAR(2): 20%   NEUTRAL(3): 70%   BULL(4): 100%   EX-BULL(5): 130%

Mechanics:
  - T+1 execution: state on day T → weight from day T+1
  - ramp: weight adjusts immediately each day (no ramp, 1-day snap)
  - TC = 0.10% on |Δweight| per day
  - Deposit = 6%/yr on idle cash fraction (when w < 1)
  - Borrow = 10%/yr on leverage (when w > 1, i.e. EX-BULL)
  - VNINDEX daily return used as market return

Usage:
  from simulate_state_timing import simulate_timing, STATE_ALLOC
  result = simulate_timing(state_csv_path, start_date="2014-01-01")
  print(result)
"""
import sys, io
import numpy as np, pandas as pd, os

WORKDIR   = r"/home/trido/thanhdt/WorkingClaude"
STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
TC_RATE     = 0.001    # 0.1% per unit of weight change
DEPOSIT_APY = 0.06     # 6%/yr on idle cash
BORROW_APY  = 0.10     # 10%/yr on leverage
INIT_NAV    = 1_000_000_000  # 1B VND


def simulate_timing(state_df_or_path, start_date="2014-01-01", end_date=None,
                    tc=TC_RATE, deposit_apy=DEPOSIT_APY, borrow_apy=BORROW_APY,
                    state_col="state", alloc=None):
    """
    Parameters
    ----------
    state_df_or_path : str or DataFrame
        Path to CSV (columns: time, state) or DataFrame
    start_date : str, e.g. "2014-01-01"
    end_date   : str, optional
    tc         : float, transaction cost per unit Δweight
    deposit_apy: float
    borrow_apy : float
    state_col  : str, column name for state in DataFrame
    alloc      : dict mapping state→weight (default: STATE_ALLOC)

    Returns
    -------
    dict with keys: final_nav, cagr, sharpe, sortino, max_dd, calmar,
                    nav_series, weight_series
    """
    if alloc is None:
        alloc = STATE_ALLOC

    # --- Load state data ---
    if isinstance(state_df_or_path, str):
        st = pd.read_csv(state_df_or_path)
    else:
        st = state_df_or_path.copy()
    st["time"] = pd.to_datetime(st["time"])
    st = st.sort_values("time").reset_index(drop=True)

    # --- Load VNINDEX ---
    vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), usecols=["time","Close"])
    vni["time"] = pd.to_datetime(vni["time"])
    vni = vni.sort_values("time").reset_index(drop=True)

    # --- Merge ---
    df = vni.merge(st[["time", state_col]], on="time", how="inner")
    df = df.dropna(subset=[state_col]).reset_index(drop=True)

    # Apply date filter
    if start_date:
        df = df[df["time"] >= start_date].reset_index(drop=True)
    if end_date:
        df = df[df["time"] <= end_date].reset_index(drop=True)
    if len(df) < 20:
        raise ValueError(f"Too few rows after date filter: {len(df)}")

    # --- Compute VNINDEX daily returns ---
    close = df["Close"].values
    ret_vni = np.zeros(len(df))
    ret_vni[1:] = close[1:] / close[:-1] - 1

    # --- Actual trading days per year (important for correct annualization) ---
    years = (df["time"].iloc[-1] - df["time"].iloc[0]).days / 365.25
    spy = len(df) / years  # sessions per year

    # --- T+1 state lag: state on day t → weight applied from day t+1 ---
    n = len(df)
    state_list  = list(df[state_col].values)
    weight_list = [alloc.get(int(s), 0.0) for s in state_list]

    # Effective weight at day t = weight from state seen at day t-1
    eff_w_list  = [0.0] + weight_list[:-1]   # length = n

    # --- Simulate NAV (loop for clarity) ---
    nav_list  = [float(INIT_NAV)] * n
    dr_list   = [0.0] * n

    for t in range(n):
        w      = eff_w_list[t]
        w_prev = eff_w_list[t-1] if t > 0 else 0.0
        r      = float(ret_vni[t])
        dw     = abs(w - w_prev)
        c_frac = max(0.0, 1.0 - w)
        l_frac = max(0.0, w - 1.0)
        daily_ret = (w * r
                     + c_frac * deposit_apy / spy
                     - l_frac * borrow_apy  / spy
                     - dw * tc)
        dr_list[t] = daily_ret
        if t > 0:
            nav_list[t] = nav_list[t-1] * (1.0 + daily_ret)

    daily_returns = np.array(dr_list)
    nav_arr       = np.array(nav_list)
    nav_series    = pd.Series(nav_arr, index=df["time"])
    final_nav     = nav_arr[-1]

    # --- Performance metrics ---
    cagr = (final_nav / INIT_NAV) ** (1 / years) - 1

    # Sharpe (annualized)
    rf_daily = deposit_apy / spy
    excess   = daily_returns - rf_daily
    sharpe   = excess.mean() / excess.std() * np.sqrt(spy) if excess.std() > 0 else 0.0

    # Sortino (downside std)
    downside = excess[excess < 0]
    sortino  = excess.mean() / downside.std() * np.sqrt(spy) if len(downside) > 0 and downside.std() > 0 else 0.0

    # MaxDD
    running_max = np.maximum.accumulate(nav_arr)
    dd_series   = (nav_arr - running_max) / running_max
    max_dd      = dd_series.min()
    calmar      = cagr / (-max_dd) if max_dd < 0 else np.inf

    return {
        "final_nav":    final_nav,
        "cagr":         cagr,
        "sharpe":       sharpe,
        "sortino":      sortino,
        "max_dd":       max_dd,
        "calmar":       calmar,
        "years":        years,
        "nav_series":   nav_series,
        "weight_series": pd.Series(eff_w_list, index=df["time"]),
    }


def print_result(label, res, ref=None):
    """Print formatted result row, optionally with delta vs ref."""
    nav_m = res["final_nav"] / 1e9  # in billions
    cagr  = res["cagr"]  * 100
    sh    = res["sharpe"]
    dd    = res["max_dd"] * 100
    cal   = res["calmar"]
    line  = f"  {label:<25} NAV={nav_m:.3f}B  CAGR={cagr:+.2f}%  Sh={sh:.2f}  DD={dd:.1f}%  Cal={cal:.2f}"
    if ref:
        dcagr = (res["cagr"] - ref["cagr"]) * 100
        dsh   = res["sharpe"]  - ref["sharpe"]
        ddd   = (res["max_dd"] - ref["max_dd"]) * 100
        dcal  = res["calmar"]  - ref["calmar"]
        line += f"  | ΔCAGR={dcagr:+.2f}pp  ΔSh={dsh:+.2f}  ΔDD={ddd:+.1f}pp  ΔCal={dcal:+.2f}"
    print(line)


# ----- If run as main: benchmark TQ34b vs baseline -----
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("="*70)
    print("  VNINDEX Timing Standalone Simulation (1B VND, 2014-2026)")
    print("="*70)

    start = "2014-01-01"
    tq_path = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")

    # Buy-and-hold benchmark (state=4 all days = 100% VNINDEX)
    tq = pd.read_csv(tq_path)
    bh = pd.DataFrame({"time": tq["time"], "state": 4})
    res_bh = simulate_timing(bh, start_date=start)
    print(f"\n[Benchmark since {start}]")
    print_result("Buy&Hold (100% VNI)", res_bh)

    # TQ34b
    res_tq = simulate_timing(tq_path, start_date=start)
    print_result("TQ34b", res_tq, ref=res_bh)

    # v3.5 if available
    v35 = os.path.join(WORKDIR, "data/vnindex_5state_v35_macro_floor.csv")
    if os.path.exists(v35):
        res_v35 = simulate_timing(v35, start_date=start)
        print_result("v3.5 macro floor", res_v35, ref=res_tq)

    # v3.6 if available
    v36 = os.path.join(WORKDIR, "data/vnindex_5state_v36_smart_floor.csv")
    if os.path.exists(v36):
        res_v36 = simulate_timing(v36, start_date=start)
        print_result("v3.6 smart floor", res_v36, ref=res_tq)

    # Annual breakdown for TQ34b
    nav_s = res_tq["nav_series"]
    print(f"\n[TQ34b annual breakdown vs Buy&Hold]")
    print(f"  {'Year':<6} {'TQ34b':>8} {'B&H':>8} {'Delta':>8}")
    nav_bh_s = res_bh["nav_series"]
    years_list = sorted(nav_s.index.year.unique())
    for yr in years_list:
        yr_mask = nav_s.index.year == yr
        if yr_mask.sum() < 5: continue
        nav_yr = nav_s[yr_mask]
        nav_bh_yr = nav_bh_s[nav_bh_s.index.year == yr]
        if len(nav_bh_yr) < 5: continue
        # year return
        ret_tq = nav_yr.iloc[-1] / nav_yr.iloc[0] - 1
        ret_bh = nav_bh_yr.iloc[-1] / nav_bh_yr.iloc[0] - 1
        print(f"  {yr:<6} {ret_tq*100:>+7.1f}%  {ret_bh*100:>+7.1f}%  {(ret_tq-ret_bh)*100:>+7.1f}pp")
