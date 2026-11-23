# DD — BSR (Tổng Công ty Lọc hoá dầu Việt Nam, NMLD Dung Quất) · **rev5 · 23/11/2026** · job `Taylor_20261123_120250`

Chuỗi bản: `REPORT.md` (rev2 09/11, tâm 17.496, skeptic r1 INCONCLUSIVE) → `REPORT_rev3.md` (tâm 16.112, r2 INCONCLUSIVE) → `REPORT_rev4.md` (tâm 16.886, r3 INCONCLUSIVE, `skeptic/r3.json`) → **bản này (rev5, áp skeptic r3)**. Không ghi đè bản cũ.
Chỉ nghiên cứu, không đặt lệnh/wire. Định giá **mù giá thị trường**: giả định khoá ở `calc/assumptions_rev5.json` (md5 `b6abb9cdc0f620a87fd2155ab7629055`, `calc/LOCK_prerun_md5_rev5.txt`) TRƯỚC khi chạy mô hình; không truy vấn giá mới — giá tham chiếu 26.250 (BQ 06/11, `calc/px_bsr.csv` md5 `5bb479ba…`), chỉ để dán nhãn.
Nhãn nguồn: **[BCTC]** PDF gốc · **[NQ5795]** · **[QĐ968]** · **[BQ]** · **[LEGAL]** legal-vn 23/11/2026 (văn bản + URL dẫn trong mục 1A) · **[UL]** ước lượng/giả định tự đặt · **[Bobby]** sector read mù 09/11.

## 0. Kết luận

| (đ/cp) | rev2 | rev3 | rev4 | **rev5 trước CK** | **rev5 sau CK (vị thế 5 tỷ)** | rev5 sau CK (40 tr) |
|---|---|---|---|---|---|---|
| Tâm (kỳ vọng có trọng số, 243 kết cục) | 17.496 | 16.112 | 16.886 | 16.621 | **16.544** | 16.614 |
| P10 / P50 / P90 | 13.093 / 17.350 / 23.345 | 11.385 / 15.933 / 21.911 | 12.159 / 16.627 / 22.451 | 11.872 / 16.361 / 22.212 | **11.818 / 16.285 / 22.110** | 11.868 / 16.354 / 22.203 |
| Nhãn @ 26.250 (06/11) | TRÊN | TRÊN | TRÊN | TRÊN | **TRÊN vùng** (+58,7% trên tâm, +18,7% trên P90) | TRÊN |

- **Vùng giá rev5:** rẻ (luật 4, 0,85×tâm) ≤ **14.062** · hợp lý **11.800–22.100** (P10–P90) · trên 22.100 là trả cho biên lọc cao kéo dài.
- **So rev4: −342 đ/cp (−2,0%)**, toàn bộ từ VAT được khấu trừ: rev4 coi 6.373 tỷ thu hồi 100% sau 1 năm (+1.121 đ/cp); rev5 dựng lại theo cơ chế pháp lý thật — **không được hoàn, chỉ bù trừ dần với GTGT đầu ra từ 01/2027** ở năng lực đo được ~2.027 tỷ/năm, và còn tích luỹ thêm ~3.119 tỷ trong Q4/2026 ⇒ PV ròng **+778 đ/cp**. Các mục skeptic r3 khác: đóng bằng nguồn độc lập (không đổi base) hoặc ghi "không kiểm chứng được" (mục 1A).
- **Giá 26.250 ngụ ý:** Ke **4,81%** (vs 13,5%), hoặc LN lõi vĩnh viễn **10.748 tỷ/năm = 3,1 lần** lõi 2023-25 (3.493) ≈ GRM cao hơn CƠ SỞ **+5,3 USD/thùng mãi mãi**. Bobby xếp STRUCTURAL p=0,15.
- **Một câu:** LN 9T/2026 kỷ lục là đỉnh chu kỳ (Hormuz + crack diesel + lãi tồn kho); giá trị nội tại ≈ tiền ròng 9.012 + nhà máy ở biên chuẩn hoá ~5.800 + LN vượt 2026Q4–2028 ~2.000 + VAT bù trừ dần ~780 − phần tuân thủ dự án mở rộng ~1.900 (kỳ vọng). **DD không ủng hộ mua theo cơ bản ở giá tham chiếu.**
- **Sizing (V8):** chuẩn sleeve 2–4% NAV/mã chỉ áp khi giá ≤ vùng hợp lý; ở TRÊN vùng DD đề xuất **0% discretionary**. Nếu LAG vẫn mua theo luật cơ học thì đó là cược PEAD/đà giá theo luật sleeve LAG, không phải DD.

