"""DD REDO VONG 3 MBB (job Taylor_20261108_164331) — ap dinh chinh fundamental-skeptic 08/11 (TOP5C_CORRECTIONS_20261108.md muc MBB).
Mo hinh RI = MBB/calc/mbb_r2.py (dau vao BCTC HN-Q3 + kich ban 31/10 chep nguyen van, dong 14-57), THEM cong tac:
  GPOL : g cua RI terminal ('r2' = g_T neu ROE_T>=Ke; 'npv0' = 0 moi nhanh: von moi sau 2029 sinh loi = Ke, moat NARROW khong ben).   D1
  W    : trong so kich ban ('r2' 0,35/0,45/0,20; 'sym' 0,275/0,45/0,275).                                                         D2
  MBV  : truc MBV ('r2' -3.500/0/+3.500/+15.688 @0,15/0,50/0,25/0,10; 'sym' -3.500/0/+3.500 @0,25/0,50/0,25).                     D3
  PT   : truc phai thu ban no MBV 11.248 (31/12/25, BCTN25) — SONG SONG (khong vao headline, xem axes_excluded).                     D4
Gia 06/11 = BQ tav2_bq.ticker (px_mbb_r3.sql -> px_mbb_r3_20261106.csv). r = 13,5% + 1,0 x (dep_12T(06/11) - 7,40%).
Chay: python3 -I mbb_r3.py  (2 lan, so md5 output)."""
import os, sys, json, csv, math, hashlib, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '_common_014125')); sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import numpy as np
import r2common as R2C                      # outcomes / stats / fmt / liq2 (wpct mid-block)
from deposit_rate_vn import effective_deposit_rate

TK = 'MBB'; ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
# ---- BCTC goc [HN-Q3] (ty dong) — chep nguyen van mbb_r2.py ----
BV = 164141.608 - 7124.845      # VCSH hop nhat - loi ich CDKKS 30/09/2026 [HN-Q3 p3-4]
SH = 10068.749885               # trieu CP = VDL 100.687,5 ty / 10.000 [HN-Q3 tr.36]
NI9 = 23784.072                 # LNST thuoc CD NH me 9T26 [HN-Q3 p6]
NI_Q4_25 = 8762.570             # LNST NH me Q4/25 [HN-Q4/25]
LT9 = 30518.358                 # LNTT 9T26 [HN-Q3 p6]
SC = {  # w_r2, PPOP Q4, DP Q4, g_loan27, NIM27, cc27, nonII/TA, CIR27, ROE path 27-29, ROE_T, g_T  (uoc luong, ban 31/10)
 'XAU':   (0.35, 16000, 7500, 0.12, 0.036, 0.022, 0.0065, 0.28, [0.13, 0.14, 0.15], 0.14, 0.06),
 'CO_SO': (0.45, 17500, 5500, 0.18, 0.039, 0.017, 0.0070, 0.27, [0.185, 0.18, 0.17], 0.16, 0.07),
 'TOT':   (0.20, 18700, 4200, 0.24, 0.041, 0.013, 0.0075, 0.26, [0.22, 0.21, 0.20], 0.18, 0.08),
}
TAX, NCI, PAYOUT = 0.20, 0.025, 0.30
W = {'r2': {n: SC[n][0] for n in SC}, 'sym': {'XAU': 0.275, 'CO_SO': 0.45, 'TOT': 0.275}}
MBV = {'r2': ((-3500, 0.15), (0, 0.50), (3500, 0.25), (15688, 0.10)), 'sym': ((-3500, 0.25), (0, 0.50), (3500, 0.25))}
PT_AX = ((0, 0.80), (11248 * 0.30, 0.20))    # [UL] song song: mat 30% phai thu 11.248 xac suat 0,20 (muc 'mat 30%' cua do nhay r1)
DROE = (-0.03, -0.015, 0.0, 0.015, 0.03); DG = (-0.01, 0.0, 0.01)

d0 = effective_deposit_rate(ANCHOR_DATE); d1 = effective_deposit_rate(ASOF)
R = R_ANCHOR + 1.0 * (d1['rate'] - d0['rate'])

base = {}
for n, (w, pp4, dp4, g, nim, cc, nonii, cir, path, roeT, gT) in SC.items():
    lt26 = LT9 + pp4 - dp4; ni26 = lt26 * (1 - TAX) * (1 - NCI)
    base[n] = dict(lt26=lt26, bv26=BV + (ni26 - NI9), path=path, roeT=roeT, gT=gT)


