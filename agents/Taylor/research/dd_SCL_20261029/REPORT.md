# DD — SCL (CTCP Sông Đà Cao Cường) · as-of 29/10/2026 · job `Taylor_20261029_052549`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán, không đổi quyết định LAG đã ack. User quyết.
> Nguồn: **[HN-Q3]** BCTC hợp nhất Q3/2026 (ký 15/10/2026, `src/bctc_hopnhat_q3_2026.pdf`, scan, đọc từng trang);
> **[BN]** BCTC hợp nhất bán niên 2026 **đã soát xét** (AVA, báo cáo 590/BCKT-TC/AVA ngày 06/08/2026, `src/dl/bannien_2026_hn_vn.pdf`);
> **[KT25]** BCTC hợp nhất 2025 **đã kiểm toán** (AVA, 245/BCKT-TC/AVA.NV5 ngày 20/03/2026, `src/dl/bctc2025_hn_vn.pdf`);
> **[GT]** giải trình 1295/GT-SCL 15/10/2026; **[NQ1363]** NQ HĐQT 26/10/2026; **[TB1368]** TB chào bán 27/10/2026;
> **[BQ]** `tav2_bq.ticker` / `ticker_financial` (giá tới 28/10/2026); **[DNSE]** `data/execution_logs/dnse_raw_2026-10-2[6-9].jsonl` (lọc theo account).
> Số không đo được gắn **(ước lượng)**. Phép tính: python inline trong phiên này.

## 1. Verdict

**NON (discretionary) ở 31.100 cum-quyền ≈ 28.612 ex-quyền lý thuyết.** Doanh nghiệp *thật* và đang tốt lên
(ý kiến kiểm toán 2025 chấp nhận toàn phần, soát xét bán niên không ngoại trừ, biên gộp 41%, phải thu không phải cờ đỏ),
nhưng giá đã trả trước kịch bản cơ sở: giá trị có trọng số **~25.500 đ/cp sau phát hành (ước lượng)**, thấp hơn TERP ~11%.

| Vùng (giá ex-quyền, trên 44,84tr CP) | Nhãn |
|---|---|
| ≤ ~21.700 (biên an toàn 15% dưới 25.500, ước lượng) | QUALIFY |
| ~21.700 – 25.500 | AMBIGUOUS |
| > 25.500 (hiện 28.612 ex / 31.100 cum) | NON |

**Đổi verdict khi:** BCTC Q4/26 cho LNST quý ≥ 38 tỷ **và** CFO quý ≥ LNST **và** phải thu VinCons giảm (⇒ nâng kịch bản cơ sở,
fair value lên ~29–30k); ngược lại biên gộp < 36% hoặc VinCons tiếp tục tăng mà không thu ⇒ nghiêng bear. Chi tiết §10.

**Vị thế LAG thật (không đổi quyết định, chỉ báo):** SpaceX **1.100 cp** giá vốn 32.364 (3,54% NAV @31.100), ZaloPay **700 cp**
giá vốn 32.371 (2,37% NAV) [DNSE positions 29/10; NAV `nav_history_*` 28/10]. Plan 29/10 không còn lệnh SCL. **Ngày GDKHQ quyền
mua (~09/11, ước lượng) rơi TRONG cửa sổ giữ 25 phiên** ⇒ luật thoát trong ack 21/10 đang có hiệu lực, cần user chọn trước **06/11** (§6).

⚠️ **Phát hiện vận hành:** phiên 28/10 SCL −6,6% (KL 335k, 10,4 tỷ) bị intraday-watch/Spyros/Wendy dán nhãn "NOISE, không có tin
48h". **Sai: có tin** — TB chào bán 1368/TB-SCL ký số 27/10 15:03 + NQ 1363 (26/10) công bố giá 12.500 và ngày chốt 10/11.
Phản ứng giá −6,6% ≈ mức pha loãng lý thuyết −8,0%. Nguồn tin của watch không phủ CBTT trên website DN.

## 2. Giả thuyết "phải thu tăng là cờ đỏ" — KHÔNG đứng (có 1 điểm theo dõi)

