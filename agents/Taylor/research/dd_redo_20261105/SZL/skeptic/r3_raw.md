**Kết luận: REFUTED (bác bỏ), độ tin cậy trung bình-cao.** Tôi đọc trực tiếp các trang BCTC Q3/2026 trong `rev4/png/` và thấy hai lỗi dữ kiện, mỗi lỗi kéo tâm định giá theo một chiều. Lỗi thứ ba là cơ sở số cổ phiếu, trình bày sai so với chính BCTC. Theo luật attack 8, mục 1 đủ để bác bỏ: thiếu một khoản đo được và vượt 5% tâm.

**Đã khớp với BCTC (q3_p08, p24, p27):** LNST 9T 132,589 · DT tài chính 37,740 · CP tài chính 4,326 · doanh thu 449,39 · BĐS đầu tư tăng 166,887 · ký quỹ dài hạn 146,987 · khoản NQ 76 giảm từ 157,834 xuống 151,988. Tái tính N0_9M_RAW = (132,589 − 37,740 + 0,8 × 4,326) × 4/3 = 131,08, khớp. GPM 9T theo BCTC là 170,90 / 449,39 = 38,03%.

**Lỗi 1 — tâm quá CAO: quỹ khen thưởng phúc lợi trích 20%, không phải 11,215%.**
- Thuyết minh 21e (tr.26, q3_p30) trừ 13,979 tỷ quỹ KTPL trên LNST Q3 69,897 tỷ, tức đúng 20,0%.
- Cùng bảng đó, Q3/2025 chỉ trừ 3,839 / 34,232 = 11,2%, đúng mức mô hình đang dùng.
- Doanh nghiệp đã đổi tỷ lệ trích cho năm 2026; báo cáo không nhắc tới.
- Chạy lại mô hình với k = 20%: tâm cỡ 5 tỷ **24.164 (−1.688, −6,5%)**.

**Lỗi 2 — tâm quá THẤP: khoản NQ 76 không đi qua P&L.**
- Bảng biến động vốn chủ (tr.25, q3_p29) ghi 5,845686 tỷ vào dòng "Phân bổ lợi nhuận giữ lại để chia cổ tức năm 2026". Bút toán này ghi thẳng vào LNST chưa phân phối.
- Thu nhập khác cả 9T chỉ có 1,578 tỷ, nên khoản này không thể nằm trong N0.
- Mục r2-3 của rev4b trừ −708 là một điều chỉnh giảm không có cơ sở. Nó được thêm vào theo gợi ý của skeptic r2 mà không kiểm lại BCTC. Theo luật của user, điều chỉnh giảm cũng cần bằng chứng độc lập như điều chỉnh tăng.
- Bỏ khoản trừ này: tâm **26.559 (+708)**.

**Gộp cả hai lỗi:** tâm cỡ 5 tỷ **24.793** (−1.059, −4,1%), P10/P90 là 21.361 / 28.310; cỡ 40 tr là **25.762**.

**Lỗi 3 — số cổ phiếu 48,199 tr trình bày sai.**
- Tại 30/09, BCTC ghi 29.114.840 cp đăng ký và 28.352.340 cp đang lưu hành. Báo cáo nói phát hành "trong Q3"; BCTC cho thấy tại 30/09 chưa phát hành.
- Con số 48,199 tr đúng bằng 28,352 tr cộng 19,8465 tr cổ phiếu thưởng. Phần thưởng này mới hạch toán vào "vốn khác của chủ sở hữu" 198,465 tỷ, chưa đăng ký vốn.
- Mẫu số EPS mỗi chỗ một khác: thuyết minh EPS chia cho 27,985 tr, còn từ KQKD suy ra khoảng 34,98 tr.
- Tâm chỉ đúng theo cơ sở sau thưởng. So với bất kỳ mức giá nào trước ngày GDKHQ sẽ lệch 1,70 lần.

