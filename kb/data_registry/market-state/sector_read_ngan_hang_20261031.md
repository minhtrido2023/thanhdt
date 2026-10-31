---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-31. Không được cung cấp mã, giá cổ phiếu, BCTC, forward return hay giả thuyết của ai về ngân hàng mục tiêu, và không đi tìm chúng.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành ngân hàng thương mại VN, trọng tâm nhóm NHTM cổ phần tư nhân quy mô lớn (bán lẻ + doanh nghiệp + tài chính tiêu dùng + chứng khoán/bảo hiểm con). Gồm pipeline tín dụng và lãi suất (bảng 5 tầng), chất lượng tài sản và pháp lý, cấu trúc cạnh tranh, phân loại chế độ, FORECAST khoá trước, checklist DD.
as_of: 2026-10-31 (tin web ≤ 2026-10-31; dữ liệu nội bộ deposit/CCTG CSV tới 2026-10-26; không truy vấn ticker_financial, không đọc BCTC NH nào)
---

# SECTOR READ: Ngân hàng thương mại Việt Nam, as-of 31/10/2026 (Bobby, real-time BLIND)

Không phải episode VNINDEX, không tính vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày. **[UĐ]** ước đoán/suy luận
của Bobby. **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này, có thể sai, không dùng làm số pin. **(ước lượng)** = số tự tính
hoặc không kiểm chứng được.

