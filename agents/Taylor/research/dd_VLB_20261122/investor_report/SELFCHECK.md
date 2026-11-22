# SELFCHECK — VLB investor report 22/11/2026 (job Taylor_20261122_100749)

- Nguồn số: ../REPORT.md (r2) + ../model/output_r2.txt (dcf_vlb.py md5 93e0ec77a0cc97bd8b48af98249e0939). build_report.py assert: có trọng số 52.732 (±1), sau CK 51.163, vùng 0,85/1,15 × tâm = 43.489/58.838, tiền ròng waterfall 488,8, NP Q3/26 BQ 117,41, giá 20/11 Price = 48.100.
- **PHÁT HIỆN MỚI (không có trong REPORT r2):** VLB tạm ứng cổ tức 2026 2.500 đ/cp, GDKHQ 19/11/2026, trả 17/12 (vietstock.vn 11/2026); BQ Close/Price 18/11 = 0,9529 ≈ (52.900−2.500)/52.900 = 0,9527 ⇒ khớp. Tiền ròng 30/9 (488,8 tỷ) CÒN chứa khoản này, giá 48.100 (20/11) thì KHÔNG ⇒ REPORT r2 so lệch cơ sở. Cùng cơ sở: tâm sau CK = (52.732 − 2.500) × (1 − 0,0298) = **48.735**; vùng ±15% 41.425–56.045; giá/tâm **0,987** (REPORT r2: 0,94). Kết luận TRONG vùng không đổi. Báo cáo trình bày cả cơ sở 30/9 (khớp REPORT) và cột "cùng cơ sở với giá".
- Lãi suất (luật 17): dcf_rate_display('2026-11-20'): r* 15,1% (30/10, n=147, p75; đỉnh 2022 15,9%, đáy 12,1%), TPCP 10Y 4,57% Δ12T +0,56pp (nguồn chưa đối chiếu độc lập). r 13,5% neo lãi huy động 12T hiệu dụng 7,4% (18/11).
- Logo/ảnh: bbcc.com.vn (http; upload/hinhanh/logo-4390.png, ảnh trụ sở, 4 ảnh sản phẩm), tải 22/11/2026. Banner: make_title_banner.py.
- Bản đồ (luật 15): 2 bản đồ khu vực (cụm mỏ Biên Hòa–Vĩnh Cửu–Thống Nhất; thị trường TP.HCM/Bình Dương cũ/BR–VT cũ/Tây Ninh/Cần Thơ), KHÔNG toàn quốc; toạ độ OSM Nominatim 22/11/2026 (Wikipedia API bị giới hạn), ghi "vị trí gần đúng". Soklu đặt ở trung tâm huyện Thống Nhất cũ.

## Grep (md + subject + HTML bỏ base64) — đều rỗng (rc=1)
- luật 18: `đính chính|thay bản|trước đây|đã sửa|vòng [0-9]|\br[0-9]\b|sai sót`
- nội bộ: `SpaceX|ZaloPay|giá vốn|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros`
- khách quan: `QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu|vùng giá nên mua|tranche|HARD ABANDON|time stop|DISPLAY-ONLY|UNVERIFIED|\bRẺ\b|ĐẮT|TRUNG TÍNH|sleeve`
- HTML: 13 thẻ <img>, 0 thiếu alt. Số từ thân (trước Phụ lục A, bỏ bảng/hình): 959.
- PDF 8 trang (thân 7, phụ lục 1). md5 md c0994fc3f5e704bf7647c80367a5fcae · pdf b8fa5bd449dd56f6260f6465811f7b95.

## send_dd_report_email.py --dry-run --html-out
images=13 size=10.2MB · DRY-RUN: không gửi. KHÔNG gửi email (chờ user).

## Kiểm bằng mắt (PNG 105 dpi): trang 1 (banner+hero+KPI), 3 (doanh nghiệp: chuỗi giá trị, ảnh SP, bảng mỏ, biểu đồ quý), 5 (khoản bù trừ + định giá + football field): dấu Việt đúng, bảng không tràn. Đã chỉnh: tiêu đề 2 biểu đồ quý chồng nhau, nhãn trung vị, glyph ⇒ thiếu trong font hình, tiêu đề mục 6 mồ côi cuối trang.
- Chưa làm: ghi kb/dd_price_zones.json (việc của Mike; nên dùng cơ sở cùng giá 48.735 hoặc ghi rõ cơ sở 30/9).
