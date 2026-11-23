**Phán quyết: INCONCLUSIVE, độ tin cậy trung bình.** Số học của rev 4 tái lập đúng, các đầu vào bảng cân đối khớp BCTC Q3. Có hai điểm khiến tâm 35.600 chưa thể xác nhận. Thứ nhất, bằng chứng chính cho cửa sổ cơ sở không vững như báo cáo trình bày. Thứ hai, tình trạng hợp nhất của VCBNeo mâu thuẫn ngay trong chuỗi báo cáo, và nguồn đã trích dẫn trả lời được một phần.

**Đã kiểm độc lập** (đọc ảnh scan `src/VCB_BCTC_Q3_2026_HN.pdf`, B02a tr.4):
- VCSH 253.761,146; NCI 92,442; vốn điều lệ 83.556,751 (tức 8.355,675 triệu cp); LNST mẹ 9T 33.032,144. Tất cả khớp.
- Tính lại từ các số trên: BVPS 30.359, KTPL 2.794 tỷ (334 đ/cp), BVPS sau trừ 30.024. Đòn bẩy 7,239, spread 9T/26 3,549% − 0,702% = 2,848%, ROE 15,10%, P/B 1,246, base 37.406. Tất cả khớp `calc_rev4_output.txt`.
- Lo ngại về mùa vụ quý 4 khi nhân ×12/9: không đúng. Năm 2025 quý 4 chiếm 24,9% PPOP và 27% chi phí dự phòng, gần đúng một phần tư.

**Chiều ĐẮT (tâm có thể quá cao):**
- Lập luận "hai cửa sổ độc lập khớp nhau ở 2,82–2,85%" là trùng hợp số học, không phải xác nhận lẫn nhau. Hai cửa sổ có thành phần trái ngược:

  | Cửa sổ | Biên | CC | Spread |
  |---|---|---|---|
  | FY2025 | 3,02 | 0,20 | 2,82 |
  | 9T/26 | 3,55 | 0,70 | 2,85 |

- Chặn "−1,9%" ở r3-5 vì thế chặn sai. Nếu cú nhảy NII (+34,5%, kèm opex +32%, chưa giải thích) đảo chiều trong khi CC giữ 0,70%, spread còn khoảng 2,32% và base khoảng 24.500 (−35%). CC 0,70% có cơ sở để giữ: nhóm 3–4 tăng gấp 4 (1.063 → 4.229), nhóm 2 tăng 85%.
- Biên 9T/26 ghép với CC bình quân chu kỳ 2017–25 (0,86%) cho base khoảng 33.500 (−10%).

**Chiều RẺ (tâm có thể quá thấp):**
- Mô hình Gordon với g 7% ngầm định tỷ lệ chi trả 54%. Thực tế VCB giữ lại khoảng 89% (cổ tức tiền 450 đ). Với ROE 15,1% > Ke, mô hình hai giai đoạn nâng base khoảng +6%. Kịch bản xấu có ROE < Ke nên bù trừ một phần; tâm có trọng số tăng khoảng +4%. Đây là ước tính nhẩm, chưa chạy lại mô hình.
- Biên chu kỳ (bình quân 3,93%) ghép CC hiện tại cho spread khoảng 3,2%. Mức này đã nằm trong kịch bản tốt.
- Đợt phát hành riêng lẻ ≤6,5% được giả định ở giá sổ sách. Đây là giả định hạ tâm mà không có căn cứ (theo luật 02/11), dù ảnh hưởng dưới 5%.

**VCBNeo:**
- Thuyết minh Q3 TM1(d) liệt kê "NHTM TNHH MTV Ngoại thương Công nghệ số" là công ty con sở hữu 100% (GP 27/03/2026). Số đếm "6 công ty con tại VN" có tính cả nó. Chính sách hợp nhất ở TM2(e) không ghi miễn trừ.
- Điều này mâu thuẫn với rev 1, vốn khẳng định "miễn hợp nhất".
- Nếu VCBNeo đã được hợp nhất, lỗ quá khứ đã nằm trong BVPS. Khi đó độ nhạy −2…−8% đếm trùng phía giảm, chỉ còn lại rủi ro từ cam kết hỗ trợ trong tương lai. Tôi không xác minh được BCTC 2025 vì là bản scan và không có OCR.
- Số nhân viên gần như không đổi (23.457 → 23.260). Vì vậy cú nhảy NII/opex năm 2026 không đến từ việc mới hợp nhất VCBNeo.

**Mục còn thiếu (attack 8):** CET1, LDR TT22 và Pillar 3 vẫn trống. Với ngân hàng đây là mục trọng yếu nhưng không định lượng được, nên theo luật dẫn tới INCONCLUSIVE. Bảo lãnh tăng 2,37 lần chưa được phân tích tập trung. Các mục khác đạt: capex tuân thủ không đáng kể, kiểm toán FY2025 chấp nhận toàn phần, lãi một lần Bonday đã loại, KTPL đã trừ, quy tắc chia lại vùng khi pha loãng đã có.

