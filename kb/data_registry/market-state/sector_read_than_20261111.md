---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-11 (lô dd_*_20261111). KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp than cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành khai thác than lộ thiên Quảng Ninh (antraxit cho nhiệt điện, xi măng, phân bón; xuất khẩu nhỏ) dưới cơ chế TKV điều phối sản lượng/giá nội bộ + nhập khẩu than pha trộn. Gồm pipeline cầu, cấu trúc cung/cơ chế giá, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED theo 2 tầm, FORECAST khoá trước có ngày chấm, checklist DD cho nhà sản xuất than lộ thiên.
as_of: 2026-11-11 (snapshot vĩ mô dd_CST_20261111 có áp độ trễ công bố; BQ commodity_prices TE tới 2026-11-09/10; tin web ≤ 2026-11-05)
---

# SECTOR READ: Khai thác than lộ thiên Quảng Ninh, as-of 11/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán /
suy luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải KIỂM trước khi dùng làm số). File chị em đối chiếu
bối cảnh: `sector_read_power_consulting_20261028.md` (PDP8, thiếu điện, BCT đề xuất bổ sung ~5.300 MW than tới 2030),
`sector_read_khi_dot_lpg_20261109.md` (cú sốc năng lượng Hormuz, cơ cấu huy động điện), `sector_read_phan_dam_ure_20261104.md`
(2 nhà máy urê dùng than miền Bắc), `sector_read_thep_20261031.md` (than cốc).

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Repo đã đọc:** snapshot `agents/Taylor/research/dd_CST_20261111/macro_snapshot_20261111.md` (CHỈ file đó; không mở file
  nào khác trong thư mục). 4 file chị em ở trên (grep đoạn liên quan than/thuỷ điện). Không tra tên/ý nghĩa chuỗi ký tự trong tên
  thư mục dispatch.
- **BQ (tự truy vấn 11/11):** `tav2_bq.commodity_prices` source `trading_economics`: `coal` (Newcastle, USD/t, daily + monthly),
  `coking_coal`. `worldbank_cmo` KHÔNG có chuỗi than. Không dùng view `*_latest`.
- **Không có trong BQ/snapshot (ghi "không có số", không suy):** giá than TKV bán cho điện (biểu giá nội địa), giá chuyển giao nội
  bộ TKV↔công ty con, giá than antraxit xuất khẩu thực, tồn kho than toàn ngành/tại nhà máy điện, hệ số bóc đất đá bình quân theo
  mỏ, thuế suất tài nguyên/phí BVMT hiện hành đối với than.
- **Rò rỉ không chủ ý (ghi trung thực, KHÔNG dùng cho phân loại/forecast/bảng số):** tóm tắt công cụ tìm kiếm nêu (a) kế hoạch
  2026 + sản lượng H1 của một công ty than hầm lò con TKV; (b) kế hoạch hạ moong của một mỏ lộ thiên con TKV (xuống −205m trước
  30/6/2026); (c) một công ty con TKV "chủ động khai thác vượt công suất" theo NQ28; (d) kế hoạch lãi/cổ tức của một DN khoáng sản
  kim loại thuộc TKV; (e) đường dẫn file BCTN 2025 của một DN thuộc ngành. Với (a)(c)(d)(e): bỏ hẳn. Với (b): chỉ dùng định tính
  "các moong lộ thiên đang tiếp tục hạ sâu" — điều này cũng là **[NỀN]** chung của ngành. Không mở BCTC, BCTN, báo cáo CTCK, giá
  cổ phiếu của DN nào.

