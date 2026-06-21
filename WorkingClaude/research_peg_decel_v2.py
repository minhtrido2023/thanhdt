#!/usr/bin/env python3
"""
research_peg_decel_v2.py
========================
Re-analyze with O1Y interpreted correctly as a RATIO (1.03 = +3% return).
Uses cached panel from research_peg_decel_panel.csv.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

df = pd.read_csv("data/research_peg_decel_panel.csv", parse_dates=["time"])
# Convert O1Y, O6M, O2Y from ratio to percent return
for c in ["O6M","O1Y","O2Y"]:
    df[f"{c}_ret"] = (df[c] - 1) * 100

print(f"Panel: {len(df):,} rows")
print(f"\nForward return distributions (percent):")
print(f"  O1Y_ret: min={df['O1Y_ret'].min():.1f}% max={df['O1Y_ret'].max():.1f}% median={df['O1Y_ret'].median():.1f}%")
print(f"  Quantiles: {df['O1Y_ret'].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).to_dict()}")

# Now correctly identify peak reversals
df["is_premium"] = (df["PE_sector_z"] > 0.5) & (df["was_high_growth"] == True)
df["is_peak_reversal"] = (df["O1Y_ret"] < -20)
df["is_big_loss"] = (df["O1Y_ret"] < -30)
print(f"\n  Premium + high prior growth: {df['is_premium'].sum():,} ({100*df['is_premium'].mean():.1f}%)")
print(f"  Forward 1Y < -20% (any): {df['is_peak_reversal'].sum():,} ({100*df['is_peak_reversal'].mean():.1f}%)")
print(f"  Forward 1Y < -30% (big loss): {df['is_big_loss'].sum():,} ({100*df['is_big_loss'].mean():.1f}%)")

sub = df.dropna(subset=["O1Y_ret"])
prem = sub[sub["is_premium"]]
print(f"\n  Base rate forward-1Y < -20% (full): {sub['is_peak_reversal'].mean()*100:.1f}%")
print(f"  Premium subset                     : {prem['is_peak_reversal'].mean()*100:.1f}%")
print(f"  Median O1Y full   : {sub['O1Y_ret'].median():+.2f}%")
print(f"  Median O1Y premium: {prem['O1Y_ret'].median():+.2f}%")

# ─── IC ANALYSIS ─────────────────────────────────────────────────────────
def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 30: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

candidates = [
    "NP_growth_yoy", "NP_qq_yoy", "Rev_yoy", "GPM_change", "ROIC_diff_trail_vs_5Y",
    "CFOA_NP_ratio", "PE_z", "PE_sector_z", "PEG", "NP_growth_decel_from_4Q_max",
    "PE_to_growth", "GPM_compression_flag",
]

print("\n" + "="*110)
print("  SPEARMAN IC vs O1Y forward return (correct units)")
print("="*110)
print(f"\n  {'Indicator':<35}{'IC (full)':>11}{'N (full)':>9}{'IC (premium)':>14}{'N (prem)':>9}")
for c in candidates:
    ic_full, n_full = spearman_ic(df[c], df["O1Y_ret"])
    ic_prem, n_prem = spearman_ic(prem[c], prem["O1Y_ret"])
    print(f"  {c:<35}{ic_full:>+11.4f}{n_full:>9}{ic_prem:>+14.4f}{n_prem:>9}")

# ─── COMBINATION FILTERS — test each as DEAL-BREAKER for LH portfolio ────
print("\n" + "="*110)
print("  COMBINATION FILTERS — flag = exclude from LH")
print("="*110)

filters = [
    ("[reference] full universe (no filter)", pd.Series(True, index=df.index)),
    ("decel only (>15pp)", df["NP_growth_decel_from_4Q_max"] > 0.15),
    ("HighGrowth + decel", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("PE_z>1 + decel", (df["PE_z"] > 1.0) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("PE_sec>0.5 + decel", (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+PE_sec>0.5+decel", (df["was_high_growth"] == True) & (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+PE_z>1+decel", (df["was_high_growth"] == True) & (df["PE_z"] > 1.0) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+decel+GPM_drop", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15) & (df["GPM_change"] < 0)),
    ("HiGrowth+decel+ROIC_drop", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15) & (df["ROIC_diff_trail_vs_5Y"] < 0)),
    # Stricter: high PE AND decel AND was hi-growth AND margin/ROIC drop
    ("STRICT_PEG_decel", (df["was_high_growth"] == True) & (df["PE_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.20) & (df["NP_growth_yoy"] < 0.15)),
    # Pure absolute growth turn negative
    ("Growth_turn_negative", (df["was_high_growth"] == True) & (df["NP_growth_yoy"] < 0)),
    # Premium + growth fell below 10%
    ("Premium+growth<10pct", (df["PE_sector_z"] > 0.3) & (df["NP_growth_yoy"] < 0.10) & (df["was_high_growth"] == True)),
]

base_med = sub["O1Y_ret"].median()
print(f"\n  {'Filter':<38}{'N_flag':>8}{'O1Y med':>11}{'O1Y mean':>11}{'WR%':>7}{'big-loss%':>11}{'vs_base':>10}")
for name, mask in filters:
    sub_f = df[mask & df["O1Y_ret"].notna()]
    if len(sub_f) < 30: continue
    med = sub_f["O1Y_ret"].median()
    mean = sub_f["O1Y_ret"].mean()
    wr = (sub_f["O1Y_ret"] > 0).mean() * 100
    big_loss = (sub_f["O1Y_ret"] < -20).mean() * 100
    delta = med - base_med
    print(f"  {name:<38}{len(sub_f):>8}{med:>+10.2f}%{mean:>+10.2f}%{wr:>6.1f}%{big_loss:>10.1f}%{delta:>+9.2f}pp")

# ─── 5-CASE VALIDATION — does best filter catch the peaks? ───────────────
print("\n" + "="*110)
print("  5-CASE VALIDATION — which quarters get flagged before each ticker's peak?")
print("="*110)

CASES = ["VCS", "DGC", "VNM", "FPT", "MWG"]
df["filter_HG_PEsec_decel"] = (df["was_high_growth"] == True) & (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)
df["filter_HG_PEz1_decel"] = (df["was_high_growth"] == True) & (df["PE_z"] > 1.0) & (df["NP_growth_decel_from_4Q_max"] > 0.15)
df["filter_HG_decel"] = (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15)
df["filter_growthturnneg"] = (df["was_high_growth"] == True) & (df["NP_growth_yoy"] < 0)

prices = pd.read_csv("data/prices_lh.csv", parse_dates=["time"])
for tk in CASES:
    tk_data = df[df["ticker"] == tk].sort_values("time")
    tk_px = prices[prices["ticker"] == tk].sort_values("time")
    peak_dt = tk_px.loc[tk_px["Close"].idxmax(), "time"]
    peak_px = tk_px["Close"].max()
    print(f"\n--- {tk}  peak {peak_px:.0f} on {peak_dt.date()} ---")
    # Show quarters with any filter flag
    rows_to_show = tk_data[
        tk_data["filter_HG_PEsec_decel"] | tk_data["filter_HG_PEz1_decel"] |
        tk_data["filter_HG_decel"] | tk_data["filter_growthturnneg"]
    ]
    if len(rows_to_show) == 0:
        print("  (no filter fires)")
        continue
    for _, row in rows_to_show.iterrows():
        flags = []
        if row["filter_HG_PEsec_decel"]: flags.append("HG+PEsec+decel")
        if row["filter_HG_PEz1_decel"]: flags.append("HG+PEz+decel")
        if row["filter_HG_decel"]: flags.append("HG+decel")
        if row["filter_growthturnneg"]: flags.append("Growth_neg")
        days_to_peak = (peak_dt - row["time"]).days
        print(f"  {row['quarter']:<8} t={row['time'].date()} ({days_to_peak:+5d}d to peak)  "
              f"PE={row['PE']:>5.1f} NP_yoy={row['NP_growth_yoy']*100:>+6.1f}% "
              f"decel={row['NP_growth_decel_from_4Q_max']*100:>+6.1f}pp  O1Y={row['O1Y_ret']:>+6.1f}%  [{','.join(flags)}]")

print("\nDONE")
