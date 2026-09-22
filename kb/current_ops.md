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

## Signal holds
- **VPI/BAL**: signal_hold 08-19→09-16 ĐÃ GỠ 2026-09-16. Review dựa trên `amh-adaptivity-review-20260910.md` (Taylor job A/B/C + quant-skeptic): lý do gốc của HOLD (edge-health dashboard báo mom_200 FLIPPED) đã bị bác — kênh đó REFUTED cho quyết định BAL; mom_200 IC hồi phục dương Q2/2026. User duyệt RESUME 2026-09-16 23:19 ICT: "tuân theo chiến lược production đã duyệt, không cần điều chỉnh gì" (`decided_by: user`, bus `answer/bal-vpi-checkpoint-resume-decision`). VPI/BAL trở lại logic bình thường từ plan kế tiếp — không còn escalate riêng.

## CAPIT — vị thế THẬT đang giữ (`capit_fired` ≠ "đang giữ")
⚠️ `capit_fired` tính lại mỗi phiên, KHÔNG phải cờ vị thế. Đọc `data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`). **PNJ EXCLUDED** (due-diligence gate, 07-20, TTL ~08-23). Chi tiết: `kb/current_ops_ext.md § CAPIT`.

## Domain-constraint layer
- **P1 LIVE**: `filter_lag_rating_orders()` — gate 8L rating≤3 tầng ORDER. 14/14+22/22 selfcheck.
- **P0 ACTIVE (HARD BLOCK)**: `check_plan_funding()` trong `bot_execute.py:536` từ 08-04. Chi tiết 2 bug đã vá (08-07): `kb/current_ops_ext.md § Domain-constraint`.

## Features đang LIVE — đọc đầu phiên, không để mất dấu
> Cập nhật mỗi khi có feature mới go-live. Source of truth: `kb/projects/paper_programs_registry.json`.

- **EXTREME-regime gate** (`extreme_regime_enabled=True`) — LIVE SpaceX+ZaloPay từ **2026-08-22** (account overrides `secrets/trading_bot_accounts.json`). Default config=False, override=True. Alert pipeline: `bin/extreme_regime_dd_alert.sh` hook trong `run_bot.sh`. Commit `07726527`.
- **Vol-scale buy chase-cap** (`chase_cap_vol_scale_enabled=True`) — LIVE toàn bộ từ **2026-08-04** (`config.py:190`). k=2.0, ceil=4%, clamp static→ceil theo 20d rvol.
- **fill_timing HYBRID** (`fill_timing_live_gate=False`, `fill_timing_hybrid_live_gate=False`) — LIVE từ **2026-08-26** (user duyệt option A). BUY blocks: 11:00/11:15/13:00/13:15/13:30. SELL blocks: 09:15/09:30/09:45/10:00. Monitoring: fill-vs-open mỗi ~10 phiên, rollback nếu mean >+22bps. Commit `9be375a4`.
- **CAPIT margin lever** (`capit_margin_lever.enabled=True`) — LIVE từ **2026-08-24**. Ngày có CAPIT margin phải chạy `approve_margin_day.py` TRƯỚC bot.
- **Domain-constraint P1** (`filter_lag_rating_orders()`, 8L rating≤3 gate) — LIVE. 14/14+22/22 selfcheck.
- **NAV corp-action L1 — cảnh báo TRƯỚC ex-date** (`bin/nav_exdate_forecast.py`) — LIVE từ **2026-09-22**, commit `2a7dd54e`. Wire `[pipeline-0]` trong `bq_freshness_check.sh` (TRƯỚC `exit 1` đầu tiên) ⇒ chuỗi 19:00 in cảnh báo corp-action của mã ĐANG GIỮ vào plan report + Discord. Selfcheck 58/58.
- **NAV corp-action gate v2 (L2-L4)** (`classify_qty_residual` + `_mult_explains` trong `daily_nav_snapshot.py`) — LIVE từ **2026-09-22**, commit `4dcc3643`, **5 vòng arch-review**. Thay tripwire so giá MÙ bằng PHÂN LOẠI:
  · cổ tức TIỀN có bằng chứng ⇒ mark giá **CUM**, trừ khoản phải thu khỏi tiền (không đếm 2 lần)
  · sự kiện CỔ PHIẾU ⇒ chặn **rc=5** theo bằng chứng KL credit sớm THẬT (phần dư sau khi trừ FILL trong ngày khớp tỉ lệ sự kiện) — KHÔNG chặn theo lịch, KHÔNG phụ thuộc ngưỡng giá 5% ⇒ đóng lỗ hổng sự kiện tỉ lệ nhỏ
  · `--from-raw` + corp-action ĐÃ CONFIRMED + multiplier TÁI TẠO được KL trước sự kiện ⇒ quy ngược KL (giữ đường phục hồi cũ)
  · không giải thích được ⇒ nói THẲNG "chưa giải thích được", không đoán (§29)
  Selfcheck 38/0 + 64/0 + 8/0 qua 3 TZ. rc=5 là mã MỚI: `eod_trading_report.sh` không ghi marker, `nav_sync_retry.sh` không retry 2h, `nav_snapshot_daily.sh` escalate ngay. Runbook rc=5 ở `kb/ops_runbook.md.proposed` — **CHỜ MIKE DUYỆT ĐỂ ĐƯA LIVE (§13)**.

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

## Macro watch — rủi ro cấu trúc BĐS VN (mở 2026-08-26)
Bobby classify STRUCTURAL_ACCUMULATION/AMBIGUOUS. Thesis + lead indicators + playbook đã chốt:
`kb/projects/vn-realestate-structural-risk-20260826.md`. KHÔNG đổi V2.4/DT5G/margin theo thesis này.
**Review quý — next ~2026-11-26: dispatch Bobby refresh bảng lead indicators + quét
`kb/structural_break_watch.json`** (6 sự kiện cấu trúc: nâng hạng, KRX, T+, luật margin, room
ngoại, sản phẩm mới). Protocol: `kb/projects/amh-structural-break-protocol-20260910.md` —
sự kiện kích hoạt ⇒ BẮT BUỘC re-validate đúng tầng, mặc định vẫn là KHÔNG đổi tham số.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate 2026-07-07)
Ranh giới cứng (KHÔNG tự sửa): trade plan, trading_rules.json, logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Chi tiết: `kb/ops_runbook.md`.

## Workflow ngày trading — Discord topic routing
- **Trading Daily (1521470705563340910)** — preflight, run_bot, heartbeat, ops_health_check.sh
- **DollarBill plan (1521183164364754974)** — lập kế hoạch. **Mirror duyệt plan vào đây dù đang ở topic khác.**
- **Trading report (1522576692638388364)** — báo cáo tổng hợp ngày/tuần/tháng (KHÔNG phải alert)
- Dispatch Taylor → ghi `discord_thread_id` vào job record ngay lúc dispatch, đọc lại qua `_job_thread_id`.
- Plan T+1 không sẵn sàng → ESCALATE (Telegram + Discord + bus question `plan-t1-not-ready`), KHÔNG retry tự động.
