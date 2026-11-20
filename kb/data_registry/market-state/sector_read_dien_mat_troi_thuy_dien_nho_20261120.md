---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-20. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp cụ thể (xem §0 về rò rỉ).
blind: YES
as_of: 2026-11-20 (snapshot vĩ mô /tmp/bobby_in/macro_snapshot_20261120.md có áp độ trễ công bố; lãi suất PIT `effective_deposit_rate('2026-11-20')`; tin web ≤ 2026-11-17)
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành nhà phát điện tái tạo + thuỷ điện nhỏ bán 100% cho EVN qua PPA. Gồm (a) điện mặt trời mặt đất/nổi 50-100 MWp tại Nam Trung Bộ (Ninh Thuận/Bình Thuận cũ, nay thuộc Khánh Hoà/Lâm Đồng), từng hưởng hoặc lỡ giá FIT, nay đối mặt khung giá chuyển tiếp/khung giá năm và cắt giảm công suất; (b) thuỷ điện vừa-nhỏ 8-50 MW miền Bắc/Tây Bắc, đòn bẩy cao, có dự án đang xây/đề xuất (kể cả thuỷ điện tích năng ở giai đoạn quy hoạch). Gồm pipeline cầu + cung/lưới, cấu trúc cạnh tranh, khung giá sau FIT, curtailment, chi phí vốn, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED kèm xác suất 12T/36T, FORECAST khoá trước, checklist DD.
---

# SECTOR READ: Điện mặt trời Nam Trung Bộ + thuỷ điện nhỏ miền Bắc/Tây Bắc, as-of 20/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán/suy luận
của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải KIỂM trước khi dùng làm số).
**File chị em (đọc, không chép lại):** `sector_read_thuy_dien_20261112.md` (El Niño 2026-27, CfD Qc/FMP, khung thuỷ điện 1.110 đ/kWh,
EVN tài chính, F1-F12) và `sector_read_phat_dien_20261118.md` (merit order, tái tạo ADMIN 0,60, Luật Điện lực, G1-G4). Xác suất ở §4-§5
cố ý **nhất quán** với 2 file đó; mệnh đề đã khoá thì chỉ dẫn chiếu, không khoá lại.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Snapshot:** đọc đúng file caller chỉ định `/tmp/bobby_in/macro_snapshot_20261120.md`. Không có thư mục DD nào được đưa, không thấy
  chuỗi giống mã chứng khoán trong prompt.
- **Repo:** 2 file chị em; lãi suất PIT `deposit_rate_vn.effective_deposit_rate('2026-11-20')` và `macro_killswitch_a_status()`. Không
  truy vấn `ticker_financial` (sẽ phải chọn DN ⇒ phá blind).
- **Tôi KHÔNG nhận ra danh tính doanh nghiệp.** Tổ hợp "mặt trời Nam Trung Bộ + thuỷ điện nhỏ miền Bắc + tích năng quy hoạch + đòn bẩy
  cao" khớp với nhiều hơn một DN niêm yết trong hiểu biết nền của tôi; tôi không cố thu hẹp.
- **Rò rỉ không chủ ý (ghi trung thực, KHÔNG dùng cho phân loại/forecast):** kết quả tìm kiếm trả về (i) tên 2 tập đoàn điện **nước ngoài**
  (Thái Lan) có tài sản tái tạo ở VN, một trong số đó báo phải thu EVN quá hạn >12 tháng (pv magazine 29/05/2026), một bên kỳ vọng "nút
  thắt cắt giảm" được gỡ trong Q3/2026; (ii) tên chủ đầu tư tư nhân của dự án tích năng thứ hai (khởi công 14/11/2026). Tôi chỉ dùng các mẩu
  này ở mức **cơ chế ngành** (EVN có giữ tiền thật; tích năng tư nhân đã có tiền lệ khởi công) và **không ghi tên** vào file.
- **Không có số (ghi "không có số", không suy):** tỷ lệ cắt giảm điện mặt trời Nam Trung Bộ đo được năm 2026 (có 1 con số 6,4% Q1/2026
  "miền Trung" ở nguồn cấp 3, không truy được gốc ⇒ KHÔNG dùng); phụ lục tỉnh→miền của QĐ 2946/QĐ-BCT (Khánh Hoà/Lâm Đồng mới thuộc
  "miền Trung" hay "miền Nam" của khung giá); phạm vi áp dụng chính xác của khung 2026 cho dự án chuyển tiếp đã/đang đàm phán; số dự án
  chuyển tiếp đã ký PPA chính thức tới 11/2026; số tiền EVN đang giữ lại của nhóm 173 dự án; mực nước hồ miền Bắc cuối mùa lũ 2026; cơ chế
  giá riêng cho thuỷ điện tích năng; tầng C và E của bảng chi phí vốn; dư nợ tín dụng ngân hàng cho tái tạo.

## 1. Snapshot vĩ mô: chỉ báo hợp với ngành này
Bảng ánh xạ ngành của snapshot **không có dòng "Điện"**; tôi tự chọn chỉ báo kéo cầu điện và chi phí vốn.

| Chỉ báo (TE, UNVERIFIED) | Giá trị | Δ3T / Δ12T | Đọc cho ngành |
|---|---|---|---|
| Sản xuất CN YoY | 15,0% (T10) | +0,5 / +4,6pp | Phụ tải công nghiệp mạnh, khớp điện T10 +14,3% [DK, EVN 03/11] |
| GDP YoY | 9,95% (Q3) | +1,14 / +1,70pp | Nền cầu điện ~10%/năm |
| PMI SX | 52,3 (T10) | −0,6 / −2,2 | Còn mở rộng, đà chậm nhẹ |
| FDI luỹ kế | 24,08 tỷ USD (T10) | +13,05% 12T | Cầu DPPA/điện xanh của KCN — kênh bán ngoài EVN (chậm) |
| CPI YoY / lõi | 5,09% (T10) / 4,45% (T9) | +1,84 / +1,15pp 12T | Lực cản chính trị lên giá bán lẻ (EVN giảm 2% từ 01/11) ⇒ EVN bị ép biên ⇒ áp lực hồi tố/giữ tiền tái tạo |
| USD/VND | 25.755 (19/11) | −1,33% / **−2,35%** | FIT gắn USD [NỀN] ⇒ doanh thu FIT quy VND giảm ~2,4%/12T; lỗ tỷ giá nợ USD giảm |
| US 10Y / DXY | 5,10% / 103,7 | +1,01pp / +3,5% 12T | DXY +4,85% 3T mà VND vẫn lên ⇒ phân kỳ, đuôi rủi ro đảo chiều tỷ giá |

### 1b. Chi phí vốn — bảng 5 tầng (ngành vay dự án dài hạn, VND thả nổi + một phần ngoại tệ [NỀN])
| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (cập nhật 16/11; đi ngang từ 03/10) | Tách online / tại quầy, và Big-4 6M: **không có số** (series lưu MAX) |
| B. Bán hành chính | CCTG 12M Big-4 cao nhất | **7,4%** (02/11) | Spread CCTG − tiết kiệm 12M = **+0,6pp**; từng NH, sự kiện mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi ẩn, số NH ≥7% | **không có số** | |
| D. Thị trường | LNH 3M | **7,04%** (17/11) | **Nhích 3 lần liên tiếp**: 6,39 (09/11) → 6,63 (13/11) → 7,04 (17/11) [DK, snapshot + 2 file chị em]. Spread LNH 3M − tái cấp vốn 2,54pp. OMO/tín phiếu, trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y (chỉ tin Δ) | 4,57 (+0,01 3T / +0,56pp 12T) | Lãi dài hạn cao hơn năm trước |
| E. Lượng | Tín dụng vs huy động YTD, LDR, văn bản nới | **không có số** | |

