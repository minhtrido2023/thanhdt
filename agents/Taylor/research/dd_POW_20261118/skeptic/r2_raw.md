**Verdict: INCONCLUSIVE, medium confidence.** The arithmetic holds and the QCVN 19 fix is real new information. But one material item can't be traced (PPA and gas-supply terms for CM1&2 and NT1), and the model has a small downward bias it doesn't disclose. I did not look up any market price. The report states one (13.350 đ), and I left it out of the judgement.

**What I re-checked myself**
- **The centre:** (31.394,5×0,08/0,135 + 9.000 + 2.740 − 2.255) / 3.067,85 = **9.156 đ/cp** before the liquidity discount. That matches the report. The three equity blocks add up exactly to parent equity of 43.134,5.
- **The cost of the QCVN 19 emissions upgrade if it can't be passed into the power price (P0):** I rebuilt it by hand at r=13,5% and got about **3.883 bn VND**. The report says 3.888, so it matches.
- **Share count:** 3.067.845.688 shares, confirmed in the 2025 annual report and the audited 2025 consolidated and parent statements.
- **LNG figures:** the 13/10 disclosure confirms 23,8 million MMBtu delivered in 8 cargoes and the 20,7 million MMBtu/year term contract for 2027–31. But that disclosure says "giao nhận" (delivered), not burned as the report puts it. And 2026 deliveries say little about 2027–31 take-or-pay risk, which depends on how much NT3&4 actually runs.

**Ways the centre could be too high**
- **QCVN 19 at the gas plants (CM1&2, NT1, 1.950 MW):** left out of base. The consultancy tender covers "các nhà máy nhiệt điện" (the thermal plants) in general. The report's own sensitivity is −1,3% to −2,5%.
- **VA1 compliance cost:** a one-off capex with opex running forever ignores replacing the equipment later.
- **Price-pass-through odds (0,40/0,36/0,24):** borrowed from the QTP case and subjective.
- **NT3&4 at book value (NPV=0):** depends on an LNG price formula that is not public.
- **Financing of new projects:** Quỳnh Lập LNG is about 60.000 bn VND, plus Vũng Áng III, Nậm Sum 3 and Lâm Sơn. The equity needed is large next to 43k bn of parent equity. At NPV=0 this is neutral, but it is not discussed.

**Ways the centre could be too low**
- **Retroactive receivable from EVN/EPTC (~2.755 bn pre-tax):** already in equity, but valued like legacy equity at ROE/r = 0,593×. It is an approved near-cash claim and should be worth close to 1,0× before any collection haircut. My rough estimate is +3% (about +290 đ/cp, assuming 20% tax).
- **Inconsistency in the collection test:** the 30%-uncollectible sensitivity takes the hit at about 1,0×, while base values the claim at 0,593×.
- **Finite plant life (+11 to +18%):** kept out of base on reasonable grounds.

**Items a sector analyst would expect that are missing**
- **PPA expiry and gas-supply terms for CM1&2 (2008) and NT1 (2009):** not verified. Their expiry likely falls inside the forecast horizon, and the model values legacy capital in perpetuity. This item alone forces INCONCLUSIVE.
- **Related-party transaction values:** unreadable (bad OCR of the 2025 audit note).
- **Remaining equitisation settlement owed to PVN:** unverified; the report only runs a sensitivity.
- **Covered:** audit opinion, share count, welfare fund and new-project capex at book value.

**Before CONFIRMED:**
1. Get the PPA and gas-supply terms for CM1&2 and NT1 (pvpower.vn, EVN/ERAV filings, the PV GAS annual report) and model legacy capital on its real life.
2. Re-OCR or read by hand the 2025 audit's related-party note.
3. Treat the retroactive receivable as a near-cash claim (1,0× minus a collection haircut), outside the ROE/r block, and use the same basis in the collection sensitivity.
4. Re-check VA1's emissions equipment and update the QCVN 19 size when the investment proposal comes out (Q1/2027).
5. State how equity for Quỳnh Lập and Vũng Áng III will be raised.

