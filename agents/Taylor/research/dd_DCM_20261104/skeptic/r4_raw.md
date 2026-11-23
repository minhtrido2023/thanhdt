Đang viết kết luận phản biện. Đã đối chiếu trang TM25 trong BCTC kiểm toán 2025 và tính lại hệ số quỹ KH&CN.

**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Các số tôi kiểm lại đều khớp nguồn. Ba khoản tính toán của rev9 cũng tính lại ra đúng. Tuy nhiên, tâm 27.393 vẫn dựa trên ba giả định chưa có nguồn, và mỗi giả định có thể làm tâm lệch 4–18%. Các giả định này có tác động lớn nhưng không gán được xác suất, nên theo luật DD_GENERAL kết luận phải là INCONCLUSIVE.

**Những gì đã tự kiểm lại**
- **Quỹ KH&CN (TM25 BCTC hợp nhất kiểm toán 2025, xem trực tiếp `png_r7/kt25_p37.png`):** trích 2024 là 44,78, năm 2025 là 187,99. Sử dụng 39,50 / 75,82. Chuyển sang TSCĐ 11,80 / 13,51. Phần đã thành TSCĐ còn 27,74. Tất cả khớp báo cáo.
- **Đối chiếu số dư tiền của quỹ:** 829,47 + 249,63 − ≈47,5 ≈ 1.031,6, khớp `khcn_cash` 1.031,63.
- **Lớp trích từ 2023 trở về trước theo FIFO:** 737,32 − 51,30 − 89,33 − 47,5 = 549,2. Khớp.
- **Hệ số v tính lại bằng tay:** v(10%, L=2,485) = 0,894 × 0,9463^2,485 = 0,779, tức số dư mất 22,1%. v(20%, L=5) = 0,788 × 0,9463^5 = 0,598. Cả hai khớp `model_r9_out.txt`.

**Các điểm yếu chưa giải quyết**

*Theo chiều tâm quá CAO:*
- **Cơ sở pháp lý cho việc hoàn nhập quỹ (T4).** Chưa kiểm được doanh nghiệp không phải DNNN có được hoàn nhập phần quỹ bị thu hồi hay không. Báo cáo lập luận rằng nếu không được thì phải chi cho thiết bị, coi như NPV=0, nên v vẫn là cận thận trọng. Điểm yếu:
  - Đây là chi tiêu bắt buộc. Luật user 22/11 coi khoản chi tuân thủ là dòng tiền ra, không phải NPV=0.
  - Thực tế DCM chỉ dùng 51–89 tỷ/năm, trong khi trích 188–250 tỷ. Như vậy công ty không hấp thụ được quỹ vào thiết bị.
  - Nếu đọc theo rev7 (mất 100%), tâm giảm 2.392, tức −8,7%.
- **Hồi quy đoán cao hai năm kiểm toán gần nhất.** Phần dư trung bình 2024–25 là −153 tỷ/năm (cửa sổ 2021–25) và −163 tỷ/năm (cửa sổ bỏ 2022). Tôi ước lượng điều này làm tâm cao hơn khoảng 1,2–1,3k, tức −4,4…−4,6%. Đây là ước lượng của tôi (×0,8 thuế ×0,94 quỹ phúc lợi ×10,40 đ/cp mỗi tỷ/năm), chưa chạy mô hình.
- **Thời hạn thuê đất nhà máy Cà Mau chưa kiểm được.** Nếu dừng năm 2047, tâm giảm 994; dừng năm 2042 giảm 1.873 (tức −3,6…−6,8%).
- **Giá khí sau 2034.** Phần lõi coi cấu trúc giá hiện hành là 100% xác suất mãi mãi. Trong khi chính báo cáo ghi sau 24/4/2032 không còn khối lượng cam kết, và SĐBS 12 mới là dự thảo. Mốc PSC PM3 tới 2047 là hợp đồng thượng nguồn, không phải giá bán khí cho DCM. Biến thể có trọng số cho tâm 22.574, tức −17,6%.
- **Khoản 332 tỷ bị phong toả tại MBV** vẫn tính đủ giá trị trong phần lõi. Ảnh hưởng −627 (−2,3%), dưới ngưỡng trọng yếu.

*Theo chiều tâm quá THẤP:*
- Phương án 4 cửa sổ hồi quy cho +2.024. Thuế xuất khẩu 0% với P=0,55 cho +1.033. Cả hai đều nằm ngoài phần lõi.
- Giả định "≤ 0,598" có thể thấp nếu quỹ thay được capex duy trì M.
- Tóm lại các rủi ro gần như cân hai phía. Tâm không lệch hẳn một chiều.

