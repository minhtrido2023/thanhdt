# DD — BSR (Tổng Công ty Lọc hoá dầu Việt Nam, NMLD Dung Quất) · **rev4 · 23/11/2026** · job `Taylor_20261123_050001` (resume `Taylor_20261123_003452`)

Chuỗi bản: `REPORT.md` (rev2 09/11, tâm 17.496, skeptic r1 INCONCLUSIVE) → `REPORT_rev3.md` (23/11, tâm 16.112, skeptic r2 INCONCLUSIVE, `skeptic/r2.json`) → **bản này (rev4, áp skeptic r2)**. Không ghi đè bản cũ.
Chỉ nghiên cứu, không đặt lệnh/wire. Định giá **mù giá thị trường**: giả định khoá ở `calc/assumptions_rev4.json` (md5 `902291f3fb9e925f38608391c8419c72`, `calc/LOCK_prerun_md5_rev4.txt`) TRƯỚC khi chạy mô hình; không truy vấn giá mới — giá tham chiếu 26.250 (BQ 06/11, `calc/px_bsr.csv` của rev2), chỉ để dán nhãn.
Nhãn nguồn: **[BCTC]** đọc từ PDF gốc · **[QĐ968]** · **[BQ]** · **[UL]** ước lượng/giả định tự đặt · **[Bobby]** sector read mù 09/11.

## 0. Kết luận

| (đ/cp) | rev2 | rev3 | **rev4 trước CK** | **rev4 sau CK (vị thế 5 tỷ)** | rev4 sau CK (40 tr) |
|---|---|---|---|---|---|
| Tâm (kỳ vọng có trọng số, 243 kết cục) | 17.496 | 16.112 | 16.964 | **16.886** | 16.957 |
| P10 / P50 / P90 | 13.093 / 17.350 / 23.345 | 11.385 / 15.933 / 21.911 | 12.216 / 16.704 / 22.556 | **12.159 / 16.627 / 22.451** | 12.211 / 16.697 / 22.546 |
| Nhãn @ 26.250 (06/11) | TRÊN | TRÊN | TRÊN | **TRÊN vùng** (+55% trên tâm, +17% trên P90) | TRÊN |

- **Vùng giá rev4:** rẻ (luật 4, 0,85×tâm) ≤ **14.353** · hợp lý **12.200–22.400** (P10–P90) · trên 22.400 là trả cho biên lọc cao kéo dài.
- **So rev2: −610 đ/cp (−3,5%)**: dự án mở rộng có phần **tuân thủ** (kỳ vọng tỷ trọng 30,25% ⇒ −1.885); sửa TA hai chiều + bỏ +370 (+501); VAT khấu trừ tách khỏi trục giá dầu (+774). Nhãn không đổi ở mọi biến thể (mục 3.4).
- **Giá 26.250 ngụ ý:** Ke **4,92%** (vs 13,5%), hoặc LN lõi vĩnh viễn **10.511 tỷ/năm = 3,0 lần** lõi 2023-25 (3.493) ≈ GRM cao hơn CƠ SỞ **+5,1 USD/thùng mãi mãi**. Bobby xếp STRUCTURAL p=0,15.
- **Một câu:** LN 9T/2026 kỷ lục là đỉnh chu kỳ (Hormuz + crack diesel + lãi tồn kho); giá trị nội tại ≈ tiền ròng 9.012 + nhà máy ở biên chuẩn hoá ~5.800 + LN vượt 2026Q4–2028 ~2.000 + VAT được khấu trừ ~1.100 − phần tuân thủ dự án mở rộng ~1.900 (kỳ vọng). **DD không ủng hộ mua theo cơ bản ở giá tham chiếu.**
- **Sizing (V8):** chuẩn sleeve 2–4% NAV/mã chỉ áp khi giá ≤ vùng hợp lý; ở TRÊN vùng DD đề xuất **0% discretionary**. Nếu LAG vẫn mua theo luật cơ học thì đó là cược PEAD/đà giá theo luật sleeve LAG, không phải DD.

## 1. Đính chính so với rev trước

### 1A. Áp skeptic r2 (rev3 → rev4)

