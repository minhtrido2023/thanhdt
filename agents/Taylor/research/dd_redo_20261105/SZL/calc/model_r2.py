"""SZL VONG 2 (job Taylor_20261105_020021) — ap STANDARD_r2.md. Chay: $DNA_PYEXE -B model_r2.py > model_r2_out.txt
So BCTC giu nguyen vong 1 (model.py; src/Q3_2026_hopnhat.pdf 30/09/2026, B01a-DN, doc tu anh img/p02-p08). Gia SZC/SZB + OShares: calc/bq_*.csv (BQ 04/11/2026).
Doi so vong 1:
 (1) XDCB do dang 407,0 (ma 252, chu yeu Long Phuoc) cong THEO GIA VON trong base. Vong 1 viet 'NPV 0' nhung KHONG cong tai san
     trong khi no vay tai tro du an da tru trong no rong => thuc chat NPV = -407 (vi pham dieu 3).
 (2) them truc thoi han dong tien loi: {den ~2053 (27 nam, uoc luong thoi han thue dat), vinh vien (gia han/tai cho thue)} — vong 1 dung
     Gordon vinh vien trong khi REPORT tu neu thoi han thue ~27 nam (truc chi lech xuong bi bo => dieu 2).
 (3) tam = ky vong luoi; (4) thanh khoan 250+60 + sleeve; (5) cross-check Gordon 2 bien the; (6) song song: bo XDCB, holdco 10/25%."""
import sys, os, csv, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_020021'))
import r2lib as R2
L = R2.L
SH = 48.198884
dep, dep_src = L.current_dep(); R = L.r_of(dep)
Q = R2.liq2('SZL'); PX = Q['price']; LD = Q['disc_ref']
CASH = 171.220813690; DIV_PAY = 70.360021125
LOAN_ST, LOAN_LT = 110.030903581, 196.337026604
UNEARNED = 42.901784203 + 719.254313326
CIP = 407.037010429; EQ = 784.151356245
DEPOSITS = 10.147281118 + 0.230000000 + 146.987107831   # TM17: nhan ky quy ky cuoc NH (doi tuong khac + BLQ) + DH — no that, vong 1 bo sot
LAND_RENT_ACCR = 44.265169191                       # TM16: trich bo sung chi phi thue dat KCN Long Thanh (khong doi tu dau nam)
INV_BOOK = {"SZC": 221.8, "SZB": 63.0, "An Binh": 24.5, "Binh Thuan": 80.0, "Dich vu": 8.75}
OWN = {"SZC": 0.1008, "SZB": 0.084}
NP_9M = 132.589359502
FIN_REV_9M, FIN_EXP_9M = 37.740263110, 4.326469728
PXF = os.path.join(HERE, 'bq_szc_szb_20261104.csv'); OSF = os.path.join(HERE, 'bq_oshares_szc_szb.csv')
px = {r['ticker']: float(r['Close']) for r in csv.DictReader(open(PXF))}
osh = {r['ticker']: float(r['OShares']) for r in csv.DictReader(open(OSF))}
mkt = {k: OWN[k] * osh[k] * px[k] / 1e9 for k in sorted(OWN)}
gain_tax = sum(max(mkt[k] - INV_BOOK[k], 0) for k in OWN) * 0.20
unlisted = sum(v for k, v in INV_BOOK.items() if k not in OWN)
NET_DEBT = LOAN_ST + LOAN_LT - CASH + DIV_PAY
OTHER_LIAB = DEPOSITS + LAND_RENT_ACCR
CORE_9M = NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80
N0 = CORE_9M * 4 / 3
YRS_LEFT = 27
print(f"N0 {N0:.1f}; no rong {NET_DEBT:.1f} ({NET_DEBT/SH*1000:,.0f} d/cp); niem yet thi gia {sum(mkt.values()):.1f} - thue lai von {gain_tax:.1f}; chua niem yet so {unlisted:.2f}; XDCB {CIP:.1f} ({CIP/SH*1000:,.0f} d/cp) — r2 CONG theo gia von")
print(f"No khac theo so: ky quy {DEPOSITS:.1f} + trich thue dat bo sung {LAND_RENT_ACCR:.1f} = {OTHER_LIAB:.1f} ({OTHER_LIAB/SH*1000:,.0f} d/cp) — r2 TRU")
print(f"r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({Q['price_date']})")


