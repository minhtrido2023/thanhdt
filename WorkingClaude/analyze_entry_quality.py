#!/usr/bin/env python3
"""
analyze_entry_quality.py
========================
Phân tích toàn diện chất lượng deals từ profile_hit.csv
kết hợp BẢO dữ liệu CƠ BẢN từ BigQuery (PE, PB, ROE, NP growth, FSCORE...)

Mục tiêu: tìm bộ lọc có thể áp dụng ngay khi có tín hiệu mua

Flow:
  1. Load profile_hit.csv (92K deals, 2014-2026)
  2. Fetch fundamentals từ BQ cho 453 tickers
  3. Merge -> 35+ features (kỹ thuật + cơ bản)
  4. RandomForest + feature importance
  5. Per-strategy rules (within each strategy, what separates winners?)
  6. Bộ lọc thực tế + scoring table
"""

import warnings; warnings.filterwarnings("ignore")
import json, os, subprocess, tempfile
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_FILE   = "profile_hit.csv"
PROJECT     = "lithe-record-440915-m9"
BQ_BIN      = r"bq"
BQ_CHUNK    = 120
OUT_IMG     = "analyze_entry_quality.png"
OUT_CSV     = "entry_quality_scored.csv"
TARGET_PCT  = 10.0   # "good deal" = Sell_profit > 10%
TRAIN_YEAR  = 2024   # train on <= 2024, test on 2025+

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"

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
        print(f"  [BQ ERROR] {label}: {r.stdout[:200]}")
        return None
    txt = r.stdout.strip()
    if not txt: return pd.DataFrame()
    try: return pd.read_csv(StringIO(txt))
    except: return pd.DataFrame()

# ── LOAD PROFILE HIT ──────────────────────────────────────────────────────────
print("Loading profile_hit.csv ...")
df = pd.read_csv(DATA_FILE)
df["time"] = pd.to_datetime(df["time"])
print(f"  {len(df):,} rows | {df['ticker'].nunique()} tickers | "
      f"{df['time'].min().year} -> {df['time'].max().year}")

# Filter to closed deals only
closed = df[df["Sell_filter"] != "Hold"].copy()
print(f"  Closed deals: {len(closed):,} | win rate >10%: {(closed['Sell_profit']>TARGET_PCT).mean():.1%}")

# ── FETCH FUNDAMENTALS FROM BQ ────────────────────────────────────────────────
FUND_COLS = """
    t.ticker, t.time,
    t.PE, t.PB, t.PCF,
    t.ROE5Y, t.ROE_Min3Y, t.ROE_Min5Y,
    t.ROIC5Y, t.ROIC_Min3Y,
    t.FSCORE,
    t.NP_P0, t.NP_P1, t.NP_P2, t.NP_P4,
    t.CF_OA_5Y, t.OShares,
    t.Risk_Rating,
    t.HI_3M_T1,
    t.MA10, t.MA50, t.MA200,
    t.D_CMF, t.D_MACDdiff,
    t.C_L1W, t.Close_T1W,
    t.Volume_3M_P50, t.Volume_3M_P90,
    t.D_RSI_T1,
    t.Close, t.Open,
    t.Sup_1Y, t.Res_1Y, t.VAP1M, t.VAP3M,
    t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y
"""

