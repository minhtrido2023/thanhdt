# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T23:35 ICT

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)
- approved_by ghi vào cả 2 file, verify qua production loader: block_reason=None cả 2 account.
  0 lệnh cả 2. TV1 đã đạt target cả 2 account, injector 20:30 ICT không cần chèn gì thêm.

## Đã đóng đêm nay 08-17 (rà lại việc còn hở từ phiên trước)
- Selfcheck-masking E5 capit_lever → XÁC NHẬN đã merge (`d73e673d`).
- EOD daily report chưa gửi email → XÁC NHẬN COMPLETE cả SpaceX/ZaloPay (report_delivery_gate.py).
- Winston_20260817_122149 (VHM 1:1 ops-autofix) — job "orphaned" nhưng việc THẬT đã xong
  (commit ced702ac), record tự reap.
- **verify_account_snapshot.py cost-basis=0 → KHÔNG PHẢI BUG, lỗi gọi lệnh.** Taylor điều tra
  (job Taylor_20260817_162530): script đúng khi loại vị thế không có fill trong cửa sổ --dates;
  lệnh gây ra báo cáo sai là DollarBill gọi --dates=2026-08-17 (1 ngày) thay vì full history.
  Đã tự kiểm tra: **pipeline report SẢN XUẤT (daily_nav_snapshot.py) KHÔNG dính bug này** — nó
  tự glob `exec_<account>_*_journal.csv` đúng qua `trading_dates_with_fills()`, không gọi kiểu
  1-ngày. Bug chỉ ở lệnh ad-hoc DollarBill gọi ngoài luồng report ngày 08-17 (ghi trong
  "plan-2026-08-17-tom-tat-2-account"). **Không ảnh hưởng số liệu report thật đã gửi.**
  Backlog optional (không khẩn, cần sign-off nếu làm): (a) auto-glob dates mặc định trong script,
  (b) hard-fail thay vì soft-warn khi đa số vị thế bị gắn legacy — cân nhắc sau, không chặn gì.

## Việc còn hở (ưu tiên giảm dần)
1. GDKHQ dry-run D1-D3 chưa setup — cần quyết trước VIX 08-20 (còn 3 phiên).
2. book_breakdown_current trong plan_SpaceX_2026-08-17.json ghi nhãn SCL sai (không đổi lệnh).
3. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry mới để verify.
4. Order-book Pha 0 telemetry (commit d6346efd) — chờ phiên có giao dịch thật để kiểm probe.
5. lag_entry_anchor.py:105 — đọc thẳng ticker.Price làm trần (bẫy stale-on-exdate), không khẩn.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill; dispatch job >2 phút BẮT BUỘC --bg.
- TV1 Rule A LIVE từ 08-15, an toàn, đã đạt target.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- Quy trình Discord: báo nhận việc ngay, progress 1-2 phút/lần, ScheduleWakeup khi chưa xong.

