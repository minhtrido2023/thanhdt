# DD — TCH (CTCP Đầu tư Dịch vụ Tài chính Hoàng Huy, HOSE) · **v2** · as-of 31/10/2026 · job `Taylor_20261031_151105`

> NGHIÊN CỨU READ-ONLY, trung dung. Không phải khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON, không §2.5.
> v2 = v1 (`REPORT_v1.md`, job `Taylor_20261031_141634`) + `GAPS.md` (job `Taylor_20261031_145612`) + 12 required_changes của phản biện độc lập (`SKEPTIC_20261031.md`), **mỗi đính chính đã kiểm lại trên ảnh BCTC gốc** (bảng cuối "Thay đổi v1→v2").

**Tóm tắt.** Q2 năm tài chính 2026 (01/07–30/09/2026) lãi đột biến **thật**: đợt bàn giao đầu tiên của Hoàng Huy New City-II (Thủy Nguyên).
LNST hợp nhất 750,5 tỷ, **phần cổ đông mẹ 537,7 tỷ** (NC-II nằm ở CRV, TCH hưởng 68,02%). Biên gộp BĐS 6T 51,9%.
Điểm mạnh: **không vay, không trái phiếu**; 2.993 tỷ tiền sử dụng đất 2 quỹ đất mới **đã nộp đủ**; Green River, H2 và 150 Tô Hiệu thuộc **100% công ty mẹ**; giao dịch bên liên quan nay được công bố đầy đủ.
Điểm yếu: backlog **tiêu nhanh hơn bổ sung** (NMTT NC-II −1.033 tỷ trong Q2, ở nhịp này ~3 quý), LN mẹ chuẩn hoá chỉ cho ROE ~6%, và lịch sử tuân thủ có **2 vi phạm hành chính trong 16 tháng** (UBCKNN 12/2024, Thuế Hải Phòng 04/2026).
Ở **11.850 đ** (đóng cửa 30/10/2026): P/B 0,98x VCSH mẹ, P/E TTM 14,9x.
**Giá trị hợp lý ~10.150–15.050 đ, tâm ~12.300–12.650 đ (NAV dự án, ước lượng)** ⇒ giá **NẰM TRONG vùng, ở nửa dưới (−3,5% đến −6,3% so tâm)**; giá hiện tại ngầm định chiết khấu **~20–29% so NAV dự án trước chiết khấu** (tuỳ thặng dư quỹ đất 25–55%).
Tâm v2 cao hơn v1 (~11.600–11.950) vì 3 sửa của phản biện (§8c): gán dự án đúng pháp nhân, chiết khấu holding chỉ áp phần qua công ty con, thặng dư cơ sở đặt đối xứng quanh biên lịch sử thay vì ở cận thận trọng.
WARNING quản trị/tuân thủ: **trung bình** (§6). Đổi nhận định hai chiều ở §9.

> **Nguồn** (số BCTC đọc từ ẢNH trang render pymupdf, sổ đọc `calc/notes_read.md`):
> **[Q2HN]** BCTC hợp nhất 01/04–30/09/2026 (ký 29/10/2026, **CHƯA soát xét**) · **[RIÊNG]** BCTC riêng cùng kỳ · **[GT]** CV giải trình 42/2026/TCH-CV 29/10/2026 · **[Q1HN]** BCTC hợp nhất Q1FY26 ·
> **[KT25]** BCTC hợp nhất FY25 (01/04/2025–31/03/2026) **đã kiểm toán, AASC, chấp nhận toàn phần, ký 25/06/2026** · **[NQ26]** NQ ĐHĐCĐ 2026 (24/07/2026) · **[BCTN25]** BCTN 2025 · **[QT6T26]** BC quản trị 6T 2026 ·
> **[QĐ1020]** QĐ xử phạt thuế 1020/QĐ-XPHC 03/04/2026 · **[BQ]** `tav2_bq.ticker` tới 30/10/2026 · **[DNSE]** OHLC read-only · **[SHS]** báo cáo cập nhật 08/08/2026 (bên bán, chỉ dùng số dự án/Q1; không dùng giá mục tiêu) · **[WEB]** báo chí, gắn nhãn.
> Số tự tính: `calc/tch_valuation_v2.py` → `calc/tch_valuation_v2_out.txt` (v1: `tch_valuation.py`; bổ sung: `gaps_calc.py`).
> **Đơn vị: tỷ đồng** trừ khi ghi khác. Niên độ kết thúc 31/3: **"Q2FY26" = 01/07–30/09/2026**; "6T" = 01/04–30/09/2026.

---

## 1. Kết luận và vùng giá

| Vùng giá (đ/cp, 1.003,31 tr cp) | Đọc |
|---|---|
| < ~10.150 | chỉ hợp lý nếu kịch bản tiêu cực thành hiện thực: biên quỹ đất còn lại về ~25% (thặng dư 15%), chiết khấu tổng ~28% |
| 10.150 – 15.050 (hiện 11.850) | **trong vùng**; tâm ~12.300–12.650 (ước lượng); giá **dưới tâm 3,5–6,3%** |
| > ~15.050 | đòi hỏi thặng dư quỹ đất ≥ 55% (biên gộp ~47%) **và** chiết khấu tổng ≤ 10%, tức HH1–HH4 + quỹ đất mới bán tốt và thị trường bỏ chiết khấu quản trị |

**Kịch bản** (NAV dự án, `tch_valuation_v2_out.txt`):

| Kịch bản | P | Biên ròng backlog | Thặng dư HTK (≈ biên gộp) | CK holding (phần qua cty con) / quản trị (toàn bộ) | Giá trị |
|---|---|---|---|---|---|
| Tích cực | 0,25 | 36% | 55% (~47%) | 10% / 5% | **~15.050** |
| Cơ sở | 0,50 | 33,5% | 40% (~40%) | 20% / 10% | **~12.700** |
| Tiêu cực | 0,25 | 30% | 15% (~24%) | 30% / 15% | **~10.150** |
| **Trọng số** | | | | | **~12.650** (nghiêng theo đọc ngành 0,35/0,45/0,20: **~12.280**) |

Phép thử chéo (đều ước lượng):
- SOTP hỗn hợp (mẹ theo sổ + CRV 38,19% theo sổ + HHS 58,31% theo giá thị trường) **~11.200–11.450**.
- P/B trung vị 15 DN BĐS 0,72x **cùng cơ sở BQ** (BV BQ 13.165 đ/cp) ⇒ **~9.480**; TCH theo cơ sở này 0,90x, cao hơn trung vị ~25%.
- P/E chuẩn hoá 10–16x × EPS chuẩn hoá 675–775 ⇒ **6.750–12.400** (13x × 729 ≈ 9.480).
- Cả 3 phép thử thị trường/bội số nằm **dưới** NAV dự án vì chúng không cộng thặng dư quỹ đất; NAV dự án dựa vào tham số tự đặt. Đây là căng thẳng chính của định giá.

**Ở ±5% quanh giá (11.260–12.440):** kết luận "trong vùng, nửa dưới" không đổi. Giá chỉ "trên tâm" khi > ~12.650.

