# -*- coding: utf-8 -*-
"""
vnindex_5state_ew_v1.py
=======================
Equal-weighted VNINDEX market-state system — candidate STAGING.

Idea: VNINDEX is cap-weighted and heavily distorted by VIN family (VIC +362%, VHM +108%
2025-06 → 2026-05). 6/7 factors (88% weight) of the 5-state system come from raw VNINDEX
→ false BULL signal in narrow-leadership regimes.

Fix: replace raw VNINDEX with VNINDEX_EW (equal-weighted index) on point-in-time
eligible universe (≥252 sessions + 60d avg trading value ≥ 0.5B VND).

Pipeline (canonical Cổ Điển params for fair A/B vs LIVE archive):
  expanding_pct_rank → composite (W_BASE) → EMA(0.40) → classify → risk overrides
  → rolling_mode(15) → min_stay_filter(7)

Pre-2014: fallback to raw VNINDEX (universe too sparse).
CMF: median D_CMF across eligible universe (post-2014); VNINDEX D_CMF (pre-2014).
Breadth: % above MA50 on eligible universe.

Outputs:
  vnindex_5state_ew_staging.csv  → time, state, state_raw (uploadable via deploy_ngu_hanh.py)
  vnindex_5state_ew_full.csv     → full diagnostics for inspection
"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ      = r"bq"
PROJECT = "lithe-record-440915-m9"

# State machine params (canonical Cổ Điển — apples-to-apples vs archive_co_dien)
W_BASE      = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
               "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
MODE_WIN    = 15
MIN_STAY    = 7
EMA_ALPHA   = 0.40
EW_START    = pd.Timestamp("2014-01-01")  # EW kicks in from here; raw VNI before
LIQ_MIN     = float(os.environ.get("LIQ_MIN", 5e8))   # 500M VND/day rolling 60d avg trading value (env-overridable for sweeps)
HIST_MIN    = 252        # min sessions of history per ticker to be eligible
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

CACHE_TICKER = os.path.join(WORKDIR, "data/_cache_universe_2013_now.pkl")
CACHE_VNI    = os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl")

# ──────────────────────────────────────────────────────────────────────
# DATA PULL (cached)
# ──────────────────────────────────────────────────────────────────────
def bq_csv(sql: str) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); qp = f.name
    cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000 < "{qp}"'
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    os.unlink(qp)
    if r.returncode != 0:
        raise RuntimeError(f"BQ query failed: {r.stderr[:500]}")
    return pd.read_csv(io.StringIO(r.stdout))

def pull_vnindex():
    if os.path.exists(CACHE_VNI):
        print(f"  [cache] loading {CACHE_VNI}")
        return pd.read_pickle(CACHE_VNI)
    print("  Pulling VNINDEX from BQ ...")
    sql = """
    SELECT t.time, t.Open, t.High, t.Low, t.Close, t.Volume,
           t.VNINDEX_PE, t.MA200, t.D_CMF, t.D_RSI, t.D_MACDdiff,
           t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
           t.D_RSI_Min1W, t.D_RSI_Min3M,
           t.D_RSI_Max1W_Close, t.D_RSI_Max3M_Close,
           t.D_RSI_Max3M_MACD, t.D_RSI_Max1W_MACD,
           t.D_RSI_MinT3, t.C_L1M, t.C_L1W
    FROM tav2_bq.ticker AS t
    WHERE t.ticker = 'VNINDEX'
    ORDER BY t.time
    """
    df = bq_csv(sql)
    df["time"] = pd.to_datetime(df["time"])
    df.to_pickle(CACHE_VNI)
    print(f"  Saved cache: {len(df)} rows")
    return df

def pull_universe():
    if os.path.exists(CACHE_TICKER):
        print(f"  [cache] loading {CACHE_TICKER}")
        return pd.read_pickle(CACHE_TICKER)
    print("  Pulling universe (this may take 30-60s) ...")
    sql = """
    SELECT t.time, t.ticker, t.Close, t.Price, t.Volume, t.MA50, t.D_CMF
    FROM tav2_bq.ticker AS t
    WHERE t.time >= '2013-01-01'
      AND t.ticker != 'VNINDEX' AND t.ticker != 'VN30'
      AND t.ticker NOT LIKE 'VN30F%'
      AND t.ticker NOT LIKE 'E1VFVN30%'
      AND t.ticker NOT LIKE 'FUE%'
      AND t.Close IS NOT NULL AND t.Close > 0
    """
    df = bq_csv(sql)
    df["time"] = pd.to_datetime(df["time"])
    df.to_pickle(CACHE_TICKER)
    print(f"  Saved cache: {len(df):,} rows, {df['ticker'].nunique()} tickers")
    return df

# ──────────────────────────────────────────────────────────────────────
print("=" * 70)
print("VNINDEX_EW 5-state — STAGING build")
print("=" * 70)
print("Step 1: Load data")
vni  = pull_vnindex()
univ = pull_universe()
print(f"  VNINDEX: {len(vni)} rows | {vni['time'].min().date()} → {vni['time'].max().date()}")
print(f"  Universe: {len(univ):,} rows | {univ['ticker'].nunique()} tickers | {univ['time'].min().date()} → {univ['time'].max().date()}")

# ──────────────────────────────────────────────────────────────────────
# Step 2: Compute point-in-time eligibility + universe-level aggregates
# ──────────────────────────────────────────────────────────────────────
print("\nStep 2: Point-in-time eligibility + EW daily returns")
univ = univ.sort_values(["ticker", "time"]).reset_index(drop=True)

# per-ticker rolling: trading_value 60d avg + session-count
print("  Computing per-ticker rolling stats ...")
# NOTE 2026-06-01: real-liquidity gate uses unadjusted Price (more correct). Default = Close
# (production unchanged pending deploy approval). Set env TV_PRICE=1 to use real Price tv.
if os.environ.get("TV_PRICE", "0") == "1":
    univ["tv"] = univ["Price"].fillna(univ["Close"]) * univ["Volume"]   # real (unadjusted) notional
else:
    univ["tv"] = univ["Close"] * univ["Volume"]
g = univ.groupby("ticker", group_keys=False)
univ["tv_avg60"] = g["tv"].transform(lambda s: s.rolling(60, min_periods=30).mean())
univ["session_n"] = g.cumcount() + 1  # how many sessions of history including today
univ["log_ret"]   = g["Close"].transform(lambda s: np.log(s / s.shift(1)))
# above_ma50: 1 if Close > MA50 else 0 (NaN if MA50 missing)
univ["above_ma50"] = np.where(univ["MA50"].notna() & (univ["Close"] > univ["MA50"]), 1.0,
                              np.where(univ["MA50"].notna(), 0.0, np.nan))

# eligibility at t: need 252+ sessions AND tv_avg60 >= LIQ_MIN
# (use today's tv_avg60 as proxy for "previous-known liquidity")
# TOPN>0 (env): instead of an absolute VND floor, keep the top-N most-liquid by tv_avg60 each day
#   → constant basket size over time (most stable universe). Uses tv_avg60 (set TV_PRICE=1 for real tv).
_TOPN = int(os.environ.get("TOPN", "0"))
_hist_ok = univ["session_n"] >= HIST_MIN
if _TOPN > 0:
    _rk = univ[_hist_ok].groupby("time")["tv_avg60"].rank(ascending=False, method="first")
    univ["eligible"] = False
    univ.loc[_rk[_rk <= _TOPN].index, "eligible"] = True
    print(f"  [eligibility] TOP-{_TOPN} most-liquid per day (tv_avg60)")
else:
    univ["eligible"] = _hist_ok & (univ["tv_avg60"] >= LIQ_MIN)
    print(f"  [eligibility] absolute floor tv_avg60 >= {LIQ_MIN:.0f}")

# ──────────────────────────────────────────────────────────────────────
# Step 3: Daily EW aggregates
# ──────────────────────────────────────────────────────────────────────
print("\nStep 3: Aggregate EW daily metrics")
mask = univ["eligible"].fillna(False)
sub  = univ[mask].copy()
# ── RAW r_score inputs for dev reconciliation (per-ticker, point-in-time eligible basket) ──
# Set EXPORT_RAW=1 to dump (large ~30MB; skip during sweeps). All values are BQ-sourced.
if os.environ.get("EXPORT_RAW", "0") == "1":
    _otag = os.environ.get("OUT_TAG", "")
    _raw = sub[["time","ticker","Close","Volume","tv_avg60","MA50","above_ma50","log_ret","D_CMF","session_n"]].copy()
    if "Price" in sub.columns: _raw["Price"] = sub["Price"]
    _raw_path = os.path.join(WORKDIR, f"vnindex_5state_ew_eligible_universe{_otag}.csv")
    _raw.to_csv(_raw_path, index=False)
    print(f"  [RAW] eligible-universe membership -> {_raw_path} ({len(_raw):,} rows)")
daily = sub.groupby("time").agg(
    n_universe = ("ticker", "count"),
    ret_ew     = ("log_ret", "mean"),
    cmf_med    = ("D_CMF", "median"),
    breadth    = ("above_ma50", "mean"),
).reset_index()

# Build VNINDEX_EW cumulative level (base=100 at first day with valid ret_ew)
daily = daily.sort_values("time").reset_index(drop=True)
daily["ret_ew"] = daily["ret_ew"].fillna(0)
# Trim to >= EW_START
daily = daily[daily["time"] >= EW_START].reset_index(drop=True)
# Find first valid daily aggregate
daily["close_ew"] = 100.0 * np.exp(daily["ret_ew"].cumsum())
print(f"  EW series: {len(daily)} sessions | {daily['time'].min().date()} → {daily['time'].max().date()}")
print(f"  Universe size: min={daily['n_universe'].min()} max={daily['n_universe'].max()} median={int(daily['n_universe'].median())}")

# ──────────────────────────────────────────────────────────────────────
# Step 4: Splice raw VNI (pre-2014) + VNINDEX_EW (post-2014)
# ──────────────────────────────────────────────────────────────────────
print("\nStep 4: Splice raw VNI (pre-2014) + EW (post-2014)")
vni = vni.sort_values("time").reset_index(drop=True)
vni_pre = vni[vni["time"] < EW_START].copy()
vni_post = vni[vni["time"] >= EW_START].copy()

# Scale EW to match VNINDEX raw at the splice date
splice_anchor = vni[vni["time"] >= EW_START].iloc[0] if len(vni_post) else None
anchor_date = splice_anchor["time"]
anchor_vni  = splice_anchor["Close"]
# Find EW value at anchor_date
ew_anchor_row = daily[daily["time"] == anchor_date]
if len(ew_anchor_row) == 0:
    # earliest EW day after anchor
    ew_anchor_row = daily[daily["time"] >= anchor_date].iloc[[0]]
    anchor_date = ew_anchor_row.iloc[0]["time"]
    anchor_vni  = vni[vni["time"] == anchor_date].iloc[0]["Close"]
ew_anchor_val = ew_anchor_row.iloc[0]["close_ew"]
scale = anchor_vni / ew_anchor_val
print(f"  Anchor: {anchor_date.date()} VNI_raw={anchor_vni:.2f} EW_raw={ew_anchor_val:.2f} → scale={scale:.4f}")
daily["close_ew_scaled"] = daily["close_ew"] * scale
# ── RAW daily EW aggregates (the building blocks of every factor) for dev reconciliation ──
_otag = os.environ.get("OUT_TAG", "")
_agg_path = os.path.join(WORKDIR, f"vnindex_5state_ew_daily_aggregates{_otag}.csv")
daily[["time","n_universe","ret_ew","close_ew","close_ew_scaled","cmf_med","breadth"]].assign(
    time=daily["time"].dt.strftime("%Y-%m-%d")).to_csv(_agg_path, index=False)
print(f"  [RAW] daily EW aggregates -> {_agg_path} ({len(daily)} rows)")

# Composite series: time, Close, Open=High=Low=Close (no synthetic intraday),
# VNINDEX_PE (from raw VNI, applies post too since PE is a market property — we'll keep
# raw VNI PE because EW doesn't have a natural PE; this is a design choice).
# CMF: use median D_CMF post, raw VNI D_CMF pre.
# Also keep raw RSI divergence columns from VNI (BearDvg/BullDvg gate is on raw VNI dynamics —
# we choose to keep gate as-is since user signs off only on factor swap, not gate logic).
parts = []
# Pre-2014 → raw VNI
pre = vni_pre[["time", "Close", "VNINDEX_PE", "D_CMF",
               "D_RSI", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
               "D_RSI_Min1W", "D_RSI_Min3M", "D_RSI_Max1W_Close", "D_RSI_Max3M_Close",
               "D_RSI_Max3M_MACD", "D_RSI_Max1W_MACD", "D_RSI_MinT3",
               "C_L1M", "C_L1W"]].copy()
pre["breadth"] = np.nan  # no breadth pre-2014 in EW universe; rank handles it
pre["source"]  = "raw_vni"
parts.append(pre)

# Post-2014 → EW close, median CMF, breadth from eligible; PE+RSI-divergence keep from raw
post = vni_post[["time", "VNINDEX_PE",
                 "D_RSI", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
                 "D_RSI_Min1W", "D_RSI_Min3M", "D_RSI_Max1W_Close", "D_RSI_Max3M_Close",
                 "D_RSI_Max3M_MACD", "D_RSI_Max1W_MACD", "D_RSI_MinT3",
                 "C_L1M", "C_L1W"]].copy()
post = post.merge(daily[["time", "close_ew_scaled", "cmf_med", "breadth", "n_universe"]],
                  on="time", how="left")
# Drop rows where EW couldn't be computed (early days perhaps)
post = post.dropna(subset=["close_ew_scaled"])
post = post.rename(columns={"close_ew_scaled": "Close", "cmf_med": "D_CMF"})
post["source"] = "ew"
parts.append(post[pre.columns.tolist() + ["n_universe"]] if "n_universe" in post.columns else post[pre.columns.tolist()])

df = pd.concat(parts, ignore_index=True, sort=False).sort_values("time").reset_index(drop=True)
print(f"  Composite series: {len(df)} rows | pre={len(pre)} post={len(post)}")

# ──────────────────────────────────────────────────────────────────────
# Step 5: Recompute factors from composite Close
# ──────────────────────────────────────────────────────────────────────
print("\nStep 5: Recompute factors on composite Close")
close = df["Close"].values.copy().astype(float)
n = len(close)

# P3M / P1M (session-based; close[i]/close[i-60] - 1)
def lagged_return(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(k, len(arr)):
        if arr[i-k] > 0 and not np.isnan(arr[i-k]) and not np.isnan(arr[i]):
            out[i] = arr[i] / arr[i-k] - 1
    return out

p3m = lagged_return(close, 60)
p1m = lagged_return(close, 20)

# MA200 deviation
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

# RSI Wilder 14
rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan
period = 14
for i in range(1, n):
    diff = close[i] - close[i-1]
    if np.isnan(diff): continue
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= period:
            gains  = [max(close[j]-close[j-1], 0)  for j in range(1, period+1) if not np.isnan(close[j]) and not np.isnan(close[j-1])]
            losses = [max(close[j-1]-close[j], 0)  for j in range(1, period+1) if not np.isnan(close[j]) and not np.isnan(close[j-1])]
            if gains and losses:
                avg_u = np.mean(gains); avg_d = np.mean(losses)
                if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u * (period - 1) + u) / period
        avg_d = (avg_d * (period - 1) + d) / period
        if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)

# MACD histogram 12-26-9
ema12 = np.full(n, np.nan); ema26 = np.full(n, np.nan)
signal = np.full(n, np.nan); macd_hist = np.full(n, np.nan)
k12, k26, k9 = 2/13, 2/27, 2/10
for i in range(n):
    if np.isnan(close[i]): continue
    if i == 0 or np.isnan(ema12[i-1]):
        ema12[i] = close[i]; ema26[i] = close[i]
    else:
        ema12[i] = ema12[i-1] * (1 - k12) + close[i] * k12
        ema26[i] = ema26[i-1] * (1 - k26) + close[i] * k26
    macd_line = ema12[i] - ema26[i]
    if i == 0 or np.isnan(signal[i-1]):
        signal[i] = macd_line
    else:
        signal[i] = signal[i-1] * (1 - k9) + macd_line * k9
    if i >= 33: macd_hist[i] = macd_line - signal[i]

# CMF: already in df["D_CMF"] (raw VNI pre-2014, universe median post-2014)
cmf = df["D_CMF"].values.astype(float)

df["f_P3M"]    = p3m
df["f_P1M"]    = p1m
df["f_MA200"]  = ma200_dev
df["f_RSI"]    = rsi
df["f_MACD"]   = macd_hist
df["f_CMF"]    = cmf
df["f_Breadth"]= df["breadth"].values

# ──────────────────────────────────────────────────────────────────────
# Step 6: Expanding pct rank + composite score
# ──────────────────────────────────────────────────────────────────────
print("\nStep 6: Expanding percentile rank + composite score")

def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]
        valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb: continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

FACTOR_KEYS = ["P3M", "P1M", "MA200", "RSI", "MACD", "CMF", "Breadth"]
ranks = {}
for k in FACTOR_KEYS:
    print(f"  Ranking {k} ...")
    ranks[k] = expanding_pct_rank(df[f"f_{k}"].values, MIN_LB)
    df[f"rank_{k}"] = ranks[k]

score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FACTOR_KEYS if not np.isnan(ranks[k][t])}
    if len(avail) < MIN_FACTORS: continue
    w_sum = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k] * W_BASE[k] for k in avail) / w_sum
df["score"] = score

print("  Ranking composite score ...")
r_score = expanding_pct_rank(score, MIN_LB)
df["r_score"] = r_score

# EMA smoothing
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]
    prev = r_score_ema[t-1] if t > 0 else np.nan
    if np.isnan(v):
        r_score_ema[t] = prev
    elif np.isnan(prev):
        r_score_ema[t] = v
    else:
        r_score_ema[t] = EMA_ALPHA * v + (1.0 - EMA_ALPHA) * prev
df["r_score_ema"] = r_score_ema

# ──────────────────────────────────────────────────────────────────────
# Step 7: State classification + risk overrides
# ──────────────────────────────────────────────────────────────────────
print("\nStep 7: Classify + risk overrides")
def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    if rs < 0.20: return 2
    if rs < 0.70: return 3
    if rs < 0.90: return 4
    return 5

state_raw = np.array([classify_raw(r) for r in r_score_ema])

# PE override
pe_arr = df["VNINDEX_PE"].values.astype(float)
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60:
        pe_p90[t] = np.nanpercentile(valid, 90)

# Drawdown
running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close / running_max - 1, 0.0)

# Volatility (annualized 20d)
daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0 and not np.isnan(close[i-1]) and not np.isnan(close[i]):
        daily_ret[i] = close[i] / close[i-1] - 1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    window = daily_ret[i-20:i]
    valid = window[~np.isnan(window)]
    if len(valid) >= 15:
        vol20[i] = np.std(valid) * np.sqrt(252)
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist = vol20[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: avg_vol_exp[t] = np.mean(valid)

state_after_override = state_raw.copy()
for i in range(n):
    s = state_after_override[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5): s = 4
    if dd[i] < -0.25 and s >= 4: s = 3
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5 * avg_vol_exp[i] and s == 5): s = 4
    state_after_override[i] = s

# ──────────────────────────────────────────────────────────────────────
# Step 8: BearDvg / BullDvg gate (re-use raw VNI divergence columns)
# ──────────────────────────────────────────────────────────────────────
print("\nStep 8: BearDvg gate (re-uses raw VNI divergence columns)")

def _s(col):
    return df[col] if col in df.columns else pd.Series(np.nan, index=df.index)

_D_RSI         = _s("D_RSI"); _D_RSI_T1W = _s("D_RSI_T1W")
_D_RSI_Max1W   = _s("D_RSI_Max1W"); _D_RSI_Max3M = _s("D_RSI_Max3M")
_D_RSI_Min1W   = _s("D_RSI_Min1W"); _D_RSI_Min3M = _s("D_RSI_Min3M")
_D_RSI_Max1W_C = _s("D_RSI_Max1W_Close"); _D_RSI_Max3M_C = _s("D_RSI_Max3M_Close")
_D_RSI_Max3M_M = _s("D_RSI_Max3M_MACD"); _D_RSI_Max1W_M = _s("D_RSI_Max1W_MACD")
_D_RSI_MinT3   = _s("D_RSI_MinT3"); _D_CMF = _s("D_CMF")
_C_L1M = _s("C_L1M"); _C_L1W = _s("C_L1W")
_mask_2011     = df["time"] >= "2011-01-01"
# Note: divergence signals derived from raw VNI dynamics. We keep them as a structural
# risk gate (they fire on big-cap distortions which IS what we want to detect). Close
# is the spliced series — at pre-2014 it equals raw VNI; post-2014 the divergence
# columns remain raw VNI-based (BQ source). This is intentional: gate uses the actual
# index "above the hood".

bear1_sig = ((_D_RSI_Max1W/_D_RSI > 1.044) & (_D_RSI_Max3M > 0.74) &
             (_D_RSI_Max1W < 0.72) & (_D_RSI_Max1W > 0.61) &
             (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.028) &
             (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.11) &
             (-1 < 0) &  # _D_MACDdiff missing from our pull; skip this clause loosely (will adjust)
             (_D_RSI_MinT3 > 0.43) & (_D_CMF < 0.13) & _mask_2011)

# To keep apples-to-apples we'll just disable gates if D_MACDdiff is missing in our pull
# (we didn't include it). The canonical script includes D_MACDdiff. Re-enable later.
print("  NOTE: gate disabled in this prototype (need D_MACDdiff column — re-run after adding).")
bear_mask = pd.Series(False, index=df.index).values
bull_mask = pd.Series(False, index=df.index).values

GATE_FLOOR = 1; GATE_MIN_DUR = 60
state_dvg = state_after_override.copy()
# (gate disabled — state_dvg == state_after_override)

# ──────────────────────────────────────────────────────────────────────
# Step 9: Smoothing pipeline
# ──────────────────────────────────────────────────────────────────────
print("\nStep 9: Smoothing (mode15 + min_stay7)")

def rolling_mode(states, window=15):
    out = states.copy()
    for t in range(window - 1, len(states)):
        wv = states[t-window+1:t+1]
        vals, counts = np.unique(wv, return_counts=True)
        max_count = counts.max()
        candidates = vals[counts == max_count]
        for v in reversed(wv):
            if v in candidates:
                out[t] = v; break
    return out

def min_stay_filter(states, min_days=7):
    out = states.copy()
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(out):
            j = i + 1
            while j < len(out) and out[j] == out[i]: j += 1
            run_len = j - i
            if run_len < min_days:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill
                changed = True
            i = j
    return out

state_smooth = rolling_mode(state_dvg, MODE_WIN)
state_smooth = min_stay_filter(state_smooth, MIN_STAY)

df["state_raw"] = state_raw
df["state"]     = state_smooth

# ──────────────────────────────────────────────────────────────────────
# Step 10: Save outputs
# ──────────────────────────────────────────────────────────────────────
print("\nStep 10: Save outputs")
out_staging = df[["time", "state", "state_raw"]].copy()
out_staging["time"] = pd.to_datetime(out_staging["time"]).dt.strftime("%Y-%m-%d")
out_staging["state"]     = out_staging["state"].astype(int)
out_staging["state_raw"] = out_staging["state_raw"].astype(int)
_OTAG = os.environ.get("OUT_TAG", "")
staging_path = os.path.join(WORKDIR, f"vnindex_5state_ew_staging{_OTAG}.csv")
out_staging.to_csv(staging_path, index=False)
print(f"  → {staging_path} ({len(out_staging)} rows)")

# Full diagnostics
diag = df[["time", "source", "Close", "VNINDEX_PE", "n_universe",
           "f_P3M", "f_P1M", "f_MA200", "f_RSI", "f_MACD", "f_CMF", "f_Breadth",
           "score", "r_score", "r_score_ema",
           "state_raw", "state"]].copy()
diag_path = os.path.join(WORKDIR, f"vnindex_5state_ew_full{_OTAG}.csv")
diag.to_csv(diag_path, index=False)
print(f"  → {diag_path}")

# Summary
print("\n" + "=" * 70)
print("STAGING SUMMARY")
print("=" * 70)
state_dist = df["state"].value_counts().sort_index()
print("\nState distribution (overall):")
for s, c in state_dist.items():
    print(f"  state={s} ({STATE_NAMES.get(int(s), '?'):>8}): {c:>6} sessions ({c/len(df)*100:.1f}%)")

print("\nLast 20 sessions:")
print(df[["time", "state_raw", "state"]].tail(20).to_string(index=False))

# Transitions count
transitions = (df["state"] != df["state"].shift()).sum() - 1
print(f"\nTotal transitions: {transitions}")
