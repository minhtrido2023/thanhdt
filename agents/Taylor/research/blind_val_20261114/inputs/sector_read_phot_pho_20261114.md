---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND theo dispatch ngày 2026-11-14. Không biết mã nào đang được DD, không xem giá cổ phiếu, BCTC, forward return hay kết luận của ai khác.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ phốt pho vàng (P4) và hoá chất phốt pho hạ nguồn (axit H3PO4 nhiệt, muối photphat kỹ thuật/thực phẩm, PCl3) làm từ quặng apatit VN bằng lò điện. Gồm pipeline cung-cầu, cấu trúc cạnh tranh và rào cản, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED, FORECAST khoá trước, checklist DD.
as_of: 2026-11-14 (BQ sunsirs P4 tới 2026-11-13; tin web ≤ 2026-11-05; snapshot vĩ mô `agents/Taylor/research/dd_PAT_20261114/macro_snapshot_20261114.md`)
---

# SECTOR READ: Phốt pho vàng P4 + hoá chất phốt pho nhiệt, VN, as-of 14/11/2026 (Bobby, BLIND)

Đây không phải một episode VNINDEX và không tính vào N_effective. Nhãn dùng trong file: **[DK]** = dữ kiện có nguồn và ngày.
**[UĐ]** = ước đoán hoặc suy luận của Bobby. **[NỀN]** = hiểu biết nền, lượt này chưa kiểm lại.
Không có khuyến nghị mua/bán. Lượt này **không đọc chi phí vốn/lãi suất**, nên không có bảng 5 tầng. DD nào cần r thì
phải đọc riêng theo luật multi-proxy.

## 0. Kiểm toán blind (đã đọc / đã thấy ngoài ý muốn)
- **Đã đọc:** snapshot vĩ mô do caller đưa (chỉ có dữ liệu vĩ mô thuần) và `sector_read_fertilizer_dap_20261028.md` (lấy mẫu định dạng
  cùng bối cảnh lưu huỳnh/Hormuz). Lệnh grep `feeds/bq_commodity_prices.md` trả về dòng có tên mã. Các dòng đó không chứa giá cổ phiếu
  hay KQKD, và tôi không dùng chúng.
- **Rò rỉ phải khai:** (1) Tên thư mục snapshot do caller đưa có chứa ký hiệu mã. Tôi không tra mã đó. (2) Kết quả tìm web có 1 bài phân
  tích một DN P4 về thuế XK (elibook). Tôi **không mở** bài này, chỉ đọc đoạn trích của công cụ tìm kiếm. (3) Một bài báo Lào Cai
  (20/10/2026) nêu tên một DN hạ nguồn phàn nàn thiếu quặng. Tôi chỉ dùng phần nói về **cung quặng toàn ngành**.
- **Chưa đọc:** `kb/projects/*`, `agents/Taylor/*` (ngoài snapshot), BCTC, giá cổ phiếu, báo cáo CTCK.

