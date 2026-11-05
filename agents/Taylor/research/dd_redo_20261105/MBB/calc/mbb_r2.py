"""DD REDO VONG 2 MBB (job Taylor_20261105_020013) — phan mo hinh chep nguyen van tu mbb_redo.py (vong 1, dong 2-57); phan duoi theo STANDARD_r2.md.
Khung skill due-diligence hien hanh: r = Ke noi dia 13,5% @ lai huy dong 12T hieu dung 03/11 (deposit_rate_vn), beta=1;
CK thanh khoan theo _common_014125/common.py (luat can bac hai, Q=5 ty); MBV (du an/cam ket von moi) base = gia so sach (NPV 0).
DAU VAO BCTC: doc tu BCTC goc Q3/2026 (dd_MBB_20261031/src, so doc anh: dd_MBB_20261031/calc/notes_read.md) - chep nguyen gia tri, ghi trang.
Gia dinh tuong lai = (uoc luong)."""
import os, sys, json, csv, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import numpy as np

TK = 'MBB'
# ---- BCTC goc [HN-Q3] (ty dong) ----
BV = 164141.608 - 7124.845      # VCSH hop nhat - loi ich CĐKKS 30/09/2026 [HN-Q3 p3-4]
SH = 10068.749885               # trieu CP = VDL 100.687,5 ty / 10.000 [HN-Q3 tr.36]
NI9 = 23784.072                 # LNST thuoc CĐ NH me 9T26 [HN-Q3 p6]
NI_Q4_25 = 8762.570             # LNST NH me Q4/25 [HN-Q4/25]
LT9 = 30518.358                 # LNTT 9T26 [HN-Q3 p6]
KH26 = 39408                    # KH LNTT 2026 [WEB DHCD]
# ---- gia & thanh khoan ----
L = C.liquidity(TK, free_float=0.60, ff_src='(uoc luong) 1 - Viettel 14,7% - SCIC 9,8% - Truc thang 8,4% - Tan Cang 7,1% (WEB thu cap 2024-25) ~ 60%; room ngoai KIN')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']
bvps = BV / SH * 1e3; ttm = NI9 + NI_Q4_25
DAYS = (np.datetime64('2026-12-31') - np.datetime64(PXD)).astype(int)

# ---- kich ban (giu nguyen ban 31/10 da qua skeptic CONFIRMED; uoc luong) ----
SC = {  # w, PPOP Q4, DP Q4, g_loan27, NIM27, cc27, nonII/TA, CIR27, ROE path 27-29, ROE_T, g_T
 'XAU':   (0.35, 16000, 7500, 0.12, 0.036, 0.022, 0.0065, 0.28, [0.13, 0.14, 0.15], 0.14, 0.06),
 'CO_SO': (0.45, 17500, 5500, 0.18, 0.039, 0.017, 0.0070, 0.27, [0.185, 0.18, 0.17], 0.16, 0.07),
 'TOT':   (0.20, 18700, 4200, 0.24, 0.041, 0.013, 0.0075, 0.26, [0.22, 0.21, 0.20], 0.18, 0.08),
}
TAX, NCI, PAYOUT = 0.20, 0.025, 0.30
NPV0_TERMINAL = True


def ri_ps(path, roeT, gT, ke, bv0):
    bv = bv0; pv = 0.0
    for i, r in enumerate(path, 1):
        pv += (r - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - PAYOUT)
    g_ri = 0.0 if (NPV0_TERMINAL and roeT < ke) else gT   # luat 03/11: von moi NPV 0 => ROE_T < r thi RI terminal khong tang
    tv = (roeT - ke) * bv / (ke - g_ri) / (1 + ke) ** len(path)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (DAYS / 365), tv / (bv0 + pv + tv)


