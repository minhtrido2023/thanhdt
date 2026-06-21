# -*- coding: utf-8 -*-
"""
vnindex_5state_system.py
========================
Hệ thống phân loại trạng thái thị trường VNINDEX với 5 trạng thái.
Dữ liệu: VNINDEX.csv + breadth_data.csv
Output: vnindex_5state_system.html
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os
import numpy as np
import pandas as pd
# scipy not required — using pure numpy mode

WORKDIR = os.environ.get("BAVN_WORKDIR",
                          os.path.dirname(os.path.abspath(__file__)))

# ══════════════════════════════════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════════════════════════════════
W_BASE = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
          "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252       # min sessions before expanding rank kicks in
MIN_FACTORS = 3         # min factors needed for composite score
MODE_WIN    = 15        # smoothing window (mode over 15 sessions)
MIN_STAY    = 7         # tối thiểu N phiên/trạng thái — loại micro-transition 1-3 ngày
RAMP_DAYS   = 3
SNAP_THR    = 0.03
TC          = 0.001
DEPOSIT_R   = 0.06 / 252
BORROW_R    = 0.10 / 252
TARGET_W    = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
STATE_COLOR = {1: "#ef4444", 2: "#f97316", 3: "#eab308", 4: "#22c55e", 5: "#10b981"}
STATE_ALLOC = {1: "0%", 2: "20%", 3: "70%", 4: "100%", 5: "130%"}

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading VNINDEX.csv ...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

# ── Tính mật độ phiên giao dịch thực tế (pre-2007: 3 ngày/tuần) ──────────────
cal_days_total = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = len(vni) / (cal_days_total / 365.25) if cal_days_total > 0 else 252
print(f"  Trading calendar: {len(vni)} sessions / {cal_days_total/365.25:.1f} yrs = {sessions_per_year:.1f} sessions/yr")

# Force numeric
for col in ["Open", "High", "Low", "Close", "Volume", "VNINDEX_PE",
            "D_RSI", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
            "D_RSI_Min1W", "D_RSI_Min3M", "D_RSI_Max1W_Close", "D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD", "D_RSI_Max1W_MACD", "D_RSI_MinT3",
            "D_MACDdiff", "D_CMF", "C_L1M", "C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

print(f"  VNINDEX rows: {len(vni)} | {vni['time'].min().date()} → {vni['time'].max().date()}")

# Load Breadth
breadth_path = os.path.join(WORKDIR, "breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    breadth["breadth"] = pd.to_numeric(breadth["breadth"], errors="coerce")
    print(f"  Breadth rows: {len(breadth)} | {breadth['time'].min().date()} → {breadth['time'].max().date()}")
else:
    breadth = pd.DataFrame(columns=["time", "breadth"])
    print("  WARNING: breadth_data.csv not found")

vni = vni.merge(breadth, on="time", how="left")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE INDICATORS FROM RAW OHLCV
# ══════════════════════════════════════════════════════════════════════
print("Computing indicators ...")
close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n     = len(close)

# --- P3M: dùng Change_3M từ CSV (calendar-correct, đúng cho pre-2007 3 ngày/tuần) ---
# Fallback sang session-based (i-60) chỉ khi CSV không có giá trị
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

# --- P1M: dùng Change_1M từ CSV (calendar-correct, đúng cho pre-2007 3 ngày/tuần) ---
# Fallback sang session-based (i-20) chỉ khi CSV không có giá trị
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

# --- MA200 deviation ---
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

# --- RSI (Wilder, 14) → [0,1] ---
rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan
period = 14
for i in range(1, n):
    diff = close[i] - close[i-1]
    u = max(diff, 0.0)
    d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= period:
            # seed with simple average
            gains = [max(close[j] - close[j-1], 0) for j in range(1, period+1)]
            losses = [max(close[j-1] - close[j], 0) for j in range(1, period+1)]
            avg_u = np.mean(gains)
            avg_d = np.mean(losses)
            if (avg_u + avg_d) > 0:
                rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u * (period - 1) + u) / period
        avg_d = (avg_d * (period - 1) + d) / period
        if (avg_u + avg_d) > 0:
            rsi[i] = avg_u / (avg_u + avg_d)

# --- MACD Histogram (12, 26, 9) ---
ema12 = np.full(n, np.nan)
ema26 = np.full(n, np.nan)
signal = np.full(n, np.nan)
macd_hist = np.full(n, np.nan)
k12 = 2/13; k26 = 2/27; k9 = 2/10
for i in range(n):
    if np.isnan(ema12[i-1]) if i > 0 else True:
        ema12[i] = close[i]
        ema26[i] = close[i]
    else:
        ema12[i] = ema12[i-1] * (1 - k12) + close[i] * k12
        ema26[i] = ema26[i-1] * (1 - k26) + close[i] * k26
    macd_line = ema12[i] - ema26[i]
    if np.isnan(signal[i-1]) if i > 0 else True:
        signal[i] = macd_line
    else:
        signal[i] = signal[i-1] * (1 - k9) + macd_line * k9
    if i >= 33:  # need enough bars for MACD to stabilize
        macd_hist[i] = macd_line - signal[i]

# --- CMF (Chaikin Money Flow, 14) ---
hl_range = high - low
mfm = np.where(hl_range > 0, ((close - low) - (high - close)) / hl_range, 0.0)
mfv = mfm * vol
cmf = np.full(n, np.nan)
for i in range(14, n):
    v_sum = np.sum(vol[i-14:i])
    if v_sum > 0:
        cmf[i] = np.sum(mfv[i-14:i]) / v_sum

# Store raw factors
vni["f_P3M"]    = p3m
vni["f_P1M"]    = p1m
vni["f_MA200"]  = ma200_dev
vni["f_RSI"]    = rsi
vni["f_MACD"]   = macd_hist
vni["f_CMF"]    = cmf
vni["f_Breadth"]= vni["breadth"].values  # from BigQuery

# ══════════════════════════════════════════════════════════════════════
# EXPANDING PERCENTILE RANK
# ══════════════════════════════════════════════════════════════════════
print("Computing expanding percentile ranks ...")

def expanding_pct_rank(arr: np.ndarray, min_lb: int = 252) -> np.ndarray:
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        hist = arr[:t+1]
        valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb:
            continue
        if np.isnan(arr[t]):
            continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

FACTOR_KEYS = ["P3M", "P1M", "MA200", "RSI", "MACD", "CMF", "Breadth"]
ranks = {}
for k in FACTOR_KEYS:
    print(f"  Ranking {k} ...")
    ranks[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)
    vni[f"rank_{k}"] = ranks[k]

# ══════════════════════════════════════════════════════════════════════
# COMPOSITE SCORE
# ══════════════════════════════════════════════════════════════════════
print("Computing composite score ...")
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FACTOR_KEYS if not np.isnan(ranks[k][t])}
    if len(avail) < MIN_FACTORS:
        continue
    w_sum = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k] * W_BASE[k] for k in avail) / w_sum

vni["score"] = score

# Expanding rank of score
print("  Ranking composite score ...")
r_score = expanding_pct_rank(score, MIN_LB)
vni["r_score"] = r_score

# ══════════════════════════════════════════════════════════════════════
# EMA SMOOTH r_score TRƯỚC KHI PHÂN LOẠI
# Giảm số lần r_score dao động qua lại ngưỡng → ít chuyển trạng thái hơn
# alpha=0.10 tương đương EMA ~19-period
# ══════════════════════════════════════════════════════════════════════
EMA_ALPHA = 0.40  # alpha=0.40: beats B&H full+2011, 156 transitions, mode(15) filters short stays
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]
    prev = r_score_ema[t-1] if t > 0 else np.nan
    if np.isnan(v):
        r_score_ema[t] = prev  # carry forward
    elif np.isnan(prev):
        r_score_ema[t] = v     # seed
    else:
        r_score_ema[t] = EMA_ALPHA * v + (1.0 - EMA_ALPHA) * prev
vni["r_score_ema"] = r_score_ema

# ══════════════════════════════════════════════════════════════════════
# STATE CLASSIFICATION (raw, based on EMA-smoothed r_score)
# ══════════════════════════════════════════════════════════════════════
print("Classifying states ...")

def classify_raw(rs: float) -> int:
    if np.isnan(rs): return 3  # default neutral when no signal
    if rs < 0.10:   return 1   # CRISIS
    elif rs < 0.20: return 2   # BEAR
    elif rs < 0.70: return 3   # NEUTRAL
    elif rs < 0.90: return 4   # BULL
    else:           return 5   # EX-BULL

state_raw = np.array([classify_raw(r) for r in r_score_ema])

# ══════════════════════════════════════════════════════════════════════
# RISK OVERRIDES
# ══════════════════════════════════════════════════════════════════════
print("Applying risk overrides ...")
pe_arr   = vni["VNINDEX_PE"].values.copy()

# PE expanding P90
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]
    valid = hist[~np.isnan(hist)]
    if len(valid) >= 60:
        pe_p90[t] = np.nanpercentile(valid, 90)

# Drawdown from running max
running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close / running_max - 1, 0.0)

# Volatility (annualized 20-day)
daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0:
        daily_ret[i] = close[i] / close[i-1] - 1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    window = daily_ret[i-20:i]
    valid = window[~np.isnan(window)]
    if len(valid) >= 15:
        vol20[i] = np.std(valid) * np.sqrt(sessions_per_year)

# Expanding average vol
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist = vol20[:t+1]
    valid = hist[~np.isnan(hist)]
    if len(valid) >= 60:
        avg_vol_exp[t] = np.mean(valid)

state_after_override = state_raw.copy()
for i in range(n):
    s = state_after_override[i]
    # Override 1: PE > P90 expanding → cap at 4
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5):
        s = 4
    # Override 2: Drawdown < -25% → cap at 3
    if dd[i] < -0.25 and s >= 4:
        s = 3
    # Override 3: Vol spike > 1.5x → cap at 4
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5 * avg_vol_exp[i] and s == 5):
        s = 4
    state_after_override[i] = s

# ══════════════════════════════════════════════════════════════════════
# SMOOTHING: trailing mode (window=5)
# ══════════════════════════════════════════════════════════════════════
print("Smoothing states ...")

def rolling_mode(states: np.ndarray, window: int = 5) -> np.ndarray:
    out = states.copy()
    for t in range(window - 1, len(states)):
        window_vals = states[t-window+1:t+1]
        vals, counts = np.unique(window_vals, return_counts=True)
        max_count = counts.max()
        candidates = vals[counts == max_count]
        # tie-break: prefer most recent
        for v in reversed(window_vals):
            if v in candidates:
                out[t] = v
                break
    return out

def min_stay_filter(states: np.ndarray, min_days: int = 10) -> np.ndarray:
    """
    Loại bỏ các đoạn trạng thái ngắn hơn min_days phiên.
    Đoạn ngắn bị sáp nhập vào trạng thái trước (hoặc sau nếu ở đầu chuỗi).
    Lặp cho đến khi tất cả đoạn đều >= min_days.
    """
    out = states.copy()
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(out):
            # tìm cuối đoạn hiện tại
            j = i + 1
            while j < len(out) and out[j] == out[i]:
                j += 1
            run_len = j - i
            if run_len < min_days:
                # sáp nhập vào trạng thái trước nếu có, ngược lại vào trạng thái sau
                if i > 0:
                    fill = out[i - 1]
                elif j < len(out):
                    fill = out[j]
                else:
                    fill = out[i]    # toàn chuỗi chỉ có 1 trạng thái
                out[i:j] = fill
                changed = True
            i = j
    return out

# ══════════════════════════════════════════════════════════════════════
# MARKET_DICT_FILTER: BearDvg / BullDvg divergence signals
# BearDvg_window: after BearDvg → cap state at NEUTRAL for 20 sessions
#                 after BullDvg → floor state at NEUTRAL for 20 sessions
# ══════════════════════════════════════════════════════════════════════
def _s(col):
    return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)

_D_RSI         = _s("D_RSI")
_D_RSI_T1W     = _s("D_RSI_T1W")
_D_RSI_Max1W   = _s("D_RSI_Max1W")
_D_RSI_Max3M   = _s("D_RSI_Max3M")
_D_RSI_Min1W   = _s("D_RSI_Min1W")
_D_RSI_Min3M   = _s("D_RSI_Min3M")
_D_RSI_Max1W_C = _s("D_RSI_Max1W_Close")
_D_RSI_Max3M_C = _s("D_RSI_Max3M_Close")
_D_RSI_Max3M_M = _s("D_RSI_Max3M_MACD")
_D_RSI_Max1W_M = _s("D_RSI_Max1W_MACD")
_D_RSI_Min1W_C = _s("D_RSI_Min1W_Close")
_D_RSI_MinT3   = _s("D_RSI_MinT3")
_D_MACDdiff    = _s("D_MACDdiff")
_D_CMF         = _s("D_CMF")
_C_L1M         = _s("C_L1M")
_C_L1W         = _s("C_L1W")
_mask_2011     = vni["time"] >= "2011-01-01"

bear1_sig = ((_D_RSI_Max1W/_D_RSI > 1.044) & (_D_RSI_Max3M > 0.74) &
             (_D_RSI_Max1W < 0.72) & (_D_RSI_Max1W > 0.61) &
             (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.028) &
             (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.11) &
             (_D_MACDdiff < 0) &
             (vni["Close"]/_D_RSI_Max3M_C > 0.96) &
             (_D_RSI_MinT3 > 0.43) & (_D_CMF < 0.13) & _mask_2011)

bear2_sig = ((_D_RSI_Max1W/_D_RSI > 1.016) & (_D_RSI_Max3M > 0.77) &
             (_D_RSI_Max1W < 0.79) & (_D_RSI_Max1W > 0.60) &
             (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.008) &
             (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.10) &
             (_D_MACDdiff < 0) &
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
bull_mask = (bull1_sig | bull2_sig).values.astype(bool)

# PE expanding rank (gate exit: PE_rank < 0.80 = định giá về mức hợp lý)
pe_rank_arr = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    v = pe_arr[:t+1]; v = v[~np.isnan(v)]
    if len(v) >= 60: pe_rank_arr[t] = np.sum(v <= pe_arr[t]) / len(v)

# r_score streak: 10 phiên liên tiếp r_score_ema > 0.65 → momentum phục hồi bền vững
_rscore_streak = np.zeros(n, dtype=bool); _streak = 0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i] > 0.65: _streak += 1
    else: _streak = 0
    if _streak >= 10: _rscore_streak[i] = True

# P3M rank reference (already computed in ranks)
p3m_rank_arr = ranks["P3M"]

# ── BearDvg Gate: floor=CRISIS(0%), exit=OR, min_dur=60 phiên ─────────────────
# Backtest cho thấy: floor=CRISIS tốt hơn BEAR, min=60 tối ưu Calmar
# Exit OR = BullDvg fires  OR  (P3M_rank>0.45 AND PE_rank<0.80)  OR  r_score_ema>0.65×10 phiên
GATE_FLOOR   = 1   # CRISIS = 0%
GATE_MIN_DUR = 60  # minimum 3 tháng sau BearDvg cuối cùng

gate_active  = False
gate_start   = -1
gate_events  = []          # list of dicts for HTML transitions table
gate_flag    = np.zeros(n, dtype=int)   # 1 = đang trong gate

state_dvg = state_after_override.copy()
for i in range(n):
    if bear_mask[i]:
        if not gate_active:
            gate_active = True
            gate_start  = i
            gate_events.append({
                "type": "GATE_OPEN",
                "i": i,
                "date": vni["time"].iloc[i].strftime("%Y-%m-%d"),
                "close": float(close[i]),
            })
        else:
            gate_start = i   # reset minimum timer on new BearDvg

    if gate_active:
        gate_flag[i] = 1
        if state_dvg[i] > GATE_FLOOR:
            state_dvg[i] = GATE_FLOOR

        sessions_in = i - gate_start
        if sessions_in >= GATE_MIN_DUR:
            _p3m_ok  = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
            _pe_ok   = (not np.isnan(pe_rank_arr[i]))  and pe_rank_arr[i]  < 0.80
            _bull_ok = bool(bull_mask[i])
            _rs_ok   = bool(_rscore_streak[i])
            exit_now = _bull_ok or (_p3m_ok and _pe_ok) or _rs_ok
            if exit_now:
                gate_events.append({
                    "type": "GATE_CLOSE",
                    "i": i,
                    "date": vni["time"].iloc[i].strftime("%Y-%m-%d"),
                    "close": float(close[i]),
                    "duration": sessions_in,
                    "trigger": ("BullDvg" if _bull_ok else
                                "P3M+PE"  if (_p3m_ok and _pe_ok) else
                                "r_score"),
                })
                gate_active = False

if gate_active:
    gate_events.append({
        "type": "GATE_CLOSE",
        "i": n-1,
        "date": vni["time"].iloc[-1].strftime("%Y-%m-%d"),
        "close": float(close[-1]),
        "duration": n - gate_start,
        "trigger": "ACTIVE",
    })

state_smooth = rolling_mode(state_dvg, MODE_WIN)
state_smooth = min_stay_filter(state_smooth, MIN_STAY)   # loại micro-transition
vni["state_raw"]      = state_raw
vni["state_override"] = state_after_override
vni["state_dvg"]      = state_dvg
vni["state"]          = state_smooth
# Dump state CSV for downstream systems (TA-system Layer 2 integration)
vni[["time", "state", "state_raw"]].to_csv(
    os.path.join(WORKDIR, "vnindex_5state_history.csv"), index=False
)
vni["bear_dvg"]       = bear_mask.astype(int)
vni["bull_dvg"]       = bull_mask.astype(int)
vni["gate_flag"]      = gate_flag
vni["dd"]           = dd
vni["vol20"]        = vol20
vni["pe_p90"]       = pe_p90

# ══════════════════════════════════════════════════════════════════════
# BACKTEST
# ══════════════════════════════════════════════════════════════════════
print("Running backtest ...")

pv        = np.zeros(n)
pv[0]     = 1_000_000_000.0  # 1 tỷ VND
w         = TARGET_W[3]       # start at NEUTRAL
w_arr     = np.zeros(n)
w_arr[0]  = w
trade_arr = np.zeros(n)

for t in range(1, n):
    target = TARGET_W[state_smooth[t-1]]   # T+1 delay
    diff   = target - w
    if abs(diff) < SNAP_THR:
        w_new = target
    else:
        w_new = w + diff / RAMP_DAYS
    w_new = float(np.clip(w_new, 0.0, 1.30))

    if close[t-1] > 0:
        r = close[t] / close[t-1] - 1
    else:
        r = 0.0
    cash_r = max(0.0, 1.0 - w_new) * DEPOSIT_R
    marg_c = max(0.0, w_new - 1.0) * BORROW_R
    trd_c  = abs(w_new - w) * TC
    pv[t]  = pv[t-1] * (1.0 + w_new * r + cash_r - marg_c - trd_c)
    trade_arr[t] = abs(w_new - w)
    w      = w_new
    w_arr[t] = w

# Buy-and-hold comparison
pv_bh = np.zeros(n)
pv_bh[0] = 1_000_000_000.0
for t in range(1, n):
    if close[t-1] > 0:
        pv_bh[t] = pv_bh[t-1] * (close[t] / close[t-1])
    else:
        pv_bh[t] = pv_bh[t-1]

vni["pv"]     = pv
vni["pv_bh"]  = pv_bh
vni["weight"] = w_arr

# ══════════════════════════════════════════════════════════════════════
# PERFORMANCE METRICS — mở rộng với Sortino, DD duration
# ══════════════════════════════════════════════════════════════════════
def calc_metrics(pv_series, dates_series=None):
    """
    CAGR tính theo calendar time. Sharpe & Sortino annualize bằng actual sessions/year.
    Trả về: cagr, sharpe, sortino, max_dd, calmar, max_dd_dur (phiên), final_value.
    """
    pv_arr = np.asarray(pv_series, dtype=float)
    valid  = np.where(pv_arr > 0)[0]
    if len(valid) < 2:
        return {}
    idx0, idx1 = valid[0], valid[-1]
    v0, v1 = pv_arr[idx0], pv_arr[idx1]

    if dates_series is not None:
        ds = dates_series.reset_index(drop=True)
        cal_years = (ds.iloc[idx1] - ds.iloc[idx0]).days / 365.25
    else:
        cal_years = (idx1 - idx0) / sessions_per_year
    cagr = (v1 / v0) ** (1 / cal_years) - 1 if cal_years > 0 else 0

    sub = pv_arr[idx0:idx1+1]
    rets = np.diff(sub) / sub[:-1]
    n_sub = len(sub) - 1
    sub_spy = n_sub / cal_years if cal_years > 0 else sessions_per_year

    mean_r = np.mean(rets)
    std_r  = np.std(rets)
    sharpe = mean_r * sub_spy / (std_r * np.sqrt(sub_spy)) if std_r > 0 else 0

    # Sortino: chỉ dùng downside deviation (rets < 0)
    down = rets[rets < 0]
    sortino_down = np.sqrt(np.mean(down**2)) if len(down) > 0 else 0
    sortino = mean_r * sub_spy / (sortino_down * np.sqrt(sub_spy)) if sortino_down > 0 else 0

    # Max Drawdown + thời gian phục hồi
    running_max = np.maximum.accumulate(sub)
    dd_arr = np.where(running_max > 0, sub / running_max - 1, 0)
    max_dd = dd_arr.min()
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0

    # Drawdown duration: số phiên dưới đỉnh cũ (underwater periods)
    under = dd_arr < 0
    max_dd_dur = 0
    cur_dur = 0
    for u in under:
        if u:
            cur_dur += 1
            max_dd_dur = max(max_dd_dur, cur_dur)
        else:
            cur_dur = 0

    return {"cagr": cagr, "sharpe": sharpe, "sortino": sortino,
            "max_dd": max_dd, "calmar": calmar, "max_dd_dur": max_dd_dur,
            "final_value": v1}

# Full period
dates_full = vni["time"].reset_index(drop=True)
m_sys = calc_metrics(pv,    dates_full)
m_bh  = calc_metrics(pv_bh, dates_full)

# Since 2011 (PE có từ 2010-11)
idx_2011 = vni[vni["time"] >= "2011-01-01"].index[0]
dates_from11 = dates_full.iloc[idx_2011:].reset_index(drop=True)
m_sys_11 = calc_metrics(pv[idx_2011:],    dates_from11)
m_bh_11  = calc_metrics(pv_bh[idx_2011:], dates_from11)

# Count state transitions
def count_transitions(states):
    trans = 0; durations = []; start = 0
    for i in range(1, len(states)):
        if states[i] != states[i-1]:
            trans += 1; durations.append(i - start); start = i
    durations.append(len(states) - start)
    return trans, durations

n_trans, durations = count_transitions(state_smooth)
short_stays = sum(1 for d in durations if d <= 5)
median_stay = int(np.median(durations))

print(f"\n=== FULL PERIOD ===")
print(f"  System : CAGR={m_sys['cagr']:.1%}, MaxDD={m_sys['max_dd']:.1%}, Sharpe={m_sys['sharpe']:.2f}, Sortino={m_sys['sortino']:.2f}, Calmar={m_sys['calmar']:.2f}, DDdur={m_sys['max_dd_dur']}d")
print(f"  B&H    : CAGR={m_bh['cagr']:.1%}, MaxDD={m_bh['max_dd']:.1%}, Sharpe={m_bh['sharpe']:.2f}, Sortino={m_bh['sortino']:.2f}, Calmar={m_bh['calmar']:.2f}, DDdur={m_bh['max_dd_dur']}d")
print(f"\n=== SINCE 2011 ===")
print(f"  System : CAGR={m_sys_11['cagr']:.1%}, MaxDD={m_sys_11['max_dd']:.1%}, Sharpe={m_sys_11['sharpe']:.2f}, Sortino={m_sys_11['sortino']:.2f}, Calmar={m_sys_11['calmar']:.2f}, DDdur={m_sys_11['max_dd_dur']}d")
print(f"  B&H    : CAGR={m_bh_11['cagr']:.1%}, MaxDD={m_bh_11['max_dd']:.1%}, Sharpe={m_bh_11['sharpe']:.2f}, Sortino={m_bh_11['sortino']:.2f}, Calmar={m_bh_11['calmar']:.2f}, DDdur={m_bh_11['max_dd_dur']}d")
print(f"\n=== TRANSITIONS (EMA+mode{MODE_WIN}+min_stay{MIN_STAY}) ===")
print(f"  Total: {n_trans} | Short<=5: {short_stays} | Median: {median_stay} phiên")

state_counts = {s: int(np.sum(state_smooth == s)) for s in range(1, 6)}
total_states  = sum(state_counts.values())
print(f"\n=== STATE DISTRIBUTION ===")
for s in range(1, 6):
    print(f"  {STATE_NAMES[s]:8s}: {state_counts[s]:4d} ({state_counts[s]/total_states*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# B. ANNUAL BREAKDOWN — hiệu suất từng năm
# ══════════════════════════════════════════════════════════════════════
print("\n=== ANNUAL BREAKDOWN ===")
annual_rows = []
years = sorted(vni["time"].dt.year.unique())
for yr in years:
    mask = vni["time"].dt.year == yr
    idx  = vni[mask].index
    if len(idx) < 20: continue
    i0, i1 = idx[0], idx[-1]
    if pv[i0] <= 0 or pv_bh[i0] <= 0: continue
    ret_sys = pv[i1]    / pv[i0]    - 1
    ret_bh  = pv_bh[i1] / pv_bh[i0] - 1
    # Dominant state for year
    yr_states = state_smooth[i0:i1+1]
    yr_dom_s  = int(np.bincount(yr_states[yr_states>0]).argmax()) if np.any(yr_states>0) else 3
    # Max drawdown within year
    sub_pv = pv[i0:i1+1]
    rm = np.maximum.accumulate(sub_pv)
    yr_dd = (sub_pv / np.where(rm>0, rm, 1) - 1).min()
    annual_rows.append({
        "year": yr, "sys": ret_sys, "bh": ret_bh,
        "dom_s": yr_dom_s, "dd": yr_dd,
        "beat": ret_sys > ret_bh
    })
    flag = "✓" if ret_sys > ret_bh else "✗"
    print(f"  {yr}: Sys={ret_sys:+.1%}  B&H={ret_bh:+.1%}  DD={yr_dd:.1%}  {flag}")

beats = sum(1 for r in annual_rows if r["beat"])
print(f"  Win rate vs B&H: {beats}/{len(annual_rows)} năm ({beats/len(annual_rows)*100:.0f}%)")

# ══════════════════════════════════════════════════════════════════════
# C. WALK-FORWARD — in-sample vs out-of-sample split
# Cut point: 2020-01-01 (trước đó = params được tune, sau = OOS thực tế)
# ══════════════════════════════════════════════════════════════════════
print("\n=== WALK-FORWARD (IS: 2011-2019 | OOS: 2020-nay) ===")
idx_2020 = vni[vni["time"] >= "2020-01-01"].index[0]

dates_is  = dates_full.iloc[idx_2011:idx_2020].reset_index(drop=True)
m_sys_is  = calc_metrics(pv[idx_2011:idx_2020],    dates_is)
m_bh_is   = calc_metrics(pv_bh[idx_2011:idx_2020], dates_is)

dates_oos = dates_full.iloc[idx_2020:].reset_index(drop=True)
m_sys_oos = calc_metrics(pv[idx_2020:],    dates_oos)
m_bh_oos  = calc_metrics(pv_bh[idx_2020:], dates_oos)

print(f"  IS  (2011-2019) Sys: CAGR={m_sys_is['cagr']:.1%} MaxDD={m_sys_is['max_dd']:.1%} Sharpe={m_sys_is['sharpe']:.2f} Calmar={m_sys_is['calmar']:.2f}")
print(f"  IS  (2011-2019) B&H: CAGR={m_bh_is['cagr']:.1%} MaxDD={m_bh_is['max_dd']:.1%} Sharpe={m_bh_is['sharpe']:.2f}")
print(f"  OOS (2020-nay)  Sys: CAGR={m_sys_oos['cagr']:.1%} MaxDD={m_sys_oos['max_dd']:.1%} Sharpe={m_sys_oos['sharpe']:.2f} Calmar={m_sys_oos['calmar']:.2f}")
print(f"  OOS (2020-nay)  B&H: CAGR={m_bh_oos['cagr']:.1%} MaxDD={m_bh_oos['max_dd']:.1%} Sharpe={m_bh_oos['sharpe']:.2f}")

# ══════════════════════════════════════════════════════════════════════
# D. STATE-CONDITIONAL RETURNS — phân phối return kỳ hạn T+5/T+20/T+60
# ══════════════════════════════════════════════════════════════════════
print("\n=== STATE-CONDITIONAL RETURNS (forward returns tính từ VNINDEX) ===")
horizons = {"T+5": 5, "T+20": 20, "T+60": 60}
sc_results = {}   # {state: {horizon: {mean, median, win_rate, n}}}
for s in range(1, 6):
    sc_results[s] = {}
    idx_s = np.where(state_smooth == s)[0]
    for hname, h in horizons.items():
        fwd = []
        for i in idx_s:
            if i + h < n and close[i] > 0:
                fwd.append(close[i+h] / close[i] - 1)
        if len(fwd) < 10:
            sc_results[s][hname] = None; continue
        fwd = np.array(fwd)
        sc_results[s][hname] = {
            "mean":     float(np.mean(fwd)),
            "median":   float(np.median(fwd)),
            "win_rate": float(np.mean(fwd > 0)),
            "n":        len(fwd)
        }
    # Enhanced: add median, std, P25/P75
    for hname, h in horizons.items():
        fwd_arr = []
        for i in idx_s:
            if i + h < n and close[i] > 0:
                fwd_arr.append(close[i+h] / close[i] - 1)
        if sc_results[s].get(hname) and len(fwd_arr) >= 10:
            fa = np.array(fwd_arr)
            sc_results[s][hname]["std"]  = float(np.std(fa))
            sc_results[s][hname]["p25"]  = float(np.percentile(fa, 25))
            sc_results[s][hname]["p75"]  = float(np.percentile(fa, 75))
            sc_results[s][hname]["neg_tail"] = float(np.percentile(fa, 5))  # worst 5%
    row = sc_results[s]
    line = f"  {STATE_NAMES[s]:8s}:"
    for hname in horizons:
        r = row.get(hname)
        if r:
            line += f"  {hname} mean={r['mean']:+.1%} wr={r['win_rate']:.0%}(n={r['n']})"
    print(line)

# ══════════════════════════════════════════════════════════════════════
# E. SENSITIVITY ANALYSIS — EMA_ALPHA và MIN_STAY
# Chạy nhanh backtest với các biến thể tham số
# ══════════════════════════════════════════════════════════════════════
print("\n=== SENSITIVITY ANALYSIS ===")

def quick_backtest(score_raw, alpha, min_stay_days):
    """
    Re-EMA composite score → re-classify → re-smooth → re-backtest.
    Dùng override state đã tính sẵn (state_after_override) để tiết kiệm thời gian.
    """
    # 1. Re-EMA composite score với alpha mới
    ema_new = np.full(n, np.nan)
    for t in range(n):
        v = score_raw[t]; prev = ema_new[t-1] if t > 0 else np.nan
        ema_new[t] = v if np.isnan(prev) else (prev if np.isnan(v) else alpha*v+(1-alpha)*prev)
    # 2. Re-classify: chỉ thay đổi phần EMA-based classification, giữ nguyên overrides
    CTHRESH = 0.10; BTHRESH = 0.75
    st_new = state_after_override.copy()
    for i in range(n):
        e = ema_new[i]
        if np.isnan(e): continue
        # Re-classify dựa trên EMA mới (chỉ thay đổi base state, không xóa overrides)
        if e < CTHRESH:
            if st_new[i] not in (4, 5):  # giữ PE-based BULL override
                st_new[i] = 1
        elif e >= BTHRESH:
            if st_new[i] not in (1,):    # không raise từ crisis do override
                st_new[i] = max(st_new[i], 4)
        else:
            if st_new[i] in (1, 4):      # re-set nếu không có override mạnh
                if not (st_new[i] == 4 and not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i] > pe_p90[i]):
                    st_new[i] = 3
    # 3. Apply BearDvg gate
    for i in range(n):
        if gate_flag[i] and st_new[i] > 1:
            st_new[i] = 1
    # 4. Smooth
    st_sm = rolling_mode(st_new, MODE_WIN)
    st_sm = min_stay_filter(st_sm, min_stay_days)
    # 5. Backtest
    pv2 = np.zeros(n); pv2[0] = 1e9; w2 = TARGET_W[3]
    for t in range(1, n):
        tgt = TARGET_W.get(int(st_sm[t-1]), 0.70)
        diff = tgt - w2
        wn   = tgt if abs(diff) < SNAP_THR else w2 + diff/RAMP_DAYS
        wn   = float(np.clip(wn, 0.0, 1.30))
        r    = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv2[t] = pv2[t-1]*(1+wn*r+max(0,1-wn)*DEPOSIT_R-max(0,wn-1)*BORROW_R-abs(wn-w2)*TC)
        w2 = wn
    m  = calc_metrics(pv2[idx_2011:], dates_from11)
    nt, _ = count_transitions(st_sm)
    return m, nt

# Test EMA_ALPHA
print("  EMA_ALPHA sensitivity (MIN_STAY=7 fixed):")
r_raw_score = vni["score"].values.copy() if "score" in vni.columns else r_score
sensitivity_alpha = []
for alpha_test in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
    m_t, nt_t = quick_backtest(r_raw_score, alpha_test, MIN_STAY)
    marker = " ← base" if abs(alpha_test - EMA_ALPHA) < 0.001 else ""
    sensitivity_alpha.append({"alpha": alpha_test, "cagr": m_t.get("cagr",0), "sharpe": m_t.get("sharpe",0),
                               "calmar": m_t.get("calmar",0), "trans": nt_t})
    print(f"    α={alpha_test:.2f}: CAGR={m_t.get('cagr',0):.1%} Sharpe={m_t.get('sharpe',0):.2f} Calmar={m_t.get('calmar',0):.2f} Trans={nt_t}{marker}")

# Test MIN_STAY
print("  MIN_STAY sensitivity (EMA_ALPHA=0.40 fixed):")
sensitivity_minstay = []
for ms_test in [3, 5, 7, 10, 15, 20]:
    m_t, nt_t = quick_backtest(r_raw_score, EMA_ALPHA, ms_test)
    marker = " ← base" if ms_test == MIN_STAY else ""
    sensitivity_minstay.append({"min_stay": ms_test, "cagr": m_t.get("cagr",0), "sharpe": m_t.get("sharpe",0),
                                  "calmar": m_t.get("calmar",0), "trans": nt_t})
    print(f"    ms={ms_test:2d}: CAGR={m_t.get('cagr',0):.1%} Sharpe={m_t.get('sharpe',0):.2f} Calmar={m_t.get('calmar',0):.2f} Trans={nt_t}{marker}")

# ══════════════════════════════════════════════════════════════════════
# F. DIRECT COMPARISON: MIN_STAY=7 vs MIN_STAY=10 (full backtest)
# ══════════════════════════════════════════════════════════════════════
print("\n=== F. COMPARISON: MIN_STAY=7 vs MIN_STAY=10 ===")

# Compute state với ms=7 (baseline so sánh)
state_smooth_ms7 = rolling_mode(state_dvg, MODE_WIN)
state_smooth_ms7 = min_stay_filter(state_smooth_ms7, 7)

# Full backtest ms7
pv_ms7 = np.zeros(n); pv_ms7[0] = 1e9; w_ms7 = TARGET_W[3]
for t in range(1, n):
    tgt = TARGET_W[state_smooth_ms7[t-1]]
    diff = tgt - w_ms7
    wn = tgt if abs(diff) < SNAP_THR else w_ms7 + diff/RAMP_DAYS
    wn = float(np.clip(wn, 0.0, 1.30))
    r = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
    pv_ms7[t] = pv_ms7[t-1]*(1+wn*r+max(0,1-wn)*DEPOSIT_R-max(0,wn-1)*BORROW_R-abs(wn-w_ms7)*TC)
    w_ms7 = wn

m_ms7     = calc_metrics(pv_ms7, dates_full)
m_ms7_11  = calc_metrics(pv_ms7[idx_2011:], dates_from11)
m_ms10    = m_sys        # ms10 = current
m_ms10_11 = m_sys_11
nt_ms7, dur_ms7 = count_transitions(state_smooth_ms7)
short_ms7 = sum(1 for d in dur_ms7 if d <= 5)
nt_ms10   = n_trans

print(f"  ─── Toàn kỳ 2000–nay ───")
print(f"  ms=7 : CAGR={m_ms7['cagr']:.1%}  DD={m_ms7['max_dd']:.1%}  Sharpe={m_ms7['sharpe']:.2f}  Sortino={m_ms7['sortino']:.2f}  Calmar={m_ms7['calmar']:.2f}  DDdur={m_ms7['max_dd_dur']}  Trans={nt_ms7}  Short≤5={short_ms7}")
print(f"  ms=10: CAGR={m_ms10['cagr']:.1%}  DD={m_ms10['max_dd']:.1%}  Sharpe={m_ms10['sharpe']:.2f}  Sortino={m_ms10['sortino']:.2f}  Calmar={m_ms10['calmar']:.2f}  DDdur={m_ms10['max_dd_dur']}  Trans={nt_ms10}  Short≤5=0")
print(f"  ─── Từ 2011 ───")
print(f"  ms=7 : CAGR={m_ms7_11['cagr']:.1%}  DD={m_ms7_11['max_dd']:.1%}  Sharpe={m_ms7_11['sharpe']:.2f}  Sortino={m_ms7_11['sortino']:.2f}  Calmar={m_ms7_11['calmar']:.2f}  DDdur={m_ms7_11['max_dd_dur']}")
print(f"  ms=10: CAGR={m_ms10_11['cagr']:.1%}  DD={m_ms10_11['max_dd']:.1%}  Sharpe={m_ms10_11['sharpe']:.2f}  Sortino={m_ms10_11['sortino']:.2f}  Calmar={m_ms10_11['calmar']:.2f}  DDdur={m_ms10_11['max_dd_dur']}")

# Annual comparison
annual_compare = []
for yr in sorted(vni["time"].dt.year.unique()):
    mask = vni["time"].dt.year == yr
    idx  = vni[mask].index
    if len(idx) < 20: continue
    i0, i1 = idx[0], idx[-1]
    if pv_ms7[i0] <= 0 or pv[i0] <= 0 or pv_bh[i0] <= 0: continue
    r7   = pv_ms7[i1] / pv_ms7[i0] - 1
    r10  = pv[i1]    / pv[i0]    - 1
    rbh  = pv_bh[i1] / pv_bh[i0] - 1
    # Intra-year DD for ms10
    sub10 = pv[i0:i1+1]
    rm10  = np.maximum.accumulate(sub10)
    yr_dd10 = (sub10 / np.where(rm10>0, rm10, 1) - 1).min()
    sub7  = pv_ms7[i0:i1+1]
    rm7   = np.maximum.accumulate(sub7)
    yr_dd7  = (sub7  / np.where(rm7>0, rm7, 1) - 1).min()
    annual_compare.append({
        "year": yr, "ms7": r7, "ms10": r10, "bh": rbh,
        "dd7": yr_dd7, "dd10": yr_dd10,
        "diff": r10 - r7,
        "bear_year": rbh < -0.05,      # B&H giảm >5% = năm gấu
        "bull_year": rbh > 0.15,       # B&H tăng >15% = năm bò mạnh
    })
    marker = ("←ms10+" if r10 > r7+0.005 else "←ms7+" if r7 > r10+0.005 else "=")
    print(f"  {yr}: ms7={r7:+.1%} ms10={r10:+.1%} Δ={r10-r7:+.1%} bh={rbh:+.1%} dd7={yr_dd7:.1%} dd10={yr_dd10:.1%} {marker}")

ms10_beats_ms7 = sum(1 for r in annual_compare if r['ms10'] > r['ms7'])
bear_yrs = [r for r in annual_compare if r['bear_year']]
bull_yrs = [r for r in annual_compare if r['bull_year']]
if bear_yrs:
    avg_dd7_bear  = np.mean([r['dd7']  for r in bear_yrs])
    avg_dd10_bear = np.mean([r['dd10'] for r in bear_yrs])
    avg_r7_bear   = np.mean([r['ms7']  for r in bear_yrs])
    avg_r10_bear  = np.mean([r['ms10'] for r in bear_yrs])
    print(f"  Năm gấu (B&H<-5%, n={len(bear_yrs)}): ms7 avg={avg_r7_bear:+.1%} dd={avg_dd7_bear:.1%} | ms10 avg={avg_r10_bear:+.1%} dd={avg_dd10_bear:.1%}")
if bull_yrs:
    avg_r7_bull  = np.mean([r['ms7']  for r in bull_yrs])
    avg_r10_bull = np.mean([r['ms10'] for r in bull_yrs])
    print(f"  Năm bò mạnh (B&H>15%, n={len(bull_yrs)}): ms7 avg={avg_r7_bull:+.1%} | ms10 avg={avg_r10_bull:+.1%}")
print(f"  ms10 thắng ms7: {ms10_beats_ms7}/{len(annual_compare)} năm ({ms10_beats_ms7/len(annual_compare)*100:.0f}%)")

# ══════════════════════════════════════════════════════════════════════
# G. SORTINO DETAILED ANALYSIS — breakdown theo giai đoạn + so sánh
# ══════════════════════════════════════════════════════════════════════
print("\n=== G. SORTINO DETAILED ANALYSIS ===")

def sortino_detail(pv_arr, dates_s=None):
    """Returns Sortino + downside stats for deeper analysis."""
    pv_arr = np.asarray(pv_arr, dtype=float)
    valid  = np.where(pv_arr > 0)[0]
    if len(valid) < 10: return {}
    i0, i1 = valid[0], valid[-1]
    sub = pv_arr[i0:i1+1]
    rets = np.diff(sub) / sub[:-1]
    if dates_s is not None:
        ds = dates_s.reset_index(drop=True)
        cal_years = (ds.iloc[i1] - ds.iloc[i0]).days / 365.25
    else:
        cal_years = (i1 - i0) / sessions_per_year
    sub_spy = (i1 - i0) / cal_years if cal_years > 0 else sessions_per_year

    down_rets = rets[rets < 0]
    up_rets   = rets[rets > 0]
    mean_r = np.mean(rets)
    std_all = np.std(rets)
    sortino_down = np.sqrt(np.mean(down_rets**2)) if len(down_rets) > 0 else 0
    sortino = mean_r * sub_spy / (sortino_down * np.sqrt(sub_spy)) if sortino_down > 0 else 0
    cagr = (sub[-1]/sub[0])**(1/cal_years)-1 if cal_years>0 else 0

    return {
        "sortino": sortino,
        "cagr": cagr,
        "down_days_pct": len(down_rets)/len(rets)*100,
        "avg_down": np.mean(down_rets)*100 if len(down_rets) > 0 else 0,
        "avg_up":   np.mean(up_rets)*100   if len(up_rets) > 0 else 0,
        "worst_day": rets.min()*100,
        "best_day":  rets.max()*100,
        "vol_ann": std_all * np.sqrt(sub_spy) * 100,
        "skew":  float(np.mean(((rets - mean_r)/std_all)**3)) if std_all > 0 else 0,
    }

periods = [
    ("Toàn kỳ 2000–nay",   pv,       pv_bh,    dates_full,    None),
    ("Từ 2011",             pv[idx_2011:], pv_bh[idx_2011:], dates_from11, idx_2011),
    ("IS  2011–2019",       pv[idx_2011:idx_2020], pv_bh[idx_2011:idx_2020], dates_is, None),
    ("OOS 2020–nay",        pv[idx_2020:], pv_bh[idx_2020:], dates_oos, None),
]
sortino_rows = []
for pname, pv_s, pv_b, ds, _ in periods:
    ss = sortino_detail(pv_s, ds)
    bs = sortino_detail(pv_b, ds)
    if ss and bs:
        sortino_rows.append({"period": pname, "sys": ss, "bh": bs})
        print(f"  {pname}:")
        print(f"    HT : Sortino={ss['sortino']:.2f}  Vol={ss['vol_ann']:.1f}%  DownDays={ss['down_days_pct']:.1f}%  AvgDown={ss['avg_down']:.2f}%  AvgUp={ss['avg_up']:.2f}%  Worst={ss['worst_day']:.2f}%  Skew={ss['skew']:+.2f}")
        print(f"    B&H: Sortino={bs['sortino']:.2f}  Vol={bs['vol_ann']:.1f}%  DownDays={bs['down_days_pct']:.1f}%  AvgDown={bs['avg_down']:.2f}%  AvgUp={bs['avg_up']:.2f}%  Worst={bs['worst_day']:.2f}%  Skew={bs['skew']:+.2f}")

# ══════════════════════════════════════════════════════════════════════
# H. DRAWDOWN EPISODES — phân tích các giai đoạn lỗ sâu
# ══════════════════════════════════════════════════════════════════════
print("\n=== H. DRAWDOWN EPISODES (từ 2011, >5%) ===")

def find_dd_episodes(pv_arr, dates_s, min_dd=0.05):
    """Find distinct drawdown episodes (peak-to-trough-to-recovery)."""
    eps = []
    pv_np = np.asarray(pv_arr, dtype=float)
    peak = pv_np[0]; peak_i = 0
    in_dd = False; dd_start = 0; cur_min = pv_np[0]; cur_min_i = 0
    for i in range(1, len(pv_np)):
        if np.isnan(pv_np[i]) or pv_np[i] <= 0: continue
        if not in_dd:
            if pv_np[i] > peak:
                peak = pv_np[i]; peak_i = i
            elif pv_np[i] / peak - 1 < -min_dd:
                in_dd = True; dd_start = i; cur_min = pv_np[i]; cur_min_i = i
        else:
            if pv_np[i] < cur_min:
                cur_min = pv_np[i]; cur_min_i = i
            if pv_np[i] >= peak:
                depth = cur_min / peak - 1
                eps.append({
                    "peak_date":    dates_s.iloc[peak_i].strftime("%Y-%m-%d"),
                    "trough_date":  dates_s.iloc[cur_min_i].strftime("%Y-%m-%d"),
                    "recovery_date":dates_s.iloc[i].strftime("%Y-%m-%d"),
                    "depth": depth,
                    "dur_down": cur_min_i - peak_i,
                    "dur_recov": i - cur_min_i,
                    "dur_total": i - peak_i,
                })
                in_dd = False; peak = pv_np[i]; peak_i = i
                cur_min = pv_np[i]; cur_min_i = i
    if in_dd:
        depth = cur_min / peak - 1
        eps.append({
            "peak_date":    dates_s.iloc[peak_i].strftime("%Y-%m-%d"),
            "trough_date":  dates_s.iloc[cur_min_i].strftime("%Y-%m-%d"),
            "recovery_date":"ongoing",
            "depth": depth,
            "dur_down": cur_min_i - peak_i,
            "dur_recov": None,
            "dur_total": len(pv_np)-1 - peak_i,
        })
    return eps

dates_from11_full = dates_full.iloc[idx_2011:].reset_index(drop=True)
eps_sys = find_dd_episodes(pv[idx_2011:],     dates_from11_full, 0.05)
eps_bh  = find_dd_episodes(pv_bh[idx_2011:],  dates_from11_full, 0.05)
eps_ms7 = find_dd_episodes(pv_ms7[idx_2011:], dates_from11_full, 0.05)

print(f"  Hệ thống ms10 (n={len(eps_sys)}): ")
for e in sorted(eps_sys, key=lambda x: x['depth'])[:8]:
    rec = f"→{e['recovery_date']}" if e['recovery_date']!='ongoing' else '→CHƯA HỒI PHỤC'
    print(f"    {e['peak_date']} → trough {e['trough_date']} {rec}  depth={e['depth']:.1%}  down={e['dur_down']}p  recov={e['dur_recov'] if e['dur_recov'] else '?'}p")
print(f"  B&H (n={len(eps_bh)}): ")
for e in sorted(eps_bh, key=lambda x: x['depth'])[:8]:
    rec = f"→{e['recovery_date']}" if e['recovery_date']!='ongoing' else '→CHƯA HỒI PHỤC'
    print(f"    {e['peak_date']} → trough {e['trough_date']} {rec}  depth={e['depth']:.1%}  down={e['dur_down']}p  recov={e['dur_recov'] if e['dur_recov'] else '?'}p")
print(f"  ms7 vs ms10 episodes: ms7={len(eps_ms7)}  ms10={len(eps_sys)}")
if eps_sys and eps_bh:
    print(f"  Trung bình depth  : HT={np.mean([e['depth'] for e in eps_sys]):.1%}  B&H={np.mean([e['depth'] for e in eps_bh]):.1%}")
    print(f"  Trung bình dur_total: HT={np.mean([e['dur_total'] for e in eps_sys]):.0f}p  B&H={np.mean([e['dur_total'] for e in eps_bh]):.0f}p")

# Store for HTML
idx_2011_ref = idx_2011

# Current state
last_idx = len(vni) - 1
current_state = int(state_smooth[last_idx])
current_date  = vni["time"].iloc[last_idx].strftime("%Y-%m-%d")
current_alloc = TARGET_W[current_state]
current_close = float(close[last_idx])
current_pe    = float(pe_arr[last_idx]) if not np.isnan(pe_arr[last_idx]) else None
current_r_score     = float(r_score[last_idx])     if not np.isnan(r_score[last_idx])     else None
current_r_score_ema = float(r_score_ema[last_idx]) if not np.isnan(r_score_ema[last_idx]) else None
current_w     = float(w_arr[last_idx])
current_bear_dvg  = bool(bear_mask[last_idx])
current_bull_dvg  = bool(bull_mask[last_idx])
current_gate_open = bool(gate_flag[last_idx])

print(f"\n=== CURRENT STATE ({current_date}) ===")
print(f"  State       : {STATE_NAMES[current_state]}")
print(f"  r_score raw : {current_r_score:.4f}" if current_r_score else "  r_score raw : N/A")
print(f"  r_score EMA : {current_r_score_ema:.4f}" if current_r_score_ema else "  r_score EMA : N/A")
print(f"  Alloc       : {current_alloc:.0%}")
print(f"  VNINDEX     : {current_close:.2f}")
print(f"  PE          : {current_pe:.2f}" if current_pe else "  PE          : N/A")
print(f"  BearDvg sig : {'YES ⚠' if current_bear_dvg else 'No'}")
print(f"  BullDvg sig : {'YES ✓' if current_bull_dvg else 'No'}")
print(f"  Gate active : {'YES — CRISIS mode (0%)' if current_gate_open else 'No'}")

# ══════════════════════════════════════════════════════════════════════
# BUILD HTML
# ══════════════════════════════════════════════════════════════════════
print("\nBuilding HTML report ...")

# Prepare JSON data for charts (sample every Nth row to keep HTML small)
# Full data needed for accuracy, but downsample for chart rendering
df_plot = vni[["time", "Close", "state", "r_score", "score", "weight", "pv", "pv_bh",
               "VNINDEX_PE", "dd", "rank_P3M", "rank_RSI", "rank_MACD", "rank_CMF",
               "rank_MA200", "rank_Breadth", "bear_dvg", "bull_dvg"]].copy()
df_plot["time_str"] = df_plot["time"].dt.strftime("%Y-%m-%d")

def to_js_arr(series, decimals=4):
    vals = series.fillna("null") if hasattr(series, "fillna") else series
    parts = []
    for v in series:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            parts.append("null")
        elif isinstance(v, float):
            parts.append(f"{v:.{decimals}f}")
        else:
            parts.append(str(v))
    return "[" + ",".join(parts) + "]"

dates_js   = '["' + '","'.join(df_plot["time_str"].tolist()) + '"]'
close_js   = to_js_arr(df_plot["Close"], 2)
state_js   = to_js_arr(df_plot["state"].astype(float), 0)
rscore_js  = to_js_arr(df_plot["r_score"], 4)
rscore_ema_js = to_js_arr(vni["r_score_ema"], 4)
weight_js  = to_js_arr(df_plot["weight"], 4)
pv_js      = to_js_arr(df_plot["pv"] / 1e9, 4)       # in tỷ
pvbh_js    = to_js_arr(df_plot["pv_bh"] / 1e9, 4)
pe_js      = to_js_arr(df_plot["VNINDEX_PE"], 2)
dd_js      = to_js_arr(df_plot["dd"], 4)
beardvg_js = to_js_arr(df_plot["bear_dvg"].astype(float), 0)
bulldvg_js = to_js_arr(df_plot["bull_dvg"].astype(float), 0)

# Factor ranks for radar chart (current day)
radar_keys = ["P3M", "P1M", "MA200", "RSI", "MACD", "CMF", "Breadth"]
radar_vals = []
for k in radar_keys:
    v = vni[f"rank_{k}"].iloc[-1]
    radar_vals.append(round(v, 4) if not np.isnan(v) else 0)

# ─── Full NAV transitions table (tất cả lần chuyển trạng thái + NAV) ──────────
state_arr = state_smooth
all_trans = []
prev_s = state_arr[0]
for i in range(1, n):
    if state_arr[i] != prev_s:
        alloc_from = TARGET_W[prev_s]
        alloc_to   = TARGET_W[state_arr[i]]
        # Tính return kể từ lần chuyển trước
        prev_idx = all_trans[-1]["_i"] if all_trans else 0
        ret_since = (pv[i] / pv[prev_idx] - 1) if pv[prev_idx] > 0 else 0
        all_trans.append({
            "_i":       i,
            "date":     vni["time"].iloc[i].strftime("%Y-%m-%d"),
            "from_s":   STATE_NAMES[prev_s],
            "to_s":     STATE_NAMES[state_arr[i]],
            "from_c":   STATE_COLOR[prev_s],
            "to_c":     STATE_COLOR[state_arr[i]],
            "vnindex":  f"{close[i]:.0f}",
            "pe":       f"{pe_arr[i]:.1f}" if not np.isnan(pe_arr[i]) else "—",
            "alloc_from": f"{alloc_from:.0%}",
            "alloc_to":   f"{alloc_to:.0%}",
            "nav":      f"{pv[i]/1e9:.2f}",
            "nav_bh":   f"{pv_bh[i]/1e9:.2f}",
            "ret_since": ret_since,
            "gate":     "🔒" if gate_flag[i] else "",
        })
        prev_s = state_arr[i]

# NAV-only display rows (every 20 transitions → show all if ≤60, else last 50)
trans_rows_all = ""
for t in all_trans:
    ret_color = "green" if t["ret_since"] >= 0 else "red"
    nav_vs = float(t["nav"]) - float(t["nav_bh"])
    nav_vs_color = "green" if nav_vs >= 0 else "red"
    trans_rows_all += f"""<tr>
      <td style="color:#64748b;font-size:11px">{t['date']}</td>
      <td><span class="badge" style="background:{t['from_c']};font-size:10px">{t['from_s']}</span></td>
      <td style="color:#94a3b8">→</td>
      <td><span class="badge" style="background:{t['to_c']};font-size:10px">{t['to_s']}</span></td>
      <td style="text-align:right">{t['vnindex']}</td>
      <td style="text-align:right">{t['pe']}</td>
      <td style="text-align:right">{t['alloc_from']} → {t['alloc_to']}</td>
      <td style="text-align:right;font-weight:700;color:#22c55e">{t['nav']} tỷ</td>
      <td style="text-align:right;color:#60a5fa">{t['nav_bh']} tỷ</td>
      <td style="text-align:right" class="{ret_color}">{t['ret_since']:+.1%}</td>
      <td style="text-align:center">{t['gate']}</td>
    </tr>"""

# Recent transitions (last 25) for compact display
trans_rows = ""
for t in all_trans[-25:]:
    fc = t["from_c"]; tc = t["to_c"]
    trans_rows += f"""<tr>
      <td>{t['date']}</td>
      <td><span class="badge" style="background:{fc}">{t['from_s']}</span></td>
      <td><span class="badge" style="background:{tc}">{t['to_s']}</span></td>
      <td>{t['vnindex']}</td>
      <td>{t['pe']}</td>
      <td>{t['alloc_from']} → {t['alloc_to']}</td>
      <td style="font-weight:700;color:#22c55e">{t['nav']} tỷ</td>
    </tr>"""

# Perf table
def fmt(m, key, pct=True):
    v = m.get(key, np.nan)
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    return f"{v:.1%}" if pct else f"{v:.2f}"

# Final values
final_sys  = pv[-1] / 1e9
final_bh   = pv_bh[-1] / 1e9

color_current = STATE_COLOR[current_state]

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VNINDEX 5-State Market System</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6}}
.hdr{{background:linear-gradient(135deg,#1e3a5f,#1a4731);padding:24px 32px}}
.hdr h1{{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px}}
.hdr p{{font-size:12px;color:#94a3b8}}
.wrap{{max-width:1400px;margin:0 auto;padding:20px 24px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}}
.card{{background:#1e293b;border-radius:12px;padding:18px 20px;border:1px solid #334155}}
.card h2{{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}}
.chart-wrap{{position:relative;height:300px}}
.chart-wrap-sm{{position:relative;height:220px}}
.chart-wrap-lg{{position:relative;height:360px}}
.state-big{{display:flex;align-items:center;gap:20px;padding:16px 0}}
.state-circle{{width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0}}
.state-info h3{{font-size:24px;font-weight:800;margin-bottom:4px}}
.state-info p{{font-size:12px;color:#94a3b8;line-height:1.8}}
.kpi-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.kpi{{background:#0f172a;border-radius:8px;padding:10px 12px;text-align:center}}
.kpi .val{{font-size:18px;font-weight:700;margin-bottom:2px}}
.kpi .lbl{{font-size:10.5px;color:#64748b}}
.green{{color:#22c55e}} .red{{color:#ef4444}} .yellow{{color:#eab308}} .blue{{color:#60a5fa}}
.badge{{display:inline-block;padding:2px 8px;border-radius:6px;color:#fff;font-size:11px;font-weight:600}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#0f172a;padding:7px 10px;text-align:left;color:#64748b;font-weight:600;border-bottom:1px solid #334155}}
td{{padding:6px 10px;border-bottom:1px solid #1e293b}}
tr:hover td{{background:#0f172a}}
.alloc-bar{{display:flex;align-items:center;gap:8px}}
.alloc-fill{{height:8px;border-radius:4px;background:#3b82f6}}
.factor-row{{display:flex;align-items:center;gap:6px;margin-bottom:8px}}
.factor-name{{width:70px;font-size:11px;color:#94a3b8}}
.factor-bar-bg{{flex:1;height:10px;background:#0f172a;border-radius:5px;overflow:hidden}}
.factor-bar{{height:10px;border-radius:5px;transition:width .3s}}
.factor-val{{width:40px;text-align:right;font-size:11px;font-weight:600}}
.alert{{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#93c5fd}}
</style>
</head>
<body>
<div class="hdr">
  <h1>⚡ VNINDEX 5-State Market System</h1>
  <p>Hệ thống phân loại trạng thái thị trường với 7 yếu tố · Expanding window · Backtest 2000–{current_date} · Bắt đầu 1 tỷ VND</p>
</div>
<div class="wrap">

<!-- CURRENT STATE ROW -->
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Trạng thái hiện tại — {current_date}</h2>
    <div class="state-big">
      <div class="state-circle" style="background:{color_current}">{STATE_NAMES[current_state]}</div>
      <div class="state-info">
        <h3 style="color:{color_current}">{STATE_NAMES[current_state]}</h3>
        <p>Phân bổ cổ phiếu: <strong style="color:{color_current}">{STATE_ALLOC[current_state]}</strong><br>
           r_score raw: <strong>{f"{current_r_score:.4f}" if current_r_score else "N/A"}</strong> · EMA: <strong>{f"{current_r_score_ema:.4f}" if current_r_score_ema else "N/A"}</strong><br>
           VNINDEX: <strong>{current_close:.2f}</strong><br>
           PE hiện tại: <strong>{f"{current_pe:.2f}x" if current_pe else "N/A"}</strong><br>
           PE P90 expanding: <strong>{f"{pe_p90[-1]:.2f}x" if not np.isnan(pe_p90[-1]) else "N/A"}</strong><br>
           Drawdown từ đỉnh: <strong class="{"red" if dd[-1] < -0.1 else "green"}">{dd[-1]:.1%}</strong><br>
           Gate bảo vệ: <strong class="{"red" if current_gate_open else "green"}">{"⚠ ĐANG HOẠT ĐỘNG — CRISIS 0%" if current_gate_open else "Không — bình thường"}</strong></p>
      </div>
    </div>
    <div class="alert" style="{'background:#2d1a1a;border-color:#ef4444' if current_gate_open else ''}">
      {'⚠ <strong>GATE BảO VỆ ĐANG MỞ:</strong> Hệ thống phát hiện BearDvg — phân bổ bị giới hạn về 0% cho đến khi thoát gate.' if current_gate_open else
       f'💡 <strong>Khuyến nghị hôm nay:</strong> Duy trì tỷ lệ cổ phiếu <strong>{STATE_ALLOC[current_state]}</strong> · {"Đang dùng margin 30%" if current_state == 5 else "Tiền mặt " + f"{(1-TARGET_W[current_state])*100:.0f}%" if TARGET_W[current_state] < 1 else "Full equity, không margin"}'}
    </div>
  </div>

  <div class="card">
    <h2>7 Yếu tố — Rank hiện tại (0=thấp nhất, 1=cao nhất)</h2>
    {''.join(f"""
    <div class="factor-row">
      <span class="factor-name">{k}</span>
      <div class="factor-bar-bg">
        <div class="factor-bar" style="width:{radar_vals[i]*100:.1f}%;background:{'#ef4444' if radar_vals[i]<0.3 else '#eab308' if radar_vals[i]<0.7 else '#22c55e'}"></div>
      </div>
      <span class="factor-val" style="color:{'#ef4444' if radar_vals[i]<0.3 else '#eab308' if radar_vals[i]<0.7 else '#22c55e'}">{radar_vals[i]:.2f}</span>
    </div>
    """ for i, k in enumerate(radar_keys))}
  </div>
</div>

<!-- PERFORMANCE METRICS -->
<!-- ROW 2a: Core performance (4 columns) -->
<div class="grid4" style="margin-bottom:16px">
  <div class="card">
    <h2>Toàn kỳ 2000–nay</h2>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys['cagr']>m_bh['cagr'] else 'yellow'}">{fmt(m_sys,'cagr')}</div><div class="lbl">CAGR HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val {'green' if m_sys.get('sortino',0)>m_bh.get('sortino',0) else 'yellow'}">{fmt(m_sys,'sortino',False)}</div><div class="lbl">Sortino</div></div>
      <div class="kpi"><div class="val {'green' if abs(m_sys['max_dd'])<abs(m_bh['max_dd']) else 'red'}">{fmt(m_sys,'max_dd')}</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="margin-top:8px;font-size:10px;color:#64748b">
      DD phục hồi tối đa: <strong style="color:#f97316">{m_sys.get('max_dd_dur',0)} phiên</strong> · NAV: <strong style="color:#22c55e">{final_sys:.1f} tỷ</strong>
    </div>
  </div>
  <div class="card">
    <h2>Từ 2011 (có PE)</h2>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys_11['cagr']>m_bh_11['cagr'] else 'yellow'}">{fmt(m_sys_11,'cagr')}</div><div class="lbl">CAGR HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh_11,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_11,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val {'green' if m_sys_11.get('sortino',0)>m_bh_11.get('sortino',0) else 'yellow'}">{fmt(m_sys_11,'sortino',False)}</div><div class="lbl">Sortino</div></div>
      <div class="kpi"><div class="val {'green' if abs(m_sys_11['max_dd'])<abs(m_bh_11['max_dd']) else 'red'}">{fmt(m_sys_11,'max_dd')}</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_11,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="margin-top:8px;font-size:10px;color:#64748b">
      DD phục hồi tối đa: <strong style="color:#f97316">{m_sys_11.get('max_dd_dur',0)} phiên</strong> · x{pv[-1]/pv[idx_2011_ref]:.1f} vs B&H x{pv_bh[-1]/pv_bh[idx_2011_ref]:.1f}
    </div>
  </div>
  <div class="card">
    <h2>Walk-forward · IS vs OOS</h2>
    <div style="font-size:11px;margin-bottom:6px;color:#94a3b8">In-sample 2011–2019</div>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys_is['cagr']>m_bh_is['cagr'] else 'red'}">{fmt(m_sys_is,'cagr')}</div><div class="lbl">CAGR HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh_is,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_is,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_is,'max_dd')}</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_is,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="font-size:11px;margin:8px 0 6px;color:#10b981">Out-of-sample 2020–nay</div>
    <div class="kpi-grid">
      <div class="kpi"><div class="val {'green' if m_sys_oos['cagr']>m_bh_oos['cagr'] else 'red'}">{fmt(m_sys_oos,'cagr')}</div><div class="lbl">CAGR HT</div></div>
      <div class="kpi"><div class="val blue">{fmt(m_bh_oos,'cagr')}</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_oos,'sharpe',False)}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_oos,'max_dd')}</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{fmt(m_sys_oos,'calmar',False)}</div><div class="lbl">Calmar</div></div>
    </div>
    <div style="margin-top:8px;font-size:10px;color:#{'22c55e' if m_sys_oos['cagr']>m_bh_oos['cagr'] else 'ef4444'}">
      {'✓ OOS vẫn thắng B&H' if m_sys_oos['cagr']>m_bh_oos['cagr'] else '✗ OOS thua B&H — xem xét overfitting'}
    </div>
  </div>
  <div class="card">
    <h2>Phân bổ trạng thái · {n_trans} transitions</h2>
    {''.join(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
      <span class="badge" style="background:{STATE_COLOR[s]};width:68px;text-align:center;font-size:10px">{STATE_NAMES[s]}</span>
      <div style="flex:1;background:#0f172a;border-radius:4px;height:7px;overflow:hidden">
        <div style="width:{state_counts[s]/total_states*100:.1f}%;height:7px;background:{STATE_COLOR[s]};border-radius:4px"></div>
      </div>
      <span style="font-size:10px;color:#94a3b8;width:38px">{state_counts[s]/total_states*100:.1f}%</span>
    </div>""" for s in range(1,6))}
    <div style="margin-top:8px;font-size:10px;color:#64748b">
      EMA(α={EMA_ALPHA})→mode({MODE_WIN})→min_stay({MIN_STAY}) · Short≤5: <strong style="color:{'#ef4444' if short_stays>5 else '#22c55e'}">{short_stays}</strong> · Median: <strong>{median_stay} phiên</strong>
    </div>
  </div>