## 1. Mức giá và đầu vào [DK, BQ `tav2_bq.commodity_prices`, đã bỏ T7/CN]
| Chuỗi | Hiện tại | So sánh | Ghi chú |
|---|---|---|---|
| P4 TQ (`yellow_phosphorus`, sunsirs, CNY/t, có VAT 13%) | **28.466** (13/11) | TB T11/25 là 22.790, tức **+24% YoY**. Đỉnh 2026 là 34.796 (15/06). Trung vị từ 2018 là 22.929. **Phân vị 80%** của chuỗi 2018+ | 2023-07 trở đi: p10 22.396, p90 28.229 ⇒ **đang ở đỉnh p90 của chế độ hậu-2022**. Giá đứng khoảng 69% số phiên, nhịp thực khoảng tuần |
| P4 quy USD | khoảng **4.270 USD/t** gồm VAT, khoảng 3.780 trước VAT | T11/25 khoảng 3.210 (7,10 CNY/USD) ⇒ **+32% YoY theo USD** | CNY tăng giá 6% trong 12T (snapshot) nên giá tính bằng USD lên mạnh hơn |
| Lưu huỳnh TQ (`sulfur` TE) | 5.197 (TB T11) | đỉnh T8 là 9.261 | Đang rút. Đây là chi phí của tuyến **ướt** (axit làm sạch), không phải tuyến P4 |
| Quặng photphat TQ (`phosphate_rock_cny`) | 1.018 | đứng giá khoảng 1.020-1.060 từ 2023 | Chuỗi này gần như không có thông tin |
| Than cốc TQ (`coke` sunsirs) | 2.108 (TB T11) | 1.495 (T11/25), **+41% YoY** | Chất khử trong lò. Định mức khoảng 1,4-1,6 t/t P4 [NỀN] ⇒ thêm khoảng +900 CNY/t chi phí |
| Lithium carbonate TQ (`lithium` TE) | 92.265 (TB T11) | đỉnh T5/26 là 186.944, **giảm −51%** | Ngược chiều với cầu LFP vẫn mạnh (mục 2). Giá chuỗi pin đang đi xuống |
| Điện sản xuất VN, cấp >35kV đến <220kV, từ 01/11/2026 | BT 1.792, TĐ 1.123, CĐ 3.218 đ/kWh | Bình quân bán lẻ **−2%** (QĐ 1305/QĐ-EVN ngày 30/10/2026). Thêm bậc **≥220kV**: 1.771/1.101/3.110 | Khung giờ mới (QĐ 963/QĐ-BCT): CĐ 17h30-22h30 từ T2 đến T7, **CN không có cao điểm**, TĐ 0h-6h |

**Biên điện, minh hoạ [UĐ, định mức NỀN khoảng 13.000-15.000 kWh/t P4]:** lò chạy 24/7 ở cấp >35kV có giá bình quân gia quyền
(13h BT + 6h TĐ + 5h CĐ) ≈ **1.922 đ/kWh**, khoảng 7,5 US¢. Ngày CN không có cao điểm nên số thực thấp hơn một chút. Mỗi tấn P4
tốn khoảng 27 tr đ, tức khoảng **1.050 USD**, bằng **≈25-28% giá P4 TQ trước VAT**. Đợt giảm 2% chỉ tiết kiệm khoảng **20 USD/t**.
Nếu lò dời được tải sang giờ thấp điểm thì khung giờ mới có lợi hơn. Cần đo bằng hoá đơn thật của DN.

**Thuế XK P4 là biến lớn hơn điện [DK một phần, CẦN KIỂM VĂN BẢN GỐC]:** một trang phổ biến pháp luật của chính quyền (Cần Thơ, đọc
qua đoạn trích tìm kiếm, trang không tải được) nêu mã "Phospho vàng" chịu thuế XK **5% → 10% từ 01/01/2026 → 15% từ 01/01/2027**
trong đợt sửa NĐ 26/2023, gắn với NĐ 199/2025/NĐ-CP (07-08/07/2025). Tôi **chưa đọc được Phụ lục I gốc**. NĐ 201/2026 (hiệu lực
23/07/2026) không nhắc tới P4. Quy đổi [UĐ]: ở FOB khoảng 3.800-4.000 USD, thuế 10% ≈ 380-400 USD/t và 15% ≈ 570-600 USD/t.
**Bước tăng 01/01/2027 ≈ +190 USD/t, gấp khoảng 9 lần khoản tiết kiệm từ đợt giảm giá điện.** Thuế chỉ đánh vào phần **xuất P4
thô**. Phần P4 dùng nội bộ để làm H3PO4/muối rồi mới xuất thì không chịu. Đây chính là ý đồ chính sách: đẩy chế biến sâu.