## 1. Đính chính so với rev trước

### 1A. Áp skeptic r3 (rev4 → rev5) — từng hạng mục

| # | Hạng mục skeptic r3 | Xử lý rev5 | Loại | Ảnh hưởng tâm (đ/cp) |
|---|---|---|---|---|
| B1 | **VAT khấu trừ 6.373 tỷ: rev4 tính 100% thu hồi sau 1 năm, mâu thuẫn với "tích luỹ cơ cấu"** (killer r3) | **Nguyên nhân gốc đã xác định [LEGAL]:** từ 27/3/2026 xăng/diesel/nhiên liệu bay (từ 16/4 thêm dầu hoả, mazut) thuộc diện "không phải kê khai, tính nộp thuế GTGT nhưng được khấu trừ thuế GTGT đầu vào" — QĐ 482/QĐ-TTg 26/3/2026 → NQ 19/2026/QH16 (16/4–30/6) → NQ 34/2026/NQ-CP (đến 30/9) → **NQ 43/2026/NQ-CP (đến 31/12/2026)**; chưa thấy văn bản gia hạn sau 31/12/2026. Đối chiếu [BCTC TM17, pdf tr.30]: 9T GTGT đầu ra phải nộp 312,98 tỷ, **thuế BVMT phải nộp chỉ 13,48 tỷ**, thuế XNK 2,70 tỷ — khớp cơ chế BVMT = 0 đ/lít và thuế NK MFN 0% (NĐ 72/2026) năm 2026. ⇒ Tích luỹ là **cơ cấu TRONG thời hạn chính sách**, không phải vĩnh viễn. **Hoàn thuế:** Luật GTGT 48/2024/QH15 Điều 15 k1–4 chỉ hoàn cho xuất khẩu / dự án đầu tư / cơ sở chỉ SX hàng 5% / giải thể ⇒ BSR **không thuộc diện hoàn**; NQ 19/34/43 không có điều khoản hoàn riêng (legal-vn: "không tìm thấy"). ⇒ **Base mới:** thu hồi bằng BÙ TRỪ với GTGT đầu ra từ 01/2027. Năng lực bù trừ = GTGT đầu ra phải nộp tại 31/12/2025 **168,93 tỷ** [BCTC TM17 cột đầu năm] × 12 = **2.027 tỷ/năm** (đọc số dư cuối năm = số kê khai 1 tháng là diễn giải [UL]; thận trọng vì chưa tính thuế suất 8%→10% và BVMT quay lại giá tính thuế từ 2027). Tích luỹ Q4/2026: 6.373 / 6,13 tháng cơ chế ≈ 1.040 tỷ/tháng × 3 = **3.119 tỷ** (dòng ra t=0,25). Số dư 9.492 tỷ bù trừ ~4,7 năm (2027–2031), chiết khấu Ke ⇒ PV ròng **3.896 tỷ = 778 đ/cp** (rev4: 5.615 tỷ = 1.121) | (a) | **−342** |
| B1' | Độ nhạy VAT | Năng lực bù trừ ở thuế suất 10% (2.534 tỷ/năm): **16.620** · tích luỹ Q4 theo DT kế hoạch (1.400 tỷ): **16.683** · **cơ chế gia hạn hết 2027 (b, chưa có văn bản ⇒ không vào base):** **14.939 (−1.605)** · số dư 9T mất trắng (cực đoan, trái Luật 48 vì quyền khấu trừ chuyển kỳ không mất): **15.709** | (b) | 0 |
| B2 | Quỹ KHCN 2026 ghi 0 — có thể bắt buộc trích tối thiểu 3% nếu DNNN | **[LEGAL]** Luật TNDN 67/2025/QH15 Điều 17 k1: DN được trích **tối đa** 20% thu nhập tính thuế, không có mức tối thiểu; NĐ 265/2025/NĐ-CP Điều 34 k2 **bãi bỏ NĐ 95/2014** (mức sàn 3% cho DNNN cũ); Luật KH,CN&ĐMST 93/2025 Điều 66 mang tính cho phép ⇒ **không bắt buộc**, base 0 giữ. Độ nhạy trích 10% (3.730 tỷ, tự nguyện): **15.803** | (a) đóng | 0 |
| B3 | KH 2026 điều chỉnh (NQ 5795) ngụ ý Q4 lỗ −6.323 tỷ vs XẤU −2.000 | Đọc NQ 5795 PL1 (`rev5/png/nq_p5.png`, `nq_p6.png`): chỉ có chỉ tiêu tài chính, đầu tư, lao động — **không có chỉ tiêu sản lượng/dừng máy**. Kiểm độc lập [BQ Revenue_P0/NP_P0]: DT Q1 45.919,5 / Q2 58.716,5 / Q3 59.580,6 tỷ; LNST Q1 8.264,7 / Q2 7.460,1 / Q3 8.968,0. KH LNST 18.579 − LNST 6T 15.724,8 = **2.854 tỷ cho cả H2**, nhỏ hơn riêng Q3 thực 8.968 ⇒ KH điều chỉnh = **6T thực + H2 theo kế hoạch cũ** (KH gốc 30/4 cả năm 2.162 tỷ, ROE 3,7%), không chứa Q3 thực; Q4 −6.323 là phép trừ cơ học, không phải dự báo. Base giữ. Độ nhạy Q4 = KH (vượt nền −7.649 ở mọi kịch bản): **14.532** | (a) đóng + độ nhạy | 0 |
| B4 | Quyết toán CPH phải nộp Nhà nước | Không có hồ sơ quyết toán/công văn trong nguồn; Deloitte soát xét 6T/2026 chỉ nhấn mạnh "chưa phê duyệt" ⇒ **không kiểm chứng được**; giữ WARNING, không vào base. Ảnh hưởng: không ước lượng được số tiền (không có cơ sở định lượng) | (c) | — |
| B5 | BCTC kiểm toán FY2025 vắng | **Không kiểm chứng được** trong phiên (không có trong `src/`; các phiên trước tìm web không ra). `audited_fy_missing=true`. Bù trừ: dùng soát xét 6T/2026 Deloitte (chấp nhận toàn phần) + BQ LN năm | (c) | — |
| B6 | Thuê đất / cung dầu thô / bao tiêu | Không có hợp đồng công bố ⇒ **không kiểm chứng được**; dầu thô ~88% nội địa theo Brent [Bobby]; PV OIL 21,9% DT 9T [BCTC TM22b] | (c) | — |
| B7 | Euro V bắt buộc với nhà sản xuất (ảnh hưởng mức 0,40 của trục tuân thủ) | **[LEGAL] không tìm thấy** văn bản buộc NSX chỉ SX/lưu thông mức 5: QCVN 01:2022/BKHCN (TT 16/2022) vẫn có mức 2–5; TT 19/2026/TT-BKHCN sửa đổi chủ yếu về etanol; QĐ 19/2024/QĐ-TTg áp cho xe. ⇒ Củng cố xếp GHDT/DHDT/HGU là tự nguyện; trục 0,10/0,40/0,75 giữ nguyên làm kịch bản (không hạ xác suất vì "không tìm thấy" ≠ "chắc chắn không có") | (a)/(c) | 0 |
| B8 | Phân loại GHDT/DHDT/HGU theo V4a (−919 nếu kỳ vọng 0,45) | Giữ phân loại rev4 (tự nguyện ⇒ NPV0 theo luật user 03/11) — B7 bổ sung cơ sở. Độ nhạy cố định 0,45: **15.625**. Vẫn cần user/Mike phán | (b) | 0 |
| B9 | Chiều rẻ: phần tăng trưởng NPV0; bản A giữ lãi tỷ giá | Giữ NPV0 (luật V4a, không có IRR/hợp đồng đầu ra). Bản A (+402 LN lõi): **17.123** | (b) | 0 |

