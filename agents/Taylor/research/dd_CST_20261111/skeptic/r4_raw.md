**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phần số học của rev 4 đứng vững: tôi tự đọc trang gốc TM17 và BCĐKT Q3, mọi số khớp. Cũng không tìm thấy lỗi nào đủ để đảo tâm 6.022 / 5.837. Tôi không xác nhận được vì hai hạng mục trọng yếu vẫn chưa định lượng được và hiện chỉ nằm ở bảng độ nhạy. Theo luật attack 8, hạng mục trọng yếu không định lượng được thì kết luận là INCONCLUSIVE.

**Đã tự kiểm lại (khớp)**
- **TM17 (ảnh trang 33):** ĐTPT 39.005.960.171 = 0,30000 × LNST 2024 130.019.867.238. LNST chưa phân phối 294,82 − 164,155 = 130,66 tỷ.
- **BCĐKT Q3 (ảnh trang 4):** LNST chưa phân phối 213,41 → 146,55; ĐTPT 386,31 không đổi; mục 420a = 130,66 ở cả hai kỳ. Từ đó KTPL + thưởng quản lý 2026 = 82,749 − 29,99 = 52,76. Số cổ phần 42.846.773 khớp vốn góp 428,47 tỷ.
- **Mô hình:** annuity (13,5%, T=19) = 6,739; hệ số của B₀ = 0,045. Ba kịch bản ra 3.622 / 5.887 / 9.143, bình quân trọng số 6.022. Khoản chia 130,66 tỷ cho +1.459 đ/cp. Tất cả khớp báo cáo.

**Chỗ yếu khiến tâm có thể quá CAO**
1. **Khoản chia 130,66 tỷ có thể bị trích thêm KTPL tới trần.** Theo chính quy tắc của báo cáo (`min(0,64N; 82,3)`), năm 2025 KTPL 82,30 đã chạm trần 82,3. Vì vậy số học TM17 không phân biệt được "tích luỹ đi 100% vào cổ tức" với "trần đã chặn KTPL". Năm 2026 KTPL mới 52,76, còn dư ~29,5 tỷ dưới trần. Nếu ĐHĐCĐ bất thường lấp phần dư này từ khoản 130,66, tâm giảm khoảng −330 đến −690 đ/cp (−5,5% đến −11%, ước lượng). Bảng độ nhạy của báo cáo không có kịch bản trung gian này.
2. **Nợ giảm mạnh mà báo cáo không giải thích.** Vay đi từ 485,1 tỷ xuống 129,5 tỷ trong 9 tháng 2026 (trả ròng ~356 tỷ). Điều này không khớp với giả định dự án mở rộng 1.829,5 tỷ (70% vay) còn ~1.020 tỷ phải chi (ước lượng). Có hai cách đọc: dự án chậm/đình, hoặc tiền hoạt động đang được giữ lại để trả nợ thay vì chia cổ đông.
3. **Dự phòng phải trả ngắn hạn 333,52 tỷ (TM25a) chưa rõ bản chất.** Khoản này từ 0 lên 333,52 tỷ, báo cáo chỉ coi là yếu tố mùa vụ. Nếu nó là nghĩa vụ thật thì đó là dòng tiền ra chưa được mô hình hoá.
4. **N cơ sở 75 tỷ dựa vào việc Q4/2026 lặp lại Q4/2025.** Thực tế 9 tháng 2026 chỉ có 15,88 tỷ, trong khi Q4/2024 chỉ có 6,7 tỷ.

**Chỗ yếu khiến tâm có thể quá THẤP**
- Lãi vay sẽ giảm mạnh khi dư nợ còn 129,5 tỷ (chi phí lãi vay 2025 là 30,4 tỷ), nhưng N chưa phản ánh. Ảnh hưởng còn tuỳ cơ chế giá vốn cộng lãi có đẩy phần lãi vay này về TKV hay không.
- Kịch bản đóng mỏ 2030 lại cho giá trị cao hơn base. Đây là đặc tính của khung mô hình (B₀ bị khoá, chỉ sinh N cổ đông < r·B), không phải tham số đang nghiêng về phía lạc quan.
- Kịch bản tái cơ cấu TKV ở giá sổ sách (22.436 đ/cp) chỉ được hiển thị, chưa có trọng số.

**Hạng mục thiếu (attack 8)**
- **Fail:** trữ lượng còn lại và thời hạn giấy phép khai thác của mỏ hiện tại. Mốc 08/2045 thực ra là của dự án mở rộng.
- **Fail:** NQ ĐHĐCĐ / HĐQT trong 12 tháng gần nhất về vốn cam kết cho dự án mở rộng. Ảnh hưởng ±3.017 đ/cp, tức ~50% tâm.
- **Chưa giải thích:** bản chất khoản dự phòng 333,5 tỷ.
- **Chưa kiểm:** bảo lãnh và nghĩa vụ với bên liên quan.
- **Đạt:** quỹ KTPL, số cổ phần, ý kiến kiểm toán (FY2025 có và sạch), khoản Q4 quyết toán một lần trong năm gốc.

