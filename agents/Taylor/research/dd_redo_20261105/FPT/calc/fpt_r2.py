"""DD REDO VONG 2 FPT (job Taylor_20261105_020013) — phan mo hinh chep nguyen van tu fpt_redo.py (vong 1, dong 2-56); phan duoi theo STANDARD_r2.md.
Khung skill hien hanh: r = 13,5% (Ke noi dia) gan lai huy dong 12T hieu dung (deposit_rate_vn), beta=1, MOT r cho moi kich ban
(ban cu: Ke 13,4/12,85/12,3% theo kich ban). CK thanh khoan: _common_014125/common.py. Du an dang dau tu (XDCB do dang khuon vien GD) = gia so (NPV 0).
DAU VAO BCTC goc Q3/2026 hop nhat: chep tu dd_FPT_20261101/calc/valuation.py (nguon trang ghi o do: notes_q3_bctc.md, BCTN25 p168/p170).
FOX/FRT: BQ tav2_bq.ticker 04/11/2026 (assoc_px_20261104.csv). Gia dinh tuong lai = (uoc luong)."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
import numpy as np

TK = 'FPT'
SH = 1885.727648                     # trieu cp sau thuong 10:1 (21/09/2026) [Q3HN p46]
# ---- BCTC goc Q3/2026 [Q3HN p03, p07, p08, p32, p45] ----
cash, htm, htm_l, st_debt, lt_debt = 7377.3, 21449.7, 2.5, 14316.5, 2280.0
NC = cash + htm + htm_l - st_debt - lt_debt     # tien rong 30/09 (chua tru co tuc 1.000d chot 30/11: gia 04/11 con quyen)
pat9, assoc9 = 7776.4, 2220.3                    # LNST 9T26, lai lien ket 9T26 [p08]
Q4_25_PAT, Q4_25_ASSOC = 2509.5, 600.0           # LNST me Q4/25 [BCTN25]; lai LK Q4/25 (uoc luong, GAPS G10)
NET_INT9 = 1283 - 612                            # lai tien gui - lai vay 9T [p45]
OTHER_ASSOC_BOOK = 1500.0                        # Synnex/FPT Online/khac theo so (uoc luong; BCTC khong tach)
INV_OTHER = 494.4 + 451.1                        # TPBank, FPTS gia goc [p32]
CIP_EDU = 415 + 247 + 61 + 37                    # XDCB do dang khuon vien GD: Binh Duong/Hoa Lac/Quy Nhon/Long An [Q3HN p37]
FTEL_PCT, FRT_PCT = 0.4566, 0.4654               # [Q3HN p14; BCTN25]
core_ttm = (pat9 - assoc9) + (Q4_25_PAT - Q4_25_ASSOC)
core_op = core_ttm - NET_INT9 * 4 / 3 * 0.85     # LN loi van hanh TTM (uoc luong)

ap = {r['ticker']: r for r in csv.DictReader(open(os.path.join(HERE, 'assoc_px_20261104.csv'))) if r['time'] == '2026-11-04'}
fox = float(ap['FOX']['Price']) * float(ap['FOX']['OShares']) / 1e9 * FTEL_PCT     # ty
frt = float(ap['FRT']['Price']) * float(ap['FRT']['OShares']) / 1e9 * FRT_PCT

L = C.liquidity(TK, free_float=0.80, ff_src='(uoc luong) 1 - TGB 6,89% - SCIC 5,67% - PYN 3,67% - BQN 1,76% - TTTT 1,48% ~ 80% [BCTN25]; so huu NN 28,6%/49%')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']


def dcf(base, g1, conv, gT, ke, n=5):
    pv, e = 0.0, base
    for t in range(1, n + 1):
        e *= 1 + g1; pv += e * conv / (1 + ke) ** t
    tv = e * (1 + gT) * conv / (ke - gT); pvtv = tv / (1 + ke) ** n
    return pv + pvtv, pvtv / (pv + pvtv)


SC = {  # g1 5 nam, conv, gT, chiet khau FTEL, w  - giu nguyen ban 01/11 (da qua skeptic), BO Ke theo kich ban
 'XAU':   (0.03, 0.40, 0.030, 0.30, 0.35),   # co so du lieu: conv 9T/26 -0,12, FY25 0,60, FY24 1,07 [dd_FPT REPORT 4c]
 'CO_SO': (0.09, 0.75, 0.040, 0.15, 0.45),
 'TOT':   (0.14, 0.85, 0.040, 0.00, 0.20),
}


def fv(n, ke, dconv=0.0, dg=0.0):
    g1, cv, gT, fd, _ = SC[n]
    v, tvs = dcf(core_op, g1, max(cv + dconv, 0.10), gT + dg, ke)
    return (v + fox * (1 - fd) + frt * 0.8 + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU + NC) / SH * 1e3, tvs



# ======================= VONG 2 =======================
import r2common as R2C
FRT_AX = ((0.20, 0.25), (0.0, 0.50), (-0.20, 0.25))          # FRT quanh THI GIA 04/11 (base = thi gia, bo haircut 20% vong 1) [UL]
OTH_AX = ((-1300, 0.20), (0, 0.30), (1100, 0.30), (2600, 0.20))  # d/cp: lien ket khac + TPB/FTS lech so sach [SKEPTIC_20261101 T6a/T6b] [UL]


def fv2(r, scen, dconv, dg, frt_d, oth):
    g1, cv, gT, fd, _ = SC[scen]
    v, _ = dcf(core_op, g1, max(cv + dconv, 0.10), gT + dg, r)
    return (v + fox * (1 - fd) + frt * (1 + frt_d) + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU + NC) / SH * 1e3 + oth


DCV = (-0.20, -0.10, 0.0, 0.10, 0.20); DG = (-0.01, 0.0, 0.01)
axes = [('scen', [(n, SC[n][4]) for n in SC]), ('dconv', [(x, 1 / 5) for x in DCV]), ('dg', [(x, 1 / 3) for x in DG]),
        ('frt_d', list(FRT_AX)), ('oth', list(OTH_AX))]
central_kw = dict(scen='CO_SO', dconv=0.0, dg=0.0, frt_d=0.0, oth=0)
RES = R2C.finalize(TK, HERE, PX, PXD, R, axes, fv2, central_kw, ['frt_d', 'oth'])
m = RES['main']
print(f"== FPT VONG 2 | gia {PX:,.0f} ({PXD}, con quyen co tuc 1.000d chot 30/11) | r {R:.2%}")
print(f"FRT 46,54% thi gia 04/11 {frt:,.0f} ty ({frt/SH*1e3:,.0f} d/cp); vong 1 tru 20% = {-0.2*frt/SH*1e3:,.0f} d/cp -> vong 2 base = thi gia")
print("Luoi chinh (sau CK 5 ty):", R2C.fmt(m))
print("Truoc CK:", R2C.fmt(RES['pre']))
for k, s in RES['parallel'].items(): print(f"Song song {k}:", R2C.fmt(s))
r1grid = R2C.outcomes([a for a in axes if a[0] in ('scen', 'dconv', 'dg')] + [('frt_d', [(-0.20, 1.0)]), ('oth', [(0, 1.0)])], lambda **kw: fv2(R, **kw))
print("Doi chieu: luoi vong 1 (FRT -20%, khong truc oth) tinh lai bang wpct:", R2C.fmt(R2C.stats(r1grid, PX, RES['d_ref'])))
print(f"Gia tri tai tham so trung tam (CO_SO, dconv 0, dg 0, FRT thi gia, lien ket khac theo so) sau CK: {RES['central']:,.0f}")
print(f"Nhom kich ban quanh P10: {RES['drivers']['p10_scen_mix_pm5pct']} | quanh P90: {RES['drivers']['p90_scen_mix_pm5pct']}")
Lq = RES['liq']
print(f"Thanh khoan: ADV250 {Lq['adv250']['adv_med']/1e9:,.1f} ty, ADV60 {Lq['adv60']['adv_med']/1e9:,.1f} ty | CK 5 ty {Lq['d_ref']:.3%} (ADV60 {Lq['d_ref_adv60']:.3%}) | sleeve 10tr {Lq['d_sleeve']['10tr']:.4%} 40tr {Lq['d_sleeve']['40tr']:.4%}")
print("  " + Lq['calib_note'])
print(f"NHAN: {RES['label']} (vung P10-P90 muc ket cuc, CK o co 5 ty)")
# Gordon (doi chieu, kich ban co so): A = loi van hanh (khong lai tien gui) + tien rong + co phan; B = loi + lai tien gui rong sau thue, KHONG cong tien rong
nonop = fox * (1 - SC['CO_SO'][3]) + frt + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU
ni_int = NET_INT9 * 4 / 3 * 0.85
gord = {}
for g in (0.04, 0.05):
    cv = SC['CO_SO'][1]
    gord[f'A_khong_lai_tg_g{g}'] = (core_op * cv * (1 + g) / (R - g) + nonop + NC) / SH * 1e3
    gord[f'B_co_lai_tg_g{g}'] = ((core_op + ni_int) * cv * (1 + g) / (R - g) + nonop) / SH * 1e3
print("Gordon (conv co so 0,75; truoc CK): " + ' | '.join(f"{k} {v:,.0f}" for k, v in gord.items()))
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'fpt_redo.py'), os.path.join(HERE, 'assoc_px_20261104.csv'), os.path.join(C.HERE, 'common.py'),
                 os.path.join(C.HERE, 'r2common.py'), os.path.join(C.HERE, 'bq_px_liq_20261104.csv'), os.path.join(C.HERE, '..', '_shared', 'wpct.py'),
                 os.path.join(C.WC, 'deposit_rate_vn.py'), os.path.join(C.WC, 'cctg_rate_vn.py'), os.path.join(C.WC, 'data/deposit_rate_vn_events.csv'),
                 os.path.join(C.WC, 'data/cctg_rate_vn_events.csv'), os.path.join(C.WC, 'mike/kb/dd_price_zones.json')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
extra = dict(
  axes_included=['kich ban XAU/CO_SO/TOT (0,35/0,45/0,20; FTEL CK 30/15/0% trong kich ban)', 'dich conv -0,20..+0,20 (5 diem deu, san 0,10)', 'dich g -1/0/+1pp (deu)',
                 'FRT quanh thi gia +20/0/-20% (0,25/0,50/0,25) [UL]', 'lien ket khac + TPB/FTS lech so: -1.300/0/+1.100/+2.600 d/cp (0,2/0,3/0,3/0,2) [UL; SKEPTIC T6a/T6b]'],
  axes_excluded=[dict(axis='r (Ke)', reason='luat 03/11 neo lai huy dong; ban song song co_truc_r_pm1pp'),
                 dict(axis='tien khach ung truoc 2.370 ty (hoc phi + nguoi mua tra truoc)', reason='float theo mua (vong 1 §3); khong tru; neu tru: -1.257 d/cp (doi chieu)')],
  base_adjustments=[dict(item='FTEL (FOX) chiet khau theo kich ban 30/15/0%', effect_dong_per_share=round(-0.15 * fox / SH * 1e3), basis='free float FOX <= ~4,2%, Nha nuoc (Bo Cong an) ~50,16% kiem soat; CV 1906 18/03/2026 thoi hop nhat',
                         source='dd_FPT_20261101/REPORT.md §6; Q3HN p14'),
                    dict(item='FRT', effect_dong_per_share=0, basis='thi gia 04/11 x 46,54% (vong 1 tru 20% khong co co so -> bo khoi base, chuyen thanh truc)', source='BQ tav2_bq.ticker 04/11 (assoc_px_20261104.csv)'),
                    dict(item='XDCB do dang khuon vien GD 760 ty', effect_dong_per_share=0, basis='gia so = NPV 0', source='Q3HN p37'),
                    dict(item='Lien ket khac 1.500 ty', effect_dong_per_share=0, basis='theo so (uoc luong, BCTC khong tach); lech so nam o truc oth', source='uoc luong')],
  center_vs_p50_note='xem REPORT_r2 §2', gordon_crosscheck={k: round(v) for k, v in gord.items()}, lock_md5=LOCK,
  warnings_r2_added=["Vay ngoai te 30/09 trung tung dong voi 30/06 (JPY, EUR) - nghi chua danh gia lai ty gia [SKEPTIC T; GAPS G15]",
                     "Giao dich ben lien quan 9T: mua Synnex 663 ty (cung ky 308), ban FRT 386, FTEL 115/211 [Q3HN p47-48]",
                     "Bao cao quan tri 6T/2026 chua doc", "ETR 11,1% -> 15,2% chua ro nguyen nhan (thue toi thieu toan cau hay het uu dai)",
                     "Thanh tra So TT&TT Binh Duong ve chi nhanh FTEL (2022-24) - khong trong yeu"],
  fear_buy_eligible_2_5=False)
S = R2C.write_summary(os.path.join(HERE, '..', 'SUMMARY.json'), dict(price=PX), RES, extra)
S['center_vs_p50_note'] = (f"tam = ky vong luoi {m['center']:,.0f}; P50 {m['p50']:,.0f}; gia tri tai tham so trung tam {RES['central']:,.0f}")
json.dump(S, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
json.dump(dict(main=m, pre=RES['pre'], parallel=RES['parallel'], central=RES['central'], drivers=RES['drivers'], liq=RES['liq'], gordon=gord, lock=LOCK),
          open(os.path.join(HERE, 'fpt_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json (r2) written')
