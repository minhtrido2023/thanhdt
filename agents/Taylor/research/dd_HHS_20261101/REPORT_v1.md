# HHS — Sổ sách hợp nhất ~21.200 đ/cp là thật nhờ nắm 51% CRV đang bàn giao NC-II, nhưng giá trị nằm sau 2 tầng holding, mảng xe tải Q3 giảm 37% và từng phải dùng uỷ quyền để có quyền kiểm soát CRV

DD HHS (CTCP Đầu tư Dịch vụ Hoàng Huy, HOSE) · as-of 01/11/2026 · job `Taylor_20261101_033221`

> Đây là nghiên cứu read-only, viết trung dung. Báo cáo không khuyến nghị mua hay bán, không gắn nhãn QUALIFY/NON và không chạy §2.5.
> Số BCTC đọc từ ảnh trang render (pymupdf), ghi lại trong `calc/notes_read.md`. Số tự tính nằm ở `calc/valuation.py` → `calc/valuation_out.txt`.
> **Đơn vị: tỷ đồng** trừ khi ghi khác. Niên độ là năm dương lịch: Q3/2026 = 01/07–30/09/2026, 9T = 01/01–30/09.
>
> **Nguồn**
> - **[Q3HN]** BCTC hợp nhất 9T/2026, ký 29/10/2026, chưa soát xét.
> - **[Q3R]** BCTC riêng cùng kỳ.
> - **[6THN]** BCTC hợp nhất 6T/2026, AASC soát xét, BC 270826.019 ngày 27/08/2026.
> - **[KT25]** BCTC hợp nhất 2025, AASC kiểm toán, ký 27/03/2026.
> - **[DNSE]** `latest_trade`/OHLC read-only, lấy 01/11/2026 khoảng 10:55 ICT. Phiên cuối là 30/10/2026, khớp cuối lúc 14:45:04.
> - **[BQ]** `tav2_bq.ticker`, chỉ dùng cho peer.
> - **[TCH-DD]** `../dd_TCH_20261031/REPORT.md` v2, đã đối chiếu lại các số trong đó.
> - **[Bobby]** `kb/data_registry/market-state/sector_read_xe_tai_thuong_mai_vn_20261101.md`, đọc blind.
>
> **Giới hạn:** chưa có công văn giải trình biến động LNST, BCTN 2025, BCTC Q1/2026 và Q3/2025 bản gốc. Chi tiết ở `GAPS.md`.

---

## 0. Tóm tắt

**Bản chất HHS: holding BĐS khoác áo nhà phân phối xe tải.** Tại 30/09/2026, BĐS chiếm 20.738 trên 23.060 tổng tài sản (90%). Mảng ô tô (thương mại) chỉ có 695 tài sản [Q3HN TM39].

**Q3/2026 lãi tăng mạnh là thật**, nhưng gần như toàn bộ đến từ CRV:
- CRV bàn giao Hoàng Huy New City-II: DT BĐS Q3 1.746, LN gộp BĐS 272.
- LNST hợp nhất 198,4, phần cổ đông mẹ 115,8 (Q3/2025: 17,2).
- Mảng xe tải yếu đi: DT Q3 156,4, **giảm 36,6%** so cùng kỳ; biên gộp 12,1% (cùng kỳ 16,1%). Tồn kho xe tăng gần gấp đôi lên 608.

**Lãi 9T giảm 93–96% so cùng kỳ chỉ là do nền so sánh.** 9T/2025 có khoản lãi kế toán một lần 3.488,7, ghi nhận khi HHS giành quyền kiểm soát CRV ngày 12/06/2025 [KT25 TM3.1]. Q3/2025 không có khoản này.

**Bảng cân đối sạch về nợ:**
- Không còn vay. Đã trả 390 vay dài hạn đầu năm, và 69 vay TCH (39 của HHS, 30 của CRV) đã trả hết trong kỳ.
- Tiền và tiền gửi hợp nhất 1.031. Phần lớn nằm ở CRV; công ty mẹ chỉ có 171.
- CFO 9T **−2.110** vì: (i) nộp tiền đất I.14 khoảng 1.066 [TM18]; (ii) tồn kho NC-II tăng; (iii) người mua trả trước giảm 387.

