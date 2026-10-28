# DD — TV2 (CTCP Tư vấn Xây dựng Điện 2, PECC2, HOSE) · 2026-10-28 · job `Taylor_20261028_051709`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua, không lệnh, không wire. User quyết.
> Nguồn: **[Q3 tr.X]** = BCTC hợp nhất Q3/2026 (`src/q3_hopnhat.pdf`, trang PDF, ký duyệt 28/10/2026, CHƯA soát xét);
> **[H1 tr.X]** = BCTC hợp nhất bán niên 2026 đã soát xét UHY (`src/h1_hopnhat_soatxet.pdf`); **[GT]** = công văn giải trình
> 4270/PECC2-TCKT 28/10/2026; **[BQ]** = `tav2_bq.ticker` (giá đến 27/10/2026) / `tav2_bq.ticker_financial` (đến 2026Q2);
> **[web]** = báo chí, link ở §9. Phép tính: `calc.py` → `out.txt` (cùng thư mục). Số tự đặt gắn **(ước lượng)**.
> Nền ngành: Bobby `kb/data_registry/market-state/sector_read_power_consulting_20261028.md` (không lặp lại ở đây).
> **BCTC riêng (`q3_rieng.pdf`) KHÔNG đọc** trong phiên này — chỉ dùng số LNST riêng từ [GT].

## 0. Kết luận

**Verdict: NON tại 26.050 (27/10/2026)** — lợi nhuận bùng nổ là THẬT về kế toán, nhưng **chất lượng thấp hơn tiêu đề**:
(i) ~44% LNTT 9T đến từ **lãi tiền gửi trên tiền ỨNG của khách** (float sẽ tiêu khi làm EPC); (ii) phần tăng trưởng doanh
thu lớn nhất là **EPC cho chính công ty liên kết CMC (Cà Mau, TV2 sở hữu 25,11%) mà gần như CHƯA THU TIỀN** — phải thu CMC
666 tỷ = 50% VCSH; (iii) CFO Q3 **âm 125 tỷ**; (iv) trừ float, tiền ròng "của cổ đông" ≈ **0** (ước lượng). Giá 26.050 = PB 1,32,
PE TTM 8,3 — đắt nhất nhóm PECC, cao hơn giá trị kỳ vọng ~22.900 (ước lượng).

| Tiêu chí (khung `calculated_fear_state_backstop.md`) | Áp dụng? | Phán quyết | Bằng chứng |
|---|---|---|---|
| §2 #1 Scandal cá nhân, tách lõi | Có (warning) | ⚠️ KHÔNG tách sạch | Vụ án EVNNPT/PC1 — dự án 500kV Quảng Trạch–Phố Nối mạch 3 = đúng lõi tư vấn lưới [web; H1 tr.67 TM46]. Giống TV1. Theo luật fleet 27/09: chỉ WARNING, không tự hạ verdict |
| §2 #2 NN chi phối có động cơ backstop | Có | ⚠️ một phần | EVN 51% [web VietnamFinance 23/05/2026, chưa đối chiếu danh sách cổ đông]; nhưng doanh thu từ EVN 9T chỉ ~100 tỷ/1.199 (≈8%) [Q3 tr.42] ⇒ EVN là chủ, không phải khách chính |
| §2 #3 CF_OA ≥ NP, lõi tạo tiền | Có | ❌ | CFO 9T +858,6 [Q3 tr.7] nhưng **toàn bộ nhờ tiền ứng** (+1.432); trừ tiền ứng ≈ −573 tỷ; CFO Q3 = −125,3 [Q3 tr.7 − H1 tr.10] |
| §2 #4 / §2.5 #2 Bảng cân đối sống sót | Có | ✅ | Vay chỉ 152,8 tỷ NH [Q3 tr.4]; tiền+HTM 2.104 tỷ; không có rủi ro thanh khoản trong 12 tháng |
| §2 #5 / §2.5 #4 Sàn định giá (PB≲1,2 hoặc PE<5 nén) | Có | ❌ | PB **1,32**, PE TTM **8,3**; comps TV1 PB 0,97/PE 3,3, TV4 PB 1,06/PE 5,8, TV3 PB 0,80/PE 7,3 [BQ] |
| §2.5 #1 Chu kỳ, không cấu trúc | Một phần | n/a | Không có khủng hoảng ngành để "mua sợ hãi": Bobby = STRUCTURAL_UPCYCLE khối lượng, ADMIN_GATED nhịp |
| §2.5 #3 Leader chi phí thấp | Không áp dụng | — | Ngành tư vấn oligopoly định mức nhà nước (Bobby §3), không cạnh tranh chi phí |
| "Đáy chưa tới" | Ngược chiều | — | Đây là **đỉnh lợi nhuận** (float + EPC CMC), không phải đáy |

