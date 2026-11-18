# DD — DBC (CTCP Tập đoàn Dabaco Việt Nam, HOSE) · 2026-11-18 · job `Taylor_20261118_041902` · VÒNG 2 (đã áp đính chính của fundamental-skeptic vòng 1; vòng 1 = `REPORT_v1.md`, job `Taylor_20261118_035743`)

> Chỉ nghiên cứu. Không đặt lệnh, không sửa production, không gửi email. Đơn vị: tỷ đồng, trừ khi ghi khác.
> Nguồn chính: BCTC hợp nhất Q3/2026 (`src/q3_hopnhat.pdf`, ký 21/10/2026); BCTC công ty mẹ Q3/2026 (`src/q3_congtyme.pdf`);
> BCTC hợp nhất bán niên 2026 do EY soát xét (`src/h1_d.pdf`, bản EN; `h1_a` = riêng EN, `h1_b`/`h1_c` = bản VN; báo cáo soát xét ký 26/08/2026).
> Mô hình: `model/calc.py` + `model/assumptions_DBC_20261118.json`, output `model/calc_output.txt`.
> **assumptions_md5 vòng 2 = `708441c3c673573b354d245a2428b0dc`** (vòng 1 = `511073ce713239e5cf7d242491d07922`, lưu ở `model/assumptions_DBC_20261118_v1.json`, `calc_v1.py`, `calc_output_v1.txt`). Thay đổi giả định ghi ở Phụ lục E.
> Tôi chưa có BCTC kiểm toán năm 2025. Số năm 2023–2025 lấy từ BQ `ticker_financial`, đã đối chiếu từng điểm ở §1.

## 0. Kết luận

- **Giá trị nội tại, tâm = 18.414 đ/cp** (sau chiết khấu thanh khoản 2%; trước chiết khấu 18.789). **Vùng [13.239; 29.195]** (kịch bản xấu → tốt, trọng số 25/50/25).
  r = 13,5%, g = 5%, **LNST chuẩn hoá chu kỳ 843,8 tỷ** (EPS 1.958 đ; trung bình 15 quý lịch Q1/23–Q3/26, mỗi quý tính một lần). Ở tâm, P/E 9,4 và P/B 0,91.
- **So giá (bước cuối):** giá 16.950 đ ngày 17/11/2026 (BQ `ticker`) bằng **0,92 × tâm**.
  **Kết luận phụ thuộc cách chuẩn hoá LNST: giá/tâm dao động 0,78–0,97** (bảng §2b). Mốc 0,85 × tâm (15.652) **không** thoả ở cách chuẩn hoá chính;
  chỉ thoả ở cách đọc lạc quan nhất (trung vị 12 TTM = 1.083 tỷ, giá/tâm 0,78).
  Giá cao hơn giá trị kịch bản **cơ sở** (15.929 trước chiết khấu, 15.610 sau) và cao hơn V_ngắn (11.129, toàn vốn cùng ROE). Giá nằm dưới tâm chỉ vì kịch bản tốt (trọng số 25%) kéo tâm lên.
- **Không còn cờ phân kỳ V_ngắn/V_dài.** Tính cả 573,7 tỷ tài sản thuê tài chính tăng thêm 9T/26 vào đầu tư, **FCFE 3 năm = −45 tỷ/năm (≤ 0)**, nên theo luật chỉ giữ V_ngắn và giải thích dòng tiền âm (§4). Dòng tiền âm không chứng minh được "đầu tư tăng trưởng" (§6d).
- **Q3/26 xấu:**
  - Doanh thu thuần +37,4% YoY (5.138 tỷ), LN gộp −9,9% (587,7 tỷ), biên gộp 11,4% so với 17,4%. LNST 200,2 tỷ (−41,6%). 9T/26: LNST 863,3 tỷ (−36,4%).
  - Mảng heo/trại kéo xuống (LN gộp ngoài công ty mẹ −100 tỷ). Giá heo Q3 **không** thấp hơn Q3/25 (PPI chăn nuôi lợn Q3 +0,7% YoY, Bobby §2a), nên nguyên nhân gần nhất là **chi phí đầu vào đỉnh Q3** hơn là giá heo (§3). TACN và dầu thực vật kéo lên.
- **Q4/26 nhiều khả năng còn yếu:** ước lượng LNST Q4/26 −50…+120 tỷ (Q4/25: 148,6 ở giá heo tương đương ~48–50k). Cả năm 2026 ước lượng 813–983 tỷ.
  Thị trường đã thấy hướng này; phần chưa biết là **độ sâu** và **trích lập tài sản sinh học**: ước biên độ **94–188 tỷ** (5–10% của 1.877,7; §3).
- **Bảng cân đối:** nợ ròng thật 3.285 tỷ (vay + thuê TC 7.622 − tiền và HTM 4.338), ND/E 0,38 (đầu năm 0,44). CFO 9T 1.518 tỷ nhưng **CFO cốt lõi ~1.020–1.307 tỷ** (bỏ giải phóng tồn kho 499, và/hoặc cộng lại trả trước người bán tăng 288; §4).
- **WARNING có số (mới):** **phải thu người lao động 237,1 tỷ tại 30/9 (208,8 đầu năm) = 27% LNST 9T**, phần lớn là tạm ứng giải phóng mặt bằng (§7). Không có WARNING pháp lý/kiểm toán khác.
  Giám đốc tài chính đã mua 2.000.000 cp (báo cáo 14/10/2026).
- **Moat: NARROW mỏng** (NONE cũng đứng được; ROE_Min5Y 0,5%, ROIC_Min5Y 2,3%). Không thưởng tham số moat.
- **Điểm yếu lớn nhất của báo cáo** (§10): (1) lựa chọn chuẩn hoá LNST (thay đổi tâm 17.386–21.617); (2) kịch bản xấu (ROE 9,0%) hầu như không thấp hơn base mới (9,7%) nên phân phối lệch lên;
  (3) cách đọc XDCB: coi dự án mới là NPV = 0, nếu ROE cùng mức thì cơ sở chỉ còn 11.129 (−30%).

## 1. Đối chiếu BQ với BCTC gốc

| Mục | BCTC | BQ `ticker_financial` (2026-10-21) | Lệch |
|---|---|---|---|
| LNST Q3/26 | 200,17 | NP_P0 200,17 | khớp |
| LNST H1/26 | 663,16 (soát xét) | Q1 374,04 + Q2 289,12 = 663,16 | khớp |
| LNST 9T/25 | 1.358,19 | 508,26 + 506,97 + 342,96 = 1.358,19 | khớp |
| Doanh thu Q3/26 | thuần 5.138,0; gộp 5.317,8 | Revenue_P0 5.317,8 | **BQ là doanh thu GỘP** (trước giảm trừ 179,8) |
| CFO Q3/26 | 9T 1.517,9 − H1 329,1 = 1.188,8 | CF_OA_P0 1.188,8 | khớp |
| CFO Q2/26 | H1 329,1 − Q1 (BQ 744,4) = −415,3 | CF_OA_P0 −841,8 | **lệch 426**; có thể Q1 đã được trình bày lại. Tôi dùng BCTC |
| Capex Q3/26 | 9T 1.106,0 − H1 767,6 = 338,4 | CF_Invest_P0 −338,4 | khớp: CF_Invest_P0 là capex, không gồm tiền gửi |
| Vốn chủ Q3/26 | 8.721,4 | BVPS × OShares = 8.721,4 | khớp. Một vài quý cũ (Q2/25, Q1/26) có BVPS × OShares lệch, nên không dùng |
| GPM_P0 | — | 14,8% (TTM) | là TTM, không phải quý (đúng bẫy skill) |
| Revenue_P0 Q3/25 | 3.919,5 | 5.021,6 | **lệch +1.102**: doanh thu 2025 trong BQ chia quý sai |
| Revenue_P0 Q4/25 | — | 2.350,5 | cùng lỗi chia quý; không dùng doanh thu quý 2025 từ BQ |
| Capex H1/26 | 767,6 | 279,9 + 442,0 = 721,9 | **lệch −45,7** (BQ chưa gồm phần BCTC tính) |
| Vốn chủ dòng 2022-01-27 | — | BVPS × OShares = 2.348 | lỗi số cổ phiếu ở dòng này; không dùng |

