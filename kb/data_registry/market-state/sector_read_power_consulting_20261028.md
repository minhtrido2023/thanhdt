---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-28. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay khuyến nghị của bất kỳ ai về doanh nghiệp tư vấn điện cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành tư vấn khảo sát – thiết kế – QLDA điện VN (khách hàng EVN/EVNNPT/GENCO/các ban QLDA điện + PVN và chủ đầu tư tư nhân). Gồm pipeline PDP8 điều chỉnh so với tiến độ thật, cấu trúc ngành và cơ chế giá tư vấn, phân loại nhu cầu (STRUCTURAL_UPCYCLE hay phụ thuộc hành chính), FORECAST khoá trước, chỉ báo dẫn dắt, checklist DD.
as_of: 2026-10-28 (tin web ≤ 2026-10-28; không dùng BQ)
---

# SECTOR READ: Tư vấn khảo sát – thiết kế – QLDA điện VN, as-of 28/10/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc:** `sector_read_fertilizer_dap_20261028.md` và `vn_sector_read_rubber_20261027.md` (chỉ để lấy mẫu định dạng),
  cùng phần đầu và mục lục của `vn_macro_regime_history.md` để thêm con trỏ.
- **Ghi chú trung thực 1 (context tự nạp):** KB fleet được nạp sẵn vào mọi phiên (`context_pack`) có nhắc một mã thuộc
  ngành này như một case discretionary của fleet (cụm "DGC/TV1-style", "case TV1/DRI 2026-08-11" về đối soát fill). Vì vậy tôi
  biết fleet đang quan tâm ít nhất một doanh nghiệp trong ngành. Đoạn đó không có giá, BCTC, verdict hay forward return. Tôi không
  dùng nó cho phân loại.
- **Ghi chú trung thực 2 (web):** khi tìm kiếm, tiêu đề hoặc đường dẫn của kết quả có lộ: (a) tên các CTCP Tư vấn xây dựng điện
  1-5 (PECC1-5) ở vai trò nhà thầu trúng gói tư vấn. Đây là dữ kiện cấu trúc ngành ("ai thắng thầu"), tôi dùng ở mục 3 đúng ở mức
  gói nào, giá gói và giá trúng. (b) Một tiêu đề về ngày chốt quyền cổ tức của một DN tư vấn và số tiền EVN sẽ nhận: **không mở,
  không dùng**. (c) Một trang "Corporate Analysis" có slug nhắc 2 mã tư vấn trúng thầu hạt nhân: **không mở**. (d) Một link báo
  cáo CTCK (BSC): **không mở**. (e) 24hmoney (trang chứng khoán): chỉ dùng snippet về số giải ngân của EVN (EVN không niêm yết),
  không mở bài.
- **Không đọc:** `kb/projects/*`, `agents/Taylor/*`. Không tra giá cổ phiếu, BCTC hay khuyến nghị CTCK của DN tư vấn nào.
- **BQ:** không truy vấn. `tav2_bq` không có chuỗi capex/giải ngân EVN, sản lượng điện hay kết quả thầu. **Lượt này không đọc chi
  phí vốn**, nên không lấp bảng 5 tầng lãi suất và không đưa kết luận nào về lãi suất.

