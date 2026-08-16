# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-15T17:38Z (daily retro 08-15 xong, mạch bq_admin+TV1+VIB đóng)

## Việc mở duy nhất — GDKHQ D1-D3
CONFIRMED (high), chờ user chọn: (a) duyệt dùng thật ngay, (b) dry-run trace 08-17
(BID/MBS/SSI/VIX) trước. Đã hỏi nhiều lần, không nhắc thêm — chờ tự nhiên.

## Escalation vừa mở hôm nay — wakeup-miss pattern (chờ user quyết)
Bus question `wakeup-miss-pattern-escalate-2026-08-15`: ScheduleWakeup sau dispatch --bg bị bỏ
sót tăng dần 2 retro liên tiếp (08-14: 5,9%, 08-15: 10,0%). Hỏi user: giữ kỷ luật prose hay
thêm cơ chế nhắc/lint tự động. Chưa có trả lời — theo dõi.

## Sự cố hôm nay 08-15 — đã đóng, đã ghi kb/incidents/retro/retro-2026-08-15.md
1. TV1 Rule A UPCOM anchor bug: flip live 02:24Z→bug phát hiện 03:43Z→revert→fix→relit 05:03Z.
   Đã CONFIRMED, đã fix, verify Wags xong.
2. VIB cost-basis sai trong báo cáo tuần (netting CostBook âm, bán không có lịch sử mua) — fix
   commit c74b3a69, correction đã gửi, PASS gate. Còn hở: chưa có guard chung mọi ticker.
3. `for_each_live_account.sh` fail-open + `discover_sessions.py` ENAMETOOLONG — cả 2 đã vá,
   verify chạy thật OK (Winston, weekly_ops_audit).

## Việc còn hở từ trước (chưa xử lý, không khẩn)
1. ops_health_check.sh::_rollup_resolved() substring-match — NEEDS_CHANGES 08-14, CHƯA vá.
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
4. MIKE.md 44,2KB vượt 40KB — cần tách OKF.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.
6. Cân nhắc file `kb/incidents/` tổng hợp "cost-basis sai báo cáo" nếu có ca thứ 3 (sau 07-03, 08-15).

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- CASH_VENDOR gate: giữ ĐÓNG (user duyệt 08-15), mở lại chỉ khi >=1 sự kiện ISS/hỗn hợp VÀ qua
  2026-09-13. commit dce25180.

- [2026-08-16T11:40:26Z] 2026-08-16 ~11:40Z: cron_health_check false-alarm root-cause XONG (3 commit: f3863f54/a6516c7e + coding_guidelines §29) — verified ERRORS_FOUND 6→0. Cụm bus-backlog (coord-2026-08-16, 5 round Wags) cũng XONG: 6 câu hỏi treo 2-4 ngày đã ĐÓNG THẬT bằng close_bus_question.py + bằng chứng commit, 2 vòng arch-review độc lập của tôi verify. 1 bug mới (rollup_of agent-ownership, _same_ref dùng agent đăng tổng thay vì chủ sở hữu con) tách finding riêng 'rollup-of-agent-ownership-bug-20260816' — KHÔNG khẩn (rollup_of chưa dùng production), đang chờ user quyết fix ngay hay defer.
- [2026-08-16T11:41:27Z] 2026-08-16: chuỗi cron_health_check false-positive + wags-autofix backlog ĐÃ ĐÓNG. cron_health_check.py: bidirectional-date fix + ack mechanism (state/cron_health_ack.json), fleet_housekeeping rotate threshold 10M->300K (commit f3863f54/a6516c7e). Bus backlog 10->2 pending qua 4 vòng arch-review (d65167a9/0f7ac327/c528aa7e/8e9affc3/522e29d2/517261ac) + 1 job cron tự động đóng 7 câu hỏi thật (Wags_20260816_111706). Bài học: chuỗi arch-review lặp 4 vòng, mỗi vòng tự tìm ra bug DO VÒNG TRƯỚC gây ra — dừng đúng lúc reviewer nói không phải blocker thay vì review vô hạn.
