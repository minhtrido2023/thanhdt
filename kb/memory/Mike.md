# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chờ Taylor — 4 selfcheck-red escalate 2026-08-27
- capit_lever, dc_book_waterfall (stale pin), universe_pit_quality (gap dữ liệu thật, khác dạng), lag_forensic_filter (urgency=HIGH — BAF banned 08-26 nhưng code chưa loại khỏi live selection).
- Pattern mới ghi nhận retro 08-27: thay đổi production config/data/KB đã duyệt ship xong nhưng selfcheck phụ thuộc không cập nhật pin cùng lượt — "lõi ẩn" dạng thứ 3 ngoài §23. Đề xuất (chưa quyết): thêm luật coding_guidelines §9/§23 — ship config/data/KB phải kèm grep tên field/constant qua *_selfcheck.py.

## KHẨN — security leak CHƯA đóng hẳn (>3 ngày, treo)
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. Fix code đã push (commit c1303a96, 3d358b14) — bus question `security-leak-2026-08-24-remaining-repo-visibility-and-sudo` vẫn CHƯA có answer.
- 2 hạng mục cần user quyết: (1) repo private/rewrite-history, (2) thu hồi sudo hainguyen/hungle/namiq.
- Đừng mở question thứ 2 trùng — nhắc lại đúng topic cũ.

## wakeup_audit.py — nghi false-positive (không escalate, chỉ theo dõi)
- 2 ngày liên tiếp (08-26, 08-27) đều 33,3% MISS nhưng điều tra 08-27 cho thấy job đó thuộc dạng "tự báo bus" (không cần ScheduleWakeup theo MIKE.md §8). Đề xuất: audit nên đọc dispatch prompt để loại các job tự báo khỏi bộ đếm MISS.

## time_claim_audit.py buffer-race — CHƯA SỬA
- Ngày 08-26 log cron báo count=0 sai dù bus có 1 mismatch thật. 08-27 log và bus đồng thuận (0 mismatch) nên không tái hiện, nhưng bug gốc vẫn còn nguyên trong code — sẽ tái diễn lần tới có mismatch thật.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). kb/projects/vn-realestate-structural-risk-20260826.md. Review quý next ~2026-11-26.

## Retro 2026-08-27 — đã đóng, Wags verify CONFIRMED
- kb/incidents/retro/retro-2026-08-27.md: 2 sự cố chính (batch selfcheck-red pattern MỚI; wakeup MISS khả năng false-positive) + 3 sự cố phụ tự đóng trong ngày.

