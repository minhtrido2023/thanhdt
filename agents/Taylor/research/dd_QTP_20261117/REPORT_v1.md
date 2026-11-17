# DD — QTP (CTCP Nhiệt điện Quảng Ninh, UPCOM) · 2026-11-17 · job `Taylor_20261117_035339`

> Chỉ NGHIÊN CỨU — không đặt lệnh, không wire, chưa ghi `dd_price_zones.json` (Mike làm sau skeptic).
> Nguồn chính = BCTC GỐC tải từ website công ty (`src/`, 14 PDF). BQ chỉ để đối chiếu + chuỗi lịch sử quý.
> Mô hình: `model/qtp_model.py` (md5 `d5f32105429be149298a2479fe07447f`), output `model/qtp_model_out.txt`.
> Định giá MÙ giá thị trường: giá 10.300đ (16/11) chỉ dùng ở mục 0/6 để so, không đi vào mô hình.
> Sector read (Bobby, MÙ): `kb/data_registry/market-state/sector_read_nhiet_dien_than_20261117.md`.

## 0. Kết luận

- **Q3/2026 LNST 75,7 tỷ là MÙA VỤ, không phải gãy.** Q3 năm nào cũng là đáy (Q3/23 11,6 · Q3/24 76,1 · Q3/25 33,0 tỷ). So cùng kỳ năm trước, Q3/26 **tăng 129%**. So Q2 thì giảm vì mùa mưa (thuỷ điện được ưu tiên huy động). Biên gộp Q3 chỉ 3,3%, trong khi 9T là 8,3%.
- **2025 bị phồng bởi một khoản một lần:** doanh thu chênh lệch tỷ giá **663 tỷ** (giải trình 458/NĐQN-TCKT). Trừ lỗ tỷ giá 71,3 tỷ và thuế 20% thì còn **≈473 tỷ sau thuế**. LNST 2025 sau khi loại khoản này ≈ **562 tỷ**, không phải 1.035,9 tỷ.
- **LNST chuẩn hoá** (trung vị TTM 12 quý, đã loại FX, quy thuế về 20%) = **565 tỷ** (EPS ≈ **1.257đ**). TTM Q3/26 sau điều chỉnh = 766 tỷ, cao hơn vì khấu hao giảm và năm El Niño huy động than mạnh. Phần cao hơn này **chưa được coi là bền**.
- **Giá trị nội tại** (DCF FCFE vòng đời HỮU HẠN tới 2047, r = 13,5%, 3 kịch bản có trọng số):
  - **Trước chiết khấu thanh khoản: 14.500đ/cp** (xấu 10.600 / cơ sở 14.800 / tốt 17.800).
  - **Sau chiết khấu thanh khoản 10%: ≈13.050đ/cp**, vùng **9.550–16.030**.
  - Kiểm chéo bằng bội số peer (PE 7–8,5× EPS hoạt động + tiền ròng): **11.300–12.900**, thấp hơn DCF khoảng 10–20%.
- **So giá 10.300đ:** bằng 0,79× tâm sau chiết khấu, tức **dưới ngưỡng 0,85× tâm (11.090)** theo mô hình DCF. Nếu neo theo bội số peer thì biên an toàn mỏng hơn (giá ≈ 0,80–0,91× của 11.300–12.900).
- **Nhãn:** RẺ theo DCF, RẺ VỪA theo bội số. Đây không phải đề xuất mua (mua do user duyệt từng tranche).
- **Giả thuyết "sạch nợ, cổ tức cao, bond-proxy" — NỬA ĐÚNG:**
  - Sạch nợ: đúng tại 30/9/2026, nhưng sắp vay **2.787,9 tỷ** cho dự án xử lý khí thải (QĐ 917, giai đoạn 2027–29).
  - Cổ tức cao: đúng, nhưng mức 1.000đ + 700đ trong 12 tháng được nuôi bởi năm có khoản FX một lần. Mức bền ước ≈ 900–1.000đ/năm **(ước lượng)**, tương đương DY 8,7–9,7% trên giá 10.300.
  - "Bond-proxy": là trái phiếu **trả dần gốc, có kỳ hạn** (đất thuê tới 2047), không phải trái phiếu vĩnh viễn. Ngoài ra **52% vốn chủ là khoản phải thu một bên duy nhất là EVN/EPTC** (3.089,6 tỷ).