**Gỡ ngộ nhận "lãi ×13, giá lại giảm":** ×13 là LNST **hợp nhất** so với quý gốc rất thấp (Q2FY25 56,3); LN mẹ Q2 537,7; LN mẹ TTM 796 vẫn **thấp hơn FY24** (855). Đây là chu kỳ bàn giao trở lại, chưa phải nền lợi nhuận mới.

## 2. Kiểm lại số đọc ban đầu (từng số)

| Số | BCTC/nguồn | Kết luận |
|---|---|---|
| GT: DT HN Q2 1.960,89 (+566,76%), LNST 750,54 (+1.332%); riêng DT 57,61 / LNST 40,14 | [GT] ✓; KQKD [Q2HN in 7–8] | ✓ |
| Tiền 1.035,4; HTM NH 2.203,2; HTK 15.257,7; NMTT 5.599,8; 0 vay | [Q2HN in 4–6; TM3,4,9,16,36] | ✓ (HTM DH 57,8) |
| VCSH 15.279,7; NCI 3.120,5; vốn góp 10.033,1 (cp thưởng 10:1 xong 10/09/2026) | [TM21] | ✓ |
| BQ Q(04–06/2026) LN mẹ 125,4 | [Q2HN] 6T−Q2 = 125,42 | ✓ |
| BQ "(01–03/2026) 52,4" | là 10–12/2025; 01–03/2026 = 80,5 | ✗ nhãn |
| FY25 LNST ~256 (báo) | [KT25] HN **259,20**; mẹ **211,06** | dùng số kiểm toán |
| KH FY26 DT 5.000 / LNST 2.000 | **[NQ26 tr.34] bảng "chỉ tiêu HỢP NHẤT"**; [BCTN25 tr.27] | ✓ hợp nhất (LN mẹ hàm ý ~1.400–1.450, ước lượng) |
| Giá 11.850 (30/10, −2,87%), KL 14,04 tr | [BQ]/[DNSE]; 2,4× TB 20 phiên | ✓ |
| "Phạt 380 triệu" | = 295 (TCH, QĐ 1357/QĐ-XPHC 05/12/2024) + 85 (công ty khác) cùng đợt | đính chính; **nhưng có án thứ 2 khác: QĐ thuế 1020 (§6d)** |

## 3. Lợi nhuận Q2 và 6T đến từ đâu, có bền không

### 3a. KQKD hợp nhất [Q2HN in 7–8]

| | Q2FY26 | Q2FY25 | 6T FY26 | 6T FY25 |
|---|---|---|---|---|
| DT thuần | 1.958,18 | 345,98 | 2.409,13 | 736,28 |
| LN gộp (biên) | 956,32 (**48,8%**) | 89,48 (25,9%) | 1.096,58 (45,5%) | 202,28 (27,5%) |
| DT tài chính | 74,68 | 40,18 | 175,46 | 76,32 |
| CP bán hàng / QLDN | 77,13 / 21,85 | 31,60 / 28,44 | 107,27 / 40,17 | 67,59 / 50,10 |
| LNTT | 928,53 | 72,69 | 1.129,49 | 150,45 |
| Thuế (ETR) | 177,99 (19,2%) | 16,35 | 215,19 (19,1%) | 37,88 |
| LNST HN | 750,54 | 56,34 | 914,29 | 112,57 |
| **LNST mẹ** / NCI | **537,73** / 212,81 | 40,21 / 16,13 | **663,14** / 251,15 | 78,09 / 34,48 |

Không có công ty liên kết, chi phí lãi vay 0, LN khác Q2 3,14.

### 3b. Theo mảng — 6T [TM23, TM25]; Q1 lấy từ [Q1HN] (cột so sánh) và [SHS]

| Mảng | DT 6T FY26 (FY25) | Biên gộp 6T (FY25) | Q2 ≈ 6T − Q1 |
|---|---|---|---|
| Bán BĐS | 1.954,52 (220,77) | **51,9%** (51,0%) | DT ~1.751 (Q1 ~203) |
| Ô tô tải/đầu kéo & linh kiện (HHS) | 359,47 (427,83) | 13,2% (13,9%) | ~157 — giảm; chưa có giải trình chính thức |
| Cho thuê BĐS & DV | 97,23 (87,68) | 40,5% | |

**DT BĐS Q2 gần như toàn bộ từ công ty con (NC-II):** [RIÊNG] công ty mẹ chỉ có DT Q2 57,61 (gồm cho thuê) ⇒ dự án của mẹ (Green River, H2) **gần như không bàn giao trong Q2**. Vì vậy NC-II ≈ **1.650–1.750** DT Q2 (ước lượng; v1 ước 1.000–1.200 là quá thấp).
- NMTT NC-II giảm 1.033 (gồm VAT, ≈957 ex-VAT); phần còn lại ~700–750 DT là tiền thu lúc bàn giao/phải thu (ước lượng).
- ⇒ **Nhịp tiêu NMTT NC-II −1.033/quý ⇒ 3.099 còn lại hết sau ~3 quý** nếu không có bán mới bù.

### 3c. Bao nhiêu là một lần / dồn
- **Không có lãi một lần** kiểu thoái vốn/đánh giá lại (thanh lý BĐSĐT +3,3; LN khác 4,8).
- **Tính dồn chu kỳ bàn giao:** Q2 là đợt bàn giao đầu tiên của NC-II (cọc thu từ FY24–FY25). LNST quý ~700+ **không phải mức chạy bền**; sau NC-II thấp tầng phụ thuộc HH1–HH4 (2.494 căn [SHS], đang làm hầm) và tốc độ bán.
- **Lãi tiền gửi** 173,5 trong 6T (~15% LNTT) sẽ giảm: tiền + HTM đã giảm 2.910 vì chuyển vào đất.
- **Giá vốn trích trước:** số dư trích trước chi phí xây dựng chỉ 18,95 [TM18] so giá vốn BĐS 6T 940. **Chưa kiểm được dự toán tổng** (dự toán thấp nằm trong HTK, không hiện ở chi phí phải trả) ⇒ rủi ro quyết toán sau còn mở.
- **CPBH chờ phân bổ** 447,35 [TM14] (NC-II 228,2; Green River 124,9; H2 76,7; H1 17,2) sẽ chảy vào CPBH khi bàn giao. Tỷ lệ trên NMTT: NC-II 7,4%, Green River 6,8%, H2 12,4% ⇒ **biên ròng sau thuế của backlog ~33–34%**, không 36%.

### 3d. Vì sao LN công ty mẹ riêng 40 tỷ còn hợp nhất 750 tỷ
- NC-II và I.14 nằm ở **CRV/Đại Lộc** (thuế TNDN 6T: CRV 162,64; Đại Lộc 8,98 [TM32]). Lãi này lên TCH qua cổ tức CRV (TCH hưởng 68,02%).
- **Green River, H2 Commerce và 150 Tô Hiệu là HTK của công ty MẸ** [RIÊNG TM9 in 22: 5.551,8 = TP Green River 759,6 + CPDD Green River 2.557,5, H2 555,5, 150 Tô Hiệu 1.677,5, khác 1,7]. Lãi các dự án này về thẳng cổ đông TCH, **không qua tầng thiểu số**.
- Q2 mẹ chưa bàn giao dự án và chưa nhận cổ tức không thường xuyên từ con [GT] ⇒ LN riêng thấp.

