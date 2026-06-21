# -*- coding: utf-8 -*-
"""
save_macro_data.py
==================
Lưu dữ liệu macro Việt Nam vào các file CSV để dùng lại.
Sources:
  - USD/VND daily  : Yahoo Finance (USDVND=X)
  - Lending rate   : World Bank API (FR.INR.LEND) — annual
  - CPI inflation  : World Bank API (FP.CPI.TOTL.ZG) — annual
  - USD/VND annual : World Bank API (PA.NUS.FCRF) — annual
Chạy lại file này để cập nhật dữ liệu mới nhất.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd
import requests
import json
import os

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ─── 1. USD/VND daily (Yahoo Finance via yfinance) ────────────────────────────
print("1. Downloading USD/VND daily (yfinance USDVND=X)...")
try:
    import yfinance as yf
    df_fx = yf.download("USDVND=X", start="2003-01-01", end="2026-12-31",
                        auto_adjust=True, progress=False)
    df_fx.columns = [c[0] if isinstance(c, tuple) else c for c in df_fx.columns]
    df_fx = df_fx.reset_index()[["Date","Close"]].rename(columns={"Date":"time","Close":"usdvnd"})
    df_fx["time"] = pd.to_datetime(df_fx["time"]).dt.normalize()
    df_fx = df_fx.dropna().sort_values("time").reset_index(drop=True)
    path_fx = os.path.join(WORKDIR, "macro_usdvnd.csv")
    df_fx.to_csv(path_fx, index=False)
    print(f"   Saved {len(df_fx)} rows: {df_fx['time'].iloc[0].date()} to {df_fx['time'].iloc[-1].date()}")
    print(f"   Range: {df_fx['usdvnd'].min():.0f} - {df_fx['usdvnd'].max():.0f} VND/USD")
except Exception as e:
    print(f"   ERROR: {e}")

# ─── 2. World Bank macro data (annual) ───────────────────────────────────────
def fetch_wb(indicator, name):
    url = f"https://api.worldbank.org/v2/country/VN/indicator/{indicator}?format=json&per_page=100&mrv=100"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()[1]  # [0] = metadata, [1] = data list
        rows = [(int(d["date"]), d["value"]) for d in data if d["value"] is not None]
        df = pd.DataFrame(rows, columns=["year", name]).sort_values("year").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"   ERROR fetching {indicator}: {e}")
        return pd.DataFrame(columns=["year", name])

print("2. Downloading Vietnam lending rate (World Bank FR.INR.LEND)...")
df_rate = fetch_wb("FR.INR.LEND", "lending_rate")
print(f"   Got {len(df_rate)} annual rows: {df_rate['year'].min()} - {df_rate['year'].max()}")

print("3. Downloading Vietnam CPI inflation (World Bank FP.CPI.TOTL.ZG)...")
df_cpi = fetch_wb("FP.CPI.TOTL.ZG", "cpi_yoy")
print(f"   Got {len(df_cpi)} annual rows: {df_cpi['year'].min()} - {df_cpi['year'].max()}")

print("4. Downloading Vietnam USD/VND annual average (World Bank PA.NUS.FCRF)...")
df_fx_ann = fetch_wb("PA.NUS.FCRF", "usdvnd_annual")
print(f"   Got {len(df_fx_ann)} annual rows: {df_fx_ann['year'].min()} - {df_fx_ann['year'].max()}")

# ─── 3. Merge annual data ─────────────────────────────────────────────────────
print("5. Merging annual macro data...")
df_macro = df_rate.merge(df_cpi, on="year", how="outer")
df_macro = df_macro.merge(df_fx_ann, on="year", how="outer")
df_macro = df_macro.sort_values("year").reset_index(drop=True)

# Derived: USD/VND annual YoY change (depreciation rate)
df_macro["usdvnd_chg"] = df_macro["usdvnd_annual"].pct_change() * 100

# Macro regime classification (annual)
# tightening: lending_rate > 12 OR cpi_yoy > 10 OR usdvnd_chg > 3
# easing: lending_rate < 9 AND cpi_yoy < 4 AND usdvnd_chg < 1.5
def classify_macro(row):
    r   = row.get("lending_rate", np.nan)
    cpi = row.get("cpi_yoy",      np.nan)
    chg = row.get("usdvnd_chg",   np.nan)
    if pd.isna(r) or pd.isna(cpi): return "unknown"
    if r > 12 or cpi > 10: return "tight"
    if (not pd.isna(chg) and chg > 3): return "tight"
    if r < 9 and cpi < 4: return "easy"
    return "neutral"

df_macro["macro_regime"] = df_macro.apply(classify_macro, axis=1)
path_macro = os.path.join(WORKDIR, "macro_annual.csv")
df_macro.to_csv(path_macro, index=False)
print(f"   Saved macro_annual.csv ({len(df_macro)} rows)")
print(df_macro[["year","lending_rate","cpi_yoy","usdvnd_annual","usdvnd_chg","macro_regime"]].tail(12).to_string(index=False))

# ─── 4. Build daily macro DataFrame (interpolate annual → daily) ──────────────
print("\n6. Building daily macro series (interpolate annual -> daily)...")

# Create daily date range 2000-2026
dates_daily = pd.date_range("2000-01-01", "2026-12-31", freq="D")
df_daily = pd.DataFrame({"time": dates_daily})
df_daily["year"] = df_daily["time"].dt.year

# Merge annual macro onto daily by year
df_daily = df_daily.merge(df_macro[["year","lending_rate","cpi_yoy","usdvnd_annual","usdvnd_chg","macro_regime"]],
                          on="year", how="left")

# Merge daily USD/VND (forward-fill gaps for weekends/holidays)
if "df_fx" in dir() and len(df_fx) > 0:
    df_daily = df_daily.merge(df_fx[["time","usdvnd"]], on="time", how="left")
    df_daily["usdvnd"] = df_daily["usdvnd"].ffill()
    # 52-week rolling change in USD/VND (depreciation signal)
    df_daily["usdvnd_1y_chg"] = df_daily["usdvnd"].pct_change(252) * 100
    # 3-month rolling change
    df_daily["usdvnd_3m_chg"] = df_daily["usdvnd"].pct_change(63) * 100

path_daily = os.path.join(WORKDIR, "macro_daily.csv")
df_daily[["time","lending_rate","cpi_yoy","usdvnd","usdvnd_1y_chg","usdvnd_3m_chg","macro_regime"]].to_csv(
    path_daily, index=False)
print(f"   Saved macro_daily.csv ({len(df_daily)} rows)")
print(df_daily[["time","lending_rate","cpi_yoy","usdvnd","usdvnd_1y_chg","macro_regime"]].dropna(subset=["usdvnd"]).tail(5).to_string(index=False))

print("\nDone. Files saved:")
print(f"  macro_usdvnd.csv   — USD/VND daily (Yahoo Finance, 2003-now)")
print(f"  macro_annual.csv   — Lending rate + CPI + USD/VND annual + regime (World Bank)")
print(f"  macro_daily.csv    — Daily interpolated macro signals + rolling USD/VND changes")
