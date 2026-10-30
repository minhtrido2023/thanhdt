---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-30. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp đá xây dựng cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành khai thác và chế biến đá xây dựng (đá 1x2, đá mi, 0x4/cấp phối, đá hộc) vùng Đông Nam Bộ (Đồng Nai mới gồm Bình Phước cũ; TP.HCM mới gồm Bình Dương và Bà Rịa-Vũng Tàu cũ; Tây Ninh mới). Gồm pipeline cầu 2026-2029, cung và cấu trúc cạnh tranh, giá và chi phí, phân loại chế độ ngành, FORECAST khoá trước, checklist DD.
as_of: 2026-10-30 (tin web ≤ 2026-10-15; BQ commodity_prices truy vấn 30/10)
---

# SECTOR READ: Đá xây dựng Đông Nam Bộ, as-of 30/10/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này (có thể sai, không
dùng làm số pin). Số nào không đo được trực tiếp thì ghi **(ước lượng)**.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc:** mẫu định dạng `sector_read_vlxd_nhe_aac_20261029.md` (lấy luôn nền nhà ở và đầu tư công của file đó),
  `sector_read_oil_gas_shipping_20261029.md` (chỉ nền giá dầu). Không đọc `kb/projects/*`, `agents/Taylor/*`.
- **Không tra:** mã, giá cổ phiếu, BCTC, khuyến nghị CTCK của bất kỳ DN đá nào. Không truy vấn `ticker_financial`.
- **Ghi chú trung thực (web lộ thông tin cấp DN):**
  (a) Snippet tìm kiếm lộ tên và mã của **khoảng 5 DN khai thác đá niêm yết** (Đồng Nai, Bình Dương cũ, Bình Phước cũ) và tên
  vài mỏ của họ. Tôi KHÔNG mở báo cáo CTCK nào về các DN này. Có tải 2 báo cáo ngành CTCK năm 2023 nhưng **không trích được chữ**
  (máy không có thư viện PDF), nên không dùng.
  (b) Một snippet tóm tắt báo cáo CTCK Q2/2026 về **một DN đá ở Đồng Nai** nói sản lượng tiêu thụ 2026 của DN đó dự báo
  khoảng −12,8% YoY vì các dự án hạ tầng lớn phía Nam đang hoàn thiện. Đây là số **cấp DN**, có khả năng làm lệch cách đọc. Tôi
  **không dùng nó làm bằng chứng** cho pha chu kỳ (mục 4 dựa vào tiến độ dự án có nguồn riêng). Ghi lại để người đọc biết nó có mặt.
- **Chi phí vốn VN:** lượt này không đọc mới, nên không lấp bảng 5 tầng. Bối cảnh: REGIME READ #2 (13/10) và MACRO UPDATE
  (14/10) trong `vn_macro_regime_history.md`.
- **Khoảng trống dữ liệu lớn nhất:** (1) **không có chuỗi giá đá chính thức theo tháng** 2020→nay. Bảng công bố giá của Sở XD
  Đồng Nai (CB 1443/SXD 02/06/2026, CV 3254/SXD tháng 6/2026) có tồn tại, nhưng trang mirror trả 403. (2) Không có tổng sản lượng
  hay tổng công suất đá toàn vùng ĐNB từ nguồn chính thức. (3) Không có kết quả đấu giá mỏ đá nào ở ĐNB kèm giá trúng. BQ không
  có chuỗi giá VLXD/đá nào (báo, không tự sửa).

## 1. Pipeline cầu 2026-2029

**Cơ cấu cầu [NỀN]:** khoảng >70% cầu đá đến từ hạ tầng và công nghiệp, khoảng 30% từ dân dụng (dẫn MBS 2019 qua snippet,
không rõ vùng). Đá 1x2 chủ yếu vào bê tông (thương phẩm và cấu kiện). 0x4/cấp phối và đá hộc vào nền đường và san lấp. Đá mi
ngày càng thay cát (cát sông thiếu). **Thị trường đá theo vùng**, bán kính kinh tế chở bằng đường bộ khoảng 50-80 km [NỀN].
Ngoài bán kính đó, giá giao tới công trình tăng nhanh theo cước. ĐBSCL gần như không có đá, nên kéo hàng từ ĐNB bằng sà lan [NỀN].

