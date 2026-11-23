# DD — POW (Tổng công ty Điện lực Dầu khí Việt Nam – CTCP, HOSE) · REV3 · 23/11/2026 · job `Taylor_20261123_050007`

> Chỉ nghiên cứu. Không đặt lệnh, không gửi email, không ghi sổ giá. Đơn vị: tỷ đồng, trừ khi ghi khác.
> REV3 dựng lại sau fundamental-skeptic DD_GENERAL r1 (22/11/2026, `skeptic/r1.json`: **INCONCLUSIVE**, md5 báo cáo `7d610c77…` = `REPORT.md` vòng 2).
> Bản cũ giữ nguyên: `REPORT.md` (vòng 2, tâm 9.792). Nền giữ nguyên rev2 trừ các mục ở §A.
> **Khoá giả định (mù giá):** `model/assumptions_POW_20261123_rev3.json` **md5 `858632b79798a6b3e697b9d52482a4d7`**, `dd_assumptions_lint.py --strict` 0 vi phạm.
> Đầu vào bổ sung `model/model_rev3_inputs.json`; mô hình `model/calc_rev3.py`; output `model/calc_rev3_output.txt` (tái lập rev2 9.891/9.792 khớp). Nền rev2 `model/assumptions_POW_20261118_rev2.json` md5 `721c5f28a97867749da9499ca68fa20e`.
> Nguồn: **[BCTC]** BCTC HN Q3/2026 `src/Q3_2026_BCTC_hopnhat.pdf`; **[KT25]** BCTC HN kiểm toán 2025 (Deloitte, ký 12/03/2026); **[CBTT]** `src/cbtt/<ngày>_<id>/`; **[QTP]** DD QTP r3/r3b/r3c `agents/Taylor/research/qtp_r3_envcapex_20261120/` (FS cải tạo khí thải + phân tích pháp lý legal-vn 20/11). Số không đo được gắn **(ước lượng)**.

## 0. Kết luận

- **Giá trị nội tại, tâm = 9.064 đ/cp** (sau chiết khấu thanh khoản 1%; trước: 9.156). **Vùng [6.438; 11.691]** (xấu → tốt, trọng số 25/50/25). Mốc 0,85×tâm = **7.705**.
  Rev2: 9.792, vùng [7.166; 12.419] ⇒ **−7,4%**, toàn bộ do **capex + opex tuân thủ QCVN 19:2024 tại VA1** (luật D3: capex tuân thủ = dòng tiền ra trong base): PV kỳ vọng **2.255 tỷ = −735 đ/cp** (trước CK).
- r = 13,5% (lãi huy động 12T hiệu dụng 7,4% ngày 23/11 = neo), g = 0. Ở tâm P/B mẹ = 0,64 (BVPS mẹ 14.060).
- **So giá (sau khoá):** DNSE 13.350 đ (23/11/2026 11:29) = **1,47 × tâm**, trên cận trên vùng (11.691). Nhãn **ĐẮT** (không đổi so với rev2; biên đắt rộng hơn). Giá ngầm định ROE di sản **13,7%/năm vĩnh viễn** (rev2: 12,6%).
- **Hạng mục lớn nhất chưa ngã ngũ, hai chiều:** (i) VA1 có được tính chi phí khí thải vào giá điện không — P0 (không bù) ⇒ 8.537, P100 (bù đủ) ⇒ 9.792; (ii) đời máy hữu hạn của vốn di sản (vốn thu hồi qua khấu hao, tái đầu tư NPV=0) ⇒ +11…+18% — **chỉ độ nhạy, không vào base** (§C); (iii) NT3&4 nếu ghi giảm 30% ⇒ −9,6% — **chỉ độ nhạy** (§B2).
- Các điểm khác của rev2 giữ nguyên: 9T/26 ~40% LNTT là một lần (≈2.755), LNST mẹ cốt lõi 9T 3.980–4.063; CFO 9T 2.739 vì phải thu EPTC 23.880; nợ ròng thật **7.348** (sửa từ 7.368, §A6); moat NONE; WARNING pháp lý nhẹ (quyết toán CPH chưa duyệt).
- **Sizing (V8, chuẩn 2–4% NAV/mã):** ở giá hiện tại **không mở**. Chỉ cân nhắc khi giá ≤ 7.705 (0,85×tâm) ⇒ tối đa 2% NAV; ≤ 6.438 (cận dưới) ⇒ 3% NAV. Không đề xuất >4%.