### 3e. LN mẹ theo năm tài chính [BQ ticker_financial cộng quý; khớp KT25]

| FY21 | FY22 | FY23 | FY24 | FY25 | 6T FY26 | TTM |
|---|---|---|---|---|---|---|
| 400,5 | 246,0 | 743,8 | 855,0 | 211,0 | 663,1 | 796,0 |

Rất lồi theo chu kỳ bàn giao. TB FY21–25 491 (ROE ~4%). TB FY23–FY26E 677–777 tuỳ FY26E 900/1.117/1.300 (ROE **5,6–6,4%**).

## 4. Ghi nhận doanh thu, backlog, kế hoạch FY26
- **Ghi nhận khi bàn giao** [TM2.25], không POC. Tiền khách ứng nằm ở NMTT.
- **NMTT 30/09/2026 = 5.599,82** [TM16]: NC-II 3.099,20 (CRV) · Green River 1.837,75 (mẹ) · H2 617,83 (mẹ) · H1 38,15 · khác 6,88.
- **Backlog:** NMTT ex-VAT ≈ 5.185 (VAT bình quân ~8%, ước lượng). BCTC không công bố giá trị hợp đồng ký. Nếu khách đã trả ~70% (giả định, không có nguồn), tổng giá trị hợp đồng ≈ 7.400, **phần chưa thu ≈ 2.200**.
- **Kế hoạch FY26** (chỉ tiêu HỢP NHẤT [NQ26 tr.34]): DT 5.000 / LNST 2.000 / cổ tức dự kiến 10% (chưa rõ hình thức). 6T đạt **DT 48,3%**, **LNST HN 45,7%**; H2 FY26 cần DT 2.586, LNST 1.086.
  - Ở nhịp Q2 (DT BĐS ~1.700/quý, LNST/DT 38,3%), 2 quý cho ~1.300 LNST HN (ước lượng) ⇒ **đạt được nếu NC-II giữ nhịp bàn giao**.
  - ⇒ P(DT ≥ 5.000) ~0,60; P(LNST HN ≥ 2.000) ~0,50 (ước lượng; v1 0,45/0,40 — nâng vì DT NC-II Q2 lớn hơn v1 ước).
- **Tốc độ bổ sung backlog** (tín hiệu xấu): ΔNMTT theo quý +2.643 (Q2FY25) → +775 → +368 (Q1FY26) [SHS] → **−893 (Q2FY26)** [Q1HN→Q2HN].
  - Chưa có số doanh số ký mới. HH1–HH2 dự kiến mở bán Q3/2026 [SHS] nhưng BCTC 30/09 chưa có NMTT cho HH.

## 5. Bảng cân đối và dòng tiền

### 5a. Net cash

| Khoản | 30/09/2026 | 31/03/2026 |
|---|---|---|
| Tiền + TĐT | 1.035,35 | 1.694,17 |
| HTM ngắn + dài hạn | 2.203,19 + 57,78 | 4.228,14 + 284,30 |
| **Tiền + HTM (hợp nhất)** | **3.296,3** (3.285 đ/cp) | 6.206,6 |
| — trong đó công ty mẹ [RIÊNG] | 2.244,2 | |
| — **phần mẹ** (mẹ + 68% phần con, ước lượng) | **~2.960 (~2.950 đ/cp)** | |
| Vay / trái phiếu | **0 / 0** | 0 (FY25 trả hết 923,5) |
| Nợ tài chính khác (phải trả NB/khác, TM36) | 1.086,8 | |
| Thuế phải nộp | 198,8 | |
| **Tiền + HTM − nợ tài chính − thuế** | **~2.010 (~2.000 đ/cp)** | |

- NMTT 5.600 phải "trả" bằng nhà/đất; chi phí xây dựng còn lại cho phần đã bán **không công bố**.
- Tiền gửi ở 8+ ngân hàng [TM4]. **"NH TMCP Sài Gòn Tài Lộc" = Sacombank** (tên thương mại mới theo QĐ 36/QĐ-QLGS4 NHNN 01/06/2026; bản tiếng Anh TM4 "Saigon Fortune") — không phải rủi ro đối tác. Lưu ý: 678,3 tỷ (21% tiền + HTM) là khoản **gần như không rút** (694,2 → 678,3) trong khi HTM khác giảm 2.025; không thấy cầm cố trong TM4/TM22.

### 5b. HTK tăng 3.653 trong 6T [TM9(*), RIÊNG TM9, TM17]

| Dự án (pháp nhân) | 30/09/26 | 31/03/26 | Δ |
|---|---|---|---|
| 150 Tô Hiệu, Lê Chân (**mẹ**) | 1.677,51 | 4,40 | **+1.673,1** |
| Lô I.14 Bắc Sông Cấm, Thủy Nguyên (Đại Lộc, qua CRV) | 1.328,75 | 0 | **+1.328,8** |
| New City-II (CRV) | 7.390,37 | 7.230,42 | +160,0 |
| Green River (**mẹ**; CPDD + TP) | 3.317,07 | 2.995,59 | +321,5 |
| H2 Commerce (**mẹ**) | 555,53 | 512,78 | +42,8 |
| TP khác (H1 299,5; Gold Tower; N01) + khác | ~362 | ~372 | |

- **Tiền SDĐ đã nộp 6T 2.992,90** [TM17]: Q1 1.326,27 (khớp giá đấu I.14 1.322 [SHS]); Q2 1.666,63 (khớp 150 Tô Hiệu). Tiền + HTM giảm 2.910 đi gần trọn vào đất — **không phải tiền biến mất**.
- Pháp lý quỹ đất: I.14 giao đất 23/07/2026 [SHS]; 150 Tô Hiệu GPMB xong, bắt đầu thi công [TM9]; NC-II một phần là **đất thuê trả hằng năm** 26.664,2 m² tới 2073 [TM22b]; 17B Bà Triệu (HN) 243,18 đang làm thủ tục [TM10]. **Không có** dự phòng giảm giá HTK BĐS.
- Trả trước người bán 565,0 [TM6] cho nhà thầu (Hòa Bình 162,5; Thủy Ngân 103,9; Cảng Kim Tân 73,7 — chưa xác định pháp nhân).

### 5c. Dòng tiền [Q2HN in 9–10; KT25]

| | 6T FY26 | 6T FY25 | FY25 | FY24 |
|---|---|---|---|---|
| LN trước thay đổi VLĐ | 978,1 | 106,5 | 189,4 | 1.456,6 |
| ΔHTK | −3.653,4 | −871,0 | −3.005,0 | +1.274,1 |
| ΔPhải trả (gồm NMTT) | −692,9 | +2.843,0 | +5.947,1 | −548,9 |
| **CFO** | **−3.078,5** | +1.559,2 | **+2.030,0** | +1.467,7 |
| CFI | +2.419,7 | −2.513,9 | −3.262,6 | −872,5 |
| CFF | 0 | +2.246,6 | +1.655,7 (phát hành 2.004,3) | +187,6 |

