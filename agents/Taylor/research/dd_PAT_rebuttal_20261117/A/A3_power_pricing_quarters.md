# A3 — Giá điện, truyền dẫn chi phí, quan hệ PAT–mẹ, thay thế P4, đường phục hồi theo quý (PAT, mù giá)

Ngày truy cập tất cả nguồn web: 2026-11-17. Nhãn: [DN] công bố doanh nghiệp · [NN] cơ quan nhà nước/văn bản pháp luật (kể cả bản chép) · [BC-tên] báo chí · [DL] nhà cung cấp dữ liệu hàng hoá · [TT] tự tính (công thức ghi kèm). Đơn vị: tỷ đồng trừ khi ghi khác. Số BCTC PAT lấy từ ảnh trong `blind_val_20261114/inputs/src/` (png_q326 = Q3/2026; png_bn26 = soát xét bán niên 2026; png_kt25 = kiểm toán 2025) và `factpack/` F2/F4 (đã đối chiếu lại các bảng chính với ảnh png_q326/p32, png_bn26/p34-p35 và với F3). Tệp tính: `A/A3_calc_electricity.py`.

## 0. PHÁN QUYẾT TÓM TẮT (chi tiết + bằng chứng hai chiều ở mục 5)

| Khẳng định (phần A3) | Phán quyết |
|---|---|
| #2a "Giá điện vừa giảm 2%" | **ĐÚNG ở mức giá bán lẻ BÌNH QUÂN** (từ 01/11/2026); **MỘT PHẦN** với nhóm sản xuất (cắt thực tế theo biểu giá ≈ 1,3–3,3%, EVN-phân bổ ngụ ý ≈ 1,5–1,7%, tuỳ cấp điện áp) |
| #2a "dù không bền" | **KHÔNG KIỂM ĐƯỢC** (báo: chủ trương giảm "đến hết 31/3/2027"; QĐ 2892 không ghi ngày hết hiệu lực; không có văn bản nào nói giá sau 31/3/2027) |
| #2a độ lớn tác động lên giá thành PAT | Rất nhỏ theo cơ học: trần trên ≈ 0,6% tổng chi phí theo yếu tố; ≈ 5–16 tỷ/năm trước thuế (≈ 2–5% LNST kế hoạch 2026) |
| #2b "PAT bán lại chủ yếu cho mẹ" | **MỘT PHẦN**: ĐÚNG cho 9T/2026 (63,7% DT; Q3 85,5%), **SAI** cho 2024–2025 (18,2% / 8,5%). Quan hệ mua–bán chéo hai chiều với DLC; giá chuyển nhượng KHÔNG TÌM ĐƯỢC |
| #2c "xuất khẩu P4 là chính" | **MỘT PHẦN**: đúng với PAT 2024–2025 (~90% DT) và DGC (Nhật/Hàn/Ấn); **SAI với PAT 9T/2026** (xuất khẩu 35,3% DT; Q3 ≈ 13,5%) |
| #2c "vị thế thứ ba thế giới" | **KHÔNG KIỂM ĐƯỢC** (nguồn báo nêu "lớn nhất VN / ~1/3 xuất khẩu toàn cầu" không dẫn gốc; không tìm được xếp hạng độc lập) |
| #2c "power thương lượng giá tốt hơn" | **KHÔNG KIỂM ĐƯỢC / MỘT PHẦN**: đã thấy phần tăng giá thị trường về tới DGC một nửa (Q2) và về tới PAT trong Q2 nhưng KHÔNG về trong Q1, Q3 |
| #2d "chi phí tăng có thể chuyển cho khách trừ khi có thay thế" | **MỘT PHẦN** (truyền dẫn không đều theo quý; bằng chứng thay thế: không có thay thế diện rộng, có thay thế biên ở axit tinh khiết cho LFP) |
| #1 (phần quý) "tệ nhất Q2–Q3/2026, sau đó tốt dần" | **SAI cho PAT** (Q2 là quý tốt nhất 2026, Q1 thấp nhất); **MỘT PHẦN cho DGC hợp nhất** (Q2 yếu nhất về YoY/biên, Q3 LNST cao hơn Q2); "tốt dần" **KHÔNG KIỂM ĐƯỢC** (không có phát biểu DN về Q4/2026–2027; số học kế hoạch ngụ ý Q4 ≈ Q3 với PAT, thấp hơn Q3 nhiều với DGC) |

---

## 1. GIÁ ĐIỆN 2026 (khẳng định #2a)

