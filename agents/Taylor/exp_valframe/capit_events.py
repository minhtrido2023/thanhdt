# -*- coding: utf-8 -*-
"""VIEC 2 — Dinh gia luc CAPIT fire co tuong quan voi chat luong ket qua khong?

Su kien CAPIT tai lap DUNG luat production (pt_v23_audit_2014.py:1079-1086):
  fire_day = >=WASHOUT_GATE ty le ticker_prune co D_RSI<0.3
  su kien  = ngay DAU TIEN cua cum, cac cum cach nhau >=30 ngay lich

Dinh gia tai ngay fire do bang PHAN VI NHAN QUA (expanding: chi so sanh voi lich su
TRUOC do, khong nhin tuong lai) — theo dung 3 bai hoc (khong dung cap-weighted tho lam
thuoc do chinh; bao song song ban ben voi outlier).
"""
import numpy as np, pandas as pd
from scipy import stats
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
GATE = float(__import__('os').environ.get('GATE', '0.30'))
MINN = 100          # so ma toi thieu trong ticker_prune de breadth co nghia (CLAUDE.md: 2008+)

br = pd.read_parquet(EXP + 'breadth_prune.parquet').sort_values('time').reset_index(drop=True)
br['time'] = pd.to_datetime(br['time'])
br = br[br.n >= MINN].reset_index(drop=True)
print(f'breadth: {len(br)} phien {br.time.min().date()} -> {br.time.max().date()} (n>={MINN})')

vni = pd.read_parquet(EXP + 'vni.parquet').sort_values('time').reset_index(drop=True)
vni['time'] = pd.to_datetime(vni['time'])
vni = vni.dropna(subset=['Close']).reset_index(drop=True)
vni['dd52'] = 100 * (vni.Close / vni.Close.rolling(252, min_periods=60).max() - 1)
vni['ma200'] = vni.Close.rolling(200, min_periods=100).mean()

M = pd.read_csv(EXP + 'metrics_daily.csv', parse_dates=['time'])
VAL = ['pb_cap10', 'pb_ewmed', 'pb_cw', 'pe_cap10', 'pe_ewmed', 'pe_cw', 'eveb_cap10', 'eveb_ewmed']

# ---- phan vi NHAN QUA (expanding, burn-in 3 nam) + phan vi truot 3 nam ----
for c in VAL:
    s = M[c]
    M[c + '_pctE'] = [np.nan if i < 750 or not np.isfinite(s.iloc[i])
                      else 100.0 * (s.iloc[:i + 1].dropna() < s.iloc[i]).mean() for i in range(len(s))]
    r = s.rolling(750, min_periods=500)
    M[c + '_pct3Y'] = 100.0 * r.apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)

# ---- su kien CAPIT ----
ws = br[br.oversold >= GATE].copy()
ws['g'] = ws.time.diff().dt.days.fillna(999)
ws['c'] = (ws.g >= 30).cumsum()
ev = ws.groupby('c').first().reset_index()[['time', 'oversold']].rename(columns={'oversold': 'ovs'})
print(f'\nGATE={GATE}: {len(ws)} phien washout -> {len(ev)} su kien CAPIT')

# ---- forward outcome tren VNINDEX ----
vd = vni.time.values; vc = vni.Close.values
def fwd(t):
    i = np.searchsorted(vd, np.datetime64(t))
    if i >= len(vd): return {}
    o = {'vni': vc[i]}
    for lbl, h in (('1M', 21), ('3M', 63), ('6M', 126), ('12M', 252)):
        j = i + h
        o['r' + lbl] = 100 * (vc[j] / vc[i] - 1) if j < len(vc) else np.nan
    for lbl, h in (('3M', 63), ('12M', 252)):
        seg = vc[i:min(i + h + 1, len(vc))]
        o['mdd' + lbl] = 100 * (seg.min() / vc[i] - 1) if len(seg) > 5 else np.nan
        o['mup' + lbl] = 100 * (seg.max() / vc[i] - 1) if len(seg) > 5 else np.nan
    o['dd52'] = vni.dd52.values[i]
    o['below_ma200'] = bool(vc[i] < vni.ma200.values[i]) if np.isfinite(vni.ma200.values[i]) else None
    return o

rows = []
for _, e in ev.iterrows():
    t = e.time
    r = {'event': t.date(), 'ovs': round(100 * e.ovs, 1)}
    r.update(fwd(t))
    mm = M[M.time <= t]
    if len(mm):
        last = mm.iloc[-1]
        r['val_asof'] = last.time.date()
        for c in VAL:
            r[c] = last[c]; r[c + '_pctE'] = last[c + '_pctE']; r[c + '_pct3Y'] = last[c + '_pct3Y']
    rows.append(r)
E = pd.DataFrame(rows)
E.to_csv(EXP + f'capit_events_gate{GATE}.csv', index=False)

pd.set_option('display.width', 250)
cols = ['event', 'ovs', 'dd52', 'pb_cap10', 'pb_cap10_pctE', 'pe_cap10', 'pe_cap10_pctE',
        'eveb_cap10', 'eveb_cap10_pctE', 'r3M', 'r6M', 'r12M', 'mdd3M', 'mdd12M']
print('\n=== BANG SU KIEN CAPIT (dinh gia nhan qua + ket qua forward) ===')
print(E[cols].round(1).to_string(index=False))
