"""Do nhay moat WIDE/NARROW/NONE cho DRI (job Taylor_20261107_120601). Exec dri_redo_r2.py (calc/) toi truoc buoc ghi file
(KHONG ghi de calc/), roi doi tham so moat tuong minh tren CUNG luoi 36 ket cuc. Chay: $DNA_PYEXE -B moat_sens_5f.py
 NARROW (hien hanh): Cref = C_cal tu LN 2025 cua chinh DRI (loi the gia thanh DA NAM trong mo hinh), mid = TB chu ky RSS3 thuc,
   tai canh NPV0 (RONIC=Ke), khong gia tri cuoi sau 2054 (L0).
 NONE: xoa loi the gia thanh: Cref += GAP x price(mid TB), GAP = GPM TB 2017-25 DRI - trung vi peer (DPR/PHR/GVR) cung nam.
 NONE_half: xoa 1/2 GAP.
 WIDE [UL minh hoa]: tai canh co RONIC>Ke: moi o = NQ15_NPV0 + S x PV(capex tai canh engine); bo nhanh KINH TE (NPV<0). S=0,25."""
import os, sys, io, csv, json, contextlib, builtins, statistics as st
CALC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../calc'))
src = builtins.open(os.path.join(CALC, 'dri_redo_r2.py'), encoding='utf-8').read().split("out['files_read']")[0]
g = {'__file__': os.path.join(CALC, 'dri_redo_r2.py'), '__name__': 'r2'}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, 'dri_redo_r2.py', 'exec'), g)
ns, CEN, grid, st_, WB, val, MID, f, px = g['ns'], g['CEN'], g['grid'], g['st_'], g['WB'], g['val'], g['MID'], g['f'], g['px']
base = st_(grid(WB), f, px); assert round(base['mean']) == 14092, base   # doi chung = pin r2

# GAP GPM tu BQ ticker_financial (Q4 rows, GPM_P0 TB quy), file do BQ xuat /tmp -> chep vao day
d = {}
for r in csv.DictReader(builtins.open('gpm_peers_bq.csv')): d.setdefault(r['yr'], {})[r['ticker']] = float(r['gpm']) if r['gpm'] else None
yrs = [y for y in sorted(d) if '2017' <= y <= '2025']
dri = st.mean(d[y]['DRI'] for y in yrs)
peer = st.mean(st.median([d[y][t] for t in ('DPR', 'PHR', 'GVR') if d[y].get(t) is not None]) for y in yrs)
GAP = dri - peer
P_TB = ns['price'](MID['TB']); C0 = CEN['Cref']
res = dict(gap=dict(dri_gpm_2017_25=dri, peer_median_gpm_2017_25=peer, gap=GAP, years=yrs), Cref=C0, price_TB=P_TB, NARROW=base)
for lab, fr in (('NONE', 1.0), ('NONE_half', 0.5)):
    CEN['Cref'] = C0 + fr * GAP * P_TB
    res[lab] = st_(grid(WB), f, px); res[lab]['Cref'] = CEN['Cref']
CEN['Cref'] = C0
# WIDE: PV capex tai canh = val(ECON, capex=0) - val(ECON)
S = 0.25; cx3 = ns['capex3']
def pvcx(mid, L, p):
    e = val('NQ15_ECON', MID[mid], L, scn=p); ns['capex3'] = lambda pl, m: {}
    try: e0 = val('NQ15_ECON', MID[mid], L, scn=p)
    finally: ns['capex3'] = cx3
    return e0 - e
rows = grid({'NQ15_NPV0': 1.0})
pv_tb = pvcx('TB', 27, None)
for r in rows: r['V'] = r['V'] + S * pvcx(r['mid'], r['L'], r['path'])
res['WIDE'] = st_(rows, f, px); res['WIDE'].update(S=S, pv_capex_point_TB_L27=pv_tb)
json.dump(res, builtins.open('moat_sens_5f_out.json', 'w'), indent=1, default=float, sort_keys=True)
for k in ('NARROW', 'NONE_half', 'NONE', 'WIDE'):
    s = res[k]; print(f"{k:10s} tam {s['mean']:7,.0f} ({s['mean']-base['mean']:+,.0f}; {s['mean']/base['mean']-1:+.1%}) P10 {s['p10']:7,.0f} P50 {s['p50']:7,.0f} P90 {s['p90']:7,.0f} duoi gia {s['below']:.1%} nhan {g['C'].label(px, s['p10'], s['p90'])}")
print(f"GAP GPM {dri:.3f}-{peer:.3f}={GAP:.3f} | Cref {C0:.2f} -> NONE {res['NONE']['Cref']:.2f} tr/t | price TB {P_TB:.2f} | PV capex tai canh (TB,L27) {pv_tb:,.0f} d/cp")
