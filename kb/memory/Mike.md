# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-05 00:35 ICT)
- Broker corp-action PRIMARY: branch feat/broker-primary-20261003 HEAD 9e4d24c9, CHƯA merge, shadow trên master không đổi. Chờ log shadow T2 05/10 19:25 ICT + T3 06/10, rồi user quyết r5 hay merge có điều kiện.
- Feed vendor corp_action_daily: DEAD (asof 02/10). Chưa xác minh 03/10–04/10.
- Retro 10-04 đã ghi (kb/incidents/retro/retro-2026-10-04.md, commit a27d744d).

## Đang chờ
- user: quyết broker-primary r4→r5 hoặc merge có điều kiện (sau shadow 05/10 + 06/10).
- code-reviewer `cq-2026-10-04-hard-boundary`: chưa answer; finding (b) bot_execute.py:69 thread thứ hai không nhận thông báo cần user duyệt trước khi sửa; finding 3 chưa đọc.
- Pattern A polish-chain đã escalate: `retro-pattern-recurring-polish-chain-review-rounds-cost` (không mở lại).
- Kiểm transcript session 9d9e75de (02:42Z dispatch --bg thiếu ScheduleWakeup).

## Chờ user
- TPB cash_leg_vnd_per_share=500 đã thêm (md5 e7ace20b). Commit 877c79d0 vẫn chưa verify trong production.
- Discretionary DRI/TV1; Trứng vàng vượt trần đề xuất legal-vn (sleeve ≤10% NAV) — chưa chốt.
- Cron 21:05 auto_confirm lượt 2: KHÔNG cài tới khi broker-primary merge.

## Mốc
- 05/10 19:25 ICT: shadow broker lần đầu (kiểm log, data/corp_actions_broker_ledger, bus corp-action-broker-shadow-*).
- 05/10 20:50 ICT: cron plan_position_drift_check lần đầu. 21:00 báo cáo plan có khối vị thế.
- Invariant: data/corp_actions.json md5 e7ace20b.

## Backlog
- 9 topic selfcheck-red; selfcheck-weekly-new-red 05:08 ICT 04/10 chưa xác nhận đóng; VNM exright note cho Winston; production_manifest ROOT_TIER thiếu 3 cron; context_pack/current_ops phình (trim); paper_report_render E5/E5b rc=1 (chưa xác minh).