**Điểm nhỏ:**
- Trục g (2/3/4%) không có tác dụng: hàm `val()` không dùng `g`. Lưới n = 3.240 vì thế gồm toàn bộ kết cục lặp ba lần.
- Chi phí trả trước dài hạn gồm tiền thuê đất tại KCN Châu Đức 147,3 tỷ và Tân Đức 69,9 tỷ (q3_p24). Báo cáo không bàn khoản này đang sinh lời hay để không. Hai chiều, chưa định lượng được.
- Theo dữ liệu BQ `szl_cf_hist.csv`, lãi ròng 2019–2024 đi ngang quanh 100 tỷ/năm, trong khi chi đầu tư 140–314 tỷ/năm. Điều này làm yếu giả định capex duy trì = 1,0× khấu hao, mà đây là trục rộng nhất (±6.482).

Báo cáo có nêu giá 27.700; tôi bỏ qua khi đánh giá. Các nhãn TRONG/TRÊN do mô hình in ra cũng không được dùng. Không mở sổ vùng giá.

<<<VERDICT_JSON>>>
{
  "case_topic": "SZL (Sonadezi Long Thành) — DD REPORT_rev4b 23/11/2026",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo không tuyên bố đủ điều kiện fear-buy/§2.5 (tự ghi luật sổ KHÔNG đạt)",
    "scandal_migration_risk": "pass — WARNING khởi tố Trưởng BKS thuộc SNZ (công ty mẹ) và truy thu thuế ~14 tỷ (≈290 đ/cp, ~1%) được nêu; HARD ABANDON (a) phủ trường hợp lan sang pháp nhân SZL; không thấy tín hiệu lan sang trong các nguồn đã cite",
    "optimistic_comp_sotp_bias": "fail (hai chiều) — SOTP: (i) tỷ lệ KTPL 11,215% đã lỗi thời, BCTC Q3 tr.26 trích 20,0% (13,979/69,897) ⇒ tâm quá CAO 1.688; (ii) khoản NQ 76 bị trừ khỏi N0 dù ghi thẳng vào LNST chưa phân phối (bảng vốn chủ tr.25; thu nhập khác 9T chỉ 1,578) ⇒ tâm quá THẤP 708; trục g không có tác dụng trong val()",
    "data_provenance": "fail — 48,199 tr cp được nói là 'phát hành trong Q3', nhưng BCTC 30/09 ghi 29.114.840 đăng ký / 28.352.340 lưu hành; 48,199 = 28,352 + 19,8465 cp thưởng chưa đăng ký (vốn khác 198,465 tỷ). Mẫu số EPS mỗi chỗ một khác (27,985 tr ở thuyết minh vs ~34,98 tr suy từ KQKD). Các số còn lại khớp: NP 132,589, DT TC 37,740, CP TC 4,326, DT 449,39, BĐS ĐT +166,887, ký quỹ DH 146,987, NQ76 157,834→151,988",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất lệnh/sizing; CK thanh khoản chỉ để tham chiếu",
    "confirmation_bias_flipflop": "fail (nhẹ) — chuỗi tâm r3c 25.165 → rev4 27.397 → rev4b 25.852 có cầu nối minh bạch, nhưng khoản trừ NQ76 −708 được chấp nhận theo gợi ý skeptic r2 mà không kiểm bảng vốn chủ; điều chỉnh giảm không có bằng chứng, trái luật user 02/11–03/11",
    "exit_discipline_gap": "na — không đề xuất lệnh; mốc đổi nhận định hai chiều + HARD ABANDON (a)(b)(c) đã nêu",
    "missing_items": "fail — (1) tỷ lệ trích KTPL 2026 = 20% (BCTC Q3 tr.26) không có trong mô hình: −1.688 (−6,5% tâm), đo được, trọng yếu; (2) ý kiến kiểm toán FY2025 vẫn vắng (soát xét H1/2026 RSM chấp nhận toàn phần); (3) chi phí trả trước thuê đất Châu Đức 147,3 + Tân Đức 69,9 tỷ không được bàn (đang sinh lời hay để không? hai chiều, chưa định lượng); (4) tổng mức Long Phước 920 chỉ từ báo chí; (5) ngày GDKHQ cổ phiếu thưởng chưa kiểm chứng. Đã đạt: capex môi trường (NMXLNT GĐ4 đã đầu tư), khoản trích 44,265, nợ quỹ KTPL 23,96, mốc 2053"
  },
  "independent_verification": "Đọc trực tiếp ảnh trang BCTC Q3/2026: KQKD (q3_p08) khớp NP 132,589 / DT TC 37,740 / CP TC 4,326 / DT 449,39; TM10-11 (q3_p24) khớp BĐS ĐT +166,887; TM17 (q3_p27) khớp ký quỹ 146,987 và NQ76 5,845686/năm. Tái tính N0_9M_RAW = 131,08 khớp. KHÔNG khớp: NQ76 đi qua vốn chủ, không qua P&L (q3_p29); KTPL Q3/2026 = 20,0% (q3_p30); cp lưu hành 30/09 = 28,352 tr, không phải 48,199. Chạy lại mô hình: k=20% ⇒ tâm 5 tỷ 24.164; bỏ khoản trừ NQ76 ⇒ 26.559; gộp cả hai ⇒ 24.793 (40 tr: 25.762).",
  "killer_objection": "Tỷ lệ trích quỹ KTPL năm 2026 là 20% theo chính thuyết minh EPS Q3/2026 (13,979/69,897), không phải 11,215% như mô hình. Khoản thiếu này kéo tâm xuống 1.688 (−6,5%), vượt ngưỡng trọng yếu 5%.",
  "recommended_followups": [
    "Thay k = 20% (hoặc dựng trục 11,2%/20% kèm NQ ĐHĐCĐ 2026 về phân phối lợi nhuận) — nguồn: thuyết minh 21e BCTC Q3/2026",
    "Gỡ khoản trừ NQ76 khỏi N0 (ghi thẳng vào LNST chưa phân phối, bảng vốn chủ tr.25) và bỏ độ nhạy 'NQ76 không chịu thuế'",
    "Ghi đúng cơ sở cổ phiếu: 28.352.340 lưu hành + 19.846.500 thưởng chờ đăng ký (vốn khác 198,465 tỷ); xác minh ngày GDKHQ trước khi so tâm với bất kỳ mức giá nào",
    "Bỏ hoặc nối lại trục g (val() không dùng g)",
    "Làm rõ chi phí trả trước thuê đất Châu Đức/Tân Đức 217 tỷ: tài sản đang sinh lời hay quỹ đất chờ khai thác",
    "Kéo BCTC kiểm toán FY2025 để đóng mục ý kiến kiểm toán"
  ],
  "summary": "Hầu hết số liệu tải trọng khớp BCTC Q3/2026, nhưng mô hình có hai lỗi dữ kiện ngược chiều, đều kiểm được ngay trên BCTC. Một: tỷ lệ trích quỹ KTPL năm 2026 đã lên 20% (thuyết minh EPS Q3) trong khi mô hình vẫn dùng 11,215%; tâm quá cao 1.688 (−6,5%), đo được và trọng yếu nên bác bỏ theo luật attack 8. Hai: khoản NQ 76 5,846 tỷ/năm được phân bổ thẳng vào LNST chưa phân phối, không qua P&L, nên khoản trừ −708 thêm theo gợi ý skeptic r2 là sai; tâm quá thấp 708. Gộp lại tâm cỡ 5 tỷ khoảng 24.793 thay vì 25.852 (cỡ 40 tr khoảng 25.762). Ngoài ra, 48,199 tr cổ phiếu gồm 19,85 tr cổ phiếu thưởng chưa đăng ký tại 30/09, chứ không phải 'đã phát hành trong Q3'. Tâm chỉ đúng theo cơ sở sau thưởng. Trục g không có tác dụng, và giả định capex duy trì = 1× khấu hao (trục rộng nhất) vẫn chưa có bằng chứng."
}
<<<END_VERDICT>>>