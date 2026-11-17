# DD — QTP (CTCP Nhiệt điện Quảng Ninh, UPCOM) · 2026-11-17 · job `Taylor_20261117_035339` · **VÒNG 2** (`Taylor_20261117_041718`, áp đính chính fundamental-skeptic; bản cũ = `REPORT_v1.md`)

> Chỉ NGHIÊN CỨU — không đặt lệnh, không wire, chưa ghi `dd_price_zones.json` (Mike làm sau skeptic).
> Nguồn chính = BCTC GỐC tải từ website công ty (`src/`, 14 PDF). BQ chỉ để đối chiếu + chuỗi lịch sử quý.
> Mô hình: `model/qtp_model.py` (r2; bản r1 = `qtp_model_v1.py`), output `model/qtp_model_out.txt`.
> Định giá MÙ giá thị trường: giá 10.300đ (16/11) chỉ dùng ở mục 0/6 để so, không đi vào mô hình.
> Sector read (Bobby, MÙ): `kb/data_registry/market-state/sector_read_nhiet_dien_than_20261117.md`.

## 0. Kết luận

- **Q3/2026 LNST 75,7 tỷ là MÙA VỤ, không phải gãy.** Q3 năm nào cũng là đáy (Q3/23 11,6 · Q3/24 76,1 · Q3/25 33,0 tỷ). So cùng kỳ năm trước, Q3/26 **tăng 129%**. So Q2 thì giảm vì mùa mưa (thuỷ điện được ưu tiên huy động). Biên gộp Q3 chỉ 3,3%, trong khi 9T là 8,3%.
- **2025 bị phồng bởi một khoản một lần:** doanh thu chênh lệch tỷ giá **663 tỷ** (giải trình 458/NĐQN-TCKT). Trừ lỗ tỷ giá 71,3 tỷ và thuế 20% thì còn **≈473 tỷ sau thuế**. LNST 2025 sau khi loại khoản này ≈ **562 tỷ**, không phải 1.035,9 tỷ.
- **LNST chuẩn hoá** (trung vị TTM 12 quý, đã loại FX, quy thuế về 20%) = **565 tỷ** (EPS ≈ **1.257đ**). TTM Q3/26 sau điều chỉnh = 766 tỷ, cao hơn vì khấu hao giảm và năm El Niño huy động than mạnh. Phần cao hơn này **chưa được coi là bền**.
- **Giá trị nội tại** (DCF FCFE vòng đời HỮU HẠN tới 2047, r = 13,5%, 3 kịch bản; r2 đã thêm dòng tiền Q4/26 và sửa thu hồi vốn lưu động đúng năm dừng):
  - Kịch bản: xấu **11.546** / cơ sở **15.200** / tốt **18.324** đ/cp. Trọng số r2 **0,25 / 0,65 / 0,10** (cơ sở dữ liệu: mục 6).
  - **Trước chiết khấu thanh khoản: 14.599đ/cp. Sau chiết khấu 10%: ≈13.140đ/cp**, vùng **10.390 – 16.490**. (r1: 13.050, vùng 9.550–16.030.)
  - Tâm r2 cao hơn r1 chủ yếu vì thêm dòng tiền Q4/26 (+537đ trước chiết khấu, **ước lượng**) và hạ trọng số "tốt" kéo ngược lại.
  - **Giá trị này phụ thuộc vòng đời nhà máy:** nếu dừng 2030 → 11.510; 2035 → 12.440; 2040 → 12.850; 2047 → 13.140 (sau chiết khấu, bảng mục 6). **Văn bản gốc QĐ 768 (đã đọc 17/11/2026) không có mốc dừng sớm cho QTP:** quy tắc 20/40 năm ⇒ mốc 2051–2054, sau hạn thuê đất 2047; các dòng 2030/2035 là kịch bản trần-dưới hiếm, chỉ để đo biên (mục 7).
  - Kiểm chéo bằng bội số: **không** cho cùng kết luận với DCF. Cách A (PE × EPS chuẩn hoá 1.257, lãi tiền gửi đã nằm trong EPS, không cộng tiền ròng): PE 8,0 → 10.050, PE 9 → 11.310. Cách B (PE × EPS hoạt động + cộng tiền ròng): PE 7–8,5 → 11.260–12.940. Mục 6.
