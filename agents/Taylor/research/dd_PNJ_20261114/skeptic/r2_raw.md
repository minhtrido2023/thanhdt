**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phép tính của rev3 tự nhất quán và các số BQ đều khớp. Nhưng tâm 4.780 dựng trên hai chỗ chưa chắc:

1. **Kịch bản không thể xảy ra về pháp lý.** Giá phát hành công bằng P* thấp hơn sàn BVPS 12.586 ở 3 trên 4 kịch bản, tức 80% trọng số. Đồng nhất thức "NĐT mới trả đúng giá trị" (giá trị cổ đông hiện hữu = F0 − PV(8.000)) không thể xảy ra trong chính những kịch bản đó. Kết quả thật chỉ có hai nhánh, lệch hai chiều ngược nhau:
   - **Phát hành ở giá ≥ sàn:** cổ đông hiện hữu được hưởng phần chênh, khoảng 8.665, cao hơn tâm 81%.
   - **Thất bại:** chưa định lượng. Không chắc là sụp, vì tồn kho ròng 16.626 lớn hơn khoản lỗ thu đổi 7.071.
2. **Đầu vào chịu lực nhất không truy được nguồn.** N=1.600 và cơ cấu 8.000 tỷ (60/20/20) quyết định 80% trọng số, nhưng lấy từ bản IR mà chính báo cáo ghi "không tải lại được, chưa truy lại".

Báo cáo có công khai cả hai điểm, nhưng tâm vẫn là một con số chưa đứng vững.

**Đã tự kiểm lại (đều khớp):**
- Mô hình: F0 cơ sở 9.200,3; PV(8.000) = 7.414,6; ra 3.489 đ/cp. BVPS ước FY2026 = 12.586. Tâm trọng số = 4.779,6.
- BQ: 511,72tr cp; LNST 9T/2026 = 471,7; tồn kho 16.626,2; nợ vay 4.320,6 = 3.616,9 + 703,7; CFO TTM −2.579,5.

**Chưa đọc được PDF gốc:** máy không có poppler, pypdf hay fitz. Vì vậy các số chỉ có trong BCTC (TM17, TM27, TTrPH 1.8) tôi chưa đối chiếu độc lập được.

**Thêm hai chỗ lệch tâm:**
- **Lệch lên:** giả định phát hành sau 0,6 năm (ước lượng) cộng 1.074 vào tâm, khoảng 22%. Lý do: mô hình chiết dòng vốn cần huy động theo Ke 13,5% nhưng không tính chi phí vay bắc cầu trong thời gian chờ.
- **Lệch xuống:** LNST 2027–28 (1.300 tỷ) bị bỏ, với lý do "đã nằm trong N 2029". Báo cáo ghi sai số ±260 tỷ, nhưng chưa chứng minh.

Báo cáo có nêu giá thị trường và nhãn "ĐẮT"; tôi bỏ qua khi chấm mô hình.

