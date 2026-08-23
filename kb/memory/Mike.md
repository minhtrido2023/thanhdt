# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-23 12:22 ICT)

### Go-live V2.4 lever — LIVE từ 08-24 (đã set xong 08-22)
- fill_timing → FALSE, extreme_regime_enabled → TRUE, capit_margin_lever.enabled → TRUE (SpaceX + ZaloPay)
- Mỗi ngày có CAPIT margin: `approve_margin_day.py --account <acct> --date <date> --approved-by "John"` trước bot

### Signal holds — KHÔNG tự đổi
- VPI/BAL: HOLD đến 2026-09-16
- SpaceX + ZaloPay: HOLD_ALL (theo VPI hold)

### Đã đóng HÔM NAY (08-23) — KHÔNG tự nêu lại
- Q1 weekly-report-correction: NO_CORRECTION
- Q2 DollarBill/cap-margin-test: CANCELLED
- wags-autofix coord-2026-08-21: CLOSED
- postshock-base-formation: REFUTE, đóng sổ
- native agent name: fix PASS
- wake_debounce_selfcheck.sh: isolated temp log (commit 436cc2c6)
- notify_thread.sh UTC bug: fixed TZ=ICT (commit 44fa7fe1)
- expvol_pacing 1/25: KHÔNG phải bug — hết cơ hội sinh lệnh (TV1 hit target, CAPIT không rebalance), chờ tự nhiên hoặc user quyết thêm nguồn lệnh mới

### Còn hở nhỏ
- order_book_execution_shadow: 0/40 outcome coverage (low priority)
- probe_linger_live_gate: vẫn True (paper-only)
- capit_lever selfcheck đỏ: WARN-ONLY, đã triage

- [2026-08-23T05:25:44Z] 2026-08-23 12:25 ICT: user chọn (a) cho expvol_pacing — để tự nhiên gia hạn qua 09-15 nếu N=25 chưa đạt, không tạo thêm nguồn lệnh. Đã ghi bus answer, đóng topic expvol-pacing-investigation. Registry paper_programs_registry.json (id=expvol_pacing) đã có sẵn điều khoản này, không cần sửa.
