# DD DRI — cập nhật sau BCTC hợp nhất Q3/2026 (job `Taylor_20261027_042354`, 27/10/2026)

> Chỉ nghiên cứu, KHÔNG đặt lệnh. Không sửa `REPORT.md`, `model.py`, checklist 25/10, khối mù `dd_blind2_DRI_20261026/`
> (md5 kiểm lại `15bd430e…` khớp). Giá tham chiếu **14.700 đ = `Price` 26/10 [BQ]**; giá phiên 27/10 CHƯA đo (cần DNSE).
> Nhãn: **[BCTC3]** BCTC HN Q3/2026 (ký 22/10/2026, tải từ dri.com.vn) · **[SX]** BCTC HN bán niên 2026 soát xét (AFC, ký
> 14/08) + CV 52/CV-CT 17/08 · **[SXKD]** báo cáo SXKD tháng/quý của DRI (dri.com.vn) · **[BQ]** · **[UL]** ước lượng.
> Số trích chi tiết kèm số trang ảnh: `extract_q3_bctc.md`. Tính toán: `python3 model_q3.py`.

## 0. Kết luận
- **Theo kế hoạch đã duyệt: KHÔNG có điều kiện nào kích hoạt ⇒ GIỮ** (vùng giữa 22–50 tỷ). LNST mẹ Q3 **25,98 tỷ** ≥ 22.
  Nếu tính Q3 từ 9T trừ H1 soát xét thì được 25,54 tỷ, vẫn ≥ 22. Biên an toàn so với ngưỡng chỉ 16–18%. Dakruco không vay thêm,
  không có sự kiện Lào, giá 14.700 < 15.100.
- **Hai cờ "nghiêng GIẢM" ở bảng §6b đã bật:** (i) thành phẩm tồn kho 64,99 → **138,81 tỷ**, tức DRI đang giữ hàng;
  (ii) CFO 9T / LNST 9T = **0,75x**, dưới ngưỡng 0,8.
- **Ý kiến riêng: GIẢM 50% CHỦ ĐỘNG** (SpaceX −1.250, ZaloPay −650), không đợi giá về 15.100. Đây là đề xuất ngoài kế
  hoạch đã duyệt, user quyết.
  - Lý do: FV kỳ vọng hạ còn **11.031 đ (−25%)** [UL]. Hai cờ §6b đã bật. Thưởng 2026 vẫn chưa trích, tức Q4 còn rủi ro chi phí.
  - Lý do giữ nửa còn lại: miss Q3 phần lớn là do **chưa bán** (khoảng 1.700 t hàng tồn, ước lượng), không phải mất cầu.
    Q4 là quý bán hàng, và DRI dự kiến chuyển sàn HOSE trong Q4.
  - Mốc 15.100 giữ nguyên cho nửa còn lại.
- **Dự báo đều trượt:** DD 55–65 tỷ, F khoá mù ≥50 tỷ và biên ≥27%. Riêng F **KHÔNG được chấm là dự báo mù**. Báo cáo SXKD
  9T đăng ngày 20/10 đã công bố LNTT 9T 208,21 tỷ, suy ra LNTT Q3 khoảng 26 tỷ. Báo cáo này lên mạng **trước** giờ khoá
  26/10 12:47 (mục 2).

## 1. Nguồn đã tải (dri.com.vn, 27/10)
| Tài liệu | Ngày trên web / ngày trên văn bản | Ghi chú |
|---|---|---|
| BCTC HN + riêng Q3/2026 + CV giải trình 72/CV-CT | trang đăng **26/10/2026 17:28**; BCTC ký 22/10; CV ngày 23/10 (metadata PDF sửa 23/10 11:45) | CĐKT, LCTT, thuyết minh đã đọc (35 trang scan) |
| Báo cáo SXKD 9 tháng 2026 (29/BC-CT) | trang đăng **20/10/2026 16:20**; văn bản ngày 20/10 | tấn bán, LNTT 9T, kế hoạch Q4 |
| Báo cáo SXKD tháng 7, tháng 8, 6 tháng, Q1 | 11/08, 09/09, 22/07, 22/04 (theo văn bản) | tấn và USD theo tháng |
| BCTC HN bán niên soát xét + CV 52/CV-CT | CV ngày 17/08 | điều chỉnh H1 |
- **CHƯA lấy được:** timestamp CBTT trên HNX/UPCoM. Tìm cafef/vietstock không ra mục Q3 có giờ. Thuyết minh không công bố
  nguyên tệ USD, lãi suất, kỳ hạn của tiền gửi có kỳ hạn ở Lào (chỉ có số VND).

