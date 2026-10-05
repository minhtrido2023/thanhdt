# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-05 08:55 ICT)
- Broker corp-action PRIMARY: branch feat/broker-primary-20261003 HEAD 9e4d24c9, CHƯA merge, shadow trên master không đổi. Chờ log shadow T2 05/10 19:25 ICT + T3 06/10, rồi user quyết r5 hay merge có điều kiện.
- Feed vendor corp_action_daily: DEAD (asof 02/10). Chưa xác minh 03/10–04/10.

## Đã xong 05/10 (user duyệt)
- TPB: 877c79d0 + record cash_leg=500 ĐÃ trên master từ 10-02; --verify nay tính chân tiền (MATCH 1,1914≈BQ 1,1911). Hết việc.
- Trứng vàng = tương đương TIỀN (user 05/10), KHÔNG phải sleeve ⇒ KHÔNG áp trần legal-vn "sleeve ≤10% NAV". Rủi ro TCPH/DNSE vẫn nên hỏi DNSE bằng văn bản (2 câu chưa trả lời) nhưng không có cơ chế "vượt trần".
- Bus: đóng selfcheck-baseline (A), classifier-block (C, runbook), 2×coord-2026-10-01. Guard custom30 publish (outer main), ops_health autofix DRY-RUN sớm, baseline manual_only.

## Đang chờ user
- retro-pattern-recurring-polish-chain-review-rounds-cost (chọn: cap vào dispatch.sh code / đo trong retro / gộp arch-review cuối chuỗi).
- code-reviewer cq-2026-10-04-hard-boundary: 3 finding low ở bot_execute.py:69,209 + capit_episode.py:372 (file tiền thật — cần duyệt).
- Winston deposit-12m (6,8 online vs 5,9 quầy) + deposit-cctg (VCB 7,5; BIDV/CTG 7,2; Agri 6,6) — cần xác nhận tay; CCTG sát ngưỡng kill-switch A 7,5%.
- Cron 21:05 auto_confirm lượt 2: KHÔNG cài tới khi broker-primary merge.

## Mốc
- 05/10 19:25 ICT: shadow broker lần đầu (kiểm log, data/corp_action_broker_ledger, bus corp-action-broker-shadow-*). 20:50 plan_position_drift_check lần đầu; 21:00 báo cáo plan khối vị thế.
- Invariant: data/corp_actions.json md5 e7ace20b.
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

## Backlog
- ~14 topic Wags/selfcheck-red; production_manifest ROOT_TIER thiếu 3 cron; context_pack/current_ops phình (trim); paper_report_render E5/E5b rc=1.

