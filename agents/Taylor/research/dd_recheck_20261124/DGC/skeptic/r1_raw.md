**Kết luận: INCONCLUSIVE, độ tin cậy trung bình.** Phần cơ học của bản rà lại là đúng. Nhưng tâm 41.849 phụ thuộc vào hai hạng mục cả báo cáo lẫn r3b đều không định lượng. Một hạng mục kéo tâm lên tới khoảng +14%, một hạng mục kéo xuống tới khoảng −6% (và có thể hơn).

**Những gì đã kiểm và khớp**
- **Tôi tự chạy lại phép tính.** `calc_recheck.py` chạy trên bản sao riêng cho output md5 `e2c7541c…`, trùng với `run1.txt`. Cả 13 file đầu vào khớp md5 đã khoá.
- **Đối chiếu với BQ `ticker_financial` (mốc 29/10/2026):**
  - Tiền 230,2 tỷ, khớp.
  - Vay ngắn hạn 1.391,0 tỷ, vay dài hạn 0, khớp.
  - Số cổ phiếu 379.778.413, so với 379.779.286 trong mô hình: lệch 873 cp, không đáng kể.
  - Tồn kho 2.085,6 tỷ, khớp.
- **Chưa kiểm được:** khoản tiền gửi có kỳ hạn (HTM) 9.531 tỷ. BQ không có cột tương ứng, nên số này vẫn chỉ dựa vào bản trích BCTC nội bộ. Mức ảnh hưởng lớn: phần tiền ròng cộng Nghi Sơn theo sổ ≈ 22.960 đ/cp, tức khoảng 54% tâm trước CK.
- **Tiền đã trừ cổ tức:** cổ tức 8.000 đ/cp đã chi, phải trả cổ tức chỉ còn 0,06 tỷ, nên không đếm hai lần.
- **Ghi chú mù giá:** báo cáo có giá 33.000 (lớp nhãn). Tôi bỏ qua con số này khi đánh giá mô hình.

**Các điểm tấn công**
- **Chiều làm tâm THẤP quá (mạnh nhất).** Theo "cách B" của r3b, nhánh mở lại khai trường 25 chỉ được +500 tỷ năm 2028, rồi bằng 0 mãi mãi. Hệ quả là chắc chắn mở lại (w=1) chỉ đáng 42.484, so với 41.825 khi dừng hẳn, tức chỉ +1,6%. Trong khi chính báo cáo gọi nguồn quặng tự chủ là rủi ro moat số 1. Lợi thế giá vốn quặng là chuyện **mức lợi nhuận**, không phải tăng trưởng, nên khó gọi là "thưởng moat". Biến thể giữ biên vĩnh viễn (`ore_w0.5_term`) cho 48.101, tức +14,1%. Mốc đúng nằm giữa 0 và vĩnh viễn, đo theo thời hạn giấy phép và trữ lượng KT25/19B, nhưng cả hai đều vắng trong báo cáo.
- **Chiều làm tâm CAO quá.** Kiểm toán ngoại trừ 950,9 tỷ tồn kho (BCTC 2025). Khoản này không bị trừ trong mô hình, chỉ nằm trong danh sách "việc còn mở". Nếu mất toàn bộ thì chặn trên ≈ −2.430 đ/cp (−5,8%), chưa tính việc mức biên nền R2 có thể bị thổi phồng theo. Capex môi trường bắt buộc sau vụ án cũng chưa có số; chính báo cáo thừa nhận điều này.
- **r nền nằm ngoài dải Ke.** r = 13,5% cao hơn đầu trên dải 13,4% khoảng 10bp. Ảnh hưởng nhỏ: +0,33% ở đầu trên, khoảng +2% ở giữa dải.