tickers   = closed["ticker"].unique().tolist()
date_min  = closed["time"].min().strftime("%Y-%m-%d")
date_max  = closed["time"].max().strftime("%Y-%m-%d")
n_chunks  = -(-len(tickers) // BQ_CHUNK)
print(f"\nFetching fundamentals: {len(tickers)} tickers | {n_chunks} chunks ...")

fund_frames = []
for i in range(0, len(tickers), BQ_CHUNK):
    chunk = tickers[i:i+BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (f"SELECT {FUND_COLS} FROM tav2_bq.ticker AS t "
             f"WHERE t.ticker IN ({tstr}) "
             f"AND t.time BETWEEN '{date_min}' AND '{date_max}' "
             f"ORDER BY t.ticker, t.time")
    res = bq_query(sql, f"chunk {i//BQ_CHUNK+1}")
    if res is not None and not res.empty:
        res["time"] = pd.to_datetime(res["time"])
        fund_frames.append(res)
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: {len(res) if res is not None else 0:,} rows")

if not fund_frames:
    raise RuntimeError("No BQ data returned — check column names")
fund_df = pd.concat(fund_frames, ignore_index=True)
print(f"  Total BQ rows: {len(fund_df):,}")

# ── MERGE ─────────────────────────────────────────────────────────────────────
print("\nMerging profile_hit + BQ fundamentals ...")
merged = closed.merge(fund_df, on=["ticker","time"], how="left", suffixes=("","_bq"))
print(f"  Merged: {len(merged):,} rows | BQ match rate: {merged['PE'].notna().mean():.1%}")

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
print("Engineering features ...")

# Valuation vs history
merged["pe_vs_hist"]   = merged["PE"] / merged["PE_MA5Y"].clip(lower=0.5)
merged["pb_vs_hist"]   = merged["PB"] / merged["PB_MA5Y"].clip(lower=0.1)
merged["pe_z_score"]   = (merged["PE"] - merged["PE_MA5Y"]) / merged["PE_SD5Y"].clip(lower=0.1)
merged["pb_z_score"]   = (merged["PB"] - merged["PB_MA5Y"]) / merged["PB_SD5Y"].clip(lower=0.01)

# Earnings quality
merged["np_growth_1q"] = merged["NP_P0"] / merged["NP_P1"].replace(0, np.nan)   # QoQ
merged["np_growth_1y"] = merged["NP_P0"] / merged["NP_P4"].replace(0, np.nan)   # YoY
merged["cf_yield"]     = (merged["CF_OA_5Y"] / merged["OShares"].clip(lower=1)
                          / merged["Price"].clip(lower=1)) * 100  # CF yield %

# Trend
close_col = "Close" if "Close" in merged.columns else "Close_bq"
merged["price_vs_ma200"]  = merged[close_col] / merged["MA200"].clip(lower=1)
merged["price_vs_ma50"]   = merged[close_col] / merged["MA50"].clip(lower=1)
merged["ma10_vs_ma200"]   = merged["MA10"] / merged["MA200"].clip(lower=1)

# Technical
merged["vol_ratio"]       = merged["Volume"] / merged["Volume_1M"].clip(lower=1)
merged["vol_vs_p50"]      = merged["Volume"] / merged["Volume_3M_P50"].clip(lower=1)
merged["close_vs_lo"]     = merged[close_col] / merged["LO_3M_T1"].clip(lower=1)
merged["close_vs_vap1m"]  = merged[close_col] / merged["VAP1M"].clip(lower=1)
merged["rsi_vs_max3m"]    = merged["D_RSI"] / merged["D_RSI_Max3M"].clip(lower=0.01)
merged["rsi_vs_max1w"]    = merged["D_RSI"] / merged["D_RSI_Max1W"].clip(lower=0.01)
merged["rsi_momentum"]    = merged["D_RSI"] - merged["D_RSI_T1W"]
merged["mfi_momentum"]    = merged["D_MFI"] - merged["D_MFI_T1W"]
merged["macd_momentum"]   = merged["D_MACD"] - merged["D_MACD_T1W"]
merged["volatility"]      = merged["HI_3M_T1"] / merged["LO_3M_T1"].clip(lower=1)

# Encode strategy
le = LabelEncoder()
merged["filter_enc"] = le.fit_transform(merged["filter"])

# Strategy tier (from previous analysis)
HIGH = {"RSILow30","BuySupport","BuySupport_special","VolMax1Y","VolMax1Y_special",
        "BullDvg_special","TrendingGrowth_special","AccSup","TL3M_special"}
MED  = {"UnderBV","Conservative","SurpriseEarning","T3P4","TradingValueMax","BKMA200","TL3M"}
merged["strat_tier"] = merged["filter"].map(
    lambda f: 3 if f in HIGH else (2 if f in MED else 1))

FEATURES = [
    # Fundamental
    "PE", "PB", "PCF", "ROE5Y", "ROE_Min3Y", "ROE_Min5Y",
    "ROIC5Y", "ROIC_Min3Y", "FSCORE",
    "np_growth_1q", "np_growth_1y", "cf_yield",
    "pe_vs_hist", "pb_vs_hist", "pe_z_score", "pb_z_score",
    "Risk_Rating",
    # Technical
    "D_RSI", "D_MFI", "D_MACD", "D_MACDdiff", "D_CMF",
    "D_RSI_Max3M", "D_RSI_Max1W", "D_RSI_T1W",
    "rsi_vs_max3m", "rsi_vs_max1w", "rsi_momentum",
    "mfi_momentum", "macd_momentum",
    "vol_ratio", "vol_vs_p50",
    "close_vs_lo", "close_vs_vap1m", "C_L1W", "volatility",
    # Trend
    "price_vs_ma200", "price_vs_ma50", "ma10_vs_ma200",
    # Strategy
    "strat_tier", "filter_enc",
]

merged["is_good"]   = (merged["Sell_profit"] > TARGET_PCT).astype(int)
merged["is_profit"] = (merged["Sell_profit"] > 0).astype(int)

# Drop NaN
df_model = merged[FEATURES + ["is_good","is_profit","Sell_profit","filter","time","ticker"]].dropna()
df_model = df_model.replace([np.inf, -np.inf], np.nan).dropna()
print(f"  Model dataset: {len(df_model):,} rows after dropna")
print(f"  Win rate (>10%): {df_model['is_good'].mean():.1%} | Profitable: {df_model['is_profit'].mean():.1%}")

# ── TRAIN / TEST SPLIT ────────────────────────────────────────────────────────
train = df_model[df_model["time"].dt.year <= TRAIN_YEAR]
test  = df_model[df_model["time"].dt.year >  TRAIN_YEAR]
print(f"\nSplit: train={len(train):,} ({train['time'].dt.year.min()}-{TRAIN_YEAR}) "
      f"| test={len(test):,} ({TRAIN_YEAR+1}+)")
print(f"  Train win rate: {train['is_good'].mean():.1%} | Test: {test['is_good'].mean():.1%}")

X_tr = train[FEATURES]; y_tr = train["is_good"]
X_te = test[FEATURES];  y_te = test["is_good"]

# ── RANDOM FOREST ─────────────────────────────────────────────────────────────
print("\nTraining RandomForest ...")
rf = RandomForestClassifier(n_estimators=400, max_depth=10, min_samples_leaf=15,
                            class_weight="balanced", random_state=42, n_jobs=-1)
rf.fit(X_tr, y_tr)
y_prob_tr = rf.predict_proba(X_tr)[:,1]
y_prob_te = rf.predict_proba(X_te)[:,1]
auc_tr = roc_auc_score(y_tr, y_prob_tr)
auc_te = roc_auc_score(y_te, y_prob_te)
print(f"  AUC train={auc_tr:.3f} | AUC test={auc_te:.3f}")

df_model = df_model.copy()
df_model["score"] = rf.predict_proba(df_model[FEATURES])[:,1]

feat_imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
print(f"\nTop 15 features:")
for f, v in feat_imp.head(15).items():
    print(f"  {f:<22} {v:.4f}")

# ── SCORE THRESHOLD ANALYSIS (test set) ───────────────────────────────────────
te_df = df_model[df_model["time"].dt.year > TRAIN_YEAR].copy()
base_wr  = te_df["is_good"].mean()
base_avg = te_df["Sell_profit"].mean()
print(f"\n--- Score Threshold (test set, baseline WR={base_wr:.1%}, avg={base_avg:.1f}%) ---")
print(f"{'Score':>7} {'N':>6} {'%':>5} {'WinRate':>8} {'Lift':>6} {'AvgProfit':>10} {'MedProfit':>10}")
thr_rows = []
for thr in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
    sub = te_df[te_df["score"] >= thr]
    if len(sub) < 20: continue
    wr  = sub["is_good"].mean()
    avg = sub["Sell_profit"].mean()
    med = sub["Sell_profit"].median()
    thr_rows.append({"thr":thr,"n":len(sub),"wr":wr,"avg":avg,"med":med})
    print(f"  >={thr:.2f} {len(sub):>6} {len(sub)/len(te_df):>4.0%} "
          f"{wr:>7.1%} {wr/base_wr-1:>+5.0%} {avg:>9.1f}% {med:>9.1f}%")

# ── PER-STRATEGY ANALYSIS ─────────────────────────────────────────────────────
print("\n--- Per-strategy performance (test set) ---")
strat_stats = {}
for sf, grp in te_df.groupby("filter"):
    n   = len(grp)
    wr  = grp["is_good"].mean()
    avg = grp["Sell_profit"].mean()
    sc  = grp["score"].mean()
    strat_stats[sf] = {"n":n,"wr":wr,"avg":avg,"score":sc}

strat_df = pd.DataFrame(strat_stats).T.sort_values("wr", ascending=False)
print(strat_df[["n","wr","avg","score"]].to_string())

# ── WITHIN-STRATEGY RULES: for top 5 strategies, find what matters ─────────────
print("\n=== Within-Strategy Rules (test set) ===")
top_strats = strat_df.nlargest(5, "wr").index.tolist()

# Key features to check within each strategy (from top importance + filter.json logic)
CHECK_FEATURES = {
    "D_RSI":         ("low", 0.40, "RSI < 0.40 (oversold at entry)"),
    "D_MACD":        ("high", 0,   "MACD > 0 (positive momentum)"),
    "D_MACDdiff":    ("high", 0,   "MACDdiff > 0 (histogram rising)"),
    "D_CMF":         ("high", 0.1, "CMF > 0.10 (money flowing in)"),
    "np_growth_1q":  ("high", 1.1, "NP QoQ > 10% (earnings accelerating)"),
    "np_growth_1y":  ("high", 1.15,"NP YoY > 15%"),
    "FSCORE":        ("high", 5,   "FSCORE > 5 (quality)"),
    "ROE_Min3Y":     ("high", 0.08,"ROE Min 3Y > 8%"),
    "pe_vs_hist":    ("low", 0.90, "PE < 90% of 5Y avg (cheap vs history)"),
    "pb_vs_hist":    ("low", 0.90, "PB < 90% of 5Y avg (cheap vs history)"),
    "rsi_vs_max3m":  ("low", 0.75, "RSI < 75% of 3M peak (room to grow)"),
    "price_vs_ma200":("low", 1.15, "Price < 1.15x MA200 (not over-extended)"),
    "Risk_Rating":   ("low", 4,    "Risk_Rating <= 4 (low risk)"),
    "vol_vs_p50":    ("high", 0.8, "Volume > 80% of 3M median (active)"),
}

for strat in top_strats[:4]:
    grp = te_df[te_df["filter"] == strat]
    if len(grp) < 30: continue
    base = grp["is_good"].mean()
    print(f"\n  Strategy: {strat} (n={len(grp)}, WR={base:.1%})")
    results = []
    for feat, (direction, threshold, desc) in CHECK_FEATURES.items():
        if feat not in grp.columns: continue
        if direction == "low":
            sub = grp[grp[feat] <= threshold]
        else:
            sub = grp[grp[feat] >= threshold]
        if len(sub) < 10: continue
        sub_wr  = sub["is_good"].mean()
        lift    = sub_wr / base - 1
        results.append((desc, len(sub), sub_wr, lift, sub["Sell_profit"].mean()))
    for desc, n, wr, lift, avg in sorted(results, key=lambda x: x[3], reverse=True)[:6]:
        marker = "+++" if lift > 0.3 else ("++" if lift > 0.15 else "+")
        print(f"    {marker} {desc}: n={n} WR={wr:.0%} ({lift:+.0%} lift) avg={avg:.1f}%")

# ── COMPOSITE FILTER RULES ────────────────────────────────────────────────────
print("\n=== Composite Filter Rules (test set) ===")
print(f"Baseline: WR={base_wr:.1%}, avg={base_avg:.1f}%\n")

combos = [
    ("Score >= 0.50",
     te_df["score"] >= 0.50),
    ("Score >= 0.45 + Tier2+",
     (te_df["score"] >= 0.45) & (te_df["strat_tier"] >= 2)),
    ("MACD>0 + CMF>0.10 + RSI<0.55",
     (te_df["D_MACD"] > 0) & (te_df["D_CMF"] > 0.10) & (te_df["D_RSI"] < 0.55)),
    ("MACD>0 + NP_YoY>15% + FSCORE>4",
     (te_df["D_MACD"] > 0) & (te_df["np_growth_1y"] > 1.15) & (te_df["FSCORE"] > 4)),
    ("Tier2+ + MACD>0 + PE<hist + ROE_Min3Y>6%",
     (te_df["strat_tier"] >= 2) & (te_df["D_MACD"] > 0)
     & (te_df["pe_vs_hist"] < 1.0) & (te_df["ROE_Min3Y"] > 0.06)),
    ("Tier2+ + MACD>0 + CMF>0.05 + RSI<0.60 + NP_YoY>10%",
     (te_df["strat_tier"] >= 2) & (te_df["D_MACD"] > 0)
     & (te_df["D_CMF"] > 0.05) & (te_df["D_RSI"] < 0.60)
     & (te_df["np_growth_1y"] > 1.10)),
    ("Score>=0.45 + MACD>0 + NP_YoY>10%",
     (te_df["score"] >= 0.45) & (te_df["D_MACD"] > 0)
     & (te_df["np_growth_1y"] > 1.10)),
    ("Score>=0.50 + FSCORE>4 + ROE_Min3Y>5%",
     (te_df["score"] >= 0.50) & (te_df["FSCORE"] > 4)
     & (te_df["ROE_Min3Y"] > 0.05)),
]

best_combo = None; best_wr = 0
print(f"{'Filter':<50} {'N':>5} {'%':>5} {'WR':>7} {'Lift':>6} {'Avg':>7} {'Med':>7}")
print("-"*95)
for name, mask in combos:
    sub = te_df[mask]
    if len(sub) < 20: continue
    wr  = sub["is_good"].mean()
    avg = sub["Sell_profit"].mean()
    med = sub["Sell_profit"].median()
    lift= wr / te_df["is_good"].mean() - 1
    print(f"  {name:<48} {len(sub):>5} {len(sub)/len(te_df):>4.0%} "
          f"{wr:>6.1%} {lift:>+5.0%} {avg:>6.1f}% {med:>6.1f}%")
    if wr > best_wr and len(sub)/len(te_df) >= 0.10:
        best_wr = wr; best_combo = name

print(f"\nBest practical filter (>=10% of deals): {best_combo} -> WR={best_wr:.1%}")

# ── SAVE SCORED CSV ───────────────────────────────────────────────────────────
save_cols = ["filter","ticker","time","Sell_profit","is_good","score",
             "D_RSI","D_MACD","D_CMF","np_growth_1y","np_growth_1q",
             "FSCORE","ROE_Min3Y","pe_vs_hist","pb_vs_hist",
             "strat_tier","price_vs_ma200","rsi_vs_max3m"]
save_df = df_model[[c for c in save_cols if c in df_model.columns]]
save_df.sort_values("score", ascending=False).to_csv(OUT_CSV, index=False)
print(f"Scored CSV saved: {OUT_CSV}")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 16), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.48, wspace=0.38)

