# DD — TCH (CTCP Đầu tư Dịch vụ Tài chính Hoàng Huy, HOSE) · v1 · as-of 31/10/2026 · job `Taylor_20261031_141634`

> NGHIÊN CỨU READ-ONLY, trung dung. Không phải khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON, không §2.5.
> Pháp lý/quản trị ⇒ phân tích bình thường + WARNING (luật 27/09).

**Tóm tắt (1 đoạn).** Q2 năm tài chính 2026 (01/07–30/09/2026) lãi đột biến **thật**, đến từ đợt bàn giao đầu tiên của Hoàng Huy New City-II.
Giải trình nêu LNST hợp nhất 750,5 tỷ, nhưng **phần thuộc cổ đông công ty mẹ là 537,7 tỷ**: 28,4% thuộc cổ đông thiểu số, vì lợi nhuận BĐS nằm ở CRV, nơi TCH chỉ hưởng 68,02% lợi ích.
Biên gộp BĐS 6T là 51,9%. Chưa thấy chi phí bị dồn treo: chi phí phải trả chỉ 39,5 tỷ.
Đây là backlog đang được chuyển thành doanh thu chứ không phải lãi một lần. Đổi lại, backlog đang **tiêu nhanh hơn tốc độ bổ sung**: tiền khách ứng trước của NC-II giảm 1.033 tỷ chỉ trong Q2.
Tiền + HTM (gồm HTM dài hạn) giảm 2.910 tỷ trong 6 tháng (2.684 nếu chỉ tính ngắn hạn), CFO 6T −3.078,5 tỷ. Gần như toàn bộ là **tiền sử dụng đất 2.993 tỷ đã nộp** cho 2 quỹ đất mới (I.14 Bắc Sông Cấm và 150 Tô Hiệu), đúng bằng phần tăng HTK, nên không phải tiền "biến mất". Công ty **không có nợ vay**.
Ở 11.850 đ (30/10/2026), giá tương đương P/B 0,98x vốn CSH thuộc cổ đông mẹ, P/E TTM 14,9x và P/E chuẩn hoá FY23–FY26E khoảng 16x.
**Giá trị hợp lý 9.600–14.400 đ, tâm ~11.600–11.950 đ (ước lượng, NAV dự án có chiết khấu holding/quản trị; cận dưới của tâm là bản nghiêng trọng số theo đọc ngành của Bobby, §10)** ⇒ giá **nằm ở tâm vùng: xấp xỉ hợp lý**, không rẻ như "lãi gấp 13 lần" gợi ý.
Thị trường đã trả cho kỳ vọng bàn giao (SHS đã dự báo từ 08/2026), còn LN mẹ chuẩn hoá chỉ cho ROE khoảng 6%.
WARNING quản trị (mức trung bình): UBCKNN phạt 295 triệu ngày 05/12/2024 vì CBTT thiếu giao dịch bên liên quan. BCTC kỳ này vẫn ghi "bên liên quan: không" ở mọi khoản phải thu/phải trả.
Có thêm hai điểm cần lưu ý: EPS 6T bị tính trên LNST **hợp nhất** (911 đ, đúng phải là 661 đ), và quyền kiểm soát CRV dựa một phần vào **7,37% biểu quyết được uỷ quyền**.
Đổi nhận định hai chiều ở §9.

> **Nguồn** (mọi số BCTC đọc từ ẢNH trang render pymupdf zoom 1,5–1,8, sổ đọc `calc/notes_read.md`):
> **[Q2HN]** BCTC hợp nhất giữa niên độ 01/04–30/09/2026 (ký 29/10/2026, **CHƯA soát xét**; `src/Q2FY26_hopnhat_20261029.pdf`; TM = thuyết minh, trang in) ·
> **[GT]** CV giải trình 42/2026/TCH-CV ngày 29/10/2026 · **[Q1HN]** BCTC hợp nhất Q1FY26 (01/04–30/06/2026) ·
> **[KT25]** BCTC hợp nhất FY25 (01/04/2025–31/03/2026) **đã kiểm toán, AASC, ý kiến chấp nhận toàn phần, ký 25/06/2026** ·
> **[BQ]** `tav2_bq.ticker` tới phiên 30/10/2026, `ticker_financial` (`calc/bq_*.csv`) · **[SHS]** báo cáo cập nhật TCH 08/08/2026 (`src/web/SHS_TCH_T8_2026.pdf`, bên bán — chỉ dùng số liệu dự án/Q1, không dùng giá mục tiêu) ·
> **[WEB]** báo chí/UBCKNN qua báo, gắn nhãn. Số tự tính: `calc/tch_valuation.py` → `calc/tch_valuation_out.txt`; giá `calc/px_stats.py` → `calc/px_stats_out.txt`.
> **Đơn vị: tỷ đồng** trừ khi ghi khác. Niên độ kết thúc 31/3: **"Q2FY26" = 01/07–30/09/2026**; "6T" = 01/04–30/09/2026.

---

## 1. Kết luận và vùng giá

| Vùng giá (đ/cp, 1.003,31 tr cp) | Đọc |
|---|---|
| < ~9.600 | chỉ hợp lý nếu kịch bản xấu thành hiện thực: bàn giao chậm/huỷ, biên BĐS về ~35–40%, quỹ đất mới không lãi; ≈ P/B 0,72x peer trung vị (8.700) |
| 9.600 – 14.400 (hiện 11.850) | xấp xỉ hợp lý; tâm ~11.900 (ước lượng) — giá đang **ngay tâm** (−0,9%) |
| > ~14.400 | đòi hỏi ROE bền ≥ ~12% (Ke 12,3–13,4%) **hoặc** bán hết HH1–HH4 + 150 Tô Hiệu + I.14 với biên ~50% — cần bằng chứng ở §9 |

**Kịch bản (NAV dự án, trọng số 0,25/0,50/0,25):** xấu ~9.570 · cơ sở ~11.930 · tốt ~14.390 ⇒ trọng số **11.953 đ** (nghiêng theo đọc ngành 0,35/0,45/0,20: ~11.600, §10). Phép thử chéo:
- P/B trung vị 15 DN BĐS niêm yết 0,72x → 8.700 (cận dưới; TCH xứng đáng cao hơn vì không vay, biên ~50%).
- Look-through 68,02% CRV theo giá thị trường **10.700 đ/cp TCH**, trước chiết khấu holding. Giá CRV lấy từ web và bị trễ.
- P/E chuẩn hoá ~16x.
- SHS (08/2026) đặt giá mục tiêu 17.700. Đây là số của bên bán, giả định tiêu thụ tốt; ta không dùng.

**Gỡ ngộ nhận "lãi ×13, giá lại giảm":**
- ×13 là LNST **hợp nhất** so với một quý gốc rất thấp (Q2FY25 56,3). LN mẹ Q2 là 537,7.
- LN mẹ TTM 796 ⇒ P/E 14,9x. BQ còn ghi P/E 39,8 vì chưa nạp kỳ này.
- So với FY24 (LN mẹ 855), LN mẹ TTM hiện **vẫn thấp hơn**. Đây là chu kỳ bàn giao trở lại, chưa phải mức lợi nhuận mới.