<<<VERDICT_JSON>>>
{
  "case_topic": "POW — DD rev3 (23/11/2026), tâm 9.064 đ/cp, vùng [6.438; 11.691]",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không khẳng định fear-buy/§2.5",
    "scandal_migration_risk": "pass — mục WARNING (quyết toán CPH chưa duyệt, Deloitte FY25 chấp nhận toàn phần + đoạn nhấn mạnh, không thấy khởi tố trong 83 CBTT) được nêu và để ngoài base; số CPH còn phải nộp chưa kiểm chứng, đã chạy độ nhạy −2,6%",
    "optimistic_comp_sotp_bias": "pass có lưu ý — capex/opex QCVN19 của VA1 lấy 1:1 từ một tương tự duy nhất (FS QTP 3.485 + 572/năm), có gắn nhãn ước lượng, độ nhạy ×0,5/×1,5; trọng số P0/P50/P100 0,40/0,36/0,24 mượn từ QTP r3b, mang tính chủ quan; SOTP NT3&4 + dự án mới theo sổ, NPV=0 (quy tắc V4) — trung tính, nhưng nhu cầu vốn Quỳnh Lập (~60.000 tỷ TMĐT, CBTT 20/05) + Vũng Áng III so với VCSH mẹ 43.134 chưa được bàn",
    "data_provenance": "pass có lưu ý — số cp 3.067.845.688 khớp BCTN25/KT25 HN và riêng; tâm và PV P0 tính lại khớp; khẳng định ToP ở A2 ghi 23,8tr MMBtu là 'mức đốt thực' trong khi CBTT 13/10 ghi 'giao nhận 8 chuyến' (giao vào kho, không phải đốt); khối lượng hợp đồng 20,7tr/năm 2027–31 khớp",
    "liquidity_capacity_realism": "na — sizing có điều kiện theo giá; chiết khấu thanh khoản 1% từ ADV 63,3 tỷ (đo rev2), không chấm theo kiểu fear-buy",
    "confirmation_bias_flipflop": "pass — rev2 9.792 → rev3 9.064 (−7,4%), chênh lệch do một khoản mục mới có nguồn (CBTT 19/10 gói thầu tư vấn QCVN19 2,984 tỷ) theo đúng luật D3; nhãn không đổi; không mở dd_price_zones.json (theo ràng buộc mù), so sánh qua REPORT.md rev2",
    "exit_discipline_gap": "na — không có khẳng định fear-buy; có mốc khoá trước T1–T5 và điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (không định lượng được) — (1) hạn PPA/hợp đồng khí CM1&2 (2008) và NT1 (2009) chưa kiểm chứng, nhiều khả năng rơi trong chân trời dự báo, trong khi mô hình coi vốn di sản vĩnh viễn — trọng yếu; (2) giá trị giao dịch bên liên quan không đọc được (OCR hỏng); (3) số CPH còn phải nộp PVN chưa biết; (4) QCVN19 cho nhà máy khí 1.950 MW ngoài base (độ nhạy −1,3…−2,5%); (5) chiều RẺ: ~2.755 LNTT hồi tố (khoản phải thu đã duyệt) bị định giá ở ROE/r=0,593× thay vì ~1,0× ⇒ base thấp khoảng +3% (≈+290 đ/cp, ước lượng), và độ nhạy thu tiền ở A10 lại tính ~1,0× — không nhất quán. Đã có: kiểm toán FY25, số cp, quỹ khen thưởng phúc lợi, capex dự án mới theo sổ."
  },
  "independent_verification": "Tính lại tâm (31.394,5×0,08/0,135 + 9.000 + 2.740 − 2.255)/3.067,85 = 9.156 trước chiết khấu — khớp. Tự dựng lại PV P0 QCVN19 (capex 30/45/25% 2029–31, opex 572×0,8 vĩnh viễn từ 2032, lá chắn khấu hao 15 năm, r 13,5%, mốc 30/09/2026) ≈ 3.883 tỷ so với báo cáo 3.888 — khớp. Số cp khớp BCTN 2025 và BCTC KT 2025. Khối lượng LNG khớp CBTT 13/10, nhưng ghi nhãn sai (giao nhận ≠ đốt).",
  "killer_objection": "Toàn bộ khối vốn di sản (31.394 tỷ ≈ 61% giá trị trước trừ khoản) được định giá như dòng vĩnh viễn ở ROE 8%, trong khi hạn PPA và nguồn khí của CM1&2/NT1 — nhà máy 17–18 năm tuổi — chưa được kiểm chứng; nếu hợp đồng hết hạn trong chân trời dự báo, dấu và độ lớn chênh lệch so với base không xác định được (đời hữu hạn với tái đầu tư NPV=0 đẩy lên +11…+18%; mất PPA mà không tái ký đẩy xuống).",
  "recommended_followups": [
    "Lấy hạn PPA/hợp đồng khí của CM1&2, NT1 (pvpower.vn, ERAV/EVN, BCTN PV GAS) và mô hình hoá vốn di sản theo đời thật",
    "OCR lại hoặc đọc tay thuyết minh bên liên quan BCTC KT 2025",
    "Tách khoản phải thu hồi tố ra ngoài khối ROE/r, định giá ~1,0× trừ chiết khấu thu hồi; dùng cùng cơ sở cho độ nhạy ở A10",
    "Xác nhận VA1 đã có FGD/SCR chưa; cập nhật quy mô khi báo cáo đề xuất đầu tư QCVN19 công bố (Q1/2027)",
    "Nêu rõ cách huy động vốn chủ cho Quỳnh Lập/Vũng Áng III (phát hành mới, pha loãng) dù NPV=0"
  ],
  "summary": "Rev3 thêm đúng khoản capex tuân thủ QCVN 19 của VA1 làm dòng tiền ra và số học tái lập được: tâm 9.156 trước CK và PV P0 ~3.883 so với 3.888 đều tự tính lại khớp, số cổ phiếu khớp BCTC kiểm toán. Chưa CONFIRMED được vì một hạng mục ngành điện trọng yếu chưa kiểm chứng — hạn PPA/nguồn khí CM1&2 và NT1 — trong khi mô hình coi vốn di sản vĩnh viễn. Hai chiều: tâm có thể quá CAO (QCVN19 nhà máy khí ngoài base, công thức giá LNG NT3&4 không công bố, trọng số bù giá chủ quan) và cũng có thể quá THẤP (khoản phải thu hồi tố đã duyệt bị định giá 0,593× thay vì ~1,0×, khoảng +3% ước lượng; đời máy hữu hạn +11…+18%). Báo cáo còn gọi 23,8tr MMBtu là 'đốt thực' trong khi CBTT chỉ ghi giao nhận. Không tra hay dùng giá thị trường."
}
<<<END_VERDICT>>>