## 2. Pipeline CẦU
| Mảng | Tỷ trọng P4 [NỀN] | Hướng 6-12T | Bằng chứng |
|---|---|---|---|
| **Glyphosate/thuốc BVTV** (qua PCl3) | lớn nhất, khoảng 25-35% | **Tốt lên** | TQ chống "nội quyển", cấm bán dưới giá vốn. Glyphosate kỹ thuật lên khoảng 25.400 (11/09) rồi **29.000 CNY/t (16/10)**, NBS +2,8% kỳ 11-20/10 rồi **đi ngang cuối T10** (global-agriculture, T10/2026). Mysteel 20/01/2026: cầu P4 tăng thêm khoảng 59,5 kt, dẫn đầu là PCl3 và glyphosate |
| **H3PO4 nhiệt → muối kỹ thuật/thực phẩm, điện tử** | khoảng 30-40% | Vừa | Axit nhiệt cạnh tranh trực tiếp với axit ướt làm sạch (PPA). Lưu huỳnh đắt (đỉnh T8) làm **tuyến nhiệt cạnh tranh hơn**. Lưu huỳnh đã rút −44% ⇒ lợi thế này đang co lại [UĐ] |
| **Pin LFP** (sắt photphat, MAP kỹ thuật) | nhỏ nhưng tăng | **Mạnh về khối lượng, yếu về giá** | SMM: cathode LFP H1/2026 khoảng 2,63 tr t (**+67%**), cell LFP 1.031 GWh (+77%), lưu trữ năng lượng là động lực chính. LFP nén cao thiếu cung (21/10). **Nhưng** nguồn P chính cho LFP là **axit ướt làm sạch + MAP kỹ thuật** (MAP +36%, PPA +23% năm 2025), không phải P4. Lithium −51% từ đỉnh tạo áp lực giá dọc chuỗi [DK+UĐ] |
| Chất chống cháy, P2S5, phụ gia | nhỏ | Ổn định | [NỀN] |
| Phân bón/thức ăn chăn nuôi | **gián tiếp**, chủ yếu tuyến ướt | Chủ yếu là kênh **cạnh tranh nguồn quặng** | Cấm XK lân TQ (từ 19/03/2026, kéo dài, S&P 02/09). Ở VN, DAP/lân nung chảy tranh cùng nguồn apatit Lào Cai với lò P4 (mục 3) |

**Kết luận cầu [UĐ]:** cầu P4 năm 2026 **không** phải điểm yếu. Glyphosate hồi theo chính sách, LFP kéo cả chuỗi photphat. Câu chuyện
"P4 là kim loại pin" thì **phóng đại**: LFP chủ yếu dùng tuyến ướt, và P4 chỉ hưởng qua kênh giá thay thế khi tuyến ướt đắt (lưu huỳnh).

## 3. Pipeline CUNG
**TQ là nơi định giá, chiếm khoảng 70-80% công suất toàn cầu [NỀN].** Vân Nam, Quý Châu, Tứ Xuyên và Hồ Bắc sản xuất bằng thuỷ điện:
- **Mùa khô Tây Nam (T11 đến T4):** giá điện Vân Nam/Tứ Xuyên tăng và có cắt điện. Theo SunSirs, điện chiếm **>40% giá thành** P4
  TQ. Tiền lệ: T9-T10/2021 cắt điện Vân Nam làm P4 lên **53.329** (TB T10/21). Mùa khô 2025-26 kéo giá từ khoảng 23.000 (đầu T3)
  lên **31.163 (15/04/2026)**, đỉnh 34.796 (15/06), rồi giảm về khoảng 27.000 (T7) khi có thuỷ điện mùa mưa (SunSirs, ChemAnalyst
  T5-T7/2026). **Hiện tại (T11) là đầu mùa khô 2026-27** ⇒ chi phí TQ có xu hướng tăng theo mùa trong 1-2 quý tới [UĐ].
- **Môi trường/kiểm soát:** kiểm soát khẩn ô nhiễm ở Nghi Xương và Kinh Môn (Hồ Bắc) từ 12/12/2025 (SMM). Có hạn ngạch năng lượng
  "song carbon" và chống nội quyển [NỀN].
- **Cân đối:** Mysteel (20/01/2026) dự báo năm 2026 có thêm khoảng 105 kt công suất, cầu thêm khoảng 59,5 kt ⇒ **dư khoảng 45,5 kt**,
  cung vào H1 còn cầu vào H2. Dự báo này đã bị đợt tăng giá T3-T6 bác về **hướng**, nhưng vẫn là lời nhắc rằng công suất danh nghĩa
  dư và giá cao mở lại lò ngủ.
- **XK P4 của TQ:** không tìm thấy lệnh cấm/hạn chế XK P4 riêng nào năm 2026. Lệnh cấm chỉ áp cho phân lân. Thuế/hạn ngạch XK P4
  của TQ thì **chưa kiểm** [NỀN: TQ từng đánh thuế XK P4].
- **Kazakhstan** là nguồn cung khác của Ấn Độ (price-watch, nguồn thương mại chỉ để tham khảo).