## 2. Ngày công bố thật và tính "mù" của F
- Khoá mù lúc **26/10 12:47 ICT**. Trang BCTC Q3 trên dri.com.vn đăng sau đó (26/10 17:28). CV giải trình gửi UBCK/HNX đề
  ngày 23/10 ⇒ BCTC **có khả năng** đã nộp HNX ngày 23/10, trước giờ khoá. Điểm này chưa xác minh được timestamp.
- **Quyết định không phụ thuộc HNX:** kết quả Q3 đã suy ra được từ tài liệu công khai trước giờ khoá.
  - **20/10 16:20**, SXKD 9T: LNTT 9T **208,21 tỷ**. Trừ H1 tự lập 181,85 ⇒ LNTT Q3 ≈ **26,4 tỷ**. Bán 9T 11.989,49 t ⇒
    Q3 bán 2.369 t.
  - **22/07**, SXKD 6T: ban lãnh đạo đặt chỉ tiêu **LNTT 6 tháng cuối năm chỉ 40 tỷ**.
  - **09/09**, SXKD T8: tháng 8 khai thác chỉ đạt 71,7% kế hoạch, giảm 524 t so cùng kỳ vì mưa.
  - Thị trường đã phản ứng: ngày 21/10, giá giảm từ 16.200 xuống 15.300 (−5,6%) với KL 3,1 tr cp, gấp khoảng 6 lần
    phiên 20/10 [BQ].
- ⇒ Ghi vào sổ chấm `CYC-DRI-20261026`: F (LNST ≥ 50 tỷ, p 0,70; biên LNST mẹ ≥ 27%, p 0,70) đều **TRƯỢT**, nhưng gắn nhãn
  **`blind_scorable: no — kết quả công khai trước khoá (SXKD 9T 20/10)`**. Không dùng hai dự báo này làm bằng chứng về kỹ
  năng dự báo mù. Lỗi thật nằm ở **thu thập thông tin**: cả khối mù lẫn DD đều không đọc báo cáo SXKD tháng.

## 3. Lệch H1: điều chỉnh soát xét, không phải đọc scan sai
| | H1 trong DD (Q2 tự lập) | H1 soát xét [SX] | 9T − Q3 in [BCTC3] |
|---|---|---|---|
| Doanh thu thuần | 489,92 | 489,92 | 486,00 |
| LNTT | 181,85 | **177,36** | 176,56 |
| LNST mẹ | 146,71 | **142,21** | 141,77 |
- **LNST: −4,50 tỷ là điều chỉnh soát xét.** CV 52/CV-CT ghi rõ: LNST HN soát xét thấp hơn bản tự lập 4.495.545.192 đ
  (−3,07%), do "điều chỉnh tăng giá vốn hàng bán liên quan đến các giao dịch mua bán nội bộ trong tập đoàn". Biên gộp H1
  đúng ra là **40,6%**, không phải 41,6%. DD đọc đúng bản tự lập; cái sai là không dùng bản soát xét có sau đó.
