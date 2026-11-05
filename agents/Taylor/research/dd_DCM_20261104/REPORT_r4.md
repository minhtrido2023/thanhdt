# DD — DCM (CTCP – Tổng Công ty Phân bón Dầu khí Cà Mau, PVCFC) · as-of 05/11/2026 · **VÒNG 4 (r4 = r3 + đường giá khí theo hợp đồng)** · job `Taylor_20261104_170125`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. r1 `REPORT.md`, r2 `REPORT_r2.md`, r3 `REPORT_r3.md` giữ nguyên.
> **Câu hỏi của user (05/11 00:00):** "DCM có hợp đồng mua khí từ mỏ hợp tác với Malaysia (PM3-CAA). Hợp đồng đó sẽ thay đổi giá khí đầu vào của DCM trong tương lai." r4 kiểm giả thuyết này bằng văn bản hợp đồng gốc, rồi thay đường giá khí trong mô hình.
> **Nguồn mới (gốc, ưu tiên):**
> - **[PL12]** `src/gas/egm2026_tailieu.pdf` — Tài liệu ĐHĐCĐ bất thường 2026 của PVCFC (Vietstock static2, xác thực eoffice.pvcfc 0570/CV-VPHĐQT). Gồm Phần 4 Tờ trình và Phụ lục **"DỰ THẢO Sửa đổi bổ sung số 12"** HĐ 3918/HĐ-DKVN (pdf p22–34).
> - **[PL11]** `src/gas/egm2025_update_en.txt` (tài liệu ĐHĐCĐ bất thường 05/11/2025, pdf p15–18, 25–26).
> - **[BB25]** `src/gas/dl_1844450.txt` — Biên bản + Nghị quyết ĐHĐCĐ bất thường 05/11/2025 (fireant mirror). Kết quả biểu quyết ở pdf p4–5; phần hỏi đáp (PL I) ở pdf p8.
> - **[GAS-NQ]** NQ HĐQT PV GAS 27/NQ-KVN (16/03/2026, HOA Nam Du–U Minh) và 34/NQ-KVN (19/04/2026, GSPA Nam Du–U Minh) — `src/gas/dl_1865434.txt`, `dl_1309972.txt`. Hai NQ **không đính kèm điều khoản giá**.
> - **[JSE]** Jadestone RNS 20/04/2026 (ticker.app): DCQ 80 MMscf/d; take-or-pay 90% DCQ; "fixed annual escalation"; khí đầu cuối 2028; 2P 32 MMboe. Không nêu số USD/MMBtu.
> - **[PET]** Petronas media release 10/04/2025: KPA gia hạn PSC + UGSA PM3 CAA tới 31/12/2047, cấp khí cho VN qua Cà Mau; "enhanced terms", **không công bố giá**.
> - **[VDSC]** `txt/VDSC_Q3_2026.txt` p5–7, Bảng 3–4 (ghi nguồn "DCM, CTCK Rồng Việt") — **thứ cấp**.
>
> **Thứ tự chạy, trung thực:** tôi **đã biết giá 33.000 và nhãn ĐẮT/có điều kiện từ r1–r3** trước khi bắt đầu r4. `calc/model_r4.py` không nhận giá/vốn hoá/PE. Khoá md5 lúc **00:08:38 ICT 05/11** (`calc/LOCK_r4_md5.txt`), sau đó mới chạy `calc/compare_px_r4.py`. Tâm không được dịch theo giá: mọi thay đổi r3→r4 đều xuất phát từ văn bản hợp đồng hoặc giả định gắn nhãn; chiều tác động (giảm tâm) ngược hướng giá.
> Giả định tự đặt gắn **(ước lượng)**. Mọi thay đổi so r3 có dòng "cơ sở dữ liệu + trang nguồn".

## 0. Kết luận

### Giả thuyết của user: **NỬA ĐÚNG**
- **ĐÚNG:** hợp đồng mua khí của DCM (3918/HĐ-DKVN) đã được sửa và **sẽ đổi giá khí đầu vào từ Q4/2028**.
- **NHƯNG thay đổi giá không nằm ở PM3-CAA.** Nó đến từ nguồn **Nam Du–U Minh (Lô 46/07 & 51)**, đưa vào hợp đồng qua **Sửa đổi bổ sung số 12** [PL12]:
  - Giá Nam Du–U Minh **CỐ ĐỊNH, KHÔNG gắn dầu**: **P = 10,39 × (1+2,25%)^t USD/MMBTU** tại mỏ, chưa VAT [PL12 p31, Đ9.1].
  - Mốc t=0 là 01/01/2028 nếu khí đầu về trước hoặc đúng 31/12/2028.
