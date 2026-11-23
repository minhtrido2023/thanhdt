Phán quyết: **INCONCLUSIVE, độ tin cậy trung bình**. Phần số học của rev3 tái lập đúng. Lệch hai chiều gần như triệt tiêu nhau. Chỗ yếu còn lại là hai nguồn gốc chưa có trong tay.

**Đã kiểm độc lập**
- md5 của mô hình và file giả định khớp với báo cáo. Chạy lại `dcf_vlb_r3.py` ra kết quả giống hệt `output_r3.txt`.
- Tôi tự cộng lại net cash từ số BS 30/9 trong `notes_raw.md` và ra đúng **488,84 tỷ**.
- Truy vấn BQ `ticker_financial.CF_Invest_5Y` cho VLB: capex 5 năm là 42–65 tỷ, tức khoảng 8–13 tỷ/năm, ngang khấu hao khoảng 10,7 tỷ/năm. Vì vậy giả định "FCFE ≈ LN" đứng được. Mối lo "đội thiết bị đã khấu hao 93% thì sắp phải chi lớn" chưa có bằng chứng.
- Báo cáo §8 có ghi giá thị trường; tôi bỏ qua khi chấm mô hình.

**Lực đẩy tâm lên quá CAO**
- **LN gốc 310 tỷ** tăng 2%/năm suốt 11–13 năm. Mức này cao hơn mọi năm lõi đã kiểm toán: lõi FY25 là 264,8; LNST 2017–2024 chỉ 130–218 theo BQ. Chỉ quý TTM (357) cao hơn, và quý đó nằm ở đỉnh chu kỳ hạ tầng Đồng Nai; chính BVSC cảnh báo cầu Tân Cang giảm sau Long Thành GĐ1.
  - Nếu dùng 265 thì cơ sở giảm 10,3%. Đây là phản bác mạnh nhất, nhưng là phán đoán, không phải lỗi dữ kiện. Kịch bản xấu 250 với trọng số 0,25 đỡ được một phần.
- **Kịch bản xấu chỉ đặt khoản bù trừ = 0.** Nó không mô hình lại trường hợp truy thu như năm 2022 (>270 tỷ, khoảng −5.780 đ/cp). Báo cáo chỉ gắn trường hợp này với HARD ABANDON.
- Lỗi nhỏ: tiền khách ứng trước chỉ trừ phần giá vốn (51,5) chứ không trừ toàn bộ 76,9. Lệch khoảng +540 đ/cp (~1,2%).
- Giả định thu hồi 22,66 tỷ ký quỹ vượt dự phòng có thể sai chiều. Ký quỹ thường bằng tổng chi phí hoàn nguyên đã duyệt. Ảnh hưởng dưới 0,3%.

**Lực đẩy tâm xuống quá THẤP**
- Vốn lưu động và tiền ứng trước được trừ ngay tại 30/9, thay vì trừ khi đóng mỏ dù vẫn quay vòng. Như vậy tâm bị kéo xuống khoảng **1.930 đ/cp (~4%)**.
- Cơ sở cho giá trị bằng 0 với ~13,8 triệu m³ còn lại ở Thạnh Phú 1 và ~2,3 năm trữ lượng ở Tân Cang 1 sau 1/2038. Báo cáo lại dùng chính việc Soklu được gia hạn làm bằng chứng rằng gia hạn có xảy ra. Gia hạn cả 3 mỏ chính: +8,7%.
- Phần bù trừ còn dư 97,6 tỷ bị tính bằng 0: tối đa +802 đ/cp.

**Hạng mục còn thiếu (attack 8)**
Không có hạng mục nào định lượng được mà vượt 5% tâm. Còn ba hạng mục trọng yếu nhưng chưa định lượng được, và chúng giữ phán quyết ở INCONCLUSIVE:
1. BCTC kiểm toán FY2025: chưa tải được, nên chưa biết ý kiến kiểm toán và thuyết minh về tiền cấp quyền.
2. Hạn giấy phép chỉ lấy từ bảng tổng hợp của BVSC: chưa có số hiệu hay bản gốc giấy phép, độ nhạy khoảng ±4% cho mỗi năm.
3. Nghị quyết HĐQT về đầu tư/đền bù: chưa đọc.

