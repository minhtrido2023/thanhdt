#!/usr/bin/env python3
"""
extended_overlay_grind.py
===============================================================================
Extends the capitulation overlay beyond CRISIS: deploy the STATE-PRESCRIBED cash
reserve (f = 1 - state_weight) into the washout basket on every washout, hold 60d,
reset. State weights: CRISIS 0% -> f=1.0, BEAR 20% -> f=0.8, NEUTRAL 70% -> f=0.3,
BULL/EX-BULL -> f=0 (no reserve, skip).

Overlay return model (idle reserve was earning ~0):  new_ret = core_ret + f*basket_ret
(slight upper bound if the core re-risks its own reserve within the 60d window).

GRIND filter: a washout that REPEATS within 90 trading days of a prior one = grinding
bear (2022 trap, market keeps making lower lows). Variants:
  ALL-FULL    : deploy full f on every washout
  GRIND-HALF  : full f on SHARP, f/2 on GRIND (cautious scale-in)
  GRIND-SKIP  : full f on SHARP, 0 on GRIND
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; SDK_BIN=r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
COST=0.003; H=60
F_STATE={1:1.0, 2:0.8, 3:0.3, 4:0.0, 5:0.0}   # reserve = 1 - state target weight
def bq(sql):
    env=dict(os.environ); env["PATH"]=env.get("PATH","")+os.pathsep+SDK_BIN
    env.setdefault("CLOUDSDK_PYTHON",SDK_BIN+r"\..\platform\bundledpython\python.exe")
    o=subprocess.run([SDK_BIN+r"\bq.cmd","query","--use_legacy_sql=false",f"--project_id={PROJECT}",
        "--format=csv","--max_rows=200000"," ".join(sql.split())],capture_output=True,text=True,env=env)
    if o.returncode!=0: raise RuntimeError(o.stdout+o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))

core=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g.csv"),parse_dates=["time"]).set_index("time")
D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state_by=D.set_index("time")["state"]
ws=D[D["pct_oversold"]>=0.40].copy().sort_values("time")
ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
ev=[]
for _,grp in ws.groupby("c"):
    d0=grp.iloc[0]["time"]; st=int(state_by.get(d0,3)); ev.append((d0,st))
# grind flag: another washout within 90 trading days BEFORE this one
ev=sorted(ev); evdates=[e[0] for e in ev]
def tdgap(a,b):
    ia=D.index[D["time"]==a][0]; ib=D.index[D["time"]==b][0]; return ia-ib
events=[]
for i,(d0,st) in enumerate(ev):
    grind = i>0 and tdgap(d0,ev[i-1][0])<=90
    events.append(dict(date=d0,state=st,f=F_STATE.get(st,0),grind=grind))
E=pd.DataFrame(events)
print("washout events + state reserve + grind flag:")
print(E.assign(date=E.date.dt.date).to_string(index=False))

# basket daily NAV cache (all deploy events f>0)
cache=os.path.join(W,"data","_washout_baskets.csv")
deploy=[e for e in events if e["f"]>0]
if os.path.exists(cache):
    B=pd.read_csv(cache,parse_dates=["time"])
else:
    frames=[]
    for e in deploy:
        ds=str(e["date"].date())
        q=bq(f"""WITH elig AS (SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz0 FROM tav2_bq.ticker_prune p
          WHERE p.time=DATE '{ds}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
            AND COALESCE(p.Price,p.Close)*p.Volume/1e9>=2)
          SELECT f.time,f.ticker,f.Close,e.pbz0 FROM tav2_bq.ticker_prune f JOIN elig e USING(ticker)
          WHERE f.time>=DATE '{ds}' AND f.time<=DATE_ADD(DATE '{ds}',INTERVAL 130 DAY) ORDER BY f.ticker,f.time""")
        q["time"]=pd.to_datetime(q["time"]); pbz0=q.groupby("ticker")["pbz0"].first()
        g=pbz0[pbz0<-1].index.tolist(); c=pbz0[pbz0<0].index.tolist(); a=pbz0.index.tolist()
        names=g if len(g)>=3 else (c if len(c)>=3 else a)
        px=q[q.ticker.isin(names)].pivot(index="time",columns="ticker",values="Close").sort_index().ffill().iloc[:H+1]
        nav=px.div(px.iloc[0]).mean(axis=1); nav=nav/nav.iloc[0]
        frames.append(pd.DataFrame({"event":ds,"time":nav.index,"nav":nav.values}))
    B=pd.concat(frames); B.to_csv(cache,index=False)

idx=core.index
def overlay(col,mode):
    base=core[col]; ret=base.pct_change().fillna(0).values.copy()
    for e in deploy:
        f=e["f"]
        if mode=="half" and e["grind"]: f*=0.5
        if mode=="skip" and e["grind"]: f=0.0
        if f<=0: continue
        ds=str(e["date"].date()); bk=B[B["event"]==ds].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(e["date"]); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        ret[i0+1:i0+1+n]+=f*bret[1:1+n]     # add basket return on the idle reserve f
        ret[i0+1]-=COST*f; ret[i0+n]-=COST*f
    return pd.Series(np.cumprod(1+ret),index=idx)
def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

print("\n"+"="*78)
print("Extended overlay (deploy state reserve on EVERY washout, hold 60d)")
print("="*78)
for sysname,col in [("V4","V4_V121_ENS_TQ34b"),("V5","V5_V4_KellyQ2")]:
    cb,db,sb=metrics(core[col])
    print(f"{sysname} baseline           : CAGR {cb:5.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}")
    for tag,mode in [("ALL-FULL (no grind filt)","all"),("GRIND-HALF","half"),("GRIND-SKIP","skip")]:
        nav=overlay(col,mode); cn,dn,sn=metrics(nav)
        print(f"{sysname} +overlay {tag:<24}: CAGR {cn:5.2f}%  MaxDD {dn:6.1f}%  Sharpe {sn:.2f}   ({cn-cb:+.2f}pp)")
    print()