base = {}
for n, (w, pp4, dp4, g, nim, cc, nonii, cir, path, roeT, gT) in SC.items():
    lt26 = LT9 + pp4 - dp4; ni26 = lt26 * (1 - TAX) * (1 - NCI)
    bv26 = BV + (ni26 - NI9)
    base[n] = dict(w=w, lt26=lt26, bv26=bv26, path=path, roeT=roeT, gT=gT)


def value(n, ke, droe=0.0, dg=0.0, mbv=0.0):
    b = base[n]
    return ri_ps([x + droe for x in b['path']], b['roeT'] + droe, b['gT'] + dg, ke, b['bv26'] - mbv)



# ======================= VONG 2 =======================
import r2common as R2C
fn = lambda r, scen, droe, dg, mbv: value(scen, r, droe, dg, mbv)[0]
DROE = (-0.03, -0.015, 0.0, 0.015, 0.03); DG = (-0.01, 0.0, 0.01)
MBV_AX = ((-3500, 0.15), (0, 0.50), (3500, 0.25), (15688, 0.10))   # [UL] trong so; gia tri: +-gop 3.500 (QD 01/10/2026, WEB), lo luy ke 2024 15.688
axes = [('scen', [(n, SC[n][0]) for n in SC]), ('droe', [(x, 1 / 5) for x in DROE]), ('dg', [(x, 1 / 3) for x in DG]), ('mbv', list(MBV_AX))]
central_kw = dict(scen='CO_SO', droe=0.0, dg=0.0, mbv=0)
RES = R2C.finalize(TK, HERE, PX, PXD, R, axes, fn, central_kw, ['mbv'])
m = RES['main']
print(f"== MBB VONG 2 | gia {PX:,.0f} ({PXD}) | r {R:.2%}")
print("Luoi chinh (sau CK 5 ty):", R2C.fmt(m))
print("Truoc CK:", R2C.fmt(RES['pre']))
for k, s in RES['parallel'].items(): print(f"Song song {k}:", R2C.fmt(s))
print(f"Gia tri tai tham so trung tam (CO_SO, droe 0, dg 0, MBV NPV0) sau CK: {RES['central']:,.0f}")
print(f"Nhom kich ban quanh P10: {RES['drivers']['p10_scen_mix_pm5pct']} | quanh P90: {RES['drivers']['p90_scen_mix_pm5pct']}")
Lq = RES['liq']
print(f"Thanh khoan: ADV250 {Lq['adv250']['adv_med']/1e9:,.1f} ty, ADV60 {Lq['adv60']['adv_med']/1e9:,.1f} ty | CK 5 ty {Lq['d_ref']:.3%} (ADV60 {Lq['d_ref_adv60']:.3%}) | sleeve 10tr {Lq['d_sleeve']['10tr']:.4%} 40tr {Lq['d_sleeve']['40tr']:.4%}")
print("  " + Lq['calib_note'])
print(f"NHAN: {RES['label']} (vung P10-P90 muc ket cuc, CK o co 5 ty)")
# cross-check Gordon P/B (ngan hang: lai tien gui la nghiep vu loi => chi 1 bien the)
gord = {}
for lab, roe in (('ROE_TTM', ttm / BV), ('ROE_T_coso', 0.16)):
    for g in (0.06, 0.07):
        gord[f'{lab}_g{g}'] = bvps * (roe - g) / (R - g)