| tỷ đồng [BN/HN-Q3] | 1/1/26 | 30/6/26 | 30/9/26 |
|---|---|---|---|
| Phải thu khách hàng | 88,5 | 82,3 | **116,0** |
| — trong đó VinCons | 48,2 | **23,4** | **67,9** (58,5%) |
| Trả trước người bán | 46,4 | 56,2 | 86,6 |
| Dự phòng | −4,2 | −4,1 | −4,1 |

- **VinCons KHÔNG phải nợ đọng mãn tính**: số dư giảm 48,2 → 23,4 trong H1 (đã thu) rồi tăng +44,5 tỷ trong Q3 = hoá đơn mới quý này.
  Tuổi nợ không công bố trong cả 3 bản BCTC — **chưa kiểm được**, nhưng chuỗi số dư không giống nợ treo.
- DSO phải thu KH ~**37 ngày** (116 / (263,4×1,1 VAT) × 92). Nợ xấu cũ 5,57 tỷ gốc (Gypro, Kaola, Nậm Theun…) đứng yên từ đầu năm, không phát sinh mới.
- Trả trước: Anhui Keda (thiết bị TQ) 30,0 → 0 đã về từ 30/6 và nay là *phải trả* 6,5 tỷ ⇒ thiết bị đã giao. Tăng Q3: Điện Kym 16,0 (mới),
  Long Thành Hải 12,8, khác 33,9. **Điểm theo dõi:** XNK Quốc tế LS 19,46 (30/6) → 19,29 (30/9) đứng yên ≥ 1 quý, không nêu mục đích.
- Điểm cần theo dõi thật: AR +41% QoQ khi doanh thu chỉ +8,6% QoQ — dồn vào VinCons. Kiểm ở BCTC Q4.

## 3. Chất lượng lợi nhuận

**Không có số theo mảng** (AAC/ALC/vữa/keo/tro bay/thạch cao) trong BCTC quý, bán niên hay thuyết minh — BCTC chỉ 1 dòng
"doanh thu bán hàng hoá, thành phẩm" [HN-Q3 VI.1]. Mục này **không kiểm được từ BCTC**; cần bản cáo bạch (TB1368 nói đăng tại website) hoặc IR.

| [HN-Q3] | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần (tỷ) | 263,4 | 133,1 | 665,5 | 367,5 |
| Biên gộp | **41,2%** | 35,6% | 40,1% | 36,1% |
| CPBH | 39,5 | 17,7 | 98,1 | 54,8 |
| LNST cổ đông mẹ | 38,09 | 16,14 | 94,36 | 40,95 |
| Thu nhập khác | 0,07 | 0 | 4,76 | 0 |

- Lợi nhuận là **hoạt động lõi**: thu nhập tài chính 0,17 tỷ, thu nhập khác 0,07 tỷ. Không có lãi mua rẻ, không lợi thế thương mại.
- **Q3 ≈ Q2** (38,09 vs 38,45 [BQ]) ⇒ tăng trưởng +136% YoY là do nền 2025 thấp; QoQ đã đi ngang.
- Khấu hao Q3 9,89 tỷ vs 5,40 (+83%) đã nằm trong giá vốn — biên 41% *sau* khi gánh khấu hao Lâm Đồng ⇒ không phải biên "đẹp nhờ khấu hao".
- Lãi vay vốn hoá: **không có bằng chứng** — lãi đã trả 9T 14,29 < chi phí lãi ghi nhận 15,55 (nếu vốn hoá lớn thì trả > ghi nhận).
- Lịch sử biên gộp (BQ, định nghĩa khác BCTC): 46% (Q1/23) → 32% (Q4/24) → ~35% (2025) → 39–41% (2026). 2026 là đỉnh 3 năm, không phải mức trung bình.
- LNST năm [BQ]: 2023 45,3 · 2024 26,6 · 2025 64,3 · TTM 117,7 tỷ.
- EPS 995 vs 721: 721 **chưa điều chỉnh hồi tố** cổ tức cổ phiếu 9% + 17% (VAS 30 yêu cầu). Điều chỉnh ⇒ ~565, tăng **+76%**, không phải +38%.

