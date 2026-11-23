Kết luận là **INCONCLUSIVE, độ tin cậy trung bình**. Mô hình rev4 tái lập được: chạy lại cho output trùng từng byte và md5 trong LOCK postfix khớp. Các số chịu lực lấy từ BCTC Q3/2026 cũng khớp. Tuy vậy, bước điều chỉnh lên lớn nhất (+1.956 đ) dựa trên một trọng số không có điều khoản nào làm căn cứ. Báo cáo cũng có một lỗi logic nhỏ và bỏ sót khoản 152 tỷ theo NQ 76.

**Tôi đã tự kiểm lại từ BCTC Q3/2026 (KQKD tr.4, BCĐKT tr.3, TM16–18 tr.23):**
- Các số khớp: LNST 9T 132,589; doanh thu tài chính 37,740; chi phí tài chính 4,326; doanh thu 449,388; vay 110,03 + 196,34; tiền 171,22; cổ tức phải trả 70,36; ký quỹ dài hạn 146,99; trích thuê đất 44,265; quỹ khen thưởng phúc lợi 23,96.
- Số cổ phiếu: BQ có OShares 27,90 tr ở 2026Q2 và 48,198884 tr ở 2026Q3, khớp với cổ tức cổ phiếu 70% (ghi ở khoản "vốn khác" 198,5 tỷ). EPS Q3 là 1.998, vẫn tính trên khoảng 31 tr cổ phiếu, nên đợt phát hành nhiều khả năng diễn ra sau 30/09. Rev4 không ghi ngày này ra.

**Chiều ĐẮT (tâm có thể đang quá cao):**
1. **Mục #4 "đối xứng" sửa sai hướng (+131 đ).** Doanh thu tài chính Q3 là 36,76 tỷ, chủ yếu là cổ tức SZC/SZB, thuộc diện miễn thuế. Kiểm chứng: thuế hiện hành Q3 8,46 ≈ (78,47 − 36,76) × 20%. Vì vậy loại phần này theo số gộp là đúng. Ngược lại, lãi vay được khấu trừ thuế, nên phải cộng lại theo số sau thuế (×0,8). Hệ số 0,8 của r3c mới là đúng.
2. **Khoản 151,99 tỷ "phải trả khác dài hạn" (NQ 76/2020) không được nhắc tới.** Đây là lợi nhuận giữ lại được phân bổ dần 5,846 tỷ/năm vào lãi, đến năm 2053. Phần này là lãi không ra tiền và nằm sẵn trong N0, nhưng trục "lãi phi tiền mặt" (cận trên 17%, chỉ tính từ doanh thu chờ phân bổ 762) không bao gồm nó. Ảnh hưởng ước lượng khoảng −690 đ (−2,5%).
3. **Ký quỹ khách thuê tính theo PV 27 năm với trọng số 0,75, đóng góp +1.956 đ (7,1% tâm).** Chính báo cáo ghi "không công bố điều khoản hoàn trả". Tức là chiều tăng không có căn cứ độc lập, đúng loại thiếu sót mà luật hai chiều của user cấm. Phần ký quỹ tăng thêm trong năm (135 → 147) đi cùng mảng nhà xưởng, vốn thường là hợp đồng ngắn hạn.
4. **Độ nhạy tiền thuê đất chỉ thử tới +50%.** Bảng giá đất mới theo Luật Đất đai 2024 có thể đẩy mức tăng vượt xa con số đó. Bản thân khoản trích bổ sung 44,3 tỷ cho thấy đã từng có lần định giá lại.

**Chiều RẺ (tâm có thể đang quá thấp):**
1. Báo cáo tự xác định tiền thuê đất 13,74 tỷ được ghi nhận một lần mỗi năm. Dù vậy, N0 base vẫn nhân 9T × 4/3, nên chi phí bị tính dư khoảng 3,7 tỷ/năm sau thuế. Sau khi bù phần NQ 76 cũng bị nhân 4/3, tác động ròng khoảng +240 đ.
2. Cho trọng số 0,25 vào kịch bản "khách rời đi hết" (tính ký quỹ theo mệnh giá) là thận trọng, trong khi số dư ký quỹ đang tăng.
3. GPM 9T theo BQ là 38,97%, còn theo BCTC là 38,03%. Tuy nhiên BQ cũng cao hơn BCTC khoảng 0,8 điểm % ở 2025Q3, nên khoảng chênh dùng để chuẩn hoá biên gần như không đổi.

