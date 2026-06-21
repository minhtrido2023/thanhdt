# -*- coding: utf-8 -*-
"""
f_system_daily.py
=================
Kiểm tra tín hiệu F-system mỗi ngày.
Chạy: python f_system_daily.py
Sau khi có data cuối ngày (VNINDEX.csv cập nhật).

Output:
  === F-SYSTEM SIGNAL — YYYY-MM-DD ===
  SIG-A: CÓ — Score 2/5 → Leverage 2.4x | P(win)=82%
  SIG-B: KHÔNG CÓ
  Entry: mở cửa ngày mai | Hold: 5 phiên (đến YYYY-MM-DD)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os
import numpy as np
import pandas as pd
from datetime import timedelta

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ─── PARAMETERS (same as vnindex_5state_system.py) ────────────────────────────
W_BASE      = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
               "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
MODE_WIN    = 15
MIN_STAY    = 7
EMA_ALPHA   = 0.40

STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

# F-system thresholds — calibrated on VN30 returns (backtest 2012-2026)
# SIG-A: SUSPEND (chỉ 6 signals VN30, không đủ để hiệu chỉnh)
# SIG-B: ngưỡng ≥4 (score 3 cho net âm trên VN30)
SIGB_LEVERAGE = {4: 0.83, 5: 1.11, 6: 1.20}
SIGB_PWIN     = {4: 0.61, 5: 0.60, 6: 0.70}
SIGB_MIN_SCORE = 4   # score 3 bị loại (net return âm trên VN30)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

cal_days_total  = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = len(vni) / (cal_days_total / 365.25) if cal_days_total > 0 else 243

for col in ["Open", "High", "Low", "Close", "Volume", "VNINDEX_PE",
            "D_RSI", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
            "D_RSI_Min1W", "D_RSI_Min3M", "D_RSI_Max1W_Close", "D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD", "D_RSI_Max1W_MACD", "D_RSI_MinT3",
            "D_MACDdiff", "D_CMF", "C_L1M", "C_L1W", "VN30"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

# Load breadth (optional)
breadth_path = os.path.join(WORKDIR, "breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    breadth["breadth"] = pd.to_numeric(breadth["breadth"], errors="coerce")
else:
    breadth = pd.DataFrame(columns=["time", "breadth"])
vni = vni.merge(breadth, on="time", how="left")

# ─── COMPUTE INDICATORS ───────────────────────────────────────────────────────
close = vni["Close"].values.copy()   # VNINDEX close (for state machine only)
vn30  = vni["VN30"].values.copy()    # VN30 close (for vol/p1m features)
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n     = len(close)

# P3M
p3m = np.full(n, np.nan)
if "Change_3M" in vni.columns:
    p3m_csv = pd.to_numeric(vni["Change_3M"], errors="coerce").values
    for i in range(n):
        if not np.isnan(p3m_csv[i]):
            p3m[i] = p3m_csv[i]
        elif i >= 60 and close[i-60] > 0:
            p3m[i] = close[i] / close[i-60] - 1
else:
    for i in range(60, n):
        if close[i-60] > 0:
            p3m[i] = close[i] / close[i-60] - 1

# P1M
p1m = np.full(n, np.nan)
if "Change_1M" in vni.columns:
    p1m_csv = pd.to_numeric(vni["Change_1M"], errors="coerce").values
    for i in range(n):
        if not np.isnan(p1m_csv[i]):
            p1m[i] = p1m_csv[i]
        elif i >= 20 and close[i-20] > 0:
            p1m[i] = close[i] / close[i-20] - 1
else:
    for i in range(20, n):
        if close[i-20] > 0:
            p1m[i] = close[i] / close[i-20] - 1

# MA200 deviation
ma200     = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

# RSI Wilder 14 → [0,1]
rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan
for i in range(1, n):
    diff = close[i] - close[i-1]
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= 14:
            gains  = [max(close[j]-close[j-1], 0) for j in range(1, 15)]
            losses = [max(close[j-1]-close[j], 0) for j in range(1, 15)]
            avg_u  = np.mean(gains); avg_d = np.mean(losses)
            if (avg_u + avg_d) > 0:
                rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u * 13 + u) / 14
        avg_d = (avg_d * 13 + d) / 14
        if (avg_u + avg_d) > 0:
            rsi[i] = avg_u / (avg_u + avg_d)

# MACD histogram (12, 26, 9)
ema12 = np.full(n, np.nan); ema26 = np.full(n, np.nan)
sig9  = np.full(n, np.nan); macd_hist = np.full(n, np.nan)
k12 = 2/13; k26 = 2/27; k9 = 2/10
for i in range(n):
    c = close[i]
    ema12[i] = c if (i == 0 or np.isnan(ema12[i-1])) else ema12[i-1]*(1-k12) + c*k12
    ema26[i] = c if (i == 0 or np.isnan(ema26[i-1])) else ema26[i-1]*(1-k26) + c*k26
    ml = ema12[i] - ema26[i]
    sig9[i]  = ml if (i == 0 or np.isnan(sig9[i-1])) else sig9[i-1]*(1-k9) + ml*k9
    if i >= 33:
        macd_hist[i] = ml - sig9[i]

# CMF 14
hl  = high - low
mfm = np.where(hl > 0, ((close - low) - (high - close)) / hl, 0.0)
mfv = mfm * vol
cmf = np.full(n, np.nan)
for i in range(14, n):
    vs = np.sum(vol[i-14:i])
    if vs > 0:
        cmf[i] = np.sum(mfv[i-14:i]) / vs

vni["f_P3M"]     = p3m
vni["f_P1M"]     = p1m
vni["f_MA200"]   = ma200_dev
vni["f_RSI"]     = rsi
vni["f_MACD"]    = macd_hist
vni["f_CMF"]     = cmf
vni["f_Breadth"] = vni["breadth"].values

# ─── EXPANDING PERCENTILE RANK ────────────────────────────────────────────────
def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        hist  = arr[:t+1]
        valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb or np.isnan(arr[t]):
            continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

FACTOR_KEYS = ["P3M", "P1M", "MA200", "RSI", "MACD", "CMF", "Breadth"]
ranks = {}
for k in FACTOR_KEYS:
    ranks[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

# ─── COMPOSITE SCORE + R_SCORE ────────────────────────────────────────────────
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FACTOR_KEYS if not np.isnan(ranks[k][t])}
    if len(avail) < MIN_FACTORS:
        continue
    w_sum    = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k] * W_BASE[k] for k in avail) / w_sum

r_score = expanding_pct_rank(score, MIN_LB)

# EMA smooth
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v    = r_score[t]
    prev = r_score_ema[t-1] if t > 0 else np.nan
    if np.isnan(v):
        r_score_ema[t] = prev
    elif np.isnan(prev):
        r_score_ema[t] = v
    else:
        r_score_ema[t] = EMA_ALPHA * v + (1.0 - EMA_ALPHA) * prev

# ─── STATE CLASSIFICATION ─────────────────────────────────────────────────────
def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10:    return 1  # CRISIS
    elif rs < 0.20:  return 2  # BEAR
    elif rs < 0.70:  return 3  # NEUTRAL
    elif rs < 0.90:  return 4  # BULL
    else:            return 5  # EX-BULL

state_raw = np.array([classify_raw(r) for r in r_score_ema])

# ─── RISK OVERRIDES ───────────────────────────────────────────────────────────
pe_arr = vni["VNINDEX_PE"].values.copy()
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist  = pe_arr[:t+1]; v = hist[~np.isnan(hist)]
    if len(v) >= 60:
        pe_p90[t] = np.nanpercentile(v, 90)

running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close / running_max - 1, 0.0)

daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0:
        daily_ret[i] = close[i] / close[i-1] - 1

vol20 = np.full(n, np.nan)
for i in range(20, n):
    w2 = daily_ret[i-20:i]; valid = w2[~np.isnan(w2)]
    if len(valid) >= 15:
        vol20[i] = np.std(valid) * np.sqrt(sessions_per_year)

avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist  = vol20[:t+1]; v = hist[~np.isnan(hist)]
    if len(v) >= 60:
        avg_vol_exp[t] = np.mean(v)

state_ov = state_raw.copy()
for i in range(n):
    s = state_ov[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5):
        s = 4
    if dd[i] < -0.25 and s >= 4:
        s = 3
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5 * avg_vol_exp[i] and s == 5):
        s = 4
    state_ov[i] = s

# ─── BEAR DVG GATE ────────────────────────────────────────────────────────────
def _s(col):
    return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)

_D_RSI       = _s("D_RSI");       _D_RSI_T1W   = _s("D_RSI_T1W")
_D_RSI_Max1W = _s("D_RSI_Max1W"); _D_RSI_Max3M = _s("D_RSI_Max3M")
_D_RSI_Min1W = _s("D_RSI_Min1W"); _D_RSI_Min3M = _s("D_RSI_Min3M")
_D_RSI_Max1W_C = _s("D_RSI_Max1W_Close"); _D_RSI_Max3M_C = _s("D_RSI_Max3M_Close")
_D_RSI_Max3M_M = _s("D_RSI_Max3M_MACD");  _D_RSI_Max1W_M = _s("D_RSI_Max1W_MACD")
_D_RSI_Min1W_C = _s("D_RSI_Min1W_Close"); _D_RSI_MinT3   = _s("D_RSI_MinT3")
_D_MACDdiff  = _s("D_MACDdiff");  _D_CMF = _s("D_CMF")
_C_L1M       = _s("C_L1M");       _C_L1W = _s("C_L1W")
_mask_2011   = vni["time"] >= "2011-01-01"

bear1_sig = ((_D_RSI_Max1W/_D_RSI > 1.044) & (_D_RSI_Max3M > 0.74) &
             (_D_RSI_Max1W < 0.72) & (_D_RSI_Max1W > 0.61) &
             (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.028) &
             (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.11) & (_D_MACDdiff < 0) &
             (vni["Close"]/_D_RSI_Max3M_C > 0.96) &
             (_D_RSI_MinT3 > 0.43) & (_D_CMF < 0.13) & _mask_2011)
bear2_sig = ((_D_RSI_Max1W/_D_RSI > 1.016) & (_D_RSI_Max3M > 0.77) &
             (_D_RSI_Max1W < 0.79) & (_D_RSI_Max1W > 0.60) &
             (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.008) &
             (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.10) & (_D_MACDdiff < 0) &
             (vni["Close"]/_D_RSI_Max3M_C > 0.97) &
             (_D_RSI_MinT3 > 0.50) & (_D_CMF < 0.15) & _mask_2011)
bull1_sig = ((_D_RSI_Min1W/_D_RSI_Min3M > 0.90) & (_D_RSI_Min1W < 0.60) &
             (_D_RSI_Min3M < 0.40) & (_D_RSI_Min1W_C/_D_RSI_Max3M_C < 1.15) &
             (_D_MACDdiff > 0) & (_D_RSI_MinT3 < 0.50) & (_D_RSI_Max1W < 0.48) &
             (_D_RSI/_D_RSI_T1W > 1.12) & (_D_CMF > 0) &
             (_C_L1M < 1.21) & (_C_L1W < 1.05) & _mask_2011)
bull2_sig = ((_D_RSI_Min1W/_D_RSI_Min3M > 0.92) & (_D_RSI_Min1W < 0.52) &
             (_D_RSI_Min3M < 0.38) & (_D_RSI_Min1W_C/_D_RSI_Max3M_C < 1.10) &
             (_D_MACDdiff > 0) & (_D_RSI_MinT3 < 0.56) & (_D_RSI_Max1W < 0.64) &
             (_D_RSI/_D_RSI_T1W > 1.10) & (_D_CMF > 0) &
             (_C_L1M < 1.20) & (_C_L1W < 1.025) & _mask_2011)

bear_mask = (bear1_sig | bear2_sig).values.astype(bool)
bull_mask  = (bull1_sig | bull2_sig).values.astype(bool)

pe_rank_arr = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    v = pe_arr[:t+1]; v = v[~np.isnan(v)]
    if len(v) >= 60:
        pe_rank_arr[t] = np.sum(v <= pe_arr[t]) / len(v)

p3m_rank_arr = ranks["P3M"]
_rscore_streak = np.zeros(n, dtype=bool); _streak = 0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i] > 0.65:
        _streak += 1
    else:
        _streak = 0
    if _streak >= 10:
        _rscore_streak[i] = True

GATE_FLOOR   = 1
GATE_MIN_DUR = 60
gate_active  = False
gate_start   = -1
state_dvg    = state_ov.copy()
gate_flag    = np.zeros(n, dtype=int)

for i in range(n):
    if bear_mask[i]:
        gate_active = True
        gate_start  = i
    if gate_active:
        gate_flag[i] = 1
        if state_dvg[i] > GATE_FLOOR:
            state_dvg[i] = GATE_FLOOR
        sessions_in = i - gate_start
        if sessions_in >= GATE_MIN_DUR:
            _p3m_ok = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
            _pe_ok  = (not np.isnan(pe_rank_arr[i]))  and pe_rank_arr[i]  < 0.80
            _bull   = bool(bull_mask[i])
            _rs     = bool(_rscore_streak[i])
            if _bull or (_p3m_ok and _pe_ok) or _rs:
                gate_active = False

# ─── SMOOTHING ────────────────────────────────────────────────────────────────
def rolling_mode(states, window=15):
    out = states.copy()
    for t in range(window-1, len(states)):
        w2 = states[t-window+1:t+1]
        vals, counts = np.unique(w2, return_counts=True)
        max_c = counts.max()
        cands = vals[counts == max_c]
        for v in reversed(w2):
            if v in cands:
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
            while j < len(out) and out[j] == out[i]:
                j += 1
            if (j - i) < min_days:
                fill = out[i-1] if i > 0 else (out[j] if j < len(out) else out[i])
                out[i:j] = fill
                changed = True
            i = j
    return out

state_smooth = rolling_mode(state_dvg, MODE_WIN)
state_smooth = min_stay_filter(state_smooth, MIN_STAY)

vni["r_score"]     = r_score
vni["r_score_ema"] = r_score_ema
vni["state"]       = state_smooth

# ─── VN30-BASED VOL & P1M (for SIG-B scoring) ────────────────────────────────
# vol20 và p1m dùng VN30 (không phải VNINDEX) vì trade VN30F futures
log_r_vn30 = np.full(n, np.nan)
for i in range(1, n):
    if not np.isnan(vn30[i]) and not np.isnan(vn30[i-1]) and vn30[i-1] > 0:
        log_r_vn30[i] = np.log(vn30[i] / vn30[i-1])

vol20_vn30 = np.full(n, np.nan)
for i in range(20, n):
    w2 = log_r_vn30[i-19:i+1]; valid = w2[~np.isnan(w2)]
    if len(valid) >= 15:
        vol20_vn30[i] = np.std(valid) * np.sqrt(sessions_per_year)

p1m_vn30 = np.full(n, np.nan)
for i in range(21, n):
    if not np.isnan(vn30[i]) and not np.isnan(vn30[i-21]) and vn30[i-21] > 0:
        p1m_vn30[i] = vn30[i] / vn30[i-21] - 1

# Median vol (VN30, historical)
valid_vol_vn30 = vol20_vn30[~np.isnan(vol20_vn30)]
MEDIAN_VOL = float(np.median(valid_vol_vn30)) if len(valid_vol_vn30) > 0 else 0.145

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_bear_dur(idx):
    """Số phiên state=BEAR liên tiếp kết thúc tại idx-1 (ngày hôm qua)."""
    dur = 0
    for i in range(idx-1, -1, -1):
        if state_smooth[i] == 2:
            dur += 1
        else:
            break
    return dur

def get_bear_ret(idx):
    """Return kể từ đỉnh trước giai đoạn BEAR (đến idx-1)."""
    # tìm đầu đoạn BEAR
    start = idx - 1
    while start > 0 and state_smooth[start-1] == 2:
        start -= 1
    # tìm giá cao nhất trước khi BEAR bắt đầu (lookback 60 phiên)
    pre_start = max(0, start - 60)
    peak = np.nanmax(close[pre_start:start+1]) if start > 0 else close[0]
    current = close[idx-1]
    if peak > 0:
        return current / peak - 1
    return 0.0

def get_valley_depth(idx):
    """Depth từ đỉnh r_score trong 60 phiên trước valley (idx-1)."""
    valley_rs = r_score[idx-1]
    if np.isnan(valley_rs):
        return 0.0
    lookback = r_score[max(0, idx-61):idx-1]
    valid = lookback[~np.isnan(lookback)]
    if len(valid) == 0:
        return 0.0
    peak_rs = np.max(valid)
    return float(peak_rs - valley_rs)

# ─── SIGNAL CHECK ─────────────────────────────────────────────────────────────
today_idx = n - 1       # index of today (last row)
today_dt  = vni["time"].iloc[today_idx]

# Safety: need at least 3 days of data
if today_idx < 2:
    print("Không đủ dữ liệu.")
    sys.exit(0)

# Current values
state_today     = int(state_smooth[today_idx])
state_yesterday = int(state_smooth[today_idx - 1])
rs_today        = r_score[today_idx]
rs_yesterday    = r_score[today_idx - 1]
rs_daybefore    = r_score[today_idx - 2]
# Features dùng VN30 (không phải VNINDEX) — vì trade VN30F
vol_today       = vol20_vn30[today_idx]
p1m_today       = p1m_vn30[today_idx]

# ── SIG-A: BEAR → NEUTRAL ─────────────────────────────────────────────────────
siga_active = (state_yesterday == 2 and state_today == 3)

siga_score = 0
siga_details = []
if siga_active:
    bear_dur  = get_bear_dur(today_idx)
    bear_ret  = get_bear_ret(today_idx)
    rs_entry  = r_score[today_idx]   # r_score tại điểm chuyển trạng thái

    if bear_dur > 15:
        siga_score += 1
        siga_details.append(f"bear_dur={bear_dur}>15 (+1)")
    else:
        siga_details.append(f"bear_dur={bear_dur}<=15 (0)")

    if bear_ret < -0.08:
        siga_score += 1
        siga_details.append(f"bear_ret={bear_ret:.1%}<-8% (+1)")
    else:
        siga_details.append(f"bear_ret={bear_ret:.1%}>=-8% (0)")

    if (not np.isnan(rs_entry)) and rs_entry < 0.32:
        siga_score += 1
        siga_details.append(f"r_score={rs_entry:.3f}<0.32 (+1)")
    else:
        rs_str = f"{rs_entry:.3f}" if not np.isnan(rs_entry) else "N/A"
        siga_details.append(f"r_score={rs_str}>=0.32 (0)")

    if (not np.isnan(vol_today)) and vol_today < MEDIAN_VOL:
        siga_score += 1
        siga_details.append(f"vol20={vol_today:.1%}<median({MEDIAN_VOL:.1%}) (+1)")
    else:
        v_str = f"{vol_today:.1%}" if not np.isnan(vol_today) else "N/A"
        siga_details.append(f"vol20={v_str}>=median (0)")

    if (not np.isnan(p1m_today)) and p1m_today < -0.05:
        siga_score += 1
        siga_details.append(f"p1m={p1m_today:.1%}<-5% (+1)")
    else:
        p1m_str = f"{p1m_today:.1%}" if not np.isnan(p1m_today) else "N/A"
        siga_details.append(f"p1m={p1m_str}>=-5% (0)")

# ── SIG-B: r_score valley xác nhận ────────────────────────────────────────────
# Điều kiện: r_score[hôm qua] < r_score[hôm kia] (đang giảm)
#            r_score[hôm qua] < r_score[hôm nay] (bắt đầu tăng)
#            delta_up = r_score[hôm nay] - r_score[hôm qua] >= 0.010
sigb_active = False
delta_up    = np.nan
if (not any(np.isnan([rs_today, rs_yesterday, rs_daybefore]))):
    delta_up    = rs_today - rs_yesterday
    sigb_active = (rs_yesterday < rs_daybefore and
                   rs_yesterday < rs_today and
                   delta_up >= 0.010)

sigb_score   = 0
sigb_details = []
if sigb_active:
    rs_valley = rs_yesterday
    vd        = get_valley_depth(today_idx)   # depth từ đỉnh đến valley (hôm qua)
    vol_entry = vol_today
    p1m_entry = p1m_today

    if rs_valley < 0.40:
        sigb_score += 1
        sigb_details.append(f"r_score_valley={rs_valley:.3f}<0.40 (+1)")
    else:
        sigb_details.append(f"r_score_valley={rs_valley:.3f}>=0.40 (0)")

    if delta_up > 0.015:
        sigb_score += 1
        sigb_details.append(f"delta_up={delta_up:.3f}>0.015 (+1)")
    else:
        sigb_details.append(f"delta_up={delta_up:.3f}<=0.015 (0)")

    if vd > 0.05:
        sigb_score += 1
        sigb_details.append(f"valley_depth={vd:.3f}>0.05 (+1)")
    else:
        sigb_details.append(f"valley_depth={vd:.3f}<=0.05 (0)")

    if state_today in [3, 4, 5]:
        sigb_score += 1
        sigb_details.append(f"state={STATE_NAMES[state_today]} (+1)")
    else:
        sigb_details.append(f"state={STATE_NAMES[state_today]} (0)")

    if (not np.isnan(p1m_entry)) and p1m_entry < -0.03:
        sigb_score += 1
        sigb_details.append(f"p1m={p1m_entry:.1%}<-3% (+1)")
    else:
        p1m_str = f"{p1m_entry:.1%}" if not np.isnan(p1m_entry) else "N/A"
        sigb_details.append(f"p1m={p1m_str}>=-3% (0)")

    if (not np.isnan(vol_entry)) and vol_entry < MEDIAN_VOL:
        sigb_score += 1
        sigb_details.append(f"vol20={vol_entry:.1%}<median({MEDIAN_VOL:.1%}) (+1)")
    else:
        v_str = f"{vol_entry:.1%}" if not np.isnan(vol_entry) else "N/A"
        sigb_details.append(f"vol20={v_str}>=median (0)")

# ─── OUTPUT ───────────────────────────────────────────────────────────────────
today_str = today_dt.strftime("%Y-%m-%d")
print(f"\n{'='*52}")
print(f"  F-SYSTEM SIGNAL — {today_str}")
print(f"{'='*52}")

# Context
rs_str  = f"{r_score_ema[today_idx]:.3f}" if not np.isnan(r_score_ema[today_idx]) else "N/A"
vol_str = f"{vol_today:.1%}" if not np.isnan(vol_today) else "N/A"
p1m_str = f"{p1m_today:.1%}" if not np.isnan(p1m_today) else "N/A"
print(f"  Market state : {STATE_NAMES[state_today]} (hôm nay) ← {STATE_NAMES[state_yesterday]} (hôm qua)")
print(f"  r_score_ema  : {rs_str}")
print(f"  VN30 vol_20d : {vol_str}  (median: {MEDIAN_VOL:.1%})")
print(f"  VN30 p1m     : {p1m_str}")
print()

# SIG-A — SUSPEND (chỉ 6 signals VN30 từ 2012, không đủ sample)
if siga_active:
    print(f"  SIG-A : SUSPEND — BEAR→NEUTRAL detected nhưng VN30 chỉ có 6 signals (2012+),")
    print(f"           không đủ sample để calibrate scoring trên VN30. Bỏ qua.")
else:
    print(f"  SIG-A : Không có (state hôm qua={STATE_NAMES[state_yesterday]}, hôm nay={STATE_NAMES[state_today]})")

print()

# SIG-B
if sigb_active and sigb_score >= SIGB_MIN_SCORE:
    lev  = SIGB_LEVERAGE.get(sigb_score, 1.20)
    pwin = SIGB_PWIN.get(sigb_score, 0.61)
    entry_dt = today_dt + timedelta(days=1)
    hold_end = today_dt + timedelta(days=8)
    print(f"  SIG-B : *** CO TIN HIEU *** Score {sigb_score}/6 → Leverage {lev:.2f}x | P(win)={pwin:.0%}")
    for d in sigb_details:
        print(f"           {d}")
    du_str = f"{delta_up:.3f}" if not np.isnan(delta_up) else "N/A"
    print(f"           r_score valley hôm qua: {rs_yesterday:.3f} | delta_up={du_str}")
    print(f"           Entry: mở cửa ngày mai ({entry_dt.strftime('%Y-%m-%d')})")
    print(f"           Hold:  5 phiên giao dịch (khoảng {hold_end.strftime('%Y-%m-%d')})")
    print(f"           Lưu ý: 1-day lag — valley xác nhận hôm nay, entry ngày mai")
elif sigb_active and sigb_score < SIGB_MIN_SCORE:
    du_str = f"{delta_up:.3f}" if not np.isnan(delta_up) else "N/A"
    print(f"  SIG-B : Có valley nhưng Score={sigb_score}/6 < {SIGB_MIN_SCORE} → BỎ QUA")
    print(f"           (Score 3 cho net return âm trên VN30; cần ≥4)")
    for d in sigb_details:
        print(f"           {d}")
else:
    if not any(np.isnan([rs_today, rs_yesterday, rs_daybefore])):
        du_str = f"{delta_up:.3f}" if not np.isnan(delta_up) else "N/A"
        print(f"  SIG-B : Không có valley "
              f"(rs[-2]={rs_daybefore:.3f}, rs[-1]={rs_yesterday:.3f}, rs[0]={rs_today:.3f}, Δ={du_str})")
    else:
        print(f"  SIG-B : Không có (thiếu dữ liệu r_score)")

print()

# Summary
any_signal = (sigb_active and sigb_score >= SIGB_MIN_SCORE)
if any_signal:
    lev = SIGB_LEVERAGE.get(sigb_score, 1.20)
    print(f"  => KET LUAN: CO TIN HIEU — SIG-B Score {sigb_score}/6 → Leverage {lev:.2f}x")
    print(f"     LONG VN30F mở cửa ngày mai.")
    print(f"     Không overlap: nếu đang có lệnh chưa thoát → bỏ qua.")
else:
    print(f"  => KET LUAN: KHONG CO TIN HIEU — không giao dịch hôm nay.")
print(f"{'='*52}\n")
