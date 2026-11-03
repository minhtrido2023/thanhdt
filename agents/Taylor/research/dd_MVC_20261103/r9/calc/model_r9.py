"""DD MVC r9 (03/11/2026 ~22:50 ICT) — doi chi phi von theo luat 21 (user 03/11 22:27). Khong dung gia thi truong (MVC/NNC: gia, von hoa, P/E) lam dau vao.
Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r9.py. He thong: NNC r6 (nnc_model_r6.py: tiem r 13,5% vao N3.EV3) + MVC r8 (model_r8.py) KHONG SUA
(md5 o LOCK_md5_r9.txt). V_NNC giai DONG THOI trong tung trang thai o CUNG r (vong cheo nhat quan NNC r6). Moi gia dinh phan doan r8 GIU NGUYEN (user duyet).
THAY DOI r9 so voi r8: (1) r = 13,5% @ lai huy dong 12T hieu dung 7,40% (cctg_12m 02/11/2026), r(dep) = 13,5% + beta(dep - 7,40%), beta 1 (do nhay 0,5);
 (2) Gordon cung r (r - g = 10,5%); (3) truc r luoi {11,5; 13,5; 15,5}%; (4) chan doi chung r 13% PHAI tai lap r8 16.702.
THANH KHOAN (DANG KY TRUOC, tinh SAU khoa): cung phuong phap NNC r6 (docstring nnc_model_r6.py; ket qua MVC trong ../../../dd_NNC_20261030/r6/calc/liquidity_r6_out.json):
 d(Q) = Y x sigma_ngay x sqrt(Q/ADV_trung_vi), Y=1,0 (0,5/1,5); quy mo 1/5/10 ty; NHAN = gia so voi thang P10..P90 x (1 - d(5 ty)).
NGUONG mo hinh (dang ky truoc): RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90 (luoi 118.098 bo).
"""
import sys, os, itertools, json, csv
import numpy as np
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
N6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc')); R8D = os.path.abspath(os.path.join(HERE, '../../r8/calc'))
sys.path.insert(0, N6D); _cwd = os.getcwd(); os.chdir(N6D)
import nnc_model_r6 as N6   # noqa: E402  (patch N3.EV3 -> r 13,5%)
os.chdir(_cwd); sys.path.insert(0, R8D)
import model_r8 as V8      # noqa: E402  (dung lai nnc_model_r5 da nap => cung N3 da patch)
assert V8.N3 is N6.N3 and V8.N3.EV3 is N6.EV3r
N4, N3, S, M, R = V8.N4, V8.N3, V8.S, V8.M, V8.R
SCN, PATHS, W0, PW0, CW, V_REV = V8.SCN, V8.PATHS, V8.W0, V8.PW0, V8.CW, V8.V_REV
EV8, branch = V8.EV8, V8.branch
Ws, PWs, CWs, VRs, AMs, TLMs = V8.Ws, V8.PWs, V8.CWs, V8.VRs, V8.AMs, V8.TLMs
R0, DEP0, G = N6.R_ANCHOR, N6.DEP_ANCHOR, 0.03
R_AXIS = (R0 - 0.02, R0, R0 + 0.02)
_cell = V8._cell