- **So giá 10.300đ:** bằng **0,78×** tâm sau chiết khấu (ngưỡng 0,85× = 11.170) → RẺ theo DCF. Biên này giữ ở vòng đời tới 2047 (văn bản gốc không cắt vòng đời sớm); còn nhạy với trọng số "xấu" (0,5/0,5/0: 0,86×) và với việc gia hạn thuê đất sau 2047 (chưa có căn cứ).
- **Nhãn:** **RẺ theo DCF; xấp xỉ HỢP LÝ theo bội số** (giá 10.300 ≈ PE 8,2 × EPS chuẩn hoá, sát trung vị PE peer 8–9). Điều kiện còn lại: giá cố định PPA sau khi hết khấu hao (trọng số kịch bản) và hạn thuê đất 2047. Đây không phải đề xuất mua (mua do user duyệt từng tranche).
- **Giả thuyết "sạch nợ, cổ tức cao, bond-proxy" — NỬA ĐÚNG:**
  - Sạch nợ: đúng tại 30/9/2026, nhưng sắp vay **2.787,9 tỷ** cho dự án xử lý khí thải (QĐ 917, giai đoạn 2027–29).
  - Cổ tức cao: đúng, nhưng mức 1.000đ + 700đ trong 12 tháng được nuôi bởi năm có khoản FX một lần. Mức bền ước ≈ 900–1.000đ/năm **(ước lượng)**, tương đương DY 8,7–9,7% trên giá 10.300.
  - "Bond-proxy": là trái phiếu **trả dần gốc, có kỳ hạn** (đất thuê tới 2047), không phải trái phiếu vĩnh viễn. Ngoài ra **52% vốn chủ là khoản phải thu một bên duy nhất là EVN/EPTC** (3.089,6 tỷ).
- **Yếu tố pháp lý — WARNING (đã đọc văn bản gốc QĐ 768 ngày 17/11/2026; xem §7):** quy tắc cuối = chuyển đổi khi vận hành 20 năm (nếu giá thành phù hợp) / dừng khi >40 năm không chuyển đổi được ⇒ mốc 2051–2054 của QTP, sau hạn thuê đất 2047; "dừng sau 2030" (dự thảo, báo chí) không có trong văn bản cuối. Phụ lục chỉ đọc lướt mẫu.

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
  - Nguyên giá TSCĐ hữu hình 21.074,9 tỷ, đã khấu hao 19.271,5 tỷ (**91,4%**), giá trị còn lại **1.803,4 tỷ** (BCĐKT 30/9/26; 1.805,1 là tổng TSCĐ gồm vô hình).
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
| Phải thu khác (đã trích dự phòng **189,2** tỷ — khoản cũ, không đổi so đầu năm) | 190,8 | |
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

**Khấu hao còn lại:** 1.803,4 tỷ (trừ Q3 → còn ~1.699 tỷ từ 2027), chạy với tốc độ hiện tại 418 tỷ/năm, giảm dần, hết khoảng 2031 **(ước lượng)**.

**Moat:** NARROW, nên không thưởng tham số moat và cũng không trừ (mục 8).

**Ba kịch bản (r2):**

| Kịch bản | Giả định chính | đ/cp | Trọng số r2 |
|---|---|---|---|
| **Xấu** | LN hoạt động 85% chuẩn hoá trong 2027; **50% từ 2028** (ETS không pass-through + Qc bị cắt + giá cố định bị ép); **dừng 2040**, thu hồi vốn lưu động đúng cuối 2040 | **11.546** (r1 10.614 — sai năm thu hồi VLD) | 0,25 |
| **Cơ sở** | LN hoạt động **phẳng danh nghĩa 503,8 tỷ** tới 2047; giá cố định PPA **giảm đúng bằng khấu hao đã hết** | **15.200** | 0,65 |
| **Tốt** | Giá cố định PPA **không giảm** sau khi hết khấu hao ⇒ giữ EBITDA (khấu hao tiết kiệm → lợi nhuận ×0,8) | **18.324** | 0,10 |
| **Có trọng số, trước chiết khấu thanh khoản** | | **14.599** | |
| **Sau chiết khấu thanh khoản 10%** | | **13.139 ≈ 13.140** | |

