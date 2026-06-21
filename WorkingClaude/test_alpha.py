# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd, os

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
MIN_LB=252; RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001
DEPOSIT_R=0.06/252; BORROW_R=0.10/252
TARGET_W={1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}
SPY = 243.4  # sessions/year

vni = pd.read_csv(os.path.join(WORKDIR,"VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")
breadth = pd.read_csv(os.path.join(WORKDIR,"breadth_data.csv"))
breadth["time"] = pd.to_datetime(breadth["time"])
vni = vni.merge(breadth, on="time", how="left")

close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n = len(close)

print("Computing base indicators...")
p3m = pd.to_numeric(vni["Change_3M"], errors="coerce").values if "Change_3M" in vni.columns else np.full(n,np.nan)
p1m = pd.to_numeric(vni["Change_1M"], errors="coerce").values if "Change_1M" in vni.columns else np.full(n,np.nan)
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200>0)&~np.isnan(ma200), close/ma200-1, np.nan)

rsi = np.full(n,np.nan); avg_u=avg_d=np.nan; period=14
for i in range(1,n):
    diff=close[i]-close[i-1]; u=max(diff,0.0); d=max(-diff,0.0)
    if np.isnan(avg_u):
        if i>=period:
            avg_u=np.mean([max(close[j]-close[j-1],0) for j in range(1,period+1)])
            avg_d=np.mean([max(close[j-1]-close[j],0) for j in range(1,period+1)])
            if avg_u+avg_d>0: rsi[i]=avg_u/(avg_u+avg_d)
    else:
        avg_u=(avg_u*(period-1)+u)/period; avg_d=(avg_d*(period-1)+d)/period
        if avg_u+avg_d>0: rsi[i]=avg_u/(avg_u+avg_d)

ema12=np.full(n,np.nan); ema26=np.full(n,np.nan); sig=np.full(n,np.nan); mh=np.full(n,np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    p12=ema12[i-1] if i>0 else np.nan
    ema12[i]=close[i] if np.isnan(p12) else p12*(1-k12)+close[i]*k12
    p26=ema26[i-1] if i>0 else np.nan
    ema26[i]=close[i] if np.isnan(p26) else p26*(1-k26)+close[i]*k26
    ml=ema12[i]-ema26[i]
    ps=sig[i-1] if i>0 else np.nan
    sig[i]=ml if np.isnan(ps) else ps*(1-k9)+ml*k9
    if i>=33: mh[i]=ml-sig[i]

hl=high-low
with np.errstate(divide="ignore", invalid="ignore"):
    mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
mfv=mfm*vol
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfv[i-14:i])/vs

