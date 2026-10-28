"""DD DRI — cập nhật sau BCTC hợp nhất Q3/2026 (job Taylor_20261027_042354). Không sửa model.py (bản trước Q3).
Nguồn: [BCTC3] BCTC HN Q3/2026 (ký 22/10) · [SX] BCTC HN bán niên soát xét (AFC, ký 14/08) · [SXKD] báo cáo SXKD
tháng/quý của DRI trên dri.com.vn · [BQ] tav2_bq · [UL] ước lượng. Chạy: python3 model_q3.py"""
import csv, statistics as st
SH, PX = 73.2e6, 14700                       # [BCTN], [BQ ticker] Price 26/10/2026
MCAP = SH*PX/1e9
# ---------- 1. Sản lượng & giá theo quý [SXKD] ----------
T = {"Q1": (5778.69, 10_769_604), "Q2": (9620.16-5778.69, 9620.16*1961.65-10_769_604),
     "Q3": (703.44+941.40+724.282, 1_681_205+2_097_090+1_421_424.05)}   # tấn, USD
DT_VND = {"Q2": 489.918-279.771, "Q3": 43.71+54.52+33.85}      # tỷ: Q2 = H1[SX]−Q1[BQ]; Q3 = DT cao su tháng 7+8+9 [SXKD]
print("1) Sản lượng bán / giá")
for q, (t, usd) in T.items():
    s = f"  {q}: {t:8.1f} t  {usd/t:7.1f} USD/t"
    if q in DT_VND: s += f"  {DT_VND[q]*1e3/t:5.2f} tr đ/t"
    print(s)
q3t = T["Q3"][0]
print(f"  kiểm chéo Q3 tấn: 9T 11.989,49 − H1 9.620,16 = {11989.49-9620.16:.2f} [SXKD]")
q325t = 11989.49/1.1593 - 9620.16/1.5771     # [UL] suy từ +15,93% (9T) và +57,71% (H1) YoY [SXKD]
print(f"  Q3/2025 suy ra: {q325t:,.0f} t, giá {183.602*1e3/q325t:.2f} tr đ/t [UL]")
# ---------- 2. Biên gộp & giá vốn/tấn ----------
DT3, GV3 = 622.002-489.918, 377.401-290.838    # 9T [BCTC3] − H1 soát xét [SX] (bỏ nhiễu quy đổi tỷ giá của cột Q3)
GV2 = 290.838 - 0                                 # H1 soát xét
print(f"\n2) Q3 (9T−H1 soát xét): DT {DT3:.2f} GV {GV3:.2f} biên {1-GV3/DT3:.1%} | GV/t {GV3*1e3/q3t:.2f} tr | "
      f"H1 GV/t {GV2*1e3/9620.16:.2f} tr, biên {1-GV2/489.918:.1%} | 9T GV/t {377.401*1e3/11989.49:.2f}")
print(f"   Q3 in trên BCTC: DT 135,998 GV 89,534 biên {1-89.534/135.998:.1%}")
# ---------- 3. Chấm dự báo DD 55–65 tỷ: phân rã ----------
TAX3 = (5.279+0.503)/31.650
V_dd, P_dd, C_dd = 3750, 47.24*1.18, 33.11   # DD: Q3 3.500–4.000 t, giá 55,7, giá vốn 33,11
SGA_dd = (14.822+23.609)/2; FIN_dd = (19.838-4.710)/2*0.83; OTH_dd = 10/4
P3, C3 = DT3*1e3/q3t, GV3*1e3/q3t
SGA3, FIN3 = 5.093+12.131, 6.345-3.562
def pre(V, P, C, sga, fin, oth): return V*(P-C)/1e3 + oth - sga + fin
dd = pre(V_dd, P_dd, C_dd, SGA_dd, FIN_dd, OTH_dd)
steps = [("sản lượng", dict(V=q3t)), ("giá", dict(P=P3)), ("giá vốn/t", dict(C=C3)), ("BH+QLDN", dict(sga=SGA3)),
         ("tài chính ròng", dict(fin=FIN3)), ("khác", dict(oth=-0.374))]
cur = dict(V=V_dd, P=P_dd, C=C_dd, sga=SGA_dd, fin=FIN_dd, oth=OTH_dd); last = dd
print(f"\n3) DD LNTT Q3 ngầm định {dd:.1f} tỷ (LNST {dd*(1-0.194):.1f}) → thực LNTT 31,65 (in) / 26,36 (9T−H1 soát xét)")
for name, ch in steps:
    cur.update(ch); v = pre(**cur); print(f"   {name:15s} {v-last:+6.1f} tỷ LNTT  → {v:6.1f}"); last = v
