---
kind: group-index
group: trading-bot
title: Trading bot / execution (money-path thật)
---

# Trading bot / execution (money-path thật)

| Nguồn (file) | Status |
|---|---|
| [`dnse_openapi_v2_calling_guideline.md`](dnse_openapi_v2_calling_guideline.md) — cách gọi DNSE OpenAPI v2 (signing/OTP/endpoint/gotcha), cho dashboard quản lý danh mục | CANONICAL |
| [`bot_stop.md`](bot_stop.md) — data/BOT_STOP | CANONICAL |
| [`loss_brake_state.md`](loss_brake_state.md) — data/loss_brake/ (trạng thái monitor phanh lỗ cấp NAV, chỉ cảnh báo) | CANONICAL |
| [`dnse_raw_execution_logs.md`](dnse_raw_execution_logs.md) — data/execution_logs/dnse_raw_<date>.jsonl | CANONICAL |
| [`dnse_khoplenh_broker_email.md`](dnse_khoplenh_broker_email.md) — email DNSE "Báo cáo giao dịch khớp lệnh" + data/execution_logs/dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv — fill THẬT, đối soát độc lập với dnse_raw | CANONICAL |
| [`dcf_lens_history.md`](dcf_lens_history.md) — data/dcf_lens_history.csv (append-only DCF forecast log) | CANONICAL |
| [`gdkhq_rollout_state.md`](gdkhq_rollout_state.md) — data/gdkhq_d1d3_rollout.json + gdkhq_shadow_acceptance.json | CANONICAL (cadence chưa xác nhận) |
| [`executor_state_journal.md`](executor_state_journal.md) — data/execution_logs/exec_<label>_<date>_state.json / _journal.csv | CANONICAL |
| [`nav_history.md`](nav_history.md) — data/execution_logs/nav_history_<account>.csv | CANONICAL |
| [`nav_unit_ledger.md`](nav_unit_ledger.md) — data/execution_logs/nav_unit_ledger_<account>.csv (sổ đơn vị quỹ, chỉ-ghi-thêm; bản đối chứng) | NOT-YET-SEALED (công cụ chốt sổ đã merge 2026-10-14; CHƯA chốt thật — chờ áp đính chính + 1 chu kỳ 19:10) |
| [`account_cash_flows.md`](account_cash_flows.md) — data/account_cash_flows.json (nạp/rút, ghi tay kèm bằng chứng) | CANONICAL |
| [`nav_history_corrections.md`](nav_history_corrections.md) — data/execution_logs/nav_history_corrections.jsonl (nhật ký chỉ-thêm mọi lần SỬA TAY nav_history; công cụ `bin/fund_restatement.py`) | NOT-YET-CREATED (xuất hiện ở lần đính chính đầu tiên) |
| [`cash_identity.md`](cash_identity.md) — `bin/cash_identity.py` (đẳng thức tiền hằng tối: phát hiện nạp/rút CHƯA KHAI; lời xác nhận ở data/cash_identity_acks.json) | CANONICAL cho câu hỏi "có nạp/rút chưa khai không" — có điểm mù, xem mục "Không phủ" |
| [`account_inception.md`](account_inception.md) — data/account_inception.json (mốc + vốn khởi điểm) | CANONICAL |
| [`account_seed_capital.md`](account_seed_capital.md) — data/account_seed_capital.json (vốn đầu kỳ + lô legacy + fill broker dnse_raw thiếu, cho reconcile_equity.py) | CANONICAL |
| [`active_nav_snapshot.md`](active_nav_snapshot.md) — data/execution_logs/active_nav_<label>.json (label = SpaceX \| ZaloPay) | CANONICAL |
| [`trade_plans.md`](trade_plans.md) — data/trade_plans/plan_<account>_<YYYY-MM-DD>.json | CANONICAL |
| [`trading_bot_accounts.md`](trading_bot_accounts.md) — secrets/trading_bot_accounts.json | CANONICAL |
| [`trading_rules.md`](trading_rules.md) — data/trading_rules.json | CANONICAL |
| [`intraday_watch_shadow.md`](intraday_watch_shadow.md) — data/intraday_watch/ (state/shadow/verdicts của `intraday_price_watch.py`, cutloss SHADOW) | SHADOW (chưa có consumer production) |
| [`phs_flashapi_evaluation.md`](phs_flashapi_evaluation.md) — PHS FlashAPI (flashapi.phs.vn) go-live evaluation, khác hẳn PHS FLEX cũ | EVALUATION (chưa wire) |
| [`pnj_q3_review_watch_state.md`](pnj_q3_review_watch_state.md) — state chống-lặp watcher PNJ BCTC Q3 (bắn một lần bus question + Discord) | CANONICAL (state một-lần) |

↩ [Về index tổng](../index.md)
| [`nav_sleeve_history.md`](nav_sleeve_history.md) — data/execution_logs/nav_sleeve_history_<account>.csv (+ data/sleeve_scope.json, data/sleeve_transfers.json) — chuỗi "phần bot quản lý" | CANONICAL |
