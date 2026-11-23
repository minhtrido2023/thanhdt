## Kết luận: **BÁC BỎ** (độ tin cậy trung bình). Có hai khoản thiếu, mỗi khoản đủ lượng hoá và lớn hơn 5% tâm, kéo ngược chiều nhau.

Các số trong báo cáo có dẫn giá thị trường; tôi bỏ qua và không tra giá.

**Những gì đã kiểm chứng độc lập** (đọc ảnh BCTC gốc và chạy lại `calc_rev6.py` bằng `wc_venv`):
- **Các số trên BCTC Q3 đều khớp.** Nợ vay 259,737 + 156,724 = **416,46** tỷ. Quỹ KTPL 6,33 tỷ. LNST 9T 94,36 tỷ. Thuế 9,55 / 47,66 = 20,0%. Lãi Q3 5,167 × 4 / 416,46 = **4,96%**.
- **Số cổ phiếu khớp.** Vốn góp 388,368 tỷ = 38.836.815 cp = 32.407.875 + 5.508.940 (cổ tức cổ phiếu 55,09 tỷ) + 920.000 (ESOP trả tiền).
- **Đúng là 680k cp ESOP-2 chưa phát hành.** Mã 420a lúc 30/9 là 7,365 tỷ = 65,283 − 64,718 + **6,800** tỷ, tức 6,8 tỷ ESOP chưa được trừ khỏi lợi nhuận chưa phân phối.
- **Model tính đúng tiền thu từ đợt quyền mua.** Chênh giá trị giữa kịch bản bao phủ 100% và 0% ≈ 71,7 tỷ = 75 tỷ × (1 − 4,454%).
- **Chạy lại model ra đúng tâm 16.883** (P10 13.652 / P90 20.415).

**Hướng làm tâm bị cao: phần chia cho người lao động chỉ lấy 10%**
- Bảng phân phối lợi nhuận theo NQ 486 (BCTC 6T/2026 V.19.1) ghi năm 2026 ngoài KTPL 6,43 tỷ còn **ESOP từ LNST 6,8 tỷ**. Tổng phần chia cho người lao động là **20,6%** LNST 2025.
- Các năm trước: 2024 là 21,3%, 2025 là 17,0%. Mức 10% của base chỉ thấp vì năm 2026 phần lớn đã chuyển sang ESOP. Độ nhạy "TB 3 năm 16,1%" của báo cáo cũng bỏ sót khoản ESOP này.
- Tính lại: k = 19,6% cho tâm **15.053 (−10,8%)**. Nếu trừ khoản hoàn quỹ thưởng ban điều hành 3,6 tỷ thì k ≈ 17,8%, tâm ước lượng khoảng 15.400 (−8,8%).

**Hướng làm tâm bị thấp: thiếu lá chắn thuế của nợ**
- Khung nợ mệnh giá cộng lại lãi sau thuế (tức dòng tiền đã bỏ phần tiết kiệm thuế), chiết khấu ở Ke 13,5%, rồi trừ toàn bộ nợ theo mệnh giá. Phần giá trị của lá chắn thuế không được cộng lại ở đâu.
- Giá trị lá chắn thuế tuỳ quy ước: **+643 đ** (vĩnh viễn, chiết khấu ở Ke), +913 đ (Ke, nợ tăng 4%/năm), **+1.748 đ** (t × D).
- Báo cáo đã tự nhận khung này nghiêng thận trọng nhưng vẫn để làm headline mà không có căn cứ độc lập. Điều này trái luật của user (02/11, 03/11): điều chỉnh xuống cũng cần căn cứ độc lập như điều chỉnh lên.

Hai lỗi gần triệt tiêu nhau, nên tâm có thể đúng một cách tình cờ. Nhưng model hiện tại không bền: chỉ cần sửa một trong hai là tâm lệch hơn 5%.

**Những khoản khác còn thiếu hoặc yếu**
- **Huy động vốn lặp lại không được mô hình hoá.** Năm 2025 chào bán quyền 8 triệu cp @10.000, năm 2026 thêm 6 triệu cp @12.500, cả hai để trả nợ ngân hàng. Model 5 năm tái đầu tư mặc định tăng trưởng tự tài trợ; nếu tiếp tục phát hành dưới tâm thì đây là pha loãng nghiêng xuống, chưa lượng hoá được.
- **Biến thể "bỏ thu nhập khác" trừ số gộp 4,763 tỷ.** Lẽ ra phải trừ số ròng 1,515 tỷ, vì chi phí khác 9T là 3,248 tỷ. Biến thể này vì vậy bị bi quan quá; base không bị ảnh hưởng.
- **Vẫn mở như báo cáo đã nêu:** hợp đồng nguồn tro Phả Lại và Vĩnh Tân (thời hạn, giá); capex còn lại của dây chuyền Vĩnh Tân.

