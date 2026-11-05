"""TCH VONG 2 (job Taylor_20261105_020021) — ap STANDARD_r2.md. Chay: $DNA_PYEXE -B model_r2.py > model_r2_out.txt
So BCTC giu nguyen vong 1 (model.py; doc tu anh BCTC hop nhat/rieng 01/04-30/09/2026 chua soat xet, dd_TCH_20261031/calc/notes_read.md).
Doi so vong 1:
 (1) chiet khau holding (phan qua cong ty con) — vong 1 tam 20% trong BASE; co so du lieu chi co CAU TRUC (2 tang niem yet, CRV free float ~3%,
     khop 24/62 phien), DO LON la nhan dinh => dieu 3: chuyen sang truc xac suat {0;10;20;30}% deu 1/4 [UL], bao song song ban vong 1 va ban 0%.
 (2) tam = ky vong luoi; (3) thanh khoan 250+60 + sleeve; (4) cross-check P/B-ROE 2 bien the (co/khong lai tien gui);
 (5) song song: thang du dat cu theo bien lich su (skeptic B3), quy dat moi +-10%, CK quan tri 5/10/15%, stress tien gui NH Sai Gon Tai Loc 678,3."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_020021'))
import r2lib as R2
L = R2.L
SH = 1003.312808
dep, dep_src = L.current_dep(); R = L.r_of(dep)
Q = R2.liq2('TCH'); PX = Q['price']; LD = Q['disc_ref']
VAT, GM = 1.08, 0.519
EQ_ME = 15279.65 - 3120.54
EQ_DIRECT = 10530.2 - 4571.6
EQ_SUBS = EQ_ME - EQ_DIRECT
proj = {"NC-II": (3099.20, 0.6802, 1.0, "crv"), "Green River": (1837.75, 1.0, 1.5, "me"),
        "H2": (617.83, 1.0, 2.0, "me"), "H1+khac": (38.15 + 6.88, 0.80, 1.0, "khac")}
HTK = {"me": 759.57 + 2557.50 + 555.53 + 1677.51 + 1.71, "crv": 7390.37 + 1328.75}
HTK["khac"] = 14630.92 - HTK["me"] - HTK["crv"]
NEW = {"me": 1677.51, "crv": 1328.75}
SHARE = {"me": 1.0, "crv": 0.6802, "khac": 0.80}
cost_bl = {"me": 0.0, "crv": 0.0, "khac": 0.0}
for k, (n, sh, y, g) in proj.items():
    cost_bl[g] += n / VAT * (1 - GM)
rest_old = {k: HTK[k] - cost_bl[k] - NEW.get(k, 0.0) for k in sorted(HTK)}
SGTL = 678.3                                        # tien gui NH TMCP Sai Gon Tai Loc (skeptic B9, INCONCLUSIVE)
INT_6M = 173.51                                     # TM27 lai tien gui/cho vay 6T hop nhat


def nav(m, s_old, hold, r=R, gov=0.0, s_new=0.0, loss=0.0):
    pv = lambda y: 1 / (1 + r) ** y
    bl = {"me": 0.0, "sub": 0.0}
    for k, (n, sh, y, g) in proj.items():
        bl["me" if g == "me" else "sub"] += n / VAT * m * sh * pv(y)
    sur_me = (rest_old["me"] * s_old + NEW["me"] * s_new) * pv(4)
    sur_sub = ((rest_old["crv"] * s_old + NEW["crv"] * s_new) * SHARE["crv"] + rest_old["khac"] * s_old * SHARE["khac"]) * pv(4)
    direct = EQ_DIRECT + bl["me"] + sur_me - loss; subs = EQ_SUBS + bl["sub"] + sur_sub
    return (direct + subs * (1 - hold)) * (1 - gov) / SH * 1000


MS = (0.30, 0.335, 0.36); SS = (0.25, 0.40, 0.55); W3 = (0.25, 0.5, 0.25)
HS = (0.0, 0.10, 0.20, 0.30); WH = (0.25, 0.25, 0.25, 0.25)
RS = (R - 0.01, R, R + 0.01)


def grid(hs=(HS, WH), ss=(SS, W3), **kw):
    v, w = [], []
    for (m, wm), (s, wsv), (h, wh), (rr, wr) in itertools.product(zip(MS, W3), zip(*ss), zip(*hs), zip(RS, W3)):
        v.append(nav(m, s, h, rr, **kw)); w.append(wm * wsv * wh * wr)
    return v, w


print(f"r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({Q['price_date']}); VCSH me {EQ_ME:,.1f} ({EQ_ME/SH*1000:,.0f} d/cp) = truc tiep {EQ_DIRECT:,.1f} + qua con {EQ_SUBS:,.1f}")
vals, ws = grid()
S = R2.stats(vals, ws, PX, LD); lab = R2.label(PX, S)
print("LUOI r2: " + R2.fmt(S, PX))
cp = nav(0.335, 0.40, 0.15)
print(f"Gia tri tai tham so trung tam (m 33,5%, s_old 40%, hold 15% = trung binh truc, r {R:.1%}): {cp:,.0f} truoc / {cp*(1-LD):,.0f} sau CK; P/B ngam dinh gia {PX/(EQ_ME/SH*1000):.2f}x")
par = {}
for name, kw in {"r1_hold_10_20_30 (tam 20%)": dict(hs=((0.30, 0.20, 0.10), W3)), "hold_0 (khong CK holding)": dict(hs=((0.0,), (1.0,))),
                 "s_old_theo_bien_lich_su {40;55;70}": dict(ss=((0.40, 0.55, 0.70), W3)),
                 "quy_dat_moi_-10%": dict(s_new=-0.10), "quy_dat_moi_+10%": dict(s_new=0.10),
                 "CK_quan_tri_5%": dict(gov=0.05), "CK_quan_tri_10%": dict(gov=0.10), "CK_quan_tri_15%": dict(gov=0.15),
                 "stress_mat_100%_tien_gui_SGTL_678": dict(loss=SGTL)}.items():
    v, w = grid(**kw); s = R2.stats(v, w, PX, LD); par[name] = s
    print(f"SONG SONG {name}: " + R2.fmt(s, PX))
bvps = EQ_ME / SH * 1000
np_norm = 725 * SH / 1000                          # EPS chuan hoa 675-775 d (uoc luong v2), giua 725
int_at = INT_6M * 2 * 0.80                         # lai tien gui nam hoa sau thue (hop nhat — can tren phan me)
cash_me = 2960.0                                   # tien+HTM phan me ~2.960 (v2 §5a, skeptic B10)
cc = {"ROE_co_lai": np_norm / EQ_ME, "ROE_khong_lai_tru_tien": (np_norm - int_at) / (EQ_ME - cash_me),
      "A_PB_ROE_co_lai_g3": bvps * (np_norm / EQ_ME - 0.03) / (R - 0.03),
      "B_PB_ROE_khong_lai_g3_cong_tien": ((EQ_ME - cash_me) * ((np_norm - int_at) / (EQ_ME - cash_me) - 0.03) / (R - 0.03) + cash_me) / SH * 1000}
print(f"Cross-check P/B-ROE (g 3%, LN chuan hoa {np_norm:.0f} = EPS 725 [UL v2]): A co lai ROE {cc['ROE_co_lai']:.1%} => {cc['A_PB_ROE_co_lai_g3']:,.0f}; "
      f"B khong lai (lai TG sau thue nam hoa {int_at:.0f}) ROE {cc['ROE_khong_lai_tru_tien']:.1%} + tien me {cash_me:,.0f} => {cc['B_PB_ROE_khong_lai_g3_cong_tien']:,.0f}")
sens = {}
combos = list(itertools.product(MS, SS, HS, RS))
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        dr = L.r_of(dep + d, b) - R
        c = sum(w * nav(m, s, h, r_ + dr) for (m, s, h, r_), w in zip(combos, ws)) / sum(ws)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(dr=dr, center_pre=c, d_pct=c / S['center_pre'] - 1)
print("Do nhay lai huy dong (tam truoc CK): " + "; ".join(f"{k} {v['center_pre']:,.0f} ({v['d_pct']:+.1%})" for k, v in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
sl = {k: S['center_pre'] * (1 - Q['adv250']['sizes'][k]['disc']) for k in Q['adv250']['sizes']}
print("Tam sau CK theo co (ADV250): " + ", ".join(f"{float(k)*1000:,.0f}tr {v:,.0f}" for k, v in sl.items()))
M = dict(ticker='TCH', price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, grid=S, label=lab, center_param_pre=cp,
         rest_old=rest_old, parallel=par, crosscheck=cc, sens_dep=sens, center_by_size=sl)
R2.dump(HERE, M)
src = [os.path.abspath(__file__), os.path.join(HERE, '..', 'SUMMARY_r1.json'), os.path.join(HERE, '..', '..', '..', 'dd_TCH_20261031', 'calc', 'notes_read.md')]
for r in R2.lock(HERE, [os.path.abspath(p) for p in src]):
    print("LOCK " + r)
META = dict(
    grid_desc=("4 truc, n=108 ket cuc tat dinh: bien rong backlog {30;33,5;36}% (1/4-1/2-1/4) [UL; skeptic B12 ~33-34%] x thang du HTK dat cu sau thue {25;40;55}% (1/4-1/2-1/4) [UL; duoi bien lich su ~70% "
               "(51,9% gop) — dem chi phi hoan thanh chua cong bo] x CK holding phan qua cong ty con {0;10;20;30}% (deu 1/4) [UL] x r {R-1;R;R+1}% (1/4-1/2-1/4). Co dinh: VCSH me 12.159,1 (truc tiep 5.958,6 + qua con 6.200,5); "
               "backlog NMTT NC-II 3.099 (68,02%), Green River 1.838, H2 618 (PV 1-2 nam); thang du dat cu PV 4 nam; quy dat moi 150 To Hieu + I.14 = NPV 0 (gia so). Phan vi wpct tren 108 o; tam = ky vong luoi. CK thanh khoan 5 ty ADV250."),
    label_note="Nhan theo co 5 ty/ADV250 (CK 0,64%, Q/ADV 5,7% — TRONG vung hieu chinh). Sleeve 10-40 tr CK <0,06%. Dinh nghia vung P10-P90 khong doi.",
    axes_included=["bien rong backlog 2 chieu", "thang du dat cu 2 chieu quanh 40%", "CK holding 0-30% (MOI r2 gom 0)", "r +-100bp"],
    axes_excluded=[dict(axis="CK quan tri (governance)", reason="luat phap ly/quan tri = WARNING (2026-09-27); bao song song 5/10/15%"),
                   dict(axis="thang du quy dat moi 150 To Hieu + I.14", reason="luat du an moi 03/11: NPV 0; bao song song +-10%"),
                   dict(axis="rui ro doi tac tien gui NH Sai Gon Tai Loc 678,3", reason="skeptic B9 INCONCLUSIVE, khong co du lieu han che rut; bao stress mat 100% (can duoi cuc doan, khong phai kich ban)"),
                   dict(axis="thang du dat cu theo bien lich su ~70%", reason="giu tam 40% (dem chi phi hoan thanh chua quan sat, skeptic B3); bao song song {40;55;70}")],
    base_adjustments=[dict(item="CK holding — vong 1 tam 20% trong base; r2 chuyen thanh truc xac suat {0;10;20;30} deu (ky vong 15%)", effect_dong_per_share=None, basis="cau truc 2 tang niem yet, CRV free float ~3%, khop 24/62 phien (DNSE, dd_TCH_20261031 GAPS §1) — co so CHO SU TON TAI, DO LON = nhan dinh [UL]", source="dd_TCH_20261031/GAPS.md + SKEPTIC_20261031.md B4/B7"),
                      dict(item="thang du dat cu tam 40% (< ~70% bien lich su)", effect_dong_per_share=None, basis="dem chi phi hoan thanh HH1-HH4 + cao tang chua cong bo [UL]; skeptic B3 quy doi 40% <=> bien gop 40%", source="SKEPTIC_20261031.md B3"),
                      dict(item="quy dat moi 3.006,3 = gia so (NPV 0)", effect_dong_per_share=0.0, basis="TM17 mua dat 6T FY26: 150 To Hieu 1.677,5 (me), I.14 1.328,8 (CRV)", source="notes_read.md TM17")],
    center_vs_p50_note="tam = ky vong luoi; P50 = trung vi ket cuc; gia tri tai tham so trung tam dung hold 15% (= ky vong truc hold). Phan phoi gan doi xung; khong nhanh trong so nho nao quyet dinh P10/P90.",
    change_reason="Vong 1 +5,9% vs zone cu 12.650 (bo CK quan tri khoi base, quy dat moi NPV0). Vong 2: CK holding ky vong 20% -> 15% (truc gom 0) => tam tang.",
    change_vs_r1="(1) CK holding tu base 20% -> truc {0;10;20;30} (ky vong 15%); (2) tam = ky vong luoi; nhan TRONG giu nguyen.",
    warnings=["QD 1020/QD-XPHC 03/04/2026 Thue TP Hai Phong: khai sai TNDN, phat 2,735 + truy thu 13,676 + cham nop 3,798 = 20,21 ty (da nop, CBTT 07/04/2026)",
              "QD 1357/QD-XPHC 12/2024 UBCKNN (CBTT/giao dich ben lien quan, 295 tr) — 2 co quan, 2 loai vi pham trong 16 thang",
              "Nhom kiem soat (Do Huu Ha 30,18% + HH Finance 5,81%, nguoi lien quan) = 35,99%, chiem 71,2% phieu DHDCD 2026; Truong BKS kiem KTT cong ty con; CRV free float ~3% (chuan duy tri niem yet chua kiem)",
              "Tien gui 678,3 ty tai NH TMCP Sai Gon Tai Loc (21% tien+HTM) gan nhu khong rut khi HTM giam 2.025 — NH la ai/han che rut: INCONCLUSIVE (skeptic B9)",
              "BLQ trong tap doan da duoc cong bo (BC quan tri 6T 2026, 3 NQ HDQT 16/04, 23/06, 21/07/2026; TCH cho CRV vay 30 ty, han muc 500 ty) — con mo: BLQ NGOAI tap doan (HH Finance, gia dinh Do)",
              "Dragon Capital ban rong xuong 4,71% (15/06/2026) — nguon cung co to chuc",
              "BCTC 6T FY26 chua soat xet; su dung von chao ban 865,5 ty (M7)",
              "'Khong co khoi to/kiem toan ngoai tru': nguon = GAPS 31/10/2026 (27 PDF hoanghuy.vn) + web search 05/11/2026 (cafeland, baophapluat, stockbiz) — khong co NQ HDQT 10-11/2026 moi; NQ 08/2026 co phieu thuong 10% (da phat hanh, DKCC 04/09)"],
    open_issues=["BCTC Q3 rieng CRV (toc do tieu NMTT NC-II, skeptic B5)", "Xac minh NH Sai Gon Tai Loc", "legal-vn: nhom uy quyen 7,37% + chuan duy tri niem yet CRV", "BLQ ngoai tap doan (BC quan tri tu tr.13)",
                 "BQ OShares TCH 912,1 tr (truoc cp thuong) — dung 1.003,3", "HHS SOTP thi truong ~0,5x phan CRV (skeptic B7) chua dung lam neo"])
json.dump(META, open(os.path.join(HERE, 'meta_r2.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
SM = R2.summary(HERE, 'TCH', M, META, os.path.join(HERE, '..', 'SUMMARY_r1.json'))
print(f"SUMMARY: tam sau {SM['center_post_liq']:,.0f} | P10/50/90 {SM['p10_out']:,.0f}/{SM['p50_out']:,.0f}/{SM['p90_out']:,.0f} | {SM['label']} | vs r1 {SM['center_change_vs_r1']:+.1%} | vs cu {SM['center_change_vs_old']:+.1%}")
