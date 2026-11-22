**Kết luận: REFUTED (bác bỏ), độ tin cậy trung bình.** Tâm 24.326 đ/cp được neo vào một nền lợi nhuận trộn hai chế độ khấu hao. Trong mẫu hồi quy 2021–25, khấu hao (D&A) tụt bậc mà báo cáo không nhắc tới. Ước lượng của tôi là chỉ riêng lỗi này đã làm lệch tâm cỡ +12%, và cùng lúc báo cáo không mô hình hoá capex thay thế, là khoản kéo tâm xuống. Theo quy tắc price-blind, tôi bỏ qua mọi giá thị trường có trong báo cáo.

**Những gì tôi tự kiểm lại:**
- **Khớp:**
  - Net cash 7.539,1 tỷ: tiền 3.470,5 + HTM 4.555,6 + phong toả 2.219,9 − vay 2.699,3 − 7,5. Ra đúng 14.241 đ/cp.
  - Số cổ phiếu 529,4 triệu: khớp `OShares` trong BQ ở mọi quý từ 2021.
  - Hệ số hồi quy: tôi cộng LNST năm từ BQ `ticker_financial` (2021 1.917 · 2022 4.264 · 2023 1.107 · 2024 1.420 · 2025 1.960 tỷ). Biên proxy tôi tự dựng từ giá urê/Brent nhớ lại, và 2025 lấy số 257 của báo cáo, nên các biên proxy là ước lượng. Kết quả hệ số ≈ 8,85, khớp số 8,84 trong model.
- **Không tái lập được:** `calc/model.py` đọc `calc/bq_np_hist_out.csv` và `bq_commod_out.csv`, nhưng cả hai file đều không có trên đĩa. Chạy lại model báo FileNotFoundError.

**Các điểm tấn công:**
1. **Điểm chí mạng: nền lợi nhuận bị lẫn chế độ khấu hao (chiều RẺ, tức tâm bị đặt quá thấp).**
   - Lấy EBITDA − EBITM×doanh thu TTM trong BQ (số suy ra, ước lượng): D&A ≈ 1.130 tỷ (2021), ≈ 1.270 (2022), ≈ 1.060 (2023), rồi chỉ còn ≈ 230 (2024) và ≈ 300 (TTM Q3/26).
   - Nghĩa là các năm 2021–23 bị trừ khoảng 1 nghìn tỷ/năm chi phí không tiền mặt, khoản mà nay không còn lặp lại.
   - Hiệu chỉnh khoản này trong hồi quy: hệ số 8,85 → ≈ 10,8, LNST ở biên 179 tăng ≈ +280 tỷ/năm. Quy ra tâm ≈ **+2.900 đ/cp (+12%)** (ước lượng).
   - Báo cáo chỉ viết "nhà máy đã khấu hao gần hết" mà không tách hiệu ứng này khỏi mẫu.
2. **Chiều ĐẮT (tâm bị đặt quá cao):**
   - Capex thay thế không có trong báo cáo nhà đầu tư. Bản r6 tự đưa đơn vị −1.233 đ/cp cho mỗi 100 tỷ/năm, nhưng không vào tâm. Capex 9T/26 là 546 tỷ (gồm cả capex tăng trưởng), so với D&A ≈ 300.
   - Mô hình dùng dòng vĩnh viễn trên một nhà máy vận hành từ 2012, nhưng không có vòng đời nhà máy hay chi phí đại tu.
   - Quỹ KH&CN 1.059 tỷ (≈ 2.000 đ/cp, ≈ 8% tâm) không bị trừ, với lý lẽ "chi cho chính DCM". Nếu đó là chi tiêu bắt buộc, tiền mặt đã bị ghim, thì nó tương đương capex cam kết.
3. **Tấn công 6 (đổi kết luận giữa các bản):**
   - Báo cáo 05/11 (r5, tâm 24.326) đã bị thay bởi REPORT_r6 ngày 08/11 (điểm base 24.818) và ADDENDUM_5F. Bản r6 có thêm phong toả @50% và sửa lệch chiết khấu một năm.
   - Trước đó tâm dao động 27.021 (r2/r3) → 23.644 (r4) → 24.326 (r5). Mỗi lần đổi đều kèm cầu nối và đính chính cụ thể, nên không thấy thiên lệch xác nhận. Nhưng bản đang phản biện không phải bản mới nhất.
4. **Các mục đạt:**
   - Pháp lý được nêu đủ: 332 tỷ bị hạn chế, kết luận Thanh tra 2023, thù lao ×3,25, giao dịch với nhóm PVN.
   - Số liệu khí trích từ văn bản dự thảo và được gắn nhãn rõ.
   - So sánh bội số chỉ để tham khảo, không làm đầu vào.

