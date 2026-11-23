**Kết luận: REFUTED.** Tôi chạy lại được đúng từng con số của mô hình rev4, nhưng nhánh O2 (không phát hành được) bị phạt hai lần. Riêng lỗi này đã kéo tâm thấp đi khoảng 29–31%. Ở chiều ngược lại, giả định p=0,5 lại mâu thuẫn với chính mô hình theo hướng làm tâm cao lên. Vì vậy tâm 4.205 không đứng vững theo cả hai chiều.

Báo cáo có ghi giá thị trường và ADV (§0, §6.4, §8). Tôi bỏ qua các con số đó và không tra thêm nguồn giá nào.

**Những gì tôi tự kiểm lại**
- **Hai trang tài liệu ĐHĐCĐ [IRQ3]:** đọc trực tiếp ảnh trang.
  - p9: LNST 2027/28/29 = 0,1/1,2/1,6 nghìn tỷ, dưới tiêu đề "Nếu Huy Động Vốn thành công". Khớp với báo cáo.
  - p7: 8.000 tỷ chia 60/20/20. Phần 20% thứ ba ghi rõ "bổ sung vốn lưu động **và/hoặc thanh toán các khoản vay ngắn hạn**".
- **Các con số mô hình:** F0 = 9.200 / 14.375 / 8.106 / 7.643; sàn BVPS 12.586; phần thiếu 1.077,6; O1 = 8.191; tâm 4.205. Tất cả khớp.

**Chiều RẺ (tâm bị kéo thấp sai)**
- **O2 bị phạt hai lần.** Mô hình vừa hạ kinh tế một bậc (vì kế hoạch chỉ áp "nếu huy động được vốn"), vừa trừ toàn bộ 8.000×1,08 như thể đã vay đủ 8.000 tỷ.
  - Nếu vay được 8.000 thì doanh nghiệp vẫn có vốn, kinh tế không phải hạ bậc. Nếu không vay được thì không có khoản nợ 8.640 để trừ.
  - Chỉ cần sửa một trong hai: O2 có trọng số từ 219 lên khoảng 2.700–2.800, tâm từ 4.205 lên khoảng **5.430–5.490**.
- **1.600 tỷ trả nợ bị tính như chi phí mới.** Phần 20% dùng để trả vay ngắn hạn: nếu tài trợ bằng nợ thì chỉ là đảo nợ, không phải nhu cầu vốn mới. Khoản 1.600 này lại bị trừ như một khoản phải tìm thêm.
- **Lãi cầu nối tính trùng.** Đã trừ khoản nợ theo mệnh giá, lại cộng thêm 8% lãi một năm.
- **LNST giữ lại 2027–28 (1.300 tỷ, PV khoảng 1.019) bị bỏ ra.** Lý do đưa ra là "đã nằm trong N 2029", nhưng không có chứng minh.

**Chiều ĐẮT (tâm bị đẩy cao sai)**
- **p=0,5 mâu thuẫn với chính mô hình.** Ở nhánh O1, nhà đầu tư mới phải trả ít nhất 12.586 đ/cp cho một cổ phiếu mà theo mô hình chỉ đáng 6.102–7.569 (tức lỗ khoảng 40% ngay khi mua), trừ kịch bản tốt.
  - Nếu không có người mua chiến lược hay người nội bộ được nêu tên, p hợp lý thấp hơn 0,5. Tại p=0,25, tâm là 2.212.
  - Báo cáo cũng tự nhận p được đặt sau khi đã thấy giá.
- **Chiều xuống được neo vào đúng kế hoạch của doanh nghiệp đang khủng hoảng, không chiết khấu.** 70% trọng số nằm ở mức bằng hoặc cao hơn kế hoạch (bao gồm kịch bản tốt 20% với N=2.500).

**Hạng mục còn thiếu (attack 8)**
- Không có nhánh vỡ nợ hoặc thanh lý khi không vay được. Sàn 0 hiện là áp đặt; giá trị thanh lý của tồn kho ròng 16.626 chưa được định lượng.
- ESOP 2025/26 đã duyệt nhưng chưa phát hành: pha loãng chưa định lượng (ước lượng nhỏ).
- Vẫn chưa kiểm chứng được: NĐ 390, kiện tụng do thanh toán chậm, nguồn "vốn khác" 500 tỷ, quỹ thưởng HĐQT 50,7 tỷ.
- Đạt: số lượng cổ phiếu, ý kiến kiểm toán FY25 và soát xét H1, cổ tức 2025 đã chi trả xong, khoản vay Chủ tịch.

**Việc cần làm tiếp**
1. Dựng lại O2 theo đúng một trong hai cách: (a) tài trợ bằng nợ với kinh tế giữ nguyên kế hoạch, hoặc (b) không có nguồn vốn, kinh tế hạ bậc, kèm mô hình thanh khoản/thanh lý. Tách 1.600 tỷ đảo nợ ra khỏi phần trừ.
2. Neo p vào bằng chứng (danh tính nhà đầu tư, hồ sơ chào bán), hoặc nói rõ trong mô hình rằng O1 đòi hỏi nhà đầu tư chấp nhận lỗ khoảng 40%.
3. Xử lý rõ LNST giữ lại 2027–28 và pha loãng ESOP.

