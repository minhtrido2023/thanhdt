import pandas as pd, numpy as np
d=pd.read_csv('nnc_px.csv',parse_dates=['time']).set_index('time')
d['val']=d.Price*d.Volume/1e9
last=d.index[-1]; print('last',last.date(),d.Close.iloc[-1])
for n in (20,60,120): print(f'ADV{n} value bn',round(d.val.tail(n).mean(),2),'vol',int(d.Volume.tail(n).mean()))
y=d[d.index>last-pd.Timedelta(days=365)]
print('52w hi/lo',y.Close.max(),y.Close.idxmax().date(),y.Close.min(),y.Close.idxmin().date())
print('zero-vol days 120',int((d.Volume.tail(120)==0).sum()))
rel=['2025-04-21','2025-07-18','2025-10-17','2026-01-21','2026-04-20','2026-07-20','2026-10-20']
for r in rel:
    r=pd.Timestamp(r); i=d.index.searchsorted(r)
    if i<1 or i>=len(d): continue
    p0=d.Close.iloc[i-1]; v0=d.VNINDEX.iloc[i-1]
    out=[]
    for k in (1,5,10):
        j=min(i+k-1,len(d)-1); out.append(f'T+{k} {100*(d.Close.iloc[j]/p0-1):+.1f}% (vs VNI {100*(d.Close.iloc[j]/p0-d.VNINDEX.iloc[j]/v0):+.1f})')
    print(r.date(),'pre',p0,' | '.join(out))
for dt in ['2026-01-07','2026-10-23','2026-10-26']:
    print(dt, d.Close.asof(pd.Timestamp(dt)))