# P1: Feature importance (top 20)
ax1 = fig.add_subplot(gs[0, :2])
top20 = feat_imp.head(20)
fund_feats = {"PE","PB","PCF","ROE5Y","ROE_Min3Y","ROE_Min5Y","ROIC5Y","ROIC_Min3Y",
              "FSCORE","np_growth_1q","np_growth_1y","cf_yield","pe_vs_hist","pb_vs_hist",
              "pe_z_score","pb_z_score","Risk_Rating"}
colors1 = [ORANGE if f in fund_feats else BLUE for f in top20.index[::-1]]
ax1.barh(range(len(top20)), top20.values[::-1], color=colors1, alpha=0.85)
ax1.set_yticks(range(len(top20)))
ax1.set_yticklabels(top20.index[::-1], fontsize=8)
ax1.set_xlabel("Feature Importance")
ax1.set_title(f"Top 20 Features  |  AUC test={auc_te:.3f}\n"
              "Orange=Fundamental, Blue=Technical", color=TEXT_CLR, fontweight="bold")
for i, (f, v) in enumerate(zip(top20.index[::-1], top20.values[::-1])):
    ax1.text(v+0.001, i, f"{v:.3f}", va="center", fontsize=7, color=TEXT_CLR)

# P2: Win rate by strategy (test set)
ax2 = fig.add_subplot(gs[0, 2])
sd = strat_df.nlargest(15, "n")
colors2 = [GREEN if wr >= 0.40 else (YELLOW if wr >= 0.25 else RED)
           for wr in sd["wr"]]
