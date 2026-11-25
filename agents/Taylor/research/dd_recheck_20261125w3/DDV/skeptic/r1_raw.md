**Verdict: INCONCLUSIVE (độ tin cậy trung bình).** Phần toán của báo cáo đúng. Nhưng còn hai hạng mục có thể trọng yếu chưa được định lượng, nên chưa thể CONFIRMED.

**Đã tự kiểm lại:**
- **Biên LN chu kỳ:** tôi cộng lại 4 quý mỗi năm 2015–2025 từ `bq_hist_out.csv`, ra 4,0519%, khớp `NPM_CYCLE`.
- **Tâm:** tôi dựng lại bằng công thức đơn giản (tiền ròng 1.108, Q4 −4,38, kỳ vọng 2027 theo trọng số 0,45/0,40/0,15, Gordon trên LN giữa chu kỳ 193,6 tỷ, r 13,5%, g 3%, CK 1,47%). Kết quả 15.905 đ/cp so với 15.911 của báo cáo, lệch 0,04%.
- **Số cổ phiếu:** 146,11 triệu, không đổi trên BQ `OShares` từ 2015 đến Q3/2026.

**Điểm yếu chính (attack 8, hạng mục thiếu):**
1. **Quỹ khen thưởng phúc lợi:** không có ở báo cáo recheck, r3, lẫn DD 26/10. Mô hình coi toàn bộ LN giữa chu kỳ là của cổ đông. Phần giá trị đến từ lợi nhuận khoảng 8,6k đ/cp. Nếu trích 5–10% LN vào quỹ thì tâm giảm khoảng 2,7–5,4%, sát ngưỡng 5%. Tỷ lệ trích thực tế của DDV chưa được kiểm.
2. **Bãi thạch cao Đình Vũ:** chính báo cáo ghi là "cần kiểm chứng" và không ước số. Đây đúng là dạng thiếu sót của vụ QTP: khoản chi tuân thủ môi trường bắt buộc, chưa có trong mô hình.
3. Phụ: mô hình dùng BCTC **riêng** Q3/2026, chưa nêu vì sao không dùng BCTC hợp nhất (DDV có công ty con không?). Cổ tức tương lai và chính sách dùng tiền chưa có dữ liệu.

**Hai chiều:**
- **Chiều đắt (tâm quá cao):** DT chuẩn hoá lấy FY2025 = 5.652 tỷ, gấp 1,67 lần mức cao nhất trước đó (3.392). Nếu dùng TB 2021–25 thì tâm 12.452 (−21,7%). Bù lại, DT LTM 6.406 và 9 tháng 2026 vẫn duy trì mức cao, nên lựa chọn này còn tranh luận được, chưa phải sai.
- **Chiều rẻ (tâm quá thấp):**
  - Khoản trừ lãi gửi lấy trung điểm 35,4 tỷ, nằm nửa trên khoảng proxy lịch sử −9…+26 tỷ. Theo độ nhạy của r3, hạ về khoảng 8,5 tỷ thì tâm tăng khoảng +1.185 (+7,4%).
  - Lấy Ke ở đầu dưới 12,3% thì tâm +5,9%.
  - Dùng trọng số đường 2027 đối xứng 1/3 thì +425.
  - Không thấy sai lệch nào có bằng chứng độc lập buộc phải sửa base.