## 2. Kiểm lại số Mike đọc (từng số)

| Số Mike | BCTC/nguồn | Kết luận |
|---|---|---|
| GT: DT HN Q2 1.960,89 (+566,76%), LNST 750,54 (+1.332%); riêng DT 57,61 / LNST 40,14 (157,93, −74,6%) | [GT] ✓; KQKD [Q2HN in 7–8]: DT 1.960,89 / LNST 750,54 | ✓ khớp KQKD ↔ GT |
| BS: tiền 1.035,4 (1.694,2); HTM NH 2.203,2 (4.228,1) | [Q2HN in 4; TM3; TM4] ✓ | ✓ (HTM DH 57,8 (284,3) Mike chưa tính) |
| Phải thu KH 287,3; trả trước NB 565,0; HTK 15.257,7 (11.604,1), DP 3,4 | ✓ [in 4; TM5,6,9] | ✓; DP 3,4 toàn bộ là HTK ô tô, BĐS **0 dự phòng** |
| NMTT 5.599,8 (6.124,8); PTNB 664,2; nợ 6.937,3 (7.475,5); PT khác 366 | ✓ [in 6; TM15,16,19] | ✓ |
| "Gần như không vay" | **0 vay** trên BCĐKT; TM36 nợ tài chính chỉ là phải trả NB/khác 1.086,8; LCTT 6T: không đi vay/trả nợ | ✓ (chính xác: KHÔNG vay) |
| VCSH 15.279,7; vốn góp 10.033,1 (9.121,1) ⇒ cp thưởng ~10%; LNST CPP 1.889,2; NCI 3.120,5 (2.869,4); TTS 22.216,9 | ✓ [in 5–6; TM21]: cp thưởng 10:1 = 912,04 tỷ mệnh giá lấy từ thặng dư 843,57 + LNCPP 68,47, xong 10/09/2026 | ✓ |
| BQ Q(04–06/2026) LN mẹ 125,4 / DT 453,5 | BQ 2026Q2 ✓; [Q2HN] 6T−Q2 = 663,14−537,73 = **125,42** | ✓ (DT 453,5 là DT gộp; DTT 450,95) |
| BQ "(01–03/2026) 52,4/317,0" | **✗ nhãn sai**: 52,4/317,0 là **10–12/2025** (BQ 2025Q4); 01–03/2026 = **80,5/394,1** (BQ 2026Q1) | ✗ |
| "FY25 LNST ~256 (báo chí)" | [KT25] LNST HN **259,20**; mẹ **211,06** | ✗ nhỏ — dùng số kiểm toán |
| KH FY26 DT 5.000 / LNST 2.000 | chỉ [WEB] (24hmoney, vietstock); chưa đọc NQ ĐHĐCĐ 01/2026 gốc; **chưa rõ LNST hợp nhất hay mẹ** | chưa kiểm nguồn gốc |
| Giá 11.850 (30/10, −2,9%), KL 14,04 tr "≈ gấp ~3" | [BQ] 11.850, −2,87% (VNI −0,80%); KL 14,04 tr = **2,4× TB 20 phiên (5,87 tr)**, 2,6× TB 60 phiên | ✓ / "gấp 3" hơi cao |
| 18.150 (29/04/2026); 10.500 đáy 08/10 | [BQ] `Price` 18.150 ✓ (giá điều chỉnh cp thưởng = 16.500); 10.500 là đóng cửa 08/10 ✓, nhưng **đáy năm 2026 = 10.000 (giá điều chỉnh) ngày 27/07**; thấp nhất trong phiên 10.150 ngày 09/10 | ✓ nửa |
| ~1,003 tỷ cp; vốn hoá ~11,9 nghìn tỷ; ~0,98× VCSH mẹ | TM21d: **1.003.312.808 cp, KHÔNG có cp quỹ**, TM34: không có cp tiềm năng suy giảm; vốn hoá 11.889; VCSH mẹ 12.159,1 ⇒ BVPS 12.119, **P/B 0,98** | ✓ |
| "CFO âm gần 1.600 kỳ trước (báo chí)" | [SHS] Q1FY26 CFO −1.596 (chưa đối chiếu ảnh LCTT Q1); [Q2HN] CFO **6T −3.078,5** ⇒ Q2 ≈ −1.482 nếu số SHS đúng | ✓ (qua SHS) |
| "Phạt hành chính 380 triệu cùng một công ty khác" | [WEB Nhân Dân] **380 = 295 (TCH, QĐ 1357/QĐ-XPHC 05/12/2024) + 85 (CTCP Đầu tư tổng hợp Hà Nội)** — CÙNG một đợt công bố, KHÔNG phải án phạt thứ hai của TCH | ✗ đính chính |

## 3. Câu 1 — Lợi nhuận Q2 và 6T đến từ đâu, có bền không

### 3a. KQKD hợp nhất [Q2HN in 7–8]

| | Q2FY26 | Q2FY25 | 6T FY26 | 6T FY25 |
|---|---|---|---|---|
| DT thuần | 1.958,18 | 345,98 | 2.409,13 | 736,28 |
| Giá vốn | 1.001,86 | 256,50 | 1.312,55 | 534,01 |
| LN gộp (biên) | 956,32 (**48,8%**) | 89,48 (25,9%) | 1.096,58 (45,5%) | 202,28 (27,5%) |
| DT tài chính | 74,68 | 40,18 | 175,46 | 76,32 |
| CP bán hàng / QLDN | 77,13 / 21,85 | 31,60 / 28,44 | 107,27 / 40,17 | 67,59 / 50,10 |
| Lãi/lỗ thanh lý BĐSĐT | −5,58 | – | +3,26 | – |
| LNTT | 928,53 | 72,69 | 1.129,49 | 150,45 |
| Thuế (ETR) | 177,99 (19,2%) | 16,35 | 215,19 (19,1%) | 37,88 |
| LNST HN | 750,54 | 56,34 | 914,29 | 112,57 |
| **LNST mẹ** / NCI | **537,73** / 212,81 | 40,21 / 16,13 | **663,14** / 251,15 | 78,09 / 34,48 |

Lãi/lỗ liên doanh liên kết: **0** (không có công ty liên kết). Chi phí lãi vay: **0**. LN khác Q2: 3,14.

### 3b. Theo mảng — 6T [TM23, TM25]; Q2 suy từ Q1 của [SHS] (ước lượng)

| Mảng | DT 6T FY26 (FY25) | GV 6T | Biên gộp 6T (FY25) | Q2 ≈ (6T − Q1 SHS) |
|---|---|---|---|---|
| Bán BĐS | 1.954,52 (220,77) | 940,37 | **51,9%** (51,0%) | DT ~1.751, LN gộp ~921 (Q1 SHS: DT ~203, biên ~46%) |
| Ô tô tải/đầu kéo & linh kiện | 359,47 (427,83) | 312,07 | 13,2% (13,9%) | DT ~157 (Q1 202) — **giảm** |
| Cho thuê BĐS & DV | 97,23 (87,68) | 57,84 | 40,5% | |
| Khác | 3,14 | 2,41 | | |