Luỹ kế: rev4 16.886 → (B1 VAT bù trừ) **16.544 = rev5**. Không mục nào khác đổi base.

### 1B. Các vòng trước (giữ nguyên)
- **rev3 → rev4 (skeptic r2):** VAT tách khỏi trục giá dầu (A1, nay thay bằng B1); phân loại GHDT/DHDT/HGU (A2); quỹ KHCN độ nhạy (A3, nay đóng ở B2); cơ cấu chi phí 39.004,5 tỷ theo cụm **không kiểm chứng được** (A4); Euro V (A5, nay B7).
- **rev2 → rev3 (skeptic r1):** QĐ968 phân loại tăng trưởng/tuân thủ (−1.885 kỳ vọng); bỏ +370 + sửa TA đếm hai lần (+501); capex 3.155 = ứng nhà thầu 2.601,1 [TM7]; nguồn vốn dự án 40/60, không pha loãng.

## 2. Đối chiếu số liệu với PDF gốc (BCTC HN Q3/2026, `src/BCTC_HN_Q3_2026.pdf` md5 `7be32745…`)

| Khoản (tỷ) | Mô hình | PDF gốc | Trang |
|---|---|---|---|
| Tiền + TĐT (110) / HTM (123) / Vay NH (321) | 1.758,4 / 56.892,8 / 13.525,0 | 1.758,392 / 56.892,821 / 13.525,007 | BS tr.4–5 |
| Tiền ròng | **45.126 (9.012 đ/cp)** | — | tính |
| XDCB (252) / Trả trước dài hạn (212) | 2.525,9 / 546,3 | 2.525,899 / 546,307 | BS tr.4 |
| VAT được khấu trừ (162) | 6.509,1 (đầu năm 136,1) | 6.509,082 / 136,125 | BS tr.4 |
| Quỹ KHCN (344) / KTPL (323) / NCI (429) | 844,0 / 441,6 / 32,0 | 843,965 / 441,645 / 31,961 | BS tr.5 |
| Ứng trước nhà thầu (TM7) | 2.601,2 | 2.120,083 + 481,054 | tr.22 |
| MBV tạm dừng giao dịch (TM5) | 2.735,6 | 2.735,630 | tr.20 |
| TM17: GTGT đầu ra phải nộp đầu năm / trong kỳ | 168,93 (năng lực bù trừ) / — | 168.932.126.965 / 312.980.666.169 đ | tr.30 |
| TM17: BVMT phải nộp đầu năm / trong kỳ 9T | — | 45.807.838.000 / 13.477.271.000 đ | tr.30 |
| NQ 5795 PL1: KH DT / LNTT / LNST HN 2026 điều chỉnh (gốc 30/4) | 190.831 / 20.646 / 18.579 (154.140 / 2.405 / 2.162) | như trái | NQ tr.5 |