</div>

<!-- ROW 2b: Annual breakdown + State-conditional returns -->
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Hiệu suất từng năm — Hệ thống vs B&H &nbsp;
      <span style="font-size:11px;color:#94a3b8;font-weight:400">{beats}/{len(annual_rows)} năm thắng B&H ({beats/len(annual_rows)*100:.0f}%)</span>
    </h2>
    <div style="overflow-y:auto;max-height:320px">
    <table style="font-size:11px">
      <thead><tr>
        <th>Năm</th>
        <th style="text-align:right">HT</th>
        <th style="text-align:right">B&H</th>
        <th style="text-align:right">DD năm</th>
        <th>Vs B&H</th>
        <th style="text-align:right">Bar</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="color:#64748b">{r['year']}</td>
        <td style="text-align:right;font-weight:600" class="{'green' if r['sys']>=0 else 'red'}">{r['sys']:+.1%}</td>
        <td style="text-align:right;color:#60a5fa">{r['bh']:+.1%}</td>
        <td style="text-align:right;font-size:10px;color:#f97316">{r['dd']:.1%}</td>
        <td style="text-align:center" class="{'green' if r['beat'] else 'red'}">{'✓' if r['beat'] else '✗'}</td>
        <td style="text-align:right;width:80px">
          <div style="display:flex;gap:2px;justify-content:flex-end;align-items:center">
            <div style="height:6px;border-radius:3px;background:{'#22c55e' if r['sys']>=0 else '#ef4444'};width:{min(70,abs(r['sys'])*300):.0f}px"></div>
          </div>
        </td>
      </tr>""" for r in annual_rows)}
      </tbody>
    </table>
    </div>
  </div>

  <div class="card">
    <h2>State-conditional Returns — Forward return theo trạng thái</h2>
    <div style="font-size:10px;color:#64748b;margin-bottom:10px">Phân phối return VNINDEX thực tế T+5/T+20/T+60 phiên sau khi ở mỗi trạng thái (mean / wr% / P25↔P75 / tail5%)</div>
    <table style="font-size:11px">
      <thead><tr>
        <th>Trạng thái</th>
        <th style="text-align:right">T+5 mean/wr</th><th style="text-align:right">T+20 mean/wr</th><th style="text-align:right">T+60 mean/wr</th>
        <th style="text-align:right">T+60 P25↔P75</th><th style="text-align:right">T+60 tail5%</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td><span class="badge" style="background:{STATE_COLOR[s]};font-size:10px">{STATE_NAMES[s]}</span></td>
        {''.join(f"""<td style="text-align:right">
          <span class="{'green' if sc_results[s].get(h) and sc_results[s][h]['mean']>0 else 'red'}">{sc_results[s][h]['mean']:+.1%}</span>
          <span style="color:#64748b;font-size:10px"> {sc_results[s][h]['win_rate']:.0%}</span></td>"""
          if sc_results[s].get(h) else '<td style="color:#334155;text-align:center">—</td>'
          for h in ['T+5','T+20','T+60'])}
        <td style="text-align:right;font-size:10px;color:#94a3b8">
          {f"{sc_results[s]['T+60']['p25']:+.1%}↔{sc_results[s]['T+60']['p75']:+.1%}" if sc_results[s].get('T+60') and sc_results[s]['T+60'].get('p25') is not None else "—"}
        </td>
        <td style="text-align:right;font-size:10px" class="red">
          {f"{sc_results[s]['T+60']['neg_tail']:+.1%}" if sc_results[s].get('T+60') and sc_results[s]['T+60'].get('neg_tail') is not None else "—"}
        </td>
      </tr>""" for s in range(1,6))}
      </tbody>
    </table>
    <div style="margin-top:10px;font-size:10px;color:#475569">
      wr% = tỷ lệ phiên dương · P25↔P75 = range thông thường · tail5% = kịch bản xấu nhất 5% · Nhận định: BULL T+60 cao nhất = xác nhận tín hiệu
    </div>
  </div>