def ri_ps(path, roeT, gT, ke, bv0, days, gpol):
    bv = bv0; pv = 0.0
    for i, r in enumerate(path, 1):
        pv += (r - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - PAYOUT)
    g_ri = 0.0 if (gpol == 'npv0' or roeT < ke) else gT
    tv = (roeT - ke) * bv / (ke - g_ri) / (1 + ke) ** len(path)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (days / 365)


def days_of(pxd): return int((np.datetime64('2026-12-31') - np.datetime64(pxd)).astype(int))


def make_fn(days, gpol, droeT=0.0):
    def fn(r, scen, droe, mbv, dg=0.0, pt=0.0):
        b = base[scen]
        return ri_ps([x + droe for x in b['path']], b['roeT'] + droe + droeT, b['gT'] + dg, r, b['bv26'] - mbv - pt, days, gpol)
    return fn


def axes(wk, mk, dg=True, pt=False):
    ax = [('scen', [(n, W[wk][n]) for n in SC]), ('droe', [(x, 1 / 5) for x in DROE])]
    if dg: ax.append(('dg', [(x, 1 / 3) for x in DG]))
    ax.append(('mbv', list(MBV[mk])))
    if pt: ax.append(('pt', list(PT_AX)))
    return ax


def liq(path, pxdate):
    rows = sorted((r for r in csv.DictReader(open(path)) if r['ticker'] == TK and r['time'] <= pxdate), key=lambda r: r['time'])
    out = {}
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'adv{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig,
                              disc={f'{q:.0f}': sig * math.sqrt(q / adv) for q in (5e9, 10e6, 40e6)}, part={f'{q:.0f}': q / adv for q in (5e9, 10e6, 40e6)})
    out['d_ref'] = out['adv250']['disc']['5000000000']; out['d_ref_adv60'] = out['adv60']['disc']['5000000000']
    out['px'] = float(rows[-1]['Price']); out['pxd'] = rows[-1]['time']
    return out


def run(fn, ax, px, d, r=R):
    return R2C.stats(R2C.outcomes(ax, lambda **kw: fn(r, **kw)), px, d)


# ---- CONTROL: tai lap r2 (gia/thanh khoan 04/11, csv r2, liq2 cua r2) ----
L2 = R2C.liq2(TK)
ctrl = run(make_fn(days_of('2026-11-04'), 'r2'), axes('r2', 'r2'), 19250.0, L2['d_ref'])
L = liq(os.path.join(HERE, 'px_mbb_r3_20261106.csv'), ASOF); PX, PXD, D = L['px'], L['pxd'], L['d_ref']; DAYS = days_of(PXD)
print(f"== MBB VONG 3 | gia {PX:,.0f} ({PXD}, BQ) | r {R:.2%} (dep 12T {d1['rate']:.2%} {d1['rate_source']}; neo {d0['rate']:.2%} {d0['rate_source']})")
print(f"CK 5 ty: r2 {L2['d_ref']:.4%} | r3 {D:.4%} (ADV250 {L['adv250']['adv_med']/1e9:,.1f} ty, ADV60 {L['adv60']['adv_med']/1e9:,.1f} ty, CK ADV60 {L['d_ref_adv60']:.4%})")
print("CONTROL r2 tai lap (04/11):", R2C.fmt(ctrl))

# ---- BRIDGE r2 -> r3 (tung buoc, cong don) ----
steps = [('0 r2 (gia 04/11)', None),
         ('1 gia+thanh khoan 06/11, chiet khau tu 06/11', dict(gpol='r2', w='r2', m='r2', dg=True)),
         ('2 D1 g_RI terminal = 0 moi nhanh (bo thuong moat ngam)', dict(gpol='npv0', w='r2', m='r2', dg=True)),
         ('3 D2 trong so kich ban doi xung 0,275/0,45/0,275', dict(gpol='npv0', w='sym', m='r2', dg=True)),
         ('4 D3 truc MBV doi xung +-3.500 (diem 15.688 -> co HARD ABANDON)', dict(gpol='npv0', w='sym', m='sym', dg=True)),
         ('5 bo truc dg (vo tac dung sau D1; chi doi n)', dict(gpol='npv0', w='sym', m='sym', dg=False))]
bridge = []; prev = ctrl['center']
for nm, cfg in steps:
    s = ctrl if cfg is None else run(make_fn(DAYS, cfg['gpol']), axes(cfg['w'], cfg['m'], cfg['dg']), PX, D)
    bridge.append(dict(step=nm, center=round(s['center']), delta=round(s['center'] - prev), p10=round(s['p10']), p90=round(s['p90']),
                       pct_below_px=round(s['pct_below_px'], 4), n=s['n'])); prev = s['center']
    print(f"BRIDGE {nm}: tam {s['center']:,.0f} (buoc {bridge[-1]['delta']:+,}) P10 {s['p10']:,.0f} P90 {s['p90']:,.0f} %duoi {s['pct_below_px']:.1%} n={s['n']}")

