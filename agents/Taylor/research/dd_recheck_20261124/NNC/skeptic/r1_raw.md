**Kết luận: INCONCLUSIVE, độ tin cậy trung bình.** Phần đổi r tính đúng, và các số bảng cân đối mang tải khớp với BQ khi tôi kiểm độc lập. Lý do không CONFIRMED là mô hình gốc (r3, mà bản rà lại dùng nguyên) thiếu hai hạng mục có thể làm tâm lệch quá 5% nhưng chưa định lượng được. Tôi bỏ qua giá 47.200 có trong báo cáo khi chấm mô hình. Theo brief, tôi không mở `kb/dd_price_zones.json`.

**Kiểm độc lập (BQ `ticker_financial`, Q3/2026):**
- **Tiền và vay:** tiền 25,47, vay ngắn hạn 5,00, vay dài hạn 69,89, số cổ phiếu 21,92 triệu đều khớp `n_cash` của mô hình.
- **Tiền gửi 322,44 tỷ:** đây là khoản lớn nhất, ≈14,7k đ/cp, ≈23% tâm, và vẫn chưa kiểm PDF từ r3. Tôi dựng lại tài sản ngắn hạn từ chỉ số thanh toán hiện hành: CR 4,628 × nợ ngắn hạn 88,63 = 410,2 tỷ. Trừ tiền, phải thu và tồn kho còn khoảng 340 tỷ, đủ chỗ cho 322,44 cộng khoảng 18 tỷ tài sản khác. Chỉ số thanh toán nhanh × nợ ngắn hạn = 390,3, khớp với tài sản ngắn hạn trừ tồn kho.
- **Vốn chủ:** tổng tài sản trừ nợ = 655,7 tỷ, khớp với BVPS 29.915 × 21,92 triệu cp.
- **Tiền ròng:** tôi tự tính lại được 223,62 tỷ, khớp mô hình.
- **Vay dài hạn tăng 51 tỷ trong Q3:** trùng với khoản đền bù đất Tam Lập 1 khu II 79,48 tỷ. Mô hình đã trừ khoản vay và cộng dự án dở dang theo sổ sách, nên không sót.

**Chiều ĐẮT (tâm có thể quá cao):**
- **Quỹ khen thưởng phúc lợi trích từ lợi nhuận tương lai chưa bị trừ.** Mô hình chỉ trừ số dư hiện tại 16,78 tỷ. Dòng tiền là EBIT×(1−thuế) cho 2027–2043, cộng lợi nhuận Q4 60 tỷ, không trừ khoản trích hằng năm. Tỷ lệ trích của NNC chưa có nguồn. Nếu trích 5–10%, tâm giảm khoảng 2,3–4,6k đ/cp, tức 3,6–7,2%, quanh ngưỡng 5%.
- **"Capex duy trì ≈ khấu hao" không có nguồn.** Thực tế NNC chi 23 tỷ (2022), 54 tỷ (2025) và 24,5 tỷ cho máy nghiền mua từ NHC (2026), trong khi mô hình có 0 capex suốt 17 năm.
- **Truy thu Núi Nhỏ ~42 tỷ chưa rõ đã nằm trong dự phòng 22,37 tỷ chưa.** Phần hở tối đa ~0,9k đ/cp (1,5%).
- Chi phục hồi môi trường và đóng cửa mỏ năm 2043 không đáng kể: chiết khấu 17 năm ở 13,5% còn hệ số ≈0,12.

**Chiều RẺ (tâm có thể quá thấp):**
- **r base 13,5% nằm trên đầu trên dải Ke (12,3–13,4%).** Lấy giữa dải thì tâm cao hơn khoảng +2%, kéo về 12,3% thì +4%.
- **Phần giá trị từ 10,3% cổ phần MVC đang dùng engine MVC r6 còn lỗi trần chu kỳ chưa vá** (errata 08/11). Phần này đang bị định giá thấp, tôi ước dưới 1% tâm.
- Các độ nhạy chiều lên đã giữ ngoài base một cách đúng, vì chưa có bằng chứng độc lập:
  - đối thủ hết giấy phép từ 2034: +4.367;
  - ADMIN perm05: +4.962;
  - trả trước của CNBP là tiền thuê: +2.126;
  - trọng số STRUCTURAL 0,30: tâm ≈ +4,8%.

**Bảng độ nhạy r:** đơn điệu và lồi. Tâm giảm khoảng 1,9–2,0k đ/cp mỗi 100bp, hợp với dòng tiền hữu hạn 17 năm cộng khối tiền ròng lớn. Bản rà lại không đổi gì ngoài r, nên không có lật kết luận: tâm r2→r3 tăng +6,4% là do sửa lỗi công thức mà skeptic tìm ra, không phải đọc lại thông tin cũ cho đẹp hơn.

