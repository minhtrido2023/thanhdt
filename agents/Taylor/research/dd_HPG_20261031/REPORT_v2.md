# DD — HPG (CTCP Tập đoàn Hòa Phát) · v2 · as-of 31/10/2026 · job `Taylor_20261031_102704` (v1: `Taylor_20261031_093839`)

> NGHIÊN CỨU READ-ONLY, trung dung. Không phải khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON, không §2.5.
> Pháp lý/quản trị ⇒ phân tích bình thường + WARNING (luật 27/09).
> v2 = v1 + đính chính của fundamental-skeptic (`SKEPTIC_20261031.md`: CONFIRMED medium, B1–B2, N1–N12) + vòng đào điểm yếu
> (`GAPS.md`, 14 mục "Số vòng 1 cần SỬA"). v1 giữ nguyên ở `REPORT_v1.md`. Danh sách thay đổi: mục cuối.
>
> **Nguồn** (mọi số BCTC đọc từ ẢNH trang render pymupdf zoom 1,4–1,6; KHÔNG dùng `.txt` OCR):
> **[HN-Q3]** BCTC hợp nhất Q3/2026 (ký 29/10/2026) · **[ME-Q3]** BCTC riêng công ty mẹ Q3/2026 (`src/bctc_congtyme_q3_2026_giaitrinh.pdf`,
> tr. in 2, 4, 5, 13, 14, 22, 23) · **[BN]** BCTC hợp nhất giữa niên độ 6T/2026 **đã soát xét** (Deloitte VN, 28/08/2026) ·
> **[HN-Q1]** BCTC hợp nhất Q1/2026 · **[KT25]** BCTC hợp nhất 2025 **đã kiểm toán** (Deloitte VN, 24/03/2026) ·
> **[CBTT]** NQ HĐQT 10 & 13/NQHP-2026 (scan, `src/gaps/cbtt_raw/`) · **[BQ]** `tav2_bq.ticker` tới phiên **30/10/2026** ·
> **[NGÀNH]** `kb/data_registry/market-state/sector_read_thep_20261031.md` (đọc ngành mù, độc lập) · **[WEB]** báo chí/CBTT qua báo, gắn nhãn.
> Số tự tính: `calc/hpg_calc.py` → `hpg_calc_out.txt` (vòng 1); **định giá v2 `calc/hpg_valuation_v2.py` → `calc/hpg_valuation_v2_out.txt`**;
> β `calc/gaps_beta_out.txt`; comp `calc/gaps_peers_vn_out.txt`; sổ đọc ảnh `calc/notes_bs.md`. Giả định tự đặt gắn **(ước lượng)**. Đơn vị: tỷ đồng.

## 1. Kết luận

**Q3/2026 gấp đôi THẬT ở cấp vận hành (LNST lõi Q3 ~7,7–8,0k tỷ, +116–120% so với lõi Q3/25 ~3,6k). Nhưng 9T "+104%" bị thổi bởi lãi
thoái vốn BĐS một lần 4.929 tỷ trước thuế; LNST lõi 9T ≈ 19,2k ± 0,4k. Ở 21.000 đ (đóng cửa 30/10/2026), HPG giao dịch P/E TTM 6,5x
(báo cáo) / ~8,0x (lõi, sau trích quỹ) / P/B 1,19x. Giá trị hợp lý v2 18.000–22.500 đ, tâm ~20.200 đ (ước lượng) ⇒ giá nằm TRONG vùng,
ở nửa trên (+4% so với tâm): xấp xỉ hợp lý, không rẻ như P/E 6,5x gợi ý vì thị trường đang chiết khấu lợi nhuận đỉnh và ưu đãi thuế
không vĩnh viễn.**

| Vùng giá (đ/cp, 8.442,96 tr cp) | Đọc |
|---|---|
| < ~18.000 | chỉ hợp lý nếu kịch bản xấu (AD HRC bị cắt sau rà soát, spread 150–200 USD/t) đang thành hiện thực |
| 18.000 – 22.500 (hiện 21.000) | xấp xỉ hợp lý; tâm ~20.200 (ước lượng) |
| > ~22.500 | đòi hỏi ROE terminal sau thuế 20% ≥ ~13% (đường LN trung lập) — cần bằng chứng ở §9 |

Giá 21.000 ngầm định **ROE terminal sau thuế đầy đủ 20% ≈ 12,4%** trên đường LN trung lập, Ke 11,83% (`hpg_valuation_v2_out.txt`) —
tức thị trường trả cho "tăng trưởng gần trung tính giá trị". ROE lõi TTM ≈ 16–17% (ở ETR ~12%), 2024 ≈ 9–10%, 2025 ≈ 12% (ước lượng).

**Kịch bản (trọng số 0,25 / 0,50 / 0,25; RI ở Ke 11,83%):** xấu ~9.600 · trung lập ~19.600 · tốt ~28.100 ⇒ RI trọng số **19.221 đ**.
**Đổi nhận định hai chiều** (chi tiết §9): LÊN tới ~21–22k nếu ≥ 2 trong 3 mốc lợi nhuận/biên (H1↑, H2↑, H5↑) đúng và AD giữ sau rà soát;
XUỐNG tới ~16–17,5k nếu biên gộp **2 quý liên tiếp thấp hơn cùng kỳ** hoặc mức AD HRC < 20% sau rà soát QĐ 1902.

## 2. Kiểm lại số đọc từ slide (giữ v1, sửa 2 dòng)

| Số slide | BCTC | Kết luận |
|---|---|---|
| DT Q3 62.669 (+70%) | DT bán hàng 62.669,1 / 36.793,9; **DTT** 62.214,2 / 36.407,4 [HN-Q3 tr.5] | ✓ (slide dùng DT gộp) |
| LNST Q3 8.265 (+106%) | 8.265,4 / 4.012,3; CĐ mẹ 8.217,3 | ✓ |
| 9T DT 171.539 (+54%), LNST 23.746 (+104%) | 171.539,2; 23.745,9 | ✓ — lõi 9T ≈ 19,2k ± 0,4k (§3b) |
| ≈ 82% DT / 108% LNST KH năm | KH 2026: DT 210.000 / LNST 22.000 [WEB ACBS] | ✓; lõi ~87% KH |
| EBITDA Q3 14.307 | LNTT 9.108,7 + lãi vay 1.774,0 + KH 3.063,1 = **13.945,8** | lệch 361; KH đã đối chiếu LCTT 6T (5.705,5) khớp ⇒ lệch do định nghĩa slide, chưa giải thích |
| TTS 283.450; VCSH 149.568 | ✓; TS − (Nợ + VCSH) = 0,0 | ✓ |
| Vốn CP 84.430 ⇒ cổ tức CP 10% | ✓ 767.498.665 cp, 8.442.964.520 cp lưu hành [BN TM28; HN-Q3 VI.17c] | ✓ |
| BĐS 19% LNST | BĐS 9T LNST 4.497,9 — gần như toàn bộ là lãi thoái vốn | nửa đúng |
| Tiền + TĐT ~2.099 | **6.852,9** = 2.099,3 + 4.753,6 [HN-Q3 VI.1] | ✗ slide chỉ lấy dòng "Tiền" |
| HTM 39.273; HTK 52.130 → 46.949 | ✓; **HTK GIẢM** | ✓ |

