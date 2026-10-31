# DD — HPG (CTCP Tập đoàn Hòa Phát) · as-of 31/10/2026 · job `Taylor_20261031_093839`

> NGHIÊN CỨU READ-ONLY, trung dung. Không phải khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON (§2.5 là hồ sơ riêng, chỉ khi user xét
> mua discretionary). Pháp lý/quản trị ⇒ phân tích bình thường + WARNING (luật 27/09).
>
> **Nguồn** (mọi số BCTC đọc từ ẢNH trang render pymupdf zoom 1,4–1,6; KHÔNG dùng `.txt` OCR):
> **[HN-Q3]** BCTC hợp nhất Q3/2026 (ký 29/10/2026, `src/bctc_hopnhat_q3_2026.pdf`, tr. 2–8, 10, 16–36) ·
> **[BN]** BCTC hợp nhất giữa niên độ 6T/2026 **đã soát xét** (Deloitte VN, 28/08/2026, `src/bctc_hopnhat_soatxet_6t2026.pdf` tr. 8, 12, 15–21, 47–63) ·
> **[HN-Q1]** BCTC hợp nhất Q1/2026 (tr. 6) · **[KT25]** BCTC hợp nhất 2025 **đã kiểm toán** (Deloitte VN, 24/03/2026, tr. 6, 10–12) ·
> **[BQ]** `tav2_bq.ticker` (giá/khối lượng/PE/PB tới phiên **30/10/2026**) · **[BOBBY]** `kb/data_registry/market-state/sector_read_thep_20261031.md` (đọc mù) ·
> **[WEB]** báo chí/CBTT qua báo (link cuối file) — chỉ dùng cho dữ kiện ngoài BCTC, gắn nhãn.
> Số tự tính: `calc/hpg_calc.py` → `calc/hpg_calc_out.txt`; định giá `calc/hpg_valuation.py` → `calc/hpg_valuation_out.txt`;
> sổ đọc số từ ảnh: `calc/notes_bs.md`. Giả định tự đặt gắn **(ước lượng)**. Đơn vị: tỷ đồng nếu không ghi khác.
> Không đọc slide `tongquan_q3_2026.pdf` (scan) làm nguồn — chỉ đối chiếu số Mike đã đọc từ nó.

## 1. Kết luận (1 dòng + vùng giá)

**Lợi nhuận "gấp đôi" là NỬA ĐÚNG: Q3/2026 gấp đôi THẬT ở cấp vận hành (LNST lõi ~7.970 tỷ vs 4.012), nhưng 9T "+104%" bị thổi bởi
lãi thoái vốn BĐS một lần ~4.930 tỷ trước thuế; LNST lõi 9T ≈ 19.240 tỷ (+65%). Ở 21.000 đ (30/10), HPG giao dịch P/E TTM 6,5x
(báo cáo) / ~7,7x (lõi) / P/B 1,19x — giá đã phản ánh kịch bản cơ sở "lợi nhuận đỉnh rồi trôi về giữa chu kỳ". Vùng hợp lý
17.000–23.000 đ, trung tâm ~20.000 đ (ước lượng) ⇒ xấp xỉ hợp lý, không rẻ như P/E 6,5x gợi ý, cũng không đắt.**

| Vùng giá (đ/cp, trên 8.442,96 tr cp) | Đọc |
|---|---|
| < ~17.000 | dưới giá trị trung tâm >15% — chỉ hợp lý nếu kịch bản xấu (AD bị gỡ / spread 150–200) đang thành hiện thực |
| 17.000 – 23.000 (hiện 21.000) | xấp xỉ hợp lý quanh trung tâm ~20.000 (ước lượng) |
| > ~23.000 | đòi hỏi ROE lõi dài hạn ≥ 15% với Ke 13% — cần bằng chứng ở §9 (biên giữ ≥ 18% qua Q4/26–Q1/27, AD giữ) |

Giá hiện tại ngầm định ROE dài hạn ≈ **14,3%** (Ke 13%, g 5%, đường lợi nhuận cơ sở; `hpg_valuation_out.txt`, nội suy giữa 14% → 20.392 và
15% → 22.498). ROE lõi TTM ≈ 22.943 / VCSH mẹ bình quân ≈ 16–17% (ước lượng), 2024 ≈ 9–10%, 2025 ≈ 12% (ước lượng từ [KT25]).

**Đổi nhận định theo CẢ HAI chiều (chi tiết §9):** LÊN (vùng 24–27k) nếu Q4/26 LNST lõi ≥ 8.000 tỷ **và** biên gộp ≥ 18% **và** CFO 12T ≥ LNST lõi
**và** AD HRC còn hiệu lực 31/03/2027. XUỐNG (vùng 14–17k) nếu biên gộp một quý < 15% (mức Q4/25: 13,85%) **hoặc** AD HRC bị huỷ/giảm **hoặc**
thêm một giao dịch góp vốn ngoài ngành ≥ 5.000 tỷ.

⚠️ **Tự đính chính trong phiên** (để Mike không lặp lại): dòng "Lãi trong công ty liên kết" 9T/2026 = **1.987.970.143 VND = 1,99 tỷ**, KHÔNG phải
1.988 tỷ. Kiểm: [BN] 18.852,9 + 6.555,0 − 3.794,6 − 3.062,6 − 693,7 + 1,99 = 17.859,0 = LN thuần HĐKD báo cáo ✓.

## 2. Kiểm lại số Mike đọc từ slide

