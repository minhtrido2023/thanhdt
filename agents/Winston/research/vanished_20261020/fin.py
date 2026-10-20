import requests, pandas as pd, time, json
P='/home/trido/thanhdt/WorkingClaude/mike/kb/projects/'
F=pd.read_csv(P+'delisted-big-vanished-prices-20261020.csv',parse_dates=['end_orig_date'])
ITEMS={12700:'total_assets',13000:'total_liab',13110:'st_loan',13340:'lt_loan',14400:'total_equity',21001:'revenue',23003:'npat',23000:'npat_parent',32000:'cfo'}
H={'User-Agent':'curl/7.88','Accept':'*/*'}
out=[]
for t in F.ticker:
    for mt in (1,2,3,11,12,13):
        q=f'code:{t}~reportType:QUARTER~modelType:{mt}~itemCode:'+','.join(str(i) for i in ITEMS)
        # itemCode multi via separate param style
        try:
            r=requests.get('https://api-finfo.vndirect.com.vn/v4/financial_statements',params={'q':f'code:{t}~reportType:QUARTER~modelType:{mt}','size':3000,'sort':'fiscalDate:desc'},headers=H,timeout=40).json()['data']
        except Exception as e:
            print(t,mt,'ERR',e);continue
        for x in r:
            if int(x['itemCode']) in ITEMS: out.append(dict(ticker=t,modelType=mt,item=ITEMS[int(x['itemCode'])],fiscalDate=x['fiscalDate'],value=x['numericValue']))
        time.sleep(0.1)
pd.DataFrame(out).to_csv('fin_raw.csv',index=False); print(len(out))
