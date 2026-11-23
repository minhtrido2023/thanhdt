**Verdict: REFUTED (medium confidence).** Rev5's arithmetic checks out. The model doesn't hold together: it uses the 9-year dividend record to haircut the cash stock to 44.8%, but values future earnings at a 100% payout. The fleet's own sensitivity run says fixing this costs −14% to −22%. A second problem runs the other way: the ~850 bn 2026 investment plan has no defined treatment under the new haircut.

**Checks I redid myself (all matched)**
- **Net financial position 1,466.16:** cash 2,707.864 + held-to-maturity deposits 868.129 + 0.432 − borrowings 620.677 = 2,955.75. Net operating working capital (assets 3,679.68 − liabilities 5,169.27) = −1,489.59. 2,955.75 − 1,489.59 = 1,466.16. Customer advances and the warranty provision are already netted out, so nothing is counted twice.
- **Cash haircut f:** (1.024% + 0.0909)/(13.5% + 0.0909) = 0.4477, as reported.
- **Dividends:** the audited 2025 cash-flow statement figures, 35.776 and 27.850 bn, over 79.726m shares give 448.7 and 349.3 đ/share, matching BQ `div1y`.
- **Revenue median 2019–25:** 5,432.5 from the BQ CSV, as reported.
- **Rev4 control leg:** reproduces 32,376.

**Where the centre could be too HIGH (fails, material)**
- **Earnings are treated as fully paid out while cash is treated as trapped.** The same evidence covers both:
  - Record parent profit of 492 bn in 2025 was split only into the development fund (242) and the bonus/welfare fund (31); no cash dividend.
  - The AGM chose a 31.7% stock dividend instead.
  - Over 2017–25, total dividends were about 225 bn against cumulative profit of about 567 bn.
  - At a 38% payout the centre is 18,092; at 0% (as in 2025) it is 16,323.
- **The report's defence is weak.** It argues that the planned 1,500–2,500 bn capital raise shows the business absorbs retained capital. That would only support NOPAT/r if retained capital earns r. The cash stock is assumed to earn 1.28%, and a company holding ~1.47 trillion of excess net cash while raising more equity is not short of working capital. Applying the evidence to one side only breaks the user's two-sided rule.
- **The 1.68%-of-revenue warranty reversal add-back has the same problem.** It is non-cash, so it piles up as cash that is also "trapped", yet it is valued at /r with no haircut.

**Where the centre could be too LOW (open, material)**
- **The ~850 bn development plan and the capital raise are marked "NPV0_BOOK".** Under the new haircut that label means two different things:
  - If NPV0 means the cash becomes a project worth its book value, spending it lifts that cash from 0.448 to 1.0, about **+5,300 đ/share** (+25%, my estimate).
  - If the project's returns are trapped too, the value stays where it is.
- The direction is unknown and the scale is far above the 5% threshold, so it cannot be left unstated.
- Separately, the "0 principal releases in 9 years" framing hides a pattern. In 2018–23 dividends of 1,800 đ/share were paid while cumulative 2017–22 profit was about −15 bn. The company did pay out of the cash pile, in small amounts, so the release hazard p is not a clean zero-event series.

**Other checks**
- **Legal/scandal:** pass. The qualified audits 2023–25, the unapproved equitization (CPH) settlement, the guarantee to Lilama 69-1 and the ~330 bn of overdue subsidiary loans are all listed as warnings with sensitivities. Those loans are already inside consolidated borrowings.
- **Comps/SOTP:** pass. No peer comp is used. The release hazard p = 1/11 is an estimator choice and is labelled as an estimate, with the full grid shown.
- **Revision flip-flop:** partial fail. The centre moved 24.6k → 28.8k → 32.4k → 21.0k. The key evidence (stock dividend despite ~3.6 trillion of cash, the development-fund allocation) was already in rev2 (`REPORT.md:32`, `:218`). What drove the change is mostly a new model structure, not new facts.
- **Price-blind:** the report quotes a reference price of 33,300 and labels the stock expensive. I ignored that and judged only the model.

