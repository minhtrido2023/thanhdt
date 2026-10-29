"""DD PVP 29/10/2026 — moi so lay tu BCTC goc (trang ghi canh), don vi ty VND tru khi ghi khac.
Chay: python3 -I calc.py > out.txt   (v2 29/10 job Taylor_20261029_072547; v1 = calc_v1.py)
[AGM pN] = src/agm2026_nq_bienban.pdf (NQ+BB DHDCD thuong nien 23/06/2026); [CB] = src/cb_*.pdf
[Q3 pN] = src/bctc_q3_2026.pdf trang PDF N; [H1 pN] = src/bctc_banien_2026_kiemtoan.pdf; [Q2 pN] = src/bctc_q2_2026.pdf
Gia tri '(uoc luong)' = gia dinh tu dat, KHONG phai so do."""

def chk(name, v, tol=0.01):
    print(f"  SELF-CHECK {name}: diff={v:.4f} {'OK' if abs(v) <= tol else 'FAIL'}")

print("== 1. KQKD (dong -> ty) ==")
# [Q3 p6] KQKD quy 3 + luy ke 9T; [H1 p9] KQKD 6T soat xet
q3 = dict(dt=838.414389745, gv=744.522093524, gp=93.892296221, dtc=19.142556661, cptc=10.572278353,
          ql=17.303148685, lnkd=85.159425844, khac=0.006046714, lntt=85.165472558, thue=17.651787552, lnst=67.513685006)
n9 = dict(dt=2205.746768242, gv=1843.302852715, gp=362.443915527, dtc=61.835963996, cptc=36.421037294,
          ql=38.896265344, lnkd=348.962576885, khac=-0.022793887, lntt=348.939782998, thue=70.911174041, lnst=278.028608957)
n9_25 = dict(dt=1811.566056050, gp=225.883435710, lntt=194.344208316, lnst=154.608211416)
q3_25 = dict(dt=833.468062081, gp=85.307909755, lntt=85.875050582, lnst=69.212542535)
h1 = dict(dt=1367.332378497, gv=1098.780759191, gp=268.551619306, dtc=42.693407335, cptc=25.848758941,
          ql=21.593116659, lnkd=263.803151041, khac=-0.028840601, lntt=263.774310440, thue=53.259386489, lnst=210.514923951)
for k, d in (("Q3", q3), ("9T", n9), ("H1", h1)):
    chk(f"{k} DT-GV-GP", d["dt"] - d["gv"] - d["gp"])
    chk(f"{k} LNKD", d["gp"] + d["dtc"] - d["cptc"] - d["ql"] - d["lnkd"])
    chk(f"{k} LNTT-thue-LNST", d["lnkd"] + d["khac"] - d["thue"] - d["lnst"], 0.02)
for key in ("dt", "gp", "lntt", "lnst"):
    chk(f"H1+Q3=9T {key}", h1[key] + q3[key] - n9[key])
