"""HHS rev7 (23/11/2026, job Taylor_20261123_120407) — MU GIA (khong doc gia HHS; gia so sanh 9.700 BQ 20/11 ke thua rev5/rev6).
Ap CK holding DO DUOC (ck_holding_vn_20261123/calc_out.json) vao luoi r3 qua tham so hd_fix cua hhs_r3.make:
  core = HHS*c*(1-h) + OTHER + np*pe + bds*BDS_SURP*HHS*(1-h) - kq*KQ   (h chi ap phan HHS x CRV; NCI 48,85% da loai; OTHER/o to khong ap)
Bang: h = 0 / 0,2663 (base) / IQR 0,1998 & 0,3883 / nhom kiem soat 0,2406 / bo VIC 0,2921 / thanh khoan 0,4203 / truc r2 (27%, khong nguon).
Chay: python3 calc_rev7.py > run1.txt ; lan 2 > run2.txt (md5 trung)."""
import os, sys, json, hashlib
H = os.path.dirname(os.path.abspath(__file__))
R3 = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_redo_20261105/HHS/calc_r3/hhs_r3.py'
DIL = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_dilution_update_20261110/calc/dilution_out.json'
CKO = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/ck_holding_vn_20261123/calc_out.json'
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(R3) == 'cf5420d86989f25b4070697b38347c52'
assert md5(DIL) == '0450ba0aee972c6c4ec97847fe2de68c'
assert md5(CKO) == 'e78cc0d9a934add02fcb796f1d06ce0d'
A = json.load(open(os.path.join(H, 'assumptions.json')))
ck = json.load(open(CKO)); g0 = ck['groups'][0]
assert abs(g0['median'] - A['holding_discount']['base']) < 1e-4, (g0['median'], A['holding_discount']['base'])
src = open(R3).read(); core = src.split('# ---- CONTROL')[0]
ns = {'__file__': R3, '__name__': 'r3core'}
exec(compile(core, R3, 'exec'), ns)
R2C, make, HEAD = ns['R2C'], ns['make'], ns['HEAD']
d5 = json.load(open(DIL))['HHS']['inputs']['d5']
PX_REF = 9700.0   # BQ 20/11/2026 ke thua (rev5 post_lock_out.json) — chi dung SAU khi tinh, de gan nhan
N0, NR, CASH, DIV = 431_985_968, 259_191_580, 259_191_580 * 10_000, 0.07


def grid(cfg=HEAD, **fkw):
    ax, fn = make(cfg)
    res = R2C.outcomes(ax, lambda **a: fn(**a, **fkw))
    pre = R2C.stats(res, 0.0, 0.0); post = R2C.stats(res, 0.0, d5)
    k = ('center', 'p10', 'p50', 'p90')
    return {**{q + '_pre': round(pre[q]) for q in k}, **{q: round(post[q]) for q in k}, 'n': pre['n']}


def label(g, px=PX_REF):
    return 'DUOI vung' if px < g['p10'] else ('TREN vung' if px > g['p90'] else 'TRONG vung')


def ex(V, k):   # EX du 100% quyen, cong thuc rev5 §3 (c=1)
    return (V * N0 + (1 - d5) * k * CASH) / (N0 + NR) / (1 + DIV)


out = {'d5': d5, 'px_ref': PX_REF, 'ck_source_md5': md5(CKO)}
base0 = grid(); assert (base0['center_pre'], base0['center'], base0['p10'], base0['p90']) == (14169, 13969, 12422, 15564), base0
# phan NAV chiu CK holding (tai luoi trung tam): chenh lech h=0 vs h=1
g1 = grid(hd_fix=1.0)
out['exposed_share_of_nav_pre'] = round(1 - g1['center_pre'] / base0['center_pre'], 4)
cases = {'h=0 (rev6 headline, khong nguon)': dict(hd_fix=0.0),
         'h=0,2663 BASE rev7 (trung vi N=6)': dict(hd_fix=0.2663),
         'h=0,1998 (IQR thap)': dict(hd_fix=0.1998),
         'h=0,3883 (IQR cao)': dict(hd_fix=0.3883),
         'h=0,2406 (nhom kiem soat N=5)': dict(hd_fix=0.2406),
         'h=0,2921 (bo VIC N=5)': dict(hd_fix=0.2921),
         'h=0,4203 (do phu thanh khoan N=3)': dict(hd_fix=0.4203)}
T = {}
for name, kw in cases.items():
    g = grid(**kw); h = kw['hd_fix']
    g['label'] = label(g); g['rule4_threshold'] = round(0.85 * g['center']); g['rule4_pass'] = PX_REF <= 0.85 * g['center']
    g['ex_k1'] = round(ex(g['center'], 1.0)); g['ex_k_1_minus_h'] = round(ex(g['center'], 1 - h))
    g['ex_p10_k_1_minus_h'] = round(ex(g['p10'], 1 - h)); g['ex_p90_k_1_minus_h'] = round(ex(g['p90'], 1 - h))
    T[name] = g
# truc r2 (song song rev6, khong nguon)
gr2 = grid(cfg=dict(HEAD, hd=True)); gr2['label'] = label(gr2); gr2['rule4_threshold'] = round(0.85 * gr2['center'])
T['truc r2 0/15/25/35/45% (ky vong 27%, KHONG nguon)'] = gr2
# do nhay: CK ap len TOAN BO NAV HHS (khong chi phan CRV) — thuoc dinh nghia CK do (1 - MV/SOTP toan bo)
full = {k: round(v * (1 - 0.2663)) for k, v in base0.items() if k in ('center', 'p10', 'p50', 'p90')}
full['label'] = label(full); T['do nhay: h=0,2663 ap TOAN BO NAV'] = full
out['table'] = T
s = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True)
open(os.path.join(H, 'calc_rev7_out.json'), 'w').write(s)
print(s)
