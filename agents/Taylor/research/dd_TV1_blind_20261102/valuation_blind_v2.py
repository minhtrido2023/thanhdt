"""TV1 (EVNPECC1) — GIÁ TRỊ NỘI TẠI v2 (job Taylor_20261102_152306, 02/11/2026).
Hiệu chỉnh CƠ HỌC theo phản biện độc lập chạy mù (SKEPTIC_BLIND_20261102.md: B1, B2, B3, N1–N4); không hiệu chuẩn theo giá.
Giữ nguyên mọi giả định khác của valuation_blind.py (đã khoá md5 e3088fc5…). Không đọc giá cổ phiếu/vốn hoá/bội số TV1.
Tái lập: python3 -I valuation_blind_v2.py > valuation_blind_v2_out.txt  (ghi kèm valuation_blind_v2_out.json cho hình/báo cáo)
Nhãn nguồn như valuation_blind.py; [v2 Bx/Nx] = mục hiệu chỉnh theo phản biện."""
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
Q_P50 = 187.5     # [v2 N3] P50 185–190: BQ dài hạn công ty 181–187 (2015–25 BQ 187; 2013–23 175,3 gồm 2 năm khô); độ nhạy 175/185/190/215/236,6
def life_cfs(p_fut, q_fut=Q_P50, end=LIFE_END):
    cfs = []
    for y in range(2009, end + 1):
        c = -TMDT * inv.get(y, 0.0)
        if y >= 2013:
            q = Qh.get(y, q_fut); p = p_hist(y) if y <= 2026 else p_fut
            c += fcf_unlev(y, p, q)
        cfs.append(c)
    return cfs
print(f"IRR dự án toàn đời 2013–{LIFE_END} (không đòn bẩy, sau thuế) ở giá ròng 2027+ = 949: {irr(life_cfs(949)):.2%}; 600: {irr(life_cfs(600)):.2%}; 340: {irr(life_cfs(340)):.2%}")
print("  ĐỌC (v2, khớp LEGAL_PPA): trần IRR 12% toàn đời là TRẦN, không phải sàn bảo đảm; nó không buộc HẠ giá, nhưng cũng KHÔNG bảo vệ")
print("  chủ đầu tư khỏi bậc giá đã ghi trong hợp đồng sửa đổi (Đ.16 TT 12: giá từng năm dồn lên kỳ trả nợ). IRR dựng lại có nhiều [UL]")
print("  (sản lượng 2019–20 suy ra, thuế 20% suốt đời); trần IRR tính trên thông số thiết kế/vốn quyết toán, sản lượng thực thấp là rủi ro chủ đầu tư.")

RAB27 = 506.3 - 38.0 * 1.5
cash_be = (om(2027) + MCAPEX) / Q_P50 * 1000
acct_be = (om(2027) + 38.0) / Q_P50 * 1000
P2018 = 243.66 + 75.75 * 1.025 ** 9
print(f"\nDự thảo HĐ sửa đổi 05/2018 (EVN NQ 286/NQ-HĐTV; Cục ĐTĐL 1374/ĐTĐL-GP): bậc 243,66 từ 01/01/2022 + O&M 75,75×1,025^9 ⇒ {P2018:.0f} đ/kWh"
      " — mức DUY NHẤT có văn bản phê duyệt (chưa từng áp; điều kiện kích hoạt chưa xác định)")
print(f"Hoà vốn TIỀN MẶT {cash_be:.0f} đ/kWh; hoà vốn KẾ TOÁN {acct_be:.0f}; ở 340 biên tiền mặt ≈ {(340-cash_be)*Q_P50/1000:.0f} tỷ/năm (vẫn vận hành được)")

# ---- [v2 B1] Phân bố giá ròng 2027+ — áp CƠ HỌC theo phản biện độc lập (không hiệu chuẩn theo giá)
PRICE = {"P1_949": 949.0, "P2_600": 600.0, "P3_520": 520.0, "P4_440": 440.0, "P5_340": 340.0}
PROB = {"P1_949": 0.05, "P2_600": 0.25, "P3_520": 0.30, "P4_440": 0.20, "P5_340": 0.20}
# P1 0,05: BCTN 2025 tr.38 công ty tự viết giá "sụt giảm"; lãnh đạo nêu 500–600 từ 2027 (KBSV, chưa kiểm bản gốc).
# P2/P3: dải lãnh đạo nêu. P4 440: mức thoả thuận trung gian (KHÔNG gọi là "sàn kinh tế": Đ.14 TT 12 áp cho hợp đồng HẾT HẠN,
#   không áp cho bậc giá Đ.16 đã ghi hợp đồng). P5 340 = 243,66 + O&M ~95 — văn bản phê duyệt 2018.
assert abs(sum(PROB.values()) - 1) < 1e-9
pw = sum(PRICE[k] * PROB[k] for k in PRICE)
print("Kịch bản giá ròng 2027+: " + ", ".join(f"{k} p={PROB[k]:.2f}" for k in PRICE) + f" ⇒ kỳ vọng {pw:.0f} đ/kWh")