## 1. Chuỗi giá và đa proxy
| Chuỗi | Hiện tại | Mốc so sánh | Ghi chú |
|---|---|---|---|
| Than nhiệt Newcastle (TE daily, USD/t) | 09/11: **138,05**; TB T10 **150,26**; TB 6 phiên T11 144,2 | TB T11/2025 110,33 ⇒ hiện tại **+25% YoY**; TB T10 vs T10/2025 (104,84) **+43%**. TB T1/2026 108,8 → T3 138,6 → T9 145,8 → T10 150,3 [DK, BQ] | Giảm ~9% từ 30/10 (152,45) trong 6 phiên — cùng nhịp Brent rơi khi thị trường định giá thoả thuận Hormuz (file khí). Đỉnh vẫn thấp xa 2022 [NỀN] |
| Than cốc (TE daily, USD/t) | TB T11 257,3 | T11/2025 199,5 ⇒ +29% | Không liên quan trực tiếp antraxit nhiệt điện; chỉ để thấy than nói chung đắt |
| Giá than nhập khẩu bình quân VN (Hải quan) | **~122,3 USD/t** (1/1→15/10/2026) | 99,8 USD/t cùng kỳ ⇒ **+22,5%** [DK, cafef/Tiền Phong 27/10] | Chậm hơn Newcastle vì cơ cấu Indonesia (than nhiệt trị thấp) + hợp đồng |
| Giá than xuất khẩu tối thiểu (than cám chất lượng thấp, thị trường châu Á trừ Nhật/Hàn) | than cám 11C 54 → 66 USD/t (+8…22% các loại) | — | VnEconomy, **bài không ghi ngày** ⇒ chưa xác định đợt nào; không dùng làm số |
| Diesel 0,05S trong nước (đ/l, giá trần) | **28.696** (kỳ 5/11/2026) | T11/2025 khoảng 19.000-20.000 đ/l **[NỀN, chưa kiểm]** ⇒ ~+45-50% [UĐ] | Chi phí lớn của mỏ lộ thiên (xe tải, máy xúc). Đã giảm 2 kỳ liên tiếp đầu T11 [DK, baovanhoa/baodauthau] |
| Giá than TKV bán cho điện (biểu nội địa) | **không có số** | — | Không tìm thấy quyết định điều chỉnh giá than cho điện nào trong 2026 (tìm 1 lần, âm tính ≠ chắc chắn không có) |
| Giá chuyển giao nội bộ TKV→công ty con khai thác | **không có số** | — | Đây là biến số quan trọng nhất cho biên của nhà khai thác (mục 3) |
| USD/VND (snapshot) | 25.600 (10/11) | **−2,72% 12T** (VND tăng giá) | Làm nhẹ giá than nhập khẩu khi quy VND |

**Đọc đa proxy [UĐ]:**
1. **Đồng thuận về hướng:** than thế giới, giá than nhập khẩu VN, diesel trong nước đều cao hơn năm trước 22-50%. Đây là cú sốc
   năng lượng chung (Hormuz), không riêng than.
2. **Phân kỳ quan trọng nhất:** giá **thế giới** lên mạnh, nhưng giá **nội địa** mà nhà khai thác lộ thiên nhận được là giá hành
   chính/nội bộ TKV (không có số công khai, không thấy điều chỉnh 2026). ⇒ phần doanh thu của nhà khai thác **không** đi theo
   Newcastle; phần chi phí (diesel, thuốc nổ, lương) lại đi theo thị trường. Đây là **cơ chế ép biên khi năng lượng tăng giá** trừ
   khi TKV điều chỉnh đơn giá/định mức (có độ trễ). Mức độ ép biên = **không có số**, chỉ DD từng DN mới lượng hoá được.
3. **Phân kỳ hướng gần:** Newcastle và diesel đã bắt đầu giảm đầu T11 — nếu thoả thuận Hormuz thành, áp lực chi phí đầu vào của nhà
   khai thác **giảm** trong 2-3 quý tới, trong khi khối lượng bán vẫn cao (cầu điện + El Niño). Đây là kịch bản thuận cho biên.

## 2. Pipeline cầu

### 2a. Nhiệt điện (≈80% than TKV tiêu thụ) — CẦU MẠNH, chu kỳ thời tiết + nền tăng trưởng
- **Sản lượng điện toàn hệ thống 10T/2026: 297,4 tỷ kWh, +9,8% YoY; riêng T10 +14,3%** [DK, EVN qua VietnamPlus ~03/11/2026].
- **Cơ cấu 10T/2026:** than **147,78 tỷ kWh = 49,7%**; thuỷ điện 73,39 tỷ kWh = 24,7%; khí 7,8%; tái tạo 40,72 tỷ kWh (~13,7%,
  tự tính); nhập khẩu 4% [DK, cùng nguồn]. H1/2026: than 54,5%, thuỷ 21% (file khí).
- **So 10T/2025:** tổng 268,82 tỷ kWh; than 46,2% (~124 tỷ kWh tự tính), thuỷ 32,6% (~88 tỷ kWh) [DK cho tỷ trọng, nguồn tổng hợp
  tìm kiếm; có một nguồn mâu thuẫn nghi là số 2024]. ⇒ **điện than +19% YoY, thuỷ điện −16% YoY** [UĐ, tự tính].
- **Than TKV cấp cho điện 10T/2026: 35,44 tr t** (T10: 3,53 tr t, 109,5% KH) [DK, Nhân Dân 29/10/2026]. 9T/2025: 28,88 tr t
  [DK, vietnamenergy 18/10/2025].
- **Q4/2026 nhu cầu than cho điện ~9,6 tr t; EVN yêu cầu nhà máy nâng tồn kho than tối đa tới đầu T3/2027 và chốt hợp đồng
  antraxit 2027 ngay trong T10/2026** [DK, cafef 27/10/2026]. ⇒ **cầu tích trữ (restocking) cộng thêm vào cầu tiêu thụ** Q4/2026-Q1/2027.
