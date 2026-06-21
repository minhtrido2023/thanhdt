# -*- coding: utf-8 -*-
"""
vnindex_5state_v2g_pe2.py
=========================
Aggressive PE integration into 5-state system.

Two new mechanisms (on top of v2g_pe):
  A) PE Divergence signals (Bear_PE / Bull_PE) — mirror BearDvg/BullDvg but on PE+Close
     Bear_PE: PE expansion + market making highs → overvaluation alarm → CRISIS-like
     Bull_PE: PE crash + market crash → value extreme → reversal cue
  B) PE as composite factor — add f_PE = -PE to the existing 7-factor stack
     Low PE → high rank → bullish bias (mean-reversion via valuation)

Variants tested:
  v2g_pe        — reference (from previous run)
  v2g_pe2_dvg   — adds PE dvg signals only
  v2g_pe2_cmp_W — adds PE composite with weight W (try 0.05, 0.10, 0.15)
  v2g_pe2_full  — adds both PE dvg + composite (weight 0.10)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ════════════════════ PARAMS ════════════════════
MIN_LB, MIN_FACTORS, EMA_ALPHA = 252, 3, 0.40
RAMP_DAYS, SNAP_THR = 3, 0.03
TC, DEPOSIT_R, BORROW_R = 0.001, 0.06/252, 0.10/252
TARGET_W = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
GATE_MIN_DUR = 30
DVG_MASK_START = "2007-01-01"

# Original 7-factor weights (PE composite scales down proportionally)
W_BASE_7 = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15, "MACD":0.10, "CMF":0.08, "Breadth":0.12}

# PE dvg thresholds
PE_DVG_LOOKBACK = 120        # 6-month lookback
PE_DVG_PE_CHG   = 0.20       # Bear_PE: PE up >20% in 6M
PE_DVG_PX_CHG   = 0.15       # Bear_PE: Close up >15% in 6M
PE_DVG_PE_RANK_H = 0.85      # Bear_PE: PE rank > 0.85
PE_DVG_PX_RANK_H = 0.80      # Bear_PE: Close rank > 0.80
# Bull_PE relaxed (was 0 events with prior thresholds)
BULL_PE_PE_CHG   = -0.20     # PE drop >20% in 6M
BULL_PE_PX_CHG   = -0.15     # Close drop >15% in 6M
BULL_PE_PE_RANK_L = 0.30     # PE rank < 0.30 (was 0.15 — too tight)
BULL_PE_PX_RANK_L = 0.30     # Close rank < 0.30 (was 0.20)

# ════════════════════ LOAD ════════════════════
print("Loading cleaned VNINDEX data ...")
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
print(f"  rows={n}  spy={spy:.1f}")

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

# Mask PE quality 3-4 out of all PE-dependent calcs (composite + dvg)
pe_use = pe.copy()
pe_use[pe_q > 2] = np.nan  # only quality 0-2 enters score / dvg

print("Computing factor ranks (7 base) ...")
ranks_base = {}
factor_arrs = {"P3M":p3m, "P1M":p1m, "MA200":ma200_dev, "RSI":rsi, "MACD":macd_hist, "CMF":cmf, "Breadth":breadth_arr}
for k in W_BASE_7:
    ranks_base[k] = expanding_pct_rank(factor_arrs[k], MIN_LB)

# PE factor = -PE (low PE → high rank)
print("Computing PE factor rank (low PE = high score) ...")
neg_pe = -pe_use
rank_PE = expanding_pct_rank(neg_pe, MIN_LB)
# rank of PE itself (for dvg)
rank_PE_raw = expanding_pct_rank(pe_use, MIN_LB)
# Close rank (for dvg)
rank_Close = expanding_pct_rank(close, MIN_LB)

# Build composite scorer (PE weight = wpe parameter)
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

# ════════════════════ STATE PIPELINE (shared) ════════════════════
def build_state_series(composite_arr, mask_dvg_start, use_pe_dvg=False, gate_min=GATE_MIN_DUR):
    """Build state series from composite score using gate logic."""
    # Composite → r_score → EMA
    rs = expanding_pct_rank(composite_arr, MIN_LB)
    rs_ema = np.full(n, np.nan)
    for t in range(n):
        v = rs[t]; prev = rs_ema[t-1] if t>0 else np.nan
        if np.isnan(v): rs_ema[t]=prev
        elif np.isnan(prev): rs_ema[t]=v
        else: rs_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev
    def classify_raw(r):
        if np.isnan(r): return 3
        if r<0.10: return 1
        if r<0.20: return 2
        if r<0.70: return 3
        if r<0.90: return 4
        return 5
    state_raw = np.array([classify_raw(r) for r in rs_ema])

    # PE high override (Tier 1A+1B from v2g_pe)
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

    # Drawdown + vol overrides
    rmx = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
    dd_arr = np.where(rmx>0, close/rmx-1, 0.0)
    dr = np.full(n, np.nan)
    for i in range(1,n):
        if close[i-1]>0: dr[i] = close[i]/close[i-1]-1
    vol20_a = np.full(n, np.nan)
    for i in range(20,n):
        w_ = dr[i-20:i]; vv = w_[~np.isnan(w_)]
        if len(vv)>=15: vol20_a[i] = np.std(vv)*np.sqrt(spy)
    avg_vol = np.full(n, np.nan)
    for t in range(n):
        h = vol20_a[:t+1]; v = h[~np.isnan(h)]
        if len(v)>=60: avg_vol[t] = np.mean(v)

    state_ov = state_raw.copy()
    for i in range(n):
        s = state_ov[i]
        if pe_high[i] and s == 5: s = 4
        if dd_arr[i] < -0.25 and s >= 4: s = 3
        if not np.isnan(avg_vol[i]) and not np.isnan(vol20_a[i]) and vol20_a[i]>1.5*avg_vol[i] and s==5: s=4
        state_ov[i] = s

    # BearDvg / BullDvg (RSI-based)
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
    mask_d = (vni["time"]>=mask_dvg_start).values

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
    bear_mask_r = np.nan_to_num(bear1,nan=0).astype(bool) | np.nan_to_num(bear2,nan=0).astype(bool)
    bull_mask_r = np.nan_to_num(bull1,nan=0).astype(bool) | np.nan_to_num(bull2,nan=0).astype(bool)

    # PE Divergence signals — only when pe_quality ≤ 2
    bear_pe = np.zeros(n, dtype=bool)
    bull_pe = np.zeros(n, dtype=bool)
    if use_pe_dvg:
        for i in range(PE_DVG_LOOKBACK, n):
            if pe_q[i] > 2 or np.isnan(pe_use[i]): continue
            pe_then = pe_use[i-PE_DVG_LOOKBACK]
            if np.isnan(pe_then) or pe_then == 0: continue
            pe_chg = pe_use[i]/pe_then - 1
            px_chg = close[i]/close[i-PE_DVG_LOOKBACK] - 1
            # Bear_PE: PE up >20% AND Close up >15% AND PE_rank > 0.85 AND Close near peak
            if (pe_chg > PE_DVG_PE_CHG and px_chg > PE_DVG_PX_CHG
                and not np.isnan(rank_PE_raw[i]) and rank_PE_raw[i] > PE_DVG_PE_RANK_H
                and not np.isnan(rank_Close[i]) and rank_Close[i] > PE_DVG_PX_RANK_H):
                bear_pe[i] = True
            # Bull_PE: PE down >20% AND Close down >15% AND PE_rank < 0.15 AND Close near trough
            # Use drawdown instead of expanding Close rank (more robust for capitulation)
            dd_here = dd_arr[i] if "dd_arr" in dir() else None
            # We don't have access to dd_arr here (scope) — use rolling Close min instead
            # Bull_PE: PE drop AND Close drop AND PE rank low AND price clearly below recent max
            if (pe_chg < BULL_PE_PE_CHG and px_chg < BULL_PE_PX_CHG
                and not np.isnan(rank_PE_raw[i]) and rank_PE_raw[i] < BULL_PE_PE_RANK_L):
                # require Close currently in lower-half of 1Y range
                lookback_close = close[max(0, i-252):i+1]
                if len(lookback_close) > 0:
                    cmin = np.nanmin(lookback_close); cmax = np.nanmax(lookback_close)
                    if cmax > cmin:
                        pos = (close[i] - cmin)/(cmax - cmin)
                        if pos < 0.40:  # bottom 40% of 1Y range
                            bull_pe[i] = True

    # E2 capitulation (same as v2g)
    E2 = np.zeros(n, dtype=bool)
    for i in range(5, n):
        if (dd_arr[i] < -0.15 and close[i] > close[i-5]*1.05
            and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
            and rsi[i] > rsi[i-5]*1.15
            and not np.isnan(cmf[i]) and cmf[i] > 0):
            E2[i] = True

    # Gate: enter on (BearDvg OR Bear_PE); exit on (BullDvg OR E2 OR Bull_PE)
    state_g = state_ov.copy()
    ga = False; gs = -1
    for i in range(n):
        enter = bear_mask_r[i] or bear_pe[i]
        if enter:
            if not ga: ga = True; gs = i
            else: gs = i
        if ga:
            if state_g[i] > 1: state_g[i] = 1
            sessions_in = i - gs
            if sessions_in >= gate_min:
                if bull_mask_r[i] or E2[i] or bull_pe[i]:
                    ga = False
    return state_g, rs_ema, bear_mask_r, bull_mask_r, bear_pe, bull_pe

# ════════════════════ BUILD VARIANTS ════════════════════
print("\nBuilding variants ...")
# v2g_pe reference
score_base  = composite_score(0.0)
state_pe_ref, _, _, _, _, _ = build_state_series(score_base, DVG_MASK_START, use_pe_dvg=False)

# v2g_pe2_dvg — adds PE dvg only
print("  v2g_pe2_dvg: composite untouched, +PE dvg")
state_dvg, _, _, _, bear_pe_arr, bull_pe_arr = build_state_series(score_base, DVG_MASK_START, use_pe_dvg=True)
n_bpe = int(bear_pe_arr.sum()); n_blpe = int(bull_pe_arr.sum())
print(f"    Bear_PE events: {n_bpe}  Bull_PE events: {n_blpe}")

# v2g_pe2_cmp_W — PE composite with weight W (no PE dvg)
variants_cmp = {}
for w_pe in [0.03, 0.05, 0.07, 0.10]:
    s = composite_score(w_pe)
    st, _, _, _, _, _ = build_state_series(s, DVG_MASK_START, use_pe_dvg=False)
    variants_cmp[w_pe] = st

# v2g_pe2_full — composite W=0.05 + PE dvg (best W)
score_full = composite_score(0.05)
state_full, _, _, _, _, _ = build_state_series(score_full, DVG_MASK_START, use_pe_dvg=True)

# Bull-only PE dvg variant — adds Bull_PE as gate exit but no Bear_PE entry
def build_state_bullpe_only(composite_arr, mask_dvg_start):
    """Same as build_state_series with use_pe_dvg=True but Bear_PE forced to False."""
    return build_state_series(composite_arr, mask_dvg_start, use_pe_dvg=True)

# Bear-only variant: skip bull_pe by making it never fire (already happens if Bull_PE rare)
# We'll handle this by patching the gate logic inline — not done here. Skip.

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

print("Backtesting ...")
pv_ref = backtest(state_pe_ref)
pv_dvg = backtest(state_dvg)
pv_cmp = {w: backtest(s) for w, s in variants_cmp.items()}
pv_full = backtest(state_full)
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

def slice_pv(pv, i0):
    p = pv[i0:].copy().astype(float)
    if p[0]>0: p = p/p[0]*1e9
    return p

dates = vni["time"]
i_07 = int(np.argmax(dates >= pd.Timestamp("2007-01-01")))
i_11 = int(np.argmax(dates >= pd.Timestamp("2011-01-01")))
d_07 = dates.iloc[i_07:].reset_index(drop=True)
d_11 = dates.iloc[i_11:].reset_index(drop=True)

def report_row(name, pv):
    m_f = metrics(pv, dates)
    m_07 = metrics(slice_pv(pv, i_07), d_07)
    m_11 = metrics(slice_pv(pv, i_11), d_11)
    return f"{name:<22} | FULL: CAGR={m_f['cagr']*100:5.2f}% Sh={m_f['sharpe']:.2f} DD={m_f['max_dd']*100:5.1f}% ×{m_f['final']:5.2f} | 2007+: CAGR={m_07['cagr']*100:5.2f}% Sh={m_07['sharpe']:.2f} DD={m_07['max_dd']*100:5.1f}% | 2011+: CAGR={m_11['cagr']*100:5.2f}% Sh={m_11['sharpe']:.2f} DD={m_11['max_dd']*100:5.1f}%"

print("\n" + "="*180)
print("PE INTEGRATION VARIANTS — backtest comparison")
print("="*180)
print(report_row("v2g_pe (reference)", pv_ref))
print(report_row("v2g_pe2_dvg (+PE dvg)", pv_dvg))
for wpe in [0.03, 0.05, 0.07, 0.10]:
    print(report_row(f"v2g_pe2_cmp_W={wpe:.2f}", pv_cmp[wpe]))
print(report_row("v2g_pe2_full (dvg+W0.05)", pv_full))
print(report_row("B&H", pv_bh))

# ════════════════════ CRISIS lag (since 2007) ════════════════════
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

print("\n" + "="*80)
print("CRISIS lag stats (bottom → exit, since 2007)")
print("="*80)
for name, st in [("v2g_pe (ref)", state_pe_ref), ("v2g_pe2_dvg", state_dvg),
                  ("v2g_pe2_cmp_0.03", variants_cmp[0.03]),
                  ("v2g_pe2_cmp_0.05", variants_cmp[0.05]),
                  ("v2g_pe2_cmp_0.07", variants_cmp[0.07]),
                  ("v2g_pe2_cmp_0.10", variants_cmp[0.10]),
                  ("v2g_pe2_full", state_full)]:
    df_, n_seg = crisis_lag_stats(st)
    if len(df_) == 0: continue
    print(f"  {name:<22} n_segs={n_seg:>3} median_lag={df_['lag'].median():>5.1f} mean_lag={df_['lag'].mean():>5.1f}  median_rally={df_['rally'].median():>5.1f}%")

# ════════════════════ QWF ════════════════════
print("\n" + "="*100)
print("QUARTERLY WALK-FORWARD trailing-3Y (2010-2026)")
print("="*100)
qends = pd.date_range(start="2010-03-31", end=dates.iloc[-1], freq="QE")
rows_q = []
variant_pvs = {
    "ref": pv_ref, "dvg": pv_dvg,
    "cmp03": pv_cmp[0.03], "cmp05": pv_cmp[0.05],
    "cmp07": pv_cmp[0.07], "cmp10": pv_cmp[0.10],
    "full": pv_full, "bh": pv_bh,
}
for qe in qends:
    arr = np.where(dates <= qe)[0]
    if len(arr)==0: continue
    ei = arr[-1]
    row = {"q_end": qe.strftime("%Y-%m-%d")}
    for nm, pvx in variant_pvs.items():
        end_t = dates.iloc[ei]; start_t = end_t - pd.DateOffset(years=3)
        si_arr = np.where(dates >= start_t)[0]
        if len(si_arr) == 0: continue
        si = si_arr[0]
        if ei - si < 30: continue
        m = metrics(pvx, dates, si, ei)
        if m:
            row[f"{nm}_cagr"] = m["cagr"]*100
            row[f"{nm}_sh"]   = m["sharpe"]
            row[f"{nm}_dd"]   = m["max_dd"]*100
            row[f"{nm}_cm"]   = m["calmar"]
    rows_q.append(row)
qdf = pd.DataFrame(rows_q)
qdf.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe2_qwf.csv"), index=False)
print(f"Saved → vnindex_5state_v2g_pe2_qwf.csv  ({len(qdf)} snapshots)")

print(f"\n--- QWF trailing-3Y MEDIAN across {len(qdf)} quarters ---")
print(f"{'variant':<20} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>9} {'Calmar':>8} {'GREEN':>6} {'YELLOW':>7} {'RED':>5}")
for nm, label in [("ref","v2g_pe (ref)"), ("dvg","+PE dvg (B+B)"),
                   ("cmp03","+PE comp W0.03"), ("cmp05","+PE comp W0.05"),
                   ("cmp07","+PE comp W0.07"), ("cmp10","+PE comp W0.10"),
                   ("full","+dvg+comp W0.05"), ("bh","B&H")]:
    c_col = f"{nm}_cagr"; d_col = f"{nm}_dd"
    if c_col not in qdf.columns: continue
    c_med = qdf[c_col].dropna().median()
    s_med = qdf[f"{nm}_sh"].dropna().median()
    d_med = qdf[d_col].dropna().median()
    cm_med = qdf[f"{nm}_cm"].dropna().median()
    # traffic light vs B&H
    if nm == "bh":
        g = y = r = ""
    else:
        g = y = r = 0
        for _, rr in qdf.iterrows():
            cc = rr.get(c_col, np.nan); dd_ = rr.get(d_col, np.nan); bh = rr.get("bh_cagr", np.nan)
            if pd.isna(cc) or pd.isna(bh): continue
            if cc > bh and dd_ > -25: g += 1
            elif (cc < bh - 5) or dd_ < -25: r += 1
            else: y += 1
    print(f"  {label:<18} {c_med:>7.2f}% {s_med:>8.2f} {d_med:>8.2f}% {cm_med:>8.2f}  {str(g):>5} {str(y):>6} {str(r):>4}")

# Save state history
out_df = pd.DataFrame({
    "time": vni["time"], "Close": close,
    "state_pe_ref": state_pe_ref,
    "state_dvg": state_dvg,
    "state_cmp03": variants_cmp[0.03],
    "state_cmp05": variants_cmp[0.05],
    "state_cmp07": variants_cmp[0.07],
    "state_cmp10": variants_cmp[0.10],
    "state_full": state_full,
    "pe": pe, "pe_quality": pe_q,
    "bear_pe": bear_pe_arr.astype(int), "bull_pe": bull_pe_arr.astype(int),
    "pv_ref": pv_ref, "pv_dvg": pv_dvg,
    "pv_cmp03": pv_cmp[0.03], "pv_cmp05": pv_cmp[0.05],
    "pv_cmp07": pv_cmp[0.07], "pv_cmp10": pv_cmp[0.10],
    "pv_full": pv_full, "pv_bh": pv_bh,
})
out_df.to_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_pe2_history.csv"), index=False)
print(f"\nSaved → vnindex_5state_v2g_pe2_history.csv")
