# -*- coding: utf-8 -*-
"""
test_dt5g_breadth_gate.py
=========================
(1) Implement a VN-LOCAL BREADTH GATE on the US pillar (Pillar B) of DT5G and validate.

Rule: a US-driven cap (VIX/SPX panic) may bind ONLY when VN breadth ALSO confirms
weakness — Breadth_MA200 is VALID (universe large enough) AND below a threshold.
- Healthy/broad VN breadth while US panics  -> US-VN DECOUPLING -> suppress US cap.
- Breadth invalid (nascent <~30-stock market, e.g. 2001) -> can't confirm -> suppress
  (so the overlay self-deactivates in the immature market — data IS the maturity gate).
- The DOMESTIC SBV pillar (Pillar A) is UNCHANGED (it already is a VN signal).
- bull-bypass kept.

Breadth source: Downloads/preprocess_others_market_indicators_all_tickers.csv
(Breadth_MA200 = frac stocks > MA200, from 2000; meaningful from ~2007 when universe>100).

Compares DT4 / DT5G / DT5G+BGATE on pure-index NAV across periods + crisis windows,
and prints the episode ledger under BGATE (the 2001 false-positive should vanish while
2008/2011/2020/2023 survive). Output: data/dt5g_breadth_gate.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from macro_state_live import _dt_4gate, _commit, P, NEUTRAL, CRISIS, BEAR
from sbv_macro_overlay import SBV_REFI_EVENTS

SNAME = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL",9:"none"}
STATE_ALLOC = {1:0.0,2:0.2,3:0.7,4:1.0,5:1.3}
TC,TAX,BORROW,INIT,RF = 0.001,0.001,0.10,1_000_000_000,0.001
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}
BREADTH_FILE = r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
BREADTH_TH = 0.50          # US cap allowed only if Breadth_MA200 < this (and valid)
BREADTH_MIN_UNIVERSE = 100 # breadth invalid below this many stocks (nascent market)

# ── data ──
sf = pd.read_csv("vnindex_5state_tam_quan_v3_4b_full_history.csv"); sf["time"]=pd.to_datetime(sf["time"])
sf = sf.sort_values("time").reset_index(drop=True); sf["state_dt"]=_dt_4gate(sf["state"].values.astype(int))
vx = pd.read_csv("VNINDEX.csv"); vx["time"]=pd.to_datetime(vx["time"]); vx=vx.sort_values("time").reset_index(drop=True)
vx["MA200"]=vx["Close"].rolling(200,min_periods=50).mean()
dd_=vx["Close"].diff(); upm=dd_.clip(lower=0); dnm=(-dd_).clip(lower=0)
rs=upm.ewm(alpha=1/14,adjust=False).mean()/dnm.ewm(alpha=1/14,adjust=False).mean().replace(0,np.nan)
vx["D_RSI"]=(100-100/(1+rs))/100.0
df=vx[["time","Close","MA200","D_RSI"]].merge(sf[["time","state_dt"]],on="time",how="inner").sort_values("time").reset_index(drop=True)
df["state_dt"]=df["state_dt"].astype(int)
us=pd.read_csv("us_market_history.csv",parse_dates=["time"]).sort_values("time")
key=df[["time"]].copy(); key["jt"]=key["time"]-pd.Timedelta(days=1)
um=pd.merge_asof(key.sort_values("jt"),us.rename(columns={"time":"us_time"}),left_on="jt",right_on="us_time",direction="backward").sort_values("time").reset_index(drop=True)
df=df.merge(um[["time","vix","spx_dd_1y","vix_ma252"]],on="time",how="left")
ev=pd.DataFrame(SBV_REFI_EVENTS,columns=["time","refi"]); ev["time"]=pd.to_datetime(ev["time"])
dr=pd.DataFrame({"time":pd.date_range(df["time"].min(),df["time"].max(),freq="D")}).merge(ev,on="time",how="left")
dr["refi"]=dr["refi"].ffill().bfill(); df=df.merge(dr,on="time",how="left"); df["refi"]=df["refi"].ffill().bfill()
df["refi_chg6m"]=(df["refi"]-df["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])
peak=df["refi"].rolling(P["refi_chg_win"],min_periods=20).max()
df["refi_cut"]=((peak-df["refi"])>=P["refi_cut_drop"]).shift(P["refi_lag"]).fillna(False)
df["bull"]=((df["Close"]/df["Close"].shift(P["refi_chg_win"])-1>P["bull_r6m"])&(df["Close"]>df["MA200"])).shift(1).fillna(False)
# breadth (T-aligned, ffill); B200 + universe
bd=pd.read_csv(BREADTH_FILE); bd["time"]=pd.to_datetime(bd["time"])
bd=bd[["time","Breadth_MA200","Breadth_Total_MA200"]].sort_values("time")
df=pd.merge_asof(df.sort_values("time"),bd,on="time",direction="backward").sort_values("time").reset_index(drop=True)
df["B200"]=df["Breadth_MA200"]; df["B_univ"]=df["Breadth_Total_MA200"]
# breadth confirms US weakness only if valid universe AND below threshold; shift 1 (causal, prior close)
b_valid=(df["B_univ"].fillna(0)>=BREADTH_MIN_UNIVERSE)
breadth_confirm=(b_valid & (df["B200"]<BREADTH_TH)).shift(1).fillna(False).values.astype(bool)

n=len(df); vix=df["vix"].values; sdd=df["spx_dd_1y"].values; vma=df["vix_ma252"].values
rc6=df["refi_chg6m"].values; cut=df["refi_cut"].values.astype(bool); bull=df["bull"].values.astype(bool); close=df["Close"].values

def fuse(use_breadth_gate):
    cap=np.full(n,9); easing=np.zeros(n,bool)
    for t in range(n):
        v,ddd,vm,rr=vix[t],sdd[t],vma[t],rc6[t]
        us_ok = (not bull[t]) and ((not use_breadth_gate) or breadth_confirm[t])
        if not us_ok:
            uc=ub=umild=False
        else:
            uc=(not np.isnan(ddd) and ddd<P["spx_crisis"]) or (not np.isnan(v) and v>P["vix_crisis"])
            ub=(not np.isnan(ddd) and ddd<P["spx_bear"]) and (not np.isnan(v) and v>P["vix_bear"])
            umild=(not np.isnan(ddd) and ddd<P["spx_mild"]) and (not np.isnan(v) and v>P["vix_mild"])
        de=(not np.isnan(rr) and rr>=P["dom_extreme"]); ds=(not np.isnan(rr) and rr>=P["dom_strong"]); dm=(not np.isnan(rr) and rr>=P["dom_mild"])
        if uc or de: cap[t]=CRISIS
        elif ub or ds: cap[t]=BEAR
        elif umild or dm: cap[t]=NEUTRAL
        calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(ddd) and ddd>-0.05)
        if cap[t]==9 and cut[t] and calm: easing[t]=True
    persist=np.zeros(n,int)
    for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
    lb=P["ez_price_lb"]; pup=np.zeros(n,bool); pup[lb:]=close[lb:]>close[:-lb]
    ez=easing&(persist>=P["ez_confirm"])&pup
    cap=_commit(cap,P["cap_commit"]); st=df["state_dt"].values
    sm=np.where(cap!=9,np.minimum(st,cap),st)
    sm=np.where((cap==9)&ez&(sm<NEUTRAL),NEUTRAL,sm).astype(int)
    return sm

st=df["state_dt"].values
S_DT4=st.copy(); S_DT5G=fuse(False); S_BGATE=fuse(True)

# ── pure-index NAV ──
ma200=df["MA200"].values; rsi=df["D_RSI"].values
def build_w(state):
    w=np.array([STATE_ALLOC[int(s)] for s in state],float)
    up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72)
    cf=False; ru=rd=0; upf=np.zeros(n,bool)
    for t in range(n):
        if up_raw[t]: ru+=1; rd=0
        else: rd+=1; ru=0
        if not cf and ru>=10: cf=True
        elif cf and rd>=10: cf=False
        upf[t]=cf
    w[(state==NEUTRAL)&upf]=0.90; return w
r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
yr=df["time"].dt.year.values; dep=np.array([VGB_1Y.get(int(y),0.001) for y in yr])
spy=n/((df["time"].iloc[-1]-df["time"].iloc[0]).days/365.25)
def sim(state):
    tgt=build_w(state); tl=np.concatenate([[0.0],tgt[:-1]]); nav=np.empty(n); nav[0]=INIT; dret=np.zeros(n)
    for t in range(n):
        w=tl[t]; wp=tl[t-1] if t>0 else 0.0; cf=max(0,1-w); lf=max(0,w-1); buy=max(0,w-wp); sell=max(0,wp-w)
        dret[t]=w*r[t]+cf*dep[t]/spy-lf*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+dret[t])
    return pd.DataFrame({"time":df["time"],"nav":nav,"ret":dret})
def met(o,a,b):
    o=o[(o["time"]>=a)&(o["time"]<=b)].reset_index(drop=True)
    if len(o)<30: return None
    nv=INIT*o["nav"].values/o["nav"].values[0]; tm=pd.DatetimeIndex(o["time"]); y=(tm[-1]-tm[0]).days/365.25
    cagr=(nv[-1]/nv[0])**(1/y)-1; ex=o["ret"].values-RF/spy; sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    ddv=((nv-np.maximum.accumulate(nv))/np.maximum.accumulate(nv)).min(); return dict(cagr=cagr*100,sh=sh,dd=ddv*100)
o4=sim(S_DT4); o5=sim(S_DT5G); og=sim(S_BGATE)

# ── episode ledger under each (to show 2001 vanishes under BGATE) ──
def episodes(S):
    diff=(S!=st); dirn=np.sign(S-st); eps=[]; i=0
    while i<n:
        if not diff[i]: i+=1; continue
        d0=dirn[i]; j=i
        while j+1<n and diff[j+1] and dirn[j+1]==d0: j+=1
        eps.append((df["time"].iloc[i].date(),df["time"].iloc[j].date(),"DE-RISK" if d0<0 else "RE-RISK",
                    int(j-i+1),(close[j]/close[i]-1)*100)); i=j+1
    return eps
ep5=episodes(S_DT5G); epg=episodes(S_BGATE)

L=["# DT5G + VN-Breadth Gate on US pillar — validation\n",
   f"*Rule: US cap binds only if Breadth_MA200 valid (universe>={BREADTH_MIN_UNIVERSE}) AND "
   f"< {BREADTH_TH} (shift 1, causal). SBV pillar + bull-bypass unchanged. Pure-index, 1B.*\n",
   "## A. NAV by period (DT4 vs DT5G vs DT5G+BGATE)\n",
   "| Period | DT4 | DT5G | +BGATE | Δ DT5G | Δ BGATE | BGATE Sh | BGATE DD |","|---|---|---|---|---|---|---|---|"]
for nm,a,b in [("FULL 2000-now","2000-01-01","2026-12-31"),("2003+ (drop nascent)","2003-01-01","2026-12-31"),
               ("PRE14 2003-2013","2003-01-01","2013-12-31"),("MODERN 2014-now","2014-01-01","2026-12-31")]:
    m4=met(o4,a,b); m5=met(o5,a,b); mg=met(og,a,b)
    if not m4: continue
    L.append(f"| {nm} | {m4['cagr']:+.2f}% | {m5['cagr']:+.2f}% | {mg['cagr']:+.2f}% | "
             f"{m5['cagr']-m4['cagr']:+.2f}pp | {mg['cagr']-m4['cagr']:+.2f}pp | {mg['sh']:.2f} | {mg['dd']:.1f}% |")
    print(f"{nm:<22} DT4 {m4['cagr']:+6.2f} | DT5G {m5['cagr']:+6.2f}(Δ{m5['cagr']-m4['cagr']:+.2f}) | BGATE {mg['cagr']:+6.2f}(Δ{mg['cagr']-m4['cagr']:+.2f})")
L.append("\n## B. Crisis windows (must PRESERVE under BGATE)\n| Window | DT4 | DT5G | BGATE |\n|---|---|---|---|")
for nm,a,b in [("2008 GFC","2008-06-01","2009-03-31"),("2011 inflation","2011-01-01","2011-12-31"),
               ("2020 COVID","2020-02-01","2020-08-31"),("2023 tightening","2023-01-01","2023-06-30")]:
    m4=met(o4,a,b); m5=met(o5,a,b); mg=met(og,a,b)
    L.append(f"| {nm} | {m4['cagr']:+.1f}% | {m5['cagr']:+.1f}% | {mg['cagr']:+.1f}% |")
    print(f"  [{nm}] DT4 {m4['cagr']:+.1f} DT5G {m5['cagr']:+.1f} BGATE {mg['cagr']:+.1f}")
L.append("\n## C. Episodes: DT5G vs BGATE (2001 should disappear under BGATE)\n")
L.append("DT5G episodes: "+", ".join(f"{s}({t[:1]},{d}d,{e:+.0f}%)" for s,_,t,d,e in ep5))
L.append("\nBGATE episodes: "+", ".join(f"{s}({t[:1]},{d}d,{e:+.0f}%)" for s,_,t,d,e in epg))
with open("data/dt5g_breadth_gate.md","w",encoding="utf-8") as f: f.write("\n".join(L))
print("\nDT5G episodes:", [(s,t[:1],d) for s,_,t,d,e in ep5])
print("BGATE episodes:", [(s,t[:1],d) for s,_,t,d,e in epg])
print("Report: data/dt5g_breadth_gate.md")