BCTC **không** tách DT theo dự án. Có thể suy gián tiếp từ biến động người mua trả tiền trước (NMTT) Q2 [Q1HN TM16 → Q2HN TM16]:
- NC-II: 4.132,2 → 3.099,2 (**−1.033,0**), cùng phải thu người mua NC-II +90,5.
- Green River: 1.779,7 → 1.837,8 (+58,1); TP BĐS Green River 632 → 760 (6T).
- H2: 521,6 → 617,8 (+96,2), tức vẫn đang thu tiền, chưa bàn giao.

⇒ Phần lớn DT BĐS Q2 đến từ **NC-II** (khoảng 1.000–1.200 ex-VAT, ước lượng). Green River bàn giao rải rác.

### 3c. Bao nhiêu là một lần / dồn

- **Không có khoản lãi một lần kiểu thoái vốn/đánh giá lại.** Thanh lý BĐSĐT chỉ +3,3 trong 6T; LN khác 4,8; không có công ty liên kết.
- **Tính dồn của chu kỳ bàn giao.** Doanh thu Q2 là đợt bàn giao **đầu tiên** của NC-II: dự án bắt đầu nhận cọc từ FY24–FY25 và đến nay mới ghi nhận. Q2 lấy khoảng 1/4 số NMTT của NC-II. Với nhịp này, NMTT còn lại của NC-II (3.099) cạn sau khoảng 3 quý (ước lượng) nếu không có bán hàng mới bù vào.
  ⇒ LNST quý mức ~700+ **không phải mức chạy bền**: nó phụ thuộc HH1–HH4 (2.494 căn, [SHS], đang làm hầm) và tốc độ bán.
- **Lãi tiền gửi.** DT tài chính 6T 175,5, trong đó lãi tiền gửi 173,5 [TM27], khoảng 15% LNTT 6T. Tỷ trọng này sẽ giảm vì tiền + HTM đã giảm 2.684 tỷ: tiền đã chuyển thành đất, lãi gửi 4,8–9,8%/năm [TM4] không còn.
- **Biên gộp có bị "đẹp" nhờ trích trước giá vốn thấp không?** Giá vốn BĐS được trích trước theo dự toán, phân bổ theo diện tích [TM2.26].
  - Số dư trích trước chi phí xây dựng chỉ **18,95** (Green River 6,93) [TM18], so với giá vốn BĐS 6T 940. Không thấy trích treo lớn.
  - Biên BĐS 51,9% ngang FY25 (51,0%). Không có dấu hiệu bất thường, nhưng **chưa kiểm được dự toán tổng** (rủi ro quyết toán sau).
  - CP bán hàng chờ phân bổ 447,35 [TM14] (NC-II 228,2; Green River 124,9; H2 76,7) sẽ chảy vào CPBH khi bàn giao. Khoản này là chi phí đã trả, chưa hạch toán: **làm giảm biên ròng các quý tới**.

### 3d. Vì sao LN công ty mẹ riêng 40 tỷ còn hợp nhất 750 tỷ

- LN BĐS nằm ở công ty con. Thuế TNDN hiện hành 6T là 218,85, trong đó **CRV 162,64** và Đại Lộc 8,98 [TM32].
- Công ty mẹ riêng chỉ có DT 57,61 và DT tài chính 56,85. Q2 chưa nhận cổ tức không thường xuyên từ công ty con, trong khi Q2FY25 có [GT].
- ⇒ Tiền lãi của CRV **chưa chảy lên TCH mẹ**. Muốn lên được phải qua chia cổ tức của CRV, và cổ đông thiểu số CRV hưởng 31,98% phần đó.

### 3e. Lịch sử LN mẹ theo năm tài chính (Apr–Mar) [BQ ticker_financial cộng quý; khớp KT25]

| FY21 | FY22 | FY23 | FY24 | FY25 | 6T FY26 | TTM |
|---|---|---|---|---|---|---|
| 400,5 | 246,0 | 743,8 | 855,0 (KT25 ✓ 854,99) | 211,0 (KT25 ✓ 211,06) | 663,1 | 796,0 |

Lợi nhuận rất lồi theo chu kỳ bàn giao. Trung bình FY21–25 là 491 (ROE ~4% trên VCSH mẹ hiện tại). Trung bình FY23–FY26E là 677–777 tuỳ FY26E 900/1.117/1.300 (ROE 5,6–6,4%) [`tch_valuation_out.txt`].

## 4. Câu 2 — Ghi nhận doanh thu, backlog, kế hoạch FY26

- **Phương pháp:** ghi nhận khi chuyển giao rủi ro/lợi ích, tức **bàn giao**, không dùng POC [TM2.25]. Tiền khách ứng theo tiến độ nằm ở NMTT.
- **NMTT 30/09/2026 = 5.599,82** [TM16]: NC-II 3.099,20 · Green River 1.837,75 · H2 617,83 · H1 38,15 · khác 6,88. Có **3 dự án đang thu tiền** cộng H1 đã xong; H2 (Lê Chân) đang hoàn thiện, dự kiến ghi nhận từ FY27 [SHS].
- **Backlog doanh thu thật:** NMTT là tiền đã thu, thường chỉ là một phần giá trị hợp đồng. BCTC không công bố giá trị hợp đồng ký. Quy NMTT ra DT ex-VAT ≈ **5.185** (VAT bình quân ~8% vì phần đất không chịu VAT, ước lượng). Nếu khách đã trả ~70% (ước lượng), giá trị hợp đồng còn lại khoảng 7.400 (ước lượng).
- **Kế hoạch FY26** (5.000 DT / 2.000 LNST, [WEB], chưa đọc NQ gốc): 6T đạt **DT 48,3%** (2.414) và **LNST HN 45,7%** (914); LN mẹ mới đạt 33%. H2 cần DT 2.586 và LNST 1.086 (HN).
  - Có thể giao: NC-II 3.099 + Green River 1.838 ≈ 4.937 NMTT, cộng TP tồn Green River 760 / H1 299.
  - ⇒ **Đạt DT 5.000 khả thi nhưng chưa chắc.** P ~0,45 đạt DT; P ~0,40 đạt LNST HN ≥ 2.000 (ước lượng). Lý do: cần bàn giao gần như toàn bộ phần NC-II/Green River đã thu tiền trong 2 quý và giữ biên ~50%.
  - SHS (08/2026) dự LN mẹ FY26 1.117. Ta không dùng làm cơ sở.
- **Tốc độ bổ sung backlog** (tín hiệu xấu đáng theo dõi): ΔNMTT theo quý là +2.643 (Q2FY25), +775, **+368 (Q1FY26)** [SHS], rồi **−892,7 (Q2FY26)** [Q1HN→Q2HN].
  - Thu mới thô Q2 ≈ ΔNMTT + phần DT BĐS Q2 đi ra từ NMTT ≈ −893 + ~1.890 ≈ ~1.000 (ước lượng, gồm cả đợt thanh toán của hợp đồng cũ, **không** phải doanh số ký mới).
  - Chưa có số doanh số ký mới. HH1–HH2 dự kiến mở bán Q3/2026 [SHS] nhưng BCTC 30/09 chưa thấy NMTT cho HH.

## 5. Câu 3 — Bảng cân đối và dòng tiền

