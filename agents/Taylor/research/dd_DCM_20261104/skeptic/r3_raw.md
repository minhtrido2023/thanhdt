**Kết luận: REFUTED (độ tin trung bình).** Rev8 tự mâu thuẫn trong cách xử lý quỹ KH&CN. Lỗi này đẩy tâm theo chiều **RẺ** (tâm bị đặt quá thấp), cỡ khoảng +1,0…+2,5k đ/cp, trung tâm ≈ +2,0k (≈7,4% tâm). Mức này vượt ngưỡng trọng yếu 5%.

**Đòn chính — chiều RẺ (bỏ sót / không nhất quán):**
- S2 coi **số dư** quỹ 1.059 tỷ gần như vốn chủ, chỉ mất 11% (thuế kỳ trích + lãi). Nhưng **dòng trích hằng năm** vẫn bị tính mất 100%. Khoản này là ≈200–250 tỷ/năm trước thuế, nằm trong QLDN (REPORT_r3:66: Q2/26 trích 249,6; VDSC Q3/26 dòng 194). Nó đã trừ sẵn trong LNST lịch sử dùng để hồi quy.
- Lưới grep cho thấy `model_r5/r6/r7/r8` không có điều chỉnh nào cho dòng trích này. Chỉ có `nc_adj=-khcn*KHCN` áp lên số dư (`model_r7.py:83`).
- Theo đúng logic S2, chi phí kinh tế của khoản trích (bỏ không chi thì chỉ mất ~11%; chi cho thiết bị thì V4a NPV=0) thấp xa so với 100%. Ước lượng phần bị trừ thừa:
  - 200 tỷ × (1−20% thuế) × 0,89 / 13,5% / 529,4tr cp ≈ **+1.990 đ/cp**.
  - Dải theo mức trích: 95 tỷ → +0,95k; 250 tỷ → +2,49k.
- Quỹ tăng 857 → 1.059 tỷ trong 9T/26 dù đã trích 249,6, tức chỉ chi ≈47 tỷ. Quỹ chủ yếu tích luỹ, không chi.
- Nếu quỹ có tài trợ thiết bị HTS/LTS thì khoản đó còn bị **trừ lần hai** qua capex duy trì M.

**Phản đòn — chiều ĐẮT:**
- Khoản +1.781 của S2 dựa trên thông tin tham khảo từ legal-vn. NĐ 320/2025 và TT 20/2026 chưa được kiểm. Mức lãi "≈1 điểm" là ước lượng.
- Hồi quy cửa sổ 2021+ vẫn dự báo **quá cao** năm KT 2025 (−406/−247 tỷ). Phần dư TTM thì lệch hai phía (−9,3%/+3,2%), cho thấy tung độ gốc có thể hơi cao.
- D&A 2018–23 suy từ BQ, không lấy từ BCTC gốc. Thuyết minh TSCĐ / lịch đại tu chưa đọc (S5).

**Đã kiểm độc lập:** 0,89×1.059,37/529,4 = 1.781 đ và 0,11×… = 220 đ, khớp cầu nối §2 và độ nhạy §4. Số cổ phiếu 529,4tr khớp mã 411 = 5.294 tỷ. Thuế dài hạn TAX_LR = 20% từ 2027 có trong `model_r2.py:11`.