q2_lnst_bctc = 134.19  # [Q2 p17 giai trinh] 134,19
q1_bq = 75.543199612   # BQ ticker_financial 2026Q1 NP_P0
print(f"  Q1 suy ra = H1 soat xet - Q2 BCTC = {h1['lnst']-q2_lnst_bctc:.2f} (BQ Q1 {q1_bq:.2f}; lech {h1['lnst']-q2_lnst_bctc-q1_bq:+.2f} = dieu chinh soat xet, xem duoi)")
q2 = h1["lnst"] - q1_bq
print(f"  LNST quy: Q1 {q1_bq:.1f} | Q2 {q2:.1f} (BCTC Q2 {q2_lnst_bctc}) | Q3 {q3['lnst']:.1f} | Q3/Q2 {q3['lnst']/q2_lnst_bctc-1:+.1%} | Q3 YoY {q3['lnst']/q3_25['lnst']-1:+.1%}")
print(f"  9T LNST YoY {n9['lnst']/n9_25['lnst']-1:+.1%}; LNTT YoY {n9['lntt']/n9_25['lntt']-1:+.1%}")
kh = dict(dt=2700, lntt=270, lnst=216)  # [AGM p21] NQ 01-2026/NQ-TBD-DHDCD 23/06/2026 Phu luc 04 (goc, da doc)
print(f"  KH 2026: 9T DT {n9['dt']/kh['dt']:.1%} | LNTT {n9['lntt']/kh['lntt']:.1%} | LNST {n9['lnst']/kh['lnst']:.1%}")
q6_sum = q1_bq + q2_lnst_bctc  # 6T theo BCTC quy (chua soat xet)
print(f"  6T LNST: tong quy {q6_sum:.2f} -> soat xet {h1['lnst']:.2f} (dieu chinh {h1['lnst']-q6_sum:+.2f}) => giai thich lech Q1 0,78")
chk("Q1 lech = dieu chinh soat xet", (h1['lnst']-q2_lnst_bctc-q1_bq) - (h1['lnst']-q6_sum))
print(f"  6T LNST/KH LNST = {h1['lnst']/kh['lnst']:.1%}; 6T(quy) LNST/KH LNTT = {q6_sum/kh['lntt']:.1%} (bao chi '77,6%': gan nhat voi phep chia LNST/KH LNTT, khong tai lap dung)")

print("\n== 2. Bo phan (DT / GVHB / LN gop) ==")
# H1 [H1 p29 xoay]; Q2 [Q2 p13-14]; Q3 [Q3 p13-14]; H1/25 [H1 p30]; Q3/25 [Q3 p13-14]
seg = {
 "VT_H1": (598.117193661, 375.606611925), "VT_Q2": (365.475726265, 219.014069365), "VT_Q3": (224.430399118, 154.070339918),
 "VT_H1_25": (328.158998302, 250.012054067), "VT_Q3_25": (172.895613185, 110.359807753),
 "FSO_H1": (117.764560170, 74.076946322), "FSO_Q3": (59.657381700, 37.035887661),
 "FSO_H1_25": (122.924045800, 76.263490150), "FSO_Q3_25": (59.993854920, 38.129175075),
 "LPG_Q3": (272.152402439, 272.095889917), "UYTHAC_Q3": (280.009506488, 279.352403952), "QLT_Q3": (2.164700000, 1.967572076),
 "LPG_H1": (212.660286897, 212.621993824), "TMDV_H1": (438.790337769, 436.475207120),
}
gp = {k: v[0] - v[1] for k, v in seg.items()}
for k, (r, c) in seg.items():
    print(f"  {k:10s} DT {r:8.1f} GV {c:8.1f} LNG {r-c:7.1f} bien {(r-c)/r:6.1%}")
vt_q1 = (seg["VT_H1"][0] - seg["VT_Q2"][0], seg["VT_H1"][1] - seg["VT_Q2"][1])
print(f"  VT_Q1 suy ra DT {vt_q1[0]:.1f} LNG {vt_q1[0]-vt_q1[1]:.1f}")
chk("Q3 tong LNG bo phan = KQKD", gp["VT_Q3"] + gp["FSO_Q3"] + gp["LPG_Q3"] + gp["UYTHAC_Q3"] + gp["QLT_Q3"] - q3["gp"])
chk("H1 tong LNG bo phan = KQKD", gp["VT_H1"] + gp["FSO_H1"] + gp["LPG_H1"] + gp["TMDV_H1"] - h1["gp"])
vt9, vt9_25 = gp["VT_H1"] + gp["VT_Q3"], gp["VT_H1_25"] + gp["VT_Q3_25"]
fso9, fso9_25 = gp["FSO_H1"] + gp["FSO_Q3"], gp["FSO_H1_25"] + gp["FSO_Q3_25"]
print(f"  LNG van tai 9T {vt9:.1f} vs {vt9_25:.1f} ({vt9/vt9_25-1:+.0%}); FSO 9T {fso9:.1f} vs {fso9_25:.1f}")
print(f"  Delta LNG 9T tong {n9['gp']-n9_25['gp']:.1f}; trong do van tai {vt9-vt9_25:.1f} = {(vt9-vt9_25)/(n9['gp']-n9_25['gp']):.0%}")
print(f"  Q3 vs Q2 LNG van tai {gp['VT_Q3']:.1f} vs {gp['VT_Q2']:.1f} ({gp['VT_Q3']/gp['VT_Q2']-1:+.0%}); DT {seg['VT_Q3'][0]/seg['VT_Q2'][0]-1:+.0%}")
fso_dep9 = 111.107662983  # [Q3 p10] KH FSO 9T
print(f"  FSO GV 9T {seg['FSO_H1'][1]+seg['FSO_Q3'][1]:.2f} vs KH FSO 9T {fso_dep9:.2f} -> GV FSO gan nhu toan bo la khau hao")