## A. Đính chính so với rev trước (từng hạng mục skeptic r1)

| # | Hạng mục skeptic r1 | Xử lý rev3 | Loại | Ảnh hưởng tâm (sau CK) |
|---|---|---|---|---|
| A1 | **Capex tuân thủ QCVN 19:2024 bị bỏ sót** (CBTT thầu tư vấn) | **Vào base** như dòng tiền ra (D3): VA1 1.200 MW, tương tự QTP 1.200 MW (FS: TMĐT 3.485 + opex 572/năm), giải ngân 2029–31, opex từ 01/01/2032, sau thuế 20%, trừ lá chắn khấu hao 15 năm; xác suất bù giá P0/P50/P100 = 0,40/0,36/0,24 (QTP r3b, cùng khung pháp lý). PV P0 = 3.888; kỳ vọng 2.255. Chi tiết §B1 | (a) base, có nguồn | **9.792 → 9.064 (−7,4%)** |
| A2 | NT3&4 NPV=0 có thể quá cao (LNG định hạn ~1/3 Qc, ToP chưa có) | **Giữ NPV=0 ở sổ** (V4a). Cơ sở: hợp đồng định hạn 20,7 tr MMBtu/năm (≈3,2 tỷ kWh) **thấp hơn** mức đốt thực 2026 (23,8 tr MMBtu trong 9T ≈ 31,7/năm, CBTT 13/10) ⇒ rủi ro ToP (cam kết vượt nhu cầu) thấp; phần thiếu mua giao ngay. Rủi ro còn lại là công thức giá LNG ↔ giá Qc: **không công bố ⇒ không kiểm chứng được** ⇒ độ nhạy ghi giảm 15/30/50% | (b)/(c) | 0 ở base; −4,8% / −9,6% / −16,0% |
| A3 | Phạt ROE<r **vĩnh viễn** trên nhà máy già (tâm có thể quá thấp) | **Độ nhạy, không vào base.** Đo được: TSCĐ HH còn lại 43.475,6 / KH năm ~3.875 ⇒ 11,2 năm toàn công ty; di sản ~7 năm (ước lượng, sau khi trừ NT3&4 ~23.500). Không đo được: lợi nhuận nhà máy sau khi hết vốn (PPA bước giảm giá cố định, khí nội suy giảm) và phần vốn di sản không khấu hao (vốn lưu động, phải thu EPTC). §C | (b) | +11,5% … +18,1% |
| A4 | r 13,5% Ke chung; utility có thể thấp hơn | V1: r tâm = 13,5% (neo + β×Δ lãi huy động, Δ=0). D4: hai đầu dải Ke nội địa 12,3% ⇒ **9.584 (+5,7%)**, 13,4% ⇒ **9.104 (+0,4%)**; r 11% chỉ độ nhạy 10.276 | quy tắc | báo kèm |
| A5 | Tiền chào bán chưa dùng 1.080 ghi 1,0× trong khi tiền khác ở 0,59× (bất nhất) | **Giữ.** 1.080,1 được ĐHĐCĐ/HĐQT dành cho dự án (NQ 19 12/3/2026; báo cáo tiến độ 27/7) ⇒ V4 sổ sách. Tiền + HTM khác (30.158) **không phải tiền tự do của mảng di sản**: chúng đi kèm vay 37.505 (nợ ròng dương 7.348), lãi tiền gửi đã nằm trong ROE di sản 8% | giải trình | 0 |
| A6 | Vay ngắn hạn 19.438,3 vs 19.418,3 | **Sửa: 19.418,3** (OCR BCTC Q3 dòng 357 "19.418.289.505.077"); nợ ròng 7.367,7 → **7.347,7** | sửa số | 0 (mô hình dùng VCSH) |
| A7 | Hạn PPA / nguồn khí CM1&2 (2008), NT1 (2009) | **Không kiểm chứng được** (không công bố trong BCTN 2025, BCTC KT 2025, CBTT 11/2025–11/2026). Ảnh hưởng: nằm trong kịch bản xấu (ROE 4,5%, −29% so cơ sở) và độ nhạy đời hữu hạn (§C, chiều ngược lại) | (c) | trong vùng |
| A8 | Giá trị giao dịch bên liên quan | **Không kiểm chứng được** — thuyết minh bên liên quan KT25 là ảnh quét, OCR hỏng (không đọc được số). WARNING giữ. Ảnh hưởng: không định lượng được; cơ chế giá khí/LNG qua PV GAS là pass-through trong giá điện (Qc), nên rủi ro chuyển giá chủ yếu nằm ở mảng không pass-through (dịch vụ PVPS, ước lượng nhỏ) | (c) | không định lượng |
| A9 | Quyết toán CPH chưa duyệt — nghĩa vụ phải nộp PVN tiềm tàng | **Không kiểm chứng được** số còn lại. Độ nhạy: thêm một khoản bằng tiền lệ 728,2 (TM16 FY25) ⇒ **−235 đ/cp (−2,6%)** | (c) | −2,6% nếu xảy ra |
| A10 | ~2.755 LNTT hồi tố đã vào VCSH nhưng chưa thu tiền | Giữ base (khoản EVN/EPTC đã duyệt theo CBTT 03/08; DSO ~149 ngày không xấu đi). Độ nhạy: 30% / 50% không thu được ⇒ −238 / −396 đ/cp (−2,6% / −4,4%). Mốc T2 (§F) | (b) | độ nhạy |
| A11 | Quỹ khen thưởng phúc lợi (không trọng yếu) | Số dư 293,2 đã là nợ phải trả ⇒ không trừ thêm. Tỷ lệ trích hằng năm: **không công bố** ⇒ độ nhạy 3% / 5% LNST di sản ⇒ −2,0% / −3,3% | (c) | độ nhạy |
| A12 | (tự bổ sung) QCVN 19 cho nhà máy khí CM1&2 + NT1 (1.950 MW) | Gói tư vấn nói "các nhà máy nhiệt điện" nhưng không nêu hạng mục; **chưa xác lập có phải cải tạo** ⇒ không vào base. Độ nhạy minh hoạ 0,5 / 1,0 tỷ/MW (ước lượng thuần, sau bù kỳ vọng) ⇒ −1,3% / −2,5% | (c) | độ nhạy |

