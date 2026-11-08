"""Do nhay moat DRI tren BASE r3 (08/11/2026, job Taylor_20261108_153743). Gap GPM giong het moat_sens_5f.py (GPM_P0 dong Q4 = ca nam, ttm_bq.csv).
Exec ../calc/dri_redo_r3.py toi truoc buoc ghi file (KHONG ghi calc/). Quy uoc cuoi 08/11: moat chi CONG khi ben; NONE/NONE_half chi la do nhay rui ro
'neu bien ve trung binh nganh', KHONG phai headline. WIDE khong chay (khong co moat ben). Chay: $DNA_PYEXE -B moat_sens_5f_r3.py"""
import os, io, csv, json, contextlib, builtins, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); CALC = os.path.abspath(os.path.join(H, '../calc'))
src = builtins.open(os.path.join(CALC, 'dri_redo_r3.py'), encoding='utf-8').read().split("out['files_read']")[0]
g = {'__file__': os.path.join(CALC, 'dri_redo_r3.py'), '__name__': 'r3'}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, 'dri_redo_r3.py', 'exec'), g)
ns, CEN, grid, st_, MID, f, px, C = g['ns'], g['CEN'], g['grid'], g['st_'], g['MID'], g['f'], g['px'], g['C']
base = st_(grid(), f, px); assert round(base['mean']) == round(g['out']['post']['mean']), base
T = {}
for r in csv.DictReader(builtins.open(os.path.join(H, 'ttm_bq.csv'))):
    if not r['quarter'].endswith('Q4') or r['GPM_P0'] == '': continue
    T.setdefault(r['quarter'][:4], {})[r['ticker']] = float(r['GPM_P0'])
yrs = [str(y) for y in range(2017, 2026)]
def gapf(peers, agg): return st.mean(T[y]['DRI'] - agg([T[y][t] for t in peers if t in T[y]]) for y in yrs)
GAPS = {nm: gapf(p, a) for nm, p, a in (('median_DPR_PHR_GVR', ('DPR', 'PHR', 'GVR'), st.median), ('mean_DPR_PHR_GVR', ('DPR', 'PHR', 'GVR'), st.mean),
        ('median_+TRC', ('DPR', 'PHR', 'GVR', 'TRC'), st.median), ('mean_+TRC', ('DPR', 'PHR', 'GVR', 'TRC'), st.mean), ('DPR_only', ('DPR',), st.mean))}
assert round(GAPS['median_DPR_PHR_GVR'] * 100, 2) == 11.70, GAPS
P_TB = ns['price'](MID['TB']); C0 = CEN['Cref']
def run(gap):
    CEN['Cref'] = C0 + gap * P_TB
    try: s = st_(grid(), f, px)
    finally: CEN['Cref'] = C0
    s['Cref'] = C0 + gap * P_TB; s['label'] = C.label(px, s['p10'], s['p90']); return s
res = dict(base_r3=base, gaps=GAPS, Cref=C0, price_TB=P_TB, price=px)
res['base_r3']['label'] = C.label(px, base['p10'], base['p90'])
G = GAPS['median_DPR_PHR_GVR']
res['NONE'] = run(G); res['NONE_half'] = run(G / 2)
for k in ('mean_DPR_PHR_GVR', 'median_+TRC', 'mean_+TRC', 'DPR_only'): res[f'NONE_{k}'] = run(GAPS[k])
json.dump(res, open(os.path.join(H, 'moat_sens_5f_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
for k in ('base_r3', 'NONE_half', 'NONE', 'NONE_mean_DPR_PHR_GVR', 'NONE_median_+TRC', 'NONE_mean_+TRC', 'NONE_DPR_only'):
    s = res[k]; print(f"{k:22s} tam {s['mean']:7,.0f} ({s['mean']-base['mean']:+,.0f}; {s['mean']/base['mean']-1:+.1%}) P10 {s['p10']:7,.0f} P50 {s['p50']:7,.0f} P90 {s['p90']:7,.0f} duoi gia {s['below']:.1%} {s['label']}" + (f" Cref {s['Cref']:.2f}" if 'Cref' in s else ''))
print(f"gap pp: " + ' '.join(f'{k} {v*100:.2f}' for k, v in GAPS.items()) + f" | Cref {C0:.2f} price TB {P_TB:.2f} | gia {px:,.0f}")
