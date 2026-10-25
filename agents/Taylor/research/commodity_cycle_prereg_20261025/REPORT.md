# REPORT — Pha đầu chu kỳ hàng hoá (job Taylor_20261025_061240)

PREREG: `PREREG.md` (commit `103df32e4`, 2026-10-25 13:17 ICT, trước khi chạy). Code: `run.py`
(chính), `posthoc.py` (ngoài PREREG). Log: `run.log`, `posthoc.log`. Số liệu: `summary.json`,
`events_main.csv`, `grid.csv`, `events_posthoc_105_3M.csv`. Chỉ đọc/nghiên cứu, không wire gì.

## Kết luận
1. **Thử nghiệm đã ghi trước: KHÔNG có edge.** Biến thể chính (giá/MA12 cắt lên 1,10, chân trời
   6M, so với nhóm cùng supersector ICB) **trượt cả 6/6 tiêu chí**: TB cụm **−1,7pp**, trung vị
   −6,8pp, CI90 [−10,2; +7,4]pp, 4/11 cụm dương (sign p=0,89), IS −4,4pp / OOS +0,5pp. Kém cả
   đường nền vô điều kiện (+3,4pp). N = **21 sự kiện / 11 cụm độc lập**; MDE ≈ 14pp ⇒ underpowered,
   chỉ loại được edge lớn. Không có chứng cứ cho edge lớn.
2. **Phát hiện ngoài PREREG (chỉ là giả thuyết, KHÔNG phải kết luận):** ngưỡng sớm hơn là **1,05,
   chân trời 3M**, là ô tốt nhất trong lưới 9 ô. TB cụm **+12,0pp**, t=3,62 trên 11 cụm, p một phía
   0,0024, **Bonferroni×9 p=0,021**. Bỏ 1 cụm bất kỳ vẫn ≥ +10,7pp, bỏ 1 họ bất kỳ vẫn ≥ +8,5pp,
   IS +6,9pp / OOS +16,2pp. Hơn đường nền 3M +11,1pp. Nhưng ô này **phai nhanh**: cùng ngưỡng ở 6M
   chỉ còn +8,7pp (Bonferroni p=0,69). Lưới cũng **không đơn điệu** (1,05 tốt, 1,10 xấu, 1,20 lẫn
   lộn), đúng dạng của nhiễu sau khi chọn ô. Cách đọc hợp lý: phần "rẻ" của pha hàng hoá chỉ có ở
   tín hiệu RẤT sớm, trong 1 quý; đến khi giá đã +10% so với MA12 thì thị trường đã định giá. Cần
   **PREREG mới + OOS tương lai** (paper từ 2026-11) trước khi dùng cho bất cứ việc gì.
3. **Câu hỏi gốc về MSR: hệ thống hiện tại KHÔNG thể bắt được, vì fleet không có chuỗi giá vonfram.**
   WB CMO không có vonfram. MSR tăng **×2,17 từ 06/2025 đến 01/2026** và **×3,45 đến 10/2026**
   (giá đóng cửa cuối tháng, `posthoc.log`), trong khi mốc LAG là release 2026-10-22 / vào 2026-10-29.
   Tức pha đầu đã diễn ra khoảng 9–15 tháng trước khi LAG bắt được. Thiếu dữ liệu là nút thắt,
   không phải thiếu quy tắc.

## A. Bản đồ mã↔hàng hoá — `commodity_map.csv` (56 dòng; 20 mã trong thử nghiệm chính)
Chuỗi dùng được (WB CMO, CANONICAL, 1960→2026M09): cao su RSS3, dầu thô, urê, DAP, đường thế giới.
Ngoài ra có đồng/thiếc, than, quặng sắt, gạo VN 5%, tôm, nhưng chỉ là proxy lỏng.
**Thiếu chuỗi giá dùng được (HỔNG):**
| Hàng hoá | Mã | Hiện có | Cần |
|---|---|---|---|
| Vonfram (APT/WO3) | MSR | không có gì | APT 88,5% (Fastmarkets/Argus, trả phí) hoặc cào SunSirs/SMM "ammonium paratungstate" (chưa có lịch sử) |
| Cước tàu dầu BDTI/BCTI | PVT, VIP, GSP | `freight_rates_quarterly.csv`: dựng lại theo quý từ 2018, KHÔNG có trong data_registry | chuỗi ngày (Baltic Exchange trả phí / cào investing.com dần) |
| Cước hàng khô BDI | VOS, VNA | `bdi_daily_real.csv` CANONICAL nhưng chỉ từ 2026-05 | lịch sử BDI ngày |
| SCFI/FBX | HAH | dựng lại theo quý | Freightos FBX CSV (miễn phí cho analyst qua email) |
| Xút | CSV | `caustic_soda_monthly.csv` là **SYNTHETIC** (.SOURCE.txt) ⇒ cấm dùng | SunSirs/CCF |
| Phốt pho vàng P4 | DGC | không có (DAP chỉ là proxy) | SunSirs P4 |
| Thép HRC/thép xây dựng VN | HPG, TLH, POM, SMC | không có (quặng sắt là chi phí đầu vào, chiều ngược) | SHFE HRC / giá thép VN theo tháng |
| Cá tra xuất khẩu | VHC, ANV, IDI | không có | VASEP / Hải quan theo tháng |
| Heo hơi | DBC, MML | `hog_price_vn.csv` CANONICAL nhưng chỉ từ 2019-01 ⇒ không có IS | backfill trước 2019 |

