"""DD redo MVC 05/11/2026 (job Taylor_20261105_014135). Chay: $DNA_PYEXE -B mvc_redo.py
He thong = MVC r9 (dd_MVC_20261103/r9/calc/model_r9.py): nnc_model_r6 (tiem r) + model_r8 (Tan Lap, mo moi NPV0, V_NNC giai dong thoi) — IMPORT, KHONG SUA,
nap dung thu tu r9. File nay: (1) r tu lai huy dong hieu dung 04/11/2026 (luat 21, beta 1); (2) LUOI CHUAN HOA co trong so:
trang thai bien (STRUCTURAL/ADMIN_GATED/CYCLICAL 0,20/0,45/0,35) x chi phi Tan Lap ca {0,85;1,0;1,15} x REL gia Tan Lap/NNC {0,88;0,91;0,95}
x duong gia PWs {70/30;50/50;30/70} x san luong VRs 3 muc x han GP Tan Lap {2035; W; 2045} x anh xa ADMIN {perm05; ramp; full} = 2.187 o,
trong so = xac suat trang thai x deu; r co dinh. (Bien chu ky Tan Lap 25/30% chi chieu xuong so voi ~NNC -> de o do nhay.)
(3) thanh khoan ADV 250 phien toi 04/11/2026 (common.liquidity), gia 04/11/2026.
"""
import os, sys, json, csv, itertools
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../..')))
import common as C  # noqa: E402
import numpy as np  # noqa: E402
N6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
R8D = os.path.abspath(os.path.join(HERE, '../../../dd_MVC_20261103/r8/calc'))
sys.path.insert(0, N6D); _cwd = os.getcwd(); os.chdir(N6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd); sys.path.insert(0, R8D)
import model_r8 as V8  # noqa: E402
assert V8.N3 is N6.N3 and V8.N3.EV3 is N6.EV3r

dep, dep_src = C.dep_now(); R = C.r_of(dep); N6.R_ANCHOR = R
CW = V8.CW
AX = dict(ca=(0.85, 1.0, 1.15), REL=(0.88, 0.91, 0.95), PW=range(3), VR=range(3), endA=(2035, 'W', 2045), admin=V8.AMs)


def _cell(a):
    n, ca, rel, pi, vi, en, am = a
    b = V8.branch(n, {'ca': ca, 'REL': rel, 'PW': V8.PWs[pi], 'endA': en}, v_rev=V8.VRs[vi], admin=am)
    return dict(branch=n, ca=ca, REL=rel, PW=pi, VR=vi, endA=en, admin=am, w=CW[n] / 729, V_MVC=b['vm'], V_NNC=b['vn'])


