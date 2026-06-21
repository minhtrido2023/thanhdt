# -*- coding: utf-8 -*-
"""value_bull_when_study.py — WHEN study: tín hiệu MỀM nào báo "giai đoạn NGUY HIỂM" trong bull (user 2026-06-20).
KHÔNG dùng ngưỡng cứng BULL/EXBULL. Trong các phiên bull (state 4/5, base), test tín hiệu liên tục nào dự báo
forward-return THẤP + drawdown phía trước SÂU = cờ euphoria/đỉnh ("be fearful"). Tín hiệu candidate:
  breadth (level MA200), breadth_roc20 (rollover), ew_minus_cap20 (small/broad dẫn = junk-rally), vni_rsi14,
  extension (VNI/MA200-1), vni_vol20 (complacency→spike). Outcome: fwd_r3 (63d ret) + fwd_maxdd (DD sâu nhất 63d tới).
Cờ nguy hiểm = IC ÂM vs fwd_r3 VÀ vs fwd_maxdd; tercile cao → fwd thấp + DD sâu. Weekly sample (giảm overlap)."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude"); os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket as cb
from pt_dates import detect_end_date
START,END="2010-01-01",detect_end_date()

# EW vs cap baskets (small/broad-leadership proxy)
print("[1] build ew + capwt baskets ...")
lc,_,_,_=cb.build_pit(bq,START,END,quality="none",rebal="q2m5",gate_rating=3,weight_scheme="capwt")
le,_,_,_=cb.build_pit(bq,START,END,quality="none",rebal="q2m5",gate_rating=3,weight_scheme="ew")
cap=pd.Series(lc); cap.index=pd.to_datetime(cap.index); cap=cap.sort_index().astype(float)
ew =pd.Series(le); ew.index =pd.to_datetime(ew.index);  ew =ew.sort_index().astype(float)
ewmcap=(ew.pct_change(20)-cap.pct_change(20))   # >0 = small/broad dẫn (junk-rally)

# VNINDEX signals + forward outcomes
v=bq(f"SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time")
v["time"]=pd.to_datetime(v["time"]); v=v.set_index("time")["Close"].astype(float)
ma200=v.rolling(200,min_periods=100).mean(); ma50=v.rolling(50,min_periods=30).mean()
ext=v/ma200-1
delta=v.diff(); up=delta.clip(lower=0).rolling(14).mean(); dn=(-delta.clip(upper=0)).rolling(14).mean()
rsi=100-100/(1+up/dn.replace(0,np.nan))
vol20=v.pct_change().rolling(20).std()*np.sqrt(252)
N=63
fwd_r3=v.shift(-N)/v-1
fwd_maxdd=pd.Series(index=v.index,dtype=float)
vals=v.values
for i in range(len(v)):
    j=min(i+N,len(v)-1)
    if j>i:
        w=vals[i+1:j+1]/vals[i]-1
        fwd_maxdd.iloc[i]=w.min() if len(w) else np.nan

# breadth
br=bq(f"""SELECT time, AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 0.0 ELSE 1.0 END) AS bd
FROM tav2_bq.ticker_prune WHERE time>='{START}' AND MA200>0 GROUP BY time""")
br["time"]=pd.to_datetime(br["time"]); bd=br.set_index("time")["bd"].sort_index()
bd_roc=bd-bd.shift(20)

# state (base)
st=bq(f"SELECT time,state FROM tav2_bq.vnindex_5state WHERE time>='{START}'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep='last')].sort_index()

df=pd.DataFrame({"vni":v,"breadth":bd.reindex(v.index,method="ffill"),"bd_roc":bd_roc.reindex(v.index,method="ffill"),
    "ewmcap":ewmcap.reindex(v.index,method="ffill"),"rsi":rsi,"ext":ext,"vol20":vol20,
    "state":state.reindex(v.index,method="ffill"),"fwd_r3":fwd_r3,"fwd_maxdd":fwd_maxdd}).dropna(subset=["fwd_r3","fwd_maxdd","state"])
bull=df[df["state"].isin([4,5])].iloc[::5]   # weekly sample, bull/exbull only
print(f"[2] bull/exbull weekly obs = {len(bull)}  | mean fwd_r3 {bull['fwd_r3'].mean()*100:+.1f}%  "
      f"mean fwd_maxdd {bull['fwd_maxdd'].mean()*100:+.1f}%")

sigs={"breadth(level)":"breadth","breadth_roc20":"bd_roc","ew_minus_cap20(junk-lead)":"ewmcap",
      "vni_rsi14":"rsi","extension(VNI/MA200)":"ext","vni_vol20":"vol20"}
def sp(a,b):
    m=a.notna()&b.notna(); return a[m].rank().corr(b[m].rank()) if m.sum()>=20 else np.nan
print(f"\n{'signal':26s} {'IC_vs_fwd_r3':>13s} {'IC_vs_fwd_maxdd':>16s}   (âm cả hai = cờ NGUY HIỂM)")
for nm,c in sigs.items():
    print(f"{nm:26s} {sp(bull[c],bull['fwd_r3']):+13.3f} {sp(bull[c],bull['fwd_maxdd']):+16.3f}")
print(f"\nTercile (signal cao→thấp): mean fwd_r3 | mean fwd_maxdd")
for nm,c in sigs.items():
    try: bull["_t"]=pd.qcut(bull[c],3,labels=["LO","MID","HI"])
    except Exception: continue
    g=bull.groupby("_t",observed=True)
    r=g["fwd_r3"].mean()*100; m=g["fwd_maxdd"].mean()*100
    print(f"  {nm:26s} HI[{r.get('HI',float('nan')):+5.1f}% / {m.get('HI',float('nan')):+5.1f}]  "
          f"LO[{r.get('LO',float('nan')):+5.1f}% / {m.get('LO',float('nan')):+5.1f}]")
print("\nĐỌC: cờ nguy hiểm = HI-tercile có fwd_r3 THẤP + fwd_maxdd SÂU (vs LO). Đó là tín hiệu mềm để giảm deploy.")
