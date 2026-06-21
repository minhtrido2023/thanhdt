#!/usr/bin/env python3
"""GMD analysis + BMP cyclicality check (PVC input cost vulnerability)."""
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

# ─── GMD Analysis ────────────────────────────────────────────────────────
print("="*100)
print("  GMD (Gemadept) — Port + Logistics")
print("="*100)

fa_tk = fa[fa["ticker"]=="GMD"].sort_values("quarter")
print(f"\n  FA history: {len(fa_tk)} quarters | A: {(fa_tk['tier']=='A').sum()} ({(fa_tk['tier']=='A').sum()/max(len(fa_tk),1)*100:.1f}%) | A+B: {(fa_tk['tier'].isin(['A','B'])).sum()} ({(fa_tk['tier'].isin(['A','B'])).sum()/max(len(fa_tk),1)*100:.1f}%)")
print(f"  Recent 8Q tiers: {fa_tk.tail(8)[['quarter','tier']].to_string(index=False)}")

fin_gmd = bq_query("""
SELECT f.quarter, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
  f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.ROIC_Trailing, f.PE, f.PB, f.DY,
  f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.IntCov_P0, f.totalAsset_P0, f.OShares
FROM tav2_bq.ticker_financial AS f
WHERE f.ticker = 'GMD' AND f.time >= '2022-01-01'
ORDER BY f.time
""")

print(f"\n  --- GMD Fundamentals last 10Q ---")
print(f"  {'Quarter':<10}{'NP (B)':>10}{'NP yoy':>10}{'Rev yoy':>10}{'GPM':>8}{'NPM':>8}{'ROE':>8}{'PE':>7}{'PB':>6}{'Debt/Eq':>10}")
for _, r in fin_gmd.tail(10).iterrows():
    np_yoy = (r["NP_P0"]/r["NP_P4"] - 1)*100 if r["NP_P4"] and r["NP_P4"] != 0 else None
    rev_yoy = (r["Revenue_P0"]/r["Revenue_P4"] - 1)*100 if r["Revenue_P4"] and r["Revenue_P4"] != 0 else None
    debt = (r["StDebt_P0"] or 0) + (r["LtDebt_P0"] or 0)
    equity = (r["totalAsset_P0"] or 0) - debt
    de = debt / equity if equity > 0 else None
    np_s = f"{np_yoy:+7.1f}%" if np_yoy is not None else "    n/a"
    rev_s = f"{rev_yoy:+7.1f}%" if rev_yoy is not None else "    n/a"
    de_s = f"{de:9.2f}x" if de is not None else "      n/a"
    print(f"  {r['quarter']:<10}{r['NP_P0']/1e9:>9.1f}B{np_s:>10}{rev_s:>10}{r['GPM_P0']*100:>+7.1f}%{r['NPM_P0']*100:>+7.1f}%{r['ROE_Trailing']*100:>+7.1f}%{r['PE']:>7.1f}{r['PB']:>+5.1f}{de_s:>10}")

px_gmd = bq_query("SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume_3M_P50*t.Close AS liq FROM tav2_bq.ticker AS t WHERE t.ticker = 'GMD' ORDER BY t.time DESC LIMIT 1")
r = px_gmd.iloc[0]
vs50 = (r["Close"]/r["MA50"]-1)*100
vs200 = (r["Close"]/r["MA200"]-1)*100
print(f"\n  Price snapshot: {r['Close']:.0f} | %MA50: {vs50:+.1f}% | %MA200: {vs200:+.1f}% | RSI: {r['D_RSI']*100:.1f}% | Liq: {r['liq']/1e9:.1f}B/day")

px_long = bq_query("""
SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS lo, MAX(t.Close) AS hi, AVG(t.Close) AS avg
FROM tav2_bq.ticker AS t WHERE t.ticker = 'GMD' AND t.time >= '2018-01-01'
GROUP BY yr ORDER BY yr
""")
print(f"\n  Long-term price:")
print(f"  {'Year':<6}{'Min':>9}{'Max':>9}{'Avg':>9}")
for _, r in px_long.iterrows():
    print(f"  {int(r['yr']):<6}{r['lo']:>9.0f}{r['hi']:>9.0f}{r['avg']:>9.0f}")

