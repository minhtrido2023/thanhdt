---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-17. Không được cung cấp mã, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về ngân hàng mục tiêu; không đi tìm chúng (xem §0 về rò rỉ cấp ngân hàng qua kết quả tìm kiếm).
blind: YES
as_of: 2026-11-17 (snapshot vĩ mô tự sinh `macro_snapshot_asof.py --asof 2026-11-17`, có áp độ trễ công bố; CSV lãi suất PIT tới 2026-11-16; tin web ≤ 2026-11-14)
group: market-state
parent: vn_macro_regime_history.md
sibling: sector_read_ngan_hang_20261031.md (nhóm NHTM cổ phần tư nhân lớn, as-of 31/10 — tái dùng khung pháp lý, chu kỳ chất lượng tài sản và FORECAST F1-F12 của file đó, KHÔNG khoá lại mệnh đề trùng)
role: SECTOR READ nhóm NHTM vốn Nhà nước chi phối (quốc doanh, quy mô lớn nhất hệ thống). Gồm pipeline cầu tín dụng, cấu trúc cạnh tranh, room/chính sách NHNN, NIM/chi phí vốn (bảng 5 tầng), chất lượng tài sản, vốn (Basel III, CAR, tăng vốn/cổ tức cổ phiếu, NQ 79), phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED 2 tầm, FORECAST khoá trước có ngày chấm, checklist DD (gồm bẫy định giá riêng ngành NH).
---

# SECTOR READ: NHTM quốc doanh (vốn Nhà nước chi phối), as-of 17/11/2026 (Bobby, real-time BLIND)

Không phải episode VNINDEX, không tính vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày công bố; **[UĐ]** ước đoán / suy
luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải kiểm trước khi dùng làm số); **(ước lượng)** = số tự tính.
Ngưỡng "cờ" trong §7 là ngưỡng **soát** do Bobby đề xuất, không phải chuẩn quy định trừ khi ghi rõ.

## 0. Kiểm toán blind (đã đọc / chưa đọc / rò)
- **Đã đọc nội bộ:** `sector_read_ngan_hang_20261031.md` (file chị em, nhóm tư nhân), `vn_macro_regime_history.md` REGIME READ #3
  (10/11) gồm bảng 5 tầng 02-10/11 và 10 chỉ báo dẫn; `data/deposit_rate_vn_events.csv` (tới 16/11), `cctg_rate_vn_events.csv`,
  `cctg_rate_vn_6m_events.csv`, `cctg_rate_vn_tier2_events.csv` (tới 02/11), log `refresh_deposit_cctg_weekly_2026-11.log` (16/11).
- **Snapshot vĩ mô:** caller KHÔNG đưa đường dẫn snapshot; tôi tự chạy `bin/macro_snapshot_asof.py --asof 2026-11-17 --format md` ra
  `/tmp/bobby_snap_20261117/` (chỉ đọc `tav2_bq.macro_indicator`, không chứa mã/giá/BCTC). Không mở thư mục `dd_*` nào.
- **Không tra:** giá cổ phiếu, BCTC, BCTN, Pillar 3, báo cáo CTCK của bất kỳ NH nào; không truy vấn `ticker_financial`/`ticker`
  (nhóm niêm yết chỉ có 3 NH ⇒ chọn bất kỳ dòng nào cũng là chọn mục tiêu).
- **Rò cấp NH qua snippet tìm kiếm (khai trung thực — QUAN TRỌNG vì nhóm chỉ có 3 NH niêm yết + 1 NH chưa niêm yết):** kết quả tìm
  kiếm trả về số Q3/2026 có TÊN của cả 3 NHTM Nhà nước niêm yết: LNTT quý/9T, thay đổi dự phòng, NPL, bao phủ, tăng nợ nhóm 2, tiền gửi
  Kho bạc từng NH; một NH áp dụng sớm TT 14/2025 từ 03/2026; một NH được chấp thuận nâng vốn; một NH có biểu 12M online 5,4% (lệch 3 NH
  còn lại); cổ tức tiền mặt 4,5% năm trước. **Tôi chỉ dùng ở dạng KHOẢNG không tên (min-max của 3 NH) hoặc tổng nhóm.** Vì nhóm chỉ có 3
  phần tử, mọi khoảng đều CHỨA NH mục tiêu ⇒ người dùng file nên coi các khoảng ở §2-§3 là đã đi qua mắt tôi, và tôi không dùng
  vị trí của bất kỳ NH nào trong khoảng để phân loại. Tôi không biết NH nào là mục tiêu.

## 1. Snapshot vĩ mô (ngân hàng ↔ policy / liên NH / spread / TPCP Δ / USD-VND)
| Chỉ báo | Giá trị | Δ3T / Δ12T | Đọc cho NH quốc doanh [UĐ] |
|---|---|---|---|
| Tái cấp vốn | 4,50% (31/10) | 0 / 0 | Không có chu kỳ hạ/nâng điều hành; NHNN điều hành giá bằng công văn (§3) |
| Liên NH 3M (TE) | 6,33% (11/11) | −1,19pp / +0,03pp | Snapshot TE lệch số báo cùng tuần (TBTC 14/11: 3M **7,45%**, +0,45pp) — 2 nguồn khác phạm vi/ngày; chỉ tin HƯỚNG: kỳ hạn dài liên NH KHÔNG giảm |
| Spread 3M − điều hành | +1,83pp, phân vị 91% từ 2012 | −1,19 / +0,03 | Giả thuyết thanh khoản chưa kiểm (D2) — chỉ mô tả |
| TPCP 10Y (chỉ tin Δ) | 4,57 | 0 / **+0,57pp** | Lợi suất dài nhích ⇒ danh mục TPCP (NH quốc doanh nắm lớn [NỀN]) có lỗ đánh giá nhẹ, thu nhập lãi TPCP mới cao hơn |
| USD/VND | 25.764 (16/11) | −1,68% / −2,24% | VND mạnh lên; NHNN bắt đầu **mua** USD giao ngay (§1b) |
| CPI YoY / core | 5,09% (T10) / core T10 4,04% (NSO qua TTTCTT 03/11; snapshot còn số T9 4,45) | +0,64 / +1,84pp | Cost-push (xăng, gas), lõi giảm ⇒ không có áp lực siết hệ thống |
| GDP / IIP / bán lẻ | 9,95% (Q3) / 15,0% / 14,7% (T10) | | Cầu tín dụng sản xuất thật còn mạnh |
| US 2Y / 10Y / DXY | 4,85 / 5,13 / 103,5 (16/11) | +0,67 / +0,40pp; DXY +3,9% 3T | Ngoại sinh xấu đi; Fed 3,75-4,00% sau lần tăng 16/09, giữ 28/10 (federalreserve.gov), thị trường định giá ~81% tăng 12/2026 (entry 10/11) |
| Dự trữ ngoại hối | 82,65 tỷ USD (31/08, lag không có lịch) | −0,19% / +2,97% | Mỏng so với nhập khẩu ~58 tỷ USD/tháng (≈1,4 tháng nhập — ước lượng thô) ⇒ NHNN bảo vệ tỷ giá bằng lãi suất liên NH, không bằng bán dự trữ |

### 1a. Tín dụng vs hạn mức [DK]
- Toàn hệ thống **20,75 triệu tỷ, +11,59% YTD, +16,69% YoY (30/09)** (PTĐ Phạm Thanh Hà, họp báo 03/10; VNBA 05/10); **+11,94% YTD
  (26/10)**, "khoảng 12,27%" cuối T10 (Thống đốc tại QH 31/10). Định hướng 2026 **khoảng 15%**, điều chỉnh linh hoạt; khảo sát TCTD
  kỳ vọng cả năm **16,4%** (NHNN, Q4). Tín dụng T11: chưa có số (đúng lịch).
