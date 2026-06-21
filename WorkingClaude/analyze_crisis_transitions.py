# -*- coding: utf-8 -*-
"""
analyze_crisis_transitions.py
==============================
Phân tích path transition vào CRISIS:
- Prior state (BEAR/NEUTRAL/BULL/EX-BULL) + duration trong prior state
- Market return sau khi vào CRISIS (1W, 1M, 3M)
- Phân loại "True CRISIS" vs "False CRISIS" dựa trên forward return
- Thống kê để calibrate allocation hợp lý theo từng path
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ══════════════════════════════════════════════════════════════════════
# PARAMETERS (giống vnindex_5state_system.py)
# ══════════════════════════════════════════════════════════════════════
W_BASE = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
          "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
MODE_WIN    = 15
MIN_STAY    = 7
EMA_ALPHA   = 0.40
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

# ══════════════════════════════════════════════════════════════════════
# LOAD & PREPARE DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data ...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

for col in ["Open", "High", "Low", "Close", "Volume", "VNINDEX_PE",
            "D_RSI", "D_MACDdiff", "D_CMF", "C_L1M", "C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

breadth_path = os.path.join(WORKDIR, "breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    breadth["breadth"] = pd.to_numeric(breadth["breadth"], errors="coerce")
    vni = vni.merge(breadth, on="time", how="left")
else:
    vni["breadth"] = np.nan

n = len(vni)
close = vni["Close"].values.copy()
print(f"  {n} sessions | {vni['time'].min().date()} → {vni['time'].max().date()}")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE INDICATORS (rút gọn từ vnindex_5state_system.py)
# ══════════════════════════════════════════════════════════════════════
print("Computing indicators ...")

def rolling_ret(arr, w):
    out = np.full(len(arr), np.nan)
    for i in range(w, len(arr)):
        if arr[i-w] > 0:
            out[i] = arr[i] / arr[i-w] - 1
    return out

def expanding_rank(arr, min_lb=MIN_LB):
    out = np.full(len(arr), np.nan)
    for i in range(min_lb, len(arr)):
        window = arr[max(0,i-3000):i+1]
        valid  = window[~np.isnan(window)]
        if len(valid) < 10:
            continue
        v = arr[i]
        if np.isnan(v):
            continue
        out[i] = np.searchsorted(np.sort(valid), v) / len(valid)
    return out

# P3M (63 sessions), P1M (21 sessions)
p3m = rolling_ret(close, 63)
p1m = rolling_ret(close, 21)

# MA200 deviation
ma200 = np.full(n, np.nan)
for i in range(199, n):
    ma200[i] = np.mean(close[i-199:i+1])
ma200_dev = np.where(ma200 > 0, close / ma200 - 1, np.nan)

# RSI-Wilder 14
rsi = np.full(n, np.nan)
if "D_RSI" in vni.columns:
    rsi = vni["D_RSI"].values.copy()
else:
    gains = np.zeros(n); losses = np.zeros(n)
    for i in range(1, n):
        d = close[i] - close[i-1]
        gains[i]  = max(d, 0)
        losses[i] = max(-d, 0)
    avg_g = np.full(n, np.nan); avg_l = np.full(n, np.nan)
    avg_g[14] = np.mean(gains[1:15]); avg_l[14] = np.mean(losses[1:15])
    for i in range(15, n):
        avg_g[i] = (avg_g[i-1]*13 + gains[i]) / 14
        avg_l[i] = (avg_l[i-1]*13 + losses[i]) / 14
    rs = np.where(avg_l > 0, avg_g / avg_l, 100)
    rsi = np.where(avg_l > 0, 1 - 1/(1+rs), 1.0)

# MACD hist
if "D_MACDdiff" in vni.columns:
    macd_hist = vni["D_MACDdiff"].values.copy()
else:
    macd_hist = np.full(n, np.nan)

# CMF
if "D_CMF" in vni.columns:
    cmf_raw = vni["D_CMF"].values.copy()
else:
    cmf_raw = np.full(n, np.nan)

# Breadth
breadth_arr = vni["breadth"].values.copy() if "breadth" in vni.columns else np.full(n, np.nan)

# Expanding ranks
print("  Computing expanding ranks ...")
ranks = {
    "P3M":    expanding_rank(p3m),
    "P1M":    expanding_rank(p1m),
    "MA200":  expanding_rank(ma200_dev),
    "RSI":    expanding_rank(rsi),
    "MACD":   expanding_rank(macd_hist),
    "CMF":    expanding_rank(cmf_raw),
    "Breadth":expanding_rank(breadth_arr),
}

# Composite score
score = np.full(n, np.nan)
for i in range(n):
    vals = []
    for k, w in W_BASE.items():
        v = ranks[k][i]
        if not np.isnan(v):
            vals.append((w, v))
    if len(vals) >= MIN_FACTORS:
        tw = sum(x[0] for x in vals)
        sc = sum(x[0]*x[1] for x in vals) / tw
        score[i] = sc

# EMA smoothing
r_score = np.full(n, np.nan)
last_valid = None
for i in range(n):
    if np.isnan(score[i]):
        r_score[i] = last_valid if last_valid is not None else np.nan
    else:
        if last_valid is None:
            r_score[i] = score[i]
        else:
            r_score[i] = EMA_ALPHA * score[i] + (1 - EMA_ALPHA) * last_valid
        last_valid = r_score[i]

# Classify
def classify(rs):
    if   rs < 0.10:   return 1
    elif rs < 0.30:   return 2
    elif rs < 0.55:   return 3
    elif rs < 0.75:   return 3
    elif rs < 0.90:   return 4
    else:             return 5

def classify_v(rs_arr):
    out = np.full(len(rs_arr), 3, dtype=int)
    for i, v in enumerate(rs_arr):
        if not np.isnan(v):
            out[i] = classify(v)
    return out

state_raw = classify_v(r_score)

# PE override
pe_arr = vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n, np.nan)
pe_p90 = np.full(n, np.nan)
for i in range(252, n):
    window = pe_arr[max(0,i-3000):i+1]
    valid  = window[~np.isnan(window)]
    if len(valid) >= 50:
        pe_p90[i] = np.percentile(valid, 90)

state_after_override = state_raw.copy()
dd = np.full(n, 0.0)
peak = close[0]
for i in range(n):
    if close[i] > peak: peak = close[i]
    dd[i] = close[i] / peak - 1

vol20 = np.full(n, np.nan)
rets  = np.diff(np.log(np.where(close > 0, close, np.nan)))
rets  = np.concatenate([[np.nan], rets])
for i in range(20, n):
    vol20[i] = np.nanstd(rets[i-19:i+1]) * np.sqrt(252)
vol20_ma = np.full(n, np.nan)
for i in range(60, n):
    vol20_ma[i] = np.nanmean(vol20[i-59:i+1])

for i in range(n):
    s = state_after_override[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]):
        if pe_arr[i] > pe_p90[i] and s >= 4: state_after_override[i] = min(s, 4)
    if dd[i] < -0.25 and s >= 3:             state_after_override[i] = min(s, 3)
    if (not np.isnan(vol20[i]) and not np.isnan(vol20_ma[i])
        and vol20_ma[i] > 0 and vol20[i] > 1.5 * vol20_ma[i] and s >= 4):
        state_after_override[i] = min(s, 4)

# Mode rolling + min_stay
def rolling_mode(arr, w):
    out = arr.copy()
    for i in range(w-1, len(arr)):
        window = arr[i-w+1:i+1]
        counts = np.bincount(window, minlength=6)
        out[i] = np.argmax(counts)
    return out

def min_stay_filter(arr, ms):
    out = arr.copy()
    i = 0
    while i < len(arr):
        j = i + 1
        while j < len(arr) and arr[j] == arr[i]:
            j += 1
        if j - i < ms:
            prev = out[i-1] if i > 0 else arr[i]
            out[i:j] = prev
        i = j
    return out

state_smooth = rolling_mode(state_after_override, MODE_WIN)
state_smooth = min_stay_filter(state_smooth, MIN_STAY)
vni["state"] = state_smooth

# ══════════════════════════════════════════════════════════════════════
# EXTRACT TRANSITIONS + COMPUTE FORWARD RETURNS
# ══════════════════════════════════════════════════════════════════════
print("\nExtracting transitions ...")

# Build segment list: (state, start_idx, end_idx, duration_sessions)
segments = []
i = 0
while i < n:
    j = i + 1
    while j < n and state_smooth[j] == state_smooth[i]:
        j += 1
    segments.append({
        "state": int(state_smooth[i]),
        "start": i,
        "end":   j - 1,
        "dur_sessions": j - i,
        "start_date": vni["time"].iloc[i],
        "end_date":   vni["time"].iloc[j-1],
        "close_start": close[i],
        "close_end":   close[j-1],
    })
    i = j

print(f"  Total segments: {len(segments)}")

# Forward return helper
def fwd_ret(start_idx, horizon):
    end_idx = start_idx + horizon
    if end_idx >= n:
        return np.nan
    if close[start_idx] <= 0:
        return np.nan
    return close[end_idx] / close[start_idx] - 1

# Find all transitions INTO CRISIS (state==1)
crisis_entries = []
for seg_idx in range(1, len(segments)):
    seg   = segments[seg_idx]
    prior = segments[seg_idx - 1]
    if seg["state"] == 1:  # entering CRISIS
        entry_i = seg["start"]
        # Duration of prior segment in sessions
        prior_dur = prior["dur_sessions"]
        # Forward returns from CRISIS entry
        r1w  = fwd_ret(entry_i, 5)
        r1m  = fwd_ret(entry_i, 20)
        r3m  = fwd_ret(entry_i, 60)
        r_crisis_dur = fwd_ret(entry_i, seg["dur_sessions"])  # return over crisis period
        crisis_entries.append({
            "date":          seg["start_date"],
            "prior_state":   STATE_NAMES[prior["state"]],
            "prior_dur_s":   prior_dur,
            "crisis_dur_s":  seg["dur_sessions"],
            "close":         seg["close_start"],
            "r_score_entry": r_score[entry_i] if not np.isnan(r_score[entry_i]) else None,
            "fwd_1w":        r1w,
            "fwd_1m":        r1m,
            "fwd_3m":        r3m,
            "fwd_crisis":    r_crisis_dur,  # return trong toàn bộ crisis period
            "next_state":    STATE_NAMES[segments[seg_idx + 1]["state"]] if seg_idx + 1 < len(segments) else "END",
        })

df = pd.DataFrame(crisis_entries)
print(f"  CRISIS entries found: {len(df)}")

# ══════════════════════════════════════════════════════════════════════
# DEFINE "TRUE CRISIS" vs "FALSE CRISIS"
# ══════════════════════════════════════════════════════════════════════
# True CRISIS: market drops ≥ 5% within 1 month, OR crisis lasts ≥ 15 sessions
# False CRISIS: market stays flat/rises, OR crisis exits quickly (< 15 sessions)
df["is_true_crisis"] = ((df["fwd_1m"] < -0.05) | (df["crisis_dur_s"] >= 15))
df["is_false_crisis"] = ~df["is_true_crisis"]

# Duration bucket for prior BEAR state
def bear_dur_bucket(row):
    if row["prior_state"] != "BEAR":
        return row["prior_state"]
    if row["prior_dur_s"] > 15:
        return "BEAR_LONG (>15s)"
    else:
        return "BEAR_SHORT (≤15s)"

df["prior_path"] = df.apply(bear_dur_bucket, axis=1)

# ══════════════════════════════════════════════════════════════════════
# ANALYSIS OUTPUT
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PHÂN TÍCH TRANSITION VÀO CRISIS")
print("="*70)

print(f"\nTổng số lần vào CRISIS: {len(df)}")
print(f"  True CRISIS  (fwd_1m < -5% HOẶC kéo dài ≥15 phiên): {df['is_true_crisis'].sum()}")
print(f"  False CRISIS (flat/tăng VÀ kéo dài <15 phiên):       {df['is_false_crisis'].sum()}")

# ── Table 1: Phân bố theo prior state ──────────────────────────────
print("\n── Table 1: Phân bố theo Prior State ──")
print(f"{'Prior Path':<22} {'Count':>6} {'TrueCR%':>9} {'FalseCR%':>10} {'Med_1M':>9} {'Med_3M':>9} {'Med_CrDur':>11}")
print("-"*80)
for path in ["BEAR_LONG (>15s)", "BEAR_SHORT (≤15s)", "NEUTRAL", "BULL", "EX-BULL"]:
    sub = df[df["prior_path"] == path]
    if len(sub) == 0:
        continue
    true_pct  = sub["is_true_crisis"].mean() * 100
    false_pct = sub["is_false_crisis"].mean() * 100
    med_1m    = sub["fwd_1m"].median() * 100 if sub["fwd_1m"].notna().any() else float("nan")
    med_3m    = sub["fwd_3m"].median() * 100 if sub["fwd_3m"].notna().any() else float("nan")
    med_dur   = sub["crisis_dur_s"].median()
    print(f"{path:<22} {len(sub):>6} {true_pct:>8.0f}% {false_pct:>9.0f}% {med_1m:>+8.1f}% {med_3m:>+8.1f}% {med_dur:>9.0f}s")

# ── Table 2: Chi tiết từng lần vào CRISIS ──────────────────────────
print("\n── Table 2: Chi tiết từng lần vào CRISIS ──")
print(f"{'Date':<12} {'Prior':<20} {'PrDur':>6} {'CrDur':>6} {'1W%':>7} {'1M%':>7} {'3M%':>7} {'Next':<10} {'Type':<10}")
print("-"*95)
for _, row in df.iterrows():
    r1w  = f"{row['fwd_1w']*100:+.1f}%" if pd.notna(row['fwd_1w']) else "  N/A"
    r1m  = f"{row['fwd_1m']*100:+.1f}%" if pd.notna(row['fwd_1m']) else "  N/A"
    r3m  = f"{row['fwd_3m']*100:+.1f}%" if pd.notna(row['fwd_3m']) else "  N/A"
    typ  = "TRUE" if row["is_true_crisis"] else "false"
    print(f"{str(row['date'].date()):<12} {row['prior_path']:<20} {row['prior_dur_s']:>6} {row['crisis_dur_s']:>6} {r1w:>7} {r1m:>7} {r3m:>7} {row['next_state']:<10} {typ:<10}")

# ── Table 3: Thống kê forward return theo path ──────────────────────
print("\n── Table 3: Forward Return Distribution theo Path ──")
for path in ["BEAR_LONG (>15s)", "BEAR_SHORT (≤15s)", "NEUTRAL", "BULL", "EX-BULL"]:
    sub = df[df["prior_path"] == path]
    if len(sub) == 0:
        continue
    print(f"\n  {path} (n={len(sub)}):")
    for col, label in [("fwd_1w","1W"), ("fwd_1m","1M"), ("fwd_3m","3M")]:
        vals = sub[col].dropna() * 100
        if len(vals) == 0:
            continue
        pct_neg5 = (vals < -5).mean() * 100
        pct_pos5 = (vals > 5).mean() * 100
        print(f"    {label}: mean={vals.mean():+.1f}%  med={vals.median():+.1f}%  "
              f"min={vals.min():+.1f}%  max={vals.max():+.1f}%  "
              f"[<-5%: {pct_neg5:.0f}%]  [>+5%: {pct_pos5:.0f}%]")

# ── Table 4: r_score tại thời điểm entry ────────────────────────────
print("\n── Table 4: r_score tại CRISIS Entry theo Path ──")
print(f"{'Prior Path':<22} {'Mean_r':>8} {'Med_r':>8} {'Min_r':>8} {'Max_r':>8}")
print("-"*55)
for path in ["BEAR_LONG (>15s)", "BEAR_SHORT (≤15s)", "NEUTRAL", "BULL", "EX-BULL"]:
    sub = df[df["prior_path"] == path]
    if len(sub) == 0:
        continue
    rs = pd.to_numeric(sub["r_score_entry"], errors="coerce").dropna()
    if len(rs) == 0:
        continue
    print(f"{path:<22} {rs.mean():>8.3f} {rs.median():>8.3f} {rs.min():>8.3f} {rs.max():>8.3f}")

# ── Table 5: Allocation recommendation ──────────────────────────────
print("\n" + "="*70)
print("KẾT LUẬN — ALLOCATION KHI VÀO CRISIS")
print("="*70)
print("""
  Path                    | TrueCR% | Recommended | Lý do
  ─────────────────────────────────────────────────────────────────
  BEAR_LONG (>15s)→CRISIS | tính từ data | 0%       | Xác nhận downtrend
  BEAR_SHORT (≤15s)→CRISIS | tính từ data | 20-25%  | Có xác nhận nhưng ngắn
  NEUTRAL → CRISIS        | tính từ data | 35-40%   | Nhảy cóc, dễ false
  BULL/EX-BULL → CRISIS   | tính từ data | 45-50%   | Shock cực đoan, rất ít gặp
""")

print("\nDone.")