- **Hai lần sửa đổi liên quan PM3-CAA KHÔNG chạm giá:**
  - **SĐBS 11** (ký 18/11/2025 [PL12 p22]) **chỉ chuyển Bên bán từ PVN sang PV GAS** [PL11 p17–18, Điều 2–4]: không có điều khoản giá, khối lượng hay thời hạn mới.
  - **Gia hạn PSC/UGSA PM3-CAA tới 2047** là hợp đồng **thượng nguồn** (Petronas–PVN–chủ mỏ) [PET]: không công bố giá. Không văn bản nào thấy có điều khoản "giá mới cho DCM có hiệu lực khi PSC gia hạn 2028".
- **Điều văn bản THỰC SỰ nói về PM3:**
  - Hợp đồng mua khí bổ sung từ Petronas **kết thúc cuối năm 2027** [BB25 p8, trả lời câu 1].
  - Sản lượng PM3 chia **50% Petronas / 50% PVN**; PVN đã mua lại phần của Petronas [BB25 p8].
  - **Giá phần khí PM3 từ 2028 trở đi: KHÔNG CÔNG BỐ** ở bất kỳ nguồn gốc nào tìm được.
  - Công thức PM3 hiện hành ("46% MFO" cho phần quyền nhận PVN, "12,7% → 13,7% Brent" cho phần Petronas) **chỉ có ở CTCK** [VDSC], không có trong văn bản hợp đồng tìm được.

### Định giá r4 (mù giá đầu vào; Brent 67,8 = TB 2016–25; khung r/thuế/KTPL/ADMIN/trọng số giữ nguyên r3)
- **Kỳ vọng 23.644 đ/cp** (r3: 27.021; **Δ −3.377**) = 0,50×CYC 24.640 + 0,30×ADMIN 24.640 + 0,20×STRUCT 19.661.
- Lưới đối xứng 270 ô (biên 138/179/220): **P10 19.888 · P25 20.974 · P50 23.376 · P75 25.561 · P90 26.993**.
- Chiết khấu thanh khoản ≈ 0 (r3, ADV 74 tỷ) ⇒ sau chiết khấu thanh khoản vẫn **23.644**.
- **Cầu nối r3 → r4** (`calc/model_r4_out.txt` dòng 4):
  - **(1) Hiệu chỉnh độ dốc proxy: +2.077.** Công thức hợp đồng nhạy Brent hơn proxy 25×(2,5+0,06×Brent): 2,1 vs 1,5 USD/t mỗi USD Brent. Ở Brent dài hạn 67,8 (thấp hơn TB 2021–25 là 80,5, giai đoạn hồi quy hấp thụ) nên lợi.
  - **(2) Đường giá khí theo hợp đồng 2027–2034: −5.454.** Đây là trung bình hai cận giá phần PM3 sau 2027: −3.327 nếu rẻ ngang quyền nhận PVN, −7.581 nếu giữ 13,7% Brent. Nguồn chính là **khí Nam Du 10,39 USD/MMBTU cố định, đắt hơn khí PM3 khi Brent < ~95**, và chiếm ~54% khí của DCM 2029–33.
- **Hướng tác động của hợp đồng theo Brent — KHÔNG đối xứng như r3 viết:**
  - r3 (theo VDSC) cho rằng Nam Du **thay khí Petronas** ⇒ hoà vốn ở Brent 75,8.
  - Văn bản [PL12 Đ10.1(b), Đ4.1] **không nói Nam Du thay riêng phần Petronas**. Nguồn khí được **phân bổ theo tỷ trọng tiêu thụ**, phần PM3 còn lại vẫn là PM3 nói chung.
  - So với hỗn hợp PM3 (≈50% giá rẻ gắn MFO + 50% gắn Brent), điểm hoà vốn của Nam Du **cao hơn nhiều** (xem §A.4).
- **So giá (sau khoá):**
  - 33.000 cao hơn tâm r4 **+39,6%**. Nhãn **ĐẮT** ở cả 4 lưới: đối xứng 3 mức, đối xứng 5 mức (P90 29.334), lưới 270 cũ, và lưới đối xứng × 4 mức Brent.
  - Giá hàm ý biên urê–khí (proxy) dài hạn **≈306 USD/t** (kỳ vọng; 100% CYC ≈270) ở Brent 67,8. Mốc so sánh: TB 2016–25 = 179, năm 2025 = 257.
  - Ở biên 260 (cận trên dải bền của Bobby), giá vẫn cao hơn giá trị **+11,5%**.
