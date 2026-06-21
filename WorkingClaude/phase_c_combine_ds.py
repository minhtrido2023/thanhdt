# -*- coding: utf-8 -*-
"""Phase C combine — D + S applied together.

D: max_positions 12→20, tier_weights 10%→5% NAV/slot
S: stop_loss -20% → soft -15% trim 50% + hard -25%

Reuses phase_b_baseline + phase_c_D + phase_c_S outputs for 4-way comparison.
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

OUT_PREFIX = "phase_c_DS"
code = base_code
code = code.replace('sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")',
                    '# stdout wrap stripped')
code = code.replace("pt_v121_ens_q2_logs.csv",          f"{OUT_PREFIX}_logs.csv")
code = code.replace("pt_v121_ens_q2_transactions.csv",  f"{OUT_PREFIX}_transactions.csv")
code = code.replace("pt_v121_ens_q2_open_positions.csv",f"{OUT_PREFIX}_open_positions.csv")
code = code.replace("pt_v121_ens_q2_report.md",         f"{OUT_PREFIX}_report.md")
code = code.replace('name="pt_v121_ens_q2_BAL"',  f'name="{OUT_PREFIX}_BAL"')
code = code.replace('name="pt_v121_ens_q2_VN30"', f'name="{OUT_PREFIX}_VN30"')

# Apply BOTH D and S patches
code = code.replace("MAX_POS_V11 = 12", "MAX_POS_V11 = 20")
code = code.replace("TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}",
                    "TIER_WEIGHTS_V11 = {t: 0.05 for t in TIER_BAL}")
old = "hold_days=45, stop_loss=-0.20,"
new = "hold_days=45, stop_loss=-0.25, soft_stop_partial=(-0.15, 0.5),"
assert code.count(old) >= 2
code = code.replace(old, new)

print("#"*100)
print(f"#  RUN: {OUT_PREFIX}  (D + S combined)")
print("#"*100)
ns = {"__name__":"__main__","__file__":INNER}
exec(compile(code, INNER, "exec"), ns)

# ============================================================================
# 4-way comparison
# ============================================================================
print("\n" + "="*100)
print("  PHASE C combine — 4-way (Base / D / S / DS)")
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

base = load_logs("phase_b_baseline")
d_run = load_logs("phase_c_D")
s_run = load_logs("phase_c_S")
ds_run = load_logs(OUT_PREFIX)

IS_END = pd.Timestamp("2022-01-01")
def split_metrics(df, label):
    return metrics(df[df["ymd"]<IS_END], f"{label} IS"), metrics(df[df["ymd"]>=IS_END], f"{label} OOS")

mb, md, ms, mds = metrics(base,"Base"), metrics(d_run,"D"), metrics(s_run,"S"), metrics(ds_run,"DS")
mbi, mbo = split_metrics(base,"Base")
mdi, mdo = split_metrics(d_run,"D")
msi, mso = split_metrics(s_run,"S")
mdsi, mdso = split_metrics(ds_run,"DS")

all_m = [mb, md, ms, mds, mbi, mdi, msi, mdsi, mbo, mdo, mso, mdso]
mdf = pd.DataFrame(all_m)
print("\n")
print(mdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x))

# Year-by-year 4-way
def yearly(df, label):
    df = df.copy(); df["year"] = df["ymd"].dt.year
    return pd.DataFrame([{"year":y, label:(g["nav"].iloc[-1]/g["nav"].iloc[0]-1)*100}
                         for y,g in df.groupby("year") if len(g)>=5])
yr = (yearly(base,"Base%")
      .merge(yearly(d_run,"D%"), on="year")
      .merge(yearly(s_run,"S%"), on="year")
      .merge(yearly(ds_run,"DS%"), on="year"))
yr["dD"]  = yr["D%"]  - yr["Base%"]
yr["dS"]  = yr["S%"]  - yr["Base%"]
yr["dDS"] = yr["DS%"] - yr["Base%"]
# Additivity check: DS−Base vs (D−Base)+(S−Base)
yr["expected_DS"] = yr["dD"] + yr["dS"]
yr["DS_extra"]    = yr["dDS"] - yr["expected_DS"]
print("\nYear-by-year:")
print(yr.to_string(index=False, float_format=lambda x: f"{x:+.2f}" if isinstance(x,float) else x))

# Save summary
out = ["# Phase C combine — D+S 4-way comparison\n"]
out.append("\n## Metrics\n")
out.append("| Variant | Period | CAGR% | Sharpe | MaxDD% | Calmar | Final B |")
out.append("|---|---|---|---|---|---|---|")
for m in all_m:
    period = "FULL" if "IS" not in m["label"] and "OOS" not in m["label"] else ("IS" if "IS" in m["label"] else "OOS")
    out.append(f"| {m['label']} | {period} | {m['CAGR%']:+.2f} | {m['Sharpe']:.2f} | {m['MaxDD%']:+.2f} | {m['Calmar']:.2f} | {m['Final B']:.1f} |")

out.append("\n## Year-by-year (additivity check)\n")
out.append("| Year | Base% | D% | S% | DS% | dD | dS | dDS | Expected dDS=(dD+dS) | DS_extra |")
out.append("|---|---|---|---|---|---|---|---|---|---|")
for _,r in yr.iterrows():
    out.append(f"| {int(r['year'])} | {r['Base%']:+.2f} | {r['D%']:+.2f} | {r['S%']:+.2f} | {r['DS%']:+.2f} | {r['dD']:+.2f} | {r['dS']:+.2f} | {r['dDS']:+.2f} | {r['expected_DS']:+.2f} | {r['DS_extra']:+.2f} |")

# Gate
def gate(m_var, m_base, ratio=0.97):
    return (m_var["CAGR%"] >= m_base["CAGR%"] * ratio) and (m_var["Calmar"] >= m_base["Calmar"] * ratio)
out.append(f"\n## GATEs (OOS 2022-2026)\n")
for label, mvar in [("D", mdo), ("S", mso), ("DS", mdso)]:
    extra = ""
    if label == "DS":
        extra = f" | additive baseline (D+S extras): CAGR=+{(mdo['CAGR%']-mbo['CAGR%']) + (mso['CAGR%']-mbo['CAGR%']):.2f}pp; observed: {mdso['CAGR%']-mbo['CAGR%']:+.2f}pp"
    out.append(f"- {label}: OOS CAGR {mvar['CAGR%']:+.2f}% (Δ {mvar['CAGR%']-mbo['CAGR%']:+.2f}pp); Calmar {mvar['Calmar']:.2f} (Δ {mvar['Calmar']-mbo['Calmar']:+.2f}) — **{'PASS' if gate(mvar, mbo) else 'FAIL'}**{extra}")

with open(os.path.join(WORKDIR,"data","phase_c_combine_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("\n  data/phase_c_combine_summary.md")
