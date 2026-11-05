"""DD REDO MBB 05/11/2026 (job Taylor_20261105_014125). Chay: $DNA_PYEXE -I mbb_redo.py > mbb_redo_out.txt
Khung skill due-diligence hien hanh: r = Ke noi dia 13,5% @ lai huy dong 12T hieu dung 03/11 (deposit_rate_vn), beta=1;
CK thanh khoan theo _common_014125/common.py (luat can bac hai, Q=5 ty); MBV (du an/cam ket von moi) base = gia so sach (NPV 0).
DAU VAO BCTC: doc tu BCTC goc Q3/2026 (dd_MBB_20261031/src, so doc anh: dd_MBB_20261031/calc/notes_read.md) - chep nguyen gia tri, ghi trang.
Gia dinh tuong lai = (uoc luong)."""
import os, sys, json, csv, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
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


out = dict(ticker=TK, price=PX, price_date=PXD, r=R, anchor=A, bvps=bvps, pb=PX / bvps, pe_ttm=PX / (ttm / SH * 1e3), days_to_ye=int(DAYS))
print(f"== MBB redo | gia {PX:,.0f} ({PXD}) | BVPS 30/09 {bvps:,.0f} | P/B {PX/bvps:.2f}x | P/E TTM {out['pe_ttm']:.2f}x")
print(f"r = {R:.2%} (neo 13,5% @ {A['r_anchor']['rate']:.2%} {A['r_anchor']['source']}; asof {A['dep_asof']['rate']:.2%} {A['dep_asof']['source']})")
sc_val = {}
for n in SC:
    v, tvs = value(n, R); sc_val[n] = v
    print(f"  {n} w={SC[n][0]}: LNTT 2026 {base[n]['lt26']:,.0f} ({base[n]['lt26']/KH26:.0%} KH) | VCSH me cuoi 2026 {base[n]['bv26']:,.0f} | RI {v:,.0f} d/cp (P/B ngu y {v/bvps:.2f}x; TV {tvs:.0%})")
center_pre = sum(SC[n][0] * sc_val[n] for n in SC)
out['scen'] = sc_val; out['center_pre'] = center_pre
for lab, ww in (('w_xau_045', (0.45, 0.35, 0.20)), ('w_tot_035', (0.25, 0.40, 0.35))):
    out[lab] = sum(x * sc_val[n] for x, n in zip(ww, SC)); print(f"  do nhay trong so {lab} {ww}: {out[lab]:,.0f}")
print(f"  KY VONG (0,35/0,45/0,20) truoc CK thanh khoan: {center_pre:,.0f}")

# ---- do nhay r theo lai huy dong (+-50/100bp), beta 0,5/1,0 ----
sens = {}
for beta in (0.5, 1.0):
    for bp in (-100, -50, 50, 100):
        ke = C.r_now(beta=beta, shift=bp / 1e4)
        v = sum(SC[n][0] * value(n, ke)[0] for n in SC)
        sens[f'b{beta}_{bp:+d}bp'] = dict(r=ke, v=v, dv=v - center_pre, pct=v / center_pre - 1)
out['sens_r'] = sens
print("Do nhay (lai huy dong doi, r = 13,5% + beta*d):")
for k, s in sens.items(): print(f"  {k}: r {s['r']:.2%} -> {s['v']:,.0f} ({s['dv']:+,.0f} d/cp; {s['pct']:+.1%})")

# ---- LUOI: kich ban (w) x dich ROE 2027+ (5 diem) x dich g_T (3 diem) ----
DROE = (-0.03, -0.015, 0.0, 0.015, 0.03); DG = (-0.01, 0.0, 0.01)
cells = []
for n in SC:
    for dr in DROE:
        for dg in DG:
            cells.append((n, dr, dg, value(n, R, dr, dg)[0], SC[n][0] / (len(DROE) * len(DG))))
vals = [c[3] for c in cells]; wts = [c[4] for c in cells]
with open(os.path.join(HERE, 'grid_mbb.csv'), 'w', newline='') as fh:
    wr = csv.writer(fh); wr.writerow(['scen', 'droe', 'dg', 'value_pre', 'weight']); wr.writerows(cells)