# ─── BMP Cyclicality Deep-Dive ───────────────────────────────────────────
print(f"\n{'='*100}")
print("  BMP — Cyclicality Investigation (Input Cost Risk)")
print(f"{'='*100}")

# BMP full history to see cycles
fin_bmp = bq_query("""
SELECT f.quarter, f.time, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
  f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.PE, f.PB, f.DY,
  f.Cash_P0, f.totalAsset_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.ticker = 'BMP' AND f.time >= '2015-01-01'
ORDER BY f.time
""")
fin_bmp["time"] = pd.to_datetime(fin_bmp["time"])

# Compute NP_TTM and GPM trend
fin_bmp["NP_TTM"] = fin_bmp["NP_P0"].rolling(4).sum()
fin_bmp_recent = fin_bmp.tail(20).copy()

print(f"\n  --- BMP Quarterly history (last 20Q) — see GPM-NP correlation ---")
print(f"  {'Quarter':<10}{'NP (B)':>10}{'NP_TTM (B)':>13}{'GPM':>8}{'NPM':>8}{'ROE':>8}{'PE':>7}")
for _, r in fin_bmp_recent.iterrows():
    gpm = r["GPM_P0"]*100 if pd.notna(r["GPM_P0"]) else 0
    npm = r["NPM_P0"]*100 if pd.notna(r["NPM_P0"]) else 0
    roe = r["ROE_Trailing"]*100 if pd.notna(r["ROE_Trailing"]) else 0
    pe = r["PE"] if pd.notna(r["PE"]) else 0
    np_ttm = r["NP_TTM"]/1e9 if pd.notna(r["NP_TTM"]) else 0
    print(f"  {r['quarter']:<10}{r['NP_P0']/1e9:>9.1f}B{np_ttm:>12.1f}B{gpm:>+7.1f}%{npm:>+7.1f}%{roe:>+7.1f}%{pe:>7.1f}")

# BMP price history vs GPM
print(f"\n  --- BMP yearly price + earnings ---")
px_bmp = bq_query("""
SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS lo, MAX(t.Close) AS hi, AVG(t.Close) AS avg
FROM tav2_bq.ticker AS t WHERE t.ticker = 'BMP' AND t.time >= '2015-01-01'
GROUP BY yr ORDER BY yr
""")
yearly_np = fin_bmp.groupby(fin_bmp["time"].dt.year).agg(
    np_total=("NP_P0", "sum"),
    avg_gpm=("GPM_P0", "mean"),
).reset_index().rename(columns={"time":"yr"})

print(f"  {'Year':<6}{'Min px':>9}{'Max px':>9}{'Avg px':>9}{'Annual NP (B)':>15}{'Avg GPM':>10}")
merged = px_bmp.merge(yearly_np, on="yr", how="left")
for _, r in merged.iterrows():
    np_t = r['np_total']/1e9 if pd.notna(r['np_total']) else 0
    gpm = r['avg_gpm']*100 if pd.notna(r['avg_gpm']) else 0
    print(f"  {int(r['yr']):<6}{r['lo']:>9.0f}{r['hi']:>9.0f}{r['avg']:>9.0f}{np_t:>14.0f}B{gpm:>+9.1f}%")

# BMP price snapshot
px_bmp_now = bq_query("SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker = 'BMP' ORDER BY t.time DESC LIMIT 1")
r = px_bmp_now.iloc[0]
print(f"\n  BMP current: {r['Close']:.0f} | %MA50: {(r['Close']/r['MA50']-1)*100:+.1f}% | %MA200: {(r['Close']/r['MA200']-1)*100:+.1f}% | RSI: {r['D_RSI']*100:.1f}%")
