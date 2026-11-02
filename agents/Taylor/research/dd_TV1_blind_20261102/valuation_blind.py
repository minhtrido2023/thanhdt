"""TV1 (EVNPECC1) — GIÁ TRỊ NỘI TẠI DỰNG MÙ (job Taylor_20261102_144349, 02/11/2026).
GIAO THỨC MÙ: file này KHÔNG chứa và KHÔNG đọc giá cổ phiếu / vốn hoá / P/E-P/B-yield của TV1.
Tái lập: python3 -I valuation_blind.py > valuation_blind_out.txt
Nhãn: [FY25 trX]/[H1 trX]/[Q3 trX] = BCTC gốc trong ../dd_TV1_20261102/src (số đã trích ở REPORT §2–§7 và calc/valuation.py);
[PA2018] = PECC1 "Báo cáo phương án bán toàn bộ tài sản NMTĐ Sông Bung 5" 8/2018 (qua ../tv1_sb5_ppa_price_20261013/README.md);
[TT38] = TT 38/2026/TT-BXD Phụ lục VIII (datafiles.chinhphu.vn, đọc 02/11/2026); [BOBBY] = sector read 28/10/2026 (mù);
[UL] = giả định tự đặt (kèm căn cứ). Đơn vị: tỷ đồng, đ/kWh, triệu kWh (GWh)."""
import itertools

SH = 26_691_319                    # cp lưu hành [Q3 tr.5: vốn góp 266.913.190.000/10.000]
def ps(x): return x * 1e9 / SH     # tỷ -> đ/cp
TAX, KTPL = 0.20, 0.20             # thuế TNDN; quỹ khen thưởng phúc lợi = 30,1/150,2 LNST 2025 [H1 tr.30]
KE_BAND = (0.123, 0.1285, 0.134)   # Ke nội địa β1,1 (khung fleet 30/10, due-diligence SKILL); độ nhạy 10–14%
KE_C = KE_BAND[1]

def irr(cfs, lo=-0.5, hi=1.0):
    f = lambda r: sum(c / (1 + r) ** t for t, c in enumerate(cfs))
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) > 0: lo = m
        else: hi = m
    return m

def pv(cfs, r, t0=1):   # cfs[0] at t0
    return sum(c / (1 + r) ** (t0 + i) for i, c in enumerate(cfs))

print("=" * 100)
print("A. THUỶ ĐIỆN SÔNG BUNG 5 (57 MW, 100%, thuê đất đến 08/2059)")
print("=" * 100)
# ---- A0. Hiệu chuẩn 2025 [FY25 tr.34: DT 261,600 / KQ bộ phận 165,055 / KH 38,143; BCTN25 tr.7 Q 236,6; tr.24 thuế TN 28,66]
Q25, DT25, KQ25, DA25, TN25 = 236.6, 261.600, 165.055, 38.143, 28.66
DVMTR = 36.0                                    # đ/kWh [UL: mức DVMTR thuỷ điện ~36 đ/kWh]
pass25 = TN25 + Q25 * DVMTR / 1000             # pass-through: EVN trả thêm ngoài giá hợp đồng
p_net25 = (DT25 - pass25) / Q25 * 1000
om25 = (DT25 - KQ25) - pass25 - DA25          # chi phí tiền mặt bộ phận
print(f"2025: pass-through {pass25:.1f} ⇒ giá ròng {p_net25:.0f} đ/kWh; O&M tiền mặt {om25:.1f} tỷ ({om25/Q25*1000:.0f} đ/kWh)")

