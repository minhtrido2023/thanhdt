# -*- coding: utf-8 -*-
"""Phase B Option A: Asymmetric short-hold (CRISIS + EX-BULL only).

Map: {1:20, 2:45, 3:45, 4:45, 5:30}
  - State 1 CRISIS  → 20d (cut faster than baseline 45)
  - State 2 BEAR    → 45d (same as baseline)
  - State 3 NEUTRAL → 45d (same as baseline)
  - State 4 BULL    → 45d (same as baseline — DO NOT extend, that was the overfit in Phase B trial)
  - State 5 EX-BULL → 30d (cut faster, avoid overheat reversal)

Rationale: only cut in extreme states. Don't extend in BULL (Phase B showed extending
to 75d hurt 2023 -5.1pp despite +41pp 2021 outlier).

Reuses existing phase_b_baseline_* outputs (no need to re-run baseline).
Only runs the new variant + comparison.
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

STATE_HOLD_MAP_A = {1: 20, 2: 45, 3: 45, 4: 45, 5: 30}
OUT_PREFIX = "phase_b_optA"

INNER = os.path.join(WORKDIR, "pt_v121_ens_q2.py")
with open(INNER, "r", encoding="utf-8") as f:
    base_code = f.read()

code = base_code
code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                    '# stdout wrap stripped')
code = code.replace("pt_v121_ens_q2_logs.csv",          f"{OUT_PREFIX}_logs.csv")
code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{OUT_PREFIX}_transactions.csv")
code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{OUT_PREFIX}_open_positions.csv")
code = code.replace("pt_v121_ens_q2_report.md",         f"{OUT_PREFIX}_report.md")
code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{OUT_PREFIX}_BAL"')
code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{OUT_PREFIX}_VN30"')
old = 'hold_days=45, stop_loss=-0.20,'
new = f'hold_days=45, hold_days_by_state={STATE_HOLD_MAP_A!r}, stop_loss=-0.20,'
assert code.count(old) >= 2
code = code.replace(old, new)

print("#"*100)
print(f"#  RUN: {OUT_PREFIX}   state_map = {STATE_HOLD_MAP_A}")
print("#"*100)
ns = {"__name__":"__main__","__file__":INNER}
exec(compile(code, INNER, "exec"), ns)

# ============================================================================
# Compare with existing baseline
# ============================================================================
print("\n" + "="*100)
print("  PHASE B Option A — Metric comparison")
print("="*100)

def load_logs(prefix):
    p = os.path.join(WORKDIR,"data",f"{prefix}_logs.csv")
    df = pd.read_csv(p)
    df["ymd"] = pd.to_datetime(df["ymd"])
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
    return {"label":label, "years":years, "init":init/1e9, "final":final/1e9,
            "ret%":(final/init-1)*100, "CAGR%":cagr*100, "Sharpe":sharpe,
            "MaxDD%":maxdd*100, "Calmar":calmar}

baseline = load_logs("phase_b_baseline")
prev_state= load_logs("phase_b_state")     # prior aggressive state-cond
opt_a     = load_logs(OUT_PREFIX)

IS_END = pd.Timestamp("2022-01-01")
def split_metrics(df, label):
    is_part  = df[df["ymd"] < IS_END]
    oos_part = df[df["ymd"] >= IS_END]
    return metrics(is_part, f"{label} IS"), metrics(oos_part, f"{label} OOS")

m_base_full = metrics(baseline,  "Baseline (hold=45)")
m_prev_full = metrics(prev_state,"Prev aggressive {1:15,2:20,3:40,4:75,5:45}")
m_optA_full = metrics(opt_a,     "OptA asymmetric {1:20,2:45,3:45,4:45,5:30}")

m_base_is, m_base_oos = split_metrics(baseline, "Baseline")
m_prev_is, m_prev_oos = split_metrics(prev_state, "Prev")
m_optA_is, m_optA_oos = split_metrics(opt_a, "OptA")

all_m = [m_base_full, m_prev_full, m_optA_full,
         m_base_is, m_prev_is, m_optA_is,
         m_base_oos, m_prev_oos, m_optA_oos]
mdf = pd.DataFrame(all_m)
print("\n")
print(mdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Year-by-year side-by-side
def yearly(df, label):
    df = df.copy(); df["year"] = df["ymd"].dt.year
    rows = []
    for y, g in df.groupby("year"):
        if len(g) < 5: continue
        rows.append({"year":y, label:(g["nav"].iloc[-1]/g["nav"].iloc[0]-1)*100})
    return pd.DataFrame(rows)
yr = yearly(baseline,"Base%").merge(yearly(prev_state,"Prev%"), on="year").merge(yearly(opt_a,"OptA%"), on="year")
yr["dA_vs_Base"] = yr["OptA%"] - yr["Base%"]
yr["dA_vs_Prev"] = yr["OptA%"] - yr["Prev%"]
print("\nYear-by-year:")
print(yr.to_string(index=False, float_format=lambda x: f"{x:+.2f}" if isinstance(x,float) else x))

# Save summary
out = ["# Phase B Option A — Asymmetric short-hold\n"]
out.append(f"**Map**: `{STATE_HOLD_MAP_A}`  — only cut CRISIS (20d) + EX-BULL (30d), keep 45d in BEAR/NEUTRAL/BULL\n")
out.append("\n## Full + walk-forward metrics\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|---|")
for m in all_m:
    period = "FULL" if "IS" not in m["label"] and "OOS" not in m["label"] else ("IS" if "IS" in m["label"] else "OOS")
    out.append(f"| {m['label']} | {period} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} |")

out.append("\n## Year-by-year\n")
out.append("| Year | Baseline% | Prev (1:15..) % | OptA % | OptA−Base | OptA−Prev |")
out.append("|---|---|---|---|---|---|")
for _,r in yr.iterrows():
    out.append(f"| {int(r['year'])} | {r['Base%']:+.2f} | {r['Prev%']:+.2f} | {r['OptA%']:+.2f} | {r['dA_vs_Base']:+.2f} | {r['dA_vs_Prev']:+.2f} |")

# Gate
gate_pass = (m_optA_oos["CAGR%"] >= m_base_oos["CAGR%"] * 0.97) and (m_optA_oos["Calmar"] >= m_base_oos["Calmar"] * 0.97)
out.append(f"\n## GATE\n")
out.append(f"- OOS CAGR: base {m_base_oos['CAGR%']:+.2f}% → optA {m_optA_oos['CAGR%']:+.2f}% (Δ {m_optA_oos['CAGR%']-m_base_oos['CAGR%']:+.2f}pp)")
out.append(f"- OOS Calmar: base {m_base_oos['Calmar']:.2f} → optA {m_optA_oos['Calmar']:.2f} (Δ {m_optA_oos['Calmar']-m_base_oos['Calmar']:+.2f})")
out.append(f"- **{'PASS — deploy candidate' if gate_pass else 'FAIL — no OOS improvement'}**")

with open(os.path.join(WORKDIR,"data","phase_b_option_a_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"\n  data/phase_b_option_a_summary.md written.")
