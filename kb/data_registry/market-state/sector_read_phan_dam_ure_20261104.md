---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-04. KHÔNG biết mã cổ phiếu nào, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai khác.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ phân đạm urê VN (nhà sản xuất dùng khí tự nhiên giá gắn dầu + nhà sản xuất dùng than). Gồm pipeline cầu, chuỗi giá urê quốc tế, biên chênh urê–khí, cấu trúc cạnh tranh nội địa, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED, FORECAST khoá trước 20/60/120 ngày, checklist DD.
as_of: 2026-11-04 (giá BQ TE tới 2026-11-02/03; WB tháng tới T9/2026; tin web ≤ 2026-11-02)
---

# SECTOR READ: Phân đạm urê Việt Nam, as-of 04/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.
File chị em: `sector_read_fertilizer_dap_20261028.md` (DAP + lưu huỳnh/NH3, cùng bối cảnh Hormuz). Tôi chỉ dùng file đó
làm mẫu định dạng và để đối chiếu chuỗi Brent/TTF/urê.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Repo đã đọc:** `sector_read_fertilizer_dap_20261028.md` (mẫu). `feeds/bq_commodity_prices.md`, chỉ mục BẪY (dòng
  34-43) cộng kết quả grep từ khoá "urea/bẫy". Kết quả grep có in ra vài dòng nhắc tên mã DN thuộc ngành khác
  (lân vàng, DAP). Các dòng đó không liên quan đến urê, không có giá cổ phiếu hay KQKD, và tôi không dùng.
  `market-state/index.md` (chỉ grep "sector_read").
- **BQ (tự truy vấn ngày 04/11):** `tav2_bq.commodity_prices`, luôn chỉ rõ `source`:
  - `trading_economics` daily: `urea`, `brent`, `eu_natural_gas`, `liquefied_natural_gas_japan_korea`, `natural_gas`,
    `coal`, `di_ammonium`. Đã loại T7/CN.
  - `worldbank_cmo` monthly: `urea`, `brent`, `natural_gas`, `eu_natural_gas`, `lng_japan`, `dap`.
  - `sunsirs` daily: `fuel_oil`, `liquid_ammonia`.
  - **Không dùng view `commodity_latest`.**
- **Web:** chỉ bài có ngày công bố ≤ 04/11/2026. Ngày ghi ở mục Nguồn.
- **Chưa đọc hoặc đã bỏ qua (ghi trung thực):**
  - Không mở `kb/projects/*` hay `agents/Taylor/*`.
  - Không mở tài liệu CTCK nào: báo cáo ngành MAS (16/01/2026), HSC (08/06/2026), DSC, VDSC (researchpool), Mirae,
    elibook, stockbiz, bài "initiation" trên LinkedIn. Tôi cũng không tra giá cổ phiếu hay BCTC.
  - **Rò rỉ không chủ ý:** bản tóm tắt của công cụ tìm kiếm có trích (a) giả định giá khí kế hoạch 2026 và mức tăng chi
    phí khí của hai nhà sản xuất khí trong nước, lấy từ tài liệu CTCK hoặc KQKD sơ bộ; (b) lượng XK 9 tháng của một nhà
    sản xuất; (c) câu "thiếu cung kéo dài đến 2027" trong một báo cáo CTCK. **Tôi không dùng (a), (b), (c) cho phân
    loại, forecast hay số trong bảng.** Tên hai nhà máy khí xuất hiện trong bài báo ngành, nên trong thân file tôi chỉ
    gọi theo vùng. Riêng vài URL ở mục Nguồn vẫn có tên nhà máy trong đường dẫn. Người đọc blind sau nên bỏ qua
    mục Nguồn.
  - PDF Ausfert (09/10/2026) tải về được nhưng không giải mã được (máy không có `pdftotext`), nên không dùng.

