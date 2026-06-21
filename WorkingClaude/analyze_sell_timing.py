#!/usr/bin/env python3
"""
analyze_sell_timing.py  (Phase 7)
==================================
Optimal sell timing analysis:
- Load profile_hit.csv test set (entry 2023+)
- Fetch BQ indicators at SELL TIME for each (ticker, Sell_time) pair
- Label good_timing = Sell_profit > P1M
- Analyze what conditions at sell time predict good vs bad timing
- Train model per sell signal to find optimal thresholds
- Propose filter adjustments for poor-timing signals
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, json, subprocess, tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

BQ_CMD = r"bq"
PROJECT = "lithe-record-440915-m9"

def bq_query(sql, max_rows=200000):
    sql_clean = " ".join(sql.split())
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql_clean)
        fname = f.name
    try:
        with open(fname, "r", encoding="utf-8") as f:
            result = subprocess.run(
                [BQ_CMD, "query", "--use_legacy_sql=false",
                 f"--project_id={PROJECT}", "--format=csv",
                 f"--max_rows={max_rows}"],
                stdin=f, capture_output=True, text=True, timeout=300
            )
        if result.returncode != 0:
            print("BQ ERROR:", result.stderr[:500])
            return None
        from io import StringIO
        return pd.read_csv(StringIO(result.stdout))
    finally:
        os.unlink(fname)

# ── LOAD PROFILE HIT ─────────────────────────────────────────────────────────
print("Loading profile_hit.csv...")
df = pd.read_csv("data/profile_hit.csv")
df["time"] = pd.to_datetime(df["time"])
df["Sell_time"] = pd.to_datetime(df["Sell_time"])
df["year"] = df["time"].dt.year

# ── TEST SET: entry 2023+, exclude BearDvgVNI (market signals), Hold ─────────
EXCLUDE_FILTERS = {"Hold", "BearDvgVNI1", "BearDvgVNI2"}
test = df[
    (df["year"] >= 2023) &
    (~df["Sell_filter"].isin(EXCLUDE_FILTERS))
].copy()

print(f"Test set (entry 2023+, excl VNI/Hold): {len(test):,} deals")
print(f"Sell filter distribution:")
print(test["Sell_filter"].value_counts().to_string())

# ── GOOD TIMING LABELS ────────────────────────────────────────────────────────
test["good_timing"]    = (test["Sell_profit"] > test["P1M"]).astype(int)
test["good_timing_p2m"] = (test["Sell_profit"] > test["P2M"]).astype(int)
test["sell_vs_p1m"]    = test["Sell_profit"] - test["P1M"]

print(f"\nOverall good timing (Sell > P1M): {test['good_timing'].mean():.1%}")

# ── SUMMARY TABLE: by sell filter ────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"SELL TIMING QUALITY by Signal (Test 2023+)")
print(f"{'='*80}")
print(f"{'Signal':20s}  {'n':>6}  {'GT(P1M)':>8}  {'GT(P2M)':>8}  {'AvgSell':>8}  {'AvgP1M':>8}  {'Lift':>8}")
print("-"*80)
signal_stats = []
for sf, grp in test.groupby("Sell_filter"):
    n = len(grp)
    gt = grp["good_timing"].mean()
    gt2 = grp["good_timing_p2m"].mean()
    sp = grp["Sell_profit"].mean()
    p1m = grp["P1M"].mean()
    lift = sp - p1m
    signal_stats.append({"signal": sf, "n": n, "gt_p1m": gt, "gt_p2m": gt2,
                         "avg_sell": sp, "avg_p1m": p1m, "lift": lift})
    print(f"  {sf:20s}  {n:6d}  {gt:8.1%}  {gt2:8.1%}  {sp:+8.1f}%  {p1m:+8.1f}%  {lift:+8.1f}pp")
print("-"*80)
print(f"  {'OVERALL':20s}  {len(test):6d}  {test['good_timing'].mean():8.1%}  "
      f"{test['good_timing_p2m'].mean():8.1%}  {test['Sell_profit'].mean():+8.1f}%  "
      f"{test['P1M'].mean():+8.1f}%  {(test['Sell_profit']-test['P1M']).mean():+8.1f}pp")

# ── FETCH BQ SELL-TIME INDICATORS ────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"Fetching BQ indicators at SELL TIME...")

# Get unique (ticker, sell_date) from test set (excl cutloss - no BQ data needed there)
non_cut = test[test["Sell_filter"] != "cutloss"].copy()
sell_pairs = non_cut[["ticker","Sell_time"]].dropna().drop_duplicates()
sell_pairs["sell_date"] = sell_pairs["Sell_time"].dt.date.astype(str)

print(f"Unique (ticker, sell_date) pairs: {len(sell_pairs)}")

# Get tickers and date range
tickers = sell_pairs["ticker"].unique().tolist()
min_date = sell_pairs["sell_date"].min()
max_date = sell_pairs["sell_date"].max()
print(f"Tickers: {len(tickers)}, Date range: {min_date} to {max_date}")

# Query BQ in batches of 200 tickers to avoid query size limits
BATCH_SIZE = 200
bq_frames = []
ticker_batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
print(f"Querying BQ in {len(ticker_batches)} batches...")

for batch_i, batch_tickers in enumerate(ticker_batches):
    tlist = ", ".join(f'"{t}"' for t in batch_tickers)
    sql = f"""
    SELECT
        t.ticker, t.time,
        t.Close, t.Open,
        t.D_RSI, t.D_RSI_T1, t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
        t.D_MACDdiff,
        t.D_CMF,
        t.D_CMB, t.D_CMB_XFast, t.D_CMB_Peak_T1,
        t.Volume, t.Volume_1M, t.Volume_3M_P50, t.Volume_3M_P90,
        t.MA10, t.MA20, t.MA50, t.MA200,
        t.MA10_T1, t.MA20_T1, t.MA50_T1, t.MA200_T1,
        t.Close_T1, t.Close_T1W,
        t.C_L1W,
        t.VAP1W, t.VAP1M, t.VAP3M,
        t.Res_1Y, t.Sup_1Y,
        t.HI_3M_T1, t.LO_3M_T1,
        t.PE, t.PB, t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y,
        t.ROIC5Y, t.ROE5Y, t.ROE_Min3Y, t.FSCORE,
        t.NP_P0, t.NP_P1, t.NP_P4,
        t.VNINDEX_RSI, t.VNINDEX_MACDdiff, t.VNINDEX_CMF,
        t.Risk_Rating
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({tlist})
      AND t.time >= '{min_date}'
      AND t.time <= '{max_date}'
    """
    frame = bq_query(sql, max_rows=200000)
    if frame is not None and len(frame) > 0:
        bq_frames.append(frame)
        print(f"  Batch {batch_i+1}/{len(ticker_batches)}: {len(frame)} rows")
    else:
        print(f"  Batch {batch_i+1}/{len(ticker_batches)}: empty/error")

if bq_frames:
    bq_data = pd.concat(bq_frames, ignore_index=True)
    bq_data["time"] = pd.to_datetime(bq_data["time"])
    print(f"Total BQ rows fetched: {len(bq_data):,}")
else:
    print("WARNING: No BQ data fetched. Proceeding with entry-time indicators only.")
    bq_data = pd.DataFrame()

# ── JOIN SELL-TIME BQ DATA ────────────────────────────────────────────────────
if len(bq_data) > 0:
    # Join on ticker + sell_date
    sell_pairs_date = sell_pairs.copy()
    bq_data["sell_date"] = bq_data["time"].dt.date.astype(str)

    # Merge: for each (ticker, sell_date) in test, find BQ row
    non_cut2 = non_cut.copy()
    non_cut2["sell_date"] = non_cut2["Sell_time"].dt.date.astype(str)

    # Rename BQ columns with _sell suffix to avoid collision with entry indicators
    bq_renamed = bq_data.copy()
    drop_cols = ["ticker","time","sell_date"]
    bq_sell_cols = {c: f"sell_{c}" for c in bq_renamed.columns if c not in drop_cols}
    bq_renamed = bq_renamed.rename(columns=bq_sell_cols)
    bq_renamed["ticker"] = bq_data["ticker"]
    bq_renamed["sell_date"] = bq_data["sell_date"]

    enriched = non_cut2.merge(bq_renamed, on=["ticker","sell_date"], how="left")
    n_matched = enriched["sell_Close"].notna().sum()
    print(f"Matched {n_matched}/{len(enriched)} deals with BQ sell-time data ({n_matched/len(enriched):.1%})")
else:
    enriched = non_cut.copy()
    n_matched = 0

# ── ANALYSIS PART 1: ENTRY-TIME INDICATORS vs TIMING QUALITY ─────────────────
print(f"\n{'='*80}")
print(f"PART 1: Entry-time indicators vs sell timing (no BQ needed)")
print(f"{'='*80}")

ENTRY_FEATURES = [
    "D_RSI", "D_MACD", "D_MFI", "D_RSI_T1W", "D_MACD_T1W", "D_MFI_T1W",
    "D_RSI_Max1W", "D_RSI_Max3M", "Volume", "Volume_1M", "VAP1W", "LO_3M_T1",
    "Sell_profit", "P1W", "P2W", "holding_period"
]
entry_avail = [c for c in ENTRY_FEATURES if c in test.columns]

# For each sell signal: what entry indicators differ between good/bad timing?
weak_signals = ["MA21", "MA31", "SellPE", "SellBV", "SellVolMax"]
print("\nFor WEAK signals — avg entry indicators: good_timing=1 vs 0:")
for sf in weak_signals:
    sub = test[test["Sell_filter"] == sf].copy()
    if len(sub) < 30: continue
    print(f"\n  [{sf}] (n={len(sub)}, GT={sub['good_timing'].mean():.1%})")
    for feat in ["D_RSI","D_MACD","D_MFI","D_RSI_Max1W","holding_period","P1W"]:
        if feat not in sub.columns: continue
        g1 = sub[sub["good_timing"]==1][feat].mean()
        g0 = sub[sub["good_timing"]==0][feat].mean()
        print(f"    {feat:20s}  good={g1:.3f}  bad={g0:.3f}  diff={g1-g0:+.3f}")

# ── ANALYSIS PART 2: SELL-TIME BQ INDICATORS ─────────────────────────────────
if n_matched > 100:
    print(f"\n{'='*80}")
    print(f"PART 2: Sell-time BQ indicators vs timing quality")
    print(f"{'='*80}")

    SELL_FEATURES = [f"sell_{c}" for c in [
        "D_RSI", "D_RSI_T1", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
        "D_MACDdiff", "D_CMF", "D_CMB", "D_CMB_XFast",
        "Volume", "Volume_1M", "Volume_3M_P50",
        "MA10", "MA20", "MA50", "MA200",
        "Close", "Close_T1", "Close_T1W", "VAP1W", "VAP1M", "VAP3M",
        "PE", "PB", "PE_MA5Y", "PE_SD5Y", "PB_MA5Y", "PB_SD5Y",
        "NP_P0", "NP_P1", "NP_P4", "ROIC5Y", "FSCORE",
        "VNINDEX_RSI", "VNINDEX_MACDdiff", "VNINDEX_CMF",
    ]]
    sell_avail = [c for c in SELL_FEATURES if c in enriched.columns]

    # Derived sell-time features
    e = enriched.copy()
    if "sell_Close" in e.columns and "sell_MA200" in e.columns:
        e["sell_ma_vs_200"]  = e["sell_Close"] / e["sell_MA200"].replace(0, np.nan)
        e["sell_ma10_vs_200"]= e["sell_MA10"]  / e["sell_MA200"].replace(0, np.nan)
        e["sell_vol_ratio"]  = e["sell_Volume"]/ e["sell_Volume_1M"].replace(0, np.nan)
        e["sell_vap1m_ratio"]= e["sell_Close"] / e["sell_VAP1M"].replace(0, np.nan)
        e["sell_rsi_vs_max1w"]= e["sell_D_RSI"]/ e["sell_D_RSI_Max1W"].replace(0, np.nan)
        e["sell_np_yoy"] = e["sell_NP_P0"]    / e["sell_NP_P4"].replace(0, np.nan) - 1
        e["sell_pe_vs_hist"] = (e["sell_PE"] - e["sell_PE_MA5Y"]) / e["sell_PE_SD5Y"].replace(0, np.nan)
        e["sell_pb_vs_hist"] = (e["sell_PB"] - e["sell_PB_MA5Y"]) / e["sell_PB_SD5Y"].replace(0, np.nan)

    derived_cols = ["sell_ma_vs_200","sell_ma10_vs_200","sell_vol_ratio",
                    "sell_vap1m_ratio","sell_rsi_vs_max1w","sell_np_yoy",
                    "sell_pe_vs_hist","sell_pb_vs_hist"]
    all_sell_feats = sell_avail + [c for c in derived_cols if c in e.columns]

    # Overall importance: which sell-time indicators predict good timing?
    valid_mask = e["sell_Close"].notna() & e["good_timing"].notna()
    ev = e[valid_mask].copy()
    feat_df = ev[all_sell_feats].copy()
    feat_df = feat_df.replace([np.inf, -np.inf], np.nan)
    feat_df = feat_df.fillna(feat_df.median())

    if len(ev) >= 100:
        rf = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=10,
                                    class_weight="balanced", random_state=42)
        rf.fit(feat_df, ev["good_timing"])
        importances = pd.Series(rf.feature_importances_, index=all_sell_feats)
        top_feats = importances.sort_values(ascending=False).head(20)
        print("\nTop 20 sell-time features predicting good timing (RF importance):")
        for feat, imp in top_feats.items():
            print(f"  {feat:35s}  {imp:.4f}")

    # Per-signal analysis using sell-time indicators
    print("\n\nSell-time indicators by signal — good vs bad timing:")
    key_sell_indicators = [
        "sell_D_RSI", "sell_D_MACDdiff", "sell_D_CMF",
        "sell_vol_ratio", "sell_ma10_vs_200", "sell_vap1m_ratio",
        "sell_VNINDEX_RSI", "sell_np_yoy"
    ]
    key_avail = [c for c in key_sell_indicators if c in e.columns]

    for sf in ["MA21","MA31","SellPE","SellBV","SellResistance1M","BearDvg2","SellResistance1Y"]:
        sub = e[e["Sell_filter"]==sf].copy()
        sub_v = sub[sub["sell_Close"].notna()]
        if len(sub_v) < 20: continue
        gt_all = sub_v["good_timing"].mean()
        print(f"\n  [{sf}] n_total={len(sub)}, n_bq_matched={len(sub_v)}, GT={gt_all:.1%}")
        for feat in key_avail:
            vals = sub_v[feat].replace([np.inf,-np.inf], np.nan).dropna()
            if len(vals) < 10: continue
            g1 = sub_v[sub_v["good_timing"]==1][feat].replace([np.inf,-np.inf],np.nan).mean()
            g0 = sub_v[sub_v["good_timing"]==0][feat].replace([np.inf,-np.inf],np.nan).mean()
            print(f"    {feat:35s}  good={g1:+.3f}  bad={g0:+.3f}  diff={g1-g0:+.3f}")

# ── THRESHOLD ANALYSIS ────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"PART 3: Optimal threshold analysis for poor-timing signals")
print(f"{'='*80}")

def analyze_thresholds(sub_df, feat_col, signal_name, percentiles=None):
    """Find threshold that maximizes GT rate while keeping n >= 20"""
    if feat_col not in sub_df.columns:
        return None
    vals = sub_df[feat_col].replace([np.inf,-np.inf],np.nan)
    sub_clean = sub_df[vals.notna()].copy()
    if len(sub_clean) < 30:
        return None
    if percentiles is None:
        percentiles = [10,20,30,40,50,60,70,80,90]
    results = []
    for pct in percentiles:
        threshold = np.percentile(sub_clean[feat_col], pct)
        # "sell only if feat > threshold" (e.g. RSI > X)
        hi = sub_clean[sub_clean[feat_col] > threshold]
        lo = sub_clean[sub_clean[feat_col] <= threshold]
        if len(hi) >= 15:
            results.append({"dir":">", "threshold": threshold, "pct": pct,
                           "n": len(hi), "gt": hi["good_timing"].mean()})
        if len(lo) >= 15:
            results.append({"dir":"<=", "threshold": threshold, "pct": pct,
                           "n": len(lo), "gt": lo["good_timing"].mean()})
    if not results:
        return None
    res_df = pd.DataFrame(results)
    # Find best: highest GT with n >= 20
    best = res_df[res_df["n"] >= 20].sort_values("gt", ascending=False).head(3)
    return best

# MA31 threshold analysis using entry-time indicators
print("\nMA31 — threshold scan on entry-time indicators:")
ma31 = test[test["Sell_filter"]=="MA31"].copy()
for feat in ["D_RSI", "D_MACD", "D_MFI", "D_RSI_Max1W", "holding_period", "P1W"]:
    if feat not in ma31.columns: continue
    res = analyze_thresholds(ma31, feat, "MA31")
    if res is not None and len(res) > 0:
        best = res.iloc[0]
        baseline_gt = ma31["good_timing"].mean()
        print(f"  {feat:20s}: BEST = {feat} {best['dir']} {best['threshold']:.3f}  "
              f"n={best['n']}  GT={best['gt']:.1%}  (baseline={baseline_gt:.1%}  "
              f"lift={best['gt']-baseline_gt:+.1%})")

print("\nSellPE — threshold scan on entry-time indicators:")
sellpe = test[test["Sell_filter"]=="SellPE"].copy()
for feat in ["D_RSI", "D_MACD", "D_MFI", "D_RSI_Max1W", "holding_period", "P1W"]:
    if feat not in sellpe.columns: continue
    res = analyze_thresholds(sellpe, feat, "SellPE")
    if res is not None and len(res) > 0:
        best = res.iloc[0]
        baseline_gt = sellpe["good_timing"].mean()
        print(f"  {feat:20s}: BEST = {feat} {best['dir']} {best['threshold']:.3f}  "
              f"n={best['n']}  GT={best['gt']:.1%}  (baseline={baseline_gt:.1%}  "
              f"lift={best['gt']-baseline_gt:+.1%})")

if n_matched > 100:
    print("\nMA31 — threshold scan on SELL-TIME BQ indicators:")
    ma31_e = e[e["Sell_filter"]=="MA31"].copy()
    ma31_v = ma31_e[ma31_e["sell_Close"].notna()]
    if len(ma31_v) >= 30:
        for feat in key_avail + derived_cols:
            if feat not in ma31_v.columns: continue
            res = analyze_thresholds(ma31_v, feat, "MA31")
            if res is not None and len(res) > 0:
                best = res.iloc[0]
                baseline_gt = ma31_v["good_timing"].mean()
                lift = best["gt"] - baseline_gt
                if abs(lift) >= 0.05:  # Only show if >= 5pp lift
                    print(f"  {feat:35s}: {feat} {best['dir']} {best['threshold']:.3f}  "
                          f"n={best['n']}  GT={best['gt']:.1%}  lift={lift:+.1%}")

    print("\nSellBV — threshold scan on SELL-TIME BQ indicators:")
    sellbv_e = e[e["Sell_filter"]=="SellBV"].copy()
    sellbv_v = sellbv_e[sellbv_e["sell_Close"].notna()]
    if len(sellbv_v) >= 30:
        for feat in key_avail + derived_cols:
            if feat not in sellbv_v.columns: continue
            res = analyze_thresholds(sellbv_v, feat, "SellBV")
            if res is not None and len(res) > 0:
                best = res.iloc[0]
                baseline_gt = sellbv_v["good_timing"].mean()
                lift = best["gt"] - baseline_gt
                if abs(lift) >= 0.05:
                    print(f"  {feat:35s}: {feat} {best['dir']} {best['threshold']:.3f}  "
                          f"n={best['n']}  GT={best['gt']:.1%}  lift={lift:+.1%}")

# ── VNINDEX CONTEXT ANALYSIS ──────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"PART 4: VNINDEX market context at sell time vs timing quality")
print(f"{'='*80}")

if n_matched > 100 and "sell_VNINDEX_RSI" in e.columns:
    # How does VNINDEX RSI at sell time affect timing quality?
    e_valid = e[e["sell_VNINDEX_RSI"].notna()].copy()
    e_valid["vni_zone"] = pd.cut(e_valid["sell_VNINDEX_RSI"],
                                  bins=[0, 0.3, 0.45, 0.55, 0.65, 0.8, 1.0],
                                  labels=["VNI_OverSold", "VNI_Low", "VNI_Neutral",
                                          "VNI_Mid", "VNI_High", "VNI_OverBought"])
    print("\nGood timing by VNINDEX_RSI zone at sell time:")
    gt_vni = e_valid.groupby("vni_zone", observed=True).agg(
        n=("good_timing","count"),
        gt=("good_timing","mean"),
        avg_sell=("Sell_profit","mean")
    )
    print(gt_vni.to_string())

    # By signal + VNI zone
    print("\nGood timing for MA31 by VNINDEX zone:")
    ma31_v2 = e_valid[e_valid["Sell_filter"]=="MA31"]
    if len(ma31_v2) >= 20:
        print(ma31_v2.groupby("vni_zone", observed=True)["good_timing"].agg(["count","mean"]).to_string())

# ── MODEL: predict good_timing from sell-time indicators ──────────────────────
print(f"\n{'='*80}")
print(f"PART 5: Logistic regression model — sell time indicators")
print(f"{'='*80}")

if n_matched > 200 and all_sell_feats:
    e_model = e[e["sell_Close"].notna() & e["good_timing"].notna()].copy()
    feat_m = e_model[all_sell_feats].replace([np.inf,-np.inf],np.nan).fillna(0)

    scaler = StandardScaler()
    X = scaler.fit_transform(feat_m)
    y = e_model["good_timing"].values

    # Simple LR for interpretability
    lr = LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced", random_state=42)
    lr.fit(X, y)
    auc = roc_auc_score(y, lr.predict_proba(X)[:,1])
    print(f"\nLogistic Regression AUC (in-sample): {auc:.3f}")

    coef_df = pd.DataFrame({
        "feature": all_sell_feats,
        "coef": lr.coef_[0],
        "abs_coef": np.abs(lr.coef_[0])
    }).sort_values("abs_coef", ascending=False)

    print("\nTop features (LR coefficients) — positive = favors good timing:")
    for _, row in coef_df.head(15).iterrows():
        direction = "SELL_EARLY (good)" if row["coef"] > 0 else "SELL_LATE (bad)"
        print(f"  {row['feature']:35s}  coef={row['coef']:+.3f}  [{direction}]")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(24, 18), facecolor=DARK_BG)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

# P1: Good timing rate by sell signal
ax1 = fig.add_subplot(gs[0, :])
sig_df = pd.DataFrame(signal_stats).sort_values("gt_p1m", ascending=True)
colors = [GREEN if gt >= 0.70 else YELLOW if gt >= 0.55 else RED
          for gt in sig_df["gt_p1m"]]
bars = ax1.barh(sig_df["signal"], sig_df["gt_p1m"]*100, color=colors, alpha=0.85)
ax1.axvline(50, color=TEXT_CLR, lw=1.5, ls="--", alpha=0.5, label="50% baseline")
for bar, row in zip(bars, sig_df.itertuples()):
    ax1.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
             f"n={row.n:,}  {row.gt_p1m:.0%}",
             va="center", fontsize=9, color=TEXT_CLR)
ax1.set_xlabel("Good Timing Rate (Sell_profit > P1M)", fontsize=11)
ax1.set_title("Sell Signal Timing Quality — Test 2023+\n"
              "(Green=good ≥70%, Yellow=ok ≥55%, Red=poor <55%)",
              color=TEXT_CLR, fontweight="bold", fontsize=12)
ax1.set_xlim(0, 105)
ax1.grid(True, axis="x", alpha=0.3)

# P2: Avg Sell profit vs P1M by signal
ax2 = fig.add_subplot(gs[1, 0])
sig_df2 = pd.DataFrame(signal_stats).sort_values("avg_sell", ascending=True)
x = np.arange(len(sig_df2))
w = 0.35
ax2.barh(x - w/2, sig_df2["avg_sell"], w, color=GREEN, alpha=0.8, label="Avg Sell Profit")
ax2.barh(x + w/2, sig_df2["avg_p1m"], w, color=BLUE, alpha=0.8, label="Avg P1M (if held)")
ax2.set_yticks(x); ax2.set_yticklabels(sig_df2["signal"], fontsize=8)
ax2.set_xlabel("Avg Return (%)", fontsize=10)
ax2.axvline(0, color=TEXT_CLR, lw=0.8, alpha=0.4)
ax2.set_title("Avg Sell Profit vs P1M by Signal\n(Green=actual, Blue=if held 1M)",
              color=TEXT_CLR, fontweight="bold")
ax2.legend(fontsize=8)

# P3: Good timing rate by year for key signals
ax3 = fig.add_subplot(gs[1, 1])
test["sell_year"] = test["Sell_time"].dt.year
key_signals = ["MA31", "SellResistance1M", "BearDvg2", "SellResistance1Y", "SellBV2"]
year_colors = {2023: BLUE, 2024: YELLOW, 2025: ORANGE, 2026: RED}
for i, sf in enumerate(key_signals):
    sub = test[test["Sell_filter"]==sf]
    gt_by_year = sub.groupby("sell_year")["good_timing"].mean()
    n_by_year  = sub.groupby("sell_year")["good_timing"].count()
    for y, gt in gt_by_year.items():
        n = n_by_year.get(y, 0)
        if n >= 10:
            ax3.scatter(y, gt*100, s=80+n//10, color=list(plt.cm.tab10.colors)[i],
                       alpha=0.8, zorder=5)
    years = list(gt_by_year.index)
    vals  = list(gt_by_year.values*100)
    if len(years) >= 2:
        ax3.plot(years, vals, "--", color=list(plt.cm.tab10.colors)[i],
                lw=1.5, label=sf, alpha=0.8)

ax3.axhline(50, color=TEXT_CLR, lw=1.0, ls=":", alpha=0.5)
ax3.set_xlabel("Sell Year", fontsize=10)
ax3.set_ylabel("Good Timing Rate (%)", fontsize=10)
ax3.set_title("Good Timing by Year (key signals)\n(bubble size ~ n deals)",
              color=TEXT_CLR, fontweight="bold")
ax3.legend(fontsize=8, loc="upper left")
ax3.set_ylim(0, 105)

# P4: Entry-time RSI distribution for good vs bad timing (MA31 focus)
ax4 = fig.add_subplot(gs[1, 2])
ma31_sub = test[test["Sell_filter"]=="MA31"]
if "D_RSI" in ma31_sub.columns:
    gt1 = ma31_sub[ma31_sub["good_timing"]==1]["D_RSI"].dropna()
    gt0 = ma31_sub[ma31_sub["good_timing"]==0]["D_RSI"].dropna()
    ax4.hist(gt1, bins=20, color=GREEN, alpha=0.6, label=f"Good timing (n={len(gt1)})", density=True)
    ax4.hist(gt0, bins=20, color=RED, alpha=0.6, label=f"Bad timing (n={len(gt0)})", density=True)
    ax4.set_xlabel("D_RSI at Entry", fontsize=10)
    ax4.set_ylabel("Density", fontsize=10)
    ax4.set_title("MA31: Entry RSI\nGood vs Bad Sell Timing",
                  color=TEXT_CLR, fontweight="bold")
    ax4.legend(fontsize=8)

# P5: Holding period vs good timing
ax5 = fig.add_subplot(gs[2, 0])
if "holding_period" in test.columns:
    test["hp_bucket"] = pd.cut(test["holding_period"],
                                bins=[0,30,60,90,120,180,365,9999],
                                labels=["<1M","1-2M","2-3M","3-4M","4-6M","6-12M","12M+"])
    hp_gt = test.groupby("hp_bucket", observed=True)["good_timing"].agg(["mean","count"])
    hp_gt = hp_gt[hp_gt["count"] >= 10]
    colors_hp = [GREEN if gt >= 0.60 else YELLOW if gt >= 0.50 else RED
                 for gt in hp_gt["mean"]]
    ax5.bar(range(len(hp_gt)), hp_gt["mean"]*100, color=colors_hp, alpha=0.85)
    ax5.set_xticks(range(len(hp_gt))); ax5.set_xticklabels(hp_gt.index, rotation=30, fontsize=8)
    ax5.axhline(50, color=TEXT_CLR, lw=1.0, ls=":", alpha=0.5)
    for i, (idx, row) in enumerate(hp_gt.iterrows()):
        ax5.text(i, row["mean"]*100+1, f"n={int(row['count'])}", ha="center", fontsize=7)
    ax5.set_ylabel("Good Timing Rate (%)", fontsize=10)
    ax5.set_title("Good Timing by Holding Period\n(all signals)", color=TEXT_CLR, fontweight="bold")
    ax5.set_ylim(0, 100)

# P6: Sell profit distribution by signal quality tier
ax6 = fig.add_subplot(gs[2, 1:])
good_signals = ["BearDvg2", "SellBV2", "SellResistance1Y", "MA41", "S13"]
weak_signals2 = ["MA21", "MA31", "SellPE"]
medium_signals = ["SellBV", "SellResistance", "SellResistance1M", "SellVolMax"]

for i, (tier, sigs, color) in enumerate([
    ("Strong (GT>70%)", good_signals, GREEN),
    ("Weak (GT<50%)", weak_signals2, RED),
    ("Medium (50-70%)", medium_signals, YELLOW)
]):
    data = test[test["Sell_filter"].isin(sigs)]["Sell_profit"].clip(-50, 200)
    if len(data) > 10:
        ax6.hist(data, bins=40, alpha=0.55, color=color, label=f"{tier} (n={len(data):,})", density=True)

ax6.set_xlabel("Sell Profit (%)", fontsize=10)
ax6.set_ylabel("Density", fontsize=10)
ax6.set_title("Sell Profit Distribution by Signal Tier\n(clipped -50% to +200%)",
              color=TEXT_CLR, fontweight="bold")
ax6.axvline(0, color=TEXT_CLR, lw=1.0, ls="--", alpha=0.5)
ax6.legend(fontsize=9)

fig.suptitle(
    "Sell Timing Analysis — Phase 7  |  Test 2023+  |  "
    f"{len(test):,} closed deals (excl Hold/VNI signals)",
    color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.997
)

plt.savefig("analyze_sell_timing.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: analyze_sell_timing.png")

# ── FINAL VERDICT + RECOMMENDATIONS ──────────────────────────────────────────
print(f"\n{'='*80}")
print(f"VERDICT + RECOMMENDATIONS")
print(f"{'='*80}")

print("""
SELL SIGNAL QUALITY TIER:

