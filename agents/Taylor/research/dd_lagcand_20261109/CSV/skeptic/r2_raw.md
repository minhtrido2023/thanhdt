**Verdict: INCONCLUSIVE, medium confidence.** The r3 rebuild fixes the r2 double-count correctly, and the numbers I checked match. But the model leaves out two items of about ±5–6% each, pointing in opposite directions. Separately, the load-bearing replacement share φ (how much of the 1,844 bn Nhơn Trạch capex only replaces the old BH1 capacity) and the acid-shock (TOT) scenario cannot be verified from the filings.

**What I re-checked independently**
- **Profit history:** BQ `ticker_financial` parent net profit 2019–2025 is 244.02 / 179.66 / 208.93 / 353.21 / 209.18 / 240.78 / 208.95 bn. This matches the report exactly.
- **CO_SO value:** I recomputed it by hand, without using `model_r3.py`. At central parameters (φ 0.65, t 1.75, r 13.5%) it is **11,206 đ/cp**, the same as the report. The PV of the remaining replacement capex is 779.9 bn.
- **TB2 halt:** the company's own disclosure 1123/CBTT-HCCB (31/07/2026) confirms that Resolution 1122 stops production at the Tân Bình 2 plant. TB2 is the H2SO4 plant.

**Pushes the centre too HIGH**
1. **The TOT scenario has an internal conflict.** It is the trailing-12-month profit of 294.5 bn, which the report itself attributes to H2SO4 at +249%/+289%. That plant stopped after 15/08/2026, and where the company now gets its acid is still open (G6). If TOT is replaced by CO_SO, the centre falls by about **8–9%** (my estimate: 0.25 × (15,099 − 11,206)). Q3 rose even with 6 weeks of halt, so this is not proven either way. The Q4/26 results are the test.
2. **The remaining capex is discounted at the cost of equity (13.5%).** About 1,212 bn of the project is borrowed, so this is a contracted, fixed outflow. Discounting at a debt rate of about 8% (my assumption) changes the centre by **−641 đ/cp (−5.8%)**.
3. **BH1 demolition and site cleanup cost is absent.** The site is an old chemical plant. The cost is not in the model and cannot be quantified.