- **Phần dư (DT −3,92, LNST mẹ −0,44)** xuất hiện ở mọi dòng, trừ thuế hoãn lại. Giải thích hợp lý nhất: cột Q3 quy đổi KQKD
  của công ty con Lào theo tỷ giá bình quân 9T (VND/LAK 0,8431), khác tỷ giá áp cho H1.
  - Bằng chứng: doanh thu cao su tháng 7+8+9 trong báo cáo SXKD là 43,71 + 54,52 + 33,85 = **132,08 tỷ**, khớp đúng với
    9T − H1 soát xét (132,08). Không khớp với 136,00 trên BCTC.
  - Không có công bố hồi tố. Chỉ có tái phân loại số đầu kỳ theo TT99 (phi hồi tố) và EPS Q3/2025 trình bày lại 533 → 519
    vì trừ quỹ khen thưởng phúc lợi.
- **Q3 "kinh tế" dùng cho phân tích:** DT 132,08 · giá vốn 86,56 · biên **34,5%** · LNTT 26,36 · LNST mẹ 25,54.

## 4. Giải phẫu Q3
### 4.1 Giá vs sản lượng [SXKD; `model_q3.py` mục 1]
| | Tấn bán | USD/t | tr đ/t | DT cao su (tỷ) |
|---|---|---|---|---|
| Q3/2025 | ~4.242 [UL: suy từ % YoY] | – | ~43,3 [UL] | 183,60 |
| Q2/2026 | 3.841 | 2.109 | 54,7 | 210,15 |
| **Q3/2026** | **2.369** | **2.195** | **55,75** | 132,08 |
- So Q3/2025: sản lượng **−44%**, giá **+29%** ⇒ DT −26%. So Q2/2026: sản lượng −38%, giá +4% (USD) / +2% (VND).
- **Giá không phải vấn đề.** Giá 55,75 tr/t khớp đúng giả định 55,7 trong DD. **Sản lượng bán là nguyên nhân chính.**

### 4.2 Vì sao sản lượng bán thấp: giữ hàng + mưa
- Khai thác Q3 = 8.617 − 5.236 = **3.381 t**. Mua ngoài 666 t. Chế biến **4.086 t**. Chỉ **bán 2.369 t** [SXKD].
  ⇒ thành phẩm tăng khoảng **1.717 t** [UL]. Khớp với giá trị thành phẩm trên BCTC: 64,99 (30/06) → **138,81 tỷ**
  (30/09) [SX, BCTC3].
- Mưa kéo dài: khai thác tháng 8 đạt 71,7% kế hoạch (−524 t so cùng kỳ), tháng 9 đạt 78,7% (−138 t).
- Kế hoạch Q4 của ban lãnh đạo [SXKD 9T]: bán **4.168 t @ 58,97 tr/t**, khai thác 4.909 t ⇒ hàng tồn sẽ được xả trong Q4.

### 4.3 Vì sao biên gộp giảm từ 40,6% (H1 soát xét) xuống 34,5%
Giá vốn/tấn: Q3 **36,54 tr** so với H1 30,23 tr (+21%); bình quân 9T 31,48 [`model_q3.py` mục 2]. Ba cơ chế, chưa tách được
bằng số vì BCTC không thuyết minh giá vốn theo yếu tố hằng quý:
1. **Chi phí cố định chia trên ít tấn bán hơn.** Khấu hao vườn cây 9T 26,2 tỷ [BCTC3 5.8]. Lao động trực tiếp 2.232 người
   [SXKD]. Mưa làm giảm sản lượng cạo nhưng không giảm tiền lương.
2. **Tỷ trọng mủ mua ngoài cao hơn:** 16% sản lượng chế biến Q3, so với 11% ở H1. Mủ mua ngoài có biên mỏng [UL].
3. Chi phí SXKD dở dang (58,45 tỷ tại 30/06) đã kết chuyển vào giá thành trong Q3; còn lại 26,88 tỷ.
- **Không phải do trích thưởng.** Phải trả NLĐ 28,33 (30/06) → **25,75 tỷ** (30/09). Chi phí phải trả **0**. Quỹ khen thưởng
  phúc lợi 16,68 tỷ trích từ LNST theo nghị quyết ĐHĐCĐ, không đi qua giá vốn.
  ⇒ **Thưởng 2026 vẫn chưa trích**, nên rủi ro Q4 gánh chi phí thưởng còn nguyên.
