**Phán quyết: INCONCLUSIVE (độ tin cậy trung bình).** Rev 4 tái lập đúng từng số và khai báo minh bạch. Hai điểm chịu lực vẫn không kiểm chứng được:
- **Cơ chế giá của Ngòi Hút 2.** Nhà máy 48 MW, chiếm khoảng 59% công suất thuỷ điện, nằm ngoài biểu giá chi phí tránh được. Báo cáo vẫn áp chỉ số 1%/năm cho nó, và chính báo cáo ghi đây là giả định. Nếu NH2 phẳng danh nghĩa, tâm giảm khoảng 550 đ, tức khoảng −6,2%.
- **Cam kết vốn chủ cho Phước Hoà (1.200 MW).** Chưa công bố, không định lượng được, nhưng có thể rất lớn.

Theo luật attack 8, khoản trọng yếu mà không định lượng được thì kết luận là INCONCLUSIVE, không phải REFUTED.

**Đã tự kiểm lại:**
- **Tái lập mô hình:** chạy lại `model/dcf_tta_r4.py` ra đúng 16.201 / 12.006 / 8.058 / 2.201, tâm 8.802 trước và 8.548 sau thanh khoản. md5 của script và `out_r4.json` khớp với báo cáo.
- **Tỷ giá (K3):** từ `data/macro_usdvnd.csv`, CAGR 2016→2025 là 1,86%, khớp với 1,8% dùng trong mô hình.
- **Chuỗi doanh thu thuỷ điện (K2):** truy vấn BQ `ticker_financial` khớp tổng 4 quý cho 2021/22/23 (661,35 / 808,70 / 655,48). Nhưng đây là **tổng doanh thu**, không phải doanh thu riêng mảng điện. Năm 2024, tổng doanh thu BQ là 734,1, còn doanh thu điện theo KT25 là 720,4, chênh 13,7. Vậy thuỷ điện 2021–23 bị thổi lên khoảng 14 tỷ/năm. Trung bình cắt còn khoảng 367,7 thay vì 372,3, tâm giảm ước lượng khoảng 150 đ (−1,7%).
- **Số liệu trong PDF:** không đọc được trang nào vì máy thiếu `poppler`/`fitz`. Các số trên BCTC chỉ dựa vào việc skeptic r1 đã đối chiếu trước đó.

**Hai chiều:**
- **Tâm có thể quá CAO:**
  - Chỉ số 1%/năm đo từ 2019. Khung 2021→2026 thì gần như 0, và với g = 0% tâm là 7.865 (−10,6%).
  - NH2 có thể phẳng danh nghĩa (−550 đ).
  - Thuỷ điện 2021–23 bị thổi lên như trên (khoảng −150 đ).
  - EPTC chỉ trả 49% hoá đơn mặt trời trong 9T/2026, giảm từ 55% cùng kỳ, nhưng mô hình coi như thu đủ tiền từ 2027. Đây là thiên lệch nhỏ về giá trị thời gian, chưa đo.
- **Tâm có thể quá THẤP:**
  - Phần VAT trên khoản hồi tố không vào base. Tính theo trọng số khoảng +48 tỷ, ước lượng +267 đ.
  - 9T/2026 thuỷ điện 279,8 so với 262,3 cùng kỳ, tức năm 2026 có thể đạt khoảng 397 (ước lượng), cao hơn nền 373.
  - Tỷ giá 2021–2025 tăng 3,2%/năm, cao hơn mức 1,8% đang dùng.
  - Dòng tiền Q4/2026 bị bỏ.
- Cộng lại, hai chiều gần cân nhau. Tâm hợp lý quanh 8.800 ± khoảng 7%.

**Làm tiếp nên ưu tiên:**
1. Tìm hợp đồng mua bán điện hoặc cơ chế giá của Ngòi Hút 2.
2. Thay doanh thu 2021–23 bằng doanh thu mảng điện lấy từ BCTC kiểm toán từng năm.
3. Theo dõi công bố tổng mức đầu tư và tỷ lệ góp vốn Phước Hoà.

Tôi tuân thủ ràng buộc mù giá: không tra giá thị trường và không mở `kb/dd_price_zones.json`. Vì vậy attack 6 chỉ so với REPORT r1–r3. Các so sánh giá trong §0 và §7 của báo cáo bị bỏ qua khi chấm.

