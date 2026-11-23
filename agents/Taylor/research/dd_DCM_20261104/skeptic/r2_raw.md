**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Tôi chạy lại mô hình rev7 và ra đúng điểm base 24.809 đ/cp. Ba sửa đổi theo skeptic r1 (D&A, capex duy trì, quỹ KH&CN) có nguồn và đi cả hai chiều. Nhưng tâm vẫn dựa trên một giả định chưa có nguồn, có thể kéo giá trị xuống 30–46%. Ngoài ra còn một khoản chiều tăng chưa được mô hình hoá. Báo cáo có ghi giá thị trường; tôi bỏ qua hoàn toàn khi chấm.

**Kiểm độc lập**
- **Chạy lại mô hình:** `model_r7.pt7`, trung bình lưới M, ra 24.809. Khớp §2.
- **Lỗi dữ liệu BQ năm 2021:** dòng 2021Q4 trong `bq_da_r7_out.csv` chép nguyên EBITDA_TTM và EBITM của 2021Q3 (2.339,136 / 0,11907), chỉ doanh thu TTM là thay đổi. Vì vậy D&A 2021 = 1.127,8 là số giả. Tính lại bằng dữ liệu Q3 ra ≈1.316. Tâm tăng **+186 đ/cp (+0,7%)**, không đáng kể, nhưng báo cáo không ghi lỗi này.
- **Đối chiếu khấu hao luỹ kế (CĐKT KT 2025):** luỹ kế 15.220,6 tỷ. Tổng D&A mô hình dùng cho 2016–25 là ≈10,6–10,8 nghìn tỷ, nên 2012–15 phải vào khoảng ≈1,15 nghìn tỷ/năm. Con số này khớp với BQ thô.
  - Biến thể "hiệu chỉnh BQ ×1/0,83" (+934) **mâu thuẫn** với phép đối chiếu này: nó buộc 2012–15 chỉ còn ≈780/năm. Biến thể chiều tăng đó không có cơ sở.

**Chỗ yếu chiều ĐẮT (tâm quá cao)**
1. **Giá khí sau 2035 là giả định chưa có nguồn.** Mô hình dùng "50% PVN + 50% @13,7% Brent" (`model_r5.py:47`, tự ghi là "ước lượng"). Khối lượng cam kết hết 24/4/2032, hợp đồng Petronas hết 2027. Đổi giả định này thì tâm mất −7.606 đến −11.364 (−31% đến −46%), nhưng phần đó chỉ nằm ở độ nhạy.
2. **Nhà máy chạy vĩnh viễn với capex duy trì chỉ 342–540 tỷ/năm.** Nguyên giá năm 2012 là 16.959 tỷ, đã khấu hao 90%. Nếu thay thế theo vòng đời kinh tế ~35 năm và tính theo giá thực thì ≈700 tỷ/năm, gần biến thể M=738 (−13%). Kịch bản dừng máy 2042 cho −7%. Cả hai đều >5% và không vào base. Ngược lại, chưa có bằng chứng cho giả định vòng đời vô hạn.
3. **Cơ sở pháp lý của khoản trừ quỹ KH&CN (−2.001, −8%) là "theo hiểu biết",** chưa nhờ Wendy (legal-vn) kiểm. Số dư 1.059,37 thì có nguồn: CĐKT Q3/26 mã 344.

**Chỗ yếu chiều RẺ (tâm quá thấp)**
- **Thiếu (điểm 8 — khoản bị bỏ sót):** phân bón chuyển sang chịu VAT 5% từ 07/2025, nên VAT đầu vào được khấu trừ. Hồi quy 2021–25 gần như toàn bộ nằm trong chế độ cũ, còn báo cáo chỉ coi VAT là rủi ro quay lại chế độ cũ. Một điểm biên lợi nhuận gộp ≈ +1,9 nghìn đ/cp.
  - Phản chứng một phần: phần dư 2025 là −374, tức mô hình đang dự báo cao hơn thực tế. Chưa có ước lượng nào, nên khoản này là trọng yếu nhưng chưa định lượng được.
