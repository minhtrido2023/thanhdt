"""DD redo DRI VONG 2 (05/11/2026, job Taylor_20261105_020023). Chay: $DNA_PYEXE -B dri_redo_r2.py (tu thu muc calc nay).
Engine = dri_val_supply_adj_r4_20261027/model.py (exec nguyen van; no exec tiep r3/model.py; open chuyen huong snapshot 03/11). KHONG sua.
Vong 2 theo STANDARD_r2.md + E_CORRECTIONS.md (DRI):
 (1) MUC KET CUC: moi o -> 2 ket cuc duong gia PEAK / MID (trong so wp 0,6/0,4 [UL], khai ro); phan vi _shared/wpct.py.
 (2) BASE: bo haircut 50% khoan vay Dakruco 40 ty (dang tra dung han) va bo 'giu lai 15% tien Lao' (DOAN, [UL]) -> do nhay/WARNING.
 (3) NQ HDQT 15 (04/11/2026) Dieu 4 = DU LIEU: dau gia thanh ly 1.975,23 ha theo lich 2027-2030, gia khoi diem 36 tr LAK/ha
     (~41,05 tr VND/ha @1,1404 VND/LAK) thay wood_ha 20,87 (uoc tu ~54 ha); Dieu 3: tai canh dot 1 2028-2031 tren cung dien tich.
     Hai cach doc: NQ15-NPV0 (thanh ly theo lich NQ15, tai canh = du an moi NPV 0 - luat 20) vs NQ15-KINH TE (thanh ly + tai canh voi
     kinh te engine m7 = nhanh 'bi buoc' cu). Ban cu (giu vuon toi L27, bo qua NQ15) bao SONG SONG.
 (4) Thanh khoan: CK 5 ty (Q/ADV250 0,6x) va co sleeve that 10/40 trieu; ADV250 va ADV60.
"""
import os, sys, io, csv, json, math, builtins, contextlib, itertools, statistics as st
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
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
fvph, CEN, SH = ns['fvph'], ns['CEN'], ns['SH']
CIP = 72.712702447; CIPPS = CIP * 1e9 / SH
dep, dep_src = C.dep_now(); R = C.r_of(dep)

ORIG = dict(DKR=ns['DKR'], h=CEN['h'], wood_ha=ns['wood_ha'], R_LEFT=ns['R_LEFT'], WIN=ns['WIN'], reinv=0.9)
LAK = 1.1404; WOOD_NQ15 = 36.0 * LAK              # tr VND/ha (NQ HDQT 15 Dieu 4; ty gia theo E_CORRECTIONS)
NQ15_HA, NQ15_S, NQ15_WIN = 1975.23, 2027, 4


def setcfg(dkr=40.0, h=0.0, wood=WOOD_NQ15):
    ns['DKR'] = dkr; CEN['h'] = h; ns['wood_ha'] = wood


def val(read, mid, L, scn=None, r=R):
    """read: 'NQ15_NPV0' | 'NQ15_ECON' | 'KEEP_L27' (ban cu) | 'ENG_FORCED' (bi buoc lich engine 3.949 ha 2029-36)."""
    CEN['r'] = r
    if read in ('NQ15_NPV0', 'NQ15_ECON'):
        ns['R_LEFT'], ns['WIN'] = NQ15_HA, NQ15_WIN
        try:
            return fvph(mid, NQ15_S, L, new_on=(read == 'NQ15_ECON'), scn=scn) + CIPPS
        finally:
            ns['R_LEFT'], ns['WIN'] = ORIG['R_LEFT'], ORIG['WIN']
    if read == 'KEEP_L27':
        return fvph(mid, 2029, L, R_on=False, new_on=False, scn=scn) + CIPPS
    return fvph(mid, 2029, L, scn=scn) + CIPPS


# ---- mid RSS3 thuc (y het vong 1) ----
cpi = {r['observation_date'][:7]: float(r['CPIAUCSL']) for r in csv.DictReader(builtins.open(os.path.join(R5, 'data/fred_cpiaucsl_20261103.csv'))) if r['CPIAUCSL']}
cpi['2025-10'] = (cpi['2025-09'] + cpi['2025-11']) / 2
rss = [(m, float(p)) for m, p in csv.reader(builtins.open(os.path.join(R5, 'data/rubber_monthly_snapshot_20261103.csv'))) if m != 'month']
c25 = st.mean([cpi[f'2025-{i:02d}'] for i in range(1, 13)])
real = {m: p * c25 / cpi[m] for m, p in rss if m in cpi}
wv = sorted(v for m, v in real.items() if '2014-01' <= m <= '2026-09')
def pq(xs, q): i = q * (len(xs) - 1); lo = int(i); return xs[lo] + (xs[min(lo + 1, len(xs) - 1)] - xs[lo]) * (i - lo)
MID = {'P25': pq(wv, .25), 'TB': st.mean(wv), 'P75': pq(wv, .75)}

