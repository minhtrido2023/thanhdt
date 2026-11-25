# PVP — tài liệu ĐHĐCĐ bất thường 2026 (tàu dầu thô "Aframax") — tác động lên tâm (25/11/2026, job Taylor_20261125_080254)

**Kết luận:** **tâm base GIỮ 23.099** (vùng 13.799–30.338, nhãn, skeptic_final REFUTED_OPEN đều giữ). Lý do: NQ chưa thông qua; ĐHĐCĐ họp **30/11/2026**, đúng hạn dữ kiện, nên chưa có NQ/BB gốc. **Tâm kỳ vọng điều chỉnh E17: 22.988 → 22.838 đ/cp** (Σ p×m −1,13%), dải 22.600–23.044. Đề xuất sổ: `LEDGER_PROPOSAL_PVP.json` rev5. Mù giá: không đọc giá khi dựng.

## 0. Đính chính tiền đề dispatch
"ĐHĐCĐ ngày 23/10" thực chất là **NQ 23/NQ-TBD-HĐQT ngày 23/10**, nghị quyết gia hạn hạn họp tới ≤30/11 (dd_PVP_20261029/REPORT.md:41). Lịch họp thật nằm trong chương trình nghị sự dự thảo (`src/1-…txt`): **09h00 30/11/2026, họp trực tuyến**. Công ty đăng tài liệu ngày 09/11/2026 (trang pacificshipping.vn/co-dong/tai-lieu-dhdcd-bat-thuong-nam-2026). Thư mời `src/thu-moi…pdf` là bản scan không có lớp chữ, chưa OCR; nội dung chính không phụ thuộc file này.

## 1. Văn kiện đã đọc
Cả 7 PDF đều tải từ web công ty vào `src/`, kèm md5 và text trích bằng PyMuPDF. Tất cả đều là **DỰ THẢO**.

| Nội dung | Số liệu | Nguồn |
|---|---|---|
| Nghị sự | Có 2 tờ trình: (1) điều chỉnh danh mục đầu tư 2026; (2) chủ trương dự án **DT-08/26/TBD**. **Không có phát hành cổ phiếu hay tăng vốn.** | src/1 p1, src/5 p1 |
| Danh mục | Hai dòng "Aframax #2 56,5" và "Aframax #3 hoặc 2 MR 59,5" gộp thành **"01 đến 03 tàu (dầu thô ≤120k DWT, dầu/hoá chất ≤55k DWT)", tổng 116 tr USD, KHÔNG ĐỔI**. Lý do công ty nêu: ít chủ tàu chào bán, hoặc chào cao hơn mặt bằng; bàn giao kéo dài. Đã chào mua từ 08/2026 | src/3 p1 |
| Quyết định đầu tư | Mua 1 tàu dầu thô cũ ≤120.000 DWT, vỏ kép, đóng tại Hàn/Nhật/CSSC/COSCO, đăng kiểm IACS. Uỷ quyền HĐQT cập nhật BCNCKT nếu chỉ tiêu không thấp hơn mức duyệt | src/4 p1-3, p8 |
| Giá | TMĐT **≤80.000.000 USD**, gồm giá tàu 79.550.000 và chi phí nhận tàu 450.000. Tàu giả định **10 tuổi**, khai thác 13 năm (tới 23 tuổi) | src/4 p3, p5 |
| Nguồn vốn | VCSH + vay TCTD, **vay ≤70% giá tàu** (55,685 tr USD, lãi 6,5%, 7 năm); VCSH đối ứng 24,315 tr USD | src/4 p1, p5 |
| Tiến độ | 2026–2027 | src/4 p8 |
| Hiệu suất công ty tự tính | IRR **7,67%**; NPV dự án **33.856 USD**, tức ≈0; NPV VCSH 1.865.664 USD; ROE 11,40%; TC bình quân đời dự án 34.231 USD/ngày. Lịch TC: năm 1 71.300, năm 2 51.300, năm 3 46.300, năm 4-5 30.200, năm 6-10 28.200, năm 11-13 24.900. IRRmin = 10% + 1% = 11%. Thanh lý 17.000 LDT × 437 USD | src/4 p4-7 |
| Giá tàu thị trường (Clarksons/Allied) | Tàu 10 tuổi: 55 (2023), 52 (2024), 55 (2025), 65→80 (T4→T10/2026). Tàu 15 tuổi: 38→75 | src/4 p3 |

## 2. Tác động lên mô hình r3
Mô hình r3 không đổi: `calc/calc_afx.py` assert md5 LOCK, tái lập CONTROL từng ô (23.099), run1 = run2 md5 `1092f181…`. Theo luật 03/11, dự án mới có base NPV 0 ở nhánh cơ sở và nhánh tốt. Nhánh xấu chịu −30% × vốn mua tàu: [UL] độ lớn, dấu có cơ sở là IRR 7,67% < IRRmin 11%. **Hai điểm này giữ nguyên.** Công ty tự tính NPV dự án ≈0, nhưng đó không phải cơ sở độc lập để lệch khỏi NPV0.

