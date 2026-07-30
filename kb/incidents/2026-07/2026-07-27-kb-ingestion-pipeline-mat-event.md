---
kind: incident
date: 2026-07-27
topic: kb-ingestion-pipeline-mat-event
title: >-
  2026-07-27/28: KB-ingestion pipeline mất event âm thầm 9h, rồi chuỗi fix của chính nó gây thêm 2 lớp mất event mới — 5 vòng review độc lập trước khi đóng
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-27/28: KB-ingestion pipeline mất event âm thầm 9h, rồi chuỗi fix của chính nó gây thêm 2 lớp mất event mới — 5 vòng review độc lập trước khi đóng

**Hiện tượng ban đầu (07-27):** mở rộng cơ chế "dọn heartbeat cũ" (tuần trước, commit `7cc47cb`,
áp cho `bus/inbox/*.jsonl`) sang `kb/events_buffer.md` (cùng loại rác, chưa từng được vá). Trong
lúc làm, Wags phát hiện: `kb_nightly.sh` Phase 1b/1b2 (dọn `bus/inbox/*.jsonl` mỗi đêm) xén bớt
dòng heartbeat cũ, làm TỔNG SỐ DÒNG của file giảm — nhưng `consolidate.sh` (chạy mỗi giờ, dùng
cursor kiểu "đã đọc N dòng") KHÔNG hạ cursor theo. Hệ quả: `if total > prev` sai vĩnh viễn cho
9/11 agent → `consolidate.sh` **ngừng ingest event mới hoàn toàn, âm thầm, từ ~07:05Z tới khi
phát hiện lúc ~12:41Z (~5,5 giờ)**. Không ai biết vì tín hiệu duy nhất là 1 dòng echo vào
`logs/consolidator.log`, không ai đọc file này.

**Root cause gốc:** offset/cursor dựa trên SỐ DÒNG TRẦN, không mang thông tin nội dung — bất kỳ
thao tác nào làm thay đổi độ dài file (xén bớt) mà không đồng bộ cập nhật cursor sẽ làm cursor
sai lệch, và sai lệch đó không tự báo hiệu gì.

**Chuỗi fix (5 vòng review độc lập, MỖI VÒNG tìm ra ít nhất 1 lỗi thật khác nhau — không phải
góp ý phong cách):**

1. **Round 1** (commit `d2915c3`): fix regression riêng trong chính bản vá đầu — cursor được
   ghi xuống đĩa TRƯỚC KHI payload kịp flush ra buffer. Một SIGTERM giữa 2 bước đó (bình thường
   với job nền của fleet) làm cursor tiến lên trong khi payload = 0 byte → mất event vĩnh viễn,
   hoàn toàn im lặng, tệ hơn cả lỗi gốc. Fix: `sys.stdout.flush()` trước khi ghi cursor.
2. **Round 2-3** (thương lượng thành commit `0f2a8ab` → `fd76e61`): chuyển cursor từ số dòng
   trần sang neo theo NỘI DUNG (`event_id`+`ts`), đóng 2 chế độ mất event (cursor kẹt / nhảy
   cóc bỏ event) — nhưng khi implement lộ thêm 2 lỗ hổng (đếm-nhầm-vị-trí ở dòng rách/trống;
   nhánh `last_id=null` bỏ qua event không báo động), cả 2 được vá trong cùng chuỗi.
3. **Round 4** (commit `be8e93b`): 1 hardening không-chặn từ review trước (`bounded-replay` khi
   dòng cuối bị rách) hoá ra TỰ NÓ quá rộng — áp cả khi vẫn còn thông tin `ts` đáng tin, làm
   **mất 100/150 event thật** trong kịch bản "prune không qua `cursor_shift`" (đúng lớp lỗi gốc
   07-27), và dòng cảnh báo ghi `recovered=0` nên mất mà không ai thấy. Thu hẹp lại: chỉ bound
   khi HOÀN TOÀN không có `ts` (last_ts=None), giữ nguyên scan không giới hạn khi còn `ts`.