- Báo cáo SXKD tháng cho thấy tháng 9 **lỗ khoảng 8 tỷ LNTT** (luỹ kế 8T ước 216,27 → 9T 208,21). Đây là số ước tính của
  ban lãnh đạo, nhiều khả năng là điều chỉnh cuối quý.

### 4.4 Tiền, vay, bên liên quan, Lào [BCTC3]
| Mục | 30/09/2026 | Mốc so sánh | Đánh giá |
|---|---|---|---|
| CFO 9T | **125,28** | LNST 9T 167,44 ⇒ **0,75x**; H1 154,45 ⇒ **CFO Q3 ≈ −29 tỷ** [tính] | Phải trả giảm 68,5 tỷ; tồn kho tăng; thuế đã nộp 25,1 |
| Tồn kho | 183,87 (thành phẩm 138,81; dở dang 26,88; NVL 18,18) | 01/01: 176,05 | Không trích dự phòng. Không công bố tấn |
| Vay | NH 87,04 + DH 20,60 = **107,64** | 01/01: 104,71 | LaoViet 34,70 (10,95%); VietinBank Lào 37,99 (LAK 11% / USD 6%); VietinBank ĐL 9,17; DH VietinBank Lào 25,77 gốc (12,6%, tới 2031) |
| Tiền + TG có kỳ hạn NH | 72,57 + 271,81 = 344,38 | | Net cash sau vay **236,7**; sau cổ tức phải trả 73,92 (chưa chi) ⇒ **162,8 tỷ** (DD dùng 191,5) |
| **Dakruco** | cho vay **40 tỷ** (không đổi từ 30/06; 01/01 là 80); lãi Q3 0,907 tỷ (~9%/năm) | | **Không vay thêm, không gia hạn ⇒ trigger THOÁT không kích hoạt.** Phải trả cổ tức Dakruco 32,94 tỷ |
| Quỹ TDND Cao su ĐL | TG 70 tỷ; góp vốn 3 tỷ | 01/01: 50 | Bán niên ghi "chưa xác định được giá trị thu hồi" khoản góp 3 tỷ ⇒ WARNING nhỏ |
| **Tiền gửi tại Lào** | Có kỳ hạn: VietinBank Lào **128,22** + LaoViet 26,44 = 154,66. Không kỳ hạn: VietinBank Lào 30,55 + LaoViet 11,51. Ngoại tệ không kỳ hạn **2.351.856 USD = 60,48 tỷ** | 30/06 có kỳ hạn: 159,10 + 27,13 = 186,22 | Có kỳ hạn ở Lào giảm 31,6 tỷ trong Q3. Tăng tương ứng không nằm ở NH Việt Nam (QTDND/Agri/Vietin ĐL không đổi) ⇒ nhiều khả năng đã dùng cho vốn lưu động [UL]. Không thấy hạn chế chuyển tiền. Nguyên tệ/kỳ hạn không công bố |
| CLTG trong VCSH | −370,84 | 30/06: −355,0 (bản tự lập) | −15,8 tỷ/quý, chưa tới ngưỡng xấu 30 |
| LNST riêng công ty mẹ Q3 | 0,15 tỷ (Q3/2025: 1,00) | | Lỗ tỷ giá; dòng LN từ Lào về mẹ vẫn yếu |

## 5. Chấm điểm
### (a) Checklist 25/10 (4 điểm, không sửa)
| Điều kiện | Thực tế | Kết quả |
|---|---|---|
| LNST Q3 < 22 tỷ ⇒ đề xuất bán 50% | 25,98 (in) / 25,54 (kinh tế) | **Không kích hoạt.** Biên an toàn 16–18% |

Ba điểm còn lại của checklist nằm trong file checklist. Tôi không chép lại; thực tế của chúng đã có ở bảng 4.4: không thu
nhập bất thường (TN khác 0,04 tỷ); CFO yếu; Dakruco không đổi.

