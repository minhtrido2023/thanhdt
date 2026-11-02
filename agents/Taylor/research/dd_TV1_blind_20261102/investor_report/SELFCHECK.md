# SELFCHECK — báo cáo nhà đầu tư TV1 02/11/2026 (NỘI BỘ, job Taylor_20261102_152306)

Tái lập: `python3 -I ../valuation_blind_v2.py > ../valuation_blind_v2_out.txt` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all`
→ banner: `/home/trido/thanhdt/wc_venv/bin/python ~/.claude/skills/dd-investor-report/scripts/make_title_banner.py --title "<dòng 1 md bỏ '# '>" --ticker TV1 --kicker "Báo cáo due diligence · UPCOM: TV1" --sub "Nhóm nghiên cứu · 02/11/2026" --logo figs/logo.png --out figs/title_banner.png`
→ HTML: `python3 -I ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py <md> --pdf <pdf> --banner figs/title_banner.png --dry-run --html-out <html>` (dry-run: to=user, 17 ảnh, 8,3MB). **Chưa gửi email — Mike gửi.**

| Kiểm | Kết quả |
|---|---|
| grep cấm (đính chính/thay bản/trước đây/đã sửa/vòng N/rN/sai sót/REFUTED/lỗi phương pháp/bản r/phản biện lần/kết luận đổi/chạy mù/nhiễm) trên md + html (bỏ base64) + figs/*.csv + text PDF | RỖNG |
| grep nội bộ (SpaceX/ZaloPay/giá vốn/NAV/Taylor/Bobby/Mike/skeptic/Wendy/Spyros/legal-vn/state_TV1/QUALIFY/AMBIGUOUS/fear/kiểm định/xung đột lợi ích/đang nắm giữ) | RỖNG |
| `<img` trong HTML có alt đóng đúng | 17/17 |
| Số trong md khớp `valuation_blind_v2_out.json` (tâm, P20/P80, toàn lưới, cấu phần, LNST 2028 ×5, tư vấn ×4, cảnh báo ×4, truy thu) | khớp (script kiểm trong phiên; chỉ khác dấu trừ Unicode) |
| Độ dài | PDF 10 trang (thân 9, phụ lục ~1); thân 996 từ ngoài bảng/hình |
| Xem bằng mắt | trang 1 (banner, hero, KPI, ba điều), trang 4 (tư vấn), trang 7 (định giá), trang 8 (peer): dấu tiếng Việt đủ, bảng không tràn |
| Giá | DNSE latest_trade 19.500 đ, khớp 14:34:40 02/11/2026 (../phase2/dnse_20261102.json, fetch 21:54:42 ICT) |
| Câu trích "cạnh tranh gay gắt, quy mô một số lĩnh vực truyền thống thu hẹp" + "835,1 tỷ, +198% so 2024" | WebFetch baodauthau post192515 (19/01/2026), lời PECC1 tại tổng kết 2025 |
| KTPL 40.708.199.257 | ảnh ../../dd_TV1_20261102/img/hn_p4.png mã 323 |
| Peer TV2–TV4 (P/E, P/B, DY, ROE5Y) | BQ tav2_bq.ticker 02/11/2026 |
| Hình tái dùng nguyên trạng | fig_01, fig_04, fig_09, fig_10, fig_11 (chỉ dữ liệu BCTC/bản đồ/ảnh, không chứa định giá) |
| Lãi suất (luật 17) | dcf_rate_display.dcf_rate_lines('2026-11-02') |

md5:
```
116f25577cb5e5a757844b6ac11c6bf3  INTRINSIC_v2.md
58c7a3501965e83322c8299d912ce7b9  valuation_blind_v2.py
785bcd8c9cf47dc6709db7d065127213  valuation_blind_v2_out.txt
8fadbd4a3aada67af028c7c52da4517a  valuation_blind_v2_out.json
eb73edbb1b514143b02a10e08bee9588  investor_report/TV1_DD_investor_report_20261102.md
bf76b930d5df931ddcdcc8fe3e13a1ca  investor_report/TV1_DD_investor_report_20261102.pdf
e2fe80a7dc7c476a92f957c6e25efcf7  investor_report/TV1_DD_investor_report_20261102.html
```
Giới hạn nội bộ: người dựng đã thấy giá ở giai đoạn 2; v2 chỉ áp cơ học danh sách phản biện (INTRINSIC_v2.md đầu file). Tâm 18.100 gần giá 19.500 — ghi nhận, không hiệu chuẩn.
