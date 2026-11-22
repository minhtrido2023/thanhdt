**Kết luận: INCONCLUSIVE (độ tin trung bình).** Phần toán pha loãng của r4 đúng, nhưng báo cáo kế thừa nguyên các lỗ hổng chưa đóng của r3, và có một khoản trọng yếu không định lượng được (hợp đồng cung cấp tro/thạch cao từ nhiệt điện Phả Lại) chưa được xử lý.

**Đã tự kiểm lại:**
- **Tâm sau quyền, CK 5 tỷ:** (22.791 × 38.836.815 + (1 − 0,04454) × 74,98 tỷ) / 44.835.278 = **21.339**. Khớp r4 và khớp `post_rights.ck5ty.center_post` = 21.339,47 trong r3.
- **Số cổ phiếu trên BQ:** `OShares` = 38.836.815 từ 31/07 đến 30/09, khớp AIS và vốn góp 388,4 tỷ.
  - ⚠ Ngày **06/11, lúc cổ phiếu vẫn còn quyền, BQ đã ghi 44.836.815**: vendor ghi sổ trước số cổ phiếu sau quyền. Câu "BQ OShares = 38.836.815" của r4 chỉ đúng tại thời điểm đọc. Script nào nhân `OShares` của BQ quanh mốc này sẽ đếm trùng 6 triệu cổ phiếu.
  - Ngày 31/07 cũng đã có 38,84 triệu, tức trước khi ESOP thực hiện 03/08: vendor ghi sổ sớm theo cùng một kiểu.

**Hai chiều:**
- **Tâm có thể đang quá CAO:**
  - Lõi r3 cộng lại lãi dự án nhưng chưa có cơ sở. Bỏ phần này thì tâm còn 21.901 (cơ sở cum), thấp hơn khoảng 7%. Nó chỉ được để ở độ nhạy, thuyết minh chi phí đi vay vốn hoá chưa đọc.
  - Tiền thu cộng đủ mệnh giá trong khi headline định giá nợ dưới mệnh giá (biến thể nợ mệnh giá cho thấy khoảng 89%). Nếu 75 tỷ dùng trả nợ BIDV thì giá trị bị cộng dư khoảng 186 đ.
  - Nếu ESOP đợt 2 là đợt riêng: −233.
  - Chi phí phát hành chưa trừ.
  - CFO 9 tháng 9,9 tỷ so với LNST 94,4 tỷ, LCTT chưa đọc lại.
- **Tâm có thể đang quá THẤP:**
  - CK 4,45% ở cỡ 5 tỷ là ngoại suy. Cỡ 40 triệu cho +807 đ (+3,8%).
  - Áp CK lên phần tiền mặt: khoảng +74 đ.
  - Độ nhạy lãi suất: −100bp ⇒ +11,9%.

**Khoản còn thiếu (attack 8):**
- Hợp đồng nguồn tro/thạch cao (thời hạn, giá) chưa có. r3 §9 tự nhận còn mở, r4 không nhắc. Đây là khoản bắt buộc của ngành và trọng yếu, nhưng không định lượng được.
- Phả Lại: tổng mức đầu tư 262,9 tỷ, đã chi 190,7 tỷ, còn khoảng 72 tỷ capex cam kết. Theo quy ước "giá vốn − nợ = 0" thì trung tính, nhưng nếu dự án không đáng giá vốn thì ảnh hưởng tới 7,5% tâm.
- Không đề cập quỹ khen thưởng phúc lợi.
- ESOP đợt 2 chưa đọc được NQ 486/NQ-ĐHĐCĐ để đóng.

**Các bẫy khác:**
- `dilution_calc.py` đọc `calc_r3/model_scl_r3_out.json`, nhưng file này không còn ở đó. Bản duy nhất tìm thấy nằm ở `/tmp/fpt_r3/…`, nên hiện không chạy lại được từ repo.
- Giá thị trường trong báo cáo đã bị bỏ qua khi chấm.
- Không mở sổ vùng giá. Việc tâm r1→r3 dịch chuyển do sửa quy ước đã được r3 công khai trong bridge, r4 không định giá lại.

