"""DD FPT 01/11/2026 — v2 sau phản biện (C1–C3, T1, T4–T7)
DD FPT 01/11/2026 — tách Q3, PREREG, SOTP, DCF (Ke nội địa). Đơn vị: tỷ đồng, đ/cp.
Nguồn số: calc/notes_q3_bctc.md (BCTC hợp nhất Q3/2026 gốc, trang pNN), src/tcbc_6M2026.pdf p2,
FPT_BC_KQKD_9_M2026 (p2-p8), BQ (bq_px.csv, bq_fin.csv), DNSE (dnse_latest_raw.json).
Mọi giả định tự đặt có nhãn (ước lượng)."""
import json, itertools

P = 52.7e3                      # DNSE latest_trade FPT 2026-10-30 14:45:03 (phiên gần nhất)
SH = 1885.727648                # triệu cp, p44 / bonusslcp_p01
MCAP = P * SH / 1e3             # tỷ
print(f"Vốn hoá @52.700: {MCAP:,.0f} tỷ")

# ---------- 1) Tách Q3 = 9T − 6T ----------
r = {}
pairs = {  # (9T26, 6T26, 9T25, 6T25 or derive via growth)
 "DT hợp nhất": (40023, 26269, 35600, 26269/1.126),
 "LNTT": (8770, 5714, 7495.5, 5714/1.181),
 "LNST mẹ": (7778, 5055, 6867, 5055/1.141),
 "DT CNTT NN": (28538, 18902, 25574, 18902/1.134),
 "DT CNTT TN": (6977, 4236, 5376, 4236/1.225),
 "LNTT CNTT TN": (542, 308, 260, 308/2.005),
 "LNTT khối Công nghệ": (5052, 3314, 5052/1.166, 3314/1.169),
 "Ký mới NN": (36137, 26338, 29363, 26338/1.323),
 "DT CĐS NN": (14411, 9610, 12387, 9610/1.238),
}
print("\n== Q3 suy ra (9T − 6T); cùng kỳ suy từ % tăng trưởng FPT công bố ==")
for k, (a9, a6, b9, b6) in pairs.items():
    q, qb = a9 - a6, b9 - b6
    r[k] = (q, qb)
    print(f"{k:22s} Q3/26 {q:8,.0f}  Q3/25 {qb:8,.0f}  YoY {q/qb-1:+.1%}   | 9T YoY {a9/b9-1:+.1%}  6T YoY {a6/b6-1:+.1%}")
ln_nn_q3 = r["LNTT khối Công nghệ"][0] - r["LNTT CNTT TN"][0]
ln_nn_q3b = r["LNTT khối Công nghệ"][1] - r["LNTT CNTT TN"][1]
print(f"LNTT CNTT NN Q3 {ln_nn_q3:,.0f} vs {ln_nn_q3b:,.0f} YoY {ln_nn_q3/ln_nn_q3b-1:+.1%}; 9T 4.510 vs 4.073 {4510/4073-1:+.1%} (p29-30)")
print("Hợp đồng >10tr USD: 6T 14, 9T 16 ⇒ Q3 = 2; cùng kỳ 6T25 = 14/1,273 ≈ 11, 9T25 = 16/0,842 ≈ 19 ⇒ Q3/25 ≈ 8")
print(f"Book-to-bill NN (ký mới/DT): 9T {36137/28538:.2f}; Q3 {r['Ký mới NN'][0]/r['DT CNTT NN'][0]:.2f}; 6T {26338/18902:.2f}")

