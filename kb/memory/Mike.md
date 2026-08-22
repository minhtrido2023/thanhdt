# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-22)

### Go-live HOÀN TẤT
- fill_timing (cả fill_timing_live_gate + hybrid_live_gate) → FALSE cho SpaceX + ZaloPay
- extreme_regime_enabled → TRUE cho SpaceX + ZaloPay
- Commit mike: 08af2637 (stress test 40/40) + 2357e231 (tracker)
- secrets/trading_bot_accounts.json: gitignored, đã cập nhật trên đĩa
- Hiệu lực T2 24/08 khi run_bot.sh chạy

### Việc còn hở (từ retro 08-21 + session này)
- Wags/wags-fix-not-confirmed: coord-2026-08-21 CHƯA ĐÓNG (wake_debounce_selfcheck.sh ghi fixture vào log production)
- Weekly report 08-17→08-21 quá hạn (bus question Mike/report-cadence-overdue-weekly_2026-08-17_2026-08-21 open)
- expvol_pacing: 1/25 order-day (cần Taylor điều tra)
- order_book_execution_shadow: 0/40 outcome coverage (adverse-selection gate không đo được)
- Cycle fear backtest: NO-GO, chờ quant-skeptic verify

### Signal holds
- VPI/BAL: HOLD đến 2026-09-16
- SpaceX + ZaloPay: HOLD_ALL

### probe_linger_live_gate: vẫn True (paper-only)