## 1. Pipeline nhu cầu 2026-2030: kế hoạch và tiến độ thật [DK trừ khi ghi khác]
| Hạng mục | Kế hoạch / neo chính sách | Tiến độ thật (as-of) | Đọc |
|---|---|---|---|
| **PDP8 điều chỉnh** (QĐ 768/QĐ-TTg, 15/04/2025) | Vốn nguồn + lưới truyền tải 2026-2030 khoảng **136 tỷ USD** (dải dự thảo 136-172, nguồn 118-148, lưới 18-24). Lưới 2025-2030 là **18,1 tỷ USD**: NN 12,9, xã hội hoá 5,2. EVN chỉ đáp ứng tối đa khoảng **40%** khối lượng lưới (SGGP) | Cục Điện lực/BCT 15/09 và 07/10/2026, tính trên công suất nguồn PDP8 sau hơn 3 năm: **~5% đã vận hành, ~9% đã khởi công, ~28% có NĐT nhưng chưa khởi công, ~45% CHƯA có chủ trương đầu tư**. BCT đang soạn báo cáo tổng thể cung ứng 2027-2030 **kèm đề xuất điều chỉnh PDP8 thêm lần nữa** | Trượt nặng ở NGUỒN. Gần một nửa công suất còn ở trước bước chủ trương, tức vẫn ở **pha tư vấn** |
| **Thiếu điện** (BCT 15/09/2026) | — | Thiếu công suất **4.256 MW (2027), 8.309 (2028), 13.348 (2029), 13.964 MW / 61,18 tỷ kWh (2030)**. Riêng miền Bắc thiếu 5.680 MW năm 2027. SX điện 2026 khoảng 354,4 tỷ kWh (+9,7%). Q4/2026 dự kiến +11,3% YoY (NSMO) | Áp lực chính trị lên đầu tư lưới và nguồn đi **lên**, không đi xuống |
| **Vốn đầu tư EVN** | KH 2026 khoảng **123.000 tỷ**, thấp hơn mức thực hiện 2025 | 2024: 112.890 tỷ. 2025: **125.778 tỷ** (+14,7%, vượt KH năm thứ 2). 2026: Q1 khoảng 21.000 tỷ (**17%** KH), H1 khoảng 45.000 tỷ (**36%**). Chưa có số 9T | Capex khối EVN năm 2026 **đi ngang**, "upcycle" chưa hiện ra trong capex EVN. Giải ngân dồn H2 |
| **Lưới 110-500kV toàn EVN** | KH 2026: **khởi công 285, hoàn thành 300**. Năm 2025 thực hiện: khởi công 215, đóng điện 260 (+27.000 MVA, 3.900 km) | 9T/2026: **khởi công 136** (2×500kV, 18×220, 116×110), **đóng điện 131** (5×500kV, 16×220, 110×110), tức **48% / 44%** KH | Sau 9 tháng chưa tới một nửa KH |
| **EVNNPT** (truyền tải) | KH 2026: **khởi công 87 (28×500kV)**, **đóng điện 86 (22×500kV)**. Vốn hơn 27.270 tỷ (20.130 tỷ là thuần đầu tư) | Toàn EVN 9T chỉ **khởi công 2 và đóng điện 5 công trình 500kV**. EVN nói khối lượng 2026-2030 **"vượt khả năng nguồn lực đáp ứng cùng lúc"** và yêu cầu EVNNPT xếp hạng ưu tiên dự án (23/01/2026) | Trượt rất lớn ở cấp 500kV [UĐ: có thể lệch phạm vi đếm "công trình" với "dự án", nhưng 2 so với 28 là khoảng cách quá lớn để chỉ do cách đếm]. Đây là **trần tài chính** |
| **Tuyến 500kV mới** | Krông Buk–Tây Ninh 1 (khoảng 330 km, khoảng 14.060 tỷ, đóng điện 2030). Thốt Nốt–Đức Hòa (6.800 tỷ). LNG Bạc Liêu–Thốt Nốt (8.275 tỷ, 135,6 km, **khởi công Q2/2027, xong Q4/2028**). Bình Định–Krông Buk (8.208 tỷ). Thạnh Mỹ–Quảng Trạch–Dốc Sỏi (đoạn Đà Nẵng 3.850 tỷ, vốn vay Q4/2026 đến Q4/2028) | Phần lớn đang ở bước **chọn tư vấn KS-TK / lập FS** (mục 3) | Khối lượng tư vấn 2026-2027 có thật. Doanh thu xây lắp tới sau 2027 |
| **Nguồn do EVN làm chủ đầu tư** | KH 2026: COD Quảng Trạch I, khởi công Tuyên Quang MR (Q3), Quảng Trạch III, Sê San 3/4 MR, Bản Chát, Srepok 3 (Q4) | Quảng Trạch I (than, 2×701,5 MW) đã phát lên lưới, COD tổ 1 cuối T11 và tổ 2 cuối T12/2026. **LNG Quảng Trạch II** (1.612,8 MW): EPC PowerChina–LILAMA ký 09/02/2026 (hơn 25.000 tỷ), **khởi công 20/10/2026, trễ khoảng 1 năm**. Tuyên Quang MR và Sê San 3/4 MR vẫn **đang hoàn thiện FS** (06/10), nên mốc Q3-Q4 trượt. Sơn La/Lai Châu MR đang làm hồ sơ chủ trương | Thuỷ điện mở rộng cũng trượt, nhưng vẫn ở pha FS/thiết kế, tức vẫn là việc của tư vấn |
| **BESS** | BCT: thêm 2.000-3.000 MW giai đoạn 2027-28 | Đã xong 205 MW, miền Bắc thêm 305 MW trong T10. BESS tập trung 550 MW (Ban QLDA điện 2) và 300 MW (GENCO3) đang làm thủ tục | Định mức tư vấn cho loại hình này "chưa cập nhật đủ" (mục 3) |
| **LNG** | PDP8: **22,5 GW / 15 dự án tới 2030** | 18 dự án khí, trên 20 GW. **16/18 đã có NĐT nhưng chỉ 2 khởi công** (đầu T10). Bộ trưởng nói chỉ **Hiệp Phước** đúng tiến độ (COD Q4/2028). Nhơn Trạch 3-4 COD 05/01/2026. LNG Quảng Ninh đã GPMB 41 ha từ T4/2026 nhưng chưa khởi công vì PPA/khí/thiết bị (28/10). BCT đề xuất **chuyển LNG chậm sang 2031-2035 và bổ sung khoảng 5.300 MW than vào 2030** | Mảng LNG là **ADMIN/thương mại-gated** (PPA, Qc, giá khí). Brent khoảng 116 USD (xem file phân bón) còn làm xấu kinh tế LNG |
| **Hạt nhân Ninh Thuận 1** | 2×VVER-1200 (khoảng 2.400 MW). EVN là chủ đầu tư. Vận hành **2030-2035** (Sở NNMT Khánh Hòa); một nguồn ghi "trước hết 2031" | IGA Việt–Nga ký 03/2026. NQ 46/NQ-CP (14/03) và QĐ 496/QĐ-TTg (27/03) lập Hội đồng thẩm định NN cho **điều chỉnh chủ trương**. Pre-FS điều chỉnh **vẫn đang hoàn thiện** (12/05). Kỳ họp bất thường QH (khoảng 08/2026) **thông qua tách thành 3 dự án độc lập** và họp riêng 11/08 về phê chuẩn hiệp định (kết quả biểu quyết phê chuẩn chưa xác minh trong lượt này). Ngày 16/07 PTT TT vẫn giục hoàn thiện hồ sơ. **GPMB trễ hạn 30/06/2026; khởi tố 4 bị can** về bồi thường. Gói khảo sát địa điểm + cập nhật SAD giai đoạn 1 đã chấm thầu. Gói **tư vấn chủ đầu tư (owner's engineer)** đang chuẩn bị. MoU Rosatom–PECC2 (09/2025) cập nhật FS và hồ sơ địa điểm | Chưa có FS, EPC hay mốc khởi công nào được công bố. Với tư vấn VN đây là **khảo sát/địa điểm/hỗ trợ**, thiết kế lò thuộc phía Nga |
| **Hạt nhân Ninh Thuận 2** | PVN làm chủ đầu tư, khoảng 2.000 MW | Nhật rút. PVN–KEPCO đẩy nhanh đàm phán (09/09/2026) | Chưa có đối tác chính thức |
| **Điện gió ngoài khơi (ĐGNK)** | Khoảng **6.000 MW vào 2030-2035**. NQ 253/2025/QH15 + **NĐ 272/2026/NĐ-CP** (04/07/2026, hiệu lực tới 31/12/2030): TTg chấp thuận chủ trương cùng với chấp thuận NĐT; đơn vị khảo sát cần ≥1 tỷ đồng VCSH/MW | **Tới cuối 2025 chưa dự án nào được chấp thuận chủ trương.** PVN–CIP ký thoả thuận Nam Trung Bộ 1 (1.000 MW, trên 4 tỷ USD) ngày 22/10/2026, "giai đoạn phát triển sớm". Gia Lai chọn VinEnergo cho 2.000 MW **gần bờ** (06/02/2026). Đơn vị thuộc BQP (LLC) đề xuất 14 dự án 9.000 MW (05/2026) | Hiện chỉ có khảo sát biển, chưa có FID |
| **DPPA / mặt trời mái nhà** | NĐ 57/2025 được sửa bởi **NĐ 243/2026** (26/06/2026). Mục tiêu 2.800 MW mái nhà tại cơ sở NN trước 06/2027 | Giao dịch DPPA qua lưới đầu tiên từ 01/06/2026 (TTC Đức Huệ 2 với Samsung Thái Nguyên). Hướng dẫn vẫn chưa hoàn thiện (08/2026) | Mảng nhỏ và phân tán, ít khối lượng cho tư vấn lưới lớn [UĐ] |

**Điểm nghẽn thể chế [DK]:**
- **Giá điện:** NĐ 278/2026/NĐ-CP (09/07/2026) sửa NĐ 72/2025. Có 2 bản trích không khớp nhau: một bản nói ngưỡng tăng nâng từ
  3% lên 5% và ngưỡng giảm hạ từ 2% xuống 1%; bản kia nói EVN chỉ được tăng 2-<5% sau khi có ý kiến bằng văn bản của BCT. Cả hai
  đều thể hiện cùng một ý: **siết quy trình tăng giá**. Lỗ luỹ kế khoảng **44.700 tỷ** đang được đề xuất phân bổ dần vào giá (dự
  thảo 05-07/2026).
- **Tài chính EVN tốt hơn hẳn 2022-23:** LN hợp nhất 2025 là **51.880 tỷ** (gấp hơn 6 lần 2024). Lỗ luỹ kế hợp nhất 38.690 tỷ
  được xoá hết, LN giữ lại +5.530 tỷ. Công ty mẹ vẫn còn lỗ luỹ kế (tài liệu nội bộ: khoảng 12.976 tỷ). Tiền và tiền gửi
  **152.400 tỷ**, nợ vay 341.300 tỷ, phải trả nhiên liệu/IPP trên 118.000 tỷ (theinvestor 08-09/06/2026).
- **Khung pháp lý đang mở rộng:** NQ 70-NQ/TW (an ninh năng lượng); NQ 253/2025/QH15 + NĐ 272/2026; **Luật Điện lực sửa đổi** được
  trình ngày 20/10/2026 tại kỳ họp thứ 2 QH khoá XVI; BCT đề xuất **miễn thủ tục chủ trương riêng cho dự án đã có trong PDP8**.
  Đã có kỳ họp QH ngày 04/10 yêu cầu siết tiêu chí xác định dự án điện "cấp bách".
- **Nghẽn được nêu chính thức:** chọn NĐT, đất/GPMB, PPA (LNG), vốn, và **chất lượng tư vấn cùng năng lực nhà thầu** (EVN
  23/01/2026). Hồ sơ chủ trương, FS và TKKT đang dồn ứ.

## 2. Phân kỳ quan trọng [UĐ]
Ba proxy cùng chỉ một **hướng** là nhu cầu dài hạn tăng: thiếu điện đo được, PDP8, pháp lý đặc thù. Hai proxy cho **mức chuyển
hoá** 2026 lại nói chậm: capex EVN đi ngang (123k so với 125,8k) và 500kV khởi công 2/28. Hai điều này không mâu thuẫn. Tư vấn
đứng **trước** capex 1-3 năm. Trượt tiến độ thi công **không xoá** khối lượng tư vấn, chỉ dời nó đi. Mỗi lần đổi kế hoạch (PDP8
sửa lần 2, LNG đổi sang than, thêm BESS và mái nhà, tách dự án hạt nhân) lại **sinh thêm** việc quy hoạch, FS và thiết kế lại.
Ngược lại, khi chủ trương **chưa được duyệt** (45% công suất nguồn) thì phần tư vấn lớn nhất (TKKT, BVTC) cũng chưa thể bắt đầu.
Vì vậy nút cổ chai là **tốc độ ra quyết định hành chính**, không phải nhu cầu.

## 3. Cấu trúc ngành tư vấn điện
**Kết quả thầu công khai [DK, Báo Đấu thầu]:**
| Dự án / gói | Giá gói | Giá trúng | Giảm | Số nhà thầu | Nhà thầu trúng | Ghi chú |
|---|---|---|---|---|---|---|
| 500kV Krông Buk–Tây Ninh 1, **gói 5** (KS, TKKT-dự toán, BVTC, HSMT) | 163,568 tỷ | **158,84 tỷ** | −2,9% | 2 | Liên danh PECC3 + PECC2 + PECC4 | PECC5 bỏ 160,48 tỷ nhưng điểm tổng hợp thấp hơn. 270 ngày, đóng thầu 03/03/2026, công bố 30/03 |
| 500kV Thốt Nốt–Đức Hòa, gói 1 (KS hướng tuyến, hồ sơ chủ trương) | 6,0 tỷ | 5,9 tỷ | −1,7% | — | PECC3 | Qua mạng, rộng rãi trong nước |
| nt, **gói 2** (KS, FS, TKKT, BVTC, BIM, HSMT) | 71,328 tỷ | **70,49 tỷ** | −1,2% | ≥2 | PECC3 (thắng PECC2) | Duyệt ngày 27/03/2026 |
| nt, gói 3 (giám sát KS, thẩm tra FS/TKKT) | 4,259 tỷ | 4,046 tỷ (giá dự thầu) | −5% | **1** | PECC5 | Đang xét ngày 30/03/2026 |

- **Tỷ lệ phí [UĐ từ DK]:** phần KS + thiết kế chiếm khoảng **1,1-1,2% TMĐT** của đường dây 500kV (158,84/14.060 = 1,13%;
  81,6/6.800 = 1,2% kể cả FS). Cộng thêm giám sát thi công, thẩm tra và QLDA thuê ngoài thì tổng phí tư vấn bên ngoài có lẽ khoảng
  **2-3% TMĐT** [NỀN, chưa kiểm định mức].
- **Quy mô pool minh hoạ [UĐ]:** capex khối EVN khoảng 123-126 nghìn tỷ/năm × 1,5-3% cho ra khoảng **2-4 nghìn tỷ/năm** phí tư
  vấn ngoài từ khối EVN, chưa gồm PVN và tư nhân. Con số chưa trừ phần việc các ban QLDA tự làm.
- **Cạnh tranh [DK+UĐ]:** ở lưới 500kV, mỗi gói chỉ có **1-2 nhà thầu** và mức giảm **1-5%**. Đây là thị trường **oligopoly** của
  khối "Tư vấn xây dựng điện" gốc EVN (PECC1-5). Giá trúng sát giá gói, mà giá gói được lập theo định mức nhà nước. Liên danh 3
  PECC cho một gói cho thấy quy mô gói vượt năng lực một đơn vị, hoặc các bên chia khối lượng; nói cách khác là **hợp tác nhiều hơn
  cạnh tranh giá**. Tư vấn nước ngoài [NỀN] như Fichtner, AFRY, Tractebel, KEPCO E&C, và các đơn vị liên quan Rosatom chủ yếu làm
  dự án nguồn lớn có vốn/NĐT nước ngoài, LNG, ĐGNK, và vai trò owner's engineer hạt nhân.
- **Sở hữu [DK cũ]:** QĐ 852/QĐ-TTg (2017) định EVN thoái toàn bộ vốn tại PECC3 và PECC4, giữ PECC1 và PECC2. Trạng thái năm 2026
  chưa kiểm. DD phải tự xác minh.
- **Định mức giá tư vấn [DK]:** **NĐ 206/2026/NĐ-CP** (15/06/2026) thay NĐ 10/2021 về quản lý chi phí ĐTXD. **TT 38/2026/TT-BXD**
  (26/06, hiệu lực **01/07/2026**) thay TT 12/2021, tức thay cả bộ định mức chi phí QLDA và tư vấn (Phụ lục VIII cũ). Có thêm CV
  9947/BXD-VPB (29/06/2026) làm mơ hồ phạm vi. **Chưa kiểm được** định mức tư vấn mới tăng hay giảm. EVN thừa nhận định mức tư vấn
  cho loại hình mới (gió, mặt trời, khí, lưu trữ) "chưa được cập nhật đầy đủ" (22/03/2026).
- **Áp lực chất lượng [DK]:** hội nghị tư vấn EVN 2026 (22/03 và 01/04) ghi nhận khảo sát chưa đủ, hồ sơ thiết kế có lỗi, dự toán
  lệch thực tế, khối lượng hồ sơ tăng làm kỹ sư thẩm tra quá tải, và yêu cầu dùng BIM/mô phỏng. Hệ quả là rủi ro làm lại và rủi
  ro trách nhiệm. Phía nhà thầu xây lắp cũng nói nhiều hạng mục bị tính giá thấp so với thực tế (24/07/2026).
- **Vòng đời doanh thu [NỀN]:** hợp đồng chia theo giai đoạn (chủ trương, FS, TKKT, BVTC, giám sát tác giả). Doanh thu ghi theo
  khối lượng hoàn thành **được nghiệm thu** từng giai đoạn nên lệch pha với tiến độ, và dồn về **Q4** vì ban QLDA đẩy giải ngân cuối
  năm. Bằng chứng gián tiếp [DK]: giải ngân EVN Q1 đạt 17% và H1 đạt 36% KH, nên khoảng 64% dồn vào H2.
- **Phải thu [NỀN/UĐ]:** thanh toán sau nghiệm thu và theo kế hoạch vốn của ban QLDA. Quyết toán dự án lớn thường kéo dài nhiều
  năm. Rủi ro **EVN mất khả năng trả** đã giảm nhiều (LN 2025, tiền 152 nghìn tỷ). Rủi ro còn lại là **thủ tục quyết toán chậm**,
  vốn không phụ thuộc sức khoẻ tài chính của EVN.
- **Tập trung khách hàng [UĐ]:** tư vấn lưới truyền tải đối mặt gần như **một người mua duy nhất** (EVNNPT và các ban QLDA của
  EVN). NĐ 272 có mở đầu tư lưới cho NĐT ngoài EVN nhưng chưa thấy dự án nào. Một DN thuần lưới có thể phụ thuộc EVN trên 70%. DD
  phải đo con số này.

## 4. PHÂN LOẠI
**Kết luận: `STRUCTURAL_UPCYCLE` về NHU CẦU tư vấn, nhưng việc chuyển nhu cầu thành doanh thu là `ADMIN_GATED`: trượt tiến độ
là mặc định, không phải ngoại lệ. Độ tin cậy `ambiguous`, khoảng 65/35 nghiêng STRUCTURAL.** Nói gọn: **"cấu trúc về khối lượng
nhiều năm, hành chính về nhịp ghi nhận".**
- **Trục 1 (gốc):** nhu cầu đến từ thiếu hụt điện thật, đo được và do chính BCT công bố (4,3 GW năm 2027, 14 GW năm 2030), cầu
  điện tăng 9,7-11%, và có **nhiều tầng neo chính sách** (QĐ 768, NQ 70, NQ 253 + NĐ 272, Luật Điện lực sửa đổi, IGA hạt nhân).
  Đây không phải chu kỳ tín dụng hay chu kỳ giá.
- **Trục 2 (ai kiểm soát nhịp):** nhịp nằm **trong nước** (chủ trương, PPA, GPMB, giá điện), không phụ thuộc chu kỳ ngoại sinh,
  ngoại trừ một phần là giá khí/dầu (Hormuz) với LNG. Tuy nằm trong tay VN, tốc độ hành chính trong lịch sử chậm, và **9T/2026
  xác nhận điều đó**.
- **Vì sao không phải CYCLICAL:** trượt tiến độ dời doanh thu chứ không xoá nhu cầu. Kế hoạch cứ phải sửa liên tục (PDP8 lần 2,
  LNG sang than, BESS, mái nhà, tách dự án hạt nhân) và **mỗi lần sửa lại tạo thêm việc cho tư vấn**. Tình trạng thiếu điện làm
  chi phí chính trị của việc cắt đầu tư tăng lên.
- **Vì sao chưa clean:** (1) Capex khối EVN 2026 **đi ngang** (KH 123k so với thực hiện 125,8k năm 2025). EVNNPT nói khối lượng
  vượt nguồn lực và EVN chỉ gánh khoảng 40% lưới, nên tồn tại **trần tài chính**. Phần còn lại cần xã hội hoá lưới, việc chưa có
  tiền lệ. (2) Cấp 500kV đến 9T: khởi công 2/28 và đóng điện 5/22. (3) Các mảng "câu chuyện" (LNG, ĐGNK, hạt nhân) trượt nặng nhất
  và phần lớn giá trị tư vấn ở đó có thể vào tay **tư vấn nước ngoài** (Rosatom thiết kế lò, NĐT ngoại mang tư vấn quốc tế cho
  LNG/ĐGNK). (4) Giá tư vấn bị **định mức nhà nước giới hạn**, và khung định mức vừa đổi từ 01/07/2026 mà chưa rõ hướng.
- **Biên lợi nhuận có bền không [UĐ]:** **giữ được, khó mở rộng mạnh.** Mặt đỡ: thị trường lưới oligopoly với 1-2 nhà thầu/gói,
  giảm giá 1-5%; kỹ sư đang được dùng hết công suất, nên đòn bẩy hoạt động dương trong pha này. Mặt trần: định mức theo % chi phí,
  lương kỹ sư tăng, chi phí làm lại/trách nhiệm tăng, và nếu thị trường mở (NĐT lưới tư nhân, tư vấn ngoại) thì có thể bị cạnh
  tranh giá. Rủi ro lớn nhất **không nằm ở biên** mà ở **nhịp ghi nhận và phải thu**.
- **Đổi phán đoán:** chuyển sang **STRUCTURAL clean** nếu EVN công bố thực hiện 2026 ≥123k, KH 2027 >135k, VÀ tỷ lệ công suất
  "chưa có chủ trương" giảm xuống <35%. Chuyển sang **ADMIN-GATED/CYCLICAL** nếu giá điện không được tăng mà EVN lỗ trở lại năm
  2026-27, KH vốn 2027 ≤ KH 2026, hoặc PDP8 lần 2 **cắt** danh mục lưới.

## 5. Chỉ báo dẫn dắt và rủi ro kịch bản xấu
| # | Chỉ báo (tần suất) | Nguồn | Xác nhận STRUCTURAL ⇔ ADMIN-GATED |
|---|---|---|---|
| 1 | **Giải ngân EVN, số công trình lưới khởi công/đóng điện** (tháng, tổng kết năm) | Thông cáo EVN, Báo Đấu thầu, Bộ Tài chính | Năm 2026 ≥123k và KH 2027 >130k ⇔ năm 2026 <115k hoặc KH 2027 ≤ 2026 |
| 2 | **Kết quả thầu tư vấn** của EVNNPT và các ban QLDA (giá gói, giá trúng, số nhà thầu) (tuần) | muasamcong.mpi.gov.vn, Báo Đấu thầu | Số gói KS-TK 220/500kV mới tăng, giảm giá ≤5% ⇔ ít gói mới, giảm >10% hoặc ≥4 nhà thầu (bắt đầu cạnh tranh giá) |
| 3 | **Tỷ lệ công suất PDP8 "chưa có chủ trương"** (khoảng 45% tại 09/2026) (quý) | Báo cáo BCT/Cục Điện lực | <35% ⇔ đứng yên |
| 4 | **PDP8 lần 2 + Luật Điện lực sửa đổi + miễn thủ tục chủ trương riêng** (sự kiện) | QH, Chính phủ | Thông qua và mở rộng danh mục lưới ⇔ trì hoãn hoặc cắt danh mục |
| 5 | **Hạt nhân NT1:** điều chỉnh chủ trương, hợp đồng tín dụng/EPC, giấy phép địa điểm, gói owner's engineer (sự kiện) | EVN, Chính phủ, Rosatom | Ký EPC/tín dụng ⇔ hồ sơ tiếp tục "hoàn thiện" |
| 6 | **ĐGNK:** dự án đầu tiên được chấp thuận chủ trương theo NĐ 272 (sự kiện) | TTg, BCT | Có ⇔ không có trước 06/2027 |
| 7 | **LNG:** số dự án ký PPA hoặc khởi công (tháng) | BCT, EVN, PVN | ≥5 khởi công ⇔ chuyển sang 2031-35 |
| 8 | **Giá điện** (lần tăng giá bán lẻ bình quân, phân bổ lỗ 44,7 nghìn tỷ) và KQKD EVN (sự kiện/năm) | BCT, EVN | Tăng giá đủ và EVN có lãi ⇔ không tăng, EVN lỗ lại |
| 9 | **Định mức tư vấn mới** (TT 38/2026 hoặc văn bản thay thế) (sự kiện) | Bộ Xây dựng | Giữ hoặc tăng tỷ lệ ⇔ giảm |

**Rủi ro kịch bản xấu [UĐ]:**
1. **Trần tài chính EVN:** giá điện không tăng đủ (NĐ 278 siết quy trình) trong khi Brent khoảng 116 USD đẩy chi phí mua
   điện/khí. EVN có thể lỗ lại như 2022-23, dẫn tới giãn capex, trả chậm, KH 2027 bị cắt.
2. **Hình sự hoá/thanh tra:** vụ khởi tố GPMB NT1 và các tiền lệ cũ có thể làm cán bộ ngại ký, khiến chủ trương và FS chậm thêm.
3. **Dịch chuyển cơ cấu khách hàng:** lưới mở cho NĐT ngoài EVN; LNG/ĐGNK do NĐT ngoại kéo theo tư vấn quốc tế; hạt nhân do phía
   Nga thiết kế. Khi đó phần "upcycle" lớn nhất rơi vào tay tư vấn ngoại, còn DN VN chỉ nhận phần khảo sát và phụ trợ.
4. **Định mức mới giảm, hoặc chủ đầu tư ép giá**, hoặc xuất hiện cạnh tranh mới (tư vấn tư nhân, tư vấn của nhà thầu EPC).
5. **Chỉ định thầu/cấp bách nén tiến độ:** khối lượng tăng nhưng tiến độ bị nén, làm tăng rủi ro chất lượng, rủi ro làm lại và
   phạt.
- **Kịch bản tốt:** cơ chế cấp bách cùng miễn chủ trương làm tăng tốc thật, NT1 ký EPC, PDP8 lần 2 mở thêm danh mục lưới 500kV.

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-10-28; chấm theo nguồn công bố đầu tiên ≤ ngày kiểm; ghi Brier dưới mục này)
Mốc gốc: EVN KH vốn 2026 khoảng **123.000 tỷ**, thực hiện 2025 **125.778 tỷ**. Lưới 110-500kV KH 2026 khởi công **285** / hoàn
thành **300**, thực hiện 2025 là 215/260, 9T/2026 là 136/131. Công suất PDP8 "chưa có chủ trương" khoảng **45%** (15/09/2026).