<<<VERDICT_JSON>>>
{
  "case_topic": "DDV — recheck B5/E15/E16 25/11/2026 (tâm 15.911, vùng 13.315–18.573)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no §2/§2.5 fear-buy claim",
    "scandal_migration_risk": "pass — WARNING list (Vinachem 64% transfer pricing, Liven 217 bn, Tường Nguyên payable 326,3 bn, 2 executives resigned 20/04/2026, gypsum) carried over in full from r3 §8; no sign of seizure/licence loss in the materials; but UBCKNN/HNX not checked directly (report says so itself)",
    "optimistic_comp_sotp_bias": "pass — no comps used; RI/Gordon model on book net cash + mid-cycle NP; RONIC = Ke in every cell (moat NONE) verified in model_r3.py value_ps; mults 0,8–1,2 symmetric",
    "data_provenance": "pass — NPM_CYCLE 4,0519% recomputed from bq_hist_out.csv (2015–25, 4 quarters each year incl. 2016 loss −470,3); SH 146.109.900 matches BQ OShares through 2026Q3; NC 1.108 = cash 114,4 + HTM 1.207,8 − ST borrowings 210,9 − tax 3,3 traced to en_p1.txt via assumptions_r3; int-deduction axis openly marked unverified (no audited fin income 2015–22)",
    "liquidity_capacity_realism": "na — sizing 0% at reference, ≤2% NAV if below rule-4; DD_GENERAL, no ADV check needed; 5 bn VND liquidity discount 1,47% already applied to the centre",
    "confirmation_bias_flipflop": "pass — model and assumptions identical by md5 to r3 (0e62e59d…), centre unchanged 0%, only r-sensitivity rows added; ±50/±100bp rows match r3 §7; dd_price_zones.json not opened per blind rule",
    "exit_discipline_gap": "na — DD_GENERAL; HARD ABANDON inherited from r3 (Liven, net cash <600 bn, related-party use, Vinachem extraction, gypsum shutdown)",
    "missing_items": "fail(unquantified) — (1) welfare/bonus fund appropriation from NP absent from recheck/r3/DD 26/10; earnings part of value ≈8,6k đ/cp ⇒ 5–10% appropriation = −2,7…−5,4% of centre, DDV's actual rate unverified; (2) gypsum (Đình Vũ) compliance capex: report itself says 'cần kiểm chứng', no number — the QTP-type failure; (3) separate (riêng) not consolidated Q3/2026 statements used, no reason given; (4) future dividends / cash use: no data (9M/26 dividend 248,4 bn already left cash at 30/09 — pass). Committed growth capex 186,4 bn MAP at NPV 0 — ok. Audit: 01/01/2026 audited column used — pass. Share count — pass. Base-year one-off: FY2025 is a peak year (margin 11,2% vs cycle 4,05%), disclosed as a sensitivity (12.452)",
    "symmetry": "{too_high_checked: 5, too_low_checked: 6, too_low_items: ['Ke at low end 12,3% → 16.854 (+5,9%), checked, kept as band', 'int deduction 35,4 in upper half of proxy −9…+26 → ~8,5 gives ≈+1.185 (+7,4%); no audited data either way — reported but not added to base', '2027 weights skewed 0,45 bad, symmetric 1/3 → +425; Bobby blind read is the basis — kept', 'LTM revenue 6.406 → 17.254 (+8,4%); one cycle-high year, no basis to raise the norm', 'V6 machine baseline V_short 29.229 / D 0,855 > ln2 — driven by peak NP 393,5 and g 12,75%, rejected as a basis for raising', 'Liven at book (already the most favourable case), midcoef 0,8/1,0/1,1 removed (already upward) — no further room'] ; too_high: FY2025 peak revenue, cash possibly retained by Vinachem (11.555), welfare fund, gypsum capex, separate vs consolidated BCTC}"
  },
  "independent_verification": "Recomputed NPM_CYCLE = 4,0519% from bq_hist_out.csv (matches). Simple independent centre formula (NC 1.108 + PV Q4 −4,38 + PV expected 2027 + Gordon on mid NP 193,6 bn, r 13,5%, g 3%, discount 1,47%) = 15.905 đ/cp vs report 15.911 (−0,04%). SH 146,11M constant on BQ through 2026Q3. Market price in report text (15.200) ignored when judging the model.",
  "killer_objection": "Two claims on mid-cycle earnings/cash are absent and unquantified: the welfare/bonus fund appropriation typical of state-controlled companies (up to ~−5% of centre) and mandatory gypsum-disposal compliance capex (unknown size, could be larger — the QTP case). Separately, the mid-cycle base applies the cycle margin to peak FY2025 revenue (1,67× the earlier maximum); TB 2021–25 gives −21,7%.",
  "recommended_followups": [
    "Read the audited FY2025 BCTC note on profit distribution / AGM 2026 resolution: % of NP to bonus & welfare funds and the 2026 dividend plan; subtract the fund % from mid-cycle NP if it is ≥3%",
    "Read the environmental licence / 2026 AGM resolution / BCTC commitments note for the gypsum site (new site, remaining capacity in years, committed capex); if capex is committed, subtract it from NC as compliance capex",
    "Confirm whether DDV has subsidiaries/associates; if so, use consolidated statements",
    "Find audited financial income 2015–22 to pin the interest deduction (35,4 vs ~8,5 — about ±7% on the centre)"
  ],
  "summary": "The recheck changes only r and adds display rows; the model is byte-identical to r3 and its arithmetic holds — I recomputed the cycle margin (4,0519%) and an independent centre of 15.905 against 15.911, and the ±50/±100bp rows match r3. Two-sided review: too high — normalised revenue at the FY2025 peak (−21,7% if TB 2021–25 is used), cash possibly retained by Vinachem; too low — interest deduction in the upper half of the historical proxy (≈+7,4%), Ke at the low end (+5,9%), skewed 2027 weights (+425). Neither direction has independent evidence strong enough to change the base. The verdict is INCONCLUSIVE, not CONFIRMED, because of attack 8: the welfare/bonus fund appropriation is missing entirely (estimated −2,7…−5,4% of centre, rate unverified) and the mandatory gypsum compliance capex is still 'cần kiểm chứng' with no number — exactly the failure that cost QTP −41%. Reading the FY2025 profit-distribution note, the AGM resolution and the gypsum environmental licence would close it."
}
<<<END_VERDICT>>>