### 5a. Net cash thật

| Khoản | 30/09/2026 | 31/03/2026 |
|---|---|---|
| Tiền + TĐT | 1.035,35 | 1.694,17 |
| HTM ngắn hạn + dài hạn | 2.203,19 + 57,78 | 4.228,14 + 284,30 |
| **Tiền + HTM** | **3.296,3** (3.285 đ/cp) | 6.206,6 |
| Vay | **0** | **0** (FY25 đã trả hết 923,5 [KT25 LCTT]) |
| NMTT (nghĩa vụ giao hàng) | 5.599,82 | 6.124,75 |
| Chi phí để hoàn thành phần đã bán | **chưa công bố** — NC-II còn đang thi công | |

- Net cash tài chính là +3.296. Nhưng **phải hiểu đúng**: 5.600 tiền khách đã ứng phải được "trả" bằng nhà/đất. Phần chi phí xây dựng còn lại cho các căn đã bán **không có trên BS**, vì BCTC không công bố tổng dự toán.
- ⇒ Net cash "tự do" thấp hơn 3.296 một khoản chưa đo. Bù lại, công ty không có nợ vay, không có trái phiếu, và **không thấy bảo lãnh/cầm cố tiền gửi** trong TM4/TM22.
- Tiền gửi phân tán ở 8+ ngân hàng [TM4]. Một tên đọc trên ảnh là "Sài Gòn Tài Lộc", 678,3: **chưa xác định là ngân hàng nào** (chữ scan), cần kiểm trên bản text/bản tiếng Anh.

### 5b. HTK tăng 3.653 trong 6T — vì sao [TM9(*), TM17]

| Dự án BĐS (CPSXKDDD) | 30/09/26 | 31/03/26 | Δ |
|---|---|---|---|
| 150 Tô Hiệu (Lê Chân) | 1.677,51 | 4,40 | **+1.673,1** |
| Lô I.14/CTHH-01 Bắc Sông Cấm (Thủy Nguyên) | 1.328,75 | 0 | **+1.328,8** |
| New City-II | 7.390,37 | 7.230,42 | +160,0 (30/06: 7.818 [SHS] ⇒ Q2 xuất giá vốn bàn giao) |
| Green River | 2.557,50 | 2.363,43 | +194,1 |
| Commerce H2 | 555,53 | 512,78 | +42,8 |
| Khác | 18,91 | 7,18 | |
| TP BĐS | 1.102,34 | 997,64 | +104,7 |

- **Đối chiếu chéo:** TM17 ghi thuế nhà đất & tiền thuê đất *đã nộp* 6T **2.992,90**. Theo từng quý: Q1 1.326,27 [Q1HN TM17], khớp giá đấu I.14 1.322 [SHS]; Q2 1.666,63, khớp phần tăng của 150 Tô Hiệu.
  ⇒ Cả **3.002** tăng HTK của 2 quỹ đất mới là **tiền sử dụng đất đã nộp đủ**. Tiền + HTM giảm 2.910 trong 6T (6.206,6 → 3.296,3), đi gần trọn vào đất.
- Phải thu khác giảm 608 (BQLDA phường Lê Chân 360,8 → 0,1; Cty Đấu giá hợp danh VNA 256,5 → 0) [TM7]. Đây là các khoản ứng GPMB / đặt cọc đấu giá năm trước, nay đã tất toán vào đất.
- **Pháp lý quỹ đất:**
  - I.14 đã giao đất 23/07/2026 [SHS].
  - 150 Tô Hiệu: GPMB xong 15/04/2026 [SHS]; TM9 ghi "đã hoàn tất chuẩn bị mặt bằng, bắt đầu thi công"; tiền SDĐ đã nộp (TM17).
  - NC-II: một phần **đất thuê trả tiền hằng năm** 26.664,2 m² tới 2073 [TM22b], phần còn lại là đất giao.
  - 17B Bà Triệu (HN) 243,18 đang làm thủ tục nhận chuyển nhượng [TM10].
  - **Không** có dự phòng giảm giá HTK BĐS.
- Trả trước người bán 565,0 [TM6] là cho nhà thầu, không có bên liên quan: Hòa Bình 162,5; Thủy Ngân 103,9 (mới tăng từ 2,9); Cảng Kim Tân 73,7 (mới); XD số 1 Bắc Giang 50,0; Bạch Đằng 37,0; khác. **Chưa rõ vì sao trả trước cho Cảng Kim Tân 73,7**.

### 5c. Dòng tiền [Q2HN in 9–10; KT25]

| | 6T FY26 | 6T FY25 | FY25 | FY24 |
|---|---|---|---|---|
| LN trước thay đổi VLĐ | 978,1 | 106,5 | 189,4 | 1.456,6 |
| ΔHTK | −3.653,4 | −871,0 | −3.005,0 | +1.274,1 |
| ΔPhải trả (gồm NMTT) | −692,9 | +2.843,0 | +5.947,1 | −548,9 |
| **CFO** | **−3.078,5** | +1.559,2 | **+2.030,0** | +1.467,7 |
| CFI | +2.419,7 (rút HTM ròng 2.238) | −2.513,9 | −3.262,6 | −872,5 |
| CFF | 0 | +2.246,6 | +1.655,7 (phát hành 2.004,3) | +187,6 |

- CFO 2 năm FY25+6T FY26 cộng lại khoảng −1.050. Nếu bỏ tiền đất mới (~3.000), CFO lõi dương.
- Lệch đối chiếu nhỏ: tiền cuối kỳ trên LCTT 1.035,363 so với BS 1.035,353 (**lệch 9,95 triệu đ**), không trọng yếu.

## 6. Câu 4 — Cấu trúc tập đoàn, cổ đông, quản trị & pháp lý — ⚠️ WARNING (mức trung bình)

### 6a. Cấu trúc [TM1.5]

| Công ty con | Lợi ích | Biểu quyết | Mảng |
|---|---|---|---|
| **CRV** (Tập đoàn BĐS CRV, HN — niêm yết HOSE 10/10/2025) | **68,02%** | 96,72% | BĐS (NC-II, Golden Land) |
| Đại Lộc / Đại Thịnh Vượng (qua CRV) | 68,01% | 99,99% / 99,998% | BĐS (I.14 thuộc Đại Lộc [SHS]) |
| **HHS** (Đầu tư Dịch vụ Hoàng Huy, niêm yết) | **58,31%** | 58,31% | ô tô |
| Hoàng Giang; HHS Capital; Pruksa VN (qua HHS) | 58,19%; 58,31%; 52,58% | 99,79%; 99,996%; 90,17% | ô tô; XD; NOXH An Hải |
| Tô Hiệu (150 Tô Hiệu); Thịnh Phát; Thịnh Hiệp | 99,98%; 96,33%; 95,84% | | XD/BĐS |

