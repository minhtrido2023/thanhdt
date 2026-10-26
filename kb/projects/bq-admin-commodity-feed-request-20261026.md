# Đề nghị bổ sung chuỗi hàng hoá cho `tav2_bq.commodity_prices` (gửi bq_admin)
> Soạn 2026-10-26 (Winston) theo REPORT.md §1 "Hổng còn lại". User chuyển tay. Nguồn gợi ý là `ước lượng` theo hiểu biết thị trường — bq_admin kiểm tra lại.

Hiện bảng có 103 mã TE + 22 mã WB, nhưng nhiều mã TE tên nghe đúng mà là hàng khác (xem bẫy 5 trong `kb/data_registry/feeds/bq_commodity_prices.md`). Các chuỗi dưới đây chưa có hoặc chỉ có bản sai hàng:

| Mã CP VN | Chuỗi cần thêm | Vì sao | Nguồn gợi ý | Ưu tiên |
|---|---|---|---|---|
| MSR | Vonfram APT (USD/mtu) | Giá bán chính của MSR; hiện KHÔNG có gì | Fastmarkets / Argus / SunSirs (APT, CN) | **Cao nhất** |
| CSV | Xút (caustic soda, CNY/t hoặc USD/t) | `soda_ash` TE là Na2CO3, không phải xút | SunSirs (NaOH 32%/ 99%), ICIS | Cao |
| DGC, PAT | P4 phốt pho vàng (CNY/t) | `phosphorus` TE là quặng photphat, 43 giá trị khác nhau từ 2022 | SunSirs (yellow phosphorus) | Cao |
| PVT, VIP, GSP | Cước tàu dầu BDTI/BCTI (ngày) | Chỉ có BDI (hàng khô) | Baltic Exchange | Trung bình |
| HPG | HRC Trung Quốc/VN (CNY/t) | `hrc_steel` TE là HRC Mỹ | SunSirs / Mysteel / SHFE HRC | Trung bình |
| VHC, ANV, IDI | Cá tra, tôm (VND/kg hoặc USD/kg) | Chỉ có salmon NOK (thưa) | VASEP, giá nội địa, USDA/Urner Barry | Trung bình |
| — (nông sản XK) | Hồ tiêu, điều, Robusta, gạo VN 5% — theo NGÀY | `coffee` = Arabica, `rice` = gạo thô CBOT | VPSA, Vinacas, ICE Robusta, VFA/Vietnam Rice 5% | Trung bình |
| DPM, DCM, BFC, LAS | Kali (potash) chuỗi ngày | WB `potassium_chloride` chỉ tháng | TE/ Argus / Profercy | Thấp |
| DBC, BAF, HAG… | Heo hơi VN trước 2019 | `data/hog_price_vn.csv` ngoài BQ; `lean_hogs` là CME | Bộ NN&PTNT, giavatnuoi, chuỗi nội bộ | Thấp |

## 3 câu hỏi cho bq_admin
1. **SLA cập nhật** từng nguồn (TE daily/weekly, WB, GDT, nguồn mới): lịch, trễ tối đa, ai chịu trách nhiệm khi trễ? (đã biết: nạp chung 23:00 ICT/ngày; có mã TE chỉ cập nhật tuần.)
2. **Báo mã ngừng cập nhật:** có cơ chế nào không? (đã biết: KHÔNG — fleet tự giám sát bằng `commodity_freshness_monitor.py`.) Nếu bổ sung được một cột/bảng `last_success_at` theo mã thì tốt.
3. **TE có đúng mã** cho các chuỗi trên không (APT, xút, P4, BDTI/BCTI, HRC TQ, cá tra/tôm, tiêu/điều/Robusta/gạo VN), hay phải lấy nguồn khác (SunSirs, Baltic, VASEP…)? Nếu nguồn khác: định nghĩa hàng + đơn vị ghi rõ trong `name_en`/`unit`.
