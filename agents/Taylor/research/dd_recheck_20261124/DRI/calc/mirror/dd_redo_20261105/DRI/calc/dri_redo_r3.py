"""DD redo DRI VONG 3 (08/11/2026, job Taylor_20261108_153743). Chay: $DNA_PYEXE -B dri_redo_r3.py (tu thu muc calc nay).
Engine = dri_val_supply_adj_r4_20261027/model.py exec NGUYEN VAN (nhu r2; KHONG sua). Gia dinh khoa: assumptions_r3.json.
Vong 3 = r2 + dinh chinh fundamental-skeptic 08/11 (TOP5B_CORRECTIONS_20261108.md muc DRI), tung diem kiem bang calc:
 (1) bo nhanh NQ15-KINH TE 0,20 khoi base (sang do nhay); (2) truc mat do q KHOI thanh ly {0,7/0,85/1} (.25/.5/.25),
 mo hinh q CHI cho khoi, tong dien tich giu A0 (khac skeptic - xem assumptions); (3) wht = 10% x (1-KTPL-TAU);
 (4) wp PEAK 0,5; (5) gia + thanh khoan 06/11 tu BQ (r3data/px_dri_20261106.csv).
"""
import os, sys, io, csv, json, math, builtins, contextlib, itertools, statistics as st
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, RED); sys.path.insert(0, os.path.join(RED, '_shared'))
import common as C  # noqa: E402
from wpct import wpct, weight_below  # noqa: E402
import numpy as np  # noqa: E402
A = json.load(builtins.open(os.path.join(HERE, 'assumptions_r3.json'), encoding='utf-8'))
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
fvph, fv4, CEN, SH = ns['fvph'], ns['fv4'], ns['CEN'], ns['SH']
CIP = 72.712702447; CIPPS = CIP * 1e9 / SH
ASOF = A['asof_price']
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import deposit_rate_vn as DEP  # noqa: E402
_d = DEP.effective_deposit_rate(ASOF); dep, dep_src = float(_d['rate']), _d['rate_source']; R = C.r_of(dep)

ORIG = dict(DKR=ns['DKR'], h=CEN['h'], wood_ha=ns['wood_ha'], R_LEFT=ns['R_LEFT'], WIN=ns['WIN'], wht=CEN['wht'])
KTPL, TAU = ns['KTPL'], ns['TAU']
WHT3 = 0.10 * (1 - KTPL - TAU); WHT_OBS = ns['WHT_OBS']
LAK = 1 / 0.8769; WOOD_NQ15 = A['wood_lak_per_ha_mn'] * LAK
NQ15_HA, NQ15_S, NQ15_WIN = A['nq15_ha'], A['nq15_start'], A['nq15_window_years']
assert round(LAK, 4) == 1.1404


def setcfg(dkr=40.0, h=0.0, wood=WOOD_NQ15, wht=WHT3):
    ns['DKR'] = dkr; CEN['h'] = h; ns['wood_ha'] = wood; CEN['wht'] = wht


def build_blk(s, L, qb):
    """q CHI cho khoi thanh ly R (= NQ15_HA, da set vao ns['R_LEFT']); tong dien tich cao 2026 = A0 (BCTN25 tr.46);
    phan con lai nang suat bu yr de 2026 = KH26_V. Khong trong moi (NPV0). qb=1 => trung build3(q=1, new_on=False)."""
    A0, Rl, W, yold, alive = ns['A0'], ns['R_LEFT'], ns['WIN'], ns['yold'], ns['alive']
    yr = (A0 - qb * Rl) / (A0 - Rl); out, real = {}, {}
    for y in range(2026, ns['END'] + 1):
        oldR = Rl - sum(Rl / W for Lx in range(s, s + W) if Lx <= y)
        al = alive(y, L) if y > 2026 else 1.0
        a_old = (oldR + A0 - Rl) * al
        out[y] = ((oldR * qb + (A0 - Rl) * yr) * al * yold(y), a_old); real[y] = a_old
    return out, real


