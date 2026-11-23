# DD — POW (Tổng công ty Điện lực Dầu khí Việt Nam – CTCP, HOSE) · REV4 · 23/11/2026 · job `Taylor_20261123_050007`

> Chỉ nghiên cứu. Không đặt lệnh, không gửi email, không ghi sổ giá. Đơn vị: tỷ đồng, trừ khi ghi khác.
> Lịch sử phản biện DD_GENERAL: r1 (22/11, `REPORT.md` vòng 2, tâm 9.792) **INCONCLUSIVE** → `REPORT_rev3.md` (tâm 9.064); r2 (23/11, REPORT_rev3 md5 `72f7e933…`) **INCONCLUSIVE** → bản này. Các bản cũ giữ nguyên.
> **Khoá giả định:** `model/assumptions_POW_20261123_rev4.json` **md5 `820f22c0728ad17ee476d8b3362ba9d0`** (lint strict 0 vi phạm); rev3 lock `assumptions_POW_20261123_rev3.json` md5 `858632b79798a6b3e697b9d52482a4d7`.
> Mô hình `model/calc_rev4.py` (= calc_rev3 + tách hồi tố) + `model/model_rev3_inputs.json` + `model/model_rev4_inputs.json`; output `model/calc_rev4_output.txt` (tái lập rev3 9.156/9.064 khớp).
> **Minh bạch mù giá:** giá DNSE đã đọc ở pha sau khoá của rev3. Thay đổi duy nhất của rev4 (§A0) là sửa phương pháp do skeptic r2 yêu cầu, không do giá; hướng sửa là TĂNG tâm và nhãn không đổi.
> Nguồn: **[BCTC]** BCTC HN Q3/2026 `src/Q3_2026_BCTC_hopnhat.pdf`; **[KT25]** BCTC HN kiểm toán 2025 (Deloitte, ký 12/03/2026); **[CBTT]** `src/cbtt/<ngày>_<id>/`; **[QTP]** `agents/Taylor/research/qtp_r3_envcapex_20261120/` (FS cải tạo khí thải + pháp lý legal-vn 20/11). Số không đo được gắn **(ước lượng)**.

## 0. Kết luận

- **Giá trị nội tại, tâm = 9.387 đ/cp** (sau chiết khấu thanh khoản 1%; trước: 9.482). **Vùng [6.966; 11.808]** (xấu → tốt, trọng số 25/50/25). Mốc 0,85×tâm = **7.979**.
  So rev2 (9.792): −4,1%. Gồm hai thay đổi có nguồn: (1) **capex + opex tuân thủ QCVN 19:2024 tại VA1** là dòng tiền ra trong base (luật D3), PV kỳ vọng **2.255 tỷ = −735 đ/cp** trước CK; (2) **hồi tố sau thuế 2.454,7 tỷ** tách khỏi khối vốn di sản định giá ROE/r (0,593×), ghi theo sổ 1,0× = **+326 đ/cp** trước CK.
- r = 13,5% (lãi huy động 12T hiệu dụng 7,4% ngày 23/11 = neo), g = 0. Ở tâm P/B mẹ = 0,67 (BVPS mẹ 14.060).
- **So giá (sau khoá):** DNSE 13.350 đ (23/11/2026 11:29) = **1,42 × tâm**, trên cận trên vùng (11.808). Nhãn **ĐẮT** (không đổi). Giá ngầm định ROE di sản **13,7%/năm vĩnh viễn**.
- **Ba hạng mục hai chiều lớn nhất, đều ngoài base:** (i) VA1 có được tính chi phí khí thải vào giá điện: P0 ⇒ 8.860, P100 ⇒ 10.115; (ii) đời hữu hạn của vốn di sản ⇒ +10…+16% (§C); (iii) NT3&4 ghi giảm 30% ⇒ −9,3% (§B2). Ngay cả cận trên của (ii) (10.902) vẫn dưới giá.
- Giữ nguyên từ rev2: 9T/26 ~40% LNTT là một lần (≈2.755), LNST mẹ cốt lõi 9T 3.980–4.063; CFO 9T 2.739 vì phải thu EPTC 23.880; nợ ròng thật **7.348**; moat NONE; WARNING pháp lý nhẹ (quyết toán CPH chưa duyệt).
- **Sizing (V8, 2–4% NAV/mã):** ở giá hiện tại **không mở**. Giá ≤ 7.979 (0,85×tâm) ⇒ tối đa 2% NAV; ≤ 6.966 (cận dưới) ⇒ 3% NAV. Không đề xuất >4%.

