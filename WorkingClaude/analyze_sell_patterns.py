#!/usr/bin/env python3
"""
analyze_sell_patterns.py
========================
1. Phân tích hiệu quả các pattern bán từ profile_hit.csv
2. Validate trên BigQuery (2020-2025): sau khi signal bán fire,
   cổ phiếu đi lên hay đi xuống?
3. Đề xuất pattern bán mới/cải thiện

Metrics chính:
  - "Good timing": Sell_profit > P1M (bán ở mức tốt hơn nếu giữ 1 tháng)
  - Forward return analysis: avg return 1W/1M/2M/3M AFTER signal fires
  - A good sell signal: ret_1m < 0 (stock falls after sell)
  - A bad sell signal: ret_1m > 0 (stock rises after sell = sold too early)
"""

import warnings
warnings.filterwarnings("ignore")

import json
import os
import subprocess
import tempfile
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# ── CONFIG ────────────────────────────────────────────────────────────────────
PROFILE_FILE = "data/profile_hit.csv"
PROJECT      = "lithe-record-440915-m9"
BQ_BIN       = r"bq"
OUT_IMG      = "analyze_sell_patterns.png"
BQ_DATE_FROM = "2020-01-01"
BQ_DATE_TO   = "2025-12-31"

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0"; GREEN = "#4ecb71"
RED = "#e05c5c"; YELLOW = "#f0c060"; ORANGE = "#f0904a"; PURPLE = "#b57bee"
TEAL = "#4ecbbb"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor": GRID_CLR, "axes.labelcolor": TEXT_CLR,
    "xtick.color": TEXT_CLR, "ytick.color": TEXT_CLR,
    "text.color": TEXT_CLR, "grid.color": GRID_CLR,
    "grid.linestyle": "--", "grid.alpha": 0.4,
    "font.family": "DejaVu Sans",
})

# ── BQ HELPER ─────────────────────────────────────────────────────────────────
def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql); tmppath = f.name
    try:
        cmd = (f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=5000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmppath)
        except: pass
    if r.returncode != 0:
        print(f"  [BQ ERROR] {label}: {r.stdout[:300]}")
        return None
    txt = r.stdout.strip()
    if not txt:
        return pd.DataFrame()
    try:
        return pd.read_csv(StringIO(txt))
    except Exception:
        return pd.DataFrame()

# ── PART 1: PROFILE HIT ANALYSIS ─────────────────────────────────────────────
print("=" * 70)
print("PART 1: Sell Pattern Effectiveness (profile_hit.csv)")
print("=" * 70)

df = pd.read_csv(PROFILE_FILE)
df["time"] = pd.to_datetime(df["time"])
closed = df[df["Sell_filter"] != "Hold"].copy()

# For each Sell_filter: timing quality
# Good timing = Sell_profit > P1M (sold at higher price than 1M forward return from buy)
print(f"\nBaseline: n={len(closed):,} closed deals")
print(f"{'Sell Signal':<20} {'n':>5} {'Sell%':>7} {'P1M%':>7} {'P3M%':>7} "
      f"{'Good%':>7} {'Cnt>0%':>7} {'Grade':>6}")
print("-" * 70)

signal_stats = {}
for sf, grp in sorted(closed.groupby("Sell_filter"),
                       key=lambda x: len(x[1]), reverse=True):
    sp   = grp["Sell_profit"].mean()
    p1m  = grp["P1M"].mean()
    p3m  = grp["P3M"].fillna(grp["P1M"]).mean()
    good = (grp["Sell_profit"] > grp["P1M"]).mean()   # sold better than hold 1M more
    pos  = (grp["Sell_profit"] > 0).mean()

    # Grade: A = timing good + profit, B = timing ok, C = timing bad
    if good >= 0.70 and sp > 5:   grade = " A"
    elif good >= 0.55:             grade = " B"
    elif good >= 0.40:             grade = " C"
    else:                          grade = " D"

    signal_stats[sf] = {"n": len(grp), "sell": sp, "p1m": p1m, "p3m": p3m,
                         "good": good, "pos": pos, "grade": grade}
    print(f"  {sf:<20} {len(grp):>5} {sp:>+7.1f}% {p1m:>+7.1f}% {p3m:>+7.1f}% "
          f"{good:>6.0%} {pos:>6.0%} {grade:>6}")