def hydro_fcfe(p, q, years=range(2027, 2060), ktpl=KTPL):
    out = []
    for y in years:
        rev = q * p / 1000
        ebit = rev - om(y) - da(y) - 8.0 * 1.025 ** (y - 2026)
        ni = ebit - max(ebit, 0) * TAX
        frac = 7 / 12 if y == 2059 else 1.0
        out.append((ni * (1 - ktpl) + da(y) - MCAPEX * 1.025 ** (y - 2025)) * frac)
    return out
def hydro_ni(p, q, y=2028):
    ebit = q * p / 1000 - om(y) - da(y) - 8.0 * 1.025 ** (y - 2026)
    return ebit - max(ebit, 0) * TAX
T0 = 2 / 12
def pv_mid(cfs, r): return sum(c / (1 + r) ** (T0 + i + 0.5) for i, c in enumerate(cfs))
QS = (175, 185, Q_P50, 190, 215, 236.6)
print(f"\nGiá trị thuỷ điện (PV FCFE sau KTPL 2027–08/2059, tỷ), Ke {KE_C:.2%}:")
print(f"{'kịch bản':10s} {'LNST28':>7s} " + " ".join(f"{'Q'+str(q):>7s}" for q in QS) + f" {'Ke12,3':>7s} {'Ke13,4':>7s}")
HV = {}
for k, p in PRICE.items():
    HV[k] = {q: pv_mid(hydro_fcfe(p, q), KE_C) for q in QS}
    print(f"{k:10s} {hydro_ni(p,Q_P50):7.1f} " + " ".join(f"{HV[k][q]:7.0f}" for q in QS)
          + f" {pv_mid(hydro_fcfe(p,Q_P50),0.123):7.0f} {pv_mid(hydro_fcfe(p,Q_P50),0.134):7.0f}")
hyd_w = sum(HV[k][Q_P50] * PROB[k] for k in PRICE)
print(f"Kỳ vọng thuỷ điện (Q{Q_P50}): {hyd_w:.0f} tỷ = {ps(hyd_w):,.0f} đ/cp")
for k in ("P2_600", "P3_520"):
    d = (hydro_ni(949, Q_P50, 2027) - hydro_ni(PRICE[k], Q_P50, 2027)) * (1 - KTPL) / (1 + KE_C) ** (T0 + 0.5)
    print(f"  Mỗi năm trễ hạ bậc (giữ 949 thay {PRICE[k]:.0f}) ≈ +{d:.0f} tỷ = +{ps(d):,.0f} đ/cp")

# ---- [v2 N1] Rủi ro truy thu bậc giá 2022–2026 nếu bậc 2018 bị áp hồi tố — CHỈ WARNING/độ nhạy, KHÔNG vào tâm
TRUY_Q = {y: Qh[y] for y in range(2022, 2027)}
truy = sum(TRUY_Q[y] * (p_net25 - (243.66 + 75.75 * 1.025 ** (y - 2018))) / 1000 for y in TRUY_Q)
print(f"\n[N1] Truy thu giả định (giá ròng {p_net25:.0f} − bậc 2018 + O&M) × sản lượng 2022–26 ({sum(TRUY_Q.values()):.0f} GWh; 2024, 2026 [UL]):"
      f" ≈ {truy:.0f} tỷ trước thuế ≈ {ps(truy*(1-TAX)):,.0f} đ/cp sau thuế — xác suất thấp, chưa có văn bản; KHÔNG vào tâm")

