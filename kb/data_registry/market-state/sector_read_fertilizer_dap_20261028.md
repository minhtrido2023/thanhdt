---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-28. KHÔNG biết mã cổ phiếu nào, giá cổ phiếu, forward return hay kết luận của bất kỳ ai khác.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ phân bón lân (DAP) + chuỗi nguyên liệu lưu huỳnh–NH3 cho nhà sản xuất VN nhập khẩu nguyên liệu. Gồm phân loại cú sốc chi phí (A tạm thời / B kéo dài), độ bền giá DAP và FORECAST khoá trước.
as_of: 2026-10-28 (giá BQ tới 2026-10-23; tin web ≤ 2026-10-27)
---

# SECTOR READ: Phân bón lân DAP + chuỗi lưu huỳnh/NH3, as-of 28/10/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc:** `kb/data_registry/feeds/bq_commodity_prices.md` và `kb/data_registry/market-state/vn_sector_read_rubber_20261027.md`
  (dùng làm mẫu định dạng). Ghi chú trung thực: đoạn "Hệ quả cost" trong file feeds có nêu tên 3 mã cổ phiếu là
  đối tượng chịu chi phí lưu huỳnh. Đoạn đó không có giá cổ phiếu, KQKD hay forward return. Tôi không dùng nó cho
  phân loại.