Cùng mô hình, không đổi framework; thay đổi so r1 liệt kê ở mục "Lệch mô hình" bên dưới.

**Cơ sở dữ liệu của trọng số (BQ `ticker_financial`, quý Q4 mỗi năm, EBITDA_P0 và vay):**

| | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | TTM Q3/26 |
|---|---|---|---|---|---|---|---|---|---|---|
| EBITDA (nghìn tỷ) | 3,36 | 3,09 | 3,11 | 2,88 | 1,94 | 1,93 | 1,59 | 1,28 | 1,94 (**1,27 bỏ FX 663**) | 2,05 (**1,39 bỏ FX**) |
| Vay (nghìn tỷ) | 9,56 | 7,53 | 5,58 | 3,75 | 2,15 | 1,09 | 0,32 | 0,19 | 0 | 0 |

- 2017→2024 EBITDA giảm **62%** (3,36→1,28) khi nợ vay 9,56→0 và khấu hao rơi. Đây là bằng chứng **ủng hộ kịch bản cơ sở** (giá cố định PPA hoàn vốn/lãi vay, giảm khi hết nợ).
- 2024→2026 (nợ ≈ 0): EBITDA bỏ FX đi ngang ~1,27–1,39 nghìn tỷ trong khi khấu hao tiếp tục giảm. Không xác nhận cũng không bác bỏ "tốt": mới 2 năm, và 2026 có El Niño. Vì vậy **không có dữ liệu trực tiếp** cho "giá cố định không giảm" ⇒ hạ trọng số "tốt" 0,25 → **0,10**; "xấu" giữ 0,25 (chưa có số ETS/Qc 2027); cơ sở **0,65**.
- Bảng đo (BQ 17/11/2026): vay QTP 9.562 → 0 tỷ (2017Q4→2025Q4); EBITDA_P0 3.363 → 1.279 tỷ (2024Q4). EBITDA bỏ FX = EBITDA − 663 (**ước lượng**: toàn bộ 663 tỷ FX nằm trong EBITDA_P0 của TTM chứa Q4/25).

**Giá trị theo bộ trọng số (xấu/cơ sở/tốt; dừng 2047, đ/cp):**

| Bộ trọng số | Trước CK | Sau CK 10% | Giá 10.300 / tâm sau CK |
|---|---|---|---|
| **0,25/0,65/0,10 (chọn)** | **14.599** | **13.139** | **0,784** |
| 0,25/0,75/0 | 14.286 | 12.858 | 0,801 |
| 0,5/0,5/0 | 13.373 | 12.035 | 0,856 |
| 0,25/0,50/0,25 (r1) | 15.067 | 13.561 | 0,760 |

⇒ Kết luận "RẺ theo DCF" **mong manh** theo trọng số: nếu coi xấu = cơ sở (0,5/0,5/0) thì giá/tâm 0,86 — **vượt ngưỡng 0,85**.

**Độ nhạy vòng đời — đừng đọc tâm mà bỏ qua bảng này** (chưa có văn bản gốc chốt ngày dừng; bỏ câu "an toàn vì 40 năm" của r1):

| Dừng sau | Cơ sở trước CK | Cơ sở sau CK | **Chọn** trước CK | **Chọn** sau CK | Giá / tâm chọn | Giá / tâm cơ sở |
|---|---|---|---|---|---|---|
| 2030 | 13.117 | 11.805 | 12.785 | 11.507 | **0,895** | 0,872 |
| 2035 | 14.312 | 12.881 | 13.819 | 12.437 | 0,828 | 0,800 |
| 2040 | 14.845 | 13.361 | 14.274 | 12.847 | 0,802 | 0,771 |
| 2047 (mô hình) | 15.200 | 13.680 | 14.599 | 13.139 | 0,784 | 0,753 |
| 40 năm tuổi (*) | 15.250 | 13.725 | 14.656 | 13.191 | 0,781 | 0,750 |