Những gì văn kiện thay đổi:
1. **Pha loãng: đóng cho kỳ họp này.** Chương trình không có phát hành; vốn = VCSH + vay. Không chạm HARD ABANDON.
2. **Tổng vốn mua tàu 116 tr USD: giữ nguyên.** Nhánh "cả gói" không đổi.
3. **Nhánh "một tàu" đổi giá trị 56,5 → 80 tr USD.** Dự án Aframax #2 (56,3 tr USD, ≤15 tuổi) đã gộp vào dòng 116. Phương án một tàu nay là DT-08 (≤80, 10 tuổi). Trong mô hình, thay đổi này chỉ tác động qua nhánh xấu: **−167 đ (−0,72%)**.
4. **Kiểm chéo độ lớn −30% ở nhánh xấu.** Nếu giá tàu 10 tuổi quay về trung bình 2023–25 (54 tr USD), mức sụt so với giá mua 79,55 là **−32,1%** (calc_afx_out.json `xcheck_m30`). Kết quả này ủng hộ dấu và độ lớn đã khoá. Tham số không đổi.

| Biến thể (calc_afx_out.json) | Tâm | Δ |
|---|---|---|
| A: một tàu = 80, trọng số giữ | 22.932 | −0,72% |
| B: "không mua" 0,15→0,05 [UL] | 22.769 | −1,43% |
| C: "không mua" 0,15→0,30 [UL] | 23.249 | +0,65% |
| D: chắc chắn chỉ 1 tàu 80 | 23.054 | −0,19% |
| E: chắc chắn dùng hết 116 | 22.323 | −3,36% |
| F: NPV0 mọi nhánh | 24.678 | +6,84% |
| G: −30% vô điều kiện, một tàu 80 | 18.328 | −20,65% |

## 3. Vì sao không đổi tâm base
Dữ kiện mới là **dự thảo**, chưa được biểu quyết. Biến thể A chỉ đổi 0,72%, nhỏ hơn mọi bất định đang mở. Vì vậy mục này đi vào **E17** dưới dạng hạng mục bậc A (văn bản CBTT của công ty):
- p 0,90 [0,75; 1,00] theo thang PREREG §2. Thang không cho phép hạ p vì rủi ro biểu quyết; điểm này ghi rõ trong `adj.json`.
- m = −0,72%, khoảng [−0,72; 0]. 80 là mức trần; mua ở giá ≤56,5 thì m = 0.

`adj.json` kế thừa adj đợt 2 (assert md5): hạng mục lên đà C+ −0,48 cộng hạng mục mới −0,648, **Σ −1,128% ⇒ 22.838 (22.600–23.044)**. `calc_adj_afx.py` cho run1 = run2.

## 4. Điều kiện đổi số
| Dữ kiện | Khi | Đổi gì |
|---|---|---|
| **NQ + BB ĐHĐCĐ bất thường thông qua nguyên dự thảo** | 30/11–02/12/2026 | Đưa A vào base thành **rev mới: tâm 22.932 (−0,72%), vùng 13.363–30.338**. E17 bỏ hạng mục này, chỉ còn lên đà ⇒ ≈22.822 (ước lượng, chưa chạy) |
| NQ **không thông qua** dự án DT-08 | như trên | Nhánh một tàu quay về giá trị cũ/0. Xem biến thể C (+0,65%) và đọc lại câu chữ NQ |
| Có biểu quyết phát hành phát sinh tại đại hội | như trên | Pha loãng; dưới book = HARD ABANDON |
| CBTT ký hợp đồng mua tàu (giá, tuổi thực) | 2026–2027 | Thay 80 bằng giá thật; tuổi >10 ⇒ xem lại lên đà SS#2 1,55 tr USD (src/4 p7) |
| Giá tàu 10 tuổi quay đầu | theo dõi | Hỗ trợ nhánh xấu; tham số khoá không đổi |

## 5. Phụ phẩm (chưa áp)
Tờ trình 4 cho **giá thanh lý 437 USD/LDT** (giả định của công ty). Hạng mục "phế liệu đội tàu hiện hữu" (C, chiều lên) mới có giá/LDT. Vẫn thiếu LDT từng tàu Apollo/Era/Pride, nên chưa nâng bậc.

## 6. Việc mở / ranh giới
- Chưa chạy fundamental-skeptic lại: tâm base giữ, E17 chỉ dịch −0,65%. Mike quyết có cần không.
- Không ghi sổ master, không merge, không email, không wire. Selfcheck sổ tạm (176 entry) cho 0 lỗi ở Asia/Ho_Chi_Minh, UTC, America/New_York và `env -u TZ`, với `MIKE_SRC_ROOT=<worktree>` vì adj.json chưa có trên master. Đối chứng: sổ gốc 175 entry, 0 lỗi (`selfcheck_ledger_tmp.txt`).
- Khi Mike ghi rev5 lên master: adj.json phải có ở master cùng md5 `c062c5eb…`. Nếu không, selfcheck master FAIL (`center_adj_basis` không đọc được).