### (b) Dự báo đã khoá và dự báo trong DD
| Dự báo | Thực tế | Sai |
|---|---|---|
| F khoá mù: LNST mẹ Q3 ≥ 50 tỷ (p 0,70) | 25,98 | **TRƯỢT** (Brier 0,49). **Không chấm là mù** (mục 2) |
| F khoá mù: biên LNST mẹ ≥ 27% (p 0,70) | 19,1% (in) / 19,3% (kinh tế) | **TRƯỢT** (Brier 0,49). **Không chấm là mù** |
| DD: LNST Q3 55–65 tỷ | 25,98 | −29 đến −39 tỷ (−53% đến −60%) |

**Phân rã sai số theo LNTT** [`model_q3.py` mục 3]. DD ngầm định LNTT 74,4 tỷ; thực 26,4 tỷ (kinh tế).
| Cơ chế | Δ LNTT |
|---|---|
| **Sản lượng bán** (DD giả định 3.750 t, thực 2.369 t) | **−31,3** |
| Giá | +0,0 |
| **Giá vốn/tấn** (33,11 → 36,54) | **−8,1** |
| BH + QLDN | +2,0 |
| Tài chính ròng (Dakruco giảm nợ còn một nửa; lỗ tỷ giá) | −3,5 |
| Khác (DD giả định +2,5; thực −0,4) | −2,9 |
| Thưởng | 0 (chưa trích) |
Phần còn lại −4,3 tỷ đến từ Q3 in 31,65 vs 26,36 kinh tế và làm tròn.

**Bài học cho `model.py`** (đề xuất, chưa sửa code):
1. **Nowcast quý bằng báo cáo SXKD tháng của chính DRI.** Báo cáo này có tấn bán, USD và LNTT luỹ kế ước tính, đăng khoảng
   ngày 10 tháng sau; báo cáo quý đăng khoảng ngày 20. Thiếu nguồn này thì không được ra dự báo quý.
2. **Sản lượng bán theo quý do quyết định bán hàng, không do mùa cạo.** DD đã chia đều "bán H2 = 16.900 − H1". Thực tế công
   ty giữ hàng. Cần mô hình hoá bằng hàng tồn: chế biến − bán.
3. **Giá vốn/tấn phải có phần cố định chia theo tấn bán**, không giữ cố định 33,11. Q3 có giá vốn/tấn cao nhất trong năm.
4. **Đọc kế hoạch "phấn đấu" của ban lãnh đạo làm cận dưới** (H2 LNTT 40 tỷ; Q4 22,57 tỷ). Lịch sử cho thấy DRI đặt kế hoạch
   thấp rồi vượt, nhưng DD bỏ qua hoàn toàn nguồn này.
5. **Dùng bản soát xét khi đã có**, thay cho bản tự lập.

### (c) Bảng "đổi gì khi Q3 ra" (§6b của REPORT.md)
| Quan sát Q3 | Ngưỡng | Thực tế | Bật? |
|---|---|---|---|
| LNST mẹ Q3 | < 22 | 25,98 | Không |
| | ≥ 70 và biên ≥ 33% | 25,98; 19,1% | Không |
| Thu nhập khác (thanh lý vườn) | > 10 | 0,04 | Không |
| Chi phí phải trả / phải trả NLĐ | tăng > 20 | 25,75 (30/06: 28,33) | Không. Thưởng **chưa** trích ⇒ rủi ro dời sang Q4 |
| **Tồn kho thành phẩm** | > 100 tỷ | **138,81** | **CÓ** ⇒ giữ hàng chờ giá; rủi ro nếu giá giảm |
| **CFO 9T** | < 0,8x LNST | **0,75x** | **CÓ** ⇒ nghiêng GIẢM |
| Dakruco / phải thu bên liên quan | tăng | 40 tỷ không đổi | Không |
| CLTG VCSH | xấu thêm > 30/quý | −15,8 | Không |

