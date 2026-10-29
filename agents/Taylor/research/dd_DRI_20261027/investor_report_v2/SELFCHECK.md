# Tự kiểm — DRI_DD_investor_report_20261029_v2 (job Taylor_20261029_104401, 29/10/2026)

md5: .md `8672fd124721f3e5d11b35dbc3671c2e` · .pdf `677a8e0f98dc526a6aec228cf72723c4` (20 trang A4). HTML: 21 ảnh nhúng, 0 "Ảnh thiếu".
Nền: bản v1 `../investor_report/` (md5 .md 1217970722fe…). Mục 5–10 + Phụ lục A–F chép nguyên từ v1, chỉ thêm tham chiếu hình và 3 dòng Giới hạn + 1 dòng Phụ lục E.

(i) **Số khớp v1/nguồn.** Lấy mọi chuỗi số trong .md v2 (454 chuỗi), so với .md v1: 14 chuỗi mới. 12 có nguyên văn trong BCTN 2024/2025
(text trích từ `../../dri_val_supply_adj_r4_20261027/src/BCTN202{4,5}.pdf`): 3,33 (tỷ USD XK cao su VN 2025), 9.276,07 ha, 6.148,03 ha FSC, 83,87% CNC DRI,
500 tỷ vốn ban đầu, 2012, 2021, 1,7→2,2 t/giờ, 3,61… ; 2 chuỗi là tính/làm tròn: 9.279,68 (= 8.592,3+465,67+30,48+191,23, lệch 3,61 ha so với tổng BCTN — ghi
Giới hạn) và 93,6% (= 93,58% BCTN). Không có số định giá mới: FV/khoảng tin/đuôi trên/lưới/đường sản lượng y nguyên v1 (r4 POST-HOC + số phản biện).
Hình mới: CSV đi kèm, số lấy từ hằng số v1 (`FV_TB`, `CI_*`, `NOREPLANT`, `PEERS`, đường TB fig_07), BCTN (diện tích, cơ cấu DT, cổ đông, năng suất 2023–25, lịch sử),
BQ `fin_quarterly_bq.csv` (DT/LNST năm 2022–25) và `data/rubber_monthly.csv` (RSS3; kiểm lại trung vị 10 năm 1,865 / 5 năm 2,075 / BQ 2025 2,183 — khớp v1).

(ii) **Mô tả đã chính xác hoá so với v1** (không đổi số/kết luận): vườn cây ở 2 tỉnh Champasak **và Salavan** (BCTN 2024/2025; v1 chỉ nêu Champasak) — ghi ở Phụ lục E.
Ngày thoả thuận dự án 19/11/2004 KHÔNG có trong text BCTN; nguồn là thuyết minh BCTC như trích ở hồ sơ DD (CYCLE_BLOCK [BCTC 5.17]) — ghi rõ ở chú thích hình + Giới hạn.
"Top 50 xuất khẩu" chỉ nói tới 2021 (BCTN: "3 năm liên tục"), không suy rộng.

(iii) **Grep nội bộ** `SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|Winston|Mafee|DollarBill|LAG|sizing|vị thế|tranche|§2.5|sleeve|PREREG|dispatch`
trên .md + EMAIL_SUBJECT.txt: 0 hit. "giá vốn" chỉ nghĩa COGS. Xung đột lợi ích = câu chung của skill (user quyết giữ/bỏ).

(iv) **Luật 9:** tiêu đề giữ nguyên câu user đã khen. **Gợi ý subject email** ở `EMAIL_SUBJECT.txt` (KHÔNG đặt trong .md: send_dd_report_email.py render .md thành
thân email và comment `<!-- -->` hiện ra thành chữ — đã thử, đã gỡ).

(v) **Luật 10 + render bằng mắt:** trang 1 = tiêu đề + hero (ngành/tăng trưởng/định giá) + tear sheet + 3 luận điểm; trang 5–7 = giới thiệu doanh nghiệp kiểu BCTN
(lịch sử, chuỗi giá trị, địa bàn + sử dụng đất, cơ cấu DT, vòng đời vườn); trang 12 = định giá (football field + bảng). Mỗi mục lớn ≥1 hình (21 hình: 10 cũ + 11 mới).
Lỗi thẩm mỹ v1 đã sửa: không còn trang trống nửa (ngắt trước 1/3/4/7/8/Phụ lục A, mục 5 nối tiếp mục 4); ma trận rủi ro đặt đầu mục 8, không bị co.
Còn: trang 1 và 5 trống ~15–20% đáy (hình kế không vừa); hình xúc tác mục 10 co ~0,8 ở cuối trang 15; trang 20 (Phụ lục F) ngắn.

(vi) **Giá:** như v1 — DNSE latest_trade 14.700 (29/10 14:59:46 ICT), neo đóng cửa 28/10 14.500; NON không đổi ở cả hai mức. Không gọi lại DNSE trong phiên này.

Giới hạn tự kiểm: không đọc lại scan BCTC; sơ đồ địa bàn cách điệu (không có bản đồ ranh giới); hình hero/vòng đời là infographic, số trên hình đều có CSV.
Tái lập: `/home/trido/thanhdt/wc_venv/bin/python -I build_report.py all` rồi `python3 mike/bin/render_report_html.py <md> --out <html>`.