## 3. Câu 1 — Lợi nhuận gấp đôi có bền không?

### 3a. Bảng 7 quý (hợp nhất) [KT25/BN/HN-Q1/HN-Q3] — giữ v1

| Quý | DTT | LN gộp | Biên gộp | DT tài chính | Lãi vay | LNTT | LNST | LNST mẹ |
|---|---|---|---|---|---|---|---|---|
| Q1/25 | 37.621,7 | 5.424,2 | 14,42% | 438,1 | 627,0 | 3.839,8 | 3.349,8 | 3.344,3 |
| Q2/25 | 35.910,5 | 6.589,7 | 18,35% | 498,1 | 439,1 | 4.972,3 | 4.264,5 | 4.256,5 |
| Q3/25 | 36.407,4 | 6.087,3 | 16,72% | 711,9 | 812,2 | 4.628,3 | 4.012,3 | 3.988,3 |
| Q4/25 | 46.176,5 | 6.396,7 | 13,85% | 437,3 | 1.236,6 | 4.600,1 | 3.888,3 | 3.864,1 |
| Q1/26 | 52.900,8 | 8.365,1 | 15,81% | **5.938,3** | 1.333,4 | 10.762,2 | 9.055,9 | 8.994,0 |
| Q2/26 | 55.158,9 | 10.487,8 | 19,01% | 616,7 | 1.519,6 | 7.184,7 | 6.424,5 | 6.371,0 |
| Q3/26 | 62.214,2 | 11.922,5 | 19,16% | 1.188,0 | 1.774,0 | 9.108,7 | 8.265,4 | 8.217,3 |

Mùa vụ: Q4 và Q1 yếu hơn (2/7 quý biên < 15% đều là Q4/Q1) ⇒ so biên phải **cùng kỳ**, không so quý liền trước.

### 3b. Bóc một lần — 9T/2026

| Khoản | Trước thuế | Nguồn |
|---|---|---|
| Lãi chuyển nhượng cổ phần công ty con BĐS (toàn bộ ở Q1) | **4.929,1** | [BN TM34] |
| Thuế TNDN phân khúc BĐS H1 (thuế trên khoản lãi; 19,4% LNTT BĐS) | −1.030,2 | [BN seg tr.51] |
| Q3: lãi 112,7 − lỗ 108,4 chuyển nhượng đầu tư | 4,3 | [HN-Q3 VII.4/5] |
| **Q3: thu nhập khác 485,6 − chi phí khác 199,0 = LN khác thuần 286,6** (Q3/25: 57,3) — BCTC Q3 không thuyết minh chi tiết | 286,6 | [HN-Q3 tr.5] — **mới v2 (N12)** |
| Lãi liên doanh liên kết 9T | 1,99 | [BN tr.8] |
| BĐS vận hành (rời hợp nhất từ Q3) | ~599 sau thuế | tự tính |

⇒ **LNST lõi 9T/2026 ≈ 19,2k ± 0,4k** (19.243 theo cách v1 bỏ toàn bộ LNST BĐS; 19.695 nếu chỉ bỏ lãi thoái vốn sau thuế 20% — GAPS §10).
**Q3/26 lõi ≈ 7,7–8,0k**: 7.974 (v1) − LN khác thuần sau thuế ~260 = 7.714 nếu coi toàn bộ LN khác Q3 là phi cốt lõi.
**So lõi với lõi (N9):** Q3/25 lõi = 4.012,3 − BĐS 392,7 − LN khác ~49 ≈ **3.570** ⇒ tăng **+116%** (bỏ LN khác) / **+120%** (giữ LN khác,
so với 3.620). v1 "+99%" so lõi Q3/26 với báo cáo Q3/25 ⇒ thấp hơn thực. Tương tự, "+65,5%" của 9T so với 9T/25 báo cáo (gồm BĐS) là cận dưới.
**Chuỗi lõi theo quý (ước lượng):** Q1 ~4,9k → Q2 ~6,3k → Q3 ~7,7–8,0k (v1 ghi Q1 ~5,2k — cao ~300; GAPS §10).
**TTM lõi CĐ mẹ** = 22.943 (v1) − 260 = **~22.680**; trừ trích quỹ & thù lao tạm tính 2,16% LNST [BN TM40] ⇒ **EPS lõi ~2.630 đ, P/E lõi ~8,0x**
(v1: 2.717 / 7,7x). TTM báo cáo 27.446,5 ⇒ EPS 3.251 (khớp [BQ] PE 6,46 ⇒ BQ đã nạp Q3 kèm lãi một lần).
Thuế trên khoản lãi: 1.030,2 là chi phí P&L đúng; 1.083 [HN-Q3 VI.13] là số dư thuế phải nộp đi theo công ty con rời hợp nhất (BCĐKT) — không phải chi phí.

### 3c. Biên gộp tăng từ đâu (Q3/26 19,16% vs Q3/25 16,72%: +2,44 pp)

BCTC KHÔNG tách DT/giá vốn theo sản phẩm ⇒ không tách được bằng số BCTC phần biên đến từ spread, mix HRC hay AD. Đo được:
- Không có hoàn nhập DP HTK (DP 58,2 → 72,5). Spread HRC thô ≈ 240 → 250 USD/t, đi ngang giữa chu kỳ [NGÀNH §3b].
- **Khối lượng** [WEB thông cáo gốc hoaphat.com.vn, GAPS §4]: Q3 3,8 tr t (+54% yoy theo thông cáo); 9T 10,3 tr t (+39%), HRC 5,47 tr t (+59%), XD+CLC > 4,0 tr t (+15%).
- **Công suất (sửa v1):** thép thô **16 tr t/năm**, HRC **9 tr t/năm** ⇒ hiệu suất HRC 9T quy năm ~**81%**, thép thô ~89% (ước lượng).
- ⇒ Biên tăng chủ yếu nhờ **hấp thụ chi phí cố định khi DQ2 lên công suất + mix HRC** — yếu tố cấu trúc, không phải spread.
- KH + lãi vay DQ2 **đã vào P&L**: KH Q3 3.063 vs ~1.863/quý 2025; lãi vay 1.774 vs 812. **Lãi vay vốn hoá 2025: 1.877 tỷ → 6T/26: 162 tỷ**
  [KT25 TM15; BN TM17] ⇒ Q3/26 không còn lợi nhuận "ẩn" nhờ vốn hoá.
