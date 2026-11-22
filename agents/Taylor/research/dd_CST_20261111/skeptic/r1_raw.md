**Kết luận: REFUTED, độ tin cậy cao.** Mô hình tái lập khớp từng đồng, nhưng tâm 13.084 có lẽ đang **quá cao** vì báo cáo bỏ sót một khoản lớn: phần lợi nhuận chảy sang quỹ khen thưởng phúc lợi và các khoản khác không thuộc cổ đông.

**Phần đã kiểm độc lập**
- **Tái lập mô hình:** chạy lại công thức với `calc/assumptions.json` ra bi quan / cơ sở / lạc quan = 6.517 / 12.808 / 21.460, tâm 13.084. Khớp báo cáo.
- **Chuỗi vốn chủ trên BQ** (`ticker_financial`, VCSH = BVPS×OShares, năm 2021–2025): VCSH tăng ít hơn LNST trừ cổ tức tiền mỗi năm khoảng **46 / 56 / 84 / 83 / 92 tỷ**. Đó là phần lợi nhuận ra khỏi VCSH mà không phải cổ tức, cộng lại khoảng 37% LNST 5 năm và khoảng 79% LNST 2024–25.
- **Số liệu chính báo cáo cũng cho thấy điều này** (§6): lợi nhuận đã phân phối 82,8 tỷ, trong đó cổ tức chỉ 29,9 tỷ ⇒ **52,9 tỷ đã rời VCSH**. Báo cáo chỉ nhắc quỹ phúc lợi ở chỗ tính trần cổ tức, không đưa vào N.

**Ảnh hưởng tới tâm (chiều ĐẮT)**
- Mô hình dùng N = toàn bộ LNST trong công thức thu nhập thặng dư, nên coi cả phần quỹ phúc lợi là của cổ đông.
- Trừ phần rò theo tỷ lệ: 37% ⇒ tâm **8.617 (−34%)**; 64% ⇒ **5.358**.
- Trừ phần rò cố định 50–70 tỷ/năm ⇒ tâm **5.927 / 3.725**.
- Mức ảnh hưởng vượt xa ngưỡng 5% của tâm. Kết luận "không có biên an toàn" vẫn đứng, nhưng **cả vùng giá trị và ngưỡng luật 10.779 đều sai**.

**Chiều RẺ (có thật nhưng nhỏ hơn)**
- r = 13,5% với β = 1 có thể quá cao cho một đơn vị gia công theo giá vốn cộng lãi. Với r = 11%, tâm là 15.587 (+19%).
- Kịch bản bi quan (trọng số 30%) dựa trên kế hoạch 36 tỷ chỉ có từ báo chí. Kế hoạch của doanh nghiệp nhà nước thường đặt thấp.
- Nếu lấy N theo chu kỳ ≈ 106 thì nhãn đảo chiều (báo cáo đã tự nêu).
- Ba điểm này không bù được phần quỹ phúc lợi bị bỏ sót.

**Thiếu sót khác**
- **Vốn còn phải chi cho dự án mở rộng mỏ Cao Sơn** (tổng 1.829,5 tỷ) không có số. Báo cáo giả định NPV = 0, trong khi chính mô hình nói ROE < r. Nếu vốn mới cũng chỉ sinh lãi ở mức ROE ~7,9% thì NPV âm. Chưa định lượng được.
- **Nghĩa vụ hoàn nguyên mỏ khi đóng cửa** ngoài khoản ký quỹ môi trường 212 tỷ: không được bàn tới.
- **Thuế suất tài nguyên** chưa đọc.

**Giới hạn:** thư mục `src/` và `src_q3/` đã bị dọn ngày 19/11, nên tôi không mở lại được BCTC gốc; số liệu chỉ đối chiếu qua BQ và các số báo cáo tự trích. Theo ràng buộc mù, tôi không mở sổ vùng giá, nên phép kiểm lật kết luận qua các lần sửa được đánh `na`.