(*) TM1–2 COD 2011 → 2051; TM3–4 COD 2014 → 2054 (BCTC Vietstock 2023: tổ 3 PAC 01/01/2014, tổ 4 16/03/2014; tổ 1–2 chạy thương mại 2011 — **tài liệu VNDirect 2026 ghi 08/07/2011 và 28/04/2011, thứ tự lạ nên cần đối chiếu**). **Giả định gia hạn thuê đất qua 2047** — chưa có căn cứ; mốc 15/3/2047 vẫn là trần hợp đồng đất đã biết. Công suất 50%/50% theo cặp tổ. Với kịch bản xấu: dừng sớm nhất = min(2040, năm dừng).

- **Hiểu đúng bảng:** dừng 2030 vẫn cho giá trị 11.510 ≈ 1,12× giá — vì tiền ròng 3.425đ/cp + khấu hao còn lại + vốn lưu động 2.259 tỷ thu hồi giữ phần lớn giá trị. Tuy nhiên biên an toàn so ngưỡng 0,85 **mất** (0,895).
- Dòng tiền Q4/26 gồm trong mọi dòng của bảng.

**Lệch mô hình đã biết (nói rõ, không lấp):**
1. **Dòng tiền Q4/26** — r1 bỏ sót (mô hình bắt đầu 2027 từ bảng cân đối 30/9). r2 thêm: LNST hoạt động 145 tỷ + khấu hao 104,5 − capex 4 = **245,5 tỷ ≈ 546đ/cp** (**ước lượng**: Q4/24 154,8 (thuế 10%), Q4/25 bỏ FX 166,3, trừ ~15 lãi tiền gửi đã tính trong tiền ròng; skeptic ước ~600). Tác động: **+537đ/cp** vào giá trị có trọng số trước CK.
2. **Thu hồi vốn lưu động kịch bản xấu** — r1 chiết khấu về 2047 dù dừng 2040. r2 thu hồi đúng cuối năm dừng (2040): xấu 10.614 → **11.546** (skeptic tính 11.142 không có Q4 và cách chiết khấu khác; r2 không-Q4 = 11.008 — khác ~134đ do quy ước cuối năm/giữa năm, ghi nhận).
3. **Không có chi phí đóng cửa/hoàn nguyên bãi tro** trong mô hình (không có số). Độ nhạy (**ước lượng, 3 mức giả định**, trừ tại năm dừng 2047): 200 tỷ → −42đ; 500 tỷ → −106đ; 1.000 tỷ → −211đ/cp trước CK — nhỏ vì bị chiết khấu 20 năm; nhưng nếu dừng 2030 thì lớn hơn.
4. **LNST phẳng danh nghĩa 21 năm** (không lạm phát, không tăng giá cố định). Độ nhạy **+3%/năm** (**ước lượng**): +1.643đ/cp (14.599 → 16.241) — đây là giới hạn trên của việc "làm phẳng", không dùng làm base vì giá cố định PPA là thoả thuận có kỳ hạn.
5. TSCĐ còn lại dùng 1.803,4 (sửa từ 1.805,1) → khấu hao hết khoảng 2031 (không đổi kết luận).

**Độ nhạy theo lãi huy động** (r di chuyển 1:1, trọng số chọn):

| Lãi huy động | Giá trị (đ/cp) | Thay đổi |
|---|---|---|
| −100bp | 15.151 | +3,8% |
| −50bp | 14.868 | +1,8% |
| +50bp | 14.343 | −1,7% |
| +100bp | 14.101 | −3,4% |

**Chiết khấu thanh khoản:**
- ADV trung vị **1,22 tỷ/phiên** (BQ `ticker`, 63 phiên 15/8–16/11/2026), free float 19,6%; 15% ADV ≈ 0,18 tỷ/phiên ⇒ vị thế 1 tỷ thoát ~5,5 phiên, 3 tỷ ~16 phiên.
- Chiết khấu chọn **10%** (**ước lượng**): 5% → 13.869 · **10% → 13.139** · 15% → 12.409 (r2, trước chiết = 14.599).
- Vị thế áp dụng: **≤0,5% NAV và ≤~2 tỷ** (~11 phiên để thoát).