# ---- A1(iii). IRR dự án luỹ kế: TMĐT 1.372 (vốn tự có 411,6 + vay 960,4) [baodauthau post58787/145371, qua peer_hydro_prices.md §4]
TMDT = 1372.0
inv = {2009: 0.15, 2010: 0.25, 2011: 0.35, 2012: 0.25}     # [UL] phân bổ giải ngân; COD 2012
# Sản lượng thực [sb5_price_series.csv]: đọc được 2013–17, 2021–23, 2025; 2018 = 192,79/0,95 [UL];
# 2019+2020 suy từ bình quân công ty 2013–2023 = 175,3 [PECC1 7/2024] ⇒ tổng 2 năm; 2024 = 215,94/1,106 [UL]; 2026 = 9T+Q4 [UL]
Qh = {2013: 174.0, 2014: 125.93, 2015: 151.71, 2016: 169.50, 2017: 250.02, 2018: 203.0, 2021: 197.37, 2022: 258.89, 2023: 187.0}
Qh_1923 = 175.3 * 11 - sum(Qh[y] for y in range(2013, 2024) if y in Qh)
Qh[2019] = Qh[2020] = Qh_1923 / 2
Qh[2024], Qh[2025], Qh[2026] = 195.0, Q25, 190.0
print(f"Sản lượng suy 2019, 2020 = {Qh[2019]:.0f} mỗi năm (từ BQ 2013–23 175,3) — rất khô; 2015–2025 BQ {sum(Qh[y] for y in range(2015,2026))/11:.0f}; 2021–25 BQ {sum(Qh[y] for y in range(2021,2026))/5:.0f}")
def p_hist(y): return 939.0 if y <= 2017 else p_net25        # giá HĐ 938,78–940,76 2014–17 [PA2018]; sau đó ≈ giá ròng 2025
def om(y): return om25 * 1.025 ** (y - 2025)                 # trượt 2,5%/năm (TT 12/2025)
MCAPEX = 5.0                                                 # capex duy trì [UL; ~1,2% TMĐT = 16,5 là trần định mức TT12 gồm sửa chữa lớn]
def da(y): return 38.0 if y <= 2039 else 0.0                 # TSCĐ ròng 506 (30/6/26) / 38 ⇒ hết ~2039 [H1 tr.5]
def fcf_unlev(y, p, q):
    rev = q * p / 1000
    ebit = rev - om(y) - da(y)
    return ebit - max(ebit, 0) * TAX + da(y) - MCAPEX * 1.025 ** max(0, y - 2025)

LIFE_END = 2052   # đời sống kinh tế 40 năm (TT 12/2025 Phụ lục) từ 2013
Q_P50 = 195.0     # [UL] P50: giữa BQ dài hạn công ty (175,3, gồm 2 năm rất khô) và BQ 2021–25 (215); độ nhạy 175/215/236
def life_cfs(p_fut, q_fut=Q_P50, end=LIFE_END):
    cfs = []
    for y in range(2009, end + 1):
        c = -TMDT * inv.get(y, 0.0)
        if y >= 2013:
            q = Qh.get(y, q_fut); p = p_hist(y) if y <= 2026 else p_fut
            c += fcf_unlev(y, p, q)
        cfs.append(c)
    return cfs
irr_hist = irr([c for c in life_cfs(p_net25)[:2026 - 2009 + 1]] + [0])
print(f"\nIRR dự án (không đòn bẩy, sau thuế) nếu DỪNG ở 2026 (không giá trị còn lại): {irr_hist:.1%}")
for p in (949, 800, 600, 500, 400):
    print(f"  IRR toàn đời 2013–{LIFE_END} nếu giá ròng 2027+ = {p}: {irr(life_cfs(p)):.2%}")
def solve_p(target, end=LIFE_END):
    lo, hi = 0.0, 3000.0
    for _ in range(100):
        m = (lo + hi) / 2
        if irr(life_cfs(m, end=end)) < target: lo = m
        else: hi = m
    return m
p12 = solve_p(0.12); p10 = solve_p(0.10)
print(f"Giá ròng 2027–{LIFE_END} để IRR toàn đời = 12% (TRẦN TT 12/2025): {p12:.0f} đ/kWh; = 10%: {p10:.0f}")
print("  ⇒ Ở giá hiện hành ~949, IRR toàn đời", "≤ 12%: trần IRR KHÔNG buộc hạ giá" if p12 >= 949 else "> 12%: trần IRR có thể là căn cứ hạ giá")

# ---- A1(iii-b). GIÁ SÀN CHỦ SỞ HỮU CÒN VẬN HÀNH (Đ.14 TT 12: bù giá trị còn lại + chi phí SXKD + lợi nhuận hợp lý)
RAB27 = 506.3 - 38.0 * 1.5          # TSCĐ ròng 30/6/26 [H1 tr.5 mã 221] − 1,5 năm khấu hao ⇒ ~1/2027
N_REM = LIFE_END - 2026
def floor_price(r_pre, q=Q_P50, rab=RAB27):
    ann = rab * r_pre / (1 - (1 + r_pre) ** -N_REM)            # thu hồi + lợi nhuận trên giá trị còn lại (trước thuế)
    om_avg = om(2027) * 1.25                                    # O&M bình quân đời còn lại (trượt 2,5%/năm ~ +25%) [UL]
    rep = TMDT * 0.012 * 0.5                                    # sửa chữa lớn ~ nửa định mức 1,2% TMĐT [UL; TT12 PL]
    return (ann + om_avg + rep) / q * 1000