**Đây KHÔNG phải ca fear-buy**: giá −24,4% YTD [BQ] nhưng lợi nhuận +254% 9T ⇒ thị trường đang chiết khấu pháp lý + chất lượng
lợi nhuận, không phải hoảng loạn mù. **Giá ≤ ~19.500 (hoặc ≤ ~17.300 nếu base 7x — xem §13) chỉ KÍCH HOẠT CHẠY LẠI DD, KHÔNG tự đổi verdict**; muốn QUALIFY phải đồng thời qua cổng §2 #3 (phải thu CMC −30% và CFO năm trừ tiền ứng ≥ 0).

## 1. Kiểm chứng số Mike đã đọc

| Mike đọc | Kiểm | Kết quả |
|---|---|---|
| LNST HN Q3 61,04 vs 13,44 (+354%) | [GT], [Q3 tr.6] 61.040.762.481 | ✅ khớp tuyệt đối |
| Riêng 56,50 vs 14,20 | [GT] | ✅ (chưa đọc BCTC riêng) |
| TTS 4.822,9 vs 2.979,9; NPT 3.488 vs 1.704 | [Q3 tr.3-5] | ✅; self-check TTS − (NPT+VCSH) = 0 [out.txt] |
| Người mua trả trước NH 2.416 vs 984 | [Q3 tr.4] 2.416,36 vs 984,35 | ✅ (+ dài hạn 2,24 tỷ Mỹ Lý–Nậm Mô, không đổi) |
| CP phải trả NH 249 vs 36; vay NH 152,8 vs 81,2 | [Q3 tr.4] | ✅ |
| Đầu tư liên kết 427,7 | [Q3 tr.3, tr.23] | ✅ |
| Q2/26 DT 438, LNST 48,5; 6T ~102 | [BQ] 2026Q2 rev 438,1, np 48,5; 9T 163,3 − Q3 61,0 = 102,3 | ✅ |
| Giá 27/10 26.050, ADV 100-200k cp | [BQ] 26.050; ADV20 127,6k cp = 3,27 tỷ/ngày | ✅ |
| Giải trình "do DT SXKD và DT tài chính tăng" | Đúng nhưng thiếu: không nói DT tăng chủ yếu từ **bên liên quan CMC** | ⚠️ |

**Lệch nguồn BQ (ghi, không chọn im lặng):** BQ `ticker_financial` chưa có 2026Q3. `Cash_P0` BQ = chỉ tiền+tương đương (2025Q4:
928 vs BCTC 926,3) — **thiếu HTM** (185,9 đầu năm; 1.044,5 cuối Q3). `NP_P0` BQ cộng 2025 = 94,6 vs báo chí 95,6 (lệch 1 tỷ, chưa
tách mẹ/NCI). H1/2025 EPS bị **điều chỉnh hồi tố 483 → 320** [H1 tr.68 TM42.3] (trình bày lại theo TT99/TT43 + phương pháp VCSH
liên kết [Q3 tr.9 mục 7]) — số so sánh cùng kỳ 2025 đã là số sau điều chỉnh.

## 2. (A) Lợi nhuận từ đâu — tách lớp [Q3 tr.6, tr.37-39]