def val(read, mid, L, scn, r=R, q=1.0, qmode='blk'):
    """read: NQ15_NPV0 | NQ15_ECON | KEEP_L27 (ban cu) | ENG_FORCED. scn: PEAK|MID. qmode: blk (khoi) | eng (toan vuon, ban skeptic)."""
    CEN['r'] = r
    if read in ('NQ15_NPV0', 'NQ15_ECON'):
        ns['R_LEFT'], ns['WIN'] = NQ15_HA, NQ15_WIN
        try:
            if read == 'NQ15_NPV0' and qmode == 'blk':
                V, real = build_blk(NQ15_S, L, q)
                return fv4(scn, mid, CEN, V=V, cx=None, farea=True, addD=ns['D_V'], wood=ns['wood3'](real)) + CIPPS
            return fvph(mid, NQ15_S, L, q=q, new_on=(read == 'NQ15_ECON'), scn=scn) + CIPPS
        finally:
            ns['R_LEFT'], ns['WIN'] = ORIG['R_LEFT'], ORIG['WIN']
    if read == 'KEEP_L27':
        return fvph(mid, 2029, L, R_on=False, new_on=False, scn=scn) + CIPPS
    return fvph(mid, 2029, L, scn=scn) + CIPPS


# ---- mid RSS3 thuc (y het vong 1-2) ----
cpi = {r['observation_date'][:7]: float(r['CPIAUCSL']) for r in csv.DictReader(builtins.open(os.path.join(R5, 'data/fred_cpiaucsl_20261103.csv'))) if r['CPIAUCSL']}
cpi['2025-10'] = (cpi['2025-09'] + cpi['2025-11']) / 2
rss = [(m, float(p)) for m, p in csv.reader(builtins.open(os.path.join(R5, 'data/rubber_monthly_snapshot_20261103.csv'))) if m != 'month']
c25 = st.mean([cpi[f'2025-{i:02d}'] for i in range(1, 13)])
real_ = {m: p * c25 / cpi[m] for m, p in rss if m in cpi}
wv = sorted(v for m, v in real_.items() if '2014-01' <= m <= '2026-09')
def pq(xs, q): i = q * (len(xs) - 1); lo = int(i); return xs[lo] + (xs[min(lo + 1, len(xs) - 1)] - xs[lo]) * (i - lo)
MID = {'P25': pq(wv, .25), 'TB': st.mean(wv), 'P75': pq(wv, .75)}

WM = A['mid_weights']; WL = {int(k): v for k, v in A['L_weights'].items()}
QB = dict(zip(A['q_block']['values'], A['q_block']['weights'])); WB = A['branch_weights']; WP3 = A['wp_peak']


def grid(wb=WB, wq=QB, wp=WP3, qmode='blk', r=R):
    rows = []
    for (b, w1), (mk, w2), (L, w3), (q, w5) in itertools.product(wb.items(), WM.items(), WL.items(), wq.items()):
        if b != 'NQ15_NPV0' and qmode == 'blk' and q != 1.0:
            continue                                   # nhanh khac: q chi dinh nghia cho NPV0 (khoi); dung q=1 voi tron trong so
        wq_eff = w5 if (b == 'NQ15_NPV0' or qmode == 'eng') else 1.0
        for p, w4 in (('PEAK', wp), ('MID', 1 - wp)):
            if w1 * w4 * wq_eff == 0: continue
            rows.append(dict(read=b, mid=mk, L=L, q=q, path=p, w=w1 * w2 * w3 * wq_eff * w4, V=val(b, MID[mk], L, p, r, q, qmode)))
    return rows


def st_(rows, f=1.0, px=None):
    v = np.array([r['V'] for r in rows]) * f; w = np.array([r['w'] for r in rows]); p = wpct(v, w)
    o = dict(n=len(rows), mean=float((v * w).sum() / w.sum()), p10=p[0.1], p50=p[0.5], p90=p[0.9], min=float(v.min()), max=float(v.max()))
    if px: o['below'] = weight_below(v, w, px)
    return o


out = dict(ticker='DRI', round=3, dep=dep, dep_src=dep_src, r=R, mids=MID, wood_nq15_tr_per_ha=WOOD_NQ15, lak_vnd=LAK,
           wht=dict(base=WHT3, r2=ORIG['wht'], obs=list(WHT_OBS), ktpl=KTPL, tau=TAU))

# ---- 0. SELFCHECK ----
# (a) build_blk(q=1) == fvph(q=1, new_on=False)
setcfg()
for mk in MID:
    for L in WL:
        for p in ('PEAK', 'MID'):
            assert abs(val('NQ15_NPV0', MID[mk], L, p, q=1.0) - val('NQ15_NPV0', MID[mk], L, p, q=1.0, qmode='eng')) < 1e-6
