# -*- coding: utf-8 -*-
"""
Phan tich: He thong co tang dung co hoi phuc hoi sau khung hoang khong?
- Tim tat ca lan thoat CRISIS -> state cao hon
- Do forward returns tu diem chuyen trang thai
- So sanh: weight he thong vs weight ly tuong neu dung don bay cao hon
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Rebuild states (giong backtest_workflow.py) ────────────────────────────
vni = pd.read_csv(WORKDIR + "/data/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

if os.path.exists(WORKDIR+"/data/breadth_data.csv"):
    br = pd.read_csv(WORKDIR+"/data/breadth_data.csv")
    br["time"] = pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr, k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out

def _rank(arr, min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        v=arr[:t+1]; v=v[~np.isnan(v)]
        if len(v)>=min_lb: out[t]=np.sum(v<=arr[t])/len(v)
    return out

p3m=np.full(n,np.nan)
if "Change_3M" in vni.columns:
    cv=pd.to_numeric(vni["Change_3M"],errors="coerce").values
    for i in range(n):
        p3m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-60]-1 if i>=60 and close[i-60]>0 else np.nan)
else:
    for i in range(60,n):
        if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1

p1m=np.full(n,np.nan)
if "Change_1M" in vni.columns:
    cv=pd.to_numeric(vni["Change_1M"],errors="coerce").values
    for i in range(n):
        p1m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-20]-1 if i>=20 and close[i-20]>0 else np.nan)
else:
    for i in range(20,n):
        if close[i-20]>0: p1m[i]=close[i]/close[i-20]-1

ma200=pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev=np.where((ma200>0)&~np.isnan(ma200),close/ma200-1,np.nan)
rsi=np.full(n,np.nan); au=ad=np.nan
for i in range(1,n):
    d=close[i]-close[i-1]; u=max(d,0); dn=max(-d,0)
    if np.isnan(au):
        if i>=14:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if au+ad>0: rsi[i]=au/(au+ad)
    else:
        au=(au*13+u)/14; ad=(ad*13+dn)/14
        if au+ad>0: rsi[i]=au/(au+ad)

e12=_ema(close,2/13); e26=_ema(close,2/27)
macd_l=e12-e26; sig9=_ema(macd_l,2/10)
macd_hist=np.where(np.arange(n)>=33,macd_l-sig9,np.nan)
hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfm[i-14:i]*vol[i-14:i])/vs

br_arr=vni["breadth"].values if "breadth" in vni.columns else np.full(n,np.nan)
W={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":br_arr}
ranks={k:_rank(v) for k,v in raw.items()}
score=np.full(n,np.nan)
for t in range(n):
    av={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av)>=3:
        ws=sum(W[k] for k in av); score[t]=sum(av[k]*W[k] for k in av)/ws

r_score=_rank(score)
r_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema[t-1] if t>0 else np.nan
    r_ema[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)

pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_p90[t]=np.nanpercentile(h,90)

rm_c=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd_raw=np.where(rm_c>0,close/rm_c-1,0.0)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20[i]=np.std(w2)*np.sqrt(SPY)
avg_vol=np.full(n,np.nan)
for t in range(n):
    h=v20[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol[t]=np.mean(h)

def classify(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    elif rs<0.20: return 2
    elif rs<0.70: return 3
    elif rs<0.90: return 4
    else: return 5

st=np.array([classify(r) for r in r_ema])
for i in range(n):
    s=st[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s==5: s=4
    if dd_raw[i]<-0.25 and s>=4: s=3
    if not np.isnan(avg_vol[i]) and not np.isnan(v20[i]) and v20[i]>1.5*avg_vol[i] and s==5: s=4
    st[i]=s

def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan,index=vni.index)
_mask=vni["time"]>="2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")

bear_mask=(
 ((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&
  (_DM1WC/_DM3MC>1.028)&(_DM3MM/_DM1WM>1.11)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&
  (_DM1WC/_DM3MC>1.008)&(_DM3MM/_DM1WM>1.10)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)
).values.astype(bool)

bull_mask=(
 ((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&
  (_DMACD>0)&(_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&
  (_CL1M<1.20)&(_CL1W<1.025)&_mask)
).values.astype(bool)

pe_rank=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_rank[t]=np.sum(h<=pe_arr[t])/len(h)

p3m_rank=ranks["P3M"]
streak=np.zeros(n,dtype=bool); _k=0
for i in range(n):
    if not np.isnan(r_ema[i]) and r_ema[i]>0.65: _k+=1
    else: _k=0
    if _k>=10: streak[i]=True

gate_active=False; gate_start=-1
st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: gate_active=True; gate_start=i
    if gate_active:
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gate_start>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]):
                gate_active=False

def rolling_mode(states,w=15):
    out=states.copy()
    for t in range(w-1,len(states)):
        ww=states[t-w+1:t+1]; vs,cs=np.unique(ww,return_counts=True)
        cands=vs[cs==cs.max()]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out

def min_stay_filter(states,m=7):
    out=states.copy(); changed=True
    while changed:
        changed=False; i=0
        while i<len(out):
            j=i+1
            while j<len(out) and out[j]==out[i]: j+=1
            if j-i<m:
                fill=out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j]=fill; changed=True
            i=j
    return out

st_smooth=min_stay_filter(rolling_mode(st_dvg,15),7)
TARGET_W={1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ── 1. Tim cac diem thoat CRISIS (CRISIS → state khac) ────────────────────
print()
print("="*76)
print("  PHAN TICH: CO HOI PHUC HOI SAU KHUNG HOANG")
print("="*76)

# Tim tat ca chuyen sang: CRISIS -> non-CRISIS (T+1 sau lan dau)
exits = []  # (index_exit, date, next_state, dd_at_exit, sessions_in_crisis)
i = 0
while i < n-1:
    if st_smooth[i] == 1:
        # Bat dau mot giai doan CRISIS
        start = i
        while i < n-1 and st_smooth[i] == 1:
            i += 1
        # i bay gio la phien dau tien cua state moi (T+0 thoat)
        dur = i - start
        if i < n:
            exits.append({
                "idx": i,
                "date": vni["time"].iloc[i],
                "from_state": 1,
                "to_state": st_smooth[i],
                "dur_crisis": dur,
                "dd_at_exit": dd_raw[i],
                "close_at_exit": close[i],
            })
    else:
        i += 1

print(f"\n  Tim thay {len(exits)} lan thoat CRISIS -> state khac (tu 2000)")

# ── 2. Do forward returns sau khi thoat CRISIS ────────────────────────────
horizons = [5, 10, 20, 40, 60, 120]  # phien

print(f"\n  {'─'*74}")
print(f"  FORWARD RETURNS sau khi thoat CRISIS (T+0 = phien dau tien khong con CRISIS)")
print(f"  {'─'*74}")
print(f"  {'Lan':>3}  {'Ngay':>12}  {'Sang':>8}  {'DDkhi-thoat':>11}  {'Dur':>6}", end="")
for h in horizons:
    print(f"  {f'T+{h}':>7}", end="")
print()
print(f"  {'─'*74}")

rows_data = []
for e in exits:
    idx = e["idx"]
    fwd = {}
    for h in horizons:
        if idx + h < n and close[idx] > 0:
            fwd[h] = close[idx+h]/close[idx] - 1
        else:
            fwd[h] = np.nan
    rows_data.append({**e, **{f"fwd_{h}": fwd[h] for h in horizons}})
    next_name = STATE_NAMES.get(e["to_state"], "?")
    date_str = e["date"].strftime("%Y-%m-%d")
    dur_str = f"{e['dur_crisis']}p"
    dd_str = f"{e['dd_at_exit']*100:+.1f}%"
    print(f"  {exits.index(e)+1:>3}  {date_str:>12}  {next_name:>8}  {dd_str:>11}  {dur_str:>6}", end="")
    for h in horizons:
        v = fwd[h]
        s = f"{v*100:+.1f}%" if not np.isnan(v) else "  N/A"
        print(f"  {s:>7}", end="")
    print()

# ── 3. Thong ke tong hop ─────────────────────────────────────────────────
print(f"\n  {'─'*74}")
print(f"  THONG KE TONG HOP (trung vi va trung binh forward return)")
print(f"  {'─'*74}")
print(f"  {'':>25}", end="")
for h in horizons: print(f"  {f'T+{h}':>7}", end="")
print()

for stat in ["Trung binh", "Trung vi", "% duong", "Min", "Max"]:
    print(f"  {stat:<25}", end="")
    for h in horizons:
        vals = [r[f"fwd_{h}"] for r in rows_data if not np.isnan(r[f"fwd_{h}"])]
        if not vals:
            print(f"  {'N/A':>7}", end="")
            continue
        if stat == "Trung binh":  v = np.mean(vals)
        elif stat == "Trung vi":  v = np.median(vals)
        elif stat == "% duong":   v = np.mean([x>0 for x in vals]); print(f"  {v*100:>6.0f}%", end=""); continue
        elif stat == "Min":       v = np.min(vals)
        else:                     v = np.max(vals)
        print(f"  {v*100:>+6.1f}%", end="")
    print()

# ── 4. Phan tich: weight thuc te vs muc ly tuong ─────────────────────────
print(f"\n\n{'='*76}")
print(f"  HE THONG DANG NAM BAT BAO NHIEU % NHJP PHUC HOI?")
print(f"  (tinh theo weight thuc te sau ramp 3 phien)")
print(f"{'='*76}")

# Simulate weight thuc te (ramp logic)
w_actual = np.zeros(n)
w_sim = TARGET_W[3]
for t in range(1, n):
    target = TARGET_W[st_smooth[t-1]]
    diff = target - w_sim
    w_new = target if abs(diff) < 0.03 else w_sim + diff/3
    w_sim = float(np.clip(w_new, 0.0, 1.30))
    w_actual[t] = w_sim

print(f"\n  {'Lan':>3}  {'Ngay thoat':>12}  {'Sang':>8}  {'w T+0':>7}  {'w T+3':>7}  {'w T+5':>7}  {'Fwd T+20':>9}  {'HT huong':>9}  {'TP 120%':>9}")
print(f"  {'─'*80}")

for e in rows_data:
    idx = e["idx"]
    next_name = STATE_NAMES.get(e["to_state"], "?")
    date_str = e["date"].strftime("%Y-%m-%d")
    w0 = w_actual[idx]   if idx   < n else np.nan
    w3 = w_actual[idx+3] if idx+3 < n else np.nan
    w5 = w_actual[idx+5] if idx+5 < n else np.nan
    fwd20 = e.get("fwd_20", np.nan)

    # HT huong duoc: trung binh weight trong 20 phien x forward return 20
    if idx+20 < n and close[idx] > 0:
        ws_20 = w_actual[idx:idx+20]
        mkt_20 = close[idx+20]/close[idx] - 1
        # tinh return thuc te he thong trong 20 phien
        pv_slice = 1.0
        for t2 in range(idx, min(idx+20, n-1)):
            rm = close[t2+1]/close[t2]-1 if close[t2]>0 else 0
            pv_slice *= (1 + w_actual[t2+1]*rm)
        ht_20 = pv_slice - 1
    else:
        mkt_20 = np.nan; ht_20 = np.nan

    # Neu dung 120% ngay tu phien thoat (trong 20 phien)
    if idx+20 < n and close[idx] > 0:
        pv_120 = 1.0
        for t2 in range(idx, min(idx+20, n-1)):
            rm = close[t2+1]/close[t2]-1 if close[t2]>0 else 0
            w120 = min(1.20, w_actual[t2+1] + 0.20)  # tang them 20pp
            pv_120 *= (1 + w120*rm)
        lev120_20 = pv_120 - 1
    else:
        lev120_20 = np.nan

    print(f"  {rows_data.index(e)+1:>3}  {date_str:>12}  {next_name:>8}  {w0:>6.0%}  {w3:>7.0%}  {w5:>7.0%}  {fwd20*100:>+8.1f}%" if not np.isnan(fwd20) else f"  {rows_data.index(e)+1:>3}  {date_str:>12}  {next_name:>8}  {w0:>6.0%}  {w3:>7.0%}  {w5:>7.0%}  {'N/A':>9}", end="")
    if not np.isnan(ht_20):
        print(f"  {ht_20*100:>+8.1f}%  {lev120_20*100:>+8.1f}%", end="")
    else:
        print(f"  {'N/A':>9}  {'N/A':>9}", end="")
    print()

# ── 5. Lag analysis: tu day thuc su den khi he thong nhan ra ─────────────
print(f"\n\n{'='*76}")
print(f"  LAG: TU DAY TUNG (Close thap nhat trong CRISIS) DEN KHI THOAT")
print(f"{'='*76}")
print(f"\n  Khi CRISIS bat dau, Close thap nhat xuat hien o dau trong giai doan?")
print(f"  Day thuc = phien Close thap nhat trong giai doan CRISIS")
print(f"  Lag = so phien tu day thuc su den khi he thong chuyen sang state moi")
print()
print(f"  {'Lan':>3}  {'Bat dau CRISIS':>14}  {'Thoat CRISIS':>12}  {'Dur':>5}  {'Day thuc':>10}  {'Lag(p)':>7}  {'Gain bot-exit':>13}")
print(f"  {'─'*76}")

i2 = 0; ep_idx = 0
while i2 < n-1 and ep_idx < len(rows_data):
    e = rows_data[ep_idx]
    idx_exit = e["idx"]
    dur = e["dur_crisis"]
    idx_start = idx_exit - dur

    # Tim day thuc (close thap nhat trong CRISIS)
    segment = close[idx_start:idx_exit]
    bot_offset = np.argmin(segment)
    bot_idx = idx_start + bot_offset
    bot_date = vni["time"].iloc[bot_idx].strftime("%Y-%m-%d")
    lag = idx_exit - bot_idx  # so phien tu day den khi thoat
    gain_bot_exit = close[idx_exit]/close[bot_idx] - 1 if close[bot_idx] > 0 else np.nan

    start_date = vni["time"].iloc[idx_start].strftime("%Y-%m-%d")
    exit_date  = e["date"].strftime("%Y-%m-%d")
    print(f"  {ep_idx+1:>3}  {start_date:>14}  {exit_date:>12}  {dur:>5}  {bot_date:>10}  {lag:>7}  {gain_bot_exit*100:>+12.1f}%")
    ep_idx += 1
    i2 = idx_exit + 1

# ── 6. Ket luan dinh luong ────────────────────────────────────────────────
print(f"\n\n{'='*76}")
print(f"  KET LUAN DINH LUONG")
print(f"{'='*76}")

fwd20_all = [r["fwd_20"] for r in rows_data if not np.isnan(r.get("fwd_20", np.nan))]
fwd60_all = [r["fwd_60"] for r in rows_data if not np.isnan(r.get("fwd_60", np.nan))]

print(f"""
  Tong so lan thoat CRISIS  : {len(rows_data)}

  Forward return VNINDEX sau khi thoat CRISIS:
    T+20 : trung binh {np.mean(fwd20_all)*100:+.1f}%, trung vi {np.median(fwd20_all)*100:+.1f}%
    T+60 : trung binh {np.mean(fwd60_all)*100:+.1f}%, trung vi {np.median(fwd60_all)*100:+.1f}%

  Weight thuc te he thong khi moi thoat CRISIS:
    T+0  : thuong la 0% (con an theo CRISIS truoc do, ramp chua bat dau)
    T+3  : ~23% (1/3 ramp lan 1: neu thoat sang NEUTRAL target=70%)
    T+5  : ~38% (sau 2 lan ramp)
    → He thong bi TRE so voi thi truong ~5-10 phien khi chuyen trang thai

  Phan tich lag:
    He thong nhan ra day sau trung binh {np.mean([rows_data[i2]["idx"]-((rows_data[i2]["idx"]-rows_data[i2]["dur_crisis"])+np.argmin(close[rows_data[i2]["idx"]-rows_data[i2]["dur_crisis"]:rows_data[i2]["idx"]])) for i2 in range(len(rows_data))]):.0f} phien
    (tu day thuc su den khi state chuyen sang NEUTRAL/BULL)