**Định giá**
- Ở **9.450 đ** (đóng cửa 30/10/2026), P/B so với VCSH mẹ hợp nhất là **0,45x**. Phép so này bị phóng đại: VCSH đã gồm phần đánh giá lại tồn kho CRV theo giá trị hợp lý, khoảng 4.130 sau thuế thuộc HHS (ước lượng).
- Quy về cơ sở "giá gốc", P/B là **0,81x**.
- **Giá trị hợp lý ~8.800–15.900 đ, trung tâm trọng số ~11.900 đ (ước lượng)**. Giá hiện tại **nằm trong vùng, ở nửa dưới**, thấp hơn trung tâm khoảng 20%. Kịch bản tiêu cực (8.800) chỉ thấp hơn giá 7%.

**WARNING quản trị: trung bình–cao** (§6). Có ba điểm:
- Quyền kiểm soát CRV năm 2025 được lập bằng **uỷ quyền biểu quyết** chứ không phải mua cổ phần.
- **1.302,5 tỷ** trả cho những người bán HHS Capital mà BCTC không nêu tên, ở giá khoảng 26.000 đ/cp CRV, cao hơn giá trị hợp lý khoảng 12%.
- Công ty mẹ TCH có 2 vi phạm hành chính trong 16 tháng.

Kiểm toán và soát xét đều **chấp nhận toàn phần, không có đoạn nhấn mạnh**.

---

## 1. Kết luận và vùng giá

| Vùng giá (đ/cp, 431,99 tr cp) | Đọc |
|---|---|
| < ~8.800 | Chỉ hợp lý nếu phần đánh giá lại tồn kho CRV bị haircut ≥60%, chiết khấu holding 35% và chiết khấu quản trị 15% |
| **8.800 – 15.900** (hiện 9.450) | **Trong vùng, nửa dưới**. Trung tâm khoảng 11.900 (ước lượng), giá thấp hơn trung tâm khoảng 20% |
| > ~15.900 | Đòi hỏi CRV bán hết NC-II gần giá trị đã đánh giá lại, tiền chảy lên HHS (cổ tức), và thị trường bỏ phần lớn chiết khấu holding/quản trị |

**Ba kịch bản** (`calc/valuation_out.txt`, mọi tham số đều là ước lượng):

| Kịch bản | P | Haircut phần đánh giá lại tồn kho CRV (thuộc HHS, sau thuế ~4.134) | Ô tô: LNST × P/E | CK holding phần CRV / CK quản trị toàn bộ | Giá trị |
|---|---|---|---|---|---|
| Tích cực | 0,20 | 25% | 55 × 10 | 15% / 5% | **~15.900** |
| Cơ sở | 0,50 | 40% | 40 × 8 | 25% / 10% | **~12.100** |
| Tiêu cực | 0,30 | 60% | 25 × 6 | 35% / 15% | **~8.800** |
| **Trọng số** | | | | | **~11.900** |

- P nghiêng xuống (0,30 tiêu cực so với 0,20 tích cực). Lý do: mảng xe đang yếu đi ngược ngành, Bobby xếp ngành CYCLICAL ở pha "muộn nhịp tăng", và quyền kiểm soát CRV có lịch sử dựa vào uỷ quyền.
- Haircut phần đánh giá lại phản ánh 3 thứ. Một là thời gian bán hết. Tồn kho NC-II là 15.011, trong khi người mua mới trả trước 3.099. Hai là chiết khấu dòng tiền: hệ số PV khoảng 0,62 cho ~4 năm theo khung [TCH-DD]. Ba là rủi ro giá bán.

**Phép thử chéo:**
- P/B 0,60 / 0,72 / 0,90 nhân BV giá gốc (11.617 đ/cp) cho **6.970 / 8.360 / 10.460**. Trung vị 15 DN BĐS là 0,72x [TCH-DD]; TCH tự giao dịch ở 0,82x [BQ].
- **Thị trường đang định giá HHS gần đúng bằng 51,15% VCSH sổ riêng của CRV** (31/03/2026: 7.579 ⇒ 3.877 tỷ = 8.974 đ/cp, so vốn hoá 4.082). Nói cách khác, thị trường gần như **không trả gì** cho: (i) thặng dư tồn kho NC-II/I.14 vượt giá gốc; (ii) mảng xe; (iii) tiền của công ty mẹ.
- Giá hàm ý chiết khấu **55%** so với VCSH mẹ trên cơ sở giá trị hợp lý (9.153).

