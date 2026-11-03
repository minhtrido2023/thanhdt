# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương, UPCOM) · bản TRUNG DUNG · as-of 03/11/2026 · job `Taylor_20261103_082601` (r1) → vòng 2 `Taylor_20261103_085129` (đã áp đính chính skeptic, Phụ lục E)

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán. Không chấm §2.5 fear-buy. User quyết.
> **Nguồn gốc (tải từ vlxdbd.com.vn, mục quan-he-co-dong, 03/11/2026, lưu `src/`):**
> **[HN-Q3]** BCTC hợp nhất Q3/2026 (lập 29/10, CBTT 30/10; có text) · **[R-Q3]** BCTC riêng Q3/2026 · **[GT]** 2 CV giải trình LNST Q3 (riêng 20/10, HN 30/10)
> · **[SX6T]** BCTC HN soát xét 6T/2026 (AASCs, scan EN, đọc bằng ảnh trang) · **[KT25]** BCTC HN kiểm toán 2025 (AASCs, scan EN) · **[BCTN25]** Báo cáo thường niên 2025
> · **[ĐHĐCĐ]** tài liệu + biên bản/NQ ĐHĐCĐ 15/04/2026 · **[NQ69]** NQ HĐQT 69 (30/07/2026) · **[QT6T]** Báo cáo quản trị 6T/2026 · **[WEB]** trang đơn vị trực thuộc trên website công ty.
> **[BQ]** `tav2_bq.ticker_financial` (chỉ cột nền tảng; **dòng 2026Q3 của MVC trong BQ là bản lặp Q2 — lệch nguồn, không dùng**) · **[NNC-DD]** `../dd_NNC_20261030/REPORT.md` §13 + `calc/valuation_v2.py` (khung tái dùng, tham số NNC tự kiểm lại).
> **Ngành (đọc MÙ):** [Bobby-đá] `kb/data_registry/market-state/sector_read_da_xay_dung_nam_bo_20261030.md` · [Bobby-gạch/ICD] `sector_read_gach_nung_icd_binhduong_20261103.md` (xuất hiện trong phiên, đã đọc trước khi chốt).
> **Mù giá:** mô hình dựng không truy vấn giá/vốn hoá MVC; output khoá md5 `calc/LOCK_md5.txt` (08:36:11Z) TRƯỚC khi so giá (`calc/compare_px.py`). Giá tham chiếu chỉ ở §7.6.
> Tính toán: `calc/valuation.py` → `valuation_out.txt`, `valuation_grid.csv`, `sotp_detail.csv`; `calc/px_stats.sql` → `px_stats_out.txt`.
> Đơn vị: tỷ đồng nếu không ghi khác. 100 tr cp (vốn điều lệ 1.000 tỷ [HN-Q3 V.22]). Giả định tự đặt gắn **(ước lượng)**.

## 0. Kết luận

**Verdict trung dung (1 dòng): Ở 13.700 (đóng cửa 02/11/2026), MVC nằm DƯỚI tâm giá trị (~19.500 đ/cp) và ở sát cận dưới vùng hợp lý
~14.600–24.500 — nghiêng rẻ, nhưng biên an toàn phụ thuộc gần như hoàn toàn vào hai thứ không xác minh được: đường giá đá cụm Đồng Phú–Phú Giáo
sau 2028 và việc dự án 2 mỏ mới 1.500 tỷ có tạo ra giá trị hay không.**

| Vùng giá (đ/cp) | Đọc |
|---|---|
| ≤ ~14.500 | Dưới vùng hợp lý ở cả hai đường giá — trừ khi tin P(tiêu cực) > ~30% với giá đá danh nghĩa đi ngang |
| ~14.500 – 24.500 | Trong vùng — vị trí phụ thuộc giả định giá danh nghĩa phẳng (cận dưới) hay giữ giá trị thực (cận trên) |
| ≥ ~24.500 | Trên vùng — cần cả giá giữ giá trị thực LẪN mỏ mới chạy ≥ 80% công suất với giá không sập |

Ba kịch bản (r 13%, chiết khấu holding 15% trên phần NNC; cận phẳng … cận thực): **tích cực (25%) 34.500–51.400 · cơ sở (50%) 9.400–19.900 ·
tiêu cực (25%) 4.900–6.700**. Lưới 18 tổ hợp (2 đường giá × r 11/13/15% × holding 0/15/30%): min 12.300 · P10 13.500 · trung vị 18.900 · P90 27.000 · max 29.500.
Phân bố **lệch phải mạnh**: tâm kéo lên bởi kịch bản tích cực; kịch bản cơ sở ở đường giá phẳng (9.400) thấp hơn giá hiện tại.
**Vòng 2 (áp đính chính): tâm 19.540 và vùng 14.600–24.500 KHÔNG đổi** (mô hình không đổi; khoá md5 còn nguyên). Bổ sung phía xấu ngoài mô hình: cụm công nghiệp ≤500 tỷ + mua NNC lên 51% ⇒ cam kết vốn
tổng ~1,75 nghìn tỷ (nợ ròng ~2028 ≈1,4–1,5 nghìn tỷ, D/E ~0,9–1,0); mỏ mới trễ 1 năm ở kịch bản cơ sở: tâm 19.070 (−470); P/E TTM ex-hoàn nhập Q4/25 ≈ 4,9–5,0x (không phải 4,5x).

**MVC là gì (đính chính tiền đề brief):** không phải "công ty mẹ sống bằng liên kết". 9T/2026 **70% LNST hợp nhất là hoạt động trực tiếp**
(LNTT trực tiếp ~212 / tổng 282, chủ yếu **mỏ đá Tân Lập 1,4 tr m³/năm ở Đồng Phú — cùng cụm với mỏ Mũi Tàu của NNC**); liên kết (NNC là chính) ~30%.
ICD Hoa Lư là **công ty con 100%** (vốn điều lệ **51 tỷ**, đã góp 44,8) — con số "51" trong brief là vốn điều lệ, không phải tỷ lệ sở hữu [SX6T tr.11].
Biến cố lớn nhất năm 2026 chưa thấy trong brief: **MVC trúng đấu giá 2 mỏ đá mới (19/03/2026)** — Tam Lập 1 khu 1 (Phú Giáo, 14,81 tr m³, 1,0 tr m³/năm)
và Minh Hòa (3,95 tr m³, 0,5 tr m³/năm), tổng đầu tư **1.500 tỷ**, vay tối đa 75%, vận hành 2028 [ĐHĐCĐ NQ 03]. Đây chính là "cung Tam Lập 2028"
mà DD NNC coi là rủi ro vách giá — nay MVC vừa là chủ nguồn cung mới, vừa nắm 44% NNC.