## A0. Đính chính rev4 (từng hạng mục skeptic r2)

| # | Hạng mục skeptic r2 | Xử lý rev4 | Ảnh hưởng tâm (sau CK) |
|---|---|---|---|
| R2-1 | Hồi tố ~2.755 LNTT (phải thu đã duyệt) bị định giá 0,593× trong khối ROE/r, trong khi độ nhạy thu tiền (A10) lại tính 1,0×, không nhất quán | **Vào base:** tách 2.755 × (1 − 10,9%) = **2.454,7** khỏi E_di sản (31.394,5 → 28.939,8), ghi 1,0×. Cơ sở: khoản một lần đã được EVN/EPTC duyệt (CBTT 03/08/2026), 100% thuộc mẹ; ROE di sản 8% đã cộng phần hồi tố vào tử số các năm trước nên không tính lại vào lợi nhuận tương lai. Độ nhạy thu hồi (30% / 50% không thu được: −238 / −396 đ/cp) nay cùng cơ sở 1,0× | **9.064 → 9.387 (+3,6%)** |
| R2-2 | A2 gọi 23,8 tr MMBtu là "mức đốt thực" trong khi CBTT 13/10 chỉ ghi giao nhận 8 chuyến | **Sửa nhãn:** 23,8 tr MMBtu = **giao nhận** 9T. Lượng **đốt** ước lượng = phát 3.757 tr kWh × 6.543 BTU/kWh = **24,6 tr MMBtu/9T ≈ 32,8/năm** (ước lượng, cùng suất hao rev2) — khớp giao nhận. Kết luận ToP giữ: định hạn 20,7/năm < mức đốt | 0 |
| R2-3 | Hạn PPA / nguồn khí CM1&2, NT1 chưa kiểm chứng (trọng yếu) | Tìm thêm (web 23/11): **PPA CM1&2 ký mới với EVN ngày 15/12/2021** để tham gia thị trường điện (vietnamenergy.vn); EVN–PV Power có biên bản thống nhất phương án sửa đổi PPA (en.evn.com.vn). **Thời hạn: không công bố.** NT1: không tìm thấy. ⇒ Vẫn **không kiểm chứng được**. PPA ký lại năm 2021 làm rủi ro "hết hạn sớm không tái ký" thấp hơn, nhưng thời hạn chưa đo. Ảnh hưởng hai chiều nằm trong kịch bản xấu (ROE 4,5%: 6.966, −26%) và §C (+10…+16%) | không đổi base |
| R2-4 | Giá trị giao dịch bên liên quan (OCR hỏng) | **Không kiểm chứng được** (như rev3 A8). WARNING | không định lượng |
| R2-5 | Số CPH còn phải nộp PVN chưa biết | **Không kiểm chứng được**; độ nhạy một khoản bằng tiền lệ 728,2 ⇒ −235 đ/cp (−2,5%) | độ nhạy |
| R2-6 | QCVN 19 cho nhà máy khí 1.950 MW ngoài base | Giữ ngoài base: chưa xác lập có phải cải tạo, không có số chi phí độc lập; độ nhạy 0,5 / 1,0 tỷ/MW ⇒ −1,2% / −2,4% | độ nhạy |
| R2-7 | Trọng số bù giá P0/P50/P100 mượn từ QTP, chủ quan | Giữ (cùng khung pháp lý, cùng bên mua). Hiển thị đủ biên: P0 −5,6%, P100 +7,8%, trọng số 0,5/0,3/0,2 −0,9% (§B1) | báo kèm |
| R2-8 | Chưa bàn nhu cầu vốn chủ Quỳnh Lập (~60.000 tỷ TMĐT, CBTT 20/05) + Vũng Áng III so với VCSH mẹ 43.134 | **Bổ sung §B3.** Theo V4, dự án NPV=0 ở sổ; huy động vốn chủ mới chỉ làm thay đổi giá trị/cp nếu phát hành ở giá khác giá trị nội tại/cp. Phát hành ≥ tâm ⇒ không pha loãng giá trị (đợt 2026 phát hành 10.000 đ > tâm 9.387). Phát hành dưới tâm ⇒ pha loãng. Quy mô: vốn chủ ~30% TMĐT (ước lượng) ≈ 18.000 cho Quỳnh Lập — **không kiểm chứng được** cơ cấu vốn | không đổi base |
| R2-9 | Xác nhận VA1 đã có FGD/SCR chưa | **Không công bố**; độ nhạy quy mô ×0,5 / ×1,5 (+3,9% / −3,9%); mốc T5 | độ nhạy |

