# -*- coding: utf-8 -*-
"""
vnindex_5state_dual_v3.py
=========================
v3: dynamic-α dual-system on FULL Tinh Tế pipeline.

Architecture:
  - r_score_raw (8 factors): 7 standard + PE-comp w=0.03
  - r_score_ew  (7 factors): standard EW factors (no PE — EW has no natural PE)
  - r_score_dual = α(t) × r_score_raw + (1-α(t)) × r_score_ew
    α(t) = clip(1.0 - 2.0*max(0, c_smooth - 0.5), [0.3, 1.0])
  - EMA(0.40) → classify → risk overrides (PE/DD/Vol)
  - v2g BearDvg gate: min_dur=30, exit on (BullDvg OR E2 capitulation OR S2_bull PE slope)
  - s3 smoothing: rolling_mode(3) + min_stay_filter(2)

Output: vnindex_5state_dual_v3_staging.csv
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

W_BASE_7    = {"P3M":0.30, "P1M":0.10, "MA200":0.15, "RSI":0.15,
               "MACD":0.10, "CMF":0.08, "Breadth":0.12}
W_PE        = float(os.environ.get("W_PE", "0.03"))   # pe3c PE weight (additive); env-overridable
MIN_LB      = 252
MIN_FACTORS = 3
EMA_ALPHA   = 0.40
CONC_EMA    = 0.20
GATE_MIN_V2G = 30    # v2g gate min duration
MODE_WIN_S3 = 3      # s3 smoothing
MIN_STAY_S3 = 2
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
DVG_MASK_START = "2007-01-01"

print("="*70); print("v3 — Dual + Tinh Tế pipeline"); print("="*70)

# ─────────────────────────────────────────────────────────────────────
# Load: cached VNI + EW factors + concentration
# ─────────────────────────────────────────────────────────────────────
print("\n[1] Load cached data")
vni = pd.read_pickle(os.path.join(WORKDIR, "_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

ew_full = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_ew_full.csv"))
ew_full["time"] = pd.to_datetime(ew_full["time"])
ew_full = ew_full.rename(columns={"r_score":"r_score_ew"})

conc = pd.read_csv(os.path.join(WORKDIR, "concentration_history.csv"))
conc["time"] = pd.to_datetime(conc["time"])

# ─────────────────────────────────────────────────────────────────────
# Compute factors on raw VNI (same as v2)
# ─────────────────────────────────────────────────────────────────────
print("[2] Compute raw VNI factors")
close = vni["Close"].values.astype(float)
n = len(close)
spy_per_yr = n / ((vni["time"].iloc[-1] - vni["time"].iloc[0]).days / 365.25)

def lagged_return(arr, k):
    out = np.full(len(arr), np.nan)
    for i in range(k, len(arr)):
        if arr[i-k] > 0 and not np.isnan(arr[i-k]) and not np.isnan(arr[i]):
            out[i] = arr[i]/arr[i-k] - 1
    return out
p3m = lagged_return(close, 60); p1m = lagged_return(close, 20)
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

rsi = np.full(n,np.nan); avg_u=avg_d=np.nan; period=14
for i in range(1, n):
    diff = close[i]-close[i-1]
    if np.isnan(diff): continue
    u = max(diff,0.0); d = max(-diff,0.0)
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

ema12=np.full(n,np.nan); ema26=np.full(n,np.nan); signal=np.full(n,np.nan); macd_hist=np.full(n,np.nan)
k12,k26,k9 = 2/13,2/27,2/10
for i in range(n):
    if np.isnan(close[i]): continue
    if i==0 or np.isnan(ema12[i-1]):
        ema12[i]=close[i]; ema26[i]=close[i]
    else:
        ema12[i] = ema12[i-1]*(1-k12)+close[i]*k12
        ema26[i] = ema26[i-1]*(1-k26)+close[i]*k26
    macd_line = ema12[i]-ema26[i]
    if i==0 or np.isnan(signal[i-1]): signal[i]=macd_line
    else: signal[i] = signal[i-1]*(1-k9)+macd_line*k9
    if i>=33: macd_hist[i] = macd_line - signal[i]

cmf = vni["D_CMF"].values.astype(float)
pe  = vni["VNINDEX_PE"].values.astype(float)

vni["f_P3M"]=p3m; vni["f_P1M"]=p1m; vni["f_MA200"]=ma200_dev
vni["f_RSI"]=rsi; vni["f_MACD"]=macd_hist; vni["f_CMF"]=cmf
vni = vni.merge(ew_full[["time","f_Breadth"]], on="time", how="left")
vni["f_PE"] = pe  # 8th factor

def expanding_pct_rank(arr, min_lb=252):
    arr = np.asarray(arr, dtype=float)
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb: continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

print("[3] Rank 8 factors on raw VNI (with PE-comp)")
FACTOR_KEYS_8 = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth","PE"]
W_8 = dict(W_BASE_7); W_8["PE"] = W_PE
ranks_raw = {}
for k in FACTOR_KEYS_8:
    print(f"  Rank {k} ...")
    ranks_raw[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)

# Score with 8 factors
score_raw = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks_raw[k][t] for k in FACTOR_KEYS_8 if not np.isnan(ranks_raw[k][t])}
    if len(avail) < MIN_FACTORS: continue
    ws = sum(W_8[k] for k in avail)
    score_raw[t] = sum(avail[k]*W_8[k] for k in avail)/ws
r_score_raw = expanding_pct_rank(score_raw, MIN_LB)

# ─────────────────────────────────────────────────────────────────────
# Merge EW + concentration
# ─────────────────────────────────────────────────────────────────────
print("[4] Merge EW r_score + concentration")
df = vni.copy()
df["r_score_raw"] = r_score_raw
df = df.merge(ew_full[["time","r_score_ew"]], on="time", how="left")
df = df.merge(conc[["time","concentration_score"]], on="time", how="left")

# Smooth concentration
cs = df["concentration_score"].values
cs_ema = np.full(len(cs), np.nan)
for t in range(len(cs)):
    v=cs[t]; prev=cs_ema[t-1] if t>0 else np.nan
    if np.isnan(v): cs_ema[t]=prev
    elif np.isnan(prev): cs_ema[t]=v
    else: cs_ema[t] = CONC_EMA*v + (1-CONC_EMA)*prev
df["concentration_smooth"] = cs_ema

# α(c)
def alpha_from_c(c):
    if np.isnan(c): return 1.0
    return max(0.3, min(1.0, 1.0 - 2.0*max(0, c-0.5)))
df["alpha"] = df["concentration_smooth"].apply(alpha_from_c)

# Blend
r_raw = df["r_score_raw"].values; r_ew = df["r_score_ew"].values; a = df["alpha"].values
r_dual = np.where(np.isnan(r_ew), r_raw,
                  np.where(np.isnan(r_raw), r_ew, a*r_raw + (1-a)*r_ew))

# ─────────────────────────────────────────────────────────────────────
# EMA → classify → risk overrides
# ─────────────────────────────────────────────────────────────────────
print("[5] EMA → classify → risk overrides")
rs_ema = np.full(n, np.nan)
for t in range(n):
    v=r_dual[t]; prev=rs_ema[t-1] if t>0 else np.nan
    if np.isnan(v): rs_ema[t]=prev
    elif np.isnan(prev): rs_ema[t]=v
    else: rs_ema[t] = EMA_ALPHA*v + (1-EMA_ALPHA)*prev

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    if rs<0.20: return 2
    if rs<0.70: return 3
    if rs<0.90: return 4
    return 5
state_raw = np.array([classify_raw(r) for r in rs_ema])

pe_p90 = np.full(n, np.nan)
for t in range(n):
    h = pe[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: pe_p90[t] = np.nanpercentile(v, 90)
rmx = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(rmx>0, close/rmx-1, 0.0)
daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1]>0 and not np.isnan(close[i-1]) and not np.isnan(close[i]):
        daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    w = daily_ret[i-20:i]; v = w[~np.isnan(w)]
    if len(v)>=15: vol20[i] = np.std(v)*np.sqrt(spy_per_yr)
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    h = vol20[:t+1]; v = h[~np.isnan(h)]
    if len(v)>=60: avg_vol_exp[t] = np.mean(v)

state_ov = state_raw.copy()
for i in range(n):
    s = state_ov[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe[i]) and pe[i]>pe_p90[i] and s==5: s=4
    if dd[i] < -0.25 and s>=4: s=3
    if not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5: s=4
    state_ov[i] = s

# ─────────────────────────────────────────────────────────────────────
# BearDvg / BullDvg / E2 / S2_bull
# ─────────────────────────────────────────────────────────────────────
print("[6] BearDvg / BullDvg / E2 / S2_bull")
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
mask_d = (df["time"]>=DVG_MASK_START).values

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
bear_mask = np.nan_to_num(bear1,nan=0).astype(bool) | np.nan_to_num(bear2,nan=0).astype(bool)
bull_mask = np.nan_to_num(bull1,nan=0).astype(bool) | np.nan_to_num(bull2,nan=0).astype(bool)

# E2 capitulation
E2 = np.zeros(n, dtype=bool)
for i in range(5, n):
    if (dd[i] < -0.15
        and close[i] > close[i-5]*1.05
        and not np.isnan(rsi[i]) and not np.isnan(rsi[i-5])
        and rsi[i] > rsi[i-5]*1.15
        and not np.isnan(cmf[i]) and cmf[i] > 0):
        E2[i] = True

# S2_bull: PE 6M slope < -25%/yr  (pe3c key signal)
pe_slope = np.full(n, np.nan)
SLOPE_WIN = 120
for t in range(SLOPE_WIN, n):
    seg = pe[t-SLOPE_WIN+1:t+1]
    valid = ~np.isnan(seg)
    if valid.sum() >= 60:
        x = np.arange(SLOPE_WIN)[valid]; y = seg[valid]
        if len(x) > 1 and np.var(x) > 0:
            slope = (np.mean(x*y) - np.mean(x)*np.mean(y)) / np.var(x)
            pe_slope[t] = slope / np.nanmean(seg)
s2_bull = (pe_slope < -0.0010) & ~np.isnan(pe_slope)

print(f"  BearDvg: {bear_mask.sum()} | BullDvg: {bull_mask.sum()} | E2: {E2.sum()} | S2_bull: {s2_bull.sum()}")

# ─────────────────────────────────────────────────────────────────────
# v2g gate: min 30, exit on (BullDvg OR E2 OR S2_bull)
# ─────────────────────────────────────────────────────────────────────
print("[7] v2g gate (min_dur=30, exit=BullDvg|E2|S2_bull)")
state_v2g = state_ov.copy()
ga = False; gs = -1; n_open = n_close = 0
for i in range(n):
    if bear_mask[i]:
        if not ga: ga = True; gs = i; n_open += 1
        else: gs = i
    if ga:
        if state_v2g[i] > 1: state_v2g[i] = 1
        sessions_in = i - gs
        if sessions_in >= GATE_MIN_V2G:
            if bull_mask[i] or E2[i] or s2_bull[i]:
                ga = False; n_close += 1
print(f"  Gate events: {n_open} open / {n_close} close")

# ─────────────────────────────────────────────────────────────────────
# s3 smoothing: mode3 + min_stay2
# ─────────────────────────────────────────────────────────────────────
print("[8] s3 smoothing")
def rolling_mode(states, window):
    if window <= 1: return states.copy()
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand: out[t]=v; break
    return out
def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
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

state_final = rolling_mode(state_v2g, MODE_WIN_S3)
state_final = min_stay_filter(state_final, MIN_STAY_S3)

df["state_raw"] = state_raw
df["state"]     = state_final

# ─────────────────────────────────────────────────────────────────────
# Save + summary
# ─────────────────────────────────────────────────────────────────────
out = pd.DataFrame({
    "time": df["time"].dt.strftime("%Y-%m-%d"),
    "state": df["state"].astype(int),
    "state_raw": df["state_raw"].astype(int),
})
out.to_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_staging.csv"), index=False)

# Full diag
diag = df[["time","Close","concentration_smooth","alpha",
           "r_score_raw","r_score_ew","state_raw","state"]].copy()
diag.to_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"), index=False)

print("\n" + "="*70); print("SUMMARY"); print("="*70)
post = df[df["time"]>="2014-01-01"]
print("\nState distribution (post-2014):")
dist = post["state"].value_counts(normalize=True).sort_index() * 100
for s in [1,2,3,4,5]:
    print(f"  {STATE_NAMES[s]:<10} {dist.get(s, 0.0):>5.1f}%")
def n_trans(s):
    arr = np.asarray(s)
    return int((arr[1:]!=arr[:-1]).sum())
print(f"\nTransitions post-2014: {n_trans(post['state'].values)}")

print("\nLast 15 sessions:")
recent = df.tail(15)[["time","concentration_smooth","alpha","state_raw","state"]].copy()
recent["time"] = recent["time"].dt.strftime("%Y-%m-%d")
for _,r in recent.iterrows():
    print(f"  {r['time']}  c={r['concentration_smooth']:.2f}  α={r['alpha']:.2f}  "
          f"raw={int(r['state_raw'])}  state={STATE_NAMES.get(int(r['state']), '?')}")
print(f"\n→ vnindex_5state_dual_v3_staging.csv")