**Hai nền giá trị + cờ phân kỳ (chỉ hiển thị):**
- V_ngắn = LNST chuẩn hoá 565,5 / r = **9.308đ**; V_dài = DCF cơ sở **15.200đ** (r2). D = |ln(9.308/15.200)| = **0,49 < ln2 (0,693)** ⇒ không bật cờ.
- Dòng C4: **chưa qua tiêu chí khoá trước (2/4 chân trời), chỉ theo dõi** (không đổi so r1; số 21.034 phồng do CFO3 gồm FX 2025).
- Dòng D2: không tính (không có capex/doanh thu trung vị ngành sạch).

**Bội số — kiểm chéo, không phải tâm (r2: hai cách, đủ dải PE):**
- PE peer (BQ `ticker` 16/11/2026, TTM thô; **PE peer gồm tiền mặt của họ trong giá và lãi tiền gửi trong lợi nhuận**): 22 mã điện/thuỷ điện/NLTT, **trung vị toàn peer 8,99**; 8 mã tr1 (PPC, HND, NBP, POW, NT2, BTP, QPH, VSH) trung vị **7,96**; 8 mã nhiệt điện+thuỷ điện (PGV, NT2, NBP, POW, SJD, BTP, HND, PPC) trung vị **5,83**. (Dispatch ghi trung vị ~6,6 — không tái lập được từ bộ mã nào ở trên; tôi báo 3 bộ đo được.) QTP PE thô 3,74 (TTM có FX).
- Cách A — **PE × EPS chuẩn hoá 1.257 (đã gồm lãi tiền gửi), KHÔNG cộng tiền ròng** (like-for-like với PE peer): 
- Cách B — **PE × EPS hoạt động 1.120 + tiền ròng 3.425** (thiên về QTP vì cộng tiền mặt theo mệnh giá, trong khi PE peer đã định giá tiền mặt của họ ở mức thấp hơn mệnh giá):

| PE | Cách A | Cách B |
|---|---|---|
| 5 | 6.283 | 9.023 |
| 6 | 7.540 | 10.143 |
| 6,6 | 8.294 | 10.815 |
| 7 | 8.796 | 11.262 |
| 7,96 (tr1 8 mã) | 10.003 | 12.337 |
| 8,5 | 10.681 | 12.942 |
| 9 (≈ trung vị 22 mã) | 11.310 | 13.502 |

- PB 0,6–0,7 × BVPS 13.299 = **7.980–9.310** (cận dưới; PB peer thấp do ROE thấp, QTP ROE chuẩn hoá ~9,4%).
- **Đọc:** giá 10.300 = PE 8,2 × EPS chuẩn hoá. Cách A: giá nằm trong dải PE 7–9 (8.800–11.310) ⇒ **xấp xỉ hợp lý**. Cách B (thiên về QTP): giá thấp hơn dải 11.260–13.500 ⇒ rẻ nhẹ. Bội số **không xác nhận** mức rẻ ~22% của DCF; khoảng cách giữa DCF (13.140) và cách A (≈10.000–11.300) chính là giá trị mà DCF gán cho vòng đời dài + PPA hoàn vốn, thứ thị trường có thể đang chiết khấu.

**Tâm và vùng (sau chiết khấu thanh khoản 10%, r2):** tâm **13.140**, vùng **10.390 (xấu) – 16.490 (tốt)**, ngưỡng 0,85× tâm = **11.170**. (Hiển thị — chưa ghi `dd_price_zones.json`.)

**So với giá 10.300đ (16/11):**
- Giá ≈ **0,78×** tâm DCF; nằm trong dải bội số cách A (8.800–11.310). Nhãn: RẺ theo DCF có điều kiện / xấp xỉ hợp lý theo bội số.
- Giá đã trừ quyền tạm ứng 700đ (GDKHQ 05/11, ĐKCC 06/11). **Giảm từ ~11.300 xuống 10.300 (−1.000đ) thì ~700đ (70%) là điều chỉnh cổ tức, không phải bán tháo hay "fear-buy".** (Mốc 11.300 do Mike nêu trong dispatch; chưa tự đo.)