<<<VERDICT_JSON>>>
{
  "case_topic": "NNC — DD recheck 24/11/2026 (r3 model, r-sensitivity E15/D4/V1 only)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; no fear-buy/§2.5 claim (r3 explicitly: not eligible §2.5)",
    "scandal_migration_risk": "pass (with gap) — WARNING items carried (truy thu reaching core Mũi Tàu mine, provision 0,84; Núi Nhỏ ~42 bn; MVC 44,07% cross-holding + mandate to 51%/D195; NHC 61% of receivables). Report admits no legal news re-check after 05/11; no evidence of migration found in files",
    "optimistic_comp_sotp_bias": "pass — no peer comp; SOTP = finite DCF 2027–2043 + net cash + NHC at book + CIP at book (NPV 0) + MVC stake solved by system of equations, holding 0%. Gordon only as a cross-check. MVC leg uses dd_MVC r6, which still has the unpatched cycle-cap double-count (biases DOWN, small)",
    "data_provenance": "pass — BQ Q3/26: Cash_P0 25,47, StDebt 5,00, LtDebt 69,89, OShares 21,92m, BVPS 29.915 all match model. 322,44 HTM (≈23% of centre, PDF still unchecked) is consistent with BQ current assets (CR×StLiab = 410,2 bn; residual ≈340 bn). n_q4 60 bn is an estimate (Q3 actual 69,3), flagged as such",
    "liquidity_capacity_realism": "na — report makes no new sizing claim; keeps the previously approved 5% NAV exception; CK 3,65% at 5 bn carried from r3",
    "confirmation_bias_flipflop": "pass — recheck changes only r (centre Δ0); r2→r3 +6,4% came from skeptic-found formula errors (D1 inflation cap, D2 symmetric axis), not re-reading the same facts more favourably. Did not open dd_price_zones.json (brief forbids it)",
    "exit_discipline_gap": "na — no fear-buy/sizing claim in this report",
    "missing_items": "fail (unquantified) — (1) future welfare/bonus-fund (KTPL) appropriations from profit not deducted (only the 16,78 balance): at 5–10% of NPAT ≈ −2,3…−4,6k đ/cp (−3,6…−7,2%), NNC's rate unsourced; (2) 'sustaining capex ≈ D&A' unsourced, while actual capex 2022 23 bn / 2025 54 bn / 2026 24,5 bn (machine bought from related party NHC); (3) unclear whether the ~42 bn Núi Nhỏ truy thu sits inside the 22,37 provision (gap ≤ ~0,9k, 1,5%). Checked and passed: share basis 21,92m (BQ Q3/26); Q3 new debt +51 bn matched to Tam Lập land comp 79,48 (debt subtracted + CIP at book); license Mũi Tàu to 2043 = DCF horizon; Núi Nhỏ lease term on [UL] axis; NHC related party flagged; closure/PHMT cost beyond 4,50 immaterial (discount factor ≈0,12 at 2043); audit FY2025 (KT25) present",
    "symmetry": "{too_high_checked: 8, too_low_checked: 9, too_low_items: ['base r 13,5% above Ke band 12,3–13,4% → +0,3…+4,0% (real, small)', 'MVC leg engine r6 has unpatched cycle-cap double-count → V_MVC understated (<1% est.)', 'rival license expiry 2034 +4.367 not in scenarios — no independent basis, correctly excluded', 'ADMIN perm05 +4.962 — sensitivity only, no basis', 'CNBP prepayment = rent +2.126 — unverified, correctly excluded', 'STRUCTURAL weight 0,20 [UL]; at 0,30 → +4,8% — unsourced either way', 'symmetric working capital +886 kept as sensitivity — correct', 'Tam Lập 1 khu II upside 0 (book/NPV 0 per user rule) — correct', 'flat-nominal price path given 50% weight while costs rise 3%/yr — [UL], not demonstrably too harsh']}"
  },
  "independent_verification": "Re-queried BQ ticker_financial NNC 2026-10-20: Cash 25,47 / StDebt 5,00 / LtDebt 69,89 / OShares 21,92m / BVPS 29.915 match. Recomputed n_cash = 223,62 bn (matches). Rebuilt current assets from CR (410,2 bn) and QuickR (390,3 bn): consistent with 322,44 bn HTM. Equity = totalAsset − liabilities = 655,7 bn = BVPS × shares. r-sensitivity slope ≈ −1,9…−2,0k/100bp, plausible for a 17-year finite DCF + large net cash.",
  "killer_objection": "The DCF takes EBIT×(1−t) for 2027–2043 with no deduction for annual welfare/bonus-fund appropriations and with zero capex on the unsourced assumption 'capex ≈ D&A', even though NNC has spent 23–54 bn/year on machinery. Together these could plausibly cut the centre by more than 5%, and neither is quantified.",
  "recommended_followups": [
    "Pull NNC's 2025/2026 AGM resolution for the KTPL appropriation rate (% NPAT) and deduct it from the operating flows and n_q4",
    "Get D&A from the FY2025 cash-flow statement and 9M/26, compare with 2022–2026 capex, replace 'capex ≈ D&A' with a sourced number",
    "Check in the Q3/26 PDF whether the 22,37 provision already includes the ~42 bn Núi Nhỏ truy thu; also confirm the 322,44 HTM line in the PDF",
    "Patch the cycle-cap bug in the dd_MVC r6 engine and re-run the MVC leg inside NNC",
    "Legal re-check after 05/11 (truy thu at Mũi Tàu, D195 / MVC mandate to 51%)"
  ],
  "summary": "The recheck does what it says: it re-runs the locked r3 model and changes only r, the CONTROL run reproduces r3 byte-for-byte, and the sensitivity table is monotonic with a plausible slope (centre 59,4k–63,7k for r 14,5%–12,3%). I independently re-checked the load-bearing balance sheet against BQ Q3/26 (cash, debt, share count, BVPS) and it matches; the unchecked 322,44 bn deposit fits the BQ current-asset structure. Two-sided: on the low side, base r 13,5% sits above the Ke band (+0,3…+4%) and the MVC leg still carries the unpatched cycle-cap bug; the larger upside items (rival license expiry, ADMIN perm05, CNBP rent) are rightly kept out of base for lack of evidence. On the high side, the inherited r3 model has two material gaps it cannot quantify: future welfare/bonus-fund appropriations (potentially −3,6…−7,2%) and an unsourced 'capex ≈ D&A' assumption despite recurring capex of 23–54 bn/year. Under the attack-8 rule this is INCONCLUSIVE, not CONFIRMED, until those two items are sourced."
}
<<<END_VERDICT>>>