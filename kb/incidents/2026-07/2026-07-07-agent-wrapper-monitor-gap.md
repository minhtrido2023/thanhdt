---
kind: incident
date: 2026-07-07
topic: agent-wrapper-monitor-gap
title: >-
  2026-07-07 (chiều) — agent-wrapper-monitor-gap: Agent(isolation:worktree) dùng nhầm làm "background wrapper", Mike mất tín hiệu hoàn tất job — lần 2 lỗi giám sát job nền cùng ngày
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-07 (chiều) — agent-wrapper-monitor-gap: Agent(isolation:worktree) dùng nhầm làm "background wrapper", Mike mất tín hiệu hoàn tất job — lần 2 lỗi giám sát job nền cùng ngày

**What happened:** Mike dispatch Taylor `--bg` (job `Taylor_20260707_132048`, paper-trading
reorg) rồi bọc theo dõi bằng `Agent(isolation: "worktree")` với ý định "chạy nền, chờ job
xong rồi báo lại" theo MIKE.md §8. Wrapper trả lời sớm kiểu "đã bắt đầu theo dõi, sẽ báo lại"
rồi thoát. Job thật xong sạch ~13:32 (status:done, exit_code:0, bus finding đã post) nhưng
Mike không bao giờ nhận được tín hiệu — user phải tự hỏi "Taylor job die rồi hay bạn không
bao giờ biết" Mike mới kiểm tra tay. Lần THỨ HAI lỗi giám sát job nền trong ngày (lần 1 sáng:
LOG_AGE nhìn như treo trong khi Winston job sống → sinh cột HB_AGE trong jobs.sh).

**Root cause (2 tầng, chẩn đoán Wags job `Wags_20260707_142752`):**
1. *Trực tiếp:* `isolation: "worktree"` KHÔNG phải background — chỉ tạo git worktree cách ly;
   agent vẫn chạy ĐỒNG BỘ và tin nhắn cuối là kênh trả kết quả duy nhất. Một wrapper hứa "sẽ
   báo lại" là bất khả thi cơ học: sau khi nó trả lời, không còn gì đang chờ → không bao giờ
   có task-notification.
2. *Gốc:* schema drift sau nâng cấp harness. MIKE.md §8 + snippet in sẵn của `dispatch.sh`
   (dòng "⚠️ BẮT BUỘC...") đều chỉ định `Agent(run_in_background: true)` — nhưng harness
   Fable-5 (Mike restart 2026-07-06) đã BỎ tham số này khỏi Agent tool (schema hiện tại chỉ
   còn `description/prompt/subagent_type/model/isolation` — xác nhận trực tiếp từ tool schema
   phiên Wags 2026-07-07). Template chuẩn không làm theo được nguyên văn → Mike improvise và
   chọn nhầm tham số nghe-giống-background. Lớp fallback ScheduleWakeup poll ngắn (§8 đã có
   từ 2026-07-06) không được đặt — nếu có, Mike đã biết job xong trong ≤270s.

**Fix (Wags, cùng ngày):**
- `dispatch.sh`: viết lại snippet in sẵn sau "Theo dõi:" — (1) cơ chế CHÍNH = ScheduleWakeup
  poll ngắn 240-270s check `jobs.sh status`; (2) wrapper Agent nền CHỈ khi schema phiên hiện
  tại thật sự có tham số nền, cấm dùng isolation:worktree thay thế; (3) self-check bắt buộc:
  mọi phát ngôn về trạng thái job nền phải kèm 1 lần `jobs.sh status` trong cùng turn.
- `MIKE.md` §8: thêm khối SỬA 2026-07-07 cùng nội dung (poll ngắn thăng cấp từ fallback thành
  chính), đánh dấu đoạn "giới hạn chưa xác minh run_in_background" là MOOT.

**Lesson:** Khi 1 quy trình phụ thuộc tham số tool của harness, mỗi lần harness đổi
(restart/model swap) template có thể chết âm thầm — cơ chế chính phải là thứ KHÔNG phụ thuộc
schema (poll bằng script bền vững), cơ chế phụ thuộc schema chỉ là tăng tốc tùy chọn sau khi
kiểm tra schema thật. Và: không bao giờ khẳng định trạng thái job nền mà không có bằng chứng
`jobs.sh status` tươi trong cùng turn — cả 2 sự cố trong ngày đều quy về vi phạm này.
