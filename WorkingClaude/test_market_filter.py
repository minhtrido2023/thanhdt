# -*- coding: utf-8 -*-
"""
test_market_filter.py
=====================
1. Test accuracy của MARKET_DICT_FILTER (BearDvg / BullDvg) trên VNINDEX
2. Test nhiều chiến lược kết hợp với 5-state system
3. Chọn alpha tối ưu + integration strategy
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd, os

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
MIN_LB=252; RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001
DEPOSIT_R=0.06/252; BORROW_R=0.10/252
TARGET_W={1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
SPY=243.4
NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ─── Load data ────────────────────────────────────────────────────────────────
vni = pd.read_csv(os.path.join(WORKDIR,"VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
num_cols = ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]
for c in num_cols:
    if c in vni.columns:
        vni[c] = pd.to_numeric(vni[c], errors="coerce")
breadth = pd.read_csv(os.path.join(WORKDIR,"breadth_data.csv"))
breadth["time"] = pd.to_datetime(breadth["time"])
vni = vni.merge(breadth, on="time", how="left")
n = len(vni)
close = vni["Close"].values.copy()
dates = vni["time"].reset_index(drop=True)
print(f"Loaded {n} rows | {dates.iloc[0].date()} → {dates.iloc[-1].date()}")

# ─── PART 1: Apply MARKET_DICT_FILTER conditions ─────────────────────────────
print("\n" + "="*70)
print("PART 1: MARKET_DICT_FILTER signal accuracy")
print("="*70)

def safe(col):
    return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)

D_RSI         = safe("D_RSI")
D_RSI_T1W     = safe("D_RSI_T1W")
D_RSI_Max1W   = safe("D_RSI_Max1W")
D_RSI_Max3M   = safe("D_RSI_Max3M")
D_RSI_Min1W   = safe("D_RSI_Min1W")
D_RSI_Min3M   = safe("D_RSI_Min3M")
D_RSI_Max1W_C = safe("D_RSI_Max1W_Close")
D_RSI_Max3M_C = safe("D_RSI_Max3M_Close")
D_RSI_Max3M_M = safe("D_RSI_Max3M_MACD")
D_RSI_Max1W_M = safe("D_RSI_Max1W_MACD")
D_RSI_MinT3   = safe("D_RSI_MinT3")
D_MACDdiff    = safe("D_MACDdiff")
D_CMF         = safe("D_CMF")
C_L1M         = safe("C_L1M")
C_L1W         = safe("C_L1W")

bear1 = ((D_RSI_Max1W/D_RSI > 1.044) & (D_RSI_Max3M > 0.74) &
         (D_RSI_Max1W < 0.72) & (D_RSI_Max1W > 0.61) &
         (D_RSI_Max1W_C/D_RSI_Max3M_C > 1.028) &
         (D_RSI_Max3M_M/D_RSI_Max1W_M > 1.11) &
         (D_MACDdiff < 0) &
         (vni["Close"]/D_RSI_Max3M_C > 0.96) &
         (D_RSI_MinT3 > 0.43) & (D_CMF < 0.13))

bear2 = ((D_RSI_Max1W/D_RSI > 1.016) & (D_RSI_Max3M > 0.77) &
         (D_RSI_Max1W < 0.79) & (D_RSI_Max1W > 0.60) &
         (D_RSI_Max1W_C/D_RSI_Max3M_C > 1.008) &
         (D_RSI_Max3M_M/D_RSI_Max1W_M > 1.10) &
         (D_MACDdiff < 0) &
         (vni["Close"]/D_RSI_Max3M_C > 0.97) &
         (D_RSI_MinT3 > 0.50) & (D_CMF < 0.15))

bull1 = ((D_RSI_Min1W/D_RSI_Min3M > 0.90) & (D_RSI_Min1W < 0.60) &
         (D_RSI_Min3M < 0.40) & (D_RSI_Min1W_C := safe("D_RSI_Min1W_Close")) is not None and
         True)  # placeholder — compute properly below

# Recompute properly
D_RSI_Min1W_C = safe("D_RSI_Min1W_Close")
bull1 = ((D_RSI_Min1W/D_RSI_Min3M > 0.90) & (D_RSI_Min1W < 0.60) &
         (D_RSI_Min3M < 0.40) & (D_RSI_Min1W_C/D_RSI_Max3M_C < 1.15) &
         (D_MACDdiff > 0) & (D_RSI_MinT3 < 0.50) & (D_RSI_Max1W < 0.48) &
         (D_RSI/D_RSI_T1W > 1.12) & (D_CMF > 0) &
         (C_L1M < 1.21) & (C_L1W < 1.05))

bull2 = ((D_RSI_Min1W/D_RSI_Min3M > 0.92) & (D_RSI_Min1W < 0.52) &
         (D_RSI_Min3M < 0.38) & (D_RSI_Min1W_C/D_RSI_Max3M_C < 1.10) &
         (D_MACDdiff > 0) & (D_RSI_MinT3 < 0.56) & (D_RSI_Max1W < 0.64) &
         (D_RSI/D_RSI_T1W > 1.10) & (D_CMF > 0) &
         (C_L1M < 1.20) & (C_L1W < 1.025))

# Restrict to 2011+ (matching MARKET_DICT_FILTER time condition)
mask_2011 = vni["time"] >= "2011-01-01"
signals = {
    "BearDvg1 (~)": bear1 & mask_2011,
    "BearDvg2 (~)": bear2 & mask_2011,
    "BullDvg1 (_)": bull1 & mask_2011,
    "BullDvg2 (_)": bull2 & mask_2011,
    "BearDvg_ANY":  (bear1 | bear2) & mask_2011,
    "BullDvg_ANY":  (bull1 | bull2) & mask_2011,
}

def forward_return(signal_mask, horizons=[5,10,20,60]):
    rows = vni.index[signal_mask].tolist()
    results = {}
    for h in horizons:
        rets = []
        for idx in rows:
            if idx + h < n and close[idx] > 0:
                rets.append(close[idx+h]/close[idx]-1)
        if rets:
            results[h] = {
                "count": len(rets),
                "mean":  np.mean(rets),
                "median":np.median(rets),
                "win_rate": np.mean([r>0 for r in rets])
            }
    return results

for name, mask in signals.items():
    count = mask.sum()
    if count == 0:
        print(f"\n{name}: 0 signals")
        continue
    fwd = forward_return(mask)
    print(f"\n{name}: {count} signals")
    print(f"  {'Horizon':>8} | {'Count':>5} | {'Mean ret':>8} | {'Median':>8} | {'Win%':>6}")
    for h, r in fwd.items():
        print(f"  {h:>8}d | {r['count']:>5} | {r['mean']:>8.1%} | {r['median']:>8.1%} | {r['win_rate']:>6.0%}")

# ─── PART 2: Build base 5-state scores (reuse from test_alpha.py) ─────────────
print("\n" + "="*70)
print("PART 2: Build base 5-state r_score")
print("="*70)

high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()

p3m = pd.to_numeric(vni["Change_3M"], errors="coerce").values if "Change_3M" in vni.columns else np.full(n,np.nan)
p1m = pd.to_numeric(vni["Change_1M"], errors="coerce").values if "Change_1M" in vni.columns else np.full(n,np.nan)
ma200v = pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev = np.where((ma200v>0)&~np.isnan(ma200v), close/ma200v-1, np.nan)

rsi_c=np.full(n,np.nan); au=ad=np.nan; P=14
for i in range(1,n):
    df2=close[i]-close[i-1]; u=max(df2,0.); d=max(-df2,0.)
    if np.isnan(au):
        if i>=P:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,P+1)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,P+1)])
            if au+ad>0: rsi_c[i]=au/(au+ad)
    else:
        au=(au*(P-1)+u)/P; ad=(ad*(P-1)+d)/P
        if au+ad>0: rsi_c[i]=au/(au+ad)

e12=np.full(n,np.nan); e26=np.full(n,np.nan); sg=np.full(n,np.nan); mh=np.full(n,np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    p2=e12[i-1] if i>0 else np.nan
    e12[i]=close[i] if np.isnan(p2) else p2*(1-k12)+close[i]*k12
    p6=e26[i-1] if i>0 else np.nan
    e26[i]=close[i] if np.isnan(p6) else p6*(1-k26)+close[i]*k26
    ml=e12[i]-e26[i]
    ps=sg[i-1] if i>0 else np.nan
    sg[i]=ml if np.isnan(ps) else ps*(1-k9)+ml*k9
    if i>=33: mh[i]=ml-sg[i]

hl=high-low
with np.errstate(divide="ignore",invalid="ignore"):
    mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.)
cmf_c=np.full(n,np.nan)
mfv=mfm*vol
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf_c[i]=np.sum(mfv[i-14:i])/vs

breadth_arr=pd.to_numeric(vni["breadth"],errors="coerce").values
W_BASE={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
factors={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi_c,"MACD":mh,"CMF":cmf_c,"Breadth":breadth_arr}

def ep_rank(arr,min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        hist=arr[:t+1]; valid=hist[~np.isnan(hist)]
        if len(valid)<min_lb or np.isnan(arr[t]): continue
        out[t]=np.sum(valid<=arr[t])/len(valid)
    return out

print("  Ranking factors (this takes ~30s)...")
ranks={k:ep_rank(factors[k]) for k in factors}
score=np.full(n,np.nan)
for t in range(n):
    avail={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(avail)<3: continue
    ws=sum(W_BASE[k] for k in avail)
    score[t]=sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score=ep_rank(score)
print("  r_score ready.")

pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    v=pe_arr[:t+1]; v=v[~np.isnan(v)]
    if len(v)>=60: pe_p90[t]=np.nanpercentile(v,90)
rm=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd=np.where(rm>0,close/rm-1,0.)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20=np.full(n,np.nan)
for i in range(20,n):
    ww=dr[i-20:i]; vv=ww[~np.isnan(ww)]
    if len(vv)>=15: v20[i]=np.std(vv)*np.sqrt(SPY)
av=np.full(n,np.nan)
for t in range(n):
    vv=v20[:t+1]; vv=vv[~np.isnan(vv)]
    if len(vv)>=60: av[t]=np.mean(vv)

def apply_overrides(states):
    s=states.copy()
    for i in range(n):
        if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s[i]==5: s[i]=4
        if dd[i]<-0.25 and s[i]>=4: s[i]=3
        if not np.isnan(av[i]) and not np.isnan(v20[i]) and v20[i]>1.5*av[i] and s[i]==5: s[i]=4
    return s

def rolling_mode(states,window=15):
    out=states.copy()
    for t in range(window-1,len(states)):
        ww=states[t-window+1:t+1]; vals,counts=np.unique(ww,return_counts=True)
        mc=counts.max(); cands=vals[counts==mc]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out

def classify(rs):
    if np.isnan(rs): return 3
    return 1 if rs<0.10 else 2 if rs<0.20 else 3 if rs<0.70 else 4 if rs<0.90 else 5

def backtest(states):
    pv=np.zeros(n); pv[0]=1e9; w=TARGET_W[3]
    for t in range(1,n):
        tgt=TARGET_W[states[t-1]]; diff=tgt-w
        wn=tgt if abs(diff)<SNAP_THR else w+diff/RAMP_DAYS
        wn=float(np.clip(wn,0,1.30))
        r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.
        pv[t]=pv[t-1]*(1+wn*r+max(0,1-wn)*DEPOSIT_R-max(0,wn-1)*BORROW_R-abs(wn-w)*TC)
        w=wn
    return pv

def metrics(pv, idx0=0):
    idx1=len(pv)-1
    years=(dates.iloc[idx1]-dates.iloc[idx0]).days/365.25
    cagr=(pv[idx1]/pv[idx0])**(1/years)-1 if years>0 else 0
    rets=np.array([pv[i]/pv[i-1]-1 for i in range(idx0+1,idx1+1) if pv[i-1]>0])
    sh=np.mean(rets)*SPY/(np.std(rets)*np.sqrt(SPY)) if np.std(rets)>0 else 0
    mx=np.maximum.accumulate(pv[idx0:]); da=np.where(mx>0,pv[idx0:]/mx-1,0)
    mxdd=da.min(); cal=cagr/abs(mxdd) if mxdd!=0 else 0
    return cagr, mxdd, sh, cal

idx11=vni[vni["time"]>="2011-01-01"].index[0]
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
bh_f=metrics(pv_bh); bh_11=metrics(pv_bh,idx11)

# ─── PART 3: Test integration strategies ──────────────────────────────────────
print("\n" + "="*70)
print("PART 3: Test integration strategies (alpha=0.40, mode=15)")
print("="*70)

ALPHA = 0.40
rs_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; prev=rs_ema[t-1] if t>0 else np.nan
    rs_ema[t]=v if np.isnan(prev) else (prev if np.isnan(v) else ALPHA*v+(1-ALPHA)*prev)

base_raw=np.array([classify(r) for r in rs_ema])
base_ov=apply_overrides(base_raw)
base_sm=rolling_mode(base_ov,15)

# Signal arrays (boolean numpy)
bear_any = (bear1|bear2).values.astype(bool)
bull_any  = (bull1|bull2).values.astype(bool)
bear1_arr = bear1.values.astype(bool)
bear2_arr = bear2.values.astype(bool)
bull1_arr = bull1.values.astype(bool)
bull2_arr = bull2.values.astype(bool)

def apply_dvg_override(base_states, bear_mask, bull_mask, strategy="cap"):
    """
    strategy options:
    'cap'    : BearDvg caps state at NEUTRAL; BullDvg no effect
    'shift'  : BearDvg pushes state down 1; BullDvg pushes state up 1 (max 5, no margin bonus)
    'window' : BearDvg triggers a 20-session cap window; BullDvg triggers 20-session floor
    'combined': BearDvg caps at NEUTRAL; BullDvg allows BULL→EX-BULL upgrade when state=BULL
    """
    s = base_states.copy()
    if strategy == "cap":
        for i in range(n):
            if bear_mask[i] and s[i] >= 4: s[i] = 3
    elif strategy == "shift":
        for i in range(n):
            if bear_mask[i]: s[i] = max(1, s[i]-1)
            if bull_mask[i]: s[i] = min(4, s[i]+1)  # no margin from BullDvg alone
    elif strategy == "window":
        # BearDvg: next 20 sessions capped at NEUTRAL
        # BullDvg: next 20 sessions floor at NEUTRAL
        bear_window = np.zeros(n, dtype=bool)
        bull_window = np.zeros(n, dtype=bool)
        for i in range(n):
            if bear_mask[i]:
                bear_window[i:min(i+20,n)] = True
            if bull_mask[i]:
                bull_window[i:min(i+20,n)] = True
        for i in range(n):
            if bear_window[i] and s[i] >= 4: s[i] = 3
            if bull_window[i] and s[i] <= 2: s[i] = 3
    elif strategy == "combined":
        # BearDvg: cap at NEUTRAL; BullDvg: allow +1 upgrade
        for i in range(n):
            if bear_mask[i] and s[i] >= 4: s[i] = 3
            if bull_mask[i] and s[i] == 3: s[i] = 4  # NEUTRAL→BULL on BullDvg
    return rolling_mode(s, 15)  # re-smooth after modification

strategies = {
    "Base_5state (no dvg)": base_sm,
    "BearDvg_cap":   apply_dvg_override(base_ov, bear_any, bull_any, "cap"),
    "BearDvg_shift": apply_dvg_override(base_ov, bear_any, bull_any, "shift"),
    "BearDvg_window":apply_dvg_override(base_ov, bear_any, bull_any, "window"),
    "Combined_dvg":  apply_dvg_override(base_ov, bear_any, bull_any, "combined"),
}

print(f"\n{'Strategy':>22} | {'CAGR_full':>9} | {'CAGR_2011':>9} | {'MaxDD_11':>8} | {'Sharpe_11':>9} | {'Calmar_11':>9} | {'Trans':>5} | Beat?")
print("-"*100)

best = None
for name, states in strategies.items():
    pv = backtest(states)
    cf,df,sf,calf = metrics(pv)
    c11,d11,s11,cal11 = metrics(pv,idx11)
    trans=sum(1 for i in range(1,n) if states[i]!=states[i-1])
    beat = cf>bh_f[0] and c11>bh_11[0]
    flag = " <<BEST" if beat else (" >full" if cf>bh_f[0] else "")
    if beat and (best is None or c11 > best[1]):
        best = (name, c11, states, pv)
    print(f"{name:>22} | {cf:>9.1%} | {c11:>9.1%} | {d11:>8.1%} | {s11:>9.2f} | {cal11:>9.2f} | {trans:>5d} | {flag}")

print("-"*100)
print(f"{'B&H':>22} | {bh_f[0]:>9.1%} | {bh_11[0]:>9.1%} | {bh_11[1]:>8.1%} | {bh_11[2]:>9.2f} | {bh_11[3]:>9.2f}")

# ─── PART 4: Fine-tune alpha with best integration strategy ───────────────────
print("\n" + "="*70)
print("PART 4: Fine-tune alpha with BearDvg_cap + Combined_dvg")
print("="*70)

print(f"\n{'alpha':>5} | {'Strategy':>15} | {'CAGR_full':>9} | {'CAGR_2011':>9} | {'MaxDD_11':>8} | {'Sharpe_11':>9} | {'Trans':>5} | State_now")
print("-"*100)

for alpha in [0.30, 0.35, 0.40, 0.45, 0.50]:
    rs_e=np.full(n,np.nan)
    for t in range(n):
        v=r_score[t]; prev=rs_e[t-1] if t>0 else np.nan
        rs_e[t]=v if np.isnan(prev) else (prev if np.isnan(v) else alpha*v+(1-alpha)*prev)
    s_raw=np.array([classify(r) for r in rs_e])
    s_ov=apply_overrides(s_raw)
    s_base=rolling_mode(s_ov,15)

    for strat_name, strat_fn in [("BearCap", "cap"), ("Combined", "combined")]:
        s_dvg = apply_dvg_override(s_ov, bear_any, bull_any, strat_fn)
        pv=backtest(s_dvg)
        cf,df,sf,calf=metrics(pv)
        c11,d11,s11,cal11=metrics(pv,idx11)
        trans=sum(1 for i in range(1,n) if s_dvg[i]!=s_dvg[i-1])
        cur=NAMES[s_dvg[-1]]; ema_cur=rs_e[-1]
        beat=cf>bh_f[0] and c11>bh_11[0]
        flag=" <<" if beat else ""
        print(f"{alpha:>5.2f} | {strat_name:>15} | {cf:>9.1%} | {c11:>9.1%} | {d11:>8.1%} | {s11:>9.2f} | {trans:>5d} | {cur} ema={ema_cur:.3f}{flag}")

print("-"*100)
print(f"{'':>5} | {'B&H':>15} | {bh_f[0]:>9.1%} | {bh_11[0]:>9.1%} | {bh_11[1]:>8.1%} | {bh_11[2]:>9.2f}")
print("\n<< = beats B&H in BOTH full period AND since 2011")

# ─── Current MARKET_DICT_FILTER state ─────────────────────────────────────────
print("\n" + "="*70)
print("CURRENT SIGNALS (latest row)")
print("="*70)
latest = vni.iloc[-1]
print(f"Date: {latest['time'].date()} | VNINDEX: {latest['Close']:.2f}")
print(f"  BearDvg1: {bool(bear1.iloc[-1])} | BearDvg2: {bool(bear2.iloc[-1])} | BearDvg_ANY: {bool((bear1|bear2).iloc[-1])}")
print(f"  BullDvg1: {bool(bull1.iloc[-1])} | BullDvg2: {bool(bull2.iloc[-1])} | BullDvg_ANY: {bool((bull1|bull2).iloc[-1])}")
