# SIP — KCN + bán lẻ điện nước cho dòng lãi bền ~1,4 nghìn tỷ/năm và đã chia cổ tức tiền 50%, nhưng 6,0 nghìn tỷ cho vay công ty chứng khoán + trái phiếu doanh nghiệp (116% vốn chủ, phần lớn không tài sản bảo đảm) khiến giá 48.350 chỉ thấp hơn tâm định giá ~6–10% — trong vùng hợp lý, không phải rẻ rõ

DD SIP (CTCP Đầu tư Sài Gòn VRG, HOSE) · v1 (đã đối chiếu [Bobby]) · as-of 01/11/2026 · job `Taylor_20261101_041613`

> Nghiên cứu chỉ đọc, viết trung dung. Không khuyến nghị mua/bán, không gắn nhãn QUALIFY/NON, không chạy §2.5. Có yếu tố pháp lý/quản trị ⇒ chỉ WARNING.
> **Đơn vị: tỷ đồng** trừ khi ghi khác. Năm tài chính = năm dương lịch. Q3/2026 = 01/07–30/09/2026.
> Số tự tính nằm ở `calc/valuation.py` → `calc/valuation_out.txt`. Số đọc từ ảnh BCTC nằm ở `calc/notes_read.md`. **Mọi tham số định giá là (ước lượng).**
>
> **Mốc BCTC:** **BCTC Q3/2026 ĐÃ công bố** trên website công ty ngày 30/10/2026 (ký 29/10/2026), **chưa soát xét**. BQ `ticker_financial` mới tới 2026Q2 nên **không dùng BQ cho số tài chính**. BQ chỉ dùng cho giá lịch sử, ADV và peer.
>
> **Nguồn** (tải về `src/` từ saigonvrg.com.vn qua `ajax/tailieu.php?id=`):
> - **[Q3HN]/[Q3R]**: BCTC hợp nhất/riêng 9T/2026, chưa soát xét (id 1264).
> - **[KT25]**: BCTC hợp nhất 2025, EY Việt Nam kiểm toán, ký 30/03/2026 (id 1213).
> - **[6T]**: BCTC giữa niên độ 2026, EY soát xét (id 1260/1261). Đã tải nhưng chưa đọc từng trang; kết luận soát xét lấy từ fact sheet.
> - **[AR25]**: Báo cáo thường niên 2025, có text.
> - **[CBTT]**: `calc/cbtt_facts.md`, do agent phụ thu thập. Mỗi dòng có id/ngày; dòng ghi "[báo]" là chưa xác minh.
> - **[DNSE]**: latest_trade, lấy 01/11/2026 11:25 ICT. Khớp cuối **48.350 lúc 30/10/2026 14:45:06**, KL cả phiên 7.530 cp (3,65 tỷ).
> - **[BQ]**: lịch sử giá và peer, `calc/sip_monthly_bq.csv`, `calc/comps_bq.csv`.
> - **[Bobby]**: `kb/data_registry/market-state/sector_read_kcn_cho_thue_dat_20261101.md`, đọc ngành blind. Có lúc 11:33 ICT; đọc trước khi chốt định giá (§9).

---

## 0. Tóm tắt

**Kiểm chứng giả thuyết trong brief (nửa đúng):**
- Tên pháp nhân đúng: CTCP Đầu tư Sài Gòn VRG, HOSE từ 08/08/2023.
- **"Thuộc hệ VRG" chỉ đúng một phần.** Tập đoàn Công nghiệp Cao su VN **không có tên** trong danh sách cổ đông lớn [AR25 tr.72, 23/03/2026]. Cổ đông lớn:
  - CTCP ĐT&PT Đô thị An Lộc: 19,79%.
  - CTCP KCN Nam Tân Uyên (NTC, công ty trong hệ VRG): 9,00%.
  - Chủ tịch Trần Mạnh Hùng: 8,64%, giảm còn 7,11% sau khi bán thoả thuận 3,7 triệu cp từ 10/06/2026.
  - Lưu/Lư Thanh Nhã (TGĐ): 7,56%.
- Liên hệ VRG chỉ gián tiếp qua NTC và qua một thành viên BKS. SIP lại giữ ngược 21,76% NTC.
- **SIP không có vườn cao su** [AR25], nên đọc ngành cao su không áp dụng.