(Bốn dòng cuối đã chạy lại `bq query` trong vòng 2; không ảnh hưởng mô hình vì mô hình dùng LNST quý, vốn chủ Q3/26 và CFO/capex đã đối chiếu BCTC.)

## 2. Chất lượng lợi nhuận

### 2a. Q3 và 9T so với cùng kỳ (hợp nhất)

| | Q3/26 | Q3/25 | Δ | 9T/26 | 9T/25 | Δ |
|---|---|---|---|---|---|---|
| DT thuần | 5.138,0 | 3.739,2 | +37,4% | 13.515,0 | 11.168,6 | +21,0% |
| LN gộp | 587,7 | 652,2 | −9,9% | 1.932,1 | 2.294,4 | −15,8% |
| Biên gộp | 11,4% | 17,4% | −6,0pp | 14,3% | 20,5% | −6,2pp |
| CP bán hàng + QLDN | 291,9 | 244,6 | +19,3% | 824,1 | 725,3 | +13,6% |
| DT tài chính | 43,2 | 17,0 | | 89,4 (lãi tiền gửi 87,5) | 56,9 | |
| CP lãi vay | 100,4 | 62,5 | +61% | 247,3 | 196,9 | +25,6% |
| Lãi/lỗ liên kết | 0 | 0 | | 1,4 | −2,6 | |
| Lợi nhuận khác | 4,4 | 3,6 | | 18,3 | 13,0 | |
| LNTT | 241,3 | 365,6 | −34,0% | 967,7 | 1.438,7 | −32,7% |
| LNST | 200,2 | 343,0 | −41,6% | 863,3 | 1.358,2 | −36,4% |

Cơ cấu doanh thu 9T: thành phẩm 13.456,0; nguyên liệu và hàng hoá 505,2; **BĐS và xây dựng 98,6** (giá vốn 91,0, nên LN gộp BĐS chỉ 7,6). Mảng BĐS không thổi phồng lợi nhuận.

**Tách mảng.** BCTC quý không có số bộ phận. Lấy từ BCTC soát xét bán niên (TM 34):

| H1 (tỷ) | TACN + nguyên liệu | BĐS/xây dựng/khác | Giống & chế biến thực phẩm | Loại trừ | Tổng |
|---|---|---|---|---|---|
| DT ngoài H1/26 | 3.731,1 | 88,1 | 4.557,8 | — | 8.377,0 |
| DT ngoài H1/25 | 3.119,8 | 17,9 | 4.291,8 | — | 7.429,4 |
| DT nội bộ H1/26 | 3.656,6 | 116,1 | 209,9 | −3.982,5 | — |
| LNTT H1/26 | 1.046,7 | 16,3 | 427,4 | **−763,9** | 726,4 |
| LNTT H1/25 | 732,7 | 1,6 | 797,9 | −459,1 | 1.073,1 |

- ⚠️ **Không đọc LNTT bộ phận như lợi nhuận thật của mảng.** Mảng TACN chứa công ty mẹ, và LNTT của nó gồm cổ tức nhận từ công ty con: DT tài chính công ty mẹ 9T là 888,5 tỷ, phần lớn bị loại trừ trong dòng −763,9.
- **Đọc được chiều hướng:** LNTT mảng giống & thực phẩm giảm từ 797,9 xuống 427,4 tỷ (−46%) trong khi doanh thu ngoài +6,2%. Mảng TACN bán ngoài +19,6%. Một nửa nội bộ của chuỗi (3,66 nghìn tỷ TACN bán nội bộ) cho thấy chi phí nuôi heo phụ thuộc giá TACN do chính tập đoàn đặt.
- **Q3 riêng:**
  - Công ty mẹ (chủ yếu TACN): DT thuần 2.440,3 (+39,4%), LN gộp 178,4 (+25,0%), biên 7,3% so với 8,2%.
  - Phần hợp nhất trừ công ty mẹ (trại, dầu, công ty con, kể cả loại trừ): LN gộp 409,3 so với 509,4 (−19,7%).
  - Dầu thực vật: +320% lợi nhuận theo giải trình nhưng không có số tuyệt đối, nên không tách được dầu khỏi trại.

**Một lần và bền:**
- Q3/26 không có khoản một lần đáng kể (LN khác 4,4 tỷ).
- Lãi tiền gửi 87,5 tỷ/9T là bền chừng nào còn giữ 3,1 nghìn tỷ tiền gửi HTM. Tuy nhiên đó là gửi bằng tiền vay: chi phí lãi vay 247,3 tỷ, lãi suất 4–8,3%.
- Thuế suất hiệu dụng 9T là 10,8% (ưu đãi nông nghiệp/TACN 10–17%). Còn **647 tỷ lỗ tính thuế chưa ghi nhận tài sản thuế hoãn lại** (TM 31.4, H1), là upside nhỏ, không đưa vào mô hình.

### 2b. Chuẩn hoá lợi nhuận (`model/calc.py`) — quyết định chọn tâm

TTM LNST theo từng cuối quý (Q4/23 → Q3/26): 25 · 418 · 237 · 537 · 769 · 1.205 · 1.566 · 1.597 · 1.507 · 1.373 · 1.155 · 1.012. LNST năm: 2023 = 25,0; 2024 = 769,1; 2025 = 1.506,8; 9T/26 = 863,3.

**Năm cách chuẩn hoá và tác động tới tâm** (kịch bản xấu/tốt cố định 9,0%/15,5%, haircut XDCB trại ở xấu 40%; giá 16.950):

| Cách chuẩn hoá | LNST chuẩn hoá | ROE / vốn chủ | Giá trị cơ sở /cp | **Tâm (sau CK)** | **Giá/tâm** | V_ngắn (toàn vốn) |
|---|---|---|---|---|---|---|
| Trung vị 12 TTM (**vòng 1**) | 1.083,3 | 12,4% | 22.466 | 21.617 | **0,78** | 17.666 |
| Trung bình 12 TTM | 950,0 | 10,9% | 18.828 | 19.834 | 0,85 | 14.028 |
| TTM sau Q4/26 (ước lượng Q4 = +35) | 898,3 | 10,3% | 17.417 | 19.143 | 0,89 | 12.618 |
| **Trung bình 15 quý lịch Q1/23–Q3/26 (CHỌN)** | **843,8** | **9,7%** | **15.929** | **18.414** | **0,92** | 11.129 |
| Trung bình năm 2023–25 | 767,0 | 8,8% | 13.832 | 17.386 | 0,97 | 9.032 |

**Vì sao chọn trung bình 15 quý lịch (843,8) làm tâm, không giữ trung vị 12 TTM:**
1. Mỗi quý chỉ tính **một lần**. Các điểm TTM chồng lấn 3/4 nên trung vị 12 điểm bị dồn về giai đoạn đỉnh 2025: 6/12 điểm TTM chứa ít nhất một trong ba quý đỉnh Q1–Q3/25 (508 · 507 · 343), và sáu giá trị TTM cao nhất (1.155–1.597) đều là các điểm đó.
2. Khung 15 quý phủ **một chu kỳ đủ**: quý lỗ 2023, đáy 2023, đỉnh 2025, đoạn giảm 2026 (Bobby §6 mục 12: lợi nhuận trung bình chu kỳ, ≥ 1 chu kỳ đầy đủ ~3–4 năm; khung 15 quý = 3,75 năm).
3. Chỉ dùng số **đã đo** (không phụ thuộc ước lượng Q4/26). Cách "TTM sau Q4/26" (898) nhạy với một ước lượng chưa có, nên chỉ để đối chiếu.
4. Nó thấp hơn LNST 2026 ước lượng (813–983) ở cận dưới nhưng cùng bậc; trung vị 1.083 cao hơn cả ước lượng 2026 lẫn trung bình chu kỳ, khó bảo vệ là "chuẩn hoá".
- Điểm yếu của lựa chọn này: khung bắt đầu bằng quý lỗ −320,7 (Q1/23) và đáy sâu; nếu coi đó là bất thường thì LNST chuẩn hoá cao hơn. Cận trên hợp lý là 950 (tâm 19.834).
- Đối chiếu ROE năm 2019–2025 (vốn chủ từ BQ, ước lượng): 11,7 / 41 / 18,6 / 3,2 / 0,5 / 13,5 / 20,3%. LNST chuẩn hoá / vốn chủ Q3/26 = **9,7%**, nằm trong dải này; trung bình bỏ 2020 là 11,3%.

