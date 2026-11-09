"""Bang buoc errata r2: chay model_bsr.py tren cac to hop sua doi tu assumptions_r1.json. Ghi errata_steps.json"""
import json, os, subprocess, copy, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); PY = '/home/trido/thanhdt/wc_venv/bin/python'
R1 = json.load(open(os.path.join(HERE, 'assumptions_r1.json'))); R2 = json.load(open(os.path.join(HERE, 'assumptions.json')))
def build(e1=None, e2=False, e4=False):
    A = copy.deepcopy(R1)
    A['expansion_booked_bn'] = {'adv_engineering_TM7': 0.0, 'lt_prepaid_212_BQL_KKT_Dung_Quat': 0.0}; A['mbv_blocked'] = R2['mbv_blocked']
    A['bs_bn']['bonus_welfare_fund_323'] = 0.0; A['bs_bn']['nci_429'] = 0.0
    if e1:
        for k in ('XAU', 'CO_SO', 'TOT'): A['core_nopat_bn'][k] += {'B': 463.0, 'A': 865.0}[e1]
    if e2:
        A['expansion_booked_bn'] = {'adv_engineering_TM7': 2601.2, 'lt_prepaid_212_BQL_KKT_Dung_Quat': 546.3}
        A['wc_bn']['now']['prepay_132'] = round(A['wc_bn']['now']['prepay_132'] - 2601.2, 3)
    if e4: A['bs_bn']['bonus_welfare_fund_323'] = 441.6; A['bs_bn']['nci_429'] = 32.0
    return A
def run(name, A, mbv=False):
    d = tempfile.mkdtemp(); f = os.path.join(d, 'a.json'); o = os.path.join(d, 'o.json'); json.dump(A, open(f, 'w'), indent=1)
    env = dict(os.environ, BSR_ASSUMP=f, BSR_OUT=o, BSR_MBV_LOSS='1' if mbv else '0')
    subprocess.run([PY, '-I', os.path.join(HERE, 'model_bsr.py')], env=env, check=True, capture_output=True)
    O = json.load(open(o))['post']; return dict(name=name, center=round(O['center']), p10=round(O['p10']), p90=round(O['p90']), pct_below=O['pct_below_px'])
S = [run('r1 (cong bo)', build()),
     run('E1-B rieng (boc ty gia, loi lam 3.493)', build('B')), run('E1-A rieng (giu ty gia, loi lam 3.895)', build('A')),
     run('E2 rieng (mo rong 100% gia so)', build(e2=True)), run('E4 rieng (tru quy KTPL + NCI)', build(e4=True)),
     run('E3 rieng (MBV mat trang, do nhay)', build(), mbv=True),
     run('luy ke +E2', build(e2=True)), run('luy ke +E2+E4', build(e2=True, e4=True)),
     run('luy ke +E2+E4+E1-B = rev2 HEADLINE', build('B', True, True)),
     run('rev2 bien the A (giu ty gia)', build('A', True, True)),
     run('rev2 B + MBV mat trang', build('B', True, True), mbv=True), run('rev2 A + MBV mat trang', build('A', True, True), mbv=True)]
json.dump(S, open(os.path.join(HERE, 'errata_steps.json'), 'w'), indent=1, ensure_ascii=False)
for s in S: print(f"{s['name']:45s} {s['center']:>7,} {s['p10']:>7,} {s['p90']:>7,}  <gia {s['pct_below']:.1%}")
