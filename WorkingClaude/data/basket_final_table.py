# -*- coding: utf-8 -*-
"""basket_final_table.py — final 5-metric comparison across ALL parking vehicles x NAV.
Vehicles: strict / creation / custom(hindsight) / custompit / custompitq / custompitg / custompitgq.
Metrics: CAGR, Sharpe, Sortino, MaxDD, Calmar (+ avg idle-cash% and park%)."""
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
D = r"/home/trido/thanhdt/WorkingClaude/data"
BASE = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliq"

def load(veh, nav):
    tag = "" if nav == 50 else f"_nav{nav}B"
    fp = os.path.join(D, f"{BASE}{veh}{tag}.csv")
    if not os.path.exists(fp): return None
    A = pd.read_csv(fp, low_memory=False)
    m = A[A.record_type == "METRIC"].set_index("key")["value"]
    d = A[A.record_type == "DAILY"]
    tot = d["nav_bal_ref"].astype(float) + d["nav_lag_ref"].astype(float)
    cash = (d["bal_cash_ref"].astype(float) + d["lag_cash_ref"].astype(float)) / tot
    park = (d["bal_etf_ref"].astype(float) + d["lag_etf_ref"].astype(float)) / tot
    return dict(cagr=float(m["cagr"])*100, sh=float(m["sharpe_252"]), so=float(m["sortino_252"]),
                dd=float(m["max_dd"])*100, cal=float(m["calmar"]),
                cash=cash.mean()*100, park=park.mean()*100)

VEH = [("strict", "strict E1VFVN30 (PRODUCTION floor)"),
       ("creation", "creation E1VFVN30 (real VN30 beta)"),
       ("custompit", "PIT ex-VIC (honest, no gate)"),
       ("custompitq", "PIT + 8L tilt"),
       ("custompitg", "PIT + 05/m2 timing + GATE<=3  (SAFE honest)"),
       ("custompitgq", "PIT + timing + gate + 8L tilt  (full)"),
       ("custom", "custom STATIC ex-VIC (hindsight - ref only)")]
NAVS = [50, 100, 200, 500]

for v, lbl in VEH:
    print(f"\n=== {v}: {lbl} ===")
    print(f"{'NAV':>5} | {'CAGR%':>6} {'Sharpe':>6} {'Sortino':>7} {'MaxDD%':>7} {'Calmar':>6} | {'idle$%':>6} {'park%':>5}")
    for n in NAVS:
        r = load(v, n)
        if not r: print(f"{n:>4}B | (missing)"); continue
        print(f"{n:>4}B | {r['cagr']:>6.2f} {r['sh']:>6.2f} {r['so']:>7.2f} {r['dd']:>7.1f} {r['cal']:>6.2f} | "
              f"{r['cash']:>6.0f} {r['park']:>5.0f}")

print("\n=== HEADLINE: CAGR / Calmar by vehicle x NAV ===")
hdr = "  ".join(f"{v[:9]:>9}" for v, _ in VEH)
print(f"{'NAV':>5} | {hdr}")
for n in NAVS:
    cells = []
    for v, _ in VEH:
        r = load(v, n)
        cells.append(f"{r['cagr']:>4.1f}/{r['cal']:>4.2f}" if r else "   --    ")
    print(f"{n:>4}B | " + "  ".join(f"{c:>9}" for c in cells))
print("\n(cell = CAGR% / Calmar)   VNINDEX B&H: 10.72% / Sharpe 0.65 / MaxDD -45.3 / Calmar 0.24")