## 3. Heo hơi −40% từ T1: DBC chịu mức nào

- **Dữ kiện:** doanh thu ngoài của mảng giống & thực phẩm H1/26 là 4.557,8 tỷ. BCTC không công bố số đàn nái, số heo xuất chuồng, giá thành/kg hay doanh thu vaccine, nên mọi con số dưới đây là **ước lượng**.
- **Độ nhạy (ước lượng, cận trên):**
  - Giả sử giá heo bình quân H1/26 ≈ 70k/kg (đường giá của Bobby: T1 80k, Q2 67–70k). Khi đó sản lượng hơi quy đổi ≤ 65 nghìn tấn/6 tháng, tức ≤ 130 nghìn tấn/năm. Đây là cận trên vì doanh thu mảng còn gồm gà, trứng, thịt chế biến, heo giống.
  - **±5.000 đ/kg giá heo ⇒ ±~650 tỷ doanh thu/năm ⇒ ±550–650 tỷ LNST/năm** (trại phần lớn được ưu đãi/miễn thuế). Tương đương **±50–60% LNST chuẩn hoá**, hay ±1.300–1.500 đ EPS.
  - Đây là biến số lớn nhất của DBC, lớn hơn mọi biến số bảng cân đối.
- **Q3/26 so với Q3/25 — nguyên nhân (viết lại, vòng 2):**
  - LN gộp ngoài công ty mẹ giảm 100,1 tỷ (409,3 so với 509,4). Giá heo bình quân **không** giảm so với Q3/25: chỉ số giá sản phẩm chăn nuôi lợn (PPI, GSO) Q3/2026 **+0,7% YoY**, 9T +0,2%; 2025 cũng có cùng hình dạng giá (mở năm > 70k, rơi > 40% về ~48–50k) (Bobby §2a). Nên giá heo không giải thích được −100 tỷ.
  - Khớp hơn là **chi phí đầu vào đỉnh Q3**: chỉ số nguyên liệu RMI = 1,00 ở đỉnh T9–T10 (CBOT ngô đỉnh 525,8 ở T9), hai đợt tăng giá TACN T9–T10 chưa vào hết biên (Bobby §1, §2f). DBC tiêu thụ kho nguyên liệu mua giá cao (tồn nguyên liệu −27% trong 9T).
  - Không có số giá thành hay giá heo DBC thực nhận, nên **không tách được** phần giá heo và phần chi phí; con số "giá heo Q3 ≈ 58k so với 60–63k" ở vòng 1 là ước lượng không có cơ sở và đã bỏ.
- **Q4/26:** giá bình quân ước 50–52k (T10–T11 46–49k, T12 52–57k theo base của Bobby), thấp hơn Q3 (ước lượng).
  - Mốc so sánh: **Q4/25 LNST 148,6 tỷ ở giá heo ~48–50k** (BQ `NP_P0`; Bobby §2a: Hà Nội 48k ngày 12/11/2025). Giá Q4/26 tương đương Q4/25, nhưng chi phí lãi vay Q3/26 là 100,4 so với 62,5 (+38 tỷ/quý) và biên gộp thấp hơn, nên không có cơ sở cho mức cao hơn 148,6.
  - Bù một phần: nguyên liệu giao ngay đã hạ ~9% (RMI 0,912, độ trễ 2–4 tháng).
  - **LNST Q4/26 ước lượng −50 đến +120 tỷ** (ước lượng, giữ như vòng 1). Cả năm 2026 = 863,3 + Q4 = **813–983 tỷ**.
- **Q1/27:** Tết 06/02/2027, Bobby đặt F1 = P(T1/27 ≥ 55k) là 0,65. Nếu đúng, Q1/27 hồi về vùng 200–350 tỷ (ước lượng).
- **Biên TACN và nguyên liệu nhập:**
  - Tồn kho nguyên liệu giảm từ 1.700,9 xuống 1.241,9 tỷ (−27%) trong 9T, cho thấy công ty dùng dần kho mua giá cao và không tích trữ thêm ở đỉnh Q3.
  - Biên công ty mẹ Q3 là 7,3% (Q3/25: 8,2%). Hai đợt tăng giá TACN T9–T10 chưa vào hết biên quý 3.
  - Hướng 2 quý tới **mở** (Bobby F10/F11), nhưng sản lượng bán ngoài có rủi ro giảm nếu nông hộ giảm đàn.
- ⚠️ **Rủi ro trích lập tài sản sinh học (ước biên độ, vòng 2):**
  - Heo thịt 1.877,7 tỷ ghi theo giá gốc = giá trị có thể thu hồi (TM 12.1, `q3h_19`); dự phòng giảm giá hàng tồn kho (mã 142) = 0 (`q3h_02`).
  - Giá thành khối tích hợp ước ~48–55k/kg (Bobby, không có số công bố) so với giá T10–T11 46–49k: thiếu hụt giá trị thuần 0–15% ở cận trên. **Giả định lệch giá trị thuần 5–10% (ước lượng) ⇒ trích lập 94–188 tỷ** (218–436 đ/cp; 11–22% LNST chuẩn hoá 844). Ước lượng này **không** nằm trong tâm; nó là rủi ro Q4/26 và đã gắn vào mốc §9.
  - **Dấu hiệu loại nái** (Bobby F8): nguyên giá lợn bố mẹ 669,9 → 606,2 tỷ, trong đó thanh lý/nhượng bán 356,9 và tăng đàn 293,2 (TM 12.2, `q3h_19`). Heo nái đang được thay nhiều hơn bổ sung, phù hợp việc loại nái khi biên âm, nhưng không có số đầu con.

## 4. Bảng cân đối và dòng tiền (30/9/2026)

| | 30/9/26 | 31/12/25 | Ghi chú |
|---|---|---|---|
| Tiền + tương đương | 1.192,0 | 426,2 | 859,0 là tiền gửi ≤ 3 tháng |
| Tiền gửi HTM ngắn hạn | 3.100,5 | 1.859,2 | 798 tỷ bị **cầm cố** cho vay (TM 5, H1) |
| HTM dài hạn | 45,0 | 10,0 | |
| **Tổng tiền + HTM** | **4.337,6** | 2.295,4 | |
| Vay + thuê TC ngắn hạn | 5.763,1 | 4.770,2 | vay NH TM Nhà nước 5.619,6; bên liên quan 20 |
| Vay + thuê TC dài hạn | 1.859,2 | 1.106,4 | vay dài hạn 1.492,3 (7–9,1%); thuê tài chính 490,4 tổng |
| **Nợ vay gộp** | **7.622,3** | 5.876,6 | |
| **Nợ ròng** | **3.284,7** | 3.581,2 | ND/E 0,38 (đầu năm 0,44) |
| Vốn chủ (cổ đông mẹ) | 8.720,4 | 8.068,0 | BVPS 20.231 đ |