Điểm skeptic r1 xác nhận và giữ nguyên: tâm rev2 tái lập đúng; số cp 3.067.845.688; VCSH mẹ 43.134,5; LNST mẹ 9T 6.434,5; ROE di sản 8% có cơ sở (skeptic tự dựng ~8,0%, giữa dải — rev2 tự gọi là "cận trên", nay đính chính thành **giữa dải**).

## B. Định lượng các khoản mới

### B1. QCVN 19:2024 — VA1 (vào base)
- **Nghĩa vụ:** QCVN 19:2024/BTNMT bắt buộc với cơ sở hiện hữu từ **01/01/2032** (legal-vn 20/11, [QTP] REPORT_r3.md:91). Công ty đã khởi động: thầu "Tư vấn đánh giá kỹ thuật và lập báo cáo đề xuất đầu tư cho các nhà máy nhiệt điện của PV Power đáp ứng QCVN 19:2024 về khí thải công nghiệp" — trúng thầu **CTCP Tư vấn Xây dựng Điện 1**, **2,984 tỷ** (gồm VAT), thực hiện **Q3/2026 – Q1/2027** (CBTT 19/10/2026, `src/cbtt/2026-10-xx_7139_qcvn19/post.html`). Hai CBTT skeptic nêu (13/3 TB 545 và 15/4) — phần text đã trích không có giá gói thầu/TMĐT; số tiền chỉ thấy ở CBTT 19/10.
- **Quy mô:** TMĐT chưa công bố (báo cáo đề xuất đầu tư xong Q1/2027). Cơ sở định lượng duy nhất có nguồn độc lập: **FS QTP** cho 1.200 MW than — TMĐT **3.485 tỷ**, O&M cố định 102,0 + điện-nước-hoá chất 470,3 (amoniac 317,4) = **572 tỷ/năm** [QTP REPORT_r3.md dòng 12; r3c §2]. VA1 = 2×600 MW = cùng 1.200 MW ⇒ áp 1:1 (ước lượng). Hiện trạng thiết bị xử lý khí thải VA1 (đã có FGD/SCR chưa): **không công bố** ⇒ độ nhạy ×0,5 / ×1,5.
- **Lịch:** giải ngân 30/45/25% năm 2029/30/31, opex từ 2032 vĩnh viễn (nhất quán với giả định vốn di sản vĩnh viễn), thuế 20%, lá chắn khấu hao 15 năm; chiết khấu giữa năm về 30/09/2026 ở r 13,5% (ước lượng lịch).
- **Bù vào giá điện:** cùng khung pháp lý với QTP — TT12/2025 không có điều thoả thuận bổ sung chi phí (TT07/2024 Đ27.4 đã bãi bỏ); Luật Điện lực 61/2024 Đ52.4 mở lối nhưng chưa có tiền lệ nhà máy than được bù ⇒ dùng trọng số QTP r3b **P0 0,40 / P50 0,36 / P100 0,24**. Gánh nặng kỳ vọng = 0,40 + 0,36×0,5 = **0,58 × P0**.