## 0. Kiểm toán blind (đã đọc / chưa đọc / rò)
- **Đã đọc nội bộ:** `vn_macro_regime_history.md` (REGIME READ #2 13/10, MACRO UPDATE 14/10, đính chính nợ xấu Q2),
  `data/deposit_rate_vn_events.csv`, `cctg_rate_vn_events.csv`, `cctg_rate_vn_6m_events.csv`, `cctg_rate_vn_tier2_events.csv`,
  log `refresh_deposit_cctg_weekly_2026-10.log` (26/10). Định dạng theo `sector_read_thep_20261031.md`.
- **Không tra:** giá cổ phiếu, BCTC, khuyến nghị CTCK của bất kỳ NH nào; không truy vấn `ticker_financial`/`ticker`.
  Không mở bài tổng hợp xếp hạng LN Q3 theo từng NH (vietnambiz 31/10).
- **Rò thông tin cấp NH qua kết quả tìm kiếm (khai trung thực):** snippet có (a) số Q3/2026 của 3 NH quốc doanh (dùng ở mục 2
  làm bằng chứng Big-4, KHÔNG phải nhóm mục tiêu); (b) tiêu đề Q3 của một số NH tư nhân (một NH tư nhân lớn: "LN tăng nhờ tín
  dụng, áp lực nhóm 2"; 4 NH tư nhân nhỏ-vừa có nợ xấu/dự phòng tăng mạnh); (c) bảng VDSC tỷ lệ tăng tín dụng so với room của 3 NH
  tư nhân, tỷ trọng cho vay SXKD theo NH; (d) xếp hạng CASA Q2 theo NH; (e) doanh thu bảo hiểm của công ty con 2-3 NH tư nhân;
  (f) tỷ trọng tín dụng BĐS Q1 theo NH. Tôi **chỉ dùng ở mức ngành/nhóm** (con số tổng, khoảng min-max không tên). Không dùng
  bất kỳ số cấp NH tư nhân nào làm bằng chứng phân loại. Nếu NH mục tiêu nằm trong (b)-(f), người đọc nên biết snippet đã đi qua mắt
  tôi.

## 1. Pipeline cầu tín dụng, lãi suất, thanh khoản

### 1a. Vĩ mô nền [DK]
| Chỉ tiêu | Số | Nguồn · ngày |
|---|---|---|
| GDP | Q3/2026 **+9,95%**, 9T +9,01%; CN-XD +11,21% | Cục Thống kê công bố 03/10/2026 (VTC News, TBTC, VnExpress) |
| CPI | T9 **5,08% YoY** (+0,62% MoM, do xăng dầu); BQ 9T 4,52%; lạm phát cơ bản BQ 9T 4,26% (core T9 4,45% theo entry 13/10). CPI T10: chưa công bố (NSO ~06/11) | NSO 02-03/10/2026 (TC Kinh tế-Tài chính) |
| Lãi suất điều hành | Tái cấp vốn 4,5%, tái chiết khấu 3,0%, không đổi | `sbv_policy` verified 09/10/2026, log 26/10 |
| Fed | 3,75-4,00% sau lần tăng 16/09/2026 (1 nguồn SimianX); họp 27-28/10: **không có số kết quả** (TD Securities kỳ vọng giữ) | SimianX 15/10; TBTC 24/10 |
| Tỷ giá | Trung tâm **25.627** (23/10, −10đ/tuần); VCB 25.610/26.020; tự do 26.000-26.080; USD/VND liên NH giảm 5 tháng liên tiếp tới T10 | TBTC 24/10/2026; Elibook 22/10 |

### 1b. Tín dụng vs hạn mức [DK]
- Tín dụng toàn hệ thống **20,75 triệu tỷ, +11,59% YTD, +16,69% YoY** (30/09; PTĐ Phạm Thanh Hà, họp báo 03/10; VNBA 05/10).
  YTD 26/06 mới 7,41% ⇒ Q3 riêng khoảng +4,2pp (ước lượng). Tín dụng YoY giảm tốc: 18,26% (28/04) → 18,1% (26/06) → 16,69% (30/09).
- **Định hướng 2026 khoảng 15%**, "điều chỉnh phù hợp"; giao 1 lần/năm, kiểm soát theo quý; đa số NHTM được giao khoảng 13% đầu
  năm (vnbusiness 2026, đại diện NH nói). Khảo sát kỳ vọng TCTD quý IV: cả năm 16,4% (NHNN, entry 13/10).
- Tín dụng BĐS (kinh doanh BĐS) **2,519 triệu tỷ (30/06), +12,71% QoQ** (Bộ XD dẫn NHNN; TC KT-TC 23/08). Tỷ trọng BĐS/tổng
  khoảng 25,4-25,7% (entry 14/10). NHNN yêu cầu tín dụng BĐS không vượt tăng trưởng chung, có thể trừ room nếu vi phạm.
- Tiêu dùng: dư nợ đời sống + thẻ **4,62 triệu tỷ (T8), +21,75% YoY**; khối công ty tài chính khoảng 185 nghìn tỷ, +13,37%
  (VNBA, TC KT-TC 10/2026). Dự thảo nâng hạn mức khoản vay nhỏ 100 → 400 triệu (đề xuất, chưa hiệu lực).

### 1c. Bảng 5 tầng chi phí vốn / thanh khoản (as-of 31/10/2026)
| Tầng | Ô | Số | Nguồn · ngày |
|---|---|---|---|
| **A. Niêm yết hành chính** | Big-4 12M **online** | **6,8%** không đổi | CafeF 24/10, VietNamNet 22/10 (CSV 26/10) |
| | Big-4 12M **tại quầy** | **5,9% → 5,4%** (giảm 0,5pp sau CV 9608) | log refresh 26/10 (dẫn báo 19-25/10) |
| | Big-4 6M online / quầy | 6,6% / 3,5% (12/10, TRƯỚC cắt); sau 18/10: **không có số** | entry 13/10 |
| **B. Bán-hành-chính** | CCTG Big-4 12M (BIDV/VietinBank) | 7,4% (12/10); sau CV 9608: **không có số** (chuỗi chưa ghi 26/10 vì thiếu nguồn) | CSV 12/10; log 26/10 |
| | CCTG VCB 6M | 7,5% (12/10); sau 18/10: **không có số** | CSV 6M 12/10 |
| | Spread CCTG12M − TK online 12M | +0,6pp (12/10) | tự tính |
| | Trái phiếu cấp 2 Big-4 (biên trên tham chiếu) | +1,05 (2024) → +2,25/+2,3 (BIDV, 09/2026, bán 80,3%) → CTG NQ 16/09 trần +2,8 | entry 13/10 |
| **C. Ngoài Big-4** | Biên 12M 35 NH đầu T10 | 3,7-7,8% | TTTC Tiền tệ đầu 10/2026 |
| | Cắt niêm yết sau CV 9608 | >25 NH cắt, phần lớn −0,5pp, có NH −0,7pp (19-21/10) | Elibook 22/10 |
| | Lãi "ẩn"/thực trả | BQ 12M thực trả khoảng **8,45%**; một số NH tư nhân 6M **9,5-9,7%**; chênh niêm yết khoảng 2,5pp (1 nguồn, ước lượng của tác giả) | Elibook 19-22/10 |
| | Tiền gửi lớn / đặc biệt | 10% 12-13M ở 1 NH nhỏ (giữa T10); cộng lãi +2,2pp ở 1 NH số (tới hết T10); CCTG tư nhân lên tới 9,2% (13/10) | TC KT-TC 10/2026; CSV tier2 13/10 |
| | Spread tư nhân − Big-4 (12M) | khoảng +1,0-1,2pp niêm yết (ước lượng, 7,8-8,0 vs 6,8); thực trả khoảng +1,6pp (ước lượng) | tự tính |
| **D. Thị trường** | Liên NH (22/10) | **ON 4,31 / 1W 4,35 / 2W 5,01 / 1M 5,11 / 3M 6,93** (02/10: ON 2,73, 3M 6,73; 3M BQ T9 ≈6,98) | TBTC 24/10; entry 13/10 (VBMA) |
| | OMO | Tuần 19-23/10 **hút ròng 9.868 tỷ**; lưu hành **95.065 tỷ** (thấp nhất >1 năm; 02/10: 133 nghìn tỷ) | TBTC 24/10 |
| | Tín phiếu NHNN | **không có số** | — |
| | TPCP 10Y | Trúng thầu **4,43%** cuối T9 (+2bp); phiên 07/10 chào mua 17,6 nghìn tỷ / gọi 8 nghìn tỷ, mở thêm, huy động 12 nghìn tỷ ⇒ dư cầu, không phải Kho bạc neo giá | Báo Đấu thầu 10/10; CafeF/Tiền Phong 10/2026 |
| | USD/VND chính thức vs tự do | 25.627 trung tâm; VCB bán 26.020; tự do 26.000-26.080 (premium tự do ≈ 0 đến +60đ so VCB bán) | TBTC 24/10 |
| **E. Lượng** | Tín dụng vs huy động (cùng nguồn, cùng mốc) | NSO 28/09: huy động 9,78% vs tín dụng 10,89% (chênh 1,11pp). VDSC/TCBS 14/10: 11,22% vs 11,44% (0,22pp) — 2 nguồn khác phạm vi, KHÔNG trừ chéo | TC KT-TC 05/10; Elibook 22/10 |
| | LDR | 27 NH niêm yết Q2: **khoảng 114%** (108% cùng kỳ; định nghĩa thuần, Yuanta 24/08) | Mekong ASEAN 08/2026 |
| | Văn bản = thừa nhận áp lực vốn | **TT 50/2026** (30/09, hiệu lực 01/12): trần LDR 85→95% theo công thức mới khi chuyển LCR/NSFR. **CV 9608** (18/10): tăng trưởng tín dụng phải trừ số dư **mua lại LC miễn truy đòi** 2026 ⇒ thừa nhận kênh lách room. **CV 9736** (21/10): chuẩn cắt chuyển từ niêm yết sang **lãi BQ giao dịch mới**, mốc kỳ 11-20/10 | TBTC 18/10; Elibook 22/10; luatvietnam |

**Đồng thuận / phân kỳ:**
- **Hướng:** tầng A và C (niêm yết) **giảm** khoảng 0,5pp từ 19-21/10, do mệnh lệnh hành chính (CV 9608 kèm chế tài trừ room
  2026, hạ chỉ tiêu 2027, nâng tỷ lệ an toàn). Tầng A online 12M Big-4 **đi ngang** 6,8%. Tầng D **chặt lên** trong tháng
  (ON 2,7% → 4,3%, OMO lưu hành 133 → 95 nghìn tỷ, NHNN hút ròng): NHNN đang hạ giá niêm yết bằng công văn, đồng thời không bơm
  thanh khoản rẻ. 3M liên NH đứng khoảng 6,9-7,0%.
- **Mức:** chi phí vốn biên thật của NH tư nhân (thực trả 12M khoảng 8,45%, 6M 9,5-9,7%, cấp 2 Big-4 tham chiếu + 2,25-2,8pp ≈
  8,5-9,0% (ước lượng)) **cao hơn tầng A khoảng 1,6-2,2pp**. Phân kỳ này là thông tin, không phải nhiễu.
- **Cơ chế [UĐ, suy luận]:** CV 9736 đổi thước đo sang lãi BQ giao dịch mới ⇒ NH có thể "đạt chỉ tiêu" bằng dịch cơ cấu kỳ hạn/kênh
  (kéo giao dịch về kỳ ngắn, giảm tiền gửi lớn giá cao trong kỳ đo) mà chi phí vốn bình quân sổ sách không giảm tương ứng. Kết hợp
  LDR ~114% và TT 50 hiệu lực 01/12 (nới mẫu số) ⇒ áp lực lãi huy động bị **nén hành chính**, chưa được **giải** bằng cung tiền.
- **Độ tin cậy:** hướng (niêm yết giảm, biên thật không giảm) **trung bình-cao**; mức chênh 1,6-2,2pp **thấp-trung bình** (lãi thực
  trả chỉ 1 nguồn). Không đề xuất escalate. Ngưỡng đề xuất để user chốt (nếu muốn): ON liên NH > 5% 2 tuần liền **và** OMO lưu hành
  < 80 nghìn tỷ cùng lúc niêm yết đang bị ép giảm = dấu hiệu "nén hành chính" sắp vỡ.

### 1d. NIM toàn ngành [DK + UĐ]
- 27 NH niêm yết: NIM Q1/2026 giảm 16bp QoQ, thấp nhất nhiều năm (KBSV); **Q2/2026 3,15%** (+16bp QoQ, −10bp YoY) (Yuanta, Mekong
  ASEAN 08/2026). Q3/2026 toàn ngành: **không có số** (chưa có tổng hợp).
- Lãi suất BQ giao dịch mới (NHNN/Bộ TC): huy động 6,38-6,46% (20-30/09, +1,15-1,22pp YTD); cho vay **9,12%** (30/09, +1,03pp YTD)
  ⇒ chênh lệch biên giao dịch mới khoảng 2,7pp, hẹp đi khoảng 0,1-0,2pp YTD (ước lượng).
- CV 9608 đòi cho vay SXKD/ưu tiên giảm **1,5-2pp** trong khi huy động giảm 0,5pp. TCBS ước NIM **−3 đến −7bp**, LNTT ngành **−2
  đến −4%** nếu 3-5% dư nợ được giảm lãi (Elibook 22/10 dẫn TCBS 19/10). Gói cho vay ưu đãi NH công bố sau CV 9608: từ 10 nghìn tỷ
  đến khoảng 100 nghìn tỷ/NH.
- [UĐ] NH tư nhân thiên bán lẻ có tỷ trọng cho vay SXKD **< 30%** (VDSC, nhóm) ⇒ ít chịu chỉ thị cắt lãi cho vay ưu tiên hơn Big-4
  (51-66%), nhưng chịu chi phí vốn cao hơn (CASA thấp hơn, phụ thuộc tiền gửi kỳ hạn giá cao + GTCG). Ròng: **NIM nhóm tư nhân lớn
  Q4/2026-H1/2027 đi ngang đến giảm nhẹ**, không có dư địa mở rộng.

## 2. Chất lượng tài sản và pháp lý

### 2a. Nợ xấu, nhóm 2, bao phủ [DK]
| Chỉ tiêu | Số | Nguồn · ngày |
|---|---|---|
| NPL nội bảng toàn hệ thống (gồm NH KSĐB) | 3,31% (30/06), từ 3,44% cuối 2025 | Báo Đấu thầu 2026 |
| NPL nội bảng không gồm 5 NH KSĐB | **1,51%** (30/06), từ 1,69% | NHNN qua báo, 2026 |
| NPL 27 NH niêm yết (gộp) | **1,97-2,01%** Q2 (cao nhất quý II từ 2020); nợ xấu +17,5-21,4% YTD, 312,1 nghìn tỷ | SSI, VDSC, S&I (08/2026) |
| Loại 1 NH ngoại lệ | 1 NH chiếm 77,7% mức tăng; 26 NH còn lại NPL **giảm** 2,02 → 1,78% | TCBS (Báo Đấu thầu 21/09) |
| Nợ nhóm 2 | 1,30 → **1,45%** Q1→Q2 (SSI); 1,17 → 1,38% (TCBS, phạm vi khác); tăng 2 quý liên tiếp | SSI/TCBS 08-09/2026 |
| Bao phủ nợ xấu | **khoảng 79-83%** Q2 (95% Q2/2025; 143% Q3/2022) | SSI, S&I, Yuanta |
| Lãi dự thu | 230,7 nghìn tỷ (+61,3 nghìn tỷ YoY) | entry 13/10 |
| Xử lý nợ xấu 6T | 141,4 nghìn tỷ (−17,5% YoY), chủ yếu bằng dự phòng | NHNN qua báo 2026 |
| Q3/2026 nhóm quốc doanh (3 NH) | NPL tuyệt đối +17,6% đến +36% YTD; 1 NH tăng dự phòng ×8 (LN đi ngang), 1 NH giảm dự phòng −25% (LN +39%), 1 NH dự phòng +33% (LN +29%) | Vietstock, Người Quan Sát 10/2026 |
| Q3/2026 4 NH tư nhân nhỏ-vừa | nợ xấu +38% đến +78% YTD; dự phòng 9T +41% đến +172%; khoản phải thu tăng mạnh ở 1 NH | vietbao, nguoiquansat, doanhnghiepkinhtexanh 10/2026 |
| Công ty tài chính tiêu dùng | NPL 7,2% (2025; đỉnh 11,2% 2023); NPL cho vay đời sống tại NH > 4% | FiinGroup qua TC KT-TC 10/2026 |
| Dự báo CTCK | NPL ngành cuối 2026 khoảng 1,8%, bao phủ khoảng 85% (SSI); áp lực trích lập H2 tăng, nhất là NH bao phủ < 60% (VDSC) | 08/2026 |

**Đọc [UĐ]:** NPL ngành không bùng nổ (bỏ 1 NH ngoại lệ thì Q2 còn giảm), nhưng **tầng sớm** (nhóm 2, lãi dự thu, phải thu) xấu đi
diện rộng và **bao phủ giảm nhanh** (95 → ~80% trong 1 năm). Q3 cho thấy NPL tuyệt đối tăng cả ở Big-4 và NH nhỏ. Đây là pha
**sớm-giữa của chu kỳ xấu đi chất lượng tài sản**, độ trễ 4-8 quý sau năm tín dụng +19% (2025) [NỀN về độ trễ]. Lợi nhuận 2026 đến
nay được đỡ bởi **khối lượng** và ở một số NH bởi **giảm/ hoãn trích lập**; đó là nguồn rủi ro chính cho 4 quý tới.

### 2b. BĐS và TPDN [DK]
- Mở bán nhà ở Q3: TP.HCM tiêu thụ −66% QoQ (DKRA), HN mở bán −40% YoY (CBRE), tồn kho 51.950 căn/lô (BCĐ TW 13/10) (nguồn ở
  `sector_read_vlxd_nhe_aac_20261029.md`). Tín dụng BĐS Q2 +12,7% QoQ trong khi tiêu thụ Q3 gãy ⇒ dòng tiền chủ đầu tư phụ thuộc
  đảo nợ [UĐ].
- TPDN 9T/2026: phát hành **428,5 nghìn tỷ (+1%)**, riêng lẻ 370,6 nghìn tỷ; mua lại trước hạn T9 −56% YoY; NH là nhóm phát hành chính,
  T9 nhiều NH phát hành ≥ 9%/năm (3 năm); BĐS phát hành Q2 khoảng 38,8 nghìn tỷ, lãi phổ biến 12,5% (VBMA qua stockbiz, Báo PL,
  TC KT-TC 2026). Đáo hạn 10 tháng còn lại 2026 khoảng 194 nghìn tỷ (VBMA 02/2026); 12T tới 08/2027 khoảng 253 nghìn tỷ (1 nguồn).
  Vi phạm nghĩa vụ TPDN 12T 0,24% (entry 14/10). Chậm trả 2026: **không có số**.

### 2c. Khung pháp lý [DK, phần [NỀN] ghi rõ]
- **Luật TCTD sửa đổi (Luật 96/2025/QH15)**, thông qua 27/06/2025, hiệu lực **15/10/2025**: luật hoá NQ 42 (Điều 198a quyền thu giữ
  TSBĐ không cần toà án, điều kiện theo NĐ 304/2025 kèm nghĩa vụ trợ cấp sinh kế) (lsvn, TTTC Tiền tệ 2026). ⇒ thu hồi nợ đã xử lý
  rủi ro nhanh hơn, hỗ trợ thu nhập ngoài lãi (hoàn nhập/thu nợ ngoại bảng) 2026-2027 [UĐ].
- **TT 02/2023 (cơ cấu lại nợ giữ nhóm)** [NỀN]: đã hết hiệu lực 31/12/2024 (gia hạn bởi TT 06/2024); nợ cơ cấu còn lại chuyển nhóm
  thật dần 2025-2026. Không có số dư nợ cơ cấu còn lại toàn ngành: **không có số**.
- **Basel III — TT 14/2025/TT-NHNN** (ban hành 30/06/2025, hiệu lực 15/09/2025; thay hoàn toàn TT 41/2016 từ 01/01/2030): CAR tối
  thiểu 8%, CET1 4,5%, Tier 1 6%, lần đầu có bộ đệm vốn; mức 10,5% vào 2030 chỉ 1 nguồn phân tích (theleader, luatvietnam,
  thesaigontimes 2025-2026). ⇒ áp lực **tăng vốn cấp 1** (phát hành/giữ lại LN, hạn chế cổ tức tiền) 2026-2029.
- **TT 50/2026/TT-NHNN** (30/09, hiệu lực 01/12/2026): LDR 85→95% công thức mới khi chuyển LCR/NSFR (chậm nhất 01/10/2028); LCR
  50→100% 2028-2033; NSFR 90→100% 2028-2030 (entry 13/10). Nới ngắn hạn, siết cơ cấu kỳ hạn dài hạn.
- **Xử lý NH yếu kém:** 4 NH KSĐB đã chuyển giao bắt buộc (2024-2025) [NỀN]; SCB còn KSĐB, Chính phủ yêu cầu hoàn thiện phương án
  (SGGP, ngày bài chưa xác định); NĐ 359/2026 (VAMC, hiệu lực 06/11); QĐ 1890/QĐ-TTg (18/09) có hợp phần xử lý TCTD yếu kém (entry
  13/10). Chi phí ẩn với NH nhận chuyển giao: hỗ trợ vốn/thanh khoản đổi lấy ưu đãi room và có thể room ngoại cao hơn [NỀN].
- **CV 9608 (18/10/2026)** ngoài lãi suất còn **siết cho vay lách**: góp vốn/mua cổ phần công ty chưa niêm yết, góp vốn hợp đồng hợp
  tác dự án chưa đủ điều kiện, cho vay "bắc cầu"; nhận diện nhóm khách hàng liên quan (cùng quản lý, cùng TSBĐ, cùng dự án, cùng nguồn
  trả nợ); giám sát nhóm 2, nợ ngoại bảng, nợ cơ cấu, lãi dự thu (TBTC 18/10).

## 3. Cấu trúc cạnh tranh

| Mảng | Số / dữ kiện | Đọc cho nhóm tư nhân lớn [UĐ] |
|---|---|---|
| Big-4 quốc doanh vs tư nhân | Big-4 giữ niêm yết thấp (6,8% online, 5,4% quầy) và phát hành cấp 2 với biên rộng dần; tỷ trọng cho vay SXKD 51-66% vs tư nhân bán lẻ < 30% (VDSC) | Big-4 là "neo giá" hành chính; tư nhân trả premium khoảng 1-1,6pp để giữ thị phần huy động. Chỉ thị giảm lãi cho vay ưu tiên chủ yếu đè lên Big-4 |
| CASA | Toàn ngành **20,2%** Q2, đi ngang QoQ, −1,5pp vs cuối 2025; 22/27 NH giảm; nhóm dẫn đầu khoảng 32-35% (VietnamFinance; Yuanta 24/08) | Lãi suất kỳ hạn cao ⇒ tiền chạy khỏi không kỳ hạn; CASA là biến số NIM lớn nhất của NH bán lẻ. CASA tăng nhờ tiền gửi DN dễ đảo chiều |
| Bán lẻ / tiêu dùng / SME | Dư nợ đời sống + thẻ +21,75% YoY (T8); CTTC +13,37%; NPL CTTC 7,2% (2025) | Bán lẻ là động cơ tăng trưởng nhưng chất lượng tiêu dùng không bảo đảm (VNBA "cho vay có trách nhiệm"). Nới hạn mức khoản vay nhỏ (nếu ban hành) mở thêm cầu và rủi ro |
| Bancassurance | Phí khai thác mới nhân thọ 6T/2026 **−17% YoY** (10.787 tỷ), tổng phí −4%; bancas 44,9% phí khai thác mới (IAV) | Phí hoa hồng bảo hiểm nhân thọ chưa hồi; [NỀN] TT 67/2023 cấm bán chéo bảo hiểm đầu tư trong 60 ngày quanh khoản vay. Phí phi nhân thọ/công ty BH con tăng tốt hơn ở một số nhóm (snippet cấp NH, không dùng số) |
| Thu nhập ngoài lãi khác | Thu nợ ngoại bảng (Luật 96), phí thanh toán/thẻ; kinh doanh chứng khoán đầu tư chịu lợi suất TPCP tăng nhẹ (10Y 4,04% T1 → 4,43% T9) | Q2 ngành tăng LN mạnh "từ tín dụng và thu phí" (elibook 09/08) nhưng không có số toàn ngành |
| Lợi nhuận ngành | LNTT Q2 27 NH khoảng 95,7-111 nghìn tỷ (+25-27,6% YoY) (SSI, VDSC); MBS kỳ vọng Q3 +19,1% (dẫn bởi quốc doanh) | Nền 2026 cao ⇒ so sánh 2027 khó [UĐ] |
| FTSE nâng hạng (hiệu lực 21/09/2026) | Đợt 1 10% (21/09/2026), đợt 2 3/2027, đợt 3 6/2027 (1 nguồn; nguồn khác: 4 đợt tới 9/2027); gần 10 cổ phiếu NH vào FTSE GEIS kỳ 09/2026 | Cầu thụ động ngoại tập trung vào NH vốn hoá lớn còn room. [NỀN] room ngoại NH 30% (NH nhận chuyển giao bắt buộc có thể tới 49%). Đây là kênh **định giá**, không phải kênh LNST; không dùng làm luận điểm cơ bản |

## 4. Phân loại chế độ ngành (biến số quyết định LNST 4 quý tới)

| Nhãn | Xác suất | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,45** | Khối lượng (room 2026 khoảng 15% + điều chỉnh; chế tài hạ chỉ tiêu 2027 trong CV 9608; trừ LC miễn truy đòi; trần tăng tín dụng BĐS), giá (CV 9608/9736 ép huy động −0,5pp, cho vay ưu tiên −1,5-2pp), thanh khoản (TT 50 LDR 95% từ 01/12) đều do **văn bản** quyết, không do giá thị trường. Lần sửa CV trong 3 ngày (9608 → 9736) cho thấy NHNN điều hành ngắn hạn bằng mệnh lệnh |
| **CYCLICAL** | **0,35** | Chu kỳ chất lượng tài sản đến sau năm tín dụng +19%: nhóm 2 tăng 2 quý, bao phủ 95 → ~80%, NPL tuyệt đối Q3 tăng ở cả Big-4 và NH nhỏ; tiêu thụ BĐS Q3 gãy trong khi tín dụng BĐS Q2 +12,7% QoQ. Chi phí tín dụng là biến số dao động mạnh nhất của LNST 2027 |
| **STRUCTURAL** | **0,20** | LDR thuần khoảng 114%, CASA giảm, tín dụng/GDP khoảng 145% (entry 13/10), lộ trình LCR/NSFR 2028-2033 và Basel III 2030 ⇒ chi phí vốn dài hạn và nhu cầu vốn cấp 1 cao lên vĩnh viễn; nền vĩ mô Loại-1 STRUCTURAL_ACCUMULATION (ambiguous) |

- **Pha [UĐ]:** tăng trưởng tín dụng **giữa → muộn** nhịp (YoY giảm tốc từ 18% về 16,7%), NIM **đáy hẹp/đi ngang**, chất lượng tài
  sản **sớm-giữa pha xấu đi**, chi phí vốn biên **cao bị nén hành chính**. Giống 2018 về hình (tín dụng được ghìm dần bằng hành chính),
  giống 2011 một phần về cơ chế (niêm yết bị neo, giá thật lộ ở kênh lách). Không giống 2022 (không có trigger có tên, liên NH 3M
  < 7%).
- **Confidence: `ambiguous` (~60/40).** Chưa biết lớn nhất: (a) tổng hợp Q3 toàn ngành (NIM, nhóm 2, bao phủ) chưa có; (b) NHNN có
  nới room cuối năm hay giữ chặt theo CV 9608; (c) CV 9736 có làm giảm thật chi phí vốn BQ hay chỉ dịch cơ cấu; (d) kết quả FOMC
  27-28/10 và đường Fed 12/2026.

**Biến số chính quyết định LNST ngành Q4/2026-Q3/2027 (xếp theo độ nhạy, [UĐ]):**
1. **Chi phí tín dụng**: tốc độ chuyển nhóm 2 → nợ xấu, nhu cầu xây lại bao phủ từ ~80%, dòng tiền chủ đầu tư BĐS và TPDN đáo hạn
   (~253 nghìn tỷ tới 08/2027). Ngược chiều: thu hồi nợ nhờ Luật 96.
2. **NIM**: chỉ thị giảm lãi cho vay vs chi phí vốn biên dính (thực trả 8,45%), CASA, phần GTCG/cấp 2 giá cao trong cơ cấu vốn.
3. **Khối lượng tín dụng**: room cuối 2026 và chỉ tiêu 2027 (có thể thấp hơn cho NH bị chế tài), LDR mới từ 01/12.
4. **Thu nhập ngoài lãi**: bancas chưa hồi; thu nợ ngoại bảng; phí; lãi/lỗ chứng khoán đầu tư theo lợi suất TPCP.
5. **Vốn**: Basel III, cấp 2 đắt lên ⇒ pha loãng/cổ tức cổ phiếu, ROE pha loãng.
6. **Ngoại sinh**: Fed (3,75-4,00%, khả năng tăng 12/2026), USD/VND, giá dầu → CPI (T9 5,08%).

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-10-31; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm; không có nguồn ⇒ "không chấm được", không suy)

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | Tăng trưởng tín dụng toàn hệ thống cả năm 2026 (31/12/2026 vs 31/12/2025) **≥ 16,0%** | 0,70 | 2027-01-31 | NHNN họp báo/công bố đầu 01/2027 |
| F1b | Như F1 nhưng **≥ 18,0%** | 0,25 | 2027-01-31 | như trên |
| F2 | Big-4 tiết kiệm 12M **online** cao nhất ngày 31/03/2027 **≤ 6,8%** | 0,75 | 2027-03-31 | `deposit_rate_vn_events.csv` + báo cùng tuần |
| F2b | Như F2 nhưng **≤ 6,3%** | 0,30 | 2027-03-31 | như trên |
| F3 | CCTG 12M cao nhất Big-4 ngày 31/03/2027 **≤ 7,4%** | 0,60 | 2027-03-31 | `cctg_rate_vn_events.csv` |
| F4 | Lãi suất BQ huy động giao dịch mới VND (NHNN) tháng 3/2027 trong **[5,9%; 6,9%]** | 0,65 | 2027-04-30 | NHNN/Bộ TC công bố |
| F5 | Liên NH 3M BQ tháng 12/2026 **≤ 7,5%** | 0,75 | 2027-01-15 | VBMA báo cáo tuần (NHNN) |
| F6 | NPL nội bảng gộp 27 NH niêm yết tại 31/12/2026 trong **[1,8%; 2,3%]** | 0,70 | 2027-02-28 | tổng hợp CTCK (SSI/VDSC/S&I) sau BCTC Q4 |
| F6b | Như F6, **> 2,0%** | 0,50 | 2027-02-28 | như trên |
| F7 | Bao phủ nợ xấu gộp 27 NH niêm yết tại 31/12/2026 **< 90%** | 0,80 | 2027-02-28 | như trên |
| F8 | NIM gộp 27 NH Q4/2026 **≤** NIM Q3/2026 | 0,65 | 2027-02-28 | tổng hợp CTCK |
| F9 | LNTT gộp 27 NH niêm yết cả năm 2026 tăng **≥ 12% YoY** | 0,65 | 2027-02-28 | tổng hợp CTCK |
| F10 | NHNN **tăng** lãi suất tái cấp vốn (khỏi 4,5%) trước 31/03/2027 | 0,15 | 2027-03-31 | NHNN quyết định |
| F11 | TT 50/2026 có hiệu lực đúng 01/12/2026, không hoãn/sửa trần LDR 95% trước ngày đó | 0,85 | 2026-12-01 | NHNN/thuvienphapluat |
| F12 | Tỷ giá trung tâm ngày 31/03/2027 **≤ 26.000** | 0,75 | 2027-03-31 | NHNN |

Ghi chú [UĐ]: F1 dựa trên Q4 các năm gần đây cộng thêm khoảng 5-6pp (2024: 9T khoảng 9% → cả năm 15,1%; 2025: 9T khoảng 13,4% →
khoảng 19%) [NỀN về số 2024-2025], trừ đi chế tài room CV 9608 ⇒ trung tâm khoảng 16,8% (ước lượng). F2 nghiêng giữ vì Big-4 đã
giữ 6,8% suốt chu kỳ tăng; F2b thấp vì chi phí vốn biên chưa giảm. F7/F8 nghiêng xấu theo mục 2a và 1d. F10 thấp vì định hướng
điều hành 2026 là giảm lãi bằng hành chính chứ không tăng điều hành.

## 6. Chỉ báo dẫn dắt (theo dõi tuần/tháng/quý)
1. Tầng D hàng tuần: ON/1M/3M liên NH, OMO lưu hành và bơm/hút ròng, tín phiếu (VBMA, TBTC thứ Bảy).
2. Tầng B/C: CCTG Big-4 6M/12M sau CV 9608 (chuỗi đang thiếu nguồn), biểu 12M NH tư nhân lớn, tiền gửi lớn/cộng lãi.
3. NHNN: lãi BQ giao dịch mới (huy động/cho vay), tín dụng YTD tháng, văn bản room/chế tài, TT 50 thi hành 01/12.
4. Tổng hợp Q3 (đầu-giữa 11/2026): NIM, nhóm 2, bao phủ, lãi dự thu, phải thu khác, nợ BĐS.
5. BĐS: tiêu thụ Q4 (DKRA/CBRE/VARS), TPDN đáo hạn và chậm trả (VBMA tháng).
6. CPI T10 (~06/11), core; Fed 12/2026; USD/VND trung tâm và tự do.

## 7. DD cần kiểm gì (một NHTM cổ phần tư nhân cỡ lớn; số lấy từ BCTC hợp nhất + riêng lẻ, thuyết minh, BCTN, Basel Pillar 3)
Ngưỡng trong ngoặc là ngưỡng **soát** do Bobby đề xuất [UĐ], không phải chuẩn quy định trừ khi ghi rõ.

**A. Thu nhập và hiệu quả**
1. **NIM** theo quý 8-12 quý (hợp nhất VÀ riêng lẻ — tách phần công ty tài chính); lợi suất tài sản sinh lãi vs chi phí vốn; so với ngành
   (Q2 3,15%). Cờ: NIM riêng lẻ giảm > 30bp YoY.
2. **Chi phí vốn**: cơ cấu huy động (không kỳ hạn / có kỳ hạn / GTCG / vay TCTD khác / cấp 2); lãi suất GTCG và cấp 2 phát hành 2026.
3. **CASA** (định nghĩa: tiền gửi không kỳ hạn / tổng tiền gửi KH), tách cá nhân vs DN. Cờ: CASA DN > 50% tổng CASA (dễ đảo chiều).
4. **CIR** (chi phí hoạt động / TOI), xu hướng; cờ: CIR giảm đồng thời chi phí dự phòng giảm (LN "làm đẹp").
5. **Thu nhập ngoài lãi** tách: phí thanh toán/thẻ, **bancassurance** (thuyết minh phí hoa hồng; phí trả trước độc quyền được phân bổ
   bao nhiêu/năm, còn lại bao nhiêu năm), thu nợ ngoại bảng, kinh doanh ngoại hối, chứng khoán đầu tư/kinh doanh. Cờ: thu nợ ngoại bảng +
   chứng khoán > 25% LNTT.
6. **ROE / ROA** hợp nhất và riêng lẻ; ROE trước dự phòng (PPOP/VCSH) để tách hiệu ứng trích lập.

**B. Chất lượng tài sản**
7. **Nợ xấu** (nhóm 3-5) tỷ lệ + tuyệt đối, **nợ nhóm 2** (cờ: > 2% hoặc +> 20% QoQ), tách theo đơn vị (NH mẹ vs CTTC).
8. **LLR / bao phủ** (dự phòng chung + cụ thể / nợ xấu); cờ: < 70% hoặc giảm > 15pp/năm.
9. **Chi phí tín dụng** (dự phòng / dư nợ BQ) 8 quý; so tốc độ hình thành nợ xấu mới (NPL formation = Δ nợ xấu + nợ xoá sổ).
10. **Nợ xoá sổ** trong kỳ và **nợ ngoại bảng** (thuyết minh); **nợ cơ cấu** còn lại (thuyết minh hoặc Pillar 3).
11. **Lãi dự thu** (cờ: > 2% tổng tài sản hoặc tăng nhanh hơn dư nợ), **phải thu khác**, tài sản Có khác — kênh treo rủi ro thật.
12. **Mua lại LC miễn truy đòi / chiết khấu chứng từ** (thuyết minh cho vay và tài sản khác) — từ CV 9608 bị trừ khỏi room.

**C. Phân bổ tín dụng và rủi ro tập trung**
13. **Tín dụng BĐS** (kinh doanh BĐS + xây dựng + cho vay mua nhà cá nhân, tách riêng); cờ: kinh doanh BĐS > 15% dư nợ hoặc +> tăng trưởng chung.
14. **Trái phiếu DN nắm giữ** (theo ngành phát hành, BĐS bao nhiêu; dự phòng TPDN); TPDN được NH bảo lãnh/phân phối.
15. **Tập trung**: top-10/20 khách hàng và nhóm liên quan / VCSH; cho vay bên liên quan và cổ đông lớn (thuyết minh giao dịch bên liên
    quan); cờ theo tiêu chí nhận diện nhóm của CV 9608 (cùng TSBĐ, cùng dự án, cùng nguồn trả nợ).
16. **Tiêu dùng không TSBĐ** tỷ trọng; NPL và chi phí dự phòng của CTTC con; nguồn vốn CTTC vay từ mẹ.

**D. Thanh khoản và vốn**
17. **LDR** theo TT 22 (đến 30/11/2026) và công thức TT 50 (từ 01/12/2026); **tỷ lệ vốn ngắn hạn cho vay trung dài hạn**; LCR/NSFR nếu
    công bố. Cờ: LDR > 85% tiệm cận trần cũ.
18. **CAR** (TT 41 và, nếu đã áp dụng, TT 14) + **CET1/Tier 1** tách; cờ: CET1 < 9% (ước lượng ngưỡng an toàn khi bộ đệm áp dụng).
19. **Cấp 2 / GTCG** lưu hành, lịch đáo hạn, lãi suất; kế hoạch tăng vốn (phát hành riêng lẻ, ESOP, cổ tức cổ phiếu) ⇒ pha loãng.
20. **Room tín dụng** được giao 2026 vs đã dùng (thường nêu ở ĐHCĐ/BCTN), rủi ro bị hạ chỉ tiêu 2027 theo chế tài CV 9608.

**E. Công ty con và quản trị**
21. **Hợp nhất vs riêng lẻ**: đóng góp LNTT từng con (CTTC, chứng khoán, bảo hiểm); vốn mẹ đã rót, cam kết hỗ trợ thanh khoản.
22. **CTCK con**: dư nợ margin / VCSH, danh mục TPDN tự doanh, bảo lãnh phát hành TPDN cho khách của mẹ.
23. **Công ty bảo hiểm con**: tỷ lệ kết hợp (combined ratio), dự phòng nghiệp vụ, danh mục đầu tư, tỷ lệ phí từ khách hàng của mẹ.
24. **Sở hữu ngoại** còn room (trần 30% [NỀN]), cổ đông chiến lược, cổ đông nắm > 5% và vay của họ.
25. Ý kiến kiểm toán (ngoại trừ/nhấn mạnh), chênh LN trước/sau kiểm toán, đổi kiểm toán viên, thanh tra NHNN gần nhất.

## 8. Điều gì làm tôi sai
- Tổng hợp Q3 cho thấy nhóm 2 giảm QoQ và bao phủ tăng lại > 90% ⇒ hạ CYCLICAL (chu kỳ xấu đi đã qua đỉnh).
- NHNN nới room đáng kể cuối năm (tín dụng 2026 ≥ 18%) mà liên NH không căng ⇒ ADMIN_GATED nghiêng chiều thuận, LN 2026-H1/2027 tốt hơn.
- CCTG Big-4 và thực trả tư nhân giảm thật ≥ 0,5pp (không chỉ niêm yết) trong 11-12/2026 ⇒ áp lực NIM nhẹ hơn tôi đọc.
- Ngược lại: ON > 5% kéo dài, CCTG Big-4 ≥ 7,7%, hoặc một NH/1 chủ đầu tư lớn có trigger có tên ⇒ chuyển sang đọc episode
  (CONFIDENCE_LIQUIDITY trên nền Loại-1, mặc định MIXED/ambiguous).

**Không phải khuyến nghị mua/bán.**

## Nguồn (ngày công bố)
- VNBA, dư nợ 20,75 triệu tỷ 30/09/2026 — 05/10/2026: https://vnba.org.vn/vi/du-no-tin-dung-toan-he-thong-dat-khoang-20-75-trieu-ty-dong-tinh-den-30-9-2026-23786.htm
- VietnamFinance, tín dụng 20,75 triệu tỷ — 10/2026: https://vietnamfinance.vn/tin-dung-dat-2075-trieu-ty-nhnn-tiep-tuc-mo-du-dia-cho-vay-d151521.html
- Mekong ASEAN, tín dụng 7,41% đến 26/06: https://mekongasean.vn/den-266-tang-truong-tin-dung-toan-he-thong-dat-741-56884.html
- vnbusiness, định hướng tín dụng 2026 khoảng 15%: https://vnbusiness.vn/nganh-ngan-hang-2026-dinh-huong-tang-truong-tin-dung-15-uu-tien-on-dinh-vi-mo.html ; https://vnbusiness.vn/tin-dung-2026-giam-toc-ngan-hang-nha-nuoc-siet-room-kiem-soat-chat-bat-dong-san.html
- TBTC, CV 9608 — 18/10/2026: https://thoibaotaichinhvietnam.vn/ngan-hang-nha-nuoc-yeu-cau-giam-lai-suat-huy-dong-toi-thieu-0-5-siet-chat-cac-khoan-vay-lach-quy-dinh-205558.html
- Luatvietnam, CV 9736 (lãi BQ giao dịch mới): https://luatvietnam.vn/legal-updates/official-dispatch-no-9736-banks-must-reduce-average-deposit-interest-rates-for-terms-of-6-months-or-longer-by-at-least-05-per-annum-892-114680-article.html
- Elibook, "NHNN đổi từ giảm thực đơn sang giảm hoá đơn" — 22/10/2026: https://elibook.vn/2026/10/22/lai-suat-nhnn-doi-tu-giam-thuc-don-sang-giam-hoa-don-ky-vong-dinh-phang/
- TBTC, thị trường tiền tệ tuần 19-23/10 — 24/10/2026: https://thoibaotaichinhvietnam.vn/thi-truong-tien-te-tuan-19-23-10-bom-von-qua-kenh-omo-nho-giot-ty-gia-usd-ngan-hang-ha-nhiet-205870.html
- TTTC Tiền tệ, lãi suất đầu tháng 10/2026: https://thitruongtaichinhtiente.vn/lai-suat-dau-thang-10-2026-tiet-kiem-giu-nhip-on-dinh-chung-chi-tien-gui-hut-khach-85944.html
- TC KT-TC, lãi suất tháng 10 ưu đãi tới 9,6%: https://tapchikinhtetaichinh.vn/lai-suat-ngan-hang-vao-thang-10-nhieu-lua-chon-tren-7-nam-uu-dai-len-toi-9-6-nam-168422.html
- Báo Đấu thầu, TPCP tháng 9 (10Y 4,43%) — 10/10/2026: https://baodauthau.vn/huy-dong-hon-70139-ty-dong-trai-phieu-chinh-phu-qua-dau-thau-trong-thang-9-post209610.html
- Tiền Phong / CafeF, TPCP phiên đầu T10 kỳ hạn 10 năm đắt hàng: https://tienphong.vn/trai-phieu-chinh-phu-hut-gan-300000-ty-dong-ky-han-10-nam-dat-hang-post1884254.tpo
- VTC News, GDP Q3 9,95% — 03/10/2026: https://vtcnews.vn/gdp-quy-iii-2026-tang-9-95-9-thang-tang-9-01-ar1043199.html
- TC KT-TC, CPI 9T 4,52%: https://tapchikinhtetaichinh.vn/cpi-9-thang-tang-4-52-lam-phat-co-ban-duy-tri-muc-thap-hon-168572.html
- SimianX, lịch FOMC + lần tăng 16/09/2026 (1 nguồn) — 15/10/2026: https://www.simianx.ai/vi/stories/fed-interest-rate-decision-latest-fomc-result-and-history
- Doanh nghiệp Hội nhập, kỳ vọng Fed tháng 10 — 16/10/2026: https://doanhnghiephoinhap.vn/thi-truong-ha-ky-vong-fed-tang-lai-suat-thang-10-151788.html
- Mekong ASEAN, NIM Q2 (Yuanta): https://mekongasean.vn/nim-ngan-hang-phuc-hoi-chung-khoan-yuanta-chi-ra-nhom-co-loi-the-ve-chi-phi-von-58898.html
- The Leader, KBSV NIM 2026: https://theleader.vn/kbsv-bien-lai-nganh-ngan-hang-kho-phuc-hoi-trong-nam-2026-d46884.html
- TBTC, nợ xấu/ LN Q2 (VDSC, SSI): https://thoibaotaichinhvietnam.vn/lai-suat-dau-vao-len-mat-bang-moi-ngan-hang-truoc-ap-luc-chi-phi-von-va-no-xau-199113.html ; https://vietnamfinance.vn/ngan-hang-nua-dau-nam-2026-ap-luc-dang-sau-niem-vui-lai-lon-d148699.html
- Báo Đấu thầu, NPL toàn hệ thống 3,31% / 1,51%: https://baodauthau.vn/ty-le-no-xau-giam-nhe-ap-luc-chat-luong-tai-san-van-lon-post207731.html
- Mekong ASEAN, TCBS 3 yếu tố chất lượng tài sản: https://mekongasean.vn/tcbs-chi-ra-3-yeu-to-can-theo-doi-ve-chat-luong-tai-san-ngan-hang-cuoi-nam-59640.html
- TC KT-TC, nợ xấu tăng nhanh hơn tín dụng: https://tapchikinhtetaichinh.vn/no-xau-tang-nhanh-hon-tin-dung-la-chan-du-phong-mong-dan-164091.html
- Vietstock / Người Quan Sát, BCTC Q3/2026 nhóm quốc doanh — 10/2026: https://vietstock.vn/2026/10/tang-trich-lap-du-phong-rui-ro-gap-8-lan-vietcombank-bao-lai-truoc-thue-quy-32026-di-ngang-737-1509726.htm ; https://vietstock.vn/2026/10/giam-du-phong-rui-ro-bidv-tang-39-loi-nhuan-truoc-thue-quy-3-737-1509741.htm ; https://nguoiquansat.vn/ngan-hang-co-tong-tai-san-lon-nhat-viet-nam-lai-gan-29-500-ty-sau-9-thang-no-duoi-tieu-chuan-tang-gan-3-lan-325369.html
- NH tư nhân nhỏ-vừa Q3 (chỉ dùng khoảng): https://vietbao.vn/no-xau-ocb-tang-38-hon-5800-ty-dong-la-no-co-kha-nang-mat-von-613224.html ; https://nguoiquansat.vn/pgbank-lai-truoc-thue-630-ty-dong-sau-9-thang-no-xau-tang-gan-80-324651.html ; https://doanhnghiepkinhtexanh.vn/ncb-quy-iii2026-lai-hon-847-ty-dong-khoan-phai-thu-tang-gan-10-lan-a55209.html
- TC KT-TC, tín dụng BĐS 2,52 triệu tỷ 30/06 — 23/08/2026: https://tapchikinhtetaichinh.vn/tin-dung-bat-dong-san-vuot-2-5-trieu-ty-dong-dong-von-tiep-tuc-phan-hoa-165191.html
- Báo PL / stockbiz, TPDN 9T 428,5 nghìn tỷ: https://doanhnhan.baophapluat.vn/thi-truong-trai-phieu-doanh-nghiep-huy-dong-hon-428-500-ty-dong-sau-9-thang.md ; https://stockbiz.vn/tin-tuc/hon-47000-ty-dong-trai-phieu-tung-ra-thi-truong-trong-thang-92026-mua-lai-truoc-han-giam-manh/42205724
- TTTC Tiền tệ, TPDN đáo hạn 2026: https://thitruongtaichinhtiente.vn/trai-phieu-mua-lai-truoc-han-giam-manh-trong-thang-2-ap-luc-dao-han-nam-2026-con-tren-194-000-ty-dong-80254.html
- TTTC Tiền tệ, luật hoá quyền thu giữ TSBĐ: https://thitruongtaichinhtiente.vn/luat-hoa-quyen-thu-giu-tai-san-bao-dam-khoi-thong-dong-von-nhung-khong-bo-mac-nguoi-vay-85738.html ; lsvn: https://lsvn.vn/luat-hoa-nghi-quyet-42-tu-quyen-thu-giu-tai-san-den-cuong-che-no-xau-a160313.html
- TT 14/2025 Basel III: https://luatvietnam.vn/legal-updates/requirements-on-capital-adequacy-ratios-for-commercial-banks-foreign-bank-branches-892-103276-article.html ; https://theleader.vn/nganh-ngan-hang-doi-mat-ap-luc-tang-von-tu-thong-tu-14-d42415.html ; https://thesaigontimes.vn/saigontimes/thong-tu-14-buoc-tien-moi-cho-hanh-trinh-nang-cap-he-thong-ngan-hang/
- VietnamFinance, CASA lao dốc (ngành 20,2% Q2): https://vietnamfinance.vn/casa-lao-doc-ngan-hang-tim-cach-tang-nguon-von-re-d151451.html
- TC KT-TC, tài chính tiêu dùng (VNBA, FiinGroup) — 10/2026: https://tapchikinhtetaichinh.vn/tai-chinh-tieu-dung-chuyen-tu-tang-truong-nhanh-sang-cho-vay-co-trach-nhiem-168538.html ; VNBA 02/10: https://vnba.org.vn/vi/tai-chinh-tieu-dung--can-chuyen-tu--mo-rong-tiep-can--sang--mo-rong-tiep-can-co-trach-nhiem-23766.htm
- Tin nhanh CK, bảo hiểm nhân thọ 6T/2026: https://www.tinnhanhchungkhoan.vn/nua-nam-2026-cac-doanh-nghiep-bao-hiem-nhan-tho-da-chi-tra-khoang-35048-ty-dong-post395301.html ; https://thoibaotaichinhvietnam.vn/nhung-cai-bat-tay-huong-bancassurance-vao-chieu-sau-202757.html
- FTSE lộ trình / NH trong rổ: https://thitruongtaichinhtiente.vn/print/85242.html ; https://znews.vn/loat-co-phieu-ngan-hang-viet-vua-lot-ro-ftse-truoc-gio-g-nang-hang-post1678550.html
- SGGP, phương án xử lý SCB (ngày bài chưa xác định): https://www.sggp.org.vn/chinh-phu-yeu-cau-hoan-thien-phuong-an-xu-ly-doi-voi-scb-trong-thang-12-post768158.html
- Nội bộ: `data/deposit_rate_vn_events.csv` (26/10), `data/cctg_rate_vn_events.csv` (12/10), `data/cctg_rate_vn_tier2_events.csv` (13/10), `data/refresh_deposit_cctg_weekly_2026-10.log` (26/10); `vn_macro_regime_history.md` REGIME READ #2 (13/10) và MACRO UPDATE (14/10).