- **Nhóm quốc doanh tăng CHẬM hơn hệ thống**: khoảng **6-10% YTD** ở 3 NH niêm yết vs **12,9-33%** ở nhóm tư nhân lớn (ước tính giữa
  Q3, vnbusiness 28/09/2026); nhóm nhận chuyển giao bắt buộc **20-28% YTD** nhờ room ưu đãi (Elibook 04/10). ⇒ Room hành chính
  hiện ĐÈ lên nhóm quốc doanh nhiều hơn [UĐ: một phần do vốn mỏng (CAR) chứ không chỉ do room, xem §2c].
- **Ngoài hạn mức**: TT 08/2026 và TT 25/2026 loại trừ cho vay NOXH, KCN và 18 dự án trọng điểm khỏi hạn mức tăng trưởng chung; tỷ lệ
  vốn ngắn hạn cho vay trung dài hạn 30 → **40%** (vietnamfinance 03/08/2026). Đây là kênh nhóm quốc doanh dẫn (hạ tầng, NOXH).
- **Gói chính sách**: NOXH 120 nghìn tỷ (9 NH tham gia, gồm cả 4 NH quốc doanh; lãi 7,0% chủ đầu tư / 6,5% người mua 01/07-31/12/2026);
  gói 153 nghìn tỷ ưu đãi thấp hơn BQ ≥1-1,5pp tối thiểu 2 năm; gói SME T8/2026 thấp hơn BQ ≥1pp (vnbusiness, VNBA 2026). Một NH quốc
  doanh chưa niêm yết công bố gói NOXH 30 nghìn tỷ (VNBA 08/10).

### 1b. Bảng 5 tầng chi phí vốn / thanh khoản (as-of 17/11/2026)
| Tầng | Ô | Số | Nguồn · ngày |
|---|---|---|---|
| **A. Niêm yết hành chính** | Big-4 12M **online** | **6,8%** ở 3/4 NH; **1/4 NH 5,4%** theo 2 nguồn (CafeF 15/11 ghi 6,8 cho NH đó — mâu thuẫn) | CSV 16/11 (VietnamPlus 10/11, VietnamBiz 11/11, CafeF 15/11) |
| | Big-4 12M **tại quầy** | **5,4%** (sau CV 9608, ghi 26/10-09/11); bảng không ngày trên TBTC 14/11 vẫn in 5,9% cho 4 NH ⇒ bảng cũ, không dùng | CSV / log 26/10, 09/11 |
| | Big-4 6M online / quầy | online: **không có số mới**; quầy 3,5% (3 NH) / 4,0% (1 NH) theo bảng không ngày — độ tin cậy thấp | TBTC 14/11 (bảng không ngày) |
| **B. Bán-hành-chính** | CCTG 12M từng NH | 2 NH **7,4%** (12T); 1 NH chỉ phát 6T; 1 NH không có CCTG 12T. Lượt 16/11: vẫn 7,4% nhưng chỉ 1 gốc nguồn ⇒ chưa ghi chuỗi | CSV 02/11; log 16/11 |
| | CCTG 6M từng NH | 1 NH **7,5%** (chỉ phát 6T); 2 NH 7,2% (6-9T / 6-11T) | CSV 6M 02/11 |
| | Spread CCTG12M − TK 12M | **+0,6pp** vs online; **+2,0pp** vs quầy (từ +1,5pp trước CV 9608) | tự tính |
| | Đường cong / mở-rút kỳ hạn | 1 NH chỉ phát 6T ⇒ đường CCTG Big-4 dốc NGƯỢC nhẹ ở NH đó (6T 7,5 > 12M TK 6,8) [UĐ: kéo vốn ngắn, tránh khoá giá cao 12T]. Không thấy sự kiện mở/rút mới trong 11/2026: **không có số** | CSV |
| | Cấp 2 Big-4 (biên trên tham chiếu) | +1,05 (2024) → **+2,25/+2,3** (09/2026) → trần NQ +2,8 (16/09) | entry 13/10 |
| **C. Ngoài Big-4** | 12M tư nhân / ẩn | VPB CCTG **9,0%** (≥100tr, 184-389 ngày) / 7,5% (10tr); TCB 6T 8,0 → **7,6%**; MB 6T 7,1%; NCB giảm 0,6pp, cao nhất 6,2% (đầu T11); thực trả BQ 12M ~**8,45%** (1 nguồn, 10/2026) | CSV tier2 02/11; log 16/11; Elibook 22/10 |
| | Số NH ≥ 7% | **không có số** | — |
| | Spread tư nhân − Big-4 | niêm yết ~+0,2-1,2pp; ẩn/CCTG ~+1,6-2,2pp (ước lượng) | tự tính |
| **D. Thị trường** | Liên NH tuần 9-13/11 | **ON 4,8% (12/11; đỉnh 6,07 ngày 06/11) / 1W 4,8 / 2W 5,2 / 1M 5,5 (+0,53) / 3M 7,45 (+0,45)**; doanh số ~900 nghìn tỷ/tuần | TBTC 14/11 |
| | OMO | Tuần 9-13/11 **hút ròng 25,2 nghìn tỷ** (tuần trước bơm ròng 13,6); trúng thầu 41,1 nghìn tỷ @4,5% (14-91 ngày); lưu hành **93,98 nghìn tỷ** | TBTC 14/11 |
| | Công cụ khác | Swap USD/VND 182 ngày trần 2 tỷ USD (từ 06/11); **NHNN mua USD giao ngay 25.500 thứ Hai/Tư từ 11/11** (bơm VND, bù dự trữ); tín phiếu: **không có số** | TBTC 06/11, 14/11 |
| | TPCP 10Y + tỷ lệ trúng thầu | Δ12T +0,57pp (TE); mức + tỷ lệ trúng thầu T10-11: **không có số** | snapshot |
| | USD/VND chính thức vs tự do | Trung tâm **25.637** (13/11, +22đ/tuần); VCB bán 25.910 (+130đ/tuần); tự do 26.080-26.140 (**+230đ ≈ +0,9%** so NH) | TBTC 14/11 |
| **E. Lượng** | Tín dụng vs huy động (cùng nguồn, cùng mốc) | Q3 tới 23/09: huy động **+3,8%** vs tín dụng **+1,9%** trong quý (VDSC, nhóm theo dõi — khác phạm vi hệ thống); hệ thống cùng mốc: **không có số** | Elibook 04/10 |
| | LDR | Hệ thống (định nghĩa TT 22): **76,07%** (30/09) ⇒ KHÔNG trừ được với LDR thuần 27 NH ~114% (Q2, Yuanta — định nghĩa khác). Big-4 (TT 22): **82,9-84,5%** (31/03), sát trần 85% | TTTCTT 11/11; TBTC 11/05 |
| | Tiền gửi Kho bạc (KBNN) | Toàn hệ thống 626,7 nghìn tỷ (31/03), **99,59% tại NHTM Nhà nước**; 3 NH quốc doanh niêm yết: **406,5 (cuối 2025) → 563,0 (Q1, đỉnh) → ~556,5 (Q2) → 521,1 nghìn tỷ (Q3)**, giảm 2 quý liên tiếp. Tiền gửi có kỳ hạn KBNN toàn hệ thống ~740 nghìn tỷ (08/2026) | TBTC 11/05; vnbusiness 02/11; cafef 04/08 |
| | Văn bản = thừa nhận áp lực vốn | (1) Bỏ hẳn KBNN có kỳ hạn khỏi mẫu số LDR từ đầu 2026 → dự thảo tính lại 20% (05/2026) → QĐ NHNN tính **50%** hiệu lực 01/08/2026-31/07/2028; (2) TT 08 + 25/2026 (vốn NH cho vay TDH 40%); (3) **TT 50/2026** LDR 85 → 95% từ 01/12; (4) Bộ TC đề xuất sửa NĐ 24/2016 (bỏ trần cứng tiền gửi KBNN, dự kiến hiệu lực 01/01/2027) | TBTC 11/05; vnbusiness 02/11; vietnamfinance 03/08; cafef 04/08 |

