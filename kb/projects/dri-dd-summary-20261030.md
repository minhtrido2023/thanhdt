# DRI — CTCP Đầu tư Cao su Đắk Lắk (UPCoM): hồ sơ tổng hợp đến 30/10/2026
Điểm vào duy nhất cho DRI. Chi tiết từng chặng nằm ở các file liên kết; file này không thay chúng.

## Trạng thái vị thế (broker DNSE, 30/10 13:00 ICT, giá 14.600)
- SpaceX **1.250 cp**, ZaloPay **650 cp** (sau bán tay 21/10 @15.400: −1.200/−600; rồi giảm 50% chủ động user duyệt 27/10, khớp 28/10 sáng @14.400–14.500 qua plan T+1).
- Vị thế DRI thuộc sleeve discretionary (user quyết từng bước, `decided_by: user`); không có lệnh DRI tự động nào đang chờ.

## Dòng thời gian quyết định
- 21/10: bán tay @15.400 → `dri-manual-sell-20261021.md`; đánh giá GIỮ/BÁN sau số Q3 → `dri-q3-hold-review-20261021.md`.
- 26–27/10: DD Taylor (`agents/Taylor/research/dd_DRI_20261027/REPORT.md`) + Bobby (ngành cao su: đỉnh chu kỳ) → kế hoạch kích hoạt, định giá lại r1–r4, skeptic từng vòng, cổng mua thăm dò ≤13.000 → `dri-triggers-20261027.md` (nhật ký đầy đủ, mới nhất ở cuối file).
- BCTC hợp nhất Q3/2026: LNST mẹ 25,98 tỷ (−33% YoY), 9T 167,75 tỷ (+44%); thành phẩm 64,99 → 138,81 tỷ (giữ hàng chờ bán); CFO 9T/LNST 9T 0,75×. Dự báo của DD (55–65 tỷ) và khoá mù F đều trượt; F không được chấm là mù vì SXKD 9T đăng 20/10 trước giờ khoá → `agents/Taylor/research/dd_DRI_20261027/REPORT_Q3_UPDATE.md`.
- Định giá r4 (skeptic CONFIRMED medium): FV post-hoc đường trung bình 8.058 / 9.078 / 10.097 / 11.116 đ @ giá cao su mid 1,865 / 1,97 / 2,075 / 2,18 $/kg; khoảng tin 8,0–12,5 nghìn. Đuôi trên duy nhất vượt giá: DRI hoãn/cắt tái canh (13.225–15.115).
- 30/10: báo cáo nhà đầu tư **v3 trung dung** gửi email (tiêu đề: lợi nhuận đỉnh chu kỳ, tiền ròng dồi dào; giá 14.700 trên vùng giá trị cơ sở 9,1–11,1 nghìn, ngang kịch bản hoãn tái canh). 3 kịch bản 25/50/25, bình quân theo xác suất chủ quan ~10.500 (−29% so 14.700); khoảng giá 13,2–15,1 / 9,1–11,1 / 6,9–8,1 nghìn → `agents/Taylor/research/dd_DRI_20261027/investor_report_v3/`.

## Hai hồ sơ tách biệt — đừng trộn
- **Báo cáo nhà đầu tư** (v3): khách quan toàn diện, KHÔNG nhãn QUALIFY/NON, KHÔNG nhắc vị thế/tài khoản/cổng mua nội bộ, KHÔNG ngôn ngữ fear-buy (chuẩn skill `dd-investor-report` 30/10).
- **Hồ sơ nội bộ discretionary** (`dri-triggers-20261027.md`, cổng mua ≤13.000, trigger giảm nốt/thoát): chỉ dùng cho quyết định của user; skeptic §2.5 chỉ chạy khi user xét mua.

## Mốc theo dõi đang mở
- **~10/11**: báo cáo SXKD tháng 10 của DRI — tấn bán < 1.000 t HOẶC LNTT luỹ kế 10T thấp hơn 9T (208,21 tỷ) ⇒ trình user GIẢM NỐT (không bot tự bán).
- Quỹ TDND Cao su ĐL: tiền gửi 70 tỷ (mốc 30/09/26) tăng thêm hoặc ngoại trừ kiểm toán ⇒ báo user.
- Dakruco vay thêm/gia hạn/tăng phải thu bên liên quan; sự kiện Lào; Bobby → TROUGH ⇒ trigger thoát (xem bảng trong `dri-triggers-20261027.md`).
- Chuyển sàn UPCoM→HOSE: SXKD 9T nói "phấn đấu hoàn thành trong quý IV/2026" (nguồn mới hơn BCTN 2025); chưa có CBTT chính thức hồ sơ được chấp thuận.
- Cổ tức tiền 2025 1.000 đ/cp chi từ 20/10/2026 (thông báo 94/TB-CT).
- Cổng mua thăm dò ≤13.000 / ≤11.600: chỉ cảnh báo (`bin/dri_buy_gate_watch.py`, cron */5 phiên), mọi tranche cần user duyệt từng lần.
