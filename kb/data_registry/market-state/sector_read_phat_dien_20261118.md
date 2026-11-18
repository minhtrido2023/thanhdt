---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-18. KHÔNG biết giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp phát điện cụ thể (xem §0 về rò rỉ danh tính).
blind: YES
as_of: 2026-11-18 (snapshot vĩ mô dd_*_20261118 có áp độ trễ công bố; BQ commodity_prices TE tới 2026-11-16/17; lãi suất PIT tới 2026-11-16; tin web ≤ 2026-11-10)
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành phát điện VN đa nguồn (nhiệt điện khí nội địa + LNG, nhiệt điện than, thuỷ điện, một phần tái tạo). Bán cho EVN/EPTC (người mua duy nhất) qua PPA + thị trường phát điện cạnh tranh (CfD Qc/Pc/FMP). Gồm pipeline cầu, cơ chế giá + nhiên liệu (khí gắn dầu, LNG, than, tỷ giá), rủi ro chính sách (giá điện, PPA, Qc, hạn mức khí, FIT), phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED 2 tầm + theo phân khúc, FORECAST khoá trước có ngày chấm, checklist DD.
---

# SECTOR READ: Phát điện VN đa nguồn (khí/LNG + than + thuỷ + tái tạo), as-of 18/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán /
suy luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải KIỂM trước khi dùng làm số).
**File chị em (đọc kèm, không chép lại):** `sector_read_nhiet_dien_than_20261117.md` (than: PPA 2 thành phần, Qm>Qc, PDP8 +5.300 MW than,
ETS 2028), `sector_read_thuy_dien_20261112.md` (El Niño 2026-27, Qc/CfD, khung 1.110 đ/kWh, tái đàm phán PPA),
`sector_read_khi_dot_lpg_20261109.md` (cung khí, LNG giao ngay vs hợp đồng, Hormuz K1-K3, Lô B), `sector_read_power_consulting_20261028.md`
(PDP8 trượt tiến độ, thiếu nguồn 2027-2030). File này **thêm phần khí/LNG-cho-điện + tái tạo + góc nhìn danh mục đa nguồn**;
xác suất ở §5 cố ý **nhất quán** với các file đó, mệnh đề đã khoá thì chỉ dẫn chiếu.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Snapshot:** đọc đúng file caller chỉ định `agents/Taylor/research/dd_POW_20261118/macro_snapshot_20261118.md`. Không liệt kê/mở
  file nào khác trong thư mục đó.
- **Rò rỉ danh tính (ghi trung thực):** tên thư mục dispatch chứa một chuỗi giống mã chứng khoán và tôi **nhận ra** nó có thể ứng với một
  tổng công ty phát điện thuộc tập đoàn dầu khí nhà nước, có danh mục khí + LNG + than + thuỷ. Prompt của caller cũng nêu tên một cụm dự án
  LNG cụ thể. Tôi không tra mã đó, không mở BCTC/BCTN/báo cáo CTCK/giá cổ phiếu nào. **Kết quả tìm kiếm có trả về (KHÔNG mở):** tên file
  báo cáo doanh nghiệp của CTCK cho chuỗi ký tự đó; một tóm tắt nêu **sản lượng Q1/2026 của cụm LNG đầu tiên thấp hơn đáng kể so với Qc
  phân bổ** và "chủ đầu tư và EVN chưa thống nhất sửa đổi hợp đồng"; kiến nghị Qc ≥85% của một nhà đầu tư nhà nước; tiêu đề KQKD/sản lượng
  của một nhà máy khí Đông Nam Bộ. Tôi chỉ dùng các mẩu này ở mức **cơ chế** (Qm có thể < Qc với LNG; hợp đồng LNG–PPA còn đang sửa) và đưa
  vào checklist DD; **không** để chúng làm nặng/nhẹ phân loại, không dùng số của DN trong bảng nào.
- **BQ (tự truy vấn 18/11):** `tav2_bq.commodity_prices` TE `brent`, `coal`, `liquefied_natural_gas_japan_korea` (daily), `fuel_oil` (sunsirs
  TQ), `eu_natural_gas`; WB CMO `lng_japan` (monthly). Lãi suất PIT: `deposit_rate_vn.effective_deposit_rate('2026-11-18')`,
  `cctg_rate_vn.current_cctg_rate()`, `macro_killswitch_a_status()`. Không dùng `ticker_financial` (sẽ phải chọn DN ⇒ phá blind).
- **Không có số (ghi "không có số", không suy):** FMP/SMP tháng 9-11/2026; tỷ lệ Qc 2026/2027 theo loại hình (than, khí nội, LNG); sản lượng
  tua-bin khí 10T/2025 (để tính YoY); giá khí nội địa bán cho điện (bình quân hệ thống) 2026; giá LNG nhập thực của VN; khung giá CCGT dùng
  **LNG** riêng 2025/2026 (QĐ 1313/QĐ-BCT có tồn tại, trần không đọc được); KH vận hành hệ thống 2027 (chưa ban hành tới as-of); KQKD 9T/2026
  hợp nhất EVN; kết quả cuối của tranh chấp FIT tái tạo; tầng C/E của bảng chi phí vốn.

## 1. Snapshot vĩ mô + chuỗi giá năng lượng
Bảng ánh xạ ngành của snapshot **không có dòng "Điện"**; tôi tự chọn chỉ báo kéo cầu điện / chi phí nhiên liệu / chi phí vốn.