## 1. Chuỗi giá và đa proxy [DK, BQ trừ khi ghi khác]
| Chuỗi | Hiện tại | Mốc so sánh | Ghi chú |
|---|---|---|---|
| Urê TE daily (`urea`, USD/t, basis chưa xác minh) | **446,0** (02/11). TB T10 445,9 | TB tháng: T10/25 383,9, T2/26 456,1, đỉnh T4/26 697,9, đáy T6/26 386,9, T9/26 452,3 | Đứng 444-453 suốt 3 tuần. Phân vị **69%** trong lịch sử daily từ 2019 |
| Urê WB (Trung Đông, USD/t, tháng) | **407,5** (T9) | Đỉnh 856,9 (T4/26), nên **−52%**. Trung vị 10 năm 330, p10 214, p90 678 | Phân vị **73%** trên 120 tháng. Lệch TE−WB trung vị +4,2%, max 30,9% (bẫy 1 file feeds) |
| Urê CFR Brazil (hạt đục) | 476-488 (tuần tới 26/10), tăng từ 464-482 | — | Nobel Trading qua UkrAgroConsult 30/10. Qatar chào 485-500, TQ chào 470-475 |
| Urê hạt đục FOB Trung Đông | khoảng 445-455 (22/10). Oman khoảng 450 (Ausfert, tiêu đề) | T8 có lúc khoảng 370 (FDD 17/08) | Theo tóm tắt tìm kiếm. Không có số cuối T10 |
| Sàn giá XK Trung Quốc | 430-440 FOB (đa số điểm đến), 500 cho hàng đi Ấn Độ | Hạn ngạch 2026 = **3,3 tr t**, so với khoảng 5 tr t năm 2025 | FertilizerDaily 18/09. Có nguồn khác nói 5-5,5 tr t. **Mâu thuẫn chưa giải** |
| Urê nội địa TQ (Sơn Đông) | 1.735 CNY/t (23/10), quy đổi thô khoảng 245 USD/t [UĐ, tỷ giá ~7,1] | — | Chênh khoảng 190 USD/t so với sàn XK. Đây là kho dư cung bị hạn ngạch giữ lại |
| Ấn Độ tender | IPL 07/10: chào thấp nhất 352,10 (bờ Đông) / 356,25 (bờ Tây) CFR. **Chỉ mua khoảng 410 nghìn t / 1,7 tr t** | T4 935-959, T6 445-449, T8 khoảng 390-395 | Tồn kho urê Ấn Độ ước 6,8-8,1 tr t. Tender kế tiếp dự kiến cuối T10 - giữa T11 |
| Brent TE | **103,1** (03/11). TB T10 107,3 | TB T10/25 63,8, nên **+68% YoY**. Đỉnh 117,5 (28/10) | Ngày 02/11 Iran nói kế hoạch mở eo do Qatar làm trung gian rút còn 2 ngày. Mỹ chưa phản hồi (Mitrade 02/11) |
| Fuel oil nội địa TQ (sunsirs, CNY/t) | TB T10 **7.713**, T11 7.975 | T10/25 5.410, nên **+43% YoY** | Proxy độc lập cho HƯỚNG giá MFO, là chỉ số gắn với giá khí VN [NỀN] |
| Khí TTF (EUR/MWh) / JKM (USD/MMBtu) | 90,1 (03/11) / 31,7 (02/11) | T8: 59 / 21. T10/25: khoảng 31 / 11,1 | **Giá khí biên toàn cầu ×2,8-3 YoY.** Chi phí SX urê Tây Bắc Âu ước 740 USD/t (từ 678) |
| Than Newcastle TE | TB T10 150,3 | T10/25 104,8, nên **+43%** | Chi phí đầu vào của 2 nhà máy urê dùng than ở miền Bắc |
| NH3 nội địa TQ (sunsirs) | 2.673 CNY/t (T11) | T10/25 2.237 | Không phải NH3 CFR (bẫy NH3 trong file feeds) |

**Phân kỳ lớn nhất [UĐ dựa trên DK]:** Lượng phân bón qua Hormuz **bằng 0 trong T9-T10** (FertilizerDaily 29/10). Giá
khí biên toàn cầu tăng gấp ba so với năm trước, và chi phí SX urê châu Âu khoảng 740. Thế nhưng urê thế giới chỉ ở
**khoảng 445-490**, tức phân vị 70-73%, thấp hơn nhiều so với chi phí biên châu Âu. Có ba lực giữ giá: (1) TQ xuất qua hạn
ngạch có sàn, với kho nội địa dư (giá nội địa khoảng 245 USD); (2) Ấn Độ đã tích trữ 6,8-8,1 tr t và vừa từ chối mua 3/4
khối lượng tender; (3) huỷ cầu sau đỉnh T4 và hàng Gulf vòng qua Yanbu/Oman. **Về hướng**, giá đang được đỡ từ phía chi
phí (khí châu Âu) và phía mùa vụ (vụ xuân Bắc bán cầu T1-T3). **Về mức**, trần do TQ quyết định chứ không do khí. Giá
khí của nhà sản xuất VN gắn dầu, không gắn LNG, nên họ nằm sâu ở đầu thấp của đường chi phí. Giá bán của họ theo mức giá
TQ/SEA, không theo chi phí châu Âu.

**Bẫy dữ liệu:**
1. TE `urea` chưa xác minh basis. Mức của nó khớp FOB Trung Đông và sàn TQ, nhưng không có nhãn.
2. WB `brent` T9 là 116,8, trong khi TB daily TE T9 là 100,8 (bẫy 1 file feeds). Vì vậy tôi tính biên bằng Brent TE.
3. BQ không có giá urê nội địa VN, giá khí cấp cho nhà máy đạm hay MFO Singapore. Hai biến này phải lấy từ DN hoặc tin.

## 2. Pipeline cầu VN
**Cung–cầu năm [DK, nguồn lệch nhau]:**
- Công suất 4 nhà máy khoảng **2,6-2,73 tr t/năm**. Sản lượng bình quân 2021-2024 khoảng **2,54 tr t**.
- Tiêu thụ nội địa: 2,148 tr t (Thuế-Hải quan 09/09/2026, có vẻ là tiêu thụ biểu kiến gồm cả hàng NK), 1,6-1,8 tr t
  (CafeF 19/10/2026), khoảng 1,8 tr t (Vinachem 03/06/2026).