- **Đòn bẩy vừa phải.** EBIT 9T 1.215 (LNTT + lãi vay) gấp 4,9 lần lãi vay. Vay gộp cao song song tiền gửi lớn là mô hình "vay ngắn hạn tài trợ vốn lưu động, giữ tiền gửi" thường thấy ở doanh nghiệp quốc doanh/nông nghiệp miền Bắc. Chi phí carry ròng 9T = 247,3 − 87,5 = 159,8 tỷ.
- **Phải thu khách hàng 335,5 tỷ, DSO ~7 ngày** trên doanh thu năm hoá. Công nợ đại lý TACN rất thấp, nên rủi ro nợ xấu đại lý khi nông hộ lỗ là nhỏ. Dự phòng phải thu mới trích 3,7 tỷ.
- Trả trước người bán tăng từ 171,5 lên 459,6 tỷ (+288,1; `q3h_02`).
- ⚠️ **Phải thu người lao động 237,1 tỷ tại 30/9** (208,8 đầu năm; TM 4a, `q3h_12`) = **27,5% LNST 9T** (863,3). Phần lớn là tạm ứng giải phóng mặt bằng trại (~178 tỷ theo TM 7.1 bán niên, `h1_d`). Đây là tiền đã ra khỏi công ty cho cá nhân và chưa vào tài sản dự án; ghi thành **WARNING** ở §7, không gọi là nhỏ.
- **Tồn kho 3.281,6:** nguyên liệu 1.241,9 · dở dang 1.347,9 (trong đó **BĐS dở dang ~1.186 tại 30/6**, TM 8) · thành phẩm 365,6 · hàng hoá 78,6 · hàng đi đường 209,7. 3.020 tỷ tồn kho bị cầm cố cho vay.
- **Tài sản sinh học:** ngắn hạn 1.877,7 (heo thịt); dài hạn 740,0 (heo nái, gà bố mẹ; nguyên giá 727,2, khấu hao luỹ kế 153,9; khấu hao 9T 186,1). Ghi theo giá gốc, chi phí phân bổ theo đầu con/ngày nuôi (TM 9, H1), **không đánh giá lại**.
- **XDCB dở dang 1.302,6** (đầu năm 1.750,0):
  - Dự án đã chuyển sang TSCĐ năm 2026: nhà máy ép dầu giai đoạn 2 (1.095,4), nhà máy vaccine (234,0).
  - Đang dở: Lợn Quảng Ninh 360,2 · Nhà máy TACN Nutreco Hà Tĩnh 266,6 · khu chăn nuôi lợn CNC Ngọc Lặc 244,3 · Lào Cai 108,3 · Lam Sơn–Như Xuân 104,1 · Quảng Trị 56,6 · Trung tâm đào tạo Lạc Vệ 81,9 · gà Quảng Ninh 28,0 · khác 52,7.
  - **Nhóm dự án trại heo** (Lợn Quảng Ninh 360,2 + Lào Cai 108,3 + Ngọc Lặc 244,3 + Lam Sơn–Như Xuân 104,1 + Quảng Trị 56,6) = **873,4 tỷ** tại 30/9, so với 204,5 đầu năm (+668,9). DBC là một phần của làn sóng mở trại 2026 mà Bobby cảnh báo (§2b).
  - Theo luật 03/11, **base** ghi các dự án theo giá sổ (NPV=0). Bobby §2b có dữ liệu độc lập về nguồn cung (đàn +5,4% YoY, tăng trưởng đàn chủ yếu từ trại lớn mới) nên **kịch bản xấu** (không phải base) có haircut 40% cho 873,4 tỷ (§6b).
- **CFO 9T 1.517,9** so với LNST 863,3:
  - Trong đó giảm tồn kho +498,6, tăng phải thu −401,5 (gồm trả trước người bán −288,1), thu khác 88,0.
  - **CFO cốt lõi theo hai chiều (đối xứng):** bỏ giải phóng tồn kho một lần ⇒ 1.019,3 (1,18 × LNST); nếu coi trả trước người bán tăng 288,1 là tạm thời và cộng lại ⇒ 1.307,4 (1,51 × LNST). **Dải ~1.020–1.307.**
  - CFO còn **chứa ~87,5 tỷ lãi tiền gửi HTM**: dòng 27 (thu lãi cho vay, cổ tức) = 0 và điều chỉnh lãi đầu tư ở dòng 05 chỉ −1,6 (`q3h_06`), nên lãi tiền gửi nằm lại trong LNTT và CFO. Loại phần này thì CFO cốt lõi thấp hơn ~87,5 so với dải trên.
  - **Tổng đầu tư 9T/26 = 1.679,7** = capex tiền 1.106,0 + **tài sản thuê tài chính tăng thêm 573,7** (TM 11, `q3h_17`: máy móc thiết bị thuê TC trong năm 573.717.697.339). Gửi thêm tiền HTM 1.276,4 và đầu tư được tài trợ bằng vay ròng.
- **Ba năm (Q4/23–9T/26) — vòng 2, gồm thuê tài chính:** CFO bình quân 1.133,3/năm; đầu tư (capex tiền 987,5 + thuê TC 9T/26 573,7 ÷ 3 = 191,2) = **1.178,7/năm**; capex/CFO = **1,04** (vòng 1: 0,87). **FCFE = −45,5 tỷ/năm.**
  - Thuê TC 2023Q4–2025 **chưa tính** (chưa có BCTC kiểm toán 2025), nên 1,04 là **cận dưới**.
  - **Giải thích dòng tiền âm:** (i) CFO 3 năm gồm Q4/23 = −536 (xây tồn kho ở đáy) và 9T/26 gồm +499 giải phóng tồn kho đã bù, nên trung bình không phản ánh hết tính chu kỳ vốn lưu động; (ii) đầu tư 9T/26 (1.680) vượt CFO (1.518) dù CFO đã nhờ giải phóng tồn kho; (iii) phần thiếu do **vay ròng**: nợ vay gộp 5.876,6 → 7.622,3 (+1.745,7) và tiền + HTM 2.295,4 → 4.337,6 (+2.042,2).
  - **Không chứng minh được nhãn "FCFE thấp do capex tăng trưởng":** khấu hao gồm tài sản sinh học 748,1 trong 9T (≈ 997/năm) xấp xỉ capex tiền ~988/năm, tức một phần lớn là **duy trì** (thay đàn, thay tài sản); capex/doanh thu của DBC 8,6% so với trung vị ngành 7,1% (peer nhỏ, lệch). Phần tăng trưởng nhận diện được: XDCB trại heo 204,5 → 873,4 trong 9T (+668,9) và thuê TC 573,7 (không rõ mục đích).
- ⚠️ **Dòng tài chính có trình bày gộp:** "thu từ phát hành cổ phiếu 461,8" và "cổ tức đã trả 577,3" thực chất là **cổ tức cổ phiếu 12%** (46,18 tr cp, ghi gộp hai chiều) cộng cổ tức tiền 3% (115,5) cho năm 2025 (TM 25.3, H1). Năm 2026 **không có vốn tiền mới**. 9T/25 cũng vậy (502,0 = cổ tức cổ phiếu 15%).

## 5. Cổ đông, insider, thanh khoản

- 431.046.499 cp (ĐKDN thay đổi 26/09/2026: vốn điều lệ 4.310,46 tỷ; cập nhật địa chỉ sau sáp nhập tỉnh Bắc Ninh và ngành nghề kinh doanh. Tôi chưa giải mã được danh mục ngành nghề vì PDF lỗi font).
- **Insider:** bà Nguyễn Thị Thu Hương (Phó CT HĐQT, Phó TGĐ kiêm Giám đốc tài chính) đăng ký mua 2.000.000 cp (TB 01/10/2026) và **đã mua đủ 2.000.000** (báo cáo 14/10/2026). Sở hữu tăng từ 4.651.360 cp (1,08%) lên 6.651.360 cp (~1,54%).
  - Người mua là **giám đốc tài chính**, người nhìn thấy số Q3 trước công bố 21/10. Đây là tín hiệu tích cực có trọng lượng, nhưng chỉ ~0,46% vốn.
  - Chưa đo giá khớp bình quân.
- **Thanh khoản:** ADV trung vị 3 tháng là **20,08 tỷ/phiên**, trung bình 27,06 (BQ `ticker` 18/08–17/11/2026). Vị thế ≤ 20 tỷ thoát trong ≤ 10 phiên ở mức tham gia 10%.
  - **Chiết khấu thanh khoản 2%** (ước lượng; chưa đo Amihud), độ nhạy 0–5% ⇒ tâm 18.789 / 18.414 / 17.850.
