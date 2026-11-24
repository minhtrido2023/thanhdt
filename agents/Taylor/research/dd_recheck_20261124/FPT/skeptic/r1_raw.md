**Kết luận: INCONCLUSIVE, độ tin cậy trung bình.** Phần tái chạy cơ học của bản recheck đúng. Nhưng còn một hạng mục then chốt chưa đọc được nên chưa thể CONFIRMED: cam kết capex data center / AI factory. Ngoài ra có vài khoản trừ nhỏ bị bỏ sót, cộng lại có thể kéo tâm xuống khoảng 6–8%. Các khoản này bị bù một phần bởi các lực kéo lên: r nằm trên dải Ke, và g kịch bản cơ sở thấp hơn đà tăng trưởng LFL hiện tại.

**Đã tự kiểm lại**
- **Lợi nhuận và dòng tiền khớp nguồn:**
  - Lợi nhuận 9 tháng 2026 là 7.776,4 tỷ, lãi liên kết 2.220,3 tỷ, lợi ích cổ đông không kiểm soát 1.165,8 tỷ. Cả ba khớp `notes_q3_bctc.md` (mã 60/27/429).
  - Tiền cộng HTM là 28.830 tỷ, vay 16.596 tỷ, tiền ròng 12.233 tỷ.
  - Số cổ phiếu 1.885,73 triệu khớp vốn góp 18.857 tỷ.
- **Đối chiếu BQ `ticker_financial`:** LNST mẹ Q4/25 là 2.509,52 tỷ, khớp. Tổng Q1+Q2+Q3/26 là 7.778,1 tỷ, khớp LNST mẹ 9 tháng.
- **Lợi nhuận lõi:** tôi tự tính lại được 6.705 tỷ. Phần ngoài DCF ≈ 23.459 đ/cp, tức phần DCF ≈ 59% của tâm.
- **Gốc so sánh của TTM:** ghép Q4/25 (báo cáo gốc, còn hợp nhất FTEL) với 9 tháng 2026 (FTEL theo vốn chủ sở hữu) là nhất quán ở mức lợi nhuận phần công ty mẹ. Không có đếm hai lần FTEL.

**Chiều ĐẮT (tâm có thể quá cao)**
- **Cam kết capex data center / AI factory chưa đọc.** Bản báo cáo tự thừa nhận điều này. Dòng tiền tự do 9 tháng 2026 âm 1.077 tỷ (CFO 952 tỷ, capex 2.029 tỷ). Đây là lý do chính cho kết luận INCONCLUSIVE.
- **Quỹ khen thưởng phúc lợi 1.477 tỷ chưa trừ.** Đây là nợ phải trả nhưng tiền tương ứng vẫn được cộng vào tiền ròng: khoảng −783 đ/cp (−1,4%).
- **Trích quỹ phúc lợi hằng năm từ lợi nhuận chưa mô hình hoá:** khoảng −3% nếu tỷ lệ trích là 5%. Tỷ lệ này tôi chưa kiểm, cần nghị quyết ĐHĐCĐ.
- **Pha loãng ESOP chưa tính:** 9 tháng 2026 phát hành 108 tỷ mệnh giá, khoảng 0,57%/năm, ước khoảng −2,5%.
- **Hệ số chuyển đổi kịch bản cơ sở 0,75** cao hơn thực tế FY25 (0,60) và 9 tháng 2026 (−0,12). Dùng 0,60 thì tâm −1,85%.
- **Tâm vẫn gồm cổ tức 1.000 đ** chốt quyền 30/11. Sau ngày giao dịch không hưởng quyền, tâm giảm khoảng −1,7%.

**Chiều RẺ (tâm có thể quá thấp)**
- **r 13,5% nằm trên đầu trên dải Ke 12,3–13,4%:** tâm có thể cao hơn từ +0,5% đến +6,7%.
- **g kịch bản cơ sở 9% thấp hơn đà tăng trưởng hiện tại:** LNST LFL 9 tháng +13,7%, LNTT khối Công nghệ +16,6%. Dùng g 12% thì tâm +3,3%.
- **Giá trị các công ty liên kết khác (1.500 tỷ) chỉ là ước lượng**, chưa có số kiểm chứng.
- **XDCB "Khác" 371 tỷ chưa cộng:** khoảng +0,3%.