**Ở ±5% quanh giá (8.980–9.920):** kết luận "trong vùng, nửa dưới" không đổi. Giá chỉ "dưới vùng" khi < 8.800.

**Thanh khoản [DNSE]:** ADV20 = ADV60 = **10,8 tỷ đ/phiên**. Đỉnh/đáy 52 tuần là 15.600 / 8.580.

---

## 2. Kiểm lại các số đầu vào (từng số)

| Số / giả thuyết đầu vào | BCTC gốc | Kết luận |
|---|---|---|
| "LN 2025 3.530 tỷ là lãi kế toán một lần khi nắm quyền kiểm soát CRV" | [KT25] LNST HN 3.529,76, mẹ 3.553,22; TM3.1/TM27: **lãi đánh giá lại khoản đầu tư khi hợp nhất kinh doanh qua nhiều giai đoạn 3.488,72**. Không có lợi thế thương mại. Thực chất là đánh giá lại phần 43,56% đã nắm theo giá trị hợp lý, chứ không phải "bargain purchase" | ✓ (đúng bản chất, sai tên gọi) |
| Q3/2025 có lãi này chưa? | Không. Ngày kiểm soát là 12/06/2025 (Q2/2025). DT tài chính Q3/2025 chỉ 24,79 [Q3HN] | ✓ đã kiểm |
| Báo chí: Q2/2026 DT 233,8 (+25%), LNST ~31,6 | DT HN 6T là 479,71 [6THN TM25]. Chưa đọc BCTC Q1 riêng nên **chưa đối chiếu được Q2** | chưa kiểm (`GAPS.md`) |
| Báo chí: Q3/2026 DT 1.901, LNST 198,4 | [Q3HN] DT thuần 1.901,13; LNST 198,41; mẹ 115,76 | ✓ |
| [TCH-DD]: HHS 58,31% của TCH | [Q3HN TM22b] TCH 2.519,06 tỷ vốn góp = 58,31% | ✓ |
| [TCH-DD]: biểu quyết CRV = 35,26% qua HHS + 8,44% Hoàng Giang + 7,47% HHS Capital + 7,37% uỷ quyền | [Q3HN TM1.5] CRV: lợi ích **51,15%**, biểu quyết **58,53%** (chênh 7,38 ≈ uỷ quyền). Hoàng Giang 99,79%, HHS Capital 99,996% | ✓ khớp |
| [TCH-DD]: "HHS (độc quyền xe đầu kéo International)" | **Không có bằng chứng trong BCTC 2026.** Nhà cung cấp xe là **China DongFeng Motor Industry Imp&Exp** (phải trả 305,26, gần như toàn bộ phải trả người bán của công ty mẹ [Q3R]). Website: "hàng nghìn xe Dongfeng mỗi năm, Hoàng Huy-Dongfeng" | **✗ sửa ở [TCH-DD]**: mảng xe của HHS hiện là **Dongfeng (TQ), xe tải nặng/đầu kéo**. International/Navistar có thể là lịch sử, chưa xác minh |
| [TCH-DD]: DT ô tô 6T FY26 (04–09/2026) 359,47 | [Q3HN]−[6THN]: Q3 = 156,40 ⇒ Q2 suy ra ≈ 203,1 (ước suy) | khớp nội bộ, không mâu thuẫn |
| [TCH-DD]: TCH cho HHS vay ≤ 100 tỷ | [Q3HN TM40] đã vay **39** và **trả hết** trong kỳ; lãi 0,14. CRV vay TCH 30, cũng đã trả hết | ✓, dư nợ 30/09 = 0 |
| [TCH-DD]: TCH mua 800 tỷ cp phát hành thêm của HHS | [KT25 LCTT 9T/25] thu từ phát hành 799,95; vốn góp tăng 640 ⇒ **giá 12.500 đ/cp** (ước suy). Tiền dùng cho mua HHS Capital 1.302,5 (18/06/2025) | ✓ |
| BQ: HHS P/B 0,24, P/E 185 | BQ chia **tổng VCSH gồm cả lợi ích thiểu số** (16.880 / 431,99 tr = 39.075 đ ⇒ 0,24x). **Sai cơ sở.** P/B đúng (VCSH mẹ) là 0,45x | ✗ BẪY BQ |

---

## 3. Chất lượng lợi nhuận — tách theo mảng