- CFO FY25 + 6T FY26 ≈ −1.050; bỏ tiền đất mới (~3.000) thì CFO lõi dương. CFO luỹ kế FY24→6T FY26 / LNST HN = 0,18 (cờ, nguyên nhân rõ).
- **Vốn chào bán 2025 (2.004,6 tỷ)**: đến 25/09/2026 đã dùng 1.139,1 (Green River 938,9/1.200; H2 200,3/804,6), còn 865,5; **không đổi mục đích** [BC sử dụng vốn 29/09/2026]. Tiền đất mới không lấy từ nguồn này.

## 6. Cấu trúc tập đoàn, cổ đông, quản trị & pháp lý — ⚠️ WARNING (mức trung bình)

### 6a. Cấu trúc [TM1.5]

| Công ty con | Lợi ích | Biểu quyết | Mảng |
|---|---|---|---|
| **CRV** (niêm yết HOSE 10/10/2025) | **68,02%** | 96,72% | BĐS (NC-II; I.14 qua Đại Lộc) |
| **HHS** (niêm yết HOSE) | **58,31%** | 58,31% | ô tô (độc quyền xe đầu kéo International) |
| Tô Hiệu; Thịnh Phát; Thịnh Hiệp | 99,98%; 96,33%; 95,84% | | XD/BĐS |

- Biểu quyết tại CRV = 38,19% trực tiếp + 35,26% qua HHS + 8,44% qua Hoàng Giang + 7,47% qua HHS Capital + 7,37% do một nhóm cổ đông khác **uỷ quyền** cho HHS. **Bỏ phần uỷ quyền vẫn còn 89,35%** ⇒ kiểm soát CRV **không phụ thuộc** uỷ quyền (cơ sở: biểu quyết theo TM1.5; báo chí Q1/2025 nêu nhóm nắm ~81,7% **vốn** CRV — khác cơ sở).
- Còn mở: danh tính nhóm uỷ quyền 7,37% (không tìm được trong BCTN25/NQ26/QT6T26/5 trang báo) và **free float độc lập của CRV chỉ ~3%** (CRV khớp lệnh 24/62 phiên 03/08–30/10/2026, ~0,8 tỷ đ/3 tháng [DNSE]); chuẩn duy trì niêm yết CRV chưa kiểm.

### 6b. Cổ đông [BCTN25 tr.21, 32; NQ26]
- Ông **Đỗ Hữu Hạ** (Chủ tịch) 30,17% + **CTCP HH Finance 5,81%** — ông Hạ là Chủ tịch kiêm TGĐ HH Finance từ 06/2025 ⇒ **người có liên quan**. Nhóm kiểm soát **35,99%** = **71,2% số phiếu dự ĐHĐCĐ 2026** (đại hội chỉ có 50,51% cổ phần dự).
- Nước ngoài 10,51% (22/06/2026), room 51%. **Nhóm Dragon Capital bán ròng xuống 4,71%, không còn là cổ đông lớn từ 15/06/2026** (6 báo cáo từ 12/2025).
- HĐQT 5 người (2 người họ Đỗ), 1 độc lập. **Trưởng BKS kiêm Kế toán trưởng công ty con (Tô Hiệu)**; ĐHĐCĐ uỷ quyền **TGĐ** chọn kiểm toán ⇒ cơ chế giám sát độc lập yếu.

### 6c. Lịch sử pha loãng
Số cp 399,2 tr (2021) → 618,7 → 668,2 → 868,7 → 912,1 → **1.003,3 tr (2026)** = **×2,5 trong 5 năm** [BQ OShares tới 912,1; TM21 cho 1.003,3].
- 2025 phát hành 200,46 tr cp ở **mệnh giá** (2.004,6 tỷ). Cùng kỳ chi 1.302,5 tỷ "thay đổi tỷ lệ lợi ích tại công ty con", trả cao hơn giá trị sổ sách ~452 tỷ [TM21a].
- 2026: cp thưởng 10:1 (cổ tức FY25 không có tiền). EPS FY24 1.219 đ → TTM ~793 đ.

### 6d. Pháp lý / CBTT / tuân thủ

| Sự kiện | Nguồn | Mức |
|---|---|---|
| **QĐ 1020/QĐ-XPHC ngày 03/04/2026, Thuế TP Hải Phòng**: "khai sai căn cứ tính thuế dẫn đến thiếu số thuế TNDN phải nộp" (đ.a k1 Đ142 Luật QLT; k1a Đ16 NĐ 125/2020). Phạt 2,735 + truy thu 13,676 + chậm nộp (tới 02/04/2026) 3,798 = **20,21 tỷ**; giảm GTGT còn khấu trừ 0,108 tỷ. Không tình tiết tăng nặng/giảm nhẹ. Căn cứ biên bản kiểm tra 02/04/2026 theo QĐ 1504/QĐ-HPH 26/08/2025. **QĐ không nêu kỳ tính thuế bị kiểm tra** (đã đọc đủ 3 trang QĐ). CBTT 07/04/2026 | [QĐ1020] | **WARNING** — vi phạm thuế ở công ty mẹ; ~20 đ/cp, 0,13% VCSH HN |
| **QĐ 1357/QĐ-XPHC 05/12/2024 (UBCKNN): 295 tr đ** = 92,5 (không CBTT giải trình chênh lệch LNST BCTC riêng 2020–21) + 65 (BC quản trị 2021–23 không liệt kê giao dịch bên liên quan) + 137,5 (HĐ thuê VP với 2 công ty liên quan, HĐQT duyệt muộn 24/07/2023); QĐ 1358 buộc cải chính BCTN 2021 | [WEB] Nhân Dân, Báo Đầu Tư | WARNING — CBTT/thủ tục, không hình sự |
| Kiểm toán FY25 AASC chấp nhận toàn phần; AASC tiếp tục FY26 (HĐ 10/08/2026, gồm soát xét) | [KT25], CBTT 10/08/2026 | sạch |

**Đã khắc phục (tích cực, có bằng chứng):**
- BC quản trị 6T 2026 [QT6T26 tr.9–15] và BCTN25 tr.37 **liệt kê giao dịch bên liên quan**: thuê VP với các công ty con (viện dẫn công khai NQ 06/2023 — chính NQ bị phạt), CRV trả cổ tức 153,66 tỷ (FY25), TCH mua cp phát hành thêm của HHS 800 tỷ và CRV 166,47 tỷ, chuyển nhượng HĐ tiền gửi.
- 3 NQ HĐQT về giao dịch bên liên quan được CBTT riêng (16/04, 23/06, 21/07/2026): **TCH cho CRV vay ≤ 500 tỷ** (đã giải ngân 30 tỷ), **cho HHS vay ≤ 100 tỷ**, lãi do TGĐ quyết.
- Mọi giao dịch đều **nội bộ tập đoàn** ⇒ BCTC hợp nhất ghi "bên liên quan: –" là **đúng** (đã loại trừ khi hợp nhất), không phải dấu hiệu tái phạm. QT6T26: giao dịch với đối tượng khác "Không"; giao dịch cp người nội bộ "Không".

