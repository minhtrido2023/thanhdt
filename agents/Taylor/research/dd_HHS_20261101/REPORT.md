# HHS — Lãi Q3 tăng nhờ CRV bàn giao NC-II và bảng cân đối không vay, nhưng sổ sách ~21.200 đ/cp chứa ~4.130 tỷ thặng dư định giá chưa thực hiện; giá 9.450 chỉ thấp hơn tâm ~5–8% trên cùng cơ sở với DD TCH

DD HHS (CTCP Đầu tư Dịch vụ Hoàng Huy, HOSE) · **v2** · as-of 01/11/2026 · job `Taylor_20261101_041414`

> v2 = v1 (`REPORT_v1.md`, job `Taylor_20261101_033221`) + `GAPS_FILL.md` (job `Taylor_20261101_040247`) + 12 đính chính C1–C12 của phản biện (`SKEPTIC_20261101.md`, REFUTED medium). Các số phản biện nêu **đã tự kiểm lại trên ảnh BCTC gốc** (Q2HN tr.7–9; 6THN tr.9–10) trước khi dùng. Bảng "đã áp / không áp" ở cuối.
>
> Nghiên cứu read-only, viết trung dung. Không khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON, không chạy §2.5. Có yếu tố pháp lý ⇒ chỉ WARNING.
> **Đơn vị: tỷ đồng** trừ khi ghi khác. Niên độ dương lịch: Q3/2026 = 01/07–30/09/2026.
> Số tự tính: `calc/valuation_v2.py` → `calc/valuation_v2_out.txt` (v1: `valuation.py`). Mọi tham số định giá là **ước lượng**.
>
> **Nguồn:** **[Q3HN]/[Q3R]** BCTC hợp nhất/riêng 9T/2026, ký 29/10/2026, **chưa soát xét** · **[Q2HN]** BCTC hợp nhất Q2/2026 tự lập, ký 29/07/2026 · **[6THN]** BCTC hợp nhất 6T/2026, AASC soát xét, ký 27/08/2026 · **[KT25]** BCTC hợp nhất 2025, AASC kiểm toán · **[BCTN25]** BCTN 2025 (hoanghuyhhs.vn) · **[NQ25]** tài liệu ĐHĐCĐ 24/04/2025 · **[DNSE]** latest_trade/OHLC read-only, lấy 01/11/2026 10:40 ICT, phiên cuối 30/10/2026 (khớp cuối 14:45:04) · **[BQ]** chỉ peer · **[TCH-DD]** `../dd_TCH_20261031/REPORT.md` v2 · **[Bobby]** `sector_read_xe_tai_thuong_mai_vn_20261101.md` (đọc ngành độc lập).

---

## 0. Tóm tắt

**Bản chất:** holding BĐS (51,15% lợi ích CRV) kèm mảng nhập khẩu/phân phối xe tải Dongfeng. BĐS = 20.738 / 23.060 tổng tài sản (90%); ô tô 695 [Q3HN TM39].

**Tích cực (đều có số):**
- Q3/2026 lãi tăng mạnh là thật: CRV bàn giao đợt đầu Hoàng Huy New City-II (NC-II). DT BĐS Q3 1.746, LNST hợp nhất 198,4, mẹ 115,8 (Q3/25: 17,2).
- **Không vay** (đã trả 390 vay dài hạn và 69 vay TCH). Tiền + tiền gửi hợp nhất 1.031.
- Ngoài phần bàn giao, NC-II vẫn có **thu mới**: DT BĐS 9T ~2.026 gồm VAT, nhưng người mua trả trước chỉ giảm 354 ⇒ ~1.670 đến từ trả trước mới/phải thu (ước lượng) (C10).
- Biên gộp BĐS kinh tế (bỏ phần PPA) Q3 ≈ **52,2%**, khớp biên NC-II ở TCH 51,9% (C7).
- Kiểm toán 2025 và soát xét 6T/2026 chấp nhận toàn phần, không nhấn mạnh. BCTC 2025 **không có** thuyết minh bảo lãnh/mua lại xe (G7).

**Tiêu cực / cần lưu ý:**
- Sổ sách hợp nhất 21.188 đ/cp **không phải "giá trị đã có"**: ~4.134 tỷ (≈9.570 đ/cp) là **thặng dư định giá chưa thực hiện** do PPA khi hợp nhất CRV 06/2025 (ước lượng từ thuế hoãn lại).
- **Soát xét 6T hạ lãi mạnh** so bản tự lập: LNST mẹ 65,51 → 43,32 (**−34%**) (C2). **Q3 (mẹ 115,8) chưa soát xét** ⇒ rủi ro điều chỉnh tương tự.
- Mảng xe Q3 DT 156,4 (−36,6% YoY) — nhưng nền Q3/25 đột biến (246,5 ≈ cả H1/25); **9T +1,4%**. Cờ thật là tồn kho ×1,9, biên −3–5 điểm %, bắt đầu chiết khấu thương mại (C5).
- CFO 9T −2.110 (đất I.14 ~1.066, tồn kho NC-II); tiền công ty mẹ chỉ 171.