<<<VERDICT_JSON>>>
{
  "case_topic": "DCM — DD investor report 05/11/2026 (r5, tâm 24.326 đ/cp)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — cảnh báo pháp lý có nêu (332 tỷ hạn chế tại NH Hiện đại TM5, KL Thanh tra CP 07/7/2023 đã phân bổ hết, ủy quyền HĐQT sửa HĐ khí không qua cổ đông thiểu số); không thấy dấu hiệu lan sang pháp nhân hay tài sản lõi",
    "optimistic_comp_sotp_bias": "pass — DCF dựng từ nền tảng; bội số DPM/DDV chỉ để đối chiếu, không làm đầu vào; hai nhánh CYC và ADMIN cho cùng giá trị vì P(policy) áp độc lập, có ghi rõ",
    "data_provenance": "fail — model.py đọc calc/bq_np_hist_out.csv và bq_commod_out.csv nhưng cả hai không có trên đĩa ⇒ không tái lập được hồi quy, tức neo lợi nhuận của tâm. Net cash và số cổ phiếu thì truy được và khớp",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất sizing; chiết khấu thanh khoản ≈ 0 ở cỡ sleeve",
    "confirmation_bias_flipflop": "fail (nhẹ) — bản 05/11 (r5 24.326) đã bị thay bởi REPORT_r6 08/11 (base 24.818) và ADDENDUM_5F (sửa lệch chiết khấu 1 năm, phong toả @50%); chuỗi tâm r2/r3 27.021 → r4 23.644 → r5 24.326 có cầu nối và đính chính cụ thể, không thấy thiên lệch, nhưng bản đem phản biện không phải bản mới nhất",
    "exit_discipline_gap": "na — báo cáo định giá, không có luận điểm vào lệnh; mục 7 đã có trigger hai chiều",
    "missing_items": "fail — (1) chế độ khấu hao trong năm gốc: D&A BQ suy ra (ước lượng) ≈1,1–1,3 nghìn tỷ/năm 2021–23 so với ≈0,23–0,30 nghìn tỷ 2024–26 nằm ngay trong mẫu hồi quy 2021–25, không được tách ⇒ tâm có thể thấp ≈ +2.900 đ/cp (+12%, ước lượng). (2) capex thay thế/vòng đời nhà máy (vận hành 2012) với dòng vĩnh viễn không có trong báo cáo nhà đầu tư (r6: −1.233 đ/cp mỗi 100 tỷ/năm); capex 9T/26 546 tỷ so với D&A ≈300 ⇒ chiều giảm, chưa định lượng. (3) quỹ KH&CN 1.059 tỷ (≈2.000 đ/cp, ≈8% tâm) không trừ khỏi net cash, có thể là tiền ghim cho chi bắt buộc. Các mục đạt: số cổ phiếu 529,4tr (khớp BQ OShares), quỹ KTPL đã trừ, kiểm toán FY2025 Deloitte chấp nhận toàn phần, giao dịch bên liên quan PVN/PV GAS có nêu, capex nâng công suất 800–1.000 tỷ tính NPV=0 có ghi rõ, khoản một lần 67,4 và 102,9 tỷ có nêu"
  },
  "independent_verification": "Net cash 3.470,5+4.555,6+2.219,9−2.699,3−7,5 = 7.539,1 tỷ = 14.241 đ/cp: khớp. OShares 529,4tr (BQ ticker_financial 2021Q1–2026Q3): khớp. LNST năm từ BQ 2021–25 (1.917/4.264/1.107/1.420/1.960 tỷ) hồi quy theo biên proxy ước lượng (giá urê/Brent nhớ lại, 2025 dùng 257 của báo cáo) cho hệ số ≈8,85, khớp 8,84 của model. Chạy lại model.py thất bại do thiếu CSV đầu vào.",
  "killer_objection": "Nền lợi nhuận (hồi quy LNST 2021–25, n=5) trộn hai chế độ khấu hao: các năm 2021–23 bị trừ ≈1 nghìn tỷ/năm khấu hao nay không còn, trong khi capex thay thế cho dòng vĩnh viễn trên nhà máy 14 năm tuổi không có trong mô hình. Tâm có thể sai ±10–12% theo cả hai chiều mà dải P10–P90 không phản ánh.",
  "recommended_followups": [
    "Lấy D&A thật 2021–25 từ thuyết minh BCTC kiểm toán; hồi quy lại trên LNST cộng ngược D&A hoặc trên EBITDA, rồi trừ capex duy trì chuẩn hoá",
    "Định lượng capex duy trì/đại tu và vòng đời nhà máy (thuyết minh TSCĐ: nguyên giá, khấu hao luỹ kế, thời gian khấu hao còn lại)",
    "Khôi phục và khoá md5 calc/bq_np_hist_out.csv, bq_commod_out.csv để mô hình tái lập được",
    "Làm rõ quỹ KH&CN 1.059 tỷ: nghĩa vụ chi bắt buộc hay tiền tự do; nếu bắt buộc thì trừ khỏi net cash",
    "Đem phản biện bản mới nhất (REPORT_r6/ADDENDUM_5F) thay cho bản 05/11 đã bị thay"
  ],
  "summary": "Bảng cân đối và số cổ phiếu của báo cáo DCM 05/11 khớp nguồn, phần pháp lý và hợp đồng khí được trình bày cẩn thận, có gắn nhãn dự thảo. Nhưng tâm 24.326 đ/cp dựa trên hồi quy LNST 2021–25 mà file đầu vào đã mất, không chạy lại được. Mẫu này lẫn hai chế độ khấu hao (≈1,1–1,3 nghìn tỷ/năm 2021–23 so với ≈0,23–0,30 sau đó, suy từ BQ), nên năng lực lợi nhuận hiện tại có thể bị đánh giá thấp khoảng 12%. Ngược lại, capex thay thế cho dòng vĩnh viễn và quỹ KH&CN 1.059 tỷ không được tính, kéo tâm xuống. Cả hai lỗi đều vượt ngưỡng 5% và không nằm trong dải P10–P90. Ngoài ra bản này đã bị r6/ADDENDUM thay. Kết luận: REFUTED; cần dựng lại nền lợi nhuận theo FCF (EBITDA − capex duy trì) trước khi dùng con số tâm."
}
<<<END_VERDICT>>>