- **Yếu tố pháp lý — WARNING, không chặn:** dự thảo PDP8 (2025) nêu "Quảng Ninh" trong nhóm ~4.500 MW **không chuyển đổi, dừng khi đủ 40 năm tuổi**. Với QTP, mốc 40 năm rơi vào khoảng 2049–2054, sau mốc 2047 mô hình đã dùng. Văn bản cuối QĐ 768 chưa đọc được bản gốc. Xem mục 7.

## 1. Đối chiếu số Mike đọc từ BQ với BCTC gốc

| Chỉ tiêu | BQ (Mike) | BCTC gốc | Khớp? |
|---|---|---|---|
| Doanh thu Q3/26 | 2.814,6 | 2.814.645 tr (KQKD Q3) | ✅ |
| Doanh thu Q3/25 | ~2.056 | 2.056.385 tr | ✅ |
| LNST Q3/26 | 75,7 | 75.680,9 tr; giải trình 2018/NĐQN-TCKT 21/10/2026 | ✅ |
| LNST Q2/26 | 326,6 | H1 523,8 (giải trình 1519) − Q1 197,2 = 326,6 | ✅ |
| LNST Q4/25 | 639,7 | FY25 1.035,9 − 9T25 396,2 = 639,7 | ✅ |
| GPM_P0 ≈ 14% | là số TTM | 9T26 8,3%; Q3 3,3%; FY25 14,0% (có FX 663) | ⚠️ 14% chứa khoản FX một lần |
| "Sạch nợ" | — | Vay 0 tại 30/9/26; trả 100 tỷ gốc cuối cùng trong 2025 | ✅ (xem mục 4) |

- QTP **không có công ty con** (TM I Q3/26), nên BCTC riêng = BCTC hợp nhất.
- Kiểm toán FY2025: UHY, ý kiến **chấp nhận toàn phần**, **không có đoạn nhấn mạnh**. "Vấn đề khác" chỉ nói FY2024 do một công ty kiểm toán khác thực hiện (đổi kiểm toán viên).

## 2. Chất lượng lợi nhuận

### 2a. Q3/26 so Q2/26 và so cùng kỳ (BCTC gốc, tỷ đồng)

| | Q3/26 | Q3/25 | 9T26 | 9T25 |
|---|---|---|---|---|
| Doanh thu | 2.814,6 | 2.056,4 | 9.173,3 | 7.832,6 |
| Lợi nhuận gộp | 93,1 (3,3%) | 64,2 (3,1%) | 764,4 (8,3%) | 571,0 (7,3%) |
| Doanh thu tài chính (gần như toàn bộ là lãi tiền gửi) | 25,7 | 8,0 | 59,6 | — |
| Chi phí QLDN | 23,2 | 27,6 | 71,2 | 76,2 |
| LNTT | 94,7 | 41,3 | 749,7 | 495,5 |
| LNST | 75,7 | 33,0 | 599,5 | 396,2 |
| Khấu hao | 104,5 | 136,8 | 329,2 | 412,7 |

- **Q3 thấp so Q2 là mùa vụ:** mùa mưa ưu tiên thuỷ điện, biên gộp Q3 là thấp nhất năm (Q3/25 3,1% · Q3/26 3,3%).
  - Lịch đại tu/sửa chữa lớn theo quý không có trong BCTC quý. Năm 2025 chi phí sửa chữa lớn là 294,5 tỷ (TM26 FY25), hạch toán vào chi phí → **cần kiểm** có dồn vào Q3 không.
