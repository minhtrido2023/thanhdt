# -*- coding: utf-8 -*-
"""Phase B: V5 (pt_v121_ens_q2) backtest with state-conditional hold_days.

Runs the V5 stack TWICE on the same window:
  (1) BASELINE — hold_days=45 (existing V5 production)
  (2) STATE-COND — hold_days_by_state={1:15, 2:20, 3:40, 4:75, 5:45}

Same data, same signals, same everything else. Only difference = hold cap per
position at entry, derived from TQ v3.4b state on entry day.

Reuses pt_v121_ens_q2.py via runpy. Patches:
  - START_DATE='2014-01-02'
  - 2× simulate() calls (BAL + VN30) get hold_days_by_state injected

Outputs:
  - data/phase_b_baseline_logs.csv
  - data/phase_b_baseline_transactions.csv
  - data/phase_b_state_logs.csv
  - data/phase_b_state_transactions.csv
  - data/phase_b_summary.md (CAGR/MaxDD/Sharpe/Calmar comparison + IS/OOS walk-forward)
"""
import os, sys, io
import pandas as pd
import numpy as np

# Wrap stdout ONCE at top — both inner runs (which had their wrap stripped) reuse it
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import pt_dates
pt_dates.START_DATE = "2014-01-02"  # full backtest

STATE_HOLD_MAP = {1: 15, 2: 20, 3: 40, 4: 75, 5: 45}

INNER = os.path.join(WORKDIR, "pt_v121_ens_q2.py")
with open(INNER, "r", encoding="utf-8") as f:
    base_code = f.read()


def patch_code(out_prefix: str, inject_state_map: bool) -> str:
    code = base_code
    # Strip the inner script's stdout wrap (we run it twice in same process → would close buffer)
    code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                        '# stdout wrap stripped by phase_b wrapper')
    # Rewrite output paths
    code = code.replace("pt_v121_ens_q2_logs.csv",          f"{out_prefix}_logs.csv")
    code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{out_prefix}_transactions.csv")
    code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{out_prefix}_open_positions.csv")
    code = code.replace("pt_v121_ens_q2_report.md",         f"{out_prefix}_report.md")
    code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{out_prefix}_BAL"')
    code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{out_prefix}_VN30"')
    # Inject hold_days_by_state into the 2 simulate() calls
    if inject_state_map:
        # The unique parameter line in both BAL+VN30 simulate() calls:
        old = 'hold_days=45, stop_loss=-0.20,'
        new = f'hold_days=45, hold_days_by_state={STATE_HOLD_MAP!r}, stop_loss=-0.20,'
        n_repl = code.count(old)
        assert n_repl >= 2, f"Expected ≥2 simulate() lines to patch, found {n_repl}"
        code = code.replace(old, new)
    return code


def run_variant(out_prefix: str, inject_state_map: bool):
    print("\n" + "#"*100)
    print(f"#  RUN: {out_prefix}  state_map={inject_state_map}")
    print("#"*100)
    code = patch_code(out_prefix, inject_state_map)
    ns = {"__name__": "__main__", "__file__": INNER}
    exec(compile(code, INNER, "exec"), ns)


# ============================================================================
# 1. Run both variants
# ============================================================================
run_variant("phase_b_baseline", inject_state_map=False)
run_variant("phase_b_state",    inject_state_map=True)

# ============================================================================
# 2. Compute comparison metrics
# ============================================================================
print("\n" + "="*100)
print("  PHASE B — Metric comparison")
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
state    = load_logs("phase_b_state")

# Full period
m_base_full  = metrics(baseline, "Baseline (hold=45)")
m_state_full = metrics(state,    "State-cond hold")

# IS / OOS split
IS_END = pd.Timestamp("2022-01-01")
def split_metrics(df, label):
    is_part  = df[df["ymd"] < IS_END]
    oos_part = df[df["ymd"] >= IS_END]
    return metrics(is_part, f"{label} IS 2014-2021"), metrics(oos_part, f"{label} OOS 2022-2026")