| Chỉ báo | Giá trị | Δ3T / Δ12T | Đọc cho phát điện |
|---|---|---|---|
| Sản xuất CN YoY | 15,0% (T10) | +0,5 / +4,6pp | Phụ tải công nghiệp mạnh, khớp sản lượng điện T10 +14,3% |
| GDP YoY | 9,95% (Q3) | +1,14 / +1,70pp | Nền cầu điện ~10%/năm (độ co giãn ~1) |
| PMI SX | 52,3 (T10) | −0,6 / −2,2 | Mở rộng, đà chậm nhẹ — chưa là tín hiệu hạ phụ tải |
| FDI luỹ kế YTD | 24,08 tỷ USD (T10) | +13,05% 12T | Đường ống phụ tải KCN 2027-28 tiếp tục; nhu cầu DPPA/xanh |
| Xuất/nhập khẩu | 59,5 / 58,2 tỷ USD (T9) | +41% / +47% 12T | Hoạt động chế tạo nóng; cán cân T10 +7,3 tỷ USD đỡ VND |
| CPI YoY / lõi | 5,09% (T10) / 4,45% (T9) | +1,84 / +1,15pp 12T | **Lực cản chính trị lên giá điện bán lẻ** — EVN vừa giảm 2% từ 01/11 |
| USD/VND | 25.712,5 (17/11) | −1,77% / **−2,54%** | VND lên giá ⇒ nhiên liệu nhập (LNG/than) quy VND nhẹ hơn; lỗ tỷ giá nợ USD giảm |
| US 10Y / DXY | 5,15% / 103,6 | +1,04pp / +4,1% 12T | Đuôi xấu: đô la mạnh đảo chiều VND — chưa là xu hướng |
| Brent TE (USD/bbl) | TB T11 (12 phiên tới 17/11) **96,73**; 17/11: 93,07 | TB T10 107,51 (đỉnh); TB T11/2025 63,44 ⇒ **+52% YoY** [DK, BQ] | Qua đỉnh T10; khí nội địa gắn MFO/dầu ⇒ giá khí cho điện vẫn cao |
| FO TQ (sunsirs, CNY/t) | TB T11 **7.935** | T11/2025 5.380 ⇒ **+47%**; vẫn **tăng** so T10 (7.713) [DK, BQ] | Proxy hướng cho MFO châu Á — **phân kỳ với Brent** (chưa giảm) |
| LNG giao ngay ĐBÁ (TE, USD/MMBtu) | TB T11 **31,13**; **16/11: 27,58** (13/11: 31,35) | T11/2025 11,24 ⇒ ×2,8; T3 18,4 → T10 28,4 [DK, BQ] | Phiên 16/11 **−12%** — tín hiệu đầu tiên qua đỉnh, 1 phiên chưa là xu hướng |
| LNG Nhật bình quân (WB, ~hợp đồng gắn dầu) | **16,59** (T10) | T10/2025 11,10 ⇒ +49% [DK, BQ] | Giá hợp đồng ≈ ½ giao ngay — người mua tender giao ngay chịu gấp đôi |
| Newcastle (TE, USD/t) | TB T11 **143,91** | T10 150,28 (đỉnh); T11/2025 110,33 ⇒ +30% [DK, BQ] | Than vẫn rẻ hơn khí/LNG rất xa trong thứ tự điều độ |

**Thứ tự chi phí biến đổi (merit order) tự tính [UĐ, thông số NỀN]:**
- CCGT dùng LNG, suất hao 6.543 BTU/kWh (thông số khung giá 2026), cước 1,87 USD/MMBtu, tỷ giá 25.712:
  **LNG giao ngay 31,1 ⇒ ~5.550 đ/kWh; LNG gắn dầu 16,6 ⇒ ~3.100 đ/kWh**.
- CCGT khí nội địa ~9,7-10 USD/MMBtu tại hàng rào [DK cấp 2, một dự báo môi giới cho một nhà máy Đông Nam Bộ], suất hao ~7.000 BTU/kWh [NỀN]
  ⇒ **~1.750-1.800 đ/kWh**.
- Than nội (file than): nhiên liệu ~**1.234 đ/kWh**. Trần SMP 2026: **1.725 đ/kWh** (file thuỷ điện).
- ⇒ **LNG đứng ngoài thị trường về kinh tế** (gấp 2-3 trần SMP): chỉ chạy nhờ Qc hoặc ràng buộc an ninh hệ thống. **Khí nội địa nằm sát trần
  SMP**: là nguồn biên của miền Nam. Than đứng trước khí.

### 1b. Chi phí vốn — bảng 5 tầng (ngành nợ dài hạn: nhà máy cũ vay ngoại tệ ECA/ODA, dự án mới vay VND thả nổi + ngoại tệ [NỀN])
| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (16/11; đi ngang từ 03/10) | Tách online / tại quầy và 6M: **không có số** (series lưu MAX) |
| B. Bán hành chính | CCTG 12M Big-4 cao nhất | **7,4%** (02/11) | Spread CCTG − tiết kiệm 12M = **+0,6pp**; từng NH, mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi ẩn, số NH ≥7% | không có số | |
| D. Thị trường | LNH 3M | **6,63%** (13/11; −1,13pp 3T, +0,23pp 12T) | **Nhích lại** từ 6,33% (11/11) trong 2 phiên. OMO/tín phiếu, trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y (chỉ tin Δ) | 4,57 (+0,00 3T / +0,58pp 12T) | Lãi dài hạn cao hơn năm trước |
| E. Lượng | Tín dụng vs huy động YTD, LDR, văn bản nới | không có số lượt này | |

Đồng thuận/phân kỳ [UĐ]: **HƯỚNG** — A, B đi ngang; D 3T giảm nhưng 2 phiên gần nhất nhích lên; D dài hạn +0,58pp/12T ⇒ không proxy nào báo chi
phí vốn VND tăng mạnh 3-6T, nhưng cũng **không** có dấu hiệu hạ. **MỨC** — chi phí biên (CCTG 7,4%) cao hơn niêm yết ~0,6pp. Kill-switch A
(>7,5%) **CLEAR** (7,4%, age 2 ngày). Với genco có dự án LNG mới đang trả nợ, lãi VND là biến **cấp 1** (khác nhà máy than cũ); với nhà máy cũ,
biến tài chính chính là **tỷ giá** và **khoản phải thu chênh lệch tỷ giá từ EVN**. Độ tin cậy trung bình (thiếu C, E).

## 2. Pipeline cầu
### 2a. Phụ tải — STRUCTURAL, mạnh, đang tăng tốc
- Hệ thống **10T/2026: 297,4 tỷ kWh (+9,8%); T10: 31,58 tỷ kWh (+14,3%); NSMO dự báo T11: 28,9 tỷ kWh (+14,4%)** [DK, EVN/NSMO 03/11/2026].
  EVN 9T: 265,79 tỷ kWh (+9,3%) [DK, EVNNPC/lsvn T10/2026]. BCT ước cả năm **356,2 tỷ kWh (+10,3%)**; KH 2026 phương án cơ sở 350,007 tỷ kWh
  (QĐ 3477/QĐ-BCT 28/11/2025) ⇒ **thực tế vượt kế hoạch** [DK]. Pmax 57.537 MW (T6), +6,4% so đỉnh 2025 [DK, file than].
- **2027:** cầu dự báo +~10%; BCT cảnh báo **thiếu 4.256 MW công suất / 2,9 tỷ kWh năm 2027** (miền Bắc thiếu 5.680 MW), tăng lên 13.964 MW
  năm 2030 [DK, BCT 15/09 và 07/11/2026]. Mục tiêu cắt ≥3.000 MW đỉnh miền Bắc bằng DR (CV 10790/VPCP-CN 22/10/2026) [DK].