print(f"\nGiá trị còn lại (RAB) ~1/2027 ≈ {RAB27:.0f} tỷ; đời còn {N_REM} năm")
for r in (0.08, 0.10, 0.12, 0.15):
    print(f"  Giá sàn bù chi phí + sửa chữa + lợi nhuận {r:.0%}/năm trước thuế trên RAB: {floor_price(r):.0f} đ/kWh (Q{Q_P50:.0f}); Q175 {floor_price(r,175):.0f}")
print(f"  Đối chiếu: dự thảo HĐ sửa đổi 05/2018 [PA2018]: bậc 243,66 + O&M 75,75×1,025^9={75.75*1.025**9:.0f} ⇒ {243.66+75.75*1.025**9:.0f} đ/kWh;"
      f" nếu O&M theo định mức TT12 (nhân công 0,8% + sửa chữa lớn 1,2% TMĐT = {TMDT*0.02:.1f} tỷ ⇒ {TMDT*0.02*1.025**8/Q_P50*1000:.0f} đ/kWh): {243.66+TMDT*0.02*1.025**8/Q_P50*1000:.0f}")
cash_be = (om(2027) + MCAPEX) / Q_P50 * 1000
acct_be = (om(2027) + 38.0) / Q_P50 * 1000
print(f"  Hoà vốn TIỀN MẶT {cash_be:.0f} đ/kWh; hoà vốn KẾ TOÁN (còn khấu hao đến 2039) {acct_be:.0f} đ/kWh")

# ---- Hành lang & kịch bản giá ròng 2027+ (chưa gồm thuế TN/DVMTR — pass-through)
PRICE = {"P1_giu_HD_949": 949.0, "P2_thoa_thuan_600": 600.0, "P3_thoa_thuan_520": 520.0, "P4_san_kinh_te_440": 440.0}
PROB = {"P1_giu_HD_949": 0.15, "P2_thoa_thuan_600": 0.30, "P3_thoa_thuan_520": 0.35, "P4_san_kinh_te_440": 0.20}
# Căn cứ [UL]: P1 — chưa thấy văn bản hạ bậc nào được thực thi (2022 đã qua mà không hạ); EVN không được đơn phương hạ [LEGAL_PPA].
#   Nhưng chính công ty viết "giá điện của nhà máy TĐ Sông Bung 5 sụt giảm" (BCTN 2025 tr.38) ⇒ 0,15.
#   P2/P3 — dải lãnh đạo nêu qua KBSV 17/04/2026 (500–600, CHƯA kiểm bản gốc) nằm trong hành lang kinh tế; tách 600/520 vì
#   giá sàn kinh tế ở lợi nhuận 12–15% trên RAB rơi đúng vùng 480–560.  P4 — sàn kinh tế (lợi nhuận ~10% trên RAB).
#   Mức 340 của dự thảo 2018 nằm DƯỚI hoà vốn kế toán và chưa từng được áp ⇒ không làm kịch bản; chỉ đưa vào độ nhạy.
assert abs(sum(PROB.values()) - 1) < 1e-9
pw = sum(PRICE[k] * PROB[k] for k in PRICE)
print(f"\nKịch bản giá ròng 2027+: " + ", ".join(f"{k} p={PROB[k]:.2f}" for k in PRICE) + f" ⇒ kỳ vọng {pw:.0f} đ/kWh")

# ---- A2. DCF thuỷ điện 2027–2059 (thuê đất 08/2059; sau 2052 giá theo Đ.13 = bù chi phí + LN hợp lý ⇒ giữ mức kịch bản [UL])
def hydro_fcfe(p, q, years=range(2027, 2060), ktpl=KTPL):
    out = []
    for y in years:
        rev = q * p / 1000
        ebit = rev - om(y) - da(y) - 8.0 * 1.025 ** (y - 2026)    # 8 = chi phí chung phân bổ cho thuỷ điện [UL, như valuation.py]
        ni = ebit - max(ebit, 0) * TAX
        frac = 7 / 12 if y == 2059 else 1.0
        out.append((ni * (1 - ktpl) + da(y) - MCAPEX * 1.025 ** (y - 2025)) * frac)
    return out
def hydro_ni(p, q, y=2028):
    ebit = q * p / 1000 - om(y) - da(y) - 8.0 * 1.025 ** (y - 2026)
    return ebit - max(ebit, 0) * TAX