m_base_is, m_base_oos   = split_metrics(baseline, "Baseline")
m_state_is, m_state_oos = split_metrics(state,    "State")

# Year-by-year
def yearly(df, label):
    df = df.copy()
    df["year"] = df["ymd"].dt.year
    rows = []
    for y, g in df.groupby("year"):
        if len(g) < 5: continue
        rows.append({"year":y, "label":label,
                     "start_nav_B": g["nav"].iloc[0]/1e9,
                     "end_nav_B":   g["nav"].iloc[-1]/1e9,
                     "ret%": (g["nav"].iloc[-1]/g["nav"].iloc[0]-1)*100})
    return pd.DataFrame(rows)
yr_base = yearly(baseline, "Baseline")
yr_state = yearly(state, "State")

# Print summary
all_m = [m_base_full, m_state_full, m_base_is, m_state_is, m_base_oos, m_state_oos]
mdf = pd.DataFrame(all_m)
print("\nMetrics:")
print(mdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Year-by-year side-by-side
combined_yr = yr_base.merge(yr_state, on="year", suffixes=("_base","_state"))
combined_yr["delta%"] = combined_yr["ret%_state"] - combined_yr["ret%_base"]
print("\nYear-by-year (delta = state - baseline):")
print(combined_yr[["year","ret%_base","ret%_state","delta%"]].to_string(
    index=False, float_format=lambda x: f"{x:+.2f}" if isinstance(x,float) else x))

# ============================================================================
# 3. Save summary markdown
# ============================================================================
out = ["# Phase B — V5 state-conditional hold vs baseline\n"]
out.append(f"**Period**: {baseline['ymd'].min().date()} → {baseline['ymd'].max().date()}\n")
out.append(f"**State-hold map**: `{STATE_HOLD_MAP}`\n")
out.append("\n## Full-period metrics\n")
out.append("| Variant | Years | Init B | Final B | Return% | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|---|---|---|---|")
for m in [m_base_full, m_state_full]:
    out.append(f"| {m['label']} | {m['years']:.2f} | {m['init']:.2f} | {m['final']:.2f} | {m['ret%']:+.2f} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} |")

out.append("\n## Walk-forward IS (2014-2021) / OOS (2022-2026)\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar |")
out.append("|---|---|---|---|---|---|")
for m in [m_base_is, m_state_is, m_base_oos, m_state_oos]:
    out.append(f"| {m['label']} | — | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} |")

out.append("\n## Year-by-year\n")
out.append("| Year | Baseline% | State% | Delta% |")
out.append("|---|---|---|---|")
for _,r in combined_yr.iterrows():
    out.append(f"| {int(r['year'])} | {r['ret%_base']:+.2f} | {r['ret%_state']:+.2f} | {r['delta%']:+.2f} |")

# Gate
gate_pass = (m_state_oos["CAGR%"] >= m_base_oos["CAGR%"] * 0.95) and (m_state_oos["Calmar"] >= m_base_oos["Calmar"] * 0.95)
out.append(f"\n## GATE\n")
out.append(f"- OOS CAGR: baseline {m_base_oos['CAGR%']:+.2f}% → state {m_state_oos['CAGR%']:+.2f}% (Δ {m_state_oos['CAGR%']-m_base_oos['CAGR%']:+.2f}pp)")
out.append(f"- OOS Calmar: baseline {m_base_oos['Calmar']:.2f} → state {m_state_oos['Calmar']:.2f} (Δ {m_state_oos['Calmar']-m_base_oos['Calmar']:+.2f})")
out.append(f"- **{'PASS — state-cond hold worth deploying' if gate_pass else 'FAIL — no improvement, reject'}**")

with open(os.path.join(WORKDIR,"data","phase_b_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_b_summary.md written.")
print("\nDone.")