**Định giá (C1 — cùng cơ sở thặng dư/PV với DD TCH):**
- **Vùng ~7.600–13.000 đ, tâm ~9.950 đ** (trọng số 30/50/20; ~10.250 nếu đối xứng 25/50/25). Giá **9.450 nằm trong vùng, nửa dưới, thấp hơn tâm ~5–8%**.
- Tham chiếu cơ sở PPA của chính HHS (v1, đã sửa mảng xe): tâm ~11.700 (giá −19%). Hai cơ sở lệch nhau ở **một** điểm: PPA ghi CRV theo giá bán kỳ vọng 2025, DD TCH đặt thặng dư 15/40/55% × PV 0,617. Báo cáo này **chọn cơ sở TCH** vì cùng tài sản ⇒ hai báo cáo nhất quán.
- Chưa cộng thặng dư BĐSĐT của CRV: tối đa ~+650 đ/cp (ước lượng, cận dưới chênh sổ), không đưa vào tâm vì lợi suất cho thuê chỉ ~2,3%.

**WARNING pháp lý/quản trị: trung bình**, mở chờ G4/G11 (§6) — cấu trúc thương vụ HHS Capital (người bán không nêu tên, không định giá độc lập, TCH được biểu quyết), 2 kết luận thanh tra đang mở ở nhóm CRV/Pruksa, ký quỹ 28,4 tỷ cho cá nhân.

---

## 1. Kết luận và vùng giá (cơ sở chính = cơ sở DD TCH)

| Vùng giá (đ/cp, 431,99 tr cp) | Đọc |
|---|---|
| < ~7.600 | Chỉ hợp lý nếu thặng dư quỹ đất CRV còn lại ~15% (biên gộp ~24%), CK holding 35% + quản trị 15%, mảng xe 25 tỷ × 5x |
| **7.600 – 13.000** (hiện 9.450) | **Trong vùng, nửa dưới.** Tâm ~9.950 (30/50/20) – 10.250 (25/50/25); giá thấp hơn tâm **5–8%** |
| > ~13.000 | Cần thặng dư ≥55% (biên ~47%), CRV trả cổ tức tiền đều để CK holding về ~15%, và thị trường bỏ chiết khấu quản trị |

**Ba kịch bản** (`calc/valuation_v2_out.txt`):

| Kịch bản | P | Biên ròng backlog NC-II × PV 0,886 | Thặng dư HTK CRV còn lại (7.338,8) × PV 0,617 | CRV 100% | Ô tô LNST × P/E | CK holding / quản trị | Giá trị |
|---|---|---|---|---|---|---|---|
| Tích cực | 0,20 | 36% | 55% (biên gộp ~47%) | 11.139 | 50 × 8 | 15% / 5% | **~13.020** |
| Cơ sở | 0,50 | 33,5% | 40% (~40%) | 10.397 | 35 × 6 | 25% / 10% | **~10.160** |
| Tiêu cực | 0,30 | 30% | 15% (~24%) | 9.176 | 25 × 5 | 35% / 15% | **~7.580** |
| **Trọng số** | | | | | | | **~9.960** |

- CRV 100% = CRV giá gốc 7.735 (= CRV theo GTHL 15.818 suy từ NCI − thặng dư PPA sau thuế 8.083) + backlog + thặng dư. Tham số backlog/thặng dư/PV/Ke **lấy nguyên từ** `tch_valuation_v2.py` (NMTT NC-II 3.099,2; VAT 1,08; HTK CRV còn lại 7.338,8; Ke 12,85%).
- **Đệm biên** (theo phản biện TCH B3): cả ba kịch bản đặt biên gộp tương đương **dưới** biên lịch sử 51,9% (⇔ thặng dư ~70%). Phần chênh là đệm cho chi phí hoàn thành chưa quan sát được (HH1–HH4 cao tầng, I.14). Ở thặng dư 70% (biên ~52%) tâm cơ sở lên ~11.245 — tức là kịch bản "biên lịch sử giữ nguyên" chỉ ngang cơ sở PPA của HHS chứ không cao hơn.
- P nghiêng xuống (0,30 vs 0,20): mảng xe yếu, ngành ở pha "muộn nhịp tăng" [Bobby], Q3 chưa soát xét.
- **Mảng xe đã hạ (C8):** cơ sở 35 × 6x thay 40 × 8x — P/E theo trung vị peer 5,9x [BQ], LNST theo nhịp EBIT lõi 9T ~39 (≈ 52/năm trước thuế, ~42 sau thuế) và Q3 yếu hơn. Tác động −229 đ/cp so v1.

**Hai cơ sở, minh bạch (C1):**

| Cơ sở | Tiêu cực / Cơ sở / Tích cực | Tâm | Giá vs tâm |
|---|---|---|---|
| **TCH-DD (chính)**: thặng dư 15/40/55% × PV 0,617 + backlog × PV 0,886 | 7.580 / 10.160 / 13.020 | ~9.960 | **−5%** (−8% nếu 25/50/25) |
| PPA của HHS (tham chiếu): haircut 60/40/25% phần thặng dư PPA còn lại | 8.760 / 11.910 / 15.560 | ~11.690 | −19% |

