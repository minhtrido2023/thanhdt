# DD — DBC (CTCP Tập đoàn Dabaco Việt Nam, HOSE) · 2026-11-18 · job `Taylor_20261118_035743` · VÒNG 1 (chưa qua fundamental-skeptic)

> Chỉ nghiên cứu. Không đặt lệnh, không sửa production, không gửi email. Đơn vị: tỷ đồng, trừ khi ghi khác.
> Nguồn chính: BCTC hợp nhất Q3/2026 (`src/q3_hopnhat.pdf`, ký 21/10/2026); BCTC công ty mẹ Q3/2026 (`src/q3_congtyme.pdf`);
> BCTC hợp nhất bán niên 2026 do EY soát xét (`src/h1_d.pdf`, bản EN; `h1_a` = riêng EN, `h1_b`/`h1_c` = bản VN; báo cáo soát xét ký 26/08/2026).
> Mô hình: `model/calc.py` + `model/assumptions_DBC_20261118.json` (**assumptions_md5 = `511073ce713239e5cf7d242491d07922`**), output `model/calc_output.txt`.
> Tôi chưa có BCTC kiểm toán năm 2025. Số năm 2023–2025 lấy từ BQ `ticker_financial`, đã đối chiếu từng điểm ở §1.

## 0. Kết luận

- **Giá trị nội tại, tâm = 21.815 đ/cp** (sau chiết khấu thanh khoản 2%; trước chiết khấu 22.261). **Vùng [14.034; 29.195]**, tức kịch bản xấu đến tốt, trọng số 25/50/25.
  r = 13,5%, g = 5%, LNST chuẩn hoá chu kỳ 1.083 tỷ (EPS 2.513 đ). Ở tâm, P/E là 8,7 và P/B là 1,08.
- **So giá (bước cuối):** giá 16.950 đ ngày 17/11/2026 (BQ `ticker`) bằng **0,78 × tâm**, thấp hơn mốc 0,85 × tâm (18.543).
  **Có cờ PHÂN KỲ MẠNH**: D = 1,44 > ln3, vì V_dài (FCFE) chỉ 4.177. Nguyên nhân là FCFE thấp do capex tăng trưởng (capex/CFO 3 năm = 87%), không phải dấu hiệu đắt.
  Theo luật, khi có phân kỳ mạnh thì luật 0,85 × tâm **không tự kích hoạt** mà cần Mike/user phán đoán.
- **Q3/26 xấu đúng như chu kỳ báo:**
  - Doanh thu thuần +37,4% YoY (5.138 tỷ), nhưng LN gộp −9,9% (587,7 tỷ), biên gộp 11,4% so với 17,4%. LNST 200,2 tỷ (−41,6%).
  - 9T/26: LNST 863,3 tỷ (−36,4%).
  - Mảng heo kéo xuống. TACN (công ty mẹ: DT +39%, LN gộp +25%) và dầu thực vật (DT +303%, LN +320% theo giải trình 21/10) kéo lên.
- **Q4/26 nhiều khả năng còn xấu hơn Q3**: giá heo miền Bắc T10–T11 ở 46–49k. Ước lượng LNST Q4/26 từ −50 đến +120 tỷ (§3).
  Thị trường đã thấy hướng này; phần chưa biết là **độ sâu** và việc **có trích lập tài sản sinh học hay không**.
- **Bảng cân đối không phải điểm yếu chính:**
  - Nợ ròng thật 3.285 tỷ (vay + thuê tài chính 7.622 − tiền và tiền gửi HTM 4.338). ND/E 0,38, giảm từ 0,44 đầu năm.
  - CFO 9T 1.518 tỷ, bằng 1,76 × LNST, nhưng có 499 tỷ là do giảm tồn kho nguyên liệu (một lần).
  - Tài sản sinh học ghi theo **giá gốc** (không đánh giá lại theo giá trị hợp lý), nên **không có lãi ảo** từ đánh giá lại. Rủi ro ngược lại là phải trích lập khi giá heo dưới giá thành.
- **Pháp lý/quản trị: không có WARNING mới.**
  - EY soát xét bán niên với kết luận chấp nhận toàn phần, không có đoạn nhấn mạnh.
  - Vốn phát hành 2024 (1.330 tỷ) đã dùng 100% đúng mục đích, có kiểm toán IAV.
  - Phó Chủ tịch HĐQT kiêm Giám đốc tài chính **đã mua đủ 2.000.000 cp** (báo cáo kết quả 14/10/2026).
