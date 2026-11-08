"""DD redo NNC VONG 3 (08/11/2026, job Taylor_20261108_164333). Chay: $DNA_PYEXE -B nnc_redo_r3.py (tu thu muc calc nay).
Engine = nnc_model_r6 (-> r5 -> r4 -> r3 -> MVC r6 -> r5) IMPORT, KHONG SUA FILE; chi monkeypatch tai runtime 2 diem (co cong tat, kiem tai lap r2):
 (D1) tran chu ky P_CYC (tien 2026) tang theo lam phat 3%/nam o MUC DANH NGHIA: cap_thuc(y,path) = P_CYC*1.03^(y-2026)/g(y,path)
      (truoc: min(p, P_CYC) roi nhan g(y,path) => tren duong g2031 tran danh nghia phang toi 2030 trong khi chi phi +3%/nam).
 (D2) truc tran {SL 1,05 / theo SL nhanh / SL 1,40} deu 1/3 (r2: 2 muc, chi chieu xuong).
 Do nhay (khong vao base): co gian doi xung (bo min), kich ban xau khong chong len nhanh stress, thue chi 2043, tra truoc nguoi mua, tre GP.
 Gia + thanh khoan 06/11/2026 tu BQ (r3data/px_nnc_20261106.csv). Gia dinh khoa: assumptions_r3.json.
"""
import os, sys, json, itertools, csv, math, builtins
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
A = json.load(builtins.open(os.path.join(HERE, 'assumptions_r3.json'), encoding='utf-8'))
R6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
sys.path.insert(0, R6D); _cwd = os.getcwd(); os.chdir(R6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd)
import numpy as np  # noqa: E402
sys.path.insert(0, C.WC)
import deposit_rate_vn as DEP  # noqa: E402

ASOF = A['asof_price']
_d = DEP.effective_deposit_rate(ASOF); dep, dep_src = float(_d['rate']), _d['rate_source']; R = C.r_of(dep); N6.R_ANCHOR = R
N5, N4, N3, S = N6.N5, N6.N4, N6.N3, N6.S
RM = S.R  # MVC model_r5 (g, cell)
CW = N6.CW_BOBBY; SCN, PATHS, W0, PW0 = N5.SCN, N5.PATHS, N5.W0, N5.PW0
NODELAY = dict(cip_delay=False, delay=False)
q = 1 + R
pvf = {y: 1.03 ** (y - 2026) / q ** (y - 2026) for y in range(2027, 2044)}
FR_RENT_POST2030 = sum(v for y, v in pvf.items() if y >= 2031) / sum(pvf.values())

# ---------- monkeypatch tang day (thay ham r6 nprice ma N4 bat lam _np6) ----------
CFG = dict(infl_cap=True, sym=False, path=None, xau_nostack=False)
_np5, _cell0 = S._np5, RM.cell


def np_bottom(k, y, P):
    p = _np5(k, y, P); s = P.get('stress', 0.0)
    if y >= 2028 and s > 0:
        cap = S.P_CYC * (1.03 ** (y - 2026) / RM.g(y, CFG['path']) if CFG['infl_cap'] else 1.0)
        if CFG['xau_nostack'] and k in ('xau', 'rat_xau'):
            p = max(p, cap)                       # do nhay D5: day kich ban xau khong chong len nhanh da hoi ve TB chu ky
        p = (1 - s) * p + s * (cap if CFG['sym'] else min(p, cap))
    return p


def cell_ctx(k, path, P):
    old = CFG['path']; CFG['path'] = path
    try:
        return _cell0(k, path, P)
    finally:
        CFG['path'] = old


N4._np6 = np_bottom; RM.cell = cell_ctx


def caps(vi):
    return dict(branch=N4.cap_for(N4.eff_vol(N5.VRs[vi])), **{'1.40': N4.cap_for(1.40), '1.05': N4.cap_for(1.05)})