# ---------- 2) Chất lượng LN: tách liên kết + thuế ----------
assoc9, assoc9b = 2220.3, 1556.9          # p08
pbt9, pbt9b = 8770.2, 7495.5
pat9, pat9b = 7776.4, 6839.1
tax9 = pbt9 - pat9; tax9b = pbt9b - pat9b
core_pbt, core_pbtb = pbt9 - assoc9, pbt9b - assoc9b
print("\n== Chất lượng LN 9T (LFL, p08) ==")
print(f"LNTT trừ LN liên kết: {core_pbt:,.0f} vs {core_pbtb:,.0f} ({core_pbt/core_pbtb-1:+.1%})")
print(f"Thuế/LNTT-trừ-LK: {tax9/core_pbt:.1%} vs {tax9b/core_pbtb:.1%}")
print(f"LNST trừ LK: {pat9-assoc9:,.0f} vs {pat9b-assoc9b:,.0f} ({(pat9-assoc9)/(pat9b-assoc9b)-1:+.1%})")
print(f"Đóng góp vào tăng LNTT +{pbt9-pbt9b:,.0f}: liên kết +{assoc9-assoc9b:,.0f} ({(assoc9-assoc9b)/(pbt9-pbt9b):.0%}), Công nghệ +{5052-5052/1.166:,.0f}")
edu = 3719 - assoc9; edub = 3719/1.176 - assoc9b
print(f"Khối GD-ĐT-khác LNTT trừ LK: {edu:,.0f} vs {edub:,.0f} ({edu/edub-1:+.1%}) — gồm lãi tiền gửi ròng, chưa tách được giáo dục thuần")
print(f"Lãi tiền gửi 9T 1.283 (p45) vs lãi vay 612 ⇒ thu nhập lãi ròng {1283-612:,.0f}; CLTG ròng −111 vs +541 cùng kỳ (gốc, còn FTEL)")

# ---------- 3) Dòng tiền ----------
cfo9, cfo6 = 952.0, -1144.6; capex9, capex6 = 2028.8, 1336.5
cfo_q3, capex_q3 = cfo9 - cfo6, capex9 - capex6
print("\n== Dòng tiền (p10; Q2 BCTC p10) ==")
print(f"CFO Q3 = {cfo_q3:,.0f}; capex Q3 {capex_q3:,.0f}; FCF Q3 {cfo_q3-capex_q3:,.0f}; 9T CFO {cfo9:,.0f}, FCF {cfo9-capex9:,.0f}")
print("CFO core Q3 lịch sử (fpt_dcf_deconsol_20261014 [ĐO]): 2023 2.596 / 2024 2.585 / 2025 3.279")
print(f"CFO 9T/LNST 9T = {cfo9/pat9:.2f}")
wc = dict(AR=(10851, 10847), HTK=(1252.4, 2034.8), HD_tiendo=(301.8, 280.5), tratruoc_NB=(1866.7, 1461.7))
for k, (a, b) in wc.items(): print(f"  {k:12s} 30/6 {a:7,.0f} → 30/9 {b:7,.0f} ({b-a:+,.0f})")
unb6, unb9 = 10851+1252.4+301.8, 10847+2034.8+280.5
print(f"  AR+HTK(dở dang)+HĐ tiến độ: {unb6:,.0f} → {unb9:,.0f} ({unb9/unb6-1:+.1%}) trong khi DT Q3 ≈ Q2 (13.754 vs 13.789)")
dt_ttm = 53619 + (13754 - 12275)   # TTM core Q2/26 (fpt_q3_eval out.txt) + chênh Q3
print(f"  DSO định nghĩa PREREG (tổng phải thu NH mã 130 / DT core TTM): {13064.3/dt_ttm*365:.1f} ngày (Q2 ~91,9 theo PREREG; ngưỡng 90)")
print(f"  DSO chỉ mã 131 (tham khảo, KHÁC định nghĩa PREREG / DT TTM {dt_ttm:,.0f}): {10847/dt_ttm*365:.1f} ngày; Q2 {10851/53619*365:.1f}")


