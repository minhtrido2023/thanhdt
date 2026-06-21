#!/usr/bin/env python3
"""
build_fa_ratings_v9.py
======================
Build tav2_bq.fa_ratings_v9:
  - RE tickers (ICB 8633): re-rank with v9 axes (AdvCust_YoY/QoQ in Growth,
    RevCoverage in Cash, sector-conditional weights: Stab 0.10, Cash 0.22,
    Growth 0.17). Tier ranked WITHIN RE cohort per quarter.
  - Non-RE: use existing tav2_bq.fa_ratings unchanged.

Schema matches fa_ratings exactly so SIGNAL_V10 can swap table name.

Output: fa_ratings_v9.csv  +  uploaded to tav2_bq.fa_ratings_v9
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, sys, tempfile, io
from io import StringIO
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
ICB_RE  = 8633.0

WEIGHTS_RE_V9 = {
    "quality":     0.18,
    "stability":   0.10,   # ↓ from 0.18
    "cash":        0.22,   # ↑ from 0.18
    "shareholder": 0.15,
    "growth":      0.17,   # ↑ from 0.13
    "health":      0.08,
    "valuation":   0.10,
}
TIERS = [("A", 0.90, 1.00), ("B", 0.70, 0.90), ("C", 0.40, 0.70),
         ("D", 0.15, 0.40), ("E", 0.00, 0.15)]

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── 1. Pull RE cohort with full FA inputs + new fields ────────────────────────
SQL_RE = f"""
WITH joined AS (
  SELECT
    f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.FSCORE,
    f.NP_R, f.Revenue_YoY_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y,
    SAFE_DIVIDE(f.CF_OA_P0, f.NP_P0) AS CFOA_NP,
    f.DY, f.Dividend_Min3Y,
    SAFE_DIVIDE(f.CF_OA_5Y + f.CF_Invest_5Y, ABS(f.CF_OA_5Y)) AS FCF_OA_ratio,
    f.Debt_Eq_P0, f.IntCov_P0, f.CashR_P0,
    SAFE_DIVIDE(f.PE - f.PE_MA5Y, f.PE_SD5Y) AS PE_self_z,
    SAFE_DIVIDE(f.PB - f.PB_MA5Y, f.PB_SD5Y) AS PB_self_z,
    CASE WHEN f.PE > 0 THEN SAFE_DIVIDE(f.NP_R, f.PE) ELSE NULL END AS growth_yield,
    f.PE, f.PB, f.PCF,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
    f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0,GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    CASE WHEN GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                       f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7) > 0
         THEN SAFE_DIVIDE(f.Revenue_P0,GREATEST(f.Revenue_P0,f.Revenue_P1,f.Revenue_P2,f.Revenue_P3,
                                                 f.Revenue_P4,f.Revenue_P5,f.Revenue_P6,f.Revenue_P7))
         ELSE NULL END AS Rev_peak_ratio,
    f.AdvCust_P0, f.AdvCust_P1, f.AdvCust_P4, f.UnearnRev_P0,
    t.ICB_Code,
    t.Volume_3M_P50 * t.Close AS trading_value_1M,
    t.profit_3M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time
    AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  WHERE f.time >= "2014-01-01"
    AND t.ICB_Code = {ICB_RE}
    AND t.Volume_3M_P50 IS NOT NULL
    AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Pulling RE cohort ...")
df_re = bq_query(SQL_RE, "re_pull")
print(f"  {len(df_re):,} RE (ticker,quarter) rows, {df_re['ticker'].nunique()} tickers")

# ─── 2. New indicators ─────────────────────────────────────────────────────────
df_re["Revenue_TTM"] = df_re[["Revenue_P0","Revenue_P1","Revenue_P2","Revenue_P3"]].sum(axis=1, min_count=2)
df_re["RevCoverage"] = ((df_re["AdvCust_P0"].fillna(0) + df_re["UnearnRev_P0"].fillna(0))
                        / df_re["Revenue_TTM"].replace(0, np.nan)).clip(lower=0, upper=20)