| # | Câu hỏi (YES/NO) | Ngày chấm | P(YES) |
|---|---|---|---|
| F1 | EVN công bố vốn đầu tư/giải ngân **cả năm 2026 ≥ 123.000 tỷ** (hoặc "≥100% KH") | 2027-01-31 | **0,55** |
| F1b | Như F1 nhưng **> 125.778 tỷ** (vượt năm 2025) | 2027-01-31 | **0,40** |
| F2a | EVN cả năm 2026 **khởi công ≥ 215** công trình lưới 110-500kV (bằng mức 2025) | 2027-01-31 | 0,50 |
| F2b | ... khởi công ≥ 285 (đạt KH) | 2027-01-31 | 0,10 |
| F2c | ... **đóng điện ≥ 260** (bằng mức 2025) | 2027-01-31 | 0,30 |
| F3a | NT1: cấp có thẩm quyền **phê duyệt điều chỉnh chủ trương đầu tư** NT1 | 2027-06-30 | **0,55** |
| F3b | NT1: **ký hợp đồng EPC/tổng thầu chính** với phía Nga | 2027-06-30 | **0,25** |
| F3c | NT1: **lễ khởi công chính thức** bất kỳ hạng mục nào tại công trường (kể cả phụ trợ/hạ tầng) | 2027-06-30 | 0,30 |
| F3d | NT1: đổ bê tông lớp đầu đảo hạt nhân (FCD) | 2027-06-30 | 0,02 |
| F4 | NT2: ký văn kiện chính thức (IGA hoặc thoả thuận khung có tính ràng buộc) chọn đối tác công nghệ | 2027-06-30 | 0,30 |
| F5a | **ĐGNK** (ngoài khơi, KHÔNG tính dự án "gần bờ"): ≥1 dự án được TTg/cấp thẩm quyền **chấp thuận chủ trương đầu tư** | 2027-06-30 | **0,30** |
| F5b | ĐGNK: ≥1 dự án đạt FID hoặc khởi công | 2027-06-30 | 0,03 |
| F6 | LNG: **≥5 / 18 dự án khí** đã khởi công (gốc khoảng 3, tính cả Quảng Trạch II 20/10) | 2027-06-30 | 0,30 |
| F7 | TTg ký quyết định **điều chỉnh PDP8 lần nữa** (sau QĐ 768) | 2027-06-30 | 0,40 |
| F8 | EVN **tăng giá bán lẻ điện bình quân** ≥1 lần trong khoảng 28/10/2026 đến 30/06/2027 | 2027-06-30 | 0,55 |
| F9 | **Luật Điện lực (sửa đổi)** được QH thông qua tại kỳ họp thứ 2 khoá XVI | bế mạc kỳ họp (khoảng 12/2026) | 0,80 |
| F10 | Báo cáo BCT/Cục Điện lực kế tiếp (≤30/06/2027) cho tỷ lệ công suất PDP8 "chưa có chủ trương" **≤35%** | 2027-06-30 | 0,35 |

