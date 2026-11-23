**Kết luận: INCONCLUSIVE (độ tin cậy trung bình).** Phép tính của rev3 tái lập đúng đến từng đồng và nguồn mới truy được. Nhưng có một khoản trọng yếu chưa được định lượng ở bất kỳ kịch bản nào: khoảng 1.000 tỷ góp vốn 9T/26 không có thuyết minh. Ngoài ra kịch bản bull bị đếm trùng ΔB.

**Đã tự kiểm lại:**
- **Base:** chạy lại chuẩn hoá thuỷ văn từ bảng giả định, ra trừ 104,4 tỷ, N = 315,4 tỷ, base 32.988. Khớp hoàn toàn. Nếu dùng Etb thiết kế (k = 1) thì base còn 29.967.
- **Số liệu gốc trong BCTN25:** Cửa Đạt 591.418.950 kWh và 429,07 tỷ. KH 2026 thuế 86,04 / LNTT 562,18, tức 15,3%. Etb từng nhà máy và số cổ phiếu 83.789.658 cũng khớp.
- **Bear và tâm:** 2.764,1 − 139,7 − 401,9 = 2.222,5 tỷ. Bình quân trọng số ra 35.826. Đúng.
- **Md5 khoá:** khớp `LOCK_prerun_rev3.txt`.

**Lỗi và lỗ hổng:**
1. **Chiều đắt, chính:** trong 9T/26 có −1.545,7 tỷ "góp vốn vào đơn vị khác". Chỉ 545,7 tỷ được định danh (Linh Linh). Khoảng 1.000 tỷ còn lại, cùng 696,5 tỷ tài sản ngắn hạn khác phát sinh trong Q3, không có thuyết minh (rev2 §3).
   - Khoản này khoảng 11.900 đ/cp, xấp xỉ 33% tâm.
   - Bear chỉ trừ lỗ cho vay (50% × 803,7 tỷ), không chạm tới khoản này.
   - Chính rev2 (dòng 256) đã chọn cách đọc A để không thưởng cho khoản này. Rev3 chuyển sang cộng theo giá sổ (V4a) mà không có thông tin mới (Phụ lục B mục 4 vẫn ghi "giữ như rev2").
2. **Chiều đắt:** bull dùng LNST TTM Q3/26, đã gồm lợi nhuận từ Linh Linh và các tài sản 2026. Sau đó bull lại cộng thêm ΔB 427,9 tỷ, tức đếm trùng tới khoảng 5.100 đ/cp trên bull, khoảng −1.280 đ trên tâm (−3,6%).
3. **Sai nhỏ:** nhà máy Etb 75,81 (18 MW) thuộc sở hữu của Nậm La với 50,06%. Sở hữu hiệu dụng của VCP là 41,4%, không phải 66,9%. Nhà máy Etb 66,10 là 51%. Sửa lại thì base thành 32.935 (−53 đ), không đáng kể.
4. **Sót nguồn, không đáng kể:** báo cáo ghi giấy phép "không kiểm chứng được". Thực ra BCTN23 TM11 ghi thời hạn dự án 50 năm cho Thác Ba, Đak Robaye, Đak Lô 4. Với r = 13,5%, đời dự án 30–40 năm vẫn giữ 97,8–99,4% giá trị vĩnh viễn.
5. **Chiều rẻ:** k = 1,081 chỉ dựa trên 3 năm, trong đó năm 2024 là ước lượng và năm 2025 chính là năm đang được chuẩn hoá. Có hai bằng chứng độc lập theo hướng sản lượng cao hơn:
   - KH 2026 của công ty lập ở mức thuỷ điện khoảng 1,15 × Etb.
   - Doanh thu điện 9T/26 đã xấp xỉ cả năm 2025.

   Cả hai chiều đã có trong bảng độ nhạy (33.560 đến 42.302), nên đây chỉ là cảnh báo.
6. **Chưa kiểm chứng được:** hạn PPA Cửa Đạt và giá sau khi trả nợ. Độ nhạy tới −12,8%, mức cắt 20% là ước lượng. Hạn nhượng quyền xử lý rác của Ngôi Sao Xanh cũng chưa rõ.

Tôi không mở `kb/dd_price_zones.json` theo ràng buộc mù của brief. Vì vậy phép so lật nhận định chỉ đối chiếu rev2 với rev3 trong chính báo cáo. Các mức giá thị trường có trong text báo cáo đã bị bỏ qua khi chấm.

