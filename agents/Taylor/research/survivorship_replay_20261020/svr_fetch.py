"""Tải giá ngày (5 mã còn sống, kiểm định) + BCTC quý (5 mã sống + 21 mã mở rộng) từ VNDirect finfo.
Cùng endpoint/cách gọi với agents/Winston/research/vanished_20261020/{fetch_all,fin}.py. Ghi vào data/."""
import requests, pandas as pd, time, os, sys
H = {'User-Agent': 'curl/7.88', 'Accept': '*/*'}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
LIVE = ['HPG', 'VNM', 'HQC', 'ITA', 'DLG']
EXT = 'KSH TNA KHB VIS CAV DPS VMI AVF KSS RDP SIC IBC CEE PPI SPI GTT NDF KSK KPF ASA BGM'.split()
ITEMS = {12700: 'total_assets', 13000: 'total_liab', 13110: 'st_loan', 13340: 'lt_loan', 14400: 'total_equity',
         21001: 'revenue', 23003: 'npat', 23000: 'npat_parent', 32000: 'cfo'}
os.makedirs(OUT, exist_ok=True)
for t in LIVE:
    r = requests.get('https://api-finfo.vndirect.com.vn/v4/stock_prices', headers=H, timeout=60,
                     params={'q': f'code:{t}~date:gte:2013-01-01~date:lte:2026-06-30', 'sort': 'date', 'size': 5000}).json()['data']
    pd.DataFrame(r).to_csv(f'{OUT}/px_{t}.csv', index=False); print(t, len(r), flush=True); time.sleep(0.3)
out = []
for t in LIVE + EXT:
    for mt in (1, 2, 3):
        try:
            r = requests.get('https://api-finfo.vndirect.com.vn/v4/financial_statements', headers=H, timeout=60,
                             params={'q': f'code:{t}~reportType:QUARTER~modelType:{mt}', 'size': 3000, 'sort': 'fiscalDate:desc'}).json()['data']
        except Exception as e:
            print(t, mt, 'ERR', type(e).__name__, e, flush=True); continue
        for x in r:
            if int(x['itemCode']) in ITEMS:
                out.append(dict(ticker=t, modelType=mt, item=ITEMS[int(x['itemCode'])], fiscalDate=x['fiscalDate'], value=x['numericValue']))
        time.sleep(0.15)
pd.DataFrame(out).to_csv(f'{OUT}/fin_raw_live_ext.csv', index=False)
print('fin rows', len(out), pd.DataFrame(out).groupby('ticker').fiscalDate.nunique().to_dict())