- **⚠️ Mức chắc chắn của tâm r4 thấp hơn r3 ở khâu khí.** Ba ẩn số quyết định là giá phần PM3 sau 2027, tỷ trọng Nam Du thực tế, và Brent. Dải tâm khi đổi từng giả định: **21.517 (PM3 giữ 13,7% Brent) … 26.843 (Nam Du chỉ 30%)**. Ngay cả đầu cao 26.843 vẫn thấp hơn giá 33.000 (−18,7%).

## A. MỚI — Hợp đồng mua bán khí 3918/HĐ-DKVN: văn bản thực sự nói gì

### A.1 Chuỗi văn bản (sự kiện)
| Văn bản | Ngày | Nội dung chạm DCM | Nguồn |
|---|---|---|---|
| HĐ 3918/HĐ-DKVN "HĐ mua bán khí PM3 CAA và Lô 46 Cái Nước" | 23/5/2012 | HĐ gốc PVN → PVCFC; 10 lần sửa đổi 2013–2023 | [PL11 p15] |
| NQ HĐTV PVN 7268/NQ-CNNL | 21/8/2025 | Đổi mô hình: PVN mua khí PM3 (quyền nhận PVN) + mua bổ sung Petronas, bán toàn bộ cho PV GAS | [PL11 p15] |
| KPA gia hạn PSC + UGSA PM3 CAA | 10/4/2025 | Gia hạn tới 31/12/2047; giá không công bố | [PET] |
| **SĐBS 11** | ĐHĐCĐ thông qua 05/11/2025 (99,93% phiếu không liên quan; PVN không biểu quyết); **ký 18/11/2025** | **Chỉ đổi Bên bán PVN → PV GAS**; mọi điều khoản khác giữ nguyên (Đ4.4) | [PL11 p17–18], [BB25 p5], [PL12 p22] |
| NQ HĐQT PV GAS 27/NQ-KVN · 34/NQ-KVN; NQ HĐTV PVN 1811 (13/3/2026), 3040/NQ-CNNL (17/4/2026) | 16/3 · 19/4/2026 | HOA và GSPA Nam Du–U Minh giữa PV GAS và Mitra Energy (Jadestone) + PVN | [GAS-NQ] |
| GSPA thượng nguồn Nam Du–U Minh | ký 20/4/2026 | DCQ 80 MMscf/d; take-or-pay 90%; leo thang cố định | [JSE] |
| **SĐBS 12 (DỰ THẢO trình ĐHĐCĐ bất thường 2026)** | ĐHĐCĐ 23/9/2026 (chỉ nguồn thứ cấp xác nhận thông qua) | Đổi tên HĐ thành **"HĐ mua bán khí cho Nhà máy Đạm Cà Mau"**; thêm nguồn Nam Du–U Minh, giá, khối lượng | [PL12 p22–34] |

### A.2 Điều khoản SĐBS 12 (trích văn bản, dự thảo)
- **Giá Nam Du–U Minh** [p31, Đ9.1]:
  - **Pn3 = P0 × (1+I)^t**, trong đó **P0 = 10,39 USD/MMBTU tại mỏ, chưa VAT**; **I = 2,25%/năm cố định**.
  - Mốc trượt giá: 01/01 của năm có khí đầu, nếu khí đầu về trước hoặc đúng 31/12/2028; nếu sau 31/12/2028 thì tính từ ngày khí đầu.
  - Hệ số quy đổi GJ→MMBTU là 0,94781712.
  - **Không có sàn/trần, không gắn Brent/MFO.**
  - Cộng thêm **cước Tp** (theo Đ9.1 hiện hữu; số không có trong SĐBS 12).
- **Giá khí giao thiếu** [p31, Đ9.2]:
  - DP1 = 0,75×Pn1 + Tp (khí quyền nhận PVN); DP2 = 0,75×Pn2 + Tp (khí bổ sung); **DP3 = 0,80×Pn3 + Tp** (khí Nam Du–U Minh).
  - *Đây là nơi duy nhất văn bản nhắc tới Pn1, Pn2 (giá hai nguồn PM3), và chỉ dẫn chiếu "xác định theo Điều 9.1" của HĐ gốc — công thức không được trích.*
