"""Cau hoi 1, lam lai tren PANEL PIN (data/value_panel_2014.csv) — panel doc lap voi panel toi tu dung.
Dong thoi doi chieu voi ket qua da pin 'THREAD (c)': ey IC theo state DOWN +0.148 / NEUTRAL +0.107 / BULL +0.156."""
import numpy as np, pandas as pd
from scipy import stats
W="/home/trido/thanhdt/WorkingClaude"
px=pd.read_csv("px_factor.csv",parse_dates=["time"])
d=pd.read_csv(f"{W}/data/value_panel_2014.csv",parse_dates=["time"],
              usecols=["ticker","time","PE","profit_2M","turnover"])
d=d.merge(px[["ticker","time","Price","Close"]],on=["ticker","time"],how="left")
d["F"]=np.where(d.Close>0,d.Price/d.Close,np.nan)
d["ey_uncorr"]=np.where(d.PE>0,1/d.PE,np.nan)
d["ey_corr"]=np.where((d.PE>0)&d.F.notna(),1/(d.PE*d.F),np.nan)
fa=pd.read_csv("fa8l.csv",parse_dates=["time"]).sort_values("time")
o=[]
for tk,g in d.groupby("ticker",sort=False):
    f=fa[fa.ticker==tk]
    if f.empty: continue
    o.append(pd.merge_asof(g.sort_values("time"),f[["time","rating"]],on="time",direction="backward"))
d=pd.concat(o,ignore_index=True)
st=pd.read_csv("dt5g.csv",parse_dates=["time"])
d=d.merge(st,on="time",how="left")
d["q"]=d.time.dt.to_period("Q"); d=d.sort_values("time").groupby(["ticker","q"]).tail(1)
NAME={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}

def per_q(sub,col):
    r=[]
    for q,g in sub.groupby("q"):
        gg=g[[col,"profit_2M"]].dropna()
        if len(gg)<30: continue
        r.append(dict(q=q,state=int(g.state.iloc[0]),ic=stats.spearmanr(gg[col],gg.profit_2M).statistic))
    return pd.DataFrame(r)

def show(sub,col,tag):
    f=per_q(sub,col)
    if f.empty: print(f"\n{tag}: rong"); return
    f["grp"]=np.where(f.state.isin([1,2]),"CRISIS+BEAR",np.where(f.state==3,"NEUTRAL","BULL+EXBULL"))
    f=f.sort_values("q"); f["blk"]=(f.grp!=f.grp.shift()).cumsum()
    print(f"\n{tag}")
    print(f"  {'nhom':<13}{'N quy':>6}{'IC':>9}{'t(quy)':>8}{'N episode':>11}{'IC_ep':>9}{'t(ep)':>8}{'CI90(ep)':>20}")
    for g in ["TAT CA","CRISIS+BEAR","NEUTRAL","BULL+EXBULL"]:
        s=f if g=="TAT CA" else f[f.grp==g]
        if len(s)<2: print(f"  {g:<13}{len(s):>6}  qua mong"); continue
        x=s.ic.values; se=x.std(ddof=1)/np.sqrt(len(x))
        bm=s.groupby("blk").ic.mean().values
        if len(bm)>=2:
            seb=bm.std(ddof=1)/np.sqrt(len(bm)); tb=bm.mean()/seb; qq=stats.t.ppf(.95,len(bm)-1)
            ci=f"[{bm.mean()-qq*seb:+.3f};{bm.mean()+qq*seb:+.3f}]"
        else: tb=np.nan; ci="-"; bm=np.array([np.nan])
        print(f"  {g:<13}{len(x):>6}{x.mean():>+9.3f}{x.mean()/se:>+8.2f}{len(bm):>11}{np.nanmean(bm):>+9.3f}{tb:>+8.2f}{ci:>20}")
    for a,b in [("CRISIS+BEAR","NEUTRAL"),("BULL+EXBULL","NEUTRAL"),("CRISIS+BEAR","BULL+EXBULL")]:
        xa=f[f.grp==a].groupby("blk").ic.mean(); xb=f[f.grp==b].groupby("blk").ic.mean()
        if len(xa)>=2 and len(xb)>=2:
            t,p=stats.ttest_ind(xa,xb,equal_var=False)
            print(f"     [episode] {a} - {b}: d={xa.mean()-xb.mean():+.3f} t={t:+.2f} p={p:.3f}")
show(d,"ey_uncorr","(1) TOAN UNIVERSE, ey KHONG sua gia  [tai lap THREAD (c) da pin]")
show(d,"ey_corr",  "(2) TOAN UNIVERSE, ey DA sua gia")
show(d[(d.rating<=3)&(d.turnover>=3e9)],"ey_corr","(3) TRONG CONG production (rating<=3 & liq>=3ty), ey DA sua gia")