### 1.1 Quyết định điều chỉnh — có thật, ngày nào, áp cho ai
- [DN-EVN] EVN QĐ **1305/QĐ-EVN ngày 30/10/2026**: giá bán lẻ điện bình quân còn **2.159,9037 đ/kWh (chưa VAT), giảm 2%**, hiệu lực **01/11/2026**. Nguồn: https://www.vietnamplus.vn/evn-dieu-chinh-gia-dien-giam-2-con-21599-dongkwh-tu-ngay-mai-111-post1145418.vnp ; https://giaoduc.net.vn/evn-thong-tin-ve-viec-thuc-hien-chinh-sach-gia-dien-tu-ngay-1112026-post263825.gd (EVN, 05/11/2026) ; https://tapchicongthuong.vn/gia-ban-le-dien-binh-quan-giam-2--tu-ngay-1-11-2026-562569.htm. Chưa mở được văn bản QĐ 1305 gốc (chỉ báo).
- [NN] Bộ Công Thương **QĐ 2892/QĐ-BCT ngày 31/10/2026**: quy định giá bán điện theo nhóm khách hàng; Điều 3 "Thời gian áp dụng giá bán điện: từ ngày 01 tháng 11 năm 2026"; ngày hết hiệu lực "đang cập nhật" (không ghi ngày hết hạn). Nguồn: bản chép https://luatvietnam.vn/dien-luc/quyet-dinh-2892-qd-bct-2026-quy-dinh-gia-ban-dien-453837-d1.html (toàn văn PDF cần đăng nhập). Căn cứ nêu: Luật Điện lực 2024, NĐ 72/2025/NĐ-CP (sửa bởi NĐ 278/2026/NĐ-CP), QĐ 14/2025/QĐ-TTg, TT 60/2025/TT-BCT.
- [NN] Thông báo **557/TB-VPCP ngày 27/10/2026** (kết luận Phó Thủ tướng Nguyễn Văn Thắng về kịch bản điều hành xăng dầu, điện) — đã tải về `A/raw/tb557.pdf` nhưng PDF dùng font mã hoá riêng, KHÔNG trích được chữ (đã thử giải mã ToUnicode: chỉ ra các từ rời rạc "kịch bản điều hành xăng dầu điện"). Nội dung "giảm ~2% đến hết 31/3/2027" chỉ lấy qua báo: [BC-Người Quan Sát 31/10/2026] "hướng tới giảm giá bán lẻ điện khoảng 2% trong thời gian từ nay đến hết ngày 31/3/2027", điều kiện duy nhất nêu là EVN "khẩn trương rà soát, tiết giảm tối đa chi phí" (https://nguoiquansat.vn/pho-thu-tuong-giam-2-gia-dien-ban-le-325337.html).
- Áp nhóm nào: [BC-VietnamPlus 31/10/2026, trích EVN] giảm "cho toàn bộ khách hàng sử dụng điện với mức giảm 2%" (mức BÌNH QUÂN). Cùng đợt cấu trúc lại biểu giá: nhóm sản xuất gộp còn 3 cấp điện áp + cấp mới ≥220 kV; khung giờ mới theo QĐ 963/QĐ-BCT (22/04/2026). Giá sinh hoạt: bậc cao nhất tăng 3.460→3.844 đ/kWh (SGGP) — tức "−2%" là bình quân, không phải mọi bậc/nhóm đều giảm 2%.
- Phân bổ giảm theo nhóm (EVN, qua Báo Lào Cai 04/11/2026, https://baolaocai.vn/gia-dien-giam-2-evn-du-kien-giam-thu-gan-1600-ty-dong-moi-thang-post913548.html): tổng giảm thu "gần 1.600 tỷ/tháng"; sản xuất **578,1 tỷ** (51,8% sản lượng), sinh hoạt 424,1 (29,9%), kinh doanh dịch vụ ~433 (6,17%), bán buôn 49,54 (8,18%), hành chính 47,04 (3,8%).
- Điều chỉnh trước đó: [NN] QĐ 1279/QĐ-BCT ngày 09/05/2025, hiệu lực 10/05/2025, bình quân 2.204,0655 đ/kWh (+4,8% so 2.103,11) (https://luatvietnam.vn/tin-van-ban-moi/tang-gia-dien-len-22047-dong-kwh-tu-ngay-10-5-2025-186-102059-article.html qua tìm kiếm; hcc.nghean.gov.vn). [TT] 2.159,9037/2.204,0655 = 0,97996 (−2,0%) ⇒ giữa 10/05/2025 và 31/10/2026 giá bình quân không đổi; một nguồn khác cho mức giảm "~44 đồng" (Nhân Dân/tìm kiếm) khớp 2.204,07×2% = 44,08.

### 1.2 Biểu giá điện sản xuất (đ/kWh, chưa VAT)
Mới từ 01/11/2026 (QĐ 2892, luatvietnam; trùng SGGP https://www.sggp.org.vn/chi-tiet-gia-ban-le-dien-ap-dung-tu-ngay-1-11-2026-post880092.html): bình thường / thấp điểm / cao điểm
- ≥220 kV: 1.771 / 1.101 / 3.110 · >35–<220 kV: 1.792 / 1.123 / 3.218 · >1–35 kV: 1.814 / 1.166 / 3.348 · ≤1 kV: 1.966 / 1.274 / 3.586.
Cũ (QĐ 1279, hiệu lực 10/05/2025; nguồn Tiền Phong https://tienphong.vn/re-hon-nhieu-gia-dien-kinh-doanh-khach-hang-nao-duoc-ap-gia-dien-san-xuat-post1842772.tpo — trang hiển thị dấu ngày 12/05/2026 (lạ), giá trùng giá 1.811 của luatvietnam/thuvienphapluat; chưa đối chiếu phụ lục gốc 1279): 110 kV+: 1.811 / 1.146 / 3.266 · 22–<110 kV: 1.833 / 1.190 / 3.398 · 6–<22 kV: 1.899 / 1.234 / 3.508 · <6 kV: 1.987 / 1.300 / 3.640.
Khung giờ: cũ (TT 16/2014) cao điểm 9h30–11h30 + 17h–20h T2–T7 (5 h/ngày), thấp điểm 22h–4h (6 h); mới (QĐ 963/QĐ-BCT 22/04/2026) cao điểm 17h30–22h30 T2–T7 (5 h), thấp điểm 0h–6h hằng ngày (6 h) [BC-Tuổi Trẻ 25/04/2026, SGGP; trích qua tìm kiếm]. Số giờ mỗi loại KHÔNG đổi ⇒ phụ tải phẳng 24/7 (lò điện P4 chạy liên tục — nhận định, chưa có nguồn riêng cho PAT) có trọng số 57,14% bình thường / 25% thấp điểm / 17,86% cao điểm trước và sau.

### 1.3 [TT] Giá bình quân gia quyền cho phụ tải phẳng và thay đổi theo cấp điện áp
Công thức: P = (96/168)·P_bt + (42/168)·P_thấp + (30/168)·P_cao (96/42/30 = giờ/tuần bình thường/thấp điểm/cao điểm).
| Cũ → Mới (ghép gần nhất theo cấp) | P cũ | P mới | Δ% | Δ% chỉ giờ bình thường |
|---|---|---|---|---|
| 110 kV+ → ≥220 kV | 1.904,6 | 1.842,6 | −3,25% | −2,21% |
| 110 kV+ → 35–220 kV | 1.904,6 | 1.879,4 | −1,32% | −1,05% |
| 22–110 kV → 35–220 kV | 1.951,7 | 1.879,4 | −3,71% | −2,24% |
| 22–110 kV → 1–35 kV | 1.951,7 | 1.925,9 | −1,32% | −1,04% |
| 6–22 kV → 1–35 kV | 2.020,1 | 1.925,9 | −4,66% | −4,48% |
| <6 kV → ≤1 kV | 2.110,4 | 2.082,3 | −1,33% | −1,06% |
⇒ Mức giảm thực với nhóm sản xuất phụ thuộc cấp điện áp PAT đấu nối (**KHÔNG TÌM ĐƯỢC** cấp điện áp/đơn vị bán điện/hợp đồng mua điện của PAT; đã thử BCTC 3 bộ, web) trong khoảng ≈ 1,3%–3,7%. Phép ghép cấp điện áp cũ→mới không 1–1 (cấu trúc đổi) nên đây là khoảng tham khảo.
[TT] Cắt chéo bằng số liệu phân bổ EVN: giảm/1% sản lượng của nhóm sản xuất = 578,1/51,8 = 11,16 tỷ; trung bình mọi nhóm = 1.531,8/99,85 = 15,34 tỷ ⇒ giảm đ/kWh của sản xuất = 0,727 × mức trung bình. Nếu mức trung bình = 44,08 đ/kWh (2% × 2.204,07) ⇒ sản xuất giảm ≈ 32,0 đ/kWh ≈ **1,5–1,7%** của P cũ (1.904,6–2.110,4). Ghi chú nhất quán: tổng "gần 1.600 tỷ/tháng" hàm ý mức giảm trung bình > 2% nếu sản lượng ~25 TWh/tháng (chưa có nguồn sản lượng) — con số EVN chưa tự kiểm được, chỉ dùng tỷ lệ tương đối.

### 1.4 [TT] Điện chiếm bao nhiêu giá thành PAT và độ nhạy
- BCTC PAT KHÔNG tách điện: thuyết minh chi phí theo yếu tố có "Dịch vụ mua ngoài" (FY2025 501,863; 9T/2026 373,218; Q3/2026 115,301; Q3/2025 133,088) — Q3 TM28 không nêu gồm những gì (F2, đã đọc lại). Tổng chi phí yếu tố 9T/2026 1.186,038 ⇒ DV mua ngoài = 31,5% tổng chi phí yếu tố, 33,1% GVHB 9T/2026 (373,218/1.128,706) [TT]. `facts_extracted.md` ghi "chủ yếu điện, ước lượng" — là ước lượng, không phải số công bố.
- Bằng chứng gián tiếp điện là khoản lớn: [DN] BCTC Q3 TM4/TM12: tiền gửi 70 tỷ tại BIDV Hà Thành "đảm bảo nghĩa vụ thanh toán tiền điện" (cùng khoản 01/01/2025 và 30/06/2026) ⇒ PAT tự mua điện (có bảo lãnh thanh toán). [DL-SunSirs 15/04 và 20/05/2026, qua F3] cơ cấu giá thành P4 Trung Quốc: điện ~45% / >40%; ~14.000 kWh/tấn P4 (không phải số của PAT).
- Cận trên độ nhạy [TT] (cho điện = 100% DV mua ngoài): Δchi phí = DV × Δ%. Với DV 9T/2026 = 373,218 (quy năm ×12/9 = 497,6): −1% ⇒ 5,0 tỷ/năm; −2% ⇒ 10,0 tỷ/năm; −3,3% ⇒ 16,4 tỷ/năm; nếu chỉ áp dụng 5 tháng (01/11/2026–31/03/2027): −2% ⇒ 4,1 tỷ. Sau thuế (ETR 9T/2026 = 14,672/230,384 = 6,4%): 10,0 tỷ → 9,4 tỷ = 3,3% LNST kế hoạch 2026 (280) và 4,3% LNST 9T/2026 (215,713).
- Kiểm chéo từ dưới lên [TT, giả định]: 13.000–14.000 kWh/tấn × 1.842,6–1.904,7 đ/kWh × 16.000–20.000 tấn (công suất 20.000 t/năm theo BCN 2024 trích Tạp chí Công Thương; kế hoạch 2025 18.000 t) ⇒ 383–533 tỷ/năm (FY2025 DV mua ngoài thực: 501,9) ⇒ cỡ độ lớn khớp, nghĩa là điện có thể là phần lớn DV mua ngoài, nhưng KHÔNG chứng minh được (sản lượng thực không công bố).
- Quan sát ngược chiều (về khối lượng sản xuất): [TT từ F2 1.4] DV mua ngoài Q3/2026 115,301 vs Q3/2025 133,088 (−13,4%) trong khi H1/2026 257,918 vs H1/2025 227,773 (+13,2%) ⇒ nếu DV tỷ lệ với điện năng (giả định), khối lượng sản xuất H1 tăng, Q3 giảm; NVL Q3/2026 253,091 vs 202,907 (+24,7%).

### 1.5 "Không bền" — bằng chứng
- Ủng hộ: chủ trương nêu mốc hết 31/03/2027 (báo, mục 1.1); EVN dự kiến giảm thu ~1.600 tỷ/tháng (Báo Lào Cai); Phó Thủ tướng: Chính phủ giữ ổn định giá hàng hoá, dịch vụ nhà nước quản lý "đến hết năm 2026" (Tuổi Trẻ 09/11/2026, F3, chỉ tiêu đề+trích); EVN lỗ luỹ kế ~44.800 tỷ và dự thảo cho phép đưa vào giá (F3, nguồn báo, chưa mở trang gốc); NĐ 278/2026: điều chỉnh tăng ≥2% cần ý kiến Bộ Công Thương, giảm <1%/tăng <2% không điều chỉnh (baophapluat.vn qua tìm kiếm).
- Bác bỏ/không khẳng định: QĐ 2892 không ghi ngày hết hiệu lực (luatvietnam); báo không nói giá sau 31/03/2027 sẽ quay lại mức cũ hay tiếp tục; không có văn bản nào chuyển mức giảm thành "tạm thời có điều kiện hoàn lại".
- Phán quyết "không bền": KHÔNG KIỂM ĐƯỢC (mốc 31/03/2027 là chủ trương nêu qua báo, không phải điều khoản văn bản).

---

## 2. QUAN HỆ GIÁ PAT–MẸ (DLC) (khẳng định #2b)

### 2.1 Tỷ trọng doanh thu từ bên liên quan — số BCTC [DN]
Nguồn: Q3 TM30(a) (png_q326/p32, đã xem ảnh) và BN26 TM33.1 (png_bn26/p35-p36), KT2025 TM30.1 (qua F2/facts_extracted).
| Kỳ | Bán cho DLC | DT thuần | % | Mua từ DLC (NVL) | Cổ tức công bố/trả DLC |
|---|---|---|---|---|---|
| FY2024 | 313,004 | 1.721,436 | 18,2% | 533,622 | 102,003 / 216,757 |
| FY2025 | 163,724 | 1.923,386 | 8,5% | 749,863 | 159,380 / 31,876 |
| 9T/2025 | 153,977 | 1.420,835 | 10,8% | 537,036 | 159,380 / 31,876 |
| H1/2026 | 501,854 | 939,271 | 53,4% | 379,835 | — / 127,504 |
| 9T/2026 | 878,140 | 1.379,304 | 63,7% | 627,916 | 36,976 / 164,480 |
| Q3/2026 [TT = 9T−H1] | 376,286 | 440,032 | 85,5% | 248,081 | — |
(Q3/2025 [TT]: 73,501/506,727 = 14,5%.) Dòng Q3: "Bán nguyên vật liệu, thành phẩm, hàng hóa" cho DLC; "Mua nguyên vật liệu" (FY: "hàng hoá, dịch vụ"). DT hàng hoá 9T/2026 chỉ 12,784 ⇒ phần thành phẩm bán DLC ≥ 865,356 = ≥63,3% DT thành phẩm [TT]. Bán cho DGC (tập đoàn) 9T/2026 chỉ 0,869; Văn Minh 0,014.
- Khẳng định "bán lại chủ yếu cho mẹ DGL": **đúng cho kỳ 9T/2026 trở đi**; **không đúng** cho 2024–9T/2025. Tên pháp nhân: mẹ trực tiếp = Công ty TNHH MTV Hóa chất Đức Giang Lào Cai ("DLC", 51,00%), do CTCP Tập đoàn Hóa chất Đức Giang (DGC) sở hữu 100% (Q3 TM17(b); BC báo chí).
- Phân khúc địa lý [DN]: 9T/2026 trong nước 891,796 / nước ngoài 487,508; H1/2026 511,160 / 428,111 (png_bn26/p35) ⇒ Q3/2026 [TT]: trong nước 380,636 (86,5%), nước ngoài 59,397 (13,5%). Bán DLC / DT trong nước 9T/2026 = 98,5% ([TT] 878,140/891,796) — doanh thu "trong nước" gần như = bán cho DLC. 9T/2025: nước ngoài 1.183,32 (83,3%).
- Số dư [DN] (F2 2.3): phải trả DLC 161,593 (01/01/2025) → 313,330 (31/12/2025) → 16,519 (30/09/2026); phải thu DLC 114,345 (30/06/2026), không còn tại 30/09/2026. [TT] chênh Q3: bán DLC 376,3 vs mua từ DLC 248,1; hai chiều bù trừ lẫn nhau theo kỳ.
- Hỗ trợ tín dụng từ mẹ [DN] (Q3 TM15, F2): bảo đảm vay bằng thư bảo lãnh của DLC và DGC mỗi bên tối đa 400 tỷ (hạn mức BIDV 400 tỷ, Vietinbank 300 tỷ) + tiền gửi USD 1,61 triệu của DLC (hạn mức BIDV; đã đối chiếu ảnh ở F2); đồng thời tiền gửi 40 tỷ + 100.000 USD của PAT tại Vietinbank bảo đảm vay "của Công ty và các công ty thành viên" (Q3 TM4) — dư nợ của các công ty thành viên không được nêu.

### 2.2 Chính sách giá / hợp đồng / tờ trình
- Nguyên tắc giá (giá thị trường, cost-plus, netback), hợp đồng nguyên tắc, điều khoản chia sẻ chi phí: **KHÔNG NÊU** trong 3 bộ BCTC (TM30 chỉ liệt kê số tiền) và **KHÔNG TÌM ĐƯỢC** ở nơi nào khác (đã thử: Báo Pháp Luật, Vietstock, nhadautu, Tạp chí Công Thương, tinnhanhchungkhoan, 24hmoney, tìm theo "hợp đồng nguyên tắc/giá chuyển nhượng/tờ trình bên liên quan" 6 truy vấn; BCTN 2025 PAT không tìm thấy bản gốc).
- ĐHĐCĐ bất thường **12/05/2026** (nhadautu.vn 18/05/2026 https://nhadautu.vn/cong-ty-con-cua-hoa-chat-duc-giang-co-hdqt-moi-d105050.html và Vietstock 15/05/2026 https://vietstock.vn/2026/05/cong-ty-con-cua-hoa-chat-duc-giang-tai-cau-truc-dan-lanh-dao-214-1443012.htm): thông qua "tờ trình về giao dịch với bên liên quan trong năm nay" — **báo không nêu đối tác, giá trị, nguyên tắc giá, tỷ lệ tán thành**; cùng cuộc họp miễn nhiệm HĐQT/Trưởng BKS và bầu lãnh đạo mới "hiện đang công tác tại Tập đoàn Hóa chất Đức Giang" (Vietstock) ⇒ HĐQT hiện tại do bên mẹ cử. Ngày họp: 12/05 (nhadautu, Vietstock) vs dự kiến 13/05 (Báo Pháp Luật 23/03; BCTC ghi HĐQT thay 13/05 ở F1) — ghi cả hai.
- ĐHĐCĐ thường niên **14/08/2026**: NQ số 02/2026/NQ-ĐHĐCĐ ngày 14/08/2026 (Q3 TM, p28); CBTT "Nghị quyết ĐHĐCĐ thường niên 2026" ngày 17/08, "Tài liệu họp" 22/07, 29/07, 05/08 (24hmoney https://24hmoney.vn/stock/pat/events, chỉ tiêu đề). Nội dung tờ trình giao dịch bên liên quan 2026 ở kỳ họp này: KHÔNG TÌM ĐƯỢC. Danh sách CBTT 24hmoney tháng 8–11/2026 không có mục "giải trình"/"hợp đồng bên liên quan" (snapshot, có thể thiếu).
- Phát biểu cũ (không phải điều khoản): [BC-Tạp chí Công Thương 16/03/2025 trích BCN 2024] "các giao dịch giữa hai công ty đều minh bạch và không làm mất quyền lợi của một bên nào"; DLC "hỗ trợ cần thiết và kịp thời nguồn quặng Apatit"; thời kỳ đầu "chỉ bán được hàng cho Hóa chất Đức Giang"; PAT 20.000 t/năm (~14% cả nước), DLC 40.000 t/năm (https://tapchicongthuong.vn/doanh-nghiep-phot-pho-vang-hang-dau-viet-nam-muon-chia-co-tuc-tien-mat-ty-le-95--100-138443.htm).
- [TT, có điều kiện] Quy định pháp luật có thể liên quan: giao dịch với người liên quan ≥35% tổng tài sản (BCTC gần nhất) thuộc thẩm quyền ĐHĐCĐ, cổ đông có lợi ích liên quan không có quyền biểu quyết (LDN 2020 Đ.167, qua bài luật sư; không đọc văn bản gốc, LDN sửa đổi 2025 chưa kiểm). Tổng tài sản 31/12/2025 = 1.444,31 ⇒ 35% = 505,5; bán DLC 9T/2026 (878,1) lớn hơn ngưỡng ⇒ có thể là lý do có "tờ trình" — chưa xác nhận vì không có văn bản; không rõ DLC có bỏ phiếu hay không.

### 2.3 Kiểm tra gợi ý "giá chuyển nhượng thấp hơn thị trường" vs "chi phí đầu vào tăng" (cùng khả dĩ, không phân biệt được)
[TT] GPM theo kỳ vs tỷ trọng bán DLC: FY2025 22,8% / 8,5%; 9T/2025 24,4% / 10,8%; FY2024 21,1% / 18,2%; 9T/2026 18,2% / 63,7%; H1/2026 19,9% / 53,4%; Q3/2026 14,5% / 85,5%; Q3/2025 25,7% / 14,5%. Chiều âm khi tỷ trọng bán DLC tăng (trừ FY2024) khớp giả thuyết A (giá bán DLC thấp hơn giá xuất ngoài); nhưng khớp luôn giả thuyết B (giá vốn tăng: NVL 9T/2026 +19,1% vs DT −2,9%; DGC hợp nhất cũng tụt biên gộp 31,1% → 20,5% ở Q3 mà không có chuyển dịch bán nội bộ kiểu này). Bằng chứng phân biệt cần: đơn giá/sản lượng theo khách hàng (không công bố).

---

## 3. CHUỖI GIÁ P4 VS GIÁ BÁN THỰC TẾ CỦA PAT (khẳng định #2c, #2d)

### 3.1 Giá P4 Trung Quốc (RMB/tấn, SunSirs benchmark; BQ `tav2_bq.commodity_prices` qua `factpack/data/pat_commodity_quarterly.csv`, lọc ngày T2–T6) [DL]
| Quý | 2025Q1 | Q2 | Q3 | Q4 | 2026Q1 | Q2 | Q3 | Q4 đến 13/11 |
|---|---|---|---|---|---|---|---|---|
| TB quý | 23.561 | 23.494 | 22.592 | 22.612 | 24.514 | 31.105 | 27.606 | 28.191 |
Điểm rời [DL, F3]: 23/01/2026 23.512,67 · 27/03 26.796 · 15/04 31.162,67 · 19/05 32.429,33 · 22/05 ~33.962 · đầu 07 28.500 → đáy 25.500–25.700 · 07/08 27.000–27.200. **Cập nhật 17/11/2026** (https://www.sunsirs.com/uk/prodetail-708.html): 28.466,33 từ 12 đến 17/11 — chuỗi đứng yên 6 ngày liên tiếp (nghi chưa cập nhật). SMM 06/07/2026: P4 xuất xưởng 34.500 CNY/t, hợp đồng dài hạn là chủ đạo (https://news.metal.com/en/newscontent/103989747-phosphorus-chemical-industry-june-sulfur-surges-phosphate-rock-holds-firm-fertilizers-struggle-new-materials-expand). Không tìm được số tháng 10/2026 của SunSirs (trang bảng không hiển thị).
- Giá quốc tế FOB Hải Phòng: nguồn duy nhất tìm được là tổng hợp price-watch.ai (https://www.price-watch.ai/yellow-phosphorus-prices; không rõ ngày, không phải Argus/ICIS): Q3/2025 4.000–4.200 USD/t; Q2/2026 +29,8% QoQ; Q3/2026 ≈ +6% QoQ — **mâu thuẫn** với SunSirs Q3/2026 −11,2% QoQ; độ tin cậy thấp. Argus/ICIS: KHÔNG TÌM ĐƯỢC (paywall). Giá P4 xuất khẩu theo Hải quan: KHÔNG TÌM ĐƯỢC (đã thử tìm theo tháng/HS).

### 3.2 Doanh thu PAT theo quý vs giá P4 [TT từ F4 `pat_quarterly_series.csv` + BCTC]
| | 2025Q1 | Q2 | Q3 | Q4 | 2026Q1 | Q2 | Q3 |
|---|---|---|---|---|---|---|---|
| DT thuần | 436,4 | 477,7 | 506,7 | 502,6 | 421,9 | 517,4 | 440,0 |
| LNST | 84,7 | 77,6 | 110,0 | 75,2 (BQ; 70,9 theo BCTC KT) | 46,6 | 109,8 | 59,3 |
| Chỉ số DT (Q1/25=100) | 100 | 109,4 | 116,1 | 115,1 | 96,7 | 118,5 | 100,8 |
| Chỉ số P4 SunSirs (Q1/25=100) | 100 | 99,7 | 95,9 | 96,0 | 104,0 | 132,0 | 117,2 |
YoY 2026: DT −3,3% / +8,3% / −13,2%; LNST −45,1% / +41,5% / −46,1%; P4 (RMB) +4,0% / +32,4% / +22,2%. QoQ Q1→Q2: DT +22,6%, P4 +26,9%; Q2→Q3: DT −14,9%, P4 −11,2%. Không có sản lượng (tấn) trong BCTC (F2) ⇒ **KHÔNG TÍNH ĐƯỢC giá bán bình quân/tấn thực tế** (chỉ có giá kế hoạch 2025 = 1.800 tỷ/18.000 t = 100 triệu đ/t). Không điều chỉnh tỷ giá RMB/VND.
- Ủng hộ "tăng giá thị trường có về PAT": Q1→Q2/2026 DT +22,6% bám P4 +26,9% và GPM nhảy 13,6% → 25,0% [TT: GP Q1 = 186,994 − 129,41 = 57,584; Q2 129,41; Q3 63,604]; Q2→Q3 DT −14,9% bám P4 −11,2%. Doanh nghiệp (Q3/2025): "giá bán phốt pho vàng tăng thêm 10%" (Báo Pháp Luật 24/10/2025; F2).
- Bác bỏ/mâu thuẫn: (i) YoY khoảng cách DT − P4: Q1 −7,3pt, Q2 −24,1pt, Q3 −35,4pt ⇒ phần tăng giá thị trường (+32%/+22%) không hiện ra tương ứng trong DT (hoặc sản lượng giảm/ giá bán DLC thấp). (ii) Q3/2026: giá P4 YoY +22,2% nhưng GPM 14,5% vs 25,7% và LNST −46,1%. (iii) Q1/2026 DN: "giá bán sản phẩm phốt pho vàng không có biến động nhiều" trong khi "giá vốn sản xuất tăng 14%" (CafeF 23/04/2026, index.vn 24/04/2026, F2) — kèm thuế XK 5%→10% từ 01/01/2026. (iv) [TT thô, nhiều giả định] DT/DV mua ngoài (proxy "DT trên một đơn vị sản xuất điện năng"): Q3/2026 440,032/115,301 = 3,816 vs Q3/2025 506,727/133,088 = 3,807 (+0,2%); H1/2026 3,642 vs H1/2025 4,013 (−9,3%) ⇒ giá thực hiện bình quân/đơn vị sản xuất gần như không đổi trong Q3 YoY trong khi benchmark +22% (không tính tồn kho: HTK tăng 74,843 → 120,190 từ 30/06 đến 30/09/2026, sản xuất > tiêu thụ).
- DGC (mẹ cao nhất) cùng kỳ: [BC-24hmoney 15/08/2026] Q2/2026 mảng P4 doanh thu 1.572 tỷ (−6,3% YoY), sản lượng tiêu thụ −19,5% ⇒ [TT] giá bình quân ngầm định = 0,937/0,805 = 1,164 → **+16,4% YoY** so với benchmark SunSirs Q2 +32,4% (chỉ khoảng một nửa); HĐQT DGC (Phạm Duy Tùng, ĐHĐCĐ 13/08/2026, Mekong ASEAN https://mekongasean.vn/lanh-dao-dgc-noi-ve-ly-do-loi-nhuan-sut-giam-van-de-xu-ly-moi-truong-58434.html): sụt lợi nhuận "hoàn toàn không đến từ mảng phốt pho, bởi sản lượng và giá bán mặt hàng này vẫn duy trì ở mức ổn định" (mâu thuẫn nội bộ với số sản lượng −19,5% từ nguồn báo khác).

### 3.3 Power thương lượng / chuyển giá chi phí cho khách hàng
- Ủng hộ khả năng chuyển giá: P4 nhu cầu tăng (tiêu thụ biểu kiến Trung Quốc ~1,0019 triệu tấn 2025, +18% [DL-SunSirs 13/02/2026 https://www.sunsirs.com/uk/detail_news-30660.html]); công suất mới Trung Quốc bị kiểm soát chặt (cùng nguồn); EU phụ thuộc nhập khẩu P4 (CRU 22/04/2026, chỉ đoạn mở: phiên "P4 – rủi ro nguồn cung" tại hội nghị CRU Paris); P4 xuất khẩu của VN chủ yếu Nhật/Hàn/Ấn (nhadautu 08/05/2026 cho DGC) .
- Bác bỏ/giới hạn: (i) Cung dư: Mysteel (20/01/2026, trích F3) dự kiến thặng dư ròng 2026 ~45,5 kt; SunSirs 07/08/2026: nhu cầu "không có tín hiệu phục hồi tổng thể"; SMM 06/07/2026: giá cao "kìm hãm mua của hạ nguồn". (ii) Quy mô PAT: 20.000 t/năm ≈ 14% công suất VN (BCN 2024); tổng công suất VN ~125.000 t (VietTimes 18/03/2026, F3) so với Trung Quốc sản lượng 2024 ~851.800 t (tìm kiếm, nguồn thứ cấp) ⇒ PAT đơn lẻ ≪ 5% cung toàn cầu. (iii) 2026 PAT bán 63,7% cho DLC ⇒ "power thương lượng" của PAT chính là giá chuyển nhượng do bên mẹ đặt, không phải giá thị trường với khách ngoài. (iv) Dữ liệu chuyển thuế XK: PAT 9T/2026 thuế XNK phát sinh 51,610 trên DT nước ngoài 487,508 = 10,6% [TT] (FY2025: 88,627/1.738,334 = 5,1%) — tức DT xuất khẩu của PAT chịu ~đủ 10% (không thấy hưởng 0%); DN không công bố phần chuyển sang giá.
- "Vị thế thứ ba thế giới": TheLEADER 17/12/2025 (https://theleader.vn/phot-pho-vang-gap-kho-hoa-chat-duc-giang-se-ra-sao-d43513.html) viết DGC là "nhà xuất khẩu P4 lớn nhất thế giới, ~1/3 xuất khẩu toàn cầu" (không dẫn gốc); một báo cáo thị trường (marketpublishers, qua tìm kiếm) "gần 1/3 xuất khẩu toàn cầu" (không nguồn). KHÔNG TÌM ĐƯỢC xếp hạng "thứ ba". ⇒ KHÔNG KIỂM ĐƯỢC (hai nguồn báo đều nói mạnh hơn user nhưng không gốc).

---

## 4. RỦI RO THAY THẾ P4 (khẳng định #2d)

- Cơ cấu cầu P4 (SunSirs 13/02/2026): axit photphoric nhiệt 33%, glyphosate 27%, PCl3 24%, ~16% còn lại không phân tách; tăng trưởng mới từ LiPF6. Nhu cầu glyphosate "ổn định".
- **Có thay thế biên (bác bỏ "không có rủi ro thay thế")**: [DL-SMM 15/04/2026 https://news.metal.com/newscontent/103857855-Brief-Analysis-of-Production-Changes-in-Chinas-Phosphorus-Based-New-Energy-Materials-2025] sản lượng axit photphoric tinh chế quy trình ướt tăng **23,19%** (2025 vs 2024), LFP +60,06%, sắt photphat +67,17%; SunSirs mô tả axit tinh chế quy trình ướt (chiết dung môi) là nguồn P cho LFP. ⇒ một phần cầu LFP được phục vụ bằng đường ướt, không qua P4.
- **Xu hướng ngược (ủng hộ "khó thay thế")**: lưu huỳnh tăng mạnh (nội địa TQ 4.065 NDT/t ngày 04/02/2026, +172% so đầu 2025; >10.000 NDT/t tháng 06/2026, +257% từ đầu năm [SMM 06/07/2026]) đẩy chi phí đường ướt (1,292 t S/t axit; tăng ~3.319 NDT/t axit); axit nhiệt rẻ hơn axit ướt từ 05/2025 và độ tinh khiết cao hơn (SunSirs 13/02/2026); SMM 06/07/2026: Wengfu axit ướt 85% tăng 10.600 → 12.100 NDT/t. Bán dẫn: độ tinh khiết yêu cầu khiến thay thế khó (tìm kiếm trích marketpublishers/ChemAnalyst; trang ChemAnalyst 403 không mở được).
- Châu Âu coi P4 là nguyên liệu chiến lược (ESPP SCOPE 159, 03/2026; CRU 22/04/2026; chỉ tiêu đề/đoạn mở).
- Không tìm được nguồn nào cho thấy công nghệ "P4-free" cho axit tinh khiết/ LFP/ bán dẫn đã đạt thương mại hoá 2026 (đã thử: SunSirs, SMM, ChemAnalyst, CRU, ESPP, tìm theo "alternative route"). Không tìm được số liệu thay thế trong thuốc BVTV (glyphosate) ở 2026.
- Phán quyết: không có bằng chứng thay thế P4 diện rộng đang xảy ra; có bằng chứng thay thế biên ở axit tinh khiết cho LFP (nhóm cầu mới tăng nhanh). Rủi ro thay thế hiện KHÔNG phải kênh tác động chính lên PAT năm 2026 (kênh chính: chi phí quặng/lưu huỳnh/than, giá chuyển nhượng nội bộ, sản lượng).

---

## 5. ĐƯỜNG PHỤC HỒI THEO QUÝ (phần quý của #1)

### 5.1 PAT — số công bố [DN, ảnh BCTC + BQ; F4]
| Quý | DT | GP / GPM | LNST | YoY LNST |
|---|---|---|---|---|
| Q1/2025 | 436,4 | — / 26,5% | 84,7 | |
| Q2/2025 | 477,7 | — / 21,1% | 77,6 | |
| Q3/2025 | 506,7 | 130,471 / 25,7% | 110,0 | |
| Q4/2025 | 502,6 | 92,365 / 18,4% [TT: 439,449−347,084] | 75,2 (BQ) / 70,9 (BCTC KT) | |
| Q1/2026 | 421,9 | 57,584 / 13,6% [TT] | 46,6 | −45,1% |
| Q2/2026 | 517,4 | 129,41 / 25,0% | 109,8 | +41,5% |
| Q3/2026 | 440,0 | 63,604 / 14,5% | 59,3 | −46,1% |
9T/2026 LNST 215,713 (−20,8%); DT 1.379,304 (−2,9%); GPM 9T 18,2% vs 24,4%. (GPM Q1/Q2 2025 từ báo chí/F2; [TT] H1/2025: GP 216,612/DT 914,108 = 23,7%.) Bất nhất của riêng 2025: Q4/2025 BQ chưa kiểm toán vs BCTC KT (LNST +4,28; F4 1.4).
- **So với khẳng định "tệ nhất Q2, Q3, sau đó tốt dần"**: PAT quý thấp nhất 2026 là **Q1** (46,6); **Q2 là quý tốt nhất 2026 và tốt hơn Q2/2025 +41,5%**; Q3 (59,3) yếu thứ nhì và kém Q3/2025 −46,1%. Ủng hộ một phần: Q3/2026 là quý có GPM thấp (14,5%) cùng Q1 (13,6%) và LNST −46% YoY; chưa có số Q4. Bác bỏ: Q2 không phải đáy; đường đi không đơn điệu (Q1 thấp → Q2 cao → Q3 thấp).
- Có thể Q2/2026 chịu yếu tố một lần? KHÔNG TÌM ĐƯỢC giải trình Q2/Q3 của DN (Báo Pháp Luật 24/07 và 24/10/2026: "không nêu/không có giải trình chính thức"; tinnhanhchungkhoan 23/07/2026 không có giải thích; 24hmoney: không có mục "giải trình" PAT tháng 8–11/2026).

### 5.2 DGC (hệ sinh thái hợp nhất) — số báo chí về BCTC DGC [BC]
| Quý/2026 | DT | GPM | LNST | YoY LNST |
|---|---|---|---|---|
| Q1 | 2.124,6 (−24,4%) | ~23% (35% Q1/25) | 430,05 | −48,6% |
| Q2 | ~2.416 (−16,5% đến −16,6% tuỳ nguồn) | 18,9% (từ 33,9%) theo elibook 08/09/2026; 24hmoney ghi "21%" — mâu thuẫn | ~440,8 | −50,5% |
| Q3 | 2.469,45 (−12,3%) | 20,5% (từ 31,1%) | 506,68 | −37% |
(Nguồn: doanhnghiephoinhap.vn 07/07/2026 và Báo Pháp Luật (Q1); elibook https://elibook.vn/2026/09/08/dgc-loi-nhuan-quy-2-roi-hon-nua-kiem-toan-ngoai-tru-va-ghe-chu-tich-doi-nguoi-nhung-khong-doi-ho/ (Q2); Báo Pháp Luật 29/10/2026 (Q3).) 9T/2026 LNST 1.369,4 (−45,9%), 85,6% mục tiêu; [TT] 430,05+440,8+506,68 = 1.377,5 ≠ 1.369,4 (lệch 8,1, có thể do LNST hợp nhất vs của cổ đông công ty mẹ — chưa xác định). Kế hoạch 2026: DT 10.100, LNST 1.600 (ĐHĐCĐ 13/08/2026).
- Với DGC: "Q2 tệ nhất" **khớp** (YoY −50,5%, GPM thấp nhất 18,9%); "Q3 tệ" **không khớp** (LNST Q3 > Q2, YoY cải thiện −37%, GPM 20,5% > 18,9%); về mức LNST tuyệt đối Q1 thấp nhất. "Tốt dần": LNST Q1→Q2→Q3 tăng 430 → 441 → 507 nhưng vẫn −37% YoY.

### 5.3 Phát biểu của DN/mẹ về Q4/2026 và 2027
- **PAT**: KHÔNG TÌM ĐƯỢC phát biểu/dự báo Q4/2026, 2027 (đã thử: Báo Pháp Luật, tinnhanhchungkhoan, 24hmoney, Tạp chí Công Thương, tìm theo "quý 4/2026", "kế hoạch 2027"; không có IR/BCTN 2025/NQ gốc). Chỉ có kế hoạch năm 2026: DT 2.111, LNST 280, cổ tức 90% (Báo Pháp Luật 24/10/2026; không nêu nguồn nghị quyết; F1: nghị quyết ĐHĐCĐ không xác nhận được). [TT] số học kế hoạch: Q4 cần DT 731,696 và LNST 64,287 (so Q3 440,0/59,3; Q4/2025 502,6/70,9 BCTC KT) ⇒ kế hoạch ngụ ý Q4 LNST ≈ Q3 và −9% YoY, không phải "tốt lên".
- **DGC**: 13/08/2026 (nhadautu https://nhadautu.vn/dgc-dat-ke-hoach-loi-nhuan-giam-gan-mot-nua-nguon-quang-tro-thanh-bien-so-d106952.html): quặng "ngày càng khan hiếm", mục tiêu trước mắt đảm bảo nguyên liệu "ít nhất đến đầu năm sau", đa dạng hoá nhập khẩu; chưa có kết luận chính thức khai trường 25 nên chưa nêu ngày chạy lại; lưu huỳnh, than cốc, năng lượng tăng áp lực chi phí; Nghi Sơn mục tiêu chạy Q4/2026 (~5 tháng chậm so kế hoạch). 08/05/2026 (nhadautu): CEO lúc đó "Lượng quặng không thiếu, nhưng chi phí nguyên liệu tăng và đó là điều chúng ta phải chấp nhận"; nhập quặng Pakistan/Ai Cập, đàm phán 5 nhà cung cấp. Mục tiêu LNST 2026 (1.600) so với 9T (1.369,4) ⇒ Q4 ngụ ý ≈ 230,6 (24hmoney: "còn cách chỉ tiêu ~231 tỷ trong quý IV") — thấp hơn nhiều so với Q3 (506,7) ⇒ hoặc kế hoạch bảo thủ, hoặc dự phòng/chi phí Q4; không có giải thích của DN. Phát biểu về 2027: KHÔNG TÌM ĐƯỢC (nhadautu/mekongasean/24hmoney: không có). Yếu tố lịch đã biết có thể ảnh hưởng đầu 2027: thuế XK P4 15% từ 01/01/2027 (NĐ 199/2025, F3); mốc 31/03/2027 của chủ trương giảm giá điện (mục 1); gia hạn giấy phép khai trường 25 cuối 2026 "có thể bị ảnh hưởng" (tìm kiếm — nguồn báo/CTCK, chưa xác minh, không dùng làm fact).
- Phán quyết "sau đó tốt dần lên": **KHÔNG KIỂM ĐƯỢC** (không có tài liệu DN; số học kế hoạch không ủng hộ cải thiện Q4; chiều giá P4 có phục hồi (Q4 đến nay 28.191 vs Q3 27.606, +2,1%) nhưng chi phí quặng/lưu huỳnh chưa có tín hiệu giảm trong dữ liệu đã tìm).

---

## 6. PHÁN QUYẾT CHI TIẾT (ủng hộ + bác bỏ)

**#2a Giá điện −2%, không bền — ĐÚNG (bình quân) / MỘT PHẦN (nhóm sản xuất) / KHÔNG KIỂM ĐƯỢC (độ bền).**
- Ủng hộ: QĐ 1305/QĐ-EVN và 2892/QĐ-BCT có thật, 01/11/2026, −2% bình quân (2.204,0655 → 2.159,9037); mốc chủ trương 31/03/2027; Chính phủ chỉ ổn định giá "đến hết 2026"; EVN lỗ luỹ kế.
- Bác bỏ: mức giảm sản xuất không đều theo cấp điện áp (≈1,3–3,7% theo biểu; ≈1,5–1,7% theo phân bổ EVN); sinh hoạt bậc cao tăng; tác động lên PAT rất nhỏ (≤ ~0,6% tổng chi phí yếu tố, ≈10 tỷ/năm trước thuế tại trần trên); văn bản không ghi hạn.
**#2b PAT bán chủ yếu cho mẹ — MỘT PHẦN.** Ủng hộ: 63,7% DT 9T/2026, 85,5% Q3, 98,5% DT trong nước; mua từ DLC ~88% chi phí NVL. Bác bỏ: 18,2%/8,5% năm 2024/2025; xuất khẩu trực tiếp ~90% DT 2025; giá/điều khoản không công bố; tờ trình nội dung không tìm được.
**#2c Xuất khẩu là chính, thứ ba thế giới, power thương lượng — MỘT PHẦN / KHÔNG KIỂM ĐƯỢC.** Ủng hộ: DGC Nhật/Hàn/Ấn; Q2 PAT hưởng giá cao (GPM 25%); P4 tăng giá thị trường. Bác bỏ: PAT 9T/2026 xuất khẩu 35% DT; phần tăng giá +32% (Q2) chỉ về ~một nửa ở DGC (+16,4% ngầm định); Q3 giá +22% mà GPM −11pt; "thứ ba" không kiểm được; cung Trung Quốc dư (Mysteel).
**#2d Chuyển chi phí cho khách hàng, trừ rủi ro thay thế — MỘT PHẦN.** Ủng hộ: Q2/2026 margin phục hồi cùng giá P4; sulfur cao làm P4 có lợi thế chi phí so với đường ướt. Bác bỏ: Q1/2026 giá bán không đổi khi chi phí +14% và thuế XK 5→10%; Q3/2026 biên về 14,5%; thay thế biên ở LFP (axit ướt +23%); DT xuất khẩu chịu ~10,6% thuế (không thấy 0%).
**#1 (phần quý) — SAI cho PAT; MỘT PHẦN cho DGC; "tốt dần": KHÔNG KIỂM ĐƯỢC.** Bảng 5.1/5.2.

---

## ĐÃ BỎ
- Báo cáo CTCK có định giá/dự phóng (Vietcap, DSC, TCBS, BSC, KBSV, FPTS, HSC, SHS) — chỉ dùng như điểm trỏ khi báo chí trích; ĐÃ BỎ: số giá P4 ~3.400/4.000 USD/t của TCBS, tỷ lệ chuyển thuế XK sang khách của Vietcap (nguồn CTCK), dự phóng DSC về Nghi Sơn 2027–2029, nhận định rủi ro gia hạn giấy phép khai trường 25 (nguồn CTCK/báo, không dùng làm fact).
- Nội dung giá cổ phiếu/vốn hoá/khuyến nghị trong các bài (24hmoney, Vietcap tiêu đề "Outperform", elibook): không đọc, không chép.
- Vietcap/trang CTCK các URL "research-center": không mở.

## KHÔNG TÌM ĐƯỢC (đã thử)
- Cấp điện áp, nhà cung cấp điện, hợp đồng mua điện và định mức kWh/tấn của PAT (BCTC 3 bộ; web; BCN 2025 PAT không có bản gốc).
- Văn bản QĐ 1305/QĐ-EVN gốc; nội dung văn bản 557/TB-VPCP (PDF không trích được chữ); bảng giá phụ lục QĐ 1279 gốc (chỉ báo/bản chép).
- Giá chuyển nhượng PAT–DLC, hợp đồng nguyên tắc, điều khoản chia sẻ chi phí; nội dung tờ trình giao dịch bên liên quan ĐHĐCĐ 12/05 và 14/08/2026; số hiệu NQ 12/05; tỷ lệ biểu quyết (6+ truy vấn, 24hmoney/Vietstock/nhadautu).
- Sản lượng P4 (tấn) PAT, đơn giá bán bình quân/tấn thực tế; giá P4 xuất khẩu USD/t theo Hải quan; Argus/ICIS.
- Số liệu Q1/2026 riêng của "bán cho DLC" (không có BCTC Q1); giải trình DN Q2, Q3/2026.
- Phát biểu của DN về Q4/2026 và 2027 (PAT); phát biểu 2027 (DGC).
- Xếp hạng "thứ ba thế giới" của DGC.
- Xác nhận 31/03/2027 trong văn bản gốc.

## ĐIỂM MÂU THUẪN
1. Phân khúc địa lý PAT: H1/2025 (BN26 so sánh) trong nước 348,691 / nước ngoài 565,417; 9T/2025 (Q3 so sánh) 237,52 / 1.183,32; FY2025 185,052 / 1.738,334 ⇒ trong nước giảm 348,7 → 237,5 → 185,1 theo kỳ luỹ kế (không thể giảm) và Q3/2025 trong nước ngầm định âm (−111,2). Số trong nước H1/2025 trùng chữ số với FY2024 (348,69). Không giải quyết được; bán DLC 80,5 → 154,0 → 163,7 thì tăng đúng.
2. Mức giảm điện: EVN/báo "2% mọi nhóm" (VietnamPlus) vs biểu giá cho thấy sinh hoạt bậc cao tăng và sản xuất giảm ≠ 2% (nhóm); EVN "gần 1.600 tỷ/tháng" hàm ý giảm trung bình > 2% nếu sản lượng ~25 TWh/tháng (chưa có nguồn sản lượng).
3. "Giảm 2% đến hết 31/03/2027" (Người Quan Sát: mục tiêu của Phó Thủ tướng) vs QĐ 2892 không nêu hạn.
4. SunSirs vs price-watch Q3/2026: −11,2% QoQ (RMB, SunSirs) vs ≈ +6% QoQ (FOB Hải Phòng, price-watch).
5. DGC Q2/2026 GPM: 18,9% (elibook) vs "thu hẹp còn 21%" (24hmoney, không rõ chỉ số).
6. DGC: "sản lượng và giá bán [phốt pho] ổn định" (HĐQT, 13/08) vs sản lượng tiêu thụ P4 −19,5% Q2 (24hmoney 15/08).
7. DGC LNST 9T 1.369,4 vs tổng ba quý báo chí 1.377,5.
8. Ngày ĐHĐCĐ bất thường PAT 12/05 vs 13/05/2026.
9. Q4/2025 PAT LNST: BQ 75,165 vs BCTC kiểm toán 70,885 (suy từ FY−9T).
10. Giá điện cũ: nguồn Tiền Phong dấu ngày 12/05/2026 trình biểu giá 1279 (đã áp từ 10/05/2025); trùng 1.811 và 1.833/1.190/3.398 với nguồn khác nhưng chưa đối chiếu phụ lục gốc.
