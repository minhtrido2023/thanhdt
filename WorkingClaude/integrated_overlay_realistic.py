#!/usr/bin/env python3
"""
integrated_overlay_realistic.py  — (e) honest overlay using ACTUAL idle-cash frac
===============================================================================
The +4.6pp overlay (integrated_capitulation_overlay.py) assumed 100% of NAV is
redeployed during DT5G CRISIS. Reality: the core is only PARTLY parked. The
core's realized equity exposure over a window = its daily BETA to the market;
so idle-cash fraction f = clip(1 - beta, 0, 1). Only that f is redeployed:
   overlay_daily_ret = f*basket_ret + (1-f)*core_ret
Reports baseline vs realistic-f vs sensitivity grid (f=0.5/0.7/1.0).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; SDK_BIN=r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
COST=0.003; H=60
def bq(sql):
    env=dict(os.environ); env["PATH"]=env.get("PATH","")+os.pathsep+SDK_BIN
    env.setdefault("CLOUDSDK_PYTHON",SDK_BIN+r"\..\platform\bundledpython\python.exe")
    o=subprocess.run([SDK_BIN+r"\bq.cmd","query","--use_legacy_sql=false",f"--project_id={PROJECT}",
        "--format=csv","--max_rows=200000"," ".join(sql.split())],capture_output=True,text=True,env=env)
    if o.returncode!=0: raise RuntimeError(o.stdout+o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))

core=pd.read_csv(os.path.join(WORKDIR,"data","5sys_prodspec_201401_202605_dt5g.csv"),parse_dates=["time"]).set_index("time")
D=pd.read_csv(os.path.join(WORKDIR,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
D["ew"]=(1+D["avg_ret"]).cumprod()
ew=D.set_index("time")["ew"]; ew_ret=ew.pct_change()
state_by=D.set_index("time")["state"]
def declust(d,gap=30):
    d=d.sort_values("time").copy();d["g"]=d["time"].diff().dt.days.fillna(999);d["c"]=(d["g"]>=gap).cumsum()
    return d.groupby("c").first()["time"].tolist()
deploy=[d for d in declust(D[D["pct_oversold"]>=0.40]) if int(state_by.get(pd.Timestamp(d),3))==1]

# basket daily NAV (cache to CSV)
cache=os.path.join(WORKDIR,"data","_overlay_baskets.csv")
if os.path.exists(cache):
    B=pd.read_csv(cache,parse_dates=["time"])
else:
    frames=[]
    for d in deploy:
        ds=pd.Timestamp(d).date()
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
        frames.append(pd.DataFrame({"event":str(ds),"time":nav.index,"nav":nav.values}))
    B=pd.concat(frames); B.to_csv(cache,index=False)

idx=core.index
def build_overlay(col, fmode):
    base=core[col]; ret=base.pct_change().fillna(0).values.copy(); cret=ret.copy()
    notes=[]
    for d in deploy:
        ds=str(pd.Timestamp(d).date()); bk=B[B["event"]==ds].set_index("time")["nav"]
        if len(bk)<5: continue
        i0=idx.searchsorted(pd.Timestamp(d)); bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        win=slice(i0+1,i0+1+n)
        # core's equity exposure over the window = beta to EW market
        cwin=pd.Series(cret[win]); mwin=ew_ret.reindex(idx[win]).fillna(0).values
        var=np.var(mwin)
        beta=float(np.cov(cwin,mwin)[0,1]/var) if var>0 else 1.0
        if   fmode=="real": f=min(max(1-beta,0),1)
        else: f=float(fmode)
        ret[win]=f*bret[1:1+n]+(1-f)*cret[win]
        ret[i0+1]-=COST*f; ret[i0+n]-=COST*f
        notes.append((ds,round(beta,2),round(f,2)))
    return pd.Series(np.cumprod(1+ret),index=idx), notes

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    return (nav.iloc[-1]**(1/yrs)-1)*100, (nav/nav.cummax()-1).min()*100, r.mean()/r.std()*np.sqrt(252)

print("deploy windows (DT5G CRISIS + washout>=40%):")
_,nt=build_overlay("V4_V121_ENS_TQ34b","real")
print("  date        beta(core->mkt)  idle-cash f=1-beta")
for ds,b,f in nt: print(f"  {ds}      {b:>5.2f}            {f:>4.2f}")
print()
for sysname,col in [("V4","V4_V121_ENS_TQ34b"),("V5","V5_V4_KellyQ2")]:
    cb,db,sb=metrics(core[col])
    print(f"{sysname} baseline      : CAGR {cb:5.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}")
    for tag,fm in [("realistic f=1-beta","real"),("f=0.5","0.5"),("f=0.7","0.7"),("f=1.0 (idealized)","1.0")]:
        nav,_=build_overlay(col,fm); cn,dn,sn=metrics(nav)
        print(f"{sysname} +overlay {tag:<18}: CAGR {cn:5.2f}%  MaxDD {dn:6.1f}%  Sharpe {sn:.2f}   ({cn-cb:+.2f}pp)")
    print()
