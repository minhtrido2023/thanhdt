# -*- coding: utf-8 -*-
"""
custom30v_singlebook_faithful.py — FAITHFUL single-book sim of the custom30 basket run "like production"
(DT5G-gated), for selectors yieldcombo (=custom30V) vs v3comp (full 8L value v3). Adds the costs the
crude variant-C missed: (a) DT5G exposure-TRANSITION turnover TC (de-risk/re-risk trades), (b) BORROW
cost on EXBULL leverage (>100%), (c) quarterly rebal TC, (d) slippage in the TC rate. Reports CAGR/
Sharpe/DD/Calmar 2014→now & 2018→now + BY-YEAR (sustainability of v3comp's edge vs yieldcombo).
"""
import os, sys, numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L","/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

W_STATE={1:0.0,2:0.2,3:0.7,4:1.0,5:1.3}   # DT5G production 5-state allocation
TC=0.003; REBAL_TURN=0.35; BORROW=0.10/252.0   # 0.3% slippage+cost/unit turnover; 10%/yr borrow on leverage
st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live s"); st["time"]=pd.to_datetime(st["time"])
SD=dict(zip(st["time"],st["state"]))

def metrics(r):
    s=(1+r).cumprod(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; spd=len(r)/yrs
    sh=r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0; dd=(s/s.cummax()-1).min()
    return cagr*100, sh, dd*100, (cagr*100)/abs(dd*100) if dd<0 else 0

def faithful(sel):
    os.environ["BASKET_SELECT"]=sel
    lvl,_,memdf,_=cb.build_pit(bq,"2014-01-01","2026-06-19",quality="none",rebal="q2m5",gate_rating=3,weight_scheme="namecap")
    s=pd.Series(lvl).sort_index(); s.index=pd.to_datetime(s.index); rb=s.pct_change().dropna()
    idx=rb.index
    w=pd.Series([W_STATE.get(int(SD.get(d,np.nan)) if pd.notna(SD.get(d,np.nan)) else 3,0.7) for d in idx],index=idx)
    w=w.ffill().bfill(); w_lag=w.shift(1).fillna(0.7)               # causal exposure (T-1 state)
    r=w_lag*rb                                                       # gated gross return
    r=r-np.maximum(0.0,w_lag-1.0)*BORROW                            # borrow on leverage (EXBULL)
    r=r-(w_lag.diff().abs().fillna(0.0))*TC                         # exposure-TRANSITION turnover TC
    rebd=set(pd.to_datetime(memdf["rebal_date"].unique()))
    r=r-pd.Series([REBAL_TURN*TC*w_lag[d] if d in rebd else 0.0 for d in idx],index=idx)  # quarterly rebal TC
    return rb, r

print(f"costs: TC={TC} (slippage incl), rebal_turn={REBAL_TURN}, borrow={BORROW*252:.0%}/yr on leverage; DT5G W={W_STATE}")
WINS=[("FULL 2014→now",None,None),("IS 2014-2019",None,pd.Timestamp("2019-12-31")),
      ("OOS 2020→now",pd.Timestamp("2020-01-01"),None)]
RES={}
for sel in ["yieldcombo","v3comp"]:
    rb,r=faithful(sel); RES[sel]=(rb,r)
    print(f"\n### {sel}  single-book faithful (DT5G-gated) — WALK-FORWARD ###")
    for tag,a,b in WINS:
        rr=r.copy()
        if a is not None: rr=rr[rr.index>=a]
        if b is not None: rr=rr[rr.index<=b]
        c,sh,dd,cal=metrics(rr); print(f"  {tag:<14} CAGR {c:6.2f}%  Sharpe {sh:.2f}  MaxDD {dd:6.1f}%  Calmar {cal:.2f}")

print("\n### SUSTAINABILITY — by-year NAV return %, yieldcombo vs v3comp (faithful gated) ###")
ry=RES["yieldcombo"][1]; rv=RES["v3comp"][1]
print(f"  {'year':<6}{'yieldcombo':>12}{'v3comp':>10}{'v3-yc':>9}")
yrs=sorted(set(ry.index.year))
pos=0;tot=0
for y in yrs:
    a=(1+ry[ry.index.year==y]).prod()-1; b=(1+rv[rv.index.year==y]).prod()-1
    print(f"  {y:<6}{a*100:>11.1f}%{b*100:>9.1f}%{(b-a)*100:>+8.1f}")
    tot+=1; pos+= 1 if b>a else 0
print(f"  v3comp beats yieldcombo in {pos}/{tot} years")
print("\n(ref) gross index (no cost/no gate): yieldcombo 36.5% / v3comp 38.0% (2014→now)")
print("(ref) Production V2.3 multi-book 2018→now (audited): 25.07% / Sh1.52 / DD-29.9 / Cal0.84")
