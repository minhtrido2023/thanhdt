"""Nạp dữ liệu dùng chung cho B2-B4. Nguồn: te_daily.parquet (TE daily, source tường minh), data/bq_cache/ticker (Close điều chỉnh),
data/bq_cache/universe_pit (PIT universe), data/bq_cache/ticker_financial.parquet (Release_Date = ngày công bố PIT)."""
import pandas as pd, numpy as np, glob, os
W='/home/trido/thanhdt/WorkingClaude'; O=os.path.dirname(os.path.abspath(__file__))
def te():
    d=pd.read_parquet(f'{O}/te_daily.parquet'); return d.pivot(index='observation_date',columns='metric_key',values='value').sort_index()
def cmap(tiers=('A','B')):
    m=pd.read_csv(f'{O}/commodity_map_te.csv'); return m[m.tier.isin(tiers)&(m.ticker!='-')]
_px=None
def px():
    global _px
    if _px is None:
        t=pd.concat([pd.read_parquet(f,columns=['ticker','time','Close']) for f in sorted(glob.glob(f'{W}/data/bq_cache/ticker/*.parquet'))])
        t['time']=pd.to_datetime(t.time); _px=t.pivot_table(index='time',columns='ticker',values='Close').sort_index()
    return _px
def univ():
    u=pd.concat([pd.read_parquet(f,columns=['ticker','time','in_universe']) for f in sorted(glob.glob(f'{W}/data/bq_cache/universe_pit/*.parquet'))])
    u['time']=pd.to_datetime(u.time); return u[u.in_universe==True].pivot_table(index='time',columns='ticker',values='in_universe',aggfunc='first').notna().sort_index()
def fin():
    f=pd.read_parquet(f'{W}/data/bq_cache/ticker_financial.parquet',columns=['ticker','quarter','Release_Date','Revenue_P0','Revenue_P1','Revenue_P4','NP_P0','NP_P1','NP_P4','GPM_P0','GPM_P1','GPM_P4','PE','PCF'])
    f['Release_Date']=pd.to_datetime(f.Release_Date)
    f=f.sort_values('Release_Date').drop_duplicates(['ticker','quarter'],keep='first')  # bản công bố ĐẦU TIÊN (chống restate)
    q=pd.PeriodIndex(f.quarter.str.replace('Q','Q'),freq='Q'); f['qend']=q.end_time.normalize()
    return f
def bench(px,u):
    r=px.pct_change(fill_method=None).where(u.reindex(px.index).fillna(False).shift(1).fillna(False))
    return r.mean(axis=1).fillna(0)   # EW universe_pit, thành viên tại t-1
