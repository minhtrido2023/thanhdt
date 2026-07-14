# -*- coding: utf-8 -*-
"""LOO + DSR for Pha-3 variant A (exclude_rich) vs baseline. job Taylor_20260714_073643"""
import numpy as np, pandas as pd, warnings
from scipy import stats
warnings.filterwarnings("ignore")
W="/home/trido/thanhdt/WorkingClaude"
B=f"{W}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
def nav(p):
    d=pd.read_csv(p,low_memory=False)
    d=d[d.combined_nav.notna()&d.ymd.notna()].copy()
    d["ymd"]=pd.to_datetime(d.ymd,errors="coerce")
    return d.dropna(subset=["ymd"]).sort_values("ymd").groupby("ymd").combined_nav.last().astype(float)
base=nav(f"{B}_exp_dcfctrl20260714.csv"); varA=nav(f"{B}_exp_dcfexrich.csv")
def logret(s): return np.log(s/s.shift(1)).dropna()
def met(r):
    if len(r)<20: return dict(cagr=np.nan,sharpe=np.nan,mdd=np.nan,calmar=np.nan)
    yrs=(r.index[-1]-r.index[0]).days/365.25; spy=len(r)/yrs
    eq=np.exp(r.cumsum()); cagr=(eq.iloc[-1]**(1/yrs)-1)*100
    sh=r.mean()/r.std(ddof=1)*np.sqrt(spy)
    mdd=((eq/eq.cummax())-1).min()*100
    return dict(cagr=cagr,sharpe=sh,mdd=mdd,calmar=cagr/abs(mdd) if mdd<0 else np.nan)
rb,ra=logret(base),logret(varA)
print("=== per-year LEAVE-ONE-OUT (drop 1 year, re-chain remaining) ===")
print(f"{'drop':<7}{'baseSh':>8}{'A_Sh':>8}{'dSh':>8}{'baseCal':>9}{'A_Cal':>8}{'dCal':>8}{'dCAGRpp':>9}  gate")
yrs=sorted(set(ra.index.year))
rows=[]
for y in ["none"]+yrs:
    m=(slice(None) if y=="none" else None)
    b2=rb if y=="none" else rb[rb.index.year!=y]; a2=ra if y=="none" else ra[ra.index.year!=y]
    mb,ma=met(b2),met(a2)
    ok=(ma["sharpe"]>mb["sharpe"]) and (ma["calmar"]>mb["calmar"])
    rows.append((y,ok))
    print(f"{str(y):<7}{mb['sharpe']:>8.3f}{ma['sharpe']:>8.3f}{ma['sharpe']-mb['sharpe']:>+8.3f}"
          f"{mb['calmar']:>9.3f}{ma['calmar']:>8.3f}{ma['calmar']-mb['calmar']:>+8.3f}"
          f"{ma['cagr']-mb['cagr']:>+9.2f}  {'PASS' if ok else 'FAIL'}")
nf=[str(y) for y,ok in rows if not ok]
print(f"\nLOO summary: {sum(1 for _,ok in rows if ok)}/{len(rows)} pass; FAIL when dropping: {nf if nf else 'none'}")
# DSR on the DEPLOY candidate (variant A), N trials declared
def dsr(r, N, sr_bench_var=None):
    T=len(r); sr=r.mean()/r.std(ddof=1)          # per-observation SR
    g3=stats.skew(r); g4=stats.kurtosis(r,fisher=False)
    # expected max SR of N independent trials (Bailey-Lopez de Prado)
    e=np.euler_gamma
    sr_std=np.sqrt(sr_bench_var) if sr_bench_var else 0.0
    sr0=sr_std*((1-e)*stats.norm.ppf(1-1/N)+e*stats.norm.ppf(1-1/(N*np.e)))
    num=(sr-sr0)*np.sqrt(T-1)
    den=np.sqrt(1-g3*sr+((g4-1)/4)*sr**2)
    return stats.norm.cdf(num/den), sr, sr0
# variance across the trials actually compared (ctrl, A, B) — per-obs SR
trials=[]
for p in ["_exp_dcfctrl20260714","_exp_dcfexrich","_exp_dcftb025"]:
    rr=logret(nav(f"{B}{p}.csv")); trials.append(rr.mean()/rr.std(ddof=1))
v=np.var(trials,ddof=1)
for N in (3,8):
    d,sr,sr0=dsr(ra,N,v)
    print(f"DSR(variant A, N={N} trials, var_SR={v:.2e}): {d:.4f}  (SR/obs {sr:.4f}, SR0 {sr0:.4f})  -> {'PASS >=0.95' if d>=0.95 else 'RED FLAG <0.95'}")
db,_,_=dsr(rb,3,v); print(f"DSR(baseline ctrl, N=3): {db:.4f}  [reference]")
