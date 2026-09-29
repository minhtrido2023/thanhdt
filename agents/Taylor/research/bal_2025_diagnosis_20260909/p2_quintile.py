import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('p2_panel_exp.csv',parse_dates=['time']); d=d[d.adv_vnd>=1e9].copy()
FEAT=['prox52','idiovol_ann','ey','mom12_1','trend_atr','eff_ratio60','bb_pctb_centered','rsi','fip','cmf','volratio','residmom_scaled','mom3m','macddiff','px_ma50','pe_z','relmom12_1']
def nw_t(x,l):
    x=np.asarray(x,float);n=len(x);e=x-x.mean();g0=(e*e).sum()/n;s=g0
    for L in range(1,l+1): s+=2*(1-L/(l+1))*((e[L:]*e[:-L]).sum()/n)
    return x.mean()/np.sqrt(s/n) if s>0 else np.nan
# --- BH correction on FULL + OOS, fwd=profit_1M ---
res=[]
for f in FEAT:
    for lab,(a,b) in {'FULL':(None,None),'OOS':('2020-01-01','2026-06-19')}.items():
        s=d if a is None else d[(d.time>=a)&(d.time<=b)]
        ics=[]
        for t,g in s.groupby('time'):
            g=g[[f,'profit_1M']].dropna()
            if len(g)>=20: ics.append(stats.spearmanr(g[f],g['profit_1M']).statistic)
        ics=np.array(ics); t_=nw_t(ics,1)
        res.append(dict(feature=f,window=lab,n=len(ics),ic=ics.mean(),t=t_,p=2*(1-stats.norm.cdf(abs(t_)))))
R=pd.DataFrame(res)
for lab in ['FULL','OOS']:
    m=R.window==lab
    p=R.loc[m,'p'].values; n=len(p); o=np.argsort(p); adj=np.empty(n)
    prev=1.0
    for k in range(n-1,-1,-1):
        prev=min(prev, p[o[k]]*n/(k+1)); adj[o[k]]=prev
    R.loc[m,'p_BH']=adj
print('=== IC + BH (fwd=profit_1M, N=months) ===')
print(R.sort_values(['window','p_BH']).round(4).to_string(index=False))
R.to_csv('p2_ic_bh.csv',index=False)

# --- quintile spread, monotonicity ---
print('\n=== Quintile mean profit_1M (%) by feature, monthly cross-section ===')
rows=[]
for f in ['prox52','idiovol_ann','ey','mom12_1']:
    for lab,(a,b) in {'FULL':(None,None),'IS':('2014-01-01','2019-12-31'),'OOS':('2020-01-01','2026-06-19'),'2026H1':('2026-01-01','2026-06-19')}.items():
        s=d if a is None else d[(d.time>=a)&(d.time<=b)]
        s=s.dropna(subset=[f,'profit_1M']).copy()
        s['q']=s.groupby('time')[f].transform(lambda x: pd.qcut(x.rank(method='first'),5,labels=False)+1 if x.nunique()>=5 else np.nan)
        mm=s.groupby(['time','q']).profit_1M.mean().unstack()
        if mm.shape[1]<5: continue
        sp=(mm[5]-mm[1]).dropna()
        rows.append(dict(feature=f,window=lab,**{f'Q{i}':mm[i].mean() for i in range(1,6)},
                         spread=sp.mean(), t_spread=nw_t(sp.values,1), n_m=len(sp),
                         monotonic=bool(np.all(np.diff([mm[i].mean() for i in range(1,6)])>0) or np.all(np.diff([mm[i].mean() for i in range(1,6)])<0))))
Q=pd.DataFrame(rows); print(Q.round(3).to_string(index=False)); Q.to_csv('p2_quintiles.csv',index=False)

print('\n=== Spearman correlation between top candidates (pooled) ===')
print(d[['prox52','idiovol_ann','ey','mom12_1','rsi','trend_atr','adv_vnd']].corr(method='spearman').round(3).to_string())
