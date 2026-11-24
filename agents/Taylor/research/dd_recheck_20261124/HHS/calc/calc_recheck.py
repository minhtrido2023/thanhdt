"""HHS recheck 24/11/2026 (job Taylor_20261124_094353) — MU GIA, khong doc gia.
Tai dung NGUYEN lua rev7 (calc_rev7.py: luoi r3 + hd_fix=0,2663), CHI doi r (E15, D4 dai Ke, V1 +-50/100bp).
Khong doi bat ky tham so khoa nao cua rev7 (assumptions md5 3afcd113...).
Chay: python3 calc_recheck.py > run1.txt ; lan 2 > run2.txt (md5 trung)."""
import os, json, hashlib
H = os.path.dirname(os.path.abspath(__file__))
M = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research'
R3 = M + '/dd_redo_20261105/HHS/calc_r3/hhs_r3.py'
DIL = M + '/dd_dilution_update_20261110/calc/dilution_out.json'
A7 = M + '/dd_dilution_update_20261110/HHS/rev7/calc/assumptions.json'
O7 = M + '/dd_dilution_update_20261110/HHS/rev7/calc/calc_rev7_out.json'
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(R3) == 'cf5420d86989f25b4070697b38347c52'
assert md5(DIL) == '0450ba0aee972c6c4ec97847fe2de68c'
assert md5(A7) == '3afcd113013fad82acfa5ea35c5bce1d'
assert md5(O7) == 'b7d912f6062f59a6ef08ece9a7f92264'
src = open(R3).read(); core = src.split('# ---- CONTROL')[0]
ns = {'__file__': R3, '__name__': 'r3core'}
exec(compile(core, R3, 'exec'), ns)
R2C, make, HEAD, R = ns['R2C'], ns['make'], ns['HEAD'], ns['R']
assert abs(R - 0.135) < 1e-12, R
d5 = json.load(open(DIL))['HHS']['inputs']['d5']
N0, NR, CASH, DIV = 431_985_968, 259_191_580, 259_191_580 * 10_000, 0.07
H_BASE = json.load(open(A7))['holding_discount']['base']; assert H_BASE == 0.2663


def grid(**fkw):
    ax, fn = make(HEAD)
    res = R2C.outcomes(ax, lambda **a: fn(**a, **fkw))
    pre = R2C.stats(res, 0.0, 0.0); post = R2C.stats(res, 0.0, d5)
    k = ('center', 'p10', 'p50', 'p90')
    return {**{q + '_pre': round(pre[q]) for q in k}, **{q: round(post[q]) for q in k}, 'n': pre['n']}


def ex(V, k):
    return (V * N0 + (1 - d5) * k * CASH) / (N0 + NR) / (1 + DIV)


out = {'d5': d5, 'r_base': R, 'h_base': H_BASE}
base = grid(hd_fix=H_BASE)
rev7 = json.load(open(O7))['table']['h=0,2663 BASE rev7 (trung vi N=6)']
for q in ('center', 'p10', 'p50', 'p90', 'center_pre'):
    assert base[q] == rev7[q], (q, base[q], rev7[q])   # CONTROL: tai lap rev7 dung tung dong
out['control_rev7_reproduced'] = True
T = {}
for name, r in [('r=12,3% (E15 / dau duoi dai Ke)', 0.123), ('r=13,4% (dau tren dai Ke)', 0.134),
                ('r=12,5% (-100bp)', 0.125), ('r=13,0% (-50bp)', 0.130), ('r=13,5% BASE', 0.135),
                ('r=14,0% (+50bp)', 0.140), ('r=14,5% (+100bp)', 0.145)]:
    g = grid(hd_fix=H_BASE, r=r)
    g['d_center_vs_base_pct'] = round(100 * (g['center'] / base['center'] - 1), 2)
    g['d_center_vnd'] = g['center'] - base['center']
    g['ex_k1_center'] = round(ex(g['center'], 1.0)); g['ex_k734_center'] = round(ex(g['center'], 1 - H_BASE))
    g['ex_k734_p10'] = round(ex(g['p10'], 1 - H_BASE)); g['ex_k734_p90'] = round(ex(g['p90'], 1 - H_BASE))
    T[name] = g
# do nhay r cho headline doi chieu CK 0% (rev6) — de nguoi doc thay E15 khong phu thuoc CK
g0 = grid(hd_fix=0.0); g0r = grid(hd_fix=0.0, r=0.123)
T['doi chieu CK 0%: r=12,3%'] = {**g0r, 'd_center_vs_ck0_base_pct': round(100 * (g0r['center'] / g0['center'] - 1), 2), 'ck0_base_center': g0['center']}
# doi chieu CK v5 (ck_holding_vn_20261124_v5: moc hien tai 20/11 = 19,7%; trung vi N=12 = -3,24% ~ 0%) — CHI HIEN THI, khong doi base
for h in (0.197,):
    for r in (0.135, 0.123):
        T[f'doi chieu CK v5 hien tai {h}: r={r}'] = grid(hd_fix=h, r=r)
out['table'] = T
# V6 V_ngan (chi hien thi): LNST chuan hoa 260,5 ty / r, g=0 (rev5 §4)
out['v6_v_short_cum'] = {f'{r:.3f}': round(260.5e9 / r / N0) for r in (0.123, 0.135)}
s = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True)
open(os.path.join(H, 'calc_recheck_out.json'), 'w').write(s)
print(s)
