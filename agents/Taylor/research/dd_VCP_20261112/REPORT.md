# DD — VCP (CTCP Xây dựng và Năng lượng VCP, UPCoM) · 2026-11-12 · job `Taylor_20261112_051752`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua, không đặt lệnh, không wire, không gửi email. User quyết.
> Định giá MÙ giá thị trường: mô hình dựng xong mới so giá.
> Nguồn: **[Q3]** = BCTC hợp nhất Q3/2026, chưa soát xét, lập 28–29/10/2026 (`src/bctc_hn_q3_2026.pdf`, ảnh `img/hn_q3_pNN.png`).
> **[H1]** = BCTC hợp nhất giữa niên độ 6T/2026, AASC soát xét, kết luận chấp nhận toàn phần, 25/08/2026 (`src/bctc_hn_h1_2026_reviewed.pdf`, `img2/h1_pNN.png`).
> **[KT25]** = BCTC hợp nhất 2025, AASC kiểm toán, ý kiến chấp nhận toàn phần, không có đoạn nhấn mạnh, 24/03/2026 (`src/bctc_hn_2025_audited.pdf`, `img2/kt25_pNN.png`).
> **[GT]** = CV 110/2026/CV-VCP ngày 29/10/2026 giải trình LNST Q3. **[QĐ]** = QĐ 16587/QĐ-HAN-KTr3-XPHC ngày 09/10/2026 của Thuế TP Hà Nội.
> **[CT]** = TB 1xx/2026/CV-VCP ngày 05/10/2026 về chốt quyền cổ tức 2025. **[BQ]** = `tav2_bq.ticker_financial` / `tav2_bq.ticker`.
> **[Bobby]** = `kb/data_registry/market-state/sector_read_thuy_dien_20261112.md` (đọc mù).
> Mô hình: `calc/model.py` + `calc/assumptions.json` → `calc/model_out.json` (md5 ở `calc/MD5.txt`). Số không đo được ghi **(ước lượng)**.

## 0. Kết luận

**Tâm giá trị 41.560 đ/cp trước chiết khấu thanh khoản; 40.273 đ/cp sau chiết khấu (vị thế 1 tỷ).
Vùng [21.669 ; 67.385]** (bear/bull trước chiết khấu; sau chiết khấu [20.997 ; 65.297]). r = 13,5%, g = 2% (ước lượng).
*(Vòng 1: tâm 41.810 / 40.515, bear 22.502. Vòng 2 đổi rổ lỗ cho vay ở bear 332,0 → 401,9 tỷ nên bear và tâm giảm; mọi thứ khác giữ nguyên. Skeptic vòng 1: REFUTED mức văn bản, §Phụ lục E.)*

| Giá so sánh | So với tâm sau chiết khấu (40.273) | Nhãn |
|---|---|---|
| **37.900** (đóng cửa 11/11/2026, BQ) | **−5,9%**, trên ngưỡng 0,85 × tâm = 34.232 | **TRONG VÙNG, sát tâm.** Chưa đủ biên an toàn |
| 31.700 (giá trong brief; theo BQ là giá đóng 05–06/11) | −21,3%, dưới 0,85 × tâm | Rẻ, nếu còn mua được ở mức đó |

**Biên −5,9% là mỏng, và nhạy với đúng những phần chưa giải thích được ở bull** (tâm sau chiết khấu, bear mới, [model_out.json]):

| Độ nhạy | Tâm trước / sau chiết khấu | 37.900 so với tâm sau CK |
|---|---|---|
| Headline (w 0,30/0,45/0,25) | 41.560 / **40.273** | −5,9% |
| (a) Bull trừ LN gộp phế liệu Q3 vượt mức thường: N bull 700,8 → 625,9 (−74,9) | 39.618 / **38.390** | −1,3% |
| (b) = (a) + trừ lãi dồn tích chưa thu bằng tiền: N bull → 568,1 (−57,8 thêm) | 38.118 / **36.937** | **+2,6% (giá TRÊN tâm)** |
| Trọng số bear/base/bull 0,35/0,45/0,20 | 39.275 / 38.058 | −0,4% |
| Trọng số 0,40/0,40/0,20 | 38.334 / 37.146 | +2,0% |

(a): GP hàng hoá Q3 ước ≈ 123,7 tỷ trên DT ≈ 488,6 tỷ (biên ≈ 25%); ở biên thường 4,5% (H1/26) chỉ còn 22,0 ⇒ phần vượt 101,7 × (1 − 20% thuế thương mại, ước lượng) × 0,92 phần mẹ = 74,9.
Skeptic ước ~72; tính lại ra 74,9 (chênh vì biên chuẩn và thuế suất là ước lượng). (b): lãi dồn tích chưa thu 9T = 91,6 − 21,25 = 70,4 tỷ (§2a) × 0,92 × (1 − 10,7%) = 57,8.
**Hai độ nhạy (a), (b) CHỈ hiển thị, không đổi tâm** (cả hai phần đều chưa chứng minh là không lặp lại). Trọng số 0,30/0,45/0,25 **không có cơ sở định lượng** (ước lượng);
bỏ hai phần chưa giải thích ở bull thì giá 37.900 nằm trên tâm. Hướng ngược lại: biến thể B của mô hình (§8) cho tâm **47.555 / 46.081**.
**Vùng bất định của tâm sau chiết khấu ≈ 36.900 … 46.100 (−3,3k / +5,8k)**; 37.900 nằm gần đáy vùng này.

⚠️ **Lệch giá với brief:** brief ghi 31.700 là giá đóng 11/11. BQ cho thấy 31.700 là giá đóng 05/11 và 06/11; ba phiên sau là
33.600, 35.600, **37.900** (11/11). Từ 23.400 (Price chưa điều chỉnh, 23/10, trước KQ Q3) lên 37.900 là **+62% trong 13 phiên** [BQ].

**Ba điều cần biết nhất:**
1. **Mảng điện có thật và tốt**, nhưng **không phải nguồn của LNST Q3 +100%.** DT điện Q3 **223,0 tỷ (−1,4% YoY)**. LN gộp điện
   tăng 174,4 so với 150,3 vì giá vốn điện giảm 75,9 → 48,6 tỷ, chưa giải thích được. Phần tăng chính đến từ **mảng ngoài điện**:
   LN gộp 174,0 so với 67,8 tỷ, biên **28,9%**. Năm 2025, mảng "hàng hoá" (phế liệu) chỉ có biên gộp 1,5%, H1/26 4,5% [KT25, H1].
   Giải trình CV110 nói tăng "do doanh thu kinh doanh phế liệu" nhưng không giải thích biên.
