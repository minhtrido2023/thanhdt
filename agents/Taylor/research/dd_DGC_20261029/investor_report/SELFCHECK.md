# SELFCHECK — DGC_DD_investor_report_20261029 (job Taylor_20261029_121056, 29/10/2026 ~19:25 ICT)

## 1. Rò rỉ nội bộ — RỖNG (đạt)
Lệnh: `grep -n -i -E "SpaceX|ZaloPay|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|Winston|Mafee|DollarBill|HARD ABANDON|time-stop|\bP1\b|\bT[1-8]\b|giá vốn mua|vị thế|tài khoản|10\.000 ?cp|35,8" <md> <html> figs/*.csv`
- Hit duy nhất: `\bT[1-8]\b` khớp tên THÁNG ("T8", "T9", "T5/2027") trong bảng ngành/rủi ro — không phải trigger nội bộ. Không có tên agent, tài khoản, số lượng vị thế, giá vốn mua, %NAV, quy tắc nội bộ.
- "giá vốn" (7 hit) đều nghĩa COGS.
- Văn bản dùng "nhóm nghiên cứu", "người đọc ngành độc lập", "người phản biện".

## 2. "mua/bán/khuyến nghị" cá nhân hoá — 0 (đạt)
Mọi hit là thuật ngữ kế toán/kinh doanh: "mua ngoài" (quặng), "chi mua sắm TSCĐ", "bên mua" (thanh lý TSCĐ), "chi phí bán hàng", "giá bán", "bán hay xoá sổ" (khoản Đắk Nông), "không phải khuyến nghị cá nhân hoá". Không có câu khuyên giao dịch.

## 3. Số khớp nguồn đã phản biện — 59/59 tìm thấy (đạt)
Script đối chiếu (`/tmp/numchk.txt`): 42 số định giá đều có trong `dgc_valuation_20261029_r10/REPORT.md` hoặc `inputs/ERRATA_r10_skeptic_round4.md`
(A7 32.182, B7 37.060, R1 30.598, R2-ex 36.880, r4-ex 32.399, toàn bộ lưới out_r10_final_grid, 26.117/26.340/26.558, 6.065/7.406/1.796/6.282, 4.878, 1.420, ±2pp 29.345/35.017, T1 vụ án 31.872/31.082/29.766/36.353/35.563/34.247);
17 số BCTC có trong `dgc_valuation_20261027_r6/MIKE_EXTRACT_BCTC_Q3_2026.md`/r7 (9.761,2; 1.391,0; 8.370,2; 22.040; 19.400; 34.425; 2.469,45; 478,16; 1.267,10; 755,6; 4.213,0; 48,23; 63,38; 332,3; 2.085,9; 1.452,8; 13.073,9).
Số tự tính (ghi "ước lượng" trong báo cáo): vốn hoá 12.495; P/E TTM 6,6× (LNST mẹ 4 quý 1.888,8 từ BQ+BCTC); định giá ngược lõi 5.127 tỷ / LNST lõi ≈1.131 / P/E lõi ≈4,5× (từ KQKD 9T Q3 extract); biên 9T 20,7%/33,3%; CP BH+QLDN; 36,5% DT tài chính/LNTT; giá điều chỉnh −56% (price_raw.csv).

## 4. Errata vòng 4 — đã áp
1. Không "nghiêng hữu hạn" như kết luận → "chưa phân định; hai chiều cân nhau" (§7, Investment Summary). Không nối 200 với vụ án như sự thật (note 36).
2. Dải đối xứng 2 nền × N quý, có ô nền biên thấp + lặp vĩnh viễn ≈26,1–26,6k; lặp vĩnh viễn 30.598 đặt dưới nền biên cao; gọi trung lập "tổ hợp thấp nhất/cao nhất".
3. Không có tỷ lệ 23×/5,8× (chỉ nhắc trong Phụ lục E như điều đã bỏ).
4. Câu pháp nhân có cửa sổ nguồn (Pháp luật 15/08; quét 01–29/10; 16/08–30/09 chưa quét); khởi tố GĐ công ty con = cá nhân.
5. Thuế theo errata; lá chắn 20% [giả định], thuế ưu đãi 13%.
6. Không dùng Đ.235 làm trần; không trích ngày gỡ hạn chế HOSE; lý do hạn chế = một nguồn; Đ.221 ghi "chưa đối chiếu nguyên văn".
7. Không dùng điểm mã 315/316; "suy luận loại trừ, chưa xác nhận"; 332,3 "theo bản trích; cần đối chiếu ảnh".

## 5. Giá
DNSE latest_trade đọc 19:12 ICT 29/10: khớp cuối 33.300 (14:45:02); basicPrice 32.900 = đóng cửa 28/10 (neo). Kết luận ghi rõ không đổi ở cả hai mức. Sàn HOSE theo secdef marketId=STO.

## 6. Kiểm mắt PDF
19 trang A4; đã render trang 1, 2, 11, 12 ra PNG và xem: dấu tiếng Việt đủ, bảng không tràn, hero trang 1 đúng luật 10. Mỗi mục lớn (1 hero, 3, 4, 5a–5d, 6, 7, 8, 9) có ≥1 hình; 13 hình, mỗi hình có CSV trong figs/.

## Giới hạn selfcheck
Số BCTC chép tay từ scan (không tự mở lại ảnh mọi trang trong phiên này; đã mở p09–p10 thuyết minh 1). Không gửi email (Mike gửi).
