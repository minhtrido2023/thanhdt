"""DD redo NNC VONG 2 (05/11/2026, job Taylor_20261105_020023). Chay: $DNA_PYEXE -B nnc_redo_r2.py (tu thu muc calc nay).
Mo hinh = nnc_model_r6 (-> r5 -> r4 -> r3 -> MVC r6) IMPORT, KHONG SUA. Vong 2 theo STANDARD_r2.md + E_CORRECTIONS.md:
 (1) MUC KET CUC: moi o -> 8 ket cuc (4 kich ban W0 x 2 duong gia PW0), trong so = w_o x W0[k] x PW0[p]; phan vi bang _shared/wpct.py.
     (Truc tron PW 70/30-50/50-30/70 deu trong so = PW0 50/50 tren cung gia tri ket cuc => gop, khong lam doi phan phoi.)
 (2) LUOI DOI XUNG: trang thai bien (Bobby 0,20/0,45/0,35) x K {0,87;0,97;1,07} x SL VRs 3 x ADMIN {perm05,ramp,full}
     x TRAN CHU KY {branch, SL 1,40} (dua lai, truoc bi loai 'chi chieu xuong') x THUE NUI NHO {toi 2043, toi 2030, khong} (deu) [UL].
 (3) BASE NPV0 that: bo chi phi tre GP ky vong (Bobby F6, chi la nhan dinh) cho CA CIP Tam Lap 1 khu II (cip_delay) VA mo moi MVC (delay)
     -> do nhay rieng. Ban 'co tre' bao song song.
 (4) Thanh khoan: CK o 5 ty (tham chieu, Q/ADV250 = 2,4x) VA cO sleeve that 10/40 trieu; ADV250 va ADV60.
"""
import os, sys, json, itertools, csv
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
R6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
sys.path.insert(0, R6D); _cwd = os.getcwd(); os.chdir(R6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd)
import numpy as np  # noqa: E402

dep, dep_src = C.dep_now(); R = C.r_of(dep); N6.R_ANCHOR = R
N5, N4, N3, S = N6.N5, N6.N4, N6.N3, N6.S
CW = N6.CW_BOBBY; SCN, PATHS, W0, PW0 = N5.SCN, N5.PATHS, N5.W0, N5.PW0
NODELAY = dict(cip_delay=False, delay=False)
q = 1 + R
pvf = {y: 1.03 ** (y - 2026) / q ** (y - 2026) for y in range(2027, 2044)}
FR_RENT_POST2030 = sum(v for y, v in pvf.items() if y >= 2031) / sum(pvf.values())   # xap xi nhu r6 (dong thue tuyen tinh trong EBIT)