2. **Phân bổ vốn là rủi ro số 1.** Cho vay **823,4 tỷ** (30/06/2026), chủ yếu cho **cá nhân**, đảm bảo bằng cổ phần bên thứ ba,
   có khoản đảm bảo bằng **chính cổ phiếu VCP** [H1 PL01]. Đó là khoảng **32% vốn chủ công ty mẹ**.
   **Lãi cho vay chủ yếu chưa thu bằng tiền:** 9T/26 DT tài chính 91,6 tỷ nhưng LCTT dòng 27 "tiền thu lãi cho vay, cổ tức, lợi nhuận được chia" chỉ **21,25 tỷ** ⇒ khoảng **77% là dồn tích** [Q3 p5, p7]. Năm 2025 riêng ông Vũ Tuấn Cường
   vay 684,1 tỷ, được ghi là "bên khác" [KT25 PL02]. Các khoản đặt cọc/mua cổ phần lớn trả cho cá nhân lặp lại: 538,8 tỷ ký quỹ ông
   Đoàn Mạnh Hưng (01/01/2025), 266,8 tỷ ông Đỗ Hoàng Dương (31/12/2025), mua Linh Linh 545,7 tỷ từ bà Lương Thị Lợi (03/2026).
   Ngoài ra **46,8% số cổ phiếu VCP (39,22 triệu cp của bên thứ ba) đang cầm cố** cho trái phiếu 500 tỷ dùng để mua Linh Linh [KT25 PL04].
3. **LCTT 9T không khớp biến động bảng cân đối.** Tồn kho hàng hoá tăng 237,8 → 631,7 tỷ và tài sản ngắn hạn khác 26,4 → 768,3 tỷ.
   Trong khi đó dòng ΔHTK trên LCTT 9T chỉ −5,9 tỷ. CFO 9T 1.004,4 tỷ có 373,3 tỷ từ "giảm phải thu", là khoản một lần (§3).

**Điều kiện đổi nhận định:** xem §10. Tóm tắt chiều tốt: BCTC năm 2026 kiểm toán tách được mảng ngoài điện, biên gộp Q3 có cơ sở hợp
đồng, dư nợ cho vay cá nhân giảm rõ. Chiều xấu: Q4/26 biên gộp ngoài điện về ≤5%, có trích lập cho vay, hoặc kiểm toán năm 2026 có
ngoại trừ.

**Pháp lý:** chỉ WARNING. Phạt thuế **101,99 triệu đồng** (QĐ 09/10/2026), trong đó có hành vi "khấu trừ hoá đơn của đơn vị không hoạt
động tại địa chỉ đăng ký". Rủi ro "scandal di cư" ở cho vay cá nhân và M&A với cá nhân (§7).

---

## 1. Kiểm chứng số Mike đã đọc

| Mục | Mike | Bản gốc | Kết quả |
|---|---|---|---|
| DT Q3 | 825,6 (+31,3%) | 825,597 vs 629,038 = +31,25% [Q3 p5, GT] | ✅ |
| GVHB / LN gộp / biên | 477,3 / 348,3 / 42,2% vs 34,7% | 477,269 / 348,328 / 42,19% vs 218,163/629,038 = 34,68% | ✅ |
| DT tài chính | 56,8 | 56,835, toàn bộ là lãi tiền gửi và cho vay [Q3 p16 VI.12] | ✅ |
| CP tài chính / lãi vay | 85,0 / 82,8 | 84,960. Lãi vay trên KQKD là 82,771; thuyết minh VI.13 ghi 84,231 (lệch 1,46 tỷ nội bộ BCTC) | ⚠️ |
| QLDN | 29,8 (x2) | 29,821 vs 14,351 (+108%) | ✅ |
| LNTT / thuế / LNST / mẹ | 288,1 / 24,1 / 263,9 / 245,4 | 288,056 / 24,134 (8,4%) / 263,922 / 245,381 vs 125,377 | ✅ |
| 9T DT / LNST / mẹ | 2.264,5 / 612,6 / 563,3 | 2.264,520 / 612,575 / 563,270 vs 303,927 (+85,3%) | ✅ |
| Tiền + TĐT | 487,9 vs 850,4 | 487,864 vs 850,388 | ✅ |
| HTM ngắn / dài | 724,4 / 246,7 | 724,374 (dự phòng −19,676) / 246,678 | ✅ nhưng **không phải tiền gửi** (§3) |
| Hàng tồn kho / hàng hoá | 763,5 / 631,7 | 763,471 / 631,714 vs 237,769 | ✅ |
| TS ngắn hạn khác (mã 155) | 696,5 | 696,453, Q3 không thuyết minh | ✅ chưa rõ bản chất |
| Phải thu dài hạn khác | 538,0 | 537,986 | ✅ |
| XDCB / liên kết / LTTM | 540,1 / 70,5 / 372,0 | 540,066 / 70,500 / 372,026 vs 156,574 | ✅ |
| Vay | 679,4 + 3.602,6 | 679,444 + 3.602,587 (vay dài hạn 3.109,1 + **trái phiếu 493,4**) [Q3 p14 V.8] | ✅ |
| VCSH / LICKS / mẹ | 3.269,8 / 619,7 / ≈2.650 | 3.269,768 / 619,697 / 2.650,071 | ✅ |
| LCTT 9T | CFO 1.004,4; capex 351,8; góp vốn −1.545,7; vay 1.453,2; trả 906,0; cổ tức 48,6 | khớp [Q3 p7–8] | ✅ |

**Lệch nguồn BQ:** `Revenue_P0` 825,6 và `NP_P0` 245,4 (Q3/26) khớp BCTC. **`BVPS` BQ = 39.024 đ/cp là VCSH GỒM lợi ích cổ đông
không kiểm soát** (3.269,8/83,79). BVPS công ty mẹ đúng là **31.628** (30/09), và **30.728** sau khi trừ cổ tức 900 đ/cp chi ngày 06/11.

## 2. Chất lượng lợi nhuận — tách theo mảng

### 2a. Theo mảng (tỷ đồng)

| Kỳ | DT điện | LN gộp điện (biên) | DT ngoài điện | LN gộp ngoài điện (biên) | Nguồn |
|---|---|---|---|---|---|
| 2025 | 898,3 | 605,1 (67,4%) | Hàng hoá 1.012,1 / dịch vụ 383,5 / khác 9,3 | Hàng hoá 15,3 (**1,5%**) / dịch vụ 173,9 (45,3%) / khác 0,5 | [KT25 PL07] |
| H1/26 | 569,5 | 432,8 (76,0%) | Hàng hoá 656,7 / dịch vụ 224,0 / khác 4,2 | Hàng hoá 29,8 (**4,5%**) / dịch vụ 100,6 (44,9%) / khác 0,2 | [H1 PL07 p53] |
| Q3/25 | 226,2 | 150,3 (66,4%) | 402,8 | 67,8 (16,8%) | [Q3 p16 VI.10–11] |
| **Q3/26** | **223,0** | **174,4 (78,2%)** | **602,6** | **174,0 (28,9%)** | [Q3 p16] |
| 9T/26 | 792,5 | 607,2 (76,6%) | 1.472,0 | 304,7 (20,7%) | H1 + Q3 |

- **"Dịch vụ"** = xử lý chất thải và điện rác của Ngôi Sao Xanh (Bắc Ninh). Hoạt động này được **miễn thuế TNDN** [H1 2.30]. Theo
  địa lý, DT Bắc Ninh 2025 là **1.429,8 tỷ = 62,5% DT hợp nhất** [KT25 PL07b]. ⇒ VCP ngày nay **không còn là "thuỷ điện thuần"**:
  thuỷ điện chỉ chiếm 39% DT 2025 nhưng 76% LN gộp.
