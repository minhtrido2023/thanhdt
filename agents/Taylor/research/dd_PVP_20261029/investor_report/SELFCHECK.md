# Tự kiểm — PVP_DD_investor_report_20261029 (job Taylor_20261029_074021, 29/10/2026)

(i) Số liệu: 82 cặp số trọng yếu (tiền ròng, capex, P/E, P/B, tăng trưởng cùng cơ sở, FSO PV + độ nhạy 8/10/12%, SOTP/PP-A/PB, sàn dải,
định giá ngược, kịch bản mua, trọng số) đối chiếu tự động .md ↔ ../out.txt: 81 có trong .md và khớp; "−2,5%" (Q3 YoY LNST) chỉ nằm ở tiêu đề hình 3, khớp out.txt.
Số tính mới trong phiên (không có trong out.txt), đã tính lại bằng python: −6,9% (18.750/20.150); tiền ròng/vốn hoá 52%; định giá ngược tại 20.150
= ~754 / ~957 tỷ; biên gộp Q3 11,2%, 9T 16,4% (Phụ lục B); 21/10 −7,0%, 25/09 +6,8% (price_raw.csv).
(ii) 7 sửa nhỏ phản biện vòng 2 — áp vào REPORT.md (v2.1, dòng §14) + calc.py (thêm fso_pv_at(), sàn dải, phải trả cổ tức) ⇒ out.txt 0 FAIL / 29 self-check;
và vào báo cáo nhà đầu tư: (a) trigger PB≲0,75 chỉ kèm (a)/(b); "giá ≤13.200" ⇒ xem lại định giá ngoài §2.5, không gán AMBIGUOUS — grep "13.200": 3 hit, không hit nào gán nhãn;
(b) sàn dải 13,6–14,9k / 4,7–6,1k; (c) VAT chỉ xuất hiện dưới dạng "không áp dụng" (§3) + Phụ lục E; (d) NPV CSH +2.237.928 USD, IRRmin 10%+1%, IRR 7,67% cấp dự án;
(e) LCTT 03 chung, gán sửa chữa = suy luận; (f) "đã chi 20/10" grep 0 hit, ghi "lịch thanh toán 20/10 theo NQ 17, chưa có chứng từ", 109,5 gồm ~5,8 tồn cũ; (g) FSO PV 792,5/760,7/731,8.
(iii) grep -i "SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|Winston|Mafee|DollarBill|LAG|sizing|vị thế" trên .md + figs/*.csv: 0 hit
("giá vốn" chỉ nghĩa COGS; "NAVY" là tên màu trong build_report.py). Không có mục sizing/NAV, số lượng vị thế, giá vốn mua, %NAV, tên tài khoản. Không nhắc luật nội bộ.
(iv) Không có nhãn mua/bán cá nhân hoá; chỉ NON + điều kiện chạy lại §2.5. Biến động giá 21/10, 29/10 ghi "quan sát", không gán nhân quả.
Giá: DNSE latest_trade PVP 18.750 (sàn) 14:29:47 ICT, KL 294.240 (G1); secdef marketId=STO (HOSE), tham chiếu 20.150 = đóng cửa BQ 28/10. PVT 21.300 = sàn (DNSE 14:29:59).
Render: HTML qua mike/bin/render_report_html.py (10 ảnh nhúng, 0 "Ảnh thiếu"); PDF 14 trang A4 pymupdf.Story, kiểm bằng mắt trang 1 + trang 11 + toàn bộ ở độ phân giải thấp
(dấu tiếng Việt OK, bảng không tràn). Lưu ý: tiêu đề Phụ lục B nằm cuối trang 12, bảng sang trang 13.
Giới hạn tự kiểm: chưa đọc lại trang scan BCTC trong phiên này (số nền lấy từ calc.py đã qua 2 vòng phản biện).
