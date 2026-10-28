import pandas as pd, requests, time, os, sys
P='/home/trido/thanhdt/WorkingClaude/mike/kb/projects/'
out=P+'delisted-tickers-survivorship-20261020.d/prices_all/'
d=pd.read_csv(P+'delisted-tickers-survivorship-20261020.csv')
d=d[(d.in_data==False)&(d.cat!='chuyen_san')]
print(len(d),'tickers')
for t in d.ticker.unique():
    f=out+t+'.csv'
    if os.path.exists(f): continue
    try:
        r=requests.get('https://api-finfo.vndirect.com.vn/v4/stock_prices',params={'q':f'code:{t}','sort':'date:asc','size':10000},timeout=40,headers={'User-Agent':'curl/7.88','Accept':'*/*'}).json()['data']
    except Exception as e:
        print(t,'ERR',e); continue
    pd.DataFrame(r).to_csv(f,index=False); time.sleep(0.15)
print('done')
