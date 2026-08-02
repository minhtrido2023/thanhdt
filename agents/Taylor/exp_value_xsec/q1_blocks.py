import numpy as np, pandas as pd
from scipy import stats
dp=pd.read_csv("dispersion.csv",parse_dates=["d"]); dp["terc"]=pd.qcut(dp.iqr,3,labels=["HEP","GIUA","RONG"])
def bstat(x, label):
    x=np.asarray(x,float); n=len(x)
    if n<2: return f"{label:<14}N={n:>3} IC={x.mean() if n else np.nan:+.3f}  (qua mong)"
    se=x.std(ddof=1)/np.sqrt(n); t=x.mean()/se if se>0 else np.nan
    q=stats.t.ppf(.95,n-1)
    return (f"{label:<14}N_block={n:>3}  IC={x.mean():+.4f}  t={t:+.2f}  "
            f"p={2*(1-stats.t.cdf(abs(t),n-1)):.3f}  CI90=[{x.mean()-q*se:+.3f};{x.mean()+q*se:+.3f}]")
for v in ["ey_pct","vs_proxy"]:
    for y in ["fwd20","fwd60"]:
        fm=pd.read_csv(f"fm_{v}_{y}.csv",parse_dates=["d"])
        fm["grp"]=np.where(fm.state.isin([1,2]),"CRISIS+BEAR",np.where(fm.state==3,"NEUTRAL","BULL+EXBULL"))
        fm["blk"]=(fm.grp!=fm.grp.shift()).cumsum()
        bm=fm.groupby(["blk","grp"]).agg(ic=("ic","mean"),nm=("ic","size")).reset_index()
        print(f"\n=== CAU HOI 1 muc EPISODE — {v}/{y} ===")
        print(bstat(fm.ic,"TAT CA(thang)"))
        for g in ["CRISIS+BEAR","NEUTRAL","BULL+EXBULL"]:
            sub=bm[bm.grp==g]
            print("  "+bstat(sub.ic,g)+f"   [{int(sub.nm.sum())} thang]")
        for a,b in [("CRISIS+BEAR","NEUTRAL"),("BULL+EXBULL","NEUTRAL"),("CRISIS+BEAR","BULL+EXBULL")]:
            xa=bm[bm.grp==a].ic; xb=bm[bm.grp==b].ic
            t,p=stats.ttest_ind(xa,xb,equal_var=False)
            print(f"     {a} - {b}: d={xa.mean()-xb.mean():+.3f} t={t:+.2f} p={p:.3f}")
# ERA confound cho cau hoi 2
print("\n=== CAU HOI 2 — kiem tra nham lan voi HIEU UNG THOI KY ===")
for v in ["ey_pct","vs_proxy"]:
    for y in ["fwd20","fwd60"]:
        fm=pd.read_csv(f"fm_{v}_{y}.csv",parse_dates=["d"]).merge(dp[["d","terc","iqr"]],on="d")
        e1=fm[fm.d<"2020-01-01"]; e2=fm[fm.d>="2020-01-01"]
        print(f"\n{v}/{y}: IC 2014-2019 = {e1.ic.mean():+.4f} (N={len(e1)} thang, "
              f"RONG {int((e1.terc=='RONG').sum())})  |  2020-2026 = {e2.ic.mean():+.4f} "
              f"(N={len(e2)}, RONG {int((e2.terc=='RONG').sum())})")
        for nm,e in (("2014-19",e1),("2020-26",e2)):
            xr=e[e.terc=="RONG"].ic; xh=e[e.terc=="HEP"].ic
            if len(xr)>2 and len(xh)>2:
                t,p=stats.ttest_ind(xr,xh,equal_var=False)
                print(f"    trong {nm}: RONG({len(xr)}t)={xr.mean():+.3f} HEP({len(xh)}t)={xh.mean():+.3f} d={xr.mean()-xh.mean():+.3f} t={t:+.2f} p={p:.3f}")
            else:
                print(f"    trong {nm}: khong du thang o 1 trong 2 tercile (RONG={len(xr)}, HEP={len(xh)}) -> KHONG kiem dinh duoc")