**Bản chất kinh doanh:** chủ đầu tư 5 KCN, tổng 3.205 ha, 2.441 ha thương phẩm, còn 937 ha chưa cho thuê, lấp đầy 61,6% [AR25].
- Doanh thu chủ yếu là **bán lại điện nước trong KCN**: 9T 5.730 / 7.003 = 82%, biên gộp chỉ 8,7%.
- **Lợi nhuận** đến từ ba nguồn: tiện ích KCN, phân bổ tiền thuê đất và **lãi trên khoản tiền khách trả trước**.

**Tích cực (đều có số):**
- **Lãi bền, ít lumpy:** LNST mẹ 9T/26 1.078,0 (+7,6% YoY), TTM 1.399.
  - Tiền thuê đất được ghi nhận **phân bổ** theo thời hạn thuê, không ghi một lần: 9T chỉ 341,8 DT [Q3HN TM25].
  - Ngoài ra còn **15.077 doanh thu chưa thực hiện** (tiền khách đã trả) sẽ chảy dần vào lãi kế toán [TM21].
- **Lãi ổn định từ tiện ích:** LN gộp điện nước 497 (+13% YoY), dịch vụ KCN khác 238 (+12%).
- **Cổ tức tiền cao:** 2025 chi 50% VĐL (5.000 đ/cp, payout 111% LNST riêng). Lợi suất 10,3% trên giá 48.350.
- **Kiểm toán sạch:** EY kiểm toán 2025 chấp nhận toàn phần, không nhấn mạnh [KT25 tr.4–5]. Soát xét 6T/2026 không ngoại trừ [CBTT].
- **Định giá bề mặt thấp:** PE TTM 8,37, thấp hơn trung vị peer KCN [BQ].

**Tiêu cực / cần lưu ý:**
- ⚠️ **Phơi nhiễm tín dụng phi ngân hàng 6.016 = 116% VCSH mẹ = 51% vốn hoá:**
  - **Cho công ty chứng khoán vay 4.223,4.** Theo [TM4b], chỉ 31,07% có tài sản bảo đảm của bên vay; 68,93% (~2.911) dựa vào "bên thứ ba phối hợp quản lý dòng tiền". Tên bên vay và lãi suất không công bố.
  - **Trái phiếu doanh nghiệp 1.792,4 mua mới trong 9T** (01/01: 0), gồm CTCP Thời Đại Mới T&T 1.000,7, Vinhomes 363,6, CTCP Đầu tư Phước Sơn 200,0 và khác 228,1. Giá trị hợp lý "chưa xác định được" [TM4a].
- **Nguồn tiền cho các khoản trên:** **vay ngân hàng tín chấp 4.374** (6 hạn mức, đều tín chấp, mục đích "bổ sung vốn lưu động") cộng tiền khách trả trước.
  - Lãi vay 9T tăng 81% (211,4 so với 117,0).
  - Lãi tiền gửi + cho vay 9T là 602,0 (+60%).
  - **Lãi tài chính ròng ≈ 27% LNTT** (ước lượng run-rate, §3).
- **Q3/2026 đi lùi YoY:** LNST mẹ 344,4 (−5,9%), LN gộp 351,6 (−4,1%), chi phí tài chính ×2,6. Số Q3 **chưa soát xét**.
- **Tạm ứng 643,7 cho nhân viên "để tìm hiểu và mua đất"** [TM7], cộng 2.529,6 tạm ứng đền bù. Đây là quy trình nhạy cảm về kiểm soát.
- **Thanh khoản cạn:** ADV 3 tháng 4,1 tỷ/phiên; từ 07/2026 chỉ 3,4–4,7 tỷ/phiên (2025 là 18–68 tỷ). Phiên 30/10 khớp 7.530 cp.
- **Cho thuê đất chậm:** 2025 chỉ 28,6 ha so với kế hoạch 45 ha; kế hoạch 2026 là 60 ha [AR25]. Phước Đông B mới lấp 25%.

**Định giá (§7):**
- Vùng kịch bản **~31.000–78.000 đ**. Tâm có trọng số **~51.500** (30/50/20, nghiêng xuống), hoặc **~53.850** nếu đối xứng.
- **Vùng hợp lý hẹp ~44.000–58.000** (cơ sở ± độ nhạy tín dụng/đất và PE 8–10x).
- **Giá 48.350 nằm trong vùng, nửa dưới, thấp hơn tâm ~6–10%.**
- Hai biến chi phối:
  1. **Chất lượng 6.016 tỷ tín dụng:** mỗi 10% lỗ trên phần không bảo đảm (4.340) ≈ −1.600 đ/cp.
  2. **Giá thực thu và tốc độ cho thuê 937 ha** (72% là Phước Đông B ở Tây Ninh, vùng vệ tinh mà [Bobby] ghi giá −6,8% YoY, lấp đầy 61%): mỗi ±4 tỷ/ha ròng ≈ ±4.400 đ/cp.