- Room ngoại / free float: **chưa có số** (BQ không có cột; cần DNSE secdef). Chưa kiểm.

## 6. Định giá (MÙ giá thị trường; giá chỉ ở bước so sánh cuối)

### 6a. Khung
- **r = 13,5%.** Lãi huy động 12T hiệu dụng tại điểm neo 03/11 là 7,4%; ngày 18/11 cũng 7,4% (`deposit_rate_vn.effective_deposit_rate`, nguồn CCTG 12T 02/11; Big-4 6,8%). Chênh 0bp nên r giữ 13,5% (β pass-through = 1).
- **g = 5%** (ước lượng: tăng trưởng danh nghĩa dài hạn ngành thịt/TACN, thấp hơn GDP danh nghĩa).
- **Phương pháp:** thu nhập thặng dư / P/B hợp lý = (ROE − g)/(r − g), áp lên vốn chủ hoạt động; **XDCB dở dang 1.302,6 ghi theo giá sổ (NPV=0) ở base**.
  - ROE chuẩn hoá trên vốn chủ hoạt động = 843,8 / (8.720,4 − 1.302,6) = **11,4%** (ROE / tổng vốn chủ 9,7%).
  - Moat NARROW nên **không có tham số moat**.
- **Mọi khoản giảm trừ khỏi giá trị cơ sở (base) và cơ sở dữ liệu:**

| Khoản | Mức | Cơ sở dữ liệu |
|---|---|---|
| Chiết khấu thanh khoản | −2% giá trị (ước lượng; độ nhạy 0–5%) | ADV trung vị 3T 20,08 tỷ/phiên (BQ `ticker` 18/08–17/11/2026); vị thế ≤ 20 tỷ thoát ≤ 10 phiên ở 10% tham gia |
| XDCB trại heo | **0 ở base**; −40% × 873,4 tỷ = −349,4 tỷ **chỉ ở kịch bản xấu** (dải 30–50%) | TM 8 (`q3h_13`) cho 873,4; Bobby §2b (nguồn cung, đàn +5,4% YoY) cho haircut |
| Trích lập tài sản sinh học | **0 trong tâm** (rủi ro 94–188 tỷ, §3) | TM 12.1 (`q3h_19`): giá gốc = thu hồi; mã 142 = 0 (`q3h_02`) |
| Phải thu người lao động | **0** (WARNING, §7) | TM 4a (`q3h_12`) |

### 6b. Kịch bản

| | Trọng số | ROE / tổng vốn | ROE / vốn hoạt động | Giá trị/cp (trước CK) | Cơ sở |
|---|---|---|---|---|---|
| Xấu | 25% | 9,0% | 10,6% | **13.509** (14.320 nếu không haircut) | TB ROE 2021–2024; đáy heo kéo dài, F3/F8 của Bobby trượt. **Haircut 40% XDCB trại 873,4 tỷ** (−349,4 tỷ, −811 đ/cp) |
| Cơ sở | 50% | 9,7% | 11,4% | 15.929 | LNST chuẩn hoá 843,8 (TB 15 quý lịch) |
| Tốt | 25% | 15,5% | 18,2% | 29.791 | TB ROE 2019–2025 gồm siêu chu kỳ ASF 2020 |
| **Tâm** | | | | **18.789 trước / 18.414 sau CK** | |

Vùng sau chiết khấu thanh khoản là [13.239; 29.195]. Ở tâm, P/E chuẩn hoá 9,4 và P/B 0,91.
- **Haircut XDCB:** 0% ⇒ tâm 18.612; 30% ⇒ 18.463; 40% ⇒ 18.414; 50% ⇒ 18.364 (mỗi 10% haircut = −50 đ tâm).
- ⚠️ **Hai bất đối xứng trong tập kịch bản (đã nêu, không sửa):**
  1. **Kịch bản tốt dựa trên TB ROE 2019–25 gồm năm 2020 (ROE 41%).** Bỏ 2020 thì TB còn 11,3%, thấp hơn ROE cơ sở vòng 1 (12,4%) và gần ROE cơ sở vòng 2 (9,7%). ROE trên vốn hoạt động (kịch bản tốt 18,2%; cơ sở vòng 1 14,6%) dùng mẫu số đã trừ XDCB nên không so trực tiếp với ROE lịch sử tính trên toàn vốn; hai con số chỉ nhất quán nếu tỷ lệ XDCB/vốn chủ quá khứ tương tự (31/12/25: 1.750,0/8.068,0 = 21,7%, nay 14,9%).
  2. **Kịch bản xấu (9,0%) gần ROE cơ sở mới (9,7%)**, nên phân phối lệch lên. Thử đặt lại (chỉ để kiểm độ vững, **không** dùng làm tâm): xấu = TB ROE 2022–24 (5,7%) ⇒ tâm 16.507 (giá/tâm 1,03); tốt = TTM trung vị (12,4%, bỏ 2020) ⇒ 16.618 (1,02); cả hai ⇒ **14.711 (giá/tâm 1,15)**.

### 6c. Độ nhạy

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| Tâm (β = 1) | 20.500 (+11,3%) | 19.392 (+5,3%) | 18.414 | 17.544 (−4,7%) | 16.766 (−8,9%) |
| Tâm (β = 0,5) | 19.392 | 18.888 | 18.414 | 17.966 | 17.544 |

- **g:** 4% ⇒ 18.541 · 6% ⇒ 18.252 · 7% ⇒ 18.040 (tăng g làm giá trị giảm vì ROE cơ sở 11,4% < r nên tăng trưởng tái đầu tư không tạo giá trị; kịch bản tốt ngược lại). Ít nhạy.
- **Chiết khấu thanh khoản:** 0% ⇒ 18.789 · 5% ⇒ 17.850.
- **Chuẩn hoá LNST (điểm yếu số 1):** xem bảng §2b — tâm 17.386 đến 21.617 tuỳ cách chuẩn hoá; chọn 18.414.
- **Cách đối xử XDCB (lựa chọn phán đoán, điểm yếu số 2):** nếu áp ROE chuẩn hoá lên **toàn bộ** vốn chủ (XDCB cũng chỉ sinh 9,7% < r), cơ sở là **11.129** (−30% so với 15.929). Luật 03/11 buộc base ghi dự án theo giá sổ nên base giữ 15.929; 11.129 là cận dưới của cách đọc này.
- **Moat:** NARROW và NONE cho cùng giá trị (luật "không trừ"). WIDE không áp được vì không có bằng chứng.

### 6d. Nền định giá + C4/D2 (vòng 2: chỉ V_ngắn)

| Nền | Giá trị/cp | Ghi chú |
|---|---|---|
| V_ngắn (LNST chuẩn hoá 843,8 × (1 − g/ROE 9,7%)/(r − g)) | 11.129 | tái đầu tư 51,7% (< 80%, không bị chặn); bằng "cơ sở toàn vốn" |
| V_dài (FCFE) | **không xác định** | **FCFE 3 năm = −45,5 tỷ/năm ≤ 0** (CFO 1.133,3 − đầu tư gồm thuê TC 1.178,7; capex/CFO 1,04, cận dưới). Theo luật: chỉ giữ V_ngắn; **bỏ V_dài, D và cờ phân kỳ**. Giải thích dòng tiền âm ở §4 |
| V theo C4 = CFO3 − min(đầu tư, khấu hao gồm TSSH ~832/năm, ước lượng) | 8.624 | khấu hao sửa: 9T gồm tài sản sinh học = 748,1 (562,0 + 186,1), Q3 = 268,4 (vòng 1 ghi sai 82); ước 3 năm = TB(2025 ~667, 9T/26 quy năm 997). Chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi |
| V theo D2 = CFO3 − 7,1% × DT (trung vị capex/DT ngành) | 382 | chưa qua tiêu chí khoá trước (0/9 nền qua), chỉ theo dõi; trung vị ngành 7,1% từ HAG 29%, BAF 40%, MML 2,4%, VLC 5,7%, VSN 1,8%, DBC 8,6%; peer nhỏ và lệch nên không đáng tin |