T0 = 2 / 12   # định giá tại 02/11/2026; dòng 2027 nhận ~giữa 2027 ⇒ chiết khấu t = 0,67, 1,67… [UL: quy ước giữa năm]
def pv_mid(cfs, r): return sum(c / (1 + r) ** (T0 + i + 0.5) for i, c in enumerate(cfs))
print("\nGiá trị thuỷ điện (PV FCFE sau KTPL, 2027–08/2059, tỷ) — Ke 12,85% | 12,3% | 13,4%:")
print(f"{'kịch bản':22s} {'LNST28 Q195':>11s} {'Q175':>8s} {'Q195':>8s} {'Q215':>8s} {'Q236':>8s}  {'Q195 Ke12,3':>11s} {'Ke13,4':>8s}")
HV = {}
for k, p in PRICE.items():
    row = {q: pv_mid(hydro_fcfe(p, q), KE_C) for q in (175, 195, 215, 236.6)}
    HV[k] = row
    print(f"{k:22s} {hydro_ni(p,195):11.1f} {row[175]:8.0f} {row[195]:8.0f} {row[215]:8.0f} {row[236.6]:8.0f}  "
          f"{pv_mid(hydro_fcfe(p,195),0.123):11.0f} {pv_mid(hydro_fcfe(p,195),0.134):8.0f}")
hyd_w = sum(HV[k][195] * PROB[k] for k in PRICE)
print(f"Kỳ vọng theo xác suất giá (Q195, Ke 12,85%): {hyd_w:.0f} tỷ = {ps(hyd_w):,.0f} đ/cp")
print(f"Độ nhạy dự thảo 2018 (340): Q195 {pv_mid(hydro_fcfe(340,195),KE_C):.0f} tỷ")
print(f"Đối chiếu tài sản: AASC 2018 thẩm định 1.686 tỷ (Ke 7%); đấu giá 2019–21 khởi điểm 1.688→1.351,7 tỷ, KHÔNG có người đăng ký [PA2018; baodauthau]")
# Mốc trễ: mỗi năm giữ giá HĐ thêm sau 2026 (Q4/2026 đã gần xong ở giá cũ) ⇒ +ΔLNST×(1-KTPL)
for k in ("P2_thoa_thuan_600", "P3_thoa_thuan_520"):
    d = (hydro_ni(949, 195, 2027) - hydro_ni(PRICE[k], 195, 2027)) * (1 - KTPL) / (1 + KE_C) ** (T0 + 0.5)
    print(f"  Mỗi năm trễ hạ bậc (giữ 949 thay {PRICE[k]:.0f}) cộng ≈ {d:.0f} tỷ = {ps(d):,.0f} đ/cp")

# ---- A3. Điện mặt trời nổi 46 MWp + 5 MW BESS (~800 tỷ, ~90 tỷ DT/năm) [baodauthau 27/06/2025; ĐHCĐ 30/04/2026]
capex_s, rev_s = 800.0, 90.0
om_s = capex_s * 0.015                                    # [UL] O&M 1,5% capex
s_cfs = [-capex_s] + [(rev_s * 0.995 ** t - om_s) - max(rev_s * 0.995 ** t - om_s - capex_s / 20, 0) * TAX for t in range(25)]
print(f"\nA3. ĐMT nổi: IRR dự án (25 năm, suy giảm 0,5%/năm, O&M 1,5%) ≈ {irr(s_cfs):.1%} < Ke {KE_C:.2%} ⇒ NPV@Ke {pv(s_cfs[1:],KE_C)-capex_s:+.0f} tỷ; "
      "KHÔNG tính (chưa vào quy hoạch Đà Nẵng mới, chưa có cơ chế giá). Chỉ có giá trị dương nếu capex ≲ "
      f"{pv(s_cfs[1:],KE_C):.0f} tỷ hoặc giá bán cao hơn.")

print("\n" + "=" * 100)
print("B. TƯ VẤN KS-TK ĐIỆN — DỰNG TỪ ĐƯỜNG ỐNG")
print("=" * 100)
# ---- B0. Số thật: DT tư vấn = DT thuần − DT thuỷ điện [bq_fin cộng 4 quý; FY25 tr.34-35]
dt_tot = {2023: 96.43 + 91.10 + 120.60 + 225.14, 2024: 78.08 + 107.92 + 148.06 + 228.10, 2025: 112.59 + 128.69 + 149.31 + 318.03}
dt_hyd = {2023: 214.59, 2024: 215.941, 2025: DT25}
dt_con = {y: dt_tot[y] - dt_hyd[y] for y in dt_tot}
gp_con = {2024: 85.728, 2025: 80.841}                       # KQ bộ phận tư vấn [FY25 tr.34-35]
ovh = {2024: 74.878, 2025: 44.084}                          # chi phí chung không phân bổ
ebit_con = {y: gp_con[y] - (ovh[y] - 8.0) for y in gp_con}
for y in dt_con:
    s = f"  {y}: DT tư vấn {dt_con[y]:.1f}"
    if y in gp_con: s += f", LN gộp {gp_con[y]:.1f} ({gp_con[y]/dt_con[y]:.1%}), EBIT sau chi phí chung {ebit_con[y]:.1f} ({ebit_con[y]/dt_con[y]:.1%})"
    print(s)
