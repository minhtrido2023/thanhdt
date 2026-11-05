"""DD redo MVC VONG 2 (05/11/2026, job Taylor_20261105_020023). Chay: $DNA_PYEXE -B mvc_redo_r2.py (tu thu muc calc nay).
He thong = MVC r9 (nnc_model_r6 tiem r + model_r8) IMPORT, KHONG SUA. Vong 2 theo STANDARD_r2.md + E_CORRECTIONS.md (MVC):
 (1) MUC KET CUC: moi o -> 8 ket cuc (4 kich ban W0 x 2 duong gia PW0); trong so = w_o x W0 x PW0; phan vi _shared/wpct.py.
     (Truc tron PW 70/30-50/50-30/70 deu = PW0 tren cung ket cuc => gop.)
 (2) LUOI DOI XUNG: trang thai 0,20/0,45/0,35 x ca 3 x REL 3 x SL VRs 3 x han GP Tan Lap 3 x ADMIN 3
     x BIEN CHU KY TAN LAP {25%, 30%, ~NNC} (DUA LAI; deu [UL]) x TRAN CHU KY {branch, SL 1,40} (nhu NNC r2; deu).
 (3) BASE NPV0 that: bo chi phi tre GP ky vong (Bobby F6) cho mo moi MVC (delay) va CIP Tam Lap NNC (cip_delay) -> do nhay rieng.
 (4) Thanh khoan: CK 5 ty (Q/ADV250 ~11x = NGOAI SUY) + 1 ty + sleeve that 10/40 trieu; ADV250 va ADV60.
"""
import os, sys, json, csv, itertools, math
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
import numpy as np  # noqa: E402
N6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
R8D = os.path.abspath(os.path.join(HERE, '../../../dd_MVC_20261103/r8/calc'))
sys.path.insert(0, N6D); _cwd = os.getcwd(); os.chdir(N6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd); sys.path.insert(0, R8D)
import model_r8 as V8  # noqa: E402
assert V8.N3 is N6.N3 and V8.N3.EV3 is N6.EV3r

dep, dep_src = C.dep_now(); R = C.r_of(dep); N6.R_ANCHOR = R
CW = V8.CW; SCN, PATHS, W0, PW0 = V8.SCN, V8.PATHS, V8.W0, V8.PW0
NODELAY = dict(delay=False, cip_delay=False)
AX = dict(ca=(0.85, 1.0, 1.15), REL=(0.88, 0.91, 0.95), VR=range(3), endA=(2035, 'W', 2045), admin=V8.AMs, tl_m=(0.25, 0.30, 'nnc'), cap=('branch', '1.40'))
NPER = math.prod(len(v) for v in AX.values())


def _cell(a):
    n, ca, rel, vi, en, am, tm, cb = a
    b = V8.branch(n, {'ca': ca, 'REL': rel, 'endA': en, 'tl_m': tm, **NODELAY}, v_rev=V8.VRs[vi], cap_basis=cb, admin=am)
    return [dict(branch=n, ca=ca, REL=rel, VR=vi, endA=en, admin=am, tl_m=tm, cap=cb, scn=k, path=p,
                 w=CW[n] / NPER * W0[k] * PW0[p], V=b['res'][(k, p)]['ps']) for k in SCN for p in PATHS]


def stats(v, w, f=1.0, px=None):
    p = wpct(v * f, w)
    o = dict(n=int(len(v)), mean=float((v * w).sum() / w.sum() * f), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(v.min() * f), max=float(v.max() * f))
    if px: o['below'] = weight_below(v * f, w, px)
    return o