# Cutloss analysis
print(f"\n--- Cutloss detail ---")
cl = closed[closed["Sell_filter"] == "cutloss"]
print(f"  After cutloss, stock RECOVERED (P1M > sell): {(cl['P1M'] > cl['Sell_profit']).mean():.0%}")
print(f"  After cutloss, stock fell MORE (P1M < sell): {(cl['P1M'] < cl['Sell_profit']).mean():.0%}")
print(f"  Avg loss at cutloss: {cl['Sell_profit'].mean():.1f}%")

# SellVolMax problem
print(f"\n--- SellVolMax detail ---")
svm = closed[closed["Sell_filter"] == "SellVolMax"]
print(f"  After SellVolMax, stock ROSE (P1M > sell): {(svm['P1M'] > svm['Sell_profit']).mean():.0%}")
print(f"  Stock gained >10% after SellVolMax: {(svm['P1M'] > 10).mean():.0%}")
print(f"  Stock gained >20% after SellVolMax: {(svm['P1M'] > 20).mean():.0%}")

# ── PART 2: BQ FORWARD RETURN ANALYSIS ───────────────────────────────────────
print("\n" + "="*70)
print("PART 2: BigQuery Forward-Return Validation (2020-2025)")
print("="*70)
print("Testing each sell signal: does stock fall AFTER signal fires?")
print("A good signal -> negative forward return (sold at the right time)")

# Build a single big query with LEAD() for all signals at once
# This is efficient: one table scan, compute forward returns with LEAD()
# Then evaluate each signal's WHERE clause

