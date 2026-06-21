#!/usr/bin/env python3
"""analyze_path_dependency.py — Compare fresh-start vs 2014-start backtests.

For each start date in {2018, 2020, 2022, 2024}:
  fresh CAGR (50B init that date -> 2026-05) vs rebased 2014-start CAGR (same window).
Quantifies how much path dependency adds/subtracts from returns.

Reads: data/5sys_prodspec_<startshort>_<endshort>.csv (5 files)
Writes: data/path_dependency_report.md + .csv + .png
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

# 5 NAV files
FILES = {
    "2014-01": "data/5sys_prodspec_201401_202605.csv",  # canonical
    "2018-01": "data/5sys_prodspec_201801_202605.csv",
    "2020-01": "data/5sys_prodspec_202001_202605.csv",
    "2022-01": "data/5sys_prodspec_202201_202605.csv",
    "2024-01": "data/5sys_prodspec_202401_202605.csv",
}
SYSTEMS = ["V1_V11_TQ34b","V2_V12_TQ34b","V3_V12_LIVE","V4_V121_ENS_TQ34b","V5_V4_KellyQ2"]
SHORT   = ["V1","V2","V3","V4","V5"]

# Load
dfs = {}
for tag, f in FILES.items():
    if not os.path.exists(f):
        print(f"WARN: missing {f}")
        continue
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    dfs[tag] = df
    print(f"{tag}: shape={df.shape}, range={df.index.min().date()}->{df.index.max().date()}")

if "2014-01" not in dfs:
    print("ERROR: canonical 2014-start missing"); sys.exit(1)
canon = dfs["2014-01"]

def cagr_dd_sharpe(s):
    s = s.dropna()
    if len(s) < 30: return None, None, None, None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1]-s.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s-s.cummax())/s.cummax()).min()
    return cagr*100, sh, dd*100, s.iloc[-1]/s.iloc[0]

# ─── 1. Compare fresh-start vs rebased 2014-start ───────────────────────────
rows = []
for tag in ["2018-01","2020-01","2022-01","2024-01"]:
    if tag not in dfs: continue
    fresh = dfs[tag]
    fresh_start = fresh.index.min()
    fresh_end = fresh.index.max()
    # Rebase canonical over the SAME window
    canon_sub = canon[(canon.index>=fresh_start) & (canon.index<=fresh_end)]
    if len(canon_sub) < 30: continue
    for sys_col, short in zip(SYSTEMS, SHORT):
        # Fresh: nav already starts at 1.0 (relative)
        fresh_s = fresh[sys_col].dropna()
        # 2014-start: rebase NAV to 1.0 at fresh_start
        canon_s_raw = canon_sub[sys_col].dropna()
        if len(canon_s_raw) < 30 or len(fresh_s) < 30: continue
        canon_s = canon_s_raw / canon_s_raw.iloc[0]

        f_cagr, f_sh, f_dd, f_w = cagr_dd_sharpe(fresh_s)
        c_cagr, c_sh, c_dd, c_w = cagr_dd_sharpe(canon_s)
        if f_cagr is None or c_cagr is None: continue

        rows.append({
            "Start": tag, "System": short,
            "Fresh_CAGR": f_cagr, "Canon_CAGR": c_cagr, "ΔCAGR": f_cagr - c_cagr,
            "Fresh_Sh": f_sh, "Canon_Sh": c_sh, "ΔSharpe": f_sh - c_sh,
            "Fresh_DD": f_dd, "Canon_DD": c_dd, "ΔDD": f_dd - c_dd,
            "Fresh_Wealth": f_w, "Canon_Wealth": c_w,
            "Years": (fresh_end - fresh_start).days / 365.25,
        })
gap_df = pd.DataFrame(rows)
gap_df.to_csv("data/path_dependency_gaps.csv", index=False)

# ─── 2. Markdown report ─────────────────────────────────────────────────────
md = []
md.append("# Path-dependency Variance — Fresh-start vs 2014-start backtests")
md.append("")
md.append(f"*Generated: {pd.Timestamp.now().date()}*  •  *All 5 systems, prod-spec, 50B init*  •  *End: {canon.index.max().date()}*")
md.append("")
md.append("Question: nếu start sim FRESH 50B tại 2018/2020/2022/2024, kết quả có khác so với 2014-start (đã chạy liên tục, mang positions tích lũy)?")
md.append("")
md.append("## A. CAGR comparison — Fresh vs Rebased-canonical (same end date)")
md.append("")
for tag in ["2018-01","2020-01","2022-01","2024-01"]:
    sub = gap_df[gap_df["Start"]==tag]
    if len(sub)==0: continue
    years = sub["Years"].iloc[0]
    md.append(f"### Start = {tag}  →  end {canon.index.max().date()}  ({years:.2f} years)")
    md.append("")
    md.append("| System | Fresh CAGR | Canon CAGR (rebased) | ΔCAGR | Fresh Sh | Canon Sh | ΔSh | Fresh DD | Canon DD | ΔDD |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in sub.iterrows():
        md.append(f"| {r['System']} | {r['Fresh_CAGR']:+.2f}% | {r['Canon_CAGR']:+.2f}% | **{r['ΔCAGR']:+.2f}pp** | {r['Fresh_Sh']:+.2f} | {r['Canon_Sh']:+.2f} | {r['ΔSharpe']:+.2f} | {r['Fresh_DD']:+.2f}% | {r['Canon_DD']:+.2f}% | {r['ΔDD']:+.2f}pp |")
    md.append("")
    avg_d = sub["ΔCAGR"].mean()
    md.append(f"**Avg ΔCAGR across 5 systems = {avg_d:+.2f}pp**.  ")
    if avg_d > 1: md.append(f"Fresh-start outperforms 2014-start by {avg_d:.2f}pp on average — favourable timing or scale benefit.")
    elif avg_d < -1: md.append(f"Fresh-start underperforms 2014-start by {abs(avg_d):.2f}pp — likely deployment lag + carryover momentum loss.")
    else: md.append("Negligible average gap — path dependency washes out at this start.")
    md.append("")

md.append("## B. Gap matrix (ΔCAGR fresh − canonical, pp)")
md.append("")
pv = gap_df.pivot_table(index="Start", columns="System", values="ΔCAGR")
pv = pv.reindex(columns=SHORT)
md.append("| Start | " + " | ".join(SHORT) + " | Mean |")
md.append("|---|" + "|".join(["---:"]*(len(SHORT)+1)) + "|")
for tag in pv.index:
    cells = [f"{pv.loc[tag,c]:+.2f}" if not pd.isna(pv.loc[tag,c]) else "-" for c in SHORT]
    mean = pv.loc[tag].mean()
    md.append(f"| {tag} | " + " | ".join(cells) + f" | **{mean:+.2f}** |")
md.append("")
col_means = pv.mean()
md.append(f"**Column means** (avg gap per system across 4 start dates):  " + " · ".join([f"{c}={col_means[c]:+.2f}pp" for c in SHORT]))
md.append("")

md.append("## C. Wealth comparison")
md.append("")
md.append("| Start | System | Fresh Wealth | Canon Wealth (rebased) | Ratio Fresh/Canon |")
md.append("|---|---|---:|---:|---:|")
for _, r in gap_df.iterrows():
    md.append(f"| {r['Start']} | {r['System']} | {r['Fresh_Wealth']:.3f}x | {r['Canon_Wealth']:.3f}x | {r['Fresh_Wealth']/r['Canon_Wealth']:.3f} |")
md.append("")

# ─── 3. Plot equity curves: fresh vs canon for V5 only (most volatile) ──────
fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharey=False)
for ax, tag in zip(axes.ravel(), ["2018-01","2020-01","2022-01","2024-01"]):
    if tag not in dfs:
        ax.set_visible(False); continue
    fresh = dfs[tag]
    fresh_start = fresh.index.min()
    canon_sub = canon[canon.index >= fresh_start]
    for sys_col, short, color in zip(["V1_V11_TQ34b","V5_V4_KellyQ2"], ["V1","V5"], ["#1f77b4","#9467bd"]):
        fresh_s = fresh[sys_col].dropna()
        canon_s = canon_sub[sys_col].dropna()
        if len(canon_s) < 2: continue
        canon_rb = canon_s / canon_s.iloc[0]
        ax.plot(fresh_s.index, fresh_s, label=f"{short} fresh", color=color, linewidth=1.2)
        ax.plot(canon_rb.index, canon_rb, label=f"{short} canon-rebased", color=color, linewidth=1.0, linestyle="--", alpha=0.7)
    ax.set_title(f"Fresh-start {tag} (init=1.0) vs canon (rebased)")
    ax.grid(True, alpha=0.3); ax.legend(loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("data/path_dependency_curves.png", dpi=120)
plt.close()
md.append("## D. Equity curves (V1 + V5)")
md.append("")
md.append("![curves](data/path_dependency_curves.png)")
md.append("")

# ─── 4. Synthesis ───────────────────────────────────────────────────────────
md.append("## E. Synthesis")
md.append("")
all_gaps = gap_df["ΔCAGR"]
md.append(f"- **20 datapoints** (5 systems × 4 start dates)")
md.append(f"- Mean ΔCAGR (fresh - canonical, rebased): **{all_gaps.mean():+.2f}pp**")
md.append(f"- Std ΔCAGR: **{all_gaps.std():.2f}pp**")
md.append(f"- Min: {all_gaps.min():+.2f}pp  (start={gap_df.loc[all_gaps.idxmin(),'Start']}, sys={gap_df.loc[all_gaps.idxmin(),'System']})")
md.append(f"- Max: {all_gaps.max():+.2f}pp  (start={gap_df.loc[all_gaps.idxmax(),'Start']}, sys={gap_df.loc[all_gaps.idxmax(),'System']})")
md.append(f"- Fresh > Canon: {(all_gaps>0).sum()}/{len(all_gaps)}  ({(all_gaps>0).mean()*100:.0f}%)")
md.append("")
md.append("**Reading**: if average is near 0 with high std, path dependency is large but symmetric → start timing is a coin flip. If average is positive/negative, there's systematic carryover bias.")
md.append("")
md.append("## F. Source")
md.append("")
md.append("- `data/5sys_prodspec_*.csv` — 5 daily NAV CSVs (one per start date)")
md.append("- `data/path_dependency_gaps.csv` — gap table")
md.append("- `data/path_dependency_curves.png` — V1/V5 fresh vs canon overlay")
md.append("- `run_5systems_prodspec.py` — engine (env START_DATE controls start)")

with open("data/path_dependency_report.md","w",encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"\nWrote data/path_dependency_report.md ({len(md)} lines)")
print(f"Wrote data/path_dependency_gaps.csv ({len(gap_df)} rows)")
print(f"Wrote data/path_dependency_curves.png")

# Quick stdout summary
print("\n=== GAP MATRIX (fresh - canonical CAGR, pp) ===")
print(pv.round(2).to_string())
print(f"\nMean gap = {all_gaps.mean():+.2f}pp, std = {all_gaps.std():.2f}pp")