- **Khối lượng** [p26–28]:
  - **LKN 495 triệu Sm3/năm; LKNTT (bao tiêu) 445,5 triệu Sm3 (90%)** đến 24:00 ngày 24/4/2032.
  - LKNTT Nam Du–U Minh ở giai đoạn bình ổn **269,74 triệu Sm3** (= 60,5% LKNTT). Bao tiêu Nam Du tính hằng tháng ở mức **70% luỹ kế**.
  - **LKNTĐ 1,5 triệu Sm3/ngày @37,3 MJ/Sm3**, trong đó **Nam Du 0,81** (54%).
  - Khí nhận trước của Nam Du được khấu trừ ≤15% LKNTT năm sau.
  - **Từ 25/4/2032: lượng khí do Bên bán thông báo**, tuỳ cam kết của chủ mỏ ⇒ sau 2032 **không còn khối lượng cam kết**.
- **Thời điểm** [p29–30]:
  - Khí Nam Du đầu tiên **không muộn hơn Q4/2028**. Trễ thì phạt giao thiếu áp từ 01/01/2029.
  - Vận hành thử 30 (+10) ngày ở **97%** giá; tăng trưởng 30 ngày.
  - Bình ổn tối thiểu kết thúc ở mốc sớm hơn của **55 tháng** hoặc **120,45 bscf** luỹ kế.
  - Khí sai đặc tính được trả 90% giá.
- **Thời hạn** [p26, Đ3.3]: hết hạn vào ngày **muộn nhất** của (i) HĐ PM3 CAA PVN–PV GAS, (ii) GSPA Nam Du–U Minh, (iii) 24/4/2032.
- **Phân bổ** [p32, Đ10.1(b)]: lượng khí trong tháng của các nguồn xác định được phân bổ cho Bên mua và các hộ tiêu thụ khác (GPP Cà Mau, Điện Cà Mau 1&2) **theo tỷ trọng tiêu thụ thực tế**.
- **Thanh toán Nam Du** [p33]: hoá đơn bằng USD, trả bằng VND theo tỷ giá bán VCB lúc 10:00 trước ngày thanh toán ⇒ **DCM chịu rủi ro tỷ giá** trên phần khí này.
- **Hiệu lực** [p34]: từ ngày ký hoặc ngày Bên mua phê duyệt, tuỳ ngày nào đến sau.

### A.3 Cơ cấu nguồn khí theo năm — số HỢP ĐỒNG vs suy luận
| Năm | PM3 – quyền nhận PVN | PM3 – phần Malaysia (Petronas) | Nam Du–U Minh | Căn cứ |
|---|---|---|---|---|
| 2026–27 | ~50% @46% MFO **[VDSC]** | ~50% @12,7% (2026) / 13,7% (2027) Brent **[VDSC]** | 0 | 50/50 [BB25]; giá [VDSC] |
| 2028 | phần còn lại | **HĐ mua bổ sung Petronas hết cuối 2027 [BB25]**; giá 2028+ **không công bố** | ≤ Q4 ⇒ ~13,5% năm **(ước lượng)** | VDSC ghi 35% cho 2028 — **không khớp** hạn khí đầu Q4/2028 |
| 2029–33 | ~23% (ước lượng: (1−0,54)×50%) | ~23% (ước lượng) | **54%** (= 0,81/1,5 LKNTĐ [PL12 p28]); bao tiêu ≈ 269,74/495 = 54,5% | VDSC: 50%→60%, Petronas 0% |
| 2034 | | | ~27% (ước lượng; suy giảm; trữ lượng 4,44 tỷ Sm3 / ~0,7 tỷ Sm3/năm ≈ 6,3 năm) | Tuổi Trẻ/PVN 20/04/2026 (thứ cấp) |
| 2035+ | **không có cam kết** sau 25/4/2032 | | 0 | (ước lượng) quay về 50% PVN + 50% @13,7% Brent |

- **VDSC "Petronas 50% → 15% → 0%"** là **suy luận của CTCK**: không có văn bản nào nói phần Malaysia biến mất.
- Theo [BB25], sản lượng PM3 chia 50/50 theo chủ quyền, và [PET] UGSA gia hạn vẫn cấp khí PM3 cho VN qua Cà Mau tới 2047. Phần Malaysia **vẫn tồn tại**; cái mất đi chỉ là HĐ mua bổ sung **hiện hành** (giá 12,7–13,7% Brent).
- **Elibook 06/10/2026 (thứ cấp, chưa kiểm):** ban lãnh đạo cam kết giá Nam Du giai đoạn 2028–2034 "không vượt giá khí Petronas hiện tại". Không có trong dự thảo SĐBS 12 ⇒ **không vào mô hình**.

