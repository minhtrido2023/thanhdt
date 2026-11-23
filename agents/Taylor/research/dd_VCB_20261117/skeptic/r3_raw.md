**Phán quyết: INCONCLUSIVE, độ tin cậy trung bình.** Phần số học của rev 3 khớp hoàn toàn. Điểm yếu là một phán đoán quyết định kết quả nhưng chưa có căn cứ độc lập: báo cáo lấy riêng 9 tháng đầu 2026 (9T/26) làm cửa sổ cho ROE bền. Nếu dùng cửa sổ khác thì giá trị cơ sở dao động từ −3% đến +17%. Thêm vào đó, VCBNeo vẫn chưa định lượng được.

**Đã tự kiểm lại (khớp):**
- md5 của file giả định, `calc_rev3.py` và output đều đúng như báo cáo khai.
- Đòn bẩy 7,30 khớp: dư nợ bình quân 1.744.810 / VCSH mẹ bình quân 239.078 = 7,298.
- ROE cơ sở: 2,85% × 7,298 × 0,8 × (1 − 0,0846) = 15,24%. Từ đó P/B 1,267 và giá trị 38.393 đ/cp, khớp.
- BVPS: 253.669 tỷ / 8.355,7 triệu cp = 30.359 đ.
- Đối soát VCSH 2025 cộng trừ ra 224.554,8 tỷ, đúng như báo cáo.

**Chiều khiến tâm quá THẤP:**
- **Biên cơ sở nằm gần đáy lịch sử.** Chênh lệch biên PPOP trừ chi phí tín dụng cơ sở là 2,85%. Trong 9 năm kiểm toán 2017–2025, chênh lệch từng năm chạy từ 2,26% đến 3,55%, trung vị 3,11%. Mức 2,85% chỉ cao hơn hai năm.
- **Áp đúng luật "cùng kỳ" của skeptic r2 cho cửa sổ dài nhất thì tâm cao hơn.** Cả 9 năm 2017–25 cho chênh lệch 3,06%, giá trị **43.900** (+14%). Riêng 2017–21 cho 40.800. Năm có chênh lệch ở mức trung vị cho 44.800.
- **Kịch bản xấu thấp hơn mọi năm đã kiểm toán.** Báo cáo ghép biên 2025 với chi phí tín dụng trung bình 9 năm, ra chênh lệch 2,15%. Mức này dưới năm tệ nhất 2017 (2,26%), tức là một điều chỉnh giảm không có bằng chứng độc lập. Ảnh hưởng nhỏ: dùng năm 2017 thì giá trị có trọng số lên 36.600 (+1,7%).
- **Chi phí tín dụng 0,70% gồm phần trích thêm để tăng bao phủ.** Chính báo cáo ghi rằng 9T không xoá nợ mới. Tổn thất thực tế chỉ 0,49–0,62%.

**Chiều khiến tâm quá CAO:**
- **Lệch giữa đòn bẩy và BVPS.** ROE tính bằng đòn bẩy bình quân 7,30 nhưng đem nhân với BVPS cuối kỳ. Đòn bẩy cuối kỳ chỉ 7,16, cho giá trị **37.100** (−3,4%).
- **BVPS 30/09 chưa trừ quỹ khen thưởng phúc lợi (KTPL) 2026.** Quỹ này chỉ trích cuối năm. Tôi ước lượng khoảng −405 đ/cp, đưa giá trị về 37.900 (−1,2%).
- **Biên 9T/26 bật lên chưa giải thích được.** Thu nhập lãi thuần trên dư nợ nhảy từ 3,76% lên 4,37% trong lúc có chỉ đạo giảm lãi. Báo cáo tự nhận chưa kiểm chứng được nguyên nhân, nhưng con số này vẫn nằm trong cơ sở.
- **Gordon giả định ROE bất biến,** trong khi biên PPOP đã giảm từ 4,45% xuống 3,02% giai đoạn 2022–25.

**Hạng mục còn thiếu (attack 8):**
- **VCBNeo:** chưa định lượng được, mà theo minh hoạ của chính báo cáo có thể kéo tới −8%. Đây là lý do chính cho phán quyết INCONCLUSIVE.
- **CET1, LDR theo TT22, Pillar 3:** không có. CAR 11,14% chỉ lấy từ báo chí.
- **CASA:** chỉ dẫn lại từ bản 17/11, không đọc lại từ báo cáo tài chính.
- **Pha loãng:** cổ phiếu thưởng 12,8%, cộng khả năng chia 16.571 tỷ bằng cổ phiếu (≈19,8%). Gộp lại có thể nhân số cổ phiếu lên khoảng 1,35 lần. Báo cáo nói "không đổi giá trị" nhưng không nêu quy tắc chia lại vùng giá theo đầu cổ phiếu sau ngày GDKHQ.
- **Lệch nhãn trong file giả định:** `cc_bull_source` ghi "TB 2023-2025" (0,28%), trong khi báo cáo và output tính đều dùng 2022–26 (0,49%).