# (b) doi chung r2: cau hinh r2 (wht 10%, wp 0,6, NPV0 0,8/ECON 0,2, q=1, thanh khoan 04/11) tai lap tam sau CK 14.092
L04 = C.liquidity('DRI', ff=A['free_float'], qs=(0.01e9, 0.04e9, 1e9, 5e9))
f04 = 1 - L04['pos']['5']['disc']['Y1.0']
setcfg(wht=ORIG['wht'])
r2rows = grid({'NQ15_NPV0': 0.8, 'NQ15_ECON': 0.2}, {1.0: 1.0}, 0.6)
ctrl_r2 = st_(r2rows, f04, L04['price'])
assert round(ctrl_r2['mean']) == 14092 and round(ctrl_r2['p10']) == 12006 and round(ctrl_r2['p90']) == 16146, ctrl_r2
out['control_r2'] = ctrl_r2
# (c) tai lap so skeptic (q toan vuon, NPV0 only, wht 10%, wp 0,6, CK 04/11): q 0,85 -> 14.902
sk = {q: st_(grid({'NQ15_NPV0': 1.0}, {q: 1.0}, 0.6, qmode='eng'), f04)['mean'] for q in (0.85, 0.7, 0.5)}
out['skeptic_repro_eng_q'] = sk
setcfg()

# ---- 1. thanh khoan 06/11 ----
C.LIQ_CSV = os.path.join(HERE, 'r3data/px_dri_20261106.csv')
L_ = C.liquidity('DRI', ff=A['free_float'], asof=ASOF, qs=(0.01e9, 0.04e9, 1e9, 5e9)); out['liq'] = L_
assert L_['price_date'] == ASOF, L_['price_date']
d_ref = L_['pos']['5']['disc']['Y1.0']; f = 1 - d_ref; px = L_['price']
out['ck_ref'] = dict(size_bn=5, Y=1.0, adv250=d_ref, adv60=L_['d_ref_adv60'], q_over_adv250=5e9 / L_['adv_med'], q_over_adv60=5e9 / L_['adv_60'])
out['ck_real_sleeve'] = {f'{q/1e6:.0f}tr': dict(adv250=L_['sigma_d'] * math.sqrt(q / L_['adv_med']), adv60=L_['sigma_d'] * math.sqrt(q / L_['adv_60'])) for q in (0.01e9, 0.04e9)}

# ---- 2. HEADLINE ----
rows = grid(); assert abs(sum(r['w'] for r in rows) - 1) < 1e-9
out['pre'] = st_(rows, 1.0, px); out['post'] = st_(rows, f, px)
fs = {k: 1 - L_['sigma_d'] * math.sqrt(q / L_['adv_med']) for k, q in (('10tr', 0.01e9), ('40tr', 0.04e9))}
out['post_real_sleeve'] = {k: st_(rows, v, px) for k, v in fs.items()}
out['n_outcomes'] = len(rows); out['n_cells'] = len(rows) // 2
out['center_param_pre'] = WP3 * val('NQ15_NPV0', MID['TB'], 27, 'PEAK', q=0.85) + (1 - WP3) * val('NQ15_NPV0', MID['TB'], 27, 'MID', q=0.85)
out['by_q_post'] = {f'{q:.2f}': st_([r for r in rows if r['q'] == q], f, px) for q in QB}

# ---- 3. CAU NOI r2 -> r3 (tam sau CK, tuan tu) ----
br = [('r2 cong bo (CK 04/11)', ctrl_r2['mean'])]
setcfg(wht=ORIG['wht'])
br.append(('CK cap nhat du lieu 06/11', st_(r2rows, f)['mean']))
br.append(('(1) bo nhanh KINH TE 0,20 -> NPV0 1,0', st_(grid({'NQ15_NPV0': 1.0}, {1.0: 1.0}, 0.6), f)['mean']))
br.append(('(2) truc q khoi {0,7/0,85/1}', st_(grid({'NQ15_NPV0': 1.0}, QB, 0.6), f)['mean']))
setcfg()
br.append(('(3) wht 10% -> 10%x(1-KTPL-TAU)', st_(grid({'NQ15_NPV0': 1.0}, QB, 0.6), f)['mean']))
br.append(('(4) wp PEAK 0,6 -> 0,5 = r3', out['post']['mean']))
assert abs(br[-1][1] - st_(grid(), f)['mean']) < 1e-6
out['bridge_r2_to_r3'] = [dict(step=k, center_post=v, delta=(v - br[i - 1][1]) if i else 0.0) for i, (k, v) in enumerate(br)]