FH = make_fn(DAYS, 'npv0'); AXH = axes('sym', 'sym', dg=False)
res = R2C.outcomes(AXH, lambda **kw: FH(R, **kw)); R2C.write_grid(os.path.join(HERE, 'grid_mbb_r3.csv'), res)
main = R2C.stats(res, PX, D); pre = R2C.stats(res, PX, 0.0)
central = FH(R, scen='CO_SO', droe=0.0, dg=0.0, mbv=0) * (1 - D)
print("HEADLINE r3 (sau CK 5 ty):", R2C.fmt(main)); print("Truoc CK:", R2C.fmt(pre))
print(f"Gia tri tai tham so trung tam (CO_SO, droe 0, MBV 0) sau CK: {central:,.0f}")
for sc in SC:
    print(f"  {sc}: r3 {FH(R, scen=sc, droe=0, dg=0, mbv=0):,.0f} | r2-style {make_fn(DAYS, 'r2')(R, scen=sc, droe=0, dg=0, mbv=0):,.0f} (truoc CK)")
v = np.array([x[1] for x in res]) * (1 - D); w = np.array([x[2] for x in res])
def near(q):
    m = np.abs(v - q) <= 0.05 * abs(q); tw = w[m].sum(); out = {}
    for (kw, _, ww), mm in zip(res, m):
        if mm: out[kw['scen']] = out.get(kw['scen'], 0) + ww / tw
    return {k: round(float(x), 3) for k, x in sorted(out.items())}
drivers = dict(p10_scen_mix_pm5pct=near(main['p10']), p90_scen_mix_pm5pct=near(main['p90']))
print("Nhom kich ban quanh P10/P90:", drivers)

# ---- BIEN THE SONG SONG ----
alts = {
 'A_RONIC_gt_Ke_(g_RI_r2)_trong_so+MBV_doi_xung': (make_fn(DAYS, 'r2'), axes('sym', 'sym')),
 'B_chi_D1_(trong_so_r2,MBV_r2)': (make_fn(DAYS, 'npv0'), axes('r2', 'r2', dg=False)),
 'C_D1+D2_MBV_r2_(giu_diem_15.688)': (make_fn(DAYS, 'npv0'), axes('sym', 'r2', dg=False)),
 'D_D1+D3_trong_so_r2': (make_fn(DAYS, 'npv0'), axes('r2', 'sym', dg=False)),
 'E_co_truc_phai_thu_MBV_(mat_30%_p=0,20)': (make_fn(DAYS, 'npv0'), axes('sym', 'sym', dg=False, pt=True)),
 'F_ROE_T_-2pp': (make_fn(DAYS, 'npv0', -0.02), AXH),
 'G_ROE_T_+2pp': (make_fn(DAYS, 'npv0', +0.02), AXH),
 'H_khong_truc_MBV_(NPV0)': (make_fn(DAYS, 'npv0'), [a if a[0] != 'mbv' else ('mbv', [(0, 1.0)]) for a in AXH]),
}
alt_out = {}
for k, (f, ax) in alts.items():
    s = run(f, ax, PX, D); alt_out[k] = s
    print(f"SONG SONG {k}:", R2C.fmt(s))
rax = [(R - 0.01, 0.25), (R, 0.50), (R + 0.01, 0.25)]
s_r = R2C.stats(R2C.outcomes(AXH + [('r', rax)], lambda r, **kw: FH(r, **kw)), PX, D); alt_out['co_truc_r_pm1pp'] = s_r
print("SONG SONG co_truc_r_pm1pp:", R2C.fmt(s_r))
sens_r = {f'{dr*1e4:+.0f}bp': round(run(FH, AXH, PX, D, r=R + dr)['center']) for dr in (-0.01, -0.005, 0.005, 0.01)}
print("Do nhay r (tam):", sens_r)
hard = FH(R, scen='CO_SO', droe=0, dg=0, mbv=15688) * (1 - D)
print(f"Co HARD ABANDON: CO_SO + bu lo luy ke MBV 15.688 sau CK = {hard:,.0f}")


# ---- GIA NGU Y ----
def solve(f, lo, hi):
    up = f(hi) > f(lo)
    for _ in range(60):
        m = (lo + hi) / 2
        if (f(m) > PX) != up: lo = m
        else: hi = m
    return m
