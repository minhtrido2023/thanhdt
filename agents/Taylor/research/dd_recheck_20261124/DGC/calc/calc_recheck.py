"""dd_recheck 24/11 DGC (job Taylor_20261124_095517): E15 + dai Ke + do nhay r, CUNG mo hinh r3b, CHI doi r.
Mo hinh: dd_redo_20261105/DGC/calc_r3b/model_r3b.py (+ calc/model_r3, model_r2, model; _common_014127; dgc_valuation_20261029_r12), bi TRIM khoi git.
Khoi phuc vao <root>=/tmp/ddrestore_B/agents/Taylor/research: git archive 14ad1c925^ .../dd_redo_20261105 ; 60fe58b82^ .../dgc_valuation_20261029_r12
Base r3b co truc r = r_now ±50bp (0,25/0,5/0,25). Doi r = DICH CA TRUC: C.r_now(shift) -> r_now(shift) + dr. Ngoai ra bao ban 1 diem r (khong truc) nhu r_sens cua r3b.
CK 5 ty = 0,725% (ADV250, r3b summary) giu nguyen; post = pre x (1 - CK). Chay: wc_venv python -I calc_recheck.py <root>"""
import sys, os, json, hashlib, runpy
ROOT = os.path.abspath(sys.argv[1]); RED = os.path.join(ROOT, 'dd_redo_20261105')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'dd_redo_20261105/DGC/calc_r3b/model_r3b.py': 'b1a44b72cb52b200b8bac89701bebb18', 'dd_redo_20261105/DGC/calc_r3b/model_r3b_out.json': 'a8fa8dac3439d64f3bffdfd4429fbd73',
 'dd_redo_20261105/DGC/calc/model_r3_out.json': 'ba91265ff8014116f6e4b9179a73d0fa', 'dd_redo_20261105/DGC/calc/model_r3.py': 'a6a38309532a4c146a48483eb8080519',
 'dd_redo_20261105/DGC/calc/model_r2.py': 'e951b6fde1b50cd674d22771c0bcbe48', 'dd_redo_20261105/DGC/calc/model.py': '99ff32c92d864a70220a81005aa9cf2b',
 'dd_redo_20261105/DGC/calc/model_r2_out.json': '60b495ceab994b1503a135502ac77872', 'dd_redo_20261105/_common_014127/common.py': '24943cb1a1d35d91bee6ca1fab9d7202',
 'dd_redo_20261105/_common_014127/common_r2.py': '95da3038b3710b57e66747acfcd95722', 'dd_redo_20261105/_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6',
 'dgc_valuation_20261029_r12/out_A_forecast.csv': '4edd3d973ae5e1ce28c75c59d3bd8162', 'dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md': '0e8288ee53d4fd906e56f469457ab4da',
 'dgc_valuation_20261029_r12/r9_calc.py': '7736471239b3a5e2b21ba39944ebf838'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
g = runpy.run_path(os.path.join(RED, 'DGC', 'calc_r3b', 'model_r3b.py'), run_name='r3b')   # khong chay __main__ (khong ghi de out)
grid, mean, CFG3B, C = g['grid'], g['mean'], g['CFG3B'], g['C']
sys.path.insert(0, os.path.join(RED, '_shared')); from wpct import wpct
OUT = json.load(open(os.path.join(RED, 'DGC', 'calc_r3b', 'model_r3b_out.json')))
SUMJ = json.load(open(os.path.join(RED, 'DGC', 'calc_r3b', 'summary_r3b_core.json')))
CK = SUMJ['ck_ref_size']['disc_adv250']; F = 1 - CK
r0 = C.r_now(); assert abs(r0 - 0.135) < 1e-12
_orig = C.r_now
def at(dr, axis=True):
    C.r_now = lambda beta=1.0, shift=0.0: _orig(beta, shift) + dr
    try:
        v, w = grid(CFG3B) if axis else grid(CFG3B, r_shift=0.0)
    finally:
        C.r_now = _orig
    p = wpct([x * F for x in v], w)
    return dict(center=mean(v, w) * F, center_pre=mean(v, w), p10=p[0.1], p90=p[0.9])
b = at(0.0)
assert abs(b['center_pre'] - OUT['center_pre']) < 1e-6 and round(b['center']) == 41849 and round(b['p10']) == 33272 and round(b['p90']) == 50227, b
for bp, key in ((-100, '-100bp'), (-50, '-50bp'), (50, '+50bp'), (100, '+100bp')):  # CONTROL ban 1 diem r = r_sens_pre cua r3b
    assert abs(at(bp / 1e4, axis=False)['center_pre'] - OUT['r_sens_pre'][key]) < 1e-6, key
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', 0.125), ('13,0% (-50bp)', 0.130), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', 0.135), ('14,0% (+50bp)', 0.140), ('14,5% (+100bp)', 0.145)]:
    s = at(r - r0); s1 = at(r - r0, axis=False)
    rows.append(dict(label=lab, r=r, center=round(s['center']), center_pre=round(s['center_pre']), p10=round(s['p10']), p90=round(s['p90']),
                     d_center=round(s['center'] - b['center']), d_pct=round(s['center'] / b['center'] - 1, 4), center_point_r=round(s1['center'])))
res = dict(r_base=r0, ck=CK, base=dict(center=round(b['center']), p10=round(b['p10']), p90=round(b['p90'])), rows=rows,
           note='center = truc r dich (nhat quan voi base); center_point_r = 1 diem r khong truc (cach r_sens cua r3b)')
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
