"""DD redo DRI 05/11/2026 (job Taylor_20261105_014135). Chay: $DNA_PYEXE -B dri_redo.py
Engine = dri_val_supply_adj_r4_20261027/model.py, nap Y HET cach dri_model_r5.py (exec, `open` chuyen huong sang snapshot
dd_DRI_20261027/r5/calc/data/, assert khong doc file song). KHONG sua file cu; khong ghi vao thu muc cu.
Thay doi so voi r5: (1) r doc lai lai huy dong hieu dung 04/11/2026 (luat 21, beta 1); (2) LUOI CHUAN HOA lien ma:
kich ban {co so NPV0 0,80 ; tai canh bi buoc 0,20} x mid RSS3 thuc {P25 .25, TB .5, P75 .25} x doi cao L {22 .25, 27 .5, 32 .25}
= 18 o co trong so, r CO DINH = r(04/11) (r6/r5 cu de r la mot truc luoi); (3) thanh khoan ADV 250 phien toi 04/11/2026, gia 04/11.
"""
import os, sys, io, csv, json, builtins, contextlib, itertools, statistics as st
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../..')))
import common as C  # noqa: E402
import numpy as np  # noqa: E402
R5 = os.path.abspath(os.path.join(HERE, '../../../dd_DRI_20261027/r5/calc'))
WC = '/home/trido/thanhdt/WorkingClaude/data'
REDIR = {f'{WC}/rubber_monthly.csv': os.path.join(R5, 'data/rubber_monthly_snapshot_20261103.csv'),
         f'{WC}/macro_usdvnd.csv': os.path.join(R5, 'data/macro_usdvnd_snapshot_20261103.csv')}
SEEN = []


def _open(p, *a, **k):
    p2 = REDIR.get(os.path.abspath(str(p)), p)
    assert not str(p2).startswith(WC), f'doc file song {p2}'
    SEEN.append(os.path.abspath(str(p2))); return builtins.open(p2, *a, **k)


ENG = os.path.abspath(os.path.join(HERE, '../../../dri_val_supply_adj_r4_20261027/model.py'))
ns = {'__file__': ENG, '__name__': 'eng', 'open': _open}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(builtins.open(ENG, encoding='utf-8').read(), ENG, 'exec'), ns)
assert all(not s.startswith(WC) for s in SEEN)
fvph, CEN, SH = ns['fvph'], ns['CEN'], ns['SH']
CIP = 72.712702447; CIPPS = CIP * 1e9 / SH            # XDCB 30/09/2026 [BCTC HN Q3 ma 252] (nhu r5)

dep, dep_src = C.dep_now(); R = C.r_of(dep)


def base(mid, L=27, r=R):
    CEN['r'] = r; return fvph(mid, 2029, L, R_on=False, new_on=False) + CIPPS


def forced(mid, L=27, r=R):
    CEN['r'] = r; return fvph(mid, 2029, L) + CIPPS


def liqread(mid, L=27, r=R):
    CEN['r'] = r; return fvph(mid, 2029, L, new_on=False) + CIPPS


# mid: y het r5 (CPI-U FRED snapshot, RSS3 thuc USD2025, cua so 2014-01..2026-09)
cpi = {r['observation_date'][:7]: float(r['CPIAUCSL']) for r in csv.DictReader(builtins.open(os.path.join(R5, 'data/fred_cpiaucsl_20261103.csv'))) if r['CPIAUCSL']}
cpi['2025-10'] = (cpi['2025-09'] + cpi['2025-11']) / 2
rss = [(m, float(p)) for m, p in csv.reader(builtins.open(os.path.join(R5, 'data/rubber_monthly_snapshot_20261103.csv'))) if m != 'month']
c25 = st.mean([cpi[f'2025-{i:02d}'] for i in range(1, 13)])
real = {m: p * c25 / cpi[m] for m, p in rss if m in cpi}
w = [v for m, v in real.items() if '2014-01' <= m <= '2026-09']