### 3a. KQKD hợp nhất [Q3HN]

| | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 1.901,13 | 323,38 | 2.379,38 | 610,04 |
| LN gộp | 288,77 | 29,61 | 358,95 | 64,03 |
| DT tài chính | 17,58 | 24,79 | 93,77 | **3.736,81** |
| CPBH / QLDN | 54,89 / 11,14 | 25,22 / 13,53 | 90,78 / 34,47 | 41,01 / 23,83 |
| Lỗ thanh lý BĐSĐT | −5,58 | – | −17,89 | – |
| Lãi/lỗ liên kết | – | – | – | −130,23 |
| LNTT | 238,34 | 15,87 | 310,38 | 3.594,65 |
| Thuế hiện hành / hoãn lại | 167,66 / **−127,74** | 14,86 / −9,54 | 197,19 / −148,18 | |
| LNST / **mẹ** / thiểu số | 198,41 / **115,76** / 82,65 | 10,55 / 17,25 / −6,69 | 261,37 / **159,09** / 102,28 | 3.582,32 / 3.591,72 / −9,40 |

### 3b. Theo mảng — Q3 = 9T − 6T [Q3HN TM24/26 − 6THN TM25/27]

| Mảng | DT Q3/26 (Q3/25) | LN gộp Q3/26 (Q3/25) | Biên | 9T/26 DT (9T/25) | Biên 9T (9T/25) |
|---|---|---|---|---|---|
| **BĐS** (CRV: NC-II, H1 Commerce) | 1.746,23 (75,33) | 272,38 (−10,5) | 15,6% | 1.875,89 (110,28) | 15,8% |
| **Ô tô & phụ tùng** (công ty mẹ) | 156,40 (246,51) **−36,6%** | 18,85 (39,72) | 12,1% (16,1%) | 503,25 (496,28) +1,4% | 13,0% (15,9%) |
| Khác | 1,21 | | | 4,41 | |

**Vì sao biên BĐS ở HHS chỉ 15,6% trong khi CRV/TCH báo khoảng 52%:**
- Khi hợp nhất CRV, HHS **nâng giá trị tồn kho CRV lên giá trị hợp lý** (PPA), kèm thuế hoãn lại phải trả 2.183,9 [KT25 TM3.1].
- Khi bán, giá vốn ở cấp HHS gồm cả phần nâng giá này: khoảng **718 trong 9T** = (2.164,36 − 2.020,76) / 20% (ước lượng, thuế suất 20%).
- Cộng lại phần này thì biên gộp BĐS 9T **≈ 54%** (ước lượng), khớp với biên NC-II ở TCH (51,9%).
- ⇒ **Phần lớn lãi của NC-II đã được ghi vào LN HHS năm 2025** dưới dạng 3.488,7 tỷ. Lãi BĐS báo cáo hằng quý của HHS **thấp có hệ thống** so với lãi kinh tế. Thu nhập thuế hoãn lại (Q3: +127,7) bù một phần.
- **Hệ quả cho định giá:** P/E của HHS vô nghĩa (P/E 9T annualized ≈ 19x, ước lượng). Cần định giá theo **NAV / P/B**.

**Bao nhiêu là một lần hoặc dồn:**
- Không có lãi một lần trong 9T/2026. Lỗ thanh lý BĐSĐT là −17,9; LN khác +5,4.
- Q3 là **đợt bàn giao đầu tiên của NC-II**, nên mang tính dồn. Người mua trả trước NC-II giảm từ 3.453,1 xuống 3.099,2 (−354 trong 9T).
- LN mẹ Q3 115,8 **không phải mức chạy bền**. NCI ăn 41,7% LNST vì CRV chỉ thuộc HHS 51,15%.
- Lãi tiền gửi 9T là 91,5, sẽ giảm: HTM ngắn hạn đã giảm từ 2.435 xuống 849 vì chuyển vào đất I.14.

### 3c. Mảng xe tải — so với đọc ngành của Bobby