| Số Mike | BCTC | Kết luận |
|---|---|---|
| DT Q3 62.669 (+70%), Q3/25 36.794 | DT bán hàng 62.669,1 / 36.793,9 (+70,3%); **DTT** 62.214,2 / 36.407,4 [HN-Q3 tr.5] | ✓ (slide dùng DT gộp) |
| LNST Q3 8.265 (+106%), Q3/25 4.012 | 8.265,4 / 4.012,3 (+106,0%); CĐ mẹ 8.217,3 | ✓ |
| 9T DT 171.539 (+54%), LNST 23.746 (+104%) | 171.539,2 (+54,5%); 23.745,9 (+104,2%) | ✓ — nhưng xem §3: lõi 9T ≈ 19.243 |
| ≈ 82% DT / 108% LNST KH năm | KH ĐHĐCĐ 2026: DT 210.000 / LNST 22.000 [WEB ACBS 24/04] ⇒ 81,7% / 107,9% | ✓; **lõi chỉ ~87% KH** |
| EBITDA Q3 14.307 | Tự tính LNTT 9.108,7 + lãi vay 1.774,0 + KH 3.063,1 = **13.945,8** | lệch 361 (định nghĩa slide khác, chưa đối chiếu) |
| TTS 283.450 / 257.899; VCSH 149.568 / 131.221 | 283.449,8 / 257.899,2; 149.568,4 / 131.220,0 [HN-Q3 tr.2–4]; TS − (Nợ + VCSH) = 0,0 ✓ | ✓ |
| Vốn CP 84.430 / 76.755 ⇒ thưởng 10%? | ✓ **cổ tức bằng CP 10%** cho năm 2025: 767.498.665 cp, hoàn tất 26/05/2026, niêm yết 02/07, GD từ 15/07/2026; 8.442.964.520 cp lưu hành, không có CP quỹ [BN TM28/43; HN-Q3 VI.17c] | ✓ |
| Lợi ích CĐKS 772,9 | 772,9 (đầu năm 2.039,0 — giảm 1.705,9 do **thanh lý công ty con**) | ✓ |
| Thép DT 165.784 / LNST 18.396; NN 5.064/948; BĐS 1% DT / 19% LNST | BĐS 9T LNST = 4.293,0 [BN seg] + 204,9 [HN-Q3 seg] = **4.497,9** (18,9%) — **gần như toàn bộ là lãi thoái vốn một lần**; NN 648,2 + 300,0 = 948,2 ✓; thép + loại trừ = 18.299,8 (slide 18.396, lệch 96 — chưa rõ cách phân bổ) | nửa đúng: "19% từ BĐS" không phải lợi nhuận kinh doanh BĐS |
| Tiền + TĐT ~2.099 | **6.852,9** = tiền 2.099,3 + **tương đương tiền 4.753,6** [HN-Q3 VI.1] | ✗ slide/Mike chỉ lấy dòng "Tiền" |
| HTM 39.273 (19.878 đầu năm); PT NH 16.896 | 39.273,9 (tiền gửi có kỳ hạn 39.261,9 + CCTG 12,0) / 19.878,1; 16.896,5 | ✓ |
| HTK 52.130 → 46.949 | 52.130,8 → 46.949,2 (gộp 52.189,0 → 47.021,6; DP 58,2 → 72,5) | ✓ **HTK GIẢM**, không tăng |

## 3. Câu 1 — Lợi nhuận gấp đôi có bền không?

### 3a. Bảng 7 quý (hợp nhất; Q2, Q4 = luỹ kế trừ nhau) [KT25/BN/HN-Q1/HN-Q3; `hpg_calc_out.txt`]

| Quý | DTT | LN gộp | Biên gộp | DT tài chính | Lãi vay | LNTT | LNST | LNST mẹ |
|---|---|---|---|---|---|---|---|---|
| Q1/25 | 37.621,7 | 5.424,2 | 14,42% | 438,1 | 627,0 | 3.839,8 | 3.349,8 | 3.344,3 |
| Q2/25 | 35.910,5 | 6.589,7 | 18,35% | 498,1 | 439,1 | 4.972,3 | 4.264,5 | 4.256,5 |
| Q3/25 | 36.407,4 | 6.087,3 | 16,72% | 711,9 | 812,2 | 4.628,3 | 4.012,3 | 3.988,3 |
| Q4/25 | 46.176,5 | 6.396,7 | **13,85%** | 437,3 | 1.236,6 | 4.600,1 | 3.888,3 | 3.864,1 |
| Q1/26 | 52.900,8 | 8.365,1 | 15,81% | **5.938,3** | 1.333,4 | 10.762,2 | 9.055,9 | 8.994,0 |
| Q2/26 | 55.158,9 | 10.487,8 | 19,01% | 616,7 | 1.519,6 | 7.184,7 | 6.424,5 | 6.371,0 |
| Q3/26 | 62.214,2 | 11.922,5 | 19,16% | 1.188,0 | 1.774,0 | 9.108,7 | 8.265,4 | 8.217,3 |

Đối chiếu cộng: 9T/26 − (H1 + Q3) lệch ≤ 0,6 tỷ ở mọi dòng (làm tròn) ✓.

### 3b. Bóc một lần — 9T/2026

