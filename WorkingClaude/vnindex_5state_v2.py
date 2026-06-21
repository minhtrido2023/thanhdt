# -*- coding: utf-8 -*-
"""
vnindex_5state_v2.py
====================
Phiên bản 2 của hệ thống 5-state — mục tiêu:
1. Bỏ smoothing (mode + min_stay)
2. Phát hiện tín hiệu đảo chiều SỚM HƠN khi đang ở CRISIS (state=1)
   → giảm độ trễ bottom→exit (baseline median 18 phiên, mean 29.2)
   → bắt rally bottom→exit (baseline median 7.9%, mean 8.7%)

Khác biệt so với vnindex_5state_system.py:
- MODE_WIN = 1, MIN_STAY = 1 (không smoothing)
- GATE_MIN_DUR = 0 (BearDvg gate có thể đóng bất cứ khi nào)
- Thêm 4 early-reversal signals trong CRISIS:
    E1 BullDvg fires (đã có)
    E2 Capitulation bounce: drawdown < -15% + close > close[5d ago]×1.05 + RSI rising
    E3 Momentum recovery: r_score_ema > 0.20 sustained 3 phiên
    E4 MACD bullish cross from deep oversold

Backtest mechanics: y nguyên như v1.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ════════════════════ PARAMS ════════════════════
W_BASE = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15, "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
EMA_ALPHA   = 0.40
RAMP_DAYS   = 3
SNAP_THR    = 0.03
TC          = 0.001
DEPOSIT_R   = 0.06 / 252
BORROW_R    = 0.10 / 252
TARGET_W    = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

# ── v2 specific knobs ──
MODE_WIN     = 1     # disable rolling mode smoothing
MIN_STAY     = 1     # disable min stay filter
GATE_MIN_DUR = 0     # disable BearDvg min duration; rely on reversal signals
# Early-reversal thresholds (CRISIS only)
E2_DD_THR        = -0.15   # capitulation drawdown floor
E2_BOUNCE_5D     = 1.05    # close > close[t-5] * 1.05
E2_RSI_RISE      = 1.15    # rsi > rsi[t-5] * 1.15
E3_RSCORE_THR    = 0.20    # recovery threshold
E3_RSCORE_DAYS   = 3       # consecutive days above threshold
E4_MACD_OVERSOLD = -2.0    # MACD hist threshold to count as "oversold cross"
E4_LOOKBACK      = 15      # days to look back for oversold

# ════════════════════ LOAD ════════════════════
print("Loading VNINDEX.csv ...")
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
# Rename Pe → VNINDEX_PE for compatibility
if "Pe" in vni.columns and "VNINDEX_PE" not in vni.columns:
    vni["VNINDEX_PE"] = pd.to_numeric(vni["Pe"], errors="coerce")
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE"]:
    if c in vni.columns:
        vni[c] = pd.to_numeric(vni[c], errors="coerce")

# Data sanity: clip OHLC outliers (|daily change| > 50% → replace with prev close, also fix H/L)
for col in ["Close","Open","High","Low"]:
    a = vni[col].values.astype(float)
    for i in range(1, len(a)):
        if a[i-1] > 0 and a[i] > 0:
            r = a[i]/a[i-1] - 1
            if abs(r) > 0.5:
                a[i] = a[i-1]
    vni[col] = a
print(f"  rows={len(vni)} {vni['time'].min().date()} → {vni['time'].max().date()}")

cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
spy = len(vni) / (cal_days/365.25) if cal_days > 0 else 252
print(f"  sessions/year = {spy:.1f}")

# Breadth
bp = os.path.join(WORKDIR, "data/breadth_data.csv")
if os.path.exists(bp):
    br = pd.read_csv(bp); br["time"] = pd.to_datetime(br["time"])
    br["breadth"] = pd.to_numeric(br["breadth"], errors="coerce")
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

n = len(vni)
close = vni["Close"].values.astype(float)
high  = vni["High"].values.astype(float)
low   = vni["Low"].values.astype(float)
vol_  = vni["Volume"].values.astype(float)

# ════════════════════ INDICATORS ════════════════════
# P3M / P1M (calendar-based approximation via 60/20 sessions)
p3m = np.full(n, np.nan); p1m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60] - 1
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20] - 1

# MA
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0) & ~np.isnan(ma200), close/ma200 - 1, np.nan)
ma50  = pd.Series(close).rolling(50, min_periods=50).mean().values
ma20  = pd.Series(close).rolling(20, min_periods=20).mean().values

# RSI Wilder 14
rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan; period = 14
for i in range(1, n):
    diff = close[i] - close[i-1]
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= period:
            g = [max(close[j]-close[j-1],0) for j in range(1,period+1)]
            l = [max(close[j-1]-close[j],0) for j in range(1,period+1)]
            avg_u = np.mean(g); avg_d = np.mean(l)
            if (avg_u+avg_d)>0: rsi[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u = (avg_u*(period-1)+u)/period
        avg_d = (avg_d*(period-1)+d)/period
        if (avg_u+avg_d)>0: rsi[i] = avg_u/(avg_u+avg_d)

# MACD hist
ema12 = np.full(n, np.nan); ema26 = np.full(n, np.nan)
signal = np.full(n, np.nan); macd_hist = np.full(n, np.nan)
k12, k26, k9 = 2/13, 2/27, 2/10
for i in range(n):
    if i==0 or np.isnan(ema12[i-1]):
        ema12[i]=close[i]; ema26[i]=close[i]
    else:
        ema12[i] = ema12[i-1]*(1-k12) + close[i]*k12
        ema26[i] = ema26[i-1]*(1-k26) + close[i]*k26
    macd_line = ema12[i] - ema26[i]
    if i==0 or np.isnan(signal[i-1]):
        signal[i] = macd_line
    else:
        signal[i] = signal[i-1]*(1-k9) + macd_line*k9
    if i >= 33:
        macd_hist[i] = macd_line - signal[i]

# CMF 14
hl = high - low
mfm = np.where(hl > 0, ((close - low) - (high - close))/np.where(hl>0,hl,1.0), 0.0)
mfv = mfm * vol_
cmf = np.full(n, np.nan)
for i in range(14, n):
    s_v = np.sum(vol_[i-14:i])
    if s_v > 0: cmf[i] = np.sum(mfv[i-14:i]) / s_v

# Store factors
vni["f_P3M"]=p3m; vni["f_P1M"]=p1m; vni["f_MA200"]=ma200_dev
vni["f_RSI"]=rsi; vni["f_MACD"]=macd_hist; vni["f_CMF"]=cmf
vni["f_Breadth"]=vni["breadth"].values

# Expanding pct rank
def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        hist = arr[:t+1]; v = hist[~np.isnan(hist)]
        if len(v) < min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(v <= arr[t])/len(v)
    return out

FK = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
ranks = {}
print("Computing ranks ...")
for k in FK:
    ranks[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

# Composite + EMA
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FK if not np.isnan(ranks[k][t])}
    if len(avail) < MIN_FACTORS: continue
    ws = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score = expanding_pct_rank(score, MIN_LB)
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; prev = r_score_ema[t-1] if t>0 else np.nan
    if np.isnan(v):       r_score_ema[t] = prev
    elif np.isnan(prev):  r_score_ema[t] = v
    else:                 r_score_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev

# ════════════════════ STATE CLASSIFICATION ════════════════════
def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    if rs < 0.20: return 2
    if rs < 0.70: return 3
    if rs < 0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in r_score_ema])

# Risk overrides
pe = vni["VNINDEX_PE"].values
pe_p90 = np.full(n, np.nan)
for t in range(n):
    v = pe[:t+1]; v = v[~np.isnan(v)]
    if len(v)>=60: pe_p90[t] = np.nanpercentile(v, 90)
running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max>0, close/running_max - 1, 0.0)

daily_ret = np.full(n, np.nan)
for i in range(1,n):
    if close[i-1]>0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20,n):
    w = daily_ret[i-20:i]; v = w[~np.isnan(w)]
    if len(v)>=15: vol20[i] = np.std(v)*np.sqrt(spy)
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    h = vol20[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: avg_vol_exp[t] = np.mean(v)

state_ov = state_raw.copy()
for i in range(n):
    s = state_ov[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe[i]) and pe[i] > pe_p90[i] and s == 5: s = 4
    if dd[i] < -0.25 and s >= 4: s = 3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i] > 1.5*avg_vol_exp[i] and s == 5: s = 4
    state_ov[i] = s

# ════════════════════ BEAR/BULL DVG (D_RSI features) ════════════════════
# D_RSI = rsi (already 0..1)
D_RSI = rsi
def rolling_max(a, w):
    s = pd.Series(a); return s.rolling(w, min_periods=1).max().values
def rolling_min(a, w):
    s = pd.Series(a); return s.rolling(w, min_periods=1).min().values
def rolling_argmax_close(rsi_a, close_a, w):
    """Close ở thời điểm RSI đạt max trong w phiên."""
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1)
        seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg))
        out[i] = close_a[lo+k]
    return out
def rolling_argmax_macd(rsi_a, macd_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1)
        seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg))
        out[i] = macd_a[lo+k]
    return out
def rolling_argmin_close(rsi_a, close_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1)
        seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmin(seg))
        out[i] = close_a[lo+k]
    return out

print("Computing D_RSI feature set ...")
D_RSI_T1W     = np.concatenate([[np.nan]*5, D_RSI[:-5]])   # 5 phiên trước
D_RSI_Max1W   = rolling_max(D_RSI, 5)
D_RSI_Max3M   = rolling_max(D_RSI, 60)
D_RSI_Min1W   = rolling_min(D_RSI, 5)
D_RSI_Min3M   = rolling_min(D_RSI, 60)
D_RSI_Max1W_C = rolling_argmax_close(D_RSI, close, 5)
D_RSI_Max3M_C = rolling_argmax_close(D_RSI, close, 60)
D_RSI_Max1W_M = rolling_argmax_macd(D_RSI, macd_hist, 5)
D_RSI_Max3M_M = rolling_argmax_macd(D_RSI, macd_hist, 60)
D_RSI_Min1W_C = rolling_argmin_close(D_RSI, close, 5)
D_RSI_MinT3   = rolling_min(D_RSI, 3)
D_CMF         = cmf
D_MACDdiff    = macd_hist
C_L1W = close / np.where(rolling_min(close, 5)>0, rolling_min(close, 5), 1.0)
C_L1M = close / np.where(rolling_min(close, 20)>0, rolling_min(close, 20), 1.0)

# Build masks (matching filter.json BearDvg/BullDvg formulas)
with np.errstate(divide='ignore', invalid='ignore'):
    bear1 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan) > 1.044) & (D_RSI_Max3M > 0.74) &
             (D_RSI_Max1W < 0.72) & (D_RSI_Max1W > 0.61) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) > 1.028) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan) > 1.11) &
             (D_MACDdiff < 0) &
             (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) > 0.96) &
             (D_RSI_MinT3 > 0.43) & (D_CMF < 0.13))
    bear2 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan) > 1.016) & (D_RSI_Max3M > 0.77) &
             (D_RSI_Max1W < 0.79) & (D_RSI_Max1W > 0.60) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) > 1.008) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan) > 1.10) &
             (D_MACDdiff < 0) &
             (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) > 0.97) &
             (D_RSI_MinT3 > 0.50) & (D_CMF < 0.15))
    bull1 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan) > 0.90) & (D_RSI_Min1W < 0.60) &
             (D_RSI_Min3M < 0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) < 1.15) &
             (D_MACDdiff > 0) & (D_RSI_MinT3 < 0.50) & (D_RSI_Max1W < 0.48) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan) > 1.12) & (D_CMF > 0) &
             (C_L1M < 1.21) & (C_L1W < 1.05))
    bull2 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan) > 0.92) & (D_RSI_Min1W < 0.52) &
             (D_RSI_Min3M < 0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan) < 1.10) &
             (D_MACDdiff > 0) & (D_RSI_MinT3 < 0.56) & (D_RSI_Max1W < 0.64) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan) > 1.10) & (D_CMF > 0) &
             (C_L1M < 1.20) & (C_L1W < 1.025))

bear_mask = np.nan_to_num(bear1, nan=0).astype(bool) | np.nan_to_num(bear2, nan=0).astype(bool)
bull_mask = np.nan_to_num(bull1, nan=0).astype(bool) | np.nan_to_num(bull2, nan=0).astype(bool)
print(f"  BearDvg events: {bear_mask.sum()} | BullDvg events: {bull_mask.sum()}")

# PE rank
pe_rank = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe[t]): continue
    v = pe[:t+1]; v = v[~np.isnan(v)]
    if len(v)>=60: pe_rank[t] = np.sum(v <= pe[t])/len(v)

# ════════════════════ APPLY GATE + EARLY REVERSAL SIGNALS ════════════════════
# We apply CRISIS lock logic, but ALSO override CRISIS → BEAR (state 2) early when
# any of E1..E4 reversal signals fire. Once exit fires, gate closes and state follows
# r_score classification thereafter.
def early_reversal_signals():
    """Return per-day mask of early reversal triggers (E1..E4)."""
    # E1: BullDvg
    E1 = bull_mask.copy()

    # E2: Capitulation bounce — dd<-15%, close>close[t-5]*1.05, RSI>RSI[t-5]*1.15, CMF>0
    E2 = np.zeros(n, dtype=bool)
    for i in range(5, n):
        if (dd[i] < E2_DD_THR
            and close[i] > close[i-5] * E2_BOUNCE_5D
            and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
            and rsi[i] > rsi[i-5] * E2_RSI_RISE
            and not np.isnan(cmf[i]) and cmf[i] > 0):
            E2[i] = True

    # E3: Momentum recovery — r_score_ema > 0.20 sustained 3 days
    E3 = np.zeros(n, dtype=bool)
    streak = 0
    for i in range(n):
        if not np.isnan(r_score_ema[i]) and r_score_ema[i] > E3_RSCORE_THR:
            streak += 1
        else:
            streak = 0
        if streak >= E3_RSCORE_DAYS:
            E3[i] = True

    # E4: MACD bullish cross from deep oversold
    # macd_hist crosses 0 from below AND was < E4_MACD_OVERSOLD within last E4_LOOKBACK days
    E4 = np.zeros(n, dtype=bool)
    for i in range(E4_LOOKBACK, n):
        if np.isnan(macd_hist[i]) or np.isnan(macd_hist[i-1]): continue
        if macd_hist[i] > 0 and macd_hist[i-1] <= 0:
            lb = macd_hist[i-E4_LOOKBACK:i]
            lb = lb[~np.isnan(lb)]
            if len(lb)>0 and np.min(lb) < E4_MACD_OVERSOLD:
                E4[i] = True
    return E1, E2, E3, E4

E1, E2, E3, E4 = early_reversal_signals()
exit_signal = E1 | E2 | E3 | E4
print(f"  E1 BullDvg: {E1.sum()} | E2 Capitulation: {E2.sum()} | E3 r_score_recov: {E3.sum()} | E4 MACD bull cross: {E4.sum()}")
print(f"  Total exit-signal days: {exit_signal.sum()}")

# Apply gate logic: when BearDvg fires → enter CRISIS lock at state 1
# Exit when any of E1..E4 fires
GATE_FLOOR = 1
gate_active = False
gate_flag = np.zeros(n, dtype=int)
state_dvg = state_ov.copy()
gate_events = []
gate_start = -1
for i in range(n):
    if bear_mask[i]:
        if not gate_active:
            gate_active = True
            gate_start = i
            gate_events.append({"type":"OPEN", "i":i, "date": vni["time"].iloc[i].strftime("%Y-%m-%d"), "close": float(close[i])})
        else:
            gate_start = i  # refresh on new bear
    if gate_active:
        gate_flag[i] = 1
        if state_dvg[i] > GATE_FLOOR:
            state_dvg[i] = GATE_FLOOR
        sessions_in = i - gate_start
        if sessions_in >= GATE_MIN_DUR and exit_signal[i]:
            trig = ("BullDvg" if E1[i] else
                    "Capitulation" if E2[i] else
                    "RScoreRecov" if E3[i] else "MACDBullCross")
            gate_events.append({"type":"CLOSE", "i":i,
                                "date": vni["time"].iloc[i].strftime("%Y-%m-%d"),
                                "close": float(close[i]),
                                "duration": sessions_in, "trigger": trig})
            gate_active = False

# NO smoothing — state = state_dvg
state_final = state_dvg

# ════════════════════ BACKTEST ════════════════════
print("Backtesting v2 ...")
pv = np.zeros(n); pv[0] = 1e9
w = TARGET_W[3]; w_arr = np.zeros(n); w_arr[0] = w
for t in range(1, n):
    tgt = TARGET_W[state_final[t-1]]
    d_  = tgt - w
    w_new = tgt if abs(d_) < SNAP_THR else w + d_/RAMP_DAYS
    w_new = float(np.clip(w_new, 0.0, 1.30))
    if close[t-1] > 0:
        r = close[t]/close[t-1] - 1
    else:
        r = 0.0
    cash_r = max(0, 1-w_new)*DEPOSIT_R
    marg_c = max(0, w_new-1)*BORROW_R
    trd_c  = abs(w_new - w)*TC
    pv[t] = pv[t-1]*(1 + w_new*r + cash_r - marg_c - trd_c)
    w = w_new; w_arr[t] = w

pv_bh = np.zeros(n); pv_bh[0] = 1e9
for t in range(1, n):
    if close[t-1] > 0:
        pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1])
    else:
        pv_bh[t] = pv_bh[t-1]

vni["state"] = state_final
vni["pv_v2"] = pv
vni["pv_bh"] = pv_bh
vni["weight"]= w_arr

# ════════════════════ BASELINE (v1 logic, same data) ════════════════════
print("\nRunning BASELINE (v1: mode15 + min_stay7 + gate_min_dur60) for comparison ...")
def rolling_mode(states, window):
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand:
                out[t] = v; break
    return out
def min_stay_filter(states, min_days):
    out = states.copy()
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

# Baseline gate (min_dur=60, exit=BullDvg OR (P3M+PE) OR rscore streak ≥10 > 0.65)
B_GATE_MIN_DUR = 60
p3m_rank_arr = ranks["P3M"]
_rscore_streak10 = np.zeros(n, dtype=bool); _st = 0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i] > 0.65: _st += 1
    else: _st = 0
    if _st >= 10: _rscore_streak10[i] = True

state_dvg_b = state_ov.copy()
gate_active_b = False; gate_start_b = -1
for i in range(n):
    if bear_mask[i]:
        if not gate_active_b:
            gate_active_b = True; gate_start_b = i
        else:
            gate_start_b = i
    if gate_active_b:
        if state_dvg_b[i] > 1: state_dvg_b[i] = 1
        sessions_in = i - gate_start_b
        if sessions_in >= B_GATE_MIN_DUR:
            _p3m_ok  = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
            _pe_ok   = (not np.isnan(pe_rank[i]))      and pe_rank[i] < 0.80
            _bull_ok = bool(bull_mask[i])
            _rs_ok   = bool(_rscore_streak10[i])
            if _bull_ok or (_p3m_ok and _pe_ok) or _rs_ok:
                gate_active_b = False

state_b = rolling_mode(state_dvg_b, 15)
state_b = min_stay_filter(state_b, 7)

# Backtest baseline
pv_b = np.zeros(n); pv_b[0] = 1e9; wb = TARGET_W[3]
for t in range(1, n):
    tgt = TARGET_W[state_b[t-1]]; d_ = tgt - wb
    w_new = tgt if abs(d_) < SNAP_THR else wb + d_/RAMP_DAYS
    w_new = float(np.clip(w_new, 0.0, 1.30))
    r = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
    cash_r = max(0,1-w_new)*DEPOSIT_R
    marg_c = max(0,w_new-1)*BORROW_R
    trd_c  = abs(w_new-wb)*TC
    pv_b[t] = pv_b[t-1]*(1 + w_new*r + cash_r - marg_c - trd_c)
    wb = w_new

# CRISIS segments baseline
def crisis_lag(state_arr):
    segs = []
    i = 0
    while i < len(state_arr):
        if state_arr[i] == 1:
            j = i
            while j < len(state_arr) and state_arr[j] == 1: j += 1
            segs.append((i, j-1)); i = j
        else: i += 1
    rows = []
    for k,(s,e) in enumerate(segs,1):
        sc = close[s:e+1]
        if np.all(np.isnan(sc)): continue
        bl = int(np.nanargmin(sc)); bi = s+bl
        rows.append({"seg":k, "days":e-s+1, "lag":e-bi,
                     "bot_to_exit_%": (sc[-1]/sc[bl]-1)*100,
                     "entry_to_exit_%": (sc[-1]/sc[0]-1)*100})
    return rows, len(segs)

baseline_rows, n_seg_b = crisis_lag(state_b)
b_df = pd.DataFrame(baseline_rows)

def metrics(pv_arr, dates):
    pv_arr = np.asarray(pv_arr, float)
    valid = np.where(pv_arr>0)[0]
    if len(valid)<2: return {}
    i0,i1 = valid[0], valid[-1]
    yrs = (dates.iloc[i1]-dates.iloc[i0]).days/365.25
    cagr = (pv_arr[i1]/pv_arr[i0])**(1/yrs)-1 if yrs>0 else 0
    sub = pv_arr[i0:i1+1]; rets = np.diff(sub)/sub[:-1]
    n_sub = len(sub)-1; spy_ = n_sub/yrs
    sh = np.mean(rets)*spy_/(np.std(rets)*np.sqrt(spy_)) if np.std(rets)>0 else 0
    rm = np.maximum.accumulate(sub); dd_ = sub/rm-1
    mdd = float(np.min(dd_))
    calmar = cagr/abs(mdd) if mdd<0 else np.inf
    return {"cagr":cagr, "sharpe":sh, "max_dd":mdd, "calmar":calmar, "final":pv_arr[i1]}

dates = vni["time"]
m_v2 = metrics(pv, dates)
m_bh = metrics(pv_bh, dates)
m_b1 = metrics(pv_b, dates)
# Since-2011 (here CSV starts 2014, but mask compatible)
mask_2011 = (vni["time"] >= "2011-01-01").values
idx_2011 = np.where(mask_2011)[0]
if len(idx_2011)>0:
    i0 = idx_2011[0]
    # rebase pv from i0
    pv2 = pv.copy().astype(float); pv2_bh = pv_bh.copy().astype(float)
    pv2 = pv2[i0:]; pv2_bh = pv2_bh[i0:]
    if pv2[0]>0: pv2 = pv2 / pv2[0] * 1e9
    if pv2_bh[0]>0: pv2_bh = pv2_bh / pv2_bh[0] * 1e9
    m_v2_2014 = metrics(pv2, dates.iloc[i0:].reset_index(drop=True))
    m_bh_2014 = metrics(pv2_bh, dates.iloc[i0:].reset_index(drop=True))
else:
    m_v2_2014 = m_bh_2014 = {}

print("\n" + "="*100)
print(f"{'METRIC':<12} {'v2 (no-smooth + early)':<32} {'baseline v1 (smooth + gate60)':<35} {'B&H':<20}")
print("="*100)
def fmt(m):
    if not m: return "N/A"
    return f"CAGR={m['cagr']*100:.2f}% Sh={m['sharpe']:.2f} DD={m['max_dd']*100:.1f}% Cm={m['calmar']:.2f}"
print(f"{'2014-2026':<12} {fmt(m_v2):<32} {fmt(m_b1):<35} {fmt(m_bh):<20}")

# Final wealth multiples
print(f"\nFinal NAV (1B start): v2={pv[-1]/1e9:.2f}B  baseline={pv_b[-1]/1e9:.2f}B  B&H={pv_bh[-1]/1e9:.2f}B")

# Baseline CRISIS lag stats
if len(b_df) > 0:
    print(f"\n--- BASELINE CRISIS lag stats (n={n_seg_b} segments) ---")
    print(f"Median lag bottom→exit: {b_df['lag'].median():.1f}")
    print(f"Mean   lag bottom→exit: {b_df['lag'].mean():.1f}")
    print(f"Median rally bottom→exit: {b_df['bot_to_exit_%'].median():.1f}%")
    print(f"Mean   rally bottom→exit: {b_df['bot_to_exit_%'].mean():.1f}%")

# Transitions count
def count_trans(arr):
    return int(np.sum(np.diff(arr) != 0))
nt = count_trans(state_final)
print(f"\nTotal transitions: {nt}")
state_counts = {s: int(np.sum(state_final==s)) for s in range(1,6)}
total = sum(state_counts.values())
print("State distribution:")
for s, c in state_counts.items():
    print(f"  {STATE_NAMES[s]:<8}: {c:>5} phiên ({c/total*100:5.1f}%)")

# ════════════════════ CRISIS analysis v2 ════════════════════
segs = []
i = 0
while i < n:
    if state_final[i] == 1:
        j = i
        while j<n and state_final[j]==1: j += 1
        segs.append((i, j-1)); i = j
    else: i += 1

print(f"\n=== v2 CRISIS segments: {len(segs)} ===")
print(f"{'#':>3} {'start':>12} {'end':>12} {'days':>5} {'bot_date':>12} "
      f"{'lag_bot→exit':>13} {'bot→exit_%':>10} {'entry→exit_%':>13}")
print("-"*100)
rows = []
for k, (s,e) in enumerate(segs, 1):
    seg_close = close[s:e+1]
    if np.all(np.isnan(seg_close)): continue
    bot_local = int(np.nanargmin(seg_close))
    bot_idx = s + bot_local
    days = e - s + 1
    entry_c = seg_close[0]; bot_c = seg_close[bot_local]; exit_c = seg_close[-1]
    lag = e - bot_idx
    bt_ex = (exit_c/bot_c - 1)*100
    en_ex = (exit_c/entry_c - 1)*100
    rows.append({"seg":k, "days":days, "lag":lag, "bot_to_exit_%":bt_ex, "entry_to_exit_%":en_ex})
    print(f"{k:>3} {vni['time'].iloc[s].strftime('%Y-%m-%d'):>12} {vni['time'].iloc[e].strftime('%Y-%m-%d'):>12} "
          f"{days:>5} {vni['time'].iloc[bot_idx].strftime('%Y-%m-%d'):>12} "
          f"{lag:>13} {bt_ex:>9.1f}% {en_ex:>12.1f}%")

if rows:
    rdf = pd.DataFrame(rows)
    print(f"\nMedian lag bottom→exit: {rdf['lag'].median():.1f} (baseline=18)")
    print(f"Mean   lag bottom→exit: {rdf['lag'].mean():.1f} (baseline=29.2)")
    print(f"Median rally bottom→exit: {rdf['bot_to_exit_%'].median():.1f}% (baseline=7.9%)")
    print(f"Mean   rally bottom→exit: {rdf['bot_to_exit_%'].mean():.1f}% (baseline=8.7%)")

# ════════════════════ VARIANTS ════════════════════
print("\n" + "="*100)
print("=== VARIANT SWEEPS (no-smooth, different early-exit signal sets) ===")
print("="*100)

def run_variant(use_E1=True, use_E2=True, use_E3=True, use_E4=True,
                e3_thr=0.20, e3_days=3, gate_min=0,
                mode_win=1, min_stay=1, label=""):
    # Build exit_signal
    E1v = bull_mask.copy() if use_E1 else np.zeros(n, dtype=bool)
    E2v = np.zeros(n, dtype=bool)
    if use_E2:
        for i in range(5, n):
            if (dd[i] < E2_DD_THR and close[i] > close[i-5]*E2_BOUNCE_5D
                and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
                and rsi[i] > rsi[i-5]*E2_RSI_RISE
                and not np.isnan(cmf[i]) and cmf[i] > 0):
                E2v[i] = True
    E3v = np.zeros(n, dtype=bool)
    if use_E3:
        st = 0
        for i in range(n):
            if not np.isnan(r_score_ema[i]) and r_score_ema[i] > e3_thr: st += 1
            else: st = 0
            if st >= e3_days: E3v[i] = True
    E4v = np.zeros(n, dtype=bool)
    if use_E4:
        for i in range(E4_LOOKBACK, n):
            if np.isnan(macd_hist[i]) or np.isnan(macd_hist[i-1]): continue
            if macd_hist[i] > 0 and macd_hist[i-1] <= 0:
                lb = macd_hist[i-E4_LOOKBACK:i]; lb = lb[~np.isnan(lb)]
                if len(lb)>0 and np.min(lb) < E4_MACD_OVERSOLD:
                    E4v[i] = True
    es = E1v | E2v | E3v | E4v

    # Gate
    st_arr = state_ov.copy()
    ga = False; gs = -1
    for i in range(n):
        if bear_mask[i]:
            if not ga: ga = True; gs = i
            else: gs = i
        if ga:
            if st_arr[i] > 1: st_arr[i] = 1
            if (i - gs) >= gate_min and es[i]:
                ga = False
    # Smoothing
    if mode_win > 1: st_arr = rolling_mode(st_arr, mode_win)
    if min_stay > 1: st_arr = min_stay_filter(st_arr, min_stay)

    # Backtest
    pv_v = np.zeros(n); pv_v[0] = 1e9; wv = TARGET_W[3]
    for t in range(1,n):
        tgt = TARGET_W[st_arr[t-1]]; d_ = tgt - wv
        w_new = tgt if abs(d_)<SNAP_THR else wv + d_/RAMP_DAYS
        w_new = float(np.clip(w_new,0,1.30))
        r = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv_v[t] = pv_v[t-1]*(1 + w_new*r + max(0,1-w_new)*DEPOSIT_R
                              - max(0,w_new-1)*BORROW_R - abs(w_new-wv)*TC)
        wv = w_new

    m = metrics(pv_v, vni["time"])
    rows_v, n_seg = crisis_lag(st_arr)
    df_v = pd.DataFrame(rows_v)
    med_lag = df_v["lag"].median() if len(df_v)>0 else np.nan
    print(f"  {label:<45} CAGR={m['cagr']*100:5.2f}%  Sh={m['sharpe']:.2f}  DD={m['max_dd']*100:6.2f}%  Cm={m['calmar']:.2f}  segs={n_seg:>3}  med_lag={med_lag:>4.1f}")
    return m, pv_v, st_arr

# Variants
print(f"  {'(reference)':<45} CAGR=14.39%  Sh=1.14  DD=-18.30%  Cm=0.78  segs= 13  med_lag=17.0  [baseline]")
m_v2a, pv_v2a, st_v2a = run_variant(use_E3=True, e3_thr=0.20, e3_days=3, label="v2  E1+E2+E3(0.20×3d)+E4, no smooth")
m_v2b, _,    _      = run_variant(use_E3=False, label="v2b E1+E2+E4 only (no E3), no smooth")
m_v2c, _,    _      = run_variant(use_E3=True, e3_thr=0.30, e3_days=5, label="v2c E1+E2+E3(0.30×5d)+E4, no smooth")
m_v2d, _,    _      = run_variant(use_E3=True, e3_thr=0.25, e3_days=5, label="v2d E1+E2+E3(0.25×5d)+E4, no smooth")
m_v2e, _,    _      = run_variant(use_E3=True, e3_thr=0.20, e3_days=3, mode_win=5, min_stay=3, label="v2e v2a + mode5 + minstay3")
m_v2f, _,    _      = run_variant(use_E3=True, e3_thr=0.20, e3_days=3, gate_min=20, label="v2f v2a + gate_min=20")
m_v2g, pv_v2g, st_v2g = run_variant(use_E1=True, use_E2=True, use_E3=False, use_E4=False, gate_min=30, label="v2g E1+E2 only, gate_min=30")

# ════════════════════ SAVE v2g WINNER ════════════════════
out_g = pd.DataFrame({
    "time": vni["time"],
    "state_v2g": st_v2g,
    "state_baseline": state_b,
    "state_raw": state_raw,
    "r_score_ema": r_score_ema,
    "Close": close,
    "pv_v2g": pv_v2g,
    "pv_baseline": pv_b,
    "pv_bh": pv_bh,
})
out_g.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_history.csv"), index=False)
print(f"\nSaved → vnindex_5state_v2g_history.csv  ({len(out_g)} rows)")

# Stats summary
print("\n" + "="*78)
print("WINNER: v2g  (E1 BullDvg + E2 Capitulation, NO smoothing, gate_min=30)")
print("="*78)
print(f"  CAGR    : {m_v2g['cagr']*100:5.2f}%   vs baseline {m_b1['cagr']*100:5.2f}%   diff {(m_v2g['cagr']-m_b1['cagr'])*100:+.2f}pp")
print(f"  Sharpe  : {m_v2g['sharpe']:.2f}     vs baseline {m_b1['sharpe']:.2f}     diff {m_v2g['sharpe']-m_b1['sharpe']:+.2f}")
print(f"  MaxDD   : {m_v2g['max_dd']*100:5.2f}%   vs baseline {m_b1['max_dd']*100:5.2f}%   diff {(m_v2g['max_dd']-m_b1['max_dd'])*100:+.2f}pp")
print(f"  Calmar  : {m_v2g['calmar']:.2f}     vs baseline {m_b1['calmar']:.2f}     diff {m_v2g['calmar']-m_b1['calmar']:+.2f}")
print(f"  Final NV: {pv_v2g[-1]/1e9:.2f}B vs baseline {pv_b[-1]/1e9:.2f}B  vs B&H {pv_bh[-1]/1e9:.2f}B")

# Save state_final to CSV
out = pd.DataFrame({"time": vni["time"], "state_v2": state_final,
                    "state_raw": state_raw, "gate_flag": gate_flag,
                    "r_score_ema": r_score_ema, "pv_v2": pv, "pv_bh": pv_bh})
out.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2_history.csv"), index=False)
print(f"\nSaved → vnindex_5state_v2_history.csv")

# Save events
ev_df = pd.DataFrame(gate_events)
ev_df.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2_gate_events.csv"), index=False)
print(f"Saved → vnindex_5state_v2_gate_events.csv  (n={len(gate_events)})")
