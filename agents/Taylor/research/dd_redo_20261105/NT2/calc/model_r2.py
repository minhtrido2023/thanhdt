"""NT2 VONG 2 (job Taylor_20261105_020021) — ap STANDARD_r2.md. Chay: $DNA_PYEXE -B model_r2.py > model_r2_out.txt
So BCTC giu nguyen tu vong 1 (model.py; src/Q3_2026_hopnhat_va_giaitrinh.pdf, BCTC rieng B01a-DN 30/09/2026, doc tu anh img/p06-p09).
Doi so vong 1: (1) tam = ky vong cua LUOI (vong 1 tam = 3 kich ban 400/800/1150, khac luoi); (2) them von luu dong rong 837 thu hoi
cuoi thoi han (PV) — vong 1 bo ra khoi gia tri = lech so sach khong co co so; (3) thanh khoan 250+60 phien, co 5 ty + sleeve;
(4) cross-check Gordon 2 bien the; (5) song song: bo truc von luu dong / them nhanh 15 nam."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_020021'))
import r2lib as R2
L = R2.L
SH = 287.876029
dep, dep_src = L.current_dep(); R = L.r_of(dep)
Q = R2.liq2('NT2'); PX = Q['price']; LD = Q['disc_ref']
CASH, HTM_ST = 11.835947084, 5362.324001394
LOAN = 1795.772639513
DIV_PAY = 297.125837477
AR, AP, ACCR = 4252.014358468, 2637.441833617, 777.396880480
EQ = 5421.366757659
FIN_REV_9M, FIN_EXP_9M = 226.366187841, 68.448729333
NP_9M = 906.356157027
NET_CASH = CASH + HTM_ST - LOAN - DIV_PAY
FIN_NET_AT = (FIN_REV_9M - FIN_EXP_9M) * 4 / 3 * 0.80
NWC = AR - AP - ACCR
print(f"Net cash {NET_CASH:,.1f} ty ({NET_CASH/SH*1000:,.0f} d/cp); von luu dong rong {NWC:,.1f}; thu nhap TC rong sau thue nam hoa {FIN_NET_AT:.1f}")
print(f"r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({Q['price_date']})")


def val(np_norm, yrs=10, r=R, nwc=True):
    op = np_norm - FIN_NET_AT
    pv = sum(op / (1 + r) ** t for t in range(1, yrs + 1))
    wc = NWC / (1 + r) ** yrs if nwc else 0.0
    return (NET_CASH + pv + wc) / SH * 1000


NPS = (450, 625, 800, 975, 1150); WNP = (0.1, 0.2, 0.4, 0.2, 0.1)
YRS = (8, 10, 12); WY = (0.25, 0.5, 0.25)
RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)


def grid(**kw):
    yrs = kw.pop('yrs', (YRS, WY))
    v, w = [], []
    for (a, wa), (y, wy), (rr, wr) in itertools.product(zip(NPS, WNP), zip(*yrs), zip(RS, WR)):
        v.append(val(a, y, rr, **kw)); w.append(wa * wy * wr)
    return v, w


vals, ws = grid()
S = R2.stats(vals, ws, PX, LD); lab = R2.label(PX, S)
print("LUOI r2: " + R2.fmt(S, PX))
center_param = val(800)
print(f"Gia tri tai tham so trung tam (LNST 800, 10 nam, r {R:.1%}): {center_param:,.0f} truoc CK / {center_param*(1-LD):,.0f} sau CK")
par = {}
for name, kw in {"khong_von_luu_dong (=ban r1)": dict(nwc=False), "them_nhanh_15_nam (8/10/12/15 = .2/.4/.2/.2)": dict(yrs=((8, 10, 12, 15), (0.2, 0.4, 0.2, 0.2)))}.items():
    v, w = grid(**kw); s = R2.stats(v, w, PX, LD); par[name] = s
    print(f"SONG SONG {name}: " + R2.fmt(s, PX))
cc = {"A_co_lai_tien_gui": 800 / R / SH * 1000, "B_khong_lai_tien_gui_cong_net_cash": ((800 - FIN_NET_AT) / R + NET_CASH) / SH * 1000,
      "ROE_co_lai": 800 / (EQ - DIV_PAY), "ROE_khong_lai": (800 - FIN_NET_AT) / (EQ - DIV_PAY - NET_CASH)}
print(f"Cross-check Gordon g=0 VO HAN (can tren, bo qua thoi han PPA): A co lai tien gui 800/r = {cc['A_co_lai_tien_gui']:,.0f}; "
      f"B (800-{FIN_NET_AT:.0f})/r + net cash = {cc['B_khong_lai_tien_gui_cong_net_cash']:,.0f}; ROE co lai {cc['ROE_co_lai']:.1%}, ROE van hanh (tru tien) {cc['ROE_khong_lai']:.1%}")
sens = {}
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        rr = L.r_of(dep + d, b); c = sum(w * val(a, y, rr) for (a, y, _), w in zip(itertools.product(NPS, YRS, RS), ws)) / sum(ws)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(r=rr, center_pre=c, d_pct=c / S['center_pre'] - 1)
print("Do nhay lai huy dong (tam truoc CK): " + "; ".join(f"{k} {v['center_pre']:,.0f} ({v['d_pct']:+.1%})" for k, v in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
sl = {k: S['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
print("Tam sau CK theo co (ADV250): " + ", ".join(f"{float(k)*1000:,.0f}tr {v:,.0f}" for k, v in sl.items()))
M = dict(ticker='NT2', price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, grid=S, label=lab, center_param_pre=center_param,
         net_cash=NET_CASH, nwc=NWC, fin_net_at=FIN_NET_AT, parallel=par, crosscheck=cc, sens_dep=sens, center_by_size=sl)
R2.dump(HERE, M)
src = [os.path.abspath(__file__), os.path.join(HERE, '..', 'SUMMARY_r1.json'), os.path.join(HERE, '..', 'src', 'Q3_2026_hopnhat_va_giaitrinh.pdf')]
for r in R2.lock(HERE, [os.path.abspath(p) for p in src]):
    print("LOCK " + r)
META = dict(
    grid_desc=("3 truc, n=45 ket cuc tat dinh (1 o = 1 ket cuc): LNST chuan hoa/nam {450;625;800;975;1150} ty (0,1/0,2/0,4/0,2/0,1) [UL] x thoi han dong tien "
               "con lai {8;10;12} nam (1/4-1/2-1/4) [UL, PPA/GSA ~2036 1 nguon] x r {R-1;R;R+1}% (1/4-1/2-1/4). Net cash 3.281,3 co dinh; von luu dong rong 837,2 "
               "thu hoi cuoi thoi han (PV). Gia tri sau thoi han = 0 [UL]. LNST van hanh = LNST - 168 thu nhap TC rong sau thue (nam hoa 9T). "
               "Phan vi = _shared/wpct.py tren 45 o; tam = ky vong trong so cua luoi. CK thanh khoan 5 ty (ADV250) ap dong loat."),
    label_note="Nhan theo gia tri sau CK o co 5 ty (ADV250); o co sleeve 10-40 tr CK ~0,03-0,05% — nhan khong doi. Vung P10-P90 nhu vong 1 (khong doi dinh nghia).",
    axes_included=["LNST chuan hoa (Qc/thuy van/FMP-gas gop vao) 2 chieu quanh 800", "thoi han dong tien 8/10/12 nam (2 chieu quanh 10)", "r +-100bp"],
    axes_excluded=[dict(axis="NT5 dung tien NT2", reason="luat du an moi 03/11: NPV 0 => ban co truc trung voi ban khong truc; chi WARNING quan tri"),
                   dict(axis="rui ro doi tac tien gui SHB", reason="khong co du lieu (chua doc thuyet minh tien gui theo NH); chi WARNING, khong luong hoa"),
                   dict(axis="gia han PPA > 12 nam", reason="1 nguon; bao song song nhanh 15 nam (trong so 0,2)")],
    base_adjustments=[dict(item="gia tri sau thoi han PPA/GSA = 0", effect_dong_per_share=None, basis="thoi han PPA ~10/2036 (substack, 1 nguon) [UL]; truc thoi han 8/10/12 + song song 15 nam", source="dd_NT2_20261026 §5"),
                      dict(item="von luu dong rong 837,2 thu hoi cuoi thoi han (MOI r2, cong vao)", effect_dong_per_share=NWC / (1 + R) ** 10 / SH * 1000, basis="BCTC 30/09/2026 ma 131/311/315..: phai thu KH 4.252,0 - phai tra NB 2.637,4 - CP phai tra 777,4", source="src/Q3_2026_hopnhat_va_giaitrinh.pdf tr.2-3"),
                      dict(item="co tuc phai tra 297,1 tru khoi net cash", effect_dong_per_share=-DIV_PAY / SH * 1000, basis="BCTC ma 313; GDKHQ 29/10/2026, gia 04/11 da ex-div", source="BCTC tr.3 + BQ Price")],
    center_vs_p50_note="tam = ky vong trong so luoi; P50 = trung vi ket cuc (wpct); gia tri tai tham so trung tam = LNST 800/10 nam/r 13,5%. Luoi gan doi xung => 3 so sat nhau; khong nhanh trong so nho nao quyet dinh P10/P90.",
    change_reason="Tam sau CK r2 vs zone cu 25.400 (26/10): xem center_change_vs_old; cau vong 1 (-10,9%) giu nguyen (co tuc 297, r, thu nhap TC, CK); r2 them von luu dong (+) va doi tam sang ky vong luoi.",
    change_vs_r1="(1) +von luu dong 837 thu hoi cuoi thoi han; (2) tam = ky vong luoi (LNST TB 800 thay 787,5); nhan khong doi.",
    warnings=["Xung dot loi ich voi POW (59,4%): chia co tuc hay giu tien cho NT5; quy dau tu phat trien 791 ty (BCTC 30/09) gan NT5 [elibook 22/10/2026]",
              "Tien gui tap trung SHB (bao chi Vietstock, DD 26/10; chua doi chieu thuyet minh)",
              "Lich su so lieu: soat xet H1/2026 giam LNST ~94 ty; dinh chinh BCTC 2022; phat thue 10,6 ty (2020); TTCP QHD VII (lich su); DHCD 2026 de xuat mien nhiem 1 TV BKS (ly do chua ro)",
              "'Chua thay vu viec phap ly dang mo cham tai san loi': nguon = tra bao chi trong DD 26/10/2026 (vneconomy, baophapluat, thuongtruong) + web search 05/11/2026 (xem REPORT_r2 §6)"],
    open_issues=["NQ HDQT 08/07/2026 lay y kien co dong Phu luc 13 HD mua ban khi PV Gas [24hmoney] — noi dung chua doc, khong vao mo hinh", "Thoi han PPA/GSA 2036 1 nguon","Cong thuc pass-through nhien lieu PPA", "Qc 2027 (cuoi 2026)", "Thuyet minh tien gui theo NH, phai thu EPTC qua han", "Rating 8L=3 co hoc tu power_lens.csv cu 08-28 (D/E gop, bo qua tien gui)"])
json.dump(META, open(os.path.join(HERE, 'meta_r2.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
SM = R2.summary(HERE, 'NT2', M, META, os.path.join(HERE, '..', 'SUMMARY_r1.json'))
print(f"SUMMARY: tam sau {SM['center_post_liq']:,.0f} | P10/50/90 {SM['p10_out']:,.0f}/{SM['p50_out']:,.0f}/{SM['p90_out']:,.0f} | {SM['label']} | vs r1 {SM['center_change_vs_r1']:+.1%} | vs cu {SM['center_change_vs_old']:+.1%}")