| Kênh / dự án | Số liệu as-of [DK] | Đọc |
|---|---|---|
| **Dự án trọng điểm 2025** | Đồng Nai (08/03/2025): Long Thành + Vành đai 3 cần **>6,4 tr m³** đá. Dự án trọng điểm phía Nam đăng ký với tỉnh cho 2025 **>10 tr m³** (KTSG). Bộ XD (qua snippet tìm kiếm, không mở bài gốc): riêng 2025, Long Thành + cao tốc Biên Hòa–Vũng Tàu + VĐ3 cần **>10 tr m³**, Long Thành thiếu khoảng 4,7 tr m³, BH–VT thiếu khoảng 1,2 tr m³. Đăng ký 2025 (21/05/2025): Long Thành khoảng 5,0 tr m³, Sóc Trăng 0,84, hạ tầng TP.HCM 0,75+, đường HCM 0,5 | **Đỉnh cầu dự án là 2025-H1/2026.** Cung hụt so với cầu dù công suất danh nghĩa đủ, nên đây là năm giá tăng mạnh nhất |
| **Dự án trọng điểm 2026** | Đồng Nai (KTSG/TTXVN 25/03/2026): dự án trọng điểm phía Nam cần **khoảng 15 tr m³ đá năm 2026**; tỉnh đã cấp **gần 9 tr m³** ("năm nay", văn bản không rõ là 2025 hay kế hoạch 2026). Nhu cầu Long Thành, BH–VT, VĐ3 **"cơ bản đáp ứng"**. Các bên đang xin đá: TP.HCM, Cần Thơ, Tây Ninh, BQL đường HCM, Binh đoàn 12. Báo Đấu thầu (29/10/2025): ĐNB H2/2025-2026 khoảng **4,6 tr m³** cho cao tốc TP.HCM–Thủ Dầu Một–Chơn Thành, Gò Dầu–Xa Mát, TP.HCM–Mộc Bài; ĐBSCL khoảng **8,5 tr m³** H2/2025-2030; An Giang khoảng **5 tr m³** cho 21 công trình APEC 2027 ở Phú Quốc | Cầu dự án 2026 vẫn cao, nhưng **dịch chuyển**: từ Long Thành/VĐ3 (gần mỏ Biên Hòa) sang cao tốc hướng Tây Bắc (Bình Dương cũ, Tây Ninh) và ĐBSCL (xa, cần sà lan) |
| **Sân bay Long Thành GĐ1** | Mục tiêu chuyến bay thương mại đầu tiên **01/12/2026**, 3 đợt vận hành thử T9-T11 (KTSG 18-20/07/2026). Tờ trình 747/CP-TTr: lùi hạn hoàn thành tới **31/12/2026** | Khách hàng đá lớn nhất 2025 **rút dần** từ H2/2026. GĐ2 chưa có lịch thi công [NỀN] |
| **Vành đai 3 TP.HCM** (76,3 km) | Mục tiêu thông xe toàn tuyến cao tốc 30/04/2026; hoàn thành cả dự án (gồm đường song hành) **30/06/2026**. Không tìm thấy tin xác nhận đã đạt | Đã qua đỉnh tiêu thụ đá. Cầu đá dự án VĐ3 ước khoảng 2,3-3,1 tr m³ (2 nguồn khác thời điểm) ⇒ **khoảng 30-40 nghìn m³/km** (ước lượng, dùng làm hệ số quy đổi) |
| **Vành đai 4 TP.HCM** (khoảng 207 km, GĐ1 khoảng 120.412 tỷ) | Đoạn Bình Dương cũ khởi công 06/2025. Gói 2-2 qua Đồng Nai (>46 km, >16.000 tỷ) khởi công khoảng **30/09/2026** (Tuổi Trẻ). Tây Ninh khởi động gói 2-4, 2-5 (78,3 km) ngày **15/10/2026**. Mục tiêu hoàn thành **cuối 2028**. Lùi mốc khởi công nhiều lần (19/05 → 02/09 → T9-T10) | **Làn sóng cầu kế tiếp.** Áp hệ số VĐ3: 207 km × 30-40 nghìn m³/km ≈ **6-8 tr m³** trong 2026-2028 (ước lượng), đỉnh tiêu thụ khoảng 2027-H1/2028 [UĐ]. Rủi ro trượt tiến độ do GPMB là cao (đã lùi nhiều lần) |
| **Hạ tầng khác** | Metro TP.HCM (mạng lưới mới), cầu/cảng Cần Giờ, mở rộng cao tốc TP.HCM–Long Thành (mục tiêu 2026), đường kết nối Long Thành, QL51 trên cao [NỀN và DK rời rạc, không có khối lượng] | Có thật, nhưng không có số đá. Không cộng vào ước lượng |
| **Nhà ở / dân dụng** | (Từ file AAC 29/10) DKRA TP.HCM Q3/2026: tiêu thụ căn hộ sơ cấp **3.471 (−66% QoQ)**; tồn kho cả nước 51.950 tăng QoQ. Đầu tư công giải ngân **64,6%** KH tới 15/10/2026 | Kênh dân dụng **yếu dần sang 2027-2028** (đợt mở bán đã gãy Q3). Bê tông thương phẩm cho nhà ở là nguồn cầu 1x2 ổn định nhất, nhưng đang chậm lại [UĐ] |

**Ước lượng cầu đá cho dự án trọng điểm** (nguồn chính thức không có tổng; đây là ước lượng của Bobby, độ tin cậy THẤP):

| Năm | Cầu dự án trọng điểm ĐNB + phần ĐBSCL lấy từ ĐNB (tr m³) | Cơ sở |
|---|---|---|
| 2025 | >10 (thực cấp có thể khoảng 8-10) | DK: đăng ký >10; cung bị nghẽn |
| 2026 | khoảng 10-15 (ước lượng) | DK "khoảng 15" là cầu đăng ký. H2 Long Thành/VĐ3 rút |
| 2027 | khoảng 7-11 (ước lượng) | VĐ4 khoảng 2,5-3,5/năm + 3 cao tốc Tây Bắc + ĐBSCL khoảng 1,5-2/năm + APEC Phú Quốc. **Khoảng trũng** so với 2025-26 [UĐ] |
| 2028 | khoảng 8-12 (ước lượng) | VĐ4 về đích + có thể Long Thành GĐ2/metro. Rủi ro lớn hai chiều |
| 2029 | không đủ cơ sở | Phụ thuộc kế hoạch ĐTC trung hạn 2026-2030 (không đọc trong lượt này) |

Tổng cầu đá toàn vùng (gồm dân dụng, công nghiệp, bê tông thương phẩm) **không có nguồn**. Ước lượng thô **khoảng 35-50 tr
m³/năm** (ước lượng, độ tin cậy rất thấp; suy từ công suất thiết kế Đồng Nai >20 tr m³ và Bình Dương cũ 19 GP còn hiệu lực).
Không dùng số này làm pin.

## 2. Cung và cấu trúc cạnh tranh

