"""DD redo MVC VONG 3 (09/11/2026, job Taylor_20261108_180136). Chay: $DNA_PYEXE -B mvc_redo_r3.py [--check] (tu thu muc calc_r3 nay).
Engine = MVC r9 (nnc_model_r6 tiem r + model_r8 -> nnc_model_r5 -> r4 -> r3 -> MVC r6 -> r5) IMPORT, KHONG SUA FILE.
Monkeypatch tai runtime (co cong tat; kiem tai lap r2 trung so):
 (D1) tran chu ky tang theo lam phat: cap_thuc(y,path) = S.P_CYC*1.03^(y-2026)/g(y,path) — ap cho tran NNC, tran ~NNC va tran bien 30/38/25% cua
      Tan Lap (model_r8.tanlap8 dat S.P_CYC = cap_tl roi goi S.nprice -> N4._np6). Cung ham nhu NNC r3 (nnc_redo_r3.py:40-47).
 (D2) truc tran {SL 1,05 / theo nhanh / SL 1,40} (ham branch rieng: model_r8.py:76 quy moi gia tri != 'branch' ve 1,40).
 (D3) truc thue Nui Nho {2043 / 2030 / khong} nhu NNC r3.
 (D4) truc bien Tan Lap doi xung {30% / ~NNC / 38%} (r2 {25/30/~NNC} chi mo chieu giam -> ban song song).
 (D5) ICD Hoa Lu = tai san thuan tru tien 38,728 ty (r2: von gop 44,797; tien ICD 2,923 da nam trong NETFIN hop nhat).
Gia dinh khoa: assumptions_r3.json (LOCK_r3_md5.txt ghi TRUOC khi chay). --check: chi in kiem co che, KHONG doc gia/thanh khoan.
"""
import os, sys, json, csv, itertools, math, builtins
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
import numpy as np  # noqa: E402
A = json.load(builtins.open(os.path.join(HERE, 'assumptions_r3.json'), encoding='utf-8'))
N6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
R8D = os.path.abspath(os.path.join(HERE, '../../../dd_MVC_20261103/r8/calc'))
sys.path.insert(0, N6D); _cwd = os.getcwd(); os.chdir(N6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd); sys.path.insert(0, R8D)
import model_r8 as V8  # noqa: E402
assert V8.N3 is N6.N3 and V8.N3.EV3 is N6.EV3r
sys.path.insert(0, C.WC)
import deposit_rate_vn as DEP  # noqa: E402

ASOF = A['asof_price']
_d = DEP.effective_deposit_rate(ASOF); dep, dep_src = float(_d['rate']), _d['rate_source']; R = C.r_of(dep); N6.R_ANCHOR = R
N4, N3, S = V8.N4, V8.N3, V8.S
RM = S.R; assert RM is V8.R
CW = V8.CW; SCN, PATHS, W0, PW0 = V8.SCN, V8.PATHS, V8.W0, V8.PW0
NODELAY = dict(delay=False, cip_delay=False)
q = 1 + R
pvf = {y: 1.03 ** (y - 2026) / q ** (y - 2026) for y in range(2027, 2044)}
FR_RENT_POST2030 = sum(v for y, v in pvf.items() if y >= 2031) / sum(pvf.values())

# ---------- monkeypatch D1 (giong NNC r3) ----------
CFG = dict(infl_cap=True, path=None)
_np5, _cell0 = S._np5, RM.cell


def np_bottom(k, y, P):
    p = _np5(k, y, P); s = P.get('stress', 0.0)
    if y >= 2028 and s > 0:
        cap = S.P_CYC * (1.03 ** (y - 2026) / RM.g(y, CFG['path']) if CFG['infl_cap'] else 1.0)
        p = (1 - s) * p + s * min(p, cap)
    return p


def cell_ctx(k, path, P):
    old = CFG['path']; CFG['path'] = path
    try:
        return _cell0(k, path, P)
    finally:
        CFG['path'] = old


N4._np6 = np_bottom; RM.cell = cell_ctx
ICD_R2, ICD_R3 = A['icd_bv_r2'], A['icd_net_assets_ex_cash']
assert abs(RM.ICD_BV - ICD_R2) < 1e-9