### A.4 Giá khí hiện hành thực tế vs công thức vs proxy (câu c)
- **Hiệu chỉnh định mức khí** (`calc/model_r4_out.txt` dòng 1):
  - Cách tính: tiền khí TM38 (9T/25 PVN 3.109,5 + PV GAS 3,4; 9T/26 PV GAS 4.258,1 + PVN 22,4 tỷ [BCTC Q3/26 pdf p42]) ÷ sản lượng 9T (ước lượng 700–750 kt) ÷ giá công thức trước VAT gồm cước (Brent 2025 = 69,0; 9T/26 = 94,0).
  - Kết quả: **21,1–22,8 MMBtu/t**, cả hai năm khớp nhau ⇒ dùng **22 (ước lượng)**; độ nhạy 20/25: −157 / +236 đ/cp.
  - *Không chắc: TM38 có gồm VAT không; sản lượng 9T là ước lượng.*
- **Proxy của Bobby so với công thức hợp đồng 2026** (USD/t urê, định mức 22):

  | Brent | Proxy 25×(2,5+0,06B) | Công thức HĐ (CTCK) | Chênh |
  |---|---|---|---|
  | 67,8 | 164 | 168 | +4 |
  | 82 | 186 | 198 | +13 |
  | 90 | 198 | 215 | +18 |
  | 103 | 217 | 242 | +25 |

  - Mức proxy **khớp tốt ở Brent 60–70**, nhưng **độ dốc thấp hơn**: 1,5 so với 2,1 USD/t mỗi USD Brent.
  - Hệ số hiệu chỉnh: chi phí thực ≈ proxy × (1,02 @67,8 … 1,12 @103). Theo USD/MMBtu, proxy thấp hơn công thức 14–21%, nhưng bù lại bằng định mức 25 so với ~22.
- **Điểm hoà vốn của Nam Du so với khí PM3 thay thế** (giá tại mỏ, không cước):
  - **So với hỗn hợp PM3 50/50 @13,7%** (cận V2): 10,39 = 0,5×0,0648B + 0,5×0,137B ⇒ **B ≈ 103**.
  - **So với khí quyền nhận PVN** (cận V1): ⇒ **B ≈ 160**.
  - **So với riêng khí Petronas @13,7%**: **B ≈ 75,8** (đúng số VDSC).
  - Vì [PL12] phân bổ theo tỷ trọng tiêu thụ chứ không "thay riêng Petronas", điểm hoà vốn thích hợp là **~100+**, không phải 75,8. Thêm vào đó, giá Nam Du leo thang 2,25%/năm.
  - Hệ quả: **với Brent TB 10 năm, hợp đồng mới làm chi phí khí TĂNG; chỉ có lợi khi Brent bền ở ~100+.**

## 1–4. Bóc tách quý, chất lượng lợi nhuận, 12 mục Bobby, bảng cân đối — **KHÔNG ĐỔI so với r3** (xem `REPORT_r3.md` §1–4)
Chỉ cập nhật mục Bobby #3 "Giá khí & công thức" (r3 ghi "sàn/trần, take-or-pay: chưa tìm thấy"):
- **Sàn/trần:** không có cho Nam Du [PL12 p31].
- **Take-or-pay:** 90% LKN (445,5/495 triệu Sm3) tới 24/4/2032; Nam Du 269,74 triệu Sm3/năm, thanh toán 70% luỹ kế tháng [PL12 p26–27].
- **Bên bán:** PV GAS từ SĐBS 11 (ký 18/11/2025).
- **LNG:** văn bản không nhắc; [BB25] nói PV GAS là đầu mối mua khí từ chủ mỏ và "nguồn khác (như LNG)".

## 5. Định giá r4 [`calc/model_r4.py`, khoá md5 00:08:38 ICT 05/11 trước khi so giá]

