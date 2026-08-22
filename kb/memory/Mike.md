# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cuối ngày 2026-08-22)

### Go-live V2.4 lever HOÀN TẤT — hiệu lực T2 24/08
- fill_timing (fill_timing_live_gate + hybrid_live_gate) → FALSE cho SpaceX + ZaloPay
- extreme_regime_enabled → TRUE cho SpaceX + ZaloPay
- capit_margin_lever.enabled → TRUE (user confirmed 08-22)
- CAPIT margin lever: mỗi ngày có leveraged CAPIT orders phải chạy
  `approve_margin_day.py --account <acct> --date <date> --approved-by "John"` trước khi bot chạy —
  lever chỉ fire khi capit_signal_today AND dd52<=-20% AND approval file tồn tại.

### R&D — TẤT CẢ đã đóng, không còn backlog mở từ tuần này
- A1/A2 (rate-regime × parking, forward-horizon matrix): KHÔNG đổi production, radar giữ DISPLAY-ONLY.
- B1 (BAL exit DT candidate), B2 (breadth vs radar), B3 (CAPIT radar-band guard): cả 3 NO-GO/ARCHIVE.
  capit_base() giữ nguyên. Breadth-tercile PIT (không phải radar) là trục 2 mặc định mới (đã ghi
  kb/canonical.md, user duyệt 08-22).
- Taylor_20260822_153901 (B2-ext, alpha vs breadth-tercile) đang chạy lúc cuối ngày — kiểm kết quả
  khi vào phiên tiếp theo (bus finding "b2-alpha-breadth-20260822" — REFUTE, đã có kết quả rồi,
  không cần chờ thêm).

### Retro 2026-08-22 — XONG, đã đóng đúng
- File: kb/incidents/retro/retro-2026-08-22.md. 4 sự cố: #1 weekly report có 2 nội dung lỗi thời
  (CÒN HỞ — cần user quyết có gửi đính chính không), #2 insider_flags cron-env (đã đóng),
  #3 wags-fix-not-confirmed coord-2026-08-21 (đã đóng thật bằng commit 13f7bd591 — draft ban đầu
  từng báo sai "còn hở", Wags GAPS FOUND sửa lại, escalation sai đã đóng bằng answer event),
  #4 ScheduleWakeup MISS 10% (dao động, chưa cần escalate).
- 3 pattern xuyên suốt CHƯA có gate cơ học: (1) report nội dung lỗi thời không tự xoá, (2) cron-env
  câm lặng đường lỗi (lần 3), (3) ScheduleWakeup MISS dao động 8-27% (lần 4). Đề xuất formalize
  Pattern 2 vào coding_guidelines nếu tái diễn lần 4.

### Việc còn hở
- Weekly report 08-17→08-21 đã gửi có 2 nội dung sai (breadth ticker_prune, limitation egg lỗi
  thời) — CHƯA đính chính, chờ user quyết (retro #1).
- expvol_pacing: 1/25 order-day (cần Taylor điều tra — chưa dispatch).
- order_book_execution_shadow: 0/40 outcome coverage.
- wake_debounce_selfcheck.sh vẫn ghi fixture vào logs/wake_thread_errors.log (nợ kỹ thuật nhẹ,
  không còn gây báo động giả vì daily_retro.sh đã ngừng đọc file đó).

### Signal holds — KHÔNG tự đổi
- VPI/BAL: HOLD đến 2026-09-16.
- SpaceX + ZaloPay: HOLD_ALL (theo VPI hold).

### probe_linger_live_gate: vẫn True (paper-only)