Câu phân loại: P(**khối lượng tư vấn điện 2027 > 2025**, đo bằng KH vốn EVN 2027 > 125.778 tỷ VÀ số gói tư vấn KS-TK 220/500kV
công bố năm 2027 > năm 2025) ≈ **0,65**. Chấm khi có KH vốn EVN 2027 (khoảng 01/2027) và tổng kết thầu năm 2027.

## 7. Điều gì làm tôi sai
1. **Tôi đánh giá thấp tốc độ "cấp bách":** nếu cơ chế đặc thù cộng miễn chủ trương được dùng mạnh tay, 2027 có thể nhảy vọt
   (tiền lệ mạch 3 năm 2024 làm xong trong khoảng 6 tháng [NỀN]). Khi đó F1/F2 sẽ thấp hơn thực tế ở năm sau và nhãn
   ADMIN-GATED là quá bi quan.
2. **Tôi đánh giá quá cao phần dành cho tư vấn VN:** nếu nguồn lớn (LNG, ĐGNK, hạt nhân) do NĐT/EPC ngoại mang tư vấn của họ thì
   "upcycle" chủ yếu nằm ở lưới, mà lưới lại bị trần tài chính EVN chặn.
3. **Số đếm của EVN không cùng phạm vi** (công trình hay dự án, EVN hay EVNNPT), nên đọc "2/28" ở 500kV có thể phóng đại mức trượt.
4. **Ghi nhận doanh thu tư vấn có thể không dồn Q4** nếu DN ghi theo % hoàn thành. Điều này chỉ BCTC từng DN mới trả lời được,
   và tôi cố ý không đọc BCTC.
