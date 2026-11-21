import sys; sys.path.insert(0,'agents/Taylor/research/lead_signal_runup_20261118')
import lib, numpy as np, pandas as pd
df,_=lib.load(2012)
df=df[df.in_universe].copy()
g=df.groupby('ticker')
df['ref']=g['Price'].shift(1); df['gap']=(df.time-g['time'].shift(1)).dt.days
df['r']=df.Price/df.ref-1
df['y']=df.time.dt.year
print(df.groupby('y').agg(n=('r','size'),mn=('r','min'),p001=('r',lambda x:x.quantile(.001)),p999=('r',lambda x:x.quantile(.999)),mx=('r','max')))
# fraction of days with r<=-6.5% / -4.5 / by year
for t in (-.045,-.065,-.068):
    print(t, df[df.r<=t].groupby('y').size().to_dict())
df.to_pickle('/tmp/pf_df.pkl'); print(len(df))
