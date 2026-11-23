**Phán quyết: INCONCLUSIVE, độ tin trung bình.** Phần tính toán của rev3 khớp với nguồn. Nhưng một mục trọng yếu mà BCTC tự công bố vẫn chưa được định lượng: các hợp đồng mua khí hết hạn 12/2026. Ngoài ra có một lỗi nguồn nhỏ ở tỷ lệ trích quỹ KT-PL.

**Tự kiểm lại (khớp):**
- **Hồi quy LN–Brent** (2016–2025, 2025 trừ 1.304,8): tự tính được a = 2.239,9, b = 119,78, R² = 0,677. LN hoạt động ra 9.175 / 10.350 / 11.877 tỷ ở Brent 62/72/85, khớp báo cáo tới hàng đơn vị. RES thô 2.291, sau trừ khấu hao giảm còn 1.754, cũng khớp.
- **Cầu tiền ròng:** cộng 7 dòng trong assumptions ra đúng 39.654,7 tỷ.
- **Số cổ phiếu:** 2.412.949.756 tại 31/12/2025 (KT k49) và 30/06/2026 (soát xét p53). NQ ĐHĐCĐ 22/06/2026 chỉ chia cổ tức tiền 25%, không phát hành thêm.
- **Ý kiến kiểm toán FY2025:** Deloitte, 28/02/2026, chấp nhận toàn phần (k08).

**Chiều làm tâm quá CAO:**
1. **Hợp đồng khí hết hạn 12/2026, chưa định lượng (lý do chính của phán quyết).** Hai hợp đồng Lô 05.2/05.3 và 05-1b/c, tổng ≈1,76 tỷ m³/năm, cùng hợp đồng bán khí NCS cho NT2 0,6 tỷ m³/năm đều nằm ngay đầu chân trời dự báo (k60). Báo cáo chỉ nói ảnh hưởng "đã nằm trong trục suy giảm 0/1,4/2,8%". Nhưng trục đó được dựng từ xu hướng phần dư 2016–2025, không phải từ sự kiện hết hợp đồng. Không có độ nhạy "không gia hạn" và cũng không có dữ kiện nào về điều khoản gia hạn. Mục này trọng yếu nhưng không định lượng được từ nguồn, nên theo luật là INCONCLUSIVE.
2. **Tỷ lệ trích quỹ KT-PL bị đánh giá thấp.**
   - NQ ĐHĐCĐ (soát xét p52) ghi tổng trích từ LN 2025 là **379,6 tỷ**: đã tạm trích 187,75 trong năm 2025, cộng trích bổ sung 191,8.
   - Báo cáo chỉ lấy 214,4, tức phần phát sinh trong 9T/2026. Như vậy đã bỏ sót phần tạm trích năm 2025.
   - Tỷ lệ đúng ≈3,4% chứ không phải 1,91%. Ước lượng ảnh hưởng ≈ −500 đ/cp (~−1% tâm), dưới ngưỡng 5%.
3. **Dự phòng thu dọn 3.300 tỷ chưa có lịch chi.** Riêng Bể Cửu Long là 1.994,8 tỷ. Nếu mỏ đóng sớm khi hợp đồng hết hạn thì chi sẽ sớm hơn. Báo cáo coi đây là độ nhạy một chiều (chi sau 10 năm thì +976), không xét khả năng chi sớm.

**Chiều làm tâm quá THẤP:**
1. **Neo LN bền có thể quá thấp.**
   - LN 9T/2026 là 13.381 tỷ, quy năm ≈17.842 (tôi tự tính). Mức khớp hồi quy ở Brent trung bình 9T (88,3) chỉ ≈12.820 (tôi tự tính).
   - Mô hình neo phần vượt xu hướng (RES) vào TTM, tức gồm cả Q4/25 thấp bất thường (1.361 tỷ), rồi chỉ tính 50%. Q4/25 chưa được soát xem có khoản một lần nào không. Ngoài khoản hoàn nhập 492 tỷ, Q2/26 (5.860 tỷ) cũng chưa được soát.
   - Nếu Q4/25 là một lần, base bị hạ. Nếu Q2/26 là một lần, base đang bị đẩy lên.
2. **β = 1 cho mảng khí trung nguồn có cước điều tiết, không có cơ sở độc lập.** Báo cáo đã nêu dải Ke 12,3% ⇒ tâm 53.227 nhưng vẫn giữ 13,5%.
3. **Có phần đã cân đối hai chiều tốt.** Vốn lưu động (+656) và chiết khấu giữa kỳ (đã kiểm: TV ở mốc 1,6 năm là đúng cho dòng tiền đầu tiên giữa năm 2029) đều đã xét cả hai chiều.

**Ràng buộc mù:** báo cáo có giá thị trường, P/E, r ngụ ý. Tôi bỏ qua hết và không mở `kb/dd_price_zones.json`.

