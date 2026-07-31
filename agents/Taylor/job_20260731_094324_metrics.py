import glob, sys, numpy as np, pandas as pd
D="/home/trido/thanhdt/WorkingClaude/data/"
LEGS=[("ctrl cash (spec pinned)","*wtnamecap_exp_capsz_ctrl_univpit.csv"),
      ("idle (cash+park full)","*szbidle_*capsz_idle_univpit.csv"),
      ("booknav (LIVE formula)","*szbbooknav_*capsz_booknav_univpit.csv"),
      ("nav:0.10","*szbnav010_*capsz_nav10_univpit.csv"),
      ("nav:0.20","*szbnav020_*capsz_nav20_univpit.csv"),
      ("idlecap:0.30","*szbidlecap030_*capsz_idlecap30_univpit.csv")]
LEGS += [(n,p) for n,p in [(a,b) for a,b in zip([],[])]]
extra = sys.argv[1:]
for e in extra:
    LEGS.append((e.split("=")[0], e.split("=",1)[1]))
def nav_of(p):
    df=pd.read_csv(p,low_memory=False)
    d=df[df["combined_nav"].notna()&df["ymd"].notna()].copy()
    d["ymd"]=pd.to_datetime(d["ymd"],errors="coerce"); d=d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)
def m(s):
    s=s.dropna()
    if len(s)<20: return dict(cagr=np.nan,sharpe=np.nan,dd=np.nan,calmar=np.nan)
    yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100
    r=np.diff(np.log(s.values)); spy=len(r)/yrs
    sh=r.mean()/r.std(ddof=1)*np.sqrt(spy) if r.std(ddof=1)>0 else np.nan
    dd=((s/s.cummax())-1).min()*100
    return dict(cagr=cagr,sharpe=sh,dd=dd,calmar=cagr/abs(dd) if dd<0 else np.nan)
rows=[]
for name,pat in LEGS:
    f=sorted(glob.glob(D+pat))
    if not f: print(f"[THIEU] {name} ({pat})"); continue
    s=nav_of(f[-1]); full=m(s); iss=m(s[s.index<="2019-12-31"]); oos=m(s[s.index>="2020-01-01"])
    rows.append((name,full,iss,oos,len(s),f[-1].split("/")[-1]))
print(f"{'leg':<26}| {'CAGR':>6} {'Shrp':>5} {'MaxDD':>7} {'Calm':>5} | {'IS_CAGR':>7} {'IS_Cal':>6} | {'OOS_CAGR':>8} {'OOS_Cal':>7}")
print("-"*104)
for n,f,i,o,ns,fn in rows:
    print(f"{n:<26}| {f['cagr']:>6.2f} {f['sharpe']:>5.2f} {f['dd']:>7.2f} {f['calmar']:>5.2f} | "
          f"{i['cagr']:>7.2f} {i['calmar']:>6.2f} | {o['cagr']:>8.2f} {o['calmar']:>7.2f}   n={ns}")
