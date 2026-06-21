#!/usr/bin/env python3
"""
quality_tactical_scanner.py
===========================
Daily scanner: identify quality stocks at undervalued entry points.

Combines:
  - Quality filter: FA history ≥70% A+B, latest A/B, liquidity ≥5B/day
  - Valuation undervalued: PE_z < -0.5 OR PB_z < -0.5 OR DD>25% from 52w high
  - TA confirmation: RSI rebound OR MA50/MA200 reclaim with volume
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
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

print("="*120)
print("  QUALITY + TACTICAL ENTRY SCANNER")
print("="*120)

# ─── STEP 1: Quality universe ────────────────────────────────────────────
print("\n[1] Building quality universe ...")
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time"])
latest_q = fa["quarter"].max()
print(f"  Latest quarter: {latest_q}")

# Tickers with ≥12 quarters history
qhist = fa.groupby("ticker").agg(
    n_q=("quarter", "count"),
    n_A=("tier", lambda x: (x=="A").sum()),
    n_AB=("tier", lambda x: x.isin(["A","B"]).sum()),
).reset_index()
qhist["pct_AB"] = qhist["n_AB"] / qhist["n_q"] * 100
quality = qhist[(qhist["n_q"] >= 12) & (qhist["pct_AB"] >= 70)].copy()

# Latest FA must be A or B
latest_fa = fa[fa["quarter"] == latest_q][["ticker","tier","score","sub"]].rename(columns={"tier":"fa_latest","score":"fa_score"})
quality = quality.merge(latest_fa, on="ticker", how="inner")
quality = quality[quality["fa_latest"].isin(["A","B"])]
print(f"  Quality universe (FA history ≥12Q, ≥70% A+B, latest A/B): {len(quality)} tickers")

# ─── STEP 2: Pull current market data for quality universe ───────────────
tickers_str = "','".join(quality["ticker"].tolist())
print(f"\n[2] Pulling latest market data ({len(quality)} tickers) ...")

market = bq_query(f"""
WITH latest AS (
  SELECT t1.ticker AS tk, MAX(t1.time) AS time FROM tav2_bq.ticker_1m AS t1
  WHERE t1.ticker IN ('{tickers_str}') AND t1.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY t1.ticker
)
SELECT t.ticker, t.time, t.Close, t.MA50, t.MA200,
  t.D_RSI, t.D_RSI_T1W, t.D_MACDdiff,
  t.Volume, t.Volume_3M_P50,
  t.PE, t.PE_MA5Y, t.PE_SD5Y, t.PB, t.PB_MA5Y, t.PB_SD5Y,
  t.HI_3M_T1, t.LO_3M_T1, t.Volume_Max1Y_High,
  t.Close_T1W, t.Close_T1,
  t.Volume_3M_P50 * t.Close AS liq_vnd
