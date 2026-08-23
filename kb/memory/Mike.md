# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-23 12:10 ICT)

### Go-live V2.4 lever — LIVE từ 08-24 (đã set xong 08-22)
- fill_timing → FALSE, extreme_regime_enabled → TRUE, capit_margin_lever.enabled → TRUE (SpaceX + ZaloPay)
- Mỗi ngày có CAPIT margin: `approve_margin_day.py --account <acct> --date <date> --approved-by "John"` trước bot

### Signal holds — KHÔNG tự đổi
- VPI/BAL: HOLD đến 2026-09-16
- SpaceX + ZaloPay: HOLD_ALL (theo VPI hold)

### Đang chờ kết quả
- Taylor_20260823_051738: điều tra expvol_pacing 1/25 order-day (dispatch 12:10 ICT, timeout 600s)
  → ScheduleWakeup ~180s để poll

### Đã đóng HÔM NAY (08-23)
- Q1 weekly-report-correction-08-17-08-21: user quyết NO_CORRECTION
- Q2 DollarBill/cap-margin-test-mechanism-needed: CANCELLED (option C)
- wags-autofix-review-needed: coord-2026-08-21: CLOSED (đã xong từ commit 13f7bd59 08-22)
- postshock-base-formation: REFUTE, đóng sổ
- native agent name: fix, smoke-test PASS
- wake_debounce_selfcheck.sh: fix isolated temp log (commit 436cc2c6)
- notify_thread.sh UTC timestamp bug: fix TZ=ICT (commit 44fa7fe1)

### Vẫn còn hở nhỏ
- order_book_execution_shadow: 0/40 outcome coverage (low priority)
- probe_linger_live_gate: vẫn True (paper-only)
- expvol_pacing: đang điều tra

### Signal holds
- VPI/BAL: HOLD đến review 2026-09-16
- capit_lever selfcheck đỏ: WARN-ONLY, đã triage

### KHÔNG tự nêu lại các vấn đề đã đóng ở trên trong lần kiểm tra tiếp theo