# ---------- 3b) Tỷ lệ chuyển lãi thành tiền — MỘT định nghĩa (v2, theo phản biện C2/C3) ----------
# conv = (CFO + lãi vay đã trả×(1−t) − capex mã 21) / LN lõi vận hành
# LN lõi vận hành = (LNTT − mã 05 "lãi hoạt động đầu tư" + mã 06 chi phí lãi vay) × (1 − t)
# t = thuế TNDN (51+52) / (LNTT − lãi liên kết). Mọi thành phần đọc từ LCTT/KQKD gốc.
# Nguồn: 2024, 2025 = BCTN25 p168 (KQKD) + p170 (LCTT) [ảnh calc/bctn25_p169.png, p171.png], phạm vi CŨ (gồm FTEL);
#        9T/2025 = cột so sánh BCTC Q3/2026 (phạm vi cũ); 9T/2026 = BCTC Q3/2026 (phạm vi mới, FTEL là liên kết).
def conv_d(pbt, m05, m06, tax, assoc, cfo, m14, capex):
    t = tax/(pbt-assoc); core = (pbt - m05 + m06)*(1-t); num = cfo + m14*(1-t) - capex
    return num, core, num/core, t
conv_rows = {  # pbt, |mã05|, mã06, thuế(51+52), lãi LK, CFO, |mã14|, |capex|
 "FY2024 (gồm FTEL)": (11069.7, 1725.0, 551.6, 1922.9-280.7, 392.5, 11703.8, 607.2, 3275.3),
 "FY2025 (gồm FTEL)": (13043.6, 2575.8, 809.8, 1917.0-105.7, 658.0, 10136.0, 812.5, 5097.9),
 "9T/2025 (gồm FTEL)": (9540.5, 1828.2, 602.7, 1430.8-127.7, 374.3, 6027.6, 583.3, 4125.6),
 "9T/2026 (FTEL là LK)": (8770.2, 3541.0, 612.4, 1083.8-90.1, 2220.3, 952.0, 566.9, 2028.8),
}
print("\n== Tỷ lệ chuyển lãi thành tiền — định nghĩa duy nhất (CFO + lãi vay trả×(1−t) − capex)/LN lõi vận hành ==")
convd = {}
for k, v in conv_rows.items():
    num, core, c, t = conv_d(*v); convd[k] = c
    print(f"  {k:22s} tử {num:7,.0f}  mẫu {core:7,.0f}  t {t:.1%}  conv {c:+.2f}")
print("  2021–2023: CHƯA ĐO trên định nghĩa này (cần LCTT gốc BCTN 2022–2023; BQ không có mã 05/06/14).")
print("  Tham khảo định nghĩa CŨ 14/10 (CFO−capex)/LNST mẹ, phạm vi lõi bỏ FTEL [fpt_dcf_deconsol_20261014/cashflow_scope.csv]:")
print("    2021 0,55 · 2022 0,44 · 2023 0,80 · 2024 0,86 · 2025 0,39  (định nghĩa KHÁC — chỉ để thấy hình dạng)")
print(f"  Số tham khảo khác gốc 9T/2026: CFO/LNST {952.0/7776.4:.2f} (lệch gốc) · CFO/(LNTT − mã05 − thuế) {952.0/(8770.2-3541.0-993.7):.2f} · (CFO + mã 27)/LNST {(952.0+1246.0)/7776.4:.2f}")
q4_25 = (5732-2402)   # tử số Q4/2025 = FY25 − 9T25 (phạm vi cũ)
print(f"  Mùa vụ: tử số Q4/2025 = FY − 9T ≈ {conv_d(*conv_rows['FY2025 (gồm FTEL)'])[0]-conv_d(*conv_rows['9T/2025 (gồm FTEL)'])[0]:,.0f} tỷ (phạm vi cũ)")
# Ngưỡng CFO cả năm 2026 ứng với conv (mẫu ≈ LN lõi vận hành TTM; lãi vay trả năm ≈ 756; capex năm ≈ 2.705, đều ước lượng)
int_paid_y, capex_y, t_y = 566.9*4/3, 2028.8*4/3, 0.152
def cfo_for(c, core): return c*core - int_paid_y*(1-t_y) + capex_y