- **Bỏ 2 cửa sổ hồi quy có dữ liệu 2016–20 (−1.977):** việc này có cơ sở là phần dư trên các năm đã kiểm toán, không chọn theo chiều giá. Tôi chấp nhận.

**Các điểm còn lại đều đạt:** số cổ phiếu, quỹ KTPL, ý kiến kiểm toán FY2025, khoản một lần, thanh khoản, HARD ABANDON. Thay đổi r6→rev7 xuất phát từ các hạng mục skeptic r1 có nguồn, không phải lật kết luận.

<<<VERDICT_JSON>>>
{
  "case_topic": "DCM (PVCFC) — DD rev7 23/11/2026, tâm 24.822 đ/cp",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "mode": "DD_GENERAL",
  "checks": {
    "discriminator_cherry_picking": "na — báo cáo tự ghi không đủ điều kiện §2.5 (không có sự kiện sợ hãi); không có claim fear-buy",
    "scandal_migration_risk": "pass — WARNING pháp lý giữ từ r6 (HĐ khí là giao dịch bên liên quan PVN→PV GAS→DCM, SĐBS 12 mới là dự thảo, 332 tỷ bị hạn chế tại MBV); rev7 tự ghi không tra lại tin pháp lý kể từ 04–05/11 ⇒ cũ ~19 ngày, không thấy dấu hiệu lan sang pháp nhân trong hồ sơ",
    "optimistic_comp_sotp_bias": "pass — không dùng comp/SOTP; mô hình hồi quy LNST theo biên + lưới 2.430 kết cục; bỏ 2 cửa sổ hồi quy 2016–20 có cơ sở phần dư năm kiểm toán (−463/−651), không chọn theo giá",
    "data_provenance": "fail (không lật) — D&A 2018–23 suy từ BQ; dòng 2021Q4 trong bq_da_r7_out.csv chép nguyên EBITDA_TTM/EBITM của 2021Q3 ⇒ D&A 2021 = 1.127,8 là số giả (đúng ≈1.316, tâm +186 / +0,7%), báo cáo không ghi; cơ sở pháp lý quỹ KH&CN (−2.001) 'theo hiểu biết, chưa nhờ Wendy kiểm'; giá khí 2035+ trong base là 'ước lượng' (model_r5.py:47)",
    "liquidity_capacity_realism": "pass — ADV trung vị 250 phiên 89 tỷ vs vị thế 5 tỷ (5,6% ADV), CK 0,585% theo luật căn bậc hai; nhãn như nhau ở mọi cỡ sleeve 2–4% NAV",
    "confirmation_bias_flipflop": "pass — r6→rev7 do các hạng mục K1–K3 của skeptic r1, có nguồn BCTC (LCTT mã 02, TM16, CĐKT mã 344), đi cả hai chiều (+2.833 vs −2.908); nhãn TRÊN vùng không đổi; chỉ đọc REPORT_r6 + skeptic/r1, không mở sổ vùng giá",
    "exit_discipline_gap": "pass — có tranche 2% NAV khi giá ≤ 0,85×tâm, HARD ABANDON khi giá > P90, trigger làm lại (dừng máy > 60 ngày, PVN thoái vốn đổi HĐ khí, SĐBS 12 ký khác dự thảo), hạn DD = BCTC Q4/26 hoặc +120 ngày",
    "missing_items": "fail (chưa định lượng) — (a) THIẾU: chế độ VAT 5% từ 07/2025 (VAT đầu vào được khấu trừ) không vào hồi quy; chiều TĂNG, ~+1,9k đ/cp mỗi 1pp biên gộp, chưa ước lượng, phần dư 2025 −374 phản chứng một phần; (b) có trong độ nhạy nhưng ngoài base và chưa có nguồn: giá khí 2035+ (−7.606…−11.364, −31…−46%), vòng đời/capex thay thế theo giá thực (dừng 2042 −7%, M=738 −13%); còn lại đạt: capex cam kết (tăng trưởng NPV0), số cổ phiếu 529,4 tr (30/9/26, không ESOP), quỹ KTPL 265,3 + quỹ KH&CN 1.059,4 đã trừ, kiểm toán FY2025 Deloitte chấp nhận toàn phần, khoản một lần đã liệt kê, thuế TNDN 20% từ 2027"
  },
  "independent_verification": "Chạy lại model_r7.pt7 (lưới M 342/401/540) ra base 24.809, khớp §2. Tự tính D&A BQ 2021/2022/2023 = 1.127,8/1.273,5/1.062,8, khớp, nhưng phát hiện 2021Q4 là dòng chép của Q3; sửa thành 1.316,1 thì tâm 24.995 (+186). Đối chiếu khấu hao luỹ kế 15.220,6 (KT 2025) với tổng D&A 2016–25 ≈10,6–10,8 nghìn tỷ: nhất quán với BQ thô, mâu thuẫn với biến thể hiệu chỉnh ×1/0,83 (+934).",
  "killer_objection": "Tâm gánh một giả định giá khí 2035+ không có hợp đồng ('50% PVN + 50% @13,7% Brent', ước lượng) trong khi khối lượng cam kết hết 24/4/2032; đổi giả định này thì tâm dao động −31…−46%, lớn hơn mọi sửa đổi rev7 cộng lại. Ở chiều ngược lại, chế độ VAT 5% (khấu trừ đầu vào) chưa vào mô hình.",
  "recommended_followups": [
    "Ghi nguồn hoặc biện minh cho giá khí 2035+ trong base (PSC PM3 tới 2047, kế hoạch nguồn khí PV GAS); nếu không có nguồn thì đưa kịch bản flat/esc vào lưới với trọng số khai báo",
    "Ước lượng tác động VAT 5% lên chi phí: VAT đầu vào khí/vật tư được khấu trừ, tỷ trọng bán nội địa, phần chuyển sang giá bán; đối chiếu biên gộp H2/2025–9T/26 với H1/2025",
    "Sửa dòng 2021Q4 stale trong bq_da_r7 (dùng TTM Q3 hoặc BCTC KT 2021) và ghi chú trong báo cáo",
    "Nhờ legal-vn (Wendy) kiểm Luật KH&CN 2013 Đ63 / TT 67/2022 cho khoản trừ −2.001",
    "Đọc thuyết minh TSCĐ KT 2025 (thời gian khấu hao còn lại, lịch đại tu) để chốt M dài hạn hoặc năm dừng máy"
  ],
  "summary": "Rev7 tái lập được (base 24.809 khớp) và đã xử lý đúng hướng cả ba lỗi skeptic r1: D&A, capex duy trì, quỹ KH&CN. Các khoản đều có trang BCTC dẫn nguồn, đi cả hai chiều. Phép đối chiếu khấu hao luỹ kế ủng hộ D&A BQ thô và bác biến thể tăng +934. Lỗi dữ liệu 2021Q4 (dòng chép của quý trước) chỉ làm lệch +0,7%. Chưa thể CONFIRMED vì hai lý do: (1) giá khí 2035+ trong base là ước lượng không hợp đồng, có thể kéo giá trị xuống 31–46%, và vòng đời nhà máy vô hạn với capex 342–540 tỷ/năm cũng chưa có nguồn; (2) ở chiều ngược lại, chế độ VAT 5% từ 07/2025 chưa vào hồi quy và có thể làm tâm thấp đi vài nghìn đ/cp. Tâm 24.822 hợp lý như một điểm giữa, nhưng dải P10–P90 hẹp hơn độ bất định thật."
}
<<<END_VERDICT>>>