- Biểu quyết tại CRV gồm 38,19% trực tiếp + 58,53% gián tiếp. Phần gián tiếp có **qua HHS 42,63%, trong đó 7,37% là quyền biểu quyết do "1 nhóm cổ đông khác UỶ QUYỀN cho HHS"**.
- Danh tính nhóm uỷ quyền không công bố. Kiểm soát CRV (và việc hợp nhất) dựa một phần vào uỷ quyền, vốn có thể thu hồi: **cần kiểm** hợp đồng uỷ quyền, thời hạn, và nhóm đó có phải người liên quan của ông Đỗ Hữu Hạ không.
- **NCI ăn 27,5% LNST 6T.** Lợi nhuận phải đi qua 2 tầng niêm yết (CRV → HHS/TCH) mới thành cổ tức cho cổ đông TCH.

### 6b. Cổ đông [TM21b; SHS]
- Ông **Đỗ Hữu Hạ** (Chủ tịch) nắm 302,75 tr cp, **30,18%**. CTCP HH Finance nắm 5,81%, *chưa kiểm* có phải người liên quan không. Cổ đông khác 64,01%.
- NĐT nước ngoài ~9,5% (SHS, 08/2026). Room và dòng khối ngoại quanh 29–30/10 **chưa đo** (BQ không có dữ liệu khối ngoại).
- HĐQT có 5 người, trong đó 2 người họ Đỗ (Hạ, Hưng). Chỉ **1 thành viên độc lập**. Thù lao HĐQT 6T là 0,456 tỷ [TM38].

### 6c. Lịch sử pha loãng
Số cp: 399,2 tr (2021) → 618,7 → 668,2 → 868,7 → 912,1 → **1.003,3 tr (2026)**, tức **×2,5 trong 5 năm** [BQ OShares; TM21].
- Năm 2025 phát hành 200,46 tr cp thu **2.004,6 tỷ = đúng mệnh giá 10.000 đ/cp** [TM21a: thặng dư −0,36].
- Ngay trong kỳ đó TCH chi 1.302,5 tỷ "thay đổi tỷ lệ lợi ích tại công ty con": làm giảm LNCPP 452,1 và NCI 850,4 [TM21a], tức trả **cao hơn giá trị sổ sách 452 tỷ** để mua thêm phần lợi ích ở công ty con.
- Năm 2026 phát hành cp thưởng 10%.
- LN mẹ/cp do đó bị pha loãng mạnh. EPS FY24 1.219 đ còn TTM hiện chỉ ~793 đ.

### 6d. Pháp lý / CBTT

| Sự kiện | Nguồn | Mức |
|---|---|---|
| **QĐ 1357/QĐ-XPHC ngày 05/12/2024 (UBCKNN): phạt 295 tr đ** = 92,5 tr (không CBTT giải trình chênh lệch LNST BCTC riêng 2020–2021) + **65 tr (BC quản trị 2021–2023 không liệt kê giao dịch bên liên quan**: cổ tức CRV 320 tỷ 07/2022 và 66,5 tỷ 12/2022; DT với HHS, Thịnh Hiệp, Thịnh Phát, Pruksa VN, Hoàng Giang; góp vốn Tô Hiệu 2023) + **137,5 tr (HĐ thuê văn phòng với 2 công ty liên quan, HĐQT duyệt muộn 24/07/2023)**; QĐ 1358/QĐ-KPHQ buộc huỷ/cải chính BCTN 2021 | [WEB] Nhân Dân, Báo Đầu Tư | WARNING — vi phạm CBTT/thủ tục, mức phạt nhỏ, không hình sự |
| "380 triệu" | = 295 (TCH) + 85 (CTCP Đầu tư tổng hợp Hà Nội) cùng đợt | không phải án thứ 2 |
| Kiểm toán FY25: **AASC, chấp nhận toàn phần, không nhấn mạnh** | [KT25 in 4–5] | sạch |

**Kiểm "scandal di cư"** (vi phạm cũ có chuyển sang hình thức khác không):
1. **Công bố giao dịch bên liên quan vẫn mỏng.**
   - TM38 kỳ này chỉ liệt kê thù lao. Mọi bảng phải thu/phải trả/trả trước/NMTT đều ghi "bên liên quan: –".
   - Án phạt 2024 lại chính là vì **HĐ thuê văn phòng với 2 công ty liên quan** và giao dịch nội bộ không được liệt kê.
   - Trong 6T có DT cho thuê 97,2 và chi phí; **không kiểm được** HĐ thuê văn phòng với công ty liên quan có còn hay không.
   - ⇒ **Rủi ro di cư: CÓ THỂ, chưa xác minh.** Lần kiểm tới: BC tình hình quản trị bán niên 2026 và BCTC riêng.
2. **EPS 6T bị tính sai/không nhất quán** [Q2HN TM34].
   - Tử số kỳ này 914,29 là **LNST hợp nhất gồm NCI**, ra 911 đ. Kỳ trước dùng 78,09 là LN mẹ.
   - Chính sách TM2.29 nói rõ phải dùng LN phân bổ cho cổ đông phổ thông. EPS đúng 6T = 663,14/1.003,31 = **661 đ**, tức EPS báo cáo **cao hơn 38%**.
   - Kỳ so sánh cũng chưa điều chỉnh hồi tố cho cp thưởng (673,69 tr cp).
   - Đây là lỗi trình bày trên BCTC **chưa soát xét**. Cùng họ "CBTT thiếu cẩn trọng" như án 2024, không chạm tiền thật. Kiểm lại ở bản soát xét AASC.
3. Khoản Pruksa International tạm ứng 59,43 tỷ (2,261 tr USD) treo nhiều năm vì "chưa thống nhất phương án khấu trừ" [TM19]. Nhỏ, nhưng là tranh chấp tiềm ẩn với đối tác.
4. Quyền kiểm soát CRV dựa vào 7,37% uỷ quyền (§6a).

⇒ WARNING mức **trung bình**: chưa có dấu hiệu gian lận/khởi tố/kiểm toán ngoại trừ. Tuy vậy, chất lượng CBTT có lịch sử vi phạm và kỳ này vẫn còn lỗi trình bày.

## 7. Câu 5 — Kiểm toán

- FY25 do **AASC** kiểm toán (BC số 250626.006/BCTC.KT7, ký 25/06/2026): **ý kiến chấp nhận toàn phần, không có đoạn nhấn mạnh** [KT25 in 4–5]. Thời điểm ký là 86 ngày sau 31/03, sát hạn 90 ngày.
- 6T FY25 được AASC soát xét. Số so sánh 6T FY25 trong BCTC này khớp phần "kỳ trước" (LNST 112,57; mẹ 78,09).
- **6T FY26 (kỳ này) CHƯA soát xét.** Bản soát xét bán niên là mốc kiểm M1 (§9).
- Điều chỉnh sau kiểm toán FY25 so với BCTC quý: tổng 4 quý LN mẹ theo BQ là 211,0, khớp số kiểm toán 211,06 ⇒ **không thấy điều chỉnh trọng yếu** (đo trên LN mẹ; chưa so từng khoản mục BS).
- BCTC bán niên 2025 soát xét (01/04–30/09/2025) **chưa tải**; chỉ đối chiếu qua cột so sánh.

## 8. Câu 6 — Định giá (giá 11.850 đ, đóng cửa 30/10/2026 [BQ]) — `calc/tch_valuation_out.txt`

### 8a. Bội số

