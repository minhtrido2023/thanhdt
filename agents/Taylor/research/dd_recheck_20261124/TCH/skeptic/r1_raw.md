Đã chạy lại và tái lập được calc của báo cáo. Kết quả phản biện: **INCONCLUSIVE, độ tin trung bình**. Phần cơ học đổi r và CK holding đúng. Nhưng mô hình nền của r3b vẫn còn hai lỗ lớn chưa đóng, và lần rà lại này không đọc lại BCTC gốc nào.

**Phần đã kiểm độc lập và khớp**
- **Calc:** chạy lại `calc_recheck.py`, khớp từng số:
  - base 15.864 / P10 14.563;
  - r 12,3% → 16.270;
  - CK +20% → 14.294;
  - CK 27% → 13.745;
  - g 42,7% → 13.642.
- **Số cổ phiếu:** vốn góp 10.033,13 tỷ / 10.000 đ = 1.003,31 triệu cp, khớp `SH` = 1003.312808. Nguồn `notes_read.md:6`, BCTC HN 6T FY26.
- **Vốn chủ của cổ đông mẹ:** 15.279,65 − NCI 3.120,54 = 12.159,1 tỷ, khớp `EQ_ME`.
- **V_ngắn:** 796,1 / 13,5% / SH = 5.878 đ/cp, khớp.
- **Nợ vay bằng 0** (TM36) nên không có chi phí lãi vay bị bỏ sót. FY25 kiểm toán chấp nhận toàn phần, không có đoạn nhấn mạnh (`notes_read.md:55`).
- **Mù giá:** báo cáo có nêu giá 13.500 ở §0. Tôi bỏ qua con số đó khi đánh giá mô hình.

**Các điểm yếu chính**
1. **Chiều đắt, biên gộp (điểm phản đối mạnh nhất):**
   - Base dùng g = 51,9%. Số này lấy từ 6T FY26, chưa soát xét, và chủ yếu là NC-II.
   - Hai năm kiểm toán FY24 và FY25 đều cho biên BĐS 42,7%. Nếu dùng mức này thì tâm là 13.642 (**−14%**), vượt xa ngưỡng trọng yếu 5%.
   - Lần rà lại để nguyên điểm này và chỉ ghi "chờ soát xét".
2. **Chiều đắt, thiếu hạng mục (đòn 8):**
   - Nghĩa vụ NƠXH 20% và tiền SDĐ bổ sung ở GR, H2, NC-II chưa có số.
   - TM19 có dòng "đặt cọc thuê NOXH An Hải 57,20", tức công ty có dính NƠXH.
   - Đây là hạng mục có thể trọng yếu nhưng chưa định lượng được, nên theo luật verdict là INCONCLUSIVE.
3. **Chiều đắt, các khoản nhỏ hơn:**
   - Quỹ khen thưởng, phúc lợi chưa trừ. Tôi ước khoảng −1,8%.
   - Khoản HTM 678,3 tỷ ở "Sài Gòn Tài Lộc" chưa rõ danh tính ngân hàng. Mất trắng thì tối đa −4,2%.
   - CK base 0% nằm ở đầu lạc quan của dải. Ở mức +20% thì tâm −9,9%, và dải này vốn chốt cho HHS chứ chưa xác nhận cho TCH.
   - Mô hình không tính phần hàng tồn bán chậm sau khi hoàn thành dự án.
4. **Chiều rẻ:**
   - r base 13,5% nằm trên đầu trên của dải Ke (13,4%). Ảnh hưởng nhỏ: +0,2% ở 13,4%, +2,6% ở 12,3%.
   - Mô hình giả định toàn bộ tiền về ở mốc hoàn thành và chi phí chiết khấu đã là dạng thận trọng.
   - Giá bán không được tăng đến 2030.
   - Quỹ đất mới khoảng 3.006 tỷ chỉ tính bằng giá sổ.
   - TMĐT có thể gồm dự phòng, làm k bị cao.
   - Chưa cái nào trong số này đủ định lượng để đẩy tâm lên. Điểm 51,0% / 51,9% của hai kỳ sáu tháng gần nhất là bằng chứng nghiêng về phía rẻ, nhưng chưa được soát xét.