<<<VERDICT_JSON>>>
{
  "case_topic": "PNJ — DD rev3 (REPORT_rev3.md, 23/11/2026), định giá cổ đông hiện hữu sau đợt riêng lẻ 8.000 tỷ",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; report makes no fear-buy/§2.5 claim (NON, sizing 0%)",
    "scandal_migration_risk": "fail (partial) — legal/regulatory items the report itself lists as unverified: NĐ 390/2026, customer litigation/guarantees, 'vốn khác' 500 bn, HĐQT/BĐH bonus fund 50,7 bn (0,7 at start of year), related-party disclosure check on 'em trai thành viên HĐQT'; none shown to migrate, but none closed",
    "optimistic_comp_sotp_bias": "fail — two-sided. TOO HIGH: recap timing t=0,6y (ước lượng) adds +1.074 to the centre (4.780 vs 3.706 at t=0, ≈22%) by discounting the required raise at Ke with no bridge-financing cost; bull (p 0,2, subjective) supplies 2.720 of 4.780 (57%). TOO LOW: the transfer case (placement at ≥ legal floor) gives 8.665 base, +81% vs centre; 2027–28 NPAT 1.300 bn excluded ('đã nằm trong N 2029', ±260 bn unproven); company provision 7.071 vs observed TM17 loss rates ⇒ 3.867 (+5.878 đ/cp) kept as sensitivity only. Structural: the identity V = F0 − PV(8.000) assumes fair-price issuance, which the report itself shows is legally impossible (P* < BVPS floor 12.586) in scenarios carrying 80% weight ⇒ the centre is an average over infeasible states",
    "data_provenance": "fail — the single most load-bearing input (plan NPAT 2029 = 1.600 and the 8.000 bn 60/20/20 split, which drive scenarios with 80% weight) comes from an IR deck the report says 'không tải lại được … chưa truy lại'. BQ-traceable numbers all match. Filing-only numbers (TM17 21.057,9 / 821,4; TM27 7.071,1; TTrPH 1.8 price rule) could not be re-read independently (no PDF tooling on host)",
    "liquidity_capacity_realism": "na — sizing 0%, no position proposed; ADV in §6.5 not judged (post-lock market data)",
    "confirmation_bias_flipflop": "pass — r2 → r3 centre ~7.005 → 4.780, NON label unchanged; changes trace to skeptic r1 identity/terminal corrections plus new TM17 data, not to reinterpreting the same facts. Note: r1 implied base ≈0, r3 base 3.489 owes ~1.144 to the new t=0,6 assumption (base 2.345 at t=0)",
    "exit_discipline_gap": "na — no entry or sizing; §8 does state two-sided change conditions (placement outcome, FY2026 audit, 2 quarters of NPAT)",
    "missing_items": "fail — (1) PwC H1/2026 review carries an emphasis-of-matter (TM39, per assumptions_r3.json audit_opinion), but the report only cites the clean FY2025 opinion; TM39 content is not discussed (possible going-concern / deferred customer payments, TM2.1) — material, unquantified; (2) unexplained BQ Q2/2026 NPAT revision: Q2 row NP_P0 = −282,9 vs Q3 row NP_P1 = −738,9 (Δ −456 bn; source src/3c CV giải trình not cited); (3) the 2025 dividend-adjustment proposal (src/'Tờ trình điều chỉnh tỷ lệ chia cổ tức 2025') is in src but absent from the report — any unpaid cash dividend is a cash claim not in the model, amount unknown; (4) bridge-financing cost before the raise not modelled (centre effect up to −22% via the t assumption); (5) issuance-failure scenario unquantified (report admits). Pass: share base/bonus/ESOP (511,72tr matches BQ OShares), committed capex none, welfare fund treated as a liability, chairman loan 703,7 disclosed, FY2025 audit read"
  },
  "independent_verification": "Re-ran the model math by hand: F0 base = 1600/0,135/1,135^2 = 9.200,3; PV(8.000 @ t=0,6) = 7.414,6 ⇒ (9.200,3−7.414,6)/511,72 = 3.489 ✓; BVPS FY2026 est (13.182,31−6.741,66)/511,72 = 12.586 ✓; weighted centre 0,5·3489+0,2·13602+0,2·1351+0,1·445 = 4.779,6 ✓. BQ ticker_financial PNJ 2026Q3: OShares 511,72M ✓; 9M NPAT 1.467,4−738,9−256,9 = 471,7 ✓; Inventory 16.626,2 ✓; StDebt 4.320,6 = 3.616,9+703,7 ✓; CFO TTM −1.695,0+3.557,8−1.568,2−2.874,1 = −2.579,5 ✓; BVPS×OShares = 13.198 ≈ equity_parent 13.182 ✓. Not verified: filing-only TM17/TM27/TTrPH figures (PDFs are on disk, but the host has no PDF reader) and plan N=1.600 (source missing)",
  "killer_objection": "The centre averages existing-holder value over a fair-price issuance that, by the report's own legal-floor check (P* < BVPS 12.586), cannot happen in scenarios carrying 80% weight. The real outcome is bimodal: placement at ≥ floor with value transferred to existing holders (~8.665, +81%), or a failed/shrunk placement (unquantified, not necessarily near 445 since net inventory 16.626 exceeds the 7.071 loss). So 4.780 is not a reliable centre in either direction, and its main input N=1.600 is untraceable on disk.",
  "recommended_followups": [
    "Re-download or OCR the IR 'Cập nhật tình hình Q3/2026' p9 and lock NPAT 2027–29 + the 8.000 bn use-of-proceeds split into src/ with md5",
    "Read the PwC H1/2026 review TM39 (emphasis of matter) and TM2.1 (going concern / deferred payments); state their content and effect",
    "Replace the fair-issue identity with an explicit feasible-outcome tree: (a) placement at ≥ legal floor (transfer case), (b) shrunk placement at floor (6.923 bn), (c) no placement, funded from inventory release / debt with interest — each with p and value",
    "Model bridge-financing cost for the raise delay (or drop t=0,6 back to t=0 as base) — centre impact up to −1.074",
    "Explain the Q2/2026 NPAT revision (−282,9 → −738,9) from src/3c CV giải trình",
    "Check the 2025 dividend-adjustment proposal for any declared-but-unpaid cash dividend",
    "Install poppler-utils on the host so skeptics can independently re-read cited filing pages"
  ],
  "summary": "Rev3 fixes r1's arithmetic error, and every number I could recompute (model outputs, BVPS floor, share base, 9M NPAT, inventory, debt, TTM CFO) matches BQ and the locked model. The centre 4.780 still is not trustworthy. It assumes new investors pay exactly fair value, yet the report's own check shows that price is below the legal floor in scenarios carrying 80% weight. Realistic outcomes are either a transfer to existing holders (~8.665, higher) or a failed/shrunk raise (unquantified, not necessarily catastrophic), so the error can run either way. The recap-timing assumption flatters the centre by ~22% with no bridge cost. The load-bearing plan input N=1.600 is untraceable on disk. Attack 8 also finds three gaps: an undiscussed PwC H1 emphasis-of-matter, an unexplained Q2 profit revision, and a 2025 dividend document absent from the report. The NON label itself is not challenged here (price-blind); the valuation zone needs the outcome-tree rebuild before it can be confirmed."
}
<<<END_VERDICT>>>