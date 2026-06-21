#!/usr/bin/env python3
"""
realistic_extended_overlay.py — final beta-adjusted extended overlay
===============================================================================
Replaces the THEORETICAL state reserve (f=1-state_weight) with the REALISTIC idle
cash measured from the core's actual equity exposure: f = clip(1 - beta(core->mkt))
over each 60d window (beta = realized exposure read from NAV co-movement). Correct
addition model: new_ret = core_ret + f*basket_ret (idle f earned ~0 in baseline,
invested 1-f keeps earning core's return -> no double-count).

Variants: CRISIS-ONLY (beta) · EXTENDED-ALL (beta, every washout) ·
EXTENDED-GRIND-HALF (beta, half deploy on repeat-washout events).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; SDK_BIN=r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
COST=0.003; H=60
def bq(sql):
    env=dict(os.environ); env["PATH"]=env.get("PATH","")+os.pathsep+SDK_BIN
    env.setdefault("CLOUDSDK_PYTHON",SDK_BIN+r"\..\platform\bundledpython\python.exe")
    o=subprocess.run([SDK_BIN+r"\bq.cmd","query","--use_legacy_sql=false",f"--project_id={PROJECT}",
        "--format=csv","--max_rows=200000"," ".join(sql.split())],capture_output=True,text=True,env=env)
    if o.returncode!=0: raise RuntimeError(o.stdout+o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))

core=pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g.csv"),parse_dates=["time"]).set_index("time")
D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
D["ew"]=(1+D["avg_ret"]).cumprod(); ew_ret=D.set_index("time")["ew"].pct_change()
state_by=D.set_index("time")["state"]
ws=D[D["pct_oversold"]>=0.40].copy().sort_values("time"); ws["g"]=ws["time"].diff().dt.days.fillna(999); ws["c"]=(ws["g"]>=30).cumsum()
ev=sorted([(g.iloc[0]["time"], int(state_by.get(g.iloc[0]["time"],3))) for _,g in ws.groupby("c")])
def tdpos(t): return D.index[D["time"]==t][0]
events=[]
for i,(d0,st) in enumerate(ev):
    grind = i>0 and (tdpos(d0)-tdpos(ev[i-1][0]))<=90
    events.append(dict(date=d0,state=st,grind=grind))

# basket cache for ALL washout events (extend the f>0 cache with any missing)
cache=os.path.join(W,"data","_washout_baskets.csv")
B=pd.read_csv(cache,parse_dates=["time"]) if os.path.exists(cache) else pd.DataFrame(columns=["event","time","nav"])
have=set(B["event"].unique())
miss=[e for e in events if str(e["date"].date()) not in have]
if miss:
    frames=[B]
    for e in miss:
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
def beta_f(col,e):
    bk=B[B["event"]==str(e["date"].date())].set_index("time")["nav"]
    i0=idx.searchsorted(e["date"]); n=min(H,len(bk)-1,len(idx)-1-i0)
    if n<5: return None,None,None
    cret=core[col].pct_change().fillna(0).values
    win=slice(i0+1,i0+1+n); mkt=ew_ret.reindex(idx[win]).fillna(0).values; cc=cret[win]
    var=np.var(mkt); beta=float(np.cov(cc,mkt)[0,1]/var) if var>0 else 1.0
    f=min(max(1-beta,0),1)
    return beta,f,(i0,n,bk)
def overlay(col,scope):  # scope: 'crisis','all','grindhalf'
    ret=core[col].pct_change().fillna(0).values.copy()
    for e in events:
        if scope=="crisis" and e["state"]!=1: continue
        beta,f,info=beta_f(col,e)
        if info is None: continue
        if scope=="grindhalf" and e["grind"]: f*=0.5
        i0,n,bk=info; bret=bk.pct_change().fillna(0).values
        ret[i0+1:i0+1+n]+=f*bret[1:1+n]; ret[i0+1]-=COST*f; ret[i0+n]-=COST*f
    return pd.Series(np.cumprod(1+ret),index=idx)
def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100,(nav/nav.cummax()-1).min()*100,r.mean()/r.std()*np.sqrt(252)

# per-event realistic f (V4)
print("per-event realistic idle-cash f = 1 - beta(core->mkt), 60d window (V4):")
print(f"  {'date':<12}{'state':>6}{'grind':>7}{'beta':>7}{'f_real':>8}")
for e in events:
    beta,f,info=beta_f("V4_V121_ENS_TQ34b",e)
    if info is None: print(f"  {str(e['date'].date()):<12}{e['state']:>6}{str(e['grind']):>7}   (censored)"); continue
    print(f"  {str(e['date'].date()):<12}{e['state']:>6}{str(e['grind']):>7}{beta:>7.2f}{f:>8.2f}")

print("\n"+"="*82)
print("REALISTIC beta-adjusted overlay (final +pp)")
print("="*82)
for sysname,col in [("V4","V4_V121_ENS_TQ34b"),("V5","V5_V4_KellyQ2")]:
    cb,db,sb=metrics(core[col])
    print(f"{sysname} baseline                  : CAGR {cb:5.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}")
    for tag,sc in [("CRISIS-only (beta)","crisis"),("EXTENDED-ALL (beta)","all"),("EXTENDED-GRIND-HALF (beta)","grindhalf")]:
        nav=overlay(col,sc); cn,dn,sn=metrics(nav)
        print(f"{sysname} +overlay {tag:<26}: CAGR {cn:5.2f}%  MaxDD {dn:6.1f}%  Sharpe {sn:.2f}   ({cn-cb:+.2f}pp)")
    print()