print("\n" + "=" * 100)
print("B. TƯ VẤN — LỊCH SỬ BIÊN + ĐƯỜNG ỐNG")
print("=" * 100)
# ---- [v2 B3] Tách biên tư vấn lịch sử. Cách tách: EBIT hợp nhất năm = Σ quý (Revenue_P0 × EBITM_P0) từ BQ ticker_financial
#   (v2data/bq_tv1_quarterly_2022_2025.csv); trừ kết quả bộ phận thuỷ điện (2025: kiểm toán 165,055 [FY25 tr.34];
#   2022–24: mô hình Q × giá ròng 949 − O&M − KH 38, cùng hàm đã hiệu chuẩn 2025). DT tư vấn = DT thuần − DT thuỷ điện (gồm pass-through).
#   Biên "sau toàn bộ chi phí chung" = cận dưới; cộng lại 8 tỷ chi phí chung phân bổ cho thuỷ điện (định nghĩa m trong mô hình) = cận trên.
import csv, os
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2data", "bq_tv1_quarterly_2022_2025.csv"))))
ebit_y, rev_y = {}, {}
for r in rows:
    y = int(r["quarter"][:4]); rv = float(r["Revenue_P0"]) / 1e9
    rev_y[y] = rev_y.get(y, 0) + rv; ebit_y[y] = ebit_y.get(y, 0) + rv * float(r["EBITM_P0"])
pass_y = lambda y: (TN25 + Q25 * DVMTR / 1000) * Qh[y] / Q25
hyd_res = {y: Qh[y] * p_net25 / 1000 - om(y) - 38.0 for y in (2022, 2023, 2024)}; hyd_res[2025] = KQ25
hyd_dt = {y: Qh[y] * p_net25 / 1000 + pass_y(y) for y in (2022,)}; hyd_dt.update({2023: 214.59, 2024: 215.941, 2025: DT25})
MH = {}
for y in (2022, 2023, 2024, 2025):
    dtc = rev_y[y] - hyd_dt[y]; e = ebit_y[y] - hyd_res[y]
    MH[y] = (e / dtc, (e + 8.0) / dtc)
    print(f"  {y}: DT hợp nhất {rev_y[y]:.1f}, EBIT {ebit_y[y]:.1f}, thuỷ điện KQ {hyd_res[y]:.1f} ⇒ DT tư vấn {dtc:.1f}, EBIT tư vấn {e:+.1f} "
          f"⇒ biên {MH[y][0]:+.0%} … {MH[y][1]:+.0%}")
print("  Đối chiếu kiểm toán: tư vấn sau toàn bộ chi phí chung 2024 = 85,73 − 74,88 = 10,9; 2025 = 80,84 − 44,08 = 36,8")
print("  9T/2026 (v1 §B, Q3 chưa soát xét): biên 11% (A: hoàn nhập phải thu trong QLDN) … 17% (B)")
print("  ⇒ biên có CHU KỲ: âm 2022–23, 3–5% 2024, 8–10% 2025, 11% 9T/26. Kịch bản 'biên 5%' = mức 2024, không phải đáy lịch sử.")

con9 = 446.9 - (81.20 + 41.2)
CON26 = con9 + 195.0
SCN = {
    "C_bien5": dict(g=0.03, m=0.05, note="[v2 B3] biên quay về mức 2024 (5%), tăng 3%/năm; dự phòng phải thu 86–113 tỷ; HĐ ký mới 2024 ≈280 tỷ"),
    "C_thap":  dict(g=0.03, m=0.08, note="capex EVN đi ngang; biên ~TB 2024–25"),
    "C_giua":  dict(g=0.08, m=0.11, note="capex EVN ~70% KH 830k + trượt giá + dịch cơ cấu; biên 2025–9T26"),
    "C_cao":   dict(g=0.14, m=0.14, note="KH 830k đạt đủ + NT1/HVDC; đòn bẩy chi phí chung"),
}
P_CON = {"C_bien5": 0.20, "C_thap": 0.30, "C_giua": 0.40, "C_cao": 0.10}   # [v2 B3] theo phản biện độc lập
assert abs(sum(P_CON.values()) - 1) < 1e-9
WC_INT = 0.49      # [v2 N2] đo 45–53% ΔDT ((phải thu ròng + dở dang − trả trước)/DT); tâm 0,49, độ nhạy 0,45/0,53
G_TERM = 0.05
def consult(s, ke=KE_C, ktpl=KTPL, g_term=G_TERM, shock=None, wc=None):
    wc = WC_INT if wc is None else wc
    p = SCN[s]; rev = CON26; prev_eff = CON26; out = []; nis = []
    for i, y in enumerate(range(2027, 2033)):
        g = p["g"] if y <= 2030 else (p["g"] + g_term) / 2
        rev_new = rev * (1 + g)
        r_eff = rev_new * (shock[i] if shock and i < len(shock) else 1.0)
        ebit = r_eff * p["m"]
        if r_eff < rev_new:
            ebit -= (rev_new - r_eff) * (1 - p["m"]) * 0.5
        ni = ebit * (1 - TAX)
        out.append(ni * (1 - ktpl) - wc * (r_eff - prev_eff) - 5.0); nis.append(ni); rev = rev_new; prev_eff = r_eff
    ni_t = rev * (1 + g_term) * p["m"] * (1 - TAX)
    tv = (ni_t * (1 - ktpl) - wc * rev * g_term - 5.0) / (ke - g_term)
    v = pv_mid(out, ke) + tv / (1 + ke) ** (T0 + len(out))
    return v, nis, tv / (1 + ke) ** (T0 + len(out)) / v
