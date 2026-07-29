# -*- coding: utf-8 -*-
"""VIEC 2b — dinh gia co THEM thong tin so voi thu he thong DA DUNG khong?
Luat sizing CAPIT hien tai da dung: state (DT5G), dd52w, grind, breadth oversold.
Neu phan vi PB chi la bien the cua dd52w thi khong co gi moi (bai hoc Phu luc A.4.1).
"""
import numpy as np, pandas as pd
from scipy import stats
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
pd.set_option('display.width', 250)
E = pd.read_csv(EXP + 'capit_events_gate0.3.csv', parse_dates=['event'])

print('=== 1. Da cong tuyen: phan vi PB vs cac bien HE THONG DA DUNG ===')
for a in ['pb_cap10_pctE', 'pe_cap10_pctE', 'eveb_cap10_pctE']:
    for b in ['dd52', 'ovs']:
        d = E[[a, b]].dropna()
        r, p = stats.spearmanr(d[a], d[b])
        print(f'  {a:20s} ~ {b:6s}: rho={r:+.3f} p={p:.4f} N={len(d)}')

print('\n=== 2. Hoi quy tang dan (OLS, chuan hoa) — R2 co/khong co bien dinh gia ===')
def ols_r2(X, y):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in X])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    yh = X @ b; ss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ((y - yh) ** 2).sum() / ss
    n, k = len(y), X.shape[1]
    return r2, 1 - (1 - r2) * (n - 1) / (n - k)
for o in ['r3M', 'r6M', 'r12M', 'mdd12M']:
    d = E[['dd52', 'ovs', 'pb_cap10_pctE', 'pe_cap10_pctE', o]].dropna()
    if len(d) < 12: continue
    y = d[o].values
    r2a, a_ = ols_r2([d.dd52, d.ovs], y)
    r2b, b_ = ols_r2([d.dd52, d.ovs, d.pb_cap10_pctE], y)
    r2c, c_ = ols_r2([d.dd52, d.ovs, d.pb_cap10_pctE, d.pe_cap10_pctE], y)
    print(f'  {o:7s} N={len(d)}  base(dd52,ovs) R2adj={a_:+.3f} | +PB {b_:+.3f} (dR2={r2b-r2a:+.3f}) | +PB+PE {c_:+.3f}')

print('\n=== 3. Tuong quan RIENG PHAN (partial Spearman, khu dd52 va ovs) ===')
def partial_rank(x, y, ctrl):
    rx = stats.rankdata(x); ry = stats.rankdata(y)
    C = np.column_stack([np.ones(len(x))] + [stats.rankdata(c) for c in ctrl])
    ex = rx - C @ np.linalg.lstsq(C, rx, rcond=None)[0]
    ey = ry - C @ np.linalg.lstsq(C, ry, rcond=None)[0]
    return stats.pearsonr(ex, ey)
for a in ['pb_cap10_pctE', 'pe_cap10_pctE']:
    for o in ['r3M', 'r6M', 'r12M', 'mdd12M']:
        d = E[[a, o, 'dd52', 'ovs']].dropna()
        if len(d) < 12: continue
        r, p = partial_rank(d[a].values, d[o].values, [d.dd52.values, d.ovs.values])
        r0, p0 = stats.spearmanr(d[a], d[o])
        print(f'  {a:16s} ~ {o:7s}: tho rho={r0:+.3f}(p={p0:.3f}) -> rieng phan={r:+.3f}(p={p:.3f}) N={len(d)}')

print('\n=== 4. Chi cua so PRODUCTION (su kien 2014+) ===')
E14 = E[E.event >= '2014-01-01']
print(f'  N su kien 2014+ = {len(E14)}')
for a in ['pb_cap10_pctE', 'pe_cap10_pctE']:
    for o in ['r3M', 'r6M', 'r12M', 'mdd12M']:
        d = E14[[a, o]].dropna()
        if len(d) < 8: continue
        r, p = stats.spearmanr(d[a], d[o])
        print(f'  {a:16s} ~ {o:7s}: rho={r:+.3f} p={p:.3f} N={len(d)}')