| # | Hạng mục skeptic r2 | Xử lý rev4 | Loại | Ảnh hưởng tâm (đ/cp) |
|---|---|---|---|---|
| A1 | **VAT được khấu trừ 136 → 6.509 tỷ bị gộp vào trục giải phóng WC theo giá dầu** (chiều rẻ) | Đọc TM17 (pdf tr.30, `rev3/png/hn_p30_tm17.png`): 9T thuế GTGT đầu ra phải nộp chỉ **312,98 tỷ** vs GTGT hàng nhập khẩu **3.136,18 tỷ** ⇒ tích luỹ đầu vào mang tính **cơ cấu**, không theo giá dầu. Tách khỏi trục WC; base = phần tăng 6.373,0 tỷ theo mệnh giá, chiết khấu 1 năm ở Ke (quyền khấu trừ/hoàn đối với Nhà nước, ghi sổ trong BCTC) | (a) | **+774** |
| A2 | Phân loại GHDT/DHDT/HGU là NPV0 "chỉ vì không thấy văn bản bắt buộc" (killer r2; ước −900 nếu dồn kỳ vọng ~0,45) | **Giữ phân loại, nêu cơ sở:** không bắt buộc ⇒ là chi tiêu TỰ NGUYỆN do ĐHĐCĐ quyết ⇒ theo luật user 03/11 (V4a, cấm "đầu tư mới ⇒ giảm giá trị") ghi NPV0 trừ khi có cơ sở độc lập. Bằng chứng tạo giá trị độc lập [QĐ968]: lưu huỳnh thu hồi **13 → 56,7 t/ngày (×4,4)** = khả năng chạy dầu thô lưu huỳnh cao hơn (mục tiêu 4, cấu hình Azeri 53% + ESPO 47%) ⇒ đầu vào rẻ hơn; FO 7 → 0 nghìn thùng. Premium không lượng hoá được ⇒ NPV0, không NPV dương. **Độ nhạy khi dồn kỳ vọng 0,45: 15.967 (−919)** — vẫn TRÊN vùng. Điểm này cần user/Mike phán (luật V4a vs lập luận "không tạo doanh thu") | (a) phân loại + (b) độ nhạy | 0 (độ nhạy −919) |
| A3 | Trích quỹ KHCN/KTPL năm 2026 chưa dồn tích | Quỹ KHCN 856 → 844 trong 9T (chưa trích); tỷ lệ trích lịch sử của BSR **không có trong thư mục** ⇒ (b) độ nhạy, không vào base: trích tối đa 10% thu nhập tính thuế 2026 (ước 3.730 tỷ = LNTT 9T ~28.000 × 4/3 × 10%) ⇒ **16.144 (−742)**. KTPL của DNNN bị trần theo quỹ lương ⇒ nhỏ, không lượng hoá | (b) | 0 (độ nhạy −742) |
| A4 | Cơ cấu chi phí 39.004,5 tỷ theo cụm phân xưởng | Phụ lục tổng mức đầu tư QĐ968, hợp đồng EPC, hồ sơ ECA **không công bố/không tìm được** ⇒ **không kiểm chứng được**; giữ trục 0,10/0,40/0,75 [UL]. Ảnh hưởng: 0,10 → 0,75 làm tâm 18.148 → 14.097 | (c) | — |
| A5 | Văn bản bắt buộc Euro V với nhà sản xuất | Tìm web 23/11: QCVN 01:2022/BKHCN (TT 16/2022, bắt buộc từ 15/6/2023) vẫn cho lưu thông nhiều mức; không thấy mốc bắt buộc mức 5. **Chưa kiểm chứng đầy đủ** (chưa qua legal-vn) — quyết định mức 0,40 | (c) | — |
| A6 | BCTC KT FY2025, quyết toán CPH, hợp đồng thuê đất / dầu thô / bao tiêu | **Không kiểm chứng được** trong phiên; `audited_fy_missing=true`; CPH = WARNING. Dầu thô ~88% nội địa theo giá Brent [Bobby]; bao tiêu: PV OIL 21,9% DT 9T [BCTC TM22b] — không có hợp đồng dài hạn công bố | (c) | 0 |
| A7 | Lãi tiền gửi 2023-24 không lấy nguồn (dùng 9T/25 quy năm) | Giữ; skeptic r2 đánh giá "nhỏ". Bản A (giữ tỷ giá, +402) là song song | (c) | — |

