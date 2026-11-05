"""DD REDO HHS 05/11/2026 (job Taylor_20261105_014125). Chay: $DNA_PYEXE -I hhs_redo.py > hhs_redo_out.txt
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


out = dict(ticker=TK, price=PX, price_date=PXD, r=R, anchor=A, crv_fv=CRV_FV, crv_cost=CRV_COST, step=STEP_AT, other=OTHER)
print(f"== HHS redo | gia {PX:,.0f} ({PXD}) | r {R:.2%} (neo 13,5% @ {A['r_anchor']['rate']:.2%} {A['r_anchor']['source']})")
print(f"CRV GTHL {CRV_FV:,.0f} - thang du PPA sau thue {STEP_AT:,.0f} = CRV gia goc {CRV_COST:,.0f}; phan khac {OTHER:,.0f}; I.14 gia so {NEW_I14:,.0f} (thang du 0)")
sv = {k: val(k, R) for k in SC}
for k, s in SC.items(): print(f"  {k} p={s['p']}: bien backlog {s['m']:.1%}, thang du HTK cu {s['s']:.0%}, o to {s['np']}x{s['pe']}, CK holding {s['hd']:.0%} -> {sv[k]:,.0f}")
center_pre = sum(SC[k]['p'] * sv[k] for k in SC); out['scen'] = sv; out['center_pre'] = center_pre
print(f"  KY VONG truoc CK thanh khoan: {center_pre:,.0f}")
gov = {f'gov_{int(g*100)}': sum(SC[k]['p'] * val(k, R, gov=g) for k in SC) for g in (0.05, 0.10, 0.15)}
out['sens_gov'] = gov
print("  Do nhay CK quan tri (WARNING, KHONG vao base): " + ' | '.join(f"{k} {v:,.0f} ({v-center_pre:+,.0f})" for k, v in gov.items()))
i14 = {f'i14_s{int(x*100)}': sum(SC[k]['p'] * val(k, R, s_new=x) for k in SC) for x in (-0.15, 0.40)}
out['sens_i14'] = i14
print("  Do nhay I.14 (base NPV 0): " + ' | '.join(f"{k} {v:,.0f} ({v-center_pre:+,.0f})" for k, v in i14.items()))
bds = (2459.74 - 1438.45) * 0.8 * HHS * 0.75 / SH * 1e3
out['bdsdt_upside'] = bds
print(f"  Thang du BDSDT CRV (khong vao tam, can duoi, CK holding co so): +{bds:,.0f} d/cp")

sens = {}
for beta in (0.5, 1.0):
    for bp in (-100, -50, 50, 100):
        ke = C.r_now(beta=beta, shift=bp / 1e4); v = sum(SC[k]['p'] * val(k, ke) for k in SC)
        sens[f'b{beta}_{bp:+d}bp'] = dict(r=ke, v=v, dv=v - center_pre, pct=v / center_pre - 1)
out['sens_r'] = sens
print("Do nhay r theo lai huy dong:")
for k, s in sens.items(): print(f"  {k}: r {s['r']:.2%} -> {s['v']:,.0f} ({s['dv']:+,.0f}; {s['pct']:+.1%})")

DS = (-0.15, -0.075, 0.0, 0.075, 0.15); DHD = (-0.05, 0.0, 0.05)
cells = [(k, ds, dh, val(k, R, ds, dh), SC[k]['p'] / (len(DS) * len(DHD))) for k in SC for ds in DS for dh in DHD]
with open(os.path.join(HERE, 'grid_hhs.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['scen', 'd_surplus', 'd_holding_disc', 'value_pre', 'weight']); w.writerows(cells)
grid_desc = ("Luoi co trong so n=45: kich ban TIEU CUC/CO SO/TICH CUC (w 0,30/0,50/0,20) x dich thang du HTK CRV cu -15/-7,5/0/+7,5/+15 pp "
             "x dich CK holding -5/0/+5 pp (deu); r co dinh 13,50%; NAV: CRV gia goc + backlog NC-II x PV1 + thang du HTK cu x PV4 (I.14 gia so, NPV 0); "
             "khong CK quan tri (WARNING). Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
S = C.summarize(TK, PXD, PX, center_pre, [c[3] for c in cells], [c[4] for c in cells], L, grid_desc)
print(f"Luoi n={S['grid_n']}: truoc CK P10 {S['p10_pre']:,} P50 {S['p50_pre']:,} P90 {S['p90_pre']:,}")
print(f"Thanh khoan: ADV trung vi 250 phien {L['adv_med']/1e9:,.1f} ty | sigma {L['sigma_d']:.2%} | CK @5 ty {L['d_label']:.2%} (Y0,5 {L['pos']['5']['disc']['Y0.5']:.2%}; Y1,5 {L['pos']['5']['disc']['Y1.5']:.2%}; 1 ty {L['pos']['1']['disc']['Y1.0']:.2%}; 10 ty {L['pos']['10']['disc']['Y1.0']:.2%}) | phien thoat 5 ty @10/15/20% {L['pos']['5']['days']['p10']:.1f}/{L['pos']['5']['days']['p15']:.1f}/{L['pos']['5']['days']['p20']:.1f} | Amihud {L['amihud_med_per_bn']:.2e} | free float {L['free_float']:.1%}")
print(f"SAU CK: tam {S['center_post_liq']:,} | P10 {S['p10_post']:,} P25 {S['p25_post']:,} P50 {S['p50_post']:,} P75 {S['p75_post']:,} P90 {S['p90_post']:,}")
print(f"Gia {PX:,.0f}: vs tam {S['px_vs_center_post']:+.1%} | vs P10 {S['px_vs_p10_post']:+.1%} | vs P90 {S['px_vs_p90_post']:+.1%} | NHAN {S['label']}")

es = [e for e in json.load(open(C.WC + '/mike/kb/dd_price_zones.json'))['entries'] if e.get('ticker') == TK]; e = es[-1]
zo = dict(low=e['zone_low'], center=e['center'], high=e['zone_high'], dd_date=e['dd_date'], center_kind=e.get('center_kind'))
# cau noi tu ban cu (Ke 12,85%, I.14 co thang du, CK quan tri g 15/10/5%)
G_OLD = {'TIEU_CUC': 0.15, 'CO_SO': 0.10, 'TICH_CUC': 0.05}
def old_like(ke, i14_surplus=True, gov=True):
    t = 0
    for k, s in SC.items():
        c = crv(s['m'], s['s'], ke, s['s'] if i14_surplus else 0.0)
        t += s['p'] * ((HHS * c) * (1 - s['hd']) + OTHER + s['np'] * s['pe']) * (1 - (G_OLD[k] if gov else 0)) / SH * 1e3
    return t
b0 = old_like(0.1285); b1 = old_like(R); b2 = old_like(R, i14_surplus=False)
print(f"Cau noi: cu tai lap {b0:,.0f} (ban cu ghi {zo['center']:,}) -> r 13,5% {b1:,.0f} ({b1-b0:+,.0f}) -> I.14 NPV0 {b2:,.0f} ({b2-b1:+,.0f}) -> bo CK quan tri {center_pre:,.0f} ({center_pre-b2:+,.0f}) -> sau CK thanh khoan {S['center_post_liq']:,} ({S['center_post_liq']-center_pre:+,.0f}); lech {S['center_post_liq']/zo['center']-1:+.1%}")
out.update(summary_core=S, liq=L, zone_old=zo, bridge=dict(old_repro=b0, r135=b1, i14_npv0=b2, no_gov=center_pre))
json.dump(out, open(os.path.join(HERE, 'hhs_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)

summ = dict(ticker=TK, asof_price_date=PXD, price=PX, r=R, r_anchor=dict(rate=A['r_anchor']['rate'], date=A['r_anchor']['date'], source=A['r_anchor']['source'],
            asof_rate=A['dep_asof']['rate'], rule='r = 13,5% + beta x (dep - dep_neo), beta = 1 (gia dinh)'),
            center_pre_liq=S['center_pre_liq'], center_post_liq=S['center_post_liq'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
            p25_post=S['p25_post'], p75_post=S['p75_post'], p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], liq_disc_5ty=S['liq_disc_5ty'],
            px_vs_center_post=S['px_vs_center_post'], px_vs_p10_post=S['px_vs_p10_post'], px_vs_p90_post=S['px_vs_p90_post'],
            grid_desc=grid_desc, grid_n=S['grid_n'], label=S['label'], zone_old=zo, center_change_vs_old=S['center_post_liq'] / zo['center'] - 1,
            sens_r={k: dict(r=v['r'], value=round(v['v']), dv=round(v['dv']), pct=v['pct']) for k, v in sens.items()},
            change_reason=(f"Bo CK quan tri 15/10/5% khoi base (phap ly/quan tri chi WARNING) {center_pre-b2:+,.0f}; I.14 theo gia so NPV 0 {b2-b1:+,.0f}; "
                           f"r 12,85->13,5% {b1-b0:+,.0f}; CK thanh khoan {S['center_post_liq']-center_pre:+,.0f} (ADV {L['adv_med']/1e9:,.1f} ty). Kich ban giu ban 01/11 (khong co BCTC moi)."),
            warnings=["Quan tri (WARNING trung binh): thuong vu HHS Capital nguoi ban khong neu ten, khong dinh gia doc lap, TCH duoc bieu quyet; ky quy 28,4 ty cho ca nhan",
                      "KL 08/KL-TTTP 26/02/2026 (Thanh tra HP) NOXH Pruksa (HHS 90,17%): ra soat dieu chinh gia ban; 2 ket luan thanh tra dang mo nhom CRV/Pruksa",
                      "TCH (me) co 2 QD xu phat that (UBCKNN 12/2024; thue 20,21 ty 04/2026); HHS chua thay QD 2023-26",
                      "Q3/2026 chua soat xet; soat xet 6T ha LNST me -34% so ban tu lap",
                      f"CK quan tri neu ap 10%: {gov['gov_10']-center_pre:+,.0f} d/cp (chi do nhay)"],
            open_issues=["I.14 1.329 ty gia dinh nam trong HTK CRV con lai 7.338,8 (tham so DD TCH)", "CK holding 25% co so la uoc luong (co so: CRV chua tra co tuc tien ve HHS 9T/26)",
                         "Danh tinh nguoi ban HHS Capital (G4/G11)", "Thang du BDSDT CRV chua vao tam", "Chua quet tin moi 01-04/11/2026"])
json.dump(summ, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json written')