<<<VERDICT_JSON>>>
{
  "case_topic": "DGC — dd_recheck 24/11/2026 (REPORT_recheck_DGC.md, tái dùng mô hình r3b, chỉ đổi r)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra claim fear-buy/§2.5 (tự ghi §2 trụ #2 trượt ⇒ NON, EXCLUDED ZaloPay)",
    "scandal_migration_risk": "pass (có caveat) — WARNING ghi rõ: chưa thấy khởi tố pháp nhân, HOSE hạn chế 26/05, ngoại trừ kiểm toán 2025; trục pháp lý haircut tiền ròng 3/9/29% (legal_axis 39.203 trước CK, −7,0%) được báo song song, loại khỏi base theo luật user 02/11. Recheck tự thừa nhận 'không đọc tin mới' ⇒ tình trạng pháp lý hiện tại chưa được làm mới kể từ r3b",
    "optimistic_comp_sotp_bias": "pass — không dùng comp. SOTP = lõi EBIT (RONIC=Ke) + tiền ròng theo sổ + Nghi Sơn theo giá vốn (NPV 0, trục ±500). Hai nền máy V6 (84.931/74.747) chỉ hiển thị, không trộn vào tâm",
    "data_provenance": "pass một phần — BQ ticker_financial 29/10/2026: tiền 230,2 ✓, vay NH 1.391,0 ✓, vay DH 0 ✓, OShares 379.778.413 vs mô hình 379.779.286 (Δ 873 cp) ✓, tồn kho 2.085,6 ✓. HTM 9.531,0 (≈54% tâm qua tiền ròng) chỉ truy được về MIKE_EXTRACT note 4 p24, chưa đối chiếu PDF gốc (báo cáo tự ghi nhận). Cổ tức 8.000 đ/cp đã chi, phải trả cổ tức 0,06 ⇒ tiền đã ở trạng thái sau cổ tức",
    "liquidity_capacity_realism": "na — không đề xuất sizing mới (EXCLUDED); CK 5 tỷ 0,725% kế thừa r3b",
    "confirmation_bias_flipflop": "pass — tâm 41.849 = r3b (tái lập bằng assert + tôi chạy lại ra cùng md5); chỉ thêm dòng hiển thị r/E15/E16/V6, không đổi giả định. Theo ràng buộc mù, không mở dd_price_zones.json",
    "exit_discipline_gap": "na — không có claim sizing/fear-buy; errata HARD ABANDON (OR) kế thừa ở 'việc còn mở'",
    "missing_items": "fail-unquantified — (1) THỜI HẠN GIẤY PHÉP + TRỮ LƯỢNG KT25/19B vắng mặt: đây là căn cứ duy nhất để chọn giữa biên mở lại = 0 sau 2028 (base, 42.154) và vĩnh viễn (48.101, +14,1%); trọng yếu, không định lượng được nếu thiếu thời hạn. (2) Ngoại trừ kiểm toán FY2025 tồn kho 950,9 tỷ: không trừ trong mô hình; chặn trên ≈ −2.430 đ/cp (−5,8%), xác suất chưa có cơ sở. (3) Capex môi trường bắt buộc mới sau vụ án (bãi thải/xử lý nước/hoàn nguyên KT25): báo cáo tự nêu là chưa có số. (4) Nhà cung cấp quặng mua ngoài và giao dịch bên liên quan (nhánh 'dừng' định giá vĩnh viễn trên quặng mua ngoài): chưa kiểm. (5) Đạt: quỹ KTPL 592,8 đã trừ; dự phòng 200 đã trừ; số cổ phiếu có nguồn p36 khớp BQ; Nghi Sơn có trục ±500 tỷ chi vượt dự toán. (6) Giá điện (đầu vào lớn của phốt pho vàng): na, không kiểm được",
    "symmetry": "{\"too_high_checked\": 8, \"too_low_checked\": 9, \"too_high_items\": [\"HTM 9.531 chưa đối chiếu PDF\", \"ngoại trừ tồn kho 950,9 (≤−5,8%)\", \"capex môi trường bắt buộc sau vụ án chưa có\", \"trục pháp lý ngoài base (−7,0%)\", \"nền biên r4 39.714 (−5,8%) vs R2 — GPM Q3 thực tế 20,5%/24,6% ủng hộ R2 ⇒ pass\", \"Q4 lấy trung bình EBIT 9T có thể gồm thời gian khai trường còn chạy (<1%)\", \"cổ tức/số cổ phiếu sau 30/09 — pass\", \"bên liên quan / nguồn cung quặng mua ngoài chưa kiểm\"], \"too_low_items\": [\"cách B: nhánh mở lại không có biên sau 2028 ⇒ w=1 chỉ +1,6%; biên vĩnh viễn +14,1%\", \"r nền 13,5% > đầu trên dải Ke 13,4% (+0,33%; giữa dải ≈+2%)\", \"RONIC=Ke trong khi NOPAT/vốn hoạt động ~40% (ronic20 44.133, +4,7%) — theo luật D4, không phải lỗi\", \"lá chắn thuế dự phòng 0 [UL] (shield20 +1,4%)\", \"nhánh dự phòng vĩnh viễn 100 tỷ/quý trọng số 1/3 chỉ dựa tiền lệ TKV, không có dữ liệu riêng DGC\", \"tồn kho 2.086 so với YE25 1.682: vốn lưu động có thể được giải phóng (chưa vào mô hình)\", \"nền máy V6 cao gấp 1,8–2,0 lần tâm — chênh lệch do lớp phán đoán\", \"trọng số kịch bản 0,25/0,5/0,25 vs r2 0,3/0,5/0,2 (đã nghiêng lên, pass)\", \"dự thu lãi 93,2 trong HTM đã tính, tiền tính theo mệnh giá — pass\"]}"
  },
  "independent_verification": "(a) Chạy lại calc_recheck.py trên bản sao riêng (/tmp, wc_venv python -I): output md5 e2c7541c… = run1.txt, mọi assert CONTROL đạt. (b) BQ tav2_bq.ticker_financial DGC 2026-10-29: Cash 230,18 tỷ, StDebt 1.391,0, LtDebt 0, OShares 379.778.413, tồn kho 2.085,6 — đều khớp hằng số trong model.py. (c) Tính lại: CASH_DEP = 230,2 + 9.531,0 = 9.761,2 ✓; tiền ròng + NS theo sổ ≈ 8.719 tỷ phần cổ đông mẹ ≈ 22.960 đ/cp ≈ 54% tâm trước CK, giải thích vì sao tâm ít nhạy với r (−120bp ⇒ +4,3%). HTM 9.531 không có trong BQ ⇒ chưa kiểm độc lập được",
  "killer_objection": "Giá trị của việc mở lại khai trường 25 (nguồn moat chính được nêu) là một cú chuyển nhị phân không có dữ liệu: base cho bằng 0 sau 2028 (w=1 chỉ +1,6%), biến thể vĩnh viễn cho +14,1%. Giá trị đúng phụ thuộc thời hạn giấy phép/trữ lượng mỏ, nhưng không bản DD nào ghi thời hạn này. Ở chiều xuống, ngoại trừ kiểm toán 950,9 tỷ tồn kho chưa được mô hình hoá (≤−5,8%). Tâm 41.849 đúng về số học nhưng chưa có căn cứ đầy đủ ở cả hai đầu.",
  "recommended_followups": [
    "Lấy thời hạn giấy phép + trữ lượng còn lại của KT25/19B từ văn bản gốc (Bộ TN&MT / công bố DGC); thay biên mở lại bằng 0 hoặc vĩnh viễn bằng biên hữu hạn theo thời hạn giấy phép",
    "Đối chiếu HTM 9.531,0 và note 4 p24 với PDF BCTC HN Q3/2026 gốc",
    "Định lượng ngoại trừ tồn kho 950,9 tỷ: đối chiếu với BCTC soát xét bán niên 2026 xem ngoại trừ đã được gỡ chưa; nếu chưa, thêm trục haircut tồn kho đối xứng",
    "Quét NQ HĐQT/ĐHCĐ và công văn cơ quan quản lý 12 tháng gần nhất tìm capex môi trường bắt buộc (bãi thải, xử lý nước, hoàn nguyên KT25)",
    "Xác định nhà cung cấp quặng mua ngoài và kiểm tra có phải bên liên quan không (rủi ro liên tục nguồn cung cho nhánh 'dừng' định giá vĩnh viễn)",
    "Làm mới quét pháp lý (recheck ghi rõ không đọc tin mới) trước khi tái dùng nhãn"
  ],
  "summary": "Bản rà lại đúng như mô tả: chỉ đổi r trên mô hình r3b đã khoá. Tôi tự chạy lại ra đúng md5, và các con số bảng cân đối then chốt (tiền, vay, số cổ phiếu, tồn kho) khớp BQ. Bảng độ nhạy r nội tại nhất quán, và tâm ít nhạy với r là do ~54% giá trị nằm ở tiền ròng. Tuy vậy tâm 41.849 còn dựa trên hai điểm chưa có căn cứ đầy đủ, ngược chiều nhau. Chiều lên: nhánh mở lại khai trường không được ghi biên lợi nhuận nào sau 2028 (chắc chắn mở lại chỉ +1,6%), trong khi biến thể vĩnh viễn cho +14%; thời hạn giấy phép và trữ lượng mỏ, dữ kiện quyết định điểm đúng, đều vắng. Chiều xuống: ngoại trừ kiểm toán 950,9 tỷ tồn kho chưa được mô hình hoá (≤−5,8%), capex môi trường bắt buộc sau vụ án chưa có số, và HTM 9.531 chưa đối chiếu PDF gốc. Không có hạng mục nào định lượng chắc chắn >5% để REFUTED, nhưng cũng chưa đủ căn cứ để CONFIRMED."
}
<<<END_VERDICT>>>