# ---------- 4) BCĐ: net cash ----------
cash = {"30/9/26": (7377.3, 21449.7, 2.5, 14316.5, 2280.0), "30/6/26": (9065.5, 19906.1, 0, 16367.8, 2080.6)}
print("\n== Net cash (tiền + HTM ngắn/dài − vay) ==")
for k, (c, h, hl, s, l) in cash.items(): print(f"{k}: {c+h+hl:,.0f} − {s+l:,.0f} = {c+h+hl-s-l:,.0f}")
nc = 7377.3 + 21449.7 + 2.5 - 14316.5 - 2280.0
div_pending = 1000 * SH / 1e3     # cổ tức tiền 1.000đ, chốt 30/11, trả 10/12 (div_p02)
nc_pf = nc - div_pending
nc_cum = nc   # v2 (T1): giá 52.700 còn quyền cổ tức 1.000đ (chốt 30/11) ⇒ so cùng gốc, KHÔNG trừ cổ tức
print(f"Net cash pro-forma trừ cổ tức đợt 1/2026 {div_pending:,.0f}: {nc_pf:,.0f} = {nc_pf/SH*1e3:,.0f} đ/cp")
print(f"v2 dùng tiền ròng CHƯA trừ cổ tức {nc_cum:,.0f} = {nc_cum/SH*1e3:,.0f} đ/cp, vì giá 52.700 gồm quyền 1.000đ")

# ---------- 5) SOTP ----------
FOX_P, FOX_SH = 55.4e3, 738.763463   # DNSE 30/10; BQ OShares
FRT_P, FRT_SH = 148.7e3, 178.815054
fox_stake = FOX_P*FOX_SH/1e3*0.4566; frt_stake = FRT_P*FRT_SH/1e3*0.4654
other_assoc_book = 1500.0   # Synnex 48%, FPT Online 23,86%, khác — (ước lượng), BCTC không tách
inv_other = 494.4 + 451.1    # TPBank, FPTS giá gốc (p32) — sổ sách
print("\n== SOTP @ giá 30/10 ==")
print(f"FTEL 45,66% thị giá {fox_stake:,.0f} tỷ ({fox_stake/SH*1e3:,.0f} đ/cp) — FOX ADV 1T ~3,5 tỷ/phiên ⇒ thị giá mỏng")
print(f"FRT 46,54% thị giá {frt_stake:,.0f} tỷ ({frt_stake/SH*1e3:,.0f} đ/cp)")
# core LN ex-LK TTM: 9T core 5.556 + Q4/25 core (ước lượng: Q4/25 LNST mẹ 2.510 − LK Q4/25 ước 600)
core_ttm = (pat9 - assoc9) + (2509.5 - 600)          # (ước lượng)
net_int_after_tax = (1283 - 612) * 4/3 * 0.85          # (ước lượng) thu nhập lãi ròng năm sau thuế
core_op_ttm = core_ttm - net_int_after_tax
print(f"LN core (trừ LK) TTM ≈ {core_ttm:,.0f} (ước lượng); trừ lãi ròng ≈ {core_op_ttm:,.0f} (ước lượng)")
implied = MCAP - fox_stake - frt_stake - other_assoc_book - inv_other - nc_cum
print(f"Giá thị trường ngầm định cho core vận hành: {implied:,.0f} tỷ ⇒ PE core vận hành {implied/core_op_ttm:.1f}x (ước lượng)")

def sotp(pe_core, fox_disc, frt_disc=0.2):
    v = core_op_ttm*pe_core + fox_stake*(1-fox_disc) + frt_stake*(1-frt_disc) + other_assoc_book + inv_other + nc_cum
    return v/SH*1e3
print("SOTP đ/cp — hàng PE core vận hành, cột chiết khấu FTEL (FRT ck 20%):")
for pe in (6, 8, 10, 12, 14):
    print(f"  PE {pe:2d}: " + "  ".join(f"ck{int(d*100)}% {sotp(pe,d):7,.0f}" for d in (0, .15, .30)))