**Các phần khác**
- **Không có đảo chiều kết luận:** tâm giữ nguyên 57.312 so với r3. Tôi không mở `dd_price_zones.json` theo ràng buộc mù.
- **Mù giá:** tôi bỏ qua mọi giá thị trường có trong báo cáo khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "FPT — DD recheck 24/11/2026 (re-run r3, chỉ đổi r; tâm 57.312 đ/cp)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass (có caveat) — rủi ro pháp lý cốt lõi đã hiện thực hoá và đã được định giá: FTEL ra khỏi hợp nhất từ 01/01/2026 theo Công văn 1906 ngày 18/03/2026 của Bộ Công an (notes:333), mô hình định giá FTEL = thị giá FOX × 45,66%. Báo cáo chỉ để WARNING; quét pháp lý sau 01/11 vẫn còn mở (§3 Việc còn mở #2)",
    "optimistic_comp_sotp_bias": "pass — không dùng comp. Phần SOTP: FOX 9.624 đ/cp và FRT 6.267 đ/cp theo thị giá BQ, chiết khấu FTEL 0% (đã có trục 30/15/0% song song); OTHER_ASSOC_BOOK 1.500 tỷ là [UL], có trục oth −1.300…+2.600 đ/cp",
    "data_provenance": "pass — pat9 7.776,4 / assoc9 2.220,3 / lợi ích CĐKKS 1.165,8 / tiền+HTM 28.830 / vay 16.596 / SH 1.885,73tr đều khớp notes_q3_bctc.md; Q4/25 2.509,5 khớp BQ NP_P0 2025Q4. Còn [UL]: lãi liên kết Q4/25 600 tỷ (G10), OTHER_ASSOC_BOOK 1.500 tỷ",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất sizing mới; giữ ngoại lệ 5% NAV đã duyệt 05/11",
    "confirmation_bias_flipflop": "pass — so với r3: tâm 57.312 giữ nguyên, phần thay đổi chỉ là thêm dòng hiển thị (E15/E16/dải Ke/V6). Không mở dd_price_zones.json theo ràng buộc mù của brief",
    "exit_discipline_gap": "na — không có claim fear-buy/sizing mới",
    "missing_items": "fail (không có mục nào đơn lẻ >5%, nhưng có 1 mục trọng yếu chưa lượng hoá được) — (1) cam kết capex data center/AI factory: CHƯA ĐỌC, FCF 9 tháng 2026 = −1.077 tỷ, không lượng hoá được ⇒ INCONCLUSIVE; (2) quỹ khen thưởng phúc lợi 1.477 tỷ nằm trong nợ nhưng tiền tương ứng vẫn cộng vào NC ≈ −783 đ/cp (−1,4%); (3) trích quỹ phúc lợi hằng năm từ LNST chưa mô hình hoá ≈ −3% nếu trích 5% (tỷ lệ chưa kiểm); (4) pha loãng ESOP ~0,57%/năm (108 tỷ mệnh giá 9 tháng 2026) ≈ −2,5%; (5) tâm còn gồm cổ tức tiền 1.000 đ chốt 30/11 ≈ −1,7% sau ngày GDKHQ. Cộng (2)–(4) ≈ −6–7%. Ý kiến kiểm toán: BCTC Q3 là báo cáo giữa niên độ, chưa kiểm ý kiến soát xét",
    "symmetry": "{too_high_checked: 9, too_low_checked: 10, too_low_items: ['r 13,5% > đầu trên dải Ke 13,4% (+0,5%…+6,7%)', 'g CO_SO 9% < LNST LFL 9 tháng 2026 +13,7% / LNTT khối CN +16,6% (g 12% ⇒ +3,32%)', 'OTHER_ASSOC_BOOK 1.500 tỷ ước lượng, có thể thấp so với sổ liên kết 10.753 tỷ', 'XDCB Khác 371 tỷ chưa cộng (+0,3%)', 'tiền khách ứng trước 2.370 tỷ không trừ ở base (kiểm: đã đúng hướng cao)', 'lợi ích CĐKKS trừ theo sổ dù LN CĐKKS 9 tháng ≈ −1,6 tỷ (kiểm: hợp lý, không nâng)', 'lãi LK Q4/25 600 tỷ: nếu thực tế thấp hơn thì tâm cao hơn (chưa kiểm)', 'trọng số đối xứng 0,275/0,45/0,275 so với lịch sử tăng trưởng của mã', 'RONIC terminal = Ke dù ROIC5Y 17,7% (luật moat NARROW — giữ)', 'chiết khấu FTEL 0% (đã ở mức cao nhất)']}"
  },
  "independent_verification": "Tự tính lại core_op = (7.776,4−2.220,3)+(2.509,5−600)−671×4/3×0,85 = 6.705 tỷ và NC = 12.233 tỷ từ notes_q3_bctc.md — khớp mô hình. BQ ticker_financial: NP Q4/25 2.509,52 tỷ (khớp); Q1+Q2+Q3/26 = 7.778,1 tỷ = LNST mẹ 9 tháng (khớp). Tái chạy model_r3.py: tâm base 57.312, XẤU/CƠ SỞ/TỐT = 45.521/57.665/66.773 (trước CK), phần ngoài DCF 23.459 đ/cp. Probe: g CO_SO 12% ⇒ +3,32%; conv CO_SO 0,60 ⇒ −1,85%",
  "killer_objection": "Báo cáo tự nhận chưa đọc thuyết minh cam kết vốn, trong khi FCF 9 tháng 2026 âm 1.077 tỷ và capex 2.029 tỷ; conv CO_SO 0,75 vẫn được giữ. Một cam kết capex data center/AI chưa ghi nhận, cộng các claim ngoài vốn chủ (quỹ phúc lợi, ESOP), có thể kéo tâm xuống >5% — đúng mẫu lỗi QTP",
  "recommended_followups": [
    "Đọc thuyết minh cam kết vốn/capex (data center, AI factory, khuôn viên giáo dục còn phải chi) trong BCTC Q3/2026 và nghị quyết HĐQT 12 tháng gần nhất; phân loại growth vs tuân thủ",
    "Lấy tỷ lệ trích quỹ khen thưởng phúc lợi và kế hoạch ESOP từ nghị quyết ĐHĐCĐ 2026; trừ số dư quỹ 1.477 tỷ khỏi NC hoặc chạy độ nhạy",
    "Ghi rõ tâm còn gồm cổ tức 1.000 đ (chốt 30/11); sau ngày GDKHQ cập nhật tâm −1.000 đ",
    "Kiểm lãi liên kết Q4/25 (G10) từ BCTN25 bản điều chỉnh theo phương pháp vốn chủ",
    "Quét pháp lý FTEL/Bộ Công an sau 01/11/2026",
    "Cân nhắc kịch bản g CO_SO theo đà LFL hiện tại (12–14%) như độ nhạy chiều lên, song song với chặn conv"
  ],
  "summary": "Phần tái chạy cơ học của bản recheck FPT đúng: các số then chốt (LNST, lãi liên kết, CĐKKS, tiền ròng, số cổ phiếu, LNST Q4/25) khớp BCTC Q3/2026 và BQ; bảng độ nhạy r tái lập được. Tuy vậy, kiểm thiếu hạng mục (attack 8) chưa qua. Cam kết capex data center/AI factory chưa được đọc trong khi FCF 9 tháng 2026 âm. Mô hình cũng bỏ qua quỹ khen thưởng phúc lợi 1.477 tỷ (−1,4%), trích quỹ hằng năm (~−3%) và pha loãng ESOP (~−2,5%), cộng lại ≈ −6–7%. Chiều ngược lại có lực kéo lên có cơ sở: r 13,5% cao hơn dải Ke 12,3–13,4% (đến +6,7%), và g cơ sở 9% thấp hơn đà LFL +13,7% (g 12% ⇒ +3,3%). Hai chiều gần bù nhau nên chưa đủ để bác tâm, nhưng chưa thể CONFIRMED khi hạng mục capex còn bỏ trống."
}
<<<END_VERDICT>>>