**Còn mở:**
1. Khoản vay nội bộ có lãi do TGĐ quyết **chuyển giá trị giữa cổ đông TCH và cổ đông thiểu số CRV/HHS** (quy mô hiện nhỏ).
2. **EPS 6T trình bày sai**: tử số 914,29 là LNST hợp nhất (911 đ); đúng theo TM2.29 là 663,14/1.003,31 = **661 đ** (cao hơn 38%). Lỗi trên BCTC chưa soát xét — kiểm ở bản soát xét (M1).
3. Pruksa International tạm ứng 59,43 tỷ treo nhiều năm [TM19].
4. Giao dịch bên liên quan **ngoài** tập đoàn (HH Finance, gia đình ông Hạ): không thấy trong QT6T26/BCTN25; chưa tra ssc.gov.vn và CBTT của HHS/CRV.

⇒ **WARNING trung bình: "lịch sử tuân thủ (CBTT + thuế), 2 cơ quan – 2 loại vi phạm trong 16 tháng"**, đồng thời trục từng bị phạt (công bố bên liên quan) đã được khắc phục. Không có dấu hiệu gian lận/khởi tố/kiểm toán ngoại trừ.

## 7. Kiểm toán
- FY25 **AASC** (BC 250626.006/BCTC.KT7, ký 25/06/2026): chấp nhận toàn phần, không nhấn mạnh; ký sát hạn 90 ngày.
- **6T FY26 CHƯA soát xét** ⇒ mốc M1. Năm ngoái BCTC bán niên (website ghi "đã kiểm toán") công bố 28/11/2025.
- Tổng 4 quý LN mẹ FY25 theo BQ 211,0 khớp kiểm toán 211,06 ⇒ không thấy điều chỉnh trọng yếu ở LN mẹ.

## 8. Định giá (giá 11.850 đ, đóng cửa 30/10/2026 [BQ, DNSE]) — `calc/tch_valuation_v2_out.txt`

### 8a. Bội số

| | Giá trị | Ghi chú |
|---|---|---|
| P/B (VCSH mẹ 12.159,1; BVPS 12.119) | **0,98x** | cơ sở BQ (BVPS 13.165): 0,90x |
| P/E TTM mẹ (796,0; EPS 793) | **14,9x** | BQ 39,8 — chưa nạp Q2FY26 |
| P/E chuẩn hoá FY23–FY26E (EPS 675–775) | **15,3–17,6x** | FY26E 900/1.117/1.300 (ước lượng) |
| Tiền + HTM phần mẹ / cp | ~2.950 đ (25% giá) | sau nợ tài chính + thuế (HN): ~2.000 đ |
| ROE chuẩn hoá | 5,6–6,4% | VCSH phình vì quỹ đất mới chưa sinh lãi |

**Comp** [BQ 30/10/2026; P/B, P/E do BQ tính — **cùng cơ sở BQ**]: KDH 0,86/9,8 · NLG 0,73/17,3 · PDR 0,89/18,4 · DIG 0,79/10,5 · DXG 0,61/66,7 · HDG 0,72/6,5 · CEO 1,00/34,6 · HDC 0,86/13,4 · NVL 0,51/7,9 · KHG 0,38 · SCR 0,32 · DXS 0,31.
- P/B trung vị 15 tên (bỏ VHM) **0,72**. TCH theo BV BQ (14.481 đ × 912,1 tr cp = 13.208 tỷ, chia 1.003,3 tr cp = 13.165 đ/cp) ⇒ **0,90x, cao hơn trung vị ~25%**; ở 0,72x ⇒ ~9.480 đ. BV của BQ chưa truy nguyên cơ sở; 7/15 peer yếu hoặc không thuần chủ đầu tư ⇒ phép thử phụ.
- Mức cao hơn trung vị có lý do: không vay, biên ~50%, quỹ đất sạch đã nộp tiền SDĐ.

### 8b. Chi phí vốn
- β tuần 2 năm vs VNINDEX **1,23**, Blume **1,16** (n=100). rf chuẩn hoá 6,75%; ERP nội địa 4,8–5,7% ⇒ **Ke 12,3–13,4%** (tâm ~12,85%; dải rộng 10,5–14,0%). Thống nhất toàn báo cáo.
- P/B hợp lý theo (ROE−g)/(Ke−g), g=3%: ROE 6% ⇒ 0,29–0,32x; 10% ⇒ 0,67–0,75x; 12% ⇒ 0,87–0,97x ⇒ **giá hiện tại ngầm định ROE bền ~12%**, gấp đôi mức chuẩn hoá. Khoảng chênh chỉ biện minh được nếu sổ sách **đánh giá thấp quỹ đất** ⇒ dùng NAV dự án làm phương pháp chính (dòng tiền BĐS có thời hạn).

### 8c. NAV dự án (ước lượng; mọi tham số tự đặt)
NAV = [VCSH trực tiếp của mẹ + lãi backlog/thặng dư dự án của mẹ (100%)] + [VCSH mẹ trong các công ty con + lãi backlog/thặng dư dự án qua CRV (68,02%)] − chiết khấu.

| Thành phần | Cơ sở tính |
|---|---|
| VCSH trực tiếp của mẹ | [RIÊNG] VCSH 10.530,2 − đầu tư con thuần 4.571,6 = **5.958,6** |
| VCSH mẹ qua công ty con | 12.159,1 − 5.958,6 = **6.200,5** |
| Backlog (NMTT ex-VAT) × biên ròng sau thuế × phần × PV | NC-II 68,02% PV 0,886 (~1 năm); Green River 100% PV 0,834 (~1,5 năm); H2 100% PV 0,785 (~2 năm) |
| HTK còn lại sau giá vốn backlog | mẹ 4.458 (100%) · CRV 7.339 (68,02%) · khác 340 (80%, ước lượng) = 12.137; × thặng dư × PV 0,617 (~4 năm) |
| Chiết khấu holding | **chỉ** phần qua công ty con (2 tầng niêm yết CRV/HHS; HHS thị trường định giá ~4.082 tỷ ≈ phần HHS trong VCSH CRV ~3.880, ước lượng) |
| Chiết khấu quản trị | toàn bộ (lịch sử tuân thủ, pha loãng, vay nội bộ lãi do TGĐ quyết). **Không** tính "NCI" (đã loại khi lấy phần mẹ) |

| | Tiêu cực | Cơ sở | Tích cực |
|---|---|---|---|
| Biên ròng sau thuế backlog | 30% | 33,5% | 36% |
| Thặng dư sau thuế trên HTK (≈ biên gộp) | 15% (~24%) | 40% (~40%) | 55% (~47%) |
| CK holding / quản trị | 30% / 15% | 20% / 10% | 10% / 5% |
| NAV trước CK (đ/cp) | 14.100 | 15.720 | 16.710 |
| CK hiệu dụng tổng | 28,0% | 19,2% | 9,9% |
| **Giá trị / cp** | **~10.150** | **~12.700** | **~15.050** |

