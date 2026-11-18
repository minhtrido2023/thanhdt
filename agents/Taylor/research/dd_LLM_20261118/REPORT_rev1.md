# DD — LLM (Tổng Công ty Lắp máy Việt Nam – CTCP, Lilama; UPCoM) · 2026-11-18 · job `Taylor_20261118_122349` · VÒNG 1 (chưa qua fundamental-skeptic)

> Chỉ nghiên cứu, không phải khuyến nghị mua. Không đặt lệnh, không wire. Pháp lý chỉ ghi WARNING (luật 27/09).
> Ký hiệu nguồn:
> - **[HN pX]** = BCTC hợp nhất Q3/2026, ký 27/10/2026 (`src/bao_cao_tai_chinh_hop_nhat_q3.2026_vie-da_nen.pdf`). pX là số trang PDF; đã render ảnh `png/hn_pXX.png` và đọc từ ảnh. Lớp text OCR bị lệch cột (xem §2).
> - **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker`.
> - **[GT-Q2]** = giải trình LNST Q2, CV 23/TCT-TCKT ngày 30/07/2026.
> - **[Web]** = báo chí, có URL ở mục Nguồn.
> - **[Bobby]** = `kb/data_registry/market-state/sector_read_epc_lap_may_20261118.md`.
>
> Mọi số do tôi tự đặt đều gắn nhãn **(ước lượng)**. Mô hình tái lập: `model/calc.py` + `model/assumptions_LLM_20261118.json`, md5 `dea9f4745bf0227a6f2b2d06c3e897ee`. Output: `model/calc_output.txt`.

## 0. Kết luận

**Giá 33.300 đ (18/11/2026) = 1,05 lần tâm giá trị 31.589 đ, tức nằm quanh giá trị hợp lý.** Giá không rẻ. Nó cũng không đắt rõ rệt, **nếu** chấp nhận rằng tiền ròng tính theo sổ sách. Vùng giá trị sau chiết khấu thanh khoản là **4.497–51.769**, rộng bất thường. Mốc 0,85×tâm = **26.850**.

- **Lợi nhuận "kỷ lục" phần lớn KHÔNG bền.**
  - LNTT 9T/26 = 904,5 tỷ. Trong đó 290,5 tỷ là khoản một lần đã gọi tên được:
    - hoàn nhập dự phòng bảo hành ròng 227,1 [HN p41 TM31];
    - lãi thanh lý tài sản cố định 61,0 [HN p42 TM33–34];
    - hoàn nhập bảo hành khác 2,3.
  - Phần còn lại vẫn mang **biên gộp quyết toán**: 9T là 31,3%, Q3 là 51,2%. Biên gộp 9T/25 chỉ 4,0%; GPM TTM trên BQ giai đoạn 2017–24 chủ yếu 2–6%.
  - LNST mẹ 7 năm 2018–2024 cộng dồn là **−71 tỷ** [BQ].
  - LNST chuẩn hoá theo luật (trung vị TTM 12 quý Q4/23–Q3/26) = **107,2 tỷ** ⇒ V_ngắn **9.965**.
- **Tiền mặt lớn nhưng phần lớn là tiền "trôi nổi" của dự án.**
  - Tiền + tiền gửi = 3.576 tỷ; trừ vay 621 ⇒ net cash 2.956.
  - Vốn lưu động vận hành **−1.490 tỷ**, gồm: khách hàng ứng trước 1.119 (586 của Quảng Trạch II); chi phí phải trả 1.600 (Vũng Áng 1 là 752); dự phòng bảo hành 747.
  - ⇒ **Vị thế tài chính ròng sau nợ vận hành = 1.466 tỷ = 18.390 đ/cp**.
- **Tâm phụ thuộc gần như hoàn toàn vào câu hỏi: 1.466 tỷ có được dùng/chia với giá trị bằng sổ sách không.**
  - Kịch bản cơ sở (SOTP): ghi theo sổ sách, nhất quán với luật NPV=0 và kế hoạch "đầu tư phát triển ~850 tỷ" năm 2026 [Web baokiemtoan].
  - Kịch bản xấu: tiền vẫn mắc kẹt như suốt 2017–2024. Khi đó tiền 2–3 nghìn tỷ nằm yên trong khi ROE ~0, và lãi tiền gửi 9T/26 chỉ 34,4 tỷ trên 3,6 nghìn tỷ (≈1,3%/năm) ⇒ **4.996**.
  - Nếu tiền mắc kẹt ở MỌI kịch bản, phương pháp thu nhập thặng dư cho **13.560** ⇒ giá/tâm 2,46.
- **Hai nền giá trị phân kỳ mạnh.** V_ngắn là 9.965, V_dài là 54.216, **D = 1,69 > ln3**. V_dài cao là do vốn lưu động được giải phóng (tạm ứng QT II, thu nợ cũ), không phải do capex thấp. Theo luật, 0,85×tâm KHÔNG tự kích hoạt; cần Mike/user phán đoán.
- **Pháp lý và quản trị — WARNING:**
  - Free float ~2%: Bộ Xây dựng nắm 78,03 triệu cp ≈ 97,9%, theo hồ sơ Vietstock cập nhật 2020, cần kiểm lại.
  - Vietstock ghi LLM "đang bị cảnh báo"; lý do chưa tìm được.
  - Chưa tìm được ý kiến kiểm toán BCTC 2025.
  - Phải thu và cho vay các đơn vị Lilama yếu kém đã dự phòng gần đủ.
  - Có dính tới Thái Bình 2: phải thu 204 tỷ, đã dự phòng 100%.
- **Thanh khoản cực thấp:** ADV trung vị 90 phiên = 15.200 cp ≈ **0,45 tỷ/phiên** [BQ]. Ở 10–20% tham gia, vị thế 1 tỷ cần 11–22 phiên để thoát.

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
| BQ NP Q2/26 490,3 | Q2 mẹ = 694,98 − 115,9 − 99,2 = **479,9** | Trùng số Mike (479,9) |
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
- **Q2/2026: LNST hợp nhất 489,4** [GT-Q2]. Q3 không có hoàn nhập bảo hành (CP bán hàng Q3 = 0) ⇒ khoản hoàn nhập 376,0 nằm ở H1, gần như chắc ở Q2. Q2 scan chưa render nên chưa tách chính xác Q1/Q2.
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
  - Hàng tồn kho giảm 763,1 → 307,4 [p3], đúng với dự án đã bàn giao/quyết toán.
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
- **Không thấy** thuyết minh tiền gửi bị hạn chế hay ký quỹ bảo lãnh trong các trang đã đọc. Cần kiểm hạn mức bảo lãnh (điểm 8 của Bobby).

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
- **Chi phí lãi vay:** 25,0/9T trên vay bình quân ~810 ⇒ **~4,1%/năm (ước lượng)**, thấp hơn tầng B–C 7,4–9% của Bobby. Vay ngắn hạn có bảo đảm hay không: chưa đọc TM16.
- **Rủi ro ngoài bảng [p37 TM24]:** đã thu 160,4 tỷ tiền bảo lãnh thực hiện hợp đồng của Hamon (Sông Hậu 1) nhưng **chưa ghi nhận vào lãi lỗ**, vì Hamon đang phá sản và nghĩa vụ chưa xác định. Có thể thành thu nhập (upside) hoặc phải hoàn trả. Không đưa vào base.

## 6. Cấu trúc tập đoàn, SOTP, Lilama 69-1 — trả lời câu hỏi 4

- **Công ty con hợp nhất** chỉ có 5 đơn vị nhỏ [p10]: Lilama SEA (Brunei) 99%; Lilama 5 51%; Lilama 7 51%; Cơ khí Lắp máy 51%; Tư vấn LHT 60% (đang giải thể).
- **L10, L18 (LM8), 69-1, 69-3, 45.x là CÔNG TY LIÊN KẾT** (vốn chủ sở hữu, 35–41%) [p23]. ⇒ LLM hợp nhất gần như = công ty mẹ, và "cổ tức từ con" bị loại khi hợp nhất không phải là nguồn lãi.
- **NCI −66,3** (công ty con âm vốn).
- **Đầu tư liên kết theo sổ: 328,2**; đầu tư khác 255,2 (dự phòng −30,2) [p3, p24].
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

### 8a. Khung

- **r = 13,5%.** Lãi huy động 12T hiệu dụng 7,4% (CCTG 12M 02/11) = điểm neo 03/11 ⇒ r không đổi [Bobby nguồn; macro snapshot].
- **g = 0.** ROE cơ sở < r ⇒ tái đầu tư vào mảng cũ phá giá trị. Hợp đồng/dự án mới được tính NPV=0.
- **Phương pháp chính (SOTP):** giá trị = NOPAT hoạt động / r + vị thế tài chính ròng sau nợ vận hành (1.466,2, theo sổ) + đầu tư tài chính dài hạn theo sổ (553,7) + lãi ẩn HNA (77,2).
- **Cơ sở ghi tiền theo sổ:** luật NPV=0. Kế hoạch 2026 "đầu tư phát triển ~850 tỷ" và tăng vốn lên 1.500 tỷ [Web baokiemtoan] cho thấy tiền sẽ được triển khai.

| Kịch bản | Giả định | Cơ sở | Giá trị/cp (trước TK thanh khoản) |
|---|---|---|---|
| Xấu (25%) | Tiền tiếp tục là float/mắc kẹt; ROE 2% trên VCSH mẹ (thu nhập thặng dư) | 2017–24: tiền 2–3 nghìn tỷ [BQ Cash_P0] trong khi ROE ~0; lãi tiền gửi hiện ~1,3%/năm | **4.996** |
| Cơ sở (50%) | NOPAT 136 = 0,8 × (DT 4.500 × biên gộp 7% − QLDN 100 − bảo hành/dự phòng 45) **(ước lượng)** | DT TB 2023–25 = 5.538, KH 2026 3.378, thêm QT II/Ô Môn I; biên 7% = trên trung bình GPM lịch sử 2–6%, dưới biên quyết toán 2026 | **38.939** |
| Tốt (25%) | NOPAT 336 = 0,8 × (6.000 × 10% − 120 − 60) **(ước lượng)** | DT 2024 = 6.102; KH LNTT 2026 450 | **57.521** |
| **Có trọng số** | | | **35.099 trước TK / 31.589 sau TK 10%** |

- Ngoài ra (chỉ là độ nhạy, không phải kịch bản riêng): nếu SOTP-xấu dùng NOPAT −30 và tổn thất phải thu cũ 200 **(ước lượng)** thay cho thu nhập thặng dư ⇒ 21.007.
- **Không đưa vào base:**
  - Hamon 160,4 (hai chiều).
  - Dự phòng bảo hành dài hạn 737,7 có thể hoàn nhập khi hết hạn (upside một lần, đã có tiền lệ 376).
  - Quyết toán Vũng Áng 1 (phải thu 876,7 vs chi phí phải trả 752,1; ròng +124,6 nếu thu đủ).
  - Thoái L61 (≤41).

### 8b. Độ nhạy (`calc_output.txt`)

- **Lãi huy động (β=1):** ±50bp ⇒ 32.112 / 31.102 (+1,7% / −1,5%); ±100bp ⇒ 32.678 / 30.650 (+3,4% / −3,0%). β=0,5: một nửa.
- **Chiết khấu thanh khoản 0 / 5 / 10 / 20%:** 35.099 / 33.344 / **31.589** / 28.079.
- **Tiền mắc kẹt một phần** (cắt 25% / 50% vị thế tài chính ròng): 28.485 / 25.382.
- **Tiền mắc kẹt ở cả 3 kịch bản** (thu nhập thặng dư, ROE 2 / 7 / 12%): **13.560** ⇒ đây là cận dưới "phương pháp".
- **Trọng số:** xấu 50 / cơ sở 40 / tốt 10 ⇒ 21.443; xấu 10 / 50 / tốt 40 ⇒ 38.680. HNA = 0 ⇒ 30.717.
- **ROE ngầm định ở giá 33.300** (thu nhập thặng dư, sau thanh khoản): **17,9%** vĩnh viễn trên VCSH mẹ. Mức này chỉ đạt ở năm quyết toán/hoàn nhập; trong 10 năm chưa năm nào đạt mà không có khoản một lần.
- **Cổ tức cổ phiếu 31,7%** (đã thông qua, chưa thực hiện): không đổi tổng giá trị. Quy đổi sau chia: tâm ~23.985; giá ~25.285.

### 8c. Hai nền giá trị (chỉ hiển thị, không đổi tâm)

| Nền | Giá trị | Ghi chú |
|---|---|---|
| V_ngắn (LNST chuẩn hoá = trung vị TTM 12 quý = 107,2; ROE 4,9%; g = 0 ⇒ không tái đầu tư) | **9.965** | Trung vị neo vào 2023–25 khi quyết toán chưa xảy ra |
| V_dài (FCFE = CFO 3 năm TB 595,6 − capex 12,1) | **54.216** | capex/CFO 0,02 |
| V theo C4 = CFO − min(capex, KH 15,7) | 54.216 | Chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi |
| V theo D2 = CFO − 1,75% × DT TTM 4.145,5 | 48.600 | Chưa qua tiêu chí khoá trước (0/9 nền qua; D2 đạt T1–T4, trượt BH-FDR ở 3/6 tháng, chỉ sống ở 12 tháng), chỉ theo dõi; capex/DT trung vị 12 mã xây dựng BQ |

**D = |ln(9.965 / 54.216)| = 1,69 > ln3 ⇒ PHÂN KỲ MẠNH.** Nguồn chênh KHÔNG phải capex (capex/CFO 2%), mà là **vốn lưu động**:
- CFO 3 năm gồm tạm ứng mới (QT II 586, Ô Môn 338); giải phóng tồn kho 441; thu nợ cũ.
- CFO các năm 2019–2023 âm ở 9/20 quý [BQ].
- ⇒ V_dài **không** phải bằng chứng rẻ.

Luật 0,85×tâm không tự kích hoạt; vùng đọc mở rộng [9.965; 54.216] ⊃ vùng mô hình.

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

- Tâm **31.589**; vùng **[4.497; 51.769]**; 0,85×tâm = **26.850**.
- Giá 33.300 = **1,05× tâm ⇒ "quanh giá trị hợp lý / không rẻ"**. Theo cận dưới phương pháp (tiền mắc kẹt, 13.560) giá là 2,46× ⇒ ĐẮT. Theo V_dài thì rẻ.
- ⇒ **Nhãn phụ thuộc giả định tiền; chưa đủ cơ sở gắn "rẻ".**
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
| 4 Ghi nhận, WIP, dự án COD chưa quyết toán | Tồn kho/WIP 307,4 (đầu năm 763,1). Chưa quyết toán: Vũng Áng 1 (chi phí phải trả 752,1, phải thu 876,7 — COD nhiều năm trước, năm cụ thể chưa kiểm), Sông Hậu 1, NT3&4 (chi phí phải trả 323,7). **Đúng tiền lệ "COD nhiều năm chưa quyết toán"** |
| 5 Dự phòng lỗ HĐ, lãi bị đảo | 2025 trích +448,4 dự phòng (LCTT 9T/25) → 2026 hoàn nhập −150,9; bảo hành hoàn nhập 376,0. Q4 chiếm 32–48% DT năm. Lệch LN–CFO: 2018–24 CFO âm nhiều quý trong khi LN ~0 |
| 6 Ý kiến kiểm toán | **Chưa tìm được** (BCTC kiểm toán 2025 chưa tải/đọc). Tờ CBTT BCTC Q3 tick "không" cho mục ý kiến kiểm toán, nhưng mục này chỉ áp cho BCTC năm 2026. **GAP** |
| 7 Phải thu, tuổi nợ, dự phòng | Phải thu KH 3.101,8, dự phòng 422,8; nợ xấu gốc 582,5 thu hồi 150,0 [p28]; người mua trả trước 1.119,1. Tiền giữ lại bảo hành: không tách |
| 8 Hạn mức bảo lãnh | **Không có** trong các trang đã đọc. GAP — cần BCTC năm / thuyết minh vay |
| 9 Vay, lãi suất | Vay ngắn hạn 620,7, dài hạn 0; lãi vay 25,0/9T ≈ 4,1%/năm (ước lượng); lãi vay đã trả 39,1. Khả năng trả lãi dư thừa (net cash) |
| 10 Sở hữu NN, mẹ–con | Bộ Xây dựng ~97,9% (cần cập nhật). Họ Lilama là liên kết 35–41%; giao dịch nội bộ: phải trả Lilama 10 137,4, chi phí phải trả L10 100,7 [p34, p36] ⇒ **rủi ro chuyển giá mẹ–liên kết, WARNING** |
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

## 11. Pháp lý / quản trị — chỉ WARNING

- ⚠️ **Free float ~2%**: Bộ Xây dựng 78.032.404 cp (Vietstock, cập nhật 2020; tỷ lệ hiện tại và kế hoạch thoái vốn: **không tìm thấy**). Cổ đông thiểu số không có tiếng nói về dùng tiền mặt; đây là trụ của kịch bản xấu.
- ⚠️ **Cảnh báo UPCoM**: Vietstock ghi "đang bị cảnh báo" (18/11); một kết quả tìm kiếm nói vào diện từ 10/04/2025 (chưa thấy trang gốc). Lý do và quyết định gỡ: **không tìm thấy**.
- ⚠️ **Phạt CBTT 60 triệu**: không tìm được quyết định gốc ⇒ chưa xác minh.
- ⚠️ **Room ngoại**: CBTT điều chỉnh tỷ lệ tối đa — **không tìm thấy**.
- ⚠️ **Kiểm toán 2025**: tên kiểm toán viên và loại ý kiến — **không tìm thấy**. LNST 2025 sau kiểm toán 492 tỷ, cao hơn số tự lập 154 tỷ (+45%) [Web baodauthau 19/05/2026] ⇒ kiểm toán **tăng** lãi (bất thường, chưa rõ lý do).
- ⚠️ **"Scandal di cư"**:
  - Thái Bình 2 (vụ án PVC — lịch sử) đã dự phòng 100% phải thu.
  - Vũng Áng 1 / Long Phú 1 (PV Power) là nợ đọng nhà nước, chưa có tranh chấp công khai.
  - Rủi ro di cư sang **quyết toán** (đảo các khoản đã hoàn nhập) và **chuyển giá với liên kết họ Lilama**.
- ⚠️ **Cho vay họ Lilama yếu** (Lisemco, 45.1, Hà Nội) 394,7 đã mất trắng (dự phòng 100%) ⇒ lịch sử dùng tiền kém, cùng chiều với kịch bản xấu.
- ⚠️ **Pha loãng / tăng vốn**: tăng vốn điều lệ lên 1.500 tỷ (2026–27) và 2.500 tỷ (2028–30) [Web]. Sau cổ tức cổ phiếu 31,7% (~1.050 tỷ) vẫn còn ~450 tỷ phát hành mới; giá phát hành chưa rõ. Base NPV=0.

## 12. Mốc khoá trước (2026-11-18) + điều kiện đổi nhận định (hai chiều)

**Mốc khoá trước:**
1. **BCTC Q4/2026** (~20/01/2027): LNTT Q4 sau khi loại hoàn nhập/thanh lý.
   - Dự báo khoá: ≤ 150 tỷ.
   - Biên gộp Q4: **≤ 20%** (quyết toán giảm dần).
2. **BCTC kiểm toán 2026** (~03/2027): loại ý kiến kiểm toán; hạn mức bảo lãnh; WIP theo dự án; tiền bị hạn chế.
3. **Kết quả đấu giá L61** (Q4/2026) và **số cp HNA còn giữ**.
4. **Dùng tiền:** tiền gửi có kỳ hạn + không kỳ hạn tại 31/12/2026 ≥ 2.500 tỷ (khoá: còn), hoặc giải ngân "đầu tư phát triển" có dự án cụ thể.

**Đổi nhận định LÊN (về phía rẻ / nâng tâm):**
- (a) Biên gộp ≥ 10% ở **hai quý liên tiếp không có quyết toán/hoàn nhập** ⇒ NOPAT cơ sở ~250 ⇒ tâm ~+8.000 (ước lượng).
- (b) Cổ tức tiền ≥ 3.000 đ/cp, hoặc mua lại/chia tiền ⇒ giảm trọng số kịch bản xấu.
- (c) Thu đủ Vũng Áng 1 hoặc ghi nhận Hamon 160 có lợi.
- (d) Giá ≤ 26.850 (0,85×tâm). Do D > ln3, cần Mike/user xác nhận.

**Đổi nhận định XUỐNG:**
- (a) Q4/26 hoặc Q1/27 lỗ hoạt động khi hết quyết toán.
- (b) Kiểm toán ngoại trừ phải thu/WIP.
- (c) Tiền dùng cho vay/đầu tư vào đơn vị họ Lilama yếu kém (lặp lại 394,7 đã mất).
- (d) Phát hành tăng vốn giá thấp cho cổ đông chi phối.
- (e) Phải thu TKV 1.080 quá hạn > 12 tháng.

## 13. Theo dõi

- Ngày thực hiện cổ tức cổ phiếu 31,7%: điều chỉnh giá và số cp.
- Lý do cảnh báo UPCoM.
- Phần giá trị LLM trong QT II (BCTN 2026).
- Hạn mức bảo lãnh.
- Giá trị thị trường các liên kết L43/L44/L45/L63.

## Phụ lục E — Phản biện & đính chính
Chưa có (vòng 1, chờ fundamental-skeptic).

## Nguồn

**BCTC và công bố của công ty:**
- BCTC hợp nhất / riêng Q3/2026 (Lilama IR): https://lilama.com.vn/bao-cao-tai-chinh-rieng-hop-nhat-quy-iii-nam-2026 — `src/`. Trang đã đọc ảnh: p3–8, 10, 21–26, 28, 34–38, 40–42.
- Giải trình LNST Q2/2026, CV 23/TCT-TCKT 30/07/2026: `src/giai_trinh_lnst_hop_nhat_tv_v2.pdf`.

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
