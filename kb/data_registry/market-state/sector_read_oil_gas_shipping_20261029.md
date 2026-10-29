---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-10-29. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp vận tải biển dầu khí cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành vận tải biển chuyên dụng dầu khí VN (tàu dầu thô, dầu sản phẩm, LPG, hoá chất; phần lớn thuê định hạn cho tập đoàn dầu khí/lọc hoá dầu, phần còn lại chạy giao ngay quốc tế). Gồm pipeline cầu nội địa, cấu trúc cạnh tranh, phân loại chế độ ngành + vị trí chu kỳ cước tanker, FORECAST khoá trước, checklist DD.
as_of: 2026-10-29 (cước tới 23/10/2026; BQ tới 28/10; tin web ≤ 2026-10-28)
---

# SECTOR READ: Vận tải biển chuyên dụng dầu khí VN, as-of 29/10/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Đã đọc:** `sector_read_fertilizer_dap_20261028.md` (mẫu định dạng + bối cảnh Hormuz đã có nguồn, dùng lại ở mục 3),
  `sector_read_power_consulting_20261028.md` (60 dòng đầu, mẫu), `feeds/bdi_daily.md`, `feeds/vcb_fx_rate.md`, phần đầu
  `vn_macro_regime_history.md` để thêm con trỏ.
- **BQ (tự truy vấn 29/10):** `tav2_bq.commodity_prices` `source='trading_economics'`, `cadence='daily'`: `brent`, `crude_oil`,
  `urals_oil`, `te_crack_spread_index`, `propane`, `naphtha`, `gasoline`, `heating_oil`. **BQ KHÔNG có chuỗi cước tàu dầu nào
  (không BDTI/BCTI/VLGC)**, chỉ có `baltic_dry` (hàng rời, không liên quan). Đây là **khoảng trống dữ liệu**, báo Mike/Winston,
  không tự sửa. Local: `data/vcb_fx_rate.csv` (USD/VND).
- **Ghi chú trung thực (web lộ thông tin ở cấp DN):** khi tìm kiếm, tiêu đề/snippet của kết quả có lộ:
  (a) tiêu đề một ghi chú CTCK (Vietcap) về một mã vận tải dầu khí VN, nói "Hormuz-driven tailwinds… 2027 rate normalization
  expected"; trình tóm tắt tìm kiếm còn chép ra một con số "cước tanker giảm khoảng 30% YoY". **Không mở, không dùng con số đó.**
  Forecast ở mục 4 dựng từ Optima/Baltic, Lloyd's List, BIMCO, Breakwave. Rủi ro neo (anchoring) vẫn có, nên ghi ra đây.
  (b) tên một tàu của DN trong nước trong tiêu đề bài về phao rót dầu Dung Quất; (c) tiêu đề về một DN thuộc VIMC đặt 2 tàu
  sản phẩm 47-50k dwt ở Hàn Quốc, tiêu đề ĐHĐCĐ 2026 của DN đó ("mục tiêu lợi nhuận đi lùi"), và câu "không đầu tư, đội tàu
  sẽ già hoá". Tôi dùng (c) chỉ ở cấp **cấu trúc** (có đơn vị đang thay tàu), không dùng số lợi nhuận. (d) Link PDF CTCK
  về PV GAS: **không mở**.
- **Không đọc:** `kb/projects/*`, `agents/Taylor/*`. Không tra giá cổ phiếu, BCTC hay khuyến nghị CTCK của DN vận tải nào.
- **Chi phí vốn VN:** lượt này **không đọc**, nên không lấp bảng 5 tầng lãi suất và không kết luận gì về lãi suất VND. Chỉ ghi
  tỷ giá (mục 3.4) vì nó trực tiếp vào nợ USD của ngành.

## 1. Pipeline cầu [DK trừ khi ghi khác]
Cầu của ngành có **hai tầng tách biệt**, phải đọc riêng:
**(i) nội địa / cabotage** (dầu thô mỏ → Dung Quất, sản phẩm từ 2 nhà máy lọc dầu ra kho ven biển, LPG phân phối ven biển,
thuê định hạn cho tập đoàn) và **(ii) quốc tế** (NK dầu thô cho Nghi Sơn, NK sản phẩm/LPG, tàu chạy giao ngay ngoài nước).

