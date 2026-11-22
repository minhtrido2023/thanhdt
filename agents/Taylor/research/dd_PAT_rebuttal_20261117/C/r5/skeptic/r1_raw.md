**Kết luận: REFUTED (độ tin cậy trung bình).** Con số tâm 66.470 (sau chiết khấu 59.823, cổng 50.850) dựa trên bước +4.800 "đọc H1/26 là quan sát sạch". Bước này mâu thuẫn với chính tài liệu của fleet. Gỡ nó đi thì tâm về **62.578 / sau chiết khấu 56.320 / cổng ≈47.870**, tức −5,9%, vượt ngưỡng 5%. Ngoài ra còn hai khoản thiếu lớn chưa định lượng được, một khoản kéo tâm xuống và một khoản có thể kéo lên.

Báo cáo có nhắc giá tham chiếu 70.200. Tôi bỏ qua con số này khi chấm mô hình.

## Kiểm độc lập (khớp)
- **Tiền ròng 415,407.** Lấy từ BCĐKT 30/09/26 (`facts_extracted.md:20-24`): tiền 1,246 + HTM 558,07 − vay 67,22 − quỹ khen thưởng phúc lợi 76,69 = **415,406** ✓. Phần trừ 12,94 bằng 6% × LNCPP 215,71 = 12,94 ✓. Số cổ phiếu 25 triệu lấy từ BCTC Q3 ✓.
- **"UHY ngoại trừ tồn kho 67,7 tỷ"**, báo cáo ghi là "theo dispatch". Điều này **đúng** theo nguyên văn BCKT 749/2026/UHY-BCKT (F2 §4).

