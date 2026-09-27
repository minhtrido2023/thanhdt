# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-09-27 11:45 ICT)
- custom30V fix ĐÃ MERGE main WorkingClaude a808a613 (user sign-off 11:33). R3 28,86%→24,38%.
- User RẤT THẤT VỌNG về quản lý: lỗi cơ bản (Close adj × OShares thay đổi theo quý = đếm 2 lần)
  sống từ 2026-06 tới 09-27. Đã trả lời root-cause + accountability 11:4x. Cam kết: audit toàn diện.
- 3 job Taylor đang chạy (opus, 3h, dispatch 11:35):
  · I  Taylor_20260927_043541 (effort medium): hậu kiểm sau merge — selfcheck main, re-pin R3, bootstrap+DSR/PBO mới, +7,4pp parking đo lại, KB .proposed §13
  · G  Taylor_20260927_043542 (high): TICKET 1 (user duyệt) weight-leg OShares tại ex-date — worktree, KHÔNG merge, cần user sign-off lần 2
  · H  Taylor_20260927_043544 (high): AUDIT đo lường 6 bất biến × mọi chuỗi return/level/weight — read-only, REPORT.md + bus finding 'measurement-integrity-audit-2026-09-27'
  Wakeup: claim-reply từng job trước khi post. Sau H: Mike phải tự đọc REPORT, trả lời user "còn lỗi cơ bản nào".
- TICKET 2 (BQ Close nhảy/đảo 30/01→02/02/2026): data-ops ĐÃ TRẢ LỜI — Close ĐÚNG, Price thô bị chép T-1 toàn universe 3 phiên (2025-02-03 403/403, 2025-03-17 197/410, 2026-01-30 419/419); cache = live ⇒ lỗi ETL nguồn; corp-action loại trừ; KHÔNG ảnh hưởng số đang dùng (trước go-live; rebal custom30V 05/02 không trùng). Nguyên nhân sâu cần log ETL bq_admin. Việc tiếp: thêm check "Price flat ≥50% universe" vào bq_freshness_check.sh + đề nghị bq_admin backfill.
- Sau khi I xong: duyệt KNOWLEDGE.md/canonical.md .proposed (§13), lounge closing note.
- Pre-existing: *_screen.py ascending=False rating picks 25 worst — chưa fix (đưa vào audit H).
- Xoá cron FiinPro harvest + cron_registry sau 28/09.
- Carry-over cũ: retro-pattern-recurring-ack-topic-counter (đã merge 4aeaae82?), fpt-vendor-backfill Layer1 detect-only đang làm.