def _g(num, den): return (num / den.replace(0, np.nan) - 1).clip(lower=-1.0, upper=5.0)
df_re["AdvCust_YoY"] = _g(df_re["AdvCust_P0"], df_re["AdvCust_P4"])
df_re["AdvCust_QoQ"] = _g(df_re["AdvCust_P0"], df_re["AdvCust_P1"])

# ─── 3. Standard transforms ────────────────────────────────────────────────────
_np_r = df_re["NP_R"].fillna(0)
_mult = np.where(_np_r >= 0, 1.0, np.clip(1 + 2 * _np_r, 0.0, 1.0))
df_re["DY_adj"]  = df_re["DY"] * _mult
df_re["DY_sust"] = _mult

NP_COLS  = [f"NP_P{i}"      for i in range(8)]
REV_COLS = [f"Revenue_P{i}" for i in range(8)]
np_arr  = df_re[NP_COLS].values.astype(float)
rev_arr = df_re[REV_COLS].values.astype(float)
np_n  = np.sum(~np.isnan(np_arr),  axis=1)
rev_n = np.sum(~np.isnan(rev_arr), axis=1)
with np.errstate(divide="ignore", invalid="ignore"):
    np_mean  = np.nanmean(np_arr,  axis=1)
    np_std   = np.nanstd(np_arr,   axis=1, ddof=1)
    rev_mean = np.nanmean(rev_arr, axis=1)
    rev_std  = np.nanstd(rev_arr,  axis=1, ddof=1)
    df_re["NP_CV"]  = np.where(np_n  >= 6, np_std  / np.maximum(np.abs(np_mean),  1e6), np.nan)
    df_re["Rev_CV"] = np.where(rev_n >= 6, rev_std / np.maximum(np.abs(rev_mean), 1e6), np.nan)
    df_re["NP_CV"]  = df_re["NP_CV"].clip(upper=10)
    df_re["Rev_CV"] = df_re["Rev_CV"].clip(upper=10)
rev_p0 = df_re["Revenue_P0"].values; rev_p7 = df_re["Revenue_P7"].values
mask = (rev_p0 > 0) & (rev_p7 > 0)
df_re["LT_CAGR"] = np.where(mask, (rev_p0 / rev_p7) ** (4/7) - 1, np.nan)
df_re["LT_CAGR"] = df_re["LT_CAGR"].clip(lower=-0.95, upper=5.0)
df_re["growth_yield"] = df_re["growth_yield"].clip(lower=-0.15, upper=0.15)

# Industry-relative valuation (within RE cohort × quarter)
for col in ["PE","PB","PCF"]:
    grp = df_re.groupby("quarter")[col]
    med = grp.transform("median"); sd = grp.transform("std")
    df_re[f"{col}_ind_z"] = (df_re[col] - med) / sd.replace(0, np.nan)

# Invert lower-is-better
for c in ["Debt_Eq_P0","PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","NP_CV","Rev_CV"]:
    df_re[c] = -df_re[c]

# ─── 4. v9 axes with new indicators ────────────────────────────────────────────
AXIS_COLS = {
    "quality":     ["ROIC5Y","ROE_Min5Y","FSCORE"],
    "stability":   ["NP_CV","Rev_CV","LT_CAGR"],
    "cash":        ["CF_OA_5Y","CFOA_NP","RevCoverage"],
    "shareholder": ["DY_adj","Dividend_Min3Y","FCF_OA_ratio","DY_sust"],
    "growth":      ["NP_R","Revenue_YoY_P0","GPM_change","NP_peak_ratio","Rev_peak_ratio",
                    "AdvCust_YoY","AdvCust_QoQ"],
    "health":      ["Debt_Eq_P0","IntCov_P0","CashR_P0"],
    "valuation":   ["PE_self_z","PB_self_z","PE_ind_z","PB_ind_z","PCF_ind_z","growth_yield"],
}
for cols in AXIS_COLS.values():
    for c in cols:
        df_re[f"r_{c}"] = df_re.groupby("quarter")[c].rank(pct=True, na_option="keep")
for axis, cols in AXIS_COLS.items():
    df_re[f"score_{axis}"] = df_re[[f"r_{c}" for c in cols]].mean(axis=1, skipna=True)

