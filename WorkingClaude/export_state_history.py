# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

breadth_path = os.path.join(WORKDIR, "data/breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    vni = vni.merge(breadth, on="time", how="left")
else:
    vni["breadth"] = np.nan

close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n     = len(close)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = n / (cal_days / 365.25)

W = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB = 252

p3m = np.full(n, np.nan)
for i in range(60, n):
    if close[i-60] > 0: p3m[i] = close[i]/close[i-60]-1

p1m = np.full(n, np.nan)
for i in range(20, n):
    if close[i-20] > 0: p1m[i] = close[i]/close[i-20]-1

ma200     = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan
for i in range(1, n):
    diff = close[i]-close[i-1]; u = max(diff,0); d = max(-diff,0)
    if np.isnan(avg_u):
        if i >= 14:
            avg_u = np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            avg_d = np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if avg_u+avg_d > 0: rsi[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u=(avg_u*13+u)/14; avg_d=(avg_d*13+d)/14
        if avg_u+avg_d > 0: rsi[i] = avg_u/(avg_u+avg_d)

ema12=np.full(n,np.nan); ema26=np.full(n,np.nan); sig=np.full(n,np.nan); macd_hist=np.full(n,np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    ema12[i] = close[i] if (i==0 or np.isnan(ema12[i-1])) else ema12[i-1]*(1-k12)+close[i]*k12
    ema26[i] = close[i] if (i==0 or np.isnan(ema26[i-1])) else ema26[i-1]*(1-k26)+close[i]*k26
    ml = ema12[i]-ema26[i]
    sig[i] = ml if (i==0 or np.isnan(sig[i-1])) else sig[i-1]*(1-k9)+ml*k9
    if i >= 33: macd_hist[i] = ml-sig[i]

hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0); mfv=mfm*vol
cmf=np.full(n,np.nan)
for i in range(14, n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfv[i-14:i])/vs

breadth_arr = vni["breadth"].values if "breadth" in vni.columns else np.full(n,np.nan)
raw_factors = {"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":breadth_arr}

def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) >= min_lb: out[t] = np.sum(valid<=arr[t])/len(valid)
    return out

ranks = {k: expanding_pct_rank(v, MIN_LB) for k,v in raw_factors.items()}
MIN_FACTORS = 3
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(avail) >= MIN_FACTORS:
        w_sum = sum(W[k] for k in avail)
        score[t] = sum(avail[k]*W[k] for k in avail)/w_sum

r_score = expanding_pct_rank(score, MIN_LB)
EMA_ALPHA = 0.40
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; prev = r_score_ema[t-1] if t>0 else np.nan
    r_score_ema[t] = (v if np.isnan(prev) else prev if np.isnan(v) else EMA_ALPHA*v+(1-EMA_ALPHA)*prev)

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10:    return 1
    elif rs < 0.20:  return 2
    elif rs < 0.70:  return 3
    elif rs < 0.90:  return 4
    else:            return 5

state_raw = np.array([classify_raw(r) for r in r_score_ema])

pe_arr = vni["VNINDEX_PE"].values.copy()
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: pe_p90[t] = np.nanpercentile(valid, 90)

running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max>0, close/running_max-1, 0.0)

daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1]>0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    w = daily_ret[i-20:i]; valid = w[~np.isnan(w)]
    if len(valid) >= 15: vol20[i] = np.std(valid)*np.sqrt(sessions_per_year)

avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist = vol20[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: avg_vol_exp[t] = np.mean(valid)

state_after_override = state_raw.copy()
for i in range(n):
    s = state_after_override[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s==5): s=4
    if dd[i] < -0.25 and s >= 4: s=3
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol_exp[i] and s==5): s=4
    state_after_override[i] = s

def _s(col): return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)
_D_RSI=_s("D_RSI"); _D_RSI_T1W=_s("D_RSI_T1W")
_D_RSI_Max1W=_s("D_RSI_Max1W"); _D_RSI_Max3M=_s("D_RSI_Max3M")
_D_RSI_Min1W=_s("D_RSI_Min1W"); _D_RSI_Min3M=_s("D_RSI_Min3M")
_D_RSI_Max1W_C=_s("D_RSI_Max1W_Close"); _D_RSI_Max3M_C=_s("D_RSI_Max3M_Close")
_D_RSI_Max3M_M=_s("D_RSI_Max3M_MACD"); _D_RSI_Max1W_M=_s("D_RSI_Max1W_MACD")
_D_RSI_Min1W_C=_s("D_RSI_Min1W_Close"); _D_RSI_MinT3=_s("D_RSI_MinT3")
_D_MACDdiff=_s("D_MACDdiff"); _D_CMF=_s("D_CMF")
_C_L1M=_s("C_L1M"); _C_L1W=_s("C_L1W")
_mask_2011 = vni["time"] >= "2011-01-01"