- Bản trước khi đọc Bobby (đất 12/8/4 tỷ/ha) cho tâm ~48.350, thấp hơn ~3.150 (`calc/valuation_out_preBobby.txt`). Chỉ khối đất thay đổi, do giá chào thị trường ~47 tỷ/ha gộp mà [Bobby] dẫn cao hơn giả định ban đầu.

**WARNING pháp lý/quản trị: TRUNG BÌNH** (§6). Chưa thấy khởi tố hay xử phạt trong CBTT đã đọc, nhưng có ba điểm cần theo dõi:
- Cấu trúc tín dụng phi ngân hàng lớn, bên vay không nêu tên.
- Hợp đồng BCC với CTCP XD&PT Thế Hệ Mới (SIP giữ 18,89%), với phân chia lợi ích bất thường.
- Tạm ứng nhân viên mua đất.

---

## 1. Kết luận và vùng giá

| Vùng giá (đ/cp, 242,11 tr cp) | Đọc |
|---|---|
| < ~44.000 | Hợp lý nếu lỗ ≥50% phần tín dụng không bảo đảm, **hoặc** core chỉ đáng PE ~7x, **hoặc** 937 ha còn lại chỉ thu ≤4 tỷ/ha ròng (giá thuê thấp/chậm) |
| **~44.000 – 58.000** (hiện 48.350) | **Trong vùng, nửa dưới; thấp hơn tâm ~6–10%.** Cơ sở 53.170; PE 8–10x trên EPS TTM 5.778 cho 46.200–57.800 |
| > ~58.000 | Cần: tín dụng thu hồi đủ + công bố bên vay; cho thuê đạt ≥60 ha/năm ở ~120 USD/m²; không chiết khấu quản trị |

**Ba kịch bản** (`calc/valuation_out.txt`; SOTP = vận hành × PE + tài sản tài chính ròng − lỗ tín dụng − thuế tương lai + đất còn lại; nhân (1 − NCI 8,5%)):

| Kịch bản | P | Core (vận hành trừ phân bổ đất, sau thuế) × PE | Lỗ phần TD không bảo đảm | Đất còn lại 937 ha (tỷ/ha ròng, số năm) | CK quản trị | Giá trị |
|---|---|---|---|---|---|---|
| Tích cực | 0,20 | 10x → 7.572 | 0% | 18, 15 năm (~62 ha/năm) → 7.067 | 0% | **~77.970** |
| Cơ sở | 0,50 | 9x → 6.815 | 5% → 217 | 12, 22 năm (~43 ha/năm) → 3.564 | 10% | **~53.170** |
| Tiêu cực | 0,30 | 7x → 5.300 | 30% → 1.302 | 6, 30 năm (~31 ha/năm) → 1.366 | 20% | **~31.090** |
| **Trọng số** | | | | | | **~51.510** (đối xứng 25/50/25: ~53.850) |

Tài sản tài chính ròng sau CP hạ tầng phải trả là 5.051 (× (1 − NCI) = 4.621), giống nhau ở cả ba kịch bản. Thuế tương lai trên DT chờ phân bổ có PV 383/479/575 (ước lượng). Cách dựng từng khối:
- **Tài sản tài chính ròng = 5.051:**
  - Tiền 400,8 + tiền gửi 7.187,6 + cho vay CTCK 4.223,4 + trái phiếu 1.792,4 + cổ phiếu (GTHL) 203,9 = **13.808**.
  - − vay 5.494,2 − **chi phí hoàn thành hạ tầng đã cho thuê phải trả 3.262,8** [TM20] = 5.051.
  - DT chưa thực hiện 15.077 **không** trừ: tiền đã thu, chi phí đã nằm trong BĐSĐT và trích trước. Chỉ trừ **thuế TNDN tương lai** khi phân bổ: 15.077 × 69% biên × 20%, phân bổ 35 năm, PV 13% ≈ 479 (ước lượng). Giả định thuế nộp theo phân bổ vì BCĐ **không** có tài sản thuế hoãn lại lớn; nếu thuế đã nộp khi thu tiền thì khoản trừ này bằng 0, cộng ~+2.000 đ/cp.