**Đồng thuận / phân kỳ (đọc riêng cho nhóm quốc doanh):**
- **HƯỚNG:** tầng A-quầy giảm 0,5pp (hành chính, CV 9608/9736 + thanh tra CV 10488 tháng 11); A-online 3/4 NH đứng 6,8; B đứng
  7,4-7,5; D ngắn (ON/1W) giảm sau đỉnh đầu tháng nhưng **D 1M/3M tăng lại** (5,5 / 7,45); E: các văn bản nới LDR dồn dập trong 6 tháng,
  **phần lớn nhắm đúng nhóm quốc doanh** (KBNN 99,6% nằm ở đó; Big-4 LDR sát 85%).
- **MỨC:** chi phí vốn biên của nhóm quốc doanh = CCTG 7,4-7,5% và cấp 2 (tham chiếu + 2,25-2,8pp), cao hơn niêm yết online ~0,6-0,7pp
  và quầy ~2,0pp. Nhưng **chi phí vốn BÌNH QUÂN** của nhóm thấp hơn tư nhân nhờ CASA + KBNN + tiền gửi tổ chức nhà nước [NỀN về cơ cấu].
- **Cơ chế [UĐ, suy luận]:** nhóm quốc doanh là "neo giá" hành chính — giữ niêm yết thấp theo chỉ đạo, và bù thanh khoản bằng (a) KBNN
  (rẻ, ngắn, có thể rút), (b) CCTG/cấp 2 (đắt, ngoài phạm vi CV 9608), (c) nới định nghĩa LDR. Khi giải ngân đầu tư công tăng tốc Q4
  (74,1% kế hoạch tới 31/10, còn ~247 nghìn tỷ phải giải ngân — ước lượng từ 955,9 − 708,6; Bộ TC 03/11), KBNN rút ⇒ nhóm mất nguồn
  rẻ đúng lúc phải giảm lãi cho vay ⇒ **áp lực NIM Q4/2026-Q1/2027 tập trung ở nhóm quốc doanh** nhiều hơn nhóm tư nhân bán lẻ.
- **Độ tin cậy:** hướng trung bình-cao; mức chênh trung bình (CCTG lượt 16/11 chỉ 1 gốc nguồn; tầng C số NH ≥7% thiếu). Không đề xuất
  escalate. Kill-switch A (>7,5%) **CLEAR** (7,4%).

## 2. Chất lượng tài sản, NIM, vốn — nhóm quốc doanh

### 2a. NIM và lợi nhuận [DK + UĐ]
- **NIM nhóm quốc doanh thấp cấu trúc:** khoảng **2,7-3,0%** (3 NH, ước tính giữa Q3; vnbusiness 28/09) vs **3,7-4,7%** ở NH tư nhân
  bán lẻ; năm 2025 Big-4 **2,1-2,6%** (HDBS 12/2025). Ngành (27 NH): Q2/2026 3,15% (Yuanta); Q3 dự phóng 3,18% (VDSC, −3bp QoQ); số
  Q3 thực tế toàn ngành: **không có số tổng hợp đủ mẫu**.
- **Lợi nhuận 2026 của nhóm được đỡ bởi DỰ PHÒNG GIẢM:** dự phòng nhóm quốc doanh **−18,5% YoY** vs tư nhân **+28,8%** (VDSC, Elibook
  04/10); LNTT nhóm quốc doanh Q3 ước **+28% YoY** (VDSC) vs tư nhân +19%; thay đổi dự phòng Q3 giữa 3 NH trải từ **−46% đến khoảng ×8**
  (phân hoá cực mạnh trong nhóm). MBS: LN Q3 ngành +19,1% "chủ yếu nhờ NII và tiết giảm dự phòng của nhóm quốc doanh" (28/09).
- **CV 9608 (18/10) + CV 9736 (21/10) + CV 10488/NHNN-TTNH (thanh tra trong T11, báo cáo TTg; vi phạm có thể bị hạ chỉ tiêu tín
  dụng)** (vietbao 13/11): giảm ≥0,5pp huy động niêm yết ≥6T, giảm **1,5-2pp** cho vay SXKD/ưu tiên. Tỷ trọng cho vay SXKD nhóm quốc
  doanh **51-66%** vs tư nhân bán lẻ <30% (VDSC, file 31/10) ⇒ chỉ thị đè lên nhóm quốc doanh nặng nhất. TCBS ước NIM ngành −3 đến
  −7bp, LNTT −2 đến −4% nếu 3-5% dư nợ được giảm lãi (19/10).
- **Đọc [UĐ]:** NIM nhóm quốc doanh Q4/2026-Q1/2027 **đi ngang đến giảm** (lãi cho vay bị ép, KBNN rút, CCTG/cấp 2 đắt); H2/2027 có
  thể nhẹ đi khi tiền gửi kỳ hạn tái định giá theo mặt bằng quầy thấp hơn — nhưng chỉ khi tầng B/D đi xuống, hiện chưa thấy.

### 2b. Chất lượng tài sản [DK]
| Chỉ tiêu | Số | Nguồn · ngày |
|---|---|---|
| NPL ngành (SSI, 13 NH) | **2,09%** (30/09) từ 1,97% (Q2); nợ nhóm 2 **1,63%**; bao phủ **77%** từ 83% | SSI qua vietbao 08/11 |
| NPL ngành (28 NH) | Nợ xấu nội bảng **340,4 nghìn tỷ** (30/09); nhóm 5 chiếm 48,6% (63,8% cuối 2025 — nợ xấu MỚI đang chiếm tỷ trọng lớn hơn); bao phủ ~80%, thấp nhất 5 năm (FiinRatings) | vnbusiness 05/11 |
| Nhóm quốc doanh — cấp nhóm | NPL **~1,3%** ổn định, bao phủ **~150%** | SSI qua vietbao 08/11 |
| Nhóm quốc doanh — khoảng 3 NH niêm yết | NPL **1,20-1,85%**; bao phủ **~73% đến ~243%**; NPL tuyệt đối **+18% đến +36% YTD**; nợ nhóm 2 **+26% đến +33%** | vnbusiness 05/11 (tự tổng hợp BCTC Q3) |
| Tư nhân (SSI) | NPL 2,83%, bao phủ 55% | vietbao 08/11 |
| Tín dụng ngoại bảng (cam kết, bảo lãnh) | **+24% lên 3.243 nghìn tỷ** H1/2026, ~18% dư nợ (FiinRatings) | vnbusiness 05/11 |
| Lãi dự thu ngành | **+40% YoY**, gấp 2 tăng tín dụng (Q3, Elibook 04/10); 230,7 nghìn tỷ (entry 13/10) | |
| Hình thành nợ xấu | MBS: NPL formation/dư nợ BQ 6T giảm 5bp YoY, dưới TB 3-5 năm (28/09) — **mâu thuẫn** với NPL tuyệt đối +18-36% ở nhóm quốc doanh; chưa hoà giải được (khác kỳ đo, khác mẫu) | |