print("\n== 3. Chat luong LN 9T ==")
lai_gui_9t = 57.414145379  # [Q3 p7] LCTT ma 05 lai hoat dong dau tu (lai tien gui)
du_phong_9t25 = 53.138535290  # [Q3 p7] LCTT 9T/25 ma 03 cac khoan du phong; 9T/26 = 0
print(f"  Lai hoat dong dau tu (lai gui) 9T {lai_gui_9t:.1f} = {lai_gui_9t/n9['lntt']:.1%} LNTT")
print(f"  Du phong sua chua dinh ky trich 9T/25 {du_phong_9t25:.1f}; 9T/26 = 0 (TT99) -> {du_phong_9t25/n9['lntt']:.1%} LNTT 9T/26; sau thue ~{du_phong_9t25*0.8:.1f}")
# Khau hao [Q3 p7 LCTT ma 02] 9T/26 239,514 vs 9T/25 275,164; [Q2 p14 TM 8a] Q2/26 79,764 vs Q2/25 98,489
kh9_26, kh9_25, khq2_26, khq2_25 = 239.514217273, 275.164286673, 79.763897394, 98.488635642
apollo9_25 = kh9_25 - kh9_26  # suy luan: chenh KH 9T gan het do Apollo het khau hao giua 2025 (Era/Pride da KH du nam 2025)
print(f"  KH 9T {kh9_25:.1f}->{kh9_26:.1f} (chenh {apollo9_25:.1f}); Q2 {khq2_25:.1f}->{khq2_26:.1f} (chenh {khq2_25-khq2_26:.1f}); Q1+Q3 chenh {apollo9_25-(khq2_25-khq2_26):.1f}")
basisA = (n9['lntt'] - du_phong_9t25 - apollo9_25, n9_25['lntt'])   # ca hai ky CO trich sua chua + CO KH Apollo
basisB = (n9['lntt'], n9_25['lntt'] + du_phong_9t25 + apollo9_25)   # ca hai ky KHONG trich + KHONG KH Apollo
print(f"  LNTT 9T cung co so A (deu trich + deu KH Apollo): {basisA[0]:.1f} vs {basisA[1]:.1f} = {basisA[0]/basisA[1]-1:+.1%}")
print(f"  LNTT 9T cung co so B (deu khong trich + khong KH Apollo): {basisB[0]:.1f} vs {basisB[1]:.1f} = {basisB[0]/basisB[1]-1:+.1%}")
print(f"  (bao cao: {n9['lntt']/n9_25['lntt']-1:+.1%}; v1 chi bo trich sua chua: {(n9['lntt']-du_phong_9t25)/n9_25['lntt']-1:+.1%})")
dp_q3_25 = du_phong_9t25 / 3  # suy luan: trich deu theo quy, gan vao gia von van tai
vt_q3_25_adj = 62.535805432 + dp_q3_25
print(f"  Q3 LNG van tai cung co so (Q3/25 cong lai trich ~{dp_q3_25:.1f}, suy luan): 70,4 vs {vt_q3_25_adj:.1f} = {70.360059200/vt_q3_25_adj-1:+.1%} (bao cao +12,6%)")