5. **Định mức mới (TT 38/2026, NĐ 206/2026) có thể thay đổi đáng kể tỷ lệ phí** theo bất kỳ hướng nào. Tôi chưa đọc được bảng
   tỷ lệ.
6. **Giá điện/EVN:** giá dầu khí cao kéo dài cộng thuỷ văn xấu (El Niño mạnh, xem file cao su) có thể đẩy EVN lỗ lại năm 2027 và
   kích hoạt rủi ro 1 sớm hơn tôi nghĩ.

## 8. Checklist cho DD một DN tư vấn điện (Bobby không làm; dành cho người làm DD)
- **Backlog:** giá trị HĐ đã ký chưa thực hiện, tách theo khách hàng (EVNNPT, các ban A/B/C, GENCO, PVN, tư nhân), theo giai đoạn
  (FS, TKKT, BVTC, giám sát), theo loại công trình (lưới 500/220kV, thuỷ điện, nhiệt điện, LNG, ĐGNK, hạt nhân, BESS). Tính
  backlog/doanh thu năm và giá trị HĐ ký mới năm 2026 so với 2025. Với gói liên danh, phải lấy **tỷ lệ phần việc của DN**, không
  lấy cả giá gói. Đối chiếu với muasamcong (ví dụ gói 5 Krông Buk–TN1 158,84 tỷ, 270 ngày từ khoảng T4/2026, nên phần lớn sản
  phẩm giao trong khoảng Q4/2026-Q1/2027 [UĐ]).
