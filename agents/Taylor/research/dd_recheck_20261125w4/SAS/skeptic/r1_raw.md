**Kết luận: INCONCLUSIVE (độ tin trung bình).** Phần tính toán của báo cáo đúng. Mình tự tính lại tâm và khớp, D4 cũng áp đúng. Nhưng vẫn còn ba mảng có thể làm lệch tâm nhiều mà báo cáo chưa định lượng, và thiếu một hạng mục định lượng được theo chiều làm tâm tăng.

**Đã tự kiểm lại**
- **Tâm tại điểm giữa lưới** (Δ −25%, N0 479,7, r 13,5%), dùng số bảng cân đối trong `assumptions_r3.json`:
  - PV vận hành ≈ 2.458 tỷ. Tiền ròng + Q4 850,7; đầu tư dài hạn 253,8; phải thu dài hạn 242,0; XDCB+BĐS đầu tư 150,3; trừ KTPL 9T 63,1.
  - Kết quả 29.159 đ/cp trước CK và ≈27.430 sau CK, so với 29.208 / 27.477 báo cáo. Phần chênh đến từ độ lồi theo r. **Khớp.**
- **Biên vận hành:** 12,57% (9T/25) và 15,42% (9T/26), tính lại từ q3_11 OCR. **Khớp.** Tổng 9T trong báo cáo KQKD tự cân.
- **Số cổ phiếu:** q3_35 cho 133.481.310 phát hành, 133.451.910 đang lưu hành, không đổi trong 9T. Mình đã nghi pha loãng vì EPS Q3 hàm ý ~135,9 tr cp, giả thuyết này bị bác. Mô hình dùng số phát hành thay vì số lưu hành, lệch +0,02%, không đáng kể.
- **Cột Q3 của OCR có lỗi.** Doanh thu Q3/26 trên OCR là "719,65 tỷ", BQ cho 779,65. Vì vậy mức "DT Q3 −10,6% YoY" thực chất chỉ là −3%. Các so sánh trong quý ở §3.4 chưa đáng tin, nhưng không chịu tải vì E17 #1 dùng số 9T.

**Chiều đắt (tâm có thể quá cao)**
1. **Xác suất trượt thầu Long Thành mặc định 50%, không có bằng chứng.** Kết cục thực tế có hai đỉnh (trượt −40…−55%, trúng +5…−10%). Lưới lại một đỉnh, tâm Δ −25% ứng đúng q = 0,5. Mỗi 10 điểm % Δ ≈ 8% tâm. Nếu q = 0,7 thì tâm giảm khoảng 7%. P10–P90 cũng hẹp hơn thực tế vì lưới không thể hiện hai đỉnh.
2. **Thiếu thời hạn hợp đồng mặt bằng ACV** trong khi mô hình định giá vĩnh viễn TV = E₂₀₂₈/r. Mặt bằng được giao không đấu thầu (KL TTCP 2017). Không định lượng được nhưng trọng yếu.
3. **Truy thu tiền thuê đất 2015–2024** là nghĩa vụ tiền mặt, có thể định lượng, nhưng chỉ để ở mức WARNING và không tra lại ngày 25/11. Báo cáo không nói có dự phòng hay chưa.
4. **E17 #1 chỉ kéo biên về mức 9T/25.** Theo BQ, EBITM của chính SAS: 2023–24 khoảng 6–13%, 2025 khoảng 14–21%, 2026 khoảng 22–24%. Đỉnh lợi nhuận có thể kéo dài nhiều năm, không chỉ một năm.
5. **E17 #3 có lỗi nhất quán:** cộng tài sản GTGT 240,6 tỷ mà không bù trừ các khoản phải trả vận hành, vốn cũng đang tính bằng 0. VLĐ ròng ngoài tiền chỉ 130,3 tỷ, nên m của #3 bị phóng đại khoảng 46%. Ảnh hưởng tới tâm khoảng −1%.

**Chiều rẻ (tâm có thể quá thấp)**
1. **Năm hoá 9T×4/3 bỏ qua mùa vụ Q4.** Theo BQ, doanh thu Q4 bằng 1,10× / 1,12× / 1,25× trung bình Q1–Q3 trong 2023/24/25. Báo cáo không có mục này. Ước tâm tăng khoảng +2…+5%, giả định biên Q4 không giảm.
2. **Hệ số cắt 86% ở E17 #2** lấy từ tiền lệ khác bản chất (đối tác liên doanh vỡ). Ứng đền bù GPMB thường chuyển thành quyền sử dụng đất. Đây là điều chỉnh giảm chưa có cơ sở độc lập.
3. **Các mục khác đã kiểm, không vào tâm:** cổ tức từ Xăng dầu TSN (độ nhạy +5,43% ở 71 tỷ/năm), dải Ke (+0,46…+5,95%), β = 1 là giả định không kiểm được (BQ chỉ có Beta dạng bậc 2/3, gần nhất là NULL), HTK hàng hoá tăng thêm 134 tỷ có thể thu hồi ra tiền.