- **Moat: NARROW** (tích hợp 3F + quy mô TACN miền Bắc + ép đậu tương tự cung). **Không thưởng tham số moat** vì ROE_Min5Y chỉ 0,5% và ROIC_Min5Y chỉ 2,3%, tức không có lợi nhuận siêu ngạch bền qua chu kỳ.
- **Điểm yếu lớn nhất của báo cáo:**
  - Tâm phụ thuộc lựa chọn "XDCB ghi theo giá sổ (NPV=0), ROE chuẩn hoá áp lên vốn trừ XDCB". Nếu áp ROE 12,4% lên toàn bộ vốn thì kịch bản cơ sở là 17.666, tức −21% (§6c).
  - Không có số đàn nái hay số heo xuất chuồng nên độ nhạy giá heo chỉ là cận trên ước lượng.

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

### 2b. Chuẩn hoá lợi nhuận (`model/calc.py`)

TTM LNST theo từng cuối quý (Q4/23 → Q3/26): 25 · 418 · 237 · 537 · 769 · 1.205 · 1.566 · 1.597 · 1.507 · 1.373 · 1.155 · 1.012.
- **Trung vị là 1.083,3 tỷ** (EPS 2.513 đ trên 431,05 tr cp). Cửa sổ này phủ cả đáy 2023 và đỉnh 2025, gần một chu kỳ đủ.
- Đối chiếu ROE năm 2019–2025 (vốn chủ từ BQ, ước lượng): 11,7 / 41 / 18,6 / 3,2 / 0,5 / 13,5 / 20,3%. Trung vị 13,5%, trung bình bỏ năm 2020 là 11,3%.
- LNST chuẩn hoá / vốn chủ Q3/26 = **12,4%**, nằm trong dải đó.

## 3. Heo hơi −40% từ T1: DBC chịu mức nào

- **Dữ kiện:** doanh thu ngoài của mảng giống & thực phẩm H1/26 là 4.557,8 tỷ. BCTC không công bố số đàn nái, số heo xuất chuồng, giá thành/kg hay doanh thu vaccine, nên mọi con số dưới đây là **ước lượng**.
- **Độ nhạy (ước lượng, cận trên):**
  - Giả sử giá heo bình quân H1/26 ≈ 70k/kg (đường giá của Bobby: T1 80k, Q2 67–70k). Khi đó sản lượng hơi quy đổi ≤ 65 nghìn tấn/6 tháng, tức ≤ 130 nghìn tấn/năm. Đây là cận trên vì doanh thu mảng còn gồm gà, trứng, thịt chế biến, heo giống.
  - **±5.000 đ/kg giá heo ⇒ ±~650 tỷ doanh thu/năm ⇒ ±550–650 tỷ LNST/năm** (trại phần lớn được ưu đãi/miễn thuế). Tương đương **±50–60% LNST chuẩn hoá**, hay ±1.300–1.500 đ EPS.
  - Đây là biến số lớn nhất của DBC, lớn hơn mọi biến số bảng cân đối.
- **Q3/26 so với Q3/25:** LN gộp ngoài công ty mẹ giảm 100 tỷ. Giá heo Q3/26 ≈ 58k (ước lượng) so với ~60–63k Q3/25 (ước lượng). Như vậy Q3 mới chỉ chịu một phần cú rơi.
- **Q4/26:** giá bình quân ước 50–52k (T10–T11 46–49k, T12 52–57k theo base của Bobby), thấp hơn Q3 khoảng 6–8k/kg.
  - Ước tính LN gộp trại −200 đến −260 tỷ so với Q3. Bù một phần nhờ nguyên liệu TACN giao ngay đã hạ ~9% (RMI 0,912, có độ trễ 2–4 tháng).
  - **LNST Q4/26 ước lượng −50 đến +120 tỷ** (Q4/25: 148,6). Cả năm 2026 ước lượng 810–985 tỷ.
