**Kết luận: INCONCLUSIVE, độ tin cậy trung bình.** Mô hình rev4 tái lập khớp từng số. Nhưng lựa chọn quan trọng nhất của rev4 (k = 1,0) lại nằm **dưới** chính chuỗi số đo mà rev4 vừa thu thập. Ngoài ra, ba hạng mục vẫn chưa kiểm chứng được và đều lớn: hạn PPA và giá bán điện Cửa Đạt, khoản góp vốn ~1.000 tỷ chưa thuyết minh, thời hạn giấy phép các nhà máy. Báo cáo có ghi thị giá; tôi bỏ qua khi đánh giá mô hình.

**Đã kiểm độc lập:**
- **Mô hình:** chạy `model_rev4.py` ra tâm 30.805, N base 282,5, phần thuỷ văn vượt 139,5 tỷ, md5 khớp phụ lục A. Tôi tính tay phần thuỷ văn vượt theo từng nhà máy, ra ≈139,4 tỷ.
- **Sản lượng 2021:** BCTN21 ghi 614.816.689 kWh cho 6 nhà máy, trong đó Cửa Đạt 396.472.368. Khớp.
- **Sản lượng 2024:** cộng từng nhà máy trong BCTN24 được 6 nhà máy thuỷ điện = 732,9 tr kWh, tức 1,028 × Etb. Báo cáo ghi 732,0 (1,027). Lệch nhỏ, không đổi kết luận.
- **ĐHĐCĐ 2026:** đã xem ảnh trang chương trình họp (TL26 tr.4): 9 nội dung, không có phát hành, ESOP hay cổ tức cổ phiếu. Số cổ phiếu 83.789.658 đứng vững.

**Chiều RẺ — tâm có thể quá thấp:**
- Báo cáo viết "Etb nằm trong khoảng đo [1,009 ; 1,061]". **Câu này sai:** 1,0 nhỏ hơn 1,009.
- Chuỗi riêng của Cửa Đạt, ghép từ chính nguồn báo cáo dẫn, gồm 0,747 / 0,951 / 1,300 / 0,881 / 1,063 / 1,418. Trung bình 6 năm = **1,06 × Etb**, kể cả năm thấp kỷ lục 2020. Cửa Đạt chiếm 56% Etb của cả hệ thống.
- Kế hoạch sản lượng của công ty không phải ước lượng không lệch cho mức bình thường: KH2020 = 1,00 nhưng thực tế 0,747; KH2022 = 0,963 nhưng thực tế 1,21.
- Tác động lên tâm: dùng k = 1,061 cho cả hệ thống thì +5,2% (32.412). Chỉ chỉnh riêng Cửa Đạt lên 1,06 thì khoảng +2,7% (ước lượng).
- Hệ số k đã đi 1,081 (rev3) → 1,127 (rev3b) → 1,0 (rev4), mỗi lần bám theo phản biện gần nhất. Lần này hạ thấp hơn cả dữ liệu mới vừa thu thập. Theo luật của user, điều chỉnh xuống phải có căn cứ độc lập, nhưng căn cứ ở đây chỉ là "kế hoạch ≈ Etb", vốn yếu.

**Chiều ĐẮT — tâm có thể quá cao:**
- Bull lấy lợi nhuận 12 tháng gần nhất, năm thuỷ văn ướt, rồi nhân lên vĩnh viễn mà không chuẩn hoá thuỷ văn, với trọng số 0,25.
- ΔB cộng đủ theo giá sổ, kể cả 132,7 tỷ (biên phế liệu + lãi dồn tích) mà bull đã loại. Nếu trừ ra: −3,9%.
- Giá bán điện Cửa Đạt (Pc) giảm 20%: −7,3% đến −13,8%. Mức 20% là ước lượng.
- Ngày hết ưu đãi thuế từng nhà máy chưa kiểm chứng: −1,3% đến −4,6%.
- Khoản góp vốn ~1.000 tỷ vẫn chưa định danh.

