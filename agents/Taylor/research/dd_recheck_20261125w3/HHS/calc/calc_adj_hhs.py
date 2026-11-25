"""HHS E17 (25/11/2026, job Taylor_20261125_053007 resume of Taylor_20261125_032448) — MÙ GIÁ.
Lõi = calc_rev9.py (exec phần trước 'T = {}'), chỉ thêm probe s_shift (biên HTK cũ) x CK holding.
Mục đích: lượng hoá 2 killer skeptic r1 (CK 0% đầu lạc quan; biên 52% vs luật 3c) để hiển thị — CẢ HAI là tham số luật/user, KHÔNG vào Σ (PREREG_adj §1 dòng 25)."""
import os, json, hashlib
H = os.path.dirname(os.path.abspath(__file__))
src = open(H + '/calc_rev9.py').read().split('T = {}')[0]
src = src.replace("open(os.path.join(H, 'calc_rev9_out.json'), 'w')", "None")
ns = {'__file__': H + '/calc_rev9.py', '__name__': 'rev9core'}
exec(compile(src, 'calc_rev9_core', 'exec'), ns)
grid, ex, base = ns['grid'], ns['ex'], ns['base']
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
P = os.path.normpath(H + '/../../../dd_adjcenter_20261124')
assert md5(P + '/PREREG_adj.md') == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(P + '/PREREG_adj_v2.md') == '835dfc1e07f9c67ac7f6c3028b529d13'
G_OBS = (0.519 + 0.522) / 2; S_OBS = 0.8 * (G_OBS - 0.1) / (1 - G_OBS)
s_of = lambda g: 0.8 * (g - 0.1) / (1 - g)
out = {'control_base': base['center'], 's_obs': round(S_OBS, 4)}
assert base['center'] == 13969
T = {}
for gname, g in [('obs 52,05%', G_OBS), ('TB peer 37,7%', 0.377), ('TCH 29,9%', 0.299)]:
    for h in (-0.0324, 0.0, 0.197, 0.20):
        r = grid(hd_fix=h, s_shift=s_of(g) - S_OBS)
        T[f'{gname} | CK {h}'] = dict(center=r['center'], p10=r['p10'], p90=r['p90'], d_pct=round(100 * (r['center'] / base['center'] - 1), 2), ex_k1=round(ex(r['center'])))
out['grid'] = T
print(json.dumps(out, ensure_ascii=False, indent=1))
