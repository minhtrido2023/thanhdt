"""DDV 3c r2 — sua sau skeptic (job Taylor_20261108_024219). KHONG sua model.py/model_r2.py, khong sua ddv_moat_sens.py (r1).
Sua 2 loi r1: (1) peer cat mot chieu -> headline = peer PHOT-PHAT LAS/NFC (+ dai co DHB); ex-urea (BFC/SFG/VAF pha tron) ha xuong do nhay.
(2) tron bien tong/van hanh: NPM peer da gom thu nhap TC cua peer -> bien the 'noint' KHONG tru INT_AT_NORM (co so nhat quan),
    bien the 'int' giu tru (bao thu, dem thieu) -> bao ca hai lam dai.
Kenh R: RONIC=Ke doi xung moi o luoi (f27 + terminal). Peer data: calc5f/peer_r2_out.csv (= peer_out.csv + DHB, cung SQL).
Chay: $DNA_PYEXE -I ddv_moat_sens_r2.py  (2 lan, cmp trung byte)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../calc')); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1, model_r2 as MR, common_r2 as R2
C = R2.C
rows = list(csv.DictReader(open(os.path.join(HERE, '../calc5f/peer_r2_out.csv'))))
acc = {}
for r in rows:
    y = int(r['quarter'][:4])
    if 2015 <= y <= 2025 and r['NP_P0'] and r['Revenue_P0']:
        a = acc.setdefault(r['ticker'], {}).setdefault(y, [0.0, 0.0, 0]); a[0] += float(r['NP_P0']); a[1] += float(r['Revenue_P0']); a[2] += 1
npm = {}
for tk, yy in acc.items():
    full = {y: v for y, v in yy.items() if v[2] == 4}
    npm[tk] = dict(npm=sum(v[0] for v in full.values()) / sum(v[1] for v in full.values()), years=len(full), y0=min(full), y1=max(full))
gpm_ann = {tk: {r['quarter'][:4]: round(float(r['GPM_P0']), 4) for r in rows if r['ticker'] == tk and r['quarter'].endswith('Q4') and r['GPM_P0']} for tk in acc}


def med(xs):
    xs = sorted(xs); n = len(xs); return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


SETS = {'phos2_LAS_NFC': ('LAS', 'NFC'), 'phos3_LAS_NFC_DHB': ('LAS', 'NFC', 'DHB'),
        'exUrea5_LAS_NFC_BFC_SFG_VAF': ('LAS', 'NFC', 'BFC', 'SFG', 'VAF'), 'all7': ('DPM', 'DCM', 'LAS', 'BFC', 'VAF', 'NFC', 'SFG')}
PEER = {}
for k, ts in SETS.items():
    xs = [npm[t]['npm'] for t in ts]; PEER[k + '_med'] = med(xs); PEER[k + '_mean'] = sum(xs) / len(xs)


def value_ps(s, m, r, q4, lv, ronic=None, npm_=None, sub_int=True):
    c = M1.SCN[s]; g = M1.G; ro = M1.RONIC if ronic is None else (r if ronic == 'Ke' else ronic)
    npm_ = M1.NPM_CYCLE if npm_ is None else npm_
    f27 = c['np27'] * ((1 - g / ro) if c['np27'] > 0 else 1.0)
    mid = npm_ * M1.REV_NORM - (M1.INT_AT_NORM if sub_int else 0.0)
    e_term = mid * c['mid'] * m * (1 + g) * (1 - g / ro)
    v = M1.NC_NORM - MR.LIVEN[lv]['loss'] + MR.Q4[q4]['np'] / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + e_term / (r - g) / (1 + r) ** 1.25
    return v * 1e9 / M1.SH


def grid(**kw):
    vals, wts = [], []
    for (s, sc), m, (r, rw, _), (q, qc), (l, lc) in itertools.product(M1.SCN.items(), M1.MULTS, R2.r_points(), MR.Q4.items(), MR.LIVEN.items()):
        vals.append(value_ps(s, m, r, q, l, **kw)); wts.append(sc['w'] / len(M1.MULTS) * rw * qc['w'] * lc['w'])
    return vals, wts


L = R2.liquidity_r2('DDV'); px = L['last_price']; d = L['d_ref']; r0 = C.r_now(); d40 = L['w250']['sizes']['40tr']['disc']


def summ(**kw):
    v, w = grid(**kw); cp = value_ps('coso', 1.0, r0, 'nhu_q3', 'thu_du', **kw); ce = sum(a * b for a, b in zip(v, w)) / sum(w)
    s = R2.summarize_r2(v, w, ce, cp, px, d); s40 = R2.summarize_r2(v, w, ce, 0.0, px, d40)
    return dict(centre=s['center_post'], p10=s['p10_out'], p50=s['p50_out'], p90=s['p90_out'], pct_below=round(s['pct_weight_below_price'], 3),
                label=s['label'], label_sleeve40=s40['label'], p90_vs_px=round(s['p90_out'] / px - 1, 4), centre_param=round(cp * (1 - d)), **{k: v_ for k, v_ in kw.items() if k != 'ronic'})


V = {'CURRENT_r2 (RONIC 20%, bien DDV)': {}, 'R_only (RONIC=Ke, bien DDV)': dict(ronic='Ke'), 'WIDE_hypo (RONIC 25%)': dict(ronic=0.25)}
for k in PEER:
    V[f'CHAT3C_{k}_int (RONIC=Ke, tru INT_AT_NORM)'] = dict(ronic='Ke', npm_=PEER[k], sub_int=True)
    V[f'CHAT3C_{k}_noint (RONIC=Ke, khong tru INT_AT_NORM)'] = dict(ronic='Ke', npm_=PEER[k], sub_int=False)
out = dict(r=r0, px=px, px_date=L['last_date'], d_ref=d, d_40tr=d40, ddv_npm_cycle=M1.NPM_CYCLE, int_at_norm=M1.INT_AT_NORM, rev_norm=M1.REV_NORM,
           int_at_norm_pct_rev=M1.INT_AT_NORM / M1.REV_NORM, peer_npm=npm, peer_sets=SETS, peer_stats=PEER,
           roic_2025Q4={r['ticker']: {k: r[k] for k in ('ROIC5Y', 'ROIC_Min5Y', 'ROIC10Y', 'ROIC_Min10Y', 'ROE5Y', 'ROE_Min5Y')} for r in rows if r['quarter'] == '2025Q4'},
           gpm_annual_Q4row=gpm_ann, variants={k: summ(**kw) for k, kw in V.items()})
json.dump(out, open(os.path.join(HERE, 'ddv_moat_sens_r2_out.json'), 'w'), indent=1, ensure_ascii=False, sort_keys=True)
with open(os.path.join(HERE, 'ddv_moat_sens_r2_out.txt'), 'w') as f:
    print(f"r={r0:.4f} px={px} ({L['last_date']}) d_ref={d:.4%} DDV NPM cycle={M1.NPM_CYCLE:.4%} INT_AT_NORM={M1.INT_AT_NORM:.1f} ty ({M1.INT_AT_NORM / M1.REV_NORM:.2%} DT)", file=f)
    for t, v in sorted(npm.items()): print(f"  {t} NPM={v['npm']:.4%} years={v['years']} ({v['y0']}-{v['y1']})", file=f)
    for k, v in PEER.items(): print(f"  {k}={v:.4%}", file=f)
    for k, s in out['variants'].items(): print(k, json.dumps(s, ensure_ascii=False), file=f)
print(open(os.path.join(HERE, 'ddv_moat_sens_r2_out.txt')).read())
