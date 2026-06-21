# 8L Quality Rating (1–5) — Criteria Spec  (step (c), 2026-06-02)

Rating tín-dụng-hóa cho cổ phiếu, **một trục = độ bền / rủi ro mất vốn vĩnh viễn** (KHÔNG phải tín hiệu mua).
Định giá/timing nằm ở trục riêng (PB-floor + PB_z + Ngũ Hành). Buy-rule: bắt dislocation chỉ ở **rating ≤ 3**.

## Thang chung (route-agnostic)
| Rating | Tên | Analog | Ý nghĩa |
|---|---|---|---|
| **1** | Cao nhất | AAA/AA | Sống sót mọi chu kỳ; rủi ro mất vốn vĩnh viễn ~0 |
| **2** | Cao | A | Mạnh, tì vết nhỏ |
| **3** | Trung bình | BBB | Sàn đầu tư thấp nhất — dip vẫn là cơ hội |
| — | *ranh giới IG / đầu cơ* | | *= ranh giới "dip=cơ hội" vs "dip=bẫy"* |
| **4** | Đầu cơ khả thi | BB | Mong manh, cần điều kiện thuận; dip cần catalyst |
| **5** | Rủi ro cao | B/CCC | Yếu, rủi ro mất vốn cao; dip = value trap; tránh |

**Nguyên tắc**: (1) through-the-cycle (dùng sàn `_Min5Y`, không chấm đỉnh chu kỳ); (2) sticky — KHÔNG hạ bậc chỉ vì giá rơi (tránh pro-cyclicality kiểu credit agency); (3) hard red-flag gate ép xuống 5 bất kể điểm; (4) Risk_Rating(Beta/Dev) của BQ = **outlook notch** (±), không phải rating chính.

---

## COMPOUNDER (mặc định — công nghiệp/tiêu dùng/bán lẻ/tech)
**RED-FLAG GATE → ép Rating 5** (bất kể scorecard): `ROIC_Min5Y<0` HOẶC `FSCORE≤3` HOẶC `Debt_Eq_P0>3` HOẶC NP TTM<0 HOẶC bad-cash-raise (pha loãng + tiền mặt không tăng).

**Scorecard** (chỉ áp cho mã qua gate; tổng max 15):
| Trục | 2 đ | 1 đ | 0 đ |
|---|---|---|---|
| ROIC5Y | ≥0.15 (+1 nếu ≥0.20) | ≥0.10 | <0.10 |
| ROIC bền (ROIC_Min5Y) | ≥0.10 | ≥0.05 | <0.05 |
| ROE floor (ROE_Min5Y) | ≥0.12 | ≥0.08 | <0.08 |
| Bảng cân đối (Debt_Eq_P0) | ≤0.3 | ≤1.0 | >1.0 |
| Cash-machine (CFO/NP TTM) | ≥1.0 & cash↑ | ≥0.7 | <0.7 |
| Piotroski (FSCORE) | ≥8 | ≥6 | <6 |
| Moat (L4 tag) | WIDE | NARROW | NONE |

**Bin** (sẽ hiệu chỉnh ở bước (a)): ≥12→**1** · 9–11→**2** · 6–8→**3** · 3–5→**4** · <3→**5**.

---

## BANK (ICB 8355 — dùng bank_lens_v3 làm xương sống)
Gate cứng (NPL/coverage/CAR/ROE/NPL-trend, dữ liệu vnstock thật):
- **5 (AVOID)**: NPL>3% HOẶC coverage<50% HOẶC CAR<9% HOẶC ROE<8%
- **4 (WATCH)**: NPL>2% HOẶC coverage<80% HOẶC NPL tăng >+0.5pp/4q
- **CLEAN → chấm 1–3**:
  - **1**: ROE≥18% & NPL≤1.5% & coverage≥120% & CAR≥11% & CASA cao (đệm dày, sinh lời elite)
  - **2**: ROE≥14% & NPL≤2% & coverage≥90%
  - **3**: CLEAN còn lại (ROE 8–14% / đệm mỏng hơn)
*Bank KHÔNG dùng Debt_Eq (đòn bẩy là bản chất ngành); rủi ro #1 = nợ xấu.*

---

## POWER (ICB 7535 — debt-paydown lifecycle, power_lens)
Đòn bẩy cao là BÌNH THƯỜNG (annuity hạ tầng) → phạt nợ KHÔNG-trả-được/đang-tăng, không phạt mức nợ.
- **2 (MATURE_YIELD)**: hết nợ / nợ thấp + CFO ổn định + cổ tức đều → annuity chất lượng cao, nhưng tăng trưởng hạn chế nên capped ở 2.
- **3 (PRE-INFLECTION)**: nợ cao **đang giảm** + CFO trả được nợ → sàn đầu tư, đây là zone "mua đáy" (NT2-2013 2Y+53%).
- **4–5 (DEBT_STRESS)**: nợ tăng / CFO≤0 → 4 nếu còn dòng tiền, **5** nếu CFO âm kéo dài.