**Đọc [UĐ]:** nhóm quốc doanh có **đệm cấp nhóm dày** (bao phủ ~150%) nhưng **phân tán rất lớn trong nhóm** (73-243%), và **tầng sớm
xấu đi ĐỒNG LOẠT** ở cả 3 NH (nhóm 2 +26-33%, NPL tuyệt đối +18-36% trong 9 tháng, trong khi tín dụng nhóm chỉ +6-10%) ⇒ tốc độ hình
thành nợ xấu nhóm quốc doanh đang **nhanh hơn tốc độ cho vay** — đây là pha sớm-giữa của chu kỳ, cùng pha với file 31/10. Việc 2026
dùng **giảm dự phòng** để tạo tăng trưởng LN ở một phần nhóm (dự phòng −18,5% YoY cấp nhóm) đúng lúc nhóm 2 tăng là điểm rủi ro chính
cho LN 2027: hoặc phải trích bù, hoặc bao phủ tiếp tục giảm.

### 2c. Vốn — Basel III, CAR, cơ chế tăng vốn [DK, phần [NỀN] ghi rõ]
- **Tỷ trọng:** 4 NHTM Nhà nước giữ **~40-45% tài sản hệ thống, >45% tín dụng, nhưng chỉ ~20% vốn điều lệ** (VNBA 21/05/2026). ⇒ đòn
  bẩy cao nhất hệ thống, vốn là ràng buộc gắt nhất.
- **CAR:** Big-4 lịch sử "quanh 8-10%" (theleader 26/08/2025); 26 NH nội BQ ~12% (cuối 2025, vietnamfinance 03/08/2026). CAR Q3/2026
  từng NH: **không có số** (cố ý không tra).
- **TT 14/2025/TT-NHNN** (hiệu lực 15/09/2025): tự nguyện áp dụng 15/09/2025-31/12/2029, **bắt buộc 01/01/2030**; CAR tối thiểu 8% +
  bộ đệm bảo toàn tăng dần ⇒ **10,5%**; CET1 4,5% → (khi đủ bộ đệm) ~7%, Tier 1 6% → ~8,5% (theleader 26/08/2025; vneconomy 03/12/2025).
  **Chưa có phụ phí D-SIB** (dự kiến 1-3,5% nếu ban hành — sẽ đè lên Big-4); đệm phản chu kỳ 0-2,5%. NOXH rủi ro 20-50% (thấp nhất), cho
  vay mua nhà chia theo LTV × nguồn trả nợ. Ít nhất 1 NH quốc doanh đã áp dụng tính vốn theo TT 14 từ 03/2026 (tin báo).
- **Cơ chế tăng vốn mới — NQ 79-NQ/TW (06/01/2026)** về kinh tế nhà nước: cho NH quốc doanh **giữ lại lợi nhuận sau thuế để tăng vốn
  điều lệ** thay vì nộp cổ tức tiền mặt vào ngân sách; mục tiêu ≥3 NHTM Nhà nước vào top-100 châu Á theo tài sản; triển khai qua NQ
  29/NQ-CP và QĐ 464/QĐ-NHNN (ngày ban hành: **không có số**). Nghị định hướng dẫn riêng tỷ lệ giữ lại: **không tìm thấy**.
  Tiền lệ: QĐ TTg 06/07/2026 bổ sung vốn cho NH quốc doanh chưa niêm yết ~29-30 nghìn tỷ cho 2025-2027 (từ LN phải nộp ngân sách)
  (vietnamfinance 15/07); ít nhất 1 NH niêm yết được chấp thuận nâng vốn điều lệ 2026; ĐHCĐ 04/2026 các NH niêm yết trình phương án
  dùng LN còn lại chia cổ tức **cổ phiếu** (vnbusiness 12/03; vietnamfinance 2026).
- **Chuỗi phê duyệt [NỀN, cần kiểm]:** phương án tăng vốn của NH Nhà nước chi phối cần ĐHCĐ + chấp thuận NHNN + ý kiến/quyết định của
  cơ quan đại diện chủ sở hữu (Bộ TC/Chính phủ, có lúc phải Quốc hội cho phần vốn NS) ⇒ **thời điểm tăng vốn là biến hành chính**, không
  do NH tự quyết. Tỷ lệ sở hữu Nhà nước tối thiểu ở 3 NH niêm yết **~65%** theo đề án cơ cấu lại [NỀN]; trần room ngoại 30% [NỀN].
- **Hệ quả cổ đông [UĐ]:** NQ 79 chuyển nhóm quốc doanh từ "cổ tức tiền mặt thấp + tăng vốn chậm" sang "cổ tức cổ phiếu lớn + ít tiền
  mặt" ⇒ số cổ phiếu lưu hành tăng theo nhịp phê duyệt; BVPS/EPS phải tính theo số cổ phiếu ĐIỀU CHỈNH. Không phải pha loãng giá trị
  (LN giữ lại vẫn thuộc cổ đông) nhưng là bẫy đọc chỉ số (§7). Phát hành riêng lẻ/chiến lược (nếu có) mới là pha loãng thật — phụ thuộc
  giá phát hành vs BVPS.
- Toàn hệ thống: NH niêm yết dự kiến tăng ~**128 nghìn tỷ** vốn cổ phần 2026, gấp >7 lần 2025 (FiinGroup, vietnamfinance 15/07) ⇒
  cung cổ phiếu NH lớn trên thị trường 2026-2027 (kênh định giá, không phải LNST).

### 2d. Khung pháp lý chung (tái dùng file 31/10 §2c, không lặp)
Luật TCTD sửa đổi 96/2025 (quyền thu giữ TSBĐ, hiệu lực 15/10/2025); TT 02/2023 hết hiệu lực 31/12/2024 [NỀN]; TT 50/2026 (LDR, LCR
50→100% 2028-2033, NSFR 90→100% 2028-2030); xử lý NH yếu kém (4 NH đã chuyển giao bắt buộc [NỀN]; SCB còn KSĐB). **Riêng nhóm quốc
doanh:** vai trò "chủ lực" (NQ 79) ⇒ kênh dẫn chính sách (gói NOXH, giảm lãi theo chỉ đạo, có thể được giao nhận chuyển giao/hỗ trợ
TCTD yếu kém [NỀN]) — lợi thế niềm tin huy động đổi lấy nghĩa vụ phi thương mại.

