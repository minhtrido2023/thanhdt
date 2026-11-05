"""DD REDO VONG 2 HPG (job Taylor_20261105_020013) — phan mo hinh chep nguyen van tu hpg_redo.py (vong 1, dong 2-49); phan duoi theo STANDARD_r2.md.
Khung hien hanh: r = 13,5% (Ke noi dia) gan lai huy dong 12T hieu dung (deposit_rate_vn), beta=1 (ban cu: Ke 11,83% = rf 6,75% + beta do 0,915 x ERP 5,55%).
Tam = ky vong RI thuan (ban cu: 2/3 RI + 1/3 EV/EBITDA 5x -> nay chi doi chieu). CK thanh khoan: _common_014125/common.py.
Du an dang/sap dau tu (XDCB 16.113, cam ket ~19.472, DQ2 con lai): RI dung BV0 theo gia so + capex tuong lai khong tru => NPV 0 ngam dinh (luat 03/11).
DAU VAO BCTC goc [HN-Q3] + duong LN kich ban: chep tu dd_HPG_20261031/calc/hpg_valuation_v2.py (v3, da qua skeptic CONFIRMED + GAPS/GAPS2)."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
import numpy as np

TK = 'HPG'
SH = 8442.96452; BV0 = 148795.5       # trieu cp luu hanh; VCSH me 30/09/2026 [HN-Q3]
PAYOUT, G = 0.20, 0.05
TAXF = 0.80 / 0.88                     # thue terminal 20% (het uu dai) vs ETR hien hanh ~12% [ban cu GAPS §2/§7]
SC = {  # LNST me Q4/26, 2027, 2028, 2029 (ty, uoc luong); g terminal; w  — giu nguyen ban v3 31/10
 'XAU':   dict(w=0.25, e=[5500, 16000, 15000, 16000], g=0.03),
 'TRUNG_LAP': dict(w=0.50, e=[7000, 26000, 26000, 27000], g=0.05),
 'TOT':   dict(w=0.25, e=[8000, 31000, 33000, 35000], g=0.05),
}
TLSH = 9915.0                          # co phan TLSH (duoi trai, KHONG vao base) [ban cu §6]
ND, PT_DH, MI, INV_LK = 59607.6, 3828.9, 772.9, 12664.1   # no rong, phai tra NB DH, CDKKS, lien ket [HN-Q3]

L = C.liquidity(TK, free_float=1 - 0.3546, ff_src='(uoc luong) 1 - nhom ong Tran Dinh Long ~35,46% [dd_HPG_20261031 REPORT §6]; NN 21,8%, room con 27,2% [WEB 24hmoney 30/10]')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']
ROLL = (np.datetime64(PXD) - np.datetime64('2026-09-30')).astype(int) / 365   # gia tri tinh tai 30/09 -> day toi ngay gia


NPV0_TERMINAL = True   # luat 03/11: von tang them khong bi gia dinh pha gia tri => ROE_T < r thi RI terminal KHONG tang (g_RI = 0)


def ri(e, ke, g, mult=1.0, dg=0.0, bv0=BV0, npv0=None):
    npv0 = NPV0_TERMINAL if npv0 is None else npv0
    bv = bv0; pv = 0.0; t = 0.0; e = [x * mult for x in e]
    for i, ni in enumerate(e):
        dt = 0.25 if i == 0 else 1.0; t += dt
        pv += (ni - ke * dt * bv) / (1 + ke) ** t; bv += ni * (1 - PAYOUT)
    gg = g + dg; roeT = e[-1] * (1 + gg) * TAXF / bv
    g_ri = 0.0 if (npv0 and roeT < ke) else gg
    tv = (roeT - ke) * bv / (ke - g_ri) / (1 + ke) ** t
    return (bv0 + pv + tv) / SH * 1e3 * (1 + ke) ** ROLL, roeT, tv / (bv0 + pv + tv)


def W(ke, ws=None, **kw):
    ws = ws or [s['w'] for s in SC.values()]
    return sum(w * ri(s['e'], ke, s['g'], **kw)[0] for w, s in zip(ws, SC.values()))


bvps = BV0 / SH * 1e3

# ======================= VONG 2 =======================
import r2common as R2C
TLSH_AX = ((-0.25, 0.10), (0.0, 0.50), (0.25, 0.20), (0.50, 0.12), (1.00, 0.08))   # ty le mat gia tri khoan TLSH 9.915 ty (am = lai) [UL]
SLOPE = (-0.05, 0.0, 0.05)   # doc LN 2028-29: e28*(1+s), e29*(1+s)^2 [SKEPTIC N2: khong kich ban nao tang] [UL]


def fv2(r, scen, mult, dg, slope, tlsh):
    s = SC[scen]; e = list(s['e']); e[2] *= 1 + slope; e[3] *= (1 + slope) ** 2
    return ri(e, r, s['g'], mult=mult, dg=dg)[0] - tlsh * TLSH / SH * 1e3


MULT = (0.80, 0.90, 1.00, 1.10, 1.20); DG = (-0.01, 0.0, 0.01)
axes = [('scen', [(n, s['w']) for n, s in SC.items()]), ('mult', [(x, 1 / 5) for x in MULT]), ('dg', [(x, 1 / 3) for x in DG]),
        ('slope', [(x, 1 / 3) for x in SLOPE]), ('tlsh', list(TLSH_AX))]
central_kw = dict(scen='TRUNG_LAP', mult=1.0, dg=0.0, slope=0.0, tlsh=0.0)
RES = R2C.finalize(TK, HERE, PX, PXD, R, axes, fv2, central_kw, ['slope', 'tlsh'])
m = RES['main']
print(f"== HPG VONG 2 | gia {PX:,.0f} ({PXD}) | BVPS {bvps:,.0f} | r {R:.2%} | TLSH 100% = {TLSH/SH*1e3:,.0f} d/cp")
print("Luoi chinh (sau CK 5 ty):", R2C.fmt(m))
print("Truoc CK:", R2C.fmt(RES['pre']))
for k, s in RES['parallel'].items(): print(f"Song song {k}:", R2C.fmt(s))
r1grid = R2C.outcomes([a for a in axes if a[0] in ('scen', 'mult', 'dg')] + [('slope', [(0.0, 1.0)]), ('tlsh', [(0.0, 1.0)])], lambda **kw: fv2(R, **kw))
print("Doi chieu: luoi vong 1 tinh lai bang wpct:", R2C.fmt(R2C.stats(r1grid, PX, RES['d_ref'])))
print(f"Gia tri tai tham so trung tam (TRUNG_LAP, mult 1, dg 0, slope 0, TLSH NPV0) sau CK: {RES['central']:,.0f}")
print(f"Nhom kich ban quanh P10: {RES['drivers']['p10_scen_mix_pm5pct']} | quanh P90: {RES['drivers']['p90_scen_mix_pm5pct']}")
Lq = RES['liq']
print(f"Thanh khoan: ADV250 {Lq['adv250']['adv_med']/1e9:,.1f} ty, ADV60 {Lq['adv60']['adv_med']/1e9:,.1f} ty | CK 5 ty {Lq['d_ref']:.3%} (ADV60 {Lq['d_ref_adv60']:.3%}) | sleeve 10tr {Lq['d_sleeve']['10tr']:.4%} 40tr {Lq['d_sleeve']['40tr']:.4%}")
print("  " + Lq['calib_note'])
print(f"NHAN: {RES['label']} (vung P10-P90 muc ket cuc, CK o co 5 ty)")
# r ngu y: tam luoi (sau CK) = gia
lo, hi = 0.08, 0.20
for _ in range(60):
    mm = (lo + hi) / 2
    c = sum(w * fv2(mm, **kw) for kw, _, w in R2C.outcomes(axes, lambda **kw: 0.0)) * (1 - RES['d_ref'])
    if c > PX: lo = mm
    else: hi = mm
print(f"r ma tam luoi sau CK = gia: {mm:.2%}")
ke_beta = {f'beta{b}': 0.0675 + b * 0.0555 for b in (0.84, 0.93, 1.0)}
kb = {k: sum(w * fv2(v, **kw) for kw, _, w in R2C.outcomes(axes, lambda **kw: 0.0)) * (1 - RES['d_ref']) for k, v in ke_beta.items()}
print("Doi chieu r theo beta (CAPM ban cu rf 6,75% + beta x ERP 5,55%; KHONG phai luat hien hanh): " + ' | '.join(f"{k} r {ke_beta[k]:.2%} -> tam {v:,.0f}" for k, v in kb.items()))
gord = {}
for lab, roe in (('ROE_2027_TRUNG_LAP', SC['TRUNG_LAP']['e'][1] / BV0), ('ROE_9T26_x4/3', 19200 * 4 / 3 / BV0)):
    for g in (0.04, 0.05):
        gord[f'{lab}_g{g}'] = bvps * (roe - g) / (R - g)
print("Gordon P/B (BVPS 30/09): " + ' | '.join(f"{k} {v:,.0f}" for k, v in gord.items()))
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'hpg_redo.py'), os.path.join(C.HERE, 'common.py'), os.path.join(C.HERE, 'r2common.py'),
                 os.path.join(C.HERE, 'bq_px_liq_20261104.csv'), os.path.join(C.HERE, '..', '_shared', 'wpct.py'), os.path.join(C.WC, 'deposit_rate_vn.py'),
                 os.path.join(C.WC, 'cctg_rate_vn.py'), os.path.join(C.WC, 'data/deposit_rate_vn_events.csv'), os.path.join(C.WC, 'data/cctg_rate_vn_events.csv'),
                 os.path.join(C.WC, 'mike/kb/dd_price_zones.json')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
extra = dict(
  axes_included=['kich ban XAU/TRUNG_LAP/TOT (0,25/0,50/0,25)', 'he so duong LN 0,8..1,2 (5 diem deu)', 'dich g terminal -1/0/+1pp (deu)',
                 'doc LN 2028-29 -5/0/+5%/nam (deu) [UL; SKEPTIC N2]', 'TLSH ty le mat gia tri -25/0/25/50/100% (0,10/0,50/0,20/0,12/0,08) [UL]'],
  axes_excluded=[dict(axis='r / beta rieng ma', reason='luat 03/11 r 13,5% dong nhat; ban song song co_truc_r_pm1pp + doi chieu beta 0,84/0,93/1,0 (cau hoi mo cho Mike/user)'),
                 dict(axis='26,55% BDS HP con lai + lien danh BT song Hong', reason='khong co so lieu de luong hoa (nghia vu gop von/bao lanh chua thuyet minh); WARNING'),
                 dict(axis='EV/EBITDA 5x', reason='doi chieu, khong vao tam (khong co comp)')],
  base_adjustments=[dict(item='TLSH o base', effect_dong_per_share=0, basis='so sach (NPV 0); lech nam o truc tlsh', source='HN-Q3; GAPS2'),
                    dict(item='Du an dang dau tu (XDCB 16.113, cam ket ~19.472, DQ2)', effect_dong_per_share=0, basis='BV0 theo gia so, capex tuong lai khong tru (NPV 0)', source='HN-Q3'),
                    dict(item='Thue terminal 20% (TAXF 0,80/0,88)', effect_dong_per_share=None, basis='het uu dai thue: Luat thue TNDN 20%; ETR hien hanh ~12%; thoi han uu dai chua cong bo', source='dd_HPG_20261031 GAPS §2/§7')],
  r_implied_center_eq_px_r2=mm, r_by_beta_crosscheck={k: dict(r=ke_beta[k], center=round(v)) for k, v in kb.items()},
  gordon_crosscheck={k: round(v) for k, v in gord.items()}, lock_md5=LOCK,
  warnings_r2_added=["QD 244/QD-XPHC 11/05/2022 phat 125 trieu (thieu TV HDQT doc lap) - lich su", "Giao dich noi bo: Tran Vu Minh mua 33,3 trieu + dang ky 50 trieu cp 07/10-05/11/2026; TV doc lap Dang Ngoc Khanh dang ky ban 100 nghin cp 04/11-03/12",
                     "Thu lao HDQT 2024 244,7 / 2025 83,2 / 6T26 207,7 ty", "Co tuc '15%' nam 2025 hay KH 2026 chua doi chieu TM28",
                     "Phong ve thuong mai: QD 1917/QD-BCT chong lan tranh 27,83% hieu luc 28/07/2026; vu AD ton ma My/EU/Uc/Dai Loan chua ra",
                     "Thue DQ2: CV 377/TCT-CS (30/01/2024) du an moi hay mo rong - chua co ket qua; thuyet minh thue KT25 chua doc"],
  fear_buy_eligible_2_5=False)
S = R2C.write_summary(os.path.join(HERE, '..', 'SUMMARY.json'), dict(price=PX), RES, extra)
S['center_vs_p50_note'] = f"tam = ky vong luoi {m['center']:,.0f}; P50 {m['p50']:,.0f}; gia tri tai tham so trung tam {RES['central']:,.0f}"
json.dump(S, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=m, pre=RES['pre'], parallel=RES['parallel'], central=RES['central'], drivers=RES['drivers'], liq=RES['liq'], gordon=gord, r_implied=mm, r_beta=kb, lock=LOCK),
          open(os.path.join(HERE, 'hpg_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json (r2) written')
