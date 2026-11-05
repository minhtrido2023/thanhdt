"""Sinh SUMMARY.json tu calc/model_out.json + calc/meta.json + kb/dd_price_zones.json (zone cu, chi DOC). 0 hardcode so.
Chay: $DNA_PYEXE -B summary.py <TICKER>"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); tk = sys.argv[1]
base = os.path.join(HERE, '..', tk)
M = json.load(open(os.path.join(base, 'calc', 'model_out.json'))); meta = json.load(open(os.path.join(base, 'calc', 'meta.json')))
Z = [e for e in json.load(open('/home/trido/thanhdt/WorkingClaude/mike/kb/dd_price_zones.json'))['entries'] if e['ticker'] == tk]
z = sorted(Z, key=lambda e: (e['dd_date'], e.get('recorded_at', '')))[-1] if Z else {}
pick = [e for e in Z if e.get('center_kind') == 'expected_weighted'] or Z
z = sorted(pick, key=lambda e: (e['dd_date'], e.get('recorded_at', '')))[-1] if pick else {}
S = dict(ticker=tk, asof_price_date=M['price_date'], price=M['price'], r=M['r'],
         r_anchor=dict(rate=0.074, date='2026-11-03', source='effective_deposit_rate = max(Big-4 12M 6,8%, CCTG 12M 7,4% ngay 02/11/2026); r neo 13,5%'),
         dep_now=dict(rate=M['dep'], source=M['dep_src']),
         center_pre_liq=M['center_pre'], center_post_liq=M['center_post'],
         p10_post=M['grid_post']['P10'], p50_post=M['grid_post']['P50'], p90_post=M['grid_post']['P90'],
         p10_pre=M['grid_pre']['P10'], p50_pre=M['grid_pre']['P50'], p90_pre=M['grid_pre']['P90'],
         liq_discount_ref=M['liq']['disc_ref'], liq_ref_position_bn_vnd=5, adv_med_bn_vnd=M['liq']['adv_med_vnd'] / 1e9,
         grid_n=M['grid_n'], grid_desc=meta['grid_desc'], label=M['label'],
         px_vs_center=M['price'] / M['center_post'] - 1, px_vs_p10=M['price'] / M['grid_post']['P10'] - 1, px_vs_p90=M['price'] / M['grid_post']['P90'] - 1,
         zone_old=dict(low=z.get('zone_low'), center=z.get('center'), high=z.get('zone_high'), dd_date=z.get('dd_date'), center_kind=z.get('center_kind')),
         center_change_vs_old=(M['center_post'] / z['center'] - 1) if z.get('center') else None,
         change_reason=meta['change_reason'], warnings=meta['warnings'], open_issues=meta['open_issues'],
         sources=dict(model='calc/model.py -> calc/model_out.json/txt', liq='_common/liq.py + _common/bq_px_4ma_20261104.csv'))
json.dump(S, open(os.path.join(base, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(json.dumps({k: S[k] for k in ('ticker', 'price', 'center_pre_liq', 'center_post_liq', 'p10_post', 'p50_post', 'p90_post', 'label', 'px_vs_center', 'center_change_vs_old')}, default=float))
