#!/usr/bin/env python3
"""Quick comparative check on SIP, REE, DCM."""
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

for tk in ["SIP", "REE", "DCM"]:
    print(f"\n{'='*100}")
    print(f"  {tk} — QUICK ASSESSMENT")
    print(f"{'='*100}")

    # FA history
    fa_tk = fa[fa["ticker"]==tk].sort_values("quarter")
    n_q = len(fa_tk)
    n_A = (fa_tk["tier"]=="A").sum()
    n_AB = (fa_tk["tier"].isin(["A","B"])).sum()
    print(f"\n  FA history: {n_q} quarters | A: {n_A} ({n_A/max(n_q,1)*100:.1f}%) | A+B: {n_AB} ({n_AB/max(n_q,1)*100:.1f}%)")
    if n_q > 0:
        recent_tiers = fa_tk.tail(6)[["quarter","tier","score"]].to_string(index=False)
        print(f"  Recent 6Q:\n{recent_tiers}")

    # Fundamentals last 8Q
    fin = bq_query(f"""
    SELECT f.quarter, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
      f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.PE, f.PB, f.DY,
      f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.IntCov_P0, f.totalAsset_P0,
      f.AdvCust_P0, f.UnearnRev_P0, f.OShares
    FROM tav2_bq.ticker_financial AS f
    WHERE f.ticker = '{tk}' AND f.time >= '2023-01-01'
    ORDER BY f.time
    """)
    print(f"\n  --- Fundamentals last 8Q ---")
    print(f"  {'Quarter':<10}{'NP (B)':>10}{'NP yoy':>10}{'Rev yoy':>10}{'GPM':>8}{'ROE':>8}{'PE':>7}{'PB':>6}{'DY':>7}{'Debt/Eq':>10}")
    for _, r in fin.tail(8).iterrows():
        np_yoy = (r["NP_P0"]/r["NP_P4"] - 1)*100 if r["NP_P4"] and r["NP_P4"] != 0 else None
        rev_yoy = (r["Revenue_P0"]/r["Revenue_P4"] - 1)*100 if r["Revenue_P4"] and r["Revenue_P4"] != 0 else None
        debt = (r["StDebt_P0"] or 0) + (r["LtDebt_P0"] or 0)
        equity = (r["totalAsset_P0"] or 0) - debt
        debt_eq = debt / equity if equity > 0 else None
        np_yoy_s = f"{np_yoy:+7.1f}%" if np_yoy is not None else "    n/a"
        rev_yoy_s = f"{rev_yoy:+7.1f}%" if rev_yoy is not None else "    n/a"
        de_s = f"{debt_eq:>9.2f}x" if debt_eq is not None else "      n/a"
        gpm = r["GPM_P0"]*100 if pd.notna(r["GPM_P0"]) else 0
        roe = r["ROE_Trailing"]*100 if pd.notna(r["ROE_Trailing"]) else 0
        dy = r["DY"]*100 if pd.notna(r["DY"]) else 0
        pe = r["PE"] if pd.notna(r["PE"]) else 0
        pb = r["PB"] if pd.notna(r["PB"]) else 0
        print(f"  {r['quarter']:<10}{r['NP_P0']/1e9:>9.1f}B{np_yoy_s:>10}{rev_yoy_s:>10}{gpm:>+7.1f}%{roe:>+7.1f}%{pe:>7.1f}{pb:>+5.1f}{dy:>+6.1f}%{de_s:>10}")

    # Current price + key levels
    px = bq_query(f"""
    SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume_3M_P50,
      t.Volume_3M_P50 * t.Close AS liq
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = '{tk}' AND t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 10 DAY)
    ORDER BY t.time DESC LIMIT 1
    """)
    if len(px) > 0:
        r = px.iloc[0]
        vs50 = (r["Close"]/r["MA50"]-1)*100 if pd.notna(r["MA50"]) and r["MA50"] > 0 else None
        vs200 = (r["Close"]/r["MA200"]-1)*100 if pd.notna(r["MA200"]) and r["MA200"] > 0 else None
        vs50_s = f"{vs50:+.1f}%" if vs50 is not None else "n/a"
        vs200_s = f"{vs200:+.1f}%" if vs200 is not None else "n/a"
        print(f"\n  --- Price snapshot ({r['time']}) ---")
        print(f"  Close: {r['Close']:.0f} | %MA50: {vs50_s} | %MA200: {vs200_s} | RSI: {r['D_RSI']*100:.1f}%")
        print(f"  Liquidity: {r['liq']/1e9:.1f}B VND/day")

    # Price journey
    print(f"\n  --- Yearly price journey ---")
    px_yr = bq_query(f"""
    SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS lo, MAX(t.Close) AS hi, AVG(t.Close) AS avg
    FROM tav2_bq.ticker AS t WHERE t.ticker = '{tk}' AND t.time >= '2020-01-01'
    GROUP BY yr ORDER BY yr
    """)
    print(f"  {'Year':<6}{'Min':>9}{'Avg':>9}{'Max':>9}")
    for _, r in px_yr.iterrows():
        print(f"  {int(r['yr']):<6}{r['lo']:>9.0f}{r['avg']:>9.0f}{r['hi']:>9.0f}")