| Tỷ đồng | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| DT thuần | 517,1 | 253,8 | 1.199,2 | 769,5 |
| LN gộp (biên) | 90,3 (17,5%) | 40,7 (16,0%) | 188,6 (15,7%) | 118,9 (15,5%) |
| BH + QLDN | 42,9 | 34,8 | 112,3 | 95,8 |
| **EBIT lõi** | **47,5** | 5,9 | **76,3** | 23,2 |
| DT TC − CP TC | 27,3 | 3,4 | **85,6** | 5,7 |
| Lãi liên kết | 0,7 | 4,5 | 31,3 | 23,9 |
| Khác ròng | 1,0 | 1,0 | 2,3 | −0,4 |
| **LNTT** | 76,4 | 14,8 | 195,4 | 52,3 |
| Tỷ trọng lõi / TC / LK | 62 / 36 / 1% | 40 / 23 / 31% | **39 / 44 / 16%** | 44 / 11 / 46% |

- **Tài chính**: lãi tiền gửi/cho vay 9T **87,1 tỷ** vs 3,6 [Q3 tr.38 TM23]; Q3 DT TC 35,7 ⇒ năm hoá ~143 tỷ trên tiền+HTM 2.104 ≈ 6,8%
  (ước lượng, số dư cuối kỳ, chưa bình quân). Tiền gửi tập trung **MB Sở Giao dịch 2** [Q3 tr.20-22]. Thêm lãi trả chậm 5,5 tỷ — phần lớn
  **tính trên CMC** [Q3 tr.43] (lãi dồn tích, chưa thu).
- **Doanh thu theo mảng**: BCTC KHÔNG tách tư vấn/EPC (TM21 chỉ chia "bán hàng & dịch vụ 1.179,1 / bán điện 16,7 / vật tư 3,4" [Q3 tr.37]).
  Tách gián tiếp qua bên liên quan [Q3 tr.42-43; H1 tr.63]:
  - **CMC (liên kết 25,11%)**: DT 9T **478,7** (H1 244,4 ⇒ **Q3 ≈ 234,4 = 45% DT Q3**), kèm dòng điều chỉnh **−58,1** chưa rõ bản chất
    (có thể loại trừ lãi chưa thực hiện giao dịch với liên kết — **chưa xác minh**).
  - Khối EVN (các ban QLDA, Truyền tải, GENCO): cộng tay ≈ **100 tỷ 9T** (ước lượng, cộng ~25 dòng [Q3 tr.42]); các ban QLDA truyền tải giảm mạnh
    YoY (miền Bắc 30,9 → 5,6; miền Trung 21,9 → 5,7) — khớp vụ án + trượt tiến độ lưới (Bobby).
  - Phần còn lại ~620 tỷ (ước lượng) = EPC eREX sinh khối + PVN + tư nhân + tư vấn khác — không tách được từ BCTC.
- **Chi phí theo yếu tố**: dịch vụ mua ngoài 594,6 vs 278,1 (+316) [Q3 tr.39 TM28] ⇒ tăng trưởng là **EPC (thiết bị/thầu phụ chuyển giao)**,
  không phải giờ kỹ sư. Nhân công +24% (325 vs 263).
- **Bền vs một lần**: (bền-ish) EBIT lõi tư vấn; (tạm) lãi trên float — giảm dần khi eREX giải ngân thiết bị tới COD ~2028; (một lần/
  chu kỳ dự án) EPC CMC — Tân Thuận GĐ3 25MW mục tiêu vận hành Q4/2026 [web] ⇒ **dòng doanh thu CMC có thể gần hết sau Q4/2026**
  (giả định: hợp đồng CMC 2026 = Tân Thuận GĐ3 — **suy luận, chưa có nguồn xác nhận PECC2 là EPC GĐ3**). Lãi liên kết theo mùa gió/thuỷ (Q3 0,7).
- **Q4 mùa vụ** [BQ NP]: Q4/2025 = 52% LN năm; 2024 31%; 2023 25%.

## 3. (B) Người mua trả tiền trước 2.418 tỷ [Q3 tr.31 TM13]

| Khách | 30/09/26 | 01/01/26 |
|---|---|---|
| **Điện Sinh khối eREX Yên Bái** | **929,4** | 212,1 |
| **Điện Sinh khối eREX Tuyên Quang** | **914,1** | 215,3 |
| CN PVN — Ban QLDA chuyên ngành điện | 467,1 | 470,1 |
| Khác + bên liên quan (EVN) | 105,8 | 83,8 |
| Dài hạn (Mỹ Lý–Nậm Mô) | 2,2 | 2,2 |