**Đồng thuận/phân kỳ [UĐ]:** về **HƯỚNG**, A và B đi ngang; **D phân kỳ đi lên** trong tháng 11 (+0,65pp/8 ngày) sau khi đã hạ từ đỉnh ~7,75%
3 tháng trước. Cơ chế suy luận (không có nguồn): nhu cầu thanh khoản cuối năm + tín dụng chạy nhanh hơn huy động, thường lộ ở liên NH trước
khi lộ ở số niêm yết bị neo. Về **MỨC**, chi phí biên thật (CCTG 7,4%) cao hơn niêm yết ~0,6pp. Lãi vay dự án thả nổi thường = lãi huy động
12M tham chiếu + biên ~3-4pp [NỀN] ⇒ **~10-11,5%/năm** cho DN đòn bẩy cao. Kill-switch A (>7,5%) **CLEAR** (7,4%, tuổi 4 ngày) — khoảng
cách chỉ 0,1pp. Độ tin cậy trung bình (thiếu C, E). **Đây là biến cấp 1 với DN đòn bẩy cao**: +1pp lãi vay trên nợ ≈ 60-70% tổng tài sản
[UĐ, cấu trúc điển hình] ăn trực tiếp vào lợi nhuận. Đề xuất (không phải ngưỡng): theo dõi LNH 3M >7,5% hai tuần liên tiếp như tín hiệu sớm
trước khi CCTG đổi.

## 2. Pipeline cầu + cung/lưới
### 2a. Phụ tải hệ thống — STRUCTURAL, mạnh (chi tiết: file phát điện §2a)
- 10T/2026: 297,4 tỷ kWh (+9,8%); T10 +14,3%; NSMO dự báo T11 +14,4% [DK, EVN 03/11/2026]. BCT cảnh báo thiếu 4.256 MW năm 2027 [DK, file
  phát điện].
- ⇒ [UĐ] Ở cấp **hệ thống**, mọi kWh đều có người mua. Rủi ro khối lượng của ngành này **không** đến từ cầu, mà từ (i) thuỷ văn (thuỷ điện),
  (ii) **lưới cục bộ + hình dạng phụ tải trong ngày** (mặt trời), (iii) văn bản (giá/thanh toán).

### 2b. Điện mặt trời Nam Trung Bộ — cung, lưới, curtailment
- **Sản lượng:** mặt trời 10T/2026 **24,04 tỷ kWh** (8,1% hệ thống) [DK, EVN 03/11/2026] so với 10T/2025 **20,59 tỷ kWh** [DK cấp 2, bản tin
  EVN 2025 qua tóm tắt tìm kiếm] ⇒ **~+16,8% YoY** [UĐ tự tính; gồm cả nguồn mới và mái nhà bán lên lưới — không tách được cho nhà máy cũ].
- **Công suất:** PV >19 GW cuối 2025 (số liệu chính phủ qua pv magazine 29/05/2026); PDP8 điều chỉnh (QĐ 768/QĐ-TTg, 15/04/2025) mục tiêu
  mặt trời 2030 **46-73 GW**; tỉnh mời thầu >400 MW mặt trời tập trung 5T/2026 [DK, pv magazine]. Ninh Thuận + Bình Thuận (cũ) chiếm phần lớn
  tài sản mặt trời tập trung [DK cấp 2/NỀN; nguồn thị trường nói >60%, chưa kiểm].
- **Hình dạng phụ tải (cơ chế cắt giảm chính 2026):** ví dụ ~17.000 MW mặt trời phát khi phụ tải >52.000 MW lúc 12h30-14h30; thêm mặt trời
  làm "đáy trưa" sâu hơn ⇒ dư cục bộ ⇒ phải cắt; áp lực dồn sang 17h30-22h30 [DK, Công Thương "Điện mặt trời VN kỳ 5", 2026]. Tức là cắt giảm
  đã chuyển từ **quá tải đường dây** (2019-2020) sang **quá tải đường dây + dư công suất giờ trưa** (vấn đề hệ thống, không chỉ địa phương).
- **Tiền lệ lịch sử:** 2019-2020, đa số đường dây/TBA 110-500 kV ở Ninh Thuận/Bình Thuận quá tải; nhà máy bị yêu cầu cắt 30-60% công suất
  hằng ngày, có ngày 70% [DK, EVN/Thanh Niên/VnExpress 2019-2020 — số cũ, chỉ làm biên trên lịch sử].
- **2026:** hệ số công suất mặt trời miền Trung **xấu đi** Q1/2025→Q1/2026, nhất quán với cắt giảm/ràng buộc lưới — **không có số** đo
  [DK, pv magazine 29/05/2026]. **PPA tiêu chuẩn không có điều khoản bồi thường cắt giảm** [DK, cùng nguồn]. Tin T11/2025: dư nguồn do bão và
  phụ tải thấp ⇒ NSMO cắt đều thuỷ điện, gió, tái tạo (trọng tâm miền Bắc) [DK, Tuổi Trẻ News 14/11/2025]. ⇒ năm thừa nước là năm cắt nhiều.
- **Lưới:** EVN cam kết đóng điện ~1.200 km đường dây 500 kV mới tới cuối 2027 [DK cấp 2, MOIT qua một nguồn thị trường]; PDP8 đặt đầu tư
  truyền tải ~3,6 tỷ USD/năm 2026-2030, gấp ~5 lần bình quân 0,7 tỷ USD/năm 5 năm qua [DK, pv magazine]. Tiến độ các công trình 220/500 kV
  giải toả riêng Nam Trung Bộ: **không có số** lượt này.
- **BESS:** khung giá BESS độc lập 2026 tối đa **3.209,98 đ/kWh** (QĐ 2987/QĐ-BCT ký 11/11/2026, hai thành phần, mô hình 2h, 85% hiệu suất)
  [DK, ESS News 17/11/2026]; khung mặt trời 2026 có hạng "kèm BESS ≥10% công suất, 2h" với giá trần cao hơn ~13-14% (§3b). Mục tiêu BESS 2030
  10-16,3 GW [DK, PDP8]. ⇒ [UĐ] BESS là van giảm cắt giảm có cơ chế giá rõ từ T11/2026, nhưng cần capex mới ⇒ áp lực thêm lên bảng cân đối
  đòn bẩy cao.
- **El Niño 2026-27 cho mặt trời [UĐ]:** El Niño mạnh nhất ở Nam Trung Bộ/Tây Nguyên/Nam Bộ (file thuỷ điện) ⇒ (i) bức xạ mùa khô 2027 nhiều
  khả năng **cao hơn** bình thường; (ii) thuỷ điện miền Trung/Nam **thấp** ⇒ ít cạnh tranh giờ trưa ⇒ **giảm** áp lực cắt giảm ở cấp hệ thống.
  Nhưng nghẽn đường dây cục bộ không đổi. Kết luận: năm El Niño **thuận** cho mặt trời về khối lượng; ngược với 2025 (La Niña, thừa nước).
- **Đánh giá rủi ro cắt giảm 12T [UĐ]:** **vừa**, nghiêng thấp hơn 2025 nhờ cầu +14% và El Niño; nhưng **xu hướng 36T là tăng** (46-73 GW
  mục tiêu, đáy trưa sâu dần, lưới chậm hơn nguồn như tiền lệ). Độ tin cậy thấp vì không có số đo cắt giảm 2026.