FROM tav2_bq.ticker_1m AS t
JOIN latest AS l ON l.tk = t.ticker AND l.time = t.time
WHERE t.Close > 0
""")
print(f"  Pulled {len(market)} rows")

# Also pull 52w high from rolling
hi52 = bq_query(f"""
WITH px AS (
  SELECT t.ticker, t.time, t.Close,
    MAX(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time
      ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi_52w
  FROM tav2_bq.ticker AS t
  WHERE t.ticker IN ('{tickers_str}') AND t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 400 DAY)
)
SELECT ticker, hi_52w FROM px
WHERE time = (SELECT MAX(time) FROM px AS p2 WHERE p2.ticker = px.ticker)
""")

# Merge
scan = market.merge(quality, on="ticker", how="left").merge(hi52, on="ticker", how="left")
scan = scan[scan["liq_vnd"] >= 5e9]  # liquidity filter
print(f"  After liquidity filter (≥5B/day): {len(scan)}")

# ─── STEP 3: Compute scoring ────────────────────────────────────────────
print(f"\n[3] Scoring entry signals ...")
scan["pe_z"] = ((scan["PE"] - scan["PE_MA5Y"]) / scan["PE_SD5Y"].replace(0, np.nan)).clip(-10, 10)
scan["pb_z"] = ((scan["PB"] - scan["PB_MA5Y"]) / scan["PB_SD5Y"].replace(0, np.nan)).clip(-10, 10)
scan["dd_52w_pct"] = (scan["Close"] / scan["hi_52w"] - 1) * 100
scan["vs_MA50_pct"] = (scan["Close"] / scan["MA50"] - 1) * 100
scan["vs_MA200_pct"] = (scan["Close"] / scan["MA200"] - 1) * 100
scan["vol_ratio"] = scan["Volume"] / scan["Volume_3M_P50"]
scan["rsi"] = scan["D_RSI"] * 100
scan["rsi_1w_ago"] = scan["D_RSI_T1W"] * 100

# Valuation undervalued (any condition)
scan["v_undervalued_PE"] = scan["pe_z"] < -0.5
scan["v_undervalued_PB"] = scan["pb_z"] < -0.5
scan["v_undervalued_DD"] = scan["dd_52w_pct"] < -25
scan["v_undervalued_ANY"] = scan["v_undervalued_PE"] | scan["v_undervalued_PB"] | scan["v_undervalued_DD"]

# TA reversal signals
scan["t_rsi_rebound"] = (scan["rsi_1w_ago"] < 35) & (scan["rsi"] > 40)
scan["t_above_ma50"] = scan["vs_MA50_pct"] > 0
scan["t_above_ma200"] = scan["vs_MA200_pct"] > 0
scan["t_volume_surge"] = scan["vol_ratio"] > 1.5
scan["t_macd_pos"] = scan["D_MACDdiff"] > 0
# Combined TA: (above MA50 AND/OR above MA200) OR (RSI rebound)
scan["t_setup_OK"] = scan["t_rsi_rebound"] | (scan["t_above_ma50"] & (scan["rsi"] > 45))

# Composite buy score
scan["entry_score"] = (
    (-scan["pe_z"].fillna(0).clip(-3, 3)) * 3 +     # cheap PE = positive points
    (-scan["pb_z"].fillna(0).clip(-3, 3)) * 2 +     # cheap PB
    np.where(scan["dd_52w_pct"] < -25, (-scan["dd_52w_pct"]/10).clip(0, 5), 0) * 2 +  # depth bonus
    np.where(scan["t_rsi_rebound"], 5, 0) +          # RSI rebound bonus
    np.where(scan["t_above_ma200"], 2, -2) +         # uptrend bonus
    np.where(scan["t_volume_surge"] & scan["t_above_ma50"], 3, 0)  # breakout volume
)

# ─── STEP 4: Output BUY candidates ───────────────────────────────────────
print(f"\n{'='*120}")
print(f"  BUY CANDIDATES — Valuation undervalued + TA reversal setup")
print(f"{'='*120}")

# 4A: Valuation+TA both confirm
strong_buy = scan[scan["v_undervalued_ANY"] & scan["t_setup_OK"] & scan["t_above_ma200"]].sort_values("entry_score", ascending=False)
print(f"\n--- 🟢 STRONG BUY: Valuation undervalued + TA reversal + above MA200 ---")
print(f"  {'Ticker':<7}{'FA':>4}{'%AB':>6}{'sub':<14}{'Close':>8}{'PE':>6}{'PE_z':>7}{'PB_z':>7}{'%DD_52w':>10}{'%MA50':>9}{'%MA200':>9}{'RSI':>6}{'Vol':>7}{'Score':>8}")
for _, r in strong_buy.head(20).iterrows():
    print(f"  {r['ticker']:<7}{r['fa_latest']:>4}{r['pct_AB']:>5.0f}%{r['sub'][:13]:<14}{r['Close']:>8.0f}{r['PE']:>6.1f}{r['pe_z']:>+7.2f}{r['pb_z']:>+7.2f}{r['dd_52w_pct']:>+9.1f}%{r['vs_MA50_pct']:>+8.1f}%{r['vs_MA200_pct']:>+8.1f}%{r['rsi']:>+5.0f}%{r['vol_ratio']:>+6.1f}x{r['entry_score']:>+8.2f}")

# 4B: Deeply undervalued but not yet TA-confirmed (WATCH list)
watch = scan[scan["v_undervalued_ANY"] & ~scan["t_setup_OK"]].sort_values("entry_score", ascending=False)
print(f"\n--- 🟡 WATCH: Undervalued but no TA reversal yet (wait for RSI rebound or MA50 reclaim) ---")
print(f"  {'Ticker':<7}{'FA':>4}{'%AB':>6}{'sub':<14}{'Close':>8}{'PE':>6}{'PE_z':>7}{'%DD_52w':>10}{'%MA200':>9}{'RSI':>6}{'Wait for':>20}")
for _, r in watch.head(15).iterrows():
    wait_signal = "RSI > 45 (now {:.0f})".format(r['rsi']) if r['rsi'] < 45 else "MA50 reclaim"
    print(f"  {r['ticker']:<7}{r['fa_latest']:>4}{r['pct_AB']:>5.0f}%{r['sub'][:13]:<14}{r['Close']:>8.0f}{r['PE']:>6.1f}{r['pe_z']:>+7.2f}{r['dd_52w_pct']:>+9.1f}%{r['vs_MA200_pct']:>+8.1f}%{r['rsi']:>+5.0f}%{wait_signal:>20}")

# 4C: Quality + TA breakout but valuation rich (momentum mode)
momentum = scan[~scan["v_undervalued_ANY"] & scan["t_above_ma200"] & (scan["vs_MA50_pct"] > 0) & (scan["vol_ratio"] > 1.5)].sort_values("entry_score", ascending=False)
print(f"\n--- 🔵 MOMENTUM: Above MA200 + MA50 breakout (no valuation discount but trend strong) ---")
print(f"  {'Ticker':<7}{'FA':>4}{'%AB':>6}{'sub':<14}{'Close':>8}{'PE':>6}{'PE_z':>7}{'%MA200':>9}{'RSI':>6}{'Vol':>7}")
for _, r in momentum.head(10).iterrows():
    print(f"  {r['ticker']:<7}{r['fa_latest']:>4}{r['pct_AB']:>5.0f}%{r['sub'][:13]:<14}{r['Close']:>8.0f}{r['PE']:>6.1f}{r['pe_z']:>+7.2f}{r['vs_MA200_pct']:>+8.1f}%{r['rsi']:>+5.0f}%{r['vol_ratio']:>+6.1f}x")

# Save
scan.to_csv(f"quality_tactical_scan_{pd.Timestamp.today().date()}.csv", index=False)
print(f"\nSaved: quality_tactical_scan_{pd.Timestamp.today().date()}.csv")
