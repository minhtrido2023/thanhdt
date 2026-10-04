# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-04 00:35 ICT)
- Broker corp-action là nguồn CHÍNH (user duyệt 10-03 23:27): `Taylor_20261003_162814` (Opus high, branch feat/broker-primary-20261003) đang chạy attempt 2/2 (max-turns 160). CHƯA merge — chờ log shadow T2 05/10 + T3 06/10 19:25 ICT VÀ user duyệt lại.
- Feed vendor `corp_action_daily` DEAD (asof 10-02, tuổi 6 ngày). Log asof 10-03 CHƯA xác minh.
- Retro 10-03 đã ghi (`kb/incidents/retro/retro-2026-10-03.md`, commit f32ec27f). Wags verify GAPS FOUND → đã sửa.

## Đang chờ
- Taylor_20261003_162814: kết quả broker PRIMARY + 2 mục báo cáo (plan 21:00 đọc broker sau cập nhật chưa; nav_exdate_forecast mất cảnh báo khi vendor chết).
- Cron 19:25 ICT T2 05/10 `corp_action_auto_confirm` chạy nhánh broker SHADOW lần đầu → kiểm log, `data/corp_action_broker_ledger.jsonl`, bus `corp-action-broker-shadow-*`, dnse_raw không phát sinh quote_unmapped.
- Cron 08:00 ICT `daily_decision_topic.py` chạy thật đầu 04/10 → kiểm topic 04.10 có tạo không.

## Chờ user
- Port P1 report-prompt (Wags): duyệt; merge `1b9d4d46`, `1afc0c59` chưa merge. Kiểm 6 file mất sau merge `9311ac03` (daily_nav_snapshot, check_report_cadence, eod_trading_report, send_report_email, render_report_html, paper_programs_daily_report).
- Cổ tức TPB: BQ 531.300đ lệch tiền thật 100.000đ — cần người kiểm nguyên nhân; `cash_leg_vnd_per_share` chưa có trong record ⇒ commit 877c79d0 chưa verify trong production.
- Discretionary DRI/TV1. Trứng vàng vượt trần đề xuất legal-vn (sleeve ≤10% NAV) — chưa chốt.

## Quyết định hôm nay (10-03)
- Broker r4 (8b436975) + r5 (2c2abc63) merged SHADOW; knob lùi `MIKE_CA_BROKER_SOURCE=off`. Chưa bật live, chưa `MIKE_EXDATE_REGISTRY_FALLBACK`, chưa cron 21:00.
- Đính chính TPB (Mike, 10-02): gate hết chặn vì ex-date đã qua, KHÔNG phải nhờ 877c79d0.
- NAV SpaceX 10-01 backfill = estimate.

## Backlog
- 9 topic selfcheck-red; VNM exright note cho Winston; ack SCL bán tay 09-30; production_manifest ROOT_TIER thiếu 3 cron; context_pack/current_ops phình (trim); `paper_report_render` E5/E5b rc=1 (Wags: lỗi có sẵn, chưa xác minh).