<<<VERDICT_JSON>>>
{
  "case_topic": "TCH — DD recheck 24/11/2026 (r3b reuse; r band E15/D4, CK holding Bước 0)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — no fear-buy/§2.5 claim; FLOOR_FAIL keeps it out of candidates, V8 sizing not applied",
    "scandal_migration_risk": "pass — no legal/regulatory WARNING in report; FY25 audit unqualified, no emphasis (notes_read.md:55); TM37 no material subsequent events; TM38 discloses no related-party loans or guarantees. Residual: 'Sài Gòn Tài Lộc' HTM 678,3 bn counterparty unidentified (open item 4)",
    "optimistic_comp_sotp_bias": "fail (partial) — no peer comps, but base g=51,9% (6T FY26 unreviewed, mostly NC-II) is the most favourable margin datapoint vs audited FY24 and FY25 both 42,7%; the audited basis gives 13.642 (−14%). Kept only as a parallel run, not in the base or the weighted grid. CK holding base 0% = optimistic end of a range chosen for HHS, not measured for TCH (+20% ⇒ 14.294, −9,9%)",
    "data_provenance": "pass with caveats — SH, EQ_ME, NCI, HTK, TMĐT, expensed bounds trace to notes_read.md/BCTN25/audited FY25 p42; g_obs traces to an unreviewed half-year; m=0,8(g−0,10) (10% SG&A, 20% CIT), ±5pp g and ±25% F axes are [UL] conventions; recheck re-read no source filing (admitted §3 D3)",
    "liquidity_capacity_realism": "na — no sizing (FLOOR_FAIL); 5 bn CK 0,63% from SUMMARY_r3b only applied mechanically",
    "confirmation_bias_flipflop": "pass (limited) — per brief, kb/dd_price_zones.json was not opened; compared only to r3/r3b inside the report: r3 16.347 pre → r3b 15.964 pre was a method fix demanded by skeptic (discount symmetry), recheck changes centre 0%; no favourable reinterpretation detected",
    "exit_discipline_gap": "na — no position or fear-buy claim",
    "missing_items": "fail (unquantified) — (1) NƠXH 20% / supplementary land-use fee at GR, H2, NC-II absent; TM19 shows NOXH An Hải deposit so exposure exists; unquantified, potentially >5% ⇒ INCONCLUSIVE; (2) bonus/welfare fund on retained + future surplus not deducted, est. ~−1,8% (5% × ~5,7k bn); (3) HTM 678,3 bn counterparty unverified, max −4,2%; (4) post-completion sell-through tail not modelled; pass: share count (vốn góp 10.033,13 bn ⇒ 1.003,31 m sh), no borrowings (TM36), latest audited FY25 present & unqualified, related parties only remuneration, compliance capex none identified beyond NƠXH",
    "symmetry": "{too_high_checked: 6, too_low_checked: 7, too_low_items: ['r base 13,5% above Ke band top 13,4% (+0,21%; 12,3% ⇒ +2,56%) — quantified, small', 'all unsold cash assumed at completion despite pre-sale collections (customer advances 5.599,8 bn) — conservative, unquantified', 'C_unsold uses skeptic (smaller) form; exact_C parallel larger — not in base', 'no selling-price escalation to 2030 completion; g fixed at past realised', 'new land bank (150 Tô Hiệu 1.677,5 + I.14 1.328,8) at NPV0/book — any surplus ignored', 'TMĐT is a legal estimate possibly incl. contingency ⇒ k could be overstated (axis is symmetric ±25%)', 'two consecutive half-years 51,0%/51,9% support g above audited 42,7% — evidence not yet reviewed']}"
  },
  "independent_verification": "Re-ran calc_recheck.py: base 15.864/P10 14.563, r12,3% 16.270, CK20% 14.294, CK27% 13.745, g42,7% 13.642 — all match. SH = vốn góp 10.033,13 bn / 10.000 = 1.003,31 m (matches 1003.312808); EQ_ME = 15.279,65 − 3.120,54 = 12.159,1 (matches); V_ngắn 796,1/0,135/SH = 5.878 (matches); no borrowings (TM36) confirmed in notes_read.md.",
  "killer_objection": "Base margin 51,9% comes from an unreviewed half-year, while two audited full years show 42,7% for property sales; at the audited margin the centre is 13.642 (−14%), and the recheck neither resolves this nor weights it into the base distribution.",
  "recommended_followups": [
    "Obtain AASC-reviewed 6T FY26 and recompute g by project (NC-II vs GR/H2); if reviewed g≈51,9% keep base, else move base or weight 42,7% into the grid",
    "Quantify NƠXH 20% land / cash-in-lieu and supplementary land-use fee per project from BCTN25 / project approvals",
    "Deduct bonus & welfare fund appropriation using TCH's AGM distribution ratio",
    "Identify 'Sài Gòn Tài Lộc' HTM counterparty (678,3 bn) from the original PDF, not the image read",
    "User to confirm whether the HHS-derived CK range 0…+20% applies to TCH and where base sits"
  ],
  "summary": "The recheck's mechanics are correct: I reproduced every r and CK-holding number and verified share count, parent equity and zero debt against the filing notes. But the recheck only changed r and the holding discount on r3b's unchanged model, and re-read no filing. Two of r3b's load-bearing weaknesses remain open. First, base gross margin 51,9% (unreviewed 6T FY26) against 42,7% in two audited years, worth −14% to the centre. Second, an absent, unquantified NƠXH / supplementary land-use-fee obligation that the company demonstrably has exposure to. Smaller too-high items: welfare fund ~−1,8%, unverified 678 bn deposit up to −4,2%, CK at the optimistic end (−9,9% at +20%). Too-low items (r above the Ke band, completion-timing conservatism, no price escalation, new land at book) are real but mostly unquantified and small where quantified. The centre 15.864 is a reproducible output of the model, but it is not yet a confirmed fair value."
}
<<<END_VERDICT>>>