print("Gordon P/B (BVPS 30/09): " + ' | '.join(f"{k} {v:,.0f}" for k, v in gord.items()) + f" | ROE TTM {ttm/BV:.1%}")
ke15 = {k: sum(SC[n][0] * value(n, k)[0] for n in SC) for k in (0.145, 0.15)}
print('RI trong so (truoc CK, tham so trung tam) o Ke 14,5% / 15%: ' + ' / '.join(f'{v:,.0f}' for v in ke15.values()) + ' (doi chieu skeptic 31/10: ~20,5k @15%; R1 ghi 18,7k)')
# Q4/26 doi chieu (co skeptic 31/10): LNTT Q4 ngu y moi kich ban vs Q4/25
q4 = {n: SC[n][1] - SC[n][2] for n in SC}
print("LNTT Q4/26 ngu y (PPOP-DP): " + ', '.join(f"{n} {v:,.0f}" for n, v in q4.items()))
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'mbb_redo.py'), os.path.join(C.HERE, 'common.py'), os.path.join(C.HERE, 'r2common.py'),
                 os.path.join(C.HERE, 'bq_px_liq_20261104.csv'), os.path.join(C.HERE, '..', '_shared', 'wpct.py'), os.path.join(C.WC, 'deposit_rate_vn.py'),
                 os.path.join(C.WC, 'mike/kb/dd_price_zones.json')])
dep_extra = [p for p in ('cctg_rate_vn.py', 'data/deposit_rate_vn_events.csv', 'data/cctg_rate_vn_events.csv') if os.path.exists(os.path.join(C.WC, p))]
LOCK.update(R2C.md5s([os.path.join(C.WC, p) for p in dep_extra]))
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
extra = dict(
  axes_included=['kich ban XAU/CO_SO/TOT (0,35/0,45/0,20)', 'dich ROE 2027-29+T -3..+3pp (5 diem deu)', 'dich g_T -1/0/+1pp (deu)',
                 'MBV: -3.500 (loi ich uu dai, len) / 0 (NPV0) / +3.500 (mat trang gop) / +15.688 (bu lo luy ke 2024) trong so 0,15/0,50/0,25/0,10 [UL]'],
  axes_excluded=[dict(axis='r (Ke)', reason='luat 03/11: r neo lai huy dong 12T, khong phai bien bat dinh cua cong ty; bao song song co truc r +-1pp (parallel_versions.co_truc_r_pm1pp)'),
                 dict(axis='uu dai MBV (tran tin dung 35%/nam x4, room ngoai 49%)', reason='nam trong diem -3.500 cua truc MBV (len) va truc droe; khong co du lieu tach rieng')],
  base_adjustments=[dict(item='MBV o base', effect_dong_per_share=0, basis='NPV 0 (so sach): BCTC HN-Q3 tr.2 chua gop von MBV tai 30/09', source='HN-Q3 PDF p9')],
  center_vs_p50_note=f"tam = ky vong luoi {m['center']:,.0f}; P50 {m['p50']:,.0f}; gia tri tai tham so trung tam {RES['central']:,.0f}. Truc MBV lech xuong (diem 15.688) keo tam xuong {RES['parallel']['khong_truc_mbv']['center']-m['center']:,.0f} d/cp so ban khong truc MBV.",
  gordon_crosscheck={k: round(v) for k, v in gord.items()}, ri_at_ke_145_15={str(k): round(v) for k, v in ke15.items()}, lock_md5=LOCK,
  warnings_r2_added=["Uu dai MBV (tran tang truong tin dung, room ngoai 49% theo ND 69/2025) [WEB] - chua kiem", "No ngoai bang/no co cau TT02/Pillar 3 chua kiem",
                     "Cho vay ben lien quan, top-10/20 KH, TPDN BDS chua kiem", "Tier1 9,02% la so 30/06 truoc khi nhan ~8k quyen mua, khong phai CET1",
                     "Nghi quyet DHDCD/HDQT goc ve phat hanh 2026 chua doc (tach 15%+10% chi tu WEB)", "Lo phai sinh -1.066 (swap) la suy luan"],
  fear_buy_eligible_2_5=False)
S = R2C.write_summary(os.path.join(HERE, '..', 'SUMMARY.json'), dict(price=PX), RES, extra)
import json as _j
_j.dump(dict(main=m, pre=RES['pre'], parallel=RES['parallel'], central=RES['central'], drivers=RES['drivers'], liq=RES['liq'], gordon=gord, q4=q4, lock=LOCK),
        open(os.path.join(HERE, 'mbb_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json (r2) written')