**Mỏ đang khai thác [DK]:**
- **Đồng Nai** (trước sáp nhập): **32 mỏ có giấy phép**, tổng trữ lượng gần 400 tr m³, **còn lại khoảng 265 tr m³**; công suất thiết
  kế **>20 tr m³/năm** (KTSG 21/05/2025; KTSG 08/03/2025). Đồng Nai sau sáp nhập: **30 mỏ đá đang hoạt động**, trữ lượng còn
  khoảng 265 tr m³, "lớn nhất cả nước" (KTSG/TTXVN 25/03/2026). Trữ lượng/công suất ≈ **13 năm** ở công suất thiết kế (ước lượng).
- **Bình Dương cũ**: 22 mỏ đá có GP, **19 còn hiệu lực** (Sở TN&MT, qua snippet, ngày không rõ). Mỏ Tân Đông Hiệp (gần đô thị) hết
  hạn cuối 2017, gia hạn tới cuối 2019 rồi đóng cửa cải tạo (tin 2018-2020). Thời điểm đóng thật chưa xác nhận.
- **Bình Phước cũ, Bà Rịa-VT cũ, Tây Ninh**: có mỏ nhưng không có số trong lượt này.

**Nút thắt thật là pháp lý đất, không phải trữ lượng [DK]:** KTSG 08/03/2025: một số khu vực mỏ đã thoả thuận bồi thường với
dân nhưng **chưa xong thủ tục thuê đất** nên **phải dừng**. Cụm **Phước Tân–Tam Phước (Biên Hòa, gần TP.HCM và Long Thành nhất)**
chỉ khai thác được **khoảng 2 tr m³** tới hết 2025, so với nhu cầu Long Thành + VĐ3 là 6,4 tr m³. Tỉnh xin cho khai thác tạm phần
đã GPMB nhưng chưa thuê đất tới hết 12/2025. Nếu được thì cung khoảng 9,6 tr m³, **vẫn thiếu**. Mỏ không nâng được 50% công suất
theo cơ chế đặc thù vì Long Thành **không nằm trong danh mục**. Báo Đấu thầu (08/09/2025): **đình chỉ hàng loạt** do GP hết hạn
và nguy cơ sạt lở. Cùng lúc, có nguồn nói công suất Đồng Nai >20 tr m³ còn cầu dự án chỉ >7 tr m³ nên "không thể gọi là thiếu".
⇒ Thiếu là **thiếu cục bộ theo vị trí và pháp lý**, không phải thiếu tài nguyên [UĐ].

**Mỏ mới đấu giá [DK]:**
- QĐ 971/QĐ-UBND Đồng Nai: kế hoạch đấu giá 2026 gồm **16 khu vực, 464,55 ha: 13 mỏ đá xây dựng**, 1 cát, 2 đất san lấp, phần
  lớn ở **phía Bắc Đồng Nai** (KTSG 25/03/2026). Dự kiến trước đó 19 khu vực, 565 ha (VnEconomy 13/01/2026).
- Ví dụ: **Gia Canh** (Định Quán) 46,61 ha, **15,30 tr m³**, tổng vốn đầu tư 244,8 tỷ, đặt trước 11,325 tỷ. **Đồng Tâm 1** 18,76
  ha, 2,63 tr m³ đá + 1,31 tr m³ đất, đặt trước 2,919 tỷ. Cả hai **giá khởi điểm R = 3%**, bước giá 5% (Báo Đấu thầu 22/05/2026).
  Đăk Ơ (Bình Phước cũ) 4,6 ha, 0,574 tr m³. **Chưa thấy kết quả trúng giá nào ở ĐNB.**
- **Hệ quả địa lý [UĐ]:** cụm mỏ gần TP.HCM (Tân Đông Hiệp, Phước Tân–Tam Phước) đang **cạn hoặc vướng pháp lý**, còn cung mới
  nằm ở Định Quán (khoảng 100-120 km tới TP.HCM, ước lượng) và Bình Phước cũ (xa hơn). ⇒ **giá giao tới công trình tăng mang tính
  cấu trúc**, và mỏ gần đô thị còn GP hợp lệ có **tô khan hiếm vị trí**.
- **Độ trễ đấu giá → sản xuất [NỀN]:** thăm dò, phê duyệt trữ lượng, ĐTM, thuê đất, cấp phép, rồi xây dựng cơ bản mỏ. Thường
  **2-4 năm**. Báo Đấu thầu 15/05/2026: DN trúng đấu giá cát/sỏi **chậm hoàn tất thủ tục**. ⇒ Mỏ đấu giá 2026 hầu như **không ra
  hàng trước 2028** [UĐ].

**Luật và van xả cung [DK]:**
- Luật ĐC&KS 2024 có hiệu lực 01/07/2025; NĐ 193/2025/NĐ-CP hiệu lực **02/07/2025**.
- **Luật 147/2025/QH15** (thông qua 11/12/2025): rút thời gian ưu tiên nộp hồ sơ khai thác nhóm III từ 36 xuống **18 tháng**.
  **Chủ tịch UBND tỉnh được cấp GP khai thác nhóm III làm VLXD cho dự án quan trọng/cấp bách, cấp thẳng cho nhà thầu hoặc chủ đầu
  tư.** NQ 66.4/2025/NQ-CP (21/09/2025): cơ chế đặc thù khai thác nhóm III cho dự án đặc thù. Bộ NN&MT đang dự thảo sửa NĐ 193
  để mở rộng khu vực **không đấu giá** cho nhóm III phục vụ dự án trọng điểm (VCCI, chưa ban hành).
