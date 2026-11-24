**Phán quyết: INCONCLUSIVE (độ tin trung bình).** Phép tính cơ học của bản recheck đúng. Tôi tự tính lại SOTP từ `assumptions_r2.json` và ra đúng 26.778:

- Lõi: 914,7 tỷ
- Liên kết: 400,9 tỷ
- Legend City (LGC): 365,3 tỷ
- Nợ ròng: −33,3 tỷ
- Tổng: 1.647,6 tỷ chia 61,524 triệu cp

V_ngắn 25.733 cũng khớp. Nhưng các điểm mở có thể làm tâm lệch quá 5% vẫn chưa đóng được, và tôi tìm thêm một khoản bị thiếu. Giá 19.300 trong báo cáo đã bị bỏ qua khi chấm.

**Điểm mới tìm được:**
1. **Độ nhạy CK +20% tính sai nền.** Báo cáo suy ngược từ r2 ra phần đóng góp của liên kết + LGC là 13.377 đ/cp, rồi ra 24.103 (−10,0%). Đọc thẳng từ model thì phần này là 400,9 + 365,3 = 766,2 tỷ, tức 12.454 đ/cp, cho ra 24.288 (−9,3%). Chỉ là số hiển thị, nhưng con số dùng không truy được về model.
2. **Thiếu quỹ khen thưởng phúc lợi.** Cả báo cáo r2 lẫn recheck đều không nhắc tới (grep "khen thưởng|phúc lợi" không ra dòng nào). EPV lõi coi 100% LNST thuộc cổ đông. Nếu trích 5–10% LNST thì tâm giảm khoảng 2,8–5,6%. Tỷ lệ thật nằm trong nghị quyết ĐHCĐ, chưa đọc.
3. **Hai giả định lõi lệch về hai phía:**
   - SG&A base 1,5% thấp hơn TTM 1,625%, trong khi chi phí bán hàng 9T tăng 59%. Theo hướng làm tâm cao, khoảng −3%.
   - r base 13,5% nằm trên đầu trên dải Ke 13,4%. Theo hướng làm tâm thấp: +0,5% so với đầu trên dải, khoảng +3,4% nếu về giữa dải.

**Điểm mở kế thừa từ r2 (chưa đóng):**
- Capex duy trì khoảng 45 tỷ/năm so với khấu hao khoảng 12 tỷ/năm: có thể làm tâm cao 7–15%.
- Legend City định giá bằng giá gốc (NPV = 0) trong khi lợi nhuận NOXH có trần theo quy định: có thể quá cao, chưa định lượng được.
- Capex môi trường bắt buộc: báo cáo tự nhận chưa soát.
- LCTT 9T/26 gốc chưa đọc lại, nên V_dài chưa có.

**Chiều làm tâm thấp đi:** GPM 3,6% so với biên sản phẩm tự sản xuất 5,29%, doanh thu base 7.700 thấp hơn TTM 7.849,6, LGC không có kịch bản tốt, khoản ứng trước Vinaconex 38 tỷ, và cách đọc (b) cổ tức liên kết (+535 đ). Từng khoản đều dưới 5% và chưa có bằng chứng độc lập.