Tôi không mở `kb/dd_price_zones.json` (ràng buộc mù của nhiệm vụ). Giá 30.400 có trong báo cáo; tôi bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "DCM (PVCFC) — DD rev8 23/11/2026, tâm 26.780 đ/cp sau CK",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo tự ghi không đủ điều kiện §2.5, không có claim fear-buy",
    "scandal_migration_risk": "pass — WARNING §9 (HĐ khí bên liên quan PVN→PV GAS→DCM, SĐBS 12 dự thảo, 332 tỷ hạn chế MBV, thù lao ×3,25) được nêu và giữ ngoài base; không thấy dấu hiệu lan sang pháp nhân trong hồ sơ; báo cáo tự nhận không tra lại tin pháp lý từ 04–05/11 (khoảng trống ~18 ngày)",
    "optimistic_comp_sotp_bias": "pass — không dùng comp/SOTP; mô hình hồi quy biên urê–khí với lưới đối xứng 138/179/220 và 2 cửa sổ hồi quy; biến thể 4 cửa sổ (+2.044) bị loại khỏi headline vì phần dư 2024/25 xấu — đúng chiều thận trọng, có bằng chứng",
    "data_provenance": "fail (một phần) — D&A 2018–23 suy từ BQ (EBITDA−EBIT), không có BCTC gốc; S2 +1.781 dựa trên legal-vn (thông tin tham khảo), NĐ 320/2025 và TT 20/2026 chưa kiểm; lãi '≈1 điểm' là ước lượng; S5 thuyết minh TSCĐ chưa đọc. Số cổ phiếu 529,4tr (mã 411) và thuế 20% từ 2027 có nguồn",
    "liquidity_capacity_realism": "na — sizing 0% hiện tại; CK căn bậc hai 0,585% @5 tỷ trên ADV 89 tỷ là hợp lý, không có claim khớp lệnh",
    "confirmation_bias_flipflop": "pass có cảnh báo — xử lý quỹ KH&CN dao động r3 (không trừ) → rev7 (trừ 100%) → rev8 (trừ 11%), nhãn TRÊN→TRONG; lý do rev8 là đầu vào mới (legal-vn 23/11, lỗi dòng BQ 2021Q4 do skeptic r2 phát hiện), nhưng sửa sau khi đã biết giá (báo cáo tự khai). Không mở sổ vùng giá vì ràng buộc mù của nhiệm vụ",
    "exit_discipline_gap": "pass — tranche đầu 2% NAV khi giá ≤0,85×tâm, chờ user duyệt; HARD ABANDON > P90; các mốc làm lại định giá được nêu",
    "missing_items": "fail — (1) DÒNG trích quỹ KH&CN hằng năm (~95–250 tỷ trước thuế; 249,6 năm 2026 theo REPORT_r3:66, VDSC Q3/26) nằm trong QLDN của LNST hồi quy và bị coi là mất 100%, trong khi S2 coi SỐ DƯ chỉ mất 11% — không nhất quán; tâm thấp khoảng +0,95…+2,49k (trung tâm ≈+1,99k, 7,4%) ⇒ trọng yếu, định lượng được; có thể còn trừ trùng với M nếu quỹ tài trợ thiết bị duy trì. (2) Hạn thuê đất / giấy phép nhà máy Cà Mau so với chân trời vĩnh viễn: không thấy nêu (chưa định lượng). (3) Khối lượng khí cam kết sau 24/4/2032: nêu ở biến thể, không vào base. Đạt: số dư quỹ phúc lợi 265 tỷ + trích 5,97%, ý kiến kiểm toán FY2025 chấp nhận toàn phần, cơ sở số cổ phiếu, khoản một lần, capex cam kết TM16, bên liên quan"
  },
  "independent_verification": "Tính lại tác động S2: 0,89×1.059,37/529,4 = 1.781 đ/cp và 0,11×1.059,37/529,4 = 220 đ/cp — khớp cầu nối §2 và độ nhạy 'quỹ 0% +220'. Xác nhận TAX_LR = 0,20 (model_r2.py:11) và nc_adj chỉ áp lên số dư quỹ (model_r7.py:83). Grep model_r2/r5/r6/r7/r8: không có điều chỉnh nào cho dòng trích hằng năm.",
  "killer_objection": "Báo cáo nâng tâm +1.781 bằng lập luận quỹ KH&CN chủ yếu là vốn của cổ đông (chỉ mất thuế + lãi nếu không chi), nhưng lại giữ nguyên khoản trích ~200–250 tỷ/năm trong LNST vĩnh viễn như chi phí mất trắng. Áp lập luận đó nhất quán thì tâm tăng thêm ~+1–2,5k (lên ≈28,8k). Nếu ngược lại quỹ thực sự phải chi cho hạng mục không sinh giá trị thì +1.781 của S2 sai. Dù theo cách nào, tâm hiện tại nằm ở một điểm lai không nhất quán.",
  "recommended_followups": [
    "Lấy số trích quỹ KH&CN từng năm 2021–25 (TM QLDN; làm rõ 196,7 vs 95,0 năm 2025), cộng lại phần trích ×(1−t) vào LN hồi quy, rồi trừ phần mất kinh tế theo đúng tỷ lệ S2 (11% hoặc theo biến thể)",
    "Đối chiếu khoản chi từ quỹ với capex LCTT mã 21 để loại phần trừ trùng với M",
    "Kiểm NĐ 320/2025 và TT 20/2026 (nguồn gốc, không chỉ legal-vn) trước khi giữ +1.781",
    "Nêu hạn thuê đất / giấy phép nhà máy Cà Mau so với giả định vĩnh viễn g=0",
    "Tra lại tin pháp lý/quản trị sau 05/11"
  ],
  "summary": "Rev8 truy nguồn tốt (số cổ phiếu, thuế 20% từ 2027, quỹ phúc lợi, kiểm toán FY2025, cầu nối tái lập được) và đã minh bạch chuyện sửa sau khi biết giá. Nhưng mô hình xử lý quỹ KH&CN hai kiểu: số dư chỉ trừ 11% theo lập luận pháp lý S2, còn dòng trích hằng năm ~200–250 tỷ đã nằm trong chi phí QLDN của LNST hồi quy thì vẫn coi là mất 100% vĩnh viễn. Theo chính logic của S2, tâm bị đặt thấp khoảng 1–2,5k đ/cp (trung tâm ~7%), có thể thêm phần trừ trùng với capex duy trì. Chiều ngược lại, +1.781 của S2 dựa trên nghị định/thông tư chưa kiểm và lãi ước lượng, và hồi quy 2021+ vẫn dự báo quá cao năm KT 2025. Vì sai lệch nội tại trọng yếu (>5%) và định lượng được, kết luận là REFUTED. Cần làm lại cùng lúc dòng trích và số dư quỹ theo một quy tắc duy nhất."
}
<<<END_VERDICT>>>