v1 viết "giá thấp hơn tâm ~20%" là ở cơ sở PPA; trên cùng cơ sở với DD TCH khoảng cách chỉ ~5–8%. "Kịch bản tiêu cực" của v1 (8.800) gần bằng "cơ sở" của cơ sở TCH chiết khấu 30% — nghĩa là v1 lạc quan hơn DD TCH đáng kể khi định giá cùng một tài sản.

**Ma trận thặng dư (CK 25%/10%, xe 210):** 10% → 9.075 (giá +4%) · 25% → 9.617 (−2%) · **40% → 10.160 (−7%)** · 55% → 10.702 (−12%) · 70% → 11.245 (−16%). Giá 9.450 ngầm định thặng dư ~20% (biên gộp ~28%) ở mức chiết khấu cơ sở.

**Độ nhạy cơ sở (đ/cp):** CK holding ±5đ% ≈ ∓555 · CK quản trị ±5đ% ≈ ∓565 · thặng dư ±15đ% ≈ ±545 · mảng xe 25×5 → 50×8 = −180/+395 · Ke 12,3–13,4% chỉ ±30. **Chiết khấu là tham số nhạy nhất**, giống DD TCH.

**Chưa cộng — thặng dư BĐSĐT CRV:** BĐSĐT hợp nhất HHS 2.459,74 vs TCH 1.438,45 cùng 30/09/2026 (TCH hợp nhất HHS theo giá gốc) ⇒ thặng dư ≥ ~1.021 trước thuế (cận dưới, vì 1.438 còn gồm BĐSĐT riêng TCH nếu có) ⇒ phần HHS sau thuế ~418 ⇒ **+~650 đ/cp** sau CK cơ sở. **Không đưa vào tâm**: thu tiền thuê tối thiểu ≤1 năm chỉ 57,2 (~2,3% giá trị sổ) và DD TCH cũng giữ BĐSĐT theo sổ.

**Phép thử chéo:**
- TCH tự giao dịch ở **0,98x VCSH mẹ** [TCH-DD] ⇒ 0,98 × BV giá gốc 11.617 = **11.385** (chưa trừ chiết khấu tầng holding thứ hai) (C4).
- Trung vị peer BĐS 0,72x (cơ sở BQ, **chưa truy nguyên** cách tính VCSH) ⇒ 8.364.
- 51,15% × VCSH CRV sổ riêng 31/03/2026 (7.579) = **8.974 đ/cp** — thị trường gần như chỉ trả cho phần CRV theo sổ.
- Giá niêm yết CRV ~23.000 (khớp cuối 21/10/2026) **bị loại**: chỉ 24 phiên có khớp từ 03/08 [DNSE], thanh khoản ~0,8 tỷ/3 tháng như [TCH-DD §8d] (C9).

**Ở ±5% quanh giá (8.980–9.920):** vẫn "trong vùng, dưới tâm". Giá chỉ ngang tâm khi ≥ ~9.950.

**Thanh khoản [DNSE]:** ADV20 = ADV60 = 10,8 tỷ đ/phiên; đỉnh/đáy 52 tuần 15.600 / 8.580.

---

## 2. Kiểm lại các số đầu vào

| Số / giả thuyết | BCTC gốc | Kết luận |
|---|---|---|
| "LN 2025 ~3.530 là lãi kế toán một lần khi kiểm soát CRV" | [KT25] TM3.1/TM27: lãi đánh giá lại khoản đầu tư khi hợp nhất qua nhiều giai đoạn **3.488,72**; không có lợi thế thương mại. Là đánh giá lại phần 43,56% đã nắm theo GTHL | ✓ ghi nhận kế toán nội bộ nhóm, **không tạo giá trị kinh tế mới** |
| Báo chí: Q2/2026 DT 233,8, LNST 31,6 | **[Q2HN tr.7–8, tự kiểm]** DTT Q2 233,81; LNST Q2 31,60; mẹ 25,34; 6T tự lập LNST 81,96, mẹ 65,51, EPS 152 | ✓ (v1 ghi "chưa kiểm" là sai — có Q2HN trong `src/`) (C2) |
| 6T tự lập vs soát xét | xem bảng §3a' | **soát xét hạ LNST mẹ 34%** |
| Q3/2026 DT 1.901, LNST 198,4 | [Q3HN] DTT 1.901,13; LNST 198,41; mẹ 115,76 (= 9T 159,09 − 6T soát xét 43,32) | ✓, nhưng 9T **chưa soát xét** |
| [TCH-DD]: HHS 58,31% của TCH | [Q3HN TM22b] 2.519,06 tỷ = 58,31%; [BCTN25 p.15] 251.905.777 cp | ✓ |
| [TCH-DD]: CRV biểu quyết qua HHS | [Q3HN TM1.5] lợi ích 51,15%, biểu quyết 58,53% | ✓ |
| [TCH-DD]: "HHS độc quyền xe đầu kéo International" | [BCTN25 p.12] HHS là "đại lý xe tải Dongfeng"; nhà cung cấp China Dongfeng Motor Industry Imp&Exp (phải trả 305,26); Hoàng Giang bán Sinotruk/Howo, "tuỳ thời điểm" International; BCTN p.21: HHS "sẽ mua và phân phối các dòng xe Navistar của TCH" | **✗ sửa ở [TCH-DD]**: HHS = Dongfeng; Navistar/International chủ yếu ở TCH |
| [TCH-DD] P/B TCH | 0,98x VCSH mẹ (v1 ghi 0,82x [BQ] — sai cơ sở) | ✗ đã sửa (C4) |
| BQ: HHS P/B 0,24 | BQ chia **tổng VCSH gồm NCI** tại 30/06 (16.681,5 ⇒ BVPS 38.616; P/B 0,2447 — theo phản biện; Q2HN tự lập ghi 16.700,5) | ✗ BẪY BQ. P/B đúng (VCSH mẹ) 0,45x (C6) |
| TCH mua 800 tỷ cp HHS | [KT25 LCTT] thu 799,95; vốn tăng 640 ⇒ 12.500 đ/cp; 64,0 tr cp hạn chế 1 năm [BCTN25] | ✓ |

