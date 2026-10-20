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
- [2026-10-20T03:16:05Z] 20/10 10:2x: user báo bq_admin vụ DMX (BQ vẫn 0 dòng DMX). Duyệt vòng sửa Taylor job Taylor_20261020_031558 (G9/G10 ack, chặn trộn mức giữ giá, test) → sau đó quant-skeptic xác nhận lại. Việc 3: ĐÃ áp proposed_fix vào ZaloPay weekly 12-16/10 chỉ trong file, KHÔNG gửi lại (bak: .bak_pre_proposedfix_20261020).
- [2026-10-20T03:17:53Z] 20/10 10:2x: job Taylor_20261020_031558 (vòng sửa C) TRÙNG với Taylor_20261020_031436 đã chạy sẵn — 031558 tự dừng, không sửa gì. Chờ 031436 xong → quant-skeptic vòng 2.
- [2026-10-20T03:19:28Z] 20/10 10:25 ICT: EOD 16/10 ĐÃ gửi lại COMPLETE cả 2 account (backup /tmp/eod1016/*_orig.md). Winston DMX xong (đã claim-reply): hệ thống — 12 mã niêm yết mới từ 05/2026 (AAN,LPS,DMX HOSE + 9 UPCOM) 0 dòng tav2_bq.ticker; ETL upstream ngoài repo, cần user/bq_admin hỏi owner thêm mã+backfill; đề xuất check cron NLIS-có-mà-ticker-0. Chờ Taylor_20261020_031433 (A) + _031436 (C); xong thì arch-review A, quant-skeptic vòng 2 C, đóng 2 câu bus retro (decided_by user).
- [2026-10-20T03:21:58Z] 20/10 10:2x: user chọn 8L-lag 1+3 → Taylor dispatch (opus, --bg, out agents/Taylor/research/rating_8l_lag_20261020/). Xong thì dispatch PHẦN 2 (trễ tín hiệu: rating đổi hạng chậm hơn giá bao nhiêu phiên, N sự kiện độc lập, quant-skeptic) — user đã duyệt làm sau 1+3.
- [2026-10-20T03:24:00Z] 20/10 10:35 ICT: C Taylor xong c42350f1a (nhánh research/vnindex-tr-carry-forward-20261019), quant-skeptic vòng 2 đang chạy nền (logs/verify_20261020_032149_*.log). A (Taylor_20261020_031433) vẫn running. Câu hỏi user chờ: dùng ack DMX hay chờ bq_admin; đính chính báo cáo đã gửi (ZaloPay since-inception dòng 90+93).
- [2026-10-20T03:39:47Z] 20/10 10:50 ICT: 2 câu bus retro ĐÃ ĐÓNG (decided_by user, A+C). A: arch-review NEEDS_CHANGES 4 BLOCKING -> vòng 2 Taylor_20261020_033928 (nhánh feat/gate-block-owned-recovery-20261020, gồm cron sweep+ROOT_TIER; KHÔNG cài cron/merge trước user duyệt) -> sau đó arch-review vòng 2 (Opus medium, toàn nhánh). C: quant-skeptic CONFIRMED medium @c42350f1a; killer: DMX cổ tức ~0,06pp gấp ~20 lần phần sửa carry -> KHÔNG gửi đính chính -6,86 đơn lẻ; chờ giá DMX từ bq_admin (user đã báo). Khuyến nghị thêm G11 vào production v1.
- [2026-10-20T03:45:55Z] 20/10 10:5x: 8L-lag P1+P3 XONG (claim-reply xong, artifact verify khớp: 7 ca peek chắc, stdout khớp). Đã dispatch PHẦN 2 Taylor_20261020_034545 (opus, out agents/Taylor/research/rating_8l_lag_p2_20261020/, timeout 90'). Xong → quant-skeptic verify rồi báo user. Việc user chờ quyết từ P3: đề xuất eff=time khi RD<=RD quý trước/RD<cuối quý (cần quant-skeptic + re-pin 1 trục), hỏi bq_admin nguồn Release_Date + cột first_ingested_at, thêm stock_news vào data_registry (Mike duyệt).
- [2026-10-20T03:58:31Z] 20/10 11:0x: P2 Taylor_20261020_034545 XONG + claim-reply xong; số G1 B3 [2,20] +1,105% q=0,004 khớp CSV. quant-skeptic đang chạy job quant-skeptic_20261020_035622 (topic rating-8l-lag-p2). Chờ verdict → báo user. Kết luận P2: giá đi trước ~59% (G1), còn drift +1,1..1,6% tới +20..40 phiên (nhiều khả năng PEAD), G2 không tín hiệu, ngân hàng không đủ N.