## A. Đính chính rev3 (skeptic r1) — vẫn hiệu lực

| # | Hạng mục skeptic r1 | Xử lý | Ảnh hưởng |
|---|---|---|---|
| A1 | Capex tuân thủ QCVN 19:2024 bị bỏ sót | **Vào base** (D3): VA1 1.200 MW tương tự QTP 1.200 MW (FS: TMĐT 3.485 + opex 572/năm), giải ngân 2029–31, opex từ 01/01/2032, thuế 20%, lá chắn khấu hao 15 năm; P0/P50/P100 = 0,40/0,36/0,24. PV P0 3.888 (skeptic r2 tự dựng lại 3.883); kỳ vọng 2.255 | −735 đ/cp trước CK |
| A2 | NT3&4 NPV=0 có thể quá cao | Giữ NPV=0 ở sổ (V4a). ToP: định hạn 20,7 tr MMBtu/năm < mức đốt ~32,8/năm (ước lượng, R2-2) ⇒ rủi ro cam kết vượt nhu cầu thấp. Công thức giá LNG ↔ giá Qc: **không công bố** ⇒ độ nhạy ghi giảm 15/30/50% | −4,6% / −9,3% / −15,5% |
| A3 | Phạt ROE<r vĩnh viễn trên nhà máy già | Độ nhạy, không vào base (§C) | +10,3% … +16,1% |
| A4 | r 13,5% là Ke chung | V1: r tâm 13,5%. D4 hai đầu dải Ke 12,3% ⇒ 9.861 (+5,0%), 13,4% ⇒ 9.423 (+0,4%); r 11% ⇒ 10.492 | báo kèm |
| A5 | Tiền chào bán chưa dùng 1.080 ở 1,0× vs tiền khác 0,59× | Giữ: 1.080,1 dành cho dự án (NQ 19 12/3/2026; BC tiến độ 27/7) ⇒ V4. Tiền + HTM khác 30.158 đi kèm vay 37.505 (nợ ròng dương 7.348); lãi tiền gửi đã nằm trong ROE di sản | 0 |
| A6 | Vay NH 19.438,3 vs 19.418,3 | Sửa 19.418,3 (OCR BCTC Q3 dòng 357); nợ ròng 7.347,7 | 0 |
| A9 | Quyết toán CPH | như R2-5 | −2,5% nếu xảy ra |
| A11 | Quỹ KTPL | Số dư 293,2 đã là nợ phải trả; tỷ lệ trích không công bố ⇒ độ nhạy 3%/5% LNST di sản ⇒ −1,8% / −2,9% | độ nhạy |

Skeptic r1 và r2 đều tái lập được số học: tâm, PV QCVN19, số cp 3.067.845.688 (TM23, BCTN25/KT25), VCSH mẹ 43.134,5, LNST mẹ 9T 6.434,5. ROE di sản 8% nằm **giữa dải** (skeptic r1 tự dựng ~8,0%).

## B. Định lượng các khoản

