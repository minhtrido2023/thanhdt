**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phần tính toán của r5 tái lập được, và khoản sửa lớn nhất (quỹ khen thưởng phúc lợi 9,55%) đã khớp với BCTC kiểm toán. Còn một hạng mục chưa có trong báo cáo, có thể đẩy tâm lên khoảng 7% (ước lượng). Theo luật attack 8, mục thiếu đáng kể mà chưa định lượng được thì verdict là INCONCLUSIVE.

**Đã tự kiểm lại:**
- **Quỹ khen thưởng phúc lợi:** đọc thẳng ảnh trang TM33 kiểm toán FY2025 (`fy2025_kt_p38.jpg`). Năm 2025 trích 20,9 tỷ trên LNST 208,948 tỷ, tức 10,00%. Năm 2024 trích 21,6896 tỷ trên 238,636 tỷ, tức 9,09% (đã trình bày lại theo NQ ĐHĐCĐ 02/2025). Không có cổ phiếu tiềm năng gây suy giảm. Khớp báo cáo.
- **Tâm:** tự viết công thức riêng, không gọi `model_r5.py`. Ở tham số trung tâm ra **10.668** trước chiết khấu thanh khoản, khớp báo cáo đến từng đồng. NPV khoản vay +79,7 tỷ và tiền ròng 484,69 tỷ cũng khớp. Mỗi +1pp trích quỹ làm tâm giảm 136 đ/cp (báo cáo ghi −134).
- **Lỗi lệch năm kiểm toán (kiểu TV1):** không có. FY2025 kiểm toán chấp nhận toàn phần, có đủ trong `src/`.

**Hướng làm tâm quá THẤP:**
- **Thu nhập lãi tính không cùng cơ sở (mục thiếu, chưa định lượng được).** Báo cáo trừ khỏi E (bình quân LN 2019–2025) toàn bộ thu nhập lãi theo nhịp hiện tại, 32,65 tỷ/năm sau thuế. Nhưng E lịch sử chỉ chứa thu nhập lãi lịch sử, và số này thấp hơn:
  - LCTT kiểm toán, mã 05 "lãi từ hoạt động đầu tư": 2024 là 28,9 tỷ, 2025 là 37,4 tỷ trước thuế.
  - BQ `Cash_P0` cuối năm 2019–2023 chỉ 107–260 tỷ. Tiền gửi các năm đó chưa đo, vì `Cash_P0` lúc 25Q4 chỉ 91,7 tỷ nên có vẻ không gồm tiền gửi.
  - Nếu lãi bình quân lịch sử khoảng 20 tỷ sau thuế (ước lượng), lợi nhuận lõi đang bị tính thiếu khoảng 12 tỷ/năm, tức khoảng **+7%** tâm (ước lượng).
- Ba khoản bồi thường BH1, φ chưa có số capex theo dây chuyền, và khoản trả trước G2 vẫn để ở độ nhạy. Báo cáo ghi nhận đủ, không thiên vị một chiều.

**Hướng làm tâm quá CAO:** chi phí hoàn nguyên môi trường (−8,5% mỗi 100 tỷ), gián đoạn sản xuất 2026–31 (−3,1%, chỉ ở độ nhạy), kịch bản TỐT mâu thuẫn với việc TB2 dừng, và giá điện. Tất cả đã gắn WARNING hoặc độ nhạy; không cái nào đo được trước BCTC Q4/26.

**Chỗ nhỏ:**
- LN 2024 lấy từ BQ là 240,78 tỷ, BCTC kiểm toán là 238,64 tỷ. Ảnh hưởng tâm không đáng kể.
- Câu "NQ HĐQT 2026 ảnh hưởng < 1%" không có nguồn.

