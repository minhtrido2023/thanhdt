**Kết luận: REFUTED, độ tin cậy trung bình.** Bản r3 sửa đúng lỗi quy ước ROE, nhưng chỉ sửa theo chiều làm tâm tăng. Phần chất lượng thu nhập lẽ ra kéo tâm xuống thì chỉ được xử lý như một lần xoá sổ trên số dư, và lại bỏ sót một dòng lãi dự thu. Thêm vào đó, cơ sở số cổ phiếu trước/sau quyền mua không được ghi nhãn, lệch khoảng 6,5%.

**Số đã tự kiểm lại từ BCTC kiểm toán 2025 (`src/bctn_2025.txt`), đều khớp:**
- Lãi thực thu 16.497.163 / 18.910.323 (LCTT, dòng 8628) so với lãi ghi nhận 21.601.251 / 18.681.257. Tỷ lệ thu tiền 76% năm 2025, 101% năm 2024.
- Lãi phải thu tín dụng 6.802.719 / 3.272.745 (dòng 11409).
- Quỹ khen thưởng phúc lợi chỉ 25,8 tỷ. VCSH 2025 tăng đúng bằng LNST (5.628), nên không có khoản nào ngoài vốn chủ ăn vào lợi nhuận giữ lại.
- Quy đổi ROE bình quân sang ROE đầu kỳ tính lại đúng: 14% → 15,05%, 12,5% → 13,33%.
- `model_r3.py` lấy BV đầu kỳ cộng 9.360 tỷ tiền quyền mua, trừ đi giá trị hiện tại của khoản tiền nộp, rồi chia cho 3.744 triệu CP. Cách này nhất quán nếu hiểu là giá trị trên mỗi cổ phiếu đang giữ quyền mua.

**Chiều ĐẮT (tâm có thể quá cao):**
1. **ROE nền lấy từ lợi nhuận đã bị lãi dồn tích thổi phồng.**
   - Năm 2025 lãi phải thu tín dụng tăng 3.530 tỷ. Nếu giữ tỷ lệ 1,854% dư nợ như 2024 thì với dư nợ tăng thêm 28.716 tỷ, phần tăng bình thường chỉ khoảng 532 tỷ. Phần vượt khoảng 3.000 tỷ trước thuế, tương đương ~6,5pp ROE.
   - Ngay ở mức tổn thất kỳ vọng 17,5% mà chính trục haircut của báo cáo dùng, ROE 2025 giảm ~1,1pp. 6T/2026 còn vượt thêm ~835 tỷ, ước lượng giảm ROE 2026E ~0,5pp.
   - Trục haircut chỉ xoá một lần trên số dư (−1,0%), trong khi đường ROE dự báo vẫn neo vào 15,3% / 14,4% chưa điều chỉnh.
   - Điều chỉnh khoảng −1pp ROE CƠ SỞ sẽ kéo tâm xuống khoảng −11%, vượt ngưỡng trọng yếu 5%. Đây là ước lượng.
2. **Lãi phải thu từ đầu tư chứng khoán bị bỏ sót.** Khoản này tăng 1.208 → 2.180 tỷ (+80%) trong 2025, không có trong trục haircut và không được giải thích. Chỉ riêng TPDN 1.961 tỷ thì không thể sinh ra mức dồn tích này.
3. **Đường ROE CƠ SỞ đi ngược xu hướng.** ROE đầu kỳ đang giảm (17,6% → 15,3% → 14,4%) và CASA mòn (28,3% → 20,4%), nhưng kịch bản vẫn cho ROE leo lên 15,1% sau khi VCSH tăng 20% từ quyền mua. Trọng số giữa XẤU và TỐT được đặt đối xứng.

**Chiều RẺ (tâm có thể quá thấp):**
- Ke trung tâm 13,5% nằm ngoài dải Ke nội địa 12,3–13,4% mà chính báo cáo nêu. Dùng 13,4% thì tâm +1,2%, dùng 12,3% thì +16%.
- Tỷ lệ thu tiền 9T26 đã hồi lên 91%. Nếu phần dồn tích chỉ là chênh lệch kỳ trả lãi của khoản vay dài hạn thì lập luận ở mục chiều ĐẮT số 1 yếu đi.

**Hạng mục thiếu (attack 8):**
- **Cơ sở số cổ phiếu trước/sau quyền mua không được ghi nhãn.** Tâm 14.674 là giá trị trên cổ phiếu còn giữ quyền mua. Sau ngày giao dịch không hưởng quyền, giá trị tương đương chỉ khoảng 13.713 đ/cp (−6,5%). Ngày chốt quyền chưa được xác định. Mọi so sánh nhãn hay luật 4 sau mốc đó sẽ lệch nếu không quy đổi.
- ESOP 2026 chưa kiểm chứng.
- Số liệu Q3/6T/2026 chỉ truy về ghi chú đọc ảnh (`calc/notes_read.md`), vì PDF gốc không còn. Gồm LC 9.229 tỷ và phải thu khác 18.501 tỷ; hai khoản này chỉ ảnh hưởng ở mức độ nhạy.
- Các mục còn lại đạt: chỉ tiêu ngân hàng (CAR, NPL, nhóm 2, bao phủ, LDR, CASA), ý kiến kiểm toán, bên liên quan, quỹ khen thưởng phúc lợi.