def val(n0=N0, g=0.03, r=R, nc=0.10, T=None, hold=0.0, cip=True, oth=True):
    cf = n0 * (1 - nc)
    core = cf / (r - g) if T is None else cf * (1 - ((1 + g) / (1 + r)) ** T) / (r - g)
    inv = (sum(mkt.values()) - gain_tax) * (1 - hold) + unlisted
    return (core + inv + (CIP if cip else 0.0) - (OTHER_LIAB if oth else 0.0) - NET_DEBT) / SH * 1000


NS = (N0 * 0.88, N0 * 0.94, N0, N0 * 1.06, N0 * 1.12); WN = (0.1, 0.2, 0.4, 0.2, 0.1)
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25); RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
NCS = (0.20, 0.10, 0.0); WNC = (0.25, 0.5, 0.25)
TS = (YRS_LEFT, None); WT = (0.75, 0.25)   # TM17: NQ DHDCD 76/2020 phan bo LN den 2053 => co so du lieu cho moc 2053; vinh vien = gia han [UL]


def grid(ts=(TS, WT), **kw):
    v, w = [], []
    for (n, wn), (g, wg), (rr, wr), (nc, wc), (T, wt) in itertools.product(zip(NS, WN), zip(GS, WG), zip(RS, WR), zip(NCS, WNC), zip(*ts)):
        v.append(val(n, g, rr, nc, T, **kw)); w.append(wn * wg * wr * wc * wt)
    return v, w


vals, ws = grid()
S = R2.stats(vals, ws, PX, LD); lab = R2.label(PX, S)
print("LUOI r2: " + R2.fmt(S, PX))
cp27, cpinf = val(T=YRS_LEFT), val()
print(f"Gia tri tai tham so trung tam (N0, g 3%, r {R:.1%}, nc 10%): 27 nam {cp27:,.0f} / vinh vien {cpinf:,.0f} truoc CK; trung binh {(cp27+cpinf)/2*(1-LD):,.0f} sau CK")
par = {}
for name, kw in {"bo_XDCB (=cach r1, NPV thuc -407)": dict(cip=False), "chi_vinh_vien (bo truc thoi han)": dict(ts=((None,), (1.0,))),
                 "bo_no_khac (ky quy + thue dat)": dict(oth=False), "r1_tai_lap (bo XDCB + bo no khac + vinh vien)": dict(cip=False, oth=False, ts=((None,), (1.0,))),
                 "holdco_10%": dict(hold=0.10), "holdco_25%": dict(hold=0.25)}.items():
    v, w = grid(**kw); s = R2.stats(v, w, PX, LD); par[name] = s
    print(f"SONG SONG {name}: " + R2.fmt(s, PX))
fin_ann = (FIN_REV_9M - FIN_EXP_9M * 0.8) * 4 / 3
cc = {"A_LNST_gom_co_tuc_vinh_vien_tru_no": ((N0 + fin_ann) * 0.9 / (R - 0.03) + CIP - OTHER_LIAB - NET_DEBT) / SH * 1000,
      "B_loi_vinh_vien_cong_co_phan_thi_gia": val(), "ROE_co_TC": (N0 + fin_ann) / EQ,
      "ROE_loi_tru_dau_tu_XDCB": N0 / (EQ - sum(INV_BOOK.values()) - CIP + NET_DEBT + OTHER_LIAB)}
print(f"Cross-check Gordon (g 3%, nc 10%, vinh vien): A von hoa LNST gom co tuc SZC/SZB (khong cong co phan) {cc['A_LNST_gom_co_tuc_vinh_vien_tru_no']:,.0f}; "
      f"B loi + co phan thi gia {cc['B_loi_vinh_vien_cong_co_phan_thi_gia']:,.0f}; ROE co TC {cc['ROE_co_TC']:.1%}; ROE loi (tru dau tu, XDCB) {cc['ROE_loi_tru_dau_tu_XDCB']:.1%}")
sens = {}
combos = list(itertools.product(NS, GS, RS, NCS, TS))
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        dr = L.r_of(dep + d, b) - R
        c = sum(w * val(n, g, r_ + dr, nc, T) for (n, g, r_, nc, T), w in zip(combos, ws)) / sum(ws)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(dr=dr, center_pre=c, d_pct=c / S['center_pre'] - 1)
