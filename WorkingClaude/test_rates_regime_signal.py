# -*- coding: utf-8 -*-
"""
test_rates_regime_signal.py
===========================
Honest test of the user's hypothesis: does the VN domestic interest-rate
(lending_rate) LEVEL and MOMENTUM carry leading information for the equity
market regime — beyond the price-only signal the DT4G 5-state model uses?

Real data: macro_daily.csv (lending_rate, cpi_yoy, 2000+), VNINDEX price + DT4
state from BQ. Macro LAGGED 21 trading days for publication safety (no look-ahead).
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

PUB_LAG = 21   # trading days macro is lagged (publication delay) -> strictly causal

# --- data ---
px = bq("""SELECT p.time, p.Close, s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
m = pd.read_csv("macro_daily.csv", parse_dates=["time"])[["time", "lending_rate", "cpi_yoy"]]
df = px.merge(m, on="time", how="left").sort_values("time").reset_index(drop=True)
df["lending_rate"] = df["lending_rate"].ffill(); df["cpi_yoy"] = df["cpi_yoy"].ffill()
df = df.dropna(subset=["lending_rate"]).reset_index(drop=True)

# --- features (all LAGGED by PUB_LAG -> known only with delay) ---
lr = df["lending_rate"]; cpi = df["cpi_yoy"]
df["real_rate"] = lr - cpi
df["rate_chg6m"] = lr - lr.shift(126)          # 6-month change in rate
df["rate_lvl_rank"] = lr.expanding(min_periods=252).apply(
    lambda x: (x.rank(pct=True).iloc[-1]), raw=False)   # expanding percentile (point-in-time)
for c in ["lending_rate", "real_rate", "rate_chg6m", "rate_lvl_rank"]:
    df[c + "_lag"] = df[c].shift(PUB_LAG)

# --- forward VNINDEX returns ---
for h in (20, 60, 120):
    df[f"fwd{h}"] = df["Close"].shift(-h) / df["Close"] - 1

def ic(a, b):
    s = pd.concat([a, b], axis=1).dropna()
    return s.corr(method="spearman").iloc[0, 1] if len(s) > 50 else np.nan

print("=" * 78)
print("  RATE-as-regime-signal test (real lending_rate, lagged %dd, no look-ahead)" % PUB_LAG)
print("=" * 78)
print("\n[1] Spearman IC of lagged rate features vs forward VNINDEX return")
print(f"  {'feature':<20}{'fwd20':>10}{'fwd60':>10}{'fwd120':>10}")
for f in ["lending_rate_lag", "real_rate_lag", "rate_chg6m_lag", "rate_lvl_rank_lag"]:
    print(f"  {f:<20}" + "".join(f"{ic(df[f], df[f'fwd{h}']):>10.3f}" for h in (20, 60, 120)))

print("\n[2] Forward 60d/120d VNINDEX return, conditioned on rate MOMENTUM (6m chg)")
q = df["rate_chg6m_lag"]
hi = df[q > q.quantile(0.80)]; lo = df[q < q.quantile(0.20)]; mid = df[(q >= q.quantile(0.20)) & (q <= q.quantile(0.80))]
for label, g in [("Rates RISING fast (top 20%)", hi), ("Rates flat (mid)", mid), ("Rates FALLING fast (bot 20%)", lo)]:
    print(f"  {label:<32} fwd60 {g['fwd60'].mean()*100:+6.2f}%  fwd120 {g['fwd120'].mean()*100:+6.2f}%  n={len(g)}")

print("\n[3] Forward 60d return, conditioned on rate LEVEL (expanding percentile)")
r = df["rate_lvl_rank_lag"]
for label, g in [("Rate level HIGH (>80pct)", df[r > 0.80]), ("Rate level mid", df[(r >= 0.2) & (r <= 0.8)]), ("Rate level LOW (<20pct)", df[r < 0.20])]:
    print(f"  {label:<28} fwd60 {g['fwd60'].mean()*100:+6.2f}%  fwd120 {g['fwd120'].mean()*100:+6.2f}%  n={len(g)}")

print("\n[4] Does a rate signal LEAD the price-based CRISIS state?")
df["is_crisis"] = (df["state"] == 1).astype(int)
onsets = df.index[(df["is_crisis"].diff() == 1)].tolist()
print(f"  CRISIS onsets: {len(onsets)}")
lead_hi = lead_rising = 0
for i in onsets:
    win = df.iloc[max(0, i-126):i]    # 6 months before onset
    if len(win) < 30: continue
    if win["rate_lvl_rank_lag"].iloc[-1] is not np.nan and (win["rate_lvl_rank_lag"].iloc[-1] or 0) > 0.6: lead_hi += 1
    if (win["rate_chg6m_lag"].iloc[-1] or 0) > 0: lead_rising += 1
print(f"  ...preceded by HIGH rate level (>60pct): {lead_hi}/{len(onsets)}")
print(f"  ...preceded by RISING rates (6m chg>0):  {lead_rising}/{len(onsets)}")

print("\n[5] Recovery test: after rates PEAK and start falling, forward 120d return")
# rate peak = local max over +-63d; then measure fwd return from 21d after peak
lr_l = df["lending_rate_lag"]
peak = (lr_l == lr_l.rolling(127, center=True, min_periods=60).max()) & (lr_l.shift(-63) < lr_l)
g = df[peak.fillna(False)]
print(f"  Days at/just-after a rate peak (n={len(g)}): fwd120 {g['fwd120'].mean()*100:+.2f}%  "
      f"(all-days avg {df['fwd120'].mean()*100:+.2f}%)")
print("\nDONE.")
