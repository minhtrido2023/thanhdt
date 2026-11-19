import pandas as pd, numpy as np
R='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/'
BK=['VAB','KLB','NVB','PGB','SGB','PCB','ABB','BAB','BVB','VBB']
h=pd.read_csv('hist_control.csv'); f=pd.read_csv('bank_roe.csv',parse_dates=['time'])
for e,fn in (('pin0%','features.csv'),('pin1M','features_pin1M.csv')):
    d=pd.read_csv(R+'lag_bal_discriminators_20261025/'+fn); d=d[(~d.abandoned)&(~d.mtm)]
    print(e,'deals in 10 banks:',d[d.ticker.isin(BK)].groupby(['ticker','book']).size().to_dict() or 'NONE', '| any ledger incl. abandoned/mtm:', pd.read_csv(R+'lag_bal_discriminators_20261025/'+fn).query('ticker in @BK').shape[0])
b=h[h.ticker.isin(BK)]
print('hist rows for 10 banks',len(b),'by rating',b.rating.value_counts().sort_index().to_dict(),'| routes',b.route.unique())
f['roe']=f.ROE_Trailing.fillna(f.ROE5Y).fillna(f.ROE3Y)
m=b.merge(f[['ticker','time','quarter','roe']],left_on=['ticker','q_time'],right_on=['ticker',f.time.dt.strftime('%Y-%m-%d')] if False else ['ticker','time'],how='left') if False else None
f['q_time']=f.time.dt.strftime('%Y-%m-%d'); m=b.merge(f[['ticker','q_time','roe']],on=['ticker','q_time'],how='left')
print('unmatched to ticker_financial:',m.roe.isna().sum(),'of',len(m))
nd=m[m.roe.isna()]; print('ROE all-NaN rows',len(nd),'with rating<=3 (default branch):',(nd.rating<=3).sum(), nd.groupby('ticker').size().to_dict())
print('rating==3 rows total',(m.rating==3).sum(),'| of which ROE in [12%,..) etc: roe-derived',((m.rating==3)&m.roe.notna()).sum())
# pairs that would change if nodata 3->4: rows from default branch with rating 3
print('PAIRS flipping if default 3->4 in history (ROE NaN & rating 3):',((m.roe.isna())&(m.rating==3)).sum())
# in-universe overlap
u=pd.read_csv('bank_universe.csv'); print(u.to_string())
# STB/EIB/SSB
for t in ['STB','EIB','SSB']:
    x=f[f.ticker==t].sort_values('time').tail(5)[['quarter','ROE_Trailing','ROE5Y','ROE3Y']]; print(t); print(x.round(4).to_string(index=False))
