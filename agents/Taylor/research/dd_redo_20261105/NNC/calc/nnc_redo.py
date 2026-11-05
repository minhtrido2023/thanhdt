"""DD redo NNC 05/11/2026 (job Taylor_20261105_014135). Chay: $DNA_PYEXE -B nnc_redo.py  (tu thu muc calc nay)
Mo hinh dinh gia = nnc_model_r6 (dd_NNC_20261030/r6/calc, md5 khoa LOCK_md5_r6.txt) IMPORT, KHONG SUA. File nay chi:
 (1) doc lai lai huy dong 12T hieu dung tai 04/11/2026 -> r theo luat 21 (beta 1);
 (2) chuan hoa phan vi: LUOI CO TRONG SO = trang thai bien (STRUCTURAL/ADMIN_GATED/CYCLICAL, trong so Bobby 0,20/0,45/0,35)
     x K chi phi {0,87; 0,97; 1,07} x san luong nam thuong VRs {(1,05;1,05); (1,10;1,20); (1,20;1,30)} x duong gia PWs {70/30; 50/50; 30/70}
     x anh xa ADMIN {perm05; ramp; full}  = 243 o, trong so = xac suat trang thai x deu. r co dinh = r(04/11).
     (cap_basis '1.40' chi co chieu xuong -> de o do nhay, khong vao luoi doi xung.)
 (3) chiet khau thanh khoan tren ADV 250 phien toi 04/11/2026 (common.liquidity), gia 04/11/2026 tu tav2_bq.ticker.
"""
import os, sys, json, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../..')))
import common as C  # noqa: E402
R6D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r6/calc'))
sys.path.insert(0, R6D); _cwd = os.getcwd(); os.chdir(R6D)
import nnc_model_r6 as N6  # noqa: E402
os.chdir(_cwd)
import numpy as np  # noqa: E402

dep, dep_src = C.dep_now()
R = C.r_of(dep)
N6.R_ANCHOR = R                     # EV3r doc N6.R_ANCHOR luc goi
N5 = N6.N5
CW = N6.CW_BOBBY

out = dict(ticker='NNC', dep=dep, dep_src=dep_src, r=R)
vn, vm, b = N6.EV5(detail=True)
out['center_pre'] = vn; out['mvc_simul'] = vm
out['branches'] = {n: dict(w=CW[n], V_NNC=b[n][0], V_MVC=b[n][1]) for n in b}
out['control_r6_pin'] = dict(pin=60702, got=vn, diff=vn - 60702)

cells = []
for n, k, vi, pi, am in itertools.product(CW, (0.87, 0.97, 1.07), range(3), range(3), N5.AMs):
    x, y = N5.branch(n, {'K': k, 'PW': N5.PWs[pi]}, v_rev=N5.VRs[vi], admin=am)
    cells.append(dict(branch=n, K=k, VR=vi, PW=pi, admin=am, w=CW[n] / 81, V_NNC=x, V_MVC=y))
v = np.array([c['V_NNC'] for c in cells]); w = np.array([c['w'] for c in cells])
out['grid_n'] = len(cells); out['grid_wmean_pre'] = float((v * w).sum() / w.sum())
out['grid_pct_pre'] = C.wpct(v, w)

# so sanh: luoi r6 cu (4.374 o "ky vong", khong trong so) tai r 13,5%
import csv  # noqa: E402
g6 = [float(r['ev']) for r in csv.DictReader(open(os.path.join(R6D, 'grid_r6.csv'))) if abs(float(r['r']) - 0.135) < 1e-9]
out['r6_grid_r135'] = dict(n=len(g6), **{f'p{q}': float(np.percentile(g6, q)) for q in (10, 50, 90)})

# do nhay r (lai huy dong)
dsens = {}
for beta in (1.0, 0.5):
    for bp in (-100, -50, 50, 100):
        rr = C.R_ANCHOR + beta * (dep + bp / 1e4 - C.DEP_ANCHOR)
        x = N6.EV5({'r': rr}); dsens[f'b{beta}_{bp:+d}'] = dict(r=rr, V=x, d=x - vn, pct=x / vn - 1)
out['dep_sens'] = dsens

L = C.liquidity('NNC', ff=0.363); out['liq'] = L
d = L['d_ref']; f = 1 - d
out['center_post'] = vn * f
out['grid_pct_post'] = {q: p * f for q, p in out['grid_pct_pre'].items()}
px = L['price']; P = out['grid_pct_post']
out['price'] = px; out['price_date'] = L['price_date']
out['px_vs_center_post'] = px / out['center_post'] - 1
out['px_vs_p10_post'] = px / P[10] - 1; out['px_vs_p90_post'] = px / P[90] - 1
out['label'] = C.label(px, P[10], P[90])
out['label_pre'] = C.label(px, out['grid_pct_pre'][10], out['grid_pct_pre'][90])
out['share_cells_below_px_post'] = float(w[(v * f) < px].sum() / w.sum())