⚠️ V_ngắn (11.129) là **nền thấp hơn giá** (16.950). Khác vòng 1, nơi V_ngắn ≈ giá, ở LNST chuẩn hoá mới thị trường đang trả cao hơn mức "mọi đồng vốn kiếm 9,7%". Phần chênh đến từ cách đọc XDCB NPV = 0 và kịch bản tốt.

### 6e. So sánh ngành (BQ `ticker`, ngày 17/11/2026; P/E TTM méo theo chu kỳ)

| Mã | Lý do chọn | P/E TTM | P/B | ROE5Y | ADV trung vị 3T (tỷ) |
|---|---|---|---|---|---|
| **DBC** | | 7,2 | 0,84 | 11,2% | 20,1 |
| HAG | chăn nuôi heo quy mô lớn (lẫn trái cây) | 5,2 | 0,97 | 15,7% | 24,1 |
| MML | 3F gần nhất (TACN đã bán, nay thịt chế biến), nhưng thanh khoản 1,4 tỷ/phiên | 16,8 | 1,44 | 3,5% | 1,4 |
| BAF | **BANNED vĩnh viễn — chỉ tham chiếu** (heo, đang mở rộng mạnh) | 137,2 | 2,88 | 9,9% | 52,1 |

- Peer khu vực (CP Foods, Japfa): **chưa đo trong phiên này**, nên không trích số.
- EV/EBIT chuẩn hoá ở giá 17/11: EV ≈ 7.306 + 3.285 = 10.591; EBIT chuẩn hoá ≈ 1.414 (ước lượng); tỷ số ≈ 7,5×.

### 6f. So giá (bước cuối)
- Giá 16.950 (17/11) bằng **0,92 × tâm** (18.414), nằm trong vùng [13.239; 29.195]. Trên mọi cách chuẩn hoá của §2b, giá/tâm trong **0,78–0,97**.
- Giá **cao hơn** giá trị kịch bản cơ sở sau chiết khấu (15.610) và cao hơn V_ngắn (11.129). Giá thấp hơn tâm vì kịch bản tốt (25%, 29.791) kéo tâm lên.
- Mốc 0,85 × tâm (15.652) **không** thoả ở tâm chính (giá cao hơn 8%); chỉ thoả ở cách chuẩn hoá lạc quan nhất (0,78). Theo luật, không có tín hiệu "rẻ rõ" ở tâm chính; kết luận hướng "rẻ" phụ thuộc cách chuẩn hoá và độ tin vào kịch bản tốt.

## 7. Pháp lý / quản trị / chính sách — chỉ WARNING

- **Kiểm toán:**
  - EY soát xét BCTC bán niên 2026 với kết luận chấp nhận toàn phần, không ngoại trừ, không nhấn mạnh (trang 5 `h1_d`).
  - Có trình bày lại số đầu kỳ theo Thông tư 99/43 (TM 37). Đây là phân loại lại: HTM ngắn hạn, tài sản sinh học tách khỏi tồn kho. Không đổi lợi nhuận.
- ⚠️ **WARNING (mới, có số): phải thu người lao động 237,1 tỷ tại 30/9/2026** (208,8 tại 31/12/2025; TM 4a `q3h_12`; ~178 tỷ là tạm ứng giải phóng mặt bằng trại theo TM 7.1 bán niên). Bằng **27,5% LNST 9T** (863,3) và 2,7% vốn chủ.
  - Đây là tiền tạm ứng cho cá nhân chưa chuyển thành tài sản dự án; tăng 28,3 tỷ trong 9T; không có dự phòng (dự phòng phải thu 3,7 tỷ chỉ cho khách hàng).
  - Không có dấu hiệu sai phạm trong tài liệu đã đọc, nhưng đây là loại khoản mục dễ kéo theo rủi ro quản trị (tạm ứng lớn, theo dõi thanh toán). **Chưa kiểm:** thời hạn hoàn ứng, ai nhận, thuyết minh quyết toán; cần BCTC kiểm toán/BCTN.
- **Vốn phát hành 2024:** 1.330,0 tỷ (chào bán cho cổ đông 1.210,0 + ESOP 120,0).
  - 1.285,3 tỷ góp vào Công ty Dầu thực vật Dabaco cho dự án nhà máy ép và tinh luyện dầu: 816,1 thiết bị, 469,3 vốn lưu động. 44,7 tỷ bổ sung vốn lưu động.
  - **Dùng 100% tính đến 25/06/2026**, đúng phương án ĐHĐCĐ, kiểm toán IAV (CBTT 09/09/2026; tôi đọc trang tóm tắt và bảng sử dụng vốn).
- **Bên liên quan nhỏ:** liên kết Transeco (vận tải 55,8 tỷ H1; cho DBC vay ngắn hạn 25 tỷ không lãi tại 30/6, còn 20 tỷ tại 30/9). CTCP Chế biến thực phẩm Dabaco (49,56%, phải trả 11,4 tỷ).
- **ASF/vaccine:** nhà máy vaccine 234 tỷ đã vào TSCĐ năm 2026. BCTC **không tách doanh thu vaccine** nên tôi **không định giá vaccine** (tránh định giá theo PR). Rủi ro ASF trong trại nái: không có số ổ dịch của DBC.
- Không thấy khởi tố, xử phạt hay ý kiến ngoại trừ trong tài liệu đã đọc. **Chưa kiểm:** giấy phép môi trường từng trại; báo cáo quan trắc môi trường có trên website nhưng chưa đọc.

## 8. Vị thế và lợi thế cạnh tranh (5F tầng b) — làm ĐẦY ĐỦ lần đầu

`data/moat_tags.csv` chưa có DBC; không có DD DBC cũ. Nhận diện loại hình: **doanh nghiệp nông nghiệp hàng hoá tích hợp dọc (feed–farm–food)** cộng mảng phụ BĐS, dầu thực vật, vaccine.

| Lực | Đánh giá | Bằng chứng (nguồn) |
|---|---|---|
| Cạnh tranh nội ngành | Cao | TACN: khối FDI ~60%+ thị phần, chuyển giá đồng loạt 6–7 lần/năm 2026 (Bobby §3, [NỀN]/[DK]). Biên gộp công ty mẹ chỉ 7,3–8,2% |
| Người mua | Phân mảnh; với heo hơi, DBC là người nhận giá | Phải thu 335,5 tỷ ~ DSO 7 ngày: đại lý trả nhanh. Đây là sức mạnh thu nợ, không phải sức mạnh định giá |
| Nhà cung cấp | Cao (ngô/đậu nhập, VN tự chủ ~37%) | **Có phần tự cung:** nhà máy ép đậu (vốn 2024, 1.285 tỷ) tạo khô đậu nội bộ; dầu thực vật +320% LN Q3/26 |
| Sản phẩm thay thế | Trung bình–cao | Thịt nhập rẻ hơn 30–40%, đơn giá nhập −38% YoY (Bobby §2c); gia cầm |
| Gia nhập mới | Trung bình | Làn sóng trại lớn 2025–26 (Bobby §2b), chính DBC cũng đang mở 6 dự án |
| Lực thứ 6 | ASF; quy định môi trường/khoảng cách trại; thuế thịt nhập (FTA) | ASF 2026 401 ổ/25 tỉnh tới T4 (Bobby §2d) |

