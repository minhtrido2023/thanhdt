# Hàng chờ xác nhận tay — nhãn `skeptic_final` backfill MƠ HỒ (A2, 22/11/2026)

20/95 entry có `skeptic_final_basis=ambiguous_backfill` (luật cố định không đọc chắc được từ văn bản tự do ⇒ gán `FIXED_UNVERIFIED`, KHÔNG tự gán CONFIRMED). **Hạn xác nhận tay: 29/11/2026** (Mike; ưu tiên mã đang giữ / rev cuối). Đóng một mục = thêm rev mới hoặc ghi quyết định vào đây; KHÔNG sửa tại chỗ nhãn của entry cũ (sổ append-only).
Cách cập nhật khi có vòng skeptic MỚI trên cùng một DD: thêm **rev mới** với `skeptic_final` mới + `skeptic_final_basis: "skeptic_run"` + `skeptic_verdict_path` tới file verdict thật + `correction_reason` (không sửa entry cũ).

| # | mã@dd_date#rev | rev cuối của mã? | nhãn gán | skeptic_status (trích 160 ký tự) |
|---|---|---|---|---|
| 4 | HPG@2026-10-31#1 | — | FIXED_UNVERIFIED | CONFIRMED (medium; B1/B2 đã sửa; v3) |
| 5 | MBB@2026-10-31#1 | — | FIXED_UNVERIFIED | CONFIRMED (medium; 1 BLOCKING MBV đã xử) |
| 8 | DRI@2026-10-30#1 | — | FIXED_UNVERIFIED | CONFIRMED (medium; định giá r4) |
| 11 | PVT@2026-10-29#1 | — | FIXED_UNVERIFIED | CONFIRMED phân loại NON; định giá đã đính chính (REPORT §14) |
| 22 | HPG@2026-10-31#2 | — | FIXED_UNVERIFIED | CONFIRMED (medium; B1/B2 đã sửa; v3) |
| 23 | MBB@2026-10-31#2 | — | FIXED_UNVERIFIED | CONFIRMED (medium; 1 BLOCKING MBV đã xử) |
| 25 | HPG@2026-10-31#3 | — | FIXED_UNVERIFIED | CONFIRMED (medium; B1/B2 đã sửa; v3) |
| 30 | TV1@2026-11-02#5 | — | FIXED_UNVERIFIED | định giá nội tại dựng mù giá (khoá md5 trước khi so giá) + phản biện độc lập mù giá + phản biện báo cáo cuối (tái lập byte-for-byte; sửa cân bằng cờ kế toán)  |
| 31 | MVC@2026-11-03#1 | — | FIXED_UNVERIFIED | định giá SOTP dựng mù giá (khoá md5 calc/LOCK_md5*.txt trước khi so giá) + fundamental-skeptic CONFIRMED (12 đính chính đã áp; tâm/vùng không đổi) |
| 33 | MVC@2026-11-03#3 | — | FIXED_UNVERIFIED | định giá SOTP r3 mù giá (khoá md5 r3/calc/LOCK_md5_r3.txt); fundamental-skeptic vòng 3 CONFIRMED (medium) tâm 20.181 và vùng 17.500–22.900; r4 chỉ đổi thang nhã |
| 34 | NNC@2026-10-31#3 | — | FIXED_UNVERIFIED | mô hình nhất quán MVC r3 qua skeptic vòng 3 (CONFIRMED medium, phía MVC); NNC rev 3 chưa có vòng phản biện riêng |
| 67 | SZL@2026-10-26#2 | CÓ | FIXED_UNVERIFIED | r3c (09/11, cụm 3b): A (RONIC=Ke) skeptic cuối r3b xác nhận cài đúng; B cài sai khung ở r3b đã sửa ở r3c (khung BÁN, KTPL trên lãi vốn sau thuế) — r3c Mike kiểm |
| 72 | MSB@2026-11-09#1 | CÓ | FIXED_UNVERIFIED | r2 (09/11): skeptic r1 CONFIRMED (medium) với 7 đính chính câu chữ/độ nhạy (room tín dụng đã quan sát, phải thu RRTD 4.101, NPL, kịch bản XẤU bất đối xứng 11%→1 |
| 73 | HHS@2026-11-01#4 | CÓ | FIXED_UNVERIFIED | r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253) |
| 74 | SCL@2026-10-29#5 | CÓ | FIXED_UNVERIFIED | r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253) |
| 78 | PNJ@2026-11-14#1 | CÓ | FIXED_UNVERIFIED | vòng 1 fundamental-skeptic CONFIRMED (medium) cho giữ loại; khối định giá KHÔNG xác nhận — 10 thay đổi đã áp ở r2 (bỏ nhãn mù giá, biên gộp trước dự phòng, vay  |
| 82 | PAT@2026-11-14#4 | — | FIXED_UNVERIFIED | skeptic lần 2 (15/11) mù giá hai chiều: lạc quan REFUTED nhẹ (tâm hiệu chỉnh 56.100, −13,4%: nút T bất đối xứng, vận chuyển 4,69%, O1), bi quan CONFIRMED (68.00 |
| 85 | PAT@2026-11-17#1 | — | FIXED_UNVERIFIED | phản biện user 17/11: 4 agent kiểm dữ kiện + quant-skeptic cohort cổ tức (CONFIRMED, tin cậy TB, có đính chính); 2 skeptic mù giá trên r3 66.864 (lạc quan CONFI |
| 89 | QTP@2026-11-17#3 | CÓ | FIXED_UNVERIFIED | fundamental-skeptic vòng 1 (r3): INCONCLUSIVE; vòng 2 (r3b): CONFIRMED, độ tin cậy trung bình; đã áp đính chính (r3c: lỗi bù FOM+VC 2030–31, điều kiện huỷ có ng |
| 92 | PAT@2026-11-17#2 | CÓ | FIXED_UNVERIFIED | r5 (22/11, user duyệt) áp 7 mục từ skeptic r4; CHƯA chạy skeptic trên r5 (Taylor khuyến nghị bác/xác nhận lựa chọn đọc H1/26 'sạch'). Mike 22/11: assumptions md |
