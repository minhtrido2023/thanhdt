#!/usr/bin/env python3
"""
show_hybrid_v11_fresh_start.py
==============================
Hybrid v11 trades from a FRESH START on 2025-06-01 with NAV=50B (25B each leg).

Difference from show_hybrid_v11_trades.py:
  - LH leg starts EMPTY at 2025-06-01 (no inherited positions from prior cohorts)
  - LH ramps from 0% deploy → 50% deploy over ~12 months (4-quarter cohort cycle)
  - During ramp, LH leg holds cash (no VHM/VNM sells in 2025-12, those were from prior cohorts)
  - BA leg: similar ramp but faster (45d cycle = ~1-2 months to full deploy)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, _CACHE

START = pd.Timestamp("2025-06-01")
END = pd.Timestamp("2026-05-15")
TOTAL_NAV = 50e9
LH_NAV = 25e9
BA_NAV = 25e9

# ─── LH FRESH START ──────────────────────────────────────────────────────
print(f"Running LH gated FRESH START from {START.date()} ...")
_CACHE.clear()
lh_res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                 refresh_mode="staggered", crisis_gate=True, init_nav=LH_NAV,
                 start=START.strftime("%Y-%m-%d"), end=END.strftime("%Y-%m-%d"))
lh_trades = lh_res["trades"]
lh_trades["dt"] = pd.to_datetime(lh_trades["dt"])
print(f"  LH trades: {len(lh_trades)} ({(lh_trades['side']=='BUY').sum()} buys, {(lh_trades['side'].isin(['SELL','TRAIL_STOP'])).sum()} sells)")

# Show LH trades chronologically
print("\n" + "="*120)
print(f"  LH LEG TRADES (FRESH START, 25B init)")
print("="*120)
print(f"\n  {'date':<12}{'side':<8}{'ticker':<8}{'price':>10}{'shares':>12}{'cash_flow_M':>16}{'q_cohort':>10}")
for _, t in lh_trades.sort_values("dt").iterrows():
    print(f"  {t['dt'].strftime('%Y-%m-%d')}  {t['side']:<8}{t['ticker']:<8}{t['px']:>10.0f}{t['shares']:>12.0f}{t['net']/1e6:>+15.2f}M{str(t.get('q',''))[:10]:>10}")

# LH NAV trajectory
print("\n--- LH NAV trajectory (monthly) ---")
lh_nav = lh_res["nav"]["nav"]
lh_nav_w = lh_nav[(lh_nav.index >= START) & (lh_nav.index <= END)]
lh_n_pos = lh_res["nav"]["n_pos"]
lh_cash = lh_res["nav"]["cash"]
print(f"  {'Month':<12}{'NAV (B)':>10}{'cash (B)':>11}{'equity (B)':>13}{'n_pos':>7}{'NAV_chg':>10}{'deploy%':>10}")
for dt in pd.date_range(START, END, freq="ME"):
    nav_at = lh_nav_w.asof(dt) if dt in lh_nav_w.index else lh_nav_w[lh_nav_w.index <= dt].iloc[-1] if len(lh_nav_w[lh_nav_w.index <= dt]) > 0 else np.nan
    if pd.isna(nav_at): continue
    actual_dt = lh_nav_w[lh_nav_w.index <= dt].index[-1] if len(lh_nav_w[lh_nav_w.index <= dt]) > 0 else dt
    cash_at = lh_cash.loc[actual_dt]
    npos_at = int(lh_n_pos.loc[actual_dt])
    chg = (nav_at / LH_NAV - 1) * 100
    deploy = (1 - cash_at / nav_at) * 100
    print(f"  {actual_dt.strftime('%Y-%m'):<12}{nav_at/1e9:>9.3f}B{cash_at/1e9:>10.3f}B{(nav_at-cash_at)/1e9:>12.3f}B{npos_at:>7d}{chg:>+9.2f}%{deploy:>9.1f}%")

print(f"\n  LH final NAV: {lh_nav_w.iloc[-1]/1e9:.3f}B ({(lh_nav_w.iloc[-1]/LH_NAV - 1)*100:+.2f}%)")

# ─── BA LEG (use existing trades, fresh-start approximation) ─────────────
# For BA, 45-day cycle means ramp is much faster (~1-2 months). The existing trades log from
# refresh_ba_with_trades.py captures actual trades from a full continuous sim. For a fresh start
# at 2025-06-01, BA would also start empty and quickly fill up. The earliest entries in our log
# after START are 2025-06-04+. We'll filter to entries on/after START.
ba_bal = pd.read_csv("data/ba_trades_bal_refresh.csv", parse_dates=["entry_date","exit_date"])
ba_vn30 = pd.read_csv("data/ba_trades_vn30_refresh.csv", parse_dates=["entry_date","exit_date"])

# Only include trades with entry IN window (= fresh-start assumption: no inherited positions)
ba_bal_fresh = ba_bal[(ba_bal["entry_date"] >= START) & (ba_bal["entry_date"] <= END)].copy()
ba_vn30_fresh = ba_vn30[(ba_vn30["entry_date"] >= START) & (ba_vn30["entry_date"] <= END)].copy()

# P3 overheated filter (none active in this window per prior check)
vn = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn = vn[vn["Close"] > 100].sort_values("time").reset_index(drop=True)
vn["MA200"] = vn["Close"].rolling(200, min_periods=200).mean()
overheated = set(vn[vn["Close"] / vn["MA200"] > 1.30]["time"])

ba_bal_fresh = ba_bal_fresh[~ba_bal_fresh["entry_date"].isin(overheated)]
ba_vn30_fresh = ba_vn30_fresh[~ba_vn30_fresh["entry_date"].isin(overheated)]

print("\n" + "="*120)
print(f"  BA LEG TRADES (fresh-start approximation, 25B init, entries on/after {START.date()})")
print("="*120)
print(f"\n  BA BAL: {len(ba_bal_fresh)} trades")
print(f"  {'entry':<12}{'ticker':<8}{'entry_px':>10}{'exit':<12}{'exit_px':>10}{'reason':<8}{'days':>5}{'ret_net':>10}")
for _, t in ba_bal_fresh.sort_values("entry_date").head(40).iterrows():
    exit_d = t['exit_date'].strftime('%Y-%m-%d') if pd.notna(t['exit_date']) else 'open'
    print(f"  {t['entry_date'].strftime('%Y-%m-%d')}  {t['ticker']:<8}{t['entry_price']:>10.0f}  {exit_d}  {t['exit_price']:>10.0f}  {t['reason']:<8}{int(t['days_held']):>5}{t['ret_net']*100:>+9.2f}%")

print(f"\n  BA VN30: {len(ba_vn30_fresh)} trades")
print(f"  {'entry':<12}{'ticker':<8}{'entry_px':>10}{'exit':<12}{'exit_px':>10}{'reason':<8}{'days':>5}{'ret_net':>10}")
for _, t in ba_vn30_fresh.sort_values("entry_date").head(40).iterrows():
    exit_d = t['exit_date'].strftime('%Y-%m-%d') if pd.notna(t['exit_date']) else 'open'
    print(f"  {t['entry_date'].strftime('%Y-%m-%d')}  {t['ticker']:<8}{t['entry_price']:>10.0f}  {exit_d}  {t['exit_price']:>10.0f}  {t['reason']:<8}{int(t['days_held']):>5}{t['ret_net']*100:>+9.2f}%")

# BA NAV simulation from trades — simple approximation
# Each trade: position_size = init_nav / max_positions (10). 25B / 10 = 2.5B per position.
# But actual sim uses dynamic NAV. For approximation:
print("\n--- BA NAV trajectory (approximate, from trade returns) ---")
# Combine BAL+VN30 ret_net per month (each leg 12.5B = 25B/2)
def trade_to_pnl(trades, leg_nav):
    """Compute PnL per trade as ret_net × position_size."""
    pos_size = leg_nav / 10  # max_positions=10
    trades = trades.copy()
    trades["pnl"] = trades["ret_net"] * pos_size
    return trades

bal_pnl = trade_to_pnl(ba_bal_fresh, BA_NAV/2)
vn30_pnl = trade_to_pnl(ba_vn30_fresh, BA_NAV/2)
all_ba_trades = pd.concat([bal_pnl.assign(leg="BAL"), vn30_pnl.assign(leg="VN30")], ignore_index=True)
all_ba_trades["exit_month"] = pd.to_datetime(all_ba_trades["exit_date"]).dt.to_period("M")
monthly_pnl = all_ba_trades.groupby("exit_month")["pnl"].sum()
cum_pnl = monthly_pnl.cumsum()
print(f"  {'Month':<10}{'Monthly PnL (M)':>18}{'BA NAV est (B)':>16}")
for m, pnl in monthly_pnl.items():
    nav_est = BA_NAV + cum_pnl.loc[m]
    print(f"  {str(m):<10}{pnl/1e6:>+17.2f}M{nav_est/1e9:>15.3f}B")

ba_nav_final = BA_NAV + (monthly_pnl.sum() if len(monthly_pnl) else 0)
ba_chg = (ba_nav_final/BA_NAV - 1) * 100
print(f"\n  BA final NAV approx: {ba_nav_final/1e9:.3f}B ({ba_chg:+.2f}%)")

# ─── HYBRID SUMMARY ──────────────────────────────────────────────────────
lh_final = lh_nav_w.iloc[-1]
hybrid_final = lh_final + ba_nav_final
hyb_chg = (hybrid_final/TOTAL_NAV - 1) * 100

print("\n" + "="*120)
print("  HYBRID v11 FRESH-START SUMMARY")
print("="*120)
print(f"  Initial NAV:     {TOTAL_NAV/1e9:.1f}B (BA 25B + LH 25B)")
print(f"  BA leg final:    {ba_nav_final/1e9:.3f}B ({(ba_nav_final/BA_NAV-1)*100:+.2f}%)")
print(f"  LH leg final:    {lh_final/1e9:.3f}B ({(lh_final/LH_NAV-1)*100:+.2f}%)")
print(f"  Hybrid final:    {hybrid_final/1e9:.3f}B ({hyb_chg:+.2f}%)")

# VNI compare
vn_win = vn[(vn["time"] >= START) & (vn["time"] <= END)].sort_values("time")
vn_chg = (vn_win["Close"].iloc[-1] / vn_win["Close"].iloc[0] - 1) * 100
print(f"  VNINDEX B&H:     {vn_chg:+.2f}%  |  alpha vs VNI: {hyb_chg - vn_chg:+.2f}pp")

# Caveat
print("""

  ⚠️ KEY DIFFERENCES FROM PRIOR SLICED REPORT:
  - LH leg starts EMPTY (no VHM/VNM 2024-vintage positions)
  - LH ramps slowly: ~2-3 picks per quarter, 4 quarters to full deploy
  - During ramp, LH leg has SIGNIFICANT CASH (12.5-37.5% NAV for first 9 months)
  - LH return is much lower than sliced report (~+9-15% vs sliced +33%)
  - Cohort exits (like VHM 2025-12 sold +205B) DID NOT happen here — those were 2024Q4 cohort

  → True picture: fresh-start hybrid returns will be DOMINATED BY BA in first 12 months,
    LH only contributes from its slow ramp.
""")