- Nhập khẩu 309-400 nghìn t/năm, giá thấp, từ TQ và Indonesia.
- Xuất khẩu khoảng 661 nghìn t/năm, gồm cả hàng tái xuất.
- **Dư cung cấu trúc khoảng 0,6-1,0 tr t/năm, nên VN là nước XK ròng urê.** Cả ngành phân bón XK 9 tháng 2026 khoảng
  2,2 tr t, gần 1,2 tỷ USD (+31,6% lượng, +69% trị giá YoY; Hải quan qua CafeF 19/10).

**Mùa vụ [NỀN + DK]:** cầu giảm mạnh từ T6 đến T11 (Vinachem 03/06). Đông Xuân là vụ bón chính: Nam Bộ xuống giống
T11-T12, Bắc Bộ T1-T2. Hè Thu T4-T6. Thu Đông ở ĐBSCL T8-T10. **As-of 04/11, VN đang ra khỏi mùa thấp điểm và vào mùa
bán Đông Xuân**, nên cầu nội địa và giá bán nội địa thường được đỡ trong T11-T2 [UĐ].

**Giá bán nội địa [DK, rời rạc]:**
- Giữa T3/2026 urê gần 900 nghìn đ/bao 50kg, có đại lý bán 950 nghìn (tăng 200-250 nghìn so với cuối T2; Vinachem 24/03).
- T4 và 08/05/2026: urê miền Tây khoảng **675 nghìn đ/bao** (660-690; báo Hà Tĩnh, báo Nghệ An), tức khoảng 13.500 đ/kg.
- Hai mức này mâu thuẫn. Có thể khác điểm bán hoặc giá đã hạ từ T3 sang T4 [UĐ].
- **Giá nội địa T10/2026: không có số.**
- Quy đổi thô 13.500 đ/kg là khoảng 510 USD/t, đã gồm VAT và chiết khấu đại lý [UĐ, tỷ giá ~26.300 chưa kiểm]. Mức này
  **thấp hơn nhiều** so với giá thế giới đỉnh T4 (WB 857). Giá nội địa VN "dính" và chỉ ăn được một phần cú sốc [UĐ].

**Nhập khẩu và xuất khẩu:** XK urê VN chịu **thuế XK 5%** (NĐ 26/2023/NĐ-CP) [DK]. Đối thủ (TQ, Indonesia, Malaysia,
Brunei) chịu 0%. Bộ Tài chính đã gửi Bộ Tư pháp thẩm định **dự thảo hạ thuế XK urê 5% xuống 0%** (CafeF 19/10/2026;
Thuế-Hải quan 09/09/2026) [DK]. Chưa có ngày hiệu lực.

**Bên ngoài [DK]:**
- **TQ:** hạn ngạch 2026 khoảng 3,3 tr t, sàn FOB 430-440. Theo tiền lệ, TQ thường siết XK trong mùa tích trữ vụ xuân
  nội địa, từ khoảng Q4 đến Q1 [NỀN]. Lượng XK T6-T7/2026 khoảng 410 nghìn t (tóm tắt tìm kiếm).
- **Ấn Độ:** mua rất mạnh ở T4 (giá khoảng 935-1.000), nay tồn kho cao và giảm mua (07/10 chỉ mua khoảng 24% khối lượng
  mời thầu).
- **Trung Đông:** XK urê từ các nền kinh tế phụ thuộc Hormuz giảm 83% ở T4 (UN ITC qua FertilizerDaily 07/08). Hàng phân
  bón qua eo bằng 0 trong T9-T10 (29/10). Saudi chở xe tải sang Yanbu, và ít nhất 15 tàu urê Saudi kẹt trong Vịnh. Qatar
  vẫn chào hàng 485-500 cho Brazil, nhưng không rõ nguồn hàng.

## 3. Biên gộp tách theo (giá urê − chi phí khí) [UĐ, công thức minh hoạ]
**Giả định ([NỀN], phải thay bằng số thật của DN):**
- Định mức khí khoảng **25 MMBtu/t urê**, gồm cả nhiên liệu và tiện ích. Nhà máy cũ có thể 26-28.
- Giá khí cấp cho đạm ở VN gắn MFO Singapore và Brent, có phí vận chuyển. Xấp xỉ tuyến tính: **giá khí ≈ 2,5 + 0,06 ×
  Brent USD/MMBtu**, tức khoảng 6,3 ở Brent 64 và khoảng 8,9 ở Brent 107.
- Hệ số thật, sàn/trần, độ trễ tính trung bình (1-3 tháng) và tỷ trọng LNG pha trộn đều **chưa biết**.
- **Proxy biên = urê TE − 25 × (2,5 + 0,06 × Brent TE).**