**VN, cung bị chặn ở QUẶNG chứ không ở lò [DK, Báo Lào Cai 20/10/2026 + các tin T9-T10/2026]:**
- Từ đầu **T6/2026**, một số dây chuyền tuyển apatit ở KCN Tằng Loỏng của đơn vị khai thác nhà nước **dừng hoặc giảm công suất**.
  Theo bản tóm tắt tìm kiếm, cả 3 nhà máy tuyển (Tằng Loỏng, Cam Đường, Bắc Nhạc Sơn, tổng **1,37 tr t/năm**) có lúc dừng, Bắc
  Nhạc Sơn dự kiến chạy lại từ 18/09/2026, Tằng Loỏng chạy khoảng 1/3 công suất.
- Nguyên nhân là **hành chính/đất đai, không phải cạn trữ lượng**: GPMB (tranh chấp đền bù, thiếu đất tái định cư), thủ tục khai
  thác và thuê đất, bãi thải và hồ thải quặng đuôi hết dung tích hoặc hết hạn thuê, thủ tục ĐTM, và quy hoạch đang rà soát.
- Ngày 14/09/2026 tỉnh xác nhận cho thu hồi khoảng **436.565 t quặng loại III** (Mỏ Cóc 1). Theo DN, lượng này **chỉ đủ chạy cầm
  chừng đến hết T11/2026**. Còn **3,53 tr t quặng loại III tồn** ở Làng Cáng và KT13, đang xin trung ương cho dùng. GPMB các mỏ Cam
  Đường, Hợp Thành, Cốc San dự kiến xử lý trong T10/2026, KT32 và Làng Cáng 2 trong Q4/2026.
- Tỉnh có 46 dự án khoáng sản: 23 đang chạy, 11 tạm dừng, 12 chưa chạy. Dự án tuyển Tam Đỉnh 250 kt/năm đã vào sản xuất.
- **Tác động lên lò P4 [UĐ]:** lò điện cần **quặng cục loại I** (hoặc quặng tinh loại III đã thiêu kết/vê viên). Bài báo nói rõ nhà
  máy **DAP, lân nung chảy và phốt pho vàng** có nguy cơ thiếu quặng, hệ số sử dụng thiết bị thấp. DN **có mỏ hoặc quặng cục riêng**
  ít bị ảnh hưởng hơn DN **mua quặng** của đơn vị khai thác nhà nước. Đây là điểm phân hoá lớn nhất trong ngành lúc này.
- **Điện VN:** biểu giá một giá theo cấp điện áp. **Không có "giá điện ưu đãi" riêng cho ngành P4** [NỀN; chưa thấy văn bản nào].
  Lợi thế so với TQ là **ổn định** (không có giá mùa khô, ít cắt điện), không phải mức giá thấp hơn. Lưu ý NĐ 72/2025 sửa bởi NĐ
  278/2026 (09/07/2026): EVN được điều chỉnh tối thiểu 3 tháng/lần, **không điều chỉnh** nếu mức tính ra giảm dưới 1% hoặc tăng dưới 2%.
  Chi phí điện 2025 thấp hơn giá bán 5,32% (Tuổi Trẻ 24/10/2026) nên mới có đợt giảm 2%. Năm 2026 LNG/khí đắt vì Hormuz (TTF khoảng
  94 EUR/MWh cuối T10, xem bản đọc DAP) ⇒ chi phí điện **năm 2026**, công bố khoảng 2027-28, có thể đảo chiều [UĐ].

## 4. Cấu trúc cạnh tranh và rào cản gia nhập VN [chủ yếu NỀN + UĐ]
- **Địa lý:** apatit VN nằm gần như toàn bộ ở **Lào Cai** (vành đai Cam Đường đến Bát Xát). Lò P4 tập trung ở KCN Tằng Loỏng và Bắc
  Duyên Hải. Công suất ngành khoảng **180-200 kt/năm**: sản lượng 2022 khoảng 180,9 kt (Nông nghiệp VN, bài 2024), là nhà XK lớn
  thứ hai thế giới sau TQ [NỀN]. Thị trường XK là Nhật, Hàn, Ấn Độ, châu Âu.
