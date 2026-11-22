**Verdict: REFUTED, medium confidence.** The report's direction ("centre well below the bands") holds up. Its centre of 6.342 đ/cp before the liquidity discount, 6.159 after, does not. One undisclosed modelling choice, worth more than 5% of the centre, pushes it too low. Several smaller items push it too high.

I ignored the market price that appears in the report text. I did not open `dd_price_zones.json`, so attack 6 is judged only against r1/r2/r3 in the report's own folder.

**What I checked myself**
- Re-ran `dcf_tta_r3.py` (md5 `5ff89722…` matches). It reproduces A/B/B′/C = 12.651 / 8.821 / 5.559 / 1.175 and the centre 6.342.
- From the Q3/2026 scan (note page 18), the report's figures match:
  - receivable from EVN's power-purchasing company (EPTC): 399,628 bn, up from 237,660 bn
  - receivable from the Northern power corporation: 43,979 bn
  - term deposits 116 bn (BIDV 70 + MB 46); loans to the related company Trường Thành 12,5 + 2,5 bn
- From the 2026 AGM resolution (Điều 6), two more matches:
  - profit share paid to the business cooperation contract (HTKD) partners in 2025: 31,003 bn
  - bonus/welfare funds: 12,037 + 2,000 bn, which fits the model's "6% of profit + 2"
  - dividend 0%
- The EPTC payment ratios recompute correctly: 55,4% for 9M/2025 and 49,2% for 9M/2026.
- The PDFs have no text layer, so I checked against the page images.

**Too low (the decisive point)**
- **Hydro revenue is held flat at 330 bn/year in nominal terms until 2060, while hydro costs grow 3%/year and overhead also grows 3%/year.** That amounts to the tariff falling about 3%/year in real terms for 34 years, on top of the −15% cut after 2036. No report revision mentions it.
  - If hydro revenue rises 2%/year, the centre goes **6.342 → 7.728 (+22%)**.
  - At 3%/year it goes to 8.545.
  - At 1%/year it would be roughly +11% (my estimate, not run).
- Ngòi Hút 2, the largest hydro plant at 48 of 82 MW, still has its pricing mechanism marked "chưa kiểm" (unchecked) in r1.
- **The solar feed-in tariffs (FIT) are priced in USD, but the forecast holds the exchange rate fixed at 25.755.** The back-pay calculation uses the historical, rising rate, so the two halves of the model are inconsistent. A +2%/year exchange rate on FIT revenue moves the centre **6.342 → 6.873 (+8,4%)**. The fixed post-FIT price is not indexed either.

**Too high**
- The ~330 bn "excess receivable" from EPTC includes VAT; the report itself multiplies by 1,08 in §2. Netting it against the back-pay ex-VAT gives 6.205 (**−2,2%**).
- That 330 is itself an estimate. If it is never collected, the centre falls to 4.494 (−29%).
- The Phương Mai wind associate (99,4 bn) is carried at book value with no financial statements. That is about 557 đ/cp, roughly 9% of the centre.
- The BIDV 70 bn deposit is pledged against a guarantee facility but counted as free cash.
- The hydro base comes from 9M/2026, which had favourable rainfall.

**Missing items (attack 8)**
- Not quantified and left out of the scenarios: Bầu Ngứ's missing operating licence under the Irrigation Law, which r1 raised.
- Also not quantified: further equity calls for the Phước Hoà pumped-storage project; 19,9 bn was spent in 9M/2026 alone.
- Never checked: the term of the HTKD contracts, and the hydro water-use and land licence terms through 2060.
- Small: Q4/2026 cash flow is left out. Net of the Q4 debt repayment it is about −113 to +121 đ/cp, by scenario.

**Next steps**
1. Add a hydro tariff indexation case (0/1/2%) and index the FIT revenue to the exchange rate, then recompute the centre and the bands.
2. Get Ngòi Hút 2's power purchase agreement and pricing mechanism, plus the Pá Hu/NH2A pricing history from 2016 to 2026.
3. Net the 330 bn receivable of VAT, and derive the 330 from the actual EPTC billing cycle.
4. Get Phương Mai's financial statements or apply a haircut, and exclude the pledged 70 bn deposit.
5. Write the Bầu Ngứ licence risk and Phước Hoà's equity commitment into the scenarios or the HARD ABANDON list.