- **BQ (tự truy vấn ngày 28/10):** `tav2_bq.commodity_prices` với `source` chỉ định rõ, gồm TE daily `sulfur`, `di_ammonium`,
  `urea`, `brent`, `eu_natural_gas`, `phosphate_rock_cny` và WB monthly `dap`, `tsp`, `phosphate_rock`, `urea`,
  `potassium_chloride`, `natural_gas`, `eu_natural_gas`, `brent`. Tôi không dùng view `commodity_latest` (bẫy #2).
  **BQ không có chuỗi NH3/amoniac nào.**
- **Web:** chỉ dùng bài công bố ≤ 28/10/2026, có ghi ngày ở mục Nguồn.
- **Chưa đọc hoặc đã bỏ qua:** `kb/projects/*`, `agents/Taylor/*` và mọi file nhắc tên mã DN phân bón. Khi tìm web, tiêu
  đề của 2 kết quả là bài phân tích một mã DN phân bón VN (elibook 11/03/2026, báo cáo CTCK 03/05/2026). Tôi **không
  mở** hai bài này. Tôi không tra giá cổ phiếu, BCTC hay khuyến nghị CTCK.

## 1. Mức giá và đa proxy [DK, BQ trừ khi ghi khác]
| Chuỗi | Hiện tại | Mốc so sánh | Ghi chú |
|---|---|---|---|
| Lưu huỳnh TE (`sulfur`, CNY/t, giá nội địa TQ) | **5.714** (22-23/10) | TB tháng đạt đỉnh 9.261 (T8/26), đỉnh ngày 11.084 (T6). TB T1-T2/2026 (trước chiến tranh) là 3.989/3.892. TB 2025 khoảng 2.600. TB 2023-24 khoảng 750-1.700 | Từ đỉnh tháng giảm −38%, từ đỉnh ngày giảm −48%. Từ 14/10 mỗi tuần giảm khoảng −300 đến −500. Còn cao **×1,45** so với mức trước chiến tranh |
| Lưu huỳnh Trung Đông, hợp đồng tháng FOB | T10: Qatar **835**, KPC 820, ADNOC 890 USD/t | T9 (suy ngược) 880/865/960. Index ME đạt đỉnh 947 (T7). Năm trước khoảng 150-180 | SMM 08/10/2026. **ME chỉ giảm −5 đến −10% từ đỉnh, trong khi TQ nội địa giảm −38%** |
| DAP TE (`di_ammonium`, USD/t) | **802,5** (23/10) | Đứng yên 800-802,5 từ 09/09. T4/26 là 723, T12/25 là 622 | Basis chưa rõ (xem bẫy). Báo giá rất "dính" |
| DAP WB (US Gulf, USD/t, tháng) | **800,6** (T9) | **Phân vị 96,7%** của 120 tháng (từ 10/2016). Max 10 năm là 954 (T4/2022) | Khớp với caller (p96-98) |
| DAP CFR Ấn Độ | 895-915 (T9). IPL mua 930-935 CFR (T5) | Chênh khoảng +100 so với WB/TE | Producer.com trích Argus (T10); Business Standard 12/05/2026 |
| Urea TE / WB | 453 (23/10) / 407,5 (T9) | WB đạt đỉnh 856,9 (T4/26) rồi giảm −52% | TQ vẫn XK 6-7 tr t urea năm 2026 |
| Tỷ lệ DAP/urea (WB) | **1,96** (T9) | Trung vị 10 năm 1,48, p90 1,73. **Phân vị 97,5%** | Lân đắt nhất tương đối so với đạm trong 10 năm, nên áp lực huỷ cầu dồn vào P |
| Quặng photphat WB | 170 (từ T7/26) | 152,5 đứng yên 2024 đến T5/26 | WB đứng giá lâu, tín hiệu yếu |
| Quặng photphat TQ TE (CNY/t) | 1.019 | Khoảng 1.020-1.026 | 94% phiên đứng giá, gần như không có thông tin |
| Brent TE | **116,7** (23/10) | 83,8 (03/08), nên tăng +39% trong 11 tuần | Leo thang Hormuz T10 |
| Khí TTF TE (EUR/MWh) | **93,9** (23/10) | 57,5 (03/08), WB T9 là 25,4 $/mmbtu | Khí tăng +63% từ đầu T8. Đây là chi phí NH3 ở châu Âu và giá biên NH3 toàn cầu |
| NH3 | không có số T10 | Tampa 01/2026 là 585 CFR. Qcintel 29/09 nói Tampa T10 "giảm nhẹ" (không có con số). ICIS dự báo nền cao hơn T9-T12 | Gulf chiếm khoảng 20-30% NH3 XK. Qatar ngừng NH3, Iran ngừng (WB 14/05). Theo EnterpriseAM 06/10, hàng NH3 rời Gulf "gần như dừng" |

**Phân kỳ quan trọng [UĐ]:** TE `sulfur` là giá **nội địa TQ** và nó giảm nhanh vì TQ đang huỷ cầu: nhà máy lân cắt
công suất khoảng −12% YoY, NK lưu huỳnh T8 −65% YoY, người mua từ chối giá >1.000 USD (Argus qua SCMP, T9/2026),
và TQ cấm xuất lân nên không cần chạy hết công suất. Nhà sản xuất DAP **VN nhập khẩu** mua theo giá CFR Đông Nam Á, gần
**ME FOB + cước**, chứ không theo giá nội địa TQ. Ở đầu ngành, Indonesia HPAL (niken) tranh mua cùng nguồn. Vì vậy:
**về HƯỚNG**, hai proxy đồng thuận (đỉnh đã qua). **Về MỨC**, chi phí biên thật của nhà NK VN giảm ít hơn nhiều so với
mức −38% mà TE CNY gợi ý: ME FOB T10 vẫn khoảng 820-890, chỉ thấp hơn đỉnh 5-10%. Quy đổi thô: 5.714 CNY/t gồm VAT TQ
13% tương đương khoảng 710 USD/t trước thuế, tức **thấp hơn** import parity ME (835 + cước). Đó là lý do TQ ngừng mua.
Proxy TE dẫn hướng trước nhưng không phải giá vốn của VN.

**Bẫy dữ liệu:** (1) TE `di_ammonium` đứng giá 800-802,5 suốt 6 tuần và basis chưa xác minh. Nếu đây là giá FOB TQ
trong lúc TQ không xuất thì nó là báo giá danh nghĩa. Cần dùng WB DAP và CFR Ấn Độ đối chiếu. (2) TE `sulfur` có 53%
phiên đứng giá (theo file feeds), nên đọc theo nhịp tuần. (3) BQ không có NH3. Cột NH3 ở trên hoàn toàn từ web, không
có chuỗi để chấm điểm.

## 2. Nguyên nhân gốc: hai tầng chồng nhau
**Tầng 1 là cú sốc cung ngoại sinh (Hormuz) [DK].** Ngày 28/02/2026 Mỹ–Israel tấn công Iran. Ngày 02-05/03 Hormuz đóng
trên thực tế (rút bảo hiểm P&I). Các thoả thuận ngừng bắn đều đổ vỡ: 08/04 (Islamabad thất bại 13/04), MoU 17/06 (Iran
đóng lại 20/06), đình chiến tạm sụp đổ 08/07. Tình hình T10: "Strait closed, Day 240" (straits.live 27/10). Tuần kết thúc
04/10 có 11 tàu dầu bị tấn công (IMO qua CNBC 09/10). Ngày 14/10 một tàu container chìm. Ngày 23/10 một tàu dầu bị vô
hiệu hoá. Khoảng 492 tàu chờ ngoài eo (JMIC 25/10). Đàm phán đình trệ: ngày 19/10 Araghchi nói điều kiện mở eo không
đổi (Mỹ gỡ phong toả + nới trừng phạt) và Trump bác đề xuất ngừng bắn 7 ngày. Dầu đã đi vòng được, Kpler 21/10 cho thấy
xuất khẩu dầu Trung Đông khoảng 24 tr thùng/ngày, cao hơn trước chiến tranh, và dòng qua Hormuz khoảng 82%. **Nhưng phân
bón và lưu huỳnh KHÔNG có đường ống**: T9 chỉ 8 tàu urea rời Gulf, NH3 gần như dừng, Ma'aden phải dùng khoảng 3.500 xe
tải chở sang Yanbu và xuất 1 lô DAP qua Duqm (Oman). Gulf chiếm khoảng 44% lưu huỳnh XK đường biển toàn cầu
(EnterpriseAM 06/10). Ma'aden hạ kế hoạch 2026 xuống 6-6,5 tr t DAP-eq vì thiếu lưu huỳnh. Mosaic giảm một nửa sản lượng
2 nhà máy Mỹ và dừng Brazil.

**Tầng 2 là thiếu hụt lưu huỳnh CẤU TRÚC đã có từ TRƯỚC chiến tranh [DK + UĐ].** TE `sulfur` đi từ khoảng 950-1.400
(2024) lên 2.300-2.900 (Q2-Q3/2025), rồi 3.900 (T12/25-T2/26). Tức là ×3-4 **trước** ngày 28/02. Động lực là cầu axit
sunfuric cho niken HPAL Indonesia (NK >3 tr t/năm, Argus 12/2024) và LFP, cộng phốt phát; *Sulphur* 422 (28/01/2026)
có bài "The sulphur market in deficit". Bằng chứng đây là cấu trúc chứ không phải nhiễu: ngày 07/10/2026 Vale–Huayou
tính thu hồi lưu huỳnh từ bã thải Pomalaa để "giảm chi phí lưu huỳnh cao" (BC Insight). Đây là phản ứng đầu tư nhiều
năm, không phải điều chỉnh tồn kho. SunSirs/Securities Daily 20/10 viết: "trọng tâm giá khó quay lại mức thấp trước đây".

**Chính sách TQ khuếch đại phía DAP [DK].** Từ 19/03/2026 TQ cấm xuất khẩu toàn bộ MAP/DAP và NP/NK, ban đầu "tới
31/08" (OilChem 27/03), sau đó thực tế kéo dài. XK lân TQ năm 2026 gần bằng 0, so với 5,3 tr t năm 2025
(UkrAgroConsult 16/10). TQ cũng hạn chế xuất axit sunfuric. Argus dự báo 2027 chỉ phục hồi khoảng 2 tr t và XK lân TQ
nối lại khoảng T5/2027, với rủi ro trễ nếu lưu huỳnh không giảm đủ.

## 3. PHÂN LOẠI cú sốc chi phí lưu huỳnh/NH3 (trục 1 + trục 2)
**Kết luận: (B) KÉO DÀI/CẤU TRÚC về MỨC chi phí. Độ tin cậy khoảng 70/30. Nhưng HƯỚNG trong 1-2 quý tới là GIẢM
(đỉnh cấp tính đã qua).** Nói gọn: **"A về hướng, B về mức".**
- **Trục 1 (gốc):** nền là thiếu hụt cấu trúc đã có từ trước (tầng 2), cộng thêm cú sốc ngoại sinh. Nền này không do
  VN tạo ra và không phải mất cân đối vĩ mô VN.
- **Trục 2 (có khoanh được không):** **KHÔNG khoanh được bằng một hành động chính sách.** VN không có công cụ nào.
  Muốn giải quyết cần thoả thuận Mỹ–Iran, và đã có 3 lần ngừng bắn đổ vỡ trong 8 tháng. Chuỗi phân bón và lưu huỳnh
  bình thường hoá **chậm hơn** dầu (không có đường ống, tàu hàng rời mất 30-40 ngày để quay về, vòng NH3 phải khởi
  động lại). Ngay cả khi có thoả thuận, phí bảo hiểm và gom tàu vẫn kéo dài hàng tuần đến hàng tháng.
- **Vì sao không phải A:** "bình thường" cho nhà NK VN là mức 2024-H1/2025 (TE khoảng 1.000-2.600 CNY/t, ME khoảng
  150-300 USD). Để về đó trong ≤3 quý (tới khoảng 31/07/2027) cần đồng thời (a) Hormuz mở thật sớm và (b) cầu
  HPAL/LFP hạ nhiệt. Tôi ước P(TE `sulfur` ≤ 3.000 vào 31/07/2027) ≈ 0,25. Ngay mức trước chiến tranh (khoảng 3.900)
  đã gấp 1,5-4 lần "bình thường" đó. NH3: TTF tăng +63% từ T8 và NH3 Gulf gần như dừng, nên tôi không thấy lối về
  bình thường trước Q2/2027.
- **Vì sao không phải B "clean":** đỉnh đã tự vỡ do huỷ cầu ngay cả khi Hormuz **vẫn đóng**: TE −48% từ đỉnh ngày, ME
  FOB giảm 2 tháng liên tiếp, Argus/ICIS báo người mua kháng giá và tồn kho TQ cao hơn. Tiền lệ 2022: TE đi từ 3.925
  (T6) xuống 1.114 (T8), tức **−72% trong 2 tháng**. ME từ 589 về 253 USD (−57%) trong khoảng 1 tháng. Nếu có thoả
  thuận thật, lượng lưu huỳnh tồn kho mắc kẹt ở Gulf (đóng khối do kho đầy) có thể **xả ồ ạt** và đưa giá về vùng
  trước chiến tranh nhanh hơn nhiều so với kịch bản B.
- **Biên nhà sản xuất DAP nhập S + NH3, có quặng nội địa [UĐ, định mức NỀN]:** mỗi tấn DAP cần khoảng 0,40-0,42 t S
  và khoảng 0,22 t NH3. Ở S CFR khoảng 900 và NH3 khoảng 600: S+NH3 ≈ 370 + 130 = **500 USD/t DAP**, chênh với DAP 800
  là khoảng **300**. Ở mức giữa 2025 (S khoảng 250, NH3 khoảng 450, DAP khoảng 715): khoảng 105 + 100 = 205, chênh
  khoảng **510**. **Biên nguyên liệu bị ép khoảng 200 USD/t (−40%)** dù DAP đang ở p97. Mỗi −100 USD/t lưu huỳnh CFR
  trả lại khoảng +40 USD/t DAP. Đây là minh hoạ. Người dùng phải thay bằng định mức và giá mua thật của DN.

## 4. Độ bền giá DAP (~800, p96-97 của 10 năm)
**Đánh giá: BỀN VỪA PHẢI tới hết Q1/2027, vùng 720-830. Đuôi xuống lớn hơn đuôi lên. Lực đỡ từ phía cung, lực trần từ
phía cầu.** [UĐ dựa trên DK]
- **Đỡ (cung):** TQ không xuất khẩu tới ít nhất khoảng T5/2027 theo kịch bản Argus. Ma'aden và OCP bị giới hạn bởi lưu
  huỳnh (OCP nhập khoảng 3,7 tr t/năm từ Gulf). Brazil đóng nhà máy MAP/SSP/TSP. Ấn Độ phải nhập cho rabi: tồn kho DAP
  đầu rabi 3,03 tr t (+9%) nhưng "phosphate kém thoải mái" (UkrAgroConsult 07/10). Tender IPL 1,7 tr t đang đóng (T10).
  CFR Ấn Độ khoảng 900 cao hơn WB/TE khoảng 100.
- **Trần (cầu):** affordability lân tệ nhất nhiều năm (Argus). DAP/urea ở **p97,5** của 10 năm, nên nông dân chuyển sang
  N, giảm P, hoặc hoãn bón. Argus dự báo tiêu thụ DAP/MAP/TSP 2026 **−13%** (CoBank). Urea đã giảm −52% từ đỉnh vì TQ
  vẫn xuất 6-7 tr t, nên không còn kéo DAP lên. Chi phí lưu huỳnh giảm làm hạ sàn chi phí của nhà sản xuất tích hợp.
  Argus T10 hạ mạnh dự báo DAP Ấn Độ so với T7 (giảm "có giới hạn"). StoneX phản biện: còn cao chừng nào Hormuz còn hạn
  chế. WB (14/05): DAP +6% năm 2026 và −10% năm 2027, rủi ro lệch lên nếu Hormuz kéo dài qua Q3/2026. Điều kiện đó
  **đã xảy ra**.
- **Mùa vụ [NỀN]:** Q4-Q1 là mùa thấp điểm của Bắc bán cầu. Cầu Ấn Độ đạt đỉnh rabi T10-T12. Mùa xuân Bắc Mỹ/TQ
  (T2-T4) có thể đỡ giá lại.
- **Tiền lệ:** sau khi TQ mở cửa sổ XK 2025, DAP WB đi từ 795 (T8/25) xuống 627 (T12/25), **−21% trong 4 tháng**. Đó là
  cường độ giảm khi một nguồn cung lớn quay lại. Kịch bản đó cần TQ nối lại XK sớm hoặc Hormuz mở thật.

## 5. Ba chỉ báo dẫn dắt (quan sát được) và chỉ báo phụ
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu A (bình thường hoá) ⇔ B (kéo dài) |
|---|---|---|---|
| 1 | **Hormuz: số tàu hàng rời và tàu phân bón/lưu huỳnh đi qua eo, phí war-risk, trạng thái đàm phán Mỹ–Iran** (tuần) | JMIC, Lloyd's List Intelligence (brief tuần), straits.live, Kpler | Thoả thuận + >60 lượt/ngày bền 4 tuần + phí bảo hiểm hạ ⇔ tấn công tàu tiếp diễn, <30 lượt/ngày |
| 2 | **Giá hợp đồng lưu huỳnh ME tháng (Qatar QSP/KPC/ADNOC) và chênh của nó với TE `sulfur` CNY, cộng tồn kho cảng lưu huỳnh TQ** (tháng/tuần) | SMM, Argus, Mysteel, BQ `sulfur` | QSP < 600 và chênh ME–TQ co lại, tồn kho cảng TQ tăng ⇔ QSP tăng lại > 900 hoặc TQ tái tích trữ T11-T12 kéo CNY > 7.000 |
| 3 | **Chính sách XK lân TQ (cửa sổ quota/kiểm hoá) và giá trúng tender DAP Ấn Độ (IPL/NFL CFR)** (sự kiện/tháng) | OilChem, Argus, S&P Global, Business Standard | TQ công bố cửa sổ trước T5/2027, CFR Ấn Độ < 800 ⇔ TQ gia hạn cấm qua Q2/2027, CFR > 950 |
| phụ | NH3 Tampa tháng + khí TTF ngày | Qcintel/Argus; BQ `eu_natural_gas` | TTF < 50 ⇔ > 100 |
| phụ | Cầu lưu huỳnh HPAL Indonesia (NK, dự án thu hồi S) | Argus, BC Insight | — (nền cấu trúc) |

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-10-28, chấm theo quan sát cuối cùng ≤ ngày kiểm)
**Proxy chấm điểm chính:** BQ `tav2_bq.commodity_prices`, `source='trading_economics'`, `cadence='daily'`:
`sulfur` (CNY/t, giá nội địa TQ; **không phải** ME FOB) và `di_ammonium` (USD/t). **Proxy phụ:** giá hợp đồng tháng
Qatar QSP FOB (USD/t, SMM/Argus) và WB `dap` tháng (US Gulf). Mốc gốc: TE sulfur **5.714** (23/10), Qatar T10 **835**,
TE DAP **802,5** (23/10), WB DAP **800,6** (T9).