**Mốc kiểm chứng khoá trước** (chấm theo CẢ HAI chiều, §10): (1) BCTC Q4/26 (~20–30/01/2027); (2) Q1/27 (~04/2027); (3) GP khai thác 2 mỏ mới
(kế hoạch "hoàn tất pháp lý 2027"); (4) CBTT mua thêm NNC lên 51% (ĐHĐCĐ đã uỷ quyền); (5) giá đá công bố Đồng Nai Q2/27 (F2 Bobby-đá);
(6) NQ chi cổ tức 2026 (chính sách 50% LNST riêng vào quỹ cổ tức).

**3 điểm yếu lớn nhất của chính báo cáo này:**
1. **Không có tách doanh thu đá / gạch / xăng dầu** (BCTC gộp "thành phẩm" + "hàng hoá"); LN gộp mỏ đá ~265 tỷ/năm là **suy ra bằng phép trừ** (ước lượng),
   sản lượng 1,3 tr m³ và chi phí 130k/m³ là hiệu chỉnh ngược, không phải số công bố.
2. **Hạn giấy phép mỏ Tân Lập và hạn thu phí BOT ĐT743 CHƯA XÁC MINH** — đặt theo kịch bản (2035/2040/2045; 2–8 năm). Độ nhạy hạn GP: −1.800 / +460 đ/cp.
3. **Tổng đầu tư 1.500 tỷ cho 2 mỏ mới** chỉ có con số tổng trong NQ ĐHĐCĐ (không có cơ cấu: đất / tiền trúng đấu giá / thiết bị); mô hình coi 1.500 là
   ngân sách đủ. 1.500 / 18,75 tr m³ trữ lượng ≈ **80k/m³**, nhưng 1.500 gồm ~432 đất (một phần ~30 ha bãi công nghiệp) còn 244,8 của Gia Cảnh KHÔNG gồm tiền cấp quyền [Bobby-đá]: loại đất ≈ **57k/m³ (~3,5× tiền lệ 16k/m³)** — hướng đúng (trả đắt), bội số nhỏ hơn 5×; nếu đúng là trả đắt, mỏ mới là chỗ phá giá trị.

---

## 1. Kiểm chứng tiền đề brief — ĐÚNG MỘT PHẦN

| Tiền đề | Kiểm bằng số | Kết quả |
|---|---|---|
| "Công ty mẹ, nhiều liên kết ghi theo VCSH" | Liên kết 9T: lãi LK 59,07 [HN-Q3 KQKD mã 25] + cổ tức LK hạch toán vào DT tài chính 10,57 [HN-Q3 VI.3] = **69,6 = 30%** LNST HN 231,8 | Nửa đúng — trọng tâm là mỏ đá trực tiếp |
| NNC 44,07% | 9.659.170 cp / 21,92 tr [HN-Q3 V.12]; đầu năm 9.545.270 (43,55%) — **mua thêm 113.900 cp, 6,01 tỷ** trong 9T [LCTT mã 25] | ĐÚNG; ĐHĐCĐ uỷ quyền mua lên **51%** |
| MCC 29,9%, NHC 30,04% | MCC 1.500.012 cp = 29,9% (riêng) / 30,08% (HN); NHC 913.794 cp = 30,04% | ĐÚNG; cả hai rất nhỏ (vốn chủ MCC ~74 tỷ, NHC ~60 tỷ [BQ]) |
| ICD Hoa Lư 51% | **100%** sở hữu, vốn điều lệ 51 tỷ, đã góp 44,80, còn 6,20 chưa góp; KKT cửa khẩu Hoa Lư (Lộc Thạnh, Đồng Nai) [SX6T tr.11] | SAI tỷ lệ |
| "Cảng cạn?" | Dự án ICD 25 ha **chưa có đất**: tỉnh đang duyệt giá đất thuê trả một lần, dự kiến xong Q2/2026 [BCTN25 III.1; ĐHĐCĐ]; CIP ICD 37,69 (31/12/25) → **0** (30/06/26) [SX6T 6.11] | Chưa vận hành; biến động CIP chưa giải thích |
| "Mảng BĐS trực tiếp" | 4 dự án nhà ở (Lai Hưng 6,1 ha, Mỹ Phước 3,1 ha, NOXH Mỹ Phước 2,4 ha, Long Nguyên 11,9 ha) — **tất cả chưa có chủ trương đầu tư** [ĐHĐCĐ] | Option, chưa phải dòng tiền |
| "Xây dựng" | Không có doanh thu xây lắp; DT gồm thành phẩm (đá+gạch), hàng hoá (xăng dầu), BOT, dịch vụ [KT25 7.1] | Không có hợp đồng xây dựng ⇒ không có rủi ro ghi nhận POC |

## 2. Chất lượng lợi nhuận

**Doanh thu/LN gộp theo nhóm** [KT25 7.1–7.2; SX6T 9.4]:

| | 2024 | 2025 | 6T/2026 |
|---|---|---|---|
| DT thành phẩm (đá + gạch) | 335,9 | **523,8** | 401,4 (gộp với hàng hoá) |
| LN gộp thành phẩm | 79,8 | **138,5** (26,4%) | 149,9 (37,3%, gộp hàng hoá) |
| DT hàng hoá (xăng dầu) / LN gộp | 184,7 / 11,8 | 152,1 / 10,6 | — |
| DT BOT / LN gộp | 56,8 / 31,9 | 54,7 / 31,9 | 26,9 / 17,1 |
| DT dịch vụ khác / LN gộp | 23,3 / 3,7 | 16,6 / 6,3 | 9,5 / 4,8 |
| **Tổng DT / LN gộp** | 600,9 / 122,2 | **747,3 / 187,3** | 437,9 / 171,7 |

**Quý và 9T** [HN-Q3 KQKD]: DT Q3 221,5 vs 192,3 (+15%); LN gộp **79,5 vs 38,6 (+106%)**, biên 35,9% vs 20,1%. 9T: DT 659,4 vs 525,3 (+26%);
LN gộp 251,2 vs 128,0 (+96%), biên 38,1% vs 24,4%. LNST Q3 81,3 vs 35,6 (+128%); 9T **231,8 vs 104,1 (+123%)** [GT-HN: "DT ngành đá, ngành gạch tăng; lãi LK tăng"].

**Tách trực tiếp / liên kết (9T/26):** LNTT 282,0 − lãi LK 59,07 − cổ tức LK 10,57 = **LNTT trực tiếp 212,4** (9T/25: 120,0 − 32,9 − ~9,5 ≈ 77,6 ⇒ ×2,7).
Q3: 94,06 − 19,84 − 10,57 = 63,7 (Q3/25 ≈ 20,9). ⇒ động lực tăng trưởng là **biên gộp mỏ đá** (giá), không phải liên kết.
Ước suy LN gộp mỏ đá (ước lượng, phép trừ): 9T "thành phẩm+hàng hoá" 251,19 − BOT 25,67 − dịch vụ 6,93 = 218,6; trừ xăng dầu ~8 và gạch ~10 (ước lượng) ⇒ **đá ~200/9T ≈ 265/năm**.