- [2026-10-03T17:56:52Z] 10-04 01:00 ĐÍNH CHÍNH working memory: report-prompt port ĐÃ MERGE (db357342 + r2 56c38165) — mục 'Chờ user: Port P1' là LỖI THỜI. Taylor_20261003_162814 broker-primary DONE nhưng STOPPED_NEW_BUG_CLASS (branch feat/broker-primary-20261003, a1e1923e): arch-review NEEDS_CHANGES, 5 required_changes (registry reconciliation mọi provenance, confirm-only dùng held_before, post-ex re-verify, price-only ngân sách thời gian, m1/m3/m4+đột biến sống). KHÔNG merge; shadow trên master không đổi. Q5 plan 21:00: rủi ro exdate_gate fail-OPEN khi vendor chết + không đối chiếu lại sau 20:15 (BID); Q6 nav_exdate_forecast báo all-clear GIẢ khi feed stale (mất cảnh báo TPB 10-01). CHỜ USER: dispatch vòng sửa 5 mục + có làm Q5/Q6 không (Q5 chạm bot_execute ⇒ cần user duyệt riêng).
- [2026-10-04T02:44:19Z] 10-04 09:45 user DUYỆT: giao 3 job — A Taylor_20261004_024239 (vòng sửa 5 mục broker-primary, Opus high, branch feat/broker-primary-20261003, KHÔNG merge tới khi shadow T2 05/10 + T3 06/10 + user duyệt lại); B Wags_20261004_024241 (nav_exdate_forecast feed_status, Sonnet medium, Mike tự kiểm + merge TRƯỚC 19:00 T2 05/10); C Taylor_20261004_024243 (plan_position_drift_check ~20:50 + nhúng send_plan_report, hướng nhẹ, KHÔNG chặn/không đụng bot_execute; cron 20:50 + 21:00 auto_confirm lượt 2 do Mike cài SAU khi merge+tự kiểm + registry). Poll ScheduleWakeup.
- [2026-10-04T02:54:14Z] 10-04 09:58 job B Wags XONG + MERGED master 108069cd (nav_exdate_forecast feed_status; tự kiểm 111/0 + 25/0 x2 interp x3 TZ, real-data: 09-28 & feed khoẻ byte-identical master, 09-30/10-01 STALE cảnh báo, 10-02 FAILED feed_dead). Chỉ 1 vòng arch-review (NEEDS_CHANGES đã sửa, không review lại). Còn chờ A (Taylor_20261004_024239) + C (Taylor_20261004_024243).
- [2026-10-04T03:37:48Z] 10-04 10:50 job C MERGED master 637d3008 (plan_position_drift_check, CHỈ CỜ; tự kiểm selfcheck 98/98 x2 interp x3 TZ, replay BID 08-14/VPB 09-23/TPB 10-01 có cờ, ZaloPay 10-01 không cờ; arch-review 1 vòng, phần sửa chưa review lại). Cron 20:50 + luot 21:05 auto_confirm CHƯA cài — chờ user duyệt crontab (đề xuất: chỉ 20:50, bỏ 21:05 tới khi broker-primary merge). Job A Taylor_20261004_024239 STOPPED_NEW_BUG_CLASS lần 2 (r2 arch-review NEEDS_CHANGES: M1 cash_leg im lặng, M2 LOẠI MỚI UNVERIFIED→record_proposed áp hệ số 2 lần, M3, M4, M5 + 7 minor) — KHÔNG merge, đề xuất tạm dừng polish, đợi log shadow 05/10+06/10. Việc mở: TPB record trong data/corp_actions.json thiếu cash_leg_vnd_per_share (500đ/cp) — cần user duyệt trước khi sửa registry production. dnse_raw_2026-10-04.jsonl dòng 5-8 = 4 bản positions SpaceX thật do đột biến selfcheck của Taylor (10:21-10:28 ICT), giữ nguyên.
- [2026-10-04T10:36:55Z] 10-04 17:45 user DUYỆT: (1) vòng 3 broker-primary → Taylor_20261004_103554 (Opus xhigh, write-scope corp_action_*, arch-review đúng 1 lần cuối, KHÔNG merge); (2) cron 20:50 plan_position_drift_check ĐÃ CÀI (crontab dòng 52, backup state/crontab_backup/crontab.20261004T103610Z.bak, registry+CHANGELOG commit bcec8227), KHÔNG cài lượt 21:05; (3) TPB cash_leg_vnd_per_share=500 vào data/corp_actions.json: user duyệt nhưng HOÃN tới khi job A3 xong vì A3 dry-run đang dùng đúng record thiếu trường làm ca thử + md5 bfd681e5 là invariant của A3; park_holdings bỏ qua record ex_date<=asof nên TPB hiện không ảnh hưởng. Sau A3: thêm trường bằng tmp+os.replace, chạy corp_actions.validate, báo md5 mới.
