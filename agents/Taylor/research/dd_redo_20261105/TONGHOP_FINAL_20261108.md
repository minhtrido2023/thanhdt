# DD redo mùa BCTC Q3/2026 — bảng tổng hợp tâm / P10–P90 (lập 08/11/2026)
Tâm = giá trị kỳ vọng trọng số kịch bản, sau chiết khấu thanh khoản (cỡ tham chiếu 5 tỷ). P10/P90 = phân vị có trọng số ở mức kết cục của lưới kịch bản (vòng 2, `_shared/wpct.py`). Giá = đóng cửa 04/11/2026 (SCL: giá cum-quyền). "Giá vs tâm": âm = giá dưới tâm (rẻ hơn tâm), dương = giá trên tâm. Moat = nhãn DD-5F (08/11), chỉ thông tin, không trừ vào định giá (user chốt 08/11). DCM lấy bản r5 (04/11).

| Mã | Giá 04/11 | Tâm | P10 | P90 | % KC dưới giá | Giá vs tâm | Nhãn | Moat 5F |
|---|---|---|---|---|---|---|---|---|
| MBB | 19.250 | 23.804 | 14.444 | 35.860 | 32% | -19% | TRONG vùng | NARROW |
| FPT | 53.900 | 54.203 | 32.389 | 74.557 | 48% | -1% | TRONG vùng | NARROW |
| HPG | 21.700 | 16.286 | 8.942 | 23.520 | 84% | +33% | TRONG vùng | NARROW |
| HHS | 9.550 | 10.387 | 8.252 | 12.827 | 35% | -8% | TRONG vùng | NONE |
| DGC | 33.450 | 44.767 | 32.518 | 57.101 | 12% | -25% | TRONG vùng | NARROW |
| DDV | 15.200 | 13.109 | 10.115 | 16.270 | 77% | +16% | TRONG vùng | NONE |
| PVP | 18.400 | 22.366 | 12.702 | 32.834 | 31% | -18% | TRONG vùng | NONE |
| PVT | 21.000 | 17.675 | 12.533 | 23.135 | 78% | +19% | TRONG vùng | NONE |
| SIP | 49.000 | 53.175 | 34.501 | 73.949 | - | -8% | TRONG vùng | NARROW |
| SCL | 30.000 | 22.769 | 17.348 | 27.119 | 98% | +32% | TRÊN vùng (>P90) | NONE |
| TV1 | 19.600 | 15.379 | 4.693 | 24.544 | 71% | +27% | TRONG vùng | NARROW |
| TV2 | 27.400 | 15.832 | 2.726 | 30.675 | 84% | +73% | TRONG vùng | NONE |
| NT2 | 22.650 | 23.617 | 18.386 | 28.278 | 38% | -4% | TRONG vung | NONE |
| SAS | 34.700 | 31.066 | 23.751 | 38.022 | 74% | +12% | TRONG vung | NARROW |
| SZL | 27.650 | 32.391 | 28.966 | 36.075 | 3% | -15% | DUOI vung (<P10) | NARROW |
| TCH | 12.750 | 13.768 | 12.559 | 14.983 | 19% | -7% | TRONG vung | NONE |
| NNC | 46.900 | 57.589 | 30.219 | 93.649 | 37% | -19% | TRONG vùng | NARROW |
| DRI | 13.500 | 14.092 | 12.006 | 16.146 | 35% | -4% | TRONG vùng | NARROW |
| MVC | 13.800 | 15.276 | 9.857 | 23.516 | 51% | -10% | TRONG vùng | NARROW |
| DCM (r5) | 33.000 | 24.326 | 20.522 | 27.708 | - | +36% | ĐẮT (trên P90) | - |

## Giới hạn cần biết
- Giá là 04/11, chưa cập nhật tới phiên 07/11.
- Vòng 2 (05/11) chưa có phản biện độc lập hoàn tất: 7 phiên fundamental-skeptic bị cắt giữa chừng do chạm giới hạn usage 05/11. Vòng 1 NNC/DRI/MVC đã bị REFUTED (lưới, nguồn) và vòng 2 đã áp đính chính nhưng chưa được phản biện lại. Phản biện 08/11 chỉ phủ phần DD-5F của một số mã (NT2/PVT/TV2 CONFIRMED, DDV/PVP REFUTED rồi sửa), không phải toàn bộ r2.
- Chưa ghi sổ `kb/dd_price_zones.json` (luật: chỉ ghi sau phản biện). Chưa email.
- Nhãn "TRONG vùng" của hầu hết mã là hệ quả định nghĩa vùng P10–P90 rất rộng (vd TV2 P10 2.726 / P90 30.675), không phải tín hiệu rẻ. Đọc cột % kết cục dưới giá và Giá vs tâm.