<<<VERDICT_JSON>>>
{
  "case_topic": "TTA — DD REPORT_r3 (dd_TTA_20261120), tâm V1 6.342 trước TK / 6.159 sau TK",
  "verdict": "REFUTED",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; r2 Phụ lục A đã chạy §2/§2.5 ra NON, r3 không đưa claim fear-buy/sizing",
    "scandal_migration_risk": "pass (có lưu ý) — dòng tiền bên liên quan (96,64 tỷ qua Chủ tịch, vay BLĐ 139,25→0, cho vay Trường Thành 15 tỷ, thuê biệt thự Chủ tịch) được nêu WARNING có nguồn trang; nhưng vấn đề giấy phép Luật Thuỷ lợi của Bầu Ngứ (r1 bảng §3) bị rơi khỏi r2/r3, không vào kịch bản hay HARD ABANDON",
    "optimistic_comp_sotp_bias": "fail nhẹ (hai chiều) — không có comp; cấu phần SOTP: Phương Mai 99,4 tỷ (≈557 đ/cp, ~9% tâm) để giá gốc−DP, không có BCTC; tiền gửi BIDV 70 tỷ đang cầm cố bảo lãnh tính như tiền tự do; cho vay bên liên quan 15 tỷ tính đủ mệnh giá",
    "data_provenance": "pass (có lưu ý) — đã đối chiếu ảnh scan: phải thu EPTC 399,628/237,660, EVNNPC 43,979, HTM 116 + 12,5 + 2,5, HTKD 2025 31,003, quỹ 12,037+2,0, cổ tức 0% đều khớp; giả định chịu lực vẫn là ước lượng có nhãn: phải thu vượt 330, sản lượng thiết kế 98/85 GWh, lịch trả gốc, loại tỷ giá hồi tố",
    "liquidity_capacity_realism": "na — báo cáo không đề xuất cỡ vị thế; chiết khấu thanh khoản theo quy ước fleet (2,89%, cận dưới ADV 68 phiên 3,87%) đã khai",
    "confirmation_bias_flipflop": "pass có điều kiện — so trong thư mục: r1 8.040 → r2/r3 6.342 trước TK, đều đi xuống theo đính chính của skeptic; B′ có căn cứ (KL TTCP nêu cả hai nhà máy), nhưng bộ trọng số chốt là bộ THẤP NHẤT trong ba bộ đã thử và neo vào N=2 kỳ thanh toán của một người mua — luật 02-03/11 đòi căn cứ độc lập cho điều chỉnh đi xuống; r3 có khai đường thử. Không mở dd_price_zones.json theo ràng buộc của brief",
    "exit_discipline_gap": "na — không có claim sizing; vẫn có 5 điều kiện HARD ABANDON (#3 đã sửa: DSCR sau thuế + HTKD < 1,00)",
    "missing_items": "fail — (1) KHÔNG ghi nhận: DT thuỷ điện phẳng danh nghĩa 330 tới 2060 trong khi chi phí thuỷ điện và G&A +3%/năm ⇒ giá thực giảm ~3%/năm suốt 34 năm, chưa từng nêu/kiểm; DT thuỷ điện +2%/năm ⇒ tâm 6.342→7.728 (+22%), có định lượng >5% ⇒ REFUTED theo hướng QUÁ THẤP; cơ chế giá Ngòi Hút 2 vẫn 'chưa kiểm'; (2) FIT tính theo USD nhưng tỷ giá tương lai cố định 25.755 (trong khi hồi tố dùng tỷ giá lịch sử tăng) ⇒ +2%/năm tỷ giá: 6.873 (+8,4%); (3) phải thu vượt 330 gồm VAT ⇒ −137 đ/cp (−2,2%); (4) vốn chủ phải góp thêm cho Phước Hoà không mô hình hoá (19,9 tỷ trong 9T) — không định lượng được; (5) rủi ro giấy phép Thuỷ lợi Bầu Ngứ — không định lượng được; (6) thời hạn HTKD, giấy phép nước/đất thuỷ điện tới 2060 — chưa kiểm; (7) dòng tiền Q4/2026 sau trả gốc ≈ −113…+121 đ/cp — nhỏ. Đạt: số cổ phiếu 178,559 tr (khớp ngược EPS 849,10 in sẵn), không phát hành/ESOP trong NQ ĐHĐCĐ 2026, kiểm toán 2025 chấp nhận toàn phần và có mặt, quỹ khen thưởng phúc lợi và HTKD đã mô hình hoá, DSCR/lịch nợ có"
  },
  "independent_verification": "Chạy lại dcf_tta_r3.py (md5 5ff89722e26d04ad7f808cd170285a19): A/B/B′/C 12.651/8.821/5.559/1.175, tâm 6.342 — khớp. Đối chiếu ảnh BCTC Q3/2026 trang thuyết minh 18: phải thu EPTC 399,628 / đầu năm 237,660, EVNNPC 43,979, tiền gửi kỳ hạn 116 (BIDV 70, MB 46), cho vay Trường Thành 12,5+2,5 — khớp. NQ ĐHĐCĐ 2026 Điều 6: HTKD 2025 31,003 tỷ, quỹ 12,037+2,0, cổ tức 0% — khớp cấu trúc mô hình. Tính lại tỷ lệ EPTC trả: 55,4% / 49,2% — khớp. Độ nhạy tự chạy: DT thuỷ điện +2%/năm → 7.728; tỷ giá FIT +2%/năm → 6.873; phải thu vượt trừ VAT → 6.205; phải thu vượt = 0 → 4.494.",
  "killer_objection": "Tâm 6.342 dựa trên giả định chưa khai báo: doanh thu thuỷ điện cố định danh nghĩa 34 năm trong khi chi phí lạm phát 3%/năm (và FIT theo USD bị khoá tỷ giá). Chỉ cần chỉ số hoá giá 2%/năm cho thuỷ điện là tâm +22% (7.728) — lớn hơn mọi đính chính r2→r3 cộng lại — nên mức số và các ngưỡng vùng hiện chưa đáng tin, dù hướng kết luận vẫn có thể giữ.",
  "recommended_followups": [
    "Thêm tham số chỉ số hoá DT thuỷ điện (0/1/2%) và chỉ số hoá tỷ giá cho FIT; tính lại tâm và các ngưỡng vùng",
    "Lấy PPA/cơ chế giá Ngòi Hút 2 (>30 MW) và lịch sử biểu giá chi phí tránh được 2016-2026 của Pá Hu/NH2A để neo tốc độ tăng giá",
    "Trừ VAT khỏi phải thu vượt 330 và dựng 330 từ chu kỳ hoá đơn EPTC thực, không phải '~70 bình thường'",
    "Phương Mai: lấy BCTC liên kết hoặc áp haircut; loại 70 tỷ tiền gửi BIDV đang cầm cố khỏi tiền tự do",
    "Đưa rủi ro giấy phép Luật Thuỷ lợi Bầu Ngứ và cam kết vốn chủ Phước Hoà vào kịch bản hoặc danh sách HARD ABANDON",
    "Kiểm thời hạn HTKD và giấy phép tài nguyên nước/đất thuỷ điện trong chân trời tới 2060"
  ],
  "summary": "Số liệu nguồn của r3 trung thực: phải thu EPTC, tiền gửi, HTKD, quỹ khen thưởng phúc lợi và cổ tức khớp với ảnh BCTC/NQ ĐHĐCĐ, mô hình tái lập đúng 6.342. Nhưng mô hình có một thiên lệch có hệ thống theo chiều QUÁ THẤP chưa được khai báo ở vòng nào: doanh thu thuỷ điện cố định danh nghĩa tới 2060 trong khi chi phí tăng 3%/năm, và FIT theo USD bị khoá tỷ giá. Chỉ số hoá thuỷ điện 2%/năm đẩy tâm +22%, tỷ giá 2%/năm cho FIT +8%. Chiều ngược lại có các lỗi nhỏ hơn: phải thu vượt gồm VAT (−2%), Phương Mai để giá sổ sách chưa kiểm (~9% tâm), tiền gửi đang cầm cố, cơ sở thuỷ văn năm thuận. Rủi ro giấy phép Bầu Ngứ và cam kết vốn Phước Hoà vẫn chưa định lượng. Mục thiếu đã định lượng >5% tâm ⇒ REFUTED về mức số và ngưỡng vùng; hướng 'tâm thấp hơn nhiều so với các vùng nêu' có thể vẫn đúng nhưng phải tính lại."
}
<<<END_VERDICT>>>