<<<VERDICT_JSON>>>
{
  "case_topic": "TTA — DD rev 4 (REPORT_r4.md, 23/11/2026)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra claim fear-buy hay §2.5",
    "scandal_migration_risk": "pass — rủi ro pháp lý ở cấp pháp nhân/tài sản (kết luận TTCP về FIT, giấy phép Thuỷ lợi Bầu Ngứ, tiền gửi BIDV 70 tỷ cầm cố) được mô hình hoá qua kịch bản B/B′/C, độ nhạy Bầu Ngứ dừng 2027 (−826) và HARD ABANDON #6",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; DCF dòng tiền hữu hạn tới 2060; đối chiếu chéo V_ngắn 6.632 vs V_dài 8.802, D = 0,283 < ln2; K1 chọn 1% (thấp hơn mức 2% skeptic r1 đề xuất); trọng số giữ nguyên từ r3",
    "data_provenance": "pass, có caveat — tỷ giá và BQ khớp; nhưng thuỷ điện 2021–23 dùng TỔNG doanh thu BQ, không phải doanh thu riêng mảng điện (2024: 734,1 vs 720,4), làm nền 373 cao thêm khoảng 4–5 tỷ (khoảng −150 đ/cp, ước lượng). Giá sau FIT 1.100, cắt −15% sau 2036 và lộ trình thuế đều đã gắn nhãn ước lượng. Không đọc lại được PDF vì thiếu poppler",
    "liquidity_capacity_realism": "na — không có claim sizing mua; chiết khấu thanh khoản tính sau khi khoá mô hình (2,89%/3,87%)",
    "confirmation_bias_flipflop": "pass — +38,8% so với r3 đến từ bằng chứng mới thật (3 quyết định biểu giá chi phí tránh được, doanh thu bộ phận KT25 tr.45, tệp tỷ giá); có bảng phân rã từng bước; trọng số không re-tune. Theo ràng buộc của nhiệm vụ, chỉ so với REPORT r1–r3, không mở dd_price_zones",
    "exit_discipline_gap": "na — không đề xuất mua; vẫn có HARD ABANDON #1–#7 và điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (không định lượng được) — (1) cơ chế giá/PPA Ngòi Hút 2 (48/82 MW thuỷ điện) chưa kiểm, mô hình áp chỉ số 1% không có bằng chứng, nếu phẳng thì khoảng −550 đ (−6,2%); (2) cam kết vốn chủ cho Phước Hoà 1.200 MW chưa công bố, có thể rất lớn so với VCSH, tính NPV0 tại giá sổ 90,7 kèm HARD ABANDON #7; (3) thời hạn HTKD và giấy phép nước/đất thuỷ điện chưa có (dừng 2050 thì −565). Đạt: cơ sở số cổ phiếu 178,559 tr. tại 30/9/2026 (NQ ĐHĐCĐ: không phát hành/ESOP), quỹ khen thưởng phúc lợi đã trừ, BCTC kiểm toán FY2025 chấp nhận toàn phần + soát xét H1/26, bên liên quan (cho vay 15 tỷ, HTKD), không có khoản một-lần, lộ trình ưu đãi thuế khớp nhà máy COD 2019/2020"
  },
  "independent_verification": "Chạy lại dcf_tta_r4.py: các tâm A/B/B′/C và tâm 8.802/8.548 khớp, md5 khớp. CAGR tỷ giá trung bình năm 2016→2025 = 1,86% từ macro_usdvnd.csv (khớp 1,8%). BQ ticker_financial: tổng 4 quý 2021/22/23 = 661,35/808,70/655,48 (khớp), nhưng là tổng doanh thu, không phải doanh thu điện (năm 2024 tổng 734,1 vs mảng điện 720,4) ⇒ chuỗi thuỷ điện 2021–23 hơi cao",
  "killer_objection": "Chỉ số 1%/năm cho thuỷ điện được đo từ 2019, trong khi 2021→2026 biểu giá gần như đứng yên; và nó còn được áp cho Ngòi Hút 2 (khoảng 59% công suất), nhà máy nằm ngoài biểu giá và không có bằng chứng nào. g = 0% cho tâm 7.865 (−10,6%); riêng NH2 phẳng là khoảng −6%.",
  "recommended_followups": [
    "Tìm hợp đồng mua bán điện hoặc cơ chế giá của Ngòi Hút 2 (thị trường điện cạnh tranh hay hợp đồng song phương, có điều khoản chỉ số hoá không)",
    "Thay doanh thu thuỷ điện 2021–23 bằng doanh thu mảng điện / bộ phận Yên Bái lấy từ BCTC kiểm toán từng năm, thay vì tổng doanh thu BQ",
    "Báo cáo kèm tâm với chỉ số thuỷ điện 0% đo trên khung 2021→2026 cạnh base 1%",
    "Theo dõi công bố tổng mức đầu tư / tỷ lệ góp vốn Phước Hoà và giấy phép Thuỷ lợi Bầu Ngứ",
    "Cài poppler để đọc lại trực tiếp KT25 tr.45 và Q3/26 tr.18"
  ],
  "summary": "Rev 4 tái lập chính xác và sửa đúng các thiên lệch QUÁ THẤP mà skeptic r1 chỉ ra, bằng bằng chứng mới thật (biểu giá chi phí tránh được, doanh thu bộ phận, chuỗi tỷ giá đo được), không re-tune trọng số. Hai chiều gần cân nhau: chiều đắt gồm chỉ số 1% dựa vào khung từ 2019, NH2 không có bằng chứng giá, thuỷ điện 2021–23 hơi cao vì dùng tổng doanh thu, và EPTC đang trả ít hơn; chiều rẻ gồm VAT trên hồi tố bị loại, nhịp thuỷ điện 2026 khoảng 397 > 373, tỷ giá gần đây tăng nhanh hơn. Tâm khoảng 8.800 ± 7% là hợp lý. Nhưng giá NH2 và cam kết vốn Phước Hoà là hạng mục trọng yếu không định lượng được, nên chưa CONFIRMED."
}
<<<END_VERDICT>>>