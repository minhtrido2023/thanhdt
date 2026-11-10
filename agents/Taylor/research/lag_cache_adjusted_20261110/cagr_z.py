import pandas as pd, numpy as np, glob, gzip, hashlib
R="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-mike-lagadj-1110/agents/Taylor/research/lag_cache_adjusted_20261110"
P="/home/trido/thanhdt/wt-lagadj-1110/WorkingClaude/data/pinned_ledgers/"
for f in []:
    b=gzip.open(f).read(); print(f.split("/")[-1], hashlib.md5(b).hexdigest())
def stats(p):
    x=pd.read_csv(p,low_memory=False); d=x[x.record_type=="DAILY"].copy()
    d["t"]=pd.to_datetime(d.ymd); d=d.set_index("t"); nav=d.combined_nav.astype(float)
    yrs=(nav.index[-1]-nav.index[0]).days/365.25
    cagr=(nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1; dd=(nav/nav.cummax()-1).min()
    yr=nav.groupby(nav.index.year).last(); yr0=pd.concat([pd.Series([nav.iloc[0]],index=[2013]),yr]); yret=(yr0/yr0.shift(1)-1).dropna()
    return cagr,dd,nav,yret
res={}
for t in ["ctrl_p0_off","adj_p0_off","ctrl_p0_1m","adj_p0_1m"]:
    p=glob.glob(f"{R}/sandbox_{t.split('_')[0]}/data/*exp_r3z_{t}_univpit*.csv")[0]
    c,dd,nav,yret=stats(p); res[t]=(nav,yret); print(t, f"CAGR {c*100:.3f} DD {dd*100:.2f} final {nav.iloc[-1]/1e9:.3f}B start {nav.index[0].date()} end {nav.index[-1].date()}")
for a,b in [("ctrl_p0_off","adj_p0_off"),("ctrl_p0_1m","adj_p0_1m")]:
    ya,yb=res[a][1],res[b][1]; print(b,"per-year diff pp", ((yb-ya)*100).round(2).to_dict())
    # leave-one-year-out CAGR diff
    na,nb=res[a][0],res[b][0]
    ra,rb=na.pct_change().fillna(0),nb.pct_change().fillna(0)
    yrs=(na.index[-1]-na.index[0]).days/365.25
    for y in [2023,2025,2019]:
        m=na.index.year!=y; ya_=yrs-((na.index[na.index.year==y][-1]-na.index[na.index.year==y][0]).days+1)/365.25
        ca=(1+ra[m]).prod()**(1/ya_)-1; cb=(1+rb[m]).prod()**(1/ya_)-1
        print(f"  drop {y}: ctrl {ca*100:.2f} adj {cb*100:.2f} d {100*(cb-ca):.2f}pp")
    # drop 2023 and 2025 both
    m=~na.index.year.isin([2023,2025]); ya_=yrs-2
    print(f"  drop 2023+2025: d {100*(((1+rb[m]).prod()**(1/ya_))-((1+ra[m]).prod()**(1/ya_))):.2f}pp")