## Chiều ĐẮT (tâm quá cao)
1. **Mục 3 (+4.800) mâu thuẫn tài liệu của chính fleet.** `assumptions_objective_r3.md:33` (#N9) ghi Q1/26 "có một phần quặng tự khai thác tới ~17/03". Chính #R6 của r5 cũng ghi KT25 dừng "chậm nhất 17/03, có nguồn ghi từ cuối 2025". Vậy H1/26 có lẫn quặng của nguồn A, không phải ô (A tắt, B bật) thuần. Mức GĐ1/O2 (48,64%) gần mức 2025 khi A còn chạy (46,60%), nên mức này nghiêng về lạc quan. Lý do "tồn kho 30/06 bình thường" dùng tồn kho của **PAT**, trong khi kho quặng nằm ở **DLC**, nơi PAT mua NVL. Tồn kho của PAT không cho biết DLC có đốt kho quặng rẻ hay không.
2. **Tiêu chuẩn bất đối xứng.** Tồn kho bị gỡ (−1.538) với lý do "đọc lại dữ liệu có từ 14/11, không có bằng chứng mới". Ô O2 được đưa vào (+4.800) với đúng điều kiện đó (#R4/#R6/#R7 đều có từ 14/11). Theo luật của user (02/11, 03/11), áp nhất quán thì phải gỡ cả hai, ra 62.578.
3. **Thiếu khoản môi trường bắt buộc (kiểu QTP).** PAT sinh khoảng 137 nghìn tấn xỉ/năm (kế hoạch 2025, F2:86). Vụ án nêu "đổ thải trái phép hàng triệu tấn tại KCN Tằng Loỏng", là nơi đặt nhà máy PAT. Chủ tịch PAT bị khởi tố tội gây ô nhiễm môi trường. Mô hình đặt capex = khấu hao 45 và không có capex tuân thủ hay chi phí xử lý xỉ. Chỉ có độ nhạy "một lần −50" (khoảng −3%).
4. **Thời hạn thuê đất nằm trong tầm dự báo.** Chi phí GPMB đất thuê phân bổ trong 16 năm, tức đến khoảng 2042, còn mô hình dùng chuỗi 2027–2045 cộng Gordon. Nghĩa vụ hoàn nguyên đất thuê là nợ tiềm tàng không trích lập. Phần giá trị sau năm 16 bằng (1,02/1,135)^16 ≈ 18% giá trị hoạt động, khoảng 9.400 đ/cp. Hạn thuê thật chưa được kiểm.
5. **Cầm cố.** 439/551,6 tỷ HTM (79,6%) đang bị cầm cố. ACB nhận 130 tỷ cầm cố nhưng không có dư nợ ACB trong TM15. Tại 30/06, khoản 249 tỷ BIDV ghi bảo đảm cho "các đơn vị trong cùng Tập đoàn". Độ nhạy −42,6 có thể chưa đủ lớn.

## Chiều RẺ (tâm quá thấp)
- **Tồn kho dư 44,4 tỷ** (khoảng 1.778 đ/cp) là tài sản thật trên BCĐKT 30/09. Bỏ hẳn nó là thận trọng nhưng không có căn cứ bằng chứng.
- **Vốn lưu động tại 30/09 đang cao.** Tính gần đúng: phải thu + tồn kho − phải trả ≈ 87 tỷ, so với khoảng −25 tỷ tại 31/12/25. Giả định ΔVLĐ = 0 khoá tiền ròng ở mức thấp. Nếu vốn lưu động trở lại mức cuối 2025 thì tâm có thể thêm tối đa khoảng 4.500 đ/cp. Báo cáo không xác định được "mức bình thường" nên đây là bất định hai chiều, không định lượng được.

## Truy nguồn
GTGD, số dư 39,4 và chênh giá chuyển giao "+1% so +19,5%" đều "theo dispatch, chưa tự đo". Các số này không gánh tâm trước chiết khấu nhưng gánh tỷ lệ chiết khấu 10% và WARNING.

<<<VERDICT_JSON>>>
{
  "case_topic": "PAT — VALUATION_r5 (tâm 66.470 trước CK / 59.823 sau CK / cổng 50.850)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không tuyên bố QUALIFY §2/§2.5; tự ghi PAT trượt §2 trụ #2",
    "scandal_migration_risk": "fail (một phần) — GĐ và KTT của chính PAT bị khởi tố theo Điều 221 (kế toán, 'che giấu doanh thu'); Chủ tịch PAT bị khởi tố tội ô nhiễm môi trường; UHY ngoại trừ cả BCKT 2025 lẫn soát xét H1/26 vì không đánh giá được nghĩa vụ phải trả/dự phòng. Tức rủi ro đã chạm sổ sách và nghĩa vụ của pháp nhân PAT, nhưng trong base chỉ có độ nhạy 'một lần −50'. Báo cáo có nêu WARNING nên không im lặng, nhưng khoản truy thu thuế/phạt/xử lý thải chưa định lượng",
    "optimistic_comp_sotp_bias": "na — không dùng comp/SOTP; cây DCF. Lưu ý độ nhạy giá ±5% ⇒ ±24.700 (≈37%): tâm cực nhạy với E[p]",
    "data_provenance": "pass có điều kiện — tiền ròng 415,407 và quỹ KTPL tự kiểm khớp; UHY ngoại trừ tồn kho 67,7 tỷ khớp nguyên văn BCKT 749/2026. Còn treo: GTGD 1,01/0,60 tỷ, dư 39,4, giá chuyển giao +1%/+19,5% đều 'theo dispatch, chưa tự đo'",
    "liquidity_capacity_realism": "na — không có đề xuất sizing ngoài ghi chú ≤0,5% NAV; chiết khấu 10% dựa trên ADV chưa tự đo",
    "confirmation_bias_flipflop": "fail — giải phóng tồn kho đổi qua lại r2 bỏ → r4 thêm → r5 bỏ; ánh xạ ô (A tắt, B bật) 50/50 → O2; mọi thay đổi r4→r5 đều là đọc lại thông tin có từ 14/11 (báo cáo tự nhận, #R11). Tiêu chuẩn 'không có bằng chứng mới ⇒ không đổi' được áp để gỡ tồn kho (−1.538) nhưng KHÔNG áp cho ô O2 (+4.800). Áp nhất quán ⇒ 62.578. Chỉ đọc dòng của chính PAT trong thư mục rebuttal; không mở dd_price_zones.json theo ràng buộc mù",
    "exit_discipline_gap": "na — không đề xuất mua; ledger_notes có HARD ABANDON §3 #4 và các mốc theo dõi",
    "missing_items": "fail — (1) capex tuân thủ môi trường / xử lý ~137kt xỉ/năm và nghĩa vụ đổ thải KCN Tằng Loỏng: vắng mặt, capex = khấu hao 45, không định lượng được, có thể trọng yếu; (2) hạn thuê đất: GPMB phân bổ 16 năm (~2042) + hoàn nguyên đất thuê không trích lập, trong khi mô hình kéo tới 2045 + Gordon; phần giá trị sau năm 16 ≈18% giá trị hoạt động (~9.400 đ/cp) nếu không gia hạn, chưa kiểm; (3) 79,6% HTM bị cầm cố, ACB 130 tỷ cầm cố mà không có dư nợ ACB, 30/06 có 249 tỷ BIDV cho 'các đơn vị trong cùng Tập đoàn': độ nhạy −42,6 có thể thiếu; (4) chiều lên: VLĐ 30/09 cao hơn 31/12/25 khoảng 110 tỷ, giả định ΔVLĐ = 0 có thể làm tâm thấp tới ~4.500 đ/cp. Đạt: số cổ phiếu 25 triệu (BCTC Q3), quỹ phúc lợi (76,69 + 12,94 + FCFE×0,94), ý kiến kiểm toán FY2025 có mặt, bên liên quan (nút T)"
  },
  "independent_verification": "Tiền ròng: tiền 1,246 + HTM 558,07 − vay NH 67,22 − quỹ KTPL 76,69 = 415,406 so với 415,407 của mô hình — KHỚP. Trích quỹ 9T: 6% × 215,71 = 12,94 — KHỚP. Ngoại trừ tồn kho 67,7 tỷ của UHY (BCKT 749/2026, kt25/p06) — KHỚP. Tính lại ảnh hưởng trên tâm: gỡ bước O2 ⇒ 62.578 (−5,85%) theo bảng độ nhạy của chính báo cáo.",
  "killer_objection": "Bước +4.800 (ô (A tắt, B bật) → O2) dựa trên giả định H1/26 là quan sát 'sạch' của chế độ không có mỏ DGC. Nhưng tài liệu r3 của fleet (#N9) và chính #R6 của r5 ghi Q1/26 vẫn có quặng tự khai thác đến ~17/03. Bằng chứng 'không có kho quặng rẻ' lại dùng tồn kho của PAT, trong khi kho quặng nằm ở DLC. Không có bằng chứng mới nào sau 14/11, và cùng tiêu chuẩn đó đã được dùng để gỡ tồn kho. Áp nhất quán thì tâm là 62.578 / 56.320 / cổng ~47.870.",
  "recommended_followups": [
    "Đưa base về ánh xạ D (62.578 trước CK) hoặc đưa ra bằng chứng MỚI tách được quặng A khỏi H1/26 (sản lượng tấn hoặc cơ cấu nguồn quặng Q1 vs Q2/26 của DLC)",
    "Áp MỘT tiêu chuẩn bằng chứng cho cả tồn kho và ô O2: hoặc cả hai vào base, hoặc cả hai ra",
    "Truy hợp đồng thuê đất KCN Tằng Loỏng của PAT (hạn thuê, điều khoản hoàn nguyên); nếu hết hạn trước 2045 thì cắt giá trị cuối hoặc thêm chi phí gia hạn",
    "Định lượng capex/chi phí xử lý xỉ phốt pho bắt buộc và mọi chi phí khắc phục đổ thải KCN Tằng Loỏng thuộc phần của PAT; tách capex tuân thủ khỏi capex = khấu hao",
    "Đối chiếu cầm cố ACB 130 tỷ khi không có dư nợ ACB, và wording 249 tỷ BIDV 'đơn vị trong Tập đoàn' tại 30/06 so với 30/09",
    "Tự đo lại trên BQ: ADV 64 phiên (cho chiết khấu 10%), dư tồn kho 7 quý 39,4",
    "Chạy độ nhạy VLĐ về mức 31/12/25 và mức trung bình nhiều quý (chiều lên)"
  ],
  "summary": "Phần cơ học của mô hình r5 sạch: tiền ròng, quỹ phúc lợi, số cổ phiếu và ý kiến ngoại trừ của UHY đều truy được về BCTC và khớp khi tự tính lại; self-check cây vs đường độc lập đạt. Nhưng con số tâm 66.470 không đứng vững. Bước lớn nhất (+4.800, ô O2) là đọc lại thông tin cũ và mâu thuẫn với ghi chú của chính fleet: Q1/26 còn quặng tự khai thác đến ~17/03, và kho quặng nằm ở DLC chứ không phải PAT. Trong khi đó cùng tiêu chuẩn 'không có bằng chứng mới' lại được dùng để gỡ tồn kho theo chiều xuống. Áp nhất quán thì tâm là 62.578 trước / 56.320 sau chiết khấu (−5,9%). Theo mục thiếu, mô hình chưa có capex tuân thủ môi trường cho xỉ P4 dù có cáo buộc đổ thải tại chính KCN của PAT. Thời hạn thuê đất có dấu hiệu kết thúc khoảng 2042, nằm trong tầm dự báo (tới ~18% giá trị hoạt động). Mức cầm cố tiền gửi lớn hơn độ nhạy đang dùng. Ở chiều ngược lại, tồn kho dư 44 tỷ và vốn lưu động cao tại 30/09 có thể làm tâm bị thấp tới vài nghìn đồng. Kết luận 'không có biên an toàn' không bị lật, nhưng tâm và cổng phải hạ hoặc phải có bằng chứng mới cho ô O2."
}
<<<END_VERDICT>>>