print(f"NNC redo | dep {dep:.2%} ({dep_src}) -> r {R:.2%}")
print(f"  tam truoc CK {vn:,.0f} (pin r6 60.702, lech {vn-60702:+.1f}) | MVC dong thoi {vm:,.0f}")
for n in b: print(f"   {n:11s} w {CW[n]:.2f}: {b[n][0]:,.0f}")
print(f"  luoi {len(cells)} o (trong so): TB {out['grid_wmean_pre']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in out['grid_pct_pre'].items()))
print(f"  [so sanh] luoi r6 ky-vong r13,5 n={len(g6)}: P10 {out['r6_grid_r135']['p10']:,.0f} P50 {out['r6_grid_r135']['p50']:,.0f} P90 {out['r6_grid_r135']['p90']:,.0f}")
for kk, s in dsens.items(): print(f"   dep {kk}: r {s['r']:.2%} -> {s['V']:,.0f} ({s['d']:+,.0f}; {s['pct']:+.1%})")
print(f"  thanh khoan {L['window']}: ADV trung vi {L['adv_med']/1e9:.2f} ty | ADV60 {L['adv_60']/1e9:.2f} | sigma {L['sigma_d']:.2%} | CK 5 ty Y1 {d:.2%} (ADV60: {L['d_ref_adv60']:.2%})")
for q, s in L['pos'].items(): print(f"   {q} ty: CK {s['disc']['Y0.5']:.1%}/{s['disc']['Y1.0']:.1%}/{s['disc']['Y1.5']:.1%} | phien thoat 10/20% {s['days']['p10']:.0f}/{s['days']['p20']:.0f}")
print(f"  tam SAU CK {out['center_post']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in P.items()))
print(f"  gia {px:,.0f} ({L['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | o duoi gia {out['share_cells_below_px_post']:.1%}")
json.dump(out, open(os.path.join(HERE, 'nnc_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
with open(os.path.join(HERE, 'grid_nnc_redo.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(cells[0])); wr.writeheader(); wr.writerows(cells)

# ---- SUMMARY.json (moi so lay tu `out` o tren; chu thich van ban o day) ----
GRID_DESC = (f"Luoi co trong so n={len(cells)}: trang thai bien (STRUCTURAL 0,20 / ADMIN_GATED 0,45 / CYCLICAL 0,35 - Bobby) x K chi phi 0,87/0,97/1,07 "
             "x san luong nam thuong 3 muc x duong gia g2031/real 70-30/50-50/30-70 x anh xa ADMIN perm05/ramp/full; trong so o = xac suat trang thai x deu; "
             f"r co dinh {R:.2%}. Phan vi co trong so. Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
CHANGE = ("Tam sau CK giu nguyen ban 03/11 (lai huy dong 12T hieu dung khong doi 7,40% -> r 13,5%; ADV 250 phien 2,10 ty nhu cu). "
          "Vung DOI DINH NGHIA: cu = P25-P75 cua luoi 'ky vong tung o' (trong so trang thai co dinh trong moi o, nen phan tan bi nen); "
          "moi = P10-P90 cua luoi co trang thai bien la mot TRUC => rong hon nhieu (P10 44,9k vs P10 cu sau CK 50,4k). Nhan doi tu 'RE (duoi P10)' "
          "sang 'TRONG vung' (gia sat P10) chu yeu do dinh nghia luoi, khong do co ban.")
WARN = ["Phap ly/quan tri (WARNING, khong loai): so huu cheo MVC 44,07% NNC <-> NNC 10,3% MVC (co the bi buoc thoai, can y kien phap ly)",
        "Ben lien quan NHC: 61% phai thu; 16% phan tang doanh thu Q3",
        "Truy thu/phat hanh chinh nho (0,63 ty 2024; 0,04 ty 2025); truy thu Nui Nho da du phong",
        "Bien da o dinh 15 nam (GPM Q3/2026 57,9%) - rui ro chu ky chiem uu the"]
OPEN = ["Thoi han hop dong cho thue Nui Nho chua xac minh (-2,0k den -3,4k/cp)",
        "Tra truoc dai han CNBP 59,2 ty chua ro ban chat (+2,1k/cp neu la tien thue da tra)",
        "Tam Lap 1 khu II chua co giay phep/tru luong cong bo (base = von da chi, NPV 0)",
        "Xac suat 3 trang thai bien la nhan dinh cua Bobby, khong phai tan suat do duoc"]
s = C.write_summary(out, os.path.join(HERE, '..', 'SUMMARY.json'), GRID_DESC, CHANGE, WARN, OPEN)
print(f"  SUMMARY: tam {s['center_post_liq']:,} P10 {s['p10_post']:,} P50 {s['p50_post']:,} P90 {s['p90_post']:,} | cu {s['zone_old']} | doi tam {s['center_change_pct']:+.1%}")