### 2c. Thuỷ điện nhỏ miền Bắc/Tây Bắc — thuỷ văn + lưới 110 kV
- **Thuỷ văn:** kế thừa file thuỷ điện §2b (El Niño xác suất rất mạnh 60-65%, cực đại T11/2026-T1/2027; tác động Bắc Bộ yếu và ít nhất quán
  hơn Nam Trung Bộ; mưa lớn diện rộng Bắc Bộ T8/2026). Nhà máy 8-50 MW miền núi phía Bắc phần lớn **đập dâng/hồ nhỏ, dòng chảy tự nhiên**
  [DK, Báo Lào Cai 17/11/2026] ⇒ sản lượng mùa khô bám sát dòng chảy cơ bản, không có hồ để "để dành" ⇒ nhạy với lượng mưa mùa khô
  T12/2026-T4/2027 hơn thuỷ điện hồ lớn. Mùa mưa miền Bắc theo biểu giá chi phí tránh được: **01/7-31/10** [DK, TT 20/2026/TT-BCT qua
  Năng lượng VN 23/04/2026].
- **Lưới 110 kV Tây Bắc (nút thắt cục bộ đã đo):** Lào Cai (sau sáp nhập) có **109 nhà máy thuỷ điện ~1.800 MW**, 63 nhà máy đấu 110 kV
  (1.482,4 MW); đường 110 kV Thác Bà 2-Đoan Hùng có lúc **94,55%** định mức, Văn Yên-Yên Bái-Thác Bà **94,64%**; TBA 220 kV Bảo Thắng/Yên
  Bái một máy chạy 90-100% khi tách lưới nhận điện TQ; TBA 110 kV Nghĩa Lộ đang nhận 260,4 MW, quy hoạch thêm 170,8 MW ⇒ vượt hạ tầng; ~300 MW
  trong quy hoạch **chưa có điểm đấu nối**; 2 đường 220 kV vướng quy hoạch khoáng sản/giải phóng mặt bằng [DK, Báo Lào Cai 17/11/2026].
  Không có số giờ/MW bị giới hạn phát.
- **Gần 400 thuỷ điện nhỏ** đấu lưới phân phối EVNNPC, bổ sung ~1.800-1.900 MW lúc cao điểm [DK, VOH 2026, file thuỷ điện] ⇒ miền Bắc vẫn
  **thiếu nguồn**, nên rủi ro điều độ thấp; rủi ro thật là **nghẽn 110 kV mùa lũ** khi nhiều nhà máy cùng phát đầy [UĐ].

### 2d. Thuỷ điện tích năng (dự án giai đoạn quy hoạch)
- PDP8 điều chỉnh: tích năng **2.400-6.000 MW tới 2030**, **20.691-21.327 MW tới 2050** [DK, MOIT/tóm tắt tìm kiếm; cần đối chiếu QĐ 768 gốc].
- Dự án thứ nhất (~1.200 MW, Khánh Hoà, chủ đầu tư nhà nước) đang thi công [DK cấp 2; mốc COD: không có số]. Dự án thứ hai **1.200 MW ở Sơn La
  khởi công 14/11/2026**, vốn ~27.871 tỷ (~23 tỷ/MW), GĐ1 900 MW 2027-2030, GĐ2 300 MW 2031-2032, ~1,5 tỷ kWh/năm, thủ tục đầu tư hoàn tất 76 ngày
  sau chủ trương [DK, VietnamPlus/Báo Đấu thầu 11/2026].
- **Cơ chế giá cho tích năng:** không tìm thấy khung/phương pháp riêng lượt này (BESS đã có hai thành phần từ T1/2026 theo TT 62 + QĐ 2987)
  [DK + không có số]. ⇒ [UĐ] Dự án tích năng ở giai đoạn quy hoạch = **quyền chọn ADMIN thuần**: giá trị phụ thuộc vào (i) có trong danh mục
  quy hoạch/kế hoạch thực hiện, (ii) chủ trương đầu tư, (iii) cơ chế giá công suất + PPA, (iv) huy động ~20-25 tỷ VND/MW. Với DN đòn bẩy cao,
  phần vốn chủ 20-30% của 1.000+ MW là cam kết **lớn hơn nhiều lần** quy mô tài sản điển hình của nhóm 50-100 MWp + 8-50 MW [UĐ].

## 3. Cấu trúc cạnh tranh và cơ chế giá
### 3a. Người mua duy nhất, sức khoẻ EVN
- 100% bán cho EVN/EPTC (hoặc đơn vị phân phối với thuỷ điện nhỏ) [NỀN]. DPPA (NĐ 57/2025, sửa bởi NĐ 243/2026 [DK cấp 2]) là kênh đa dạng
  hoá **chậm**, chủ yếu cho dự án mới [UĐ].
- EVN 2025 lãi ~51.881 tỷ nhưng 2026 bị ép: thuỷ điện −16%, nhiên liệu đắt, bán lẻ −2% từ 01/11/2026 (file thuỷ điện, file phát điện) ⇒
  [UĐ] **EVN có động cơ tài chính trực tiếp** để kéo dài đàm phán giá tái tạo và giữ tiền; đây là cùng một lực với "kìm giá bán lẻ".

### 3b. Khung giá điện mặt trời sau FIT — văn bản gốc và cái chưa kiểm được
**Sửa tiền đề của prompt (quan trọng):** FIT điện mặt trời có **thời hạn 20 năm kể từ COD** (QĐ 11/2017/QĐ-TTg; QĐ 13/2020/QĐ-TTg) [NỀN — PHẢI
KIỂM văn bản]. Thứ "đã hết hạn" là **cửa sổ đủ điều kiện** (FIT1 9,35 USc/kWh cho COD trước 30/06/2019, riêng Ninh Thuận có gia hạn tới
31/12/2020 cho tổng ~2.000 MW theo NQ 115/NQ-CP; FIT2 7,09 USc mặt đất / 7,69 USc nổi cho COD tới 31/12/2020) [NỀN]. Nhà máy COD 2019-2020
có FIT thì **không** hết hạn trước ~2039-2040. Vì vậy với nhà máy 50-100 MWp, "chuyển sang khung giá chuyển tiếp" chỉ xảy ra qua 2 đường:

| Đường | Cơ chế | Văn bản | Trạng thái as-of |
|---|---|---|---|
| **(1) Lỡ cửa sổ FIT = dự án chuyển tiếp** | Đàm phán giá ≤ trần QĐ 21/QĐ-BCT (07/01/2023): mặt trời mặt đất **1.184,90**, nổi **1.508,27** đ/kWh (chưa VAT); trong lúc đàm phán phát lên lưới với **giá tạm 50% trần** | QĐ 21/2023 | Tới 06/2025 chỉ **16 dự án / 943,93 MW** chốt giá chính thức [DK, VnExpress/tóm tắt tìm kiếm]. Số 2026: không có số |
| **(2) Có FIT nhưng thiếu văn bản chấp thuận nghiệm thu (CCA) tại COD = "hồi tố"** | KL 1027/KL-TTCP (28/04/2023): thiếu CCA thì không đủ điều kiện FIT. **173 nhà máy/phần nhà máy (~12 GW)**. Phương án EVN: 28 giữ FIT1, 25 FIT1→FIT2, 13 tạm dừng thanh toán, **106 áp trần chuyển tiếp**; giá tạm ~**70% FIT2**; đề xuất T4/2026: chỉ áp giá thấp cho **giai đoạn COD→ngày có CCA**, từ ngày có CCA trả đủ FIT | KL 1027/2023; NQ 233/2024; TT 10/2023 | **05/10/2026: EPTC đề nghị đàm phán "giảm giá điện tối đa" cho giai đoạn vi phạm, không vượt trần chuyển tiếp**; BCT khuyến nghị rà soát, xác định lại giá, báo cáo để **bù trừ thanh toán** [DK, VnExpress 05/10/2026]. Nhà đầu tư phản đối hồi tố, có ý kiến dọa từ chối bán điện [DK, VCCI 07/2026]. EVN đã bắt đầu thanh toán lại một phần [DK, pv magazine 29/05/2026, không có %]. **Chưa có quyết định cuối** |

