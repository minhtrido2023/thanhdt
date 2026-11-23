**Kết luận: INCONCLUSIVE, độ tin cậy medium.** Số học của mô hình đúng. Nhưng tâm vẫn phụ thuộc vào ba giả định không kiểm chứng được, mỗi cái kéo tâm hơn 5%, và có một hạng mục lớn bị bỏ sót. Các mục giá thị trường, ADV và "biên an toàn" trong báo cáo tôi bỏ qua khi chấm mô hình, đúng ràng buộc mù.

**Kiểm chứng độc lập (khớp):**
- Tra BQ `ticker_financial` NP_P0 của VCP:
  - Cộng 4 quý 2025: 75,24 + 103,31 + 125,38 + 137,53 = **441,46 tỷ**, khớp N_2025.
  - TTM Q3/26: 137,53 + 140,19 + 177,70 + 245,38 = **700,80 tỷ**, khớp đầu vào bull.
- md5 của assumptions/model khớp file khoá. Tôi tự tính lại từ file giả định:
  - k = 1,1269 và phần thuỷ văn vượt = 85,7 tỷ (k = 1 thì 139,5).
  - N base = 332,86 tỷ, V = 2.893,6 tỷ, tức **34.534 đ/cp**. Khớp.

**Theo chiều ĐẮT (tâm có thể quá cao):**
1. **Chọn k = 1,127 thay vì Etb thiết kế.**
   - Báo cáo dẫn KH 2026 (1,15 × Etb) làm bằng chứng phụ cho k, nhưng bỏ qua KH 2025: 762,1 triệu kWh, gồm cả NSX và Đak Robaye cả năm, tức phần thuỷ điện chỉ ≈ 0,99 × Etb [BCTN25 dòng 1410]. Công ty chỉ nâng kế hoạch sau một năm nước nhiều.
   - Chuỗi 4 năm có 2 năm La Niña, và tỷ lệ năm 2024 là ước lượng.
   - k = 1,0 cho tâm 30.501 (−9,9%). Etb là trung bình nhiều năm do thiết kế công bố, nên chính việc lệch lên khỏi Etb mới cần cơ sở độc lập.
2. **ΔB 427,9 tỷ cộng đủ giá sổ** dù trong đó có LN 9T/26. Phần LN này chứa đúng biên phế liệu Q3 bất thường và lãi dồn tích chưa thu mà kịch bản bull đã loại ra. Đây là xử lý không nhất quán. Tôi ước tác động lên tâm dưới 2%, nên không lật kết luận.
3. **Hạn PPA và giá sau trả nợ của Cửa Đạt** chưa kiểm chứng được. Nhà máy đã khấu hao khoảng 75%; giả định Pc −20% từ năm 0 cho −14,2%. Báo cáo có ghi rõ đây là điểm mở.

**Theo chiều RẺ (tâm có thể quá thấp):**
- Đak Lô 1/3 (dự kiến phát điện 2027–2028) và Thác Ba chỉ được tính NPV0 theo giá sổ, nên giá trị tăng trưởng bằng 0.
- Kịch bản bear chồng ba cú cùng lúc: El Niño, lỗ 50% cho vay, lỗ 50% pool. Trong khi đó N của bear vẫn còn lãi cho vay của chính khoản bị coi là lỗ.
- Trọng số kịch bản tự đặt: bộ 0,25/0,45/0,30 cho 35.095 (+3,7%).
- Nếu tính k chỉ trên các năm đo được thật (2022, 2023, 2025) thì k = 1,156, tâm xấp xỉ 34,4k.

**Hạng mục thiếu (attack 8):**
- **Bảo lãnh khoản vay và hỗ trợ tài chính cho Đak Lô 1-3** của công ty mẹ (NQ HĐQT 05/2025 và 11/2025 [BCTN25 dòng 2415–2430]). Cả rev3b lẫn rev2 đều không nhắc tới. Đây là nghĩa vụ tiềm tàng trên khoản vay MB cho dự án tổng mức đầu tư 1.213 tỷ, không lượng hoá được.
- **Nghị quyết ĐHĐCĐ 2026** đã được công bố (`src/cb_dai-hoi-co-dong.html`) nhưng không được tải về, không được đọc.
  - Số cổ phiếu chỉ được xác nhận tới 30/09/2026 [Q3 p15].
  - Chưa rà các kế hoạch phát hành, ESOP, capex hay cổ tức được duyệt sau ngày đó.
- **Tiền cấp quyền khai thác tài nguyên nước và giấy phép** của các nhà máy đang chạy chưa được kiểm tra.
- Phần đạt: kiểm toán KT25 chấp nhận toàn phần, H1 soát xét; quỹ KT-PL đã vào base; capex Đak Lô/Thác Ba đúng là dự án tăng trưởng, không phải capex tuân thủ.

