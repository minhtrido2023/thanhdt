"""Multiple-testing view over the 4 HIGH-LOW comparisons per period + monotonicity verdict
against PREREG 2.3 (i)(ii)(iii). Post-hoc robustness clearly labelled as such."""
import numpy as np, pandas as pd
ics=pd.read_csv("h5_daily_ic.csv",parse_dates=["date"])
def bb(x,mon,B=4000,seed=11):
    rng=np.random.default_rng(seed); um=mon.unique(); idx={m:np.where(mon==m)[0] for m in um}
    return np.array([np.nanmean(x[np.concatenate([idx[m] for m in rng.choice(um,len(um),True)])]) for _ in range(B)])
rows=[]
for period,a,b in [("IS","2016-04-01","2019-12-31"),("OOS","2020-01-01","2026-08-31")]:
    w=ics[(ics.date>=a)&(ics.date<=b)]
    for axis in ["retail_ter","breadth_ter"]:
        for fac in ["ic_mom","ic_ey"]:
            hi,lo=w[w[axis]=="HIGH"],w[w[axis]=="LOW"]
            mid=w[w[axis]=="MID"]
            vals=[np.nanmean(lo[fac]),np.nanmean(mid[fac]),np.nanmean(hi[fac])]
            mono = (vals[0]<=vals[1]<=vals[2]) or (vals[0]>=vals[1]>=vals[2])
            d=bb(hi[fac].to_numpy(),hi.date.dt.to_period("M"))-bb(lo[fac].to_numpy(),lo.date.dt.to_period("M"),seed=23)
            p=2*min((d<=0).mean(),(d>=0).mean())
            rows.append(dict(period=period,axis=axis.replace("_ter",""),factor=fac,
                             n_mon_LO=lo.date.dt.to_period("M").nunique(),
                             n_mon_MID=mid.date.dt.to_period("M").nunique(),
                             n_mon_HI=hi.date.dt.to_period("M").nunique(),
                             hi_minus_lo=round(vals[2]-vals[0],4),monotonic=mono,p_boot=round(p,4)))
r=pd.DataFrame(rows)
# BH within each period over the 4 comparisons
for per in ["IS","OOS"]:
    m=r.period==per; pv=r.loc[m,"p_boot"].to_numpy(); o=np.argsort(pv); n=len(pv)
    adj=np.empty(n); prev=1.0
    for rank,i in enumerate(o[::-1]):
        prev=min(prev,pv[i]*n/(n-rank)); adj[i]=prev
    r.loc[m,"p_BH_4cmp"]=np.round(adj,4)
print(r.to_string(index=False))
print("\n=== PREREG 2.3 PASS/FAIL (can CA 3: (i) cung dau IS&OOS, (ii) CI OOS khong chua 0, (iii) don dieu) ===")
for axis in ["retail","breadth"]:
    for fac in ["ic_mom","ic_ey"]:
        i_=r[(r.axis==axis)&(r.factor==fac)&(r.period=="IS")].iloc[0]
        o_=r[(r.axis==axis)&(r.factor==fac)&(r.period=="OOS")].iloc[0]
        c1=np.sign(i_.hi_minus_lo)==np.sign(o_.hi_minus_lo)
        c2=o_.p_boot<0.05
        c3=bool(i_.monotonic and o_.monotonic)
        v="PASS" if (c1 and c2 and c3) else "KHONG DU BANG CHUNG"
        print(f"  {axis:8s} {fac:7s}: (i)cung_dau={c1}  (ii)OOS_CI_loai_0={c2} (p_boot={o_.p_boot}, p_BH={o_.p_BH_4cmp})  (iii)don_dieu IS={i_.monotonic}/OOS={o_.monotonic}  => {v}")
r.to_csv("h5_ic_verdict.csv",index=False)