### 5.1 Phương pháp
- **Khung r2/r3 giữ nguyên** (gọi lại `model_r2.ev_r2`, md5 không đổi): r 13,5% @ lãi huy động 7,40%; thuế 20% từ 2027; quỹ KTPL; ADMIN chuẩn hoá; dự án mới NPV 0; trọng số 0,50/0,30/0,20.
- **Thêm:** giá trị r4 = r2 + PV(Δ chi phí khí theo năm) sau thuế 20% và KTPL; cùng cộng vào mọi nhánh.
- **Δ biên năm y ở Brent B** (USD/t) = [proxy(B) − 22 × giá khí(y,B)] − độ lệch TB 2021–25 (−11,7). Phần trừ đi là chế độ mà hồi quy LNST~proxy đã hấp thụ (ước lượng: 2021–25 cùng cơ cấu 50/50 @12,7%).
- **Giữ cố định biên proxy dài hạn** (urê = proxy(B) + biên). Hệ quả: khi Brent cao, urê tăng 1,5 USD/t mỗi USD Brent theo proxy, còn chi phí thực tăng 2,1 ⇒ phần "độ dốc" âm. *Đây là giả định; nếu urê bám chi phí thực thì phần độ dốc bằng 0.*
- **Đường giá khí** (USD/MMBtu trước VAT gồm cước 1,14; định mức 22):
  - 2027: 50% @0,0648B (46% MFO; MFO = 5,72B/40,6 [VDSC]) + 50% @0,137B.
  - 2028: Nam Du 13,5%.
  - 2029–33: Nam Du 54% @10,39×1,0225^(y−2028).
  - 2034: Nam Du 27%.
  - Phần PM3 2028–34 lấy **trung bình hai cận, trọng số 0,5/0,5 (ước lượng)**: V1 = phần Malaysia rẻ ngang quyền nhận PVN; V2 = giữ 13,7% Brent.
  - 2035+: 50/50 @13,7%, vĩnh viễn.

Lịch giá (Brent 67,8; USD/MMBtu V1/V2; Δ biên USD/t V1/V2; dòng 2):

| Năm | 2027 | 2028 | 2029 | 2030 | 2032 | 2034 | 2035+ |
|---|---|---|---|---|---|---|---|
| Giá V1 / V2 | 7,99 / 7,99 | 6,35 / 8,46 | 8,90 / 10,03 | 9,03 / 10,15 | 9,30 / 10,42 | 7,56 / 9,34 | 7,99 |
| Δ biên V1 / V2 | +0,3 / +0,3 | +36 / −10 | −20 / −45 | −23 / −48 | −29 / −53 | +10 / −30 | +0,3 |

(Ở Brent 103, Δ biên 2030 là V1 +7 / V2 −31; năm 2035+ −25 do phần độ dốc.)

### 5.2 Kết quả & cầu nối
| Bước | Kỳ vọng (đ/cp) | Δ | Cơ sở dữ liệu + trang nguồn |
|---|---|---|---|
| r3 (= r2) | 27.021 | | `calc/model_r2_out.txt` |
| + hiệu chỉnh độ dốc proxy | 29.098 | **+2.077** | công thức PM3 [VDSC p6 Bảng 3–4]; định mức 22 từ TM38 [BCTC Q3/26 pdf p42] (ước lượng) |
| + đường khí hợp đồng 2027–34 (trung bình hai cận) | **23.644** | **−5.454** (V1 −3.327 / V2 −7.581) | Nam Du giá/khối lượng/thời điểm [PL12 p26–31]; Petronas hết 2027 [BB25 p8]; phân bổ theo tỷ trọng [PL12 p32] |
| **r4** | **23.644** | **−3.377** | |

| Nhánh | P | Giá trị đ/cp |
|---|---|---|
| CYCLICAL (biên 179) | 0,50 | 24.640 |
| ADMIN | 0,30 | 24.640 |
| STRUCTURAL (biên 125) | 0,20 | 19.661 |
| **Kỳ vọng** | | **23.644** |

### 5.3 Theo Brent (phẳng) và theo biên dài hạn (đ/cp; dòng 5–6)
| Biên dài hạn \ Brent | 67,8 | 82 | 90 | 103 |
|---|---|---|---|---|
| 150 | 21.499 | 21.097 | 20.869 | 20.499 |
| **179** | **23.632** | 23.230 | 23.002 | 22.632 |
| 220 | 26.648 | 26.245 | 26.018 | 25.648 |
| 242 | 28.266 | 27.864 | 27.636 | 27.266 |
| 260 | 29.590 | 29.188 | 28.960 | 28.590 |