## 6. Mô hình chạy lại (`model_q3.py`)
### 6.1 Kịch bản Q4/2026 [UL — mức thưởng là giả định, không có số]
| | Tấn | Giá | Giá vốn/t | Thưởng trích | LNST Q4 | LNST FY26 |
|---|---|---|---|---|---|---|
| Bear | 3.500 | 52,0 | 36,5 | 25 | **13,7** | 181,2 |
| Base | 4.200 | 56,0 | 35,0 | 15 | **49,7** | 217,1 |
| Bull | 4.900 | 59,0 | 34,0 | 0 | **90,0** | 257,4 |
| Kế hoạch BLĐ | 4.168 | 58,97 | – | – | ~18,4 (LNTT 22,57) | ~186 |
- Q4/2025 LNST mẹ 40,6 tỷ [BQ `NP_P0`]. Q4 các năm trước 2023–2025 nằm khoảng 31–41 tỷ [BQ].
- Kế hoạch BLĐ cho LNTT Q4 chỉ 22,57 tỷ dù DT 257 tỷ. Như vậy hoặc kế hoạch rất thận trọng như trước (H1 đã đạt 122% kế hoạch LNTT CẢ NĂM),
  hoặc BLĐ đã tính sẵn chi phí lớn cuối năm (thưởng, lương 3P). Tôi không phân biệt được hai khả năng này bằng dữ liệu
  hiện có.
- **Run-rate LN:** 221 tỷ trong DD nay thành **FY26E 181–257, base 217** [UL]. Năm 2026 vẫn là năm đỉnh. Q3 không phải
  dấu hiệu đảo chiều giá; giá bán Q3 còn tăng.

### 6.2 Định giá chu kỳ (cùng phương pháp `model.py`, cập nhật số)
Thay đổi so với DD:
- Net cash 191,5 → **162,8**: cổ tức chưa chi; CFO Q3 âm.
- Chi phí BH+QLDN, tài chính ròng và thuế lấy theo Q3 × 4.
- Phần "LN vượt chuẩn" neo theo FY26E 217,1 thay vì 221,6.

| Kịch bản (w) | LNST chuẩn | PE lõi @14.700 | FV/cp | (DD cũ) |
|---|---|---|---|---|
| Bear (25%) | 60,6 | 16,9x | **8.029** | 8.839 |
| Base (50%) | 80,9 | 12,3x | **10.878** | 11.686 |
| Bull (25%) | 101,2 | 9,6x | **14.339** | 15.142 |
| **Kỳ vọng** | | | **11.031 (−25%)** | 11.838 (−19%) |
- FV giảm khoảng 800 đ/cp. Khoảng 390 đ đến từ net cash. Phần còn lại đến từ thu nhập tài chính thấp hơn sau khi Dakruco
  trả 40 tỷ. Giả định giá giữa chu kỳ **không đổi** vì giá Q3 không mới.
- Định giá vẫn nhạy nhất với giả định RSS3 giữa chu kỳ. Q3 không cung cấp thông tin mới về điểm này.

## 7. Khuyến nghị
**Theo kế hoạch đã duyệt (`kb/projects/dri-triggers-20261027.md`): GIỮ.**
- Không dòng nào ở GIẢM 50% hay THOÁT chạm.
- Chỉ báo Bobby (Qingdao, lốp, TSR20) **chưa cập nhật** trong job này nên không chấm.
- Không bot nào tự bán: điều kiện chạm thì Mike báo user và đưa lệnh qua plan như thường lệ.

**Ý kiến riêng (đề xuất ngoài kế hoạch, user quyết): GIẢM 50% chủ động trong phiên tới, không đợi 15.100.**
- **Ủng hộ giảm:**
  - Hai cờ §6b đã bật.
  - FV −25%.
  - Thưởng chưa trích, Q4 có thể gánh.
  - BLĐ tự đặt LNTT Q4 thấp (22,57).
  - LN riêng công ty mẹ gần 0, nên cổ tức 2026 phụ thuộc dòng LN chuyển từ Lào.
  - Cổ tức 2025 (1.000 đ) đã chốt quyền, nên bán bây giờ không mất cổ tức đó. Ngày chốt cần Mike/Mafee xác nhận với sổ
    broker; DD ghi ex khoảng 22/09.
