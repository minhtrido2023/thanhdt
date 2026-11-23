**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phần số học và nguồn của rev4 đúng. Nhưng còn hai hạng mục vắng mặt có thể trọng yếu mà chưa định lượng được, mỗi cái đẩy tâm về một chiều. Ngoài ra, mốc "giữa chu kỳ" vẫn neo vào năm cao nhất lịch sử. Tôi bỏ qua mọi giá thị trường ở §8 và không mở sổ vùng giá.

**Đã tự kiểm lại (khớp):**
- Lấy LNST theo quý trong BQ `ticker_financial` cộng lại: FY25 = 58,5+79,2+63,1+100,7 = **301,5 tỷ**, khớp 301,437 [KT25]. FY24 = **218,0 tỷ**, khớp với lõi 212,1 sau khi trừ DTTC.
- Tiền 30/9/2026: BQ **27,6** khớp 27,576.
- Tự tính lại: lõi FY25 (376,993−30,655−15,031)×0,8 = 265,05 ✓; số CP 46,9216−0,20104 = 46,72056 ✓; phần net cash trừ ngay 607,44 ✓.

**Điểm yếu theo chiều ĐẮT (tâm quá cao):**
1. **Neo giữa chu kỳ = FY25, năm cao nhất từng có trước TTM.**
   - Theo BQ, LNST 2017–2024 nằm trong khoảng ~140–218 tỷ/năm (2022 lỗ do truy thu).
   - Đường cơ sở không bao giờ xuống dưới 265 và tăng lên ~303 ở năm 6.
   - Kịch bản xấu đặt 250 phẳng, vẫn cao hơn mọi năm trước 2025.
   - Bằng chứng độc lập cho chiều xuống: lịch sử đã kiểm toán; KH 2026 sản lượng 6,8 tr m³, thấp hơn 7,59 đã bán năm 2025; BVSC dự báo cầu giảm sau Long Thành GĐ1.
   - Nếu neo giữa FY24 và FY25 và cho kịch bản xấu = lõi FY24: tôi ước tâm khoảng **−5 đến −6%**.
2. **Vốn lưu động hoãn đến khi đóng mỏ (+4,0%) là đổi quy ước, không phải thông tin mới.**
   - Số dư 144 tỷ gồm 54,2 tỷ phải trả người lao động, nhiều khả năng mang tính mùa vụ (chi Tết). Số này không phải khoản quay vòng thường trực.
   - Tiền khách ứng trước đang ở mức đỉnh chu kỳ.
   - Mô hình cho LN giảm 26% nhưng không giải phóng phần vốn lưu động tương ứng. Ước lệch cao khoảng 1–2%.
3. **Kịch bản tốt gia hạn 3 mỏ chính không tính chi phí:** không có tiền cấp quyền mới cho ~14,7 tr m³ trữ lượng thêm, không có đền bù đất.
4. **Khoản bù trừ chiết khấu ở 7,4% (lãi huy động)** dù đã có tiền lệ đảo chiều năm 2022. Chiết khấu ở 13,5% thì tâm −1,5%.

**Điểm yếu theo chiều RẺ (tâm quá thấp):**
1. **Năm 1 bắt đầu từ TTM 357,4, thấp hơn tốc độ hiện tại.** Q3/26 LNST 117,4 tỷ, doanh thu +35% so với cùng kỳ; nhân 4 và trừ DTTC thì lõi ≈ 440. Ước tâm cơ sở bị thấp khoảng +3%.
2. **Hạng mục vắng: khấu hao không được cộng lại.**
   - Mô hình lấy dòng tiền = LNST × (1−quỹ), không cộng khấu hao.
   - CP trả trước dài hạn 286,75 tỷ là tiền đền bù đất ĐÃ TRẢ, đang phân bổ dần (~20 tỷ/năm, không tốn tiền mặt). Capex theo BQ những năm gần đây chỉ khoảng 1–16 tỷ/năm.
   - Báo cáo không nêu số khấu hao. Ước tâm bị thấp khoảng +3–5%, chưa định lượng được.

**Hạng mục vắng chiều xuống:** BCTN p36 ghi đền bù phần diện tích còn lại "gặp khó", cộng thêm thủ tục huy động 44,3 ha ở TC1. Báo cáo xếp vào V4/WARNING với NPV = 0. Nhưng nếu phần đất này cần để khai thác trữ lượng cơ sở thì đây là dòng tiền ra bắt buộc, không phải tăng trưởng. Ước tính thô, chưa kiểm chứng: 90–130 tỷ, tức khoảng 4–6% tâm.