- **Số người chơi:** **ít**, khoảng 5-8 pháp nhân vận hành lò. Gồm một nhóm DN thuộc tập đoàn hoá chất nhà nước (mua quặng của đơn vị
  khai thác cùng hệ thống) và một vài tập đoàn tư nhân tích hợp mỏ, lò và hạ nguồn. **Cạnh tranh về giá là "price-taker" theo giá TQ.**
  Cạnh tranh thật diễn ra ở **quyền tiếp cận quặng** và **mức chế biến sâu**.
- **Rào cản (từ cao xuống thấp):**
  1. **Quặng/giấy phép khai thác:** theo Luật Địa chất và Khoáng sản 2024 (hiệu lực 01/07/2025) [NỀN] và quy hoạch khoáng sản. Trữ
     lượng loại I hữu hạn. Cấp phép mới chậm và vướng GPMB (mục 3). Đây là **hào thật duy nhất**, nhưng là hào **hành chính**, có thể
     đóng hoặc mở theo văn bản.
  2. **Môi trường:** xỉ lò, bùn phốt pho, khí lò, hồ thải. ĐTM và kiểm soát ngày càng chặt [UĐ].
  3. **Hạ tầng điện:** đấu nối 110-220kV, bậc ≥220kV mới có giá thấp hơn khoảng 1-3%.
  4. **Vốn và know-how:** lò 10-20 kt mỗi dây chuyền, tích hợp hạ nguồn (axit nhiệt, muối thực phẩm) cần chứng nhận khách hàng.
  5. **Chính sách thuế XK tăng dần:** **rào cản với mô hình "xuất P4 thô"**, và là **lợi thế với DN đã tích hợp hạ nguồn**.
- **Ngược chiều:** không có rào cản ở **đầu ra** vì giá do TQ đặt. Không có quyền định giá. Biên = giá TQ quy USD − (điện + quặng +
  cốc + thuế XK). Ba cấu phần sau là **hành chính/quản lý** ở VN.

## 5. PHÂN LOẠI (động lực chính của biên ngành VN trong 12 tháng tới)
**ADMIN_GATED p ≈ 0,45 · CYCLICAL p ≈ 0,40 · STRUCTURAL p ≈ 0,15. Độ tin cậy: AMBIGUOUS** (bằng chứng trộn lẫn).
- **ADMIN_GATED (0,45):** ở VN, cả **khối lượng** (quặng do GPMB/thủ tục/quy hoạch, mục 3), **thuế XK** (10%→15% ngày
  01/01/2027, đã biết trước nhưng chưa kiểm văn bản gốc) và **giá điện** (EVN/BCT quyết, khung giờ thay đổi) đều do văn bản quyết
  định. Lời giải cũng là một văn bản: cho dùng 3,53 tr t quặng tồn, phê duyệt quy hoạch, nâng công suất khai trường. **Trục 2:
  khoanh được** bằng 1-2 quyết định cấp tỉnh/bộ, nhưng tiến độ thực tế đã trễ ít nhất 5 tháng (T6→T11) ⇒ không phải "vài tuần".
- **CYCLICAL (0,40):** giá P4 do TQ đặt, theo **mùa thuỷ điện**, chu kỳ glyphosate và giá lưu huỳnh của tuyến cạnh tranh. Hiện ở
  **p90 của chế độ 2023+**. Lịch sử T11→T5 không có mùa vụ ổn định: trung vị khoảng −1%, dao động từ −33% (2022-23) đến +36%
  (2025-26). **Cả hai lần xuất phát từ mức cao (T11/2022, T11/2023) đều giảm 12-33%.**
- **STRUCTURAL (0,15):** "P4 thành vật liệu chiến lược năng lượng mới, kèm hạn ngạch năng lượng TQ" ⇒ nền giá cao vĩnh viễn hơn
  2018-20 (khoảng 15.000-18.000). Bằng chứng ủng hộ: chế độ giá 2023+ có trung vị khoảng 23.700, cao hơn khoảng 50% so với
  2018-20. Bằng chứng chống: LFP dùng tuyến ướt, lithium −51%, Mysteel thấy dư cung.

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-11-14, chấm theo quan sát cuối cùng ≤ ngày chấm)
**Proxy chính:** BQ `tav2_bq.commodity_prices`, `metric_key='yellow_phosphorus'`, `source='sunsirs'`, `cadence='daily'`, bỏ T7/CN.
Mốc gốc **28.466 CNY/t (13/11/2026)**. Lý do nghiêng về giảm [UĐ]: mức đang ở p90, lưu huỳnh rút làm mất lợi thế thay thế, giá cao mở lại
công suất ngủ, lithium/LFP giảm giá. Lực ngược là mùa khô T11-T4 và chính sách chống nội quyển.