SELL_SIGNALS = {
    # Note: use SAFE_DIVIDE() for all divisions to avoid zero-division
    # MA200_T1 does NOT exist in BQ (only MA10_T1, MA20_T1, MA50_T1)
    "MA31": """
        SAFE_DIVIDE(t.MA10, t.MA200) < 1.05
        AND SAFE_DIVIDE(t.MA10_T1, t.MA50_T1) > 1.05
        AND SAFE_DIVIDE(t.Close, NULLIF(t.Close_T1W,0)) < 1.03
        AND SAFE_DIVIDE(t.D_RSI, NULLIF(t.D_RSI_T1W,0)) < 0.90
        AND t.D_RSI < 0.62
        AND t.D_MACDdiff < -1.0
        AND t.Volume > 0.99*t.Volume_3M_P50""",

    "MA41": """
        t.Close > 1.55*t.MA200
        AND SAFE_DIVIDE(t.NP_P0, NULLIF(t.NP_P1,0)) < 0.92
        AND t.Volume > 1.17*t.Volume_3M_P50
        AND SAFE_DIVIDE(t.Close, NULLIF(t.Close_T1W,0)) < 1.0
        AND t.Close < 1.05*t.VAP1M""",

    "SellBV": """
        t.Close > 1.85*t.BVPS
        AND SAFE_DIVIDE(t.NP_P0, NULLIF(t.NP_P1,0)) < 0.91
        AND t.Close < 0.97*t.VAP1M
        AND t.Close_T1W > 0.92*t.VAP1M
        AND t.Volume > 0.95*t.Volume_3M_P50""",

    "SellBV2": """
        t.PB > 1.23*t.PB_MA5Y + 0.84*t.PB_SD5Y
        AND SAFE_DIVIDE(t.NP_P0, NULLIF(t.NP_P1,0)) < 0.62
        AND t.Close < 0.99*t.VAP1M
        AND t.Close_T1W > 0.80*t.VAP1M
        AND t.D_RSI > 0.28
        AND t.Volume > 1.01*t.Volume_3M_P50""",

    "SellPE": """
        t.PE >= 1.25*t.PE_MA5Y + 1.23*t.PE_SD5Y
        AND SAFE_DIVIDE(t.NP_P0, NULLIF(t.NP_P1,0)) < 1.01
        AND t.Close < 0.98*t.VAP3M
        AND t.Close_T1W > 0.89*t.VAP3M
        AND t.Volume > 1.24*t.Volume_3M_P50""",

    "SellResistance": """
        SAFE_DIVIDE(t.Open, NULLIF(t.Close,0)) < 0.95
        AND t.Close < 0.80*t.Res_1Y
        AND SAFE_DIVIDE(t.Close, NULLIF(t.LO_3M_T1,0)) > 1.58
        AND t.Volume > 2.47*t.Volume_3M_P50""",

    "BearDvg2": """
        SAFE_DIVIDE(t.D_RSI_Max1W, NULLIF(t.D_RSI,0)) > 0.88
        AND SAFE_DIVIDE(t.D_RSI_T1, NULLIF(t.D_RSI,0)) > 1.11
        AND t.D_RSI_Max3M > 0.66
        AND t.D_RSI_Max1W < 0.76
        AND t.D_RSI_Max1W > 0.57
        AND SAFE_DIVIDE(t.D_RSI_Max1W_Close, NULLIF(t.D_RSI_Max3M_Close,0)) > 1.12
        AND SAFE_DIVIDE(t.D_RSI_Max3M_MACD, NULLIF(t.D_RSI_Max1W_MACD,0)) > 1.29
        AND t.Volume > 1.11*t.Volume_1M
        AND SAFE_DIVIDE(t.D_RSI_Max3M, NULLIF(t.D_RSI_Max1W,0)) > 1.21""",

    "SellVolMax": """
        SAFE_DIVIDE(t.Close, NULLIF(t.Volume_MaxTop5_2Y_Close,0)) < 0.84
        AND t.ID_Current - t.Volume_MaxTop5_2Y_ID <= 128.0
        AND t.Close < 1.17*t.VAP1W
        AND t.D_RSI < 0.55
        AND SAFE_DIVIDE(t.Close, NULLIF(t.Close_T1,0)) < 1.10
        AND SAFE_DIVIDE(t.D_RSI, NULLIF(t.D_RSI_T1W,0)) < 1.03
        AND SAFE_DIVIDE(t.Close_T1, NULLIF(t.LO_3M_T1,0)) > 1.59""",

    # ── NEW PROPOSED SIGNALS ──────────────────────────────────────────────────
    # NEW1: RSI Peak Exit (overbought + declining momentum + MACD turning)
    "NEW_RSI_Peak": """
        t.D_RSI > 0.72
        AND t.D_RSI_T1 > t.D_RSI
        AND t.D_RSI_Max1W < t.D_RSI_Max3M
        AND t.D_MACDdiff < 0
        AND t.Volume > 0.80*t.Volume_3M_P50""",

    # NEW2: VAP Breakdown + Volume Distribution
    "NEW_VAP_Break": """
        t.Close < 0.97*t.VAP1M
        AND t.Close_T1W >= 0.97*t.VAP1M
        AND t.Volume > 1.80*t.Volume_3M_P50
        AND t.Close < t.Open
        AND t.D_RSI > 0.40""",

    # NEW3: MA10 x MA20 Death Cross + Volume confirmation
    "NEW_MA_DeathX": """
        t.MA10 < t.MA20
        AND t.MA10_T1 >= t.MA20_T1
        AND t.Volume > 1.20*t.Volume_3M_P50
        AND t.D_RSI < 0.65
        AND t.Close < t.VAP1M""",

    # NEW4: SellVolMax v2 — add RSI falling + MACD negative confirmation
    "NEW_VolMax_v2": """
        SAFE_DIVIDE(t.Close, NULLIF(t.Volume_MaxTop5_2Y_Close,0)) < 0.84
        AND t.ID_Current - t.Volume_MaxTop5_2Y_ID <= 128.0
        AND t.D_RSI < 0.55
        AND t.D_RSI_T1 > t.D_RSI
        AND t.D_MACDdiff < 0
        AND t.Close < t.Open
        AND SAFE_DIVIDE(t.Close_T1, NULLIF(t.LO_3M_T1,0)) > 1.59""",

    # NEW5: Profit-Lock — big gain + overbought + earnings slowing
    "NEW_ProfitLock": """
        t.Close > 1.40*t.MA200
        AND t.D_RSI > 0.75
        AND t.D_RSI_T1 > t.D_RSI
        AND SAFE_DIVIDE(t.NP_P0, NULLIF(t.NP_P1,0)) < 1.05
        AND t.Volume > 1.00*t.Volume_3M_P50""",
}