LN năm 2019–25, DT/LN quý 2025–26 và số CP 5.007,3 tr: [BQ] `calc/bq_bsr_fin.csv` (md5 `f45b76e7…`), mô hình tự assert lại.

## 3. Định giá (mù giá)

### 3.1 Khung
Giá trị = (a) nhà máy: LN lõi (không gồm lãi tiền gửi/tỷ giá) / Ke, RONIC = Ke, trừ phần thuế 10%→20% sau 2039 · + (b) PV LN VƯỢT nền 2026Q4–2028 · + (c) tiền ròng + XDCB + khoản ghi sổ mở rộng (NPV0 phần tăng trưởng) − quỹ KHCN − KTPL − NCI · **+ (d) VAT: −tích luỹ Q4/2026 + PV bù trừ số dư từ 2027 ở 2.027 tỷ/năm (mới rev5)** · + (e) giải phóng WC vượt KHÔNG gồm VAT (trục 0/27%/54% × 4.040 tỷ) · − (f) phần TUÂN THỦ dự án mở rộng.

| Tham số | XẤU | CƠ SỞ | TỐT | Cơ sở |
|---|---|---|---|---|
| Trọng số | 0,30 | 0,50 | 0,20 | Bobby 09/11; bản đối xứng 0,275/0,45/0,275 |
| LN lõi chuẩn hoá (tỷ/năm) | 2.611,9 | **4.011,9** | 6.111,9 | neo 2023-25 sau bóc lãi/tỷ giá 3.492,7 [BQ+BCTC TM24/25] + TA/12 519,2 [BQ]; khoảng cách −1.400/+2.100 [UL] |
| ± trục LN lõi | −20/0/+20% (0,25/0,5/0,25) | | | [UL] |
| LN vượt Q4/26 · 2027 · 2028 (tỷ) | −2.000 · +557,6 · 0 | 4.000 · 5.557,6 · 1.000 | 7.000 · 13.557,6 · 5.000 | rev2 + TA/4 cho 2027; Bobby [UL]; hệ số 0,5/1/1,5 |
| Ke (r, V1) | 13,50% | | | 13,5% + 1,0×(lãi huy động 12T hiệu dụng 7,40% `cctg_12m` 02/11 − neo 7,40% 03/11) |
| Thuế TNDN | 10% đến 2039, 20% sau | | | QĐ 952/QĐ-TTg (TM thuế HN Q3/26) |
| VAT | số dư 6.373 + Q4 3.119; bù trừ 2.027 tỷ/năm từ 2027 | | | B1 [LEGAL]+[BCTC TM17] |
| Tỷ trọng tuân thủ dự án mở rộng | 0,10 (p 0,50) · 0,40 (p 0,35) · 0,75 (p 0,15) | | | mục 3.2 [UL] |