Phần mô hình nên giữ nguyên. Nên bổ sung ba thứ trước khi chốt tâm: thời hạn hợp đồng ACV, số tiền truy thu tiền thuê đất cùng tình trạng dự phòng, và cơ sở cho xác suất trúng thầu Long Thành.

<<<VERDICT_JSON>>>
{
  "case_topic": "SAS (SASCO, UPCoM) — DD rev3 25/11/2026, tâm 27.477 đ/cp (P10–P90 22.430–32.420), tâm_adj sơ bộ 26.256",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không đưa ra claim fear-buy/§2.5 (§6 tự ghi 'không đủ điều kiện')",
    "scandal_migration_risk": "fail (mềm) — mặt bằng ACV không đấu thầu (KL TTCP 2017) và truy thu tiền thuê đất 2015–2024 vốn đã ở cấp pháp nhân, nhưng §3.7 'không tra lại 25/11': chưa xác nhận trạng thái pháp lý hiện tại, chưa định lượng nghĩa vụ truy thu hay dự phòng",
    "optimistic_comp_sotp_bias": "fail (một phần) — không dùng comp; nhưng lưới Long Thành gán ngầm q(trượt thầu)=0,5 mà không có bằng chứng (kết cục hai đỉnh mô hình hoá thành một đỉnh tâm −25%); mỗi 10pp Δ ≈ 8% tâm. E17 #3 cộng tài sản GTGT 240,6 tỷ mà không bù trừ khoản phải trả vận hành (VLĐ ròng ngoài tiền chỉ 130,3) ⇒ m #3 phóng đại khoảng 46%",
    "data_provenance": "pass — số BCTC truy được về q3_07/q3_11/q3_28/q3_35/h1_10/h1_52 và assumptions_r3; tổng 9T tự cân; số CP 133.481.310 khớp q3_35 (lưu hành 133.451.910, chênh 0,02%). Caveat: OCR cột Q3 có lỗi (DT Q3/26 OCR 719,65 vs BQ 779,65; lợi nhuận gộp Q3 không cân) ⇒ các so sánh trong quý ở §3.4 chưa đáng tin, nhưng không chịu tải",
    "liquidity_capacity_realism": "na — không đề xuất sizing (V8 ≤2% NAV chỉ ở dạng điều kiện; CK kế thừa r3)",
    "confirmation_bias_flipflop": "pass — Δ −13,21% so với r3 do luật D4 (thay đổi luật, có ghi chép) + lãi Q4 +51 đ; CONTROL tái lập r3 31.658. Không mở dd_price_zones.json theo ràng buộc mù của brief",
    "exit_discipline_gap": "na — không có claim mua; §8 có mốc đổi nhận định hai chiều",
    "missing_items": "fail (không định lượng được) — (1) thời hạn/điều khoản hợp đồng mặt bằng ACV vắng mặt trong khi TV vĩnh viễn E/r: không định lượng được, trọng yếu; (2) số tiền truy thu tiền thuê đất + trạng thái dự phòng: định lượng được nhưng chưa làm; (3) capex cam kết ĐHĐCĐ 2026 / nghĩa vụ cải tạo mặt bằng ACV: báo cáo tự ghi 'chưa có văn bản'; (4) mùa vụ Q4 trong năm hoá N0 (chiều lên, ước +2…+5%). Pass: số CP, quỹ KTPL (99,7 tỷ + eps_ratio 0,883), BCTC 2025 đã kiểm toán có, loại thu nhập tài chính khỏi N0 (one-off cổ tức). Chưa nêu ý kiến kiểm toán/soát xét có đoạn nhấn mạnh hay không",
    "symmetry": "{too_high_checked: 7, too_low_checked: 8, too_low_items: ['mùa vụ Q4 (BQ: DT Q4 = 1,10/1,12/1,25× TB Q1–Q3 2023–25) — năm hoá 9T×4/3 và Q4=N0/4 có thể thấp, ước +2…+5%', 'E17 #2 cắt 86% dựa trên tiền lệ khác bản chất (đối tác liên doanh vỡ vs ứng GPMB thường chuyển thành QSDĐ)', 'r 13,5% vs dải Ke 12,3–13,4% (+0,46…+5,95%, chỉ hiển thị)', 'β=1 giả định — BQ risk_rating chỉ có bậc 2/3/NULL, không kiểm được', 'cổ tức Xăng dầu TSN vốn hoá > sổ (+5,43% ở 71 tỷ/năm; để C hợp lý vì 2 điểm dữ liệu)', 'HTK hàng hoá tăng 134 tỷ có thể thu hồi ra tiền nếu chuyển về mô hình đối tác', 'số CP phát hành vs lưu hành (+0,02%, không đáng kể)', 'giả thuyết pha loãng từ EPS Q3 hàm ý 135,9 tr cp — bác bỏ (q3_35 không đổi)']; too_high: ['q(trượt Long Thành) ngầm 0,5', 'thiếu thời hạn hợp đồng ACV trong TV vĩnh viễn', 'truy thu tiền thuê đất chưa định lượng', 'E17 #1 chỉ neo vào 9T/25 trong khi EBITM 2023–24 khoảng 6–13%', 'E17 #3 không bù trừ VLĐ', 'OCR Q3 làm méo bằng chứng cơ chế biên', 'capex/nghĩa vụ ACV chưa kiểm']}"
  },
  "independent_verification": "Tự tính lại tâm tại điểm giữa lưới (Δ −25%, N0 479,7, r 13,5%, TV E/r, +Q4, chiết khấu 55 ngày): 29.159 trước CK / ≈27.430 sau CK, so với báo cáo 29.208 / 27.477 (chênh do độ lồi theo r) — KHỚP. Tính lại biên vận hành 12,57% / 15,42% từ q3_11 — KHỚP. Số CP 133.481.310 khớp q3_35. BQ ticker_financial: DT Q3/26 = 779,65 tỷ, cho thấy OCR (719,65) sai ở cột Q3",
  "killer_objection": "Tâm phụ thuộc mạnh vào hai giả định không có bằng chứng: TV vĩnh viễn trên mặt bằng ACV vốn giao không đấu thầu, chưa rõ thời hạn hợp đồng, và xác suất trượt thầu Long Thành ngầm bằng 50% (mỗi 10pp Δ ≈ 8% tâm). Hai giả định này đều có thể kéo tâm xuống nhiều hơn toàn bộ Σ E17 (−4,44%)",
  "recommended_followups": [
    "Tra thời hạn/điều khoản hợp đồng thuê mặt bằng SAS–ACV tại TSN; nếu có kỳ hạn thì thay TV vĩnh viễn bằng niên kim hữu hạn",
    "Định lượng số tiền truy thu tiền thuê đất 2015–2024 và kiểm dự phòng trong thuyết minh nợ phải trả/dự phòng",
    "Ghi cơ sở bằng chứng cho xác suất trúng thầu Long Thành; cân nhắc lưới hai đỉnh để P10/P90 phản ánh đúng kết cục",
    "Kiểm mùa vụ Q4 (tách thu nhập tài chính Q4/2024–Q4/2025 từ BCTC) trước khi giữ năm hoá 9T×4/3",
    "Sửa E17 #3: dùng VLĐ ròng ngoài tiền (130,3) hoặc bù trừ khoản phải trả vận hành thay vì cộng gộp GTGT 240,6",
    "Đọc ý kiến kiểm toán FY2025 / soát xét H1/2026 (đoạn nhấn mạnh) và nghị quyết ĐHĐCĐ 2026 về capex",
    "OCR lại cột Q3 trang q3_11/q3_35 trước khi dùng làm bằng chứng cơ chế biên"
  ],
  "summary": "Mô hình rev3 tính đúng: tâm tái lập độc lập khớp 27.477, D4 áp đúng (TV = E₂₀₂₈/r, không tái đầu tư), số BCTC 9T truy được về nguồn và tự cân, số CP khớp thuyết minh. Chưa CONFIRMED vì ba mảng có thể làm lệch tâm nhiều mà báo cáo chưa định lượng: (1) TV vĩnh viễn trong khi thiếu thời hạn hợp đồng mặt bằng ACV vốn giao không đấu thầu; (2) truy thu tiền thuê đất để ở mức WARNING, không tra lại; (3) xác suất trượt thầu Long Thành ngầm 0,5 không có cơ sở. Chiều ngược lại, báo cáo bỏ sót mùa vụ Q4 (BQ: DT Q4 cao hơn TB Q1–Q3 10–25%), có thể làm tâm cao hơn +2…+5%; hệ số cắt 86% của E17 #2 dựa trên tiền lệ khác bản chất; E17 #3 cộng GTGT không bù trừ VLĐ. Theo bằng chứng hiện có, tâm có rủi ro hai chiều; chiều xuống lớn hơn về độ lớn nhưng chưa định lượng được, chiều lên nhỏ hơn nhưng có dữ liệu."
}
<<<END_VERDICT>>>