**Hạng mục còn thiếu (đòn 8):**
- **Đạt:** số cổ phiếu, quỹ khen thưởng phúc lợi, ý kiến kiểm toán 2025 (chấp nhận toàn phần, theo REPORT.md), capex tăng trưởng ~1.680 tỷ (tính NPV0 theo luật V4a), bảo lãnh Đak Lô (đã hợp nhất).
- **Chưa đạt, không lượng hoá được nhưng trọng yếu:** hạn PPA và giá bán Cửa Đạt, thời hạn giấy phép khai thác nước của các nhà máy đang chạy, bản chất khoản ~1.000 tỷ và 823 tỷ cho cá nhân vay. Theo luật đòn 8, các mục này dẫn tới INCONCLUSIVE.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCP — DD rev4 (REPORT_rev4.md), tâm 30.805 / 29.686 sau CK",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — pháp lý chỉ ở mức WARNING, không vào base; không thấy dấu hiệu lan sang pháp nhân/tài sản lõi trong các nguồn được dẫn; rủi ro phân bổ vốn (cho vay cá nhân 823,4 tỷ, 46,8% cp cầm cố) đã nêu rõ",
    "optimistic_comp_sotp_bias": "fail (hai chiều, mỗi chiều đều dưới 5%) — base k=1,0 nằm DƯỚI khoảng đo [1,009;1,061] mà báo cáo tự khẳng định là chứa nó; chuỗi riêng Cửa Đạt 2020–25 = 0,747/0,951/1,300/0,881/1,063/1,418, trung bình 1,06 (Cửa Đạt chiếm 56% Etb) ⇒ tâm có thể thấp đi 2,7–5,2%. Ngược lại, bull nhân vĩnh viễn TTM năm ướt chưa chuẩn hoá thuỷ văn (w=0,25) và ΔB còn chứa 132,7 tỷ bull đã loại (−3,9%) ⇒ đẩy tâm lên",
    "data_provenance": "pass — 2021 614.816.689 kWh / Cửa Đạt 396.472.368 khớp text BCTN21; 2024 cộng từng nhà máy ra 732,9 so với 732,0 của báo cáo (1,028 vs 1,027); chương trình ĐHĐCĐ 2026 có 9 nội dung, không phát hành (ảnh tl26_p4); md5 khớp và mô hình tái lập đúng. Riêng câu §2 'Etb nằm trong khoảng đo' sai về mặt dữ kiện",
    "liquidity_capacity_realism": "na — DD_GENERAL không có đề xuất sizing; chiết khấu thanh khoản hiển thị cơ học, không đánh giá",
    "confirmation_bias_flipflop": "fail (nhẹ) — k đi 1,081 (rev3) → 1,127 (rev3b) → 1,0 (rev4), mỗi lần bám theo skeptic gần nhất. Rev4 có dữ liệu mới thật (chuỗi 2020–22, 2024), nhưng dữ liệu đó trỏ về ~1,03–1,06 mà base lại chọn 1,0, chỉ dựa vào 'kế hoạch ≈ Etb' (KH2020 1,00 vs thực 0,747; KH2022 0,963 vs 1,21 ⇒ kế hoạch không phải ước lượng không lệch)",
    "exit_discipline_gap": "na — DD_GENERAL; §10 có bảng điều kiện đổi nhận định hai chiều",
    "missing_items": "fail (không lượng hoá được) — ĐẠT: số cp (NQ/TL ĐHĐCĐ 2026), quỹ KT-PL 1,84%, kiểm toán KT25 chấp nhận toàn phần, capex Đak Lô/Thác Ba ~1.680 tỷ (ước lượng, NPV0 V4a), bảo lãnh Đak Lô (công ty con hợp nhất), thuế tài nguyên trong chi phí. THIẾU: hạn PPA/giá bán sau trả nợ Cửa Đạt (độ nhạy −7,3…−13,8%); thời hạn giấy phép khai thác nước các nhà máy đang chạy + truy thu tiền cấp quyền (< −1.290 đ, ước lượng); bản chất ~1.000 tỷ góp vốn 9T/26 (độ nhạy 29.015–32.595); ngày hết ưu đãi thuế (−1,3…−4,6%)"
  },
  "independent_verification": "Chạy lại model_rev4.py: tâm 30.805, N_base 282,5, phần thuỷ văn vượt 139,5, md5 khớp. Tính tay phần thuỷ văn vượt theo nhà máy ≈139,4. BCTN21: 614.816.689 kWh / Cửa Đạt 396.472.368 — khớp. BCTN24: 443,483+138,968+62,267+64,190+24,001 = 732,9 tr kWh (1,028 Etb) so với báo cáo 732,0 — khớp ±0,1%. Ảnh tl26_p4: 9 nội dung ĐHĐCĐ 2026, không phát hành — khớp.",
  "killer_objection": "Mức thuỷ văn base k=1,0 là lựa chọn hạ tâm không có căn cứ đo độc lập: chính chuỗi 6 năm của Cửa Đạt (gồm năm thấp kỷ lục 2020) cho 1,06 × Etb và trung bình hệ thống 2021–25 = 1,061, nên câu 'Etb nằm trong khoảng đo' là sai. Đồng thời, phía đắt vẫn treo trên ba ẩn số trọng yếu không lượng hoá được (PPA/giá Cửa Đạt, pool ~1.000 tỷ, giấy phép).",
  "recommended_followups": [
    "Sửa câu §2 'Etb nằm trong khoảng đo [1,009;1,061]' (1,0 < 1,009); hoặc chọn k từ chuỗi đo (vd trung bình Cửa Đạt 6 năm 1,06 cho Cửa Đạt, Etb cho phần còn lại), hoặc ghi rõ k=1,0 là lựa chọn bảo thủ có chủ đích kèm độ nhạy +2,7…+5,2%",
    "Chuẩn hoá thuỷ văn cho N_bull (ít nhất k=1,15 theo KH2026) thay vì nhân vĩnh viễn TTM năm ướt",
    "Tìm hạn PPA/cơ chế giá Cửa Đạt (HĐ 06/2012 + PL11) và giấy phép khai thác nước các nhà máy đang chạy",
    "Chờ thuyết minh BCTC Q4/2026 hoặc kiểm toán 2026 cho khoản ~1.000 tỷ góp vốn và dư nợ cho vay cá nhân"
  ],
  "summary": "Số học và nguồn của rev4 đúng: mô hình tái lập khớp; sản lượng 2021, 2024 và chương trình ĐHĐCĐ 2026 đều kiểm chéo được với nguồn gốc. Điểm yếu chính nằm ở thay đổi duy nhất của rev4: k = 1,0. Báo cáo nói Etb nằm trong khoảng đo [1,009;1,061], nhưng 1,0 nằm dưới khoảng đó. Chuỗi riêng Cửa Đạt (56% Etb) trung bình 1,06 × Etb kể cả năm thấp kỷ lục 2020, và kế hoạch công ty không phải ước lượng không lệch. Vì vậy tâm có thể thấp đi 2,7–5,2%, đúng kiểu điều chỉnh xuống thiếu căn cứ độc lập mà user cấm. Hệ số k cũng đã dao động 1,081 → 1,127 → 1,0 theo từng vòng phản biện. Theo chiều đắt, bull nhân vĩnh viễn TTM năm ướt, ΔB còn chứa 132,7 tỷ bull đã loại, và ba ẩn số trọng yếu (PPA/giá Cửa Đạt, pool ~1.000 tỷ, giấy phép) vẫn chưa kiểm chứng. Không có lỗi đơn lẻ nào lượng hoá được rõ ràng trên 5% để REFUTED, nhưng các hạng mục trọng yếu không lượng hoá được khiến CONFIRMED chưa đủ điều kiện. Thị giá trong báo cáo đã bị bỏ qua."
}
<<<END_VERDICT>>>