- Snapshot đồng thuận: IP +15%, FDI +13%, GDP 9,95% ⇒ không có tín hiệu hạ phụ tải trong 6-12T. ⇒ [UĐ] **Rủi ro cầu ở cấp hệ thống ≈ 0**;
  rủi ro thật nằm ở **phân bổ sản lượng giữa các loại nguồn** (điều độ + Qc) và **đơn giá** (văn bản).

### 2b. Thuỷ văn — CYCLICAL, đang vào đáy (chi tiết: file thuỷ điện)
- Thuỷ điện 10T/2026: 73,39 tỷ kWh = **24,7%** (10T/2025 ~32,6%) ⇒ ~−16% YoY [DK + UĐ tự tính, file thuỷ điện]. Dòng về hồ ~80% TBNN; cả
  năm 2026 thấp hơn 2025 ~18,5 tỷ kWh; hồ tích tối đa tới 31/12/2026 và **giữ tới 31/3/2027** (lần đầu kéo dài như vậy) [DK, BCT 07/11/2026].
- **El Niño:** xác suất rất mạnh 60-65%, cực đại T11/2026-T1/2027; kịch bản (2) kéo dài tới ~T6/2027 [DK, KTTV T9-T11/2026].
- ⇒ [UĐ] Mùa khô 2027 = **đỉnh nhu cầu nhiệt điện** (than trước, khí sau). Phía Nam (Tây Nguyên/Nam Trung Bộ chịu El Niño mạnh nhất) là
  nơi khí/LNG đóng vai trò nguồn bù chính. **Đảo chiều chu kỳ cần theo dõi:** El Niño tắt giữa 2027 ⇒ thuỷ điện hồi mùa lũ 2027 ⇒ nhiệt
  điện H2/2027 giảm YoY (file than F4 P0,40).

### 2c. Cơ cấu nguồn 10T/2026 [DK, EVN 03/11/2026]
Than 147,78 tỷ kWh (**49,7%**), thuỷ 73,39 (24,7%), **tua-bin khí 23,28 (7,8%)**, tái tạo 40,72 (13,7%; mặt trời 24,04, gió 15,37), nhập khẩu
11,77 (4%). Khí chỉ 7,8% dù cầu +9,8% và LNG đã vào ⇒ khí là nguồn **bị điều độ theo giá**, không phải nguồn nền (file khí).

### 2d. Nguồn mới cạnh tranh trong điều độ
- Đã vào/sắp vào 12T: Quảng Trạch I (than 1.403 MW, COD 2026); **cụm LNG đầu tiên ~1.624 MW (Đồng Nai) COD 05/01/2026, tham gia thị trường
  điện từ 01/01/2026, Qc 65% trong 10 năm** [DK, nhiều báo T1/2026]; BESS; mái nhà.
- 2027-2028: Long Phú I, An Khánh-Bắc Giang (than, mốc 2027); **Ô Môn I chuyển khí Lô B — first gas Q3/2027 (~T8/2027)** [DK, TCCT/SGGP
  2026, PVN đặt mục tiêu]; LNG Hiệp Phước (COD Q4/2028, dự án LNG duy nhất "đúng tiến độ"); LNG Quảng Trạch II khởi công 20/10/2026, COD ~2030.
- **18 dự án điện LNG (>20 GW): 16/18 có NĐT, chỉ 2-3 khởi công**; BCT đề xuất **dời một phần LNG sang 2031-2035 và bổ sung ~5.300 MW than**
  tới 2030 [DK, Bloomberg 07/10, VNS 07/11/2026]. ⇒ [UĐ] Tầm 12-24T, cầu tăng (~35 tỷ kWh/năm) **lớn hơn** nguồn mới ⇒ không nguồn hiện hữu nào
  bị đẩy khỏi điều độ vì thừa công suất. Cạnh tranh nội bộ là **về giá biến đổi**: than > khí nội > LNG.

### 2e. Cung khí cho điện — "thừa khí mà thiếu khí"
- PV GAS: khả năng cấp khí cho điện 2026 ~**6,4 tỷ Sm³ (3,3 nội địa + 3,1 LNG)**; tiêu thụ khí nội địa cho điện ước **~2,9 tỷ Sm³** (< khả năng);
  LNG cho điện theo KH BCT ~**0,9 tỷ Sm³**; kho Thị Vải (1 tr t/năm) chạy **<40%**; 2027 cung khí cho điện **vượt** nhu cầu điều độ; khí nội địa
  những năm gần đây chỉ tiêu thụ hơn 80% khả năng khai thác [DK, Báo Đầu Tư 28/08/2026].
- Cơ chế gây "thiếu": mặt trời ưu tiên ban ngày ⇒ khí chạy thấp, tối phải tăng nhanh mà cơ chế cấp khí không linh hoạt; cước ống một số tuyến
  **tạm tính** do chưa rõ thẩm quyền duyệt giá [DK, cùng nguồn]. Đề xuất: cấp linh hoạt/pha trộn khí nội + LNG, ưu tiên khí nội [DK].
- Mỏ: Nam Côn Sơn/Cửu Long suy giảm tự nhiên; mỏ mới (Sư Tử Trắng 2B, Thiên Nga–Hải Âu, Hải Thạch–Mộc Tinh…) ~13% cung Đông Nam Bộ 2026-27,
  ~30% từ 2028 [DK cấp 2, báo cáo môi giới — không mở]. Cá Voi Xanh: không có FID, không cập nhật 2026 (file khí).
- ⇒ [UĐ] **Ràng buộc không phải lượng khí mà là giá khí so với giá điện được phép.** Hạn mức khí là biến ADMIN (điều độ + phân bổ khí nội cho
  điện vs đạm vs công nghiệp), không phải biến địa chất trong 12T.

### 2f. Hormuz / LNG toàn cầu — CYCLICAL ngoại sinh, không theo lịch VN
- Qatar: Ras Laffan mất ~17% công suất (2 train, ~12,8 mtpa) từ T3; **bất khả kháng giao LNG châu Á/châu Âu gia hạn tới hết T11**; lượt bốc hàng
  tăng dần (10 ngày tới ~10/11) nhưng vẫn dưới mức trước chiến sự; vụ tấn công tàu cuối T10 không làm giảm lượt qua eo [DK, Bloomberg qua
  gCaptain/Oilprice T10-T11/2026]. JKM proxy −12% phiên 16/11 [DK, BQ].
