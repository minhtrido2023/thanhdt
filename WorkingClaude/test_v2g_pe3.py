# -*- coding: utf-8 -*-
"""
test_v2g_pe3.py
===============
Combine the two winning PE enhancements into v2g_pe3:
  - PE composite weight W=0.03 (low weight, doesn't dominate r_score)
  - S2_bull = PE 6M slope < -25%/yr (PE crash confirms capitulation)

Test additivity: does (comp 0.03) + (S2_bull) ≈ sum of individual gains?

Variants:
  ref          : v2g_pe (current canonical baseline)
  pe3a         : pe_comp 0.03 only
  pe3b         : S2_bull only
  pe3c         : pe_comp 0.03 + S2_bull  ← target hybrid
  pe3d         : pe_comp 0.03 + S2_bull + S4_bull
  pe3e         : pe_comp 0.05 + S2_bull
  pe3f         : pe_comp 0.03 + S1_bull + S2_bull + S4_bull (all bull dvg)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

W_BASE_7 = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10, "CMF":0.08, "Breadth":0.12}
MIN_LB, MIN_FACTORS, EMA_ALPHA = 252, 3, 0.40
RAMP_DAYS, SNAP_THR = 3, 0.03
TC, DEPOSIT_R, BORROW_R = 0.001, 0.06/252, 0.10/252
TARGET_W = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
GATE_MIN_DUR = 30
DVG_MASK_START = "2007-01-01"

# ════════════════════ LOAD ════════════════════
print("Loading cleaned VNINDEX ...")
vni = pd.read_csv(os.path.join(WORKDIR, "vnindex_full_2000_2026.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
n = len(vni)
close = vni["Close"].values.astype(float)
high  = vni["High"].values.astype(float)
low   = vni["Low"].values.astype(float)
vol_  = vni["Volume"].values.astype(float)
pe    = vni["VNINDEX_PE_clean"].values.astype(float)
pe_q  = vni["pe_quality"].values.astype(int)
breadth_arr = vni["breadth"].values.astype(float)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
spy = n/(cal_days/365.25)

pe_use = pe.copy(); pe_use[pe_q > 2] = np.nan

# ════════════════════ INDICATORS ════════════════════
print("Computing indicators ...")
p3m = np.full(n, np.nan); p1m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60] - 1
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20] - 1
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

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

hl = high - low
mfm = np.where(hl>0, ((close-low)-(high-close))/np.where(hl>0,hl,1), 0)
mfv = mfm * vol_
cmf = np.full(n, np.nan)
for i in range(14, n):
    s_v = np.sum(vol_[i-14:i])
    if s_v>0: cmf[i] = np.sum(mfv[i-14:i])/s_v

def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        h = arr[:t+1]; v = h[~np.isnan(h)]
        if len(v)<min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(v <= arr[t])/len(v)
    return out

print("Computing factor ranks ...")
factor_arrs = {"P3M":p3m, "P1M":p1m, "MA200":ma200_dev, "RSI":rsi, "MACD":macd_hist, "CMF":cmf, "Breadth":breadth_arr}
ranks_base = {k: expanding_pct_rank(factor_arrs[k], MIN_LB) for k in W_BASE_7}
neg_pe = -pe_use
rank_PE = expanding_pct_rank(neg_pe, MIN_LB)

def composite_score(wpe):
    if wpe > 0:
        w = {k: W_BASE_7[k]*(1-wpe) for k in W_BASE_7}
        w["PE"] = wpe
        rmap = dict(ranks_base); rmap["PE"] = rank_PE
        keys = list(w.keys())
    else:
        w = dict(W_BASE_7); rmap = ranks_base; keys = list(w.keys())
    s = np.full(n, np.nan)
    for t in range(n):
        avail = {k: rmap[k][t] for k in keys if not np.isnan(rmap[k][t])}
        if len(avail) < MIN_FACTORS: continue
        ws = sum(w[k] for k in avail)
        s[t] = sum(avail[k]*w[k] for k in avail)/ws
    return s

# ════════════════════ PE Bull Signals ════════════════════
# S2_bull = PE 6M slope < -0.10%/day (-25%/yr)
print("Computing PE bull signals ...")
pe_slope = np.full(n, np.nan)
SLOPE_WIN = 120
for t in range(SLOPE_WIN, n):
    if pe_q[t] > 2: continue
    seg = pe_use[t-SLOPE_WIN+1:t+1]
    valid = ~np.isnan(seg)
    if valid.sum() >= 60:
        x = np.arange(SLOPE_WIN)[valid]; y = seg[valid]
        if len(x) > 1 and np.var(x) > 0:
            slope = (np.mean(x*y) - np.mean(x)*np.mean(y)) / np.var(x)
            pe_slope[t] = slope / np.nanmean(seg)
s2_bull = (pe_slope < -0.0010) & ~np.isnan(pe_slope)

# S1_bull = PE z-score < -1.5 sustained 30d
pe_z = np.full(n, np.nan)
ZW = 5*252
for t in range(n):
    if pe_q[t] > 2: continue
    lo = max(0, t-ZW+1)
    h = pe_use[lo:t+1]; v = h[~np.isnan(h)]
    if len(v) >= 60:
        mu = np.mean(v); sd = np.std(v)
        if sd > 0 and not np.isnan(pe_use[t]):
            pe_z[t] = (pe_use[t]-mu)/sd
s1_bull = np.zeros(n, dtype=bool); st = 0
for i in range(n):
    if not np.isnan(pe_z[i]) and pe_z[i] < -1.5: st += 1
    else: st = 0
    if st >= 30: s1_bull[i] = True

# S4_bull = PE/MA5Y < 0.80 sustained 20d
pe_ma5y = pd.Series(pe_use).rolling(5*252, min_periods=252).mean().values
pe_ratio = pe_use / pe_ma5y
s4_bull_raw = (pe_ratio < 0.80) & ~np.isnan(pe_ratio)
s4_bull = np.zeros(n, dtype=bool); st = 0
for i in range(n):
    if s4_bull_raw[i]: st += 1
    else: st = 0
    if st >= 20: s4_bull[i] = True

print(f"  S1_bull={s1_bull.sum()}  S2_bull={s2_bull.sum()}  S4_bull={s4_bull.sum()}")

# ════════════════════ BUILD STATE PIPELINE ════════════════════
def roll_max(a,w): return pd.Series(a).rolling(w, min_periods=1).max().values
def roll_min(a,w): return pd.Series(a).rolling(w, min_periods=1).min().values
def arg_close_max(rsi_a, c_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = c_a[lo+k]
    return out
def arg_macd_max(rsi_a, m_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmax(seg)); out[i] = m_a[lo+k]
    return out
def arg_close_min(rsi_a, c_a, w):
    out = np.full(len(rsi_a), np.nan)
    for i in range(len(rsi_a)):
        lo = max(0, i-w+1); seg = rsi_a[lo:i+1]
        if np.all(np.isnan(seg)): continue
        k = int(np.nanargmin(seg)); out[i] = c_a[lo+k]
    return out

D_RSI = rsi
D_RSI_T1W = np.concatenate([[np.nan]*5, D_RSI[:-5]])
D_RSI_Max1W = roll_max(D_RSI,5); D_RSI_Max3M = roll_max(D_RSI,60)
D_RSI_Min1W = roll_min(D_RSI,5); D_RSI_Min3M = roll_min(D_RSI,60)
D_RSI_Max1W_C = arg_close_max(D_RSI, close, 5); D_RSI_Max3M_C = arg_close_max(D_RSI, close, 60)
D_RSI_Max1W_M = arg_macd_max(D_RSI, macd_hist, 5); D_RSI_Max3M_M = arg_macd_max(D_RSI, macd_hist, 60)
D_RSI_Min1W_C = arg_close_min(D_RSI, close, 5)
D_RSI_MinT3 = roll_min(D_RSI, 3)
C_L1W = close/np.where(roll_min(close,5)>0, roll_min(close,5), 1)
C_L1M = close/np.where(roll_min(close,20)>0, roll_min(close,20), 1)
mask_d = (vni["time"]>=DVG_MASK_START).values

with np.errstate(divide='ignore', invalid='ignore'):
    bear1 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044) & (D_RSI_Max3M>0.74) &
             (D_RSI_Max1W<0.72) & (D_RSI_Max1W>0.61) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.028) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.11) &
             (macd_hist<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.96) &
             (D_RSI_MinT3>0.43) & (cmf<0.13) & mask_d)
    bear2 = ((D_RSI_Max1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016) & (D_RSI_Max3M>0.77) &
             (D_RSI_Max1W<0.79) & (D_RSI_Max1W>0.60) &
             (D_RSI_Max1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>1.008) &
             (D_RSI_Max3M_M/np.where(D_RSI_Max1W_M!=0,D_RSI_Max1W_M,np.nan)>1.10) &
             (macd_hist<0) & (close/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)>0.97) &
             (D_RSI_MinT3>0.50) & (cmf<0.15) & mask_d)
    bull1 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.90) & (D_RSI_Min1W<0.60) &
             (D_RSI_Min3M<0.40) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.15) &
             (macd_hist>0) & (D_RSI_MinT3<0.50) & (D_RSI_Max1W<0.48) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.12) & (cmf>0) &
             (C_L1M<1.21) & (C_L1W<1.05) & mask_d)
    bull2 = ((D_RSI_Min1W/np.where(D_RSI_Min3M>0,D_RSI_Min3M,np.nan)>0.92) & (D_RSI_Min1W<0.52) &
             (D_RSI_Min3M<0.38) & (D_RSI_Min1W_C/np.where(D_RSI_Max3M_C>0,D_RSI_Max3M_C,np.nan)<1.10) &
             (macd_hist>0) & (D_RSI_MinT3<0.56) & (D_RSI_Max1W<0.64) &
             (D_RSI/np.where(D_RSI_T1W>0,D_RSI_T1W,np.nan)>1.10) & (cmf>0) &
             (C_L1M<1.20) & (C_L1W<1.025) & mask_d)
bear_rsi = np.nan_to_num(bear1,nan=0).astype(bool) | np.nan_to_num(bear2,nan=0).astype(bool)
bull_rsi = np.nan_to_num(bull1,nan=0).astype(bool) | np.nan_to_num(bull2,nan=0).astype(bool)

# Risk overrides shared
rmx = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd_arr = np.where(rmx>0, close/rmx-1, 0.0)
daily_ret = np.full(n, np.nan)
for i in range(1,n):
    if close[i-1]>0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20,n):
    w_ = daily_ret[i-20:i]; v_ = w_[~np.isnan(w_)]
    if len(v_)>=15: vol20[i] = np.std(v_)*np.sqrt(spy)
avg_vol = np.full(n, np.nan)
for t in range(n):
    h = vol20[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: avg_vol[t] = np.mean(v)

pe_p90_exp = np.full(n, np.nan); pe_p85_roll = np.full(n, np.nan)
for t in range(n):
    h = pe_use[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p90_exp[t] = np.nanpercentile(v, 90)
    lo = max(0, t-5*252+1); h2 = pe_use[lo:t+1]; v2 = h2[~np.isnan(h2)]
    if len(v2)>=60: pe_p85_roll[t] = np.nanpercentile(v2, 85)
pe_high = np.zeros(n, dtype=bool)
for t in range(n):
    if pe_q[t] > 2 or np.isnan(pe_use[t]): continue
    if ((not np.isnan(pe_p90_exp[t]) and pe_use[t] > pe_p90_exp[t]) or
        (not np.isnan(pe_p85_roll[t]) and pe_use[t] > pe_p85_roll[t])):
        pe_high[t] = True

E2 = np.zeros(n, dtype=bool)
for i in range(5, n):
    if (dd_arr[i] < -0.15 and close[i] > close[i-5]*1.05
        and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
        and rsi[i] > rsi[i-5]*1.15
        and not np.isnan(cmf[i]) and cmf[i] > 0):
        E2[i] = True

def build_state(wpe, bull_extras):
    """Build v2g_pe state with composite weight + additional bull-exit signals."""
    score = composite_score(wpe)
    rs = expanding_pct_rank(score, MIN_LB)
    rs_ema = np.full(n, np.nan)
    for t in range(n):
        v = rs[t]; prev = rs_ema[t-1] if t>0 else np.nan
        if np.isnan(v): rs_ema[t]=prev
        elif np.isnan(prev): rs_ema[t]=v
        else: rs_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev
    def cls(r):
        if np.isnan(r): return 3
        if r<0.10: return 1
        if r<0.20: return 2
        if r<0.70: return 3
        if r<0.90: return 4
        return 5
    state_raw = np.array([cls(r) for r in rs_ema])

    state_ov = state_raw.copy()
    for i in range(n):
        s = state_ov[i]
        if pe_high[i] and s == 5: s = 4
        if dd_arr[i] < -0.25 and s >= 4: s = 3
        if not np.isnan(avg_vol[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol[i] and s==5: s=4
        state_ov[i] = s

    bull_extra = np.zeros(n, dtype=bool)
    for be in bull_extras:
        bull_extra |= be

    state_g = state_ov.copy()
    ga = False; gs = -1
    for i in range(n):
        if bear_rsi[i]:
            if not ga: ga = True; gs = i
            else: gs = i
        if ga:
            if state_g[i] > 1: state_g[i] = 1
            if (i - gs) >= GATE_MIN_DUR:
                if bull_rsi[i] or E2[i] or bull_extra[i]:
                    ga = False
    return state_g, rs_ema

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

def metrics(pv, dates, i0=None, i1=None):
    a = np.asarray(pv, float)
    if i0 is None: i0 = 0
    if i1 is None: i1 = len(a)-1
    a = a[i0:i1+1]; valid = np.where(a>0)[0]
    if len(valid)<2: return {}
    j0, j1 = valid[0], valid[-1]
    yrs = (dates.iloc[i0+j1] - dates.iloc[i0+j0]).days/365.25
    cagr = (a[j1]/a[j0])**(1/yrs)-1 if yrs>0 else 0
    sub = a[j0:j1+1]; rets = np.diff(sub)/sub[:-1]
    spy_ = (len(sub)-1)/yrs if yrs>0 else 252
    sh = np.mean(rets)*spy_/(np.std(rets)*np.sqrt(spy_)) if np.std(rets)>0 else 0
    rm = np.maximum.accumulate(sub); ddx = sub/rm - 1
    mdd = float(np.min(ddx)); cal = cagr/abs(mdd) if mdd<0 else np.inf
    return {"cagr":cagr, "sharpe":sh, "max_dd":mdd, "calmar":cal, "final":a[j1]/a[j0]}

def slice_pv(pv, i0):
    p = pv[i0:].copy().astype(float)
    if p[0]>0: p = p/p[0]*1e9
    return p

dates = vni["time"]
i_07 = int(np.argmax(dates >= pd.Timestamp("2007-01-01")))
i_11 = int(np.argmax(dates >= pd.Timestamp("2011-01-01")))
d_07 = dates.iloc[i_07:].reset_index(drop=True)
d_11 = dates.iloc[i_11:].reset_index(drop=True)

# ════════════════════ BUILD VARIANTS ════════════════════
print("Building variants ...")
variants = {
    "ref (v2g_pe)":          (0.00, []),
    "pe3a (comp 0.03)":      (0.03, []),
    "pe3b (S2_bull)":        (0.00, [s2_bull]),
    "pe3c (comp 0.03 + S2_bull)":     (0.03, [s2_bull]),
    "pe3d (comp 0.03 + S2 + S4)":     (0.03, [s2_bull, s4_bull]),
    "pe3e (comp 0.05 + S2)":          (0.05, [s2_bull]),
    "pe3f (comp 0.03 + S1+S2+S4)":    (0.03, [s1_bull, s2_bull, s4_bull]),
}
states = {}
pvs = {}
for nm, (wpe, bulls) in variants.items():
    st, _ = build_state(wpe, bulls)
    pv = backtest(st)
    states[nm] = st; pvs[nm] = pv

# ════════════════════ REPORT ════════════════════
print("\n" + "="*135)
print("v2g_pe3 VARIANTS — additivity test")
print("="*135)
ref_pv = pvs["ref (v2g_pe)"]
ref_full = metrics(ref_pv, dates)
ref_07 = metrics(slice_pv(ref_pv, i_07), d_07)
ref_11 = metrics(slice_pv(ref_pv, i_11), d_11)

print(f"{'variant':<32} | {'FULL':<55} | {'Δ vs ref':<22} | {'2011+ delta':<14}")
print("-"*135)
for nm in variants.keys():
    pv = pvs[nm]
    m_f = metrics(pv, dates)
    m_07 = metrics(slice_pv(pv, i_07), d_07)
    m_11 = metrics(slice_pv(pv, i_11), d_11)
    d_cagr = (m_f["cagr"] - ref_full["cagr"])*100
    d_sh   = m_f["sharpe"] - ref_full["sharpe"]
    d_07_cagr = (m_07["cagr"] - ref_07["cagr"])*100
    d_11_cagr = (m_11["cagr"] - ref_11["cagr"])*100
    print(f"  {nm:<30} | CAGR={m_f['cagr']*100:5.2f}% Sh={m_f['sharpe']:.2f} DD={m_f['max_dd']*100:5.1f}% ×{m_f['final']:5.2f} | ΔCAGR{d_cagr:+5.2f}pp Sh{d_sh:+.2f} | 2007+Δ{d_07_cagr:+.2f}pp 2011+Δ{d_11_cagr:+.2f}pp")

# Additivity check
ind_a = (metrics(pvs["pe3a (comp 0.03)"], dates)["cagr"] - ref_full["cagr"])*100
ind_b = (metrics(pvs["pe3b (S2_bull)"], dates)["cagr"] - ref_full["cagr"])*100
combo = (metrics(pvs["pe3c (comp 0.03 + S2_bull)"], dates)["cagr"] - ref_full["cagr"])*100
print(f"\n--- Additivity test (FULL CAGR delta) ---")
print(f"  pe3a alone     : +{ind_a:.3f}pp")
print(f"  pe3b alone     : +{ind_b:.3f}pp")
print(f"  sum if additive: +{ind_a+ind_b:.3f}pp")
print(f"  pe3c combined  : +{combo:.3f}pp")
synergy = combo - (ind_a + ind_b)
print(f"  synergy        : {synergy:+.3f}pp  ({'positive' if synergy>0 else 'negative'} interaction)")

# ════════════════════ QWF ════════════════════
print("\n" + "="*100)
print("QWF trailing-3Y MEDIAN across 65 quarters (2010-2026)")
print("="*100)
qends = pd.date_range(start="2010-03-31", end=dates.iloc[-1], freq="QE")
qrows = []
pv_bh = np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
for qe in qends:
    arr = np.where(dates <= qe)[0]
    if len(arr)==0: continue
    ei = arr[-1]; end_t = dates.iloc[ei]; start_t = end_t - pd.DateOffset(years=3)
    si_arr = np.where(dates >= start_t)[0]
    if len(si_arr) == 0: continue
    si = si_arr[0]
    if ei - si < 30: continue
    row = {"q_end": qe.strftime("%Y-%m-%d")}
    for nm, pvx in pvs.items():
        m = metrics(pvx, dates, si, ei)
        if m:
            row[f"{nm}_cagr"] = m["cagr"]*100
            row[f"{nm}_sh"]   = m["sharpe"]
            row[f"{nm}_dd"]   = m["max_dd"]*100
            row[f"{nm}_cm"]   = m["calmar"]
    m_bh = metrics(pv_bh, dates, si, ei)
    if m_bh: row["bh_cagr"] = m_bh["cagr"]*100
    qrows.append(row)
qdf = pd.DataFrame(qrows)
qdf.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe3_qwf.csv"), index=False)

print(f"{'variant':<32} {'CAGR med':>10} {'Sh med':>8} {'DD med':>9} {'GREEN':>6} {'YELLOW':>7} {'RED':>5}")
for nm in variants.keys():
    c_col = f"{nm}_cagr"; d_col = f"{nm}_dd"
    if c_col not in qdf.columns: continue
    c_med = qdf[c_col].dropna().median()
    s_med = qdf[f"{nm}_sh"].dropna().median()
    d_med = qdf[d_col].dropna().median()
    g = y = r = 0
    for _, rr in qdf.iterrows():
        cc = rr.get(c_col, np.nan); dd_ = rr.get(d_col, np.nan); bh = rr.get("bh_cagr", np.nan)
        if pd.isna(cc) or pd.isna(bh): continue
        if cc > bh and dd_ > -25: g += 1
        elif (cc < bh - 5) or dd_ < -25: r += 1
        else: y += 1
    print(f"  {nm:<30} {c_med:>9.2f}% {s_med:>8.2f} {d_med:>8.2f}% {g:>5} {y:>6} {r:>4}")

# Save winning state history
winner = "pe3c (comp 0.03 + S2_bull)"
st_win = states[winner]
out_df = pd.DataFrame({
    "time": vni["time"], "Close": close,
    "state_v2g_pe3": st_win, "pe": pe, "pe_quality": pe_q,
    "s2_bull": s2_bull.astype(int),
    "pv_v2g_pe3": pvs[winner],
    "pv_ref": pvs["ref (v2g_pe)"],
    "pv_bh": pv_bh,
})
out_df.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe3_history.csv"), index=False)
print(f"\nSaved winner ({winner}) → vnindex_5state_v2g_pe3_history.csv")