ax2.barh(range(len(sd)), sd["wr"]*100, color=colors2, alpha=0.85)
ax2.axvline(te_df["is_good"].mean()*100, color=RED, linewidth=1.5, linestyle="--")
ax2.set_yticks(range(len(sd)))
ax2.set_yticklabels([f"{s}\n(n={int(r['n'])})" for s,r in sd.iterrows()], fontsize=7)
ax2.set_xlabel("Win Rate (>10%)")
ax2.set_title("Win Rate by Strategy\n(test set)", color=TEXT_CLR, fontweight="bold")

# P3: Score calibration
ax3 = fig.add_subplot(gs[1, 0])
bins = np.arange(0.1, 0.9, 0.06)
mids = [(a+b)/2 for a,b in zip(bins[:-1],bins[1:])]
wr_b, n_b = [], []
for lo, hi in zip(bins[:-1], bins[1:]):
    sub = te_df[(te_df["score"]>=lo)&(te_df["score"]<hi)]
    wr_b.append(sub["is_good"].mean()*100 if len(sub)>10 else np.nan)
    n_b.append(len(sub))
ax3.bar(mids, wr_b, width=0.055, color=BLUE, alpha=0.7)
ax3.axhline(te_df["is_good"].mean()*100, color=RED, linewidth=1.5, linestyle="--", label="Baseline")
ax3.axhline(50, color=YELLOW, linewidth=1.0, linestyle=":")
ax3.set_xlabel("Predicted Score"); ax3.set_ylabel("Win Rate (%)")
ax3.set_title("Score Calibration", color=TEXT_CLR, fontweight="bold")
ax3.legend(fontsize=8); ax3.set_ylim(0,100)