print("\n== 4. Can doi 30/9/2026 [Q3 p3-5, p11] ==")
cash, htm = 718.157785658, 1015.871222815
vay_nh, vay_dh = 134.947466668, 473.526733330
ct_phai_tra = 109.525626200
dp_suachua = 232.937139850
eq = 2099.610822117
tts, npt = 3597.451169157, 1497.840347040
chk("TTS = NPT + VCSH", tts - npt - eq)
chk("TTS = TSNH + TSDH", tts - 2317.939622076 - 1279.511547081)
chk("Vay = chi tiet TM11", vay_nh + vay_dh - 608.474199998)
net_cash = cash + htm - vay_nh - vay_dh
print(f"  Tien+HTM {cash+htm:.1f}; vay {vay_nh+vay_dh:.1f} (VND, Woori/VCB) ; NET CASH {net_cash:.1f}; tru co tuc phai tra {net_cash-ct_phai_tra:.1f}")
div25 = 103.702452  # [CB NQ 17/NQ-TBD-HDQT 28/08/2026] co tuc 2025 10%, DKCC 18/09, THANH TOAN 20/10/2026
print(f"  Co tuc 2025 {div25:.1f} ty: lich thanh toan 20/10 theo NQ 17 (sau ngay BCTC; chua co chung tu); KH tam ung 2026 10% = {div25:.1f} ty nua [AGM p22], chua co ngay")
lai_gui_q3 = 23.017556835
print(f"  Lai gui Q3 nam hoa / (tien+HTM) = {lai_gui_q3*4/(cash+htm):.1%}")
cfo9, capex9 = 473.034903663, 0.179985
d_a9 = 239.514217273
print(f"  CFO 9T {cfo9:.1f} = {cfo9/n9['lnst']:.2f}x LNST; capex {capex9:.2f}; KH 9T {d_a9:.1f}")
ebitda9 = n9["gp"] - n9["ql"] + d_a9
print(f"  EBITDA 9T (LNG - QLDN + KH) {ebitda9:.1f}; nam hoa {ebitda9*4/3:.1f}")
shares = 103.702452  # trieu cp [Q3 p13]
bvps = eq / shares * 1000
print(f"  BVPS {bvps:,.0f} VND; net cash/cp {net_cash/shares*1000:,.0f}")
ships = {"Apollo": (446.436130362, 446.436130362), "Pacific Era": (580.284981192, 237.767305551),
         "Pacific Pride": (688.016961981, 192.348828085), "FSO Dai Hung Queen": (1873.653675912, 1484.577737767)}
dep9 = {"Apollo": 0, "Pacific Era": 54.467926128, "Pacific Pride": 73.716103071, "FSO Dai Hung Queen": 111.107662983}
for k, (ng, hm) in ships.items():
    nbv = ng - hm; yr = dep9[k] * 4 / 3
    print(f"  {k:20s} NG {ng:8.1f} NBV {nbv:7.1f} KH/nam {yr:6.1f} con {nbv/yr if yr else 0:4.1f} nam")