out = dict(ticker='DRI', dep=dep, dep_src=dep_src, r=R, mids=MID, wood_nq15_tr_per_ha=WOOD_NQ15, wood_old_tr_per_ha=ORIG['wood_ha'])
# chan doi chung: cau hinh vong 1 (DKR 20, h 0,15, wood cu) tai lap pin r5 15.860 / vong 1 forced 11.924
setcfg(ORIG['DKR'], ORIG['h'], ORIG['wood_ha'])
out['control'] = dict(keep_r1=val('KEEP_L27', MID['TB'], 27), forced_r1=val('ENG_FORCED', MID['TB'], 27))
assert round(out['control']['keep_r1']) == 15860 and round(out['control']['forced_r1']) == 11924, out['control']
# cau noi base: tung buoc
br = {}
setcfg(40.0, ORIG['h'], ORIG['wood_ha']); br['+bo haircut Dakruco'] = val('KEEP_L27', MID['TB'], 27)
setcfg(40.0, 0.0, ORIG['wood_ha']); br['+bo giu 15% tien Lao'] = val('KEEP_L27', MID['TB'], 27)
setcfg(40.0, 0.0, WOOD_NQ15); br['+wood_ha = gia khoi diem NQ15'] = val('KEEP_L27', MID['TB'], 27)
br['+doc NQ15-NPV0 (lich thanh ly 1.975 ha 2027-30)'] = val('NQ15_NPV0', MID['TB'], 27)
br['(nhanh) NQ15-KINH TE (tai canh kinh te engine m7)'] = val('NQ15_ECON', MID['TB'], 27)
br['(doi chieu) bi buoc lich engine 3.949 ha 2029-36'] = val('ENG_FORCED', MID['TB'], 27)
out['bridge_point_TB_L27'] = br

# ---- luoi muc ket cuc ----
WB = {'NQ15_NPV0': 0.80, 'NQ15_ECON': 0.20}            # 0,20 = trong so nhanh 'bi buoc' cu (nhan dinh, [UL]) - giu de so sanh
WM = {'P25': .25, 'TB': .5, 'P75': .25}; WL = {22: .25, 27: .5, 32: .25}; WP = {'PEAK': 0.6, 'MID': 0.4}


def grid(wb, wp=WP):
    rows = []
    for (b, w1), (mk, w2), (L, w3) in itertools.product(wb.items(), WM.items(), WL.items()):
        for p, w4 in wp.items():
            if w1 * w4 == 0: continue
            rows.append(dict(read=b, mid=mk, L=L, path=p, w=w1 * w2 * w3 * w4, V=val(b, MID[mk], L, scn=p)))
    return rows


def st_(rows, f=1.0, px=None):
    v = np.array([r['V'] for r in rows]) * f; w = np.array([r['w'] for r in rows]); p = wpct(v, w)
    o = dict(n=len(rows), mean=float((v * w).sum() / w.sum()), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(v.min()), max=float(v.max()))
    if px: o['below'] = weight_below(v, w, px)
    return o


setcfg()
rows = grid(WB); assert abs(sum(r['w'] for r in rows) - 1) < 1e-9
# kiem: trung binh 2 duong = fvph (wp 0,6)
assert abs(0.6 * val('NQ15_NPV0', MID['TB'], 27, 'PEAK') + 0.4 * val('NQ15_NPV0', MID['TB'], 27, 'MID') - val('NQ15_NPV0', MID['TB'], 27)) < 1e-6
L_ = C.liquidity('DRI', ff=0.55, qs=(0.01e9, 0.04e9, 1e9, 5e9)); out['liq'] = L_
d_ref = L_['pos']['5']['disc']['Y1.0']; f = 1 - d_ref; px = L_['price']
out['ck_ref'] = dict(size_bn=5, Y=1.0, adv250=d_ref, adv60=L_['d_ref_adv60'], q_over_adv250=5e9 / L_['adv_med'], q_over_adv60=5e9 / L_['adv_60'])
out['ck_real_sleeve'] = {f'{q/1e6:.0f}tr': dict(adv250=L_['sigma_d'] * math.sqrt(q / L_['adv_med']), adv60=L_['sigma_d'] * math.sqrt(q / L_['adv_60'])) for q in (0.01e9, 0.04e9)}
out['pre'] = st_(rows, 1.0, px); out['post'] = st_(rows, f, px)
out['n_outcomes'] = len(rows); out['n_cells'] = len(rows) // 2
out['center_param_pre'] = 0.8 * val('NQ15_NPV0', MID['TB'], 27) + 0.2 * val('NQ15_ECON', MID['TB'], 27)
out['branch_post'] = {b: st_([r for r in rows if r['read'] == b], f, px) for b in WB}
# song song: ban cu (giu vuon L27 thay NQ15-NPV0; bi buoc lich engine) voi base da sua
out['parallel_keepL27'] = st_(grid({'KEEP_L27': 0.8, 'ENG_FORCED': 0.2}), f, px)
out['parallel_NQ15_npv0_only'] = st_(grid({'NQ15_NPV0': 1.0}), f, px)
# nhay trong so nhanh kinh te / wp / reinv / haircut
out['sens_w_econ'] = {f'{p:.1f}': st_(grid({'NQ15_NPV0': 1 - p, 'NQ15_ECON': p}) if p < 1 else grid({'NQ15_ECON': 1.0}), f, px) for p in (0.0, 0.1, 0.3, 0.5)}
out['sens_wp'] = {}
for wp in (0.0, 0.5, 1.0):
    out['sens_wp'][f'{wp:.1f}'] = st_(grid(WB, {'PEAK': wp, 'MID': 1 - wp}), f, px)
