"""FETCH — du lieu tang VI THE cho cau hoi "vay margin + Kelly trong pha washout CAPIT".

Tai lap DUNG luat production (khong dinh nghia lai):
  - su kien washout : pt_v23_audit_2014.py:1133-1140  (ticker_prune, D_RSI<0.3, gate 0.30, cum cach >=30 ngay lich)
  - ro CAPIT        : pt_v23_audit_2014.py:1180-1210  (capit_basket: ROE_Min5Y>=.12 ROIC5Y>=.10 FSCORE>=6
                      thanh khoan >=2 ty; pbz<-1 (>=3 ten) else pbz<0 else all; top-15 pbz nho nhat)
  - hold            : CAPIT_HOLD = 60 phien
Gia dung cho RETURN = Close (da dieu chinh co tuc/chia tach) — dung quy tac §9 skill quant-research:
gia tri phuc vu tinh SUAT SINH LOI phai dung gia da dieu chinh; `Price` (tho PIT) chi dung cho
SELECTION/thanh khoan (o day dung dung nhu production trong dieu kien loc >=2 ty).

Output: exp_margin_kelly/{events.csv, basket.csv, px.parquet, state.csv, vni.csv}
"""
import os
import numpy as np
import pandas as pd
from google.cloud import bigquery

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
VALF = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
c = bigquery.Client(project='lithe-record-440915-m9')
GATE, MINN, HOLD = 0.30, 100, 60


def q(sql):
    return c.query(sql).to_dataframe()


# ---------------------------------------------------------------- 1. su kien washout
br = pd.read_parquet(VALF + 'breadth_prune.parquet').sort_values('time').reset_index(drop=True)
br['time'] = pd.to_datetime(br['time'])
br = br[br.n >= MINN].reset_index(drop=True)
ws = br[br.oversold >= GATE].copy()
ws['g'] = ws.time.diff().dt.days.fillna(999)
ws['c'] = (ws.g >= 30).cumsum()
ev = ws.groupby('c').first().reset_index()[['time', 'oversold']].rename(columns={'oversold': 'ovs'})
print(f'breadth {br.time.min().date()} -> {br.time.max().date()} | washout events N={len(ev)}')

# self-check: phai trung DUNG danh sach su kien cua exp_valframe (bao cao 2026-07-29, 26 su kien)
ref = pd.read_csv(VALF + 'capit_events_gate0.3.csv', parse_dates=['event'])
same = list(ev.time.dt.date) == list(ref.event.dt.date)
print(f'  SELF-CHECK tai lap su kien vs capit_events_gate0.3.csv: {"MATCH" if same else "MISMATCH"} '
      f'({len(ev)} vs {len(ref)})')
assert same, 'khong tai lap duoc danh sach su kien -> dung lai'

# ---------------------------------------------------------------- 2. ro CAPIT tai tung su kien
rows = []
for _, e in ev.iterrows():
    d = e.time.date()
    df = q(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    if df.empty:
        print(f'  {d}: pool rong')
        continue
    g = df[df.pbz < -1]
    cc = df[df.pbz < 0]
    pick = g if len(g) >= 3 else (cc if len(cc) >= 3 else df)
    pick = pick.nsmallest(15, 'pbz') if len(pick) > 15 else pick
    for _, r in pick.iterrows():
        rows.append({'event': e.time, 'ticker': r.ticker, 'pbz': r.pbz})
    print(f'  {d}: pool={len(df)} -> ro={len(pick)} ({",".join(sorted(pick.ticker))})')
bk = pd.DataFrame(rows)
bk.to_csv(EXP + 'basket.csv', index=False)
ev.to_csv(EXP + 'events.csv', index=False)

# ---------------------------------------------------------------- 3. bang gia cho moi ten trong ro
names = sorted(bk.ticker.unique())
inl = ','.join(f"'{t}'" for t in names)
px = q(f"""SELECT t.time, t.ticker, t.Close, COALESCE(t.Price,t.Close) px_raw
FROM tav2_bq.ticker t WHERE t.ticker IN ({inl}) AND t.time >= DATE '2008-01-01'
ORDER BY t.time, t.ticker""")
px['time'] = pd.to_datetime(px['time'])
px.to_parquet(EXP + 'px.parquet', index=False)
print(f'px: {len(px):,} dong / {px.ticker.nunique()} ten')

# ---------------------------------------------------------------- 4. DT5G (production) + VNINDEX
st = q("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s ORDER BY s.time""")
st['time'] = pd.to_datetime(st['time'])
st.to_csv(EXP + 'state.csv', index=False)
print(f'DT5G: {st.time.min().date()} -> {st.time.max().date()} N={len(st)}')

vni = q("""SELECT t.time, t.Close, t.VNINDEX_PE FROM tav2_bq.ticker t
WHERE t.ticker='VNINDEX' AND t.time>='2005-01-01' ORDER BY t.time""")
vni['time'] = pd.to_datetime(vni['time'])
vni.to_csv(EXP + 'vni.csv', index=False)
print(f'VNINDEX: {vni.time.min().date()} -> {vni.time.max().date()} '
      f'(PE co tu {vni.dropna(subset=["VNINDEX_PE"]).time.min().date()})')
print('DONE')
