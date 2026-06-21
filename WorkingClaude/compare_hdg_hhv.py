#!/usr/bin/env python3
"""Compare HDG vs HHV — both real assets / infrastructure plays."""
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

fa = pd.read_csv("data/fa_ratings_lh.csv")

results = {}
for tk in ["HDG", "HHV"]:
    fa_tk = fa[fa["ticker"]==tk].sort_values("quarter")
    n_q = len(fa_tk)
    n_A = (fa_tk["tier"]=="A").sum()
    n_AB = (fa_tk["tier"].isin(["A","B"])).sum()
    pct_A = n_A/max(n_q,1)*100
    pct_AB = n_AB/max(n_q,1)*100

    fin = bq_query(f"""
    SELECT f.quarter, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
      f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.ROIC_Trailing, f.PE, f.PB, f.DY,
      f.Cash_P0, f.StDebt_P0, f.LtDebt_P0, f.IntCov_P0, f.totalAsset_P0,
      f.AdvCust_P0, f.UnearnRev_P0, f.OShares, f.BVPS, f.ROE_Min5Y, f.CF_OA_5Y
    FROM tav2_bq.ticker_financial AS f
    WHERE f.ticker = '{tk}' AND f.time >= '2022-01-01'
    ORDER BY f.time
    """)

    px_now = bq_query(f"SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI, t.Volume_3M_P50*t.Close AS liq FROM tav2_bq.ticker AS t WHERE t.ticker = '{tk}' ORDER BY t.time DESC LIMIT 1")

    px_long = bq_query(f"""
    SELECT EXTRACT(YEAR FROM t.time) AS yr, MIN(t.Close) AS lo, MAX(t.Close) AS hi, AVG(t.Close) AS avg
    FROM tav2_bq.ticker AS t WHERE t.ticker = '{tk}' AND t.time >= '2018-01-01'
    GROUP BY yr ORDER BY yr
    """)

    results[tk] = {"fa_tk":fa_tk, "fin":fin, "px_now":px_now, "px_long":px_long, "pct_A":pct_A, "pct_AB":pct_AB, "n_q":n_q}

# Side-by-side comparison
print("="*120)
print("  HDG vs HHV — Side-by-Side Comparison")
print("="*120)

print(f"\n  {'Metric':<35}{'HDG':>20}{'HHV':>20}")
print(f"  {'─'*35}{'─'*20}{'─'*20}")

# FA history
print(f"  {'FA quarters tracked':<35}{results['HDG']['n_q']:>20}{results['HHV']['n_q']:>20}")
print(f"  {'A-tier %':<35}{results['HDG']['pct_A']:>19.1f}%{results['HHV']['pct_A']:>19.1f}%")
print(f"  {'A+B-tier %':<35}{results['HDG']['pct_AB']:>19.1f}%{results['HHV']['pct_AB']:>19.1f}%")
print(f"  {'Latest FA tier':<35}{results['HDG']['fa_tk']['tier'].iloc[-1] if len(results['HDG']['fa_tk'])>0 else 'N/A':>20}{results['HHV']['fa_tk']['tier'].iloc[-1] if len(results['HHV']['fa_tk'])>0 else 'N/A':>20}")