def branch_res(name, over, v_rev, cap_basis, admin):
    o = dict(over)
    if name == 'STRUCTURAL':
        o.update(stress=0.0, nnc_vol=(1.40, 1.40), ramp=False); cap = S.P_CYC
    else:
        st, rp = N5.ADMIN[admin] if name == 'ADMIN_GATED' else (1.0, False)
        o.update(stress=st, ramp=rp, nnc_vol=v_rev); o.setdefault('tl_vol', v_rev)
        cap = N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else float(cap_basis))
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, res = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return vn, {(k, p): res[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS}


# ---------- kiem doi chung: tat D1 => tai lap r2 trung byte ----------
r2 = json.load(open(os.path.join(HERE, 'nnc_redo_r2_out.json')))
CFG['infl_cap'] = False
for n in CW:
    a = N5.branch(n, {}); b_, _ = branch_res(n, {}, N5.V_REV, 'branch', 'ramp'); assert abs(a[0] - b_) < 1e-6, (n, a, b_)
c0_r2 = N6.EV5(NODELAY); assert abs(c0_r2 - r2['center_param_nodelay']) < 1e-6, (c0_r2, r2['center_param_nodelay'])
CFG['infl_cap'] = True

RENT_AX = ('2043', '2030', 'none'); CAP_AX = tuple(A['cap_axis'])


def build(cap_ax=CAP_AX, cfg=None):
    old = dict(CFG); CFG.update(cfg or {}); rows = []
    try:
        for n, k, vi, am, cb in itertools.product(CW, (0.87, 0.97, 1.07), range(3), N5.AMs, cap_ax):
            _, rT = branch_res(n, {'K': k, **NODELAY}, N5.VRs[vi], cb, am)
            _, rF = branch_res(n, {'K': k, 'rent': False, **NODELAY}, N5.VRs[vi], cb, am)
            wc = CW[n] / (3 * 3 * 3 * len(cap_ax) * 3)
            for ra in RENT_AX:
                for kp in rT:
                    v = rT[kp] if ra == '2043' else (rF[kp] if ra == 'none' else rT[kp] - FR_RENT_POST2030 * (rT[kp] - rF[kp]))
                    rows.append(dict(branch=n, K=k, VR=vi, admin=am, cap=cb, rent=ra, scn=kp[0], path=kp[1], w=wc * W0[kp[0]] * PW0[kp[1]], V=v))
    finally:
        CFG.clear(); CFG.update(old)
    return rows


def arr(rows): return np.array([r['V'] for r in rows]), np.array([r['w'] for r in rows])


def stats(v, w, mask=None, f=1.0):
    vv, ww = (v, w) if mask is None else (v[mask], w[mask])
    p = wpct(vv * f, ww)
    return dict(n=int(len(vv)), mean=float((vv * ww).sum() / ww.sum() * f), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(vv.min() * f), max=float(vv.max() * f))


out = dict(ticker='NNC', asof_price=ASOF, dep=dep, dep_src=dep_src, r=R, fr_rent_post2030=FR_RENT_POST2030, cap_axis=list(CAP_AX),
           caps_k={str(vi): caps(vi) for vi in range(3)}, check_r2_center_param_nodelay=c0_r2)
rows = build(); v, w = arr(rows); assert abs(w.sum() - 1) < 1e-9
out['n_outcomes'] = len(rows); out['n_cells'] = len(rows) // 8
out['center_param_nodelay'] = c0 = N6.EV5(NODELAY)
out['center_param_withdelay'] = N6.EV5()
out['pre'] = stats(v, w)
M = lambda key, val: np.array([r[key] == val for r in rows])  # noqa: E731
out['branch_pre'] = {n: stats(v, w, M('branch', n)) for n in CW}
out['cap_level_pre'] = {c: stats(v, w, M('cap', c)) for c in CAP_AX}

# ---------- bridge r2 -> r3 (truoc CK, tam luoi) ----------
br = {}
rr = build(cap_ax=('branch', '1.40'), cfg={'infl_cap': False}); V2, W2 = arr(rr); br['r2_rebuild'] = stats(V2, W2)
assert abs(br['r2_rebuild']['mean'] - r2['pre']['mean']) < 1e-6, (br['r2_rebuild']['mean'], r2['pre']['mean'])
rr = build(cap_ax=('branch', '1.40')); vv, ww = arr(rr); br['D1_infl_cap'] = stats(vv, ww)
br['D2_cap_axis_3'] = out['pre']
out['bridge_pre'] = br

# ---------- bien the song song (truoc CK) ----------
alt = {}
alt['rent_only_2043'] = stats(v, w, M('rent', '2043'))
rr = build(cfg={'sym': True}); vv, ww = arr(rr); alt['D4_sym_elastic'] = stats(vv, ww)
rr = build(cfg={'xau_nostack': True}); vv, ww = arr(rr); alt['D5_xau_nostack'] = stats(vv, ww)
rr = build(cfg={'infl_cap': False}); vv, ww = arr(rr); alt['no_D1_cap_axis_3'] = stats(vv, ww)
alt['cyc_100'] = out['branch_pre']['CYCLICAL']
sens_w = {}
for ws in (0.10, 0.20, 0.30):
    rest = 1 - ws; scale = {'STRUCTURAL': ws / CW['STRUCTURAL'], 'ADMIN_GATED': rest * 0.45 / 0.80 / CW['ADMIN_GATED'], 'CYCLICAL': rest * 0.35 / 0.80 / CW['CYCLICAL']}
    w2 = w * np.array([scale[r['branch']] for r in rows]); p = wpct(v, w2)
    sens_w[f'{ws:.2f}'] = dict(mean=float((v * w2).sum() / w2.sum()), p10=p[0.1], p50=p[0.5], p90=p[0.9])
out['sens_w_structural_pre'] = sens_w
out['alternatives_pre'] = alt

# ---------- do nhay don (tam tham so, khong tre) ----------
T = {}
def t(lab, over=None, **kw): x = N6.EV5({**NODELAY, **(over or {})}, **kw); T[lab] = dict(V=x, d=x - c0)
t('co tre GP ky vong (Bobby F6) CIP Tam Lap + mo MVC', {'cip_delay': True, 'delay': True})
t('tran SL 1,40', cap_basis='1.40'); t('ADMIN perm05', admin='perm05'); t('ADMIN full', admin='full')
t('bo thue Nui Nho', {'rent': False})
pp = sum(12.8 / q ** (i + 0.5) for i in range(4)) + 0.6 * 12.8 / q ** 4.5
t('(+) tra truoc CNBP 59,2 la tien thue da tra (CHUA XAC MINH)', {'extra': pp})
t('(+) doi thu het GP tu 2034', {'up2034': True}); t('STRESS duong gia danh nghia phang', {'PW': {'flat': 1.0}})
SH = N3.N_SH
for lab, x in (('(-) tru nguoi mua tra truoc 5,03 ty mot chieu', -A['cust_adv_bn']),
               ('(+) VLD doi xung: phai thu BQ AR_P0 24,44 - tra truoc 5,03', A['ar_bq_bn'] - A['cust_adv_bn'])):
    T[lab] = dict(V=c0 + x * 1e9 / SH, d=x * 1e9 / SH)
out['tornado'] = T

# ---------- thanh khoan + gia 06/11 ----------
C.LIQ_CSV = os.path.join(HERE, 'r3data/px_nnc_20261106.csv')
L = C.liquidity('NNC', ff=0.363, asof=ASOF, qs=(0.01e9, 0.04e9, 1e9, 5e9)); out['liq'] = L
assert L['price_date'] == ASOF and L['price'] == A['price_expected'], (L['price_date'], L['price'])
d_ref = L['pos']['5']['disc']['Y1.0']; f = 1 - d_ref
out['ck_real_sleeve'] = {f'{qq/1e6:.0f}tr': dict(adv250=L['sigma_d'] * math.sqrt(qq / L['adv_med']), adv60=L['sigma_d'] * math.sqrt(qq / L['adv_60'])) for qq in (0.01e9, 0.04e9)}
out['ck_ref'] = dict(size_bn=5, Y=1.0, adv250=d_ref, adv60=L['d_ref_adv60'], q_over_adv250=5e9 / L['adv_med'], q_over_adv60=5e9 / L['adv_60'])
px = L['price']; out['price'] = px; out['price_date'] = L['price_date']
out['post'] = stats(v, w, f=f)
out['center_post'] = out['post']['mean']; out['center_pre'] = out['pre']['mean']
out['post_alternatives'] = {k: {kk: (vv_ * f if kk in ('mean', 'p10', 'p50', 'p90', 'min', 'max') else vv_) for kk, vv_ in s.items()} for k, s in alt.items()}
out['bridge_post'] = {k: s['mean'] * f for k, s in br.items()}
out['bridge_post']['r2_pin_post_at_r2_ck'] = r2['post']['mean']
out['pct_weight_below_price'] = weight_below(v * f, w, px)
out['px_vs_center_post'] = px / out['center_post'] - 1
out['px_vs_p10_post'] = px / out['post']['p10'] - 1; out['px_vs_p90_post'] = px / out['post']['p90'] - 1
out['label'] = C.label(px, out['post']['p10'], out['post']['p90'])
out['rule4_px_below_center_15pct'] = bool(px <= 0.85 * out['center_post'])
out['center_param_nodelay_post'] = c0 * f
# r2 o gia moi (cung CK r3) — de so
out['r2_at_new_price'] = dict(below=weight_below(V2 * f, W2, px), mean_post=br['r2_rebuild']['mean'] * f)
g6 = json.load(open(os.path.join(R6D, 'nnc_model_r6_out.json')))
out['gordon'] = dict(roe_lock=g6['gordon']['tron_roe_lock'], roe_fin=g6['gordon']['tron_roe_fin'],
                     roe_implied_center_pre=N6.G + out['center_pre'] / N3.BVPS_NNC * (R - N6.G),
                     roe_implied_by_price=N6.G + (px / f) / N3.BVPS_NNC * (R - N6.G))
out['implied_by_price'] = dict(px_pre_ck=px / f, roe_gordon=out['gordon']['roe_implied_by_price'],
                               cyc100_post=alt['cyc_100']['mean'] * f, cyc100_vs_px=alt['cyc_100']['mean'] * f / px - 1,
                               w_below=out['pct_weight_below_price'])

json.dump(out, open(os.path.join(HERE, 'nnc_redo_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
with open(os.path.join(HERE, 'grid_nnc_redo_r3.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader()
    for r in rows: wr.writerow({**r, 'w': f"{r['w']:.12g}", 'V': f"{r['V']:.4f}"})


def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} max {s['max']:,.0f} (n {s['n']})"


print(f"NNC r3 | dep {dep:.2%} ({dep_src}) -> r {R:.2%} | tai lap r2: tam tham so {c0_r2:,.0f}, luoi {br['r2_rebuild']['mean']:,.0f} (OK)")
print('  tran (k/m3): ' + ' | '.join(f"VR{vi}: " + ', '.join(f"{a} {b:.1f}" for a, b in caps(vi).items()) for vi in range(3)))
print(f"  tam tham so khong tre {c0:,.0f} / co tre {out['center_param_withdelay']:,.0f}")
print('  TRUOC CK ' + fm(out['pre']))
for n, s in out['branch_pre'].items(): print(f'   {n:11s} ' + fm(s))
for c, s in out['cap_level_pre'].items(): print(f'   tran {c:7s} ' + fm(s))
print('  BRIDGE truoc CK: ' + ' -> '.join(f"{k} {s['mean']:,.0f}" for k, s in br.items()))
for k_, s in alt.items(): print(f'   ALT {k_:18s} ' + fm(s))
for k_, s in sens_w.items(): print(f"   w_STRUCT {k_}: tam {s['mean']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f}")
for k_, s in T.items(): print(f"   {k_:60s} {s['V']:8,.0f} ({s['d']:+,.0f})")
print(f"  CK ref 5 ty: ADV250 {L['adv_med']/1e9:.2f} ty -> {d_ref:.2%} (Q/ADV {out['ck_ref']['q_over_adv250']:.1f}x) | ADV60 {L['adv_60']/1e9:.2f} ty -> {L['d_ref_adv60']:.2%} | sleeve 10tr {out['ck_real_sleeve']['10tr']['adv250']:.2%} 40tr {out['ck_real_sleeve']['40tr']['adv250']:.2%}")
print('  SAU CK ' + fm(out['post']))
for k_, s in out['post_alternatives'].items(): print(f'   ALT sau CK {k_:18s} ' + fm(s))
print('  BRIDGE sau CK: ' + ' | '.join(f"{k} {x:,.0f}" for k, x in out['bridge_post'].items()))
print(f"  gia {px:,.0f} ({L['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | trong so duoi gia {out['pct_weight_below_price']:.1%} (r2 o gia moi {out['r2_at_new_price']['below']:.1%}) | luat4 {out['rule4_px_below_center_15pct']}")
print(f"  Gordon ROE khoa {out['gordon']['roe_lock']['ps']:,.0f} / +LN tai chinh {out['gordon']['roe_fin']['ps']:,.0f} | ROE ham y tam {out['gordon']['roe_implied_center_pre']:.1%} | ROE ham y GIA {out['gordon']['roe_implied_by_price']:.1%} | 100% CYC sau CK {out['implied_by_price']['cyc100_post']:,.0f} ({out['implied_by_price']['cyc100_vs_px']:+.1%} vs gia)")