| Biến thể | Gánh nặng PV (tỷ) | Tâm sau CK | so tâm rev3 |
|---|---|---|---|
| **Base (kỳ vọng)** | **2.255** | **9.064** | — |
| P0 (không bù) | 3.888 | 8.537 | −5,8% |
| P50 | 1.944 | 9.165 | +1,1% |
| P100 (bù đủ) | 0 | 9.792 | +8,0% |
| Trọng số 0,5/0,3/0,2 | 2.527 | 8.977 | −1,0% |
| Quy mô ×0,5 (VA1 đã có một phần) | 1.128 | 9.428 | +4,0% |
| Quy mô ×1,5 | 3.383 | 8.701 | −4,0% |
| Opex dừng 2045 (đời VA1 30 năm) | 2.074 | 9.123 | +0,6% |
| Thuế 10,9% | 2.420 | 9.011 | −0,6% |

Ước của skeptic r1 (−7…−12% nếu không bù) nằm quanh P0 của mô hình (−12,8% so rev2: 9.792 → 8.537); base −7,4% vì có xác suất bù.

### B2. NT3&4 (giữ NPV=0 sổ sách — chỉ độ nhạy)
Vốn chủ 9.000 theo sổ (rev2 §4). Lập luận ToP ở A2. Thiếu: công thức giá LNG định hạn và cơ chế chuyển giá nhiên liệu trong giá Qc ⇒ **không kiểm chứng được**. Lỗ/lãi NT3&4 không tách được từ BCTC HN (không có báo cáo bộ phận theo nhà máy). Ghi giảm 15/30/50% ⇒ 8.629 / 8.193 / 7.612.

## C. Đời máy hữu hạn của vốn di sản (chỉ độ nhạy)
Mô hình: vốn di sản giảm tuyến tính phần đang khấu hao (tỷ trọng s) trong T năm, vốn thu hồi tái đầu tư ở NPV=0 (V4); phần còn lại vĩnh viễn. TSCĐ HH Q3/26: nguyên giá 95.454,9, hao mòn luỹ kế 51.979,3, còn lại 43.475,6; KH 9T 2.905,9 [BCTC TM TSCĐ].