- **Lợi nhuận siêu ngạch bền? KHÔNG.** ROE_Min5Y 0,5%, ROIC_Min5Y 2,3%, ROIC5Y 8,7% (BQ `ticker_financial` 21/10/2026). ROE theo năm dao động 0,5–41%. Điều kiện (i) trượt.
- **Cơ chế rào cản gọi tên được: CÓ nhưng hẹp.** Gồm (a) chuỗi tích hợp dùng 3,66 nghìn tỷ TACN nội bộ/6 tháng; (b) ép đậu tự cung khô đậu; (c) di truyền giống (công ty giống cụ kỵ, bố mẹ) + vaccine. Không đo được thị phần TACN miền Bắc của DBC (chưa có số).
- **Đồng hồ cắt hào:** không có giấy phép hay trữ lượng hết hạn. Lực thứ 6 là cú sốc ngẫu nhiên (ASF), không phải đồng hồ.
- **⇒ moat_tier = NARROW (mỏng), moat_type = COST/INTEGRATION; rủi ro số 1 = chu kỳ giá heo + ASF lọt trại nái.** Không thưởng tham số moat (§6a).
  - **Ranh giới NARROW/NONE:** NARROW đứng được nhờ cơ chế gọi tên được (a)–(c), nhưng **không định lượng được thị phần** và không có lợi nhuận siêu ngạch bền (ROIC_Min5Y 2,3%). **NONE cũng đứng được.** Giá trị không đổi giữa hai nhãn (luật "không trừ").
- **Đề xuất dòng `moat_tags.csv` (KHÔNG sửa file):**
  `DBC,NARROW,COST/INTEGRATION,-,"THIN narrow (NONE also defensible; share not quantified). Hog-price cycle (±5k VND/kg ≈ ±50-60% normalized NPAT, upper-bound est.) + ASF in sow farms; ROE_Min5Y 0.5%/ROIC_Min5Y 2.3% => no through-cycle excess return; partial input self-supply via 2026 soybean-crush plant",2026-11-18,dd_DBC_20261118,N`

## 9. Mốc khoá trước — điều kiện đổi nhận định THEO CẢ HAI CHIỀU

| Mốc | Ngày chấm | Hướng tăng (tâm ↑ / trọng số tốt ↑) | Hướng giảm (tâm ↓ / trọng số xấu ↑) |
|---|---|---|---|
| BCTC Q4/26 | ≤ 30/01/2027 | LNST Q4/26 ≥ 120 tỷ, không trích lập tài sản sinh học | LNST Q4/26 < −50 tỷ **hoặc** trích lập tài sản sinh học/tồn kho > 100 tỷ (cận dưới dải 94–188) ⇒ trọng số xấu 35% |
| Bobby F1 (giá heo T1/27 ≥ 55k) | 05/02/2027 | đúng và ≥ 65k (F2) ⇒ trọng số tốt 35% | < 50k ⇒ trọng số xấu 35% |
| BCTC Q1/27 | ≤ 30/04/2027 | LNST Q1/27 ≥ 300 tỷ **và** biên gộp công ty mẹ ≥ 8,5% (biên TACN mở) | LNST Q1/27 < 150 tỷ |
| Bobby F8 (đàn cuối T3/27 ≤ +3% YoY) | 15/04/2027 | đúng ⇒ chu kỳ tự sửa | sai (≥ +4%) ⇒ đáy kéo dài, trọng số xấu 40% |
| Bảng cân đối Q4/26–Q2/27 | theo BCTC | ND/E ≤ 0,35 khi XDCB vào vận hành | ND/E > 0,6 **hoặc** phát hành tăng vốn tiền mặt dưới BVPS ⇒ WARNING tăng vốn |
| Lãi huy động 12T hiệu dụng | liên tục | giảm ≥ 50bp ⇒ +5,4% | tăng ≥ 50bp ⇒ −4,8% |
| TTM LNST | Q2/27 | TTM LNST ≥ 1.200 tỷ qua đáy ⇒ nâng chuẩn hoá về trung vị 12 TTM (tâm 21.617) | TTM LNST < 600 tỷ tại Q2/27 ⇒ chuẩn hoá về TB năm 2023–25 = 767 (tâm 17.386) |
| Phải thu người lao động | BCTC Q4/26 | giảm về ≤ 150 tỷ (hoàn ứng) ⇒ gỡ WARNING | tăng > 300 tỷ hoặc trích lập ⇒ WARNING quản trị cấp cao hơn |

## 10. Điểm yếu của chính báo cáo / việc còn mở

1. **Chọn LNST chuẩn hoá (843,8).** Tâm thay đổi 17.386–21.617 (giá/tâm 0,78–0,97) tuỳ cách chuẩn hoá; đây là điểm yếu **ngang hàng** với cách đọc XDCB. Khung 15 quý bắt đầu bằng quý lỗ −320,7 (Q1/23); loại quý đó thì chuẩn hoá cao hơn. Bobby chỉ ghi "≥ 1 chu kỳ ~3–4 năm", không chỉ định cách tính.
2. **Tập kịch bản lệch lên.** Kịch bản xấu (9,0%) ≈ cơ sở (9,7%); kịch bản tốt lấy trung bình gồm năm 2020. Đặt lại cả hai theo dữ liệu gần hơn (xấu 5,7%, tốt 12,4%) ⇒ tâm 14.711, giá/tâm **1,15** (§6b). Chưa chọn lại vì cần chỉ đạo (ranh giới giữa sửa phương pháp và sửa kết luận).
3. **Cách đọc XDCB (NPV=0) và ROE trên vốn hoạt động** đẩy cơ sở cao hơn 43% so với "toàn vốn" (15.929 so với 11.129).
4. **Không có số vận hành** (đàn nái, heo xuất chuồng, giá thành/kg, sản lượng TACN bán ngoài, giá heo DBC thực nhận). Độ nhạy giá heo là cận trên ước lượng; không tách được giá và chi phí trong −100 tỷ LN gộp Q3.
5. **Chưa đọc BCTC kiểm toán năm 2025.** Số năm lấy từ BQ. Thuê tài chính 2023Q4–2025 chưa tính vào đầu tư nên capex/CFO 1,04 là cận dưới. Chưa tìm trên `dabaco.vn/quan-he-co-dong/page/2/`.
6. LNTT bộ phận bị méo bởi loại trừ cổ tức nội bộ (−764 tỷ), nên không tách được lợi nhuận thật theo mảng. Dầu thực vật và trại chưa tách được Q3.
7. Khấu hao 3 năm (832/năm) là ước lượng; chỉ dùng cho C4 (hiển thị).
8. **Lộ giá trong phiên:** truy vấn so sánh peer (§6e) trả về giá DBC trước khi tôi chạy mô hình vòng 1. Tham số mô hình (ROE, r, g, trọng số) đặt theo BCTC/BQ và luật skill. **Vòng 2 đã biết giá khi chọn cách chuẩn hoá**; lựa chọn 843,8 dựa trên lý do kỹ thuật ở §2b (một quý một lần, một chu kỳ đủ, chỉ số đã đo), và toàn bộ năm cách được công bố cạnh nhau.
9. Chưa có room ngoại/free float; chưa đo Amihud. Chiết khấu thanh khoản 2% là ước lượng.
10. Q4/26 ước lượng dựa trên đường giá heo của Bobby. Bobby tự khai không hoàn toàn mù (§0 sector read: thấy tiêu đề tin "lãi quý 3 giảm sâu").
11. Phải thu người lao động 237,1 tỷ chưa kiểm được thời hạn hoàn ứng (§7).