### B1. QCVN 19:2024 — VA1 (vào base)
- **Nghĩa vụ:** QCVN 19:2024/BTNMT bắt buộc với cơ sở hiện hữu từ **01/01/2032** (legal-vn 20/11, [QTP] REPORT_r3.md:91). Công ty đã khởi động: thầu "Tư vấn đánh giá kỹ thuật và lập báo cáo đề xuất đầu tư cho các nhà máy nhiệt điện của PV Power đáp ứng QCVN 19:2024 về khí thải công nghiệp", trúng thầu **CTCP Tư vấn Xây dựng Điện 1**, **2,984 tỷ** (gồm VAT), thực hiện **Q3/2026 – Q1/2027** (CBTT 19/10/2026, `src/cbtt/2026-10-xx_7139_qcvn19/post.html`). Hai CBTT skeptic r1 nêu (13/3 TB 545 và 15/4): phần text đã trích không có giá gói thầu hay TMĐT.
- **Quy mô:** TMĐT chưa công bố. Cơ sở độc lập duy nhất: **FS QTP** 1.200 MW than — TMĐT **3.485 tỷ**, O&M cố định 102,0 + điện-nước-hoá chất 470,3 (amoniac 317,4) = **572 tỷ/năm** [QTP REPORT_r3.md dòng 12; r3c §2]. VA1 = 2×600 MW ⇒ áp 1:1 (ước lượng).
- **Lịch:** giải ngân 30/45/25% năm 2029/30/31; opex từ 2032 vĩnh viễn (nhất quán với vốn di sản vĩnh viễn); thuế 20%; lá chắn khấu hao 15 năm; chiết khấu giữa năm về 30/09/2026 ở 13,5% (ước lượng lịch).
- **Bù vào giá điện:** TT12/2025 không có điều thoả thuận bổ sung chi phí (TT07/2024 Đ27.4 đã bãi bỏ); Luật Điện lực 61/2024 Đ52.4 mở lối nhưng chưa có tiền lệ nhà máy than ⇒ trọng số QTP r3b **0,40 / 0,36 / 0,24**; gánh nặng kỳ vọng = 0,58 × P0.

| Biến thể | Gánh nặng PV (tỷ) | Tâm sau CK | so tâm rev4 |
|---|---|---|---|
| **Base (kỳ vọng)** | **2.255** | **9.387** | — |
| P0 (không bù) | 3.888 | 8.860 | −5,6% |
| P50 | 1.944 | 9.488 | +1,1% |
| P100 (bù đủ) | 0 | 10.115 | +7,8% |
| Trọng số 0,5/0,3/0,2 | 2.527 | 9.299 | −0,9% |
| Quy mô ×0,5 | 1.128 | 9.751 | +3,9% |
| Quy mô ×1,5 | 3.383 | 9.023 | −3,9% |
| Opex dừng 2045 | 2.074 | 9.445 | +0,6% |
| Thuế 10,9% | 2.420 | 9.334 | −0,6% |

### B2. NT3&4 (NPV=0 sổ sách; chỉ độ nhạy)
Vốn chủ 9.000 theo sổ (rev2 §4). ToP ở A2/R2-2. Công thức giá LNG và chuyển giá nhiên liệu trong giá Qc: **không kiểm chứng được**; lỗ/lãi NT3&4 không tách được (không có báo cáo bộ phận theo nhà máy). Ghi giảm 15/30/50% ⇒ 8.951 / 8.516 / 7.935.

### B3. Vốn chủ cho Quỳnh Lập / Vũng Áng III (định tính)
Theo V4, dự án ghi NPV=0; tâm/cp chỉ đổi qua cách huy động: phát hành ≥ giá trị nội tại/cp ⇒ không pha loãng; phát hành < tâm ⇒ pha loãng tương ứng. Cơ cấu vốn, thời điểm, giá phát hành: **không công bố**. Đợt 2026: 281.024.592 cp × 10.000 đ (TM23) — trên tâm rev4.

## C. Đời hữu hạn của vốn di sản (chỉ độ nhạy)
Phần đang khấu hao (tỷ trọng s) của vốn di sản giảm tuyến tính trong T năm; vốn thu hồi tái đầu tư NPV=0 (V4); phần còn lại vĩnh viễn. TSCĐ HH Q3/26: nguyên giá 95.454,9, hao mòn luỹ kế 51.979,3, còn lại 43.475,6; KH 9T 2.905,9 [BCTC TM TSCĐ] ⇒ 11,2 năm toàn công ty; di sản ~7 năm (ước lượng, trừ NT3&4 ~23.500).