---

## 3. Chất lượng lợi nhuận

### 3a. KQKD hợp nhất [Q3HN]

| | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 1.901,13 | 323,38 | 2.379,38 | 610,04 |
| LN gộp | 288,77 | 29,61 | 358,95 | 64,03 |
| DT tài chính | 17,58 | 24,79 | 93,77 | **3.736,81** |
| CPBH / QLDN | 54,89 / 11,14 | 25,22 / 13,53 | 90,78 / 34,47 | 41,01 / 23,83 |
| Lãi/lỗ thanh lý BĐSĐT | −5,58 | – | −17,89 | – |
| LNTT | 238,34 | 15,87 | 310,38 | 3.594,65 |
| Thuế hiện hành / hoãn lại | 167,66 / −127,74 | 14,86 / −9,54 | 197,19 / −148,18 | |
| LNST / **mẹ** / thiểu số | 198,41 / **115,76** / 82,65 | 10,55 / 17,25 / −6,69 | 261,37 / **159,09** / 102,28 | 3.582,32 / 3.591,72 / −9,40 |

### 3a'. Bản tự lập vs bản soát xét — 6T/2026 (C2, tự kiểm trên ảnh)

| Chỉ tiêu | Tự lập [Q2HN tr.8–9, 29/07] | Soát xét AASC [6THN tr.9, 27/08] | Chênh |
|---|---|---|---|
| Giá vốn hàng bán | 397,79 | 408,08 | +10,29 |
| Lãi/lỗ thanh lý BĐSĐT | **+8,95** | **−12,30** | −21,25 |
| LN thuần HĐKD | 102,95 | 71,45 | −31% |
| LNTT | 101,67 | 72,04 | **−29%** |
| Thuế hoãn lại | −10,99 | −20,44 | |
| LNST | 81,96 | 62,95 | **−23%** |
| LNST mẹ | 65,51 | 43,32 | **−34%** |
| EPS (đ) | 152 | 100 | |

- Q2 sau soát xét (suy ra, ước lượng): LNST ≈ 62,95 − (81,96 − 31,60) = **12,6**; mẹ ≈ 3,2. Báo chí dùng số tự lập 31,6.
- Điều chỉnh tập trung ở **giá vốn và lãi/lỗ bán BĐSĐT** — chính những dòng chịu ảnh hưởng của PPA khi bán tài sản đã được đánh giá lại.
- ⚠️ **WARNING:** Q3 (LNST mẹ 115,8; LNST 198,4) **chưa soát xét/kiểm toán**. Có tiền lệ điều chỉnh −34% ở 6T, cùng loại dòng (giá vốn BĐS sau PPA). Mốc kiểm: BCTC năm 2026 kiểm toán (03/2027) — xem M1.

### 3b. Theo mảng — Q3 = 9T − 6T [Q3HN TM24/26 − 6THN TM25/27]

| Mảng | DT Q3/26 (Q3/25) | LN gộp Q3/26 (Q3/25) | Biên | DT 9T/26 (9T/25) | Biên 9T (9T/25) |
|---|---|---|---|---|---|
| **BĐS** (CRV: NC-II, H1) | 1.746,23 (75,33) | 272,38 (−10,5) | 15,6% | 1.875,89 (110,28) | 15,8% |
| **Ô tô & phụ tùng** (mẹ) | 156,40 (246,51) | 18,85 (39,72) | 12,1% (16,1%) | 503,25 (496,28) **+1,4%** | 13,0% (15,9%) |
| Khác | 1,21 | | | 4,41 | |