## 7. Pháp lý / quản trị / chính sách — chỉ WARNING

- **PDP8 / QĐ 768/QĐ-TTg (15/04/2025) — ĐÃ ĐỌC VĂN BẢN GỐC (17/11/2026, user duyệt tải thủ công):** PDF 177 trang từ moit.gov.vn (`src_qd768/qd768.pdf`, bản scan; ảnh trang trích: `qd768_p07_nhiet_dien_than.png`, `qd768_p05_dinh_huong.png`).
  - **Điều khoản nhiệt điện than (tr.7, mục III.1.b(vi), nguyên văn):** "Chỉ thực hiện tiếp các dự án đã có trong quy hoạch và đang đầu tư xây dựng đến năm 2030. Định hướng thực hiện chuyển đổi nhiên liệu sang sinh khối/amoniac với các nhà máy đã vận hành được 20 năm **khi giá thành phù hợp**. **Dừng hoạt động các nhà máy có tuổi thọ trên 40 năm nếu không thể chuyển đổi nhiên liệu.**" Năm 2030: ~31.055 MW; khẩn trương hoàn thành 5 dự án/4.360 MW đang xây (Na Dương II, An Khánh–Bắc Giang, Vũng Áng 2, Quảng Trạch I, Long Phú 1). Định hướng 2050: không còn dùng than phát điện, chuyển sang sinh khối/amoniac (25.798 MW). Tr.5: "chấm dứt hoạt động với các nhà máy không đáp ứng tiêu chuẩn môi trường".
  - **Kết luận về mệnh đề "dừng sau 2030":** **KHÔNG có trong văn bản cuối.** Quy tắc thật = 20 năm (chuyển đổi, có điều kiện giá) / 40 năm (dừng nếu không chuyển đổi được). Với QTP (COD 2011 và 2014): mốc 20 năm = 2031/2034 (tùy chọn khi giá thành phù hợp), mốc 40 năm = 2051/2054 — **sau hạn thuê đất 2047 của mô hình**. Vòng đời trong mô hình (2047) **không bị quy hoạch cắt**. Phụ lục (tr.18–177, đã lướt mẫu bằng mắt, KHÔNG tra cứu toàn bộ): các bảng là phân bổ công suất MỚI theo tỉnh, danh mục dự án nguồn/lưới mới — không thấy danh sách dừng nhà máy hiện hữu; chưa OCR toàn văn nên không khẳng định tuyệt đối. Tên "Quảng Ninh" trong dự thảo 2025 (báo chí) là cấp 2 và không còn xuất hiện trong điều khoản cuối.
  - **Quan điểm user (17/11 14:16 ICT, ghi lại, không phải bằng chứng):** Việt Nam đang thiếu điện, chưa có nguồn nào bù đắp một nhà máy nhiệt điện than lớn, vẫn đang xây thêm nhiệt điện, nên ~20 năm tới rủi ro dừng nhà máy rất thấp. Cơ sở dữ liệu ủng hộ: thiếu nguồn miền Bắc 2027 4.256 MW (BCT), 5 dự án than 4.360 MW đang xây, BCT đề xuất thêm 5.300 MW (nguồn báo chí 07/11/2026). Giữ nguyên cách mô hình: **base = vận hành tới 2047**; các dòng dừng 2030/2035 trong bảng độ nhạy là **kịch bản trần-dưới hiếm, không có cơ sở văn bản**, chỉ để đo biên.
  - **Năm COD từng tổ (BCTC Vietstock 2023, VNDirect 2026 — chưa đối chiếu BCTN):** TM1 ~2011, TM2 ~2011, TM3 01/01/2014, TM4 16/03/2014.
  - **Rủi ro còn lại thật (không phải ngày dừng):** (i) gia hạn thuê đất sau 2047 chưa có căn cứ — là trần vòng đời thực của mô hình; (ii) nhà máy hiệu suất thấp bị điều độ ít khi LNG/tái tạo vào (sau 2028 — Bobby) ⇒ đã nằm trong kịch bản xấu; (iii) tiêu chuẩn môi trường: dự án khí thải ~3.485 tỷ đang làm chính là để đáp ứng.
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
| **BCTC Q4/26** (~21/01/2027) — mốc 1, đã viết lại: 9T26 đã 599,5 nên không dùng LNST năm | **LNST Q4/26 ≥ ~190 tỷ** (kỳ vọng ~160 = Q4/24 154,8 / Q4/25 bỏ FX 166,3, **ước lượng**; +El Niño) VÀ **lợi nhuận gộp Q4 ≥ ~160 tỷ** với sản lượng không thấp hơn cùng kỳ ⇒ tăng trọng số "tốt" (khấu hao giảm, giá cố định không bị cắt) | **LNST Q4/26 ≤ ~130 tỷ** (cùng ngưỡng đối xứng ±30 tỷ quanh 160) hoặc lợi nhuận gộp Q4 < 120 tỷ ⇒ tăng trọng số "xấu"/coi "cơ sở" là trần. **Tách sản lượng vs giá:** đọc lợi nhuận gộp/kWh (cần sản lượng điện thương phẩm từ giải trình/BCTN): gộp/kWh giảm khi sản lượng tăng = giá bị cắt (xấu); gộp/kWh tăng hoặc phẳng khi khấu hao giảm = giá không bị cắt (tốt) |
| Doanh thu/biên Q1–Q2/2027 | Sản lượng tăng và biên tăng | **Biên gộp giảm so cùng kỳ trong khi sản lượng tăng** ⇒ dấu hiệu giá cố định PPA bị cắt ⇒ tăng trọng số "xấu" |
| Phải thu EPTC (31/12/2026, 31/3/2027) | < 2.500 tỷ ⇒ dòng tiền về tốt | > **3.800 tỷ** (>120 ngày) ⇒ chiết khấu thêm, xem lại cổ tức |
| Cổ tức 2026 cả năm (ĐHĐCĐ 04/2027) | ≥ 1.200đ | < **800đ** ⇒ hạ DY bền xuống ~7% |
| PDP8 / văn bản lịch dừng (Bobby F12, 2027-12-31) | Danh sách cuối không có QN, hoặc cho chuyển đổi/gia hạn | Lịch dừng QTP **trước 2047** ⇒ rút ngắn vòng đời |
| Thêm doanh thu chênh lệch tỷ giá (văn bản EVN) | Có ⇒ cộng giá trị một lần | — |
| Vượt dự toán dự án khí thải / EVN không đưa vào giá | — | Có số cụ thể ⇒ chuyển phần vốn chủ ~697 tỷ sang kịch bản tiêu cực |