SIGNAL_LABELS = {
    "MA31":           "MA31 (current)",
    "MA41":           "MA41 (current)",
    "SellBV":         "SellBV (current)",
    "SellBV2":        "SellBV2 (current)",
    "SellPE":         "SellPE (current)",
    "SellResistance": "SellResistance (current)",
    "BearDvg2":       "BearDvg2 (current)",
    "SellVolMax":     "SellVolMax (current - BAD)",
    "NEW_RSI_Peak":   "NEW: RSI Peak Exit",
    "NEW_VAP_Break":  "NEW: VAP Breakdown",
    "NEW_MA_DeathX":  "NEW: MA Death Cross",
    "NEW_VolMax_v2":  "NEW: SellVolMax v2",
    "NEW_ProfitLock": "NEW: Profit Lock",
}

# Run BQ query for each signal using LEAD() for forward returns
# One query per signal (cleaner, cheaper than massive UNION)
bq_results = {}

for sig_name, where_clause in SELL_SIGNALS.items():
    print(f"  Testing {sig_name} ...", end=" ", flush=True)
    sql = f"""
WITH base AS (
  SELECT
    t.ticker, t.time, t.Close,
    LEAD(t.Close, 5)  OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_1w,
    LEAD(t.Close, 10) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_2w,
    LEAD(t.Close, 20) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_1m,
    LEAD(t.Close, 40) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_2m,
    LEAD(t.Close, 60) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_3m,
    t.Open, t.Close_T1, t.Close_T1W, t.VAP1M, t.VAP1W, t.VAP3M,
    t.D_RSI, t.D_RSI_T1, t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
    t.D_RSI_Max1W_Close, t.D_RSI_Max3M_Close,
    t.D_RSI_Max3M_MACD, t.D_RSI_Max1W_MACD,
    t.D_MACDdiff,
    t.MA10, t.MA20, t.MA200, t.MA10_T1, t.MA20_T1, t.MA50_T1,
    t.Volume, t.Volume_3M_P50, t.Volume_1M,
    t.NP_P0, t.NP_P1, t.PE, t.PE_MA5Y, t.PE_SD5Y,
    t.PB, t.PB_MA5Y, t.PB_SD5Y, t.BVPS,
    t.LO_3M_T1, t.Res_1Y,
    t.Volume_MaxTop5_2Y_Close, t.Volume_MaxTop5_2Y_ID, t.ID_Current
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN '{BQ_DATE_FROM}' AND '{BQ_DATE_TO}'
    AND t.Close IS NOT NULL AND t.Close > 0
)
SELECT
  COUNT(*) AS n,
  ROUND(AVG((close_1w/Close - 1)*100), 3) AS ret_1w,
  ROUND(AVG((close_2w/Close - 1)*100), 3) AS ret_2w,
  ROUND(AVG((close_1m/Close - 1)*100), 3) AS ret_1m,
  ROUND(AVG((close_2m/Close - 1)*100), 3) AS ret_2m,
  ROUND(AVG((close_3m/Close - 1)*100), 3) AS ret_3m,
  ROUND(COUNTIF(close_1m < Close) / COUNT(*), 4) AS pct_fell_1m,
  ROUND(COUNTIF(close_3m < Close) / COUNT(*), 4) AS pct_fell_3m,
  ROUND(AVG(CASE WHEN close_1m IS NOT NULL THEN (close_1m/Close - 1)*100 END), 3) AS ret_1m_clean
FROM base AS t
WHERE close_1m IS NOT NULL
  AND close_3m IS NOT NULL
  AND {where_clause}
"""
    res = bq_query(sql, sig_name)
    if res is not None and not res.empty:
        bq_results[sig_name] = res.iloc[0].to_dict()
        r = bq_results[sig_name]
        print(f"n={int(r['n']):,} | ret_1m={r['ret_1m']:+.1f}% | fell_1m={r['pct_fell_1m']:.0%}")
    else:
        print("no data")