**Quy đổi độ lớn [UĐ, tỷ giá 25.755, mệnh giá USc là NỀN]:** FIT1 ≈ **2.408** đ/kWh; FIT nổi ≈ **1.981**; FIT2 ≈ **1.826**; 70% FIT2 ≈ 1.278; trần
chuyển tiếp mặt đất 1.184,90 (**−51% so FIT1**), nổi 1.508,27 (**−24% so FIT nổi**). ⇒ Với nhà máy rơi vào "106 dự án áp trần chuyển tiếp",
doanh thu đơn vị giảm một nửa cho giai đoạn bị xác định lại, **cộng** nghĩa vụ hoàn/bù trừ phần đã nhận theo FIT. Đây là rủi ro lớn nhất của
phân khúc (a), và nó **nhị phân theo từng nhà máy** (có/không CCA, ngày CCA so với COD).

**Khung giá năm 2026 cho nhà máy mặt trời (QĐ 2946/QĐ-BCT ký 05/11/2026)** [DK, EVN 10/11/2026; Thanh Niên 14/11/2026], đ/kWh, chưa VAT:

| Loại hình | Bắc | Trung | Nam | Δ so 2025 (QĐ 988/QĐ-BCT 10/04/2025) |
|---|---|---|---|---|
| Mặt đất, không BESS | 1.591,02 | **1.293,17** | **1.104,32** | +15,1% / **+16,8%** / +9,1% (2025: 1.382,7 / 1.107,1 / 1.012,0) |
| Nổi, không BESS | 1.939,74 | 1.560,63 | 1.340,21 | +~112-254 đ |
| Mặt đất, kèm BESS (≥10% công suất, 2h) | 1.813,48 | 1.469,90 | 1.254,97 | |
| Nổi, kèm BESS | 2.120,31 | 1.703,21 | 1.461,39 | |

- **Phạm vi:** "loại hình nhà máy quy định tại điểm a khoản 2 Điều 1 TT 09/2025/TT-BCT" [DK]. **TT 54/2025/TT-BCT** (hiệu lực 21/11/2025) bổ
  sung nhóm phải áp khung giá mới: nhà máy **đã hết thời hạn biểu giá hoặc PPA**, BOT đã chuyển giao, và tái tạo nhỏ **không còn** thuộc diện
  chi phí tránh được [DK, MOIT 11/2025].
- **CHƯA KIỂM ĐƯỢC (phải đọc văn bản gốc trước khi dùng):** (i) khung 2026 có áp cho dự án chuyển tiếp **chưa ký** PPA theo QĐ 21 hay không
  (tức trần 1.184,90 còn hiệu lực hay được thay bằng khung năm); (ii) **Khánh Hoà/Lâm Đồng mới thuộc "miền Trung" hay "miền Nam"** trong phụ
  lục QĐ 2946 — chênh 189 đ/kWh (17%) giữa 2 miền ở hạng mặt đất; (iii) thông số tính (suất đầu tư, giờ nắng, WACC, tỷ giá) — không có trên
  trang công bố; (iv) dự thảo BCT 03/09/2026 đổi cách xác định khung giá mặt trời/gió [DK cấp 2] — nội dung chưa đọc.
- **Đọc [UĐ]:** khung "miền Trung" 2026 mặt đất (1.293) **cao hơn** trần chuyển tiếp 2023 (1.185) ~9%; khung "miền Nam" (1.104) **thấp hơn**
  ~7%. ⇒ Nếu dự án chuyển tiếp được đàm phán lại theo khung năm, hướng của cú sốc phụ thuộc hoàn toàn vào ánh xạ tỉnh→miền (điểm (ii)). Với
  nhà máy có FIT hợp lệ, khung năm **không** tác động trực tiếp tới 2039-2040.
- **FX:** FIT tính theo USc và quy đổi theo tỷ giá [NỀN] ⇒ VND lên giá −2,35%/12T là lực cản nhỏ, ngược chiều có lợi cho nợ USD.

### 3c. Khung giá thuỷ điện nhỏ / vừa
- **≤30 MW (biểu giá chi phí tránh được, hợp đồng tối đa 20 năm từ COD):** QĐ 392/QĐ-BCT (06/03/2026, áp 01/01-31/12/2026): giá điện năng
  **miền Bắc mùa khô 725-726, mùa mưa 702-704 đ/kWh; điện năng dư 351 đ/kWh; giá công suất 1.932 đ/kWh** (áp cho giờ cao điểm mùa khô [NỀN —
  PHẢI KIỂM]) [DK, luatvietnam]. **Biểu giá CHƯA gồm** thuế tài nguyên nước, tiền DVMTR, tiền cấp quyền khai thác TN nước và VAT — **bên mua
  trả thêm** [DK, QĐ 392]. ⇒ trả lời phần "pass-through" còn mở ở file thuỷ điện, **cho nhóm ≤30 MW**. Phương pháp (TT 10/2025 sửa bởi TT
  20/2026, hiệu lực 02/06/2026): giá điện năng = chi phí nhiên liệu bình quân của nhiệt điện biến đổi cao nhất được huy động; vùng theo **ranh
  giới điều độ**, không theo địa giới; sáp nhập tỉnh không đổi biểu giá hợp đồng đã ký [DK]. Biểu giá năm mới chưa ban hành ⇒ tạm áp năm trước.
- **Hết hợp đồng chi phí tránh được:** đàm phán lại theo Luật Điện lực + khung giá mới (TT 54/2025). Ca thật: bên mua (đơn vị miền Trung) đề
  xuất **giá tạm ~1/4 giá cũ**, một số nhà máy dừng phát 2 tháng đến >1 năm, xả bỏ nước [DK, Tiền Phong 30/10/2026]. **Miền Bắc: chưa thấy ca
  tương tự** (tìm 1 lần — âm tính không có nghĩa là không có). Nhà máy COD ≤2007-2010 sẽ chạm mốc 20 năm trong 2027-2030 [UĐ].
- **>30 MW:** tham gia thị trường trực tiếp, CfD `Qc×Pc + (Qm−Qc)×FMP`, khung thuỷ điện 2026 **0-1.110 đ/kWh** (QĐ 1127/QĐ-BCT) — chi tiết và
  bất đối xứng năm khô ở file thuỷ điện §3. Với dải 8-50 MW, **ngưỡng 30 MW tách DN thành 2 cơ chế doanh thu khác hẳn nhau** — DD phải tách.