<<<VERDICT_JSON>>>
{
  "case_topic": "VLB — DD rev4 (23/11/2026), tâm 45.161 đ/cp ex-div sau CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không tuyên bố QUALIFY fear-buy (§8 tự ghi không đủ điều kiện sleeve)",
    "scandal_migration_risk": "pass — các mục pháp lý (tiền cấp quyền đảo chiều 2022↔2026, rà soát GP Soklu, đất theo Kiểm toán NN) đều được nêu ở §10; truy thu kiểu 2022 là STRESS ngoài mô hình (−4.623 đ/cp) + HARD ABANDON; SK2/SK5 đã có GP mới 28/02/2025 [BCTN p8]. Không thấy tín hiệu lan sang 3 mỏ chính trong tài liệu đã cung cấp",
    "optimistic_comp_sotp_bias": "fail (vừa phải, hai chiều) — không dùng comp, nhưng 'giữa chu kỳ' neo vào lõi FY25 265 = năm kiểm toán cao nhất; BQ: LNST 2017–2024 ~140–218/năm; kịch bản xấu 250 phẳng vẫn cao hơn mọi năm trước 2025. Mid = trung bình FY24/FY25 và xấu = lõi FY24 ⇒ ước ≈ −5–6% tâm. Chiều ngược lại: năm 1 lấy TTM 357 trong khi tốc độ Q3/26 (LNST 117,4; DT +35% cùng kỳ) ⇒ lõi ≈ 440 ⇒ ước ≈ +3% cơ sở. Khoản bù trừ chiết khấu 7,4% dù có tiền lệ đảo chiều (−1,5% nếu 13,5%)",
    "data_provenance": "pass với caveat — đối chiếu BQ ticker_financial: NP FY25 301,5 (BC 301,437), FY24 218,0, tiền 30/9 27,6 (BC 27,576); số học lõi FY25 265,05, số CP 46,72056, net cash trừ ngay 607,44 khớp. Caveat: BCTC KT 2025 là bản scan, chỉ đọc vài trang; op 9T/25 là ước lượng; fund_accrued_9t = 565,97 − 11,345×46,72 là phép tính ngược, ý nghĩa không giải thích; tỷ trọng LN theo sản lượng (không có biên LN từng mỏ)",
    "liquidity_capacity_realism": "na — không đề xuất vào lệnh; có CK thanh khoản (5 tỷ ≈ 22 phiên ở 20% ADV)",
    "confirmation_bias_flipflop": "pass với ghi chú — rev3→rev4 +5,5%: +3,5% từ nguồn sơ cấp mới (BCTN p8, có số GP) là thông tin mới; −3,0% fade LN là sửa đúng hướng; +4,0% là ĐỔI QUY ƯỚC VLĐ (không phải thông tin mới, dù skeptic r2 đã nêu) và số dư VLĐ 144 tỷ gồm 54,2 tỷ phải trả NLĐ có vẻ mùa vụ + ứng trước ở mức đỉnh, không thu hẹp khi LN fade 26% ⇒ ước lệch cao ~1–2%. Không mở dd_price_zones.json theo ràng buộc của brief; so với rev3 REPORT",
    "exit_discipline_gap": "na — không có sizing/QUALIFY; vẫn có mốc khoá M1–M5 và điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (chưa định lượng được, hai chiều) — (1) KHẤU HAO/PHÂN BỔ không cộng lại: dòng tiền = LNST×(1−quỹ), trong khi CP trả trước DH 286,75 tỷ (đền bù đất đã trả, đang phân bổ ~20 tỷ/năm, không tốn tiền) + khấu hao TSCĐ so với capex BQ những năm gần đây ~1–16 tỷ/năm ⇒ ước +3–5% tâm, báo cáo không nêu số khấu hao. (2) ĐỀN BÙ phần diện tích còn lại (BCTN p36 'gặp khó') + huy động 44,3 ha TC1 (BCTN p41) được xếp vào V4 NPV=0/WARNING; nếu cần để khai thác trữ lượng cơ sở thì là dòng tiền ra bắt buộc — ước thô 90–130 tỷ ≈ −4–6% tâm, chưa có số. (3) Kịch bản tốt gia hạn không tính tiền cấp quyền mới/đền bù cho ~14,7 tr m³ thêm (lệch cao trong kịch bản tốt). Đạt: BCTC KT FY25 chấp nhận toàn phần; số CP + CP quỹ + không ESOP; quỹ KTPL 14,84%; thuế 20% (thuế trên 343,93 nộp bằng tiền theo notes_raw); bên liên quan = 0; một lần 343,93 đã loại; NQ HĐQT 12 tháng không có cam kết vốn; hạn GP/trữ lượng có số GP; ký quỹ hoàn nguyên có tính"
  },
  "independent_verification": "BQ tav2_bq.ticker_financial VLB: tổng NP_P0 4 quý FY25 = 301,5 tỷ (BC 301,437 ✓), FY24 = 218,0; Cash_P0 2026Q3 = 27,6 (BC 27,576 ✓); NP 2017–2024 ≤ 218/năm (xác nhận neo giữa chu kỳ = mức cao nhất lịch sử); Q3/26 NP 117,4 / DT 442,1 (tốc độ hiện tại cao hơn TTM). Tự tính lại lõi FY25 265,05, FY24 212,07, số CP 46,72056, net cash 607,44 — khớp.",
  "killer_objection": "Đường LN cơ sở coi FY25 (lõi 265, năm kiểm toán cao nhất; LNST 2017–2024 ≤218) là 'giữa chu kỳ' vĩnh viễn và tăng 2%/năm, trong khi chính công ty lên KH 2026 sản lượng 6,8 tr m³ < 7,59 đã bán năm 2025. Một phần lệch được bù bởi việc năm 1 dùng TTM thấp hơn tốc độ Q3/26 và khấu hao không được cộng lại, nhưng không hạng mục nào trong số này được định lượng trong báo cáo — nên tâm 45.161 có dải sai số thật vào khoảng ±6%, chưa đến mức ±1–2% như các độ nhạy được báo.",
  "recommended_followups": [
    "Trích khấu hao TSCĐ + phân bổ CP trả trước DH (đền bù đất) từ LCTT BCTC KT 2025 / Q3/26; mô hình FCF = LNST + D&A − capex duy trì thay cho LNST",
    "Đọc thuyết minh BCTN p36/p41 + CP trả trước DH [Q3 p18]: diện tích đền bù còn lại nằm TRONG ranh GP (cần cho trữ lượng cơ sở) hay mở rộng; ước số tiền theo đơn giá đền bù đã trả (271,5 tỷ / số ha)",
    "Thêm độ nhạy neo giữa chu kỳ = trung bình lõi FY21–FY25 (bỏ 2022 hoặc chuẩn hoá) và kịch bản xấu = lõi FY24 212",
    "Bóc 54,2 tỷ phải trả NLĐ: phần thưởng/lương tháng 13 trích trước (chi trong 6 tháng) phải trừ ngay, không hoãn đến khi đóng mỏ; cho số dư VLĐ co theo đường LN",
    "Kịch bản tốt: trừ tiền cấp quyền mới + đền bù cho phần trữ lượng gia hạn",
    "Năm 1: đối chiếu TTM với tốc độ Q3/26 (lõi ≈ 440 nhân 4) — xét mùa vụ trước khi chọn mức xuất phát"
  ],
  "summary": "Rev4 đã xử lý đúng các mục thiếu của skeptic r2 (BCTC kiểm toán FY25 chấp nhận toàn phần, số GP và hạn GP từ BCTN, NQ HĐQT 12 tháng), và mọi con số kiểm lại được đều khớp BQ và phép tính. Nhưng mô hình vẫn lệch theo cả hai chiều chưa định lượng: chiều đắt — neo giữa chu kỳ vào năm cao nhất lịch sử, kịch bản xấu vẫn trên mọi năm trước 2025, VLĐ mùa vụ được coi là quay vòng đến khi đóng mỏ (đây là đổi quy ước +4%, không phải thông tin mới), và kịch bản gia hạn không tính phí; chiều rẻ — năm 1 thấp hơn tốc độ Q3/26 và khấu hao/phân bổ tiền đền bù đã trả (286,75 tỷ) không được cộng lại vào dòng tiền. Hạng mục thiếu: đền bù phần diện tích còn lại/44,3 ha TC1 (có thể −4–6%) và khấu hao (có thể +3–5%) — đều trọng yếu nhưng chưa có số, nên kết luận INCONCLUSIVE chứ không phải REFUTED hay CONFIRMED."
}
<<<END_VERDICT>>>