Giá 52.100 và mục 7 trong báo cáo được bỏ qua theo ràng buộc mù giá.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCB — DD rev4 (BCTC Q3/2026), tâm có trọng số 35.600 đ/cp, vùng 30.900–42.100",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — §8: EY 2025 unqualified, KTNN +29 tỷ, branch-level SBV inspections only; no legal-entity/asset migration signal. VCBNeo is a policy obligation, not a scandal",
    "optimistic_comp_sotp_bias": "fail (two-sided, not decisive) — no comps; the window choice is the bias vector. The 'independent corroboration' FY2025 2,82% vs 9T/26 2,85% has opposite composition (margin 3,02/CC 0,20 vs 3,55/0,70), so it is coincidence, not confirmation. If the unexplained NII step-up reverses while CC stays 0,70 (G3-4 ×4, G2 +85%), spread ≈2,32 and base ≈24.500 (−35%), so the r3-5 '−1,9%' bound is understated. Through-cycle CC 0,86% gives ≈33.500 (−10%). Upward: Gordon payout 54% vs actual retention ~89% at ROE>Ke understates base ~+6% (weighted ~+4%); cycle margin is already covered by the bull case",
    "data_provenance": "pass with one contradiction — equity 253.761,146, NCI 92,442, charter capital 83.556,751 (8.355,675m sh), NPAT 9M 33.032,144 read directly from Q3 B02a p.4. Contradiction: rev1 asserted VCBNeo 'miễn hợp nhất' (citing KT2025 TM1), but Q3 TM1(d) lists it as a 100% subsidiary in the consolidated count (6 VN subs) and TM2(e) shows no exemption; rev4 calls consolidation status 'unverifiable' although the cited source partly answers it",
    "liquidity_capacity_realism": "na — sizing only post-lock (§7), 2–4% NAV vs ADV 175 tỷ; not re-queried (price-blind)",
    "confirmation_bias_flipflop": "pass — per report's own chain 38.800→44.900→36.000→35.600; rev3→rev4 −1%, each move tied to a named r3 item with audited-source inputs (2017 audited bear, end-period leverage, KTPL accrual). dd_price_zones.json not opened per brief",
    "exit_discipline_gap": "na — no position proposed ('không đề xuất mở vị thế'); §9 lists change-of-view triggers",
    "missing_items": "fail (unquantifiable) — CET1, LDR TT22, Pillar 3 still absent (bank-mandatory; CAR 11,14% press-only); cause of NII +34,5% / opex +32% step-up (base driver) unexplained; guarantee book ×2,37 not concentration-analysed; VCBNeo future support commitment unknown (historic losses likely already in BVPS if consolidated per TM1(d), so the −2…−8% sensitivity likely double-counts downside). Pass: no material compliance capex for a bank; share count dated+sourced (Q3 TM1/B02a); bonus/stock-div rebase rule present; KTPL deducted; FY2025 EY unqualified present; Bonday 3.171 one-off removed; NPL G2 0,28%, coverage 243%, CASA 31,8% sourced to Q3"
  },
  "independent_verification": "Read Q3/2026 B02a p.4 scan: equity/NCI/charter capital/9M NPAT match assumptions exactly. Recomputed BVPS 30.359→30.024 (KTPL 8,459%×33.032=2.794 tỷ), leverage 7,239, 9T/26 spread 3,549−0,702=2,848%, ROE 15,10%, P/B 1,246, base 37.406: all match calc_rev4_output. Seasonality check: FY2025 Q4 = 24,9% PPOP / 27% provisions, so ×12/9 annualisation is fair. Q3 TM1(d)/TM2(e) checked for VCBNeo consolidation (listed as consolidated subsidiary, no exemption shown); headcount flat 23.457→23.260 so the 2026 NII/opex jump is not from new consolidation",
  "killer_objection": "The base rests on the 9T/26 margin of 3,55%, driven by an unexplained +34,5% NII step-up, paired with CC 0,70%. The FY2025 'cross-check' matches only by coincidence (different margin/CC mix). If the NII step reverses while the current asset-quality-driven CC persists, base falls ~35% to ≈ the bear case, and the report's −1,9% bound does not capture this",
  "recommended_followups": [
    "Explain the 2026 NII +34,5% and opex +32% jump from the Q3 notes (interest income/expense breakdown, TM on NII; check for gross-up/reclass vs real margin) — the single largest open driver",
    "Resolve VCBNeo consolidation: OCR/read KT2025 TM1 + Q3 TM1(d)/TM2(e); if consolidated, drop the historic-loss sensitivity and keep only future-support risk",
    "Replace the 'FY2025 bound' with a component-consistent stress: 2025 margin × current CC (≈2,32%) and 9T/26 margin × cycle CC (≈2,69%)",
    "Show a two-stage retention-consistent model (retention ~89%, g1 = ROE×b for N years) in both directions, or justify the Gordon payout of 54%",
    "Obtain Pillar 3 / CET1 / LDR TT22 at 30/06/2026 before CONFIRMED"
  ],
  "summary": "Rev 4's arithmetic and audited inputs are verified and reproduce exactly; the centre moved only −1% and each move traces to a sourced r3 item. Its central claim that the base window is independently corroborated does not hold: FY2025 and 9T/26 reach the same ~2,83% spread through opposite margin/credit-cost mixes, and the 2026 margin rebound behind the base is still unexplained. A component-consistent downside is about −35% (≈ the bear case) and a through-cycle-CC reading about −10%. Upward, the Gordon payout assumption versus VCB's actual ~89% retention understates value by about +4–6%. On VCBNeo, the Q3 notes list it as a consolidated 100% subsidiary, which contradicts rev 1's 'exempt' claim and probably makes the −2…−8% sensitivity a double count. Bank-mandatory CET1/LDR remain absent. The centre is one defensible reading within roughly ±10% that the report already shows, but it is not established."
}
<<<END_VERDICT>>>