- **Q1/27:** Tết 06/02/2027, Bobby đặt F1 = P(T1/27 ≥ 55k) là 0,65. Nếu đúng, Q1/27 hồi về vùng 200–350 tỷ (ước lượng).
- **Biên TACN và nguyên liệu nhập:**
  - Tồn kho nguyên liệu giảm từ 1.700,9 xuống 1.241,9 tỷ (−27%) trong 9T, cho thấy công ty dùng dần kho mua giá cao và không tích trữ thêm ở đỉnh Q3.
  - Biên công ty mẹ Q3 là 7,3% (Q3/25: 8,2%). Hai đợt tăng giá TACN T9–T10 chưa vào hết biên quý 3.
  - Hướng 2 quý tới **mở** (Bobby F10/F11), nhưng sản lượng bán ngoài có rủi ro giảm nếu nông hộ giảm đàn.
- ⚠️ **Rủi ro trích lập:**
  - Tài sản sinh học ngắn hạn (heo thịt) 1.877,7 tỷ ghi theo giá gốc. TM Q3 ghi giá trị có thể thu hồi bằng đúng giá gốc, không trích lập.
  - Nếu giá heo T11–T12 dưới giá thành (khối tích hợp ~48–55k theo ước lượng của Bobby), Q4 có thể phải trích lập dự phòng. Báo cáo này không ước được quy mô.

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
- Trả trước người bán tăng từ 171,5 lên 459,6 tỷ. Tạm ứng nhân viên ~178 tỷ để giải phóng mặt bằng trại (TM 7.1, H1) là khoản cần theo dõi, nhưng nhỏ so với quy mô.
- **Tồn kho 3.281,6:** nguyên liệu 1.241,9 · dở dang 1.347,9 (trong đó **BĐS dở dang ~1.186 tại 30/6**, TM 8) · thành phẩm 365,6 · hàng hoá 78,6 · hàng đi đường 209,7. 3.020 tỷ tồn kho bị cầm cố cho vay.
- **Tài sản sinh học:** ngắn hạn 1.877,7 (heo thịt); dài hạn 740,0 (heo nái, gà bố mẹ; nguyên giá 727,2, khấu hao luỹ kế 153,9). Ghi theo giá gốc, chi phí phân bổ theo đầu con/ngày nuôi (TM 9, H1), **không đánh giá lại**.
- **XDCB dở dang 1.302,6** (đầu năm 1.750,0):
  - Dự án đã chuyển sang TSCĐ năm 2026: nhà máy ép dầu giai đoạn 2 (1.095,4), nhà máy vaccine (234,0).
  - Đang dở: Lợn Quảng Ninh 360,2 · Nhà máy TACN Nutreco Hà Tĩnh 266,6 · khu chăn nuôi lợn CNC Ngọc Lặc 244,3 · Lào Cai 108,3 · Lam Sơn–Như Xuân 104,1 · Quảng Trị 56,6 · Trung tâm đào tạo Lạc Vệ 81,9 · gà Quảng Ninh 28,0 · khác 52,7.
  - **DBC là một phần của làn sóng mở trại 2026** mà Bobby cảnh báo (§2b sector read). Theo luật, base ghi các dự án này theo giá sổ (NPV=0).
- **CFO 9T 1.517,9** so với LNST 863,3:
  - Trong đó giảm tồn kho +498,6, tăng phải thu −401,5, thu khác 88,0.
  - Không tính phần giải phóng tồn kho thì CFO cốt lõi ~1.020, xấp xỉ 1,2 × LNST.
  - Capex 9T 1.106,0. Gửi thêm tiền HTM 1.276,4 tài trợ bằng vay ròng (+1.837).
- **Ba năm (Q4/23–9T/26):** CFO bình quân 1.133/năm, capex 988/năm, nên FCFE (chưa tính vay ròng) chỉ 146/năm.
- ⚠️ **Dòng tài chính có trình bày gộp:** "thu từ phát hành cổ phiếu 461,8" và "cổ tức đã trả 577,3" thực chất là **cổ tức cổ phiếu 12%** (46,18 tr cp, ghi gộp hai chiều) cộng cổ tức tiền 3% (115,5) cho năm 2025 (TM 25.3, H1). Năm 2026 **không có vốn tiền mới**. 9T/25 cũng vậy (502,0 = cổ tức cổ phiếu 15%).

## 5. Cổ đông, insider, thanh khoản

