# GAPS — DD FPT 01/11/2026 (v1 job Taylor_20261101_042936; cập nhật v2 job Taylor_20261101_101423)

**Đã có (nguồn gốc):** BCTC hợp nhất Q3/2026 (fpt.com `/api/media/20261028_FPT_BCTC_hop_nhat_Quy_3_nam_2026_5cc2369cdd.pdf`, 54 trang scan; Mike nói IR chưa có, thực ra đã đăng ở mục "Thông tin công bố") · BCTC riêng Q3 (đã tải, CHƯA đọc) · BCTC hợp nhất Q2/2026 · soát xét bán niên 2026 (chỉ đọc 12 trang đầu) · thông cáo 6T và 9T · BCTN 2025 · CBTT phạt thuế, cổ phiếu thưởng, ESOP, cổ tức. Tất cả nằm ở `src/`.

| # | Thiếu | Ảnh hưởng | Cách lấp |
|---|---|---|---|
| G1 | Định nghĩa "doanh thu ký mới" (TCV hay ACV, có gồm gia hạn không), backlog, thời hạn hợp đồng bình quân, utilization | Không so được với peer; không tính được tỷ lệ chuyển backlog thành doanh thu 12 tháng | Hỏi IR / tài liệu analyst meeting của FPT; BCTN không định nghĩa |
| G2 | Bản chất khoản "chi phí phát triển khách hàng" 618.772.175.000 đ [Q3HN p37], trùng đúng khoản vay 17,5 triệu GBP [p42] | Có thể là trả trước cho một khách hàng hoặc thương vụ ở Anh; góp vào CFO yếu | Hỏi IR; đọc BCTC riêng Q3 và BC quản trị |
| G3 | Học phí nhận trước tại 30/9/2025, số sinh viên nhập học 2026, tỷ lệ lấp đầy chỉ tiêu | Không có chỉ báo tuyển sinh sớm của khối giáo dục | BCTC Q3/2025 hợp nhất (cột 30/9/2025 không in lại trong Q3/2026); thông cáo tuyển sinh ĐH FPT |
| G4 | Lãi liên kết theo từng công ty (FTEL, FRT, Synnex, FPT Online); giá trị ghi sổ từng khoản | Phần FTEL hiện là ước lượng từ BQ (45,66% × LNST FOX); "liên kết khác 1.500 tỷ" là ước lượng | BCTC Q3 của FOX và FRT; BCTC năm 2026 FPT |
| G5 | TTDL: MW đã xây / đã bán / đang dùng, capex TTDL, giá điện | Không trả lời được câu hỏi (3) phần TTDL | BCTC và BCTN của FOX (FTEL) |
| G6 | ~~Tỷ lệ sở hữu nước ngoài~~ ĐÃ LẤP v2: 28,74% (18/05/2026), 28,60% sau ESOP [esopnq_p04]; số sau 18/05 vẫn chưa có | Thiếu dữ kiện dòng vốn ngoại | HOSE / VSDC; DNSE secdef không có trường này |
| G7 | Báo cáo quản trị 6T/2026 (89 trang scan) — giao dịch bên liên quan ngoài tập đoàn, thù lao HĐQT | Bài học từ skeptic TCH: bỏ sót BC quản trị bị REFUTED | `src/20260730_FPT_Bao_cao_tinh_hinh_quan_tri...pdf` đã tải, chưa đọc |
| G8 | PE / EV/EBIT của peer IT services khu vực (Infosys, TCS, HCLTech, Cognizant, EPAM) đo trong phiên | Comp hiện chỉ dùng VN (CMG, ELC, FOX) và lịch sử FPT | Nguồn giá peer có ngày; không dùng số nhớ |
| G9 | Phải thu khu vực công theo tuổi nợ | Thuyết minh không có bảng tuổi nợ | Hỏi IR / BCTC năm |
| G10 | Q4/2025 core theo phạm vi mới (lãi liên kết Q4/25 đã điều chỉnh) | LN lõi TTM 7.466 / 6.705 là ước lượng (giả định lãi liên kết Q4/25 khoảng 600 tỷ) | Thông cáo KQKD 2026 sẽ in số so sánh Q4/25 đã điều chỉnh |
| G11 | Thuế suất hiệu dụng tăng (11,1% → 15,2% trên LNTT trừ liên kết): do thuế tối thiểu toàn cầu hay hết ưu đãi | Ảnh hưởng tăng trưởng LNST lõi các năm sau | Thuyết minh thuế BCTC năm; BCTC riêng |
| G12 | Số nhân sự CNTT tại 30/9/2025 | Không tính được doanh thu/kỹ sư cùng kỳ | Thông cáo KQKD 9T/2025 |

**Không làm theo brief:** không có (BCTC Q3 gốc đã tìm được). Báo cáo nhà đầu tư và email: Mike làm.

## Bổ sung v2 (01/11, sau phản biện)
| # | Thiếu | Ảnh hưởng | Cách lấp |
|---|---|---|---|
| G13 | LCTT gốc 2021–2023 (mã 05, 06, 14, 21) | Chuỗi conv thống nhất chỉ đo được 2024, 2025, 9T/25, 9T/26; 2021–23 chỉ có định nghĩa cũ 14/10 | Tải BCTN 2022, 2023 từ fpt.com |
| G14 | Thị giá TPBank/FPTS phần FPT nắm; lãi liên kết khác chính xác (FRT Q3/26 chưa vào BQ) | Khoảng bất định SOTP −1,3k…+2,4k đ/cp chưa thu hẹp được | BCTC Q3 FRT; giá TPB/FPTS ngày định giá |
| G15 | Vay ngoại tệ 30/9 trùng từng đồng với 30/6 (chưa đánh giá lại tỷ giá?) | Nhỏ với tiền ròng; liên quan cách đọc khoản 618,8 tỷ | Hỏi IR; đối chiếu BCTC năm 2026 |
| G16 | Render lại slide KQKD9T cho JPY/USD theo quý, học phí 30/6 (tm21 Q2) | Số T8 và 966 hiện lấy theo phản biện | Render `src/FPT_BC_KQKD_9_M2026*.pdf`, `20260727_FPT_BCTC_hop_nhat_Quy_2*.pdf` |
| G7 | BC quản trị 6T/2026 | **Vẫn chưa đọc** ở v2 (ngoài ngân sách) | như trên |
