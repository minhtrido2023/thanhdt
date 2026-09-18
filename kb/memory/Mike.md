# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal_hold ĐÃ GỠ 2026-09-16 — logic bình thường, không còn escalate riêng.

## Việc đang mở / cần theo dõi
1. **`coord-2026-09-17` (Wags wags-fix-not-confirmed round 2, mở 09-17 05:48:17Z) CÒN HỞ ~19h,
   chưa có answer.** required_changes round 2 chưa xác nhận đã làm: urgency câu hỏi
   `zalopay-active-nav-excluded-ticker-dividend-receivable-option-c` (normal→cần nâng),
   suppress_days=8 (cần rút ngắn), 2 câu hỏi tồn đọng coord-2026-09-14. Rủi ro thật: mọi plan
   ZaloPay 18-25/09 có lệnh mua có thể vẫn bị phồng size ~15% nếu option-c chưa xử lý.
2. **Pattern "arch-review NEEDS_CHANGES vòng 2 ⇒ auto-escalate" (đề xuất từ retro-09-14) vẫn CHƯA
   wire thành code** — tái diễn y hệt ở coord-2026-09-17. Cần Mike/user quyết có build gate thật
   trong `wags_autofix.sh` không (retro-2026-09-17.md có đề xuất cụ thể).
3. **FiinPro/OShares harvest**: dừng 09-15 ở 4/59 lô oshares, 0/15 fx — 2 bug vá (tool_use_id
   filter, cooldown hourly/daily) CHƯA có selfcheck/commit xác nhận, chỉ sống trong logic phiên
   headless cũ — cần port thành code thật hoặc coi là mất.
4. Treasury buyback/corp_action mở rộng (dispatch Taylor_20260917_150848, job đã xong 2 nhánh):
   ĐANG CHỜ USER QUYẾT 5 việc — (1) bảng riêng hay trộn corp_action; (2) one-time hay recurring;
   (3) sự kiện thiếu size giữ+cờ hay trả rỗng; (4) xoá hay giữ 2 dòng MANUAL_FILL VRE/SRF; (5) mở
   sprint cổ tức mô tả không. Quyết định KHÔNG WIRE 09-08 (relative-delta absorption) vẫn đứng —
   design mới của Taylor (persistent quarterly-snapshot adjust, bảng riêng) khác hẳn đề xuất ban
   đầu của Mike (đã bị bác vì sai bản chất treasury buyback).
5. Code-quality Tầng 3 auto-dispatch ĐÃ WIRE vào `code_quality_weekly.sh` bước 7 hôm nay
   (arch-reviewer CONFIRMED sau 5 vòng) — chạy lần đầu tự động Chủ Nhật 2026-09-20 03:00 UTC.
   Backlog quan sát (manifest T0 107 file) — CHƯA quyết có cần thu hẹp gate.

## Retro 09-17 đã đóng (`6fcb489d`) — 2 sự cố, Wags CONFIRMED
- Funding-gate double-count biến thể 4 (HOÀN CHỈNH, d6568e13). Wags NEEDS_CHANGES round 2 CÒN HỞ
  (mục 1 ở trên). Tin tốt: TV1 (retro-09-16) đã đóng đúng <15h — prevention hoạt động.
- Đã đóng bù `Winston/ops-autofix-unresolved: run-bot-fail-ZaloPay-2026-09-17` (root cause đã fix,
  chỉ sót không đóng theo).

## Còn mở không khẩn
- `job_cancel_guard` nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- `append_event.sh` JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

- [2026-09-18T04:18:27Z] 09-18 11:2x: Treasury-buyback compliance-window monitor LANDED — merge master (commit chứa a8301c27 lineage), cron 07:10 T2 hang tuan cai xong (crontab xac nhan), CLOSE_WINDOW_DAYS giu 45 (user chot: WARN phai toi khi con hanh dong duoc). Registry + data_registry doc da cap nhat DA CAI. Worktree/branch da don. Con 4 quyet dinh cu (bang rieng/one-time/UNSIZED/MANUAL_FILL VRE-SRF) van CHUA hoi lai user vi da tach thanh viec rieng (window-monitor) - neu can quay lai bang overlay day du thi phai hoi tiep.
- [2026-09-18T04:52:03Z] 09-18 11:5x: Thu hẹp gate code-quality autodispatch theo yêu cầu user 'tăng tỉ lệ tự sửa' — 2 vòng arch-review, cả 2 lần đều tìm killer thật (lần 1: lọc tier_root là hiện vật thứ tự crontab, bỏ sót 20 file ghi lệnh; lần 2: thiếu bot_heartbeat.sh + send_plan_report.sh). Đã vá cả 2, đo cuối 72 file qua manifest + 10 EXACT tay (từ 107 gốc, quá rộng). Commit chuỗi: 90f93d5b (thu hẹp lần 1) → db0c46ea (vá vòng 1) → 6fd028a0 (vá vòng 2). Backlog KHÔNG chặn cần trình user: append_event.sh trong SAFE_TOOLING_ALLOWLIST hơi rộng so với yêu cầu gốc; dispatch.sh tới lượt HOT_CORE ~2026-10-11 sẽ tự sửa bởi agent do nó dispatch; manifest không có cron tái sinh. Đã báo tóm tắt cho user.
- [2026-09-18T12:28:18Z] 09-18 19:2x: User chot huong tieu thu treasury_share_events - hieu chinh theo BCTC MOI NHAT (khong cong don lich su) la MAC DINH cua toan he thong, khong rieng treasury. UNSIZED (413/577) GIU trong bang lam bang chung giai thich, khong phai input tinh toan, trang thai terminal (khong treo). Con lai: 4 file kb/data_registry/price-volume/*.proposed cho session Taylor treasury_table_20260918 (branch feat/treasury-share-events-table, commit 4e7f51d4, qua 2 vong arch-review) CHUA duoc Mike/user duyet chinh thuc; bang BQ that CHUA tao (cho thiet ke consumer/oshares_live hook truoc, theo khuyen nghi arch-reviewer).