- ⇒ [UĐ] VN mua LNG chủ yếu tender giao ngay (file khí) ⇒ chi phí LNG cho điện 2026-27 nhạy với JKM gấp ~2 lần người có hợp đồng gắn dầu.
  Kịch bản đỡ: thoả thuận Hormuz + công suất Qatar/Mỹ mới 2027-28 ⇒ nền giá LNG thấp hơn tầm 24-36T.

## 3. Cấu trúc cạnh tranh & cơ chế giá
### 3a. Người mua duy nhất + thị trường
- **EVN/EPTC là người mua duy nhất** (bán buôn) [NỀN]. Thị trường bán buôn cạnh tranh theo **TT 29/2026/TT-BCT** (~20/07/2026): nhà máy
  tham gia trực tiếp nhận `Qc×Pc + (Qm−Qc)×FMP` (+CAN), FMP = SMP + CAN; tỷ lệ Qc trong khung 60-100% [DK cấp 2, file thuỷ điện/than].
  Trần SMP 2026 **1.725 đ/kWh**; CAN 2026 **130 hoặc 160 đ/kWh (2 nguồn lệch)**; FMP Q1/2026 **1.255 đ/kWh**; 8T ~1.430 (+37%, DK cấp 2);
  **T9-T11: không có số**. FMP 2025 có lúc chỉ ~700-800 đ/kWh [DK cấp 2, VCBS 01/2026].
- **Hệ quả theo loại nguồn [UĐ]:**
  - **Than:** biến đổi (~1.234) < FMP ⇒ phần Qm>Qc **có lãi** ⇒ năm khô thuận.
  - **Khí nội địa:** biến đổi ~1.750-1.800 ≈ trần SMP ⇒ phần vượt Qc gần **hoà/lỗ biên**. Doanh thu do Pc×Qc + (nếu có) khoản thanh toán
    **"phát tăng do ràng buộc hệ thống"** theo giá chào [NỀN — PHẢI KIỂM quy định hiện hành].
  - **LNG:** biến đổi ~3.100-5.550 ≫ trần SMP ⇒ **Qm<Qc lại có lợi về mặt CfD** (mua lại phần thiếu ở FMP rẻ hơn nhiên liệu), **NHƯNG** chỉ
    khi hợp đồng LNG **không** take-or-pay cứng. Nếu LNG take-or-pay mà điện không được huy động ⇒ lỗ kép. Mismatch Qc(điện) ↔ ToP(LNG) là
    rủi ro số 1 của LNG-điện [UĐ + NỀN].
  - **Thuỷ:** năm khô Qm<Qc khi FMP cao ⇒ bất đối xứng xấu (file thuỷ điện).
- **Tái tạo:** tranh chấp FIT — từ đầu 2025 EPTC giữ lại một phần thanh toán/áp giá tạm thấp hơn FIT; EVN đề xuất (T4/2026) trả đủ FIT chỉ từ
  ngày có văn bản nghiệm thu (CCA), trước đó trả "giá chuyển tiếp" (một nguồn nêu 1.184,9 đ/kWh), nhà đầu tư phản đối, có ý kiến dọa từ chối bán
  điện (VCCI 10/07/2026); **chưa thấy quyết định cuối** [DK, Reccessary/SolarQuarter T4, VCCI T7/2026]. Cộng rủi ro cắt giảm công suất (đã có ca
  dừng huy động ~40% công suất một dự án lớn — DK cấp 2, không rõ năm). ⇒ ADMIN thuần.

### 3b. PPA, khung giá, chuyển ngang nhiên liệu
- **Khung giá CCGT khí thiên nhiên 2026: 0-3.410,64 đ/kWh** (QĐ 1882/QĐ-BCT, 23/07/2026), **+11,1%** so 2025 (3.069,38, QĐ 983/QĐ-BCT
  10/04/2025). Thông số: nhà máy chuẩn 1.008 MW, suất hao 6.542,96 BTU/kWh ở 85% tải, **giá khí 11,98 + cước 1,87 USD/MMBtu, tỷ giá 26.378**
  [DK, VNS/Tuổi Trẻ 28/07/2026]. Tự tính [UĐ]: nhiên liệu ≈ 13,85 × 6,543 × 26.378/1000 ≈ **2.390 đ/kWh (~70% trần)**; phần cố định + biên ~1.020.
  Tỷ giá giả định 26.378 cao hơn thực tế 25.712 (−2,5%) ⇒ nếu PPA quy đổi theo tỷ giá thực thì đơn giá VND thấp hơn khung một chút.
  Khung riêng CCGT **LNG** (QĐ 1313/QĐ-BCT 13/05/2025): **trần không đọc được**.
- **NĐ 100/2025** (sửa NĐ 56/2025, hiệu lực 08/05/2025): **chuyển ngang giá nhiên liệu vào giá điện + Qc dài hạn tối thiểu 65% trong 10 năm**
  cho điện khí LNG. **Dự thảo BCT: Qc ≥75% trong ≤15 năm** cho dự án mới — tới T7/2026 vẫn là đề xuất; nhà đầu tư đòi 85-95%; EVN phản đối vì
  65% đã là gánh nặng [DK, TCCT/Báo Đấu thầu/The Investor 2025-T7/2026]. **Không thấy văn bản ban hành tới as-of.**
- **PPA nhà máy khí/than cũ [NỀN]:** 2 thành phần (cố định = khấu hao + lãi + O&M cố định + ROE; biến đổi = suất hao × giá nhiên liệu). Bước
  giảm giá cố định khi hết khấu hao/trả nợ; BOT chuyển giao khi hết hạn; nhà máy hết PPA phải đàm phán lại theo TT 12/2025/TT-BCT, thời gian thẩm
  định có thể kéo dài nhiều tháng (ca thuỷ điện nhỏ bị giá tạm ~1/4, file thuỷ điện).
- **Khí nội địa gắn dầu [NỀN + DK file khí]:** giá khí cho điện ~% MFO có sàn ⇒ Brent/FO cao ⇒ giá khí cao ⇒ (i) giá điện khí cao (pass-through)
  ⇒ (ii) bị xếp sau than ⇒ Qm thấp. FO TQ **chưa giảm** theo Brent (T11 vẫn tăng) ⇒ giá khí Q4/2026-Q1/2027 chưa hạ.