## 3. Cấu trúc cạnh tranh
| Mảng | Dữ kiện | Đọc cho nhóm quốc doanh [UĐ] |
|---|---|---|
| Quy mô / niềm tin | ~40-45% tài sản, >45% tín dụng (VNBA 21/05); tổng tài sản từng NH ~2,4-3,3 triệu tỷ cuối 2025 (vnbusiness 12/01) | Bảo lãnh ngầm của Nhà nước ⇒ hút tiền gửi khi có sự cố ở NH tư nhân (2022 SCB [NỀN]). Lợi thế chi phí vốn BQ, không phải chi phí biên |
| Nguồn vốn rẻ đặc quyền | KBNN 99,6% tại NHTM Nhà nước; 3 NH niêm yết 521 nghìn tỷ (Q3); đấu thầu tiền gửi KBNN công khai nhưng nhóm quốc doanh vẫn chiếm ưu thế | Đặc quyền HÀNH CHÍNH (lực thứ 6): có thể đổi khi Bộ TC sửa NĐ 24/2016 (01/2027) hoặc KBNN rút để giải ngân. Rẻ nhưng ngắn và biến động |
| Cho vay | Tỷ trọng SXKD 51-66%; doanh nghiệp lớn, DNNN, hạ tầng, NOXH; tăng 6-10% YTD (Q3 ước) | Bán buôn biên mỏng, rủi ro tập trung khách lớn; được loại trừ khỏi room ở NOXH/KCN/18 dự án ⇒ khối lượng 2027 phụ thuộc đầu tư công |
| Bán lẻ / thẻ / thanh toán | Nền khách hàng lớn nhất [NỀN]; tư nhân dẫn CASA (một NH tư nhân ~42-43%; ngành 20,2% Q2) | CASA nhóm quốc doanh: **không có số** cấp nhóm ⇒ DD phải lấy |
| Giá huy động | Neo niêm yết thấp nhất (quầy 5,4%; online 6,8 / 1 NH 5,4) | Neo theo chỉ đạo ⇒ mất thị phần tiền gửi dân cư giá-nhạy vào NH tư nhân (ẩn ~9%) [UĐ]; bù bằng CCTG/cấp 2 |
| Tín dụng ngoại bảng | +24% H1, 18% dư nợ (ngành) | Bảo lãnh/LC cho dự án lớn — tập trung ở nhóm quốc doanh [NỀN]; CV 9608 trừ mua lại LC miễn truy đòi khỏi room |
| Định giá thị trường | Ngành P/B 1,42x (TB 5 năm 1,63x), ROAE 16,2% vs Ke 14,6% (VDSC, Elibook 04/10); khối ngoại bán ròng CP NH **>37 nghìn tỷ 9T/2026** (> cả 2025) | Kênh định giá/dòng tiền, KHÔNG dùng làm luận điểm cơ bản; FTSE (hiệu lực 21/09/2026) ưu tiên NH vốn hoá lớn còn room — nhóm quốc doanh room ngoại bị giới hạn bởi sở hữu NN ~65% [NỀN] |
| ROE lịch sử nhóm | ROE NHTM Nhà nước 12,9% (2017) → đỉnh 20,7% (2022) → ~18-20% (2023-2025); thấp hơn nhóm cổ phần | TC KT-TC (nghiên cứu, 2026) — 1 nguồn học thuật, coi là [DK cấp 2] |

## 4. Phân loại chế độ (biến số quyết định LNST nhóm quốc doanh)

### 4a. Tầm 4 quý (Q4/2026-Q3/2027)
| Nhãn | Xác suất | Lý do |
|---|---|---|
| **ADMIN_GATED** | **0,55** | Mọi biến số lớn của nhóm do VĂN BẢN quyết: khối lượng (room ~15%, chế tài hạ chỉ tiêu 2027 qua CV 9608/10488, loại trừ NOXH/KCN/18 dự án), giá (CV 9608/9736 ép huy động −0,5pp + cho vay −1,5-2pp, thanh tra T11 báo cáo TTg), thanh khoản (LDR: KBNN 50% từ 01/08, TT 50 95% từ 01/12, NĐ 24 sửa 01/2027), vốn (NQ 79, tăng vốn cần chấp thuận chủ sở hữu). Cao hơn nhóm tư nhân (0,45 ở file 31/10) vì nhóm quốc doanh vừa là đối tượng vừa là công cụ của chỉ đạo |
| **CYCLICAL** | **0,25** | Chu kỳ chất lượng tài sản: nhóm 2 +26-33%, NPL tuyệt đối +18-36% YTD ở cả 3 NH niêm yết; LN 2026 dựa phần vào giảm dự phòng ⇒ chi phí tín dụng 2027 là biến dao động lớn nhất. Thấp hơn nhóm tư nhân vì đệm bao phủ cấp nhóm ~150% |
| **STRUCTURAL** | **0,20** | Vốn ~20% vốn điều lệ hệ thống gánh ~45% tín dụng; Basel III bắt buộc 2030 (+ khả năng D-SIB 1-3,5%); NIM thấp cấu trúc do vai trò chính sách; nền vĩ mô Loại-1 STRUCTURAL_ACCUMULATION (ambiguous) |

### 4b. Tầm 3-5 năm (2027-2030)
| Nhãn | Xác suất | Lý do |
|---|---|---|
| **STRUCTURAL** | **0,45** | Ràng buộc vốn (Basel III 2030, D-SIB) + nhiệm vụ chủ lực (NQ 79, top-100 châu Á) ⇒ tăng trưởng tài sản bị trần bởi tốc độ tích luỹ vốn; NQ 79 nới trần đó (giữ LN) — là thay đổi cấu trúc CÓ LỢI về khối lượng, đổi lấy cổ tức tiền mặt |
| **ADMIN_GATED** | **0,35** | Lộ trình bỏ room (TTg yêu cầu từ 2025, "chưa gỡ về danh nghĩa" 08/2026; bỏ room làm CAR thành thước đo — vietnamfinance 03/08) và quy chế KBNN là hai công tắc hành chính lớn nhất; mốc chưa có |
| **CYCLICAL** | **0,20** | Một chu kỳ tín dụng-BĐS đầy đủ nằm trong 3-5 năm |

- **Pha [UĐ]:** tín dụng nhóm quốc doanh **chậm hơn hệ thống** (vốn + room), NIM **đáy mỏng, bị ép hành chính**, chất lượng tài sản
  **sớm-giữa pha xấu đi** (tầng sớm xấu đồng loạt, đệm nhóm còn dày nhưng phân tán), vốn **sắp được nới bằng cơ chế giữ LN** (NQ 79).
- **Confidence: `ambiguous` (~60/40)** — chưa biết lớn nhất: (a) LN 2026/2027 của nhóm được giữ lại bao nhiêu và khi nào được duyệt;
  (b) Q4 có phải trích bù dự phòng không; (c) KBNN rút bao nhiêu trong Q4 và NĐ 24 sửa ra sao; (d) NHNN có thực sự trừ room 2027 với NH
  không đạt CV 9608 (khó áp với nhóm quốc doanh — [UĐ]).