- **Cơ cấu chi phí Q3/26:** nhiên liệu/vật liệu 2.387,8 tỷ = **87%** tổng chi phí (TM VII.10). Nhiên liệu là phần pass-through, nên biên tuyệt đối chủ yếu đến từ giá cố định của PPA.
- **Khấu hao đang giảm dần — động lực cấu trúc của tăng trưởng 2026:**
  - Nguyên giá TSCĐ hữu hình 21.074,9 tỷ, đã khấu hao 19.271,5 tỷ (**91,4%**), giá trị còn lại 1.805,1 tỷ (BCĐKT 30/9/26).
  - Khấu hao 9T26 thấp hơn cùng kỳ 83,5 tỷ, trong khi lợi nhuận gộp tăng 193,4 tỷ. Phần còn lại ~110 tỷ đến từ sản lượng (El Niño, nhu cầu điện miền Bắc).
- **Khoản một lần năm 2025:** doanh thu chênh lệch tỷ giá 663 tỷ (giải trình FY25) và lỗ tỷ giá 71,3 tỷ (TM24 FY25: 69,0 + 2,2).
  - Sau thuế: **473,4 tỷ**, gán vào Q4/25 **(ước lượng: Q4/25 639,7 so Q4/24 154,8)**.
  - Nợ vay ngoại tệ đã hết từ 2025, nên **không mô hình hoá thêm khoản FX nào**. Nếu EVN duyệt thêm chênh lệch tỷ giá các năm cũ thì đó là upside (Bobby: EVN còn ~17.500 tỷ chưa phân bổ ở cấp toàn hệ thống).
- **Thuế suất:** 2024 hiệu dụng 10,1% (69,2/688,5), 2025 trở đi 20% (giải trình FY25: hết ưu đãi). Mọi quý 2023–24 được quy về thuế 20% (hệ số 0,8/0,9; **giả định 2023 cũng ~10% — ước lượng**).

### 2b. Chuẩn hoá lợi nhuận (`model/qtp_model.py`)

- TTM điều chỉnh, 12 điểm từ Q4/23 đến Q3/26 (tỷ): 546 · 620 · 543 · 600 · 550 · 522 · 568 · 534 · 563 · 587 · 723 · 766.
- **Trung vị = 565,5 tỷ** (EPS 1.257đ). TTM thô 1.239,2 tỷ (EPS 2.754đ) — chính con số thô này làm BQ cho PE = 3,7× và DY = 16,5% trông rẻ một cách giả tạo.
- **Lợi nhuận hoạt động** (bỏ phần lãi tiền gửi trên tiền ròng, để không đếm hai lần với tiền ròng cộng riêng): 565,5 − 61,7 = **503,8 tỷ**. Lãi 5%/năm × 1.541 tỷ × 0,8 là **ước lượng**.

## 3. Cơ chế giá PPA, thị trường điện, than, tỷ giá — đã biết và chưa biết

| Mục | Kết quả |
|---|---|
| Giá cố định PPA sau khi hết khấu hao/trả nợ | **CHƯA CÓ SỐ.** BCTC không thuyết minh PPA. Bằng chứng gián tiếp: 2026 khấu hao giảm và chưa thấy doanh thu/biên bị cắt tương ứng (biên gộp 9T tăng). ⇒ Đây là **biến lớn nhất** của mô hình, xử lý bằng kịch bản (mục 6). |
| Sản lượng hợp đồng (Qc) 2027, tỷ lệ tham gia thị trường điện, FMP | Không có trong BCTC. Bobby: Qc than 2026/2027 "không có số", thiếu nguồn miền Bắc 2027 4.256 MW ⇒ huy động tối đa mùa khô 2027 rất khả dĩ. |
| Giá than / than nhập | Không có trong BCTC. Ngành: TKV phải pha than nhập. Rủi ro thật là chất lượng than so với thiết kế lò, không phải giá (vì giá than pass-through). |
| Tỷ giá với EVN | Nợ ngoại tệ = 0. Đã ghi nhận 663 tỷ năm 2025. Số dư chênh lệch tỷ giá còn phải thu: **không thuyết minh riêng** ⇒ cần hỏi IR. |
| Thuế | 20% từ 2025, hết ưu đãi. |

