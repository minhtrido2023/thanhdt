#!/usr/bin/env python3
"""re_unearned_ic.py — IC test of deferred-revenue (UnearnRev) factors for IP/RE asset-plays (ICB 8633).
User priority: STEADY, gradually-rising leasing pace > absolute backlog level.
Factors tested: backlog_yield(level/MktCap), g1y(YoY), slope(trend over 8q), consistency(monotonic-up),
steady(slope×consistency), vs forward 6M/12M returns. 45-day report lag (no look-ahead). vs PB control."""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
def spearman(a,b):
    a=pd.Series(np.asarray(a,float)); b=pd.Series(np.asarray(b,float)); ra,rb=a.rank(),b.rank()
    return ra.corr(rb) if (ra.std()>0 and rb.std()>0) else np.nan
W=r"/home/trido/thanhdt/WorkingClaude"
fin=pd.read_csv(os.path.join(W,"data","re_fin_panel.csv")); px=pd.read_csv(os.path.join(W,"data","re_price_panel.csv"))
fin["rt"]=pd.to_datetime(fin["rt"]); px["time"]=pd.to_datetime(px["time"])
px=px.sort_values("time")
UN=[f"UnearnRev_P{i}" for i in range(8)]

def price_asof(tk, dt):
    s=px[(px.ticker==tk)&(px.time>=dt)]
    return (s.iloc[0]["Close"], s.iloc[0]["liqB"]) if len(s) else (np.nan,np.nan)

rows=[]
for _,r in fin.iterrows():
    tk=r["ticker"]; d0=r["rt"]+pd.Timedelta(days=45)              # report lag → point-in-time
    p0,liq=price_asof(tk,d0);
    if not np.isfinite(p0) or r["OShares"]<=0: continue
    p6,_=price_asof(tk,d0+pd.Timedelta(days=182)); p12,_=price_asof(tk,d0+pd.Timedelta(days=365))
    mc=p0*r["OShares"]
    un=np.array([r[c] for c in UN],float)                         # [P0..P7] newest..oldest
    chrono=un[::-1]                                               # oldest..newest
    lvl=r["UnearnRev_P0"]/mc if mc>0 else np.nan
    eq=r["Equity"]; un_eq=(r["UnearnRev_P0"]/eq) if (pd.notna(eq) and eq>0) else np.nan
    g1=(un[0]/un[4]-1) if (pd.notna(un[4]) and un[4]>0) else np.nan
    # slope (normalized) + consistency over 8q chrono
    valid=np.isfinite(chrono)
    if valid.sum()>=6 and np.nanmean(chrono)>0:
        x=np.arange(len(chrono))[valid]; y=chrono[valid]
        slope=np.polyfit(x,y,1)[0]/np.nanmean(chrono)             # normalized slope (per-quarter, % of mean)
        diffs=np.diff(y); consistency=(diffs>0).mean()            # fraction of QoQ steps that rose
        steady=slope*consistency
    else: slope=consistency=steady=np.nan
    rows.append(dict(ticker=tk,rt=r["rt"],PB=r["PB"],mc=mc,un_lvl=lvl,un_eq=un_eq,g1=g1,
        slope=slope,consistency=consistency,steady=steady,
        f6=(p6/p0-1) if np.isfinite(p6) else np.nan, f12=(p12/p0-1) if np.isfinite(p12) else np.nan))
d=pd.DataFrame(rows); d["q"]=d["rt"].dt.to_period("Q")
print(f"panel {len(d)} obs, {d.ticker.nunique()} RE tickers, {d.rt.dt.year.min()}-{d.rt.dt.year.max()}")
lease=d[d["un_eq"]>=0.05]   # IP/lease subset (meaningful deferred rev)
print(f"lease-model subset (UnearnRev/Equity>=5%): {len(lease)} obs, {lease.ticker.nunique()} tickers\n")

def xs_ic(df,m,f):
    ics=[g[[m,f]].dropna().pipe(lambda z: spearman(z[m],z[f])) for _,g in df.groupby("q") if len(g[[m,f]].dropna())>=6]
    ics=np.array([i for i in ics if pd.notna(i)])
    return (ics.mean(), ics.mean()/ics.std()*np.sqrt(len(ics)) if ics.std()>0 else np.nan, len(ics)) if len(ics)>=5 else (np.nan,np.nan,len(ics))

for label,df in [("ALL ICB-8633",d),("LEASE subset",lease)]:
    print(f"=== {label}: cross-sectional IC (mean Spearman by quarter) ===")
    print(f"{'factor':<13}{'IC 6M':>20}{'IC 12M':>20}")
    for m in ["un_lvl","un_eq","g1","slope","consistency","steady","PB"]:
        i6,t6,n6=xs_ic(df,m,"f6"); i12,t12,n12=xs_ic(df,m,"f12")
        print(f"{m:<13}{f'{i6:+.3f}(t{t6:+.1f},n{n6})':>20}{f'{i12:+.3f}(t{t12:+.1f},n{n12})':>20}")
    print()
# incremental: slope/steady after removing backlog level + PB (lease subset, 12M)
print("=== Incremental IC (lease subset, 12M): factor after removing un_lvl & PB ===")
for m in ["slope","consistency","steady","g1"]:
    ics=[]
    for _,g in lease.groupby("q"):
        z=g[[m,"un_lvl","PB","f12"]].dropna()
        if len(z)<8: continue
        R=z.rank(); X=np.column_stack([np.ones(len(R)),R["un_lvl"],R["PB"]])
        try: b,_,_,_=np.linalg.lstsq(X,R[m].values,rcond=None); res=R[m].values-X@b
        except Exception: continue
        ic=spearman(res,z["f12"]);
        if pd.notna(ic): ics.append(ic)
    ics=np.array(ics)
    if len(ics)>=5: print(f"  {m:<12} resid IC 12M: {ics.mean():+.3f} (t={ics.mean()/ics.std()*np.sqrt(len(ics)):+.1f}, n={len(ics)})")