- ⇒ Với **phân khúc dự án nhà nước**, Nhà nước có thể vượt mặt mỏ thương mại (cấp mỏ cho nhà thầu). Đây là **trần hành chính lên
  sức mạnh định giá** của DN đá ở đúng phân khúc tăng nhanh nhất [UĐ].

**Kiểm soát giá và phân bổ hành chính [DK]:** Đồng Nai **phân bổ đá theo từng mỏ, từng nhà thầu** (CV 3605/UBND-KTN 03/04/2025;
4649 ngày 22/04/2025). CV 5137/UBND-KTN (05/2025) yêu cầu mỏ khai thác cả ngày lễ, ca đêm. Mỏ Tân Cang 6 có khoảng 0,45 tr m³ chưa
phân bổ thì bị **giao cho BQL dự án giao thông tỉnh**. **CV 2757/UBND-KTN (10/06/2026):** bình ổn giá VLXD, ưu tiên dự án trọng
điểm, buộc **niêm yết giá**, cấm găm hàng và tăng giá bất hợp lý, tăng kiểm tra. Bộ yêu cầu Sở CT và Sở XD Đồng Nai kiểm soát giá.

**Vận chuyển [DK + NỀN]:** Đá 1x2 tại mỏ khoảng 140-150 nghìn đ/tấn so với khoảng 380 nghìn đ/tấn tại TP.HCM ("nghịch lý giá đá",
**không rõ năm**, có lẽ ≤2020). Tháng 9/2025: tại mỏ miền Đông 1x2 **217.230 đ/m³**, còn giá sỉ TP.HCM 1x2 đen **305.000**, xanh
**465.000 đ/m³**. ⇒ cước + trung gian chiếm khoảng **30-60%** giá giao (ước lượng). ĐBSCL: giá giao công trình cao tốc từ
470-500 nghìn lên **550-600 nghìn đ/m³** từ đầu 08/2025. Đồng Tháp **thiếu đá diện rộng**, phải xin Đồng Nai. Đường HCM đoạn Kiên
Giang thiếu gần 0,5 tr m³.

**Sức mạnh định giá — tổng hợp [UĐ]:**
- **Cao** ở phân khúc bán lẻ/thương phẩm trong bán kính gần TP.HCM, nhờ mỏ gần cạn, cung mới ở xa, và trễ cấp phép 2-4 năm.
- **Bị khống chế** ở phân khúc dự án trọng điểm: phân bổ hành chính, CV bình ổn, cấp mỏ trực tiếp cho nhà thầu theo Luật 147.
- **Bị cước nuốt** ở thị trường xa (ĐBSCL): cước sà lan/xe và diesel ăn phần chênh.

## 3. Giá đá 2020→nay và chi phí

**Giá (mốc rời rạc, không phải chuỗi chính thức):**

| Thời điểm | Mốc | Nguồn |
|---|---|---|
| ≤2020 (không rõ năm) | 1x2 tại mỏ khoảng 140-150 nghìn đ/tấn; TP.HCM khoảng 380 nghìn đ/tấn | TNCK / Báo Đầu tư "Nghịch lý giá đá" (không ghi ngày) |
| 2022-2023 | **Không tìm được số.** 2022 có cú sốc diesel, 2023 BĐS đóng băng [NỀN] | khoảng trống |
| H2/2024 | Phía Nam bắt đầu thiếu cung, giá **tăng trở lại** | elibook (snippet, không rõ ngày) |
| Q2/2025 | Đá **+4,0 đến +7,9%** so với Q1/2025 và cuối 2024 | Bộ XD (qua snippet) |
| 06/2025 | Đá **+7,3 đến +11,11% MoM** | Viện KTXD, dẫn Báo Đấu thầu 08/09/2025 |
| 07/2025 | Tại mỏ miền Đông: 1x2 **217.230**, 0x4 132.000, hộc 152.000 đ/m³ | Báo Đấu thầu 08/09/2025 |
| 09/2025 | Sỉ TP.HCM: 1x2 đen 305.000 / xanh 465.000; 0x4 đen 255.000 / xanh 395.000; 4x6 đen 365.000 đ/m³ | Báo Đấu thầu 08/09/2025 |
| 2025 | "+10 đến +18% mỗi quý từ đầu năm" (phương pháp và vùng không rõ, độ tin cậy thấp) | snippet |
| cuối 2025→đầu 2026 | Một số VLXD **+25 đến +50%** (chủ yếu miền Trung, cát) | Báo Đấu thầu 15/05/2026 |
| khoảng đầu 2026 | Báo giá tại mỏ Đồng Nai cũ: 1x2 ly tâm **177.480 đ/tấn**, 13x25 181.850, 10x16 183.780; Bình Phước cũ: 1x2 **230-240 nghìn đ/tấn**. TP.HCM công bố 400-500 nghìn đ/m³, **có lúc giao dịch tới 1 triệu đ/m³** | Báo Đấu thầu 04/03/2026 (giá không ghi ngày) |
| Q2/2026 | "Từ đầu Q2/2026 giá nhiều VLXD tiếp tục tăng", đá và cát tăng cao | TS Thái Duy Sâm (TBTC) |
| Q3/2026 | Thị trường VLXD **ổn định** (thời tiết, giá đầu vào giảm); Q4 dự báo **tăng nhẹ** khi ĐTC giải ngân mạnh | TBTC "Dự báo giá VLXD quý IV tăng nhẹ" |

**Đọc giá [UĐ]:**
- 177.480 đ/tấn quy đổi ở 1,45-1,5 t/m³ ≈ **257-266 nghìn đ/m³** (ước lượng). Như vậy khoảng **+18 đến +22%** so với 217.230
  (07/2025), nhưng khác người bán và khác quy cách.