| Chỉ tiêu [Q3R/Q3HN] | 31/12/25 | 30/09/26 | Đọc |
|---|---|---|---|
| HTK ô tô (đi đường + NVL + SP + HH + gửi bán) | 317,6 | **608,2** (×1,9) | **cờ vàng** — Bobby §7.10: tồn kho tăng nhanh hơn doanh thu |
| — trong đó **xe ô tô sát xi** (NVL) | 38,65 | **255,42** (×6,6) | nhập sát xi chờ đóng thùng/lắp |
| — **hàng gửi bán** (ở đại lý) | 210,57 | 229,30 | cờ: Bobby §7.23 (channel stuffing), chưa kiểm được tồn kho đại lý |
| Phải thu khách mua ô tô | 89,87 | 87,96 (DP 3,495 Phúc Hưng) | ổn định; Ô tô Nam Việt 50,6 = 58% |
| Phải trả DongFeng TQ | 364,01 | 305,26 | tài trợ tồn kho bằng tín dụng nhà cung cấp, không vay NH |
| Biên gộp ô tô (riêng) | 16,0% (9T/25) | **12,5%** (9T/26); Q3 10,7% | giảm 3–5 điểm % |
| CK thương mại (giảm trừ DT) | 0 | 3,88 (9T); 2,45 Q3 | **bắt đầu giảm giá/chiết khấu** |
| DP bảo hành | 0,25 (9T/25) | 0 | có vẻ hãng chịu (chưa xác nhận) |
| Bảo lãnh/mua lại xe cho NH | — | **không thấy thuyết minh** | Bobby §7.12 (mục quan trọng nhất) — **chưa xác nhận có hay không** (GAPS) |
| Thuế NK nộp 9T | | 141,97 | xe/linh kiện nhập khẩu |

**Đọc:**
- Ngành xe thương mại Q3/2026 đi ngang, khoảng −3% đến 0% YoY theo ước lượng của Bobby. HHS **−36,6%**, tệ hơn ngành nhiều. Có hai khả năng: HHS mất thị phần trong phân khúc nặng/đầu kéo TQ, hoặc mua trước ở Q2 (Q2 suy ra ≈ 203, H1 +38,9%).
- Tồn kho gấp đôi cộng biên giảm cộng bắt đầu có chiết khấu thương mại ⇒ **rủi ro giảm giá hàng tồn ở Q4/Q1** nếu F2/F3 của Bobby đúng (Q4 < +10%, Q1/2027 < +5%).
- Quy mô nhỏ: EBIT lõi mảng ô tô 9T ≈ **39** (= 62,79 − 18,20 − 5,40 [Q3R]). Cả mảng đáng khoảng 150–550 tỷ (ước lượng), tức **4–13% vốn hoá**. Mảng xe **không quyết định** giá trị HHS.

**Peer P/E [BQ 30/10/2026]:** HTL 5,9 · TMT 5,4 · SVC 4,1 · VEA 6,4 · HAX 16,2 (CTF 163 bị méo). Trung vị khoảng 5,9x ⇒ kịch bản dùng 6/8/10x.

---

## 4. Bảng cân đối — net cash thật, riêng và hợp nhất

| [tỷ] | Riêng (mẹ) 30/09/26 | Hợp nhất 30/09/26 | Hợp nhất 01/01/26 |
|---|---|---|---|
| Tiền + HTM ngắn hạn + HTM dài hạn | 12,89 + 158,49 = **171,4** | 181,95 + 848,60 = **1.030,6** | 793,79 + 2.435,35 + 215,55 = 3.444,7 |
| Vay | **0** | **0** | 390,0 |
| Người mua trả trước (BĐS, phải dùng để hoàn thành dự án) | 4,5 | 3.142,8 (NC-II 3.099,2) | 3.530,0 |
| Kinh phí bảo trì căn hộ giữ hộ (trong tiền gửi) | – | 124,75 | 119,30 |
| Pruksa International tạm ứng treo | – | 59,43 | 59,64 |