# ---------- 6) DCF FCFE core, Ke nội địa (skill 2026-10-30) ----------
def dcf(base, g1, conv, gT, ke, n=5):
    pv, e = 0.0, base
    for t in range(1, n+1):
        e *= 1+g1; pv += e*conv/(1+ke)**t
    tv = e*(1+gT)*conv/(ke-gT); pvtv = tv/(1+ke)**n
    return pv+pvtv, pvtv/(pv+pvtv)
scen = {  # (g1, conv, gT, Ke, fox_disc, P)  — tất cả (ước lượng)
 "Xấu":   (0.03, 0.40, 0.030, 0.134, 0.30, 0.35),   # v2: conv 0,40 ≈ mức đã quan sát (0,39 cũ 2025; FY26 dự phóng 0,3–0,45)
 "Cơ sở": (0.09, 0.75, 0.040, 0.1285, 0.15, 0.45),
 "Tốt":   (0.14, 0.85, 0.040, 0.123, 0.00, 0.20),   # v2 (T5): không vừa hạ Ke vừa nâng g ⇒ g 4%
}
print("\n== DCF FCFE core vận hành + LK thị giá có chiết khấu + net cash pro-forma ==")
ev = 0; out = {}
for k, (g1, cv, gT, ke, fd, p) in scen.items():
    v, tvs = dcf(core_op_ttm, g1, cv, gT, ke)
    fv = (v + fox_stake*(1-fd) + frt_stake*0.8 + other_assoc_book + inv_other + nc_cum)/SH*1e3
    out[k] = fv; ev += p*fv
    print(f"{k:6s} g5y {g1:.0%} conv {cv:.2f} gT {gT:.1%} Ke {ke:.2%} FTELck {fd:.0%} P={p:.2f} → FV {fv:,.0f} đ/cp ({fv/P-1:+.0%}); TV {tvs:.0%}")
print(f"Kỳ vọng có trọng số: {ev:,.0f} đ/cp ({ev/P-1:+.0%})")
print("Độ nhạy cơ sở (conv 0,75, g5y 9%): hàng gT, cột Ke")
for gT in (0.03, 0.04, 0.05):
    row = []
    for ke in (0.105, 0.123, 0.1285, 0.134, 0.14, 0.158):
        v, _ = dcf(core_op_ttm, 0.09, 0.75, gT, ke)
        row.append(f"Ke{ke:.1%} {(v + fox_stake*0.85 + frt_stake*0.8 + other_assoc_book + inv_other + nc_cum)/SH*1e3:7,.0f}")
    print(f"  gT {gT:.0%}: " + " ".join(row))
print("Độ nhạy conv (cơ sở): " + "  ".join(f"{c:.2f}→{(dcf(core_op_ttm,0.09,c,0.04,0.1285)[0]+fox_stake*0.85+frt_stake*0.8+other_assoc_book+inv_other+nc_cum)/SH*1e3:,.0f}" for c in (0.4,0.5,0.6,0.75,0.9)))

# ---------- 7) PE ----------
eps_ttm = (2509.5 + 7778.1)/SH*1e3
npat26 = 7778.1 + 2509.5*1.12      # Q4/26 = Q4/25 × 1,12 (ước lượng)
print(f"\nEPS TTM {eps_ttm:,.0f} ⇒ PE {P/eps_ttm:.1f}; LNST mẹ 2026E {npat26:,.0f} (ước lượng; KH LNTT +15%) EPS {npat26/SH*1e3:,.0f} PE {P/(npat26/SH*1e3):.1f}")
print("PE lịch sử FPT (BQ weekly): 10 năm p10/p50/p90 = 10,5/15,4/23,7; 5 năm 12,7/19,3/26,5; peer VN: CMG 10,9, ELC 9,3, FOX 10,9 (BQ 30/10)")
for pe in (9, 11, 13, 15): print(f"  PE {pe} × EPS 2026E = {pe*npat26/SH*1e3:,.0f}")