- Hai hợp đồng EPC eREX (Nhật): **Yên Bái 1 50MW ký 07/11/2025, COD đầu 2028**; Tuyên Quang 50MW ký ~12/2025 [web mekongasean, eREX].
  Giá trị hợp đồng **không công bố**. Nhà cung cấp đã được ứng: Isgec (lò hơi, Ấn Độ) 69,5; Triveni Turbine 25,3; HAMATRA 46,4; Toshiba T&D 45,6;
  Licogi Đông Anh 25,3 [Q3 tr.26]; nợ China Energy Engineering Guangdong Electric Power Design Institute 87,0 [Q3 tr.31] (thuê thiết kế TQ).
- **Backlog ngầm (ước lượng)**: 50MW sinh khối ~2.000-2.500 tỷ TMĐT/nhà máy (giả định thị trường, chưa kiểm) ⇒ 2 hợp đồng ~4.000-5.000 tỷ;
  tiền ứng 1.843 ≈ 37-46% giá trị — **cao bất thường** so tỷ lệ ứng EPC thường 10-30% (ước lượng) ⇒ hoặc hợp đồng lớn hơn ước tính,
  hoặc ứng theo mốc mua thiết bị. Backlog eREX ~2,2-2,7x DT 12 tháng (~1.834 tỷ: 9T/26 1.199 + Q4/25 634,5 [BQ 2025 1.404]).
  **Biên EPC thấp** (thiết bị nhập chuyển giao) ⇒ backlog lớn ≠ lợi nhuận lớn.
- PVN 467 tỷ đứng yên cả năm — dự án chưa chạy (chưa xác định dự án nào; **chưa đo**).
- **Tiền ròng thật của cổ đông** = tiền+HTM 2.104,2 − vay 152,8 − float ròng (ứng 2.418,6 − trả trước NCC 293,0 − dở dang 119,5 = 2.006,2)
  ≈ **−55 tỷ** (đầu năm +108) (ước lượng; float ròng là xấp xỉ, chưa trừ phần lãi gộp sẽ hưởng). ⇒ **2.104 tỷ tiền KHÔNG phải của cổ đông**.
- **Rủi ro**: (1) lãi trên float ~100-140 tỷ/năm trước thuế (ước lượng) sẽ co lại khi giải ngân thiết bị 2027; (2) hoàn ứng nếu eREX dừng —
  eREX dùng vốn ADB + JCM [web], rủi ro thấp-trung bình; (3) TV2 gánh rủi ro chi phí EPC giá cố định (tỷ giá INR/USD thiết bị).

## 4. (C) Chi phí phải trả 249 tỷ, quỹ, ghi nhận doanh thu

- CP phải trả = **trích trước chi phí công trình 248,2** (đầu năm 34,7) [Q3 tr.33 TM16]. Đây là ghi nhận CHI PHÍ đã phát sinh chưa có hoá đơn
  — **chiều thận trọng**, không phải giấu chi phí. Nhưng đi kèm DT EPC tăng ⇒ cần xem Q4 có hoá đơn khớp không.
- Chính sách: HĐ xây dựng ghi DT theo **phần việc hoàn thành ĐƯỢC KHÁCH XÁC NHẬN** [Q3 tr.15 mục 11.1] (VAS15 cách 2) — không phải POC tự ước.
  Rủi ro: khách xác nhận là **CMC (liên kết của chính TV2)** ⇒ chứng từ xác nhận đến từ bên liên quan.
- Không có khoản "phải thu theo tiến độ HĐXD" (mã 134 = 0) [Q3 tr.2]. Dở dang 119,5 vs 42,7 [Q3 tr.27 TM7].
- Quỹ khen thưởng phúc lợi 67,9 vs 42,4 [Q3 tr.4] — trích từ LN 2025, bình thường. Phải trả người lao động giảm 215,5 → 112,0 (chi lương/thưởng).

## 5. (D) Phải thu, dự phòng, dòng tiền [Q3 tr.25, tr.27, tr.43-44; H1 tr.64]