- So với mốc ≤2020 (140-150 nghìn đ/tấn), giá tại mỏ đầu 2026 cao khoảng **+20 đến +25%** danh nghĩa nếu so cùng đơn vị tấn. Giá
  giao tới TP.HCM thì tăng mạnh hơn nhiều (cước + khan hiếm) (ước lượng).
- **Mức hiện tại là đỉnh danh nghĩa trong các mốc tìm được**; không thấy mốc nào trước đó cao hơn. Đáy gần nhất **không đo
  được** (ứng viên là 2023, [NỀN]).
- **Hướng:** từ tăng nhanh (06/2025, +7-11% MoM) sang **đi ngang** (Q3/2026). **Mức:** giá công bố của Sở **thấp hơn giá giao
  dịch thật** (TP.HCM 400-500 nghìn so với có lúc 1 triệu; An Giang 380 nghìn so với 780-800 nghìn). Tức là số công bố bị neo
  hành chính, giống bài học lãi suất: **không đọc giá đá bằng một con số Sở công bố**.

**Chi phí [DK BQ + NỀN]:**
- **Diesel** (máy xúc, xe tải nội mỏ, và quan trọng hơn là cước giao hàng). BQ `tav2_bq.commodity_prices` (TE daily), trung bình
  tháng, truy vấn 30/10/2026:

  | Chuỗi | 10/2025 | 01-02/2026 | 03/2026 | 05/2026 | 07/2026 | 09/2026 | 10/2026 |
  |---|---|---|---|---|---|---|---|
  | Brent (USD/thùng) | 63,8 | 64,6-69,4 | 98,1 | 103,7 | 83,6 | 100,8 | **107,0** |
  | Heating oil (USD/gal, proxy diesel) | 2,3 | 2,3-2,5 | 3,9 | 3,9 | 3,8 | 4,8 | **4,8** |

  Heating oil **+109% YoY**. Diesel bán lẻ VN: tiêu đề báo 03/04/2026 nói "dầu trong nước chạm ngưỡng 40.000 đồng"; DO 0,05S
  ngày 27/07/2026 là **25.760-26.270 đ/lít**; kỳ 01/10/2026 diesel **−780 đ/lít**. Giá diesel bán lẻ T10 **không có số**.
- **Thuốc nổ:** do Nhà nước định giá/cung ứng tập trung [NỀN]; không có số 2026.
- **Thuế tài nguyên đá VLXD thông thường:** khoảng **7-10%** giá tính thuế, sàn là bảng giá tính thuế của UBND tỉnh [NỀN, chưa
  kiểm văn bản gốc]. **Phí BVMT** khoảng 5-7,5 nghìn đ/m³ [NỀN, chưa kiểm].
- **Tiền cấp quyền:** giá khởi điểm đấu giá Đồng Nai **R = 3%** [DK]. Nếu giá tính khoảng 200 nghìn đ/m³ thì R 3% ≈ **6 nghìn
  đ/m³ trữ lượng** (ước lượng). Ở tỉnh khác, mỏ đá trúng R = **4,5-5,1%** (Điện Biên 04/2026); mỏ cát trúng tới 63% [DK, 15/05/2026].
  Gánh nặng tiền cấp quyền **tăng theo cơ chế đấu giá**, nhưng với đá vẫn là phần nhỏ so với giá bán [UĐ].
- **Capex mỏ mới:** Gia Canh 244,8 tỷ / 15,3 tr m³ ≈ **16 nghìn đ/m³ trữ lượng** (ước lượng thô, chưa gồm tiền cấp quyền).
- **Cơ cấu giá vốn tại mỏ [NỀN, ước lượng]:** nhiên liệu + điện khoảng 15-25%; thuốc nổ khoảng 10-15%; thuế, phí và tiền cấp quyền
  khoảng 10-15% doanh thu; còn lại là khấu hao, nhân công, sửa chữa. Biên gộp DN đá có mỏ tốt thường cao [NỀN] ⇒ **một cú sốc
  diesel cắn vào cước giao hàng (bên mua chịu) nhiều hơn vào biên mỏ**, trừ khi DN tự vận chuyển.

## 4. Phân loại và pha chu kỳ

**Phân loại (xác suất chủ quan, cộng = 1):**

| Nhãn | P | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,45** | Cả hai phía đều do hành chính quyết. **Cung:** GP, thuê đất, đấu giá, đình chỉ, phân bổ theo mỏ/nhà thầu, Luật 147 cấp thẳng cho nhà thầu. **Cầu:** dự án trọng điểm, tiến độ GPMB. **Giá:** CV bình ổn, giá công bố bị neo. Đợt tăng giá 2025 có nguyên nhân gần nhất là **đình chỉ mỏ + nghẽn thuê đất**, không phải cạn tài nguyên |
| **CYCLICAL** | **0,35** | Cầu đi theo sóng dự án hạ tầng có ngày bắt đầu và kết thúc: Long Thành/VĐ3 rút, VĐ4 vào. Nhà ở đang quay xuống. Q3/2026 giá đi ngang |
| **STRUCTURAL** | **0,20** | Cụm mỏ gần TP.HCM cạn hoặc bị đô thị bao vây; cung mới ở xa 100+ km; đấu giá làm tăng chi phí vào ngành; trễ cấp phép 2-4 năm; cát sông cạn nên đá mi được thay vào. ⇒ **sàn giá giao tới TP.HCM dâng lên dài hạn**, độc lập với chu kỳ |

**Độ tin cậy: `ambiguous` khoảng 60/40.** Chỗ lẫn lớn nhất là tách "nghẽn pháp lý tạm thời" (ADMIN, gỡ được trong 6-18 tháng)
khỏi "cạn vị trí gần đô thị" (STRUCTURAL, không gỡ được). Cả hai đều cho ra cùng một triệu chứng: giá tăng và thiếu cục bộ.

