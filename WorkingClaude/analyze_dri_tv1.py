#!/usr/bin/env python3
"""
analyze_dri_tv1.py
==================
Deep analysis on DRI and TV1 — user has been holding 1Y, wants assessment.
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

for tk in ["DRI", "TV1"]:
    print(f"\n{'='*100}")
    print(f"  {tk} — DEEP ANALYSIS")
    print(f"{'='*100}")

    # Basic info first
    info = bq_query(f"""
    SELECT t.ticker, MIN(t.time) AS first_dt, MAX(t.time) AS last_dt,
      t.ICB_Code, AVG(t.Volume_3M_P50 * t.Close) AS avg_liq
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = '{tk}' AND t.time >= '2020-01-01'
    GROUP BY t.ticker, t.ICB_Code
    """)
    if len(info) == 0:
        print(f"  NO data found for {tk}")
        continue
    print(f"\n  ICB Code: {info.iloc[0]['ICB_Code']}")
    print(f"  Data range: {info.iloc[0]['first_dt']} → {info.iloc[0]['last_dt']}")
    print(f"  Avg liquidity: {info['avg_liq'].iloc[0]/1e9:.2f}B VND/day")

    # Fundamentals last 12Q
    fin = bq_query(f"""
    SELECT f.ticker, f.quarter, f.time, f.Release_Date,
      f.NP_P0, f.NP_P1, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
      f.GPM_P0, f.GPM_P4, f.NPM_P0,
      f.ROIC_Trailing, f.ROE_Trailing, f.ROE_Min5Y, f.ROE3Y,
      f.PE, f.PE_MA5Y, f.PB, f.DY, f.EPS_P0, f.BVPS,
      f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.EBITDA_P0, f.IntCov_P0,
      f.AdvCust_P0, f.UnearnRev_P0, f.Inventory_P0, f.OShares,
      f.totalAsset_P0, f.NP_R, f.Revenue_YoY_P0, f.FSCORE
    FROM tav2_bq.ticker_financial AS f
    WHERE f.ticker = '{tk}' AND f.time >= '2021-01-01'
    ORDER BY f.time
    """)
    fin["time"] = pd.to_datetime(fin["time"])

    fa = pd.read_csv("data/fa_ratings_lh.csv")
    fa_tk = fa[fa["ticker"]==tk].sort_values("quarter")

    print(f"\n--- Fundamentals last 12Q ---")
    print(f"  {'Quarter':<10}{'NP_P0 (B)':>12}{'NP_yoy':>10}{'Rev_yoy':>10}{'GPM':>8}{'NPM':>8}{'ROE':>8}{'PE':>8}{'PB':>7}{'DY':>7}{'Debt/Eq':>10}{'FA':>4}")
    for _, r in fin.tail(12).iterrows():
        np_yoy = (r["NP_P0"]/r["NP_P4"] - 1)*100 if r["NP_P4"] not in [0, None] and pd.notna(r["NP_P4"]) and r["NP_P4"] != 0 else None
        rev_yoy = (r["Revenue_P0"]/r["Revenue_P4"] - 1)*100 if r["Revenue_P4"] not in [0, None] and pd.notna(r["Revenue_P4"]) and r["Revenue_P4"] != 0 else None
        q = r["quarter"]
        fa_row = fa_tk[fa_tk["quarter"]==q]
        fa_tier = fa_row["tier"].iloc[0] if len(fa_row) > 0 else "-"
        np_yoy_str = f"{np_yoy:+7.1f}%" if np_yoy is not None else "    n/a"
        rev_yoy_str = f"{rev_yoy:+7.1f}%" if rev_yoy is not None else "    n/a"
        debt_total = (r["StDebt_P0"] or 0) + (r["LtDebt_P0"] or 0)
        # Equity = totalAsset - debt (approx)
        equity_proxy = (r["totalAsset_P0"] or 0) - debt_total - (r["StDebt_P0"] or 0)
        debt_eq = debt_total / max(r["totalAsset_P0"] - debt_total, 1) if r["totalAsset_P0"] else None
        debt_eq_str = f"{debt_eq:>9.2f}x" if debt_eq is not None else "      n/a"
        dy_str = f"{r['DY']*100:+5.1f}%" if pd.notna(r['DY']) else "  n/a"
        npm = r["NPM_P0"]*100 if pd.notna(r["NPM_P0"]) else 0
        roe = r["ROE_Trailing"]*100 if pd.notna(r["ROE_Trailing"]) else 0
        pb = r["PB"] if pd.notna(r["PB"]) else 0
        print(f"  {q:<10}{r['NP_P0']/1e9:>11.1f}B{np_yoy_str:>10}{rev_yoy_str:>10}{r['GPM_P0']*100:>+7.1f}%{npm:>+7.1f}%{roe:>+7.1f}%{r['PE']:>8.1f}{pb:>+6.1f}{dy_str:>7}{debt_eq_str:>10}{fa_tier:>4}")

    # Cash, debt, balance sheet detail latest
    if len(fin) > 0:
        latest = fin.iloc[-1]
        print(f"\n--- Latest balance sheet snapshot ({latest['quarter']}) ---")
        cur_px_row = bq_query(f"SELECT t.Close FROM tav2_bq.ticker AS t WHERE t.ticker = '{tk}' ORDER BY t.time DESC LIMIT 1")
        cur_px = cur_px_row["Close"].iloc[0] if len(cur_px_row) > 0 else 0
        mcap = latest["OShares"] * cur_px
        print(f"  OShares: {latest['OShares']/1e6:.1f}M | Current price: {cur_px:.0f}")
        print(f"  Est MktCap: {mcap/1e9:.0f}B VND")
        cash_pct = latest["Cash_P0"]/mcap*100 if mcap > 0 and pd.notna(latest["Cash_P0"]) else None
        print(f"  Cash: {latest['Cash_P0']/1e9:.1f}B  ({cash_pct:.1f}% MktCap)" if cash_pct else f"  Cash: {latest['Cash_P0']/1e9:.1f}B")
        print(f"  Debt: ST {(latest['StDebt_P0'] or 0)/1e9:.0f}B + LT {(latest['LtDebt_P0'] or 0)/1e9:.0f}B = {((latest['StDebt_P0'] or 0)+(latest['LtDebt_P0'] or 0))/1e9:.0f}B")
        if pd.notna(latest["IntCov_P0"]):
            print(f"  IntCov: {latest['IntCov_P0']:.1f}x")
        if pd.notna(latest["BVPS"]):
            print(f"  BVPS: {latest['BVPS']:.0f} | P/BVPS: {cur_px/latest['BVPS']:.2f}x")

    # Price action recent
    print(f"\n--- Price action recent 60 trading days ---")
    px = bq_query(f"""
    SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume, t.Volume_3M_P50
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = '{tk}'
      AND t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 80 DAY)
    ORDER BY t.time DESC LIMIT 10
    """)
    px["time"] = pd.to_datetime(px["time"])
    print(f"  {'Date':<12}{'Close':>9}{'MA50':>9}{'MA200':>9}{'%MA50':>9}{'%MA200':>9}{'RSI':>7}{'Vol/Avg':>10}")
    for _, r in px.sort_values("time").iterrows():
        vs50 = (r["Close"]/r["MA50"]-1)*100 if pd.notna(r["MA50"]) and r["MA50"] > 0 else None
        vs200 = (r["Close"]/r["MA200"]-1)*100 if pd.notna(r["MA200"]) and r["MA200"] > 0 else None
        v_ratio = r["Volume"]/r["Volume_3M_P50"] if pd.notna(r["Volume_3M_P50"]) and r["Volume_3M_P50"] > 0 else None
        vs50_s = f"{vs50:+8.1f}%" if vs50 is not None else "     n/a"
        vs200_s = f"{vs200:+8.1f}%" if vs200 is not None else "     n/a"
        v_s = f"{v_ratio:+8.2f}x" if v_ratio is not None else "      n/a"
        print(f"  {r['time'].strftime('%Y-%m-%d'):<12}{r['Close']:>9.0f}{r['MA50']:>9.0f}{r['MA200']:>9.0f}{vs50_s:>9}{vs200_s:>9}{r['D_RSI']*100:>+6.1f}%{v_s:>10}")

    # Long-term price journey
    print(f"\n--- Long-term price journey (yearly snapshots) ---")
    px_long = bq_query(f"""
    SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS px_min, MAX(t.Close) AS px_max,
      AVG(t.Close) AS px_avg
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = '{tk}' AND t.time >= '2018-01-01'
    GROUP BY yr ORDER BY yr
    """)
    print(f"  {'Year':<6}{'Min':>9}{'Avg':>9}{'Max':>9}{'Range %':>11}")
    for _, r in px_long.iterrows():
        range_pct = (r["px_max"]/r["px_min"] - 1) * 100
        print(f"  {int(r['yr']):<6}{r['px_min']:>9.0f}{r['px_avg']:>9.0f}{r['px_max']:>9.0f}{range_pct:>+10.1f}%")

    # FA tier history full
    if len(fa_tk) > 0:
        print(f"\n--- FA tier history (since first record) ---")
        print(f"  Total quarters in FA history: {len(fa_tk)}")
        tier_counts = fa_tk["tier"].value_counts().to_dict()
        print(f"  Tier distribution: {tier_counts}")
        a_pct = (fa_tk["tier"]=="A").sum() / len(fa_tk) * 100
        ab_pct = (fa_tk["tier"].isin(["A","B"])).sum() / len(fa_tk) * 100
        print(f"  A-tier %: {a_pct:.1f}%, A+B %: {ab_pct:.1f}%")
        # Recent 8 quarters
        recent = fa_tk.tail(8)
        print(f"  Recent 8Q: {recent[['quarter','tier','score']].to_string(index=False)}")