| Thời điểm | Urê | Brent | Chi phí khí/t | Biên proxy |
|---|---|---|---|---|
| TB 2024 (WB) | khoảng 340 | khoảng 80 | khoảng 183 | **khoảng 157** |
| T10/2025 (TE) | 383,9 | 63,8 | 158 | **khoảng 226** |
| T4/2026 (TE) | 697,9 | 101,3 | 215 | **khoảng 483** (đỉnh cú sốc) |
| T10/2026 (TE) | 445,9 | 107,3 | 224 | **khoảng 222** |
| Gốc forecast (TB 5 quan sát cuối) | 447,0 | 110,4 | 228 | **khoảng 219** |

Phân vị 10 năm của proxy theo WB: T9/2026 là 57%, đỉnh T4 là 96%. Trung vị 10 năm là 152.

**Đọc [UĐ]:**
1. Biên T10/2026 về lại **đúng mức T10/2025**. Urê +16% YoY bị triệt tiêu bởi chi phí khí ước +41%. Fuel oil TQ +43% YoY
   xác nhận độc lập về hướng.
2. "Lợi nhuận bất thường" chỉ có trong khoảng T3-T5/2026. Nếu giá khí trễ 1-3 tháng, Q2 là quý hưởng nhiều nhất, vì giá
   urê tăng ngay còn giá khí tính theo bình quân tháng trước.
3. Từ T6 trở đi biên về vùng 200-260, tức **cao hơn trung vị 10 năm nhưng không còn bất thường**.
4. Độ nhạy: **+10 USD Brent làm biên giảm khoảng 15 USD/t. +10 USD urê làm biên tăng 10 USD/t.** Kịch bản hoà bình làm
   Brent và urê giảm cùng lúc nên biên tự hedge một phần (xem mục 6).
5. Nhà máy dùng than ở miền Bắc: than +43% YoY và urê +16%, nên biên của nhóm này bị ép mạnh hơn nhóm dùng khí [UĐ].
   Đây là nhóm chi phí cao, có thể giảm tải khi giá thấp.

## 4. Cấu trúc cạnh tranh nội địa
- **4 nhà sản xuất** [DK, Thuế-Hải quan 09/09]. **2 nhà máy dùng khí ở phía Nam** (Đông Nam Bộ, Tây Nam Bộ), mỗi nhà máy
  khoảng 0,8 tr t, tổng khoảng 1,6 tr t (tóm tắt tìm kiếm). **2 nhà máy dùng than ở miền Bắc**, khoảng 1,0-1,1 tr t
  [NỀN]. Cộng thêm urê NK giá thấp (TQ, Indonesia, Malaysia).
- **Nhà máy mới:** không tìm thấy dự án urê mới nào ở VN [UĐ, tìm kiếm không đầy đủ]. Dư cung khoảng 0,6-1 tr t khiến
  đầu tư mới không hợp lý. Ở vùng: SABIC có kế hoạch 2,6 tr t công suất urê mới (FertilizerDaily 22/08). TQ tiếp tục mở
  rộng công suất 2026 (SunSirs).
- **Bảo dưỡng:** nhà máy khí Đông Nam Bộ bảo dưỡng tổng thể cuối 2025, chạy lại 24/01/2026, sớm 4 ngày (báo Đại biểu
  Nhân dân). Chu kỳ bảo dưỡng tổng thể thường 2-3 năm/lần, dừng khoảng 30-45 ngày [NỀN]. Lịch 2026-27 của 3 nhà máy còn
  lại: không có số.
- **Nguồn khí:** PV GAS 2026 dự kiến khoảng 6,4 tỷ Sm3, gồm khoảng 3,3 tỷ khí nội địa và khoảng 3,1 tỷ LNG (Báo Đầu tư,
  2026). Khí nội địa suy giảm. Mỏ mới (Thiên Nga-Hải Âu, Sư Tử Trắng 2B, Khánh Mỹ-Đầm Rơi, Nam Du-U Minh) dự kiến bổ sung
  khoảng 11 tỷ m3 giai đoạn cuối 2026-2028. Đường ống Nam Côn Sơn giảm khả năng cấp. Mùa khô ưu tiên khí cho điện.
  → **Rủi ro cấu trúc trung hạn [UĐ]:** nếu nhà máy đạm phải nhận phần khí đắt hơn (LNG pha trộn) hoặc bị cắt khí mùa
  khô, lợi thế "khí gắn dầu" bị bào mòn. Với JKM 32, khí LNG làm chi phí khí khoảng 800 USD/t urê, tức lỗ nặng.
- **Độ bền biên [UĐ]:**
  - Nhóm khí phía Nam có vị thế chi phí rất tốt so với thế giới, miễn là hợp đồng khí còn gắn dầu và đủ lượng.
  - Trần giá bán là import parity từ TQ/SEA (CFR SEA khoảng 412,5 ở giữa T9; FertilizerDaily 18/09) cộng chi phí phân
    phối. Sàn là export parity trừ thuế XK 5%.
  - Biên **bền ở mức trung bình (khoảng 180-260 USD/t)**. Nó không bền ở mức đỉnh T4.
  - Rủi ro lớn nhất trong 1-2 năm là TQ nới hạn ngạch (sàn 430-440 bị bỏ, giá nội địa TQ 245 sẽ kéo FOB xuống khoảng
    300-350) đi cùng Brent vẫn cao. Tổ hợp đó làm **biên co về khoảng 100-150**.