r_imp = solve(lambda rr: run(FH, AXH, PX, D, r=rr)['center'], 0.10, 0.25)
droeT_imp = solve(lambda x: run(make_fn(DAYS, 'npv0', x), AXH, PX, D)['center'], -0.08, 0.04)
droe_all_imp = solve(lambda x: R2C.stats(R2C.outcomes([a if a[0] != 'droe' else ('droe', [(x, 1.0)]) for a in AXH], lambda **kw: FH(R, **kw)), PX, D)['center'], -0.10, 0.05)
print(f"GIA NGU Y: Ke {r_imp:.2%} | ROE_T dich {droeT_imp*100:+.2f}pp (CO_SO ROE_T {0.16+droeT_imp:.2%}) | dich ca duong ROE 27-29+T {droe_all_imp*100:+.2f}pp (CO_SO ROE_T {0.16+droe_all_imp:.2%})")

ttm = NI9 + NI_Q4_25; bvps = BV / SH * 1e3
gord = {f'{lab}_g{g}': bvps * (roe - g) / (R - g) for lab, roe in (('ROE_TTM', ttm / BV), ('ROE_T_coso', 0.16)) for g in (0.06, 0.07)}
gord_npv0 = {f'{lab}_g0': bvps * roe / R for lab, roe in (('ROE_TTM', ttm / BV), ('ROE_T_coso', 0.16))}
print("Gordon P/B (BVPS 30/09): " + ' | '.join(f"{k} {x:,.0f}" for k, x in {**gord, **gord_npv0}.items()) + f" | ROE TTM {ttm/BV:.1%}")
q4 = {n: SC[n][1] - SC[n][2] for n in SC}
print("LNTT Q4/26 ngu y (PPOP-DP): " + ', '.join(f"{n} {x:,.0f}" for n, x in q4.items()) + " | Q4/25 that 11.129 (mbb_calc.py:106)")

WC = '/home/trido/thanhdt/WorkingClaude'
LOCK_FILES = [os.path.abspath(__file__), os.path.join(HERE, 'px_mbb_r3.sql'), os.path.join(HERE, 'px_mbb_r3_20261106.csv'),
              os.path.join(ROOT, '_common_014125', 'r2common.py'), os.path.join(ROOT, '_common_014125', 'bq_px_liq_20261104.csv'),
              os.path.join(ROOT, '_shared', 'wpct.py'), os.path.join(ROOT, 'MBB', 'calc', 'mbb_r2.py'), os.path.join(ROOT, 'MBB', 'calc', 'mbb_redo.py'),
              os.path.join(WC, 'mike/agents/Taylor/research/dd_MBB_20261031/calc/mbb_calc.py'),
              os.path.join(WC, 'deposit_rate_vn.py'), os.path.join(WC, 'cctg_rate_vn.py'),
              os.path.join(WC, 'data/deposit_rate_vn_events.csv'), os.path.join(WC, 'data/cctg_rate_vn_events.csv'),
              os.path.join(HERE, 'summary_r3_extra.json'), os.path.join(ROOT, 'TOP5C_CORRECTIONS_20261108.md'), os.path.join(ROOT, 'STANDARD_r2.md'),
              os.path.join(WC, 'mike/kb/data_registry/market-state/sector_read_ngan_hang_20261031.md')]
LOCK = {os.path.relpath(p, ROOT): hashlib.md5(open(p, 'rb').read()).hexdigest() for p in LOCK_FILES}
for k, x in LOCK.items(): print(f"LOCK {x} {k}")


def r1(x): return int(round(x))
def sm(s): return {k: (r1(x) if k not in ('pct_below_px', 'n') else x) for k, x in s.items()}
def labf(x): return 'DƯỚI vùng' if PX < x['p10'] else ('TRÊN vùng' if PX > x['p90'] else 'TRONG vùng')