# Latest fundamentals (Q1 2026 if available)
def latest_metric(d, field, formatter=lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"):
    fin = d["fin"]
    if len(fin) == 0: return "N/A"
    val = fin.iloc[-1][field]
    return formatter(val)

print()
print(f"  {'Latest quarter (Q1 2026)':<35}")
print(f"  {'NP_P0 (B VND)':<35}{results['HDG']['fin']['NP_P0'].iloc[-1]/1e9 if len(results['HDG']['fin'])>0 else 0:>19.1f}B{results['HHV']['fin']['NP_P0'].iloc[-1]/1e9 if len(results['HHV']['fin'])>0 else 0:>19.1f}B")

for fld, label, fmt in [
    ("ROE_Trailing", "ROE_Trailing", lambda x: f"{x*100:.1f}%"),
    ("ROIC_Trailing", "ROIC_Trailing", lambda x: f"{x*100:.1f}%"),
    ("ROE_Min5Y", "ROE_Min5Y", lambda x: f"{x*100:.1f}%"),
    ("PE", "PE", lambda x: f"{x:.1f}"),
    ("PB", "PB", lambda x: f"{x:.2f}"),
    ("DY", "DY", lambda x: f"{x*100:.1f}%"),
    ("GPM_P0", "GPM", lambda x: f"{x*100:.1f}%"),
    ("NPM_P0", "NPM", lambda x: f"{x*100:.1f}%"),
    ("IntCov_P0", "IntCov", lambda x: f"{x:.1f}x"),
    ("CF_OA_5Y", "CF_OA_5Y (cum)", lambda x: f"{x/1e9:.0f}B"),
]:
    h_val = results['HDG']['fin'][fld].iloc[-1] if len(results['HDG']['fin']) > 0 else None
    v_val = results['HHV']['fin'][fld].iloc[-1] if len(results['HHV']['fin']) > 0 else None
    h_str = fmt(h_val) if pd.notna(h_val) else "N/A"
    v_str = fmt(v_val) if pd.notna(v_val) else "N/A"
    print(f"  {label:<35}{h_str:>20}{v_str:>20}")

# Debt / leverage
print()
for tk in ["HDG", "HHV"]:
    fin = results[tk]['fin']
    if len(fin) == 0: continue
    r = fin.iloc[-1]
    debt = (r["StDebt_P0"] or 0) + (r["LtDebt_P0"] or 0)
    equity = (r["totalAsset_P0"] or 0) - debt
    debt_eq = debt / equity if equity > 0 else None
    debt_ta = debt / r["totalAsset_P0"] if r["totalAsset_P0"] else None
    cash_pct = (r["Cash_P0"] or 0) / r["totalAsset_P0"] * 100 if r["totalAsset_P0"] else 0
    print(f"  {tk}: Total Asset {r['totalAsset_P0']/1e9:.0f}B | Total Debt {debt/1e9:.0f}B | Debt/Equity {debt_eq:.2f}x | Debt/Asset {debt_ta*100:.1f}% | Cash/Asset {cash_pct:.1f}%")

# Recent NP trend
print(f"\n  --- NP last 8Q YoY trend ---")
print(f"  {'Quarter':<10}{'HDG NP':>10}{'HDG yoy':>10}{'HHV NP':>10}{'HHV yoy':>10}")
all_q = sorted(set(results['HDG']['fin']['quarter'].tolist() + results['HHV']['fin']['quarter'].tolist()))[-8:]
for q in all_q:
    h = results['HDG']['fin'][results['HDG']['fin']['quarter']==q]
    v = results['HHV']['fin'][results['HHV']['fin']['quarter']==q]
    if len(h) > 0:
        h_np = h['NP_P0'].iloc[0]/1e9
        h_yoy = (h['NP_P0'].iloc[0]/h['NP_P4'].iloc[0]-1)*100 if h['NP_P4'].iloc[0] and h['NP_P4'].iloc[0] != 0 else None
    else: h_np = None; h_yoy = None
    if len(v) > 0:
        v_np = v['NP_P0'].iloc[0]/1e9
        v_yoy = (v['NP_P0'].iloc[0]/v['NP_P4'].iloc[0]-1)*100 if v['NP_P4'].iloc[0] and v['NP_P4'].iloc[0] != 0 else None
    else: v_np = None; v_yoy = None
    h_np_s = f"{h_np:.1f}B" if h_np is not None else "  N/A"
    v_np_s = f"{v_np:.1f}B" if v_np is not None else "  N/A"
    h_yoy_s = f"{h_yoy:+.1f}%" if h_yoy is not None else "   N/A"
    v_yoy_s = f"{v_yoy:+.1f}%" if v_yoy is not None else "   N/A"
    print(f"  {q:<10}{h_np_s:>10}{h_yoy_s:>10}{v_np_s:>10}{v_yoy_s:>10}")

# Price snapshot
print(f"\n  --- Price snapshot ---")
for tk in ["HDG", "HHV"]:
    r = results[tk]['px_now'].iloc[0] if len(results[tk]['px_now']) > 0 else None
    if r is not None:
        vs50 = (r["Close"]/r["MA50"]-1)*100 if pd.notna(r["MA50"]) and r["MA50"] > 0 else None
        vs200 = (r["Close"]/r["MA200"]-1)*100 if pd.notna(r["MA200"]) and r["MA200"] > 0 else None
        vs50_s = f"{vs50:+.1f}%" if vs50 is not None else "n/a"
        vs200_s = f"{vs200:+.1f}%" if vs200 is not None else "n/a"
        print(f"  {tk}: Close {r['Close']:.0f} | %MA50: {vs50_s} | %MA200: {vs200_s} | RSI: {r['D_RSI']*100:.1f}% | Liq: {r['liq']/1e9:.1f}B/day")

# Yearly price journey
print(f"\n  --- Yearly price journey ---")
print(f"  {'Year':<6}{'HDG min':>10}{'HDG max':>10}{'HDG avg':>10}{'HHV min':>10}{'HHV max':>10}{'HHV avg':>10}")
all_yrs = sorted(set(results['HDG']['px_long']['yr'].tolist() + results['HHV']['px_long']['yr'].tolist()))
for yr in all_yrs:
    h_row = results['HDG']['px_long'][results['HDG']['px_long']['yr']==yr]
    v_row = results['HHV']['px_long'][results['HHV']['px_long']['yr']==yr]
    h_lo = h_row['lo'].iloc[0] if len(h_row) > 0 else 0
    h_hi = h_row['hi'].iloc[0] if len(h_row) > 0 else 0
    h_avg = h_row['avg'].iloc[0] if len(h_row) > 0 else 0
    v_lo = v_row['lo'].iloc[0] if len(v_row) > 0 else 0
    v_hi = v_row['hi'].iloc[0] if len(v_row) > 0 else 0
    v_avg = v_row['avg'].iloc[0] if len(v_row) > 0 else 0
    print(f"  {int(yr):<6}{h_lo:>10.0f}{h_hi:>10.0f}{h_avg:>10.0f}{v_lo:>10.0f}{v_hi:>10.0f}{v_avg:>10.0f}")
