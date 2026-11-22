---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, dispatch 2026-11-22 (thư mục DD của Taylor). KHÔNG biết mã, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về một DN đá cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
supersedes_in_part: sector_read_da_xay_dung_nam_bo_20261030.md (mục 3 "Q3/2026 ổn định", pha "đỉnh → bình nguyên", xác suất phân loại). Forecast F1-F10 của file 30/10 GIỮ NGUYÊN, chấm theo ngày của chúng (xem mục 5.1 về F1, F7 bị định nghĩa lỏng).
role: SECTOR READ ngành khai thác và cung cấp đá xây dựng thông thường (1x2, 4x6, hộc, mi, 0x4) vùng Đông Nam Bộ (Đồng Nai mới gồm Bình Phước cũ; TP.HCM mới gồm Bình Dương và Bà Rịa–Vũng Tàu cũ; Tây Ninh mới). Pipeline cầu 2026-2030, cấu trúc cạnh tranh và pháp lý mỏ (Luật ĐC&KS 2024, Luật 147/2025, NĐ 193/2025, NĐ 21/2026), phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED, FORECAST khoá trước, checklist DD.
as_of: 2026-11-22 (tin web ≤ 2026-11-17; macro snapshot TE as-of 2026-11-22; BQ commodity_prices tới 2026-11-20)
---

# SECTOR READ: Đá xây dựng Đông Nam Bộ, as-of 22/11/2026 (Bobby, real-time BLIND, bản cập nhật)

Không phải episode VNINDEX, không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày đăng; **[UĐ]** ước đoán/suy luận
của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (không dùng làm số pin). Số không đo trực tiếp ghi **(ước lượng)**.
"STRUCTURAL" trong file này là nghĩa NGÀNH (mất cân đối cung-cầu kéo dài nhiều năm, không tự hết theo chu kỳ dự án), KHÁC nghĩa
"Loại-1 STRUCTURAL" của sổ episode vĩ mô.