| s \ T | 7 năm | 11 năm |
|---|---|---|
| 0,50 | 10.348 (+14,2%) | 10.109 (+11,5%) |
| 0,64 | 10.708 (+18,1%) | 10.401 (+14,8%) |

Vì sao **không vào base**: (1) không có số theo nhà máy để biết lợi nhuận giữ ROE 8% trên vốn đang giảm hay giảm nhanh hơn (PPA bước giảm giá cố định sau giai đoạn thu hồi vốn; mỏ khí cấp CM1&2/NT1 suy giảm — Bobby); (2) s phụ thuộc giả định gán toàn bộ nợ ròng cho NT3&4 (cận trên); (3) ROE di sản 8% lịch sử được đo trên vốn đã có khấu hao + tái đầu tư, nên một phần hiệu ứng này đã nằm trong số đo. Đây là **độ nhạy lên lớn nhất** — cả cận trên (10.708) vẫn dưới giá 13.350.

## D. Độ nhạy khác (calc_rev3_output.txt; tâm sau CK)
- Lãi huy động ±50bp (β=1): 9.269 / 8.874 (+2,3% / −2,1%); ±100bp: 9.490 / 8.698 (+4,7% / −4,0%); β=0,5: ±1,1% / ±2,3%.
- Dải Ke D4: r 12,3% ⇒ 9.584; 13,4% ⇒ 9.104. r 11% ⇒ 10.276.
- ROE cả 3 kịch bản −2pp / +2pp: 7.564 / 10.565.
- Thanh khoản (V3): ADV trung vị 62 phiên **63,3 tỷ/phiên** (BQ, đo 18/11, rev2 §8b); vị thế ≤30 tỷ thoát ≤5 phiên ở 10% tham gia ⇒ chiết khấu 1% (0–3%). Trước CK 9.156 / sau CK 9.064.
- Upside ngoài base: CLTG VA1 còn ~490 tỷ chưa ghi nhận ⇒ +141 đ/cp (hai chiều, rev2 §5).

## E. Kịch bản (base)
| Kịch bản | ROE di sản | Trọng số | Trước CK | Sau CK |
|---|---|---|---|---|
| Xấu | 4,5% | 25% | 6.503 | 6.438 |
| Cơ sở | 8,0% | 50% | 9.156 | 9.064 |
| Tốt | 11,5% | 25% | 11.809 | 11.691 |
| **Có trọng số** | | | **9.156** | **9.064** |
Khung: Giá trị = E_di sản 31.394,5 × ROE/r + E_NT3&4 9.000 + E_dự án mới 2.740 − PV QCVN19 VA1 kỳ vọng 2.255; chia 3.067,85 tr cp.

**V6 (chỉ hiển thị, không đổi):** V_ngắn 3.487; V_dài âm (FCFE ≤ 0 do chu kỳ xây NT3&4 + phải thu EVN) ⇒ chỉ V_ngắn; C4 2.042, D2 6.590 ("chưa qua tiêu chí khoá trước, chỉ theo dõi") — rev2 §8c. Capex QCVN19 sau 2029 làm FCFE tương lai thấp hơn nữa; không đổi nhận định.
**V5 (5F):** làm đầy đủ 18/11/2026 (<12 tháng) ⇒ tái dùng: moat **NONE (kinh tế)**, rủi ro số 1 Qc/ToP LNG + pass-through nhiên liệu. Kiểm nhanh 23/11: QCVN 19 thêm một lực "nhà nước" (chi phí tuân thủ có thể không được tính vào giá) — củng cố NONE, không đổi tier.
**V1:** r 13,5%; lãi huy động 12T hiệu dụng 7,4% ngày 23/11/2026 (`deposit_rate_vn`: CCTG 12M 02/11; Big-4 6,8%) = neo 03/11 ⇒ Δ=0.

