import numpy as np, pandas as pd
from scipy import stats
dp = pd.read_csv("dispersion.csv", parse_dates=["d"])
dp["terc"]=pd.qcut(dp.iqr,3,labels=["HEP","GIUA","RONG"])
print("phan bo tercile theo nam:")
print(pd.crosstab(dp.d.dt.year, dp.terc).to_string())
# dem block lien tuc
def blocks(mask, dates):
    b=[];cur=None
    for m,d in zip(mask,dates):
        if m and cur is None: cur=[d,d]
        elif m: cur[1]=d
        elif cur: b.append(tuple(cur)); cur=None
    if cur: b.append(tuple(cur))
    return b
for tc in ["HEP","RONG"]:
    bl=blocks((dp.terc==tc).values, dp.d.values)
    print(f"\n{tc}: {int((dp.terc==tc).sum())} thang -> {len(bl)} block lien tuc; "
          f"do dai(thang) {[int(round((pd.Timestamp(b)-pd.Timestamp(a)).days/30.4))+1 for a,b in bl]}")
    print("   ", [f"{pd.Timestamp(a):%Y-%m}..{pd.Timestamp(b):%Y-%m}" for a,b in bl])
print("\nautocorr IQR lag1..6:", [round(dp.iqr.autocorr(k),3) for k in range(1,7)])

# t-test o MUC BLOCK (moi block = 1 quan sat doc lap) cho ca 4 bien the
for v in ["ey_pct","vs_proxy"]:
    for y in ["fwd20","fwd60"]:
        fm=pd.read_csv(f"fm_{v}_{y}.csv",parse_dates=["d"]).merge(dp[["d","terc","iqr"]],on="d")
        fm["blk"]=(fm.terc!=fm.terc.shift()).cumsum()
        bm=fm.groupby(["blk","terc"],observed=True).ic.mean().reset_index()
        xr=bm[bm.terc=="RONG"].ic; xh=bm[bm.terc=="HEP"].ic
        t,p=stats.ttest_ind(xr,xh,equal_var=False)
        # bootstrap block: lay mau lai cac block
        rng=np.random.default_rng(7); dif=[]
        for _ in range(20000):
            a=rng.choice(xr.values,len(xr)); b=rng.choice(xh.values,len(xh)); dif.append(a.mean()-b.mean())
        lo,hi=np.percentile(dif,[5,95])
        print(f"\n{v}/{y}: BLOCK-level  N_RONG={len(xr)} block, N_HEP={len(xh)} block")
        print(f"   IC_RONG={xr.mean():+.3f}  IC_HEP={xh.mean():+.3f}  d={xr.mean()-xh.mean():+.3f}"
              f"  t={t:+.2f} p={p:.3f}  CI90(bootstrap block)=[{lo:+.3f};{hi:+.3f}]")