## 4. Bảng cân đối và dòng tiền [BCTC 30/9/2026]

| | Tỷ đồng | đ/cp |
|---|---|---|
| Tiền | 82,2 | |
| Tiền gửi giữ đến đáo hạn ngắn hạn (mã 123) | 1.774,1 | |
| Vay ngắn + dài hạn | **0** | |
| Tạm ứng cổ tức 2026, 700đ (ĐKCC 06/11, trả 27/11) — trừ trước | −315,0 | |
| **Tiền ròng thật** | **1.541,3** | **3.425** |
| Phải thu khách hàng (EPTC 3.089,6) | 3.091,5 | 6.870 |
| Phải thu khác (đã trích dự phòng 188,7 tỷ — khoản cũ, không đổi so đầu năm) | 190,8 | |
| Hàng tồn kho (chủ yếu than/vật tư) | 729,3 | |
| Tổng nợ phải trả (không có vay) | 1.578,5 | |
| Vốn chủ sở hữu | 5.984,7 | BVPS **13.299** |

- **Dòng tiền kinh doanh (CFO) 9T26: 707,7 tỷ** (9T25: 1.168,7). Thấp hơn chủ yếu do nộp thuế TNDN 291 tỷ (khoản thuế của năm FX 2025) và phải trả giảm 157,8 tỷ.
  - Phải thu giảm 220,6 tỷ (EPTC trả bớt).
  - CFO theo năm (BQ, đã khớp quý): 2024 1.200 · 2025 1.706 · TTM 1.244 tỷ.
- **Đầu tư TSCĐ 9T26 chỉ 5,0 tỷ.** Sửa chữa lớn được hạch toán vào chi phí nên capex duy trì rất thấp. Mô hình dùng 15 tỷ/năm **(ước lượng)**.
- **Kỳ thu tiền EPTC:**
  - 3.089,6 tỷ ≈ **~100 ngày** doanh thu Q3 (2.814,6 tỷ/quý). Đầu năm là 3.211,4 tỷ.
  - Không thuyết minh nợ quá hạn, không trích dự phòng.
  - Rủi ro là **kéo dài** kỳ thu tiền (EVN bị ép biên 2026–27 — Bobby), không phải mất trắng.
- **Dự án nâng cấp hệ thống xử lý khí thải:**
  - Hợp đồng EPC (QĐ 1710): **~89,2 triệu USD + 901,8 tỷ VND**; thời gian 38 tháng. OCR đọc được hai số USD, 89.156.813 và 89.756.813 — cần đối chiếu bản gốc.
  - Khoản vay (QĐ 917, 15/6/2026): **2.787,9 tỷ = 80% tổng mức đầu tư trước VAT** ⇒ tổng mức đầu tư ≈ **3.485 tỷ**, phần vốn chủ ≈ 697 tỷ.
  - Nhà tài trợ vốn đã được xếp hạng (QĐ 21/9/2026): liên danh ngân hàng, BIDV, Vietcombank.
  - **Luật 03/11 — NPV = 0 trong base:** vốn bỏ ra = tài sản theo giá vốn, không trừ giá trị. Dự án mang tính tuân thủ môi trường.
  - Nếu EVN không cho đưa chi phí này vào giá cố định thì đó là rủi ro CỤ THỂ, nhưng **chưa có cơ sở dữ liệu** ⇒ chỉ là độ nhạy: −697 tỷ vốn chủ ≈ **−1.550đ/cp** nếu mất trắng toàn bộ phần vốn chủ; mức này là cực đoan, không đưa vào base.
  - Tác động dòng tiền: phần vốn chủ ~230 tỷ/năm trong 2027–29 **(ước lượng)**, có thể làm giảm payout.