**Hợp nhất vs riêng:** LNST riêng 9T **211,9** vs HN 231,8 [GT]. Riêng có **hoàn nhập dự phòng đầu tư tài chính 39,0** (48,05 → 9,05) trong 6T — CP tài chính riêng 9T = **−26,78** [R-Q3]
⇒ **riêng ex-hoàn nhập: LNTT ≈ 223,1, LNST ≈ 180,7** (đối chiếu: thuế hoãn lại riêng 9T 7,91 ≈ 20% × 39,0 ⇒ khoản hoàn nhập đã chịu thuế; LNTT riêng 262,1 = LNST 211,9 + thuế hiện hành 42,3 + hoãn lại 7,9 [R-Q3]). HN không bị ảnh hưởng ở LNTT (liên kết theo VCSH); HN lại **gánh thuế hoãn lại 7,96 của khoản này** (khớp 7,91 riêng) ⇒ LNST HN 9T có một khoản phi thường ~−8 do hợp nhất (chiều: làm GIẢM LNST HN; bản chất chưa xác minh). **Chênh HN − riêng thật = lãi LK giữ lại (không về tiền).**
Riêng: đầu tư ICD 44,80 / MCC 17,44 / NNC 319,77 / NHC 28,14 giá gốc [R-Q3 V.12]; dự phòng còn 9,05 chưa phân bổ theo từng khoản (CHƯA XÁC MINH khoản nào).

**Tiền thật từ liên kết:** cổ tức nhận 9T **10,57** (NNC 9,66 = 1.000 đ/cp; NHC 0,91) vs phần LN ghi nhận 69,6 ⇒ **15% về tiền**. NNC chuyển phần lớn LN vào quỹ ĐTPT
([NNC-DD] E11: quỹ ĐTPT NNC 87,3 → 353,3). Tức là ~30% LNST HN của MVC là LN "trên giấy" ở cấp mẹ — chỉ thành tiền nếu NNC đổi chính sách cổ tức hoặc MVC hợp nhất NNC.

**Một lần vs bền:** thu nhập khác 9T 7,73 (lãi thanh lý TSCĐ 2,05 ở Q3) — nhỏ. Thuế hoãn lại 9T 7,96 (chi phí, tài sản thuế hoãn lại 8,49 → 0,58). **Hoàn nhập dự phòng giảm giá HTK 4,89 (4,889 → 0)** [HN-Q3 V.6] làm tăng LN gộp 9T một lần (cũng nằm trong hiệu chỉnh GP đá ~200/9T ở trên ⇒ GP đá bền thực ≈ 195; nằm trong dải độ nhạy chi phí mỏ ±15%). DT tài chính lãi tiền gửi 9T ~13,7.
**Kế hoạch:** NQ69 ký 30/07/2026, TRƯỚC Q3 ⇒ con số 294 (H2 LNTT 108) là kế hoạch cũ, không phải guidance Q4 (Q3 một mình 94 LNTT HN = 87% kế hoạch H2). Mô hình đặt Q4 trực tiếp 50 sau thuế (ước lượng), chấm ở mốc (1).

## 3. Bảng cân đối — net cash THẬT [HN-Q3 tr.1–3, V.1, V.2, V.19, V.20]

| Khoản | 30/09/2026 | 31/12/2025 |
|---|---|---|
| Tiền + tương đương | 117,40 | 33,21 |
| Đầu tư HTM ngắn hạn (tiền gửi 266,10 + lãi dự thu 8,32; cho vay 0 vs 62,32) | 274,42 | 421,04 |
| HTM dài hạn (trái phiếu BIDV 2 năm, cầm cố) | 20,00 | 20,00 |
| − Vay ngắn hạn (BIDV 451,87; MB, OCB, Vietinbank) | **−461,85** | −256,81 |
| **= Net cash thô** | **−50,0** | 217,4 |
| − Cổ tức phải trả (600 đ/cp, trả 09/10/2026 — sau ngày khoá sổ) | −60,00 | — |
| − Quỹ khen thưởng phúc lợi | −6,52 | −2,80 |
| **= Nợ ròng sau nghĩa vụ ngoài vận hành** | **−116,6 (−1.166 đ/cp)** | |

- **Đảo chiều từ tiền ròng sang nợ ròng trong 9 tháng:** CIP "chuyển nhượng QSDĐ để thực hiện dự án [mỏ đá]" **34,98 → 246,93 (30/6) → 431,86 (30/9)** [SX6T 6.11; HN-Q3 V.11],
  tài trợ bằng **vay vốn lưu động ngắn hạn** BIDV (HĐ 160/2024: hạn mức 350 tỷ, kỳ hạn 12 tháng, mục đích "bổ sung vốn lưu động" [KT25 6.18]). Dư nợ BIDV 451,9 > hạn mức 350 của HĐ cũ ⇒ đã có HĐ mới/nâng hạn mức — CHƯA XÁC MINH.
  **Lệch kỳ hạn:** tài sản dài hạn (đất mỏ) tài trợ bằng vay ngắn hạn — WARNING thanh khoản, giảm nhẹ vì tiền gửi 266 + trái phiếu 20 đang cầm cố cho chính khoản vay.
- **Cam kết vốn còn lại (ước lượng):** 1.500 − 438,4 đã chi (đất 431,86 + tiền cấp quyền 6,56) ≈ **1.062**; hạn mức vay dự án 1.125 (75%) [ĐHĐCĐ]. **ĐHĐCĐ 2026 (Vấn đề 4.3) còn duyệt thêm
  CỤM CÔNG NGHIỆP đến 500 tỷ và uỷ quyền mua NNC lên 51% (~1,52 tr cp × ~47k ≈ 72 tỷ)** — hai khoản này KHÔNG có trong mô hình SOTP (chưa có kế hoạch/giá). Cộng nợ ròng hiện tại 116,6 + 1.062 + 500 + 72 ≈ **1,75 nghìn tỷ
  tổng cam kết trước dòng tiền hoạt động 2027–28** (`calc/valuation_v2_out.txt` (3)); ước nợ ròng ~2028 **≈ 1,4–1,5 nghìn tỷ** sau dòng tiền (ước lượng) trên VCSH 1.546 ⇒ **D/E ~0,9–1,0** (không phải 0,6–0,7) — trước khi mỏ mới có doanh thu.
- **Mục đột biến:** tạm ứng **60,63** (đầu năm 50,09) [V.5] — lớn, không thuyết minh đối tượng (WARNING); dự phòng phải thu khó đòi 12,10. Chi phí SXKD dở dang **152,4** [V.6]
  (tồn kho lớn so DT; nhiều khả năng đá/tầng phủ mỏ — CHƯA XÁC MINH). Phải trả người lao động 12,92 → 0,09. Thuế TNDN phải nộp 36,91.
