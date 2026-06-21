#!/usr/bin/env python3
"""
integrated_capitulation_overlay.py
===============================================================================
Tests the user's design: core V4/V5 runs normally; during DT5G CRISIS the core
is PARKED in cash; on a STRONG capitulation signal (oversold>=40%) redeploy that
idle cash into the EW quality basket, hold 60d, return to the core's parked state.

Only touches money the core was leaving in cash (deploy events = STRONG while
DT5G==CRISIS). Splices the ACTUAL basket daily path into the core NAV so intra-
window drawdown is correct. Also tests SCALE-IN (rai lenh) vs all-in entry.
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
state_by=D.set_index("time")["state"]
def declust(d,gap=30):
    d=d.sort_values("time").copy();d["g"]=d["time"].diff().dt.days.fillna(999);d["c"]=(d["g"]>=gap).cumsum()
    return d.groupby("c").first()["time"].tolist()
strong=declust(D[D["pct_oversold"]>=0.40])
# deploy events = STRONG while core is PARKED (DT5G CRISIS)
deploy=[d for d in strong if int(state_by.get(pd.Timestamp(d),3))==1]
print(f"STRONG events: {len(strong)} | deploy-while-CRISIS (core parked): {len(deploy)}")
print("  deploy dates:", [str(pd.Timestamp(d).date()) for d in deploy])

def basket_daily(d, scalein=0):
    """EW quality(+golden fallback) basket daily-return path for H days from d.
       scalein=0 all-in; k>0 = average entry equally over first k days (rai lenh)."""
    ds=pd.Timestamp(d).date()
    q=bq(f"""WITH elig AS (SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz0 FROM tav2_bq.ticker_prune p
      WHERE p.time=DATE '{ds}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
        AND COALESCE(p.Price,p.Close)*p.Volume/1e9>=2)
      SELECT f.time,f.ticker,f.Close,e.pbz0 FROM tav2_bq.ticker_prune f JOIN elig e USING(ticker)
      WHERE f.time>=DATE '{ds}' AND f.time<=DATE_ADD(DATE '{ds}',INTERVAL 130 DAY) ORDER BY f.ticker,f.time""")
    if len(q)==0: return None
    q["time"]=pd.to_datetime(q["time"]); pbz0=q.groupby("ticker")["pbz0"].first()
    g=pbz0[pbz0<-1].index.tolist(); c=pbz0[pbz0<0].index.tolist(); a=pbz0.index.tolist()
    names=g if len(g)>=3 else (c if len(c)>=3 else a)
    px=q[q.ticker.isin(names)].pivot(index="time",columns="ticker",values="Close").sort_index().ffill().iloc[:H+1]
    cum=px.div(px.iloc[0])                      # per-ticker cumret, all-in at day0
    if scalein<=1:
        nav=cum.mean(axis=1)                    # equal-weight, all-in
    else:
        # average entry: 1/k of capital enters on each of first k trading days
        w=np.zeros(len(px))
        navs=[]
        for t in range(len(px)):
            # weight invested by day t = min(t+1,k)/k ; entered tranches track their own cumret
            inv=0.0; val=0.0
            for j in range(min(t,scalein-1)+1):
                val += (1/scalein)*(px.iloc[t]/px.iloc[j]).mean()
                inv += 1/scalein
            cash=(1-inv)
            navs.append(val+cash)              # uninvested tranche sits in cash (=1.0 base)
        nav=pd.Series(navs,index=px.index)
    return nav/nav.iloc[0]

def metrics(nav):
    nav=nav.dropna(); r=nav.pct_change().dropna()
    yrs=(nav.index[-1]-nav.index[0]).days/365.25
    cagr=nav.iloc[-1]**(1/yrs)-1
    dd=(nav/nav.cummax()-1).min()
    sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0
    return cagr*100, dd*100, sh

# ---- Part A: integrated overlay NAV (splice basket daily path into parked windows)
print("\n"+"="*70); print("PART A — Integrated overlay vs baseline core (V4 & V5)"); print("="*70)
idx=core.index
baskets={d:basket_daily(d,0) for d in deploy}
for sysname,col in [("V4","V4_V121_ENS_TQ34b"),("V5","V5_V4_KellyQ2")]:
    base=core[col]
    ret=base.pct_change().fillna(0).values.copy()
    for d in deploy:
        bk=baskets[d]
        if bk is None: continue
        i0=idx.searchsorted(pd.Timestamp(d))
        bret=bk.pct_change().fillna(0).values
        n=min(H,len(bret)-1,len(idx)-1-i0)
        ret[i0+1:i0+1+n]=bret[1:1+n]           # replace parked-cash days with basket days
        ret[i0+1]-=COST; ret[i0+n]-=COST       # entry+exit cost
    new=pd.Series(np.cumprod(1+ret),index=idx)
    cb,db,sb=metrics(base); cn,dn,sn=metrics(new)
    print(f"{sysname:>3} baseline : CAGR {cb:5.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}   final x{base.iloc[-1]:.2f}")
    print(f"{sysname:>3} +overlay : CAGR {cn:5.2f}%  MaxDD {dn:6.1f}%  Sharpe {sn:.2f}   final x{new.iloc[-1]:.2f}   (CAGR {cn-cb:+.2f}pp)")

# ---- Part B: scale-in (rai lenh) vs all-in, on the deploy events --------------
print("\n"+"="*70); print("PART B — Scale-in (rai lenh) vs all-in, 60d hold, deploy events"); print("="*70)
print(f"{'entry method':<22}{'mean60':>9}{'median60':>10}{'win%':>7}")
for label,k in [("all-in (day0)",0),("3 tranches",3),("5 tranches",5)]:
    rr=[]
    for d in deploy:
        nav=basket_daily(d,k)
        if nav is None: continue
        rr.append(nav.iloc[min(H,len(nav)-1)]-1-COST)
    rr=np.array(rr)*100
    print(f"{label:<22}{rr.mean():>9.1f}{np.median(rr):>10.1f}{100*(rr>0).mean():>7.0f}")
print("\n(deploy events only = STRONG-while-CRISIS; scale-in averages capital over first k trading days)")
