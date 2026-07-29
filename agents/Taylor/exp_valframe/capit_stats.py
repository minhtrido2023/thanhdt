# -*- coding: utf-8 -*-
"""VIEC 2 (phan thong ke) — dinh gia luc CAPIT fire co du bao chat luong ket qua khong?
Trung thuc ve co mau: N su kien ~20-26, moi test deu bao N, CI bootstrap, va hieu chinh
da phep thu (Benjamini-Hochberg) tren TOAN BO ho test da chay.
"""
import numpy as np, pandas as pd
from scipy import stats
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'
rng = np.random.default_rng(20260729)
pd.set_option('display.width', 250)

E = pd.read_csv(EXP + 'capit_events_gate0.3.csv', parse_dates=['event'])
MET = ['pb_cap10', 'pb_ewmed', 'pe_cap10', 'pe_ewmed', 'eveb_cap10', 'pb_cw', 'pe_cw']
OUT = ['r3M', 'r6M', 'r12M', 'mdd12M']

def boot_ci(x, f=np.median, B=4000):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 3: return (np.nan, np.nan)
    s = [f(rng.choice(x, len(x), replace=True)) for _ in range(B)]
    return (np.percentile(s, 5), np.percentile(s, 95))

res = []
for m in MET:
    for suf in ['_pctE', '_pct3Y']:
        c = m + suf
        for o in OUT:
            d = E[[c, o]].dropna()
            if len(d) < 8: continue
            rho, p = stats.spearmanr(d[c], d[o])
            res.append(dict(metric=m, pct=suf, outcome=o, N=len(d), rho=round(rho, 3), p=round(p, 4)))
R = pd.DataFrame(res)
# Benjamini-Hochberg tren TOAN BO ho test
R = R.sort_values('p').reset_index(drop=True)
R['bh_thr'] = 0.05 * (R.index + 1) / len(R)
R['pass_BH'] = R.p <= R.bh_thr
R['bonf_thr'] = 0.05 / len(R)
R['pass_bonf'] = R.p <= R.bonf_thr
R.to_csv(EXP + 'capit_stats_spearman.csv', index=False)
print(f'=== SPEARMAN: phan vi dinh gia luc fire  vs  ket qua forward ({len(R)} phep thu) ===')
print(R.head(14).to_string(index=False))
print(f'\nSo test qua BH(0.05): {R.pass_BH.sum()} / {len(R)}   |   qua Bonferroni: {R.pass_bonf.sum()}')

# ---- chia doi theo phan vi dinh gia (median split) ----
print('\n=== CHIA DOI: RE (phan vi thap) vs KHONG-RE (phan vi cao), phan vi NHAN QUA ===')
rows = []
for m in ['pb_cap10', 'pe_cap10', 'eveb_cap10', 'pb_ewmed']:
    c = m + '_pctE'
    for o in OUT:
        d = E[[c, o, 'event']].dropna()
        if len(d) < 10: continue
        thr = d[c].median(); lo = d[d[c] <= thr][o].values; hi = d[d[c] > thr][o].values
        obs = np.median(lo) - np.median(hi)
        pool = np.concatenate([lo, hi]); nlo = len(lo)
        perm = []
        for _ in range(20000):
            q = rng.permutation(pool); perm.append(np.median(q[:nlo]) - np.median(q[nlo:]))
        pv = (np.abs(perm) >= abs(obs)).mean()
        rows.append(dict(metric=m, outcome=o, N=len(d), n_re=nlo, n_dat=len(hi),
                         med_re=round(np.median(lo), 1), med_dat=round(np.median(hi), 1),
                         delta=round(obs, 1), p_perm=round(pv, 4)))
S = pd.DataFrame(rows); S.to_csv(EXP + 'capit_stats_split.csv', index=False)
print(S.to_string(index=False))
S2 = S.sort_values('p_perm').reset_index(drop=True)
S2['bh_thr'] = 0.05 * (S2.index + 1) / len(S2)
print(f"\nqua BH(0.05) trong ho chia-doi: {(S2.p_perm <= S2.bh_thr).sum()} / {len(S2)}")

# ---- bang mo ta: 3 nhom theo terciles phan vi PB ----
print('\n=== TERCILE theo pb_cap10_pctE ===')
d = E.dropna(subset=['pb_cap10_pctE']).copy()
d['g'] = pd.qcut(d.pb_cap10_pctE, 3, labels=['RE nhat', 'giua', 'DAT nhat'])
print(d.groupby('g', observed=True).agg(N=('event', 'size'), pctE=('pb_cap10_pctE', 'median'),
      r3M=('r3M', 'median'), r6M=('r6M', 'median'), r12M=('r12M', 'median'),
      mdd12M=('mdd12M', 'median')).round(1).to_string())
for g_ in ['RE nhat', 'DAT nhat']:
    x = d[d.g == g_]['r12M'].dropna()
    print(f'  {g_}: r12M trung vi {np.median(x):+.1f}%  CI90 bootstrap {boot_ci(x)[0]:+.1f}..{boot_ci(x)[1]:+.1f}  (N={len(x)})')