<<<VERDICT_JSON>>>
{
  "case_topic": "VGS — recheck DD r2 theo luật B5/E15/E16 (24/11/2026)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; the report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — no legal/regulatory WARNING in the recheck; r2 W6: NQ 17 only amends business lines, no issuance; FY25 audit unqualified, H1/26 review unqualified. Open: entire Supervisory Board resigned 09/2025 and associate ownership not traced (r2 W4) — governance, no sign of migration",
    "optimistic_comp_sotp_bias": "pass/partial — SOTP recomputes exactly (core 914.7 + assoc 400.9 + LGC 365.3 − net debt 33.3 = 1,647.6bn = 26,778 đ/cp). Assoc bull 5×TTM = 581bn ≈ 2.3× book, weight 0.25. No external comps. LGC valued at a related-party cost price (Vinaconex is two-way), acknowledged",
    "data_provenance": "fail (minor, display-only) — CK +20% sensitivity uses a 13,377 đ/cp base back-solved from r2's 30% number; the model gives assoc+LGC weighted = 766.2bn = 12,454 đ/cp ⇒ 24,288 (−9.3%), not 24,103 (−10.0%). The rest traces to assumptions_r2.json (md5 c1301436… matches) and BQ v6_bq.csv",
    "liquidity_capacity_realism": "na — no new sizing; inherits the separately approved 5% NAV V8 exception. Note: the post-CK haircut uses ADV250 6.17bn; ADV60 2.23bn would give CK 1.57% instead of 0.94% at 1bn",
    "confirmation_bias_flipflop": "pass — compared only against r2 of the same ticker (REPORT.md r2 + skeptic r2.json): centre unchanged 0%, label unchanged; the recheck states plainly that r2's INCONCLUSIVE items are still open; no reinterpretation toward YES",
    "exit_discipline_gap": "na — no new sizing/entry claim; r2 has a milestone table M4/M5 with failure conditions",
    "missing_items": "fail (INCONCLUSIVE level) — (1) bonus & welfare fund not modelled (grep r2+recheck: 0 hits); EPV takes 100% of NI ⇒ −2.8…−5.6% if 5–10% of NI, not quantified; (2) maintenance capex ~45bn vs D&A ~12bn (open from r2) ⇒ −7…−15% core, unverified; (3) Legend City NOXH profit cap + remaining committed capital ⇒ base ×1.0 at cost may be too high, unquantified; (4) environmental compliance capex not checked (report admits); (5) LCTT 9M/26 not re-read (V_dài missing). Pass: share count 61,524,155 unchanged in 2026 (NQ 17, CBTT); FY25 audit present and unqualified; one-offs (21.1bn provision reversal, 26.6bn assoc dividend) identified; ST bank debt itemised, no LT bank debt",
    "symmetry": "{too_high_checked: 9, too_low_checked: 9, too_low_items: ['base r 13.5% above Ke-band top 13.4% (+0.5%; mid-band +3.4%)', 'base GPM 3.6% (10Y median incl. trading) vs own-product margin 5.29% and falling trading share; +0.35pp ⇒ ~+4.9%, unproven', 'base revenue 7,700 < TTM 7,849.6', 'Legend City has no bull scenario although 214,481 m² of phase 1A land is delivered + land-use-fee exemption', 'Vinaconex advance 38.02bn omitted (+~618 đ/cp if a free asset; likely project cost)', 'assoc reading (b) 2025 = 70.2 ⇒ +535 đ', 'assoc bear 0.7× book evidenced only by 2024 ROE ~9%', 'post-CK liquidity haircut subtracted from intrinsic centre (convention)', 'HTM–loan carry: checked, net fin 9M26 = −10.7bn ⇒ no upside']} — too_high items: maintenance capex>D&A, NOXH cap on LGC, welfare fund, SGA 1.5% < TTM 1.625% (~−3%), compliance capex, ADV60 vs ADV250, assoc base avg3 includes peak TTM, short-term loan rollover (free net debt −327.6bn), CK +20% base error"
  },
  "independent_verification": "Re-ran model_r2.py (copied to /tmp, assumptions md5 matches) and hand-checked: core bear/base/bull NI 56.0/129.4/179.2bn ⇒ weighted EPV 914.7bn; assoc 179.0/421.6/581.5 ⇒ 400.9; LGC net 401.4 ⇒ 365.3; net debt 71.653+1,096.6−1,201.601 = −33.3 ⇒ centre 26,778 MATCH. TTM NP 276.7 and V_ngắn 25,733 MATCH. CK +20% sensitivity DOES NOT MATCH (24,288 vs reported 24,103).",
  "killer_objection": "EPV of the core = NOPAT/r assumes maintenance capex = D&A (~12bn/yr) and 100% of NI to shareholders (no welfare fund), while non-LGC capex is ~45bn/yr; these two items together could cut the centre ~10–20%, and Legend City at cost ignores the NOXH profit cap — none of these were quantified in r2 or the recheck.",
  "recommended_followups": [
    "Read LCTT FY24/FY25/9M26 to split maintenance/growth capex for the pipe core (closes the r2 open item + V_dài)",
    "Read the FY25/FY26 AGM resolutions for the bonus & welfare fund rate; deduct it from core NI",
    "Look up the statutory NOXH profit cap and Legend City's remaining committed capital; rerun LGC NPV at r 13.5%",
    "Fix the CK +20% sensitivity to use the model's direct assoc+LGC weighted value (12,454 đ/cp ⇒ 24,288)",
    "Review base SGA 1.5% vs TTM 1.625% and base r 13.5% vs Ke band 12.3–13.4% (one in each direction)"
  ],
  "summary": "The recheck is a correct mechanical rerun: same model and assumptions (md5 verified), centre 26,778 / 26,526 reproduced independently, r sensitivities 12.3–14.5% match. But as a valuation it still carries r2's unclosed load-bearing gaps (maintenance capex vs D&A, Legend City at cost vs NOXH profit cap, compliance capex), adds no new data to close them, and a new missing item turned up (bonus/welfare fund absent from EPV). One display number was back-solved wrongly (CK +20%: 24,103 should be ~24,288). Upside items (GPM mix, revenue below TTM, r above the Ke band, LGC with no bull, Vinaconex advance) were also checked; each is <5% and unevidenced. The downside items are larger but unquantifiable from the files on hand ⇒ INCONCLUSIVE, consistent with r2."
}
<<<END_VERDICT>>>