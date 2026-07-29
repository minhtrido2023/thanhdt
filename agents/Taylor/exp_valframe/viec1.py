# -*- coding: utf-8 -*-
"""VIEC 1 — bo chi so dinh gia chuan nganh cho VN: CAPE, ERP, EV/EBITDA, composite.
Moi chi so: gia tri hien tai + phan vi (cap-weighted THO va ban BEN voi outlier),
+ kiem tra DA CONG TUYEN voi PE/PB (bai hoc Phu luc A.4.1).
"""
import sys, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from cpi_vn import cpi_monthly_df
from deposit_rate_vn import DEPOSIT_EVENTS
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width', 250)

M = pd.read_csv(EXP + 'metrics_daily.csv', parse_dates=['time'])
vni = pd.read_parquet(EXP + 'vni.parquet'); vni['time'] = pd.to_datetime(vni.time)
M = M.merge(vni[['time', 'Close']].rename(columns={'Close': 'vni'}), on='time', how='left')

# ---------- 1. CHI SO GIA TIEU DUNG (de khu lam phat cho CAPE) ----------
# 2011+ : cpi_vn.py (Tier1 NSO that 2025-06+, Tier2 proxy noi suy truoc do)
# 2007-2010: bo sung anchors BINH QUAN NAM tu nguon cong khai (WB/GSO), xac minh
# bang WebSearch 2026-07-29: 2007 8.36 / 2008 22.98 / 2009 6.70 / 2010 9.23.
c = cpi_monthly_df(end='2026-07-01')
ann = c.assign(y=c.time.dt.year).groupby('y').cpi_yoy.mean()
ann = pd.concat([pd.Series({2007: 8.36, 2008: 22.98, 2009: 6.70, 2010: 9.23}), ann]).sort_index()
lvl = {2006: 100.0}
for y in range(2007, 2027):
    lvl[y] = lvl[y - 1] * (1 + ann.get(y, ann.iloc[-1]) / 100)
cpi_y = pd.Series(lvl).sort_index()
cpi_daily = pd.Series(np.interp(M.time.map(lambda t: t.year + (t.dayofyear - 1) / 365.25),
                                cpi_y.index.values + 0.5, cpi_y.values), index=M.index)
M['cpi'] = cpi_daily
print('CPI index (2006=100):', {int(k): round(v, 1) for k, v in list(cpi_y.items())[::4]})

# ---------- 2. CAPE ----------
for pecol, tag in (('pe_cap10', ''), ('pe_cw', '_cw')):
    M['E' + tag] = M['vni'] / M[pecol]                    # loi nhuan tren 1 don vi chi so
    M['Ereal' + tag] = M['E' + tag] / M['cpi']            # khu lam phat (ve mat bang gia 2006)
for N in (5, 7, 10):
    w = int(N * 250)
    for tag in ('', '_cw'):
        avg = M['Ereal' + tag].rolling(w, min_periods=int(w * 0.9)).mean()
        M[f'cape{N}{tag}'] = M['vni'] / (avg * M['cpi'])

# ---------- 3. ERP (earnings yield - lai suat huy dong Big4-12M) ----------
dep = pd.DataFrame(DEPOSIT_EVENTS, columns=['time', 'dep']); dep['time'] = pd.to_datetime(dep.time)
extra = pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv',
                    usecols=['effective_date', 'deposit_rate']).rename(
                    columns={'effective_date': 'time', 'deposit_rate': 'dep'})
extra['time'] = pd.to_datetime(extra.time)
dep = pd.concat([dep, extra[extra.time > dep.time.max()]]).drop_duplicates('time').sort_values('time')
M = pd.merge_asof(M.sort_values('time'), dep, on='time', direction='backward')
M['ey'] = 100.0 / M.pe_cap10
M['ey_cw'] = 100.0 / M.pe_cw
M['erp'] = M.ey - M.dep
M['erp_cw'] = M.ey_cw - M.dep
M.to_csv(EXP + 'metrics_full.csv', index=False)

# ---------- 4. bang phan vi ----------
COLS = ['pe_cap10', 'pe_cw', 'pb_cap10', 'pb_cw', 'pb_ewmed', 'eveb_cap10', 'eveb_cw', 'eveb_ewmed',
        'cape5', 'cape7', 'cape10', 'cape5_cw', 'ey', 'erp', 'erp_cw']
cur = M.iloc[-1]; end = cur.time
wins = {'full': M.time >= '2007-01-01', '10Y': M.time >= end - pd.DateOffset(years=10),
        '5Y': M.time >= end - pd.DateOffset(years=5), '3Y': M.time >= end - pd.DateOffset(years=3)}
out = []
for wn, msk in wins.items():
    for cc in COLS:
        s = M.loc[msk, cc].dropna()
        if len(s) < 100: continue
        out.append(dict(window=wn, metric=cc, N=len(s), cur=round(cur[cc], 3),
                        pctile=round(100 * (s < cur[cc]).mean(), 1),
                        p05=round(s.quantile(.05), 2), p50=round(s.quantile(.5), 2), p95=round(s.quantile(.95), 2),
                        first=str(M.loc[msk & M[cc].notna(), 'time'].min().date())))
P = pd.DataFrame(out); P.to_csv(EXP + 'viec1_percentiles.csv', index=False)
print('\n=== HIEN TAI (%s) + PHAN VI ===' % end.date())
pv = P.pivot(index='metric', columns='window', values='pctile').reindex(COLS)[['full', '10Y', '5Y', '3Y']]
pv['cur'] = P.drop_duplicates('metric').set_index('metric').cur.reindex(COLS)
pv['bat_dau'] = P[P.window == 'full'].set_index('metric').first.reindex(COLS)
print(pv.to_string())

# ---------- 5. DA CONG TUYEN voi PE/PB (bai hoc Phu luc A.4.1) ----------
print('\n=== DA CONG TUYEN: hoi quy log-log chi so MOI ~ log(PE) + log(PB) ===')
def r2(y, Xs):
    X = np.column_stack([np.ones(len(y))] + Xs)
    b, *_ = np.linalg.lstsq(X, y, rcond=None); yh = X @ b
    return 1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()
base = M[['pe_cap10', 'pb_cap10']].apply(np.log)
for cc in ['cape5', 'cape7', 'cape10', 'eveb_cap10', 'erp']:
    d = M[[cc, 'pe_cap10', 'pb_cap10']].dropna()
    y = np.log(d[cc].values) if d[cc].min() > 0 else d[cc].values
    Rpe = r2(y, [np.log(d.pe_cap10.values)])
    Rpb = r2(y, [np.log(d.pb_cap10.values)])
    Rb = r2(y, [np.log(d.pe_cap10.values), np.log(d.pb_cap10.values)])
    print(f'  {cc:11s} N={len(d):5d}  R2|PE={Rpe:.3f}  R2|PB={Rpb:.3f}  R2|PE+PB={Rb:.3f}'
          f'   -> thong tin MOI = {1-Rb:.1%} phuong sai')