- **El Niño 2026-2027:** dự báo 60-65% khả năng đạt mức rất mạnh 11/2026-1/2027; năm El Niño thường 100% hồ thuỷ điện không tích đủ
  nước [DK, Nhân Dân special / MAE / VietnamPlus, T9-T10/2026]. NSMO soạn 4 kịch bản vận hành 2027 [DK, cafef 27/10]. ⇒ mùa khô
  2027 thuỷ điện thiếu, than phải huy động cao [UĐ, xác suất cao].
- **Nguồn than mới:** một nhà máy nhiệt điện than 2×701,5 MW miền Trung COD tổ 1 cuối T11, tổ 2 cuối T12/2026 (file power
  consulting) — loại than dùng (antraxit nội/nhập/pha trộn) **không có số** trong lượt này. BCT đề xuất chuyển LNG chậm sang
  2031-2035 và **bổ sung ~5.300 MW than vào 2030** (file power consulting) ⇒ chính sách đang **kéo dài** vai trò than, không rút ngắn.
- **Cơ cấu dài hạn [NỀN]:** PDP8 vẫn hướng giảm tỷ trọng than sau 2030 và cam kết net-zero 2050; tái tạo + LNG + hạt nhân tăng.
  Nhưng tầm 12-36 tháng, thiếu điện + trễ LNG làm than là nguồn cân bằng.

### 2b. Xi măng — CẦU TỐT
- Tiêu thụ xi măng nội địa Q1/2026 >18,4 tr t, **+~30% YoY**; H1/2026 nội địa +12,2% (hoặc tổng tiêu thụ xi măng+clinker 60,98 tr t,
  +~16% — 2 số mâu thuẫn cơ sở) [DK, Hiệp hội Xi măng / một tổng công ty xi măng nhà nước, qua tìm kiếm]. Xuất khẩu xi măng+clinker
  Q1/2026 gần 10 tr t, +21% [DK, Hải quan qua trungtamwto]. Cả năm 2025 kỷ lục ~112 tr t [DK].
- Snapshot: Sản xuất CN +15,0% YoY (T10), GDP Q3 +9,95%, PMI 52,3 [DK, snapshot]. GDP xây dựng: snapshot có nhưng gãy định nghĩa,
  không in Δ ⇒ không dùng.
- Than cho xi măng là thị trường cạnh tranh hơn (nhà máy xi măng được nhập khẩu trực tiếp) [NỀN] ⇒ phần này của cầu than nội có
  tính thị trường hơn điện.

### 2c. Phân bón — NHỎ, đang bị ép biên
- 2 nhà máy urê dùng than ở miền Bắc (~1,0-1,1 tr t urê/năm); than +43% YoY vs urê +16% ⇒ biên nhóm này bị ép (file urê). Khối lượng
  than cho phân bón nhỏ so với điện [UĐ]; hướng: ổn định, rủi ro giảm tải nếu biên âm.

### 2d. Xuất khẩu — NHỎ, hành chính, đang tăng
- Xuất khẩu than đầu 2026 tăng mạnh; Nhật là thị trường lớn nhất (~27% lượng 4T, ~285 nghìn t, +220%) [DK, cafef, tìm kiếm]. Giá xuất
  khẩu tối thiểu do nhà nước quy định, chỉ xuất loại trong nước không dùng hết [NỀN]. Quy mô (vài trăm nghìn t/quý) ≪ 44 tr t tiêu thụ
  ⇒ không phải driver của ngành [UĐ].

### 2e. Nhập khẩu & cân đối
- **Nhập khẩu 1/1→15/10/2026: >60 tr t (+11,2%), 7,3 tỷ USD (+36,2%)**; nửa đầu T10: 2,5 tr t (+19,3% lượng, +51,8% trị giá);
  Indonesia ~23,5 tr t (9T), Úc ~2,6 tỷ USD, **Nga ~9,8 tr t (×1,94)** [DK, cafef/Tiền Phong 27/10/2026]. Cả năm 2025 kỷ lục 65,43 tr t
  [DK]. Indonesia cắt hạn ngạch khai thác ⇒ xuất khẩu thấp nhất 5 năm (Bloomberg/DBX qua tìm kiếm, không rõ ngày) ⇒ đỡ giá than nhập.
- **TKV 10T/2026:** tiêu thụ **44,06 tr t (+~20%)**; than nguyên khai 30,78 tr t; than thành phẩm 31,77 tr t; **bóc đất đá 98,24 tr
  m³** (T10: 11,25 tr m³, 107,2% KH); doanh thu 156.061 tỷ đ (+15%) [DK, Nhân Dân 29/10/2026]. KH T11: tiêu thụ 4,27 tr t, thành phẩm
  3,54 tr t.
