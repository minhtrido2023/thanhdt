#!/usr/bin/env python
"""Robustness + lich HYBRID. Doc per_day_exp.csv sinh boi twap_vs_window.py."""
import math
import pandas as pd, numpy as np

CORE = ['09:15','09:30','09:45','10:00','10:15','10:30','10:45','11:00','11:15',
        '13:00','13:15','13:30','13:45','14:00','14:15','14:30']
D = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_twap_20260804/per_day_exp.csv'


def bps(x, b): return (x / b - 1.0) * 1e4


def daily_series(df, cols):
    """gia tb cua 1 lich (equal-weight cac block trong cols) -> chuoi theo PHIEN."""
    px = df[['px_' + c for c in cols]].mean(axis=1)
    e = bps(px, df.vwap)
    return pd.DataFrame({'day': df.day, 'e': e}).dropna().groupby('day').e.mean()


def stat(s):
    m, sd, n = s.mean(), s.std(ddof=1), len(s)
    return m, m / (sd / math.sqrt(n)), sd, n


def main():
    df = pd.read_csv(D)
    df['year'] = pd.to_datetime(df.day).dt.year

    SCHED = {
        'TWAP16 (trai deu ca ngay)': CORE,
        'BUY gom @11:15':            ['11:15'],
        'SELL gom @09:15':           ['09:15'],
        'HYBRID BUY 11:00-13:30 (5 block)':  ['11:00','11:15','13:00','13:15','13:30'],
        'HYBRID BUY chieu 13:00-13:45 (4)':  ['13:00','13:15','13:30','13:45'],
        'HYBRID SELL 09:15-10:00 (4 block)': ['09:15','09:30','09:45','10:00'],
    }

    print('## A. Toan mau (2023-09 -> 2026-05) — sai lech vs day-VWAP, bps')
    print(f'{"lich":>34} {"mean":>7} {"t":>7} {"sd":>6} {"MAD":>6} {"IR":>6}')
    base = {}
    for name, cols in SCHED.items():
        s = daily_series(df, cols); base[name] = s
        m, t, sd, n = stat(s)
        print(f'{name:>34} {m:7.2f} {t:7.2f} {sd:6.1f} {s.abs().mean():6.1f} {m/sd:6.3f}')

    print('\n## B. On dinh theo NAM (leave-one-year-out style, mean bps vs VWAP)')
    yrs = sorted(df.year.unique())
    print(f'{"lich":>34} ' + ' '.join(f'{y:>8}' for y in yrs))
    for name, cols in SCHED.items():
        out = []
        for y in yrs:
            s = daily_series(df[df.year == y], cols)
            out.append(f'{s.mean():8.2f}')
        print(f'{name:>34} ' + ' '.join(out))
    print(f'{"(so phien moi nam)":>34} ' +
          ' '.join(f'{df[df.year==y].day.nunique():8d}' for y in yrs))

    print('\n## C. On dinh theo MA (BUY@11:15 vs TWAP; so ma co dau co loi)')
    win, lose = 0, 0
    for t_, g in df.groupby('ticker'):
        if g.day.nunique() < 60: continue
        a = daily_series(g, ['11:15']); b = daily_series(g, CORE)
        d = (a - b).mean()
        win += d < 0; lose += d >= 0
    print(f'  BUY@11:15 re hon TWAP o {win}/{win+lose} ma')
    win, lose = 0, 0
    for t_, g in df.groupby('ticker'):
        if g.day.nunique() < 60: continue
        a = daily_series(g, ['09:15']); b = daily_series(g, CORE)
        d = (a - b).mean()
        win += d > 0; lose += d <= 0
    print(f'  SELL@09:15 cao hon TWAP o {win}/{win+lose} ma')

    print('\n## D. Vong khu hoi (BUY + SELL) — loi/hai so voi TWAP thuan, bps')
    tw = base['TWAP16 (trai deu ca ngay)']
    for bname, sname, label in [
        ('BUY gom @11:15', 'SELL gom @09:15', 'gom-cua-so hien tai'),
        ('HYBRID BUY 11:00-13:30 (5 block)', 'HYBRID SELL 09:15-10:00 (4 block)', 'HYBRID'),
    ]:
        b = base[bname].reindex(tw.index); s = base[sname].reindex(tw.index)
        rt = ((tw - b) + (s - tw)).dropna()      # mua re hon + ban cao hon
        m, t, sd, n = stat(rt)
        print(f'  {label:>22}: {m:+.2f} bps/vong  t={t:+.2f}  sd={sd:.1f}  N_phien={n}')
    # rui ro: sd cua tung chan
    print('\n  sd tung chan (bps):')
    for k in base: print(f'    {k:>34}: {base[k].std(ddof=1):6.1f}')


if __name__ == '__main__':
    main()