- **Giá trị bảo hộ AD (ước lượng):** chênh 25–45 USD/t × ~7,3 tr t HRC/năm ≈ **4.700–8.500 tỷ/năm trước thuế** (tỷ giá ~26.000).
- CPBH/DTT 2,72% (Q3/25 2,19%), đi cùng XK tăng (26,4% DTT Q3 vs 12,6%).

### 3d. Tài chính, tỷ giá, thuế
- Lãi tiền gửi Q3 704,3 ⇒ ~6,8%/năm trên tiền + HTM; lãi vay ~6,7%/năm ⇒ carry gần trung tính. **~8.294 tỷ tiền gửi có kỳ hạn là tài sản
  thế chấp cho hạn mức tín dụng tại 30/6/2026** (31/12/25: ~6.809) [BN TM6a, tr. in 31 — tự đọc ảnh].
- Vay USD 3.575 (31/12/25) → 12.612 tỷ (30/6/26) [BN TM25a]. CLTG Q3 nhỏ.
- **Thuế (sửa v1):** ETR Q3/26 9,3%, 9T 12,2%, 2025 14,3%; **phân khúc thép 6T/26 chỉ 6,5%** (1.451,3/22.160,5) [BN seg]. Thời hạn ưu đãi:
  **BCTC không công bố** (KT25 TM37, BN TM39 chỉ ghi "hưởng ưu đãi theo GCN đầu tư"). CV 377/TCT-CS (01/2024) yêu cầu xác định DQ2 là dự án
  mới hay mở rộng — kết luận chưa tìm được. ⇒ Mô hình v2 giả định **ETR ~12% tới 2029, 20% từ terminal** (§7).

### 3e. LNST chuẩn hoá — sửa mâu thuẫn v1 (N2)
v1 vừa nói spread "đi ngang giữa chu kỳ" và biên tăng nhờ yếu tố cấu trúc (§3c), vừa gọi Q3 là "khoảng trên của chu kỳ" rồi cho cả 3 kịch bản
LN 2027→2029 đi xuống, ROE "tốt" 15% < ROE lõi TTM. v2 tách hai câu hỏi:
- **Q3 cao một phần do mùa vụ**, không phải đỉnh chu kỳ: Q3 lõi × 4 ≈ 30,9k, nhưng LNST lõi 2026E ≈ 4,9 + 6,3 + 7,7 + ~7,0 ≈ **26k** (ước lượng).
- **LN/tấn** (LNST/sản lượng bán, ước lượng): 2023 ~1,05 · 2024 ~1,46 · 2025 ~1,48 · 9T/26 lõi ~1,87 tr đ/t. 2026 cao hơn nhờ hấp thụ định phí.
- **Kịch bản trung lập** = KL ~15 tr t 2027 (hiệu suất 81% → ~90%) × LN/tấn trôi 1,87 → ~1,73 ⇒ **26k/năm 2027–2028, 27k 2029 — đi NGANG,
  không đi xuống**. Lực kéo xuống được NÓI RÕ: mở bán nhà ở gãy từ Q3/2026 với độ trễ sang thép XD ~H2/2027 [NGÀNH], VinMetal thành đối thủ HRC
  thứ hai sau 2027, rủi ro rà soát AD. Lực đỡ: khối lượng DQ2, XDCB 16,1k còn đưa vào vận hành.
- **ROE terminal không tự chọn nữa** mà suy ra nhất quán = LN 2029 × (1+g) × (0,80/0,88) / BV cuối 2029: xấu 7,9% · trung lập 11,8% · tốt 14,3%
  (sau thuế 20%). Tương đương ROE ở ETR 12%: ~8,7% / 13,0% / 15,7%.

## 4. Câu 2 — Bảng cân đối, dòng tiền [HN-Q3]

| 30/09/2026 vs 01/01/2026 | Số | Ghi chú |
|---|---|---|
| Tiền + TĐT | 6.852,9 / 8.325,1 | 01/01 "số điều chỉnh lại" (KT25 8.300,9) |
| Tiền gửi HTM ngắn + dài | 39.276,2 / 22.145,0 | **~8.294 trong đó bị cầm cố** (30/6) [BN TM6a] |
| Vay NH + DH | 78.615,0 + 27.121,7 = **105.736,7** / 92.174,2 | ~90% vay NH có bảo đảm (30/6) [BN TM25a] |
| Phải trả người bán dài hạn | 3.828,9 | nợ có tính chất vay (trả chậm thiết bị) |
| Nợ ròng (vay − tiền − toàn bộ HTM) | 59.607,6 / 61.704,1 | **cận dưới** — coi toàn bộ tiền gửi là tự do |
| EBITDA TTM | 49.170,7 báo cáo; **44.235 lõi** | |

**Nợ ròng / EBITDA lõi (B1, sửa v1 — bỏ chữ "thật"):**

| Cách tính | Nợ ròng | ×EBITDA lõi |
|---|---|---|
| Không trừ phần tiền gửi cầm cố 8.294 | 67.901,6 | **1,54x** |
| + phải trả người bán DH 3.829 | 71.730,5 | **1,62x** |
| Cận dưới — nếu coi toàn bộ tiền gửi là tự do | 59.607,6 | 1,35x |

Cả ba dưới ngưỡng cờ đỏ 3x của người đọc ngành ⇒ đòn bẩy **ổn**. Lưu ý số cầm cố là số 30/6 (BCTC Q3 không thuyết minh lại).
Vay/VCSH 0,71x. HTK 46.949,2 (~85 ngày GVHB), DP 72,5. PTKH 12.237,6 (~18 ngày). XDCB 16.113,3 (DQ 11.146,0). Cam kết vốn ~19.472 (30/6).
Đầu tư liên kết **12.664,1** (TLSH + BĐS HP, §6).

**Dòng tiền 9T/2026** [HN-Q3 tr.6–7]: CFO **20.936,3** = 1,09x LNST lõi — **nhưng có hai khoản một lần bù nhau (N10)**: hoàn VAT (VAT được
khấu trừ 7.429,9 → 2.294,2, **+5.135,7**, chủ yếu VAT capex DQ2) và phải trả người bán NH giảm −4.410,4. **CFO điều chỉnh:** bỏ hoàn VAT ⇒ 15.800,6
(**0,82x lõi**); bỏ cả hai ⇒ 20.211,0 (**1,05x**). Capex 14.607,2 ⇒ FCF ≈ 6.329 (báo cáo). Cổ tức tiền −3.937,4; thu thoái vốn +9.800,8;
**chi góp vốn vào đơn vị khác −4.892,9**; gửi HTM ròng −24.790,5. 2025 CFO 17.365,9 vs LNST 15.514,9; 2024 6.608,3 vs 12.020,0.

