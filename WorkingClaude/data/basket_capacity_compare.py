# -*- coding: utf-8 -*-
"""basket_capacity_compare.py — decompose the large-NAV capacity ceiling across parking vehicles.
Reads the BQ-audited deploy-config files for strict E1VFVN30 / creation E1VFVN30 / custom ex-VIC
basket at NAV 50/100/200/500B, prints CAGR/Sharpe/MaxDD/Calmar + avg composition, and the two
deltas: (creation - strict) = pure CAPACITY recovery; (custom - creation) = the ex-VIC vehicle choice.
"""
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
D = r"/home/trido/thanhdt/WorkingClaude/data"
BASE = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliq"

def fname(veh, nav):
    tag = "" if nav == 50 else f"_nav{nav}B"
    return os.path.join(D, f"{BASE}{veh}{tag}.csv")

def load(veh, nav):
    fp = fname(veh, nav)
    if not os.path.exists(fp): return None
    A = pd.read_csv(fp, low_memory=False)
    m = A[A["record_type"] == "METRIC"].set_index("key")["value"]
    d = A[A["record_type"] == "DAILY"].copy()
    navb = d["nav_bal_ref"].astype(float); navl = d["nav_lag_ref"].astype(float)
    tot = navb + navl
    stk = (d["bal_stocks_ref"].astype(float) + d["lag_stocks_ref"].astype(float)) / tot
    cash = (d["bal_cash_ref"].astype(float) + d["lag_cash_ref"].astype(float)) / tot
    etf = (d["bal_etf_ref"].astype(float) + d["lag_etf_ref"].astype(float)) / tot
    return dict(cagr=float(m["cagr"])*100, sharpe=float(m["sharpe_252"]),
                sortino=float(m["sortino_252"]), dd=float(m["max_dd"])*100, calmar=float(m["calmar"]),
                stk=stk.mean()*100, cash=cash.mean()*100, etf=etf.mean()*100)

NAVS = [50, 100, 200, 500]
VEH = [("strict", "strict E1VFVN30 (PRODUCTION floor)"),
       ("creation", "creation E1VFVN30 (real VN30 beta, high cap)"),
       ("custom", "custom ex-VIC basket (STATIC/hindsight membership)"),
       ("custompit", "custom ex-VIC basket (PIT quarterly membership, honest)"),
       ("custompitq", "custom ex-VIC PIT + 8L quality tilt")]
res = {}
for v, _ in VEH:
    for n in NAVS:
        res[(v, n)] = load(v, n)

for v, lbl in VEH:
    print(f"\n=== {v.upper()}: {lbl} ===")
    print(f"{'NAV':>5} | {'CAGR':>6} {'Sharpe':>6} {'MaxDD':>6} {'Calmar':>6} | {'stk%':>5} {'cash%':>6} {'park%':>6}")
    for n in NAVS:
        r = res[(v, n)]
        if r is None: print(f"{n:>4}B | (missing)"); continue
        print(f"{n:>4}B | {r['cagr']:>6.2f} {r['sharpe']:>6.2f} {r['dd']:>6.1f} {r['calmar']:>6.2f} | "
              f"{r['stk']:>5.0f} {r['cash']:>6.0f} {r['etf']:>6.0f}")

print("\n=== HEADLINE CAGR by vehicle x NAV ===")
print(f"{'NAV':>5} | {'strict':>7} {'creation':>9} {'custom':>8} {'custompit':>10} {'custompitq':>11}")
for n in NAVS:
    row = [res[(v, n)] for v, _ in VEH]
    cells = [f"{r['cagr']:>7.2f}" if r else "  miss " for r in row]
    print(f"{n:>4}B | {cells[0]:>7} {cells[1]:>9} {cells[2]:>8} {cells[3]:>10} {cells[4]:>11}")

print("\n=== HONEST DECOMPOSITION (CAGR pp vs strict) ===")
print(f"{'NAV':>5} | {'cap(cr-st)':>11} {'hindsight(cu-pit)':>18} {'exVIC-PIT(pit-cr)':>18} {'quality(pitq-pit)':>18} | {'HONEST total(pitq-st)':>21}")
for n in NAVS:
    st, cr, cu, pit, pitq = (res[(v, n)] for v in ["strict", "creation", "custom", "custompit", "custompitq"])
    if not all([st, cr, cu, pit, pitq]): print(f"{n:>4}B | incomplete"); continue
    print(f"{n:>4}B | {cr['cagr']-st['cagr']:>+11.2f} {cu['cagr']-pit['cagr']:>+18.2f} "
          f"{pit['cagr']-cr['cagr']:>+18.2f} {pitq['cagr']-pit['cagr']:>+18.2f} | {pitq['cagr']-st['cagr']:>+21.2f}")
print("\nLegend: cap = pure capacity (real VN30 beta). hindsight = survivorship in static custom (cu-pit, the bias we removed).")
print("        exVIC-PIT = honest ex-VIC vehicle edge over creation. quality = 8L tilt. HONEST total = deployable custompitq vs strict.")
print("\nVNINDEX B&H reference: 10.72% / Sharpe 0.65 / MaxDD -45.3%")