| | Giá trị | Ghi chú |
|---|---|---|
| P/B (VCSH mẹ 12.159,1; BVPS 12.119) | **0,98x** | BQ ghi 0,82 (BV khác cách tính) — so peer dùng cùng nguồn BQ |
| P/E TTM mẹ (796,0; EPS 793) | **14,9x** | BQ 39,8 — chưa nạp Q2FY26 |
| P/E chuẩn hoá FY23–FY26E (EPS 675–775) | **15,3–17,6x** | FY26E 900 / 1.117 / 1.300 (ước lượng) |
| P/E TB FY21–25 (491) | 24,2x | |
| Tiền + HTM / cp | 3.285 đ (28% giá) | trước nghĩa vụ hoàn thành phần đã bán |
| ROE chuẩn hoá | 5,6–6,4% | VCSH phình vì tiền gửi + quỹ đất mới chưa sinh lãi |

**Comp ngành nhà ở/đô thị** [BQ 30/10/2026, P/B và P/E do BQ tính]:
- KDH 0,86 / 9,8 · NLG 0,73 / 17,3 · PDR 0,89 / 18,4 · DIG 0,79 / 10,5 · DXG 0,61 / 66,7 · HDG 0,72 / 6,5 · CEO 1,00 / 34,6 · HDC 0,86 / 13,4 · NVL 0,51 / 7,9 · VHM 1,82 / 6,5 · KHG 0,38 · SCR 0,32 · DXS 0,31.
- **P/B trung vị 15 tên (bỏ VHM) = 0,72**. TCH theo cùng nguồn BQ là 0,82, tức cao hơn trung vị ~14%.
- Điều đó hợp lý vì TCH không vay, biên ~50%, quỹ đất sạch đã nộp tiền SDĐ, trong khi phần lớn peer còn nợ vay/trái phiếu.

### 8b. Chi phí vốn (khung skill 29–30/10)
- β tuần 2 năm vs VNINDEX là **1,23**, Blume **1,16** (n=100 tuần). rf chuẩn hoá 6,75%; ERP nội địa 5,0–6,1% ⇒ **Ke ≈ 12,6–13,8%** (dải rộng 10,5–14,0%).
- P/B hợp lý theo (ROE−g)/(Ke−g), g=3%:
  - ROE 6% ⇒ 0,29–0,32x.
  - ROE 10% ⇒ 0,67–0,75x.
  - ROE 12% ⇒ 0,87–0,97x.
- ⇒ **Giá hiện tại ngầm định ROE bền ~12–13%**, gấp đôi mức chuẩn hoá lịch sử. Khoảng chênh chỉ được biện minh nếu VCSH sổ sách **đánh giá thấp quỹ đất**, tức thặng dư chưa ghi nhận trong HTK theo giá gốc. Vì vậy dùng NAV dự án làm phương pháp chính, không dùng DCF vô hạn: dòng tiền BĐS có thời hạn theo dự án.

### 8c. NAV dự án (ước lượng; mọi tham số tự đặt)
NAV = VCSH mẹ 12.159 + LN sau thuế còn nằm trong backlog đã thu tiền (phần mẹ) + thặng dư sau thuế trên HTK còn lại (phần mẹ, PV), rồi trừ chiết khấu holding/quản trị.

| | Xấu | Cơ sở | Tốt |
|---|---|---|---|
| Backlog: DT ex-VAT ~5.185 × biên ròng sau thuế | 28% | 36% | 40% |
| HTK còn lại ~12.038 (sau trừ giá vốn backlog) × thặng dư sau thuế | 10% | 25% | 40% |
| PV hệ số (backlog ~1 năm 0,90; HTK ~4 năm 0,70), phần mẹ 72,5–75% | | | |
| Chiết khấu holding/quản trị (2 tầng niêm yết, NCI, lịch sử CBTT, pha loãng) | 30% | 20% | 10% |
| **Giá trị / cp** | **~9.570** | **~11.930** | **~14.390** |

Trọng số 0,25/0,50/0,25 ⇒ **11.953 đ**, so với giá 11.850 (−0,9%).
- Thặng dư sau thuế 25% trên giá vốn tương đương biên gộp khoảng 40–45%, sau khi trừ CPBH ~10% và thuế 20%. Mức này dưới biên lịch sử 51,9% để dành chỗ cho chi phí hoàn thành chưa thấy và giá Hải Phòng có thể đi ngang (ước lượng).
- **Độ nhạy:** mỗi ±5 điểm % thặng dư HTK ⇒ ±~315 tỷ NAV phần mẹ ⇒ ±~250 đ/cp (sau chiết khấu 20%). Mỗi ±10 điểm % chiết khấu holding ⇒ ±~1.490 đ/cp. **Chiết khấu holding là tham số nhạy nhất.**

### 8d. Phép thử thị trường — SOTP qua CRV
- CRV 23.000 đ (21/10/2026, stockanalysis, **trễ, chưa kiểm**) × 687,40 tr cp = 15.810 tỷ. 68,02% của TCH tương đương **10.754 tỷ = 10.719 đ/cp TCH**, trong khi vốn hoá TCH là 11.889.
- ⇒ Thị trường trả cho **mọi thứ ngoài CRV** khoảng 1.135 tỷ, trước chiết khấu holding: HHS ô tô, Tô Hiệu (150 Tô Hiệu, 1.678 tỷ tiền đất), Thịnh Phát/Hiệp, tiền ở công ty mẹ.
- Hai cách đọc: TCH rẻ so với CRV, **hoặc** CRV (free float nhỏ, P/E 21) đắt. Không dùng phép thử này để kết luận "rẻ".

### 8e. Phản ứng giá quanh BCTC 29/10 [BQ, `px_stats_out.txt`]
- 29/10: 12.200 (+0,8%; VNI −0,63%). 30/10: **11.850 (−2,87%; VNI −0,80%)**, KL 14,04 tr, gấp 2,4× TB 20 phiên.
- Trước đó cp đã tăng từ 10.500 (08/10) lên 12.200 (29/10): **+16,2%**. Phiên 21/10 +5,3% cùng ngày VNI +2,75%, nên đó là nhịp chung của thị trường.
- 1 năm qua TCH **−36,8%**, VNI **+6,2%**. Đỉnh 2026 là 16.500 (giá điều chỉnh, 29/04).
- Giải thích khả dĩ cho "lãi ×13 mà giảm" (**giả thuyết, không chứng minh được bằng số đang có**):
  1. Bàn giao Q3 đã được dự báo công khai (SHS 08/2026), nên kỳ vọng đã nằm trong giá sau nhịp +16%.
  2. Con số thuộc cổ đông mẹ là 538, không phải 750.
  3. NMTT giảm 893 và tiền + HTM giảm 2.910 trong 6T, tức backlog đang tiêu.
  4. Khối ngoại: **chưa đo**.
- Các phiên BCTC trước:
  - 29/07/2026: phản ứng nhẹ, 10.180 → 10.500 hai phiên sau.
  - 28/07/2025: 19.690 → 18.350 (−6,8%), KL 21,3 tr.
  - Mẫu hình "bán theo tin" ở TCH **không phải lần đầu**.

## 9. Mốc khoá trước có ngày chấm — HAI CHIỀU (lập 31/10/2026; P = ước lượng; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm)