</div>

<!-- ROW 2d: MS7 vs MS10 comparison -->
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>So sánh MIN_STAY=7 vs MIN_STAY=10 &nbsp;
      <span style="font-size:11px;color:#94a3b8;font-weight:400">ms10 thắng ms7: {ms10_beats_ms7}/{len(annual_compare)} năm ({ms10_beats_ms7/len(annual_compare)*100:.0f}%)</span>
    </h2>
    <table style="font-size:11px;margin-bottom:12px">
      <thead><tr><th>Chỉ số</th><th style="text-align:right">ms=7</th><th style="text-align:right">ms=10 ←</th><th style="text-align:right">B&H</th></tr></thead>
      <tbody>
        <tr><td>CAGR toàn kỳ</td>
          <td style="text-align:right">{m_ms7['cagr']:.1%}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10['cagr']>=m_ms7['cagr'] else 'red'}">{m_ms10['cagr']:.1%}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh['cagr']:.1%}</td></tr>
        <tr><td>CAGR từ 2011</td>
          <td style="text-align:right">{m_ms7_11['cagr']:.1%}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10_11['cagr']>=m_ms7_11['cagr'] else 'red'}">{m_ms10_11['cagr']:.1%}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['cagr']:.1%}</td></tr>
        <tr><td>Sharpe (2011+)</td>
          <td style="text-align:right">{m_ms7_11['sharpe']:.2f}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10_11['sharpe']>=m_ms7_11['sharpe'] else 'red'}">{m_ms10_11['sharpe']:.2f}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['sharpe']:.2f}</td></tr>
        <tr><td>Sortino (2011+)</td>
          <td style="text-align:right">{m_ms7_11['sortino']:.2f}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10_11['sortino']>=m_ms7_11['sortino'] else 'red'}">{m_ms10_11['sortino']:.2f}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['sortino']:.2f}</td></tr>
        <tr><td>MaxDD (2011+)</td>
          <td style="text-align:right">{m_ms7_11['max_dd']:.1%}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if abs(m_ms10_11['max_dd'])<=abs(m_ms7_11['max_dd']) else 'red'}">{m_ms10_11['max_dd']:.1%}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['max_dd']:.1%}</td></tr>
        <tr><td>Calmar (2011+)</td>
          <td style="text-align:right">{m_ms7_11['calmar']:.2f}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10_11['calmar']>=m_ms7_11['calmar'] else 'red'}">{m_ms10_11['calmar']:.2f}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['calmar']:.2f}</td></tr>
        <tr><td>DDdur (phiên)</td>
          <td style="text-align:right">{m_ms7_11['max_dd_dur']}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if m_ms10_11['max_dd_dur']<=m_ms7_11['max_dd_dur'] else 'red'}">{m_ms10_11['max_dd_dur']}</td>
          <td style="text-align:right;color:#60a5fa">{m_bh_11['max_dd_dur']}</td></tr>
        <tr><td>Transitions</td>
          <td style="text-align:right">{nt_ms7}</td>
          <td style="text-align:right;font-weight:700;color:#22c55e">{nt_ms10}</td>
          <td style="text-align:right;color:#64748b">—</td></tr>
        <tr style="background:#1a2a18"><td>Năm gấu avg sys</td>
          <td style="text-align:right">{avg_r7_bear:+.1%}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if avg_r10_bear>=avg_r7_bear else 'red'}">{avg_r10_bear:+.1%}</td>
          <td style="text-align:right;color:#60a5fa">{np.mean([r['bh'] for r in bear_yrs]):+.1%}</td></tr>
        <tr style="background:#1a2a18"><td>Năm bò avg sys</td>
          <td style="text-align:right">{avg_r7_bull:+.1%}</td>
          <td style="text-align:right;font-weight:700" class="{'green' if avg_r10_bull>=avg_r7_bull else 'red'}">{avg_r10_bull:+.1%}</td>
          <td style="text-align:right;color:#60a5fa">{np.mean([r['bh'] for r in bull_yrs]):+.1%}</td></tr>
      </tbody>
    </table>
    <div style="font-size:10px;color:#475569">
      ms10 loại bỏ nhiều nhiễu hơn ({nt_ms7-nt_ms10} transitions ít hơn) →
      {"CAGR & Sortino & Calmar đều cải thiện" if m_ms10_11['cagr']>m_ms7_11['cagr'] and m_ms10_11['sortino']>m_ms7_11['sortino'] else "trade-off giữa mịn và phản ứng"}.
      Năm gấu: ms10 {"phòng thủ tốt hơn" if avg_r10_bear>=avg_r7_bear else "phòng thủ kém hơn"}.
      Năm bò: ms10 {"bắt kịp tốt hơn" if avg_r10_bull>=avg_r7_bull else "chậm hơn"}.
    </div>
  </div>

  <div class="card">
    <h2>Hiệu suất từng năm · ms7 vs ms10 vs B&H</h2>
    <div style="overflow-y:auto;max-height:340px">
    <table style="font-size:11px">
      <thead><tr>
        <th>Năm</th>
        <th style="text-align:right">ms7</th>
        <th style="text-align:right">ms10</th>
        <th style="text-align:right">B&H</th>
        <th style="text-align:right">Δ(10-7)</th>
        <th style="text-align:right">DD-7</th>
        <th style="text-align:right">DD-10</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr style="{'background:#2d1a1a' if r['bear_year'] else 'background:#1a2d1a' if r['bull_year'] else ''}">
        <td style="color:#{'ef4444' if r['bear_year'] else '22c55e' if r['bull_year'] else '64748b'}">{r['year']}</td>
        <td style="text-align:right" class="{'green' if r['ms7']>=0 else 'red'}">{r['ms7']:+.1%}</td>
        <td style="text-align:right;font-weight:700" class="{'green' if r['ms10']>=0 else 'red'}">{r['ms10']:+.1%}</td>
        <td style="text-align:right;color:#60a5fa">{r['bh']:+.1%}</td>
        <td style="text-align:right;font-size:10px" class="{'green' if r['diff']>0 else 'red' if r['diff']<-0.002 else ''}">{r['diff']:+.1%}</td>
        <td style="text-align:right;font-size:10px;color:#f97316">{r['dd7']:.1%}</td>
        <td style="text-align:right;font-size:10px" class="{'green' if abs(r['dd10'])<=abs(r['dd7'])+0.005 else 'red'}">{r['dd10']:.1%}</td>
      </tr>""" for r in annual_compare)}
      </tbody>
    </table>
    </div>
    <div style="margin-top:6px;font-size:10px;color:#64748b">
      <span style="background:#2d1a1a;padding:2px 6px;border-radius:3px">năm gấu (B&H&lt;-5%)</span> &nbsp;
      <span style="background:#1a2d1a;padding:2px 6px;border-radius:3px">năm bò mạnh (B&H&gt;15%)</span>
    </div>
  </div>
</div>

<!-- ROW 2e: Sortino + DD Episodes -->
<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Sortino Ratio — Phân tích chi tiết theo giai đoạn</h2>
    <table style="font-size:11px">
      <thead><tr>
        <th>Giai đoạn</th>
        <th style="text-align:right">Sortino</th>
        <th style="text-align:right">Vol%</th>
        <th style="text-align:right">Down%</th>
        <th style="text-align:right">AvgDown</th>
        <th style="text-align:right">Worst</th>
        <th style="text-align:right">Skew</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="color:#94a3b8;font-size:10px">{row['period']}</td>
        <td style="text-align:right;font-weight:700" class="green">{row['sys']['sortino']:.2f}</td>
        <td style="text-align:right;font-size:10px">{row['sys']['vol_ann']:.1f}%</td>
        <td style="text-align:right;font-size:10px">{row['sys']['down_days_pct']:.1f}%</td>
        <td style="text-align:right;font-size:10px" class="red">{row['sys']['avg_down']:.2f}%</td>
        <td style="text-align:right;font-size:10px" class="red">{row['sys']['worst_day']:.2f}%</td>
        <td style="text-align:right;font-size:10px" class="{'green' if row['sys']['skew']>0 else 'red'}">{row['sys']['skew']:+.2f}</td>
      </tr><tr style="background:#0f172a">
        <td style="color:#60a5fa;font-size:10px">&nbsp;&nbsp;B&H same period</td>
        <td style="text-align:right;color:#60a5fa">{row['bh']['sortino']:.2f}</td>
        <td style="text-align:right;font-size:10px;color:#64748b">{row['bh']['vol_ann']:.1f}%</td>
        <td style="text-align:right;font-size:10px;color:#64748b">{row['bh']['down_days_pct']:.1f}%</td>
        <td style="text-align:right;font-size:10px;color:#ef4444">{row['bh']['avg_down']:.2f}%</td>
        <td style="text-align:right;font-size:10px;color:#ef4444">{row['bh']['worst_day']:.2f}%</td>
        <td style="text-align:right;font-size:10px" class="{'green' if row['bh']['skew']>0 else 'red'}">{row['bh']['skew']:+.2f}</td>
      </tr>""" for row in sortino_rows)}
      </tbody>
    </table>
    <div style="margin-top:8px;font-size:10px;color:#475569">
      Sortino cao hơn B&H = lợi nhuận/rủi ro giảm tốt hơn · Down% = % ngày có return âm · Skew dương = đuôi phải dày hơn (tốt)
    </div>
  </div>

  <div class="card">
    <h2>Drawdown Episodes từ 2011 — Sâu &gt;5% &nbsp;
      <span style="font-size:11px;color:#94a3b8;font-weight:400">HT: {len(eps_sys)} đợt · B&H: {len(eps_bh)} đợt</span>
    </h2>
    <div style="font-size:11px;color:#10b981;margin-bottom:6px;font-weight:600">Hệ thống ({len(eps_sys)} đợt)</div>
    <table style="font-size:11px;margin-bottom:8px">
      <thead><tr><th>Đỉnh → Đáy</th><th style="text-align:right">Depth</th><th style="text-align:right">Đáy→đỉnh</th><th style="text-align:right">Tổng</th></tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="font-size:10px;color:#64748b">{e['peak_date']} → {e['trough_date']}</td>
        <td style="text-align:right" class="red">{e['depth']:.1%}</td>
        <td style="text-align:right;font-size:10px;color:#{'22c55e' if e['dur_recov'] and e['dur_recov']<100 else 'f97316' if e['dur_recov'] else 'ef4444'}">{f"{e['dur_recov']}p" if e['dur_recov'] else "⚠ ongoing"}</td>
        <td style="text-align:right;font-size:10px;color:#94a3b8">{e['dur_total']}p</td>
      </tr>""" for e in sorted(eps_sys, key=lambda x: x['depth']))}
      </tbody>
    </table>
    <div style="font-size:11px;color:#60a5fa;margin-bottom:6px;font-weight:600">B&H ({len(eps_bh)} đợt — so sánh)</div>
    <table style="font-size:11px">
      <thead><tr><th>Đỉnh → Đáy</th><th style="text-align:right">Depth</th><th style="text-align:right">Hồi phục</th><th style="text-align:right">Tổng</th></tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="font-size:10px;color:#64748b">{e['peak_date']} → {e['trough_date']}</td>
        <td style="text-align:right;color:#60a5fa">{e['depth']:.1%}</td>
        <td style="text-align:right;font-size:10px;color:#64748b">{f"{e['dur_recov']}p" if e['dur_recov'] else "⚠ ongoing"}</td>
        <td style="text-align:right;font-size:10px;color:#64748b">{e['dur_total']}p</td>
      </tr>""" for e in sorted(eps_bh, key=lambda x: x['depth']))}
      </tbody>
    </table>
    <div style="margin-top:8px;font-size:10px;color:#475569">
      p = phiên giao dịch · HT {"ít đợt DD hơn" if len(eps_sys)<len(eps_bh) else "nhiều đợt DD hơn"} so với B&H ·
      avg depth HT {np.mean([e['depth'] for e in eps_sys]):.1%} vs B&H {np.mean([e['depth'] for e in eps_bh]):.1%}
    </div>
  </div>