grid_desc = ("Luoi co trong so n=45: kich ban XAU/CO SO/TOT (w 0,35/0,45/0,20) x dich ROE 2027-29+terminal -3/-1,5/0/+1,5/+3 pp "
             "x dich g terminal -1/0/+1 pp (deu); r co dinh 13,50%; RI 3 giai doan, BV0 = VCSH me cuoi 2026 theo kich ban; terminal: ROE_T < r => RI khong tang (von moi NPV 0). "
             "Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
S = C.summarize(TK, PXD, PX, center_pre, vals, wts, L, grid_desc)
out['summary_core'] = S; out['liq'] = L
print(f"Luoi n={len(cells)}: truoc CK P10 {S['p10_pre']:,} P50 {S['p50_pre']:,} P90 {S['p90_pre']:,}")
print(f"Thanh khoan: ADV trung vi 250 phien {L['adv_med']/1e9:,.1f} ty | sigma ngay {L['sigma_d']:.2%} | CK @5 ty Y1 {L['d_label']:.3%} "
      f"(1 ty {L['pos']['1']['disc']['Y1.0']:.3%}; 10 ty {L['pos']['10']['disc']['Y1.0']:.3%}) | so phien thoat 5 ty @10/20% {L['pos']['5']['days']['p10']:.2f}/{L['pos']['5']['days']['p20']:.2f} | Amihud {L['amihud_med_per_bn']:.2e}/ty")
print(f"SAU CK: tam {S['center_post_liq']:,} | P10 {S['p10_post']:,} P25 {S['p25_post']:,} P50 {S['p50_post']:,} P75 {S['p75_post']:,} P90 {S['p90_post']:,}")
print(f"Gia {PX:,.0f}: vs tam {S['px_vs_center_post']:+.1%} | vs P10 {S['px_vs_p10_post']:+.1%} | vs P90 {S['px_vs_p90_post']:+.1%} | NHAN: {S['label']}")

# ---- MBV: base = so sach (NPV 0). Do nhay (khong vao base) ----
mbv = {}
for lab, x in (('gop 3.500 mat trang', 3500), ('gop 5.000 mat trang', 5000), ('phai thu ban no 11.248 mat 30%', 11248 * 0.3), ('bu lo luy ke 2024 15.688 (can tren tho)', 15688)):
    v = sum(SC[n][0] * value(n, R, mbv=x)[0] for n in SC)
    mbv[lab] = dict(x=x, v=v, dv=v - center_pre)
    print(f"  MBV do nhay - {lab}: ky vong {v:,.0f} ({v-center_pre:+,.0f} d/cp)")
out['mbv_sens'] = mbv

# ---- doi chieu ban cu ----
import json as J
es = [e for e in J.load(open(C.WC + '/mike/kb/dd_price_zones.json'))['entries'] if e.get('ticker') == TK]; e = es[-1]
out['zone_old'] = dict(low=e['zone_low'], center=e['center'], high=e['zone_high'], dd_date=e['dd_date'])
v134 = sum(SC[n][0] * value(n, 0.134)[0] for n in SC)
out['bridge'] = dict(old_center_blend=e['center'], ri_at_134_new_dates=v134, ri_at_135=center_pre)
print(f"Cau noi: tam cu (blend RI/comps/PB) {e['center']:,} -> RI thuan @13,4% (ngay 04/11) {v134:,.0f} -> @13,5% {center_pre:,.0f} -> sau CK {S['center_post_liq']:,}; lech tam {S['center_post_liq']/e['center']-1:+.1%}")
# cross-check (khong vao tam): P/B ngu y tai cac muc
out['implied_pb_center'] = S['center_post_liq'] / bvps
json.dump(out, open(os.path.join(HERE, 'mbb_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)

# ---- SUMMARY.json (moi so lay tu bien o tren) ----
summ = dict(ticker=TK, asof_price_date=PXD, price=PX, r=R, r_anchor=dict(rate=A['r_anchor']['rate'], date=A['r_anchor']['date'], source=A['r_anchor']['source'],
            asof_rate=A['dep_asof']['rate'], rule='r = 13,5% + beta x (dep - dep_neo), beta = 1 (gia dinh)'),
            center_pre_liq=S['center_pre_liq'], center_post_liq=S['center_post_liq'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
            p25_post=S['p25_post'], p75_post=S['p75_post'], p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], liq_disc_5ty=S['liq_disc_5ty'],
            px_vs_center_post=S['px_vs_center_post'], px_vs_p10_post=S['px_vs_p10_post'], px_vs_p90_post=S['px_vs_p90_post'],
            grid_desc=grid_desc, grid_n=S['grid_n'], label=S['label'], zone_old=out['zone_old'], center_change_vs_old=S['center_post_liq'] / out['zone_old']['center'] - 1,
            sens_r={k: dict(r=v['r'], value=round(v['v']), dv=round(v['dv']), pct=v['pct']) for k, v in sens.items()},
            change_reason=("Tam cu 22.000 = blend 0,5 RI @Ke 13,4% + 0,25 hoi quy comps + 0,25 P/B lich su; khung moi: tam = ky vong RI thuan @ r 13,5% (comps chi la doi chieu). "
                           f"Kich ban/gia dinh giu nguyen ban 31/10 (khong co BCTC moi sau Q3). Lech {S['center_post_liq']/out['zone_old']['center']-1:+.1%} chu yeu do bo 2 chan comps/P/B lich su (thap hon RI), r 13,4->13,5% chi {center_pre-v134:+,.0f} d/cp. "
                           f"Vung cu {out['zone_old']['low']:,}-{out['zone_old']['high']:,} la tham chieu tu chon; moi = P10-P90 luoi n={S['grid_n']} ({S['p10_post']:,}-{S['p90_post']:,}) rong hon vi luoi gom truc dich ROE +-3pp x g +-1pp."),
            warnings=[f"MBV (OceanBank cu) ngoai bang: khong hop nhat, QD gop 3.500 ty 01/10/2026; base = so sach (NPV 0); do nhay {mbv['gop 3.500 mat trang']['dv']:+,.0f} (gop 3.500 mat trang) den {mbv['bu lo luy ke 2024 15.688 (can tren tho)']['dv']:+,.0f} d/cp (bu lo luy ke 2024)",
                      "Chat luong tai san Q3 xau nhanh: nhom 2 HN +42% QoQ, me +67%; bao phu 93,6% -> 84,7% (WARNING phan tich, khong phai phap ly)",
                      "Phap ly/thanh tra 2025-26: khong tim thay (tim khong thay != khong co)"],
            open_issues=["CAR/CET1 30/09/2026 chua co so goc", "Nhom 2 Q3 cua nganh chua co de so sanh", "CASA chuan MB Q3 chua kiem",
                         "Khong quet tin moi 01-04/11/2026", "Ty le free float 60% la uoc luong tu so huu 2024-25 thu cap"])
json.dump(summ, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print("SUMMARY.json written")
