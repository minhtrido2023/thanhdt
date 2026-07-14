# Plan-approval gate (second-chance cron + code-gate)
> Dự án đã đóng — tách khỏi context_pack 2026-07-13. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. XONG — second-chance re-send 23:00 + code-gate bot_execute.py, hiệu lực 09:05 07-14 (commits 4216295/27e1282/54d488c).

## Second-chance re-send cron ĐÃ CÀI + code-gate approval đang thiết kế (2026-07-13)
User duyệt cron backup (`0 16 * * 1-5 ... send_plan_report.sh --second-chance`, 23:00 ICT) —
đã cài + verify (crontab -l xác nhận, dry-run thật trên production path OK). quant-skeptic
CONFIRMED (high) commit `4216295` trước khi cài.

User đồng thời duyệt luôn root-cause 2 (code-gate cứng trong `bot_execute.py`, vùng cấm executor,
cần sign-off riêng — đã có). Dispatch Taylor (fable) job `Taylor_20260713_021202`: BẮT BUỘC điều
tra hành vi thực tế requires_user_approval/approved_by trên plan 2 tuần gần đây của cả SpaceX lẫn
ZaloPay TRƯỚC khi viết code — rủi ro lớn nhất là nếu TOÀN BỘ plan hàng ngày đều đặt
requires_user_approval=true theo triết lý canonical.md nhưng chưa ai set approved_by (vì trước
giờ không gate nên không ai cần) → bật gate sẽ chặn oan giao dịch thường lệ SpaceX sáng mai. Đã
dặn Taylor DỪNG báo cáo lại nếu phát hiện rủi ro này, không tự quyết cách xử lý.

## Code-gate approval trong bot_execute.py XONG (commit 27e1282) — quant-skeptic CONFIRMED, 1 hardening nhỏ đang vá (2026-07-13)
Taylor điều tra kỹ trước khi code (yêu cầu quan trọng nhất): 24 plan thật 06-30→07-13 xác nhận
SpaceX thường lệ dùng `requires_user_approval=false/approved_by="auto"` — gate KHÔNG chặn giao
dịch thường lệ. Paper `main` thiếu field hoàn toàn → backward-compat default=False (an toàn, không
chặn 3 paper trial đang chạy). Bonus: phát hiện `load_plan()` từng ÂM THẦM LỌC MẤT field approval
khỏi dataclass — gate không thể hoạt động nếu không fix cả chỗ này. Gate wire trước lock/broker
connect, fail-safe exit 2 + alert Discord/Telegram/bus khi chặn, HOLD (0 lệnh) không bao giờ bị
chặn. Selfcheck mới 16/16 PASS + regression 6/6 PASS + E2E 2 chiều PASS + audit 20 plan thật (chỉ
đúng 1 plan lịch sử từng là lỗ hổng thật bị chặn, 0 false-block).

**quant-skeptic CONFIRMED (high)** — tự tái lập toàn bộ selfcheck + audit. Tìm 1 lỗ hổng residual
thật: `approved_by` không chuẩn hoá string như `requires_user_approval` — plan ghi `"approved_by":
"None"` (chuỗi literal) sẽ KHÔNG bị chặn (false-negative). Chưa xảy ra trong luồng hiện tại nhưng
là lỗ hổng thật trong lớp an toàn. Dispatch Taylor vá ngay (job `Taylor_20260713_023002`): normalize
approved_by giống requires_user_approval, thêm 2 selfcheck case, verify lại.

**Gate có hiệu lực từ cron 09:05 sáng 07-14** — từ nay plan `req=true` phải có `approved_by` thật
trước giờ chạy, không thì bot tự chối + alert (đúng ý user yêu cầu, khớp cron second-chance 23:00).

## Hardening approval gate: normalize approved_by string 'None'/'null'/'nil'/'nan' = chưa duyệt XONG (commit 54d488c, 2026-07-13)
Vá lỗ hổng residual quant-skeptic tìm thấy — `approval_block_reason()` giờ coi các chuỗi
lowercase `{none,null,nil,nan}` là approved_by trống → BLOCK. Selfcheck 19/19 PASS (file gốc 17
check chứ không phải 16 như dự kiến, đính chính) + regression 6/6 PASS. quant-skeptic CONFIRMED
(high) — tự tái lập false-negative pre-fix, xác nhận không false-block approver thật.

**Chuỗi việc hôm nay đã khép kín hoàn toàn (đều quant-skeptic CONFIRMED):**
1. Plan ZaloPay 07-13 duyệt + thực thi đúng giờ.
2. Cron `send_plan_report.sh --second-chance` 23:00 ICT — đã cài, chống tái diễn "plan sửa sau
   21:00 không được gửi lại duyệt" (commit `4216295`).
3. Code-gate approval cứng trong `bot_execute.py` (commit `27e1282`) + hardening residual
   (commit `54d488c`) — có hiệu lực từ cron 09:05 sáng mai 07-14.