### 3d. Cấu trúc cạnh tranh
- Không cạnh tranh về giá với nhau (bán theo biểu giá/PPA cho 1 người mua); "cạnh tranh" thật là **giành chỗ trong đường dây và giờ trưa**:
  nhà máy cùng nút lưới bị cắt theo tiêu chí "minh bạch, không phân biệt" của NSMO [DK, Tuổi Trẻ News 14/11/2025] ⇒ nhà máy mới cùng nút làm
  tăng cắt giảm của nhà máy cũ [UĐ]. Rào cản gia nhập thấp về công nghệ, cao về **đấu nối + quy hoạch + giá**.
- Nhóm DN niêm yết cùng loại thường là IPP tư nhân vừa và nhỏ, đòn bẩy cao, phụ thuộc vào ngân hàng trong nước để tái cấp vốn [NỀN].
  Ember ước IRR mặt trời tập trung **6,1%**, kèm BESS **7,3%** [DK, pv magazine, không rõ ngày báo cáo] — **thấp hơn** lãi vay VND ~10-11,5%
  (§1b) ⇒ [UĐ] dự án mới theo khung năm chỉ "bankable" với cấu trúc vốn thận trọng hoặc DPPA; tăng trưởng công suất của IPP đòn bẩy cao bị
  chặn bởi chi phí vốn nhiều hơn bởi cơ hội.

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1 — nguyên nhân gốc của bối cảnh hiện tại:** áp lực lên ngành đến từ **(i) văn bản/thanh tra** (CCA, hồi tố, giá tạm, hết hợp đồng),
**(ii) lưới đi sau nguồn** (cấu trúc, lặp lại từ 2019), **(iii) thuỷ văn** (El Niño, ngoại sinh). **Không** phải mất cân đối vĩ mô trong nước;
cầu điện +10-14% là nền **thuận**. Lạm phát 5,09% chỉ vào qua kênh chính trị giá bán lẻ ⇒ EVN ép biên ⇒ củng cố (i).
**Trục 2 — có tự giới hạn không:** (i) cần **một chuỗi quyết định hành chính** (Chính phủ/BCT chốt phương án 173 dự án; phương pháp giá sau
hợp đồng) — làm được trong vài tháng về mặt kỹ thuật, nhưng lịch sử 2023-2026 cho thấy kéo dài >3 năm ⇒ **không chứa gọn theo tháng**. (ii)
theo lịch đầu tư lưới 2027+. (iii) theo lịch tự nhiên (đáy mùa khô 2027).

### 4a. Theo phân khúc — driver CHÍNH của lợi nhuận/giá trị (tổng = 1 mỗi dòng)
| Phân khúc | Tầm | ADMIN_GATED | CYCLICAL | STRUCTURAL | Lý do ngắn |
|---|---|---|---|---|---|
| (a) Mặt trời Nam Trung Bộ có FIT / chuyển tiếp | **12T** | **0,60** | 0,20 | 0,20 | = file phát điện §4a (tái tạo 0,60/0,20/0,20). Kết quả CCA/giá chuyển tiếp/bù trừ thanh toán là biến nhị phân lớn nhất; cyclical = bức xạ + thuỷ điện miền Nam thấp (El Niño, thuận); structural = nghẽn lưới + đáy trưa |
| (a) | **36T** | **0,50** | 0,10 | 0,40 | Văn bản vẫn quyết (phương án CCA, khung năm, DPPA, Luật Điện lực); structural tăng vì mục tiêu 46-73 GW làm đáy trưa sâu hơn nhanh hơn lưới/BESS |
| (b) Thuỷ điện nhỏ 8-50 MW miền Bắc | **12T** | 0,35 | **0,55** | 0,10 | = file thuỷ điện §4. Với nhà máy ≤30 MW: biểu giá cố định (không CfD) ⇒ thuần khối lượng; nhà máy chạm mốc hết hợp đồng trong 12T ⇒ tự chuyển sang ADMIN ≥0,7 |
| (b) | **36T** | **0,45** | 0,35 | 0,20 | = file thuỷ điện: giá sau hợp đồng (TT 54/2025), gia hạn giấy phép, nghẽn 110 kV Tây Bắc (structural) |
| (c) Tích năng giai đoạn quy hoạch | 36T+ | **0,75** | 0,05 | 0,20 | Không có dòng tiền trong 36T; giá trị = có/không cơ chế giá + PPA + vốn; structural = nhu cầu lưu trữ thật (PDP8 2,4-6 GW) |

### 4b. Tổng hợp cho DN hỗn hợp (a)+(b) (+(c) là quyền chọn)
| Tầm | ADMIN_GATED | CYCLICAL | STRUCTURAL | Diễn giải |
|---|---|---|---|---|
| **12 tháng** | **0,50** | 0,35 | 0,15 | Trung bình ~50/50 theo doanh thu (a)/(b) [UĐ — phải thay bằng tỷ trọng thật]. **Phòng hộ tự nhiên một phần**: El Niño thuận cho (a), bất lợi cho (b), nhưng hai tài sản ở 2 vùng khí hậu khác nhau và (b) miền Bắc chịu El Niño nhẹ hơn ⇒ phòng hộ yếu hơn cảm giác |
| **36 tháng** | **0,50** | 0,20 | 0,30 | Văn bản + chi phí vốn (đòn bẩy cao) quyết giá trị; structural là lưới/đáy trưa (bất lợi cho (a)) và thiếu nguồn miền Bắc (thuận cho (b)) |

**Công thức thay trọng số:** `P_DN = w_a × dòng(a) + w_b × dòng(b)`, với w = tỷ trọng EBITDA (không phải doanh thu, vì biên mặt trời FIT cao hơn).
Nếu ≥30% công suất mặt trời nằm trong nhóm 173 dự án CCA ⇒ ADMIN 12T của DN ≥0,60.

**Độ tin cậy: AMBIGUOUS ~60/40.** Nhãn ADMIN cho (a) khá chắc; phần mơ hồ: không có số cắt giảm 2026, ánh xạ tỉnh→miền QĐ 2946 chưa đọc,
không biết phạm vi khung năm cho dự án chuyển tiếp.
**Pha [UĐ]:** (a) đang ở **giữa một tranh chấp hành chính** đã kéo 3,5 năm (từ KL 1027/2023), lần đề xuất gần nhất (05/10/2026) nghiêng về
hướng **có hồi tố một phần** (giai đoạn COD→CCA), đổi lại giữ FIT sau CCA; khung năm vừa tăng 9-17%. (b) đi **từ đỉnh thuỷ văn (2025) xuống
đáy (mùa khô 2027)**. Chi phí vốn: niêm yết đứng yên, **liên NH đang nhích lên**.

**Điều làm tôi đổi phân loại (falsifiers):**
- (i) Văn bản chính thức chốt phương án 173 dự án **không hồi tố** (giữ FIT từ COD) ⇒ ADMIN 12T (a) xuống ~0,40, STRUCTURAL lên.
- (ii) Chốt phương án **hồi tố toàn thời gian** hoặc áp trần chuyển tiếp cho cả phần sau CCA ⇒ ADMIN (a) ≥0,70 và rủi ro thanh khoản DN đòn bẩy
  cao (hoàn tiền + vi phạm covenant) chuyển thành rủi ro tồn tại.
- (iii) Số NSMO/EVN cho thấy cắt giảm mặt trời Nam Trung Bộ 2026 ≥10% sản lượng ⇒ STRUCTURAL 12T (a) ≥0,35.
- (iv) Mực nước/dòng chảy mùa khô miền Bắc T12/2026-T2/2027 ≥ trung bình nhiều năm ⇒ CYCLICAL 12T (b) xuống ~0,45.
- (v) LNH 3M >7,5% kéo dài + CCTG 12M >7,5% (kill-switch A ARMED) ⇒ thêm một lớp tài chính vào cả (a) và (b) cho DN đòn bẩy cao.

