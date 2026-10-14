# Khai báo trước (pre-registration) — viết TRƯỚC khi chạy mô hình ma trận, 2026-10-14 ~12:58 ICT

Job Taylor_20261014_055001 (resume của 051329). Chưa có FV nào của mô hình mới được tính khi viết file này.
md5 của file này được ghi lên bus (heartbeat) trước khi chạy `fpt_deconsol_dcf.py`.

## Tổ hợp chính thức (KHÔNG đổi sau khi thấy kết quả)
| Nhãn | g_T | r | Phạm vi / FOX | g stage-1 |
|---|---|---|---|---|
| Thận trọng | `cpi` (TB CPI 5 năm) | rf hiện hành + ERP 8,5% | core ex-FOX + FOX theo giá thị trường, chiết khấu 30% | công thức production (g_T + 0,5×(g_hist − g_T)), g_hist = TĂNG TRƯỞNG THẤP NHẤT trong {LNST mẹ core 3 năm, kế hoạch 2026} |
| Cơ sở | `cpi_gdp_half` | rf hiện hành + ERP 7,5% | core ex-FOX + FOX chiết khấu 15% | công thức production, g_hist = TB {LNST core 3 năm, kế hoạch LNTT 2026 +15%} |
| Lạc quan | `cap_rf` (production default) | rf hiện hành + ERP 6,5% (production default) | core ex-FOX + FOX chiết khấu 0% | công thức production, g_hist = CAO NHẤT |

Lý do chọn cơ sở = điểm giữa mỗi trục: production default (cap_rf × ERP 6,5%) cho r − g_T = 6,5% là đầu
lạc quan; `cpi` × ERP 8,5% là đầu xấu. Hàng "rf chậm MA12" được báo trong ma trận nhưng KHÔNG dùng làm
nhãn nào (là biến thể nghiên cứu 13/10, chưa duyệt).

## FCFE core (cách làm khai trước)
FCFE_core_năm = (CF_OA + CF_Invest)_FPT hợp nhất cũ − (CF_OA + CF_Invest)_FOX hợp nhất (BQ, cùng quý),
2023–2025; KHÔNG cộng lại cổ tức FOX trả cho FPT (vì phần vốn FOX được định giá riêng theo giá thị trường
→ cộng cổ tức = đếm trùng). Gốc = trung bình 3 năm (giống production) ; báo thêm biến thể 2 năm & chuẩn hoá
theo tỷ lệ FCF/LNST core.
Cầu nối: FV/cp = (PV FCFE core + 45,66% × vốn hoá FOX × (1 − chiết khấu)) / OShares. Không trừ nợ ròng
(FCFE: lãi vay đã trong CFO, lãi tiền gửi + gửi/rút kỳ hạn đã trong CF_Invest) — báo riêng một dòng kiểm.

## Quyết định stop
Stop 50,5k "hợp lý" chỉ khi < FV thận trọng. Nếu FV thận trọng < 50,5k thì nói thẳng stop không được FV đỡ.