Ba kịch bản đứng sau phân phối [UĐ]:
- **K1, Hormuz còn tranh chấp/đóng phần lớn tới hết Q1/2027 (p ≈ 0,55):** huỷ cầu tiếp tục, có thể bật lại khi TQ tái
  tích trữ T11-T12. TE 4.500-6.200, QSP 650-800.
- **K2, thoả thuận thật trước giữa T1/2027 (p ≈ 0,30):** lưu huỳnh mắc kẹt bị xả và lặp lại mẫu 2022. TE 3.000-4.200,
  QSP 400-600.
- **K3, leo thang (Brent > 125, đánh vào hạ tầng Gulf) (p ≈ 0,15):** TE 6.500-9.000, QSP > 900.

| Mốc | Chuỗi | Dự báo |
|---|---|---|
| **2027-01-31** | TE `sulfur` CNY/t | Trung vị **khoảng 4.900**, khoảng 80% **3.400-6.800**. **P(<5.714) = 0,65**; P(<4.000) = 0,25; P(>7.000) = 0,10 |
| | Qatar QSP T1/2027 (phụ) | Trung vị khoảng 650; P(<835) = 0,75; P(<600) = 0,40 |
| **2027-04-30** | TE `sulfur` CNY/t | Trung vị **khoảng 4.400**, khoảng 80% **2.800-7.000**. **P(<5.714) = 0,68**; P(<4.000) = 0,40; P(>7.000) = 0,12 |
| | Qatar QSP T4/2027 (phụ) | Trung vị khoảng 580; P(<835) = 0,75 |
| **2027-01-31** | TE `di_ammonium` USD/t | Trung vị **khoảng 770**, khoảng 80% **690-840**. **P(<802,5) = 0,60**; P(≤720) = 0,25; P(≥850) = 0,08 |
| | WB `dap` T1/2027 (phụ, công bố đầu T2) | Trung vị khoảng 765; P(<800,6) = 0,62 |
| **Câu phân loại** | TE `sulfur` ≤ 3.000 vào 2027-07-31 (tức A đúng) | P = **0,25** |

