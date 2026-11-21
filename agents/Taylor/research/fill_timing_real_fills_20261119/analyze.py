import pandas as pd,numpy as np
D='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fill_timing_real_fills_20261119/'
M=pd.read_csv(D+'orders_classified_raw.csv'); B=pd.read_csv(D+'bq_open.csv')
B['open_unadj']=B.Open*B.Price/B.Close
M=M.merge(B.rename(columns={'ticker':'sym','d':'date'})[['sym','date','open_unadj','Open','Close','Price']],on=['sym','date'],how='left')
print('no open:',M.open_unadj.isna().sum())
M['bps']=(M.avg/M.open_unadj-1)*1e4
M['group']=np.where(M.cls=='NO_JOURNAL_MATCH','NO_JOURNAL(ATC/late)',np.where(M.post_0826,M.cls,'PRE_HYBRID_UNIFORM'))
M['dayret']=(M.Close/M.open_unadj-1)  # Close adj vs open_unadj mismatch? use Price/open_unadj
M['dayret']=M.Price/M.open_unadj-1
M.to_csv(D+'orders_classified.csv',index=False)
# unit = account,date,sym,side,group
U=M.groupby(['account','date','sym','side','group']).apply(lambda g:pd.Series(dict(bps=np.average(g.bps,weights=g.qty),n_ord=len(g),qty=g.qty.sum(),dayret=g.dayret.iloc[0]))).reset_index()
U['week']=pd.to_datetime(U.date).dt.strftime('%G-W%V')
rng=np.random.default_rng(20261119)
def ci(x,w):
    ws=sorted(w.unique());
    if len(x)<30 or len(ws)<8: return np.nan,np.nan
    g={k:x[w==k].values for k in ws}; m=[]
    for _ in range(5000):
        s=np.concatenate([g[k] for k in rng.choice(ws,len(ws))]); m.append(s.mean())
    return np.percentile(m,2.5),np.percentile(m,97.5)
out=[]
for (side,grp),g in U.groupby(['side','group']):
    lo,hi=ci(g.bps,g.week)
    out.append(dict(side=side,group=grp,n_orders=int(g.n_ord.sum()),n_units=len(g),n_days=g.date.nunique(),n_weeks=g.week.nunique(),mean_bps=g.bps.mean(),median_bps=g.bps.median(),ci_lo=lo,ci_hi=hi,enough_N=not np.isnan(lo)))
R=pd.DataFrame(out); R.to_csv(D+'results_bps.csv',index=False); print(R.round(1).to_string())
# ex-post: down/up day
U['dn']=np.where(U.dayret<0,'down','up/flat')
print(U.groupby(['side','group','dn']).bps.agg(['count','mean']).round(1).to_string())
# by account
print(U.groupby(['side','group','account']).bps.agg(['count','mean']).round(1).to_string())
# BUY HYB by block hour
M['hh']=M.created.str[:5]
print(M[(M.group.str.startswith('HYB'))].groupby(['side','group',M.created.str[:2]]).bps.agg(['count','mean']).round(1).to_string())
print('hi/lo bps', M.bps.describe().round(1).to_string())
