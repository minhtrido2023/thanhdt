# SELFCHECK — VCB investor report 22/11/2026 (job Taylor_20261122_094949)

- Nguồn số: ../REPORT.md + ../calc_r4_output.txt (calc.py, assumptions md5 85d41e08f834127e57cd740ed88dd931). build_report.py assert: tâm 35.497, xấu 28.958, mốc 16% 42.035, Ke±100bp 41.950/30.764, có trọng số 38.787 (sai số ≤1 đ); giá BQ 17/11 = 52.100, 20/11 = 50.200.
- Số mới tính (cùng công thức P/B, chỉ hiển thị): ở giá 20/11 50.200 đ: P/B 1,654, ROE hàm ý 17,7%, Ke hàm ý 11,6%; giá/tâm 1,47 (17/11), 1,41 (20/11).
- Giá: DNSE latest_trade VCB G1 20/11/2026 14:45:05 matchPrice 50,2 (secdef basicPrice 50,2; marketId STO = HOSE). Hôm nay CN 22/11 HOSE đóng cửa. Kết luận (TRÊN vùng 30.800–42.000) không đổi ở cả 52.100 và 50.200.
- Lãi suất (luật 17): dcf_rate_display('2026-11-17'): r* 15,1% (panel 30/10, n=147, p75), TPCP 10Y 4,57% Δ12T +0,57pp. deposit_rate_vn 20/11: 7,40% (cctg_12m 02/11) => r 13,5% không điều chỉnh.
- Logo/ảnh: vietcombank.com.vn (Logo-VCB-no-60.png, KHCN_MB-NGANG_Dark.jpg, Desktop_HahaVisa.jpg), tải 22/11/2026. Banner: make_title_banner.py.
- Bản đồ (luật 15): 2 bản đồ khu vực (Hà Nội, TP.HCM), KHÔNG toàn quốc; số PGD 30/9/2025 Vietnamnet; toạ độ trung tâm quận Hoàn Kiếm / TP.HCM theo Wikipedia (gần đúng). Không có số mạng lưới theo vùng cuối 2025 -> ghi Phụ lục D.

## Grep (md + subject + HTML đã bỏ base64)
```
grep -n -i -E "đính chính|thay bản|trước đây|đã sửa|vòng [0-9]|\br[0-9]\b|sai sót|kiểm tra độc lập|chưa render" md subject.txt html   -> rỗng (rc=1)
grep -n -i -E "SpaceX|ZaloPay|giá vốn|\bNAV\b|Taylor|Bobby|Mike|skeptic|Wendy|Spyros" ...                                      -> rỗng (rc=1)
grep -n -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu|vùng giá nên mua|DISPLAY-ONLY|UNVERIFIED" ... -> rỗng (rc=1)
```
- HTML: 15 thẻ <img>, 0 thẻ thiếu alt đóng đúng.
- Số từ thân (trước Phụ lục A, bỏ bảng/hình): 1.262 (mục tiêu ≤ ~1.800).
- PDF 12 trang (thân 10, phụ lục 2). md5 md 60c3ebb06e77fbe98988ff89d3764816 · pdf 0dcfbe9e4012e99e353b61b61c38e7c5.
- Font: dấu "~" của Be Vietnam Pro trông như dấu trừ ở cỡ nhỏ -> đổi toàn bộ sang "≈"; không dùng → ⇒ β.

## Hình (figs/, mỗi hình có CSV)
fig_00_hero · fig_01_npat_quarterly · fig_02_income_9m · fig_03_asset_quality · fig_04_funding · fig_05_roe · fig_06_roe_value · fig_07_football_field · fig_08_pb_peers · fig_09_price_12m (dựng, chưa đưa vào thân để giữ ≤10 trang) · fig_10_dividend · fig_11_rate_sens · fig_12_risk_matrix · fig_13_products · fig_14_map (ghép fig_map_hn + fig_map_hcm) · title_banner. Dữ liệu gốc: fin_quarterly_bq.csv, price_raw.csv.

## send_dd_report_email.py --dry-run --html-out
`to=<địa chỉ user trong secrets> images=15 size=7.5MB subject=VCB: tài sản sạch nhất, vốn rẻ nhất hệ thống — nhưng giá 52.100 đ đã trả cho ROE bền ≈18%, trên vùng giá trị hợp lý 30.800–42.000 đ` · `DRY-RUN: không gửi`. KHÔNG gửi email.

## Kiểm bằng mắt (render PNG 110 dpi)
Trang 1 (banner+hero+KPI), 3 (ngành+bản đồ+sản phẩm), 4 (LN), 8 (định giá: ROE/kịch bản/độ nhạy, football field, P/B), 10 (đổi nhận định): dấu tiếng Việt đúng, bảng không tràn. Đã sửa: tiêu đề football field bị cắt, ma trận rủi ro bị nén, nhãn ROE chồng nhau, trang 4 trống nửa (bỏ ngắt trang).
- Chưa làm: ghi kb/dd_price_zones.json (việc của Mike sau khi duyệt).