<<<VERDICT_JSON>>>
{
  "case_topic": "PNJ — DD rev4 (REPORT_rev4.md, tâm 4.205 đ/cp, vùng 2.212–6.198, nhãn NON)",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim",
    "scandal_migration_risk": "pass — SX TM39 (PwC HCM18793, unqualified with emphasis): no diamond-origin litigation to 30/6; NĐ 390, late-payment lawsuits after 30/6, 'vốn khác' 500 and bonus fund 50,7 correctly flagged as unverified WARNING; no evidence of migration to core assets in the documents read",
    "optimistic_comp_sotp_bias": "fail — the outcome tree is internally biased in BOTH directions. LOW: O2 applies an economics downgrade (no capital) AND deducts the full 8.000×1,08 as if fully debt-funded (capital present), a double penalty; it also treats 1.600 of ST-debt repayment (IRQ3 p7, 3rd 20%) as new need although debt-for-debt is a wash, and charges bridge interest on top of face value. Fixing either error lifts O2 from 219 to ~2.670–2.790 and the centre from 4.205 to ~5.430–5.490 (+29–31%). HIGH: p=0,5 is inconsistent with O1, where new investors pay ≥12.586 for a share the model values at 6.102–7.569 (except bull); at p=0,25 the centre is 2.212. Base also takes the distressed issuer's own plan unhaircut with 70% weight at/above it",
    "data_provenance": "pass — IRQ3 p9 (LNST 0,1/1,2/1,6; 'Nếu Huy Động Vốn thành công') and p7 (8.000 = 60/20/20) verified on page images; share base 511,72tr, BVPS floor and shortfall recomputed; r anchor documented. Caveat: p and the bull N=2.500 are self-labelled estimates; p was set after seeing price (disclosed)",
    "liquidity_capacity_realism": "na — sizing 0%; no position proposed (the report's ADV figures were ignored under the price-blind rule)",
    "confirmation_bias_flipflop": "pass (with note) — centre 7.005→4.780→4.205 is driven by method fixes the skeptic demanded, not by new facts; rev4's net downward move rests partly on the O2 double count, an unjustified downgrade under the user's two-sided rule. Did not open kb/dd_price_zones.json (blind constraint in the brief); comparison uses only the report's own revision history",
    "exit_discipline_gap": "na — NON verdict, no position; two-sided label-change conditions are listed in §8",
    "missing_items": "fail — (1) no liquidation/default branch for O2: floor 0 is imposed, liquidation value of 16.626 net inventory not quantified (material, unquantifiable); (2) 2027–28 retained earnings (~1.300, PV ~1.019 ≈ +960 đ/cp in O1) omitted on an unproven 'already in N 2029' claim; (3) ESOP 2025/26 approved but unissued, dilution unquantified (small); (4) NĐ 390, late-payment litigation, 'vốn khác' 500, bonus fund 50,7 still unverified. Passed: share base, FY25 audit opinion and H1 review, 2025 dividend paid, chairman loan 703,7, capex commitments none"
  },
  "independent_verification": "Re-read IRQ3 p7/p9 page images: plan numbers and 60/20/20 split match; the 3rd 20% includes ST-loan repayment. Recomputed F0 (9.200,1/14.375,2/8.105,9/7.642,6), BVPS floor 12.586,2, shortfall 1.077,6, O1 8.191 and centre 4.205 — all match model_r4_out.json. Recomputed O2 variants: no economics shift ⇒ centre 5.490; shift but 1.600 netted as refinancing ⇒ 5.431",
  "killer_objection": "Branch O2 assumes simultaneously that the company has NO capital (plan downgraded one notch) and that it HAS borrowed the full 8.000 (deducting 8.640). That is a double penalty, pinning O2 to 219 and the centre ~30% too low. At the same time p=0,5 ignores the model's own conclusion that new investors lose ~40% on day one, which pulls the centre down. The 4.205 centre is not a stable number in either direction.",
  "recommended_followups": [
    "Rebuild O2 with one consistent mechanism: (a) debt-funded, plan economics, net of the 1.600 refinancing; or (b) unfunded, downgraded economics, with a liquidity/liquidation model instead of a 0 floor",
    "Anchor p to evidence (named investors, offering file) or state in the model that O1 requires investors to accept a ~40% loss vs model value",
    "Decide explicitly whether 2027–28 retained earnings are counted; quantify ESOP dilution",
    "Re-run the skeptic after the fix; the NON label is outside the scope of this price-blind review"
  ],
  "summary": "Rev4 fixes the identity error from r2, and every number I could trace matches the source (IRQ3 p7/p9 on page images, BVPS floor, share base, the full model). The outcome tree is still wrong. O2 penalises twice: it downgrades the economics because no capital is raised, then also deducts the full 8.000 plus bridge as if it were borrowed. It also counts 1.600 of debt refinancing as new need. Fixing this lifts the centre from 4.205 to ~5.4–5.5k. On the other side, p=0,5 contradicts the model itself: O1 requires investors to pay ≥12.586 for a share the model values at ~6–7.6k, which argues for a lower p (2.212 at p=0,25). There is also no liquidation/default branch, retained earnings 2027–28 are omitted, and ESOP dilution is unquantified. Errors run in both directions by >5% of the centre, so the zone needs rebuilding."
}
<<<END_VERDICT>>>