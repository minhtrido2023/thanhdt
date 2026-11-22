**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phép tính của báo cáo đúng và các số BCTC tôi kiểm lại đều khớp. Vấn đề là mô hình bỏ sót một khoản capex tuân thủ môi trường mà chính công ty đã khởi động. Đây đúng là kiểu lỗi đã gặp ở QTP. Cũng chưa ai chứng minh NT3&4 có NPV = 0 như mô hình giả định.

**Phần tôi tự kiểm lại**
- **Tâm 9.891 tái lập đúng.** Vốn di sản 31.394,5 × 8%/13,5% = 18.604; cộng 9.000 (NT3&4) + 2.740 (dự án mới) = 30.344 tỷ; chia 3.067,85 tr cp = 9.891 đ. Hai kịch bản xấu/tốt ra 7.238 / 12.544, khớp báo cáo.
- **Số cp 3.067.845.688 khớp** với TM23 (OCR BCTC Q3).
- **Vốn chủ mẹ 43.134,5 khớp.** Cộng các dòng vốn chủ từ OCR ra đúng số này. Riêng dòng Quỹ ĐTPT bị OCR nhoè, tôi suy ra ~2.797,9 từ tổng nên đây là tính nhất quán, không phải một lần đọc độc lập.
- **ROE di sản 8% có cơ sở.** Tôi tính lại theo chuỗi BQ: bỏ ~9.000 vốn NT3&4 khỏi mẫu số 2023-25 rồi cộng lại phần hồi tố ~2.455 sau thuế chia cho 7 năm, ra ~8,0% (ước lượng). Như vậy 8% nằm giữa dải, không phải cận lạc quan như báo cáo tự nhận.
- **Chênh nhỏ:** vay ngắn hạn theo OCR là 19.418,3, báo cáo ghi 19.438,3 (có thể do OCR). Không ảnh hưởng đến kết luận.

**Các điểm chưa đạt**
1. **Khoản bị bỏ sót (tấn công 8):** CBTT `2026-04-15_6851` và `2026-03-13_6803` là kết quả chọn thầu gói "Tư vấn đánh giá kỹ thuật và lập báo cáo đề xuất đầu tư cho các nhà máy nhiệt điện của PV Power đáp ứng QCVN 19:2024 về khí thải".
   - Báo cáo chỉ xếp mục này vào "Carbon — chưa có số". Không có dòng tiền ra nào trong mô hình.
   - Nếu VA1 (than, 1.200 MW) cần mức tương tự QTP (~3.485 tỷ), tác động khoảng −650 đến −1.140 đ/cp, tức −7 đến −12% tâm (ước lượng theo tương tự, giả định không được tính vào giá điện).
2. **Chiều ĐẮT (tâm có thể quá cao):** NT3&4 được ghi theo sổ với giả định NPV = 0.
   - Qc 65% tương đương ~9,2 tỷ kWh/năm (ước lượng). Hợp đồng LNG dài hạn chỉ phủ ~3,2 tỷ kWh/năm, phần còn lại mua giao ngay với JKM 27,6 USD/MMBtu.
   - Điều khoản take-or-pay và công thức giá chưa có số, nên NPV có thể âm.
   - Ngoài ra ~2.755 tỷ LNTT hồi tố đã nằm trong vốn chủ nhưng chưa thu tiền (phải thu EPTC 23.880).
3. **Chiều RẺ (tâm có thể quá thấp):**
   - Mô hình phạt vĩnh viễn ROE < r trên vốn di sản (định giá 0,59× sổ) cho các nhà máy 17-18 năm tuổi. Nếu đời máy hữu hạn và vốn được thu hồi, phần phạt này có thời hạn nên giá trị cao hơn.
   - r 13,5% là Ke chung, utility có thể thấp hơn.
   - Tiền chào bán chưa dùng 1.080 tỷ được tính theo sổ (1,0×), trong khi tiền mặt khác nằm trong vốn di sản bị định giá 0,59×. Cách đối xử này không nhất quán.