<<<VERDICT_JSON>>>
{
  "case_topic": "SCL — cập nhật pha loãng sau GDKHQ quyền mua 15,4453% @12.500 (r4, 10/11/2026)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — report makes no fear-buy/§2.5 claim (r3 explicitly states not eligible)",
    "scandal_migration_risk": "pass — WARNING items carried from r3 §7 (dilution, 26bn related-party loan @10%, Vincons 58.5% receivable unprovisioned, weak CFO); no sanction/prosecution news found per r3 WebSearch 05/11 & 08/11; r4 adds no new legal item and none was contradicted",
    "optimistic_comp_sotp_bias": "pass (with nit) — no comp; linear transform V→(V·S0+(1−d)·c·Cash)/(S0+c·Nr) is exact for weighted quantiles. Nit: cash added at par while headline debt is valued below par (nợ-mệnh-giá variant ⇒ ~89% of par); if proceeds repay BIDV debt, post-rights centre overstated ~186 đ (<1%)",
    "data_provenance": "fail (non-flipping) — load-bearing input calc_r3/model_scl_r3_out.json is missing from its canonical path (only copy at /tmp/fpt_r3/...), so dilution_calc.py is not reproducible from the repo; 'BQ OShares = 38.836.815' is time-dependent: BQ now shows 44.836.815 already on 06/11 (cum date) — vendor pre-books post-rights count. S0 still independently supported by AIS 17/09 and charter capital 388.4bn",
    "liquidity_capacity_realism": "na — no position/sizing proposed (report states no buy action)",
    "confirmation_bias_flipflop": "pass — r4 does not re-value; r1→r3 centre drift (22.855→22.769→23.652) is attributed step-by-step to data/convention fixes in r3 §2 bridge; ledger not opened per price-blind rule",
    "exit_discipline_gap": "na — no entry; r3 §8 two-sided milestones and HARD ABANDON (qualified audit on receivables, Vincons loss >50%, rights cancelled/changed) carried forward",
    "missing_items": "fail (unquantifiable) — (1) ash/gypsum supply contract with Phả Lại thermal plant: term/price absent (r3 §9 admits 'chưa có HĐ tro/thạch cao'), sector-mandatory, material, unquantifiable ⇒ INCONCLUSIVE; (2) remaining Phả Lại committed capex ≈72bn (262.9 total − 190.7 spent) not modelled — neutral under 'cost − debt = 0' convention, up to ≈1.600 đ/cp (~7.5%) if the project does not earn its cost; (3) capitalised borrowing-cost note unread ⇒ project-interest add-back (≈−1.750 cum, ~7%) still unsupported; (4) welfare/bonus fund not addressed; (5) ESOP-2 2.1% unresolved (NQ 486 unread, −233 đ, 1.1%); (6) offering costs not deducted (minor). Audit FY2025 unqualified ✓, share basis ✓, related-party loan ✓"
  },
  "independent_verification": "Recomputed ck5ty full-subscription centre: (22.791×38.836.815 + (1−0,044537)×74.980.782.340)/44.835.278 = 21.339 — matches r4 and r3 post_rights center_post 21.339,47. BQ tav2_bq.ticker OShares = 38.836.815 on 31/07, 05/08, 30/09 (matches); but 44.836.815 on 06/11 (pre-booked before issuance).",
  "killer_objection": "The r4 number is only as good as the r3 core it transforms. That core still includes an unsupported project-interest add-back (~7% of centre, capitalised-borrowing note unread) and has no data on the ash/gypsum supply contract that the Phả Lại project and the AAC/ash business depend on. A precise dilution update on top of an unclosed base is not a confirmed centre.",
  "recommended_followups": [
    "Restore calc_r3/model_scl_r3_out.json to its canonical path (verify md5 vs r3 '73a84983…') so dilution_calc.py is reproducible",
    "Read the BCTC note on capitalised borrowing costs; rerun the core without the interest add-back inside calc_r3 rather than quoting the skeptic's 21.901",
    "Obtain the term/price of the ash/gypsum supply contract with Phả Lại thermal plant and the remaining committed capex/schedule for Phả Lại",
    "Read NQ 486/NQ-ĐHĐCĐ 24/04/2026 to close the ESOP-2 2.1% question",
    "Notify data-ops: BQ OShares for SCL pre-books post-rights count (44.84M on cum date 06/11) and Close is not back-adjusted for the rights — both corrupt per-share/return calcs around 09/11",
    "Deduct offering costs and re-check the debt-repayment effect under the below-par debt convention"
  ],
  "summary": "The dilution arithmetic in SCL r4 checks out. I recomputed the post-rights centre (21.339 at the 5bn liquidity discount) from r3's cum distribution and the NQ 1363 terms, and the pre-rights share count 38.836.815 matches BQ, the AIS and charter capital. But r4 is a mechanical transform on the r3 core and inherits its open gaps. On the high side: the project-interest add-back (~7%, unsupported), the possible ESOP-2 (−1,1%), cash added at par against debt valued below par (~−0,9%), and offering costs. On the low side: the 4,45% 5bn discount is an extrapolation (40m size gives +3,8%), and rate sensitivity is large (±10%). The decisive missing item is the ash/gypsum supply contract (term/price), which is material and unquantifiable; remaining Phả Lại capex (~72bn) is also unmodelled. The input JSON r4 depends on has also gone missing from the repo (only a /tmp copy exists), and the BQ share count is now pre-booked at 44.84M on the cum date. Not refuted, not confirmable as written."
}
<<<END_VERDICT>>>