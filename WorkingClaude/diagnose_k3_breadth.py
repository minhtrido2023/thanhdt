#!/usr/bin/env python3
"""
diagnose_k3_breadth.py
======================
K3: pause new buys when breadth (% tickers > MA50) drops below 30% within 5 days.

Step 1 (diagnostic): is breadth a leading indicator?
  - Pull daily breadth for ticker_prune universe
  - Identify 2026 trajectory + historical bear periods
  - Check: does breadth crash precede state5 BEAR transitions?

Step 2 (if positive): build SQL-embedded filter + canonical sim
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

print("Pulling daily breadth (% ticker_prune above MA50) ...")
BREADTH_SQL = """
WITH base AS (
  SELECT t.time, t.ticker,
    CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END AS above
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM `lithe-record-440915-m9.tav2_bq.ticker_prune` AS t2)
    AND t.time >= "2014-01-01"
    AND t.MA50 IS NOT NULL AND t.Close IS NOT NULL
)
SELECT time,
  COUNT(*) AS n_tickers,
  SUM(above) AS n_above,
  ROUND(SUM(above) / COUNT(*), 3) AS pct_above_ma50
FROM base
GROUP BY time
ORDER BY time
"""
breadth = bq(BREADTH_SQL)
breadth["time"] = pd.to_datetime(breadth["time"])
print(f"  {len(breadth)} sessions, breadth range "
      f"[{breadth['pct_above_ma50'].min():.2f}, {breadth['pct_above_ma50'].max():.2f}]")

# Compute K3 signal: breadth dropped from >50% to <30% within 5 days (or current <30%)
breadth["br5d_max"] = breadth["pct_above_ma50"].rolling(5).max()
breadth["br5d_min"] = breadth["pct_above_ma50"].rolling(5).min()
breadth["k3_signal"] = (breadth["pct_above_ma50"] < 0.30) & (breadth["br5d_max"] >= 0.50)
# Less strict variant: just below threshold
breadth["br_below_30"] = breadth["pct_above_ma50"] < 0.30
breadth["br_below_40"] = breadth["pct_above_ma50"] < 0.40

# Compare with state5
print("\nPulling state5 ...")
s5 = bq('SELECT time, state FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state` ORDER BY time')
s5["time"] = pd.to_datetime(s5["time"])
m = breadth.merge(s5, on="time", how="left")
m["state"] = m["state"].ffill()

# Pull VNI for context
vni = bq('SELECT time, Close AS vni FROM `lithe-record-440915-m9.tav2_bq.ticker` WHERE ticker="VNINDEX" ORDER BY time')
vni["time"] = pd.to_datetime(vni["time"])
m = m.merge(vni, on="time", how="left")

# === Analysis 1: K3 signal vs state5 BEAR transitions ===
print("\n=== K3 signal triggers (full history) ===")
k3_days = m[m["k3_signal"]].copy()
print(f"Total K3 triggers: {len(k3_days)}")
print(f"Trigger dates with surrounding state:")
print(k3_days[["time","pct_above_ma50","state","vni"]].to_string(index=False, max_rows=30))

# === Analysis 2: For each state5 BEAR/CRISIS entry, did K3 fire first? ===
m["prev_state"] = m["state"].shift(1)
bear_entries = m[(m["state"].isin([1, 2])) & (~m["prev_state"].isin([1, 2]))].copy()
print(f"\n=== BEAR/CRISIS entries: did K3 lead? ===")
print(f"Total BEAR/CRISIS regime entries: {len(bear_entries)}")
for _, ev in bear_entries.iterrows():
    # Look back 30 days for K3 trigger
    lookback = m[(m["time"] < ev["time"]) & (m["time"] >= ev["time"] - pd.Timedelta(days=30))]
    k3_in_window = lookback[lookback["k3_signal"]]
    br_below_in_window = lookback[lookback["br_below_30"]]
    lead_k3 = (ev["time"] - k3_in_window["time"].max()).days if len(k3_in_window) else "n/a"
    lead_br = (ev["time"] - br_below_in_window["time"].max()).days if len(br_below_in_window) else "n/a"
    print(f"  {ev['time'].date()} (state5 → {int(ev['state'])}): "
          f"K3 lead = {lead_k3} days, breadth<30 lead = {lead_br} days, "
          f"breadth at entry = {ev['pct_above_ma50']:.2f}")

# === Analysis 3: 2026 trajectory in detail ===
print("\n=== 2026 BREADTH TRAJECTORY ===")
m26 = m[m["time"] >= pd.Timestamp("2026-01-01")].copy()
print(f"{'date':<12}{'breadth':>8}{'state5':>7}{'vni':>8}{'k3':>5}{'br<30':>7}{'br<40':>7}")
for _, r in m26.iterrows():
    flag_k3 = "★" if r["k3_signal"] else ""
    flag_b30 = "★" if r["br_below_30"] else ""
    flag_b40 = "★" if r["br_below_40"] else ""
    print(f"{r['time'].strftime('%Y-%m-%d'):<12}{r['pct_above_ma50']:>8.2f}"
          f"{int(r['state']) if pd.notna(r['state']) else '?':>7}{r['vni']:>8.0f}"
          f"{flag_k3:>5}{flag_b30:>7}{flag_b40:>7}")

# Save full breadth for later use
m.to_csv("breadth_full.csv", index=False)
print(f"\nSaved breadth_full.csv ({len(m)} rows)")
