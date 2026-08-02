import numpy as np, pandas as pd, os
from scipy import stats
p = pd.read_csv("panel.csv.gz", parse_dates=["d"])
print("fwd20 mean %.3f%% median %.3f%%  fwd60 mean %.3f%%" % (100*p.fwd20.mean(),100*p.fwd20.median(),100*p.fwd60.mean()))
raw = pd.read_csv("panel_raw.csv", parse_dates=["d","d20","d60"])
print("panel_raw rows", len(raw), " sau gate rating<=3&liq:", len(p))

def ic_series(df, vcol, ycol, minn=20):
    r=[]
    for d,g in df.groupby("d"):
        g=g[[vcol,ycol]].dropna()
        if len(g)<minn: continue
        r.append(stats.spearmanr(g[vcol],g[ycol]).statistic)
    x=np.array(r); return len(x), x.mean(), x.mean()/(x.std(ddof=1)/np.sqrt(len(x)))

# A. cac bien the do value tren CUNG panel (da qua gate)
p["ey_rank_glob"]=p.groupby("d").earn_yield.rank(pct=True)
p["ey_raw"]=p.earn_yield
for v in ["ey_pct","ey_rank_glob","ey_raw","vs_proxy","cfy_pct","dy_pct","eveb_pct"]:
    for y in ["fwd20","fwd60"]:
        n,m,t=ic_series(p,v,y); print(f"  gate-pool  {v:14} {y}: N={n:3d} IC={m:+.4f} t={t:+.2f}")

# B. universe RONG (chi liq>=3ty, KHONG gate rating) — value co song o do khong?
fa=pd.read_csv("fa8l.csv",parse_dates=["time"])
w = raw[raw.liq>=3e9].copy()
f = np.where(w.Close>0, w.Price/w.Close, 1.0)
w["PEc"]=np.where(w.PE>0,w.PE*f,np.nan); w["ey"]=np.where(w.PEc>0,1/w.PEc,np.nan)
w["fwd20"]=w.c20/w.Close-1; w["fwd60"]=w.c60/w.Close-1
g20=(w.d20-w.d).dt.days; g60=(w.d60-w.d).dt.days
w.loc[~g20.between(20,50),"fwd20"]=np.nan; w.loc[~g60.between(70,130),"fwd60"]=np.nan
w["ey_rank"]=w.groupby("d").ey.rank(pct=True)
for y in ["fwd20","fwd60"]:
    n,m,t=ic_series(w,"ey_rank",y); print(f"  WIDE(liq only, {len(w)} dong)  ey_rank {y}: N={n:3d} IC={m:+.4f} t={t:+.2f}")
# C. khong sua he so gia
w["ey_nofix"]=np.where(w.PE>0,1/w.PE,np.nan); w["r2"]=w.groupby("d").ey_nofix.rank(pct=True)
for y in ["fwd20","fwd60"]:
    n,m,t=ic_series(w,"r2",y); print(f"  WIDE khong sua gia   ey_rank {y}: N={n:3d} IC={m:+.4f} t={t:+.2f}")
# D. kiem chung nguoc: dung cot profit_1M/3M cua BQ (chi de doi chieu, KHONG dung lam ket qua)