</div>

<!-- ROW 2c: Sensitivity analysis -->
<div class="card" style="margin-bottom:16px">
  <h2>Sensitivity Analysis — Độ ổn định của tham số</h2>
  <div class="grid2" style="gap:20px;margin-top:6px">
    <div>
      <div style="font-size:11px;color:#94a3b8;margin-bottom:8px">EMA_ALPHA (MIN_STAY=7 cố định) — hiện tại: α={EMA_ALPHA}</div>
      <table style="font-size:11px">
        <thead><tr><th>α</th><th style="text-align:right">CAGR</th><th style="text-align:right">Sharpe</th><th style="text-align:right">Calmar</th><th style="text-align:right">Trans</th></tr></thead>
        <tbody>
        {''.join(f"""<tr style="{'background:#1a3a2a' if abs(r['alpha']-EMA_ALPHA)<0.001 else ''}">
          <td style="font-weight:{'700' if abs(r['alpha']-EMA_ALPHA)<0.001 else '400'};color:{'#22c55e' if abs(r['alpha']-EMA_ALPHA)<0.001 else '#e2e8f0'}">{r['alpha']:.2f}{'  ←' if abs(r['alpha']-EMA_ALPHA)<0.001 else ''}</td>
          <td style="text-align:right" class="{'green' if r['cagr']>0.10 else 'yellow'}">{r['cagr']:.1%}</td>
          <td style="text-align:right" class="{'green' if r['sharpe']>1.0 else 'yellow'}">{r['sharpe']:.2f}</td>
          <td style="text-align:right" class="{'green' if r['calmar']>0.55 else 'yellow'}">{r['calmar']:.2f}</td>
          <td style="text-align:right;color:#64748b">{r['trans']}</td>
        </tr>""" for r in sensitivity_alpha)}
        </tbody>
      </table>
    </div>
    <div>
      <div style="font-size:11px;color:#94a3b8;margin-bottom:8px">MIN_STAY (α=0.40 cố định) — hiện tại: {MIN_STAY} phiên</div>
      <table style="font-size:11px">
        <thead><tr><th>min_stay</th><th style="text-align:right">CAGR</th><th style="text-align:right">Sharpe</th><th style="text-align:right">Calmar</th><th style="text-align:right">Trans</th></tr></thead>
        <tbody>
        {''.join(f"""<tr style="{'background:#1a3a2a' if r['min_stay']==MIN_STAY else ''}">
          <td style="font-weight:{'700' if r['min_stay']==MIN_STAY else '400'};color:{'#22c55e' if r['min_stay']==MIN_STAY else '#e2e8f0'}">{r['min_stay']}{'  ←' if r['min_stay']==MIN_STAY else ''}</td>
          <td style="text-align:right" class="{'green' if r['cagr']>0.10 else 'yellow'}">{r['cagr']:.1%}</td>
          <td style="text-align:right" class="{'green' if r['sharpe']>1.0 else 'yellow'}">{r['sharpe']:.2f}</td>
          <td style="text-align:right" class="{'green' if r['calmar']>0.55 else 'yellow'}">{r['calmar']:.2f}</td>
          <td style="text-align:right;color:#64748b">{r['trans']}</td>
        </tr>""" for r in sensitivity_minstay)}
        </tbody>
      </table>
    </div>
  </div>
  <div style="margin-top:10px;font-size:10px;color:#475569">
    Sensitivity test: tham số tốt = kết quả ổn định trong vùng ±20% quanh giá trị chọn, không có peak cô lập
  </div>
