# Charter — EXTREME-regime gate (`extreme_regime`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Gate phòng thủ intraday (arm 2-poll, sell-to-floor, buy-pause, cadence ×0.25) có ZERO false-trigger trong thị trường benign không? (stress-injection đã PASS 24/24)

## 📅 Nghiệm thu / mốc kết thúc

20 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-08-03. Mốc cũ 2026-07-28 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm.

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) Stress-injection 24/24 PASS (arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls) — stress_extreme_regime.py, week-1
- ⏳ (pending) ZERO false-trigger qua ~4 tuần benign trên account paper main
- ⏳ (pending) Không can thiệp NORMAL-path
- ⏳ (pending) User sign-off trước khi bật live

## ℹ️ Ghi chú vận hành

Evidence tích lũy CHỈ khi executor chạy phiên trên account main — 0 phiên = 0 evidence, không tính là PASS. Từ 2026-07-07: probe harness chạy paper main mỗi ngày T2-T6 (cron 08:52 sinh plan mike/bin/paper_main_probe_plan.py, executor 09:10 + 13:05, log mike/logs/run_bot_main_*.log).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)`
- `stress_extreme_regime.py`