- **Net cash "thật" hợp nhất** ≈ 1.031 − 125 (bảo trì giữ hộ) = **~906**. Số này chưa trừ chi phí còn phải bỏ ra để giao các căn khách đã trả trước (3.099), vì BCTC không cho dự toán còn lại (ước lượng: có thể âm khi tính đủ).
- **Tiền của công ty mẹ HHS chỉ 171.** Phần còn lại nằm ở CRV/Đại Lộc, nơi cổ đông thiểu số có 48,85%.
- **Tiền đi đâu trong 9T:** HTM giảm 1.802 và tiền giảm 612. Tương ứng: nộp tiền đất/thuê đất **1.066** [TM18]; HTK tăng 1.909 [LCTT], gồm I.14 1.329, NC-II +336 và ô tô +290; trả nợ vay 390; capex 240 (17B Bà Triệu 243 — đất làm trụ sở CRV, "đang thủ tục pháp lý" [TM10]).
- **TCH chuyển nhượng hợp đồng tiền gửi 852 cho CRV (215,5) và Đại Lộc (636,6)** [TM40]: giao dịch bên liên quan, CRV/Đại Lộc trả tiền cho TCH.
- **CFO:** 9T/26 −2.110 (đất + tồn kho); 9T/25 +1.273 (thu cọc). Cả hai đều chủ yếu là BĐS, không đại diện cho dòng tiền ô tô.
- Cổ tức: 9T/26 trả 0. Cổ tức phải trả tồn đọng 23,54.

---

## 5. Cấu trúc sở hữu và chiết khấu holding

```
Ông Đỗ Hữu Hạ + HH Finance 35,99% ─► TCH ─58,31%─► HHS ─51,15% lợi ích (58,53% biểu quyết, gồm 7,37% uỷ quyền)─► CRV ─► NC-II, I.14 (Đại Lộc), H1
                                      └─────────── 38,19% trực tiếp ───────────────────────────────────────────► CRV
```

- **HHS nắm CRV 51,15% lợi ích** (trực tiếp + Hoàng Giang 99,79% + HHS Capital 99,996%) [TM1.5]. **Không cần uỷ quyền vẫn trên 50%, nhưng biên chỉ 1,15 điểm %.**
- **Lịch sử quyền kiểm soát** [KT25 TM3.1–3.2]:
  - 12/06/2025: HHS mới nắm **43,56%** lợi ích. HHS nhận uỷ quyền biểu quyết **7,53%** từ "một số cổ đông" CRV, nâng biểu quyết lên 51,11% ⇒ **kiểm soát** ⇒ ghi lãi 3.488,7.
  - 18/06/2025 (6 ngày sau): mua 99,996% **HHS Capital** (nắm 7,45% CRV) giá **1.302,55 tỷ** ⇒ lợi ích lên 51,011%.
  - Tức là **lãi 3.488,7 được ghi nhờ uỷ quyền**, rồi mới mua cổ phần để củng cố.
- **Giá mua HHS Capital** ≈ 1.302,55 / 50,1 tr cp CRV ≈ **26.000 đ/cp CRV** (ước suy), cao hơn giá trị hợp lý cùng thời điểm (15.555,6 / ~672,5 tr cp ≈ 23.130 đ) khoảng **12%**.
  - **Người bán không được nêu tên.** TCH nhìn cùng giao dịch: "trả cao hơn giá trị sổ sách ~452" [TCH-DD §6c].
  - Tiền trả lấy từ 800 tỷ TCH góp + vay.
- **Đếm kép với TCH — đã kiểm:**
  - Lợi ích hiệu dụng của TCH tại CRV = 38,19% + 58,31% × 51,15% = **68,02%**, khớp [TCH-DD].
  - Định giá HHS ở đây chỉ tính 51,15% CRV. Khi so với SOTP của TCH, **thay** dòng "HHS 58,31% theo giá thị trường" bằng giá trị HHS ở đây, không cộng thêm CRV.
  - Nếu HHS = 11.900, SOTP hỗn hợp của TCH tăng khoảng 58,31% × (11.900 − 9.450) × 431,99 / 1.003,31 ≈ **+615 đ/cp TCH** (ước lượng).
- **Chiết khấu 2 tầng:**
  - Tiền NC-II chỉ lên HHS qua **cổ tức CRV**, trong đó thiểu số CRV (48,85%) hưởng tương ứng.
  - Năm 2025 CRV trả cổ tức (HHS + Hoàng Giang nhận 196,3 trước khi kiểm soát). **9T/2026 chưa thấy cổ tức CRV về HHS** (DT tài chính riêng 9T chỉ 21,6).
  - Cổ đông HHS chịu thêm tầng TCH 58,31%.
- **Free float HHS:** cổ đông ngoài TCH là 41,69% [TM22b]. Danh tính, sở hữu nước ngoài và room **chưa có** (BQ không có khối ngoại; GAPS).

---

## 6. Pháp lý, quản trị — ⚠️ WARNING (mức trung bình–cao)