Trọng số 0,25/0,50/0,25 ⇒ **~12.650 đ** (giá −6,3%); nghiêng đọc ngành 0,35/0,45/0,20 ⇒ **~12.280 đ** (giá −3,5%).

**Quy đổi thặng dư ↔ biên gộp** (CPBH 10% DT, thuế 20%): s·(1−g) = 0,8·(g−0,1) ⇒ g = (s+0,08)/(s+0,8). s=10% ↔ g 20%; 25% ↔ 31,4%; 40% ↔ 40%; 55% ↔ 46,7%; **biên lịch sử 51,9% ↔ s ≈ 70%**. (v1 viết "25% ≈ biên 40–45%" là sai.)

**Chiều lệch từng giả định (luật trung lập):**
- Thặng dư cơ sở 40% đặt **giữa** biên lịch sử (51,9% ⇔ s≈70%, thuận lợi, hợp lý cho đất cũ thấp tầng) và quỹ đất mới mỏng hơn (150 Tô Hiệu tiền đất ~103 tr/m² đất, ~30–43% giá bán, ước lượng ⇒ s~10–25%, bất lợi). Quỹ đất mới ~25% HTK còn lại ⇒ bình quân theo tỷ trọng ~45%; dùng 40% vì NC-II còn lại gồm cả cao tầng HH1–HH4 (biên thường thấp hơn thấp tầng) ⇒ lệch **nhẹ về thận trọng**.
- HTK là chi phí đến nay, chưa gồm chi phí hoàn thành tương lai ⇒ áp thặng dư lên HTK có thể **thiếu** lợi nhuận tuyệt đối (lệch thận trọng) nhưng chưa kiểm được dự toán (lệch lạc quan nếu dự toán thấp).
- PV 4 năm cho toàn bộ HTK còn lại (Green River hạn Q4/2028, H2 Q4/2027 lệch thận trọng; I.14/150 Tô Hiệu có thể > 4 năm lệch lạc quan).
- Phần mẹ khác 80% cho HTK 340 không xác định pháp nhân: ảnh hưởng < 30 đ/cp.

**Ma trận thặng dư × chiết khấu tổng hiệu dụng (đ/cp; biên ròng backlog 33,5%):**

| Thặng dư (biên gộp) | CK 0% | 10% | 15% | 20% | 25% | 30% | CK ngầm định trong giá 11.850 |
|---|---|---|---|---|---|---|---|
| 10% (~20%) | 13.928 | 12.535 | 11.839 | 11.142 | 10.446 | 9.749 | 14,9% |
| 25% (~31%) | 14.824 | 13.342 | 12.600 | 11.859 | 11.118 | 10.377 | **20,1%** |
| 40% (~40%) | 15.720 | 14.148 | 13.362 | 12.576 | 11.790 | 11.004 | **24,6%** |
| 55% (~47%) | 16.616 | 14.955 | 14.124 | 13.293 | 12.462 | 11.631 | **28,7%** |
| 70% (~52%) | 17.513 | 15.761 | 14.886 | 14.010 | 13.134 | 12.259 | 32,3% |

⇒ **Giá 11.850 ngầm định chiết khấu ~20–29% so NAV dự án** (thặng dư 25–55%). NAV trước chiết khấu ở mọi dòng **> sổ sách (12.119 đ/cp)**: kết luận không đơn thuần là "giá ≈ sổ sách".
- Độ nhạy: ±5 điểm % chiết khấu quản trị ≈ ±700 đ/cp; ±15 điểm % thặng dư ≈ ±720 đ/cp (ở CK 20%); Ke 12,3–13,4% chỉ đổi ±45 đ/cp (PV ngắn). **Chiết khấu là tham số nhạy nhất.**

### 8d. Phép thử thị trường — SOTP hỗn hợp (thay SOTP qua giá CRV của v1)
- **Bỏ giá CRV 23.000**: CRV chỉ khớp 24/62 phiên (03/08–30/10/2026), ~0,8 tỷ đ/3 tháng, P/B 2,06x, P/E FY25 205x ⇒ không phải giá thị trường.
- SOTP hỗn hợp = mẹ trực tiếp theo sổ 5.958,7 + CRV trực tiếp 38,19% × VCSH CRV 31/03/2026 7.579 = 2.894,4 + HHS 58,31% theo **giá thị trường** (9.450 × 431,99 tr cp = 4.082 tỷ) = 2.380,4 ⇒ **11.234 tỷ = 11.196 đ/cp**.
- Cộng 38,19% LNST CRV 6T ước ~651 (suy từ thuế TNDN CRV 162,64, ETR 20%, ước lượng) ⇒ **~11.450 đ/cp (giá +3,5%)**.
- Thiên lệch: phần mẹ (Green River, H2, 150 Tô Hiệu) và CRV tính **theo sổ, chưa có thặng dư quỹ đất** ⇒ SOTP là cận dưới kiểu "sổ sách + thị trường"; HHS theo giá thị trường đã chứa chiết khấu holding tầng HHS.

### 8e. Phản ứng giá quanh BCTC 29/10 [BQ]
- 29/10: 12.200 (+0,8%; VNI −0,63%). 30/10: **11.850 (−2,87%; VNI −0,80%)**, KL 14,04 tr = 2,4× TB 20 phiên.
- Trước đó +16,2% từ 10.500 (08/10). 1 năm qua TCH −36,8%, VNI +6,2%; đỉnh 2026 16.500 (giá điều chỉnh, 29/04).
- Giả thuyết (không chứng minh được): bàn giao đã được dự báo công khai (SHS 08/2026); con số thuộc mẹ là 538 chứ không phải 750; NMTT giảm. Khối ngoại: chưa đo. Mẫu hình "bán theo tin" đã có ở 28/07/2025 (−6,8%).

## 9. Mốc khoá trước có ngày chấm — HAI CHIỀU (lập 31/10/2026; P = ước lượng)

