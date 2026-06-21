#!/usr/bin/env python3
"""
analyze_deal_quality.py
=======================
Phân tích chất lượng deals từ profile_hit.csv
Mục tiêu: tìm ra bộ lọc giúp chọn deals có tỉ lệ thành công cao nhất

Phương pháp:
  1. Phân tích đơn biến: từng feature tác động đến Sell_profit như thế nào
  2. RandomForest để tìm feature quan trọng nhất
  3. Xây dựng bộ điểm (score) cho mỗi deal
  4. Calibrate: score → win rate
  5. Đề xuất bộ lọc thực tế có thể áp dụng ngay

Target: Sell_profit > 10% (deal "tốt")
Baseline win rate (toàn bộ data): ~35%
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.inspection import permutation_importance

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_FILE  = "data/profile_hit.csv"
OUT_IMG    = "analyze_deal_quality.png"
OUT_CSV    = "data/deals_scored.csv"
TARGET_PCT = 10.0   # "good deal" threshold: Sell_profit > TARGET_PCT%
MIN_PROFIT = 5.0    # min profit threshold for "acceptable" deal

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0"; GREEN = "#4ecb71"
RED = "#e05c5c"; YELLOW = "#f0c060"; ORANGE = "#f0904a"; PURPLE = "#b57bee"
TEAL = "#4ecbbb"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor": GRID_CLR,  "axes.labelcolor": TEXT_CLR,
    "xtick.color": TEXT_CLR,     "ytick.color": TEXT_CLR,
    "text.color": TEXT_CLR,      "grid.color": GRID_CLR,
    "grid.linestyle": "--",      "grid.alpha": 0.4,
    "font.family": "DejaVu Sans",
})

# ── LOAD ──────────────────────────────────────────────────────────────────────
print("Loading data ...")
df = pd.read_csv(DATA_FILE)
df["time"] = pd.to_datetime(df["time"])
print(f"  {len(df):,} deals | {df['filter'].nunique()} strategies | "
      f"time: {df['time'].min().date()} -> {df['time'].max().date()}")

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
print("Engineering features ...")

# Derived features
df["vol_ratio"]    = df["Volume"] / df["Volume_1M"].clip(lower=1)
df["close_vs_lo"]  = df["Close"] / df["LO_3M_T1"].clip(lower=1)
df["close_vs_vap"] = df["Close"] / df["VAP1W"].clip(lower=1)
df["rsi_delta_1w"] = df["D_RSI"] - df["D_RSI_T1W"]         # RSI momentum (positive = accelerating)
df["mfi_delta_1w"] = df["D_MFI"] - df["D_MFI_T1W"]
df["macd_delta_1w"]= df["D_MACD"] - df["D_MACD_T1W"]
df["rsi_vs_max3m"] = df["D_RSI"] / df["D_RSI_Max3M"].clip(lower=0.01)  # RSI vs 3M peak
df["rsi_vs_max1w"] = df["D_RSI"] / df["D_RSI_Max1W"].clip(lower=0.01)  # RSI vs 1W peak

# Encode filter category
le = LabelEncoder()
df["filter_enc"] = le.fit_transform(df["filter"])

# Strategy tier (from win_rate analysis)
HIGH_WIN_STRATS   = {"RSILow30","BuySupport","BuySupport_special","VolMax1Y",
                     "VolMax1Y_special","BullDvg_special","TrendingGrowth_special",
                     "AccSup","TL3M_special"}
MED_WIN_STRATS    = {"UnderBV","Conservative","SurpriseEarning","T3P4",
                     "TradingValueMax","BKMA200","TL3M"}
LOW_WIN_STRATS    = {"BullDvg","DividendYield","CashCowStock","SuperGrowth","TrendingGrowth"}

df["strat_tier"] = df["filter"].map(
    lambda f: 3 if f in HIGH_WIN_STRATS else (2 if f in MED_WIN_STRATS else 1)
)

# Feature list (available at entry, no look-ahead)
FEATURES = [
    "D_RSI",          # RSI at entry
    "D_MFI",          # MFI at entry
    "D_MACD",         # MACD at entry
    "D_RSI_Max3M",    # 3-month RSI high
    "D_RSI_Max1W",    # 1-week RSI high
    "D_RSI_T1W",      # RSI 1 week ago
    "D_MFI_T1W",      # MFI 1 week ago
    "D_MACD_T1W",     # MACD 1 week ago
    "vol_ratio",      # Volume / 1M avg
    "close_vs_lo",    # Close / 3M low
    "close_vs_vap",   # Close / VAP1W
    "rsi_delta_1w",   # RSI acceleration
    "mfi_delta_1w",   # MFI acceleration
    "macd_delta_1w",  # MACD acceleration
    "rsi_vs_max3m",   # RSI vs 3M peak ratio
    "rsi_vs_max1w",   # RSI vs 1W peak ratio
    "strat_tier",     # Strategy quality tier
    "filter_enc",     # Strategy (encoded)
]

TARGET = "Sell_profit"
df["is_good"]  = (df[TARGET] > TARGET_PCT).astype(int)
df["is_profit"]= (df[TARGET] > 0).astype(int)

# Drop rows with NaN in features
df_model = df[FEATURES + ["is_good","is_profit",TARGET,"filter","time","ticker"]].dropna()
print(f"  {len(df_model):,} rows with complete features")
print(f"  Baseline win rate (>{TARGET_PCT}%): {df_model['is_good'].mean():.1%}")
print(f"  Baseline profitable rate (>0%):    {df_model['is_profit'].mean():.1%}")

# ── TEMPORAL SPLIT ────────────────────────────────────────────────────────────
split_date = pd.Timestamp("2025-07-01")
train_mask = df_model["time"] <  split_date
test_mask  = df_model["time"] >= split_date

X_train = df_model.loc[train_mask, FEATURES]
y_train = df_model.loc[train_mask, "is_good"]
X_test  = df_model.loc[test_mask,  FEATURES]
y_test  = df_model.loc[test_mask,  "is_good"]

print(f"\nTemporal split: train={train_mask.sum():,} | test={test_mask.sum():,}")
print(f"  Train win rate: {y_train.mean():.1%} | Test win rate: {y_test.mean():.1%}")

# ── RANDOM FOREST ─────────────────────────────────────────────────────────────
print("\nTraining RandomForest ...")
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=20,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
rf.fit(X_train, y_train)
y_prob_train = rf.predict_proba(X_train)[:, 1]
y_prob_test  = rf.predict_proba(X_test)[:, 1]

auc_train = roc_auc_score(y_train, y_prob_train)
auc_test  = roc_auc_score(y_test,  y_prob_test)
print(f"  AUC train={auc_train:.3f} | AUC test={auc_test:.3f}")

# Score all data
df_model = df_model.copy()
df_model["score"] = rf.predict_proba(df_model[FEATURES])[:, 1]

# ── FEATURE IMPORTANCE ────────────────────────────────────────────────────────
feat_imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
print(f"\nTop 10 features:")
for feat, imp in feat_imp.head(10).items():
    print(f"  {feat:<20} {imp:.4f}")

# ── THRESHOLD ANALYSIS ────────────────────────────────────────────────────────
print("\nScore threshold analysis (test set):")
test_df = df_model[test_mask].copy()
print(f"{'Threshold':>10} {'N':>6} {'%Total':>7} {'WinRate':>8} {'AvgProfit':>10} {'MedProfit':>10}")
print("-" * 55)
thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
threshold_stats = []
for thr in thresholds:
    sub = test_df[test_df["score"] >= thr]
    if len(sub) == 0: continue
    stats = {
        "threshold": thr,
        "n": len(sub),
        "pct": len(sub) / len(test_df) * 100,
        "win_rate": (sub[TARGET] > TARGET_PCT).mean() * 100,
        "avg_profit": sub[TARGET].mean(),
        "med_profit": sub[TARGET].median(),
    }
    threshold_stats.append(stats)
    print(f"  >= {thr:.2f}    {stats['n']:>6} {stats['pct']:>6.1f}% "
          f"{stats['win_rate']:>7.1f}% {stats['avg_profit']:>9.1f}% {stats['med_profit']:>9.1f}%")

thr_df = pd.DataFrame(threshold_stats)

# ── UNIVARIATE ANALYSIS: top features ─────────────────────────────────────────
print("\nUnivariate analysis: avg Sell_profit by feature decile")
top_feats = feat_imp.head(6).index.tolist()
univar = {}
for feat in top_feats:
    bins = pd.qcut(df_model[feat], q=5, duplicates="drop")
    grp  = df_model.groupby(bins, observed=True)[TARGET].agg(["mean","count"])
    grp.columns = ["avg_profit","n"]
    univar[feat] = grp

# ── PER-STRATEGY ANALYSIS ─────────────────────────────────────────────────────
strat_perf = df_model.groupby("filter").agg(
    n             = (TARGET, "count"),
    avg_profit    = (TARGET, "mean"),
    med_profit    = (TARGET, "median"),
    win_rate      = ("is_good", "mean"),
    profit_rate   = ("is_profit", "mean"),
    avg_score     = ("score", "mean"),
).sort_values("win_rate", ascending=False)

print("\nStrategy performance:")
print(strat_perf[["n","avg_profit","win_rate","profit_rate","avg_score"]].to_string())

# ── RULE EXTRACTION from top features ─────────────────────────────────────────
# Find best thresholds for top 5 features
print("\n=== Actionable Filter Rules (test set) ===")
print("Conditions derived from top features:\n")

# Build simple interpretable rules
rules = [
    ("strat_tier >= 3 (RSILow30, BuySupport, VolMax1Y, ...)",
     test_df["strat_tier"] >= 3),
    ("D_RSI <= 0.55 (not overbought at entry)",
     test_df["D_RSI"] <= 0.55),
    ("D_MFI <= 60 (MFI not in overbought zone)",
     test_df["D_MFI"] <= 60),
    ("vol_ratio >= 0.8 (adequate volume confirmation)",
     test_df["vol_ratio"] >= 0.8),
    ("rsi_vs_max3m <= 0.85 (RSI below 3M peak = still room to grow)",
     test_df["rsi_vs_max3m"] <= 0.85),
    ("close_vs_lo <= 1.25 (price not far from 3M low = support valid)",
     test_df["close_vs_lo"] <= 1.25),
    ("D_MACD > 0 (positive MACD momentum)",
     test_df["D_MACD"] > 0),
    ("rsi_delta_1w >= 0 (RSI accelerating upward)",
     test_df["rsi_delta_1w"] >= 0),
]

baseline_wr = (test_df[TARGET] > TARGET_PCT).mean()
baseline_avg = test_df[TARGET].mean()
print(f"Baseline (all deals): n={len(test_df):,} | win_rate={baseline_wr:.1%} | avg_profit={baseline_avg:.1f}%\n")

for desc, mask in rules:
    sub = test_df[mask]
    wr  = (sub[TARGET] > TARGET_PCT).mean()
    avg = sub[TARGET].mean()
    med = sub[TARGET].median()
    lift = wr / baseline_wr - 1
    print(f"  {desc}")
    print(f"    n={len(sub):,} ({len(sub)/len(test_df):.0%}) | win_rate={wr:.1%} ({lift:+.0%} lift) "
          f"| avg={avg:.1f}% | med={med:.1f}%")
    print()

# ── COMBINED RULE ─────────────────────────────────────────────────────────────
print("=== COMPOSITE FILTER (best practical combination) ===")
combos = [
    ("Tier3 + RSI<=0.55 + MACD>0",
     (test_df["strat_tier"] >= 3) & (test_df["D_RSI"] <= 0.55) & (test_df["D_MACD"] > 0)),
    ("Tier3 + RSI<=0.55 + MFI<=60",
     (test_df["strat_tier"] >= 3) & (test_df["D_RSI"] <= 0.55) & (test_df["D_MFI"] <= 60)),
    ("Tier2+ + RSI<=0.50 + MACD>0 + MFI<=60",
     (test_df["strat_tier"] >= 2) & (test_df["D_RSI"] <= 0.50)
     & (test_df["D_MACD"] > 0) & (test_df["D_MFI"] <= 60)),
    ("Tier2+ + RSI<=0.55 + rsi_vs_max3m<=0.85 + MACD>0",
     (test_df["strat_tier"] >= 2) & (test_df["D_RSI"] <= 0.55)
     & (test_df["rsi_vs_max3m"] <= 0.85) & (test_df["D_MACD"] > 0)),
    ("Score >= 0.50",
     test_df["score"] >= 0.50),
    ("Score >= 0.45 + Tier2+",
     (test_df["score"] >= 0.45) & (test_df["strat_tier"] >= 2)),
    ("Score >= 0.40 + RSI<=0.55 + MACD>0",
     (test_df["score"] >= 0.40) & (test_df["D_RSI"] <= 0.55) & (test_df["D_MACD"] > 0)),
]
print(f"\n{'Combo':<45} {'N':>5} {'%':>5} {'WinRate':>8} {'Lift':>6} {'Avg':>7} {'Med':>7}")
print("-" * 90)
for name, mask in combos:
    sub = test_df[mask]
    if len(sub) == 0: continue
    wr   = (sub[TARGET] > TARGET_PCT).mean()
    lift = wr / baseline_wr - 1
    avg  = sub[TARGET].mean()
    med  = sub[TARGET].median()
    print(f"  {name:<43} {len(sub):>5} {len(sub)/len(test_df):>4.0%} "
          f"{wr:>7.1%} {lift:>5.0%} {avg:>6.1f}% {med:>6.1f}%")

# ── SAVE SCORED CSV ───────────────────────────────────────────────────────────
save_cols = ["filter","ticker","time","Sell_profit","is_good","score",
             "D_RSI","D_MFI","D_MACD","vol_ratio","close_vs_lo","rsi_vs_max3m",
             "strat_tier","rsi_delta_1w"]
df_model[[c for c in save_cols if c in df_model.columns]].sort_values("score", ascending=False).to_csv(OUT_CSV, index=False)
print(f"\nScored deals saved to: {OUT_CSV}")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 16), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.48, wspace=0.38)

# Panel 1: Feature importance (horizontal bar)
ax1 = fig.add_subplot(gs[0, :2])
imp_sorted = feat_imp.sort_values()
colors1 = [GREEN if i >= len(imp_sorted)-5 else BLUE for i in range(len(imp_sorted))]
bars = ax1.barh(range(len(imp_sorted)), imp_sorted.values, color=colors1, alpha=0.85)
ax1.set_yticks(range(len(imp_sorted)))
ax1.set_yticklabels(imp_sorted.index, fontsize=8)
ax1.set_xlabel("Feature Importance (RandomForest)")
ax1.set_title("Feature Importance\n(top 5 highlighted in green)", color=TEXT_CLR, fontweight="bold")
for bar, val in zip(bars, imp_sorted.values):
    if val > 0.02:
        ax1.text(val + 0.001, bar.get_y() + bar.get_height()/2,
                 f"{val:.3f}", va="center", fontsize=7, color=TEXT_CLR)

# Panel 2: Score → Win rate calibration
ax2 = fig.add_subplot(gs[0, 2])
score_bins = np.arange(0.1, 0.9, 0.05)
wr_by_score, avg_by_score, n_by_score = [], [], []
for lo, hi in zip(score_bins[:-1], score_bins[1:]):
    sub = test_df[(test_df["score"] >= lo) & (test_df["score"] < hi)]
    wr_by_score.append((sub[TARGET] > TARGET_PCT).mean() * 100 if len(sub) > 0 else np.nan)
    avg_by_score.append(sub[TARGET].mean() if len(sub) > 0 else np.nan)
    n_by_score.append(len(sub))
mids = [(a + b) / 2 for a, b in zip(score_bins[:-1], score_bins[1:])]
ax2.bar(mids, wr_by_score, width=0.04, color=BLUE, alpha=0.7, label="Win Rate")
ax2.axhline(baseline_wr * 100, color=RED, linewidth=1.5, linestyle="--",
            label=f"Baseline {baseline_wr:.0%}")
ax2.axhline(50, color=YELLOW, linewidth=1.0, linestyle=":")
ax2.set_xlabel("Predicted Score")
ax2.set_ylabel("Win Rate (%)")
ax2.set_title(f"Score Calibration\n(Win Rate by Score Bucket)", color=TEXT_CLR, fontweight="bold")
ax2.legend(fontsize=8)
ax2.set_ylim(0, 100)

# Panel 3: Strategy win rate comparison
ax3 = fig.add_subplot(gs[0, 3])
top_strats = strat_perf.nlargest(15, "win_rate")
colors3 = [GREEN if t >= 3 else (YELLOW if t >= 2 else RED)
           for t in df_model.groupby("filter")["strat_tier"].first().loc[top_strats.index]]
bars3 = ax3.barh(range(len(top_strats)), top_strats["win_rate"] * 100, color=colors3, alpha=0.85)
ax3.axvline(baseline_wr * 100, color=RED, linewidth=1.2, linestyle="--")
ax3.set_yticks(range(len(top_strats)))
ax3.set_yticklabels([f"{s}\n(n={int(top_strats.loc[s,'n'])})"
                     for s in top_strats.index], fontsize=7)
ax3.set_xlabel("Win Rate (>10%)")
ax3.set_title("Strategy Win Rates\n(green=Tier3, yellow=Tier2)", color=TEXT_CLR, fontweight="bold")
for bar, val in zip(bars3, top_strats["win_rate"]):
    ax3.text(val * 100 + 0.5, bar.get_y() + bar.get_height()/2,
             f"{val:.0%}", va="center", fontsize=7, color=TEXT_CLR)

# Panel 4: Score distribution by outcome (test set)
ax4 = fig.add_subplot(gs[1, :2])
good  = test_df[test_df["is_good"] == 1]["score"]
poor  = test_df[test_df["is_good"] == 0]["score"]
bins4 = np.linspace(0, 1, 30)
ax4.hist(poor,  bins=bins4, alpha=0.6, color=RED,   label=f"Poor deal (<{TARGET_PCT}%)", density=True)
ax4.hist(good,  bins=bins4, alpha=0.6, color=GREEN, label=f"Good deal (>={TARGET_PCT}%)", density=True)
ax4.axvline(0.45, color=YELLOW, linewidth=2, linestyle="--", label="Score=0.45 cutoff")
ax4.set_xlabel("Predicted Score")
ax4.set_ylabel("Density")
ax4.set_title("Score Distribution: Good vs Poor Deals (test set)", color=TEXT_CLR, fontweight="bold")
ax4.legend(fontsize=9)

# Panel 5: Profit distribution by score quartile
ax5 = fig.add_subplot(gs[1, 2:])
test_df["score_quartile"] = pd.qcut(test_df["score"], q=4,
                                     labels=["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"])
quartile_data = [test_df[test_df["score_quartile"] == q][TARGET].values
                 for q in ["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"]]
colors5 = [RED, ORANGE, YELLOW, GREEN]
bp = ax5.boxplot(quartile_data,
                 tick_labels=["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"],
                 patch_artist=True,
                 medianprops=dict(color="white", linewidth=2),
                 flierprops=dict(marker=".", markersize=2, alpha=0.3))
for patch, color in zip(bp["boxes"], colors5):
    patch.set_facecolor(color); patch.set_alpha(0.6)
ax5.axhline(0,         color=TEXT_CLR, linewidth=0.8, linestyle="--")
ax5.axhline(TARGET_PCT,color=YELLOW,   linewidth=0.8, linestyle=":", label=f"+{TARGET_PCT}% target")
ax5.set_ylabel("Sell_profit (%)")
ax5.set_title("Profit Distribution by Score Quartile", color=TEXT_CLR, fontweight="bold")
ax5.set_ylim(-40, 100)
ax5.legend(fontsize=8)
# Add win rate labels
for i, (q_data, color) in enumerate(zip(quartile_data, colors5)):
    wr = (np.array(q_data) > TARGET_PCT).mean()
    ax5.text(i + 1, 80, f"WR\n{wr:.0%}", ha="center", fontsize=9,
             color=color, fontweight="bold")

# Panel 6: Top univariate features — avg profit by quintile
for fi, feat in enumerate(top_feats[:4]):
    ax = fig.add_subplot(gs[2, fi])
    grp = univar[feat].reset_index()
    bars_u = ax.bar(range(len(grp)), grp["avg_profit"],
                    color=[GREEN if v > 5 else (RED if v < 0 else YELLOW)
                           for v in grp["avg_profit"]], alpha=0.85)
    ax.axhline(baseline_avg, color=BLUE, linewidth=1.2, linestyle="--", alpha=0.7)
    ax.axhline(0, color=TEXT_CLR, linewidth=0.6, linestyle=":")
    ax.set_xticks(range(len(grp)))
    ax.set_xticklabels([str(v)[:8] for v in grp[feat]], fontsize=6, rotation=30)
    ax.set_ylabel("Avg Sell_profit (%)", fontsize=8)
    ax.set_title(f"{feat}\n(n per bin shown)", color=TEXT_CLR, fontsize=8)
    for bar, (_, row) in zip(bars_u, grp.iterrows()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{int(row['n'])}", ha="center", fontsize=6, color=TEXT_CLR)

fig.suptitle(
    f"Deal Quality Analysis  |  {len(df_model):,} deals  |  Baseline win rate: {baseline_wr:.1%}  |  "
    f"AUC test: {auc_test:.3f}",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.99
)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: {OUT_IMG}")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY: ACTIONABLE FILTER RULES")
print("="*70)
best_combo_mask = ((test_df["strat_tier"] >= 2) & (test_df["D_RSI"] <= 0.55)
                   & (test_df["rsi_vs_max3m"] <= 0.85) & (test_df["D_MACD"] > 0))
best_sub = test_df[best_combo_mask]
best_wr  = (best_sub[TARGET] > TARGET_PCT).mean()
print(f"""
Best practical filter (test set):
  strat_tier >= 2  (exclude BullDvg, DividendYield, CashCowStock, SuperGrowth, TrendingGrowth)
  D_RSI <= 0.55    (RSI not overbought at entry)
  rsi_vs_max3m <= 0.85  (RSI below 85% of 3-month peak)
  D_MACD > 0       (MACD positive momentum)

  Deals passing filter: {len(best_sub):,} / {len(test_df):,} ({len(best_sub)/len(test_df):.0%})
  Win rate:  {best_wr:.1%}  (vs baseline {baseline_wr:.1%} -> +{best_wr/baseline_wr-1:.0%} lift)
  Avg profit: {best_sub[TARGET].mean():.1f}%  (vs baseline {test_df[TARGET].mean():.1f}%)
  Med profit: {best_sub[TARGET].median():.1f}%  (vs baseline {test_df[TARGET].median():.1f}%)
""")