- **Q3/26:** LN gộp tăng 130,2 tỷ YoY. Trong đó **điện +24,1** (do giá vốn điện giảm, DT phẳng) và **ngoài điện +106,1**. Q3 không
  tách hàng hoá và dịch vụ (BCTC riêng Q3 cũng không tách được — §Phụ lục B). Giả sử dịch vụ giữ nửa mức H1 (DT 224,0/2 ≈ 112 tỷ, biên 44,9% ⇒ GP ≈ 50,3; ước lượng) và DT khác ≈ 2:
  **DT hàng hoá Q3 ≈ 602,6 − 112 − 2 ≈ 488,6 tỷ (≈ 490, không phải ~450) và GP hàng hoá ≈ 174,0 − 50,3 ≈ 123,7 tỷ, biên ≈ 25%** (ước lượng). Mảng này từng có biên 1,5–4,5%.
  **Đây là con số quan trọng nhất cần giải thích. CV110 không giải thích nó.**
  **Giả thuyết thay thế:** mảng *dịch vụ* tăng mạnh hơn mức nửa-H1 nhờ dự án BCC điện rác Hiệp Hoà (523,2 tỷ góp vốn, §3) bắt đầu ghi doanh thu; khi đó phần GP "vượt thường" thuộc dịch vụ
  (biên 45%, miễn thuế) chứ không phải thương mại phế liệu. Giả thuyết này không loại được bằng BCTC Q3, nhưng không làm biến mất câu hỏi: dịch vụ tăng từ ~112 lên ≥ ~280 tỷ/quý cũng là một bước nhảy chưa được giải trình.
- **DT điện phẳng dù đã mua thêm nhà máy** (Đắk Lô 1-3 mua 11/12/2025; Linh Linh 51% mua 27/03/2026) ⇒ sản lượng của các nhà máy cũ
  giảm. Điều này khớp với Bobby: thuỷ điện toàn quốc 10T/26 khoảng −16%, nền 2025 là năm La Niña. **Giá vốn điện giảm 27,3 tỷ khi tài
  sản tăng** là bất thường. Khấu hao trên LCTT 9T26 là 134,2 tỷ, thấp hơn cả khấu hao TSCĐ hữu hình của riêng H1 (124,4 tỷ [H1 PL02]) cộng Q3; thuyết minh TSCĐ 9T ghi 193,4 + 3,2 = 196,6 tỷ [Q3 p7, p13–14].
  Hai số lệch 62 tỷ. **Cần kiểm chứng** xem có đổi thời gian khấu hao hay không.
- **DT tài chính Q3 56,8 tỷ** (×4 = 227 tỷ/năm). Số dư sinh lãi nhận diện được (tiền tương đương 351,5 + HTM 971 + có thể cả TS ngắn
  hạn khác 696,5) ở lãi suất 4,75–9,1% chỉ cho khoảng **30–45 tỷ/quý (ước lượng)**. Phần vượt **cần kiểm chứng** (lãi phạt, lãi hợp
  đồng BCC HHK?).
  **Thu bằng tiền thì sao?** LCTT 9T dòng 27 "tiền thu lãi cho vay, cổ tức, lợi nhuận được chia" = **21,25 tỷ**, so với DT tài chính 9T = **91,6 tỷ** ⇒ chỉ khoảng 23% thu bằng tiền, **khoảng 77% (70,4 tỷ) chưa thu (dồn tích)** [Q3 p5, p7].
  Chú ý: dòng 27 chưa chắc chứa hết lãi tiền gửi (có thể nằm trong thu hồi HTM, dòng 24); nên 77% là cận trên của phần chưa thu. BCTC riêng 9T: DT tài chính 86,8 tỷ trong 91,6 hợp nhất ⇒ lãi gần như toàn bộ phát sinh ở công ty mẹ, nơi giữ các khoản cho vay.
  Đây là **bằng chứng cho rủi ro số 1** (cho vay cá nhân): lợi nhuận kế toán từ cho vay lớn hơn nhiều so với tiền thực nhận.
- **Chi phí vay** Q3 84,2 tỷ (+48,5%). Dư nợ 4.282 tỷ ⇒ khoảng 7,9%/năm.
- **Thuế suất hiệu dụng 8,4%** (9T: 10,7%; 2025: 11,1%). Mức này **hợp lệ về cơ chế**: điện rác miễn thuế, thuỷ điện 10%, các công ty
  con được miễn 4 năm và giảm 50% trong 9 năm [KT25 2.25, H1 2.30]. Rủi ro: các ưu đãi hết hạn. QĐ phạt thuế cũng chỉ ra công ty đã
  **hạch toán thu nhập tài chính vào thu nhập được ưu đãi** [QĐ p2].
- **LNST thuộc cổ đông thiểu số** Q3 = 18,5 tỷ, 9T = 49,3 tỷ (8%).

### 2b. Lịch sử LNST công ty mẹ (tỷ đồng) [BQ NP_P0 cộng quý; 2024–25 khớp KT25]

2017 130,6 · 2018 235,1 · 2019 220,5 · 2020 45,0 · 2021 68,2 · 2022 408,6 · **2023 113,7** (El Niño) · 2024 306,5 · 2025 441,5 ·
**TTM Q3/26 700,8** (EPS 8.364). TTM tại Q3/24 = 265,7, tại Q3/25 = 411,8 ⇒ **trung vị TTM 3 năm = 411,8**.
Biên độ năm xấu/tốt rất rộng (113,7 → 441,5). Năm El Niño 2023 có ROE khoảng 7% (ước lượng, LN/VCSH đầu kỳ).

## 3. Bảng cân đối và dòng tiền (30/09/2026, tỷ đồng)

**HTM ≠ tiền gửi.** Từ 2026 công ty áp dụng TT 99/2025. BCTC H1 trình bày lại số đầu năm: khoản **"Phải thu về cho vay" 622,4
(ngắn hạn) + 135,0 (dài hạn) được chuyển sang "Đầu tư nắm giữ đến ngày đáo hạn"**. Khoản cọc 266,8 tỷ cho ông Đỗ Hoàng Dương chuyển
sang "Đầu tư góp vốn vào đơn vị khác" (0,7 → 267,5) [H1 PL08 p55]. ⇒ Đọc HTM 971 tỷ như tiền gửi ngân hàng là **sai**.

| Danh mục cho vay 30/06/2026 [H1 PL01 p39] | Lãi suất | Đảm bảo | Số dư |
|---|---|---|---|
| (4) HĐ cho vay "phục vụ hoạt động không trái quy định" (năm 2025: ông Vũ Tuấn Cường) | 7,5–9,1% | Cổ phần của bên thứ ba | **566,6** |
| (6) HĐ cho vay mới 2026, cùng mẫu | 8,5% | Cổ phần của bên thứ ba | **97,4** |
| (5)(7) Cho vay "phục vụ mục đích cá nhân" (SMA) | 11% | **Cổ phiếu VCP** | 30,6 + 20,4 = 51,0 |
| (5) 01/2026/HĐVT/DL13-ĐHD, (3) GKC-DRB/DL13 | 5% | Tín chấp | 84,2 + 4,5 |
| (1) CP Đầu tư và Xây lắp Sông Đà (đã dự phòng 100%) | 9,6% | Tín chấp | 19,7 |
| **Cộng** | | | **823,4** (đầu năm 787,4) |