## 5. PHÂN LOẠI
**(a) Cú sốc giá urê T3-T5/2026 là TẠM THỜI. Đã đảo chiều, độ tin cậy clean, khoảng 0,9.**
- Bằng chứng: WB −52% từ đỉnh trong 3 tháng. Tender Ấn Độ đi từ 935-959 (T4) xuống 445 (T6) rồi khoảng 352-395
  (T8-T10). Lúc giá đảo chiều, Hormuz **vẫn đóng**.
- Cơ chế đảo chiều: TQ mở hạn ngạch có sàn (cuối T5), Ấn Độ tích trữ đủ rồi rút lui, huỷ cầu.
- Mẫu này giống chu kỳ lưu huỳnh/DAP ở file chị em: đỉnh cấp tính tự vỡ trước khi nguyên nhân gốc được giải quyết.
- P(urê TE > 700 lần nữa trước 31/03/2027) ≈ **0,07**. Điều kiện cần: leo thang (K3) cộng TQ đóng XK cộng Ấn Độ quay
  lại mua mạnh.

**(b) Chế độ biên urê–khí của nhà sản xuất VN, 2-4 quý tới:**
| Nhãn | P | Lý do |
|---|---|---|
| **CYCLICAL** | **0,50** | Giá urê đã về phân vị khoảng 70%. Biên proxy đã về mức năm trước. Động lực chính là chu kỳ khí/dầu, mùa vụ, tồn kho Ấn Độ và tái mở Gulf, tức các biến đảo chiều được trong vài quý |
| **ADMIN_GATED** | **0,30** | Trần và sàn giá bán do **chính sách** quyết định: hạn ngạch và sàn FOB của TQ (430-440/500), thuế XK VN 5% (dự thảo 0%), VAT 5% từ 01/07/2025 (khấu trừ đầu vào, có đề xuất quay lại "không chịu thuế" ở QH 09/12/2025, chưa có quyết định), giá khí do hợp đồng với nhà cung cấp khí nhà nước. Một quyết định hành chính có thể dịch biên ±50-100 USD/t chỉ trong 1 quý |
| **STRUCTURAL** | **0,20** | Khí nội địa suy giảm, LNG chiếm khoảng 50% nguồn cung PV GAS 2026, khí biên toàn cầu tăng gấp 3. Nếu hợp đồng khí đạm chuyển dần sang giá có LNG thì lợi thế chi phí mất **vĩnh viễn**. Hiện chưa có bằng chứng điều đó đang xảy ra cho nhà máy đạm. Cũng có mặt ngược: dư cung khoảng 0,6-1 tr t là cấu trúc |

Diễn giải: đây **không phải cú sốc vĩ mô VN**. Nó là chu kỳ giá hàng hoá bên ngoài, đi qua bộ lọc hành chính (TQ, thuế
VN, hợp đồng khí). VN không khoanh được nguyên nhân gốc (Hormuz, hạn ngạch TQ). VN chỉ chỉnh được tham số biên: thuế
XK, VAT và giá khí.

**(c) Phần còn lại của cú sốc chi phí (khí/dầu) là KÉO DÀI hơn cú sốc giá urê.** Brent +68% YoY và TTF/JKM gấp 3 chỉ hạ khi
Hormuz mở thật. Ngay cả khi mở, khí LNG bình thường hoá chậm hơn dầu (file chị em). Với nhà sản xuất VN, điều đó có nghĩa
là **chi phí khí giảm chậm hơn giá urê nếu có hoà bình**, nên trong tháng đầu của kịch bản hoà bình biên có thể co lại
trước khi nới ra [UĐ].

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-11-04; chấm theo quan sát cuối cùng ≤ ngày kiểm)
**Proxy chấm chính:** BQ `tav2_bq.commodity_prices`, `source='trading_economics'`, `cadence='daily'`, loại T7/CN:
- `urea` USD/t: **TB 5 quan sát cuối ≤ ngày chấm**. Gốc = **447,0** (5 quan sát 27/10-02/11).
- **Biên proxy** = TB5(`urea`) − 25 × (2,5 + 0,06 × TB5(`brent`)). Gốc = **219** (TB5 Brent 110,4, các quan sát 28/10-03/11).

**Proxy phụ:** `worldbank_cmo` `urea` theo tháng (gốc 407,5 ở T9) và tender Ấn Độ kế tiếp (CFR thấp nhất).

**Ba kịch bản [UĐ]:**
- **K1, Hormuz còn tranh chấp/đóng phần lớn tới hết Q1/2027 (p ≈ 0,50).** Giảm từ 0,55 ở file DAP vì ngày 02/11 có kế
  hoạch 2 ngày do Qatar làm trung gian và Brent về 103. TQ siết XK mùa đông, châu Âu khí cao, Ấn Độ đứng ngoài. Urê
  430-500, Brent 98-115.
