# -*- coding: utf-8 -*-
"""
pull_us_market.py
Pull S&P 500 (^GSPC) + VIX (^VIX) daily history 2000-now via yfinance.
Save to local cache for use as Tam Quan v3.1 override input.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import yfinance as yf
import pandas as pd
import numpy as np

WORKDIR = os.environ.get("STATE_WORKDIR", os.path.dirname(os.path.abspath(__file__)))

# Pull SPX (^GSPC) and VIX (^VIX)
print("Pulling SPX (^GSPC)...")
spx = yf.download("^GSPC", start="2000-01-01", end="2026-05-21", progress=False, auto_adjust=False)
spx = spx.reset_index()
spx.columns = [c if isinstance(c, str) else c[0] for c in spx.columns]
spx = spx[["Date", "Close"]].rename(columns={"Date":"time", "Close":"spx_close"})
print(f"  SPX: {len(spx)} rows | {spx['time'].iloc[0].date()} → {spx['time'].iloc[-1].date()}")

print("Pulling VIX (^VIX)...")
vix = yf.download("^VIX", start="2000-01-01", end="2026-05-21", progress=False, auto_adjust=False)
vix = vix.reset_index()
vix.columns = [c if isinstance(c, str) else c[0] for c in vix.columns]
vix = vix[["Date", "Close"]].rename(columns={"Date":"time", "Close":"vix"})
print(f"  VIX: {len(vix)} rows | {vix['time'].iloc[0].date()} → {vix['time'].iloc[-1].date()}")

# Merge
us = spx.merge(vix, on="time", how="outer").sort_values("time").reset_index(drop=True)
us["time"] = pd.to_datetime(us["time"]).dt.tz_localize(None)
us["spx_close"] = pd.to_numeric(us["spx_close"], errors="coerce")
us["vix"] = pd.to_numeric(us["vix"], errors="coerce")

# Compute derived signals
print("Computing US shock signals...")
us["spx_ret_20d"] = us["spx_close"] / us["spx_close"].shift(20) - 1
us["spx_ret_60d"] = us["spx_close"] / us["spx_close"].shift(60) - 1
us["spx_ma200"]   = us["spx_close"].rolling(200, min_periods=200).mean()
us["spx_ma200_dev"] = us["spx_close"]/us["spx_ma200"] - 1
# Drawdown from running max (1y rolling)
us["spx_max_1y"] = us["spx_close"].rolling(252, min_periods=60).max()
us["spx_dd_1y"]  = us["spx_close"]/us["spx_max_1y"] - 1
# VIX rolling stats
us["vix_ma60"] = us["vix"].rolling(60, min_periods=20).mean()
us["vix_ma252"] = us["vix"].rolling(252, min_periods=60).mean()

# Save
out_path = os.path.join(WORKDIR, "us_market_history.csv")
us.to_csv(out_path, index=False)
print(f"\nSaved → {out_path} ({len(us)} rows)")

# Summary
print(f"\nLatest row ({us['time'].iloc[-1].date()}):")
last = us.iloc[-1]
print(f"  SPX = {last['spx_close']:.1f}  VIX = {last['vix']:.1f}")
print(f"  SPX 20d ret = {last['spx_ret_20d']*100:+.2f}%  60d ret = {last['spx_ret_60d']*100:+.2f}%")
print(f"  SPX MA200 dev = {last['spx_ma200_dev']*100:+.2f}%  1Y DD = {last['spx_dd_1y']*100:+.2f}%")
print(f"  VIX 60d MA = {last['vix_ma60']:.1f}  252d MA = {last['vix_ma252']:.1f}")

# Notable historical shock days
print(f"\nHistorical SHOCK days (VIX > 40 OR spx_ret_60d < -20%):")
shock = us[((us["vix"] > 40) | (us["spx_ret_60d"] < -0.20)) & us["time"].between("2007-01-01", "2013-12-31")]
print(f"  2007-2013: {len(shock)} shock days")
if len(shock) > 0:
    print(f"  First: {shock['time'].iloc[0].date()} | Last: {shock['time'].iloc[-1].date()}")
    print(f"  Peak VIX: {shock['vix'].max():.1f}  Worst 60d ret: {shock['spx_ret_60d'].min()*100:+.2f}%")
