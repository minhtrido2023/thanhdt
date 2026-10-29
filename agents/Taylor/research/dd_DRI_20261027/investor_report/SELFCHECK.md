# Tự kiểm — DRI_DD_investor_report_20261029 (job Taylor_20261029_093106, 29/10/2026)

md5: .md `1217970722fe51707aefbb52b382e2b4` · .pdf `ce087678d6e411fd86cf9cf5ceaafc5e` (17 trang A4).

(i) **Số khớp nguồn đã phản biện.** 117 số trọng yếu (FV r4 POST-HOC 3 đường × 4 mid, lưới 27 ô, trục tái canh T1/T2b/T2c + số phản biện 13.225/15.115,
phase 2, NPV tái canh, diện tích/sản lượng BCTN, luồng tấn Q3, tồn kho, CFO, tiền tại Lào, Dakruco, Quỹ TDND, ngành, phân rã sai số Q3)
grep -F tự động trong REPORT.md, REPORT_Q3_UPDATE.md, extract_q3_bctc.md, r4 REPORT.md/out.txt, dri-triggers, đọc ngành: 115 thấy nguyên văn;
2 là phép cộng/làm tròn từ số trong extract: 11,07 (= 11.073.900.741) và 42,07 (= 30,55 + 11,51).
Số tính mới trong phiên (python, ghi trong build_report.py/figs CSV): BVPS 9.971; P/E TTM 5,09/5,16; P/B 1,45/1,47; vốn hoá 1.061,4/1.076,0; EV 898,6/913,2;
EV/LNST TTM 4,31/4,38; tiền ròng 236,74 → 162,82 (2.224 đ/cp); DY 6,9/6,8%; premium vs đường TB +80/+60/+44/+30% (14.500), +82/+62/+46/+32% (14.700);
mid ngầm định 2,529/2,549 (ngoại suy tuyến tính đường TB — ghi "ước lượng"); 9T DT +27,6%, LNST mẹ +43,6%; Q3 −26,1%/−33,3%; biên gộp Q3 34,2%, Q3/25 35,5%,
9T 39,3%/37,9%; ADV 63 phiên tới 28/10 16,85 tỷ; 12T Close 10.910–16.900; P/B nhóm × BVPS 8.874–18.845 (trung vị 13.909).
FV chính = r4 POST-HOC (đã qua phản biện vòng 4, CONFIRMED medium). KHÔNG dùng 11.838/11.031/14.301/12–14k làm FV chính (chỉ nhắc ở mục 5e/Phụ lục E như lịch sử).

(ii) **Đính chính đã áp:** H1 dùng bản soát xét (−4,50 tỷ); bỏ "tái canh gần hoà vốn" (ghi rõ làm giảm giá trị ~4,0k); có trục thực hiện/hoãn/cắt tái canh; đơn giá
KTCB 24,655 tr/ha đối chiếu BCTN 2024; HOSE Q4/2026 theo SXKD 9T (ghi là kế hoạch, chưa phải sự kiện); dự báo Q3 trượt + F không chấm mù nêu ở 5e và Phụ lục E;
phần POST-HOC ngoài kế hoạch đăng ký trước và các giả định [UL] nêu ở mục 7.

(iii) **Grep nội bộ** `SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros|Winston|Mafee|DollarBill|LAG|sizing|vị thế|tranche|13.000|15.100|G0–G7|§2.5|sleeve|PREREG|dispatch`
trên .md + figs/*.csv: 0 hit. "giá vốn" 7 hit, đều nghĩa COGS. Không có số lượng vị thế, giá vốn mua, %NAV, tên tài khoản, lệnh bán tay, trigger giảm/thoát/mua lại,
cổng mua thăm dò. Ngưỡng theo dõi chỉ ở dạng chung (SXKD T10, TSR20/Qingdao/lốp, Dakruco, Quỹ TDND, Lào, HOSE), không gắn lệnh. Câu xung đột lợi ích dùng đúng câu chung
của skill — **user quyết giữ/bỏ**.

(iv) **Nhãn:** chỉ NON; vùng giá thấp = "cần chạy lại kiểm định, tối đa AMBIGUOUS" (sàn tài sản thực không đạt). Giá 21/10, 26–27/10 ghi "quan sát", không gán nhân quả.

(v) **Giá:** DNSE latest_trade DRI G1 14.700, 14:59:46 ICT 29/10 (sau đóng cửa; KL 129.490 lô ×10 = 1.294.900 cp, khớp BQ); secdef marketId=UPX ⇒ UPCoM; basicPrice 14.400 =
bình quân phiên 28/10 (UPCoM), khác đóng cửa 28/10 = 14.500 [BQ]. Kết luận NON không đổi ở cả 14.500 và 14.700.

(vi) **Render:** HTML qua mike/bin/render_report_html.py (10 ảnh nhúng, 0 "Ảnh thiếu"); PDF pymupdf.Story 17 trang. Kiểm bằng mắt: trang 1 (tear sheet + football field)
và trang 11 (định giá) ở 100 dpi, toàn bộ 17 trang ở 38 dpi — dấu tiếng Việt OK, bảng không tràn. Lưu ý: trang 2 và trang 5 còn ~nửa trang trống (ngắt trang trước mục 1
và sau hình 7); ma trận rủi ro (trang 13) bị co nhỏ để vừa trang.

**Giới hạn tự kiểm:** không đọc lại trang scan BCTC trong phiên này (số nền từ extract_q3_bctc.md + r4 đã qua phản biện); số đuôi trên 13.225/15.115 là số của người phản biện,
mô hình r4 không tái lập đúng (dải T2b–T2a); kịch bản FY26E 181/217/257 lấy từ model_q3 (trước r4), chỉ dùng cho LN năm 2026, không cho định giá.