if __name__ == '__main__':
    out = dict(ticker='MVC', dep=dep, dep_src=dep_src, r=R)
    vm, vn, b = V8.EV8(detail=True)
    out['center_pre'] = vm; out['V_NNC_simul'] = vn
    out['branches'] = {n: dict(w=CW[n], V_MVC=b[n]['vm'], V_NNC=b[n]['vn']) for n in b}
    out['control_r9_pin'] = dict(pin=16482, got=vm)
    base_cell = _cell(('ADMIN_GATED', 1.0, 0.91, 1, 1, 'W', 'ramp'))['V_MVC']
    out['check_base_cell_admin'] = dict(cell=base_cell, branch=b['ADMIN_GATED']['vm'])
    args = list(itertools.product(CW, *AX.values()))
    with Pool(8) as pool: cells = pool.map(_cell, args, chunksize=20)
    v = np.array([c['V_MVC'] for c in cells]); w = np.array([c['w'] for c in cells])
    out['grid_n'] = len(cells); out['grid_wmean_pre'] = float((v * w).sum() / w.sum()); out['grid_pct_pre'] = C.wpct(v, w)
    r9 = [float(x['ev']) for x in csv.DictReader(open(os.path.abspath(os.path.join(HERE, '../../../dd_MVC_20261103/r9/calc/grid_r9.csv')))) if abs(float(x['r']) - 0.135) < 1e-9]
    out['r9_grid_r135'] = dict(n=len(r9), **{f'p{q}': float(np.percentile(r9, q)) for q in (10, 50, 90)})
    dsens = {}
    for beta in (1.0, 0.5):
        for bp in (-100, -50, 50, 100):
            rr = C.R_ANCHOR + beta * (dep + bp / 1e4 - C.DEP_ANCHOR); x = V8.EV8({'r': rr})
            dsens[f'b{beta}_{bp:+d}'] = dict(r=rr, V=x, d=x - vm, pct=x / vm - 1)
    out['dep_sens'] = dsens
    out['tl_margin_sens'] = {str(t): V8.EV8({'tl_m': t}) for t in (0.25, 0.30)}
    L = C.liquidity('MVC', ff=0.302); out['liq'] = L; f = 1 - L['d_ref']
    out['center_post'] = vm * f
    out['grid_pct_post'] = {q: p * f for q, p in out['grid_pct_pre'].items()}
    px = L['price']; P = out['grid_pct_post']
    out.update(price=px, price_date=L['price_date'], px_vs_center_post=px / out['center_post'] - 1, px_vs_p10_post=px / P[10] - 1,
               px_vs_p90_post=px / P[90] - 1, label=C.label(px, P[10], P[90]), share_cells_below_px_post=float(w[(v * f) < px].sum() / w.sum()))
    print(f"MVC redo | dep {dep:.2%} ({dep_src}) -> r {R:.2%}")
    print(f"  tam truoc CK {vm:,.0f} (pin r9 16.482, lech {vm-16482:+.1f}) | V_NNC dong thoi {vn:,.0f} | kiem o co so ADMIN {base_cell:,.0f} vs nhanh {b['ADMIN_GATED']['vm']:,.0f}")
    for n in b: print(f"   {n:11s} w {CW[n]:.2f}: MVC {b[n]['vm']:,.0f} | NNC {b[n]['vn']:,.0f}")
    print(f"  luoi {len(cells)} o (trong so): TB {out['grid_wmean_pre']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in out['grid_pct_pre'].items()))
    print(f"  [so sanh] luoi r9 ky-vong r13,5 n={len(r9)}: P10 {out['r9_grid_r135']['p10']:,.0f} P50 {out['r9_grid_r135']['p50']:,.0f} P90 {out['r9_grid_r135']['p90']:,.0f}")
    for kk, s in dsens.items(): print(f"   dep {kk}: r {s['r']:.2%} -> {s['V']:,.0f} ({s['d']:+,.0f}; {s['pct']:+.1%})")
    print(f"   bien Tan Lap 25%/30%: {out['tl_margin_sens']['0.25']:,.0f} / {out['tl_margin_sens']['0.3']:,.0f}")
    print(f"  thanh khoan {L['window']}: ADV trung vi {L['adv_med']/1e9:.2f} ty | ADV60 {L['adv_60']/1e9:.2f} | sigma {L['sigma_d']:.2%} | phien 0 KL {L['zero_vol_share']:.1%} | CK 5 ty {L['d_ref']:.2%} (ADV60 {L['d_ref_adv60']:.2%})")
    for q, s in L['pos'].items(): print(f"   {q} ty: CK {s['disc']['Y0.5']:.1%}/{s['disc']['Y1.0']:.1%}/{s['disc']['Y1.5']:.1%} | phien thoat 10/20% {s['days']['p10']:.0f}/{s['days']['p20']:.0f}")
    print(f"  tam SAU CK {out['center_post']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in P.items()))
    print(f"  gia {px:,.0f} ({out['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | o duoi gia {out['share_cells_below_px_post']:.1%}")
    json.dump(out, open(os.path.join(HERE, 'mvc_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    with open(os.path.join(HERE, 'grid_mvc_redo.csv'), 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(cells[0])); wr.writeheader(); wr.writerows(cells)
    GRID_DESC = (f"Luoi co trong so n={len(cells)}: trang thai bien (0,20/0,45/0,35 - Bobby) x chi phi Tan Lap 0,85/1,0/1,15 x REL 0,88/0,91/0,95 "
                 "x duong gia 70-30/50-50/30-70 x san luong nam thuong 3 muc x han GP Tan Lap 2035/W/2045 x anh xa ADMIN 3 muc; trong so o = xac suat "
                 f"trang thai x deu; r co dinh {R:.2%}; V_NNC giai dong thoi trong tung o. Ban SAU = x (1 - CK thanh khoan 5 ty, Y=1,0).")
    CHANGE = ("Tam truoc CK = r9 (r 13,5% khong doi). CK thanh khoan 5 ty doi theo ADV 250 phien toi 04/11 (cu 8,4% @ ADV 0,45 ty toi 03/11). "
              "Vung cu = P25-P75 luoi 'ky vong tung o' sau CK; moi = P10-P90 luoi co trang thai la truc (rong hon).")
    WARN = ["Phap ly/quan tri (WARNING): so huu cheo MVC 44,07% NNC <-> NNC 10,3% MVC",
            "Mo moi ~1.500 ty von: giay phep/tien do chua chac (base NPV0 theo so sach, luat 03/11)",
            "Vay ngan han lon; no rong du kien ~1.070 ty cuoi 2028 (r8, lai suat gia dinh 7%)",
            "Thanh khoan rat thap (ADV trung vi < 0,5 ty/phien) - rui ro thuc thi lon nhat trong 3 ma"]
    OPEN = ["Bien chu ky mang da Tan Lap CHUA KIEM (khong co bo phan rieng): 25%/30% cho tam thap hon",
            "Free float 30,2% uoc tu 4 co dong lon (BCTN 2025)",
            "Xac suat 3 trang thai la nhan dinh cua Bobby"]
    s = C.write_summary(out, os.path.join(HERE, '..', 'SUMMARY.json'), GRID_DESC, CHANGE, WARN, OPEN)
    print(f"  SUMMARY: tam {s['center_post_liq']:,} P10 {s['p10_post']:,} P50 {s['p50_post']:,} P90 {s['p90_post']:,} | cu {s['zone_old']['low']}/{s['zone_old']['center']}/{s['zone_old']['high']} | doi tam {s['center_change_pct']:+.1%}")
