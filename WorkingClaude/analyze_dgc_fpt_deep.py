#!/usr/bin/env python3
"""
analyze_dgc_fpt_deep.py
=======================
Deep dive on DGC and FPT — user holds 200B DGC + considering FPT entry.
"""
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

# Pull last 12 quarters of fundamentals + last 1Y daily prices
for tk in ["DGC", "FPT"]:
    print(f"\n{'='*100}")
    print(f"  {tk} — DEEP ANALYSIS")
    print(f"{'='*100}")

    fin = bq_query(f"""
    SELECT f.ticker, f.quarter, f.time, f.Release_Date,
      f.NP_P0, f.NP_P1, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
      f.GPM_P0, f.GPM_P4, f.NPM_P0, f.NPM_P4,
      f.ROIC_Trailing, f.ROE_Trailing, f.ROE_Min5Y,
      f.PE, f.PE_MA5Y, f.PB, f.DY, f.EPS_P0,
      f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.EBITDA_P0, f.IntCov_P0,
      f.AdvCust_P0, f.UnearnRev_P0, f.Inventory_P0, f.OShares
    FROM tav2_bq.ticker_financial AS f
    WHERE f.ticker = '{tk}' AND f.time >= '2022-01-01'
    ORDER BY f.time DESC
    """)
    fin["time"] = pd.to_datetime(fin["time"])

    # FA tier history
    fa = pd.read_csv("data/fa_ratings_lh.csv")
    fa_tk = fa[fa["ticker"]==tk].sort_values("quarter").tail(12)

    print(f"\n--- Fundamentals last 12Q ---")
    print(f"  {'Quarter':<10}{'NP_TTM (B)':>13}{'NP_yoy':>10}{'Rev_yoy':>10}{'GPM':>8}{'NPM':>8}{'ROE':>8}{'PE':>8}{'Cash (B)':>12}{'FA':>4}")
    np_ttm_list = []
    rev_yoy_list = []
    for _, r in fin.head(12).sort_values("time").iterrows():
        np_ttm = (fin[fin["quarter"]==r["quarter"]]["NP_P0"].iloc[0]) if False else r["NP_P0"]
        # TTM NP: P0+P1+P2+P3 from any row's perspective
        pass
    # Simpler: use NP_P0 / NP_P4 for YoY
    fin_sorted = fin.sort_values("time")
    for _, r in fin_sorted.tail(12).iterrows():
        np_yoy = (r["NP_P0"]/r["NP_P4"] - 1)*100 if r["NP_P4"] not in [0, None] and pd.notna(r["NP_P4"]) else None
        rev_yoy = (r["Revenue_P0"]/r["Revenue_P4"] - 1)*100 if r["Revenue_P4"] not in [0, None] and pd.notna(r["Revenue_P4"]) else None
        q = r["quarter"]
        fa_row = fa_tk[fa_tk["quarter"]==q]
        fa_tier = fa_row["tier"].iloc[0] if len(fa_row) > 0 else "-"
        np_yoy_str = f"{np_yoy:+7.1f}%" if np_yoy is not None else "    n/a"
        rev_yoy_str = f"{rev_yoy:+7.1f}%" if rev_yoy is not None else "    n/a"
        cash_b = r["Cash_P0"]/1e9 if pd.notna(r["Cash_P0"]) else None
        cash_str = f"{cash_b:>9.0f}B" if cash_b else "      n/a"
        print(f"  {q:<10}{r['NP_P0']/1e9:>12.0f}B{np_yoy_str:>10}{rev_yoy_str:>10}{r['GPM_P0']*100:>+7.1f}%{r['NPM_P0']*100:>+7.1f}%{r['ROE_Trailing']*100:>+7.1f}%{r['PE']:>8.1f}{cash_str:>12}{fa_tier:>4}")

    # Last quarter snapshot
    if len(fin) > 0:
        latest = fin.sort_values("time").iloc[-1]
        print(f"\n--- Latest quarter snapshot ({latest['quarter']} released {latest['Release_Date']}) ---")
        mcap = latest["OShares"] * (50800 if tk=="DGC" else 73900)  # use current px as proxy
        print(f"  OShares: {latest['OShares']/1e6:.1f}M | est MktCap: {mcap/1e9:.0f}B VND")
        print(f"  Cash on balance: {latest['Cash_P0']/1e9:.0f}B  (Cash/MktCap: {latest['Cash_P0']/mcap*100:.1f}%)")
        print(f"  Debt: ST {latest['StDebt_P0']/1e9:.0f}B + LT {latest['LtDebt_P0']/1e9:.0f}B = {(latest['StDebt_P0']+latest['LtDebt_P0'])/1e9:.0f}B")
        print(f"  IntCov: {latest['IntCov_P0']:.1f}x  EBITDA Q0: {latest['EBITDA_P0']/1e9:.0f}B")
        print(f"  AdvCust: {latest['AdvCust_P0']/1e9:.1f}B  UnearnRev: {latest['UnearnRev_P0']/1e9:.1f}B  Inventory: {latest['Inventory_P0']/1e9:.0f}B")

    # Price action
    print(f"\n--- Price action 6M ---")
    px = bq_query(f"""
    SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume, t.Volume_3M_P50
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = '{tk}'
      AND t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
    ORDER BY t.time DESC LIMIT 15
    """)
    px["time"] = pd.to_datetime(px["time"])
    print(f"  {'Date':<12}{'Close':>9}{'MA50':>9}{'MA200':>9}{'vs MA50':>10}{'vs MA200':>11}{'RSI':>7}{'Vol/AvgVol':>12}")
    for _, r in px.sort_values("time").tail(15).iterrows():
        vs50 = (r["Close"]/r["MA50"]-1)*100 if pd.notna(r["MA50"]) else None
        vs200 = (r["Close"]/r["MA200"]-1)*100 if pd.notna(r["MA200"]) else None
        v_ratio = r["Volume"]/r["Volume_3M_P50"] if pd.notna(r["Volume_3M_P50"]) and r["Volume_3M_P50"] > 0 else None
        vs50_s = f"{vs50:+8.1f}%" if vs50 is not None else "     n/a"
        vs200_s = f"{vs200:+9.1f}%" if vs200 is not None else "      n/a"
        v_s = f"{v_ratio:+10.2f}x" if v_ratio is not None else "       n/a"
        print(f"  {r['time'].strftime('%Y-%m-%d'):<12}{r['Close']:>9.0f}{r['MA50']:>9.0f}{r['MA200']:>9.0f}{vs50_s:>10}{vs200_s:>11}{r['D_RSI']*100:>+6.1f}%{v_s:>12}")