| Khoản | Trước thuế | Nguồn |
|---|---|---|
| Lãi bán, thanh lý khoản đầu tư tài chính ("chủ yếu chuyển nhượng cổ phần tại các công ty con") — nằm ở Q1 (DTTC Q1 5.938,3) | **4.929,1** | [BN TM34] |
| Q3: lãi 112,7 − lỗ 108,4 chuyển nhượng đầu tư | 4,3 | [HN-Q3 VII.4/5] |
| Lãi liên doanh liên kết | 1,99 | [BN tr.8] |
| Thuế TNDN phân khúc BĐS H1 (proxy thuế trên khoản lãi trên) | −1.030,2 | [BN seg tr.51] |
| BĐS vận hành (H1 phần dư + Q3) — rời hợp nhất từ Q3 | ~599 sau thuế | tự tính |

⇒ **LNST lõi 9T/2026 ≈ 19.243 tỷ (+65,5% vs 9T/25 11.626,6)**; **Q3/26 lõi ≈ 7.974 tỷ (+99%)** (bỏ BĐS 204,9 và 80% CLTG chưa thực hiện
+104,4 & lãi đầu tư thuần 4,3). Chuỗi lõi theo quý ≈ Q1 ~5,2k → Q2 ~6,4k → Q3 ~8,0k (ước lượng Q1: 9.055,9 − 4.929,1 + 1.030,2 − phần BĐS).
**TTM lõi CĐ mẹ ≈ 22.943 tỷ ⇒ EPS lõi 2.717 đ**; TTM báo cáo 27.446,5 ⇒ EPS 3.251 đ (khớp [BQ] PE 6,46 ngày 30/10 ⇒ BQ đã nạp Q3 và dùng
số có lãi một lần).

Lưu ý: tăng vốn chủ ở HPA (IPO 30 tr cp, 01/2026) đi thẳng VCSH (+383,5 LNCPP, +356,6 CĐKS), **không qua P&L** [HN-Q3 VI.17 tr.27] — đúng chuẩn.

### 3c. Biên gộp tăng từ đâu (Q3/26 19,16% vs Q3/25 16,72%: +2,44 pp; vs Q2/26 19,01%: phẳng)

BCTC KHÔNG tách DT/giá vốn theo sản phẩm (thép XD / HRC / ống / tôn) — chỉ 3 mảng thép / nông nghiệp / BĐS ⇒ **không tách được bằng số
BCTC** pp biên nào đến từ spread, mix HRC, hay thuế AD. Những gì đo được:
- **Không có hoàn nhập dự phòng HTK**: DP tăng 58,2 → 72,5 [HN-Q3 VI.5]. Biên không đến từ hoàn nhập.
- **Spread không giúp**: [BOBBY §3b] spread HRC thô ≈ 240 (H1) → 250 USD/t (10/2026), "đi ngang giữa chu kỳ". Quặng −, than cốc +36% yoy.
- **Khối lượng**: Q3 3,8 tr t (+54% yoy, +8% qoq), 9T ~10,3 tr t (+39%), HRC ~5,47 tr t (+59%), thép XD + cuộn CLC >4 tr t (+15%) [WEB, chưa
  đọc thông cáo gốc]. ⇒ Biên tăng chủ yếu nhờ **hấp thụ chi phí cố định khi Dung Quất 2 lên công suất + mix HRC** (cùng chiều đọc của Bobby).