### 1B. Áp skeptic r1 (rev2 → rev3, giữ nguyên trong rev4)

| # | Hạng mục skeptic r1 | Xử lý | Ảnh hưởng |
|---|---|---|---|
| 1 | Thiếu phân loại tăng trưởng/tuân thủ dự án mở rộng | QĐ 968/QĐ-BSR (`src_rev3/`, md5 `821ab1af…`); tăng công suất + nâng cơ cấu SP = tăng trưởng (NPV0); cụm môi trường SRU3/4 + SWS2 + ARU2 = tuân thủ (dòng tiền ra); trục tỷ trọng mục 3.2 | −1.885 |
| 2 | Nguồn gốc PDF / file calc | `src/` khôi phục, md5 6 PDF khớp; E1–E4 đọc lại trên PDF gốc, khớp (mục 2) | 0 |
| 3 | CƠ SỞ +370 trên neo | Bỏ | gộp #4 |
| 4 | TA đếm hai lần | Chi phí TA5 = TB(2023,2025) − 2024 = 6.230,5 tỷ [BQ]; lõi +TA/12 (+519,2); LN vượt 2027 +TA/4 (+1.557,6) | #3+#4: **+501** |
| 5 | Capex 3.155 chưa giải thích | Đóng: trả trước người bán +2.637, trong đó 2.601,1 ứng China Chengda + Beijing Petrochemical Engineering [TM7] | 0 |
| 6 | Nguồn vốn 15.601,8 VCSH | QĐ968: 40/60; VCSH từ khấu hao + LN, phát hành CP chỉ khi thiếu; tiền ròng 45.126 > 15.601,8 ⇒ base không pha loãng | 0 |
| 7–9 | KT FY2025 / CPH / tin pháp lý T11 | không kiểm chứng được (xem A6) | 0 |