print("\n== 5. Capex Aframax #2/#3 [H1 p34] ==")
fx = 26040  # VCB ban USD 29/10/2026 (Bobby §3.4)
proj = {"Aframax#2": (56.5, 17.08, 39.42), "Aframax#3/2xMR": (59.5, 18.11, 41.39)}
tot = sum(v[0] for v in proj.values()); eqp = sum(v[1] for v in proj.values()); debt = sum(v[2] for v in proj.values())
chk("tong = VCSH + vay", tot - eqp - debt)
print(f"  Tong {tot} trUSD = {tot*fx/1e3:,.0f} ty; VCSH {eqp:.2f} trUSD = {eqp*fx/1e3:,.0f} ty; vay {debt:.2f} = {debt*fx/1e3:,.0f} ty")
cash_after = cash + htm - ct_phai_tra - eqp * fx / 1e3
debt_after = vay_nh + vay_dh + debt * fx / 1e3
print(f"  Neu mua ca 2: tien con {cash_after:,.0f}; vay {debt_after:,.0f}; no rong {debt_after-cash_after:,.0f}; /VCSH {(debt_after-cash_after)/eq:.2f}")
print(f"  So voi von hoa @18.750: {tot*fx/1e3/(shares*18.75):.2f}x")
print("  Kha thi cong ty [AGM p44]: TC binh quan doi du an 30.240 USD/ngay, NPV du an 43.719 USD (~0), IRR 7,67%, ROE 10,03%")
# Kich ban mua (uoc luong): DHDCD 23/06 da duyet ca 2 du an; Aframax #2 co BCNCKT (PL11); DHDCD bat thuong (<=30/11) ve tau #3 [web 12/09]
BUY = {"ca 2 du an": (0.50, 56.5 + 59.5, 17.08 + 18.11), "chi Aframax #2": (0.35, 56.5, 17.08), "khong mua": (0.15, 0.0, 0.0)}
chk("tong xac suat mua = 1", sum(v[0] for v in BUY.values()) - 1)
exp_cost = sum(v[0] * v[1] for v in BUY.values()); exp_eq = sum(v[0] * v[2] for v in BUY.values())
print(f"  Kich ban mua (uoc luong): " + "; ".join(f"{k} p={v[0]:.2f} {v[1]:.1f} trUSD (VCSH {v[2]*fx/1e3:,.0f} ty)" for k, v in BUY.items()))
print(f"  Ky vong: gia tri tau mua {exp_cost:.1f} trUSD = {exp_cost*fx/1e3:,.0f} ty; VCSH chi {exp_eq*fx/1e3:,.0f} ty")

print("\n== 6. Dinh gia ==")
px = {"DNSE 14:29 29/10 (san)": 18750, "BQ dong cua 28/10": 20150, "brief Mike (=dong cua 20/10)": 22900}
q4_25 = 43.867285779  # BQ 2025Q4 NP_P0
ttm = n9["lnst"] + q4_25
eps_ttm = ttm / shares * 1000
lnst_hist = {2023: 183.97, 2024: 207.10, 2025: 198.48}  # tong NP_P0 quy BQ; 2025 khop TM20 'lai 2025' 198,475
for k, p in px.items():
    mc = p * shares / 1000
    ev = mc - net_cash + ct_phai_tra
    print(f"  {k:30s} gia {p:,} vh {mc:,.0f} PE_TTM {p/eps_ttm:.2f} PB {p/bvps:.2f} EV {ev:,.0f} EV/EBITDA9Tnh {ev/(ebitda9*4/3):.2f} DY(1.000) {1000/p:.1%}")
print(f"  LNST TTM {ttm:.1f}; EPS {eps_ttm:,.0f}; LNST 2023-25 TB {sum(lnst_hist.values())/3:.1f}")
print("  PVP lich su 2018- [BQ]: PE p25/50/75 4,90/6,33/8,00; PB 0,53/0,77/0,91")
print(f"  PB trung vi lich su x BVPS = {0.7678*bvps:,.0f}")

# --- Trong so nhanh (uoc luong). v2: tot = 0,15 = K3 Bobby (sector_read_oil_gas_shipping_20261029 §3-4); 0,05 chuyen sang xau (CYCLICAL 0,55, P(BDTI<=3.500 @30/09/27)=0,58)
SC = {"xau": 0.40, "co so": 0.45, "tot": 0.15}
SC_ALT = {"v1 0,35/0,45/0,20": {"xau": 0.35, "co so": 0.45, "tot": 0.20}, "v2 0,40/0,45/0,15": SC, "nghiem 0,45/0,40/0,15": {"xau": 0.45, "co so": 0.40, "tot": 0.15}}
for k, w in SC_ALT.items():
    chk(f"trong so {k} = 1", sum(w.values()) - 1)