## 10. Việc còn mở / cần kiểm chứng

1. PPA: thời hạn, lịch giá cố định sau khi hết khấu hao — hỏi IR hoặc đọc BCTN.
2. Qc 2027 và FMP — đợi kế hoạch vận hành 2027 của BCT (Bobby F13).
3. Năm COD từng tổ máy — đối chiếu BCTN/IR (nguồn hiện tại: BCTC Vietstock 2023, VNDirect 2026; thứ tự tổ 1–2 lạ).
4. Số USD chính xác của hợp đồng EPC.
5. Số dư chênh lệch tỷ giá còn phải thu từ EVN.
6. Room ngoại.
7. **Văn bản gốc QĐ 768:** ĐÃ ĐỌC điều khoản chung (17/11/2026); phụ lục 177 trang là bản scan, mới lướt mẫu, chưa OCR toàn văn — không thấy danh sách dừng nhà máy hiện hữu.
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

## 12. HARD ABANDON — điều kiện huỷ (chỉ lưu; KHÔNG làm hồ sơ §2.5 bây giờ)

> Nếu user sau này xét QTP theo luật discretionary 4. Đây là danh sách điều kiện **huỷ ý định**, không phải đề xuất mua.

1. **Phải thu EPTC vượt ngưỡng:** > **3.800 tỷ** (>120 ngày doanh thu) ở hai quý liên tiếp, hoặc xuất hiện **nợ quá hạn / trích dự phòng** (hiện: 3.089,6 tỷ ≈ 100 ngày, không dự phòng).
2. **Cắt/huỷ cổ tức:** cổ tức tiền mặt 2026 cả năm **< 800đ** (hiện đã tạm ứng 700đ), hoặc ĐHĐCĐ 04/2027 không chia / chuyển sang giữ lại để góp vốn dự án khí thải.
3. **Văn bản PDP8/BCT có ngày dừng QTP trước 2040** (hoặc dừng sau 2030 theo dự thảo trở thành chính thức): giá/tâm ≥ 0,83 (bảng vòng đời, dừng ≤2035) ⇒ mất biên 0,85.
4. **EVN từ chối đưa chi phí khí thải vào giá cố định PPA** (vốn chủ ~697 tỷ ≈ −1.550đ/cp nếu mất trắng) hoặc ETS 2028 bắt buộc mà không pass-through.
5. (kèm theo) Giá giảm 11.300 → 10.300 vừa qua **~70% là điều chỉnh cổ tức 700đ (GDKHQ 05/11)** — không coi là tín hiệu fear-buy.