- Phải thu KH 1.386,2 (đầu năm 919,9); **bên liên quan 992,4** (534,4). **CMC: 208,1 → 367,1 (30/6) → 666,4 (30/9)**; Q3 tăng 299,2 > DT Q3 từ
  CMC 234,4 (+VAT) ⇒ **thu tiền Q3 từ CMC ≈ 0** (ước lượng). 666 tỷ = **50% VCSH**, cao hơn cả giá trị đầu tư vào CMC (188,6 tỷ ghi sổ,
  lỗ luỹ kế −40,2 tỷ trong phần TV2 [Q3 tr.23]). Đây là **vendor financing cho bên liên quan** — điểm yếu lớn nhất của ca này.
- Hậu Giang sinh khối (sở hữu 10%, đã dự phòng 4,6 tỷ khoản đầu tư) nợ 63,6-73,6 tỷ, không giảm cả năm.
- Nợ quá hạn 120,4 tỷ, dự phòng 71,0 (+20 tỷ YTD; dự phòng vào QLDN 9T 20,0 [Q3 tr.39]); quá hạn >3 năm 37,2 tỷ [Q3 tr.27].
- Trả trước người bán 293,0 (21,1) — thiết bị EPC eREX, khớp §3.
- CFO 9T **+858,6**; H1 +984,0 ⇒ **Q3 −125,3**; 9T trừ tăng tiền ứng ≈ **−573** [out.txt]. Thu lãi tiền gửi 9T bằng tiền 109,2 [Q3 tr.7] — lãi là tiền thật.
- Vay NH 152,8 tỷ khi tiền dư 2.104: phần thế chấp 200 tỷ tài sản tại công ty con PECC2 Dịch vụ & Kỹ thuật Năng lượng [H1 tr.68 TM43] —
  vay ở con, tiền ở mẹ (chưa kiểm mục đích).

## 6. (E) Khách hàng, cổ đông, room ngoại

- EVN ≈ 8% DT 9T (ước lượng, §2) — **không phải khách chính** năm 2026; khách chính = CMC (liên kết) + eREX + PVN.
- EVN sở hữu 51% [web, chưa đối chiếu]. Cơ chế backstop của EVN với TV2 yếu hơn TV1 (TV1 có thuỷ điện Sông Bung 5 tạo tiền độc lập).
- Thông báo room ngoại 14/09/2026: **KHÔNG tìm thấy** nội dung qua web search — **chưa đọc**, không đánh giá được tác động.
- Lao động 1.432 người [Q3 tr.9]. ĐHĐCĐ 30/06/2026: KH DT HN 2.503 tỷ, LNTT 125, LNST 100, cổ tức ≥10% [web]; 9T đạt LNST **163%** KH, DT 48% KH.

## 7. (F) Định giá tại 26.050 [BQ, out.txt]

- Vốn hoá **1.759 tỷ** (67,526 tr cp [Q3 tr.8]); BVPS mẹ 19.708; **PB 1,32**; LNST TTM ~211 (9T mẹ 162,2 + Q4/25 48,8 [BQ]) ⇒ **PE 8,3**.
- EV/net cash: net cash thô 1.951 làm EV trông ≈ 0 — **sai** vì tiền là float (§3). Net cash chuẩn hoá ≈ 0 ⇒ EV ≈ vốn hoá.
- Cổ tức 1.000 đ/cp/năm nhiều năm [BQ Dividend_1Y] (3,8% tại 26.050); năm 2025 chia 10% [Q3 tr.37].
- Comps [BQ, TTM tới 2026Q2]: TV1 PE 3,3/PB 0,97 (có thuỷ điện SB5); TV4 PE 5,8/PB 1,06; TV3 PE 7,3/PB 0,80. Cả 3 **ADV <1 tỷ/ngày** — so sánh
  bội số thô, chưa chuẩn hoá. TV2 đắt nhất nhóm.

**Kịch bản LNST 2027 (ước lượng — trọng số chủ quan):**

| | Giả định | LNST 2027 | Giá trị/cp |
|---|---|---|---|
| **Bear** 30% | CMC không trả được một phần ⇒ dự phòng ~200 tỷ trước thuế (~160 sau thuế); tư vấn EVN đi ngang; lãi float ~50 | ~110 thường xuyên + hit một lần | **~13.900** (0,8x book sau dự phòng) |
| **Base** 50% | eREX EPC chạy (DT ~1.500, biên ~8%) + tư vấn; float giảm còn TC ròng ~60; LK 35; thuế 20% | ~170 | **~22.700** (9x) |
| **Bull** 20% | Thêm gói 500kV mới/HĐ hạt nhân ký thật; CMC thu đủ | ~250 | **~37.000** (10x) |

