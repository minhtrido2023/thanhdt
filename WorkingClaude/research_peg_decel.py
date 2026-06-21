#!/usr/bin/env python3
"""
research_peg_decel.py
=====================
Test hypothesis: PEG-decel pattern predicts peak-reversal.

  When stock has (a) high prior growth + (b) premium PE + (c) recent growth deceleration,
  market re-rates the multiple down → big negative forward return.

Method:
  1) Pull (ticker, quarter) panel with NP_TTM, PE, GPM, ROIC, CF_OA history
  2) Compute candidate indicators
  3) Compute Spearman IC of each indicator vs O1Y forward return
  4) Slice by "premium-growth subset" (high PE + high prior growth) to see if signal is stronger there
  5) Validate on 5 case tickers (VCS/DGC/VNM/FPT/MWG)
  6) If significant signal found → propose as LH filter
"""
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
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── PULL DATA ───────────────────────────────────────────────────────────
print("Pulling FA panel + O1Y/O6M forward returns ...")
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P4,
    f.GPM_P0, f.GPM_P4,
    f.ROIC_Trailing, f.ROIC5Y, f.ROE_Trailing,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.PE, f.PE_MA5Y, f.PE_SD5Y, f.PE_MA3M,
    f.PB, f.OShares,
    t.Close, t.ICB_Code, t.Volume_3M_P50,
    tp.O6M, tp.O1Y, tp.O2Y,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sector,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker_prune` AS tp
    ON tp.ticker = t.ticker AND tp.time = t.time
  WHERE f.time >= '2014-01-01'
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
    AND f.PE > 0
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""
df = bq_query(SQL)
df["time"] = pd.to_datetime(df["time"])
print(f"  {len(df):,} (ticker,quarter) rows, {df['ticker'].nunique()} tickers")

# ─── BUILD CANDIDATE INDICATORS ──────────────────────────────────────────
print("\nBuilding candidate indicators ...")

# 1) NP TTM growth: now (P0..P3) vs prv year (P4..P7)
df["NP_TTM_now"] = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
df["NP_TTM_prv"] = df[[f"NP_P{i}" for i in range(4,8)]].sum(axis=1, skipna=False)
df["NP_growth_yoy"] = (df["NP_TTM_now"] / df["NP_TTM_prv"].abs().replace(0,np.nan) - 1).clip(-5,5)

# 2) NP_P0 growth single-quarter YoY (already exists in some form)
df["NP_qq_yoy"] = (df["NP_P0"] / df["NP_P4"].abs().replace(0,np.nan) - 1).clip(-5,5)

# 3) Revenue YoY
df["Rev_yoy"] = (df["Revenue_P0"] / df["Revenue_P4"].abs().replace(0,np.nan) - 1).clip(-5,5)

# 4) GPM change YoY (margin compression)
df["GPM_change"] = df["GPM_P0"] - df["GPM_P4"]

# 5) ROIC trend: ROIC_Trailing vs ROIC5Y (declining trailing = signal)
df["ROIC_diff_trail_vs_5Y"] = df["ROIC_Trailing"] - df["ROIC5Y"]

# 6) Cash flow quality: CF_OA / NP_TTM (low = earnings quality issue)
df["CF_4Q"] = df[[f"CF_OA_P{i}" for i in range(4)]].sum(axis=1, skipna=True)
df["CFOA_NP_ratio"] = (df["CF_4Q"] / df["NP_TTM_now"].abs().replace(0,np.nan)).clip(-5,5)

# 7) PE z-score
df["PE_z"] = ((df["PE"] - df["PE_MA5Y"]) / df["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)

# 8) PE vs sector median (premium) — within (sector, quarter)
df["PE_log"] = np.log(df["PE"].clip(lower=0.1))
df["PE_sector_z"] = df.groupby(["sector","quarter"])["PE_log"].transform(lambda x: (x - x.median()) / x.std() if x.std() > 0 else 0)

# 9) PEG ratio: PE / NP_growth_yoy (where growth is positive; otherwise PEG meaningless)
df["PEG"] = np.where(df["NP_growth_yoy"] > 0.02, df["PE"] / (df["NP_growth_yoy"] * 100), np.nan)
df["PEG"] = df["PEG"].clip(0, 30)

# 10) Prior 3Y growth flag (high-growth history)
# We need lookback over 12 quarters. Sort and shift per ticker.
df = df.sort_values(["ticker","time"]).reset_index(drop=True)
# Rolling: 4Q ago NP_TTM (1Y ago growth state)
df["NP_growth_yoy_lag4"] = df.groupby("ticker")["NP_growth_yoy"].shift(4)
df["NP_growth_yoy_lag8"] = df.groupby("ticker")["NP_growth_yoy"].shift(8)

# 11) **KEY: Growth deceleration** — was high, now lower
# decel = max(growth in last 4Q) - current growth. Positive = deceleration.
df["NP_growth_max4Q"] = df.groupby("ticker")["NP_growth_yoy"].transform(
    lambda x: x.rolling(4, min_periods=2).max().shift(0))
df["NP_growth_decel_from_4Q_max"] = df["NP_growth_max4Q"] - df["NP_growth_yoy"]

# 12) **KEY: Was high-growth recently?**
df["was_high_growth"] = (df["NP_growth_yoy_lag4"] > 0.30) | (df["NP_growth_yoy_lag8"] > 0.30)

# 13) **KEY: PE/Growth dislocation** — PE didn't compress to match growth fall
df["PE_to_growth"] = df["PE"] / np.maximum(df["NP_growth_yoy"] * 100, 1)

# 14) Multi-Q margin compression
df["GPM_compression_flag"] = (df["GPM_change"] < -0.02).astype(int)  # GPM dropped > 2pp YoY

# 15) MktCap
df["MktCap"] = df["OShares"] * df["Close"]

# ─── PEAK REVERSAL EVENT DEFINITION ──────────────────────────────────────
# A "peak event" = stock that was in premium-growth zone AND forward 1Y return < -20%
df["is_premium"] = (df["PE_sector_z"] > 0.5) & (df["was_high_growth"] == True)
df["is_peak_reversal"] = (df["O1Y"] < -20)  # forward 1Y return < -20%
df["is_premium_reversal"] = df["is_premium"] & df["is_peak_reversal"]

print(f"\nPanel stats:")
print(f"  Premium + high prior growth rows: {df['is_premium'].sum():,} ({100*df['is_premium'].mean():.1f}%)")
print(f"  Forward 1Y < -20% (any): {df['is_peak_reversal'].sum():,}")
print(f"  Premium AND peak-reversal: {df['is_premium_reversal'].sum():,}")

# Base rate
sub_with_o1y = df.dropna(subset=["O1Y"])
prem_with_o1y = sub_with_o1y[sub_with_o1y["is_premium"]]
print(f"\n  Base rate forward-1Y < -20%: {sub_with_o1y['is_peak_reversal'].mean()*100:.1f}% (full universe)")
print(f"  Premium subset: {prem_with_o1y['is_peak_reversal'].mean()*100:.1f}%")
print(f"  Median O1Y full: {sub_with_o1y['O1Y'].median():+.2f}%")
print(f"  Median O1Y premium: {prem_with_o1y['O1Y'].median():+.2f}%")

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

print("\n" + "="*100)
print(f"  SPEARMAN IC vs O1Y forward return")
print("="*100)
print(f"\n  {'Indicator':<35}{'IC (full)':>12}{'N (full)':>10}{'IC (premium)':>15}{'N (prem)':>10}")
ic_rows = []
for c in candidates:
    ic_full, n_full = spearman_ic(df[c], df["O1Y"])
    prem = df[df["is_premium"]]
    ic_prem, n_prem = spearman_ic(prem[c], prem["O1Y"])
    print(f"  {c:<35}{ic_full:>+12.4f}{n_full:>10}{ic_prem:>+15.4f}{n_prem:>10}")
    ic_rows.append({"indicator":c,"ic_full":ic_full,"n_full":n_full,"ic_premium":ic_prem,"n_premium":n_prem})

# ─── COMBINATION FILTER TEST ─────────────────────────────────────────────
# Hypothesis: prior-high-growth + premium PE + recent decel → bad forward
# Filter rule: was_high_growth=True AND PE_sector_z > 0.5 AND NP_growth_decel > 0.15
print("\n" + "="*100)
print("  COMBINATION FILTER: high-prior-growth + premium PE + growth decel")
print("="*100)

df["filter_PEG_decel"] = (df["was_high_growth"] == True) & (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)
flag = df[df["filter_PEG_decel"] & df["O1Y"].notna()]
nofl = df[~df["filter_PEG_decel"] & df["O1Y"].notna()]

print(f"\n  Flag fired: {len(flag):,} rows ({100*len(flag)/df['O1Y'].notna().sum():.1f}%)")
print(f"  {'group':<20}{'N':>8}{'O1Y median':>14}{'O1Y mean':>12}{'WR (>0)':>10}{'big_loss (<-20%)':>20}")
print(f"  {'flagged':<20}{len(flag):>8}{flag['O1Y'].median():>+13.2f}%{flag['O1Y'].mean():>+11.2f}%{(flag['O1Y']>0).mean()*100:>9.1f}%{(flag['O1Y']<-20).mean()*100:>19.1f}%")
print(f"  {'not flagged':<20}{len(nofl):>8}{nofl['O1Y'].median():>+13.2f}%{nofl['O1Y'].mean():>+11.2f}%{(nofl['O1Y']>0).mean()*100:>9.1f}%{(nofl['O1Y']<-20).mean()*100:>19.1f}%")

# Try multiple filter variants
print("\n  Alternate filter variants:")
filters = [
    ("PE_decel only", (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HighGrowth + decel", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("PE_z>1 + decel", (df["PE_z"] > 1.0) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("PE_sec>0.5 + decel", (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+PE_sec>0.5+decel", (df["was_high_growth"] == True) & (df["PE_sector_z"] > 0.5) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+PE_z>1+decel", (df["was_high_growth"] == True) & (df["PE_z"] > 1.0) & (df["NP_growth_decel_from_4Q_max"] > 0.15)),
    ("HiGrowth+decel+GPM_drop", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15) & (df["GPM_change"] < 0)),
    ("HiGrowth+decel+ROIC_drop", (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15) & (df["ROIC_diff_trail_vs_5Y"] < 0)),
]

print(f"\n  {'filter':<28}{'N_flag':>8}{'O1Y med':>12}{'O1Y mean':>12}{'WR':>8}{'big_loss%':>11}{'vs_base':>10}")
base_med = sub_with_o1y["O1Y"].median()
for name, mask in filters:
    sub = df[mask & df["O1Y"].notna()]
    if len(sub) < 50: continue
    med = sub["O1Y"].median()
    delta = med - base_med
    print(f"  {name:<28}{len(sub):>8}{med:>+11.2f}%{sub['O1Y'].mean():>+11.2f}%{(sub['O1Y']>0).mean()*100:>7.1f}%{(sub['O1Y']<-20).mean()*100:>10.1f}%{delta:>+9.2f}pp")

# ─── 5-CASE VALIDATION ───────────────────────────────────────────────────
print("\n" + "="*100)
print("  5-CASE VALIDATION — does PEG-decel filter catch VCS/DGC/VNM/FPT/MWG peaks?")
print("="*100)

CASES = ["VCS", "DGC", "VNM", "FPT", "MWG"]
df["any_filter"] = (df["was_high_growth"] == True) & (df["NP_growth_decel_from_4Q_max"] > 0.15)

for tk in CASES:
    tk_data = df[df["ticker"] == tk].sort_values("time")
    if len(tk_data) == 0: continue
    print(f"\n--- {tk} ---")
    # Show quarters where any of the filters would have fired
    for _, row in tk_data.iterrows():
        flags = []
        if row.get("filter_PEG_decel", False): flags.append("PEG-decel")
        if (row.get("was_high_growth") == True) and (row.get("NP_growth_decel_from_4Q_max", 0) > 0.15): flags.append("HiG-decel")
        if row.get("PE_z", 0) > 1.0: flags.append("PE_hi")
        o1y = row.get("O1Y", np.nan)
        if flags or (pd.notna(o1y) and o1y < -10):
            print(f"  {row['quarter']:<8} PE={row['PE']:>5.1f} PE_z={row['PE_z']:+5.2f} NP_yoy={row['NP_growth_yoy']*100:>+6.1f}% decel={row['NP_growth_decel_from_4Q_max']*100:>+6.1f}pp "
                  f"O1Y={o1y:>+6.1f}% [{','.join(flags)}]")

# Save
df.to_csv("data/research_peg_decel_panel.csv", index=False)
print("\nSaved: research_peg_decel_panel.csv")
print("DONE")
