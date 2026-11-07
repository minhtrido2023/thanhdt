"""Do nhay moat DRI VONG 2 (job Taylor_20261107_122446). Sua r1: GAP GPM nay la TTM co trong so doanh thu (khong phai GPM_P0 quy Q4).
Exec dri_redo_r2.py (calc/) toi truoc buoc ghi file (KHONG ghi de calc/). Chay: $DNA_PYEXE -B moat_sens_5f.py (du lieu: ttm_bq.csv = BQ ticker_financial).
 GPM TTM(ticker, nam) = sum_i(GPM_Pi*Revenue_Pi)/sum_i(Revenue_Pi), i=0..3, tai dong Q4 (GPM_Pi, Revenue_Pi la gia tri tung quy).
 NONE: Cref += GAP*price(mid TB) (GAP = TB 2017-25 cua [GPM TTM DRI - trung vi peer] moi nam); NONE_half: 1/2 GAP.
 NONE_sym: NONE + RONIC=Ke doi xung (trong so nhanh KINH TE = 0).
 WIDE [UL]: tai canh NPV = +S*PV(capex), S=0,25; WIDE_econ_only: chi bo nhanh KINH TE (S=0) de tach phan moat that."""
import os, sys, io, csv, json, contextlib, builtins, statistics as st
CALC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../calc'))
src = builtins.open(os.path.join(CALC, 'dri_redo_r2.py'), encoding='utf-8').read().split("out['files_read']")[0]
g = {'__file__': os.path.join(CALC, 'dri_redo_r2.py'), '__name__': 'r2'}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, 'dri_redo_r2.py', 'exec'), g)
ns, CEN, grid, st_, WB, val, MID, f, px = g['ns'], g['CEN'], g['grid'], g['st_'], g['WB'], g['val'], g['MID'], g['f'], g['px']
base = st_(grid(WB), f, px); assert round(base['mean']) == 14092, base

