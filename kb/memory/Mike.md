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

### R&D đang chạy
- **Taylor_20260822_131318**: A1 (rate-regime×parking bank 74%) + A2 (forward-horizon matrix + parking/CAPIT rows)
  - A1: replay custom30V PIT × 3 rate bucket (LOW<5/MID5-6.5/HIGH>6.5%), sector-cap 40/50%, LOO/năm
  - A2: forward-matrix 60/120/250 phiên cho mỗi ô + thêm hàng parking+CAPIT
  - Bus: finding "parking-rate-bucket-20260822" + "forward-horizon-matrix-20260822" + "a1-a2-combined-20260822"
  - Timeout 7200s, opus/high
  - User chốt hướng 2026-08-22 ~20:08 ICT

### Việc còn hở
- Wags/wags-fix-not-confirmed: coord-2026-08-21 CHƯA ĐÓNG (wake_debounce_selfcheck.sh ghi fixture vào log production)
- Weekly report 08-17→08-21 quá hạn (bus question open)
- expvol_pacing: 1/25 order-day (cần Taylor điều tra)
- order_book_execution_shadow: 0/40 outcome coverage

### Signal holds
- VPI/BAL: HOLD đến 2026-09-16
- SpaceX + ZaloPay: HOLD_ALL

### probe_linger_live_gate: vẫn True (paper-only)

### R&D backlog (user đã review, chưa dispatch)
- B1: BAL exit theo DT candidate streak
- B2: Breadth thay Value Radar làm trục 2 (sửa confound zone≈kỷ nguyên)
- B3: CAPIT × radar band guard (dải 0-20 vs 20-33)
- Tier C: LAG-in-BEAR (đóng), Alpha Lens audit 09-30, CAPIT hold dài hơn

- [2026-08-22T13:50:34Z] A1+A2 xong (Taylor_20260822_131318). Kết luận: KHÔNG thay đổi production. Parking HIGH bucket -0.7% CI[-22,+22] = hòa vốn; edge ở MID/LOW. NON-BANK (không phải ngân hàng) là cái sập trong HIGH. Forward ô NEUTRAL+RE không vượt base rate. V2.4 đã hấp thụ radar → giữ DISPLAY-ONLY. Chờ user chốt B1/B2/B3.
- [2026-08-22T14:12:03Z] Taylor_20260822_141143 đang chạy B1 (BAL exit DT candidate) + B2 (breadth vs radar matrix) + B3 (CAPIT radar-band guard). opus/high, timeout 9000s. Dispatch 2026-08-22 ~21:11 ICT.
