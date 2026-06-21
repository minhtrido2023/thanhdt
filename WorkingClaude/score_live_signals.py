#!/usr/bin/env python3
"""
score_live_signals.py  (Phase 5)
=================================
Train entry quality model -> score current HOLD positions -> rank actionable deals.

Flow:
  1. Load profile_hit.csv
  2. Fetch BQ fundamentals for ALL tickers (closed + hold)
  3. Train RF model on closed deals (<=2024 train, 2025 test)
  4. Score all 3,386 HOLD (open) positions
  5. Per-strategy ranking + composite filter
  6. Output: live_scored.csv + score_live_signals.png
"""

import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, pickle
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_FILE   = "data/profile_hit.csv"
PROJECT     = "lithe-record-440915-m9"
BQ_BIN      = r"bq"
BQ_CHUNK    = 110
OUT_IMG     = "score_live_signals.png"
OUT_CSV     = "data/live_scored.csv"
MODEL_FILE  = "data/entry_quality_model.pkl"
TARGET_PCT  = 10.0
TRAIN_YEAR  = 2024
TODAY       = "2026-04-13"

DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"

plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

# ── BQ HELPER ─────────────────────────────────────────────────────────────────
def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql); tmppath = f.name
    try:
        cmd = (f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmppath)
        except: pass
    if r.returncode != 0:
        print(f"  [BQ ERROR] {label}: {(r.stdout or r.stderr)[:400]}")
        return None
    txt = r.stdout.strip()
    if not txt: return pd.DataFrame()
    try: return pd.read_csv(StringIO(txt))
    except: return pd.DataFrame()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
print("=" * 70)
print("PHASE 5 — Live Signal Scoring Pipeline")
print("=" * 70)
print(f"\nLoading {DATA_FILE} ...")
df = pd.read_csv(DATA_FILE)
df["time"] = pd.to_datetime(df["time"])
print(f"  Total signals: {len(df):,} | {df['ticker'].nunique()} tickers")

closed = df[df["Sell_filter"] != "Hold"].copy()
hold   = df[df["Sell_filter"] == "Hold"].copy()
print(f"  Closed deals : {len(closed):,} | WR(>10%): {(closed['Sell_profit']>TARGET_PCT).mean():.1%}")
print(f"  HOLD (active): {len(hold):,} | {hold['ticker'].nunique()} tickers | "
      f"{hold['time'].min().date()} -> {hold['time'].max().date()}")

# ── FETCH BQ FUNDAMENTALS ─────────────────────────────────────────────────────
FUND_COLS = """
    t.ticker, t.time,
    t.PE, t.PB, t.PCF,
    t.ROE5Y, t.ROE_Min3Y, t.ROE_Min5Y,
    t.ROIC5Y, t.ROIC_Min3Y,
    t.FSCORE,
    t.NP_P0, t.NP_P1, t.NP_P2, t.NP_P4,
    t.CF_OA_5Y, t.OShares,
    t.Risk_Rating,
    t.HI_3M_T1, t.LO_3M_T1,
    t.MA10, t.MA50, t.MA200,
    t.D_CMF, t.D_MACDdiff,
    t.C_L1W, t.Close_T1W,
    t.Volume_3M_P50, t.Volume_3M_P90,
    t.D_RSI_T1,
    t.Close, t.Open,
    t.Sup_1Y, t.Res_1Y, t.VAP1M, t.VAP3M,
    t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y,
    t.D_RSI, t.D_RSI_Max1W, t.D_RSI_Max3M, t.D_RSI_T1W,
    t.Volume, t.Volume_1M
"""

