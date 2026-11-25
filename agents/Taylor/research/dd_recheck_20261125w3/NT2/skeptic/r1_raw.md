**Kết luận: REFUTED, độ tin cậy trung bình.** Lỗi then chốt nghiêng về phía tâm 24.003 đ/cp **quá THẤP**. Có thêm vài khoản chiều ngược lại (tâm quá cao) chưa lượng hoá được.

**Các số tôi tự tính lại:**
- Net cash khớp: (11,8 + 5.362,3 − 1.795,8 − 297,1) / 287,876 triệu cp = 11.398 đ/cp.
- Hệ số niên kim 10 năm @13,5% khớp: 5,3195.
- Tôi cộng theo năm từ `fin_nt2_r3.csv`, tức BQ, cùng nguồn báo cáo dùng. Dòng tiền tự do (CFO + CFI) **lớn hơn LNST ở 10/11 năm** 2015–2025. Bình quân 2022–25 là 1.382 / 853 / 524 / 994 ⇒ khoảng 938 tỷ/năm. 9T/26 là 1.254 tỷ.

**Lỗi then chốt (quá thấp):**
- LNST chuẩn hoá 800 lấy từ biên 2015–25 (10,39%). Phần lớn giai đoạn đó còn gánh khấu hao khoảng 550 tỷ/năm, nay khấu hao chỉ còn 115–153.
- Mô hình đặt dòng tiền gốc = LNST chuẩn hoá, trục ±150 có tâm 0. Chính cách tách của r3 cho thấy khi khấu hao ~550 thì dòng tiền ≈ LNST + 433. Mức −110 là phần dư so với khấu hao, không phải so với LNST đã gánh khấu hao cũ.
- Dòng tiền vận hành trung tâm của mô hình là 800 − 168,5 (thu nhập tài chính ròng sau thuế) = 631,5 tỷ/năm. Thực tế 2022–25 ước khoảng 770–840 sau khi bỏ lãi tài chính.
- Chênh lệch +140…210 tỷ/năm ⇒ tâm tăng khoảng +2.600…3.900 đ/cp (+11…16%), vượt ngưỡng trọng yếu 5%.
- Nếu giá bán theo PPA giảm khi tài sản hết khấu hao, mức điều chỉnh sẽ nhỏ hơn. Biên 2025 là 14,2% và 9T/26 là 11,6–12,8% cho thấy lợi ích chỉ chuyển một phần sang lợi nhuận. Vì vậy chiều quá thấp có cơ sở nhưng chưa ra một con số chắc.

**Khoản còn thiếu (quá cao, chưa lượng hoá):**
- Khi tính tiền ròng, mô hình chỉ trừ nợ vay và cổ tức phải trả.
- Chưa trừ: thuế phải nộp, quỹ khen thưởng phúc lợi (cả số dư lẫn phần trích hằng năm từ LNST), các khoản phải trả khác.
- Chưa cộng: hàng tồn kho phụ tùng, phải thu khác.
- Chưa kiểm thuế suất TNDN thực tế và mốc hết ưu đãi thuế trong thời hạn dự phóng.
- Tôi không đọc được file PDF BCTC Q3 vì máy không có pdftotext, PyMuPDF hay pypdf. Vì vậy các khoản này chưa kiểm được.

