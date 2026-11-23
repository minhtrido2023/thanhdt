Đang chốt verdict: số base đã tái lập khớp; còn một lỗ hổng về chu kỳ tái đầu tư cần báo.

## Phản biện DD_GENERAL: CSV r4 → **INCONCLUSIVE** (độ tin trung bình)

Báo cáo có ghi giá thị trường (20.300) và P/E, P/B ở §1, §6, §7. Tôi bỏ qua toàn bộ, chỉ đánh giá mô hình và dữ kiện.

**Tự kiểm chứng (khớp).** Tôi tự tính lại công thức base r4 (`/tmp/sk_csv.py`, không dùng `model_r4.py`):
- CƠ SỞ 11.363, XẤU 7.744, TỐT 15.254. Báo cáo ghi 11.361 / 7.744 / 15.254, chênh 2 đ do làm tròn.
- Phần thay thế còn chi −855,5 tỷ, lá chắn thuế +92,6 tỷ, đều khớp §4.
- Capex lịch sử lấy từ BQ `ticker_financial` (CF_Invest_P0) 2017–2025 là −20 / −97 / −35 / −47 / −58 / −22 / −18 / −26 / −59 tỷ, trung bình khoảng 42 tỷ/năm. 9T/2026 là −265,7, khớp §3.

**Chiều ĐẮT (tâm có thể quá CAO)**
1. **Base không có chu kỳ tái đầu tư cho nhà máy mới. Đây là phản bác mạnh nhất.** Mô hình coi Nhơn Trạch là khoản chi một lần, nhà máy dùng mãi mãi. Bản "lặp lại mỗi 30 năm" chỉ nằm ở độ nhạy. Báo cáo lại tự dùng đời khấu hao 12 năm (máy 4–10 năm) để tính lá chắn thuế. Như vậy lợi ích thuế được tính theo đời ngắn, còn chi phí thay lại theo đời 30 năm hoặc không có.
   - Tôi tính lại tâm CƠ SỞ khi phần thay thế lặp lại mỗi N năm:

     | N | Tâm | Δ |
     |---|---|---|
     | 30 | 11.183 | −1,6% |
     | 20 | 10.685 | −6,0% |
     | 15 | 9.981 | −12,2% |
     | 12 | 9.164 | −19,3% |

   - Có một yếu tố giảm nhẹ: E lịch sử đã gánh khoảng 42 tỷ/năm capex duy trì, tương đương 3,7% nguyên giá 1.145 tỷ. Nhưng chưa đối chiếu được với khấu hao trong P&L, nên chưa biết phần này bù được bao nhiêu.
2. **Gián đoạn sản xuất không nằm trong base.** BH1 bị cưỡng chế đến 31/12/2026, TB2 dừng sau 15/08, nghiệm thu toàn bộ 12/2031. Kịch bản gián đoạn (−3,1%) chỉ ở độ nhạy.
3. **Kịch bản TỐT mâu thuẫn với việc TB2 đã dừng.** Rủi ro này được ghi nhận nhưng vẫn giữ trong base; bỏ đi thì tâm −8,5%.
4. **Chi phí hoàn nguyên môi trường** không có số, chỉ có độ nhạy (−7,9%).
5. **Biểu giá điện cho xút–clo** là chi phí đầu vào cốt lõi của ngành nhưng báo cáo không nhắc tới.

**Chiều RẺ (tâm có thể quá THẤP)**
1. Phần thay thế được tính hiệu suất bằng nhà máy cũ. Nhà máy mới có thể tiết kiệm điện năng và chi phí vận hành, nhưng không được ghi nhận gì.
2. Bồi thường BH1 để base = 0, dù QĐ 2408 có dẫn NĐ 88/2024 và VB 719 về "hồ sơ bồi thường". Độ nhạy +7,9%.
3. φ đo theo tấn; nếu đo theo capex có thể thấp hơn 0,65. Mỗi 0,1 φ đổi khoảng ±12% tâm.
4. Khoản trả trước 242 tỷ (G2) chưa phân loại. Nếu là của Nhơn Trạch thì +13,9%.