Giá trị kỳ vọng **~22.900** (−12% so giá). Ngưỡng biên an toàn 15%: **~19.500**. 2026E (ước lượng): 9T 163,3 + Q4 ~50-70 ⇒ ~215-235 tỷ;
2026 cao hơn 2027 base vì đỉnh lãi float + EPC CMC.

**Diễn biến giá [BQ]**: YTD −24,4% (34.450 → 26.050); từ đỉnh 43.050 (02/03) −39,5%; từ 21/05 −18,5%; đáy 23.650 (27/07) → +10,1%.
Phiên 22/05 (sau CBTT khởi tố 21/05 17:24): **−4,5%**, KL 1,54 tr cp (~5x bình thường). Phiên 29/07 (sau KQ Q2): **+7,0%**. Phiên 27/08
(soát xét H1): +2,7%. Giá dưới MA200 (30.994) — thị trường đã chiết khấu pháp lý nhưng KHÔNG thưởng cho LN Q2 bùng nổ.

## 8. (G) Mốc khoá trước + ngưỡng đổi quan điểm

| Mốc | Ngày dự kiến | Đổi NON → AMBIGUOUS/QUALIFY nếu | Cứng hoá NON nếu |
|---|---|---|---|
| BCTC Q4/2026 + kiểm toán năm 2026 | 01-03/2027 | Phải thu CMC giảm ≥30% (≤470 tỷ) **và** CFO năm (trừ tăng tiền ứng) ≥ 0 | Phải thu CMC >700 tỷ hoặc dự phòng CMC; ý kiến kiểm toán ngoại trừ |
| Kiểm toán FY2026 | ĐHĐCĐ 2027 | Big4/kiểm toán không ngoại trừ | Không chọn được kiểm toán / ngoại trừ (tiền lệ TV1) |
| Tân Thuận GĐ3 COD | Q4/2026 [web] | COD + PPA ký ⇒ CMC có dòng tiền trả nợ | Trượt COD sang 2027, CMC không có giá bán điện |
| Vụ án EVNNPT/PC1 | — | Kết luận điều tra không quy trách nhiệm pháp nhân TV2 | Pháp nhân TV2 bị truy tố / cấm dự thầu EVN |
| HĐ mới (EVN 500kV, hạt nhân NT1 — Bobby F3) | 2027 | HĐ ký có giá trị công bố | — |
| **Giá** | bất kỳ | ≤ ~19.500 chỉ kích hoạt chạy lại DD (không đổi verdict một mình; sửa theo skeptic) | — |

## 9. (H) Thanh khoản / capacity

ADV20 **3,27 tỷ/ngày** (127,6k cp), ADV60 2,95, trung vị 60 phiên 2,58 [BQ]. Gom ≤15-20% ADV (tiền lệ TV1) ⇒ ~0,4-0,6 tỷ/ngày ⇒
10 tỷ cần ~17-25 phiên. Trần sleeve ≤0,5-1,0% NAV (tiền lệ TV1/DGC). Thanh khoản tốt hơn TV1 ~4-5x nhưng vẫn mỏng cho thoát nhanh khi có tin xấu.

## 10. Pháp lý / quản trị — WARNING (luật fleet 27/09: không tự hạ verdict)

- ⚠️ **05/2026: khởi tố Chủ tịch Nguyễn Chơn Hùng + KTT Bùi Thị Ngọc Lý** trong vụ án tại EVNNPT, PC1 và các công ty liên quan
  [H1 tr.67 TM46; cbtt 21/05/2026]; dự án trung tâm 500kV Quảng Trạch–Phố Nối mạch 3 [web]. Cùng vụ: Chủ tịch TV1, lãnh đạo PC1, PECC3 [web].
  ⇒ **chạm lõi tư vấn lưới** (scandal-di-cư cấp độ ngành), nhưng mảng tăng trưởng 2026 (EPC CMC/eREX) KHÔNG nằm trong vụ án theo nguồn đã đọc.