print(f"   thưởng/chi phí phải trả: 0 (phải trả NLĐ 28,33→25,75; CP phải trả 0) [BCTC3]")
# ---------- 4. Kịch bản Q4/2026 ----------
print("\n4) Q4/2026 LNST mẹ (OTH sầu riêng 2 tỷ [UL]; FIN = Q3; thuế = Q3 {:.1%})".format(TAX3))
Q4 = {"Bear": (3500, 52.0, 36.5, 25), "Base": (4200, 56.0, 35.0, 15), "Bull": (4900, 59.0, 34.0, 0)}
q4res = {}
for k, (V, P, C, bonus) in Q4.items():
    lt = pre(V, P, C, SGA3+bonus, FIN3, 2.0); q4res[k] = lt*(1-TAX3)
    print(f"   {k}: {V} t × ({P}−{C}) , thưởng trích {bonus} tỷ → LNTT {lt:5.1f} LNST {q4res[k]:5.1f} | FY26 LNST {167.44+q4res[k]:6.1f}")
print(f"   KH ban lãnh đạo [SXKD 9T]: bán 4.168 t @58,97 tr/t, LNTT Q4 22,57 tỷ ⇒ LNST ~{22.57*(1-TAX3):.1f}")
# ---------- 5. Định giá chu kỳ (cùng phương pháp model.py, cập nhật số) ----------
r = [(m, float(p)) for m, p in csv.reader(open('/home/trido/thanhdt/WorkingClaude/data/rubber_monthly.csv')) if m != 'month']
med10 = st.median([p for m, p in r if m >= '2016-10']); med5 = st.median([p for m, p in r if m >= '2021-10'])
rss25 = st.mean([p for m, p in r if m.startswith('2025')])
V, C0, OTHER_GP = 14000, 33.11, 10
SGA = SGA3*4; FIN = FIN3*4*0.83; TAX = TAX3
def lnst(P, C=C0, sga=SGA): return (V*(P-C)/1e3 + OTHER_GP - sga + FIN)*(1-TAX)
RUN = 167.44 + q4res["Base"]                 # FY2026E thay cho run-rate 221,6 của DD
CASH = 72.571 + 271.809; DEBT = 87.039 + 20.598; DIVP = 73.922   # 30/09 [BCTC3]; cổ tức đã ghi nợ, chưa chi
NETC = CASH - DEBT - DIVP; DKR = 40*0.5
print(f"\n5) net cash 30/09 sau cổ tức phải trả {NETC:.1f} tỷ (DD: 191,5) | run-rate FY26E {RUN:.1f} (DD 221,6)")
def scen(name, rss, c, r_, peak, w):
    P = 47.24*rss/rss25; ni = lnst(P, C=c, sga=SGA*0.9); core = ni - NETC*0.05*0.8
    ann = (1-(1+r_)**-28)/r_
    exc = sum((RUN-ni)*0.9/(1+r_)**(t+0.5) for t in range(int(peak))) + (peak % 1)*(RUN-ni)*0.9/(1+r_)**(int(peak)+0.5)
    fv = (core*0.9*ann + exc + NETC + DKR)*1e9/SH
    print(f"   {name}: P {P:4.1f} NI_norm {ni:5.1f} PEcore {(MCAP-NETC)/core:4.1f}x FV {fv:7,.0f} w {w}"); return fv, w
S = [scen("Bear", med10, 32.0, .14, .5, .25), scen("Base", (med10+med5)/2, 32.5, .13, 1.0, .5), scen("Bull", med5, 33.0, .12, 2.0, .25)]
ev = sum(f*w for f, w in S); print(f"   Kỳ vọng {ev:,.0f} đ vs {PX:,} ({ev/PX-1:+.0%})")
# ---------- 6. Bảng 6b ----------
print(f"\n6) CFO 9T/LNST 9T = {125.280/167.440:.2f}x | thành phẩm 30/09 138,81 tỷ (30/06 64,99) | "
      f"CLTG VCSH Q3 {-370.842+355.0:+.1f} tỷ | Dakruco 40 tỷ (không đổi)")
print(f"   tồn kho thành phẩm tăng ~{(9590-5504.22)-q3t:,.0f} t trong Q3 [UL: chế biến Q3 − bán Q3, SXKD]")