**Lịch sử các lần sửa (đọc trong REPORT_r5…rev9, không mở `dd_price_zones.json` theo ràng buộc mù):** tâm đi r3 27.021 → r4 23.644 → r5 24.326 → r6 24.822 → rev7 24.822 → rev8 26.780 → rev9 27.393.
- Từ rev7 đến nay mọi lần sửa đều đi lên, và nhãn đổi từ TRÊN vùng sang TRONG vùng.
- Mỗi lần sửa đều do skeptic yêu cầu và có nguồn. Riêng rev9 tăng ít hơn mức skeptic r3 ước tính (+613 so với +0,95…+2,49k), nên không giống sửa theo hướng mình muốn.
- Có một sai sót trong phần công bố: báo cáo nói giá được biết "từ pha rev7", nhưng r5 và r6 đã ghi giá 33.000 và 32.100.

Bỏ qua mọi giá thị trường xuất hiện trong báo cáo (30.400, 0,85×tâm…). Tôi không tra giá.

<<<VERDICT_JSON>>>
{
  "case_topic": "DCM (PVCFC) — DD định giá REPORT_rev9 (tâm 27.393 đ/cp sau CK)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo tự ghi không đủ điều kiện fear-buy §2.5; không có claim fear-buy",
    "scandal_migration_risk": "pass — §9 vẫn giữ WARNING (HĐ khí khép kín PVN→PV GAS→DCM, HĐQT được uỷ quyền sửa nội dung cơ bản, SĐBS 12 mới là dự thảo, 332 tỷ phong toả tại MBV, phải thu PVN tăng); tra tin 05–23/11 không thấy sự kiện mới, nhưng chưa mở trực tiếp hose.vn/pvcfc.com.vn",
    "optimistic_comp_sotp_bias": "fail (mềm) — không dùng comp nhưng phần lõi gán 100% cho cấu trúc giá khí hiện hành sau 2034, dù chính báo cáo ghi sau 24/4/2032 không còn khối lượng cam kết và SĐBS 12 mới là dự thảo; PSC PM3 tới 2047 là hợp đồng thượng nguồn, không phải giá bán cho DCM. Biến thể có trọng số 0,5/0,25/0,25 cho 22.574 (−17,6%). Chiều ngược: 4 cửa sổ +2.024 và thuế XK 0% +1.033 cũng nằm ngoài phần lõi ⇒ cả hai chiều đều có giả định chưa có bằng chứng",
    "data_provenance": "pass có cờ — TM25 KT 2025 xem trực tiếp khớp (44,78/187,99; 39,50/75,82; 11,80/13,51; 27,74); thuế 20% từ 2027, số cổ phiếu 529,4tr, quỹ phúc lợi có nguồn. Cờ: D&A 2018–22 lấy từ BQ (2023 kiểm chéo +1,9%); tỷ lệ trích 2016–22 là ước lượng (a_hist 2021 142,8 / 2022 317,6 là số suy, không phải số BCTC); Y5 = 3% ước lượng; NĐ 320/TT 20 chưa đối chiếu Công báo; việc doanh nghiệp không phải DNNN được hoàn nhập quỹ bị thu hồi CHƯA KIỂM — trong khi đây là tiền đề của +744 (dòng) và của lập luận 'v là cận thận trọng'",
    "liquidity_capacity_realism": "na — sizing hiện 0%; thanh khoản V3 dựa trên ADV DNSE, không có claim khớp lệnh",
    "confirmation_bias_flipflop": "pass có cờ — r3 27.021 → r4 23.644 → r5 24.326 → r6 24.822 → rev7 24.822 → rev8 26.780 → rev9 27.393: mọi lần sửa từ rev7 đều đi lên, nhãn TRÊN→TRONG. Mỗi lần do skeptic yêu cầu và có nguồn; rev9 tăng ít hơn mức skeptic r3 ước (+613 vs +950…+2.490) và khai minh bạch chuyện khoá lại sau lần chạy so giá đầu (27.208). Sai trong công bố: nói giá biết 'từ pha rev7' nhưng r5/r6 đã ghi giá 33.000/32.100",
    "exit_discipline_gap": "na — không mở vị thế; vẫn có các mốc HARD ABANDON/làm lại định giá (§8)",
    "missing_items": "fail (chưa định lượng được xác suất) — (1) năm hết hạn thuê đất nhà máy Cà Mau chưa kiểm: −994…−1.873 (−3,6…−6,8%); (2) thuyết minh TSCĐ / lịch đại tu chưa đọc (S5) — gián tiếp qua trục M, −1.040 mỗi 100 tỷ/năm; (3) chưa kiểm được việc hoàn nhập quỹ KH&CN cho doanh nghiệp không phải DNNN — nếu chi bắt buộc là dòng tiền ra (luật user 22/11) thay vì NPV=0, tới −2.392 (−8,7%); (4) 332 tỷ phong toả MBV vẫn tính đủ giá trị trong lõi −627 (−2,3%, dưới ngưỡng); (5) chưa kiểm đoạn 'vấn đề cần nhấn mạnh' trong ý kiến kiểm toán FY2025 (đặc biệt về 332 tỷ MBV). Đạt: số cổ phiếu (CĐKT Q3/26, không có thưởng/ESOP), quỹ phúc lợi 265,34 + 5,97%/năm, thuế, kiểm toán chấp nhận toàn phần FY2025, khoản một lần, capex dở dang 724 tỷ phân loại growth/duy trì"
  },
  "independent_verification": "Xem trực tiếp TM25 BCTC HN KT 2025 (png_r7/kt25_p37.png): trích 2024 44,78 / 2025 187,99, sử dụng 39,50 / 75,82, chuyển TSCĐ 11,80 / 13,51, số dư đã thành TSCĐ 27,74 — khớp. Đối chiếu số dư: 829,47 + 249,63 − ≈47,5 ≈ 1.031,6 = khcn_cash 1.031,63. Lớp ≤2023 theo FIFO 737,32 − 51,30 − 89,33 − 47,5 = 549,2 — khớp. Tính lại bằng tay v_stock = 0,894×(1,074/1,135)^2,485 = 0,779 và v_flow = 0,788×(1,074/1,135)^5 = 0,598 — khớp model_r9_out. Không tự trích được KQKD Q3/26 (PDF dạng scan, không có lớp chữ).",
  "killer_objection": "Phần lõi gộp hai giả định thuận lợi chưa có bằng chứng: (a) giá khí sau 2034 giữ nguyên cấu trúc Đ9.1 mãi mãi, dù sau 2032 không còn khối lượng cam kết và SĐBS 12 mới là dự thảo (biến thể có trọng số −17,6%); (b) quỹ KH&CN thu hồi được hoàn nhập, hoặc chi bắt buộc có NPV=0 — điều chưa kiểm và trái luật user 22/11 coi chi tuân thủ là dòng tiền ra (tới −8,7%). Cộng thêm hồi quy đoán cao 2024–25 khoảng 150–160 tỷ/năm (ước lượng −4,5%), tâm có thể cao 5–20%. Ngược lại, 4 cửa sổ (+7,4%) và thuế XK 0% (+3,8%) không được tính nên độ lệch không hoàn toàn một chiều.",
  "recommended_followups": [
    "Lấy văn bản xác nhận (Công báo hoặc legal-vn trích nguyên văn) việc doanh nghiệp không phải DNNN có được hoàn nhập quỹ KH&CN bị thu hồi không; nếu không, xét v = 0,8 (thay được capex nhưng mất lá chắn khấu hao thuế) hoặc 0 cho phần vượt khả năng dùng thực tế (~50–90 tỷ/năm)",
    "Tìm hạn thuê đất nhà máy Cà Mau (GCNĐT 61101000153 / hợp đồng thuê đất / BCTN) và gán xác suất cho dừng 2042/2047",
    "Đọc thuyết minh TSCĐ và lịch đại tu trong BCTC KT 2025 (S5) để chốt trục M",
    "Trình bày tâm có trọng số theo trục khí 2035+ cùng cấp với phần lõi, hoặc nêu bằng chứng cho xác suất 100% giá Đ9.1 sau 2034",
    "Đọc ý kiến kiểm toán FY2025 xem có đoạn nhấn mạnh về 332 tỷ tại MBV không",
    "Sửa câu công bố mù giá: giá đã biết từ r5 (33.000), không phải từ rev7"
  ],
  "summary": "Rev9 truy nguồn tốt và cơ học mô hình đúng: TM25 quỹ KH&CN khớp BCTC kiểm toán, số dư và lớp FIFO đối chiếu khớp, v = 0,779 / 0,598 tính lại khớp, và việc sửa quỹ theo một quy tắc đã giải quyết lỗi xử lý hai kiểu mà skeptic r3 nêu. Nhưng tâm 27.393 vẫn đứng trên ba tiền đề chưa kiểm: hoàn nhập quỹ KH&CN cho doanh nghiệp không phải DNNN (tới −8,7%), hạn thuê đất Cà Mau (−3,6…−6,8%), và giá khí sau 2034 được gán 100% theo công thức hiện hành (biến thể có trọng số −17,6%). Thêm vào đó, hồi quy đoán cao hai năm kiểm toán gần nhất khoảng 150–160 tỷ/năm (ước lượng −4,5%). Phía tăng có 4 cửa sổ (+2.024) và thuế XK 0% (+1.033) đều ngoài lõi, nên độ lệch không một chiều. Chuỗi sửa sau khi biết giá đều đi lên nhưng mỗi bước có nguồn và có khai báo; riêng câu 'giá biết từ rev7' sai vì r5/r6 đã ghi giá. Các tác động lớn này không gán được xác suất nên kết luận là INCONCLUSIVE, không phải REFUTED: mô hình dùng được làm điểm tham chiếu, nhưng chưa được coi tâm 27.393 là một số chắc chắn."
}
<<<END_VERDICT>>>