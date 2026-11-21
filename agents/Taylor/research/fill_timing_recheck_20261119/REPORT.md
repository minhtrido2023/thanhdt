# REPORT — fill_timing HYBRID recheck (job Taylor_20261119_044040) — CHƯA qua quant-skeptic
PREREG md5 `93638a29cfc701d0d04b7986492edd3e` (khoá trước khi chạy). Engine: `engine.py` (1m, 16 mã), `engine15.py` (15m, 335 mã). Không đổi config live, không lệnh/tiền thật.

## 1. Kết luận
- **KHOẢNG TRỐNG DỮ LIỆU: không có intraday sau 2026-06-12** (1m) / 2026-05-12 (15m). Giai đoạn thị trường giảm 06→11/2026 **chưa được kiểm**; không có OOS thật. Tất cả dữ liệu có TRƯỚC khi luật được duyệt (bus 06-26; live 08-26). Không tự fetch VCI/DNSE (theo chỉ đạo).
- **BUY blocks (11:00–13:30) rẻ hơn open: PASS theo prereg** trên dữ liệu có sẵn: −18,0 bps CI95 [−23,8; −12,5] (16 mã, 686 phiên); không đổi dấu ở nhóm ngày giảm. Robust 15m/335 mã: −20,9 [−25,9; −16,1] (663 phiên). Xa ngưỡng rollback +22 bps.
- **SELL blocks (09:15–10:00) vs open: KHÔNG PASS.** −1,2 bps [−3,2; +0,7] (1m); 15m/335 mã +2,6 [+0,6; +4,5] nhưng <+5 bps; nhóm ngày giảm âm (−7,1 / −8,4). Block 09:15 = chính open nên pha loãng; không có bằng chứng bán trong block tốt hơn bán ở open. Đây là chỗ "chưa chứng minh", không phải bằng chứng luật sai.
- **Cảnh báo diễn giải:** nhóm "ngày giảm" xác định EX-POST (median lợi suất ngày <0) nên lợi thế BUY ở đó phần lớn cơ học (giá trôi xuống trong ngày) — không dùng làm bộ lọc live. Ngày TĂNG, BUY block ĐẮT hơn open: +7,8 bps (1m, [+1,9; +13,6]); cửa sổ B +30,7. Edge BUY trung bình = đánh đổi: rẻ nhiều ở ngày giảm, đắt ở ngày tăng; phụ thuộc tỉ lệ ngày giảm trong mẫu (45% ngày trong 1m).

## 2. Bảng chính (bps so với open ngày; BUY âm = tốt, SELL dương = tốt). Nguồn: results_1m.csv, results_15m_335.csv
| Panel / cửa sổ | BUY all | BUY ngày giảm | BUY ngày tăng | SELL all | SELL ngày giảm |
|---|---|---|---|---|---|
| 1m 16 mã A 2023-09→2025-12 (n=579) | −18,3 [−24,6;−12,4] | −48,6 | +4,5 [−1,6;+10,2] | −1,3 [−3,6;+0,9] | −6,3 |
| 1m 16 mã B 2026-01→06-12 (n=107)* | −16,2 [−29,3;−3,3] | −52,9 | +30,7 [+14,3;+47,1] | −0,8 [−4,4;+3,0] | −10,5 |
| 1m 5 mã thanh khoản thấp, ALL | −15,5 [−23,9;−7,9] | −59,3 | +20,5 | +0,8 [−5,5;+6,2] | −17,5 |
| 15m 335 mã B 2026-01→05-12 (n=84) | −19,2 [−27,3;−10,7] | −54,5 | +12,9 [−2,3;+30,0] | −1,7 [−6,3;+2,5] | −15,7 |
| 15m 335 mã, 20% thanh khoản thấp nhất, ALL | −28,1 [−34,2;−22,3] | −69,5 | +0,7 | +1,7 [−1,5;+4,6] | −16,1 |
*B không phải OOS thật (xem §1). Theo từng block (ALL, 1m): 11:00 −13,5 · 11:15 −17,4 · 13:00 −23,0 · 13:15 −20,1 · 13:30 −16,1; SELL 09:30 −3,2 · 09:45 0,0 · 10:00 −2,3.

## 3. Self-check
- Control: `intraday_fill_timing.py` gốc cho open +18,7 / 11:15 +1,1 bps (n=9670); engine mới tái lập **+18,73 / +1,09 (n=9670)** (lần đầu lệch +19,2/+1,6 do bỏ ngày <50 bar khỏi chuỗi prior-close — đã sửa trước khi báo; file selfcheck_control.csv).
- Point-in-time: chỉ dùng tỷ số trong cùng ngày + prior close; không dùng cột forward. Giá điều chỉnh: tỷ số trong ngày không phụ thuộc điều chỉnh; control kế thừa xử lý của script gốc (1m là giá chưa tra rõ thô/điều chỉnh — HPG 2023-09 ghi 19,61 gợi ý đã điều chỉnh; chưa xác minh).
- 15m: lọc ngày open ≤0 hoặc |lệch|≥1500 bps (lỗi chia 0 ở lần chạy đầu, đã sửa). Bootstrap khối tuần ISO, 10.000 (1m) / 5.000 (15m), seed 0.
- Giới hạn: 16 mã thanh khoản tương đối cao; "5 mã thanh khoản thấp" vẫn là mã khá lớn; ước lượng fill = giá open bar phút, chưa mô hình hàng đợi/khối lượng (không nói lên fill thực). Chưa tính phí (0,097%/chiều, bằng nhau cho mọi lịch nên triệt tiêu trong so sánh).
- Không đối chiếu được với "mã ta thực sự giao dịch": journal fills không nằm trong phạm vi tác vụ này; chỉ có 15m 335 mã phủ phần lớn universe. Việc monitor live (fill-vs-open ~10 phiên) vẫn là nguồn duy nhất cho 06→11/2026.

## 4. Đề xuất (chỉ đề xuất, chưa qua Opus skeptic)
1. Giữ nguyên lịch live — không có tín hiệu rollback; BUY edge tái lập.
2. Lấp khoảng trống: xin duyệt để Winston/Mafee kéo intraday 06-13→hôm nay (hoặc log fill thực của 2 tài khoản) rồi chạy lại ĐÚNG prereg này trên cửa sổ OOS thật.
3. SELL block: cân nhắc kiểm riêng "bán ở open" vs block (cần tách 09:15 khỏi trung bình); chưa đề xuất đổi.