def pct(xs, q):
    xs = sorted(xs); i = q * (len(xs) - 1); lo = int(i); return xs[lo] + (xs[min(lo + 1, len(xs) - 1)] - xs[lo]) * (i - lo)


MID = {'P25': pct(w, .25), 'TB': st.mean(w), 'P75': pct(w, .75)}
out = dict(ticker='DRI', dep=dep, dep_src=dep_src, r=R, mids=MID)
# chan doi chung: tam base r5 15.860 @ r 13,5%
out['control_r5'] = dict(pin=15860, got=base(MID['TB'], 27, 0.135))

WM = {'P25': .25, 'TB': .5, 'P75': .25}; WL = {22: .25, 27: .5, 32: .25}; WS = {'co_so_NPV0': 0.80, 'tai_canh_bi_buoc': 0.20}
FN = {'co_so_NPV0': base, 'tai_canh_bi_buoc': forced}
cells = [dict(scen=s, mid=mk, L=L, w=ws * wm * wl, v=FN[s](MID[mk], L)) for (s, ws), (mk, wm), (L, wl) in itertools.product(WS.items(), WM.items(), WL.items())]
v = np.array([c['v'] for c in cells]); wt = np.array([c['w'] for c in cells])
out['center_pre'] = float((v * wt).sum() / wt.sum())        # = 0,8 x TB(base) + 0,2 x TB(bi buoc), r co dinh
out['scen_mean'] = {s: float(sum(c['v'] * c['w'] for c in cells if c['scen'] == s) / WS[s]) for s in WS}
out['center_base_point'] = base(MID['TB']); out['forced_point'] = forced(MID['TB']); out['liqread_point'] = liqread(MID['TB'])
out['grid_n'] = len(cells); out['grid_pct_pre'] = C.wpct(v, wt)
dsens = {}
for beta in (1.0, 0.5):
    for bp in (-100, -50, 50, 100):
        rr = C.R_ANCHOR + beta * (dep + bp / 1e4 - C.DEP_ANCHOR)
        x = sum(c['w'] * FN[c['scen']](MID[c['mid']], c['L'], rr) for c in cells)
        dsens[f'b{beta}_{bp:+d}'] = dict(r=rr, V=x, d=x - out['center_pre'], pct=x / out['center_pre'] - 1)
out['dep_sens'] = dsens
out['p_forced_sens'] = {str(p): (1 - p) * out['scen_mean']['co_so_NPV0'] + p * out['scen_mean']['tai_canh_bi_buoc'] for p in (0.0, 0.1, 0.2, 0.3)}

L_ = C.liquidity('DRI', ff=0.55); out['liq'] = L_; f = 1 - L_['d_ref']
out['center_post'] = out['center_pre'] * f
out['grid_pct_post'] = {q: p * f for q, p in out['grid_pct_pre'].items()}
px = L_['price']; P = out['grid_pct_post']
out.update(price=px, price_date=L_['price_date'], px_vs_center_post=px / out['center_post'] - 1, px_vs_p10_post=px / P[10] - 1,
           px_vs_p90_post=px / P[90] - 1, label=C.label(px, P[10], P[90]), share_cells_below_px_post=float(wt[(v * f) < px].sum() / wt.sum()))

