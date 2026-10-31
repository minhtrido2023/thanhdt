---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-31. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về chủ đầu tư BĐS cụ thể nào.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành BĐS NHÀ Ở / KHU ĐÔ THỊ phía Bắc (Hà Nội, Hải Phòng sau sáp nhập Hải Dương, vùng lân cận như Hưng Yên/Bắc Ninh), phân khúc liền kề/biệt thự/shophouse và chung cư, chủ đầu tư tư nhân vừa-lớn, bàn giao theo giai đoạn, ghi nhận doanh thu khi bàn giao. Gồm chi phí vốn 5 tầng (phía người mua), pipeline cầu, pháp lý, hạ tầng, cấu trúc cạnh tranh, phân loại chế độ ngành, FORECAST khoá trước, checklist DD.
as_of: 2026-10-31 (tin web ≤ 2026-10-22; CSV lãi suất nội bộ ≤ 2026-10-26)
---

# SECTOR READ: BĐS nhà ở / khu đô thị phía Bắc, as-of 31/10/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn và ngày; **[UĐ]** ước đoán/suy luận
của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (có thể sai, không dùng làm số pin). Số tự tính ghi **(ước lượng)**.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc (macro, của chính vai trò này):** `vn_macro_regime_history.md` (REGIME READ 30/09, REGIME READ #2 13/10, MACRO UPDATE
  14/10), `reports/bobby_vn_macro_update_20261014.md` (chỉ grep phần BĐS/tín dụng), `kb/projects/vn_realestate_monthly_checks/2026-10.md`,
  mẫu định dạng `sector_read_da_xay_dung_nam_bo_20261030.md`. CSV nội bộ `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn*_events.csv`.
- **Không tra:** mã, giá cổ phiếu, BCTC, khuyến nghị CTCK của bất kỳ chủ đầu tư nào. Không truy vấn `ticker_financial`, không đọc
  `agents/Taylor/*` hay bất kỳ file DD nào.
- **Ghi chú trung thực (web lộ thông tin cấp DN):** snippet/bài báo lộ tên **khoảng 4-5 chủ đầu tư lớn** (1 tập đoàn BĐS quốc gia
  lớn nhất, 1 chủ đầu tư Malaysia ở Hải Phòng, 1 chủ đầu tư phía Nam đang chậm trả trái phiếu, 1 dự án nghỉ dưỡng Cát Bà) và vài tên
  dự án. Chỉ dùng **ở mức cấu trúc ẩn danh**: "1 chủ đầu tư quốc gia chiếm khoảng 47% giao dịch thấp tầng sơ cấp Đông Hải Phòng H1/2026"
  (HPREA). Không dùng bất kỳ số nào làm bằng chứng về một DN cụ thể.
- **Khoảng trống dữ liệu lớn nhất:** (1) **Hải Phòng Q3/2026: không có báo cáo nào** (CBRE/Savills/HPREA) — số mới nhất là H1/2026.
  (2) Không có chuỗi chính thức "doanh số bàn giao toàn ngành" — dùng tổng hợp báo chí mùa BCTC làm proxy chấm (mục 5). (3) Lãi suất
  vay mua nhà T10/2026 không có khảo sát mới; số mới nhất là DKRA T8 + CBRE Q3 (15/10). (4) Ngày biểu quyết 3 luật chưa xác minh.

## 1. Chi phí vốn — đọc từ phía NGƯỜI MUA NHÀ (bảng 5 tầng + tầng vay mua nhà)

| Tầng | Số as-of | Nguồn (ngày) |
|---|---|---|
| A. Niêm yết hành chính | Big-4 12M **online 6,8%** (không đổi từ 06/2026); tại quầy 5,9% (12/10; SGGP 22/10 nói quầy nâng lên 6,8% — 1 nguồn, chưa kiểm) | `deposit_rate_vn_events.csv` 26/10 (CafeF 24/10, VietNamNet 22/10) |
| B. Bán-hành-chính | CCTG 12M cao nhất Big-4 **7,4%** (BIDV/VietinBank); CCTG 6M VCB 7,5% ⇒ spread CCTG − tiết kiệm 12M ≈ +0,6pp | `cctg_rate_vn_events.csv` 12/10 |
| C. Ngoài Big-4 | ACB online 12M 8,0% (≈05/10); CCTG VPB "lên tới" 9,2% (13/10); ~10 NH chào ≥9% (30/09) | REGIME READ #2; `cctg_rate_vn_tier2_events.csv` |
| D. Thị trường | Liên NH 3M bình quân T9 ≈ 6,98%; tuần 05/10 trở đi: **không có số** | REGIME READ #2 (VBMA) |
| E. Lượng | Tín dụng +10,89% vs huy động +9,78% (28/09, cùng phạm vi NSO) ⇒ chênh 1,11pp; TT 50/2026 nới LDR 85→95% từ 01/12 | REGIME READ #2 |
| **F. Vay mua nhà (tầng quyết định cho ngành này)** | Cố định 12-24T phổ biến tại 11 NH **10,9%** (DKRA T8/2026); dải ưu đãi 8,5-11% chỉ 6-12 tháng (VARS-IRE Q2); **thả nổi 13-15%** (CBRE Q3, 15/10), có nơi 15-16,5% (DXS-FERI H1). Cùng kỳ 2025: 5-8% ưu đãi, 9-11% thả nổi. NOXH H2/2026: người mua 6,5%, chủ đầu tư 7% (+0,6/+0,9pp so H1) | Nhà Đầu tư 28/08; VietnamFinance 02/08; TCKTTC 15/10; VOV 20/10 |

- **Đồng thuận:** B, C, E và F cùng nói chi phí vốn biên **cao và đang ở đỉnh nhiều năm**. **Phân kỳ:** A đứng yên 6,8% suốt 2026 trong khi
  F tăng **+3 đến +5pp** trong khoảng 12-15 tháng. Cơ chế (suy luận): ngân hàng định giá khoản vay dài hạn theo chi phí vốn BIÊN (CCTG,
  tiền gửi lớn ≥9%, trái phiếu cấp 2 Big-4 +2,25-2,8pp) chứ không theo lãi niêm yết bị neo; vay mua nhà là khoản dài hạn, rủi ro lệch kỳ
  hạn lớn ⇒ bị đẩy giá mạnh nhất. Một số NH cài điều khoản tăng lãi kể cả trong kỳ cố định nếu lãi huy động >10% [DK, VnFinance qua Nhà Đầu tư].