## 5. FORECAST khoá trước (2026-11-20)
Bobby không tự chấm. Mike/người chấm đọc nguồn chính thức (EVN, NSMO, BCT, Chính phủ, UBND tỉnh) tại ngày chấm; nguồn không công bố trước
ngày chấm ⇒ "không chấm được". **Đã khoá ở file chị em (chỉ dẫn chiếu, KHÔNG khoá lại):** tỷ trọng thuỷ điện 2026 ≤26% P0,85 (thuỷ F1);
H1/2027 <21% P0,60 (thuỷ F2); hồ lớn Bắc/Bắc Trung Bộ về mực nước chết trước 30/06/2027 P0,45 (thuỷ F8); El Niño còn ở T3-T5/2027 P0,45 (thuỷ
F10); CCTG 12M ≤7,4% ngày 2027-05-12 P0,55 (thuỷ F11); văn bản phương pháp giá thuỷ điện sau hết PPA trước 30/09/2027 P0,40 (thuỷ F12); giá
bán lẻ tăng ≥1 lần tới 30/06/2027 P0,40 (thuỷ F7); Luật Điện lực sửa đổi thông qua kỳ họp 2 P0,70 (than F9).

| # | Mệnh đề (kiểm chứng được) | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| **S1** | Có văn bản chính thức (Chính phủ/Thủ tướng/BCT) **chốt phương án giá** cho nhóm 173 nhà máy vướng CCA, HOẶC EVN/BCT công bố đã thống nhất giá với **≥50%** số nhà máy đó | **0,35** | 2027-06-30 | chinhphu.vn / moit.gov.vn / EVN qua báo |
| **S2** | Nếu S1 xảy ra: phương án **có** giảm giá/hồi tố cho giai đoạn COD→CCA (không giữ nguyên FIT từ COD cho mọi nhà máy) | **0,75** (có điều kiện) | 2027-06-30 | văn bản S1 |
| **S3** | EVN/NSMO công bố sản lượng **điện mặt trời cả năm 2026 ≥ 27,8 tỷ kWh** (10T: 24,04) | **0,70** | 2027-01-31 | EVN cơ cấu nguồn cả năm |
| **S4** | BCT ban hành khung giá phát điện mặt trời **năm 2027**, hạng mặt đất không BESS **miền Trung ≥ 1.293,17 đ/kWh** | **0,55** | 2027-12-31 | moit.gov.vn / EVN |
| **S5** | Biểu giá chi phí tránh được **2027** cho thuỷ điện nhỏ: giá điện năng **miền Bắc mùa khô giờ cao điểm > 726 đ/kWh** | **0,70** | 2027-06-30 | QĐ BCT biểu giá 2027 |
| **S6** | Trước 30/06/2027, EVN/NSMO/BCT/UBND-Sở Công Thương (hoặc báo chính thống trích nguồn đó) nêu **cắt giảm/giới hạn huy động điện mặt trời tại Nam Trung Bộ** (địa bàn Ninh Thuận/Bình Thuận cũ) **xảy ra trong năm 2027** do lưới/dư công suất | **0,55** | 2027-06-30 | EVN/NSMO/báo |
| **S7** | Trước 30/06/2027, có **≥1 thuỷ điện nhỏ miền Bắc** được nguồn chính thức/báo chính thống nêu **dừng phát hoặc bị áp giá tạm** do hết hợp đồng biểu giá chi phí tránh được | **0,45** | 2027-06-30 | báo/Sở Công Thương/EVNNPC |

Lập luận [UĐ]:
- **S1/S2:** tranh chấp đã qua 3,5 năm, đề xuất mới nhất (05/10/2026) vẫn là "đề nghị đàm phán"; EVN bị ép biên 2026-27 ⇒ không vội chốt;
  Luật Điện lực sửa đổi có thể tạo khung xử lý nhưng không tự chốt giá. S2 cao vì mọi phương án đã nêu (EVN T4/2026, EPTC 10/2026, BCT) đều có
  giảm giá cho giai đoạn thiếu CCA; giữ nguyên FIT từ COD mâu thuẫn với KL 1027.
- **S3:** cần T11-T12 ≥3,76 tỷ kWh, tức ~1,88/tháng so với bình quân 10T ~2,40 ⇒ dư địa rộng. Rủi ro: T11-T12 mùa mưa bão miền Trung, cắt giảm
  vì lũ/thuỷ điện xả.
- **S4:** khung 2026 tăng 9-17% vì giá thiết bị tăng (nhà đầu tư nêu) và thông số mới; lực ngược: VND lên giá, giá module có thể hạ, EVN ép biên,
  dự thảo 03/09/2026 đổi phương pháp (chưa đọc) ⇒ gần 50/50 nghiêng nhẹ lên.
- **S5:** phương pháp gắn chi phí nhiên liệu nhiệt điện biến đổi cao nhất được huy động; 2026 giá than +30%, LNG ×2,8, khí gắn dầu cao (file phát
  điện §1) và nhiệt điện chạy nhiều ⇒ biểu giá 2027 nhiều khả năng tăng. Lực ngược: Brent/JKM đã qua đỉnh T10-T11, VND lên giá.
- **S6:** El Niño + cầu +14% làm giảm cắt giảm ở cấp hệ thống, nhưng đáy trưa và nghẽn cục bộ vẫn còn; điều kiện "có nguồn công khai" kéo P xuống.
- **S7:** ca đã có ở miền Trung (10/2026); miền Bắc có nhiều nhà máy nhỏ COD sớm, nhưng chưa thấy ca ⇒ dưới 0,5.

## 6. DD cần kiểm gì (checklist cho người đọc BCTC — kiểm bằng số, theo TỪNG nhà máy)
**A. Mặt trời Nam Trung Bộ (50-100 MWp)**
1. **Loại giá từng nhà máy:** FIT1 9,35 / FIT2 7,09 / nổi 7,69 USc hay **chuyển tiếp** (QĐ 21/2023); ngày COD; **ngày văn bản chấp thuận nghiệm
   thu (CCA)** so với COD. Có trong danh sách 173 không, thuộc nhóm nào (giữ FIT1 / FIT1→FIT2 / tạm dừng / áp trần chuyển tiếp). Nếu DN mô tả
   "FIT đã hết hạn" ⇒ yêu cầu giải thích: FIT có thời hạn 20 năm, nên câu đó hàm ý nhà máy chuyển tiếp hoặc bị xác định lại.
2. **Ghi nhận doanh thu:** đang ghi theo FIT đầy đủ, theo giá tạm (70% FIT2 / 50% trần), hay theo tiền thực thu? **Doanh thu đã ghi nhưng EVN
   chưa trả** (phải thu tranh chấp) — số dư, tuổi nợ theo quý 2024→2026, dự phòng, ý kiến kiểm toán (ngoại trừ/nhấn mạnh). Mô phỏng **nghĩa vụ
   hoàn/bù trừ** nếu áp trần chuyển tiếp cho giai đoạn COD→CCA (đ/kWh chênh × kWh giai đoạn đó).
3. **Sản lượng và cắt giảm:** kWh thương phẩm theo tháng 2020→2026 so với P50/P90 thiết kế; **kWh bị cắt** (theo lệnh điều độ) theo tháng và %;
   hệ số công suất; suy giảm tấm pin/năm. Tách giảm do bức xạ vs do cắt giảm.