- **Chênh lệch tỷ giá:** cơ chế cho phép thu hồi chênh lệch tỷ giá khoản vay ngoại tệ, EVN trả **trễ nhiều năm** theo văn bản chấp thuận; EVN còn
  **~17.500 tỷ chênh lệch tỷ giá chưa phân bổ** tới hết 2025 [DK, Tuổi Trẻ 11/06/2026; file than]. ⇒ dòng thu ADMIN, lumpy.

### 3c. Sức khoẻ người mua + giá bán lẻ
- EVN 2025: LNST hợp nhất ~51.881 tỷ, hết lỗ luỹ kế hợp nhất (mẹ còn ~5,6 nghìn tỷ), tiền gửi ~152 nghìn tỷ, phải trả IPP + nhiên liệu >118 nghìn tỷ
  [DK, file thuỷ điện]. Lãi 2025 nhờ thuỷ điện rẻ + CGM 2025 giảm mạnh + giá bán lẻ tăng ~17% giai đoạn 2023-25 [DK, nhadautu/VietnamNet 2026].
- 2026 ngược lại: thuỷ −18,5 tỷ kWh, than +~19%, khí/LNG đắt, mà **giá bán lẻ bình quân giảm 2% còn 2.159,9037 đ/kWh từ 01/11/2026**
  (QĐ 1305/QĐ-EVN) [DK, Thời báo TC/Báo Đấu thầu T10/2026]; NĐ 278/2026 siết thủ tục tăng giá (file khí). **KQKD 9T/2026 EVN: không có số.**
- ⇒ [UĐ] Biên EVN bị ép 2026-27 ⇒ rủi ro **kéo dài kỳ thu tiền / chậm giải ngân tỷ giá** tăng từ thấp lên **thấp-vừa**; rủi ro **không thanh toán**
  vẫn thấp (đệm tiền mặt). Đây cũng là lý do EVN **chống Qc cao** cho LNG: mỗi kWh LNG bao tiêu đắt gấp 2-3 FMP.

### 3d. Luật/quy hoạch đang mở (văn bản quyết giá trị 36T)
- **Luật Điện lực sửa đổi**: trình kỳ họp 2 QH khoá XVI (20/10/2026), thảo luận T10-đầu T11; có đề xuất giao đơn vị độc lập xây khung giá điện,
  bên mua phải ký với nhà thầu trúng thầu không đàm phán lại [DK, VCCI/lsvn/Đại biểu Nhân dân 03/11/2026]; **chưa thấy biểu quyết tới as-of**.
- **PDP8 điều chỉnh (QĐ 768/QĐ-TTg 15/04/2025)**: LNG 22.524 MW tới 2030 (bản chính thức theo MOIT; dự thảo từng có số khác — cần đối chiếu
  văn bản gốc), khí nội 10.861-14.930 MW; BCT đang soạn **đề xuất điều chỉnh tiếp** (dời LNG sang 2031-35, thêm than) [DK, file tư vấn điện].
- **Carbon:** ETS thí điểm 2025-26 phân bổ miễn phí 100% (34 nhiệt điện), tuân thủ bắt buộc mở rộng từ 2028 (file than) ⇒ chi phí mới với PPA cũ
  chưa có điều khoản pass-through [NỀN — PHẢI KIỂM]. Khí phát thải ~½ than/kWh ⇒ **tương đối có lợi** cho khí khi ETS siết [UĐ].

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1 — nguyên nhân gốc của bối cảnh hiện tại:** bối cảnh 2026 (than + khí chạy cao, thuỷ điện thấp, nhiên liệu đắt, giá bán lẻ bị kìm) là
**thời tiết ngoại sinh** (La Niña 2025 → El Niño 2026-27) + **cú sốc cung năng lượng ngoại sinh** (Hormuz từ T3/2026) trên **nền cầu cấu trúc**
~10%/năm và **thiếu nguồn nền mới** (PDP8 trượt). **Không** phải mất cân đối vĩ mô trong nước gây ra; lạm phát nội 5,09% là **lực cản chính trị**
lên đơn giá chứ không phải nguồn cầu.
**Trục 2 — tự giới hạn?** Thuỷ văn: có, theo lịch tự nhiên (đáy mùa khô 2027). Hormuz/LNG: **ngoại sinh, không theo lịch VN**. Thiếu nguồn: **không**
tự hết trong 24-36T. Phần ADMIN (Qc, khung giá, PPA, giá bán lẻ, FIT, Luật Điện lực) nằm **trong tay VN** nhưng lịch sử chậm, và chiều chính sách
**đang tách đôi**: nới cơ chế đầu tư (Qc, luật, PDP8) trong khi kìm đơn giá bán lẻ.

### 4a. Theo phân khúc — driver CHÍNH của lợi nhuận 12T (tổng = 1 mỗi dòng)
| Phân khúc | ADMIN_GATED | CYCLICAL | STRUCTURAL | Lý do ngắn |
|---|---|---|---|---|
| Khí nội địa (CCGT cũ) | **0,45** | 0,35 | 0,20 | Qm do điều độ + Qc; giá khí gắn dầu (cyclical) nhưng pass-through; mỏ suy giảm → pha LNG (structural) |
| LNG mới | **0,65** | 0,25 | 0,10 | Sống nhờ Qc 65%/NĐ 100 + sửa PPA + khớp ToP LNG; JKM/Hormuz là cyclical thứ cấp |
| Than | 0,45 | 0,40 | 0,15 | = file than (khoá 17/11) |
| Thuỷ | 0,35 | **0,55** | 0,10 | = file thuỷ điện (khoá 12/11) |
| Tái tạo (mặt trời/gió) | **0,60** | 0,20 | 0,20 | FIT/CCA, giá chuyển tiếp, cắt giảm; bức xạ/gió là phụ |

### 4b. Tổng hợp cho genco đa nguồn (khí + LNG + than + thuỷ, tái tạo nhỏ)
| Tầm | ADMIN_GATED | CYCLICAL | STRUCTURAL | Diễn giải |
|---|---|---|---|---|
| **12 tháng** | **0,45** | 0,40 | 0,15 | Sản lượng nhiệt điện gần chắc cao tới mùa khô 2027 (cyclical El Niño + thiếu nguồn), nhưng **biên** do văn bản: Qc từng loại hình 2027, chuyển ngang giá khí/LNG, sửa PPA LNG, thanh toán chênh lệch tỷ giá, kỳ thu tiền EVN, giá bán lẻ bị kìm. Thuỷ điện trong danh mục kéo ngược chiều nhiệt điện (đệm tự nhiên) |
| **36 tháng** | **0,45** | 0,20 | 0,35 | Giá trị do: Qc 75%/15 năm, PDP8 sửa lần nữa (LNG dời/than thêm), Luật Điện lực + thị trường bán buôn/bán lẻ, gia hạn PPA/BOT, ETS 2028. Structural: thiếu nguồn ~14 GW 2030 (đỡ khối lượng) + suy giảm khí nội → LNG pass-through biên mỏng (ép biên) + chuyển dịch carbon — hai lực ngược chiều |