## 4. Bảng cân đối / dòng tiền thật [HN-Q3]

- Vay **416,5 tỷ** = NH 259,7 (BIDV 252,9 + dài hạn đến hạn 6,8) + DH 156,7 (BIDV 130,7 + **vay cổ đông lớn CTCP CN-DV Cao Cường 26,0 tỷ, lãi 10%**, hạn 05/02/2028).
  Tiền 95,1 ⇒ **nợ ròng 321,4 tỷ**; nợ ròng/VCSH 0,60; nợ ròng/EBITDA (9T năm hoá 227,6) **1,41×**; EBITDA Q3×4 = 250,8.
- **"Vay vượt hạn mức BIDV"**: thuyết minh vẫn mô tả HĐ 01/2025 hạn mức 230 tỷ "cho đến khi hạn mức 2026-2027 được duyệt"; TB1368 dẫn
  **HĐ tín dụng 02/2026/1605829/HĐTD ngày 29/07/2026** — rất có thể là hạn mức mới chưa cập nhật vào thuyết minh. Giải thích khả dĩ, **chưa xác minh hạn mức mới**.
- Khoản BIDV 184 tỷ (HĐ 01/2026, 12/03/2026) cho Phả Lại: bảo lãnh/mở LC ⇒ xác nhận giả thuyết trả trước liên quan thiết bị Phả Lại (gián tiếp).
- **CFO 9T 9,86 tỷ** vs LNTT 118,0: Q1 −96,2 / Q2 +56,7 / Q3 +49,3 [BQ, khớp tổng]. Q2+Q3 = 1,39× LNST. Cộng lại tăng trả trước người bán
  (+40,2, phần lớn mang tính capex) ⇒ CFO điều chỉnh ~50 tỷ = 0,53× LNST 9T. Tồn kho 39,8 → 73,3 (+33,4; thành phẩm 12,8 → 20,2) đi theo quy mô.
- Capex 9T 198,1 tỷ. XDCB dở dang 206,6: Phả Lại 178,0 + 12,7 (tổng vốn 262,9 ⇒ còn ~72 tỷ, ước lượng) + tách tro Vĩnh Hảo GĐ2 14,8.
- **Hợp nhất "lần đầu"**: chỉ là lần đầu có BCTC hợp nhất *quý*. BCĐKT 31/12/2025 hợp nhất **đã kiểm toán**; công ty con duy nhất
  **CTCP Green SCL 85,834%** (Vĩnh Hảo, Lâm Đồng — tro xỉ Vĩnh Tân). Đóng góp nhỏ: LNST riêng Q3 37,995 vs hợp nhất 38,105; LNST CĐKKS 9T 6,9 triệu. Không goodwill, không lãi mua rẻ.
- Số CP: 22,39tr (30/9/25) → +8,0tr quyền mua @12.500 + 2,02tr CT 9% (Q4/25) → 32,41tr → +5,51tr CT 17% → 37,92tr → **+0,92tr ESOP mệnh giá 10.000 (Q3/26)** → **38,84tr**.

## 5. Ghi nhận doanh thu, backlog, khách hàng

- Ghi nhận khi giao hàng (bán thành phẩm), không theo tiến độ hợp đồng xây dựng ⇒ không có rủi ro retention/doanh thu chưa xuất hoá đơn kiểu xây lắp. Chiết khấu thương mại 14,6 tỷ/quý (5,2% DT gộp).
- Backlog: **không công bố**. GT chỉ nói "ký nhiều hợp đồng cung cấp lớn", "xuất khẩu ký dài hạn" — không có số.
- Vingroup ~25% DT (lời Chủ tịch, nguồn báo chí 10/2026 — chưa đối chiếu). BCTC chỉ cho số dư: VinCons 58,5% phải thu KH. Trọng Phóng 10,8, Vạn Thiên A 4,7.

## 6. QUYỀN MUA 100:15,4453 @12.500 [NQ1363, TB1368]