**Lỗi logic nhỏ.** Chiết khấu dòng chi thay thế ở kd làm giá trị tăng khi lãi vay tăng (độ nhạy kd 9,5% cho +1,1%). Chiều này sai về kinh tế, nhưng tác động chỉ khoảng ±1%.

**Kết luận.** Mô hình nhất quán, tái lập được, và nguồn số tốt. Nhưng hai hạng mục lớn hơn 5% chưa được định lượng chắc trong base: chu kỳ tái đầu tư và hoàn nguyên/gián đoạn. Ở chiều ngược lại, φ theo capex và bồi thường cũng lớn hơn 5%. Vì vậy chưa thể CONFIRMED.

<<<VERDICT_JSON>>>
{
  "case_topic": "CSV (Hoá chất Cơ bản Miền Nam) — DD r4 ứng viên LAG_LO, tâm 11.224 đ/cp",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — QĐ 2408 cưỡng chế BH1 và QĐ 1122 dừng TB2 là đề án chuyển đổi KCN, không phải xử phạt; hệ quả kinh tế (capex thay thế) đã nằm trong base qua D3. Cờ quản trị 'không chấp hành tháo dỡ' có ghi ở WARNING §9. Không có tín hiệu thu hồi giấy phép hay tài sản lõi ngoài phần đã mô hình hoá",
    "optimistic_comp_sotp_bias": "fail (vừa phải) — không dùng comp. Cấu phần SOTP-capex lệch hai chiều: base không có chu kỳ tái đầu tư nhà máy mới, trong khi lá chắn thuế lại dùng L = 12 năm (lợi ích theo đời ngắn, chi phí theo đời vô hạn); TỐT giữ dù TB2 đã dừng; gián đoạn để ngoài base. Ngược lại, hiệu suất của nhà máy mới không được ghi nhận và bồi thường = 0. Chiết khấu ở kd làm giá trị tăng khi kd tăng (+1,1% ở 9,5%), sai chiều nhưng nhỏ",
    "data_provenance": "pass — bảng cân đối 30/09 (mã 110/121/321/323/344/429/411) có ảnh BCTC; LN 2019–25 và capex khớp BQ (tôi tự query); tổng vốn 1.844 tỷ chỉ có nguồn báo chí, NQ HĐQT không có trong src/ (đã ghi là không kiểm chứng được); kiểm toán FY2025 chấp nhận toàn phần (tự đọc), soát xét 6T đúng năm, không lẫn năm. kd 8% có 1,6pp là ước lượng, đã gắn nhãn",
    "liquidity_capacity_realism": "na — sizing 0% NAV; báo cáo không claim vị thế nào cần khớp lệnh",
    "confirmation_bias_flipflop": "pass — tâm r2 20.717 → r3 11.041 → r4 11.224, mỗi lần đổi đều xuất phát từ phản biện có tài liệu (r1 REFUTED: đếm hai lần; r2 INCONCLUSIVE: F1 nâng, F2 hạ). Đã đổi theo cả hai chiều. Lưu ý r4 khoá lại sau khi đã thấy giá, nhưng hai tham số mới đều có nguồn BCTC và tác động ngược chiều nhau (+838 / −650). Không đọc kb/dd_price_zones.json do ràng buộc mù",
    "exit_discipline_gap": "na — báo cáo không đưa ra claim sizing hay mua; vẫn có mốc NÂNG/HẠ ở §8 và HARD ABANDON",
    "missing_items": "fail — (1) chu kỳ tái đầu tư nhà máy mới không có trong base: định lượng được −6% (N = 20) đến −19% (N = 12, nhất quán với L = 12 của chính báo cáo), giảm nhẹ một phần vì E lịch sử đã gánh khoảng 42 tỷ/năm capex (BQ) nhưng chưa đối chiếu khấu hao P&L; (2) gián đoạn sản xuất 2026–2031 không nằm trong base (độ nhạy −3%); (3) hoàn nguyên môi trường BH1 không có số (≥ −8% mỗi 100 tỷ); (4) biểu giá điện cho xút–clo không được nhắc; (5) chiều tăng: bồi thường BH1 > 0 có căn cứ pháp lý nhưng không có số, phân loại khoản trả trước 242 tỷ (G2), φ theo capex. Đạt: số cổ phiếu (mã 411, 30/09/2026, không có cổ phiếu quỹ, không tăng vốn), quỹ KTPL/KH&CN đã trừ cả số dư lẫn tỷ lệ trích 2,43%, capex cam kết Nhơn Trạch có trong mô hình, kiểm toán FY2025 có mặt và sạch, đất HCM là đất thuê, cổ tức CĐKKS đã giải thích"
  },
  "independent_verification": "Tự tính lại công thức base r4 bằng script riêng: CƠ SỞ 11.363 / XẤU 7.744 / TỐT 15.254 so với báo cáo 11.361 / 7.744 / 15.254 — khớp. Phần thay thế còn chi −855,5 và lá chắn thuế +92,6 tỷ khớp. Capex BQ 2017–25 trung bình khoảng 42 tỷ/năm; 9T/26 là 265,7 tỷ, khớp §3.",
  "killer_objection": "Base giả định nhà máy mới (φ·1.844 tỷ) chỉ cần thay một lần rồi dùng mãi, nhưng lá chắn thuế lại tính theo đời 12 năm. Dùng cùng giả định đời 12–20 năm cho cả chu kỳ thay thế thì tâm còn khoảng 9.164–10.685, giảm 6–19%. Trước khi tách được phần capex duy trì khoảng 42 tỷ/năm vốn đã nằm trong E lịch sử, tâm 11.224 có thể đang cao.",
  "recommended_followups": [
    "Đọc khấu hao TSCĐ trong lưu chuyển tiền tệ FY2019–25 để so với capex khoảng 42 tỷ/năm, tức xác định E lịch sử đã gánh bao nhiêu chi phí duy trì; sau đó đưa chu kỳ tái đầu tư nhất quán với L vào base",
    "Đưa kịch bản gián đoạn 2027–2029 vào base, có trọng số, thay vì để ở độ nhạy",
    "Thêm hạng mục điện năng tiêu thụ / biểu giá EVN và mức tiết kiệm kỳ vọng của công nghệ màng ở Nhơn Trạch (chiều tăng)",
    "Sửa cách chiết khấu dòng chi thay thế để kd cao hơn không làm giá trị tăng (APV: chiết khấu capex ở lãi suất của dòng tiền cam kết, cộng lá chắn thuế lãi vay riêng)",
    "Chờ BCTC Q4/26 để kiểm doanh thu H2SO4 sau khi TB2 dừng (giữ hay bỏ TỐT), thuyết minh G2 và số bồi thường"
  ],
  "summary": "Mô hình r4 nhất quán và tái lập được: tôi tự tính lại khớp ba kịch bản đến từng đồng, nguồn số tốt, kiểm toán đúng năm, và lần sửa sau r3 đi theo cả hai chiều có cơ sở. Tuy vậy, base có một lỗ hổng cấu trúc: Nhơn Trạch được coi là chi một lần, không có chu kỳ thay lại, trong khi lá chắn thuế dùng đời 12 năm. Dùng đời nhất quán thì tâm giảm 6–19%, giảm nhẹ một phần vì E lịch sử đã gánh khoảng 42 tỷ/năm capex mà chưa đo được chính xác. Gián đoạn, hoàn nguyên và kịch bản TỐT so với TB2 cũng kéo tâm xuống nhưng chưa nằm trong base. Chiều ngược lại, hiệu suất nhà máy mới, bồi thường, φ theo capex và khoản trả trước G2 đều có thể kéo tâm lên hơn 5%. Hai bên lệch nhau chưa định lượng được, nên kết luận là INCONCLUSIVE chứ không phải CONFIRMED."
}
<<<END_VERDICT>>>