- **Core:** LN gộp 9T trừ mảng đất (836,4) − BH+QL (108,4) + LDLK (47,8), × 4/3 → **1.035 trước thuế/năm** (ước lượng, chưa chỉnh mùa vụ).
  - PE 9x ≈ Ke 13% với g 2%, khớp khung chi phí vốn (Ke nội địa 12,3–13,4%).
  - Lãi tài chính **không** vốn hoá vào PE vì đã đếm trong tài sản tài chính ròng, tránh đếm hai lần.
- **Đất còn lại:**
  - "tỷ/ha ròng" = tiền thuê trả trước − đền bù/hạ tầng − thuế, cho kỳ thuê còn lại (ước lượng).
  - Tham chiếu: giá chào vùng 185 USD/m² ≈ 47 tỷ/ha gộp; Tây Ninh 179,6 USD [Bobby/C&W Q2]. Giá thực thu thường thấp hơn giá chào; [báo] Phước Đông ~90–110 USD/m², chưa xác minh.
  - Tỷ/ha ròng 6/12/18 ≈ 13–38% giá chào gộp sau đền bù (đang tăng theo bảng giá đất hằng năm [Bobby]), hạ tầng và thuế.
  - Tốc độ: 2025 thực tế 28,6 ha, kế hoạch 2026 60 ha. Cơ sở ~43 ha/năm.
  - **Không có giá thuê/m² chính thức** [AR25 chỉ ghi "đi ngang"]. Phần này rộng nhất, nên P nghiêng xuống.
- **PE chéo:** EPS TTM mẹ 5.778. Trong đó ~1.574 đ/cp là lãi tài chính ròng sau thuế và ~950 đ/cp là phân bổ doanh thu đất (phi tiền mặt). PE 8x ra 46.226, 10x ra 57.783.

**Độ nhạy cơ sở theo lỗ phần tín dụng không bảo đảm** (2.911 cho vay + 1.429 TP ngoài Vinhomes):

| Lỗ | 0% | 10% | 20% | 30% | 50% |
|---|---|---|---|---|---|
| Giá trị cơ sở (đ/cp) | 53.976 | 52.363 | 50.750 | 49.136 | 45.910 |

**Độ nhạy cơ sở theo tỷ/ha ròng của đất còn lại** (22 năm):

| Tỷ/ha ròng | 4 | 8 | 12 | 16 | 20 |
|---|---|---|---|---|---|
| Giá trị cơ sở (đ/cp) | 44.337 | 48.753 | 53.170 | 57.586 | 62.002 |

---

## 2. Kiểm lại số đầu vào

| Số | Brief/fact sheet | BCTC gốc | Ghi chú |
|---|---|---|---|
| Giá | 48.350 (BQ 30/10) | DNSE 48.350, 14:45:06 30/10 | Khớp |
| "~4.900 tỷ cho vay CTCK" (ĐHĐCĐ 04/2026) | 4.900 | 4.927,9 (01/01/26) → **4.223,4** (30/09/26) | Giảm 704 trong 9T, nhưng cùng lúc **mua mới 1.792,4 trái phiếu** |
| VRG cổ đông lớn | "thuộc hệ VRG" | Không có trong danh sách CĐ lớn | Sửa giả thuyết |
| Cao su | "nếu còn mảng" | Không có vườn cây | Bỏ |
| "01/01/2026 trình bày lại" | — | TM42: phân loại lại theo TT99 | Không đổi lãi/VCSH |

---

## 3. Chất lượng lợi nhuận

### 3a. KQKD hợp nhất [Q3HN tr.7–8]

| | Q3/26 | Q3/25 | YoY | 9T/26 | 9T/25 | YoY |
|---|---|---|---|---|---|---|
| DTT | 2.425,8 | 2.233,7 | +8,6% | 7.003,0 | 6.304,3 | +11,1% |
| LN gộp | 351,6 | 366,4 | −4,1% | 1.072,2 | 977,5 | +9,7% |
| DT tài chính | 242,8 | 173,7 | +39,8% | 646,1 | 619,2 | +4,3% |
| CP tài chính (lãi vay) | 117,5 (88,8) | 45,4 (45,6) | ×2,6 | 267,6 (211,4) | 152,3 (117,0) | +76% |
| LDLK (chủ yếu NTC) | 10,2 | 28,0 | −64% | 47,8 | 46,2 | +3% |
| LN khác | −0,9 | 0,6 | | 75,6 | −5,7 | Một lần: thanh lý BCC 67,8 |
| LNTT | 462,3 | 468,0 | −1,2% | 1.465,8 | 1.373,5 | +6,7% |
| **LNST mẹ** | **344,4** | **365,8** | **−5,9%** | **1.078,0** | **1.001,9** | **+7,6%** |