Đã xác minh: GCN 632/GCN-UBCK 23/10/2026; 6.000.000 CP; ĐKCC **10/11/2026**; chuyển nhượng quyền 17/11–03/12 (1 lần); đăng ký + nộp tiền 17/11–08/12;
thu **75 tỷ** để **trả khoản vay theo HĐ 02/2026/1605829/HĐTD (BIDV, 29/07/2026)** và nợ thuê TC; tư vấn TVSI, kiểm toán AVA.
GDKHQ **~09/11/2026 (ước lượng** — 1 phiên trước ĐKCC; chưa thấy TB VSDC). Phiên cuối còn quyền: **06/11**.
Lệch nhỏ: 6,0tr / 38,837tr = 15,449% vs tỷ lệ 15,4453% (cơ sở ngầm 38,846tr) — không trọng yếu.

| Chỉ tiêu (giá cum 31.100, đóng cửa 28/10 [BQ]) | Giá trị |
|---|---|
| TERP | **28.612** (−8,0%) |
| Giá trị lý thuyết quyền / CP đang giữ | **2.488 đ** |
| CP sau phát hành | 44,84tr (+15,45%) |
| BVPS | 13.688 → 13.529; PB 2,27 → 2,11 @TERP |
| Nợ ròng (nếu 75 tỷ trả nợ hết) | 321,4 → **246,4**; /EBITDA 1,41 → 1,08; /VCSH 0,60 → 0,41 |
| EPS TTM | 3.031 → **2.746** pro-forma (cộng tiết kiệm lãi ~5,4 tỷ sau thuế, ước lượng lãi 9%); PE @TERP 10,4 |

**Có giải quyết đòn bẩy không?** Giảm một phần (nợ ròng −23%), không thay đổi bản chất: Phả Lại còn ~72 tỷ capex (ước lượng) và CFO
9T mới ~10 tỷ ⇒ không có đợt phát hành, nợ ròng/EBITDA cuối năm có thể quay lại ~1,4× (ước lượng). Cổ đông nội bộ (Kiều Văn Mát 11,54%
+ Cao Cường 12,50% = 24,0%) — nếu họ không mua, phần dư HĐQT phân phối (TB không nêu; chưa kiểm).

**Hành động cho người đang giữ (số thật):**

| Account | CP | CP được mua | Tiền cần | Mất nếu bỏ quyền (@31.100) |
|---|---|---|---|---|
| SpaceX | 1.100 | 169 | 2,11 tr | 2,74 tr = **0,28% NAV** |
| ZaloPay | 700 | 108 | 1,35 tr | 1,74 tr = **0,19% NAV** |

- (a) **Thực hiện quyền**: rẻ nhất về giá trị; tốn 3,46tr tiền; CP mới về sau khi phát hành (~cuối 12/2026–01/2027, ước lượng) ⇒ **lô lẻ mồ côi** sau ngày thoát LAG.
- (b) **Bán quyền**: chuyển nhượng 1 lần qua CTCK, thanh khoản thấp; DNSE có hỗ trợ không — **chưa xác minh** (hỏi Mafee).
- (c) **Bán cổ phiếu trước GDKHQ (≤06/11)**: đúng luật thoát skeptic đặt trong ack 21/10; chấm dứt LAG sớm ~3 tuần.
- (d) Bỏ quyền: mất 4,48tr tổng — tệ nhất. **Bot hiện không tự đăng ký/bán quyền** (skeptic 21/10).
⇒ Tổn thất tối đa nhỏ (≤0,28% NAV) nhưng là quyết định của user trước 06/11; Taylor không chọn.

## 7. Pháp lý / quản trị — WARNING (luật 27/09)

