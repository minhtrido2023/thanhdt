"""DD REDO VONG 3 HPG (job Taylor_20261108_142020) — ap dinh chinh fundamental-skeptic 08/11 (TOP5_CORRECTIONS_20261108.md muc HPG).
Mo hinh RI = hpg_r2.py (dau vao BCTC HN-Q3 + duong LN v3 31/10 chep nguyen van), THEM 4 cong tac:
  RET  : von giu lai sau 30/09 sinh loi bao nhieu (r2 = 0%).  C1.
  TAXY : nam bat dau thue TNDN 20% day du (r2 = 2030).        C2.
  GPOL : g cua RI terminal ('r2' = g neu ROE_T>=r, 'npv0' = 0 moi nhanh vi moat NARROW khong ben).  C3.
  TLSH : truc ty le mat gia tri khoan TLSH trong base (r2 = truc lech xuong [UL]; r3 = so sach).  C4.
Gia 06/11 = BQ tav2_bq.ticker (px_hpg_r3.sql -> px_hpg_r3_20261106.csv). r = 13,5% + 1,0 x (dep_12T(06/11) - 7,40%).
Chay: python3 -I hpg_r3.py  (2 lan, so md5 output)."""
import os, sys, json, csv, math, hashlib, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '_common_014125')); sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import numpy as np
import r2common as R2C                      # outcomes / stats / fmt (wpct mid-block)
from deposit_rate_vn import effective_deposit_rate

TK = 'HPG'; ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
SH = 8442.96452; BV0 = 148795.5            # trieu cp; VCSH me 30/09/2026 [HN-Q3]
PAYOUT = 0.20; TAXF = 0.80 / 0.88           # thue 20% vs ETR hien hanh ~12% [dd_HPG_20261031 GAPS §2]
SC = {'XAU': dict(w=0.25, e=[5500, 16000, 15000, 16000], g=0.03),
      'TRUNG_LAP': dict(w=0.50, e=[7000, 26000, 26000, 27000], g=0.05),
      'TOT': dict(w=0.25, e=[8000, 31000, 33000, 35000], g=0.05)}
TLSH = 9915.0
XDCB, COMMIT = 16113.0, 19472.0             # XDCB 30/09 [HN-Q3]; COMMIT = cam ket von tai 30/06/2026 (notes_bs.md:73 TM41), KHONG phai HN-Q3.
# LUU Y: phan chi Q3 da chuyen vao XDCB 30/09 => dem trung ~-200 d/cp o muc r (uoc luong, chua chay lai; khong sua so)
TLSH_AX_R2 = ((-0.25, 0.10), (0.0, 0.50), (0.25, 0.20), (0.50, 0.12), (1.00, 0.08))
SLOPE = (-0.05, 0.0, 0.05); MULT = (0.80, 0.90, 1.00, 1.10, 1.20); DG = (-0.01, 0.0, 0.01)

d0 = effective_deposit_rate(ANCHOR_DATE); d1 = effective_deposit_rate(ASOF)
R = R_ANCHOR + 1.0 * (d1['rate'] - d0['rate'])
DEP_AT = d1['rate'] * 0.80                  # lai tien gui 12T sau thue 20%


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