Cộng các lệch định lượng được: khoảng −580 đ (−2%), dưới ngưỡng 5%, nên không bác bỏ. Chưa CONFIRMED vì: trọng số ký quỹ chiếm 7,1% tâm mà không có căn cứ; ý kiến kiểm toán FY2025 chưa có; dải độ nhạy tiền thuê đất có thể quá hẹp; tổng mức đầu tư Long Phước 920 và giấy phép đất 2053 đều chưa được đối chiếu.

<<<VERDICT_JSON>>>
{
  "case_topic": "SZL (Sonadezi Long Thành) — DD REPORT_rev4 23/11/2026, tâm 5 tỷ 27.397 / 40 tr 28.468, nhãn TRONG/TRONG",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo nêu rõ KHÔNG đủ điều kiện §2.5, không đưa ra luận điểm fear-buy",
    "scandal_migration_risk": "pass (yếu) — vụ khởi tố Trưởng BKS thuộc SNZ (công ty mẹ); báo cáo giữ WARNING cùng HARD ABANDON (a). Khoản truy thu thuế ~14 tỷ (≈290 đ, 1%) chưa rõ đã hạch toán hay chưa; tôi không tra lại pháp lý mới (giới hạn của phiên)",
    "optimistic_comp_sotp_bias": "fail (vừa phải) — SOTP không dùng comp, nhưng bước tăng lớn nhất (ký quỹ dài hạn PV 27 năm, trọng số 0,75, +1.956 = 7,1% tâm) không có căn cứ; báo cáo tự ghi 'không công bố điều khoản hoàn trả'. BĐS ĐT mới +1.707: số 166,887 có nguồn TM10, còn DC 78,7 và trọng số 0,25/0,5/0,25 đều là [UL]",
    "data_provenance": "pass có lỗi nhỏ — NP 9T 132,589, DT tài chính 37,740, CP tài chính 4,326, DT 449,388, vay, tiền, cổ tức phải trả 70,36, ký quỹ 146,99, trích thuê đất 44,265 đều khớp BCTC Q3 (KQKD tr.4, BCĐKT tr.3, TM16-17 tr.23). Lỗi: mục #4 cộng lại lãi vay theo số gộp, trong khi DT tài chính là cổ tức miễn thuế (thuế HH Q3 8,46 ≈ (78,47−36,76)×20%), nên CP tài chính phải ×0,8 như r3c (+131 sai chiều). GPM 9T theo BQ 38,97% vs BCTC 38,03% (BQ lệch tương tự trong quá khứ nên khoảng chênh gần như không đổi)",
    "liquidity_capacity_realism": "na — DD không đề xuất lệnh; CK thanh khoản giữ nguyên r3c",
    "confirmation_bias_flipflop": "pass (có lưu ý) — tâm +8,9% so với r3c, có thể truy về đúng 4 hạng mục skeptic r1 và control tái lập 25.165. Hai bước tăng (+1.707, +1.956) và một bước giảm (−1.562) đều dựa trên trọng số [UL]; chiều tăng của ký quỹ thiếu căn cứ tương đương với chiều giảm mà r1 đã chê. Không đọc dd_price_zones (ràng buộc mù)",
    "exit_discipline_gap": "na — không có claim sizing/fear-buy; mốc đổi nhận định hai chiều và HARD ABANDON a/b/c có nêu",
    "missing_items": "fail (dưới ngưỡng REFUTE) — (1) 151,99 tỷ 'phải trả khác DH' theo NQ 76/2020 (TM17): lãi giữ lại phân bổ 5,846 tỷ/năm đến 2053, là lãi phi tiền mặt nằm trong N0 nhưng không vào trục nc ⇒ ước lượng −690 đ (−2,5%); báo cáo không nhắc. (2) Tiền thuê đất 13,74 tỷ ghi một lần/năm nhưng N0 base vẫn ×4/3 ⇒ chi phí bị tính dư ⇒ +~240 đ ròng sau bù NQ 76; mâu thuẫn nội bộ. (3) Ý kiến kiểm toán FY2025 vắng (không định lượng được). (4) Đơn giá thuê đất mới theo Luật Đất đai 2024 chỉ thử tới +50% (−792); mức tăng gấp đôi (≈−1.584, 5,8%) chưa thử, không có nguồn. (5) Ngày phát hành cổ tức cổ phiếu 70% làm cơ sở 48,199 tr cp không ghi (EPS Q3 1.998 vẫn trên ~31 tr cp; BQ OShares đổi sang 48,2 tr ở kỳ 2026Q3). Đạt: quỹ KTPL 23,96 + K 11,2%, cổ tức phải trả 70,36 vào nợ, ký quỹ BLQ 0,23, cổ tức Q3 36,76 tỷ (khoản một lần trong năm gốc) đã loại, thu nhập khác nhỏ (1,19), capex NMXLNT đã đầu tư 116,3"
  },
  "independent_verification": "Đọc trực tiếp BCTC Q3/2026 (png q3_p06, q3_p08, q3_p27): NP 9T 132.589.359.502, DT tài chính 37.740.263.110, CP tài chính 4.326.469.728, DT 449.387.721.455 — khớp hằng số trong model_rev4.py. Thuế HH Q3 8,46 ≈ 20% × (LNTT − cổ tức) ⇒ DT tài chính là cổ tức miễn thuế ⇒ mục #4 rev4 sai. BQ ticker_financial: OShares 27,90 tr (2026Q2) → 48,198884 tr (2026Q3), khớp SH; GP BQ 9T 175,1 vs BCTC 170,9. Chạy lại model_rev4.py: output trùng byte với model_rev4_out.txt, md5 LOCK_rev4_postfix OK.",
  "killer_objection": "Bước +1.956 đ (7,1% tâm, lớn nhất trong rev4) đến từ việc đặt 0,75 trọng số vào giả định ký quỹ khách thuê chỉ hoàn trả vào 2053, trong khi báo cáo tự thừa nhận không có điều khoản nào được công bố. Phần ký quỹ tăng thêm trong năm gắn với nhà xưởng, vốn thường là hợp đồng ngắn hạn. Đây đúng là một bước tăng không có căn cứ độc lập; nếu bỏ đi thì tâm 5 tỷ về 25.441.",
  "recommended_followups": [
    "Đặt lại hệ số loại CP tài chính về ×0,8 (sau thuế), hoàn bước +131",
    "Đưa 5,846 tỷ/năm theo NQ 76 vào trục lãi phi tiền mặt (nc) và nêu khoản 151,99 tỷ trong báo cáo",
    "Sửa N0: bỏ ×4/3 cho các khoản ghi một lần/năm (thuế đất 13,74; NQ 76 5,846) cho nhất quán với mục post-fix",
    "Tìm hợp đồng thuê mẫu / thuyết minh BCTC kiểm toán 2025 về điều khoản hoàn trả ký quỹ; chưa có thì cân nhắc trọng số trung lập 0,5 mệnh giá / 0,5 PV",
    "Lấy BCTC kiểm toán 2025 (ý kiến kiểm toán) và thông báo đơn giá thuê đất Đồng Nai 2026; mở rộng độ nhạy tiền thuê đất lên ×2",
    "Ghi ngày chốt/phát hành cổ tức cổ phiếu 70% làm cơ sở số cổ phiếu 48,199 tr"
  ],
  "summary": "Rev4 tái lập được (output trùng byte, md5 OK) và các số BCTC chịu lực khớp BCTC Q3/2026 gốc. Các hạng mục skeptic r1 được xử lý minh bạch, có control tái lập r3c. Tuy vậy, tâm tăng +8,9% chủ yếu nhờ hai trục có trọng số [UL]; riêng trục ký quỹ PV 27 năm (+1.956, 7,1%) không có điều khoản nào làm căn cứ, đúng loại điều chỉnh một chiều mà luật hai chiều yêu cầu phải có bằng chứng. Lỗi nhỏ: mục #4 'đối xứng' sai vì DT tài chính là cổ tức miễn thuế còn lãi vay được khấu trừ (+131 sai chiều). Bỏ sót khoản 151,99 tỷ NQ 76 (lãi phi tiền mặt 5,85 tỷ/năm, khoảng −690 đ), và N0 vẫn ×4/3 các khoản ghi một lần/năm (khoảng +240 đ). Tổng các lệch định lượng được khoảng −2%, dưới ngưỡng 5% nên không REFUTED. Các mục mở chưa định lượng được (kiểm toán FY2025, đơn giá thuê đất mới, căn cứ ký quỹ) khiến chưa thể CONFIRMED. Nhãn TRONG nhiều khả năng giữ được, nhưng tâm 27.397 vẫn phụ thuộc vào trọng số chưa có căn cứ."
}
<<<END_VERDICT>>>