| # | Mốc | Ngày chấm | P | Nếu ĐÚNG | Nếu SAI |
|---|---|---|---|---|---|
| M1 | BCTC 6T FY26 **soát xét** (AASC): LN mẹ 6T trong ±5% của 663,1; không ngoại trừ/nhấn mạnh; EPS sửa về ~661 | 30/11/2026 | 0,75 | giữ vùng | ngoại trừ/điều chỉnh LN >5% ⇒ hạ tâm ~1.000 đ + nâng WARNING |
| M2 | Q3FY26 (01/10–31/12/2026): LN mẹ quý ≥ 250 | 15/02/2027 | 0,60 | cùng M3 ⇒ LÊN | < 150 cùng NMTT NC-II không giảm (bàn giao khựng) ⇒ XUỐNG ~10.500–11.000 |
| M3 | Thu mới thô Q3 (NMTT 31/12 + DT BĐS Q3 × 1,08 − NMTT 30/09) ≥ 1.000, **hoặc** NMTT xuất hiện dòng HH1–HH2 ≥ 300 | 15/02/2027 | 0,45 | cùng M2 ⇒ tâm ~14.000–15.000 | thu mới < 500 hai quý liên tiếp ⇒ hạ thặng dư về kịch bản tiêu cực |
| M4 | FY26: LNST HN ≥ 2.000 **và** DT ≥ 5.000 (KH hợp nhất, NQ26) | 15/05/2027; kiểm toán 30/06/2027 | 0,50 | LÊN biên trên nếu đi cùng M3 | LNST HN < 1.400 ⇒ tâm ~11.000 |
| M5 | Biên gộp BĐS 9T FY26 ≥ 45% | 15/02/2027 | 0,70 | | < 40% ⇒ kịch bản tiêu cực (~10.150) |
| M6 | Không có QĐ xử phạt/khởi tố mới đối với TCH/CRV/HHS hoặc người nội bộ | 31/03/2027 | 0,75 | giảm CK quản trị 5 điểm % ⇒ +~700 đ | QĐ mới ⇒ +10 điểm % ⇒ −~1.400 đ |
| M7 | BC sử dụng vốn kỳ 03/2027: 865,5 tỷ còn lại dùng đúng Green River/H2, không đổi mục đích | 31/03/2027 | 0,80 | giữ | đổi sang quỹ đất mới / cho công ty con vay ⇒ −~700 đ |

(M6 v1 vế "BC quản trị bán niên liệt kê bên liên quan" **đã xảy ra** 29/07/2026 ⇒ bỏ.)

**Điều kiện đổi nhận định (đối xứng):**
- **Tích cực hơn** (tâm → ~14.000–15.000): (M2 ∧ M3), hoặc HH1–HH2 công bố bán > 50% số căn, hoặc M1 + M6 cùng đúng và thị trường thu hẹp chiết khấu.
- **Tiêu cực hơn** (tâm → ~10.150–11.000): M2 sai kiểu "bàn giao khựng", M5 sai, M1 có ngoại trừ, hoặc một QĐ xử phạt mới (M6 sai).

## 10. Ngành → doanh nghiệp (đọc ngành độc lập, `kb/data_registry/market-state/sector_read_bds_nha_o_do_thi_phia_bac_20261031.md`, đọc SAU phần BCTC)

**Đọc ngành (tóm tắt):** CYCLICAL 0,45 / STRUCTURAL 0,35 / ADMIN_GATED 0,20 (ambiguous). Hà Nội đầu→giữa pha suy về khối lượng (căn hộ bán Q3 −48 đến −66% YoY; thấp tầng hấp thụ 9%, thấp nhất 10 năm). **Hải Phòng trễ Hà Nội 2–4 quý** (cuối pha tăng → đầu pha chững; chưa có số Q3). Lãi vay mua nhà cố định ~10,9%, thả nổi 13–15%. Bẫy: lợi nhuận 2026 phản ánh bán hàng 2024–25 ⇒ có thể đẹp nhất đúng lúc bán mới gãy; chỉ báo dẫn = NMTT + doanh số ký mới.

| Mục cần kiểm | Trên TCH | Kết quả |
|---|---|---|
| Quỹ đất theo dự án | TM9(*) + RIÊNG TM9 theo pháp nhân; số căn từ [SHS]/website | một phần |
| % tiền SDĐ đã nộp | 2.992,9 đã nộp 6T; NC-II một phần đất thuê trả hằng năm tới 2073 | phần lớn đã nộp |
| Giá vốn quỹ đất mới vs giá bán | 150 Tô Hiệu ~103 tr/m² đất, ~1,68 tỷ tiền đất/căn (998 căn [SHS]); I.14 ~70 tr/m² đất | **biên quỹ đất mới mỏng hơn NC-II** — đã phản ánh ở thặng dư |
| NMTT xu hướng 4 quý | +2.643 → +775 → +368 → **−893** | âm lần đầu; Q3FY26 là quý quyết định (M3) |
| Hỗ trợ lãi suất / giảm giá ẩn | trích trước hỗ trợ lãi vay KH 5,64 (0,51, ×11); CPBH BĐS 6T ×2 | nhỏ (0,3% DT BĐS) nhưng đúng hướng cảnh báo |
| Nợ vay, TPDN | 0 / 0 | **điểm mạnh nhất so ngành** |
| Tập trung 1 tỉnh | >90% HTK BĐS ở Hải Phòng | cờ tập trung |
| Cạnh tranh siêu dự án | NC-II, Green River ở Thủy Nguyên, nơi một siêu dự án của chủ đầu tư quốc gia chiếm 47% giao dịch thấp tầng Đông HP H1/2026 | cạnh tranh trực diện |

- Nghiêng trọng số theo đọc ngành ⇒ ~12.280 (giá −3,5%), vẫn trong vùng. Không dùng để hạ vùng vì Hải Phòng chưa có số Q3.
- Nếu DT FY26 tăng mạnh trong khi NMTT giảm (đúng như ngành cảnh báo), cần đọc lợi nhuận FY26 là **đỉnh chu kỳ bàn giao, không phải nền mới**.

## 11. Lệch nguồn BQ vs BCTC
- BQ `ticker_financial` mới nhất 2026Q2 dương lịch (04–06/2026); `PE` 39,8 cũ; OShares 912,1 tr (**chưa cập nhật cp thưởng** 10/09/2026 ⇒ 1.003,3 tr).
- BQ `PB` 0,82 dùng BVPS 14.481 × 912,1 tr cp; cùng cơ sở BQ với số cp mới là 0,90x.
- **CRV không có trong `tav2_bq.ticker`** ⇒ giá CRV lấy từ DNSE. BQ không có dữ liệu khối ngoại.

## 12. Kiểm nhất quán nội bộ vs nguồn độc lập vs chưa kiểm

**Kiểm nhất quán NỘI BỘ (cùng bộ tài liệu công ty):** KQKD ↔ GT; BS ↔ thuyết minh (TM3, 4, 9, 16, 15, 19, 21); LN mẹ 6T KQKD ↔ BS ↔ TM21a; HTK mẹ RIÊNG TM9 ↔ HN TM9(*); NMTT mẹ RIÊNG 2.457 ↔ Green River + H2 HN TM16 (2.455,6); tiền SDĐ TM17 ↔ tăng HTK 2 quỹ đất.
**Đối chiếu NGUỒN ĐỘC LẬP:** LN mẹ Q1/FY24/FY25 ↔ BQ; số cp TM1.1 ↔ TM21d ↔ NQ26 (BQ OShares 912,1 là trước cp thưởng — không khớp, đã giải thích); giá đấu I.14 [SHS] ↔ TM17 Q1; Sacombank ↔ bản tiếng Anh TM4 + QĐ NHNN qua báo; giá TCH/HHS BQ ↔ DNSE.
**Chỉ 1 nguồn / chưa kiểm:** DT Q1 theo mảng, CFO Q1 (SHS); quy mô HH1–HH4/150 Tô Hiệu (SHS, website); án UBCKNN 2024 (2 báo cùng thông cáo); danh tính nhóm uỷ quyền 7,37%; Cảng Kim Tân; quan hệ gia đình bà Nguyễn Thị Hà (4,89%); khối ngoại tháng 10; mọi tham số NAV (ước lượng).