if __name__ == '__main__':
    out = dict(r=R0, dep_anchor=DEP0, dep_src=N6.DEP_SRC, beta=1.0)
    vm, vn, b = EV8(detail=True); out['tam'] = vm; out['V_NNC'] = vn
    out['branches'] = {n: dict(w=CW[n], V_MVC=b[n]['vm'], V_NNC=b[n]['vn']) for n in b}
    print(f'=== 1. TAM MVC r9 (r 13,5% @ huy dong 7,40%; con lai = r8): {vm:,.0f} d/cp | V_NNC dong thoi {vn:,.0f} (NNC r6 tam 60.702)')
    for n in b:
        r_ = b[n]['res']
        print(f'  {n:11s} w {CW[n]:.2f}: MVC {b[n]["vm"]:7,.0f} | NNC {b[n]["vn"]:8,.0f} | ' + ' '.join(f'{k} {np.mean([r_[(k, p)]["ps"] for p in PATHS]):7,.0f}' for k in SCN))
    c13, cn13 = EV8({'r': 0.13}, detail=True)[:2]; out['control_r13'] = c13
    print(f'  CHAN DOI CHUNG r 13%: MVC {c13:,.0f} (r8 pin 16.702; lech {c13-16702:+.1f}) | V_NNC {cn13:,.0f}')
    out['mvc_at_vnnc_r6'] = EV8({'VN_fix': 60702}); print(f'  V_NNC co dinh = NNC r6 60.702 -> MVC {out["mvc_at_vnnc_r6"]:,.0f}')

    print('\n=== 2. Phan ung theo r ===')
    rt = {}
    for r in (0.12, 0.125, 0.13, 0.135, 0.14, 0.145, 0.15):
        x, y, bb = EV8({'r': r}, detail=True)
        rt[f'{r:.3f}'] = dict(V_MVC=x, V_NNC=y, d_vs_135=x - vm, pct_vs_135=x / vm - 1, **{n: bb[n]['vm'] for n in bb})
        print(f'  r {r:.1%}: {x:7,.0f} ({x-vm:+6,.0f}; {x/vm-1:+.1%}) | V_NNC {y:,.0f} | ' + ' '.join(f'{n[:4]} {bb[n]["vm"]:,.0f}' for n in bb))
    out['r_table'] = rt
    print('\n=== 3. Do nhay lai huy dong ===')
    dep = {}
    for beta in (1.0, 0.5):
        for bp in (-100, -50, 50, 100):
            r = N6.r_of(DEP0 + bp / 1e4, beta); x, y, _ = EV8({'r': r}, detail=True)
            dep[f'b{beta}_{bp:+d}'] = dict(beta=beta, bp=bp, r=r, V_MVC=x, V_NNC=y, d=x - vm, pct=x / vm - 1)
            print(f'  beta {beta}: {bp:+d}bp -> r {r:.2%}: {x:7,.0f} ({x-vm:+6,.0f}; {x/vm-1:+.1%})')
    out['dep_sens'] = dep

    out['tl_margin_axis'] = {}
    for tm in TLMs:
        x, y, bb = EV8({'tl_m': tm}, detail=True)
        out['tl_margin_axis'][str(tm)] = dict(V_MVC=x, V_NNC=y, CYC=bb['CYCLICAL']['vm'], ADMIN=bb['ADMIN_GATED']['vm'])
    out['admin_axis'] = {am: EV8(admin=am) for am in AMs}
    out['branch_path'] = {f'{n}|{p}': dict(V_MVC=(x := branch(n, {'PW': {p: 1.0}}))['vm'], V_NNC=x['vn']) for n in CW for p in PATHS}
    keys = ['A', 'B', 'BOT', 'gach_xang', 'dat_o', 'LK_nho_ICD', 'Q4', 'NETFIN', 'Dm', 'stake', 'VM']
    br = {kk: sum(CW[n] * W0[k] * PW0[p] * b[n]['res'][(k, p)][kk] for n in CW for k in SCN for p in PATHS) for kk in keys}
    brc = {kk: sum(W0[k] * PW0[p] * b['CYCLICAL']['res'][(k, p)][kk] for k in SCN for p in PATHS) for kk in keys}
    out['bridge_ty'] = br; out['bridge_cyc_ty'] = brc
    print('\n=== 4. CAU NOI (ty; d/cp = x10) ===\n  ' + ' | '.join(f'{kk} {v:,.1f}' for kk, v in br.items()))
    print('  CYC: ' + ' | '.join(f'{kk} {v:,.1f}' for kk, v in brc.items()))

    print(f'\n=== 5. Gordon (ROE-g)/(r-g), r {R0:.1%} ===')
    roe_avg = float(np.mean(list(S.ROE_MVC.values())))
    st = {'STRUCTURAL': S.ROE_NOW, 'ADMIN_GATED': roe_avg, 'CYCLICAL': roe_avg}
    gor = {n: dict(roe=x, ps=(x - G) / (R0 - G) * S.BVPS, ps_r13=(x - G) / 0.10 * S.BVPS) for n, x in st.items()}
    rw = sum(CW[n] * st[n] for n in CW); gor['tron'] = dict(roe=rw, ps=(rw - G) / (R0 - G) * S.BVPS, ps_r13=(rw - G) / 0.10 * S.BVPS)
    for n, d in gor.items(): print(f'  {n:11s}: ROE {d["roe"]:5.1%} -> {d["ps"]:7,.0f} (r13 {d["ps_r13"]:,.0f})')
    cyc = b['CYCLICAL']['vm']; book_like = brc['B'] + brc['dat_o'] + brc['LK_nho_ICD'] + brc['Q4'] + brc['NETFIN']; ops = brc['A'] + brc['BOT'] + brc['gach_xang']
    out['gordon'] = gor
    out['dcf_vs_gordon_cyc'] = dict(DCF_CYC=cyc, stake_NNC_ps=brc['stake'] * 10, book_like_ps=book_like * 10, ops_ps=ops * 10, gordon_cyc=gor['CYCLICAL']['ps'],
                                    roe_implied_dcf_cyc=G + cyc / S.BVPS * (R0 - G))
    out['roe_implied_tam'] = G + vm / S.BVPS * (R0 - G)
    print(f'  ROE ham y tam {vm:,.0f}: {out["roe_implied_tam"]:.1%}')
    d0 = V8.debt_path('nnc', 0.07); out['debt'] = {'nnc|0.07': d0}
    print(f'  no rong (khong phu thuoc r): 2026 {d0["end2026"]:,.0f} | 2027 {d0["end2027"]:,.0f} | 2028 KV {d0["end2028_exp"]:,.0f}')

    print('\n=== 6. Luoi 118.098 bo (truc r 11,5/13,5/15,5) ===')
    args = list(itertools.product(R_AXIS, (0.85, 1.0, 1.15), (0.88, 0.91, 0.95), range(3), range(3), range(3), range(3), ('branch', '1.40'),
                                  (2035, 'W', 2045), AMs, TLMs))
    with Pool(8) as pool: grid = pool.map(_cell, args, chunksize=200)
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'  N={len(ge)}: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    out['grid_sub'] = {}
    for key in ('r', 'admin', 'tl_m'):
        for v in sorted(set(x[key] for x in grid), key=str):
            s_ = np.array([x['ev'] for x in grid if x[key] == v])
            out['grid_sub'][f'{key}={v}'] = dict(p10=float(np.percentile(s_, 10)), p50=float(np.median(s_)), p90=float(np.percentile(s_, 90)))
    with open('grid_r9.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (truoc CK thanh khoan): RE <= {:,.0f} | RE CO DK {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    print('\n=== 7. Do nhay (so voi tam r9) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV8(over, **kw); tor[lab] = x - vm; print(f'  {lab:70s} {x:8,.0f} ({x - vm:+7,.0f})')
    T('bien chu ky Tan Lap 25% (CHUA KIEM)', {'tl_m': 0.25}); T('bien chu ky Tan Lap 30% (CHUA KIEM)', {'tl_m': 0.30})
    T('anh xa ADMIN 0,5 vinh vien', admin='perm05'); T('anh xa ADMIN 1,0 tu 2028', admin='full')
    T('tran chu ky SL 1,40 (236,1k)', cap_basis='1.40')
    T('trong so nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('(+) upside doi thu het GP tu 2034', {'up2034': True})
    T('han GP Tan Lap 2035', {'endA': 2035}); T('han GP Tan Lap 2045', {'endA': 2045})
    T('chi phi Tan Lap +15%', {'ca': 1.15}); T('chi phi Tan Lap -15%', {'ca': 0.85}); T('REL 0,88', {'REL': 0.88}); T('REL 0,95', {'REL': 0.95})
    T('r 11,5%', {'r': 0.115}); T('r 15,5%', {'r': 0.155}); T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('mo moi: hai phia co trong so (upside + NPV gia xau)', {'up': True, 'mine_xau': True}); T('mo moi: bo rui ro tre GP', {'delay': False})
    T('holding 15%', {'hold': 0.15}); T('holding 30%', {'hold': 0.30})
    x1 = EV8({'VN_fix': 50000}); x2 = EV8({'VN_fix': 60000}); out['vnnc_slope_per10k'] = x2 - x1
    out['tornado'] = tor; out['bridge'] = dict(r8_r13=c13, r9_r135=vm)
    print(f'\n  Cau noi: r8 (r13) {c13:,.0f} -> r9 (r13,5) {vm:,.0f} ({vm-c13:+,.0f}; {vm/c13-1:+.1%}); do doc MVC/10k V_NNC {x2-x1:+,.0f}')
    with open('model_r9_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