**Biên BĐS báo cáo 15,6% vs kinh tế ~52%:**
- Khi hợp nhất CRV, HHS nâng HTK CRV lên GTHL (PPA), kèm thuế hoãn lại phải trả 2.183,9 [KT25 TM3.1]. Khi bán, giá vốn cấp HHS gồm cả phần nâng giá.
- Q3: thu nhập thuế hoãn lại 127,74 ⇒ phần PPA qua giá vốn ≈ 638,7 ⇒ biên ex-PPA = (272,38 + 638,7)/1.746,23 = **52,2%** (ước lượng, thuế 20%) (C7). (v1 dùng 9T 718 — gồm cả PPA của BĐSĐT bán ra.)
- ⇒ Phần lớn lãi NC-II đã vào LN HHS năm 2025 (3.488,7). LN BĐS hằng quý của HHS **thấp có hệ thống** so lãi kinh tế ⇒ P/E vô nghĩa (9T annualized ~19x); định giá theo NAV.

**Một lần / dồn:**
- Q3 là **đợt bàn giao đầu** của NC-II, mang tính dồn. LN mẹ Q3 115,8 không phải mức chạy bền. NCI hưởng 41,7% LNST.
- **Tích cực (C10):** người mua trả trước NC-II chỉ giảm 354 (3.453,1 → 3.099,2) trong khi DT BĐS 9T ~2.026 gồm VAT ⇒ ~1.670 là trả trước mới hoặc phải thu (ước lượng) ⇒ NC-II **vẫn đang bán thêm**, backlog chưa cạn nhanh như phép chia đơn giản.
- Lãi tiền gửi 9T 91,5 sẽ giảm: HTM ngắn hạn 2.435 → 849 do nộp tiền đất I.14.

### 3c. Mảng xe tải (đối chiếu [Bobby])

| Chỉ tiêu [Q3R/Q3HN] | 31/12/25 | 30/09/26 | Đọc |
|---|---|---|---|
| HTK ô tô | 317,6 | **608,2** (×1,9) | cờ vàng — tồn kho tăng nhanh hơn doanh thu |
| — xe sát xi (NVL) | 38,65 | 255,42 | nhập sát xi chờ đóng thùng |
| — hàng gửi bán (đại lý) | 210,57 | 229,30 | chưa kiểm được tồn kho đại lý |
| Phải thu khách mua xe | 89,87 | 87,96 (DP 3,50 Phúc Hưng) | ổn định |
| Phải trả Dongfeng TQ | 364,01 | 305,26 | tài trợ tồn kho bằng tín dụng nhà cung cấp |
| Biên gộp ô tô (riêng) | 16,0% (9T/25) | 12,5% (9T/26); Q3 10,7% | giảm 3–5 điểm % |
| CK thương mại | 0 | 3,88 (9T); 2,45 Q3 | bắt đầu chiết khấu |
| Bảo lãnh/mua lại xe cho NH | — | **[KT25] không có thuyết minh** (TM24 chỉ thuê hoạt động) | không có bằng chứng; "không thuyết minh ≠ không có" (G7) |

**Đọc (C5):**
- DT xe theo quý 2026: Q1 ~143,8 / Q2 ~203 / Q3 156,4 (Q1, Q2 suy từ 6T và [TCH-DD], ước lượng). Q3/25 = 246,51 là quý **đột biến** (≈ cả H1/25 249,77). So với nền đó Q3 −36,6%; **cả 9T +1,4%**. "Giảm 37%" không phải xu hướng năm.
- Cờ thật là **tồn kho ×1,9 + biên giảm + chiết khấu** ⇒ rủi ro giảm giá hàng tồn Q4/Q1 nếu ngành chậm (F2/F3 của Bobby).
- Quy mô nhỏ: EBIT lõi mảng xe 9T ≈ 39. Mảng xe ≈ 125–400 tỷ (3–10% vốn hoá). **Không quyết định** giá trị HHS.
- Peer P/E [BQ 30/10]: HTL 5,9 · TMT 5,4 · SVC 4,1 · VEA 6,4 · HAX 16,2 ⇒ trung vị ~5,9x ⇒ dùng 5/6/8x.
- Sản phẩm [BCTN25, G2]: Dongfeng hạng trung/nặng; DT ô tô & phụ tùng 2025 699,58 (2024: 522,05); Hoàng Giang (Sinotruk/Howo) LNST 2025 71,5. Chưa có số xe, chưa thấy từ "độc quyền".

---

## 4. Bảng cân đối

| [tỷ] | Riêng (mẹ) 30/09/26 | Hợp nhất 30/09/26 | Hợp nhất 01/01/26 |
|---|---|---|---|
| Tiền + HTM | **171,4** | **1.030,6** | 3.444,7 |
| Vay | **0** | **0** | 390,0 |
| Người mua trả trước | 4,5 | 3.142,8 (NC-II 3.099,2) | 3.530,0 |
| Kinh phí bảo trì giữ hộ | – | 124,75 | 119,30 |

