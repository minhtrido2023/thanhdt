import pandas as pd,numpy as np
from google.cloud import bigquery
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/'
pd.set_option('display.width',240)
p=pd.read_csv(EXP+'t100_panel2.csv',parse_dates=['time'])
n=p.groupby('time').size()
print('=== Ngay co n<100 trong "top-100" (thieu du lieu) ===')
bad=n[n<100]; print('N ngay=%d'%len(bad)); print(bad.tail(12).to_string())
print('\n2025-05-01..05-15:'); print(n['2025-05-01':'2025-05-15'].to_string())

c=bigquery.Client(project='lithe-record-440915-m9')
q="""SELECT t.time,t.ticker,t.Price,t.Close,t.OShares,t.BVPS,t.PB,t.PE
FROM `lithe-record-440915-m9.tav2_bq.ticker` t
WHERE t.ticker IN ('VIC','VHM','VCB') AND t.time IN ('2026-07-28','2025-12-31','2024-12-31')
ORDER BY t.ticker,t.time"""
print('\n=== Kiem chung du lieu VIC/VHM/VCB ===')
d=c.query(q).result().to_dataframe()
d['mcap_tyVND']=d.Price*d.OShares/1e9; d['pb_calc']=d.Price/d.BVPS
print(d.round(3).to_string(index=False))