loss = {"xau": 0.30, "co so": 0.10, "tot": 0.0}  # thiet hai mua o dinh gia tau cu (uoc luong), ap CHO MOI du an duoc mua
npv = {k: -loss[k] * exp_cost * fx / 1e3 for k in SC}  # ty, ky vong theo kich ban mua
npv_both = {k: -loss[k] * (56.5 + 59.5) * fx / 1e3 for k in SC}
print("  NPV mua dat (ky vong theo xac suat mua):", {k: round(v) for k, v in npv.items()}, "| neu mua ca 2:", {k: round(v) for k, v in npv_both.items()})
chk("NPV ca 2 xau = -0,30 x 3.021", npv_both["xau"] + 0.30 * 116 * fx / 1e3)

# --- FSO: lich cam ket [H1 p34] la RIENG FSO Dai Hung Queen, da theo don gia + thoi han moi den 31/12/2036 -> KHONG nhan he so gia
fso_contract = 1163.667442078
fso_b = {"<=1 nam (7/26-6/27)": 415.806684400, "nam 2-5 (7/27-6/31)": 542.907538963, ">5 nam (7/31-12/36)": 204.953218715}
fso_b0 = {"<=1": 234.570469879, "2-5": 652.914144715, ">5": 238.145590595}  # so dau ky 01/01/2026
chk("FSO lich = tong cam ket", sum(fso_b.values()) - fso_contract)
chk("FSO lich dau ky = 1.125,6", sum(fso_b0.values()) - 1125.630205189)
fso_q3 = seg["FSO_Q3"][0]
fso_run = fso_q3 * 4
print(f"  FSO doanh thu hien nay ~{fso_run:.0f}/nam (Q3 x4); lich cam ket: nam 1 {fso_b['<=1 nam (7/26-6/27)']:.1f}, nam 2-5 {fso_b['nam 2-5 (7/27-6/31)']/4:.1f}/nam, sau nam 5 {fso_b['>5 nam (7/31-12/36)']/5.5:.1f}/nam (5,5 nam)")
print(f"  Dau ky (01/01/26): <=1 nam {fso_b0['<=1']:.1f} (~ run-rate), 2-5 {fso_b0['2-5']/4:.1f}/nam, >5 {fso_b0['>5']/6:.1f}/nam (6 nam)")
added = fso_contract - sum(fso_b0.values()) + seg["FSO_H1"][0]
print(f"  Doi soat H1: cam ket tang {fso_contract-sum(fso_b0.values()):+.1f} du da thu H1 {seg['FSO_H1'][0]:.1f} => cam ket moi bo sung ~{added:.1f} ty, don vao nam 1 (+{fso_b['<=1 nam (7/26-6/27)']-fso_b0['<=1']:.1f}). KHONG hoa giai duoc (gia thuyet: chenh lech gia hoi to chua ghi nhan)")
fso_y1_excess = fso_b['<=1 nam (7/26-6/27)'] - fso_run
# dong tien FSO sau thue tu 30/9/2026: rev*0,8 + KH*0,2 (gia von FSO ~ toan bo la KH); chiet khau 10%/nam (uoc luong)
r = 0.10
nbv_fso = 1873.653675912 - 1484.577737767; kh_fso_yr = 111.107662983 * 4 / 3
flows = []  # (t nam tu 30/9/2026, doanh thu)
flows.append((0.375, fso_b['<=1 nam (7/26-6/27)'] - fso_q3))       # 10/26-6/27, giua ky ~0,375 nam
for y in range(4): flows.append((0.75 + y + 0.5, fso_b['nam 2-5 (7/27-6/31)'] / 4))
for y in range(6): flows.append((4.75 + y + 0.5, fso_b['>5 nam (7/31-12/36)'] / 5.5 * (0.5 if y == 5 else 1.0)))
chk("FSO dong tien con lai = cam ket - Q3", sum(f[1] for f in flows) - (fso_contract - fso_q3))
dep_left = nbv_fso; fso_pv = 0.0
for t, rev in flows:
    period = 0.75 if t < 0.75 else 1.0
    dep = min(dep_left, kh_fso_yr * period); dep_left -= dep
    fso_pv += (rev * 0.8 + dep * 0.2) / (1 + r) ** t