## 5. Cổ tức, cổ đông, room

- **Cơ cấu cổ đông** (TM19.2 FY25):
  - EVNGENCO1: **42,0%**
  - Nhiệt điện Phả Lại (PPC — cũng thuộc hệ GENCO1): 16,35%
  - SCIC: 11,42%
  - Điện lực TKV: 10,62%
  - Cổ đông khác: **19,6%** — đây là free float thực tế.
  - Có CBTT GENCO1/EEMC/QTP thoái vốn tại NPS: đó là QTP **bán** phần vốn ở công ty khác, không phải bán cổ phần QTP.
- **Cổ tức tiền mặt:**
  - 2024 chia 787,5 tỷ (1.750đ, TM19.3 FY25).
  - 2025 chỉ ghi "cổ tức đã chia" 90 tỷ trong năm.
  - Tạm ứng cổ tức 2025 là 10% (1.000đ), chi trong 9T26: 449,3 tỷ theo LCTT; báo chí ghi ~450 tỷ.
  - **Tạm ứng 2026: 7% (700đ)**, ĐKCC 06/11/2026, trả từ 27/11/2026 (thông báo 09/11/2026).
- **DY:**
  - Trailing (1.700đ) / 10.300 = **16,5%** — phồng do năm 2025 có FX.
  - Mức bền: payout ~75–80% × EPS chuẩn hoá 1.257 ≈ **900–1.000đ** **(ước lượng)** ⇒ **8,7–9,7%**.
  - 2027–29 có thể thấp hơn do phải góp vốn chủ cho dự án khí thải.
- **Room ngoại:** không tìm thấy trong tài liệu đã tải ⇒ "cần kiểm chứng". Với free float 19,6% thì room trên thực tế không phải ràng buộc chính.

## 6. Định giá (MÙ giá thị trường)

**Chi phí vốn:** r = **13,5%**, đúng điểm neo. Lãi huy động 12T hiệu dụng `deposit_rate_vn.effective_deposit_rate('2026-11-17')` = **7,40%** (CCTG 12M 02/11) — bằng mức neo 03/11 nên không điều chỉnh. β pass-through = 1.

**Vòng đời hữu hạn:**
- Dòng tiền 2027–2047, mốc là hết hạn hợp đồng thuê đất chính 15/3/2047 (TM20 FY25).
- Cuối kỳ: thu hồi vốn lưu động ròng 2.259 tỷ (chiết khấu về hiện tại), giá trị nhà máy = 0.
- Không dùng tăng trưởng vĩnh viễn (g_T).

**Khấu hao còn lại:** 1.805 tỷ, chạy với tốc độ hiện tại 418 tỷ/năm, giảm dần, hết khoảng 2031 **(ước lượng)**.

**Moat:** NARROW, nên không thưởng tham số moat và cũng không trừ (mục 8).

**Ba kịch bản:**

| Kịch bản | Giả định chính | đ/cp | Trọng số |
|---|---|---|---|
| **Xấu** | LN hoạt động 85% chuẩn hoá trong 2027; **50% từ 2028** (ETS bắt buộc không được pass-through + Qc bị cắt + giá cố định bị ép); **dừng 2040** (không chuyển đổi được) | **10.614** | 0,25 |
| **Cơ sở** | LN hoạt động **phẳng danh nghĩa 503,8 tỷ** tới 2047; giá cố định PPA **giảm đúng bằng khấu hao đã hết** (khấu hao chỉ là dòng tiền thu hồi phần còn lại) | **14.796** | 0,50 |
| **Tốt** | Giá cố định PPA **không giảm** sau khi hết khấu hao ⇒ giữ EBITDA; khấu hao tiết kiệm được chuyển thành lợi nhuận (×0,8 sau thuế) | **17.814** | 0,25 |
| **Có trọng số, trước chiết khấu thanh khoản** | | **14.505** | |