# 9T/2026: DT 446,9; DT thuỷ điện H1 81,20 + Q3 ~41,2 (proxy thuế TN) [REPORT §4]; LN gộp 9T 36,4%×446,9
con9 = 446.9 - (81.20 + 41.2); con9_25 = 390.6 - (DT25 - 123.3)
gp9 = 0.364 * 446.9 - 64.8 - 5.7        # trừ LN gộp thuỷ điện 9T ~64,8 [REPORT §4] và hoàn nhập HTK 5,7 (một lần)
ebit9_B = gp9 - (42.4 - 6.0); ebit9_A = ebit9_B - 19.2
print(f"  9T/26: DT tư vấn {con9:.1f} (9T/25 {con9_25:.1f}, {con9/con9_25-1:+.0%}); LN gộp lõi {gp9:.1f} ({gp9/con9:.1%}); "
      f"EBIT lõi {ebit9_A:.1f}–{ebit9_B:.1f} ({ebit9_A/con9:.0%}–{ebit9_B/con9:.0%}) [A: hoàn nhập phải thu 19,2 trong QLDN | B: không]")
print(f"  Hợp đồng ký mới 2025: 835,1 tỷ (+~198%, cao nhất lịch sử) [baodauthau post192515] vs DT tư vấn 2025 {dt_con[2025]:.0f} ⇒ book-to-bill {835.1/dt_con[2025]:.2f}; "
      "người mua trả trước 104,4 → 138,7 (+33%) [Q3 tr.4]")
print(f"  Định mức 2026 cho mảng 2026 KH: 641,5 − 187 = {641.5-187:.1f} (công ty: 'thận trọng', chỉ HĐ hiện có) [ĐHCĐ 30/04/2026]")

# ---- B1. Tỷ lệ phí theo định mức [TT38 PL VIII, công trình công nghiệp (năng lượng), cấp I]
# TKKT 1.000–2.000 tỷ chi phí xây dựng: 1,28→1,09%; BVTC = 60% TKKT ⇒ thiết kế 2 bước ≈ 1,74–2,05% CHI PHÍ XÂY DỰNG;
# FS (Bảng 2.3, CN, XD+TB 1.000–5.000): 0,404–0,248%; giám sát thi công (Bảng 2.24, CN 1.000–5.000): 0,82–0,64%.
# Đối chiếu gói thật [BOBBY §3]: 500kV Krông Buk–Tây Ninh 1 gói KS+TKKT+BVTC+HSMT 158,84 / TMĐT 14.060 = 1,13%; Thốt Nốt–Đức Hòa
# gói 1+2 (76,4)/6.800 = 1,12% (+ gói 3 giám sát KS 4,0).  ⇒ phần KS-TK-FS mà nhóm PECC nắm ≈ 1,1–1,3% TMĐT; cả giám sát/thẩm tra/
# QLDA thuê ngoài ≈ 2–3% TMĐT (BOBBY [NỀN]). Dùng f = 1,2% (KS-TK-FS) + 0,4% (giám sát/khác mà nhóm PECC thắng) = 1,6% [UL].
F_RATE = 0.016
capex_evn = {2024: 112_890, 2025: 125_778}                  # nghìn tỷ → tỷ [BOBBY §1]
pool25 = capex_evn[2025] * F_RATE
share25 = dt_con[2025] / pool25
print(f"\nB1. Bể phí tư vấn khối EVN 2025 ≈ capex {capex_evn[2025]:,} × {F_RATE:.1%} = {pool25:,.0f} tỷ ⇒ thị phần hiệu dụng TV1 ≈ {share25:.0%} "
      "(chưa trừ khách ngoài EVN: Tanahu-Nepal, PVN/PTSC — nên thị phần trong EVN thấp hơn chút)")