- **Khấu hao + lãi vay DQ2 ĐÃ vào P&L**: KH Q3/26 3.063 vs ~1.863/quý 2025 (9T/25 5.588 ÷ 3); lãi vay Q3 1.774 vs 812 (Q3/25). Nghĩa là
  "vách khấu hao/lãi vay khi dự án vận hành" (checklist #11) **đã đi qua** — lợi nhuận Q3 đã gánh nó.
- **Giá trị bảo hộ AD (ước lượng)**: HRC nội 556 USD/t vs Trung Quốc FOB 493 (+cước ~15–20) và Indonesia CFR 536 [BOBBY §2d]. Nếu không có
  AD, trần giá ≈ 510–530 ⇒ chênh 25–45 USD/t × ~7,3 tr t HRC/năm (9T 5,47 quy năm) ≈ **180–330 tr USD ≈ 4.700–8.500 tỷ/năm trước thuế** (tỷ giá ~26.000)
  (ước lượng, giả định truyền dẫn đủ, chưa trừ mất khối lượng do nhập khẩu quay lại). Đây là cỡ rủi ro F8.
- Chi phí bán hàng/DTT 2,72% (Q3/25 2,19%): vận chuyển & XK 1.063,0 vs 347,6 — đi cùng XK tăng (XK = **26,4% DTT Q3** vs 12,6%) [VII.1/VII.6].

### 3d. Tài chính, tỷ giá, thuế
- Lãi tiền gửi Q3 704,3 trên số dư tiền + HTM bình quân ~41,7k ⇒ **~6,8%/năm** (ước lượng; số dư 30/6 đọc ở độ phân giải thấp). Lãi vay Q3
  1.774 trên vay ~106k ⇒ ~6,7%/năm. ⇒ Giữ 39k tiền gửi trong khi vay 106k là **carry gần trung tính**; một phần tiền gửi là **tài sản bảo đảm
  khoản vay** [BN TM25]. Không phải "lãi tài chính một lần".
- CLTG Q3: đã thực hiện +261,9 / −248,8; chưa thực hiện +105,3 / −0,9 — nhỏ. Vay USD 12.612 tỷ tại 30/6 (31/12/25: 3.575) [BN TM25a].
- **Thuế suất hiệu dụng**: Q3/26 **9,3%**, 9T 12,2%, 2025 14,0% (tự tính). Thấp hơn 20% ⇒ có ưu đãi (Dung Quất). **Thời hạn ưu đãi chưa
  kiểm được** (không đọc thuyết minh thuế BCTC năm). Mỗi +5 pp thuế suất ≈ −1.700 tỷ LNST/năm trên LNTT lõi ~34k (ước lượng).
- Liên kết: 1,99 tỷ — không đáng kể (xem §1 đính chính).

### 3e. LNST chuẩn hoá chu kỳ (ước lượng)
Mid-cycle EBITDA ≈ 40.000 tỷ (KL ~14–15 tr t, spread ~200–240 USD/t, KH ~12k/năm, lãi vay ~6–7k) ⇒ LNST mẹ chuẩn hoá ≈ **21.000–23.000 tỷ**
(ROE ≈ 12–14% trên VCSH ~165–175k năm 2027). Q3 quy năm (~32k) là **khoảng trên** của chu kỳ hiện tại, không phải mức chuẩn.
Độ nhạy: ±10 USD/t giá HRC × ~7,3 tr t ≈ ±1.900 tỷ LNTT/năm (ước lượng); spread 250 → 175 USD/t ≈ −14.000 tỷ LNTT/năm trên riêng HRC.

## 4. Câu 2 — Bảng cân đối, dòng tiền [HN-Q3]

| 30/09/2026 vs 01/01/2026 | Số | Ghi chú |
|---|---|---|
| Tiền + TĐT | 6.852,9 / 8.325,1 | 01/01 "số điều chỉnh lại" (KT25 cuối năm 8.300,9; lệch 24,2 — đổi mẫu TT 43/2026, chưa đọc TM điều chỉnh) |
| Tiền gửi HTM ngắn + dài | 39.276,2 / 22.145,0 | |
| Vay NH + DH | 78.615,0 + 27.121,7 = **105.736,7** / 92.174,2 | vay +13.562,5 |
| **Nợ ròng thật** (vay − tiền − HTM) | **59.607,6** / 61.704,1 | giảm nhẹ dù capex lớn |
| EBITDA TTM | 49.170,7 báo cáo; **44.235 lõi** (bỏ 4.935 một lần) | |
| **Nợ ròng / EBITDA lõi** | **1,35x** | Bobby ngưỡng cờ đỏ >3x — ổn |
| Vay / VCSH | 0,71x | |
| HTK | 46.949,2 (đi đường 4.340,7 ↓ từ 10.799,5; NVL 25.515,5 ↑; thành phẩm 13.188,4; SXKD dở dang 607,6 ↓ từ 3.190 = BĐS ra khỏi hợp nhất) | ~85 ngày GVHB Q3 (ước lượng) |
| DP giảm giá HTK | 72,5 (0,15% HTK) | quặng ở đáy 2 năm, chưa thấy trích lập |
| Phải thu KH | 12.237,6 (DP 131,8) | ~18 ngày DT Q3 |
| Trả trước người bán NH | 3.805,1 / 1.878,1 | +1.927 |
| XDCB dở dang | 16.113,3 / 10.702,1 — **KLH Dung Quất 11.146,0** (6.300,9), Container 2.269,7, NM thép Long An 880,5, Hải Dương 496,6 | DQ vẫn còn hạng mục |
| Cam kết vốn chưa thực hiện | ~19.472 tại 30/6 (31/12/25: ~32.072) | [BN TM41] |
| Đầu tư liên kết | **12.664,1** / 0 | TLSH 25,13% + BĐS HP 26,55% (§6) |

**Dòng tiền 9T/2026** [HN-Q3 tr.6–7]: CFO **20.936,3** (9T/25 8.801,6) = 0,88x LNST báo cáo, **1,09x LNST lõi** ✓. Capex 14.607,2 ⇒ **FCF ≈ 6.329**;
cổ tức tiền −3.937,4; thu thoái vốn +9.800,8; chi góp vốn −4.892,9; cho vay/gửi HTM ròng −24.790,5. 2025: CFO 17.365,9 vs LNST 15.514,9; 2024: CFO
6.608,3 vs 12.020,0 [KT25] — 2024 là năm vốn lưu động phình.

**TTS +25.550,6 tài trợ bằng**: VCSH +18.348,4 (LN giữ lại; cổ tức CP không đổi tổng VCSH) + nợ +7.202,2 (vay +13.562,5, phải trả người bán NH −4.410,4).
Phần lớn tài sản tăng đi vào **tiền gửi HTM (+17.131)** và **đầu tư liên kết (+12.664)**, không vào TSCĐ (NG +7.062).

**Cổ tức/pha loãng**: 2025 = 5% tiền (3.837,7 tỷ cho CĐ mẹ ≈ 500 đ/cp) + 10% CP; KH 2026 = 15% (hình thức chưa công bố) [BN TM28].
EPS TTM sau thưởng (8.442,96 tr cp): **3.251 báo cáo / 2.717 lõi**. BVPS 17.624 đ (VCSH mẹ 148.795,5).

## 5. Câu 3 — Ngành → doanh nghiệp

- **Xuất khẩu theo khu vực 6T/2026** [BN tr.53]: VN 79,1%, Á (trừ VN) 12,3%, Âu 3,6%, Mỹ 4,0%, Úc 1,0%, Phi 0,1%. **EU + Mỹ + Úc = 8,5%
  DTT** < ngưỡng 30% của Bobby. Q3: XK 26,4% DTT (16.395 tỷ) — tăng mạnh nhưng chủ yếu châu Á (chưa có phân rã Q3).
- **Mỹ AD thép cây**: nhóm Hòa Phát 121,97% (sơ bộ 03/2026) [WEB]; Bobby: lệnh cuối 09/2026, 123–137%. Mỹ ~4% DTT H1 gồm cả sản phẩm khác ⇒
  mất phần thép cây sang Mỹ là nhỏ (ước lượng < 2% DTT). **Không thấy dự phòng/ký quỹ PVTM** trong TM16 [HN-Q3].
- **EU** quota VN ~1,6 tr t/năm, ngoài hạn ngạch 50% [BOBBY]; EU 3,6% DTT HPG ⇒ tác động vừa; **CBAM chưa kiểm được** (cần BC PTBV).
- **Mất AD HRC (F8)**: ≈ 4.700–8.500 tỷ LNTT/năm (ước lượng §3c) ≈ 15–25% LNTT lõi + mất một phần khối lượng thay thế nhập khẩu.
- **Thị phần thép XD**: 35% 9T/2026 (36% 2025, 38% 2024) [BOBBY/VSA]; HPG XD +15% vs ngành +19,6%, miền Nam ngành +29,9% ⇒ **mất thị phần nhẹ,
  rõ nhất nơi tăng trưởng nhanh** (miền Nam — phân rã theo vùng của HPG chưa kiểm được).
- **Giá bán bình quân** (thô, ước lượng): DTT ngoài phân khúc thép Q3 60.362 / 3,8 tr t ≈ 15,9 tr đ/t (~610 USD/t) — gồm cả ống/tôn nên chỉ là chỉ báo.
- **Công suất/hiệu suất**: HRC 9T 5,47 tr t ≈ 7,3 tr t/năm vs DQ1 ~3 + DQ2 5,6 (thiết kế) [BOBBY] ⇒ ~85% (ước lượng). VinMetal (F10, P 0,35) là
  đối thủ HRC thứ hai sau 2027.

## 6. Câu 4 — Quản trị & pháp lý — ⚠️ WARNING

- **Kiểm toán**: BCTC 2025 Deloitte VN, **chấp nhận toàn phần** (24/03/2026); soát xét 6T/2026 Deloitte, **kết luận chấp nhận toàn phần, không nhấn
  mạnh** (28/08/2026) [KT25 tr.6; BN tr.8]. ⚠️ "Vấn đề khác" KT25: BCTC 2024 do **một công ty kiểm toán khác** kiểm toán ⇒ **đổi kiểm toán viên từ
  năm 2025** (tên KTV cũ chưa đọc; không thấy ý kiến ngoại trừ ở cả hai).
- ⚠️ **Thoái vốn BĐS sang Tập đoàn Tương lai Sông Hồng (TLSH)** — giao dịch quản trị lớn nhất năm:
  - NQ 10/NQHP-2026 (22/07/2026): HPG mua 799,5 tr cp mới TLSH (7.995 tỷ mệnh giá), **trả bằng cổ phần CTCP Phát triển BĐS Hòa Phát** [BN TM43].
    Hoàn tất (CBTT 01/10/2026): HPG góp tổng 9.915 tỷ = **25,13% TLSH**; còn giữ **26,55% BĐS HP** [WEB Mekong ASEAN; HN-Q3 tr.9 xác nhận 25,133% /
    26,547%].
  - TLSH: thành lập 14/11/2025, vốn 1.500 → 39.450 tỷ trong < 1 năm; CT HĐQT Trần Đăng Khoa 40% sáng lập; dự án KĐT 696 ha Thư Lâm/Đông Anh
    (TMĐT 60.600 tỷ) và KĐT/tái định cư Lĩnh Nam phục vụ Đại lộ cảnh quan Sông Hồng (liên danh Đại Quang Minh, Thaco, Hòa Phát, TLSH) [WEB].
  - **Định giá cổ phần BĐS HP mang góp chưa thống nhất giữa các nguồn**: VietnamFinance 24/07 nêu 32.000 đ/cp; Mekong ASEAN 01/10 nêu ~778,4 tr cp
    (ngầm ~10.270 đ/cp). **Chưa đọc CBTT gốc.** BCTC Q3 KHÔNG ghi lãi đáng kể từ giao dịch này (Q3 lãi đầu tư thuần 4,3 tỷ) ⇒ giao dịch ghi
    xấp xỉ giá trị sổ trong hợp nhất (suy luận).
  - Hệ quả: tài sản BĐS (~14,7k tỷ tại 30/9/25 [HN-Q3 seg tr.34]) đổi thành **12.664 tỷ khoản đầu tư liên kết** (8,5% VCSH) vào một doanh nghiệp
    BĐS mới, đòn bẩy dự án lớn, không do HPG kiểm soát. **Không thấy công bố là giao dịch bên liên quan** (BCTC Q3 không có thuyết minh bên liên
    quan; [BN TM42] chỉ có thù lao). Rủi ro "scandal di cư": giá trị khoản đầu tư phụ thuộc pháp lý dự án đất lớn Hà Nội; nghĩa vụ góp vốn
    thêm/bảo lãnh cho TLSH **chưa kiểm được**.
  - Trước đó, H1 đã bán cổ phần các công ty con BĐS (KCN/đô thị) lãi **4.929 tỷ** — người mua không nêu trong BCTC [BN TM34]; thuế TNDN của
    các công ty con rời hợp nhất 1.083 tỷ [HN-Q3 VI.13].
- ⚠️ **Vay ngân hàng được bảo đảm một phần bằng "cổ phiếu HPG do các cá nhân sở hữu"** [BN TM25a] — đan xen tài sản cá nhân cổ đông lớn với
  tín dụng của công ty; số lượng/giá trị cổ phiếu cầm cố không công bố.
- **Cổ đông**: nhóm ông Trần Đình Long ~35,46% (Long 25,80%, Vũ Thị Hiền 6,88%, Trần Vũ Minh 2,73%) [BN TM28; WEB]. Trần Vũ Minh đăng ký mua 50 tr
  cp 07/10–05/11/2026 (đợt 3–4/2026 đăng ký 50 tr, chỉ mua 33,29 tr) [WEB] — nội bộ mua vào ở vùng 20.000.
- **Thù lao HĐQT 6T/2026 207,7 tỷ** (6T/25 83,2) + 180,0 tỷ thưởng/thù lao trích từ LNCPP trong 9T [BN TM42; HN-Q3 VI.17] — tăng mạnh, cùng chiều lợi nhuận.
- **Sở hữu nhà nước**: không có (cơ cấu cổ đông [BN TM28]). **Kiện tụng/khởi tố liên quan HPG**: tìm web 31/10 **không thấy** [WEB]; không thấy
  khoản dự phòng pháp lý trong TM16. Đây là "không tìm thấy", không phải "đã xác minh sạch".
- Đầu tư ngoài ngành mới: Điện gió Ngoài khơi Sông Hậu 30% × 2.000 tỷ = 600 tỷ (NQ 08/NQHP-2026) [BN TM41].

## 7. Câu 5 — Định giá (giá 21.000 đ phiên 30/10/2026 [BQ])

**Thị trường**: vốn hoá **177.302 tỷ**; EV (vốn hoá + nợ ròng 59.608 + CĐKS 773 − đầu tư liên kết 12.664) ≈ **225.019 tỷ**.

| Bội số | Hiện tại | Lịch sử [BQ, trung vị năm] |
|---|---|---|
| P/E TTM báo cáo | 6,46x | 2018 9,7 · 2019 7,9 · 2020 9,3 · 2021 10,8 · 2022 4,7 · 2023 82,8 · 2024 19,2 · 2025 14,3 |
| P/E TTM lõi (EPS 2.717) | **7,7x** | (BQ PE dùng EPS trễ ⇒ méo ở đáy/đỉnh chu kỳ: 2022 4,7x ở đỉnh LN, 2023 82,8x ở đáy) |
| P/E Q3 lõi × 4 | 5,6x | — |
| P/B | 1,19x | 2018 2,37 · 2019 1,46 · 2020 1,52 · 2021 2,96 · 2022 1,38 · 2023 1,31 · 2024 1,60 · 2025 1,57 · 2026 YTD 1,44; p10 thấp nhất 1,0 (2022) |
| EV/EBITDA lõi TTM | **5,1x** | BQ EVEB trung vị 2018–2025 ≈ 4,7–15,6 (méo như PE) |

P/B 1,19x là mức thấp nhất kể từ 2022 (p10 2022 = 1,0). Giá điều chỉnh từ đỉnh 25.710 (02/2026) xuống 21.000 (−18%) trong khi VNINDEX −7% và LN
lõi tăng — thị trường đang chiết khấu "lợi nhuận đỉnh + rủi ro TLSH/AD".

**Comp ngành** — chỉ tham chiếu, KHÔNG đề xuất (NKG, HSG BANNED): **chưa đo trong phiên** (không truy vấn BQ cho POM/NKG/HSG; peer khu vực
không có nguồn). Ghi "chưa kiểm được".

**Mô hình thu nhập thặng dư (RI) 3 kịch bản** (BV0 = VCSH mẹ 148.795,5; payout tiền 20%; g = 5% ≤ GDP danh nghĩa dài hạn; tất cả LN (ước lượng)):

| Kịch bản (trọng số) | LNST mẹ Q4/26 · 2027 · 2028 · 2029 | ROE dài hạn | Điều kiện | Ke 12,3% | Ke 13,0% | Ke 13,4% |
|---|---|---|---|---|---|---|
| Xấu (0,25) | 6,0k · 15k · 13k · 14k | 10% | spread 150–200, AD giảm/gỡ, TQ nới XK | 11.304 | 10.189 | 9.637 |
| Cơ sở (0,50) | 7,5k · 26k · 23k · 22k | 12,5% | spread 200–240, AD giữ, DQ2 đủ tải | 19.121 | 17.233 | 16.298 |
| Tốt (0,25) | 8,5k · 32k · 30k · 28k | 15% | spread ≥ 250, KL ~15 tr t | 27.160 | 24.457 | 23.118 |
| **Trọng số** | | | | **19.176** | **17.278** | **16.338** |

- Ke nội địa β ~1,1 báo theo KHOẢNG **12,3–13,4%** (rf chuẩn hoá ~6,75% + ERP nội địa 5,0–6,1%), khung user duyệt 29–30/10; β HPG thật chưa đo.
  Kiểm RONIC ≥ Ke: kịch bản cơ sở ROE dài hạn 12,5% ≈ Ke ⇒ tăng trưởng gần như không tạo giá trị (terminal −6% giá trị ở Ke 13%); kịch bản tốt
  RONIC 15% > Ke ⇒ terminal +15–25%.
- **Độ nhạy g × Ke** (cơ sở): g 3–6% × Ke 11,5–14% ⇒ 14.713–22.276 đ (`hpg_valuation_out.txt`). **ROE dài hạn** là biến nhạy nhất: 12% → 16.180;
  14% → 20.392; 16% → 24.604 (Ke 13%).
- **Cross-check EV/EBITDA** (EBITDA chuẩn hoá xấu 28k / cơ sở 40k / tốt 48k, ước lượng) × 6x: 14.247 / 22.774 / 28.460 ⇒ trọng số ~22.060 đ;
  × 5–7x cơ sở: 18.037–27.512.
- **Tổng hợp**: RI trọng số 16.300–19.200 + EV/EBITDA ~22.000 ⇒ **vùng 17.000–23.000, trung tâm ~20.000 đ (ước lượng)**. Giá 21.000 ≈ +5% trên trung tâm.

**Phản ứng giá quanh BCTC** [BQ]: Q3/26 (29/10): +2,2% (VNI −0,6%), GTGD 772 tỷ ≈ 2× bình quân, 30/10 −0,9%. Q2 (28–29/07): +3,2% & +3,1%
(VNI +0,7%, +1,4%). Q1 (29/04): 0%. Q3/25 (29/10/25): +1,7%. ⇒ Thị trường phản ứng **nhạt** với lợi nhuận gấp đôi.

## 8. Câu 6 — Thanh khoản / sở hữu nước ngoài
GTGD bình quân **10/2026 ≈ 393 tỷ/phiên** (2025: 1.071; 02/2026: 1.523) [BQ]. Room ngoại còn ~26,4% (ACBS 24/04/2026 [WEB]) ⇒ NN sở hữu ~22,6%
(ước lượng); **số 10/2026 chưa kiểm được**. Megacap — lệnh vài tỷ đồng chỉ ~1% GTGD một phiên; thanh khoản không ràng buộc sizing ở quy mô fleet.

## 9. Mốc khoá trước có ngày chấm (lập 31/10/2026; P = ước lượng của Taylor; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm)

| # | Mệnh đề | P | Ngày chấm | Hướng nếu SAI |
|---|---|---|---|---|
| H1 | BCTC Q4/26: LNST hợp nhất Q4/26 ≥ 7.000 tỷ **và** biên gộp Q4 ≥ 17% | 0,55 | 2027-02-05 | ↓ (biên < 15% ⇒ vùng 14–17k) |
| H2 | HTK 31/12/2026 ≤ 52.000 tỷ **và** DP giảm giá HTK ≤ 300 tỷ | 0,70 | 2027-02-05 | ↓ (vốn lưu động phình/tồn kho giá cao) |
| H3 | CFO 12T/2026 ≥ 26.000 tỷ | 0,60 | 2027-02-05 | ↓ chất lượng LN |
| H4 | (= Bobby F8) Thuế AD HRC TQ + chống lẩn tránh 27,83% còn hiệu lực ngày 2027-03-31 | 0,90 | 2027-03-31 | ↓ mạnh (−4.700–8.500 tỷ LNTT/năm) |
| H5 | (≈ F7) BCTC Q1/27: LNST ≥ 6.000 tỷ **và** biên gộp ≥ 16% | 0,60 | 2027-05-05 | ↓ |
| H6 | VSA: thị phần thép XD HPG cả năm 2026 ≥ 34% | 0,65 | 2027-02-15 | ↓ (mất thị phần nội địa) |
| H7 | BCTC kiểm toán 2026: ý kiến chấp nhận toàn phần **và** không phát sinh cam kết/bảo lãnh cho TLSH hoặc góp thêm vào TLSH ≥ 2.000 tỷ | 0,75 | 2027-04-15 | ↓ (scandal di cư) |
| H8 | ĐHĐCĐ 2027: kế hoạch LNST 2027 ≥ 24.000 tỷ **và** cổ tức tiền ≥ 5% | 0,50 | 2027-05-31 | ↑ nếu đúng (xác nhận kịch bản cơ sở-tốt) |

**Đổi nhận định LÊN** (vùng 24.000–27.000): H1 với LNST lõi ≥ 8.000 **và** H3 **và** H4 đúng **và** Q1/27 biên ≥ 18% ⇒ ROE lõi bền ≥ 15% ⇒ chuyển
trọng số tốt từ 0,25 lên 0,40. Thêm nếu VN khởi xướng AD với HRC ASEAN (Bobby).
**Đổi nhận định XUỐNG** (vùng 14.000–17.000): biên gộp một quý < 15%, **hoặc** H4 sai, **hoặc** HRC TQ FOB < 450 USD/t (Bobby), **hoặc** HTK > 55.000 tỷ
kèm DP tăng, **hoặc** thêm giao dịch góp vốn/thoái vốn ngoài ngành ≥ 5.000 tỷ.

## 10. Checklist Bobby §7 (21 mục) bằng số HPG

| # | Kết quả |
|---|---|
| 1 cơ cấu SP/thị trường | Theo SP: **không có trong BCTC** (chỉ thép/NN/BĐS). Theo vùng: EU+Mỹ+Úc 8,5% DTT H1 < 30% ✓ |
| 2 sản lượng/thị phần | 9T ~10,3 tr t [WEB]; thị phần XD 35% (↓ từ 36%) ⚠️; chuỗi 8 quý: chưa kiểm được |
| 3 công suất vs sản lượng | HRC ~85% (ước lượng); từng dây chuyền: **chưa kiểm được** |
| 4 mô hình chuỗi | Tích hợp BOF; tự chủ quặng/than: chưa kiểm được |
| 5 biên gộp 7 quý | 13,85–19,16% (§3a); biên tăng khi spread phẳng ⇒ nhờ KL/mix, không nhờ spread |
| 6 giá vốn/tấn | GVHB Q3 50.292 / 3,8 tr t ≈ 13,2 tr đ/t (thô, gồm phi-thép); định mức tiêu hao: chưa kiểm được |
| 7 tồn kho/DP | 46.949 (~85 ngày), DP 72,5 — không có lãi "tồn kho giá rẻ" tách được |
| 8 CPBH/DT, lãi vay/EBIT | 2,72%; lãi vay/EBIT Q3 = 1.774 / 10.883 = 16% |
| 9 nợ/VCSH, ND/EBITDA, vay ngoại tệ | 0,71x; **1,35x**; vay USD 12.612 tỷ (30/6) |
| 10 CFO vs LNST | 9T 1,09x lõi ✓; 2025 1,12x; 2024 0,55x |
| 11 capex/XDCB/vốn hoá lãi vay | Capex 9T 14.607; XDCB 16.113 (DQ 11.146); cam kết ~19.472; **lãi vay vốn hoá: chưa kiểm được** (Q3 không có TM vay) |
| 12 phải thu, trả trước | PTKH ~18 ngày; trả trước NB +1.927; phải thu bên liên quan: chưa kiểm được |
| 13 LC/bảo lãnh/HĐ dài hạn | Chỉ có cam kết vốn dự án; **LC/bảo lãnh chưa kiểm được** |
| 14 PVTM bị đơn | Mỹ AD thép cây ~122% [WEB]; không thấy dự phòng/ký quỹ trong BCTC |
| 15 hưởng AD nội | Có (HRC); giá trị ước 4.700–8.500 tỷ LNTT/năm (ước lượng) |
| 16 CO₂/CBAM | **Chưa kiểm được** |
| 17 ưu đãi thuế | ETR 9,3–14% ⇒ có; **thời hạn chưa kiểm được** |
| 18 bên liên quan | Không có thuyết minh trong BCTC Q3; ⚠️ cổ phiếu cá nhân bảo đảm vay; TLSH (§6) |
| 19 ngoài ngành | ⚠️ 12.664 tỷ liên kết BĐS (TLSH + BĐS HP), điện gió 600 tỷ, nông nghiệp 6,0k TS |
| 20 pha loãng | Cổ tức CP 10% (2025), +20% (2024→2025: VĐL 63.963 → 76.755); không ESOP/riêng lẻ trong 9T |
| 21 kiểm toán | Chấp nhận toàn phần (KT25 & BN); ⚠️ đổi KTV từ 2025 |

## 11. Lệch nguồn BQ vs BCTC
- [BQ] PE 30/10 = 6,46 = khớp EPS TTM báo cáo 3.251 ⇒ BQ đã có Q3 nhưng **gồm lãi thoái vốn** (PE lõi 7,7x). PB 1,185 ≈ 1,19 ✓.
- BQ `EVEB` rỗng ngày 29–30/10 (cột chưa cập nhật). BQ PE/EVEB lịch sử dùng LN trễ ⇒ không dùng làm "trung vị chu kỳ" trực tiếp.
- Không dùng `ticker_financial` (Cash_P0 thiếu HTM; GPM/NP_P0 là TTM — bẫy đã biết).

## Giới hạn
- BCTC Q3 không có thuyết minh vay chi tiết, lãi vay vốn hoá, bên liên quan, thuế ưu đãi — các mục đó lấy từ [BN] 30/6 hoặc ghi "chưa kiểm được".
- Định giá BĐS HP mang góp TLSH, người mua các công ty con BĐS H1, nghĩa vụ với TLSH: cần CBTT gốc (HOSE) — chưa đọc.
- Sản lượng theo sản phẩm và thị phần là số báo chí/VSA, không có trong BCTC.
- β HPG, comp ngành, room ngoại 10/2026: chưa đo.
- Số dư tiền/HTM 30/6 dùng cho lãi suất ngầm đọc ở ảnh độ phân giải thấp (chỉ ảnh hưởng ước lượng ~6,8%).

## Nguồn web (truy cập 31/10/2026)
- Thời báo Tài chính VN, "Hòa Phát bán hơn 10,3 triệu tấn thép trong 9 tháng": https://thoibaotaichinhvietnam.vn/hoa-phat-ban-hon-10-3-trieu-tan-thep-trong-9-thang-205266.html
- Báo Pháp luật/Doanh nhân (HRC 5,47 tr t): https://doanhnhan.baophapluat.vn/hoa-phat-ban-hon-10-3-trieu-tan-thep-trong-9-thang-tang-39-so-voi-cung-ky-nam-truoc-0248b535.md
- Báo Đấu thầu (Q3 3,8 tr t): https://baodauthau.vn/hoa-phat-ban-hon-103-trieu-tan-thep-trong-9-thang-nam-2026-post209725.html
- VietnamFinance 24/07/2026 (TLSH, 32.000 đ/cp): https://vietnamfinance.vn/hoa-phat-gop-gan-8000-ty-vao-dn-lien-quan-du-an-dai-lo-song-hong-d148030.html
- Mekong ASEAN 01/10/2026 (TLSH hoàn tất 25,13%): https://mekongasean.vn/hoa-phat-gop-gan-10000-ty-dong-vao-tap-doan-tuong-lai-song-hong-60223.html
- Mekong ASEAN 02/10/2026 (Trần Vũ Minh mua 50 tr cp): https://mekongasean.vn/con-trai-ong-tran-dinh-long-du-chi-hon-1000-ty-dong-mua-co-phieu-hpg-60254.html
- Nhà Đầu Tư (AD Mỹ 121,97%): https://nhadautu.vn/bi-ap-thue-den-122-hoa-phat-anh-huong-ra-sao-d103536.html
- ACBS Flashnote 24/04/2026 (room ngoại, KH 2026): https://acbs.com.vn/acbsmedia/2026/04/HPG_Flashnote_24042026.pdf