all_tickers = df["ticker"].unique().tolist()
date_min    = df["time"].min().strftime("%Y-%m-%d")
date_max    = df["time"].max().strftime("%Y-%m-%d")
n_chunks    = -(-len(all_tickers) // BQ_CHUNK)
print(f"\nFetching BQ fundamentals: {len(all_tickers)} tickers in {n_chunks} chunks ...")
print(f"  Date range: {date_min} -> {date_max}")

fund_frames = []
for i in range(0, len(all_tickers), BQ_CHUNK):
    chunk = all_tickers[i : i + BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (f"SELECT {FUND_COLS} FROM tav2_bq.ticker AS t "
             f"WHERE t.ticker IN ({tstr}) "
             f"AND t.time BETWEEN '{date_min}' AND '{date_max}' "
             f"ORDER BY t.ticker, t.time")
    res = bq_query(sql, f"chunk {i//BQ_CHUNK+1}")
    cn  = i // BQ_CHUNK + 1
    if res is not None and not res.empty:
        res["time"] = pd.to_datetime(res["time"])
        fund_frames.append(res)
        print(f"  [{cn}/{n_chunks}] {len(res):,} rows ok")
    else:
        print(f"  [{cn}/{n_chunks}] empty/error")

if not fund_frames:
    raise RuntimeError("No BQ data returned")
fund_df = pd.concat(fund_frames, ignore_index=True)
print(f"  Total BQ rows: {len(fund_df):,}")

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
def make_features(src, fund):
    """Merge src (profile_hit rows) with BQ fundamentals and engineer features."""
    m = src.merge(fund, on=["ticker","time"], how="left", suffixes=("","_bq"))

    # Use BQ Close if profile Close is missing
    close_col = "Close" if "Close" in m.columns else "Close_bq"

    # Valuation vs history
    m["pe_vs_hist"]    = m["PE"] / m["PE_MA5Y"].clip(lower=0.5)
    m["pb_vs_hist"]    = m["PB"] / m["PB_MA5Y"].clip(lower=0.1)
    m["pe_z_score"]    = (m["PE"] - m["PE_MA5Y"]) / m["PE_SD5Y"].clip(lower=0.1)
    m["pb_z_score"]    = (m["PB"] - m["PB_MA5Y"]) / m["PB_SD5Y"].clip(lower=0.01)

    # Earnings quality
    m["np_growth_1q"]  = m["NP_P0"] / m["NP_P1"].replace(0, np.nan)
    m["np_growth_1y"]  = m["NP_P0"] / m["NP_P4"].replace(0, np.nan)
    m["cf_yield"]      = (m["CF_OA_5Y"] / m["OShares"].clip(lower=1)
                          / m[close_col].clip(lower=1)) * 100

    # Trend
    m["price_vs_ma200"] = m[close_col] / m["MA200"].clip(lower=1)
    m["price_vs_ma50"]  = m[close_col] / m["MA50"].clip(lower=1)
    m["ma10_vs_ma200"]  = m["MA10"] / m["MA200"].clip(lower=1)

    # After merge: BQ columns that conflict with profile_hit get suffix "_bq"
    # D_RSI exists in both -> profile_hit="D_RSI", BQ="D_RSI_bq"
    # D_MACDdiff, D_CMF, D_RSI_T1W, D_RSI_Max1W, D_RSI_Max3M -> BQ only (no conflict)
    # D_MACD, D_MFI, D_MACD_T1W, D_MFI_T1W -> profile_hit only (not in BQ)
    # Volume, Volume_1M -> both -> profile_hit="Volume", BQ="Volume_bq"

    # Prefer profile_hit RSI where available (entry signal), fallback to BQ
    d_rsi_use     = m.get("D_RSI",      pd.Series(np.nan, index=m.index))
    d_rsi_bq      = m.get("D_RSI_bq",   pd.Series(np.nan, index=m.index))
    d_rsi_use     = d_rsi_use.fillna(d_rsi_bq)

    d_macd_use    = m.get("D_MACD",     pd.Series(np.nan, index=m.index))  # profile_hit only
    d_mfi_use     = m.get("D_MFI",      pd.Series(np.nan, index=m.index))  # profile_hit only
    d_rsi_t1w_use = m.get("D_RSI_T1W",  pd.Series(np.nan, index=m.index))  # profile_hit only; BQ has D_RSI_T1W too
    d_macd_t1w_use= m.get("D_MACD_T1W", pd.Series(np.nan, index=m.index))  # profile_hit only
    d_mfi_t1w_use = m.get("D_MFI_T1W",  pd.Series(np.nan, index=m.index))  # profile_hit only

    rsi_max1w = m.get("D_RSI_Max1W", pd.Series(np.nan, index=m.index))
    rsi_max3m = m.get("D_RSI_Max3M", pd.Series(np.nan, index=m.index))
    lo3m      = m.get("LO_3M_T1",    pd.Series(np.nan, index=m.index))
    vol       = m.get("Volume",       pd.Series(np.nan, index=m.index))
    vol1m     = m.get("Volume_1M",    pd.Series(np.nan, index=m.index))
    vol3m_p50 = m.get("Volume_3M_P50",pd.Series(np.nan, index=m.index))

    m["vol_ratio"]      = vol / vol1m.clip(lower=1)
    m["vol_vs_p50"]     = vol / vol3m_p50.clip(lower=1)
    m["close_vs_lo"]    = m[close_col] / lo3m.clip(lower=1)
    m["close_vs_vap1m"] = m[close_col] / m["VAP1M"].clip(lower=1)
    m["rsi_vs_max3m"]   = d_rsi_use / rsi_max3m.clip(lower=0.01)
    m["rsi_vs_max1w"]   = d_rsi_use / rsi_max1w.clip(lower=0.01)
    m["rsi_momentum"]   = d_rsi_use - d_rsi_t1w_use
    # macd_momentum: use D_MACDdiff from BQ (if merged) or D_MACD from profile_hit
    d_macdiff = m.get("D_MACDdiff", pd.Series(np.nan, index=m.index))
    m["macd_momentum"]  = d_macdiff.fillna(d_macd_use)
    m["volatility"]     = m["HI_3M_T1"] / lo3m.clip(lower=1)
    # Ensure D_RSI column uses combined value
    m["D_RSI"] = d_rsi_use

    # Strategy tier
    HIGH = {"RSILow30","BuySupport","BuySupport_special","VolMax1Y","VolMax1Y_special",
            "BullDvg_special","TrendingGrowth_special","AccSup","TL3M_special"}
    MED  = {"UnderBV","Conservative","SurpriseEarning","T3P4","TradingValueMax","BKMA200","TL3M",
            "TrendingGrowth","SuperGrowth","CashCowStock","DividendYield"}
    m["strat_tier"] = m["filter"].map(
        lambda f: 3 if f in HIGH else (2 if f in MED else 1))

    return m

print("\nEngineering features for training set ...")
train_merged = make_features(closed, fund_df)

# ── FEATURE LIST ──────────────────────────────────────────────────────────────
FEATURES = [
    # Fundamental
    "PE","PB","PCF","ROE5Y","ROE_Min3Y","ROE_Min5Y",
    "ROIC5Y","ROIC_Min3Y","FSCORE",
    "np_growth_1q","np_growth_1y","cf_yield",
    "pe_vs_hist","pb_vs_hist","pe_z_score","pb_z_score",
    "Risk_Rating",
    # Technical (D_RSI from profile_hit; D_MACDdiff, D_CMF from BQ)
    "D_RSI","D_MACDdiff","D_CMF",
    "D_RSI_Max3M","D_RSI_Max1W","D_RSI_T1W",
    "rsi_vs_max3m","rsi_vs_max1w","rsi_momentum",
    "macd_momentum",
    "vol_ratio","vol_vs_p50",
    "close_vs_lo","close_vs_vap1m","C_L1W","volatility",
    # Trend
    "price_vs_ma200","price_vs_ma50","ma10_vs_ma200",
    # Strategy
    "strat_tier",
]

train_merged["is_good"] = (train_merged["Sell_profit"] > TARGET_PCT).astype(int)
df_model = train_merged[FEATURES + ["is_good","Sell_profit","filter","time","ticker"]].copy()
df_model = df_model.replace([np.inf, -np.inf], np.nan).dropna()
print(f"  Model dataset: {len(df_model):,} rows after dropna")

# Train / val split
train_df = df_model[df_model["time"].dt.year <= TRAIN_YEAR]
val_df   = df_model[df_model["time"].dt.year >  TRAIN_YEAR]
print(f"  Train: {len(train_df):,} rows (WR={train_df['is_good'].mean():.1%}) "
      f"| Val2025: {len(val_df):,} rows (WR={val_df['is_good'].mean():.1%})")

# ── TRAIN MODEL ───────────────────────────────────────────────────────────────
print(f"\nTraining RandomForest (400 trees) ...")
rf = RandomForestClassifier(
    n_estimators=400, max_depth=10, min_samples_leaf=15,
    class_weight="balanced", random_state=42, n_jobs=-1)
rf.fit(train_df[FEATURES], train_df["is_good"])

auc_tr = roc_auc_score(train_df["is_good"], rf.predict_proba(train_df[FEATURES])[:,1])
auc_va = roc_auc_score(val_df["is_good"],   rf.predict_proba(val_df[FEATURES])[:,1])
print(f"  AUC train={auc_tr:.3f} | AUC val2025={auc_va:.3f}")

# Save model
with open(MODEL_FILE, "wb") as f:
    pickle.dump({"model": rf, "features": FEATURES, "target_pct": TARGET_PCT}, f)
print(f"  Model saved: {MODEL_FILE}")

feat_imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
print(f"\nTop 10 features:")
for fn, fv in feat_imp.head(10).items():
    print(f"  {fn:<22} {fv:.4f}")

# ── SCORE VAL 2025: THRESHOLD ANALYSIS ────────────────────────────────────────
print(f"\n--- Score Thresholds (val 2025, baseline WR={val_df['is_good'].mean():.1%}) ---")
val_df = val_df.copy()
val_df["score"] = rf.predict_proba(val_df[FEATURES])[:,1]
base_wr = val_df["is_good"].mean()
thr_data = []
for thr in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
    sub = val_df[val_df["score"] >= thr]
    if len(sub) < 20: continue
    wr  = sub["is_good"].mean()
    avg = sub["Sell_profit"].mean()
    med = sub["Sell_profit"].median()
    thr_data.append({"thr":thr,"n":len(sub),"pct":len(sub)/len(val_df),"wr":wr,"avg":avg,"med":med})
    print(f"  >={thr:.2f}  n={len(sub):>5}  {len(sub)/len(val_df):>4.0%}  "
          f"WR={wr:.1%}  lift={wr/base_wr-1:>+4.0%}  avg={avg:.1f}%  med={med:.1f}%")

# ── SCORE HOLD POSITIONS ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"SCORING {len(hold):,} ACTIVE HOLD POSITIONS ...")
print(f"{'='*60}")

hold_merged = make_features(hold, fund_df)
hold_model  = hold_merged[[f for f in FEATURES if f in hold_merged.columns]].copy()
# Add missing features
for f in FEATURES:
    if f not in hold_model.columns:
        hold_model[f] = np.nan
hold_model = hold_model[FEATURES].replace([np.inf,-np.inf], np.nan)

# Score (allow NaN by using estimator's predict for rows with missing data)
# Fill remaining NaN with median from training
fill_vals = train_df[FEATURES].median()
hold_filled = hold_model.fillna(fill_vals)
hold_merged["score"] = rf.predict_proba(hold_filled)[:,1]

# Add signals (use D_MACDdiff from BQ; fallback to D_MACD from profile_hit)
macd_signal = hold_merged.get("D_MACDdiff", pd.Series(np.nan, index=hold_merged.index))
macd_signal = macd_signal.fillna(hold_merged.get("D_MACD", pd.Series(np.nan, index=hold_merged.index)))
hold_merged["macd_pos"]     = macd_signal > 0
hold_merged["cmf_pos"]      = hold_merged.get("D_CMF",  pd.Series(np.nan, index=hold_merged.index)) > 0.05
hold_merged["rsi_ok"]       = hold_merged.get("D_RSI",  pd.Series(np.nan, index=hold_merged.index)) < 0.60
hold_merged["np_yoy_ok"]    = hold_merged.get("np_growth_1y", pd.Series(np.nan, index=hold_merged.index)) > 1.10
hold_merged["fscore_ok"]    = hold_merged.get("FSCORE",       pd.Series(np.nan, index=hold_merged.index)) > 4
hold_merged["roe_ok"]       = hold_merged.get("ROE_Min3Y",    pd.Series(np.nan, index=hold_merged.index)) > 0.06

# Composite flag
hold_merged["PASS_A"]  = (hold_merged["score"] >= 0.50)
hold_merged["PASS_B"]  = ((hold_merged["score"] >= 0.45) &
                           hold_merged["macd_pos"] & hold_merged["np_yoy_ok"])
hold_merged["PASS_C"]  = ((hold_merged["score"] >= 0.45) &
                           hold_merged["macd_pos"] & hold_merged["cmf_pos"] &
                           hold_merged["fscore_ok"])
hold_merged["grade"] = "D"
hold_merged.loc[hold_merged["PASS_B"] | hold_merged["PASS_C"], "grade"] = "C"
hold_merged.loc[hold_merged["PASS_A"], "grade"] = "B"
hold_merged.loc[hold_merged["PASS_A"] & hold_merged["np_yoy_ok"] & hold_merged["roe_ok"], "grade"] = "A"

# Keep latest signal per ticker per strategy
hold_ranked = (hold_merged.sort_values("time")
               .drop_duplicates(subset=["ticker","filter"], keep="last")
               .sort_values("score", ascending=False))

print(f"\nHold positions after dedup (latest per ticker+strategy): {len(hold_ranked):,}")
print(f"\nGrade distribution:")
for g in ["A","B","C","D"]:
    sub = hold_ranked[hold_ranked["grade"]==g]
    print(f"  Grade {g}: {len(sub):>4}  avg_score={sub['score'].mean():.3f}")

# ── PER-STRATEGY HOLD SUMMARY ─────────────────────────────────────────────────
print(f"\n--- Hold positions by strategy ---")
strat_hold = (hold_ranked.groupby("filter")
              .agg(n=("score","count"),
                   avg_score=("score","mean"),
                   pct_A=("grade", lambda x: (x=="A").mean()),
                   pct_AB=("grade", lambda x: x.isin(["A","B"]).mean()))
              .sort_values("avg_score", ascending=False))
print(strat_hold.round(3).to_string())

# ── TOP 30 PICKS ──────────────────────────────────────────────────────────────
print(f"\n--- TOP 30 HOLD positions (by model score) ---")
show_cols = ["filter","ticker","time","score","grade","D_RSI","D_MACDdiff","np_growth_1y",
             "FSCORE","ROE_Min3Y","pe_vs_hist","pb_vs_hist","strat_tier"]
avail = [c for c in show_cols if c in hold_ranked.columns]
top30 = hold_ranked.nlargest(30, "score")[avail]
print(top30.to_string(index=False))

# ── SAVE SCORED CSV ───────────────────────────────────────────────────────────
save_cols = ["filter","ticker","time","score","grade",
             "D_RSI","D_CMF","D_MACDdiff",
             "np_growth_1y","np_growth_1q","FSCORE",
             "ROE_Min3Y","ROE5Y","ROIC5Y","pe_vs_hist","pb_vs_hist",
             "PE","PB","Risk_Rating","strat_tier",
             "price_vs_ma200","rsi_vs_max3m","vol_vs_p50",
             "macd_pos","cmf_pos","np_yoy_ok","fscore_ok","roe_ok",
             "PASS_A","PASS_B","PASS_C"]
avail_save = [c for c in save_cols if c in hold_ranked.columns]
hold_ranked[avail_save].sort_values("score", ascending=False).to_csv(OUT_CSV, index=False)
print(f"\nScored CSV saved: {OUT_CSV} ({len(hold_ranked):,} positions)")

# ── ALSO QUERY BQ FOR LATEST DATE ────────────────────────────────────────────
print(f"\n{'='*60}")
print("Fetching latest BQ signals (last 5 trading days) ...")
print(f"{'='*60}")

sql_latest = f"""
SELECT
    t.ticker, t.time,
    t.Close, t.Open,
    t.D_RSI, t.D_MACDdiff, t.D_CMF,
    t.MA10, t.MA50, t.MA200,
    t.PE, t.PB, t.PCF,
    t.ROE5Y, t.ROE_Min3Y, t.ROIC5Y, t.ROIC_Min3Y, t.FSCORE,
    t.NP_P0, t.NP_P1, t.NP_P4,
    t.CF_OA_5Y, t.OShares,
    t.Risk_Rating,
    t.HI_3M_T1, t.LO_3M_T1,
    t.D_RSI_Max3M, t.D_RSI_Max1W, t.D_RSI_T1W,
    t.Volume, t.Volume_1M, t.Volume_3M_P50,
    t.C_L1W, t.VAP1M, t.VAP3M,
    t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y,
    t.Sup_1Y, t.Res_1Y,
    t.ICB_Code
FROM tav2_bq.ticker AS t
WHERE t.time >= DATE_SUB((SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2), INTERVAL 7 DAY)
  AND t.time <= (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2)
  AND t.D_RSI IS NOT NULL
ORDER BY t.ticker, t.time DESC
"""
latest_df = bq_query(sql_latest, "latest_date")
if latest_df is not None and not latest_df.empty:
    latest_df["time"] = pd.to_datetime(latest_df["time"])
    # Keep most recent row per ticker
    latest_df = latest_df.sort_values("time").groupby("ticker").last().reset_index()
    print(f"  Latest BQ data: {len(latest_df):,} tickers | most recent: {latest_df['time'].max().date()}")

    # Engineer features for scoring
    latest_df["pe_vs_hist"]    = latest_df["PE"] / latest_df["PE_MA5Y"].clip(lower=0.5)
    latest_df["pb_vs_hist"]    = latest_df["PB"] / latest_df["PB_MA5Y"].clip(lower=0.1)
    latest_df["pe_z_score"]    = (latest_df["PE"] - latest_df["PE_MA5Y"]) / latest_df["PE_SD5Y"].clip(lower=0.1)
    latest_df["pb_z_score"]    = (latest_df["PB"] - latest_df["PB_MA5Y"]) / latest_df["PB_SD5Y"].clip(lower=0.01)
    latest_df["np_growth_1q"]  = latest_df["NP_P0"] / latest_df["NP_P1"].replace(0, np.nan)
    latest_df["np_growth_1y"]  = latest_df["NP_P0"] / latest_df["NP_P4"].replace(0, np.nan)
    latest_df["cf_yield"]      = (latest_df["CF_OA_5Y"] / latest_df["OShares"].clip(lower=1)
                                   / latest_df["Close"].clip(lower=1)) * 100
    latest_df["price_vs_ma200"]= latest_df["Close"] / latest_df["MA200"].clip(lower=1)
    latest_df["price_vs_ma50"] = latest_df["Close"] / latest_df["MA50"].clip(lower=1)
    latest_df["ma10_vs_ma200"] = latest_df["MA10"] / latest_df["MA200"].clip(lower=1)
    latest_df["vol_ratio"]     = latest_df["Volume"] / latest_df["Volume_1M"].clip(lower=1)
    latest_df["vol_vs_p50"]    = latest_df["Volume"] / latest_df["Volume_3M_P50"].clip(lower=1)
    latest_df["close_vs_lo"]   = latest_df["Close"] / latest_df["LO_3M_T1"].clip(lower=1)
    latest_df["close_vs_vap1m"]= latest_df["Close"] / latest_df["VAP1M"].clip(lower=1)
    latest_df["rsi_vs_max3m"]  = latest_df["D_RSI"] / latest_df["D_RSI_Max3M"].clip(lower=0.01)
    latest_df["rsi_vs_max1w"]  = latest_df["D_RSI"] / latest_df["D_RSI_Max1W"].clip(lower=0.01)
    latest_df["rsi_momentum"]  = latest_df["D_RSI"] - latest_df["D_RSI_T1W"]
    latest_df["macd_momentum"] = latest_df["D_MACDdiff"]  # use histogram directly
    latest_df["volatility"]    = latest_df["HI_3M_T1"] / latest_df["LO_3M_T1"].clip(lower=1)
    latest_df["strat_tier"]    = 2  # default to MED for universe scan

    # Score all tickers in BQ universe
    avail_feats = [f for f in FEATURES if f in latest_df.columns]
    X_latest = latest_df[avail_feats].replace([np.inf,-np.inf], np.nan)
    # Build full feature matrix with median fill
    X_full = pd.DataFrame(index=latest_df.index, columns=FEATURES, dtype=float)
    for f in FEATURES:
        if f in X_latest.columns:
            X_full[f] = X_latest[f].values
        else:
            X_full[f] = fill_vals.get(f, 0)
    X_full = X_full.fillna(fill_vals)

    latest_df["score"] = rf.predict_proba(X_full)[:,1]

    # High-conviction screens (D_MACDdiff > 0 means MACD histogram positive)
    screen_A = latest_df[
        (latest_df["score"] >= 0.55) &
        (latest_df["D_RSI"] < 0.55) &
        (latest_df["D_MACDdiff"] > 0) &
        (latest_df["np_growth_1y"] > 1.10)
    ].sort_values("score", ascending=False)

    screen_B = latest_df[
        (latest_df["score"] >= 0.50) &
        (latest_df["D_RSI"] < 0.60) &
        (latest_df["D_MACDdiff"] > 0) &
        (latest_df["FSCORE"] > 4) &
        (latest_df["ROE_Min3Y"] > 0.06)
    ].sort_values("score", ascending=False)

    print(f"\n  Screen A (score>=0.55 + RSI<0.55 + MACD>0 + NP_YoY>10%): {len(screen_A)} tickers")
    if len(screen_A) > 0:
        cols_a = ["ticker","time","score","D_RSI","D_MACDdiff","np_growth_1y","FSCORE","ROE_Min3Y","pe_vs_hist","ICB_Code"]
        avail_a = [c for c in cols_a if c in screen_A.columns]
        print(screen_A[avail_a].head(20).to_string(index=False))

    print(f"\n  Screen B (score>=0.50 + MACD hist rising + FSCORE>4 + ROE_Min3Y>6%): {len(screen_B)} tickers")
    if len(screen_B) > 0:
        cols_b = ["ticker","time","score","D_RSI","D_MACDdiff","FSCORE","ROE_Min3Y","PE","PB","ICB_Code"]
        avail_b = [c for c in cols_b if c in screen_B.columns]
        print(screen_B[avail_b].head(20).to_string(index=False))

    # Save universe scan
    latest_df.sort_values("score", ascending=False).to_csv("data/universe_scored.csv", index=False)
    print(f"\n  Universe scan saved: universe_scored.csv ({len(latest_df):,} tickers)")
else:
    print("  No latest BQ data returned")
    latest_df = pd.DataFrame()

# ── CHART ─────────────────────────────────────────────────────────────────────
print(f"\nGenerating charts ...")
fig = plt.figure(figsize=(24, 18), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.40)

# P1: Score distribution of HOLD positions
ax1 = fig.add_subplot(gs[0, :2])
grade_clr = {"A": GREEN, "B": BLUE, "C": YELLOW, "D": RED}
for g in ["A","B","C","D"]:
    sub = hold_ranked[hold_ranked["grade"]==g]["score"]
    if len(sub) > 0:
        ax1.hist(sub, bins=30, alpha=0.7, color=grade_clr[g], label=f"Grade {g} (n={len(sub)})")
ax1.set_xlabel("Model Score"); ax1.set_ylabel("Count")
ax1.set_title(f"Score Distribution of Active HOLD Positions\n"
              f"({len(hold_ranked):,} unique ticker+strategy positions)",
              color=TEXT_CLR, fontweight="bold")
ax1.axvline(0.45, color=YELLOW, linewidth=1.5, linestyle="--", label="0.45 threshold")
ax1.axvline(0.55, color=GREEN,  linewidth=1.5, linestyle="--", label="0.55 threshold")
ax1.legend(fontsize=9)

# P2: Top strategies in HOLD by avg score
ax2 = fig.add_subplot(gs[0, 2])
sd2 = strat_hold.head(12)
colors2 = [GREEN if s>=0.50 else (YELLOW if s>=0.42 else RED) for s in sd2["avg_score"]]
bars2 = ax2.barh(range(len(sd2)), sd2["avg_score"]*100, color=colors2, alpha=0.85)
ax2.axvline(45, color=YELLOW, linewidth=1.2, linestyle="--")
ax2.axvline(55, color=GREEN,  linewidth=1.2, linestyle="--")
ax2.set_yticks(range(len(sd2)))
ax2.set_yticklabels([f"{s}\n(n={int(r['n'])})" for s,r in sd2.iterrows()], fontsize=7.5)
ax2.set_xlabel("Avg Score (x100)")
ax2.set_title("Avg Score by Strategy\n(HOLD positions)", color=TEXT_CLR, fontweight="bold")
for i, (bar, (s, r)) in enumerate(zip(bars2, sd2.iterrows())):
    ax2.text(bar.get_width()+0.3, i, f"{r['avg_score']:.3f}", va="center", fontsize=7.5, color=TEXT_CLR)

# P3: % Grade A+B per strategy
ax3 = fig.add_subplot(gs[0, 3])
sd3 = strat_hold.nlargest(12, "pct_AB")
colors3 = [GREEN if p>=0.30 else (YELLOW if p>=0.15 else ORANGE) for p in sd3["pct_AB"]]
ax3.barh(range(len(sd3)), sd3["pct_AB"]*100, color=colors3, alpha=0.85)
ax3.set_yticks(range(len(sd3)))
ax3.set_yticklabels([s for s in sd3.index], fontsize=8)
ax3.set_xlabel("% Grade A or B")
ax3.set_title("% High-Quality Positions\n(Grade A+B)", color=TEXT_CLR, fontweight="bold")

# P4: Score threshold analysis (val 2025)
ax4 = fig.add_subplot(gs[1, :2])
if thr_data:
    td = pd.DataFrame(thr_data)
    ax4_twin = ax4.twinx()
    ax4.bar(range(len(td)), td["wr"]*100, color=[
        GREEN if wr>=0.50 else (YELLOW if wr>=0.40 else RED) for wr in td["wr"]
    ], alpha=0.7, label="Win Rate")
    ax4_twin.plot(range(len(td)), td["pct"]*100, "o--", color=CYAN, linewidth=2, label="% of deals")
    ax4.axhline(val_df["is_good"].mean()*100, color=RED, linewidth=1.5, linestyle="--", label=f"Baseline {val_df['is_good'].mean():.0%}")
    ax4.set_xticks(range(len(td)))
    ax4.set_xticklabels([f">={t['thr']:.2f}" for _,t in td.iterrows()])
    ax4.set_ylabel("Win Rate (%)"); ax4_twin.set_ylabel("% of Deals (cyan)", color=CYAN)
    ax4.set_title(f"Score Threshold Analysis — Val 2025\nAUC={auc_va:.3f}  baseline WR={val_df['is_good'].mean():.1%}",
                  color=TEXT_CLR, fontweight="bold")
    ax4.legend(fontsize=8, loc="upper right")
    for i, (_, t) in enumerate(td.iterrows()):
        ax4.text(i, t["wr"]*100+0.5, f"{t['wr']:.0%}", ha="center", fontsize=9, color=TEXT_CLR, fontweight="bold")

# P5: Feature importance top 20
ax5 = fig.add_subplot(gs[1, 2:])
top20 = feat_imp.head(20)
fund_feats = {"PE","PB","PCF","ROE5Y","ROE_Min3Y","ROE_Min5Y","ROIC5Y","ROIC_Min3Y",
              "FSCORE","np_growth_1q","np_growth_1y","cf_yield","pe_vs_hist","pb_vs_hist",
              "pe_z_score","pb_z_score","Risk_Rating"}
colors5 = [ORANGE if f in fund_feats else BLUE for f in top20.index[::-1]]
ax5.barh(range(len(top20)), top20.values[::-1], color=colors5, alpha=0.85)
ax5.set_yticks(range(len(top20)))
ax5.set_yticklabels(top20.index[::-1], fontsize=8)
ax5.set_xlabel("Feature Importance")
ax5.set_title(f"Feature Importance  (Orange=Fundamental, Blue=Technical)\nAUC train={auc_tr:.3f} | AUC val={auc_va:.3f}",
              color=TEXT_CLR, fontweight="bold")

# P6: Top 20 Hold positions by score
ax6 = fig.add_subplot(gs[2, :2])
top20h = hold_ranked.nlargest(20, "score").reset_index(drop=True)
label6  = [f"{r['ticker']}\n{r['filter'][:8]}" for _,r in top20h.iterrows()]
score6  = top20h["score"].values
grade6  = top20h["grade"].values
col6    = [grade_clr.get(g, PURPLE) for g in grade6]
bars6   = ax6.barh(range(len(top20h)), score6, color=col6, alpha=0.85)
ax6.set_yticks(range(len(top20h)))
ax6.set_yticklabels(label6, fontsize=7)
ax6.axvline(0.50, color=YELLOW, linewidth=1.2, linestyle="--")
ax6.axvline(0.55, color=GREEN,  linewidth=1.2, linestyle="--")
ax6.set_xlabel("Score")
ax6.set_title(f"TOP 20 HOLD Positions by Score\n(Green=A, Blue=B, Yellow=C)",
              color=TEXT_CLR, fontweight="bold")
for bar, (_, r) in zip(bars6, top20h.iterrows()):
    ax6.text(bar.get_width()+0.002, bar.get_y()+bar.get_height()/2,
             f"{r['score']:.3f} [{r['grade']}]", va="center", fontsize=7, color=TEXT_CLR)

# P7: Universe scan score distribution (if available)
ax7 = fig.add_subplot(gs[2, 2:])
if not latest_df.empty and "score" in latest_df.columns:
    bins_u = np.arange(0.1, 0.95, 0.04)
    ax7.hist(latest_df["score"], bins=bins_u, color=PURPLE, alpha=0.7, label="All tickers")
    if len(screen_A) > 0:
        ax7.hist(screen_A["score"], bins=bins_u, color=GREEN, alpha=0.85, label=f"Screen A (n={len(screen_A)})")
    if len(screen_B) > 0:
        ax7.hist(screen_B["score"], bins=bins_u, color=BLUE,  alpha=0.70, label=f"Screen B (n={len(screen_B)})")
    ax7.axvline(0.50, color=YELLOW, linewidth=1.5, linestyle="--")
    ax7.axvline(0.55, color=GREEN,  linewidth=1.5, linestyle="--")
    ax7.set_xlabel("Score"); ax7.set_ylabel("Count")
    ax7.set_title(f"Universe Scan — Latest {latest_df['time'].max().date()}\n"
                  f"{len(latest_df):,} tickers scored", color=TEXT_CLR, fontweight="bold")
    ax7.legend(fontsize=9)
else:
    ax7.text(0.5, 0.5, "No universe data", transform=ax7.transAxes,
             ha="center", va="center", color=TEXT_CLR, fontsize=14)
    ax7.set_title("Universe Scan", color=TEXT_CLR)

fig.suptitle(
    f"PHASE 5 — Live Signal Scoring  |  Model AUC={auc_va:.3f}  |  "
    f"Hold: {len(hold_ranked):,} positions  |  Today: {TODAY}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.995)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"Chart saved: {OUT_IMG}")

# ── FINAL ACTIONABLE SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*70}")
print("ACTIONABLE SUMMARY")
print(f"{'='*70}")

grade_a = hold_ranked[hold_ranked["grade"]=="A"]
grade_b = hold_ranked[hold_ranked["grade"]=="B"]
print(f"""
MODEL PERFORMANCE:
  AUC (train <=2024) : {auc_tr:.3f}
  AUC (val  2025)    : {auc_va:.3f}
  Baseline WR (2025) : {val_df['is_good'].mean():.1%}

SCORE >= 0.55 threshold (val 2025):
  {next((f"n={d['n']} ({d['pct']:.0%} of signals) | WR={d['wr']:.1%} | avg={d['avg']:.1f}%" for d in thr_data if d['thr']==0.55), 'N/A')}

ACTIVE HOLD POSITIONS:
  Total unique (latest per ticker+strategy): {len(hold_ranked):,}
  Grade A (highest quality): {len(grade_a):>4}  tickers: {', '.join(grade_a['ticker'].head(15).tolist())}{'...' if len(grade_a)>15 else ''}
  Grade B (good quality)   : {len(grade_b):>4}  tickers: {', '.join(grade_b['ticker'].head(15).tolist())}{'...' if len(grade_b)>15 else ''}

KEY RULES FOR ENTRY FILTER:
  [1] Score >= 0.55 : keep only top-quality signals (WR ~51%)
  [2] MACD > 0      : momentum confirmed (primary technical gate)
  [3] NP_YoY > 10%  : earnings growth confirmed (fundamental gate)
  [4] ROE_Min3Y > 6%: quality floor (never lose quality companies)
  [5] FSCORE > 4    : financial health (Piotroski)

COMBINED FILTER (Score>=0.45 + MACD>0 + NP_YoY>10%):
""")
combo_val = val_df[
    (val_df["score"] >= 0.45) &
    (val_df["D_MACDdiff"] > 0) &
    (val_df["np_growth_1y"] > 1.10)
]
print(f"  n={len(combo_val)} ({len(combo_val)/len(val_df):.0%}) | "
      f"WR={combo_val['is_good'].mean():.1%} | "
      f"avg={combo_val['Sell_profit'].mean():.1f}% | "
      f"lift={combo_val['is_good'].mean()/val_df['is_good'].mean()-1:+.0%}")

print(f"\nOutputs:")
print(f"  {OUT_CSV}         -- Scored active HOLD positions")
print(f"  universe_scored.csv -- All tickers scored on latest BQ data")
print(f"  {MODEL_FILE}   -- Trained RF model (pickle)")
print(f"  {OUT_IMG}  -- Charts")
print(f"\nDone.")