- Net cash hợp nhất "thật" ≈ 1.031 − 125 = ~906, chưa trừ chi phí còn lại để giao các căn đã nhận tiền (G10).
- Tiền mẹ chỉ 171; phần còn lại ở CRV/Đại Lộc (thiểu số 48,85%).
- 9T: nộp tiền đất ~1.066 [TM18]; HTK +1.909 (I.14 1.329, NC-II +336, ô tô +290); trả vay 390; capex 240 (17B Bà Triệu 243 — đất trụ sở CRV, "đang thủ tục pháp lý").
- Vay duy nhất trong 2025 (390 VietinBank Ngô Quyền) do **CRV** vay, thế chấp tài sản NC-II; HHS mẹ không bảo lãnh [KT25 TM16]. Đã trả hết.
- Cổ tức 9T/26: 0.

---

## 5. Cấu trúc sở hữu

```
Ông Đỗ Hữu Hạ + HH Finance 35,99% ─► TCH ─58,31%─► HHS ─51,15% lợi ích (58,53% biểu quyết)─► CRV ─► NC-II, I.14 (Đại Lộc), H1
                                      └──────────── 38,19% trực tiếp ─────────────────────────► CRV
```

- HHS nắm CRV 51,15% lợi ích (trực tiếp + Hoàng Giang 99,79% + HHS Capital 99,996%) — không cần uỷ quyền vẫn >50% (biên 1,15đ%). Cả nhóm TCH kiểm soát CRV 89,35% biểu quyết kể cả bỏ uỷ quyền.
- Lợi ích hiệu dụng của TCH tại CRV = 38,19% + 58,31% × 51,15% = 68,02% ✓ [TCH-DD].
- **SOTP TCH (C12):** thay dòng "HHS 58,31% theo giá thị trường" bằng tâm ~9.960 ⇒ **+~128 đ/cp TCH** (v1: +615). ⚠️ Trộn cơ sở: CRV trực tiếp (38,19%) theo sổ giá gốc, CRV qua HHS theo NAV cơ sở TCH có chiết khấu. Chỉ là phép thử, không cộng vào tâm TCH.
- Chiết khấu 2 tầng: tiền NC-II chỉ lên HHS qua cổ tức CRV; 9T/2026 chưa thấy cổ tức CRV về HHS.
- **Cổ đông [BCTN25 p.15, G6]:** TCH 58,31%; nhỏ 41,69%; nước ngoài 0,59% (112 cổ đông), room 50%. Nhóm Đinh Quang Chiến + CTCP PT Đô thị Từ Liêm + CTCP Thuỷ điện Trà Xom thành cổ đông lớn 5,06% (04/06/2026) → 5,12% (19/10/2026). Free float thực ~36–37% (tự tính).

---

## 6. Pháp lý, quản trị — ⚠️ WARNING mức **trung bình**, mở chờ G4/G11

**Vì sao "trung bình" (hạ từ "trung bình–cao" của v1) (C11):** TCH có 2 QĐ xử phạt thật (UBCKNN 295 tr 12/2024; thuế 20,21 tỷ 04/2026); **HHS chưa thấy QĐ xử phạt nào** 2023–2026 (đã tra CBTT trang 1–7, BCTN25, web; chưa tra ssc.gov.vn). Thương vụ HHS Capital **đã được ĐHĐCĐ duyệt** và AASC chấp nhận. Nhưng **giữ mở**: 2 kết luận thanh tra chưa lượng hoá, người bán chưa xác định. Hai sự kiện nâng lại mức: người bán là người liên quan (M4) hoặc QĐ phạt/khởi tố mới (M7).

**(a) Thương vụ kiểm soát CRV và HHS Capital (C3, viết lại theo bằng chứng):**
- **Quy trình đã duyệt trước:** ĐHĐCĐ 24/04/2025 duyệt nâng sở hữu CRV (Điều 10, 99,459% tán thành) [NQ25]. BBTT 02/2025 ngày 06/05/2025 cho HHS quyền bổ nhiệm HĐQT/GĐ HHS Capital **trước** khi trả tiền ⇒ quyền kiểm soát dựa trên sở hữu đã sắp đặt trước, uỷ quyền 7,53% là bước nối. Lãi đánh giá lại 3.488,7 phát sinh khi vượt ngưỡng kiểm soát — đi đường nào cũng ghi nhận như vậy.
- **Bản chất 3.488,7:** ghi nhận kế toán **nội bộ nhóm** (CRV vốn đã là con TCH), không tạo giá trị kinh tế mới cho cổ đông TCH.
- **Điểm cần cảnh báo:**
  - Tờ trình 07/TT-HĐQT nói HHS Capital và người bán "không phải người liên quan" nhưng **không nêu tên**; dự thảo hợp đồng để trống bên bán; **không có định giá độc lập**; Điều 10 **không** loại cổ đông có lợi ích liên quan ⇒ TCH được biểu quyết [NQ25 p.3–11, 97–103].
  - HHS Capital lập 31/03/2025 theo báo cáo sở hữu CRV (cùng ngày tờ trình; **BCTN25 lại ghi 31/05/2025** — chưa hoà giải), vốn 501 tỷ = 50,1 tr cp CRV; HHS trả 1.302,55 tỷ (~26.000 đ/cp CRV) ngày 18/06/2025, cao hơn GTHL (~23.130) khoảng 12% ⇒ **premium ~143,5 tỷ ≈ 3,5% vốn hoá HHS hiện tại**, ghi giảm LNST chưa phân phối.
  - Uỷ quyền 7,53% từ "a group of shareholders" — không tên, không thời hạn [KT25].