**Lật kết luận giữa các vòng:** không thấy. Cả ba thay đổi r4→r5 đều có nguồn: quỹ phúc lợi từ kiểm toán (tôi đã kiểm), chu kỳ tái đầu tư từ TM11, APV là sửa phương pháp. Tôi không mở `kb/dd_price_zones.json` theo ràng buộc mù. Báo cáo có chứa giá thị trường, tôi đã bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "CSV (Hoá chất Cơ bản Miền Nam) — DD r5 23/11/2026, tâm 10.447 đ/cp sau CK 5 tỷ",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — §9 nói rõ việc cưỡng chế BH1/dừng TB2 là đề án chuyển đổi KCN (QĐ 2408, QĐ 1122), không phải xử phạt; cờ quản trị 'không chấp hành tháo dỡ' đã được ghi; HARD ABANDON có điều kiện 'kiểm toán ngoại trừ BCTC 2026'. Không thấy dấu hiệu chuyển sang pháp nhân/tài sản lõi trong tài liệu đã đọc",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; mô hình APV/perpetuity tái lập độc lập ra 10.668 trước CK (khớp); r_commit 8% < Ke là lựa chọn thận trọng (r_commit = Ke cho +15,2%); trục N 20/30/40 là ước lượng nhưng có cơ sở TM11 (92,3% nguyên giá hết khấu hao vẫn dùng) và độ nhạy N = 12 được công bố",
    "data_provenance": "pass — TM33 kiểm toán FY2025 (ảnh p38) đọc trực tiếp: 20,9/208,948 = 10,00%, 21,6896/238,636 = 9,09%, 110.499.910 cp, không có CP tiềm năng suy giảm; LCTT p10: khấu hao 33,90/44,60, capex 59,26/22,44 khớp. Chỗ nhỏ: LN 2024 trong E = 240,78 (BQ) so với 238,64 kiểm toán (ảnh hưởng tâm không đáng kể); câu 'NQ HĐQT 2026 < 1%' không có nguồn",
    "liquidity_capacity_realism": "na — sizing 0% NAV; CK thanh khoản thuộc postlock, không đánh giá vì ràng buộc mù giá",
    "confirmation_bias_flipflop": "pass — r2 20.717 → r3 11.041 → r4 11.224 → r5 10.447; cả ba thay đổi r5 có nguồn (T1 từ BCTC kiểm toán, đã kiểm; H1 từ TM11; H6 sửa phương pháp theo đúng khuyến nghị skeptic r3); khoá lại sau khi đã thấy giá nhưng mọi thay đổi đều kéo tâm XA giá chứ không về phía giá. Không mở dd_price_zones.json theo ràng buộc của brief",
    "exit_discipline_gap": "na — DD_GENERAL; dù vậy §8 có mốc đổi nhận định hai chiều và HARD ABANDON",
    "missing_items": "fail (chưa định lượng được) — (1) thu nhập lãi tính không cùng cơ sở: E bình quân 2019–2025 chỉ chứa thu nhập lãi lịch sử nhưng bị trừ thu nhập lãi theo nhịp hiện tại 32,65 tỷ sau thuế; LCTT mã 05: 2024 là 28,9, 2025 là 37,4 tỷ trước thuế; BQ Cash_P0 2019–23 chỉ 107–260 tỷ ⇒ lợi nhuận lõi có thể bị tính thiếu ~12 tỷ/năm, tâm ~+7% (ước lượng, cần doanh thu tài chính 2019–2023). (2) Chi phí hoàn nguyên BH1 (−8,5%/100 tỷ) và bồi thường (+8,5%/100 tỷ) vẫn chưa có số. Đã soát và đạt: capex cam kết Nhơn Trạch đã vào base; số cổ phiếu có ngày + nguồn và không có suy giảm; quỹ phúc lợi đã sửa; ý kiến kiểm toán FY2025 chấp nhận toàn phần; trích quỹ KH&CN 15 tỷ (mã 07) đã nằm trong E và trong tiền ròng; phần đất Nhơn Trạch là tiền thuê trả một lần đã tính vào phần đã chi. Bên liên quan (Vinachem) và khoản trả trước G2 242 tỷ chưa được thuyết minh"
  },
  "independent_verification": "(a) Đọc ảnh TM33 kiểm toán FY2025: tỷ lệ trích quỹ phúc lợi 10,00%/9,09% và số CP 110.499.910 — khớp. (b) Tự viết công thức tính tâm (không import model_r5.py): 10.668 đ/cp tại φ 0,65, t 1,75, N 30, CƠ SỞ — khớp từng đồng; NPV khoản vay 79,7 tỷ, tiền ròng 484,69 tỷ khớp; mỗi +1pp trích quỹ ra −136 đ/cp (báo cáo −134). (c) LCTT kiểm toán p10: khấu hao, capex, lãi từ hoạt động đầu tư 37,4/28,9 tỷ.",
  "killer_objection": "Thu nhập lãi tính không cùng cơ sở: E là lợi nhuận bình quân 2019–2025, khi số dư tiền gửi và thu nhập lãi thấp hơn hiện nay, nhưng mô hình trừ thu nhập lãi theo nhịp 2026 rồi lại cộng toàn bộ tiền ròng hiện tại. Lợi nhuận lõi vì vậy có thể bị tính thiếu ~12 tỷ/năm, khoảng +7% tâm (ước lượng); hướng này đi ngược mọi chỉnh sửa giảm của r5 và chưa vòng nào kiểm.",
  "recommended_followups": [
    "Lấy doanh thu tài chính / lãi tiền gửi 2019–2023 từ BCTC kiểm toán, tính lại E_core = bình quân(LN_t − lãi_t sau thuế) thay vì bình quân(LN) − lãi hiện tại",
    "Đối chiếu LN 2024 trong fin_csv_bq.csv (240,78) với kiểm toán (238,64)",
    "Ghi nguồn cho câu 'NQ HĐQT 2026 / NQ tổng vốn Nhơn Trạch ảnh hưởng < 1%' hoặc gỡ câu đó",
    "BCTC Q4/26: kiểm tra gián đoạn sau khi TB2 dừng, thuyết minh trả trước G2, chi phí hoàn nguyên nếu có"
  ],
  "summary": "Phần tính toán của r5 tái lập đúng và có nguồn: tôi tự tính lại ra tâm 10.668 trước CK, khớp đến từng đồng, và đọc trực tiếp TM33 kiểm toán xác nhận tỷ lệ trích quỹ phúc lợi 9,55% — khoản sửa lớn nhất (−954). APV và chu kỳ tái đầu tư đều có căn cứ và công bố độ nhạy hai chiều; không thấy dấu hiệu chỉnh tham số theo giá. Dù vậy có một mục thiếu chưa vòng nào kiểm: thu nhập lãi được trừ khỏi lợi nhuận bình quân lịch sử theo nhịp hiện tại cao hơn, nên tâm có thể bị đánh giá THẤP khoảng 7% (ước lượng). Cộng thêm chi phí hoàn nguyên và bồi thường hai chiều vẫn chưa có số, kết luận là INCONCLUSIVE chứ không phải CONFIRMED."
}
<<<END_VERDICT>>>