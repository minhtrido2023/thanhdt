# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE (SpaceX+ZaloPay). Mỗi ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — SpaceX+ZaloPay HOLD_ALL theo VPI, không tự đổi.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Đang chờ
- Taylor job Taylor_20260825_105028: crisis_margin_framework_adaptive — forensic (tại sao 11/2022 không fire) + coverage map 5 episode × trigger + adaptive decision framework Loại-2. Dispatch 17:50 ICT 25/08. ~60-90 phút.

## Mandate mới từ anh John (25/08/2026) — ghi vào KB sau khi Taylor xong
- VNVN market: 90% nhà đầu tư cá nhân → overreaction là đặc trưng CẤU TRÚC, không phải noise
- Framework phải ADAPTIVE, không phải rigid policy chỉ đúng cho thị trường đã trưởng thành
- Statistical significance wrong tool cho N=3-5 crisis — dùng causal framework + human judgment
- Deliverable: observable indicators + escalation process, không phải auto-trade rule

## KHẨN — security leak CHƯA đóng
- Số tài khoản DNSE THẬT lộ public GitHub minhtrido2023/thanhdt. 2 commit fix local chưa push.
- CẦN user tự git push origin main ở /home/trido/thanhdt.

## Còn hở nhỏ (low priority)
- order_book_execution_shadow: 0/40 outcome coverage.

- [2026-08-25T11:39:07Z] Taylor job Taylor_20260825_113846 đang chạy: margin cap sizing Loại-2 + early-recovery forensic. Dispatch 18:38 ICT 25/08. Timeout 90 phút.
- [2026-08-25T11:48:08Z] Taylor job Taylor_20260825_113846 DONE: margin_cap_recovery_forensic_20260825.md. Kết quả: trần ≤5% NAV equity sleeve giữ nguyên nhưng cơ sở đổi (lỗ tối đa trước de-lever = 1% NAV/lần escalate); trần exposure làm rõ thành ≤6,5% NAV (≠≤5%). Recovery-entry NO-GO. Cần user/risk-auditor xác nhận trần mới chính thức.
- [2026-08-25T13:18:56Z] Taylor_20260825_125936 DONE: early_recovery_margin_lever_20260825.md. VERDICT NO-GO. 3 lý do: N=2 (LOO 77-94% từ COVID), 0 IS session, chân vô điều kiện thắng cửa sổ. 2 đính chính: V2.4 chưa bao giờ vay thật (gross 0.60), hệ không có 130% EX-BULL (SB_GATE code). Quant-skeptic đang verify (bg). Câu hỏi mở thật: vì sao BULL/EX-BULL gross 0.60-0.62 thấp hơn NEUTRAL 0.72 — signal scarcity.