# Also get baseline (all days)
print("  Computing market baseline ...", end=" ", flush=True)
sql_base = f"""
WITH base AS (
  SELECT t.Close,
    LEAD(t.Close, 20) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_1m,
    LEAD(t.Close, 60) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_3m
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN '{BQ_DATE_FROM}' AND '{BQ_DATE_TO}'
    AND t.Close IS NOT NULL AND t.Close > 0
)
SELECT
  COUNT(*) AS n,
  ROUND(AVG((close_1m/Close - 1)*100), 3) AS ret_1m,
  ROUND(AVG((close_3m/Close - 1)*100), 3) AS ret_3m,
  ROUND(COUNTIF(close_1m < Close) / COUNT(*), 4) AS pct_fell_1m
FROM base WHERE close_1m IS NOT NULL AND close_3m IS NOT NULL
"""
base_res = bq_query(sql_base, "baseline")
if base_res is not None and not base_res.empty and len(base_res) > 0:
    bq_results["_baseline"] = base_res.iloc[0].to_dict()
    r = bq_results["_baseline"]
    print(f"n={int(r['n']):,} | ret_1m={r['ret_1m']:+.1f}% | fell_1m={r['pct_fell_1m']:.0%}")
else:
    bq_results["_baseline"] = {"n": 0, "ret_1m": 1.0, "ret_1w": 0.3,
                                "ret_3m": 3.0, "pct_fell_1m": 0.46}
    print("using defaults")

# Print BQ results table
print(f"\n{'Signal':<25} {'N':>7} {'Ret1W':>7} {'Ret1M':>7} {'Ret2M':>7} {'Ret3M':>7} {'Fell1M':>7} {'Fell3M':>7}")
print("-" * 80)
baseline_1m = bq_results.get("_baseline", {}).get("ret_1m", 0)
baseline_fell = bq_results.get("_baseline", {}).get("pct_fell_1m", 0.5)
print(f"  {'[Market Baseline]':<23} {int(bq_results['_baseline']['n']):>7,} "
      f"{bq_results['_baseline'].get('ret_1w',0):>+6.1f}% "
      f"{bq_results['_baseline']['ret_1m']:>+6.1f}% "
      f"{'--':>7} "
      f"{bq_results['_baseline']['ret_3m']:>+6.1f}% "
      f"{bq_results['_baseline']['pct_fell_1m']:>6.0%} "
      f"{'--':>7}")
print("-"*80)

