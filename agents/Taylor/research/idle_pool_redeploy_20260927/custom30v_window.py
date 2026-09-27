#!/usr/bin/env python3
"""custom30V PIT-weighted return over the AlphaLens window (2026-07-01..2026-09-25).
Membership/weights from data/bq_cache/custom30v_8l.parquet (real quarterly rebals, PIT — no
look-ahead: 07-01..08-04 uses the 2026-05-05 rebal, 08-05.. uses the 2026-08-05 rebal).
NOTE: effective_to is EXCLUSIVE and the windows leave 2026-08-04 uncovered; carry-forward of the
last rebal is required or that day is silently dropped (dropping it gives -8.03% instead of -7.42%).
"""
import pandas as pd
WC="/home/trido/thanhdt/WorkingClaude"
c=pd.read_parquet(f'{WC}/data/bq_cache/custom30v_8l.parquet')
c['effective_from']=pd.to_datetime(c['effective_from'],errors='coerce')
px=pd.read_parquet(f'{WC}/data/bq_cache/ticker/2026.parquet',columns=['time','ticker','Close'])
px['time']=pd.to_datetime(px['time'])
R=px.pivot_table(index='time',columns='ticker',values='Close',aggfunc='last').sort_index().pct_change()
days=[d for d in R.index if pd.Timestamp('2026-07-01')<=d<=pd.Timestamp('2026-09-25')]
rebs=sorted(c['effective_from'].dropna().unique())
nav=1.0
for d in days:
    m=c[c['effective_from']==[x for x in rebs if x<=d][-1]]
    w=m.set_index('ticker')['weight']; tk=[t for t in w.index if t in R.columns]
    nav*=1+float((R.loc[d,tk].fillna(0)*w[tk]).sum()/w[tk].sum())
print(f"custom30V PIT-weighted {days[0].date()}..{days[-1].date()} ({len(days)} days) = {(nav-1)*100:+.2f}%")