- **46,8% số cổ phiếu VCP (39,22 triệu cp của bên thứ ba, nhiều khả năng là cổ đông lớn) đang cầm cố cho trái phiếu 500 tỷ của VCP** [KT25 PL04]. Giá giảm mạnh ⇒ rủi ro bổ sung tài sản/bán giải chấp.
- Cổ phiếu VCP làm tài sản đảm bảo cho khoản vay của chính VCP: khi giá VCP giảm thì tài sản đảm bảo giảm cùng lúc với tài sản của
  công ty. Đây là rủi ro vòng.
- Ông Vũ Tuấn Cường từng **cho VCP vay** 173,8 tỷ (01/01/2025, đã trả trong 2025). Sau đó **VCP cho ông vay** 972,7 tỷ trong 2025
  (thu về 288,6) [KT25 PL02, PL04]. KT25 không liệt kê ông là bên liên quan.

| Khoản mục | 30/09/26 | 31/12/25 | Ghi chú |
|---|---|---|---|
| Tiền + TĐT | 487,9 | 850,4 | 30/06 chỉ còn 162,8 [H1] |
| HTM ngắn + dài (ròng) | 951,4 | 778,7 (đã trình bày lại) | Chủ yếu là **cho vay** |
| Phải thu ngắn hạn khác | 74,9 | 125,0 | 30/06: **455,3** |
| **TS ngắn hạn khác (mã 155)** | **696,5** | 0 | Phát sinh trong Q3. Q3 không thuyết minh. **Cần kiểm chứng** |
| Hàng hoá | 631,7 | 237,8 | 30/06 hàng tồn kho đã là 600,3 |
| Phải thu dài hạn khác | 538,0 | 537,4 | 523,2 = góp vốn BCC dự án điện rác Hiệp Hoà với CP ĐT&TM HHK [KT25 TM9] |
| XDCB dở dang | 540,1 | 209,9 | Gồm Thác Ba, Đắk Lô 1/3 [KT25 TM9(1)] |
| Lợi thế thương mại | 372,0 | 156,6 | +250,5 Linh Linh, trừ phân bổ |
| Vay + trái phiếu | 4.282,0 | 3.487,0 | Trái phiếu 500 tỷ, 25/12/2025 → 25/12/2028, lãi 10–10,2%, mục đích mua cổ phần Linh Linh; **đảm bảo bằng 39.223.482 cp VCP (46,8% số cp lưu hành) của bên thứ ba** [KT25 p47 PL04] |
| VCSH mẹ | 2.650,1 | 2.146,8 | Trừ cổ tức 75,4 chi 06/11 ⇒ **2.574,7** (30.728 đ/cp) |

- **Nợ ròng:** chỉ trừ tiền = **3.794 tỷ**; coi cả HTM như tiền = **2.843 tỷ**.
  EBITDA TTM ≈ LNTT 849,8 + lãi vay 266,0 + khấu hao khoảng 220 (TTM, ước lượng: KH 9T26 134,2 trên LCTT + Q4/25 ≈ 85; dùng 220 thay cho 279,5 của năm 2025) = **khoảng 1.336** ⇒ nợ vay/EBITDA **3,2x** (với 279,5 thì 3,1x).
  ICR 9T = (686,0 + 227,7)/227,7 = **4,0x**. Vay ngắn hạn (gồm nợ dài hạn đến hạn) 679,4 tỷ, trong khi tiền 487,9 tỷ.
  Tài sản đảm bảo là toàn bộ tài sản hình thành từ các dự án Cửa Đạt, Xuân Minh, Đắk Lô, Đắk Robaye, Nậm La và quyền đòi nợ
  [KT25 PL04, chi tiết p46–48]. **Việc thế chấp quyền thu tiền EVN theo từng hợp đồng: cần kiểm chứng.**
- **Thương vụ 9T (−1.545,7 tỷ "góp vốn vào đơn vị khác"):** 545,7 tỷ trả cho Linh Linh (51%, mua 27/03/2026) [H1 TM3]. Phần còn lại
  khoảng **1.000 tỷ** không được thuyết minh. Khớp về độ lớn với liên kết 70,5 + TS ngắn hạn khác 696,5 + khoảng 233 chưa định danh
  (ước lượng, phép trừ).
- **Linh Linh:** tài sản thuần 578,8 tỷ, trong đó **phải thu 359,0 (62%)**, TSCĐ 221,1 và tiền 1,6. Giá mua 545,7 tỷ cho 51%
  (295,2) ⇒ **lợi thế thương mại 250,5 tỷ = 85% phần tài sản thuần mua được** [H1 p20]. Bên bán là cá nhân (bà Lương Thị Lợi,
  KT25 TM38). Phải thu của Linh Linh đã thu về sau khi hợp nhất, nhiều khả năng đi vào dòng "giảm phải thu" +373,3 trên LCTT (ước lượng).
- **CFO 9T26 = 1.004,4 tỷ là chất lượng thấp:** 373,3 tỷ đến từ giảm phải thu, là khoản một lần gắn với thương vụ. Phải thu khác
  giảm 455,3 → 74,9 trong Q3, đúng lúc TS ngắn hạn khác tăng 696,5 tỷ. CFO trước biến động vốn lưu động là 885,3 tỷ. Mô hình dùng
  **CFO TTM đã trừ 373,3** (776,7).
- **Không khớp LCTT–BS:** tồn kho tăng 421,8 tỷ (341,7 → 763,5), nhưng ΔHTK trên LCTT chỉ −5,9. Thương vụ Linh Linh không mang theo
  tồn kho. Phải trả người bán chỉ tăng 137,9. ⇒ Phần lớn mức tăng hàng hoá **không đi qua CFO.** Có thể đã được thanh toán bằng bù trừ
  hoặc nằm trong dòng đầu tư. **Cần kiểm chứng**, là câu hỏi số 2 sau biên phế liệu.

## 4. Thuỷ điện — đối chiếu 13 mục "DD cần kiểm" của Bobby

