"""B4b: custom30V membership (data/bq_cache/custom30v_8l.parquet) — tỉ trọng mã producer hàng hoá + pha chu kỳ lúc rebal + lợi suất vượt trội kỳ giữ (đến effective_to) so với thành viên khác."""
import pandas as pd, numpy as np, json
from common import *
c=pd.read_parquet(f'{W}/data/bq_cache/custom30v_8l.parquet'); c['effective_from']=pd.to_datetime(c.effective_from); c['effective_to']=pd.to_datetime(c.effective_to)
m=pd.read_csv('commodity_map_te.csv'); prod=m[(m.sign>0)&(m.ticker!='-')].drop_duplicates('ticker').set_index('ticker')
T=te(); A63={k:T[k].dropna().rolling(63).mean().dropna() for k in prod.te_metric_key.unique()}
def pct_at(key,d):
    a=A63[key]; a=a[a.index<=d-pd.Timedelta(days=2)]; return (a<=a.iloc[-1]).mean() if len(a)>=504 else np.nan
P=px().ffill(); idx=P.index
def r(t,a,b):
    i,j=idx.searchsorted(a),min(idx.searchsorted(b),len(idx)-1)
    if i>=len(idx) or t not in P.columns: return np.nan
    x,y=P[t].iloc[i],P[t].iloc[j]; return y/x-1 if x>0 else np.nan
c['ret']=[r(t,a,b) for t,a,b in zip(c.ticker,c.effective_from,c.effective_to.fillna(idx[-1]))]
c['ex']=c.ret-c.groupby('effective_from').ret.transform('mean')
c['prod']=c.ticker.isin(prod.index)
c['pct']=[pct_at(prod.te_metric_key[t],d) if t in prod.index else np.nan for t,d in zip(c.ticker,c.effective_from)]
print('rebal',c.effective_from.nunique(),c.effective_from.min().date(),c.effective_from.max().date(),'member-rows',len(c))
print('producer share of member-rows',round(c['prod'].mean(),3), c[c['prod']].ticker.value_counts().to_dict())
p=c[c['prod']].dropna(subset=['pct','ex'])
print('producer ex-ret vs basket mean: all',round(p.ex.mean(),4),'n',len(p),'| peak(pct>=.67)',round(p[p.pct>=.67].ex.mean(),4),len(p[p.pct>=.67]),'| trough(<=.33)',round(p[p.pct<=.33].ex.mean(),4),len(p[p.pct<=.33]))
p.to_csv('b4b_custom30v_producers.csv',index=False)
json.dump(dict(share=round(c['prod'].mean(),3),n=len(p),ex_all=p.ex.mean(),ex_peak=p[p.pct>=.67].ex.mean(),n_peak=int((p.pct>=.67).sum()),ex_trough=p[p.pct<=.33].ex.mean(),n_trough=int((p.pct<=.33).sum())),open('b4b_results.json','w'),default=float)