| s \ T | 7 năm | 11 năm |
|---|---|---|
| 0,50 | 10.571 (+12,6%) | 10.350 (+10,3%) |
| 0,64 | 10.902 (+16,1%) | 10.620 (+13,1%) |

(Nay E_di sản 28.939,8 nên s đo được ≈ 19.976/28.939,8 = 0,69; lưới 0,50–0,64 giữ để so với rev3, ước lượng.)
Không vào base vì: (1) không có số theo nhà máy để biết lợi nhuận có giữ ROE 8% trên vốn đang giảm không (PPA bước giảm giá cố định; mỏ khí cấp CM1&2/NT1 suy giảm); (2) s phụ thuộc giả định gán toàn bộ nợ ròng cho NT3&4; (3) ROE lịch sử 8% đã đo trên vốn có khấu hao + tái đầu tư. Chiều ngược lại (PPA hết hạn không tái ký) nằm trong kịch bản xấu.

## D. Độ nhạy khác (calc_rev4_output.txt; tâm sau CK)
- Lãi huy động ±50bp (β=1): 9.574 / 9.214 (+2,0% / −1,8%); ±100bp: 9.775 / 9.053 (+4,1% / −3,6%); β=0,5: +1,0…+2,0% / −0,9…−1,8%.
- D4: r 12,3% ⇒ 9.861; 13,4% ⇒ 9.423. r 11% ⇒ 10.492.
- ROE cả 3 kịch bản −2pp / +2pp: 8.004 / 10.771.
- Thanh khoản (V3): ADV trung vị 62 phiên **63,3 tỷ/phiên** (BQ, đo 18/11, rev2 §8b); vị thế ≤30 tỷ thoát ≤5 phiên ở 10% tham gia ⇒ chiết khấu 1% (0–3%). Trước CK 9.482 / sau CK 9.387.
- Hồi tố không thu được 30% / 50%: −238 / −396 đ/cp. CPH thêm 728,2: −235. Quỹ KTPL 3%/5%: −1,8%/−2,9%. QCVN19 nhà máy khí: −1,2…−2,4%.
- Upside ngoài base: CLTG VA1 còn ~490 tỷ ⇒ +141 đ/cp (hai chiều).

## E. Kịch bản (base)
| Kịch bản | ROE di sản | Trọng số | Trước CK | Sau CK |
|---|---|---|---|---|
| Xấu | 4,5% | 25% | 7.036 | 6.966 |
| Cơ sở | 8,0% | 50% | 9.482 | 9.387 |
| Tốt | 11,5% | 25% | 11.928 | 11.808 |
| **Có trọng số** | | | **9.482** | **9.387** |

Khung: Giá trị = E_di sản 28.939,8 × ROE/r + E_NT3&4 9.000 + E_dự án mới 2.740 + hồi tố sau thuế 2.454,7 − PV QCVN19 VA1 kỳ vọng 2.255; chia 3.067,85 tr cp.

**V6 (chỉ hiển thị):** V_ngắn 3.487; V_dài âm (FCFE ≤ 0 do chu kỳ xây NT3&4 + phải thu EVN) ⇒ chỉ V_ngắn; C4 2.042, D2 6.590 ("chưa qua tiêu chí khoá trước, chỉ theo dõi") — rev2 §8c. FCFE thấp vì đầu tư (capex), không đọc là cảnh báo đắt; capex QCVN19 2029–31 làm FCFE tương lai thấp thêm.
**V5 (5F):** làm đầy đủ 18/11/2026 (<12 tháng) ⇒ tái dùng: moat **NONE (kinh tế)**, rủi ro số 1 Qc/ToP LNG + chuyển giá nhiên liệu. Kiểm nhanh 23/11: QCVN 19 thêm chi phí tuân thủ có thể không được bù (lực "nhà nước") — củng cố NONE.
**V1:** r 13,5%; lãi huy động 12T hiệu dụng 7,4% ngày 23/11/2026 (`deposit_rate_vn`: CCTG 12M 02/11; Big-4 6,8%) = neo 03/11 ⇒ Δ=0.