<<<VERDICT_JSON>>>
{
  "case_topic": "SCL — DD rev6 (23/11/2026), tâm 16.883 cơ sở sau quyền 45.516.815 cp, CK 5 tỷ",
  "mode": "DD_GENERAL",
  "verdict": "REFUTED",
  "confidence": "medium",
  "checks": {
    "discriminator_cherry_picking": "na — DD_GENERAL; báo cáo không đưa ra luận điểm fear-buy/§2.5",
    "scandal_migration_risk": "pass — báo cáo ghi chưa thấy tin xử phạt/khởi tố (WebSearch 05/11, 08/11, 23/11); BCTC Q3/6T đã đọc không có mục pháp lý mới; tôi không tự tra web",
    "optimistic_comp_sotp_bias": "pass (kèm lưu ý) — không dùng comp; dải 5 khung định giá nợ 16.558–22.868 được công bố đầy đủ; headline nằm gần đầu dưới và bỏ sót lá chắn thuế (xem missing_items)",
    "data_provenance": "pass — nợ 416,46, KTPL 6,33, LNST 9T 94,36, thuế 20,0%, lãi 4,96%, vốn góp 388,368 tỷ = 38.836.815 cp đều khớp ảnh BCTC Q3/2026; ESOP-2 6,8 tỷ khớp 6T V.19.1; ADV120 2,35 tỷ và β=1 tái dùng từ r3, chưa kiểm lại",
    "liquidity_capacity_realism": "na — không đề xuất mua hay quy mô vị thế",
    "confirmation_bias_flipflop": "pass — bridge r4→rev6 −20,9% đi từng bước, mỗi bước có nguồn mới (cấu trúc nợ, NQ 486, ESOP-2) hoặc luật 08/11 (RONIC=Ke); chân đối chứng tái lập 21.339; không mở dd_price_zones.json theo ràng buộc của nhiệm vụ",
    "exit_discipline_gap": "na — không có luận điểm mua hay sizing",
    "missing_items": "fail — (1) CHIỀU ĐẮT: phần chia cho người lao động lấy 10% trong khi năm 2026 còn có ESOP từ LNST 6,8 tỷ; tổng là 20,6% LNST 2025 (2024 21,3%, 2025 17,0%); k=19,6% ⇒ tâm 15.053 (−10,8%), nếu trừ khoản hoàn quỹ thưởng BĐH 3,6 tỷ thì ≈ −8,8%; (2) CHIỀU RẺ: khung nợ mệnh giá thiếu lá chắn thuế: +643 đ (Ke vĩnh viễn) / +913 đ (Ke, g=4%) / +1.748 đ (t×D), tức +3,8% đến +10,4%; (3) chưa lượng hoá: huy động vốn lặp lại (quyền mua 2025 8 triệu cp @10.000, 2026 6 triệu cp @12.500, cả hai để trả nợ) — pha loãng nghiêng xuống; hợp đồng nguồn tro chưa kiểm chứng; capex còn lại dây chuyền Vĩnh Tân chưa công bố; cổ tức phải trả 0,76 tỷ chưa trừ (không đáng kể)"
  },
  "independent_verification": "Đọc ảnh BCTC HN Q3/2026 tr.2-3: nợ vay 259,737+156,724=416,46 tỷ; KTPL 6,33; LNST 9T 94,36; lãi Q3 5,167×4/416,46=4,96%; thuế 20,0% — đều khớp. Vốn góp 388,368 tỷ = 32.407.875 + 5.508.940 (cổ tức cổ phiếu) + 920.000 (ESOP) = 38.836.815 cp — khớp. 420a 7,365 = 0,565 + 6,800 ⇒ 680k cp ESOP-2 chưa phát hành — khớp. Chạy lại calc_rev6.py (wc_venv) ra tâm 16.883 / P10 13.652 / P90 20.415 — khớp đến đồng. Chênh giá trị bao phủ quyền 100%/0% ≈ 75 tỷ × (1−CK) — khớp.",
  "killer_objection": "Hệ số chia cho người lao động k=10% lấy từ đúng năm phần cash-fund thấp vì lợi nhuận đã chuyển sang ESOP miễn phí 6,8 tỷ; tổng phần chia thực tế ổn định ~17–21% LNST suốt 3 năm ⇒ tâm cao khoảng 9–11%. Khoản này đang được bù tình cờ bởi lá chắn thuế bị bỏ sót (+4–10%), nên tâm hiện tại đúng nhờ hai lỗi triệt tiêu chứ không nhờ model đúng.",
  "recommended_followups": [
    "Đổi k thành tổng phần chia cho người lao động (KTPL + thưởng BĐH + ESOP từ LNST, ròng các khoản hoàn quỹ), dùng TB 3 năm 2024–26 làm base và để 10% thành biến thể",
    "Thêm lá chắn thuế vào khung nợ mệnh giá (APV), khai rõ quy ước chiết khấu; hoặc nói rõ 13,5% là Ke có đòn bẩy và chuyển sang khung WACC nhất quán",
    "Thêm kịch bản huy động vốn lặp lại (quyền mua dưới tâm, tần suất theo lịch sử 2025–26) vào phần độ nhạy pha loãng",
    "Sửa biến thể bỏ thu nhập khác: trừ số ròng 1,515 tỷ (thu nhập khác 4,763 − chi phí khác 3,248) thay vì số gộp 4,763",
    "Tiếp tục tìm hợp đồng nguồn tro Phả Lại/Vĩnh Tân và capex còn lại dây chuyền Vĩnh Tân"
  ],
  "summary": "Các số then chốt của rev6 (nợ, KTPL, LNST, lãi, thuế, số cp, ESOP-2 chưa phát hành, tiền thu quyền mua) truy được về BCTC gốc, và calc tái lập đúng tâm 16.883. Model còn thiếu hai khoản đủ lượng hoá, kéo ngược chiều nhau. Chiều đắt: hệ số chia cho người lao động 10% bỏ qua ESOP miễn phí 6,8 tỷ cùng năm; tổng phần chia thực tế 17–21% ⇒ tâm −9 đến −11%. Chiều rẻ: khung nợ mệnh giá bỏ lá chắn thuế ⇒ tâm +4 đến +10%. Mỗi khoản vượt ngưỡng 5% nên kết luận là REFUTED theo luật attack 8. Hai lỗi gần triệt tiêu nhau nên tâm có thể đúng tình cờ, nhưng model chưa bền. Pha loãng do huy động vốn lặp lại để trả nợ là rủi ro nghiêng xuống chưa được lượng hoá."
}
<<<END_VERDICT>>>