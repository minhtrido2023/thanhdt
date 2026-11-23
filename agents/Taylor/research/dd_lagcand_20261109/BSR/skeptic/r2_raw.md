Đang viết kết luận. Đã đối chiếu các số then chốt (bảng cân đối trang 5, vốn lưu động vượt, tiền ròng, khoản trừ phần tuân thủ, TA5) và chúng khớp. Kết luận là **INCONCLUSIVE**, không phải REFUTED.

**Đã tự tính lại, đều khớp:**
- **Bảng cân đối HN Q3/26, trang 5 (đọc từ ảnh PDF gốc):**
  - mã 321 = 13.525,007; 323 = 441,645; 344 = 843,965; 429 = 31,961
  - vốn góp 411 = 50.073 tỷ ⇒ 5.007,3 triệu cổ phiếu.
- **Nợ khác trên bảng cân đối:** không có khoản nợ lớn nào bị bỏ sót (cổ tức phải trả 0,17 tỷ, doanh thu chờ phân bổ 4 tỷ).
- **Vốn lưu động vượt:** 23.416,4 − 13.003,6 = **10.412,8 tỷ**, khớp 10.413.
- **Khoản trừ phần tuân thủ:** mỗi đơn vị tỷ trọng = (5.285,2 + 33.719,3/1,135^1,5) × 0,945 / 5.007,3 = **6.260 đ/cp**. Ra đúng 626 / 2.504 / 4.695 ở ba mức; kỳ vọng ≈ 1.894 trước chiết khấu thanh khoản (báo cáo ghi 1.885 sau chiết khấu).
- **TA5 và lõi lãi:** TA5 = 6.230,45; lõi TB 2023-25 = 4.784,7; phần bóc lãi 889,6 + 402 = 1.292. Đều khớp.
- **Nguồn QĐ968 (bản docx):** xác nhận 7 phân xưởng mới, mục tiêu "lộ trình bắt buộc", tổng mức 36.397 tỷ, cơ cấu vốn 40/60 và phát hành cổ phiếu chỉ khi không đủ vốn.

**Chỗ yếu, cả hai chiều:**
- **Chiều ĐẮT — logic phân loại không đứng vững:** báo cáo xếp GHDT, DHDT, HGU vào "tăng trưởng, NPV0" chỉ vì chưa có văn bản bắt buộc Euro V.
  - Các phân xưởng xử lý lưu huỳnh và sinh hydro hầu như không tạo thêm sản lượng. Nếu không bắt buộc thì chúng là chi tiêu không sinh doanh thu, không phải tăng trưởng NPV0.
  - Mức 0,10 với xác suất 0,50 vì thế lạc quan. Nếu kỳ vọng tỷ trọng là ~0,45 thay vì 0,3025, tâm giảm khoảng −900 đ/cp (≈ −5,8%, ước lượng).
- **Chiều RẺ — khoản thuế GTGT bị gộp nhầm loại:**
  - Thuế GTGT được khấu trừ tăng từ 136 lên 6.509 tỷ nhưng bị gộp vào trục "giải phóng vốn lưu động theo giá dầu", với kỳ vọng chỉ 27%.
  - Nếu đây là khoản được hoàn hoặc khấu trừ, phần giá trị bị bỏ sót khoảng +900 đ/cp (ước lượng).
  - Thêm nữa, SRU3/4 một phần phục vụ mục tiêu chạy dầu thô chua (linh hoạt nguyên liệu), nên không hoàn toàn là tuân thủ.
- **Chiều ĐẮT, nhỏ:** TA5 = 6.230 tỷ gộp cả biên lọc yếu năm 2024, nên lõi được cộng vĩnh viễn +519/năm có thể quá tay (≈ −400 đ/cp, bù một phần qua khoản cộng lại năm 2027).
- **Thiếu, chưa lượng hoá:**
  - Trích quỹ KHCN và KTPL cho FY2026 trên lợi nhuận kỷ lục chưa ghi nhận: trong 9 tháng quỹ KHCN đi từ 856 xuống 844, tức chưa trích thêm. Luật cho trích tới 10% thu nhập tính thuế ⇒ 0 đến ~560 đ/cp (ước lượng).
  - Số phải nộp khi quyết toán cổ phần hoá: vẫn chỉ là WARNING.
  - BCTC kiểm toán FY2025 vắng mặt.
  - Thời hạn thuê đất và hợp đồng bao tiêu/nguyên liệu không được nhắc tới.

**Kết luận:** số học sạch và tỷ trọng tuân thủ đã được xử lý trung thực thành một trục kịch bản. Nhưng điểm then chốt (tỷ trọng tuân thủ, xác suất, tình trạng pháp lý Euro V) vẫn là giả định tự đặt, và lập luận phân loại có lỗ hổng. Theo luật, khoản thiếu trọng yếu mà không lượng hoá được thì ra INCONCLUSIVE. Nhãn TRÊN vùng không đổi ở mọi tỷ trọng tuân thủ, nhưng tôi không đánh giá điều đó vì ràng buộc mù giá.

