**Verdict: INCONCLUSIVE (độ tin cậy trung bình).** Số học của rev4 đúng, tôi tự tính lại được. Nhưng khoản +774 đ/cp nâng tâm trong rev4 (VAT được khấu trừ, tính đủ 100% mệnh giá và thu hồi trong 1 năm) dựa trên một giả định thời hạn mà chính bằng chứng báo cáo dẫn ra lại phản bác. Ngoài ra còn hai mục trọng yếu chưa lượng hoá được: quyết toán cổ phần hoá (CPH) và BCTC kiểm toán FY2025.

**Kiểm độc lập (khớp):**
- **Khoản cố định 11.005 đ/cp:** tự tính lại từ bảng giả định khớp. Gồm tiền ròng 45.126,2 tỷ, XDCB 2.525,9, đầu tư dài hạn 9,4, trừ KHCN 844 / KTPL 441,6 / NCI 32, cộng ứng nhà thầu 2.601,2 + chi phí giải phóng mặt bằng 546,3, cộng VAT 6.373/1,135 = 5.615.
- **Kịch bản CƠ SỞ 17.097:** khớp (5.808 + 1.960 + 11.005 + 218 − 1.894).
- **TM17 (pdf tr.30), đọc trên ảnh trang gốc:** VAT đầu ra phải nộp 312,98 tỷ, VAT hàng nhập khẩu 3.136,18 tỷ. Khớp.
- **BQ 2019–25:** CFO cộng dồn 36.519 tỷ, capex 1.608, LNST 35.542. Như vậy FCF ≈ LNST, nên cách vốn hoá LN lõi/Ke (không tăng trưởng) đứng vững. Lệch nhẹ theo chiều làm tâm thấp đi, không phải cao lên.

**Chiều ĐẮT (tâm có thể quá cao):**
1. **VAT khấu trừ (A1, +774).** Báo cáo dùng TM17 để chứng minh khoản tích luỹ là *cơ cấu*. Nhưng nếu đầu vào vượt đầu ra một cách cơ cấu thì kỳ khai thuế sau không bù trừ hết được. Khi đó việc thu hồi phụ thuộc hoàn thuế, mà điều kiện hoàn thuế theo Luật GTGT 2024 chưa được kiểm (chưa qua legal-vn). Nguyên nhân gốc (thuế suất đầu ra giảm tạm thời? VAT nhập thiết bị dự án?) cũng chưa xác định.
   - Thu hồi trong 3 năm: −251 đ/cp.
   - Trong 5 năm: −446 đ/cp.
   - 0%: −1.116 đ/cp (−6,6%).
2. **Quỹ KHCN 2026 bị ghi 0 trong base.** Nếu BSR là doanh nghiệp nhà nước theo luật thì có thể bị bắt buộc trích tối thiểu 3% thu nhập tính thuế (luật hiện hành chưa kiểm). Ước lượng: khoảng −224 đ/cp (~1,3%), nhỏ.
3. **Kế hoạch 2026 điều chỉnh (NQ 5795, HĐQT duyệt 06/11) ngụ ý Q4 lỗ −6.323 tỷ.** Kịch bản XẤU chỉ dùng −2.000. Ước lượng ảnh hưởng ≈ −300 đ/cp. Lập luận "kế hoạch hành chính" có cơ sở (doanh thu Q4 26,6 nghìn tỷ so với Q3 59,6) nhưng chưa loại trừ được khả năng có dừng máy.
4. **Quyết toán CPH và BCTC kiểm toán FY2025** vẫn thiếu, không lượng hoá được.

**Chiều RẺ (tâm có thể quá thấp):**
- Phần tăng trưởng của dự án mở rộng đang ghi NPV0, dù đã có bằng chứng tạo giá trị (lưu huỳnh thu hồi ×4,4, bỏ hẳn FO).
- Bản A (giữ lãi tỷ giá trong LN lõi) cho +402 đ/cp.

**Mục 8 (khoản thiếu):** chưa thấy khoản nào vừa lượng hoá được vừa >5% tâm, trừ VAT ở mức thu hồi 0%. Tôi đánh fail ở mức "trọng yếu nhưng chưa lượng hoá được".

Các mục còn mở cộng lại chỉ dịch tâm khoảng −7%…+2%. Vòng tới nên cho user/Mike quyết định ba điểm: luật V4a, thời hạn hoàn VAT, Euro V. Polish thêm một vòng nữa thì không đáng.

