import pandas as pd, numpy as np
BASE="mike/agents/Taylor/research/fearbuy_blend"; HOLD=375
f="data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_discC4_control_univpit.csv"
d=pd.read_csv(f,low_memory=False); d=d[d.combined_nav.notna()&d.ymd.notna()].copy(); d['ymd']=pd.to_datetime(d['ymd']); d=d.sort_values('ymd')
g=d.groupby('ymd')
v24=g['combined_nav'].last().astype(float); cal=v24.index; r_v24=v24.pct_change().fillna(0.0)
# invested fraction: (bal_stocks+bal_etf+lag_stocks+lag_etf)/combined_nav
def col(c): return g[c].last().astype(float)
inv=(col('bal_stocks_ref').fillna(0)+col('bal_etf_ref').fillna(0)+col('lag_stocks_ref').fillna(0)+col('lag_etf_ref').fillna(0))/v24
inv=inv.clip(0,1.2); cash_w=(1-inv).clip(0,1)
print("invested-fraction quantiles:", inv.quantile([0,.1,.25,.5,.75,.9,1]).round(2).tolist())

px=pd.read_csv(f"{BASE}/prices.csv"); px['time']=pd.to_datetime(px['time'])
pv=px.pivot(index='time',columns='ticker',values='Close').sort_index().reindex(cal).ffill(limit=5); ret=pv.pct_change()
pan=pd.read_csv(f"{BASE}/panel.csv"); pan['adv_b']=pan['adv_vnd']/1e9; pan['s']=-pan['mkt_dd']; pan['entry_date']=pd.to_datetime(pan['entry_date'])
pbmax=np.clip(1.0-2.0*(pan.s-0.20),0.40,1.0)
q=pan[(pan.s>=0.20)&(pan.PB<=pbmax)&(pan.adv_b>=10)].sort_values(['entry_date','PB'])
def m2c(dt): i=cal.searchsorted(dt); return min(i,len(cal)-1)
pos=[]
for _,r in q.iterrows():
    if r.ticker not in ret.columns: continue
    ei=m2c(r.entry_date); pos.append((r.ticker,ei,min(ei+HOLD,len(cal)-1)))
sr=pd.Series(0.0,index=cal); nheld=pd.Series(0,index=cal)
for ti in range(len(cal)):
    held=[p for p in pos if p[1]<=ti<p[2]]
    if not held: continue
    nheld.iloc[ti]=len(held)
    rr=[ret[p[0]].iloc[ti] for p in held]; rr=[x for x in rr if pd.notna(x)]
    if rr: sr.iloc[ti]=np.mean(rr)
active=nheld>0
print(f"\nactive sessions={active.sum()} ({100*active.mean():.0f}% of time)")

# --- redundancy test: during active windows, sleeve vs V2.4 cumret ---
sa=sr[active]; va=r_v24[active]
print("\n=== DURING ACTIVE WINDOWS ===")
print(f"  sleeve total cumret : {((1+sr[active]).prod()-1)*100:+.0f}%   annualized ~{(( (1+sr[active]).prod())**(252/active.sum())-1)*100:+.1f}%")
print(f"  V2.4   total cumret : {((1+r_v24[active]).prod()-1)*100:+.0f}%   annualized ~{(( (1+r_v24[active]).prod())**(252/active.sum())-1)*100:+.1f}%")
print(f"  corr(sleeve, V2.4) on active days: {np.corrcoef(sa,va)[0,1]:.2f}")
print(f"  sleeve beats V2.4 on {100*(sa.values>va.values).mean():.0f}% of active days")
# baseline invested fraction during active windows (is capital idle?)
print(f"  baseline invested-fraction during active windows: mean={inv[active].mean():.2f} median={inv[active].median():.2f}")
print(f"  ... during FIRST 40 sessions of each entry (deep trough): ", end="")
firsts=[]
seen=set()
for p in pos:
    for ti in range(p[1],min(p[1]+40,len(cal))): firsts.append(ti)
firsts=sorted(set(firsts)); print(f"invested mean={inv.iloc[firsts].mean():.2f}")

# --- cash-aware UPPER-BOUND blend: fund from idle cash first, book only if needed ---
def metrics(nav):
    nav=nav.dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    c=((nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1)*100; dd=((nav/nav.cummax()-1).min())*100
    r=nav.pct_change().dropna(); npy=len(r)/yrs; sh=(r.mean()/r.std())*np.sqrt(npy)
    return c,sh,dd,(c/abs(dd))
mb=metrics(v24); print(f"\nBASELINE full: CAGR={mb[0]:.2f}% Sharpe={mb[1]:.2f} MaxDD={mb[2]:.1f} Calmar={mb[3]:.2f}")
print("\n=== CASH-AWARE UPPER BOUND (fund sleeve from idle cash first; displace book only if w>cash) ===")
print(f"  {'w':<6}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'dCAGR':>8}{'dMaxDD':>8}")
for w in [0.05,0.10,0.15,0.20]:
    wt=pd.Series(0.0,index=cal); wt[active]=w
    x=np.minimum(wt,cash_w)          # funded from cash (earns ~0, so we ADD sleeve ret)
    disp=(wt-x).clip(lower=0)        # displaces book
    rbook=(r_v24/inv.clip(lower=0.25))  # approx return on invested portion
    rc=r_v24 + wt*sr - disp*rbook - x*0.0
    nav=(1+rc).cumprod()*v24.iloc[0]; m=metrics(nav)
    print(f"  {w:<6.2f}{m[0]:>7.2f}%{m[1]:>8.2f}{m[2]:>7.1f}%{m[3]:>8.2f}{m[0]-mb[0]:>+7.2f}{m[2]-mb[2]:>+7.1f}")

print("\n"+"="*90)
print("ROBUSTNESS: IS(2014-19) vs OOS(2020+) + per-entry-year sleeve contribution")
print("="*90)
def winm(nav,y1,y2):
    s=nav[(nav.index.year>=y1)&(nav.index.year<=y2)]; return metrics(s)
# cash-aware w=0.10 blend nav
w=0.10; wt=pd.Series(0.0,index=cal); wt[active]=w
x=np.minimum(wt,cash_w); disp=(wt-x).clip(lower=0); rbook=(r_v24/inv.clip(lower=0.25))
rc=r_v24+wt*sr-disp*rbook; navb=(1+rc).cumprod()*v24.iloc[0]
for lab,(y1,y2) in [("IS 2014-19",(2014,2019)),("OOS 2020-26",(2020,2026))]:
    mb2=winm(v24,y1,y2); mm=winm(navb,y1,y2)
    print(f"  {lab}:  base CAGR={mb2[0]:.2f}%  blend(w10,cash-aware)={mm[0]:.2f}%  dCAGR={mm[0]-mb2[0]:+.2f}pp  dMaxDD={mm[2]-mb2[2]:+.1f}")
# per-entry-year: cumret of sleeve names entered that crisis-year (standalone, ex-VNI not needed here)
print("\n  per-entry-crisis sleeve standalone (equal-wt basket, 18m buy&hold, mean r24 of that year's entries):")
for y in sorted(q.yr.unique()):
    yy=q[q.yr==y]; r24=yy['r24'].dropna(); ex24=yy['ex24'].dropna()
    print(f"    {y}: N={len(yy):>2}  mean r24={r24.mean()*100:+6.0f}%  median ex24={ex24.median()*100:+5.0f}%")