- Không tìm thấy khởi tố/xử phạt/hạn chế GD (Wendy 29/10 01:20Z, search giới hạn; chưa tra trực tiếp UBCKNN/HNX).
- ⚠️ **Pha loãng liên tục**: 4 đợt trong 13 tháng (quyền 8tr, CT 9%, CT 17%, ESOP) + đợt quyền 6tr đang chạy. CP 17,3tr (2023) → 44,8tr pro-forma = **2,6×**.
- ⚠️ **ESOP 0,92tr @10.000** khi giá thị trường ~25–28k (ước lượng) ⇒ chuyển giá trị ~14–17 tỷ (ước lượng) cho người lao động/quản lý, không ghi chi phí (VAS).
- ⚠️ Giao dịch bên liên quan: vay 26 tỷ từ cổ đông lớn Cao Cường @10% (cao hơn BIDV 9,5–10,5% DH, NH thả nổi); mua hàng ~0,54 tỷ/quý từ cùng bên.
- ⚠️ Chất lượng trình bày: EPS so sánh không điều chỉnh hồi tố; bảng thuế ghi nhãn cột "31/12/2025, 01/01/2025" sai kỳ. Kiểm toán viên là AVA (hãng nhỏ, thành viên MGI).
- ⚠️ Phải thu khác 0,78 tỷ từ cá nhân (Trịnh Anh Quang, Lưu Trung Thành, Phạm Tiến Trung) — tiền thoái vốn Thạch Cao Đình Vũ 2/2024 chưa thu hơn 2,5 năm (nhỏ).
- Scandal di cư (Vingroup/VinCons): rủi ro tín dụng tập trung vào hệ sinh thái 1 tập đoàn — kịch bản B của Bobby (đóng băng BĐS cục bộ ⇒ CĐT chậm trả/cấn trừ sản phẩm) là kênh lây.
  Không thấy BĐS đầu tư/hàng hoá BĐS trong BCĐKT ⇒ **chưa có cấn trừ bằng sản phẩm**.
- Giao dịch nội bộ gần đây: không tra được trong phiên này (cần HNX/Vietstock) — **chưa kiểm**.

## 8. Định giá (trên 44,84tr CP sau phát hành)

PE TTM 10,3 cum / 10,4 pro-forma @TERP; PE Q3 năm hoá 8,1 @TERP; EV/EBITDA 6,7 (9T năm hoá) / 6,1 (Q3×4); PB 2,27.
Comp [BQ 28/10, PE/PB/EV-EBITDA]: VGC 10,8/1,61/5,6 · VCS 8,7/0,98/6,2 · PLC 11,8/1,23/7,9 · DHA 5,5/1,47 · NNC 5,1/1,65/4,1 · HT1 13,1/1,02/4,1 · KSB 7,8/0,56 · BMP 9,0/3,56/6,0.
SCL rẻ nếu Q3 bền, đắt theo PB (2,1–2,3 vs nhóm ~1,0–1,6).

| Kịch bản (LN 2027, ước lượng) | Giả định | PE | Giá trị/cp | Trọng số |
|---|---|---|---|---|
| Bear | Biên về mức 2025, DT −20% do kênh nhà ở gãy (Bobby: rủi ro nhất 2027-28) ⇒ LNST 65 tỷ ≈ 2025 | 9 | **13.050** | 0,30 |
| Base | Run-rate Q3 có chuẩn hoá biên ~38% ⇒ 135 tỷ | 9 | **27.100** | 0,50 |
| Bull | Phả Lại chạy, +~34 tỷ (vòng quay 1,3× trên 263 tỷ, biên ròng 10%) ⇒ 180 tỷ | 10 | **40.150** | 0,20 |

**Có trọng số ≈ 25.500** (xác suất chủ quan) vs TERP 28.612 (−11%). Downside bear −54%, upside bull +40% ⇒ bất đối xứng **xấu**.
PE chuẩn hoá chu kỳ: TB LNST 2023–TTM ≈ 63 tỷ ⇒ ~1.410 đ/cp ⇒ PE chuẩn hoá ~20× @TERP. Giá đang định giá lợi nhuận đỉnh.

## 9. Sizing vs thanh khoản

ADV [BQ, Price×Volume]: 3T **4,01 tỷ** (63 phiên), T10 3,91, 6T 2,69. Vị thế tổng 1.800 cp ≈ 56tr = **1,4% ADV 3T** ⇒ thoát 1 phiên, không vấn đề.
Tiền lệ disc. ≤0,5–1,0% NAV: vị thế hiện tại (3,54%/2,37% NAV) là sizing **LAG**, không phải disc.; với lens discretionary verdict NON ⇒ không thêm.
Nếu 1 disc. size 1% NAV (~9,7tr) thì càng không vướng thanh khoản. Rủi ro thanh khoản thật nằm ở gap giá (28/10 −6,6% trong 1 phiên).