<<<VERDICT_JSON>>>
{
  "case_topic": "BSR — DD REPORT_rev4 (23/11/2026), tâm 16.886 đ/cp sau CK",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL, báo cáo không đưa ra claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — các mục pháp lý báo cáo nêu (CPH chưa quyết toán do Deloitte nhấn mạnh, MBV 2.735,6 tỷ tạm dừng giao dịch) đều được giữ ở WARNING kèm độ nhạy (MBV mất trắng −544); không thấy tín hiệu lan tới tài sản lõi trong tài liệu đã đọc; tin pháp lý T11 chưa kiểm",
    "optimistic_comp_sotp_bias": "pass — không dùng comp; số học SOTP tự tính lại khớp (khoản cố định 11.005, CO_SO 17.097); BQ 2019-25 CFO−capex 34.911 ≈ LNST 35.542 ⇒ vốn hoá LN/Ke không thổi phồng",
    "data_provenance": "fail (nhẹ) — số BS/TM khớp PDF và ảnh TM17; nhưng thời hạn thu hồi VAT (100%, 1 năm) là [UL] lại bị chính lý lẽ 'tích luỹ cơ cấu' từ TM17 phản bác: cơ cấu ⇒ kỳ sau không bù trừ được ⇒ phụ thuộc điều kiện hoàn thuế theo Luật GTGT 2024, chưa kiểm; nguyên nhân gốc chưa xác định",
    "liquidity_capacity_realism": "na — DD đề xuất 0% discretionary; ADV250 260,6 tỷ [BQ] lấy từ báo cáo, không tra giá",
    "confirmation_bias_flipflop": "pass — chuỗi tâm 17.496→16.112→16.886; mỗi bước đều gắn với điểm skeptic cụ thể và bằng chứng mới đọc (QĐ968, TM17); nhãn không đổi. Không mở dd_price_zones.json theo ràng buộc mù. Lưu ý: bước +774 là điều chỉnh tăng mà thời hạn thu hồi chỉ là [UL]",
    "exit_discipline_gap": "na — không đề xuất mua/sizing (0% discretionary); có liệt kê điều kiện đổi nhận định theo hai chiều",
    "missing_items": "fail (trọng yếu nhưng chưa lượng hoá được) — (1) thời hạn/cơ chế thu hồi VAT 6.373 tỷ: 3 năm −251, 5 năm −446, 0% −1.116 đ/cp (−6,6%); (2) quyết toán CPH phải nộp Nhà nước: chưa lượng hoá; (3) BCTC kiểm toán FY2025 vắng; (4) trích quỹ KHCN tối thiểu nếu là DNNN (luật hiện hành chưa kiểm), ước lượng ~−224 đ/cp, ghi 0 trong base; (5) Q4/2026 lỗ −6.323 tỷ ngụ ý từ NQ 5795, XẤU chỉ −2.000, ước lượng ~−300 đ/cp; (6) hợp đồng thuê đất / cung dầu thô / bao tiêu chưa xử lý. Đã đạt: capex cam kết (QĐ968/NQ5795), số CP từ mã 411, ưu đãi thuế tới 2039, bên liên quan PV OIL, cổ tức phải trả không đáng kể"
  },
  "independent_verification": "Tự tính lại khoản cố định 11.005 đ/cp và kịch bản CO_SO 17.097 từ assumptions_rev4.json: khớp. Đọc trực tiếp ảnh trang TM17 pdf tr.30: VAT đầu ra phải nộp 312.980.666.169 đ, VAT nhập khẩu 3.136.178.769.095 đ: khớp. BQ ticker_financial BSR 2019-25: CFO 36.519 / capex 1.608 / LNST 35.542 tỷ ⇒ FCF ≈ LNST, giả định vốn hoá đứng vững.",
  "killer_objection": "Khoản +774 của rev4 coi VAT khấu trừ 6.373 tỷ thu hồi 100% sau 1 năm, nhưng chính bằng chứng TM17 dùng để tách nó khỏi trục giá dầu lại cho thấy tích luỹ là cơ cấu (đầu vào > đầu ra kéo dài). Khi đó khoản này chỉ thu về qua hoàn thuế, với điều kiện pháp lý chưa kiểm, hoặc sau nhiều năm; ở 0% tâm giảm −1.116 đ/cp (−6,6%).",
  "recommended_followups": [
    "legal-vn: điều kiện hoàn VAT theo Luật GTGT 2024 (48/2024/QH15) cho nhà máy lọc dầu có VAT đầu vào dư lũy kế; kiểm thuế suất đầu ra xăng dầu 2025-26 có giảm tạm thời không",
    "Đọc thuyết minh khoản 162/VAT trong BCTC riêng Q3/2026 hoặc soát xét 6T/2026 để tách VAT nhập thiết bị dự án (dự án đầu tư được hoàn) khỏi VAT nhập dầu thô",
    "Kiểm luật trích quỹ KHCN tối thiểu cho DNNN (PVN 92,12%) theo luật KH&CN hiện hành; nếu bắt buộc thì đưa mức tối thiểu vào base",
    "Đọc NQ 5795 PL1 xem doanh thu Q4 thấp có phải do kế hoạch dừng máy không, trước khi coi −6.323 là 'hành chính'",
    "Trình user/Mike phán ba điểm treo (phân loại GHDT/DHDT/HGU theo V4a, thời hạn VAT, Euro V) thay vì thêm vòng skeptic"
  ],
  "summary": "Rev4 sạch về số học: khoản cố định và kịch bản CƠ SỞ tính lại khớp, TM17 khớp ảnh trang gốc, và dữ liệu BQ 2019-25 cho thấy FCF ≈ LNST nên cách vốn hoá đứng vững. Điểm yếu nằm ở chính thay đổi mới của rev4: VAT khấu trừ 6.373 tỷ được tính đủ mệnh giá, thu hồi sau 1 năm (+774), trong khi lý lẽ 'tích luỹ cơ cấu' từ TM17 lại hàm ý không tự bù trừ được và phải chờ hoàn thuế với điều kiện chưa kiểm. Dải ảnh hưởng 0 đến −1.116 đ/cp. Chiều đắt còn có quỹ KHCN tối thiểu nếu là DNNN (~−224, ước lượng), Q4 kế hoạch lỗ −6.323 so với XẤU −2.000 (~−300, ước lượng), và CPH/FY2025 kiểm toán chưa lượng hoá. Chiều rẻ: phần tăng trưởng ghi NPV0 dù có bằng chứng tạo giá trị, và bản giữ lãi tỷ giá (+402). Tổng các mục mở dịch tâm khoảng −7%…+2%; chưa xác nhận được cho tới khi cơ chế thu hồi VAT và quyết toán CPH có nguồn."
}
<<<END_VERDICT>>>