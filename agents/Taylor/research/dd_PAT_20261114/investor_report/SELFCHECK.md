# Tự kiểm — PAT_DD_investor_report_20261114 (job Taylor_20261114_122716, 14/11/2026)

Kết quả đo trong phiên này (lệnh ở cột phải):
| Kiểm | Kết quả | Lệnh |
|---|---|---|
| grep SpaceX/ZaloPay/NAV/Taylor/Bobby/Mike/skeptic/Wendy/Spyros | RỖNG (md và html bỏ base64) | `grep -n -i -E ... PAT_DD_investor_report_20261114.md` |
| grep QUALIFY/AMBIGUOUS/NON/§2.5/fear/sợ hãi/kiểm định/xung đột lợi ích/đang nắm giữ cổ phiếu | RỖNG | idem |
| grep đính chính/thay bản/trước đây/đã sửa/vòng N/rN/revN/sai sót | RỖNG | idem |
| Số khớp REPORT.md + calc/valuation_PAT.csv | 28/29 chuỗi số tra có trong nguồn (chuỗi "8.100" là mục tra thừa, không dùng trong báo cáo); tâm 66.593→66.600, 56.608→56.600, 71.572→71.600, 106.120→106.100 (làm tròn 100), assert trong `figs()` | `build_report.py figs` |
| Số tính lại | giá/tâm +6,6%; cách cận trên −7,3%; vốn hoá 1.775 tỷ; tiền ròng/vốn hoá 23,4%; cổ tức 9.000/71.000 = 12,7%; P/E TTM 6,19 (LNST TTM 286,6); P/B 2,51; 0,446×15% = 0,0669 tỷ/phiên → 0,5 tỷ = 7,5 phiên, 2 tỷ = 29,9 phiên | python trong phiên |
| Đếm từ thân (không bảng/hình/tiêu đề/phụ lục) | 740; gồm bảng 1.777 (mục tiêu ≤ ~1.800) | python |
| PDF | 8 trang A4, pymupdf Story; render trang 1, 2, 3, 4, 5, 6, 7, 8 ra PNG và xem bằng mắt: dấu tiếng Việt đúng, bảng không tràn, không tách bảng | `build_report.py pdf` |
| HTML email | 11 ảnh, mọi `<img` có alt đóng đúng; dry-run KHÔNG gửi | `send_dd_report_email.py --dry-run --html-out` |

## ĐIỂM LỆCH SO VỚI BRIEF (cần Mike xác nhận)
- Brief/REPORT ghi "giá đóng cửa 13/11 = 72.700". BQ `tav2_bq.ticker` (Close = Price, khớp không điều chỉnh): **13/11 = 71.000**; 72.700 là đóng cửa **06/11**. Báo cáo dùng 71.000 (đo): cao hơn tâm 6,6%, cách cận trên 7,3%, vẫn TRONG vùng. Nếu giá DNSE 13/11 khác BQ thì đổi `PX` trong build_report.py và 5 chỗ trong md (tear sheet, §1, §5, hero, football field).
- Lợi suất cổ tức kế hoạch tính theo 71.000: 12,7% (REPORT 12,4% theo 72.700).
- Hình sản phẩm: BCTC/BN scan không có ảnh; website IR không truy cập được → sơ đồ vector "minh hoạ"; logo: không có → huy hiệu chữ PAT.
- Bản đồ: chỉ toạ độ xã Tằng Loỏng (vi.wikipedia 22,3048 B; 104,1267 Đ) và TP Lào Cai làm tham chiếu; không vẽ mỏ (không có toạ độ có nguồn).
- Không ghi `dd_price_zones.json`; không gửi email.
