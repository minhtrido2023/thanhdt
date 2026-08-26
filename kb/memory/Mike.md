# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Pattern đang escalate — self-report ≠ artifact (3 ngày liên tiếp, 4 hình dạng)
- Topic mở: `retro-pattern-recurring-2days-selfreport-vs-artifact` — chờ user/agent quyết prevention tổng quát (flush stdout trước subprocess con + quy tắc coding_guidelines mới).
- Retro 08-26 mới thêm: `time_claim_audit.py` buffer-race (log cron báo count=0 sai, bus có count=1 thật) — CHƯA SỬA, còn nguyên trong code, sẽ tái diễn mỗi lần có mismatch thật.

## KHẨN — security leak CHƯA đóng hẳn (>1 ngày, tái diễn lần 3 trong retro)
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. Fix code đã push (commit c1303a96, 3d358b14) — nhưng bus question `security-leak-2026-08-24-remaining-repo-visibility-and-sudo` vẫn CHƯA có answer.
- 2 hạng mục cần user quyết: (1) repo private/rewrite-history, (2) thu hồi sudo hainguyen/hungle/namiq.
- Đừng mở question thứ 2 trùng — nhắc lại đúng topic cũ.

## Retro 2026-08-26 — đã đóng, Wags verify CONFIRMED
- kb/incidents/retro/retro-2026-08-26.md: 3 sự cố chính (time_claim_audit buffer-race MỚI+CHƯA SỬA; wakeup MISS N=1 chưa đủ pattern; security-leak treo lần 3) + 2 sự cố phụ tự đóng trong ngày (fill_timing classifier-block đúng thiết kế; oshares EVF 8% fix commit 8ad317b3).

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). kb/projects/vn-realestate-structural-risk-20260826.md. Review quý next ~2026-11-26.