---

## SECURITIES (ICB 8770-8779 — own lens, thêm 2026-06-02)
Chứng khoán: ROIC thấp/vô nghĩa, đòn bẩy = vốn vay tài trợ margin (vận hành), FSCORE/GPM/cash N/A. Lợi nhuận CYCLICAL mạnh (theo turnover + dư nợ margin). Chấm ROE (ROE_Trailing fallback ROE3Y), **cap 2** (cyclical):
- **5**: lỗ (ROE<0 / NP_TTM<0). **2**: ROE≥13% & ROE3Y≥11%. **3**: ≥9% & ≥7%. **4**: ≥5%.

## INSURANCE (ICB 8530-8579 — own lens, thêm 2026-06-02)
Bảo hiểm: vốn=danh mục ĐT+float; dự phòng nghiệp vụ=nợ vận hành (như tiền gửi bank); thiên tai/tai nạn spike rồi phục hồi. **ROIC/GPM/FSCORE/Debt_Eq VÔ NGHĨA** (ROIC3Y âm toàn ngành dù ROE khỏe). Chấm theo **ROE level + ổn định** (ROE_Trailing + ROE3Y avg = tự smooth năm cat):
- **5**: ROE_Trailing<0 (đang lỗ). **1**: ROE_tr≥15% & ROE3Y≥12% (PVI/PRE/ABI). **2**: ≥11% & ≥9%. **3**: ≥7%. **4**: ≥0.

## REALESTATE (ICB 8633 — L8 asset-play, thêm 2026-06-02)
KCN/BĐS: tiền thuê đất trả trước ghi vào NỢ (D/E ảo cao), bán đất lô lớn → CFO âm năm gom đất.
COMPOUNDER red-flag (D/E>3, CFO-âm, ROIC_min<0) MISFIRE → junk oan operator tốt (SIP/NTC).
- **Red-flag → 5**: chỉ NP_TTM<0 (lỗ thật). Bỏ D/E & CFO & ROIC_min.
- **Scorecard** (max ~9): ROE_Trailing(2/1@.18/.10) + ROIC5Y(2/1@.12/.07) + leverage-lenient(2/1@≤1.0/≤2.5) + cash-light(1@cfo_np≥.8) + FSCORE(1@≥6) + ROIC_Min5Y≥0(1).
- **Bin: cap 2 / FLOOR 4** (đất bảo chứng giá trị thu hồi → giới hạn mất vốn vĩnh viễn): s≥6→2, s≥4→3, else→4. Chỉ lỗ-TTM mới =5.
- HOLDING_OVERRIDE (REE) → COMPOUNDER dù ICB 7535.

## CYCLICAL (commodity map + SUGAR — through-the-cycle là tối thượng)
Chấm bằng **khả năng sống sót qua đáy chu kỳ** + sàn ROIC qua chu kỳ:
**RED-FLAG GATE → 5**: Debt_Eq>1.5 ở đáy chu kỳ (không qua nổi trough) HOẶC ROIC_Min5Y<0 HOẶC lỗ TTM.
- **2** (trần cho cyclical thường): nhà sản-xuất chi-phí-thấp + bảng cân đối pháo đài (net-cash) + ROIC_Min5Y≥0.10 (vd NNC/DHA stone ROIC 50%+ no-debt; HPG quy mô).
- **3**: cyclical ổn định, đòn bẩy vừa (Debt_Eq≤1.0), sống được qua đáy → dip ở đáy commodity = cơ hội (contrarian).
- **4**: đòn bẩy cao nhưng còn trả được / biên mỏng / phụ thuộc giá commodity mạnh.
- **5**: gate đỏ.
*Cyclical hiếm khi đạt 1 (biến động vốn có cap ở BBB ≈ rating 2). SUGAR: trend-cyclical, dùng cùng khung độ-bền nhưng entry-logic ngược (mua dip ở regime GOOD).*

---

## Quyết định đã CHỐT (user 2026-06-02)
1. ✅ **Cyclical trần ở rating 2** (trừ low-cost-fortress net-cash: NNC/DHA/HPG-scale mới xét lên). Phản ánh biến động vốn có của ngành.
2. ✅ **MATURE_YIELD power = rating 2** (annuity an toàn nhưng tăng trưởng cụt → dành rating 1 cho compounder tăng trưởng thật).
3. ⏳ **Bin cutoff COMPOUNDER** = draft; bước (a) hiệu chỉnh để (i) đơn điệu từng ngành, (ii) ranh giới 3/4 trùng ranh giới dip=cơ-hội vs bẫy.
4. ✅ **KHÔNG outlook notch giai đoạn đầu** — rating thuần fundamental (sạch, dễ kiểm chứng đơn điệu). Thêm notch sau khi calibrate xong.