| # | Mốc | Ngày chấm | P | Nếu ĐÚNG | Nếu SAI |
|---|---|---|---|---|---|
| M1 | BCTC bán niên 6T FY26 **soát xét** (AASC): LN mẹ 6T trong ±5% của 663,1; không ngoại trừ/nhấn mạnh; EPS sửa về ~661 | 30/11/2026 | 0,75 | giữ vùng | ngoại trừ/điều chỉnh LN >5% ⇒ hạ tâm ~1.000 đ + nâng WARNING |
| M2 | Q3FY26 (01/10–31/12/2026): LN mẹ quý ≥ 250 | 15/02/2027 | 0,55 | | < 150 cùng NMTT NC-II không giảm (bàn giao khựng) ⇒ XUỐNG ~10.000–10.500 |
| M3 | NMTT tổng 31/12/2026 + DT BĐS Q3 × 1,08 − NMTT 30/09 (thu mới thô) ≥ 1.000; hoặc NMTT xuất hiện dòng HH1–HH2 ≥ 300 | 15/02/2027 | 0,45 | cùng M2 ⇒ LÊN ~13.000–13.500 | thu mới < 500 hai quý liên tiếp ⇒ backlog cạn, hạ thặng dư HTK xuống kịch bản xấu |
| M4 | FY26 (01/04/2026–31/03/2027): LNST HN ≥ 2.000 **và** DT ≥ 5.000 | 15/05/2027 (BCTC Q4); kiểm toán 30/06/2027 | 0,40 | LÊN biên trên ~14.000+ nếu đi cùng M3 | LNST HN < 1.400 ⇒ tâm về ~10.500 |
| M5 | Biên gộp BĐS 9T FY26 ≥ 45% | 15/02/2027 | 0,70 | | < 40% ⇒ chuyển sang kịch bản xấu (~9.600) |
| M6 | Không có QĐ xử phạt/khởi tố mới liên quan CBTT/bên liên quan của TCH/CRV/HHS; BC quản trị bán niên 2026 liệt kê giao dịch bên liên quan (thuê VP, cổ tức nội bộ) | 31/03/2027 | 0,80 | giảm chiết khấu quản trị 5 điểm % ⇒ +~750 đ | QĐ mới ⇒ chiết khấu +10 điểm % ⇒ −~1.500 đ |

**Điều kiện đổi nhận định** (đối xứng):
- **LÊN** (tâm → ~13.500–14.400) nếu (M2 ∧ M3) đúng, hoặc HH1–HH2 công bố bán > 50% số căn.
- **XUỐNG** (tâm → ~9.600–10.500) nếu M2 sai kiểu "bàn giao khựng", M5 sai, hoặc M1 có ngoại trừ.

## 10. Ngành → doanh nghiệp (đọc ngành MÙ của Bobby, `kb/data_registry/market-state/sector_read_bds_nha_o_do_thi_phia_bac_20261031.md`, đọc SAU khi xong phần BCTC)

**Đọc của Bobby (tóm tắt):**
- Phân loại CYCLICAL 0,45 / STRUCTURAL 0,35 / ADMIN_GATED 0,20, độ tin cậy ambiguous.
- Hà Nội đang ở đầu → giữa pha suy về khối lượng: căn hộ bán Q3 −48 đến −66% YoY; thấp tầng hấp thụ 9%, thấp nhất 10 năm.
- **Hải Phòng trễ Hà Nội 2–4 quý**: cuối pha tăng → đầu pha chững. Chưa có số Q3.
- Lãi vay mua nhà cố định ~10,9%, thả nổi 13–15%.
- Bẫy đọc số: lợi nhuận 2026 phản ánh bán hàng 2024–25, nên có thể **đẹp nhất đúng lúc bán mới đang gãy**. Chỉ báo dẫn là NMTT và doanh số ký mới, không phải doanh thu.

**Áp vào TCH — "DD cần kiểm gì" (§6 của Bobby) đã kiểm thế nào:**

| # Bobby | Kiểm trên TCH | Kết quả |
|---|---|---|
| A1 quỹ đất theo dự án/giai đoạn | TM9(*) theo dự án + [SHS] cho số căn | một phần: có giá trị sổ theo dự án; **không có** ha/số sản phẩm còn lại từ BCTC |
| A2 % tiền SDĐ đã nộp | TM17: 2.992,9 đã nộp 6T (I.14 + 150 Tô Hiệu đủ); TM9 ghi CPDD NC-II/Green River/H2 "gồm tiền SDĐ"; NC-II một phần là **đất thuê trả hằng năm** tới 2073 (TM22b) ⇒ chịu bảng giá × K hằng năm | phần lớn đã nộp (ước lượng); tiền thuê hằng năm NC-II là rủi ro nhỏ còn mở |
| A3 truy thu tiền SDĐ | không thấy khoản tranh chấp/dự phòng phải trả (TM 322 dự phòng phải trả = 0) | không thấy |
| A4 sổ tồn đọng | không công bố | **chưa kiểm** |
| A5 giá vốn quỹ đất mới vs giá bán | **150 Tô Hiệu: 1.673 tỷ / 16.177 m² = ~103 tr/m² đất; ~1,68 tỷ tiền đất/căn** (998 căn theo SHS). Căn hộ HP phổ biến ~40 tr/m², hàng >55 tr/m² chiếm 26% (Bobby §2d). Căn ~70–80 m² ở 55–70 tr/m² ⇒ ~3,9–5,6 tỷ/căn (ước lượng) ⇒ **tiền đất ~30–43% giá bán** trước chi phí xây cao tầng 40 tầng. I.14: 1.322 tỷ / 18.778 m² đất = ~70 tr/m² đất | **biên quỹ đất mới mỏng hơn hẳn NC-II** (đất cũ, biên ~52%) ⇒ khớp cảnh báo "giai đoạn sau biên thấp hơn" (C13). Đã phản ánh: thặng dư HTK cơ sở 25% = ~30% trên đất cũ (~9.000) + ~8% trên đất mới (~3.000) (ước lượng) |
| B6 doanh số ký mới | không công bố | **chưa kiểm** — chỉ có proxy NMTT |
| B8 NMTT xu hướng 4 quý | ΔNMTT: +2.643 (Q2FY25) → +775 → +368 → **−893 (Q2FY26)** | mức tăng giảm 3 quý liền, nay **âm lần đầu**. Chưa đủ "2 quý giảm liên tiếp" của Bobby — **Q3FY26 là quý quyết định** (M3) |
| B10 hỗ trợ lãi suất / giảm giá ẩn | TM18: trích trước hỗ trợ lãi vay cho khách mua căn hộ **5,64 (đầu năm 0,51, ×11)**; CPBH "kinh doanh BĐS" 6T 85,7 vs 42,6 (×2); SHS nâng giả định CPBH 5% → 10% DT | tỷ lệ còn nhỏ (0,3% DT BĐS), nhưng **hướng đúng như Bobby cảnh báo**; nghĩa vụ hỗ trợ lãi suất còn lại ngoài bảng **chưa lượng hoá được** |
| B9 huỷ HĐ | hàng bán bị trả lại 6T 1,33 (chưa tách mảng) | không thấy dấu hiệu, chưa đủ dữ liệu |
| C14 lãi vay vốn hoá vào HTK | **0 vay** | không có |
| C16 CFO luỹ kế / LN ròng | FY24 + FY25 + 6T FY26: CFO 419 / LNST HN 2.295 = **0,18** | < 0,5 — **cờ**, nhưng nguyên nhân rõ: 3.000 tiền đất mới + tiền khách đã thu trước từ FY25. Cần đo lại qua cả chu kỳ khi NC-II bàn giao xong |
| D17–18 nợ vay, TPDN | 0 vay, 0 trái phiếu | đạt (điểm mạnh nhất so với ngành) |
| D19 ứng trước đối tác/đặt cọc/bên liên quan | trả trước NB 565 + phải thu khác 46 = **5,0% VCSH mẹ**; bên liên quan 0 (theo BCTC) | đạt (với lưu ý CBTT bên liên quan §6d) |
| E21 tập trung 1 tỉnh | ~toàn bộ HTK BĐS ở **Hải Phòng** (trừ 17B Bà Triệu 243 và Golden Land HN tồn nhỏ) | **>90% — cờ tập trung** |
| E21–22 cạnh tranh siêu dự án / khách ngoài tỉnh | NC-II và Green River đều ở **Thủy Nguyên**, nơi Bobby ghi nhận siêu dự án của 1 chủ đầu tư quốc gia chiếm 47% giao dịch thấp tầng Đông HP H1/2026 | cạnh tranh trực diện; không có số khách Hà Nội của TCH |
| F24 quản trị | §6d | WARNING trung bình |