4. **Round 5** (commit `c30e4d4`): tìm ra ĐƯỜNG THẬT khiến `last_ts=None` xảy ra trong sản
   xuất — `append_event.sh`'s `printf` không ghi 1 dòng lớn (>4KB) bằng 1 `write()` nguyên tử
   (strace xác nhận: dòng 14KB tách thành 2 lần `write()`), và `consolidate.sh` đọc file không
   giữ khoá cùng `append_event.sh` → có thể đọc trúng lúc dòng đang ghi dở (đo thật: 149/2111
   event sống >4KB, race test đo được 19/153.676 lần đọc bị rách). Fix gốc rễ: bỏ dòng cuối
   không kết thúc bằng `\n` TRƯỚC khi xử lý — 1 dòng chưa có dấu kết thúc về định nghĩa không
   phải 1 event hoàn chỉnh, bỏ qua kỳ này thì kỳ sau (khi writer ghi xong) sẽ được nạp bình
   thường, không mất.

**Cũng trong round 4/5:** `kb_nightly.sh` Phase 0 mới (chạy `bin/cursor_advance_selfcheck.py`,
42 assertion, trước mọi phase archival) — ban đầu chỉ CẢNH BÁO rồi vẫn chạy tiếp phase dọn dẹp
bằng logic vừa bị phát hiện lỗi (round 5 chỉ ra: phát hiện mà không chặn = không phải fail-safe
pause) — đã sửa thành GATE thật: selfcheck fail → Phase 1b/1b2 (đụng `bus/inbox` + `cursor_shift`)
bị SKIP đêm đó, không tiếp tục dùng logic đã biết hỏng.

**Bài học chính, áp dụng ngoài phạm vi bug cụ thể này:**
- **"Đã test kỹ" trong commit message không phải bằng chứng** — bộ test tạm (ad-hoc, không
  commit) của round 1-3 đã "PASS" trên chính bản có bug round-4 phát hiện. Chỉ có bộ test
  CỐ ĐỊNH, commit vào repo, mới đáng tin theo thời gian.
- **1 review CONFIRMED không đủ cho hạ tầng lõi chạy liên tục** — 4/5 vòng review liên tiếp
  đều tìm ra lỗi thật KHÁC NHAU trên cùng 1 đoạn code nhỏ (~150 dòng). Đây không phải do agent
  cẩu thả — là bằng chứng cụ thể cho việc concurrency/torn-write/silent-loss là lớp lỗi khó, cần
  nhiều góc nhìn độc lập mới phủ hết.
- **Sửa TRIỆU CHỨNG (bound lại 1 nhánh) dễ tạo lỗ hổng MỚI hơn là sửa GỐC RỄ** (bỏ dòng chưa
  hoàn chỉnh tại nguồn) — round 4 patch nhánh resync-ts 2 lần trước khi round 5 nhận ra vấn đề
  thật nằm ở TẦNG ĐỌC FILE, không phải tầng xử lý cursor.
- **Phát hiện lỗi rồi vẫn chạy tiếp bằng logic đã biết hỏng = không phải fail-safe** — đúng
  nguyên tắc `coding_guidelines.md` §5 áp dụng ngược lại cho chính pipeline giám sát.

**Verify cuối cùng:** `bin/cursor_advance_selfcheck.py` 42/42 assertion (commit vào repo, gắn
vào `kb_nightly.sh` Phase 0 chạy mỗi đêm — không còn là test tạm bị bỏ quên như các vòng trước);
`bash -n`/`py_compile` sạch; `data_registry_audit.sh` FAIL=0/WARN=0; chạy `consolidate.sh` thật
trên `bus/inbox` sống nhiều lần, steady-state đúng, 0 cảnh báo giả.

**Còn treo:** không có — round 5 là vòng review cuối, verdict CONFIRMED sau khi fix gốc rễ (round
5 tự đề xuất) đã áp dụng. Entry này chính là hạng mục "viết postmortem" mà round 5 chỉ ra còn
thiếu (trước đó lý do/đánh đổi duplicate-vs-drop chỉ nằm trong commit message + code comment).