| # | Mốc | Biến | Dự báo |
|---|---|---|---|
| F1 | **2027-05-14** (6T) | P4 sunsirs | Trung vị **≈ 26.500** (−7%), khoảng 80%: **22.500-32.500**. **P(< 28.466) = 0,60**; P(< 24.000) = 0,25; P(> 32.000) = 0,12 |
| F2 | **2027-11-12** (12T) | P4 sunsirs | Trung vị **≈ 25.000** (−12%), khoảng 80%: **20.500-31.500**. **P(< 28.466) = 0,66**; P(< 23.000) = 0,32; P(> 32.000) = 0,10 |
| F3 | 2027-02-26 (giữa mùa khô) | P4 sunsirs | P(> 28.466) = **0,50**. Đây là cửa sổ duy nhất tôi thấy cân bằng (rủi ro mùa khô) |
| F4 | 2027-11-12 | **Biên điện** = P4 sunsirs (CNY) × USD/CNY⁻¹ × USD/VND − 14.000 kWh × giá BT cấp >35kV của EVN | P(co lại so với mốc 14/11/2026) = **0,65**. Mốc ≈ 28.466/6,67×25.725 − 14.000×1.922 ≈ **110 tr − 27 tr ≈ 83 tr đ/t** (chỉ minh hoạ, giá có VAT TQ) |
| F5 | 2027-11-14 | Giá bán lẻ điện bình quân EVN | P(> 2.159,9 đ/kWh) = **0,55**; P(≥ +5%) = **0,25**; P(< 2.159,9) = 0,10 |
| F6 | 2027-01-15 | Thuế XK P4 (HS 2804.70) | P(mức 15% hiệu lực từ 01/01/2027 theo văn bản, không bị hoãn/giảm) = **0,70** |
| F7 | 2027-05-31 | Quặng VN | P(tin công khai xác nhận cả 3 nhà máy tuyển của đơn vị khai thác nhà nước chạy lại ≥ 80% công suất) = **0,30**; P(có quyết định cho dùng 3,53 tr t quặng loại III tồn) = **0,50** |

Chấm điểm: Mike hoặc Bobby đọc BQ (`source` chỉ định rõ) ở F1-F4, đọc văn bản EVN/BCT/Chính phủ ở F5-F6, Báo Lào Cai/Bộ Công Thương ở F7.
Ghi Brier dưới mục này.

## 7. Chỉ báo dẫn dắt
1. **Giá P4 Vân Nam và đấu thầu hàng tuần** (đấu thầu thứ Năm của một nhà sản xuất lớn TQ: 27.350 ngày 06/08/2026, SMM) và **thông báo cắt điện
   hoặc giá điện mùa khô** Vân Nam/Tứ Xuyên. Báo động khi có lệnh cắt điện bắt buộc.
2. **Glyphosate kỹ thuật NBS 10 ngày.** Giảm 2 kỳ liên tiếp sẽ làm mất lực cầu chính.
3. **Lưu huỳnh TQ/ME** (`sulfur`). Lưu huỳnh rút sâu ⇒ tuyến ướt rẻ lại ⇒ áp lực lên axit nhiệt.
4. **Quặng Lào Cai:** quyết định dùng quặng tồn, GPMB các khai trường, phê duyệt quy hoạch khoáng sản.
5. **Văn bản thuế XK P4** và **EVN/BCT** (mỗi lần điều chỉnh, khung giờ).
6. Vĩ mô (snapshot): USD/VND −2,4% YoY (VND mạnh lên) làm giảm doanh thu XK quy VND. CNY +6% có lợi cho cạnh tranh của VN so với TQ.
   CPI VN 5,09% đang tăng tốc (+1,84pp YoY), là rủi ro EVN tăng giá và chi phí nhân công.

