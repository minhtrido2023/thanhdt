"""VONG 2 — SAU KHOA: <TK>/calc/model_r2_out.json phai khop md5 dong 1 cua LOCK_r2_md5.txt (cac dong sau = md5 file upstream, kiem lai tung file).
-> gia 04/11 + thanh khoan (ADV 250/60, co 5 ty + sleeve 10/20/40 tr) -> <TK>/SUMMARY.json (backup SUMMARY_r1.json 1 lan) + calc/compare_r2_out.txt.
Chay: $DNA_PYEXE -I compare_r2.py <TK>"""
import hashlib, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_r2 as R2
C = R2.C
tk = sys.argv[1]; base = os.path.join(os.path.dirname(R2.HERE), tk); calc = os.path.join(base, 'calc')
lock = [l.split() for l in open(os.path.join(calc, 'LOCK_r2_md5.txt')) if l.strip()]
for h, p in lock:
    fp = p if os.path.isabs(p) else os.path.join(C.WC, p)
    assert hashlib.md5(open(fp, 'rb').read()).hexdigest() == h, f'doi sau khoa: {p}'
M = json.load(open(os.path.join(calc, 'model_r2_out.json')))
L = R2.liquidity_r2(tk); px = L['last_price']; d = L['d_ref']
S = dict(ticker=tk, round=2, job='Taylor_20261105_020016', asof_price_date=L['last_date'], price=px)
S.update(R2.summarize_r2(M['outcomes_vals'], M['outcomes_wts'], M['center_pre'], M['center_param_pre'], px, d))
S['px_vs_center_post'] = px / S['center_post'] - 1
S['parallel'] = {}
for k, P in M.get('parallel', {}).items():
    s = R2.summarize_r2(P['vals'], P['wts'], P['center_pre'], P.get('center_param_pre', P['center_pre']), px, d)
    S['parallel'][k] = dict(desc=P['desc'], **{x: s[x] for x in ('n_outcomes', 'center_post', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label')})
# truong cu (giu ten): p10_post... = ban muc ket cuc moi
S.update(center_pre_liq=S['center_pre'], center_post_liq=S['center_post'], p10_post=S['p10_out'], p25_post=S['p25_out'], p50_post=S['p50_out'],
         p75_post=S['p75_out'], p90_post=S['p90_out'], liq_disc_5ty=d, grid_n=S['n_outcomes'], grid_desc=M['grid_desc'])
S['ck_ref_size'] = dict(q_vnd=R2.Q_REF, adv='250 phien', disc=d, in_calib=L['w250']['sizes']['5000tr']['in_calib'],
                        disc_adv60=L['w60']['sizes']['5000tr']['disc'])
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], q_over_adv250=L['w250']['sizes'][k]['q_over_adv'],
                               in_calib=L['w250']['sizes'][k]['in_calib']) for k in ('10tr', '20tr', '40tr')}
S['liquidity'] = L
for k in ('axes_included', 'axes_excluded', 'base_adjustments', 'center_vs_p50_note_model', 'r', 'r_sens_pre', 'scenarios_pre', 'gordon_roe_xcheck',
          'free_float', 'free_float_src', 'change_reason', 'warnings', 'open_issues', 'new_data_obs', 'branch_note', 'fear_buy_25'):
    if k in M:
        S[k] = M[k]
f = 1 - d
S['r_sens_post'] = {k: round(v * f) for k, v in M.get('r_sens_pre', {}).items()}
S['center_vs_p50_note'] = (f"tam (ky vong trong so luoi, sau CK) {S['center_post']} vs P50 ket cuc {S['p50_out']} vs gia tri tai tham so trung tam "
                           f"{S['center_param_post']}. " + M.get('center_vs_p50_note_model', ''))
r1p = os.path.join(base, 'SUMMARY_r1.json')
if not os.path.exists(r1p):
    shutil.copy(os.path.join(base, 'SUMMARY.json'), r1p)
R1 = json.load(open(r1p))
S['r1'] = dict(center_post=R1['center_post_liq'], p10_post=R1['p10_post'], p90_post=R1['p90_post'], label=R1['label'])
S['delta_center_vs_r1_pct'] = S['center_post'] / R1['center_post_liq'] - 1
S['zone_old'] = R1.get('zone_old')
json.dump(S, open(os.path.join(base, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(calc, 'compare_r2_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'n_outcomes', 'center_pre', 'center_post', 'center_param_post', 'p10_out', 'p25_out', 'p50_out', 'p75_out', 'p90_out',
              'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'liq_disc_5ty', 'delta_center_vs_r1_pct'):
        print(f'{k}: {S[k]}', file=fo)
    print('r1:', json.dumps(S['r1'], ensure_ascii=False), file=fo)
    for n in ('w250', 'w60'):
        w = L[n]
        print(f"{n} {w['window']} ADV {w['adv_med']/1e9:.2f} ty sigma {w['sigma_d']:.4f} | " +
              ' | '.join(f"{k}: CK {v['disc']:.3%} Q/ADV {v['q_over_adv']:.4%} calib={v['in_calib']} phien@15% {v['days_at_15pct']:.2f}" for k, v in w['sizes'].items()), file=fo)
    for k, v in S['parallel'].items():
        print(f'parallel {k}:', json.dumps(v, ensure_ascii=False), file=fo)
    print('r_sens_post:', json.dumps(S['r_sens_post']), file=fo)
print(open(os.path.join(calc, 'compare_r2_out.txt')).read())