- **Năm 2025 [KT25]:** DTT 8.596,2; LNTT 1.838,5; LNST mẹ 1.322,9 (EPS 4.972). Suy ra Q4/25: LNTT 465,0, LNST mẹ 321,0.
- **Một lần trong 9T/26:** lãi thanh lý BCC với Thế Hệ Mới 67,8 và lãi bán khoản đầu tư 16,5 (9T/25: 124,2). Loại hai khoản này thì 9T/26 LNTT core ≈ 1.381,5, **+10,6%** so với 9T/25 sau khi cũng loại 124,2 khỏi 9T/25 (ước lượng; 9T/25 còn có thể có khoản một lần khác chưa tách).
- **Kế hoạch 2026 (LNST HN 874,2) đã vượt sau 9T (1.178,3).** Kế hoạch rất thấp, nên không phải tín hiệu bất ngờ.

### 3b. Theo mảng 9T [Q3HN TM25/27] — chỉ có số 9T, Q3 riêng chưa tách được

| Mảng | DT 9T/26 | GVHB | LN gộp | Biên | LN gộp 9T/25 | Bền? |
|---|---|---|---|---|---|---|
| Điện, nước KCN | 5.730,3 | 5.233,3 | **497,0** | 8,7% | 439,9 | Bền, theo lấp đầy; biên mỏng; phải trả Điện lực Tây Ninh 168,7 |
| Dịch vụ tiện ích KCN khác | 514,8 | 276,4 | **238,4** | 46% | 212,9 | Bền |
| Cho thuê đất đã PT hạ tầng | 341,8 | 106,0 | **235,8** | 69% | 211,8 | **Phân bổ**, phi tiền mặt (tiền đã thu từ trước) |
| Bán BĐS | 74,4 | 31,1 | 43,3 | 58% | 78,2 | Lumpy (KDC Thuận Lợi, Phước Đông New City) |
| Hàng hoá/thành phẩm | 121,3 | 95,3 | 25,9 | 21% | 11,2 | |
| Dịch vụ khác + xây dựng | 220,4 | 188,6 | 31,9 | | 23,6 | |
| **Tổng** | 7.003,0 | 5.930,8 | **1.072,2** | 15,3% | 977,5 | |

- **Doanh thu cho thuê đất ghi nhận phân bổ, không ghi một lần.** DT chưa thực hiện tăng 1.701,8 trong 9T (13.375,4 → 15.077,2), tức tiền thuê mới thu thêm. Đây là chỉ báo **cho thuê mới tốt hơn** DT kế toán. ~1.702 cộng phân bổ 342 ⇒ tiền thuê thu mới ~2.044 trong 9T (ước lượng; có thể gồm thu đợt sau của hợp đồng cũ).
- **Một lần/thanh lý:** thanh lý BCC 67,8 (TN khác). Khoản Baikai→Billion 68,1 là phải trả, không phải lãi.
- **Chất lượng lãi tài chính:** lãi tiền gửi + cho vay 602,0 trên số dư bình quân ≈ (10.038 + 11.414)/2 + TP ≈ 11.600 ⇒ ~6,9%/năm (ước lượng). Chi phí vay 211,4 trên ~5.150 ⇒ ~5,5%/năm. **Chênh lãi mang theo tín dụng doanh nghiệp/CTCK**, không phải lãi tiền gửi thuần.

### 3c. Dòng tiền 9T/26 [Q3HN tr.9–10]
- CFO báo cáo 1.340,9, nhưng đã trừ 1.840,5 **mua chứng khoán kinh doanh (trái phiếu)** xếp vào hoạt động kinh doanh. CFO trước CK KD = **3.181,5**. Trong đó tăng phải trả 1.793,2 (chủ yếu tiền thuê trả trước).
- Capex 569,4; cho vay/mua công cụ nợ ròng −1.227,6; thu lãi 488,4.
- Cổ tức trả 1.155,5; vay ròng +676,6. **Tiền mặt giảm 446,6**, còn 400,8.

---

## 4. Bảng cân đối — net cash THẬT