# ---- B2. Đường ống 2026–2030 (tư vấn đi TRƯỚC capex 1–3 năm ⇒ DT tư vấn năm t theo capex t+1..t+2)
# Neo: EVN 2026–2030 ~830.000 tỷ (vietnamplus) ⇒ BQ 166k/năm; bản tin EVN số 12/2026: ~5 tỷ USD/năm (~130k); KH 2026 123k [BOBBY].
# Phân bổ đặc thù TV1 (thuỷ điện MR Sơn La 800MW, Lai Châu 800MW, Tuyên Quang MR 120MW [HĐ 81,7 tỷ, 62 tháng], Sông Ba Hạ, An Vương,
# Quảng Trị; 500kV AC/HVDC; FS lại NT1 cùng PECC2+Viện NL; ĐGNK cùng PTSC) [ĐHCĐ 30/04/2026; vietnamfinance 11/2025]
CON26 = con9 + 195.0          # Q4/26 ≈ Q4/25 (318,03 − 123,3) [UL]; KH công ty 454,5 thấp hơn (thận trọng)
SCN = {   # (tăng DT 2027–2030 /năm, biên EBIT bền, thị phần ghi chú) [UL] — căn cứ ở INTRINSIC.md §B
    "C_thap":  dict(g=0.03, m=0.08, note="capex EVN đi ngang ~123–130k (ADMIN_GATED, BOBBY F1 P=0,55); thị phần giữ; biên ~TB 2024–25"),
    "C_giua":  dict(g=0.08, m=0.11, note="capex EVN ~70% KH 830k (BQ ~145k, +15% mức) + trượt giá XD 3% + dịch cơ cấu sang thuỷ điện MR/500kV; biên 2025–9T26"),
    "C_cao":   dict(g=0.14, m=0.14, note="KH 830k đạt đủ + NT1 FS/khảo sát + HVDC; đòn bẩy chi phí chung; biên 9T26 trường hợp B"),
}
WC_INT = 0.40      # vốn lưu động tăng thêm / ΔDT: (phải thu ròng 319 + dở dang ròng 95 − trả trước 139)/DT ~520 ≈ 0,53; dùng 0,40 biên [UL]
G_TERM = 0.05      # g dài hạn (≤ GDP danh nghĩa VN dài hạn ~8–10%; chọn thấp vì capex lưới theo chu kỳ) [UL]
def consult(s, ke=KE_C, ktpl=KTPL, g_term=G_TERM, shock=None):
    p = SCN[s]; rev = CON26; prev_eff = CON26; out = []; nis = []
    for i, y in enumerate(range(2027, 2033)):
        g = p["g"] if y <= 2030 else (p["g"] + g_term) / 2
        rev_new = rev * (1 + g)                                   # đường DT không sốc (hồi phục về đây khi hết cấm thầu)
        r_eff = rev_new * (shock[i] if shock and i < len(shock) else 1.0)
        ebit = r_eff * p["m"]
        if r_eff < rev_new:          # mất DT: một nửa chi phí trực tiếp của phần DT mất là cố định (nhân sự) [UL]
            ebit -= (rev_new - r_eff) * (1 - p["m"]) * 0.5
        ni = ebit * (1 - TAX)
        fcfe = ni * (1 - ktpl) - WC_INT * (r_eff - prev_eff) - 5.0
        out.append(fcfe); nis.append(ni); rev = rev_new; prev_eff = r_eff
    ni_t = rev * (1 + g_term) * p["m"] * (1 - TAX)
    fcfe_t = ni_t * (1 - ktpl) - WC_INT * rev * g_term - 5.0
    tv = fcfe_t / (ke - g_term)
    v = pv_mid(out, ke) + tv / (1 + ke) ** (T0 + len(out))
    ronic = ni_t * (1 - ktpl) / (WC_INT * rev * g_term * 1.0)
    return v, nis, tv / (1 + ke) ** (T0 + len(out)) / v, ronic
print(f"\nDT tư vấn 2026E {CON26:.0f} [UL] | g dài hạn {G_TERM:.0%} | ΔVLĐ {WC_INT:.0%}×ΔDT | Ke {KE_C:.2%}")
CV = {}
for s in SCN:
    v, nis, tw, ron = consult(s)
    CV[s] = v
    print(f"  {s:8s}: LNST 2027 {nis[0]:5.1f} · 2030 {nis[3]:5.1f} · 2032 {nis[5]:5.1f} ⇒ giá trị {v:6.0f} tỷ = {ps(v):7,.0f} đ/cp "
          f"(terminal {tw:.0%}; RONIC sau KTPL {ron:.0%} ≥ Ke) — {SCN[s]['note']}")
P_CON = {"C_thap": 0.30, "C_giua": 0.50, "C_cao": 0.20}     # [UL] BOBBY: P(khối lượng 2027 > 2025) ≈ 0,65; F1 0,55
con_w = sum(CV[s] * P_CON[s] for s in SCN)
print(f"  Kỳ vọng tư vấn: {con_w:.0f} tỷ = {ps(con_w):,.0f} đ/cp")
print("  Độ nhạy Ke × g (C_giua):")
for ke in (0.10, 0.123, 0.1285, 0.134, 0.14):
    print("    Ke {:.2%}: ".format(ke) + "  ".join(f"g{g:.0%} {consult('C_giua', ke=ke, g_term=g)[0]:5.0f}" for g in (0.03, 0.05, 0.07)))