## 10. Điều kiện đổi verdict + mốc khoá trước

| Mốc | Kiểm gì | Hệ quả |
|---|---|---|
| **06/11/2026** (phiên cuối cum) | User chọn (a)/(b)/(c) ở §6 | Bắt buộc với vị thế LAG |
| 09/11 GDKHQ (ước lượng) · 10/11 ĐKCC | Giá điều chỉnh; xác nhận ngày qua TB VSDC | — |
| 03/12 / 08/12 | Hết hạn chuyển nhượng / nộp tiền | Sau 08/12 quyền mất giá trị |
| BCTC Q4/26 (~20/01/2027) | LNST quý ≥38 tỷ, biên gộp ≥39%, CFO ≥ LNST, VinCons giảm, nợ ròng ≤260 tỷ | Cả 4 đạt ⇒ base nâng, AMBIGUOUS ở giá hiện tại |
| BCTC 2026 kiểm toán (~03/2027) | Ý kiến chấp nhận toàn phần; tuổi nợ (nếu có) | Ngoại trừ ⇒ NON cứng |
| Phả Lại vận hành (~T11/2026 theo DN) | Doanh thu mới xuất hiện từ Q1/27 | Bull |
| Bất kỳ | VinCons chậm trả / cấn trừ BĐS / đợt phát hành mới | NON cứng; hủy điều kiện của ack 21/10 |

## 11. Lệch nguồn BQ vs BCTC

- `Revenue_P0` Q3/26 BQ 277,9 = DT **gộp**; DT thuần 263,4. Gói DD từng dùng 281,6 — không khớp cả hai.
- `GPM_P0` 0,387 ≠ biên gộp quý 41,2% (BCTC) — không phải biên quý.
- `OShares` Q2/26 = 38,84tr nhưng BCTC: 30/6 = 37,92tr (ESOP 0,92tr phát hành Q3) — BQ cập nhật sớm.
- `NP_P0` 3 quý 2026 cộng 94,37 = BCTC 9T ✓; `CF_OA_P0` cộng 9,8 ≈ 9,86 ✓; `Cash_P0` 95,1 ✓.
- Sàn: Mike ghi HNX, Wendy ghi UPCoM — GT gửi Sở GDCK Hà Nội (quản lý cả hai); **chưa đối chiếu**.

## 12. Checklist Bobby §6 (23 mục) — kiểm được từ BCTC?

Kiểm được: #6 tồn kho (~43 ngày giá vốn, không dự phòng) · #10 phải thu (DSO 37 ngày; tuổi nợ KHÔNG công bố) · #11 cấn trừ BĐS (không thấy) ·
#12 retention (không áp dụng — bán hàng) · #13 trả trước (§2; Anhui Keda đã giao; LS 19,3 tỷ đứng yên) · #14 XDCB (Phả Lại 9 tháng, chưa quá hạn; không thấy vốn hoá lãi) ·
#16 vốn góp (tăng vốn bằng tiền thật: quyền 8tr @12.500, ESOP 9,2 tỷ thu tiền) · #17 lợi nhuận lõi (✓) · #19 nợ/EBITDA 1,41×, NH tài trợ một phần DH ·
#20 pha loãng (⚠️ §7) · #21 đầu tư ngoài ngành (không thấy; Quỹ TD Phả Lại 0,8 tỷ).
Một phần: #15 khấu hao (có số, không có thời gian khấu hao trong phần đã đọc) · #18 capex Phả Lại (tổng vốn, không có giả định hiệu suất).
Không kiểm được từ BCTC: #1 kênh, #2 top-10 KH (chỉ số dư), #3 backlog, #4 thị phần vùng, #5 công suất/hiệu suất, #7 năng lượng hấp,
#8 hợp đồng tro/thạch cao (giá, hạn), #9 độ nhạy đầu vào, #22 môi trường/bãi tro, #23 hợp chuẩn ⇒ cần bản cáo bạch đợt chào bán + IR.
**Forecast F11 (biên gộp DN thuần AAC)**: chưa đến hạn (2027-11-30); ghi điểm dữ liệu Q3/26 = 41,2% (9T 40,1%). SCL có mảng tro bay/phụ gia lớn ⇒ có thể không thuộc "thuần AAC" — để người chấm quyết.

