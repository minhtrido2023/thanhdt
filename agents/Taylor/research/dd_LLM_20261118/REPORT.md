# DD — LLM (Tổng Công ty Lắp máy Việt Nam – CTCP, Lilama; UPCoM) · 2026-11-18 · job `Taylor_20261118_122349` → VÒNG 2 job `Taylor_20261118_124655` (đã áp fundamental-skeptic r1 REFUTED — 13 đính chính, xem Phụ lục E)

> Chỉ nghiên cứu, không phải khuyến nghị mua. Không đặt lệnh, không wire. Pháp lý chỉ ghi WARNING (luật 27/09).
> Ký hiệu nguồn:
> - **[HN pX]** = BCTC hợp nhất Q3/2026, ký 27/10/2026 (`src/bao_cao_tai_chinh_hop_nhat_q3.2026_vie-da_nen.pdf`). pX là số trang PDF; đã render ảnh `png/hn_pXX.png` và đọc từ ảnh. Lớp text OCR bị lệch cột (xem §2).
> - **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker`.
> - **[GT-Q2]** = giải trình LNST Q2, CV 23/TCT-TCKT ngày 30/07/2026.
> - **[SX pX]** = BCTC hợp nhất bán niên 2026 ĐÃ SOÁT XÉT (AASC, `src/bchn_lilama_30.06.26_tv.pdf`, 57 trang, render toàn bộ `png/bn_pXX.png`).
> - **[RG]** = BCTC riêng Q3/2026 (`png/rg3_p03–04`); **[GTR-Q2]**/**[GTR-6T]** = giải trình LNST BCTC riêng Q2 (CV 30/07/2026) và 6T (CV 608/TCT-TCKT 28/08/2026), `src_r2/`.
> - **[KT25]** = BCTC kiểm toán 2025 + CV 197/TCT-TCKT giải trình ngoại trừ; **[HNX381]** = QĐ 381/QĐ-SGDHN 06/04/2026 duy trì diện cảnh báo + CV 245/TCT-TCKT 17/04/2026 (`src_r2/`).
> - **[Web]** = báo chí, có URL ở mục Nguồn.
> - **[Bobby]** = `kb/data_registry/market-state/sector_read_epc_lap_may_20261118.md`.
>
> Mọi số do tôi tự đặt đều gắn nhãn **(ước lượng)**. Mô hình tái lập: `model/calc.py` + `model/assumptions_LLM_20261118.json`, md5 rev2 `aaaeec2149986398055371ea535850ea` (rev1 `dea9f474…` giữ ở `model/assumptions_LLM_20261118_rev1.json`). Output: `model/calc_output.txt` (khối `===== REV2 =====`); bản v1: `model/calc_output_rev1.txt`.

## 0. Kết luận (VÒNG 2 — NHÃN ĐỔI)

**Giá 33.300 đ (18/11/2026) = 1,35 lần tâm giá trị 24.599 đ ⇒ ĐẮT so với giá trị nội tại.** Vòng 1 ghi "quanh hợp lý, 1,05×" là SAI vì hai lỗi: (i) biên gộp cơ sở 7% không có cơ sở độc lập, nay hạ về **trung vị lịch sử 4,5%**; (ii) kịch bản xấu dùng phương pháp khác (thu nhập thặng dư) với cơ sở/tốt (SOTP), nay **cả ba kịch bản cùng SOTP**. Vùng sau chiết khấu thanh khoản **3.630–39.728**; mốc 0,85×tâm = **20.909**. Giá chỉ "hợp lý" nếu biên gộp cơ sở bền vững ≥ **10,3%** (gấp 2,3 lần trung vị 9 năm) — chưa có bằng chứng nhiều chu kỳ.

- **Lợi nhuận "kỷ lục" phần lớn KHÔNG bền — chính công ty xác nhận.**
  - LNTT 9T/26 = 904,5 tỷ. Trong đó 290,5 tỷ là khoản một lần đã gọi tên được:
    - hoàn nhập dự phòng bảo hành ròng 227,1 [HN p41 TM31];
    - lãi thanh lý tài sản cố định 61,0 [HN p42 TM33–34];
    - hoàn nhập bảo hành khác 2,3.
  - Phần còn lại mang **biên gộp quyết toán**: 9T là 31,3%, Q3 là 51,2%. Giải trình 6T BCTC riêng [GTR-6T] viết thẳng: LN gộp 6T tăng 85,06 → 576,89 tỷ "chủ yếu do quyết toán một số dự án ở giai đoạn kết thúc, cho biên cao" + hoàn nhập bảo hành Q2.
  - GPM TTM 2017Q3–2024Q4: trung vị **4,55%** (30 quý); GPM năm 2017–2025: 4,2 / 5,0 / 5,9 / 4,5 / 5,3 / 3,1 / 2,4 / 1,7 / 7,0% [BQ].
  - LNST mẹ 7 năm 2018–2024 cộng dồn **−71 tỷ** [BQ]. LNST chuẩn hoá (trung vị TTM 12 quý) = **107,2 tỷ** ⇒ V_ngắn **9.965**.
- **Tiền mặt lớn nhưng phần lớn là float dự án.** Tiền + tiền gửi 3.576; vay 621 ⇒ net cash 2.956. Vốn lưu động vận hành **−1.490** ⇒ **vị thế tài chính ròng sau nợ vận hành 1.466 tỷ = 18.390 đ/cp** (HN). Theo BCTC riêng của mẹ: **1.605,8** (cao hơn 139,6 vì HN gánh 100% vay quá hạn của công ty con) — tâm theo riêng 24.604 ≈ HN ⇒ dùng HN là nhất quán, không lạc quan.
- **Kiểm toán: NGOẠI TRỪ 3 năm liền (2023, 2024, 2025) + soát xét bán niên 2026 ngoại trừ + nhấn mạnh quyết toán cổ phần hoá chưa được duyệt** [SX p5–7; HNX381]. Đây là lý do LLM bị HNX **duy trì diện cảnh báo** (QĐ 381/QĐ-SGDHN 06/04/2026). Các khoản ngoại trừ nằm ở công ty con (Lilama 5/7, Cơ khí Lắp máy) và liên kết (Lilama 69-3, BĐS Lilama, 45.3). Trigger XUỐNG (b) của vòng 1 thực ra **đã kích hoạt từ trước** — vòng 1 bỏ sót. Không đưa vào base (luật); độ nhạy: xoá 100% khoản mục con bị ngoại trừ (382,5 tỷ) ⇒ tâm 21.278; thêm liên kết về 0 ⇒ 17.573 — **nhãn ĐẮT không đổi chiều, chỉ đắt hơn**.
- **Công ty con vỡ nợ ngân hàng:** ~330 tỷ trong 870,9 tỷ vay ngắn hạn HN tại 30/06 là vay QUÁ HẠN chịu lãi phạt (Lilama 5 222,2; Cơ khí Lắp máy 80,5 hết hạn 2022; Lilama 7 27,7) [SX p54–55, Phụ lục 01]. Tài sản bảo đảm ghi là tài sản/hợp đồng của chính công ty con; **không thấy** bảo lãnh của mẹ trong các trang đã đọc (chưa loại trừ hẳn). Câu "lãi vay ~4,1%/năm" của vòng 1 bị rút lại.
- **Hai nền giá trị:** V_ngắn 9.965, V_dài 54.216, D = 1,69 > ln3. Đã lượng hoá: bỏ riêng tạm ứng mới 657,8 (người mua trả trước 461,3 → 1.119,1) và giải phóng tồn kho 440,9 ⇒ V_dài **20.189** (CFO 9T/26 theo BQ) / **23.088** (theo BCTC), **D = 0,71–0,84** (vẫn > ln2, nhưng hết "phân kỳ mạnh"). Bỏ tiếp CFO bất thường Q3/24 (+462) và Q2/25 (+376) ⇒ dòng tiền 3 năm âm. ⇒ V_dài cao gần như hoàn toàn do vốn lưu động một lần.
- **Pháp lý/quản trị — WARNING:** Bộ Xây dựng 97,88% (780,32 tỷ vốn góp, 30/06/2026 [SX p43]) ⇒ free float 2,12%; quyết toán CPH treo; ngoại trừ 3 năm; ĐHĐCĐ 2026 chọn cổ tức **cổ phiếu** 31,7% dù cầm ~3,6 nghìn tỷ tiền.
- **Thanh khoản cực thấp:** ADV trung vị 90 phiên = 15.200 cp ≈ **0,45 tỷ/phiên** [BQ]. Ở 10–20% tham gia, vị thế 1 tỷ cần 11–22 phiên để thoát.
- **§2.5 fear-buy KHÔNG áp dụng:** P/B mẹ 1,22 > 1, moat NONE, giá đang xu hướng tăng — khớp các lượt quét fear-buy 14/08 và 07/09 đã loại LLM.

## 1. Phương pháp + minh bạch đọc mù

- Bobby đọc ngành MÙ và ghi sector read trước. Phân loại 12T: ADMIN_GATED/CYCLICAL/STRUCTURAL = 0,45/0,30/0,25. Biên nhà thầu nội "mỏng cấu trúc" ở mức 0,65.
- Tôi chỉ đọc file đó sau khi đã có số BCTC. Tên thư mục lộ mã cho Bobby; Mike đã ghi nhận việc này.
- Định giá MÙ giá thị trường. Giá chỉ dùng ở §8e để gắn nhãn, và ở §8b để tính "ROE ngầm định" (thông tin, không vào tâm).
- Ngoại lệ: giá HNA (một tài sản khác) dùng để định giá khoản nắm giữ HNA.

## 2. Đối chiếu số Mike đọc nhanh (OCR) với ảnh trang BCTC

Lớp text OCR của cả BS, KQKD và LCTT **lệch xuống 1 dòng** so với nhãn. Vì vậy nhiều số Mike đọc nhanh bị gán nhầm dòng.

| Mike đọc | Ảnh trang [HN] | Ghi chú |
|---|---|---|
| "DT 9T/25 3.565,9" | DT 9T/25 = **3.712,8**; 3.565,9 là **giá vốn** [p5] | 9T/26 so cùng kỳ: −34,7% (không phải −32%) |
| "chi lãi vay đã trả 225" | Lãi vay đã trả = **39,1**; 225,3 là **thuế TNDN đã nộp** [p7] | Chi phí lãi vay 9T = 41,6 (thuyết minh: 25,0 lãi tiền vay + 5,6 dự phòng lãi cho vay) [p41] |
| "EPS 9T 1.232" | EPS Q3/26 = 1.244; EPS Q3/25 = 1.232; **EPS 9T/26 = 8.717** [p6] | Số cp 79.726.104 [p4 mã 411] |
| "Vay trả gốc 1.719 vs nhận 1.078" | 9T/26: nhận **701,5**, trả **1.078,9**. 1.594/1.719 là của 9T/25 [p7] | Vay ngắn hạn giảm 998,2 → 620,7 |
| "D/E 2,76 ⇒ vốn chủ ~2,1T" | VCSH 2.101,5 (gồm NCI −66,3) ⇒ **VCSH mẹ 2.167,7**, BVPS mẹ **27.190** | P/B mẹ **1,22** (không phải ~1,0) |
| "Q3 lợi ích không kiểm soát −1,1" | Đúng. 9T: **mẹ 694,98 / NCI 23,54** [p6] | |
| BQ NP Q2/26 490,3 | Q2 mẹ = 694,98 − 115,9 − 99,2 = **479,9** | Chênh 10,4 **không phải lỗi BQ**: BQ giữ số Q2 tự lập; LNST mẹ H1 tự lập 606,2 → sau soát xét 595,8 [SX p10] (đính chính 6) |
| BQ CFO 9T = 1.137,7 | LCTT 9T = **1.231,3** [p7] | BQ lệch 93,6 — dùng BCTC |
| — | **Cash_P0 BQ 2.708 thiếu tiền gửi có kỳ hạn 868,1** (mã 123) | Bẫy giống ca DDV |

## 3. Chất lượng lợi nhuận — trả lời câu hỏi 1

**KQKD hợp nhất [HN p5–6]:**

| tỷ đ | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| Doanh thu thuần | 340,7 | 668,2 | 2.425,7 | 3.712,8 |
| LN gộp (biên) | 174,5 (**51,2%**) | 56,6 (8,5%) | 760,2 (**31,3%**) | 146,9 (4,0%) |
| DT tài chính / CP tài chính | 18,2 / 31,2 | 55,0 / 21,7 | 105,7 / 109,2 | 138,5 / 113,4 |
| Chi phí bán hàng | 0 | 0 | **−227,1 (âm = hoàn nhập)** | 0 |
| QLDN | 33,9 | −7,6 (hoàn nhập) | 150,0 (gồm dự phòng 76,6) | 14,6 |
| LD-LK | 0 | 5,8 | 7,9 | 6,6 |
| LN khác | −0,1 | −0,7 | 62,7 | 15,2 |
| **LNTT** | **127,6** | 102,5 | **904,5** | 179,2 |
| LNST mẹ | 99,2 | 98,2 | 695,0 | 177,2 |

**Các khoản một lần đã gọi tên** (thuyết minh):
- **TM31:** dự phòng bảo hành mới 148,9; **hoàn nhập dự phòng bảo hành công trình 376,0** ⇒ chi phí bán hàng ròng −227,1.
  - Từ 2026, theo TT 99/2025, khoản hoàn nhập này ghi giảm chi phí bán hàng (trước đây ghi thu nhập khác) và áp dụng phi hồi tố.
  - TM23 [p36] cho thấy dự phòng bảo hành ngắn hạn giảm 386,3 → 9,4, tức đã hết hạn bảo hành. Dự phòng dài hạn tăng thêm 146,1 lên **737,7**.
- **TM33:** thu nhập thanh lý TSCĐ 61,1 (giá trị còn lại 0,1); hoàn nhập bảo hành 2,3.
- **Tỷ giá:** lãi phát sinh 71,3; lỗ phát sinh 11,4; **lỗ đánh giá lại 67,0** ⇒ ròng ≈ −7,1. Có thêm −65,1 ảnh hưởng tỷ giá lên tiền [p8]. Số dư ngoại tệ 63,8 triệu USD [p40].
- **Không có** cổ tức nội bộ hay lãi chuyển nhượng vốn trong 9T/26 (TM29: cổ tức = 0; lãi thanh lý đầu tư = 0) [p40].
- Danh mục đầu tư vào công ty liên kết và đơn vị khác không đổi từ 01/01 đến 30/09 [p23–24]. ⇒ Giả thuyết "lãi chuyển nhượng vốn / cổ tức từ con" **SAI**.
- Đóng góp LD-LK chỉ 7,9 tỷ. Câu giải trình Q2 "lãi LD-LK tăng" [GT-Q2] **không đáng kể về số**.

**LNTT cốt lõi 9T** = 904,5 − 290,5 = **614,0** ⇒ LNST ~491 (thuế 20%). Năm hoá 655, tức ROE 30% trên VCSH mẹ.
- Con số này VẪN chưa phải "bền", vì gồm biên gộp 31–51%. Đây là biên của giai đoạn **quyết toán** các công trình Sông Hậu 1 và Nhơn Trạch 3&4 (ĐHĐCĐ 2026 nêu đang quyết toán [Web baokiemtoan]).
- BCTC quý không tách doanh thu/giá vốn theo dự án (TM2.34: không lập báo cáo bộ phận) ⇒ **chưa tách được phần quyết toán**. Đây là giới hạn dữ liệu, ghi rõ.
- **Q2/2026: LNST hợp nhất 489,4** [GT-Q2]; **LNST riêng của mẹ Q2 483,96** (Q2/25: 35,39) [GTR-Q2]; LNST riêng 6T sau soát xét **566,49** (6T/25: 85,04) [GTR-6T]. Công ty giải thích: DT Q2 +62%, LN gộp tăng mạnh, một số dự án hoàn thành quyết toán và nghĩa vụ bảo hành ⇒ hoàn nhập dự phòng; 6T: LN gộp 85,06 → 576,89 "chủ yếu do quyết toán … cho biên cao". Q3 không có hoàn nhập bảo hành (CP bán hàng Q3 = 0) ⇒ hoàn nhập 376,0 nằm ở H1, theo giải trình là Q2 (đính chính 12: đã đọc đủ file scan).
- **2025:** LNST 473–492 tỷ, gồm hoàn nhập bảo hành >174 tỷ và thu nhập bồi thường/khắc phục sự cố nhà thầu phụ [Web nguoiquansat 07/11/2026]. ⇒ Q4/25 (314,8) cũng mang tính một lần.

**Chuỗi LNST mẹ năm [BQ]:** 2018 −163,1 · 2019 −78,0 · 2020 55,5 · 2021 15,4 · 2022 10,2 · 2023 1,1 · 2024 87,8 · 2025 492,0 · 9T/26 695,0.
- Dự phòng lớn trích trong 2025 (LCTT 9T/25: +448,4) và hoàn nhập trong 2026 (LCTT 9T/26: −150,9) [p7]. Đây là **dòng đảo của cùng một chu kỳ dự án**.
- **TTM 12 quý (Q4/23→Q3/26):** 1,1 / 37,3 / 98,6 / 105,8 / 87,8 / 103,7 / 108,7 / 192,0 / 492,0 / 556,0 / 1.008,8 / 1.009,8 ⇒ trung vị **107,2** (ROE 4,9% trên VCSH mẹ hiện tại).

**Phản ứng giá [BQ]:**
- Trước công bố Q2 (giải trình ký 30/07): giá 19.000–19.400.
- Sau công bố: 22.000 (31/07) → **40.400 (10/08)**, +108% trong 8 phiên, khối lượng 47–127 nghìn cp/phiên.
- Sau đó trôi về 25.600 (19/10).
- Công bố Q3 (29/10): **−12% (26.400) ngày 30/10**, khối lượng 199 nghìn cp, kỷ lục của chuỗi.
- 12–13/11: +13% và +10% (31.000 → 34.200) trên 104–140 nghìn cp. **Chưa tìm được tin kích hoạt** (có thể liên quan cổ tức cổ phiếu 31,7%, cần kiểm).

## 4. Doanh thu, backlog, ghi nhận — trả lời câu hỏi 2

- **Ghi nhận doanh thu:** DT xây lắp 9T 2.392,4 (98,6% tổng); dịch vụ 33,3 [p40].
  - Phải thu theo tiến độ, chi phí dở dang theo dự án và tuổi WIP: **không có trong BCTC quý** (cần BCTC kiểm toán 2025).
  - Hàng tồn kho HN giảm 763,1 → 307,4 [p3]. **Đính chính 4:** 242,7/307,4 (79%) nằm ở **công ty con** (tồn kho riêng của mẹ chỉ 64,7 [RG]), trùng khoản chi phí SXKD dở dang 250,2 tỷ tại Lilama 5/7/Cơ khí mà AASC **ngoại trừ** vì không xác định được tính chính xác và tổn thất [SX p6]. Không thể đọc phần này là "dự án đã bàn giao".
- **Backlog đọc được từ bảng cân đối:**
  - Tạm ứng Ban QLDA Điện 2 (EVN) cho **Quảng Trạch II: 586,4 tỷ** [p34 TM18]. Đây là hợp đồng EPC 25.202 tỷ, liên danh PowerChina–Lilama, ký 09/02/2026, khởi công 20/10/2026 [Web, Bobby].
  - **Phần giá trị riêng của LLM: KHÔNG tìm thấy.** Ước lượng thô từ tạm ứng (giả định tạm ứng ~10–15% phần LLM): **~3.900–5.900 tỷ (ước lượng)** — không dùng trong định giá.
  - **Ô Môn I chuyển đổi khí:** EVNGENCO2 tạm ứng 338,5 [p34]. Gói EPC-01 ~1.949 tỷ, liên danh **Lilama đứng đầu** + EVNGENCO3, ký 09/2025 [Web kinhtechungkhoan 25/08/2025].
  - Ban QLDA hạ tầng Hà Nội tạm ứng 100,0 (mới); Long Phú 1 (PTSC) 40,9.
  - **Phải thu TKV (Ban QLDA chuyên ngành Điện): 1.080,0** (đầu năm 66,7) [p25]. Đây là hoạt động lớn mới trong năm; tên dự án chưa xác định, có thể là Na Dương II (cần kiểm).
  - Neom Hydrogen và module H2GS (xuất khẩu chế tạo) có chi phí phải trả 76,2 / 18,0 [p36].
- **Kế hoạch 2026 (công ty mẹ):** DT 3.377,8, LNTT 450 [Web baokiemtoan]. 9T đã vượt xa LNTT kế hoạch nhờ các khoản một lần.
- **Tỷ trọng Q4:** 2023 Q4 chiếm 48% DT năm; 2025 là 32% [BQ] ⇒ Q4 thường lớn (quyết toán cuối năm).
- **Phân mảng** EPC / chế tạo / BĐS / điện: BCTC không lập bộ phận. Thực tế gần như 100% là xây lắp. BĐS và điện nằm ở công ty liên kết (BĐS Lilama 27,93%) và đầu tư khác (HNA).

## 5. Bảng cân đối, net cash thật, CFO — trả lời câu hỏi 3

**Vị thế tài chính:**
- Tiền 2.707,9 [p21 TM3]: tiền mặt 3,8; không kỳ hạn **1.752,8**; tương đương tiền 951,2.
- Tiền gửi có kỳ hạn 868,1 [p22 TM4]: BIDV 447,1, TPBank 393,9, Agribank 20,4.
- Trái phiếu BID2 dài hạn 140 *triệu* đ; tiền gửi dài hạn 0,3.
- Vay ngắn hạn 620,7; vay dài hạn 0 ⇒ **net cash 2.955,7**.
- **Không thấy** thuyết minh tiền gửi bị hạn chế hay ký quỹ trong TM3/TM4 [SX p25–26]. Hạn mức tín dụng của MẸ tại 30/06 (gồm vay vốn lưu động, **bảo lãnh, mở L/C**): BIDV 3.000 + 1.800 + 2.600, TPBank 1.300 + 600, VietinBank 70, VIB 500 = **9.870 tỷ**; số bảo lãnh đang phát hành: không công bố [SX p54, Phụ lục 01].

**Nợ vận hành (phải trả bằng tiền khi dự án tiến triển) [p4, p34, p36, p37]:**
- Phải trả người bán 1.183,5.
- Khách ứng trước 1.119,1.
- Chi phí phải trả **1.600,2**: Vũng Áng 1 752,1 (không đổi cả năm); Nhơn Trạch 3&4 323,7; Neom 76,2; lãi vay 88,0; khác 301,7.
- Dự phòng bảo hành 747,1; phải trả khác 297,0; lương 95,1; quỹ khen thưởng 83,1; thuế 30,6; doanh thu chưa thực hiện 13,5.
- **Tổng 5.169,2.**

**Tài sản vận hành:**
- Phải thu khách hàng 3.101,8; trả trước 521,2; phải thu khác 449,5; dự phòng −871,2; tồn kho 307,4; phải thu dài hạn 171,0.
- **Tổng 3.679,7** ⇒ **NWC −1.489,6**.
- ⇒ **Vị thế tài chính ròng sau nợ vận hành = 1.466,2 tỷ = 18.390 đ/cp.** Đây là "net cash thật" nếu toàn bộ phải thu còn lại thu được.
- **Đối chiếu BCTC RIÊNG của mẹ [RG] (đính chính 10):** tiền 2.656,8 + tiền gửi 861,3 − vay 289,7 = net cash 3.228,4; NWC vận hành −1.622,7 ⇒ **vị thế ròng mẹ 1.605,8** (HN 1.466,2). HN thấp hơn 139,6 chủ yếu vì gánh 100% vay quá hạn của công ty con (51%). Đầu tư TC dài hạn riêng 446,8 (HN 553,7). Tâm theo riêng 24.604 ≈ HN 24.599 ⇒ dùng HN không lạc quan hơn.
- Các khoản phải thu lớn nhất chưa dự phòng: PV Power Vũng Áng–Quảng Trạch 876,7 (đối ứng chi phí phải trả Vũng Áng 1 752,1); TKV 1.080,0; PV Power QLDA 312,0 [p25].

**Đã dự phòng (sàn bảo thủ đã đi trước):**
- Cho vay 394,7, dự phòng 100%: Lisemco 223,2; Lilama 45.1 92,1; Lilama Hà Nội 41,2; 45.3 24,2; Phú Mỹ Trung Việt 14,0 [p28].
- Lãi cho vay phải thu 292,4, dự phòng 100% [p26].
- Nợ xấu phải thu khách hàng 582,5 gốc, giá trị thu hồi 150,0 [p28].

**CFO 9T/26 +1.231,3 (9T/25 −271,5) [p7]:**
- Lợi nhuận trước thay đổi vốn lưu động 761,3.
- Giảm hàng tồn kho +440,9; tăng phải trả +515,1 (chủ yếu tạm ứng QT II + Ô Môn); tăng phải thu −216,1 (TKV); thuế đã nộp −225,3; lãi vay −39,1.
- ⇒ **Phần lớn CFO là một lần**: tạm ứng mới 658 và giải phóng tồn kho.

**Khác:**
- Capex 9T 24,6 (nhẹ tài sản); thanh lý TSCĐ thu 67,2.
- Gửi tiền có kỳ hạn mới 861,5; lãi đã nhận 39,3.
- Cổ tức tiền 9T chỉ 5,2 [p7].
- Thuế TNDN 9T: phải nộp 183,3 / đã nộp 225,3 [p35] ⇒ lợi nhuận chịu thuế thật, không phải lãi "trên giấy" thuần.
- **Chi phí lãi vay (đính chính 3 — rút lại con số ~4,1%/năm của vòng 1, nó là ẢO):** vay ngắn hạn HN 30/06 = 870,9 [SX p37 TM16]: mẹ 539,2, công ty con 331,7. Trong phần con, **~330 tỷ là vay QUÁ HẠN chịu lãi phạt**: Lilama 5 222,2 (BIDV 183,0 + VietinBank 5,6 + 8,3 + 25,4; hợp đồng ký 2017–2018, đều ghi "đã quá hạn thanh toán"); Cơ khí Lắp máy BIDV 80,5 (hết hạn 21/01/2022); Lilama 7 Agribank 27,7 (hết hạn 24/02/2024) [SX p55, Phụ lục 01]. AASC **không xác định được tính đầy đủ chi phí lãi** của Lilama 5 (lãi quá hạn đã ghi 74,0) và phát hiện Cơ khí vốn hoá 36,6 tỷ lãi vay vào phải thu khác [SX p6]. ⇒ chi phí lãi thật **chưa đo được**, không dùng tỷ lệ suy ra. Vay riêng của mẹ tại 30/09: 289,7 [RG].
- **Bảo lãnh của mẹ cho khoản vay con:** tài sản bảo đảm ghi trong Phụ lục 01 là tài sản/hợp đồng của chính công ty con (QSDĐ, tài sản hình thành từ hợp đồng); **không thấy** bảo lãnh của Tổng công ty trong các trang đã đọc ⇒ chưa loại trừ (cần thuyết minh cam kết trong BCTC kiểm toán năm).
- **Rủi ro ngoài bảng [p37 TM24]:** đã thu 160,4 tỷ tiền bảo lãnh thực hiện hợp đồng của Hamon (Sông Hậu 1) nhưng **chưa ghi nhận vào lãi lỗ**, vì Hamon đang phá sản và nghĩa vụ chưa xác định. Có thể thành thu nhập (upside) hoặc phải hoàn trả. Không đưa vào base.

## 6. Cấu trúc tập đoàn, SOTP, Lilama 69-1 — trả lời câu hỏi 4

- **Công ty con hợp nhất** chỉ có 5 đơn vị nhỏ [p10]: Lilama SEA (Brunei) 99%; Lilama 5 51%; Lilama 7 51%; Cơ khí Lắp máy 51%; Tư vấn LHT 60% (đang giải thể).
- **L10, L18 (LM8), 69-1, 69-3, 45.x là CÔNG TY LIÊN KẾT** (vốn chủ sở hữu, 35–41%) [p23]. ⇒ LLM hợp nhất gần như = công ty mẹ, và "cổ tức từ con" bị loại khi hợp nhất không phải là nguồn lãi.
- **NCI −66,3** (công ty con âm vốn).
- **Đầu tư liên kết theo sổ: 328,2**; đầu tư khác 255,2 (dự phòng −30,2) [p3, p24]. ⚠️ **Đính chính 5:** AASC **ngoại trừ** giá trị khoản đầu tư vào liên kết (Lilama 69-3, BĐS Lilama — vì BCTC 2025 của chúng bị kiểm toán ngoại trừ) [SX p7]. Base vẫn giữ sổ (NPV=0, không bake), độ nhạy ở §8b: liên kết về 50% ⇒ tâm 22.746; về 0 cùng xoá khoản mục con bị ngoại trừ ⇒ 17.573.
  - Theo [HN p23], Lilama 10 = L10 và Lilama 18 = **LM8**. Mã BQ `L18` là doanh nghiệp KHÁC, không thuộc họ Lilama. Giá trị thị trường [BQ 18/11, vốn hoá × tỷ lệ]: L10 389 × 36% = 140; LM8 155 × 36% = 56 ⇒ 196 cho 2 mã. L43/L44/L45/L63/LCD chưa định giá thị trường.
  - Không có bằng chứng giá trị thị trường các liên kết vượt rõ sổ 328,2 ⇒ **giữ sổ sách** (NPV=0), không cộng premium.
- **HNA (Thủy điện Hủa Na):** giá gốc 85,7. Nếu còn giữ ~8,72 triệu cp (3,71%, từng đấu giá 07/2025, kết quả không tìm thấy; giá gốc không đổi cả năm), giá trị thị trường 20.900 × 8,72 = 182,2.
  - ⇒ Lãi ẩn sau thuế **77,2 tỷ = 968 đ/cp**. Đưa vào base; **cần kiểm số cp còn giữ**.
- **Lilama 69-1:** NQ 327/NQ-HĐQT ngày 12/10/2026 thoái toàn bộ 3.113.862 cp (41,1%), đấu giá lô trên HNX, giá khởi điểm 13.200 đ, ~41,1 tỷ, dự kiến Q4/2026 [Web baodauthau 20/10/2026].
  - L61 âm vốn chủ −102,6 tỷ (2025). Giá BQ 16/10 chỉ 1.200 đ ⇒ **khả năng bán được ở giá khởi điểm thấp**.
  - Giá trị sổ khoản này trong LLM ~0 (khoản đầu tư liên kết trên 255/328 không còn giá trị). Kết quả bất kỳ chỉ là upside nhỏ (≤41 tỷ ≈ 515 đ/cp).
  - Danh mục thoái 2026–30: 17 khoản; giữ L10, L18, L69-3 [Web kinhtechungkhoan 14/10/2026].

## 7. Vị thế & lợi thế cạnh tranh (5F tầng b) — trả lời câu hỏi 7

Lần 5F đầu tiên (không có trong `data/moat_tags.csv`, đã grep). Loại hình: tổng thầu lắp máy / EPC công nghiệp-năng lượng nhà nước, nhẹ tài sản (TSCĐ ròng 124,5 tỷ).

| Lực | Bằng chứng | Đánh giá |
|---|---|---|
| Khách hàng | Tập trung EVN / PV Power / TKV / PVN. Phải thu 3 chủ đầu tư lớn = 2.269/3.102 [p25]. Có lịch sử nợ đọng (Vũng Áng 1 876,7 nhiều năm; Thái Bình 2 dự phòng 100%) | Sức mạnh khách hàng **rất cao** |
| Đối thủ | Ở gói lớn, LLM là **thành viên liên danh với tổng thầu TQ** (QT II với PowerChina); đối thủ GE, Doosan, Gezhouba [Bobby] | Cạnh tranh giá gay gắt |
| Thay thế / gia nhập | Năng lực lắp máy nội có, nhưng gói EPC lớn cần tài chính và bảo lãnh của tổng thầu nước ngoài | Trung bình |
| Nhà cung cấp | Thiết bị chính do OEM nước ngoài (Doosan, Hamon, Flsmidth: phải trả 85–161 tỷ mỗi bên) [p34] | Bị ép biên |
| Lực thứ 6 | PDP8 / đầu tư công (cầu thuận), nhưng ADMIN_GATED 0,45 [Bobby]; định mức NĐ 206/2026 chưa rõ chiều | Cầu tốt, biên không tự cải thiện |

**Bằng chứng định lượng nhiều chu kỳ:**
- ROE_Min5Y **−0,7%**, ROIC_Min5Y **0,0** [BQ].
- LNST mẹ 2018–24 cộng dồn −71 tỷ.
- GPM TTM 2017–24 chủ yếu 2–6% [BQ], so với peer lắp máy: ROE_Min5Y L10 5,9%, LM8 (Lilama 18) 3,9%, peer xây dựng L18 5,7% [BQ].
- ROIC − Ke < 0 suốt chu kỳ.
- ⇒ **moat_tier = NONE**. moat_type: "thương hiệu/kinh nghiệm tổng thầu lắp máy nhà nước", chưa thành lợi nhuận siêu ngạch.
- Rủi ro số 1: biên quyết toán 2025–26 bị coi là bền; nợ đọng chủ đầu tư nhà nước tái diễn.
- **Không thưởng moat** (không tham số moat nào trong mô hình). **Cũng không trừ:** base ROE/NOPAT không ép về Ke.
- Độ nhạy "moat sai" không áp dụng (tier NONE). Nếu ai cho rằng 2026 là "biên mới bền" (ROE ~18% ngầm định trong giá), thì đó là giả định WIDE-like **chưa có bằng chứng nhiều chu kỳ**.

**Đề xuất dòng `data/moat_tags.csv`** (không tự sửa file):
`LLM,NONE,EPC_TRACK_RECORD_SOE,M,"Bien quyet toan 2025-26 (GPM 31-51%) bi coi la ben; 2018-24 LNST cong don -71 ty, ROE_Min5Y -0,7%; khach EVN/PVN/TKV no dong (Vung Ang 1 877 ty, Thai Binh 2 du phong 100%); thanh vien lien danh voi tong thau TQ o goi lon",2026-11-18,dd_LLM_20261118,N`

## 8. Định giá — MÙ giá thị trường (giá chỉ so ở bước cuối) — trả lời câu hỏi 6

### 8a. Khung (VÒNG 2)

- **r = 13,5%.** Lãi huy động 12T hiệu dụng 7,4% (CCTG 12M 02/11) = điểm neo 03/11 ⇒ r không đổi [Bobby nguồn; macro snapshot].
- **g = 0.** ROE cơ sở < r ⇒ tái đầu tư vào mảng cũ phá giá trị. Hợp đồng/dự án mới được tính NPV=0.
- **Phương pháp (một phương pháp cho cả ba kịch bản — đính chính 8):** SOTP = NOPAT hoạt động / r + vị thế tài chính ròng sau nợ vận hành × f + đầu tư tài chính dài hạn theo sổ (553,7) + lãi ẩn HNA (77,2) − tổn thất phải thu cũ (chỉ kịch bản xấu).
  - f = hệ số "tiền dùng được". Cơ sở/tốt: f = 1 (theo sổ, luật NPV=0; kế hoạch "đầu tư phát triển ~850 tỷ" 2026 [Web baokiemtoan]).
  - Kịch bản xấu: tiền mắc kẹt vĩnh viễn, chỉ có giá trị bằng lãi tiền gửi thực nhận: lãi tiền gửi 9T/26 34,4 tỷ trên ~3,6 nghìn tỷ ≈ 1,3%/năm × (1 − 20%) / 13,5% ⇒ **f = 0,077**. Thay cho cách dùng thu nhập thặng dư của vòng 1.
- **Biên gộp cơ sở (đính chính 7):** vòng 1 dùng 7% "trên trung bình lịch sử" — **không có cơ sở độc lập** (biên QT II/Ô Môn I không công bố; biên 2026 là biên quyết toán, công ty tự xác nhận). ⇒ **hạ về trung vị lịch sử 4,5%** (GPM TTM 2017Q3–2024Q4 trung vị 4,55%; năm 2017–24 trung vị 4,35% [BQ]). Kịch bản tốt = **7,0%** = GPM năm 2025, mức cao nhất 9 năm (đã gồm một phần quyết toán).

| Kịch bản | Giả định | Cơ sở | Giá trị/cp trước TK | sau TK 10% |
|---|---|---|---|---|
| Xấu (25%) | NOPAT −30; tổn thất phải thu cũ 200 **(ước lượng)**; f = 0,077 | 2018–19 LNST −163/−78; tiền 2–3 nghìn tỷ nằm yên 2017–24 với ROE ~0; PV Power Vũng Áng–Quảng Trạch 876,7 + QLDA PV Power 312,0 chưa dự phòng | **4.033** | 3.630 |
| Cơ sở (50%) | NOPAT 46 = 0,8 × (DT 4.500 × **4,5%** − QLDN 100 − bảo hành 45) **(ước lượng)**; f = 1 | DT TB 2023–25 = 5.538, KH 2026 3.378 + QT II/Ô Môn I; biên = trung vị lịch sử | **30.577** | 27.519 |
| Tốt (25%) | NOPAT 192 = 0,8 × (6.000 × **7%** − 120 − 60) **(ước lượng)**; f = 1 | DT 2024 = 6.102; biên = năm 2025 | **44.142** | 39.728 |
| **Có trọng số** | | | **27.332** | **24.599** |

- **Trọng số 25/50/25 = mặc định đối xứng, KHÔNG có cơ sở định lượng độc lập** — ghi rõ. Bằng chứng nghiêng về xấu chưa đưa vào trọng số: ĐHĐCĐ 2026 chọn cổ tức **cổ phiếu** 31,7% dù cầm ~3,6 nghìn tỷ; trích quỹ đầu tư phát triển +242 tỷ (125,0 → 367,3 [SX p43]); quyết toán CPH treo; ngoại trừ 3 năm liền. Độ nhạy trọng số ở §8b.
- **Tách phần biên độ do phương pháp:** vòng 1 vùng [4.497; 51.769] trộn thu nhập thặng dư (xấu) với SOTP (cơ sở/tốt). Nay một phương pháp: [3.630; 39.728]. Biên độ vẫn rộng vì **trục tiền mắc kẹt** (f 0,077 ↔ 1 ≈ 17.000 đ/cp sau TK) và **trục biên gộp** (4,5% ↔ 7% ≈ 6.000 đ/cp), không còn do trộn phương pháp. Đối chiếu: thu nhập thặng dư cho cả ba kịch bản (tiền mắc kẹt ở mọi kịch bản) = 13.560.
- **Không đưa vào base:** Hamon 160,4 (hai chiều); dự phòng bảo hành dài hạn 737,7 có thể hoàn nhập (upside một lần); quyết toán Vũng Áng 1 (phải thu 876,7 vs chi phí phải trả 752,1); thoái L61 (≤41); các khoản ngoại trừ kiểm toán (độ nhạy dưới).

### 8b. Độ nhạy (`calc_output.txt`, khối REV2; đều sau TK thanh khoản 10%)

- **Biên gộp cơ sở (tham số mạnh nhất; tốt giữ 7%):** 4,0% ⇒ 23.846 (1,40×) · **4,5% ⇒ 24.599 (1,35×)** · 5,0% ⇒ 25.351 (1,31×) · 6,0% ⇒ 26.857 (1,24×) · 7,0% ⇒ 28.362 (1,17×). Nếu tốt = cơ sở + 3pp: 7%/10% (= giả định vòng 1) ⇒ 31.372 (1,06×). **Biên gộp cơ sở để tâm = giá: 10,3%.**
- **Trọng số:** 40/45/15 ⇒ 19.795 (1,68×); 50/40/10 ⇒ 16.795 (1,98×); 10/50/40 ⇒ 30.013 (1,11×); chỉ cơ sở ⇒ 27.519 (1,21×). **Không tổ hợp nào trong lưới cho giá/tâm < 1.**
- **Lãi huy động (β=1):** −100 / −50 / +50 / +100bp ⇒ 25.024 / 24.803 / 24.409 / 24.233 (+1,7% / +0,8% / −0,8% / −1,5%). β=0,5: một nửa.
- **Chiết khấu thanh khoản 0 / 5 / 10 / 20%:** 27.332 / 25.965 / **24.599** / 21.866.
- **Tiền mắc kẹt một phần ở cơ sở/tốt** (f = 0,75 / 0,5): 21.496 / 18.392.
- **Ngoại trừ kiểm toán (WARNING, không vào base):** xoá 100% khoản mục con bị ngoại trừ (phải thu quá hạn 87,6 + WIP 250,2 + lãi vay vốn hoá 36,6 + lãi chậm nộp BHXH 8,0 = 382,5) ⇒ 21.278; thêm liên kết 328,2 về 0 ⇒ 17.573; chỉ liên kết về 50% ⇒ 22.746. (Lưu ý: xoá 100% là cận xấu — HN gánh 100% khoản của công ty con 51%, NCI đã âm.)
- **BCTC riêng (đính chính 10):** vị thế TC ròng mẹ 1.605,8 (net cash 3.228,4; NWC −1.622,7), đầu tư TC dài hạn theo sổ 446,8 ⇒ tâm 24.604 (HN 24.599).
- HNA = 0 ⇒ 23.727.
- **ROE ngầm định ở giá 33.300** (thu nhập thặng dư, sau thanh khoản): **17,9%** vĩnh viễn trên VCSH mẹ — chưa năm nào đạt trong 10 năm nếu không có khoản một lần.
- **Cổ tức cổ phiếu 31,7%** (đã thông qua, chưa thực hiện): không đổi tổng giá trị. Quy đổi sau chia: tâm ~18.678; giá ~25.285.

### 8c. Hai nền giá trị (chỉ hiển thị, không đổi tâm)

| Nền | Giá trị | Ghi chú |
|---|---|---|
| V_ngắn (LNST chuẩn hoá = trung vị TTM 12 quý = 107,2; ROE 4,9%; g = 0) | **9.965** | Trung vị neo vào 2023–25 khi quyết toán chưa xảy ra |
| V_dài (FCFE = CFO 3 năm TB 595,6 − capex 12,1) | **54.216** | capex/CFO 0,02 |
| V theo C4 = CFO − min(capex, KH 15,7) | 54.216 | Chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi |
| V theo D2 = CFO − 1,75% × DT TTM 4.145,5 | 48.600 | Chưa qua tiêu chí khoá trước (0/9 nền qua; D2 đạt T1–T4, trượt BH-FDR ở 3/6 tháng, chỉ sống ở 12 tháng), chỉ theo dõi |

**D = |ln(9.965 / 54.216)| = 1,69 > ln3 ⇒ PHÂN KỲ MẠNH. Lượng hoá nguồn chênh (đính chính 9):**

| CFO 12 quý dùng cho V_dài | CFO/năm | V_dài | D |
|---|---|---|---|
| Gốc (BQ, 1.786,9) | 595,6 | 54.216 | 1,69 |
| Bỏ tạm ứng mới 657,8 (người mua trả trước 461,3 → 1.119,1 [HN p34]) + giải phóng tồn kho 440,9 [HN p7] | 229,4 | **20.189** | **0,71** |
| Như trên nhưng CFO 9T/26 theo BCTC 1.231,3 (BQ 1.137,7) | 260,6 | **23.088** | **0,84** |
| Bỏ thêm CFO Q3/24 (+462,3) và Q2/25 (+375,9) — chưa giải thích được | −50,0 | âm | n/a |

- Riêng hai khoản vốn lưu động 9T/26 giải thích phần lớn D (1,69 → 0,71–0,84). D vẫn > ln2 nên vẫn ghi cờ, nhưng **hết "phân kỳ mạnh"** sau khi khử một lần.
- Hai quý CFO dương lớn Q3/24 và Q2/25: BQ không tách nguồn; chưa đọc LCTT từng quý ⇒ **chưa giải thích**. Bỏ chúng thì dòng tiền 3 năm âm.
- ⇒ V_dài **không** phải bằng chứng rẻ. Vùng đọc mở rộng [9.965; 23.088] (sau khử) ⊂ vùng mô hình.

### 8d. Bội số & comp ([BQ] `ticker` 18/11/2026, trailing)

| Mã | PE | PB | EV/EBITDA | ROE_Min5Y |
|---|---|---|---|---|
| **LLM** | 2,63 (gồm một lần) | 1,26 (tổng VCSH) / **1,22 mẹ** | 0,53 (net cash) | −0,7% |
| L10 | 2,37 | 0,91 | — | 5,9% |
| L18 (không thuộc họ Lilama) | 3,57 | 0,65 | 7,32 | 5,7% |
| LM8 | 13,63 | 0,52 | 8,43 | 3,9% |
| L14 | 140 | 1,17 | 23,4 | 3,6% |
| PC1 | 7,04 | 0,82 | 5,47 | 1,7% |
| CTD | 9,87 | 0,79 | 14,0 | 0,3% |
| VCG | 9,27 | 0,81 | 10,3 | 5,5% |
| LCG | 8,69 | 0,48 | 5,74 | 4,5% |
| HUT | 47,6 | 0,73 | 14,5 | 0,7% |
| TV2 | 8,89 | 1,41 | 6,42 | 3,9% |
| **Trung vị 10 peer** | **~9,1** | **0,80** | **~8,4** | |

- Bất đồng: theo PE trailing, LLM **rẻ nhất nhóm**, nhưng PE gồm một lần và biên quyết toán.
- Theo PB, LLM **cao hơn trung vị 52%** (1,22 vs 0,80) dù ROE_Min5Y thấp nhất nhóm. L10 và LM8 (họ Lilama) có PB 0,91 và 0,52 (L10 PE 2,37) ⇒ **thị trường định giá các mã họ Lilama theo PB < 1 dù PE thấp**.
- LLM ở PB 1,22 là ngoại lệ, có thể do kỳ vọng tiền mặt/QT II. Lưu ý PB của LLM cao một phần vì 46% tổng tài sản là tiền.
- Comp chỉ để đọc, không vào tâm.

### 8e. Vùng giá (sau chiết khấu thanh khoản 10%)

- Tâm **24.599** (v1: 31.589); vùng **[3.630; 39.728]** (v1: [4.497; 51.769]); 0,85×tâm = **20.909** (v1: 26.850).
- Giá 33.300 = **1,35× tâm ⇒ ĐẮT** (v1: 1,05× "quanh hợp lý" — **nhãn đổi**). Giá nằm trong vùng nhưng ở phần trên, giữa tâm và kịch bản tốt.
- Đắt ở mọi biến thể trong lưới độ nhạy (biên gộp 4–7%, trọng số, lãi huy động, thanh khoản 0–20%, mẹ hay HN). Chỉ hết đắt khi biên gộp cơ sở bền ≥ 10,3%, hoặc thanh khoản 0% + biên ≥ ~8% **(ước lượng nội suy)**.
- Áp dụng cho vị thế ≤ 0,5–1 tỷ (thoát 11–22 phiên ở 10–20% tham gia).
- Chiết khấu thanh khoản 10% là **(ước lượng)**, chỉ là độ nhạy 0–20%:
  - ADV trung vị 0,45 tỷ/phiên; trung bình 0,76 tỷ; 0 phiên trắng trong 61 phiên [BQ].
  - Free float ~2%.
  - Vị thế tham chiếu 0,5–1% NAV của quỹ 50 tỷ = 250–500 triệu ⇒ thoát 3–11 phiên ở 10–20% tham gia. Vị thế 2 tỷ ⇒ 22–44 phiên.
  - Không có số liệu thực thi/Amihud độc lập ⇒ mức 10% không được coi là đo lường.

## 9. Trả lời 15 điểm "DD cần kiểm gì" của Bobby

| # | Trả lời bằng số / trạng thái |
|---|---|
| 1 Backlog phần của DN, vai trò | QT II: thành viên liên danh với PowerChina (đứng đầu), phần LLM **không tìm thấy**, tạm ứng 586,4 [p34]. Ô Môn I: LLM đứng đầu, gói ~1.949, tạm ứng 338,5. Long Phú 1: tạm ứng PTSC 40,9. Dung Quất: liên danh Chengda–BPE trúng, LLM **không** thấy trong kết quả [Bobby]. |
| 2 Ký mới 2025–26, tỷ lệ thắng | Chưa có số tổng. Ký mới thấy được: QT II (02/2026), Ô Môn I (09/2025), Hà Nội hạ tầng (tạm ứng 100). Tỷ trọng DT theo chủ đầu tư: chưa công bố |
| 3 Trượt giá / tiền tệ | Có hợp đồng USD: số dư ngoại tệ 63,8 triệu USD [p40]; lỗ đánh giá lại 67,0 / 9T [p41] ⇒ LLM chịu rủi ro tỷ giá. Điều khoản trượt giá: chưa đọc được |
| 4 Ghi nhận, WIP, dự án COD chưa quyết toán | Tồn kho/WIP HN 307,4 (đầu năm 763,1); 242,7 ở công ty con, trùng WIP 250,2 bị ngoại trừ; của mẹ chỉ 64,7. Chưa quyết toán: Vũng Áng 1 (chi phí phải trả 752,1, phải thu 876,7 — COD nhiều năm trước, năm cụ thể chưa kiểm), Sông Hậu 1, NT3&4 (chi phí phải trả 323,7). **Đúng tiền lệ "COD nhiều năm chưa quyết toán"** |
| 5 Dự phòng lỗ HĐ, lãi bị đảo | 2025 trích +448,4 dự phòng (LCTT 9T/25) → 2026 hoàn nhập −150,9; bảo hành hoàn nhập 376,0. Q4 chiếm 32–48% DT năm. Lệch LN–CFO: 2018–24 CFO âm nhiều quý trong khi LN ~0 |
| 6 Ý kiến kiểm toán | **NGOẠI TRỪ** 2023, 2024, 2025 (AASC) ⇒ HNX duy trì diện cảnh báo (QĐ 381, 06/04/2026). Soát xét H1/2026: **kết luận ngoại trừ** (phải thu quá hạn 87,6; WIP 250,2; lãi vay quá hạn Lilama 5; lãi vốn hoá 36,6; BHXH 8,03; liên kết 69-3/BĐS Lilama) + **nhấn mạnh quyết toán CPH chưa duyệt** [SX p5–7]. Chi tiết §11 |
| 7 Phải thu, tuổi nợ, dự phòng | Phải thu KH 3.101,8, dự phòng 422,8; nợ xấu gốc 582,5 thu hồi 150,0 [p28]; người mua trả trước 1.119,1. Tiền giữ lại bảo hành: không tách |
| 8 Hạn mức bảo lãnh | Hạn mức tín dụng của mẹ (gồm bảo lãnh, L/C) 9.870 tỷ tại 8 hợp đồng [SX p54]; số bảo lãnh đang phát hành: không công bố. Không thấy ký quỹ/tiền bị hạn chế [SX p25–26]. Bảo lãnh của mẹ cho vay công ty con: không thấy, chưa loại trừ |
| 9 Vay, lãi suất | Vay ngắn hạn HN 620,7 (30/09); tại 30/06: 870,9 = mẹ 539,2 + con 331,7, trong đó **~330 vay quá hạn chịu lãi phạt** ở Lilama 5/7/Cơ khí [SX p37, p55]. Chi phí lãi thật chưa đo được (AASC ngoại trừ) — rút lại "~4,1%/năm". Mẹ: net cash dư thừa |
| 10 Sở hữu NN, mẹ–con | Bộ Xây dựng **97,88%** (780,32 tỷ vốn góp, 30/06/2026 [SX p43]). Họ Lilama là liên kết 35–41%; giao dịch nội bộ: phải trả Lilama 10 137,4, chi phí phải trả L10 100,7 [p34, p36] ⇒ **rủi ro chuyển giá mẹ–liên kết, WARNING** |
| 11 Tài sản ngoài lõi | HNA (lãi ẩn ~77 sau thuế), BĐS Lilama 27,93%, BV Invest 92,8, xi măng Sông Thao 35,7 / Thăng Long 16,2 (dự phòng 10,3) [p24] |
| 12 Tranh chấp / vụ án | Hamon (Sông Hậu 1) phá sản — 160,4 tỷ bảo lãnh đã thu, treo. Thái Bình 2 (PVC) phải thu 204,4, dự phòng 100%. Không tìm thấy khởi tố liên quan LLM [Web] |
| 13 Năng lực, chi phí | Không công bố số thợ hàn trong BCTC quý. Lương phải trả 95,1. Xuất khẩu chế tạo: Neom (Saudi), module H2GS (Thuỵ Điển) |
| 14 Biên theo mảng / vai trò | Không có báo cáo bộ phận. Biên gộp tổng: 9T/25 4,0% → 9T/26 31,3% (quyết toán) |
| 15 Định mức NĐ 206 / TT 38 | Chưa có thông tin từ DN |

## 10. Vĩ mô (display-only — không đổi giá trị nội tại)

**Từ snapshot 18/11:**
- IP T10 +15,0%; GDP Q3 +9,95%; CPI 5,09%.
- Lương +10,0% YoY ⇒ áp lực chi phí nhân công cho nhà thầu.
- FDI luỹ kế +13,1%.
- USD/VND −2,54%/12T: LLM giữ 63,8 triệu USD ⇒ VND mạnh lên gây lỗ đánh giá lại.
- Lãi huy động hiệu dụng 7,4% đi ngang.
- `gdp_construction` STALE ⇒ chưa có số.

**Bobby:** ngành EPC lắp máy 12T ADMIN 0,45 / CYCLICAL 0,30 / STRUCTURAL 0,25; pipeline điện (QT II, Ô Môn IV, Long Phú 1, LNG) dồi dào nhưng tiến độ do hành chính quyết định.

## 11. Pháp lý / quản trị — chỉ WARNING (không bake vào base)

- ⚠️ **Kiểm toán NGOẠI TRỪ 3 năm liền + diện cảnh báo HNX.** BCTC hợp nhất kiểm toán 2023, 2024, 2025 (AASC) đều ngoại trừ [HNX381; CV 245/TCT-TCKT 17/04/2026]. HNX ra QĐ 381/QĐ-SGDHN ngày 06/04/2026 **duy trì diện cảnh báo** với lý do "BCTC năm bị kiểm toán ngoại trừ từ 03 năm liên tiếp trở lên" (điểm a khoản 1 Điều 33 Quy chế UPCoM theo QĐ 23/QĐ-HĐTV 18/03/2026). Phương án khắc phục công ty nêu: đôn đốc người đại diện vốn ở con/liên kết; trình "Định hướng phát triển 2026–2030" (gồm thoái vốn đơn vị yếu) — **chưa được phê duyệt**, đề án cơ cấu lại 2021–2025 đã hết hiệu lực.
- ⚠️ **Soát xét bán niên 2026 (AASC số 280826.018/BCTC.KT2, 28/08/2026): KẾT LUẬN NGOẠI TRỪ** [SX p5–7]:
  - Công ty con (Cơ khí Lắp máy, Lilama 5, Lilama 7): phải thu quá hạn 87,61 tỷ chưa đánh giá được khả năng thu hồi; chi phí SXKD dở dang 250,22 tỷ không xác định được tính chính xác/tổn thất; Lilama 5 lãi vay quá hạn 74,01 + khoản vay BIDV 183 tỷ — không xác định tính đầy đủ chi phí lãi; Cơ khí Lắp máy vốn hoá 36,6 tỷ lãi vay vào "phải thu khác" (LN chưa phân phối ghi thừa 36,6); lãi chậm nộp BHXH 8,03 tỷ chưa ghi nhận; Lilama 7 chi phí chờ phân bổ 2,1 tỷ và công nợ 50,89/48,35 tỷ không đánh giá được.
  - Liên kết (Lilama 69-3, BĐS Lilama): giá trị theo vốn chủ sở hữu chưa xét ảnh hưởng ngoại trừ trên BCTC 2025 của chính chúng.
  - **Vấn đề cần nhấn mạnh:** công việc **quyết toán cổ phần hoá** đang thực hiện; chưa có quyết định phê duyệt quyết toán giá trị vốn Nhà nước tại thời điểm chuyển thành công ty cổ phần.
  - Các khoản ngoại trừ **lặp lại gần nguyên** từ năm 2025 (phải thu quá hạn 76,17 → 92,26; WIP 287,24 → 246,69 [KT25, CV 197]) ⇒ vấn đề mang tính cấu trúc, không phải mới phát sinh.
- ⚠️ **Quyết toán CPH chưa duyệt:** khi được duyệt có thể phát sinh điều chỉnh vốn Nhà nước (hai chiều, chưa lượng hoá được). WARNING, không vào base.
- ⚠️ **Công ty con vỡ nợ ngân hàng:** ~330 tỷ vay quá hạn (Lilama 5 từ 2017–18; Cơ khí Lắp máy hết hạn 2022; Lilama 7 hết hạn 02/2024) [SX p55]. Không thấy bảo lãnh của mẹ trong các trang đã đọc (Phụ lục 01 ghi tài sản bảo đảm của chính công ty con) — chưa loại trừ; định giá HN đã trừ 100% các khoản vay này (thận trọng).
- ⚠️ **Free float 2,12%**: Bộ Xây dựng 97,88% = 780,32 tỷ vốn góp tại 30/06/2026 [SX p43, TM25b] (đính chính 2, bỏ nguồn Vietstock 2020). Cổ đông thiểu số không có tiếng nói về dùng tiền; là trụ của kịch bản xấu.
- ⚠️ **Kiểm toán 2025 TĂNG lãi:** LNST HN trước kiểm toán 356,9 → sau 473,3; LNST mẹ riêng 356,9 → 507,1 [KT25, CV 197]. Công ty chỉ giải thích "số liệu BCTC công ty mẹ sau kiểm toán thay đổi" — **không nêu khoản mục** ⇒ chưa rõ lý do.
- ⚠️ **Phạt CBTT 60 triệu**; **room ngoại**: không tìm được văn bản gốc ⇒ chưa xác minh.
- ⚠️ **"Scandal di cư"**: Thái Bình 2 (vụ án PVC — lịch sử) đã dự phòng 100%; Vũng Áng 1 / Long Phú 1 là nợ đọng nhà nước, chưa có tranh chấp công khai; rủi ro di cư sang **quyết toán** (đảo các khoản đã hoàn nhập), **chuyển giá với liên kết họ Lilama**, và **quyết toán CPH**.
- ⚠️ **Cho vay họ Lilama yếu** (Lisemco, 45.1, Hà Nội) 394,7 đã mất trắng (dự phòng 100%) ⇒ lịch sử dùng tiền kém.
- ⚠️ **Pha loãng / tăng vốn**: tăng vốn điều lệ lên 1.500 tỷ (2026–27) và 2.500 tỷ (2028–30) [Web]. Sau cổ tức cổ phiếu 31,7% (~1.050 tỷ) vẫn còn ~450 tỷ phát hành mới; giá chưa rõ. Base NPV=0.

## 12. Mốc khoá trước (2026-11-18, cập nhật vòng 2) + điều kiện đổi nhận định (hai chiều)

**Mốc khoá trước:**
1. **BCTC Q4/2026** (~20/01/2027): LNTT Q4 sau khi loại hoàn nhập/thanh lý.
   - Dự báo khoá: ≤ 150 tỷ.
   - Biên gộp Q4: **≤ 20%** (quyết toán giảm dần).
2. **BCTC kiểm toán 2026** (~03/2027): loại ý kiến (dự báo khoá: **vẫn ngoại trừ**, năm thứ 4); thuyết minh cam kết/bảo lãnh của mẹ cho con; WIP theo dự án; tiền bị hạn chế.
3. **Kết quả đấu giá L61** (Q4/2026) và **số cp HNA còn giữ**.
4. **Dùng tiền:** tiền gửi có kỳ hạn + không kỳ hạn tại 31/12/2026 ≥ 2.500 tỷ (khoá: còn), hoặc giải ngân "đầu tư phát triển" có dự án cụ thể.
5. **Định hướng 2026–2030 / quyết toán CPH**: có quyết định phê duyệt trong 2026 hay không (khoá: chưa).

**Đổi nhận định LÊN (về phía rẻ / nâng tâm):**
- (a) Biên gộp ≥ 10% ở **hai quý liên tiếp không có quyết toán/hoàn nhập** ⇒ biên cơ sở 10% ⇒ tâm ~32.900 (tuyến tính theo §8b: +1.505 đ/cp mỗi 1pp) ⇒ giá/tâm ~1,0.
- (b) Cổ tức tiền ≥ 3.000 đ/cp, hoặc mua lại/chia tiền ⇒ giảm trọng số kịch bản xấu (10/50/40 ⇒ 30.013).
- (c) Thu đủ Vũng Áng 1 hoặc ghi nhận Hamon 160 có lợi.
- (d) Giá ≤ 20.909 (0,85×tâm mới). D gốc 1,69 > ln3 (sau khử một lần 0,71–0,84) ⇒ cần Mike/user xác nhận, không tự kích hoạt.
- (e) Gỡ ngoại trừ / ra khỏi diện cảnh báo nhờ thoái vốn Lilama 5/7/Cơ khí.

**Đổi nhận định XUỐNG:**
- (a) Q4/26 hoặc Q1/27 lỗ hoạt động khi hết quyết toán.
- (b) ~~Kiểm toán ngoại trừ phải thu/WIP.~~ **ĐÃ KÍCH HOẠT** (thực ra đã có từ 2023; vòng 1 bỏ sót). Ảnh hưởng nhãn: không đưa vào base theo luật; độ nhạy xoá 100% khoản ngoại trừ ⇒ tâm 21.278 (17.573 nếu thêm liên kết về 0) ⇒ **nhãn ĐẮT giữ nguyên, nghiêng đắt hơn**. Thay bằng trigger mới: (b') ngoại trừ **mở rộng sang công ty mẹ** hoặc chuyển thành **từ chối / trái ngược**.
- (c) Tiền dùng cho vay/đầu tư vào đơn vị họ Lilama yếu kém (lặp lại 394,7 đã mất), hoặc mẹ phải trả nợ thay công ty con.
- (d) Phát hành tăng vốn giá thấp cho cổ đông chi phối.
- (e) Phải thu TKV 1.080 quá hạn > 12 tháng.
- (f) Quyết toán CPH điều chỉnh giảm vốn chủ.

## 13. Theo dõi

- Ngày thực hiện cổ tức cổ phiếu 31,7%: điều chỉnh giá và số cp.
- Diện cảnh báo HNX (ngoại trừ 3 năm) — thoát được khi BCTC 2026 không còn ngoại trừ.
- Quyết toán CPH + Định hướng 2026–2030 (thoái vốn Lilama 5/7/Cơ khí).
- CFO Q3/24, Q2/25: truy nguồn trong LCTT quý.
- Phần giá trị LLM trong QT II (BCTN 2026).
- Bảo lãnh đang phát hành; bảo lãnh của mẹ cho vay công ty con (BCTC kiểm toán 2025 đã tải, chưa đọc thuyết minh).
- Giá trị thị trường các liên kết L43/L44/L45/L63.

## Phụ lục E — Phản biện & đính chính
**fundamental-skeptic r1 (18/11/2026): REFUTED (medium)** — `skeptic_r1.md`. Số cốt lõi vòng 1 tái lập được (tâm SOTP 31.589; BS/KQKD khớp ảnh; BQ khớp); bị bác ở nhãn "quanh hợp lý 1,05×" và phần kiểm toán/pháp lý. Vòng 2 áp đủ 13 đính chính:

| # | Vòng 1 viết | Vòng 2 sửa | Nguồn kiểm |
|---|---|---|---|
| 1 | Ý kiến kiểm toán "chưa tìm được / GAP" | Ngoại trừ 2023–25 + soát xét H1/26 ngoại trừ + nhấn mạnh quyết toán CPH; AASC kiểm toán 2025 | [SX p5–7, p53 TM44], [KT25], [HNX381] |
| 2 | Bộ Xây dựng ~97,9% theo Vietstock 2020 | 97,88% = 780,32 tỷ tại 30/06/2026 | [SX p43] |
| 3 | Lãi vay ~4,1%/năm | Rút lại: ~330/871 tỷ vay HN là vay quá hạn lãi phạt ở công ty con; chi phí lãi thật chưa đo được | [SX p37, p54–55] |
| 4 | "Tồn kho giảm … dự án bàn giao" | 242,7/307,4 ở công ty con (mẹ 64,7), trùng WIP bị ngoại trừ | [RG], [SX p6] |
| 5 | Giữ liên kết 328,2 theo sổ, không cảnh báo | Giữ sổ (NPV=0) + WARNING + độ nhạy 50% / 0 | [SX p7]; calc REV2 |
| 6 | Chênh Q2 10,4 tỷ quy cho BQ | Điều chỉnh soát xét (H1 mẹ 606,2 → 595,8), không phải lỗi BQ | [SX p10]: LNST mẹ H1 soát xét 595,78; tự lập 115,9 + 490,3 = 606,2 |
| 7 | Biên gộp cơ sở 7%, không có độ nhạy | Hạ về trung vị lịch sử 4,5% (không có cơ sở độc lập cho 7%); độ nhạy 4–7% + điểm hoà vốn 10,3% | BQ gpm_ttm; calc REV2 |
| 8 | Xấu = RI, cơ sở/tốt = SOTP; trọng số không cơ sở | Một phương pháp SOTP cho cả 3 (tiền mắc kẹt qua f = 0,077); trọng số ghi rõ là mặc định + lưới độ nhạy; tách nguồn biên độ | calc REV2 |
| 9 | D = 1,69 chưa lượng hoá | Khử tạm ứng 657,8 + tồn kho 440,9 ⇒ V_dài 20.189–23.088, D 0,71–0,84; CFO Q3/24 & Q2/25 chưa giải thích | calc REV2 |
| 10 | Không đối chiếu BCTC riêng | NFP mẹ 1.605,8 vs HN 1.466,2; tâm theo riêng 24.604 ≈ HN | [RG]; calc REV2 |
| 11 | Thiếu WARNING CPH / vỡ nợ con / lý do cảnh báo | Đã thêm (§11); lý do cảnh báo = ngoại trừ 3 năm liền | [HNX381] |
| 12 | Chưa render file scan, chưa có giải trình riêng | Render toàn bộ 57 trang soát xét; đọc GTR-Q2 (LNST riêng Q2 483,96) + GTR-6T (566,49; "quyết toán cho biên cao") | `src_r2/`, `png/bn_*`, `png/gtr6_*` |
| 13 | Không nói về §2.5 | §2.5 fear-buy không áp dụng (P/B mẹ 1,22, moat NONE, xu hướng tăng) | §0 |

**Nhãn:** v1 "quanh giá trị hợp lý, 1,05×" → v2 **"ĐẮT, 1,35×"** (tâm 31.589 → 24.599). Phần lớn thay đổi do đính chính 7 (biên cơ sở 7% → 4,5% và kịch bản tốt 10% → 7%); đính chính 8 (xấu RI → SOTP-mắc-kẹt) gần trung tính (4.996 → 4.033 trước TK).
**Chưa làm:** CFO Q3/24 và Q2/25 chưa truy nguồn; thuyết minh cam kết/bảo lãnh trong BCTC kiểm toán 2025 (57 trang, đã tải `src_r2/llm_25cn_bctc_hn_da_kt_signed.pdf`, mới render 9 trang đầu, chưa đọc); chưa chạy fundamental-skeptic vòng 2.


## Nguồn

**BCTC và công bố của công ty:**
- BCTC hợp nhất / riêng Q3/2026 (Lilama IR): https://lilama.com.vn/bao-cao-tai-chinh-rieng-hop-nhat-quy-iii-nam-2026 — `src/`. Trang đã đọc ảnh: p3–8, 10, 21–26, 28, 34–38, 40–42.
- Giải trình LNST Q2/2026, CV 23/TCT-TCKT 30/07/2026: `src/giai_trinh_lnst_hop_nhat_tv_v2.pdf`.
- BCTC hợp nhất bán niên 2026 đã soát xét (AASC): `src/bchn_lilama_30.06.26_tv.pdf` (render `png/bn_p01–57`).
- Giải trình LNST BCTC riêng Q2 và 6T/2026: https://lilama.com.vn/sites/default/files/giai_trinh_lnst_rieng_tv.pdf ; https://lilama.com.vn/sites/default/files/giai_trinh_lnst_bctc_rieng_6_thang_dau_nam_2026-_ta.pdf
- BCTC kiểm toán 2025 + CV 196/197 giải trình ngoại trừ: https://lilama.com.vn/bao-cao-tai-chinh-rieng-hop-nhat-sau-kiem-toan-nam-2025-va-giai-trinh-lnst-tren-bctc
- QĐ 381/QĐ-SGDHN + CV 245 giải trình cảnh báo: https://lilama.com.vn/cong-van-cua-so-giao-dich-chung-khoan-ha-noi-va-giai-trinh-ve-nguyen-nhan-canh-bao-doi-voi-co-phieu
- (Tất cả bản tải ở `src_r2/`.)

**Báo chí:**
- nguoiquansat 07/11/2026: https://nguoiquansat.vn/lai-dot-bien-470-ty-dong-nho-hoan-nhap-du-phong-ong-lon-tong-thau-nganh-lap-may-chia-co-tuc-ty-le-gan-32-326748.html
- baodauthau 19/05/2026 (LN sau kiểm toán): https://baodauthau.vn/nhung-doanh-nghiep-doi-mau-loi-nhuan-sau-kiem-toan-post199005.html
- ĐHĐCĐ 2026: https://baokiemtoan.vn/vi/bai-viet/dai-hoi-dong-co-dong-2026-lilama-cung-co-noi-luc-san-sang-but-pha
- L61: https://baodauthau.vn/lilama-sap-dau-gia-411-von-tai-lilama-69-1-thach-thuc-vuc-day-doanh-nghiep-lo-lon-post210406.html ; https://kinhtechungkhoan.vn/lilama-muon-rut-sach-von-khoi-lilama-69-1-he-lo-phuong-an-chuyen-nhuong
- HNA: https://vietstock.vn/2025/06/gia-dau-cao-hon-thi-gia-gan-40-ai-se-mua-hon-87-trieu-cp-hna-tu-lilama-739-1316302.htm
- Ô Môn I: https://kinhtechungkhoan.vn/lilama-gianh-duoc-hop-dong-epc-gan-2-nghin-ty-tai-du-an-nhiet-dien-o-mon-1-1398265.html
- QT II: https://nhadautu.vn/powerchina-cung-lilama-tham-gia-du-an-dien-hon-52000-ty-tai-quang-tri-d102896.html
- Hồ sơ cổ đông / cảnh báo: https://finance.vietstock.vn/LLM/ho-so-doanh-nghiep.htm ; https://finance.vietstock.vn/LLM-tong-cong-ty-lap-may-viet-nam-ctcp.htm

**Dữ liệu nội bộ:**
- BQ: `model/bq_fin_LLM.csv`, `model/bq_peers.csv`, `model/bq_px_LLM.csv`.
- Bobby: `kb/data_registry/market-state/sector_read_epc_lap_may_20261118.md`.
- Snapshot: `macro_snapshot_20261118.md`.