def branch(name, over, v_rev=V8.V_REV, cap_basis='branch', admin='ramp'):
    o = dict(over or {})
    if name == 'STRUCTURAL':
        o.update(stress=0.0, ramp=False, nnc_vol=(1.40, 1.40)); cap = S.P_CYC
    else:
        st, rp = V8.ADMIN[admin] if name == 'ADMIN_GATED' else (1.0, False)
        o.update(stress=st, ramp=rp, nnc_vol=v_rev); o.setdefault('tl_vol', v_rev)
        cap = N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else float(cap_basis))
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, res = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return dict(vn=vn, vm=vm, res=res, cap=cap)


def EVc(over=None, cw=CW, **kw):
    b = {n: branch(n, {**NODELAY, **(over or {})}, **kw) for n in cw}
    return sum(cw[n] * b[n]['vm'] for n in cw)


def set_icd(x): RM.ICD_BV = x


# ---------- kiem doi chung: tat D1 + ICD r2 => tai lap r2 ----------
r2 = json.load(open(os.path.join(HERE, '../calc/mvc_redo_r2_out.json')))
CFG['infl_cap'] = False; set_icd(ICD_R2)
for n in CW:
    for cb in ('branch', '1.40'):
        a = V8.branch(n, dict(NODELAY), cap_basis=cb)['vm']; b_ = branch(n, NODELAY, cap_basis=cb)['vm']; assert abs(a - b_) < 1e-6, (n, cb, a, b_)
c0_r2 = EVc(); assert abs(c0_r2 - r2['center_param_nodelay']) < 1e-6, (c0_r2, r2['center_param_nodelay'])
CFG['infl_cap'] = True; set_icd(ICD_R3)


def tl_margin():
    """bien Tan Lap tai tran ~NNC (SL nhanh trung tam): truoc D1 tren g2031 o 2030 vs sau D1."""
    cap = N4.cap_for(N4.eff_vol(V8.V_REV)); ctl = RM.costA(RM.BASE) * V8.fixfac(N4.eff_vol(V8.V_REV))
    return dict(cap_2026=cap, price_TL_2026=0.91 * cap, cost_TL_2026=ctl, margin_D1=1 - ctl / (0.91 * cap),
                margin_preD1_g2031_2030=1 - ctl * 1.03 ** 4 / (0.91 * cap), nnc_margin_D1=1 - N4.unit_cost(N4.eff_vol(V8.V_REV)) / cap)


AXV = dict(ca=(0.85, 1.0, 1.15), REL=(0.88, 0.91, 0.95), VR=range(3), endA=(2035, 'W', 2045), admin=V8.AMs,
           tl_m=(0.25, 0.30, 'nnc', 0.38), cap=tuple(A['cap_axis']))
RENT = tuple(A['rent_axis'])


def _cell(a):
    n, ca, rel, vi, en, am, tm, cb, icd = a
    set_icd(icd)
    base = {'ca': ca, 'REL': rel, 'endA': en, 'tl_m': tm, **NODELAY}
    bT = branch(n, base, v_rev=V8.VRs[vi], cap_basis=cb, admin=am)['res']
    bF = branch(n, {**base, 'rent': False}, v_rev=V8.VRs[vi], cap_basis=cb, admin=am)['res']
    out = []
    for ra in RENT:
        for k in SCN:
            for p in PATHS:
                vT, vF = bT[(k, p)]['ps'], bF[(k, p)]['ps']; nT, nF = bT[(k, p)]['V_NNC_ps'], bF[(k, p)]['V_NNC_ps']
                if ra == '2043': v, vn = vT, nT
                elif ra == 'none': v, vn = vF, nF
                else: v, vn = vT - FR_RENT_POST2030 * (vT - vF), nT - FR_RENT_POST2030 * (nT - nF)
                out.append((n, ca, rel, vi, en, am, tm, cb, ra, k, p, CW[n] * W0[k] * PW0[p], v, vn))
    return out


COLS = ('branch', 'ca', 'REL', 'VR', 'endA', 'admin', 'tl_m', 'cap', 'rent', 'scn', 'path', 'wraw', 'V', 'VN')


def stats(v, w, f=1.0, px=None):
    p = wpct(v * f, w)
    o = dict(n=int(len(v)), mean=float((v * w).sum() / w.sum() * f), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(v.min() * f), max=float(v.max() * f))
    if px: o['below'] = weight_below(v * f, w, px)
    return o