| 30/09/2026 | Hợp nhất | Riêng (mẹ) |
|---|---|---|
| Tiền + tương đương | 400,8 | 221,2 |
| Tiền gửi có kỳ hạn (HTM) | 7.187,6 | 6.912,2 (HTM mẹ; chưa tách tiền gửi/cho vay) |
| Cho vay CTCK | 4.223,4 | (trong HTM mẹ / con — chưa tách) |
| Trái phiếu DN | 1.792,4 | 1.792,4 (**toàn bộ ở mẹ**) |
| Cổ phiếu KD (GTHL) | 203,9 | — |
| **Tổng tài sản tài chính** | **13.808** | **8.925,8** |
| Vay (NH + DH) | 5.494,2 (tín chấp NH 4.374) | 5.491,9 |
| **Net tài chính** | **8.313,9** | **3.433,9** |
| CP phải trả DH: hoàn thành hạ tầng đã cho thuê | 3.262,8 | 2.652,8 |
| **Net sau nghĩa vụ hạ tầng** | **5.051** (≈20.860 đ/cp) | **781** |
| DT chưa thực hiện (tiền thuê trả trước) | 15.077,2 | 10.569,6 |

- **Mẹ gần như không có net cash thật** sau nghĩa vụ hạ tầng (781). Phần dư nằm ở các công ty con (ước lượng ~4.270 = hợp nhất − mẹ, gồm cả phần NCI). **Cổ tức về mẹ phụ thuộc chia từ con.**
- **Tiền phải tiêu tiếp:** CP hạ tầng phải trả 3.262,8; XDCB dở dang 2.205,6 (Phước Đông-Bời Lời 1.268,9). Đền bù Phước Đông GĐ3: đã tạm ứng 2.421,1; HM vay VCB 1.509; GPMB >90% [CBTT].
- **Phải thu khác ngắn hạn 2.675,6** gồm tạm ứng đền bù 2.529,6. Phải thu khác dài hạn 1.601,8 gồm **tạm ứng nhân viên 643,7** và góp BCC 667,0.
- **HTK nhỏ (137,4)**: đất cho thuê nằm ở BĐSĐT 6.417,1, không nằm ở hàng tồn kho.

---

## 5. Cổ đông, thanh khoản, sizing

- **Cổ đông lớn** [AR25, 23/03/2026] như §0.
  - Nước ngoài sở hữu 2,60%, room 49% (còn ~46,4%, tính tay, chưa đối chiếu VSDC).
  - Free float ước lượng ≈ 100 − 19,79 − 9,00 − 7,11 − 7,56 ≈ **56,5%** (ước lượng; chưa tính người liên quan).
- **Thanh khoản [BQ]:**
  - ADV 3 tháng 4,11 tỷ; 6 tháng 6,64 tỷ. Từ 07/2026 chỉ 3,4–4,7 tỷ/phiên (năm 2025: 18–68).
  - Lý do sụt chưa rõ, xem G6.
  - Biên độ giá 12–13 tháng: 46.600–64.500 (chưa điều chỉnh; cổ tức 4.000 đ GDKHQ 14/05/2026: 59.000 → 54.900).
- **Sizing** (tiền lệ ≤0,5–1,0% NAV):
  - Ở ADV ~4 tỷ, mua 20% ADV mỗi phiên ≈ 0,8 tỷ/phiên.
  - Vị thế 1% NAV của book ~50 tỷ (0,5 tỷ) cần khoảng 1 phiên; ra hàng khi xấu có thể chậm và trượt giá lớn. Ước lượng, không phải khuyến nghị.

## 6. Pháp lý, quản trị — ⚠️ WARNING mức TRUNG BÌNH

1. **Tín dụng phi ngân hàng 6.016:**
   - Cho vay CTCK 4.223,4: 68,93% không có tài sản bảo đảm của bên vay, chỉ có "thỏa thuận hợp tác với bên thứ ba". Bên vay và lãi suất không công bố.
   - Trái phiếu 1.792,4: lớn nhất là **CTCP Thời Đại Mới T&T 1.000,7**, mua trong 9T/26, GTHL chưa xác định.
   - Hai khoản này được tài trợ một phần bằng **vay ngân hàng tín chấp**.
   - Rủi ro "scandal di cư": lợi ích có thể được chuyển ra ngoài qua kênh cho vay/đầu tư. **Chưa có bằng chứng sai phạm**; đây là cờ cấu trúc.