# P4: Score distribution by outcome
ax4 = fig.add_subplot(gs[1, 1])
good_s = te_df[te_df["is_good"]==1]["score"]
poor_s = te_df[te_df["is_good"]==0]["score"]
bins4  = np.linspace(0, 1, 30)
ax4.hist(poor_s, bins=bins4, alpha=0.6, color=RED,   label="Poor (<10%)", density=True)
ax4.hist(good_s, bins=bins4, alpha=0.6, color=GREEN, label="Good (>=10%)", density=True)
ax4.axvline(0.45, color=YELLOW, linewidth=2, linestyle="--", label="0.45 cutoff")
ax4.set_xlabel("Score"); ax4.set_ylabel("Density")
ax4.set_title("Score: Good vs Poor Deals", color=TEXT_CLR, fontweight="bold")
ax4.legend(fontsize=8)

# P5: Profit quartile by score
ax5 = fig.add_subplot(gs[1, 2])
te_df["sq"] = pd.qcut(te_df["score"], q=4, labels=["Q1","Q2","Q3","Q4"])
qdata  = [te_df[te_df["sq"]==q]["Sell_profit"].values for q in ["Q1","Q2","Q3","Q4"]]
qcols  = [RED, ORANGE, YELLOW, GREEN]
bp = ax5.boxplot(qdata, tick_labels=["Q1\n(low)","Q2","Q3","Q4\n(high)"],
                 patch_artist=True,
                 medianprops=dict(color="white", linewidth=2),
                 flierprops=dict(marker=".", markersize=2, alpha=0.3))