print(f"\nDT tư vấn 2026E {CON26:.0f} [UL] | g dài hạn {G_TERM:.0%} | ΔVLĐ {WC_INT:.0%}×ΔDT | Ke {KE_C:.2%}")
CV = {}
for s in SCN:
    v, nis, tw = consult(s); CV[s] = v
    print(f"  {s:8s} P={P_CON[s]:.2f}: LNST 2027 {nis[0]:5.1f} · 2030 {nis[3]:5.1f} ⇒ {v:6.0f} tỷ = {ps(v):7,.0f} đ/cp (terminal {tw:.0%}) — {SCN[s]['note']}")
con_w = sum(CV[s] * P_CON[s] for s in SCN)
print(f"  Kỳ vọng tư vấn: {con_w:.0f} tỷ = {ps(con_w):,.0f} đ/cp")

print("\n" + "=" * 100)
print("C. TIỀN & BẢNG CÂN ĐỐI 30/09/2026")
print("=" * 100)
cash, htm, loans, div_pay, int_pay = 30.735, 167.815, 129.880, 43.154, 64.253
KTPL_FUND = 40.708199257      # [v2 B2] BCTC Q3/2026 mã 323 (img/hn_p4.png, kiểm 02/11): 40.708.199.257; đầu năm 26.750.642.257
ni9 = 124.636; ktpl_9t = ni9 * KTPL; q4_ni = 50.0
net_adj = cash + htm - loans - div_pay - int_pay
BS = net_adj - KTPL_FUND - ktpl_9t + q4_ni * (1 - KTPL)
print(f"Tiền+HTM {cash+htm:.1f} − vay {loans:.1f} − cổ tức phải trả {div_pay:.1f} − lãi vay cá nhân phải trả {int_pay:.1f} = {net_adj:+.1f}")
print(f"− quỹ KTPL đã trích chưa chi (mã 323) {KTPL_FUND:.1f} − KTPL sẽ trích từ LNST 9T/26 {ktpl_9t:.1f} + LNST Q4/26 sau KTPL {q4_ni*(1-KTPL):.1f} [UL]")
print(f"⇒ Tiền ròng điều chỉnh: {BS:+.1f} tỷ = {ps(BS):+,.0f} đ/cp  (nợ tranh chấp 127,63 đã trong sổ)")

print("\n" + "=" * 100)
print("F. SOTP v2 — GIÁ TRỊ NỘI TẠI/CP (hiệu chỉnh cơ học theo phản biện độc lập chạy mù; không hiệu chuẩn theo giá)")
print("=" * 100)
def sotp(pk, ck, q=Q_P50, ke=KE_C, ktpl=KTPL, wc=None, bs=None, g_term=G_TERM):
    return pv_mid(hydro_fcfe(PRICE[pk], q, ktpl=ktpl), ke) + consult(ck, ke=ke, ktpl=ktpl, wc=wc, g_term=g_term)[0] + (BS if bs is None else bs)
grid = {(pk, ck): sotp(pk, ck) for pk in PRICE for ck in SCN}
print(f"{'PPA / tư vấn':10s}" + "".join(f"{c:>10s}" for c in SCN))
for pk in PRICE:
    print(f"{pk:10s}" + "".join(f"{ps(grid[(pk,ck)]):10,.0f}" for ck in SCN))
def centre_of(**kw):
    return ps(sum(sotp(pk, ck, **kw) * PROB[pk] * P_CON[ck] for pk in PRICE for ck in SCN))
centre = centre_of()
vals = sorted((ps(v), PROB[pk] * P_CON[ck]) for (pk, ck), v in grid.items())
def quant(qt):
    acc = 0
    for v, w in vals:
        acc += w
        if acc >= qt - 1e-12: return v