def ri(e, ke, g, mult=1.0, dg=0.0, roll=0.0, ret='zero', taxy=2030, gpol='r2'):
    """ret: 'zero' (r2) | 'dep' (moi von giu lai = lai tien gui sau thue) | 'capex' (COMMIT tu von giu lai + XDCB trong BV0 sinh loi = r, con lai = tien gui sau thue)
       | 'skcapex' (skeptic: 35.585 dau tien cua von giu lai = r, XDCB trong BV0 = 0)
       | float (moi von giu lai sinh loi = so nay, dung cho gia ngu y)."""
    bv = BV0; pv = 0.0; t = 0.0; cum = 0.0; e = [x * mult for x in e]; inc = 0.0; base = 0.0
    for i, ni in enumerate(e):
        dt = 0.25 if i == 0 else 1.0
        if ret == 'zero': inc = 0.0
        elif ret == 'dep': inc = DEP_AT * cum * dt
        elif ret == 'capex': inc = (ke * min(cum, COMMIT) + DEP_AT * max(cum - COMMIT, 0.0) + ke * XDCB) * dt   # XDCB theo gia so sinh loi = r tu 30/09 (NPV0 dung nghia)
        elif ret == 'skcapex': inc = (ke * min(cum, XDCB + COMMIT) + DEP_AT * max(cum - XDCB - COMMIT, 0.0)) * dt   # cach skeptic: 35.585 cua von giu lai = r
        else: inc = float(ret) * cum * dt
        tot = ni + inc; t += dt
        pv += (tot - ke * dt * bv) / (1 + ke) ** t; bv += tot * (1 - PAYOUT); cum += tot * (1 - PAYOUT); base = ni
    gg = g + dg
    inc_y = inc / (0.25 if len(e) == 1 else 1.0)
    roe12 = (base * (1 + gg) + inc_y * (1 + gg)) / bv          # ETR hien hanh (taxf=1) cho phan thep
    roe20 = (base * (1 + gg) * TAXF + inc_y * (1 + gg)) / bv    # thue 20% chi ap phan thep (phan tang them da sau thue)
    n1 = max(0, min(taxy, 2200) - 2030)                         # so nam ETR hien hanh sau 2029
    def gri(roe): return 0.0 if (gpol == 'npv0' or roe < ke) else gg
    g1, g2 = gri(roe12), gri(roe20)
    tv = sum((roe12 - ke) * bv * (1 + g1) ** (k - 1) / (1 + ke) ** k for k in range(1, n1 + 1))
    tv += (roe20 - ke) * bv * (1 + g1) ** n1 / (ke - g2) / (1 + ke) ** n1
    tv /= (1 + ke) ** t
    return (BV0 + pv + tv) / SH * 1e3 * (1 + ke) ** roll, roe20, roe12


def make_fn(roll, ret, taxy, gpol):
    def fn(r, scen, mult, dg, slope, tlsh):
        s = SC[scen]; e = list(s['e']); e[2] *= 1 + slope; e[3] *= (1 + slope) ** 2
        rr = ret[scen] if isinstance(ret, dict) else ret
        return ri(e, r, s['g'], mult=mult, dg=dg, roll=roll, ret=rr, taxy=taxy, gpol=gpol)[0] - tlsh * TLSH / SH * 1e3
    return fn


def axes(tlsh_ax):
    return [('scen', [(n, s['w']) for n, s in SC.items()]), ('mult', [(x, 0.2) for x in MULT]), ('dg', [(x, 1 / 3) for x in DG]),
            ('slope', [(x, 1 / 3) for x in SLOPE]), ('tlsh', list(tlsh_ax))]


def run(fn, ax, px, d, r=R):
    return R2C.stats(R2C.outcomes(ax, lambda **kw: fn(r, **kw)), px, d)


def roll_of(pxd): return (np.datetime64(pxd) - np.datetime64('2026-09-30')).astype(int) / 365


# ---- CONTROL: tai lap r2 (gia/thanh khoan 04/11, csv r2) ----
L04 = liq(os.path.join(ROOT, '_common_014125', 'bq_px_liq_20261104.csv'), '2026-11-04')
ctrl = run(make_fn(roll_of('2026-11-04'), 'zero', 2030, 'r2'), axes(TLSH_AX_R2), L04['px'], L04['d_ref'])
L = liq(os.path.join(HERE, 'px_hpg_r3_20261106.csv'), ASOF); PX, PXD, D = L['px'], L['pxd'], L['d_ref']; ROLL = roll_of(PXD)
print(f"== HPG VONG 3 | gia {PX:,.0f} ({PXD}, BQ) | r {R:.2%} (dep 12T {d1['rate']:.2%} {d1['rate_source']}; neo {d0['rate']:.2%}) | dep sau thue {DEP_AT:.2%}")
print("CONTROL r2 tai lap (04/11):", R2C.fmt(ctrl))

# ---- BRIDGE r2 -> r3 (tung buoc, cong don) ----
H = dict(ret='capex', taxy=2035, gpol='npv0', tlsh=((0.0, 1.0),))
steps = [('0 r2 (gia 04/11)', None),
         ('1 gia+thanh khoan 06/11, roll', dict(ret='zero', taxy=2030, gpol='r2', tlsh=TLSH_AX_R2)),
         ('2 C1 von giu lai: COMMIT+XDCB = r, con lai tien gui sau thue', dict(ret='capex', taxy=2030, gpol='r2', tlsh=TLSH_AX_R2)),
         ('3 C3 bo thuong moat ngam (g_RI=0 moi nhanh)', dict(ret='capex', taxy=2030, gpol='npv0', tlsh=TLSH_AX_R2)),
         ('4 C4 TLSH ve so sach trong base', dict(ret='capex', taxy=2030, gpol='npv0', tlsh=((0.0, 1.0),))),
         ('5 C2 thue 20% tu 2035 (lich uu dai DQ1) thay 2030', H)]