- Tiêu thụ (44,06) − sản xuất thành phẩm (31,77) ≈ **12,3 tr t** ⇒ phần chênh lệch do than nhập khẩu pha trộn + giảm tồn kho
  [UĐ — không có số tồn kho để tách].
- Tỷ lệ bóc thô cấp tập đoàn: 98,24 tr m³ / 30,78 tr t than nguyên khai ≈ **3,2 m³/t** — gộp cả hầm lò (gần như không bóc) nên hệ số
  thật của riêng lộ thiên **cao hơn nhiều; không có số** [UĐ].
- TKV phát triển "than sạch từ sản phẩm ngoài than" (tận thu từ bãi thải/đất đá lẫn than): KH 2026 2,46 tr t, 8T đạt >1,148 tr t;
  các đơn vị lộ thiên được chỉ đạo tập trung chế biến nguồn này Q4; nhập than gốc Lào theo hiệp định liên chính phủ [DK, VCCI/Báo
  Đầu tư 29/09/2026].

## 3. Cấu trúc cạnh tranh & cơ chế giá/sản lượng
- **Độc quyền hành chính** [NỀN]: TKV (+ một tổng công ty quốc phòng nhỏ hơn) nắm gần như toàn bộ giấy phép antraxit Quảng Ninh.
  Các công ty khai thác lộ thiên là **công ty con/đơn vị của TKV** (một phần đã cổ phần hoá, TKV giữ chi phối). Họ **không bán ra thị
  trường**: than giao cho TKV (đơn vị kinh doanh than của tập đoàn) theo **hợp đồng phối hợp kinh doanh/giao khoán**, giá mua nội bộ
  dựng từ **định mức chi phí theo khâu (bóc đất đá theo hệ số, khai thác, vận chuyển cung độ) + lợi nhuận định mức** [NỀN — PHẢI KIỂM].
  ⇒ Biên của nhà khai thác **là biên do TKV phân bổ**, không phải biên thị trường.
- **Sản lượng:** do (i) giấy phép khai thác (công suất + trữ lượng), (ii) kế hoạch TKV giao, (iii) cơ chế tạm thời **NQ 28/2026/NQ-CP
  (09/6/2026): khai thác vượt ≤15% công suất giấy phép, hiệu lực tới 31/12/2027, phần vượt chỉ dùng cho điện, không vượt trữ lượng
  được cấp** [DK, Báo Đấu thầu / Nhân Dân / VCCI, T6/2026]. TKV xin bỏ điều kiện "chỉ khi cấp bách" và "chỉ cho điện"; Cục Địa chất &
  Khoáng sản 10/9 yêu cầu TKV làm đúng NQ; BCT đề xuất sửa NQ28 — 2 nguồn mô tả nội dung đề xuất khác nhau [DK, moit.gov.vn công văn
  12/10/2026; cafef/Tiền Phong 27/10]. ⇒ Sản lượng là **ADMIN_GATED**, đang được nới.
- **Trần sản lượng dài hạn:** tiêu đề tin quốc tế "TKV giữ sản lượng than ~40 tr t/năm tới 2030" [DK chỉ ở mức TIÊU ĐỀ, engineeringnews
  29/10/2026, bài bị chặn 403 — chưa đọc thân bài]. Quy hoạch Quảng Ninh tới 2030 **kiên định đóng cửa các mỏ lộ thiên** để bảo vệ
  cảnh quan du lịch/môi trường; xu hướng chuyển xuống hầm lò cơ giới hoá; một mỏ lộ thiên lớn ở Hạ Long đã đóng lộ thiên từ 2021 [DK,
  Nông nghiệp & Môi trường, tìm kiếm, không rõ ngày cụ thể].
- **Hệ số bóc đất đá:** moong càng sâu ⇒ hệ số bóc và cung độ vận chuyển đất đá **tăng theo thời gian** [NỀN]; số cụ thể **không có**.
  Chi phí/tấn của lộ thiên do đó tăng cấu trúc; chỉ bù được nếu định mức đơn giá TKV điều chỉnh theo hệ số thực.
- **Giá bán cho điện:** TKV bán than (nội + nhập pha trộn) cho EVN/GENCO theo hợp đồng; giá than pha trộn phản ánh phần nhập khẩu
  [NỀN]. Không tìm thấy quyết định điều chỉnh giá 2026. Giá điện bán lẻ do nhà nước quản lý ⇒ EVN có động cơ kìm giá than nội ⇒ giá
  nội có **trần hành chính ngầm** [UĐ].