for sig_name, r in bq_results.items():
    if sig_name == "_baseline": continue
    is_new = sig_name.startswith("NEW_")
    label  = SIGNAL_LABELS.get(sig_name, sig_name)
    n      = int(r.get("n", 0))
    ret1w  = r.get("ret_1w", 0)
    ret1m  = r.get("ret_1m", 0)
    ret2m  = r.get("ret_2m", 0)
    ret3m  = r.get("ret_3m", 0)
    fell1m = r.get("pct_fell_1m", 0)
    fell3m = r.get("pct_fell_3m", 0)
    marker = ">>>" if is_new else "   "
    # Grade: good signal = ret_1m < baseline, fell_1m > baseline
    good_sig = ret1m < baseline_1m and fell1m > baseline_fell
    tag = "[GOOD]" if good_sig else "[WEAK]"
    print(f"{marker} {label:<23} {n:>7,} {ret1w:>+6.1f}% {ret1m:>+6.1f}% "
          f"{ret2m:>+6.1f}% {ret3m:>+6.1f}% {fell1m:>6.0%} {fell3m:>6.0%} {tag}")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 16), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.46, wspace=0.38)

# Panel 1: Sell filter timing quality (profile hit)
ax1 = fig.add_subplot(gs[0, :2])
stats_list = [(sf, v) for sf, v in signal_stats.items()]
stats_list.sort(key=lambda x: x[1]["good"], reverse=True)
sf_names = [s[0] for s in stats_list]
good_pcts = [s[1]["good"] * 100 for s in stats_list]
sell_avgs  = [s[1]["sell"] for s in stats_list]
bar_colors = [GREEN if g >= 70 else (YELLOW if g >= 50 else RED) for g in good_pcts]
bars1 = ax1.bar(range(len(sf_names)), good_pcts, color=bar_colors, alpha=0.85)
ax1.axhline(50, color=YELLOW, linewidth=1.2, linestyle="--", label="50% line")
ax1.axhline(70, color=GREEN,  linewidth=1.0, linestyle=":",  label="70% (good)")
ax1.set_xticks(range(len(sf_names)))
ax1.set_xticklabels(sf_names, fontsize=8, rotation=30, ha="right")
ax1.set_ylabel("Good Timing % (Sell_profit > P1M)")
ax1.set_title("Sell Signal Timing Quality (profile_hit.csv)\n"
              "= % of deals where selling at signal beat holding 1 more month",
              color=TEXT_CLR, fontweight="bold")
ax1.set_ylim(0, 105)
ax1.legend(fontsize=8)
for bar, val, sp in zip(bars1, good_pcts, sell_avgs):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.0f}%\n({sp:+.0f}%)", ha="center", fontsize=7, color=TEXT_CLR)

# Panel 2: Sell profit distribution by signal (violin/box)
ax2 = fig.add_subplot(gs[0, 2])
plot_signals = ["BearDvgVNI2","SellResistance","MA41","SellBV","MA31","SellVolMax","cutloss"]
plot_data    = [closed[closed["Sell_filter"] == s]["Sell_profit"].clip(-40, 100).values
                for s in plot_signals if s in closed["Sell_filter"].values]
plot_labels  = [s for s in plot_signals if s in closed["Sell_filter"].values]
if plot_data:
    bp = ax2.boxplot(plot_data, tick_labels=plot_labels, patch_artist=True, vert=True,
                     medianprops=dict(color="white", linewidth=2),
                     flierprops=dict(marker=".", markersize=2, alpha=0.3))
    sig_colors = [GREEN if signal_stats.get(s, {}).get("good", 0) >= 0.65
                  else (YELLOW if signal_stats.get(s, {}).get("good", 0) >= 0.45
                  else RED) for s in plot_labels]
    for patch, color in zip(bp["boxes"], sig_colors):
        patch.set_facecolor(color); patch.set_alpha(0.6)
    ax2.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax2.set_xticklabels(plot_labels, fontsize=6, rotation=40, ha="right")
    ax2.set_ylabel("Sell_profit (%)")
    ax2.set_title("Sell Profit Distribution\n(green=good timing, red=bad)", color=TEXT_CLR)
    ax2.set_ylim(-42, 120)

