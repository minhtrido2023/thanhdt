import pandas as pd, glob, os, numpy as np
P='/home/trido/thanhdt/WorkingClaude/mike/kb/projects/'
d=pd.read_csv(P+'delisted-tickers-survivorship-20261020.csv').drop_duplicates('ticker').set_index('ticker')
rows=[]
for f in glob.glob(P+'delisted-tickers-survivorship-20261020.d/prices_all/*.csv'):
    t=os.path.basename(f)[:-4]
    try: x=pd.read_csv(f)
    except: rows.append(dict(ticker=t,n=0));continue
    if x.empty or 'date' not in x: rows.append(dict(ticker=t,n=0));continue
    x['date']=pd.to_datetime(x.date); x=x.sort_values('date')
    x['val']=(x.nmValue.fillna(0))  # VND? check
    ld=pd.to_datetime(d.loc[t,'last_trade'],dayfirst=True,errors='coerce')
    dd=pd.to_datetime(d.loc[t,'delist_date'],dayfirst=True,errors='coerce')
    cut=ld if pd.notna(ld) else dd
    rows.append(dict(ticker=t,n=len(x),first=x.date.min(),last=x.date.max(),floor_last=x.floor.iloc[-1],cut=cut,
        maxval=x.val.max(),med60=x.val.tail(60).median(),maxmed60=x.val.rolling(60).median().max()))
r=pd.DataFrame(rows); r=r.join(d[['exch2','cat','reason']],on='ticker')
r.to_csv('stats_all.csv',index=False)
print(r.n.eq(0).sum(),'empty of',len(r))
print(r.sort_values('maxmed60',ascending=False).head(40)[['ticker','exch2','cat','n','first','last','floor_last','cut','maxval','maxmed60']].to_string())