**Độ tin cậy: AMBIGUOUS ~60/40.** 12T ADMIN và CYCLICAL sát nhau; phần quyết định nằm ở biến **không có số** (Qc 2027 từng loại hình, FMP T9-T11,
điều khoản ToP LNG, tiến độ sửa PPA LNG).
**Pha [UĐ]:** khối lượng nhiệt điện ở **đỉnh chu kỳ** (Q4/2026 → mùa khô 2027); giá nhiên liệu **vừa qua đỉnh** (Brent T10, JKM mới gãy 16/11, FO TQ
chưa gãy); FMP **giữa→muộn nhịp tăng**; chính sách đơn giá **đang siết** (bán lẻ −2%), chính sách đầu tư **đang nới** (dự thảo Qc, luật, PDP8).

**Falsifiers (đổi nhãn):** (i) KH vận hành 2027 giao Qc khí/LNG thấp hoặc huy động khí 2027 < 2026 ⇒ CYCLICAL 12T giảm, ADMIN tăng; (ii) ban hành
Qc ≥75% áp cho **cả** dự án đã vận hành ⇒ ADMIN 36T giảm (rủi ro được khoá), STRUCTURAL tăng; (iii) Hormuz thoả thuận + JKM <15 trước Q2/2027 ⇒
CYCLICAL chuyển sang hướng thuận cho LNG; (iv) EVN báo lỗ 2026 + dừng giải ngân chênh lệch tỷ giá ⇒ ADMIN 12T ≥0,55.

## 5. FORECAST khoá trước (2026-11-18)
Bobby không tự chấm. Mike/người chấm đọc nguồn chính thức (EVN, NSMO, BCT, Chính phủ) tại ngày chấm; nguồn không công bố trước ngày chấm ⇒
"không chấm được". **Đã khoá ở file chị em (chỉ dẫn chiếu, KHÔNG khoá lại):** FMP 2026 ≥1.475 P0,65 (thuỷ F3); giá bán lẻ tăng ≥1 lần 12/11/2026→
30/06/2027 P0,40 (thuỷ F7); EVN LNST hợp nhất 2026 >0 P0,55 (than F8); Luật Điện lực sửa đổi thông qua kỳ họp 2 P0,70 (than F9); KH vận hành 2027
trước 15/01/2027 P0,70 (than F13); văn bản Qc khí/LNG ≥70% ban hành trước 31/03/2027 P0,40 (khí E1); Lô B first gas trước 30/09/2027 P0,45 (khí E4);
JKM T1/T3/2027 (khí F5/F6).

| # | Mệnh đề (kiểm chứng được) | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| **G1** | Tổng sản lượng điện sản xuất + nhập khẩu toàn hệ thống **cả năm 2026 ≥ 354 tỷ kWh** (≈ +9,6%; 10T 297,4, T11 dự báo 28,9) | **0,70** | 2027-01-31 | EVN/NSMO tổng kết năm |
| **G2** | Tỷ trọng **tua-bin khí** (gồm LNG) trong sản lượng hệ thống **cả năm 2026 ≥ 7,6%** (10T: 7,8%) | **0,70** | 2027-01-31 | EVN/NSMO cơ cấu nguồn cả năm |
| **G3** | BCT ban hành khung giá phát điện **CCGT khí thiên nhiên năm 2027** với trần **> 3.410,64 đ/kWh** (QĐ 1882/2026) | **0,65** | 2027-09-30 | moit.gov.vn / báo dẫn QĐ |
| **G4** | Có **≥1 PPA dự án điện LNG mới** (ngoài cụm LNG đã COD 01/2026) được **ký chính thức** với EVN/EPTC | **0,40** | 2027-06-30 | EVN/BCT/chủ đầu tư qua báo |

Lập luận [UĐ]:
- **G1:** T11-T12/2025 ≈ 52 tỷ kWh (suy từ 10T và cả năm 2025, tự tính). G1 cần T11-T12/2026 ≥ ~56,6 tỷ kWh, tức +~9%. T10 +14,3% và T11 dự
  báo +14,4% ⇒ dư địa rộng. Rủi ro: lũ/thời tiết mát T12, ước tính T11 bị hạ.
- **G2:** Q4 BCT chỉ đạo tăng nhiệt điện để dành nước ⇒ khí miền Nam giữ hoặc tăng. Lực ngược: lũ miền Trung T11 nâng thuỷ điện; khí đắt nên NSMO
  ưu tiên than.
- **G3:** khung 2025→2026 +11% khi giả định khí 11,98 USD. Brent bình quân T1-T11/2026 (~91, BQ) cao hơn 2025 (~68, NỀN) ⇒ giả định khí 2027 nhiều khả năng cao
  hơn. Lực ngược: tỷ giá giả định hạ (VND lên giá) và Brent đã qua đỉnh. Nếu tới 30/09/2027 khung 2027 chưa ban hành ⇒ "không chấm được".
- **G4:** cơ chế Qc 75% chưa ban hành, EVN phản đối Qc cao, BCT đề xuất dời LNG sang 2031-35 ⇒ dưới 0,5. Đỡ: thiếu điện thật, Hiệp Phước "đúng tiến
  độ", Luật Điện lực sửa đổi có thể tháo nút đàm phán.

**⚠ Mâu thuẫn đã khoá giữa các file chị em (báo Mike, KHÔNG sửa):** "giá bán lẻ tăng ≥1 lần tới 30/06/2027" có **P0,55** (tư vấn điện F8, khoá 28/10,
trước khi EVN giảm 2%) và **P0,40** (thuỷ điện F7, khoá 12/11); "Luật Điện lực thông qua" có **P0,80** (tư vấn F9) và **P0,70** (than F9). Đọc hiện tại
của Bobby đứng với số **khoá sau** (0,40 / 0,70) vì có thông tin mới (giảm giá 01/11, NĐ 278, chưa biểu quyết tới 18/11). Khi chấm, chấm cả hai như hai
lần khoá độc lập.