- 431.046.499 cp (ĐKDN thay đổi 26/09/2026: vốn điều lệ 4.310,46 tỷ; cập nhật địa chỉ sau sáp nhập tỉnh Bắc Ninh và ngành nghề kinh doanh. Tôi chưa giải mã được danh mục ngành nghề vì PDF lỗi font).
- **Insider:** bà Nguyễn Thị Thu Hương (Phó CT HĐQT, Phó TGĐ kiêm Giám đốc tài chính) đăng ký mua 2.000.000 cp (TB 01/10/2026) và **đã mua đủ 2.000.000** (báo cáo 14/10/2026). Sở hữu tăng từ 4.651.360 cp (1,08%) lên 6.651.360 cp (~1,54%).
  - Người mua là **giám đốc tài chính**, người nhìn thấy số Q3 trước công bố 21/10. Đây là tín hiệu tích cực có trọng lượng, nhưng chỉ ~0,46% vốn.
  - Chưa đo giá khớp bình quân.
- **Thanh khoản:** ADV trung vị 3 tháng là **20,08 tỷ/phiên**, trung bình 27,06 (BQ `ticker` 18/08–17/11/2026). Vị thế ≤ 20 tỷ thoát trong ≤ 10 phiên ở mức tham gia 10%.
  - **Chiết khấu thanh khoản 2%** (ước lượng; chưa đo Amihud), độ nhạy 0–5% ⇒ tâm 22.261 / 21.815 / 21.148.
- Room ngoại / free float: **chưa có số** (BQ không có cột; cần DNSE secdef). Chưa kiểm.

## 6. Định giá (MÙ giá thị trường; giá chỉ ở bước so sánh cuối)

### 6a. Khung
- **r = 13,5%.** Lãi huy động 12T hiệu dụng tại điểm neo 03/11 là 7,4%; ngày 18/11 cũng 7,4% (`deposit_rate_vn.effective_deposit_rate`, nguồn CCTG 12T 02/11; Big-4 6,8%). Chênh 0bp nên r giữ 13,5% (β pass-through = 1).
- **g = 5%** (ước lượng: tăng trưởng danh nghĩa dài hạn ngành thịt/TACN, thấp hơn GDP danh nghĩa). Độ nhạy 4–7%.
- **Phương pháp:** thu nhập thặng dư / P/B hợp lý = (ROE − g)/(r − g), áp lên vốn chủ hoạt động; **XDCB dở dang 1.302,6 ghi theo giá sổ (NPV=0)**.
  - ROE chuẩn hoá trên vốn chủ hoạt động = 1.083,3 / (8.720,4 − 1.302,6) = **14,6%**.
  - Moat NARROW nên **không có tham số moat** (không kéo dài fade, không RONIC > Ke). Đồng thời **không trừ** gì thêm.

### 6b. Kịch bản

| | Trọng số | ROE / tổng vốn | ROE / vốn hoạt động | Giá trị/cp | Cơ sở |
|---|---|---|---|---|---|
| Xấu | 25% | 9,0% | 10,6% | 14.320 | TB ROE 2021–2024 (hai năm đáy 2022–23). Đáy heo kéo dài, F3/F8 của Bobby trượt |
| Cơ sở | 50% | 12,4% | 14,6% | 22.466 | LNST trung vị TTM 3 năm |
| Tốt | 25% | 15,5% | 18,2% | 29.791 | TB ROE 2019–2025 gồm siêu chu kỳ ASF 2020 |
| **Tâm** | | | | **22.261 trước / 21.815 sau CK thanh khoản** | |

Vùng sau chiết khấu thanh khoản là [14.034; 29.195]. Ở tâm, P/E chuẩn hoá 8,7 và P/B 1,08.

### 6c. Độ nhạy

| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| Tâm (β = 1) | 24.329 (+11,5%) | 22.994 (+5,4%) | 21.815 | 20.768 (−4,8%) | 19.831 (−9,1%) |
| Tâm (β = 0,5) | 22.994 | 22.387 | 21.815 | 21.277 | 20.768 |