- **K2, thoả thuận thật trước giữa T1/2027 (p ≈ 0,35).** Hàng Gulf mắc kẹt được xả. Urê 360-420, có khả năng thủng sàn TQ
  ở FOB Trung Đông như T8 (khoảng 370). Brent 75-90. **Biên co ít hơn giá urê** nhờ chi phí khí cũng giảm.
- **K3, leo thang (thả mìn tàu, đánh hạ tầng Gulf) (p ≈ 0,15).** Urê 500-650, Brent 120-140.

| Mốc (ngày chấm) | Chuỗi | Dự báo |
|---|---|---|
| **2026-11-24** (+20 ngày) | TB5 TE `urea` | Trung vị **445**, khoảng 80% **420-478**. **P(<447,0) = 0,52**; P(≤420) = 0,10; P(≥480) = 0,08 |
| | Biên proxy | Trung vị **224**, khoảng 80% **195-255**. **P(>219) = 0,57** |
| **2027-01-03** (+60 ngày) | TB5 TE `urea` | Trung vị **440**, khoảng 80% **385-515**. **P(<447,0) = 0,56**; P(≤400) = 0,20; P(≥500) = 0,13 |
| | Biên proxy | Trung vị **225**, khoảng 80% **170-285**. **P(>219) = 0,54** |
| | WB `urea` T12/2026 (phụ, công bố đầu T1) | Trung vị khoảng 425; P(<407,5) = 0,40 |
| **2027-03-04** (+120 ngày) | TB5 TE `urea` | Trung vị **430**, khoảng 80% **355-535**. **P(<447,0) = 0,60**; P(≤400) = 0,32; P(≥520) = 0,11 |
| | Biên proxy | Trung vị **222**, khoảng 80% **155-300**. **P(>219) = 0,51** |
| **Câu phân loại (a)** | TE `urea` > 700 ở bất kỳ phiên nào trước 2027-03-31 | P = **0,07** |
| **Câu chính sách** | Nghị định hạ thuế XK urê xuống 0% được **ban hành** trước 2027-03-31 | P = **0,55** [UĐ: đã sang Bộ Tư pháp thẩm định, nhưng đề xuất đã lặp nhiều năm] |

Cách chấm: Mike/Bobby truy vấn BQ (`source` chỉ định rõ) tại 3 mốc rồi ghi Brier dưới bảng này. Biên proxy là **thước đo
hướng** với tham số cố định (2,5; 0,06; 25). Nó không phải biên thật của bất kỳ DN nào.

## 7. Chỉ báo dẫn dắt
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu lên ⇔ xuống |
|---|---|---|---|
| 1 | Hạn ngạch/sàn XK urê TQ và giá nội địa Sơn Đông (tuần/sự kiện) | SunSirs, OilChem, FertilizerDaily | Đóng XK mùa đông, nội địa > 1.900 CNY ⇔ hạn ngạch 2027 sớm, sàn bị bỏ |
| 2 | Tender Ấn Độ (khối lượng mua / mời, CFR thấp nhất) (sự kiện) | Argus, FertilizerDaily, UkrAgroConsult | Mua ≥ 80% khối lượng mời và CFR > 450 ⇔ mua < 40% và CFR < 380 |
| 3 | Hormuz: lượt tàu hàng rời và tàu phân bón qua eo, kế hoạch Qatar (tuần) | JMIC, Lloyd's List, World Visualized | Thoả thuận cộng tàu phân bón > 0 bền 4 tuần (urê xuống, Brent xuống) ⇔ mìn hoặc tấn công tiếp |
| 4 | Brent / MFO Singapore và TTF/JKM (ngày) | BQ `brent`, `eu_natural_gas`, sunsirs `fuel_oil` | Brent < 90 làm chi phí khí VN giảm khoảng 30 USD/t ⇔ Brent > 120 |
| 5 | Văn bản VN: thuế XK urê 0%, VAT phân bón, giá khí cấp đạm, phân bổ khí mùa khô (sự kiện) | Cổng Chính phủ, Bộ Tài chính, PV GAS | Thuế XK 0% ban hành ⇔ quay lại "không chịu VAT", cắt khí đạm |

## 8. DD cần kiểm gì (BCTC một nhà sản xuất urê VN phải chứng minh được)
1. **Giá bán bình quân (ASP)** theo kênh: nội địa và xuất khẩu tách riêng, theo quý, **sau chiết khấu/hỗ trợ đại lý**, đã
   tách VAT. So ASP nội địa với import parity (CFR SEA + phí) và export parity (FOB − thuế XK 5%). ASP nội địa không thể
   cao hơn import parity lâu.
2. **Sản lượng SX và tiêu thụ** theo quý và theo vụ. Hệ số vận hành. Số ngày dừng máy theo kế hoạch và ngoài kế hoạch
   (đặc biệt do thiếu khí mùa khô).
3. **Giá khí đầu vào thực tế (USD/MMBtu) và công thức:** gắn MFO hay Brent, hệ số, **sàn/trần**, độ trễ tính bình quân,
   phí vận chuyển, **take-or-pay**, tỷ trọng **LNG pha trộn** và giá của phần LNG. Thời hạn hợp đồng và điều khoản tái
   đàm phán. Có khoản truy thu hay điều chỉnh hồi tố giá khí nào không.