<<<VERDICT_JSON>>>
{
  "case_topic": "VCP — DD rev3 (tâm 35.826 trước CK / 34.522 sau CK)",
  "mode": "DD_GENERAL",
  "verdict": "INCONCLUSIVE",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không có claim fear-buy/§2.5",
    "scandal_migration_risk": "pass — pháp lý chỉ WARNING (QĐ xử phạt thuế Cục Thuế HN trong src/), không thấy tín hiệu tịch thu tài sản/huỷ HĐ/thu hồi giấy phép; 46,8% cp cầm cố trái phiếu đã nêu",
    "optimistic_comp_sotp_bias": "fail (nhẹ) — bull = TTM Q3/26 (đã gồm lợi nhuận Linh Linh mua 03/2026 và tài sản 2026) + ΔB 427,9 theo giá sổ ⇒ đếm trùng tới ~5.100 đ/cp trên bull, ≈ −1.280 đ (−3,6%) trên tâm; trọng số 0,30/0,45/0,25 không có cơ sở (báo cáo tự nhận)",
    "data_provenance": "pass — Cửa Đạt 591.418.950 kWh/429,07 tỷ, KH2026 thuế 86,04/LNTT 562,18, Etb từng nhà máy, 83.789.658 cp đều truy được trong bctn_2025_vn.txt; md5 khoá khớp. Lỗi nhỏ: nhà máy Etb 75,81 do Nậm La sở hữu 50,06% ⇒ hiệu dụng 41,4%, không phải 66,9% (base −53 đ); tỷ lệ 2024 trong k là ước lượng (đã gắn nhãn)",
    "liquidity_capacity_realism": "na — không đề xuất vị thế; có chiết khấu thanh khoản σ√(Q/ADV60)",
    "confirmation_bias_flipflop": "fail (một phần) — giảm tâm 41,6k→35,8k dựa trên dữ liệu mới thật (BCTN25 sản lượng từng nhà máy, KH thuế 2026), OK; nhưng việc chuyển ΔB sang cộng giá sổ (V4a) đảo lại chính lập luận của rev2 dòng 256 (cách đọc A được chọn để không thưởng cho ~1.000 tỷ góp vốn chưa thuyết minh) mà không có thông tin mới (Phụ lục B mục 4 'giữ như rev2'). Không mở dd_price_zones.json theo ràng buộc của brief",
    "exit_discipline_gap": "na — không có claim sizing/vị thế; §10 có điều kiện đổi nhận định hai chiều",
    "missing_items": "fail — (1) ~1.000 tỷ góp vốn 9T/26 chưa thuyết minh + TS ngắn hạn khác 696,5 phát sinh Q3: không có haircut ở base hay bear (bear chỉ trừ lỗ cho vay 803,7), trọng yếu (~11.900 đ/cp ≈ 33% tâm), không định lượng được ⇒ INCONCLUSIVE; (2) hạn PPA/giá sau trả nợ Cửa Đạt chưa kiểm chứng (độ nhạy tới −12,8%); (3) thời hạn dự án 50 năm có trong BCTN23 TM11 (Thác Ba, Đak Robaye, Đak Lô 4) nhưng báo cáo ghi 'không kiểm chứng được' — ảnh hưởng ≤2% ở r=13,5%; (4) đạt: capex cam kết (TMĐT 2.220, tăng trưởng, vay MB), số cp 83.789.658 (BCTN25, cổ tức bằng tiền, trái phiếu riêng lẻ ≤500 tỷ không pha loãng), quỹ KT-PL 1,84%, kiểm toán KT25 chấp nhận toàn phần (rev2), one-off lãi dồn tích (độ nhạy −4,3%)"
  },
  "independent_verification": "Chạy lại chuẩn hoá thuỷ văn từ bảng giả định: trừ 104,4 tỷ, N 315,4, base 32.988, khớp; k=1 ⇒ base 29.967. Sửa sở hữu bảng 2 về 41,4% ⇒ base 32.935. Bear 2.222,5 tỷ và tâm 35.826 tái lập khớp. Đối chiếu nguồn gốc BCTN25 (sản lượng/doanh thu Cửa Đạt, KH 2026, Etb, số cp): khớp.",
  "killer_objection": "Tâm cộng toàn bộ vốn chủ theo giá sổ (N/r trên B 2025 + ΔB theo giá sổ) trong khi ~1.000 tỷ góp vốn 9T/26 và 696,5 tỷ TS ngắn hạn khác chưa thuyết minh — đúng ở chỗ rủi ro phân bổ vốn mà báo cáo tự gọi là rủi ro số 1 — không bị haircut ở kịch bản nào; khoản này ≈ 1/3 tâm.",
  "recommended_followups": [
    "Lấy thuyết minh BCTC soát xét/kiểm toán (hoặc CBTT) cho ~1.000 tỷ góp vốn 9T/26 và TS ngắn hạn khác 696,5; thêm vào bear một haircut có nguồn",
    "Bull: dùng N TTM mà không cộng ΔB, hoặc trừ phần lợi nhuận TTM do tài sản 2026 tạo ra",
    "Sửa sở hữu hiệu dụng nhà máy Etb 75,81 = 82,76% × 50,06%",
    "Trích thời hạn dự án 50 năm từ BCTN23 TM11 thay cho 'không kiểm chứng được'; tiếp tục tìm hạn PPA Cửa Đạt",
    "Nêu căn cứ của k=1,081 so với Etb thiết kế và KH 1,15 của công ty; nên dùng trung bình dài hạn từ chuỗi sản lượng nhiều năm nếu có"
  ],
  "summary": "Phép tính của rev3 đúng: base, bear và tâm đều tái lập khớp; nguồn mới (BCTN 2023/2025) truy được từng con số; chuẩn hoá thuỷ văn và thuế KH 2026 có bằng chứng độc lập. Lỗi nhỏ gồm sở hữu một nhà máy sai (−53 đ) và thời hạn dự án 50 năm có trong BCTN23 nhưng bị ghi 'không kiểm chứng được'. Hai điểm chiều đắt: bull đếm trùng ΔB với lợi nhuận TTM (≈ −3,6% tâm); và ~1.000 tỷ góp vốn cùng 696,5 tỷ tài sản ngắn hạn khác chưa thuyết minh (≈ 33% tâm) không bị haircut ở kịch bản nào, dù rev2 từng chọn cách đọc A chính để tránh thưởng cho khoản này. Chiều rẻ: k=1,081 có thể thấp so với KH 1,15 × Etb của công ty, nhưng đã có trong bảng độ nhạy. Chưa thể CONFIRMED khi khoản 1.000 tỷ chưa được định danh."
}
<<<END_VERDICT>>>