- **Tách phần khí theo Brent:** cận V1 −1.250 / −1.209 / −1.186 / −1.148; cận V2 −5.504 / −6.350 / −6.829 / −7.606 (Brent 67,8 / 82 / 90 / 103). Riêng phần độ dốc: +2.077 / −242 / −1.553 / −3.683.
  - **Riêng đường hợp đồng (bỏ phần độ dốc)** thì Brent càng cao càng lợi: V1 −3.327 → +2.535 ở Brent 103. Nhưng phần độ dốc (giả định biên proxy cố định) lật ngược chiều tổng.
  - Nếu cơ cấu 2030 kéo dài vĩnh viễn (V1): −3.488 ở 67,8 / +1.978 ở 103.
- **Độ nhạy (dòng 7):**
  - Nam Du **30%** (nếu phân bổ theo tỷ trọng cả cụm Cà Mau, ~30% nhu cầu): **26.843** (24.129 ở Brent 103). Nam Du **60,5%**: 22.772.
  - Khí đầu trễ sang 2029: 24.412.
  - Chỉ V1: 25.771; chỉ V2: 21.517.
  - Định mức 25 / 20: 23.880 / 23.487.
  - Lãi huy động ±50bp (β1): 23.265 / 24.056; ±100bp: 22.916 / 24.504.

### 5.4 Lưới (dòng 8)
| Lưới | n | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|---|
| **Đối xứng 138/179/220** (thay lưới lệch lên) | 270 | 19.888 | 20.974 | 23.376 | 25.561 | 26.993 |
| Đối xứng 98/138/179/220/260 | 450 | 17.373 | 19.752 | 23.376 | 27.108 | 29.334 |
| Lưới 270 cũ (150/179/210) — để so | 270 | 20.712 | 21.819 | 23.376 | 25.081 | 26.244 |
| Đối xứng 3 mức × Brent 67,8/82/90/103 | 1.080 | 19.334 | 20.449 | 22.858 | 25.170 | 26.478 |

Lưới mở rộng lệch lên (150/179/220/260) của r3 **bỏ** theo yêu cầu.

### 5.5 So giá (sau khoá, `calc/compare_px_r4_out.txt`)
- 33.000 (đóng cửa 04/11/2026) so với tâm 23.644 = **+39,6%** (so với CYC +33,9%). **ĐẮT** ở cả bốn lưới.
- Biên dài hạn hàm ý của giá: **306 / 312 / 315 / 320 USD/t** (kỳ vọng) ở Brent 67,8 / 82 / 90 / 103; 270–281 nếu 100% CYC.
- Ở biên 260, giá cao hơn giá trị **+11,5 … +15,4%**; ở 220, **+23,8 … +28,7%**.
- **Thay đổi so với r3:** r3 gắn nhãn có điều kiện ("HỢP LÝ nếu biên ≥ ~233–260"). Sau khi đưa giá khí Nam Du vào, **điều kiện đó không còn trong dải bền của Bobby (180–260)**. Nhãn một chữ là **ĐẮT** và **bớt phụ thuộc lựa chọn biên** hơn r3.
- Chỉ đảo nếu tổ hợp các giả định thuận lợi cùng xảy ra: Nam Du ~30%, phần PM3 sau 2027 rẻ, **và** biên ≥ ~280.

## 6. Mốc khoá trước & điều kiện đổi nhận định (cả hai chiều)
Mốc Bobby giữ như r3 (24/11/2026; 03/01/2027; 04/03/2027; BCTC Q4/26 cuối 01/2027; nghị định thuế XK 0% hạn 31/03/2027). **Thêm các mốc khí:**
- **NQ/Biên bản ĐHĐCĐ 23/9/2026 + bản SĐBS 12 đã KÝ** (đối chiếu với dự thảo).
- **Công bố giá khí PM3 từ 01/01/2028** (UGSA gia hạn / HĐ PM3 PVN–PV GAS).
- **Ngày khí Nam Du đầu tiên** (≤ Q4/2028).
- **Thông báo lượng khí từ 25/4/2032.**

**Điều kiện NÂNG** (mỗi điều kiện ⇒ CHẠY LẠI mô hình):
- (a)–(d) như r3.
- (e) **Giá phần PM3 2028+ công bố ≤ mức quyền nhận PVN (46% MFO): +2.127** (V1 so với tâm).
- (f) Tỷ trọng Nam Du thực tế ≤ ~30% (phân bổ theo cụm): +3.199.
- (g) Brent bền ≥ ~100 **và** urê bám chi phí khí thực (phần độ dốc = 0).
- (h) Văn bản xác nhận cam kết "giá Nam Du không vượt giá Petronas hiện tại".