**Độ nhạy theo lãi huy động** (r di chuyển 1:1):

| Lãi huy động | Giá trị (đ/cp) | Thay đổi |
|---|---|---|
| −100bp | 15.092 | +4,0% |
| −50bp | 14.791 | +2,0% |
| +50bp | 14.234 | −1,9% |
| +100bp | 13.977 | −3,6% |

Độ nhạy thấp vì dòng tiền ngắn và tiền ròng lớn.

**Chiết khấu thanh khoản:**
- Cơ sở dữ liệu (BQ `ticker`, 63 phiên từ 15/8 đến 16/11/2026): ADV trung vị **1,22 tỷ/phiên** (113,9k cp), trung bình 1,60 tỷ, không có phiên nào khối lượng 0; free float 19,6%.
- Ở mức tham gia 15% ADV (0,18 tỷ/phiên): vị thế 1 tỷ thoát trong ~5,5 phiên; 3 tỷ thoát trong ~16 phiên.
- Mức chiết khấu chọn **10%** **(ước lượng)**:

| Chiết khấu | Giá trị (đ/cp) |
|---|---|
| 5% | 13.780 |
| **10% (chọn)** | **13.055** |
| 15% | 12.329 |

- Quy mô vị thế áp dụng: **≤0,5% NAV và ≤~2 tỷ** (~11 phiên để thoát).

**Hai nền giá trị + cờ phân kỳ (chỉ hiển thị):**
- **V_ngắn** = LNST chuẩn hoá 565,5 / r, với g = 0 (ROE chuẩn hoá 9,4%, tái đầu tư = 0) = **9.308đ**.
- **V_dài** = DCF FCFE kịch bản cơ sở = **14.796đ**.
- **D = 0,463 < ln2** ⇒ không bật cờ. V_ngắn thấp hơn vì không tính riêng tiền ròng 3.425đ/cp và khấu hao còn lại.
- **Dòng C4** (CFO3 1.305 − min(capex, khấu hao) = 1.290 tỷ/năm): 21.034đ (hữu hạn tới 2047) — **"chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi"**. Con số này phồng vì CFO3 gồm năm FX 2025 và cộng lại khấu hao vốn sẽ biến mất.
- **Dòng D2:** **không tính** — không có capex/doanh thu trung vị ngành sạch (`CF_Invest` trong BQ trộn lẫn tiền gửi).

**Bội số — kiểm chéo, không phải tâm:**
- Peer (BQ `ticker` 16/11, TTM thô chưa chuẩn hoá):

| Mã | PE | PB | Ghi chú |
|---|---|---|---|
| PPC | 8,9 | 0,58 | |
| HND | 8,5 | 0,67 | |
| NBP | 5,1 | 0,43 | |
| POW | 5,6 | 0,85 | |
| NT2 | 4,7 | 1,26 | |
| BTP | 7,6 | 0,38 | |
| QPH | 8,3 | 1,68 | thuỷ điện |
| VSH | 11,4 | 1,97 | thuỷ điện |

- Trung vị nhiệt điện than (PPC/HND/NBP): PE ~8,5, PB ~0,58.
- PE 7–8,5 × EPS hoạt động (1.120) + tiền ròng 3.425 ⇒ **11.262–12.942**.
- PB 0,6–0,7 × BVPS 13.299 ⇒ **7.980–9.310**. Đây là cận dưới: PB peer phản ánh ROE thấp (ROE_Min3Y PPC 3,8%, HND 4,5%), còn QTP 10,7%.

**Tâm và vùng (sau chiết khấu thanh khoản 10%):** tâm **13.050**, vùng **9.550 (xấu) – 16.030 (tốt)**, ngưỡng 0,85× tâm = **11.090**.