4. **PPA:** điều khoản cắt giảm (mặc định: không bồi thường), điều khoản tỷ giá (USD→VND, kỳ điều chỉnh), thời hạn, quyền đơn phương của bên mua,
   cơ chế giải quyết tranh chấp.
5. **Đấu nối:** cấp điện áp, TBA/đường dây đấu nối, chung nút với nhà máy nào (nhà máy mới cùng nút ⇒ cắt nhiều hơn), công trình lưới giải toả
   đã/chưa đóng điện.
6. **BESS:** kế hoạch lắp thêm (capex/MW, nguồn vốn), có được hưởng khung "kèm BESS" không (đã có PPA thì thường không).
7. **Khung giá 2026 áp được không:** với dự án chuyển tiếp chưa ký PPA — đang đàm phán theo trần QĐ 21 hay khung năm; nhà máy thuộc "miền Trung"
   hay "miền Nam" theo phụ lục QĐ 2946 (chênh 17%).
8. **Đất/giấy phép:** thời hạn thuê đất, mặt nước (nổi), tranh chấp đất/quy hoạch, sáp nhập tỉnh có đổi thẩm quyền.

**B. Thuỷ điện nhỏ/vừa miền Bắc (8-50 MW)**
9. **Tách theo ngưỡng 30 MW:** nhà máy ≤30 MW theo biểu giá chi phí tránh được (năm ký, **năm hết hợp đồng 20 năm**, giá năm 2026 theo QĐ 392:
   725-726 / 702-704 / dư 351 / công suất 1.932 đ/kWh miền Bắc) vs >30 MW tham gia thị trường (Qc/Pc/FMP — dùng checklist file thuỷ điện §6).
10. **Mốc hết hợp đồng trong 2027-2030:** kế hoạch đàm phán theo TT 54/2025, kịch bản giá tạm ~1/4 (ca Tiền Phong 30/10/2026), số tháng không có
    doanh thu chịu được với dòng tiền + lịch trả nợ.
11. **Sản lượng:** kWh theo tháng ≥10 năm, năm El Niño (2015-16, 2019-20, 2023) vs La Niña (2022, 2025); tỷ trọng mùa khô; điện năng dư (giá 50%).
12. **Pass-through:** tiền cấp quyền khai thác TN nước, thuế tài nguyên nước, DVMTR 36 đ/kWh — bên mua **có trả thêm** đúng như QĐ 392 không, phải
    thu liên quan, tranh chấp.
13. **Lưới 110 kV:** số giờ/MWh bị giới hạn phát mùa lũ (Lào Cai/Yên Bái cũ: các tuyến đã chạm ~95% định mức), điểm đấu nối có trong 300 MW "chưa
    có điểm đấu nối" không.
14. **Thiên tai/an toàn đập:** thiệt hại lũ/sạt lở (tiền lệ bão lớn miền Bắc 2024 [NỀN]), bảo hiểm, chi phí khắc phục, quy trình vận hành hồ, nghĩa
    vụ xả hạ du.
15. **Giấy phép:** thời hạn giấy phép khai thác TN nước, thuê đất, giấy phép hoạt động điện lực.

**C. Dự án đang xây / đề xuất (kể cả tích năng)**
16. Trạng thái pháp lý từng dự án: có trong PDP8/kế hoạch thực hiện chưa, chủ trương đầu tư, giấy phép xây dựng, PPA/cơ chế giá (tích năng: **chưa
    thấy khung giá riêng** — DN dựa vào văn bản nào?).
17. Tổng vốn, tỷ lệ vốn chủ, cam kết góp vốn so với vốn chủ hiện có; nguồn vốn (ngân hàng, trái phiếu, phát hành thêm); bên liên quan nhận thầu
    EPC/cung cấp thiết bị (giá chuyển nhượng). Theo luật user: **dự án mới định giá base = sổ sách/NPV 0**, lệch chỉ khi có cơ sở độc lập; mọi
    tăng vốn trong chu kỳ đầu tư ⇒ WARNING.

**D. Đòn bẩy và chi phí vốn (biến cấp 1 của ngành này)**
18. Dư nợ theo đồng tiền, kỳ hạn, **lịch trả gốc 2027-2029**, lãi thả nổi (biên trên lãi huy động 12M tham chiếu của NH nào), tài sản đảm bảo
    (quyền đòi nợ EVN?), covenant DSCR và tình trạng vi phạm/miễn trừ; trái phiếu DN đáo hạn, điều khoản mua lại trước hạn.
19. **DSCR ở kịch bản xấu kết hợp:** áp trần chuyển tiếp cho giai đoạn COD→CCA + cắt giảm 10% + thuỷ điện năm El Niño + lãi +1pp.
20. Bảo lãnh cho công ty liên quan, khoản cho vay/ứng trước cho bên liên quan, cổ tức có vượt FCF không.
21. **Độ nhạy bắt buộc ghi số:** ±1pp lãi vay; ±5pp cắt giảm; FIT→trần chuyển tiếp cho từng nhà máy trong danh sách 173; ±20% sản lượng thuỷ điện;
    ±1% USD/VND; EVN trả chậm +90 ngày.

Định giá (nếu dùng): r neo lãi huy động 12T (effective **7,4%** hôm nay, CCTG 12M) + chiết khấu thanh khoản; **không** ngoại suy 2025 (La Niña)
cho thuỷ điện; dòng tiền mặt trời tách kịch bản theo kết quả CCA từng nhà máy, không dùng một kịch bản "trung bình".

## 7. Tự kiểm và giới hạn
- **Tốt hơn tôi nghĩ:** khung giá mặt trời 2026 **tăng** 9-17% (BCT vẫn cập nhật chi phí, không kìm như thuỷ điện 1.110); BESS có khung giá hai
  thành phần; El Niño thuận cho mặt trời Nam Trung Bộ; cầu +14% hấp thụ tốt hơn 2025; QĐ 392 xác nhận phí/thuế nước được bên mua trả thêm cho
  thuỷ điện nhỏ.
- **Xấu hơn / chưa biết:** tiền đề "FIT hết hạn" của prompt không khớp văn bản tôi biết (FIT 20 năm) ⇒ rủi ro thật là **hồi tố CCA**, nhị phân và
  chưa chốt sau 3,5 năm; không có số cắt giảm 2026; ánh xạ tỉnh→miền QĐ 2946 chưa đọc; phạm vi khung năm cho dự án chuyển tiếp chưa rõ; không có
  cơ chế giá tích năng; liên NH đang nhích lên trong khi số niêm yết đứng yên; mệnh giá FIT (USc) và thời hạn 20 năm là [NỀN] chưa mở văn bản gốc.
- **Blind:** không nhận ra danh tính DN; rò rỉ tên DN nước ngoài/chủ đầu tư tích năng ghi ở §0, không dùng.
- Snapshot vĩ mô UNVERIFIED (TradingEconomics), không vintage.