print(f"\nTÂM v2 (Q{Q_P50}, Ke {KE_C:.2%}): {centre:,.0f} đ/cp")
print(f"Phân vị 20/50/80 (lưới {len(grid)} ô có trọng số): {quant(0.2):,.0f} / {quant(0.5):,.0f} / {quant(0.8):,.0f}")
print(f"Toàn lưới: {vals[0][0]:,.0f} – {vals[-1][0]:,.0f}")
print(f"Cấu phần: thuỷ điện {ps(hyd_w):,.0f} + tư vấn {ps(con_w):,.0f} + tiền ròng {ps(BS):+,.0f}")
print("\nĐộ nhạy tâm v2 (đ/cp):")
SENS = {}
SENS["Ke"] = {f"{k:.1%}": centre_of(ke=k) for k in (0.10, 0.11, 0.12, 0.123, 0.1285, 0.134, 0.14)}
SENS["San_luong"] = {f"Q{q:g}": centre_of(q=q) for q in QS}
SENS["KTPL_ty_le"] = {f"{k:.0%}": centre_of(ktpl=k) for k in (0.10, 0.15, 0.20, 0.25)}
SENS["VLD"] = {f"{w:.0%}": centre_of(wc=w) for w in (0.40, 0.45, 0.49, 0.53)}
SENS["Quy_KTPL_323"] = {"trừ 40,7": centre, "không trừ": centre_of(bs=BS + KTPL_FUND)}
SENS["Gia_PPA_C_giua"] = {str(int(p)): ps(pv_mid(hydro_fcfe(p, Q_P50), KE_C) + CV["C_giua"] + BS) for p in (340, 440, 520, 600, 750, 949)}
SENS["Gia_PPA_ky_vong_tu_van"] = {str(int(p)): ps(pv_mid(hydro_fcfe(p, Q_P50), KE_C) + con_w + BS) for p in (340, 440, 520, 600, 750, 949)}
SENS["Tu_van_kich_ban"] = {ck: ps(hyd_w + CV[ck] + BS) for ck in SCN}
SENS["g_dai_han"] = {f"{g:.0%}": centre_of(g_term=g) for g in (0.03, 0.05, 0.07)}
for k, d in SENS.items():
    print(f"  {k}: " + "  ".join(f"{a} {b:,.0f}" for a, b in d.items()))

print("\n" + "=" * 100)
print("D. WARNING — TÁCH KHỎI TÂM (vụ án + truy thu)")
print("=" * 100)
WARN = []
base_c = consult("C_giua")[0]
for lab, shock in [("Cấm thầu EVN 3 năm, DT tư vấn −50% 2027–29", [0.5] * 3), ("Cấm 5 năm, −50%", [0.5] * 5), ("Cấm 3 năm, −70%", [0.3] * 3)]:
    v = consult("C_giua", shock=shock)[0]; WARN.append((lab, ps(v - base_c)))
for amt in (20, 50, 100):
    WARN.append((f"Buộc nộp lợi bất chính/bồi thường {amt} tỷ", ps(-amt / (1 + KE_C))))
WARN.append(("Truy thu bậc giá 2022–26 nếu áp hồi tố đủ (sau thuế)", ps(-truy * (1 - TAX) / (1 + KE_C))))
for lab, d in WARN:
    print(f"  {lab}: Δ {d:+,.0f} đ/cp")

import json
OUT = dict(centre=round(centre), p20=quant(0.2), p50=quant(0.5), p80=quant(0.8), lo=vals[0][0], hi=vals[-1][0],
           hydro=ps(hyd_w), consult=ps(con_w), netcash=ps(BS), netcash_bn=BS, price_exp=pw, Q=Q_P50, Ke=KE_C,
           PRICE=PRICE, PROB=PROB, P_CON=P_CON, SCN={k: dict(g=v["g"], m=v["m"]) for k, v in SCN.items()},
           grid={f"{pk}|{ck}": ps(v) for (pk, ck), v in grid.items()},
           hydro_val={k: {str(q): v for q, v in HV[k].items()} for k in HV}, hydro_ni28={k: hydro_ni(p, Q_P50) for k, p in PRICE.items()},
           consult_val={k: ps(v) for k, v in CV.items()}, consult_ni={k: consult(k)[1] for k in SCN},
           margin_hist={str(y): MH[y] for y in MH}, sens=SENS, warn=WARN, truy_bn=truy, ktpl_fund=KTPL_FUND,
           floor=dict(cash_be=cash_be, acct_be=acct_be, p2018=P2018))
json.dump(OUT, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "valuation_blind_v2_out.json"), "w"), ensure_ascii=False, indent=1)