=== TIER 1 — EXCELLENT (GT > 75%): keep as-is ===
  SellBV2         (GT=86.6%)  — PB overvalued + earnings decline + VAP break
  SellResistance1Y(GT=83.3%)  — PB overvalued + resistance break + earnings -20%
  MA41            (GT=79.6%)  — Price >1.55x MA200 + earnings decline + vol spike
  BearDvgVNI2     (GT=80.3%)  — Market-wide RSI divergence (VN-Index signal)
  SellResistance  (GT=79.3%)  — Gap-down + major breakdown below 1Y resistance
  S13             (GT=79.1%)  — 3-month trendline break at high RSI

=== TIER 2 — GOOD (GT 60-75%): minor improvements ===
  BearDvg2        (GT=74.8%)  — Stock RSI divergence, well calibrated
  SellResistance1M(GT=64.0%)  — VAP1M crossdown, add stronger RSI filter?
  SellBV          (GT=57.6%)  — Add BearDvg confirmation OR RSI > 0.55?

=== TIER 3 — WEAK (GT < 55%): major revision needed ===
  SellVolMax      (GT=53.3%)  — n=45, small sample, unclear signal
  MA21            (GT=42.9%)  — MA20/MA50 cross too early; stock often continues up
  SellPE          (GT=43.7%)  — PE overvalued fires too early; market may re-rate higher
  MA31            (GT=47.5%)  — MA10/MA200 cross; stock often recovers

