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
- [2026-08-23T06:26:38Z] 2026-08-23 13:35 ICT: user đồng ý hướng report-only cho code-quality review; đã viết plan kb/projects/code-quality-review-plan-20260823.md (3 tầng: ruff ratchet pre-commit → LLM weekly CN 10:00 read-only → ledger tốt nghiệp ra gate; sunset sau 6-8 tuần theo metric). CHỜ user duyệt plan; nếu duyệt → bước 1 dispatch Wags làm Tầng 1 (ruff + baseline + gate + selfcheck).
- [2026-08-23T07:13:02Z] 2026-08-23 14:12 ICT: user Go — dispatch Wags_20260823_071251 (--bg, timeout 2400s) triển khai Tầng 1 code-quality plan (ruff + baseline + pre-commit gate ratchet + selfcheck). Chờ ScheduleWakeup poll. Khi xong: kiểm artifact thật (selfcheck output, test commit đã revert) rồi mới báo user, sau đó cần arch-reviewer audit trước khi coi Tầng 1 CONFIRMED (rủi ro trung bình - pre-commit gate mới).
- [2026-08-23T07:58:18Z] 2026-08-23 15:05 ICT: user mandate mới — margin thành cơ chế hợp lý, trigger theo spread định giá (EY/DY vs deposit). Dispatch Taylor_20260823_075808 Phase 0 (bằng chứng + plan pre-registered, KHÔNG backtest). Khi xong: đọc finding topic margin-valuation-spread-phase0, trình plan cho user duyệt trước Phase 1. Đã nói rõ với user: margin cost ~10-12.5% ≠ deposit 6%, spread đúng là EY vs margin rate. Commit 322c7f4e: duyệt plan = tự duyệt margin.