| # | Mục | Kết quả |
|---|---|---|
| 1–2 | Sản lượng, giờ vận hành, thuỷ văn | **Không có số** (BCTC không công bố kWh). Đại diện duy nhất là DT điện Q3 −1,4% dù đã thêm nhà máy ⇒ sản lượng cùng danh mục giảm. Danh mục [H1 PL02 p43] (nguyên giá / giá trị còn lại, tỷ): Cửa Đạt 1.227/305 (97 MW theo brief, Thanh Hoá; **đã khấu hao 75%** ⇒ phần trả nợ trong Pc sắp hết, đúng rủi ro tái đàm phán của Bobby), Xuân Minh 449/308, Bái Thượng 159/95, Nậm La 713/179, Tắt Ngoẵng 199/125, Đăkglun 599/288, Đak Robaye 346/300, Nậm Khoá 3 660/215, điện rác Ngôi Sao Xanh; mua thêm Đắk Lô 1-3 và Linh Linh; đang xây Thác Ba và Đắk Lô 1/3. **Cửa Đạt ở Bắc Trung Bộ, nằm đúng vùng rủi ro tích nước T11–T1 mà Bobby nêu** |
| 3 | Giá bán bình quân, Qc/Qm | Không có số. Khách mua: Công ty Mua bán điện (phải thu 146,1 tỷ) và EVN miền Bắc/Trung/Nam [H1 TM6] |
| 4 | PPA | Có HĐ 06/2012HĐ-NMĐ-Cửa Đạt cùng phụ lục sửa đổi số 11 [KT25 TM9(6)]. **Ngày hết hạn và giá sau trả nợ: cần kiểm chứng** |
| 5 | Pass-through | Phải thu Công ty Mua bán điện 6,6 tỷ chênh lệch tỷ giá năm 2019 vẫn chưa thu [KT25 TM9(6)]. Thuế tài nguyên phải nộp 11,5 tỷ [Q3 V.6]. Khoản hỗ trợ lãi suất sau đầu tư Cửa Đạt 36,7 tỷ (2015–16) đang treo ở NHPT và đã dự phòng [KT25 TM9(4)] |
| 6 | Khấu hao | 2025: 279,5 tỷ. Khấu hao 9T26 lệch giữa LCTT và thuyết minh (§2a) |
| 7 | Nợ vay | 4.282 tỷ, lãi thả nổi theo từng lần giải ngân, kỳ hạn tới 192 tháng [KT25 PL04]. Không có nợ ngoại tệ đáng kể |
| 8 | Phải thu EVN | 227,1 tỷ (30/06) so với 182,1 (đầu năm) [H1 TM6]. Chưa lập dự phòng |
| 9 | Tập trung khách | Điện: 100% EVN. DT ngoài điện lớn hơn DT điện. **Khách hàng phế liệu: chưa có danh tính** |
| 10–12 | Đa mục tiêu, quyền, lưới | Cửa Đạt là công trình thuỷ lợi đa mục tiêu (nhận hỗ trợ lãi suất nhà nước). Thời hạn giấy phép và đất: **cần kiểm chứng** |
| 13 | Cổ tức, FCF năm xấu | FCFE (CFO − capex): 2024 = 383,3; 2025 = 258,5. Cổ tức 2025 bằng tiền **9% = 900 đ/cp = 75,4 tỷ (17% LNST mẹ 2025)**, chi 06/11/2026 [CT]. Năm 2023 (El Niño) CFO vẫn dương [BQ] |

## 5. Cổ đông, cổ phiếu, thanh khoản

- **Số cổ phiếu 83.789.658, không đổi** từ 2022 đến 30/09/2026. Bảng biến động VCSH 9T/26 không có tăng vốn [Q3 p15].
  Chưa thấy ESOP hay trái phiếu chuyển đổi (trái phiếu 500 tỷ là trái phiếu thường).
- **Cổ đông lớn** [KT25 TM41]: CTCP Đầu tư VSD, CTCP DH Holdings, Tổng Công ty Sông Đà. Ông Đỗ Tuấn Anh và bà Phạm Thu Huyền đã thôi
  là cổ đông lớn từ 06/2025. **Tỷ lệ sở hữu, free float, room ngoại: chưa đo** (BCTC không ghi).
- Chủ tịch HĐQT Vũ Ngọc Tú, TGĐ Phạm Văn Minh [KT25 p3]. Thù lao TGĐ 2025: 1,61 tỷ.
- **Thanh khoản [BQ, `calc/px_vcp.csv`]:** giá trị giao dịch trung vị 250 phiên **0,27 tỷ/phiên**, 60 phiên 0,30 tỷ, **20 phiên 3,01 tỷ**
  (tăng vọt sau KQ Q3). σ ngày 1,70%.

| Vị thế | Số phiên thoát (tham gia 10% / 20%, ADV60) | Chiết khấu (σ√(Q/ADV60)) | Tâm sau chiết khấu |
|---|---|---|---|
| 1,0 tỷ | 33 / 17 | 3,1% | 40.273 |
| 0,3 tỷ | 10 / 5 | 1,7% | 40.855 |
| 0,1 tỷ | 3,3 / 1,7 | 1,0% | 41.153 |

⇒ Thanh khoản 20 phiên gần nhất là bất thường. Theo nền 60–250 phiên, **vị thế thực tế nên ≤ 0,3 tỷ**.

## 6. Bối cảnh ngành (Bobby, đọc mù — chỉ để tham chiếu)

Nhãn 12 tháng: **CYCLICAL 0,55** / ADMIN_GATED 0,35. Pha hiện tại: khối lượng thuỷ điện **đi từ đỉnh 2025 xuống đáy mùa khô 2027**.
El Niño 2026–27 có xác suất mạnh đến rất mạnh 60–65%. Khung giá PPA 0–1.110 đ/kWh bị đóng băng. Giá bán lẻ giảm 2% từ 01/11/2026
⇒ biên EVN bị ép. Rủi ro tái đàm phán PPA sau khi trả hết nợ. ⇒ Kịch bản bear dùng LNST mẹ năm 2024 và không dùng TTM.

## 7. Pháp lý và quản trị — chỉ WARNING

- **Phạt thuế [QĐ]:** tổng truy thu, phạt và chậm nộp **101.994.544 đ**. Hành vi: (i) kê khai khấu trừ và hạch toán chi phí từ **hoá
  đơn của đơn vị không hoạt động tại địa chỉ đăng ký**; (ii) chưa phân bổ giảm VAT đầu vào cho doanh thu không chịu thuế; (iii) chưa
  phân bổ lãi vay cho XDCB; (iv) hạch toán thu nhập tài chính vào thu nhập được ưu đãi; (v) lập chậm 4 hoá đơn năm 2026. Tình tiết
  tăng nặng: không có. **Tác động tài chính không đáng kể**. Hành vi (i) là dấu hiệu quản trị hoá đơn cần theo dõi ở mảng thương mại
  phế liệu, nơi rủi ro hoá đơn đầu vào cao nhất. Đây là suy luận, chưa có bằng chứng liên hệ.
- **Kiểm toán:** KT25 chấp nhận toàn phần, không có đoạn nhấn mạnh. H1/26 soát xét chấp nhận toàn phần (AASC). Q3 chưa soát xét.
- **Rủi ro "scandal di cư" (đánh giá, chưa có vụ việc):** dòng vốn lớn đi tới cá nhân (cho vay, đặt cọc, mua cổ phần) với tài sản đảm
  bảo khó định giá. Thương vụ Linh Linh có lợi thế thương mại 85% phần tài sản thuần mua được. Mảng thương mại có biên tăng đột biến.
  Nếu xảy ra sự kiện pháp lý, kênh lan truyền có thể là: (a) trích lập cho vay; (b) huỷ hoặc điều chỉnh hồi tố doanh thu thương mại;
  (c) tranh chấp thương vụ M&A. Chưa thấy CBTT về khởi tố, thanh tra chứng khoán hay đổi kiểm toán.
- **Cảnh báo kiểm soát nội bộ (chỉ WARNING, vòng 2):** (a) BCTC hợp nhất Q3/26 do **cùng một người, Nguyễn Viết Hoàng, ký cả "Người lập biểu" lẫn "Kế toán trưởng"** [Q3 p8]
  (BCTC riêng Q3 cùng kỳ có hai người khác nhau: người lập biểu Vương Hoàng Bảo Long, kế toán trưởng Nguyễn Viết Hoàng [riêng p4–5]). (b) Báo cáo bộ phận H1/26 (đã soát xét) ghi mảng **"hàng hoá" có tài sản bộ phận = 0 và nợ bộ phận = 0**
  dù DT hàng hoá H1 656,7 tỷ và **hàng tồn kho 30/06 là 600,3 tỷ** [H1 PL07 p53; H1 BS] ⇒ củng cố câu hỏi số 2 ở §3 (hàng hoá tăng không đi qua CFO và không nằm trong tài sản bộ phận). Cả hai chưa có bằng chứng sai phạm.
