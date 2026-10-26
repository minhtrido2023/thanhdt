import pandas as pd, numpy as np
D='/home/trido/thanhdt/WorkingClaude/data/'
def pct(x,v): x=x.dropna(); return round(100*(x<v).mean()+50*(x==v).mean(),1)
b=pd.read_csv(D+'brent_monthly.csv'); b['m']=pd.to_datetime(b.month)
last=b.iloc[-1]; print('brent last',last.month,last.price)
b5=b[b.m>last.m-pd.DateOffset(years=5)]; b10=b[b.m>last.m-pd.DateOffset(years=10)]
print('brent 5y median',b5.price.median(),'10y pct',pct(b10.price,last.price))
# 12m avg (gas price formula lags)
b['p12']=b.price.rolling(12).mean(); b10=b[b.m>last.m-pd.DateOffset(years=10)]
print('brent 12m avg',round(b.p12.iloc[-1],1),'5y med 12mavg',round(b5.index.map(lambda i:b.p12[i]).to_series().median(),1),'10y pct',pct(b10.p12,b.p12.iloc[-1]))
print(b.tail(8)[['month','price']].to_string())
o=pd.read_csv(D+'oni_index.csv'); print(o.tail(6).to_string())
o10=o[o.year>=2016]; print('oni 10y pct',pct(o10.anom,o.anom.iloc[-1]),'5y med',o[o.year>=2021].anom.median())
fx=pd.read_csv(D+'vcb_fx_rate.csv'); print(fx.columns.tolist()); print(fx.tail(2))