## 8. Điều gì làm tôi sai
1. **Mùa khô 2026-27 khắc nghiệt** (lặp lại 2021) ⇒ P4 > 35.000, F1/F2 sai hướng.
2. **Chống nội quyển TQ cắt mạnh công suất P4/glyphosate** ⇒ nền STRUCTURAL đúng hơn 0,15.
3. **VN gỡ nhanh quặng tồn** ⇒ cổng ADMIN mở sớm, khi đó trọng số chuyển sang CYCLICAL.
4. **Thuế XK P4 không như tôi đọc** (văn bản gốc khác) ⇒ F6 và phần quy đổi USD/t ở mục 1 sai.
5. Proxy sunsirs **không phải giá XK FOB VN**. Hợp đồng XK có thể ký theo quý hoặc năm, nên KQKD trễ 1-2 quý so với chuỗi.

## 9. DD cần kiểm gì (cho DN trong ngành này)
1. **Nguồn quặng:** tỷ lệ quặng tự khai thác so với mua ngoài. Giấy phép mỏ (số, hạn, công suất, trữ lượng còn lại loại I). Bị ảnh hưởng
   bởi đợt dừng tuyển T6/2026 tới đâu (sản lượng P4 từng tháng Q3-Q4/2026). Tồn kho quặng đầu kỳ. Giá mua quặng và cơ chế giá.
2. **Hệ số sử dụng lò** (công suất danh định so với thực tế) theo quý 2025-2026, và số lò dừng.
3. **Điện:** kWh/t thực tế, cấp điện áp đấu nối (≥220kV?), tỷ trọng tiêu thụ giờ thấp điểm, hoá đơn trước/sau 01/11/2026, rủi ro khung
   giờ mới.
4. **Thuế XK:** tỷ trọng doanh thu **P4 xuất thô** so với **hạ nguồn**. Mức thuế áp thực tế năm 2026 (tờ khai). Tác động khi lên 15%. Có
   chuyển được sang hạ nguồn không.
5. **Cơ cấu giá bán:** spot hay hợp đồng, kỳ định giá, tiền tệ. Độ trễ so với sunsirs. Khách hàng top-5 và tập trung theo quốc gia.
6. **Chi phí than cốc** (+41% YoY ở TQ) và nguồn cốc.
7. **Hạ nguồn:** axit nhiệt, muối thực phẩm/kỹ thuật, PCl3. Chứng nhận (thực phẩm, điện tử). Tiếp xúc thật với chuỗi LFP (đơn hàng,
   không phải "câu chuyện").