- **HƯỚNG:** đi ngang ở mức cao (không thấy dấu hiệu hạ tới cuối T10). **MỨC:** cao hơn ngưỡng chịu đựng của người mua — khảo sát
  PropertyGuru: >80% chỉ vay khi <9%, **100% ngừng dùng đòn bẩy ở ≥11%** [DK 28/08]. Batdongsan: sức mua giảm mạnh trên 9% [DK 02/08].
  Độ tin cậy: trung bình (khảo sát T8, không có số T10).
- **Gánh nặng trả nợ (ước lượng):** khoản vay 3 tỷ, 20 năm, trả góp đều: ở 7% ≈ **23,3 tr/tháng**; ở 14% ≈ **37,3 tr/tháng (+60%)**.
  Đây là cơ chế chính làm gãy cầu đầu tư có đòn bẩy (người vay ưu đãi 2025 đang bị reset sang thả nổi trong 2026).

## 2. Pipeline cầu và cung

### 2a. Toàn quốc (bối cảnh)
| Chỉ báo | Số | Nguồn |
|---|---|---|
| Giao dịch Q3/2026 | **92.004** (92% Q2); căn hộ + nhà riêng lẻ **22.847 (86% Q2)**; đất nền 69.157 (94%). 9T: 80.269 căn hộ/nhà + 251.607 đất nền | BXD qua VOV 20/10, Báo Đấu thầu 13/10 |
| Tồn kho | **51.950** căn/lô (27/34 địa phương, Q3) vs 39.284 (25/34, Q2) — **khác phạm vi**, số do chủ đầu tư tự báo ⇒ cận dưới | BXD 13/10 |
| Tín dụng BĐS 31/08 | 5,21 triệu tỷ, +9,49% YTD, 25,39% tổng dư nợ; nợ xấu BĐS **2,4%** | NHNN tại BCĐ 13/10 qua VOV |
| **Cơ cấu tín dụng BĐS** | **Kinh doanh BĐS (chủ đầu tư) 2,59 triệu tỷ, +19,59% YTD**; tiêu dùng/mua nhà tự ở 2,61 triệu tỷ, **+1,02% YTD** | NHNN qua VOV 20/10 |
| Nguồn cung Q4/2026 | khoảng 30.300 sản phẩm toàn quốc, **miền Bắc ~8.000 (26%)**; cả năm sơ cấp có thể >140.000 | FERI qua VnBusiness 14/10 |
| NOXH | 9T hoàn thành 46.962 căn (48% KH >97.000); gói 153.000 tỷ mới giải ngân ~17.500 tỷ (11,4%), trong đó chỉ ~2.500 tỷ cho người mua | BXD/NHNN 13/10 |
| TPDN | Đáo hạn Q4/2026 ~77.000 tỷ (VIS; 1 nguồn 83.000); BĐS H2/2026 ~60.000 tỷ, **40% thuộc DN từng chậm trả/gia hạn**; coupon BĐS phát hành Q2 11,5-12%; tỷ lệ chậm trả 12T 0,24% (07/09) | VIS qua Tiền Phong/Mekong ASEAN, T7-T9 |
| Giá/thu nhập | Toàn quốc khoảng **30 năm** (2026) so với 23,5 (2023) — 1 nguồn, phương pháp không rõ | báo tổng hợp (snippet) |

**Đọc [UĐ]:** dòng tín dụng BĐS năm 2026 gần như **toàn bộ đi vào phía chủ đầu tư** (+19,6%), còn phía người mua đứng yên (+1,0%). Tức là
tín dụng đang tài trợ cho **hàng tồn kho và quỹ đất**, không phải cho giao dịch cuối. Đây là chữ ký "tích tụ" (khớp nhãn nền
STRUCTURAL_ACCUMULATION trong `vn_macro_regime_history.md`), không phải chữ ký "phục hồi".

### 2b. Hà Nội — chung cư (Q3/2026)
| Chỉ báo | CBRE (TCKTTC 15/10) | Savills (VOV 20/10) | Khác |
|---|---|---|---|
| Mở bán mới | **6.200** (−28% QoQ, −40% YoY); 9T 22.820 (+8% YoY); **>50% Q3 từ siêu dự án Văn Giang (Hưng Yên)** | 3.100 (−42% QoQ, −51% YoY) | Avison Young: >3.200, đang chào ~11.500; >80% cao cấp/hạng sang |
| Bán được | **>3.900 (−33% QoQ, −66% YoY)**, thấp nhất từ Q1/2024 | 3.800 (−26% QoQ, −48% YoY) | Knight Frank: −40% QoQ, −52% YoY |
| Hấp thụ | ~63% mở bán mới (ước lượng) | 39% toàn thị trường, 59% hàng mới | Knight Frank 38% (thấp nhất từ 2024); Avison Young ~31% (vs 70-80% cùng kỳ) |
| Giá sơ cấp | **86 tr/m² (−9% QoQ, −6% YoY)**; nội đô 102 (−6% QoQ) | — | Avison Young: +1,5-2,3% (cùng dự án) |
| Giá thứ cấp | **60 tr/m² (−5% QoQ, −8% YoY)** | — | Batdongsan: chỉ số rao thứ cấp **−15% YTD** tới T9 (sơ cấp −9%); người mua tiền mặt ép giảm 8-12% |
| Cả năm 2026 | 30.000-32.000 (83-88% của 2025; T7 còn dự báo ~39.000) | — | — |

- Tồn kho sơ cấp đang chào khoảng 11.500 / bán khoảng 3.800 mỗi quý ⇒ **khoảng 3 quý hàng** (ước lượng). Chưa cực đoan, nhưng 9T mở
  bán vẫn +8% YoY trong khi bán Q3 −48 đến −66% YoY ⇒ khoảng hở đang **mở rộng** [UĐ].
- Giá sơ cấp bình quân giảm phần lớn do **đổi cơ cấu** (nhiều hàng vùng ven Hưng Yên giá thấp hơn) — cùng dự án vẫn +1,5-2,3%. Chủ đầu
  tư giữ giá niêm yết và **giảm giá ẩn** (chiết khấu, giãn thanh toán, hỗ trợ lãi suất tới 5 năm) [DK FERI/CBRE]. Đây là bài học "đừng đọc
  một con số" áp cho giá nhà: giá niêm yết sơ cấp là số ít thông tin nhất; giá thứ cấp và chiết khấu thực mới lộ giá thật.