- **Phụ thuộc EVN:** % doanh thu từ EVN và các đơn vị thành viên, top-5 khách hàng, % lưới so với nguồn. **Tỷ lệ EVN sở hữu** và
  kế hoạch thoái vốn (QĐ 852/2017 và đề án tái cơ cấu hiện hành).
- **Phải thu và vốn lưu động:** phải thu khách hàng, "phải thu theo tiến độ HĐ xây dựng", chi phí SXKD dở dang (WIP), DSO, tuổi nợ
  (>1 năm, >3 năm), dự phòng, các dự án **đã đóng điện nhiều năm mà chưa quyết toán**, tiền giữ lại. So tiền mặt với phải thu để
  biết bao nhiêu tiền đang "kẹt" ở ban QLDA.
- **Ghi nhận:** chính sách ghi theo nghiệm thu giai đoạn hay theo % hoàn thành; tỷ trọng doanh thu Q4 trong 3-5 năm; độ lệch giữa
  doanh thu và CFO theo quý.
- **Biên và năng lực:** biên gộp theo mảng, chi phí nhân công/doanh thu, số kỹ sư và doanh thu/kỹ sư, chi phí thuê thầu phụ khảo
  sát địa chất. Hỏi trực tiếp **định mức mới (TT 38/2026, NĐ 206/2026) áp cho HĐ ký sau 01/07/2026 làm phí tăng hay giảm**.