- **Tài nguyên/thuế phí:** thuế tài nguyên than, phí BVMT khai thác, **tiền cấp quyền khai thác** (theo Luật Địa chất & Khoáng sản
  2024) [NỀN — mức cụ thể chưa kiểm]. Năm 2026: Thông tư 89/2026/TT-BTC (mẫu kê khai từ 1/7/2026) + dự thảo sửa TT152/2015 về thuế
  tài nguyên (27/6/2026) + Quảng Ninh bổ sung giá tính thuế tài nguyên với **đất đá thải mỏ than dùng làm vật liệu san lấp** [DK, tìm
  kiếm]. Không thấy nghị định đổi mức thuế than ⇒ rủi ro thuế/phí 12T: thấp-vừa [UĐ].
- **Tái cơ cấu TKV 2026-2030:** Tổng Bí thư 29/7/2026 yêu cầu tái định vị TKV thành tập đoàn công nghiệp năng lượng–vật liệu; Đề án rà
  từng đơn vị để **giữ vốn / củng cố / hợp nhất / hợp tác / thoái vốn / chấm dứt**; dự thảo Đề án + Chiến lược phải xong **trước
  27/11/2026**; mục tiêu giảm 5% đầu mối; HĐTV sẽ quyết sáp nhập công ty con vào công ty mẹ theo đề án đã trình BTC [DK, Tạp chí Công
  Thương / VCCI 29/09 / Thời báo Tài chính, 2026]. Nghị quyết 79-NQ/TW (06/1/2026) về kinh tế nhà nước [DK]. ⇒ **sự kiện hành chính
  lớn nhất 12T tới cho cổ đông thiểu số của công ty con** (hợp nhất/sáp nhập/hoán đổi) — chiều tác động **không biết** [UĐ].

## 4. Phân loại (2 trục + 3 nhãn ngành)

### Trục 1 — nguyên nhân gốc của bối cảnh hiện tại
Cầu than tăng mạnh 2026 đến từ (a) cú sốc năng lượng ngoại sinh (Hormuz, đẩy LNG/khí đắt ⇒ điều độ chuyển sang than), (b) thuỷ văn
xấu (thuỷ điện −16%), (c) tăng trưởng cầu điện ~10%/năm theo GDP ~10%. (c) là **nền cấu trúc trung hạn**; (a)(b) là **chu kỳ/ngoại sinh**.
Lạm phát nội VN đang tăng (CPI 5,09%, +1,84pp 12T; LNH 3M 7,0%, +0,68pp) nhưng không phải nguồn của cầu than.

### Trục 2 — có containable không
Sốc giá (a) có lối ra rõ (thoả thuận Hormuz, Newcastle đã −9% từ đỉnh). Thuỷ văn (b) tự hết sau mùa khô 2027 nếu El Niño suy yếu
giữa 2027. Không cần chính sách VN để "giải".

### Nhãn driver biên/lợi nhuận của nhà khai thác lộ thiên (xác suất là trọng số "driver CHÍNH", tổng = 1)
| Tầm | ADMIN_GATED | CYCLICAL | STRUCTURAL | Diễn giải |
|---|---|---|---|---|
| **12 tháng** | **0,55** | 0,25 | 0,20 | Khối lượng (kế hoạch TKV + NQ28) và đơn giá (định mức nội bộ) do hành chính quyết; giá thế giới chỉ đi vào qua chi phí (diesel) và qua việc TKV có điều chỉnh đơn giá hay không. Cyclical = cầu điện/El Niño kéo khối lượng; structural = hệ số bóc tăng dần |
| **3-5 năm** | 0,35 | 0,10 | **0,55** | Đóng cửa mỏ lộ thiên theo quy hoạch Quảng Ninh 2030, cạn moong, hệ số bóc tăng, chuyển hầm lò; tái cơ cấu TKV quyết định hình thái pháp nhân |

**Độ tin cậy: AMBIGUOUS (vừa).** Lý do: thiếu 2 biến then chốt — giá chuyển giao nội bộ và tồn kho — nên không đo được trực tiếp ép
biên; phân loại ADMIN_GATED dựa trên cơ chế **[NỀN]** chưa kiểm lại trong lượt này.

**Kết luận chiều [UĐ]:** Ngành ở pha **khối lượng cao bất thường + chi phí đầu vào đã qua đỉnh + đơn giá hành chính dính**. Với nhà
khai thác lộ thiên: khối lượng 12T tới **gần như chắc chắn cao** (cầu điện + El Niño + restocking + NQ28), biên **phụ thuộc định mức
TKV**, không phải Newcastle. Rủi ro đuôi chính không đến từ cầu mà từ (i) tái cơ cấu TKV, (ii) tai biến thời tiết/sạt lở bãi thải mùa
mưa, (iii) quy hoạch đóng lộ thiên sớm/đúng hạn.

