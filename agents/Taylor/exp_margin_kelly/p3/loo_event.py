"""LEAVE-ONE-EVENT-OUT tren ho park:0.25 — dong lo hong quant-skeptic neu ra (LOO theo NAM
khong loai duoc kha nang 1 dot washout ganh het edge OOS). job Taylor_20260803_082141."""
import warnings; warnings.filterwarnings('ignore')
import sys, glob, math
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav

DATA = '/home/trido/thanhdt/WorkingClaude/data/'
EV = {2: '2015-08-24 (IS)', 3: '2016-01-18 (IS)', 5: '2018-07-05 (IS)',
      6: '2020-02-03 (OOS)', 8: '2020-07-27 (OOS)', 16: '2025-10-20 (OOS)',
      17: '2026-03-09 (OOS)'}


def m(s, a=None, b=None):
    if a: s = s[(s.index >= a) & (s.index <= b)]
    y = (s.index[-1] - s.index[0]).days / 365.25
    return 100 * ((s.iloc[-1] / s.iloc[0]) ** (1 / y) - 1)


def mdd(s):
    return 100 * (s / s.cummax() - 1).min()


def get(tag):
    g = glob.glob(DATA + f'*exp_{tag}_univpit*.csv')
    return load_nav(g[0]) if g else None


ctl, full = get('p3_P0_control'), get('p3_LOOnone')
pk025 = get('p3_PK025')
print('REGRESSION: p3_LOOnone (park:0.25, CAPIT_PARK_LOO rong) vs p3_PK025 (truoc khi them knob LOO)')
print(f'  LOOnone CAGR {m(full):.4f}%  |  PK025 CAGR {m(pk025):.4f}%  '
      f'=> {"IDENTICAL" if abs(m(full)-m(pk025)) < 1e-9 else "KHAC — knob LOO da lam doi ket qua!"}')
d_full = m(full) - m(ctl)
d_oos_full = m(full, '2020-01-01', '2026-12-31') - m(ctl, '2020-01-01', '2026-12-31')
print(f'\nChan day du park:0.25: dCAGR {d_full:+.2f}pp, dOOS {d_oos_full:+.2f}pp, MaxDD {mdd(full):.2f}%')
print('\n' + '=' * 118)
print('Bo TUNG su kien khoi boost parking (van giu co so `cash` cho su kien do):')
print('=' * 118)
print(f'{"bo su kien":<24}{"CAGR":>9}{"dCAGR vs ctl":>15}{"con lai % edge":>17}'
      f'{"dOOS vs ctl":>14}{"con lai % OOS":>16}{"MaxDD":>9}')
rows = []
for e, lbl in EV.items():
    s = get(f'p3_LOOe{e}')
    if s is None:
        print(f'  (thieu CSV cho E{e})'); continue
    d = m(s) - m(ctl)
    do = m(s, '2020-01-01', '2026-12-31') - m(ctl, '2020-01-01', '2026-12-31')
    rows.append((e, lbl, d, do))
    print(f'E{e} {lbl:<20}{m(s):8.2f}%{d:+14.2f}pp{100*d/d_full:16.0f}%{do:+13.2f}pp'
          f'{100*do/d_oos_full:15.0f}%{mdd(s):8.2f}%')
if rows:
    worst = min(rows, key=lambda r: r[2])
    worst_o = min(rows, key=lambda r: r[3])
    print(f'\nSu kien ganh nhieu nhat (FULL): E{worst[0]} {worst[1]} — bo di con '
          f'{100*worst[2]/d_full:.0f}% edge ({worst[2]:+.2f}pp / {d_full:+.2f}pp)')
    print(f'Su kien ganh nhieu nhat (OOS):  E{worst_o[0]} {worst_o[1]} — bo di con '
          f'{100*worst_o[3]/d_oos_full:.0f}% edge OOS ({worst_o[3]:+.2f}pp / {d_oos_full:+.2f}pp)')
    print(f'So su kien mà bo di lam edge doi DAU (am): '
          f'{sum(1 for r in rows if r[2] < 0)}/{len(rows)} (FULL), '
          f'{sum(1 for r in rows if r[3] < 0)}/{len(rows)} (OOS)')
print('DONE')
