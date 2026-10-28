"""Đếm tần suất ngành của mã trong discretionary_funnel.log 2026-10-06..23 (mọi làn).
Ngành = route 8L + ICB_Code lấy từ snapshot rating_8l_daily cùng asof."""
import re, sys, collections, pandas as pd
WC = '/home/trido/thanhdt/WorkingClaude'
log = open(f'{WC}/mike/logs/discretionary_funnel.log', encoding='utf-8').read().splitlines()
rows, asof = [], None
for ln in log:
    m = re.match(r'=== Funnel 8L asof (\d{4}-\d{2}-\d{2})', ln)
    if m: asof = m.group(1); continue
    if asof is None or not ('2026-10-06' <= asof <= '2026-10-23'): continue
    m = re.match(r'• ([A-Z0-9]{3}) · làn ([ABC])', ln)
    if m: rows.append((asof, m.group(1), m.group(2), 'listed')); continue
    m = re.match(r'\s*LOẠI ([A-Z0-9]{3}) \(làn ([ABC])', ln)
    if m: rows.append((asof, m.group(1), m.group(2), 'loai'))
df = pd.DataFrame(rows, columns=['asof','ticker','lane','kind'])
snaps = []
for a in df['asof'].unique():
    s = pd.read_csv(f'{WC}/data/rating_8l_daily/rating_8l_{a}.csv', usecols=['ticker','route','ICB_Code']); s['asof']=a; snaps.append(s)
df = df.merge(pd.concat(snaps), on=['asof','ticker'], how='left')
ICB = {8355:'Ngân hàng',8633:'BĐS (phát triển/KCN)',8637:'Dịch vụ BĐS',2357:'Xây dựng hạ tầng',2353:'Vật liệu xây dựng',
       1357:'Hoá chất đặc biệt',1353:'Hoá chất hàng hoá',7535:'Điện',7537:'Điện thay thế',7573:'Gas/khí',7577:'Nước',
       1757:'Thép',1753:'KL màu',1737:'Giấy',2777:'Vận tải/cảng',2773:'Vận tải biển',4577:'Dược',3577:'Thực phẩm',
       8777:'Chứng khoán',8536:'Bảo hiểm phi nhân thọ',8575:'Bảo hiểm nhân thọ',533:'Dầu khí',573:'Thiết bị dầu khí',
       3763:'Dệt may',2727:'Thiết bị điện',5373:'Bán lẻ chuyên',3726:'Đồ gia dụng',1775:'KL quý'}
df['icb_name'] = df.ICB_Code.map(lambda c: ICB.get(int(c), f'ICB {int(c)}') if pd.notna(c) else 'NA')
df.to_csv('funnel_rows_20261006_20261023.csv', index=False)
n_runs = df['asof'].nunique()
print('runs', n_runs, 'rows', len(df), 'unmapped', df.ICB_Code.isna().sum())
uniq = df.drop_duplicates(['ticker'])
g = df.groupby('icb_name').agg(ticker_days=('ticker','size'), uniq=('ticker','nunique'),
     tickers=('ticker', lambda s: ','.join(sorted(set(s))))).sort_values('ticker_days', ascending=False)
print(g.to_string())
print(df.groupby('route').agg(ticker_days=('ticker','size'), uniq=('ticker','nunique')).sort_values('ticker_days',ascending=False).to_string())
print(df.groupby(['icb_name','lane']).size().unstack(fill_value=0).loc[g.index[:10]].to_string())
