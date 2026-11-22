Kết luận: **INCONCLUSIVE (độ tin cậy trung bình)**. Phần số học của báo cáo đúng ở mọi điểm tôi tính lại. Nhưng có một khoản lớn chưa được phân loại: dự án mở rộng 39.004,5 tỷ là đầu tư tăng trưởng hay đầu tư tuân thủ (bắt buộc). Khoản này có thể làm tâm lệch vài chục phần trăm.

**Đã tự kiểm lại và khớp:**
- **LN năm từ BQ:** 2019 2.841 · 2020 −2.809 · 2021 6.705 · 2022 14.450 · 2023 8.510 · 2024 631 · 2025 5.214. TB 2023-25 = 4.784,8.
- **Số cổ phiếu:** 5.007,3 tr cp, không đổi từ 2025Q3.
- **Tiền ròng:** 1.758,4 + 56.892,8 − 13.525 = 45.126 tỷ = 9.012 đ/cp.
- **Bóc lãi bản giữ tỷ giá:** (940,7 − 199,4) × 4/3 × 0,9 = 890. Lõi bản bóc tỷ giá 4.785 − 1.292 = 3.493.
- **Độ nhạy GRM:** 55 tr thùng × 25.582,5 × 0,9 = 1.266 tỷ cho mỗi USD/thùng.
- **Giá trị nhà máy kịch bản CƠ SỞ:** 3.863 / 13,5% = 28.615 tỷ; trừ phần thuế lên 20% sau 2039 (≈ −613) ⇒ 5.592 đ/cp.

**Điểm yếu, cả hai chiều:**

1. **Thiếu phân loại dự án mở rộng (attack 8).** Báo cáo ghi NPV = 0 và cộng 3.147,5 tỷ đã chi theo giá sổ, nhưng không nói dự án là tăng trưởng hay tuân thủ. Theo luật user 22/11, capex tuân thủ là dòng tiền ra.
   - Tôi nhớ (chưa kiểm, không có trong thư mục) dự án chủ yếu để nâng chuẩn Euro V và linh hoạt dầu thô, công suất tăng ít.
   - Nếu phần lớn là tuân thủ: khoảng 35.900 tỷ còn phải chi ≈ −7.170 đ/cp, tức khoảng −40% tâm (giống ca QTP).
   - Nếu 50% là tuân thủ: khoảng −20%.
   - Kéo tâm **xuống**.
2. **Nguồn gốc dữ kiện (attack 4).** Thư mục BSR không còn `src/` (6 PDF), `model_out.json`, `SUMMARY.json`, các file LOCK, `bq_bsr_fin.csv`, `px_bsr.csv`. Báo cáo cũng tự nhận số E1–E4 chép từ errata, chưa đối chiếu PDF gốc. Tôi chỉ đối chiếu được LN và số cổ phiếu qua BQ; các khoản bảng cân đối thì không.
3. **CƠ SỞ cao hơn neo lịch sử (chiều đắt).** LN lõi CƠ SỞ 3.863 cao hơn cả hai mốc neo khoảng 370 tỷ (+10,6%): 3.493 (2023-25) và ≈3.530 (2019-25). Lý do "công suất ~115%" của r1 đã bị bỏ khỏi chữ ở rev2 mà phần cộng thêm vẫn giữ. Tác động ≈ +550 đ/cp (~3%).
4. **Đếm TA hai lần (chiều rẻ).** Cửa sổ 2023-25 cho TA5 trọng 1/3, trong khi chu kỳ ~4 năm (1/4), lệch ≈ −520 tỷ/năm ≈ −770 đ/cp. Đồng thời TA6 lại bị trừ thêm trong LN vượt 2027. Hai lệch ở mục 3 và 4 gần bù trừ nhau.
5. **Mục mở có thể đóng được (không đổi giá trị).** "Capex 3.155 tỷ chưa giải thích" khớp với khoản trả trước người bán tăng +2.637 tỷ, chủ yếu là 2.601 tỷ ứng cho 2 nhà thầu TQ. Vậy capex duy trì thực ≈ 550 tỷ trong 9T, dưới mức khấu hao.
6. **Lật kết luận (attack 6):** r1 → r2 do errata dựa trên chứng từ, nhãn không đổi. Theo ràng buộc mù tôi không mở `kb/dd_price_zones.json`.