### 2c. Hà Nội — liền kề / biệt thự / shophouse (Q3/2026)
| Chỉ báo | Savills (Tiền Phong 16/10) | CBRE (TCKTTC 15/10) |
|---|---|---|
| Nguồn cung | Sơ cấp ~2.101 căn (+5% YoY), mở mới 378 | Mở mới **1.517** (+37% QoQ, +144% YoY); cả năm ~5.000 |
| Bán được / hấp thụ | **191 căn, hấp thụ 9% — thấp nhất 10 năm**; 9T <1.000 căn | >500 căn (~30% hàng mới) |
| Giá sơ cấp | **281 tr/m² đất**; 44% hàng ≥30 tỷ/căn, **không còn sản phẩm <10 tỷ từ 2025** | 247 tr/m² (+18% QoQ, +33% YoY — **đổi cơ cấu**) |
| Giá thứ cấp | "tăng YoY" (không có số) | **183 tr/m² (−6% QoQ, −4% YoY)** |
| Q2/2026 | — | CBRE: 660 giao dịch thấp tầng (−30% QoQ, **−74% YoY**); JLL: sơ cấp ~210 tr/m², −20% YoY do cơ cấu |
| Pipeline | **>35.000 căn từ Q4/2026 tới 2029** (~12%/năm); Savills cảnh báo giá đi ngang/giảm | — |

- Thứ cấp phía Tây Hà Nội: giá rao **−4 đến −14%** so với đỉnh 2025, môi giới nói chủ nhà chấp nhận cắt 10-20% nhưng vẫn ít giao dịch
  [DK VietnamFinance 29/07]. Sản phẩm >17 tỷ khó bán nếu không có chính sách hỗ trợ [DK JLL qua cùng bài].
- **Tỷ lệ pipeline/hấp thụ (ước lượng, độ tin cậy thấp):** 35.000 căn trong khoảng 3,25 năm ≈ 10.800 căn/năm, so với tốc độ bán 2026
  khoảng 1.300 (Savills) đến 2.000 (CBRE) căn/năm ⇒ **gấp 5-8 lần**. Pipeline sẽ không ra hết — nó sẽ bị **hoãn mở bán**, và chính việc
  hoãn đó là cơ chế đè lên vòng quay tiền của chủ đầu tư (vốn nằm ở quỹ đất + hạ tầng, lãi vay vốn hoá vào tồn kho) [UĐ].
- **Phân khúc này là phân khúc đầu tư có đòn bẩy điển hình** (vé 12-30+ tỷ, lợi suất cho thuê thấp) ⇒ nhạy nhất với tầng F lãi vay.

### 2d. Hải Phòng (sau sáp nhập Hải Dương) — số mới nhất là H1/2026
| Chỉ báo | Số | Nguồn |
|---|---|---|
| Giao dịch sơ cấp Đông HP H1 | **1.359**: thấp tầng 941, căn hộ TM 345, nghỉ dưỡng 73; giảm YoY (không có %), vùng ven giảm mạnh | HPREA qua VietnamFinance 10/07 |
| Tập trung | 1 dự án của **1 chủ đầu tư quốc gia = 441 căn = 47% giao dịch thấp tầng**; top-4 dự án ≈ 89% (ước lượng) | như trên |
| Giá thấp tầng | khoảng 53-140 tr/m² | HPREA |
| Đấu giá đất | 753 lô, 717 thành công (95%); số lô **+250% YoY**; sản phẩm 2-3 tỷ chiếm ưu thế, <1 tỷ thanh khoản thấp | HPREA |
| Căn hộ | phổ biến ~40 tr/m² (Q1/2026, +17% YoY); thuê ~11 tr/tháng ⇒ lợi suất gộp **4,8%** (Hà Nội 2,3%); **người Hà Nội = 32% lượt quan tâm**; tỷ trọng hàng >55 tr/m² 16% (2023) → 26% | Batdongsan/CBRE qua TheLEADER 24/08 |
| Vĩ mô địa phương | FDI 9T **3,64 tỷ USD (+64,4% YoY, 93,3% KH)**, 90,8% vào KCN/KKT; GRDP 9T **+12,08%**; khoảng 45-46 KCN sau sáp nhập | VietnamPlus/VOV T10; HPREA |
| NOXH Đông HP | H1 hoàn thành 1.383 căn; mục tiêu 2026 >7.000 | HPREA |
| Triển vọng | HPREA: H2/2026 "tích luỹ", thanh khoản cải thiện chậm, giá đất nền đi ngang; JLL: nguồn cung thấp tầng tăng đáng kể 3 năm tới (Thủy Nguyên) | HPREA; JLL qua snippet |

**Đọc [UĐ]:** Hải Phòng có **nền cầu thật tốt hơn Hà Nội** (FDI, KCN, dân cư từ sáp nhập, lợi suất thuê 4,8%), nhưng cầu đó là cầu
**ở/thuê/NOXH/căn hộ 2-3 tỷ**, không phải cầu cho liền kề/biệt thự 5-15+ tỷ. Phân khúc thấp tầng HP đang **phụ thuộc dòng tiền nhà đầu tư
Hà Nội** (32% lượt quan tâm) và **tập trung vào vài siêu dự án** — tức là nó **trễ pha Hà Nội khoảng 2-4 quý** và sẽ nhận cú sốc lãi suất
qua kênh nhà đầu tư Hà Nội. Không có số Q3 nên chưa xác nhận được.

### 2e. Hạ tầng liên vùng và chính sách
- **Hạ tầng [DK]:** VĐ4 Vùng Thủ đô: Bắc Ninh GPMB 99,5%; mục tiêu cơ bản xong 2026, đường song hành Q3/2026, cầu Hồng Hà 2027 (T5-T7/2026).
  Sân bay Gia Bình (Bắc Ninh): yêu cầu xong đồng bộ 2026 / phục vụ APEC 2027 — **chưa thấy tin hoàn thành**. Đường sắt Lào Cai–Hà Nội–Hải
  Phòng: mục tiêu khởi công 19/12/2025, dự án thành phần 2 khởi công cuối 2026, hoàn thành ≤2030; HP GPMB trước 06/2026. Khu thương mại tự do
  HP: 711 thủ tục mới, chưa có số tiến độ. Sân bay Tiên Lãng: **không tìm thấy thông tin** lượt này.
- **Đọc hạ tầng [UĐ]:** hạ tầng là động lực **giá đất dài hạn** (Savills: Nam Hà Nội/sông Hồng ~30%/năm 5 năm qua) và là lý do pipeline vùng
  ven lớn, nhưng nó **không giải được vấn đề khả năng chi trả** ở chu kỳ 6-12 tháng. Hạ tầng hoàn thành 2026-2027 = thêm nguồn cung đất được
  "mở khoá", tức là áp lực cung, không phải áp lực cầu, trong ngắn hạn.