2. **BCC với CTCP XD&PT Thế Hệ Mới** (SIP giữ 18,89%, giá gốc 201,0):
   - Hợp đồng 29/04/2025 tới 2060, góp vốn 667,0.
   - Nhóm SIP nhận DT nhà xưởng; **Thế Hệ Mới nhận toàn bộ DT "hoạt động đầu tư khác"** (điện mặt trời, logistics, đầu tư tài chính, BĐS khác) [TM7(iii)].
   - BCC cũ (2023) đã thanh lý, SIP lãi 67,8.
   - Phân chia này cần được giải thích.
3. **Tạm ứng nhân viên 643,7 để mua đất** [TM7(iv)].
4. **Nhân sự:** miễn nhiệm PTGĐ Trần Ngọc Vân 21/05/2026; thay thành viên BKS 21/04/2026. **Chủ tịch bán 3,7 triệu cp** (~1,5% vốn) từ 10/06/2026, sau GDKHQ cổ tức 40%.
5. **Đền bù/GPMB:** Phước Đông GĐ3 >90%, mục tiêu xong 2026; Long Đức 2 đang điều chỉnh quy hoạch 1/2000. Chưa thấy tranh chấp hay khởi tố trong CBTT đã tải. **Chưa quét HOSE/UBCK/vietstock**, nên sự vắng mặt chưa được xác minh (G5).
6. **Kiểm toán:** EY, ý kiến 2025 chấp nhận toàn phần, không nhấn mạnh. **Q3/2026 chưa soát xét.**

## 7. Comps KCN [BQ 30/10/2026; PE/PB theo BQ, TTM tới quý BQ có]

| Mã | Giá | PE | PB | DY | ROE5Y | ADV 1T (tỷ) |
|---|---|---|---|---|---|---|
| **SIP** | 48.350 | 8,2 (tự tính 8,37) | 2,18 | 10,3% | 29,7% | 4,2 |
| IDC | 34.200 | 7,8 | 1,53 | 8,8% | 30,0% | 41,9 |
| NTC | 128.000 | 12,6 | 2,05 | 4,7% | 33,6% | 1,1 |
| PHR | 31.000 | 8,1 | 1,56 | 4,5% | 17,9% | 13,4 |
| VGC | 42.200 | 10,5 | 1,56 | 10,4% | 16,6% | 35,5 |
| KBC | 26.000 | 14,0 | 0,88 | 0% | 7,9% | 33,5 |
| SZC | 19.300 | 21,7 | 1,14 | 5,2% | 14,7% | 10,6 |
| BCM | 38.400 | 19,0 | 1,73 | 2,9% | 12,2% | 22,5 |
| LHG | 26.500 | 4,6 | 0,68 | 7,9% | 15,1% | 1,3 |
| D2D | 21.150 | 34,6 | 1,11 | 23,6% (đột biến) | 14,2% | 1,0 |
| SZL | 27.950 | 7,5 | 1,72 | 8,9% | 18,1% | 0,4 |
| TIP | 15.700 | 4,5 | 0,53 | 10,8% | 11,9% | 0,3 |

- **SIP rẻ hơn trung vị PE** (~10,5 trên 11 peer) và ROE cao, nhưng **PB cao**: VCSH nhỏ vì chi cổ tức lớn và vì 15.077 tiền thuê treo ở nợ phải trả. **So gần nhất là IDC** (cũng có điện nước + KCN): PE 7,8, DY 8,8%, thanh khoản gấp 10 lần.
- Lịch sử PE của SIP [BQ]: 2024–Q1/2025 ~13–16; từ 04/2025 ~9,6–11,4; từ 05/2026 ~8,1–9,6. Định giá đã co dần. PE_MA5Y 12,2.

## 8. Mốc kiểm chứng — HAI chiều