## 11. Nguồn
- `src/q3_hopnhat.pdf`: BS trang 2–4, KQKD trang 5, LCTT trang 6–7, TM trang 12–23, giải trình 518/CV-DBC trang 24. Vòng 2 kiểm lại trên scan: trang 2 (trả trước người bán, mã 142), 3 (TSSH dài hạn), 6 (LCTT: dòng 02, 05, 21, 27), 12 (TM 4a phải thu NLĐ), 13 (TM 8 XDCB), 17 (TM 11 thuê TC), 19 (TM 12 tài sản sinh học).
- `src/q3_congtyme.pdf`: KQKD công ty mẹ trang 5.
- `src/h1_d.pdf`: kết luận soát xét EY trang 9; TM 5, 7, 8, 9, 14, 23, 25, 31, 32, 34 (trang 31–64); giải trình 431/CV-DBC trang 69.
- `src/web/insider_tb.pdf` (01/10/2026), `src/web/insider_kq.pdf` (14/10/2026), `src/web/dkdn.pdf` (26/09/2026), `src/web/vonph_1Yqen…pdf` (CBTT 09/09/2026, IAV). Trang gốc: `src/ir.html`, `src/q3.html`, `src/h1.html`.
- BQ: `tav2_bq.ticker_financial` (DBC 2019–Q3/26; peer TTM), `tav2_bq.ticker` (giá/ADV/PE/PB 18/08–17/11/2026).
- Ngành: `kb/data_registry/market-state/sector_read_chan_nuoi_heo_tacn_20261118.md` (Bobby, blind).
- Vĩ mô: `macro_snapshot_20261118.md`. Chỉ dòng `ok`, DISPLAY-ONLY:
  - CPI 5,09% (T10, thịt lợn đang kéo CPI xuống);
  - bán lẻ +14,7% (cầu không yếu, nên giá heo giảm là vấn đề cung);
  - USD/VND −2,54% 12T (ngô/đậu nhập rẻ hơn khi quy VND);
  - LNH 3M 6,63%, −1,13pp 3T (chi phí vay ngắn hạn dịu, có lợi cho mô hình vay ngắn hạn 5,6 nghìn tỷ).
  - **Điều thị trường chưa tính (bối cảnh, không đổi giá trị):** biên TACN mở 1–2 quý tới nhờ nguyên liệu hạ trong khi giá bán dính; tiền gửi HTM 3,1 nghìn tỷ hưởng lãi trong khi lãi vay ngắn hạn dịu.

## 12. Ghi sổ giá (CHỜ skeptic vòng 2)
Chưa ghi `kb/dd_price_zones.json` (theo chỉ đạo vòng 2). Khi ghi: `center 18414`, `zone [13239, 29195]`, `assumptions_file model/assumptions_DBC_20261118.json`, `assumptions_md5 708441c3c673573b354d245a2428b0dc` (`rev` mới so với vòng 1: 511073ce…, center 21815). Không ghi `v_short`/`v_long`/`D` (luật 11/11). Sửa giả định sau khi ghi sổ thì phải thêm `rev` mới.

## Phụ lục E — Đính chính sau phản biện vòng 1 (nội bộ; bản gửi nhà đầu tư sẽ KHÔNG nhắc mục này)

fundamental-skeptic vòng 1: REFUTED ở mức văn bản/trình bày (confidence medium). Các số trong REPORT vòng 1 truy về scan khớp (~30 số). Dưới đây là từng đính chính và nơi đã sửa. `assumptions_md5`: `511073ce…` → `708441c3c673573b354d245a2428b0dc`.

| # | Đính chính | Đã sửa ở | Kết quả |
|---|---|---|---|
| 1 | Headline "0,78 × tâm, dưới mốc 0,85" phụ thuộc trung vị 12 TTM | §0, §2b, §6b, §6f, §10 | Thêm bảng 5 cách chuẩn hoá; **chọn trung bình 15 quý lịch (843,8)**, tâm 21.815 → **18.414**, giá/tâm **0,92**, dải 0,78–0,97. Skeptic ước 0,78–0,96 (0,88/0,91/0,96 ở ba cách giữa); chênh ≤ 0,01 vì tôi đã gồm haircut XDCB (#6). Đếm "8/12 điểm TTM chứa quý đỉnh" của skeptic: tôi đếm được 6/12 (quý đỉnh = Q1–Q3/25); không đổi kết luận |
| 2 | Capex 9T/26 thiếu 573,7 tỷ thuê tài chính; FCFE ≤ 0 | §0, §4, §6d, §10 | Đầu tư 9T = 1.679,7 (đã kiểm `q3h_17`). capex/CFO 0,87 → **1,04** (cận dưới), FCFE 146 → **−45,5/năm**. **Bỏ V_dài (4.177), D (1,44) và cờ phân kỳ**; giải thích dòng tiền âm; bỏ nhãn "capex tăng trưởng" |
| 3 | Khấu hao C4 thiếu tài sản sinh học | §4, §6d, §10 mục 7 | 562,0 = 482,1 + 74,0 + 5,8 (+ TSSH 186,1 = 748,1); Q3 = 268,4 (không phải 82). Ước 3 năm 667 → **832**/năm (ước lượng); V_C4 13.372 → 8.624 (chỉ hiển thị). Skeptic gợi ≈ 750; 832 theo công thức TB(2025 ~667, 9T/26 quy năm 997) |
| 4 | "Q3 chỉ chịu một phần cú rơi" mâu thuẫn Bobby §2a | §0, §3 | Viết lại: PPI heo Q3 +0,7% YoY; −100 tỷ LN gộp khớp đỉnh giá nguyên liệu hơn giá heo; bỏ "giá heo Q3 ≈ 58k vs 60–63k" (ước lượng không cơ sở); thêm mốc Q4/25 LNST 148,6 ở giá ~48–50k |
| 5 | Ước biên độ trích lập TSSH | §0, §3, §9 | 5–10% × 1.877,7 = **94–188 tỷ** (ước lượng), 218–436 đ/cp, 11–22% LNST chuẩn hoá; dự phòng tồn kho = 0 (`q3h_02`); thêm dấu hiệu loại nái: 669,9 → 606,2, thanh lý 356,9 (`q3h_19`) |
| 6 | Haircut XDCB trại heo ở kịch bản xấu | §4, §6a, §6b | −40% × 873,4 = −349,4 tỷ chỉ ở **xấu** (bad 14.320 → 13.509; tâm −198 đ). Base giữ NPV = 0. Số XDCB trại tôi cộng lại từ scan: **873,4** (skeptic ghi 873,5) và 204,5 đầu năm (skeptic ghi 204,6); chênh làm tròn |
| 7 | Phải thu người lao động 237,1 tỷ = 27% LNST 9T | §0, §4, §7, §9 | Ghi thành **WARNING có số** (237,1 tại 30/9; 208,8 đầu năm; 27,5%). Skeptic ghi 212,2 tại 30/6 (H1); tôi không kiểm lại số H1 nên dùng 208,8 (đầu năm, `q3h_12`) |
| 8 | CFO cốt lõi đối xứng hai chiều | §4 | Dải **1.020–1.307** (bỏ giải phóng tồn kho 498,6; cộng lại trả trước người bán 288,1); lãi tiền gửi ~87,5 nằm trong CFO (dòng 27 = 0; dòng 05 = −1,6; `q3h_06`) |
| 9 | Kịch bản tốt dùng TB ROE gồm 2020; ROE_op cao | §6b, §10 | Nêu bất đối xứng (bỏ 2020: 11,3%); thêm tính độ vững (xấu 5,7%, tốt 12,4% ⇒ tâm 14.711, giá/tâm 1,15). **Không** đổi tập kịch bản. Câu "ROE_op cao hơn mọi mốc lịch sử" của skeptic tôi diễn đạt lại: mẫu số khác nhau nên không so trực tiếp (§6b) |
| 10 | BQ vs BCTC thêm 4 dòng | §1 | Đã chạy lại BQ: Revenue_P0 Q3/25 5.021,6; Q4/25 2.350,5; capex H1/26 279,9 + 442,0 = 721,9 (vs 767,6); vốn chủ 2022-01-27 = 2.348 |
| 11 | Moat NARROW mỏng | §0, §8 | Nêu ranh giới NARROW/NONE; dòng `moat_tags` thêm "THIN narrow (NONE also defensible…)" |

**Việc skeptic ghi nhưng KHÔNG đưa vào REPORT (đúng chỉ đạo):** hồ sơ §2.5 cho mua discretionary (hôm nay sẽ trượt "đáy chu kỳ chưa xác định" và "dẫn đầu chi phí thấp" chưa chứng minh).

**Quyết định cần Mike/user biết:** (a) chọn 843,8 thay vì giữ 1.083 là phán đoán của tôi, có lý do §2b, năm cách đều công bố; (b) tập kịch bản xấu/tốt **không** đổi nên phân phối lệch lên; đặt lại theo dữ liệu gần hơn cho giá/tâm 1,15 (cần chỉ đạo nếu muốn đổi); (c) vòng 2 chọn cách chuẩn hoá sau khi đã biết giá.
