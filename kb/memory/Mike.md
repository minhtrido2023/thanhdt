# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-22)

### Go-live HOÀN TẤT
- fill_timing (cả fill_timing_live_gate + hybrid_live_gate) → FALSE cho SpaceX + ZaloPay
- extreme_regime_enabled → TRUE cho SpaceX + ZaloPay
- **capit_margin_lever.enabled → TRUE** (user confirmed 2026-08-22, bus event ghi)
- Hiệu lực T2 24/08 khi run_bot.sh chạy

### CAPIT margin lever — cổng thứ hai PHẢI chạy khi lever fire
- Mỗi ngày có leveraged CAPIT orders: chạy `approve_margin_day.py --account SpaceX --date YYYY-MM-DD --approved-by "John"`
- Lever chỉ fire khi: capit_signal_today AND dd52<=-20% AND approval file tồn tại

### Việc còn hở
- Wags/wags-fix-not-confirmed: coord-2026-08-21 CHƯA ĐÓNG (wake_debounce_selfcheck.sh ghi fixture vào log production)
- Weekly report 08-17→08-21 quá hạn (bus question open)
- expvol_pacing: 1/25 order-day (cần Taylor điều tra)
- order_book_execution_shadow: 0/40 outcome coverage

### Signal holds
- VPI/BAL: HOLD đến 2026-09-16
- SpaceX + ZaloPay: HOLD_ALL

### probe_linger_live_gate: vẫn True (paper-only)