**Điều kiện HẠ:**
- (a)–(e) như r3; **(b) của r3 viết lại:** Nam Du ≥ 54% khi Brent < ~100 là **base hiện tại**, không còn là kịch bản hạ.
- (f) Giá phần PM3 2028+ ≥ 13,7% Brent: **−2.127**.
- (g) Sau 2032 không có khí thay thế giá ≤ PM3 (LNG): chưa mô hình hoá — phía hạ.
- (h) VND mất giá: hoá đơn Nam Du tính bằng USD (cùng chiều vị thế USD 189 triệu của DCM — tự phòng hộ một phần).

## 7. Pháp lý / quản trị — WARNING (không vào base)
Giữ nguyên các mục §7 của r3. **Thêm:**
- ⚠️ **Hợp đồng khí là giao dịch bên liên quan khép kín:** PVN → PV GAS (con PVN) → DCM (PVN 75,56%). SĐBS 11 được thông qua với PVN **không biểu quyết** — 30,98 triệu cp tham gia, 99,93% tán thành [BB25 p5].
  - ĐHĐCĐ 2025 **uỷ quyền HĐQT** tự sửa "nội dung cơ bản" của HĐ khi chính sách nhà nước thay đổi [BB25 p5, mục 2]. Tờ trình SĐBS 12 xin lại quyền này [PL12 p23].
  - ⇒ Các thay đổi giá khí sau này có thể **không qua cổ đông thiểu số**.
- ⚠️ **SĐBS 12 tôi đọc là DỰ THẢO.** Bản ký và kết quả biểu quyết 23/9/2026 chưa thấy ở nguồn gốc; chỉ có Elibook 06/10/2026 nói "thông qua ngày 23/9".
- ⚠️ Sau 24/4/2032 hợp đồng **không còn khối lượng cam kết** (Đ4.1(b)) ⇒ rủi ro nguồn cung dài hạn (PM3 suy giảm [BB25]).

## 8. Chưa xác minh (ưu tiên)
1. **Giá khí PM3 (Pn1, Pn2) từ 01/01/2028** — ẩn số lớn nhất của r4 (V1/V2 cách nhau 4.254 đ/cp). Công thức hiện hành (46% MFO / 12,7–13,7% Brent) chỉ có ở CTCK.
2. **Bản SĐBS 12 đã ký + NQ ĐHĐCĐ 23/9/2026** (tỷ lệ biểu quyết, khác biệt so với dự thảo).
3. **Tỷ trọng Nam Du thực tế của DCM** khi phân bổ theo tỷ trọng tiêu thụ (Đ10.1(b)) so với bao tiêu riêng 269,74 triệu Sm3. Độ nhạy 30%↔60,5%: 26.843 ↔ 22.772.
4. **Cước Tp** từ 2028 (VDSC 1,06 so với 1,14) — triệt tiêu trong Δ nếu chung mọi nguồn.
5. Định mức khí MMBtu/t (ước lượng 22, từ TM38 + sản lượng ước lượng); TM38 có gồm VAT không.
6. Chế độ giá khí 2021–25 (giả định 50/50 @12,7%) — quyết định độ lệch −11,7 và phần độ dốc +2.077.
7. Cam kết "giá Nam Du không vượt Petronas" (Elibook, thứ cấp).
8. Các mục 2, 4–10 của r3 §8 vẫn mở.

## 9. Sản phẩm
- `calc/model_r4.py` (+`model_r4_out.txt/.json`); `calc/LOCK_r4_md5.txt` (00:08:38 ICT 05/11).
- `calc/compare_px_r4.py` (+`_out.txt`): chạy sau khoá.
- `src/gas/egm2026_tailieu.pdf/.txt` (tài liệu ĐHĐCĐ bất thường 2026, SĐBS 12); `src/gas/dl_*.txt` (Biên bản ĐHĐCĐ 2025, NQ PV GAS); `src/gas/dl/` (PDF gốc).
- `txt/VDSC_Q3_2026.txt`.
- `png/egm26_p31.png`, `egm26_p32.png` (trang điều khoản giá); `png/gasNQ*.png`.
- **Chưa làm:** skeptic r4; cập nhật báo cáo nhà đầu tư (PDF r3 hiện dùng tâm 27.021 và câu khí "hoà vốn 75,8" — **đã lỗi thời so với r4**); `dd_price_zones.json`. **Không gửi email, không đặt lệnh, không sửa plan.**