# Panel 3: BQ forward returns — current signals
ax3 = fig.add_subplot(gs[1, :2])
current_sigs = [s for s in SELL_SIGNALS if not s.startswith("NEW_") and s in bq_results]
ret1m_vals   = [bq_results[s].get("ret_1m", 0) for s in current_sigs]
fell1m_vals  = [bq_results[s].get("pct_fell_1m", 0) * 100 for s in current_sigs]

x = np.arange(len(current_sigs))
w = 0.35
bars3a = ax3.bar(x - w/2, ret1m_vals, width=w, alpha=0.85, label="Avg 1M return after signal",
                 color=[GREEN if v < baseline_1m else RED for v in ret1m_vals])
bars3b = ax3.bar(x + w/2, fell1m_vals, width=w, alpha=0.85, label="% stocks fell 1M after",
                 color=[BLUE]*len(current_sigs))
ax3.axhline(baseline_1m,       color=ORANGE, linewidth=1.5, linestyle="--",
            label=f"Market baseline ret_1m={baseline_1m:+.1f}%")
ax3.axhline(baseline_fell*100, color=TEAL,   linewidth=1.5, linestyle=":",
            label=f"Market baseline fell={baseline_fell:.0%}")
ax3.set_xticks(x)
ax3.set_xticklabels(current_sigs, fontsize=8, rotation=20, ha="right")
ax3.set_ylabel("Return / % fell (%)")
ax3.set_title("BQ Validation: Current Sell Signals\n"
              "Green bar = good (ret_1m < market baseline = sold at right time)",
              color=TEXT_CLR, fontweight="bold")
ax3.legend(fontsize=7, loc="lower right")
ax3.axhline(0, color=TEXT_CLR, linewidth=0.6, linestyle=":")

# Panel 4: BQ — New proposed signals vs current best
ax4 = fig.add_subplot(gs[1, 2])
compare_sigs = ["BearDvg2","SellResistance","SellBV2"] + \
               [s for s in SELL_SIGNALS if s.startswith("NEW_") and s in bq_results]
compare_ret1m = [bq_results.get(s, {}).get("ret_1m", 0) for s in compare_sigs]
compare_fell  = [bq_results.get(s, {}).get("pct_fell_1m", 0) * 100 for s in compare_sigs]
ax4_colors = [BLUE]*3 + [ORANGE]*(len(compare_sigs)-3)
bars4 = ax4.barh(range(len(compare_sigs)), compare_ret1m, color=ax4_colors, alpha=0.85)
ax4.axvline(baseline_1m, color=RED, linewidth=1.5, linestyle="--")
ax4.axvline(0, color=TEXT_CLR, linewidth=0.6, linestyle=":")
ax4.set_yticks(range(len(compare_sigs)))
ax4.set_yticklabels([SIGNAL_LABELS.get(s, s).replace(" (current)","") for s in compare_sigs],
                    fontsize=7)
ax4.set_xlabel("Avg 1M return after signal (lower=better for sell)")
ax4.set_title("New vs Existing Signals\n(blue=current, orange=proposed)",
              color=TEXT_CLR, fontweight="bold")
for bar, val in zip(bars4, compare_ret1m):
    ax4.text(val + 0.05, bar.get_y() + bar.get_height()/2,
             f"{val:+.1f}%", va="center", fontsize=8, color=TEXT_CLR)

# Panel 5: cutloss recovery analysis
ax5 = fig.add_subplot(gs[2, 0])
cl = closed[closed["Sell_filter"] == "cutloss"]
ax5.hist(cl["Sell_profit"], bins=30, alpha=0.7, color=RED,  label="Cutloss profit at exit")
ax5.hist(cl["P1M"],          bins=30, alpha=0.7, color=BLUE, label="P1M (1M forward from buy)")
ax5.axvline(0, color=TEXT_CLR, linewidth=1.0, linestyle="--")
ax5.set_xlabel("Return (%)")
ax5.set_title(f"Cutloss: Recovery After Exit\n"
              f"93% of cutloss stocks recovered (P1M > sell)",
              color=TEXT_CLR, fontweight="bold")
