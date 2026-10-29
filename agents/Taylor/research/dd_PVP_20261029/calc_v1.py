"""DD PVP 29/10/2026 — moi so lay tu BCTC goc (trang ghi canh), don vi ty VND tru khi ghi khac.
Chay: python3 -I calc.py > out.txt
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
print(f"  Q1 suy ra = H1 soat xet - Q2 BCTC = {h1['lnst']-q2_lnst_bctc:.2f} (BQ Q1 {q1_bq:.2f}; lech {h1['lnst']-q2_lnst_bctc-q1_bq:+.2f} = dieu chinh sau soat xet?)")
q2 = h1["lnst"] - q1_bq
print(f"  LNST quy: Q1 {q1_bq:.1f} | Q2 {q2:.1f} (BCTC Q2 {q2_lnst_bctc}) | Q3 {q3['lnst']:.1f} | Q3/Q2 {q3['lnst']/q2_lnst_bctc-1:+.1%} | Q3 YoY {q3['lnst']/q3_25['lnst']-1:+.1%}")
print(f"  9T LNST YoY {n9['lnst']/n9_25['lnst']-1:+.1%}; LNTT YoY {n9['lntt']/n9_25['lntt']-1:+.1%}")
kh = dict(dt=2700, lntt=270, lnst=216)  # [web] baophapluat 11/02/2026
print(f"  KH 2026: 9T DT {n9['dt']/kh['dt']:.1%} | LNTT {n9['lntt']/kh['lntt']:.1%} | LNST {n9['lnst']/kh['lnst']:.1%}")
print(f"  6T LNST/KH LNST = {h1['lnst']/kh['lnst']:.1%}; 6T LNST/KH LNTT = {h1['lnst']/kh['lntt']:.1%}  <- bao chi '77,6%' la so LNST chia KH LNTT")

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
print(f"  LNTT 9T neu van trich nhu 9T/25 (uoc luong): {n9['lntt']-du_phong_9t25:.1f} (YoY {(n9['lntt']-du_phong_9t25)/n9_25['lntt']-1:+.0%})")

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

print("\n== 6. Dinh gia ==")
px = {"DNSE 13:58 29/10 (san)": 18750, "BQ dong cua 28/10": 20150, "brief Mike (=dong cua 20/10)": 22900}
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

# --- PP-A: PE tren LNST (uoc luong), PE theo lich su PVP; tru NPV tau moi
SC = {"xau": 0.35, "co so": 0.45, "tot": 0.20}  # trong so theo Bobby (CYCLICAL 0,55 / K1-K2 / K3) - uoc luong
ship2 = 56.5 * fx / 1e3
npv = {"xau": -0.30 * ship2, "co so": -0.10 * ship2, "tot": 0.0}  # mua Aframax #2 o dinh, gia tau ve -30/-10% (uoc luong)
lnst27 = {"xau": 190, "co so": 240, "tot": 300}  # uoc luong
pe = {"xau": 4.90, "co so": 6.33, "tot": 8.00}
va = {k: (lnst27[k] * pe[k] + npv[k]) / shares * 1000 for k in SC}
print("  PP-A (PE lich su x LNST 2027 uoc luong + NPV tau #2):", {k: round(v) for k, v in va.items()}, "ky vong", round(sum(SC[k]*va[k] for k in SC)))

# --- PP-B: SOTP
fso_contract = 1163.667442078  # [H1 p34] cam ket cho thue con lai tai 30/6/2026
fso_q3 = seg["FSO_Q3"][0]
fso_pv = {"xau": 0.70 * 0.70, "co so": 0.70 * 0.90, "tot": 0.70}  # PV+thue ~0,70 (uoc luong) x gia thue sau phu luc (xau -30%, co so -10%)
tank_ebitda = {"xau": 300, "co so": 400, "tot": 550}  # uoc luong; 9T/26 nam hoa xem duoi
mult = {"xau": 3.0, "co so": 3.5, "tot": 4.0}  # uoc luong
corp = 52 * 0.8 * 5  # QLDN ~52/nam x (1-thue) x 5 (uoc luong)
vt_ebitda_9t = vt9 + dep9["Pacific Era"] + dep9["Pacific Pride"]
print(f"  EBITDA van tai 9T/26 {vt_ebitda_9t:.1f} (nam hoa {vt_ebitda_9t*4/3:.1f}, dinh); 9T/25 LNG VT {vt9_25:.1f}")
vb = {}
for k in SC:
    parts = dict(net_cash=net_cash - ct_phai_tra, fso=(fso_contract - fso_q3) * fso_pv[k], tankers=tank_ebitda[k] * mult[k],
                 drydock=-dp_suachua, corp=-corp, ship2=npv[k])
    vb[k] = sum(parts.values()) / shares * 1000
    print(f"  PP-B {k:6s}", {a: round(b) for a, b in parts.items()}, f"=> {vb[k]:,.0f}/cp")
print("  PP-B ky vong", round(sum(SC[k]*vb[k] for k in SC)))
floor = (net_cash - ct_phai_tra + (fso_contract - fso_q3) * fso_pv["xau"] - dp_suachua) / shares * 1000
print(f"  San tai san (tien rong + HD FSO kich ban xau - du phong sua chua, doi tau = 0): {floor:,.0f}/cp")
implied = 18750 * shares / 1000 - (net_cash - ct_phai_tra) - (fso_contract - fso_q3) * fso_pv["co so"] + dp_suachua + corp
print(f"  @18.750 thi truong dang dinh gia doi tau dau ~{implied:,.0f} ty (so sach Era+Pride+Apollo {342.517675641+495.668133896:,.0f})")

print("\n== 7. Thanh khoan [BQ] ==")
adv20, adv60 = 33.1, 22.8
for nav in (50e9, 100e9):
    for w in (0.005, 0.01):
        pos = nav * w / 1e9
        print(f"  NAV {nav/1e9:.0f} ty x {w:.1%} = {pos:.2f} ty = {pos/adv20:.1%} ADV20")