bridge = []; prev = ctrl['center']
for nm, cfg in steps:
    s = ctrl if cfg is None else run(make_fn(ROLL, cfg['ret'], cfg['taxy'], cfg['gpol']), axes(cfg['tlsh']), PX, D)
    bridge.append(dict(step=nm, center=round(s['center']), delta=round(s['center'] - prev), p10=round(s['p10']), p90=round(s['p90']))); prev = s['center']
    print(f"BRIDGE {nm}: tam {s['center']:,.0f} ({s['center'] - bridge[0]['center'] if bridge else 0:+,.0f} luy ke) P10 {s['p10']:,.0f} P90 {s['p90']:,.0f}")

FH = make_fn(ROLL, H['ret'], H['taxy'], H['gpol']); AXH = axes(H['tlsh'])
res = R2C.outcomes(AXH, lambda **kw: FH(R, **kw)); R2C.write_grid(os.path.join(HERE, 'grid_hpg_r3.csv'), res)
main = R2C.stats(res, PX, D); pre = R2C.stats(res, PX, 0.0)
central = FH(R, scen='TRUNG_LAP', mult=1.0, dg=0.0, slope=0.0, tlsh=0.0) * (1 - D)
print("HEADLINE r3 (sau CK 5 ty):", R2C.fmt(main)); print("Truoc CK:", R2C.fmt(pre))
print(f"Gia tri tai tham so trung tam sau CK: {central:,.0f}")
for sc in SC:
    v, r20, r12 = ri(SC[sc]['e'], R, SC[sc]['g'], roll=ROLL, ret='capex', taxy=2035, gpol='npv0')
    v0, r20o, _ = ri(SC[sc]['e'], R, SC[sc]['g'], roll=ROLL)
    print(f"  {sc}: gia tri {v:,.0f} (r2-style {v0:,.0f}) | ROE_T sau thue 20%: r3 {r20:.2%} vs r2 {r20o:.2%} | ROE_T ETR 12% r3 {r12:.2%}")

# ---- BIEN THE SONG SONG ----
alts = {
 'A_skeptic_san_dep_6pct_moi_von_giu_lai': dict(ret='dep', taxy=2035, gpol='npv0', tlsh=((0.0, 1.0),)),
 'B_capex_r_thue_2030_(chi C1+C3+C4)': dict(ret='capex', taxy=2030, gpol='npv0', tlsh=((0.0, 1.0),)),
 'C_capex_r_thue_12pct_vinh_vien': dict(ret='capex', taxy=9999, gpol='npv0', tlsh=((0.0, 1.0),)),
 'D_capex_r_thue2035_gRI_r2': dict(ret='capex', taxy=2035, gpol='r2', tlsh=((0.0, 1.0),)),
 'E_capex_r_thue2035_truc_TLSH_r2': dict(ret='capex', taxy=2035, gpol='npv0', tlsh=TLSH_AX_R2),
 'F_von_giu_lai_0pct_(r2)_thue2035': dict(ret='zero', taxy=2035, gpol='npv0', tlsh=((0.0, 1.0),)),
 'G_dep_6pct_thue2030_gRI_r2_TLSH_r2 (tai lap skeptic san)': dict(ret='dep', taxy=2030, gpol='r2', tlsh=TLSH_AX_R2),
 'H_skcapex_thue2030_gRI_r2_TLSH_r2 (tai lap skeptic capex)': dict(ret='skcapex', taxy=2030, gpol='r2', tlsh=TLSH_AX_R2),
 'J_TOT_chi_tien_gui (chong dem trung capex o nhanh TOT)': dict(ret=dict(XAU='capex', TRUNG_LAP='capex', TOT='dep'), taxy=2035, gpol='npv0', tlsh=((0.0, 1.0),)),
 'I_skcapex_khung_r3 (XDCB trong BV0 khong sinh loi)': dict(ret='skcapex', taxy=2035, gpol='npv0', tlsh=((0.0, 1.0),)),
}
alt_out = {}
for k, c in alts.items():
    s = run(make_fn(ROLL, c['ret'], c['taxy'], c['gpol']), axes(c['tlsh']), PX, D); alt_out[k] = s
    print(f"SONG SONG {k}:", R2C.fmt(s))
