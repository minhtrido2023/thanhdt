#!/usr/bin/env python3
"""
test_fa_kcn_diagnose.py
=======================
Deep diagnosis of KCN sub-sector:
  1. KCN sector base rate (% positive quarters, by year)
  2. Multi-horizon test for V4 schema (3M / 6M / 1Y / 2Y)
  3. Time-decomposition (which years drove negative A returns)
  4. Sub-cycle analysis (KCN behavior by market regime)

Goal: confirm whether long-horizon makes KCN A positive.
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
TIERS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

KCN_TICKERS = {"SIP","KBC","IDC","NTC","TIP","BCM","SZB","SZC","LHG","SZL","D2D","IDV","BAX",
               "ITA","SNZ","VRG","VGC","HPI","MH3","SZG","TID","TIX","LHC","DXP"}

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(f"{r.stdout[:300]}|{r.stderr[:300]}")
    return pd.read_csv(StringIO(r.stdout.strip()))

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 10: return float("nan"), 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# Pull KCN + full universe baseline for comparison; include O6M/O1Y/O2Y
ticker_filter = ",".join([f'"{t}"' for t in sorted(KCN_TICKERS)])
SQL = f"""
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROIC5Y, f.ROE_Min5Y, f.ROE_Trailing,
    f.NP_R, f.Revenue_P0,
    SAFE_DIVIDE(f.GPM_P0 - f.GPM_P4, ABS(f.GPM_P4)) AS GPM_change,
    f.CF_OA_5Y, f.DY, f.Dividend_Min3Y,
    f.PE, f.PB, f.OShares,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    f.AdvCust_P0, f.AdvCust_P1, f.AdvCust_P2, f.AdvCust_P4,
    f.UnearnRev_P0,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3,
    f.Cash_P0,
    CASE WHEN GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7) > 0
         THEN SAFE_DIVIDE(f.NP_P0, GREATEST(f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7))
         ELSE NULL END AS NP_peak_ratio,
    t.Close, t.ICB_Code, t.profit_3M,
    tp.O6M, tp.O1Y, tp.O2Y,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker_prune` AS tp
    ON tp.ticker = t.ticker AND tp.time = t.time
  WHERE f.time >= "2014-01-01" AND f.quarter LIKE "%Q4"
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
    AND t.ticker IN ({ticker_filter})
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""

print("Fetching KCN data ..."); df = bq_query(SQL); print(f"  {len(df):,} rows")
df["year"] = pd.to_datetime(df["time"]).dt.year

# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSIS 1: KCN sector base rate (yearly)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("DIAG 1: KCN sector base rate by year — profit_3M"); print("="*80)
print(f"\n{'Year':<6}{'N':>5}{'Mean':>9}{'Median':>10}{'WR':>8}{'Min':>9}{'Max':>9}")
for y in sorted(df["year"].unique()):
    sub = df[df["year"]==y].dropna(subset=["profit_3M"])
    if len(sub) == 0: continue
    p = sub["profit_3M"]
    print(f"{y:<6}{len(p):>5}{p.mean():>+8.2f}%{p.median():>+9.2f}%{(p>0).mean()*100:>+7.1f}%{p.min():>+8.2f}%{p.max():>+8.2f}%")

# All-time stats
print(f"\n  KCN all-time (N={len(df)}):")
p_all = df["profit_3M"].dropna()
print(f"    Mean: {p_all.mean():+.2f}%   Median: {p_all.median():+.2f}%   WR: {(p_all>0).mean()*100:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSIS 2: Multi-horizon comparison
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("DIAG 2: KCN base rate at different horizons"); print("="*80)
for h in ["profit_3M","O6M","O1Y","O2Y"]:
    p = df[h].dropna()
    if h.startswith("O"):
        # convert ratio to %
        p_pct = (p - 1) * 100
    else:
        p_pct = p
    print(f"  {h:<12}  N={len(p):4d}  mean={p_pct.mean():+6.2f}%  median={p_pct.median():+6.2f}%  WR={(p>0 if h.startswith('profit') else p>1).mean()*100:5.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSIS 3: Build V4 schema + test at multi-horizon
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("DIAG 3: V4 schema multi-horizon tier ordering"); print("="*80)

# Build indicators (subset for V4)
df["MktCap"] = df["Close"] * df["OShares"]
df["NP_4Q_mean"] = df[[f"NP_P{i}" for i in range(4)]].mean(axis=1, skipna=True)
df["smoothed_EY"] = (df["NP_4Q_mean"] / df["OShares"].replace(0,np.nan) / df["Close"].replace(0,np.nan)).clip(-1,1)
df["BY"] = np.where(df["PB"]>0, 1.0/df["PB"], np.nan)
df["FCF_4Q"] = df["CF_OA_P0"] + df["CF_OA_P1"] + df["CF_OA_P2"] + df["CF_OA_P3"]
df["FCF_yield"] = (df["FCF_4Q"] / df["MktCap"]).clip(-1, 1)
df["Cash_MktCap"] = np.where(df["MktCap"]>0, df["Cash_P0"]/df["MktCap"], np.nan).clip(-1,5)
def sd(num, den):
    return np.where(np.abs(den)>1e-3, num / den.replace(0,np.nan), np.nan)
df["AdvCust_MktCap_yld"] = sd(df["AdvCust_P0"], df["MktCap"]).clip(-1, 20)
df["AdvCust_QoQ"] = sd(df["AdvCust_P0"]-df["AdvCust_P1"], df["AdvCust_P1"].abs()).clip(-5, 20)
df["AdvCust_QoQ_prev"] = sd(df["AdvCust_P1"]-df["AdvCust_P2"], df["AdvCust_P2"].abs()).clip(-5, 20)
df["AdvCust_accel"] = df["AdvCust_QoQ"] - df["AdvCust_QoQ_prev"]
df["AdvCust_accel_inv"] = -df["AdvCust_accel"]
df["NP_peak_inv"] = -df["NP_peak_ratio"]

np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
np_n = np.sum(~np.isnan(np_arr),axis=1)
with np.errstate(divide="ignore",invalid="ignore"):
    np_m = np.nanmean(np_arr,axis=1); np_s = np.nanstd(np_arr,axis=1,ddof=1)
    df["NP_CV"] = -np.where(np_n>=6, np_s/np.maximum(np.abs(np_m),1e6), np.nan).clip(max=10)

RANK_COLS = ["ROIC5Y","ROE_Min5Y","ROE_Trailing","NP_CV","CF_OA_5Y","Cash_MktCap","DY","Dividend_Min3Y",
             "smoothed_EY","BY","FCF_yield","AdvCust_MktCap_yld","AdvCust_accel","AdvCust_accel_inv","NP_peak_inv"]
for c in RANK_COLS:
    df[f"r_{c}"] = df.groupby("quarter")[c].rank(pct=True, na_option="keep")

# V4 schema
V4 = {
    "quality":     (["r_ROE_Min5Y","r_ROIC5Y"], 0.20),
    "stability":   (["r_NP_CV"], 0.10),
    "shareholder": (["r_DY","r_Dividend_Min3Y"], 0.10),
    "valuation":   (["r_AdvCust_MktCap_yld","r_smoothed_EY","r_BY"], 0.40),
    "anti_mom":    (["r_AdvCust_accel_inv","r_NP_peak_inv"], 0.15),
    "cash":        (["r_FCF_yield"], 0.05),
}

def score(df_local, schema):
    weights_sum = sum(w for _, w in schema.values())
    total = np.zeros(len(df_local))
    nan_mask = np.zeros(len(df_local), dtype=bool)
    for axis, (rank_cols, w) in schema.items():
        axis_score = df_local[rank_cols].mean(axis=1, skipna=True).values
        nan_mask |= np.isnan(axis_score)
        total += np.nan_to_num(axis_score, nan=0.0) * w
    return np.where(nan_mask, np.nan, total / weights_sum)

def tier_of(p):
    for n,lo,hi in TIERS:
        if lo<=p<=hi: return n
    return "E"

df["s_v4"] = score(df, V4)
s = df.dropna(subset=["s_v4"]).copy()
s["pct"] = s.groupby("quarter")["s_v4"].rank(pct=True)
s["tier"] = s["pct"].apply(tier_of)

# Multi-horizon tier ordering
print(f"\n{'Horizon':<12}{'Tier':<6}{'N':>5}{'Median':>10}{'Mean':>10}{'WR':>8}")
for h in ["profit_3M","O6M","O1Y","O2Y"]:
    v = s.dropna(subset=[h])
    print(f"\n--- {h} (N={len(v)}) ---")
    for tier in ["A","B","C","D","E"]:
        g = v[v["tier"]==tier][h]
        if len(g):
            if h.startswith("O"):
                med = (g.median() - 1) * 100
                mean = (g.mean() - 1) * 100
                wr = (g>1).mean() * 100
            else:
                med = g.median(); mean = g.mean(); wr = (g>0).mean()*100
            print(f"  {tier:<6}{len(g):>5}{med:>+9.2f}%{mean:>+9.2f}%{wr:>+7.1f}%")

# IC at each horizon
print("\n" + "="*60); print("V4 schema IC at each horizon"); print("="*60)
for h in ["profit_3M","O6M","O1Y","O2Y"]:
    sub_h = s.dropna(subset=[h])
    rho, n = spearman_ic(sub_h["s_v4"], sub_h[h])
    print(f"  {h:<12}  IC={rho:+.4f}  N={n}")

# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSIS 4: Time decomposition — A tier returns by year
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*80); print("DIAG 4: V4 A-tier returns by year"); print("="*80)
A = s[s["tier"]=="A"].copy()
A["year"] = pd.to_datetime(A["time"]).dt.year
print(f"\n{'Year':<6}{'A_n':>5}{'A_med_3M':>12}{'A_WR_3M':>10}  Tickers")
for y in sorted(A["year"].unique()):
    sub = A[A["year"]==y]
    p = sub["profit_3M"].dropna()
    if len(p) == 0: continue
    tks = ",".join(sub["ticker"].unique())
    print(f"{y:<6}{len(sub):>5}{p.median():>+11.2f}%{(p>0).mean()*100:>+9.1f}%  {tks}")

# Combined long-period (2014-2019 vs 2020-2025)
A19 = A[A["year"]<=2019]; A20 = A[A["year"]>=2020]
print(f"\n  Period split:")
for label, sub in [("2014-2019", A19), ("2020-2025", A20)]:
    p = sub["profit_3M"].dropna()
    if len(p):
        print(f"    {label}: N={len(p)}, median {p.median():+.2f}%, mean {p.mean():+.2f}%, WR {(p>0).mean()*100:.1f}%")

print("\n" + "="*80); print("DONE"); print("="*80)
