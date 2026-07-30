---
kind: incident
date: 2026-07-12
topic: lag-edge-health-2-tien-de-sai
title: >-
  2026-07-12 — `lag_edge_health.csv`: 2 tiền đề sai liên tiếp về "bug staleness/catch-up" bị bác bỏ sau điều tra sâu — không có bug thật, tốn 2 chu kỳ dispatch để xác nhận
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-12 — `lag_edge_health.csv`: 2 tiền đề sai liên tiếp về "bug staleness/catch-up" bị bác bỏ sau điều tra sâu — không có bug thật, tốn 2 chu kỳ dispatch để xác nhận

**Hiện tượng:** trong ngày, `lag_edge_health.csv` (file tracking hiệu suất lịch sử LAG,
dùng để tính `mean12` cho allocator w_LAG) bị nghi ngờ có bug/staleness **2 lần độc lập**,
mỗi lần dẫn tới 1 dispatch "hãy sửa" trước khi có ai verify premise là đúng hay sai:

- **Tiền đề #1 (nguồn: dispatch ban đầu của Mike, KHÔNG verify trước)** — "không có lịch
  refresh tự động" cho file này. Dispatch Winston điều tra/sửa (`Winston_20260712_114800`)
  → **SAI**: `edge_health_monitor.py --refresh` đã là step [22] của `papertrade_daily.sh`,
  cron `30 8 * * 1-5` (15:30 ICT), chạy `[ok]` mọi ngày giao dịch, gần nhất 07-10. Data
  dừng ở 2026-05-11 là **hành vi ĐÚNG** — hết mùa BCTC Q1 (hạn nộp 30/04, entry hợp lệ
  cuối = release+5+25 phiên hold = 05-11), không phải thiếu refresh. Winston tự chạy thật
  `--refresh` bằng đúng env production để verify độc lập (CSV rewrite, nội dung
  byte-identical — đúng kỳ vọng không có event mới).
- **Tiền đề #2 (nguồn: chính audit `Winston_20260712_151206`, phát hiện phụ "F2" trong
  lúc dọn cron paper-trading)** — "cron có nhưng `--refresh` không catch-up chuỗi LAG
  edge, bug nằm TRONG script". Dispatch Taylor điều tra/sửa (`Taylor_20260712_155038`) →
  **CŨNG SAI**: `lag_edge_health()` chạy VÔ ĐIỀU KIỆN mỗi lần invoke (không phụ thuộc flag
  `--refresh`, chỉ ảnh hưởng `edge_panel.csv` khác), rebuild toàn bộ series từ cache
  daily-refreshed mỗi lần chạy. BQ live xác nhận **zero** sự kiện NP_R từ 05-05→07-07
  (khoảng trống thật giữa 2 mùa BCTC). Taylor báo cáo lại premise sai thay vì tự mở rộng
  sửa code (đúng kỷ luật `verify_finding.sh`/dispatch instruction #6) — **KHÔNG sửa code
  nào**.

**Kết luận cuối cùng:** verdict TROUGH hiện tại (mean12 +0.45%, n=631) là số đúng và tươi
nhất có thể có — không có gap production nào ở đây. Probe WARN-only mtime-check (commit
`f67e09a`, ra đời từ tiền đề #1, vẫn giữ vì bản thân nó vô hại và đúng đắn — cảnh báo khi
mtime quá cũ so ngưỡng) không liên quan gì tới 2 lần nhầm lẫn content này.

**Root cause (cả 2 lần):** một CLAIM về hành vi thực tế của 1 script/pipeline ("không có
refresh", "refresh không catch-up") được đưa vào dispatch dưới dạng tiền đề ĐÃ XÁC NHẬN,
trong khi thực ra chỉ là suy luận từ triệu chứng bề mặt (file dừng ở 1 ngày cũ trông giống
"stale"; tên flag `--refresh` gợi ý nó phải catch-up mọi thứ) — không ai đọc code thực thi
+ đối chiếu BQ ground-truth TRƯỚC khi dispatch "đi sửa". Cả 2 lần chỉ được bác bỏ khi
người nhận dispatch (Winston lần 1, Taylor lần 2) tự đọc code + tự verify độc lập thay vì
tin tiền đề và bắt đầu sửa ngay.

**Bài học:** đây là biến thể MỚI của nguyên tắc "trust the artifact, not self-report"
(MIKE.md #2) — không phải áp dụng cho TRẠNG THÁI JOB (đã biết, đã có cơ chế) mà cho
**CLAIM CHẨN ĐOÁN** ("có bug ở đây") được truyền xuống dispatch tiếp theo dưới dạng tiền
đề. Điểm tích cực: cả 2 lần agent nhận việc đều làm ĐÚNG — không âm thầm "sửa cho khớp
tiền đề", mà tự verify trước, phát hiện premise sai, báo cáo lại thay vì mở rộng phạm vi
tự chế ra 1 bug để sửa. Cái tốn kém duy nhất là 2 chu kỳ dispatch (khoảng 20-45 phút mỗi
lần) — không có rủi ro production nào phát sinh vì không code nào bị sửa sai.
