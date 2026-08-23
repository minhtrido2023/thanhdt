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
- [2026-08-23T08:13:14Z] 2026-08-23 15:13 ICT: Tầng 1 code-quality gate XONG + verify độc lập PASS (commits da401a71..d1098640 tồn tại thật, selfcheck 9/9 PASS chạy lại, hook đăng ký đúng .pre-commit-config.yaml, baseline 143 files/37 lỗi F841+F401 chủ yếu). arch-review 3 vòng nội bộ CONFIRMED. Tầng 1 ĐÓNG. Bước tiếp theo (Tầng 2, khi user muốn): viết ~/.claude/agents/code-reviewer.md + bin/code_quality_weekly.sh, chạy tay 1 lần trước khi bật cron CN 10:00.
- [2026-08-23T08:18:22Z] 2026-08-23 15:20 ICT: Taylor Phase 0 margin (job Taylor_20260823_075808) XONG — verdict GO_PHASE_1_NARROW. Plan agents/Taylor/plan_margin_valuation_spread_20260823.md (N_trials=7 V1-V7 + control V0=dd52, gate 6 điều kiện, CAPIT-only). Đã trình user, CHỜ user duyệt Phase 1. Nếu duyệt: bước 0 = dispatch Mafee lấy tỷ lệ ký quỹ duy trì gói 1840 + Winston phân biệt cổ tức tiền/cổ phiếu, rồi dispatch Taylor Phase 1 (--timeout ≥4h).
- [2026-08-23T08:23:41Z] 2026-08-23 15:24 ICT: user duyệt Tầng 2. Đã viết ~/.claude/agents/code-reviewer.md + bin/code_quality_weekly.sh (worktree wt-1540947310874198108, chưa merge). Fix 1 bug thật khi test: git log trong WorkingClaude/ (thư mục con của toplevel /home/trido/thanhdt) trả path relative TOPLEVEL không phải  -> path bị nối đôi; fix bằng git rev-parse --show-toplevel + pathspec '-- .'. Dry-run OK (25 file scoped, 113 dropped logged). Đang chạy REAL test (PID 2831963, log /tmp/code_quality_weekly_realrun.log, chạy từ worktree nên ghi vào bus/report/state CÔ LẬP, không đụng production) để verify trước khi merge + đăng ký cron CN 10:00. Chưa merge, chưa bật cron.
