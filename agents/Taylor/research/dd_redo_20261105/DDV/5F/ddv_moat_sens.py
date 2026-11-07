"""DDV 3c — do nhay moat tren mo hinh r2 (KHONG sua model.py/model_r2.py). Job Taylor_20261107_131633.
Kenh R: RONIC 20% (model.py G,RONIC) -> Ke=r (doi xung, moi o luoi, ca f27 va terminal).
Kenh M: bien LN rong chu ky DDV 2015-25 (NPM_CYCLE, BQ) -> TB chu ky NGANH phan bon SX (peer 2015-25, BQ peer_out.csv) trung vi / trung binh.
Chay: $DNA_PYEXE -I ddv_moat_sens.py  (2 lan, cmp trung byte)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../calc')); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1, model_r2 as MR, common_r2 as R2
C = R2.C
rows = list(csv.DictReader(open(os.path.join(HERE, '../calc5f/peer_out.csv'))))
PEERS = ('DPM', 'DCM', 'LAS', 'BFC', 'VAF', 'NFC', 'SFG')   # SX phan bon noi dia; loai DGC (hoa chat P4, khong phai phan bon)
acc = {}
for r in rows:
    y = int(r['quarter'][:4])
    if 2015 <= y <= 2025:
        a = acc.setdefault(r['ticker'], {}).setdefault(y, [0.0, 0.0, 0]); a[0] += float(r['NP_P0']); a[1] += float(r['Revenue_P0']); a[2] += 1
npm = {}
for tk, yy in acc.items():
    full = {y: v for y, v in yy.items() if v[2] == 4}
    npm[tk] = dict(npm=sum(v[0] for v in full.values()) / sum(v[1] for v in full.values()), years=len(full))
gpm_ann = {tk: {r['quarter'][:4]: round(float(r['GPM_P0']), 4) for r in rows if r['ticker'] == tk and r['quarter'].endswith('Q4') and r['GPM_P0']} for tk in acc}
pv = sorted(npm[t]['npm'] for t in PEERS); n = len(pv)
PEER_MED = pv[n // 2] if n % 2 else (pv[n // 2 - 1] + pv[n // 2]) / 2
PEER_MEAN = sum(pv) / n
pv_ex = sorted(npm[t]['npm'] for t in PEERS if t not in ('DPM', 'DCM'))   # loai urea khi (dau vao khi, khac cau truc)
PEER_EXU_MEAN = sum(pv_ex) / len(pv_ex)
PEER_EXU_MED = pv_ex[len(pv_ex) // 2] if len(pv_ex) % 2 else (pv_ex[len(pv_ex) // 2 - 1] + pv_ex[len(pv_ex) // 2]) / 2


def value_ps(s, m, r, q4, lv, ronic=None, npm_=None):
    c = M1.SCN[s]; g = M1.G; ro = M1.RONIC if ronic is None else (r if ronic == 'Ke' else ronic)
    npm_ = M1.NPM_CYCLE if npm_ is None else npm_
    f27 = c['np27'] * ((1 - g / ro) if c['np27'] > 0 else 1.0)
    mid = npm_ * M1.REV_NORM - M1.INT_AT_NORM
    e_term = mid * c['mid'] * m * (1 + g) * (1 - g / ro)
    v = M1.NC_NORM - MR.LIVEN[lv]['loss'] + MR.Q4[q4]['np'] / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + e_term / (r - g) / (1 + r) ** 1.25
    return v * 1e9 / M1.SH


def grid(**kw):
    vals, wts = [], []
    for (s, sc), m, (r, rw, _), (q, qc), (l, lc) in itertools.product(M1.SCN.items(), M1.MULTS, R2.r_points(), MR.Q4.items(), MR.LIVEN.items()):
        vals.append(value_ps(s, m, r, q, l, **kw)); wts.append(sc['w'] / len(M1.MULTS) * rw * qc['w'] * lc['w'])
    return vals, wts


L = R2.liquidity_r2('DDV'); px = L['last_price']; d = L['d_ref']; r0 = C.r_now()
def summ(**kw):
    v, w = grid(**kw); cp = value_ps('coso', 1.0, r0, 'nhu_q3', 'thu_du', **kw)
    s = R2.summarize_r2(v, w, sum(a * b for a, b in zip(v, w)) / sum(w), cp, px, d)
    f40 = 1 - L['w250']['sizes']['40tr']['disc']; q10, q90 = s['p10_pre'] if 'p10_pre' in s else None, None
    return dict(centre=s['center_post'], p10=s['p10_out'], p50=s['p50_out'], p90=s['p90_out'], pct_below=round(s['pct_weight_below_price'], 3), label=s['label'],
                centre_param=round(cp * (1 - d)), _raw=s)


V = {
    'CURRENT_r2 (RONIC 20%, bien DDV)': {},
    'R_only (RONIC=Ke, bien DDV)': dict(ronic='Ke'),
    'CHAT3C_med (RONIC=Ke, bien peer trung vi)': dict(ronic='Ke', npm_=PEER_MED),
    'CHAT3C_mean (RONIC=Ke, bien peer TB)': dict(ronic='Ke', npm_=PEER_MEAN),
    'CHAT3C_exUrea_med (RONIC=Ke, peer bo DPM/DCM)': dict(ronic='Ke', npm_=PEER_EXU_MED),
    'CHAT3C_exUrea_mean (RONIC=Ke, peer bo DPM/DCM, TB)': dict(ronic='Ke', npm_=PEER_EXU_MEAN),
    'M_only_med (RONIC 20%, bien peer trung vi)': dict(npm_=PEER_MED),
    'WIDE_hypo (RONIC 25%)': dict(ronic=0.25),
}
out = dict(r=r0, px=px, px_date=L['last_date'], d_ref=d, ddv_npm_cycle=M1.NPM_CYCLE, peer_npm=npm, peer_set=PEERS,
           peer_med=PEER_MED, peer_mean=PEER_MEAN, peer_exurea_med=PEER_EXU_MED, peer_exurea_mean=PEER_EXU_MEAN,
           roic_2025Q4={r['ticker']: {k: r[k] for k in ('ROIC5Y', 'ROIC_Min5Y', 'ROIC10Y', 'ROIC_Min10Y', 'ROE5Y', 'ROE_Min5Y')} for r in rows if r['quarter'] == '2025Q4'}, gpm_annual_Q4row=gpm_ann, variants={})
for k, kw in V.items():
    s = summ(**kw); raw = s.pop('_raw'); out['variants'][k] = s
# sleeve 40tr label check
for k, kw in V.items():
    v, w = grid(**kw); s = R2.summarize_r2(v, w, sum(a * b for a, b in zip(v, w)) / sum(w), 0.0, px, L['w250']['sizes']['40tr']['disc'])
    out['variants'][k]['label_sleeve40'] = s['label']
json.dump(out, open(os.path.join(HERE, 'ddv_moat_sens_out.json'), 'w'), indent=1, ensure_ascii=False, sort_keys=True)
with open(os.path.join(HERE, 'ddv_moat_sens_out.txt'), 'w') as f:
    print(f"r={r0:.4f} px={px} ({L['last_date']}) d_ref={d:.4%} DDV NPM cycle={M1.NPM_CYCLE:.4%} peer med={PEER_MED:.4%} mean={PEER_MEAN:.4%} exUrea med={PEER_EXU_MED:.4%} exUrea mean={PEER_EXU_MEAN:.4%}", file=f)
    for t, v in sorted(npm.items()): print(f"  {t} NPM2015-25={v['npm']:.4%} years={v['years']}", file=f)
    for k, s in out['variants'].items(): print(k, json.dumps(s, ensure_ascii=False), file=f)
print(open(os.path.join(HERE, 'ddv_moat_sens_out.txt')).read())
