---
kind: incident
date: 2026-07-14
topic: zalopay-mat-plan-dispatch-timeout
title: >-
  2026-07-14 — ZaloPay mất plan ngày 07-14: dispatch DollarBill timeout ×2, attempt 2 chỉ được nửa thời gian
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-14 — ZaloPay mất plan ngày 07-14: dispatch DollarBill timeout ×2, attempt 2 chỉ được nửa thời gian

**What happened.** `send_plan_report.sh` 21:00 + second-chance 23:00 (07-13) đều báo
plan ZaloPay T+1 chưa sẵn sàng; `ops_health_check` 08:20 sáng 07-14 flag 2 question
`plan-t1-not-ready-ZaloPay` chưa answer. Truy vết (job `Winston_20260714_012012`): dispatch
`DollarBill_20260713_120124` (lập plan ZaloPay) **timeout cả 2 attempt** (exit 124), trong
khi job SpaceX song song (`DollarBill_20260713_120125`) hoàn thành sau ~12 phút. Hệ quả:
ZaloPay không có plan 07-14 — bot 09:05 tự bỏ qua an toàn (verified `bot_execute.py`:
không có plan → skip, không đặt lệnh), nhưng account mất 1 phiên giao dịch.

**Root cause.** Hai tầng: (1) phiên DollarBill treo từ đầu — log attempt-2 RỖNG 0 dòng,
không output nào; pattern lặp lại từ 07-06 (dispatch ZaloPay từng treo 2 lần y hệt, chưa
từng root-cause được vì log bị đè). (2) `dispatch.sh` dùng **deadline tuyệt đối chung**
cho mọi attempt: job ZaloPay deadline = start + 1200s, attempt 1 ăn ~10 phút → attempt 2
chỉ còn ~10 phút, trong khi job SpaceX cùng loại cần 12 phút — attempt 2 gần như không có
cửa thành công kể cả khi không treo. Logfile dùng chung giữa các attempt nên dấu vết
attempt 1 bị mất.

**Fix.** Escalation chain hoạt động đúng thiết kế (21:00 → 23:00 → 08:20, đúng policy
KHÔNG tự re-dispatch, human-in-the-loop). Winston nhắc user khẩn qua Telegram 08:25 +
Trading Daily, post `answer` đóng 2 question với chẩn đoán + 2 option (re-dispatch hoặc
bỏ qua phiên — transition đã xong 5/5 ngày 07-13 nên plan hôm nay khả năng chỉ HOLD/drift
nhỏ). KHÔNG sửa code trong lượt (dispatch-infra thuộc Wags/Mike).

**Lesson.** (1) Dispatch lập plan cho 2 account nên coi attempt 2 là retry ĐẦY ĐỦ thời
gian, không phải phần thừa của deadline cũ; (2) logfile phải tách theo attempt để còn
root-cause được treo-không-output; (3) DollarBill-ZaloPay treo đã tái diễn ≥2 lần
(07-06, 07-13) — cần Wags điều tra một lần dứt điểm thay vì mỗi lần chỉ ghi nhận.
Trace: bus `Winston_20260714_012012`, job record `DollarBill_20260713_120124.json`.

**Wags follow-up cùng sáng (job `Wags_20260714_012002`, commit `e4a5ea6`) — đính chính
cơ chế + fix dứt điểm.** Hai điểm trong Root cause trên không khớp bằng chứng record:
(1) KHÔNG có "deadline tuyệt đối chung" — `dispatch.sh` cấp mỗi attempt đủ TIMEOUT riêng
(`deadline=$((astart + TIMEOUT))`); record attempt-2 cho thấy deadline = attempt-2-start
+600s. Số 1200s của job SpaceX không phải budget gốc mà là 600s base + 1 lần hb-extension
(`hb_extensions=1` trong record `DollarBill_20260713_120125.json`, xong ở 725s). Hai cách
đọc trùng số ở vụ này chỉ vì attempt 1 ăn trọn đúng 600s. (2) DollarBill KHÔNG treo —
heartbeat bus attempt-2 có nội dung thực chất tới phút cuối (12:14 "đọc execution journal",
12:19 "tính VPB trim + CTG entry plan"); log 0-byte vì `claude -p` chỉ flush output khi
kết thúc, bị kill là mất sạch — log rỗng ≠ treo (đúng bài học LOG_AGE 2026-07-07).
Root cause thật: base 600s quá ngắn cho plan-job 10-20+ phút, và cadence heartbeat thực
chất của DollarBill (~5 phút) luôn > cửa sổ fresh `HB_FRESH_S=120s` tại deadline → không
bao giờ được gia hạn → kill-while-alive (lần #4-5, cùng họ với Winston 900s 07-07 và
Wags 1800s 07-09). Fix (`e4a5ea6`, sandbox test 6/6): per-agent base-timeout default
trong dispatch.sh — DollarBill 1800s khi caller không truyền `--timeout` (mọi call-site
hưởng, gồm cả dispatch ad-hoc từng treo 07-06); `--timeout` tường minh và env
`DISPATCH_TIMEOUT_DOLLARBILL` vẫn thắng. Kèm fix thứ 2 phát hiện trong lúc truy vết:
phrase CLI mới "You've hit your session limit · resets 12:50am" không khớp regex
`_looks_like_usage_limit` → DAILY RETRO 00:30 ICT 07-14 (`Mike_20260713_173001`) thành
`failed` thay vì `usage_limited`+auto-resume (fallback usage_watch pct≥95 cũng không cứu
được — cần xem riêng vì sao, không chặn); đã thêm `session limit` vào regex.