## 7. Điều gì làm tôi sai
1. **Thoả thuận Mỹ–Iran nhanh, và lưu huỳnh tồn đọng ở Gulf được xả.** Mẫu 2022 (−72%/2 tháng) cho thấy giá có thể về
   vùng trước chiến tranh trong 1 quý, khi đó A gần đúng về hướng. Lưu ý: kể cả lúc đó, mức trước chiến tranh vẫn
   ×1,5-4 so với 2023-24.
2. **Tôi đánh giá quá cao tầng cấu trúc.** Cầu HPAL Indonesia có thể chững lại (giá niken, dự án thu hồi S); TQ có thể
   tăng lưu huỳnh từ lọc dầu và axit pyrite. Khi đó "bình thường mới" thấp hơn 3.000 sớm hơn tôi nghĩ.
3. **Proxy TE không phải giá vốn VN.** Nếu nhà NK VN mua theo hợp đồng dài hạn có giá trễ, chi phí thực hiện trong
   BCTC sẽ trễ 1-2 quý so với cả TE lẫn ME. Đây là rủi ro đọc sai **thời điểm**, không phải sai hướng.
4. **DAP:** TQ mở cửa sổ XK sớm (trước T5/2027), hoặc Ấn Độ hoãn tender vì tồn kho +9%, sẽ đẩy giảm mạnh hơn khoảng 80%
   dưới (mẫu −21%/4 tháng của 2025). Ngược lại, OCP/Ma'aden cắt sản lượng sâu hơn vì thiếu S, cộng với cầu vụ xuân,
   có thể giữ DAP > 850.
