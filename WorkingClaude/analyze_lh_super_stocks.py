#!/usr/bin/env python3
"""
analyze_lh_super_stocks.py
==========================
Find the "super compounders" — stocks that LH system held longest with biggest returns.

Methodology:
  1) Run LH v1 baseline (v8c tier) and LH v3-C16 hybrid full 12y backtest
  2) For each ticker, aggregate ALL trades (each cohort entry/exit)
  3) Compute:
     - Total realized return (sum of all completed trade returns)
     - Hold time per cohort
     - Number of times re-entered
     - Cumulative hold duration
  4) Rank by total $ gain and CAGR-equivalent
  5) Cross-reference with FA score consistency (how many quarters at top)
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, _CACHE

INIT_NAV = 50e9

# Run LH v1 baseline
print("Running LH v1 baseline (v8c tier) — full 12y backtest ...")
_CACHE.clear()
res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
              refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

trades = res["trades"].copy()
trades["dt"] = pd.to_datetime(trades["dt"])
print(f"Total trades: {len(trades)} ({(trades['side']=='BUY').sum()} buys / {(trades['side'].isin(['SELL','TRAIL_STOP'])).sum()} sells)")

# Match BUY and SELL pairs to compute per-trade return
buys = trades[trades["side"]=="BUY"].copy().reset_index(drop=True)
sells = trades[trades["side"].isin(["SELL","TRAIL_STOP"])].copy().reset_index(drop=True)

# For each ticker, match sequential buys with sells
trade_pairs = []
for tk in buys["ticker"].unique():
    tk_buys = buys[buys["ticker"]==tk].sort_values("dt").reset_index(drop=True)
    tk_sells = sells[sells["ticker"]==tk].sort_values("dt").reset_index(drop=True)
    for i, b in tk_buys.iterrows():
        # Find next sell after this buy
        future_sells = tk_sells[tk_sells["dt"] > b["dt"]]
        if len(future_sells) > 0:
            s = future_sells.iloc[0]
            tk_sells = tk_sells[tk_sells["dt"] > s["dt"]]  # remove used sell
            trade_pairs.append({
                "ticker": tk,
                "entry_dt": b["dt"], "entry_px": b["px"], "shares": b["shares"],
                "exit_dt": s["dt"], "exit_px": s["px"], "exit_side": s["side"],
                "hold_days": (s["dt"] - b["dt"]).days,
                "ret_gross_pct": (s["px"]/b["px"] - 1) * 100,
                "pnl_vnd": (s["px"] - b["px"]) * b["shares"],
                "status": "CLOSED",
            })
        else:
            # Still open at end of sim
            trade_pairs.append({
                "ticker": tk,
                "entry_dt": b["dt"], "entry_px": b["px"], "shares": b["shares"],
                "exit_dt": None, "exit_px": None, "exit_side": "OPEN",
                "hold_days": None, "ret_gross_pct": None, "pnl_vnd": None,
                "status": "OPEN",
            })

tp_df = pd.DataFrame(trade_pairs)
print(f"Trade pairs: {len(tp_df)} (closed: {(tp_df['status']=='CLOSED').sum()}, open: {(tp_df['status']=='OPEN').sum()})")

# For open trades, mark-to-market with latest price
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])
latest_px = prices.sort_values("time").groupby("ticker")["Close"].last()
for i, row in tp_df.iterrows():
    if row["status"] == "OPEN":
        tk = row["ticker"]
        if tk in latest_px.index:
            cur = latest_px[tk]
            tp_df.at[i, "exit_px"] = cur
            tp_df.at[i, "exit_dt"] = prices["time"].max()
            tp_df.at[i, "hold_days"] = (prices["time"].max() - row["entry_dt"]).days
            tp_df.at[i, "ret_gross_pct"] = (cur / row["entry_px"] - 1) * 100
            tp_df.at[i, "pnl_vnd"] = (cur - row["entry_px"]) * row["shares"]

tp_df["hold_years"] = tp_df["hold_days"] / 365.25
tp_df["cagr_pct"] = tp_df.apply(
    lambda r: ((1 + r["ret_gross_pct"]/100) ** (1/max(r["hold_years"], 0.1)) - 1) * 100
    if pd.notna(r["ret_gross_pct"]) else None, axis=1)

# Aggregate by ticker
ticker_summary = tp_df.groupby("ticker").agg(
    n_trades=("ticker","size"),
    total_ret_pct=("ret_gross_pct","sum"),
    avg_ret_pct=("ret_gross_pct","mean"),
    best_single_ret=("ret_gross_pct","max"),
    worst_single_ret=("ret_gross_pct","min"),
    total_hold_days=("hold_days","sum"),
    max_hold_days=("hold_days","max"),
    total_pnl_vnd=("pnl_vnd","sum"),
    first_entry=("entry_dt","min"),
    last_exit=("exit_dt","max"),
    avg_cagr=("cagr_pct","mean"),
).sort_values("total_pnl_vnd", ascending=False)

# Top 25 by total PnL
print("\n" + "="*120)
print("  TOP 25 BY TOTAL PnL (LH v1 baseline 50B 12y backtest)")
print("="*120)
print(f"\n  {'Ticker':<7}{'N':>3}{'Tot PnL (M)':>13}{'Tot Ret%':>10}{'Avg Ret%':>10}{'Best%':>9}{'Hold days':>11}{'Max hold y':>12}{'First entry':>13}{'Last exit':>13}")
for tk, r in ticker_summary.head(25).iterrows():
    print(f"  {tk:<7}{int(r['n_trades']):>3}{r['total_pnl_vnd']/1e6:>+12.1f}M{r['total_ret_pct']:>+9.1f}%{r['avg_ret_pct']:>+9.1f}%{r['best_single_ret']:>+8.1f}%{int(r['total_hold_days']):>11}{r['max_hold_days']/365.25:>11.2f}y  {r['first_entry'].strftime('%Y-%m'):>11} {r['last_exit'].strftime('%Y-%m'):>11}")

# Top 15 by single best trade return
print("\n" + "="*120)
print("  TOP 15 SINGLE-TRADE WINNERS (multi-bagger picks)")
print("="*120)
print(f"\n  {'Ticker':<7}{'Entry':<14}{'Entry px':>10}{'Exit':<14}{'Exit px':>10}{'Hold years':>13}{'Return%':>11}{'CAGR%':>10}{'Status':>10}")
top_single = tp_df.dropna(subset=["ret_gross_pct"]).sort_values("ret_gross_pct", ascending=False).head(20)
for _, r in top_single.iterrows():
    exit_dt = r["exit_dt"].strftime("%Y-%m-%d") if r["exit_dt"] is not None else "OPEN"
    print(f"  {r['ticker']:<7}{r['entry_dt'].strftime('%Y-%m-%d'):<14}{r['entry_px']:>10.0f}{exit_dt:<14}{r['exit_px']:>10.0f}{r['hold_years']:>11.2f}y{r['ret_gross_pct']:>+10.1f}%{r['cagr_pct']:>+9.1f}%{r['status']:>10}")

# Long-hold compounders (highest hold days × good returns)
print("\n" + "="*120)
print("  LONG-HOLD COMPOUNDERS (held longest with positive returns)")
print("="*120)
long_hold = tp_df.dropna(subset=["ret_gross_pct"]).copy()
long_hold["compound_score"] = long_hold["hold_years"] * np.clip(long_hold["ret_gross_pct"]/100, 0, 20)
long_hold = long_hold[long_hold["ret_gross_pct"] > 50].sort_values("hold_years", ascending=False).head(20)
print(f"\n  {'Ticker':<7}{'Entry':<14}{'Hold years':>13}{'Total ret%':>12}{'CAGR%':>9}{'Status':>10}")
for _, r in long_hold.iterrows():
    print(f"  {r['ticker']:<7}{r['entry_dt'].strftime('%Y-%m-%d'):<14}{r['hold_years']:>11.2f}y{r['ret_gross_pct']:>+11.1f}%{r['cagr_pct']:>+8.1f}%{r['status']:>10}")

# Tickers consistently in top picks across many quarters (FA quality consistency)
print("\n" + "="*120)
print("  FA SCORE QUALITY CONSISTENCY — tickers in A tier most quarters")
print("="*120)
fa = pd.read_csv("fa_ratings_lh.csv")
fa_a = fa[fa["tier"]=="A"].groupby("ticker").size().sort_values(ascending=False)
fa_ab = fa[fa["tier"].isin(["A","B"])].groupby("ticker").size().sort_values(ascending=False)
total_q = fa.groupby("ticker").size()

# Merge: A tier count, A+B tier count, total appearances
quality_df = pd.DataFrame({
    "n_A_quarters": fa_a,
    "n_AB_quarters": fa_ab,
    "n_total_quarters": total_q,
}).fillna(0).astype(int)
quality_df["pct_A"] = (quality_df["n_A_quarters"] / quality_df["n_total_quarters"] * 100).round(1)
quality_df = quality_df[quality_df["n_total_quarters"] >= 30].sort_values("n_A_quarters", ascending=False)

print(f"\n  {'Ticker':<7}{'A quarters':>13}{'A+B qtrs':>11}{'Total qtrs':>13}{'% A':>8}")
for tk, r in quality_df.head(25).iterrows():
    print(f"  {tk:<7}{int(r['n_A_quarters']):>13}{int(r['n_AB_quarters']):>11}{int(r['n_total_quarters']):>13}{r['pct_A']:>7.1f}%")

# Save outputs
tp_df.to_csv("lh_v1_trade_pairs.csv", index=False)
ticker_summary.to_csv("lh_v1_ticker_summary.csv")
quality_df.to_csv("lh_v1_quality_consistency.csv")
print("\nSaved: lh_v1_trade_pairs.csv, lh_v1_ticker_summary.csv, lh_v1_quality_consistency.csv")
print("DONE")
