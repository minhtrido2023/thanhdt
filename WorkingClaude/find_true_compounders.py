#!/usr/bin/env python3
"""
find_true_compounders.py
========================
Find true SUPER COMPOUNDERS: stocks the LH system would have bought (A-tier consistently)
and that produced massive multi-year price appreciation.

User mandate: "không quan tâm phải bán sớm nếu vẫn còn hiệu quả về mặt fundamental"
→ Compute "buy and hold from first A-tier appearance to today" return for top quality names.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

# Load ratings + prices
fa = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time"])
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])

# For each ticker, find first A-tier quarter and compute price appreciation to peak / to today
ticker_summary = []
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("time")
    # First A-tier appearance
    a_rows = g[g["tier"] == "A"]
    if len(a_rows) < 1: continue

    first_a_time = a_rows["time"].iloc[0]
    # Price at first A
    p = prices[prices["ticker"] == tk].sort_values("time")
    if len(p) == 0: continue

    # Get price at first A (closest after first_a_time)
    p_at_first = p[p["time"] >= first_a_time]
    if len(p_at_first) == 0: continue
    first_a_px = p_at_first["Close"].iloc[0]
    first_a_dt = p_at_first["time"].iloc[0]

    # Peak price after first A
    p_after = p[p["time"] >= first_a_dt]
    if len(p_after) == 0: continue
    peak_px = p_after["Close"].max()
    peak_dt = p_after.loc[p_after["Close"].idxmax(), "time"]
    current_px = p_after["Close"].iloc[-1]
    current_dt = p_after["time"].iloc[-1]

    years_to_peak = (peak_dt - first_a_dt).days / 365.25
    years_to_now = (current_dt - first_a_dt).days / 365.25

    ticker_summary.append({
        "ticker": tk,
        "n_quarters": len(g),
        "n_A_quarters": (g["tier"] == "A").sum(),
        "n_AB_quarters": (g["tier"].isin(["A","B"])).sum(),
        "pct_A": (g["tier"] == "A").sum() / len(g) * 100,
        "first_A_dt": first_a_dt,
        "first_A_px": first_a_px,
        "peak_px": peak_px,
        "peak_dt": peak_dt,
        "current_px": current_px,
        "years_to_peak": years_to_peak,
        "years_to_now": years_to_now,
        "peak_multiple": peak_px / first_a_px,
        "current_multiple": current_px / first_a_px,
        "peak_cagr": ((peak_px / first_a_px) ** (1/max(years_to_peak, 0.1)) - 1) * 100,
        "current_cagr": ((current_px / first_a_px) ** (1/max(years_to_now, 0.1)) - 1) * 100,
    })

ts = pd.DataFrame(ticker_summary)

# Filter: meaningful presence (≥10 quarters of data, ≥5 A quarters, first_A before 2023)
qualified = ts[
    (ts["n_quarters"] >= 10) &
    (ts["n_A_quarters"] >= 5) &
    (ts["first_A_dt"] < pd.Timestamp("2023-01-01"))  # enough time to compound
].copy()

# ─── 1. TRUE SUPER COMPOUNDERS (peak from first A entry) ─────────────────
print("="*120)
print("  TRUE SUPER COMPOUNDERS — Buy at first A-tier appearance, hold to PEAK")
print("  (Filtered: ≥10 quarters data, ≥5 A quarters, entered before 2023)")
print("="*120)
top_peak = qualified.sort_values("peak_multiple", ascending=False).head(25)
print(f"\n  {'Ticker':<7}{'First A':<13}{'First px':>10}{'Peak px':>10}{'Peak dt':<13}{'Yrs':>5}{'Multiple':>10}{'CAGR%':>9}{'% A qtrs':>10}")
for _, r in top_peak.iterrows():
    print(f"  {r['ticker']:<7}{r['first_A_dt'].strftime('%Y-%m-%d'):<13}{r['first_A_px']:>10.0f}{r['peak_px']:>10.0f}{r['peak_dt'].strftime('%Y-%m-%d'):<13}{r['years_to_peak']:>4.1f}y{r['peak_multiple']:>9.2f}x{r['peak_cagr']:>+8.1f}%{r['pct_A']:>9.1f}%")

# ─── 2. CURRENT HOLD WINNERS (still up vs entry) ─────────────────────────
print("\n" + "="*120)
print("  STILL-WINNERS TODAY — Entry from first A-tier → current price")
print("="*120)
top_current = qualified.sort_values("current_multiple", ascending=False).head(20)
print(f"\n  {'Ticker':<7}{'First A':<13}{'First px':>10}{'Current px':>12}{'Yrs held':>10}{'Multiple':>10}{'CAGR%':>9}{'% A qtrs':>10}")
for _, r in top_current.iterrows():
    print(f"  {r['ticker']:<7}{r['first_A_dt'].strftime('%Y-%m-%d'):<13}{r['first_A_px']:>10.0f}{r['current_px']:>12.0f}{r['years_to_now']:>9.1f}y{r['current_multiple']:>9.2f}x{r['current_cagr']:>+8.1f}%{r['pct_A']:>9.1f}%")

# ─── 3. CONSISTENT A-TIER QUALITY + GOOD CURRENT RETURNS ─────────────────
print("\n" + "="*120)
print("  ELITE COMPOUNDERS — High A-tier consistency (≥60%) AND positive current return")
print("="*120)
elite = qualified[(qualified["pct_A"] >= 60) & (qualified["current_multiple"] >= 1.2)].sort_values("current_multiple", ascending=False)
print(f"\n  {'Ticker':<7}{'% A qtrs':>10}{'First A':<13}{'Yrs held':>10}{'Multiple':>10}{'CAGR%':>9}{'Peak Multiple':>15}{'Peak in past Y':>17}")
for _, r in elite.iterrows():
    peak_in_past = (pd.Timestamp.now() - r["peak_dt"]).days / 365.25
    print(f"  {r['ticker']:<7}{r['pct_A']:>9.1f}%{r['first_A_dt'].strftime('%Y-%m-%d'):<13}{r['years_to_now']:>9.1f}y{r['current_multiple']:>9.2f}x{r['current_cagr']:>+8.1f}%{r['peak_multiple']:>14.2f}x{peak_in_past:>16.2f}y")

# ─── 4. FA A-TIER STILL TODAY (latest quarter A picks) ───────────────────
print("\n" + "="*120)
print("  STILL A-TIER NOW (2026-Q1) — these are CURRENT compounder candidates")
print("="*120)
latest_q = fa["quarter"].max()
latest_a = fa[(fa["quarter"]==latest_q) & (fa["tier"]=="A")]["ticker"].tolist()
print(f"\nLatest quarter: {latest_q}, A-tier count: {len(latest_a)}")
latest_a_summary = qualified[qualified["ticker"].isin(latest_a)].sort_values("pct_A", ascending=False)
print(f"\n  {'Ticker':<7}{'% A qtrs':>10}{'First A':<13}{'Yrs held':>10}{'Current mult':>14}{'CAGR%':>9}")
for _, r in latest_a_summary.iterrows():
    print(f"  {r['ticker']:<7}{r['pct_A']:>9.1f}%{r['first_A_dt'].strftime('%Y-%m-%d'):<13}{r['years_to_now']:>9.1f}y{r['current_multiple']:>13.2f}x{r['current_cagr']:>+8.1f}%")

# ─── 5. MISSED OPPORTUNITY — system bought but cohort cut early ──────────
print("\n" + "="*120)
print("  COHORT-CUT VICTIMS — system held only 1Y, but stock continued to multi-year peak")
print("="*120)
# Top single trades from earlier analysis that had MUCH bigger subsequent runs
tp = pd.read_csv("lh_v1_trade_pairs.csv", parse_dates=["entry_dt","exit_dt"])
tp_closed = tp[tp["status"]=="CLOSED"].copy()

# For each closed trade, find max price after exit
victims = []
for _, t in tp_closed.iterrows():
    tk = t["ticker"]
    p = prices[(prices["ticker"]==tk) & (prices["time"] > t["exit_dt"])].sort_values("time")
    if len(p) == 0: continue
    post_exit_max = p["Close"].max()
    post_exit_max_dt = p.loc[p["Close"].idxmax(), "time"]
    days_to_post_peak = (post_exit_max_dt - t["exit_dt"]).days
    missed_pct = (post_exit_max / t["exit_px"] - 1) * 100
    if missed_pct > 50:  # Missed >50% additional gain after exit
        victims.append({
            "ticker": tk,
            "entry_dt": t["entry_dt"], "exit_dt": t["exit_dt"],
            "entry_px": t["entry_px"], "exit_px": t["exit_px"],
            "trade_ret": t["ret_gross_pct"],
            "post_exit_peak_px": post_exit_max,
            "post_exit_peak_dt": post_exit_max_dt,
            "missed_pct": missed_pct,
            "days_after_exit_to_peak": days_to_post_peak,
        })
v_df = pd.DataFrame(victims).sort_values("missed_pct", ascending=False)
print(f"\n  Closed trades that SUBSEQUENT PEAK was >50% higher than exit price (top 25):")
print(f"\n  {'Ticker':<7}{'Trade exit':<13}{'Exit px':>10}{'Post peak px':>14}{'Days after':>12}{'Missed%':>10}{'Trade ret':>10}")
for _, r in v_df.head(25).iterrows():
    print(f"  {r['ticker']:<7}{r['exit_dt'].strftime('%Y-%m-%d'):<13}{r['exit_px']:>10.0f}{r['post_exit_peak_px']:>14.0f}{r['days_after_exit_to_peak']:>12}{r['missed_pct']:>+9.1f}%{r['trade_ret']:>+9.1f}%")

# Save
qualified.to_csv("true_compounders_universe.csv", index=False)
elite.to_csv("elite_compounders.csv", index=False)
v_df.to_csv("cohort_cut_victims.csv", index=False)
print("\nSaved: true_compounders_universe.csv, elite_compounders.csv, cohort_cut_victims.csv")