## F. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| # | Mệnh đề | P (ước lượng) | Chấm |
|---|---|---|---|
| T1 | LNST mẹ Q4/2026 trong [900; 2.000] tỷ | 0,60 | BCTC Q4/26 (~30/01/2027) |
| T2 | Phải thu KH ngắn hạn 31/12/2026 < 20.000 tỷ | 0,45 | BCTC Q4/26 |
| T3 | CFO cả năm 2026 ≥ 5.000 tỷ | 0,50 | BCTC KT 2026 |
| T4 | KH vận hành 2027 giao NT3&4 Qc ≥ 65% | 0,65 | QĐ BCT (trước 15/01/2027) |
| T5 | Báo cáo đề xuất đầu tư QCVN19 công bố TMĐT VA1 trong [1.700; 5.200] tỷ | 0,60 | CBTT/NQ HĐQT ~Q2/2027 |

**Đổi LÊN:** EVN/BCT chấp thuận đưa chi phí khí thải vào giá (P100 ⇒ +7,8%); TMĐT VA1 < 1.700 (~+4%); công bố hạn PPA/giá trị sổ theo nhà máy cho thấy vốn di sản thu hồi trong ≤11 năm ⇒ chuyển §C vào base (+10…+16%); 2 quý 2027 ROE mẹ cốt lõi năm hoá ≥ 11%, không hồi tố, CFO ≥ LNST ⇒ ROE cơ sở 10%; lãi huy động −100bp (+4,1%). **Hoặc giá ≤ 7.979**.
**Đổi XUỐNG:** EVN/BCT từ chối bù bằng văn bản (P0 ⇒ −5,6%); TMĐT > 5.200; NT3&4 lỗ / Qc 2027 < 65% / ghi giảm khi quyết toán; phải thu EPTC không giảm; nghĩa vụ CPH mới; phát hành vốn cho dự án mới dưới tâm; lãi huy động +100bp (−3,6%).

## G. Pháp lý / quản trị — chỉ WARNING (không vào base)
Deloitte FY2025 chấp nhận toàn phần + nhấn mạnh quyết toán CPH chưa duyệt; lợi nhuận phụ thuộc quyết định hành chính (hồi tố ~40% LNTT 9T); giao dịch bên liên quan dày (giá trị **không kiểm chứng được**); PVN 79,94%. Không thấy khởi tố/xử phạt trong 83 CBTT 11/2025–11/2026 (chưa tra UBCKNN trực tiếp).

## H. Không kiểm chứng được / chưa làm
TMĐT QCVN19 thực của VA1 và hiện trạng FGD/SCR (chờ Q1/2027) · thời hạn PPA CM1&2 (ký 2021) và NT1, giá trị sổ/lợi nhuận theo nhà máy · giá trị giao dịch bên liên quan KT25 (OCR hỏng) · nghĩa vụ quyết toán CPH còn lại · cơ cấu vốn Quỳnh Lập/Vũng Áng III · tra UBCKNN.

## Nguồn
BCTC HN Q3/2026, KT 2025, soát xét 6T/2026: `src/` (pvpower.vn). CBTT `src/cbtt/`: 2026-10-xx_7139_qcvn19 (19/10/2026), 2026-08-03_7013 (hồi tố), 2026-10-13_7130 (LNG, PPA SĐBS 02), 2026-11-10_7184 (NQ 90), 2026-01-30_6739 (chào bán). QTP: `agents/Taylor/research/qtp_r3_envcapex_20261120/REPORT_r3.md`, `REPORT_r3b.md` (§1, §4), `REPORT_r3c.md` (§2). PPA CM1&2: https://vietnamenergy.vn/signing-power-purchase-agreement-for-ca-mau-1-and-2-power-plants-28016.html ; https://en.evn.com.vn/d6/news/Agreement-on-the-plan-for-revision-of-power-purchase-agreements-of-Ca-Mau-1-2-Power-Plants-66-163-2530.aspx . Giá sau khoá: DNSE `latest_trade` POW 13.350 (23/11/2026 11:29:50). Lãi huy động: `deposit_rate_vn.effective_deposit_rate('2026-11-23')`.