- **Pháp lý đất [DK]:** Luật Đất đai 2024; **NQ 254/2025/QH15** (hiệu lực 01/01/2026): bảng giá đất là căn cứ chính tính tiền sử dụng đất/thuê
  đất/bồi thường; **hệ số điều chỉnh giá đất do UBND tỉnh ban hành HẰNG NĂM, có thể điều chỉnh trong năm**; cho phép giao đất theo tiến độ dự
  án/GPMB; hướng dẫn NĐ 49/2026/NĐ-CP. Hà Nội: bảng giá đất lần đầu từ 01/01/2026 (NQ 52/2025/NQ-HĐND), hệ số K theo QĐ 19/2026/QĐ-UBND
  (02/02/2026); dự thảo cho vùng ven **+tới 26%**. Với dự án thương mại, giá tính tiền sử dụng đất có thể là **giá đất cụ thể** hoặc giá trúng
  đấu giá (NĐ 103/2024 Điều 5) [DK qua thuvienphapluat].
- **Ba luật sửa đổi [DK]:** Luật Đất đai, Nhà ở, KDBĐS (sửa đổi) trình kỳ họp thứ 2 QH khoá XVI; trình/thẩm tra và thảo luận tổ **22/10/2026**;
  UBTVQH đã đưa Luật Đất đai sửa đổi vào chương trình "cho ý kiến và thông qua" tại kỳ này (06/07). **Chưa có tin biểu quyết.** Dự thảo KDBĐS:
  đưa 5% giá trị còn lại vào tài khoản đảm bảo tại ngân hàng (thay vì thu khi cấp sổ) — đề xuất, chưa thông qua.
- **Thanh toán nhà hình thành trong tương lai (Luật KDBĐS 2023, hiệu lực 01/08/2024) [DK qua luatvietnam/lsvn]:** cọc ≤5% và chỉ khi dự án đủ
  điều kiện kinh doanh; lần đầu ≤30% gồm cọc; ≤70% trước bàn giao [NỀN cho mốc 70%]; **≤95% trước khi cấp giấy chứng nhận**.
- **Thuế [DK]:** Luật Thuế TNCN 2025 hiệu lực 01/07/2026; chuyển nhượng BĐS vẫn **2% giá chuyển nhượng**; phương án 20% trên lợi nhuận **chưa
  được áp dụng** (để nghiên cứu sau khi số hoá dữ liệu đất đai). Thuế BĐS thứ hai: chỉ là đề xuất/thảo luận.
- **Tín dụng [DK]:** CV 8509 (16/09) nới — dư nợ tăng thêm vào khách sạn/du lịch/nghỉ dưỡng không tính vào room BĐS; NOXH/KCN đã được loại khỏi
  room trước đó. **Không có văn bản siết nào** nhắm vào tín dụng nhà ở thương mại.
- **Đấu giá đất ngoại thành Hà Nội [DK]:** đầu 2026 "nóng lại" — trúng 2-3 lần giá khởi điểm (VTC 02/03/2026), có lô 10-13 lần (nguồn MXH, độ tin
  cậy thấp). Đây là **neo giá đất đầu vào** cho dự án vùng ven: giá vốn quỹ đất mới mua 2025-2026 cao, đúng lúc giá bán đầu ra chững lại.

## 3. Cấu trúc cạnh tranh và rủi ro ngành

**Lớn vs vừa [DK + UĐ]:**
- Thị phần cung mới phía Bắc đang dồn về **vài siêu dự án** (Q3 >50% căn hộ mới "Hà Nội" thực chất ở Văn Giang, Hưng Yên; Đông HP: 1 chủ
  đầu tư 47% giao dịch thấp tầng, top-4 ~89%). Chủ đầu tư lớn có quỹ đất giá vốn thấp (mua trước 2020), có thể **hỗ trợ lãi suất tới 5 năm,
  giãn thanh toán, cam kết thuê** — tức là tự gánh tầng F thay người mua. Chủ đầu tư vừa không gánh được lâu ⇒ **mất thị phần trong pha suy**
  hoặc phải cắt giá thật [UĐ].
- Chủ đầu tư vừa thường: 1-3 dự án trọng điểm, tập trung 1 tỉnh, bàn giao theo giai đoạn, quỹ đất các giai đoạn sau **chưa chốt tiền sử dụng
  đất** ⇒ chịu bảng giá đất mới × hệ số K hằng năm. Đây là rủi ro **biên lợi nhuận giai đoạn sau thấp hơn giai đoạn đầu** [UĐ].

**Chu kỳ ghi nhận doanh thu dồn — cái bẫy đọc số [NỀN + UĐ]:**
- Doanh thu ghi nhận khi **bàn giao** (chuyển giao rủi ro/lợi ích; với đất nền là khi bàn giao đất) [NỀN, VAS]. Độ trễ bán → bàn giao: căn hộ
  khoảng 18-36 tháng, thấp tầng/đất nền có hạ tầng khoảng 6-18 tháng [NỀN].
- ⇒ Doanh thu/lợi nhuận **2026 và đầu 2027** của ngành phần lớn phản ánh **bán hàng 2024-2025** (năm hấp thụ 70-80%). Lợi nhuận báo cáo có thể
  **đẹp nhất đúng lúc bán hàng mới đang gãy** (Hà Nội căn hộ Q3 −48 đến −66% YoY, thấp tầng hấp thụ 9%). Chỉ báo dẫn đúng là **người mua trả
  tiền trước** (giảm 2 quý liên tiếp = bán mới < bàn giao) và **doanh số ký mới/backlog**, không phải doanh thu [UĐ].
- **Lồi lợi nhuận:** 1 giai đoạn bàn giao có thể chiếm phần lớn lợi nhuận năm ⇒ YoY từng quý gần như vô nghĩa; phải đọc 8-12 quý.

**Tiền khách trả trước [DK luật + UĐ]:** cọc ≤5%, lần đầu ≤30%, ≤95% trước sổ ⇒ dòng tiền khách là **nguồn vốn rẻ nhất** của chủ đầu tư.
Khi hấp thụ gãy, nguồn này cạn trước ⇒ chủ đầu tư phải thay bằng vay NH/TPDN (coupon BĐS 11,5-12%) ⇒ khớp với dữ kiện tín dụng chủ đầu tư
+19,6% YTD. Dự thảo đưa 5% cuối vào tài khoản đảm bảo sẽ **giảm thêm** dòng tiền khả dụng nếu thông qua.