**(b) Bảng sự kiện:**

| Sự kiện | Nguồn | Mức |
|---|---|---|
| HHS Capital: người bán không tên, không định giá độc lập, premium ~143,5 tỷ | [NQ25], [KT25 TM3.2] | WARNING — không kiểm được tuyên bố "không liên quan" |
| **KL 08/KL-TTTP 26/02/2026** (Thanh tra TP Hải Phòng) — NƠXH của Pruksa VN (HHS 90,17%): yêu cầu "rà soát, điều chỉnh giá bán theo kết quả quyết toán", soát xét hồ sơ mua sai thông tin | [KT25 TM37] sự kiện sau niên độ, không điều chỉnh BCTC | WARNING mở — quy mô chưa đo; mảng NƠXH nhỏ (thu thuê tối thiểu ≤1 năm 57,2) |
| **TB 2124/TB-TTCP 11/10/2024** (Thanh tra Chính phủ) — chuyển mục đích đất, khối đế N01 (275 Nguyễn Trãi) của CRV: tạm trích 7,87 tỷ, CRV "chưa nhận văn bản chính thức" | [KT25 TM20] | WARNING mở — HHS hưởng ~51% nếu phát sinh thêm |
| Ký quỹ **28,4 tỷ cho cá nhân Phạm Văn Xuân** — phát sinh 2026 (31/12/2025 ký quỹ chỉ 3,77) | [Q3HN TM07], [KT25 TM8] | cờ vàng — ~66 đ/cp nếu mất trắng; mục đích chưa rõ |
| Chi phí phạt/truy thu thuế 2025 2,44 tỷ (2024: 0,04), không nêu QĐ | [KT25 TM32] | nhỏ |
| TCH: QĐ 1020/QĐ-XPHC thuế 20,21 tỷ; UBCKNN 295 tr | [TCH-DD §6d] | WARNING ở công ty mẹ |
| Kiểm toán 2025 / soát xét 6T: chấp nhận toàn phần | [KT25], [6THN] | sạch — nhưng soát xét điều chỉnh LN −34% (§3a') |
| HĐQT 5 người, 2 người họ Đỗ, 1 độc lập | [Q3HN] | giám sát độc lập yếu |
| Q3HN TM41 câu chữ "đã soát xét … do Công ty tự lập"; trình bày ĐTTC dài hạn lạ | [Q3HN] | lỗi soạn thảo, không ảnh hưởng tổng |

Không có dấu hiệu khởi tố hay ngoại trừ kiểm toán. Theo luật 27/09: phân tích bình thường, chỉ cảnh báo.

---

## 7. Định giá — tóm cơ sở

1. VCSH mẹ hợp nhất 9.152,9 = 21.188 đ/cp (cơ sở GTHL tại 12/06/2025).
2. Thặng dư PPA còn trong sổ: thuế hoãn lại 2.020,76 / 20% ⇒ 10.104 trước thuế, 8.083 sau thuế, **phần HHS 4.134** (ước lượng; gồm HTK và BĐSĐT). BV giá gốc = 5.018 = **11.617 đ/cp**.
3. **Cơ sở chính (TCH):** CRV 100% = 7.735 + NMTT 3.099,2/1,08 × biên ròng × 0,886 + 7.338,8 × thặng dư × 0,617. HHS = [51,15% × CRV × (1 − CK holding) + khác 678 + xe] × (1 − CK quản trị).
4. **Chi phí vốn:** Ke nội địa 12,3–13,4% (tâm 12,85%, β ~1,16–1,23 của TCH) ⇒ PV 0,886 (1 năm) / 0,617 (4 năm). Không chạy DCF vô hạn vì dòng tiền BĐS có thời hạn. Ke trong dải chỉ đổi ±30 đ/cp.
5. Độ nhạy và ma trận: §1.

---

## 8. Mốc kiểm chứng — HAI chiều

| # | Mốc | Ngày | Đổi lên nếu | Đổi xuống nếu |
|---|---|---|---|---|
| M1 | **BCTC năm 2026 kiểm toán** (kiểm lại Q3 chưa soát xét) | 03/2027 | LNST mẹ 9T không bị điều chỉnh >10%; kiểm toán sạch | Điều chỉnh >10% như 6T (−34%), hoặc ngoại trừ/nhấn mạnh về PPA/HTK/uỷ quyền ⇒ tâm −1.000 đến −1.500 đ (ước lượng) + nâng WARNING |
| M1b | BCTC Q4/2026 tự lập | 01/2027 | NMTT NC-II tiếp tục có thu mới; DT BĐS Q4 ≥ 1.000 | DT BĐS Q4 < 500 và NMTT không bổ sung |
| M2 | Mảng xe Q4/2026 [Q4R] | 01/2027 | DT ô tô ≥ 200 **và** HTK ô tô < 450 | DT < 150 **và** HTK > 600 hoặc trích DP giảm giá HTK |
| M3 | Cổ tức tiền CRV về HHS | 31/12/2027 | ≥ 500 tỷ toàn CRV ⇒ CK holding −5đ% ⇒ +~555 đ | Không có, CRV tiếp tục dồn tiền vào đất mới |
| M4 | Danh tính người bán HHS Capital / nhóm uỷ quyền | bất kỳ | Bên độc lập ⇒ CK quản trị −5đ% (+~565 đ) | Người liên quan ông Hạ/HH Finance ⇒ CK quản trị +5đ% (−~565 đ) + WARNING trung bình–cao |
| M5 | Ngành xe [Bobby F2/F3] | 20/01/2027, 20/04/2027 | Q4 > +15% | Q4 âm hai chữ số |
| M6 | BCTC soát xét TCH 6T FY26 | 30/11/2026 | Số NC-II/CRV khớp | Điều chỉnh lớn ở CRV |
| M7 | QĐ phạt/khởi tố mới (TCH/CRV/HHS/người nội bộ); toàn văn KL 08 / văn bản nghĩa vụ đất N01 | đến 31/03/2027 | Không có ⇒ giữ | Có ⇒ CK quản trị +10đ% (≈ −1.130 đ) |

**Điều làm sai:**
- **Hướng tốt:** NC-II giữ biên ~52% suốt dự án (thặng dư ~70%) ⇒ tâm ~11.245; cộng thặng dư BĐSĐT ⇒ ~11.900 — tiến về cơ sở PPA.
- **Hướng xấu:** BĐS miền Bắc vào nhịp yếu, cao tầng HH1–HH4/I.14 bán chậm, Q3 bị điều chỉnh khi kiểm toán, mảng xe phải giảm giá tồn kho.

---

## 9. Sửa ở [TCH-DD]
- "HHS độc quyền xe đầu kéo International" ⇒ HHS là đại lý **Dongfeng**; Navistar/International chủ yếu ở TCH [BCTN25 p.12, 21].
- Cùng tài sản CRV: hai báo cáo nay dùng **cùng** tham số thặng dư/PV.

---

## 10. Đã áp / không áp — đính chính phản biện C1–C12

| # | Nội dung | Áp? | Ghi chú / bằng chứng tự kiểm |
|---|---|---|---|
| C1 | Hoà giải cơ sở thặng dư với DD TCH; sửa tiêu đề "là thật" | **Áp** | `valuation_v2.py`: tái lập 9.176/10.397/11.139 (phản biện: 9.163/10.382/11.124; lệch <0,2% do CRV giá gốc 7.735). Chọn cơ sở TCH làm chính, PPA làm tham chiếu. Thêm ước lượng thặng dư BĐSĐT (+~650 đ, không vào tâm). Tâm ~9.960 (thấp hơn ~10.140 của phản biện do áp C8) |
| C2 | Dùng Q2HN; bảng tự lập vs soát xét; WARNING Q3 | **Áp** | Đọc lại ảnh Q2HN tr.7–9 và 6THN tr.9–10: mọi số phản biện nêu khớp |
| C3 | Viết lại WARNING uỷ quyền/HHS Capital | **Áp** | §6a theo [NQ25], BBTT 06/05/2025, premium 143,5 |
| C4 | TCH P/B 0,98x; phép thử 11.385; peer 0,72 chưa truy nguyên | **Áp** | §1 |
| C5 | Xe −37% kèm nền đột biến, 9T +1,4% | **Áp** | §3c |
| C6 | BQ dùng VCSH 30/06 16.681,5 | **Áp một phần** | Ghi theo phản biện; tự kiểm được Q2HN tự lập 16.700,5 (chưa mở BS soát xét) |
| C7 | Biên BĐS ex-PPA Q3 52,2% | **Áp** | §3b |
| C8 | Xe P/E cơ sở theo peer 5,9x, LNST theo nhịp Q3 | **Áp** | 35×6 thay 40×8: −229 đ/cp |
| C9 | Nêu giá CRV ~23.000 rồi loại | **Áp** | DNSE: khớp cuối 21/10/2026, 24 phiên có khớp từ 03/08 |
| C10 | Thu mới NC-II | **Áp** | ~1.670 (ước lượng, gồm phải thu) |
| C11 | Mức WARNING | **Áp** | Hạ "trung bình", mở chờ G4/G11; thêm KL 08, TB 2124, ký quỹ 28,4 |
| C12 | SOTP TCH trộn cơ sở | **Áp** | §5: +128 đ/cp TCH, ghi chú trộn cơ sở |
| — | Không áp | | Không có đính chính nào bị bác. Giữ trọng số 30/50/20 (phản biện không phản đối) và hiển thị thêm 25/50/25 cho đối xứng với TCH |