| Sự kiện | Nguồn | Mức |
|---|---|---|
| Quyền kiểm soát CRV (và lãi 3.488,7) lập bằng **uỷ quyền biểu quyết 7,53%** của cổ đông không nêu tên. Đến nay danh tính nhóm uỷ quyền (7,37%) vẫn chưa công khai | [KT25 TM3.1], [Q3HN TM1.5], [TCH-DD §6a] | WARNING — kế toán hợp pháp theo VAS (AASC chấp nhận), nhưng lợi nhuận lớn nhất lịch sử phụ thuộc thoả thuận ngoài sở hữu |
| **1.302,55 tỷ mua HHS Capital** từ người bán không nêu tên, giá ~12% trên giá trị hợp lý | [KT25 TM3.2] | WARNING — rủi ro chuyển giá trị; cần CBTT/NQ ĐHĐCĐ 24/04/2025 để biết người bán |
| Ký quỹ **28,4 tỷ cho cá nhân Phạm Văn Xuân** (mới phát sinh 2026) | [Q3HN TM07] | cờ vàng — mục đích chưa rõ (có thể đặt cọc mua đất/BĐS) |
| Pruksa International 2,261 tr USD tạm ứng treo nhiều năm | [TM20] | cũ, nhỏ |
| TCH: QĐ 1020/QĐ-XPHC thuế 20,21 tỷ (04/2026); UBCKNN phạt 295 tr (12/2024) | [TCH-DD §6d] | WARNING ở công ty mẹ. **Không thấy QĐ xử phạt nào đối với HHS** (chưa tra ssc.gov.vn/thuế riêng HHS) |
| Kiểm toán 2025 / soát xét 6T/2026: AASC **chấp nhận toàn phần, không nhấn mạnh** | [KT25 tr.5], [6THN tr.4] | sạch |
| Giao dịch bên liên quan được thuyết minh: thuê VP TCH 1,82; vay/trả TCH 69; chuyển nhượng HĐ tiền gửi 852; thù lao HĐQT/BKS/BGĐ 1,06 (9T) | [TM40] | minh bạch, quy mô nhỏ trừ 852 |
| HĐQT 5 người, trong đó **2 người họ Đỗ** (ông Hạ Chủ tịch, ông Hậu) và 1 độc lập; GĐ Nguyễn Thế Hùng kiêm HĐQT | [Q3HN tr.2] | giám sát độc lập yếu (giống TCH) |
| TM41 ghi số so sánh 9T/2025 "đã được soát xét ... do Công ty tự lập" | [Q3HN TM41] | câu chữ mâu thuẫn — có thể lỗi soạn thảo; BCTC Q3 chưa soát xét |
| ĐTTC dài hạn trình bày lạ: −570,3 (cty con) −565,7 (LDLK) +1.136,0 (khác) = 0 | [Q3HN BS mã 261–263] | lỗi trình bày (không ảnh hưởng tổng) |

⇒ WARNING **trung bình–cao**, nặng hơn TCH một bậc, vì 2 giao dịch 2025 (uỷ quyền + HHS Capital) xảy ra **ngay tại pháp nhân HHS**. Không có dấu hiệu khởi tố hay ngoại trừ kiểm toán. Theo luật 27/09: phân tích bình thường, chỉ cảnh báo.

---

## 7. Định giá — tóm cơ sở

1. **VCSH mẹ hợp nhất 9.152,9 = 21.188 đ/cp** (cơ sở giá trị hợp lý của CRV tại 12/06/2025, đã trừ thuế hoãn lại).
2. Phần đánh giá lại còn trong sổ: thuế hoãn lại 2.020,76 / 20% ⇒ **10.104 trước thuế, 8.083 sau thuế, phần HHS 4.134** (ước lượng). BV giá gốc tương đương = **5.018 = 11.617 đ/cp**.
3. CRV trên cơ sở giá trị hợp lý (100%) ≈ NCI / 48,85% ≈ **15.818** (ước lượng; NCI gồm cả Pruksa VN 9,83%, sai số nhỏ). Đối chiếu: giá trị hợp lý tại 12/06/2025 là 15.556 [KT25].
4. NAV = [51,15% × CRV − haircut × 4.134] × (1 − CK holding) + phần khác ~678 (tiền mẹ, Pruksa, Hoàng Giang; số dư) + ô tô (LNST × P/E); sau đó × (1 − CK quản trị). Kết quả ở §1.
5. **Chi phí vốn:** dùng PV 0,62 cho ~4 năm (Ke nội địa β1,1 khoảng 12,3–13,4%, khung 29–30/10) để đặt haircut. Không chạy DCF vô hạn vì dòng tiền BĐS có thời hạn.
6. **Độ nhạy chính:**
   - Mỗi 10 điểm % haircut phần đánh giá lại ≈ **±650 đ/cp**.
   - Mỗi 5 điểm % CK holding ≈ **±600–700 đ/cp**.
   - Mảng xe (P/E 6→10, LNST 25→55) chỉ đổi khoảng **−350 đến +480 đ/cp** so với cơ sở.