**Pushes the centre too LOW**
1. **The tax shield from new depreciation is missing.** The φ part of the plant will be depreciated (the old plant's net book value is only 37 bn). At a 20-year life and 20% tax this is worth about **+593 đ/cp (+5.4%)** (my estimate). A shorter life makes it larger.
2. **φ is counted in tonnes, not capex.** Chlor-alkali electrolysis usually costs far more per tonne than an H2SO4 line. The caustic soda benchmark gives φ ≈ 0.5, so a capex-weighted φ is probably below 0.65. Each −0.1 of φ adds 1,406 đ/cp.
3. **The 0.80 upper anchor is weak.** It uses 2021 output in commercial tonnes against a new design capacity stated as 100%-equivalent, so the real ratio is probably lower.

Items 2 (debt-rate discounting) and 1 (tax shield) roughly cancel. φ dominates everything else, and its range (0.5/0.65/0.8 with weights 0.25/0.5/0.25) is the report's own estimate built from press articles.

**Following the price-blind rule:** I ignored every market price, P/E and "above the zone" label in the report and did not open the price-zone ledger.

<<<VERDICT_JSON>>>
{
  "case_topic": "CSV (Hoá chất Cơ bản Miền Nam) — DD r3, tâm 11.041 đ/cp sau CK 5 tỷ",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không có claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — cưỡng chế BH1 (QĐ 2408) và dừng TB2 (QĐ 1122, tôi đọc CBTT 1123 ngày 31/07/2026) là thi hành đề án chuyển đổi KCN, không phải xử phạt pháp nhân; hệ quả kinh tế đã nằm trong base qua D3; đất HCM là đất thuê tự nguyện trả lại (TB 610). Không thấy dấu hiệu tịch thu tài sản lõi",
    "optimistic_comp_sotp_bias": "fail (hai chiều, không quyết định) — không dùng comp; mô hình capex có hai thiếu sót ngược chiều: (−) capex còn chi phần lớn vay nợ 1.212 tỷ nhưng chiết khấu ở Ke 13,5%, ở 8% thì −641 đ/cp; (+) thiếu lá chắn thuế khấu hao nhà máy mới, φ×1.844/20 năm×20% thuế ≈ +593 đ/cp [ước lượng]. φ đo theo tấn, không theo capex; xút–clo tốn capex/tấn hơn H2SO4 nên φ theo capex nhiều khả năng < 0,65 (chiều RẺ)",
    "data_provenance": "fail (mềm) — số BCTC/BQ khớp; nhưng hai đầu vào chịu tải nhất chỉ có nguồn báo chí: tổng vốn 1.844 tỷ (cafef/danchuphapluat, không có NQ ĐHĐCĐ/HĐQT trong src/) và φ (công suất xút 50k t từ TCCT; 245.949 t BCTN 2021 đơn vị thương phẩm so với 307.900 t quy 100%, không cùng đơn vị). Báo cáo tự gắn nhãn ước lượng cho φ — minh bạch, nhưng là ước lượng chiếm ±1.406 đ/cp mỗi 0,1",
    "liquidity_capacity_realism": "na — sizing 0% tại hiện tại; CK thanh khoản 1,69% ở 5 tỷ đã tự ghi chú ngoài vùng hiệu chỉnh; không đánh giá theo giá",
    "confirmation_bias_flipflop": "pass — r2 20.717 → r3 11.041 do sửa phương pháp theo skeptic r1 (đếm hai lần) cộng nguồn mới (TCCT 21/05/2025, BCTN 2021); có cầu nối r2→r3 đầy đủ; đã đối chiếu skeptic/r1.json + ERRATA, không mở dd_price_zones.json theo ràng buộc nhiệm vụ",
    "exit_discipline_gap": "na — không đề xuất mở vị thế; HARD ABANDON và mốc hai chiều đã liệt kê ở §8",
    "missing_items": "fail — (1) lá chắn thuế khấu hao mới ≈ +5,4% [ước lượng, đời 20 năm]; (2) chi phí tháo dỡ/hoàn nguyên môi trường BH1 (khu hoá chất cũ) vắng hoàn toàn, chưa định lượng được, chiều RẺ; (3) nguồn H2SO4 sau khi TB2 dừng 15/08/2026 (G6) ảnh hưởng trực tiếp kịch bản TỐT 'cú sốc axit duy trì' trọng số 0,25, thay bằng CƠ SỞ ≈ −8–9% [ước lượng]; (4) NQ phê duyệt tổng vốn Nhơn Trạch không có trong src/. Đạt: số CP 110.499.910 (mã 411, 30/09/2026), kiểm toán FY2025 + soát xét 6T chấp nhận toàn phần, quỹ KTPL/KH&CN đã trừ, cổ tức 21,14 tỷ là của CĐKKS, NCLQ <1% (chưa đọc NQ)"
  },
  "independent_verification": "BQ ticker_financial LN mẹ 2019-2025 tính lại: 244,02/179,66/208,93/353,21/209,18/240,78/208,95 — khớp từng số. Tự tính tay (không dùng model_r3.py) giá trị CƠ SỞ tại tham số trung tâm = 11.206 đ/cp, PV capex thay thế còn chi = 779,9 tỷ — khớp báo cáo. CBTT 1123/CBTT-HCCB 31/07/2026 xác nhận QĐ 1122 dừng sản xuất nhà máy Tân Bình 2.",
  "killer_objection": "Tâm dựa vào φ (±1.406 đ/cp mỗi 0,1) và kịch bản TỐT (axit), cả hai đều không có nguồn sơ cấp: φ suy từ báo chí và tấn khác đơn vị, còn TỐT giả định cú sốc H2SO4 kéo dài trong khi chính nhà máy axit đã dừng từ 15/08/2026. Hai thiếu sót mô hình (lãi suất chiết khấu capex vay nợ, lá chắn thuế khấu hao) mỗi cái ~5-6% nhưng ngược chiều nên gần triệt tiêu.",
  "recommended_followups": [
    "Lấy NQ ĐHĐCĐ/HĐQT phê duyệt dự án Nhơn Trạch (tổng vốn, cơ cấu công suất theo sản phẩm) và BCTN 2022-2025 có bảng công suất BH1 cũ → chốt φ theo capex, không theo tấn",
    "BCTC Q4/26: kiểm doanh thu/biên H2SO4 sau khi TB2 dừng (G6) trước khi giữ trọng số 0,25 cho TỐT",
    "Thêm vào model: lá chắn thuế khấu hao phần thay thế, và độ nhạy chiết khấu capex còn chi ở lãi vay (~8%) thay vì Ke",
    "Tìm cam kết/chi phí tháo dỡ và hoàn nguyên môi trường BH1 (QĐ cưỡng chế 2408 có quy định ai chịu chi phí không)"
  ],
  "summary": "Bản r3 sửa đúng lỗi đếm hai lần của r2, và các con số kiểm được đều khớp: LN mẹ trên BQ, tâm CƠ SỞ 11.206 tính lại độc lập, CBTT dừng TB2. Tuy vậy chưa thể CONFIRMED. Biến lớn nhất là φ (±1.406 đ/cp mỗi 0,1), chỉ có nguồn báo chí và so tấn khác đơn vị; đo theo capex thì φ có lẽ thấp hơn, tức tâm cao hơn. Kịch bản TỐT giả định cú sốc axit kéo dài trong khi nhà máy axit TB2 đã dừng, tức tâm thấp hơn khoảng 8-9% nếu bỏ. Mô hình còn thiếu lá chắn thuế khấu hao (+~5%) và chiết khấu capex vay nợ ở Ke thay vì lãi vay (−~6%); hai khoản gần triệt tiêu nhau. Chi phí tháo dỡ/hoàn nguyên BH1 vắng mặt và không định lượng được. Tôi đánh giá mô hình cẩn thận và minh bạch nhưng chưa đủ bằng chứng sơ cấp cho hai đầu vào chịu tải. Bỏ qua mọi giá thị trường trong báo cáo theo luật mù giá."
}
<<<END_VERDICT>>>