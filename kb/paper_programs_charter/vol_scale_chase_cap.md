# Charter — Vol-scale buy chase-cap (patch#3) (`vol_scale_chase_cap`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Nới trần đuổi mua theo realised vol 20d (clamp(k·rvol, static, ceil), k=2.0/ceil=0.04, monotone-safe, fail-safe về static) có wiring đúng trên quote thật không? (executor-path stress đã PASS 15/15)

## 📅 Nghiệm thu / mốc kết thúc

10 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-07-20. Mốc cũ 2026-07-14 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm.

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) Executor-path stress 15/15 PASS (wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · NEG-control) — stress_vol_scale_chase_cap.py
- ⏳ (pending) Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache
- ⏳ (pending) Không can thiệp NORMAL-path ngày non-gap
- ⏳ (pending) Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target
- ⏳ (pending) User sign-off trước khi bật live

## ℹ️ Ghi chú vận hành

Cap-widen KHÔNG có marker riêng trong journal (áp silent trong _buy_chase_pct) — đo qua stress script + so limit price ngày gap-up; cần phiên executor paper + ngày gap mới có evidence tự động. Từ 2026-07-07: probe harness chạy paper main mỗi ngày (6 BUY/phiên trên quote thật — xem entry extreme_regime cho cron).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)`
- `stress_vol_scale_chase_cap.py`