## 6. DD cần kiểm gì — genco đa nguồn niêm yết (kiểm bằng số, theo từng nhà máy)
1. **Danh mục theo nhà máy:** loại nhiên liệu, MW, năm COD từng tổ, sở hữu (%), hình thức (BOT/IPP/thuộc tổng công ty), PPA còn bao nhiêu năm,
   tham gia thị trường trực tiếp/gián tiếp. Tỷ trọng doanh thu/lợi nhuận theo nhiên liệu ⇒ áp đúng nhãn §4a cho từng mảng, không áp một nhãn chung.
2. **Qc từng nhà máy:** Qc năm 2025-2026 và **Qc 2027 dự kiến** (KH vận hành 2027), Qm thực theo tháng, tỷ lệ Qm/Qc; doanh thu tách **Pc×Qc /
   FMP / CAN / khoản thanh toán phát tăng do ràng buộc**; tranh chấp quyết toán thị trường.
3. **LNG (mảng rủi ro cao nhất):** (a) PPA đã ký bản cuối chưa, phụ lục sửa đổi, Qc 65%/10 năm áp dụng thế nào (năm, tháng, có tính sản lượng
   bị cắt vì lý do hệ thống không); (b) **hợp đồng mua LNG: take-or-pay, công thức giá (JKM/Brent/Henry Hub), tỷ trọng giao ngay**; (c) **khớp
   Qc điện ↔ ToP LNG** — sản lượng tối thiểu điện có phủ ToP khí không; (d) chuyển ngang giá nhiên liệu theo NĐ 100 có độ trễ bao lâu, trần khung
   giá có chặn không; (e) phí tái hoá/kho, cước ống; (f) nợ vay dự án: đồng tiền, lãi thả nổi, lịch trả gốc, DSCR ở kịch bản Qm = Qc; (g) **luật user:
   dự án mới định giá base = sổ sách/NPV 0**, lệch chỉ khi có cơ sở độc lập (skill dd-investor-report luật 20).
4. **Khí nội địa:** hợp đồng mua khí (mỏ, % MFO, sàn, cước), lịch suy giảm cung khí theo mỏ, **thứ tự ưu tiên phân bổ khí** (điện vs đạm vs công
   nghiệp) khi thiếu, việc pha LNG vào khí nội (giá bình quân gia quyền đổi ra sao), khí bị cắt do điều độ (Qm < khả năng).
5. **Than & thuỷ trong danh mục:** dùng checklist ở `sector_read_nhiet_dien_than_20261117.md` §6 và `sector_read_thuy_dien_20261112.md` §6
   (pha trộn than nhập, suất hao, mực nước hồ cuối T12/2026, CfD năm khô).
6. **Tỷ giá:** dư nợ theo đồng tiền; **phải thu chênh lệch tỷ giá từ EVN** (số dư, năm phát sinh, văn bản chấp thuận, đã ghi doanh thu chưa); độ
   nhạy ±1% USD/VND. VND hiện lên giá (−2,5% 12T) — đừng ngoại suy thành xu hướng.
7. **Người mua:** kỳ thu tiền EVN theo quý 2024→2026, nợ quá hạn, lãi chậm trả; khoản tái tạo bị giữ lại (FIT/CCA) nếu có mảng tái tạo.
8. **Giá cố định & đồng hồ PPA:** năm hết khấu hao/trả nợ từng nhà máy, bước giảm giá cố định, PPA/BOT hết hạn trong 36T và trạng thái đàm phán
   (giá tạm?); tách "lãi kế toán tăng vì hết khấu hao" khỏi "đơn giá giảm vì hết trả nợ".
9. **Khả dụng & bảo dưỡng:** hệ số khả dụng, giờ sự cố, lịch đại tu mùa khô 2027 (BCT muốn đại tu T1-T4); tuổi tua-bin, LTSA.
10. **Capex & đầu tư mới:** cam kết vốn chủ cho dự án LNG/khí mới (Lô B hạ nguồn nếu có), nguồn vốn, ảnh hưởng cổ tức; dự án có PPA hay chưa (G4).
11. **Carbon & môi trường:** hạn ngạch 2026 vs phát thải; ai chịu chi phí từ 2028; tro xỉ (nếu có than).
12. **Cổ đông nhà nước:** tỷ lệ chi phối, chính sách cổ tức, kế hoạch thoái vốn/tái cơ cấu; giao dịch với công ty mẹ (mua khí/LNG từ bên liên quan
    ⇒ kiểm giá chuyển nhượng).
13. **Độ nhạy bắt buộc ghi số:** ±10% Qm nhiệt điện; ±5pp Qc khí/LNG; ±100 đ/kWh FMP; ±2 USD/MMBtu giá khí/LNG khi **có/không** pass-through đầy
    đủ; ±1% USD/VND; trễ thanh toán EVN +30 ngày.

Định giá (nếu dùng): theo chỉ đạo user, r neo lãi huy động 12T (effective **7,4%** hôm nay, CCTG 12M) + chiết khấu thanh khoản; **năm El Niño
2026-27 KHÔNG được ngoại suy làm năm chuẩn** cho nhiệt điện (đỉnh chu kỳ) cũng như thuỷ điện (đáy chu kỳ); dòng tiền mảng LNG tách theo kịch bản
Qc 65% hiện hành vs Qc 75% (chưa ban hành).

## 7. Tự kiểm & giới hạn
- **Tốt hơn tôi nghĩ:** cầu điện tăng tốc (+14% T10-T11) và thiếu nguồn được chính phủ công bố ⇒ khối lượng hệ thống không phải rủi ro; giá
  LNG/Brent đã có dấu hiệu qua đỉnh; khung giá khí 2026 +11% cho thấy BCT vẫn cập nhật đầu vào nhiên liệu.
- **Xấu hơn / chưa biết:** LNG đứng ngoài thị trường về kinh tế (2-3× trần SMP) ⇒ toàn bộ giá trị LNG phụ thuộc Qc + ToP, cả hai đang trong đàm phán;
  không có FMP T9-T11, Qc 2027, khung giá CCGT LNG, KQKD 9T EVN; G2 thiếu số 2025 để so YoY; merit order là **tự tính** từ thông số khung giá và một
  ước giá khí cấp 2.
- **Blind:** xem §0 — danh tính có thể đã bị nhận ra qua tên thư mục và prompt; mọi số trong file là cấp ngành/hệ thống/văn bản, không có số DN.
- Snapshot vĩ mô UNVERIFIED (TradingEconomics), không vintage.