## 5. FORECAST khoá trước (2026-11-11; Bobby không chấm hộ — Mike/người chấm đọc nguồn chính thức tại ngày chấm)
| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | TKV tiêu thụ than **cả năm 2026 ≥ 52,0 tr t** (10T 44,06 + KH T11 4,27 + T12 ~4,3-4,5) | 0,70 | 2027-01-20 | Thông cáo kết quả năm TKV |
| F2 | Nhập khẩu than VN **cả năm 2026 ≥ 70 tr t** (Hải quan) | 0,65 | 2027-02-20 | Hải quan / báo lại |
| F3 | Điện than **≥ 49,0%** sản lượng toàn hệ thống cả năm 2026 (EVN/NSMO) | 0,65 | 2027-01-20 | EVN tổng kết năm |
| F4 | Điện than **H1/2027 tăng ≥ +5% YoY** (tỷ kWh, so H1/2026) | 0,55 | 2027-07-31 | EVN 6 tháng |
| F5 | TKV tiêu thụ than **H1/2027 ≥ H1/2026** (cùng nguồn TKV) | 0,65 | 2027-07-31 | TKV 6 tháng |
| F6 | Chính phủ ban hành văn bản **sửa đổi/nới NQ 28/2026** (bỏ điều kiện "cấp bách"/"chỉ cho điện", hoặc nâng >15%, hoặc gia hạn quá 2027) | 0,50 | 2027-06-30 | Cổng Chính phủ |
| F7 | Newcastle TE **TB tháng 10/2027 < 150,3 USD/t** (TB T10/2026) | 0,65 | 2027-11-05 | BQ `commodity_prices` TE `coal` daily |
| F8 | Có quyết định **điều chỉnh tăng giá than TKV bán cho điện** được công bố trong 12T | 0,35 | 2027-11-11 | BCT/TKV/EVN, báo chí |
| F9 | Có quyết định cấp có thẩm quyền về **sáp nhập/hợp nhất ≥1 công ty con khai thác than đã cổ phần hoá** của TKV (công bố, không cần hoàn tất) | 0,20 | 2027-11-11 | CBTT/Chính phủ/BTC |
| F10 | **Biên gộp tổng hợp** nhóm DN khai thác than con TKV niêm yết, **9T/2027 so 9T/2026**: thay đổi trong **±1,5pp** | 0,60 | 2027-11-20 | BCTC Q3/2027 (danh sách DN do Mike chốt TRƯỚC khi chấm, Bobby không chọn) |
| F10b | … giảm **> 1,5pp** | 0,25 | 2027-11-20 | như trên |
| F10c | … tăng **> 1,5pp** | 0,15 | 2027-11-20 | như trên |

Lập luận [UĐ]: F1-F5 dựa trên quán tính 10T + El Niño + yêu cầu restocking tới T3/2027 + nhà máy than mới COD cuối 2026. F4 thấp hơn
F5 vì nền H1/2026 đã cao (than 54,5%) và tái tạo/LNG mới vào. F7 dựa trên khả năng bình thường hoá Hormuz + Indonesia cắt hạn ngạch
(đỡ giá) — cân bằng nghiêng giảm. F10: đơn giá nội bộ dính + chi phí diesel đã qua đỉnh ⇒ biên **ổn định** là kịch bản trung tâm; đuôi
giảm do hệ số bóc tăng/định mức chậm điều chỉnh lớn hơn đuôi tăng.

**Điều sẽ làm tôi đổi nhãn (falsifiers):** (i) TKV/BCT công bố cơ chế giá than nội gắn thị trường (⇒ CYCLICAL tăng mạnh trọng số);
(ii) Đề án tái cơ cấu (27/11) nêu lịch đóng/sáp nhập cụ thể đơn vị lộ thiên (⇒ STRUCTURAL/ADMIN tầm 12T tăng); (iii) El Niño suy
yếu nhanh trước T3/2027 + thuỷ điện hồi (⇒ F4/F5 sai).

## 6. DD cần kiểm gì — nhà sản xuất than lộ thiên (con TKV)
1. **Chi phí bóc đất đá & dự phòng/phân bổ:** chính sách kế toán (chi phí bóc đất đá vượt/thiếu hệ số bóc trung bình được **vốn hoá
   trả trước dài hạn** hay **trích trước**?); số dư trên BCĐKT và xu hướng; hệ số bóc **thực tế vs kế hoạch vs hệ số trung bình thiết
   kế mỏ** từng năm; ai phê duyệt hệ số (TKV). Số dư trả trước tăng nhanh = lợi nhuận hiện tại đang mượn của tương lai.
2. **Giá bán chuyển giao nội bộ:** hợp đồng phối hợp kinh doanh với TKV — công thức đơn giá (định mức theo khâu, cung độ, hệ số bóc),
   **lợi nhuận định mức** (% hay đồng/tấn), tần suất & độ trễ điều chỉnh khi diesel/lương/thuốc nổ tăng; doanh thu/tấn vs giá vốn/tấn
   theo quý (đo ép biên 2026). Than vượt công suất theo NQ28: cùng đơn giá hay đơn giá riêng?
