"""Cau hoi 2 lam lai tren PANEL PIN — do phan tan dinh gia (IQR cua 1/PE da sua gia) trong cong production."""
import numpy as np, pandas as pd
from scipy import stats
W="/home/trido/thanhdt/WorkingClaude"
px=pd.read_csv("px_factor.csv",parse_dates=["time"])
d=pd.read_csv(f"{W}/data/value_panel_2014.csv",parse_dates=["time"],usecols=["ticker","time","PE","profit_2M","turnover"])
d=d.merge(px[["ticker","time","Price","Close"]],on=["ticker","time"],how="left")
d["F"]=np.where(d.Close>0,d.Price/d.Close,np.nan)
d["ey"]=np.where((d.PE>0)&d.F.notna(),1/(d.PE*d.F),np.nan)
fa=pd.read_csv("fa8l.csv",parse_dates=["time"]).sort_values("time")
o=[]
for tk,g in d.groupby("ticker",sort=False):
    f=fa[fa.ticker==tk]
    if f.empty: continue
    o.append(pd.merge_asof(g.sort_values("time"),f[["time","rating"]],on="time",direction="backward"))
d=pd.concat(o,ignore_index=True)
d=d[(d.rating<=3)&(d.turnover>=3e9)]
d["q"]=d.time.dt.to_period("Q"); d=d.sort_values("time").groupby(["ticker","q"]).tail(1)
print("so ma/quy trong cong:", d.groupby("q").ticker.size().describe()[["min","25%","50%","75%","max"]].round(0).to_dict())
rows=[]
for q,g in d.groupby("q"):
    gg=g[["ey","profit_2M"]].dropna()
    if len(gg)<30: continue
    q1,q3=gg.ey.quantile([.25,.75])
    rows.append(dict(q=q,iqr=q3-q1,ic=stats.spearmanr(gg.ey,gg.profit_2M).statistic,n=len(gg)))
f=pd.DataFrame(rows).sort_values("q")
f["terc"]=pd.qcut(f.iqr,3,labels=["HEP","GIUA","RONG"])
f["blk"]=(f.terc!=f.terc.shift()).cumsum()
print(f"\n{'tercile':<8}{'N quy':>7}{'IC':>9}{'t(quy)':>8}{'N ep':>6}{'IC_ep':>8}{'CI90(ep)':>20}")
for tc in ["HEP","GIUA","RONG"]:
    s=f[f.terc==tc]; x=s.ic.values; se=x.std(ddof=1)/np.sqrt(len(x))
    bm=s.groupby("blk").ic.mean().values
    seb=bm.std(ddof=1)/np.sqrt(len(bm)) if len(bm)>1 else np.nan
    qq=stats.t.ppf(.95,max(len(bm)-1,1))
    print(f"{tc:<8}{len(x):>7}{x.mean():>+9.3f}{x.mean()/se:>+8.2f}{len(bm):>6}{bm.mean():>+8.3f}"
          f"{f'[{bm.mean()-qq*seb:+.3f};{bm.mean()+qq*seb:+.3f}]':>20}")
xr=f[f.terc=='RONG']; xh=f[f.terc=='HEP']
t,p=stats.ttest_ind(xr.ic,xh.ic,equal_var=False); print(f"  RONG-HEP muc QUY:     d={xr.ic.mean()-xh.ic.mean():+.3f} t={t:+.2f} p={p:.3f}")
br=xr.groupby("blk").ic.mean(); bh=xh.groupby("blk").ic.mean()
t,p=stats.ttest_ind(br,bh,equal_var=False); print(f"  RONG-HEP muc EPISODE: d={br.mean()-bh.mean():+.3f} t={t:+.2f} p={p:.3f} (N={len(br)} vs {len(bh)})")
print("\nphan bo tercile theo nam:"); print(pd.crosstab(f.q.astype(str).str[:4],f.terc).to_string())