- **Mảng mới thật hay MoU:** hạt nhân, ĐGNK, LNG, BESS cần có **hợp đồng đã ký** (giá trị, đối tác, phạm vi). MoU không phải
  backlog (ví dụ MoU Rosatom–PECC2 09/2025 vẫn chỉ là MoU tại as-of này nếu chưa có HĐ).
- **Pháp lý (theo luật fleet: chỉ WARNING, không chặn):** tranh chấp, sai sót thiết kế, có liên quan hồ sơ GPMB/khởi tố NT1 hay
  không.
- **Mốc cần kiểm:** tổng kết năm EVN (khoảng 01/2027: F1/F2), bế mạc kỳ họp 2 QH (F9), báo cáo BCT về PDP8 (F7/F10), các bước
  NT1 (F3), kết quả thầu tư vấn của các tuyến 500kV mới (Bạc Liêu–Thốt Nốt, Bình Định–Krông Buk, Thạnh Mỹ–Dốc Sỏi).

**Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- Báo Đấu thầu, "9 tháng năm 2026: EVN khởi công 136 công trình lưới điện, đẩy mạnh đầu tư BESS", 06/10/2026: https://baodauthau.vn/9-thang-nam-2026-evn-khoi-cong-136-cong-trinh-luoi-dien-day-manh-dau-tu-bess-post209156.html
- Báo Đấu thầu, "Năm 2026, EVN tăng tốc đầu tư loạt dự án nguồn và lưới điện", 30/12/2025: https://baodauthau.vn/nam-2026-evn-tang-toc-dau-tu-loat-du-an-nguon-va-luoi-dien-post191545.html
- EVN, "EVNNPT: Prioritizing projects amid investment pressure in 2026-2030 period", 23/01/2026: https://en.evn.com.vn/d/en-US/news/EVNNPT-Prioritizing-projects-amid-investment-pressure-in-2026-2030-period-60-203-501234
- 24hmoney (chỉ snippet), EVN H1/2026 giải ngân khoảng 45.000 tỷ, 36,4% KH khoảng 123.000 tỷ: https://24hmoney.vn/news/evn-kinh-doanh-the-nao-sau-ky-luc-lai-52-000-ty-dong-c27a2798725.html ; EVN Q1 khoảng 21.000 tỷ, 17% (snippet): https://en.evn.com.vn/d/en-US/news/EVN-ensures-power-supply-and-proactive-preparedness-in-Q1-60-163-501384
- The Investor, EVN tiền 152.400 tỷ, nợ, giải ngân 2024-2025, 09/06/2026: https://theinvestor.vn/vietnam-state-utility-evn-explains-why-it-holds-58-bln-in-cash-bank-deposits-d19276.html ; LN 2025 51.880 tỷ, 08/06/2026: https://theinvestor.vn/from-147-bln-accumulated-loss-to-197-bln-net-profit-in-2025-what-drove-vietnam-electricitys-turnaround-d19273.html
- Tiền Phong, "Bộ Công Thương cảnh báo nguy cơ thiếu điện từ năm 2027", 15/09/2026: https://tienphong.vn/bo-cong-thuong-canh-bao-nguy-co-thieu-dien-tu-nam-2027-post1876576.tpo ; "Nguồn điện chậm tiến độ, lấy gì bù thiếu hụt?", 08/10/2026: https://tienphong.vn/nguon-dien-cham-tien-do-lay-gi-bu-thieu-hut-post1883163.tpo
- The Star/Bloomberg, "Vietnam's LNG power plans face massive delays", 07/10/2026: https://www.thestar.com.my/business/business-news/2026/10/07/vietnams-lng-power-plans-face-massive-delays
- The Investor, Nhơn Trạch 3-4 COD 05/01/2026: https://theinvestor.vn/vietnams-first-lng-power-plants-may-incur-38-mln-loss-in-2026-broker-d17870.html (chỉ dùng mốc COD)
- Tạp chí Công Thương / Thời báo TC, khởi công LNG Quảng Trạch II 20/10/2026: https://tapchicongthuong.vn/khoi-cong-nha-may-nhiet-dien-lng-quang-trach-ii-559538.htm ; https://thoibaotaichinhvietnam.vn/evn-khoi-cong-du-an-nha-may-nhiet-dien-lng-quang-trach-ii-205643.html ; EPC PowerChina–LILAMA: https://vietnamfinance.vn/lien-danh-powerchina-lilama-trung-thau-xay-nha-may-dien-khi-ty-usd-o-quang-tri-d140054.html
- PDP8 điều chỉnh, QĐ 768/QĐ-TTg, 15/04/2025 và nhu cầu vốn (tổng hợp báo chí): https://baolaocai.vn/thu-tuong-chinh-phu-phe-duyet-dieu-chinh-quy-hoach-dien-viii-post400323.html ; https://baodauthau.vn/dieu-chinh-quy-hoach-dien-viii-giai-bai-toan-von-cach-nao-post174422.html ; lưới 18,1 tỷ USD, EVN đáp ứng khoảng 40%: https://www.sggp.org.vn/tong-nhu-cau-von-dau-tu-luoi-dien-giai-doan-2025-2030-la-hon-18-ty-usd-post808390.html
- Báo Đấu thầu, gói 5 Krông Buk–TN1, 30/03/2026: https://baodauthau.vn/lien-danh-3-thanh-vien-trung-goi-thau-tu-van-dien-hon-158-ty-dong-tai-evnnpt-post196106.html ; Thốt Nốt–Đức Hòa, 01/04/2026: https://baodauthau.vn/du-an-6800-ty-dong-duong-day-500kv-thot-not-duc-hoa-day-nhanh-tien-do-chuan-bi-dau-tu-post196243.html ; Krông Buk–TN1 khoảng 14.060 tỷ: https://baodauthau.vn/lam-dong-chap-thuan-chu-truong-dau-tu-du-an-duong-day-500kv-krong-buk-tay-ninh-1-gan-14060-ty-dong-post202212.html ; "Phép thử năng lực nhà thầu", 24/07/2026: https://baodauthau.vn/tang-toc-dau-tu-du-an-truyen-tai-dien-phep-thu-nang-luc-nha-thau-post203420.html
- Vietnamplus/Báo Đấu thầu, HĐ tín dụng 15.600 tỷ mạch 3, 26/01/2026: https://www.vietnamplus.vn/ky-hop-dong-tin-dung-hon-15600-ty-dong-trien-khai-cac-du-an-duong-day-500kv-post923242.vnp ; Thạnh Mỹ–Quảng Trạch–Dốc Sỏi: https://vneconomy.vn/da-nang-chap-thuan-chu-truong-dau-tu-du-duong-day-500kv-mach-kep-tong-chieu-dai-hon-77-km-von-dau-tu-3850-ty-dong.htm
- EVN, "Ninh Thuan 1 Nuclear Power Project accelerates investment preparation steps", 12/05/2026: https://en.evn.com.vn/d/en-US/news/Ninh-Thuan-1-Nuclear-Power-Project-accelerates-investment-preparation-steps-60-202-501456 ; NucNet, IGA 03/2026: https://www.nucnet.org/news/russia-and-vietnam-sign-agreement-to-build-ninh-thuan-1-nuclear-plant-3-1-2026 ; Báo Đấu thầu, QH họp riêng 11/08/2026: https://baodauthau.vn/quoc-hoi-hop-thao-luan-ve-du-an-nha-may-dien-hat-nhan-ninh-thuan-post204742.html ; Tạp chí Công Thương, QH thông qua tách dự án: https://tapchicongthuong.vn/quoc-hoi-thong-qua-viec-tach-du-an-dien-hat-nhan-ninh-thuan-thanh-cac-du-an-doc-lap-544488.htm ; VOV, GPMB trễ hạn và khởi tố 4 bị can: https://vov.vn/kinh-te/khanh-hoa-lap-to-cong-tac-dac-biet-go-vuong-mat-bang-cac-du-an-dien-hat-nhan-post1321008.vov ; MoU Rosatom–PECC2 09/2025: https://vietnamnews.vn/economy/1726111/rosatom-pecc2-sign-mou-on-cooperation-in-nuclear-power-plant-project.html ; NQ 46/NQ-CP và QĐ 496/QĐ-TTg: https://tapchicongthuong.vn/thanh-lap-hoi-dong-tham-dinh-dieu-chinh-chu-truong-dau-tu-du-an-dien-hat-nhan-ninh-thuan-503011.htm
- Vietnam Finance, PVN–KEPCO NT2, 09/09/2026: https://vietnamfinance.vn/petrovietnam-va-kepco-day-nhanh-tien-trinh-dien-hat-nhan-ninh-thuan-2-d150334.html
- Tạp chí Công Thương, NĐ 272/2026/NĐ-CP, 07/07/2026: https://tapchicongthuong.vn/chinh-phu-quy-dinh-chi-tiet-mot-so-co-che--chinh-sach-phat-trien-nang-luong-giai-doan-2026-2030-531949.htm ; ĐGNK (vietnamplus): https://www.vietnamplus.vn/quy-dinh-moi-ve-dieu-kien-khao-sat-dau-tu-dien-gio-ngoai-khoi-post1122669.vnp ; PVN–CIP 22/10/2026 (solarquarter, trả 403, chỉ đọc qua tóm tắt tìm kiếm): https://solarquarter.com/2026/10/22/vietnam-and-denmarks-cip-plan-4-billion-investment-in-1000-mw-offshore-wind-project/ ; VinEnergo 06/02/2026: https://www.oedigital.com/amp/news/535377-germany-s-pne-loses-bid-for-vietnam-s-offshore-wind-project ; giao khu vực biển 01/2026: https://theinvestor.vn/vietnam-allocates-sea-areas-to-state-giants-for-offshore-wind-surveys-d18218.html
- DPPA đầu tiên và NĐ 243/2026: https://tapchicongthuong.vn/dau-moc-moi-cua-thi-truong-dien--giao-dich-mua-ban-dien-truc-tiep--dppa--dau-tien-duoc-xac-lap-522663.htm
- Giá điện NĐ 278/2026 (09/07/2026): https://vietnamfinance.vn/siet-lai-quy-trinh-tang-gia-dien-evn-khong-the-tu-dieu-chinh-tu-2-tro-len-d147425.html ; https://doanhnhan.baophapluat.vn/quy-dinh-moi-ve-gia-ban-le-dien-giam-duoi-1-tang-duoi-2-khong-dieu-chinh-18a4e1a4.html ; lỗ luỹ kế khoảng 44.700 tỷ (05-07/2026): https://tuoitre.vn/bo-cong-thuong-muon-co-co-che-phan-bo-khoan-lo-cua-evn-vao-gia-dien-2026051410413268.htm
- Luật Điện lực sửa đổi, trình 20/10/2026 (cổng BCT, qua tóm tắt tìm kiếm): https://moit.gov.vn/tag/Luật%20Điện%20lực%20sửa%20đổi ; UBTVQH cho ý kiến 21/09/2026: https://tapchicongthuong.vn/uy-ban-thuong-vu-quoc-hoi-cho-y-kien-ve-du-an-luat-sua-doi--bo-sung-mot-so-dieu-cua-luat-dien-luc-551777.htm
- NQ 253/2025/QH15 (văn bản): https://vbpl.vn/TW/Lists/vbpq/Attachments/186009/Nq%20253.docx ; diễn đàn QH 04/10/2026 về tiêu chí dự án cấp bách: https://daibieunhandan.vn/lam-ro-tieu-chi-du-an-quan-trong-cap-bach-10399680.html
- Định mức: TT 38/2026/TT-BXD và NĐ 206/2026/NĐ-CP (thuvienphapluat, tóm tắt): https://thuvienphapluat.vn/phap-luat-nha-dat/thong-tu-382026ttbxd-ban-hanh-dinh-muc-xay-dung-tu-172026-moi-nhat-17210.html ; VBHN 36/2026 Phụ lục VIII: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/6/36-vbhn-bxd.pdf
- Đại biểu Nhân dân, "EVN đặt yêu cầu cao hơn với hoạt động tư vấn dự án điện", 22/03/2026: https://daibieunhandan.vn/evn-dat-yeu-cau-cao-hon-voi-hoat-dong-tu-van-du-an-dien-10410776.html ; Diễn đàn DN, 01/04/2026: https://diendandoanhnghiep.vn/evn-nang-cao-chat-luong-tu-van-dau-tu-xay-dung-10177404.html
- QĐ 852/QĐ-TTg (2017), thoái vốn PECC3/PECC4 (tin cũ): https://tapchicongthuong.vn/evn-se-thoai-von-tai-5-cong-ty-co-phan-54775.htm
