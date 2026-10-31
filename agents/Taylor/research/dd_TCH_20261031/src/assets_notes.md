# TCH — ghi chú hình ảnh & toạ độ cho báo cáo nhà đầu tư (luật 15 skill dd-investor-report)
> Lập 31/10/2026, job `Taylor_20261031_145612`. Mọi ảnh dưới đây đều do **công ty tự công bố** trên hoanghuy.vn (truy cập 31/10/2026). Đây là ảnh phối cảnh/marketing, không phải ảnh hiện trạng, nên khi đưa vào báo cáo phải chú thích "Ảnh: Hoàng Huy công bố (phối cảnh)".

## Logo
| File | Nguồn | Ghi chú |
|---|---|---|
| `src/logo.png` (810×268) | cắt từ `https://www.hoanghuy.vn/images/general/1201731510515.png` (header trang chủ, alt "CÔNG TY CỔ PHẦN ĐẦU TƯ DỊCH VỤ TÀI CHÍNH HOÀNG HUY") | chữ "HOANG HUY GROUP"; nền là ảnh mờ, không trong suốt. Muốn nền trắng sạch thì phải lấy từ BCTN 2025 (bản PDF có text) |
| `src/logo_candidate_general.png` | ảnh gốc header 1172×150 | |
| `src/logo_candidate_finance.png` | `/images/global/hoanghuyfinance.png` (262×23, chữ nhỏ) | không dùng |

## Ảnh dự án (`src/photos/`)
| File | Dự án | URL gốc (hoanghuy.vn) |
|---|---|---|
| `newcity_phoicanh_tongthe.jpg` | Hoàng Huy New City (phối cảnh tổng thể) | `/images/users/images/New%20City%20Phoi%20canh%20tong%20the.jpg` (trang `/duanbatdongsan/hoang-huy-new-city/`) |
| `newcity_shophouse.jpg` | Hoàng Huy New City (shophouse) | `/images/users/images/New%20City%20Anh%20shophouse.jpg` |
| `commerce_1.jpg`, `commerce_14.jpg`, `commerce_15.jpg` | Hoang Huy Commerce (H1/H2/H3) | `/images/users/images/1_1.jpg`, `14.jpg`, `15.jpg` (trang `/duanbatdongsan/hoang-huy-commerce/`) |
| `commerce_banner.jpg` | Hoang Huy Commerce (banner) | `/images/hinhanh/du%20an%20commerce%20realestate202158163538.jpg` |

**Không có:** trang Green River (`/duanbatdongsan/hoang-huy-green-river/`) không có ảnh riêng, chỉ có chữ. Ảnh HH1–HH4 (Hải Đăng/Cánh Buồm), 150 Tô Hiệu và I.14 Bắc Sông Cấm cũng không có trên website. BCTN 2025 (bản PDF có text, 80 trang, `src/gaps/pdf/20260715_-_tch_-_bao_cao_thuong_nien_2025.pdf`) có ảnh dự án nhúng; nếu cần thì trích bằng pymupdf `page.get_images()`. **Chưa trích.**

## Toạ độ (WGS84) — nguồn: OpenStreetMap Nominatim, truy vấn 31/10/2026
| Điểm | Lat, Lon | Độ chính xác | Kết quả Nominatim |
|---|---|---|---|
| Trụ sở 116 Nguyễn Đức Cảnh (Lê Chân) | 20.85492, 106.67596 | cấp **phố** (không có số nhà) | Phố Nguyễn Đức Cảnh, Cát Dài, P. Lê Chân |
| 150 Tô Hiệu (Lê Chân) | 20.85117, 106.68070 | cấp **phố** | Phố Tô Hiệu, An Biên, P. Lê Chân |
| Hoang Huy Commerce H1/H2 (Võ Nguyên Giáp, Lê Chân) | 20.82977, 106.68587 | trong KĐT (khớp POI ở KĐT Hoàng Huy Commerce) | KĐT Hoàng Huy Commerce – Võ Nguyên Giáp |
| Hoàng Huy New City (NC-II, HH1–HH4) (Thủy Nguyên) | 20.89262, 106.68241 | POI khu đô thị | KĐT Hoàng Huy New City, P. Thủy Nguyên |
| Green River (phường Hoa Động cũ → P. Thủy Nguyên) | 20.89273, 106.66566 | **xấp xỉ**: Nominatim khớp "Đông Hoa", không khớp dự án | cần kiểm lại trên bản đồ trước khi vẽ |
| Lô I.14 Bắc Sông Cấm (Thủy Nguyên) | 20.87740, 106.67800 | POI cấp KĐT Bắc Sông Cấm (không khớp riêng lô I.14) | KĐT Bắc Sông Cấm, P. Thủy Nguyên |
| Văn phòng Hà Nội 183 Bà Triệu (HHS/CRV, tòa nhà Hoàng Huy) | 21.01224, 105.84934 | số nhà | Tòa nhà Hoàng Huy, 183 Bà Triệu |
| 17B Bà Triệu (HN, đang nhận chuyển nhượng) | — | **không định vị được**: Nominatim trả về sai chỗ (Phú Xuyên) | |
| Pruksa Town (An Hải), Grand Tower (Cầu Bính), đại lý/nhà máy ô tô | — | **không tìm thấy** trên Nominatim | |

Ghi chú: tất cả dự án BĐS nằm trong bán kính khoảng 8 km quanh trung tâm Hải Phòng. NC-II, Green River và I.14 ở bờ bắc sông Cấm (Thủy Nguyên), còn H2 và 150 Tô Hiệu ở Lê Chân. Mức tập trung địa lý này khớp với cờ E21 trong REPORT §10.