- **g:** 4% ⇒ 21.606 · 6% ⇒ 22.081 · 7% ⇒ 22.428. Ít nhạy vì ROE gần r.
- **Cách đối xử XDCB (lựa chọn phán đoán, đây là điểm yếu số 1):** nếu áp ROE 12,4% lên **toàn bộ** vốn chủ (XDCB cũng chỉ sinh 12,4% < r), kịch bản cơ sở là **17.666** (−21%). Luật 03/11 buộc base ghi dự án theo giá sổ nên base giữ 22.466; 17.666 là cận dưới của cách đọc này.
- **Moat:** NARROW và NONE cho cùng giá trị (luật "không trừ"). WIDE không áp được vì không có bằng chứng.

### 6d. Hai nền + C4/D2 (chỉ hiển thị)

| Nền | Giá trị/cp | Ghi chú |
|---|---|---|
| V_ngắn (LNST chuẩn hoá 1.083 × (1 − g/ROE 12,4%)/(r − g)) | 17.666 | tái đầu tư 40% (< 80%, không bị chặn) |
| V_dài (FCFE = CFO − capex, TB 3 năm 146 tỷ/năm) | 4.177 | capex/CFO = 0,87 |
| **D = \|ln(V_ngắn/V_dài)\| = 1,44 > ln3** | **PHÂN KỲ MẠNH** | FCFE thấp vì đầu tư tăng trưởng (capex: dầu GĐ2, vaccine, 6 dự án trại/TACN), **không đọc là cảnh báo đắt**. Vùng đọc mở rộng: [4.177; 29.195] |
| V theo C4 = CFO3 − min(capex, khấu hao ~667/năm, ước lượng) | 13.372 | chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi |
| V theo D2 = CFO3 − 7,1% × DT (trung vị capex/DT ngành) | 382 | chưa qua tiêu chí khoá trước (0/9 nền qua), chỉ theo dõi. Trung vị ngành 7,1% từ HAG 29%, BAF 40%, MML 2,4%, VLC 5,7%, VSN 1,8%, DBC 8,6%; tập peer nhỏ và lệch nên không đáng tin |

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
- Giá 16.950 (17/11) bằng **0,78 × tâm**, nằm trong vùng [14.034; 29.195].
- Giá ≈ V_ngắn (17.666) và ≈ kịch bản "toàn vốn ROE 12,4%". Như vậy **thị trường đang định giá DBC đúng ở mức LNST chuẩn hoá không có phần bù cho XDCB**.
- Phần chênh với tâm đến từ (i) cách đọc NPV=0 cho dự án mới và (ii) kịch bản tốt có trọng số 25%.

## 7. Pháp lý / quản trị / chính sách — chỉ WARNING

- **Kiểm toán:**
  - EY soát xét BCTC bán niên 2026 với kết luận chấp nhận toàn phần, không ngoại trừ, không nhấn mạnh (trang 5 `h1_d`).
  - Có trình bày lại số đầu kỳ theo Thông tư 99/43 (TM 37). Đây là phân loại lại: HTM ngắn hạn, tài sản sinh học tách khỏi tồn kho. Không đổi lợi nhuận.
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
- **⇒ moat_tier = NARROW, moat_type = COST/INTEGRATION; rủi ro số 1 = chu kỳ giá heo + ASF lọt trại nái.** Không thưởng tham số moat (§6a).
- **Đề xuất dòng `moat_tags.csv` (KHÔNG sửa file):**
  `DBC,NARROW,COST/INTEGRATION,-,"Hog-price cycle (±5k VND/kg ≈ ±50-60% normalized NPAT, upper-bound est.) + ASF in sow farms; ROE_Min5Y 0.5%/ROIC_Min5Y 2.3% => no through-cycle excess return; partial input self-supply via 2026 soybean-crush plant",2026-11-18,dd_DBC_20261118,N`

## 9. Mốc khoá trước — điều kiện đổi nhận định THEO CẢ HAI CHIỀU

