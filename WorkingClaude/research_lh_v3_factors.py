#!/usr/bin/env python3
"""
research_lh_v3_factors.py
=========================
Multi-factor IC analysis for LH v3 design.

Tests 30+ factors across Quality, Value, Momentum, LowVol, Growth, Shareholder, Health, VN-specific.
Outputs:
  1) Individual factor IC at 3M/6M/1Y/2Y forward returns
  2) Composite scores (4-5 candidates)
  3) Top decile of each composite — forward return analysis
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

# ─── PULL COMPREHENSIVE FACTOR DATA ──────────────────────────────────────
print("Pulling comprehensive factor panel ...")
SQL = """
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    -- Quality
    f.ROIC_Trailing, f.ROIC5Y, f.ROE_Trailing, f.ROE_Min5Y,
    f.FSCORE, f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
    f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3, f.Revenue_P4, f.Revenue_P7,
    f.GPM_P0, f.GPM_P4,
    f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3, f.CF_OA_5Y,
    f.CF_Invest_P0, f.CF_Invest_P1, f.CF_Invest_P2, f.CF_Invest_P3,
    -- Value
    f.PE, f.PE_MA5Y, f.PE_SD5Y, f.PB, f.PCF, f.EVEB,
    -- Health
    f.StDebt_P0, f.LtDebt_P0, f.Cash_P0, f.EBITDA_P0, f.IntCov_P0,
    -- Shareholder
    f.DY, f.Dividend_Min3Y,
    -- VN-specific
    f.AdvCust_P0, f.UnearnRev_P0,
    f.OShares,
    -- Price & meta
    t.Close, t.ICB_Code, t.Volume_3M_P50,
    -- Forward returns
    tp.O3M, tp.O6M, tp.O1Y, tp.O2Y,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sector,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = f.ticker AND t.time <= f.time AND t.time >= DATE_SUB(f.time, INTERVAL 90 DAY)
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker_prune` AS tp
    ON tp.ticker = t.ticker AND tp.time = t.time
  WHERE f.time >= '2014-01-01'
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50 * t.Close >= 1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn = 1
"""
df = bq_query(SQL)
df["time"] = pd.to_datetime(df["time"])
print(f"  {len(df):,} (ticker,quarter) rows, {df['ticker'].nunique()} tickers")
df["MktCap"] = df["Close"] * df["OShares"]
df = df.sort_values(["ticker","time"]).reset_index(drop=True)

# ─── BUILD FACTOR LIBRARY ────────────────────────────────────────────────
print("\nBuilding factor library ...")

# Convert forward returns
for c in ["O3M","O6M","O1Y","O2Y"]:
    df[f"{c}_ret"] = (df[c] - 1) * 100

# === QUALITY ===
df["F_ROIC_trail"]    = df["ROIC_Trailing"]
df["F_ROIC5Y"]        = df["ROIC5Y"]
df["F_ROE_min5Y"]     = df["ROE_Min5Y"]
df["F_ROE_trail"]     = df["ROE_Trailing"]
df["F_FSCORE"]        = df["FSCORE"]

np_arr = df[[f"NP_P{i}" for i in range(8)]].values.astype(float)
rev_arr = df[[f"Revenue_P{i}" for i in range(4)]].values.astype(float)
with np.errstate(divide="ignore", invalid="ignore"):
    np_m = np.nanmean(np_arr, axis=1); np_s = np.nanstd(np_arr, axis=1, ddof=1)
    rev_m = np.nanmean(rev_arr, axis=1); rev_s = np.nanstd(rev_arr, axis=1, ddof=1)
    df["F_NP_stability"]  = -np.where(np.sum(~np.isnan(np_arr),axis=1) >= 6, np_s/np.maximum(np.abs(np_m), 1e6), np.nan).clip(max=10)
    df["F_Rev_stability"] = -np.where(np.sum(~np.isnan(rev_arr),axis=1) >= 3, rev_s/np.maximum(np.abs(rev_m), 1e6), np.nan).clip(max=10)

df["F_GPM_change"] = df["GPM_P0"] - df["GPM_P4"]
df["F_CFOA_NP"]    = np.where(df["NP_P0"].abs() > 1e6, df["CF_OA_P0"] / df["NP_P0"].abs(), np.nan).clip(-5, 5)

# Cash quality: 4Q CF_OA / 4Q NP
df["NP_4Q"] = df[[f"NP_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
df["CF_4Q"] = df[[f"CF_OA_P{i}" for i in range(4)]].sum(axis=1, skipna=False)
df["F_CFOA_NP_4Q"] = np.where(df["NP_4Q"].abs() > 1e6, df["CF_4Q"] / df["NP_4Q"].abs(), np.nan).clip(-5, 5)

# === VALUE ===
df["F_smoothed_EY"] = np.where((df["NP_4Q"]/4 > 0) & (df["MktCap"] > 0),
                                 (df["NP_4Q"]/4) / df["MktCap"] * 4, np.nan).clip(-1, 1)
df["F_EY"]   = np.where(df["PE"] > 0, 1.0/df["PE"], np.nan)
df["F_BY"]   = np.where(df["PB"] > 0, 1.0/df["PB"], np.nan)
df["F_CFY"]  = np.where(df["PCF"] > 0, 1.0/df["PCF"], np.nan)
df["F_EVEB_inv"] = np.where(df["EVEB"] > 0, 1.0/df["EVEB"], np.nan)

df["FCF_4Q"] = df[[f"CF_OA_P{i}" for i in range(4)]].sum(axis=1, skipna=True) + \
                df[[f"CF_Invest_P{i}" for i in range(4)]].sum(axis=1, skipna=True)
df["F_FCF_yield"] = np.where(df["MktCap"] > 0, df["FCF_4Q"] / df["MktCap"], np.nan).clip(-1, 1)

df["F_PE_z"] = np.where(df["PE_SD5Y"] > 0, -(df["PE"] - df["PE_MA5Y"]) / df["PE_SD5Y"], np.nan).clip(-10, 10)

# Magic formula: avg(rank(ROIC), rank(EY)) within quarter
df["F_magic"] = (df.groupby("quarter")["F_ROIC_trail"].rank(pct=True) +
                 df.groupby("quarter")["F_EY"].rank(pct=True)) / 2

# === GROWTH ===
df["F_NP_TTM_growth"] = np.where(df[["NP_P4","NP_P5","NP_P6","NP_P7"]].sum(axis=1, skipna=False).abs() > 0,
                                   (df["NP_4Q"] / df[["NP_P4","NP_P5","NP_P6","NP_P7"]].sum(axis=1, skipna=False).abs() - 1), np.nan).clip(-5, 5)
df["F_Rev_yoy"]       = np.where(df["Revenue_P4"].abs() > 0, df["Revenue_P0"] / df["Revenue_P4"].abs() - 1, np.nan).clip(-5, 5)
df["F_LT_CAGR"]       = np.where((df["Revenue_P0"] > 0) & (df["Revenue_P7"] > 0),
                                    (df["Revenue_P0"]/df["Revenue_P7"]) ** (4/7) - 1, np.nan).clip(-0.95, 5.0)

# Peak detection (smaller = past peak)
np_max = np.nanmax(np_arr, axis=1)
df["F_NP_peak_ratio"] = np.where(np_max > 0, df["NP_P0"] / np_max, np.nan)
df["F_NP_peak_ratio_inv"] = 1 - df["F_NP_peak_ratio"]  # smaller=better hidden value

# === SHAREHOLDER ===
df["F_DY"]            = df["DY"]
df["F_Div_Min3Y"]     = df["Dividend_Min3Y"]
# DY_sust: penalize if NP declining
np_r = df["F_NP_TTM_growth"].fillna(0)
df["F_DY_sust"]       = df["DY"] * np.clip(1 + 2*np_r, 0.0, 1.0)

# === HEALTH ===
df["TotalDebt"] = df["StDebt_P0"].fillna(0) + df["LtDebt_P0"].fillna(0)
df["NetDebt"] = df["TotalDebt"] - df["Cash_P0"].fillna(0)
df["F_NetDebt_EBITDA_inv"] = -np.where(df["EBITDA_P0"] > 0, df["NetDebt"]/df["EBITDA_P0"], np.nan).clip(-20, 50)
df["F_IntCov"]              = df["IntCov_P0"].clip(-100, 100)
df["F_Cash_MktCap"]         = np.where(df["MktCap"] > 0, df["Cash_P0"] / df["MktCap"], np.nan).clip(0, 5)
df["F_NetDebt_MktCap_inv"]  = -df["NetDebt"] / df["MktCap"].replace(0, np.nan)  # cash-rich = positive

# === VN-SPECIFIC ===
df["F_AdvCust_yld"]   = np.where(df["MktCap"] > 0, df["AdvCust_P0"] / df["MktCap"], np.nan).clip(-1, 10)
df["F_Backlog_yld"]   = np.where(df["MktCap"] > 0,
                                   (df["AdvCust_P0"].fillna(0) + df["UnearnRev_P0"].fillna(0)) / df["MktCap"], np.nan).clip(-1, 10)

# Sector leader: top 3 by mcap within (quarter, sector)
df["sector_mcap_rank"] = df.groupby(["quarter","sector"])["MktCap"].rank(ascending=False)
df["F_sector_leader"]  = (df["sector_mcap_rank"] <= 3).astype(int)

# Liquidity decile
df["F_liq_decile"] = df.groupby("quarter")["Volume_3M_P50"].transform(lambda x: x.rank(pct=True))

# === MOMENTUM (from prices) ===
print("Computing momentum factors from prices ...")
prices = pd.read_csv("data/prices_lh.csv", parse_dates=["time"])
px_close = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
ma200 = px_close.rolling(200, min_periods=100).mean()
ret_12m = px_close.pct_change(252)
ret_6m  = px_close.pct_change(125)
ret_3m  = px_close.pct_change(63)
ret_1m  = px_close.pct_change(21)
vol_120d = px_close.pct_change().rolling(120, min_periods=60).std() * np.sqrt(252)

# 52w high distance
hi_52w = px_close.rolling(252, min_periods=60).max()

def lookup(df_pivot, row):
    if row["ticker"] not in df_pivot.columns: return np.nan
    series = df_pivot[row["ticker"]]
    if row["time"] not in series.index:
        idx = series.index.searchsorted(row["time"])
        if idx == 0 or idx >= len(series): return np.nan
        return series.iloc[idx-1]
    return series.loc[row["time"]]

# Use asof for speed
def asof_lookup(df_pivot, df_main, col_name):
    df_main = df_main.sort_values("time")
    res = []
    for tk, g in df_main.groupby("ticker"):
        if tk not in df_pivot.columns:
            res.append(pd.Series([np.nan]*len(g), index=g.index, name=col_name))
            continue
        series = df_pivot[tk].dropna()
        if len(series) == 0:
            res.append(pd.Series([np.nan]*len(g), index=g.index, name=col_name))
            continue
        # reindex with asof: for each row's time, find latest series ≤ time
        merged = pd.merge_asof(g[["time"]].sort_values("time"), series.reset_index().rename(columns={tk:col_name}),
                                on="time", direction="backward")
        merged.index = g.index
        res.append(merged[col_name])
    return pd.concat(res).reindex(df_main.index)

df["F_ret_12m"]  = asof_lookup(ret_12m,  df, "F_ret_12m")
df["F_ret_6m"]   = asof_lookup(ret_6m,   df, "F_ret_6m")
df["F_ret_3m"]   = asof_lookup(ret_3m,   df, "F_ret_3m")
df["F_ret_1m"]   = asof_lookup(ret_1m,   df, "F_ret_1m")
df["F_ret_12_1"] = df["F_ret_12m"] - df["F_ret_1m"]  # 12-1 momentum (skip recent)
df["F_ret_6_3"]  = df["F_ret_6m"] - df["F_ret_3m"]   # 6-3 medium momentum
df["F_vol_120d_inv"] = -asof_lookup(vol_120d, df, "F_vol_120d_inv")
_h52 = asof_lookup(hi_52w, df, "_h52")
_m200 = asof_lookup(ma200, df, "_m200")
df["F_dist_52w_high"] = df["Close"].values / _h52.values
df["F_above_MA200"] = (df["Close"].values >= _m200.values).astype(int)

# ─── IC ANALYSIS ─────────────────────────────────────────────────────────
def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 100: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

# All factors
FACTORS = [c for c in df.columns if c.startswith("F_")]
print(f"\nTotal factors built: {len(FACTORS)}")

print("\n" + "="*120)
print(f"  INDIVIDUAL FACTOR IC (Spearman) — sorted by |IC at 1Y|")
print("="*120)

ic_rows = []
for f in FACTORS:
    row = {"factor":f}
    for hzn in ["O3M_ret","O6M_ret","O1Y_ret","O2Y_ret"]:
        ic, n = spearman_ic(df[f], df[hzn])
        row[hzn] = ic
        row[f"n_{hzn}"] = n
    ic_rows.append(row)
ic_df = pd.DataFrame(ic_rows).sort_values("O1Y_ret", key=lambda s: s.abs(), ascending=False)
print(f"\n  {'factor':<25}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'N (at 1Y)':>12}")
for _, r in ic_df.iterrows():
    print(f"  {r['factor']:<25}{r['O3M_ret']:>+8.4f}{r['O6M_ret']:>+8.4f}{r['O1Y_ret']:>+8.4f}{r['O2Y_ret']:>+8.4f}{int(r['n_O1Y_ret']):>12}")

ic_df.to_csv("data/lh_v3_factor_ic.csv", index=False)

# ─── COMPOSITE SCORES ────────────────────────────────────────────────────
print("\n" + "="*120)
print("  COMPOSITE SCORE CANDIDATES")
print("="*120)

# Helper: rank within quarter
def rank_pct(df, factors):
    out = pd.DataFrame(index=df.index)
    for f in factors:
        out[f] = df.groupby("quarter")[f].rank(pct=True, na_option="keep")
    return out

# Composite 1: Classic Quality + Value + Momentum (QVM)
QVM_W = {
    "F_ROIC5Y": 0.10, "F_ROE_min5Y": 0.10, "F_NP_stability": 0.05, "F_CFOA_NP_4Q": 0.05,  # Quality 30%
    "F_smoothed_EY": 0.10, "F_FCF_yield": 0.10, "F_BY": 0.05, "F_magic": 0.05,  # Value 30%
    "F_ret_12_1": 0.15, "F_above_MA200": 0.10,  # Momentum 25%
    "F_vol_120d_inv": 0.10,  # LowVol 10%
    "F_DY_sust": 0.05,  # Shareholder bonus 5%
}

# Composite 2: Quality-tilted (defensive)
QUALITY_TILT_W = {
    "F_ROIC5Y": 0.12, "F_ROE_min5Y": 0.12, "F_NP_stability": 0.08, "F_CFOA_NP_4Q": 0.08,  # Quality 40%
    "F_smoothed_EY": 0.10, "F_FCF_yield": 0.10, "F_BY": 0.05,  # Value 25%
    "F_ret_12_1": 0.10, "F_above_MA200": 0.05,  # Momentum 15%
    "F_vol_120d_inv": 0.10, "F_NetDebt_EBITDA_inv": 0.10,  # LowVol/Health 20%
}

# Composite 3: Pre-sales aware (VN-specific for RE/KCN)
PRESALES_W = {
    "F_ROIC5Y": 0.10, "F_ROE_min5Y": 0.10, "F_NP_stability": 0.05,  # Quality 25%
    "F_smoothed_EY": 0.10, "F_BY": 0.05, "F_FCF_yield": 0.05,  # Value 20%
    "F_AdvCust_yld": 0.10, "F_Backlog_yld": 0.10,  # Pre-sales 20%
    "F_ret_12_1": 0.10, "F_above_MA200": 0.05,  # Momentum 15%
    "F_DY_sust": 0.05, "F_vol_120d_inv": 0.10,  # 15% defensive
    "F_NetDebt_EBITDA_inv": 0.05,
}

# Composite 4: Pure Momentum (chase trends)
MOMENTUM_W = {
    "F_ret_12_1": 0.25, "F_ret_6_3": 0.15, "F_above_MA200": 0.15, "F_dist_52w_high": 0.10,  # Mom 65%
    "F_ROIC5Y": 0.10, "F_ROE_min5Y": 0.05,  # Quality light 15%
    "F_NP_TTM_growth": 0.10, "F_LT_CAGR": 0.05,  # Growth 15%
    "F_vol_120d_inv": 0.05,  # LowVol 5%
}

# Composite 5: Value-deep (cheap + safe)
VALUE_DEEP_W = {
    "F_smoothed_EY": 0.15, "F_FCF_yield": 0.10, "F_BY": 0.10, "F_magic": 0.10, "F_PE_z": 0.05,  # Value 50%
    "F_ROIC5Y": 0.10, "F_NP_stability": 0.05, "F_FSCORE": 0.05,  # Quality 20%
    "F_DY_sust": 0.05, "F_Div_Min3Y": 0.05,  # Shareholder 10%
    "F_NetDebt_EBITDA_inv": 0.10, "F_IntCov": 0.05,  # Health 15%
    "F_above_MA200": 0.05,  # Mom safety 5%
}

COMPOSITES = {
    "C1_QVM_classic":    QVM_W,
    "C2_quality_tilt":   QUALITY_TILT_W,
    "C3_presales_VN":    PRESALES_W,
    "C4_momentum_lead":  MOMENTUM_W,
    "C5_value_deep":     VALUE_DEEP_W,
}

# Validate weights
for name, w in COMPOSITES.items():
    total = sum(w.values())
    assert abs(total - 1.0) < 0.001, f"{name} weights sum {total} != 1.0"

# Compute composite scores
for name, w_dict in COMPOSITES.items():
    score_components = []
    weights = []
    for f, w in w_dict.items():
        if f not in df.columns:
            print(f"WARN: {f} not in df for {name}")
            continue
        rank_col = df.groupby("quarter")[f].rank(pct=True, na_option="keep")
        score_components.append(rank_col * w)
        weights.append(w)
    score = sum(score_components)
    # Normalize by sum of weights actually used
    df[name] = score / sum(weights) if weights else np.nan

# IC of composites
print("\n  Composite IC (Spearman):")
print(f"  {'Composite':<25}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}")
for name in COMPOSITES:
    row = [name]
    for hzn in ["O3M_ret","O6M_ret","O1Y_ret","O2Y_ret"]:
        ic, _ = spearman_ic(df[name], df[hzn])
        row.append(ic)
    print(f"  {row[0]:<25}{row[1]:>+8.4f}{row[2]:>+8.4f}{row[3]:>+8.4f}{row[4]:>+8.4f}")

# Compare to current FA score (v8c_final via fa_ratings_lh)
print("\n  Baseline FA v8c_final IC:")
fa = pd.read_csv("data/fa_ratings_lh.csv", usecols=["ticker","quarter","score"])
df = df.merge(fa, on=["ticker","quarter"], how="left", suffixes=("","_v8c"))
for hzn in ["O3M_ret","O6M_ret","O1Y_ret","O2Y_ret"]:
    ic, _ = spearman_ic(df["score"], df[hzn])
    print(f"    {hzn}: IC = {ic:+.4f}")

# ─── TOP DECILE FORWARD RETURN ───────────────────────────────────────────
print("\n" + "="*120)
print("  TOP DECILE FORWARD RETURN (each composite)")
print("="*120)
print(f"\n  {'Composite':<25}{'O1Y_ret_top10%':>16}{'O1Y_ret_full':>16}{'spread':>10}{'WR_top10':>12}{'big_loss%':>12}")
for name in list(COMPOSITES.keys()) + ["score"]:
    if name not in df.columns: continue
    df_v = df.dropna(subset=[name, "O1Y_ret"])
    if len(df_v) < 100: continue
    df_v["decile"] = df_v.groupby("quarter")[name].rank(pct=True)
    top10 = df_v[df_v["decile"] >= 0.90]
    full_med = df_v["O1Y_ret"].median()
    top_med = top10["O1Y_ret"].median()
    spread = top_med - full_med
    wr = (top10["O1Y_ret"] > 0).mean() * 100
    big_loss = (top10["O1Y_ret"] < -20).mean() * 100
    label = name if name != "score" else "v8c_final (baseline)"
    print(f"  {label:<25}{top_med:>+15.2f}%{full_med:>+15.2f}%{spread:>+9.2f}pp{wr:>11.1f}%{big_loss:>11.1f}%")

# Save panel
df.to_csv("data/lh_v3_factor_panel.csv", index=False)
print(f"\nSaved: lh_v3_factor_ic.csv, lh_v3_factor_panel.csv")
print("DONE")