print("\n" + "=" * 100)
print("C. TIỀN & BẢNG CÂN ĐỐI 30/09/2026 [Q3 tr.1-5, 21-24; H1 tr.27]")
print("=" * 100)
cash, htm, loans, div_pay, int_pay = 30.735, 167.815, 129.880, 43.154, 64.253
ni9 = 124.636
ktpl_9t = ni9 * KTPL                    # KTPL sẽ trích từ LNST 2026 (đã nằm trong tiền) ⇒ rò rỉ khỏi cổ đông
oneoff = 31.9                           # khác ròng Q3 (đã thành tiền?/hoàn nhập phi tiền 21,5) — KHÔNG cộng thêm (đã trong BCĐKT)
q4_ni = 50.0                            # LNST Q4/2026 [UL: thuỷ điện ~37 ở giá cũ + tư vấn ~13]; tiền vào trước 01/2027
net_adj = cash + htm - loans - div_pay - int_pay
print(f"Tiền+HTM {cash+htm:.1f} − vay {loans:.1f} (cá nhân/bên liên quan 118,8) − cổ tức phải trả {div_pay:.1f} − lãi vay cá nhân phải trả {int_pay:.1f} = {net_adj:+.1f}")
print(f"Nợ tranh chấp Long+Ngãi 127,63 (gốc+lãi) ĐÃ nằm trong sổ ⇒ khấu trừ theo sổ (xác suất phải trả: vụ Ngãi phúc thẩm thua 26/08/2026; Long đang kiện) — không trừ thêm")
print(f"KTPL trên LNST 9T/26: −{ktpl_9t:.1f}; LNST Q4/26 sau KTPL: +{q4_ni*(1-KTPL):.1f} [UL]")
BS = net_adj - ktpl_9t + q4_ni * (1 - KTPL)
print(f"⇒ Điều chỉnh tiền ròng cho cổ đông: {BS:+.1f} tỷ = {ps(BS):+,.0f} đ/cp")
print(f"  GIỚI HẠN: số dư quỹ KTPL chưa chi (trích 30,1 từ LNST 2025 trong H1/26) chưa tách được từ BCTC Q3 — nếu còn nguyên: {ps(-30.1):+,.0f} đ/cp")
# Độ nhạy IRR theo giả định sản lượng 2019–2020 (suy ra, không đọc được)
_q = Qh[2019]; Qh[2019] = Qh[2020] = 175.0
print(f"  (A1 phụ) nếu 2019–20 = 175 thay vì {_q:.0f}: IRR toàn đời ở 949 = {irr(life_cfs(949)):.2%}; giá cho IRR 12% = {solve_p(0.12):.0f}")
Qh[2019] = Qh[2020] = _q

print("\n" + "=" * 100)
print("F. SOTP — GIÁ TRỊ NỘI TẠI/CP (mù giá; KHÔNG có xác suất vụ án trong tâm)")
print("=" * 100)
def sotp(pk, q, ck, ke=KE_C, ktpl=KTPL):
    h = pv_mid(hydro_fcfe(PRICE[pk], q, ktpl=ktpl), ke)
    c = consult(ck, ke=ke, ktpl=ktpl)[0]
    return h + c + BS
print(f"{'giá PPA / tư vấn':22s}" + "".join(f"{c:>18s}" for c in SCN))
grid = {}
for pk in PRICE:
    line = f"{pk:22s}"
    for ck in SCN:
        v = sotp(pk, Q_P50, ck); grid[(pk, ck)] = v
        line += f"{v:8.0f} ={ps(v):7,.0f}"
    print(line)
centre = sum(grid[(pk, ck)] * PROB[pk] * P_CON[ck] for pk in PRICE for ck in SCN)
mid_core = sotp("P3_thoa_thuan_520", Q_P50, "C_giua")
vals = sorted((ps(v), PROB[pk] * P_CON[ck]) for (pk, ck), v in grid.items())
def quant(qt):
    acc = 0
    for v, w in vals:
        acc += w
        if acc >= qt: return v
print(f"\nTÂM (kỳ vọng xác suất giá × đường ống, Q{Q_P50:.0f}, Ke {KE_C:.2%}): {centre:.0f} tỷ = {ps(centre):,.0f} đ/cp")
print(f"Ô trung vị (P3 520 × C_giua): {ps(mid_core):,.0f} đ/cp")
print(f"Phân vị 20/50/80 của lưới 12 ô (trọng số): {quant(0.2):,.0f} / {quant(0.5):,.0f} / {quant(0.8):,.0f} đ/cp")
print(f"Toàn dải lưới: {min(v for v,_ in vals):,.0f} – {max(v for v,_ in vals):,.0f} đ/cp")
print(f"Cấu phần tâm: thuỷ điện {ps(hyd_w):,.0f} + tư vấn {ps(con_w):,.0f} + tiền ròng điều chỉnh {ps(BS):+,.0f}")