- **Ủng hộ chờ:**
  - Q3 thấp do giữ hàng (~1.717 t, 139 tỷ). Q4 bán ra ở giá kế hoạch 59 tr/t thì Q4 có thể đẹp (base 50 tỷ).
  - DRI dự kiến chuyển sàn HOSE trong Q4/2026. Đây là catalyst thanh khoản [SXKD 9T].
  - Thị trường đã trừ một phần: giá giảm 16.200 → 14.700 kể từ 20/10.
- **Cân nhắc:** vị thế nhỏ (3.800 cp ≈ 55,9 tr đ), thanh khoản không phải ràng buộc. EV âm khoảng 25% so với FV. Hai tín
  hiệu chất lượng LN đều xấu. ⇒ Giảm nửa bây giờ và giữ nửa còn lại cho catalyst Q4/HOSE, với mốc 15.100 như đã duyệt.
  Nếu user muốn bám đúng kế hoạch thì GIỮ cả 3.800 cp cũng nhất quán với luật; chi phí kỳ vọng nhỏ do vị thế nhỏ.
- **Mốc tiếp theo:** báo cáo SXKD tháng 10 (~10/11) cho biết tấn bán tháng 10 và LNTT luỹ kế. Đây là nowcast Q4 sớm nhất.
  Nếu tháng 10 bán < 1.000 t hoặc LNTT luỹ kế 10T giảm so với 9T ⇒ chuyển sang GIẢM nốt.

## 8. ⚠️ WARNING pháp lý / quản trị (chỉ cảnh báo)
1. Cho Dakruco vay còn 40 tỷ, tài sản đảm bảo là chính cổ phiếu DRI. Không đổi trong Q3; Dakruco đã trả 40 tỷ trong H1 (tích cực).
2. Tiền gửi ở Lào khoảng 197 tỷ, cả có kỳ hạn lẫn không kỳ hạn [tính từ BCTC3]. Thuyết minh không công bố nguyên tệ, lãi
   suất, kỳ hạn. Đây là thiếu minh bạch, chưa phải dấu hiệu vi phạm.
3. Khoản góp vốn 3 tỷ vào Quỹ TDND Cao su ĐL: kiểm toán viên bán niên ghi chưa xác định được giá trị có thể thu hồi.
4. BCTC có lỗi trình bày nhỏ: dòng tiền gửi LAK quy đổi sai tỷ giá; chi phí đi vay Q3/2025 trên thuyết minh 0,55 tỷ trong
   khi KQKD ghi 1,21 tỷ. Không trọng yếu, nhưng cho thấy chất lượng BCTC quý (chưa soát xét) thấp.
5. Kế hoạch chuyển sàn HOSE trong Q4/2026 và dự án cà phê liên kết với Daknoruco/Dakruco (bên liên quan) đang được đánh
   giá ⇒ cần theo dõi giao dịch bên liên quan mới.

## Nguồn
- dri.com.vn: `/bao-cao-tai-chinh-cong-ty-me-va-hop-nhat-quy-3-nam-2026-…-13627.html` (PDF `2.VI_BaoCaoTaiChinh_Q3_2026_HopNhat.pdf`,
  `3.VI_GiaiTrinhLienQuanDenBCTC_Q3_2026.pdf`); `…-9-thang-nam-2026-13623.html` (`BC 29.2026 CBTT.Bao cao 9 thang 2026 (f).pdf`);
  tháng 07 (13604), tháng 08 (13607), 6 tháng (13599), quý 1 (13565); bán niên soát xét (13605).
  Cache: `/tmp/dri_q3/`, ảnh trang `/tmp/dri_q3_img/`. Bản sao cục bộ: `sxkd9t.pdf`, `3.VI_GiaiTrinh…Q3_2026.pdf`, `sx_gt.pdf`.
- Trích số chi tiết kèm trang: `extract_q3_bctc.md`.
- BQ `tav2_bq.ticker` (giá tới 26/10), `tav2_bq.ticker_financial` (Q4 lịch sử), truy vấn 27/10.
