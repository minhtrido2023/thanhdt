**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Rev 2 sửa đúng lỗi lớn nhất của rev 1, và số học tái lập khớp. Nhưng tâm 4.563 vẫn treo vào hai giả định chưa có văn bản gốc, mỗi giả định kéo tâm đi hơn ±60%.

**Đã tự kiểm và khớp nguồn gốc:**
- Ảnh trang KT25 tr.30 TM17 cho phân phối LN 2024 đúng như báo cáo ghi: ĐTPT 39,006; KTPL 81,988; thưởng quản lý 0,315; cổ tức 42,847 (tổng 164,155). LNST 2024 là 130,02, LNST 2025 là 82,749, LN chưa phân phối cuối 2025 là 213,41.
- Số cổ phần 42.846.773 khớp với cổ tức 1.000 đ/cp = 42.846.773.000 đ.
- Tôi tính lại tâm từ `assumptions_rev2.json` (md5 khớp khoá): annuity 6,7395, hệ số chiết khấu 0,0902, tâm **4.562,8**. Độ nhạy α = 37% cho 7.787, khớp báo cáo.

**Chiều ĐẮT (tâm có thể quá cao):**
- **Dự án mở rộng Cao Sơn.** KT25 tr.19 ghi dự án chạy theo Giấy phép khai thác số 280/GP-BTNMT (07/08/2023), "hoạt động tới tháng 8/2045 theo giấy phép khai thác". Mốc 2045 là nguồn của T = 19 trong mô hình (báo cáo ghi "mỏ hữu hạn tới 08/2045"). Vậy base nhận đủ 19 năm thu nhập theo giấy phép của dự án nhưng coi dự án có NPV = 0.
  - Tổng mức đầu tư 1.829,5 tỷ, 70% vay; XDCBDD của dự án mới 29,5 tỷ.
  - Phần N cổ đông / B₀ ≈ 2,3%, thấp xa r = 13,5% ⇒ giả định NPV = 0 là lạc quan.
  - Chính báo cáo ước kịch bản xấu là −3.017 đ/cp (−66% tâm), nhưng con số ~1.020 tỷ vốn còn phải chi chỉ là ước lượng.
- **Q4/2025 = 59,35 tỷ, chiếm 79% LNST TTM 75,2** dùng cho kịch bản cơ sở. Báo cáo không kiểm Q4 có khoản một lần hay quyết toán giá với TKV hay không.

**Chiều RẺ (tâm có thể quá thấp):**
- **Dạng quy tắc trích KTPL không khớp nguồn.** Nghị quyết ĐHĐCĐ trích KTPL bằng 49,95% của *tổng quỹ phân phối* 164,155 tỷ, quỹ này rút cả từ LN tích luỹ, chứ không phải 63% của N.
  - α = 0,64 chỉ dựa trên 2 năm LN thấp.
  - Nếu cơ chế thật là trần tuyệt đối theo quy chế của TKV (văn bản không có trong src), tâm nằm đâu đó trong khoảng 1.243–7.787. Chiều nào cũng chưa có căn cứ văn bản.
- **Tỷ lệ thu hồi sổ sách ρ = 0,5 là ước lượng**, làm tâm lệch ±1.001. Mô hình còn cho tâm *cao hơn* nếu đóng mỏ sớm (8.244 khi đóng 2030), nghĩa là giá trị phụ thuộc nặng vào ρ.
- **Khoản chia 130,7 tỷ LN tích luỹ chỉ được +1.459 đ/cp** vì báo cáo giả định vay 8% để chia. Giả định vay này chưa được đối chiếu với số dư tiền.

Tôi không tra giá thị trường và không mở `kb/dd_price_zones.json` (theo ràng buộc của brief). Vì vậy so sánh với bản trước chỉ dựa trên REPORT.md rev 1; con số 14.100 trong báo cáo không dùng để chấm.

