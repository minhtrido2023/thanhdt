"""5F addendum HPG VONG SUA r2 (job Taylor_20261107_131620). Chay: $DNA_PYEXE -I hpg_5f_r2.py > hpg_5f_r2_out.txt
Mo hinh RI + luoi 675 ket cuc CHEP NGUYEN hpg_5f.py (r1, = hpg_r2.py). Khac r1:
 (1) NEO TB chu ky nganh dung lai tu ROE NAM QUAN SAT (ROE_Trailing dong Q4, 2016-2025, peer_roe_q4_2016_2025.csv),
     KHONG dung truong vendor ROE10Y. GDA (chi 3 nam 2023-25) LOAI khoi neo chinh, chi bao bien the.
 (2) Truc NEO terminal (REV, RONIC=Ke) -> nhan theo neo.
 (3) Bien the KHONG PHAT DQ2: REVF = chenh (neo - Ke) san 0 (moi von terminal sinh loi >= Ke);
     REVD = chi von ngoai XDCB do dang (16.113 ty, HN-Q3) chiu chenh (neo - Ke), XDCB = Ke.
 Che do REV: ROE_T = NEO (ROE sau thue THUC cua peer), KHONG nhan TAXF (thue 20%) - khac CUR/SYM."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '_common_014125'))
import common as C, r2common as R2C
import numpy as np

SH = 8442.96452; BV0 = 148795.5; PAYOUT = 0.20; TAXF = 0.80 / 0.88; CWIP = 16113.0
SC = {'XAU': dict(w=0.25, e=[5500, 16000, 15000, 16000], g=0.03),
      'TRUNG_LAP': dict(w=0.50, e=[7000, 26000, 26000, 27000], g=0.05),
      'TOT': dict(w=0.25, e=[8000, 31000, 33000, 35000], g=0.05)}
TLSH = 9915.0
TLSH_AX = ((-0.25, 0.10), (0.0, 0.50), (0.25, 0.20), (0.50, 0.12), (1.00, 0.08))
SLOPE = (-0.05, 0.0, 0.05); MULT = (0.80, 0.90, 1.00, 1.10, 1.20); DG = (-0.01, 0.0, 0.01)
NFADE = 5
ROE = {}
for row in csv.DictReader(open(os.path.join(HERE, 'peer_roe_q4_2016_2025.csv'))):
    ROE.setdefault(row['ticker'], {})[row['quarter']] = float(row['roe'])
PEERS = ['HSG', 'NKG', 'VGS', 'SMC', 'TLH', 'TVN']
pm = {k: float(np.mean(list(ROE[k].values()))) for k in PEERS + ['GDA']}
pmed = {k: float(np.median(list(ROE[k].values()))) for k in PEERS}
A_MED = float(np.median([pm[k] for k in PEERS])); A_MEAN = float(np.mean([pm[k] for k in PEERS]))
A_MEDMED = float(np.median([pmed[k] for k in PEERS]))
A_MEAN_GDA = float(np.mean([pm[k] for k in PEERS + ['GDA']]))
hp = ROE['HPG']; HPG_MEAN10 = float(np.mean(list(hp.values())))
HPG_2225 = float(np.mean([hp[q] for q in ('2022Q4', '2023Q4', '2024Q4', '2025Q4')]))
HPG_ROE5Y_TAX = 0.169 * TAXF
L = R2C.liq2('HPG'); PX, PXD = 21700.0, '2026-11-04'
A = C.anchor_info(); R = A['r']
ROLL = (np.datetime64(PXD) - np.datetime64('2026-09-30')).astype(int) / 365


def ri(e, ke, g, mult=1.0, dg=0.0, mode='CUR', anc=None):
    bv = BV0; pv = 0.0; t = 0.0; e = [x * mult for x in e]
    for i, ni in enumerate(e):
        dt = 0.25 if i == 0 else 1.0; t += dt
        pv += (ni - ke * dt * bv) / (1 + ke) ** t; bv += ni * (1 - PAYOUT)
    gg = g + dg; roeT = e[-1] * (1 + gg) * TAXF / bv
    d = (1 + ke) ** t
    if mode == 'CUR':
        g_ri = 0.0 if roeT < ke else gg; tv = (roeT - ke) * bv / (ke - g_ri) / d
    elif mode == 'SYM':
        tv = (roeT - ke) * bv / ke / d
    elif mode == 'NONE':
        tv = sum((roeT - ke) * bv * max(0.0, 1 - (k - 1) / NFADE) / (1 + ke) ** (t + k) for k in range(1, NFADE + 1))
    elif mode == 'REV':
        roeT = anc; tv = (roeT - ke) * bv / ke / d
    elif mode == 'REVF':
        roeT = anc; tv = max(roeT - ke, 0.0) * bv / ke / d
    elif mode == 'REVD':
        roeT = anc; tv = (roeT - ke) * (bv - CWIP) / ke / d
    return (BV0 + pv + tv) / SH * 1e3 * (1 + ke) ** ROLL, roeT


def fv(r, scen, mult, dg, slope, tlsh, mode, anc):
    s = SC[scen]; e = list(s['e']); e[2] *= 1 + slope; e[3] *= (1 + slope) ** 2
    return ri(e, r, s['g'], mult=mult, dg=dg, mode=mode, anc=anc)[0] - tlsh * TLSH / SH * 1e3


axes = [('scen', [(n, s['w']) for n, s in SC.items()]), ('mult', [(x, 1 / 5) for x in MULT]), ('dg', [(x, 1 / 3) for x in DG]),
        ('slope', [(x, 1 / 3) for x in SLOPE]), ('tlsh', list(TLSH_AX))]
print(f"r {R:.2%} | d_ref 5ty {L['d_ref']:.4%}")
print("ROE nam quan sat (Q4 ROE_Trailing) TB 2016-25 / trung vi:", {k: (round(pm[k], 4), round(pmed.get(k, float('nan')), 4), len(ROE[k])) for k in PEERS + ['GDA']})
print(f"NEO peer(6, bo GDA): trung vi-cua-TB {A_MED:.4f} | TB-cua-TB {A_MEAN:.4f} | trung vi-cua-trung vi {A_MEDMED:.4f} | TB co GDA(3 nam) {A_MEAN_GDA:.4f}")
print(f"HPG: TB ROE nam 2016-25 {HPG_MEAN10:.4f} | TB 2022-25 {HPG_2225:.4f} | ROE5Y vendor x thue {HPG_ROE5Y_TAX:.4f}")
for n, s in SC.items():
    print(f"  {n}: ROE_T (CUR) {ri(s['e'], R, s['g'])[1]:.2%}")
RUNS = [('CUR', None, 'hien hanh r2'), ('SYM', None, 'chi RONIC=Ke'), ('NONE', None, 'spread fade 5 nam')]
ANCH = [('7.9%', 0.079), ('9.5%', 0.095), ('peer TB-cua-TB', A_MEAN), ('peer trung vi-cua-TB', A_MED), ('peer trung vi-cua-trung vi', A_MEDMED),
        ('peer TB co GDA', A_MEAN_GDA), ('HPG TB 2022-25', HPG_2225), ('11.6% (r1 vendor TB)', 0.1159), ('12.4% (r1 vendor trung vi)', 0.124),
        ('13.5% = Ke', 0.135), ('HPG ROE5Y x thue 15.36%', HPG_ROE5Y_TAX), ('HPG TB 2016-25', HPG_MEAN10)]
ANCH.sort(key=lambda x: x[1])
RUNS += [('REV', a, f'REV neo {n}') for n, a in ANCH]
RUNS += [(m, a, f'{m} neo {n}') for m in ('REVF', 'REVD') for n, a in ANCH if n.startswith('peer') and 'GDA' not in n]
OUT = []
for mode, anc, name in RUNS:
    res = R2C.outcomes(axes, lambda **kw: fv(R, mode=mode, anc=anc, **kw))
    o = {}
    for lab, d in (('5ty', L['d_ref']), ('10tr', L['d_sleeve']['10tr']), ('40tr', L['d_sleeve']['40tr'])):
        st = R2C.stats(res, PX, d); st['label'] = R2C.label(PX, st); o[lab] = st
    m = o['5ty']; OUT.append(dict(mode=mode, anchor=anc, name=name, res=o))
    a_s = f"{anc:.4f}" if anc is not None else '  -   '
    print(f"{mode:5s} {a_s} {name:38s} tam {m['center']:,.0f} P10 {m['p10']:,.0f} P50 {m['p50']:,.0f} P90 {m['p90']:,.0f} | gia/P90-1 {PX / m['p90'] - 1:+.1%} | nhan 5ty {m['label']} / 10tr {o['10tr']['label']} / 40tr {o['40tr']['label']}")
lo, hi = 0.135, 0.1536
for _ in range(30):
    mid = (lo + hi) / 2
    p90 = R2C.stats(R2C.outcomes(axes, lambda **kw: fv(R, mode='REV', anc=mid, **kw)), PX, L['d_ref'])['p90']
    lo, hi = (mid, hi) if p90 < PX else (lo, mid)
BREAK = (lo + hi) / 2
print(f"NEO HOA VON nhan TREN->TRONG (P90 = gia {PX:,.0f}, 5ty): {BREAK:.4%}")
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'peer_roe_q4_2016_2025.csv'), os.path.join(HERE, '..', 'hpg_r2.py'),
                 os.path.join(R2C.HERE, 'common.py'), os.path.join(R2C.HERE, 'r2common.py'), os.path.join(R2C.HERE, 'bq_px_liq_20261104.csv')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
json.dump(dict(r=R, peer_mean=pm, peer_median=pmed, a_med=A_MED, a_mean=A_MEAN, a_medmed=A_MEDMED, a_mean_gda=A_MEAN_GDA,
               hpg_mean10=HPG_MEAN10, hpg_2225=HPG_2225, hpg_roe5y_tax=HPG_ROE5Y_TAX, cwip=CWIP, break_anchor=BREAK, runs=OUT, lock=LOCK),
          open(os.path.join(HERE, 'hpg_5f_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