# ---- 4. BIEN THE SONG SONG / DO NHAY (tam sau CK 5 ty, 06/11) ----
alt = {}
alt['skeptic: q toan vuon cu (dien tich A0/q)'] = st_(grid(qmode='eng'), f, px)
alt['q=1 (khong truc mat do, nhu r2)'] = st_(grid(wq={1.0: 1.0}), f, px)
alt['q khoi 0,5 co dinh'] = st_(grid(wq={0.5: 1.0}), f, px)
for w in (0.1, 0.2, 0.3):
    alt[f'nhanh KINH TE {w:.1f} (q=1 o nhanh KINH TE)'] = st_(grid({'NQ15_NPV0': 1 - w, 'NQ15_ECON': w}), f, px)
alt['chi nhanh KINH TE 1,0 (tai canh pha gia tri 100%)'] = st_(grid({'NQ15_ECON': 1.0}), f, px)
alt['ban cu giu vuon L27 (bo qua NQ15) 0,8 + bi buoc 0,2'] = st_(grid({'KEEP_L27': 0.8, 'ENG_FORCED': 0.2}, {1.0: 1.0}), f, px)
out['alternatives'] = alt
sens = {}
def S(lab, **cfg):
    setcfg(**cfg); sens[lab] = st_(grid(), f)['mean']; setcfg()
S('wht 10% phang (r2)', wht=0.10); S(f'wht {WHT_OBS[0]:.2%} (quan sat 2025)', wht=WHT_OBS[0]); S(f'wht {WHT_OBS[1]:.2%} (quan sat 2024)', wht=WHT_OBS[1])
S('(-) haircut 50% khoan vay Dakruco 40 ty', dkr=20.0); S('(-) khoan vay Dakruco mat trang', dkr=0.0); S('(-) giu 15% tien Lao', h=0.15)
S('gia go LAK -10%', wood=WOOD_NQ15 * 0.9); S('gia go LAK +10%', wood=WOOD_NQ15 * 1.1); S('gia go cu 20,87 tr/ha', wood=ORIG['wood_ha'])
for wp in (0.4, 0.6, 0.0, 1.0):
    sens[f'wp PEAK {wp:.1f}'] = st_(grid(wp=wp), f)['mean']
_fv4 = ns['fv4']
for rv in (0.8, 1.0):
    def fv4r(*a, _f=_fv4, _rv=rv, **k): k['reinv'] = _rv; return _f(*a, **k)
    ns['fv4'] = fv4r; fv4 = fv4r
    try: sens[f'FCF/LN loi {rv:.0%} (base 90% [UL])'] = st_(grid(), f)['mean']
    finally: ns['fv4'] = _fv4; fv4 = _fv4
for bp in (-100, -50, 50, 100):
    rr = C.R_ANCHOR + (dep + bp / 1e4 - C.DEP_ANCHOR)
    sens[f'lai huy dong {bp:+d}bp (r {rr:.2%})'] = st_(grid(r=rr), f)['mean']
CEN['r'] = R
sens['CK Y 0,5'] = out['post']['mean'] / f * (1 - 0.5 * d_ref); sens['CK Y 1,5'] = out['post']['mean'] / f * (1 - 1.5 * d_ref)
out['sens_mean_post'] = sens

# ---- 5. GIA NGU Y (giai 1 tham so, cac truc khac = headline) ----
def solve(fn, lo, hi, it=60):
    flo, fhi = fn(lo) - px, fn(hi) - px
    if flo * fhi > 0: return None
    for _ in range(it):
        m = (lo + hi) / 2; fm_ = fn(m) - px
        if flo * fm_ <= 0: hi = m
        else: lo, flo = m, fm_
    return (lo + hi) / 2
