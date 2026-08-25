# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Mỗi ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chờ
- Taylor_20260825_142021: Hướng B backtest (PARK_STATES_DICT {4:X}) + 3-book design (LAG+BAL+DC 1/3 each). Dispatch 21:20 ICT 25/08. Timeout 90 phút. Job phức tạp, poll 5-10 phút/lần.

## Đã đóng hôm nay (25/08)
- Early-recovery margin lever: NO-GO CONFIRMED. Quant-skeptic CONFIRMED high.
- BULL/EX-BULL gross scarcity: LAG thủ phạm (PEAD signal khan trong BULL). EX-BULL out of scope.
- LAG cash routing BULL: Hướng A LOẠI (BAL full), Hướng B promising (parking), 3-book (DC) mở.
- Mandate Loại-2 adaptive committed (975e37bd).

## KHẨN — security leak CHƯA đóng
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. 2 commit fix local chưa push.
- CẦN user tự git push origin main ở /home/trido/thanhdt.

