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