3. **Tồn kho:** than thành phẩm/nguyên khai chưa giao TKV, than "ngoài than" chờ chế biến, vật tư–phụ tùng; vòng quay; than tồn có được
   TKV cam kết mua không.
4. **Quyền khai thác:** giấy phép (số, ngày hết hạn, công suất, trữ lượng còn lại ⇒ **tuổi mỏ còn lại** theo sản lượng hiện tại);
   vị trí trong quy hoạch **đóng lộ thiên tới 2030** của Quảng Ninh; kế hoạch chuyển hầm lò/tận thu; **tiền cấp quyền khai thác** —
   tổng phải nộp, lịch nộp, hạch toán (chi phí trả trước phân bổ hay ghi thẳng), nợ đọng.
5. **Thuế/phí tài nguyên:** thuế suất tài nguyên than lộ thiên, giá tính thuế (theo bảng giá Quảng Ninh, kể cả **đất đá thải dùng san
   lấp** mới bổ sung), phí BVMT/tấn; ảnh hưởng dự thảo sửa TT152; truy thu thuế/kết luận thanh tra gần đây.
6. **Môi trường & đóng cửa mỏ:** **ký quỹ phục hồi môi trường** (số đã ký/còn phải ký), dự phòng đóng cửa mỏ/hoàn nguyên, bãi thải
   (rủi ro sạt lở, trôi lấp mùa mưa bão — có bị gián đoạn sản xuất do bão 2024/2026 không), nước thải mỏ, xử phạt.
7. **Bên liên quan & dòng tiền:** phải thu TKV (kỳ thu tiền, có bị TKV chiếm dụng vốn khi EVN chậm trả?); vay/tiền gửi qua công ty tài
   chính tập đoàn; cổ tức do công ty mẹ quyết (tỷ lệ chi trả lịch sử); giao dịch mua thiết bị/dịch vụ nội bộ tập đoàn.
8. **Capex & khấu hao:** thay thế xe tải/máy xúc (đầu tư lớn, vay nợ), lịch khấu hao vs tuổi mỏ còn lại (khấu hao có hết trước khi
   đóng mỏ không), capex hạ moong/mở rộng.
9. **Lao động & an toàn:** quỹ lương theo đơn giá tiền lương/tấn TKV duyệt (lương snapshot +10% 12T), tai nạn lao động, thiếu lao động.
10. **Tái cơ cấu TKV:** đơn vị có nằm trong diện hợp nhất/sáp nhập/thoái vốn của Đề án 2026-2030 (dự thảo trước 27/11/2026) không;
    cơ chế định giá hoán đổi nếu sáp nhập vào công ty mẹ/đơn vị khác — **rủi ro/lợi ích thiểu số**.
11. **Độ nhạy (bắt buộc ghi số khi DD):** ±10% diesel ⇒ ±? giá vốn/tấn; ±0,5 m³/t hệ số bóc ⇒ ±? giá vốn/tấn; ±10% sản lượng (NQ28) ⇒
    ±? lợi nhuận — để biết biên đang ăn vào biến nào.

Định giá (nếu dùng): theo chỉ đạo user, r neo lãi huy động 12T + chiết khấu thanh khoản; vòng đời mỏ HỮU HẠN (không dùng g_T vĩnh viễn
cho DN đơn mỏ lộ thiên có lịch đóng cửa) [UĐ].

## 7. Tự kiểm & giới hạn
- **Tốt hơn tôi nghĩ:** cầu than 2026 mạnh hơn kỳ vọng nền (+20% tiêu thụ TKV), chính sách đang nới khối lượng (NQ28) và kéo dài vai
  trò than trong PDP8 sửa đổi.
- **Xấu hơn tôi nghĩ / chưa biết:** không có số giá nội bộ và tồn kho; tiêu đề "40 tr t/năm tới 2030" chưa đọc thân bài; số 10T/2025
  điện có nguồn mâu thuẫn; mức thuế/phí tài nguyên chưa kiểm; giá diesel T11/2025 là [NỀN].
- Không dùng số nào về DN cụ thể; snapshot vĩ mô dùng nguyên trạng (UNVERIFIED, không vintage).