## Nguồn (một số URL có tên DN/tổ chức trong đường dẫn — người đọc blind sau có thể bỏ qua)
- Snapshot: `/tmp/bobby_in/macro_snapshot_20261120.md` (as-of 2026-11-20). Lãi suất PIT: `deposit_rate_vn.effective_deposit_rate('2026-11-20')` = 7,4% (CCTG 12M 02/11; Big-4 6,8%; last_update 16/11); `macro_killswitch_a_status()` CLEAR.
- QĐ 2946/QĐ-BCT khung giá mặt trời 2026 (EVN, 10/11/2026): https://www.evn.com.vn/d/vi-VN/news/Bo-Cong-Thuong-phe-duyet-khung-gia-phat-dien-loai-hinh-nha-may-dien-mat-troi-nam-2026-60-17-510253 ; Thanh Niên 14/11/2026: https://thanhnien.vn/tang-gia-dien-mat-troi-khuyen-khich-dau-tu-pin-luu-tru-18526111320091118.htm ; MOIT: https://moit.gov.vn/tin-tuc/bo-cong-thuong-phe-duyet-khung-gia-phat-dien-loai-hinh-nha-may-dien-mat-troi-nam-2026.html
- Dự thảo khung giá gió/mặt trời 2026 (Tuổi Trẻ 17/07/2026): https://tuoitre.vn/bo-cong-thuong-lay-y-kien-khung-gia-dien-gio-dien-mat-troi-nam-2026-do-evn-tinh-toan-100260717122110667.htm
- QĐ 988/QĐ-BCT khung 2025: https://tapchicongthuong.vn/gia-phat-dien-toi-da-cho-nha-may-dien-mat-troi-la-1-876-57-dong-kwh-139270.htm ; https://vepg.vn/wp-content/uploads/2025/08/988_QD-BCT_659929.doc
- TT 54/2025/TT-BCT (sửa TT 09/2025, TT 12/2025): https://moit.gov.vn/tin-tuc/phat-trien-nang-luong/bo-cong-thuong-ban-hanh-thong-tu-sua-doi-khung-gia-phat-dien-va-phuong-phap-xac-dinh-gia-dich-vu-phat-dien.html ; TT 09/2025: https://luatvietnam.vn/xuat-nhap-khau/thong-tu-09-2025-tt-bct-thu-tuc-phuong-phap-xac-dinh-khung-gia-phat-dien-khung-gia-nhap-khau-dien-389500-d1.html
- 173 dự án CCA, EPTC đề nghị đàm phán (VnExpress 05/10/2026): https://vnexpress.net/evn-de-nghi-dam-phan-lai-gia-mua-dien-loat-du-an-tai-tao-vuong-nghiem-thu-5128495.html ; phương án 28/25/13/106: https://bbw.vn/evn-de-xuat-hai-phuong-an-doi-voi-173-du-an-dien-tai-tao-can-xac-dinh-lai-gia-ban-dien-uu-dai-53988.html ; https://znews.vn/business-times-evn-de-xuat-cat-manh-gia-uu-dai-173-du-an-dien-tai-tao-post1644310.html ; VCCI: https://www.vcci.com.vn/news/phan-doi-gia-tam-tinh-cua-evn-dn-nang-luong-tai-tao-co-the-tu-choi-ban-dien ; https://diendandoanhnghiep.vn/hoi-to-gia-ban-dien-tai-tao-chua-co-su-dong-thuan-10151494.html
- Dự án chuyển tiếp, giá tạm 50% (2023): https://baodautu.vn/du-an-nang-luong-tai-tao-chuyen-tiep-gia-tran-khong-phai-la-gia-chot-d191955.html ; https://nhadautu.vn/bo-cong-thuong-duyet-gia-tam-cho-19-du-an-dien-tai-tao-chuyen-tiep-d76768.html
- pv magazine 29/05/2026 (công suất, hệ số công suất miền Trung, PPA không bồi thường cắt giảm, IRR Ember, đầu tư truyền tải): https://www.pv-magazine.com/2026/05/29/vietnam-solar-boom-strains-grid-and-tests-project-finance/
- QĐ 2987/QĐ-BCT khung giá BESS 2026 (ESS News 17/11/2026): https://www.ess-news.com/2026/11/17/vietnam-finalizes-2026-storage-pricing-under-two-part-tariff-as-curtailment-pressure-grows/
- Đáy trưa / cắt giảm: https://congthuong.vn/dien-mat-troi-viet-nam-ky-5-suc-ep-he-thong-va-nghich-ly-khung-gio-464249.html ; https://vietnamnet.vn/dien-mat-troi-phat-manh-ban-ngay-nguon-dien-dat-do-van-ganh-gio-cao-diem-toi-2524740.html ; dư nguồn T11/2025: https://news.tuoitre.vn/unseasonal-weather-leaves-vietnams-grid-with-power-surplus-cuts-across-hydropower-wind-coal-103251113163512117.htm ; tiền lệ 2019-2020: https://www.evn.com.vn/d6/news/Qua-tai-dien-mat-troi-khu-vuc-Ninh-Thuan-Binh-Thuan-Thiet-hai-khong-chi-cua-rieng-nha-dau-tu-dien-mat-troi-66-142-23998.aspx ; https://vnexpress.net/o-at-dau-tu-dien-mat-troi-khien-luoi-dien-qua-tai-3946925.html
- Sản lượng/cơ cấu 10T/2026: https://www.vietnamplus.vn/san-luong-dien-10-thang-tang-98-evn-tap-trung-bao-dam-nguon-cung-cuoi-nam-post1145791.vnp ; https://nhandan.vn/post-999892.html
- Biểu giá chi phí tránh được 2026 (QĐ 392/QĐ-BCT 06/03/2026): https://luatvietnam.vn/dien-luc/quyet-dinh-392-qd-bct-2026-ban-hanh-bieu-gia-chi-phi-tranh-duoc-cho-nha-may-thuy-dien-nho-431541-d1.html ; TT 20/2026/TT-BCT: https://nangluongvietnam.vn/bieu-gia-chi-phi-tranh-duoc-cho-nguon-nang-luong-tai-tao-nho-dieu-chinh-nam-2026-35958.html ; https://luatvietnam.vn/dien-luc/thong-tu-20-2026-tt-bct-sua-doi-bo-sung-bieu-gia-chi-phi-tranh-duoc-cho-nha-may-dien-tai-tao-432803-d1.html ; sáp nhập tỉnh không đổi biểu giá: https://luatvietnam.vn/tin-van-ban-moi/sap-nhap-tinh-khong-lam-thay-doi-bieu-gia-mua-dien-cua-nha-may-thuy-dien-nho-trong-hop-dong-da-ky-186-111891-article.html
- Thuỷ điện nhỏ dừng phát vì giá tạm (Tiền Phong 30/10/2026): https://tienphong.vn/vuong-dam-phan-gia-mot-so-nha-may-nho-phai-dung-phat-dien-post1889871.tpo
- Lưới 110/220 kV Lào Cai/Yên Bái (Báo Lào Cai 17/11/2026): https://baolaocai.vn/nguon-dien-tang-nhanh-luoi-truyen-tai-truoc-ap-luc-qua-tai-post914656.html ; gần 400 thuỷ điện nhỏ miền Bắc: https://voh.com.vn/kinh-te/gan-400-thuy-dien-nho-giam-ap-luc-phu-tai-mien-bac-658634.html
- Tích năng: PDP8 điều chỉnh https://moit.gov.vn/tin-tuc/phat-trien-nang-luong/chinh-thuc-phe-duyet-quy-hoach-dien-viii-dieu-chinh.html ; khởi công dự án 1.200 MW Sơn La 14/11/2026: https://www.vietnamplus.vn/khoi-cong-du-an-thuy-dien-tich-nang-dong-phu-yen-tai-tinh-son-la-post1148285.vnp ; https://baodauthau.vn/sap-khoi-cong-du-an-thuy-dien-tich-nang-dong-phu-yen-gan-28000-ty-dong-post211855.html
- File chị em: `sector_read_thuy_dien_20261112.md`, `sector_read_phat_dien_20261118.md` (cùng thư mục).
