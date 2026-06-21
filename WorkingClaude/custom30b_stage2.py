# -*- coding: utf-8 -*-
"""custom30b_stage2.py — improved custom30B: selector (+RSI, Part A winner) x liquidity-floor sweep
(2/5/10B, Part B). Basket return on BULL/EXBULL days only, full + IS/OOS signature + Sharpe/DD/std.
Also reports basket median member daily-liquidity at last rebal (capacity check for low floors)."""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket

END=os.environ.get("AUDIT_END","2026-06-19"); START="2014-01-01"
st=bq(f"SELECT time,state FROM tav2_bq.vnindex_5state_dt5g_live WHERE time>='{START}' AND time<='{END}'")
st["time"]=pd.to_datetime(st["time"]); state=st.set_index("time")["state"]
state=state[~state.index.duplicated(keep="last")].sort_index()
bull_days=state[state.isin([4,5])].index

def build(env):
    for k,v in env.items(): os.environ[k]=str(v)
    lvl,adv,mem,raw=custom_basket.build_pit(bq,START,END,top_n=30,gate_rating=3,rebal="q2m5",weight_scheme="namecap")
    for k in env: os.environ.pop(k,None)
    s=pd.Series(lvl); s.index=pd.to_datetime(s.index); s=s.sort_index()
    # capacity: median member ADV at last rebal
    last_q=mem["rebal_date"].max(); names=mem[mem.rebal_date==last_q]["ticker"].tolist()
    med_adv=np.median([adv.get(n,{}).get(pd.Timestamp(END),np.nan) if isinstance(adv.get(n),dict) else np.nan for n in names]) if names else np.nan
    return s, len(names)
def met(r):
    r=r.dropna()
    if len(r)<20: return None
    nav=(1+r).cumprod(); yrs=(r.index[-1]-r.index[0]).days/365.25
    cg=nav.iloc[-1]**(1/yrs)-1; dd=(nav/nav.cummax()-1).min()
    return dict(c=cg*100,sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0,dd=dd*100,
                cal=cg/abs(dd) if dd<0 else 0,std=r.std()*np.sqrt(252)*100)
def bo(s): r=s.pct_change(); return r[r.index.isin(bull_days)]
def win(r,lo,hi): return r[(r.index>=lo)&(r.index<=hi)]
def rep(lbl,env):
    s,nm=build(env); rb=bo(s)
    f=met(rb); i=met(win(rb,"2014-01-01","2019-12-31")); o=met(win(rb,"2020-01-01","2026-12-31")); fa=met(s.pct_change())
    if not f: print(f"  {lbl:30s} n/a"); return
    sig="PASS" if (i and o and i['c']>0 and o['c']>0) else "fail"
    print(f"  {lbl:30s} BULL {f['c']:5.1f}%/Sh{f['sh']:.2f}/DD{f['dd']:6.1f}/std{f['std']:4.0f} "
          f"IS {i['c']:5.1f} OOS {o['c']:5.1f} [{sig}] all{fa['c']:5.1f}%")

print(f"{START}->{END} bull/exbull days={len(bull_days)}\n")
print("=== SELECTOR (floor 10B): does RSI help on top of 1/PE / 1/PE+mom? ===")
rep("pemom1.0 (champ)",        {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":10,"BASKET_MOM_W":1.0})
rep("petop + rsi0.5",         {"BASKET_SELECT":"petop","BASKET_LIQ_FLOOR_B":10,"BASKET_RSI_W":0.5})
rep("pemom1.0 + rsi0.5",      {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":10,"BASKET_MOM_W":1.0,"BASKET_RSI_W":0.5})
rep("pemom1.0 + rsi1.0",      {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":10,"BASKET_MOM_W":1.0,"BASKET_RSI_W":1.0})
print("\n=== LIQUIDITY FLOOR sweep (selector = pemom1.0+rsi0.5): does 2B open better bull opps? ===")
rep("floor 10B",  {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":10,"BASKET_MOM_W":1.0,"BASKET_RSI_W":0.5})
rep("floor  5B",  {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":5, "BASKET_MOM_W":1.0,"BASKET_RSI_W":0.5})
rep("floor  2B",  {"BASKET_SELECT":"pemom","BASKET_LIQ_FLOOR_B":2, "BASKET_MOM_W":1.0,"BASKET_RSI_W":0.5})
print("\nREAD: higher BULL CAGR+Sharpe & PASS = better. std up at low floor = expect (smaller caps); namecap diversifies.")
print("Capacity: floor 2B => 1/30 of NAV per name must fit ~2B/day ADV (small-NAV only). Note tradeoff explicitly.")