**Hệ quả cho định giá:**
- Đọc ngành không đổi cơ chế NAV, nhưng nghiêng rủi ro về phía **tốc độ bán mới** (HH1–HH4, 150 Tô Hiệu, I.14) và **biên các dự án mới**. Lợi nhuận FY26 phần lớn là backlog đã thu tiền nên ít bị ảnh hưởng.
- Nếu nghiêng trọng số kịch bản theo đọc ngành (0,35/0,45/0,20), NAV trọng số là **~11.600** thay vì 11.950: cả hai đều trong ±2% giá hiện tại.
- ⇒ **Kết luận không đổi: xấp xỉ hợp lý, tâm ~11.600–11.950.** Không dùng nghiêng này để hạ vùng, vì Hải Phòng chưa có số Q3 xác nhận (forecast F11 của Bobby chấm 31/08/2027).
- **Bobby F12/F13 khớp đúng TCH:** DT FY26 tăng mạnh còn NMTT giảm. Nếu cả hai xảy ra trên toàn ngành, cần đọc lợi nhuận FY26 của TCH là **đỉnh chu kỳ bàn giao, không phải nền mới**.

## 11. Lệch nguồn BQ vs BCTC
- BQ `ticker_financial` mới nhất là 2026Q2 dương lịch (04–06/2026, phát hành 29/07), **chưa có** kỳ 07–09/2026. `PE` 39,8 trên BQ là cũ. Giá trị BQ của TCH là quý (khớp kiểm toán), **không** phải TTM.
- BQ `PB` 0,82 khác số tự tính 0,98 (VCSH mẹ). Có thể BQ dùng BVPS cũ 14.481 × số cp cũ; chưa truy nguyên.
- **CRV không có trong `tav2_bq.ticker`** dù đã niêm yết HOSE 10/10/2025, nên giá CRV phải lấy từ web (trễ). Đề xuất Winston bổ sung.
- BQ không có dữ liệu khối ngoại.

## 12. Số đã đối chiếu chéo 2 chỗ vs chưa kiểm

**Đã đối chiếu 2 nguồn độc lập:**
- KQKD Q2 DT/LNST ↔ GT.
- BS ↔ thuyết minh: tiền TM3, HTM TM4, HTK TM9/9(*), NMTT TM16, PTNB TM15, PT khác TM19, VCSH TM21.
- LN mẹ 6T: KQKD 663,14 ↔ BS 420b 663,14 ↔ TM21a.
- LN mẹ Q1 suy ra (125,42) ↔ BQ 125,4. FY24/FY25 LN mẹ BQ ↔ KT25.
- Tiền SDĐ TM17 (Q1 Q1HN + Q2 suy ra) ↔ tăng HTK 2 quỹ đất ↔ giá đấu I.14 [SHS].
- NMTT theo dự án Q1HN ↔ SHS.
- Số cp TM1.1 ↔ TM21d ↔ BQ OShares.
- Án phạt 295 = 92,5 + 65 + 137,5 (2 báo).

**Chỉ 1 nguồn / chưa kiểm:**
- DT Q1 theo mảng (SHS).
- CFO Q1 −1.596 (SHS).
- Giá đấu I.14 1.322, quy mô HH1–HH4 / 150 Tô Hiệu (SHS).
- Giá CRV (stockanalysis, trễ).
- Kế hoạch FY26 (báo).
- Tên ngân hàng "Sài Gòn Tài Lộc" (scan).
- Nhóm 7,37% uỷ quyền.
- HH Finance có phải người liên quan.
- HĐ thuê VP với công ty liên quan có còn không.
- Khối ngoại.
- BCTC riêng, BC thường niên, NQ ĐHĐCĐ 01/2026 (chưa tải).
- Mọi tham số NAV (ước lượng).

## Giới hạn
- BCTC 6T chưa soát xét; mọi số đọc từ ảnh scan.
- Không có tổng dự toán dự án, giá trị hợp đồng ký và số căn đã bán/còn lại ⇒ NAV phụ thuộc tham số tự đặt; vùng giá rộng (±20%).
- Chưa tải BCTC riêng, báo cáo thường niên, BC quản trị, trang CBTT `hoanghuy.vn/cong-bo-thong-tin/`.

## Nguồn web (truy cập 31/10/2026)
- Nhân Dân — phạt 380 triệu (TCH + Đầu tư tổng hợp HN): https://nhandan.vn/post-849025.html
- Báo Đầu Tư — chi tiết vi phạm TCH: https://baodautu.vn/vi-pham-hang-loat-quy-dinh-tai-chinh-hoang-huy-nhan-an-phat-d231955.html
- SHS cập nhật TCH 08/08/2026: https://s3-storage.shs.com.vn/shs-website/Cap_nhat_TCH_T8_2026_d5200d2ec5.pdf
- 24hmoney — kế hoạch FY26: https://24hmoney.vn/news/ctcp-dau-tu-dich-vu-tai-chinh-hoang-huy-tch-nam-ban-le-ban-giao-du-an-ky-vong-loi-nhuan-but-pha-trong-nien-do-tai-chinh-2026-c30a2811608
- CRV niêm yết HOSE 10/10/2025: https://nhadautu.vn/crv-tang-tran-phien-chao-san-von-hoa-dat-21000-ty-dong-d99830.html ; giá CRV: https://stockanalysis.com/quote/hose/CRV/
- NC-II 543 căn thấp tầng đủ điều kiện kinh doanh: https://nhadautu.vn/543-can-thap-tang-du-an-hoang-huy-new-city-ii-duoc-phep-kinh-doanh-d97221.html