def branch_res(name, over, v_rev, cap_basis, admin):
    """Ban sao logic N5.branch nhung tra ve res 8 ket cuc (k, path) -> V_NNC_ps, V_MVC."""
    o = dict(over)
    if name == 'STRUCTURAL':
        o.update(stress=0.0, nnc_vol=(1.40, 1.40), ramp=False); cap = S.P_CYC
    else:
        st, rp = N5.ADMIN[admin] if name == 'ADMIN_GATED' else (1.0, False)
        o.update(stress=st, ramp=rp, nnc_vol=v_rev)
        o.setdefault('tl_vol', v_rev)
        cap = N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else 1.40)
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, res = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return vn, {(k, p): res[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS}


# kiem doi chung: branch_res tai lap N5.branch
for n in CW:
    a = N5.branch(n, {}); b_, _ = branch_res(n, {}, N5.V_REV, 'branch', 'ramp')
    assert abs(a[0] - b_) < 1e-6, (n, a, b_)

out = dict(ticker='NNC', dep=dep, dep_src=dep_src, r=R, fr_rent_post2030=FR_RENT_POST2030)
out['center_param_withdelay'] = N6.EV5()            # = pin r6 60.702 (co tre)
out['center_param_nodelay'] = N6.EV5(NODELAY)      # gia tri tai tham so trung tam, NPV0 that

RENT_AX = ('2043', '2030', 'none'); CAP_AX = ('branch', '1.40')
rows = []
for n, k, vi, am, cb in itertools.product(CW, (0.87, 0.97, 1.07), range(3), N5.AMs, CAP_AX):
    _, rT = branch_res(n, {'K': k, **NODELAY}, N5.VRs[vi], cb, am)
    _, rF = branch_res(n, {'K': k, 'rent': False, **NODELAY}, N5.VRs[vi], cb, am)
    for ra in RENT_AX:
        wc = CW[n] / (3 * 3 * 3 * 2 * 3)
        for kp in rT:
            v = rT[kp] if ra == '2043' else (rF[kp] if ra == 'none' else rT[kp] - FR_RENT_POST2030 * (rT[kp] - rF[kp]))
            rows.append(dict(branch=n, K=k, VR=vi, admin=am, cap=cb, rent=ra, scn=kp[0], path=kp[1],
                             w=wc * W0[kp[0]] * PW0[kp[1]], V=v))
v = np.array([r['V'] for r in rows]); w = np.array([r['w'] for r in rows])
assert abs(w.sum() - 1) < 1e-9


def stats(mask=None, f=1.0):
    vv, ww = (v, w) if mask is None else (v[mask], w[mask])
    p = wpct(vv * f, ww)
    return dict(n=int(len(vv)), mean=float((vv * ww).sum() / ww.sum() * f), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(vv.min() * f), max=float(vv.max() * f))


out['n_outcomes'] = len(rows); out['n_cells'] = len(rows) // 8
out['pre'] = stats()
cap_b = np.array([r['cap'] == 'branch' for r in rows]); rent43 = np.array([r['rent'] == '2043' for r in rows])
out['pre_r1axes_only'] = stats(cap_b & rent43)                 # = luoi vong 1 (khong cap, thue 2043) o muc ket cuc, khong tre
out['pre_no_cap_axis'] = stats(cap_b)
out['pre_no_rent_axis'] = stats(rent43)
out['branch_pre'] = {n: stats(np.array([r['branch'] == n for r in rows])) for n in CW}
# nhay trong so STRUCTURAL (P90 = vung nhanh STRUCTURAL?)
sens_w = {}
for ws in (0.10, 0.15, 0.20, 0.30):
    rest = 1 - ws; scale = {'STRUCTURAL': ws / CW['STRUCTURAL'], 'ADMIN_GATED': rest * 0.45 / 0.80 / CW['ADMIN_GATED'], 'CYCLICAL': rest * 0.35 / 0.80 / CW['CYCLICAL']}
    ww = w * np.array([scale[r['branch']] for r in rows]); p = wpct(v, ww)
    sens_w[f'{ws:.2f}'] = dict(mean=float((v * ww).sum() / ww.sum()), p10=p[0.1], p50=p[0.5], p90=p[0.9])
out['sens_w_structural_pre'] = sens_w

# do nhay don (tam tham so, khong tre)
c0 = out['center_param_nodelay']; T = {}
def t(lab, over=None, **kw): x = N6.EV5({**NODELAY, **(over or {})}, **kw); T[lab] = dict(V=x, d=x - c0)
t('co tre GP ky vong (Bobby F6) CA CIP Tam Lap + mo MVC', {'cip_delay': True, 'delay': True})
t('chi tre CIP Tam Lap 1 khu II', {'cip_delay': True}); t('chi tre mo moi MVC', {'delay': True})
t('tran SL 1,40', cap_basis='1.40'); t('ADMIN perm05', admin='perm05'); t('ADMIN full', admin='full')
t('bo thue Nui Nho', {'rent': False})
T['thue Nui Nho toi 2030 (xap xi PV)'] = dict(d=FR_RENT_POST2030 * T['bo thue Nui Nho']['d']); T['thue Nui Nho toi 2030 (xap xi PV)']['V'] = c0 + T['thue Nui Nho toi 2030 (xap xi PV)']['d']
pp = sum(12.8 / q ** (i + 0.5) for i in range(4)) + 0.6 * 12.8 / q ** 4.5
t('(+) tra truoc CNBP 59,2 la tien thue da tra (CHUA XAC MINH)', {'extra': pp})
t('(+) doi thu het GP tu 2034', {'up2034': True}); t('STRESS duong gia danh nghia phang', {'PW': {'flat': 1.0}})
out['tornado'] = T
cip_delay_vnd = (N6.EV5({**NODELAY, 'cip_delay': True}) - c0)
out['base_adj_cip_delay_removed'] = -cip_delay_vnd

# thanh khoan
L = C.liquidity('NNC', ff=0.363, qs=(0.01e9, 0.04e9, 1e9, 5e9)); out['liq'] = L
d_ref = L['pos']['5']['disc']['Y1.0']; f = 1 - d_ref
import math  # noqa: E402
out['ck_real_sleeve'] = {f'{qq/1e6:.0f}tr': dict(adv250=L['sigma_d'] * math.sqrt(qq / L['adv_med']), adv60=L['sigma_d'] * math.sqrt(qq / L['adv_60'])) for qq in (0.01e9, 0.04e9)}
out['ck_ref'] = dict(size_bn=5, Y=1.0, adv250=d_ref, adv60=L['d_ref_adv60'], q_over_adv250=5e9 / L['adv_med'], q_over_adv60=5e9 / L['adv_60'])
px = L['price']; out['price'] = px; out['price_date'] = L['price_date']
out['post'] = stats(f=f); out['post_r1axes_only'] = stats(cap_b & rent43, f=f)
out['center_post'] = out['post']['mean']; out['center_pre'] = out['pre']['mean']
out['pct_weight_below_price'] = weight_below(v * f, w, px)
out['pct_weight_below_price_pre'] = weight_below(v, w, px)
out['px_vs_center_post'] = px / out['center_post'] - 1
out['px_vs_p10_post'] = px / out['post']['p10'] - 1; out['px_vs_p90_post'] = px / out['post']['p90'] - 1
out['label'] = C.label(px, out['post']['p10'], out['post']['p90'])
out['rule4_px_below_center_15pct'] = bool(px <= 0.85 * out['center_post'])
out['center_param_nodelay_post'] = c0 * f
# kiem toan: lai so skeptic (muc ket cuc, luoi vong 1 CO tre, 1.944)
sk = []
for n, k, vi, am in itertools.product(CW, (0.87, 0.97, 1.07), range(3), N5.AMs):
    _, rr = branch_res(n, {'K': k}, N5.VRs[vi], 'branch', am)
    for kp, x in rr.items(): sk.append((x, CW[n] / 27 * W0[kp[0]] * PW0[kp[1]]))
skv = np.array([a for a, _ in sk]); skw = np.array([b for _, b in sk]); p = wpct(skv * f, skw)
out['audit_skeptic_1944'] = dict(n=len(sk), p10=p[0.1], p50=p[0.5], p90=p[0.9], below=weight_below(skv * f, skw, px))
g6 = json.load(open(os.path.join(R6D, 'nnc_model_r6_out.json')))
out['gordon'] = dict(roe_lock=g6['gordon']['tron_roe_lock'], roe_fin=g6['gordon']['tron_roe_fin'], roe_implied_center_pre=N6.G + out['center_pre'] / N3.BVPS_NNC * (R - N6.G))

json.dump(out, open(os.path.join(HERE, 'nnc_redo_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
with open(os.path.join(HERE, 'grid_nnc_redo_r2.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader()
    for r in rows: wr.writerow({**r, 'w': f"{r['w']:.12g}", 'V': f"{r['V']:.4f}"})


def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} max {s['max']:,.0f} (n {s['n']})"


print(f"NNC r2 | dep {dep:.2%} -> r {R:.2%} | tam tham so co tre {out['center_param_withdelay']:,.0f} / KHONG tre {c0:,.0f} (CIP delay {cip_delay_vnd:+,.0f})")
print('  TRUOC CK ' + fm(out['pre'])); print('   [luoi vong-1 truc, muc ket cuc, khong tre] ' + fm(out['pre_r1axes_only']))
print('   [bo truc cap] ' + fm(out['pre_no_cap_axis'])); print('   [bo truc thue] ' + fm(out['pre_no_rent_axis']))
for n, s in out['branch_pre'].items(): print(f'   {n:11s} ' + fm(s))
for k_, s in sens_w.items(): print(f"   w_STRUCT {k_}: tam {s['mean']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f}")
for k_, s in T.items(): print(f"   {k_:60s} {s['V']:8,.0f} ({s['d']:+,.0f})")
print(f"  CK ref 5 ty: ADV250 {L['adv_med']/1e9:.2f} ty -> {d_ref:.2%} (Q/ADV {out['ck_ref']['q_over_adv250']:.1f}x) | ADV60 {L['adv_60']/1e9:.2f} ty -> {L['d_ref_adv60']:.2%} | sleeve {out['ck_real_sleeve']}")
print('  SAU CK ' + fm(out['post']))
print(f"  gia {px:,.0f} ({L['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | {out['label']} | trong so duoi gia {out['pct_weight_below_price']:.1%} | luat4 (gia<=0,85 tam) {out['rule4_px_below_center_15pct']}")
print(f"  audit skeptic 1.944 (co tre, sau CK): P10 {out['audit_skeptic_1944']['p10']:,.0f} P50 {out['audit_skeptic_1944']['p50']:,.0f} P90 {out['audit_skeptic_1944']['p90']:,.0f} duoi gia {out['audit_skeptic_1944']['below']:.1%}")
print(f"  Gordon ROE khoa {out['gordon']['roe_lock']['ps']:,.0f} / +LN tai chinh {out['gordon']['roe_fin']['ps']:,.0f} | ROE ham y tam {out['gordon']['roe_implied_center_pre']:.1%}")