print(f"  FSO PV sau thue @10%: {fso_pv:,.1f} ty = {fso_pv/shares*1000:,.0f} d/cp (v1 dung 541/696/773 voi he so gia, da BO)")
fso_pv_noexcess = fso_pv - fso_y1_excess * 0.8 / (1 + r) ** 0.375
print(f"  Do nhay: neu phan nam 1 vuot run-rate ({fso_y1_excess:.1f} ty) KHONG thanh tien: FSO PV {fso_pv_noexcess:,.1f} ({(fso_pv_noexcess-fso_pv)/shares*1000:+,.0f} d/cp)")
# v2.1 (skeptic vong 2, sua g): do nhay suat chiet khau FSO 8/10/12%
def fso_pv_at(rr):
    dl = nbv_fso; v = 0.0
    for t, rev in flows:
        d = min(dl, kh_fso_yr * (0.75 if t < 0.75 else 1.0)); dl -= d
        v += (rev * 0.8 + d * 0.2) / (1 + rr) ** t
    return v
chk("fso_pv_at(10%) = fso_pv", fso_pv_at(0.10) - fso_pv)
print("  v2.1 Do nhay FSO PV theo chiet khau: " + " | ".join(f"r={rr:.0%} {fso_pv_at(rr):,.1f} ty ({(fso_pv_at(rr)-fso_pv)/shares*1000:+,.0f} d/cp)" for rr in (0.08, 0.10, 0.12)))

# --- PP-A: PE lich su PVP x LNST 2027 (uoc luong) + NPV mua dat
# v2: LNST 2027 tru ~40 ty (uoc luong) cho FSO giam tu ~237 xuong ~136/nam tu 7/2027: (237-136)/2 x 0,8
lnst27 = {"xau": 150, "co so": 200, "tot": 260}
pe = {"xau": 4.90, "co so": 6.33, "tot": 8.00}
va = {k: (lnst27[k] * pe[k] + npv[k]) / shares * 1000 for k in SC}
print("  PP-A (PE lich su x LNST 2027 uoc luong + NPV mua dat):", {k: round(v) for k, v in va.items()}, "ky vong", round(sum(SC[k]*va[k] for k in SC)))

# --- PP-B: SOTP
tank_ebitda = {"xau": 300, "co so": 400, "tot": 550}  # uoc luong
mult = {"xau": 3.0, "co so": 3.5, "tot": 4.0}  # uoc luong
corp = 52 * 0.8 * 5  # QLDN ~52/nam x (1-thue) x 5 (uoc luong)
vt_ebitda_9t = vt9 + dep9["Pacific Era"] + dep9["Pacific Pride"]
print(f"  EBITDA van tai 9T/26 {vt_ebitda_9t:.1f} (nam hoa {vt_ebitda_9t*4/3:.1f}, dinh); 9T/25 LNG VT {vt9_25:.1f}")
nc_div = net_cash - ct_phai_tra
vb = {}
for k in SC:
    parts = dict(net_cash=nc_div, fso=fso_pv, tankers=tank_ebitda[k] * mult[k], drydock=-dp_suachua, corp=-corp, ships_new=npv[k])
    vb[k] = sum(parts.values()) / shares * 1000
    print(f"  PP-B {k:6s}", {a: round(b) for a, b in parts.items()}, f"=> {vb[k]:,.0f}/cp")
for name, w in SC_ALT.items():
    print(f"  Do nhay trong so {name}: PP-A {sum(w[k]*va[k] for k in SC):,.0f} | PP-B {sum(w[k]*vb[k] for k in SC):,.0f}")