Giá thị trường có trong báo cáo, tôi đã bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "BSR — DD rev2 09/11/2026 (dd_lagcand_20261109), centre 17.496 đ/cp, P10 13.093 / P90 23.345",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass (partial) — legal WARNING items are listed: CPH settlement not approved (Deloitte emphasis), MBV-blocked deposit 2.735,6 bn with a total-loss sensitivity of −544 đ/cp, PVN 92,12% related-party flows. The report admits it did not scan legal news after 03/11",
    "optimistic_comp_sotp_bias": "pass with caveat — no external comp; SOTP arithmetic recomputed and matches (plant BASE 5.592, net cash 9.012, GRM 1.266 bn/USD). Bias in both directions: BASE core 3.863 sits ~370 bn/yr (+10,6%, ≈+550 đ/cp) above both anchors (3.493 for 2023-25, ≈3.530 for 2019-25) after rev2 dropped the r1 '~115% capacity' rationale (toward HIGH). The 2023-25 window weights TA5 at 1/3 vs a ~1/4 cycle (≈−770 đ/cp) and TA6 is also deducted in 2027 excess profit (double count, toward LOW). Net roughly offsets",
    "data_provenance": "fail (partial) — the src/ PDFs (6 files + SRC_md5.txt), model_out.json, SUMMARY.json, LOCK_*.txt, bq_bsr_fin.csv and px_bsr.csv cited in §10 are absent from the BSR folder. The report states E1–E4 figures were copied from the errata without re-reading the PDFs. BQ-traceable numbers (annual NP, shares) verified; balance-sheet line items not verifiable",
    "liquidity_capacity_realism": "na — no sizing claim beyond 'minimum ration'; ADV ~260 bn per the report",
    "confirmation_bias_flipflop": "pass — r1→r2 (16.437→17.496) driven by documentary errata E1–E4 (interest-strip correction, expansion at book, funds/NCI); label unchanged. kb/dd_price_zones.json not opened per the brief's blind constraint",
    "exit_discipline_gap": "na — the report makes no buy/sizing recommendation (label ABOVE range; defers to LAG rules)",
    "missing_items": "fail — (1) growth-vs-compliance classification of the 39.004,5 bn expansion is ABSENT. NPV0 plus 3.147,5 bn at book assumes growth; if mostly compliance (Euro V/crude flexibility, my unverified recollection) the remaining ~35.900 bn is an outflow ≈ −7.170 đ/cp (~−40%); 50% compliance ≈ −20%. Material, but the split is not quantifiable from the files present. (2) Funding of the 15.601,8 bn equity portion (cash vs share issuance) unstated; share basis 5.007,3 m verified in BQ. (3) Latest audited FY2025 opinion not cited, only the H1/26 review. (4) CPH settlement and possible payment to the state: WARNING only, unquantified. Present items: welfare fund 441,6, NCI 32, KHCN 844, tax 10%→20% after 2039, MBV sensitivity"
  },
  "independent_verification": "BQ ticker_financial: annual NP 2019-25 = 2.841/−2.809/6.705/14.450/8.510/631/5.214 (avg 2023-25 4.784,8 ✓); OShares 5.007,3 m unchanged since 2025Q3 ✓. Recomputed net cash 45.126 bn = 9.012 đ/cp ✓, interest strip 890 ✓, plant BASE 5.592 đ/cp ✓, GRM 1.266 bn/USD ✓. All match; balance-sheet inputs could not be checked against the PDFs (src/ missing)",
  "killer_objection": "The 39.004,5 bn Dung Quất expansion is booked as NPV-zero growth capex with no growth-vs-compliance classification. If it is mainly a compliance/upgrade project, the ~35.900 bn still to be spent is a value outflow under the 22/11 rule and the centre falls by up to ~40% — the QTP failure mode",
  "recommended_followups": [
    "Pull the investment decision/feasibility for the NMLD Dung Quất upgrade-expansion: capacity before/after, purpose (Euro V vs capacity), and IRR. Split capex into growth vs compliance and re-run with the compliance share as an outflow",
    "Restore src/ PDFs and the calc output files (model_out.json, SUMMARY.json, LOCK md5); re-read E1–E4 figures from the Q3/2026 consolidated statements",
    "Justify or remove the +370 bn/yr uplift of BASE core over the historical anchor; align the TA allowance between the normalisation window and the 2027 excess",
    "Close the 'capex 3.155 unexplained' open item: it matches the +2.637 bn rise in supplier prepayments (2.601 to the Chinese engineering contractors)",
    "Cite the FY2025 audit opinion; state how the 15.601,8 bn equity portion is funded; scan legal news after 03/11 (CPH settlement, MBV)"
  ],
  "summary": "The rev2 BSR model is arithmetically sound: every BQ-traceable input (annual NP, share count) and every recomputed component (net cash 9.012, interest strip 890/1.292, plant value 5.592, GRM sensitivity) matches. Two-sided biases are small and roughly offset: BASE core sits ~10% above the historical anchor (toward high), while the turnaround is over-weighted in the window and double-counted in 2027 (toward low). The decisive gap is a missing item: the 39.004,5 bn expansion is valued at NPV zero with no growth-vs-compliance classification. If it is largely a compliance upgrade, the centre could fall 20-40%. Provenance is also weakened because the cited source PDFs and output files are absent from the folder and the errata figures were never re-read from the filings. Not refuted on the numbers present, but not confirmable until the expansion is classified and the sources are restored."
}
<<<END_VERDICT>>>