<<<VERDICT_JSON>>>
{
  "case_topic": "CST (Than Cao Sơn – TKV) — DD định giá 11/11/2026, tâm 13.084 (12.681 sau CK)",
  "verdict": "REFUTED",
  "confidence": "high",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — §7 chỉ có WARNING (tái cơ cấu TKV hạn 27/11, giao dịch bên liên quan, đổi kiểm toán, dòng 17 LCTT có dấu lạ); không có vụ việc trong tài liệu, nhưng chưa tra pháp lý bên ngoài (báo cáo tự ghi)",
    "optimistic_comp_sotp_bias": "pass — comp chỉ để đối chiếu, không quyết định tâm; đã bổ sung MVB; không dùng SOTP. Chiều RẺ: r=13,5% β=1 có thể cao cho đơn vị cost-plus (r=11% ⇒ 15.587)",
    "data_provenance": "fail (một phần) — mô hình tái lập đúng; LNST quý và VCSH khớp BQ; nhưng src/ và src_q3/ đã bị TRIM 19/11 nên không mở lại được BCTC gốc; N bi quan (30% trọng số) dựa trên báo chí, mâu thuẫn −28%/−56% chưa giải",
    "liquidity_capacity_realism": "na — không có đề xuất vị thế; báo cáo đã tự giới hạn 0,1–0,3 tỷ trên ADV60 0,132 tỷ",
    "confirmation_bias_flipflop": "na — brief cấm mở kb/dd_price_zones.json; lần phản biện duy nhất (11/11, Phụ lục E) đã được áp, không đảo nhãn",
    "exit_discipline_gap": "na — không có luận điểm sizing/fear-buy; §10 có mốc M1–M4 hai chiều",
    "missing_items": "fail — (1) QUỸ KHEN THƯỞNG PHÚC LỢI / phần LN rời VCSH không phải cổ tức: BQ 2021–25 rò 46/56/84/83/92 tỷ/năm (~37% LNST 5 năm, ~79% 2024–25); 9T/26 rò 52,9 = 82,8 phân phối − 29,9 cổ tức (số chính báo cáo). Mô hình dùng N = toàn bộ LNST ⇒ tâm 8.617 (rò 37%) tới 3.725 (rò cố định 70 tỷ), −34% tới −72%, định lượng được và trọng yếu. (2) Vốn còn phải chi cho dự án mở rộng 1.829,5 tỷ không có số; giả định NPV=0 mâu thuẫn ROE<r. (3) Nghĩa vụ hoàn nguyên mỏ ngoài ký quỹ 212 tỷ không được bàn. (4) Thuế suất tài nguyên chưa đọc. Đạt: số cp 42.846.773 (khớp BQ OShares, không thấy phát hành), BCTC 2025 kiểm toán sạch, 6T soát xét sạch, một lần 2024 đã chuẩn hoá, giấy phép tới 2045"
  },
  "independent_verification": "Chạy lại công thức với assumptions.json ⇒ 6.517/12.808/21.460, tâm 13.084: KHỚP. Đối chiếu BQ ticker_financial: VCSH 30/9/26 = 961,3 và 31/12/25 = 1.028,2 KHỚP báo cáo; từ cùng chuỗi đó tính ra phần LN rời VCSH không phải cổ tức 46–92 tỷ/năm mà mô hình bỏ sót.",
  "killer_objection": "N trong mô hình là LNST gộp, nhưng mỗi năm 46–92 tỷ (trung bình ~37%, gần đây ~79% LNST) rời VCSH vào quỹ khen thưởng phúc lợi/khoản không thuộc cổ đông. Phần lãi thật thuộc cổ đông chỉ bằng một phần nhỏ của 75 tỷ ⇒ tâm có lẽ ở ~4.000–8.600 chứ không phải 13.084.",
  "recommended_followups": [
    "Đọc thuyết minh VCSH/quỹ khen thưởng phúc lợi trong KT25 và Q3/26 (bảng biến động VCSH) để tách 52,9 tỷ (và 92 tỷ năm 2025) thành quỹ KTPL / quỹ thưởng quản lý / khoản khác; lấy lại BCTC gốc vì src đã bị TRIM",
    "Dựng lại N theo phần cổ đông thực nhận (LNST − trích quỹ không thuộc VCSH), theo tỷ lệ hoặc theo mức tuyệt đối tuỳ quy chế trích quỹ của TKV",
    "Định lượng vốn còn phải chi dự án mở rộng Cao Sơn và kiểm giả định NPV=0 khi ROE<r",
    "Kiểm nghĩa vụ hoàn nguyên/đóng mỏ ngoài ký quỹ 212 tỷ và thuế suất tài nguyên",
    "Kiểm lại r cho đơn vị cost-plus (chiều RẺ) và nguồn gốc kế hoạch 36 tỷ (NQ ĐHĐCĐ gốc)"
  ],
  "summary": "Mô hình thu nhập thặng dư của CST tái lập chính xác, và các số VCSH khớp BQ. Nhưng báo cáo bỏ sót một mục bắt buộc trong checklist: lợi nhuận bị trích ra khỏi VCSH ngoài cổ tức (quỹ khen thưởng phúc lợi). Chuỗi VCSH trên BQ cho thấy 46–92 tỷ/năm rời VCSH như vậy, và chính số liệu 9T/26 của báo cáo cũng xác nhận: phân phối 82,8 tỷ, cổ tức chỉ 29,9. Mô hình lại dùng LNST gộp làm N, nên tâm bị đẩy lên khoảng 34–72%. Chiều rẻ có thật nhưng nhỏ hơn: r=13,5% có thể cao cho đơn vị cost-plus (+19% nếu r=11%), kịch bản bi quan dựa trên báo chí. Hai điểm này không bù được khoản bỏ sót. Kết luận 'giá trên tâm' có lẽ còn mạnh hơn, nhưng tâm, vùng và ngưỡng 10.779 phải tính lại. BCTC gốc đã bị dọn khỏi thư mục nên chưa kiểm lại được tận gốc."
}
<<<END_VERDICT>>>