for patch, c in zip(bp["boxes"], qcols):
    patch.set_facecolor(c); patch.set_alpha(0.6)
ax5.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
ax5.axhline(TARGET_PCT, color=YELLOW, linewidth=0.8, linestyle=":")
ax5.set_ylim(-40, 100); ax5.set_ylabel("Sell_profit (%)")
ax5.set_title("Profit by Score Quartile", color=TEXT_CLR, fontweight="bold")
for i, (qd, c) in enumerate(zip(qdata, qcols)):
    wr = (np.array(qd)>TARGET_PCT).mean()
    ax5.text(i+1, 82, f"WR\n{wr:.0%}", ha="center", fontsize=9, color=c, fontweight="bold")

# P6–P8: Top fundamental features vs profit (univariate)
top_fund = [f for f in feat_imp.index if f in fund_feats][:3]
for fi, feat in enumerate(top_fund):
    ax = fig.add_subplot(gs[2, fi])
    try:
        bins_u = pd.qcut(df_model[feat], q=5, duplicates="drop")
        grp    = df_model.groupby(bins_u, observed=True)["Sell_profit"].agg(["mean","count"]).reset_index()
        cols_u = [GREEN if v>10 else (YELLOW if v>0 else RED) for v in grp["mean"]]
        ax.bar(range(len(grp)), grp["mean"], color=cols_u, alpha=0.85)
        ax.axhline(df_model["Sell_profit"].mean(), color=BLUE, linewidth=1.2, linestyle="--")
        ax.axhline(0, color=TEXT_CLR, linewidth=0.6, linestyle=":")
        ax.set_xticks(range(len(grp)))
        ax.set_xticklabels([str(v)[:9] for v in grp[feat]], fontsize=6, rotation=30)
        ax.set_ylabel("Avg Sell_profit (%)", fontsize=8)
        ax.set_title(f"{feat}\n(5 quintiles)", color=TEXT_CLR, fontsize=8, fontweight="bold")
        for bar, (_, r) in zip(ax.patches, grp.iterrows()):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                    f"n={int(r['count'])}", ha="center", fontsize=6, color=TEXT_CLR)
    except Exception as e:
        ax.text(0.5, 0.5, f"{feat}\n(error)", transform=ax.transAxes,
                ha="center", va="center", color=RED)

fig.suptitle(
    f"Entry Quality Analysis  |  {len(df_model):,} deals  |  "
    f"AUC test={auc_te:.3f}  |  Baseline WR={te_df['is_good'].mean():.1%}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.99)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: {OUT_IMG}")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print("\n"+"="*70)
print("ACTIONABLE ENTRY FILTER")
print("="*70)
best_mask = ((te_df["score"] >= 0.45) & (te_df["D_MACD"] > 0)
             & (te_df["np_growth_1y"] > 1.10))
bs = te_df[best_mask]
print(f"""
Best filter (Score>=0.45 + MACD>0 + NP YoY>10%):
  Deals passing: {len(bs):,} / {len(te_df):,} ({len(bs)/len(te_df):.0%})
  Win rate:      {bs['is_good'].mean():.1%}  (vs baseline {te_df['is_good'].mean():.1%})
  Avg profit:    {bs['Sell_profit'].mean():.1f}%  (vs baseline {te_df['Sell_profit'].mean():.1f}%)
  Med profit:    {bs['Sell_profit'].median():.1f}%
""")
