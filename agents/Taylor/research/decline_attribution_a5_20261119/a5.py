import sys, numpy as np, pandas as pd
sys.path.insert(0,'.'); import groups
B=20000; rng=np.random.default_rng(20261119)
F={'pin0%':'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/lag_bal_discriminators_20261025/features.csv','pin1M':'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/lag_bal_discriminators_20261025/features_pin1M.csv'}
def boot(x):  # x: DataFrame with ym, ret_pct ; returns B draws of mean via month-cluster resample (ratio of sums)
    g=x.groupby('ym').ret_pct.agg(['sum','count']); s=g['sum'].values; c=g['count'].values; k=len(g)
    idx=rng.integers(0,k,(B,k)); return s[idx].sum(1)/c[idx].sum(1)
rows=[]
for end,f in F.items():
    d=groups.load(f)
    for bk in ('BAL','LAG'):
        for gp in sorted(d.grp.unique()):
            a=d[(d.book==bk)&(d.grp==gp)&(d.era=='2024+')]; b=d[(d.book==bk)&(d.grp==gp)&(d.era=='2014-19')]
            r=dict(end=end,book=bk,grp=gp,n_late=len(a),m_late=a.ym.nunique(),n_early=len(b),m_early=b.ym.nunique(),
                   mean_late=a.ret_pct.mean(),mean_early=b.ret_pct.mean())
            if len(a) and len(b):
                dl=boot(a)-boot(b); dl0=a.ret_pct.mean()-b.ret_pct.mean()
                r.update(delta=dl0,lo90=np.percentile(dl,5),hi90=np.percentile(dl,95),
                         p=max(2*min((dl<=0).mean(),(dl>=0).mean()),1/B))
            rows.append(r)
R=pd.DataFrame(rows)
def bh(p):
    p=np.asarray(p,float); o=np.argsort(p); m=len(p); q=np.empty(m); q[o]=np.minimum.accumulate((p[o]*m/(np.arange(m)+1))[::-1])[::-1]; return np.minimum(q,1)
R['q']=np.nan
for e in F:
    m=(R.end==e)&R.p.notna(); R.loc[m,'q']=bh(R.loc[m,'p'])
piv=R.pivot_table(index=['book','grp'],columns='end',values=['hi90','q'])
lab=[]
for (bk,gp),_ in piv.iterrows():
    h=[piv.loc[(bk,gp),('hi90',e)] for e in F]; q=[piv.loc[(bk,gp),('q',e)] for e in F]
    sig=all(pd.notna(x) and x<0 for x in h)
    lab.append(dict(book=bk,grp=gp,label='tụt có ý nghĩa' if sig else 'không phân biệt được',
                    bh_q010_both=bool(all(pd.notna(x) and x<0.10 for x in q)) if sig else ''))
L=pd.DataFrame(lab); R=R.round(3); R.to_csv('a5_results.csv',index=False); L.to_csv('a5_labels.csv',index=False)
print(R.to_string()); print(L.to_string())
# selfcheck: pnl totals & appendix reproduction for pin0%
d=groups.load(F['pin0%']); print('SELF pnl sum by book',d.groupby('book').pnl.sum().round(0).to_dict(),'rows',len(d))