<<<VERDICT_JSON>>>
{
  "case_topic": "GAS (PV GAS) — DD rev3 23/11/2026, REPORT_rev3.md",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — legal WARNINGs disclosed (free float 4,24% <10% with 31/12/2026 deadline, Chairman/CEO removed 07/2026, reasons unchecked); none touches core assets/licences in the filings read; reasons for dismissal remain unverified",
    "optimistic_comp_sotp_bias": "pass — no comp/M&A precedent; SOTP pieces (growth commitments 21.238,7 bn and XDCB 5.916 at NPV0 book, ARO 100% book) are symmetric and carry ±sensitivities; Lô B tariff/IRR unknown both ways",
    "data_provenance": "fail (minor) — welfare/KT-PL rate 1,91% uses 214,4 bn (9T/26 movement only); NQ ĐHĐCĐ 47/NQ-KVN 22/06/2026 (soát xét p52) shows total 2025 appropriation 379,6 bn (187,75 tạm trích 2025 + 191,8 bổ sung) ⇒ ≈3,4%, centre ≈ −500 đ/cp (estimate, ~−1%). All other load-bearing numbers trace: regression, net cash bridge, shares, audit opinion",
    "liquidity_capacity_realism": "na — report proposes no value position; sizing only notes ≤2% NAV floor if LAG buys mechanically",
    "confirmation_bias_flipflop": "pass — r2→r3 centre +1,0% (50.146→50.651), every step itemised in a cumulative bridge tied to a filing (BCC Lô B +574, ARO −680, KHCN −97, RES-dep −747, mid-period +1.908, welfare −631); mid-period switch is the largest upward step but is a standard convention, applied correctly; label unchanged. Did not open dd_price_zones (budget); comparison done against in-folder r1/r2",
    "exit_discipline_gap": "na — no position proposed; HARD ABANDON conditions stated anyway (delisting decision, 4Q NP <9.500 bn at Brent ≥80)",
    "missing_items": "fail (unquantified) — (1) gas purchase contracts Lô 05.2/05.3 + 05-1b/c ≈1,76 bcm/yr and NCS→NT2 sale 0,6 bcm/yr expire 12/2026 (BCTC KT 2025 k60), inside horizon, with no 'non-renewal' sensitivity, only folded into a generic decline axis ⇒ material, unquantifiable from filings; (2) ARO 3.300 timing (Bể Cửu Long 1.994,8) could be pulled forward by those expiries, sensitivity only one-sided; (3) welfare rate understated (above, ~−1%); (4) one-off screen of Q4/25 (1.361) and Q2/26 (5.860) not done beyond the 492 reversal. Pass: compliance capex (ARO deducted 100%), share count/no dilution 2026 (p53, NQ cash-only dividend), audit FY2025 clean, related-party PVPower/PVN quantified, free-float dilution mechanics stated"
  },
  "independent_verification": "Recomputed the Brent OLS from calc/np_hist_gas.csv + brent_y.csv in pure python: a=2.239,9 b=119,78 R²=0,677, op NP 9.175/10.350/11.877 at Brent 62/72/85 and RES 2.291→1.754 — exact match. Summed the net-cash bridge = 39.654,7 bn — match. Shares 2.412.949.756 confirmed in KT 2025 k49 and H1/26 p53. Deloitte FY2025 clean opinion confirmed (k08). Mismatch found: welfare appropriation 379,6 bn per NQ ĐHĐCĐ vs 214,4 used.",
  "killer_objection": "The legacy-field purchase contracts (≈1,76 bcm/yr) and the NT2 sale contract all expire 12/2026, right at the start of the forecast horizon. The model's earnings base is a 2016–2025 Brent regression that assumes those volumes continue, minus a generic 0–2,8%/yr decline. Non-renewal or worse terms could cut NOPAT by more than any sensitivity the report shows, and no filing states the renewal terms.",
  "recommended_followups": [
    "Find the renewal/extension status and terms for Lô 05.2/05.3, 05-1b/c and the NCS–NT2 contract (CBTT, NQ HĐQT, PVN announcements) and add an explicit non-renewal sensitivity sized by the share of volume/gross profit",
    "Fix the welfare rate to the full 2025 appropriation (379,6 bn parent + subsidiaries) ÷ base-year NP, then re-run",
    "Screen Q4/25 and Q2/26 for one-off items (other income, provision reversals/charges, FX) before choosing the TTM vs 9T/26 residual anchor; the result could move the centre either way",
    "Tie ARO timing to field/contract expiry (Bể Cửu Long) so the timing sensitivity covers early spending as well as late",
    "State the basis for β=1 versus a regulated-midstream β, or keep it marked [UL]"
  ],
  "summary": "Rev3's arithmetic holds up. The Brent regression, the LN tại các mức Brent, RES, the net-cash bridge, the share count and the FY2025 clean audit opinion all reproduce exactly from the cited files. It is still not CONFIRMED. The biggest gap is that the 12/2026 expiry of the legacy gas purchase contracts (~1,76 bcm/yr) and the NT2 sale contract is shown only as a WARNING and assumed to sit inside a generic decline axis, which is material and cannot be quantified from the filings. A smaller provenance error understates the KT-PL appropriation (≈3,4% vs 1,91%, about −1% to the centre). In the other direction, the earnings anchor may be too low: the TTM residual includes an unscreened weak Q4/25 and is only half-credited, while 9T/26 annualised earnings run well above the fit; the β=1 choice is also unsupported. Net direction is unclear. Market prices in the report were ignored."
}
<<<END_VERDICT>>>