if __name__ == '__main__':
    out = dict(ticker='MVC', dep=dep, dep_src=dep_src, r=R)
    out['center_param_withdelay'] = V8.EV8()                 # = pin r9 16.482
    out['center_param_nodelay'] = V8.EV8(dict(NODELAY))
    # kiem: ket cuc tai lap ky vong nhanh
    b = V8.branch('ADMIN_GATED', dict(NODELAY))
    assert abs(sum(W0[k] * PW0[p] * b['res'][(k, p)]['ps'] for k in SCN for p in PATHS) - b['vm']) < 1e-6
    args = list(itertools.product(CW, *AX.values()))
    with Pool(8) as pool: rows = [r for cell in pool.map(_cell, args, chunksize=40) for r in cell]
    v = np.array([r['V'] for r in rows]); w = np.array([r['w'] for r in rows]); assert abs(w.sum() - 1) < 1e-9
    m = lambda key, val: np.array([r[key] == val for r in rows])
    L = C.liquidity('MVC', ff=0.302, qs=(0.01e9, 0.04e9, 1e9, 5e9)); out['liq'] = L
    d5 = L['pos']['5']['disc']['Y1.0']; d1 = L['pos']['1']['disc']['Y1.0']; f = 1 - d5; px = L['price']
    out['ck_ref'] = dict(size_bn=5, Y=1.0, adv250=d5, adv60=L['d_ref_adv60'], q_over_adv250=5e9 / L['adv_med'], q_over_adv60=5e9 / L['adv_60'], disc_1bn=d1,
                         disc_1bn_adv60=L['sigma_d'] * math.sqrt(1e9 / L['adv_60']))
    out['ck_real_sleeve'] = {f'{q/1e6:.0f}tr': dict(adv250=L['sigma_d'] * math.sqrt(q / L['adv_med']), adv60=L['sigma_d'] * math.sqrt(q / L['adv_60'])) for q in (0.01e9, 0.04e9)}
    out['n_outcomes'] = len(rows); out['n_cells'] = len(args)
    out['pre'] = stats(v, w, 1.0, px); out['post'] = stats(v, w, f, px); out['post_1bn'] = stats(v, w, 1 - d1, px)
    keep_r1 = m('tl_m', 'nnc') & m('cap', 'branch')
    out['post_r1axes_only'] = stats(v[keep_r1], w[keep_r1], f, px)
    out['post_no_tlm_axis'] = stats(v[m('tl_m', 'nnc')], w[m('tl_m', 'nnc')], f, px)
    out['post_no_cap_axis'] = stats(v[m('cap', 'branch')], w[m('cap', 'branch')], f, px)
    out['branch_post'] = {n: stats(v[m('branch', n)], w[m('branch', n)], f, px) for n in CW}
    sw = {}
    for ws in (0.10, 0.15, 0.30):
        rest = 1 - ws; sc = {'STRUCTURAL': ws / CW['STRUCTURAL'], 'ADMIN_GATED': rest * 0.45 / 0.80 / CW['ADMIN_GATED'], 'CYCLICAL': rest * 0.35 / 0.80 / CW['CYCLICAL']}
        ww = w * np.array([sc[r['branch']] for r in rows]); sw[f'{ws:.2f}'] = stats(v, ww, f, px)
    out['sens_w_structural_post'] = sw
    c0 = out['center_param_nodelay']; T = {}
    def t(lab, over=None, **kw): x = V8.EV8({**NODELAY, **(over or {})}, **kw); T[lab] = dict(V=x, d=x - c0)
    t('co tre GP ky vong (Bobby F6) mo moi + CIP NNC', {'delay': True, 'cip_delay': True}); t('chi tre mo moi MVC', {'delay': True})
    t('bien Tan Lap 25%', {'tl_m': 0.25}); t('bien Tan Lap 30%', {'tl_m': 0.30}); t('tran SL 1,40', cap_basis='1.40')
    t('mo moi hai phia (upside + NPV gia xau; lech NPV0)', {'up': True, 'mine_xau': True}); t('ADMIN perm05', admin='perm05'); t('ADMIN full', admin='full')
    t('bo thue Nui Nho (NNC)', {'rent': False})
    out['tornado'] = T
    dsens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.R_ANCHOR + (dep + bp / 1e4 - C.DEP_ANCHOR); x = V8.EV8({**NODELAY, 'r': rr}); dsens[f'{bp:+d}'] = dict(r=rr, V=x, pct=x / c0 - 1)
    out['dep_sens_param'] = dsens
    # kiem toan: luoi vong 1 (co tre, khong truc tl_m/cap) o muc ket cuc
    def _cell1(a):
        n, ca, rel, vi, en, am = a
        bb = V8.branch(n, {'ca': ca, 'REL': rel, 'endA': en}, v_rev=V8.VRs[vi], admin=am)
        return [(bb['res'][(k, p)]['ps'], CW[n] / 243 * W0[k] * PW0[p]) for k in SCN for p in PATHS]
    a1 = list(itertools.product(CW, AX['ca'], AX['REL'], AX['VR'], AX['endA'], AX['admin']))
    au = [x for c in map(_cell1, a1) for x in c]; av = np.array([x for x, _ in au]); aw = np.array([y for _, y in au])
    out['audit_r1_grid_outcome'] = stats(av, aw, f, px)
    P = out['post']
    out.update(price=px, price_date=L['price_date'], center_pre=out['pre']['mean'], center_post=P['mean'], pct_weight_below_price=P['below'],
               px_vs_center_post=px / P['mean'] - 1, px_vs_p10_post=px / P['p10'] - 1, px_vs_p90_post=px / P['p90'] - 1,
               label=C.label(px, P['p10'], P['p90']), label_1bn=C.label(px, out['post_1bn']['p10'], out['post_1bn']['p90']),
               rule4_px_below_center_15pct=bool(px <= 0.85 * P['mean']))
    json.dump(out, open(os.path.join(HERE, 'mvc_redo_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
    with open(os.path.join(HERE, 'grid_mvc_redo_r2.csv'), 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader()
        for r in rows: wr.writerow({**r, 'w': f"{r['w']:.12g}", 'V': f"{r['V']:.4f}"})

    def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} | duoi gia {s.get('below', float('nan')):.1%} (n {s['n']})"
    print(f"MVC r2 | r {R:.2%} | tham so trung tam co tre {out['center_param_withdelay']:,.0f} (pin r9 16.482) / KHONG tre {c0:,.0f}")
    print('  TRUOC CK ' + fm(out['pre'])); print('  SAU CK 5 ty ' + fm(P)); print('  SAU CK 1 ty ' + fm(out['post_1bn']))
    print('   [truc vong 1 only, khong tre] ' + fm(out['post_r1axes_only'])); print('   [bo truc bien TL] ' + fm(out['post_no_tlm_axis'])); print('   [bo truc tran] ' + fm(out['post_no_cap_axis']))
    print('   [kiem toan luoi vong 1 co tre, muc ket cuc] ' + fm(out['audit_r1_grid_outcome']))
    for n, s in out['branch_post'].items(): print(f'   {n:11s} ' + fm(s))
    for k, s in sw.items(): print(f'   w_STRUCT {k}: ' + fm(s))
    for k, s in T.items(): print(f"   {k:50s} {s['V']:8,.0f} ({s['d']:+,.0f})")
    for k, s in dsens.items(): print(f"   dep {k}bp: r {s['r']:.2%} -> {s['V']:,.0f} ({s['pct']:+.1%})")
    print(f"  CK: 5 ty {d5:.2%} (Q/ADV250 {out['ck_ref']['q_over_adv250']:.1f}x, ADV60 {L['d_ref_adv60']:.2%}) | 1 ty {d1:.2%} (ADV60 {out['ck_ref']['disc_1bn_adv60']:.2%}) | ADV250 {L['adv_med']/1e9:.3f} ty ADV60 {L['adv_60']/1e9:.3f} | sleeve {json.dumps(out['ck_real_sleeve'])}")
    print(f"  gia {px:,.0f} ({L['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} (1 ty: {out['label_1bn']}) | luat4 {out['rule4_px_below_center_15pct']}")
