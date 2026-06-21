# -*- coding: utf-8 -*-
"""
vnindex_5state_dual_v2_dynamic.py
=================================
v2: dynamic-α dual-system. α varies with concentration_score:

  α(c) = clip(1.0 − 2.0 × max(0, c_smooth − 0.5), min=0.3, max=1.0)

  c_smooth = EMA(0.20) of concentration_score
  c < 0.5  → α=1.0  (pure LIVE — broad market, no degradation)
  c = 0.6  → α=0.8  (mild blend)
  c = 0.7  → α=0.6  (moderate blend)
  c = 0.85 → α=0.3  (heavy EW lean, capped)
  c > 0.85 → α=0.3  (floor — never go full EW)

Same downstream as v1 (mode15 + min_stay7 + risk overrides).
Pre-252-session: c=NaN → α=1.0 default.

Output: vnindex_5state_dual_v2_staging.csv + diagnostic vnindex_5state_dual_v2_full.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

W_BASE      = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15, "RSI": 0.15,
               "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
MODE_WIN    = 15
MIN_STAY    = 7
EMA_ALPHA   = 0.40   # EMA on r_score (state machine)
CONC_EMA    = 0.20   # EMA on concentration_score (smooth α changes)
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

print("="*70)
print("v2 Dynamic-α Dual System")
print("="*70)

# ─────────────────────────────────────────────────────────────────────
# Load r_score_raw + r_score_ew from previous artifacts
# ─────────────────────────────────────────────────────────────────────
print("\n[1] Load r_scores + concentration history")
ew_full = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_ew_full.csv"))
ew_full["time"] = pd.to_datetime(ew_full["time"])
# ew_full has r_score (= r_score_ew)
ew_full = ew_full.rename(columns={"r_score": "r_score_ew"})

# Need r_score_raw — recompute by running same logic as canonical on raw VNI
# Re-use cached VNI pickle.
vni = pd.read_pickle(os.path.join(WORKDIR, "_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

# Recompute factors on raw VNI (same as v1 dual)
close = vni["Close"].values.astype(float)
n = len(close)

def lagged_return(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(k, len(arr)):
        if arr[i-k] > 0 and not np.isnan(arr[i-k]) and not np.isnan(arr[i]):
            out[i] = arr[i] / arr[i-k] - 1
    return out

p3m = lagged_return(close, 60); p1m = lagged_return(close, 20)
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

rsi = np.full(n, np.nan); avg_u = avg_d = np.nan
for i in range(1, n):
    diff = close[i] - close[i-1]
    if np.isnan(diff): continue
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= 14:
            gains  = [max(close[j]-close[j-1], 0)  for j in range(1, 15)]
            losses = [max(close[j-1]-close[j], 0)  for j in range(1, 15)]
            avg_u = np.mean(gains); avg_d = np.mean(losses)
            if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u * 13 + u) / 14; avg_d = (avg_d * 13 + d) / 14
        if (avg_u + avg_d) > 0: rsi[i] = avg_u / (avg_u + avg_d)

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
    if i == 0 or np.isnan(signal[i-1]): signal[i] = macd_line
    else: signal[i] = signal[i-1] * (1 - k9) + macd_line * k9
    if i >= 33: macd_hist[i] = macd_line - signal[i]

cmf_raw = vni["D_CMF"].values.astype(float)
vni["f_P3M"]    = p3m;       vni["f_P1M"]    = p1m
vni["f_MA200"]  = ma200_dev; vni["f_RSI"]    = rsi
vni["f_MACD"]   = macd_hist; vni["f_CMF"]    = cmf_raw

# Breadth from EW (only post-2014)
vni = vni.merge(ew_full[["time", "f_Breadth"]], on="time", how="left")

def expanding_pct_rank(arr, min_lb=252):
    arr = np.asarray(arr, dtype=float)
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb: continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

FACTOR_KEYS = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
print("[2] Rank factors on raw VNI")
ranks_raw = {}
for k in FACTOR_KEYS:
    print(f"  Rank {k} ...")
    ranks_raw[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

print("[3] Composite + r_score (raw)")
score_raw = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks_raw[k][t] for k in FACTOR_KEYS if not np.isnan(ranks_raw[k][t])}
    if len(avail) < MIN_FACTORS: continue
    w_sum = sum(W_BASE[k] for k in avail)
    score_raw[t] = sum(avail[k] * W_BASE[k] for k in avail) / w_sum
r_score_raw = expanding_pct_rank(score_raw, MIN_LB)
vni["r_score_raw"] = r_score_raw

# ─────────────────────────────────────────────────────────────────────
# Merge EW + concentration
# ─────────────────────────────────────────────────────────────────────
print("[4] Merge EW r_score + concentration history")
df = vni.merge(ew_full[["time", "r_score_ew"]], on="time", how="left")
conc = pd.read_csv(os.path.join(WORKDIR, "concentration_history.csv"))
conc["time"] = pd.to_datetime(conc["time"])
df = df.merge(conc[["time", "concentration_score"]], on="time", how="left")

# Smooth concentration_score
cs = df["concentration_score"].values
cs_ema = np.full(len(cs), np.nan)
for t in range(len(cs)):
    v = cs[t]; prev = cs_ema[t-1] if t > 0 else np.nan
    if np.isnan(v): cs_ema[t] = prev
    elif np.isnan(prev): cs_ema[t] = v
    else: cs_ema[t] = CONC_EMA * v + (1 - CONC_EMA) * prev
df["concentration_smooth"] = cs_ema

# Compute alpha
def alpha_from_score(c):
    if np.isnan(c): return 1.0  # no concentration data → pure LIVE
    return max(0.3, min(1.0, 1.0 - 2.0 * max(0, c - 0.5)))

df["alpha"] = df["concentration_smooth"].apply(alpha_from_score)

# Blend r_score
r_raw = df["r_score_raw"].values
r_ew  = df["r_score_ew"].values
a     = df["alpha"].values
r_dual = np.where(np.isnan(r_ew), r_raw,
                  np.where(np.isnan(r_raw), r_ew, a * r_raw + (1-a) * r_ew))

# EMA → classify → overrides → smooth
print("[5] Pipeline: EMA → classify → overrides → smooth")
rs_ema = np.full(n, np.nan)
for t in range(n):
    v = r_dual[t]
    prev = rs_ema[t-1] if t > 0 else np.nan
    if np.isnan(v): rs_ema[t] = prev
    elif np.isnan(prev): rs_ema[t] = v
    else: rs_ema[t] = EMA_ALPHA * v + (1.0 - EMA_ALPHA) * prev

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    if rs < 0.20: return 2
    if rs < 0.70: return 3
    if rs < 0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in rs_ema])

# Risk overrides — use raw VNI PE
pe_arr = vni["VNINDEX_PE"].values.astype(float)
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

s_or = state_raw.copy()
for i in range(n):
    s = s_or[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5): s = 4
    if dd[i] < -0.25 and s >= 4: s = 3
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5 * avg_vol_exp[i] and s == 5): s = 4
    s_or[i] = s

def rolling_mode(states, window=15):
    out = states.copy()
    for t in range(window - 1, len(states)):
        wv = states[t-window+1:t+1]
        vals, counts = np.unique(wv, return_counts=True)
        max_count = counts.max()
        candidates = vals[counts == max_count]
        for v in reversed(wv):
            if v in candidates: out[t] = v; break
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
                out[i:j] = fill; changed = True
            i = j
    return out

s_sm = rolling_mode(s_or, MODE_WIN)
s_sm = min_stay_filter(s_sm, MIN_STAY)

df["r_dual"] = r_dual
df["r_dual_ema"] = rs_ema
df["state_raw"] = state_raw
df["state"]     = s_sm

# ─────────────────────────────────────────────────────────────────────
# Save outputs
# ─────────────────────────────────────────────────────────────────────
out_staging = pd.DataFrame({
    "time": df["time"].dt.strftime("%Y-%m-%d"),
    "state": df["state"].astype(int),
    "state_raw": df["state_raw"].astype(int),
})
out_staging.to_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v2_staging.csv"), index=False)

diag = df[["time", "Close", "concentration_score", "concentration_smooth", "alpha",
           "r_score_raw", "r_score_ew", "r_dual", "r_dual_ema",
           "state_raw", "state"]].copy()
diag.to_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v2_full.csv"), index=False)

# ─────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Distribution
print("\nState distribution (post-2014):")
post = df[df["time"] >= "2014-01-01"]
dist = post["state"].value_counts(normalize=True).sort_index() * 100
for s in [1,2,3,4,5]:
    print(f"  {STATE_NAMES[s]:<10} {dist.get(s, 0.0):>5.1f}%")

# α distribution
print(f"\nα distribution (post-2014):")
print(f"  α = 1.00 (pure LIVE): {(post['alpha']>=0.999).mean()*100:>5.1f}% of days")
print(f"  0.7 ≤ α < 1.0:        {((post['alpha']>=0.7) & (post['alpha']<0.999)).mean()*100:>5.1f}% of days")
print(f"  0.5 ≤ α < 0.7:        {((post['alpha']>=0.5) & (post['alpha']<0.7)).mean()*100:>5.1f}% of days")
print(f"  α < 0.5 (heavy EW):   {(post['alpha']<0.5).mean()*100:>5.1f}% of days")
print(f"  α = 0.30 (floor):     {(post['alpha']<=0.301).mean()*100:>5.1f}% of days")

# Transitions
def n_trans(s):
    arr = np.asarray(s)
    return int((arr[1:] != arr[:-1]).sum())
print(f"\nTransitions post-2014: {n_trans(post['state'].values)}")

print(f"\nLast 20 sessions:")
recent = df.tail(20)[["time", "concentration_smooth", "alpha", "r_dual_ema", "state_raw", "state"]].copy()
recent["time"] = recent["time"].dt.strftime("%Y-%m-%d")
for _, r in recent.iterrows():
    print(f"  {r['time']}  c={r['concentration_smooth']:.2f}  α={r['alpha']:.2f}  "
          f"r_dual={r['r_dual_ema']:.3f}  raw={int(r['state_raw'])} state={STATE_NAMES.get(int(r['state']), '?')[:7]}")

print(f"\nDone — staging written to vnindex_5state_dual_v2_staging.csv")
