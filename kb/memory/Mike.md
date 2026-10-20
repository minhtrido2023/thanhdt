# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 19/10 (dọn 00:35 ICT 20/10)
## Chờ USER
- Retro-pattern fail-closed gate (2 câu bus trùng chủ đề: `...-owned-recovery-path` 18/10 + `...-recovery-path-recurring` 19/10; trả lời xong đóng CẢ HAI). Đề xuất: cron 08:30 T2-T6 nhắc duyệt plan trước 09:05.
- Lãi CCTG A/B (nguồn báo mâu thuẫn 6,8% vs 5,9%; mặc định giữ 6,80/7,40).
- Áp `reports/ZaloPay_weekly_..._.md.proposed_fix` + gửi lại; EOD 16/10 thiếu khối giao dịch.
- Taylor carry-forward v2 (branch research/vnindex-tr-carry-forward-20261019 @37aa83657, quant-skeptic CONFIRMED medium, CHƯA wire): DMX thiếu dòng BQ → giao Winston/bq_admin; vòng sửa a-e.
## Việc dở (Mike/Wags)
- Dọn 10 câu `plan-t1-not-ready-*` hết hiệu lực; giao chủ trần giá injector (không neo biên độ ngày); xử arch-review NEEDS_CHANGES wags-fix coord-2026-10-19 (2 question bus còn treo, chưa có quyết định user).
- Điều tra cảnh báo watchdog "no enabled mike@ units found" lặp mỗi 10' (retro 19/10 bổ sung) — nhiễu hay cần bỏ check.
## Đã chốt 19/10
- Plan 20/10 cả 2 account = HOLD ALL 0 lệnh. DT gate: user chọn A (giữ luật đếm; CRISIS commit sớm nhất ~11/11).
- Vòng plan CN: merged + ĐÃ cài 4 cron; chạy thật đầu CN 25/10 19:00 ICT (xem logs/sunday_plan_round.log).
- AIS chain-order PARKED (kb/projects/ais-lockup-stale-base-parked-20261019.md). treasury_buyback + corp_action_feed_canary merged 602d56c33; monitor kỳ đầu 26/10.
- Retro 19/10 logged (Wags GAPS FOUND đã sửa).
## Mốc
- nav-loss-brake 11-09; review BĐS 11-26; measurement audit ~12-27; LAG checkpoint 12-15.
- TODO nhỏ: data_registry corporate_action_bq.md qua .proposed; ZaloPay DNSE 401 chưa giao Winston; worktree wt-Taylor_20261018_173105, wt-1521183164364754974, wt-Taylor_20261019_052148 dọn sau.

- [2026-10-20T03:14:53Z] 20/10 10:15 ICT: user bảo 'làm EOD + escalation'. EOD 16/10: nguyên nhân = ATC price=None crash (vá 87441a7bc); đang dựng lại báo cáo (staging /tmp/eod1016, SpaceX_new.md xong, ZaloPay chờ block.py) rồi ghi đè reports/*_daily_report_2026-10-16.md + report_delivery_gate (gửi lại). Escalation: chọn A+C — dispatch Taylor_20261020_031433 (A, nhánh feat/gate-block-owned-recovery-20261020, opus), Taylor_20261020_031436 (C vòng sửa a-e), Winston_20261020_031438 (DMX). Sau đó: arch-review A, quant-skeptic vòng 2 C, đóng 2 câu bus (decided_by user).