SUMP = os.path.join(ROOT, 'MBB', 'SUMMARY.json'); BK = os.path.join(ROOT, 'MBB', 'SUMMARY_r2.json')
if not os.path.exists(BK): shutil.copyfile(SUMP, BK)
old = json.load(open(BK)); S = dict(old)
lab = labf(main)
S.update(round='r3', job='Taylor_20261108_164331', asof_price_date=PXD, price=PX, price_date=PXD, price_source='BQ tav2_bq.ticker Price (px_mbb_r3_20261106.csv)', r=R,
         r_anchor=dict(r=R_ANCHOR, rate=d0['rate'], source=d0['rate_source'], date=ANCHOR_DATE, dep_asof=d1['rate'], dep_asof_source=d1['rate_source'], rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
         center_post_liq=r1(main['center']), center_pre_liq=r1(pre['center']), p10_post=r1(main['p10']), p25_post=r1(main['p25']), p50_post=r1(main['p50']),
         p75_post=r1(main['p75']), p90_post=r1(main['p90']), p10_pre=r1(pre['p10']), p50_pre=r1(pre['p50']), p90_pre=r1(pre['p90']),
         p10_out=r1(main['p10']), p50_out=r1(main['p50']), p90_out=r1(main['p90']), pct_weight_below_price=main['pct_below_px'], n_outcomes=main['n'],
         min_outcome=r1(main['min']), central_param_value_post=r1(central), liq_disc_5ty=D, label=lab, drivers=drivers,
         px_vs_center_post=PX / main['center'] - 1, px_vs_p10_post=PX / main['p10'] - 1, px_vs_p90_post=PX / main['p90'] - 1,
         ck_ref_size=dict(size_vnd=5e9, disc_adv250=D, disc_adv60=L['d_ref_adv60'], adv250=L['adv250']['adv_med'], adv60=L['adv60']['adv_med'], part_adv250=L['adv250']['part']['5000000000']),
         ck_real_sleeve=dict(sizes_vnd=[10e6, 40e6], disc_adv250={'10tr': L['adv250']['disc']['10000000'], '40tr': L['adv250']['disc']['40000000']},
                             note='sleeve 10-40tr << 0,1% ADV250, DUOI vung hieu chinh luat can bac hai (CK that ~ nua spread, chua do)'),
         grid_desc=('Luoi n=60: kich ban XAU/CO_SO/TOT (0,275/0,45/0,275 [UL], doi xung) x dich ROE 2027-29+T -3..+3pp (5 diem deu) x MBV -3.500/0/+3.500 (0,25/0,50/0,25 [UL]). '
                    'RI, BV0 = VCSH me 30/09 + LN Q4/26 kich ban; g_RI terminal = 0 moi nhanh (von moi sau 2029 sinh loi = Ke, moat NARROW khong ben); truc g_T bo vi vo tac dung. Sau CK 5 ty Y=1.'),
         grid_n=main['n'], sens_r=sens_r, r_implied_center_eq_px=r_imp, center_change_vs_old=r1(main['center']) - old['center_post_liq'],
         parallel_versions={k: sm(x) for k, x in alt_out.items()}, bridge_r2_to_r3=bridge, control_r2_reproduced=sm(ctrl),
         implied_by_price=dict(ke=r_imp, roeT_shift_pp=droeT_imp * 100, roeT_co_so=0.16 + droeT_imp, roe_path_and_T_shift_pp=droe_all_imp * 100, roeT_co_so_all=0.16 + droe_all_imp),
         hard_abandon_flag_value=r1(hard), gordon_crosscheck={k: r1(x) for k, x in {**gord, **gord_npv0}.items()}, q4_pbt_implied=q4,
         lock_md5=LOCK, zone_r2=dict(center=old['center_post_liq'], p10=old['p10_post'], p90=old['p90_post'], label=old['label'], price=old['price'], date=old['asof_price_date'],
                                    pct_below=old['pct_weight_below_price']))
S['headline_vs_alternatives'] = [dict(name='HEADLINE r3', center=r1(main['center']), p10=r1(main['p10']), p50=r1(main['p50']), p90=r1(main['p90']), pct_below_px=main['pct_below_px'], label=lab)] + \
    [dict(name=k, center=r1(x['center']), p10=r1(x['p10']), p50=r1(x['p50']), p90=r1(x['p90']), pct_below_px=x['pct_below_px'], label=labf(x)) for k, x in alt_out.items()]
EXTRA = os.path.join(HERE, 'summary_r3_extra.json')
if os.path.exists(EXTRA): S.update(json.load(open(EXTRA)))
json.dump(S, open(SUMP, 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=main, pre=pre, central=central, ctrl=ctrl, bridge=bridge, alts=alt_out, sens_r=sens_r, liq=L, lock=LOCK, drivers=drivers,
               implied=dict(ke=r_imp, droeT=droeT_imp, droe_all=droe_all_imp), hard=hard, gordon=gord, gordon_npv0=gord_npv0),
          open(os.path.join(HERE, 'mbb_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(f"NHAN: {lab} | gia {PX:,.0f} vs tam {main['center']:,.0f} ({PX/main['center']-1:+.1%}) | SUMMARY.json (r3) written")