Tôi không xem giá thị trường. Các giá báo cáo tự nêu ở mục 1 và mục 8 đã được bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "MSB — DD r3 (RI ngân hàng, tâm 14.621 đ/cp sau CK), REPORT_r3.md 23/11/2026",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không có claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — không có mục WARNING pháp lý; bên liên quan 142,6 tỷ (KT25 TM42) không trọng yếu; ghi chú: phần pháp lý kế thừa r2, chưa tìm lại",
    "optimistic_comp_sotp_bias": "fail — không dùng comp, nhưng đường ROE CƠ SỞ 13,3→15,1% đi lên sau khi VCSH tăng 20% từ quyền mua, trong khi ROE đầu kỳ đang giảm 17,6→15,3→14,4% và CASA 28,3→20,4%; chiều ngược lại: Ke 13,5% nằm ngoài dải nội địa 12,3–13,4% do chính báo cáo nêu (+1,2% đến +16%)",
    "data_provenance": "pass (có lưu ý) — số FY2025 truy được về BCTC EY gốc (đã tự khớp); số Q3/6T chỉ truy về notes_read.md đọc ảnh, PDF gốc thiếu, có đối chiếu BQ và báo chí; LC 9.229 và phải thu khác 18.501 chỉ có một nguồn",
    "liquidity_capacity_realism": "na — đề xuất 0% discretionary; không có claim sizing cần kiểm",
    "confirmation_bias_flipflop": "pass (bất đối xứng) — tâm r2 13.018 → r3 14.621 do sửa lỗi quy ước ROE thật mà skeptic r1 nêu, có đối chứng 12.989; nhưng phần sửa theo chiều giảm (chất lượng dồn tích) chỉ được −1%, không chạm tới nền ROE",
    "exit_discipline_gap": "na — không có claim vào lệnh; mục 6 vẫn liệt kê mốc kiểm hai chiều",
    "missing_items": "fail — (1) lãi phải thu từ đầu tư chứng khoán 1.208→2.180 tỷ (+972) không có trong haircut và không giải thích; (2) phần lãi dự thu tín dụng vượt chuẩn ~3.000 tỷ trước thuế năm 2025 nằm sẵn trong ROE nền 15,3%/14,4%: ở tổn thất kỳ vọng 17,5% của chính báo cáo, ROE giảm ~1pp ⇒ tâm ≈ −11% (ước lượng); (3) cơ sở số CP trước/sau quyền mua không ghi nhãn: tương đương sau quyền ≈ 13.713 (−6,5%), ngày chốt quyền chưa xác định; (4) ESOP 2026 chưa kiểm; đạt: CAR/NPL/nhóm 2/bao phủ/LDR/CASA, kiểm toán FY2025 EY chấp nhận toàn phần, quỹ KTPL 25,8 tỷ, ΔVCSH 2025 = LNST"
  },
  "independent_verification": "Đối chiếu bctn_2025.txt: lãi thực thu 16.497.163 / 18.910.323 (LCTT), lãi ghi nhận 21.601.251 / 18.681.257, lãi phải thu tín dụng 6.802.719 / 3.272.745, lãi phải thu CK 2.179.948 / 1.208.103, quỹ KTPL 25.808 — tất cả KHỚP với báo cáo. Tính lại quy đổi ROE (14%→15,05%, 12,5%→13,33%) KHỚP. Đọc model_r3.py: BV + 9.360 rồi trừ PV tiền nộp, chia 3.744 tr CP ⇒ giá trị trên CP còn quyền mua, tương đương sau quyền ≈ (14.674×3.744 + 9.237)/4.680 ≈ 13.713.",
  "killer_objection": "Báo cáo thừa nhận năm 2025 chỉ thu tiền được 76% lãi ghi nhận và có ~3.800 tỷ lãi dự thu vượt chuẩn, nhưng vẫn neo ROE dự báo vào lợi nhuận 2025–26 chưa loại phần dồn tích đó và chỉ xoá một lần trên số dư (−1%). Áp chính mức tổn thất kỳ vọng 17,5% của báo cáo lên dòng thu nhập thì ROE nền giảm ~1pp, tâm giảm ~11% (ước lượng). Phần lãi phải thu chứng khoán +972 tỷ thì hoàn toàn không được xem xét.",
  "recommended_followups": [
    "Điều chỉnh ROE 2025 và 2026E theo phần dồn tích vượt chuẩn (hoặc ghi rõ vì sao không cần), chạy lại lưới với ROE CƠ SỞ sạch",
    "Giải thích lãi phải thu từ đầu tư chứng khoán 2.180 tỷ (TM: TPCP / TPDN / CCTG), đưa vào trục haircut nếu bất thường",
    "Ghi nhãn tâm là giá trị trên CP còn quyền mua, công bố kèm giá trị tương đương sau quyền (≈13.700) và ngày chốt quyền",
    "Tải lại PDF Q3/6T/2026 gốc để chuyển LC 9.229 và phải thu khác 18.501 khỏi trạng thái một nguồn",
    "Giải trình Ke 13,5% nằm ngoài dải 12,3–13,4%, hoặc hạ về dải"
  ],
  "summary": "r3 sửa đúng lỗi ROE bình quân nhân trên VCSH đầu kỳ, và các số FY2025 đều khớp BCTC EY gốc. Tuy nhiên báo cáo dùng lợi nhuận 2025–26 có thu tiền thấp (76%) làm nền ROE, chỉ haircut một lần trên số dư lãi dự thu tín dụng và bỏ qua lãi phải thu chứng khoán tăng gấp ~1,8 lần. Nhất quán với chính giả định tổn thất của báo cáo, ROE nền thấp hơn ~1pp, kéo tâm xuống ~11% (ước lượng, trên ngưỡng 5%). Cơ sở số cổ phiếu trước/sau quyền mua không được ghi nhãn (≈ −6,5% sau quyền). Chiều ngược lại: Ke 13,5% nằm ngoài dải nội địa do chính báo cáo nêu, và tỷ lệ thu tiền 9T26 đã hồi lên 91%, hai yếu tố này bù một phần. Kết luận: REFUTED mức trung bình, cần chạy lại với ROE nền đã làm sạch."
}
<<<END_VERDICT>>>