| Mốc (ngày) | Đổi nhận định LÊN nếu | Đổi nhận định XUỐNG nếu |
|---|---|---|
| **BCTC năm 2026 kiểm toán (~31/03/2027)** | EY không ngoại trừ/nhấn mạnh về cho vay CTCK/TP; dư nợ cho vay CTCK giảm < 3.000 hoặc công bố bên vay + TSĐB | Có dự phòng/ngoại trừ/nhấn mạnh ở TM4; TP T&T bị gia hạn/không định giá được; tăng thêm tín dụng phi ngân hàng |
| **BCTC Q4/2026 (~30/01/2027)** | DT chưa thực hiện tăng tiếp > +500 trong Q4 (cho thuê mới); Q4 LNST mẹ ≥ 321 (Q4/25) | Q4 LNST mẹ < 300 với chi phí lãi tăng tiếp; tạm ứng nhân viên/đền bù tăng mà không có hợp đồng thuê |
| **ĐHĐCĐ 2027 (~04/2027)** | Cổ tức tiền 2026 ≥ 30% VĐL; công bố giá thuê/m² và tiến độ Phước Đông GĐ3 | Cổ tức chỉ 10% sàn trong khi lãi giữ nguyên; thêm BCC/đầu tư ngoài ngành |
| **Cho thuê đất 2026 (AR26)** | ≥ 60 ha (kế hoạch) | ≤ 30 ha lần 2 liên tiếp (2025: 28,6) |
| Thanh khoản | ADV 3T trở lại > 10 tỷ | Thêm cổ đông lớn bán thoả thuận |

## 9. Đọc ngành (Bobby) — đối chiếu

Nguồn: [Bobby] `sector_read_kcn_cho_thue_dat_20261101.md`, blind. Có lúc 11:33 ICT, sau khi viết bản nháp; đọc trước khi chốt.

| Điểm của Bobby | Đối chiếu SIP | Hệ quả |
|---|---|---|
| Giá chào đi ngang: +1,5–1,7% YoY, 185 USD/m² | AR25: giá SIP "đi ngang" 2025 | Khớp; không giả định tăng giá thực |
| **Phân hoá lõi/vệ tinh:** TP.HCM lấp đầy 86%, giá +6,8%; **Tây Ninh 61%, −6,8%** | 678/937 ha còn lại (72%) là **Phước Đông B (Tây Ninh)**, mới lấp 25%; đất lõi còn ít: LMX3 97,7 ha (HCM), Đông Nam 21,5, Lộc An-Bình Sơn 115,5 (Đồng Nai, gần Long Thành) | Lý do P nghiêng xuống và tốc độ cơ sở chỉ ~43 ha/năm |
| Hấp thụ đất hồi từ nền thấp (CBRE 9T +56%); xưởng xây sẵn −48% | DT chưa thực hiện +1.702 trong 9T/26 (tiền thuê mới) | Cùng chiều: 2026 cho thuê đất tốt hơn 2025 (ước lượng) |
| **Đền bù tăng theo bảng giá đất hằng năm** ⇒ biên dự án mới bị ép | Đền bù Phước Đông GĐ3 đã tạm ứng 2.421; Long Đức 2 chưa xong 1/2000 | Kịch bản xấu dùng 6 tỷ/ha ròng |
| **TT 99/2025: từ 2026 doanh thu thuê đất phải phân bổ** ⇒ LNST 2026 của nhóm từng ghi một lần giảm cơ học | **SIP đã phân bổ từ trước** (DT chưa thực hiện 13.375 tại 01/01/2026) ⇒ **lãi 2026 của SIP không gãy chuỗi** | **PE peer không so thẳng được.** Peer ghi một lần (cần kiểm từng mã) sẽ có PE 2026 phình ra cơ học. Cột PE peer ở §7 là TTM BQ, có thể đã trộn hai chế độ; chỉ là tham chiếu thô |
| Nhóm gắn DNNN: phân loại vốn (QĐ 40/2026), đền bù đất cao su | SIP không do VRG chi phối, không có vườn cao su | Ít liên quan |
| Pha: giữa chu kỳ, cung đuổi kịp cầu; ADMIN_GATED 0,40 / CYCLICAL 0,40 / STRUCTURAL 0,20 | | Không dùng PE cao cho khối đất |
| Mục "DD cần kiểm gì": diện tích ký mới, tiền khách trả trước, DT chưa thực hiện | Đã đo DT chưa thực hiện (+1.702); **diện tích ký mới 9T/26 chưa có** (G12) | Mốc §8 dùng DT chưa thực hiện |

Ngành cao su (`vn_sector_read_rubber_20261027.md`) **không áp dụng**: SIP không có vườn cây.

## 10. Giới hạn
- Q3/2026 chưa soát xét. BCTC 6T soát xét đã tải nhưng **chưa đọc trang-by-trang**; chưa so bản tự lập Q2 với bản soát xét.
- Doanh thu theo mảng chỉ có số 9T, nên Q3 riêng theo mảng chưa tách.
- Số liệu KCN lấy theo AR25 (31/12/2025), chưa có số 30/09/2026.
- Xem `GAPS.md`.
