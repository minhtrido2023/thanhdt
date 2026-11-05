"""SAS VONG 2 (job Taylor_20261105_020021) — ap STANDARD_r2.md. Chay: $DNA_PYEXE -B model_r2.py > model_r2_out.txt
So BCTC giu nguyen vong 1 (model.py; src/Q3_2026_tonghop_kemgiaitrinh.pdf, BCTC tong hop 30/09/2026, doc tu anh img/p04, p07-p12).
Doi so vong 1: (1) phai thu dai han khac 242,0 (ma 215) ghi theo SO SACH trong base — vong 1 loai ma khong co co so du lieu (vi pham dieu 3);
(2) them truc g {2;3;4}% (Gordon vo han, truc trong yeu bi bo o vong 1); (3) tam = ky vong luoi; (4) thanh khoan 250+60 phien + sleeve;
(5) cross-check Gordon 2 bien the; (6) song song: bo phai thu DH (= cach r1), bo truc g."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_020021'))
import r2lib as R2
L = R2.L
SH = 133.481310
dep, dep_src = L.current_dep(); R = L.r_of(dep)
Q = R2.liq2('SAS'); PX = Q['price']; LD = Q['disc_ref']
CASH, HTM = 280.717512019, 664.486706849
EMP_PAY, BONUS_FUND, TAX_PAY = 141.169135385, 99.711533217, 50.247155609
LT_INV = 253.830133419
LT_RECV = 242.036924823
EQ = 1878.261409822
NP_9M = 539.458668050
FIN_REV_9M, FIN_EXP_9M = 194.955804947, 6.671156612
EPS_RATIO = 0.883
XCASH = CASH + HTM - EMP_PAY - BONUS_FUND - TAX_PAY
FIN_AT_9M = (FIN_REV_9M - FIN_EXP_9M) * 0.80
N0 = (NP_9M - FIN_AT_9M) * 4 / 3
print(f"Tien thua {XCASH:.1f} ({XCASH/SH*1000:,.0f} d/cp); dau tu DH so sach {LT_INV:.1f} ({LT_INV/SH*1000:,.0f}); phai thu DH khac {LT_RECV:.1f} ({LT_RECV/SH*1000:,.0f}) — r2 GHI THEO SO")
print(f"LN van hanh nam hoa N0 {N0:.1f}; thu nhap TC rong sau thue nam hoa {FIN_AT_9M*4/3:.1f}; r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({Q['price_date']})")


def val(delta, n0=N0, r=R, g=0.03, recv=True):
    e27 = n0 * (1 + delta / 2); e28 = n0 * (1 + delta)
    pv = e27 / (1 + r) + e28 / (r - g) / (1 + r)
    return (XCASH + LT_INV + (LT_RECV if recv else 0.0) + pv * EPS_RATIO) / SH * 1000


DS = (-0.55, -0.40, -0.25, -0.10, 0.05); WD = (0.1, 0.2, 0.4, 0.2, 0.1)
NS = (N0 * 0.9, N0, N0 * 1.1); WN = (0.25, 0.5, 0.25)
RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25)


def grid(gs=(GS, WG), **kw):
    v, w = [], []
    for (d, wd), (n, wn), (rr, wr), (g, wg) in itertools.product(zip(DS, WD), zip(NS, WN), zip(RS, WR), zip(*gs)):
        v.append(val(d, n, rr, g, **kw)); w.append(wd * wn * wr * wg)
    return v, w


vals, ws = grid()
S = R2.stats(vals, ws, PX, LD); lab = R2.label(PX, S)
print("LUOI r2: " + R2.fmt(S, PX))
cp = val(-0.25)
print(f"Gia tri tai tham so trung tam (Delta -25%, N0, r {R:.1%}, g 3%): {cp:,.0f} truoc / {cp*(1-LD):,.0f} sau CK")
par = {}
for name, kw in {"bo_phai_thu_DH (=cach r1)": dict(recv=False), "bo_truc_g (g=3% co dinh)": dict(gs=((0.03,), (1.0,))),
                 "r1_tai_lap (bo phai thu DH + bo truc g)": dict(recv=False, gs=((0.03,), (1.0,)))}.items():
    v, w = grid(**kw); s = R2.stats(v, w, PX, LD); par[name] = s
    print(f"SONG SONG {name}: " + R2.fmt(s, PX))
# cross-check Gordon (dieu 10), Delta=-25% tu 2028, g 3%
fin_ann = FIN_AT_9M * 4 / 3
cc = {"A_co_thu_nhap_TC_khong_cong_tien": ((N0 * 0.75 + fin_ann) * EPS_RATIO / (R - 0.03)) / SH * 1000,
      "B_khong_thu_nhap_TC_cong_tien_va_tai_san": (N0 * 0.75 * EPS_RATIO / (R - 0.03) + XCASH + LT_INV + LT_RECV) / SH * 1000,
      "ROE_co_TC": (N0 + fin_ann) / EQ, "ROE_van_hanh_tru_tien_TS": N0 / (EQ - XCASH - LT_INV - LT_RECV)}
print(f"Cross-check Gordon (Delta -25% vinh vien, g 3%, khong co nam chuyen tiep): A co thu nhap TC {cc['A_co_thu_nhap_TC_khong_cong_tien']:,.0f}; "
      f"B khong TC + tien/TS {cc['B_khong_thu_nhap_TC_cong_tien_va_tai_san']:,.0f}; ROE co TC {cc['ROE_co_TC']:.1%}; ROE van hanh {cc['ROE_van_hanh_tru_tien_TS']:.1%}")
sens = {}
combos = list(itertools.product(DS, NS, RS, GS))
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        rr0 = L.r_of(dep + d, b) - R
        c = sum(w * val(dd, n, r_ + rr0, g) for (dd, n, r_, g), w in zip(combos, ws)) / sum(ws)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(dr=rr0, center_pre=c, d_pct=c / S['center_pre'] - 1)
print("Do nhay lai huy dong (tam truoc CK, dich ca truc r): " + "; ".join(f"{k} {v['center_pre']:,.0f} ({v['d_pct']:+.1%})" for k, v in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
sl = {k: S['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
print("Tam sau CK theo co (ADV250): " + ", ".join(f"{float(k)*1000:,.0f}tr {v:,.0f}" for k, v in sl.items()))
lab_sleeve = 'DUOI' if PX < S['p10_pre'] * (1 - Q['disc_sleeve_max']) else ('TREN' if PX > S['p90_pre'] * (1 - Q['disc_sleeve_max']) else 'TRONG')
print(f"Nhan o co sleeve 40 tr (CK {Q['disc_sleeve_max']:.2%}): {lab_sleeve} vung (P10/P90 {S['p10_pre']*(1-Q['disc_sleeve_max']):,.0f}/{S['p90_pre']*(1-Q['disc_sleeve_max']):,.0f}); gia/tam {PX/(S['center_pre']*(1-Q['disc_sleeve_max']))-1:+.1%}")
M = dict(ticker='SAS', price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, grid=S, label=lab, center_param_pre=cp,
         xcash=XCASH, n0=N0, parallel=par, crosscheck=cc, sens_dep=sens, center_by_size=sl, label_sleeve40=lab_sleeve)
R2.dump(HERE, M)
src = [os.path.abspath(__file__), os.path.join(HERE, '..', 'SUMMARY_r1.json'), os.path.join(HERE, '..', 'src', 'Q3_2026_tonghop_kemgiaitrinh.pdf')]
for r in R2.lock(HERE, [os.path.abspath(p) for p in src]):
    print("LOCK " + r)
META = dict(
    grid_desc=("4 truc, n=135 ket cuc tat dinh: tac dong Long Thanh len LN van hanh tu 2028 Delta {-55;-40;-25;-10;+5}% (0,1/0,2/0,4/0,2/0,1) [UL; bien duoi ~ mat toan bo mang gan khach quoc te ~57% DT Q3] "
               "x N0 {-10%;0;+10%} quanh 518,4 (1/4-1/2-1/4) x r {R-1;R;R+1}% x g {2;3;4}% (moi truc 1/4-1/2-1/4). 2027 = nua tac dong [UL]. Tien thua 654,1 + dau tu DH so sach 253,8 "
               "+ phai thu DH khac so sach 242,0 co dinh; LN x 0,883 (EPS/LNST 2025). Phan vi = wpct tren 135 o; tam = ky vong luoi. CK thanh khoan 5 ty ADV250 ap dong loat."),
    label_note="Nhan theo co 5 ty/ADV250 (CK ~6%, Q/ADV ~850% — NGOAI xa vung hieu chinh, con so CK chi mang tinh quy uoc). O co sleeve 10-40 tr (CK <=0,6%) xem label_sleeve40 trong model_r2_out.json. Dinh nghia vung P10-P90 khong doi.",
    axes_included=["Delta Long Thanh 2 chieu quanh -25%", "N0 +-10%", "r +-100bp", "g 2/3/4% (MOI r2)"],
    axes_excluded=[dict(axis="truy thu tien thue dat them (sau 2015-2024 da hach toan Q4/2025)", reason="khong co du lieu so tien/quyet dinh moi; WARNING"),
                   dict(axis="pha loang khi phat hanh/chuyen HOSE", reason="chua co gia/ty le; phat hanh theo gia thi truong ~ NPV 0; WARNING"),
                   dict(axis="trich lap HTK 204,3 / phai thu DH 242 khong thu hoi", reason="chua doc thuyet minh; khong co du lieu suy giam => ghi so sach; song song bo phai thu DH duoc bao")],
    base_adjustments=[dict(item="Delta Long Thanh tam -25% tu 2028 (2027 = -12,5%)", effect_dong_per_share=None, basis="lo trinh Cuc HK chuyen chuyen quoc te sang Long Thanh 28/3/2027-25/3/2028; DT mien thue+phong cho ~57% DT Q3 gan khach quoc te; DO LON tam = nhan dinh [UL] — da la truc xac suat 2 chieu", source="dd_SAS_20261026 §2-3"),
                      dict(item="phai thu DH khac 242,0 ghi theo so (MOI r2, vong 1 loai)", effect_dong_per_share=LT_RECV / SH * 1000, basis="BCTC ma 215; khong co du lieu suy giam", source="src/Q3_2026_tonghop_kemgiaitrinh.pdf in tr.1-2"),
                      dict(item="tru phai tra NLD 141,2 + quy KTPL 99,7 + thue 50,2 khoi tien", effect_dong_per_share=-(EMP_PAY + BONUS_FUND + TAX_PAY) / SH * 1000, basis="BCTC ma 315/323/314", source="BCTC in tr.3-4"),
                      dict(item="LN x 0,883 (trich quy khong thuoc co dong)", effect_dong_per_share=None, basis="EPS 2025 4.602 / (LNST 695,6 / 133,45 tr cp)", source="DHDCD 2026 (vietnambiz 25/06/2026) + BQ")],
    center_vs_p50_note="tam = ky vong trong so luoi (Gordon loi => phan phoi lech phai nhe, tam > P50); P50 = trung vi ket cuc; gia tri tai tham so trung tam (Delta -25, g 3) thap hon tam vi Gordon loi theo g. Khong nhanh trong so nho nao quyet dinh P10/P90.",
    change_reason="Vong 1 -10,5% vs zone cu 32.600 (CK thanh khoan + cau truc BCTC goc + r). Vong 2 them phai thu DH 242 (+1.813 d truoc CK) va truc g (loi Gordon => nang tam).",
    change_vs_r1="(1) +phai thu DH 242 theo so; (2) +truc g 2/3/4%; (3) tam = ky vong luoi (trung voi 3 kich ban ve Delta trung binh -25%).",
    warnings=["Mat bang ACV giao truc tiep khong dau thau (KL TTCP 2017); lo dat chua hoan tat thu tuc; truy thu tien thue dat 2015-2024 'hang chuc ty' hach toan Q4/2025 [vietstock] — rui ro truy thu them",
              "Giao dich ben lien quan nhom IPP (IPPG 24,98%/ACFC 14,89%/DAFC 4,92%/DAT 1,71% = 46,5%) vua co dong vua doi tac; lich su phai thu LD Nha Viet ~292 ty trich lap ~251 ty",
              "Free float ~4,4% (ACV 49,07% + IPP 46,50%) — rang buoc thuc thi; Chu tich noi tu van hanh mien thue 'khong the keo dai', doi tac moi chua cong bo dieu khoan",
              "Ke hoach chuyen HOSE + co the phat hanh them (chua co lich)",
              "Nhan su: HDQT bo nhiem TGD moi Du Kim Thang 03/08/2026, TGD cu Nguyen Van Hung Cuong ve ACV [cafef 04/08/2026]",
              "'Khong thay vu viec hinh su/khoi to lien quan SASCO': nguon = DD 26/10/2026 (anninhthudo, thuonghieucongluan, vietstock) + web search 05/11/2026 (cafef, dnse, baophapluat) — khong co ket qua moi; khong thay NQ HDQT 10-11/2026 ve Long Thanh"],
    open_issues=["Thuyet minh V.5b phai thu DH khac 242,0 (ky quy ACV?) — r2 ghi so sach, can doc", "Khoan bu DFS Q4/2025 chua co so", "Ben tra co tuc dau tu 195,0 9T", "Ket qua thau Long Thanh + lo trinh chuyen bay chinh thuc",
                 "HTK 68,9 -> 204,3 chua trich lap", "Thieu sector read dich vu hang khong", "BQ EPS = 0 moi quy SAS (cot hong)"])
json.dump(META, open(os.path.join(HERE, 'meta_r2.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
SM = R2.summary(HERE, 'SAS', M, META, os.path.join(HERE, '..', 'SUMMARY_r1.json'))
print(f"SUMMARY: tam sau {SM['center_post_liq']:,.0f} | P10/50/90 {SM['p10_out']:,.0f}/{SM['p50_out']:,.0f}/{SM['p90_out']:,.0f} | {SM['label']} | vs r1 {SM['center_change_vs_r1']:+.1%} | vs cu {SM['center_change_vs_old']:+.1%}")
