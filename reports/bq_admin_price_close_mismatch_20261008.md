# Gửi bq_admin — `tav2_bq.ticker`: `Price` và `Close` lệch nhau 1–2 bước giá, kể cả ngày không có sự kiện

Ngày 08/10/2026 · nguồn: Mike (fleet), số đo trực tiếp trên BQ.

## Tóm tắt
- Hệ số điều chỉnh của vendor **đúng** cho DRI, DVN, SHC (khớp hệ số tự tính tới ≤0,07%).
- Cái lệch là **giá thô**: ở một số phiên, `Close` (đã điều chỉnh) × hệ số **không** ra đúng `Price` của
  cùng phiên. Phần chênh luôn là số nguyên bước giá (thường ±100đ) — tức hai trường đến từ **hai bản in
  giá khác nhau**, không phải do làm tròn (làm tròn ở bước 10đ chỉ gây ≤0,04%).
- Xảy ra cả ở phiên **không có sự kiện quyền nào** (`Close` ≠ `Price` trong khi hệ số = 1).

## Ví dụ
| Mã | Phiên | Price | Close | Close × hệ số | Ghi chú |
|---|---|---|---|---|---|
| DRI | 2026-09-14 | 14.100 | 13.240 | 14.200 | hệ số 1,072464 (cổ tức 1.000đ, GDKHQ 22/09). Broker DNSE: 14.200 |
| DRI | 2026-09-11 | 14.400 | 13.520 | 14.500 | |
| DRI | 2026-09-21 | 14.800 | 13.890 | 14.900 | |
| DRI | 2026-09-25 | 15.000 | 15.100 | 15.100 | hệ số = 1 (sau GDKHQ), không có sự kiện |
| DRI | 2026-10-06 | 16.300 | 16.400 | 16.400 | hệ số = 1. Broker DNSE: 16.400 |
| DVN | 2026-06-22 | 20.400 | 19.470 | 20.600 | hệ số 1,05848 |
| SHC | 2026-06-30 → 07-09 | 10.900 (đứng) | 11.810 | 12.400 | 8 phiên KL 0–13 cp; 07-10 Price lên 12.400 |

Các phiên còn lại của cùng mã khớp hoàn hảo (vd DRI 09-17, 09-18: 14.800 / 13.800 = 1,072464).
Ở 2 ngày đối chiếu được với broker (09-14, 10-06), **`Close` khớp broker, `Price` lệch**.

## Quy mô (2026-01-01 → 2026-10-07)
Chỉ đếm phiên lệch **đơn lẻ** (tỉ số Price/Close khác >0,3% so với 2 phiên kề, trong khi 2 phiên kề khớp nhau):
**2.278 phiên / 887 mã / 207.563 dòng (~1,1%)**, trong đó 738 phiên có KL ≥100.000. Trung vị chênh ±100đ.

| Tháng | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Số phiên | 905 | 219 | 313 | 255 | 232 | 215 | 81 | 33 | 20 | 5 |

(Không tính các chuỗi lệch nhiều phiên liền nhau như DRI 09-10/11/14 hay SHC — con số thật cao hơn.)

## Nhờ admin
1. **Xác nhận trường nào là giá đóng cửa chuẩn** khi `Price` và `Close`·hệ số không khớp — và vì sao hai
   trường lấy từ hai bản in khác nhau (ATC vs khớp cuối? snapshot trong phiên vs cuối ngày?).
2. **Sửa tận gốc**: lưu giá thô MỘT lần, sinh `Close` = `Price` ÷ hệ số luỹ kế từ chính giá đó — khi đó
   hai trường không thể lệch nhau.
3. **Đưa cột hệ số luỹ kế** (vd `adj_factor`) vào bảng. Phía fleet sẽ so hệ số với hệ số trực tiếp thay vì
   suy ngược từ Price/Close, nên lỗi giá thô và lỗi hệ số không còn lẫn vào nhau.

Phía fleet trong lúc chờ: detector tách nhãn "lệch trường Price" khỏi DRIFT (đang làm), không ảnh hưởng giao dịch.