**Pha chu kỳ hiện tại: ĐỈNH, chuyển sang bình nguyên** (giá đứng ở mức cao, khối lượng dự án sắp vào khoảng trũng 2027, chưa
phải pha suy rõ rệt).
- **Ủng hộ 1:** Hai khách hàng đá lớn nhất 2025 đang rút. Long Thành GĐ1 nhắm chuyến bay thương mại 01/12/2026. VĐ3 nhắm hoàn
  thành 30/06/2026. Đồng Nai (03/2026) nói nhu cầu Long Thành, BH–VT, VĐ3 đã "cơ bản đáp ứng".
- **Ủng hộ 2:** Đà giá chậm lại và van xả cung đã mở. Từ +7-11% MoM (06/2025) xuống "ổn định" Q3/2026. Luật 147 (12/2025) cho cấp
  mỏ thẳng cho nhà thầu. 13 mỏ đá vào kế hoạch đấu giá 2026. CV 2757 (06/2026) bình ổn giá.
- **Chống:** VĐ4 (207 km, khoảng 6-8 tr m³ ước lượng) mới khởi công các gói lớn 30/09 và 15/10/2026, đỉnh tiêu thụ 2027-H1/2028.
  ĐBSCL/APEC Phú Quốc còn thiếu đá. Diesel +109% YoY đẩy chi phí. ⇒ Có thể **không có khoảng trũng** mà là **đỉnh kéo dài tới 2028**.

**Điều kiện đổi phân loại:**
- **Sang STRUCTURAL ≥0,40** nếu tới giữa 2027 cụm Phước Tân–Tam Phước bị đóng hẳn hoặc không gia hạn VÀ giá 1x2 tại mỏ vẫn tăng dù
  khối lượng dự án giảm.
- **Sang CYCLICAL ≥0,50 (pha suy)** nếu VĐ4 trượt sang 2027 và giá công bố của Sở Q2/2027 giảm.

## 5. FORECAST khoá trước (30/10/2026, falsifiable)

| # | Chấm ngày | Biến (nguồn chấm) | Dự báo |
|---|---|---|---|
| F1 | 2027-01-31 | Long Thành GĐ1 có **chuyến bay thương mại đầu tiên** trước hoặc vào 31/12/2026 (ACV/Bộ XD) | **P = 0,65** |
| F2 | 2027-08-31 | Giá đá 1x2 trong công bố giá VLXD của Sở XD Đồng Nai, bình quân Q2/2027 so với bình quân Q3/2026, cùng quy cách, cùng điểm giao | Trong ±7%: **P = 0,55**; > +7%: P = 0,30; < −7%: P = 0,15 |
| F3 | 2027-05-31 | Báo cáo giá VLXD của Viện KTXD/Bộ XD: đá xây dựng khu vực phía Nam Q1/2027 **tăng** (>0%) so với Q4/2026 | **P = 0,55** |
| F4 | 2026-12-31 | Số mỏ đá xây dựng thuộc KH đấu giá 2026 của Đồng Nai (13 mỏ, QĐ 971) **đã có kết quả trúng đấu giá được công bố** | ≥5 mỏ: **P = 0,35** |
| F5 | 2027-06-30 | Như F4 | ≥5 mỏ: **P = 0,60** |
| F6 | 2027-06-30 | ≥1 mỏ đá **đấu giá năm 2025-2026** ở ĐNB được **cấp GP khai thác** | **P = 0,30** |
| F7 | 2027-03-31 | Nghị định sửa NĐ 193/2025 **mở rộng khu vực không đấu giá** cho nhóm III phục vụ dự án trọng điểm được **ban hành** | **P = 0,55** |
| F8 | 2027-06-30 | VĐ4 TP.HCM: BQL hoặc báo chính thống báo sản lượng xây lắp toàn tuyến **≥20%** giá trị | **P = 0,35** |
| F9 | 2027-04-15 | BQ `commodity_prices` heating_oil, trung bình tháng 03/2027 **< 4,0 USD/gal** | **P = 0,55** |
| F10 | 2027-02-15 | Giải ngân ĐTC cả năm 2026 (Bộ Tài chính, số tới 31/01/2027) **≥85%** KH TTg giao | **P = 0,50** |

**Cách chấm:** mỗi F đúng hoặc sai theo nguồn ghi trong cột. Nguồn không công bố được thì ghi "không chấm được", không suy.
**Không phải khuyến nghị mua/bán.**

## 6. DD cần kiểm gì cho một DN khai thác đá ĐNB

**A. Giấy phép và tài nguyên (quan trọng nhất)**
1. Danh sách **từng GP**: số GP, ngày cấp, **ngày hết hạn**, công suất cấp phép (m³/năm), **cote đáy** được phép.
2. **Trữ lượng còn lại thật** (cấp 121/122 so với 333 dự báo) chia cho sản lượng thực ⇒ số năm còn khai thác của từng mỏ.
   So với kế hoạch khấu hao.
3. **Thuê đất đã đủ cho toàn bộ diện tích khai thác chưa.** Đây là bẫy Phước Tân–Tam Phước 2025: đã bồi thường nhưng chưa
   thuê đất thì phải dừng.
4. Mở rộng hoặc khai thác xuống sâu: **có phải qua đấu giá theo Luật 2024 không**; tiến độ hồ sơ thăm dò; trễ dự kiến.
5. Lịch sử **xử phạt**: khai thác vượt công suất, vượt cote, ngoài ranh, đình chỉ do sạt lở. Mỗi lần đình chỉ là một quý mất
   sản lượng.