**Cổ tức (sửa #7, đã đọc lại ảnh [BN TM28 tr. in 47]):** cả hai nguồn đều đúng — hai câu khác nhau:
(i) cổ tức **năm 2025** = 10% bằng CP (hoàn tất 26/05/2026) + 5% tiền (3.837,7 tỷ cho CĐ mẹ ≈ 500 đ/cp), tổng 15%;
(ii) NQ 01/NQ-ĐHĐCĐ.2026 (21/04/2026): **"tỷ lệ trả cổ tức dự kiến năm 2026 là 15%"** — hình thức chưa công bố.
EPS TTM sau thưởng: 3.251 báo cáo / ~2.630 lõi sau trích quỹ. BVPS 17.624 đ.

## 5. Câu 3 — Ngành → doanh nghiệp

- **Xuất khẩu theo khu vực 6T/2026** [BN tr.53]: VN 79,1%, Á 12,3%, Âu 3,6%, Mỹ 4,0%, Úc 1,0% ⇒ EU+Mỹ+Úc 8,5% DTT < ngưỡng 30%.
- **Mỹ (sửa #4):** AD thép cây HPG **cuối 128,53%** (cash deposit 123,49%; sơ bộ 121,97%) + **CVD 6,80%**; order ~18/09/2026 [Federal Register, GAPS §5].
  Mỹ ~4% DTT gồm cả SP khác ⇒ tác động nhỏ (ước lượng < 2% DTT). Không thấy dự phòng/ký quỹ PVTM trong BCTC.
- **EU (sửa #5):** AD HRC EU với HPG **0%** (DN VN khác 12,1%) [báo]; safeguard vĩnh viễn từ 01/07/2026. **CBAM:** HPG đã kiểm kê phát thải
  hàng XK EU với TÜV (BCTN 2025), **không công bố tCO₂/t**; phơi nhiễm EU 3,6% DTT ⇒ nhỏ.
- **AD HRC nội (sửa #3):** **QĐ 1959/QĐ-BCT (04/07/2025)**, 23,10–27,83%, hiệu lực 06/07/2025 → ~07/2030 (ước lượng 5 năm). Chống lẩn tránh
  tạm thời QĐ 612/QĐ-BCT (02/04/2026). **Rà soát hành chính lần 1 QĐ 1902/QĐ-BCT (27/07/2026) — rủi ro gần, nằm trong cửa sổ H4.**
  Mất AD ≈ 4.700–8.500 tỷ LNTT/năm (ước lượng) ≈ 15–25% LNTT lõi.
- **Thị phần thép XD:** HPG tự công bố 36% (Q1, H1/2026); VSA 9T 35% [NGÀNH]; tính chéo ≥ 34,4% (ước lượng). HPG XD +15% vs ngành +19,6%,
  miền Nam ngành +29,9% ⇒ mất thị phần nhẹ nơi tăng nhanh nhất. HRC 2025: ~60% thị phần.
- **Công suất (sửa #6):** thép thô 16 tr t, HRC 9 tr t ⇒ hiệu suất HRC ~81%. VinMetal (P 0,35 [NGÀNH]) là đối thủ HRC thứ hai sau 2027.

## 6. Câu 4 — Quản trị & pháp lý — ⚠️ WARNING

- **Kiểm toán:** KT25 Deloitte VN, chấp nhận toàn phần; soát xét 6T/2026 Deloitte, chấp nhận toàn phần. ⚠️ BCTC 2024 do **một công ty kiểm toán
  khác** kiểm toán ⇒ đổi KTV từ năm 2025. Tên KTV 2024: trang tổng hợp 24hmoney ghi **KPMG Việt Nam** [WEB] — **chưa đọc báo cáo kiểm toán gốc
  2024**, lý do đổi chưa xác nhận (tờ trình ĐHĐCĐ 2025 không nêu tên).
- ⚠️ **TLSH (Tập đoàn Tương lai Sông Hồng)** — giao dịch quản trị lớn nhất năm (sửa #10, N5–N7):
  - **9.915 tỷ = 1.920 tỷ TIỀN** (15% TLSH, H1, khi vốn TLSH 12.800) [BN TM6b] **+ 7.995 tỷ bằng cổ phần CTCP PT BĐS Hòa Phát** (Q3) ⇒ 25,13% TLSH.
  - **32.000 đ/cp và ~10.271 đ/cp là HAI PHƯƠNG ÁN**, không phải hai nguồn báo sai: NQ 10/NQHP-2026 (22/07): 32.000 đ/cp, ~250 tr cp, HPG giữ 76,41%;
    NQ 13/NQHP-2026 (30/09): góp **778.405.218 cp** cho cùng 7.995 tỷ, giữ 26,55% [CBTT]. HPG giao lượng BĐS HP gấp ~3,1 lần cho cùng số cổ phần
    TLSH; lý do và tổ chức thẩm định giá **không công bố**.
  - **Tự kiểm từ ảnh [ME-Q3] (mới v2):** BCTC riêng công ty mẹ: đầu tư BĐS HP **10.598,0 tỷ giá gốc** (01/01, = 1.059,8 tr cp × mệnh giá) → 0 ở mục
    công ty con; mục liên kết 30/9 = **TLSH 9.915,0 + BĐS HP 2.813,9 = 12.728,9** (2.813,9 = 281.394.782 cp × 10.000 đ) [ME-Q3 tr. in 13].
    **Thu nhập khác Q3 công ty mẹ có dòng "thu nhập khác" 210.947.820.000 đ** [ME-Q3 tr. in 23] = **đúng bằng 7.995,0 − 7.784,05 (778.405.218 cp ×
    10.000 đ)** ⇒ hoán đổi ghi theo giá thoả thuận 7.995 (~10.271 đ/cp), giá gốc theo mệnh giá, **chênh ~211 tỷ ghi vào thu nhập khác của công ty mẹ**
    (suy luận từ khớp số tuyệt đối; BCTC riêng không thuyết minh dòng này). Người phản biện viết "không có lãi hoán đổi" — đúng ở DTTC, nhưng khoản
    chênh nằm ở thu nhập khác. Ở hợp nhất, phần lãi/lỗ rời hợp nhất tính trên tài sản thuần BĐS HP, khác số công ty mẹ — **Q3 hợp nhất không thuyết
    minh**; LN khác thuần Q3 hợp nhất 286,6 đã bóc khỏi lõi (§3b).
    Hệ quả: HPG đổi ~73% một công ty con BĐS đang kiểm soát lấy cổ phần thiểu số của một DN < 1 năm tuổi, ở giá **xấp xỉ mệnh giá**. Nếu tài sản BĐS
    có giá trị thị trường > sổ sách, phần chênh đi sang TLSH — đây là câu hỏi quản trị cốt lõi.
  - **Bên liên quan (N7):** TLSH là công ty liên kết (HPG có đại diện HĐQT, ảnh hưởng đáng kể [BN TM6b]) ⇒ **theo VAS 26 là bên liên quan và giao dịch
    hoán đổi là giao dịch bên liên quan; BCTC (HN-Q3, BN TM42, KT25 TM40) KHÔNG thuyết minh giao dịch này như giao dịch bên liên quan** — chỉ thuyết
    minh thù lao. CBTT gốc không dùng chữ "bên liên quan"; chỉ HĐQT thông qua, không có NQ ĐHĐCĐ. Ngưỡng ĐHĐCĐ theo Điều lệ/LDN: chưa kiểm (cần tư vấn pháp lý).
  - **Truy dòng vốn (N6):**
    (a) LCTT hợp nhất 9T "chi góp vốn vào đơn vị khác" 4.892,9 (H1 3.634,7): xác định được TLSH 1.920. **Còn ~2.973 CHƯA TÌM ĐƯỢC** đích đến. Đã thử:
    BCTC riêng mẹ (chi góp vốn 9T 9.120,0 ≈ +7.150 vào Gang thép HP + 1.920 TLSH + ~50, đều nội bộ trừ TLSH ⇒ khoản 2.973 do công ty con chi);
    danh sách liên kết 30/9 (chỉ TLSH + BĐS HP); Điện gió Sông Hậu 600 không có trong danh sách liên kết; HN-Q3 không có thuyết minh đầu tư khác.
    (b) Phải thu dài hạn khác hợp nhất mới **600,0** (HTKD 100; ký quỹ 499,9) [HN-Q3 VI.4]; công ty mẹ **495,8 = đặt cọc/ký quỹ 361,2 + phải thu
    hợp đồng BCC đồng kiểm soát 134,6** [ME-Q3 VI.4 tr. in 14] — **đối tác không thuyết minh**, chưa tìm được.
    (c) Phải thu dài hạn **1.600 tỷ** "tiền chuyển cho đối tác theo thoả thuận liên danh 02/2026/TTLD (08/05/2026)" — Dự án Đại lộ cảnh quan sông Hồng
    (BT) [BN TM9(ii)] → còn **100 tỷ** tại 30/9 [HN-Q3 VI.4]: **1.500 tỷ không có thuyết minh** (hoàn trả / chuyển vào TLSH-BĐS HP rời hợp nhất / phân
    loại lại — chưa kiểm được) ⇒ mốc **H9**.
  - TLSH: thành lập 14/11/2025, vốn 1.500 → 39.450 tỷ trong < 1 năm; sáng lập Trần Đăng Khoa 40% [báo]; ai góp 18.655 tỷ còn lại: chưa tìm được.
    Không thấy quan hệ sở hữu với nhóm cổ đông lớn HPG ("không tìm thấy", không phải "đã xác minh"). Dự án KĐT Thư Lâm–Đông Anh 696 ha.
  - Đuôi trái: mất 50% khoản TLSH ≈ **−587 đ/cp** (ước lượng) — không đổi tâm, là rủi ro đuôi.
- ⚠️ **Cầm cố:** vay ngân hàng được bảo đảm một phần bằng **"cổ phiếu HPG do các cá nhân sở hữu"** [KT25 tr.37; BN TM25a] — số lượng không công bố;
  ~8.294 tỷ tiền gửi cầm cố (§4).
- **Cổ đông:** nhóm ông Trần Đình Long ~35,46%. Trần Vũ Minh đăng ký mua 50 tr cp 07/10–05/11/2026 (đợt trước đăng ký 50, mua 33,3 tr) [CBTT/báo].
- **Thù lao HĐQT (sửa #11):** 2024 **244,7** · 2025 **83,2** · 6T/26 **207,7** tỷ [KT25 TM40; BN TM42] + 180 tỷ trích từ LNCPP 9T — biến động theo
  lợi nhuận, 2024 còn cao hơn ⇒ không phải bất thường mới.
- **Sở hữu nhà nước:** không. **Kiện tụng/khởi tố, xử phạt 2025–2026:** không tìm thấy ("không tìm thấy" ≠ "sạch"). Cờ thuế mềm: nếu DQ2 bị xếp
  "mở rộng" có rủi ro truy thu ưu đãi (CV 377/TCT-CS).

## 7. Câu 5 — Định giá (giá 21.000 đ, đóng cửa 30/10/2026 [BQ])

**Thị trường:** vốn hoá **177.302 tỷ**; EV (vốn hoá + nợ ròng 59.608 + phải trả NB DH 3.829 + CĐKS 773 − liên kết 12.664) ≈ **228.848 tỷ**.

| Bội số | Hiện tại | Lịch sử [BQ] |
|---|---|---|
| P/E TTM báo cáo | 6,46x | trung vị năm (mọi ngày): 2018 9,7 · 2019 7,9 · 2020 9,3 · 2021 10,8 · 2022 4,7 · **2023 14,5** · 2024 19,2 · 2025 14,3 |
| P/E TTM lõi (EPS ~2.630 sau trích quỹ) | **~8,0x** | BQ PE dùng EPS trễ ⇒ méo ở đáy/đỉnh chu kỳ |
| P/E 2027 trung lập (26k) | 6,8x | — |
| P/B | 1,19x | đáy năm: 2020 0,94 · 2022 0,72 · **2023 1,14** · 2024 1,46 · **2025 1,19** · 2026 1,185 (= phiên 30/10) |
| EV/EBITDA lõi TTM | **5,2x** (4,7x trên EBITDA 2027 trung lập) | — |

v1 ghi P/E 2023 "82,8" = trung vị chỉ các ngày PE > 0 — sai cách tính; trung vị cả năm **14,5** (N8).
**P/B (B2, sửa v1):** 1,19x là đáy của năm 2026 và **ngang đáy 2025 (1,19)**, **trên đáy 2023 (1,14)** — KHÔNG phải "thấp nhất kể từ 2022".
Giá điều chỉnh từ đỉnh **26.240 (26/02/2026)** xuống 21.000: **−20,0%**, trong khi VNINDEX −7,3% (1.879,6 → 1.741,6) và LN lõi tăng [BQ, kiểm lại 31/10].

**Comp có số (sửa #13, N4)** [BQ 30/10; khu vực: stockanalysis.com, tin cậy trung bình — GAPS §6]:

| | P/E | P/B | EV/EBITDA | ROE |
|---|---|---|---|---|
| HPG | 6,5 báo cáo / ~8,0 lõi | 1,19 | 5,2 lõi | ~16–17% lõi (19,5% báo cáo) |
| Trung vị thép VN (n=9; HSG/NKG chỉ tham chiếu) | 13,35 | 0,67 | 11,1 | 8,0% |
| Trung vị khu vực (8 hãng) | 13,5 | 0,57 | 7,8 | 4,1% |

HPG rẻ hơn ~40% trên P/E và 35–54% trên EV/EBITDA, nhưng đắt gấp ~2 lần trên P/B. Cách đọc: peers đang ở **đáy** chu kỳ (ROE 4–8%) nên bội số
trên lợi nhuận của họ bị thổi lên; HPG đang ở ROE cao nhờ AD + DQ2. Chiết khấu P/E ~40% tương đương kỳ vọng ROE HPG trôi về ~11–12% — khớp
mức ROE terminal mà giá hiện tại ngầm định (12,4%).

**Chi phí vốn (sửa #1, N1):** β đo (HPG vs VNINDEX, tuần, Close điều chỉnh) 2 năm **0,84** / 3 năm **0,89**; Blume **0,90–0,93** [BQ, `gaps_beta_out.txt`].
rf 6,75%, ERP nội địa 5,0–6,1% ⇒ **Ke 11,2–12,4%** (dải đầy đủ theo β 0,84–0,93: 10,97–12,42%); **tâm Ke 11,83%** (β 0,915 × ERP 5,55%).
**Đi cùng: thuế terminal 20%** (GAPS §2 + §7): chỉ hạ β mà giữ ETR ~12% vĩnh viễn thổi giá trị +2.911 đ/cp (`hpg_valuation_v2_out.txt`).

**RI 3 kịch bản** (BV0 VCSH mẹ 148.795,5; payout tiền 20%; g 5% (xấu 3%); LN ở ETR ~12% tới 2029; ROE terminal suy ra nhất quán sau thuế 20%; tất cả LN (ước lượng)):

| Kịch bản (trọng số) | LNST mẹ Q4/26 · 2027 · 2028 · 2029 | ROE terminal sau thuế 20% | Điều kiện | Ke 11,23% | **Ke 11,83%** | Ke 12,42% |
|---|---|---|---|---|---|---|
| Xấu (0,25) | 5,5k · 16k · 15k · 16k | 7,9% (g 3%) | AD cắt sau rà soát, spread 150–200; ~1,1 tr đ/t (mức 2022–23) | 10.415 | **9.612** | 8.923 |
| Trung lập (0,50) | 7,0k · 26k · 26k · 27k | 11,8% | KL 15 tr t, LN/tấn 1,87 → 1,73; nhà ở gãy, VinMetal | 21.653 | **19.563** | 17.838 |
| Tốt (0,25) | 8,0k · 31k · 33k · 35k | 14,3% | LN/tấn ~2,0 với 15,5–16 tr t; AD mở rộng ASEAN | 31.187 | **28.147** | 25.640 |
| **Trọng số** | | | | **21.227** | **19.221** | **17.560** |

(Ke 11,23% = β 0,90 × ERP 5,0%; 12,42% = β 0,93 × ERP 6,1%.)
- **Vì sao trọng số giữ 0,25/0,50/0,25:** rủi ro xuống gần (rà soát AD QĐ 1902, nhà ở gãy H2/2027) và rủi ro lên (DQ2 còn ~10 pp hiệu suất, XDCB 16,1k)
  có cỡ tương đương; v1 lệch xuống vì ba đường LN đều đi xuống, v2 sửa bằng đường trung lập đi ngang. Độ nhạy trọng số: 0,30/0,50/0,20 ⇒ 18.294;
  0,20/0,50/0,30 ⇒ 20.148.
- **Độ nhạy ROE terminal × Ke (trung lập):** ROE 11% → 17.347; 12% → 19.971; 13% → 22.596; 14% → 25.220 (Ke 11,83%). Biến nhạy nhất vẫn là ROE dài hạn.
- **Kiểm RONIC ≥ Ke:** trung lập 11,8% ≈ Ke 11,83% ⇒ tăng trưởng trung tính giá trị; giữ g 5%, không nâng.
- **Đối chiếu:** β 1,1 cũ (Ke 12,85%) + thuế 20% ⇒ 16.484.

**Cross-check EV/EBITDA — neo bằng comp, nói rõ chiều lệch (N3):** EBITDA 2027 theo kịch bản = LN/0,88 + lãi vay ~7,1k + KH ~12,3k (Q3/26 × 4):
xấu 37,6k / trung lập 48,9k / tốt 54,6k (ước lượng).

| Bội số | Neo | Trọng số (đ/cp) |
|---|---|---|
| 5x | ≈ bội số thị trường đang trả HPG (5,2x TTM lõi) | **22.025** |
| 6x | điểm giữa, không có neo riêng | 27.651 |
| 7x | ≈ trung vị khu vực 7,8x — nhưng tính trên EBITDA ĐÁY chu kỳ của peers | 33.277 |

Chiều lệch: comp (VN 11,1x, khu vực 7,8x) đo trên EBITDA đáy ⇒ áp lên EBITDA gần đỉnh của HPG sẽ **thổi giá trị lên**; bội số EV/EBITDA cũng bỏ qua
bước nhảy thuế 20% và ROE trôi. ⇒ chỉ dùng **5x** làm cross-check; 6–7x chỉ để thấy độ nhạy (~5,6k/cp mỗi 1x).

**Tổng hợp (tự tính lại độc lập):** tâm = (2 × RI 19.221 + EV/EBITDA 5x 22.025) / 3 = **20.156 đ** (RI là neo chính vì đã gồm ROE trôi + thuế terminal).
Cận dưới (Ke 12,42% + EBITDA −10%) **18.110**; cận trên (Ke 10,97% + 5x) **22.157** ⇒ **vùng hợp lý 18.000–22.500, tâm ~20.200 đ (ước lượng)**.
Giá 21.000 = **+4,2%** so với tâm ⇒ trong vùng, nửa trên. So với người phản biện (tâm ghép nhất quán 18,5–20,5k): tâm v2 **nằm trong** dải đó, nhưng
ra bằng đường khác — RI v2 đã sửa đồng thời β, thuế terminal và đường LN đi ngang; EV/EBITDA chỉ ở 5x thay vì 6x. Hai thiên lệch v1 (β thận trọng kéo
xuống, 6x hào phóng kéo lên) nay được thay bằng tham số có neo, không còn bù trừ ngầm.

**Phản ứng giá quanh BCTC** [BQ]: Q3/26 (29/10) +2,2% (VNI −0,6%), GTGD 772 tỷ ≈ 2× bình quân; 30/10 −0,9% ⇒ phản ứng nhạt với lợi nhuận gấp đôi.

## 8. Câu 6 — Thanh khoản / sở hữu nước ngoài (sửa #12)
GTGD bình quân 3 tháng **410 tỷ/phiên** (trung vị 370); 10/2026 393–401 tỷ tuỳ cách tính; 02/2026 1.523 ⇒ **−74%** so với đỉnh 02/2026 [BQ].
Sở hữu nước ngoài 30/10/2026 **21,8%**, room còn **27,2%** KLCP (trần 49%) [WEB 24hmoney] ⇒ NN giảm nhẹ ~0,8 pp so với 04/2026. VanEck VNM: 5,01% NAV.

## 9. Mốc khoá trước có ngày chấm — HAI CHIỀU (lập 31/10/2026; P = ước lượng; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm)

| # | Mệnh đề (đo) | P(trong khoảng giữa hoặc tốt hơn) | Ngày chấm | ↑ nếu | ↓ nếu |
|---|---|---|---|---|---|
| H1 | Biên gộp Q4/26 so **cùng kỳ** Q4/25 13,85% | 0,75 | 2027-02-05 | ≥ 18,0% | < 13,85% |
| H2 | LNST lõi Q4/26 (bỏ thoái vốn/LN khác bất thường) | 0,70 | 2027-02-05 | ≥ 8.000 | < 5.500 |
| H3 | CFO 12T/2026 **trừ hoàn VAT một lần** / LNST lõi | 0,65 | 2027-02-05 | ≥ 1,0x | < 0,7x |
| H4 | Mức AD HRC TQ áp cho nhà sản xuất chính sau rà soát hành chính QĐ 1902 (đang 23,10–27,83%) | 0,85 | 2027-03-31 | giữ ≥ 23,1% **và** QĐ chính thức chống lẩn tránh | < 20% hoặc huỷ |
| H5 | Biên gộp Q1/27 so **cùng kỳ** Q1/26 15,81% | 0,70 | 2027-05-05 | ≥ 17,5% | < 14,0% |
| H6 | Thị phần thép XD HPG cả năm 2026 (VSA hoặc HPG công bố) | 0,65 | 2027-02-15 | ≥ 36% | < 33% |
| H7 | BCTC kiểm toán 2026: chấp nhận toàn phần, không cam kết/bảo lãnh/góp thêm TLSH ≥ 2.000 tỷ | 0,75 | 2027-04-15 | thêm: thuyết minh TLSH như giao dịch bên liên quan + công bố thẩm định giá | ý kiến ngoại trừ/nhấn mạnh **hoặc** góp/bảo lãnh ≥ 2.000 |
| H8 | ĐHĐCĐ 2027: kế hoạch LNST 2027 | 0,60 | 2027-05-31 | ≥ 28.000 | < 22.000 |
| H9 | BCTC kiểm toán 2026 thuyết minh số phận 1.500 tỷ ứng liên danh Đại lộ sông Hồng và ~2.973 góp vốn chưa rõ đích | 0,60 | 2027-04-15 | hoàn trả / đích minh bạch ngoài hệ TLSH | chuyển thành góp vốn/BT vào hệ TLSH không thuyết minh |

**Quy tắc đổi nhận định (đối xứng, không dùng trigger một quý):**
- **LÊN** khi ≥ 2 trong {H1↑, H2↑, H5↑} **và** H4 không ↓ ⇒ trọng số 0,15/0,50/0,35 + đường trung lập 8,0k · 28k · 28k · 29k ⇒ **~22.100** (chỉ đổi
  trọng số: 21.075). H7↑ + H9↑ bỏ chiết khấu đuôi TLSH (~+590 đ/cp).
- **XUỐNG** khi biên gộp **2 quý liên tiếp thấp hơn cùng kỳ** (H1↓ và H5↓) **hoặc** H4↓ ⇒ trọng số 0,35/0,50/0,15 + đường trung lập 5,5k · 23k · 23k · 24k
  ⇒ **~15.800** (chỉ đổi trọng số: 17.368). H7↓ hoặc H9↓ ⇒ thêm đuôi TLSH (~−590 đ/cp) và nâng WARNING quản trị.
- Một quý lệch đơn lẻ (vd. biên Q4 yếu theo mùa) **không** tự kích hoạt.

## 10. Checklist ngành §7 (21 mục) bằng số HPG

| # | Kết quả |
|---|---|
| 1 cơ cấu SP/thị trường | Theo SP: không có trong BCTC. EU+Mỹ+Úc 8,5% DTT H1 < 30% ✓ |
| 2 sản lượng/thị phần | 8 quý từ thông cáo gốc (GAPS §4); thị phần XD 35–36% ⚠️ nhích xuống |
| 3 công suất vs sản lượng | Thép thô 16 tr t (~89%), HRC 9 tr t (~81%) (ước lượng) |
| 4 mô hình chuỗi | Tích hợp BOF; tự chủ quặng/than: chưa kiểm được |
| 5 biên gộp 7 quý | 13,85–19,16%; biên tăng khi spread phẳng ⇒ nhờ KL/mix |
| 6 giá vốn/tấn | GVHB Q3 ≈ 13,2 tr đ/t (thô) |
| 7 tồn kho/DP | 46.949 (~85 ngày), DP 72,5 |
| 8 CPBH/DT, lãi vay/EBIT | 2,72%; 16% |
| 9 nợ/VCSH, ND/EBITDA, vay ngoại tệ | 0,71x; **1,54x (không trừ tiền gửi cầm cố) / 1,62x (+ phải trả NB DH)**, cận dưới 1,35x; vay USD 12.612 |
| 10 CFO vs LNST | 9T 1,09x lõi báo cáo; **0,82x bỏ hoàn VAT; 1,05x bỏ cả hoàn VAT và giảm phải trả NB**; 2025 1,12x; 2024 0,55x |
| 11 capex/XDCB/vốn hoá lãi vay | Capex 9T 14.607; XDCB 16.113; cam kết ~19.472; **vốn hoá lãi vay 2025 1.877 → 6T/26 162** |
| 12 phải thu, trả trước | PTKH ~18 ngày; ⚠️ phải thu DH mới 600 (ký quỹ 499,9) đối tác không thuyết minh; 1.600 → 100 liên danh |
| 13 LC/bảo lãnh/HĐ dài hạn | Cam kết vốn dự án; LC/bảo lãnh/covenant: không thuyết minh |
| 14 PVTM bị đơn | Mỹ AD thép cây 128,53% + CVD 6,80%; không thấy dự phòng/ký quỹ |
| 15 hưởng AD nội | QĐ 1959/QĐ-BCT; giá trị ~4.700–8.500 tỷ LNTT/năm (ước lượng); rà soát QĐ 1902 |
| 16 CO₂/CBAM | Đã kiểm kê (TÜV); tCO₂/t không công bố |
| 17 ưu đãi thuế | ETR thép 6T/26 6,5%; thời hạn **BCTC không công bố**; DQ2 mới/mở rộng chưa có kết luận |
| 18 bên liên quan | ⚠️ TLSH là bên liên quan (VAS 26), BCTC không thuyết minh giao dịch; cổ phiếu cá nhân bảo đảm vay |
| 19 ngoài ngành | ⚠️ 12.664 liên kết BĐS, ≤ 1.600 ứng BT, điện gió 600, nông nghiệp |
| 20 pha loãng | Cổ tức CP 10% (2025); KH cổ tức 2026 15% (hình thức chưa công bố); không ESOP/riêng lẻ |
| 21 kiểm toán | Chấp nhận toàn phần; ⚠️ đổi KTV từ 2025 (2024: KPMG theo trang tổng hợp, chưa đọc gốc) |

## 11. Lệch nguồn BQ vs BCTC
- [BQ] PE 30/10 = 6,46 khớp EPS TTM báo cáo 3.251 ⇒ gồm lãi thoái vốn. PB 1,185 ✓. `EVEB` rỗng 29–30/10.
- Không dùng `ticker_financial` cho tiền/HTM (Cash_P0 thiếu HTM).

## Giới hạn
- BCTC Q3 không thuyết minh vay chi tiết, bên liên quan, thuế ưu đãi, thu nhập khác hợp nhất — lấy từ [BN] 30/6 hoặc ghi "chưa kiểm được".
- Chưa tìm được: đích ~2.973 tỷ góp vốn; đối tác ký quỹ 499,9 và BCC 134,6; số phận 1.500 tỷ ứng liên danh; lý do hạ giá ×3 và tổ chức thẩm định BĐS HP;
  ai góp 18.655 tỷ vào TLSH; số CP HPG cá nhân cầm cố; covenant; tên KTV 2024 từ bản gốc.
- Sản lượng theo SP, thị phần, AD/PVTM: thông cáo gốc + Federal Register + báo (GAPS); peer khu vực từ một aggregator (tin cậy trung bình).
- Đường LN 2027–2029, LN/tấn, EBITDA 2027, ERP: (ước lượng). Thị trường đóng cửa — giá dùng đóng cửa 30/10/2026, không cần giá khớp trong phiên.

## Nguồn web (truy cập 31/10/2026)
- v1: thoibaotaichinhvietnam.vn, doanhnhan.baophapluat.vn, baodauthau.vn (sản lượng 9T); vietnamfinance.vn 24/07; mekongasean.vn 01/10 & 02/10;
  nhadautu.vn (AD Mỹ sơ bộ); ACBS Flashnote 24/04/2026 — link đầy đủ ở `REPORT_v1.md`.
- v2 vòng đào: `src/gaps/web_output_ad_peers.md`, `src/gaps/web_tlsh_governance.md` (URL từng mục).
- KTV 2024: https://24hmoney.vn/stock/hpg (trang tổng hợp; chưa đối chiếu báo cáo kiểm toán gốc).

## Ghi chú cho Mike
- File người đọc ngành `kb/data_registry/market-state/sector_read_thep_20261031.md` (F8) ghi "QĐ 1917" — **đúng là QĐ 1959/QĐ-BCT (04/07/2025)**; thêm
  rà soát QĐ 1902 (27/07/2026) và chống lẩn tránh tạm thời QĐ 612 (02/04/2026). Cần đính chính (Mike làm; Taylor không sửa file đó).

## Thay đổi so với v1

| # | Mục | v1 | v2 | Nguồn đính chính |
|---|---|---|---|---|
| 1 | §4 nợ ròng/EBITDA | "nợ ròng thật", 1,35x | 1,54x không trừ tiền gửi cầm cố 8.294; 1,62x + phải trả NB DH; 1,35x chỉ là cận dưới; bỏ chữ "thật" | B1, ảnh BN TM6a |
| 2 | §7 P/B, đỉnh giá | "thấp nhất kể từ 2022"; đỉnh 25.710, −18% | ngang đáy 2025 (1,19), trên đáy 2023 (1,14); đỉnh 26.240 (26/02), −20,0% | B2, BQ kiểm lại |
| 3 | §7 β/Ke | β ~1,1 chưa đo, Ke 12,3–13,4% | β 0,84–0,89, Blume 0,90–0,93, Ke 11,2–12,4% **đi cùng thuế terminal 20%** | N1, GAPS #1 |
| 4 | §3e/§7 kịch bản | 3 đường LN đều đi xuống; ROE terminal tự chọn 10/12,5/15% | trung lập đi ngang 26–27k (giải thích lực kéo xuống); ROE terminal suy ra nhất quán 7,9/11,8/14,3% sau thuế 20% | N2 |
| 5 | §7 EV/EBITDA | 6x không neo, kéo tâm lên | comp có số; chỉ dùng 5x (≈ thị trường), nói rõ chiều lệch của 6–7x | N3, N4, GAPS #13 |
| 6 | §1/§7 vùng | 17–23k, tâm ~20k | **18,0–22,5k, tâm ~20,2k**; giá +4% trên tâm, nửa trên vùng | tự tính `hpg_valuation_v2.py` |
| 7 | §3b lõi | lõi Q3 7.974 (+99%); EPS 2.717; P/E 7,7x; Q1 ~5,2k | Q3 lõi 7,7–8,0k (+116–120% lõi/lõi); LN khác 286,6 bóc; EPS ~2.630, P/E ~8,0x; Q1 ~4,9k; 9T 19,2k ± 0,4k | N8, N9, N12, GAPS #8–9 |
| 8 | §4 CFO | 1,09x ✓ | thêm CFO điều chỉnh 0,82x (bỏ hoàn VAT 5,1k) / 1,05x (bỏ cả giảm phải trả NB) | N10 |
| 9 | §4 cổ tức | "KH 2026 = 15%" | cả hai đúng: cổ tức 2025 = 10% CP + 5% tiền; KH 2026 dự kiến 15% (đọc lại ảnh BN TM28) | GAPS #7 |
| 10 | §6 TLSH | 32.000 vs 10.270 "chưa thống nhất"; "không thấy công bố là bên liên quan" | hai phương án NQ 10 vs NQ 13; 1.920 tiền + 7.995 CP; ghi theo ~mệnh giá, chênh ~211 tỷ ở thu nhập khác công ty mẹ (tự kiểm ảnh ME-Q3); là bên liên quan theo VAS 26 nhưng không thuyết minh; truy 2.973 / 499,9 / 1.500 (chưa tìm được đích) | N5–N7, GAPS #10 |
| 11 | §9 mốc | 7/8 mốc một chiều; trigger "biên 1 quý < 15%" | 9 mốc hai chiều, so cùng kỳ, quy tắc ≥ 2 mốc; thêm H9 | N11 |
| 12 | §5 AD/PVTM | QĐ (theo F8) 1917; Mỹ 121,97% | QĐ 1959/QĐ-BCT; rà soát QĐ 1902 trong cửa sổ H4; Mỹ cuối 128,53% + CVD 6,80%; EU 0%; CBAM | GAPS #3–5 |
| 13 | §3d thuế | "thời hạn chưa kiểm được" | BCTC không công bố; ETR thép 6,5%; mô hình giả định terminal 20% | GAPS #2, N12 |
| 14 | §3c/§5 công suất | 14–15 tr t; HRC 85% | thép thô 16, HRC 9 tr t; HRC ~81% | GAPS #6 |
| 15 | §3c, §10 | vốn hoá lãi vay chưa kiểm | 2025 1.877 → 6T/26 162 | GAPS #14 |
| 16 | §6 | thù lao "tăng mạnh"; KTV 2024 chưa đọc | bối cảnh 2024 244,7 / 2025 83,2; KTV 2024 KPMG theo trang tổng hợp (chưa gốc) | GAPS #11 |
| 17 | §8 | room 26,4%, NN ~22,6% | room 27,2%, NN 21,8%; ADV 3T 410 tỷ, −74% vs 02/2026 | GAPS #12 |
| 18 | §7 P/E 2023 | 82,8 | 14,5 (trung vị cả năm) | N8 |
