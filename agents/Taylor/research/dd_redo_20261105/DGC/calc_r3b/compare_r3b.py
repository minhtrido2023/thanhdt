"""VONG 3b — SAU KHOA LOCK_r3b_md5.txt: gia 06/11 (BQ, ../calc/r3data/px_dgc_20261106.csv) + thanh khoan + lua chon exit (STANDARD #8) -> summary_r3b_core.json + compare_r3b_out.txt.
Chay: $DNA_PYEXE -I compare_r3b.py"""
import csv, hashlib, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import common_r2 as R2
WC = '/home/trido/thanhdt/WorkingClaude'
for l in open(os.path.join(HERE, 'LOCK_r3b_md5.txt')):
    if l.strip() and not l.startswith('#'):
        h, p = l.split(); assert hashlib.md5(open(os.path.join(WC, p), 'rb').read()).hexdigest() == h, f'doi sau khoa: {p}'
M = json.load(open(os.path.join(HERE, 'model_r3b_out.json')))
rows = list(csv.DictReader(open(os.path.join(BASE, 'calc/r3data/px_dgc_20261106.csv'))))
assert rows[-1]['time'] == '2026-11-06'
L = dict(last_price=float(rows[-1]['Price']), last_date=rows[-1]['time'])
for n in (250, 60):
    d = rows[-n - 1:]
    c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    adv = float(np.median((p * v)[1:])); sig = float(np.std(np.diff(np.log(c)), ddof=1))
    L[f'w{n}'] = dict(window=f"{d[1]['time']}..{d[-1]['time']}", adv_med=adv, sigma_d=sig,
                      sizes={f'{q/1e6:.0f}tr': dict(q_over_adv=q / adv, disc=sig * math.sqrt(q / adv), in_calib=bool(R2.CALIB[0] <= q / adv <= R2.CALIB[1])) for q in (R2.Q_REF,) + R2.Q_SLEEVE})
d = L['w250']['sizes']['5000tr']['disc']; px = L['last_price']; f = 1 - d
S = dict(ticker='DGC', round='3b', job='Taylor_20261108_175121', asof_price_date=L['last_date'], price=px, price_src='BQ tav2_bq.ticker Price 2026-11-06 (calc/r3data/px_dgc_r3.sql)')
S.update(R2.summarize_r2(M['outcomes_vals'], M['outcomes_wts'], M['center_pre'], M['center_param_pre'], px, d))
S['px_vs_center_post'] = px / S['center_post'] - 1
alt = {}
for k, P in M['parallel'].items():
    s = R2.summarize_r2(P['vals'], P['wts'], P['center_pre'], P['center_pre'], px, d)
    alt[k] = dict(desc=P['desc'], **{x: s[x] for x in ('n_outcomes', 'center_post', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label')})
S['headline_vs_alternatives'] = alt
S['r_sens_post'] = {k: round(v * f) for k, v in M['r_sens_pre'].items()}
S['ck_ref_size'] = dict(q_vnd=R2.Q_REF, disc_adv250=d, in_calib_adv250=L['w250']['sizes']['5000tr']['in_calib'], disc_adv60=L['w60']['sizes']['5000tr']['disc'], in_calib_adv60=L['w60']['sizes']['5000tr']['in_calib'])
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], in_calib_adv250=L['w250']['sizes'][k]['in_calib'], in_calib_adv60=L['w60']['sizes'][k]['in_calib']) for k in ('10tr', '20tr', '40tr')}
S['liquidity'] = L
# --- ky luat exit (STANDARD #8): vi the that ZaloPay (broker dnse_raw_2026-11-08 19:07, NAV nav_history_ZaloPay.csv 06/11) ---
QTY, COST, NAV = 10000, 39775.0, 934551492.0
a60, s60 = L['w60']['adv_med'], L['w60']['sigma_d']
mv = QTY * px
def opt(target_frac, label, tranches):
    keep = int(math.floor(target_frac * NAV / px / 100) * 100) if target_frac is not None else QTY
    sell = QTY - keep; q = sell * px
    return dict(option=label, keep_qty=keep, sell_qty=sell, keep_pct_nav_mkt=keep * px / NAV, sell_value_vnd=q, q_over_adv60=q / a60,
                impact_adv60_one_shot=s60 * math.sqrt(q / a60) if q else 0.0, per_tranche_q_over_adv60=(q / tranches / a60) if q else 0.0, tranches=tranches,
                realized_pnl_vnd_at_px=-(COST - px) * sell, fee_tax_vnd=q * (0.00097 + 0.001))
S['exit_discipline'] = dict(
    position=dict(account='ZaloPay', qty=QTY, cost=COST, price=px, mkt_value=mv, nav_0611=NAV, pct_nav_mkt=mv / NAV, pct_nav_cost=QTY * COST / NAV, sleeve_cap=(0.02, 0.04),
                  unrealized_vnd=(px - COST) * QTY, src='dnse_raw_2026-11-08.jsonl (accountNo 0001743768, tradeQuantity 10000, costPrice 39775) + data/execution_logs/nav_history_ZaloPay.csv 2026-11-06'),
    options=[opt(None, 'A giu nguyen 10.000 cp (35,3% NAV) — vi pham tran sleeve, can user chap nhan ngoai le bang van ban', 0),
             opt(0.10, 'B giam ve ~10% NAV (buoc dem, 2 dot)', 2),
             opt(0.04, 'C giam ve tran sleeve 4% NAV, 3 dot', 3),
             opt(0.02, 'D giam ve san sleeve 2% NAV, 3 dot', 3)],
    note='Lenh HOSE han che giao dich chi phien chieu; dot = 1 phien chieu. Impact = sigma60*sqrt(Q/ADV60) (cung cong thuc CK). KHONG quyet thay user, KHONG dat lenh.')
S['model_r3b_out_md5'] = hashlib.md5(open(os.path.join(HERE, 'model_r3b_out.json'), 'rb').read()).hexdigest()
R3 = json.load(open(os.path.join(BASE, 'SUMMARY_r3.json')))
S['r3'] = {k: R3[k] for k in ('center_post', 'p10_out', 'p50_out', 'p90_out', 'label', 'price', 'pct_weight_below_price')}
S['delta_center_vs_r3_pct'] = S['center_post'] / R3['center_post'] - 1
json.dump(S, open(os.path.join(HERE, 'summary_r3b_core.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'compare_r3b_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'n_outcomes', 'center_pre', 'center_post', 'center_param_post', 'p10_out', 'p25_out', 'p50_out', 'p75_out', 'p90_out',
              'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'delta_center_vs_r3_pct'):
        print(f'{k}: {S[k]}', file=fo)
    print('r3:', json.dumps(S['r3'], ensure_ascii=False), file=fo)
    for n in ('w250', 'w60'):
        w = L[n]; print(f"{n} {w['window']} ADV {w['adv_med']/1e9:.2f} ty sigma {w['sigma_d']:.4f} | " + ' | '.join(f"{k}: CK {v['disc']:.3%} Q/ADV {v['q_over_adv']:.4%} calib={v['in_calib']}" for k, v in w['sizes'].items()), file=fo)
    for k, v in alt.items():
        print(f'alt {k}:', json.dumps(v, ensure_ascii=False), file=fo)
    print('r_sens_post:', json.dumps(S['r_sens_post']), file=fo)
    print('exit:', json.dumps(S['exit_discipline'], ensure_ascii=False), file=fo)
print(open(os.path.join(HERE, 'compare_r3b_out.txt')).read())