<<<VERDICT_JSON>>>
{
  "case_topic": "CST (Than Cao Sơn – TKV) DD REPORT_rev2 2026-11-23, tâm 4.563 trước CK / 4.422 sau CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — report lists WARNINGs only (TKV restructuring plan deadline 27/11/2026, related-party dominance, auditor change AASC→PKF-TTG, both opinions clean); no seizure/licence-revocation evidence in sources read; external UBCKNN/HNX check still not done (Phụ lục B)",
    "optimistic_comp_sotp_bias": "pass (no comps) — but the model has hidden single-point dependencies: α=0,64 fitted on 2 years, ρ=0,5 (ước lượng) moves ±1.001 (±22%), and the model returns 8.244 for closure in 2030 vs 4.563 for 19 years, showing value is driven by terminal book recovery, not operations",
    "data_provenance": "pass with caveat — TM17 (KT25 tr.30), TM8 (tr.19) and the share count checked against page images: match; KTPL 2026 52,76 is a residual (82,749 − 29,99), not a direct fund note; 2022–23 KTPL inferred from the BQ equity series; bear-case N from press, not the original AGM resolution",
    "liquidity_capacity_realism": "na — no position proposed (§9); liquidity discount σ√(Q/ADV60) computed from px_cst.csv restored from git",
    "confirmation_bias_flipflop": "pass — 13.084→4.563 (−65%) driven by audited TM17 (KTPL priority over shareholders), a document-level piece of evidence that rev 1 skipped; the downward revision has an independent evidentiary basis; dd_price_zones.json not opened per the brief's blind constraint",
    "exit_discipline_gap": "na — no position; §10 states re-lock conditions in both directions plus a DD expiry date",
    "missing_items": "fail (unquantifiable but material) — (1) Expansion capex 1.829,5 bn (70% debt) is committed (licence 280/GP-BTNMT 07/08/2023 granted, construction began 09/2023) and its licence underpins T=19 to 08/2045, yet base sets NPV=0; report's own estimate −3.017 đ/cp (−66% of centre) rests on an estimated ~1.020 bn remaining and has no project interest/cost-plus pass-through data; (2) KTPL rule: source sets fund as 49,95% of a 164,155 distribution pool (including retained earnings), not as % of N — legal basis (TKV fund policy / SOE wage-bonus regime) absent, span 1.243–7.787; (3) one-off check of Q4/25 (59,35 = 79% of base TTM) absent; (4) cash balance vs the 130,7 bn distribution (borrowing assumption) not checked. Pass: share count, audit opinion and FY2025 present, welfare fund now included, related-party 97% disclosed, licence term read"
  },
  "independent_verification": "Read KT25 tr.30 image: LN2024 distribution ĐTPT 39,006 / KTPL 81,988 / QL 0,315 / dividend 42,847 = 164,155; LNST 2024 130,02, 2025 82,749; retained 213,41 — all match. Shares 42.846.773 match dividend 1.000đ = 42.846.773.000. KT25 tr.19 image: project 1.829,52 bn, 70/30, licence 280/GP-BTNMT, to 08/2045, XDCBDD 29,48 — match. Recomputed centre from assumptions_rev2.json (md5 72300e34… matches lock): 4.562,8; α=37% ⇒ 7.787 — match.",
  "killer_objection": "The 2045 horizon (T=19) comes from the expansion project's licence 280/GP-BTNMT, yet the project's 1.829,5 bn cost (70% debt) is valued at NPV=0 when shareholder return on book is ~2,3% ≪ r; the report's own downside (−3.017, −66%) is excluded on an estimated remaining-capex figure. In the other direction, α=0,64 does not match how the AGM resolution actually sets the fund (49,95% of the distribution pool) — the centre's error may be large in both directions.",
  "recommended_followups": [
    "Get the 2026 AGM resolution / TKV fund policy (or the applicable SOE wage-bonus decree) to set the KTPL rule as absolute vs %N; rerun all 3 scenarios",
    "Get the remaining project capex schedule, debt financing and whether TKV's transfer price passes through depreciation + interest of the expansion (cost-plus); if not, put the −3.017 scenario into the weights",
    "Break out Q4/2025 (59,35 bn) for year-end cost-plus true-ups/one-offs before keeping base N=75",
    "Check cash and debt at 30/9/26 to decide whether the 130,7 bn distribution needs borrowing (+1.459 vs ~+3.050 đ/cp)",
    "Bound ρ (book recovery) with the composition of B0 (PP&E vs deposits vs working capital)"
  ],
  "summary": "Rev 2 correctly fixes rev 1's killer error: the audited TM17 confirms the bonus-welfare fund took 82,3 bn of 2024 profit ahead of shareholders, and the arithmetic reproduces 4.563 exactly. But the centre rests on two unverified structural choices with large effects in both directions. (1) The fund rule min(0,64N; 82,3) does not match how the resolution sets the fund (49,95% of a pool that includes retained earnings); without the TKV/SOE fund policy the centre spans 1.243–7.787. (2) The committed 1.829,5 bn expansion is the licence that defines the 2045 horizon, yet it is held at NPV=0 while shareholder return on book is ~2,3%; the report's own downside of −66% is excluded. Add the Q4/25 concentration (79% of base TTM) and the unverified ρ=0,5 (±22%). The direction of the revision is evidence-based; the magnitude is not yet decidable."
}
<<<END_VERDICT>>>