6. **Đô thị bao vây**: khoảng cách tới dân cư và quy hoạch tỉnh mới sau sáp nhập. Tiền lệ Tân Đông Hiệp là mỏ gần đô thị bị đóng.

**B. Kinh tế học vị trí**
7. Khoảng cách (km) từ mỏ tới TP.HCM, Long Thành, các gói VĐ4, trạm trộn lớn; có **bến thủy nội địa hoặc sà lan** ra ĐBSCL không.
8. **Ai trả cước**: giá xuất mỏ hay giá giao. DN tự vận chuyển thì chịu thẳng cú sốc diesel (+109% YoY proxy).
9. Cơ cấu sản phẩm: 1x2 / 0x4 / mi / hộc. **Đá mi thay cát** là động lực riêng (cát sông thiếu).

**C. Khách hàng, giá và tiền**
10. Tỷ trọng doanh thu **dự án trọng điểm** so với bê tông thương phẩm/đại lý; tỷ trọng **khách hàng top 5**.
11. Khối lượng có bị **tỉnh phân bổ hành chính** không, giá bán cho dự án trọng điểm có bị khống chế không (CV 3605/4649/2757).
12. **ASP thực** (doanh thu chia m³) theo quý so với giá công bố của Sở. Lệch lớn là dấu hiệu bán qua trung gian hoặc liên quan.
13. **Phải thu** từ nhà thầu dự án công: kỳ thu tiền, nợ quá hạn. Nhà thầu kẹt hợp đồng trọn gói khi giá vật liệu tăng
    (Báo Đấu thầu 15/05/2026), nên dễ chậm trả.
14. Sản lượng 2025 có bị **dồn sớm** (Long Thành/VĐ3) không: so sản lượng H2/2026 với H1/2026 để đo khoảng trũng.

**D. Chi phí và nghĩa vụ**
15. Tiền cấp quyền: **đã nộp hay còn phải nộp**, theo R nào, có **truy thu** khi điều chỉnh trữ lượng hay công suất không.
16. Thuế tài nguyên tính theo giá bán thật hay theo sàn bảng giá tỉnh; rủi ro truy thu thuế khi giá tăng.
17. **Ký quỹ cải tạo, phục hồi môi trường** và chi phí đóng cửa mỏ: đã trích lập đủ chưa.
18. Độ nhạy biên gộp với diesel, thuốc nổ, điện; có hợp đồng nhiên liệu hay pass-through giá không.

**E. Quản trị**
19. Cổ đông Nhà nước hoặc công ty mẹ: thoái vốn, **chuyển giá qua bán cho công ty liên quan**.
20. Tham gia đấu giá mỏ mới: mỏ nào, R trúng, nguồn tiền (Gia Canh cần **100% dự toán thăm dò bằng vốn chủ hoặc bảo lãnh**).
    Capex dự kiến khoảng 16 nghìn đ/m³ trữ lượng (ước lượng). Trúng đấu giá giá cao thì có thể hủy giá trị.
21. Tài sản ngoài mỏ (đất sau cải tạo, KCN, BĐS). Đây là nguồn giá trị **hoặc** nguồn rủi ro chuyển hướng vốn.

## 7. Chỉ báo theo dõi

| # | Chỉ báo | Nguồn | Ngưỡng đổi đọc |
|---|---|---|---|
| 1 | Giá 1x2 công bố của Sở XD Đồng Nai / TP.HCM (tháng) + giá giao dịch thật trên báo | Sở XD, Báo Đấu thầu | Q2/2027 lệch >±7% so với Q3/2026 |
| 2 | Kết quả đấu giá 13 mỏ đá Đồng Nai, R trúng | UBND, Sở NN&MT | R trúng >10% ⇒ chi phí vào ngành tăng mạnh |
| 3 | Tiến độ VĐ4 (gói khởi công, % sản lượng) | BQL, UBND TP.HCM / Đồng Nai / Tây Ninh | <20% tới 06/2027 ⇒ khoảng trũng sâu hơn |
| 4 | Giải ngân ĐTC (tuần) | Bộ Tài chính | |
| 5 | NĐ sửa NĐ 193 (không đấu giá cho dự án trọng điểm) | Chính phủ | Ban hành ⇒ trần định giá phân khúc dự án |
| 6 | Heating oil / diesel bán lẻ | BQ `commodity_prices`, BCT | |
| 7 | Tình trạng pháp lý cụm Phước Tân–Tam Phước | UBND Đồng Nai | Đóng hẳn ⇒ nâng STRUCTURAL |