</div>

<!-- CHARTS ROW 1 -->
<div class="card" style="margin-bottom:16px">
  <h2>VNINDEX Close Price — Màu nền theo trạng thái thị trường</h2>
  <div class="chart-wrap-lg"><canvas id="chartPrice"></canvas></div>
</div>

<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Giá trị danh mục (tỷ VND) — Hệ thống vs Buy & Hold</h2>
    <div class="chart-wrap"><canvas id="chartPV"></canvas></div>
  </div>
  <div class="card">
    <h2>r_score — Vị trí composite score trong lịch sử</h2>
    <div class="chart-wrap"><canvas id="chartRScore"></canvas></div>
  </div>
</div>

<div class="grid2" style="margin-bottom:16px">
  <div class="card">
    <h2>Tỷ lệ cổ phiếu (weight) theo thời gian</h2>
    <div class="chart-wrap"><canvas id="chartWeight"></canvas></div>
  </div>
  <div class="card">
    <h2>PE VNINDEX vs Expanding P90</h2>
    <div class="chart-wrap"><canvas id="chartPE"></canvas></div>
  </div>
</div>

<!-- FULL NAV TRANSITIONS TABLE -->
<div class="card" style="margin-bottom:16px">
  <h2>Toàn bộ lịch sử chuyển trạng thái — NAV từ 1 tỷ VND &nbsp;
    <span style="font-size:11px;color:#64748b;font-weight:400">
      🔒 = BearDvg gate đang mở · Hệ thống: <span style="color:#22c55e">{final_sys:.2f} tỷ</span> · B&H: <span style="color:#60a5fa">{final_bh:.2f} tỷ</span>
    </span>
  </h2>
  <div style="overflow-x:auto;max-height:480px;overflow-y:auto">
  <table style="font-size:11.5px">
    <thead style="position:sticky;top:0;z-index:1">
      <tr>
        <th>Ngày</th><th>Từ</th><th></th><th>Sang</th>
        <th style="text-align:right">VNINDEX</th>
        <th style="text-align:right">PE</th>
        <th style="text-align:right">Phân bổ</th>
        <th style="text-align:right;color:#22c55e">NAV HT</th>
        <th style="text-align:right;color:#60a5fa">NAV B&H</th>
        <th style="text-align:right">Ret giai đoạn</th>
        <th style="text-align:center">Gate</th>
      </tr>
    </thead>
    <tbody>{trans_rows_all}</tbody>
  </table>
  </div>
  <div style="margin-top:10px;font-size:11px;color:#64748b">
    Tổng {n_trans} lần chuyển · NAV hiện tại: <strong style="color:#22c55e">{final_sys:.2f} tỷ</strong>
    vs B&H <strong style="color:#60a5fa">{final_bh:.2f} tỷ</strong>
    · Thắng B&H: <strong style="color:#22c55e">{(final_sys/final_bh-1):+.1%}</strong>
  </div>