4. **Định mức tiêu hao khí (MMBtu/t urê)** và xu hướng qua các năm (nhà máy già đi thì tiêu hao tăng). Với nhà máy than:
   t than/t urê và giá than.
5. **Tồn kho:** số ngày tồn, giá trị, dự phòng giảm giá (NRV) cuối quý. Kiểm tra có "đẩy hàng vào kênh" (sell-in) cuối
   quý không: tồn kho đại lý, phải thu tăng.
6. **Chi phí dừng máy bảo dưỡng tổng thể:** vốn hoá hay hạch toán ngay vào chi phí, có trích trước không, lịch đợt kế
   tiếp. Quý có bảo dưỡng thì sản lượng giảm và chi phí cố định/t tăng.
7. **Chính sách thuế:**
   - VAT 5% từ 01/07/2025: thuế đầu vào được khấu trừ thì giá vốn giảm. Hạch toán VAT đầu vào trước 07/2025 thế nào (từng
     tính vào giá vốn). **Số dư VAT được hoàn hoặc khấu trừ** và rủi ro nếu quay lại diện "không chịu thuế".
   - **Thuế XK 5%** nằm ở khoản giảm trừ doanh thu hay giá vốn. Tác động nếu xuống 0%.
   - Ưu đãi thuế TNDN còn hay hết.
8. **Thanh toán khí:** phải trả nhà cung cấp khí (số ngày, quá hạn, lãi chậm trả), bảo lãnh, giao dịch bên liên quan.
   Tranh chấp giá khí (nếu có) và dự phòng.
9. **Biên gộp tách theo mảng:** urê tự SX, NPK, phân bón kinh doanh thương mại và hoá chất. Trong lợi nhuận có bao nhiêu
   từ **lãi tiền gửi**: nếu DN dư tiền lớn, lãi tiền gửi gắn lãi suất huy động có thể chiếm phần đáng kể LNTT.
10. **Tỷ giá:** XK thu USD. Giá khí tính theo USD nhưng có thể thanh toán bằng VND. Kiểm tra vị thế ngoại tệ ròng.
11. **Capex và dự án mới** (NPK, mở rộng NH3, hydro, thu hồi CO2): nguồn vốn, IRR công bố so với giả định giá urê/khí.
12. **Phải thu đại lý và chính sách tín dụng mùa vụ:** dự phòng nợ khó đòi, tập trung đại lý.

## 9. Điều gì làm tôi sai
1. **TQ đóng XK sớm và cứng hơn trong mùa đông, đồng thời Ấn Độ quay lại mua mạnh** (tồn kho 6,8-8,1 tr t có thể là ước
   cao). Khi đó urê có thể lên 500-550 trong K1, và forecast 60/120 ngày lệch xuống quá nhiều.
2. **Thoả thuận Hormuz nhanh.** Urê có thể giảm mạnh hơn (FOB Trung Đông khoảng 350-370 như T8). Biên proxy co ít hơn nhờ
   Brent giảm, nhưng nếu giá khí VN có **sàn** thì phần chi phí không giảm theo và biên thật co mạnh hơn proxy.
3. **Công thức giá khí sai.** Nếu giá khí cấp đạm ít nhạy với Brent hơn (có trần, hoặc phần khí giá cố định lớn), biên
   thật hiện nay **cao hơn** proxy (khoảng 222). Ngược lại, nếu có phần LNG thì thấp hơn. Đây là biến DD quan trọng nhất.
4. **TE `urea` basis chưa xác minh.** Chuỗi có thể đứng giá (đã đứng 444-453 trong 3 tuần), nên forecast "đúng do chuỗi
   không nhúc nhích". Vì vậy chấm kèm WB và tender Ấn Độ.
5. **Giá nội địa VN dính.** BCTC có thể trễ hoặc làm mượt so với giá thế giới. Trong T3-T5, giá nội địa (khoảng 13.500
   đ/kg) thấp xa giá thế giới, nên ASP thực hiện có thể không phản ánh chuỗi TE trong 1-2 quý.

**Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices`: TE daily (`urea`, `brent`, `eu_natural_gas`, `liquefied_natural_gas_japan_korea`, `coal`),
  WB monthly (`urea`, `brent`), sunsirs (`fuel_oil`, `liquid_ammonia`), truy vấn ngày 04/11/2026. Phân vị tự tính: urê
  WB T9 73,1% trên 120 tháng; urê TE 446 là 69,4% lịch sử daily.
- FertilizerDaily, "China urea export quota 2026 / nitrogen price floor", 18/09/2026: https://www.fertilizerdaily.com/20260918-china-urea-export-quota-2026-nitrogen-price-floor/
- FertilizerDaily, IPL tender 1,7 tr t (07/10), 28-29/09/2026: https://www.fertilizerdaily.com/20260929-india-urea-tender-ipl-1-7-million-tonnes-december/
- UkrAgroConsult (Nobel Trading 26/10), "Urea prices in Brazil rise amid higher gas costs…", 30/10/2026: https://ukragroconsult.com/en/news/urea-prices-in-brazil-rise-amid-higher-gas-costs-and-limited-supplies/
- Bloomberg, "India Urea Offers Fall…", 08/10/2026 (chỉ tóm tắt tìm kiếm): https://www.bloomberg.com/news/articles/2026-10-08/india-urea-offers-fall-in-sign-of-easing-global-fertilizer-costs
- FDD, tender RCF T8 và cảng TQ, 17/08/2026: https://www.fdd-global.com/article-hot-news/india-tender-lands-with-higher-volume-and-lower-prices-urea-retests-the-policy-floor.html
- FertilizerDaily, lượng phân bón qua Hormuz bằng 0 trong T10, 29/10/2026: https://www.fertilizerdaily.com/20261029-hormuz-fertilizer-shipments-zero-october/md/ ; UN ITC −83%, 07/08/2026: https://www.fertilizerdaily.com/20260807-un-itc-hormuz-disruption-urea-exports-83-percent-drop/ ; SABIC Yanbu, 25/05/2026: https://www.fertilizerdaily.com/20260525-sabic-trucks-25000-tonnes-of-urea-overland-from-jubail-to-yanbu-1250-truckloads-to-bypass-hormuz-closure/md/ ; SABIC công suất mới, 22/08/2026: https://www.fertilizerdaily.com/20260822-sabic-maaden-fertilizer-mou-2026/
- Argus, tender IPL 20/11/2025 (mốc tham chiếu 418 CFR): https://www.argusmedia.com/de/news-and-insights/latest-market-news/2756347-ipl-tender-urea-offer-at-418.40-t-cfr-ec-update
- Mitrade, "Brent slips to $111 as a two-day Hormuz plan lands", 02/11/2026: https://www.mitrade.com/insights/commodity-analysis/oil-news/brent-111-hormuz-two-day-plan-premium-20261102J1102
- Tạp chí Kinh tế-Tài chính (Thuế & Hải quan), "Vì sao urea, SOP được đề xuất giảm thuế…", 09/09/2026: https://thuehaiquan.tapchikinhtetaichinh.vn/vi-sao-urea-sop-duoc-de-xuat-giam-thue-supe-lan-van-giu-5-166478.html
- CafeF, "Đề xuất giảm thuế xuất khẩu phân bón từ 5% xuống 0%", 19/10/2026: https://cafef.vn/de-xuat-giam-thue-xuat-khau-phan-bon-tu-5-xuong-0-188261019074122928.chn
- Thời báo Tài chính, "Từ 1/7/2025: phân bón chịu thuế GTGT 5%" (luật thông qua 26/11/2024): https://thoibaotaichinhvietnam.vn/tu-172025-mat-hang-phan-bon-chiu-thue-gia-tri-gia-tang-5-164936.html
- Doanh nghiệp Hội nhập, ĐBQH đề xuất đưa phân bón trở lại diện không chịu VAT, 10/12/2025: https://doanhnghiephoinhap.vn/de-xuat-dua-phan-bon-tro-lai-dien-khong-chiu-vat-de-giam-ganh-nang-cho-nong-dan-123152.html
- Vinachem, "Vietnam in the global fertilizer shock", 24/03/2026: https://www.vinachem.com.vn/articles/market-and-product-vnc/vietnam-in-the-global-fertilizer-shock.html ; "Fertilizer prices surge…", 03/06/2026: https://www.vinachem.com.vn/articles/market-and-product-vnc/fertilizer-prices-surge-as-domestic-market-faces-pressure-from-global-volatility.html
- Báo Hà Tĩnh, giá phân bón 08/05/2026 (urê 675 nghìn/bao): https://baohatinh.vn/tv/gia-phan-bon-hom-nay-8-5-2026-ure-ca-mau-on-dinh-675-000d-bao-39698.html ; Báo Nghệ An 15/04/2026: https://baonghean.vn/en/gia-phan-bon-hom-nay-15-4-2026-ure-675-000-d-bao-10332951.html
- Đại biểu Nhân dân, bảo dưỡng tổng thể nhà máy khí Đông Nam Bộ, chạy lại 24/01/2026: https://daibieunhandan.vn/nha-may-dam-phu-my-hoan-thanh-bao-duong-tong-the-vuot-tien-do-4-ngay-10405112.html
- PV GAS kịch bản cung khí 2026 (mekongasean): https://mekongasean.vn/pv-gas-xay-dung-kich-ban-bao-dam-nguon-cung-khi-nam-2026-50132.html ; Báo Đầu tư "Nghịch lý thừa khí thiếu khí cho phát điện": https://baodautu.vn/nghich-ly-thua-khi-thieu-khi-cho-phat-dien-d686850.html (ngày chưa xác minh)
- SunSirs, "Urea market … capacity will continue to expand in 2026": https://www.sunsirs.com/uk/detail_news-29536.html