**So với giá 10.300đ (16/11):**
- Giá ≈ 0,79× tâm, nằm dưới ngưỡng 0,85× tâm.
- Nếu tin bội số peer hơn DCF thì giá ≈ 0,80–0,91× ⇒ biên an toàn có nhưng mỏng.
- Giá đã trừ quyền tạm ứng 700đ (ĐKCC 06/11).

## 7. Pháp lý / quản trị / chính sách — chỉ WARNING

- **PDP8 — kiểm lời cảnh báo của Bobby:**
  - Dự thảo điều chỉnh PDP8 (2025, nguồn báo chí cấp 2 — chưa đọc được văn bản gốc) liệt kê "Phả Lại II, Hải Phòng, **Quảng Ninh**, Na Dương I, Sơn Động, Uông Bí, Formosa Đồng Nai, VeDan" (~4.500 MW) là nhóm **không chuyển đổi nhiên liệu, dừng sau 40 năm tuổi thọ**. Tức là "dừng khi đủ 40 năm", **không phải dừng ngay sau 2030**.
  - Tên "Quảng Ninh" ~1.200 MW khớp với QTP.
  - Năm COD từng tổ máy **chưa kiểm văn bản gốc** (BCTC không ghi). Kiến thức nền: tổ 1–2 khoảng 2009–2011, tổ 3–4 khoảng 2013–2014 **(ước lượng)** ⇒ mốc 40 năm ~2049–2054, **sau** mốc 2047 của mô hình.
  - Rủi ro thật là ngược lại: nhà máy hiệu suất thấp bị điều độ ít hơn khi LNG/tái tạo vào (sau 2028 — Bobby) ⇒ đã nằm trong kịch bản xấu.
  - QĐ 768/QĐ-TTg (15/4/2025) đã ký, nhưng danh sách từng nhà máy trong bản cuối **chưa xác minh**.
- **ETS:** thí điểm, cấp hạn ngạch miễn phí 100% cho 2025–26; bắt buộc từ 2028; PPA cũ chưa có điều khoản pass-through ⇒ đã đưa vào kịch bản xấu.
- **Quản trị:** cổ đông nhà nước chi phối (~80%), cổ tức đều đặn. Không thấy khởi tố hay xử phạt trong các CBTT 2026 đã đọc (bổ nhiệm phó TGĐ, đổi địa chỉ/mẫu dấu, mất sổ cổ đông). Đổi kiểm toán viên từ FY2025 là bình thường đối với DNNN.

## 8. Vị thế và lợi thế cạnh tranh (5F) — TÁI DÙNG

- Nguồn: `data/moat_tags.csv`, QTP = **NARROW, REGULATORY/COST**, rào cản gia nhập H, asof 2026-06-05 (<12 tháng). Không làm lại.
  - Rủi ro số 1: EVN độc quyền mua, giới hạn lợi suất PPA; PDP8 không cho than mới ⇒ lợi suất có kỳ hạn và giảm dần.
- **Kiểm nhanh có gì đổi hào:**
  - (i) Tính đến 30/9/2026, ROIC/ROE chuẩn hoá ~9–10% (565/5.985), thấp hơn mức "12–16%" trong tag (tag tính trên TTM có FX).
  - (ii) Chính sách ngành nghiêng ủng hộ than (BCT đề xuất 5.300 MW than mới, thiếu nguồn 2027) nhưng không đổi cơ chế PPA một người mua ⇒ **không đổi hào**.
  - Đề xuất (không sửa file): ghi chú lại "durable ROIC" của tag thành ~9–10% sau khi loại FX một lần.
- NARROW ⇒ mô hình **không thêm tham số moat**. Độ nhạy theo moat không áp dụng; độ nhạy theo cơ chế PPA chính là kịch bản tốt/xấu.

## 9. Mốc khoá trước — điều kiện đổi nhận định THEO CẢ HAI CHIỀU

