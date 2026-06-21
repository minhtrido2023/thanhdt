#!/usr/bin/env python3
"""Format saved sim outputs with detailed cash/cost tracking."""
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

INIT_NAV = 50e9
MAX_POS = 10
TARGET_PER_POS = INIT_NAV / MAX_POS  # 5B per pick (approx, equal-weight)

trades = pd.read_csv("data/sim_v11_jun2025_trades.csv")
nav = pd.read_csv("data/sim_v11_jun2025_nav.csv")
trades["entry_date"] = pd.to_datetime(trades["entry_date"])
trades["exit_date"] = pd.to_datetime(trades["exit_date"])
nav["time"] = pd.to_datetime(nav["time"])

# Map entry_date to NAV-at-entry for accurate cost calc
nav_lookup = nav.set_index("time")[["nav","cash_pct","deployed_pct","n_pos","state"]]

print("="*135)
print(f"  BA V11 — Trade-by-trade detail (vốn ban đầu 50 tỷ VND)")
print("="*135)
print(f"\n{'#':<3}{'Ticker':<7}{'Entry':<12}{'Exit':<12}{'NAV@Buy(B)':>12}"
      f"{'Cost~(B)':>11}{'Ret%':>8}{'P&L~(M)':>10}{'Reason':<8}{'PlayType':<22}")
print("-"*135)

trades = trades.sort_values("entry_date").reset_index(drop=True)
for i, r in trades.iterrows():
    # NAV at entry
    nav_at_entry_idx = nav_lookup.index.get_indexer([r["entry_date"]], method="nearest")[0]
    nav_at_entry = nav_lookup.iloc[nav_at_entry_idx]["nav"]
    # Approximate cost: NAV / max_positions, but adjusted for actual deployment
    # Better: estimate cost from ret_net * cost = proceeds - cost
    # Cost ≈ position target_value at entry time
    cost_est = nav_at_entry / MAX_POS  # equal-weight target
    pnl_est = cost_est * r["ret_net"]
    print(f"{i+1:<3}{r['ticker']:<7}{str(r['entry_date'].date()):<12}{str(r['exit_date'].date()):<12}"
          f"{nav_at_entry/1e9:>11.3f}{cost_est/1e9:>10.3f}"
          f"{r['ret_net']*100:>+7.2f}%{pnl_est/1e6:>+9.0f}M"
          f"{r['reason']:<8}{r['play_type']:<22}")

# Aggregate
print()
print(f"Total trades: {len(trades)}")
print(f"Winners:  {(trades['ret_net']>0).sum()} ({(trades['ret_net']>0).mean()*100:.1f}%)")
print(f"Losers:   {(trades['ret_net']<=0).sum()} ({(trades['ret_net']<=0).mean()*100:.1f}%)")
print(f"Stops:    {(trades['reason']=='STOP').sum()}")
print(f"Time:     {(trades['reason']=='TIME').sum()}")
print(f"Avg ret:  {trades['ret_net'].mean()*100:+.2f}%")
print(f"Best:     {trades.loc[trades['ret_net'].idxmax(),'ticker']} "
      f"({trades['ret_net'].max()*100:+.2f}% in {trades.loc[trades['ret_net'].idxmax(),'days_held']:.0f}d)")
print(f"Worst:    {trades.loc[trades['ret_net'].idxmin(),'ticker']} "
      f"({trades['ret_net'].min()*100:+.2f}% in {trades.loc[trades['ret_net'].idxmin(),'days_held']:.0f}d)")

# ─── NAV / Cash tracking ──────────────────────────────────────────────
START = pd.Timestamp("2025-06-09")
END = pd.Timestamp("2026-05-14")
nav_w = nav[(nav["time"] >= START) & (nav["time"] <= END)].copy()
nav_w["cash"] = nav_w["nav"] * nav_w["cash_pct"] / 100
nav_w["deployed"] = nav_w["nav"] * nav_w["deployed_pct"] / 100

print(f"\n{'='*100}")
print(f"  💰 NAV / CASH / POSITION TRACKING (key dates)")
print(f"{'='*100}")
print(f"\n{'Date':<12}{'NAV(B)':>11}{'Cash(B)':>11}{'Deployed(B)':>13}{'Deployed%':>11}{'#Pos':>6}{'State':>7}{'P&L(M)':>10}")
print("-" * 91)

# Sample monthly + at major NAV peaks/troughs
nav_w["yr_mo"] = nav_w["time"].dt.to_period("M")
monthly_last = nav_w.groupby("yr_mo").tail(1)
# Add first day and last day
samples = pd.concat([nav_w.iloc[[0]], monthly_last, nav_w.iloc[[-1]]]).drop_duplicates("time").sort_values("time")

for _, r in samples.iterrows():
    state_str = str(int(r["state"])) if pd.notna(r["state"]) else "-"
    pnl = r["nav"] - INIT_NAV
    print(f"{str(r['time'].date()):<12}{r['nav']/1e9:>10.3f}{r['cash']/1e9:>10.3f}"
          f"{r['deployed']/1e9:>12.3f}{r['deployed_pct']:>10.1f}%{int(r['n_pos']):>6}"
          f"{state_str:>7}{pnl/1e6:>+9.0f}M")

# ─── Final summary ─────────────────────────────────────────────────────
print(f"\n{'='*100}")
print(f"  📊 SUMMARY")
print(f"{'='*100}")

final_nav = nav_w["nav"].iloc[-1]
final_cash = nav_w["cash"].iloc[-1]
final_deployed = nav_w["deployed"].iloc[-1]
final_n_pos = int(nav_w["n_pos"].iloc[-1])
total_ret = (final_nav / INIT_NAV - 1) * 100
n_days = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days
yrs = n_days / 365.25
cagr = (final_nav / INIT_NAV) ** (1/yrs) - 1 if yrs > 0 else 0
rets = nav_w["nav"].pct_change().dropna()
sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()

print(f"\n  📅 Period:         {nav_w['time'].iloc[0].date()} → {nav_w['time'].iloc[-1].date()} ({n_days} ngày)")
print(f"  💵 Vốn ban đầu:    {INIT_NAV/1e9:>10.3f} tỷ VND")
print(f"  💵 NAV cuối kỳ:    {final_nav/1e9:>10.3f} tỷ VND")
print(f"     - Tiền mặt:      {final_cash/1e9:>10.3f} tỷ VND ({final_cash/final_nav*100:.1f}%)")
print(f"     - Đang holding:  {final_deployed/1e9:>10.3f} tỷ VND ({final_deployed/final_nav*100:.1f}%) trong {final_n_pos} vị thế")
print(f"\n  📈 Lợi nhuận:")
print(f"     - Tổng:          {total_ret:>+10.2f}%  ({(final_nav-INIT_NAV)/1e6:>+10.0f}M VND)")
print(f"     - Annualized:    {cagr*100:>+10.2f}% CAGR")
print(f"     - Sharpe:        {sharpe:>10.2f}")
print(f"     - Max DD:        {dd*100:>+10.2f}%")
print(f"\n  📊 Giao dịch:      {len(trades)} trades, WR {(trades['ret_net']>0).mean()*100:.1f}%, Avg {trades['ret_net'].mean()*100:+.2f}%")