print("\nRONIC ngầm định = gT/(1−conv): " + " · ".join(f"{k} {v[2]/(1-v[1]):.1%}" for k, v in scen.items()) + " (so Ke 12,3–13,4%; xấu < Ke = tăng trưởng huỷ giá trị, giả định cắt vĩnh viễn)")
print(f"Vùng cơ sở 1 trục (C1): lưới gT 3–5% × Ke 12,3–13,4%, conv 0,75, g5y 9% ⇒ xem bảng độ nhạy (min gT3/Ke13,4; max gT5/Ke12,3)")
print("Vùng 2 trục (tham khảo): conv 0,6–0,9 tại gT 4%, Ke 12,85%")

# ---------- T6: bất định SOTP ----------
oth_assoc_y = (2220.3 - 2883.8*0.4566 - (287.4+341.5+341.5)*0.4654)*4/3   # FRT Q3 ≈ Q2 (ước lượng)
print(f"\nLãi liên kết khác ước lượng ≈ {oth_assoc_y:,.0f} tỷ/năm (9T 2.220 − FTEL 45,66%×FOX 9T 2.884 − FRT 46,54%×(H1 629 + Q3≈Q2) , ước lượng)")
for pe in (6, 8, 10):
    print(f"  liên kết khác theo PE {pe}: {oth_assoc_y*pe:,.0f} tỷ vs sổ 1.500 ⇒ {(oth_assoc_y*pe-1500)/SH*1e3:+,.0f} đ/cp")
adv = 1609.3 + 761.0
print(f"  tiền khách ứng trước (học phí 1.609 + người mua trả trước 761) = {adv:,.0f} tỷ = {adv/SH*1e3:,.0f} đ/cp (nếu coi là nợ, trừ khỏi tiền ròng)")
print("  TPBank/FPTS: theo giá gốc 945 tỷ; thị giá chưa đo ⇒ chỉ có thể làm TĂNG (ước lượng chiều)")

# ---------- C3: ngưỡng CFO cả năm 2026 ↔ conv ----------
core_fy26 = conv_d(*conv_rows["9T/2026 (FTEL là LK)"])[1] * 4/3   # (ước lượng) LN lõi vận hành năm 2026
print(f"\nNgưỡng CFO cả năm 2026 (LN lõi vận hành 2026 ≈ {core_fy26:,.0f}, lãi vay trả ≈ {int_paid_y:,.0f}, capex ≈ {capex_y:,.0f}; ước lượng):")
for c in (0.0, 0.2, 0.4, 0.6, 0.75, 0.9):
    print(f"  conv {c:.2f} ⇔ CFO ≈ {cfo_for(c, core_fy26):,.0f} tỷ")
print(f"  CFO 4.000 ⇔ conv {(4000 + int_paid_y*(1-t_y) - capex_y)/core_fy26:.2f}; CFO 2.000 ⇔ conv {(2000 + int_paid_y*(1-t_y) - capex_y)/core_fy26:.2f}")

# ---------- T7: cầu nối FV ----------
v_old_ke, _ = dcf(core_op_ttm, 0.09, 0.75, 0.04, 0.15)
fv_ke15 = (v_old_ke + fox_stake*0.85 + frt_stake*0.8 + other_assoc_book + inv_other + nc_cum)/SH*1e3
print(f"\nCầu nối: FV 14/10 49,6k → 21/10 49,8k (Ke 14–16%, mô hình cũ) → v1 01/11 58,8k → v2 cơ sở {out['Cơ sở']:,.0f}")
print(f"  cấu trúc mới nhưng Ke 15% (gần khung cũ): {fv_ke15:,.0f} ⇒ phần do đổi Ke ≈ {out['Cơ sở']-fv_ke15:+,.0f} đ/cp; phần còn lại do SOTP thị giá + tách tiền ròng (đổi phương pháp), KHÔNG do tin Q3")
json.dump({"fv": out, "ev": ev, "nc_pf": nc_pf, "nc_cum": nc_cum, "convd": convd, "core_op_ttm": core_op_ttm, "mcap": MCAP}, open(__file__.replace("valuation.py", "valuation_out.json"), "w"), ensure_ascii=False, indent=1)
