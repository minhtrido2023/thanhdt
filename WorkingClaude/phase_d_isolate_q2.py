# -*- coding: utf-8 -*-
"""Phase D — Isolate Q2 overlay effect.

Run V5 (pt_v121_ens_q2.py) with cash_etf_states={3:0.7} (V4 V121_ENS production setting).
Diff vs Phase B baseline (which has {3:1.0}) = isolated Q2 overlay effect.

For "C bare V121_ENS validation 24.32%" — already exists in test_rolling_m3_v121_ensemble.log.

Compares 4 systems:
  C — test_rolling_m3 (bare V121_ENS validation, simplified config) → 24.32% (already logged)
  A — V5 stack with {3:0.7} (= V4 V121_ENS production) → THIS RUN
  B — V5 stack with {3:1.0} (= V5 V121_ENS+Q2 production) → 18.34% (phase_b_baseline)
"""
import os, sys, io
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import pt_dates
pt_dates.START_DATE = "2014-01-02"

INNER = os.path.join(WORKDIR, "pt_v121_ens_q2.py")
with open(INNER, "r", encoding="utf-8") as f:
    base_code = f.read()

OUT_PREFIX = "phase_d_v5_no_q2"  # V5 stack without Q2 overlay
code = base_code
code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                    '# stdout wrap stripped')
code = code.replace("pt_v121_ens_q2_logs.csv",          f"{OUT_PREFIX}_logs.csv")
code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{OUT_PREFIX}_transactions.csv")
code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{OUT_PREFIX}_open_positions.csv")
code = code.replace("pt_v121_ens_q2_report.md",         f"{OUT_PREFIX}_report.md")
code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{OUT_PREFIX}_BAL"')
code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{OUT_PREFIX}_VN30"')

# Disable Q2 overlay: revert {3:1.0} to {3:0.7} in both BAL + VN30 simulate() calls
old = "cash_etf_states={3:1.0}"
new = "cash_etf_states={3:0.7}"
n = code.count(old)
assert n == 2, f"Expected 2 occurrences of {old}, found {n}"
code = code.replace(old, new)

print("#"*100)
print(f"#  RUN: {OUT_PREFIX}   (V5 stack but cash_etf_states={{3:0.7}} — Q2 overlay disabled)")
print("#"*100)
ns = {"__name__":"__main__","__file__":INNER}
exec(compile(code, INNER, "exec"), ns)

# ============================================================================
# 3-way + reference comparison
# ============================================================================
print("\n" + "="*100)
print("  PHASE D — Isolating Q2 overlay effect")
print("="*100)

def load_logs(prefix):
    p = os.path.join(WORKDIR,"data",f"{prefix}_logs.csv")
    df = pd.read_csv(p); df["ymd"] = pd.to_datetime(df["ymd"])
    return df.sort_values("ymd").reset_index(drop=True)

def metrics(df, label):
    df = df.copy()
    df["ret"] = df["nav"].pct_change().fillna(0)
    df["peak"] = df["nav"].cummax()
    df["dd"] = df["nav"]/df["peak"] - 1
    years = (df["ymd"].iloc[-1] - df["ymd"].iloc[0]).days / 365.25
    final = df["nav"].iloc[-1]; init = df["nav"].iloc[0]
    cagr = (final/init)**(1/max(years,1e-9)) - 1
    sharpe = df["ret"].mean()/df["ret"].std() * np.sqrt(252) if df["ret"].std()>0 else 0
    maxdd = df["dd"].min()
    calmar = cagr/abs(maxdd) if maxdd<0 else np.nan
    return {"label":label, "years":years, "CAGR%":cagr*100, "Sharpe":sharpe,
            "MaxDD%":maxdd*100, "Calmar":calmar, "Final B":final/1e9,
            "Wealth_x": final/init}

B = load_logs("phase_b_baseline")     # V5 production with {3:1.0} Q2 overlay
A = load_logs(OUT_PREFIX)              # V5 stack with {3:0.7} (Q2 removed)

IS_END = pd.Timestamp("2022-01-01")
def split_metrics(df, label):
    return metrics(df[df["ymd"]<IS_END], f"{label} IS"), metrics(df[df["ymd"]>=IS_END], f"{label} OOS")

# A and B (V5 stack with vs without Q2)
mA, mB = metrics(A, "A: V5 stack, {3:0.7} (no Q2)"), metrics(B, "B: V5 stack, {3:1.0} (Q2 ON, prod)")
mA_is, mA_oos = split_metrics(A, "A")
mB_is, mB_oos = split_metrics(B, "B")

# C reference (from test_rolling_m3 log — hardcoded)
C_ref = {"label":"C: test_rolling_m3 bare V121_ENS (simpler config)",
         "CAGR%": 24.32, "Sharpe": 1.74, "MaxDD%": -15.32, "Calmar": 1.59, "Wealth_x": 14.75}
