# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-08-21 (token-cost trim #4 — warm sections → `kb/current_ops_ext.md`;
> giữ lại hot path: kill-switch, trading status, signal holds, routing rules).
> Chi tiết CAPIT/domain-constraint/due-diligence/cron/daemon: `cat kb/current_ops_ext.md`

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking **80%** idle cash (config F1, đổi từ 70% ngày 2026-08-04, `trading_rules.json` `neutral_parking.default_park_of_idle_pct`). run_bot.sh 09:05 ICT T2-T6. NAV: `nav_history_SpaceX.csv` hoặc EOD report.
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, CASH-ONLY. **DGC EXCLUDED** (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026). Sizing dùng `active_nav`. Cùng target parking 80% (không có override riêng).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking đến 2026-09-30. DollarBill phụ trách.
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,2tr / ZaloPay ~38,8tr (đo 08-19), đã cộng NAV tự động — KHÔNG phải `availableCash`, cần rút T+1. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.

## Signal holds — KHÔNG tự thay đổi trước checkpoint
- **VPI/BAL**: HOLD đến review **2026-09-16**. Lý do: hiệu suất BAL gần đây chưa tốt, chưa phải thiếu tiền. Quyết định user 08-19 (`decided_by: user`). Tín hiệu BAL mới → escalate hỏi, không tự mua hay tự hold theo logic cũ.
- **SpaceX plan 2026-08-21**: HOLD_ALL (VPI signal_hold đến 09-16).
- **ZaloPay plan 2026-08-21**: HOLD_ALL (VPI signal_hold đến 09-16).

## CAPIT — vị thế THẬT đang giữ (`capit_fired` ≠ "đang giữ")
⚠️ `capit_fired` tính lại mỗi phiên, KHÔNG phải cờ vị thế. Đọc `data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`). **PNJ EXCLUDED** (due-diligence gate, 07-20, TTL ~08-23). Chi tiết: `kb/current_ops_ext.md § CAPIT`.

## Domain-constraint layer
- **P1 LIVE**: `filter_lag_rating_orders()` — gate 8L rating≤3 tầng ORDER. 14/14+22/22 selfcheck.
- **P0 ACTIVE (HARD BLOCK)**: `check_plan_funding()` trong `bot_execute.py:536` từ 08-04. Chi tiết 2 bug đã vá (08-07): `kb/current_ops_ext.md § Domain-constraint`.

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

## Macro watch — rủi ro cấu trúc BĐS VN (mở 2026-08-26)
Bobby classify STRUCTURAL_ACCUMULATION/AMBIGUOUS. Thesis + lead indicators + playbook đã chốt:
`kb/projects/vn-realestate-structural-risk-20260826.md`. KHÔNG đổi V2.4/DT5G/margin theo thesis này.
**Review quý — next ~2026-11-26: dispatch Bobby refresh bảng lead indicators.**

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate 2026-07-07)
Ranh giới cứng (KHÔNG tự sửa): trade plan, trading_rules.json, logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Chi tiết: `kb/ops_runbook.md`.

## Workflow ngày trading — Discord topic routing
- **Trading Daily (1521470705563340910)** — preflight, run_bot, heartbeat, ops_health_check.sh
- **DollarBill plan (1521183164364754974)** — lập kế hoạch. **Mirror duyệt plan vào đây dù đang ở topic khác.**
- **Trading report (1522576692638388364)** — báo cáo tổng hợp ngày/tuần/tháng (KHÔNG phải alert)
- Dispatch Taylor → ghi `discord_thread_id` vào job record ngay lúc dispatch, đọc lại qua `_job_thread_id`.
- Plan T+1 không sẵn sàng → ESCALATE (Telegram + Discord + bus question `plan-t1-not-ready`), KHÔNG retry tự động.
