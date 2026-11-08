"""VONG 3 — SAU KHOA LOCK_r3_md5.txt: gia dong cua 06/11 (BQ, r3data/px_dgc_20261106.csv) + thanh khoan -> ../SUMMARY.json (backup SUMMARY_r2.json) + compare_r3_out.txt.
Chay: $DNA_PYEXE -I compare_r3.py"""
import csv, hashlib, json, math, os, shutil, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import common_r2 as R2
WC = '/home/trido/thanhdt/WorkingClaude'
for l in open(os.path.join(HERE, 'LOCK_r3_md5.txt')):
    if l.strip():
        h, p = l.split(); assert hashlib.md5(open(os.path.join(WC, p), 'rb').read()).hexdigest() == h, f'doi sau khoa: {p}'
M = json.load(open(os.path.join(HERE, 'model_r3_out.json')))
rows = list(csv.DictReader(open(os.path.join(HERE, 'r3data/px_dgc_20261106.csv'))))
assert rows[-1]['time'] == '2026-11-06'
L = dict(last_price=float(rows[-1]['Price']), last_date=rows[-1]['time'])
for n in (250, 60):
    d = rows[-n - 1:]
    c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    adv = float(np.median((p * v)[1:])); sig = float(np.std(np.diff(np.log(c)), ddof=1))
    L[f'w{n}'] = dict(window=f"{d[1]['time']}..{d[-1]['time']}", adv_med=adv, sigma_d=sig,
                      sizes={f'{q/1e6:.0f}tr': dict(q_over_adv=q / adv, disc=sig * math.sqrt(q / adv), in_calib=bool(R2.CALIB[0] <= q / adv <= R2.CALIB[1]),
                                                    days_at_15pct=q / (0.15 * adv)) for q in (R2.Q_REF,) + R2.Q_SLEEVE})
d = L['w250']['sizes']['5000tr']['disc']; px = L['last_price']; f = 1 - d
S = dict(ticker='DGC', round=3, job='Taylor_20261108_164329', asof_price_date=L['last_date'], price=px, price_src='BQ tav2_bq.ticker Price 2026-11-06 (r3data/px_dgc_r3.sql)')
S.update(R2.summarize_r2(M['outcomes_vals'], M['outcomes_wts'], M['center_pre'], M['center_param_pre'], px, d))
S['px_vs_center_post'] = px / S['center_post'] - 1
alt = {}
for k, P in M['parallel'].items():
    s = R2.summarize_r2(P['vals'], P['wts'], P['center_pre'], P['center_pre'], px, d)
    alt[k] = dict(desc=P['desc'], **{x: s[x] for x in ('n_outcomes', 'center_post', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label')})
S['headline_vs_alternatives'] = alt
S['bridge_pre'] = M['bridge_pre']; S['single_correction_post'] = {k: round(v * f) for k, v in M['single_correction_pre'].items()}
S['r_sens_post'] = {k: round(v * f) for k, v in M['r_sens_pre'].items()}
S['ck_ref_size'] = dict(q_vnd=R2.Q_REF, adv='250 phien', disc=d, in_calib=L['w250']['sizes']['5000tr']['in_calib'], disc_adv60=L['w60']['sizes']['5000tr']['disc'],
                        in_calib_adv60=L['w60']['sizes']['5000tr']['in_calib'])
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], q_over_adv250=L['w250']['sizes'][k]['q_over_adv'],
                               in_calib=L['w250']['sizes'][k]['in_calib']) for k in ('10tr', '20tr', '40tr')}
S['liquidity'] = L
S['p10_post'], S['p50_post'], S['p90_post'], S['center_post_liq'], S['liq_disc_5ty'], S['grid_n'], S['grid_desc'] = S['p10_out'], S['p50_out'], S['p90_out'], S['center_post'], d, S['n_outcomes'], M['grid_desc']
S['model_r3_out_md5'] = hashlib.md5(open(os.path.join(HERE, 'model_r3_out.json'), 'rb').read()).hexdigest()
r2p = os.path.join(BASE, 'SUMMARY_r2.json')
if not os.path.exists(r2p):
    shutil.copy(os.path.join(BASE, 'SUMMARY.json'), r2p)
R = json.load(open(r2p)); S['r2'] = {k: R[k] for k in ('center_post', 'p10_out', 'p50_out', 'p90_out', 'label', 'price', 'asof_price_date', 'pct_weight_below_price')}
S['delta_center_vs_r2_pct'] = S['center_post'] / R['center_post'] - 1
json.dump(S, open(os.path.join(HERE, 'summary_r3_core.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'compare_r3_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'n_outcomes', 'center_pre', 'center_post', 'center_param_post', 'p10_out', 'p25_out', 'p50_out', 'p75_out', 'p90_out',
              'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'liq_disc_5ty', 'delta_center_vs_r2_pct'):
        print(f'{k}: {S[k]}', file=fo)
    print('r2:', json.dumps(S['r2'], ensure_ascii=False), file=fo)
    for n in ('w250', 'w60'):
        w = L[n]
        print(f"{n} {w['window']} ADV {w['adv_med']/1e9:.2f} ty sigma {w['sigma_d']:.4f} | " + ' | '.join(
            f"{k}: CK {v['disc']:.3%} Q/ADV {v['q_over_adv']:.4%} calib={v['in_calib']}" for k, v in w['sizes'].items()), file=fo)
    for k, v in alt.items():
        print(f'alt {k}:', json.dumps(v, ensure_ascii=False), file=fo)
    print('single_post:', json.dumps(S['single_correction_post']), file=fo); print('r_sens_post:', json.dumps(S['r_sens_post']), file=fo)
print(open(os.path.join(HERE, 'compare_r3_out.txt')).read())
