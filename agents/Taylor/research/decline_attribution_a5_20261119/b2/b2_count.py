import pandas as pd, numpy as np
R='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/'
c=pd.read_csv('hist_control.csv'); t=pd.read_csv('hist_treat.csv'); cur=pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/rating_8l_history.csv')
print('control vs existing csv: rows',len(c),len(cur),'identical frame:',c.equals(cur))
if not c.equals(cur):
    m=c.merge(cur,on=['ticker','eff_date','q_time'],suffixes=('','_cur')); print(' diff rows',(m.rating!=m.rating_cur).sum())
X=['PVS','PVD','PVC','PVB','GAS','BSR','TLH','VOS','HAH','DRC','CSM','BMP','NTP']
k=['ticker','eff_date','q_time']; m=c.merge(t,on=k,suffixes=('_c','_t'),how='outer',indicator=True); print(m._merge.value_counts().to_dict())
d=m[m._merge=='both']; print('non-X rows changed:',((d.rating_c!=d.rating_t)&~d.ticker.isin(X)).sum(), 'route chg in X:',d[d.ticker.isin(X)].groupby(['route_c','route_t']).ticker.nunique().to_dict())
x=d[d.ticker.isin(X)].copy(); x['pc']=x.rating_c<=3; x['pt']=x.rating_t<=3
x['flip']=x.pc!=x.pt; x['rating_changed']=x.rating_c!=x.rating_t
print('X rows',len(x),'tickers',x.ticker.nunique(),'| rating changed rows',x.rating_changed.sum(),'| GATE flips (mã,quý)',x.flip.sum(),'| pass->fail',(x.pc&~x.pt).sum(),'| fail->pass',(~x.pc&x.pt).sum())
print(x[x.flip].groupby('ticker').size().to_string())
x[x.flip].to_csv('b2_gate_flips.csv',index=False)
# deals
x['eff']=pd.to_datetime(x.eff_date); out=[]
for f,e in (('features.csv','pin0%'),('features_pin1M.csv','pin1M')):
    d2=pd.read_csv(R+'lag_bal_discriminators_20261025/'+f); d2=d2[(~d2.abandoned)&(~d2.mtm)&d2.ticker.isin(X)].copy()
    d2['sd']=pd.to_datetime(d2.signal_date)
    for _,r in d2.iterrows():
        s=x[(x.ticker==r.ticker)&(x.eff<=r.sd)].sort_values('eff')
        if not len(s): continue
        l=s.iloc[-1]; out.append(dict(end=e,book=r.book,ticker=r.ticker,signal_date=r.signal_date,eff=l.eff_date,q=l.q_time,rating_c=l.rating_c,rating_t=l.rating_t,flip=bool(l.flip),ret=r.ret,year=r.year))
O=pd.DataFrame(out); O.to_csv('b2_deals_X.csv',index=False)
print(O.groupby(['end','book']).agg(deals=('flip','size'),flip=('flip','sum')).to_string())
print(O[O.flip].to_string())
# pairs touched by any pin deal (mã, quý)
for e in ('pin0%','pin1M'):
    o=O[(O.end==e)&O.flip]; print(e,'distinct flipped (mã,quý) with deals:',o[['ticker','q']].drop_duplicates().shape[0])