Luỹ kế: rev2 17.496 → (#3+#4) 17.997 → (#1 tuân thủ kỳ vọng) 16.112 = rev3 → (A1 VAT) **16.886 = rev4**.

## 2. Đối chiếu số liệu với PDF gốc (BCTC HN Q3/2026, `src/BCTC_HN_Q3_2026.pdf` md5 `7be32745…`)

| Khoản (tỷ) | Mô hình | PDF gốc | Trang |
|---|---|---|---|
| Tiền + TĐT (110) / HTM (123) / Vay NH (321) | 1.758,4 / 56.892,8 / 13.525,0 | 1.758,392 / 56.892,821 / 13.525,007 | BS tr.4–5 |
| Tiền ròng | **45.126 (9.012 đ/cp)** | — | tính |
| XDCB (252) / Trả trước dài hạn (212) | 2.525,9 / 546,3 | 2.525,899 / 546,307 | BS tr.4 |
| VAT được khấu trừ (162) | 6.509,1 (đầu năm 136,1) | 6.509,082 / 136,125 | BS tr.4 |
| Quỹ KHCN (344) / KTPL (323) / NCI (429) | 844,0 / 441,6 / 32,0 | 843,965 / 441,645 / 31,961 | BS tr.5 |
| Ứng trước nhà thầu (TM7) | 2.601,2 | 2.120,083 + 481,054 = 2.601,1 | tr.22 |
| MBV tạm dừng giao dịch (TM5) | 2.735,6 | 2.735,630 | tr.20 |
| DT tài chính 9T/25 (TM24) | lãi gửi 940,7 + TG 521,7 + cổ tức 0,28 | 940,735 + 521,735 + 0,280 = 1.462,750 | tr.34 |
| Chi phí vay / lỗ TG 9T/25 (TM25) | 199,4 / (TG ròng 335) | 199,369 / 186,653 ⇒ 335,1 | tr.34 |
| GTGT đầu ra / hàng NK phải nộp 9T/26 (TM17) | — | 312,980 / 3.136,179 | tr.30 |

LN năm 2019–25 và số CP 5.007,3 tr: [BQ], model tự assert lại từ `calc/bq_bsr_fin.csv`; skeptic r1 và r2 đã tự kiểm khớp (r2 đọc thêm mã 411 = 50.072,997 tỷ ⇒ 5.007,3 tr cp).

## 3. Định giá (mù giá)

### 3.1 Khung
Giá trị = (a) nhà máy: LN lõi (không gồm lãi tiền gửi/tỷ giá) / Ke, RONIC = Ke, trừ phần thuế 10%→20% sau 2039 · + (b) PV LN VƯỢT nền 2026Q4–2028 · + (c) tiền ròng + XDCB + khoản ghi sổ mở rộng (NPV0 phần tăng trưởng) − quỹ KHCN − KTPL − NCI · **+ (d) phần tăng VAT khấu trừ, mệnh giá PV 1 năm (mới rev4)** · + (e) giải phóng WC vượt KHÔNG gồm VAT (trục 0/27%/54% × 4.040 tỷ) · − (f) phần TUÂN THỦ dự án mở rộng.

| Tham số | XẤU | CƠ SỞ | TỐT | Cơ sở |
|---|---|---|---|---|
| Trọng số | 0,30 | 0,50 | 0,20 | Bobby 09/11 (K2+ADMIN / K1 / STRUCTURAL+K3); bản đối xứng 0,275/0,45/0,275 |
| LN lõi chuẩn hoá (tỷ/năm) | 2.611,9 | **4.011,9** | 6.111,9 | neo 2023-25 sau bóc lãi/tỷ giá 4.784,7 − 1.292 = 3.492,7 [BQ+BCTC TM24/25] + TA/12 519,2 [BQ]. XẤU/TỐT giữ khoảng cách −1.400 / +2.100 (≈+1,66 USD/thùng × 1.266 tỷ) [UL] |
| ± trục LN lõi | −20/0/+20% (0,25/0,5/0,25) | | | [UL] |
| LN vượt Q4/26 · 2027 · 2028 (tỷ) | −2.000 · +557,6 · 0 | 4.000 · 5.557,6 · 1.000 | 7.000 · 13.557,6 · 5.000 | rev2 + TA/4 cho 2027; Bobby F1–F4, D2/D3 [UL]; hệ số 0,5/1/1,5 |
| Ke (r, V1) | 13,50% | | | 13,5% + 1,0×(lãi huy động 12T hiệu dụng 7,40% `cctg_12m` 02/11 − neo 7,40% 03/11) |
| Thuế TNDN | 10% đến 2039, 20% sau | | | TM thuế HN Q3/26 (QĐ 952/QĐ-TTg) |
| VAT khấu trừ | 100% mệnh giá, PV 1 năm | | | TM17 (mục 1A-A1); độ nhạy 50%/0% |
| Tỷ trọng tuân thủ dự án mở rộng | 0,10 (p 0,50) · 0,40 (p 0,35) · 0,75 (p 0,15) | | | mục 3.2 [UL] |

### 3.2 Dự án nâng cấp mở rộng NMLD Dung Quất — phân loại (V4)
**Nguồn:** QĐ 968/QĐ-BSR 28/3/2024 (`src_rev3/bsr_2024_03_29_board_decision.docx`) + NQ 5795/NQ-BSR 06/11/2026 PL2 (tổng mức hiện hành **39.004,5 tỷ**, vay 23.402,7 / VCSH 15.601,8; KH chi 2026 7.787,3; vận hành 2028). Tổng mức 3/2024 là 36.397,3 tỷ ⇒ đã +7,2%.
- **Mục tiêu [QĐ968]:** (1) 148 → **171 nghìn thùng/ngày (+15,5%)**; (2) sản phẩm **Euro V**; (3) chuẩn môi trường **theo lộ trình bắt buộc**; (4) linh hoạt dầu thô; (5) tăng hiệu quả đầu tư.
- **Phân xưởng mới:** GHDT, DHDT, ALK, HGU, SRU3/4 + SWS2, ARU2; cải hoán CDU, RFCC, NHT, ISOM, CCR, PRU…
- **Cơ cấu sản phẩm/ngày [QĐ968]:** FO 7 → 0 nghìn thùng; Jet 5,3 → 13,1; xăng 65,9 → 79,7; DO 53,2 → 59,2; propylene 462 → 685 t; lưu huỳnh 13 → 56,7 t.
- **Phân loại:**
  - **Tăng trưởng (NPV0, V4a):** tăng công suất; FO → Jet/xăng/PP; linh hoạt dầu thô. **GHDT/DHDT/HGU** xếp ở đây ở mức 0,10 vì là chi tiêu tự nguyện (không bắt buộc) + bằng chứng tạo giá trị độc lập (lưu huỳnh thu hồi ×4,4 ⇒ chạy dầu chua hơn, rẻ hơn) — xem 1A-A2.
  - **Tuân thủ (dòng tiền ra, V4b/D3):** cụm môi trường SRU3/4 + SWS2 + ARU2 (mục tiêu 3 "lộ trình bắt buộc").
  - **Euro V nhiên liệu:** chưa thấy văn bản bắt buộc mức 5 với nhà sản xuất ⇒ mức 0,40 (nếu bắt buộc, GHDT/DHDT/HGU thành tuân thủ). Mức 0,75 = giả thuyết "phần lớn là tuân thủ" của skeptic r1.
- **Tỷ trọng chi phí từng cụm không công bố** ⇒ mức 0,10/0,40/0,75 và xác suất 0,50/0,35/0,15 là **[UL]** — trục kịch bản, không phải số đo.
- **Cách trừ:** s × (đã ghi sổ 5.285,2 [CIP mở rộng 2.137,7 + ứng nhà thầu 2.601,2 + GPMB 546,3] + còn chi 33.719,3 chiết khấu 1,5 năm ở Ke) × 0,945 (lá chắn thuế khấu hao 10% [UL]). Theo đ/cp: **s=0,10 ⇒ −626 · 0,40 ⇒ −2.504 · 0,75 ⇒ −4.695**; kỳ vọng 30,25% ⇒ −1.885.
- Không có IRR/hợp đồng đầu ra kiểm được ⇒ không cho NPV dương phần tăng trưởng.

### 3.3 Cấu phần (đ/cp, Ke 13,5%)
Tiền ròng 9.012 · cố định (tiền ròng + CIP + khoản ghi sổ mở rộng − KHCN − KTPL − NCI + VAT PV) **11.005** · nhà máy XẤU 3.781 / CƠ SỞ **5.808** / TỐT 8.848 · LN vượt XẤU −284 / CƠ SỞ **1.960** / TỐT 4.662 · WC vượt (không gồm VAT) 4.040 tỷ trục 0/27/54% · tuân thủ kỳ vọng −1.885.
Kịch bản giữa trục: **XẤU 12.826 · CƠ SỞ 17.097 · TỐT 22.840**.

### 3.4 Độ nhạy (sau CK 5 tỷ)
- **r (V1):** +100bp 16.510 (−2,2%) · +50bp 16.691 · −50bp 17.095 · −100bp 17.321 (+2,6%). Dải Ke nội địa 12,3–13,4% (V2) = −120bp…−10bp ⇒ tâm ~16.930–17.370 (ước lượng nội suy). Nhạy thấp vì ~65% giá trị là khoản cố định.
- **Tỷ trọng tuân thủ cố định:** 0 ⇒ 18.771 · 0,10 ⇒ 18.148 · 0,40 ⇒ 16.278 · 0,45 ⇒ 15.967 · 0,75 ⇒ 14.097 · 1,0 ⇒ 12.539. **TRÊN vùng ở mọi mức** (P90 cao nhất 24.619 khi s=0 < 26.250).
- **VAT khấu trừ:** thu hồi 50% ⇒ 16.328 · 0% ⇒ 15.770. **Trích quỹ KHCN 10% thu nhập tính thuế 2026:** 16.144.
- **Bản A (giữ lãi tỷ giá trong lõi, +402):** 17.465. **MBV mất trắng:** 16.342. Bản trọng số đối xứng: 17.421 (P90 23.996). Moat WIDE giả định (RONIC 20%, g 4%): 17.694 (thông tin).
- 1 USD/thùng GRM bền ≈ 1.266 tỷ LN/năm ≈ **1.870 đ/cp**.

### 3.5 Hai nền (V6) — chỉ HIỂN THỊ
- **V_ngắn** = LNST chuẩn hoá (trung vị 2023-25 = 5.213,6 tỷ [BQ]) × (1 − g/ROE)/(r − g), g = 0 ⇒ **7.713 đ/cp**.
- **V_dài (FCFE DCF): không tính** — mô hình là tổng-các-phần; FCFE 2026-28 bị chi phối bởi capex mở rộng 39 nghìn tỷ.
- Chênh V_ngắn vs tâm 16.886: ln(2,19) = 0,78 > ln2. **Nguồn chênh:** V_ngắn vốn hoá cả lãi tiền gửi (sau thuế ~3–4%/năm) ở Ke 13,5%, tức định giá 45 nghìn tỷ tiền ròng chỉ ~25% mệnh giá; DD cộng tiền ròng theo mệnh giá. Vùng đọc mở rộng [7.713; 22.451] — vẫn TRÊN vùng ở giá tham chiếu. Tâm/vùng/nhãn vẫn từ mô hình DD.

## 4. Cờ tự động của hệ

| Cờ | Kết luận | Lý do bằng số |
|---|---|---|
| DCF auto RICH 21.359 | **THẬT** về hướng | Tâm DD 16.886, P90 22.451 < giá 26.250 |
| PE TTM 4,74 "rẻ" | **NHIỄU** | LN TTM 27.754 tỷ ≈ 6,9–7,9 lần LN lõi 3.493–4.012; PE chuẩn hoá (vốn hoá − tiền ròng)/4.012 ≈ 21,5 |
| LAG_HI | **THẬT về số, KHÔNG BỀN** | +888% YoY do crack + tồn kho; giá sau công bố −8,7% (28/10 → 06/11) |
| ADV | **THẬT** | ADV250 trung vị 260,6 tỷ, ADV60 257,1 tỷ [BQ] |

## 5. Rủi ro & điều đổi nhận định (HAI chiều)
**Rủi ro số 1:** biên lọc mean-revert (Hormuz mở, K2 p0,35) + TA6 2027 + lỗ tồn kho; KH 2026 điều chỉnh LNST 18.579 < 9T thực 24.902 (đọc là kế hoạch hành chính; XẤU dùng Q4 −2.000 vượt nền).
**Rủi ro số 2:** tỷ trọng tuân thủ dự án mở rộng ≥ 0,40 (Euro V bắt buộc / cụm môi trường đắt hơn) ⇒ tâm 14.100–16.300.
**Rủi ro số 3:** VAT khấu trừ không được hoàn/khấu trừ (đầu ra không chịu thuế) ⇒ tới −1.116 đ/cp.

**Đổi lên:** giá ≤ 22.400 ⇒ TRONG vùng; ≤ 14.353 ⇒ luật 4 · crack TE ≥ 45 bền đến Q3/2027 sau khi Hormuz mở ≥ 2 quý (~+1,5 USD/thùng ≈ +2.800 đ/cp, ước lượng) · BSR công bố cơ cấu tổng mức đầu tư cho thấy cụm môi trường < 10% hoặc IRR/hợp đồng đầu ra ⇒ tâm tới 18.148–18.771 · thuế NK MFN xăng dầu khôi phục 01/01/2027.
**Đổi xuống:** crack TE T3/2027 < 35 hoặc ULSD−Brent T9/2027 < 50 (F4 p0,65) · Q4/2026 lỗ ≤ −3.000 tỷ · văn bản bắt buộc Euro V nhiên liệu cho nhà sản xuất · tổng mức đầu tư tăng tiếp · nhà nước thu LN bất thường · quyết toán CPH ra số phải nộp (WARNING).

## 6. Vị thế & lợi thế cạnh tranh (5F, V5)
Làm đầy đủ 09/11/2026 (< 12 tháng) ⇒ **tái dùng** rev2 mục 6: `moat_tier = NARROW`, `moat_type = ADMIN/LOCATION`, không bền ⇒ RONIC = Ke. Kiểm nhanh 23/11: (i) ROIC_Min5Y −1,0% [BQ] ⇒ vẫn trượt điều kiện ROIC−Ke dương liên tục; (ii) dự án mở rộng (+15,5% công suất, 2028) nâng rào cản quy mô nhưng không đổi vị thế người nhận giá MOPS. Rủi ro số 1 của moat: Lực 6 Nhà nước (thuế NK/BVMT, lệnh chạy tối đa, PVN 92,12%). Dòng `moat_tags.csv` đề xuất giữ như rev2 (không tự sửa file).

## 7. Thanh khoản & sizing (V3, V8)
ADV250 trung vị 260,6 tỷ, σ ngày 3,34% [BQ]. CK thanh khoản σ·√(Q/ADV): 5 tỷ **0,46%** (1,9% ADV, thoát 1 phiên ở 10–20% tham gia); 40 tr 0,04%. Free float ~7,9% nhưng thanh khoản thực cao ⇒ không phải ràng buộc. Nhãn theo giá trị SAU CK (5 tỷ). Sizing: mục 0.

## 8. Pháp lý / quản trị — chỉ WARNING (không vào base)
- Deloitte soát xét 6T/2026 chấp nhận; **nhấn mạnh** quyết toán CPH (2018) chưa được phê duyệt. FY2025 KT: không có bản gốc trong thư mục (`audited_fy_missing=true`).
- MBV (ex-OceanBank) 2.735,6 tỷ tạm dừng giao dịch; BĐH đánh giá sẽ giao dịch lại khi có quy định NHNN [TM5]. Base giữ nguyên; độ nhạy mất trắng −544 đ/cp.
- SOE PVN 92,12%; giao dịch bên liên quan lớn (PV OIL 21,9% DT 9T).

## 9. Còn mở / không kiểm chứng được
- Cơ cấu chi phí 39.004,5 tỷ theo cụm: **không kiểm chứng được** ⇒ trục kịch bản; 0,10 → 0,75 làm tâm 18.148 → 14.097.
- Phân loại GHDT/DHDT/HGU (luật V4a vs "không tạo doanh thu"): **cần Mike/user phán** — độ nhạy −919 nếu dồn kỳ vọng 0,45.
- Khả năng hoàn VAT khấu trừ và kỳ hạn: chưa có thuyết minh riêng; base 100% PV 1 năm, độ nhạy 0–50%.
- Chi phí TA6 giả định = TA5 (6.230,5 tỷ) [UL]; nếu TA6 chỉ bằng 60% TA5 ⇒ LN vượt 2027 +~2.490 tỷ (≈ +460 đ/cp, ước lượng). Chu kỳ TA 4 năm [UL].
- Tỷ lệ trích KHCN/KTPL lịch sử, BCTC KT FY2025, văn bản Euro V, tin pháp lý T11/2026: không kiểm chứng được trong phiên.
- `dd_assumptions_lint.py`: chế độ cảnh báo (rc=0) — file khoá theo định dạng cũ, chưa chuyển schema v1; cảnh báo L9 về `adv_*` là dương tính giả (`adv_312` = người mua trả trước, `adv_engineering` = ứng trước nhà thầu).

## 10. File
`src/` (6 PDF, md5 khớp `src/SRC_md5.txt`) · `src_rev3/` (QĐ968, `SRC_rev3_md5.txt`) · `rev3/png/` (ảnh trang PDF đã đối chiếu) · `calc/assumptions_rev4.json` (md5 `902291f3…`) · `calc/model_bsr_rev4.py` (md5 `214ecf78…`; chạy 2 lần, `model_out_rev4.json` md5 `6f720774…` trùng) · `calc/LOCK_post_md5_rev4.txt`. Chạy: `cd calc; OMP_NUM_THREADS=1 /home/trido/thanhdt/wc_venv/bin/python -I model_bsr_rev4.py` (biến thể: `BSR_COMP_SHARE=`, `BSR_VAT_REC=`, `BSR_FUND_ACCR=`, `BSR_CORE_ADD=402`, `BSR_MBV_LOSS=1`).