imp = {}
imp['trong so nhanh KINH TE'] = solve(lambda w: st_(grid({'NQ15_NPV0': 1 - w, 'NQ15_ECON': w}) if w < 1 else grid({'NQ15_ECON': 1.0}), f)['mean'], 0.0, 1.0)
imp['q khoi co dinh'] = solve(lambda q: st_(grid(wq={q: 1.0}), f)['mean'], 0.0, 1.0)
imp['wp PEAK'] = solve(lambda w: st_(grid(wp=w), f)['mean'], 0.0, 1.0)
def _rv(rv):
    def g(*a, _f=_fv4, **k): k['reinv'] = rv; return _f(*a, **k)
    global fv4
    ns['fv4'] = g; fv4 = g
    try: return st_(grid(), f)['mean']
    finally: ns['fv4'] = _fv4; fv4 = _fv4
imp['FCF/LN loi'] = solve(_rv, 0.5, 0.9)
imp['lai huy dong 12T'] = solve(lambda d: st_(grid(r=C.R_ANCHOR + d - C.DEP_ANCHOR), f)['mean'], 0.06, 0.30)
CEN['r'] = R
out['implied_by_price'] = imp

P = out['post']
out.update(price=px, price_date=L_['price_date'], center_pre=out['pre']['mean'], center_post=P['mean'], pct_weight_below_price=P['below'],
           px_vs_center_post=px / P['mean'] - 1, px_vs_p10_post=px / P['p10'] - 1, px_vs_p90_post=px / P['p90'] - 1,
           label=C.label(px, P['p10'], P['p90']), rule4_px_below_center_15pct=bool(px <= 0.85 * P['mean']), rule4_threshold=0.85 * P['mean'])
out['files_read'] = sorted(set(SEEN))
json.dump(out, open(os.path.join(HERE, 'dri_redo_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
with open(os.path.join(HERE, 'grid_dri_redo_r3.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader()
    for r in rows: wr.writerow({**r, 'w': f"{r['w']:.12g}", 'V': f"{r['V']:.4f}"})


def fm(s): return f"tam {s['mean']:,.0f} | P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | min {s['min']:,.0f} | duoi gia {s.get('below', float('nan')):.1%} (n {s['n']})"


print(f"DRI r3 | r {R:.2%} (lai 12T {dep:.2%} {dep_src}) | mid {MID['P25']:.3f}/{MID['TB']:.3f}/{MID['P75']:.3f} | wht {WHT3:.4f} | LAK {LAK:.4f} -> go {WOOD_NQ15:.2f} tr/ha")
print(f"  doi chung r2: {fm(ctrl_r2)} | skeptic q toan vuon (CK 04/11): " + ' '.join(f'q{k}:{v:,.0f}' for k, v in sk.items()))
print('  TRUOC CK ' + fm(out['pre'])); print('  SAU CK 5 ty ' + fm(P))
for k, s in out['post_real_sleeve'].items(): print(f'  SAU CK sleeve {k} ' + fm(s))
for k, s in out['by_q_post'].items(): print(f'   q khoi {k}: ' + fm(s))
for b in out['bridge_r2_to_r3']: print(f"   cau noi {b['step']:42s} {b['center_post']:8,.0f} ({b['delta']:+,.0f})")
for k, s in alt.items(): print(f'   [song song] {k:52s} ' + fm(s))
for k, x in sens.items(): print(f'   {k:45s} tam sau CK {x:8,.0f} ({x-P["mean"]:+,.0f})')
for k, x in imp.items(): print(f'   gia ngu y {px:,.0f}: {k} = ' + ('khong dat trong khoang' if x is None else f'{x:.4f}'))
print(f"  CK 5 ty {d_ref:.2%} (ADV250 {L_['adv_med']/1e9:.2f} ty, Q/ADV {out['ck_ref']['q_over_adv250']:.2f}x) | ADV60 {L_['adv_60']/1e9:.2f} ty -> {L_['d_ref_adv60']:.2%} | sleeve {json.dumps(out['ck_real_sleeve'])}")
print(f"  gia {px:,.0f} ({L_['price_date']}): vs tam {out['px_vs_center_post']:+.1%} | vs P10 {out['px_vs_p10_post']:+.1%} | vs P90 {out['px_vs_p90_post']:+.1%} | {out['label']} | luat4 (<= {out['rule4_threshold']:,.0f}) {out['rule4_px_below_center_15pct']}")
print('  files doc: ' + ' '.join(os.path.relpath(p, HERE) for p in out['files_read']))
