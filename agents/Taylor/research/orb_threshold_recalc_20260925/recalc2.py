# -*- coding: utf-8 -*-
"""Bo sung: kha thi cua muc tieu DSR 0.95 so voi DOI SONG hop dong VN30F1M."""
import json, numpy as np, pandas as pd
from scipy import stats as st
a = pd.read_csv("../orb_fiinx_vn30f1m_20260925/orb_trades_extended_20220217_20260925.csv")
x=a["net"].values; n0=len(x); mu=x.mean(); sd=x.std(ddof=1)
sk=st.skew(x); ku=st.kurtosis(x,fisher=False); sr=mu/sd
G=0.5772156649
def psr(sr_,sr0,n): return st.norm.cdf((sr_-sr0)*np.sqrt(n-1)/np.sqrt(1-sk*sr_+(ku-1)/4*sr_**2))
def sr0_of(N,n):
    e=(1-G)*st.norm.ppf(1-1/N)+G*st.norm.ppf(1-1/(N*np.e)); return e/np.sqrt(n)
def dsr(n,N=20,sr_=sr): return psr(sr_,sr0_of(N,n),n)

# doi song hop dong VN30F1M: 2017-08-10 -> 2026-09-25
life_days = (pd.Timestamp("2026-09-25")-pd.Timestamp("2017-08-10")).days
life_sessions = life_days/365.25*252
res={"life_years":life_days/365.25,"life_sessions":life_sessions,
     "dsr_if_full_history": float(dsr(life_sessions)),
     "dsr_n2300": float(dsr(2300)), "dsr_n1129": float(dsr(n0))}

# SR/obs can co de DSR(N=20)=0.95 ngay o n hien tai / o n = toan bo doi song
def sr_needed(n, N=20, target=0.95):
    lo,hi=1e-5,1.0
    for _ in range(200):
        mid=(lo+hi)/2
        if dsr(n,N,mid)>=target: hi=mid
        else: lo=mid
    return hi
for n in (n0, int(life_sessions), 2000):
    s_=sr_needed(n)
    res[f"sr_needed_n{n}"]={"sr_per_obs":s_,"mean_bps":s_*sd*1e4,"sharpe_ann":s_*np.sqrt(252),
                            "x_vs_observed":s_/sr}
# N tong can (hop nhat) de dat power 80% hai phia, tru phan da co
z=st.norm.ppf(0.975)+st.norm.ppf(0.80)
res["n_total_power80_2s"]=(z*sd/mu)**2
res["n_extra_power80_2s"]=res["n_total_power80_2s"]-n0
res["yrs_extra_power80_2s"]=res["n_extra_power80_2s"]/252
res["n_extra_dsr095_N20"]=4075-n0; res["yrs_extra_dsr095_N20"]=(4075-n0)/252
print(json.dumps(res,indent=2))
json.dump(res,open("recalc2_result.json","w"),indent=2)