| Mốc (ngày chấm) | Đổi lên | Đổi xuống |
|---|---|---|
| BCTC Q4/26 + năm 2026 (~21/01/2027 và 03/2027) | LNST 2026 (không có FX mới) ≥ **750 tỷ** và biên gộp Q4 ≥ Q4/25 trừ FX ⇒ tăng trọng số "tốt" (khấu hao giảm mà PPA không bị cắt) | LNST 2026 trừ FX < **620 tỷ** ⇒ "cơ sở" là trần |
| Doanh thu/biên Q1–Q2/2027 | Sản lượng tăng và biên tăng | **Biên gộp giảm so cùng kỳ trong khi sản lượng tăng** ⇒ dấu hiệu giá cố định PPA bị cắt ⇒ tăng trọng số "xấu" |
| Phải thu EPTC (31/12/2026, 31/3/2027) | < 2.500 tỷ ⇒ dòng tiền về tốt | > **3.800 tỷ** (>120 ngày) ⇒ chiết khấu thêm, xem lại cổ tức |
| Cổ tức 2026 cả năm (ĐHĐCĐ 04/2027) | ≥ 1.200đ | < **800đ** ⇒ hạ DY bền xuống ~7% |
| PDP8 / văn bản lịch dừng (Bobby F12, 2027-12-31) | Danh sách cuối không có QN, hoặc cho chuyển đổi/gia hạn | Lịch dừng QTP **trước 2047** ⇒ rút ngắn vòng đời |
| Thêm doanh thu chênh lệch tỷ giá (văn bản EVN) | Có ⇒ cộng giá trị một lần | — |
| Vượt dự toán dự án khí thải / EVN không đưa vào giá | — | Có số cụ thể ⇒ chuyển phần vốn chủ ~697 tỷ sang kịch bản tiêu cực |

## 10. Việc còn mở / cần kiểm chứng

1. PPA: thời hạn, lịch giá cố định sau khi hết khấu hao — hỏi IR hoặc đọc BCTN.
2. Qc 2027 và FMP — đợi kế hoạch vận hành 2027 của BCT (Bobby F13).
3. Năm COD từng tổ máy.
4. Số USD chính xác của hợp đồng EPC.
5. Số dư chênh lệch tỷ giá còn phải thu từ EVN.
6. Room ngoại.
7. Văn bản gốc QĐ 768 (danh sách nhà máy).
8. Báo cáo môi giới (ACBS/DSC/BSC) chưa đọc, không cần cho kết luận.

## 11. Nguồn

- **Website công ty** (`tpcquangninh.com.vn` → file ở `quangninhtpc.com.vn/userfile/...`), lưu tại `src/`:
  - `q3_2026_bctc_giaitrinh.pdf` (BCTC Q3/26 + giải trình 2018/NĐQN-TCKT)
  - `fy2025_kt_vi.pdf` (kiểm toán UHY 271/2026) + `fy2025_giaitrinh.pdf`
  - `h1_2026_soatxet_en.pdf` + `h1_2026_giaitrinh.pdf`
  - BCTC Q1/26, Q2/26, Q3/25, Q4/25
  - `div_tamung_2026.pdf`
  - `epc_khithai_qd1710.pdf`, `vay_khithai_qd917.pdf`, `vay_khithai_xephang.pdf`
  - `codong_nhanuoc.pdf`
- **BQ:**
  - `tav2_bq.ticker_financial` QTP 2018Q4–2026Q3 (đã khớp BCTC gốc)
  - `tav2_bq.ticker` (giá/ADV đến 16/11/2026; multiple peer)
  - `deposit_rate_vn.effective_deposit_rate('2026-11-17')` = 7,40%
- **Báo chí (cấp 2, chỉ bối cảnh):**
  - Tạm ứng cổ tức 2025 10%: baophapluat.vn
  - Dự thảo PDP8, danh sách ~4.500 MW: baolaocai.vn / VnEconomy, theo tóm tắt kết quả tìm kiếm