score_cols = [f"score_{a}" for a in WEIGHTS_RE_V9]
weights = np.array([WEIGHTS_RE_V9[a] for a in WEIGHTS_RE_V9])
df_re["total_score"] = (df_re[score_cols].values * weights).sum(axis=1)
df_re = df_re.dropna(subset=score_cols, how="any").copy()
print(f"  {len(df_re):,} RE rows with full axis coverage")
df_re["score_pct"] = df_re.groupby("quarter")["total_score"].rank(pct=True)
def tier_of(p):
    for n, lo, hi in TIERS:
        if lo <= p <= hi: return n
    return "E"
df_re["tier"] = df_re["score_pct"].apply(tier_of)

# Subset to fa_ratings schema
FA_COLS = ["ticker","quarter","time","trading_value_1M","ICB_Code",
           "score_quality","score_stability","score_cash","score_shareholder",
           "score_growth","score_health","score_valuation","total_score","score_pct","tier",
           "profit_3M","NP_CV","Rev_CV","LT_CAGR","DY","DY_adj","DY_sust",
           "Dividend_Min3Y","FCF_OA_ratio","NP_R","Revenue_YoY_P0","NP_peak_ratio","Rev_peak_ratio"]
df_re_out = df_re[FA_COLS].copy()
print(f"  RE rows ready: {len(df_re_out):,}")

# ─── 5. Pull non-RE rows directly from existing fa_ratings ─────────────────────
print("\nPulling non-RE rows from existing fa_ratings ...")
df_nonre = bq_query(f"""
SELECT {','.join(FA_COLS)}
FROM `lithe-record-440915-m9.tav2_bq.fa_ratings`
WHERE ICB_Code IS NULL OR ICB_Code != {ICB_RE}
""", "nonre_pull")
print(f"  {len(df_nonre):,} non-RE rows")

# ─── 6. Concat → save CSV ──────────────────────────────────────────────────────
final = pd.concat([df_re_out, df_nonre], ignore_index=True)
final = final.sort_values(["time","ticker"], ascending=[False, True])
print(f"\n  Total fa_ratings_v9: {len(final):,} rows ({len(df_re_out):,} RE + {len(df_nonre):,} non-RE)")
out_csv = "fa_ratings_v9.csv"
final.to_csv(out_csv, index=False)
print(f"  Saved {out_csv}")

# Sanity: RE tier distribution
print("\n  RE tier distribution in v9:")
print(df_re_out["tier"].value_counts().reindex(["A","B","C","D","E"]).to_string())

# ─── 7. Upload to BQ ───────────────────────────────────────────────────────────
print("\nUploading to tav2_bq.fa_ratings_v9 ...")
schema = ("ticker:STRING,quarter:STRING,time:DATE,trading_value_1M:FLOAT,ICB_Code:FLOAT,"
          "score_quality:FLOAT,score_stability:FLOAT,score_cash:FLOAT,score_shareholder:FLOAT,"
          "score_growth:FLOAT,score_health:FLOAT,score_valuation:FLOAT,total_score:FLOAT,"
          "score_pct:FLOAT,tier:STRING,profit_3M:FLOAT,NP_CV:FLOAT,Rev_CV:FLOAT,LT_CAGR:FLOAT,"
          "DY:FLOAT,DY_adj:FLOAT,DY_sust:FLOAT,Dividend_Min3Y:FLOAT,FCF_OA_ratio:FLOAT,"
          "NP_R:FLOAT,Revenue_YoY_P0:FLOAT,NP_peak_ratio:FLOAT,Rev_peak_ratio:FLOAT")
cmd = (f'"{BQ_BIN}" load --replace --source_format=CSV --skip_leading_rows=1 '
       f'--schema="{schema}" {PROJECT}:tav2_bq.fa_ratings_v9 "{out_csv}"')
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print(r.stdout); print(r.stderr)
if r.returncode == 0:
    print("\n  Upload OK. fa_ratings_v9 ready.")
else:
    print(f"\n  Upload FAILED (code {r.returncode})")
