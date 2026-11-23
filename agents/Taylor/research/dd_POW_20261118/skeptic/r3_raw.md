**Kết luận: INCONCLUSIVE (medium).** Số học của rev4 tái lập đúng, và thay đổi duy nhất (tách khoản hồi tố, làm tâm tăng +3,6%) có nguồn gốc kiểm được. Vẫn chưa CONFIRMED vì một hạng mục ngành điện trọng yếu vẫn chưa đóng được: hạn PPA và nguồn khí của CM1&2 và NT1, trong khi mô hình coi vốn di sản là vĩnh viễn. Lần này báo cáo không có thông tin mới nào đóng được hạng mục đó. Nếu tôi chuyển sang CONFIRMED thì chính là kiểu lật nhận định mà attack 6 cấm.

**Tôi đã tự tính lại:**
- **Tâm:** (28.939,8×8%/13,5% + 9.000 + 2.740 + 2.454,7 − 2.255) / 3.067,85 tr cp = **9.482** trước chiết khấu, **9.387** sau chiết khấu 1%. Khớp báo cáo.
- **Khoản hồi tố, đối chiếu CBTT 03/08 (`src/cbtt/2026-08-03_7013/post.html`):** ở công ty mẹ, 1.103 (tỷ giá VA1 2019–21) + 991 (quyết toán Cà Mau 1&2) + 381 (giảm trích O&M) = 2.475,6. VA1 và Cà Mau là nhà máy của công ty mẹ, nên giả định "100% thuộc mẹ" có cơ sở. Kỳ 2019–21 nằm sau cổ phần hoá, nên không lặp lại trường hợp 728,2 tỷ phải nộp PVN (của kỳ 2016–17).
- **ROE di sản 8%:** tôi dựng lại từ chuỗi ROE mẹ 2019–25, bỏ vốn chủ NT3&4 đang xây dựng (ước 9.000) khỏi mẫu số 2023–25, rồi rải khoản hồi tố về các năm trước. Ra **~8,1%**. Mức 8% có tái lập được, nhưng nằm ở cận trên.

**Chiều ĐẮT (tâm có thể quá cao):**
- Tính hồi tố theo 1,0× hơi rộng tay:
  - 381 tỷ và khoảng 280 tỷ ở Q3 là hoàn nhập dự phòng, không phải tiền thu từ EPTC. Riêng 381 tỷ là khoảng **−111 đ/cp** nếu chi phí O&M quay lại sau này.
  - Thuế hiệu dụng 10,9% thay vì 20%: **−82 đ/cp**.
  - Phần tỷ giá thường được thu dần nhiều năm, nên giá trị hiện tại thấp hơn mệnh giá.
  - Cộng lại khoảng −1…−2%, dưới ngưỡng trọng yếu 5%.
- ROE 8% dựa vào các năm 2019–21, khi đội máy còn trẻ hơn. Đây chính là chỗ rủi ro PPA/nguồn khí chạm vào.

**Chiều RẺ (tâm có thể quá thấp):**
- Mô hình ngầm định lợi nhuận khoảng 3.900 tỷ/năm, thấp hơn khoảng 27% so với mức cốt lõi năm hoá 2026 (~5.350).
- NT3&4 ghi NPV=0 theo sổ, dù 6T/2026 phát thêm hơn 2,6 tỷ kWh. Cả hai đều đã được báo cáo nêu như chuẩn hoá chu kỳ hoặc độ nhạy.

