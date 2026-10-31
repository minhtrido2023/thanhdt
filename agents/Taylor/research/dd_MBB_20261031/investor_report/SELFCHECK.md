# SELFCHECK — MBB_DD_investor_report_20261031 (job Taylor_20261031_150718)

Tái lập: `bash scripts/make_maps.sh` → `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` (figs + PDF);
banner: `make_title_banner.py --title "<dòng 1 md>" --ticker MBB --kicker "Báo cáo due diligence · HOSE: MBB" --sub "Nhóm nghiên cứu · 31/10/2026" --logo ../src/logo.png --out figs/title_banner.png`;
HTML: `python3 -I ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py <md> --pdf <pdf> --banner figs/title_banner.png --dry-run --html-out <html>` (DRY-RUN, không gửi).

| Kiểm | Kết quả |
|---|---|
| Nguồn số | ../REPORT.md **v2** (áp 9 đính chính phản biện) + ../calc/mbb_calc_out.txt (chạy lại `python3 -I calc/mbb_calc.py`) |
| Đính chính phản biện không tái xuất | MBV không hợp nhất (mục 6, WARNING ngoài bảng); không còn "vốn 3.500 hợp nhất", "trích thiếu", "11,18% lãi biên", "sớm/nhanh hơn ngành", TCB 0,78x; NIM 2 cách đo; Tier1 = theo dõi |
| PDF | 12 trang A4 (thân tr.1–10, phụ lục tr.11–12); xem bằng mắt tr.1–12: dấu tiếng Việt đúng, bảng không tràn |
| Số từ thân | 1.005 từ (không tính bảng/hình/phụ lục) — trần ~1.800 |
| Hình | 15 hình + 2 bản đồ khu vực + banner; mỗi hình có CSV trong figs/ (bản đồ: CSV điểm ở scripts/pts_*.csv) |
| Luật 9 tiêu đề | Câu tóm ý hai vế (tốt: LN thật, giá nửa dưới vùng · rủi ro: nhóm 2 +42%, MBV) |
| Luật 10/15 | Hero (ảnh hội sở BCTN + KPI + thanh định giá); chuỗi giá trị ngân hàng; khung 4 ảnh/logo sản phẩm–hệ sinh thái trích BCTN 2025; 2 bản đồ KHU VỰC (Bắc, Nam), không toàn quốc; mạng lưới theo vùng (BCTN) |
| Luật 13 | Be Vietnam Pro; logo trích trang bìa BCTN 2025 PDF (không đụng mbbank.com.vn) |
| grep nội bộ (SpaceX/ZaloPay/giá vốn/NAV/tên agent) | rỗng |
| grep nhãn (QUALIFY/NON/§2.5/fear/kiểm định/xung đột lợi ích) | rỗng |
| HTML | 17 `<img>`, alt đóng đúng (0 lỗi) |
| Giá | đóng cửa 30/10/2026 = 19.300 đ (BQ; thị trường nghỉ thứ Bảy 31/10). DNSE latest_trade không gọi được trong phiên headless (client cần API key) — không ảnh hưởng vì không có phiên mới |
| Sàn | HOSE (theo CBTT; không kiểm DNSE secdef `marketId` — cùng lý do) |

Giới hạn còn lại (đã ghi Phụ lục D): CASA chuẩn MB Q3, CAR 30/09, LDR TT22/TT50, ngoại bảng/cơ cấu, tập trung KH, số MBV 2025–26 — chưa kiểm.
Không gửi email (Mike gửi). Subject dry-run = tiêu đề md.