**Biến số chính quyết định LNST nhóm Q4/2026-Q3/2027 (xếp theo độ nhạy, [UĐ]):**
1. **Chi phí tín dụng**: tốc độ chuyển nhóm 2 → nợ xấu; có phải xây lại dự phòng sau năm giảm dự phòng; thu hồi nợ ngoại bảng (Luật 96).
2. **NIM**: chỉ thị giảm lãi cho vay SXKD (tỷ trọng 51-66%) vs KBNN rút + CCTG/cấp 2 đắt; tốc độ tái định giá tiền gửi quầy.
3. **Khối lượng**: room 2027, phần loại trừ (NOXH/KCN/18 dự án), giải ngân đầu tư công (kéo cầu vay hạ tầng), vốn sau tăng vốn.
4. **Vốn/cổ tức**: thời điểm duyệt giữ LN/cổ tức cổ phiếu (số cổ phiếu), cấp 2 đắt lên.
5. **Ngoài lãi**: phí thanh toán/thẻ, bảo lãnh, ngoại hối (NHNN mua USD 25.500; swap), lãi/lỗ TPCP (10Y Δ12T +0,57pp).
6. **Ngoại sinh**: Fed 12/2026 (khả năng tăng), DXY 103,5, US10Y 5,13 ⇒ áp lực tỷ giá → liên NH.

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-11-17; chấm bằng nguồn công bố đầu tiên ≤ ngày chấm; không có nguồn ⇒ "không chấm được", không suy)
Mệnh đề ngành/hệ thống đã khoá ở file 31/10 (F1-F12: tín dụng 2026, Big-4 12M online, CCTG, lãi BQ giao dịch mới, liên NH 3M T12,
NPL/bao phủ/NIM/LNTT 27 NH, tái cấp vốn, TT 50, tỷ giá) và REGIME READ #3 (10/11) **không khoá lại**. Dưới đây chỉ mệnh đề riêng nhóm
quốc doanh. "3 NH" = 3 NHTM Nhà nước niêm yết; số lấy từ BCTC hợp nhất/thuyết minh chính thức (người chấm được phép đọc cấp NH).

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| Q1 | Tổng tiền gửi KBNN tại 3 NH (thuyết minh) ngày 31/12/2026 **< 521,1 nghìn tỷ** (mức 30/09) | 0,65 | 2027-02-28 | BCTC Q4 thuyết minh, hoặc tổng hợp báo chí cùng phạm vi |
| Q2 | Trung bình đơn giản NPL hợp nhất 3 NH tại 31/12/2026 trong **[1,2%; 1,8%]** | 0,75 | 2027-02-28 | BCTC Q4 |
| Q3 | Ít nhất **1/3** NH có bao phủ nợ xấu (dự phòng chung + cụ thể / nợ nhóm 3-5) **< 100%** tại 31/12/2026 | 0,60 | 2027-02-28 | BCTC Q4 |
| Q4 | Tổng nợ nhóm 2 của 3 NH tại 31/12/2026 **cao hơn** 31/12/2025 ít nhất **+15%** | 0,75 | 2027-02-28 | BCTC Q4 thuyết minh |
| Q5 | Trung bình đơn giản NIM (thu nhập lãi thuần năm hoá / tài sản sinh lãi BQ, tự tính cùng công thức 2 quý) của 3 NH Q4/2026 **≤** Q3/2026 | 0,65 | 2027-02-28 | BCTC Q3, Q4 |
| Q6 | Tăng trưởng cho vay khách hàng cả năm 2026 (hợp nhất) của **ít nhất 2/3** NH **thấp hơn** tăng trưởng tín dụng toàn hệ thống 2026 do NHNN công bố | 0,60 | 2027-02-28 | BCTC Q4 + NHNN 01/2027 |
| Q7 | Tổng chi phí dự phòng rủi ro tín dụng năm 2026 của 3 NH **cao hơn** năm 2025 | 0,45 | 2027-02-28 | BCTC Q4 (KQKD cả năm) |
| Q8 | Ít nhất 1/3 NH **hoàn tất** đợt tăng vốn điều lệ bằng cổ tức cổ phiếu/LN giữ lại (CBTT kết quả phát hành hoặc NHNN sửa giấy phép vốn) trong **18/11/2026 → 30/06/2027** | 0,80 | 2027-06-30 | CBTT HOSE / NHNN |
| Q9 | Chính phủ ban hành nghị định sửa NĐ 24/2016 (quản lý ngân quỹ, tiền gửi KBNN) **trước 31/01/2027** | 0,45 | 2027-01-31 | Công báo / thuvienphapluat |
| Q10 | NHNN chính thức công bố **bỏ giao chỉ tiêu tăng trưởng tín dụng riêng từng NH** cho năm 2027 (văn bản hoặc họp báo) **trước 31/03/2027** | 0,15 | 2027-03-31 | NHNN |
| Q11 | NHNN ban hành văn bản bổ sung **phụ phí vốn D-SIB** (hoặc danh sách NH quan trọng hệ thống kèm yêu cầu vốn bổ sung) **trước 31/12/2027** | 0,25 | 2027-12-31 | NHNN / thuvienphapluat |
| Q12 | Big-4 12M **tại quầy** cao nhất ngày 31/03/2027 **≤ 5,9%** (không quay lại mức trước CV 9608) | 0,75 | 2027-03-31 | báo tổng hợp biểu cùng tuần, có ngày |

Ghi chú [UĐ]: Q1 dựa trên 74,1% giải ngân tới 31/10 và mùa giải ngân Q4, nhưng thu NS cuối năm có thể bù — 0,65 không cao hơn. Q3 dựa
trên khoảng 73-243% hiện tại và mùa trích lập Q4 (có thể kéo NH thấp nhất lên). Q4 nghiêng cao vì nhóm 2 đã +26-33% sau 9T. Q7 cố ý
quanh 0,5: năm 2026 nhóm giảm dự phòng, nếu Q4 trích bù mạnh thì vượt. Q10 thấp vì "chưa gỡ về danh nghĩa" và NHNN vừa dùng room làm
chế tài trong CV 9608/10488.

## 6. Chỉ báo dẫn dắt (theo dõi tuần/tháng/quý)
1. **Tuần**: liên NH ON/1M/3M + OMO lưu hành (TBTC thứ Bảy); NHNN mua USD giao ngay/swap; CCTG Big-4 6T/12T (`cctg_rate_vn*.csv`);
   Big-4 12M online + quầy TÁCH riêng (chuỗi hiện lưu MAX).
2. **Tháng**: tín dụng YTD (NHNN), giải ngân đầu tư công (Bộ TC ~ngày 3-5), CPI/core (NSO ~ngày 6), văn bản thực thi CV 9608/10488
   (kết quả thanh tra T11 báo cáo TTg), NĐ 24/2016 sửa đổi.
3. **Quý**: BCTC Q4 (~cuối 01/2027): KBNN, nhóm 2, bao phủ, dự phòng, NIM, CASA nhóm quốc doanh; SSI/FiinRatings tổng hợp cấp nhóm.
4. **Sự kiện**: phê duyệt giữ LN/cổ tức cổ phiếu (Bộ TC/TTg/NHNN), lộ trình bỏ room 2027, D-SIB, Fed 09/12/2026.

## 7. DD cần kiểm gì — một NHTM Nhà nước niêm yết
(Bổ sung cho 25 mục của file 31/10 §7 — áp nguyên các mục đó; dưới đây chỉ phần RIÊNG nhóm quốc doanh và bẫy định giá ngành NH.)

**A. Bẫy định giá riêng ngành NH (đọc TRƯỚC khi chạm vào mô hình)**
1. **P/PCF, EV/EBITDA, FCFE kiểu doanh nghiệp sản xuất KHÔNG dùng được cho NH**: CFO của NH chứa biến động tiền gửi/cho vay (đó là
   "nguyên liệu" kinh doanh, không phải dòng tiền tự do); CFO có thể âm/dương cực đoan theo quý. Không so P/PCF NH với ngành khác,
   không đưa NH vào xếp hạng chéo theo P/PCF (đúng bẫy "bank PCF ≠ industrial PCF" của fleet). Khung V_ngắn/V_dài/C4/D2 (nền FCFE) của
   skill DD **không áp nguyên cho NH** — DD nên ghi rõ "không áp dụng" thay vì in số vô nghĩa.
2. **Định giá theo P/B – ROE – Ke**: P/B hợp lý ≈ (ROE bền − g) / (Ke − g) [công thức chuẩn, NỀN]. Dùng **ROE bền** (trung bình chu
   kỳ, hoặc ROE trước dự phòng trừ chi phí tín dụng chuẩn hoá), KHÔNG dùng ROE năm giảm dự phòng. Kiểm g ≤ ROE × (1 − tỷ lệ cổ tức tiền).
3. **BVPS phải điều chỉnh**: (a) theo số cổ phiếu sau cổ tức cổ phiếu/phát hành đã duyệt (kể cả chưa đăng ký); (b) trừ phần thiếu hụt
   dự phòng so chuẩn bao phủ chọn (vd 100%) và **lãi dự thu chưa thu** vượt mức bình thường; (c) phần tài sản Có khác/phải thu bất
   thường. Báo cả P/B thô và P/B điều chỉnh.