Báo cáo có chứa giá thị trường (14.100); tôi đã bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "CST (Than Cao Sơn – TKV) DD rev4 — tâm 6.022 / 5.837 đ/cp",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không có claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — §4 chỉ liệt kê WARNING (tái cơ cấu TKV, giao dịch bên liên quan, đổi kiểm toán, cả hai ý kiến sạch); không thấy dấu hiệu ở cấp pháp nhân trong các tài liệu đã đọc; chưa tra UBCKNN/HNX (báo cáo tự ghi)",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; mô hình RI hữu hạn tự tính lại khớp (annuity 6,739, hệ số B 0,045, 3.622/5.887/9.143 → 6.022). Hai chiều: các kịch bản tăng (tái cơ cấu theo sổ sách, TKV bù chi phí vốn, α=0,50) và giảm (dự án −3.017) đều để ở độ nhạy, không trộn vào base",
    "data_provenance": "pass — tự đọc ảnh KT25 trang 33 (TM17) và Q3 trang 4 (BCĐKT): ĐTPT 39.005.960.171 = 30,000% × 130.019.867.238; 420a 130,66 ở cả hai kỳ; 213,41→146,55; vốn góp 428,47 ⇒ 42,85 tr cp. KTPL 2026 = 52,76 là số suy ra, báo cáo đã tự gắn cờ. Kế hoạch 2026 >36 tỷ chỉ có nguồn báo chí (đã gắn nhãn)",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất vị thế (§9)",
    "confirmation_bias_flipflop": "pass (có lưu ý) — chỉ so các rev cùng mã: 13.084 → 4.563 → 6.022 → 6.022. Rev4 không đổi tâm, cơ sở chuyển từ báo chí sang số học TM17; tuy vậy số học này không loại trừ cách đọc 'trần KTPL chặn' (2025 KTPL 82,30 = đúng trần 82,3), nên nhận định 'tích luỹ 100% vào cổ tức' là suy luận chứ chưa phải bằng chứng",
    "exit_discipline_gap": "na — không có khuyến nghị sizing; §10 liệt kê điều kiện đổi nhận định theo cả hai chiều",
    "missing_items": "fail — (1) vốn cam kết dự án mở rộng 1.829,5 tỷ từ NQ ĐHĐCĐ/HĐQT 12 tháng gần nhất: thiếu, ảnh hưởng tới ±3.017 đ/cp (~50% tâm), chưa định lượng được; dấu hiệu mâu thuẫn chưa giải thích: vay giảm 485,1→129,5 tỷ trong 9T/26 dù dự án được giả định 70% vay; (2) trữ lượng còn lại và thời hạn giấy phép mỏ hiện tại (08/2045 là mốc của dự án mở rộng): thiếu; (3) dự phòng phải trả ngắn hạn 333,52 tỷ (Q3 TM25a, từ 0) chưa xác định bản chất; (4) bảo lãnh/nghĩa vụ với TKV chưa kiểm. Đạt: KTPL, số cổ phần, kiểm toán FY2025 sạch, khoản Q4 một lần"
  },
  "independent_verification": "Đọc ảnh trang gốc KT25 trang 33 và Q3 trang 4: ĐTPT = 30,000% LNST 2024 (khớp tới đồng), 420a = 130,66 không đổi, KTPL+thưởng QL 2026 suy ra = 52,76, số cổ phần 42,85 tr. Tính lại tâm từ công thức: 0,30×3.622 + 0,45×5.887 + 0,25×9.143 = 6.022; khoản chia +1.459 = 3.049 − 1.315 − 275. Tất cả khớp.",
  "killer_objection": "Năm 2025 KTPL (82,30) đúng bằng trần trong quy tắc của chính báo cáo, nên TM17 không chứng minh được rằng phần LN tích luỹ được miễn trích quỹ. Năm 2026 KTPL mới 52,76, còn ~29,5 tỷ dư dưới trần mà ĐHĐCĐ bất thường có thể lấp từ khoản 130,66 (−330 đến −690 đ/cp, ước lượng). Cộng thêm vốn còn phải chi cho dự án mở rộng và suất sinh lời của nó (±50% tâm) vẫn chưa định lượng được.",
  "recommended_followups": [
    "Lấy NQ ĐHĐCĐ bất thường 20–30/12/2026 (phương án phân phối 130,66 tỷ, có trích KTPL hay không) — điều kiện bắt buộc để chốt base",
    "Đọc Q3 TM25a: bản chất khoản dự phòng phải trả 333,52 tỷ",
    "Tìm NQ ĐHĐCĐ 2026/HĐQT về tiến độ và vốn dự án mở rộng Cao Sơn; giải thích việc trả ròng ~356 tỷ nợ vay trong 9T/26",
    "Thêm kịch bản độ nhạy 'KTPL lấp tới trần 82,3 năm 2026 từ khoản 130,66' (≈−29,5 tỷ)",
    "Xác minh trữ lượng còn lại và thời hạn giấy phép khai thác mỏ hiện tại (không phụ thuộc dự án mở rộng)"
  ],
  "summary": "Rev 4 vững về số học: TM17 và BCĐKT Q3 được tôi tự đọc từ ảnh trang gốc và khớp, công thức mô hình tái lập đúng 6.022. Bảng độ nhạy trình bày cả hai chiều. Tuy vậy lập luận then chốt của rev 4 (khoản 130,66 tỷ chia 100% cổ tức vì ĐTPT = 30% LN năm) không loại trừ được cách đọc 'KTPL bị chặn ở trần': KTPL 2025 bằng đúng trần 82,3, còn 2026 dư ~29,5 tỷ dưới trần, nên tâm có thể thấp hơn 5–11%. Theo chiều giảm còn có khoản dự phòng 333,5 tỷ chưa rõ bản chất, cùng việc trả ~356 tỷ nợ mâu thuẫn với giả định dự án 70% vay mà chưa được giải thích. Theo chiều tăng, lãi vay sẽ giảm và kịch bản tái cơ cấu TKV ở giá sổ sách chưa có trọng số. Các hạng mục ngành bắt buộc (trữ lượng, thời hạn giấy phép mỏ hiện tại, vốn cam kết dự án ~50% tâm) vẫn thiếu, nên chưa thể CONFIRMED."
}
<<<END_VERDICT>>>