| Hạng mục | Số liệu as-of | Đọc |
|---|---|---|
| **Dung Quất** (TK 6,5 tr t dầu thô/năm) | Q1/2026 chạy **123,5%** công suất quy đổi. 7T bình quân khoảng **124%**. Mục tiêu sản lượng kỷ lục **8,3 tr t** năm 2026 (Tuổi Trẻ 30/03/2026). Dầu thô chủ yếu **trong nước** (Rạng Đông, Bạch Hổ, Chim Sáo, Sư Tử Đen) qua phao rót không bến | Khối lượng tàu con thoi dầu thô nội địa + chở sản phẩm ven biển đang ở mức **trần kỹ thuật**. Còn ít dư địa tăng trước khi mở rộng |
| **Dung Quất mở rộng** | EPC Chengda–BPE ký **09/07/2026**, PMC Foster Wheeler. Gói EPC khoảng 988 tr–1,21 tỷ USD (2 nguồn lệch). Thời gian thực hiện **37 tháng** từ hiệu lực EPC (tức khoảng **T8/2029**), dù có nguồn ghi "vận hành 2028". GPMB 52% cuối T6/2026 | Bước tăng khối lượng nội địa tiếp theo **không trước 2029** [UĐ: 37 tháng mâu thuẫn với "2028"; tin 2029] |
| **Nghi Sơn** (TK 10 tr t, 200k thùng/ngày) | KH 2026 nhập khoảng **12,5 tr t dầu thô**. HĐ dài hạn Kuwait chiếm **khoảng 85%** nhu cầu ở công suất thiết kế. Từ cuối T3 đến hết T8 gần như **không có dầu Kuwait**. Đáy là 75-80% công suất trong khoảng 1 tháng. Từ T5 hồi phục, nay **khoảng 125%**. T9 Kuwait nối lại **3 chuyến, khoảng 6 tr thùng**. Nguyên liệu T10-T11 đã đủ, T12 đến đầu năm sau đang chốt (Tiền Phong 02/10/2026). Nguồn thay thế: Das Blend UAE, Basra Iraq (lô 2 tr thùng về 31/05), Idemitsu thu xếp khoảng 4 tr thùng không qua Hormuz (28/07). Ngày 13/05 PVOIL phải xin Hải quân Mỹ cho một VLCC chở Basra đi qua vùng phong toả (Marine Insight 13/05) | Đây là **cầu tàu dầu thô quốc tế** (VLCC/Suezmax, chủ yếu tàu nước ngoài [NỀN]). Phần đội tàu VN hưởng trực tiếp là nhỏ [UĐ]. Nhưng nó cho thấy rủi ro cung đầu vào |
| **Khai thác dầu thô trong nước (PVN)** | 9T/2026: **6,66 tr t, +10,4% YoY** (Đại biểu Nhân dân 06/10/2026) | Nguồn hàng tàu con thoi/tàu dầu thô nội địa tăng nhẹ. Cấu trúc dài hạn vẫn là mỏ suy giảm [NỀN] |
| **NK xăng dầu (sản phẩm)** | 4T/2026: **4,13 tr t, +28,7%**. Diesel 2,19 tr t (+45,7%), xăng 1,04 tr t (+27,5%). Tới khoảng giữa T7: 5,84 tr t (mốc ngày chưa chắc) | NK sản phẩm tăng vọt để bù thiếu hụt nhà máy. Hàng NK từ TQ/TL/SG thường là MR/LR1 khu vực [NỀN] |
| **NK dầu thô** | 4T/2026: **3,79 tr t, −23,2%** về lượng (Hải quan qua Thời báo Tài chính, khoảng T5/2026). Chưa có số 9T | Giảm do Nghi Sơn mất nguồn Kuwait trong Q2 |
| **NK LPG** | 4T/2026: **1,3 tr t, +34,5%**. Trước chiến tranh khoảng **70%** LPG NK từ Trung Đông. PV Gas Trading ra thông báo bất khả kháng ngày 02/03. PV GAS chuyển sang LPG Mỹ: 76k t trong T4, dự kiến khoảng 100k t/tháng T5-T6 (Q2 trên 300k t), và nói **không kỳ vọng quay lại khối lượng Trung Đông như trước** (FMT/Bloomberg 28/04/2026) | Hành trình dài hơn (Mỹ–VN) cho VLGC. Phần phân phối ven biển (tàu LPG nhỏ) vẫn là cabotage |
| **Tổng nguồn xăng dầu tối thiểu 2026** | **31,8 tr m³/tấn** (BCT), khoảng 2,65 tr/tháng. E10 phối trộn từ **01/06/2026** | Cầu nội địa tăng theo GDP. E10 thay một phần nhỏ xăng khoáng [UĐ: tác động khối lượng tàu không đáng kể] |
| **Long Sơn (hoá dầu)** | Không xác minh được trạng thái 2026 trong lượt này | Ô trống. Nếu chạy thì đây là nguồn cầu LPG/naphtha NK lớn |

**Đọc tổng hợp [UĐ]:** cầu **nội địa** năm 2026 ở mức **cao kỷ lục nhưng ở trần kỹ thuật** (2 nhà máy đều chạy khoảng 125%).
Đến hết 2027 không có công suất lọc dầu mới nào. Vì vậy khối lượng cabotage 2027 gần như **đi ngang**, với rủi ro lệch
xuống nếu nhà máy bảo dưỡng tổng thể (lịch TA chưa xác minh). Biến số lớn nằm ở tầng **quốc tế**: giá cước và chi phí
nhiên liệu tàu.

## 2. Cấu trúc cạnh tranh
- **Hàng rào pháp lý [DK + NỀN]:** Bộ luật Hàng hải 2015 dành vận tải nội địa cho tàu mang cờ VN. Tàu nước ngoài chỉ được
  chạy nội địa khi có giấy phép (thủ tục mới nhất: Thông tư 41/2025/TT-BXD, Điều 9; trước đó là TT 50/2016 và VBHN 29/2022).
  Tổ chức nước ngoài tham gia vận tải nội địa phải qua liên doanh, vốn nước ngoài **≤49%** (Trung tâm WTO, tài liệu tư vấn).
  Chính sách hỗ trợ đội tàu: miễn VAT khi NK tàu biển cho chủ tàu VN **đến hết 2026**; giảm ít nhất 10% phí hoa tiêu cho tàu
  cờ VN (03/2026). Bộ luật đã sửa năm 2023 và 2025, nên **cần kiểm bản hiện hành** trước khi trích điều khoản.
- **Số đối thủ [NỀN, chưa kiểm lại]:** nhóm có tàu dầu/LPG/hoá chất đi biển đáng kể khoảng **4-6 nhóm**: (1) mảng vận tải của
  tập đoàn dầu khí quốc gia (dầu thô, sản phẩm, LPG, FSO/FPSO), (2) mảng vận tải của tập đoàn xăng dầu bán lẻ nhà nước (2 đơn
  vị, chủ yếu sản phẩm cho công ty mẹ), (3) mảng tàu sản phẩm của tổng công ty hàng hải nhà nước (4 tàu 47-50k dwt, đang đặt
  thêm 2), (4) vài chủ tàu tư nhân/đầu mối xăng dầu nhỏ có tàu ven biển. **Cấu trúc: oligopoly gắn với chủ hàng**. Thị phần
  từng mảng **không có số trong lượt này**.
- **Sức mạnh đàm phán của khách hàng [UĐ]:** **cao**. Khách hàng chính là doanh nghiệp nhà nước, thường cùng hệ sinh thái với
  chủ tàu (công ty mẹ/anh em), nên giá thuê định hạn nội bộ **không bám** giá cước quốc tế khi cước tăng vọt. Đổi lại, khối
  lượng được bảo đảm khi cước sụp. Đây là **bảo hiểm hai chiều**: cắt đuôi trên và đỡ đuôi dưới.
