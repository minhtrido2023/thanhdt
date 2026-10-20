"""PREREG_V2 §3: BCTC quý VNDirect cho tập N (cùng endpoint/ITEMS với svr_fetch.py). Ghi data/fin_raw_v2.csv."""
import requests, pandas as pd, time, json
H = {'User-Agent': 'curl/7.88', 'Accept': '*/*'}
ITEMS = {12700: 'total_assets', 13000: 'total_liab', 13110: 'st_loan', 13340: 'lt_loan', 14400: 'total_equity',
         21001: 'revenue', 23003: 'npat', 23000: 'npat_parent', 32000: 'cfo'}
N = json.load(open("data/v2_sets.json"))["N"]
out, errs = [], []
for t in N:
    for mt in (1, 2, 3):
        for att in range(3):
            try:
                r = requests.get('https://api-finfo.vndirect.com.vn/v4/financial_statements', headers=H, timeout=60,
                                 params={'q': f'code:{t}~reportType:QUARTER~modelType:{mt}', 'size': 3000, 'sort': 'fiscalDate:desc'}).json()['data']
                break
            except Exception as e:
                r = None; err = f"{type(e).__name__}: {e}"; time.sleep(2)
        if r is None:
            errs.append((t, mt, err)); print(t, mt, 'ERR', err, flush=True); continue
        for x in r:
            if int(x['itemCode']) in ITEMS:
                out.append(dict(ticker=t, modelType=mt, item=ITEMS[int(x['itemCode'])], fiscalDate=x['fiscalDate'], value=x['numericValue']))
        time.sleep(0.15)
    print(t, flush=True)
pd.DataFrame(out).to_csv('data/fin_raw_v2.csv', index=False)
json.dump(errs, open('data/fin_fetch_errors.json', 'w'))
print('rows', len(out), 'tickers', pd.DataFrame(out).ticker.nunique() if out else 0, 'errs', len(errs))