print(f"DRI redo | dep {dep:.2%} ({dep_src}) -> r {R:.2%} | mid P25/TB/P75 {MID['P25']:.3f}/{MID['TB']:.3f}/{MID['P75']:.3f}")
print(f"  chan doi chung base r13,5 = {out['control_r5']['got']:,.0f} (pin r5 15.860)")
print(f"  diem: base {out['center_base_point']:,.0f} | bi buoc {out['forced_point']:,.0f} | dien giai thanh ly {out['liqread_point']:,.0f}")
print(f"  TB kich ban: " + ' | '.join(f"{s} {x:,.0f}" for s, x in out['scen_mean'].items()) + f" | p_forced: " + ' '.join(f"p{k} {x:,.0f}" for k, x in out['p_forced_sens'].items()))
print(f"  luoi {len(cells)} o: tam (TB co trong so) {out['center_pre']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in out['grid_pct_pre'].items()))
for kk, s in dsens.items(): print(f"   dep {kk}: r {s['r']:.2%} -> {s['V']:,.0f} ({s['d']:+,.0f}; {s['pct']:+.1%})")
print(f"  thanh khoan {L_['window']}: ADV trung vi {L_['adv_med']/1e9:.2f} ty | ADV60 {L_['adv_60']/1e9:.2f} | sigma {L_['sigma_d']:.2%} | CK 5 ty {L_['d_ref']:.2%}")
for q, s in L_['pos'].items(): print(f"   {q} ty: CK {s['disc']['Y0.5']:.1%}/{s['disc']['Y1.0']:.1%}/{s['disc']['Y1.5']:.1%} | phien thoat 10/20% {s['days']['p10']:.1f}/{s['days']['p20']:.1f}")
print(f"  tam SAU CK {out['center_post']:,.0f} | " + ' '.join(f"P{q} {p:,.0f}" for q, p in P.items()))
print(f"  gia {px:,.0f} ({out['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | o duoi gia {out['share_cells_below_px_post']:.1%}")
json.dump(out, open(os.path.join(HERE, 'dri_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
with open(os.path.join(HERE, 'grid_dri_redo.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(cells[0])); wr.writeheader(); wr.writerows(cells)

GRID_DESC = (f"Luoi co trong so n={len(cells)}: kich ban (co so NPV0 tai canh 0,80 / tai canh bi buoc 0,20 - nhan dinh) x mid RSS3 thuc "
             f"P25/TB/P75 (2014-01..2026-09; trong so .25/.5/.25) x doi cao L 22/27/32 (gia dinh; .25/.5/.25); r co dinh {R:.2%}. "
             "Phan vi co trong so. Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
CHANGE = ("Tam cu 14.360 = 0,8xTB luoi base + 0,2xTB luoi bi buoc TREN luoi co truc r 11,5/13,5/15,5 (ham loi theo r keo TB len) va CK 2,0% "
          "(ADV 8,33 ty toi 02/11). Moi: r co dinh 13,5% (lai huy dong khong doi), ADV toi 04/11. Vung cu = P25-P75 luoi base; moi = P10-P90 "
          "luoi co kich ban la truc => cận dưới thap hon nhieu (gom ca nhanh bi buoc).")
WARN = ["Phap ly/quan tri (WARNING): cho Dakruco (co dong ~45%) vay con 40 ty, TSDB 6 tr cp DRI",
        "NQ HDQT 15 (11/2026): nghien cuu mua Dakruwood tu Dakruco - giao dich ben lien quan (HDQT xet 12/2026)",
        "Tien gui Quy TDND Cao su Dak Lak 70 ty + gop von 3 ty (kiem toan ban nien chua xac dinh gia tri thu hoi khoan gop)",
        "~197 ty tien tai Lao khong thuyet minh nguyen te/lai suat/ky han; van ban to nhuong chua cong khai; mot phan dat thuoc quy hoach rung bao ton"]
OPEN = ["Hop dong to nhuong 01616/KD/DDT4 chua xac minh (quyet dinh p tai canh bi buoc = 20% nhan dinh)",
        "Doi cao L 22/27/32 la gia dinh, khong co dinh muc nguon",
        "SXKD thang 10 (~10/11/2026) - kiem toc do ban hang ton 1.717 t",
        "Chuyen san HOSE Q4/2026 chua co chap thuan"]
s = C.write_summary(out, os.path.join(HERE, '..', 'SUMMARY.json'), GRID_DESC, CHANGE, WARN, OPEN)
print(f"  SUMMARY: tam {s['center_post_liq']:,} P10 {s['p10_post']:,} P50 {s['p50_post']:,} P90 {s['p90_post']:,} | cu {s['zone_old']['low']}/{s['zone_old']['center']}/{s['zone_old']['high']} | doi tam {s['center_change_pct']:+.1%}")
