# FPT — đánh giá KQKD Q3/9T 2026 so với nhận định 14/10 (job Taylor_20261021_073511, 21/10 ~14:45 ICT)
CHỈ NGHIÊN CỨU, không đặt lệnh. Tiêu chí khai trước: `PREREG.md` (viết trước khi chạy lại). Nhãn [ĐO]/[CHƯA XM]/[KTĐ].

## Kết luận
**Chưa kết luận được phần dòng tiền** (CFO/CFI Q3, DSO): BQ chưa có 2026Q3 [ĐO: ticker_financial FPT mới tới 2026Q2, 28/07], Winston chưa ghi `fpt_q3_verify_20261021.md`, web chưa có 9T. Khuyến nghị: **CHỜ** (không mua, không thăm dò) cho tới khi có CFO Q3 xác minh.

## (a) Chỉ báo 14/10 vs thực tế
| Chỉ báo | Mốc khai 14/10 | Thực tế 9T/Q3 | Trạng thái |
|---|---|---|---|
| CFO core Q3 | ≥~2.600 tỷ = mùa vụ; <1.500 = vốn lưu động phình | KTĐ | **chưa biết** |
| CFO core 9T | H1 −1.146 tỷ | KTĐ | chưa biết |
| DSO core | >90 ngày = xấu (H1 90,8) | KTĐ (BQ hợp nhất Q2 64,8) | chưa biết |
| Ký mới nước ngoài 9T | H1 +32,3% | 36.137 tỷ, +23,1% [CHƯA XM] | **chậm lại** (nếu số đúng) → kích hoạt tiêu chí "chậm lại" |
| LNST mẹ 9T | ngưỡng +12% | 7.778 tỷ, +13,3% [CHƯA XM] | **qua ngưỡng** (H1 là +14,1% → hơi chậm) |
| LNTT 9T | kế hoạch 2026 +15% | 8.770, +17% [CHƯA XM] | trên kế hoạch |
| Doanh thu Q3 | – | 40.023 − 26.269 (H1) = 13.754 tỷ [suy], ≈ Q2 13.789 | đi ngang q/q |
| Biên | – | LNST mẹ/DT 9T 19,4% [suy] vs H1 19,2% | ổn định |

⚠ **Số báo chí tự mâu thuẫn**: LNST mẹ 9T 7.778 − 6T 5.055 = 2.723, nhưng báo ghi Q3 2.273 (5.055+2.273 = 7.328). Hoán vị chữ số khả dĩ; chưa biết con nào đúng. Q3 = 2.723 ⇒ +6% q/q (Q2 2.568); Q3 = 2.273 ⇒ −11% q/q. Chờ Winston/BCTC gốc. Tăng trưởng 9T +13,3% ngụ ý 9T/2025 ≈ 6.865 tỷ; không đối chiếu được.

## (b) DCF giữ nguyên giả định PREREG 14/10, chỉ đổi giá live (FPT 57.500, FOX 56.900 — DNSE 21/10 14:29/14:35)
| Tổ hợp | FV 14/10 | FV 21/10 | MOS vs 57.500 |
|---|---|---|---|
| Thận trọng | 33.900 | **34.100** | −68% |
| Cơ sở | 49.600 | **49.800** | −15% |
| Lạc quan | 65.100 | **65.400** | +12% |
Biến thể "chuẩn hoá": 41.100 / 60.500 / 79.700. Chênh nhỏ chỉ do vốn hoá FOX tăng (55.400→56.900). FCFE core, g_hist, r KHÔNG cập nhật vì thiếu CFO Q3 — đây là FV 14/10 dời giá, **không phải FV có dữ liệu Q3**. Stop 50,5k vẫn cao hơn FV cơ sở.

## (c) Nhận định 14/10: đúng / sai / chưa biết
- ĐÚNG (so với số chưa xác minh): LNST mẹ 9T ≥ +12% → hàng "tụt dưới 12%" không kích hoạt; giá +1,4% (56.700→57.500) không phản ứng lớn.
- Đang lệch chiều bất lợi: ký mới nước ngoài chậm từ +32,3% xuống +23,1% (nếu đúng) — trùng tiêu chí "chậm lại", nhưng bảng 14/10 gom nó với LNST <12% thành hành động "thoát thăm dò"; LNST không vi phạm nên tín hiệu hỗn hợp.
- CHƯA BIẾT: toàn bộ luận điểm dòng tiền (FCF/LNST 0,39, CFO H1 âm) — chính điểm quyết định vênh PE 9,4 vs DCF.

## (d) Khuyến nghị: CHỜ
Điều kiện chuyển sang thăm dò/mua (theo khung 14/10, user duyệt mới thực hiện): CFO core Q3 xác minh ≥~2.600 tỷ và phải thu không tăng ⇒ FV chuẩn hoá cơ sở 60,5k (MOS ~+5%, vẫn mỏng) ⇒ tối đa thăm dò ≤1–1,5% NAV/account, stop đóng cửa <50,5k, time-stop ~15/07/2027. CFO Q3 <1.500 hoặc DSO >90 ⇒ không mua. Việc cần làm kế: chạy lại sau khi Winston có CFO/DSO Q3 từ BCTC (BQ cập nhật ~28/10 dựa lịch năm trước).

Files: PREREG.md, PREREG_1014.md, out.txt, labels_fv.csv, matrix_fv.csv, dnse_live_raw.json, fpt_deconsol_dcf.py (bản copy 14/10, đọc dnse_live_raw.json mới).