## B. Thiết kế: xem `PREREG.md`. Tóm tắt: sự kiện = R=P/MA12 cắt lên 1,10, thời gian chết 12
tháng, PIT vào lệnh ngày giao dịch đầu tiên ≥ ngày 11 tháng m+1. Chân phơi nhiễm và đối chứng đều
lấy bình quân đều trên universe_pit tại ngày vào. Cụm = các sự kiện có ngày vào cách nhau < 126 phiên.

## C. Kết quả chi tiết
Sự kiện chính (`events_main.csv`, X = r_exp − r_ctrl, 6M): 21 sự kiện trải 2014-03 → 2026-03,
theo họ: rubber 4, crude oil 5, urea 5, DAP 4, sugar 3. Chỉ 1 sự kiện dùng đối chứng fallback (DAP
2014-03, có 1 mã). Đường nền vô điều kiện 6M theo họ: rubber +4,1, crude +1,2, urea +4,7, DAP +1,3,
sugar +7,0pp ⇒ các mã sản xuất hàng hoá vốn đã nhỉnh hơn nhóm đối chứng ở mọi thời điểm. Ngày tín
hiệu không thêm được gì.

Lưới mô tả 3 ngưỡng × 3 chân trời (`grid.csv`, TB cụm, pp):
| ngưỡng | 3M | 6M | 12M |
|---|---|---|---|
| 1,05 | **+12,0** | +8,7 | +13,5 |
| 1,10 (chính) | +5,8 | **−1,7** | +2,6 |
| 1,20 | +1,3 | −0,1 | +13,1 |
Ô 12M khá ở cả 1,05 và 1,20 nhưng đường nền 12M cũng cao (+10,1pp ở hỗn hợp 1,05). Sau khi trừ đường
nền chỉ còn +8,2pp, Bonferroni p=0,21.

## Tái lập / kiểm tra
- Tính lại tay r_exp của 3 sự kiện (sugar 2016-04, rubber 2019-04, urea 2025-02) từ parquet: khớp tới
  1e-6 (`posthoc.log`). Không có NAV ⇒ không có self-check 0 VND (đã khai trong PREREG).
- PIT: tín hiệu chỉ dùng giá đến tháng m, vào lệnh ≥ ngày 11 tháng m+1. Không dùng `profit_*` hay
  `ticker_prune`. Rủi ro tồn dư: vintage WB hiện tại thay vì vintage tại thời điểm; `Close` là giá điều
  chỉnh của bản cache hiện tại.
- Cụm phụ thuộc mạnh: cụm 2020-H2 có 5 sự kiện. LOCO đã kiểm. Universe_pit chỉ có từ 2013, nên
  không có chu kỳ 2009–11.

## Lệch PREREG
Không có lệch trong biến thể chính. `posthoc.py` (LOCO/LOFO/Bonferroni cho ô 1,05 và đường nền theo
chân trời) là phân tích **thêm sau khi thấy kết quả**, được gắn nhãn post-hoc ở mọi chỗ.

## Đề xuất (cần user/Mike quyết, KHÔNG tự làm)
1. **Dữ liệu trước, quy tắc sau:** giao Winston dựng feed giá APT vonfram (bắt MSR) và cước BDTI/BDI
   ngày (bắt PVT/VOS), rồi đăng ký vào data_registry. Không có hai feed này thì câu hỏi "bắt MSR sớm"
   không có lời giải định lượng.
2. Nếu muốn theo đuổi phát hiện 1,05/3M: soạn PREREG-2 đóng băng đúng ô đó, rồi chạy **paper forward**
   từ 2026-11. Hiện đang có tín hiệu mô tả (không phải khuyến nghị): đường R=1,215 (cắt 1,05 ở
   2026-08), DAP R=1,111, cao su R=1,13. Quant-skeptic phản biện trước.