**Rủi ro tiến độ/pháp lý dự án:** xác định tiền sử dụng đất (giá đất cụ thể), GPMB, điều kiện mở bán (bảo lãnh NH cho nhà hình thành trong
tương lai [NỀN]), cấp sổ chậm (giữ 5% cuối). Phía có lợi: NQ 254 + 3 luật sửa đổi + BCĐ TW (13/10) + đầu mối xử lý dự án tồn đọng đều đi theo
hướng **gỡ cung pháp lý** — nhưng gỡ cung trong pha cầu yếu làm tăng tồn kho chứ không tăng hấp thụ [UĐ].

**Rủi ro khách hàng:** người vay ưu đãi 2025 (5-7%) đang reset sang 13-15% ⇒ bán tháo thứ cấp, **huỷ hợp đồng/xin giãn tiến độ** ở các đợt thanh
toán theo tiến độ. Chi phí hỗ trợ lãi suất mà chủ đầu tư cam kết là **nghĩa vụ ngoài bảng** dễ bị bỏ sót [UĐ].

**Rủi ro tập trung địa lý:** chủ đầu tư vừa ở Hải Phòng phụ thuộc (a) cầu đầu tư từ Hà Nội và (b) cạnh tranh trực diện với siêu dự án của chủ đầu
tư quốc gia ở Thủy Nguyên (nguồn cung tăng mạnh 3 năm tới, JLL). Lợi thế FDI/KCN của HP chuyển hoá chủ yếu vào căn hộ/NOXH/cho thuê.

## 4. Phân loại và vị trí chu kỳ

| Nhãn | P | Lý do |
|---|---|---|
| **CYCLICAL** | **0,45** | Cú gãy 2026 có nguyên nhân gần nhất rõ: **lãi vay mua nhà +3-5pp** trên nền giá đã tăng mạnh 2024-25 (Hà Nội Q1/2026 ~+30% YoY). Khối lượng sụp trước (−48/−66% YoY căn hộ, thấp tầng hấp thụ 9%), giá thứ cấp theo sau (−5-15%), giá sơ cấp dính (chiết khấu ẩn). Đây là mẫu pha suy chu kỳ do lãi suất, đảo chiều được khi lãi vay về <9% |
| **STRUCTURAL** | **0,35** | Giá/thu nhập ~30 năm; giá liền kề Hà Nội không còn sản phẩm <10 tỷ; cầu là cầu đầu tư (lợi suất thuê Hà Nội 2,3%); tín dụng chủ đầu tư +19,6% trong khi người mua +1,0% ⇒ tồn kho được tài trợ bằng nợ; pipeline thấp tầng gấp 5-8 lần tốc độ hấp thụ; quỹ đất mới giá vốn cao (đấu giá 2-3× khởi điểm). Khớp nhãn nền vĩ mô STRUCTURAL_ACCUMULATION (giữa, ambiguous) — giải toả cần **giá thực giảm hoặc thu nhập đuổi kịp nhiều năm**, không phải 1 đợt hạ lãi |
| **ADMIN_GATED** | **0,20** | Cung bị hành chính quyết (tiền sử dụng đất, bảng giá × K hằng năm, điều kiện mở bán, 3 luật đang sửa), cầu NOXH phụ thuộc gói 153.000 tỷ, lãi vay một phần do chỉ đạo NHNN. Nhưng nút thắt **hiện tại là cầu/khả năng chi trả**, không phải cung pháp lý — nên trọng số thấp |