pb_med = 0.7678 * bvps
fv_b = sum(SC[k]*vb[k] for k in SC)
print(f"  PP-B ky vong {fv_b:,.0f}; PB trung vi {pb_med:,.0f}; PP-A ky vong {sum(SC[k]*va[k] for k in SC):,.0f}")
v_both = {k: (nc_div + fso_pv + tank_ebitda[k] * mult[k] - dp_suachua - corp + npv_both[k]) / shares * 1000 for k in SC}
print("  PP-B neu chac chan MUA CA 2:", {k: round(v) for k, v in v_both.items()}, f"ky vong {sum(SC[k]*v_both[k] for k in SC):,.0f}")

# --- San tai san
floor_pre = (nc_div + fso_pv - dp_suachua) / shares * 1000
eq_both = (17.08 + 18.11) * fx / 1e3
floor_post = (nc_div - eq_both + fso_pv - dp_suachua) / shares * 1000
print(f"  San tai san TRUOC capex (tien rong sau co tuc + FSO PV - du phong sua chua, doi tau = 0): {floor_pre:,.0f}/cp")
print(f"  Tien rong sau co tuc - VCSH du dinh chi ({eq_both:,.0f}): {nc_div-eq_both:,.1f} ty = {(nc_div-eq_both)/shares*1000:,.0f}/cp")
print(f"  San tai san SAU capex mua ca 2 (tau moi = dung bang no vay, VCSH bo vao = 0; doi tau cu = 0): {floor_post:,.0f}/cp")
floor_post_tam_ung = floor_post - div25 / shares * 1000
# v2.1 (sua b): san dang DAI - co/khong phan nam 1 FSO vuot run-rate (177 ty) chua hoa giai
dfl = (fso_pv_noexcess - fso_pv) / shares * 1000
print(f"  v2.1 San DAI: truoc capex {floor_pre+dfl:,.0f}-{floor_pre:,.0f}/cp | sau capex mua ca 2 {floor_post+dfl:,.0f}-{floor_post:,.0f}/cp (can duoi = 177 ty FSO nam 1 khong thanh tien)")
# v2.1 (sua f): phai tra co tuc 30/9 = co tuc 2025 (103,70) + ton cu
print(f"  v2.1 Phai tra co tuc 30/9 {ct_phai_tra:.1f} = co tuc 2025 {div25:.1f} + ton cu {ct_phai_tra-div25:.1f}; lich thanh toan 20/10 theo NQ 17 (chua co chung tu sau 20/10)")
print(f"  ... tru them tam ung co tuc 2026 10% (KH, chua chot): {floor_post_tam_ung:,.0f}/cp")
implied = 18750 * shares / 1000 - nc_div - fso_pv + dp_suachua + corp
print(f"  @18.750 thi truong dang dinh gia doi tau dau cu ~{implied:,.0f} ty (so sach Era+Pride+Apollo {342.517675641+495.668133896:,.0f}) - chua tru NPV mua dat")
print(f"  ... sau khi tru NPV mua dat ky vong co so ({npv['co so']:,.0f}): ~{implied - npv['co so']:,.0f} ty")
lo = min(pb_med, vb["xau"]); print(f"  Can duoi dai tin cay (min PB trung vi, PP-B xau) {lo:,.0f}; -15% = {lo*0.85:,.0f}")

print("\n== 7. Thanh khoan + sizing (NAV that) [BQ, data/execution_logs/nav_history_*.csv 28/10] ==")
adv20, adv60 = 33.1, 22.8
for acct, nav in (("SpaceX", 966685020), ("ZaloPay", 919931021)):
    for w in (0.02, 0.04):
        pos = nav * w / 1e9
        print(f"  {acct} NAV {nav/1e9:.3f} ty x {w:.0%} = {pos*1000:.1f} trieu = {pos/adv20:.3%} ADV20 = {pos*1e9/18750:,.0f} cp @18.750")
