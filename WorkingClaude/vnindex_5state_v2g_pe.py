# -*- coding: utf-8 -*-
"""
vnindex_5state_v2g_pe.py
========================
Variant of v2g that uses cleaned VNINDEX_PE (2006-2026 coverage) with quality flags.

Tier 1A: PE override active from 2007 (was 2010-11) — automatic via cleaned PE
Tier 1B: Rolling 5Y P85 trigger parallel with expanding P90
         (prevents loss of sensitivity post-2011 due to 2006-2007 bubble in expanding)
Tier 2C: mask_2011 → mask_2007 for BearDvg/BullDvg (use OHLCV-based dvg from 2007)

Quality-aware: PE-based triggers only fire when pe_quality ≤ 2 (excludes long-gap interp)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ════════════════════ PARAMS ════════════════════
W_BASE = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10, "CMF":0.08, "Breadth":0.12}
MIN_LB, MIN_FACTORS, EMA_ALPHA = 252, 3, 0.40
RAMP_DAYS, SNAP_THR = 3, 0.03
TC, DEPOSIT_R, BORROW_R = 0.001, 0.06/252, 0.10/252
TARGET_W = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# v2g_pe specific
GATE_MIN_DUR    = 30
ROLLING_PE_WIN  = 5 * 252      # 5-year rolling window for P85
ROLLING_PE_PCT  = 0.85
EXPANDING_PE_PCT = 0.90        # existing
DVG_MASK_START  = "2007-01-01"  # was 2011-01-01

# ════════════════════ LOAD CLEANED DATA ════════════════════
print("Loading cleaned VNINDEX data ...")
src_path = os.path.join(WORKDIR, "vnindex_full_2000_2026.csv")
vni = pd.read_csv(src_path, low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

n = len(vni)
print(f"  rows={n}  {vni['time'].iloc[0].date()} → {vni['time'].iloc[-1].date()}")

close = vni["Close"].values.astype(float)
high  = vni["High"].values.astype(float)
low   = vni["Low"].values.astype(float)
vol_  = vni["Volume"].values.astype(float)
pe    = vni["VNINDEX_PE_clean"].values.astype(float)
pe_q  = vni["pe_quality"].values.astype(int) if "pe_quality" in vni.columns else np.zeros(n, dtype=int)
breadth_arr = vni["breadth"].values.astype(float) if "breadth" in vni.columns else np.full(n, np.nan)

cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
spy = n/(cal_days/365.25) if cal_days>0 else 252
print(f"  sessions/year = {spy:.1f}")

# PE quality breakdown
print(f"  PE quality: q0={np.sum(pe_q==0)} q1={np.sum(pe_q==1)} q2={np.sum(pe_q==2)} q3={np.sum(pe_q==3)} q4={np.sum(pe_q==4)}")

# ════════════════════ INDICATORS (same as v2g) ════════════════════
print("Computing indicators ...")
p3m = np.full(n, np.nan); p1m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60] - 1
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20] - 1
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

# RSI Wilder 14
rsi = np.full(n, np.nan); avg_u = avg_d = np.nan; period = 14
for i in range(1, n):
    diff = close[i]-close[i-1]; u = max(diff,0); d = max(-diff,0)
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

# MACD
ema12 = np.full(n,np.nan); ema26 = np.full(n,np.nan); signal = np.full(n,np.nan); macd_hist = np.full(n,np.nan)
k12,k26,k9 = 2/13, 2/27, 2/10
for i in range(n):
    if i==0 or np.isnan(ema12[i-1]):
        ema12[i]=close[i]; ema26[i]=close[i]
    else:
        ema12[i] = ema12[i-1]*(1-k12) + close[i]*k12
        ema26[i] = ema26[i-1]*(1-k26) + close[i]*k26
    macd_line = ema12[i]-ema26[i]
    if i==0 or np.isnan(signal[i-1]): signal[i]=macd_line
    else: signal[i] = signal[i-1]*(1-k9) + macd_line*k9
    if i>=33: macd_hist[i] = macd_line - signal[i]

# CMF
hl = high - low
mfm = np.where(hl>0, ((close-low)-(high-close))/np.where(hl>0,hl,1), 0)
mfv = mfm * vol_
cmf = np.full(n, np.nan)
for i in range(14, n):
    s_v = np.sum(vol_[i-14:i])
    if s_v>0: cmf[i] = np.sum(mfv[i-14:i])/s_v

# Composite score
def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        h = arr[:t+1]; v = h[~np.isnan(h)]
        if len(v)<min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(v <= arr[t])/len(v)
    return out

FK = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
factor_arrs = {"P3M":p3m, "P1M":p1m, "MA200":ma200_dev, "RSI":rsi, "MACD":macd_hist, "CMF":cmf, "Breadth":breadth_arr}
print("Computing ranks ...")
ranks = {k: expanding_pct_rank(factor_arrs[k], MIN_LB) for k in FK}
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FK if not np.isnan(ranks[k][t])}
    if len(avail)<MIN_FACTORS: continue
    ws = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score = expanding_pct_rank(score, MIN_LB)
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; prev = r_score_ema[t-1] if t>0 else np.nan
    if np.isnan(v): r_score_ema[t]=prev
    elif np.isnan(prev): r_score_ema[t]=v
    else: r_score_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    if rs<0.20: return 2
    if rs<0.70: return 3
    if rs<0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in r_score_ema])

# ════════════════════ TIER 1A + 1B: PE OVERRIDES ════════════════════
print("Computing PE overrides (expanding P90 + rolling 5Y P85) ...")
# Compute PE_clean rank both ways. Only consider points where pe_quality ≤ 2
pe_reliable = pe.copy()
pe_reliable[pe_q > 2] = np.nan   # long-gap interp + missing excluded

# Expanding P90 of reliable PE
pe_p90_exp = np.full(n, np.nan)
for t in range(n):
    h = pe_reliable[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p90_exp[t] = np.nanpercentile(v, EXPANDING_PE_PCT*100)

# Rolling 5Y P85
pe_p85_roll = np.full(n, np.nan)
for t in range(n):
    lo = max(0, t-ROLLING_PE_WIN+1)
    h = pe_reliable[lo:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p85_roll[t] = np.nanpercentile(v, ROLLING_PE_PCT*100)

# PE high = either trigger fires (quality-gated)
pe_high = np.zeros(n, dtype=bool)
for t in range(n):
    if pe_q[t] > 2 or np.isnan(pe[t]): continue
    cond_exp  = (not np.isnan(pe_p90_exp[t])) and (pe[t] > pe_p90_exp[t])
    cond_roll = (not np.isnan(pe_p85_roll[t])) and (pe[t] > pe_p85_roll[t])
    if cond_exp or cond_roll:
        pe_high[t] = True

# PE rank (for gate exit condition) — use expanding rank
pe_rank = np.full(n, np.nan)
for t in range(n):
    if pe_q[t] > 2 or np.isnan(pe[t]): continue
    h = pe_reliable[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_rank[t] = np.sum(v<=pe[t])/len(v)

n_pe_high_pre2011 = int(np.sum(pe_high & (vni["time"]<"2011-01-01").values))
n_pe_high_post2011 = int(np.sum(pe_high & (vni["time"]>="2011-01-01").values))
print(f"  PE_high triggers: pre-2011={n_pe_high_pre2011}, post-2011={n_pe_high_post2011}")

# ════════════════════ RISK OVERRIDES (with new PE) ════════════════════
print("Computing risk overrides ...")
running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max>0, close/running_max-1, 0.0)
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
    if pe_high[i] and s == 5: s = 4              # Tier 1A+1B: PE override
    if dd[i] < -0.25 and s >= 4: s = 3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5: s=4
    state_ov[i] = s

# ════════════════════ BEAR/BULL DVG with mask_2007 ════════════════════
print(f"Computing BearDvg/BullDvg with mask_start={DVG_MASK_START} ...")
D_RSI = rsi
def roll_max(a,w): return pd.Series(a).rolling(w, min_periods=1).max().values
def roll_min(a,w): return pd.Series(a).rolling(w, min_periods=1).min().values
def arg_close_max(rsi_a, close_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = close_a[lo+k]
    return out
def arg_macd_max(rsi_a, macd_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = macd_a[lo+k]
    return out
def arg_close_min(rsi_a, close_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmin(seg)); out[i] = close_a[lo+k]
    return out

D_RSI_T1W     = np.concatenate([[np.nan]*5, D_RSI[:-5]])
D_RSI_Max1W   = roll_max(D_RSI, 5);    D_RSI_Max3M = roll_max(D_RSI, 60)
D_RSI_Min1W   = roll_min(D_RSI, 5);    D_RSI_Min3M = roll_min(D_RSI, 60)
D_RSI_Max1W_C = arg_close_max(D_RSI, close, 5);  D_RSI_Max3M_C = arg_close_max(D_RSI, close, 60)
D_RSI_Max1W_M = arg_macd_max(D_RSI, macd_hist, 5); D_RSI_Max3M_M = arg_macd_max(D_RSI, macd_hist, 60)
D_RSI_Min1W_C = arg_close_min(D_RSI, close, 5)
D_RSI_MinT3   = roll_min(D_RSI, 3)
D_CMF, D_MACDdiff = cmf, macd_hist
C_L1W = close/np.where(roll_min(close,5)>0, roll_min(close,5), 1)
C_L1M = close/np.where(roll_min(close,20)>0, roll_min(close,20), 1)
mask_dvg = (vni["time"]>=DVG_MASK_START).values

with np.errstate(divide='ignore', invalid='ignore'):
    bear1 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044) & (D_RSI_Max3M>0.74) &
             (D_RSI_Max1W<0.72) & (D_RSI_Max1W>0.61) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.028) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.11) &
             (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.96) &
             (D_RSI_MinT3>0.43) & (D_CMF<0.13) & mask_dvg)
    bear2 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016) & (D_RSI_Max3M>0.77) &
             (D_RSI_Max1W<0.79) & (D_RSI_Max1W>0.60) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.008) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.10) &
             (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.97) &
             (D_RSI_MinT3>0.50) & (D_CMF<0.15) & mask_dvg)
    bull1 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.90) & (D_RSI_Min1W<0.60) &
             (D_RSI_Min3M<0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.15) &
             (D_MACDdiff>0) & (D_RSI_MinT3<0.50) & (D_RSI_Max1W<0.48) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.12) & (D_CMF>0) &
             (C_L1M<1.21) & (C_L1W<1.05) & mask_dvg)
    bull2 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.92) & (D_RSI_Min1W<0.52) &
             (D_RSI_Min3M<0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.10) &
             (D_MACDdiff>0) & (D_RSI_MinT3<0.56) & (D_RSI_Max1W<0.64) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.10) & (D_CMF>0) &
             (C_L1M<1.20) & (C_L1W<1.025) & mask_dvg)

bear_mask = np.nan_to_num(bear1, nan=0).astype(bool) | np.nan_to_num(bear2, nan=0).astype(bool)
bull_mask = np.nan_to_num(bull1, nan=0).astype(bool) | np.nan_to_num(bull2, nan=0).astype(bool)
print(f"  BearDvg events: {bear_mask.sum()} | BullDvg events: {bull_mask.sum()}")
n_bear_pre2011 = int(np.sum(bear_mask & (vni["time"]<"2011-01-01").values))
n_bull_pre2011 = int(np.sum(bull_mask & (vni["time"]<"2011-01-01").values))
print(f"  pre-2011 captured: bear={n_bear_pre2011} bull={n_bull_pre2011}")

# ════════════════════ E2 CAPITULATION ════════════════════
E2 = np.zeros(n, dtype=bool)
for i in range(5, n):
    if (dd[i] < -0.15 and close[i] > close[i-5]*1.05
        and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
        and rsi[i] > rsi[i-5]*1.15
        and not np.isnan(cmf[i]) and cmf[i] > 0):
        E2[i] = True

# ════════════════════ v2g_pe GATE + STATE (no smoothing) ════════════════════
print("Building v2g_pe state series ...")
state_pe = state_ov.copy()
ga = False; gs = -1
for i in range(n):
    if bear_mask[i]:
        if not ga: ga = True; gs = i
        else: gs = i
    if ga:
        if state_pe[i] > 1: state_pe[i] = 1
        sessions_in = i - gs
        if sessions_in >= GATE_MIN_DUR:
            if bull_mask[i] or E2[i]:
                ga = False

# ════════════════════ ALSO RUN BASELINE v2g (no PE upgrade) for comparison ════════════════════
# Replicate v2g logic with mask_2011 and OLD PE rules
print("Building plain v2g for comparison ...")
mask_2011_arr = (vni["time"]>="2011-01-01").values
# Old PE override: same expanding P90 but on raw post-2010 PE (uses original VNINDEX_PE column)
pe_old = vni["VNINDEX_PE"].values.astype(float)
pe_old[(pe_old < 3) | np.isnan(pe_old)] = np.nan
pe_p90_old = np.full(n, np.nan)
for t in range(n):
    h = pe_old[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p90_old[t] = np.nanpercentile(v, 90)
state_ov_old = state_raw.copy()
for i in range(n):
    s = state_ov_old[i]
    if not np.isnan(pe_p90_old[i]) and not np.isnan(pe_old[i]) and pe_old[i]>pe_p90_old[i] and s==5: s=4
    if dd[i] < -0.25 and s >= 4: s = 3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5: s=4
    state_ov_old[i] = s

# Re-compute bear/bull with mask_2011 for v2g baseline
with np.errstate(divide='ignore', invalid='ignore'):
    bear1_v = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044) & (D_RSI_Max3M>0.74) &
               (D_RSI_Max1W<0.72) & (D_RSI_Max1W>0.61) &
               (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.028) &
               (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.11) &
               (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.96) &
               (D_RSI_MinT3>0.43) & (D_CMF<0.13) & mask_2011_arr)
    bear2_v = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016) & (D_RSI_Max3M>0.77) &
               (D_RSI_Max1W<0.79) & (D_RSI_Max1W>0.60) &
               (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.008) &
               (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.10) &
               (D_MACDdiff<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.97) &
               (D_RSI_MinT3>0.50) & (D_CMF<0.15) & mask_2011_arr)
    bull1_v = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.90) & (D_RSI_Min1W<0.60) &
               (D_RSI_Min3M<0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.15) &
               (D_MACDdiff>0) & (D_RSI_MinT3<0.50) & (D_RSI_Max1W<0.48) &
               (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.12) & (D_CMF>0) &
               (C_L1M<1.21) & (C_L1W<1.05) & mask_2011_arr)
    bull2_v = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.92) & (D_RSI_Min1W<0.52) &
               (D_RSI_Min3M<0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.10) &
               (D_MACDdiff>0) & (D_RSI_MinT3<0.56) & (D_RSI_Max1W<0.64) &
               (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.10) & (D_CMF>0) &
               (C_L1M<1.20) & (C_L1W<1.025) & mask_2011_arr)
bear_mask_v = np.nan_to_num(bear1_v, nan=0).astype(bool) | np.nan_to_num(bear2_v, nan=0).astype(bool)
bull_mask_v = np.nan_to_num(bull1_v, nan=0).astype(bool) | np.nan_to_num(bull2_v, nan=0).astype(bool)

# Plain v2g gate
state_v2g = state_ov_old.copy()
ga = False; gs = -1
for i in range(n):
    if bear_mask_v[i]:
        if not ga: ga = True; gs = i
        else: gs = i
    if ga:
        if state_v2g[i] > 1: state_v2g[i] = 1
        if (i-gs) >= 30 and (bull_mask_v[i] or E2[i]):
            ga = False

# ════════════════════ BASELINE v1 (smooth + gate60) ════════════════════
def rolling_mode(states, window):
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out
def min_stay_filter(states, min_days):
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j<len(out) and out[j]==out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

print("Building baseline v1 state series ...")
_rs_streak10 = np.zeros(n, dtype=bool); _st=0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i]>0.65: _st += 1
    else: _st = 0
    if _st>=10: _rs_streak10[i] = True

pe_rank_old = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_old[t]): continue
    v = pe_old[:t+1]; v = v[~np.isnan(v)]
    if len(v)>=60: pe_rank_old[t] = np.sum(v<=pe_old[t])/len(v)
p3m_rank = ranks["P3M"]
state_b_dvg = state_ov_old.copy()
ga = False; gs = -1
for i in range(n):
    if bear_mask_v[i]:
        if not ga: ga=True; gs=i
        else: gs=i
    if ga:
        if state_b_dvg[i]>1: state_b_dvg[i]=1
        if (i-gs) >= 60:
            _p3m_ok = (not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            _pe_ok  = (not np.isnan(pe_rank_old[i])) and pe_rank_old[i]<0.80
            if bull_mask_v[i] or (_p3m_ok and _pe_ok) or _rs_streak10[i]:
                ga = False
state_baseline = rolling_mode(state_b_dvg, 15)
state_baseline = min_stay_filter(state_baseline, 7)

# ════════════════════ BACKTEST ════════════════════
def backtest(state_arr):
    pv = np.zeros(n); pv[0] = 1e9; w = TARGET_W[3]
    for t in range(1, n):
        tgt = TARGET_W[state_arr[t-1]]; d_ = tgt - w
        w_new = tgt if abs(d_)<SNAP_THR else w + d_/RAMP_DAYS
        w_new = float(np.clip(w_new, 0, 1.30))
        r = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t] = pv[t-1]*(1 + w_new*r + max(0,1-w_new)*DEPOSIT_R
                          - max(0,w_new-1)*BORROW_R - abs(w_new-w)*TC)
        w = w_new
    return pv

print("Backtesting all variants ...")
pv_pe   = backtest(state_pe)
pv_v2g  = backtest(state_v2g)
pv_base = backtest(state_baseline)
pv_bh = np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]

# ════════════════════ METRICS ════════════════════
def metrics(pv, dates, i0=None, i1=None):
    a = np.asarray(pv, float)
    if i0 is None: i0 = 0
    if i1 is None: i1 = len(a)-1
    a = a[i0:i1+1]
    valid = np.where(a>0)[0]
    if len(valid)<2: return {}
    j0, j1 = valid[0], valid[-1]
    yrs = (dates.iloc[i0+j1] - dates.iloc[i0+j0]).days/365.25
    cagr = (a[j1]/a[j0])**(1/yrs)-1 if yrs>0 else 0
    sub = a[j0:j1+1]; rets = np.diff(sub)/sub[:-1]
    spy_ = (len(sub)-1)/yrs if yrs>0 else 252
    sh = np.mean(rets)*spy_/(np.std(rets)*np.sqrt(spy_)) if np.std(rets)>0 else 0
    rm = np.maximum.accumulate(sub); ddx = sub/rm - 1
    mdd = float(np.min(ddx))
    cal = cagr/abs(mdd) if mdd<0 else np.inf
    return {"cagr":cagr, "sharpe":sh, "max_dd":mdd, "calmar":cal, "n_yrs":yrs, "final":a[j1]/a[j0]}

def fmt(m):
    if not m: return "N/A"
    return f"CAGR={m['cagr']*100:5.2f}% Sh={m['sharpe']:.2f} DD={m['max_dd']*100:6.2f}% Cm={m['calmar']:.2f} ×{m['final']:.2f}"

dates = vni["time"]
print("\n" + "="*120)
print(f"{'PERIOD':<14} {'v2g_pe (PE 2007+, mask2007)':<46} {'v2g (PE 2010+, mask2011)':<44} {'baseline v1':<46} {'B&H'}")
print("="*120)

# FULL
m_full_pe   = metrics(pv_pe, dates)
m_full_v2g  = metrics(pv_v2g, dates)
m_full_base = metrics(pv_base, dates)
m_full_bh   = metrics(pv_bh, dates)
print(f"{'FULL 2000-26':<14} {fmt(m_full_pe):<46} {fmt(m_full_v2g):<44} {fmt(m_full_base):<46} {fmt(m_full_bh)}")

# SINCE 2007 (where new PE+dvg starts helping)
i_2007 = int(np.argmax(dates >= pd.Timestamp("2007-01-01")))
def slice_pv(pv, i0):
    p = pv[i0:].copy().astype(float)
    if p[0]>0: p = p/p[0]*1e9
    return p
pv_pe_07   = slice_pv(pv_pe, i_2007)
pv_v2g_07  = slice_pv(pv_v2g, i_2007)
pv_base_07 = slice_pv(pv_base, i_2007)
pv_bh_07   = slice_pv(pv_bh, i_2007)
d_07 = dates.iloc[i_2007:].reset_index(drop=True)
print(f"{'SINCE 2007':<14} {fmt(metrics(pv_pe_07, d_07)):<46} {fmt(metrics(pv_v2g_07, d_07)):<44} {fmt(metrics(pv_base_07, d_07)):<46} {fmt(metrics(pv_bh_07, d_07))}")

# SINCE 2011 (where current v2g shines)
i_2011 = int(np.argmax(dates >= pd.Timestamp("2011-01-01")))
pv_pe_11   = slice_pv(pv_pe, i_2011)
pv_v2g_11  = slice_pv(pv_v2g, i_2011)
pv_base_11 = slice_pv(pv_base, i_2011)
pv_bh_11   = slice_pv(pv_bh, i_2011)
d_11 = dates.iloc[i_2011:].reset_index(drop=True)
print(f"{'SINCE 2011':<14} {fmt(metrics(pv_pe_11, d_11)):<46} {fmt(metrics(pv_v2g_11, d_11)):<44} {fmt(metrics(pv_base_11, d_11)):<46} {fmt(metrics(pv_bh_11, d_11))}")

# ════════════════════ CRISIS lag stats (since 2007) ════════════════════
def crisis_lag_stats(state_arr, since="2007-01-01"):
    start_idx = int(np.argmax(dates >= pd.Timestamp(since)))
    segs = []; i = 0
    while i < len(state_arr):
        if state_arr[i]==1:
            j = i
            while j < len(state_arr) and state_arr[j]==1: j += 1
            if j-1 >= start_idx: segs.append((max(i,start_idx), j-1))
            i = j
        else: i += 1
    rows = []
    for s,e in segs:
        sc = close[s:e+1]
        if np.all(np.isnan(sc)): continue
        bl = int(np.nanargmin(sc)); bi = s+bl
        rows.append({"days":e-s+1, "lag":e-bi, "rally": (sc[-1]/sc[bl]-1)*100})
    return pd.DataFrame(rows), len(segs)

print("\n" + "="*78)
print("CRISIS lag stats (bottom → exit, since 2007)")
print("="*78)
for name, st in [("v2g_pe", state_pe), ("v2g", state_v2g), ("baseline", state_baseline)]:
    df_, n_seg = crisis_lag_stats(st)
    if len(df_) == 0: continue
    print(f"  {name:<10} n_segs={n_seg:>3} median_lag={df_['lag'].median():>5.1f} mean_lag={df_['lag'].mean():>5.1f}  median_rally={df_['rally'].median():>5.1f}%  mean_rally={df_['rally'].mean():>5.1f}%")

# State distribution
print("\nState distribution:")
print(f"{'state':<10} {'v2g_pe':>9} {'v2g':>9} {'baseline':>10}")
for s in range(1,6):
    print(f"  {STATE_NAMES[s]:<8} {np.sum(state_pe==s)/n*100:>8.1f}% {np.sum(state_v2g==s)/n*100:>8.1f}% {np.sum(state_baseline==s)/n*100:>9.1f}%")

# Transitions
print(f"\nTransitions: v2g_pe={int(np.sum(np.diff(state_pe)!=0))}  v2g={int(np.sum(np.diff(state_v2g)!=0))}  baseline={int(np.sum(np.diff(state_baseline)!=0))}")

# ════════════════════ QWF ════════════════════
print("\n" + "="*100)
print("QUARTERLY WALK-FORWARD trailing-3Y at each quarter-end (2010-2026)")
print("="*100)
qends = pd.date_range(start="2010-03-31", end=dates.iloc[-1], freq="QE")
rows = []
for qe in qends:
    arr = np.where(dates <= qe)[0]
    if len(arr)==0: continue
    ei = arr[-1]
    row = {"q_end": qe.strftime("%Y-%m-%d")}
    for yrs in [1, 3, 5]:
        for nm, pvx in [("pe", pv_pe), ("v2g", pv_v2g), ("base", pv_base), ("bh", pv_bh)]:
            end_t = dates.iloc[ei]; start_t = end_t - pd.DateOffset(years=yrs)
            si_arr = np.where(dates >= start_t)[0]
            if len(si_arr) == 0: continue
            si = si_arr[0]
            if ei - si < 30: continue
            m = metrics(pvx, dates, si, ei)
            if m:
                row[f"{nm}_{yrs}Y_cagr"] = m["cagr"]*100
                row[f"{nm}_{yrs}Y_sh"]   = m["sharpe"]
                row[f"{nm}_{yrs}Y_dd"]   = m["max_dd"]*100
                row[f"{nm}_{yrs}Y_cm"]   = m["calmar"]
    rows.append(row)
qdf = pd.DataFrame(rows)
qdf.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe_qwf.csv"), index=False)
print(f"Saved → vnindex_5state_v2g_pe_qwf.csv  ({len(qdf)} snapshots)")

print(f"\n--- QWF summary: trailing-3Y MEDIAN across all quarters ---")
print(f"{'system':<10} {'median CAGR':>12} {'median Sharpe':>14} {'median MaxDD':>13} {'median Calmar':>14} {'win vs B&H':>12}")
for nm, label in [("pe","v2g_pe"), ("v2g","v2g"), ("base","baseline"), ("bh","B&H")]:
    col_c, col_s, col_d, col_cm = f"{nm}_3Y_cagr", f"{nm}_3Y_sh", f"{nm}_3Y_dd", f"{nm}_3Y_cm"
    if col_c not in qdf.columns: continue
    c_med = qdf[col_c].dropna().median()
    s_med = qdf[col_s].dropna().median()
    d_med = qdf[col_d].dropna().median()
    cm_med = qdf[col_cm].dropna().median()
    win = (qdf[col_c] > qdf["bh_3Y_cagr"]).mean()*100 if nm != "bh" else 100.0
    print(f"  {label:<8} {c_med:>11.2f}% {s_med:>14.2f} {d_med:>12.2f}% {cm_med:>14.2f} {win:>11.1f}%")

print(f"\n--- Latest snapshot @ {qdf['q_end'].iloc[-1]} ---")
latest = qdf.iloc[-1]
for yrs in [1, 3, 5]:
    print(f"\n  Trailing {yrs}Y:")
    print(f"  {'system':<10} {'CAGR':>7} {'Sharpe':>8} {'MaxDD':>8} {'Calmar':>8}")
    for nm in ["pe", "v2g", "base", "bh"]:
        c = latest.get(f"{nm}_{yrs}Y_cagr", np.nan)
        s = latest.get(f"{nm}_{yrs}Y_sh", np.nan)
        d = latest.get(f"{nm}_{yrs}Y_dd", np.nan)
        cm = latest.get(f"{nm}_{yrs}Y_cm", np.nan)
        if not pd.isna(c):
            print(f"  {nm:<10} {c:>6.2f}% {s:>8.2f} {d:>7.2f}% {cm:>8.2f}")

# Traffic light for v2g_pe trailing-3Y
green = yellow = red = 0
for _, r in qdf.iterrows():
    c = r.get("pe_3Y_cagr", np.nan); d = r.get("pe_3Y_dd", np.nan); bh = r.get("bh_3Y_cagr", np.nan)
    if pd.isna(c) or pd.isna(bh): continue
    if c > bh and d > -25: green += 1
    elif (c < bh - 5) or d < -25: red += 1
    else: yellow += 1
print(f"\nTraffic light (v2g_pe trailing-3Y): 🟢 GREEN={green} 🟡 YELLOW={yellow} 🔴 RED={red}")

# Save state history
out_df = pd.DataFrame({
    "time": vni["time"], "Close": close,
    "state_v2g_pe": state_pe, "state_v2g": state_v2g, "state_baseline": state_baseline,
    "state_raw": state_raw, "r_score_ema": r_score_ema,
    "pe": pe, "pe_quality": pe_q,
    "pe_high": pe_high.astype(int), "bear_dvg": bear_mask.astype(int), "bull_dvg": bull_mask.astype(int),
    "pv_v2g_pe": pv_pe, "pv_v2g": pv_v2g, "pv_baseline": pv_base, "pv_bh": pv_bh,
})
out_df.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe_history.csv"), index=False)
print(f"\nSaved → vnindex_5state_v2g_pe_history.csv ({len(out_df)} rows)")