<<<VERDICT_JSON>>>
{
  "case_topic": "LLM (Lilama, UPCoM) — DD rev5, tâm 20.978 đ/cp (REPORT_rev5.md)",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — ngoại trừ KT 2023–25, CPH chưa quyết toán, bảo lãnh 69-1 (496,97), vay quá hạn công ty con ~330 đều nêu WARNING kèm độ nhạy (§7); không thấy tín hiệu thu hồi tài sản/giấy phép trong tài liệu được trích",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; trục quyết định p=Laplace 1/11 là lựa chọn estimator, có gắn nhãn ước lượng và có lưới MLE…3/N (11.612…28.177)",
    "data_provenance": "pass — tính lại NFP 1.466,16 từ bs_q3_bn (2.955,75 − 1.489,59), f_cash 0,4477, cổ tức 2024/25 = 448,7/349,3 đ/cp khớp LCTT KT25, trung vị DT 2019–25 5.432,5 khớp BQ; cổ tức 2017–23 chỉ có nguồn BQ (đã tự khai)",
    "liquidity_capacity_realism": "na — không đề xuất vào lệnh ở mức hiện tại; trần 2% NAV + ADV ~0,45 tỷ đã nêu",
    "confirmation_bias_flipflop": "fail (một phần) — 24.599→28.834→32.376→20.978 trên cùng hồ sơ; bằng chứng chủ chốt (cổ tức cổ phiếu 31,7% dù cầm ~3,6 nghìn tỷ, trích ĐTPT) đã có ở rev2 REPORT.md:32,:218 ⇒ biến động đến từ cấu trúc mô hình chứ chủ yếu không phải dữ kiện mới",
    "exit_discipline_gap": "na — không có claim sizing để vào lệnh; có điều kiện đổi nhận định hai chiều (§8)",
    "missing_items": "fail — (1) LN tương lai chưa áp cơ chế mắc kẹt: cùng bằng chứng với khối tiền (LN 2025 492 tỷ chia 0 tiền, cổ tức CP 31,7%, cổ tức lũy kế 2017–25 ~225 tỷ / LN ~567 tỷ) nhưng base giữ NOPAT/r với payout 100%; độ nhạy của chính báo cáo: payout 38% ⇒ 18.092 (−13,8%), 0% ⇒ 16.323 (−22%) ⇒ định lượng được, trọng yếu; dòng cộng lại bảo hành 1,68% DT cũng tích thành tiền nhưng định giá ở /r. (2) Kế hoạch ĐTPT 2026 ~850 tỷ + tăng vốn 1.500/2.500 tỷ gán NPV0_BOOK — không xác định được dưới khung f: nếu giải ngân ở mức NPV0 thì tiền đó chuyển từ f=0,448 lên 1 ⇒ ~+5.300 đ/cp (ước lượng); nếu lợi nhuận dự án cũng bị kẹt ⇒ 0. Chưa rõ chiều nhưng trọng yếu. Đạt: số cổ phiếu (79.726.104 @30/09/26), quỹ KTPL (83,1 + 6,28%), có KT 2025, NCI, cổ tức CP chờ thực hiện (đã quy đổi /1,317)"
  },
  "independent_verification": "NFP 1.466,16 = (2.707,864+868,129+0,432−620,677) − (3.679,677−5.169,268) — khớp. f_cash=(0,01024+0,0909)/(0,135+0,0909)=0,4477 — khớp. Cổ tức 35,776/27,850 tỷ ÷ 79,726tr cp = 448,7/349,3 — khớp BQ div1y. Doanh thu/LN năm từ bq_fin_LLM.csv: trung vị DT 2019–25 5.432,5 khớp; LN lũy kế 2017–25 ≈567 tỷ so với cổ tức ≈225 tỷ (tôi tự tính).",
  "killer_objection": "Rev5 dùng lịch sử chia cổ tức tiền ít để chiết khấu khối tiền xuống 44,8%, nhưng lại coi LN tương lai được chia đủ 100% (NOPAT/r), dù cùng bằng chứng đó (LN kỷ lục 2025 chia 0 tiền, chọn cổ tức cổ phiếu) áp thẳng lên dòng LN. Sửa cho nhất quán, theo độ nhạy của chính báo cáo, kéo tâm về 16.3k–18.1k (−14% đến −22%). Ngược chiều, xử lý NPV0 cho khoản ĐTPT ~850 tỷ không xác định dưới khung f và có thể làm tâm tăng ~+25%.",
  "recommended_followups": [
    "Áp một quy tắc phân phối duy nhất cho cả khối tiền và dòng LN (vd payout từ lịch sử 2017–25 hoặc cùng hazard p) — hoặc đưa bằng chứng độc lập (hồ sơ suất sinh lời trên vốn tái đầu tư) cho thấy LN giữ lại sinh lời bằng r",
    "Định nghĩa NPV0_BOOK dưới khung f: tiền giải ngân cho ĐTPT 850 tỷ / tăng vốn được định giá ở f=1 hay f_cash; lấy NQ ĐHĐCĐ 2026 đầy đủ (danh mục dự án, giá phát hành, đối tượng mua) để xác định",
    "Định nghĩa lại sự kiện p: 2018–23 có chi cổ tức vượt LN (1.800 đ/cp so với LN 2017–22 ≈ −15 tỷ) — ước lượng p/y theo dòng tiền thực trả cho cổ đông thay vì nhị phân 'phân phối gốc'",
    "Đối chiếu div1y 2017–23 với LCTT từng năm"
  ],
  "summary": "Số học và nguồn gốc dữ kiện của rev5 đều đúng: NFP, f_cash, đối chiếu cổ tức và trung vị doanh thu đều khớp khi tôi tự tính lại. Lỗi nằm ở chỗ lập luận không nhất quán. Mô hình áp bằng chứng 'cổ đông thiểu số không nhận được tiền' lên khối tiền đang có nhưng không áp lên LN tương lai, dù LN kỷ lục 2025 không chia đồng tiền nào và AGM chọn cổ tức cổ phiếu. Sửa cho nhất quán thì độ nhạy của chính báo cáo cho −14% đến −22%. Chiều ngược lại cũng còn hở: khoản ĐTPT ~850 tỷ và kế hoạch tăng vốn gán NPV0 nhưng không xác định dưới khung f, đọc theo hướng có lợi có thể +~25%. Hai khoản trọng yếu, khác chiều, chưa được giải quyết ⇒ chưa thể coi 20.978 là tâm đã vững; dải hợp lý cần thể hiện rõ hai trục này."
}
<<<END_VERDICT>>>