- **Không đưa yếu tố pháp lý vào base.** Rủi ro tín dụng cho vay cá nhân là rủi ro cụ thể quan sát được và nằm trong kịch bản bear (§8).

## 8. Định giá — mù giá thị trường

**Phương pháp:** giá trị vốn chủ công ty mẹ = N × (1 − g/ROE)/(r − g) theo 3 kịch bản LNST mẹ (N). ROE = N / B0.
Tương đương **V = B0 + (N − r·B0)/(r − g)** (đã kiểm: base 2.574,7 + (441,5 − 0,135 × 2.574,7)/0,115 = 3.391,4 tỷ = 40.475 đ/cp).
B0 = VCSH mẹ 30/09 trừ cổ tức đã chốt = **2.574,7 tỷ (30.728 đ/cp)**. Tỷ lệ tái đầu tư bị chặn trong [0; 0,8].
- **r = 13,5%.** Neo 13,5% ứng với lãi huy động 12T hiệu dụng 7,40% (`effective_deposit_rate('2026-11-12')` = CCTG 12M ngày 02/11;
  Big-4 6,8%). Mức này bằng điểm neo 03/11 ⇒ Δ = 0, r giữ nguyên. β = 1 là giả định.
- **g = 2%** (ước lượng): khung giá đóng băng, Pc giảm sau trả nợ, bù lại bằng công suất mới. Cách đặt này thấp hơn lạm phát
  (CPI 5,09%, snapshot).
- **Cách xử lý tài sản/thương vụ mới 2026 — đây là GIẢ ĐỊNH, không phải NPV = 0 hiển nhiên.** Trong công thức trên, N **cố định = LNST mẹ 2025 (441,5)**;
  tài sản mới 2026 (Thác Ba, Đắk Lô 1/3 — XDCB 540,1; Linh Linh — giá mua kể cả lợi thế thương mại; BCC HHK 523,2; TS ngắn hạn khác 696,5) vào B0 theo **giá sổ**, và chỉ được tính đủ giá sổ
  **nếu N đã chứa r × giá trị sổ của chúng** (tức chúng sinh lời đúng bằng r). N-2025 chưa có Đắk Lô 1-3 cả năm và chưa có Linh Linh ⇒ điều đó **chưa chắc đúng (ước lượng)**.
  - **Cách đọc A (HEADLINE, giữ nguyên vòng 1):** N-2025 + B0 sau cổ tức (2.574,7). Tâm 41.560 / 40.273.
  - **Cách đọc B:** B cuối 2025 (2.146,8) cho phần sinh ra N-2025; **ΔB = 427,9 tỷ** (2.574,7 − 2.146,8) cộng theo giá sổ, tức coi tài sản 2026 là NPV = 0 thật và N-2025 chưa chứa phần lãi của chúng.
    Base = 2.146,8 + (441,5 − 0,135 × 2.146,8)/0,115 + 427,9 = 3.893,6 tỷ = **46.469 đ/cp**; bear 27.663; bull 73.379; **tâm 47.555 (sau chiết khấu 1 tỷ ≈ 46.081)**.
  - **Hai hướng bất định của tâm:** xuống ≈ 36.900 (bull trừ hai phần chưa giải thích, §0) và lên ≈ 46.100 (cách đọc B): vùng khoảng ±3–6k đ/cp quanh 40.273. **Tôi giữ A làm headline** vì B thưởng cho 1.000 tỷ góp vốn/cho vay chưa thuyết minh (§3) đúng ở chỗ rủi ro nhất.

| Kịch bản | w | N (tỷ) | Cơ sở dữ liệu | Giá trị đ/cp |
|---|---|---|---|---|
| Bear | 0,30 | 306,5 − **lỗ cho vay 401,9** | N = LNST mẹ 2024 kiểm toán (năm thuỷ văn thường, ít nhà máy hơn). El Niño 2026–27 (Bobby F2/F8/F10). Lỗ = 50% × **803,7 tỷ** = 664,0 (đảm bảo bằng cổ phần bên thứ ba, PL01 (4)(6)) + 51,0 (cầm cố chính cổ phiếu VCP, (5)(7)) + 88,7 (tín chấp 5%, (5)(3)); **trừ** 19,7 Sông Đà (đã dự phòng 100%) [H1 PL01]. Tỷ lệ 50% là ước lượng. Vòng 1 chỉ lấy 664,0 (lỗ 332,0, bear 22.502) và bỏ hai phần rủi ro hơn (tín chấp, cầm cố cổ phiếu VCP) mà không giải thích | **21.669** |
| Base | 0,45 | 441,5 | LNST mẹ 2025 kiểm toán, ROE 17,1%. Gần trung vị TTM 3 năm (411,8). Năm mưa nhiều bù trừ với việc chưa có đủ nhà máy mới (ước lượng) | **40.475** |
| Bull | 0,25 | 700,8 | TTM Q4/25–Q3/26. Giả định LN gộp ngoài điện của Q3 lặp lại, **kể cả phần biên vượt thường (~75 tỷ thuộc mẹ) và lãi dồn tích chưa thu (~58 tỷ)** — độ nhạy ở §0 | **67.385** |
| **Tâm** | | | | **41.560** → **40.273** sau chiết khấu thanh khoản (1 tỷ) |

**Độ nhạy (tâm, đ/cp)** [model_out.json]:

| Biến | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| Lãi huy động, β = 1 | 45.656 (+9,9%) | 43.515 (+4,7%) | 39.769 (−4,3%) | 38.120 (−8,3%) |
| Lãi huy động, β = 0,5 | 43.515 | 42.516 | 40.646 | 39.769 |

g 0% / 1% / 3% / 4% ⇒ 39.742 / 40.579 / 42.729 / 44.144. Lỗ cho vay ở bear 0% ⇒ 42.999; 50% (headline) ⇒ 41.560; 100% ⇒ 40.122.
Trọng số kịch bản và biến thể B: §0 và đầu §8.

**Hai nền giá trị + C4 + D2 (CHỈ HIỂN THỊ, không đổi tâm)**

| Nền | Cách tính | đ/cp |
|---|---|---|
| V_ngắn | Trung vị LNST mẹ TTM 3 năm 411,8 × (1 − 0,02/16,0%)/(r − g) | **37.392** |
| V_dài | FCFE mẹ = 0,92 × trung bình (CFO − capex) {2024: 383,3; 2025: 258,5; TTM: 340,8 (CFO đã trừ 373,3 một lần)} = 301,3 → /(r − g) | **31.272** |
| D = \|ln(V_ngắn/V_dài)\| | 0,179 < ln2 | Không có cờ phân kỳ |
| V theo C4 = CFO3 − min(capex 199,7; KH 281,0) | Capex < KH ⇒ bằng V_dài. *Chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi* | 31.272 |
| V theo D2 = CFO3 − 1,33% × DT | Capex/DT trung vị của 15 mã thuỷ điện 2023–25 [BQ, `calc/peer_capex_raw.csv`]. Thiên cao vì DT của VCP gồm thương mại có capex thấp. *Chưa qua tiêu chí khoá trước (0/9 nền qua; D2 đạt T1–T4, trượt BH-FDR ở 3/6 tháng, chỉ sống ở 12 tháng), chỉ theo dõi* | 47.374 |