## Phụ lục E — Đính chính của fundamental-skeptic (INCONCLUSIVE; 14 số khớp BCTC; mô hình tái lập đúng): đã áp / không áp

| # | Đính chính | Trạng thái r2 | Ghi chú / lý do |
|---|---|---|---|
| 1 | Tìm văn bản gốc QĐ 768 + COD; sector read Bobby "dừng sau 2030"; bảng độ nhạy vòng đời; bỏ câu trấn an | **Áp một phần** | Bảng độ nhạy vòng đời + bỏ trấn an + COD từ BCTC/VNDirect: đã làm. **Văn bản gốc chưa đọc được** (nói rõ "chưa kiểm", §7). Không thể chốt "dừng 2030". |
| 2 | Trọng số kịch bản theo lịch sử EBITDA vs KH+lãi vay; hạ "tốt" | **Áp** | 0,25/0,65/0,10, cơ sở dữ liệu ở §6; báo 4 bộ trọng số. Tâm chọn có thể bị lật ở bộ 0,5/0,5/0 (giá/tâm 0,86). |
| 3 | Kiểm chéo bội số PE 5–9; trung vị peer ~6,6; có/không cộng tiền ròng; đổi nhãn | **Áp một phần** | In đủ PE 5–9, hai cách A/B. **Trung vị ~6,6 không tái lập** từ 3 bộ peer đo được (5,83 / 7,96 / 8,99) — báo cả ba. Nhãn đổi thành "xấp xỉ hợp lý theo bội số". |
| 4 | Viết lại mốc §9 #1 (LNST 2026 vô nghĩa vì 9T 599,5) | **Áp** | Dùng LNST Q4/26 và lợi nhuận gộp/gộp trên kWh; ngưỡng ±30 tỷ **(ước lượng)** quanh ~160. |
| 5 | Ghi lệch mô hình: Q4/26, WC xấu, chi phí đóng cửa, LNST phẳng | **Áp** | Q4/26 đưa vào mô hình (+537đ **ước lượng**); WC thu hồi đúng cuối 2040 (xấu 10.614 → 11.546; skeptic 11.142 — chênh quy ước, §6); chi phí đóng cửa + LNST +3% chỉ làm độ nhạy, **không** vào base. |
| 6 | Số nhỏ: 189,2; 1.803,4 | **Áp** | §2a, §4. |
| 7 | Mục HARD ABANDON + ghi giá giảm do GDKHQ | **Áp** | §12; mốc 11.300 do Mike nêu (chưa tự đo). |
| — | Q4/26 skeptic ước ~+600đ/cp | **Không áp nguyên** | r2 dùng 546đ (LNST hoạt động 145 sau trừ lãi tiền gửi đã trong tiền ròng). Khác ~54đ, không đổi kết luận. |
