# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI. Plan T+1 2026-09-14 đã HOLD_ALL đúng.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 SẼ chặn theo kỳ vọng
  (46.750−8.000=38.750 khớp broker) — quy tắc mới đã ghi kb/current_ops.md/MIKE.md (2026-09-12,
  commit e5d860d9). Xử TAY theo kb/ops_runbook.md § PRICE_XCHECK, KHÔNG hỏi lại user, KHÔNG escalate.
  Phân biệt: cổ tức TIỀN (DGC) = cho qua tự động theo quy tắc; cổ tức CỔ PHIẾU/thưởng/tách
  (đổi cả giá lẫn khối lượng) = VẪN CHẶN, cần người xử lý, không có ngoại lệ.

## 09-12 — retro đã đóng (commit 50f7cb2a), toàn bộ việc user chốt 12:18+14:22 đã XONG
Chi tiết: kb/incidents/retro/retro-2026-09-12.md + kb/incidents/2026-09/2026-09-12-report-return-gate-worktree-root.md.
- Pattern 1 (worktree/bản sao lệch cây canonical) TÁI DIỄN LẦN 3, đề xuất checker chung (git log -1
  vs canonical cho MỌI cây bản sao) — CHƯA làm, chưa tới ngưỡng escalate tự động (retro-09-11 chưa
  nêu pattern này). Nếu retro-09-13 gặp lại cùng hình dạng → escalate.
- Còn mở có chủ đích (không khẩn): ~28 file bin/*.py cùng lớp dirname-x3 ngoài đường báo cáo;
  job_cancel_guard_selfcheck.py nhánh systemd-run luôn đỏ dưới cron (cần Wags quyết định); 4
  worktree đang dùng chưa rebase (WARN-ONLY); dọn state/*.bak-*.
- NAV exdate tự động hoá: user chốt GIỮ TAY (không làm vòng 3), bản vá cất ở
  agents/Wags/research/nav_exdate_xcheck_wip_20260912.patch.

## R&D đã ĐÓNG HẲN tuần 09-05→09-11: AMH · CCS Phase 0-2 · BAL 5 vòng · custom30V 5 vòng · CCS/8L accruals.
## append_event.sh JSON isolation — pattern đã biết, không escalate (18+ lần, 0 mất dữ liệu).
## Sát ngưỡng OKF: kb/coding_guidelines.md 39,5KB/40KB — §-mới PHẢI tách _ext.md.