**Độ tin cậy: `ambiguous` khoảng 55/45** (CYCLICAL vs STRUCTURAL). Chỗ lẫn lớn nhất: lãi suất cao là nguyên nhân chu kỳ, nhưng chính lãi suất
cao lại bắt nguồn từ chênh tín dụng–huy động mang tính cấu trúc (REGIME READ #2). Nếu lãi suất không hạ được trong 2027 vì lý do cấu trúc
đó, CYCLICAL và STRUCTURAL cho ra cùng một quỹ đạo.

**Trục 2 (kiểu episode): không CONTAINABLE bằng 1 hành động.** Không có trigger có tên (không phải 1 vụ vỡ trái phiếu như 2022); tỷ lệ chậm
trả TPDN chỉ 0,24%. Lối ra cần lãi vay mua nhà hạ (phụ thuộc chênh tín dụng–huy động + Fed `EXTERNAL_CYCLE`) và/hoặc giá điều chỉnh.

**Vị trí chu kỳ: ĐẦU → GIỮA pha suy về KHỐI LƯỢNG; ĐẦU pha suy về GIÁ** (Hà Nội). **Hải Phòng: cuối pha tăng → đầu pha chững, trễ Hà Nội
khoảng 2-4 quý** (chưa có số Q3 để xác nhận).
- Ủng hộ: khối lượng Q3 thấp nhất từ Q1/2024 (căn hộ) và 10 năm (thấp tầng); thứ cấp giảm 3 quý; BXD 13/10 thừa nhận thứ cấp giảm, tồn kho tăng;
  CBRE hạ dự báo cung 2026 từ ~39.000 xuống 30-32.000 (chủ đầu tư bắt đầu hoãn).
- Chống: giá sơ cấp cùng dự án chưa giảm; chưa có làn sóng vỡ nợ chủ đầu tư; FDI/GRDP HP rất mạnh; NHNN vẫn nới (TT 50, CV 8509).
- **Giống lịch sử nhất về cơ chế:** H2/2011 → 2012 (lãi vay cao bóp người mua, khối lượng sập trước, giá thứ cấp giảm dần nhiều quý) [NỀN].
  Khác: CPI 5% vs 18%, NPL BĐS 2,4% vs hai chữ số, không có NQ 11 siết hệ thống. **Không giống 2022-23** (trigger TPDN có tên, giải bằng NĐ 08
  + hạ lãi suất trong khoảng 12-18 tháng).

**Điều kiện đổi phân loại:**
- **→ CYCLICAL đáy/phục hồi (≥0,60):** lãi vay cố định phổ biến <9% VÀ hấp thụ căn hộ Hà Nội (Savills, hàng mới) >60% 2 quý liên tiếp.
- **→ STRUCTURAL ≥0,50:** giá thứ cấp căn hộ Hà Nội ≤ −10% YoY (CBRE) VÀ (nợ xấu BĐS >3% HOẶC chậm trả TPDN 12T >1%) VÀ tín dụng chủ đầu tư
  tiếp tục >15%/năm trong khi tín dụng người mua <5%.
- **→ ADMIN_GATED ≥0,40:** 3 luật thông qua kèm cơ chế giá đất làm tiền sử dụng đất tăng mạnh (bảng giá × K vùng ven +>20%) VÀ số dự án được
  chấp thuận mới tiếp tục giảm (Q1/2026 chỉ 43 dự án, bằng 49,4% Q4/2025 — BXD qua snippet).

## 5. FORECAST khoá trước (31/10/2026, falsifiable)

| # | Chấm ngày | Biến (nguồn chấm) | Dự báo |
|---|---|---|---|
| F1 | 2027-02-15 | CBRE Hà Nội: căn hộ bán được Q4/2026 | **≤6.000 căn: P = 0,65** |
| F2 | 2027-05-15 | CBRE Hà Nội: giá chào sơ cấp căn hộ bình quân Q1/2027 so với Q3/2026 (86 tr/m²) | Trong ±5%: **P = 0,55**; < −5%: P = 0,30; > +5%: P = 0,15 |
| F3 | 2027-08-15 | CBRE Hà Nội: giá thứ cấp căn hộ Q2/2027 so cùng kỳ | **< 0% YoY: P = 0,70** |
| F4 | 2027-02-15 | Savills Hà Nội: tỷ lệ hấp thụ thấp tầng toàn thị trường Q4/2026 | **≤20%: P = 0,75** |
| F5 | 2027-08-15 | CBRE Hà Nội: giá thứ cấp thấp tầng (tr/m² đất) Q2/2027 so cùng kỳ | **≤ −5% YoY: P = 0,50** |
| F6 | 2027-01-31 | Lãi vay mua nhà cố định 12-24T phổ biến (DKRA/VARS hoặc báo tổng hợp ≥3 NH lớn), T12/2026-T1/2027 | **≥10,0%: P = 0,70** |
| F7 | 2027-02-15 | BXD: tồn kho BĐS Q4/2026 (ghi kèm số địa phương báo cáo) | **>51.950: P = 0,65** |
| F8 | 2027-04-30 | NHNN: tín dụng BĐS/tổng dư nợ tại 31/12/2026 | **Trong [24,5%; 26,5%]: P = 0,70** |
| F9 | 2027-04-30 | NHNN: dư nợ tiêu dùng/mua nhà tự ở (phân loại như số 31/08) tăng cả năm 2026 | **<5%: P = 0,65** |
| F10 | 2026-12-31 | QH thông qua Luật Đất đai (sửa đổi) | **Thông qua ≤31/12/2026: P = 0,70** |
| F11 | 2027-08-31 | HPREA: giao dịch sơ cấp H1/2027 cùng phạm vi H1/2026 (Đông HP = 1.359) | **<1.359: P = 0,60** |
| F12 | 2027-04-30 | Tổng hợp mùa BCTC Q4 (VietstockFinance/FiinTrade/báo chí): doanh thu thuần năm 2026 nhóm BĐS dân cư niêm yết so với 2025 | **Tăng: P = 0,60** (thesis độ trễ bàn giao) |
| F13 | 2027-04-30 | Cùng nguồn F12: tổng "người mua trả tiền trước" nhóm BĐS dân cư niêm yết tại 31/12/2026 so với 31/12/2025 | **Giảm: P = 0,55** |
| F14 | 2027-03-31 | VIS Rating: tỷ lệ chậm trả TPDN 12 tháng (toàn thị trường) ở bản tin T2-T3/2027 | **>0,5%: P = 0,30** |

**Cách chấm:** đúng/sai theo nguồn ghi trong cột. Nguồn không công bố hoặc đổi phương pháp mà không có số so sánh được ⇒ ghi "không chấm được",
không suy. F12 và F13 cùng đúng là xác nhận thesis "lợi nhuận báo cáo trễ chu kỳ bán hàng". **Không phải khuyến nghị mua/bán.**

## 6. DD cần kiểm gì cho một chủ đầu tư BĐS đô thị phía Bắc (checklist bằng số)

**A. Quỹ đất và pháp lý (quan trọng nhất)**
1. Bảng quỹ đất theo **từng dự án và từng giai đoạn**: ha, số sản phẩm, đã/chưa có QĐ giao đất, quy hoạch 1/500, GPXD, văn bản đủ điều kiện mở bán.
2. **Tiền sử dụng đất: % diện tích ĐÃ nộp xong** so với **chưa xác định/chưa nộp**. Với phần chưa nộp: ước nghĩa vụ theo bảng giá 2026 × hệ số K
   và **độ nhạy: +10% / +20% / +26% (dự thảo vùng ven HN)** giá đất ⇒ giảm biên gộp bao nhiêu điểm %. Phần chưa chốt >30% quỹ đất = cờ vàng.
3. Có khoản **truy thu tiền sử dụng đất** nào đang tranh chấp/chờ quyết định không (số tiền, % vốn chủ).
4. **Sổ đã cấp / sản phẩm đã bàn giao**: tồn đọng sổ >12 tháng = cờ đỏ (giữ 5% cuối không thu được; dự thảo tài khoản đảm bảo).
5. Quỹ đất mua 2025-2026 qua đấu giá/M&A: **giá vốn/m² so với giá bán thứ cấp khu vực** (CBRE thấp tầng HN 183 tr/m²; HP 53-140 tr/m²). Giá vốn
   + hạ tầng + tiền sử dụng đất >60% giá bán hiện tại = biên mỏng khi giá đi ngang.

**B. Bán hàng, backlog và dòng tiền khách**
6. **Doanh số ký mới theo quý** (không phải doanh thu) 8 quý gần nhất; so với thị trường (HN căn hộ −48/−66% YoY Q3; thấp tầng hấp thụ 9%).
7. **Backlog** (đã bán chưa bàn giao) / doanh thu năm: >1,5 năm thì lợi nhuận 2026-27 có "đệm", nhưng phải kiểm chất lượng (mục 9-10).
8. **Người mua trả tiền trước**: xu hướng 4 quý; **giảm 2 quý liên tiếp = bán mới < bàn giao** ⇒ lợi nhuận tương lai đang cạn. Kiểm trần 95% luật.
9. **Tỷ lệ huỷ hợp đồng / xin giãn tiến độ / nợ quá hạn đợt thanh toán của khách** (đặc biệt khách vay ưu đãi 2025 đang reset 13-15%).
10. **Chi phí hỗ trợ lãi suất, chiết khấu, cam kết thuê** / doanh thu: >3-5% là giảm giá ẩn; tổng **nghĩa vụ hỗ trợ lãi suất còn lại** (ngoài bảng)
    phải lượng hoá bằng tiền và so với tiền mặt.
11. Tỷ trọng bán **sỉ cho đại lý/F1 ôm hàng, bên liên quan, hợp đồng hợp tác kinh doanh**: >20% doanh số = doanh số chất lượng thấp.
12. Cơ cấu sản phẩm theo vé: % sản phẩm >10 tỷ (HN không còn sơ cấp <10 tỷ); với HP, % sản phẩm vượt dải phổ biến 2-3 tỷ.

**C. Biên lợi nhuận và ghi nhận**
13. Biên gộp **theo giai đoạn** (đầu vs sau): giai đoạn sau chịu tiền đất mới ⇒ chênh >10 điểm % là rủi ro.
14. Lãi vay **vốn hoá vào tồn kho**: % giá trị tồn kho; tăng nhanh khi hoãn mở bán ⇒ biên tương lai bị "ăn" dần.
15. Lịch bàn giao 8 quý tới theo giai đoạn ⇒ đánh dấu quý "lồi"; đừng ngoại suy YoY quý.
16. **CFO luỹ kế 3-5 năm / lợi nhuận ròng luỹ kế**: <0,5 qua cả chu kỳ = lợi nhuận chủ yếu là kế toán (dồn tích).

**D. Bảng cân đối và nguồn vốn**
17. Nợ vay ròng / vốn chủ: >1,0x = căng trong pha suy; nợ ngắn hạn + TPDN đáo hạn 12 tháng **so với tiền + 50% người mua trả trước**.
18. TPDN: lịch đáo hạn, coupon (≥11,5% = vay ở giá BĐS hiện hành), tài sản bảo đảm (cổ phần dự án?), lịch sử gia hạn (40% đáo hạn H2/2026 của ngành
    thuộc DN từng chậm trả).
19. **Phải thu/ứng trước cho "đối tác hợp tác đầu tư", đặt cọc mua quỹ đất, bên liên quan**: >20% vốn chủ = cờ đỏ (kênh chuyển dòng tiền).
20. Bảo lãnh cho bên liên quan; cam kết mua lại; bảo lãnh của NH cho nhà hình thành trong tương lai (hạn mức, phí).

**E. Tập trung và vị trí**
21. % quỹ đất/NAV ở **1 tỉnh**: >60% = rủi ro tập trung; khoảng cách tới siêu dự án của chủ đầu tư quốc gia (cạnh tranh trực diện ở Thủy Nguyên/Văn Giang).
22. Tỷ trọng khách **ngoài tỉnh** (HP: người Hà Nội ~32% lượt quan tâm) ⇒ độ nhạy với lãi vay của nhà đầu tư Hà Nội.
23. Hạ tầng làm luận điểm (VĐ4, Gia Bình, đường sắt LC–HN–HP, FTZ HP): đã khởi công/đã xong hay mới quy hoạch; định giá đang "trả trước" bao nhiêu.

**F. Quản trị**
24. Giao dịch quỹ đất/M&A dự án với bên liên quan (giá so với thị trường), thay đổi kiểm toán, ý kiến ngoại trừ, chênh lệch số trước/sau kiểm toán.
25. Có yếu tố pháp lý (thanh tra, điều tra) thì **vẫn phân tích trên BCTC như bình thường, ghi WARNING tường minh** (luật user 2026-09-27).

## 7. Chỉ báo theo dõi

| # | Chỉ báo | Nguồn | Ngưỡng đổi đọc |
|---|---|---|---|
| 1 | Lãi vay mua nhà cố định/thả nổi | DKRA, VARS-IRE, biểu NH | <9% cố định ⇒ cầu đòn bẩy quay lại; >12% ⇒ nặng thêm |
| 2 | Hấp thụ + giá thứ cấp căn hộ/thấp tầng HN (quý) | CBRE, Savills | Mục 4 điều kiện đổi |
| 3 | Báo cáo HP Q3/Q4 (HPREA, CBRE) | HPREA | Giao dịch thấp tầng −30% YoY ⇒ HP vào pha suy cùng HN |
| 4 | Cơ cấu tín dụng BĐS chủ đầu tư vs người mua | NHNN (họp báo, BCĐ) | Người mua >5% YTD ⇒ cầu thật hồi |
| 5 | Tồn kho BXD + số dự án chấp thuận mới | BXD quý | Tồn kho tăng 2 quý cùng phạm vi |
| 6 | 3 luật + bảng giá đất 2027, hệ số K | QH, HĐND/UBND HN, HP | Bảng giá vùng ven +>20% |
| 7 | TPDN BĐS: chậm trả mới, gia hạn | VIS Rating tháng | Chậm trả 12T >1% |
| 8 | Giải ngân gói NOXH 153.000 tỷ | NHNN | >30% ⇒ kênh cầu ở thật được mở |

## Nguồn (ngày đăng)
- TCKTTC 15/10/2026 (CBRE Hà Nội Q3): https://tapchikinhtetaichinh.vn/thi-truong-nha-o-ha-noi-thanh-khoan-giam-manh-gia-thu-cap-dong-loat-di-xuong-169629.html
- Tiền Phong 16/10/2026 (Savills thấp tầng HN Q3): https://tienphong.vn/thanh-khoan-biet-thu-lien-ke-ha-noi-thap-ky-luc-10-nam-qua-post1885677.tpo
- VOV 20/10/2026 (BXD Q3, Savills căn hộ, cơ cấu tín dụng BĐS, NOXH): https://vov.vn/kinh-te/thi-truong-bat-dong-san-luong-giao-dich-giam-sau-gia-nha-van-o-dinh-post1342677.vov
- Báo Đấu thầu 13/10/2026 (BCĐ TW, BXD Q3): https://baodauthau.vn/ton-kho-bat-dong-san-tang-quy-iii2026-ghi-nhan-khoang-92004-giao-dich-thanh-cong-post209850.html
- VnBusiness 14/10/2026 (Avison Young, Knight Frank, FERI Q4): https://vnbusiness.vn/hon-140000-san-pham-vao-ro-hang-dia-oc-cuoi-nam-ai-xuong-tien-mua.html
- Thời báo Tài chính (nội đô 102 tr/m², Q3/2026): https://thoibaotaichinhvietnam.vn/gia-ban-so-cap-can-ho-chung-cu-noi-do-ha-noi-dat-trung-binh-102-trieu-dong-m2-205481.html
- Doanh nhân/Báo Pháp luật (nguồn cung căn hộ HN Q3 −40%): https://doanhnhan.baophapluat.vn/nguon-cung-can-ho-ha-noi-quy-iii-2026-giam-40-thanh-khoan-di-xuong.html
- VietnamFinance 29/07/2026 (thứ cấp thấp tầng HN, JLL/CBRE Q2): https://vietnamfinance.vn/biet-thu-lien-ke-ha-noi-dong-loat-giam-gia-sau-van-kho-ban-d148288.html
- VietnamFinance 10/07/2026 (HPREA H1 Hải Phòng): https://vietnamfinance.vn/bat-dong-san-hai-phong-phan-hoa-dau-gia-dat-tro-thanh-diem-sang-d147330.html
- TheLEADER 24/08/2026 (căn hộ Hải Phòng, lợi suất thuê): https://theleader.vn/dong-luc-but-pha-cua-thi-truong-can-ho-hai-phong-d47407.html
- VietnamPlus / VOV T10/2026 (FDI HP 9T): https://www.vietnamplus.vn/hai-phong-thu-hut-hon-36-ty-usd-von-dau-tu-nuoc-ngoai-trong-9-thang-post1139434.vnp ; https://vov.vn/kinh-te/9-thang-hai-phong-thu-hut-hon-36-ty-usd-von-fdi-dat-tren-93-ke-hoach-nam-post1340353.vov
- Nhà Đầu tư 28/08/2026 (lãi vay mua nhà, khảo sát PropertyGuru): https://nhadautu.vn/lai-suat-vay-mua-nha-binh-quan-da-vuot-10-nam-d107287.html
- VietnamFinance 02/08/2026 (thả nổi tới 16%): https://vietnamfinance.vn/lai-vay-mua-nha-tang-cao-nhieu-nguoi-chi-muon-ban-nha-thoat-no-d148444.html
- Thời báo Tài chính (lãi vay mua nhà "neo" hai con số): https://thoibaotaichinhvietnam.vn/lai-suat-vay-mua-nha-neo-hai-con-so-ky-vong-ha-nhiet-khong-de-201273-201273.html
- Tiền Phong (VIS, TPDN đáo hạn Q4): https://tienphong.vn/trai-phieu-doanh-nghiep-chiu-ap-luc-dao-han-vao-quy-cuoi-nam-post1881328.tpo ; Mekong ASEAN (coupon BĐS 12,2%): https://mekongasean.vn/lai-suat-binh-quan-cua-trai-phieu-bat-dong-san-dat-122-59380.html
- LSVN 22/10/2026 (QH thảo luận 3 luật): https://lsvn.vn/quoc-hoi-thao-luan-ve-3-du-an-luat-lien-quan-toi-dat-dai-nha-o-kinh-doanh-bds-a181313.html ; Báo Lào Cai: https://baolaocai.vn/ngay-2210-quoc-hoi-thao-luan-3-du-an-luat-lien-quan-den-dat-dai-bat-dong-san-post912527.html
- NQ 254/2025/QH15 (Tạp chí Toà án): https://tapchitoaan.vn/nghi-quyet-2542025qh15-thao-go-kho-khan-vuong-mac-trong-to-chuc-thi-hanh-luat-dat-dai14622.html ; hệ số K Hà Nội (QĐ 19/2026): https://thuvienphapluat.vn/phap-luat-nha-dat/he-so-k-lam-can-cu-tinh-tien-su-dung-dat-thue-dat-tai-ha-noi-tu-dau-thang-2-2026-15192.html ; VnEconomy (vị trí, hệ số Hà Nội 2026): https://vneconomy.vn/ha-noi-quy-dinh-ro-vi-tri-va-he-so-dieu-chinh-gia-dat-ap-dung-tu-2026.htm ; dự thảo bảng giá vùng ven +26%: https://doanhnhan.baophapluat.vn/ha-noi-du-thao-bang-gia-dat-2026-trung-tam-cham-dinh-702-trieu-dongm2-vung-ven-tang-manh-88115.html
- Luật KDBĐS 2023 cọc 5% (LuatVietnam): https://luatvietnam.vn/tin-van-ban-moi/tu-2025-khong-dat-coc-mua-nha-hinh-thanh-trong-tuong-lai-qua-5-gia-ban-186-96489-article.html ; đề xuất tài khoản đảm bảo 5%: https://lsvn.vn/de-xuat-chuyen-5-gia-tri-nha-hinh-thanh-trong-tuong-lai-vao-tai-khoan-dam-bao-a179188.html
- Thuế chuyển nhượng 2026 vẫn 2%: https://thuvienphapluat.vn/phap-luat-nha-dat/thue-chuyen-nhuong-bat-dong-san-2026-tiep-tuc-ap-dung-2-dung-khong-14085.html ; đề xuất 20% trên lãi: https://luatvietnam.vn/thue-phi-le-phi/de-xuat-tinh-thue-20-tren-lai-chuyen-nhuong-bat-dong-san-565-103110-article.html
- VĐ4 / Gia Bình: https://baodauthau.vn/day-nhanh-tien-do-san-bay-gia-binh-vanh-dai-4-de-phuc-vu-apec-2027-post199222.html ; https://moc.gov.vn/vn/tin-tuc/1173/94161/pho-thu-tuong-thuong-truc-pham-gia-tuc-kiem-tra-tien-do-du-an-san-bay-gia-binh--tuyen-duong-vanh-dai-4---vung-thu-do.aspx
- Đường sắt LC–HN–HP: https://vietnamfinance.vn/quyet-tam-khoi-cong-du-an-duong-sat-lao-cai--ha-noi--hai-phong-ngay-19-12-d126552.html ; https://baolaocai.vn/hai-phong-day-nhanh-tien-do-du-an-duong-sat-lao-cai-ha-noi-hai-phong-post398953.html
- Đấu giá đất ngoại thành HN (VTC 02/03/2026): https://vtcnews.vn/dau-gia-dat-ngoai-thanh-ha-noi-lai-nong-gia-trung-cao-gap-nhieu-lan-khoi-diem-ar1005307.html
- Nội bộ: `data/deposit_rate_vn_events.csv` (26/10), `data/cctg_rate_vn_events.csv` + `_6m_` + `_tier2_` (12-13/10); `vn_macro_regime_history.md` REGIME READ #2 (13/10) và MACRO UPDATE (14/10).