## Nguồn (một số URL có tên DN/tổ chức trong đường dẫn — người đọc blind sau có thể bỏ qua)
- BQ `tav2_bq.commodity_prices` (TE `brent`, `coal`, `liquefied_natural_gas_japan_korea`, sunsirs `fuel_oil`, WB `lng_japan`), truy vấn 2026-11-18;
  `deposit_rate_vn` / `cctg_rate_vn` PIT 2026-11-18 (effective 7,4% = CCTG 12M 02/11; Big-4 6,8%; kill-switch A CLEAR).
- Snapshot: `agents/Taylor/research/dd_POW_20261118/macro_snapshot_20261118.md` (as-of 2026-11-18).
- Báo Đầu Tư, "Nghịch lý thừa khí, thiếu khí cho phát điện" — 28/08/2026: https://baodautu.vn/nghich-ly-thua-khi-thieu-khi-cho-phat-dien-d686850.html
- Việt Nam News, "2026 price cap set for gas-fired power generation at 13 cents/kWh" (QĐ 1882/QĐ-BCT 23/07/2026) — 28/07/2026: https://vietnamnews.vn/economy/1796349/2026-price-cap-set-for-gas-fired-power-generation-at-13-cents-kwh.html ; VietnamPlus: https://www.vietnamplus.vn/bo-cong-thuong-phe-duyet-gia-phat-dien-nhiet-dien-khi-nam-2026-toi-da-hon-3410-dong-post1126776.amp
- Khung giá khí 2025 (QĐ 983/QĐ-BCT 10/04/2025, 3.069,38 đ/kWh): https://tapchicongthuong.vn/bo-cong-thuong-ban-hanh-khung-gia-phat-dien-cho-nha-may-dien-khi-nam-2025-139267.htm ; QĐ 1313/QĐ-BCT (LNG): https://luatvietnam.vn/dien-luc/quyet-dinh-1313-qd-bct-2025-phe-duyet-khung-gia-phat-dien-nha-may-tua-bin-khi-chu-trinh-hon-hop-400668-d1.html
- Dự thảo Qc 75%/15 năm: https://tapchicongthuong.vn/bo-cong-thuong-de-xuat-nang-san-luong-dien-hop-dong-toi-thieu-dai-han-cho-dien-khi-len-75-407594.htm ; https://baodauthau.vn/de-xuat-bao-tieu-dien-khi-lng-len-75-trong-15-nam-tang-suc-hap-dan-cho-du-an-lng-post193147.html ; https://theinvestor.vn/vietnams-industry-ministry-proposes-75-offtake-for-lng-power-projects-d17305.html
- Sản lượng 10T/2026, dự báo T11: VietnamPlus/Nhân Dân (qua file thuỷ điện, 03/11/2026); EVN 9T: https://lsvn.vn/evnnpc-don-nhan-co-thi-dua-cua-chinh-phu-hoan-thanh-xuat-sac-nhiem-vu-9-thang-nam-2026-a180379.html
- KH vận hành 2026 (QĐ 3477/QĐ-BCT 28/11/2025): https://tapchicongthuong.vn/bo-cong-thuong-ban-hanh-ke-hoach-cung-cap-dien-va-van-hanh-he-thong-dien-nam-2026-332023.htm ; BCT 8 nhóm giải pháp 2027-28 (07/11/2026): https://www.vietnamplus.vn/bo-cong-thuong-dua-ra-8-nhom-giai-phap-bao-dam-cung-ung-dien-nam-2027-2028-post1146854.vnp
- Giá bán lẻ −2% từ 01/11/2026: https://thoibaotaichinhvietnam.vn/dieu-chinh-gia-ban-le-dien-binh-quan-tu-ngay-1-11-2026-206228.html ; https://baodauthau.vn/dieu-chinh-gia-ban-le-dien-binh-quan-tu-ngay-111-post211500.html
- FMP Q1/2026 1.255 đ/kWh: https://vneconomy.vn/ap-luc-chi-phi-mua-dien-dau-vao-tang-tu-quy-22026.htm
- Lô B first gas Q3/2027: https://tapchicongthuong.vn/don-dong-khi-lo-b-dau-tien-vao-du-an-nhiet-dien-o-mon-i-trong-quy-iii-2027-391428.htm ; https://www.sggp.org.vn/chuoi-du-an-khi-lo-b-du-kien-co-dong-khi-dau-tien-vao-thang-8-2027-post831467.html
- Cụm LNG đầu tiên COD/tham gia thị trường 01/2026 (chỉ dùng mốc + Qc 65%): https://www.enerdata.net/publications/daily-energy-news/vietnams-first-lng-power-complex-goes-online-16-gw.html ; https://news.laodong.vn/kinh-doanh/can-som-thao-go-diem-nghen-cho-dien-khi-lng-1705540.ldo
- Hormuz/Qatar: https://gcaptain.com/qatar-lng-loadings-pick-up-to-around-half-of-pre-war-levels/ ; https://oilprice.com/Latest-Energy-News/World-News/Qatar-Extends-LNG-Force-Majeure-as-Hormuz-Crisis-Drags-On.html
- FIT tái tạo: https://www.reccessary.com/en/news/evn-proposes-deep-fit-cuts-13-billion-renewable-dispute ; https://solarquarter.com/2026/04/17/vietnams-evn-proposes-retroactive-tariff-cuts-for-renewable-projects-amid-13-billion-dispute/ ; https://www.vcci.com.vn/tin-tuc/phan-doi-gia-tam-tinh-cua-evn-dn-nang-luong-tai-tao-co-the-tu-choi-ban-dien
- Luật Điện lực sửa đổi (kỳ họp 2 khoá XVI): https://vcci.com.vn/tin-tuc/ky-hop-thu-hai-quoc-hoi-khoa-xvi-se-xem-xet-luat-dien-luc-sua-doi ; https://daibieunhandan.vn/hai-hoa-loi-ich-giua-nha-nuoc-doanh-nghiep-va-nguoi-su-dung-dien-10441725.html ; https://lsvn.vn/de-xuat-giao-don-vi-doc-lap-xay-dung-khung-gia-dien-a182041.html
- PDP8 điều chỉnh QĐ 768/QĐ-TTg: https://moit.gov.vn/tin-tuc/phat-trien-nang-luong/chinh-thuc-phe-duyet-quy-hoach-dien-viii-dieu-chinh.html
- EVN 2025 (lãi, giá bán lẻ +17% 2023-25): https://nhadautu.vn/tu-lo-gan-39000-ty-dong-den-lai-52000-ty-dieu-gi-giup-evn-dao-chieu-d105503.html