**Điểm vượt qua:**
- Số cổ phiếu ổn định.
- Có kịch bản thời hạn 5–15 năm và kịch bản song song khí cạn 2030 (nút 4 năm).
- Các mốc HARD ABANDON đã nêu rõ.
- Báo cáo có giá 22.200 đ; tôi bỏ qua con số này khi chấm mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "NT2 — DD recheck 25/11/2026 (REPORT_recheck_NT2.md, model r3 reused, centre 24.003 đ/cp)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — report makes no fear-buy/§2.5 QUALIFY claim (r3 §9 states KHÔNG đủ điều kiện)",
    "scandal_migration_risk": "pass (weak) — WARNING items listed (POW conflict, SHB deposit concentration, BKS dismissal, 2020 tax fine); but legal scan not refreshed since 05/11/2026 (report admits, open item 5); no contrary evidence found",
    "optimistic_comp_sotp_bias": "pass — no comp/SOTP; finite-horizon DCF with TV=0. V6 V_dài 57.794 displayed only, correctly not blended",
    "data_provenance": "fail (partial) — BS numbers hard-coded from r2 'src/Q3_2026_hopnhat_va_giaitrinh.pdf' (could not re-open: no PDF tooling); NP 800 is [UL]; Q3/26 unaudited; PPA term two conflicting sources unresolved; ±150 FCF magnitude [UL]",
    "liquidity_capacity_realism": "pass — sizing 2% NAV ≈19M VND vs ADV250 17,8 bn, CK 0,04–0,08%",
    "confirmation_bias_flipflop": "pass — centre unchanged vs r3 by construction (control md5 asserted); r2→r3 bridge documented; dd_price_zones not opened per brief constraint",
    "exit_discipline_gap": "pass — HARD ABANDON (a)(b)(c) + two-sided milestones in r3 §9",
    "missing_items": "fail — (1) welfare/bonus fund appropriation from LNST and its balance-sheet balance absent anywhere in r3/recheck (est. −3…−5% centre if 5–8% of NP); (2) net-cash claim excludes tax payable/other payables and excludes inventory/other receivables — unquantified both sides; (3) CIT effective rate / incentive expiry inside 5–15y horizon not checked — unquantified, potentially material; (4) decommissioning/environmental obligations flagged but not read; (5) audited FY2025 used only via BQ; capex commitments: NT5 via NPV-0 rule (pass); share count 287,876,029 stable (pass)",
    "symmetry": "{too_high_checked: 6, too_low_checked: 6, too_low_items: ['FCF base = NP_norm while NP_norm margin embeds ~550bn/yr old depreciation — empirical FCF 2022-25 avg 938 > NP in 10/11 years ⇒ +11…16% (MATERIAL)', 'r 13,5% above Ke band 12,3–13,4% ⇒ +0,2…+2,6% (minor)', 'revenue normalisation 7.137 vs 2022-25 avg 7.268 / TTM 10.325 ⇒ base conservative vs TTM, defensible vs history', 'TV=0 after horizon vs plant life/PL13 2039 ⇒ covered by 12–15y nodes', 'inventory/other receivables omitted from net assets ⇒ unquantified', 'variant D (+110) excluded from base despite depreciation-ended evidence ⇒ +8,2%']} — too_high items: PPA/gas 2030 depletion weight, welfare fund, omitted payables, CIT incentive expiry, Q3 unaudited (−94bn precedent), SHB counterparty"
  },
  "independent_verification": "Net cash 3.281,3 bn / 287,876M sh = 11.398 đ/cp — MATCH. Annuity 10y@13,5% = 5,3195 — MATCH. Recomputed annual NP and CFO+CFI from fin_nt2_r3.csv (BQ): FCF−NP positive 2015–2024 every year (e.g. 2022 +499, 2023 +359, 2024 +441), 2025 −136, 9M26 +252 — contradicts using FCF=NP_norm (built on D-burdened historical margins) as grid centre.",
  "killer_objection": "Internal inconsistency in the FCF axis: NP_norm 800 comes from 2015–25 margins that bear ~550bn/yr depreciation, yet base FCF is set equal to it with the −110 residual (which is relative to depreciation, not to D-burdened NP) used to justify the −150 node. By the report's own decomposition FCF ≈ NP_hist + ~433; empirical FCF 2022–25 ≈ 938bn/yr vs model op-centre 631,5 ⇒ centre plausibly +11–16% too low (smaller if the PPA capacity price fell when depreciation ended, which 2025–26 margins of 11,6–14,2% only partially confirm).",
  "recommended_followups": [
    "Re-derive base FCF consistently: either NP at current depreciation (~115–153) with FCF−NP ≈ D − capex − overhaul excess, or NP_hist with FCF−NP ≈ +433; show the bridge on 2022–25 actuals net of ΔAR",
    "Read the BCTC Q3/2026 balance sheet in full: tax payable, welfare/bonus fund, other payables, inventory, other receivables; include them in the net-claims bridge",
    "Check CIT rate history and incentive expiry date (BCTC thuyết minh thuế TNDN) and apply in-horizon if applicable",
    "Read Phụ lục 13 GSA / NQ HĐQT 08/07/2026 to settle PPA/GSA term",
    "Refresh legal scan after 05/11/2026; read SHB deposit note",
    "Install a PDF text tool (poppler-utils or pypdf) in the env so skeptic passes can verify filings"
  ],
  "summary": "The recheck faithfully reproduces r3 (control md5, net cash and annuity factor verified) and correctly adds the Ke-band and E15/E16 rows, whose effect is small (+0,2…+2,6%). But the model it reuses has a load-bearing inconsistency: the base cash flow equals a normalised NP taken from margins burdened by ~550bn/yr of now-ended depreciation, while the fleet's own BQ cash-flow data show FCF above NP in 10 of 11 years and averaging ~938bn/yr in 2022–25 versus a model operating centre of ~632. That points to a centre roughly 11–16% too low, partly offset by too-high items that were never checked: welfare-fund appropriation, payables omitted from net claims, and CIT-incentive expiry. I could not re-open the source PDF to check those. The verdict is REFUTED (medium): the FCF base must be rebuilt consistently and the balance-sheet claims completed before the centre can stand."
}
<<<END_VERDICT>>>