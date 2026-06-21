# -*- coding: utf-8 -*-
"""
analyze_f_system_v2.py
=======================
F-system: 2 tin hieu manh nhat
  SIG-A: BEAR->NEUTRAL transition
  SIG-B: r_score valley (turn up)

Phan tich:
  1. Feature analysis: bien nao du bao xac suat thanh cong
  2. Probability bins: nhan gia xac suat theo tung feature
  3. Composite score: ket hop features -> P(win)
  4. Kelly leverage: dieu chinh leverage theo P(win)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os, numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
TC = 0.001   # 0.1% round-trip

# ══════════════════════════════════════════════════════════════════════
# LOAD & COMPUTE STATE  (same as before)
# ══════════════════════════════════════════════════════════════════════
print("Loading & computing state...")
vni=pd.read_csv(os.path.join(WORKDIR,"data/VNINDEX.csv"),low_memory=False)
vni["time"]=pd.to_datetime(vni["time"]); vni=vni.sort_values("time").reset_index(drop=True)
for col in ["Close","D_RSI","D_MACDdiff","D_CMF","VNINDEX_PE"]:
    if col in vni.columns: vni[col]=pd.to_numeric(vni[col],errors="coerce")
b_path=os.path.join(WORKDIR,"data/breadth_data.csv")
if os.path.exists(b_path):
    b=pd.read_csv(b_path); b["time"]=pd.to_datetime(b["time"])
    b["breadth"]=pd.to_numeric(b["breadth"],errors="coerce"); vni=vni.merge(b,on="time",how="left")
else: vni["breadth"]=np.nan
n=len(vni); close=vni["Close"].values.copy()
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days; SPY=n/(cal_days/365.25)

def rolling_ret(arr,w):
    out=np.full(len(arr),np.nan)
    for i in range(w,len(arr)):
        if arr[i-w]>0: out[i]=arr[i]/arr[i-w]-1
    return out
def expanding_rank(arr):
    out=np.full(len(arr),np.nan)
    for i in range(MIN_LB,len(arr)):
        win=arr[max(0,i-3000):i+1]; valid=win[~np.isnan(win)]
        if len(valid)<10 or np.isnan(arr[i]): continue
        out[i]=np.searchsorted(np.sort(valid),arr[i])/len(valid)
    return out

p3m=rolling_ret(close,63); p1m=rolling_ret(close,21)
ma200=np.full(n,np.nan)
for i in range(199,n): ma200[i]=np.mean(close[i-199:i+1])
ma200_dev=np.where(ma200>0,close/ma200-1,np.nan)
rsi=vni["D_RSI"].values.copy() if "D_RSI" in vni.columns else np.full(n,np.nan)
macd=vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n,np.nan)
cmf=vni["D_CMF"].values.copy() if "D_CMF" in vni.columns else np.full(n,np.nan)
brdt=vni["breadth"].values.copy() if "breadth" in vni.columns else np.full(n,np.nan)
ranks={"P3M":expanding_rank(p3m),"P1M":expanding_rank(p1m),"MA200":expanding_rank(ma200_dev),
       "RSI":expanding_rank(rsi),"MACD":expanding_rank(macd),"CMF":expanding_rank(cmf),"Breadth":expanding_rank(brdt)}
score=np.full(n,np.nan)
for i in range(n):
    vals=[(w,ranks[k][i]) for k,w in W_BASE.items() if not np.isnan(ranks[k][i])]
    if len(vals)>=MIN_FACTORS:
        tw=sum(x[0] for x in vals); score[i]=sum(x[0]*x[1] for x in vals)/tw
r_score=np.full(n,np.nan); last=None
for i in range(n):
    if np.isnan(score[i]): r_score[i]=last
    else:
        r_score[i]=EMA_ALPHA*score[i]+(1-EMA_ALPHA)*last if last is not None else score[i]
        last=r_score[i]
def classify(rs):
    if rs<0.10: return 1
    elif rs<0.30: return 2
    elif rs<0.55: return 3
    elif rs<0.75: return 3
    elif rs<0.90: return 4
    else: return 5
state_raw=np.array([classify(v) if not np.isnan(v) else 3 for v in r_score])
pe_arr=vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n,np.nan)
pe_p90=np.full(n,np.nan)
for i in range(252,n):
    w2=pe_arr[max(0,i-3000):i+1]; v2=w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i]=np.percentile(v2,90)
dd_a=np.zeros(n); pk=close[0]
for i in range(n):
    if close[i]>pk: pk=close[i]; dd_a[i]=close[i]/pk-1
log_r=np.concatenate([[np.nan],np.diff(np.log(np.where(close>0,close,np.nan)))])
vol20=np.full(n,np.nan)
for i in range(20,n): vol20[i]=np.nanstd(log_r[i-19:i+1])*np.sqrt(SPY)
vol20_ma=np.full(n,np.nan)
for i in range(60,n): vol20_ma[i]=np.nanmean(vol20[i-59:i+1])
so=state_raw.copy()
for i in range(n):
    s=so[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s>=4: so[i]=min(s,4)
    if dd_a[i]<-0.25 and s>=3: so[i]=min(s,3)
    if (not np.isnan(vol20[i]) and not np.isnan(vol20_ma[i])
        and vol20_ma[i]>0 and vol20[i]>1.5*vol20_ma[i] and s>=4): so[i]=min(s,4)
def rolling_mode(arr,w):
    out=arr.copy()
    for i in range(w-1,len(arr)):
        win=arr[i-w+1:i+1]; counts=np.bincount(win,minlength=6); out[i]=np.argmax(counts)
    return out
def min_stay_filter(arr,ms):
    out=arr.copy(); i=0
    while i<len(arr):
        j=i+1
        while j<len(arr) and arr[j]==arr[i]: j+=1
        if j-i<ms:
            prev=out[i-1] if i>0 else arr[i]; out[i:j]=prev
        i=j
    return out
ss=rolling_mode(so,MODE_WIN); ss=min_stay_filter(ss,MIN_STAY)
vni["state"]=ss; vni["r_score"]=r_score; vni["score_raw"]=score
vni["vol20"]=vol20; vni["p3m"]=p3m; vni["p1m"]=p1m
vni["rsi_raw"]=rsi; vni["dd"]=dd_a
print("  Done.\n")

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def fwd_ret(idx, h):
    """T+1 entry (next open), exit at close T+h+1"""
    if idx+h+1 >= n or close[idx+1]<=0: return np.nan
    return close[idx+h+1]/close[idx+1] - 1

def kelly_leverage(p, b, frac=0.3):
    """
    Kelly criterion: f* = (p*b - (1-p)) / b
    b = avg_win / avg_loss
    frac = fractional Kelly (30% for safety)
    Returns recommended leverage (capped at 3x for derivatives)
    """
    if b <= 0: return 0
    f_star = (p*b - (1-p)) / b
    f_kelly = max(0, f_star) * frac
    return min(f_kelly * 10, 3.0)  # scale to leverage units, cap 3x

def feature_analysis(records, feature_cols, target_col, n_bins=3):
    """
    Phan tich: voi moi feature, chia bins va tinh win rate / mean return.
    """
    df = pd.DataFrame(records)
    if len(df) < 5: return
    for fc in feature_cols:
        if fc not in df.columns: continue
        vals = df[fc].dropna()
        if len(vals) < 5: continue
        try:
            df[fc+"_bin"] = pd.qcut(df[fc], q=n_bins, labels=False, duplicates="drop")
        except: continue
        grp = df.groupby(fc+"_bin").agg(
            n=(target_col,"count"),
            wr=(target_col, lambda x: (x>0).mean()),
            mean_ret=(target_col, "mean"),
        ).reset_index()
        print(f"    {fc}:")
        for _,row in grp.iterrows():
            bar=int(row["wr"]*20)*"|"
            print(f"      bin{int(row[fc+'_bin'])}: n={int(row['n']):>4}  WR={row['wr']*100:>5.1f}%  mean={row['mean_ret']*100:>+6.3f}%  {bar}")

def print_trade(t, h):
    r = t.get(f"ret_T{h}")
    rs= t.get("r_score_entry",float("nan"))
    if r is None: return
    flag = "WIN" if r > TC else "LOSS"
    print(f"    {str(t['date'].date()):<12} rs={rs:.3f}  ret_T{h}={r*100:>+6.2f}%  {flag}")

# ══════════════════════════════════════════════════════════════════════
# SIG-A: BEAR -> NEUTRAL TRANSITION
# ══════════════════════════════════════════════════════════════════════
print("="*70)
print("SIG-A: BEAR -> NEUTRAL TRANSITION")
print("="*70)

# Build segment list
segs=[]
i=0
while i<n:
    j=i+1
    while j<n and ss[j]==ss[i]: j+=1
    segs.append({"state":int(ss[i]),"start":i,"end":j-1,"dur":j-i,
                 "close_start":close[i],"close_end":close[j-1],
                 "date_start":vni["time"].iloc[i],"date_end":vni["time"].iloc[j-1]})
    i=j

siga_records = []
for si in range(1, len(segs)):
    seg  = segs[si]
    prev = segs[si-1]
    if prev["state"]==2 and seg["state"]==3:  # BEAR -> NEUTRAL
        entry_i = seg["start"]
        if entry_i < MIN_LB: continue  # skip early period without full ranks

        # Features at entry
        bear_dur    = prev["dur"]
        bear_ret    = close[prev["end"]]/close[prev["start"]]-1 if close[prev["start"]]>0 else np.nan
        rs_entry    = float(r_score[entry_i]) if not np.isnan(r_score[entry_i]) else np.nan
        vol_entry   = float(vol20[entry_i]) if not np.isnan(vol20[entry_i]) else np.nan
        p3m_entry   = float(p3m[entry_i]) if not np.isnan(p3m[entry_i]) else np.nan
        p1m_entry   = float(p1m[entry_i]) if not np.isnan(p1m[entry_i]) else np.nan
        rsi_entry   = float(rsi[entry_i]) if not np.isnan(rsi[entry_i]) else np.nan
        dd_entry    = float(dd_a[entry_i])

        rec = dict(
            date        = vni["time"].iloc[entry_i],
            seg_idx     = si,
            bear_dur    = bear_dur,
            bear_ret    = bear_ret,
            r_score_entry = rs_entry,
            vol_entry   = vol_entry,
            p3m_entry   = p3m_entry,
            p1m_entry   = p1m_entry,
            rsi_entry   = rsi_entry,
            dd_entry    = dd_entry,
        )
        for h in [1,2,3,5,10]:
            rec[f"ret_T{h}"] = fwd_ret(entry_i, h)
            rec[f"win_T{h}"] = (rec[f"ret_T{h}"] or 0) - TC > 0
        siga_records.append(rec)

df_a = pd.DataFrame(siga_records)
print(f"\n  Total BEAR->NEUTRAL signals (all history): {len(df_a)}")
print(f"  Date range: {df_a['date'].min().date()} -> {df_a['date'].max().date()}")

# Overall stats
print("\n  --- Overall performance ---")
print(f"  {'Horizon':>8} {'n':>5} {'WR':>7} {'MeanRet':>9} {'MeanNet':>9} {'AvgWin':>8} {'AvgLoss':>8} {'PF':>6}")
print("  "+"-"*68)
for h in [1,2,3,5,10]:
    rets = df_a[f"ret_T{h}"].dropna().values
    if len(rets)==0: continue
    nets = rets - TC
    wr   = (nets>0).mean()
    mret = rets.mean()*100
    mnet = nets.mean()*100
    avg_w= rets[nets>0].mean()*100 if (nets>0).any() else 0
    avg_l= rets[nets<0].mean()*100 if (nets<0).any() else 0
    pf   = abs(rets[nets>0].sum()/rets[nets<0].sum()) if (nets<0).any() else 99
    print(f"  T+{h:>6}: {len(rets):>5} {wr*100:>6.1f}% {mret:>+8.3f}% {mnet:>+8.3f}% {avg_w:>+7.3f}% {avg_l:>+7.3f}% {pf:>6.2f}")

# Individual trades
print("\n  --- Individual trades (T+5) ---")
print(f"  {'Date':<12} {'BearDur':>8} {'BearRet':>9} {'rs_entry':>9} {'vol':>7} {'ret_T5':>9} {'ret_T3':>8}")
print("  "+"-"*70)
for _,row in df_a.iterrows():
    r5=row.get("ret_T5",float("nan")); r3=row.get("ret_T3",float("nan"))
    flag="WIN" if not np.isnan(r5) and r5-TC>0 else "LOSS"
    r5s=f"{r5*100:>+7.2f}%" if not np.isnan(r5) else "    N/A"
    r3s=f"{r3*100:>+6.2f}%" if not np.isnan(r3) else "   N/A"
    print(f"  {str(row['date'].date()):<12} {row['bear_dur']:>8.0f} {row['bear_ret']*100:>+8.1f}% {row['r_score_entry']:>9.3f} {row['vol_entry']*100 if not np.isnan(row['vol_entry']) else float('nan'):>6.1f}% {r5s} {r3s}  {flag}")

# Feature analysis (T+5)
print("\n  --- Feature vs Win Rate (T+5) ---")
df_a["win_T5_num"] = (df_a["ret_T5"] - TC > 0).astype(float)
feature_analysis(df_a, ["bear_dur","bear_ret","r_score_entry","vol_entry","p1m_entry","rsi_entry"], "win_T5_num")

# ══════════════════════════════════════════════════════════════════════
# COMPOSITE SCORE & PROBABILITY — SIG-A
# ══════════════════════════════════════════════════════════════════════
print("\n  --- Composite probability model (SIG-A) ---")
print("  Rules duoc xac dinh tu feature analysis:")
print("  +1 diem: bear_dur  > 15 phien   (xac nhan downtrend du lau)")
print("  +1 diem: bear_ret  < -8%        (giam manh -> hoi phuc manh)")
print("  +1 diem: r_score   < 0.32       (con gan day, room de tang)")
print("  +1 diem: vol_entry < median_vol (vol binh thuong, khong hoang loan)")
print("  +1 diem: p1m_entry < -5%        (1M truoc do yeu -> reversal)")

median_vol_a = df_a["vol_entry"].median()
def score_siga(row):
    s=0
    if not np.isnan(row["bear_dur"])    and row["bear_dur"]>15:      s+=1
    if not np.isnan(row["bear_ret"])    and row["bear_ret"]<-0.08:   s+=1
    if not np.isnan(row["r_score_entry"]) and row["r_score_entry"]<0.32: s+=1
    if not np.isnan(row["vol_entry"])   and row["vol_entry"]<median_vol_a: s+=1
    if not np.isnan(row["p1m_entry"])   and row["p1m_entry"]<-0.05:  s+=1
    return s

df_a["comp_score"] = df_a.apply(score_siga, axis=1)

print(f"\n  {'Score':>6} {'n':>5} {'WR_T3':>8} {'WR_T5':>8} {'Net_T3':>9} {'Net_T5':>9} {'Kelly30%':>10} {'Leverage':>9}")
print("  "+"-"*68)
for sc in sorted(df_a["comp_score"].unique()):
    sub = df_a[df_a["comp_score"]==sc]
    wr3=(sub["ret_T3"]-TC>0).mean(); wr5=(sub["ret_T5"]-TC>0).mean()
    net3=sub["ret_T3"].mean()-TC; net5=sub["ret_T5"].mean()-TC
    # Kelly for T+5
    w5=sub["ret_T5"][sub["ret_T5"]-TC>0].mean() if (sub["ret_T5"]-TC>0).any() else 0
    l5=abs(sub["ret_T5"][sub["ret_T5"]-TC<0].mean()) if (sub["ret_T5"]-TC<0).any() else 0.01
    b5 = w5/l5 if l5>0 else 0
    lev = kelly_leverage(wr5, b5, frac=0.3)
    flag = "OK" if net5>0 and wr5>0.55 else ("?" if net5>0 else "")
    print(f"  {sc:>6} {len(sub):>5} {wr3*100:>7.1f}% {wr5*100:>7.1f}% {net3*100:>+8.3f}% {net5*100:>+8.3f}%    f*={lev:>4.1f}x  {flag}")

# ══════════════════════════════════════════════════════════════════════
# SIG-B: r_score VALLEY (TURN UP)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SIG-B: r_score VALLEY (TURN SIGNAL)")
print("="*70)
print("  Dinh nghia: r_score[i] < r_score[i-1] AND r_score[i] < r_score[i+1]")
print("              AND delta_up (r_score[i+1]-r_score[i]) >= 0.010")

MIN_DELTA = 0.010

sigb_records = []
for i in range(2, n-6):
    rs_prev = r_score[i-1]; rs_cur = r_score[i]; rs_next = r_score[i+1]
    if any(np.isnan([rs_prev, rs_cur, rs_next])): continue
    if i < MIN_LB: continue

    # Valley condition
    if not (rs_cur < rs_prev and rs_cur < rs_next): continue
    delta_up = rs_next - rs_cur
    if delta_up < MIN_DELTA: continue

    # Features at valley
    # Prior peak: find last local max before this valley
    prior_peak_rs = max(r_score[max(0,i-30):i+1]) if not all(np.isnan(r_score[max(0,i-30):i+1])) else rs_cur
    valley_depth  = prior_peak_rs - rs_cur       # how much r_score fell
    # Duration of decline: sessions from prior peak to valley
    prior_peak_idx = i - 1
    for j in range(i-1, max(0,i-60), -1):
        if not np.isnan(r_score[j]) and r_score[j] == prior_peak_rs:
            prior_peak_idx = j; break
    valley_dur = i - prior_peak_idx

    state_val  = int(ss[i])
    vol_val    = float(vol20[i]) if not np.isnan(vol20[i]) else np.nan
    rsi_val    = float(rsi[i]) if not np.isnan(rsi[i]) else np.nan
    p1m_val    = float(p1m[i]) if not np.isnan(p1m[i]) else np.nan
    p3m_val    = float(p3m[i]) if not np.isnan(p3m[i]) else np.nan
    dd_val     = float(dd_a[i])

    rec = dict(
        date          = vni["time"].iloc[i],
        r_score_valley= rs_cur,
        delta_up      = delta_up,
        valley_depth  = valley_depth,
        valley_dur    = valley_dur,
        state         = state_val,
        state_name    = STATE_NAMES[state_val],
        vol_entry     = vol_val,
        rsi_entry     = rsi_val,
        p1m_entry     = p1m_val,
        p3m_entry     = p3m_val,
        dd_entry      = dd_val,
    )
    for h in [1,2,3,5,10]:
        rec[f"ret_T{h}"] = fwd_ret(i, h)
        rec[f"win_T{h}"] = (rec[f"ret_T{h}"] or 0) - TC > 0
    sigb_records.append(rec)

df_b = pd.DataFrame(sigb_records)
# Restrict to 2011+
df_b = df_b[df_b["date"] >= "2011-01-01"].reset_index(drop=True)
print(f"\n  Total valley signals (2011+): {len(df_b)}")
freq_b = len(df_b) / ((df_b["date"].max()-df_b["date"].min()).days/365.25)
print(f"  Frequency: {freq_b:.1f} signals/year")

# Overall stats
print("\n  --- Overall performance ---")
print(f"  {'Horizon':>8} {'n':>5} {'WR':>7} {'MeanRet':>9} {'MeanNet':>9} {'AvgWin':>8} {'AvgLoss':>8} {'PF':>6}")
print("  "+"-"*68)
for h in [1,2,3,5,10]:
    rets=df_b[f"ret_T{h}"].dropna().values
    if len(rets)==0: continue
    nets=rets-TC
    wr=(nets>0).mean(); mret=rets.mean()*100; mnet=nets.mean()*100
    avg_w=rets[nets>0].mean()*100 if (nets>0).any() else 0
    avg_l=rets[nets<0].mean()*100 if (nets<0).any() else 0
    pf=abs(rets[nets>0].sum()/rets[nets<0].sum()) if (nets<0).any() else 99
    print(f"  T+{h:>6}: {len(rets):>5} {wr*100:>6.1f}% {mret:>+8.3f}% {mnet:>+8.3f}% {avg_w:>+7.3f}% {avg_l:>+7.3f}% {pf:>6.2f}")

# Distribution by state
print("\n  --- Win rate by state ---")
for sn in ["CRISIS","BEAR","NEUTRAL","BULL","EX-BULL"]:
    sub=df_b[df_b["state_name"]==sn]
    if len(sub)<3: continue
    wr5=(sub["ret_T5"]-TC>0).mean(); n5=len(sub)
    net5=sub["ret_T5"].mean()-TC
    print(f"    {sn:<12}: n={n5:>4}  WR_T5={wr5*100:>5.1f}%  net_T5={net5*100:>+6.3f}%")

# Feature analysis (T+5)
print("\n  --- Feature vs Win Rate (T+5) ---")
df_b["win_T5_num"]=(df_b["ret_T5"]-TC>0).astype(float)
feature_analysis(df_b,["r_score_valley","delta_up","valley_depth","valley_dur","vol_entry","p1m_entry","rsi_entry"],"win_T5_num")

# ══════════════════════════════════════════════════════════════════════
# COMPOSITE SCORE & PROBABILITY — SIG-B
# ══════════════════════════════════════════════════════════════════════
print("\n  --- Composite probability model (SIG-B) ---")
print("  Rules duoc xac dinh tu feature analysis:")
print("  +1 diem: r_score_valley < 0.40  (valley o vung thap)")
print("  +1 diem: delta_up       > 0.015 (turn manh)")
print("  +1 diem: valley_depth   > 0.05  (giam sau du de bounce)")
print("  +1 diem: state in NEUTRAL/BULL  (khong o vung BEAR/CRISIS)")
print("  +1 diem: p1m_entry      < -3%   (da yeu truoc, co room hoi phuc)")
print("  +1 diem: vol_entry      < median (vol on dinh)")

median_vol_b = df_b["vol_entry"].median()
def score_sigb(row):
    s=0
    if not np.isnan(row["r_score_valley"]) and row["r_score_valley"]<0.40:    s+=1
    if not np.isnan(row["delta_up"])        and row["delta_up"]>0.015:         s+=1
    if not np.isnan(row["valley_depth"])    and row["valley_depth"]>0.05:      s+=1
    if row["state"] in [3,4,5]:                                                s+=1
    if not np.isnan(row["p1m_entry"])       and row["p1m_entry"]<-0.03:        s+=1
    if not np.isnan(row["vol_entry"])       and row["vol_entry"]<median_vol_b: s+=1
    return s

df_b["comp_score"]=df_b.apply(score_sigb,axis=1)

print(f"\n  {'Score':>6} {'n':>5} {'WR_T3':>8} {'WR_T5':>8} {'Net_T3':>9} {'Net_T5':>9} {'Kelly30%':>10} {'Leverage':>9}")
print("  "+"-"*68)
for sc in sorted(df_b["comp_score"].unique()):
    sub=df_b[df_b["comp_score"]==sc]
    wr3=(sub["ret_T3"]-TC>0).mean(); wr5=(sub["ret_T5"]-TC>0).mean()
    net3=sub["ret_T3"].mean()-TC; net5=sub["ret_T5"].mean()-TC
    w5=sub["ret_T5"][sub["ret_T5"]-TC>0].mean() if (sub["ret_T5"]-TC>0).any() else 0
    l5=abs(sub["ret_T5"][sub["ret_T5"]-TC<0].mean()) if (sub["ret_T5"]-TC<0).any() else 0.01
    b5=w5/l5 if l5>0 else 0
    lev=kelly_leverage(wr5,b5,frac=0.3)
    flag="OK" if net5>0 and wr5>0.55 else ("?" if net5>0 else "")
    print(f"  {sc:>6} {len(sub):>5} {wr3*100:>7.1f}% {wr5*100:>7.1f}% {net3*100:>+8.3f}% {net5*100:>+8.3f}%    f*={lev:>4.1f}x  {flag}")

# ══════════════════════════════════════════════════════════════════════
# COMBINED STRATEGY SIMULATION
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("COMBINED F-SYSTEM: SIG-A + SIG-B (score >= 3)")
print("  Chi giao dich khi composite score >= 3 (xac suat cao)")
print("  Hold T+5, leverage theo score")
print("="*70)

all_trades = []

# SIG-A high quality
for _,row in df_a.iterrows():
    if row["date"] < pd.Timestamp("2011-01-01"): continue
    sc = int(row["comp_score"])
    if sc < 3: continue
    r5 = row.get("ret_T5", float("nan"))
    if np.isnan(r5): continue
    all_trades.append(dict(date=row["date"], signal="SIG-A", score=sc,
                           ret_T5=r5, net_T5=r5-TC))

# SIG-B high quality
for _,row in df_b.iterrows():
    sc = int(row["comp_score"])
    if sc < 3: continue
    r5 = row.get("ret_T5", float("nan"))
    if np.isnan(r5): continue
    all_trades.append(dict(date=row["date"], signal="SIG-B", score=sc,
                           ret_T5=r5, net_T5=r5-TC))

df_trades = pd.DataFrame(all_trades).sort_values("date").reset_index(drop=True)

if len(df_trades) > 0:
    print(f"\n  Total high-quality trades (score>=3): {len(df_trades)}")
    yrs = (df_trades["date"].max()-df_trades["date"].min()).days/365.25
    print(f"  Frequency: {len(df_trades)/yrs:.1f} trades/year")
    print()
    wr = (df_trades["net_T5"]>0).mean()
    mean_net = df_trades["net_T5"].mean()
    avg_w = df_trades.loc[df_trades["net_T5"]>0,"net_T5"].mean()
    avg_l = df_trades.loc[df_trades["net_T5"]<0,"net_T5"].mean()
    pf_val= abs(df_trades.loc[df_trades["net_T5"]>0,"net_T5"].sum() /
                df_trades.loc[df_trades["net_T5"]<0,"net_T5"].sum()) if (df_trades["net_T5"]<0).any() else 99
    print(f"  WR={wr*100:.1f}%  MeanNet={mean_net*100:>+.3f}%  AvgWin={avg_w*100:>+.3f}%  AvgLoss={avg_l*100 if not np.isnan(avg_l) else 0:>+.3f}%  PF={pf_val:.2f}")

    # Trade list
    print(f"\n  {'Date':<12} {'Sig':>6} {'Score':>6} {'ret_T5':>9} {'net_T5':>9}")
    print("  "+"-"*50)
    for _,row in df_trades.iterrows():
        flag="W" if row["net_T5"]>0 else "L"
        print(f"  {str(row['date'].date()):<12} {row['signal']:>6} {row['score']:>6}  {row['ret_T5']*100:>+7.2f}%  {row['net_T5']*100:>+7.2f}%  {flag}")

# ══════════════════════════════════════════════════════════════════════
# LEVERAGE TABLE
# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("LEVERAGE RECOMMENDATION TABLE")
print("(Fractional Kelly 30%, horizon T+5, TC=0.1%)")
print("="*70)
print(f"\n  {'Signal':>8} {'Score':>6} {'n':>5} {'P(win)':>8} {'b=W/L':>7} {'f*':>6} {'Kelly30%':>9} {'Rec_Lev':>10}")
print("  "+"-"*65)

for sig_name, df_sig, score_col in [("SIG-A", df_a, "comp_score"),("SIG-B", df_b, "comp_score")]:
    for sc in sorted(df_sig[score_col].unique()):
        sub=df_sig[df_sig[score_col]==sc]
        wr5=(sub["ret_T5"]-TC>0).mean()
        w5=sub["ret_T5"][sub["ret_T5"]-TC>0].mean() if (sub["ret_T5"]-TC>0).any() else 0
        l5=abs(sub["ret_T5"][sub["ret_T5"]-TC<0].mean()) if (sub["ret_T5"]-TC<0).any() else 0.01
        b5=w5/l5 if l5>0 else 0
        f_star=(wr5*b5-(1-wr5))/b5 if b5>0 else 0
        kelly30=max(0,f_star)*0.3
        lev=kelly_leverage(wr5,b5,0.3)
        print(f"  {sig_name:>8} {sc:>6} {len(sub):>5} {wr5*100:>7.1f}% {b5:>7.2f} {f_star:>6.3f}  {kelly30*100:>7.1f}%  {lev:>6.2f}x")
    print()

print("""
  Giai thich:
  P(win)    = xac suat thang sau TC
  b = W/L   = avg_win / avg_loss (profit factor ratio)
  f*        = Kelly fraction toi uu
  Kelly 30% = fractional Kelly (an toan) = 30% x f*
  Rec_Lev   = leverage khuyen nghi = Kelly30% x 10 (cap 3x)
""")
print("Done.")
