# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Mỗi ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chạy
- Taylor_20260825_153800 (DC phase 3, timeout 2h): Phần 1=C1 backtest thật (state-conditional BULL swap + turnover cost + walk-forward), Phần 2=validate ma trận C3 (bootstrap CI + OOS stability 3 giai đoạn), Phần 3=capacity sizing 16 mã DC universe (đặc biệt DHG/MSH). Output: agents/Taylor/research/dc_3book_architecture_20260825/.

## Đã đóng hôm nay (25/08)
- Early-recovery margin lever: NO-GO. Quant-skeptic CONFIRMED high.
- BULL/EX-BULL gross scarcity: LAG thủ phạm (PEAD signal khan). Feature.
- LAG cash routing BULL: Hướng A LOẠI, Hướng B NO-GO.
- DC sleeve phase 1: GO có điều kiện.
- DC sleeve phase 2: 3-book tĩnh NO-GO. C1 +4.19pp BULL. C3 ma trận factor×regime. C2 BÁC BỎ.
- Mandate Loại-2 adaptive committed (975e37bd).

## KHẨN — security leak CHƯA đóng
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. 2 commit fix local chưa push.
- CẦN user tự git push origin main ở /home/trido/thanhdt.

