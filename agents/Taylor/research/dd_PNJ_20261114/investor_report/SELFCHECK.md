# SELFCHECK — PNJ DD investor report 14/11/2026 (job Taylor_20261114_022155) — NỘI BỘ

Nguồn: REPORT.md md5 0ecbc539064726534c3d0b24e4bf8ac0 (đã qua phản biện), calc/model_r2_out.json, sector read 14/11.

| Kiểm | Kết quả |
|---|---|
| md5 md / pdf / html | 2179180a3274b180daa979293b88544c / fea39145d72f2000ec7306c330f4e7d8 / 3bac56b1bf166aca1f86ea10e8b6740b |
| PDF | 10 trang A4 (thân ~8 trang + phụ lục 2); Be Vietnam Pro; banner logo pnj.com.vn |
| Số từ thân (không bảng/hình/phụ lục) | 900 (mục tiêu ≤1.800) |
| Grep nội bộ `SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|NON|AMBIGUOUS|QUALIFY|fear|đính chính|vòng [0-9]|r[0-9]\b` | rỗng ở md, text PDF, HTML (đã bỏ base64) |
| Grep bổ sung `excluded_tickers|custom30|park|CAPIT|INTERNAL|8L|§2.5|sợ hãi|xung đột lợi ích|thay bản|trước đây|đã sửa|sai sót|mù giá` | rỗng |
| HTML dry-run (`send_dd_report_email.py --dry-run --html-out`) | 14 `<img>`, alt đóng đúng; KHÔNG gửi |
| Glyph | md không còn ký tự ngoài font (→ ⇒ Δ β đã thay) |
| Xem bằng mắt | trang 1 (banner+hero+KPI), trang 8 (định giá+rủi ro), thumbnail 10 trang |
| Giá | DNSE latest_trade PNJ G1 matchPrice 14,95 @ 2026-11-13 14:45:04 (HOSE/STO); đọc 09:23 ICT 14/11 (thứ Bảy) |
| Lãi suất | dcf_rate_display 2026-11-14: r* 15,1% (p75), TPCP 10Y 4,57% (+0,57pp, chưa đối chiếu) |
| Luật 9/10/15 | tiêu đề câu kết luận; hero; khung 4 ảnh sản phẩm (pnj.com.vn); bản đồ KHU VỰC TP.HCM (không toàn quốc) |
| Luật 12 | TRÊN vùng cơ sở 6.370–7.640; 3 kịch bản + xác suất nhận định (không dùng làm tâm); bảng tích cực/tiêu cực ngang dòng; đổi ý hai chiều |
| Luật 19 (theo chỉ đạo dispatch) | KHÔNG mô tả định giá là "mù giá" |
| Nội dung (a) | −6.270 = kế hoạch điều chỉnh do DN công bố; 7.071 / 550tr cp / 21.057,9 = số công bố |

## Giới hạn / quyết định trình bày
- Bản đồ chỉ có trụ sở (toạ độ gần đúng); phân bổ cửa hàng theo tỉnh không có nguồn ⇒ không vẽ.
- Bỏ khỏi bản NĐT: thông tin báo chí "em trai thành viên HĐQT" (chưa có nguồn gốc đối chiếu) ⇒ chỉ ghi ở Giới hạn.
- Năm thành lập không tìm thấy nguồn ⇒ chỉ dùng mốc niêm yết 23/03/2009 (DNSE secdef) và GP vàng miếng 2012.
- Xác suất kịch bản ~20/50/30 là nhận định định tính, ghi rõ không dùng tính kỳ vọng.
- "Mức LNST ngầm định ~2.670 tỷ" = nội suy tuyến tính trên lưới model (g5, n550) — ước lượng.
- Chưa ghi `kb/dd_price_zones.json` (bước sổ mức giá thuộc Mike/sau khi user duyệt; vùng đang ở trạng thái tham khảo).
