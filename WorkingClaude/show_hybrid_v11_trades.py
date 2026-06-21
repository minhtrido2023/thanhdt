#!/usr/bin/env python3
"""
show_hybrid_v11_trades.py
=========================
Show all trades that hybrid v11 system would have executed from 2025-06-01 to today,
assuming NAV=50B split 50/50 BA v11 + LH gated.

Sources:
  BA leg: ba_trades_bal_refresh.csv + ba_trades_vn30_refresh.csv (baseline v10 sim) +
          P3 overheated filter applied post-hoc (remove BUYs on VNI/MA200>1.30 days)
  LH leg: live rerun of run_lh() with crisis_gate=True for the window
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
BA_NAV = TOTAL_NAV * 0.5  # 25B
LH_NAV = TOTAL_NAV * 0.5  # 25B

# ─── COMPUTE OVERHEATED DATES (P3 filter) ───────────────────────────────
vn = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn = vn[vn["Close"] > 100].sort_values("time").reset_index(drop=True)
vn["MA200"] = vn["Close"].rolling(200, min_periods=200).mean()
overheated = set(vn[vn["Close"] / vn["MA200"] > 1.30]["time"])
overheated_in_window = sorted([d for d in overheated if START <= d <= END])
print(f"P3 overheated dates in window: {len(overheated_in_window)}")
for d in overheated_in_window[:10]:
    print(f"  {d.date()}")

# ─── LOAD BA TRADES, APPLY P3 FILTER ────────────────────────────────────
print("\n─── BA leg trades (baseline v10 with P3 patch applied) ───")
ba_bal = pd.read_csv("data/ba_trades_bal_refresh.csv", parse_dates=["entry_date","exit_date"])
ba_vn30 = pd.read_csv("data/ba_trades_vn30_refresh.csv", parse_dates=["entry_date","exit_date"])

# Filter to window (trades with entry OR exit in window)
def slice_trades(df, start, end):
    return df[((df["entry_date"] >= start) | (df["exit_date"] >= start)) &
              (df["entry_date"] <= end)].copy()

ba_bal_win = slice_trades(ba_bal, START, END)
ba_vn30_win = slice_trades(ba_vn30, START, END)

# P3 filter: drop BUYs on overheated days (NOT applied to exits)
def p3_filter(df, overheated_set):
    return df[~df["entry_date"].isin(overheated_set)].copy()

ba_bal_p3 = p3_filter(ba_bal_win, overheated_in_window)
ba_vn30_p3 = p3_filter(ba_vn30_win, overheated_in_window)
print(f"  BAL leg: {len(ba_bal_win)} raw trades → {len(ba_bal_p3)} after P3 filter ({len(ba_bal_win)-len(ba_bal_p3)} entries blocked)")
print(f"  VN30 leg: {len(ba_vn30_win)} raw trades → {len(ba_vn30_p3)} after P3 filter")

ba_bal_p3["leg"] = "BAL"
ba_vn30_p3["leg"] = "VN30"

# ─── RUN LH GATED FOR WINDOW ────────────────────────────────────────────
print("\n─── LH leg trades (gated, A+B, staggered, 4Q hold) ───")
_CACHE.clear()
lh_res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                 refresh_mode="staggered", crisis_gate=True, init_nav=LH_NAV,
                 start="2014-04-01", end="2026-05-15")  # full sim, then slice
lh_trades = lh_res["trades"]
lh_trades["dt"] = pd.to_datetime(lh_trades["dt"])
lh_trades_win = lh_trades[(lh_trades["dt"] >= START) & (lh_trades["dt"] <= END)].copy()
print(f"  LH leg in window: {len(lh_trades_win)} trades ({(lh_trades_win['side']=='BUY').sum()} buys, {(lh_trades_win['side']=='SELL').sum()} sells)")

# ─── PRESENT BA TRADES CHRONOLOGICALLY ──────────────────────────────────
print("\n" + "="*120)
print("  BA LEG TRADES (50% NAV = 25B each on BAL + VN30 splits)")
print("="*120)

print("\n--- BAL component trades ---")
print(f"  {'entry_date':<12}{'ticker':<8}{'entry_px':>10}{'exit_date':<12}{'exit_px':>10}{'reason':<8}{'days':>6}{'ret_gross':>12}{'ret_net':>10}")
for _, t in ba_bal_p3.sort_values("entry_date").iterrows():
    exit_d = t['exit_date'].strftime('%Y-%m-%d') if pd.notna(t['exit_date']) else 'open'
    print(f"  {t['entry_date'].strftime('%Y-%m-%d')}  {t['ticker']:<8}{t['entry_price']:>10.0f}  {exit_d}  {t['exit_price']:>10.0f}  {t['reason']:<8}{int(t['days_held']):>6}{t['ret_gross']*100:>+11.2f}%{t['ret_net']*100:>+9.2f}%")

print("\n--- VN30 component trades ---")
print(f"  {'entry_date':<12}{'ticker':<8}{'entry_px':>10}{'exit_date':<12}{'exit_px':>10}{'reason':<8}{'days':>6}{'ret_gross':>12}{'ret_net':>10}")
for _, t in ba_vn30_p3.sort_values("entry_date").iterrows():
    exit_d = t['exit_date'].strftime('%Y-%m-%d') if pd.notna(t['exit_date']) else 'open'
    print(f"  {t['entry_date'].strftime('%Y-%m-%d')}  {t['ticker']:<8}{t['entry_price']:>10.0f}  {exit_d}  {t['exit_price']:>10.0f}  {t['reason']:<8}{int(t['days_held']):>6}{t['ret_gross']*100:>+11.2f}%{t['ret_net']*100:>+9.2f}%")

# ─── PRESENT LH TRADES ───────────────────────────────────────────────────
print("\n" + "="*120)
print("  LH LEG TRADES (50% NAV = 25B init)")
print("="*120)
print(f"\n  {'date':<12}{'side':<10}{'ticker':<8}{'price':>10}{'shares':>14}{'cash_flow':>16}{'q_cohort':>10}")
for _, t in lh_trades_win.sort_values("dt").iterrows():
    print(f"  {t['dt'].strftime('%Y-%m-%d')}  {t['side']:<10}{t['ticker']:<8}{t['px']:>10.0f}{t['shares']:>14.0f}{t['net']/1e6:>+15.2f}M{str(t.get('q',''))[:10]:>10}")

# ─── NAV TRAJECTORY ──────────────────────────────────────────────────────
print("\n" + "="*120)
print("  HYBRID NAV TRAJECTORY (25B BA + 25B LH from 2025-06-01)")
print("="*120)

# Load BA NAV
ba_nav_full = pd.read_csv("data/ba_v11_nav.csv", parse_dates=["time"]).sort_values("time").set_index("time")["BA_v11"]
ba_nav_win = ba_nav_full[(ba_nav_full.index >= START) & (ba_nav_full.index <= END)]
ba_nav_norm = BA_NAV * ba_nav_win / ba_nav_win.iloc[0]

# LH NAV in window
lh_nav_full = lh_res["nav"]["nav"]
lh_nav_win = lh_nav_full[(lh_nav_full.index >= START) & (lh_nav_full.index <= END)]
lh_nav_norm = LH_NAV * lh_nav_win / lh_nav_win.iloc[0]

# Align indices and combine
common_idx = ba_nav_norm.index.intersection(lh_nav_norm.index)
ba_aligned = ba_nav_norm.reindex(common_idx).ffill()
lh_aligned = lh_nav_norm.reindex(common_idx).ffill()
hybrid_nav = ba_aligned + lh_aligned

# Monthly summary
print(f"\n  {'Month':<12}{'BA NAV (B)':>14}{'LH NAV (B)':>14}{'Hybrid NAV (B)':>18}{'Hybrid Δ':>11}{'VNI Δ':>10}")
ba_monthly = ba_aligned.resample("ME").last()
lh_monthly = lh_aligned.resample("ME").last()
hyb_monthly = hybrid_nav.resample("ME").last()
vn_full = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn_full = vn_full[vn_full["Close"] > 100].sort_values("time").set_index("time")["Close"]
vn_win = vn_full[(vn_full.index >= START) & (vn_full.index <= END)]
vn_norm = vn_win / vn_win.iloc[0]
vn_monthly = vn_norm.resample("ME").last()

for i, dt in enumerate(hyb_monthly.index):
    if pd.isna(hyb_monthly.iloc[i]): continue
    hyb_chg = (hyb_monthly.iloc[i] / TOTAL_NAV - 1) * 100
    vn_chg = (vn_monthly.iloc[i] - 1) * 100 if i < len(vn_monthly) and pd.notna(vn_monthly.iloc[i]) else np.nan
    print(f"  {dt.strftime('%Y-%m'):<12}{ba_monthly.iloc[i]/1e9:>13.3f}B{lh_monthly.iloc[i]/1e9:>13.3f}B{hyb_monthly.iloc[i]/1e9:>17.3f}B{hyb_chg:>+10.2f}%{vn_chg:>+9.2f}%")

# Final stats
final_hyb = hybrid_nav.iloc[-1]
final_chg = (final_hyb / TOTAL_NAV - 1) * 100
final_vni = vn_norm.iloc[-1]
final_vni_chg = (final_vni - 1) * 100
yrs = (common_idx[-1] - common_idx[0]).days / 365.25
hyb_cagr = (final_hyb / TOTAL_NAV) ** (1/yrs) - 1 if yrs > 0 else 0
hyb_rets = hybrid_nav.pct_change().dropna()
hyb_sharpe = hyb_rets.mean() / hyb_rets.std() * np.sqrt(252) if hyb_rets.std() > 0 else 0
hyb_dd = ((hybrid_nav - hybrid_nav.cummax()) / hybrid_nav.cummax()).min() * 100

print(f"\n--- Summary ({common_idx[0].date()} → {common_idx[-1].date()}, ~{yrs*12:.1f} months) ---")
print(f"  Total NAV initial: {TOTAL_NAV/1e9:.1f}B VND")
print(f"  Total NAV final:   {final_hyb/1e9:.2f}B VND ({final_chg:+.2f}%)")
print(f"  BA leg final:      {ba_aligned.iloc[-1]/1e9:.2f}B ({(ba_aligned.iloc[-1]/BA_NAV-1)*100:+.2f}%)")
print(f"  LH leg final:      {lh_aligned.iloc[-1]/1e9:.2f}B ({(lh_aligned.iloc[-1]/LH_NAV-1)*100:+.2f}%)")
print(f"  CAGR (annualized): {hyb_cagr*100:+.2f}%")
print(f"  Sharpe:            {hyb_sharpe:+.2f}")
print(f"  MaxDD:             {hyb_dd:+.2f}%")
print(f"  VNINDEX B&H:       {final_vni_chg:+.2f}% (alpha vs VNI: {final_chg - final_vni_chg:+.2f}pp)")

# Save outputs
all_trades = []
for _, t in ba_bal_p3.iterrows():
    all_trades.append({"date":t["entry_date"],"side":"BUY","ticker":t["ticker"],"price":t["entry_price"],"leg":"BA-BAL"})
    if pd.notna(t["exit_date"]):
        all_trades.append({"date":t["exit_date"],"side":"SELL","ticker":t["ticker"],"price":t["exit_price"],"leg":"BA-BAL"})
for _, t in ba_vn30_p3.iterrows():
    all_trades.append({"date":t["entry_date"],"side":"BUY","ticker":t["ticker"],"price":t["entry_price"],"leg":"BA-VN30"})
    if pd.notna(t["exit_date"]):
        all_trades.append({"date":t["exit_date"],"side":"SELL","ticker":t["ticker"],"price":t["exit_price"],"leg":"BA-VN30"})
for _, t in lh_trades_win.iterrows():
    all_trades.append({"date":t["dt"],"side":t["side"],"ticker":t["ticker"],"price":t["px"],"leg":"LH"})

tr_df = pd.DataFrame(all_trades).sort_values("date").reset_index(drop=True)
tr_df.to_csv("data/hybrid_v11_trades_2025-06_to_now.csv", index=False)

nav_df = pd.DataFrame({"BA_NAV":ba_aligned,"LH_NAV":lh_aligned,"Hybrid_NAV":hybrid_nav,"VNI":vn_norm * TOTAL_NAV})
nav_df.to_csv("data/hybrid_v11_nav_2025-06_to_now.csv")
print(f"\nSaved: hybrid_v11_trades_2025-06_to_now.csv ({len(tr_df)} events), hybrid_v11_nav_2025-06_to_now.csv")