- **Rủi ro gia hạn hợp đồng dài hạn [UĐ]:** năm 2026-27 thị trường đang ở đỉnh, nên hợp đồng đáo hạn lúc này **có lợi cho
  chủ tàu** nếu được gia hạn theo giá thị trường. Nhưng với khách hàng cùng hệ thống, giá gia hạn mang tính hành chính/đàm
  phán nội bộ. Rủi ro thật nằm ở chiều ngược lại: nếu ký TC dài **ở đỉnh** cho khách hàng **ngoài hệ thống**, khách hàng có thể
  đòi đàm phán lại khi cước giảm (rủi ro đối tác). Đội tàu già (mục 3.3) còn có rủi ro **khách hàng quốc tế từ chối tàu >15-20
  năm tuổi** (vetting của các hãng dầu lớn) [NỀN].
- **Tuổi đội tàu:** toàn đội tàu biển VN khoảng **16,5 năm** (nguồn không ghi năm); nhóm tàu dầu/hoá chất khoảng **17,7 năm**
  (2020: 17,6) [DK, ngày mờ]. Tham chiếu thế giới: tàu sản phẩm bình quân **khoảng 14 năm**, khoảng **20% dung tích ≥20 năm**
  (BIMCO qua Hellenic Shipping News, 2025). Đội tàu VN **già hơn** thế giới khoảng 3 năm [UĐ, so khác năm].

## 3. Phân loại chế độ ngành + vị trí chu kỳ

### 3.1 Mức cước hiện tại (đa proxy) [DK]
| Chuỗi | Hiện tại | Mốc so sánh | Nguồn |
|---|---|---|---|
| **BDTI** (Baltic Dirty Tanker Index) | **7.171** (23/10) | [NỀN] 2023-25 khoảng 900-1.400; đỉnh 2022 khoảng 2.400 | Optima 26/10 |
| VLCC TCE composite | **761.352 USD/ngày** (23/10). TD3C MEG–TQ **1,29 tr USD/ngày** | Lloyd's 19/10: Oman–TQ 790k, **−13%** từ đỉnh đầu T10; USG–TQ −19% từ đỉnh mọi thời đại. [NỀN] bình thường 40-60k | Optima 26/10; Lloyd's List 19/10 |
| Suezmax TCE | 638.377 (23/10). Biển Đen–ĐTH 872k (phí chiến tranh Nga–Ukraine) | WAF–Âu −16% từ đỉnh | Optima; Lloyd's |
| **Aframax TCE** | 336.059 (Optima 23/10); rổ Baltic **kỷ lục 385.000** (BRS 26/10) | USG–Âu **−39%** từ đỉnh 06/10. Thái Bình Dương **mạnh hơn** Đại Tây Dương | Optima; Riviera 28/10; Lloyd's |
| **TD14 Aframax ĐNÁ–Đông Úc** (gần VN nhất) | **229.049** (23/10); 19/10: 256k, −6% từ kỷ lục | — | Optima; Lloyd's |
| TD8 Aframax Kuwait–Singapore | 424.906 | — | Optima |
| LR2 MEG–Nhật (sạch) | **kỷ lục 320.000/ngày** | XK sản phẩm sạch Trung Đông T9 khoảng **1 tr thùng/ngày**, so với khoảng 4 tr trước 28/02 | Riviera 28/10 |
| MR MEG–Nhật (sạch) | **WS970 (217,38 USD/t), kỷ lục** (15/10) | 113 LR2 chuyển từ sạch sang bẩn trong T1-T8/2026 (cả 2025: 67) | Argus 15/10 |
| TC 1 năm VLCC | 114k (cuối T7, Riverlake). Khoảng 200k cuối T9 (nguồn thứ cấp, **độ tin thấp**). TC 3 năm khoảng 100k | — | Riverlake tuần 31; Breakwave qua trang thứ cấp |
| VLGC (LPG) | Giao ngay tới **150.000/ngày** (21/08). **Không có số T10** | Drewry trước khủng hoảng dự báo TC 2026 khoảng 40k | India Seatrade 21/08; Drewry |
| Giá tàu cũ | T9 tăng MoM: tàu 5 tuổi +27%, 10 tuổi +37%, 15 tuổi +36%, 20 tuổi +34%. VLCC 5 tuổi 178 tr USD (KOBC 01/10). VLCC đóng 2006 bán lại khoảng 117 tr | — | Riviera 28/10; Xclusiv/KOBC |
| Nhiên liệu tàu Singapore | HSFO 887, **VLSFO 959**, LSMGO 1.358 USD/t (23/10) | [NỀN] VLSFO 2024-25 khoảng 550-650 | Optima |
| Brent / Urals (BQ, TB tháng) | Brent T10 **106,65** (max 116,7); Urals T10 **114,71**, tức **Urals > Brent** | TB T1-T2/2026: Brent 64,6-69,4; Urals 54,6-56,5 | BQ |
| Crack spread TE (BQ) | TB T10 **62,1** (T9 66,0, max T9 75,3) | TB 2025 khoảng 22-29 | BQ |
| Propane TE (BQ) | TB T10 **1,05 USD/gal** (max 1,21) | T7-T8 0,72-0,74 | BQ |