8. **Môi trường/pháp lý:** ĐTM, xử phạt, hồ thải, xỉ. Theo luật 27/09: chỉ **WARNING**, không chặn.
9. **Nhạy cảm:** EBIT theo ±10% giá P4, ±5% giá điện, thuế XK 10→15%, −20% khối lượng do quặng. Báo cáo theo khoảng, không 1 số.
10. **FX:** doanh thu USD so với chi phí VND. VND mạnh lên trong 12T vừa qua.

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (sunsirs `yellow_phosphorus`, `coke`, `caustic_soda`; TE `sulfur`, `lithium`, `phosphate_rock_cny`, `coal`), truy vấn 14/11/2026; phân vị tự tính.
- Snapshot vĩ mô `mike/agents/Taylor/research/dd_PAT_20261114/macro_snapshot_20261114.md` (as-of 14/11/2026).
- Báo Lào Cai, "Khơi thông nguồn nguyên liệu…", 20/10/2026: https://baolaocai.vn/khoi-thong-nguon-nguyen-lieu-tao-da-cho-cong-nghiep-tang-truong-post912336.html ; liên quan: https://baolaocai.vn/thao-go-kho-khan-trong-trien-khai-cac-du-an-cua-cong-ty-apatit-viet-nam-post911263.html , https://tapchicongthuong.vn/thao-go-kho-khan-cho-apatit-viet-nam-gan-voi-thuc-day-tang-truong-555773.htm (chỉ đọc qua đoạn trích tìm kiếm)
- Giáo dục VN, "EVN thông tin… giá điện từ 1/11/2026", 05/11/2026: https://giaoduc.net.vn/evn-thong-tin-ve-viec-thuc-hien-chinh-sach-gia-dien-tu-ngay-1112026-post263825.gd ; SGGP biểu giá chi tiết 05/11/2026: https://www.sggp.org.vn/chi-tiet-gia-ban-le-dien-ap-dung-tu-ngay-1-11-2026-post880092.html ; LSVN: https://lsvn.vn/gia-ban-le-dien-binh-quan-giam-2-a181851.html ; Tuổi Trẻ (chi phí điện 2025 −5,32%): https://tuoitre.vn/gia-dien.html ; Báo Pháp luật (NĐ 278/2026, ngưỡng 1%/2%): https://baophapluat.vn/quy-dinh-moi-ve-gia-ban-le-dien-giam-duoi-1-tang-duoi-2-khong-dieu-chinh.html
- Thuế XK P4: pbgdpl.cantho.gov.vn (chỉ đoạn trích, trang không tải được): https://pbgdpl.cantho.gov.vn/sua-doi-bieu-thue-xuat-khau-bieu-thue-nhap-khau-uu-dai-tai-nghi-dinh-262023nd-cp ; NĐ 199/2025 (bản EN, 403): https://thuvienphapluat.vn/van-ban/EN/Xuat-nhap-khau/Decree-199-2025-ND-CP-amendments-to-Decree-26-2023-ND-CP-schedule-of-export-tariffs/664759/tieng-anh.aspx ; NĐ 201/2026 (TT WTO 24/07/2026): https://trungtamwto.vn/tin-tuc/33076-tu-ngay-2372026-chinh-thuc-giam-thue-xuat-khau-nhieu-mat-hang-khoang-san
- Mysteel, "China yellow phosphorus market 2026: supply on rise, price under pressure", 20/01/2026: https://www.mysteel.net/news/5110731-china-yellow-phosphorus-market-2026-supply-on-rise-price-under-pressure
- SMM, đấu thầu P4 27.350 (06/08/2026): https://news.metal.com/newscontent/104046410-phosphorus-chemical-wengfu-yellow-phosphorus-thursday-tender-winning-bid-price-27350-yuanmt ; SMM Hồ Bắc kiểm soát môi trường: https://news.metal.com/vn/newscontent/103678919 ; SMM LFP/chuỗi P năng lượng mới: https://news.metal.com/en/newscontent/103857855-Brief-Analysis-of-Production-Changes-in-Chinas-Phosphorus-Based-New-Energy-Materials-2025 , https://news.metal.com/newscontent/104002063 , https://news.metal.com/newscontent/104171455-lfp-sees-another-large-order-as-high-end-product-supply-demand-tightens
- SunSirs/ChemAnalyst/CCM (đỉnh T4, cháy Quý Châu 14/05, điện >40% giá thành, T5-T7 suy yếu; chỉ đọc qua đoạn trích): https://www.sunsirs.com/commodity-news/petail-33016.html , https://www.chemanalyst.com/NewsAndDeals/NewsDetails/china-yellow-phosphorus-prices-ease-as-weak-downstream-demand-43504 , https://www.chemanalyst.com/NewsAndDeals/NewsDetails/china-yellow-phosphorus-prices-jump-4-3-as-plant-outages-44658 (403)
- Glyphosate T10/2026: https://www.global-agriculture.com/crop-protection/chinas-glyphosate-technical-price-climbs-2-8-in-october/ , https://www.global-agriculture.com/crop-protection/chinas-pesticide-technical-prices-turn-higher-as-regulators-crack-down-on-below-cost-selling/
- Cấm XK lân TQ: S&P Global 02/09/2026: https://www.spglobal.com/energy/en/news-research/latest-news/agriculture/090226-china-dap-map-exports-remain-uncertain-as-september-begins ; Fertilizer Daily 29/07/2026: https://www.fertilizerdaily.com/20260729-china-phosphate-export-restrictions-august-2026-russia-quotas/
- Sản lượng P4 VN 2022: https://vietnamagriculture.nongnghiep.vn/yellow-phosphorus-has-a-significant-domination-in-the-japan-and-korea-d378247.html ; giá P4 VN/Nhật/Ấn Q2/2026 (nguồn thương mại, tham khảo): https://www.price-watch.ai/yellow-phosphorus-price