## Giới hạn
Không có bản cáo bạch, tuổi nợ, cơ cấu mảng, backlog; không tra giao dịch nội bộ; giá hôm nay (29/10) chưa lấy từ DNSE — dùng đóng cửa 28/10.
Chưa qua fundamental-skeptic (bước kế tiếp theo skill due-diligence, Mike gọi).

## 13. PHẢN BIỆN fundamental-skeptic (29/10/2026) — REFUTED MỘT PHẦN; ĐÍNH CHÍNH của Mike (có hiệu lực hơn §1/§6 ở trên)
Verdict **NON (discretionary) ĐỨNG VỮNG**; mọi số BCTC trọng yếu, TERP 28.612, giá trị quyền 2.488đ, kịch bản 25.495, 169/108 CP, %NAV, ADV được skeptic đối chiếu lại trang gốc — KHỚP. Sai ở 4 chỗ:
1. **§1/§6 + bus finding mô tả NGƯỢC quyết định user.** Luật hiện hành (`data/lag_dd/ack.json` PROCEED 21/10 23:52 `decided_by=user`; `kb/current_ops.md`; `bin/lag_rights_exit_hold.py`): **KHÔNG bán trước ex-date; user TỰ thực hiện ĐẦY ĐỦ quyền mua; agent không hỏi lại.** "Bán trước GDKHQ" chỉ là một nhánh đề xuất của skeptic 21/10, user đã chọn nhánh kia. ⇒ **Không có việc "user phải chọn trước 06/11"**; phương án (c) KHÔNG phải luật. "Lô lẻ mồ côi" cũng sai: commit `771daf4ea` cho lô quyền KẾ THỪA entry gốc, bot bán ở phiên đầu bán được.
2. **Bẫy dữ liệu bỏ sót (Mike xác minh BQ 29/10):** `tav2_bq.corporate_action` id `6a0516165b1fb4c98c3ab2a2` (SCL, ingest 28/10 15:43): `exright_date`/`record_date`/`ref_price` = NULL, `exercise_ratio` = 0,15384615 (thật 0,154453), không giá phát hành. Hệ quả: `rights_subscription.py --record` sẽ báo "CHƯA có GDKHQ trên BQ"; trần `park_holdings.py:645` = floor(700×0,15384615)=107 < 108 CP ZaloPay được mua ⇒ lô UNVERIFIED (SpaceX 169 không sao); `lag_rights_exit_hold` HOLD + cảnh báo hằng ngày nếu vendor chưa điền. Cần vendor/Winston điền ngày + tỷ lệ TRƯỚC 17/11.
3. **Vùng "QUALIFY ≤21.700" trái §2.5** (PB ~1,6, không trigger khủng hoảng, pha loãng liên tục thuộc ❌) ⇒ tối đa AMBIGUOUS, phải chạy lại §2.5 mới được gọi QUALIFY; chưa có tranche/size §3/§12.
4. Diễn giải sai nhỏ: "−6,6% ≈ pha loãng −8%" sai cơ chế (giá cum-quyền không mất giá trị vì công bố điều khoản; tỷ lệ 15,4% đã biết từ 08/09, tin mới = giá + ngày); Long Thành Hải không tăng trong Q3 (11,23→12,8), "khác" mới tăng +14,1 (19,8→33,9); base 135 tỷ ≈ ước 2026, không phải Q3×4 chuẩn hoá (~125). Phát hiện "intraday-watch không phủ CBTT website DN" vẫn đúng.
Còn thiếu: luật cho vị thế LAG đang giữ nếu VinCons chậm trả / cấn trừ BĐS trước khi thoát LAG (ack 21/10 chỉ hủy điều kiện VÀO LỆNH, đã hết hạn 26/10).