# ---- GPM TTM co trong so doanh thu ----
T = {}
for r in csv.DictReader(builtins.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ttm_bq.csv'))):
    if not r['quarter'].endswith('Q4') or any(r[f'{c}_P{i}'] == '' for c in ('GPM', 'Revenue') for i in range(4)): continue   # GVR 2017-18 thieu du lieu BQ => peer chi con co mat
    rev = [float(r[f'Revenue_P{i}']) for i in range(4)]; gp = [float(r[f'GPM_P{i}']) for i in range(4)]
    T.setdefault(r['quarter'][:4], {})[r['ticker']] = sum(a * b for a, b in zip(gp, rev)) / sum(rev)
yrs = [str(y) for y in range(2017, 2026)]
def gapf(peers, agg):
    per = [T[y]['DRI'] - agg([T[y][t] for t in peers if t in T[y]]) for y in yrs]
    return st.mean(per), sum(p > 0 for p in per)
dri = st.mean(T[y]['DRI'] for y in yrs)
GAPS = {}
for nm, peers, agg in (('median_DPR_PHR_GVR', ('DPR', 'PHR', 'GVR'), st.median), ('mean_DPR_PHR_GVR', ('DPR', 'PHR', 'GVR'), st.mean),
                       ('median_+TRC', ('DPR', 'PHR', 'GVR', 'TRC'), st.median), ('mean_+TRC', ('DPR', 'PHR', 'GVR', 'TRC'), st.mean),
                       ('DPR_only', ('DPR',), st.mean)):
    gp, n = gapf(peers, agg); GAPS[nm] = dict(gap=gp, years_above=f'{n}/9', peer_avg=dri - gp)
P_TB = ns['price'](MID['TB']); C0 = CEN['Cref']
res = dict(dri_ttm_gpm_2017_25=dri, gaps=GAPS, Cref=C0, price_TB=P_TB, NARROW=base,
           ttm_by_year={y: {k: round(v, 4) for k, v in T[y].items()} for y in yrs})
def run(gap, w_econ=None):
    CEN['Cref'] = C0 + gap * P_TB
    try: s = st_(grid(WB if w_econ is None else {'NQ15_NPV0': 1.0}), f, px)
    finally: CEN['Cref'] = C0
    s['Cref'] = C0 + gap * P_TB; s['label'] = g['C'].label(px, s['p10'], s['p90']); return s
G = GAPS['median_DPR_PHR_GVR']['gap']
res['NONE'] = run(G); res['NONE_half'] = run(G / 2); res['NONE_sym'] = run(G, 1)
res['NONE_mean'] = run(GAPS['mean_DPR_PHR_GVR']['gap']); res['NONE_medTRC'] = run(GAPS['median_+TRC']['gap'])
res['NONE_meanTRC'] = run(GAPS['mean_+TRC']['gap']); res['NONE_DPR'] = run(GAPS['DPR_only']['gap'])
res['NARROW']['label'] = g['C'].label(px, base['p10'], base['p90'])
# ---- WIDE ----
S = 0.25; cx3 = ns['capex3']
def pvcx(mid, L, p):
    e = val('NQ15_ECON', MID[mid], L, scn=p); ns['capex3'] = lambda pl, m: {}
    try: e0 = val('NQ15_ECON', MID[mid], L, scn=p)
    finally: ns['capex3'] = cx3
    return e0 - e
rows = grid({'NQ15_NPV0': 1.0}); res['WIDE_econ_only'] = st_(rows, f, px)
for r in rows: r['V'] = r['V'] + S * pvcx(r['mid'], r['L'], r['path'])
res['WIDE'] = st_(rows, f, px); res['WIDE']['S'] = S
for k in ('WIDE', 'WIDE_econ_only'): res[k]['label'] = g['C'].label(px, res[k]['p10'], res[k]['p90'])
# ---- ROE giua chu ky mo hinh: LNST(P_TB, V=KH26 13.800 t, Cref r2) ----
V = 13800.0; cm = 1.0
Cm = C0 + CEN['k'] * (P_TB - ns['P25'])
core = ((V * P_TB - cm * Cm * ((1 - CEN['f']) * V + CEN['f'] * ns['V0'])) / 1e3 + ns['OTHER_GP'] - ns['SGA'] * 0.9 + ns['FIN']) * (1 - CEN['tax']) - ns['NETC'] * 0.05 * 0.8
res['roe_mid'] = dict(lnst_mid_ty=core, k=CEN['k'], gpm_model=1 - Cm * ((1 - CEN['f']) + CEN['f'] * ns['V0'] / V) / P_TB,
                     equity_2026Q2_ty=11004.29952842896 * 73.2e6 / 1e9, equity_2026Q3_ty=10043.77417443989 * 73.2e6 / 1e9)
for q in ('2026Q2', '2026Q3'): res['roe_mid']['roe_' + q] = core / res['roe_mid']['equity_' + q + '_ty']
json.dump(res, builtins.open('moat_sens_5f_out.json', 'w'), indent=1, default=float, sort_keys=True)
for k in ('NARROW', 'NONE_half', 'NONE', 'NONE_sym', 'NONE_mean', 'NONE_medTRC', 'NONE_meanTRC', 'NONE_DPR', 'WIDE_econ_only', 'WIDE'):
    s = res[k]; print(f"{k:14s} tam {s['mean']:7,.0f} ({s['mean']-base['mean']:+,.0f}; {s['mean']/base['mean']-1:+.1%}) P10 {s['p10']:7,.0f} P50 {s['p50']:7,.0f} P90 {s['p90']:7,.0f} duoi gia {s['below']:.1%} nhan {s['label']}" + (f" Cref {s['Cref']:.2f}" if 'Cref' in s else ''))
print(f"DRI GPM TTM 2017-25 {dri:.4f}")
for nm, d in GAPS.items(): print(f"  gap {nm:20s} {d['gap']*100:6.2f}pp peer {d['peer_avg']:.4f} nam DRI>peer {d['years_above']}")
print(f"Cref {C0:.2f} price TB {P_TB:.2f} | roe_mid {json.dumps(res['roe_mid'], default=float)}")
