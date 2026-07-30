---
kind: incident
date: 2026-07-17
topic: model-tier-drift-fable
title: >-
  2026-07-17 — Model-tier drift: fable đi từ 0%→58% dispatch trong 3 tuần, compute wall-clock +150% dù job count -76% (user hỏi "token tăng dù không research nặng")
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-17 — Model-tier drift: fable đi từ 0%→58% dispatch trong 3 tuần, compute wall-clock +150% dù job count -76% (user hỏi "token tăng dù không research nặng")

**What happened:** user quan sát chi phí vận hành tăng dù không có research nặng nào 3 tuần
qua, hỏi Mike (với vai chuyên gia thiết kế hệ agent) tìm nguyên nhân chính. Đo `bus/jobs/`
thật (975 job record, 2026-06-27→07-17): job count giảm 76% (tuần "3 tuần trước" 688 job →
tuần này 168 job), nhưng tổng compute wall-clock (`ended_at - started_at`) TĂNG 150%
(12.2h→30.4h) và kích thước `kb/context_pack.md` (nạp vào mọi dispatch) phình x6.3
(7.8KB→48.9KB). Đếm job/log-bytes (chỉ báo `bin/spend_report.py` bản đầu, cùng ngày) sẽ hoàn
toàn BỎ SÓT phát hiện này — job count giảm trông như tin tốt.

**Root cause:** 3 nguyên nhân cộng dồn, xếp theo mức ảnh hưởng:
1. **Model-tier drift, lớn nhất**: 3 tuần trước `--model` chưa tồn tại (100% "default"). Tuần
   này 58% tổng dispatch dùng **fable** (tier đắt nhất, chính sách ladder ghi rõ "dùng dè,
   chỉ cho task cực kỳ phức tạp"). Trong 94 dispatch fable tới Taylor/Winston tuần đó, chỉ 12
   đến từ pipeline tự động (`ops_autofix.sh`) — **82 là Mike tự chọn tay**, đọc mẫu prompt
   thấy phần lớn là audit cron order/dọn crontab lạc hậu/fix bug dữ liệu/soạn báo cáo bỏ
   sót — đúng tầm Opus (Q2) theo chính ladder Mike tự viết, không phải Q3.
2. **`kb/context_pack.md` phình x6.3** — cụ thể là `kb/current_ops.md` (0 byte 3 tuần trước
   → 36KB hôm nay), vì narrative sự cố ĐÃ GIẢI QUYẾT tích lại trong mục "Đang trading (LIVE)"
   thay vì rút gọn về `kb/INCIDENTS.md` sau khi đóng — quy ước archive hiện chỉ áp cho cả dự
   án R&D (`kb/projects/`), chưa áp cho narrative sự cố ngắn hạn.
3. **2 pipeline tự sửa mới** (`ops_autofix.sh` 07-06, `wags_autofix.sh` 07-07 — cả 2 không
   tồn tại 3 tuần trước) hardcode `--model fable` vô điều kiện cho MỌI issue bất kể độ phức
   tạp; `arch-reviewer.md` cũng cấu hình cứng `model: fable`.
(Bug tiêm context 2 lần từng cộng dồn thêm vào #2 suốt 3 tuần — đã sửa cùng ngày trước sự cố
này, xem entry riêng nếu cần, không lặp lại ở đây.)

**Fix:**
- Hạ default fable→opus: `ops_autofix.sh`, `wags_autofix.sh` (2 call-site), `arch-reviewer.md`.
- `dispatch.sh` in 1 dòng nhắc ra stderr mỗi lần `--model fable` được dùng — không chặn, chỉ
  nhắc lại câu hỏi Q3 của ladder tại đúng thời điểm chọn.
- `bin/spend_report.py` viết lại: chỉ số chính đổi từ job-count/log-bytes sang **compute giờ
  + %model-mix** (đúng chỉ số bắt được sự cố này); tự in cảnh báo khi %fable tổng ≥30%.
- MIKE.md §Model routing: thêm đoạn ghi lại sự cố này kèm số liệu đo được, làm ví dụ cụ thể
  thay vì chỉ có quy tắc trừu tượng.
- `kb_nightly.sh` Friday review thêm mục 5b: đọc %fable từ `spend_history.csv`, nếu ≥30% thì
  đối chiếu mẫu prompt xem có đúng là "cực kỳ phức tạp" hay không.

**Lesson:** (1) Chính sách viết đúng KHÔNG tự động được tuân thủ — cần cả nhắc-tại-thời-điểm
(dispatch.sh stderr) lẫn đo-lường-sau (spend_report %fable) làm 2 lớp bổ trợ, không chỉ dựa
vào tài liệu. (2) Đo bằng chỉ số SAI (job count) có thể che khuất hoàn toàn vấn đề thật —
`compute_h`/model-mix mới là chỉ số đúng cho "chi phí", không phải "khối lượng việc". (3) Tự
động hoá tốt (self-healing autofix, mandate hợp lý) vẫn có thể mang theo cấu hình mặc định
sai (hardcode fable) nếu không rà lại default sau khi triển khai.