## Giới hạn
- BCTC 6T chưa soát xét; số đọc từ ảnh scan.
- Không có tổng dự toán, giá trị hợp đồng ký, số căn đã bán/còn lại, **doanh số ký mới**, số thị trường Hải Phòng Q3 ⇒ NAV phụ thuộc tham số tự đặt; vùng giá rộng (−14% / +27% quanh giá).
- Chưa có: dòng khối ngoại quanh 29–30/10, danh tính nhóm uỷ quyền 7,37%, kỳ tính thuế bị truy thu (QĐ không nêu), BCTC Q3 riêng của CRV, giải trình DT ô tô giảm.

## Thay đổi v1 → v2

| # | v1 | v2 (đã kiểm trên ảnh/nguồn gốc) | Ảnh hưởng |
|---|---|---|---|
| 1 | Bỏ sót QĐ thuế | **QĐ 1020/QĐ-XPHC 03/04/2026: 20,21 tỷ** (đọc đủ 3 trang QĐ; không nêu kỳ tính thuế) | WARNING "2 cơ quan – 2 loại vi phạm / 16 tháng", vẫn trung bình |
| 2 | Kiểm soát CRV "dựa một phần vào 7,37% uỷ quyền" | TM1.5: bỏ uỷ quyền vẫn **89,35%** biểu quyết; báo chí 81,7% là **vốn** (khác cơ sở); câu hỏi thật = danh tính nhóm + free float CRV ~3% | hạ cờ |
| 3 | "Thặng dư 25% ≈ biên gộp 40–45%" | công thức s(1−g)=0,8(g−0,1) kiểm lại đúng ⇒ 25% ≈ 31,4%; 51,9% ≈ s 70% | thặng dư cơ sở đặt lại 40% (đối xứng) + ma trận |
| 4 | Phần mẹ 72,5–75% đồng đều; Green River/H2 coi như qua CRV | RIÊNG TM9 in 22 (ảnh): Green River/H2/150 Tô Hiệu là HTK mẹ ⇒ 100%; NC-II/I.14 68,02% | NAV tăng |
| 5 | PV 0,90/0,70 tự đặt; Ke 12,6–13,8% ở §8b vs 12,3–13,4% ở §1 | PV theo Ke 12,85% (0,886/0,834/0,785; HTK 0,617); Ke 12,3–13,4% thống nhất | NAV giảm nhẹ |
| 6 | Biên ròng backlog 36% | 33,5% (CPBH chờ phân bổ 6,8–12,4% NMTT) | NAV giảm nhẹ |
| 7 | Chiết khấu 20% áp toàn bộ, lý do gồm "NCI" | holding chỉ phần qua công ty con; quản trị toàn bộ; bỏ "NCI" | NAV tăng |
| 8 | P/B peer neo 8.700 (lệch cơ sở), "cao hơn trung vị 14%" | cùng cơ sở BQ: 0,90x, +25%, neo ~9.480 | cận dưới phép thử tăng |
| 9 | SOTP qua giá CRV 23.000 ⇒ 10.700 | bỏ (CRV khớp 24/62 phiên); SOTP hỗn hợp có HHS theo giá thị trường ~11.200–11.450 | |
| 10 | DT NC-II Q2 ước 1.000–1.200; P(KH FY26) 0,45/0,40 | RIÊNG: mẹ không bàn giao Q2 ⇒ NC-II ~1.650–1.750; NMTT NC-II hết ~3 quý; P 0,60/0,50 | backlog tiêu nhanh hơn; KH khả thi hơn |
| 11 | "BCTC ghi bên liên quan: không" = dấu hiệu di cư | BC quản trị 6T 2026 + BCTN25 + 3 NQ HĐQT công bố đủ; giao dịch nội bộ bị loại khi hợp nhất | bỏ nghi "di cư"; M6 vế 2 bỏ; thêm điểm tích cực |
| 12 | HH Finance "chưa kiểm" | người liên quan; nhóm 35,99% = 71,2% phiếu ĐHĐCĐ; BKS kiêm nhiệm; TGĐ chọn kiểm toán | WARNING đầy đủ |
| 13 | "Sài Gòn Tài Lộc" chưa xác định | = Sacombank; vẫn nêu 678 tỷ là khoản ít rút | đóng cờ |
| 14 | Tiền + HTM 3.285 đ/cp (hợp nhất, gồm NCI) | phần mẹ ~2.950 đ/cp; sau nợ tài chính 1.087 + thuế 199 ~2.000 đ/cp (HN) | |
| 15 | "Đối chiếu 2 nguồn"; cặp "số cp ↔ BQ OShares" | đổi thành "kiểm nhất quán nội bộ" vs "nguồn độc lập"; BQ OShares 912,1 ≠ 1.003,3 (trước cp thưởng) | |
| 16 | "Chưa thấy chi phí dồn treo" | "chưa kiểm được dự toán tổng" | |
| 17 | KH FY26 "chưa rõ hợp nhất hay mẹ" | NQ26 tr.34: hợp nhất | |
| 18 | M1–M6 | M6 bỏ vế đã xảy ra; thêm M7 (vốn chào bán) | |
| **Vùng** | 9.600–14.400, tâm ~11.600–11.950; "xấp xỉ hợp lý, ngay tâm" | **~10.150–15.050, tâm ~12.300–12.650; trong vùng, nửa dưới (−3,5% đến −6,3%)** | đổi do #3, #4, #7 (tăng) lớn hơn #5, #6 (giảm) |

## Nguồn web (truy cập 31/10/2026)
- Nhân Dân — phạt 380 triệu: https://nhandan.vn/post-849025.html · Báo Đầu Tư — chi tiết vi phạm TCH: https://baodautu.vn/vi-pham-hang-loat-quy-dinh-tai-chinh-hoang-huy-nhan-an-phat-d231955.html
- SHS cập nhật TCH 08/08/2026: https://s3-storage.shs.com.vn/shs-website/Cap_nhat_TCH_T8_2026_d5200d2ec5.pdf
- Viettimes 26/03/2025 (cơ cấu cổ đông CRV): https://viettimes.vn/hoang-huy-group-quyet-dinh-chon-me-cho-bat-dong-san-crv-post183958.html
- Sacombank đổi tên: https://theleader.vn/sacombank-doi-ten-thanh-ngan-hang-sai-gon-tai-loc-d46210.html · https://baodautu.vn/sacombank-chinh-thuc-doi-ten-thanh-ngan-hang-sai-gon-tai-loc-d611228.html
- NC-II 543 căn thấp tầng đủ điều kiện kinh doanh: https://nhadautu.vn/543-can-thap-tang-du-an-hoang-huy-new-city-ii-duoc-phep-kinh-doanh-d97221.html
- hoanghuy.vn: BCTC, CBTT, BCTN, ĐHĐCĐ (27 PDF ở `src/gaps/pdf/`).