## Nguồn (ngày đăng)
- KTSG 08/03/2025 "Đồng Nai muốn được nâng công suất khai thác đá lên 50%": https://tuoitre.vn/saigontimes/dong-nai-muon-duoc-nang-cong-suat-khai-thac-da-len-50/
- Nông nghiệp & Môi trường 03/05/2025 "Đồng Nai tăng thời gian khai thác đá…": https://nongnghiepmoitruong.vn/dong-nai-tang-thoi-gian-khai-thac-da-xay-dung-phuc-vu-du-an-trong-diem-d751187.html
- KTSG 21/05/2025 "Đồng Nai tìm thêm đá xây dựng…": https://tuoitre.vn/saigontimes/dong-nai-tim-them-da-xay-dung-cho-du-an-trong-diem-phia-nam/
- Báo Đấu thầu 08/09/2025 "Nhà thầu sốt ruột vì giá đá tăng nhanh": https://baodauthau.vn/nha-thau-sot-ruot-vi-gia-da-tang-nhanh-post184572.html
- Báo Đấu thầu 29/10/2025 "Động lực từ hạ tầng…ngành đá xây dựng": https://baodauthau.vn/dong-luc-tu-ha-tang-cu-hich-cho-ket-qua-kinh-doanh-nganh-da-xay-dung-post187604.html
- VnEconomy 13/01/2026 "Đồng Nai dự kiến đấu giá… 19 khu vực mỏ": https://vneconomy.vn/dong-nai-du-kien-dau-gia-quyen-khai-thac-khoang-san-19-khu-vuc-mo.htm
- Báo Đấu thầu 04/03/2026 "Giá vật liệu xây dựng vẫn là nỗi lo của nhà thầu": https://baodauthau.vn/gia-vat-lieu-xay-dung-van-la-noi-lo-cua-nha-thau-post194528.html
- KTSG/TTXVN 25/03/2026 "Đồng Nai đấu giá 16 mỏ khoáng sản": https://tuoitre.vn/saigontimes/dong-nai-dau-gia-16-mo-khoang-san/
- Báo Đấu thầu 15/05/2026 "Dồn dập đấu giá mỏ khoáng sản…": https://baodauthau.vn/don-dap-dau-gia-mo-khoang-san-giai-con-khat-vat-lieu-xay-dung-post198824.html
- Báo Đấu thầu 22/05/2026 "Sắp đấu giá mỏ đá Gia Canh 46,61 ha": https://baodauthau.vn/sap-dau-gia-mo-da-gia-canh-4661-ha-tai-dong-nai-post199259.html
- Báo Đấu thầu 22/05/2026 "Đồng Nai chuẩn bị đấu giá 18,76 ha mỏ đá Đồng Tâm 1": https://baodauthau.vn/dong-nai-chuan-bi-dau-gia-1876-ha-mo-da-xay-dung-dong-tam-1-post199261.html
- Doanh nghiệp Hội nhập 11/06/2026 "Đồng Nai siết quản lý VLXD…" (CV 2757/UBND-KTN 10/06/2026): https://doanhnghiephoinhap.vn/dong-nai-siet-quan-ly-vat-lieu-xay-dung-yeu-cau-rut-ngan-thu-tuc-cap-phep-cho-du-an-trong-diem-139625.html
- Thời báo Tài chính "Dự báo giá VLXD quý IV tăng nhẹ" (2026, ngày chưa xác nhận): https://thoibaotaichinhvietnam.vn/du-bao-gia-vat-lieu-xay-dung-quy-iv-tang-nhe-205146-205146.html
- Thời báo Tài chính "Giá VLXD tăng, ảnh hưởng tiến độ ĐTC" (Q2/2026): https://thoibaotaichinhvietnam.vn/gia-vat-lieu-xay-dung-tang-anh-huong-tien-do-dau-tu-cong-201544-201544.html
- Luật 147/2025/QH15 (11/12/2025), tóm tắt: https://luatvietnam.vn/linh-vuc-khac/diem-moi-luat-dia-chat-va-khoang-san-sua-doi-2025-883-106742-article.html ; VCCI về NĐ 193 / NQ 66.4: https://www.vcci.com.vn/tin-tuc/hoan-thien-chinh-sach-thao-go-vuong-mac-trong-trien-khai-luat-dia-chat-va-khoang-san
- Long Thành: KTSG ~18-20/07/2026 https://tuoitre.vn/saigontimes/nha-ga-san-bay-long-thanh-du-kien-hoan-thanh-cuoi-nam-2026/ (qua redirect thesaigontimes) ; Tờ trình 747/CP-TTr: https://vietnamfinance.vn/lui-thoi-han-hoan-thanh-dan-bay-long-thanh-den-cuoi-nam-2026-d119550.html
- VĐ3: SGGP "Dự án đường Vành đai 3 đảm bảo thông xe ngày 30-4-2026": https://www.sggp.org.vn/du-an-duong-vanh-dai-3-dam-bao-thong-xe-ngay-30-4-2026-post778392.html ; PLO "Hoàn thành toàn bộ dự án vành đai 3 vào tháng 6-2026": https://plo.vn/hoan-thanh-toan-bo-du-an-vanh-dai-3-vao-thang-6-2026-post805777.html
- VĐ4: Tuổi Trẻ (khởi công gói qua Đồng Nai, khoảng 30/09/2026; Tây Ninh 15/10/2026), qua snippet tìm kiếm, URL rút gọn không ổn định: https://tuoitre.vn/khoi-cong.html , https://tuoitre.vn/khoi-dong.html ; VnEconomy "Phấn đấu hoàn thành VĐ4 cuối 2028": https://vneconomy.vn/phan-dau-hoan-thanh-vanh-dai-4-tp-hcm-vao-cuoi-2028.htm
- Diesel: Báo Lào Cai 27/07/2026 https://baolaocai.vn/gia-xang-dau-hom-nay-2772026-dau-the-gioi-neo-cao-post904750.html ; BCT kỳ 01/10/2026 https://moit.gov.vn/tin-tuc/mot-so-thong-tin-dang-chu-y-ve-dieu-hanh-gia-xang-dau-ngay-1-10.html ; DNHN 03/04/2026 https://doanhnghiephoinhap.vn/gia-xang-dau-hom-nay-342026-dau-the-gioi-ap-sat-nguong-140-usd-dau-trong-nuoc-cham-nguong-40000-dong-131514.html
- "Nghịch lý giá đá xây dựng" (không ghi ngày): https://www.tinnhanhchungkhoan.vn/nghich-ly-gia-da-xay-dung-post172398.html
- BQ `tav2_bq.commodity_prices` (source=trading_economics, cadence=daily, metric_key brent/heating_oil), truy vấn 30/10/2026.
