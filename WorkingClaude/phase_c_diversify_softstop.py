# -*- coding: utf-8 -*-
"""Phase C — Test (1) Diversify + (2) Soft stop.

D: max_positions 12→20, tier weight 10%→5% NAV/slot  (still ~100% deployable)
S: soft stop -15% trim 50% + hard stop -25% (instead of -20% hard)

Both leave entry signals UNCHANGED. Only portfolio construction (D) or exit (S).

Reuses existing phase_b_baseline_* outputs for comparison.
Runs D and S sequentially (each ~15-20 min).
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


def patch_and_run(out_prefix, replacements):
    code = base_code
    code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                        '# stdout wrap stripped')
    code = code.replace("pt_v121_ens_q2_logs.csv",          f"{out_prefix}_logs.csv")
    code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{out_prefix}_transactions.csv")
    code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{out_prefix}_open_positions.csv")
    code = code.replace("pt_v121_ens_q2_report.md",         f"{out_prefix}_report.md")
    code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{out_prefix}_BAL"')
    code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{out_prefix}_VN30"')
    for old, new in replacements:
        n = code.count(old)
        assert n >= 1, f"Pattern not found: {old[:60]}..."
        code = code.replace(old, new)
    print("\n" + "#"*100)
    print(f"#  RUN: {out_prefix}")
    print("#"*100)
    ns = {"__name__":"__main__","__file__":INNER}
    exec(compile(code, INNER, "exec"), ns)


# ─── Variant D: diversify ─────────────────────────────────────────────────────
# Change max_positions=12 → 20 and tier_weights 10% → 5% in BOTH BAL & VN30 sims.
# These appear in pt_v121_ens_q2.py at the top as module-level constants.
REPL_D = [
    ("MAX_POS_V11 = 12",                          "MAX_POS_V11 = 20"),
    ("TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}",
     "TIER_WEIGHTS_V11 = {t: 0.05 for t in TIER_BAL}"),
]

# ─── Variant S: soft stop ────────────────────────────────────────────────────
# Inject soft_stop_partial=(-0.15, 0.5) and replace stop_loss=-0.20 with -0.25 in both simulate calls.
REPL_S = [
    ("hold_days=45, stop_loss=-0.20,",
     "hold_days=45, stop_loss=-0.25, soft_stop_partial=(-0.15, 0.5),"),
]

patch_and_run("phase_c_D", REPL_D)
patch_and_run("phase_c_S", REPL_S)

# ============================================================================
# Compare with baseline
# ============================================================================
print("\n" + "="*100)
print("  PHASE C — Diversify (D) + Soft stop (S) vs Baseline")
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
            "MaxDD%":maxdd*100, "Calmar":calmar, "Final B":final/1e9}

baseline = load_logs("phase_b_baseline")
d_run    = load_logs("phase_c_D")
s_run    = load_logs("phase_c_S")

IS_END = pd.Timestamp("2022-01-01")
def split_metrics(df, label):
    return metrics(df[df["ymd"]<IS_END], f"{label} IS"), metrics(df[df["ymd"]>=IS_END], f"{label} OOS")

m_base_full = metrics(baseline, "Baseline (12pos, 10%, -20% hard)")
m_d_full    = metrics(d_run,    "D: 20pos, 5%/slot")
m_s_full    = metrics(s_run,    "S: soft-15% trim50%, hard-25%")
m_b_is, m_b_oos = split_metrics(baseline, "Base")
m_d_is, m_d_oos = split_metrics(d_run, "D")
m_s_is, m_s_oos = split_metrics(s_run, "S")

mdf = pd.DataFrame([m_base_full, m_d_full, m_s_full,
                    m_b_is, m_d_is, m_s_is, m_b_oos, m_d_oos, m_s_oos])
print("\n")
print(mdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Year-by-year
def yearly(df, label):
    df = df.copy(); df["year"] = df["ymd"].dt.year
    rows = [{"year":y, label:(g["nav"].iloc[-1]/g["nav"].iloc[0]-1)*100}
            for y,g in df.groupby("year") if len(g) >= 5]
    return pd.DataFrame(rows)
yr = yearly(baseline,"Base%").merge(yearly(d_run,"D%"), on="year").merge(yearly(s_run,"S%"), on="year")
yr["dD"] = yr["D%"] - yr["Base%"]; yr["dS"] = yr["S%"] - yr["Base%"]
print("\nYear-by-year:")
print(yr.to_string(index=False, float_format=lambda x: f"{x:+.2f}" if isinstance(x,float) else x))

# Save summary
out = ["# Phase C — Diversify (D) + Soft stop (S) vs Baseline\n"]
out.append("\n## Metrics\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar | Final B |")
out.append("|---|---|---|---|---|---|---|")
for m in [m_base_full, m_d_full, m_s_full, m_b_is, m_d_is, m_s_is, m_b_oos, m_d_oos, m_s_oos]:
    period = "FULL" if "IS" not in m["label"] and "OOS" not in m["label"] else ("IS" if "IS" in m["label"] else "OOS")
    out.append(f"| {m['label']} | {period} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} | {m['Final B']:.1f} |")

out.append("\n## Year-by-year\n")
out.append("| Year | Base% | D% | S% | D−Base | S−Base |")
out.append("|---|---|---|---|---|---|")
for _,r in yr.iterrows():
    out.append(f"| {int(r['year'])} | {r['Base%']:+.2f} | {r['D%']:+.2f} | {r['S%']:+.2f} | {r['dD']:+.2f} | {r['dS']:+.2f} |")

# Gates
def gate(m_var, m_base):
    return (m_var["CAGR%"] >= m_base["CAGR%"] * 0.97) and (m_var["Calmar"] >= m_base["Calmar"] * 0.97)
out.append(f"\n## GATEs (OOS 2022-2026)\n")
out.append(f"- D: CAGR base {m_b_oos['CAGR%']:+.2f}% → {m_d_oos['CAGR%']:+.2f}% (Δ {m_d_oos['CAGR%']-m_b_oos['CAGR%']:+.2f}); Calmar {m_b_oos['Calmar']:.2f} → {m_d_oos['Calmar']:.2f} — **{'PASS' if gate(m_d_oos, m_b_oos) else 'FAIL'}**")
out.append(f"- S: CAGR base {m_b_oos['CAGR%']:+.2f}% → {m_s_oos['CAGR%']:+.2f}% (Δ {m_s_oos['CAGR%']-m_b_oos['CAGR%']:+.2f}); Calmar {m_b_oos['Calmar']:.2f} → {m_s_oos['Calmar']:.2f} — **{'PASS' if gate(m_s_oos, m_b_oos) else 'FAIL'}**")

with open(os.path.join(WORKDIR,"data","phase_c_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_c_summary.md")