5. **NH3/khí:** TTF tăng +63% trong 11 tuần chưa có dấu hiệu dừng. NH3 có thể lấy lại phần biên mà lưu huỳnh trả lại,
   đặc biệt với nhà sản xuất NK NH3.
6. **Báo giá TE `di_ammonium` dính:** basis chưa rõ, có thể là báo giá danh nghĩa. Forecast DAP có thể "đúng do chuỗi
   không nhúc nhích" chứ không do thị trường thật. Vì vậy chấm kèm WB.

Chấm điểm: Mike/Bobby đọc BQ (`source` chỉ định rõ) tại 3 mốc và ghi Brier dưới mục 6. **Đây không phải khuyến nghị
mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (TE daily, WB monthly), truy vấn ngày 28/10/2026. Phân vị tự tính: DAP WB 96,7% trên
  120 tháng; DAP/urea 97,5%.
- SMM, "Middle East October sulfur contract prices announced", 08/10/2026: https://news.metal.com/newscontent/104145450-smm-flash-middle-east-october-sulfur-contract-prices-announced
- SunSirs/Securities Daily, "China Industrial Sulfur: Price Surge and Correction", 20/10/2026: https://www.sunsirs.com/uk/detail_news-36937.html
- UkrAgroConsult, "China's phosphate fertilizer exports collapse to near zero", 16/10/2026: https://ukragroconsult.com/en/news/chinas-phosphate-fertilizer-exports-collapse-to-near-zero-worsening-global-supply-shortages/ ; "Record fertilizer stocks…", khoảng 07/10/2026: https://ukragroconsult.com/en/news/record-fertilizer-stocks-could-strengthen-indias-position-in-import-tenders/
- OilChem, "China implements sweeping fertilizer export ban", 27/03/2026: https://en.oilchem.net/26-0327-08-7290702267412555.html
- EnterpriseAM, "Hormuz's crude recovery hides a slower one for LNG, fertilizer…", 06/10/2026: https://enterpriseam.com/logistics/2026/10/07/hormuzs-crude-recovery-hides-a-slower-one-for-lng-fertilizer-helium-and-aluminum/
- Wikipedia, "2026 Strait of Hormuz crisis" (timeline tới 21/10/2026, Kpler): https://en.wikipedia.org/wiki/2026_Strait_of_Hormuz_crisis
- straits.live brief 27/10/2026: https://straits.live/briefs/2026-10-27 ; Lloyd's List Intelligence brief 22/10/2026: https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-22-october-2026 ; CNBC 09/10 và 14/10/2026: https://www.cnbc.com/2026/10/09/iran-war-strait-hormuz-tanker-attack-oil.html , https://www.cnbc.com/2026/10/14/container-ship-sinks-strait-hormuz-as-iran-war-attacks.html ; gCaptain (tàu dầu bị vô hiệu hoá 23/10): https://gcaptain.com/tanker-disabled-in-strait-of-hormuz-attack-another-vessel-reported-on-fire-in-persian-gulf/
- CBS News live (Araghchi 19/10, đàm phán đình trệ): https://www.cbsnews.com/live-updates/iran-war-us-trump-talks-russia-strait-of-hormuz/
- World Fertilizer, "Maaden exports DAP via Oman", 21/08/2026: https://www.worldfertilizer.com/phosphates/21082026/maaden-exports-dap-via-oman/ ; AGBI, 05/2026: https://www.agbi.com/analysis/industry/2026/05/iran-war-tests-thriving-saudi-phosphate-industry/
- World Bank Blog (CMO 04/2026), 14/05/2026: https://blogs.worldbank.org/en/opendata/fertilizer-prices-surge-as-strait-of-hormuz-disruptions-tighten-
- Producer.com, "Analysts disagree on where phosphate fertilizer prices are heading" (Argus và StoneX, T10/2026; chỉ đọc qua tóm tắt tìm kiếm vì trang trả 403): https://www.producer.com/markets/analysts-disagree-on-whats-next-for-phosphate-fertilizer-prices/
- CoBank, "Why higher fertilizer prices are here to stay" (chỉ tóm tắt): https://www.cobank.com/knowledge-exchange/why-higher-fertilizer-prices-are-here-to-stay
- SCMP, "China's sulphur imports dive 65%…", T9/2026 (chỉ tóm tắt tìm kiếm, 403): https://www.scmp.com/economy/article/3368654/chinas-sulphur-imports-dive-65-prices-surge-35-times-amid-middle-east-disruption
- Business Standard, IPL tender DAP kỷ lục, 12/05/2026: https://www.business-standard.com/economy/news/india-set-for-record-dap-import-in-single-tender-amid-supply-fears-126051201682_1.html
- BC Insight, *Sulphur* 422 "The sulphur market in deficit", 28/01/2026 (chỉ đọc tiêu đề) + mục Vale–Huayou Pomalaa 07/10/2026: https://www.bcinsight.crugroup.com/2026/01/28/the-sulphur-market-in-deficit/
- Argus, "China's sulphur prices set to cool", 02/12/2024 (cơ sở HPAL/tồn kho cảng): https://www.argusmedia.com/en/news-and-insights/latest-market-news/2634266-china-s-sulphur-prices-set-to-cool
- Qcintel (Tampa NH3, các tiêu đề 2026): https://www.qcintel.com/ammonia/article/tampa-ammonia-price-flat-at-560-mt-for-november-31314.html ; ICIS ammonia: https://www.icis.com/explore/commodities/fertilizers/ammonia/
- 24hmoney (tiền lệ lưu huỳnh 589→253 USD, khả năng 2022, năm chưa xác nhận): https://24hmoney.vn/news/gia-ure-luu-huynh-dong-loat-giam-c25a1511181


---
## ADDENDUM 29/10/2026 (Mike) — đính chính nguồn dữ liệu, KHÔNG sửa FORECAST/phân loại ở trên
Dòng "BQ không có NH3" (mục Dữ liệu, bẫy 3) **hết đúng từ 28/10 16:xx ICT**: BQ có `liquid_ammonia` (sunsirs, CNY/t, **NH3 nội địa Trung Quốc**, 2018→). Đã đối chiếu trang sunsirs, khớp. Chi tiết + bẫy: `kb/data_registry/feeds/bq_commodity_prices.md` § NH3.
Hệ quả cho bản đọc này: chuỗi mới KHÔNG phải Tampa/CFR nên **cột NH3 nhập khẩu vẫn từ web**; NH3 TQ ~2.734 CNY/t (10/2026) chỉ ≈ +22% YoY và +11% so TB 26Q3, **không tái hiện cú sốc Gulf/TTF** mà bản đọc dựa vào. Trigger phụ "NH3 Tampa" của FORECAST vẫn chấm bằng Tampa (web), không bằng chuỗi BQ.
