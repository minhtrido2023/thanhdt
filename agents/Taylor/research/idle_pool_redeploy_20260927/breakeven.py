import glob, numpy as np, pandas as pd
DATA="/home/trido/thanhdt/WorkingClaude/data"
def load(tag):
    h=sorted(glob.glob(f"{DATA}/*_parkgrid_{tag}_univpit.csv")); assert len(h)==1
    d=pd.read_csv(h[0],low_memory=False).dropna(subset=["combined_nav"])
    t=pd.to_datetime(d["ymd"],errors="coerce"); d=d[t.notna()]; t=t[t.notna()]
    g=d.groupby(t.dt.normalize()).last()
    return g["combined_nav"].astype(float), g[["bal_cash_ref","lag_cash_ref"]].fillna(0).sum(axis=1).astype(float)
n30,c30=load("030"); n80,c80=load("080")
idx=n30.index; YRS=(idx[-1]-idx[0]).days/365.25
dts=np.array([(idx[i+1]-idx[i]).days for i in range(len(idx)-1)],float)
def cagr(nav,cash,rate):
    cr=(np.maximum(cash.values[:-1],0)/nav.values[:-1])*rate*dts/365.0
    r=np.diff(np.log(nav.values))+np.log1p(cr)
    return np.exp(r.sum())**(1/YRS)-1
print(f"{'carry%':>7} {'CAGR x=0.30':>12} {'CAGR x=0.80':>12} {'diff pp':>9}")
lo,hi=None,None
for rate in np.arange(0.0,0.121,0.005):
    a,b=cagr(n30,c30,rate),cagr(n80,c80,rate)
    print(f"{rate*100:7.2f} {a*100:11.3f}% {b*100:11.3f}% {(a-b)*100:+8.3f}")
xs=np.arange(0.0,0.121,0.0005)
d=np.array([cagr(n30,c30,r)-cagr(n80,c80,r) for r in xs])
i=np.argmin(np.abs(d)); print(f"\nBREAK-EVEN carry where CAGR(0.30)==CAGR(0.80): {xs[i]*100:.2f}%/yr (diff {d[i]*100:+.4f}pp)")
print(f"measured carry 8.55% => 0.30 is AHEAD by {(cagr(n30,c30,0.0855)-cagr(n80,c80,0.0855))*100:+.3f}pp CAGR and by 7.6pp of bootstrap 5th-pct MaxDD")