## 0. Kiểm toán blind
- **Đã đọc:** `macro_snapshot_2026-11-22.md` (file đầu vào), file 30/10 cùng ngành của chính Bobby (không chứa outcome), REGIME READ #3
  (10/11) trong `vn_macro_regime_history.md`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`,
  `data/cctg_rate_vn_tier2_events.csv`, log `refresh_deposit_cctg_weekly_2026-11.log`, BQ `tav2_bq.commodity_prices` (brent, heating_oil).
- **Không tra:** mã, giá cổ phiếu, BCTC, báo cáo CTCK của DN đá nào; không truy vấn `ticker`/`ticker_financial`.
- **Rò rỉ phải khai:** (a) tên thư mục dispatch chứa một mã 3 ký tự. Bobby KHÔNG tra mã đó và không dùng nó. (b) Snippet tìm kiếm lộ
  trang vietstock của 1 DN VLXD Đồng Nai và tên 1 DN BĐS ở Long An mua đá. Không mở, không dùng. (c) Một tin đấu giá khoản nợ 615 tỷ
  có tài sản bảo đảm là quyền khai thác 1 mỏ đá ở Đồng Nai (Báo Đấu thầu, post200025). Đây là tin cấp DN, chỉ ghi để người đọc biết nó có
  mặt, không dùng làm bằng chứng ngành.
- **Khoảng trống lớn nhất (vẫn như 30/10):** không có chuỗi giá đá chính thức theo tháng cho ĐNB; không có tổng sản lượng thực khai
  thác toàn vùng; không có kết quả trúng đấu giá mỏ đá nào ở ĐNB; GDP xây dựng trong snapshot STALE (145 ngày). Không mở được toàn văn
  NĐ 21/2026, Phụ lục III NĐ 193 (mức R), NQ 1084/2015 (thuế suất). Các số pháp lý dưới đây lấy qua tóm tắt báo/trang luật.

## 1. Pipeline cầu 2026-2030

**Bối cảnh vĩ mô (snapshot TE, as-of 22/11) [DK]:** GDP Q3 9,95% YoY; IIP T10 +15,0% YoY; PMI T10 52,3; FDI luỹ kế 10T
24,08 tỷ USD (+13% YoY); CPI T10 5,09% YoY; bán lẻ +14,7%. Tăng trưởng thật mạnh, cầu xây dựng nền không yếu. GDP xây dựng
không dùng được (STALE, định nghĩa gãy).

**Khung vốn [DK]:** NQ 27/2026/QH16 (24/04/2026) kế hoạch ĐTC trung hạn 2026-2030 **8,22 triệu tỷ** (TW 3,8 + ĐP 4,42), khoảng **2,7 lần**
giai đoạn trước; mục tiêu **≥5.000 km cao tốc** tới 2030; Thủ tướng yêu cầu **"chỉ bố trí vốn khi địa phương cam kết đủ vật liệu"**, tỉnh
phải xong quy hoạch mỏ vật liệu trong Q2/2026 (KTSG 06/05/2026). Giải ngân ĐTC 2026: **74,1%** KH TTg tới 31/10 (708,6/955,9 nghìn tỷ;
TW 59,6%), tạm ứng chưa thu hồi khoảng 240 nghìn tỷ (VietnamPlus, TBTCVN 11/2026).

| # | Dự án / kênh | Dữ kiện as-of [DK] | Cầu đá với ngành ĐNB | Độ chắc |
|---|---|---|---|---|
| 1 | **Long Thành GĐ1** | ACV: khai thác thương mại dự kiến **0h 24/12/2026**, 20-30 chuyến/ngày (VietnamPlus, CafeF 30-31/10/2026). >86% khối lượng; 12/16 gói chính còn thi công; thiếu khoảng 1.600 thợ (Stockbiz). Đã có chuyến bay "khai trương" 19/12/2025 (Nhân Dân, VnEconomy, chỉ qua tiêu đề) | **Đuôi** sang H1/2027 (hoàn thiện, đường nối). Khách lớn nhất 2025 đang rút | Cao (đang rút) |
| 2 | **Long Thành GĐ2** (đường băng 3, nhà ga 2) | ACV làm chủ đầu tư theo QĐ 26/QĐ-BXD 09/01/2026; đang lập quy hoạch chi tiết + BCNCKT. Mốc chính thức cũ 2028-2032; ACV từng đề xuất làm sớm đường băng 3 | 2028-2030, khối lượng lớn, **gần mỏ Biên Hòa/Long Thành** | Thấp-TB (thời điểm) |
| 3 | **Vành đai 3** | Còn cần khoảng **870 nghìn m³ đá** (Ban Giao thông TP.HCM, TBTCVN 30/10/2026) — chưa xong như mốc 30/06/2026 | Đuôi Q4/2026-H1/2027 | Cao |
| 4 | **Vành đai 4** (khoảng 207 km, 120.412 tỷ) | Gói lớn khởi công T9-T10/2026 (Đồng Nai 30/09, Tây Ninh 15/10 — file 30/10); Tây Ninh đã chi trả >93% diện tích; Đồng Nai thi công khó (Tiền Phong); mục tiêu 2028, có nguồn ghi 2029 | **Sóng chính 2027-2029**, khoảng 6-8 tr m³ (ước lượng, hệ số VĐ3 30-40 nghìn m³/km) | TB (có thật, dễ trượt) |
| 5 | **Cao tốc TP.HCM–Mộc Bài** | 2026 cần khoảng 380-500 nghìn m³ đá (TBTCVN 30/10; Tuổi Trẻ 25/06/2026: gần 5 tr m³ vật liệu, chủ yếu cát/đất) | 2026-2028 | TB-cao |
| 6 | **TP.HCM–TDM–Chơn Thành, Gò Dầu–Xa Mát** | ĐNB H2/2025-2026 khoảng 4,6 tr m³ cho 3 cao tốc hướng Tây Bắc (Báo Đấu thầu 29/10/2025) | 2026-2028 | TB |
| 7 | **Biên Hòa–Vũng Tàu** | TP1 khai thác tạm toàn tuyến 18/05/2026 (Tiền Phong, VOV); TP2/TP3 mốc 06/2026 chưa xác nhận | Đuôi | Cao (đang rút) |
| 8 | **Đường nối TP.HCM–Long Thành–Dầu Giây, nút An Phú, Mỹ Thủy** | Khởi công 11/2025, mục tiêu 12/2026 (tổng hợp tin TP.HCM 09/2026); "nhu cầu đáng kể", không có số (TBTCVN 30/10) | 2026-2027 | TB |
| 9 | **Metro / đường sắt đô thị** | Thủ Thiêm–Long Thành (khoảng 46,5 km), Bình Dương–Suối Tiên (khoảng 32 km) dự kiến khởi công cuối 2026; TDM–TP.HCM + metro 6 >260 nghìn tỷ; TP.HCM khởi công 14 công trình 466 nghìn tỷ trong 8T/2026 (VTC/CafeF 01/09/2026). HĐND 21-22/09 duyệt 5 dự án 61 nghìn tỷ nhưng 2026-27 chủ yếu chuẩn bị đầu tư | **1x2 cho bê tông**, 2027-2030+ | Thấp-TB (thời điểm) |
| 10 | **Cần Giờ** (khu đô thị lấn biển tư nhân, cầu/hầm Cần Giờ–Vũng Tàu, cảng trung chuyển) | TP.HCM cấp mỏ trực tiếp cho chủ đầu tư/nhà thầu dự án tư nhân trọng điểm gồm Cần Giờ; khoảng 17 công trình cần >362 tr m³ cho 4 loại vật liệu, không tách đá (NNMT 09/04/2026). Cầu/hầm: còn hồ sơ kỹ thuật | Phần lớn là cát/san lấp; đá chưa rõ | Thấp (phần đá) |
| 11 | **ĐBSCL + APEC Phú Quốc 2027** | ĐBSCL khoảng 8,5 tr m³ đá H2/2025-2030; An Giang khoảng 5 tr m³ cho APEC (Báo Đấu thầu 29/10/2025) | Kéo từ ĐNB bằng sà lan; cước nuốt phần lớn chênh | TB |
| 12 | **ĐSTĐC Bắc–Nam** | Bộ XD đặt mục tiêu khởi công **12/2027** (cổng Hà Tĩnh 09/09/2026); Q4/2026-Q4/2028 lập/duyệt BCNCKT | Đoạn phía Nam: sau 2028 | Thấp trong cửa sổ |
| 13 | **Nhà ở / dân dụng** | TP.HCM Q3/2026: tiêu thụ 3.471 căn (−66% QoQ, DKRA); nguồn cung DKRA 13.200 (−31% QoQ), CBRE 3.267 căn mới (−53% YoY), hấp thụ 45%; Q4 dự kiến 7-10 nghìn căn mới; CBRE cả năm khoảng 45 nghìn căn; giá sơ cấp khoảng 75 tr/m² (VOV, CafeF 10-11/2026) | Bê tông thương phẩm dân dụng **yếu 2026-2027**; NOXH là đệm | TB (hướng yếu) |
| 14 | **FDI / KCN / nhà xưởng** | FDI 10T +13% YoY; IIP +15% (snapshot). Thuế Mục 301 12,5% từ 24/07 (REGIME READ #3) | Nền ổn định, không phải động lực chính của đá | TB |

**Định lượng vùng (ước lượng, độ tin cậy THẤP):**
- **TP.HCM mới, năm 2026 [DK]:** công suất khai thác đá **23,66 tr m³**, cầu **28,16 tr m³**, **thiếu 4,5 tr m³** (Sở NN&MT, qua NNMT
  09/04/2026). Giải pháp: nâng công suất 11 mỏ ở BR–VT và Bình Dương cũ thêm >7 tr m³.
- **Đồng Nai [DK]:** công suất thiết kế >20 tr m³/năm, trữ lượng còn khoảng 265 tr m³ (file 30/10). Cầu dự án trọng điểm phía Nam đăng ký
  khoảng 15 tr m³ cho 2026 (KTSG/TTXVN 25/03/2026).
- **Hiệp hội VLXD (23/12/2025) [DK]:** riêng ĐTC TP.HCM 2026 cần khoảng **26 tr m³ đá**; cộng miền Đông và ĐBSCL thì "gần gấp đôi".
- ⇒ Cầu đá vùng (gồm phần chở ra ĐBSCL) khoảng **50-60 tr m³/năm**, công suất cấp phép vùng khoảng **45-50 tr m³/năm** (ước lượng).
  Thiếu khoảng 5-10 tr m³, **tập trung ở TP.HCM và ở vị trí/pháp lý**, không phải ở trữ lượng. File 30/10 ước tổng cầu 35-50 tr m³ là
  **thấp**: sửa lên.

| Năm | Cầu dự án trọng điểm + ĐTC lấy đá ĐNB (tr m³, ước lượng) | Đổi so với file 30/10 |
|---|---|---|
| 2026 | khoảng 12-16 (riêng phần dự án), trong tổng cầu vùng khoảng 50-60 | giữ |
| 2027 | khoảng 10-14 | **nâng** (từ 7-11): VĐ4 vào sóng chính, đuôi Long Thành/VĐ3, Mộc Bài, metro bắt đầu |
| 2028 | khoảng 10-15 | giữ-nâng: VĐ4 về đích, có thể Long Thành GĐ2 |
| 2029-2030 | không đủ cơ sở cho số; hướng **≥2027** nếu 8,22 triệu tỷ được giải ngân | mới |

## 2. Cung và cấu trúc cạnh tranh

**2.1 Số mỏ và giấy phép [DK]**
- **Đồng Nai cũ:** 32 mỏ đá có GP; **26 đang hoạt động, 5 hết hạn đang chờ gia hạn, 1 có GP chưa khai thác**; 26 mỏ vướng cấp/điều chỉnh
  GCN đăng ký đầu tư; chồng lấn quy hoạch xây dựng và thời hạn GP (qua snippet; ngày số liệu không rõ, nhiều khả năng 2025). Sau sáp
  nhập: 30 mỏ đá đang hoạt động (KTSG/TTXVN 25/03/2026).
- **Cụm Tam Phước–Phước Tân (Biên Hòa):** quy hoạch gần 400 ha, 10 mỏ; một phần diện tích đã bồi thường nhưng chưa xong thuê đất nên phải
  dừng; chỉ khai thác được gần 2 tr m³ tới cuối 2025; tư vấn đề xuất hạ cote từ −80 m xuống −120 m (MOC/KTSG, 2025, ngày không chắc).
- **Bình Dương cũ:** 19/22 GP còn hiệu lực (file 30/10); Thường Tân III, IV chịu áp lực cầu dồn (NNMT 09/04/2026).
- **Tây Ninh:** "chưa có nguồn đá đáp ứng đủ nhu cầu"; 68 GP khoáng sản (mọi loại) còn hiệu lực, trữ lượng khoảng 52 tr m³; **59 khu vực
  không đấu giá** khoảng 130,3 tr m³ (VOV 13/10/2026). Trong đó **2 khu đá** khoảng 20,3 tr m³ (Tân Hòa khoảng 15,5; Lộc Trung khoảng 4,8)
  phục vụ dự án trọng điểm (SGGP 24/04/2026). Tỉnh xin Chính phủ điều tiết khoảng 15,6 tr m³ vật liệu.
- **BR–VT cũ, Bình Phước cũ:** không có số mỏ trong lượt này.

**2.2 Địa lý và cự ly [DK + NỀN]**
- Đá là hàng **giá trị thấp, khối lượng lớn**. Bán kính kinh tế bằng đường bộ khoảng 50-80 km [NỀN]. Cước + trung gian khoảng 30-60% giá
  giao (ước lượng, file 30/10: tại mỏ 1x2 217 nghìn đ/m³ so với sỉ TP.HCM 305-465 nghìn, 2025).
- Cụm gần TP.HCM (Tân Đông Hiệp đã đóng; Tam Phước–Phước Tân vướng đất) suy yếu. Cung mới nằm ở Định Quán, Bình Phước cũ, Tây Ninh: xa
  hơn 100 km (ước lượng). **Mỏ gần đô thị còn GP hợp lệ có tô vị trí.**
- Mỏ ven sông Đồng Nai có bến sà lan ra ĐBSCL [NỀN]. Phân khúc ĐBSCL do cước quyết định.

**2.3 Rào cản gia nhập [DK + UĐ]**
1. **Đấu giá** quyền khai thác (Luật 2024): Đồng Nai kế hoạch 2026 có 13 mỏ đá (QĐ 971), giá khởi điểm R = 3%. **Tới 22/11/2026 chưa thấy
   kết quả trúng giá nào được công bố** (tìm kiếm 22/11).
2. **Đất:** đấu giá trước khi GPMB; doanh nghiệp bị đòi bồi thường **"gấp 5 đến 10 lần giá thị trường"**, trúng đấu giá rồi vẫn kẹt
   (Hiệp hội khoáng sản TP.HCM, Báo Đầu tư 23/12/2025).
3. **Trễ** đấu giá → thăm dò → ĐTM → thuê đất → GP → XDCB: 2-4 năm [NỀN]. Mỏ đấu giá 2026 khó ra hàng trước 2028 [UĐ].
4. **Vốn:** ví dụ Gia Canh 244,8 tỷ cho 15,3 tr m³ trữ lượng ≈ 16 nghìn đ/m³ (ước lượng, file 30/10), chưa gồm tiền cấp quyền và GPMB.
⇒ Rào cản với **người mới qua kênh thương mại là cao**. Nhưng Nhà nước đang mở **kênh hành chính** cho nhà thầu (2.4), và kênh này
không phải chịu đủ các rào cản trên.

**2.4 Chính sách cấp/gia hạn và các "van xả" hành chính [DK]**
- **Luật ĐC&KS 54/2024/QH15** hiệu lực 01/07/2025; **NĐ 193/2025/NĐ-CP** hiệu lực 02/07/2025. UBND tỉnh cấp phép thăm dò/khai thác nhóm III.
- **Luật 147/2025/QH15** (11/12/2025), hiệu lực **01/01/2026** (MOIT). Có văn bản hợp nhất 149/VBHN-VPQH (10/2026). Theo file 30/10: rút
  thời gian ưu tiên nộp hồ sơ nhóm III từ 36 xuống 18 tháng; Chủ tịch UBND tỉnh cấp GP nhóm III làm VLXD cho dự án quan trọng/cấp bách,
  cấp thẳng cho nhà thầu/chủ đầu tư. Lượt này KHÔNG kiểm lại được toàn văn; giữ nhãn [DK qua tóm tắt].
- **NĐ 21/2026/NĐ-CP (16/01/2026)** sửa NĐ 193, hiệu lực 16/01/2026 (Tạp chí Công Thương). (a) Điều 61: thêm điều kiện cấp GP nhóm III làm
  VLXD thông thường cho dự án theo Điều 55 Luật; hồ sơ rút gọn. (b) **Điều 63: cho cấp lại GP cả khi GP đã hết hạn nếu khu vực còn trữ
  lượng**, với điều kiện đã làm đủ nghĩa vụ và không bị truy cứu hình sự. (c) Mỏ nằm trên ≥2 tỉnh: tỉnh có phần lớn diện tích cấp phép.
  **⚠ File 30/10 bỏ sót văn bản này** và gọi việc sửa NĐ 193 là "dự thảo" (xem 5.1).
- **Khu vực không đấu giá:** VCCI vẫn kiến nghị mở rộng Điều 143 NĐ 193 cho nhóm III phục vụ dự án trọng điểm cấp tỉnh. Nhưng **tỉnh đã
  khoanh định khu không đấu giá trên thực tế** (Tây Ninh 52 → 59 khu, có 2 khu đá). ⇒ Kênh cung "không qua đấu giá" đã vận hành.
- **Nâng 50% công suất** theo NQ 168/NQ-CP và NQ 02/2025/NQ-CP: Đồng Nai có 14 mỏ đủ điều kiện, thêm khoảng 5 tr m³, nhưng **sản lượng tăng
  thêm chỉ được bán cho dự án chỉ định**. Số mỏ đã được duyệt không thống nhất giữa các nguồn (3/6/7/22). Nhiều mỏ "chưa chủ động hoàn
  thiện hồ sơ" (24hMoney, ngày không chắc). Long Thành ban đầu nằm ngoài danh mục.
- **Phân bổ hành chính:** Đồng Nai phân bổ đá tới từng nhà thầu/gói thầu; **tỉnh đã xin Thủ tướng cho thôi điều tiết tới từng nhà thầu
  trong năm 2026** (baomoi "Cơ bản đáp ứng vật liệu cho dự án trọng điểm"; chưa thấy trả lời). Tây Ninh lập Tổ điều phối VLXD (VOV
  13/10/2026). TP.HCM có kế hoạch điều phối vật liệu thông thường 2026 và 2027-2030 (SGGP).
- **Kiểm soát giá:** Ban Giao thông TP.HCM kiến nghị **"kiểm soát giá bán tại các mỏ"** phục vụ dự án trọng điểm (TBTCVN 30/10/2026). Đồng
  Nai có CV 2757/UBND-KTN 10/06/2026 bình ổn giá (file 30/10). Hà Nội yêu cầu ổn định giá VLXD, xác minh trường hợp tăng bất thường (DĐDN
  17/11/2026; khác vùng, nhưng là tín hiệu chính sách). Đại biểu QH đề xuất "quỹ VLXD" điều tiết giá cát, đá (KTSG 06/05/2026).

**2.5 Tiền cấp quyền và thuế, phí [DK + NỀN]**
- **NĐ 193 Điều 132:** T = Q × G × R. Q theo Điều 133, G theo Điều 134. **R theo Phụ lục III, khác nhau giữa khu đấu giá và không đấu giá.**
  Nộp hằng năm Thn = T / X (X là số năm nộp). **Điều 139: quyết toán theo sản lượng nguyên khai thực khai thác từng năm (SLi)**; phần trữ lượng
  chưa khai thác được duyệt lại; nộp thừa thì bù trừ (thuviennhadat 05/09/2025; hethongphapluat). ⇒ Mô hình mới gắn tiền cấp quyền với
  **sản lượng thực** nhiều hơn mô hình NĐ 67/2019 (thu theo trữ lượng cấp phép) [UĐ]. Hệ quả: rủi ro truy thu hoặc hoàn khi quyết toán.
- **Mức R cho đá VLXD:** không đọc được Phụ lục III. Giá khởi điểm đấu giá Đồng Nai là R = 3% [DK]. Mỏ đá tỉnh khác trúng 4,5-5,1%; mỏ cát
  trúng tới 63% [DK, Báo Đấu thầu 15/05/2026].
- **Phí BVMT:** NĐ 27/2023/NĐ-CP (hiệu lực 15/07/2023) khung **1.500-7.500 đ/m³** cho đá VLXD thông thường. HĐND tỉnh quyết mức cụ thể; có
  tỉnh áp 5.000, có tỉnh 7.500 (thuvienphapluat). Mức Đồng Nai/TP.HCM: không có số.
- **Thuế tài nguyên:** biểu NQ 1084/2015/UBTVQH13 (thuế suất đá VLXD khoảng 7-10% [NỀN, chưa kiểm]). Đá đã nghiền quy về đá xô bồ, giá tính
  thuế là giá bán đá xô bồ nếu thấp hơn giá UBND tỉnh quy định (CV 2778/TCT-CS 2023). Có dự thảo nghị định hướng dẫn Luật Thuế tài nguyên
  sửa đổi (tài liệu xin ý kiến 2026) [DK, chưa rõ nội dung].

**2.6 Thiếu hụt nguồn cung vùng — tổng hợp [UĐ]**
- **Thiếu thật ở TP.HCM** (4,5 tr m³ năm 2026, số chính thức) và ở **Tây Ninh/ĐBSCL** (không có đá tại chỗ). Đồng Nai là nguồn xuất của vùng.
- Nhưng các số dư cầu do Sở/Ban công bố đang **thu hẹp**: Ban Giao thông TP.HCM (20 dự án) Q4/2026 cần 1,91 tr m³ đá, mỏ "cơ bản cân đối"
  về đá (cát mới thiếu nặng, 38-50%), tới cuối T10 còn cần 0,9 tr m³ (TBTCVN 30/10/2026). Đồng Nai nói Long Thành/BH–VT/VĐ3 "cơ bản đáp
  ứng" (03/2026). ⇒ **Đá thiếu ít hơn cát.** Nút thắt cấp tính của ngành VLXD phía Nam năm 2026 là **cát**, nên đá mi đang được dùng
  thay cát [UĐ, NỀN].
- **Giá [DK, Bộ XD qua VietnamPlus 10/11/2026, bình quân cả nước, không tách vùng/quy cách]:** đá Q3/2026 **+3,89 đến +5,83% so với Q2**;
  T10/2026 khoảng **618.324 đ/m³** (+1,04% MoM, +1,9% so với BQ Q3 606.791). Nguyên nhân: mưa kéo dài làm tăng chi phí bóc tầng phủ, và cầu
  dự án trọng điểm. Bộ XD dự báo Q4/2026 cát và đá **+3-8%**. Cát T10 khoảng 1.013.250 đ/m³ (+2% MoM). VCCI 12/11/2026: giá cát, đá tiếp tục
  chịu áp lực tăng cuối năm.
  **⚠ Đính chính file 30/10:** câu "Q3/2026 thị trường VLXD ổn định" (TBTC, không rõ ngày) **sai với đá** theo số Bộ XD. Hướng giá là **tăng
  chậm khoảng 1%/tháng**, không phải đi ngang. Không trộn mức 618 nghìn (bình quân cả nước, nhiều khả năng là giá tới hiện trường) với
  giá tại mỏ ĐNB (1x2 khoảng 257-266 nghìn đ/m³ quy đổi, đầu 2026, ước lượng): khác điểm giao, khác phạm vi.
- **Chi phí [DK BQ]:** heating oil (proxy diesel) BQ tháng: 10/2025 2,29 → 09/2026 4,80 → 10/2026 4,77 → **11/2026 (tới 20/11) 4,21 USD/gal**
  (−12% MoM, vẫn +71% YoY so với 11/2025 2,46). Brent 10/2026 107,5 → 11/2026 95,9. ⇒ Cú sốc diesel **đã qua đỉnh** nhưng mức vẫn cao.

## 3. Bảng 5 tầng chi phí vốn (as-of 16-22/11/2026; liên quan: vốn lưu động nhà thầu, lãi chiết khấu DD, cầu BĐS)

| Tầng | Số | Hướng |
|---|---|---|
| A. Niêm yết Big-4 | 12M online **6,8%** (BIDV/CTG/Agribank, 16/11; VCB 5,4 lệch theo 2/3 nguồn) · 12M quầy khoảng **5,4%** (ghi chú CSV 02-16/11, "bỏ" theo luật kênh cao nhất) · 6M online 6,6% (đọc 10/11, không có số mới) · 6M quầy: không có số | online ĐỨNG, quầy đã GIẢM sau CV 9608 |
| B. CCTG Big-4 | 12M cao nhất **7,4%** (BIDV/CTG, đọc 02/11, chưa có điểm mới sau 02/11) · VCB chỉ phát 6M **7,5%** · spread CCTG12M − online12M +0,6pp; − quầy12M khoảng +2,0pp · sự kiện mở/rút kỳ hạn: không thấy | ĐỨNG |
| C. Ngoài Big-4 | CCTG VPB **9,0%** (≥100 tr, 184-389 ngày, 02/11) · TCB 6M 7,6% (giảm từ 8,0) · MB 6M 7,1% · trần niêm yết 12M thị trường khoảng 7,0% (REGIME READ #3) · số NH ≥7%: không có số | niêm yết GIẢM, "ẩn" khoảng 9% ĐỨNG |
| D. Thị trường | LNH 3M **7,66%** (TE 18/11; +0,76pp/3T, +1,41pp/12T) so với 6,33% (11/11, trend check), 6,60% (05/11) · ON: không có số mới · OMO/tái cấp vốn 4,5% · TPCP 10Y 4,57% (TE, mức UNVERIFIED, chỉ tin Δ +0,59pp/12T), tỷ lệ trúng thầu: không có số · USD/VND 25.801 (TE 20/11, −2,1%/12T) | **3M TĂNG mạnh trong 1 tuần** |
| E. Lượng | tín dụng khoảng 12,27% YTD cuối T10 (Thống đốc, "khoảng"); huy động: không có số cùng mốc · sự kiện nới: TT 50/2026 nâng trần LDR 85→95% từ **01/12/2026** | tín dụng giảm tốc chậm |

**Đồng thuận:** A-online và B đứng yên. **Phân kỳ:** D-3M tăng lên 7,66% trong khi niêm yết đứng hoặc giảm. C-ẩn giữ khoảng 9%. **Cơ chế
(suy luận, khớp REGIME READ #3):** chỉ đạo giảm lãi hướng vào lãi **niêm yết**; giá vốn biên lộ ra ở liên NH kỳ hạn và CCTG/tiền gửi lớn. Việc
3M nhảy giữa tháng (không phải cuối tháng) là thông tin mới, cần thêm 1-2 tuần để biết có phải đợt rời hay không. TT 50 (LDR 95%) là cơ quan quản
lý gián tiếp thừa nhận áp lực vốn. **HƯỚNG:** niêm yết phẳng/giảm. **MỨC:** chi phí vốn biên khoảng 7,4-9%, cao hơn niêm yết online 0,6-2,2pp;
độ tin cậy trung bình. Với ngành đá, tác động chính đi qua **nhà thầu**: chi phí vốn cao cộng hợp đồng trọn gói thì chậm trả tiền cho mỏ (mục 6C).
Bobby không đề xuất ngưỡng mới ở đây.

## 4. Phân loại và pha

**12 tháng tới (12/2026-11/2027):**

| Nhãn | P | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,45** | Cả cung, cầu và giá đều đi qua quyết định hành chính: GP, cấp lại GP (NĐ 21 Đ63), đấu giá chưa ra kết quả, nâng 50% chỉ cho dự án chỉ định, khu không đấu giá cấp cho nhà thầu, phân bổ tới từng gói thầu (Đồng Nai xin bỏ), kiến nghị kiểm soát giá bán tại mỏ, giải ngân ĐTC 74,1% có chấm điểm KPI. Sản lượng và giá của DN trong năm tới phụ thuộc vào văn bản nhiều hơn vào cầu thị trường |
| **CYCLICAL** | **0,30** | Long Thành GĐ1, VĐ3, BH–VT đang rút; nhà ở gãy Q3; diesel qua đỉnh. Nếu VĐ4/metro trượt thì 2027 có khoảng trũng khối lượng |
| **STRUCTURAL** | **0,25** | Giá đá vẫn tăng khoảng 1%/tháng (Bộ XD, cả nước) dù khách hàng lớn nhất đang rút; TP.HCM thiếu 4,5 tr m³ theo số chính thức; cát cạn nên đá mi thay thế |

**36 tháng (2027-2029):** **STRUCTURAL 0,40 / ADMIN_GATED 0,40 / CYCLICAL 0,20.** Lý do nâng STRUCTURAL so với 30/10 (0,20): (1) NQ 27/2026
khoá khung ĐTC 5 năm 8,22 triệu tỷ (2,7 lần), ≥5.000 km cao tốc, và gắn vốn với cam kết vật liệu. Đây là cầu nhiều năm, không phải một
sóng dự án (văn bản có từ 24/04, file 30/10 chưa đọc). (2) Cung gần đô thị bị khoá bởi đất (bồi thường 5-10 lần giá) và trễ 2-4 năm. (3) Tây
Ninh và ĐBSCL không có đá, nên phải kéo từ ĐNB. Lý do giữ ADMIN ngang hàng: chính Nhà nước đang mở cung qua kênh hành chính (khu không đấu
giá, cấp thẳng cho nhà thầu, nâng công suất), và kênh đó **chia phần tô khan hiếm khỏi mỏ thương mại hiện hữu**.

**Độ tin cậy:** `ambiguous` khoảng 60/40. Chỗ lẫn lớn nhất vẫn là tách "nghẽn pháp lý gỡ được" khỏi "cạn vị trí gần đô thị", cộng thêm một lớp
mới: cầu nhiều năm là chắc về khung vốn nhưng **không chắc về tiến độ giải ngân thật** (ĐTC TW mới 59,6% tới 31/10).

**Pha:** sửa từ "ĐỈNH → bình nguyên" (30/10) thành **"giữa-muộn nhịp tăng; khối lượng dự án ĐỔI CHỖ, chưa trũng; giá còn tăng chậm"**. Cầu dời
từ Long Thành/VĐ3 (gần mỏ Biên Hòa) sang VĐ4, Mộc Bài, hướng Tây Bắc, ĐBSCL (xa hơn, cước cao hơn). Như vậy **người thắng trong vùng có
thể đổi**: mỏ phía Bắc Đồng Nai, mỏ Bình Dương/BR–VT cũ, và mỏ có bến sà lan sẽ có lợi hơn mỏ chỉ sống nhờ Long Thành [UĐ].

**Điều kiện đổi phân loại:**
- **STRUCTURAL 12T ≥0,40** nếu giá đá Bộ XD Q1/2027 vẫn tăng >+2% QoQ VÀ khối lượng Long Thành/VĐ3 đã hết.
- **CYCLICAL 12T ≥0,45 (pha suy)** nếu giá đá Bộ XD Q2/2027 giảm so với Q4/2026 VÀ VĐ4 có <50% gói xây lắp chính đã khởi công tới 03/2027.
- **ADMIN ≥0,55** nếu có văn bản trung ương áp trần/khung giá bán đá tại mỏ, hoặc ≥3 mỏ không đấu giá cấp cho nhà thầu ở ĐNB đi vào khai thác.

## 5. FORECAST khoá trước (22/11/2026, falsifiable; ID G* để không trùng F1-F10 của 30/10)

| # | Chấm ngày | Biến (nguồn chấm) | Dự báo |
|---|---|---|---|
| G1 | 2027-02-28 | Giá đá xây dựng **bình quân cả nước Q4/2026** so với BQ Q3/2026 = 606.791 đ/m³, theo báo cáo giá VLXD của Bộ XD (hoặc tin chính thống dẫn Bộ XD) | > +3%: **P = 0,50**; 0 đến +3%: P = 0,35; < 0: P = 0,15 |
| G2 | 2027-08-31 | Như G1, **BQ Q2/2027 so với BQ Q4/2026** | ≥ 0%: **P = 0,65** |
| G3 | 2027-01-31 | Long Thành GĐ1 bắt đầu **khai thác thương mại thường lệ** (lịch bay thường lệ có bán vé, không tính chuyến khai trương/thử nghiệm) **≤ 31/12/2026** (ACV/Cục HK) | **P = 0,80** |
| G4 | 2027-03-31 | VĐ4 TP.HCM: **mọi dự án thành phần** (TP.HCM, Đồng Nai, Bình Dương cũ, Tây Ninh, BR–VT cũ) đều có ≥1 gói xây lắp chính đã khởi công (BQL/UBND/báo chính thống) | **P = 0,55** |
| G5 | 2027-06-30 | ≥1 khu đá **không đấu giá** ở ĐNB (vd Tân Hòa hoặc Lộc Trung, Tây Ninh) được **cấp GP khai thác** | **P = 0,40** |
| G6 | 2027-06-30 | Ít nhất 1 trong 13 khu đá của KH đấu giá 2026 Đồng Nai (QĐ 971) có **kết quả trúng đấu giá được công bố** | **P = 0,75** |
| G7 | 2027-06-30 | Văn bản kế hoạch/báo cáo chính thức của TP.HCM về cân đối đá năm 2027 cho thấy **cầu > công suất** (thiếu hụt > 0) | **P = 0,70** |
| G8 | 2027-03-31 | Đồng Nai công bố tổng khối lượng đá **khai thác/cung ứng năm 2026 ≥ 20 tr m³** (UBND/Sở NN&MT/báo chính thống) | **P = 0,45** (không có số công bố ⇒ "không chấm được") |
| G9 | 2027-06-30 | Có văn bản cấp trung ương (Chính phủ/TTg/Bộ) áp **giá trần hoặc khung giá bán đá tại mỏ** cho dự án trọng điểm | **P = 0,15** |
| G10 | 2027-12-31 | ĐSTĐC Bắc–Nam **khởi công** (gói xây lắp hoặc lễ khởi công chính thức) ≤ 31/12/2027 | **P = 0,45** |
| G11 | 2027-06-30 | Thủ Thiêm–Long Thành HOẶC metro Bình Dương–Suối Tiên có **gói xây lắp chính khởi công** ≤ 30/06/2027 | **P = 0,50** |
| G12 | 2027-02-15 | IIP ngành "khai khoáng khác" (đá, cát, sỏi) cả năm 2026 so với 2025 > 0 (NSO/GSO, nếu công bố dòng này) | **P = 0,75** (không công bố ⇒ "không chấm được") |

**Cách chấm:** mỗi G đúng/sai theo nguồn ở cột. Nguồn không công bố thì ghi "không chấm được", không suy. **Không phải khuyến nghị mua/bán.**

### 5.1 Ghi chú về forecast cũ của file 30/10 (không sửa P, chỉ làm rõ cách chấm)
- **F1** ("chuyến bay thương mại đầu tiên ≤31/12/2026", P 0,65) bị **định nghĩa lỏng**: các tiêu đề báo nói đã có "chuyến bay khai trương / chở
  khách đầu tiên" ngày 19/12/2025, tức trước ngày khoá forecast. Đề xuất chấm F1 theo nghĩa hẹp như G3 (khai thác thương mại thường lệ). G3
  là bản đo rõ ràng thay thế.
- **F7** ("NĐ sửa NĐ 193 mở rộng khu không đấu giá ban hành ≤31/03/2027", P 0,55) bị **định nghĩa lỏng**: NĐ 21/2026 (16/01/2026) đã sửa NĐ
  193 TRƯỚC ngày khoá, và không xác minh được nó có chạm Điều 143 hay không. Đề xuất chấm F7 chỉ với văn bản **ban hành sau 30/10/2026** VÀ
  **sửa tường minh Điều 143**. Nếu không có văn bản nào như vậy thì F7 sai.
- F2-F6, F8-F10 giữ nguyên định nghĩa. Thông tin mới liên quan: F10 (ĐTC 2026 ≥85%) có mốc 74,1% tới 31/10. F9 (heating oil 03/2027 <4,0):
  11/2026 BQ 4,21.

## 6. DD cần kiểm gì cho một DN khai thác đá ĐNB

**A. Giấy phép, đất, trữ lượng (quan trọng nhất)**
1. Bảng **từng GP**: số, ngày cấp, **ngày hết hạn**, công suất cấp phép (m³/năm), **cote đáy** (−80 hay sâu hơn), diện tích. Có mỏ nào nằm
   trong **5 mỏ hết hạn chờ gia hạn** của Đồng Nai không; đã dùng cơ chế **cấp lại sau hết hạn (NĐ 21/2026 sửa Đ63)** chưa.
2. **Trữ lượng còn lại thật** (cấp chắc chắn so với dự báo) chia sản lượng thực ⇒ số năm còn khai thác của từng mỏ; so với khấu hao.
3. **Thuê đất đủ cho toàn bộ diện tích khai thác chưa** (bẫy Tam Phước–Phước Tân); GCN đăng ký đầu tư có nằm trong nhóm 26 mỏ vướng không.
4. Mở rộng hoặc hạ cote: có phải qua đấu giá không; hồ sơ thăm dò tới đâu; ước trễ.
5. Lịch sử **xử phạt/đình chỉ**: vượt công suất, vượt cote, ngoài ranh, sạt lở. Mỗi lần đình chỉ là mất sản lượng.
6. **Đô thị bao vây**: khoảng cách tới dân cư, quy hoạch tỉnh mới sau sáp nhập (tiền lệ Tân Đông Hiệp).

**B. Vị trí và kênh**
7. Khoảng cách (km) tới TP.HCM, các gói VĐ4, Mộc Bài, Long Thành GĐ2, trạm trộn lớn; có **bến sà lan** ra ĐBSCL không.
8. Ai trả cước (giá xuất mỏ hay giá giao); DN có tự vận chuyển không (độ nhạy diesel).
9. Cơ cấu sản phẩm 1x2/4x6/0x4/hộc/**mi** (mi thay cát là động lực riêng năm 2026).
10. Tỷ trọng doanh thu từ **Long Thành/VĐ3/BH–VT** (đang rút) so với VĐ4/Tây Bắc/ĐBSCL/bê tông thương phẩm: đo độ hụt 2027.

**C. Khách hàng, giá, tiền**
11. Có tham gia **nâng 50% công suất** (NQ 168/02) không. Phần tăng thêm bán cho dự án chỉ định **theo giá nào**; có bị khống chế giá không
    (CV 2757; kiến nghị kiểm soát giá tại mỏ 30/10/2026).
12. Khối lượng có bị **tỉnh phân bổ tới từng nhà thầu** không. Nếu Đồng Nai thôi phân bổ năm 2026/2027 thì DN được lợi hay thiệt.
13. **ASP thực** (doanh thu/m³) theo quý so với giá công bố Sở và giá Bộ XD. Lệch lớn là dấu hiệu bán qua trung gian/bên liên quan.
14. **Phải thu** từ nhà thầu dự án công: kỳ thu, nợ quá hạn, dự phòng (nhà thầu kẹt hợp đồng trọn gói, chi phí vốn biên 7,4-9%).
15. Tập trung khách hàng top 5.

**D. Nghĩa vụ tài chính với Nhà nước**
16. **Tiền cấp quyền**: theo NĐ 67/2019 (GP cũ) hay NĐ 193 (T = Q×G×R, **quyết toán theo sản lượng thực**, Đ139). Số đã nộp, còn phải nộp, R áp
    dụng, **rủi ro truy thu/hoàn** khi quyết toán hoặc khi điều chỉnh trữ lượng/công suất (kể cả phần nâng 50%).
17. **Thuế tài nguyên**: tính trên giá bán thật hay sàn giá tính thuế của tỉnh; quy đổi về đá xô bồ (CV 2778/TCT-CS); rủi ro truy thu khi giá tăng.
18. **Phí BVMT** (khung 1.500-7.500 đ/m³, mức HĐND tỉnh); **ký quỹ cải tạo, phục hồi môi trường** và chi phí đóng cửa mỏ đã trích đủ chưa.
19. Độ nhạy biên gộp với diesel, thuốc nổ, điện, **chi phí bóc tầng phủ khi mưa** (Bộ XD nêu là nguyên nhân tăng giá Q3/2026).

**E. Cạnh tranh mới và quản trị**
20. **Đối thủ hành chính**: khu không đấu giá cấp cho nhà thầu (Tây Ninh 2 khu đá 20,3 tr m³; TP.HCM cấp mỏ trực tiếp cho dự án tư nhân trọng
    điểm) có cắt vào thị trường mục tiêu của DN không.
21. **Tham gia đấu giá** mỏ mới (13 khu Đồng Nai): mỏ nào, R trúng, vốn (thăm dò 100% vốn chủ/bảo lãnh, capex khoảng 16 nghìn đ/m³ trữ lượng,
    GPMB có thể 5-10 lần giá). Trúng giá cao có thể huỷ giá trị.
22. Cổ đông Nhà nước/công ty mẹ: thoái vốn, **chuyển giá** qua bán cho công ty liên quan.
23. Tài sản ngoài mỏ (đất sau cải tạo, KCN, BĐS): nguồn giá trị **hoặc** kênh chuyển hướng vốn.
24. Quyền khai thác hoặc mỏ có đang là **tài sản bảo đảm** cho khoản vay/khoản nợ bị đem đấu giá không (đã có tiền lệ ở Đồng Nai, Báo Đấu thầu).

## 7. Chỉ báo theo dõi

| # | Chỉ báo | Nguồn | Ngưỡng đổi đọc |
|---|---|---|---|
| 1 | Giá đá BQ cả nước theo tháng/quý | Bộ XD (qua báo) | Q1/27 >+2% QoQ ⇒ nâng STRUCTURAL; Q2/27 < Q4/26 ⇒ nâng CYCLICAL |
| 2 | Giá 1x2 công bố Sở XD Đồng Nai/TP.HCM + giá giao dịch trên báo | Sở XD, Báo Đấu thầu | lệch >±7% (F2) |
| 3 | Kết quả đấu giá 13 khu đá Đồng Nai, R trúng | UBND, Sở NN&MT | R trúng >10% ⇒ chi phí vào ngành tăng mạnh |
| 4 | GP khu không đấu giá (Tây Ninh, TP.HCM) | UBND tỉnh | ≥3 mỏ vào khai thác ⇒ nâng ADMIN, giảm tô mỏ cũ |
| 5 | Tiến độ VĐ4 theo dự án thành phần | BQL/UBND | G4 |
| 6 | Giải ngân ĐTC (tháng), riêng vốn TW | Bộ TC | 2026 <80% ⇒ hạ cầu 2027 |
| 7 | Văn bản giá/phân bổ: trần giá tại mỏ, Đồng Nai bỏ phân bổ tới nhà thầu | Chính phủ/UBND | G9 |
| 8 | Heating oil/diesel | BQ `commodity_prices`, BCT | |
| 9 | LNH 3M, CCTG Big-4 | TE/VBMA, `cctg_rate_vn.py` | 3M >7,5% 2 tuần liên tiếp ⇒ căng vốn nhà thầu |

## Nguồn (ngày đăng)
- Macro snapshot TE as-of 2026-11-22 (`agents/Taylor/research/dd_VLB_20261122/macro_snapshot_2026-11-22.md`); BQ `tav2_bq.commodity_prices` (brent, heating_oil, TE daily) truy vấn 22/11/2026; `data/deposit_rate_vn_events.csv` (16/11), `data/cctg_rate_vn_events.csv` + `_tier2` (02/11), `data/refresh_deposit_cctg_weekly_2026-11.log`.
- VietnamPlus 10/11/2026 "Giá các loại VLXD vẫn neo cao, dự báo tiếp tục tăng": https://www.vietnamplus.vn/gia-cac-loai-vat-lieu-xay-dung-van-neo-cao-du-bao-tiep-tuc-tang-post1147414.vnp
- VCCI 12/11/2026 "Giá VLXD tăng cuối năm…": https://vcci.com.vn/tin-tuc/gia-vat-lieu-xay-dung-tang-cuoi-nam-xay-nha-co-the-doi-chi-phi-bao-nhieu ; DĐDN 17/11/2026 (Hà Nội ổn định giá VLXD): https://diendandoanhnghiep.vn/on-dinh-gia-vat-lieu-xay-dung-10187575.html
- TBTCVN 30/10/2026 "Khơi thông nguồn cung vật liệu, thúc đẩy tiến độ đầu tư công": https://thoibaotaichinhvietnam.vn/khoi-thong-nguon-cung-vat-lieu-thuc-day-tien-do-dau-tu-cong-206157.html
- NNMT 09/04/2026 "TP.HCM giải bài toán nguồn cung VLXD": https://nongnghiepmoitruong.vn/tphcm-giai-bai-toan-nguon-cung-vat-lieu-xay-dung-d805341.html
- Báo Đầu tư 23/12/2025 "Gỡ vướng pháp lý để bảo đảm nguồn cung VLXD cho TP.HCM": https://baodautu.vn/go-vuong-phap-ly-de-bao-dam-nguon-cung-vat-lieu-xay-dung-cho-tphcm-d468022.html
- KTSG 06/05/2026 "Áp lực vật liệu trong chu kỳ đầu tư công mới": https://tuoitre.vn/saigontimes/ap-luc-vat-lieu-trong-chu-ky-dau-tu-cong-moi/ ; NQ 27/2026/QH16 (24/04/2026): https://tuoitre.vn/quoc-hoi-dong-y-phan-bo-8-22-trieu-ti-dong-von-dau-tu-cong-trung-han-20260424114621296.htm
- Giải ngân ĐTC 10T/2026: https://www.vietnamplus.vn/10-thang-giai-ngan-von-dau-tu-cong-cua-ca-nuoc-dat-741-ke-hoach-post1146172.vnp ; https://thoibaotaichinhvietnam.vn/giai-ngan-von-dau-tu-cong-dat-74-1-ke-hoach-sau-10-thang-206359.html
- Long Thành 24/12: https://www.vietnamplus.vn/san-bay-long-thanh-du-kien-dua-vao-khai-thac-thuong-mai-tu-ngay-2412-post1145203.vnp ; https://cafef.vn/san-bay-long-thanh-du-kien-khai-thac-thuong-mai-tu-ngay-24-12-18826103020161464.chn ; tiến độ/thiếu thợ: https://stockbiz.vn/tin-tuc/dua-san-bay-long-thanh-vao-khai-thac-thuong-mai-acv-giai-bai-toan-ve-dich-thang-12-the-nao/41859478 ; GĐ2 (QĐ 26/QĐ-BXD): https://vcci.com.vn/tin-tuc/giao-acv-lam-chu-dau-tu-giai-doan-2-san-bay-long-thanh
- VĐ4: https://tienphong.vn/dieu-gi-khien-vanh-dai-4-tphcm-qua-dong-nai-kho-thi-cong-post1880298.tpo ; https://cafeland.vn/tin-tuc/nguoi-dan-tay-ninh-da-nhan-hon-9190-ty-tien-boi-thuong-lam-tuyen-duong-dai-nhat-dong-nam-bo-153325.html
- BH–VT 18/05/2026: https://tienphong.vn/thong-xe-toan-tuyen-cao-toc-bien-hoa-vung-tau-post1844264.tpo ; Mộc Bài: https://tuoitre.vn/cao-toc-tphcm-moc-bai-can-gan-5-trieu-m-vat-lieu-lay-tu-dau-100260625172605756.htm
- TP.HCM hạ tầng 01/09/2026: https://cafef.vn/tphcm-vao-giai-doan-dau-tu-ha-tang-lon-nhat-tu-truoc-den-nay-188260901185952501.chn
- ĐSTĐC 12/2027: https://hatinh.gov.vn/vi/bai-viet/duong-sat-toc-do-cao-bac-nam-du-kien-khoi-cong-cuoi-nam-2027
- BĐS TP.HCM Q3/2026: https://vov.vn/kinh-te/thi-truong-can-ho-tai-tphcm-quy-iii2026-suc-mua-giam-thanh-khoan-thap-post1342202.vov ; https://cafef.vn/luong-tieu-thu-can-ho-dat-nen-o-tphcm-va-vung-phu-can-giam-den-66-188261012122754748.chn
- Tây Ninh: SGGP 24/04/2026 https://www.sggp.org.vn/khoanh-dinh-mo-khong-dau-gia-tay-ninh-chuan-bi-san-vat-lieu-cho-du-an-trong-diem-post849634.html ; VOV 13/10/2026 https://vov.vn/kinh-te/tay-ninh-lap-to-dieu-phoi-uu-tien-vat-lieu-cho-cong-trinh-trong-diem-post1340867.vov
- Đồng Nai đấu giá 2026: https://baodauthau.vn/dong-nai-se-dau-gia-quyen-khai-thac-16-mo-khoang-san-trong-nam-2026-post195932.html ; nâng 50%/phân bổ: https://baomoi.com/co-ban-dap-ung-vat-lieu-cho-du-an-trong-diem-c54772525.epi , https://24hmoney.vn/news/mo-da-chua-san-sang-nang-50-cong-suat-go-nut-that-de-giu-tien-do-dai-du-an-c30a2596073.html , https://www.sggp.org.vn/tinh-dong-nai-thieu-vat-lieu-xay-dung-tai-du-an-trong-diem-post799646.html
- NĐ 21/2026/NĐ-CP: https://tapchicongthuong.vn/sua-doi-quy-dinh-ve-cap--cap-lai-giay-phep-khai-thac-khoang-san-406304.htm ; VCCI về Điều 143: https://www.vcci.com.vn/tin-tuc/hoan-thien-chinh-sach-thao-go-vuong-mac-trong-trien-khai-luat-dia-chat-va-khoang-san ; Luật 147 hiệu lực 01/01/2026: https://moit.gov.vn/en/news/completing-the-legal-framework-for-mineral-extraction-activities.html ; VBHN 149: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/10/149-vbhn-vpqh.signed.pdf
- Tiền cấp quyền NĐ 193 Đ132/139/140: https://thuviennhadat.vn/phap-ly-nha-dat/cong-thuc-tinh-tien-cap-quyen-khai-thac-khoang-san-2025-705362.html (05/09/2025) ; https://hethongphapluat.com/decree-no-193-2025-nd-cp-dated-july-02-2025-on-elaborating-the-law-on-geology-and-minerals/dieu-139
- Phí BVMT NĐ 27/2023: https://thuvienphapluat.vn/van-ban/thue-phi-le-phi/nghi-dinh-27-2023-nd-cp-phi-bao-ve-moi-truong-doi-voi-khai-thac-khoang-san-568198.aspx ; CV 2778/TCT-CS: https://thuvienphapluat.vn/cong-van/thue-phi-le-phi/cong-van-2778-tct-cs-2023-thue-tai-nguyen-580928.aspx
- Các nguồn còn hiệu lực từ file 30/10 (KTSG 08/03, 21/05/2025, 25/03/2026; Báo Đấu thầu 08/09, 29/10/2025, 04/03, 15/05, 22/05/2026): xem `sector_read_da_xay_dung_nam_bo_20261030.md` § Nguồn.