### 3.2 Dự án nâng cấp mở rộng NMLD Dung Quất — phân loại (V4)
Nguồn: QĐ 968/QĐ-BSR 28/3/2024 (`src_rev3/`) + NQ 5795 PL2 (tổng mức **39.004,5 tỷ**, vay 23.402,7 / VCSH 15.601,8; vận hành 2028). Mục tiêu: 148 → 171 nghìn thùng/ngày; Euro V; môi trường theo lộ trình bắt buộc; linh hoạt dầu thô. Cơ cấu SP: FO 7 → 0; Jet 5,3 → 13,1; lưu huỳnh 13 → 56,7 t/ngày.
- **Tăng trưởng (NPV0, V4a):** tăng công suất, FO → Jet/xăng/PP, linh hoạt dầu thô; GHDT/DHDT/HGU (tự nguyện — B7: không tìm thấy văn bản bắt buộc Euro V với NSX).
- **Tuân thủ (dòng tiền ra, V4b):** cụm môi trường SRU3/4 + SWS2 + ARU2.
- Tỷ trọng từng cụm không công bố ⇒ trục 0,10/0,40/0,75 (p 0,50/0,35/0,15) [UL]. Trừ = s × (ghi sổ 5.285,2 + còn chi 33.719,3 chiết khấu 1,5 năm) × 0,945. Kỳ vọng 30,25% ⇒ −1.885 đ/cp.

### 3.3 Cấu phần (đ/cp, Ke 13,5%)
Tiền ròng 9.012 · cố định (tiền ròng + CIP + khoản ghi sổ mở rộng − KHCN − KTPL − NCI + VAT PV 778) **10.662** · nhà máy XẤU 3.781 / CƠ SỞ **5.808** / TỐT 8.848 · LN vượt XẤU −284 / CƠ SỞ **1.960** / TỐT 4.662 · WC vượt (không gồm VAT) 4.040 tỷ trục 0/27/54% · tuân thủ kỳ vọng −1.885.
Kịch bản giữa trục: **XẤU 12.483 · CƠ SỞ 16.753 · TỐT 22.496**.