<<<VERDICT_JSON>>>
{
  "case_topic": "BSR — DD rev3 23/11/2026 (REPORT_rev3.md), tâm 16.112 đ/cp sau CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — legal items (CPH settlement emphasis by Deloitte 6M/26, MBV 2.735,6 bn frozen) are disclosed as WARNING with MBV total-loss sensitivity −544 đ/cp; T11/2026 news scan admitted incomplete; no evidence of migration to core assets",
    "optimistic_comp_sotp_bias": "fail (partial) — SOTP math recomputes exactly, but the compliance-share axis 0,10/0,40/0,75 at p 0,50/0,35/0,15 is [UL] and its 0,10 base rests on a non-sequitur: GHDT/DHDT/HGU (hydrotreating + hydrogen, add no volume) are treated as growth NPV0 just because no Euro V mandate was found; if not mandatory they are non-revenue spend, not NPV0 growth. Shifting expected share to ~0,45 ⇒ about −900 đ/cp (estimate). Upward offset: SRU3/4 partly enables sour-crude flexibility (objective 4)",
    "data_provenance": "pass — BS p5 image re-read: 321 13.525,007 / 323 441,645 / 344 843,965 / 429 31,961 / 411 50.072,997 bn (⇒ 5.007,3m shares) all match; QĐ968 docx confirms units, objectives, 36.397 bn total, 40/60 funding. 2023-24 interest income not sourced (9M/25 annualized used for whole window) — small",
    "liquidity_capacity_realism": "na — report sizes 0% discretionary; ADV250 260,6 bn vs 5 bn position not material",
    "confirmation_bias_flipflop": "pass — internal revisions r1 16.437 → rev2 17.496 → rev3 16.112; each step tied to a documented change (errata E1–E4, then QĐ968 + TA/+370 fixes from skeptic r1); no label flip. dd_price_zones.json not opened per brief",
    "exit_discipline_gap": "na — no position recommended (0% discretionary)",
    "missing_items": "fail (unquantified) — (1) FY2026 KHCN/KTPL appropriations on record 9M profit not accrued: KHCN fund 856→844 over 9M, i.e. no appropriation yet; up to 10% of taxable income ⇒ 0…~560 đ/cp (estimate); (2) VAT receivable 136→6.509 bn lumped into the oil-price WC-release axis (27% expected) — if refundable, ~+900 đ/cp understated (estimate; LOW-side error); (3) CPH settlement amount owed to the state — WARNING only, unquantifiable; (4) FY2025 audited statements absent; (5) land-lease term and crude supply/offtake contracts not addressed; (6) Euro V mandate status for producers unverified — decides the 0,40 tier. Committed capex, share count/dilution, tax incentive to 2039, related party (PV OIL 21,9%) and the CPH emphasis-of-matter are covered"
  },
  "independent_verification": "Re-read BCTC HN Q3/26 balance-sheet p5 image: all liability/fund/NCI/charter-capital figures match the model. Recomputed WC_EX = 23.416,4 − 13.003,6 = 10.412,8 (report 10.413 ✓); compliance deduction per unit share 6.260 đ/cp ⇒ 626/2.504/4.695 ✓, expected ≈1.894 pre-CK vs 1.885 post-CK ✓; TA5 = (8.509,5+5.213,6)/2 − 631,1 = 6.230,45 ✓; core 2023-25 average 4.784,7 ✓; interest strip 889,6 (+402 FX) = 1.292 ✓. Read QĐ968 docx text: objectives/units/total/funding match the report.",
  "killer_objection": "The base compliance share of 0,10 (p 0,50) rests on a logical error: the Euro V hydrotreating/hydrogen units add no volume, so if they are not mandatory they are non-revenue spend, not growth at NPV0. The expected compliance share is likely understated (about −900 đ/cp, estimate). It is partly offset in the other direction by the VAT receivable of 6.509 bn being forced into an oil-price release axis (+~900 đ/cp, estimate). The cost breakdown in the investment total is not public, so neither side can be quantified from source.",
  "recommended_followups": [
    "Find a cost breakdown of the 39.004,5 bn total by unit cluster (FEED/EPC contract with China Chengda, ECA loan prospectus, BSR AGM/annual report) to replace the [UL] compliance share",
    "Re-classify GHDT/DHDT/HGU: growth only if a Euro V price premium or extra volume can be shown; otherwise compliance/non-revenue regardless of mandate",
    "Verify the Euro V fuel mandate status for producers (QCVN 01:2022 roadmap, emission roadmap Decision 19/2024) via legal-vn",
    "Read the VAT receivable note (mã 152/162) in BCTC Q3/26: whether it is refundable or carried forward, and the timing; move it out of the oil-price WC axis if it is a refund",
    "Accrue the expected FY2026 KHCN/KTPL appropriations against net cash or core earnings; check BSR's historical KHCN appropriation rate",
    "Obtain the FY2025 audited financial statements and the audit opinion"
  ],
  "summary": "Rev3 fixes every item skeptic r1 raised, and its arithmetic is clean: the balance sheet, share count, WC excess, compliance deduction, TA5 and interest strip all recompute exactly from the PDF and BQ. The weakness is now concentrated in one [UL] axis: the compliance share of the 39.004,5 bn expansion. Its base tier (0,10 at p 0,50) relies on treating Euro V hydrotreating/hydrogen units as growth NPV0 merely because no mandate was found, which biases the centre high by roughly 900 đ/cp (estimate). Pushing the other way, an unexplained VAT receivable of 6,5 nghìn tỷ may be under-released, biasing it low by a similar amount (estimate). FY2026 fund appropriations, the CPH settlement and the missing FY2025 audit remain unquantified. Not refuted on the numbers present; not confirmable until the expansion cost split and the VAT receivable are sourced."
}
<<<END_VERDICT>>>