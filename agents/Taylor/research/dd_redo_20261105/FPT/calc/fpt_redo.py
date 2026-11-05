"""DD REDO FPT 05/11/2026 (job Taylor_20261105_014125). Chay: $DNA_PYEXE -I fpt_redo.py > fpt_redo_out.txt
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


out = dict(ticker=TK, price=PX, price_date=PXD, r=R, anchor=A, nc=NC, nc_ps=NC / SH * 1e3, fox_stake=fox, frt_stake=frt, core_op=core_op,
           implied_pe_core=(PX * SH / 1e3 - fox - frt - OTHER_ASSOC_BOOK - INV_OTHER - CIP_EDU - NC) / core_op)
print(f"== FPT redo | gia {PX:,.0f} ({PXD}, con quyen co tuc 1.000d chot 30/11) | r {R:.2%} (neo 13,5% @ {A['r_anchor']['rate']:.2%} {A['r_anchor']['source']})")
print(f"Tien rong 30/09 {NC:,.0f} ty ({NC/SH*1e3:,.0f} d/cp) | FTEL {FTEL_PCT:.2%} thi gia 04/11 {fox:,.0f} ty ({fox/SH*1e3:,.0f} d/cp) | FRT {frt:,.0f} ty ({frt/SH*1e3:,.0f} d/cp)")
print(f"XDCB do dang GD (NPV 0, gia so) {CIP_EDU:,.0f} ty ({CIP_EDU/SH*1e3:,.0f} d/cp) | LN loi van hanh TTM {core_op:,.0f} ty (uoc luong) | PE loi ngam dinh {out['implied_pe_core']:.1f}x")
sv = {}
for n in SC:
    v, tvs = fv(n, R); sv[n] = v
    print(f"  {n} w={SC[n][4]} g1 {SC[n][0]:.0%} conv {SC[n][1]:.2f} gT {SC[n][2]:.1%} FTELck {SC[n][3]:.0%}: FV {v:,.0f} (TV {tvs:.0%})")
center_pre = sum(SC[n][4] * sv[n] for n in SC); out['scen'] = sv; out['center_pre'] = center_pre
out['non_r_ps_base'] = (fox * (1 - SC['CO_SO'][3]) + frt * 0.8 + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU + NC) / SH * 1e3
print(f"  phan KHONG phu thuoc r (kich ban co so): {out['non_r_ps_base']:,.0f} d/cp")
print(f"  KY VONG truoc CK: {center_pre:,.0f}")
for lab, ww in (('w_xau_045', (0.45, 0.40, 0.15)), ('w_tot_030', (0.25, 0.45, 0.30))):
    out[lab] = sum(x * sv[n] for x, n in zip(ww, SC)); print(f"  do nhay trong so {lab} {ww}: {out[lab]:,.0f}")

sens = {}
for beta in (0.5, 1.0):
    for bp in (-100, -50, 50, 100):
        ke = C.r_now(beta=beta, shift=bp / 1e4); v = sum(SC[n][4] * fv(n, ke)[0] for n in SC)
        sens[f'b{beta}_{bp:+d}bp'] = dict(r=ke, v=v, dv=v - center_pre, pct=v / center_pre - 1)
out['sens_r'] = sens
print("Do nhay r theo lai huy dong:")
for k, s in sens.items(): print(f"  {k}: r {s['r']:.2%} -> {s['v']:,.0f} ({s['dv']:+,.0f}; {s['pct']:+.1%})")

DCV = (-0.20, -0.10, 0.0, 0.10, 0.20); DG = (-0.01, 0.0, 0.01)
cells = [(n, dc, dg, fv(n, R, dc, dg)[0], SC[n][4] / (len(DCV) * len(DG))) for n in SC for dc in DCV for dg in DG]
with open(os.path.join(HERE, 'grid_fpt.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['scen', 'dconv', 'dg', 'value_pre', 'weight']); w.writerows(cells)
grid_desc = ("Luoi co trong so n=45: kich ban XAU/CO SO/TOT (w 0,35/0,45/0,20) x dich ty le chuyen lai thanh tien conv -0,20/-0,10/0/+0,10/+0,20 (san 0,10) "
             "x dich g dai han -1/0/+1 pp (deu); r co dinh 13,50%; DCF FCFE loi + FTEL/FRT thi gia 04/11 co CK + lien ket khac so + tien rong + XDCB do dang (NPV 0). "
             "Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
S = C.summarize(TK, PXD, PX, center_pre, [c[3] for c in cells], [c[4] for c in cells], L, grid_desc)
print(f"Luoi n={S['grid_n']}: truoc CK P10 {S['p10_pre']:,} P50 {S['p50_pre']:,} P90 {S['p90_pre']:,}")
print(f"Thanh khoan: ADV trung vi 250 phien {L['adv_med']/1e9:,.1f} ty | sigma {L['sigma_d']:.2%} | CK @5 ty {L['d_label']:.3%} (1 ty {L['pos']['1']['disc']['Y1.0']:.3%}; 10 ty {L['pos']['10']['disc']['Y1.0']:.3%}) | phien thoat 5 ty @10/20% {L['pos']['5']['days']['p10']:.2f}/{L['pos']['5']['days']['p20']:.2f} | Amihud {L['amihud_med_per_bn']:.2e}")
print(f"SAU CK: tam {S['center_post_liq']:,} | P10 {S['p10_post']:,} P25 {S['p25_post']:,} P50 {S['p50_post']:,} P75 {S['p75_post']:,} P90 {S['p90_post']:,}")
print(f"Gia {PX:,.0f}: vs tam {S['px_vs_center_post']:+.1%} | vs P10 {S['px_vs_p10_post']:+.1%} | vs P90 {S['px_vs_p90_post']:+.1%} | NHAN {S['label']}")

es = [e for e in json.load(open(C.WC + '/mike/kb/dd_price_zones.json'))['entries'] if e.get('ticker') == TK]; e = es[-1]
zo = dict(low=e['zone_low'], center=e['center'], high=e['zone_high'], dd_date=e['dd_date'], center_kind=e.get('center_kind'))
# cau noi: ban cu Ke theo kich ban, FOX/FRT 30/10, khong XDCB
old_ke = {'XAU': 0.134, 'CO_SO': 0.1285, 'TOT': 0.123}
b1 = sum(SC[n][4] * fv(n, old_ke[n])[0] for n in SC)
b0 = b1 - CIP_EDU / SH * 1e3
print(f"Cau noi: tam cu {zo['center']:,} (Ke kich ban, FOX/FRT 30/10) -> gia LK 04/11 + XDCB NPV0, Ke cu {b1:,.0f} (trong do XDCB {CIP_EDU/SH*1e3:+,.0f}; gia LK {b0-zo['center']:+,.0f}) -> r 13,5% {center_pre:,.0f} ({center_pre-b1:+,.0f}) -> sau CK {S['center_post_liq']:,}; lech {S['center_post_liq']/zo['center']-1:+.1%}")
out.update(summary_core=S, liq=L, zone_old=zo, bridge=dict(old=zo['center'], assoc_px_cip=b1, r135=center_pre))
json.dump(out, open(os.path.join(HERE, 'fpt_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)

summ = dict(ticker=TK, asof_price_date=PXD, price=PX, r=R, r_anchor=dict(rate=A['r_anchor']['rate'], date=A['r_anchor']['date'], source=A['r_anchor']['source'],
            asof_rate=A['dep_asof']['rate'], rule='r = 13,5% + beta x (dep - dep_neo), beta = 1 (gia dinh)'),
            center_pre_liq=S['center_pre_liq'], center_post_liq=S['center_post_liq'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
            p25_post=S['p25_post'], p75_post=S['p75_post'], p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], liq_disc_5ty=S['liq_disc_5ty'],
            px_vs_center_post=S['px_vs_center_post'], px_vs_p10_post=S['px_vs_p10_post'], px_vs_p90_post=S['px_vs_p90_post'],
            grid_desc=grid_desc, grid_n=S['grid_n'], label=S['label'], zone_old=zo, center_change_vs_old=S['center_post_liq'] / zo['center'] - 1,
            sens_r={k: dict(r=v['r'], value=round(v['v']), dv=round(v['dv']), pct=v['pct']) for k, v in sens.items()},
            change_reason=(f"r: Ke theo kich ban 13,4/12,85/12,3% -> MOT r 13,5% ({center_pre-b1:+,.0f} d/cp, chu yeu kich ban TOT mat Ke 12,3%); "
                           f"FOX/FRT theo thi gia 04/11 + XDCB do dang GD theo gia so (NPV 0) {b1-zo['center']:+,.0f}; kich ban/conv/g giu nguyen ban 01/11. "
                           f"Vung cu {zo['low']:,}-{zo['high']:,} = 1 truc g x Ke cua kich ban co so; moi = P10-P90 luoi n={S['grid_n']} ({S['p10_post']:,}-{S['p90_post']:,})."),
            warnings=["FTEL: Nha nuoc (Bo Cong an) kiem soat ~50,16%, FPT 45,66% theo von chu; free float FOX <= ~4,2%; CK FTEL 0/15/30% theo kich ban",
                      "Khoan 'chi phi phat trien khach hang' 618,8 ty chua thuyet minh (cau hoi IR)",
                      "Dong tien 9T/26 am (conv -0,12) - bien so quyet dinh la CFO Q4/26",
                      "Phat thue 0,244 ty da nop (khong trong yeu); PwC soat xet 6T chap nhan toan phan"],
            open_issues=["Lai lien ket khong tach theo cong ty; Q4/25 lai LK 600 ty la uoc luong", "conv 2021-2023 chua do cung dinh nghia",
                         "Gia tri lien ket khac (Synnex, FPT Online) theo so 1.500 ty (uoc luong)", "Chua quet tin moi 02-04/11/2026",
                         "XDCB do dang chi gom 4 khuon vien da liet ke (760 ty); co the trung lap mot phan voi g1"])
json.dump(summ, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json written')