4. **Cổ tức cổ phiếu ≠ thu nhập**: cổ tức cổ phiếu chỉ đổi số cổ phiếu (không phải lợi suất tiền); EPS/BVPS lịch sử phải điều chỉnh
   hồi tố; "tỷ lệ cổ tức %" tính trên mệnh giá 10.000đ, KHÔNG phải trên giá. Phát hành riêng lẻ/chiến lược dưới BVPS mới là pha loãng
   giá trị.
5. **ROE bị nâng bởi đòn bẩy, không phải hiệu quả**: nhóm quốc doanh có vốn ~20% hệ thống gánh ~45% tín dụng ⇒ ROE cao một phần do CAR
   sát sàn. Khi Basel III 2030 buộc tăng CET1, ROE pha loãng cơ học ⇒ báo ROE ở mức CET1 mục tiêu (vd 9-10%) cạnh ROE hiện tại.
6. **Ke** theo khung fleet (Ke nội địa β ~1,1, khoảng 12,3-13,4%; neo r 13,5% gắn lãi huy động 12T — luật 03/11) — NH quốc doanh có β
   thị trường riêng, DD kiểm β thật, không mặc định 1,1. Lãi huy động 12T neo dùng **effective = max(Big-4 12M, CCTG 12M)** = 7,4%
   (16/11), không dùng niêm yết quầy 5,4%.

**B. Nguồn vốn và NIM (riêng nhóm quốc doanh)**
7. **Tiền gửi KBNN**: số dư từng quý 2025-2026, kỳ hạn, lãi suất (thuyết minh tiền gửi khách hàng/tiền gửi Chính phủ); tỷ trọng / tổng
   huy động; độ nhạy NIM nếu KBNN rút về mức cuối 2025 (cờ: KBNN > 8% tổng huy động).
8. **CASA** tách cá nhân / DN / tổ chức nhà nước; xu hướng 8 quý.
9. **CCTG + trái phiếu phát hành + cấp 2**: lưu hành, lãi suất, lịch đáo hạn 2027-2028; tỷ trọng / tổng nguồn vốn (cờ: tăng > 2pp YoY).
10. **Tỷ trọng cho vay SXKD/ưu tiên và các gói chỉ đạo** (NOXH, SME, 153 nghìn tỷ, gói sau CV 9608): quy mô, lãi suất, phần dư nợ được
    giảm lãi ⇒ ước tác động NIM của CV 9608 riêng NH.
11. **LDR theo TT 22 và theo TT 50 (từ 01/12)** + phần KBNN được tính (50%); tỷ lệ vốn ngắn hạn cho vay TDH (trần 40%). Cờ: LDR(TT22)
    > 83% trước 01/12.

**C. Chất lượng tài sản**
12. NPL, **nhóm 2** (Δ YTD so tăng cho vay), bao phủ, nợ xoá sổ, nợ ngoại bảng, lãi dự thu — 8 quý; **NPL formation** = Δ nợ xấu + xoá sổ.
    Cờ: nhóm 2 tăng > 2 lần tốc độ cho vay (hiện cả 3 NH đều chạm cờ này theo khoảng §2b).
13. **Chi phí dự phòng 2026 vs 2025** và PPOP: LN tăng do PPOP hay do giảm dự phòng? Cờ: dự phòng giảm trong khi nhóm 2 tăng.
14. **Tập trung khách lớn / DNNN / hạ tầng / BĐS**: top-10/20 nhóm khách / VCSH; cho vay chủ đầu tư BĐS và dự án hạ tầng; trái phiếu DN
    nắm giữ; **tín dụng ngoại bảng (bảo lãnh, LC)** / VCSH (ngành +24% H1).
15. **Nghĩa vụ chính sách/phi thương mại**: nhận chuyển giao/hỗ trợ TCTD yếu kém, cho vay theo chỉ định, khoanh/giãn nợ theo chương trình
    Chính phủ — có trong thuyết minh/BCTN không.

**D. Vốn và cổ đông**
16. **CAR, CET1, Tier 1** theo TT 41 và TT 14 (nếu đã chuyển), RWA/tổng tài sản; khoảng cách tới 10,5% + giả định D-SIB 1-2% (cờ: CET1 <
    9% ước lượng).
17. **Kế hoạch tăng vốn**: LN giữ lại theo NQ 79 (năm nào, đã duyệt chưa, cấp duyệt), cổ tức cổ phiếu (tỷ lệ, ngày chốt dự kiến), phát
    hành riêng lẻ/chiến lược; tỷ lệ sở hữu Nhà nước hiện tại vs sàn (~65% [NỀN]) ⇒ phát hành cho NĐT ngoài bị giới hạn bởi sàn đó.
18. **Room ngoại** còn lại (trần 30% [NỀN]), cổ đông chiến lược nước ngoài, free float thật (trừ Nhà nước + chiến lược).
19. **Cổ tức tiền mặt** lịch sử (thường thấp, ~4-5% mệnh giá [DK cấp 2, năm không xác nhận]) — tỷ lệ chi trả / LNST để kiểm g.

**E. Quản trị / pháp lý**
20. Kết luận thanh tra NHNN/Kiểm toán Nhà nước gần nhất, các vụ án liên quan cán bộ/khách hàng lớn (WARNING theo luật 27/09, không
    chặn); ý kiến kiểm toán; chênh LN trước/sau kiểm toán. Quan hệ với cơ quan đại diện chủ sở hữu (Bộ TC/NHNN) và chỉ tiêu được giao.

## 8. Điều gì làm tôi sai
- BCTC Q4 cho thấy nhóm 2 của nhóm quốc doanh **giảm** QoQ và bao phủ tăng mà không cần trích bù lớn ⇒ hạ CYCLICAL (tầng sớm chỉ là
  nhiễu chuyển nhóm kỹ thuật).
- KBNN tại 3 NH **tăng** lại Q4 và NĐ 24 sửa theo hướng tăng tiền gửi có kỳ hạn KBNN ⇒ áp lực NIM nhẹ hơn tôi đọc.
- Chính phủ duyệt nhanh giữ toàn bộ LN 2025-2026 (cả 3 NH niêm yết) trong H1/2027 ⇒ ràng buộc vốn nới sớm, ADMIN_GATED nghiêng chiều
  thuận về khối lượng.
- Ngược lại: CCTG Big-4 ≥ 7,8% hoặc 3M liên NH > 7,5% kéo dài sang 2027, hoặc một sự kiện có tên buộc nhóm quốc doanh nhận/hỗ trợ một
  TCTD yếu kém ⇒ chuyển đọc sang episode (CONFIDENCE_LIQUIDITY trên nền Loại-1), và nghĩa vụ phi thương mại thành biến số chính.

**Không phải khuyến nghị mua/bán. Không dùng làm cổng/sizing.**

