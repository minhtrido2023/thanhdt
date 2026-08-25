# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## DC state-adaptive — CHỐT 26/08 (không còn job chạy)
- Tầng 1 XONG: dc_book_waterfall_paper.py v2.1 (DHG/MSH excluded, per-name caps 10 mã) + c1_shadow_paper.py (cron 00:20 ICT T3-T7 ĐÃ CÀI, commit 82548b82).
- C1 live-25% REFUTED bởi quant-skeptic (high) — BLOCKED. Mở lại chỉ khi: rolling 3-4 IS/OOS windows + shadow đủ dài (mục tiêu ≥60 phiên BULL forward) + caps cưỡng chế trong allocator + skeptic pass MỚI. Checkpoint 2027-03-31.
- CRISIS: DC universe (hygiened) = candidate basket cho crisis sleeve Loại-2 (escalation-based).
- Bobby macro re-read 2017-2020: accommodative low-rate + bank listing wave — nhưng edge DC 2020+ cũng có thể one-time (skeptic point, cắt 2 chiều).

## KHẨN — security leak CHƯA đóng
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. 2 commit fix local chưa push.
- CẦN user tự git push origin main ở /home/trido/thanhdt.