breadth_arr = pd.to_numeric(vni["breadth"], errors="coerce").values
W_BASE={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
factors={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":mh,"CMF":cmf,"Breadth":breadth_arr}

def ep_rank(arr, min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        hist=arr[:t+1]; valid=hist[~np.isnan(hist)]
        if len(valid)<min_lb or np.isnan(arr[t]): continue
        out[t]=np.sum(valid<=arr[t])/len(valid)
    return out

print("Ranking factors...")
ranks={k: ep_rank(factors[k]) for k in factors}
score=np.full(n,np.nan)
for t in range(n):
    avail={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(avail)<3: continue
    ws=sum(W_BASE[k] for k in avail)
    score[t]=sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score=ep_rank(score)
print("  r_score computed.")

pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    valid=pe_arr[:t+1]; valid=valid[~np.isnan(valid)]
    if len(valid)>=60: pe_p90[t]=np.nanpercentile(valid,90)
rm=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd=np.where(rm>0,close/rm-1,0.0)
daily_ret=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: daily_ret[i]=close[i]/close[i-1]-1
vol20=np.full(n,np.nan)
for i in range(20,n):
    ww=daily_ret[i-20:i]; v=ww[~np.isnan(ww)]
    if len(v)>=15: vol20[i]=np.std(v)*np.sqrt(SPY)
avg_vol=np.full(n,np.nan)
for t in range(n):
    v=vol20[:t+1]; v=v[~np.isnan(v)]
    if len(v)>=60: avg_vol[t]=np.mean(v)

def apply_overrides(states):
    s=states.copy()
    for i in range(n):
        if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s[i]==5: s[i]=4
        if dd[i]<-0.25 and s[i]>=4: s[i]=3
        if not np.isnan(avg_vol[i]) and not np.isnan(vol20[i]) and vol20[i]>1.5*avg_vol[i] and s[i]==5: s[i]=4
    return s

def rolling_mode(states, window):
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
        r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1+wn*r+max(0,1-wn)*DEPOSIT_R-max(0,wn-1)*BORROW_R-abs(wn-w)*TC)
        w=wn
    return pv

def metrics(pv, dates, idx0=0):
    idx1=len(pv)-1
    years=(dates.iloc[idx1]-dates.iloc[idx0]).days/365.25
    cagr=(pv[idx1]/pv[idx0])**(1/years)-1 if years>0 else 0
    rets=np.array([pv[i]/pv[i-1]-1 for i in range(idx0+1,idx1+1) if pv[i-1]>0])
    sharpe=np.mean(rets)*SPY/(np.std(rets)*np.sqrt(SPY)) if np.std(rets)>0 else 0
    mx=np.maximum.accumulate(pv[idx0:]); da=np.where(mx>0,pv[idx0:]/mx-1,0)
    mxdd=da.min(); calmar=cagr/abs(mxdd) if mxdd!=0 else 0
    return cagr, mxdd, sharpe, calmar

dates=vni["time"].reset_index(drop=True)
idx11=vni[vni["time"]>="2011-01-01"].index[0]

pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
bh_f=metrics(pv_bh,dates); bh_11=metrics(pv_bh,dates,idx11)

NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

print()
print(f"{'alpha':>5} | {'CAGR_full':>9} | {'CAGR_2011':>9} | {'MaxDD_11':>8} | {'Sharpe_11':>9} | {'Calmar_11':>9} | {'Trans':>5} | {'Short':>5} | State_now")
print("-"*100)

results = []
for alpha in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]:
    rs_ema=np.full(n,np.nan)
    for t in range(n):
        v=r_score[t]; prev=rs_ema[t-1] if t>0 else np.nan
        rs_ema[t] = v if np.isnan(prev) else (prev if np.isnan(v) else alpha*v+(1-alpha)*prev)

    state_raw=np.array([classify(r) for r in rs_ema])
    state_ov=apply_overrides(state_raw)
    state_sm=rolling_mode(state_ov,15)
    pv=backtest(state_sm)

    cf,df,sf,calf=metrics(pv,dates)
    c11,d11,s11,cal11=metrics(pv,dates,idx11)

    trans=sum(1 for i in range(1,n) if state_sm[i]!=state_sm[i-1])
    durs=[]; st=0
    for i in range(1,n):
        if state_sm[i]!=state_sm[i-1]: durs.append(i-st); st=i
    durs.append(n-st)
    short=sum(1 for d in durs if d<=5)
    med=int(np.median(durs))
    cur_state=NAMES[state_sm[-1]]
    cur_ema=rs_ema[-1]

    beat_full = cf > bh_f[0]
    beat_11   = c11 > bh_11[0]
    flag = " <<" if beat_full and beat_11 else (" >full" if beat_full else "")

    print(f"{alpha:>5.2f} | {cf:>9.1%} | {c11:>9.1%} | {d11:>8.1%} | {s11:>9.2f} | {cal11:>9.2f} | {trans:>5d} | {short:>5d} | {cur_state} ema={cur_ema:.3f}{flag}")
    results.append((alpha, cf, c11, d11, s11, cal11, trans, short, med, cur_state, cur_ema))

print("-"*100)
print(f"{'B&H':>5} | {bh_f[0]:>9.1%} | {bh_11[0]:>9.1%} | {bh_11[1]:>8.1%} | {bh_11[2]:>9.2f} | {bh_11[3]:>9.2f}")
print()
print("<< = beats B&H in BOTH full period AND since 2011")
