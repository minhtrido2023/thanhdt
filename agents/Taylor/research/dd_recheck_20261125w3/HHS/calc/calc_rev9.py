"""HHS rev9 (25/11/2026, job Taylor_20261125_032448) — MÙ GIÁ, không đọc giá.
Tái dùng NGUYÊN lưới r3 của rev7 (hhs_r3.py, dilution_out.json), CHỈ đổi CK holding base 0,2663 → 0 (assumptions_rev9.json, LOCK_md5.txt).
CONTROL: h=0,2663 tái lập rev7 (10.805); h=0 tái lập headline rev6 (13.969). Chạy: python3 calc_rev9.py > run1.txt; lần 2 > run2.txt."""
import os, json, hashlib
H = os.path.dirname(os.path.abspath(__file__))
M = os.path.normpath(os.path.join(H, '../../..'))
R3 = M + '/dd_redo_20261105/HHS/calc_r3/hhs_r3.py'
DIL = M + '/dd_dilution_update_20261110/calc/dilution_out.json'
A9 = H + '/assumptions_rev9.json'
O7 = M + '/dd_dilution_update_20261110/HHS/rev7/calc/calc_rev7_out.json'
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(R3) == 'cf5420d86989f25b4070697b38347c52'
assert md5(DIL) == '0450ba0aee972c6c4ec97847fe2de68c'
assert md5(O7) == 'b7d912f6062f59a6ef08ece9a7f92264'
assert md5(A9) == open(H + '/LOCK_md5.txt').read().split()[-2], 'assumptions_rev9 lệch LOCK'
src = open(R3).read(); core = src.split('# ---- CONTROL')[0]
ns = {'__file__': R3, '__name__': 'r3core'}
exec(compile(core, R3, 'exec'), ns)
R2C, make, HEAD, R = ns['R2C'], ns['make'], ns['HEAD'], ns['R']
assert abs(R - 0.135) < 1e-12
d5 = json.load(open(DIL))['HHS']['inputs']['d5']
N0, NR, CASH, DIV = 431_985_968, 259_191_580, 259_191_580 * 10_000, 0.07
A = json.load(open(A9)); H_BASE = A['holding_discount']['base']; K = A['k_base']; assert H_BASE == 0.0 and K == 1.0

def grid(**fkw):
    ax, fn = make(HEAD)
    res = R2C.outcomes(ax, lambda **a: fn(**a, **fkw))
    pre = R2C.stats(res, 0.0, 0.0); post = R2C.stats(res, 0.0, d5)
    k = ('center', 'p10', 'p50', 'p90')
    return {**{q + '_pre': round(pre[q]) for q in k}, **{q: round(post[q]) for q in k}, 'n': pre['n']}
def ex(V, k=K): return (V * N0 + (1 - d5) * k * CASH) / (N0 + NR) / (1 + DIV)

out = {'d5': d5, 'r_base': R, 'h_base': H_BASE, 'k_base': K}
rev7 = json.load(open(O7))['table']['h=0,2663 BASE rev7 (trung vi N=6)']
c7 = grid(hd_fix=0.2663)
for q in ('center', 'p10', 'p50', 'p90', 'center_pre'): assert c7[q] == rev7[q], (q, c7[q], rev7[q])
base = grid(hd_fix=H_BASE)
assert (base['center'], base['p10'], base['p90']) == (13969, 12422, 15564), base   # = headline rev6 (REPORT_rev7 bảng §0)
out['control'] = {'rev7_h02663': c7['center'], 'rev6_h0': base['center']}
out['base'] = {**base, 'ex_center': round(ex(base['center'])), 'ex_p10': round(ex(base['p10'])), 'ex_p90': round(ex(base['p90']))}
T = {}
for name, r in [('r=12,3% (E15 / đầu dưới dải Ke)', 0.123), ('r=12,5% (-100bp)', 0.125), ('r=13,0% (-50bp)', 0.130), ('r=13,4% (đầu trên dải Ke)', 0.134),
                ('r=14,0% (+50bp)', 0.140), ('r=14,5% (+100bp)', 0.145)]:
    g = grid(hd_fix=H_BASE, r=r); g['d_vnd'] = g['center'] - base['center']; g['d_pct'] = round(100 * (g['center'] / base['center'] - 1), 2)
    g['ex_center'] = round(ex(g['center'])); T[name] = g
out['r_sens'] = T
B = {}
for h in (0.20, 0.197, 0.2663, 0.377):
    g = grid(hd_fix=h); g['d_pct'] = round(100 * (g['center'] / base['center'] - 1), 2)
    g['ex_center_k1'] = round(ex(g['center'], 1.0)); g['ex_center_k1mh'] = round(ex(g['center'], 1 - h)); B[f'h={h}'] = g
out['display_band_ck'] = B
out['v6_v_short_cum'] = {f'{r:.3f}': round(260.5e9 / r / N0) for r in (0.123, 0.135)}
s = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True)
open(os.path.join(H, 'calc_rev9_out.json'), 'w').write(s); print(s)