Hai nền thấp hơn tâm (37,4k và 31,3k so với 41,6k) vì tâm có trọng số bull 25% dựa trên TTM. **Dòng tiền thật (V_dài 31,3k) gần
bằng giá trị sổ sách** (30,7k). Đây là lý do thứ hai để không nâng tâm.

**Kiểm chéo bội số tại giá 37.900:** P/E TTM mẹ 4,5x · P/E trên N base 7,2x · P/B mẹ sau cổ tức 1,23x.
Tại 31.700: 3,8x / 6,0x / 1,03x.

**Comp thuỷ điện (đo [BQ] `tav2_bq.ticker` ngày 11/11/2026, 13 mã có dữ liệu trong rổ `calc/peer_capex_raw.csv`; HNA và TTE không có dòng ngày 11/11; `calc/peer_multiples_20261111.csv`):**

| Bội số | Trung vị 13 mã | Min | Max | VCP (BQ) |
|---|---|---|---|---|
| P/E | **9,3x** | GHC 5,8x | HJS 12,7x | **4,5x** |
| EV/EBITDA | **6,7x** | TBC 4,7x | TMP 7,8x | 5,6x |
| P/B (BVPS BQ gồm cổ đông không kiểm soát) | 2,0x | NED 0,46x | DRL 3,2x | 0,97x |
| PE_MA5Y (P/E trung bình 5 năm) | 11,3x | SJD 7,2x | NED 21,7x | 10,1x |

VCP có P/E thấp hơn trung vị ngành khoảng 51% (và thấp hơn cả mã rẻ nhất, GHC 5,8x); EV/EBITDA thấp hơn khoảng 15%. P/E TTM của VCP bị kéo xuống vì LNST TTM 700,8 gồm Q3 chưa giải thích; trên N base (441,5) P/E là 7,2x, còn thấp hơn trung vị 23%.
EV/EBITDA ít chênh vì VCP nợ nặng (nợ vay/EBITDA 3,2x) — phần thấp hơn là phần vốn chủ bị chiết khấu.
**VCP có xứng đáng bị chiết khấu so với ngành không?** Có một phần: (i) quản trị và phân bổ vốn (cho vay cá nhân 823,4 tỷ, lãi 77% chưa thu bằng tiền, §7); (ii) cơ cấu doanh thu: thuỷ điện chỉ 39% DT 2025,
phần còn lại là thương mại phế liệu biên mỏng và điện rác; thị trường chưa có tiền lệ để định giá biên 25% của Q3; (iii) UPCoM, thanh khoản 0,27 tỷ/phiên (§5); (iv) kiểm soát nội bộ (§7). Một phần chiết khấu có thể quá mức nếu Q4 xác nhận biên Q3.
Comp **chỉ kiểm chéo, không đổi tâm**: tâm 40.273 tương ứng P/E TTM 4,8x, vẫn thấp hơn trung vị ngành nhiều.

## 9. Vị thế và lợi thế cạnh tranh (5F tầng b) — lần đầu

`data/moat_tags.csv` chưa có VCP, `kb/projects/` chưa có DD VCP ⇒ làm lần đầu.

- **Loại hình:** tập đoàn hỗn hợp gồm (a) danh mục thuỷ điện vừa và nhỏ ở miền Bắc, Bắc Trung Bộ, Tây Nguyên, bán 100% cho EVN;
  (b) nhượng quyền xử lý chất thải và điện rác Bắc Ninh; (c) thương mại phế liệu; (d) **hoạt động tài chính (cho vay, M&A)**.
- **moat_tier = NARROW (chỉ có cơ chế giấy phép), về định lượng tương đương NONE** (cả ROIC_Min5Y 7,8%, ROIC5Y 12,2%, ROE_Min3Y 8,4% đều < Ke 13,5%); moat_type = *quyền khai thác tài nguyên nước và vị trí đập (giấy phép), nhượng quyền xử lý rác địa phương*.
  - Bằng chứng định lượng: **ROIC_Min5Y 7,8%, ROIC5Y 12,2%, ROE_Min3Y 8,4% — đều < Ke 13,5%** [BQ] ⇒ không có lợi nhuận siêu ngạch
    xuyên chu kỳ (điều kiện i trượt). Biên gộp điện 67–78% là cấu trúc tài sản nặng vốn, không phải hào. Giá bán do khung EVN/BCT
    quyết. Có một người mua duy nhất.
  - Đồng hồ cắt hào (lực thứ 6): hết PPA và tái đàm phán Pc sau khi trả nợ (Bobby §3), khung giá đóng băng, tiền cấp quyền khai thác
    nước, ưu đãi thuế hết hạn.
  - Thương mại phế liệu: NONE (biên 1,5–4,5% trong 2025–H1/26).
- **Tham số moat thêm vào mô hình: KHÔNG** (NARROW ⇒ không thưởng, không trừ, theo luật 08/11).
  ⚠️ Base có ROE 17,1% > Ke vĩnh viễn, tức **ngầm thưởng**. Nếu ROE về Ke ở mọi kịch bản thì **tâm = 29.289** (−30%). Đây là thông
  tin rủi ro, không đổi headline.
- **Rủi ro số 1:** quản trị và phân bổ vốn (cho vay cá nhân, M&A với cá nhân), không phải thuỷ văn.
- **Đề xuất dòng `moat_tags.csv`** (human-curated, KHÔNG tự sửa): `VCP,NARROW,water_license+local_waste_concession,2026-11-12,"NARROW chi o co che giay phep, dinh luong ~NONE (ROIC_Min5Y 7.8%/ROIC5Y 12.2%/ROE_Min3Y 8.4% < Ke); PPA/tariff clock; capital allocation risk"`.

## 10. Mốc khoá trước và điều kiện đổi nhận định (cả hai chiều)

| Mốc | Ngày | Nâng (tâm lên, nghiêng bull) nếu | Hạ (tâm xuống, nghiêng bear) nếu |
|---|---|---|---|
| BCTC Q4/2026 | ≤ 30/01/2027 | LN gộp ngoài điện Q4 ≥ 100 tỷ **và** có thuyết minh khách hàng/hợp đồng phế liệu | LN gộp ngoài điện ≤ 5% DT mảng; hoặc hàng hoá tồn kho > 600 tỷ mà không bán được |
| BCTC 2026 kiểm toán | ≤ 31/03/2027 | Chấp nhận toàn phần; tách được TS ngắn hạn khác 696,5 thành tài sản sinh lời; dư nợ cho vay cá nhân ≤ 400 tỷ | Ngoại trừ hoặc nhấn mạnh; trích lập cho vay; hồi tố DT thương mại ⇒ bear (21,7k) thành trung tâm |
| Thuỷ văn Bắc Trung Bộ | 31/12/2026 | Mực nước hồ ≥ MNDBT (điều kiện (i) của Bobby) | F8 hoặc F10 của Bobby đúng ⇒ N bear |
| Lãi huy động 12T | Liên tục | −50bp ⇒ +4,7% | +50bp ⇒ −4,3% |
| Giá | — | ≤ 34.232 (0,85 × tâm sau chiết khấu) ⇒ có biên an toàn | ≥ 55.000 (ước lượng, gần bull) ⇒ đắt so với base |