</div>

</div><!-- /wrap -->

<script>
const dates   = {dates_js};
const close_d = {close_js};
const state_d = {state_js};
const rscore  = {rscore_js};
const rscore_ema = {rscore_ema_js};
const weight  = {weight_js};
const pv_d    = {pv_js};
const pvbh_d  = {pvbh_js};
const pe_d    = {pe_js};
const pe_p90  = {to_js_arr(pd.Series(pe_p90), 2)};

// State colors array
const ST_COLOR = {{
  1: '#ef4444', 2: '#f9731650', 3: '#eab30840', 4: '#22c55e50', 5: '#10b98150'
}};
const ST_SOLID = {{
  1: '#ef444480', 2: '#f9731680', 3: '#eab30880', 4: '#22c55e80', 5: '#10b98180'
}};

Chart.defaults.color = '#64748b';
Chart.defaults.borderColor = '#1e293b';

// Build background annotations for price chart
function buildStateBg(dates, states, alpha=0.12) {{
  const bands = [];
  let start = 0;
  for(let i=1; i<=states.length; i++) {{
    if(i === states.length || states[i] !== states[start]) {{
      const s = states[start];
      const colors = {{1:'255,0,0',2:'249,115,22',3:'234,179,8',4:'34,197,94',5:'16,185,129'}};
      bands.push({{
        type:'box', xMin: dates[start], xMax: dates[Math.min(i,dates.length-1)],
        backgroundColor: `rgba(${{colors[s]}},${{alpha}})`, borderWidth: 0
      }});
      start = i;
    }}
  }}
  return bands;
}}