- **Chi phí trả trước dài hạn 263,7**: bốc tầng phủ CN Bình Phước 39,80; tiền cấp quyền mỏ Tân Lập **48,30** (43,26 đầu năm — nộp thêm 2026); bốc đất sét Long Nguyên 2,01;
  thăm dò 0,62; bốn dòng còn lại có nhãn [HN-Q3 V.13, đọc lại 03/11]: **115,05 = QSDĐ CN Bình Phước để khai thác đá**; **7,75 và 21,89 = đất/đền bù NM gạch Long Nguyên 1 và 2**; **1,45 = đất mở rộng Long Nguyên 2 (chưa xây)**; "khác" 26,86 chưa phân tách.
- TSCĐ vô hình: quyền thu phí BOT ĐT743 nguyên giá **200,25 đã khấu hao hết** [V.9] ⇒ DT BOT gần như toàn LN tiền mặt (trừ duy tu).

## 4. Dòng tiền [HN-Q3 tr.5]

- **CFO 9T = 155,1** vs LNST 231,8 (0,67x); so với **LNST trực tiếp ~162** (ước lượng: 231,8 − 69,6) ⇒ ~0,96x, **nhưng chưa đánh giá được chất lượng tiền của mảng trực tiếp**: tiền thu bán hàng chỉ 221,1 so DT 659,4 [LCTT mã 01];
  "thu khác 608,2 / chi khác 325,4" [mã 06/07] rất lớn so DT (gộp ký quỹ/VAT/tạm ứng?) — CHƯA XÁC MINH bản chất; chỉ kết luận được khi rõ thu/chi khác.
- **Capex 9T 445,0** (9T/25: 19,1) — gần hết là đất mỏ mới. FCF 9T ≈ **−290**, tài trợ: rút HTM ròng +144,4, vay ròng +205,0. Chưa trả cổ tức trong 9T (60 trả 09/10).
- **Phải thu KH 22,96** (đầu năm 38,09; DSO ~10 ngày, ước lượng); NM gạch Bến Cát chiếm 14,70. Không có dấu hiệu nợ đọng từ dự án công.
- **Cổ tức:** 2024 450 đ (45 tỷ), 2025 600 đ (60 tỷ, 49% LNST riêng 2025 122,5) [ĐHĐCĐ TTr 01]. Chính sách 2026: **50% LNST riêng vào quỹ cổ tức**, mức chi do ĐHĐCĐ 2027 quyết.
  LNST riêng 9T 211,9 gồm ~31 hoàn nhập phi tiền sau thuế (ex: ~180,7). Tiền lệ: quỹ cổ tức 2025 trích 70% (85,76) nhưng chỉ trả 60, chuyển 26,69 sang quỹ đầu tư phát triển [biên bản ĐHĐCĐ] ⇒ "quỹ" ≠ "trả". Cổ tức 2026 ≥ 1.000 đ/cp là khả năng, không phải mặc định (ước lượng) — và cạnh tranh với phần vốn chủ ~375 tỷ (25% của 1.500) cho mỏ mới + cụm công nghiệp.

## 5. Tài sản lõi