**Lật nhận định (flip-flop):** Tâm trước chiết khấu đi từ 52.732 (r2) xuống 46.689 (r3). Lần giảm này có cơ sở mới thật: bảng giấy phép BVSC tr.7 và định nghĩa LN lõi khớp với số kiểm toán, không phải đọc lại cùng dữ kiện. Tôi chỉ so trong thư mục DD, không mở sổ vùng giá theo đúng ràng buộc mù.

<<<VERDICT_JSON>>>
{
  "case_topic": "VLB — DD rev3 23/11/2026 (REPORT_rev3.md), tâm 46.689 trước CK / 42.800 ex-div sau CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không đưa ra claim fear-buy/§2.5 (nói rõ không đủ điều kiện vào sleeve)",
    "scandal_migration_risk": "pass — các WARNING (tiền cấp quyền đảo chiều 2022↔2026, rà soát GP Soklu, Kiểm toán NN về đất) được nêu ở §10. Soklu5 gia hạn theo QĐ 473 [FP p6]. Không có tín hiệu lan sang TC1/TP1/TT2 trong tài liệu được trích. Lưu ý: kịch bản xấu không mô hình truy thu kiểu 2022 (>270 tỷ ≈ −5.780 đ/cp), chỉ gắn HARD ABANDON",
    "optimistic_comp_sotp_bias": "pass — không dùng comp. Mô hình hữu hạn theo từng mỏ, không terminal. V6 Gordon chỉ để hiển thị. Lệch hai chiều gần triệt tiêu: lên (trừ ứng trước chỉ phần giá vốn +544 đ/cp; giả định thu hồi ký quỹ +118) vs xuống (VLĐ trừ ngay thay vì lúc đóng mỏ ≈ −1.930 đ/cp; dư bù trừ = 0 ≈ −802; trữ lượng TP1/TC1 sau 2038 = 0 ngoài kịch bản tốt, tới +8,7%)",
    "data_provenance": "fail (mềm) — net cash, LN 9T, khoản bù trừ, ký quỹ, quỹ phúc lợi đều truy được về BCTC Q3/H1 (đã soát xét) và NQ ĐHĐCĐ. Nhưng hạn GP/trữ lượng — yếu tố mang phần lớn giá trị — chỉ có từ bảng tổng hợp của BVSC (bán-sơ cấp, không số GP). DTTC/thu nhập khác FY25 (31/15) lấy từ BVSC, không từ BCTC kiểm toán. op 9T/25 là ước lượng",
    "liquidity_capacity_realism": "na — không đề xuất sizing. Báo cáo tự nêu ADV250 1,14 tỷ, thoát 5 tỷ mất ~22 phiên",
    "confirmation_bias_flipflop": "pass — trước CK đi 52.732 (r2) → 46.689 (r3), giảm theo nguồn mới (bảng GP BVSC 2/2026 tr.7; LN lõi FY25 tính lại từ LNTT kiểm toán 376,993). Báo cáo tự khai đã biết giá từ r2 (mù theo quy trình). Chỉ so trong thư mục DD; không mở dd_price_zones theo ràng buộc của brief",
    "exit_discipline_gap": "na — không có claim vào lệnh. Mốc M1–M4 và điều kiện đổi nhận định hai chiều đã khoá trước ở §9",
    "missing_items": "fail (không định lượng được) — (1) BCTC kiểm toán FY2025 vắng (ý kiến kiểm toán + thuyết minh tiền cấp quyền); soát xét H1/26 chấp nhận toàn phần làm giảm, không loại rủi ro. (2) Bản gốc/số hiệu GP vắng (±4% mỗi năm hạn TC1+TP1). (3) NQ HĐQT về đầu tư/đền bù chưa đọc. Đạt: số CP 46,72056tr [Q3 p22, CP quỹ đã loại, không ESOP], quỹ KTPL/thưởng 14,84%, bên liên quan = 0, một lần 343,93 đã loại, thuế 20%, capex tuân thủ (hoàn nguyên) có tính, capex duy trì (BQ CF_Invest_5Y 42–65 tỷ ≈ khấu hao). Không có hạng mục định lượng được nào >5% tâm"
  },
  "independent_verification": "(a) md5 mô hình/giả định khớp; chạy lại dcf_vlb_r3.py ra giống hệt output_r3.txt (tâm trước CK 46.689). (b) Tự cộng net cash từ số BS Q3: 27,576+785,008−107,466−61,748−51,54−67,06−35,93 = 488,84 tỷ, khớp. (c) BQ ticker_financial VLB: CF_Invest_5Y 42–65 tỷ (≈8–13 tỷ/năm) ≈ khấu hao ~10,7/năm ⇒ FCFE≈LN hợp lý, không thiếu capex duy trì. (d) LNST năm theo BQ (2017–2024: 130–218; 2025: 301,4) cho thấy LN gốc 310 cao hơn mọi năm lõi đã kiểm toán",
  "killer_objection": "LN gốc 310 tỷ tăng 2%/năm suốt 11–13 năm cao hơn mọi năm lõi đã kiểm toán (lõi FY25 264,8; 2017–2024 ≤218) và dựa vào TTM ở đỉnh chu kỳ hạ tầng Đồng Nai, nơi chính BVSC báo cầu Tân Cang giảm sau Long Thành GĐ1. Dùng 265 ⇒ cơ sở −10,3%. Ngược lại, cho trữ lượng TP1/TC1 sau 2038 giá trị bằng 0 (trừ kịch bản tốt 25%) dù có tiền lệ Soklu được gia hạn ⇒ lên tới +8,7%. Kiểm toán FY2025 chưa đọc được nên chưa thể chốt",
  "recommended_followups": [
    "Lấy BCTC kiểm toán FY2025 (HNX/UPCoM CBTT, SSC IDS) để đọc ý kiến kiểm toán và thuyết minh tiền cấp quyền/giấy phép",
    "Đối chiếu bảng GP BVSC tr.7 với giấy phép gốc (số GP, ngày cấp, cote) qua CBTT công ty hoặc Sở NN&MT/Sở XD Đồng Nai",
    "Thêm kịch bản xấu có truy thu kiểu 2022 (khoảng −270 tỷ) thay vì chỉ đặt khoản bù trừ = 0, hoặc ghi rõ đây là ngoài mô hình",
    "Thống nhất quy ước vốn lưu động/khách ứng trước: hoặc trừ đủ 76,9 tỷ ứng trước, hoặc trừ VLĐ theo PV lúc đóng mỏ (chênh khoảng ±4%)",
    "Báo kèm độ nhạy trọng số gia hạn GP (25% → 50%), vì báo cáo tự dẫn tiền lệ Soklu được gia hạn",
    "Đọc các NQ HĐQT 12 tháng gần nhất để tìm cam kết đầu tư/đền bù"
  ],
  "summary": "Rev3 của VLB đúng về số học: mô hình và net cash 488,84 tỷ tái lập chính xác, và giả định capex duy trì ≈ khấu hao được BQ xác nhận. Lần giảm tâm từ r2 có nguồn mới thật (bảng giấy phép BVSC, LN lõi khớp số kiểm toán), không phải đọc lại cùng dữ kiện. Xét hai chiều: phía đắt, LN gốc 310 cao hơn mọi năm lõi đã kiểm toán và dựa vào TTM ở đỉnh chu kỳ hạ tầng (265 thì −10%), còn kịch bản xấu không mô hình truy thu kiểu 2022. Phía rẻ, vốn lưu động bị trừ ngay (−4%), trữ lượng sau 2038 và phần bù trừ còn dư tính bằng 0. Các lệch này gần triệt tiêu và không hạng mục định lượng được nào vượt 5% tâm. Phán quyết vẫn là INCONCLUSIVE vì ba thứ chưa có trong tay: BCTC kiểm toán FY2025, bản gốc giấy phép (yếu tố mang phần lớn giá trị, hiện chỉ từ bảng tổng hợp của BVSC) và NQ HĐQT về đầu tư. Giá thị trường trong §8 của báo cáo đã được bỏ qua khi chấm mô hình."
}
<<<END_VERDICT>>>