## Nguồn (ngày công bố; một số URL có tên NH — người đọc blind sau có thể bỏ qua)
- Snapshot vĩ mô tự sinh: `bin/macro_snapshot_asof.py --asof 2026-11-17` (tav2_bq.macro_indicator, TE UNVERIFIED) — 17/11/2026.
- Nội bộ: `data/deposit_rate_vn_events.csv` (16/11), `cctg_rate_vn_events.csv` / `_6m_` / `_tier2_` (02/11), `refresh_deposit_cctg_weekly_2026-11.log` (16/11); `vn_macro_regime_history.md` REGIME READ #3 (10/11); `sector_read_ngan_hang_20261031.md`.
- TBTC, thị trường tiền tệ tuần 9-13/11 — 14/11/2026: https://thoibaotaichinhvietnam.vn/thi-truong-tien-te-tuan-9-13-11-usd-bat-tang-kich-hoat-hai-cong-cu-giua-nhip-hut-rong-hon-25-000-ty-dong-206938.html
- TBTC, tuần 2-6/11 — 06/11/2026: https://thoibaotaichinhvietnam.vn/thi-truong-tien-te-tuan-2-6-11-vay-muon-qua-dem-vuot-1-trieu-ty-dong-van-thanh-khoan-mo-qua-mua-cao-diem-206551.html
- Vietbao (dẫn thuonghieucongluan), CV 10488/NHNN-TTNH thanh tra giảm lãi suất trong T11 — 13/11/2026: https://vietbao.vn/ngan-hang-nha-nuoc-thanh-tra-viec-giam-lai-suat-ngay-trong-thang-11-615704.html
- Vietbao (SSI), nợ xấu Q3 2,09%, nhóm 2 1,63%, bao phủ 77%; quốc doanh ~1,3% / ~150% — 08/11/2026: https://vietbao.vn/no-xau-ngan-hang-tang-tro-lai-chat-luong-tai-san-tao-khoang-cach-giua-cac-nha-bang-614997.html
- VnBusiness, nợ xấu 28 NH 340,4 nghìn tỷ, bao phủ ~80% thấp nhất 5 năm — 05/11/2026: https://vnbusiness.vn/no-xau-va-no-tiem-an-tang-toc-dem-du-phong-ngan-hang-roi-xuong-day-5-nam.html
- VnBusiness, tiền gửi KBNN tại 3 NH quốc doanh 521,1 nghìn tỷ Q3 — 02/11/2026: https://vnbusiness.vn/hon-nua-trieu-ty-dong-tien-gui-cua-kho-bac-nam-tai-ba-ngan-hang-quoc-doanh.html
- TTTCTT, hệ thống TCTD 30,89 triệu tỷ tài sản, LDR 76,07% — 11/11/2026: https://thitruongtaichinhtiente.vn/he-thong-to-chuc-tin-dung-cham-moc-30-89-trieu-ty-dong-tai-san-86950.html
- Bộ TC qua VietnamPlus/TBTC/Báo Đấu thầu, giải ngân đầu tư công 74,1% tới 31/10 — 11/2026: https://thoibaotaichinhvietnam.vn/giai-ngan-von-dau-tu-cong-dat-74-1-ke-hoach-sau-10-thang-206359.html ; https://baodauthau.vn/10-thang-nam-2026-giai-ngan-von-dau-tu-cong-dat-741-ke-hoach-post211842.html
- Elibook, bức tranh Q3/2026 ngành NH (VDSC/MBS/HSC) — 04/10/2026: https://elibook.vn/?p=123663
- VnBusiness, phân hoá Q3 (ước MBS) — 28/09/2026: https://vnbusiness.vn/cuoc-phan-hoa-nghin-ty-tai-nhom-ngan-hang-quy-iii2026.html
- Diễn đàn DN (VDSC), NIM Q3 dự phóng 3,18%: https://diendandoanhnghiep.vn/ngan-hang-chu-dong-phong-ve-rui-ro-10185351.html
- TBTC, LDR Big-4 82,9-84,5% (31/03), dự thảo tính 20% tiền gửi KBNN — 11/05/2026: https://thoibaotaichinhvietnam.vn/ty-le-ldr-ngan-hang-big-4-ap-sat-nguong-85-de-xuat-sua-doi-quy-dinh-ve-tien-gui-kho-bac-nha-nuoc-197129.html
- CafeF, Bộ TC đề xuất sửa NĐ 24/2016 (01/01/2027), KBNN ~740 nghìn tỷ — 04/08/2026: https://cafef.vn/ho-tro-thanh-khoan-he-thong-ngan-hang-bo-tai-chinh-muon-sua-quy-dinh-lien-quan-den-hang-tram-nghin-ty-du-kien-ap-dung-tu-1-1-2027-188260804210004397.chn
- VietnamFinance, thời hậu room tín dụng; TT 08/25/2026; CAR 26 NH ~12% — 03/08/2026: https://vietnamfinance.vn/chuan-bi-cho-cuoc-choi-thoi-hau-room-tin-dung-d148189.html
- VietnamFinance, mở không gian vốn cho Big-4 (NQ 79) — 18/08/2026: https://vietnamfinance.vn/mo-khong-gian-von-de-big4-dan-dat-dong-von-cho-tang-truong-kinh-te-d148894.html
- VNBA, NQ 79 mở dư địa cho NH trụ cột (40-45% tài sản, >45% tín dụng, ~20% vốn điều lệ) — 21/05/2026: https://vnba.org.vn/vi/nghi-quyet-79-nq-tw--mo-rong-du-dia-phat-trien-cho-cac-ngan-hang-tru-cot-21877.htm
- QuanLyNhaNuoc, NQ 79-NQ/TW — 08/01/2026: https://www.quanlynhanuoc.vn/2026/01/08/nghi-quyet-so-79-nq-tw-cua-bo-chinh-tri-ve-phat-trien-kinh-te-nha-nuoc/
- VnBusiness, mùa ĐHCĐ 2026, Big-4 và cơ chế giữ LN — 12/03/2026: https://vnbusiness.vn/mua-dai-hoi-co-dong-2026-co-co-che-dot-pha-big-4-khong-con-lep-ve-truoc-khoi-tu-nhan-trong-cuoc-dua-tang-von.html
- VietnamFinance, chiến dịch tăng vốn 128 nghìn tỷ; QĐ TTg 06/07/2026 — 15/07/2026: https://vietnamfinance.vn/he-thong-ngan-hang-buoc-vao-chien-dich-tang-von-lon-nhat-lich-su-d147636.html
- VnEconomy, TT 14 tác động nhóm quốc doanh — 03/12/2025: https://vneconomy.vn/thong-tu-14-tac-dong-the-nao-den-nhom-ngan-hang-quoc-doanh.htm
- The Leader, vì sao NH quốc doanh yếu thế (CAR 8-10%, D-SIB 1-3,5%) — 26/08/2025: https://theleader.vn/ly-do-khien-cac-ngan-hang-quoc-doanh-yeu-the-trong-cuoc-dua-tang-truong-d41797.html
- VnBusiness, tài sản Big-4 cuối 2025 — 12/01/2026: https://vnbusiness.vn/tai-san-nhom-big-4-lap-ky-luc-khoi-tu-nhan-bam-duoi-quyet-liet.html
- VnBusiness / VNBA, gói NOXH 120 nghìn tỷ, 153 nghìn tỷ — 2026: https://vnbusiness.vn/goi-tin-dung-nha-o-xa-hoi-vuot-153000-ty-dong-cam-ket-cho-vay-tang-gan-3-lan.html ; https://vnba.org.vn/vi/agribank-trien-khai-goi-tin-dung-30-000-ty-dong-cho-nha-o-xa-hoi-23838.htm
- TC KT-TC (nghiên cứu), ROE nhóm NHTM Nhà nước 2017-2025: https://nghiencuu.tapchikinhtetaichinh.vn/tac-dong-cua-ngan-hang-so-den-hieu-qua-tai-chinh-cua-cac-ngan-hang-thuong-mai-nha-nuoc-viet-nam-164578.html
- File 31/10 (CV 9608/9736, TT 50, Luật 96, TT 14, CASA ngành, cấp 2 Big-4, FTSE): xem danh mục nguồn ở `sector_read_ngan_hang_20261031.md`.