print("\nĐộ nhạy tâm (đ/cp):")
def centre_with(ke=KE_C, ktpl=KTPL, q=Q_P50):
    return ps(sum(sotp(pk, q, ck, ke=ke, ktpl=ktpl) * PROB[pk] * P_CON[ck] for pk in PRICE for ck in SCN))
print("  Ke: " + "  ".join(f"{k:.1%} {centre_with(ke=k):,.0f}" for k in (0.10, 0.123, 0.1285, 0.134, 0.14)))
print("  KTPL: " + "  ".join(f"{k:.0%} {centre_with(ktpl=k):,.0f}" for k in (0.10, 0.15, 0.20, 0.25)))
print("  Sản lượng: " + "  ".join(f"Q{q:.0f} {centre_with(q=q):,.0f}" for q in (175, 195, 215, 236.6)))
print("  Giá PPA (C_giua, Q195): " + "  ".join(f"{p} {ps(pv_mid(hydro_fcfe(p,195),KE_C)+CV['C_giua']+BS):,.0f}" for p in (340, 440, 520, 600, 750, 949)))

print("\nGIÁ TRỊ TIẾP CẬN QUA CỔ TỨC (cổ đông thiểu số không quyết định phân phối):")
# Mô phỏng 10 năm: LNST tâm (P3×C_giua) ; cổ tức = payout × LNST ; phần giữ lại không cần cho VLĐ/capex nằm thành tiền gửi
# lãi 5,5%/năm trước thuế [UL: lãi tiền gửi 9T/26 ~5–6% REPORT §3]; năm 10: giá trị = giá trị hoạt động khi đó (ước bằng tâm SOTP
# tăng theo g) + tiền tích luỹ theo sổ (KHÔNG chiết khấu tuỳ ý) ⇒ rò rỉ = chênh lợi suất tiền gửi sau thuế vs Ke trên tiền bị giữ.
def leakage(payout, years=10, dep=0.055):
    pk, ck = "P3_thoa_thuan_520", "C_giua"
    con_nis = consult(ck)[1]
    trapped = 0.0; loss = 0.0
    for i in range(years):
        y = 2027 + i
        ni = hydro_ni(PRICE[pk], Q_P50, y) + (con_nis[i] if i < len(con_nis) else con_nis[-1] * 1.05 ** (i - 5))
        need = WC_INT * (CON26 * 0.08) + 5 + 5          # VLĐ + capex hai mảng [UL]
        free = ni * (1 - KTPL) - need
        retained = max(free - payout * ni, 0)
        trapped += retained
        loss += trapped * (KE_C - dep * (1 - TAX)) / (1 + KE_C) ** (i + 1)
    return loss
for po in (0.27, 0.40, 0.60):
    L = leakage(po)
    print(f"  payout {po:.0%}: PV rò rỉ do tiền bị giữ ở lãi tiền gửi ≈ {L:.0f} tỷ = {ps(L):,.0f} đ/cp ⇒ giá trị tiếp cận ≈ {ps(centre - L):,.0f} đ/cp")
print("  (payout 27% = FY2025 thực; KTPL 20% đã trừ ở mọi dòng. Không áp chiết khấu thanh khoản/thiểu số tuỳ ý.)")

print("\n" + "=" * 100)
print("D. ĐỘ NHẠY VỤ ÁN (TÁCH KHỎI CƠ SỞ — không vào tâm)")
print("=" * 100)
base_c = consult("C_giua")[0]
for lab, shock in [("cấm thầu EVN 3 năm: DT tư vấn −50% 2027–29", [0.5, 0.5, 0.5]),
                   ("cấm thầu EVN 5 năm: DT −50% 2027–31", [0.5] * 5),
                   ("cấm 3 năm, mất 70% DT", [0.3, 0.3, 0.3])]:
    v = consult("C_giua", shock=shock)[0]
    print(f"  {lab}: tư vấn {base_c:.0f} → {v:.0f} (Δ {ps(v-base_c):+,.0f} đ/cp)")
for amt in (20, 50, 100):
    print(f"  Buộc nộp lợi bất chính/bồi thường {amt} tỷ (2027): Δ {ps(-amt/(1+KE_C)):+,.0f} đ/cp")