""")

# Tinh lag trung binh
lags = []
gains_bot_exit = []
for e in rows_data:
    idx_exit = e["idx"]; dur = e["dur_crisis"]; idx_start = idx_exit - dur
    if idx_start >= 0:
        seg = close[idx_start:idx_exit]
        if len(seg) > 0:
            bot_offset = np.argmin(seg)
            lags.append(idx_exit - (idx_start + bot_offset))
            if close[idx_start+bot_offset] > 0:
                gains_bot_exit.append(close[idx_exit]/close[idx_start+bot_offset] - 1)

print(f"  Lag trung binh (day -> thoat CRISIS): {np.mean(lags):.0f} phien (trung vi: {np.median(lags):.0f} phien)")
print(f"  Gain tu day den khi thoat CRISIS     : trung binh {np.mean(gains_bot_exit)*100:+.1f}%, trung vi {np.median(gains_bot_exit)*100:+.1f}%")
print(f"  → Phan cua nhip phuc hoi da 'bi bo lo' truoc khi he thong kip chuyen trang thai")
print()
print(f"  SO SANH: cach hien tai vs don bay cao hon NGAY SAU CRISIS:")
print(f"    T+20 trung binh VNINDEX    : {np.mean(fwd20_all)*100:+.1f}%")

# ht vs ht120
ht_list=[]; ht120_list=[]
for e in rows_data:
    idx=e["idx"]
    if idx+20 < n and close[idx] > 0:
        pv=1.0; pv120=1.0
        for t2 in range(idx, min(idx+20, n-1)):
            rm=close[t2+1]/close[t2]-1 if close[t2]>0 else 0
            pv     *= (1 + w_actual[t2+1]*rm)
            w120    = min(1.20, w_actual[t2+1]+0.20)
            pv120  *= (1 + w120*rm)
        ht_list.append(pv-1); ht120_list.append(pv120-1)

print(f"    T+20 trung binh HT hien tai: {np.mean(ht_list)*100:+.1f}%  (= {np.mean(ht_list)/np.mean(fwd20_all)*100:.0f}% cua thi truong)")
print(f"    T+20 trung binh HT w+20pp  : {np.mean(ht120_list)*100:+.1f}%  (= {np.mean(ht120_list)/np.mean(fwd20_all)*100:.0f}% cua thi truong)")
print(f"    Chenh lech                 : {(np.mean(ht120_list)-np.mean(ht_list))*100:+.2f}pp trong cua so T+20 sau CRISIS")
print()
print(f"  QUAN TRONG - Rui ro cua don bay cao hon sau CRISIS:")
print(f"    - Co {sum(1 for v in fwd20_all if v<0)} / {len(fwd20_all)} lan T+20 < 0 (false recovery)")
print(f"    - Max loss T+20 sau CRISIS : {min(fwd20_all)*100:+.1f}%")
print(f"    - Don bay 120% trong false recovery → thiet hai nang hon")
print()
