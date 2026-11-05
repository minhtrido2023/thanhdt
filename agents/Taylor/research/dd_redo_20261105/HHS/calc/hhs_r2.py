"""DD REDO VONG 2 HHS (job Taylor_20261105_020013) — phan mo hinh chep nguyen van tu hhs_redo.py (vong 1, dong 2-40); phan duoi theo STANDARD_r2.md.
Khung hien hanh: r = 13,5% gan lai huy dong 12T hieu dung (ban cu Ke 12,85%); CK thanh khoan _common_014125/common.py;
(c) du an moi: HTK du an I.14 (Dai Loc) 1.329 ty = GIA SO, thang du 0 (NPV 0) - chi NC-II/HTK cu duoc thang du (co so: bien NC-II quan sat 51,9-52,2%);
(d) phap ly/quan tri = WARNING: BO 'CK quan tri' 15/10/5% khoi base (ban cu) -> chi con la do nhay.
DAU VAO: chep tu dd_HHS_20261101/calc/valuation_v2.py (BCTC goc Q3HN 30/09/2026 + tham so DD TCH v2); gia dinh = (uoc luong)."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C

TK = 'HHS'
SH = 431.985968; HHS = 0.5115                # trieu cp; loi ich HHS tai CRV [Q3HN TM1.5]
EQ_ME, NCI = 9152.94, 7726.98                # VCSH me, loi ich CĐKKS 30/09 [Q3HN]
CRV_FV = NCI / (1 - HHS)
STEP_AT = 2020.76 / 0.20 * 0.8               # thang du PPA con lai sau thue (tu thue hoan lai 2.020,76) [Q3HN]
CRV_COST = CRV_FV - STEP_AT
OTHER = EQ_ME - HHS * CRV_FV - (694.84 - 310.74)   # tien me, Pruksa, Hoang Giang... (ban cu)
NMTT, VAT = 3099.20, 1.08                    # nguoi mua tra truoc NC-II; VAT [DD TCH v2]
REST_CRV = 7338.8                            # HTK CRV con lai [DD TCH v2]
NEW_I14 = 1329.0                             # HTK du an I.14 Dai Loc 30/09 (gom tien dat ~1.066) [dd_HHS REPORT §5 TM18] - (uoc luong: gia dinh nam trong REST_CRV)
SC = {  # p, m bien rong backlog, s thang du HTK cu, LNST o to, P/E, CK holding  — giu ban 01/11, g (CK quan tri) = 0
 'TIEU_CUC': dict(p=0.30, m=0.30, s=0.15, np=25, pe=5, hd=0.35),
 'CO_SO':    dict(p=0.50, m=0.335, s=0.40, np=35, pe=6, hd=0.25),
 'TICH_CUC': dict(p=0.20, m=0.36, s=0.55, np=50, pe=8, hd=0.15),
}
L = C.liquidity(TK, free_float=1 - 0.5831 - 0.0512, ff_src='1 - TCH 58,31% - nhom Dinh Quang Chien 5,12% (19/10/2026) [BCTN25 p.15; CBTT]')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']
pv = lambda y, ke: 1 / (1 + ke) ** y


def crv(m, s, ke, s_new=0.0):
    return CRV_COST + NMTT / VAT * m * pv(1, ke) + (REST_CRV - NEW_I14) * s * pv(4, ke) + NEW_I14 * s_new * pv(4, ke)


def val(sc, ke, ds=0.0, dhd=0.0, gov=0.0, s_new=0.0):
    s = SC[sc]; c = crv(s['m'], max(s['s'] + ds, 0.0), ke, s_new)
    return ((HHS * c) * (1 - min(max(s['hd'] + dhd, 0.0), 0.9)) + OTHER + s['np'] * s['pe']) * (1 - gov) / SH * 1e3


import json

# ======================= VONG 2 =======================
import r2common as R2C
BDS_SURP = (2459.74 - 1438.45) * 0.8          # thang du BDSDT CRV sau thue, can duoi chenh so [Q3HN; vong 1 §6]
KQ = 28.4                                      # ky quy cho ca nhan Pham Van Xuan [GAPS_FILL:108-113]
HD_AX = ((0.0, 0.10), (0.15, 0.15), (0.25, 0.30), (0.35, 0.30), (0.45, 0.15))   # CK holding tuyet doi [UL]; ky vong 0,27 ~ vong 1 (0,26)
GOV_AX = ((0.0, 0.55), (0.05, 0.20), (0.10, 0.15), (0.15, 0.10))                  # CK quan tri [UL]; diem = muc ban cu 5/10/15%
BDS_AX = ((0.0, 1 / 3), (0.5, 1 / 3), (1.0, 1 / 3))                               # ty le thang du BDSDT thuc hien [UL]
I14_AX = ((-0.15, 0.25), (0.0, 0.50), (0.40, 0.25))                               # thang du I.14 [UL]
KQ_AX = ((0.0, 0.70), (1.0, 0.30))                                                # mat ky quy [UL]


def fv2(r, scen, ds, hd, gov, bds, i14, kq):
    s = SC[scen]; c = crv(s['m'], max(s['s'] + ds, 0.0), r, i14)
    core = HHS * c * (1 - hd) + OTHER + s['np'] * s['pe'] + bds * BDS_SURP * HHS * (1 - hd) - kq * KQ
    return core * (1 - gov) / SH * 1e3


DS = (-0.15, -0.075, 0.0, 0.075, 0.15)
axes = [('scen', [(k, s['p']) for k, s in SC.items()]), ('ds', [(x, 1 / 5) for x in DS]), ('hd', list(HD_AX)), ('gov', list(GOV_AX)),
        ('bds', list(BDS_AX)), ('i14', list(I14_AX)), ('kq', list(KQ_AX))]
central_kw = dict(scen='CO_SO', ds=0.0, hd=0.0, gov=0.0, bds=0.0, i14=0.0, kq=0.0)
RES = R2C.finalize(TK, HERE, PX, PXD, R, axes, fv2, central_kw, ['hd', 'gov', 'bds', 'i14', 'kq'])
m = RES['main']
print(f"== HHS VONG 2 | gia {PX:,.0f} ({PXD}) | r {R:.2%}")
print("Luoi chinh (sau CK 5 ty):", R2C.fmt(m))
print("Truoc CK:", R2C.fmt(RES['pre']))
for k, s in RES['parallel'].items(): print(f"Song song {k}:", R2C.fmt(s))
# ban cau truc vong 1 (CK holding gan kich ban 35/25/15 +-5pp, khong truc moi) tinh lai bang wpct
def fv_r1(r, scen, ds, dhd):
    return fv2(r, scen, ds, SC[scen]['hd'] + dhd, 0.0, 0.0, 0.0, 0.0)
r1grid = R2C.outcomes([('scen', [(k, s['p']) for k, s in SC.items()]), ('ds', [(x, 1 / 5) for x in DS]), ('dhd', [(x, 1 / 3) for x in (-0.05, 0.0, 0.05)])], lambda **kw: fv_r1(R, **kw))
print("Doi chieu: luoi vong 1 tinh lai bang wpct:", R2C.fmt(R2C.stats(r1grid, PX, RES['d_ref'])))
hd25 = fv2(R, **dict(central_kw, hd=0.25)) * (1 - RES['d_ref'])
print(f"Gia tri tai tham so trung tam (CO_SO, ds 0, CK holding 0 = NAV thuan, gov 0, BDSDT 0, I.14 NPV0, ky quy 0) sau CK: {RES['central']:,.0f} | cung tham so nhung CK holding 25%: {hd25:,.0f}")
print(f"Nhom kich ban quanh P10: {RES['drivers']['p10_scen_mix_pm5pct']} | quanh P90: {RES['drivers']['p90_scen_mix_pm5pct']}")
Lq = RES['liq']
print(f"Thanh khoan: ADV250 {Lq['adv250']['adv_med']/1e9:,.1f} ty, ADV60 {Lq['adv60']['adv_med']/1e9:,.1f} ty | CK 5 ty {Lq['d_ref']:.3%} (ADV60 {Lq['d_ref_adv60']:.3%}) | sleeve 10tr {Lq['d_sleeve']['10tr']:.4%} 40tr {Lq['d_sleeve']['40tr']:.4%}")
print("  " + Lq['calib_note'])
print(f"NHAN: {RES['label']} (vung P10-P90 muc ket cuc, CK o co 5 ty)")
print(f"Don vi truc: BDSDT 100% = +{BDS_SURP*HHS/SH*1e3:,.0f} d/cp truoc CK holding; ky quy mat trang = -{KQ/SH*1e3:,.0f} d/cp; I.14 +40% = +{1329*0.4/(1.135**4)*HHS/SH*1e3:,.0f} d/cp truoc CK holding (PV4 @ r)")
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'hhs_redo.py'), os.path.join(C.HERE, 'common.py'), os.path.join(C.HERE, 'r2common.py'),
                 os.path.join(C.HERE, 'bq_px_liq_20261104.csv'), os.path.join(C.HERE, '..', '_shared', 'wpct.py'), os.path.join(C.WC, 'deposit_rate_vn.py'),
                 os.path.join(C.WC, 'cctg_rate_vn.py'), os.path.join(C.WC, 'data/deposit_rate_vn_events.csv'), os.path.join(C.WC, 'data/cctg_rate_vn_events.csv'),
                 os.path.join(C.WC, 'mike/kb/dd_price_zones.json')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
extra = dict(
  axes_included=['kich ban TIEU_CUC/CO_SO/TICH_CUC (0,30/0,50/0,20)', 'dich thang du HTK CRV cu -15..+15pp (5 diem deu)',
                 'CK holding tuyet doi 0/15/25/35/45% (0,10/0,15/0,30/0,30/0,15) [UL] (vong 1: gan kich ban 35/25/15 +-5pp)',
                 'CK quan tri 0/5/10/15% (0,55/0,20/0,15/0,10) [UL]', 'thang du BDSDT CRV thuc hien 0/50/100% (deu) [UL]',
                 'thang du I.14 -15/0/+40% (0,25/0,50/0,25) [UL]', 'mat ky quy ca nhan 28,4 ty 0/100% (0,70/0,30) [UL]'],
  axes_excluded=[dict(axis='r', reason='NAV gan nhu khong nhay r (PV 1-4 nam); ban song song co_truc_r_pm1pp'),
                 dict(axis='KL 08/KL-TTTP Pruksa dieu chinh gia ban; N01 tien SDD bo sung 7,87 ty', reason='khong co so luong hoa Pruksa; N01 ~9 d/cp (7,87 x 51,15% / 432) khong trong yeu -> WARNING'),
                 dict(axis='dieu chinh soat xet LN Q3 (6T bi ha -34%)', reason='anh huong qua NAV nho (LN da nam trong VCSH); WARNING + moc M1')],
  base_adjustments=[dict(item='CK holding o THAM SO TRUNG TAM', effect_dong_per_share=0, basis='vong 2: muc 25% khong co co so du lieu (chi la uoc luong) -> tham so trung tam = 0 (NAV thuan); CK holding chi o truc co xac suat; co so dinh tinh: CRV chua tra co tuc tien ve HHS 9T/2026, tien NC-II len HHS qua 2 tang', source='Q3HN LCTT; vong 1 §6.1'),
                    dict(item='Thang du PPA CRV', effect_dong_per_share=None, basis='CRV theo gia goc (GTHL - thang du PPA sau thue 8.083); thang du HTK cu theo bien NC-II quan sat 51,9-52,2% (base 40%)', source='Q3HN TM thue hoan lai 2.020,76; DD TCH v2'),
                    dict(item='I.14 1.329 ty', effect_dong_per_share=0, basis='gia so NPV 0 (chua mo ban)', source='dd_HHS REPORT §5 TM18')],
  gordon_crosscheck='khong ap dung (NAV holding; khong co dong ROE on dinh)', lock_md5=LOCK,
  warnings_r2_added=["HHS Capital: premium 143,5 ty (~12% tren GTHL), BBTT 02/2025 06/05/2025 trao quyen bo nhiem truoc khi tra tien, ngay lap lech 31/03 vs 31/05/2025, to trinh 07/TT-HDQT chi khang dinh 'khong lien quan'",
                     "Uy quyen bieu quyet 7,37-7,53% CRV tu nhom co dong khong ten; nhom TCH kiem soat 89,35% bieu quyet CRV; so huu chong tang TCH-HHS-CRV",
                     "TB 2124/TB-TTCP 11/10/2024 dat khoi de N01 CRV: tien SDD bo sung tam trich 7,87 ty", "Chi phi phat/truy thu thue 2025 = 2,44 ty khong neu QD",
                     "Vay 390 ty CRV (VietinBank) dao han 18/11/2026, the chap NC-II", "Dai ly Dongfeng: khong co tu 'doc quyen', hop dong/thoi han chua co",
                     "Du toan chi phi con lai giao can NC-II (3.099 da nhan tien) chua co"],
  fear_buy_eligible_2_5=False)
S = R2C.write_summary(os.path.join(HERE, '..', 'SUMMARY.json'), dict(price=PX), RES, extra)
S['center_vs_p50_note'] = f"tam = ky vong luoi {m['center']:,.0f}; P50 {m['p50']:,.0f}; gia tri tai tham so trung tam (NAV thuan, CK holding 0) {RES['central']:,.0f}; cung tham so CK holding 25% {hd25:,.0f}"
json.dump(S, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=m, pre=RES['pre'], parallel=RES['parallel'], central=RES['central'], central_hd25=hd25, drivers=RES['drivers'], liq=RES['liq'], lock=LOCK),
          open(os.path.join(HERE, 'hhs_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json (r2) written')