**Phân kỳ quan trọng [UĐ]:** (1) **Giao ngay đã qua đỉnh** (VLCC −13 đến −19%, Aframax Đại Tây Dương −39% từ đầu T10).
Trong khi đó **TC 1 năm và giá tàu cũ vẫn đang tăng** (số T9). Đó là dấu hiệu giai đoạn **cuối đỉnh**: tài sản và hợp đồng
kỳ hạn luôn trễ giao ngay. (2) **Tàu bẩn ≫ tàu sạch về mức**, nhưng tuyến sạch MEG–Nhật lập kỷ lục vì LR2 bị hút sang bẩn.
(3) **Urals cao hơn Brent** trong T10 (BQ) là bất thường so với chiết khấu khoảng 10-15 USD thời 2023-25. Dầu Nga đang được
trả giá cao vì không đi qua Hormuz. Tôi **không** suy ra rằng trừng phạt đã gỡ (Mỹ nói "không gỡ", Lloyd's 19/10).

### 3.2 Nguyên nhân gốc (trục 1) và có khoanh được không (trục 2)
- **Trục 1:** cước đỉnh là **cú sốc cung ngoại sinh** (Hormuz đóng thực tế từ 02-05/03/2026; 3 lần ngừng bắn đổ vỡ; tháng
  10 vẫn có tàu dầu bị tấn công; xem file phân bón 28/10, mục 2), chồng lên **chu kỳ vốn đã chặt từ trước** (đội tàu già, đóng
  mới ít giai đoạn 2021-23, đội tàu bị trừng phạt bị phân mảnh, Biển Đỏ). Nó **không** phải mất cân đối vĩ mô VN.
  Cơ chế: tàu bị kẹt và phải chờ, chuyển tải STS (11-12 tr thùng/ngày, gấp đôi đầu T9), tuyến dài hơn, tách hàng VLCC thành
  lô Aframax, phí bảo hiểm chiến tranh. Tất cả đều là **mất năng suất đội tàu**, không phải cầu dầu tăng.
- **Trục 2: KHÔNG khoanh được bởi VN.** Muốn giải quyết cần thoả thuận Mỹ–Iran. Nhịp ngành là `EXTERNAL_CYCLE`. Điểm quan
  trọng [DK BIMCO 31/08 + Breakwave 04/09]: **cả hai nhánh đều kéo cước về thấp hơn mức hiện tại trong 2027**, chỉ khác đường đi.
  · **Mở eo:** cầu tàu dầu thô 2027 **+6,5 đến +8,5%**, nhưng tháo bỏ STS/đường vòng/phí rủi ro, cộng cung tàu **+5 đến +6%**.
    Cước **bình thường hoá dần**. Lưu ý: ngay sau khi mở có thể có **vài tháng cước còn cao** do lượng hàng dồn và nhu cầu bổ
    sung tồn kho (tồn kho dầu toàn cầu đã giảm hơn 500 tr thùng).
  · **Eo vẫn hạn chế:** BIMCO ước cầu tàu dầu thô **−11 đến −13% (2026), thêm −8,5 đến −10,5% (2027)**, vì XK vùng Vịnh giảm
    và cầu dầu bị huỷ. Kém hiệu quả vẫn đỡ cước, nhưng "đây không phải kịch bản tăng vô hạn" (Breakwave).
  · **Cung:** năm 2027 giao 62 VLCC, 56 Suezmax, 88 Aframax (Clarksons qua Breakwave). Sổ đặt VLCC khoảng **35%** đội tàu,
    phần lớn giao 2028-29. Sổ đặt tàu sản phẩm khoảng 19% đội tàu (BIMCO, số cũ), giao tàu sản phẩm lên đỉnh 2026-27. Riêng năm
    2026 đã có 62 LR2 mới ra thị trường.

### 3.3 Địa chính trị
- **Hormuz:** biến số số 1 (xem trên). Lloyd's: "new normal của Hormuz sẽ không giống cũ". Sparta: eo "bị tranh chấp, hạn chế,
  chưa đóng hẳn".
- **Biển Đỏ:** Houthi phong toả tàu liên quan đến Ả Rập Xê Út. Qua Suez T9/2026 có **1.228 lượt (+21% YoY, nhưng vẫn −39%** so
  với trước khủng hoảng). Dầu Ả Rập Xê Út chuyển tuyến qua phía bắc làm tăng lượt tàu dầu qua Suez (LLI 01/10 và 15/10).
  Tác động: tuyến dài, hỗ trợ cước. Với VN: ít trực tiếp, nhưng giữ cước Á–Âu cao.
- **Trừng phạt / đội tàu bóng tối:** Mỹ dự định đưa "hàng chục đến hàng trăm" tàu bị trừng phạt vào thương mại hợp pháp (Bộ
  trưởng Năng lượng Wright). Clarksons: khoảng một nửa VLCC bị trừng phạt đang chứa dầu, nằm không hoặc hư hỏng. Môi giới cho
  rằng ít tác động trừ khi Anh/EU cũng nới (Lloyd's 19/10). **Rủi ro cung tàu tiềm ẩn cho 2027** [UĐ]: nếu nới thật, đội tàu
  bóng tối già vào lại thị trường chính thức đúng lúc tàu đóng mới đổ về.
- **Nga–Ukraine:** phí chiến tranh Biển Đen (Suezmax TD6 872k) không liên quan trực tiếp tới VN.

### 3.4 Tỷ giá (chỉ phần chạm nợ USD) [DK BQ local]
VCB bán USD: **26.463 (03/07/2026) đến 26.040 (29/10/2026)**, tức VND **tăng khoảng 1,6%**. Với chủ tàu có doanh thu USD và nợ
vay USD: lãi đánh giá lại nợ, nhưng doanh thu quy đổi giảm nhẹ. Không kết luận gì về lãi suất VND (xem mục 0).

### 3.5 KẾT LUẬN PHÂN LOẠI
**Nhãn chi phối lợi nhuận biên của ngành tới hết 2027 (các nhãn không loại trừ nhau, xác suất là nhãn nào CHI PHỐI):**
| Nhãn | P | Lý lẽ |
|---|---|---|
| **CYCLICAL** (đỉnh cấp tính do cú sốc ngoại sinh; giao ngay đã qua đỉnh, hợp đồng/tài sản còn trễ) | **0,55** | Mức cước gấp 5-15 lần bình thường, đến từ mất năng suất chứ không từ cầu. Cả 2 nhánh BIMCO đều kéo cước về trong 2027. Cung tàu +5-6%/năm |
| **ADMIN_GATED** (phần nội địa: cabotage + thuê định hạn trong hệ sinh thái nhà nước, giá đàm phán nội bộ) | **0,30** | Với DN VN có tỷ trọng TC nội địa cao, lợi nhuận **ít nhạy** cước quốc tế ở cả hai chiều. Khối lượng ở trần kỹ thuật tới 2029 |
| **STRUCTURAL** (nền cước dài hạn cao hơn trước chiến tranh: Hormuz "new normal", phân mảnh do trừng phạt, đội tàu già + quy định khí thải IMO) | **0,15** | Có lý lẽ nhưng bị cung tàu đóng mới 2026-29 và nguy cơ đội tàu bóng tối quay lại phản biện |

**Vị trí chu kỳ: "cuối đỉnh" (late-peak).** Giao ngay đã giảm từ đỉnh 06/10 nhưng vẫn ở mức lịch sử. TC kỳ hạn và giá tàu cũ
còn tăng tới T9. Độ tin cậy **ambiguous** khoảng 65/35 (đỉnh đã qua hay chỉ là nhịp điều chỉnh trong đỉnh kéo dài). Lý do:
Iran tấn công dày lên và K3 (leo thang) vẫn mở.

**Hệ quả với DN VN [UĐ, không phải khuyến nghị]:** lợi nhuận 2026 phụ thuộc gần như hoàn toàn vào **tỷ trọng giao ngay quốc
tế**, cộng **lãi thanh lý tàu cũ ở giá kỷ lục** (một lần, không lặp lại). Rủi ro 2027: cước giao ngay về lại, **chi phí tàu
mua/đóng ở đỉnh** chuyển thành khấu hao cao nhiều năm, và hợp đồng TC ký đỉnh có rủi ro đối tác.

## 4. FORECAST KHOÁ TRƯỚC (lập 2026-10-29; chấm theo quan sát cuối cùng ≤ ngày kiểm)
**Proxy chấm điểm chính:** chỉ số Baltic công bố hằng ngày (đọc qua bản tóm tắt "Dirty Tanker Index Summary" của Optima
Shipbroking hoặc Baltic Exchange). Mốc gốc ngày 23/10/2026: **BDTI 7.171; VLCC TCE 761.352; Aframax TCE 336.059; TD14
229.049**. Proxy sạch: Argus MR MEG–Nhật **WS970** (15/10). BQ **không có** chuỗi nào để chấm (mục 0), nên Mike/Bobby phải
tra web vào ngày chấm.

Ba kịch bản đứng sau phân phối (đồng bộ với file phân bón 28/10) [UĐ]:
- **K1, Hormuz còn tranh chấp/hạn chế tới hết Q1/2027 (p ≈ 0,55):** cầu dầu thô giảm, kém hiệu quả vẫn đỡ. BDTI 3.500-6.500.
- **K2, thoả thuận thật trước giữa T1/2027 (p ≈ 0,30):** có vài tuần đến vài tháng hàng dồn, sau đó STS/phí rủi ro bị tháo.
  BDTI về 2.000-4.000 vào cuối Q1, 1.300-2.500 vào Q3/2027.
- **K3, leo thang, đánh vào hạ tầng vùng Vịnh (p ≈ 0,15):** BDTI > 7.500, cước trồi lại.

| ID | Mốc | Chuỗi (gốc) | Dự báo |
|---|---|---|---|
| F1 | **2027-03-31** | BDTI (7.171) | Trung vị **khoảng 4.200**, 80% trong **2.200-8.000**. **P(<7.171) = 0,78**; P(<5.000) = 0,60; P(<3.000) = 0,25 |
| F2 | **2027-09-30** | BDTI (7.171) | Trung vị **khoảng 2.800**, 80% trong **1.400-6.500**. **P(<7.171) = 0,88**; P(<4.000) = 0,68; P(<2.000) = 0,28 |
| F3 | 2027-03-31 | Aframax TCE composite (336.059) | Trung vị khoảng 180k. **P(<336k) = 0,75**; P(<150k) = 0,40 |
| F4 | 2027-09-30 | Aframax TCE composite (336.059) | Trung vị khoảng 110k. **P(<336k) = 0,85**; P(<100k) = 0,45 |
| F5 | 2027-03-31 / 2027-09-30 | TD14 ĐNÁ–Đông Úc TCE (229.049) | P(thấp hơn gốc) = **0,72 / 0,82** |
| F6 | 2027-03-31 / 2027-09-30 | VLCC TCE composite (761.352) | P(thấp hơn gốc) = **0,80 / 0,88** |
| F7 | 2027-03-31 / 2027-09-30 | Argus MR MEG–Nhật (WS970), **độ tin thấp vì nguồn chấm khó truy cập** | P(thấp hơn gốc) = **0,70 / 0,80**. Không chấm được thì VOID |
| F8 | 2027-09-30 | TC 1 năm VLCC (gốc khoảng 200k cuối T9, nguồn yếu) | P(thấp hơn) = 0,70. Phụ, VOID nếu không có báo giá broker cùng phương pháp |
| D1 | công bố khoảng T1/2027, chấm trước **2027-03-31** | Sản lượng sản xuất năm 2026 Dung Quất (mục tiêu 8,3 tr t) | **P(≥ 8,0 tr t) = 0,65** |
| D2 | chấm trước **2027-03-31** | NK **LPG** cả năm 2026 so với 2025, về lượng (Hải quan) | **P(tăng) = 0,70** |
| D3 | chấm trước **2027-03-31** | NK **dầu thô** cả năm 2026 so với 2025, về lượng (Hải quan) | **P(giảm) = 0,55** (4T −23%; Nghi Sơn hồi 125% từ T5, Kuwait nối lại T9) |
| D4 | chấm trước **2027-03-31** | NK **xăng dầu thành phẩm** cả năm 2026 so với 2025, về lượng | **P(tăng) = 0,75** |
| D5 | **2027-09-30** (số 9T/2027 của Cục Hàng hải, công bố khoảng T10/2027; chưa có thì chấm 8T) | Khối lượng **hàng lỏng** thông qua cảng biển VN 9T/2027 so với 9T/2026 | **P(tăng) = 0,55**. Lý do: nền 2026 cao vì 2 nhà máy chạy khoảng 125% và NK sản phẩm tăng vọt; năm 2027 không có công suất mới |
| D6 | **2027-09-30** | Nghi Sơn vẫn được báo vận hành ≥ 100% công suất thiết kế (tin gần nhất trước mốc) | **P = 0,65**. Không có tin thì VOID |

**Câu phân loại:** CYCLICAL đúng nếu **BDTI ≤ 3.500 vào 2027-09-30**: P = **0,58**.
STRUCTURAL đúng nếu **BDTI ≥ 3.000 bền suốt Q3/2027** sau khi Hormuz đã mở lại ≥ 2 quý: P = **0,15**.

## 5. Chỉ báo dẫn dắt (theo dõi)
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu bình thường hoá ⇔ kéo dài/leo thang |
|---|---|---|---|
| 1 | Trạng thái Hormuz: lượt tàu dầu qua eo, số tàu chờ, phí war-risk, đàm phán Mỹ–Iran (tuần) | JMIC, LLI brief, straits.live, Kpler | Có thoả thuận + lượt qua bền 4 tuần ⇔ tấn công tiếp diễn, tàu chờ > 400 |
| 2 | Khối lượng STS và tách hàng VLCC sang Aframax (tuần) | Lloyd's, BRS, Kpler | STS < 8 tr thùng/ngày ⇔ > 12 tr |
| 3 | TC 1 năm theo hạng tàu + giá tàu cũ (tháng) | Broker weekly (BRS, Clarksons, Alibra/Seatrade), KOBC, Xclusiv | TC 1 năm giảm 2 tháng liên tiếp = đỉnh tài sản ⇔ còn tăng |
| 4 | Giao tàu mới + phá dỡ + chính sách đội tàu bị trừng phạt (tháng/sự kiện) | BIMCO, Clarksons, Lloyd's | Anh/EU nới trừng phạt, phá dỡ tăng ⇔ đội tàu bóng tối bị siết |
| 5 | Nguồn dầu thô Nghi Sơn + NK LPG/xăng dầu VN theo tháng | Hải quan, PV GAS, NSRP, BCT | Kuwait đủ 85% HĐ, NK sản phẩm hạ ⇔ NSRP phải tìm nguồn lại |
| phụ | Brent/Urals, crack spread, propane (ngày) | BQ `commodity_prices` TE daily | Crack < 35 ⇔ > 60 |
| phụ | VLSFO Singapore (chi phí nhiên liệu chủ tàu khi chạy chuyến) | Optima/Ship&Bunker | < 700 ⇔ > 950 |

## 6. DD cần kiểm gì (một DN vận tải biển dầu khí VN)
**A. Cơ cấu doanh thu & độ nhạy cước**
1. Tỷ trọng doanh thu/số ngày tàu **thuê định hạn (TC) / thuê chuyến (voyage) / giao ngay quốc tế / COA**, theo từng loại tàu
   (dầu thô, sản phẩm, LPG, hoá chất, FSO/FPSO). Đây là biến **quan trọng nhất**: nó quyết định DN hưởng bao nhiêu phần trong
   mục 3.1.
2. Danh sách hợp đồng TC: khách hàng, **ngày đáo hạn**, giá ngày (nếu công bố), điều khoản điều chỉnh giá, quyền gia hạn của
   khách. **Bao nhiêu % đội tàu đáo hạn trong 2026-27** (gia hạn ở đỉnh hay rơi vào giai đoạn cước về lại).
3. Tỷ trọng khách hàng **cùng hệ thống** (công ty mẹ/anh em) so với ngoài hệ thống; các giao dịch bên liên quan (thuyết minh
   BCTC); tập trung khách hàng (top-3).
4. Doanh thu theo vùng: nội địa (cabotage) và quốc tế; tỷ lệ tàu chạy cho hãng dầu lớn quốc tế (cần qua vetting).
**B. Đội tàu & capex**
5. Bảng đội tàu: số tàu, dwt, **năm đóng từng tàu**, tuổi bình quân (gia quyền theo dwt), cờ, tình trạng thuê.
6. **Lịch lên đà (dry-dock) và kiểm định đặc biệt** 2026-28: số ngày off-hire dự kiến, chi phí; chính sách hạch toán (vốn hoá
   rồi khấu hao hay chi phí ngay).
7. Kế hoạch **đóng mới/mua tàu cũ**: giá mua so với giá tàu cũ T9-T10/2026 (mua ở đỉnh?), lịch giao, nguồn vốn, ưu đãi miễn VAT
   NK tàu (hết hạn cuối 2026, nên có thể có động cơ dồn mua trước 31/12/2026).
8. **Thanh lý tàu cũ:** lãi thanh lý theo năm, tách khỏi lợi nhuận cốt lõi. Lãi thanh lý ở giá kỷ lục 2026 là **một lần**.
9. Khấu hao: thời gian sử dụng ước tính, giá trị thu hồi (scrap), có thay đổi ước tính kế toán nào không; kiểm tra **suy giảm
   giá trị** khi cước về lại (thử nghiệm impairment 2027-28).
10. Tuân thủ CII/EEXI, chi phí nâng cấp; rủi ro **khách từ chối tàu >15-20 tuổi**.
**C. Tài chính & tỷ giá**
11. Nợ vay theo **đồng tiền** (USD/VND), **lãi suất cố định hay thả nổi** (SOFR + biên), lịch trả gốc, covenant.
12. Lãi/lỗ **chênh lệch tỷ giá** đã và chưa thực hiện; doanh thu USD tự phòng ngừa nợ USD đến đâu; VND tăng giá 1,6% từ T7.
13. Chi phí lãi vay / EBITDA, nợ ròng / EBITDA ở **cước chuẩn hoá** (không phải cước 2026).
14. Tiền mặt, cổ tức, kế hoạch dùng lợi nhuận đỉnh (trả nợ hay mua tàu ở đỉnh).
**D. Chi phí vận hành**
15. Chi phí nhiên liệu (ai chịu: TC thì khách, chuyến thì chủ tàu); chi phí thuyền viên; bảo hiểm P&I/H&M + **phí war-risk**
    khi đi vùng Vịnh/Biển Đỏ; chi phí cảng và hoa tiêu (ưu đãi −10% cho cờ VN).
16. Off-hire, sự cố, tranh chấp; tàu nào bị kẹt/phải đi vòng vì Hormuz.
**E. Rủi ro & pháp lý**
17. Phơi nhiễm trừng phạt (chở dầu/sang mạn liên quan đến Nga/Iran/Venezuela): rủi ro bị đưa vào danh sách cấm, mất bảo hiểm P&I.
18. Phụ thuộc cabotage: có dự thảo nới quy định cho tàu nước ngoài nào đang mở không (đọc bản hiện hành Bộ luật + TT 41/2025).
19. Hợp đồng FSO/FPSO (nếu có): thời hạn mỏ, rủi ro chấm dứt sớm khi mỏ suy giảm.
20. Quan hệ với nhà máy lọc dầu: lịch bảo dưỡng tổng thể (TA) của Dung Quất/Nghi Sơn 2027 (khối lượng nội địa giảm trong TA);
    tiến độ thật dự án mở rộng Dung Quất (37 tháng từ T7/2026).

## 7. Điều gì làm tôi sai
1. **Hormuz leo thang (K3)**: BDTI có thể lên lại > 8.000. Kiểu tấn công hạ tầng vùng Vịnh, không chỉ tấn công tàu.
2. **Mở eo kèm làn sóng hàng dồn + bổ sung tồn kho kéo dài hơn tôi nghĩ** (tồn kho OECD có thể xuống khoảng 70 ngày): cước cao kéo
   dài 2-3 quý sau khi mở, và F1 sai.
3. **Kém hiệu quả thành cấu trúc** ("Hormuz new normal": tàu tránh vùng Vịnh vĩnh viễn, bảo hiểm cao, tuyến dài): nền cước 2027
   cao hơn nhiều so với 2023-25. Khi đó STRUCTURAL đúng hơn tôi cho (0,15).
4. **Đội tàu bóng tối KHÔNG quay lại và phá dỡ tăng** (tàu già, giá thép phế liệu): cung ròng thấp hơn ước tính +5-6%.
5. **Với VN:** nếu DN ký TC dài ở đỉnh 2026 với khách hàng ngoài hệ thống có tín nhiệm tốt, lợi nhuận 2027 **không** giảm theo
   cước giao ngay. Đó là lý do mục 6.A quan trọng hơn mọi dự báo cước.
6. **Dữ liệu yếu:** TC 1 năm, VLGC, MR châu Á tháng 10 không có nguồn sơ cấp trong lượt này; BQ không có chuỗi cước tàu dầu để
   chấm tự động.

Chấm điểm: Mike/Bobby tra chỉ số Baltic (qua Optima/Baltic Exchange) và số liệu Hải quan/BSR/Cục Hàng hải tại các mốc, ghi
Brier dưới mục 4. **Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (TE daily: brent, crude_oil, urals_oil, te_crack_spread_index, propane, naphtha, gasoline, heating_oil), truy vấn 29/10/2026; `data/vcb_fx_rate.csv` (03/07 và 29/10/2026).
- Optima Shipbroking, "Dirty Tanker Index Summary 26 October 2026" (số liệu tới 23/10): https://www.optimashipbroking.com/market-report/dirty-tanker-index-summary-26-october-2026/
- Lloyd's List, "Crude tanker rates retreat from epic peak as chartering pace slows", 19/10/2026: https://www.lloydslist.com/LL1158747/Crude-tanker-rates-retreat-from-epic-peak-as-chartering-pace-slows
- Riviera, "Aframax/LR2 tanker rates hit record highs as VLCC cargo cascade boosts demand", 28/10/2026 (BRS 26/10): https://www.rivieramm.com/news-content-hub/aframaxlr2-tanker-rates-hit-record-highs-as-vlcc-cargo-cascade-boosts-demand-90399
- Argus, "Mideast Gulf clean tanker rates hit record highs", 15/10/2026 (qua tóm tắt tìm kiếm): https://www.argusmedia.com/es/news-and-insights/latest-market-news/2891210-mideast-gulf-clean-tanker-rates-hit-record-highs
- Riverlake, "Average Time Charter Rates – Week 31 (28 July 2026)": https://www.riverlake.ch/average-time-charter-rates-week-31-28-july-2026-key-takeaways/ ; mức TC 1 năm VLCC khoảng 200k cuối T9 (Breakwave 23/09 qua trang thứ cấp, độ tin thấp): https://www.thepricer.org/how-much-does-it-cost-to-charter-an-oil-tanker/
- BIMCO Tanker Outlook 08/2026 (Cyprus Shipping News 31/08/2026): https://cyprusshippingnews.com/2026/08/31/export-disruptions-increasingly-hurting-tanker-demand-bimcos-tanker-shipping-market-overview-outlook-august-2026-is-out/
- Breakwave Advisors, "Hormuz 2027: Reopening or Prolonged Disruption?", 04/09/2026: https://www.breakwaveadvisors.com/insights/2026/9/4/hormuz-2027-reopening-or-prolonged-disruption
- Lloyd's List Intelligence, Red Sea Brief 01/10 và 15/10/2026: https://www.lloydslistintelligence.com/resources/blog/red-sea-brief-1-october-2026 , https://www.lloydslistintelligence.com/resources/blog/red-sea-brief-15-october-2026
- Hellenic Shipping News / BIMCO (sổ đặt tàu sản phẩm, tuổi đội tàu, số 2025): https://www.hellenicshippingnews.com/?p=1122498 ; IFC/Orgalbraiths: https://ifchorgalbraiths.com/?p=72510
- Giá tàu cũ: Xclusiv/KOBC qua tổng hợp tìm kiếm (T10/2026): https://www.shipuniverse.com/?p=21850 ; Lloyd's: https://www.lloydslist.com/LL1155189/Tanker-values-hold-firm-but-have-room-for-further-rises
- VLGC: India Seatrade News 21/08/2026: https://indiaseatradenews.com/j-m-baxi-group-enters-lpg-shipping-with-87-3-million-vlgc-acquisition/ ; Drewry LPG 2026: https://www.drewry.co.uk/maritime-research-opinion-browser/maritime-research-opinions/trade-policies-and-stronger-fleet-growth-pose-challenges-for-lpg-shipping-in-2026
- Tiền Phong, "6 tháng đứt nguồn cung từ Kuwait, Lọc dầu Nghi Sơn xoay xở thế nào?", 02/10/2026: https://tienphong.vn/6-thang-dut-nguon-cung-tu-kuwait-loc-dau-nghi-son-xoay-xo-the-nao-post1881671.tpo
- Marine Insight, Vietnam appeals to US Navy for tanker passage, 13/05/2026: https://www.marineinsight.com/vietnam-appeals-to-u-s-navy-for-tanker-passage-amidst-blockade-as-fuel-shortages-peak
- Doanh nghiệp Hội nhập, BCT về sản xuất Dung Quất/Nghi Sơn, 25/03/2026: https://doanhnghiephoinhap.vn/bo-cong-thuong-thong-tin-ve-tinh-hinh-san-xuat-cua-loc-dau-dung-quat-nghi-son-130656.html
- Tuổi Trẻ, Dung Quất nhắm 8,3 tr t, 30/03/2026: https://tuoitre.vn/van-hanh-vuot-cong-suat-loc-dau-dung-quat-nham-ky-luc-8-3-trieu-tan-giu-nguon-cung-xang-dau-20260330155910682.htm ; Dung Quất 7T khoảng 124% (Doanh nghiệp Hội nhập 06/08/2026): https://doanhnghiephoinhap.vn/nha-may-loc-dau-dung-quat-duy-tri-cong-suat-van-hanh-o-muc-cao.html
- Dung Quất mở rộng EPC 09/07/2026: https://tapchikinhtetaichinh.vn/ky-ket-hop-dong-epc-va-pmc-du-an-mo-rong-nha-may-loc-dau-dung-quat-161371.html ; https://thoibaotaichinhvietnam.vn/ky-hop-dong-goi-thau-hon-988-trieu-usd-nang-cap-mo-rong-loc-dau-dung-quat-200451.html
- Đại biểu Nhân dân, PVN khai thác dầu 9T/2026, 06/10/2026: https://daibieunhandan.vn/petrovietnam-phat-huy-vai-tro-cot-loi-trong-tham-do-khai-thac-dau-khi-10432820.html
- NK nhiên liệu 4T/2026: https://thoibaotaichinhvietnam.vn/viet-nam-chi-hon-10-ty-usd-nhap-khau-nhien-lieu-trong-4-thang-dau-nam-198033.html ; https://nhandan.vn/ocop/hon-10-ty-usd-nhap-khau-nhien-lieu-trong-bon-thang-post965191.html ; tới 15/07: https://baodautu.vn/tinh-den-157-viet-nam-chi-195-ty-usd-nhap-than-dau-tho-xang-dau-d648317.html
- LPG: Vietnam News (khoảng 70% từ Trung Đông, 03/2026): https://vietnamnews.vn/economy/1766732/pv-gas-moves-to-secure-lng-lpg-supply-amid-middle-east-tensions.html ; Vietstock (bất khả kháng 02/03): https://en.vietstock.vn/2026/03/pv-gas-reduces-lpg-deliveries-amid-middle-east-conflict-disruptions-974-629507.htm ; FMT/Bloomberg 28/04/2026: https://www.freemalaysiatoday.com/category/business/2026/04/28/vietnamese-gas-major-looks-to-us-as-iran-war-reorders-lpg-flows ; Nhà đầu tư (khoảng 100k t/tháng): https://nhadautu.vn/pv-gas-giu-vung-nguon-cung-lng-lpg-cho-thi-truong-nang-luong-viet-nam-giua-gian-doan-tai-eo-bien-hormuz-d104910.html
- Tổng nguồn xăng dầu 2026 + E10: https://vneconomy.vn/dam-bao-cung-ung-xang-dau-2026-khong-de-dut-gay-trong-moi-tinh-huong.htm
- Cabotage: Trung tâm WTO (mở cửa vận tải biển nội địa): https://trungtamwto.vn/chuyen-de/12973-tu-van-ve-mo-cua-thi-truong-dich-vu-linh-vuc-van-tai-bien-noi-dia ; TT 41/2025/TT-BXD: https://www.moc.gov.vn/Images/FileVanBan/BXD_41-2025-TT-BXD_28112025.pdf ; Bộ luật Hàng hải 2015: https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Law-No-95-2015-QH13-Vietnam-Maritime-Code-303292.aspx
- Đội tàu VN (tuổi, miễn VAT NK tàu tới 2026): https://theleader.vn/doi-tau-bien-viet-nam-thang-hang-d10493.html ; https://thuonghieucongluan.com.vn/doi-tau-bien-viet-nam-tre-hon-doi-tau-the-gioi-thang-hang-a186302.html ; phí hoa tiêu −10% (03/2026): https://en.vietstock.vn/2026/03/at-least-10-per-cent-reduction-in-pilotage-service-fees-offered-for-all-vietnamese-flagged-vessels-974-630060.htm
- Bối cảnh Hormuz (đã có nguồn): `sector_read_fertilizer_dap_20261028.md` mục 2 và mục Nguồn.