| Mốc | Ngày chấm | Hướng tăng (tâm ↑ / trọng số tốt ↑) | Hướng giảm (tâm ↓ / trọng số xấu ↑) |
|---|---|---|---|
| BCTC Q4/26 | ≤ 30/01/2027 | LNST Q4/26 ≥ 120 tỷ, không trích lập tài sản sinh học | LNST Q4/26 < −50 tỷ **hoặc** trích lập tài sản sinh học/tồn kho > 100 tỷ ⇒ trọng số xấu 35% |
| Bobby F1 (giá heo T1/27 ≥ 55k) | 05/02/2027 | đúng và ≥ 65k (F2) ⇒ trọng số tốt 35% | < 50k ⇒ trọng số xấu 35% |
| BCTC Q1/27 | ≤ 30/04/2027 | LNST Q1/27 ≥ 300 tỷ **và** biên gộp công ty mẹ ≥ 8,5% (biên TACN mở) | LNST Q1/27 < 150 tỷ |
| Bobby F8 (đàn cuối T3/27 ≤ +3% YoY) | 15/04/2027 | đúng ⇒ chu kỳ tự sửa | sai (≥ +4%) ⇒ đáy kéo dài, trọng số xấu 40% |
| Bảng cân đối Q4/26–Q2/27 | theo BCTC | ND/E ≤ 0,35 khi XDCB vào vận hành | ND/E > 0,6 **hoặc** phát hành tăng vốn tiền mặt dưới BVPS ⇒ WARNING tăng vốn |
| Lãi huy động 12T hiệu dụng | liên tục | giảm ≥ 50bp ⇒ +5,4% | tăng ≥ 50bp ⇒ −4,8% |
| TTM ROE | Q2/27 | TTM LNST ≥ 1.200 tỷ qua đáy ⇒ nâng ROE cơ sở | TTM LNST < 600 tỷ tại Q2/27 ⇒ cơ sở về 9–10% (tâm ~17–18k, ước lượng) |

## 10. Điểm yếu của chính báo cáo / việc còn mở

1. **Cách đọc XDCB (NPV=0) và ROE trên vốn hoạt động** đẩy tâm cao hơn 21% so với cách "toàn vốn". Skeptic nên tấn công điểm này đầu tiên.
2. **Không có số vận hành** (đàn nái, heo xuất chuồng, giá thành/kg, sản lượng TACN bán ngoài). Độ nhạy giá heo là cận trên ước lượng. Cần BCTN 2025 hoặc tài liệu ĐHĐCĐ.
3. **Chưa đọc BCTC kiểm toán năm 2025.** Số năm lấy từ BQ (đã khớp các mốc kiểm được ở §1). Chưa tìm trên `dabaco.vn/quan-he-co-dong/page/2/`.
4. LNTT bộ phận bị méo bởi loại trừ cổ tức nội bộ (−764 tỷ), nên không tách được lợi nhuận thật theo mảng. Dầu thực vật và trại chưa tách được Q3.
5. Định nghĩa khấu hao lệch giữa H1 (gồm tài sản sinh học, 479,7) và 9T (562,0, Q3 suy ra chỉ 82). C4 dùng khấu hao ước lượng ~667/năm.
6. **Lộ giá trong phiên:** truy vấn so sánh peer (§6e) trả về giá DBC trước khi tôi chạy mô hình. Tham số mô hình (ROE, r, g, trọng số) đặt theo BCTC/BQ và luật skill, không suy từ giá. Tôi khai minh bạch ở đây.
7. Chưa có room ngoại/free float; chưa đo Amihud. Chiết khấu thanh khoản 2% là ước lượng.
8. Q4/26 ước lượng dựa trên đường giá heo của Bobby. Bobby tự khai không hoàn toàn mù (§0 sector read: thấy tiêu đề tin "lãi quý 3 giảm sâu").

## 11. Nguồn
- `src/q3_hopnhat.pdf`: BS trang 2–4, KQKD trang 5, LCTT trang 6–7, TM trang 12–23, giải trình 518/CV-DBC trang 24.
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

## 12. Ghi sổ giá (CHỜ skeptic)
Chưa ghi `kb/dd_price_zones.json`. Khi ghi: `center 21815`, `zone [14034, 29195]`, `assumptions_file model/assumptions_DBC_20261118.json`, `assumptions_md5 511073ce713239e5cf7d242491d07922`. Không ghi `v_short`/`v_long`/`D` (luật 11/11). Sửa giả định sau khi ghi sổ thì phải thêm `rev` mới.

## Phụ lục E — Đính chính của fundamental-skeptic
(Chưa chạy. Mike gọi `Agent(subagent_type="fundamental-skeptic")` với đường dẫn REPORT này.)