rax = [(R - 0.01, 0.25), (R, 0.50), (R + 0.01, 0.25)]
s_r = R2C.stats(R2C.outcomes(AXH + [('r', rax)], lambda r, **kw: FH(r, **kw)), PX, D); alt_out['co_truc_r_pm1pp'] = s_r
print("SONG SONG co_truc_r_pm1pp:", R2C.fmt(s_r))
sens_r = {f'{dr*1e4:+.0f}bp': round(run(FH, AXH, PX, D, r=R + dr)['center']) for dr in (-0.01, -0.005, 0.005, 0.01)}
print("Do nhay r (tam):", sens_r)


# ---- GIA NGU Y ----
def solve(f, lo, hi):
    up = f(hi) > f(lo)                      # ham dong bien?
    for _ in range(60):
        m = (lo + hi) / 2
        if (f(m) > PX) != up: lo = m
        else: hi = m
    return m
r_imp = solve(lambda rr: run(FH, AXH, PX, D, r=rr)['center'], 0.08, 0.20)
def c_ret(yy, taxy, gpol, tl): return run(make_fn(ROLL, yy, taxy, gpol), axes(tl), PX, D)['center']
y_imp_r2 = solve(lambda yy: c_ret(yy, 2030, 'r2', TLSH_AX_R2), 0.0, 0.40)        # moi von giu lai sinh loi y (XDCB = 0), con lai nhu r2
y_imp_r3 = solve(lambda yy: c_ret(yy, 2035, 'npv0', ((0.0, 1.0),)), 0.0, 0.40)
mult_imp = solve(lambda mm: R2C.stats(R2C.outcomes([a if a[0] != 'mult' else ('mult', [(mm, 1.0)]) for a in AXH], lambda **kw: FH(R, **kw)), PX, D)['center'], 0.5, 2.0)
roeT_imp = ri([x * mult_imp for x in SC['TRUNG_LAP']['e']], R, 0.05, roll=ROLL, ret='capex', taxy=2035, gpol='npv0')[1]
print(f"GIA NGU Y: r {r_imp:.2%} | von giu lai sinh loi y (khung r2) {y_imp_r2:.2%} (khung r3, moi von giu lai) {y_imp_r3:.2%} | he so duong LN {mult_imp:.3f} -> ROE_T TRUNG_LAP sau thue {roeT_imp:.2%}")

LOCK_FILES = [os.path.abspath(__file__), os.path.join(HERE, 'px_hpg_r3.sql'), os.path.join(HERE, 'px_hpg_r3_20261106.csv'),
              os.path.join(ROOT, '_common_014125', 'r2common.py'), os.path.join(ROOT, '_common_014125', 'bq_px_liq_20261104.csv'),
              os.path.join(ROOT, '_shared', 'wpct.py'), os.path.join(ROOT, 'HPG', 'calc', 'hpg_r2.py'), os.path.join(ROOT, 'HPG', 'calc', 'hpg_redo.py'),
              '/home/trido/thanhdt/WorkingClaude/deposit_rate_vn.py', '/home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py',
              '/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv', '/home/trido/thanhdt/WorkingClaude/data/cctg_rate_vn_events.csv',
              os.path.join(HERE, 'summary_r3_extra.json'), os.path.join(ROOT, 'TOP5_CORRECTIONS_20261108.md'), os.path.join(ROOT, 'SKEPTIC_TOP5_20261108.md'), os.path.join(ROOT, 'STANDARD_r2.md')]
LOCK = {os.path.relpath(p, ROOT): hashlib.md5(open(p, 'rb').read()).hexdigest() for p in LOCK_FILES}
for k, v in LOCK.items(): print(f"LOCK {v} {k}")


def r1(x): return int(round(x))
def sm(s): return {k: (r1(v) if k not in ('pct_below_px', 'n') else v) for k, v in s.items()}


