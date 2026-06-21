#!/usr/bin/env python3
"""PVT (PetroVietnam Transport) — oil/gas tanker analysis."""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

fa = pd.read_csv("fa_ratings_lh.csv")

# PVT analysis
fa_tk = fa[fa["ticker"]=="PVT"].sort_values("quarter")
print("="*100)
print("  PVT (PetroVietnam Transport) — Oil/Gas Tanker")
print("="*100)
print(f"\n  FA history: {len(fa_tk)} quarters | A: {(fa_tk['tier']=='A').sum()} ({(fa_tk['tier']=='A').sum()/max(len(fa_tk),1)*100:.1f}%) | A+B: {(fa_tk['tier'].isin(['A','B'])).sum()} ({(fa_tk['tier'].isin(['A','B'])).sum()/max(len(fa_tk),1)*100:.1f}%)")
print(f"\n  Recent 10Q FA tiers:")
print(fa_tk.tail(10)[["quarter","tier","score"]].to_string(index=False))

# Fundamentals
fin = bq_query("""
SELECT f.quarter, f.time, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
  f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.ROIC_Trailing, f.PE, f.PB, f.DY,
  f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.IntCov_P0, f.totalAsset_P0, f.OShares,
  f.ROE_Min5Y, f.NP_R, f.FSCORE
FROM tav2_bq.ticker_financial AS f
WHERE f.ticker = 'PVT' AND f.time >= '2018-01-01'
ORDER BY f.time
""")
fin["time"] = pd.to_datetime(fin["time"])
fin["NP_TTM"] = fin["NP_P0"].rolling(4).sum()

print(f"\n  --- Fundamentals last 12Q ---")
print(f"  {'Quarter':<10}{'NP (B)':>9}{'NP_TTM':>10}{'NP yoy':>10}{'Rev yoy':>10}{'GPM':>8}{'NPM':>8}{'ROE':>8}{'PE':>7}{'PB':>6}{'Debt/Eq':>10}")
for _, r in fin.tail(12).iterrows():
    np_yoy = (r["NP_P0"]/r["NP_P4"] - 1)*100 if r["NP_P4"] and r["NP_P4"] != 0 else None
    rev_yoy = (r["Revenue_P0"]/r["Revenue_P4"] - 1)*100 if r["Revenue_P4"] and r["Revenue_P4"] != 0 else None
    debt = (r["StDebt_P0"] or 0) + (r["LtDebt_P0"] or 0)
    equity = (r["totalAsset_P0"] or 0) - debt
    de = debt / equity if equity > 0 else None
    np_s = f"{np_yoy:+7.1f}%" if np_yoy is not None else "    n/a"
    rev_s = f"{rev_yoy:+7.1f}%" if rev_yoy is not None else "    n/a"
    de_s = f"{de:9.2f}x" if de is not None else "      n/a"
    np_ttm = r["NP_TTM"]/1e9 if pd.notna(r["NP_TTM"]) else 0
    print(f"  {r['quarter']:<10}{r['NP_P0']/1e9:>8.1f}B{np_ttm:>9.0f}B{np_s:>10}{rev_s:>10}{r['GPM_P0']*100:>+7.1f}%{r['NPM_P0']*100:>+7.1f}%{r['ROE_Trailing']*100:>+7.1f}%{r['PE']:>7.1f}{r['PB']:>+5.1f}{de_s:>10}")

# Long-term yearly NP + GPM
print(f"\n  --- Yearly NP + GPM (since 2018) — cycle check ---")
yr = fin.groupby(fin["time"].dt.year).agg(
    np_total=("NP_P0", "sum"),
    avg_gpm=("GPM_P0", "mean"),
    avg_roe=("ROE_Trailing", "mean"),
).reset_index().rename(columns={"time":"yr"})
print(f"  {'Year':<6}{'Annual NP (B)':>15}{'Avg GPM':>10}{'Avg ROE':>10}")
for _, r in yr.iterrows():
    print(f"  {int(r['yr']):<6}{r['np_total']/1e9:>14.0f}B{r['avg_gpm']*100:>+9.1f}%{r['avg_roe']*100:>+9.1f}%")

# Price journey
px_yr = bq_query("""
SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS lo, MAX(t.Close) AS hi, AVG(t.Close) AS avg
FROM tav2_bq.ticker AS t WHERE t.ticker = 'PVT' AND t.time >= '2015-01-01'
GROUP BY yr ORDER BY yr
""")
print(f"\n  --- Yearly price journey ---")
print(f"  {'Year':<6}{'Min':>9}{'Avg':>9}{'Max':>9}{'Range %':>11}")
for _, r in px_yr.iterrows():
    range_pct = (r["hi"]/r["lo"] - 1) * 100
    print(f"  {int(r['yr']):<6}{r['lo']:>9.0f}{r['avg']:>9.0f}{r['hi']:>9.0f}{range_pct:>+10.1f}%")

# Price snapshot
px_now = bq_query("SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume_3M_P50*t.Close AS liq FROM tav2_bq.ticker AS t WHERE t.ticker = 'PVT' ORDER BY t.time DESC LIMIT 5")
print(f"\n  --- Recent price ---")
for _, r in px_now.sort_values("time").iterrows():
    vs50 = (r["Close"]/r["MA50"]-1)*100 if pd.notna(r["MA50"]) else None
    vs200 = (r["Close"]/r["MA200"]-1)*100 if pd.notna(r["MA200"]) else None
    print(f"  {r['time']} Close: {r['Close']:.0f} | %MA50: {vs50:+.1f}% | %MA200: {vs200:+.1f}% | RSI: {r['D_RSI']*100:.1f}%")

# Latest balance sheet
print(f"\n  --- Latest balance sheet ---")
latest = fin.iloc[-1]
debt = (latest["StDebt_P0"] or 0) + (latest["LtDebt_P0"] or 0)
print(f"  Total Asset: {latest['totalAsset_P0']/1e9:.0f}B")
print(f"  Total Debt: {debt/1e9:.0f}B ({debt/latest['totalAsset_P0']*100:.1f}% of asset)")
print(f"  Cash: {latest['Cash_P0']/1e9:.0f}B ({latest['Cash_P0']/latest['totalAsset_P0']*100:.1f}% of asset)")
print(f"  IntCov: {latest['IntCov_P0']:.1f}x")
print(f"  OShares: {latest['OShares']/1e6:.1f}M")
print(f"  ROE_Min5Y: {latest['ROE_Min5Y']*100:.1f}% (worst-year ROE)")
print(f"  FSCORE: {latest['FSCORE']:.0f}")

# 12y price multiple
px_first = bq_query("SELECT t.Close FROM tav2_bq.ticker AS t WHERE t.ticker = 'PVT' AND t.time >= '2014-01-01' ORDER BY t.time LIMIT 1")
px_now_close = bq_query("SELECT t.Close FROM tav2_bq.ticker AS t WHERE t.ticker = 'PVT' ORDER BY t.time DESC LIMIT 1")
if len(px_first) and len(px_now_close):
    p0 = px_first["Close"].iloc[0]
    pn = px_now_close["Close"].iloc[0]
    yrs = 12.3
    cagr = (pn/p0)**(1/yrs) - 1
    print(f"\n  Long-term: {p0:.0f} → {pn:.0f} = {pn/p0:.2f}x in {yrs:.1f}y (CAGR +{cagr*100:.1f}%)")