**Không làm được:** tôi không kiểm lại TM34(a) của báo cáo kiểm toán 2025 (bản scan) và cũng không truy vấn BigQuery. Theo ràng buộc mù, tôi không mở `kb/dd_price_zones.json`, nên attack 6 chỉ dựa trên chuỗi revision báo cáo tự khai. Giá 52.100 trong mục 7 được bỏ qua khi đánh giá mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCB — DD rev3 (BCTC Q3/2026), centre 36.000 weighted / base 38.400",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — §8 lists only branch-level SBV inspections, small KTNN restatement (+29 tỷ), EY 2025 unqualified; no legal-entity/asset migration signal in cited material. VCBNeo policy obligation flagged as unverifiable, not scandal",
    "optimistic_comp_sotp_bias": "fail (two-sided, window choice) — no comps; Gordon P/B rests on a single 9T/26 window. Recomputed same-window alternatives from the audited series in assumptions_VCB_rev3: 9-yr 2017–25 spread 3.06% ⇒ 43.900 (+14%); 2017–21 ⇒ 40.800; median audited year 3.11% ⇒ 44.800; base spread 2.85% is 2nd-lowest of 9 audited years. Bear scenario spread 2.15% is BELOW every audited year (min 2017 2.26%) = downward adjustment without independent basis (weighted +1.7% if fixed). Opposite side: avg-leverage ROE applied to period-end BVPS (end lev 7.16 ⇒ 37.100, −3.4%); 9T/26 NII/loan jump 3.76→4.37% unexplained yet in base; constant ROE despite 2022–25 margin compression",
    "data_provenance": "pass with nit — all hard numbers trace to audited PDFs/Q3 with page refs and md5-locked JSON; recomputed lev/ROE/BVPS match. Nits: cc_bull_source label in JSON says 'TB 2023-2025' (0.28%) while value used is 2022–26 0.49%; CAR 11.14% press-only; CASA reused from 17/11",
    "liquidity_capacity_realism": "na — no sizing proposed ('không đề xuất mở vị thế'); ADV 175 tỷ vs fleet size not binding",
    "confirmation_bias_flipflop": "pass (limited) — chain 38.800 → 44.900 → 36.000; each step tied to new audited input (9-yr CC series, TM34 KTPL) or r2 window-consistency fix, none to price. Checked via the report's own revision chain only (task forbade opening dd_price_zones.json). Caveat: rev3 base-window choice (9T/26 vs through-cycle) is itself a judgment that moves the centre ±15%",
    "exit_discipline_gap": "na — no entry/sizing thesis; two-sided change conditions listed in §9",
    "missing_items": "fail-unquantifiable — VCBNeo capital/accumulated losses/support/consolidation-exemption term absent (report's own illustrative −2…−8%, may exceed 5%); CET1/LDR TT22/Pillar 3 absent; 2026 KTPL not yet accrued in 30/09 BVPS (est. −405 đ/cp, −1.2%, ước lượng); pending bonus 12.8% + possible 19.8% stock dividend need explicit per-share zone rebase rule. Present/pass: audit opinion (EY unqualified FY2025 present), share count 8.355.675.094 @30/09 from Q3 TM1, NPL/group 2/coverage, off-balance guarantees, one-off 3.171 removed from base, tax ETR, private placement NPV=0, no material compliance capex for a bank"
  },
  "independent_verification": "Recomputed from assumptions_VCB_rev3 + Q3 balances: lev 1.744.810/239.078 = 7.298 ✓; ROE base 2.85%×7.298×0.8×0.9154 = 15.24% ✓; P/B 1.267, value 38.393 ✓; BVPS 30.359 ✓; equity roll 2025 = 224.554,8 ✓; md5 of assumptions/calc/output match report ✓. Alternative windows computed independently (see optimistic_comp_sotp_bias).",
  "killer_objection": "The 'durable ROE' is a single 9-month window whose spread (2.85%) sits near the bottom of nine audited years while its margin component rests on an unexplained 2026 NII jump; applying the report's own same-window rule to the full audited cycle gives +14%, to period-end leverage −3%. The centre is therefore a window choice, not a measured quantity — and VCBNeo, the one item that could cut it >5%, remains unquantified.",
  "recommended_followups": [
    "State and justify the base window explicitly; show a through-cycle 2017–25 same-window case (≈43.900) alongside 9T/26 and decide with evidence (e.g., structural NIM reset), not default",
    "Rebuild bear scenario from an actual audited year/window (2017 spread 2.26% ⇒ 23.700) or document the evidence for a spread below every audited year",
    "Use period-end leverage (or average BVPS) consistently with the BVPS multiplied; deduct estimated 2026 KTPL accrual from 30/09 BVPS",
    "Obtain VCBNeo figures (SBV restructuring plan, VCB annual report/AGM docs) — decisive for the downside",
    "Add explicit per-share rebase rule for the 12.8% bonus and the 16.571 tỷ distribution if paid in shares",
    "Fix cc_bull_source label in assumptions JSON; source CASA/LDR/CET1 from Pillar 3 or annual report"
  ],
  "summary": "Rev 3's arithmetic and provenance are solid: every load-bearing input traces to audited filings and the ROE/P/B chain reproduces exactly. The weakness is structural, and it cuts both ways. The base ROE uses one 9-month window whose margin-minus-credit-cost spread is the 2nd-lowest of nine audited years. Applying the same-window discipline to the full cycle lifts the base about 14%. The bear case uses a spread below any audited year without evidence. Pushing the other way, the mismatch between average leverage and period-end BVPS, plus the not-yet-accrued 2026 welfare fund, lower the base about 3–5%, and the 2026 margin rebound is unexplained. The centre is defensible as one reading but not established. VCBNeo remains an unquantified, potentially material item, so INCONCLUSIVE rather than CONFIRMED or REFUTED."
}
<<<END_VERDICT>>>