### 3.4 Độ nhạy (sau CK 5 tỷ; tâm base 16.544)
- **r (V1):** +100bp 16.168 · +50bp 16.349 · −50bp 16.753 · −100bp 16.979. Nhạy thấp vì ~64% giá trị là khoản cố định.
- **VAT:** bù trừ 10% 16.620 · tích luỹ Q4 1.400 tỷ 16.683 · **cơ chế gia hạn hết 2027: 14.939** · số dư 9T mất trắng 15.709.
- **Q4/2026 = KH NQ 5795 (−6.323 LNST):** 14.532.
- **Tỷ trọng tuân thủ cố định 0,45:** 15.625. **Quỹ KHCN tự nguyện 10%:** 15.803. **Bản A (+402 lõi):** 17.123. **MBV mất trắng:** 16.000. **Bản trọng số đối xứng:** 17.079 (P90 23.654). Moat WIDE giả định (RONIC 20%, g 4%): 17.352 (thông tin).
- **Tỷ trọng tuân thủ cố định 0 / 0,10 / 0,75:** 18.429 / 17.806 / 13.756.
- **TRÊN vùng ở mọi biến thể** (P90 cao nhất 24.277 khi tỷ trọng tuân thủ = 0, < 26.250).
- 1 USD/thùng GRM bền ≈ 1.266 tỷ LN/năm ≈ 1.870 đ/cp.

### 3.5 Hai nền (V6) — chỉ HIỂN THỊ
V_ngắn = LNST chuẩn hoá (trung vị 2023-25 = 5.213,6 tỷ [BQ]) / r, g = 0 ⇒ **7.713 đ/cp**. V_dài (FCFE DCF) không tính (capex mở rộng 39 nghìn tỷ chi phối 2026-28). Chênh ln(16.544/7.713) = 0,76 > ln2: V_ngắn vốn hoá lãi tiền gửi ở Ke, định giá 45 nghìn tỷ tiền ròng ~25% mệnh giá; DD cộng tiền ròng theo mệnh giá. Vùng đọc mở rộng [7.713; 22.110] — vẫn TRÊN vùng.

## 4. Cờ tự động của hệ
| Cờ | Kết luận | Lý do bằng số |
|---|---|---|
| DCF auto RICH 21.359 | **THẬT** về hướng | Tâm DD 16.544, P90 22.110 < giá 26.250 |
| PE TTM 4,74 "rẻ" | **NHIỄU** | LN TTM ≈ 6,9–7,9 lần LN lõi 3.493–4.012 |
| LAG_HI | **THẬT về số, KHÔNG BỀN** | +888% YoY do crack + tồn kho |
| ADV | **THẬT** | ADV250 trung vị 260,6 tỷ, ADV60 257,1 tỷ [BQ] |

## 5. Rủi ro & điều đổi nhận định (HAI chiều)
**Rủi ro số 1:** biên lọc mean-revert (Hormuz mở, K2 p0,35) + TA6 2027 + lỗ tồn kho.
**Rủi ro số 2:** tỷ trọng tuân thủ dự án mở rộng ≥ 0,40 ⇒ tâm 13.756 (0,75) … 15.625 (0,45).
**Rủi ro số 3:** cơ chế "không kê khai GTGT xăng dầu" gia hạn sang 2027 ⇒ VAT tích luỹ thêm, tâm ~14.939.
**Đổi lên:** giá ≤ 22.100 ⇒ TRONG vùng; ≤ 14.062 ⇒ luật 4 · crack bền sau Hormuz mở ≥ 2 quý · BSR công bố cơ cấu tổng mức đầu tư (cụm môi trường < 10%) ⇒ tâm tới 17.806–18.429 · thuế suất GTGT 10% + BVMT quay lại từ 2027 (năng lực bù trừ cao hơn: +76).
**Đổi xuống:** crack TE T3/2027 < 35 · Q4/2026 lỗ ≤ −3.000 tỷ · văn bản gia hạn cơ chế GTGT 0 kê khai sang 2027 · văn bản bắt buộc Euro V với NSX · tổng mức đầu tư tăng tiếp · quyết toán CPH ra số phải nộp (WARNING).