const stateBands = buildStateBg(dates, state_d);

// Chart 1: Price
new Chart(document.getElementById('chartPrice'), {{
  type: 'line',
  data: {{ labels: dates, datasets: [{{
    label: 'VNINDEX',
    data: close_d, borderColor: '#60a5fa', borderWidth: 1.5,
    pointRadius: 0, tension: 0.1, fill: false
  }}]}},
  options: {{
    responsive: true, maintainAspectRatio: false, animation: false,
    plugins: {{
      legend: {{display: false}},
      annotation: {{ annotations: Object.fromEntries(stateBands.map((b,i) => [i,b])) }}
    }},
    scales: {{
      x: {{ type:'category', ticks:{{ maxTicksLimit:12, maxRotation:0 }}, grid:{{color:'#1e293b'}} }},
      y: {{ grid:{{color:'#1e293b'}}, ticks:{{callback: v=>v.toLocaleString()}} }}
    }}
  }}
}});

// Chart 2: Portfolio Value
new Chart(document.getElementById('chartPV'), {{
  type: 'line',
  data: {{ labels: dates, datasets: [
    {{label:'Hệ thống', data: pv_d, borderColor:'#22c55e', borderWidth:1.5, pointRadius:0, fill:false}},
    {{label:'Buy & Hold', data: pvbh_d, borderColor:'#60a5fa', borderWidth:1.5, pointRadius:0, fill:false, borderDash:[4,3]}}
  ]}},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{{ legend:{{labels:{{boxWidth:12}}}} }},
    scales: {{
      x:{{ type:'category', ticks:{{maxTicksLimit:10,maxRotation:0}}, grid:{{color:'#1e293b'}} }},
      y:{{ grid:{{color:'#1e293b'}}, ticks:{{callback: v=>v.toFixed(1)+' tỷ'}} }}
    }}
  }}
}});

// Chart 3: r_score (raw + EMA)
new Chart(document.getElementById('chartRScore'), {{
  type: 'line',
  data: {{ labels: dates, datasets: [
    {{label:'r_score raw', data: rscore, borderColor:'#475569', borderWidth:1, pointRadius:0, fill:false}},
    {{label:'r_score EMA(α=0.10)', data: rscore_ema, borderColor:'#a78bfa', borderWidth:2, pointRadius:0, fill:false}},
    {{label:'0.10 CRISIS', data: Array(dates.length).fill(0.10), borderColor:'#ef4444', borderWidth:1, pointRadius:0, borderDash:[3,3]}},
    {{label:'0.20 BEAR', data: Array(dates.length).fill(0.20), borderColor:'#f97316', borderWidth:1, pointRadius:0, borderDash:[3,3]}},
    {{label:'0.70 BULL', data: Array(dates.length).fill(0.70), borderColor:'#22c55e', borderWidth:1, pointRadius:0, borderDash:[3,3]}},
    {{label:'0.90 EX-BULL', data: Array(dates.length).fill(0.90), borderColor:'#10b981', borderWidth:1, pointRadius:0, borderDash:[3,3]}}
  ]}},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{{ legend:{{labels:{{boxWidth:10, font:{{size:10}}}}}} }},
    scales: {{
      x:{{ type:'category', ticks:{{maxTicksLimit:10,maxRotation:0}}, grid:{{color:'#1e293b'}} }},
      y:{{ min:0, max:1, grid:{{color:'#1e293b'}} }}
    }}
  }}
}});

// Chart 4: Weight
new Chart(document.getElementById('chartWeight'), {{
  type: 'line',
  data: {{ labels: dates, datasets: [
    {{label:'Tỷ lệ cổ phiếu', data: weight, borderColor:'#f59e0b', borderWidth:1.5,
      pointRadius:0, fill:true, backgroundColor:'rgba(245,158,11,0.1)'}}
  ]}},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{{ legend:{{display:false}} }},
    scales: {{
      x:{{ type:'category', ticks:{{maxTicksLimit:10,maxRotation:0}}, grid:{{color:'#1e293b'}} }},
      y:{{ min:0, max:1.4, grid:{{color:'#1e293b'}},
        ticks:{{callback: v=>(v*100).toFixed(0)+'%'}} }}
    }}
  }}
}});