**Ràng buộc mù giá:** tôi không tra giá, không mở sổ vùng giá, và bỏ qua giá DNSE có trong báo cáo khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "POW — DD rev4 (REPORT_rev4.md, tâm 9.387 đ/cp, vùng 6.966–11.808)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — WARNING pháp lý được nêu: quyết toán CPH chưa duyệt (Deloitte FY2025 nhấn mạnh), giao dịch bên liên quan chưa kiểm chứng; không thấy tịch thu/huỷ hợp đồng/rút giấy phép trong 83 CBTT; chưa tra UBCKNN (báo cáo tự nêu)",
    "optimistic_comp_sotp_bias": "pass — không dựa vào comp; khung SOTP E_di sản×ROE/r + sổ tái lập 9.482/9.387; ROE 8% tự dựng lại ~8,1% (cận trên dải 7–8%, báo cáo tự nhận nghiêng lạc quan; độ nhạy −2pp ⇒ 8.004)",
    "data_provenance": "pass — hồi tố H1 2.475,6 = 1.103+991+381 khớp CBTT 03/08/2026 ở công ty mẹ (VA1, CM1&2 là nhà máy của mẹ ⇒ 100% mẹ có cơ sở); phần Q3 ~280 gắn nhãn ước lượng (dải 187–280); số cp, VCSH mẹ đã được r1/r2 kiểm; giao dịch bên liên quan gắn nhãn không kiểm chứng được",
    "liquidity_capacity_realism": "na — DD_GENERAL; sizing chỉ có điều kiện (2–3% NAV), ADV 63,3 tỷ/phiên lấy từ BQ cho vị thế ≤30 tỷ là hợp lý",
    "confirmation_bias_flipflop": "pass — rev3→rev4 chỉ thay đổi phương pháp theo yêu cầu skeptic r2 (tách hồi tố, +3,6%), có nguồn CBTT; nhãn không đổi; tôi chỉ đọc lịch sử phản biện của chính POW, không mở sổ vùng giá",
    "exit_discipline_gap": "na — DD_GENERAL; dù vậy báo cáo có các mốc T1–T5 khoá trước và điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (không định lượng được) — capex tuân thủ: QCVN19 VA1 trong base, nhà máy khí ở độ nhạy (pass); số cp/phát hành: 3.067,85tr theo TM23, đợt 281tr cp ×10.000 (pass); quỹ KTPL: độ nhạy (pass); kiểm toán FY2025 chấp nhận toàn phần + nhấn mạnh (pass); khoản một lần trong năm gốc: đã tách (pass); bên liên quan: chưa kiểm chứng (WARNING); PPA/nguồn khí CM1&2 và NT1: thời hạn và trữ lượng mỏ cấp khí chưa có, giá trị sổ theo nhà máy không công bố ⇒ không chặn được thiệt hại tài sản mắc kẹt (ước thô ≤~6% tâm nếu mắc kẹt toàn bộ phần sổ còn lại của nhà máy khí cũ) — trọng yếu nhưng không định lượng được"
  },
  "independent_verification": "Tái lập tâm (28.939,8×0,08/0,135+9.000+2.740+2.454,7−2.255)/3.067,85 = 9.482 → 9.387 sau CK: KHỚP. Đối chiếu hồi tố H1 với CBTT 03/08/2026: 1.103+991+381=2.475,6 ở công ty mẹ: KHỚP. Dựng lại ROE di sản: ~8,1% so với 8% của báo cáo: KHỚP (nhạy với ước lượng vốn chủ NT3&4 9.000).",
  "killer_objection": "Mô hình coi vốn di sản vĩnh viễn ở ROE chuẩn hoá có tỷ trọng các năm đội máy còn trẻ (2019–21), trong khi hạn PPA và tuổi thọ mỏ khí của CM1&2/NT1 chưa đo được và giá trị sổ theo nhà máy không có. Nếu nguồn khí cạn trước khi khấu hao hết, phần sổ chưa khấu hao bị mắc kẹt mà §C (đời hữu hạn có thu hồi vốn ⇒ +10…+16%) không phản ánh, và kịch bản xấu chỉ bao một cách gián tiếp. Chiều ngược lại: 1,0× cho phần hồi tố là hoàn nhập dự phòng (381 + ~280) cùng thuế 10,9% làm tâm cao khoảng 1–2%.",
  "recommended_followups": [
    "Lấy nguyên giá và giá trị còn lại TSCĐ theo nhà máy (BCTN 2025 / TM TSCĐ KT25) để chặn trên thiệt hại mắc kẹt của CM1&2+NT1. Đây là cách đóng hạng mục còn treo mà không cần hạn PPA",
    "Tra trữ lượng và kế hoạch cấp khí PM3-CAA/Cái Nước và Nam Côn Sơn cho CM1&2/NT1 (PVN/PV GAS CBTT) thay vì tìm hạn PPA",
    "Thay 1,0× bằng ~0,9× cho phần hoàn nhập dự phòng O&M (381 + ~280) và dùng thuế 20% cho hồi tố (−80…−190 đ/cp); kiểm lịch thu tiền chênh lệch tỷ giá VA1 (trả góp hay một lần)",
    "Tra UBCKNN và giá trị giao dịch bên liên quan KT25 bằng bản PDF gốc (OCR hỏng)"
  ],
  "summary": "Rev4 tái lập được số học (tâm 9.482/9.387) và thay đổi tăng tâm duy nhất (tách hồi tố 2.454,7 ghi 1,0×) có nguồn gốc kiểm được: CBTT 03/08 xác nhận 1.103+991+381=2.475,6 ở công ty mẹ, từ các nhà máy của mẹ. ROE di sản 8% dựng lại độc lập được ~8,1%, nằm ở cận trên. Hai chiều: tâm có thể cao hơn thực khoảng 1–2% vì phần hồi tố là hoàn nhập dự phòng, thuế hiệu dụng thấp và tỷ giá thu dần; tâm cũng có thể thấp nếu lợi nhuận cốt lõi 2026 (cao hơn ~27% so với mức mô hình ngầm định) bền vững hoặc NT3&4 có NPV>0. Hạng mục ngành bắt buộc vẫn chưa đóng: hạn PPA/nguồn khí CM1&2 và NT1, cùng giá trị sổ theo nhà máy, nên không chặn được rủi ro tài sản mắc kẹt. Báo cáo không có thông tin mới nào đóng được hạng mục này (PPA ký lại 2021 chỉ giảm một phần), nên giữ INCONCLUSIVE. Hạng mục này có thể đóng bằng cách chặn trên thiệt hại từ giá trị sổ theo nhà máy. Không tra giá; giá DNSE trong báo cáo bị bỏ qua khi đánh giá mô hình."
}
<<<END_VERDICT>>>