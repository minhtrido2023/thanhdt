"""SAU KHOA: doc <TK>/calc/model_out.json (+ LOCK_md5.txt phai khop) -> gia 04/11 + thanh khoan (common.liquidity) -> <TK>/SUMMARY.json + calc/compare_out.txt.
Chay: $DNA_PYEXE -I compare.py <TK>"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
tk = sys.argv[1]; base = os.path.join(os.path.dirname(C.HERE), tk); calc = os.path.join(base, 'calc')
mo = os.path.join(calc, 'model_out.json')
lock = open(os.path.join(calc, 'LOCK_md5.txt')).read().split()[0]
assert hashlib.md5(open(mo, 'rb').read()).hexdigest() == lock, 'model_out.json doi sau khoa'
M = json.load(open(mo))
L = C.liquidity(tk, M['free_float'], M['free_float_src'])
assert L['last_date'] == C.ASOF, L['last_date']
S = C.summarize(tk, L['last_date'], L['last_price'], M['center_pre'], M['grid_vals'], M['grid_wts'], L, M['grid_desc'])
Z = [e for e in json.load(open(os.path.join(C.WC, 'mike/kb/dd_price_zones.json')))['entries'] if e['ticker'] == tk]
z = Z[-1] if Z else None
S['zone_old'] = dict(low=z['zone_low'], center=z['center'], high=z['zone_high'], dd_date=z['dd_date'], center_kind=z['center_kind']) if z else None
ai = C.anchor_info(); S['r'] = ai['r']; S['r_anchor'] = dict(rate=ai['r_anchor']['rate'], date=ai['r_anchor']['date'], source=ai['r_anchor']['source'], r_at_anchor=C.R_ANCHOR)
f = 1 - L['d_label']
S['r_sens_post'] = {k: round(v * f) for k, v in M['r_sens_pre'].items()}
S['r_sens_pre'] = M['r_sens_pre']
S['scenarios_pre'] = M['scenarios_pre']
S['liquidity'] = L
old_c = (z['center'] if z and z['center'] else ((z['zone_low'] + z['zone_high']) / 2 if z else None))
S['old_ref'] = old_c; S['old_ref_kind'] = 'center' if (z and z['center']) else 'zone_midpoint'
S['delta_vs_old_pct'] = (S['center_post_liq'] / old_c - 1) if old_c else None
for k in ('change_reason', 'warnings', 'open_issues'):
    S[k] = M[k]
json.dump(S, open(os.path.join(base, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(calc, 'compare_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'center_pre_liq', 'center_post_liq', 'p10_pre', 'p50_pre', 'p90_pre', 'p10_post', 'p25_post', 'p50_post', 'p75_post', 'p90_post',
              'liq_disc_5ty', 'px_vs_center_post', 'px_vs_p10_post', 'px_vs_p90_post', 'label', 'old_ref', 'old_ref_kind', 'delta_vs_old_pct', 'grid_n'):
        print(f'{k}: {S[k]}', file=fo)
    print('liquidity:', json.dumps({k: v for k, v in L.items() if k != 'pos'}, ensure_ascii=False), file=fo)
    for q, p in L['pos'].items():
        print(f'  vi the {q} ty: CK Y0.5/1.0/1.5 = ' + '/'.join(f'{p["disc"][y]:.2%}' for y in ('Y0.5', 'Y1.0', 'Y1.5')) +
              ' | phien thoat 10/15/20% = ' + '/'.join(f'{p["days"][d]:.1f}' for d in ('p10', 'p15', 'p20')) + f' | Amihud@15% {p["amihud_day15"]:.2%}', file=fo)
    print('r_sens_post:', json.dumps(S['r_sens_post']), file=fo)
print(open(os.path.join(calc, 'compare_out.txt')).read())