4. **Các mục còn trống khác:** hạn PPA và nguồn khí của CM1&2/NT1; giá trị giao dịch bên liên quan; quyết toán cổ phần hoá chưa duyệt (tiền lệ: khoản 728,2 tỷ phải nộp PVN).
5. **Quỹ khen thưởng phúc lợi không trọng yếu:** trích từ lợi nhuận 2026 chỉ khoảng ~1% tâm (ước lượng).

Theo ràng buộc mù, tôi không mở `dd_price_zones.json`. Tấn công 6 (lật nhãn) chỉ so vòng 1 với vòng 2 trong chính thư mục báo cáo. Tôi cũng bỏ qua thị giá có trong văn bản báo cáo.

<<<VERDICT_JSON>>>
{
  "case_topic": "POW — DD vòng 2 (REPORT.md 2026-11-18), tâm 9.792 đ/cp, vùng [7.166; 12.419]",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không có claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — FY2025 Deloitte chấp nhận toàn phần, nhấn mạnh chưa duyệt quyết toán CPH (báo cáo có nêu); không thấy khởi tố/xử phạt; WARNING bên liên quan có nêu nhưng giá trị chưa đọc",
    "optimistic_comp_sotp_bias": "fail (nhẹ, hai chiều) — SOTP ghi NT3&4 9.000 theo sổ (NPV=0) dù HĐ LNG định hạn 20,7tr MMBtu ≈3,2 tỷ kWh/năm ≪ Qc 65% ≈9,2 tỷ kWh/năm (ước lượng), ToP/giá chưa có ⇒ NPV có thể âm (tâm quá cao); ngược lại phạt ROE<r vĩnh viễn trên vốn di sản (0,59× sổ) cho nhà máy 17-18 năm tuổi, và tiền chào bán chưa dùng 1.080 ghi 1,0× trong khi tiền khác ở 0,59× (bất nhất); bảng peer chỉ hiển thị, không neo tâm",
    "data_provenance": "pass — số cp 3.067.845.688 (TM23 OCR), vốn chủ mẹ 43.134,5 (cộng các dòng vốn chủ từ OCR, Quỹ ĐTPT suy ~2.797,9), LNST 9T 6.434,5 (dòng 420b OCR) khớp; ước lượng được gắn nhãn; lệch nhỏ vay NH 19.438,3 (báo cáo) vs 19.418,3 (OCR, có thể lỗi OCR)",
    "liquidity_capacity_realism": "na — không có claim sizing; chiết khấu thanh khoản 1% có ADV 63,3 tỷ/phiên",
    "confirmation_bias_flipflop": "pass — r1 8.806 → r2 9.792 (+11%) do đính chính skeptic r1 đã liệt kê (g 2%→0, tách vốn dự án mới 2.740 theo sổ, NT3&4 10.000→9.000); mỗi khoản có nguồn; không mở dd_price_zones.json theo ràng buộc mù của brief",
    "exit_discipline_gap": "na — không có claim fear-buy/sizing; có điều kiện đổi nhận định hai chiều (§11)",
    "missing_items": "fail — (1) CAPEX TUÂN THỦ QCVN 19:2024 khí thải nhiệt điện: CBTT 2026-03-13_6803/2026-04-15_6851 chọn thầu tư vấn 'lập báo cáo đề xuất đầu tư cho các nhà máy nhiệt điện đáp ứng QCVN 19:2024' — vắng trong mô hình (chỉ ghi 'Carbon: chưa có số'); tương tự QTP ~3.485 tỷ cho VA1 1.200MW than ⇒ −650…−1.140 đ/cp ≈ −7…−12% tâm (ước lượng, nếu không pass-through), chưa định lượng được; (2) hạn PPA/nguồn khí CM1&2 (2008), NT1 (2009) trong chân trời vĩnh viễn — 'không có'; (3) Qc 65% NT3&4: mẫu số, thời hạn, ToP LNG — chưa có; (4) giá trị giao dịch bên liên quan — chưa đọc; (5) quyết toán CPH chưa duyệt — nghĩa vụ phải nộp PVN tiềm tàng (tiền lệ 728,2) chưa định lượng; pass: số cp + ngày, kiểm toán FY2025, tách một lần 9T, capex tăng trưởng NQ 90; quỹ khen thưởng phúc lợi (nợ 293,2 trên BCĐKT; trích từ LN 2026 ~300 tỷ ≈1% tâm, ước lượng) không trọng yếu"
  },
  "independent_verification": "Tái lập tâm 9.891 trước chiết khấu (31.394,5×0,08/0,135 + 11.740 = 30.344 tỷ / 3.067,85tr cp) và kịch bản 7.238/12.544 — khớp. Số cp và LNST mẹ 9T khớp OCR BCTC Q3; vốn chủ mẹ 43.134,5 khớp khi cộng các dòng OCR (Quỹ ĐTPT suy ra ~2.797,9 vì OCR nhoè dòng này — kiểm nhất quán, không phải đọc độc lập). Tự dựng lại ROE di sản: chuỗi mẹ 2019-25 bỏ ~9.000 vốn NT3&4 khỏi mẫu số 2023-25 và cộng hồi tố ~2.455 sau thuế chia 7 năm ⇒ ~8,0% (ước lượng) — base 8% có cơ sở, nằm giữa dải chứ không phải cận lạc quan.",
  "killer_objection": "Capex tuân thủ QCVN 19:2024 khí thải nhiệt điện — đúng kiểu lỗi QTP — đã được công ty khởi động (thầu tư vấn đề xuất đầu tư) nhưng hoàn toàn vắng khỏi mô hình; nếu VA1 cần mức như QTP mà không được tính vào giá điện, tâm giảm ~7-12%; cộng thêm NT3&4 định ở sổ dù LNG định hạn chỉ phủ ~1/3 Qc 65%.",
  "recommended_followups": [
    "Đọc CBTT 2026-03-13_6803 và 2026-04-15_6851 + BCTC riêng/NQ HĐQT tìm tổng mức đầu tư dự kiến QCVN 19:2024 theo nhà máy (VA1 FGD/SCR), lộ trình hiệu lực và khả năng tính vào giá cố định PPA; mô hình hoá như dòng tiền ra (luật 22/11)",
    "Lập NPV riêng NT3&4: Qc 65% × công suất, phần LNG giao ngay vs định hạn, pass-through nhiên liệu trong giá Qc, lỗ/lãi NT3&4 9T nếu tách được từ BCTC riêng",
    "Thay ROE<r vĩnh viễn bằng mô hình đời máy hữu hạn/fade cho CM1&2, NT1 (hạn PPA + nguồn khí) — có thể đẩy tâm LÊN",
    "Định lượng nghĩa vụ tiềm tàng quyết toán CPH và giá trị giao dịch bên liên quan (PV GAS khí/LNG)",
    "Đối chiếu lại vay ngắn hạn 19.438,3 vs 19.418,3 trên PDF gốc"
  ],
  "summary": "Phép tính và dữ kiện cốt lõi của báo cáo POW vòng 2 đứng vững: tâm tái lập đúng, số cp/vốn chủ/LNST khớp BCTC, ROE di sản 8% tự dựng lại ra ~8,0%. Nhưng mô hình bỏ sót capex tuân thủ QCVN 19:2024 khí thải mà công ty đã khởi động qua thầu tư vấn đề xuất đầu tư — đúng mẫu lỗi QTP, ước −7…−12% tâm nếu không được tính vào giá điện. NT3&4 ghi theo sổ (NPV=0) trong khi LNG định hạn chỉ phủ ~1/3 Qc 65% và ToP chưa có số. Hai lỗ hổng này kéo tâm xuống; ngược lại, việc phạt ROE<r vĩnh viễn trên nhà máy già và r 13,5% chung có thể làm tâm quá thấp. Chưa định lượng được các khoản trọng yếu nên kết luận là INCONCLUSIVE, không phải CONFIRMED."
}
<<<END_VERDICT>>>