| Tài sản | Số liệu | Nguồn |
|---|---|---|
| **Mỏ đá Tân Lập** (CN Bình Phước, Đồng Phú) | Dự án 90 ha, **1,4 tr m³ đá/năm**; sản phẩm đá + cát nghiền. Cùng cụm Đồng Phú với Mũi Tàu (NNC). Nhập máy nghiền 450 t/h (2025). Mua 2 dây chuyền 450 & 350 t/h của NHC giá trị còn lại **51,09** mới là **uỷ quyền ĐHĐCĐ (TTr 05), chưa xác nhận đã thực hiện** (máy móc mua mới 9T chỉ 39,32 [HN-Q3 V.8]; NNC cũng mua máy nghiền 350 t/h từ NHC 21,29 [NNC-DD] — chưa kiểm có cùng tài sản không). **Hạn GP, trữ lượng còn lại: CHƯA XÁC MINH** | WEB; ĐHĐCĐ TTr 05 |
| **Tam Lập 1 – khu 1** (Phú Giáo) — trúng đấu giá 19/03/2026, QĐ 2083/QĐ-UBND 07/04/2026 | 29,15 ha + ~15 ha bãi; trữ lượng huy động tới −20 m **14,81 tr m³ nguyên khối**; **1,0 tr m³/năm** (~1,42 tr m³ thành phẩm, theo tỷ lệ NNC) | ĐHĐCĐ NQ 03 |
| **Minh Hòa** (Minh Thạnh) — QĐ 2080/QĐ-UBND | 14,74 ha + ~15 ha; **3,95 tr m³**; 0,5 tr m³/năm (~8 năm) | ĐHĐCĐ NQ 03 |
| Tổng 2 mỏ mới | Đầu tư **1.500**, vay ≤1.125 (BIDV, Vietinbank, MB); pháp lý xong 2027, vận hành **2028**. Đã chi 438,4 | ĐHĐCĐ; HN-Q3 V.11; SX6T 6.11 |
| **Gạch ngói Bến Cát** | 2 cơ sở: Mỹ Phước 2,5 ha (**dừng 08/2025**, chuyển dự án nhà ở/NOXH), Long Nguyên 12,5 ha; tổng 200 tr viên/năm; mỏ sét 20 ha, xin gia hạn tới 2030 (100k m³/năm); có dây chuyền gạch không nung | WEB; BCTN25; NQ65 |
| **BOT ĐT743** | Trạm Bình Thắng dừng 22/10/2024 (hết HĐ); còn Bình Thung, Lái Thiêu (~20 km tuyến quản lý). DT ~55/năm, LN gộp ~32. **Hạn thu: CHƯA XÁC MINH**; chi phí duy tu vỉa hè Bình Thung–Lái Thiêu tăng theo yêu cầu NN | WEB; BCTN25; [baodauthau](https://baodauthau.vn/du-an-bot-binh-thung-tan-van-binh-duong-dung-thu-phi-tu-ngay-22102024-post165015.html) |
| **Đất dự án nhà ở** | Lai Hưng 6,1 ha (đang giải trình quy hoạch với Sở TC); Mỹ Phước 3,1 ha (quy hoạch tổng mặt bằng); NOXH Mỹ Phước 2,4 ha; Long Nguyên 11,9 ha (đã có GCN QSDĐ, xin chủ trương). Giá gốc tổng: CHƯA XÁC MINH (lô Long Nguyên 59.895 m² nguyên giá 15,81; lô Bến Cát 30.161 m² 7,65 — đang thế chấp BIDV) | ĐHĐCĐ; KT25 6.18 |
| **ICD Hoa Lư** | Công ty con 100%, KKT cửa khẩu Hoa Lư (biên giới Campuchia) — **khác loại** với ICD gắn cảng biển BD–ĐN mà Bobby đọc; HĐQT ký HĐ cho ICD làm nhà phân phối VLXD/xăng dầu (NQ 66, 29/11/2025) | SX6T; BCTN25 |
| Xăng dầu | Mua của Thanh Lễ (bên liên quan) 66,81 trong kỳ Q3 [HN-Q3 VII]; cây xăng Long Nguyên xây 2026 | |

## 6. Cổ đông, thanh khoản, kiểm toán

- **Cổ đông lớn** (27/02/2026) [BCTN25 V.3]: Tổng Cty TM XNK Thanh Lễ **25%** (Chủ tịch HĐQT MVC Đoàn Minh Quang đại diện, đồng thời là Chủ tịch Thanh Lễ và Chủ tịch NNC);
  bà Phạm Kim Oanh **24,9%** (TV HĐQT); **CTCP Đá Núi Nhỏ 10,3%**; ông Nguyễn Xuân Thuận 9,6%; Phó TGĐ Nguyễn Quốc Bình 4,23% ⇒ **free float ~26%** (ước lượng).
  HĐQT nhiệm kỳ III (2026–31): Quang, Nguyễn Xuân Hải (mới, thay bà Oanh), Châu (TGĐ), Bộ (độc lập), Nhân. Room ngoại / sở hữu NN: **CHƯA XÁC MINH**.
- **Thanh khoản** [BQ, `calc/px_median_out.txt`]: **ADV trung vị** 20/60/120 phiên **0,49 / 0,19 / 0,17 tỷ/phiên** (trung bình 20 phiên 0,61 bị vài phiên lớn kéo). Mỏng:
  1 tỷ ≈ 5 phiên ADV trung vị-60; 10 tỷ ≈ 53 phiên ở 100% tham gia, **~270–530 phiên ở 10–20% tham gia** ⇒ không ràng buộc ở quy mô nhỏ (≲ 1 tỷ), ràng buộc mạnh ở quy mô vừa và **khi thoát lệnh lúc stress**.
- **Kiểm toán:** AASCs; BCTC riêng 2025 **chấp nhận toàn phần** [BCTN25 IX]; soát xét HN 6T/2026 kết luận chấp nhận, không ngoại trừ/nhấn mạnh [SX6T tr.4]. AASCs cũng kiểm toán NNC.
- Thù lao HĐQT+BKS+BĐH 6T/2026 5,73 tỷ [QT6T]. BĐH không sở hữu cổ phiếu trừ PTGĐ Bình. Không có giao dịch cổ phiếu nội bộ 6T/2026.

## 7. Định giá

### 7.1 Chi phí vốn
Ke nội địa β ~1,1 theo khung 30/10: **12,3–13,4%** (rf chuẩn hoá ~6,75%, ERP nội địa 5,0–6,1%; dải rộng 10,5–14,0%). Dùng **r = 13%** (dải 11–15%) cho dòng tiền
**hữu hạn** (mỏ có trữ lượng/GP, BOT có hạn) — cùng mức với DD NNC để hai mã nhất quán; cộng nhẹ cho rủi ro tập trung 1 cụm mỏ + đòn bẩy dự án. **Không dùng terminal vô hạn.**

### 7.2 Cấu trúc SOTP (`calc/valuation.py`)
- **A. Mỏ Tân Lập:** sản lượng 1,3 tr m³ (2027) → 1,2 (2028+, cơ sở; tốt 1,4; xấu 1,05; rất xấu 0,9); giá bán = **0,87 × giá NNC** cùng kịch bản (kênh phân phối, quy cách — ước lượng hiệu chỉnh
  từ LN gộp ~200k/m³); chi phí tiền mặt 130k/m³ +3%/năm; SG&A phân bổ 40; thuế 20%; hạn GP 2040 (tốt 2045, xấu 2035 — ước lượng).
- **B. 2 mỏ mới:** capex còn lại 1.062 chi 2027–28 (60/40); vận hành 2028 (xấu trễ 1 năm, rất xấu 2 năm); công suất sử dụng 2028/29/30+: tốt 60/100/100%, cơ sở 50/80/80%, xấu 40/50/50%,
  rất xấu 30/40/40%; chi phí 135k/m³ (tiền trúng đấu giá đã trong capex); capex duy trì 3% DT. Ở xấu/rất xấu: **sàn "dừng dự án" = bán lại đất 30% giá gốc (130)** — ước lượng;
  ở cơ sở/tốt: chạy theo NQ ĐHĐCĐ bất kể NPV. **Vận hành 2028 ở kịch bản cơ sở là MÉP LẠC QUAN của độ trễ 2–4 năm đấu giá→sản xuất** (Bobby-đá: "hầu như không ra hàng trước 2028"; F6: P=0,30 có GP trước 06/2027); độ trễ chỉ nằm ở kịch bản xấu — xem độ nhạy 7.4.
- **C. BOT:** 32/năm × (1−20%) trong 5 năm (tốt 8, xấu 3, rất xấu 2) — ước lượng. **D. Gạch + xăng dầu + dịch vụ − phí chung còn lại:** EBIT 9/năm (tốt 20, xấu 0, rất xấu −5) tới 2036.
- **E. NNC 44,07%:** tái dùng khung [NNC-DD v2] (đường giá × sản lượng 4 kịch bản, K = 0,97, LN gộp cho thuê, net cash sau nghĩa vụ Q3/26, CIP Tam Lập khu II ở tốt/cơ sở);
  **thay** cổ phần NHC theo giá bằng sổ sách, **bỏ** cổ phần MVC mà NNC nắm (xử lý riêng). Chiết khấu holding 15% (0/30%).
- **Sở hữu chéo:** V_MVC = D + (1−h)·0,4407·V_NNC; V_NNC = N_ex + 0,103·V_MVC ⇒ giải hệ (không cộng thẳng, không đếm NNC hai lần).
- **F. MCC + NHC:** sổ sách × (1,0 / 0,8 / 0,5 / 0,3); **ICD:** 44,8 × (1 / 0,6 / 0 / 0). **G. Đất nhà ở:** 400 / 100 / 0 / 0 (option thô, ước lượng). Q4/26 trực tiếp +50. Tài chính ròng −116,6.

### 7.3 Kết quả (r 13%, holding 15%, tỷ đồng → đ/cp) [`sotp_detail.csv`]

| Kịch bản (xác suất) | A Tân Lập | B mỏ mới | NNC (sau holding, gồm vòng chéo) | BOT+gạch+khác | Đất+LK nhỏ | Nợ ròng+Q4 | **đ/cp phẳng … thực** |
|---|---|---|---|---|---|---|---|
| Tốt (25%) | 1.337 … 2.011 | 564 … 1.253 | 916 … 1.243 | 218 | 485 | −67 | **34.500 … 51.400** |
| Cơ sở (50%) | 556 … 884 | **−313 … 202** | 470 … 682 | 135 | 159 | −67 | **9.400 … 19.900** |
| Xấu (20%) | 202 … 337 | 130 (sàn) | 208 … 288 | 63 | 20 | −67 | **5.600 … 7.700** |
| Rất xấu (5%) | 14 … 48 | 130 (sàn) | 125 … 142 | 16 | 12 | −67 | **2.300 … 2.800** |
| **Kỳ vọng** | | | | | | | **14.600 … 24.500; tâm 19.500** |

- Cận "phẳng" = giá đá danh nghĩa đi ngang tới hết đời mỏ (giá thực −3%/năm); cận "thực" = giá giữ giá trị thực. Luật 12: cả hai vào dải, tâm = điểm giữa.
- **NNC ex-MVC** (cơ sở): 1.159 … 1.614 tỷ = 52.900 … 73.600 đ/cp NNC — khớp kịch bản cơ sở của [NNC-DD §13] (57.300 phẳng / 78.100 thực) sau khi bỏ cổ phần MVC (~3.800 đ/cp NNC) và đổi NHC sang sổ sách.
- **Mỏ mới âm ở cơ sở/phẳng (−313):** vốn đầu tư 80k/m³ trữ lượng + giá 2028 rơi ~21% (đường cơ sở NNC) ⇒ phá giá trị; chỉ dương khi giá giữ giá trị thực hoặc kịch bản tốt.
  ⇒ **Quyết định đầu tư 1.500 tỷ là biến số lớn nhất do chính MVC kiểm soát.**

### 7.4 Độ nhạy (điểm giữa phẳng…thực, r 13%, h 15%; tâm 19.540) [`valuation_out.txt`]

| Thay đổi | đ/cp | Δ |
|---|---|---|
| r 11% / 15% (lưới) | P10 13.500 – P90 27.000 | |
| Giá MVC/NNC 0,80 / 0,95 | 16.200 / 23.400 | −3.300 / +3.900 |
| Mỏ mới chạy bằng mọi giá (không sàn ở xấu) | 17.300 | −2.300 |
| Mỏ mới chi phí 165k / capex +30% | 17.200 / 17.400 | −2.300 / −2.200 |
| Hạn GP Tân Lập 2035 / 2045 mọi kịch bản | 17.700 / 20.000 | −1.800 / +460 |
| Chi phí mỏ cũ ±15% | 18.000 / 21.100 | ∓1.500 |
| Đất dự án = 0 | 18.000 | −1.600 |
| **Mỏ mới trễ 1 năm ở kịch bản cơ sở (vận hành 2029)** [`valuation_v2_out.txt` (1)] | 19.070 | −470 (cơ sở: phẳng 8.400 / thực 19.050) |
| Mỏ mới trễ 1 năm ở CẢ tốt và cơ sở | 18.590 | −950 |
| **Cụm công nghiệp 500 tỷ chi, thu hồi 70% / 50% giá trị** (ước lượng; không có trong mô hình) | | −1.300 / −2.100 |

### 7.5 Đối chiếu bội số (không phải mỏ neo)
LNST HN TTM (Q4/25–Q3/26) **306,8** ⇒ EPS 3.068 đ; BVPS 30/09 **15.460**. Tâm 19.500 = 6,4x EPS TTM đỉnh / 1,26x P/B. TTM gồm ~30% LN liên kết chỉ 15% về tiền. **TTM 306,8 gồm Q4/25 = 75,05, trong đó có hoàn nhập dự phòng đầu tư HN**: KT25 HN ghi dự phòng/(hoàn nhập) đầu tư −31,30 cả năm 2025 [KT25 7.4, tr.44] và "chi phí tài chính khác" 9T/25 = 13,12 − 10,09 lãi vay = 3,03
  (ước lượng là dự phòng) ⇒ hoàn nhập Q4/25 **≈ 34,3 trước thuế (ước lượng)**. Ex-hoàn nhập: TTM ≈ **272,5–279,3** (tuỳ chịu thuế 20% hay không) ⇒ EPS ≈ 2.725–2.793; **P/E ở 13.700 ≈ 4,9–5,0x** (không phải 4,5x), tâm/EPS ≈ 7,0–7,2x (`valuation_v2_out.txt` (4)). Chưa kiểm HN Q4/25 chi tiết.
Nhóm đá niêm yết giao dịch PE ~4–7x LN đỉnh [NNC-DD 13.4].

### 7.6 So với giá thị trường (SAU khoá md5) [`compare_px_out.txt`]
Giá **13.700** (đóng cửa 02/11/2026; vốn hoá 1.370 tỷ): **−30% so tâm**, −6% so cận phẳng, −44% so cận thực; **P/E TTM 4,5x (ex-hoàn nhập Q4/25 ≈ 4,9–5,0x, ước lượng §7.5), P/B 0,89x**.
Định giá ngược (giữ tỷ lệ tích cực:cơ sở = 1:2): giá hàm ý **P(tiêu cực) ≈ 32% (đường phẳng) – 71% (đường thực)** vs 25% trong mô hình. Kết luận không đổi trong 12.500–15.000
(P hàm ý 22–41% phẳng / 65–76% thực). Đối chiếu thô: 9,66 tr cp NNC × 47.100 (30/10) = 455 tỷ = **33% vốn hoá MVC** — thị trường định giá phần còn lại (mỏ Tân Lập + BOT + 2 mỏ mới + đất − nợ) ~915 tỷ.

**Điều thị trường có thể chưa tính** (có điều kiện kiểm chứng): (+) mỏ Tân Lập ăn cùng chênh lệch giá cụm Đồng Phú như NNC nhưng MVC giao dịch P/E 4,5x ⇒ kiểm ở Q4/26 biên gộp ≥35%;
(+) 2 mỏ mới gấp ~2,5 lần sản lượng hiện tại từ 2028 — nếu giá không sập (F2 Bobby-đá P(giảm >7%) chỉ 0,15) thì đây là tăng trưởng lớn chưa vào LN; (+) đất nhà ở 23,5 ha quanh Bến Cát;
(+) mua NNC lên 51% ⇒ hợp nhất, LN NNC hiện rõ trong BCTC. **Điều thị trường có thể đã tính đúng/quá tay:** (−) vốn 1.500 tỷ ≈ 80k/m³ trữ lượng là đắt; (−) chính MVC thêm ~2,1 tr m³/năm
vào cụm có thể tự ép giá (và ép NNC); (−) 30% LN là LN liên kết không về tiền; (−) thanh khoản ~0,4 tỷ/phiên + free float ~26%.

## 8. Checklist ngành (Bobby) — trích mục áp dụng

| Mục | MVC |
|---|---|
| Đá #GP/hạn/trữ lượng | Tân Lập: **CHƯA XÁC MINH** hạn GP; 2 mỏ mới đã có QĐ công nhận trúng đấu giá, GP khai thác chưa (F6 Bobby-đá: P(≥1 mỏ đấu giá 2025-26 ở ĐNB được cấp GP trước 30/06/2027) = 0,30 — **MVC là ứng viên trực tiếp**) |
| Đá #thuê đất/pháp lý đất | Đất mỏ mới mua 431,9 (CIP); tiền thuê đất phải nộp 1,09 |
| Đá #nợ nhà thầu dự án công | Phải thu KH 23,0 — không có dấu hiệu |
| Đá #diesel/chi phí | Không tách được; biên gộp Q3 35,9% vẫn tăng mạnh YoY dù diesel +109% YoY |
| Gạch #mỏ sét, QĐ 1266 | Mỏ sét Long Nguyên xin gia hạn tới 2030; Mỹ Phước dừng 08/2025 |
| Gạch #nhiên liệu than | Không công bố; Bobby-gạch: than +43% YoY ⇒ biên gạch bị ép (mảng nhỏ trong MVC) |
| ICD #QĐ 979, đất thuê | ICD Hoa Lư: chưa có đất; Bobby-gạch/ICD đọc ICD gắn cảng biển — **không áp trực tiếp** cho ICD cửa khẩu; giá trị đặt theo sổ sách × hệ số |
| ICD #bên liên quan | ICD là nhà phân phối VLXD/xăng dầu cho chính MVC (NQ 66) |

## 9. Pháp lý / quản trị — chỉ WARNING (luật 27/09)

1. **Chồng chéo vai trò:** Chủ tịch MVC = Chủ tịch Thanh Lễ (25%) = Chủ tịch NNC; Trưởng BKS MVC = TGĐ Thanh Lễ [QT6T 4.1]; PTGĐ/KTT MVC ngồi HĐQT/BKS của NNC, NHC, MCC.
   BKS khó độc lập với cổ đông lớn. Giao dịch bên liên quan đều đã qua ĐHĐCĐ (100% tán thành): mua xăng dầu Thanh Lễ (66,8 trong kỳ Q3), bán đá qua NNC/NHC (DT từ NHC 28,4 + NNC 15,2 trong 6T [SX6T 7.1]),
   **uỷ quyền mua 2 dây chuyền nghiền của NHC 51,1 tỷ** theo giá trị còn lại (chưa xác nhận đã thực hiện). 9T/2026 MVC thanh lý máy móc nguyên giá 52,03 (còn lại 8,48), thu 5,05 [HN-Q3 V.8, LCTT mã 22], bên mua không công bố — có trùng NHC/NNC không: chưa xác minh. Không có bằng chứng sai phạm — chỉ là kênh rủi ro chuyển giá.
2. **Sở hữu chéo MVC ↔ NNC:** NNC nắm 10,3% MVC; MVC định mua NNC lên 51%. Khi NNC thành công ty con, Luật DN 2020 Đ.195 cấm công ty con sở hữu chéo công ty mẹ —
   tác động lên 10,3 tr cp MVC NNC đang nắm (thoái vốn trên thị trường ADV ~0,4 tỷ/phiên?) **CHƯA XÁC MINH cách áp luật — cần legal-vn**.
3. **Tạm ứng 60,6 tỷ** không thuyết minh đối tượng; dự phòng phải thu 12,1. WARNING nhẹ.
4. **Thanh Lễ:** tìm nhanh không thấy vụ án/khởi tố liên quan Thanh Lễ (các vụ Bình Dương tìm thấy là Tổng Cty 3/2, khu 43 ha — khác pháp nhân). **CHƯA XÁC MINH đầy đủ** — không đưa vào kịch bản.
5. Chưa thấy CBTT xử phạt hành chính/môi trường của MVC trong tài liệu đã đọc (KT25 thuyết minh "chi phí khác" chưa render đủ để khẳng định) — CHƯA XÁC MINH.

## 10. Điều kiện làm nhận định đổi — CẢ HAI chiều (khoá 03/11/2026)

**Tích cực hơn:** (a) Q4/26 + Q1/27 biên gộp ≥ 35% với DT ≥ 200/quý (giá đá giữ); (b) GP khai thác Tam Lập 1-khu 1 cấp trước 30/06/2027 kèm cơ cấu vốn đầu tư thấp hơn 1.500;
(c) công bố hạn GP Tân Lập ≥ 2040; (d) giá đá công bố Đồng Nai Q2/27 ≥ Q3/26 +7% (F2: 0,30); (e) mua NNC lên 51% với giá ≤ giá trị NNC ex-MVC (~53–74k); (f) chi cổ tức 2026 ≥ 1.000 đ/cp
mà vẫn giữ kế hoạch mỏ mới; (g) chủ trương đầu tư cho Lai Hưng hoặc Long Nguyên.

**Tiêu cực hơn:** (a) biên gộp quý < 28% với DT đi ngang; (b) giá đá Q2/27 < Q3/26 −7% (F2: 0,15); (c) tổng đầu tư mỏ mới bị nâng (> 1.950 = +30%, ngưỡng HĐQT được uỷ quyền) hoặc trễ vận hành sau 2029;
(d) hạn GP Tân Lập ≤ 2033 hoặc hạn BOT ≤ 2027; (e) vay ngắn hạn tiếp tục tài trợ dài hạn, nợ ròng > 600 trước khi có HĐ vay dự án dài hạn; (f) giao dịch bên liên quan mới
không qua ĐHĐCĐ hoặc tạm ứng tăng > 100; (g) NNC thoái 10,3% MVC ra thị trường (áp lực cung cổ phiếu); (h) HĐQT/CBTT khởi động cụm công nghiệp hoặc chi > 100 tỷ cho cụm công nghiệp (ĐHĐCĐ duyệt đến 500 tỷ).

## 11. Chưa xác minh (tổng hợp)
1. Tách DT/LN gộp đá vs gạch vs xăng dầu; sản lượng m³ và giá bán MVC (mọi số trong §2/§7 về mỏ đá là suy ra).
2. Hạn GP + trữ lượng còn lại mỏ Tân Lập; hạn thu phí trạm Bình Thung/Lái Thiêu.
3. Cơ cấu 1.500 tỷ (đất / tiền trúng đấu giá / thiết bị); giá trúng đấu giá (R%) 2 mỏ.
4. Biến động CIP ICD Hoa Lư 37,69 → 0 trong 6T/26 (bốn dòng trả trước dài hạn 146,1 đã có nhãn — §3).
5. Hợp đồng tín dụng BIDV mới (dư nợ 451,9 > hạn mức HĐ 160/2024 350).
6. Room ngoại, sở hữu nước ngoài.
7. Áp Luật DN Đ.195 cho sở hữu chéo khi MVC lên 51% NNC.
8. Dự phòng 9,05 còn lại ở báo cáo riêng thuộc khoản nào; bản chất "thu/chi khác HĐKD" 608/325.
9. Kế hoạch/giá cụm công nghiệp 500 tỷ và giá mua NNC lên 51%; mua dây chuyền NHC 51,09 đã thực hiện chưa; bên mua máy thanh lý 52,03 (nguyên giá).
10. Hoàn nhập Q4/25 HN chỉ ở mức ước lượng (≈34,3 trước thuế). MCC 30,08% trong HN là typo công ty (1.500.012/5.016.124 = 29,90%); NHC ghi 32,47 trong HN vs 30,04% × sổ sách BQ = 18,2 — mô hình dùng 18,2 (thận trọng), chênh chưa giải thích.

## 12. Nguồn
- `src/VI_BaoCaoTaiChinhHopNhat_Q3_2026.pdf`, `src/VI_BaoCaoTaiChinhRieng_Q3_2026.pdf`, `src/VI_GiaiTrinhLienQuanDenBCTC_Q3_2026*.pdf` (text; bản EN tương ứng)
- `src/EN_ReviewedConsolidatedFinancialStatements_6_months_2026.pdf` (scan; trang đã đọc: 4, 11, 33, 43, 51 — ảnh `png/hn6t_p*.png`)
- `src/EN_ConsolidatedFinancialStatements_2025.pdf` (scan; trang 34, 38, 43 — `png/hn25_p*.png`)
- `src/VI_BaoCaoThuongNien2025.pdf`, `src/EN_NoticeInvitation_and_Document2026.pdf`, `src/EN_Minutesof_the_2026AnnualgGeneralMeeting...pdf`, `src/EN_Resolution_of_the_Board_of_Directors_No_69.pdf`, `src/VI_BaoCaoQuanTri6ThangDauNam2026.pdf`
- Website: vlxdbd.com.vn/don-vi-thanh-vien/* (Chi nhánh Bình Phước, NM gạch Bến Cát, BQL ĐT743) — truy cập 03/11/2026
- BQ: `ticker_financial` (MVC/MCC/NHC NP_P0, BVPS, OShares), `ticker` (ADV, giá — chỉ sau khoá md5)
- Báo Đấu thầu 22/10/2024 (dừng thu phí trạm Bình Thắng)
- Sector read Bobby: đá ĐNB 30/10/2026; gạch nung + ICD 03/11/2026

## Phụ lục E — Việc áp đính chính của người phản biện (HỒ SƠ NỘI BỘ; không đưa vào bản gửi ngoài)
Skeptic (`SKEPTIC_20261103.md`) CONFIRMED với 12 đính chính + 2 ghi chú. Vòng 2 (job `Taylor_20261103_085129`) đã áp:
| # | Nội dung | Xử lý | Kiểm lại BCTC gốc |
|---|---|---|---|
| 1 | CCN ≤500 + mua NNC 51% thiếu phía xấu | §3 (nợ ròng ~1,4–1,5 nghìn tỷ, D/E ~0,9–1,0), §10 trigger (h), §11 mục 9; độ nhạy CCN thu hồi 70/50% = −1.300/−2.100 đ/cp (ước lượng) | ĐHĐCĐ (đọc vòng 1) |
| 2 | 4 dòng trả trước dài hạn có nhãn | §3, §11 mục 4 | **Đã đọc lại** HN-Q3 V.13: 115,05 QSDĐ CN Bình Phước khai thác đá; 7,75/21,89 Long Nguyên 1/2; 1,45 mở rộng LN2 ✔ |
| 3 | LNST riêng ex-hoàn nhập 180,7 (không phải ~173 trước thuế) | §2 | **Đã đọc lại** R-Q3: thuế hoãn lại 7,91; LNTT riêng 262,1 → 223,1 ex ✔ |
| 4 | Hoàn nhập HTK 4,89 + thuế hoãn lại HN 7,96 | §2 | **Đã đọc lại** HN-Q3 V.6 (4.888.672.735 → 0) ✔; khớp 7,96 ✔ (bản chất khoản −8 do hợp nhất: chưa xác minh) |
| 5 | TTM 306,8 gồm Q4/25 hoàn nhập | §7.5: hoàn nhập Q4/25 ≈ 34,3 (ước lượng) từ KT25 7.4 (−31,30) + 3,03 (suy từ 9T/25) ⇒ P/E 4,9–5,0x | Đã đọc KT25 tr.44 (png/hn25_p47.png) ✔; chưa kiểm HN Q4/25 chi tiết |
| 6 | NQ69 là kế hoạch cũ | §2 bỏ "mâu thuẫn guidance" | ngày NQ 30/07 |
| 7 | Mua dây chuyền NHC 51,09 mới là uỷ quyền | §5, §9, §11 mục 9 | **Đã đọc lại** V.8: máy mua mới 39,32; giảm máy móc 52,03; thu thanh lý 5,05 ✔ |
| 8 | Thanh khoản trung vị, bỏ NAV | §6 (ADV trung vị 20/60/120 = 0,49/0,19/0,17; đo lại `calc/px_median_out.txt`) | BQ ✔ |
| 9 | Chất lượng tiền chưa đánh giá được | §4 | **Đã đọc lại** LCTT: mã 01 = 221,1; mã 06/07 = 608,2/325,4 ✔ |
| 10 | Tiền lệ quỹ cổ tức 2025 70% nhưng trả 60 | §4 | biên bản ĐHĐCĐ (vòng 1) |
| 11 | 57k/m³ loại đất, ~3,5× | §0 điểm yếu 3 | tính lại 1.500−432≈1.068 / 18,75 ≈ 57k ✔ |
| 12 | Mép lạc quan độ trễ 2–4 năm + độ nhạy trễ 1 năm | §7.2B, §7.4 (tâm 19.070, −470; cả tốt+cơ sở 18.590, −950) | `calc/valuation_v2.py` |
| Ghi chú | MCC 29,90% typo; NHC 32,47 vs 18,2 | §11 mục 10 | — |
**Kết quả:** tâm 19.540, vùng 14.600–24.500, xác suất kịch bản 25/50/20/5 — KHÔNG đổi; thay đổi nằm ở độ nhạy và mô tả phía xấu. Việc còn mở (chưa làm): HĐ BIDV mới + cơ cấu 1.500 tỷ; hạn GP Tân Lập; thu/chi khác 608/325; legal-vn Đ.195.
Lệnh tái lập: `cd calc && python3 valuation_v2.py > valuation_v2_out.txt; md5sum -c LOCK_md5.txt` (3 file output khoá vòng 1 vẫn OK).