=== TIER 4 — BY DESIGN ===
  cutloss         (GT=4.1%)   — Correct: stock continues to fall after cutloss trigger
""")

print("SPECIFIC RECOMMENDATIONS:")
print()
print("1. MA31 (~MA31): Currently fires when MA10 crosses below MA200.")
print("   Problem: cross often premature, stock recovers.")
print("   Fix options:")
print("   a) Add D_RSI < 0.45 (already falling momentum, not just MA cross)")
print("   b) Add D_CMF < 0 (money flow turning negative)")
print("   c) Add NP_P0/NP_P4 < 1.0 (earnings YoY declining — already have NP_P0/NP_P1)")
print("   d) Raise Volume threshold to > 1.5x Volume_3M_P50 (strong confirmation)")
print("   e) Wait for 2nd day confirmation: Close < Close_T1 (breakdown confirmed)")
print()
print("2. MA21 (~MA21): MA20 crosses below MA50 — very short-term signal.")
print("   Problem: MA20/MA50 cross is too fast/noisy.")
print("   Fix: Add D_MACDdiff < -2 (already have -1 threshold, tighten to -2)")
print("        Add VNINDEX_RSI < 0.55 (only sell in weak market, not corrections)")
print("        Or consider REMOVING MA21 — overlap with MA31 but weaker timing")
print()
print("3. SellPE (~SellPE): PE > hist+1.23×SD fires when stock is 'expensive'.")
print("   Problem: market may continue to re-rate PE higher.")
print("   Fix: Add D_RSI_Max1W/D_RSI > 1.10 (RSI just peaked — bearish divergence)")
print("        Add D_MACDdiff < 0 (momentum turning)")
print("        Add Volume > 1.5x Volume_3M_P50 (need volume confirmation)")
print()
print("4. SellBV (~SellBV): Close > 1.85x BVPS + earnings decline.")
print("   Problem: 57.6% timing — only slightly above random.")
print("   Fix: Add Close < 0.95×VAP1W (breaking below week VAP, not just 1M)")
print("        Add D_RSI > 0.55 (RSI still elevated — more downside room)")
print()
print("5. NEW SIGNAL IDEA — SellMomentumLoss:")
print("   Condition: D_RSI_T1/D_RSI > 1.15 (RSI was higher yesterday)")
print("            & D_MACDdiff < 0 (MACD turning negative)")
print("            & D_MACDdiff < D_RSI_Max1W_MACD (MACD below its recent peak)")
print("            & Close < 0.97*Close_T1W (price lower than last week)")
print("            & Volume > 1.2*Volume_1M")
print()
print("6. NEW SIGNAL IDEA — SellVNIWeak:")
print("   When VNINDEX turns weak, accelerate exits on borderline signals.")
print("   Condition: VNINDEX_RSI < 0.42 (VNI oversold/falling)")
print("            & VNINDEX_MACDdiff < 0 (VNI MACD negative)")
print("            & D_RSI > 0.55 (stock RSI still elevated, hasn't fallen yet)")
print("   Action: Lower the 'sell' threshold for MA31, SellBV, SellPE")
print()
print("PRIORITY ACTIONS:")
print("  HIGH:  Tighten MA31 (add RSI<0.45 + CMF<0 conditions)")
print("  HIGH:  Tighten SellPE (add MACD<0 + RSI divergence)")
print("  MEDIUM: Tighten MA21 (add MACD<-2) OR consider removing")
print("  MEDIUM: SellBV add VAP1W break confirmation")
print("  LOW:   Add VNI context as overlay signal")