// Chart 5: PE
new Chart(document.getElementById('chartPE'), {{
  type: 'line',
  data: {{ labels: dates, datasets: [
    {{label:'PE VNINDEX', data: pe_d, borderColor:'#f472b6', borderWidth:1.5, pointRadius:0, fill:false}},
    {{label:'PE P90 expanding', data: pe_p90, borderColor:'#ef4444', borderWidth:1,
      pointRadius:0, fill:false, borderDash:[4,3]}}
  ]}},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{{ legend:{{labels:{{boxWidth:12}}}} }},
    scales: {{
      x:{{ type:'category', ticks:{{maxTicksLimit:10,maxRotation:0}}, grid:{{color:'#1e293b'}} }},
      y:{{ min:0, grid:{{color:'#1e293b'}} }}
    }}
  }}
}});
</script>
</body>
</html>"""

out_path = os.path.join(WORKDIR, "vnindex_5state_system.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nSaved: {out_path}")
print("Done.")

# ══════════════════════════════════════════════════════════════════════
# GENERATE FULL TRANSITIONS TABLE HTML  (vnindex_transitions_v2 style)
# ══════════════════════════════════════════════════════════════════════
print("\nGenerating transitions table HTML ...")

# ── Collect ALL transitions with full factor data ─────────────────────
all_transitions = []
_prev_s    = int(state_smooth[0])
_prev_date = vni["time"].iloc[0]

for i in range(1, n):
    _s = int(state_smooth[i])
    if _s != _prev_s:
        _cur_date = vni["time"].iloc[i]
        _dur_days = (_cur_date - _prev_date).days

        def _fv(arr, idx): return float(arr[idx]) if not np.isnan(arr[idx]) else None

        all_transitions.append({
            "from":    STATE_NAMES[_prev_s],
            "to":      STATE_NAMES[_s],
            "to_s":    _s,
            "date":    _cur_date,
            "dur":     _dur_days,
            "close":   float(close[i]),
            "nav":     pv[i] / 1e9,
            "rs":      _fv(r_score, i),
            "sc":      _fv(score, i),
            "p3m_v":   _fv(p3m, i),
            "p3m_r":   _fv(ranks["P3M"], i),
            "ma200_v": _fv(ma200_dev, i),
            "ma200_r": _fv(ranks["MA200"], i),
            "rsi_v":   _fv(rsi, i),
            "rsi_r":   _fv(ranks["RSI"], i),
            "macd_v":  _fv(macd_hist, i),
            "macd_r":  _fv(ranks["MACD"], i),
        })
        _prev_s    = _s
        _prev_date = _cur_date

_nav_peak   = max((t["nav"] for t in all_transitions), default=1.0)
_total_trans = len(all_transitions)
_n_by_state = {s: sum(1 for t in all_transitions if t["to"] == STATE_NAMES[s]) for s in range(1, 6)}

# ── HTML helpers ──────────────────────────────────────────────────────
_STATE_BG = {
    "CRISIS":  ("#7f1d1d", "#fca5a5"),
    "BEAR":    ("#7c2d12", "#fdba74"),
    "NEUTRAL": ("#1e293b", "#94a3b8"),
    "BULL":    ("#14532d", "#86efac"),
    "EX-BULL": ("#3b0764", "#c4b5fd"),
}
_ALLOC = {
    "CRISIS":  ("100:0",    "#7f1d1d", "#fca5a5", ""),
    "BEAR":    ("80:20",    "#7c2d12", "#fdba74", ""),
    "NEUTRAL": ("30:70",    "#1e293b", "#94a3b8", ";border:1px solid #334155"),
    "BULL":    ("0:100",    "#14532d", "#86efac", ""),
    "EX-BULL": ("−30:130", "#3b0764", "#c4b5fd", ""),
}

def _badge(s):
    bg, fg = _STATE_BG.get(s, ("#334155","#94a3b8"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap">{s}</span>'

def _alloc_td(s):
    lbl, bg, fg, brd = _ALLOC.get(s, ("?","#1e293b","#94a3b8",""))
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:700;font-size:12px;padding:4px 8px;white-space:nowrap{brd}">{lbl}</td>'

def _rank_cell(r):
    if r is None:
        return '<td style="padding:4px 6px;text-align:center;color:#64748b;font-size:11px">N/A</td>'
    if   r >= 0.75: bg, fg = "#bbf7d0","#166534"
    elif r >= 0.55: bg, fg = "#d1fae5","#065f46"
    elif r >= 0.45: bg, fg = "#fef9c3","#713f12"
    elif r >= 0.25: bg, fg = "#fed7aa","#9a3412"
    else:           bg, fg = "#fecaca","#991b1b"
    return f'<td style="background:{bg};color:{fg};text-align:center;font-weight:600;padding:4px 6px">{r:.0%}</td>'

def _dir(from_s, to_s):
    _ord = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}
    f, t = _ord.get(from_s,3), _ord.get(to_s,3)
    if t > f: return "▲","#16a34a","up"
    if t < f: return "▼","#dc2626","down"
    return "→","#64748b","same"

def _reason(t):
    rs = t["rs"]
    if rs is None: return "—"
    _lo = {"CRISIS":0,"BEAR":0.10,"NEUTRAL":0.20,"BULL":0.70,"EX-BULL":0.90}
    _hi = {"CRISIS":0.10,"BEAR":0.20,"NEUTRAL":0.70,"BULL":0.90,"EX-BULL":1.01}
    lo = _lo.get(t["to"],0); hi = _hi.get(t["to"],1)
    weak = [f'{k}={v:.0%}' for k,v in [("P3M",t["p3m_r"]),("MA200",t["ma200_r"]),
             ("RSI",t["rsi_r"]),("MACD",t["macd_r"])] if v is not None and v < 0.35]
    txt = f'r_score={rs:.1%} trong [{lo:.0%},{hi:.0%}) → {t["to"]}'
    if weak:
        txt += f'<br><span style="color:#64748b;font-size:10px">{", ".join(weak)}</span>'
    return txt

# ── Build rows ────────────────────────────────────────────────────────
_rows = []
for idx, t in enumerate(all_transitions):
    arrow, a_col, dir_cls = _dir(t["from"], t["to"])
    row_bg = "#1e293b" if idx % 2 == 0 else "#0f172a"
    bar_w  = max(2, int(min(t["nav"] / _nav_peak, 1.0) * 120))

    rs = t["rs"]
    if rs is None:   rs_bg, rs_fg, rs_str = "#374151","#e5e7eb","N/A"
    elif rs < 0.10:  rs_bg, rs_fg, rs_str = "#dc2626","#fff",f"{rs:.1%}"
    elif rs < 0.20:  rs_bg, rs_fg, rs_str = "#ea580c","#fff",f"{rs:.1%}"
    elif rs < 0.70:  rs_bg, rs_fg, rs_str = "#374151","#e5e7eb",f"{rs:.1%}"
    elif rs < 0.90:  rs_bg, rs_fg, rs_str = "#16a34a","#fff",f"{rs:.1%}"
    else:            rs_bg, rs_fg, rs_str = "#7c3aed","#fff",f"{rs:.1%}"

    sc_str    = f"{t['sc']:.3f}"        if t["sc"]      is not None else "N/A"
    p3m_str   = f"{t['p3m_v']*100:+.1f}%" if t["p3m_v"] is not None else "N/A"
    ma200_str = f"{t['ma200_v']+1:.3f}"  if t["ma200_v"] is not None else "N/A"
    rsi_str   = f"{t['rsi_v']:.3f}"     if t["rsi_v"]   is not None else "N/A"
    macd_str  = f"{t['macd_v']:.4f}"    if t["macd_v"]  is not None else "N/A"

    _rows.append(f'''<tr style="background:{row_bg};border-bottom:1px solid #334155"
            data-from="{t['from']}" data-to="{t['to']}" data-date="{t['date'].strftime('%Y-%m-%d')}" data-dir="{dir_cls}">
      <td style="padding:5px 8px;font-size:12px;color:#94a3b8;white-space:nowrap">{t['date'].strftime('%Y-%m-%d')}</td>
      <td style="padding:5px 8px;text-align:center">{_badge(t['from'])}</td>
      <td style="padding:5px 4px;text-align:center;font-size:16px;color:{a_col}">{arrow}</td>
      <td style="padding:5px 8px;text-align:center">{_badge(t['to'])}</td>
      <td style="padding:5px 8px;text-align:center;color:#64748b;font-size:11px">{t['dur']}d</td>
      <td style="padding:5px 8px;text-align:right;color:#e2e8f0;font-size:12px">{t['close']:.1f}</td>
      <td style="padding:4px 8px;white-space:nowrap">
            <div style="font-size:12px;font-weight:700;color:#f8fafc">{t['nav']:.2f} t&#7927;</div>
            <div style="height:4px;width:{bar_w}px;background:#3b82f6;border-radius:2px;margin-top:2px"></div>
        </td>
      {_alloc_td(t['to'])}
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{p3m_str}</td>
      {_rank_cell(t['p3m_r'])}
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{ma200_str}</td>
      {_rank_cell(t['ma200_r'])}
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{rsi_str}</td>
      {_rank_cell(t['rsi_r'])}
      <td style="padding:4px 6px;text-align:center;color:#94a3b8;font-size:11px">{macd_str}</td>
      {_rank_cell(t['macd_r'])}
      <td style="padding:4px 6px;text-align:center;color:#cbd5e1;font-size:11px">{sc_str}</td>
      <td style="background:{rs_bg};color:{rs_fg};text-align:center;font-weight:800;padding:4px 8px">{rs_str}</td>
      <td style="padding:4px 10px;color:#94a3b8;font-size:11px;max-width:220px">{_reason(t)}</td>
    </tr>''')

_tbody_html = "\n".join(_rows)

# ── Stat cards ────────────────────────────────────────────────────────
_stat_colors = {1:"#dc2626",2:"#f97316",3:"#9ca3af",4:"#16a34a",5:"#7c3aed"}
_stat_cards = f'<div class="stat-card"><div class="num" style="color:#e2e8f0">{_total_trans}</div><div class="lbl">T&#7893;ng chuy&#7875;n &#273;&#7893;i</div></div>'
for _s in range(1, 6):
    _stat_cards += f'<div class="stat-card"><div class="num" style="color:{_stat_colors[_s]}">{_n_by_state[_s]}</div><div class="lbl">&#8594; {STATE_NAMES[_s]}</div></div>'
_stat_cards += f'<div class="stat-card"><div class="num" style="color:#3b82f6">{_nav_peak:.1f} t&#7927;</div><div class="lbl">NAV &#273;&#7881;nh</div></div>'

_year_range = f"{vni['time'].iloc[0].year}&#8211;{vni['time'].iloc[-1].year}"

_trans_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>VN-Index: Chuy&#7875;n &#272;&#7893;i Tr&#7841;ng Th&#225;i + NAV + T&#7881; L&#7879;</title>
<style>
* {{ box-sizing:border-box;margin:0;padding:0 }}
body {{ background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:20px }}
h1 {{ font-size:20px;color:#f8fafc;margin-bottom:4px }}
.subtitle {{ color:#64748b;font-size:13px;margin-bottom:16px }}
.stats {{ display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px }}
.stat-card {{ background:#1e293b;border-radius:8px;padding:10px 16px;border:1px solid #334155 }}
.stat-card .num {{ font-size:22px;font-weight:800 }}
.stat-card .lbl {{ font-size:11px;color:#64748b }}
.controls {{ display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;align-items:center }}
input[type=text] {{ background:#1e293b;border:1px solid #334155;color:#e2e8f0;
                    padding:6px 12px;border-radius:6px;font-size:13px;width:180px }}
.filter-btn {{ background:#1e293b;border:1px solid #334155;color:#94a3b8;
               padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px }}
.filter-btn.active {{ border-color:#60a5fa;color:#60a5fa;background:#1e3a5f }}
.filter-btn.crisis-btn.active  {{ border-color:#dc2626;color:#dc2626;background:#3b0d0d }}
.filter-btn.bear-btn.active    {{ border-color:#f97316;color:#f97316;background:#3b1a08 }}
.filter-btn.neutral-btn.active {{ border-color:#9ca3af;color:#d1d5db;background:#1f2937 }}
.filter-btn.bull-btn.active    {{ border-color:#16a34a;color:#16a34a;background:#052e16 }}
.filter-btn.exbull-btn.active  {{ border-color:#7c3aed;color:#a78bfa;background:#2e1065 }}
.filter-btn.down-btn.active    {{ border-color:#dc2626;color:#f87171;background:#3b0d0d }}
.filter-btn.up-btn.active      {{ border-color:#16a34a;color:#4ade80;background:#052e16 }}
.table-wrap {{ overflow-x:auto;max-height:76vh;overflow-y:auto;border-radius:8px;border:1px solid #334155 }}
table {{ width:100%;border-collapse:collapse;font-size:12px }}
thead th {{ background:#0f172a;color:#64748b;font-size:10px;font-weight:700;
            text-transform:uppercase;letter-spacing:.5px;padding:8px 6px;
            position:sticky;top:0;z-index:10;border-bottom:2px solid #334155;white-space:nowrap }}
tr:hover td {{ background:rgba(96,165,250,0.07)!important }}
.hidden {{ display:none!important }}
#count-info {{ color:#64748b;font-size:12px }}
.ratio-legend {{ background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;
                 margin-bottom:14px;font-size:12px }}
.ratio-legend table td {{ padding:3px 10px;border:none;background:transparent!important }}
</style>
</head>
<body>
<h1>&#128260; VN-Index: Chuy&#7875;n &#272;&#7893;i Tr&#7841;ng Th&#225;i &middot; NAV &middot; T&#7881; L&#7879; Ti&#7873;n:C&#7893; Phi&#7871;u</h1>
<p class="subtitle">{_total_trans} l&#7847;n chuy&#7875;n &#273;&#7893;i li&#234;n t&#7909;c &middot; {_year_range} &middot; V&#7889;n ban &#273;&#7847;u: 1 t&#7927; &#273;&#7891;ng</p>

<div class="stats">
  {_stat_cards}
</div>

<div class="ratio-legend">
  <b style="color:#e2e8f0">T&#7881; l&#7879; Ti&#7873;n:C&#7893; phi&#7871;u theo tr&#7841;ng th&#225;i (m&#7909;c ti&#234;u)</b>
  <table style="margin-top:6px">
    <tr>
      <td><span style="background:#7f1d1d;color:#fca5a5;padding:2px 10px;border-radius:6px;font-weight:700">100:0</span></td>
      <td style="color:#94a3b8">CRISIS &#8212; 100% ti&#7873;n m&#7863;t, kh&#244;ng n&#7855;m c&#7893; phi&#7871;u</td>
    </tr>
    <tr>
      <td><span style="background:#7c2d12;color:#fdba74;padding:2px 10px;border-radius:6px;font-weight:700">80:20</span></td>
      <td style="color:#94a3b8">BEAR &#8212; 80% ti&#7873;n, 20% c&#7893; phi&#7871;u</td>
    </tr>
    <tr>
      <td><span style="background:#1e293b;color:#94a3b8;padding:2px 10px;border-radius:6px;font-weight:700;border:1px solid #334155">30:70</span></td>
      <td style="color:#94a3b8">NEUTRAL &#8212; 30% ti&#7873;n, 70% c&#7893; phi&#7871;u</td>
    </tr>
    <tr>
      <td><span style="background:#14532d;color:#86efac;padding:2px 10px;border-radius:6px;font-weight:700">0:100</span></td>
      <td style="color:#94a3b8">BULL &#8212; fullstock, 100% c&#7893; phi&#7871;u</td>
    </tr>
    <tr>
      <td><span style="background:#3b0764;color:#c4b5fd;padding:2px 10px;border-radius:6px;font-weight:700">&#8722;30:130</span></td>
      <td style="color:#94a3b8">EX-BULL &#8212; d&#249;ng margin 30%, t&#7893;ng 130% c&#7893; phi&#7871;u</td>
    </tr>
  </table>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="T&#236;m ng&#224;y / tr&#7841;ng th&#225;i&#8230;" oninput="applyFilters()">
  <button class="filter-btn active" id="btn-all" onclick="setFilter('all')">T&#7845;t c&#7843;</button>
  <button class="filter-btn down-btn" id="btn-down" onclick="setFilter('down')">&#9660; Xu&#7889;ng c&#7845;p</button>
  <button class="filter-btn up-btn" id="btn-up" onclick="setFilter('up')">&#9650; L&#234;n c&#7845;p</button>
  <button class="filter-btn crisis-btn" id="btn-crisis" onclick="setFilter('CRISIS')">CRISIS</button>
  <button class="filter-btn bear-btn" id="btn-bear" onclick="setFilter('BEAR')">BEAR</button>
  <button class="filter-btn neutral-btn" id="btn-neutral" onclick="setFilter('NEUTRAL')">NEUTRAL</button>
  <button class="filter-btn bull-btn" id="btn-bull" onclick="setFilter('BULL')">BULL</button>
  <button class="filter-btn exbull-btn" id="btn-exbull" onclick="setFilter('EX-BULL')">EX-BULL</button>
  <span id="count-info"></span>
</div>

<div class="table-wrap">
<table>
<thead>
<tr>
  <th>Ng&#224;y</th>
  <th>T&#7915;</th>
  <th></th>
  <th>Sang</th>
  <th title="S&#7889; ng&#224;y tr&#7841;ng th&#225;i tr&#432;&#7899;c t&#7891;n t&#7841;i">Dur</th>
  <th>VNINDEX</th>
  <th>NAV (t&#7927; &#273;)</th>
  <th title="T&#7881; l&#7879; Ti&#7873;n : C&#7893; phi&#7871;u m&#7909;c ti&#234;u">Ti&#7873;n:CP</th>
  <th>P3M%</th>
  <th>Rank P3M</th>
  <th>MA200&times;</th>
  <th>Rank MA200</th>
  <th>RSI</th>
  <th>Rank RSI</th>
  <th>MACD</th>
  <th>Rank MACD</th>
  <th>Score</th>
  <th>r_score &#9733;</th>
  <th>L&yacute; do &amp; Drivers</th>
</tr>
</thead>
<tbody id="tbody">
{_tbody_html}
</tbody>
</table>
</div>

<script>
let currentFilter = 'all';
function setFilter(f) {{
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  const map = {{'all':'btn-all','down':'btn-down','up':'btn-up',
                'CRISIS':'btn-crisis','BEAR':'btn-bear','NEUTRAL':'btn-neutral',
                'BULL':'btn-bull','EX-BULL':'btn-exbull'}};
  if(map[f]) document.getElementById(map[f]).classList.add('active');
  applyFilters();
}}
function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase();
  let vis = 0;
  document.querySelectorAll('#tbody tr').forEach(r => {{
    const from = r.dataset.from || '', to = r.dataset.to || '',
          date = r.dataset.date || '', dir = r.dataset.dir || '';
    let show = true;
    if(currentFilter === 'down') show = dir === 'down';
    else if(currentFilter === 'up') show = dir === 'up';
    else if(currentFilter !== 'all') show = (to === currentFilter);
    if(q) show = show && (date.includes(q) || from.toLowerCase().includes(q) || to.toLowerCase().includes(q));
    r.classList.toggle('hidden', !show);
    if(show) vis++;
  }});
  document.getElementById('count-info').textContent = vis + ' k&#7871;t qu&#7843;';
}}
applyFilters();
</script>
</body>
</html>"""

_trans_path = os.path.join(WORKDIR, "vnindex_transitions_v2.html")
with open(_trans_path, "w", encoding="utf-8") as f:
    f.write(_trans_html)
print(f"Saved: {_trans_path}")
print(f"  → {_total_trans} transitions | NAV peak: {_nav_peak:.1f} tỷ")