ax5.legend(fontsize=7)
ax5.set_xlim(-40, 40)

# Panel 6: SellVolMax problem
ax6 = fig.add_subplot(gs[2, 1])
svm = closed[closed["Sell_filter"] == "SellVolMax"]
ax6.scatter(svm["Sell_profit"], svm["P1M"], alpha=0.5, s=20, color=ORANGE)
ax6.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
ax6.axvline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
ax6.plot([-40, 100], [-40, 100], color=GRID_CLR, linewidth=0.8, linestyle=":")
# Quadrant labels
ax6.text(0.02, 0.98, "Sold too early\n(stock rose more)",
         transform=ax6.transAxes, va="top", fontsize=8, color=RED,
         bbox=dict(facecolor=PANEL_BG, edgecolor=RED, alpha=0.8, pad=2))
n_early = (svm["P1M"] > svm["Sell_profit"]).sum()
ax6.set_xlabel("Sell_profit at exit (%)")
ax6.set_ylabel("P1M return (from buy) %")
ax6.set_title(f"SellVolMax: Exits Too Early\n{n_early/len(svm):.0%} stocks rose after exit",
              color=TEXT_CLR, fontweight="bold")

# Panel 7: Summary table — all signals
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis("off")
table_data = []
for sf, v in sorted(signal_stats.items(), key=lambda x: x[1]["good"], reverse=True):
    bq_r = bq_results.get(sf.replace("SellFilter_",""), {})
    table_data.append([sf, f"{v['n']:,}", f"{v['good']:.0%}", f"{v['sell']:+.1f}%", v["grade"].strip()])

headers = ["Signal", "N", "GoodTiming", "AvgSell", "Grade"]
t = ax7.table(cellText=table_data, colLabels=headers, loc="center", cellLoc="center")
t.auto_set_font_size(False)
t.set_fontsize(7)
t.scale(1.0, 1.3)
for (row, col), cell in t.get_celld().items():
    cell.set_facecolor(PANEL_BG)
    cell.set_edgecolor(GRID_CLR)
    cell.set_text_props(color=TEXT_CLR)
    if row == 0:
        cell.set_facecolor("#2a2d3a")
ax7.set_title("Signal Summary", color=TEXT_CLR, fontweight="bold", y=0.98)

fig.suptitle("Sell Pattern Analysis: Effectiveness & Improvement Proposals",
             color=TEXT_CLR, fontsize=14, fontweight="bold", y=0.99)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: {OUT_IMG}")

# ── FINAL RECOMMENDATIONS ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)
print("""
SIGNALS CAN KEEP (timing good, >= 70%):
  - BearDvgVNI2 (external): 78% good timing, avg +15.6% -- EXCELLENT, keep as #1
  - SellResistance (79%), SellResistance1Y (81%), MA41 (91%)
  - SellBV2 (72%)

SIGNALS NEED IMPROVEMENT:
  - SellVolMax (D grade): 87% of time stock rose AFTER exit -- either fix or REMOVE
    Fix: add requirement D_MACDdiff < 0 AND Close < Open (bearish candle confirmation)
  - cutloss (D grade): 93% of stocks RECOVERED after cutloss -- threshold too tight
    Fix: implement trailing stop + time-stop combo instead of fixed cutloss
  - MA31 (C grade): 67% exits too early
    Fix: add minimum profit threshold (e.g., only fire if Sell_profit would be > 5%)

PROPOSED NEW SIGNALS TO TEST IN BQ:
  - NEW_RSI_Peak: RSI overbought + falling + MACD negative
  - NEW_VAP_Break: Close breaks below VAP1M with high volume (distribution day)
  - NEW_MA_DeathX: MA10 crosses below MA20 with volume
  - NEW_ProfitLock: Close > 1.4*MA200 + RSI very high + earnings declining
""")
