# -*- coding: utf-8 -*-
"""
vnindex_5state_dual_v1.py
=========================
Dual-system 5-state: score-level blend of raw VNINDEX + VNINDEX_EW.

Rationale: VNINDEX still drives market psychology (cap-weighted, what retail watches);
EW measures broad participation. Blending the two pct-rank composite scores lets
psychology lead but requires broad confirmation.

Blend formula (BEFORE EMA):
    r_score_dual[t] = α × r_score_raw[t] + (1-α) × r_score_ew[t]

Then:
    EMA(0.40) → classify(<.10/<.20/<.70/<.90/≥.90) → risk overrides (PE, DD, vol)
    → rolling_mode(15) → min_stay_filter(7)

Pre-2014: pure raw VNI (EW universe sparse).
Risk overrides: applied to raw VNI PE/DD/vol (consistent with LIVE Cổ Điển/Tinh Tế).
BearDvg gate: NOT included in this prototype (would re-use raw VNI dynamics — fine
to leave out for first integrated test; LIVE archive doesn't have it in archive_co_dien).

Outputs:
  vnindex_5state_dual_a{XX}_staging.csv  for α ∈ {0.3, 0.4, 0.5, 0.6, 0.7}
  Each is uploadable via deploy_ngu_hanh.py --to-staging.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# Params (canonical Cổ Điển — apples-to-apples)
W_BASE      = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
               "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
MODE_WIN    = 15
MIN_STAY    = 7
EMA_ALPHA   = 0.40
EW_START    = pd.Timestamp("2014-01-01")
ALPHAS      = [0.30, 0.40, 0.50, 0.60, 0.70]  # raw weight (1-α = EW weight)
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

CACHE_VNI    = os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl")
EW_FULL_CSV  = os.path.join(WORKDIR, "data/vnindex_5state_ew_full.csv")

print("=" * 70)
print("Dual-system 5-state — α-sweep build")
print("=" * 70)

# ──────────────────────────────────────────────────────────────────────
# Step 1: Load raw VNI (cached) + EW factors from previous run
# ──────────────────────────────────────────────────────────────────────
print("\nStep 1: Load raw VNI + EW factors")
vni = pd.read_pickle(CACHE_VNI)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
print(f"  raw VNI: {len(vni)} rows | {vni['time'].min().date()} → {vni['time'].max().date()}")

ew_full = pd.read_csv(EW_FULL_CSV)
ew_full["time"] = pd.to_datetime(ew_full["time"])
print(f"  EW factors: {len(ew_full)} rows")

# ──────────────────────────────────────────────────────────────────────
# Step 2: Compute factors on raw VNI (same logic as canonical script)
# ──────────────────────────────────────────────────────────────────────
print("\nStep 2: Compute factors on RAW VNI")
close = vni["Close"].values.astype(float)
n = len(close)

def lagged_return(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(k, len(arr)):
        if arr[i-k] > 0 and not np.isnan(arr[i-k]) and not np.isnan(arr[i]):
            out[i] = arr[i] / arr[i-k] - 1
    return out

p3m = lagged_return(close, 60)
p1m = lagged_return(close, 20)
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

# RSI Wilder 14
rsi = np.full(n, np.nan); avg_u = avg_d = np.nan; period = 14
for i in range(1, n):
    diff = close[i] - close[i-1]
    if np.isnan(diff): continue
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= period:
            gains  = [max(close[j]-close[j-1], 0)  for j in range(1, period+1)]
            losses = [max(close[j-1]-close[j], 0)  for j in range(1, period+1)]
            if gains and losses:
                avg_u = np.mean(gains); avg_d = np.mean(losses)
                if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u * (period - 1) + u) / period
        avg_d = (avg_d * (period - 1) + d) / period
        if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)

# MACD histogram
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

# CMF for raw VNI = D_CMF column (already in VNI pull)
cmf_raw = vni["D_CMF"].values.astype(float)

# Breadth for raw side = no direct breadth; reuse EW's breadth post-2014, NaN pre-2014
# (raw factors don't have breadth — this is one reason EW adds value)
# We pre-merge EW breadth into the same time-aligned series.
vni["f_P3M"]    = p3m
vni["f_P1M"]    = p1m
vni["f_MA200"]  = ma200_dev
vni["f_RSI"]    = rsi
vni["f_MACD"]   = macd_hist
vni["f_CMF"]    = cmf_raw

# Merge breadth from EW full
vni = vni.merge(ew_full[["time", "f_Breadth"]], on="time", how="left")
# Pre-2014 breadth NaN — that's OK, expanding rank handles it (just one less factor)

print("  Raw VNI factors computed.")

# ──────────────────────────────────────────────────────────────────────
# Step 3: Compute r_score for raw VNI
# ──────────────────────────────────────────────────────────────────────
print("\nStep 3: Composite + r_score (raw VNI)")
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
ranks_raw = {}
for k in FACTOR_KEYS:
    print(f"  Rank {k} (raw) ...")
    ranks_raw[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

score_raw = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks_raw[k][t] for k in FACTOR_KEYS if not np.isnan(ranks_raw[k][t])}
    if len(avail) < MIN_FACTORS: continue
    w_sum = sum(W_BASE[k] for k in avail)
    score_raw[t] = sum(avail[k] * W_BASE[k] for k in avail) / w_sum
vni["score_raw"] = score_raw

print("  Ranking composite (raw) ...")
r_score_raw = expanding_pct_rank(score_raw, MIN_LB)
vni["r_score_raw"] = r_score_raw

# ──────────────────────────────────────────────────────────────────────
# Step 4: Merge EW r_score
# ──────────────────────────────────────────────────────────────────────
print("\nStep 4: Merge r_score from EW")
df = vni.merge(ew_full[["time", "r_score"]].rename(columns={"r_score":"r_score_ew"}),
               on="time", how="left")
# Pre-2014: r_score_ew is NaN → fallback to r_score_raw (no blend possible there)
# Post-2014: both available → blend

# ──────────────────────────────────────────────────────────────────────
# Step 5: For each α, build full state pipeline
# ──────────────────────────────────────────────────────────────────────
print("\nStep 5: Per-α pipeline")
pe_arr = vni["VNINDEX_PE"].values.astype(float)

# Common: PE P90, DD, vol20 (computed once on raw VNI Close — same as canonical)
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: pe_p90[t] = np.nanpercentile(valid, 90)

running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close / running_max - 1, 0.0)

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

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    if rs < 0.20: return 2
    if rs < 0.70: return 3
    if rs < 0.90: return 4
    return 5

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

results = {}  # alpha -> (state_raw, state_smooth)
r_raw  = df["r_score_raw"].values
r_ew   = df["r_score_ew"].values

for alpha in ALPHAS:
    label = f"a{int(alpha*100):02d}"
    print(f"\n  Building α={alpha:.2f} (raw weight)  →  EW weight = {1-alpha:.2f}")
    # Blend pre-EMA: if EW missing (pre-2014), use raw only
    r_dual = np.where(np.isnan(r_ew), r_raw,
                      np.where(np.isnan(r_raw), r_ew,
                               alpha * r_raw + (1-alpha) * r_ew))
    # EMA
    rs_ema = np.full(n, np.nan)
    for t in range(n):
        v = r_dual[t]
        prev = rs_ema[t-1] if t > 0 else np.nan
        if np.isnan(v): rs_ema[t] = prev
        elif np.isnan(prev): rs_ema[t] = v
        else: rs_ema[t] = EMA_ALPHA * v + (1.0 - EMA_ALPHA) * prev
    # Classify
    s_raw = np.array([classify_raw(r) for r in rs_ema])
    # Risk overrides
    s_or = s_raw.copy()
    for i in range(n):
        s = s_or[i]
        if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
                and pe_arr[i] > pe_p90[i] and s == 5): s = 4
        if dd[i] < -0.25 and s >= 4: s = 3
        if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
                and vol20[i] > 1.5 * avg_vol_exp[i] and s == 5): s = 4
        s_or[i] = s
    # Smooth
    s_sm = rolling_mode(s_or, MODE_WIN)
    s_sm = min_stay_filter(s_sm, MIN_STAY)
    results[alpha] = (s_raw, s_sm, rs_ema)
    # Save staging CSV
    out_df = pd.DataFrame({
        "time": df["time"].dt.strftime("%Y-%m-%d"),
        "state": s_sm.astype(int),
        "state_raw": s_raw.astype(int),
    })
    out_path = os.path.join(WORKDIR, f"vnindex_5state_dual_{label}_staging.csv")
    out_df.to_csv(out_path, index=False)
    print(f"    → {out_path}")

# ──────────────────────────────────────────────────────────────────────
# Step 6: Compare distributions vs LIVE
# ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STATE DISTRIBUTION (post-2014)")
print("=" * 70)

# Pull LIVE for reference
import subprocess, tempfile
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
sql = "SELECT time, state, state_raw FROM tav2_bq.vnindex_5state WHERE time >= '2014-01-01' ORDER BY time"
with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(sql); qp = f.name
cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000 < "{qp}"'
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
os.unlink(qp)
live = pd.read_csv(io.StringIO(r.stdout))
live["time"] = pd.to_datetime(live["time"])

# Subset post-2014
df14 = df[df["time"] >= "2014-01-01"].reset_index(drop=True)
n14_idx = df14.index
post_mask = df["time"] >= "2014-01-01"

print(f"\n  {'State':<10} {'LIVE':>10} | " + " | ".join(f"α={a:.2f}" for a in ALPHAS))
state_names_list = [1,2,3,4,5]
live_dist = live["state"].value_counts(normalize=True).reindex(state_names_list, fill_value=0) * 100
for s in state_names_list:
    row_parts = [f"  {STATE_NAMES[s]:<10} {live_dist[s]:>9.1f}%"]
    for a in ALPHAS:
        s_sm = results[a][1][post_mask.values]
        pct = (s_sm == s).mean() * 100
        row_parts.append(f"  {pct:>5.1f}%")
    print(" | ".join(row_parts))

# Transition count
def n_trans(s):
    arr = np.asarray(s)
    return int((arr[1:] != arr[:-1]).sum())
print(f"\n  Transitions post-2014:")
print(f"    LIVE: {n_trans(live['state'].values)}")
for a in ALPHAS:
    print(f"    α={a:.2f}: {n_trans(results[a][1][post_mask.values])}")

# Recent state comparison
print("\n" + "=" * 70)
print("RECENT 15 SESSIONS — state comparison")
print("=" * 70)
live_recent = live.set_index("time")
header = f"  {'time':<12} {'LIVE':>5} | " + " | ".join(f"α{a:.1f}" for a in ALPHAS)
print(header)
recent_dates = df[df["time"] >= "2026-04-29"]["time"].tail(15).values
for t in recent_dates:
    t_ts = pd.Timestamp(t)
    live_s = int(live_recent.loc[t_ts, "state"]) if t_ts in live_recent.index else 0
    row = f"  {t_ts.strftime('%Y-%m-%d'):<12} {STATE_NAMES.get(live_s, '?')[:3]:>5}"
    for a in ALPHAS:
        s_sm = results[a][1]
        # find index
        idx = df[df["time"] == t_ts].index
        if len(idx) > 0:
            s = int(s_sm[idx[0]])
            row += f" | {STATE_NAMES.get(s,'?')[:3]:>3}"
        else:
            row += f" | ???"
    print(row)

# Year %BULL+ for each variant
print("\n" + "=" * 70)
print("YEAR-BY-YEAR %BULL+EX-BULL (risk-on bias)")
print("=" * 70)
df14_state_live = live.copy(); df14_state_live["year"] = df14_state_live["time"].dt.year
df14["year"] = df14["time"].dt.year

print(f"  {'Year':<6} {'LIVE':>6} | " + " | ".join(f"α{a:.1f}" for a in ALPHAS))
years = sorted(df14["year"].unique())
for y in years:
    parts = [f"  {y:<6}"]
    live_y = df14_state_live[df14_state_live["year"] == y]
    parts.append(f" {(live_y['state'].isin([4,5])).mean()*100:>5.1f}%")
    for a in ALPHAS:
        s_sm = results[a][1]
        ymask = (df["time"].dt.year == y) & post_mask
        vals = s_sm[ymask.values]
        pct = (np.isin(vals, [4,5])).mean() * 100 if len(vals) else 0
        parts.append(f" {pct:>4.1f}%")
    print(" | ".join(parts))

print("\n" + "=" * 70)
print("DONE — 5 staging CSVs written, one per α.")
print("Pick the α you want to take to integrated V11 backtest.")
print("=" * 70)