SUMP = os.path.join(ROOT, 'HPG', 'SUMMARY.json'); BK = os.path.join(ROOT, 'HPG', 'SUMMARY_r2.json')
if not os.path.exists(BK): shutil.copyfile(SUMP, BK)
old = json.load(open(BK)); S = dict(old)
lab = 'DƯỚI vùng' if PX < main['p10'] else ('TRÊN vùng' if PX > main['p90'] else 'TRONG vùng')
S.update(round='r3', job='Taylor_20261108_142020', asof_price_date=PXD, price=PX, r=R,
         r_anchor=dict(r=R_ANCHOR, rate=d0['rate'], source=d0['rate_source'], date=ANCHOR_DATE, dep_asof=d1['rate'], dep_asof_source=d1['rate_source'], rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
         center_post_liq=r1(main['center']), center_pre_liq=r1(pre['center']), p10_post=r1(main['p10']), p25_post=r1(main['p25']), p50_post=r1(main['p50']),
         p75_post=r1(main['p75']), p90_post=r1(main['p90']), p10_pre=r1(pre['p10']), p50_pre=r1(pre['p50']), p90_pre=r1(pre['p90']),
         p10_out=r1(main['p10']), p50_out=r1(main['p50']), p90_out=r1(main['p90']), pct_weight_below_price=main['pct_below_px'], n_outcomes=main['n'],
         min_outcome=r1(main['min']), central_param_value_post=r1(central), liq_disc_5ty=D, label=lab,
         px_vs_center_post=PX / main['center'] - 1, px_vs_p10_post=PX / main['p10'] - 1, px_vs_p90_post=PX / main['p90'] - 1,
         ck_ref_size=dict(size_vnd=5e9, disc_adv250=D, disc_adv60=L['d_ref_adv60'], adv250=L['adv250']['adv_med'], adv60=L['adv60']['adv_med'], part_adv250=L['adv250']['part']['5000000000']),
         ck_real_sleeve=dict(sizes_vnd=[10e6, 40e6], disc_adv250={'10tr': L['adv250']['disc']['10000000'], '40tr': L['adv250']['disc']['40000000']},
                             note='sleeve 10-40tr = 0,002-0,007% ADV250, DUOI vung hieu chinh luat can bac hai (CK that ~ nua spread, chua do)'),
         grid_desc=('Luoi n=225: kich ban XAU/TRUNG LAP/TOT (0,25/0,50/0,25) x he so LN 0,8..1,2 (deu) x dich g -1/0/+1pp (deu) x doc LN 2028-29 -5/0/+5% (deu) [UL]; '
                    'TLSH = so sach (truc r2 la song song E). RI, BV0 VCSH me 30/09; von giu lai: COMMIT 19.472 tu von giu lai + XDCB 16.113 sinh loi = r (NPV0, luat 20; XDCB tu 30/09), '
                    'phan con lai = lai huy dong 12T sau thue; thue 20% cho phan thep tu 2035 (ETR hien hanh 2030-34); g_RI terminal = 0 moi nhanh (moat NARROW khong ben). Sau CK 5 ty Y=1.'),
         grid_n=main['n'], sens_r=sens_r, r_implied_center_eq_px=r_imp,
         parallel_versions={k: sm(v) for k, v in alt_out.items()}, bridge_r2_to_r3=bridge, control_r2_reproduced=sm(ctrl),
         implied_by_price=dict(r=r_imp, retained_return_r2_frame=y_imp_r2, retained_return_r3_frame=y_imp_r3, path_mult=mult_imp, roeT_after_tax_trung_lap=roeT_imp),
         lock_md5=LOCK, zone_r2=dict(center=old['center_post_liq'], p10=old['p10_post'], p90=old['p90_post'], label=old['label'], price=old['price'], date=old['asof_price_date']))
def labf(x): return 'DƯỚI vùng' if PX < x['p10'] else ('TRÊN vùng' if PX > x['p90'] else 'TRONG vùng')
S['headline_vs_alternatives'] = [dict(name='HEADLINE r3', center=r1(main['center']), p10=r1(main['p10']), p50=r1(main['p50']), p90=r1(main['p90']), pct_below_px=main['pct_below_px'], label=lab)] + \
    [dict(name=k, center=r1(v['center']), p10=r1(v['p10']), p50=r1(v['p50']), p90=r1(v['p90']), pct_below_px=v['pct_below_px'], label=labf(v)) for k, v in alt_out.items()]
EXTRA = os.path.join(HERE, 'summary_r3_extra.json')
if os.path.exists(EXTRA): S.update(json.load(open(EXTRA)))
json.dump(S, open(SUMP, 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=main, pre=pre, central=central, ctrl=ctrl, bridge=bridge, alts=alt_out, sens_r=sens_r, liq=L, lock=LOCK,
               implied=dict(r=r_imp, y_r2=y_imp_r2, y_r3=y_imp_r3, mult=mult_imp, roeT=roeT_imp)), open(os.path.join(HERE, 'hpg_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(f"NHAN: {lab} | gia {PX:,.0f} vs tam {main['center']:,.0f} ({PX/main['center']-1:+.1%}) | SUMMARY.json (r3) written")