bear_mask = (
    ((_D_RSI_Max1W/_D_RSI>1.044)&(_D_RSI_Max3M>0.74)&(_D_RSI_Max1W<0.72)&(_D_RSI_Max1W>0.61)&
     (_D_RSI_Max1W_C/_D_RSI_Max3M_C>1.028)&(_D_RSI_Max3M_M/_D_RSI_Max1W_M>1.11)&(_D_MACDdiff<0)&
     (vni["Close"]/_D_RSI_Max3M_C>0.96)&(_D_RSI_MinT3>0.43)&(_D_CMF<0.13)&_mask_2011)
    |
    ((_D_RSI_Max1W/_D_RSI>1.016)&(_D_RSI_Max3M>0.77)&(_D_RSI_Max1W<0.79)&(_D_RSI_Max1W>0.60)&
     (_D_RSI_Max1W_C/_D_RSI_Max3M_C>1.008)&(_D_RSI_Max3M_M/_D_RSI_Max1W_M>1.10)&(_D_MACDdiff<0)&
     (vni["Close"]/_D_RSI_Max3M_C>0.97)&(_D_RSI_MinT3>0.50)&(_D_CMF<0.15)&_mask_2011)
).values.astype(bool)

bull_mask = (
    ((_D_RSI_Min1W/_D_RSI_Min3M>0.90)&(_D_RSI_Min1W<0.60)&(_D_RSI_Min3M<0.40)&
     (_D_RSI_Min1W_C/_D_RSI_Max3M_C<1.15)&(_D_MACDdiff>0)&(_D_RSI_MinT3<0.50)&
     (_D_RSI_Max1W<0.48)&(_D_RSI/_D_RSI_T1W>1.12)&(_D_CMF>0)&(_C_L1M<1.21)&(_C_L1W<1.05)&_mask_2011)
    |
    ((_D_RSI_Min1W/_D_RSI_Min3M>0.92)&(_D_RSI_Min1W<0.52)&(_D_RSI_Min3M<0.38)&
     (_D_RSI_Min1W_C/_D_RSI_Max3M_C<1.10)&(_D_MACDdiff>0)&(_D_RSI_MinT3<0.56)&
     (_D_RSI_Max1W<0.64)&(_D_RSI/_D_RSI_T1W>1.10)&(_D_CMF>0)&(_C_L1M<1.20)&(_C_L1W<1.025)&_mask_2011)
).values.astype(bool)

pe_rank_arr = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    v = pe_arr[:t+1]; v = v[~np.isnan(v)]
    if len(v) >= 60: pe_rank_arr[t] = np.sum(v<=pe_arr[t])/len(v)

p3m_rank_arr = ranks["P3M"]
_rscore_streak = np.zeros(n, dtype=bool); _streak = 0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i]>0.65: _streak += 1
    else: _streak = 0
    if _streak >= 10: _rscore_streak[i] = True

GATE_FLOOR=1; GATE_MIN_DUR=60
gate_active=False; gate_start=-1; gate_flag=np.zeros(n,dtype=int)
state_dvg=state_after_override.copy()

for i in range(n):
    if bear_mask[i]:
        if not gate_active: gate_active=True; gate_start=i
        else: gate_start=i
    if gate_active:
        gate_flag[i]=1
        if state_dvg[i]>GATE_FLOOR: state_dvg[i]=GATE_FLOOR
        sessions_in=i-gate_start
        if sessions_in>=GATE_MIN_DUR:
            _bull_ok=bool(bull_mask[i])
            _p3m_ok=(not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i]>0.45
            _pe_ok=(not np.isnan(pe_rank_arr[i])) and pe_rank_arr[i]<0.80
            _rs_ok=bool(_rscore_streak[i])
            if _bull_ok or (_p3m_ok and _pe_ok) or _rs_ok:
                gate_active=False

def rolling_mode(states, window=15):
    out=states.copy()
    for t in range(window-1, len(states)):
        w=states[t-window+1:t+1]
        vals,counts=np.unique(w,return_counts=True)
        cands=vals[counts==counts.max()]
        for v in reversed(w):
            if v in cands: out[t]=v; break
    return out

def min_stay_filter(states, min_days=7):
    out=states.copy(); changed=True
    while changed:
        changed=False; i=0
        while i<len(out):
            j=i+1
            while j<len(out) and out[j]==out[i]: j+=1
            if j-i<min_days:
                fill=out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j]=fill; changed=True
            i=j
    return out

state_mode   = rolling_mode(state_dvg, 15)
state_smooth = min_stay_filter(state_mode, 7)

STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
vni["state"]      = state_smooth
vni["state_name"] = [STATE_NAMES[s] for s in state_smooth]
vni["r_score_ema"] = r_score_ema

# Export full state history
out_df = vni[["time","Close","VNINDEX_PE","state","state_name","r_score_ema"]].copy()
out_path = os.path.join(WORKDIR, "data/vnindex_state_history.csv")
out_df.to_csv(out_path, index=False)
print(f"Exported {len(out_df)} rows to vnindex_state_history.csv")

# Phân tích từ 2014 (trùng với simulation Init)
df = out_df[out_df["time"] >= "2014-01-01"].copy().reset_index(drop=True)
total_days = len(df)

print(f"\n=== PHÂN TÍCH STATE (2014-01-01 den hien tai) ===")
print(f"Total trading days: {total_days}")
for s in [1,2,3,4,5]:
    cnt = (df["state"]==s).sum()
    print(f"  {STATE_NAMES[s]:<10}: {cnt:5d} ngay  ({cnt/total_days*100:.1f}%)")

# Build segments
print(f"\n=== SEGMENTS CRISIS & BEAR (2014+) ===")
segments = []
prev_s = df["state"].iloc[0]; seg_start_idx = 0
for i in range(1, len(df)):
    if df["state"].iloc[i] != prev_s:
        segments.append({"state": prev_s, "start": df["time"].iloc[seg_start_idx], "end": df["time"].iloc[i-1]})
        seg_start_idx = i; prev_s = df["state"].iloc[i]
segments.append({"state": prev_s, "start": df["time"].iloc[seg_start_idx], "end": df["time"].iloc[-1]})

crisis_bear_segs = [s for s in segments if s["state"] in [1,2]]
for s in crisis_bear_segs:
    days = len(df[(df["time"]>=s["start"])&(df["time"]<=s["end"])])
    print(f"  {STATE_NAMES[s['state']]:<8} {s['start'].strftime('%Y-%m-%d')} -> {s['end'].strftime('%Y-%m-%d')}  ({days} ngay)")

total_blocked = sum(len(df[(df["time"]>=s["start"])&(df["time"]<=s["end"])]) for s in crisis_bear_segs)
total_crisis  = sum(len(df[(df["time"]>=s["start"])&(df["time"]<=s["end"])]) for s in crisis_bear_segs if s["state"]==1)
total_bear    = sum(len(df[(df["time"]>=s["start"])&(df["time"]<=s["end"])]) for s in crisis_bear_segs if s["state"]==2)
print(f"\n  Tong blocked (CRISIS+BEAR): {total_blocked} ngay ({total_blocked/total_days*100:.1f}%)")
print(f"  CRISIS: {total_crisis} ngay ({total_crisis/total_days*100:.1f}%)")
print(f"  BEAR  : {total_bear} ngay ({total_bear/total_days*100:.1f}%)")

# Overlap với market_eval PE blocks
# PE block hiện tại: VNINDEX_PE >= P60 -> bắt đầu block
# Tính P60 expanding
pe_vals = df["VNINDEX_PE"].values
pe_p60_exp = np.full(len(df), np.nan)
for t in range(len(df)):
    hist = pe_vals[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 20: pe_p60_exp[t] = np.nanpercentile(valid, 60)

df["pe_block"] = (df["VNINDEX_PE"] >= pd.Series(pe_p60_exp, index=df.index))
df["state_block"] = df["state"].isin([1,2])

pe_block_days    = df["pe_block"].sum()
state_block_days = df["state_block"].sum()
both_block       = (df["pe_block"] & df["state_block"]).sum()
only_state       = (~df["pe_block"] & df["state_block"]).sum()
only_pe          = (df["pe_block"] & ~df["state_block"]).sum()

print(f"\n=== OVERLAP PHAN TICH ===")
print(f"  PE block (>=P60 exp):  {pe_block_days} ngay ({pe_block_days/total_days*100:.1f}%)")
print(f"  5-state block (CRISIS/BEAR): {state_block_days} ngay ({state_block_days/total_days*100:.1f}%)")
print(f"  Ca hai block:          {both_block} ngay ({both_block/total_days*100:.1f}%)")
print(f"  Chi 5-state (khong co PE): {only_state} ngay ({only_state/total_days*100:.1f}%) <- ADDED VALUE")
print(f"  Chi PE (khong co 5-state): {only_pe} ngay ({only_pe/total_days*100:.1f}%)")
if state_block_days > 0:
    overlap_pct = both_block/state_block_days*100
    print(f"\n  Overlap rate (5-state bị PE cover): {overlap_pct:.1f}%")
    print(f"  => 5-state them vao {100-overlap_pct:.1f}% ngay CHUA duoc PE cover")
