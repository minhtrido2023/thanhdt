"""PVP recheck dot 2 (job Taylor_20261124_131351). KHONG doi mo hinh r3: import pvp_r3 tu ban khoi phuc (git archive 14ad1c925^), assert md5 LOCK + CONTROL.
Chi doi r (E15, dai Ke, +-50/100bp) va them DO NHAY D3 (len da dinh ky sau TT99 — chi phi tuan thu ngoai EBITDA). MU GIA: khong doc gia.
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_recheck.py <restore_root>/agents/Taylor/research/dd_redo_20261105"""
import hashlib, json, os, sys
BASE = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
C3 = os.path.join(BASE, 'PVP', 'calc_r3')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCKED = {'PVP/calc_r3/pvp_r3.py': 'ea8c9944b846b6fa5ac1a35468ec674a', 'PVP/calc_r3/assumptions_r3.json': '1d0b7c672690f6aa729126d70851f1b9',
          'PVP/calc/model.py': '4e89831fad57543af5990bc2e8c33658', 'PVP/calc/model_r2_out.json': 'c7b2bf794ca4a8f523b962a942addbaa',
          '_common_014127/common.py': '24943cb1a1d35d91bee6ca1fab9d7202', '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6',
          'PVP/calc_r3/pvp_r3_out.json': '3e9fc88cf203cd3f0d0b2bd47770358d'}
for p, m in LOCKED.items():
    assert md5(os.path.join(BASE, p)) == m, p
sys.path.insert(0, C3); sys.path.insert(0, os.path.join(BASE, '_shared'))
import pvp_r3 as P  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
O = json.load(open(os.path.join(C3, 'pvp_r3_out.json')))
D = json.load(open(os.path.join(BASE, 'PVP', 'SUMMARY.json')))['liq_disc_5ty']; F = 1 - D
assert abs(P.R0 - 0.135) < 1e-12
v0, w0, _ = P.grid(P.R3)
assert all(abs(a - b) < 1e-9 for a, b in zip(v0, O['outcomes_vals']))           # CONTROL tung o
c0 = P.mean(v0, w0); assert round(c0 * F) == 23099, c0 * F


def summ(cfg, rb):
    v, w, _ = P.grid(cfg, rb); q = wpct(v, w, (0.10, 0.50, 0.90))
    return dict(center=round(P.mean(v, w) * F), p10=round(q[0.10] * F), p50=round(q[0.50] * F), p90=round(q[0.90] * F))


base = summ(P.R3, 0.135); assert (base['center'], base['p10'], base['p90']) == (23099, 13799, 30338), base
rs = {}
for r in (0.123, 0.125, 0.130, 0.134, 0.135, 0.140, 0.145):
    s = summ(P.R3, r); s['d_vnd'] = s['center'] - base['center']; s['d_pct'] = round(100 * s['d_vnd'] / base['center'], 2); rs[f'{r:.3f}'] = s
# r co dinh 13,5% (bo truc r trong luoi) — tach hieu ung loi cua truc r khoi tam
fixed = summ(dict(P.R3, r_axis=[(0.0, 1.0)]), 0.135)
fixed123 = summ(dict(P.R3, r_axis=[(0.0, 1.0)]), 0.123)
# D3: len da dinh ky sau TT99. Can cu: LCTT ma 03 "du phong" 9T/25 = 53,1 ty (gan cho trich sua chua = SUY LUAN, dd_PVP_20261029/REPORT.md:73)
#  => 70,8 ty/nam truoc thue; du phong 232,9 da tru (lan len da 12 thang toi). Do nhay: chi tu nam 2 den het tuoi doi n, sau thue (TAX 20%).
M1 = P.M1; DRY_Y = 53.1 * 4 / 3


def with_dry(k):
    orig = P.parts
    def parts2(s, n, r, b, fx, cfg):
        d = orig(s, n, r, b, fx, cfg); x = k * DRY_Y * (1 - M1.TAX)
        d['dry_future'] = -(M1.annuity(x, n, r) - M1.annuity(x, 1, r)); return d
    P.parts = parts2
    try:
        return summ(P.R3, 0.135)
    finally:
        P.parts = orig


dry = {f'k{k}': with_dry(k) for k in (0.5, 1.0)}
for k in dry:
    dry[k]['d_vnd'] = dry[k]['center'] - base['center']; dry[k]['d_pct'] = round(100 * dry[k]['d_vnd'] / base['center'], 2)
out = dict(ticker='PVP', liq_disc_5ty=D, base=base, r_sens=rs, r_fixed_no_axis=dict(r135=fixed, r123=fixed123),
           d3_drydock=dict(annual_pretax_bn=round(DRY_Y, 2), basis='LCTT ma 03 9T/25 53,1 ty x4/3 (gan cho trich sua chua la suy luan)', **dry))
json.dump(out, open(os.path.join(HERE, 'calc_recheck_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False, indent=1))
