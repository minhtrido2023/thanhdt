# -*- coding: utf-8 -*-
"""
test_beardvg_gate.py
====================
So sánh các biến thể của BearDvg Gate strategy.

Part 1 : Exit condition (OR vs AND vs từng điều kiện đơn lẻ)
Part 2 : Gate floor level (CRISIS=0% vs BEAR=20% vs NEUTRAL=70%)
Part 3 : Minimum gate duration (0 → 60 phiên)
Part 4 : Gate event log — từng lần kích hoạt, trigger thoát, VNINDEX change
Summary: Xếp hạng theo Calmar since 2011
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd, os

WORKDIR   = r"/home/trido/thanhdt/WorkingClaude"
MIN_LB    = 252; RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001
DEPOSIT_R = 0.06/252; BORROW_R=0.10/252
TARGET_W  = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
SPY       = 243.4
NAMES     = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ─── Load ─────────────────────────────────────────────────────────────────────
vni = pd.read_csv(os.path.join(WORKDIR,"data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE",
          "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M","D_RSI_Min1W","D_RSI_Min3M",
          "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
          "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if c in vni.columns: vni[c] = pd.to_numeric(vni[c], errors="coerce")
breadth = pd.read_csv(os.path.join(WORKDIR,"data/breadth_data.csv"))
breadth["time"] = pd.to_datetime(breadth["time"])
vni = vni.merge(breadth, on="time", how="left")
n = len(vni)
close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
dates = vni["time"].reset_index(drop=True)
print(f"Loaded {n} rows | {dates.iloc[0].date()} → {dates.iloc[-1].date()}")

# ─── Indicators ───────────────────────────────────────────────────────────────
p3m = pd.to_numeric(vni["Change_3M"],errors="coerce").values if "Change_3M" in vni.columns else np.full(n,np.nan)
p1m = pd.to_numeric(vni["Change_1M"],errors="coerce").values if "Change_1M" in vni.columns else np.full(n,np.nan)
ma200v = pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev = np.where((ma200v>0)&~np.isnan(ma200v), close/ma200v-1, np.nan)

rsi_c=np.full(n,np.nan); au=ad=np.nan; P=14
for i in range(1,n):
    d2=close[i]-close[i-1]; u=max(d2,0.); dw=max(-d2,0.)
    if np.isnan(au):
        if i>=P:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,P+1)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,P+1)])
            if au+ad>0: rsi_c[i]=au/(au+ad)
    else:
        au=(au*(P-1)+u)/P; ad=(ad*(P-1)+dw)/P
        if au+ad>0: rsi_c[i]=au/(au+ad)

e12=np.full(n,np.nan); e26=np.full(n,np.nan); sg=np.full(n,np.nan); mh=np.full(n,np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    pv2=e12[i-1] if i>0 else np.nan
    e12[i]=close[i] if np.isnan(pv2) else pv2*(1-k12)+close[i]*k12
    pv6=e26[i-1] if i>0 else np.nan
    e26[i]=close[i] if np.isnan(pv6) else pv6*(1-k26)+close[i]*k26
    ml=e12[i]-e26[i]
    ps=sg[i-1] if i>0 else np.nan
    sg[i]=ml if np.isnan(ps) else ps*(1-k9)+ml*k9
    if i>=33: mh[i]=ml-sg[i]

hl=high-low
with np.errstate(divide="ignore",invalid="ignore"):
    mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.)
cmf_c=np.full(n,np.nan); mfv=mfm*vol
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf_c[i]=np.sum(mfv[i-14:i])/vs

breadth_arr=pd.to_numeric(vni["breadth"],errors="coerce").values
W_BASE={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
factors={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi_c,"MACD":mh,"CMF":cmf_c,"Breadth":breadth_arr}

def ep_rank(arr, min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        hist=arr[:t+1]; valid=hist[~np.isnan(hist)]
        if len(valid)<min_lb or np.isnan(arr[t]): continue
        out[t]=np.sum(valid<=arr[t])/len(valid)
    return out

print("Ranking factors (this takes ~30s)...")
ranks={k:ep_rank(factors[k]) for k in factors}
score=np.full(n,np.nan)
for t in range(n):
    avail={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(avail)<3: continue
    ws=sum(W_BASE[k] for k in avail)
    score[t]=sum(avail[k]*W_BASE[k] for k in avail)/ws
r_score=ep_rank(score)
print("  done.")

pe_arr=vni["VNINDEX_PE"].values.copy()

# PE expanding P90 (for override)
pe_p90=np.full(n,np.nan)
for t in range(n):
    v=pe_arr[:t+1]; v=v[~np.isnan(v)]
    if len(v)>=60: pe_p90[t]=np.nanpercentile(v,90)

# PE expanding rank (for gate exit: PE_rank < 0.80 = valuation normalized)
pe_rank_arr=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    v=pe_arr[:t+1]; v=v[~np.isnan(v)]
    if len(v)>=60: pe_rank_arr[t]=np.sum(v<=pe_arr[t])/len(v)

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

ALPHA=0.40
rs_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; prev=rs_ema[t-1] if t>0 else np.nan
    rs_ema[t]=v if np.isnan(prev) else (prev if np.isnan(v) else ALPHA*v+(1-ALPHA)*prev)

# r_score streak: 10 phiên liên tiếp rs_ema > 0.65 → momentum phục hồi bền vững
rscore_streak=np.zeros(n,dtype=bool); streak=0
for i in range(n):
    if not np.isnan(rs_ema[i]) and rs_ema[i]>0.65: streak+=1
    else: streak=0
    if streak>=10: rscore_streak[i]=True

def apply_overrides(states):
    s=states.copy()
    for i in range(n):
        if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s[i]==5: s[i]=4
        if dd[i]<-0.25 and s[i]>=4: s[i]=3
        if not np.isnan(av[i]) and not np.isnan(v20[i]) and v20[i]>1.5*av[i] and s[i]==5: s[i]=4
    return s

def rolling_mode(states, window=15):
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

state_raw=np.array([classify(r) for r in rs_ema])
state_ov=apply_overrides(state_raw)

# ─── BearDvg / BullDvg ────────────────────────────────────────────────────────
def _s(col): return vni[col] if col in vni.columns else pd.Series(np.nan,index=vni.index)
D_RSI=_s("D_RSI"); D_RSI_T1W=_s("D_RSI_T1W")
D_RSI_Max1W=_s("D_RSI_Max1W"); D_RSI_Max3M=_s("D_RSI_Max3M")
D_RSI_Min1W=_s("D_RSI_Min1W"); D_RSI_Min3M=_s("D_RSI_Min3M")
D_RSI_Max1W_C=_s("D_RSI_Max1W_Close"); D_RSI_Max3M_C=_s("D_RSI_Max3M_Close")
D_RSI_Max3M_M=_s("D_RSI_Max3M_MACD"); D_RSI_Max1W_M=_s("D_RSI_Max1W_MACD")
D_RSI_Min1W_C=_s("D_RSI_Min1W_Close"); D_RSI_MinT3=_s("D_RSI_MinT3")
D_MACDdiff=_s("D_MACDdiff"); D_CMF=_s("D_CMF"); C_L1M=_s("C_L1M"); C_L1W=_s("C_L1W")
mask_2011=vni["time"]>="2011-01-01"

bear1=(D_RSI_Max1W/D_RSI>1.044)&(D_RSI_Max3M>0.74)&(D_RSI_Max1W<0.72)&(D_RSI_Max1W>0.61)&\
      (D_RSI_Max1W_C/D_RSI_Max3M_C>1.028)&(D_RSI_Max3M_M/D_RSI_Max1W_M>1.11)&\
      (D_MACDdiff<0)&(vni["Close"]/D_RSI_Max3M_C>0.96)&(D_RSI_MinT3>0.43)&(D_CMF<0.13)&mask_2011
bear2=(D_RSI_Max1W/D_RSI>1.016)&(D_RSI_Max3M>0.77)&(D_RSI_Max1W<0.79)&(D_RSI_Max1W>0.60)&\
      (D_RSI_Max1W_C/D_RSI_Max3M_C>1.008)&(D_RSI_Max3M_M/D_RSI_Max1W_M>1.10)&\
      (D_MACDdiff<0)&(vni["Close"]/D_RSI_Max3M_C>0.97)&(D_RSI_MinT3>0.50)&(D_CMF<0.15)&mask_2011
bull1=(D_RSI_Min1W/D_RSI_Min3M>0.90)&(D_RSI_Min1W<0.60)&(D_RSI_Min3M<0.40)&\
      (D_RSI_Min1W_C/D_RSI_Max3M_C<1.15)&(D_MACDdiff>0)&(D_RSI_MinT3<0.50)&(D_RSI_Max1W<0.48)&\
      (D_RSI/D_RSI_T1W>1.12)&(D_CMF>0)&(C_L1M<1.21)&(C_L1W<1.05)&mask_2011
bull2=(D_RSI_Min1W/D_RSI_Min3M>0.92)&(D_RSI_Min1W<0.52)&(D_RSI_Min3M<0.38)&\
      (D_RSI_Min1W_C/D_RSI_Max3M_C<1.10)&(D_MACDdiff>0)&(D_RSI_MinT3<0.56)&(D_RSI_Max1W<0.64)&\
      (D_RSI/D_RSI_T1W>1.10)&(D_CMF>0)&(C_L1M<1.20)&(C_L1W<1.025)&mask_2011

bear_mask=(bear1|bear2).values.astype(bool)
bull_mask=(bull1|bull2).values.astype(bool)
p3m_rank_arr=ranks["P3M"]

# ─── Backtest helpers ─────────────────────────────────────────────────────────
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
    yrs=(dates.iloc[idx1]-dates.iloc[idx0]).days/365.25
    cagr=(pv[idx1]/pv[idx0])**(1/yrs)-1 if yrs>0 else 0
    rets=np.array([pv[i]/pv[i-1]-1 for i in range(idx0+1,idx1+1) if pv[i-1]>0])
    sh=np.mean(rets)*SPY/(np.std(rets)*np.sqrt(SPY)) if np.std(rets)>0 else 0
    mx=np.maximum.accumulate(pv[idx0:]); da=np.where(mx>0,pv[idx0:]/mx-1,0)
    mxdd=da.min(); cal=cagr/abs(mxdd) if mxdd!=0 else 0
    return cagr, mxdd, sh, cal

def count_trans(states):
    return sum(1 for i in range(1,len(states)) if states[i]!=states[i-1])

idx11=vni[vni["time"]>="2011-01-01"].index[0]
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
bh_f=metrics(pv_bh); bh_11=metrics(pv_bh,idx11)

# ─── Gate function ─────────────────────────────────────────────────────────────
def apply_gate(base_states, gate_floor=2, exit_cond="or", min_dur=20):
    """
    gate_floor : max state allowed while gate active (1=CRISIS 0%, 2=BEAR 20%, 3=NEUTRAL 70%)
    exit_cond  : "bulldvg" | "p3m_pe" | "rscore" | "or" | "and"
                 - bulldvg : BullDvg fires
                 - p3m_pe  : P3M_rank>0.45 AND PE_rank<0.80  (momentum + định giá hợp lý)
                 - rscore  : r_score_ema>0.65 trong 10 phiên liên tiếp
                 - or      : bất kỳ điều kiện nào ở trên (KHUYẾN NGHỊ)
                 - and     : BullDvg AND P3M+PE  (chiến lược gốc của user, strict nhất)
    min_dur    : phiên tối thiểu sau BearDvg cuối cùng trước khi cho phép thoát gate
    """
    s = base_states.copy()
    gate_active = False
    gate_start  = -1
    gate_durs   = []
    gate_events = []

    for i in range(n):
        if bear_mask[i]:
            if not gate_active:
                gate_active = True
                gate_start  = i
                gate_events.append({
                    "entry_i": i,
                    "entry_date": dates.iloc[i].strftime("%Y-%m-%d"),
                    "entry_close": float(close[i]),
                })
            else:
                gate_start = i  # reset minimum timer khi có BearDvg mới trong cùng gate

        if gate_active:
            if s[i] > gate_floor:
                s[i] = gate_floor

            sessions_in = i - gate_start
            if sessions_in >= min_dur:
                p3m_ok  = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
                pe_ok   = (not np.isnan(pe_rank_arr[i]))  and pe_rank_arr[i]  < 0.80
                bull_ok = bool(bull_mask[i])
                rs_ok   = bool(rscore_streak[i])

                if exit_cond == "bulldvg":
                    exit_now = bull_ok
                elif exit_cond == "p3m_pe":
                    exit_now = p3m_ok and pe_ok
                elif exit_cond == "rscore":
                    exit_now = rs_ok
                elif exit_cond == "or":
                    exit_now = bull_ok or (p3m_ok and pe_ok) or rs_ok
                elif exit_cond == "and":
                    exit_now = bull_ok and p3m_ok and pe_ok
                else:
                    exit_now = False

                if exit_now:
                    gate_durs.append(sessions_in)
                    if gate_events:
                        e = gate_events[-1]
                        e["exit_i"]     = i
                        e["exit_date"]  = dates.iloc[i].strftime("%Y-%m-%d")
                        e["exit_close"] = float(close[i])
                        e["duration"]   = sessions_in
                        trigger = ("BullDvg" if bull_ok else
                                   "P3M+PE"  if (p3m_ok and pe_ok) else
                                   "r_score")
                        e["trigger"]    = trigger
                    gate_active = False

    if gate_active:
        dur = n - gate_start
        gate_durs.append(dur)
        if gate_events:
            e = gate_events[-1]
            e["exit_i"]     = n-1
            e["exit_date"]  = dates.iloc[-1].strftime("%Y-%m-%d")
            e["exit_close"] = float(close[-1])
            e["duration"]   = dur
            e["trigger"]    = "ACTIVE"

    return rolling_mode(s, 15), gate_durs, gate_events

# ─── Baseline: window-20 (current system) ─────────────────────────────────────
bwin=np.zeros(n,dtype=bool); bulwin=np.zeros(n,dtype=bool)
for i in range(n):
    if bear_mask[i]: bwin[i:min(i+20,n)]=True
    if bull_mask[i]: bulwin[i:min(i+20,n)]=True
state_w20=state_ov.copy()
for i in range(n):
    if bwin[i]  and state_w20[i]>=4: state_w20[i]=3
    if bulwin[i] and state_w20[i]<=2: state_w20[i]=3
state_w20=rolling_mode(state_w20,15)

state_base=rolling_mode(state_ov,15)

# ─── Print helper ─────────────────────────────────────────────────────────────
HDR = f"{'Strategy':>24} | {'CAGR_f':>7} | {'CAGR_11':>7} | {'MaxDD_11':>8} | {'Shrp_11':>7} | {'Cal_11':>6} | {'Trans':>5} | {'AvgGate':>7} | {'NGates':>6}"
SEP = "-"*100

def row(label, sm, avg_g=None, n_gates=None):
    pv=backtest(sm)
    cf,_,_,_=metrics(pv); c11,d11,s11,cal11=metrics(pv,idx11)
    ag = f"{avg_g:.0f}" if avg_g is not None else "–"
    ng = f"{n_gates}"   if n_gates is not None else "–"
    beat = " <<"        if c11>bh_11[0] and cf>bh_f[0] else ""
    return (f"{label:>24} | {cf:>7.1%} | {c11:>7.1%} | {d11:>8.1%} | {s11:>7.2f} | {cal11:>6.2f} | {count_trans(sm):>5} | {ag:>7} | {ng:>6}{beat}",
            cal11, c11, cf, d11, s11, count_trans(sm), avg_g)

def bh_row():
    return f"{'B&H':>24} | {bh_f[0]:>7.1%} | {bh_11[0]:>7.1%} | {bh_11[1]:>8.1%} | {bh_11[2]:>7.2f} | {bh_11[3]:>6.2f}"

# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*100)
print("PART 1: Exit condition comparison   (gate_floor=BEAR 20%, min_dur=20 phiên)")
print("="*100)
print(HDR); print(SEP)

summary_rows = []

# Baselines
r,*rest=row("base_5state (no dvg)", state_base); print(r); summary_rows.append(("base_5state",)+tuple(rest))
r,*rest=row("window_20 (current)",  state_w20, 20, bear_mask.sum()); print(r); summary_rows.append(("window_20",)+tuple(rest))
print(SEP)

for ec, lbl in [
    ("bulldvg", "gate_bulldvg"),
    ("p3m_pe",  "gate_p3m_pe"),
    ("rscore",  "gate_rscore"),
    ("or",      "gate_or [RECOMMENDED]"),
    ("and",     "gate_and [user strict]"),
]:
    sm, durs, events = apply_gate(state_ov, gate_floor=2, exit_cond=ec, min_dur=20)
    ng  = len(events)
    avg = np.mean(durs) if durs else None
    r,*rest = row(lbl, sm, avg, ng)
    print(r); summary_rows.append((lbl,)+tuple(rest))

print(SEP); print(bh_row())

# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*100)
print("PART 2: Gate floor level   (exit_cond=OR, min_dur=20 phiên)")
print("="*100)
print(HDR); print(SEP)

r,*rest=row("window_20 (current)",state_w20,20,bear_mask.sum()); print(r)
for fl, lbl in [
    (3, "gate_or floor=NEUTRAL 70%"),
    (2, "gate_or floor=BEAR   20%"),
    (1, "gate_or floor=CRISIS  0%"),
]:
    sm, durs, events = apply_gate(state_ov, gate_floor=fl, exit_cond="or", min_dur=20)
    ng  = len(events)
    avg = np.mean(durs) if durs else None
    r,*rest = row(lbl, sm, avg, ng)
    print(r); summary_rows.append((lbl,)+tuple(rest))

print(SEP); print(bh_row())

# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*100)
print("PART 3: Minimum gate duration   (exit_cond=OR, gate_floor=BEAR 20%)")
print("="*100)
print(HDR); print(SEP)

for md, lbl in [
    (0,  "gate_or min= 0 (không chờ)"),
    (10, "gate_or min=10 (2 tuần)"),
    (20, "gate_or min=20 (1 tháng)"),
    (40, "gate_or min=40 (2 tháng)"),
    (60, "gate_or min=60 (3 tháng)"),
    (90, "gate_or min=90 (4 tháng)"),
]:
    sm, durs, events = apply_gate(state_ov, gate_floor=2, exit_cond="or", min_dur=md)
    ng  = len(events)
    avg = np.mean(durs) if durs else None
    r,*rest = row(lbl, sm, avg, ng)
    print(r); summary_rows.append((lbl,)+tuple(rest))

print(SEP); print(bh_row())

# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*100)
print("PART 4: Gate event log — OR exit, floor=BEAR, min=20")
print("="*100)
_, durs_or, events_or = apply_gate(state_ov, gate_floor=2, exit_cond="or", min_dur=20)

if events_or:
    print(f"  {'Entry':>10} | {'Entry VNI':>9} | {'Exit':>10} | {'Exit VNI':>9} | {'Dur(ses)':>8} | {'Trigger':>9} | {'VNI chg':>8} | {'Note'}")
    print("  " + "-"*86)
    for e in events_or:
        if "exit_date" not in e: continue
        chg = e['exit_close']/e['entry_close']-1
        note = ""
        if chg < -0.10: note = "⚠ -10%+"
        elif chg >  0.15: note = "✓ +15%+"
        elif chg < -0.05: note = "↓ -5%"
        elif chg >  0.05: note = "↑ +5%"
        trigger = e.get('trigger','?')
        active  = " [ACTIVE NOW]" if trigger=="ACTIVE" else ""
        print(f"  {e['entry_date']:>10} | {e['entry_close']:>9.0f} | {e['exit_date']:>10} | {e['exit_close']:>9.0f} | {e.get('duration',0):>8} | {trigger:>9} | {chg:>8.1%} | {note}{active}")

    print("  " + "-"*86)
    total_active = sum(e.get('duration',0) for e in events_or)
    good = sum(1 for e in events_or if e.get('trigger','') in ["BullDvg","P3M+PE","r_score"] and e.get('exit_close',0)/e.get('entry_close',1)-1 > -0.05)
    total_closed = sum(1 for e in events_or if e.get('trigger','') != "ACTIVE")
    print(f"  Gates: {len(events_or)} total | Avg duration: {np.mean(durs_or):.0f} ses | "
          f"Correct exits (VNINDEX ≥ entry-5%): {good}/{total_closed}")

    # Trigger breakdown
    from collections import Counter
    trig_cnt = Counter(e.get('trigger','?') for e in events_or if e.get('trigger','') not in ['ACTIVE','?'])
    print(f"  Trigger breakdown: " + " | ".join(f"{k}: {v}" for k,v in sorted(trig_cnt.items())))

# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*100)
print("SUMMARY: Top 12 variants ranked by Calmar since 2011  (chỉ tính các biến thể đã thắng B&H)")
print("="*100)
print(HDR); print(SEP)

# Remove duplicates by name (keep first occurrence)
seen = set(); deduped = []
for row_data in summary_rows:
    k = row_data[0]
    if k not in seen:
        seen.add(k); deduped.append(row_data)

# Sort by Calmar_11 desc
deduped.sort(key=lambda x: -x[1])
for row_data in deduped[:12]:
    lbl, cal11, c11, cf, d11, s11, trans, avg_g = row_data
    ag = f"{avg_g:.0f}" if avg_g is not None else "–"
    beat = " <<"        if c11>bh_11[0] and cf>bh_f[0] else ""
    print(f"{lbl:>24} | {cf:>7.1%} | {c11:>7.1%} | {d11:>8.1%} | {s11:>7.2f} | {cal11:>6.2f} | {trans:>5} | {ag:>7} | {'–':>6}{beat}")
print(SEP); print(bh_row())
print("\n<< = beats B&H in BOTH full period AND since 2011")