- ⚠️ Kiểm toán đổi **EY (FY2025, chấp nhận toàn phần) → UHY (soát xét H1/2026)**; H1 kết luận chấp nhận + **đoạn nhấn mạnh** vụ khởi tố [H1 tr.5-6].
  Q3/2026 **chưa soát xét**, lập bởi phụ trách kế toán mới Hoàng Thụy Hoài Yến (bổ nhiệm NQ HĐQT 17/07/2026; trưởng phòng TCKT từ 28/05) [H1 tr.69; Q3 tr.41].
- ⚠️ Nhân sự: Chủ tịch mới Phạm Liên Hải từ 30/06/2026 (trước là TV HĐQT kiêm PTGĐ); ông Hùng vẫn nhận 537,6 tr lương 9T (tới 30/04) [Q3 tr.41].
- ⚠️ Giao dịch bên liên quan lớn: DT từ CMC 479 tỷ, phải thu 666 tỷ, lãi trả chậm tính trên CMC — rủi ro định giá chuyển giao/ghi nhận.
- Văn phòng Myanmar đóng 06/02/2026, mở Lào 15/01/2026 [Q3 tr.9].

## 11. Điểm yếu tự nhận (cho fundamental-skeptic tấn công)

1. Không tách được DT eREX vs khác — "~620 tỷ còn lại" là phần dư, có thể chứa khoản bất thường khác.
2. Giả định CMC 2026 = Tân Thuận GĐ3 chưa có nguồn; nếu là dự án khác lớn hơn, dòng DT CMC có thể kéo dài (bull) hoặc phải thu kẹt lâu hơn (bear).
3. Dòng −58,1 tỷ của CMC chưa hiểu bản chất — có thể làm sai số DT Q3 CMC (234 vs ~176).
4. Giá trị hợp đồng eREX và tỷ lệ ứng 37-46% là ước lượng thị trường, không có nguồn.
5. "Net cash của cổ đông ≈ 0" dùng float ròng thô; chưa trừ phần lãi gộp EPC sẽ hưởng ⇒ có thể thấp hơn thực ~100-300 tỷ.
6. Trọng số kịch bản và bội số 7-10x là chủ quan; bear giả định dự phòng 200 tỷ không có bằng chứng CMC mất khả năng trả.
7. Doanh thu EVN ~100 tỷ là cộng tay từ ảnh scan — có thể sót dòng.
8. Chưa đọc BCTC riêng và chưa đọc thông báo room ngoại 14/09; chưa kiểm EVN 51% với danh sách cổ đông.
9. Comps PECC thanh khoản quá thấp để làm neo bội số đáng tin.
10. Tỷ lệ lãi 6,8% tính trên số dư cuối kỳ, không bình quân — có thể phóng đại/giảm lãi suất thực.

## 12. Nguồn web
- Kế hoạch 2026 / ĐHĐCĐ: https://doanhnhan.baophapluat.vn/giua-bien-dong-nhan-su-cap-cao-pecc2-tv2-dat-muc-tieu-lai-100-ty-dong-don-luc-cho-dien-hat-nhan-va-lng.html ; https://www.dnse.com.vn/senses/tin-tuc/chu-tich-nguyen-chon-hung-bi-bat-doanh-nghiep-cong-bo-tai-lieu-quan-trong-35236798
- EVN 51%: https://vietnamfinance.vn/pecc2-trung-loat-goi-thau-tai-evn-va-cac-don-vi-thanh-vien-d145186.html
- eREX EPC: https://mekongasean.vn/pecc2-tiep-tuc-lam-tong-thau-xay-dung-nha-may-dien-sinh-khoi-50mw-cua-erex-48402.html ; https://en.evn.com.vn/d/en-US/news/PECC2-and-EREX-sign-EPC-contract-for-Yen-Bai-1-Biomass-Power-Plant-project-60-206-501072
- CMC / Tân Thuận: https://tapchicongthuong.vn/khanh-thanh-du-an-nha-may-dien-gio-tan-thuan-75mw-88265.htm ; https://vneconomy.vn/ca-mau-se-co-them-nha-may-dien-gio-615-trieu-kwh-van-hanh-cuoi-nam-2026.htm
- Vụ án: https://vietnamfinance.vn/khoi-to-chu-tich-cong-ty-xay-dung-dien-2-nguyen-chon-hung-d145156.html ; https://vietnamfinance.vn/evnnpt-khuyet-ca-2-ghe-chu-tich-va-tong-giam-doc-evn-dieu-nguoi-the-chan-d145971.html
- BQ: `tav2_bq.ticker` (TV1-4 đến 2026-10-27), `tav2_bq.ticker_financial` (đến 2026Q2/Q3 TV3).