if __name__ == '__main__':
    CHECK = '--check' in sys.argv
    out = dict(ticker='MVC', round=3, asof_price=ASOF, dep=dep, dep_src=dep_src, r=R, fr_rent_post2030=FR_RENT_POST2030,
               check_r2_center_param_nodelay=c0_r2, tl_margin=tl_margin())
    # ICD: dich chuyen hang so (kiem tren 3 nhanh x 2 kich ban)
    dI = {}
    for n in CW:
        x = []
        for icd in (ICD_R2, ICD_R3):
            set_icd(icd); x.append(branch(n, NODELAY)['res'])
        dI[n] = [x[0][kp]['ps'] - x[1][kp]['ps'] for kp in x[0]]
    set_icd(ICD_R3)
    flat = [d for n in dI for d in dI[n]]; assert max(flat) - min(flat) < 1e-6; DICD = float(np.mean(flat)); out['icd_shift_pre'] = DICD
    out['center_param_nodelay'] = EVc(); out['center_param_withdelay'] = EVc({'delay': True, 'cip_delay': True})
    tm = out['tl_margin']
    print(f"MVC r3 | r {R:.2%} (dep {dep:.2%}, {dep_src}) | kiem r2 tham so trung tam {c0_r2:,.2f} = pin r2 | ICD -{DICD:,.2f} d/cp (truoc CK) moi ket cuc")
    print(f"  bien Tan Lap ~NNC: truoc D1 tren g2031 nam 2030 {tm['margin_preD1_g2031_2030']:.1%} -> sau D1 {tm['margin_D1']:.1%} (NNC {tm['nnc_margin_D1']:.1%}); tham so trung tam r3 {out['center_param_nodelay']:,.0f}")
    if CHECK:
        sys.exit(0)
    args = [(*a, ICD_R3) for a in itertools.product(CW, *AXV.values())]
    with Pool(8) as pool: rows = [r for c in pool.map(_cell, args, chunksize=40) for r in c]
    set_icd(ICD_R3)
    col = {c: np.array([r[i] for r in rows], dtype=object) for i, c in enumerate(COLS)}
    V = col['V'].astype(float); VN = col['VN'].astype(float); WR = col['wraw'].astype(float)
    tl, cp, rn = col['tl_m'], col['cap'], col['rent']
    isin = lambda a, vals: np.array([x in vals for x in a])
    M_HEAD = isin(tl, (0.30, 'nnc', 0.38))
    def sub(mask, shift=0.0):
        return (V[mask] + shift), WR[mask] / WR[mask].sum()
    # thanh khoan + gia (06/11 BQ)
    C.LIQ_CSV = os.path.join(HERE, 'r3data/px_mvc_20261106.csv')
    L = C.liquidity('MVC', ff=A['free_float'], asof=ASOF, qs=tuple(A['sizes_vnd'])); out['liq'] = L
    px = L['price']; assert px == A['price_expected'] and L['price_date'] == ASOF
    sig, adv, adv60 = L['sigma_d'], L['adv_med'], L['adv_60']
    dk = {lab: dict(adv250=sig * math.sqrt(qv / adv), adv60=sig * math.sqrt(qv / adv60), q_over_adv250=qv / adv, q_over_adv60=qv / adv60)
          for lab, qv in (('5ty', 5e9), ('1ty', 1e9), ('40tr', 0.04e9), ('10tr', 0.01e9))}
    out['ck'] = dk; f5 = 1 - dk['5ty']['adv250']
    v, w = sub(M_HEAD); assert abs(w.sum() - 1) < 1e-9
    out['n_outcomes'] = int(M_HEAD.sum()); out['n_cells'] = int(M_HEAD.sum()) // 8
    out['pre'] = stats(v, w, 1.0, px); out['post'] = stats(v, w, f5, px)
    out['post_by_size'] = {lab: stats(v, w, 1 - d['adv250'], px) for lab, d in dk.items()}
    out['V_NNC_implied_pre'] = float((VN[M_HEAD] * w).sum())
    nnc3 = json.load(open(os.path.join(RED, 'NNC/calc/nnc_redo_r3_out.json'))); out['V_NNC_r3_pre'] = nnc3['pre']['mean']
    # nhanh
    out['branch_post'] = {n: stats(*sub(M_HEAD & (col['branch'] == n)), f5, px) for n in CW}
    out['branch_pre_mean'] = {n: out['branch_post'][n]['mean'] / f5 for n in CW}
    # ban thay the (song song)
    alt = {}
    alt['tl_r2_onesided_25_30_nnc'] = stats(*sub(isin(tl, (0.25, 0.30, 'nnc'))), f5, px)
    alt['tl_no_axis_nnc_only'] = stats(*sub(tl == 'nnc'), f5, px)
    alt['rent_2043_only'] = stats(*sub(M_HEAD & (rn == '2043')), f5, px)
    alt['cap_r2_branch_140'] = stats(*sub(M_HEAD & isin(cp, ('branch', '1.40'))), f5, px)
    alt['icd_r2_44797'] = stats(*sub(M_HEAD, DICD), f5, px)
    out['alternatives_post'] = alt
    sw = {}
    for ws in (0.10, 0.15, 0.30):
        rest = 1 - ws; sc = {'STRUCTURAL': ws / CW['STRUCTURAL'], 'ADMIN_GATED': rest * 0.45 / 0.80 / CW['ADMIN_GATED'], 'CYCLICAL': rest * 0.35 / 0.80 / CW['CYCLICAL']}
        ww = w * np.array([sc[b] for b in col['branch'][M_HEAD]]); sw[f'{ws:.2f}'] = stats(v, ww / ww.sum(), f5, px)
    out['sens_w_structural_post'] = sw
    # bridge r2 -> r3 (sau CK 5 ty)
    br = {}
    br['0 pin r2 (gia 04/11, CK 04/11)'] = r2['post']['mean']
    br['1 r2 o CK 06/11'] = r2['pre']['mean'] * f5
    m_r2ax = isin(tl, (0.25, 0.30, 'nnc')) & isin(cp, ('branch', '1.40')) & (rn == '2043')
    br['2 + D1 tran tang theo lam phat'] = stats(*sub(m_r2ax, DICD), f5)['mean']
    br['3 + muc tran SL 1,05'] = stats(*sub(isin(tl, (0.25, 0.30, 'nnc')) & (rn == '2043'), DICD), f5)['mean']
    br['4 + truc thue {2043/2030/khong}'] = stats(*sub(isin(tl, (0.25, 0.30, 'nnc')), DICD), f5)['mean']
    br['5 + truc bien TL doi xung {30/~NNC/38}'] = stats(*sub(M_HEAD, DICD), f5)['mean']
    br['6 + ICD tai san thuan tru tien (= r3)'] = out['post']['mean']
    out['bridge_post'] = br
    # do nhay tai tham so trung tam (truoc CK)
    c0 = out['center_param_nodelay']; T = {}
    def t(lab, over=None, icd=ICD_R3, **kw):
        set_icd(icd); x = EVc(over, **kw); set_icd(ICD_R3); T[lab] = dict(V=x, d=x - c0)
    t('tre GP ky vong (Bobby F6) mo moi + CIP NNC', {'delay': True, 'cip_delay': True})
    t('bien TL 25%', {'tl_m': 0.25}); t('bien TL 30%', {'tl_m': 0.30}); t('bien TL 38%', {'tl_m': 0.38})
    t('tran SL 1,05', cap_basis='1.05'); t('tran SL 1,40', cap_basis='1.40')
    t('mo moi hai phia (upside + NPV gia xau; lech NPV0)', {'up': True, 'mine_xau': True})
    t('ADMIN perm05', admin='perm05'); t('ADMIN full', admin='full'); t('bo thue Nui Nho', {'rent': False})
    t('ICD von gop 44,797 (r2)', icd=ICD_R2)
    t('chiet khau holding 6% (phan NNC)', {'hold': 0.06}); t('chiet khau holding 15% (phan NNC)', {'hold': 0.15})
    t('V_NNC = gia thi truong 47.200', {'VN_fix': 47200.0})
    t('chi CYCLICAL', cw={'CYCLICAL': 1.0})
    out['tornado'] = T
    dsens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.R_ANCHOR + (dep + bp / 1e4 - C.DEP_ANCHOR); x = EVc({'r': rr}); dsens[f'{bp:+d}'] = dict(r=rr, V=x, pct=x / c0 - 1)
    out['dep_sens_param'] = dsens
    # gia ngu y
    P = out['post']; Sb, Ab, Cb = (out['branch_post'][n]['mean'] for n in ('STRUCTURAL', 'ADMIN_GATED', 'CYCLICAL'))
    oth = 0.45 / 0.80 * Ab + 0.35 / 0.80 * Cb; ws_impl = (px - oth) / (Sb - oth)
    vfix = (T['V_NNC = gia thi truong 47.200']['d']) * f5
    hold_on_total = 1 - px / (P['mean'] + vfix)
    BVPS = S.BVPS; roe_impl = 0.03 + (px / f5) / BVPS * (R - 0.03); roe_center = 0.03 + out['pre']['mean'] / BVPS * (R - 0.03)
    out['implied_by_price'] = dict(w_structural_needed=ws_impl, note_ws='giu ty le ADMIN:CYC 45:35; am => gia thap hon ca ky vong khi bo han nhanh STRUCTURAL',
                                   cyclical_only_post=Cb, admin_only_post=Ab,
                                   vnnc_market_shift_post=vfix, generic_disc_needed_after_vnnc_market=hold_on_total,
                                   roe_sustainable_implied=roe_impl, roe_implied_center=roe_center, bvps=BVPS)
    # nhan + luat 4 theo co
    out['label'] = C.label(px, P['p10'], P['p90'])
    out['label_by_size'] = {lab: C.label(px, s['p10'], s['p90']) for lab, s in out['post_by_size'].items()}
    out['rule4_by_size'] = {lab: dict(center=s['mean'], thr=0.85 * s['mean'], pass_=bool(px <= 0.85 * s['mean'])) for lab, s in out['post_by_size'].items()}
    out.update(price=px, price_date=L['price_date'], center_pre=out['pre']['mean'], center_post=P['mean'], pct_weight_below_price=P['below'],
               px_vs_center_post=px / P['mean'] - 1, px_vs_p10_post=px / P['p10'] - 1, px_vs_p90_post=px / P['p90'] - 1)
    json.dump(out, open(os.path.join(HERE, 'mvc_redo_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
    with open(os.path.join(HERE, 'grid_mvc_redo_r3.csv'), 'w', newline='') as fh:
        wr = csv.writer(fh); wr.writerow(COLS)
        for r in rows: wr.writerow([*r[:11], f'{r[11]:.12g}', f'{r[12]:.4f}', f'{r[13]:.4f}'])

    def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} | duoi gia {s.get('below', float('nan')):.1%} (n {s['n']})"
    print('  TRUOC CK ' + fm(out['pre']))
    for lab, s in out['post_by_size'].items(): print(f'  SAU CK {lab:5s} ' + fm(s) + f" | {out['label_by_size'][lab]} | luat4 {out['rule4_by_size'][lab]['pass_']} (0,85x tam {out['rule4_by_size'][lab]['thr']:,.0f})")
    print(f"  V_NNC ngam trong MVC (truoc CK) {out['V_NNC_implied_pre']:,.0f} vs NNC r3 {out['V_NNC_r3_pre']:,.0f} ({out['V_NNC_implied_pre']/out['V_NNC_r3_pre']-1:+.1%})")
    for n, s in out['branch_post'].items(): print(f'   {n:11s} ' + fm(s))
    for k, s in alt.items(): print(f'   [alt {k}] ' + fm(s))
    for k, s in sw.items(): print(f'   w_STRUCT {k}: ' + fm(s))
    print('  BRIDGE sau CK 5 ty: ' + ' -> '.join(f'{k} {x:,.0f}' for k, x in br.items()))
    for k, s in T.items(): print(f"   {k:52s} {s['V']:8,.0f} ({s['d']:+,.0f})")
    for k, s in dsens.items(): print(f"   dep {k}bp: r {s['r']:.2%} -> {s['V']:,.0f} ({s['pct']:+.1%})")
    print(f"  CK (ADV250 {adv/1e9:.3f} ty, ADV60 {adv60/1e9:.3f} ty, sigma {sig:.2%}): " + ' | '.join(f"{k} {d['adv250']:.2%} (ADV60 {d['adv60']:.2%}, Q/ADV250 {d['q_over_adv250']:.2f}x)" for k, d in dk.items()))
    ib = out['implied_by_price']
    print(f"  GIA NGU Y: w_STRUCT can {ib['w_structural_needed']:.3f} | chi CYC {Cb:,.0f} | V_NNC=thi truong {vfix:+,.0f} roi CK chung {hold_on_total:.1%} | ROE ben ngu y {roe_impl:.1%} (tam {roe_center:.1%})")
    print(f"  gia {px:,.0f} ({L['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']}")