---

## 8. Mốc kiểm chứng và điều kiện đổi nhận định HAI chiều

| # | Mốc | Ngày | Đổi lên nếu | Đổi xuống nếu |
|---|---|---|---|---|
| M1 | BCTC HN Q4 & năm 2026 (kiểm toán) | 01/2027 (Q4), 03/2027 (năm) | Người mua trả trước NC-II giảm và DT BĐS Q4 ≥ 1.000 (tiêu thụ backlog tiếp); kiểm toán sạch | Kiểm toán có ngoại trừ/nhấn mạnh về PPA, giá trị tồn kho hoặc uỷ quyền ⇒ tâm −1.500 đến −2.500 đ (ước lượng) |
| M2 | Mảng xe Q4/2026 [Q4R] | 01/2027 | DT ô tô ≥ 200 **và** HTK ô tô < 450 | DT < 150 **và** HTK > 600 hoặc trích lập DP giảm giá HTK ⇒ chuyển sang kịch bản tiêu cực mảng xe |
| M3 | **Cổ tức tiền CRV về HHS** (CBTT CRV) | 31/12/2027 | Có cổ tức tiền ≥ 500 tỷ toàn CRV ⇒ CK holding −5 điểm % ⇒ +600 đến +700 đ | Không có cổ tức, CRV tiếp tục dồn tiền vào quỹ đất mới ⇒ giữ CK 25–35% |
| M4 | Công khai người bán HHS Capital / nhóm uỷ quyền 7,37% | bất kỳ | Bên độc lập, giá có định giá độc lập ⇒ CK quản trị −5 điểm % | Là người liên quan ông Hạ/HH Finance ⇒ CK quản trị +5 điểm % (≈ −670 đ) |
| M5 | Ngành (Bobby F2/F3) | 20/01/2027, 20/04/2027 | Q4 > +15% (Bobby "sai hướng tốt") | Q4 âm hai chữ số |
| M6 | BCTC soát xét TCH bán niên FY26 | 30/11/2026 | Số NC-II/CRV khớp | Điều chỉnh lớn ở CRV/HHS |
| M7 | QĐ xử phạt/khởi tố mới đối với TCH/CRV/HHS hoặc người nội bộ | đến 31/03/2027 | Không có ⇒ giữ nguyên | Có ⇒ CK quản trị +10 điểm % ⇒ ≈ −1.350 đ |

**Điều làm tôi sai:**
- **Hướng tốt:** PPA của HHS thực ra **thận trọng**, vì NC-II bán ở biên ~52% bền suốt dự án; khi đó haircut 25% là quá cao. I.14 (1.329 theo giá gốc, chưa có thặng dư trong sổ) có thặng dư lớn.
- **Hướng xấu:** giá trị hợp lý PPA đặt theo giá bán kỳ vọng năm 2025, trong khi BĐS miền Bắc vào chu kỳ yếu (sector read BĐS 31/10, kịch bản B 20–25%); phần cao tầng/NOXH NC-II bán chậm hơn 4 năm.

---

## 9. Thay đổi so với template và các số [TCH-DD] cần sửa
- "HHS độc quyền xe đầu kéo International" ⇒ **Dongfeng (TQ)** theo BCTC và website 2026 (§2).
- "HHS thị trường định giá ~4.082 ≈ phần HHS trong VCSH CRV ~3.880" — **đúng**. Bổ sung: cơ sở giá trị hợp lý cho HHS VCSH mẹ 9.153 (0,45x).
- Thêm 2 rủi ro quản trị ở pháp nhân HHS mà [TCH-DD §6] chưa nêu: uỷ quyền làm căn cứ kiểm soát, và người bán HHS Capital.