print("Do nhay lai huy dong (tam truoc CK): " + "; ".join(f"{k} {v['center_pre']:,.0f} ({v['d_pct']:+.1%})" for k, v in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
sl = {k: S['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
print("Tam sau CK theo co (ADV250): " + ", ".join(f"{float(k)*1000:,.0f}tr {v:,.0f}" for k, v in sl.items()))
d40 = Q['disc_sleeve_max']
lab_sleeve = 'DUOI' if PX < S['p10_pre'] * (1 - d40) else ('TREN' if PX > S['p90_pre'] * (1 - d40) else 'TRONG')
print(f"Nhan o co sleeve 40 tr (CK {d40:.2%}): {lab_sleeve} vung (P10/P90 {S['p10_pre']*(1-d40):,.0f}/{S['p90_pre']*(1-d40):,.0f}); gia/tam {PX/(S['center_pre']*(1-d40))-1:+.1%}")
M = dict(ticker='SZL', price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, grid=S, label=lab, center_param_pre=dict(T27=cp27, perp=cpinf),
         n0=N0, net_debt=NET_DEBT, inv_mkt=mkt, gain_tax=gain_tax, cip=CIP, parallel=par, crosscheck=cc, sens_dep=sens, center_by_size=sl, label_sleeve40=lab_sleeve)
R2.dump(HERE, M)
src = [os.path.abspath(__file__), os.path.join(HERE, '..', 'SUMMARY_r1.json'), os.path.join(HERE, '..', 'src', 'Q3_2026_hopnhat.pdf'), PXF, OSF]
for r in R2.lock(HERE, [os.path.abspath(p) for p in src]):
    print("LOCK " + r)
META = dict(
    grid_desc=("5 truc, n=270 ket cuc tat dinh: LN loi N0 {-12;-6;0;+6;+12}% quanh 131,1 (0,1/0,2/0,4/0,2/0,1) [UL] x g {2;3;4}% x r {R-1;R;R+1}% x ty le LN phi tien mat {20;10;0}% [UL; can tren 17% = DT chua thuc hien 762,2/27 nam x 0,8] "
               "(moi truc 1/4-1/2-1/4) x thoi han dong tien loi {27 nam (den 2053: TM17 NQ DHDCD 76/2020 phan bo LN den 2053); vinh vien (gia han) } (3/4-1/4) [UL trong so]. Co dinh: SZC/SZB thi gia 04/11 - thue TNDN 20% lai von; chua niem yet so sach; "
               "XDCB 407,0 gia von (NPV 0; TM8: CCN Long Phuoc 344,7, nha xuong cho thue 39,2, TDC Tam An 14,2, Chau Duc 6,1...); no rong 205,5 (sau co tuc phai tra); tru ky quy 157,4 + trich thue dat bo sung 44,3 (TM16-17). Phan vi wpct tren 270 o; tam = ky vong luoi. CK thanh khoan 5 ty ADV250 ap dong loat."),
    label_note="Nhan theo co 5 ty/ADV250 (CK ~4,2%, Q/ADV >1.000% — NGOAI xa vung hieu chinh). Nhan DOI so vong 1 (TRONG -> DUOI) do sua loi NPV0 XDCB, KHONG do doi dinh nghia vung (van P10-P90). O co sleeve 40 tr xem label_sleeve40.",
    axes_included=["LN loi +-12%", "g 2/3/4%", "r +-100bp", "LN phi tien mat 0/10/20%", "thoi han dong tien 27 nam (den 2053, co so TM17) / vinh vien (MOI r2)"],
    axes_excluded=[dict(axis="chiet khau holdco tren co phan SZC/SZB", reason="khong co du lieu (SZC thanh khoan ~7,8 ty/phien); bao song song 10%/25%"),
                   dict(axis="thanh tra tap doan SNZ lan sang SZL", reason="chua co quyet dinh/ket luan neu ten SZL; WARNING"),
                   dict(axis="Long Phuoc NPV != 0 (doi von/cho thue cao)", reason="luat du an moi 03/11: NPV 0 den khi co hop dong thue/doi von co so")],
    base_adjustments=[dict(item="tru ky quy ky cuoc NH+DH 157,4 + trich bo sung chi phi thue dat KCN Long Thanh 44,3 (MOI r2; vong 1 bo sot no theo so)", effect_dong_per_share=-OTHER_LIAB / SH * 1000, basis="TM17 nhan ky quy (doi tuong khac 10,1 + BLQ 0,2 + DH 147,0); TM16 trich thue dat 44,3 (khong doi tu 01/01)", source="src/Q3_2026_hopnhat.pdf tr.20-23 (anh trang PDF 24/27)"),
                      dict(item="XDCB 407,0 cong theo gia von (MOI r2; vong 1 bo => NPV thuc -407)", effect_dong_per_share=CIP / SH * 1000, basis="BCTC ma 242/TM8a: CCN Long Phuoc 344,7 + nha xuong 39,2 + TDC Tam An 14,2 + Chau Duc 6,1 + khac; phai tra nguoi ban chi 16,7 => khong co no xay dung lon doi ung; luat du an moi 03/11", source="src/Q3_2026_hopnhat.pdf BS in tr.2"),
                      dict(item="thue TNDN 20% tren lai von chua thuc hien SZC/SZB", effect_dong_per_share=-gain_tax / SH * 1000, basis="gia so BCTC (ma 260 + co cau ABS 30/03/2026) + thue suat 20%", source="BCTC + dd_SZL_20261026/src/abs_szl_260330.txt"),
                      dict(item="LN phi tien mat tam 10% N0", effect_dong_per_share=None, basis="DT chua thuc hien ma 319+337 = 762,2 / thoi han con lai (27 nam, UOC LUONG) => can tren 17%; tam 10% = [UL], da la truc 0/10/20", source="BCTC in tr.3"),
                      dict(item="co tuc phai tra 70,4 cong vao no", effect_dong_per_share=-DIV_PAY / SH * 1000, basis="BCTC ma 313, chi 07/10/2026", source="BCTC")],
    center_vs_p50_note="tam = ky vong luoi; P50 = trung vi ket cuc; gia tri tai tham so trung tam bao 2 nhanh thoi han (27 nam/vinh vien). Nhanh vinh vien (trong so 0,25) keo P90 len; khong nhanh trong so nho nao quyet dinh P10.",
    change_reason="Vong 1 +9,9% vs zone cu 27.200. Vong 2: +XDCB 407 theo gia von (+8.445 d/cp truoc CK) — sua loi NPV0; -no khac theo so 201,7 (-4.185 d); -truc thoi han 27 nam (trong so 3/4). Tam tang manh, nhan doi TRONG -> DUOI vung.",
    change_vs_r1="(1) +XDCB 407 (+8.445 d truoc CK); (2) -ky quy + trich thue dat 201,7 (-4.185 d); (3) +truc thoi han 27 nam/vinh vien 3/4-1/4 (-); (3) tam = ky vong luoi. NHAN DOI do sua loi NPV0, khong do doi dinh nghia vung.",
    warnings=["SNZ (me 52,7%): Truong BKS bi khoi to, tam giam (CBTT ~27-28/05/2026; nhadautu, vneconomy) — ca nhan o cong ty me; chua cham phap nhan/tai san SZL",
              "Luan chuyen tien trong he sinh thai Sonadezi (ABS); so huu cheo (SZL nam SZC/SZB; SNZ nam SZL); tra truoc nguoi ban NH 14,2 -> 72,6 chua doc doi tuong; tra truoc DH cho du an Sonadezi Binh Thuan",
              "Dong Nai: sai pham quan ly xang dau/dat dai (bao chi 2026) — SZL co mang xang dau, chua bi neu ten",
              "Free float < 25%; ADV 0,46 ty — rang buoc thuc thi",
              "'Chua thay khoi to/xu phat cham phap nhan SZL': nguon = DD 26/10/2026 (nhadautu, vneconomy, doanhnghiephoinhap) + web search 05/11/2026 (baophapluat, diendandoanhnghiep) — khong co ket qua moi; khong thay NQ HDQT/DHDCD moi"],
    open_issues=["Moc 2053 lay tu NQ DHDCD 76/2020 phan bo LN (TM17) — chua doi chieu giay phep thue dat", "Chi phi tra truoc DH 280,9 (tien thue dat Chau Duc 147,3, Tan Duc 69,9...) khong cong (tai san van hanh, da phan bo vao chi phi trong N0)", "Phai tra DH khac 152,0 = LN giu lai phan bo 5,85/nam den 2053 (phi tien mat, nam trong truc nc)", "Tach XDCB Long Phuoc vs khac; tong muc 920 + tien do (bao chi: hoat dong cuoi 2026)", "Doi tuong tra truoc nguoi ban 72,6", "Chua doc LCTT/thuyet minh", "BQ OShares/BVPS restate (bay oshares)"])
json.dump(META, open(os.path.join(HERE, 'meta_r2.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
SM = R2.summary(HERE, 'SZL', M, META, os.path.join(HERE, '..', 'SUMMARY_r1.json'))
print(f"SUMMARY: tam sau {SM['center_post_liq']:,.0f} | P10/50/90 {SM['p10_out']:,.0f}/{SM['p50_out']:,.0f}/{SM['p90_out']:,.0f} | {SM['label']} | vs r1 {SM['center_change_vs_r1']:+.1%} | vs cu {SM['center_change_vs_old']:+.1%}")
