# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Mỗi ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chạy
- Taylor_20260825_151108 (DC sleeve phase 2, ~90-120 phút): A=backtest 3-book thật, B=factor-neutral check, C1=state-conditional LAG→DC trong BULL, C2=replace LAG hoàn toàn, C3=creative architecture alternatives, C4=capacity. Output: agents/Taylor/research/dc_3book_architecture_20260825/ (thư mục con, 5 file).

## Đã đóng hôm nay (25/08)
- Early-recovery margin lever: NO-GO CONFIRMED. Quant-skeptic CONFIRMED high.
- BULL/EX-BULL gross scarcity: LAG thủ phạm (PEAD signal khan). Feature, không phải bug.
- LAG cash routing BULL: Hướng A LOẠI, Hướng B NO-GO (tăng DD -2-3pp không tương xứng).
- DC sleeve Q1-Q4 research (phase 1): GO có điều kiện — DC outperform BULL rõ OOS (Calmar 0.53→0.80), cơ chế THAY THẾ không thêm beta. Chuyển sang phase 2.
- Mandate Loại-2 adaptive committed (975e37bd).

## KHẨN — security leak CHƯA đóng
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. 2 commit fix local chưa push.
- CẦN user tự git push origin main ở /home/trido/thanhdt.