C_OOS_ref = {"label":"C OOS 2024-26 (from test_rolling log)",
             "CAGR%": 31.74, "Sharpe": 1.81, "MaxDD%": -10.88, "Calmar": 2.92}

all_full = [C_ref, mA, mB]
all_split = [mA_is, mB_is, C_OOS_ref, mA_oos, mB_oos]

mdf_full = pd.DataFrame(all_full)
print("\nFULL period (12.4y, init 50B):")
print(mdf_full.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

print("\nIS / OOS split:")
mdf_split = pd.DataFrame(all_split)
print(mdf_split.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Isolated effects
delta_q2_full = mB["CAGR%"] - mA["CAGR%"]
delta_q2_oos  = mB_oos["CAGR%"] - mA_oos["CAGR%"]
delta_prod_full = mA["CAGR%"] - C_ref["CAGR%"]   # negative means production complexity hurts vs bare

print(f"\nIsolated effect estimates (CAGR pp):")
print(f"  Q2 overlay (B - A, V5 stack same):   FULL {delta_q2_full:+.2f}pp   OOS {delta_q2_oos:+.2f}pp")
print(f"  Production complexity (A - C, both no Q2): FULL {delta_prod_full:+.2f}pp  (includes max_pos 10→12, SV_TIGHT/P3/D1, HYBRID, t1_exec)")
print(f"  Total V5 prod (B) vs bare validation (C): FULL {mB['CAGR%'] - C_ref['CAGR%']:+.2f}pp")

# Year-by-year A vs B
def yearly(df, label):
    df = df.copy(); df["year"] = df["ymd"].dt.year
    return pd.DataFrame([{"year":y, label:(g["nav"].iloc[-1]/g["nav"].iloc[0]-1)*100}
                         for y,g in df.groupby("year") if len(g)>=5])
yr = yearly(A,"A_noQ2%").merge(yearly(B,"B_Q2%"), on="year")
yr["dQ2"] = yr["B_Q2%"] - yr["A_noQ2%"]
print("\nYear-by-year Q2 effect (B − A):")
print(yr.to_string(index=False, float_format=lambda x: f"{x:+.2f}" if isinstance(x,float) else x))

# Save summary
out = ["# Phase D — Isolating Q2 overlay + production-complexity effects\n"]
out.append("## Setup\n")
out.append("- **A** (this run): V5 stack with `cash_etf_states={3:0.7}` = V4 V121_ENS production config")
out.append("- **B** (Phase B baseline): V5 stack with `cash_etf_states={3:1.0}` = V5 V121_ENS+Q2 production")
out.append("- **C** (reference): `test_rolling_m3_v121_ensemble.py` log — bare V121_ENS validation:")
out.append("  - max_pos=10 (not 12 → no 20% borrow); slippage=0.001 (vs 0.0); no SV_TIGHT/P3/D1; no HYBRID; default tier_weights")
out.append("\n## FULL period (2014-01-02 → 2026-05-19, 12.4y, init 50B)\n")
out.append("| Variant | CAGR% | Sharpe | MaxDD% | Calmar | Final B | Wealth x |")
out.append("|---|---|---|---|---|---|---|")
for m in all_full:
    out.append(f"| {m['label']} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} | {m.get('Final B','—'):.1f} | {m.get('Wealth_x',m.get('Wealth_x',0)):.2f}x |" if isinstance(m.get('Final B'), float) else f"| {m['label']} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} | — | {m.get('Wealth_x','—')}x |")

out.append("\n## IS/OOS split\n")
out.append("| Variant | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|")
for m in all_split:
    out.append(f"| {m['label']} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} |")

out.append(f"\n## Isolated effect estimates\n")
out.append(f"- **Q2 overlay** (B − A): FULL {delta_q2_full:+.2f}pp / OOS {delta_q2_oos:+.2f}pp CAGR")
out.append(f"- **Production complexity** (A − C ref): FULL {delta_prod_full:+.2f}pp (includes leverage 120%, SV_TIGHT/P3/D1 filters, HYBRID entry)")
out.append(f"- **Total V5 prod vs bare validation** (B − C): {mB['CAGR%'] - C_ref['CAGR%']:+.2f}pp")

out.append("\n## Year-by-year Q2 effect\n")
out.append("| Year | A (no Q2) % | B (Q2 ON) % | dQ2 |")
out.append("|---|---|---|---|")
for _,r in yr.iterrows():
    out.append(f"| {int(r['year'])} | {r['A_noQ2%']:+.2f} | {r['B_Q2%']:+.2f} | {r['dQ2']:+.2f} |")

with open(os.path.join(WORKDIR,"data","phase_d_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_d_summary.md")