## 6. Vị thế & lợi thế cạnh tranh (5F, V5)
Làm đầy đủ 09/11/2026 (< 12 tháng) ⇒ tái dùng rev2 mục 6: `moat_tier = NARROW`, `moat_type = ADMIN/LOCATION`, RONIC = Ke. ROIC_Min5Y −1,0% [BQ]. Rủi ro số 1 của moat: Lực 6 Nhà nước (thuế NK/BVMT/GTGT xăng dầu — B1 cho thấy chính sách thuế 2026 đổi 4 lần trong 6 tháng; PVN 92,12%).

## 7. Thanh khoản & sizing (V3, V8)
ADV250 trung vị 260,6 tỷ, σ ngày 3,34% [BQ]. CK σ·√(Q/ADV): 5 tỷ **0,46%**; 40 tr 0,04%. Nhãn theo giá trị SAU CK (5 tỷ). Sizing: mục 0 (0% ở giá tham chiếu).

## 8. Pháp lý / quản trị — chỉ WARNING (không vào base)
- Deloitte soát xét 6T/2026 chấp nhận; nhấn mạnh quyết toán CPH (2018) chưa phê duyệt. FY2025 KT không có (`audited_fy_missing=true`).
- MBV 2.735,6 tỷ tạm dừng giao dịch [TM5]; độ nhạy mất trắng −544 đ/cp.
- SOE PVN 92,12%; bên liên quan PV OIL 21,9% DT 9T.

## 9. Còn mở / không kiểm chứng được
- Cơ cấu chi phí 39.004,5 tỷ theo cụm: **không kiểm chứng được** ⇒ trục kịch bản (tỷ trọng cố định 0 / 0,10 / 0,75: 18.429 / 17.806 / 13.756).
- Phân loại GHDT/DHDT/HGU (V4a): **cần Mike/user phán** — độ nhạy 0,45: 15.625.
- Cơ chế GTGT xăng dầu sau 31/12/2026: chưa có văn bản; base = kết thúc đúng hạn NQ 43; gia hạn ⇒ 14.939. Diễn giải "168,93 tỷ = 1 tháng kê khai" là [UL].
- Quyết toán CPH, BCTC KT FY2025, hợp đồng thuê đất/dầu thô/bao tiêu: **không kiểm chứng được**; không lượng hoá.
- Văn bản gốc NQ 19/2026/QH16, NQ 43/2026/NQ-CP: legal-vn đọc qua CQNN/báo có trích (thuvienphapluat chặn 403) — chưa đọc toàn văn Công báo.
- `dd_assumptions_lint.py`: chế độ cảnh báo rc=0 (24 cảnh báo; file khoá định dạng cũ chưa schema v1; L9 `adv_*` là dương tính giả — người mua trả trước / ứng trước nhà thầu).

## 10. File
`src/` (6 PDF, `src/SRC_md5.txt`) · `src_rev3/` (QĐ968) · `rev3/png/` (TM17 tr.30 …) · `rev5/png/nq_p5.png` (md5 `799dea79…`), `nq_p6.png` (md5 `e660a3a2…`) — NQ 5795 PL1 · `calc/assumptions_rev5.json` (md5 `b6abb9cd…`) · `calc/model_bsr_rev5.py` (md5 `6976d712…`; chạy 2 lần, `model_out_rev5.json` md5 `1f05a547…` trùng) · `calc/LOCK_post_md5_rev5.txt`. Chạy: `cd calc; OMP_NUM_THREADS=1 /home/trido/thanhdt/wc_venv/bin/python -I model_bsr_rev5.py` (biến thể: `BSR_VAT_OFFSET=`, `BSR_VAT_Q4=`, `BSR_VAT_EXTEND=1`, `BSR_VAT_REC=`, `BSR_Q4_PLAN=1`, `BSR_COMP_SHARE=`, `BSR_FUND_ACCR=`, `BSR_CORE_ADD=402`, `BSR_MBV_LOSS=1`).
