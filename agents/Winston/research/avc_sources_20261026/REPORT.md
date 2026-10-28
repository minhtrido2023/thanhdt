# REPORT — Nguồn thay thế bản tin Công Thương, chỉ báo A Vương / Sông Bung 4 (job Winston_20261025_085247, 2026-10-25)

## Kết luận
**Không có nguồn công khai nào cho số liệu HẰNG NGÀY (mực nước, Q về, Q xả) của A Vương / SB4 / SB4A phủ 01–25/10/2026: 0/25 ngày ở cả 3 hướng.** Không nội suy. CSV `avc_daily_202610.csv` ghi 25 dòng trống có lý do.
Lưu ý phương pháp: tôi dùng curl + WebFetch + WebSearch (không trình duyệt JS, không đăng nhập). "Không tìm thấy" ≠ "không tồn tại" — hướng 2 có hệ thống JS (luquetsatlo) chưa đọc được.

## Hướng 1 — EVNGENCO2 / Cục KTAT&MTCN
- `evngenco2.vn/vi/news/tin-tuc` (200): chỉ có tin hoạt động; 10 tin gần nhất (tới 20/10/2026) không có số vận hành. Bài vận hành lũ (vd 17/06/2025: SB4 đỉnh 894,7 m³/s ngày 12/06/2025) là **bài rời, sau sự kiện**, không có mục số liệu ngày. Menu chỉ có Tin tức/Báo cáo (tài chính)/Công bố thông tin. robots.txt tồn tại (200), chưa đọc điều khoản.
- Cục KTAT&MTCN `atmt.gov.vn`: không kết nối (HTTP 000). `moit.gov.vn/tin-tuc/phat-trien-nang-luong` (200) có tin 2026 nhưng không thấy bản "Tình hình hồ thủy điện ngày X" năm 2026 (các bản tìm được đều 2023, URL dạng `/tinh-hinh-ho-thuy-dien-ngay-D-M-...`). → **Chuỗi ngày đã ngừng; độ phủ 0/25.**
- Lịch sử: chỉ tới 12/2023 (xem báo cáo avc_bulletin_20261025).

## Hướng 2 — hydro.gov.vn / vndms / KTTV
- `hydro.gov.vn`, `vndms.dmc.gov.vn`: **không kết nối** (000) từ máy này. (Lưu ý: lần chạy đầu in nhầm title cũ từ file tạm — đã kiểm lại, kết luận là 000.)
- `kttv.gov.vn/kttv/` (200) có mục "Bản tin dự báo thủy văn hằng ngày phục vụ quy trình liên hồ chứa… trong mùa lũ" nhưng chỉ cho **sông Mã–Chu, Ba, Kon, Srepok, Trà Khúc, Đồng Nai, Hồng** — **KHÔNG có Vu Gia–Thu Bồn** (thử đoán pattern `dbqg_{vgtb,vghn,...}` → 404). Bản Trà Khúc ngày có pattern ổn định `.../upload/thuyvan{1|2}/YYYY/M/D/dbqg_tkhn_YYYYMMDD_1500.pdf` nhưng là lưu vực Quảng Ngãi, không dùng được.
- Tin lũ quốc gia `dbqg_lulu_YYYYMMDD_{0900,1530,2100}.pdf` (pattern ổn định, thư mục `thuyvan1`/`thuyvan2` đổi tuỳ ngày): **21 bản tồn tại cho 02–11/10/2026, 0 bản cho 01 và 12–25/10** (quét 5 mốc giờ × 25 ngày). Đã tải + đọc: toàn bộ nói về sông khác (Đồng Nai/Tà Lài, Hà Tĩnh–Huế); **0/21 nhắc A Vương, Sông Bung, Vu Gia, Câu Lâu**. Mẫu 2025 (30/10/2025 21h) có mực nước trạm Câu Lâu + kịch bản vận hành A Vương/SB4 — nên bản tin chỉ nhắc A Vương khi có lũ Vu Gia. → Suy luận mềm: **không có lũ Vu Gia đáng cảnh báo 01–25/10/2026** (không có bản tin = tín hiệu vắng mặt, chưa xác nhận bằng nguồn khác, theo §28).
- Trạm Thành Mỹ / Ái Nghĩa: không có trang công khai đọc được. `luquetsatlo.nchmf.gov.vn` (200) là ứng dụng JS (Kendo/AG-Grid), không có API công khai tôi tìm được (`/HoChua` 404) → cần trình duyệt có JS; chưa thử.
- Điều khoản: kttv.gov.vn robots.txt chỉ cấm đường kỹ thuật, không cấm `/upload/`; ToS chưa đọc.

## Hướng 3 — thông báo xả lũ BCH PCTT Quảng Nam/Đà Nẵng (09–10/2026)
**Không tìm thấy đợt xả nào của A Vương/SB4 trong 09–10/2026** (3 truy vấn, gồm extended). `discharge_events_202609_202610.csv` = 1 dòng "none_found". Mọi kết quả là 2020/2022/2025 (vd 26/10/2025: BCH PCTT ĐN yêu cầu A Vương ≤372 m; SB4 đỉnh về 2.029 m³/s ngày 27/10/2025, xả 639 m³/s). Tin 2026 duy nhất: kiểm tra an toàn đập (QĐ 1926/QĐ-UBND 6/5/2026) và EVN "sẵn sàng cấp nước mùa khô 2026". Cổng danang.gov.vn có bài thông báo dạng này (vd 06/11/2025: A Vương về +371 m, SB4 +216,5 m, **không có Q**) → ngay cả khi có, thông báo **chỉ cho cao trình, hiếm khi có Q xả**, và chỉ phát sinh khi có lũ.

## Nhận xét thô: đầu mùa lũ 2026 A Vương/SB4 giữ nước hay xả nhiều?
**Không có số thật → không kết luận.** Chỉ có bằng chứng vắng mặt (không bản tin lũ Vu Gia, không thông báo xả 09–10/2026) gợi ý chưa có đợt xả lớn, nhưng đó không phải đo lường.

## Đề xuất thu thập hằng ngày (KHÔNG cài cron)
1. **Quét tin lũ KTTV** — rẻ, ổn định: mỗi ngày 18:00 ICT thử HEAD các URL `dbqg_lulu_YYYYMMDD_{0900,1530,2100}.pdf` × `thuyvan{1,2}`, tải bản mới, trích text (pypdf), ghi dòng `date,time,url,mentions_avuong/vugia(bool),WL_Cau_Lau` vào CSV, idempotent theo (ngày,giờ). Giá trị: cờ "có lũ Vu Gia" (sự kiện), không phải Q xả.
2. **Tìm tin xả lũ** bằng RSS/trang thẻ `danang.gov.vn` + `tapchicongthuong.vn/hashtag/thuy-dien-song-bung-4-15232.htm` (có thể dò từ khoá "A Vương"/"Sông Bung 4" + "xả"), ghi ngày/giờ/cao trình/Q nếu có.
3. **Việc đáng làm nhất nếu cần Q xả thật:** hỏi **AVC (CTCP Thủy điện A Vương) / EVNGENCO2** qua kênh nhà đầu tư, hoặc thử trình duyệt có JS vào `luquetsatlo.nchmf.gov.vn` (hồ chứa) — cần user duyệt vì ngoài phạm vi curl.
Rủi ro: URL KTTV đổi thư mục/giờ; PDF không có số hồ; anti-bot nếu quét dày (giữ ≤ 1 lượt/ngày); đổi cấu trúc trang tin.