sens = {}
def S(lab, **cfg):
    setcfg(**cfg); sens[lab] = st_(grid(WB), f, px)['mean']; setcfg()
S('(-) haircut 50% khoan vay Dakruco 40 ty (cu)', dkr=20.0); S('(-) giu 15% tien Lao (cu)', h=0.15); S('(-) ca hai (cau hinh cu)', dkr=20.0, h=0.15)
S('(-) khoan vay Dakruco mat trang 40 ty', dkr=0.0); S('wood_ha cu 20,87 tr/ha', wood=ORIG['wood_ha'])
setcfg()
for rv in (0.8, 1.0):
    _fv4 = ns['fv4']
    def fv4r(*a, _f=_fv4, _rv=rv, **k): k['reinv'] = _rv; return _f(*a, **k)
    ns['fv4'] = fv4r
    try: sens[f'FCF/LN loi {rv:.0%} (base 90% [UL])'] = st_(grid(WB), f, px)['mean']
    finally: ns['fv4'] = _fv4
out['sens_mean_post'] = sens
dsens = {}
for bp in (-100, -50, 50, 100):
    rr = C.R_ANCHOR + (dep + bp / 1e4 - C.DEP_ANCHOR)
    x = sum(r['w'] * val(r['read'], MID[r['mid']], r['L'], r['path'], rr) for r in rows) * f
    dsens[f'{bp:+d}'] = dict(r=rr, V=x, pct=x / out['post']['mean'] - 1)
out['dep_sens_post'] = dsens; CEN['r'] = R
out['nq15_proceeds_bn_vnd'] = NQ15_HA * WOOD_NQ15 / 1e3
P = out['post']
out.update(price=px, price_date=L_['price_date'], center_pre=out['pre']['mean'], center_post=P['mean'], pct_weight_below_price=P['below'],
           px_vs_center_post=px / P['mean'] - 1, px_vs_p10_post=px / P['p10'] - 1, px_vs_p90_post=px / P['p90'] - 1,
           label=C.label(px, P['p10'], P['p90']), rule4_px_below_center_15pct=bool(px <= 0.85 * P['mean']))
out['files_read'] = sorted(set(SEEN))
json.dump(out, open(os.path.join(HERE, 'dri_redo_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
with open(os.path.join(HERE, 'grid_dri_redo_r2.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader()
    for r in rows: wr.writerow({**r, 'w': f"{r['w']:.12g}", 'V': f"{r['V']:.4f}"})


def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} | duoi gia {s.get('below', float('nan')):.1%} (n {s['n']})"


print(f"DRI r2 | r {R:.2%} | mid {MID['P25']:.3f}/{MID['TB']:.3f}/{MID['P75']:.3f} | doi chung r1 keep {out['control']['keep_r1']:,.0f} forced {out['control']['forced_r1']:,.0f}")
print(f"  wood NQ15 {WOOD_NQ15:.2f} tr/ha (cu {ORIG['wood_ha']:.2f}) | tien dau gia 1.975 ha ~{out['nq15_proceeds_bn_vnd']:.1f} ty VND")
for k, x in br.items(): print(f"   cau noi diem TB L27: {k:55s} {x:8,.0f}")
print('  TRUOC CK ' + fm(out['pre'])); print('  SAU CK   ' + fm(P))
for b, s in out['branch_post'].items(): print(f'   nhanh {b:10s} ' + fm(s))
print('   [song song: ban cu giu L27 + bi buoc engine, base da sua] ' + fm(out['parallel_keepL27']))
print('   [chi NQ15-NPV0] ' + fm(out['parallel_NQ15_npv0_only']))
for k, s in out['sens_w_econ'].items(): print(f'   w nhanh KINH TE {k}: ' + fm(s))
for k, s in out['sens_wp'].items(): print(f'   wp PEAK {k}: ' + fm(s))
for k, x in sens.items(): print(f'   {k:50s} tam sau CK {x:8,.0f} ({x-P["mean"]:+,.0f})')
for k, s in dsens.items(): print(f"   dep {k}bp: r {s['r']:.2%} -> {s['V']:,.0f} ({s['pct']:+.1%})")
print(f"  CK 5 ty {d_ref:.2%} (ADV250 {L_['adv_med']/1e9:.2f} ty, Q/ADV {out['ck_ref']['q_over_adv250']:.2f}x) | ADV60 {L_['adv_60']/1e9:.2f} ty -> {L_['d_ref_adv60']:.2%} | sleeve {json.dumps(out['ck_real_sleeve'])}")
print(f"  gia {px:,.0f} ({L_['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | luat4 {out['rule4_px_below_center_15pct']}")
print('  files doc: ' + ' '.join(os.path.relpath(p, HERE) for p in out['files_read']))