Không gọi fundamental-skeptic (Mike điều phối bước đó theo skill due-diligence).

## 13. Phản biện fundamental-skeptic (28/10/2026) — **CONFIRMED, confidence high**; sửa đổi đã áp dụng
20 số then chốt tự kiểm trên ảnh BCTC: 0 sai. NON @26.050 đứng vững. Bổ sung theo required_change:
1. **Giá ≤19.500 = kích hoạt chạy lại DD, không đổi verdict** (đã sửa §0, §8).
2. **Độ nhạy bội số base**: 9x cao hơn mọi comp (TV1 3,3 / TV4 5,8 / TV3 7,3). Base 7x ⇒ giá trị kỳ vọng ~20.400, ngưỡng 85% ~17.300. NON vững: cần trọng số bull ≥~35% thì giá trị kỳ vọng mới vượt 26.050.
3. **BCTC riêng** (skeptic đọc, tr.6/34-35/41-42): dòng −58,1 của CMC là bút toán chỉ ở hợp nhất (riêng ghi 478,7 gộp) ⇒ DT CMC ròng hợp nhất 9T 420,6, tỷ trọng "45% DT Q3" có thể thực ~34%. Công ty mẹ: biên gộp 9T chỉ **9,7%** (DT 989,4; LN gộp 96,5); EBIT lõi mẹ ~36 tỷ vs TC ròng ~111 tỷ (~74% LNTT mẹ, có thể gồm cổ tức con — chưa tách).
4. **CFO Q2 cũng âm (−62,7)** ⇒ âm 2 quý liền (Q2, Q3).
5. **Phơi nhiễm CMC = phải thu 666,4 + đầu tư 188,6 = 855 tỷ = 64% VCSH**, không dự phòng. Kịch bản bear nặng (xoá ~50% phơi nhiễm) ⇒ giá trị ~10-11k.
6. **Cổ tức FY2025 phải trả 67,97 tỷ** (10%, chưa chi tại 30/9; BQ corporate_action chưa có ex-date).
7. **Cờ chất lượng dữ liệu (Q3 chưa soát xét)**: phải thu CMC TM3 657,3 vs TM32 666,4; DT Hậu Giang H1 14,06 → 9T 1,335 (nghi đảo ~12,7 tỷ với bên đang nợ); nợ quá hạn 6T-1 năm 2,2 → 47,3 tỷ (chưa rõ con nợ); dòng 27 LCTT 109,2 gồm 5,2 tỷ cổ tức.
8. **Base rate chu kỳ EPC của chính TV2**: 2020-21 DT 1,0-1,6 nghìn tỷ/quý, LNST đến ~101 tỷ/quý [BQ], rồi 2022-25 về ~13-20 tỷ/quý; phải thu cũ còn kẹt (Vĩnh Tân 54 tỷ, quá hạn >3 năm 37 tỷ).
9. **Pháp lý bổ sung**: họp báo Bộ Công an 02/07 nêu 13 đơn vị vi phạm gồm "các công ty tư vấn xây dựng điện"; vụ án có nhóm tội về kế toán, KTT cũ bị khởi tố. Chưa có pháp nhân TV2 bị khởi tố. Chỉ WARNING (luật 27/09).
10. Trục lịch sử chính nó: PB 1,32 vs MA5Y 1,70 (SD 0,34) ⇒ chỉ −1,1 SD (PNJ −2,6): §2 #5 trượt rõ.
Còn mở: đối chiếu EVN 51% với danh sách cổ đông; xác nhận hợp đồng CMC = Tân Thuận GĐ3; nội dung thông báo room ngoại 14/09.
