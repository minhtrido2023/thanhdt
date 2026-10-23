# AVC (A Vương) làm chỉ báo thủy văn sớm cho TV1 (Sông Bung 5)? — job Taylor_20261023_080330
CHỈ ĐỌC. Không đổi production/config/plan, không ghi pin. Dữ liệu: `avc_tv1_ticker_financial.csv` (BQ `tav2_bq.ticker_financial`, truy vấn 23/10/2026).

## KẾT LUẬN: **CHƯA ĐỦ DỮ LIỆU — nghiêng KHÔNG** (xem §4)

## 1. Địa lý (tiền đề của câu hỏi) — CHƯA XÁC MINH, có dấu hiệu lệch
| Ý | Nhãn | Nguồn |
|---|---|---|
| Sông Bung là phụ lưu Vu Gia, đổ vào Vu Gia ở xã Đại Sơn, Đại Lộc | fact (qua tóm tắt tìm kiếm của Wikipedia "Sông Bung") | vi.wikipedia.org/wiki/Sông_Bung |
| TĐ A Vương nằm trên nhánh **sông A Vương**, xã Dang (Tây Giang) + Mà Cooih (Đông Giang) | fact (Seho; Wikipedia Sông Bung liệt kê là TĐ trên sông A Vương) | seho.vn/tintuc/en/thuy-dien-tinh-quang-nam/ |
| Hầm dẫn A Vương dài 5,3 km "xả ra dòng sông Bung" | fact thứ cấp, **chưa tự đọc trang gốc** | Seho (qua tóm tắt) |
| SB5 đặt tại xã Mà Cooih (Đông Giang) + TT Thạnh Mỹ (Nam Giang) | fact | baodauthau.vn (đấu giá SB5), PECC1 |
| Vị trí hợp lưu A Vương/Bung so với SB5 | **KHÔNG BIẾT** — không nguồn nào tôi mở được mô tả; Wikipedia Vu Gia không nêu; PDF vjol tải về là nhị phân, chưa đọc được |

Suy diễn (không phải fact): A Vương có thể là nhánh riêng của Vu Gia chứ không "cùng hệ sông Bung phía trên SB5"; nhưng hầm dẫn xả vào Bung và nhà máy A Vương cùng xã Mà Cooih với SB5 làm hình dạng thực chưa rõ. **Cần bản đồ bậc thang / quy trình vận hành liên hồ Vu Gia (QĐ 1/2020? — chưa kiểm) để chốt.**
Hệ quả chắc chắn hơn: A Vương có **hồ điều tiết** (vận hành 2009) nên sản lượng quý là kết quả vận hành (EVN điều độ, lệnh xả lũ liên hồ) chứ không chỉ lượng nước về; SB5 là thủy điện dòng chảy/đập dâng nhỏ, bám sát mưa. Tín hiệu AVC bị làm mịn/lệch pha. (suy diễn)

## 2. Sản lượng
| | AVC | TV1 SB5 |
|---|---|---|
| Thiết kế | 815 tr kWh/năm, 210 MW (simplize; nguồn thứ cấp) | 187,06 tr kWh (bảng đấu giá), 2×28,5 MW |
| H1/2025 | >384 tr kWh = 52% KH năm EVNGENCO2 giao (DNSE, thứ cấp) | chưa có theo kỳ |
| Q3/2025 | KHÔNG tìm thấy tr kWh; chỉ DT 204,9 tỷ, LNST 96,6 tỷ (vietnamfinance) — khớp BQ | — |
| Thực tế | **KHÔNG thu được chuỗi sản lượng quý AVC nào** | 236,6 (2024); bq 2013-23 175,3 (README tv1_sb5_ppa_price_20261013) |
Không tìm được BCTN/thuyết minh gốc của AVC (không mở được hnx/AVC IR). → Bước 1 **không hoàn thành**: dùng doanh thu AVC làm proxy sản lượng (AVC bán theo giá EVN cố định/biểu giá nhà máy → xấp xỉ; chưa kiểm).

## 3. Đối chiếu doanh thu/LNST (đã đo — `avc_tv1_ticker_financial.csv`, quý 2018Q1→2026Q2, N=34 cặp)
- Corr doanh thu AVC~TV1: Pearson 0,522, Spearman 0,510. Corr LNST: Pearson 0,223 (NP TV1 lẫn tư vấn).
- YoY doanh thu (N=30): Pearson 0,224, Spearman 0,684.
- Tỷ trọng doanh thu theo quý (TB 2021-25): AVC Q1-Q4 = 21,8/20,4/25,3/32,5%; TV1 = 15,9/18,5/23,9/41,7%. **Phần lớn tương quan là MÙA VỤ chung (Q4 mùa lũ)**, không phải thông tin riêng về năm.
- N hiệu dụng ≈ 8 năm độc lập (không phải 34); chuỗi quý tự tương quan mùa vụ; TV1 doanh thu lẫn tư vấn + đột biến 2025Q4 (318 tỷ). Không đưa kết luận thống kê mạnh. Chưa khử mùa/khử thủy văn (chưa làm).
- Độ trễ: AVC công bố BCTC Q3 ngày 20/10/2026; TV1 Q3/2025 ngày 29/10/2025, Q2/2026 ngày 03/08/2026 → **AVC sớm hơn TV1 ~8-14 ngày** (BQ Release_Date). Q3/2026 TV1 chưa ra (tại 23/10). Chênh vài ngày chỉ có giá trị sau khi quý đã kết thúc — không phải chỉ báo "sớm" cho Q4.

## 4. Công bố sớm hơn BCTC?
Không tìm thấy AVC công bố sản lượng hàng tháng/CBTT (2 lần tìm; trang simplize/bbw chỉ có số năm). Trạng thái: **KHÔNG BIẾT** (chưa kiểm cổng HNX/UPCOM CBTT trực tiếp). Nếu AVC không có số tháng thì không có chỉ báo Q4/2026 từ AVC trước 20/01/2027 (BCTC Q4), tức muộn hơn TV1 không đáng kể (TV1 ~30/01).
Chỉ báo Q4 thay thế đề xuất (chưa kiểm khả thi): lượng mưa/lưu lượng về hồ thủy văn công khai (EVN/Trung tâm KTTV, hồ Sông Bung 4/A Vương/ĐăkMi 4 báo cáo trong đợt lũ — baovanhoa.vn, tuoitre.vn) và ONI/La Niña (xem hydro_hydrology_oni_overlay_20260912.md). Hồ S.Bung 4 (cùng sông Bung, phía trên SB5, nguồn Wikipedia) là ứng viên lý thuyết tốt hơn AVC nhưng EVN không niêm yết riêng → không dùng được.

## 5. Dòng cuối
**CHƯA ĐỦ DỮ LIỆU (nghiêng KHÔNG)**: (1) chưa xác minh A Vương cùng nhánh/ở thượng nguồn SB5; (2) không có chuỗi sản lượng AVC bằng tr kWh, cũng không có số tháng; (3) corr doanh thu 0,52 chủ yếu do mùa vụ chung, N độc lập ≈ 8; (4) hồ điều tiết làm AVC lệch pha; (5) AVC chỉ sớm hơn TV1 8-14 ngày sau quý, không phải tín hiệu Q4. Muốn nâng cấp: tìm số tr kWh theo tháng AVC trên HNX/IR và bản đồ hợp lưu có nguồn.
