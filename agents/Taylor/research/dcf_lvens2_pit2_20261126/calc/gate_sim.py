# mô phỏng cổng 2023-01..2026-10: cổng CŨ (max_time BCTC >= D-10, dòng tới D+3) vs cổng MỚI sync-v2 + cổng trễ
import sys, re, datetime as dt, numpy as np, pandas as pd, duckdb
from zoneinfo import ZoneInfo
sys.path.insert(0,'calc'); import lvens2_pit2 as L
C='/home/trido/thanhdt/WorkingClaude/data/bq_cache'; c=duckdb.connect(); ICT=ZoneInfo('Asia/Ho_Chi_Minh')
sess=pd.to_datetime(c.execute(f"select distinct cast(time as date) d from read_parquet('{C}/ticker/*.parquet') where ticker='VNINDEX' or ticker='FPT' order by 1").df().d)
fin={t:pd.to_datetime(c.execute(f"select distinct cast(time as date) d from read_parquet('{C}/{t}.parquet') order by 1").df().d) for t in ('ticker_financial','fa_ratings_8l')}
# sync thật từ log
runs=[]; cur=None
for ln in open(f'{C}/sync.log',errors='replace'):
    m=re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s+(.*)',ln)
    if not m: continue
    t=dt.datetime.strptime(m[1],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc).astimezone(ICT); s=m[2]
    if s.startswith('Syncing'): cur={'start':t,'full':set(),'ok':False}; runs.append(cur)
    elif cur is None: continue
    else:
        for tb in ('ticker_financial','fa_ratings_8l'):
            if re.match(rf'{tb}: \d+ rows',s): cur['full'].add(tb)
        if 'Cache verified OK' in s: cur['ok']=True; cur['end']=t
log0=runs[0]['start']
rows=[]
for p in pd.period_range('2023-01','2026-10',freq='M'):
    ym=str(p); D=sess[(sess.dt.strftime('%Y-%m')==ym)].max(); me=L.month_end(ym); T=L.sync_threshold(ym)
    first=me+dt.timedelta(days=1)
    while first.weekday()>=5: first+=dt.timedelta(days=1)
    old=all((f[f<=D+pd.Timedelta(days=3)].max()>=D-pd.Timedelta(days=10)) for f in fin.values())
    run1=dt.datetime(first.year,first.month,first.day,8,5,tzinfo=ICT)
    emp=None
    if T>log0:
        good=[r for r in runs if r['ok'] and r['start']>=T and r.get('end') and r['end']<=run1]
        emp=bool(good)
    rows.append(dict(ym=ym,D=D.date(),month_end=me,first_run=first,days_from_D=(first-D.date()).days,days_from_ME=(first-me).days,old_gate=old,sync_log_pass_first_run=emp))
r=pd.DataFrame(rows); r.to_csv('out/gate_sim_2023_2026.csv',index=False)
print('N tháng',len(r),'| cổng cũ chặn',int((~r.old_gate).sum()))
print('neo D: lượt đầu cách D >5 ngày:',int((r.days_from_D>5).sum()),'| >5 cả mọi lượt, theo tháng:',list(r[r.days_from_D>5].ym))
print('neo cuối tháng: lượt đầu >5:',int((r.days_from_ME>5).sum()),'| max',r.days_from_ME.max())
print('log sync bắt đầu',log0,'| tháng đo được từ log:',int(r.sync_log_pass_first_run.notna().sum()),'pass:',int((r.sync_log_pass_first_run==True).sum()))
print(r[r.sync_log_pass_first_run.notna()][['ym','D','first_run','sync_log_pass_first_run']].to_string(index=False))