## F. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| # | Mệnh đề | P (ước lượng) | Chấm |
|---|---|---|---|
| T1 | LNST mẹ Q4/2026 trong [900; 2.000] tỷ | 0,60 | BCTC Q4/26 (~30/01/2027) |
| T2 | Phải thu KH ngắn hạn 31/12/2026 < 20.000 tỷ | 0,45 | BCTC Q4/26 |
| T3 | CFO cả năm 2026 ≥ 5.000 tỷ | 0,50 | BCTC KT 2026 |
| T4 | KH vận hành 2027 giao NT3&4 Qc ≥ 65% | 0,65 | QĐ BCT (trước 15/01/2027) |
| T5 (mới) | Báo cáo đề xuất đầu tư QCVN 19 công bố TMĐT VA1 trong [1.700; 5.200] tỷ (0,5–1,5× tương tự QTP) | 0,60 | CBTT/NQ HĐQT ~Q2/2027 |

**Đổi LÊN:** (a) EVN/BCT chấp thuận đưa chi phí khí thải vào giá điện (P100 ⇒ +8,0%); (b) TMĐT VA1 công bố < 1.700 tỷ (đã có sẵn thiết bị) ⇒ ~+4%; (c) công bố hạn PPA/giá trị sổ theo nhà máy cho thấy vốn di sản thu hồi trong ≤11 năm ⇒ chuyển §C vào base (+11…+18%); (d) 2 quý 2027 ROE mẹ cốt lõi năm hoá ≥ 11% không hồi tố và CFO ≥ LNST ⇒ ROE cơ sở 10%; (e) lãi huy động −100bp ⇒ +4,7%. **Hoặc giá ≤ 7.705**.
**Đổi XUỐNG:** EVN/BCT từ chối bù bằng văn bản (P0 ⇒ −5,8%); TMĐT > 5.200; NT3&4 lỗ/Qc 2027 < 65% hoặc ghi giảm khi quyết toán; phải thu EPTC không giảm; nghĩa vụ CPH mới; lãi huy động +100bp (−4,0%).

## G. Pháp lý / quản trị — chỉ WARNING (không vào base)
Giữ rev2 §10: Deloitte FY2025 chấp nhận toàn phần + nhấn mạnh quyết toán CPH chưa duyệt; lợi nhuận phụ thuộc quyết định hành chính (hồi tố ~40% LNTT 9T); giao dịch bên liên quan dày (giá trị **không kiểm chứng được**); PVN 79,94%. Không thấy khởi tố/xử phạt trong 83 CBTT 11/2025–11/2026.

## H. Chưa làm / giới hạn
- TMĐT QCVN 19 thực của VA1 (chờ báo cáo đề xuất Q1/2027) — đang dùng tương tự QTP.
- Hạn PPA, giá trị sổ, lợi nhuận theo nhà máy — không công bố.
- Thuyết minh bên liên quan KT25 (OCR hỏng) — chưa đọc được số.
- Tra UBCKNN trực tiếp — chưa.

## Nguồn
BCTC HN Q3/2026, KT 2025, soát xét 6T/2026: `src/` (pvpower.vn). CBTT: `src/cbtt/` — 2026-10-xx_7139_qcvn19 (19/10/2026, thầu tư vấn QCVN19), 2026-08-03_7013 (hồi tố), 2026-10-13_7130 (LNG, PPA SĐBS 02), 2026-11-10_7184 (NQ 90 KH 2026). QTP: `agents/Taylor/research/qtp_r3_envcapex_20261120/REPORT_r3.md`, `REPORT_r3b.md` (§1 pháp lý, §4 trọng số), `REPORT_r3c.md` (§2 opex). Giá sau khoá: DNSE `latest_trade` POW 13.350 (23/11/2026 11:29:50). Lãi huy động: `deposit_rate_vn.effective_deposit_rate('2026-11-23')`.