## 11. Bối cảnh vĩ mô — chỉ hiển thị (`macro_snapshot_20261112.md`, dòng `ok`)

Lãi suất tái cấp vốn 4,50% · liên ngân hàng 3M 6,39% (Δ3T −1,36pp) · CPI 5,09% YoY · GDP Q3 9,95% · sản xuất công nghiệp +15,0% YoY
(10/2026). Phụ tải điện là nền cấu trúc (Bobby). Lạm phát 5% so với giá PPA đóng băng ⇒ giá thực giảm. Snapshot không đổi giá trị.

## Phụ lục A — Nguồn từng số

- KQKD, BS, LCTT Q3: [Q3 p3–8]. Thuyết minh mảng Q3: [Q3 p16 VI.10–14]. TSCĐ: [Q3 p13]. Vay: [Q3 p14 V.8]. VCSH: [Q3 p15].
- Mảng 2025: [KT25 p53–54 PL07]. Mảng H1/26: [H1 p53 PL07]. Danh mục cho vay: [KT25 p40–41 PL02], [H1 p39 PL01].
- Linh Linh: [KT25 p36 TM38], [H1 p19–20 TM3]. Đắk Lô 1-3: [KT25 p19–20 TM3]. Phải thu dài hạn: [KT25 p23 TM9b].
- Trình bày lại theo TT 99: [H1 p55 PL08]. Ý kiến kiểm toán: [KT25 p4], [H1 p4]. LCTT 2025: [KT25 p8].
- Thuế suất ưu đãi: [KT25 p18 2.25], [H1 p19 2.30]. Phạt thuế: [QĐ p1–3]. Cổ tức: [CT p1].
- LNST lịch sử, ROIC/ROE, giá, khối lượng: [BQ] (`calc/px_vcp.csv`, truy vấn trong phiên 12/11).
- Mô hình: `calc/model_out.json` (**vòng 2** md5 assumptions `22d79a2869f2f66a84d332c3e85069b7`, model `198b5fad0d76ce8fadb3d400c3c784a5`; vòng 1 là `5e4861d5cb480d0d18e13e59d218e76d` / `9c53a3d4e980d8d036c9b24a2956a7d8`).
- Vòng 2: LCTT 9T dòng 27 và DT tài chính 9T [Q3 p7, p5]; chữ ký [Q3 p8]; báo cáo bộ phận H1 [H1 PL07 p53]; sử dụng tiền trái phiếu [`src/bc_tp_vn.pdf` trang 6–7]; BCTC riêng Q3 [`src/bctc_rieng_q3_2026.pdf` trang 4–5]; comp [BQ `calc/peer_multiples_20261111.csv`].

## Phụ lục B — Chưa làm / giới hạn

- Không có sản lượng kWh, giá bán bình quân, Qc/Qm, ngày hết PPA, thời hạn giấy phép (BCTC không công bố; chưa đọc BCTN).
- Chưa tách Q3 thành hàng hoá và dịch vụ (BCTC riêng Q3 đã đọc: DT riêng Q3 170,3 tỷ, GVHB 22,5 tỷ, DT tài chính 53,1 tỷ, LNST riêng 9T 255,4 tỷ — không tách được hàng hoá/dịch vụ; nhiều khả năng hai mảng này nằm ở công ty con, suy luận). Chưa có danh tính khách hàng phế liệu. Bản chất TS ngắn hạn khác 696,5 và khoảng 1.000 tỷ
  "góp vốn" Q3 chưa rõ. Chưa đối chiếu LCTT H1.
- **Báo cáo sử dụng tiền trái phiếu: ĐÃ đọc, khớp.** Toàn bộ **500 tỷ VCP12501** đã dùng để mua 816.000 cp (51%) Linh Linh trong 01/01–30/06/2026 (lũy kế 500.000.000.000 đ; kiểm toán AASC chấp nhận) [`bc_tp_vn.pdf` tr. 6–7]. Giá mua 545,7 tỷ ⇒ phần chênh 45,7 tỷ từ nguồn khác.
- Chưa đọc BCTC HN Q3/2025 (đã tải `src/bao-cao-tai-chinh-hop-nhat-quy-iii-2025.html`, là trang HTML). Số Q3/25 lấy từ cột so sánh
  của Q3/26.
- Tỷ lệ sở hữu cổ đông lớn, free float, room ngoại: chưa đo. Comp bội số ngành: đã đo vòng 2 (§8).
- Tỷ lệ lỗ 50% ở bear, g = 2%, thuế 20% và biên chuẩn 4,5% của phần hàng hoá, và trọng số kịch bản đều là ước lượng.

## Phụ lục E — Phản biện fundamental-skeptic

**Skeptic vòng 1 = REFUTED mức văn bản (confidence medium); 10 thay đổi nội dung đã áp (brief ghi 9):**
1. NPV = 0 viết lại đúng cơ chế mô hình; thêm cách đọc B (tâm 47.555) và vùng bất định (§8).
2. Bear đổi rổ lỗ cho vay 664,0 → 803,7 tỷ (lỗ 332,0 → 401,9): bear 22.502 → 21.669, tâm 41.810 → 41.560.
3. Lãi cho vay thực thu: 21,25 vs 91,6 tỷ ⇒ ~77% dồn tích (§2a, §0).
4. Bảng độ nhạy bull (a)(b) và trọng số (§0): giá 37.900 chuyển từ dưới tâm sang trên tâm ở (b).
5. Comp ngành đo bằng BQ (§8): P/E trung vị 9,3x, EV/EBITDA 6,7x (13 mã).
6. DT hàng hoá Q3 sửa ≈ 489–490 tỷ, biên ≈ 25%; thêm giả thuyết dịch vụ/BCC Hiệp Hoà (§2a).
7. Báo cáo sử dụng tiền trái phiếu và BCTC riêng Q3 đã đọc (Phụ lục B).
8. §7 thêm hai cảnh báo (cùng người ký hai chức danh; hàng hoá tài sản bộ phận = 0 vs tồn kho 600,3).
9. Moat ghi "NARROW (chỉ cơ chế giấy phép), định lượng ≈ NONE" (§9).
10. Khấu hao TTM ≈ 220 ⇒ EBITDA ≈ 1.336, nợ vay/EBITDA 3,2x; C4 không đổi (31.272).
**Hai hướng bất định của tâm (sau chiết khấu 40.273):** xuống ≈ 36.900 (bull trừ phần biên vượt thường và lãi dồn tích; hoặc trọng số bull thấp hơn) và lên ≈ 46.100 (tài sản 2026 NPV = 0 thật, cách đọc B).
Skeptic vòng 2: chưa chạy. Mike ghi sổ `dd_price_zones.json` SAU skeptic với `assumptions_md5 = 22d79a2869f2f66a84d332c3e85069b7`
(`calc/assumptions.json`; vòng 1 là `5e4861d5cb480d0d18e13e59d218e76d`, không dùng nữa).