**Flip-flop:** tâm đi 40.273 → 34.522 → 32.605. Nước đi rev3 → rev3b có hai thành phần: haircut pool đi xuống và k tăng lên. Phần k tăng dựa trên nguồn mới (BCTN23 cho năm 2022), nên hợp lệ. Tôi không mở `kb/dd_price_zones.json` mà dùng bảng so sánh ngay trong báo cáo.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCP — DD rev3b (REPORT_rev3b.md), tâm 33.837 trước CK",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — pháp lý chỉ WARNING (phạt thuế ~102 triệu đ, rev2 §7); không thấy dấu hiệu chạm tài sản lõi trong tài liệu được dẫn. Rủi ro phân bổ vốn đã được ghi là rủi ro số 1",
    "optimistic_comp_sotp_bias": "fail (vừa) — không dùng comp, nhưng k=1,127 được đỡ bằng KH 2026 (1,15×Etb) trong khi bỏ qua KH 2025 ≈0,99×Etb (762,1 tr kWh gồm NSX, BCTN25); k=1,0 cho 30.501 (−9,9%). ΔB 427,9 tính đủ giá sổ dù chứa biên phế liệu Q3 và lãi dồn tích mà bull đã loại (không nhất quán, <2% tâm)",
    "data_provenance": "pass — N_2025 441,46 và TTM 700,8 khớp BQ NP_P0 theo từng quý; md5 khớp file khoá; các ước lượng (tỷ lệ 2024, gán bảng 1/2, chi phí biên 14,6%, trọng số) đều được gắn nhãn ước lượng",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất vị thế; số ADV là thông tin sau khoá, đã bỏ qua theo ràng buộc mù",
    "confirmation_bias_flipflop": "pass — 40.273→34.522→32.605; rev3b sửa hai chiều (pool haircut xuống, k lên nhờ nguồn mới BCTN23 cho năm 2022); báo cáo tự nhận ΔB là áp luật V4a chứ không do thông tin mới. Không mở dd_price_zones, dùng bảng so sánh trong báo cáo",
    "exit_discipline_gap": "na — không có claim sizing hay fear-buy; §10 có điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (không lượng hoá được) — (1) bảo lãnh khoản vay và hỗ trợ tài chính của công ty mẹ cho Đak Lô 1-3 (NQ HĐQT 05/2025, 11/2025, BCTN25) không được nhắc trong rev3b/rev2; (2) NQ ĐHĐCĐ 2026 đã công bố nhưng không được đọc — số cổ phiếu chỉ xác nhận tới 30/09/2026, chưa rà phát hành/ESOP/capex được duyệt; (3) tiền cấp quyền khai thác tài nguyên nước và giấy phép nhà máy đang chạy chưa kiểm; (4) hạn PPA Cửa Đạt chưa kiểm (độ nhạy −14,2%). Đạt: kiểm toán KT25 chấp nhận toàn phần, H1 soát xét, quỹ KT-PL, capex tăng trưởng, một lần biên phế liệu không có trong base 2025 (biên 1,5%)"
  },
  "independent_verification": "BQ ticker_financial NP_P0 VCP: 4 quý 2025 = 441,46 tỷ (khớp N_2025), TTM Q3/26 = 700,80 (khớp). Tự tính lại từ assumptions_rev3b.json: k=1,1269, phần vượt thuỷ văn 85,7 tỷ, N base 332,86, V base 2.893,6 tỷ = 34.534 đ/cp — khớp model_out_rev3b.json",
  "killer_objection": "Tâm phụ thuộc vào việc chọn mức thuỷ văn bình thường k=1,127 (trung bình 4 năm có 2 năm La Niña, 1 năm ước lượng) thay vì Etb thiết kế; kế hoạch 2025 của chính công ty ≈1,0×Etb. Chỉ riêng lựa chọn này kéo tâm 9,9%, cộng với hạn PPA Cửa Đạt chưa rõ (tới −14%) và bảo lãnh Đak Lô không được nêu",
  "recommended_followups": [
    "Tải và đọc NQ + tài liệu ĐHĐCĐ thường niên 2026: kế hoạch phát hành/ESOP/cổ tức cổ phiếu, danh mục đầu tư được duyệt, trần vay/bảo lãnh",
    "Định lượng nghĩa vụ bảo lãnh của công ty mẹ cho khoản vay MB Đak Lô 1-3 (thuyết minh cam kết/nợ tiềm tàng trong KT25/H1) và đưa vào bear",
    "Biện minh k bằng chuỗi thuỷ văn dài (lưu lượng nhiều năm của Cửa Đạt so với Etb) hoặc dùng k=1,0 ở base và để 1,127 thành độ nhạy; hiển thị KH 2025 cạnh KH 2026",
    "Thống nhất cách xử lý ΔB: trừ khỏi LN 9T/26 phần biên phế liệu bất thường và lãi dồn tích chưa thu giống như bull",
    "Kiểm tra tiền cấp quyền khai thác tài nguyên nước và giấy phép nhà máy đang chạy"
  ],
  "summary": "Số học và nguồn của rev3b đúng: N 2025 và TTM khớp BQ từng quý, mô hình tính lại ra đúng 34.534 đ/cp ở base. Kết luận chưa đứng vững vì ba điểm. Thứ nhất, mức thuỷ văn bình thường k=1,127 là lựa chọn kéo tâm 9,9%, được đỡ bằng KH 2026 nhưng bỏ qua KH 2025 ≈Etb. Thứ hai, hạn PPA Cửa Đạt chưa kiểm chứng. Thứ ba, báo cáo bỏ sót bảo lãnh vay Đak Lô 1-3 của công ty mẹ và chưa đọc NQ ĐHĐCĐ 2026. Theo chiều ngược lại, dự án tăng trưởng chỉ được tính NPV0 và bear chồng ba cú sốc, có thể làm tâm thấp đi. Không phát hiện lỗi đơn lẻ nào lượng hoá được trên 5% để kết luận REFUTED; giá thị trường trong báo cáo đã bị bỏ qua khi đánh giá."
}
<<<END_VERDICT>>>