## Nguồn (một số URL có tên DN/tổ chức trong đường dẫn — người đọc blind sau có thể bỏ qua)
- BQ `tav2_bq.commodity_prices` (TE `coal`, `coking_coal`), truy vấn 2026-11-11.
- Snapshot vĩ mô: `agents/Taylor/research/dd_CST_20261111/macro_snapshot_20261111.md` (as-of 2026-11-11).
- Nhân Dân, "10 tháng, TKV tiêu thụ hơn 44 triệu tấn than" — 29/10/2026: https://nhandan.vn/10-thang-tkv-tieu-thu-hon-44-trieu-tan-than-post998882.html
- CafeF (từ Tiền Phong), "Chi hơn 7,3 tỷ USD nhập khẩu than…" — 27/10/2026: https://cafef.vn/chi-hon-73-ty-usd-nhap-khau-than-ap-luc-nhien-lieu-cho-nganh-dien-188261027071236886.chn
- VietnamPlus, "Sản lượng điện 10 tháng tăng 9,8%…" — ~03/11/2026: https://www.vietnamplus.vn/san-luong-dien-10-thang-tang-98-evn-tap-trung-bao-dam-nguon-cung-cuoi-nam-post1145791.vnp
- Báo Đấu thầu, "Ban hành Nghị quyết về cơ chế khai thác than" (NQ 28/2026/NQ-CP, 09/6/2026): https://baodauthau.vn/ban-hanh-nghi-quyet-ve-co-che-khai-thac-than-post200455.html
- Bộ Công Thương, công văn TKV về NQ28 — đăng 12/10/2026: https://moit.gov.vn/upload/2005517/20261012/CV_cua_TKV_6d481.pdf
- VCCI (từ Báo Đầu tư), "TKV tăng tốc sản xuất, chuẩn bị cuộc tái cơ cấu lớn" — 29/09/2026: https://vcci.com.vn/tin-tuc/tkv-tang-toc-san-xuat-chuan-bi-cuoc-tai-co-cau-lon
- Tạp chí Công Thương, Tổng Bí thư yêu cầu tái định vị TKV — T7/2026: https://tapchicongthuong.vn/tong-bi-thu--chu-tich-nuoc-to-lam--tai-dinh-vi-tkv-thanh-tap-doan-cong-nghiep-nang-luong--vat-lieu-hien-dai-537853.htm
- Engineering News, "Vinacomin to keep coal output at 40Mt/y up to 2030" — 29/10/2026 (CHỈ tiêu đề, 403): https://www.engineeringnews.co.za/article/vietnams-vinacomin-to-keep-coal-output-at-40-million-tons-a-year-up-to-2030-state-media-reports-2026-10-29
- Nhân Dân, "El Nino đe dọa nguồn nước nhiều lưu vực sông mùa khô 2027": https://nhandan.vn/el-nino-de-doa-nguon-nuoc-nhieu-luu-vuc-song-mua-kho-2027-post988918.html ; MAE "Chủ động giữ nguồn nước trước El Niño 2026-2027": https://mae.gov.vn/chu-dong-giu-nguon-nuoc-truoc-el-nio-20262027-22889.htm
- Nông nghiệp & Môi trường, "Ngành than Quảng Ninh siết chặt ranh giới mỏ bằng công nghệ": https://nongnghiepmoitruong.vn/nganh-than-quang-ninh-siet-chat-ranh-gioi-mo-bang-cong-nghe-d791624.html
- vietnamenergy, TKV–EVN cân đối than nhập 2026-2030 — 18/10/2025: https://vietnamenergy.vn/tkv-balances-coal-imports-and-ensures-a-stable-supply-for-evn-during-2026-2030-35028.html
- Xi măng: trungtamwto (Q1/2026 xuất khẩu ~10 tr t): https://trungtamwto.vn/tin-tuc/32316-xuat-khau-xi-mang-va-clinker-trong-quy-i2026-dat-gan-10-trieu-tan ; Báo Đấu thầu "Doanh nghiệp xi măng tiếp đà tăng trưởng": https://baodauthau.vn/doanh-nghiep-xi-mang-tiep-da-tang-truong-post203880.html
- Xuất khẩu than: CafeF "Nhật Bản báo tin cực vui…": https://cafef.vn/nhat-ban-bao-tin-cuc-vui-den-viet-nam-18826090222234916.chn ; VnEconomy "Giá than xuất khẩu tăng từ 8-22%" (không ngày): https://vneconomy.vn/gia-than-xuat-khau-tang-tu-8-22.htm
- Diesel: baovanhoa (kỳ 3/11/2026): https://baovanhoa.vn/gia-xang-e5-e10-tiep-tuc-giam-dau-diesel-ha-1-370-dong-lit.html ; baodauthau (kỳ 5/11): https://baodauthau.vn/nhieu-mat-hang-xang-dau-dong-loat-giam-post211739.html
- Thuế/phí: Thời báo Tài chính "Quảng Ninh bổ sung giá tính thuế đất, đá thải mỏ than": https://thoibaotaichinhvietnam.vn/quang-ninh-bo-sung-gia-tinh-thue-dat-da-thai-mo-than-201340.html
