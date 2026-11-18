---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, dispatch ngày 2026-11-18. Không được cung cấp mã, giá cổ phiếu, BCTC, forward return hay khuyến nghị nào.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành tổng thầu EPC + xây lắp & lắp đặt cơ khí công nghiệp VN (nhiệt điện than/khí-LNG, điện gió/mặt trời, xi măng, hoá dầu, thép, hạ tầng) kèm chế tạo kết cấu thép/thiết bị cơ khí. Gồm pipeline cầu 2026-2028, cấu trúc cạnh tranh, quyền lực khách hàng, POC/ghi nhận, rủi ro thanh toán/bảo lãnh/vốn lưu động, chi phí vốn (bảng 5 tầng), phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED 2 tầm, FORECAST khoá trước, checklist DD.
as_of: 2026-11-18 (tin web ≤ 2026-11-18; BQ chỉ đọc deposit/CCTG PIT)
---

# SECTOR READ: Tổng thầu EPC + lắp máy công nghiệp VN, as-of 18/11/2026 (Bobby, real-time BLIND)

Không phải episode VNINDEX, không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày · **[UĐ]** ước đoán/suy luận
của Bobby · **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này.

**File chị em (đọc kèm, không chép lại):** `sector_read_power_consulting_20261028.md` (tiến độ PDP8, capex EVN, lưới 500kV,
hạt nhân, ĐGNK — F1-F10), `sector_read_phat_dien_20261118.md` (LNG/Qc, merit order), `sector_read_nhiet_dien_than_20261117.md`
(+5.300 MW than), `sector_read_thep_20261031.md` (giá thép đầu vào, đầu tư công), `sector_read_loc_hoa_dau_20261109.md` (Dung Quất
mở rộng), `sector_read_ngan_hang_quoc_doanh_20261117.md` (bảng 5 tầng 17/11).

## 0. Kiểm toán blind
- **Rò danh tính qua đường dẫn dispatch:** snapshot nằm ở thư mục `dd_LLM_20261118` ⇒ mã đích suy ra được (nhiều khả năng là
  tổng công ty lắp máy nhà nước). Tôi KHÔNG mở thư mục đó ngoài file snapshot được chỉ định.
- **Rò qua web:** kết quả tìm kiếm ngành không tách được khỏi tên tổng thầu (ngành có rất ít DN lớn). Tiêu đề lộ tên một tổng
  công ty lắp máy trong liên danh EPC Quảng Trạch II, Nhơn Trạch 3&4, và một bài "nâng cao năng lực tổng thầu EPC" của DN đó —
  bài sau **không mở**. Bài Báo Đấu thầu 28/07/2026 tôi đã mở có trích lời CEO DN đó (1 câu định tính về năng lực nhà thầu
  Việt) — dùng như dữ kiện cấu trúc ngành, không dùng như dữ kiện DN.
- **Không đọc:** giá cổ phiếu, BCTC, KQKD, backlog công bố, khuyến nghị CTCK của bất kỳ DN EPC/lắp máy nào; `kb/projects/*`;
  `agents/Taylor/*` (trừ snapshot). Không truy vấn `ticker_financial` (sẽ phải chọn DN ⇒ phá blind).
- **BQ/PIT:** `deposit_rate_vn.macro_killswitch_a_status()` + `cctg_rate_vn.current_cctg_rate()` chạy 18/11/2026.
- Snapshot vĩ mô: `TradingEconomics` qua `tav2_bq.macro_indicator`, status UNVERIFIED, giá trị lịch sử là bản hiệu chỉnh hiện
  hành (không vintage). Không có forward return trong snapshot.

## 1. Nền vĩ mô liên quan ngành (snapshot as-of 18/11/2026)
| Chỉ báo | Giá trị | Δ3T / Δ12T | Đọc cho EPC/lắp máy [UĐ] |
|---|---|---|---|
| GDP YoY | 9,95% (Q3) | +1,14 / +1,70pp | Nền cầu đầu tư rất mạnh; chính phủ đặt mục tiêu "hai con số" ⇒ áp lực chính trị đẩy dự án điện/hạ tầng |
| SX công nghiệp YoY | 15,0% (T10) | +0,5 / +4,6pp | Cầu điện công nghiệp + mở rộng nhà máy |
| PMI SX | 52,3 (T10) | −0,6 / −2,2 điểm | Vẫn mở rộng nhưng đà chậm lại so với năm trước |
| FDI luỹ kế YTD | 24,08 tỷ USD (T10) | +13,05% YoY | Cầu nhà xưởng/KCN — phần lớn là xây dựng dân dụng-công nghiệp nhẹ, không phải lắp máy nặng |
| CPI YoY / lõi | 5,09% (T10) / 4,45% (T9) | +0,64 / +1,84pp | **Rủi ro trượt chi phí** trong HĐ trọn gói; lực cản chính trị lên giá điện (EVN giảm bán lẻ 2% từ 01/11 — file phát điện) ⇒ tài chính EVN |
| USD/VND | 25.712 (17/11) | −1,77% / −2,54% | VND mạnh lên ⇒ thiết bị nhập rẻ hơn tính bằng VND; ngược lại phần doanh thu USD của HĐ hỗn hợp tiền tệ quy đổi thấp hơn |
| US 10Y / DXY | 5,15% / 103,6 | +0,44pp / +1,04pp 12T; DXY +4,1% | Chi phí vốn quốc tế (ECA, ngân hàng ngoại) cho dự án nguồn đắt lên — nhất là than (ít ngân hàng quốc tế tài trợ) |
| GDP xây dựng | STALE (141 ngày) | — | Không dùng |

**Đầu tư công [DK]:** KH 2026 ~1,02 triệu tỷ (cao nhất từ trước); giải ngân 10T **708.567 tỷ = 74,1%** KH TTg giao (NSTW 59,6%)
(Bộ TC qua VietnamPlus/Báo Đấu thầu, 11/2026). Trung hạn 2026-2030 **8,22 triệu tỷ** (NQ 27/2026/QH16, 24/04/2026; NSTW 3,8 triệu
tỷ, dự phòng 10%), giảm ≥30% số dự án ⇒ dự án to hơn, ít hơn. Bình quân ~1,64 triệu tỷ/năm, tức 2027-2030 phải cao hơn hẳn 2026
nếu kế hoạch thực hiện [UĐ, số học].

### 1b. Chi phí vốn / thanh khoản — bảng 5 tầng (ngành vốn lưu động nặng: vay ngắn hạn + hạn mức bảo lãnh [NỀN])
| Tầng | Proxy | Giá trị | Ghi chú / nguồn |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (MAX online/quầy) | **6,8%** (16/11; đi ngang từ 03/10) | Tách online/quầy theo NH: file NH quốc doanh 17/11 ghi quầy 5,4%, online 6,8% (3/4 NH) |
| B. Bán-hành-chính | CCTG 12M Big-4 cao nhất | **7,4%** (02/11; PIT chạy 18/11) | Spread CCTG − TK 12M online **+0,6pp**; 6M 1 NH 7,5% (file 17/11) |
| C. Ngoài Big-4 | NH tư nhân / lãi ẩn | VPB CCTG 9,0% (≥100tr); thực trả BQ 12M ~8,45% (1 nguồn 10/2026) | file NH quốc doanh 17/11; số NH ≥7%: **không có số** |
| D. Thị trường | LNH 3M | **6,63%** (13/11; −1,13pp 3T, +0,23pp 12T) | OMO, trúng thầu TPCP, USD tự do: **không có số** |
| D. | TPCP 10Y (chỉ tin Δ) | 4,57 (Δ12T +0,58pp) | Lãi dài hạn cao hơn năm trước |
| E. Lượng | Tín dụng vs huy động YTD, LDR, văn bản nới | **không có số** lượt này | TT 50 LDR 95% từ 01/12 (file NH 31/10) |
| — | Kill-switch A | CLEAR (effective 7,4% ≤ 7,5%) | `macro_killswitch_a_status()` 18/11 |

**Đọc:** HƯỚNG — chi phí vốn VND đi ngang ở mức cao, không hạ (A đứng, B đứng, D LNH 3M hạ từ đỉnh T8 nhưng vẫn +0,23pp YoY).
MỨC — chi phí biên thật (CCTG 7,4%, tư nhân ~8,5-9%) cao hơn niêm yết ~0,6-2pp. Với một nhà thầu vay ngắn hạn để ứng vốn
lưu động, lãi vay thực tế phải cộng biên tín dụng của DN (không có số; DD phải lấy). Độ tin cậy hướng: trung bình-cao; mức:
trung bình. Không đề xuất ngưỡng escalate mới.

## 2. Pipeline cầu 2026-2028

### 2a. Điện — gói EPC đã TRAO (khối lượng lắp máy 2027-2028 gần như đã "khoá") [DK]
| Dự án | Gói EPC / giá | Nhà thầu (đứng đầu → thành viên) | Mốc | Đọc |
|---|---|---|---|---|
| **LNG Quảng Trạch II** (EVN, 1.612,8 MW, CCGT, tuabin GE Vernova) | EPC TP1 **25.202 tỷ** (639,8 tr USD + 8.341 tỷ); The Investor ghi 962 tr USD | **PowerChina** – tổng công ty lắp máy VN; chỉ 2 hồ sơ (đối thủ: liên danh Gezhouba) | Ký 09/02/2026; khởi công 20/10/2026 (trễ ~1 năm); COD tổ 1/2 = 34/36 tháng từ ngày bắt đầu | Lắp đặt cao điểm 2027-2028 [UĐ] |
| **Ô Môn IV** (PVN, ~1.050-1.155 MW CCGT) | Doosan – PECC2: 560,2 tr USD + 7.660,8 tỷ | **Doosan Enerbility** (Hàn) – PECC2 | Ký 06/06/2025; bắt đầu HĐ dự kiến 01/03/2026; 67 tháng gồm 24 tháng bảo hành | Lắp đặt 2027-2028 |
| **Long Phú 1** (PVN, than) | T08 (thiết bị chính + lắp đặt) | **PTSC – TCC** đánh giá **8.173 tỷ** thắng PETROCONs–CC1–Pacific **11.305 tỷ** (chênh 3.132 tỷ, −28%) | Mở thầu 01/12/2025; 22 tháng, trọn gói; TMĐT 51.130 tỷ; mục tiêu xong 2027 | Gói T24 (484,8 tỷ) **huỷ** 06/2026: 2 hồ sơ cao hơn dự toán **40-42%** + lỗi bảo lãnh dự thầu |
| **Nhơn Trạch 3&4** (LNG) | Gói EPC >24.000 tỷ; tổng thầu lắp máy VN nhận "nhiều hạng mục kỹ thuật phức tạp" | — | COD 05/01/2026 | Đã xong ⇒ **khoảng trống** khối lượng 2026 cho đội lắp máy LNG [UĐ] |
| **Duyên Hải 3 mở rộng** – mái che kho than | **301,83 tỷ** (dự toán 306,07; −1,38%) | Đông Anh Licogi – PECC2; đối thủ duy nhất bị loại vì năng lực | Đóng thầu 13/10/2026; 6 tháng | Gói nhỏ: nhà thầu nội làm đầu ⇒ cạnh tranh mỏng, giảm giá ~1% |
| Hoà Bình mở rộng (480 MW, xong cuối 2025) | xây lắp | Trường Sơn – 47 – một đơn vị lắp máy thành viên | — | Thuỷ điện mở rộng: sân nhà thầu nội |
| Bác Ái tích năng, Trị An MR, Ô Môn I chuyển khí | đang thi công | nhà thầu nội (lắp máy, Trường Sơn, Lũng Lô) | — | Báo Đấu thầu 28/07/2026 |
| Quảng Trạch I (than 2×701,5 MW) | — | — | COD tổ 1 cuối T11, tổ 2 cuối T12/2026 | Kết thúc ⇒ đội lắp máy than được giải phóng |

### 2b. Điện — pipeline CHƯA trao (2028+), cổng hành chính [DK]
- **PDP8 (QĐ 768/QĐ-TTg 15/04/2025):** sau >3 năm, trên công suất nguồn ~5% đã vận hành, ~9% đã khởi công, ~28% có NĐT chưa
  khởi công, **~45% chưa có chủ trương** (Cục Điện lực/BCT 15/09 & 07/10/2026, qua file tư vấn). Thiếu công suất **4.256 MW (2027)
  → 13.964 MW (2030)**; miền Bắc thiếu 5.680 MW 2027 → ~13.026 MW 2030 (Tiền Phong 20/10/2026).
- **Họp TTg 12/10/2026:** giao BCT/BTC rà từng dự án, xác định dự án trễ/không khả thi/thay thế, lập danh mục có tiến độ, chủ đầu tư,
  nguồn vốn — **định hướng điều chỉnh PDP8, chưa phải quyết định** (TCCT 13/10/2026). Tới 18/11 chưa thấy QĐ điều chỉnh mới.
- **LNG:** 18 dự án >20 GW, 16/18 có NĐT, chỉ 2-3 khởi công; BCT đề xuất dời một phần sang 2031-2035. Đã khởi công thêm: Quỳnh Lập
  (hạ tầng 18/05/2026), Hải Phòng LNG 4.800 MW (khởi công, TTg yêu cầu sớm 1 năm — ngày lễ chưa xác minh), Quảng Trạch II.
  Quảng Ninh, Nghi Sơn, Cà Ná (Trung Nam–Sideros River, 57.000 tỷ), Bạc Liêu: còn chuẩn bị đầu tư.
- **Than mới:** BCT đề xuất **+5.300 MW** tới 2030 (Nam Định I, Sông Hậu II, Vĩnh Tân III) — **vướng vốn và thay đổi cơ cấu NĐT**,
  chưa được phê duyệt; PDP8 hiện chỉ giữ 5 dự án đang xây 4.360 MW (Tiền Phong 20/10/2026). Chuyên gia: thiết bị than không phải
  nút thắt, **vốn** mới là nút thắt.
- **Điện gió ngoài khơi:** tới đầu 10/2026 **chưa dự án nào** hoàn tất thủ tục; NQ 20-NQ/TW (28/07/2026) đặt 6-10 GW tới 2030;
  NQ 253/2025/QH15 + NĐ 272/2026 trao TTg chấp thuận chủ trương + NĐT không qua đấu thầu; một NĐT xin rút 14 dự án (VCCI 2026).
  PVN–CIP ký Nam Trung Bộ 1 (1.000 MW) 22/10/2026, "phát triển sớm". ⇒ chế tạo chân đế/jacket cho ĐGNK VN: **không có đơn
  trong nước trước 2028** [UĐ]; chỉ có thể là đơn xuất khẩu.
- **Lưới 500kV:** 9T/2026 toàn EVN khởi công 2 / đóng điện 5 công trình 500kV so với KH 28/22 của EVNNPT (file tư vấn). Các tuyến mới
  (Krông Buk–Tây Ninh 1, Thốt Nốt–Đức Hòa, Bạc Liêu–Thốt Nốt khởi công Q2/2027, Hòa Bình 2–Tây Hà Nội chấp thuận NĐT 17/09/2026)
  đang ở pha tư vấn ⇒ **xây lắp lưới 500kV đợt mới chủ yếu 2027-2029**. Mạch 3 Quảng Trạch–Phố Nối (~1 tỷ USD) nhà thầu nội làm
  ~6 tháng (2024) — tiền lệ "cấp bách" chứng minh năng lực nội ở lưới.
- **Hạt nhân NT1:** pre-FS điều chỉnh, chưa có EPC; thiết kế/thiết bị lò thuộc phía Nga ⇒ phần lắp máy nội (nếu có) sau 2028.
- **Chính sách:** NQ 361/NQ-CP (10/11/2026) sửa Chương trình hành động an ninh năng lượng (NQ 328/2025, thực thi NQ 70-NQ/TW) —
  thêm nhiệm vụ (REC, lưới thông minh EVN 2026-2030, dự trữ chiến lược); chưa thấy điều khoản ưu tiên nhà thầu nội. Luật Điện lực
  sửa đổi trình QH 20/10/2026, chưa thấy thông qua tới 18/11 (F9 file tư vấn). PTT nói NĐ hướng dẫn NQ 253 "không tạo thêm quyền
  ưu tiên vượt Nghị quyết" (TCCT). Dự thảo **Luật Công nghiệp chiến lược** có ưu đãi giá/lãi suất cho sản phẩm nội địa hoá (Báo
  Đấu thầu 28/07/2026) — chưa ban hành.

### 2c. Công nghiệp & hạ tầng [DK]
| Dự án | Quy mô | EPC/nhà thầu | Đọc |
|---|---|---|---|
| **Dung Quất mở rộng** (148k → 171k thùng/ngày) | EPC **988,8 tr USD** vs dự toán 1,208 tỷ (**−18%**) | **China Chengda – Beijing Petrochemical Engineering**; xếp 2: Hyundai E&C – PTSC 1,043 tỷ USD | Ký 09/07/2026, 37 tháng, mục tiêu 2028. Nhà thầu nội chỉ có san lấp (PETROCONS). Lắp máy nội = **thầu phụ** của tổng thầu TQ nếu có [UĐ] |
| Thép Hoà Phát Dung Quất: ray cao tốc + thép đặc biệt | >10.000 tỷ, xong 2027 | chủ đầu tư tự quản [NỀN: thường tự làm tổng thầu, thuê thiết bị ngoại + lắp nội] | NĐ 319 cơ chế đặc thù đường sắt tạo chỗ cho DN nội |
| Hoà Phát Đắk Lắk/Phú Yên (120.000 tỷ), Vinmetal Hà Tĩnh (80.000 tỷ) | rất lớn | chưa rõ | Tiến độ cần kiểm lại; nếu triển khai là nguồn lắp máy luyện kim lớn nhất 2027-2030 [UĐ] |
| Xi măng | VICEM tiêu thụ 6T +13% | — | Ngành dư công suất [NỀN] ⇒ ít dây chuyền mới; việc chủ yếu là cải tạo/xử lý khí thải, lò đốt rác |
| Đường sắt Lào Cai–HN–HP, cao tốc Bắc–Nam | đầu tư công | — | Nguồn kết cấu thép/cầu thép + thiết bị; chủ yếu xây dựng dân dụng, lắp máy thiết bị đến muộn [UĐ] |

**Xuất khẩu kết cấu thép/thiết bị:** không có số ngành. Mỹ áp Section 232 50% thép/nhôm, nhưng một sắc lệnh hạ một số sản phẩm chế
xuất từ thép xuống 15% (WTO Center, ngày chưa xác minh); cảnh báo "thuế chồng thuế" nếu dùng HRC từ nguồn bị AD. ⇒ đơn kết cấu
xuất Mỹ chịu rủi ro thương mại, đơn xuất EU/Úc/Nhật/Trung Đông không có số [UĐ].

## 3. Cấu trúc cạnh tranh, quyền lực khách hàng, kinh tế hợp đồng

### 3a. Phân tầng chuỗi giá trị [UĐ trên DK §2]
| Tầng | Ai thắng | Biên/quyền lực |
|---|---|---|
| Tổng thầu EPC nhà máy lớn (>10.000 tỷ, CCGT/than/lọc dầu) | **Nước ngoài đứng đầu**: PowerChina, Gezhouba, Chengda/BPE (TQ), Doosan, Hyundai (Hàn); PTSC–TCC; nội làm thành viên | Lead hưởng thiết bị + thiết kế (phần biên cao). TQ thắng nhờ thiết bị quy mô lớn, giá thấp, cung nhanh (Báo Đấu thầu 12/02/2026). Chênh giá thắng/thua 18-28% |
| Lắp đặt cơ khí-điện (thành viên liên danh / thầu phụ) | Tổng công ty lắp máy nhà nước + các CTCP thành viên, PVC/PETROCONS, nhà thầu Hàn/TQ mang đội riêng | Price-taker trước lead nước ngoài; biên phụ thuộc đàm phán tỷ lệ phần việc |
| EPC vừa/nhỏ, mở rộng, cải tạo, thuỷ điện MR | Nhà thầu nội làm đầu (Đông Anh Licogi–PECC2, Trường Sơn, Sông Đà, PC1…) | 1-2 hồ sơ, giảm giá ~1-3% ⇒ biên **khá** nhưng quy mô nhỏ |
| Lưới 110-500kV xây lắp | Nhà thầu nội gần như độc quyền (PC1 và các công ty xây lắp điện) [NỀN] | Khách gần như 1 người mua (EVN/EVNNPT); đơn giá theo dự toán NN |
| Chế tạo kết cấu thép/thiết bị | Xưởng nội (nhiều đơn vị thành viên DNNN + tư nhân) vs hàng TQ | Cạnh tranh giá với TQ; điều kiện nội địa hoá (41% chi phí nội ở Long Phú T08 — không đủ hưởng ưu đãi) |

### 3b. Quyền lực khách hàng — rất cao [DK + UĐ]
- Chủ đầu tư lớn đếm trên đầu ngón tay: EVN (+GENCO, Ban QLDA điện 1-3), PVN (+PV Power, BSR, PTSC), vài tập đoàn tư nhân (Hoà Phát,
  Vingroup/VinEnergo), NĐT ngoại LNG. DNNN cổ phần hoá thầu cho DNNN mẹ ⇒ quan hệ cùng hệ sinh thái nhưng **không có quyền định giá**.
- **Dự toán chủ đầu tư thấp hơn giá thị trường**: Long Phú T24 hai hồ sơ cao hơn dự toán 40-42%, gói huỷ (Báo Đấu thầu 05/06/2026);
  nhà thầu xây lắp nói nhiều hạng mục bị tính giá thấp so với thực tế (24/07/2026). Định mức NN mới NĐ 206/2026 + TT 38/2026
  (hiệu lực 01/07/2026) — chưa rõ hướng.
- **Điều khoản thanh toán do chủ đầu tư áp:** ca nhỏ 13/11/2026 (NĐT nhiệt điện Hải Phòng): chủ đầu tư chỉ chấp nhận tạm ứng 10%, phần
  còn lại sau nghiệm thu bàn giao, nhà thầu từ chối ký ⇒ bị đăng vi phạm, cấm chào giá 6 tháng. Từ 01/07/2026, mức tạm ứng/bảo lãnh
  tạm ứng/thu hồi do các bên thoả thuận (NĐ hợp đồng xây dựng mới cho đầu tư công & PPP). Hiệp hội nhà thầu kiến nghị chủ đầu tư phải
  có **bảo lãnh thanh toán** (≥30% cuối) — chưa thành luật.
- Lối thoát về sức mạnh đàm phán: (i) gói nhỏ/cấp bách ít đối thủ; (ii) chỉ định thầu theo cơ chế đặc thù (NQ 253, NĐ 319 đường sắt)
  — nhưng đó là cổng **hành chính**, không phải lợi thế cạnh tranh.

### 3c. Ghi nhận doanh thu POC và vốn lưu động [NỀN — VAS 15, chưa kiểm lại bản văn trong lượt này]
- VAS 15 "Hợp đồng xây dựng": khi kết quả ước tính đáng tin cậy, ghi doanh thu/chi phí theo phần công việc hoàn thành — (a) nếu HĐ
  thanh toán theo **tiến độ kế hoạch**: nhà thầu **tự xác định** phần hoàn thành ⇒ chênh lệch thành "phải thu theo tiến độ kế hoạch
  HĐXD"; (b) nếu thanh toán theo **khối lượng thực hiện**: theo khối lượng được khách hàng xác nhận. Lỗ dự kiến của HĐ phải ghi
  ngay. ⇒ Biên công bố của tổng thầu là **ước tính quản trị**, nhạy với dự toán chi phí còn lại; dự án kéo dài + trọn gói + CPI 5%
  ⇒ rủi ro "biên tốt mấy năm rồi lỗ dồn khi quyết toán" [UĐ].
- Chu trình tiền: tạm ứng (thường 10-15%, phải có bảo lãnh tạm ứng) → thanh toán theo đợt nghiệm thu, giữ lại 5% bảo hành →
  quyết toán nhiều năm sau COD. Nhà thầu phải mở **bảo lãnh dự thầu, thực hiện (thường 2-10%), tạm ứng, bảo hành** ⇒ cần hạn mức
  tín dụng lớn so với vốn chủ [NỀN]. Tiền lệ 2010s: nhiều dự án nhiệt điện tổng thầu nội nhà nước trễ nhiều năm, đội vốn, tranh chấp
  quyết toán (Thái Bình 2, Sông Hậu 1, Vũng Áng 1, Long Phú 1 bị chấm dứt EPC Power Machines–PTSC vì lệnh trừng phạt Mỹ) [NỀN cho
  3 dự án đầu; Long Phú 1 DK Báo Đấu thầu 05/06/2026].
- Hệ quả cho DN lắp máy: **lợi nhuận kế toán ≠ tiền**; WIP + phải thu theo tiến độ + giữ lại bảo hành phình theo backlog; kéo nợ
  vay ngắn hạn ⇒ nhạy với tầng B-C của bảng 5 tầng.

## 4. PHÂN LOẠI
**Kết luận: khối lượng 2027-2028 của tầng lắp máy CHỦ YẾU ĐÃ ĐƯỢC TRAO (đọc được, ít rủi ro hành chính hơn file tư vấn); khối
lượng 2029+ và phần biên cao (đứng đầu EPC) là ADMIN_GATED + cạnh tranh nước ngoài. Biên của nhà thầu nội là MỎNG CẤU TRÚC.
Độ tin cậy: `ambiguous` (~60/40).**

| Tầm | STRUCTURAL | CYCLICAL | ADMIN_GATED | Lý do |
|---|---|---|---|---|
| **12 tháng (tới 11/2027)** | 0,25 | 0,30 | **0,45** | Doanh thu 2027 = các gói đã ký (QT II, Ô Môn IV, Long Phú 1, Dung Quất, lưới đang xây) vào pha lắp đặt cao điểm; rủi ro chính là **nhịp nghiệm thu/giải ngân** của chủ đầu tư NN (EVN giải ngân H1 chỉ 36% KH; đầu tư công 10T 74,1%) và quyết toán. Cyclical: đầu tư công/FDI đang ở đỉnh nhịp tăng, CPI 5% ép HĐ trọn gói |
| **36 tháng (tới 11/2029)** | **0,40** | 0,20 | **0,40** | Structural: thiếu điện đo được ~14 GW 2030, công nghiệp hoá nặng (thép, lọc dầu), đầu tư công trung hạn ×2,7. Admin: 45% công suất PDP8 chưa có chủ trương, LNG/than mới vướng PPA-Qc-vốn, ĐGNK 0 dự án, PDP8 sửa lần nữa chưa ký |
| **Biên lợi nhuận gộp ngành (nhà thầu nội)** | **0,65 "mỏng cấu trúc"** | 0,20 | 0,15 | Lead nước ngoài giữ phần thiết bị/thiết kế; dự toán NN thấp hơn thị trường 40% (Long Phú T24); TQ thắng với chênh 18-28%; quyền lực khách hàng rất cao. Không có cơ chế đẩy biên lên trừ ưu đãi nội địa hoá (chưa ban hành) |

- **Trục 1 (gốc của cầu):** cầu đến từ thiếu hụt điện thật và công nghiệp hoá, có nhiều tầng neo chính sách (QĐ 768, NQ 70 + NQ 361,
  NQ 253 + NĐ 272, NQ 27/2026/QH16) — **không** phải chu kỳ tín dụng nội địa. Nhưng CPI tăng tốc (5,09%, +1,84pp YoY) và GDP ~10%
  cho thấy nền kinh tế đang chạy nóng [UĐ]: nếu NHNN phải siết, kênh truyền vào EPC là **chi phí vốn lưu động + giải ngân chậm**,
  không phải mất pipeline.
- **Trục 2 (ai kiểm soát nhịp):** trong nước (chủ trương, PPA/Qc, GPMB, dự toán, quyết toán) — kiểm soát được về nguyên tắc nhưng lịch
  sử chậm. Ngoại sinh một phần: giá khí/dầu (kinh tế LNG), chi phí vốn quốc tế (US 10Y 5,15%) cho dự án vay ECA, thương mại Mỹ cho
  đơn kết cấu xuất khẩu.
- **Pha [UĐ]:** khối lượng lắp đặt nguồn điện **đáy 2026 → tăng 2027-2028** (khoảng trống sau NT3&4 + QT I; lớp gói mới vào lắp đặt);
  lưới 500kV **đầu nhịp** (xây lắp 2027-2029); công nghiệp nặng **giữa nhịp** (Dung Quất, thép); chi phí đầu vào (CPI, lương) **đang
  tăng**; chi phí vốn **đi ngang ở mức cao**.
- **Đổi phán đoán:** → STRUCTURAL clean (36T) nếu TTg ký điều chỉnh PDP8 kèm danh mục có NĐT/vốn VÀ ≥3 dự án LNG/than mới ký EPC trước
  30/06/2027 VÀ có cơ chế ưu tiên nhà thầu nội (luật CN chiến lược hoặc tương đương). → CYCLICAL/ADMIN nặng hơn nếu EVN lỗ lại (giá
  bán lẻ vừa giảm 2%, CPI cao) ⇒ cắt KH vốn 2027, hoặc NHNN siết tín dụng do lạm phát >6%.

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-11-18; chấm theo nguồn công bố đầu tiên ≤ ngày chấm; Brier ghi dưới mục này)
Mốc gốc: QT II khởi công 20/10/2026; Ô Môn IV bắt đầu HĐ ~01/03/2026; Long Phú 1 mục tiêu 2027; đầu tư công 10T 74,1%; KH 2026
~1,02 triệu tỷ; trung hạn 8,22 triệu tỷ; ĐGNK 0 dự án hoàn tất thủ tục; than mới đề xuất 5.300 MW chưa duyệt.

| # | Mệnh đề (YES/NO) | Ngày chấm | P(YES) |
|---|---|---|---|
| E1 | Bộ TC công bố giải ngân đầu tư công **cả năm KH 2026 ≥ 85%** KH TTg giao (tính tới hết thời hạn giải ngân 31/01/2027) | 2027-02-28 | 0,60 |
| E1b | Như E1 nhưng **≥ 95%** | 2027-02-28 | 0,20 |
| E2 | KH đầu tư công **năm 2027** (NSNN, TTg/QH giao) **> 1,1 triệu tỷ** | 2027-01-31 | 0,80 |
| E3 | ≥1 nhà máy điện **LNG ≥1.000 MW** chưa có HĐ EPC tại 18/11/2026 **ký HĐ EPC** (nhà máy chính) | 2027-06-30 | 0,50 |
| E3b | Như E3 nhưng **≥3 nhà máy** | 2027-06-30 | 0,10 |
| E4 | ≥1 trong Nam Định I / Sông Hậu II / Vĩnh Tân III **ký HĐ EPC** | 2027-12-31 | 0,10 |
| E5 | ≥1 HĐ EPC nhà máy điện/công nghiệp **≥10.000 tỷ** ký trong khoảng 19/11/2026-31/12/2027 có **nhà thầu VN đứng đầu liên danh** | 2027-12-31 | 0,25 |
| E6 | ≥1 HĐ EPC nhà máy điện/công nghiệp ≥10.000 tỷ ký trong cùng khoảng có **nhà thầu TQ đứng đầu** | 2027-12-31 | 0,60 |
| E7 | Long Phú 1: tổ máy đầu tiên **hoà lưới/phát điện lần đầu** | 2027-12-31 | 0,15 |
| E8 | Văn bản quy phạm (luật/NĐ) **bắt buộc chủ đầu tư dự án đầu tư công có bảo lãnh thanh toán** cho nhà thầu được ban hành | 2027-12-31 | 0,10 |
| E9 | **Luật Công nghiệp chiến lược** (hoặc luật có ưu đãi giá cho nhà thầu/sản phẩm cơ khí nội địa hoá) được QH thông qua | 2027-12-31 | 0,45 |
| E10 | CPI YoY **T12/2026 ≥ 5,0%** (NSO, ~06/01/2027) | 2027-01-10 | 0,50 |
| E11 | ≥1 dự án **ĐGNK** ký HĐ EPC/cung cấp chân đế-tuabin | 2028-06-30 | 0,08 |

**Liên kết forecast đã khoá ở file chị em (KHÔNG lặp, chấm ở đó):** PDP8 điều chỉnh lần nữa (tư vấn F7 0,40 tới 2027-06-30); Luật
Điện lực sửa đổi (tư vấn F9 0,80); EVN vốn 2026 ≥123k (tư vấn F1 0,55); than mới ≥1.000 MW vào PDP8 (than F7 0,40 tới 2027-12-31);
LNG ≥5/18 khởi công (tư vấn F6 0,30); Dung Quất mở rộng COD (lọc hoá dầu D11 0,20 tới 2028-12-31).

**Câu phân loại:** P(khối lượng lắp đặt nguồn điện + công nghiệp nặng của tầng nhà thầu nội **năm 2027 > 2026**) ≈ **0,70** —
chấm khi có tổng kết 2027 của EVN/PVN/BSR (số tổ máy, gói đang lắp đặt), không chấm bằng BCTC DN.

## 6. Điều gì làm tôi sai
1. **Đánh giá thấp "cấp bách":** nếu NQ 253/chỉ định thầu được dùng mạnh tay cho than/LNG/lưới, 2027 có thể có làn sóng EPC mới do nhà
   thầu nội đứng đầu ⇒ E5 thấp, biên "mỏng cấu trúc" quá bi quan.
2. **Đánh giá cao phần của nhà thầu nội trong gói lead nước ngoài:** tổng thầu TQ có thể mang đội lắp máy riêng, nhà thầu nội chỉ nhận
   phần dân dụng ⇒ "khối lượng đã khoá" 2027-28 nhỏ hơn tôi nghĩ.
3. **Chu kỳ tài chính:** CPI 5% + GDP ~10% + US 10Y 5,15% ⇒ nếu NHNN siết, giải ngân + vốn lưu động bị bóp đúng lúc khối lượng lên.
4. **Dữ kiện thiếu:** chưa có số giải ngân EVN 9-10T/2026, chưa có hướng định mức mới (TT 38/2026), chưa xác minh ngày khởi công Hải
   Phòng LNG và tiến độ thép Đắk Lắk/Vinmetal; chưa đọc bản văn VAS 15/NĐ hợp đồng xây dựng 2026.
5. **Giá trị HĐ QT II lệch nguồn** (25.202 tỷ vs 962 tr USD) — chỉ quy mô, không ảnh hưởng phân loại.

## 7. DD cần kiểm gì (cho người làm DD một DN EPC/lắp máy — Bobby không làm)
**Backlog & vị trí trong chuỗi**
1. Backlog theo HĐ: tên dự án, chủ đầu tư, giá trị **phần của DN** (không lấy cả gói liên danh), vai trò (đứng đầu / thành viên /
   thầu phụ), loại HĐ (trọn gói / đơn giá cố định / điều chỉnh), tiến độ còn lại. Đối chiếu §2a (QT II, Ô Môn IV, Long Phú 1, Dung
   Quất, lưới 500kV) với muasamcong.
2. Giá trị ký mới 2025, 2026 YTD và tỷ lệ thắng thầu; số gói làm **đứng đầu** vs **thành viên**; tỷ trọng doanh thu từ
   EVN/PVN/tư nhân/xuất khẩu.
3. Điều khoản trượt giá (CPI, thép, lương) và đồng tiền thanh toán (USD/VND); ai chịu rủi ro tỷ giá với HĐ hỗn hợp tiền tệ.

**Ghi nhận & chất lượng lợi nhuận (VAS 15)**
4. Phương pháp ghi nhận (theo tiến độ kế hoạch hay khối lượng được xác nhận); **"phải thu theo tiến độ kế hoạch HĐXD"**, chi phí SXKD
   dở dang (WIP) theo **từng dự án**, tuổi WIP; dự án đã COD nhiều năm mà chưa quyết toán (tiền lệ nhiệt điện 2010s).
5. Dự phòng lỗ HĐ và lịch sử điều chỉnh ước tính (lãi năm trước bị đảo năm sau?); tỷ trọng doanh thu Q4; độ lệch lợi nhuận – CFO 3-5 năm.
6. **Ý kiến kiểm toán** (ngoại trừ / nhấn mạnh về WIP, phải thu, khả năng hoạt động liên tục, hợp nhất công ty con).

**Vốn lưu động, bảo lãnh, nợ**
7. Phải thu khách hàng + tuổi nợ (>1 năm, >3 năm), dự phòng; tiền giữ lại bảo hành; tạm ứng nhận từ khách (người mua trả trước) vs
   tạm ứng cho thầu phụ.
8. **Hạn mức bảo lãnh** đang dùng / tổng hạn mức (dự thầu, thực hiện, tạm ứng, bảo hành) so với vốn chủ; phí bảo lãnh; tài sản
   đảm bảo; có bảo lãnh chéo cho công ty con/liên kết không.
9. Nợ vay ngắn hạn, lãi vay thực tế/năm (so tầng B-C bảng 5 tầng: 7,4-9%), khả năng trả lãi; vi phạm covenant.

**Cấu trúc & quản trị**
10. Sở hữu NN (cơ quan đại diện, kế hoạch thoái vốn); cấu trúc mẹ–con (nhiều CTCP lắp máy thành viên niêm yết riêng?) ⇒ lợi ích
    thiểu số, giao dịch nội bộ, chuyển giá giữa mẹ và con.
11. Tài sản ngoài lõi (đất, BĐS, đầu tư tài chính) — thường là nguồn giá trị ẩn hoặc lỗ ẩn của DNNN cổ phần hoá [NỀN].
12. Tranh chấp/trọng tài với chủ đầu tư; phạt chậm tiến độ; HĐ bị chấm dứt; liên quan vụ án (theo luật fleet: chỉ **WARNING**).

**Năng lực & chi phí**
13. Số thợ hàn/kỹ sư, chi phí nhân công/doanh thu, lương bình quân (lương cả nước +10% YoY theo snapshot); công suất và tỷ lệ sử dụng
    xưởng chế tạo; đơn xuất khẩu kết cấu (thị trường, rủi ro AD/232 Mỹ).
14. Biên gộp theo mảng (lắp máy / chế tạo / EPC / khác) và theo vai trò (đứng đầu vs thầu phụ).
15. Hỏi trực tiếp: định mức mới (NĐ 206/2026, TT 38/2026) áp cho HĐ ký sau 01/07/2026 làm đơn giá tăng hay giảm.

**Mốc kiểm:** QĐ điều chỉnh PDP8; KH đầu tư công 2027 (E2) và quyết toán giải ngân 2026 (E1); tổng kết năm EVN/PVN (~01/2027);
ký EPC LNG/than mới (E3-E6); tiến độ lắp đặt QT II/Ô Môn IV/Long Phú 1.

**Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- Snapshot vĩ mô: `mike/agents/Taylor/research/dd_LLM_20261118/macro_snapshot_20261118.md` (TradingEconomics qua `tav2_bq.macro_indicator`, UNVERIFIED); PIT `deposit_rate_vn` / `cctg_rate_vn` chạy 18/11/2026 (effective 7,4% = CCTG 12M 02/11; kill-switch A CLEAR).
- QT II EPC: Báo Đấu thầu (ký 09/02/2026): https://baodauthau.vn/ky-ket-hop-dong-epc-hon-25000-ty-dong-du-an-nha-may-nhiet-dien-lng-quang-trach-ii-post193854.html ; VnEconomy: https://vneconomy.vn/ky-hop-dong-epc-tri-gia-25202-ty-dong-cho-nhiet-dien-lng-quang-trach-ii.htm ; The Investor: https://theinvestor.vn/evn-powerchina-sign-962-mln-epc-contract-for-central-vietnam-lng-power-plant-d18359.html ; VietnamFinance (GE Vernova, đối thủ Gezhouba): https://vietnamfinance.vn/lien-danh-powerchina-lilama-trung-thau-xay-nha-may-dien-khi-ty-usd-o-quang-tri-d140054.html ; khởi công 20/10/2026: https://tapchicongthuong.vn/khoi-cong-nha-may-nhiet-dien-lng-quang-trach-ii-559538.htm
- Ô Môn IV: Báo Đấu thầu: https://baodauthau.vn/lien-danh-doosan-pecc2-trung-goi-thau-epc-nha-may-nhiet-dien-o-mon-iv-post179863.html ; The Investor (ký 06/2025): https://theinvestor.vn/epc-contract-signed-for-o-mon-iv-thermal-power-project-in-southern-vietnam-d15929.html ; CafeF (bắt đầu 01/03/2026, chỉ dùng mốc): https://cafef.vn/tv2-trung-goi-thau-hon-22000-ty-dong-tai-du-an-nha-may-nhiet-dien-o-mon-iv-188250608072515951.chn
- Long Phú 1 T08, Báo Đấu thầu 12/02/2026: https://baodauthau.vn/du-an-nha-may-nhiet-dien-long-phu-1-cuoc-dua-gia-3100-ty-dong-va-bai-toan-epc-quoc-te-post194026.html ; T24, 05/06/2026: https://baodauthau.vn/goi-thau-484-ty-dong-thuoc-du-an-nha-may-nhiet-dien-long-phu-1-gap-ghenh-duong-ve-dich-post200152.html
- Duyên Hải 3 MR, Báo Đấu thầu 09/11/2026: https://baodauthau.vn/goi-thau-epc-301-ty-dong-tai-nhiet-dien-duyen-hai-3-mo-rong-vi-sao-dong-anh-licogi-pecc2-duoc-chon-post212124.html
- "Nhà thầu Việt nâng vị thế tại các công trình điện trọng điểm", Báo Đấu thầu 28/07/2026: https://baodauthau.vn/nha-thau-viet-nang-vi-the-tai-cac-cong-trinh-dien-trong-diem-post203670.html
- Dung Quất EPC: Báo Đấu thầu 19/03/2026: https://baodauthau.vn/du-an-nang-cap-mo-rong-nha-may-loc-dau-dung-quat-cuoc-dua-chon-nha-thau-thuc-hien-goi-thau-epc-ty-usd-post195570.html ; kết quả: https://baodauthau.vn/du-an-mo-rong-nha-may-loc-dau-dung-quat-buoc-tien-tai-goi-thau-epc-post202511.html ; Báo Đầu tư: https://baodautu.vn/lien-danh-chengda---bpe-la-nha-thau-epc-du-an-mo-rong-loc-dau-dung-quat-d639550.html ; TBTCVN: https://thoibaotaichinhvietnam.vn/ky-hop-dong-goi-thau-hon-988-trieu-usd-nang-cap-mo-rong-loc-dau-dung-quat-200451.html
- Họp TTg 12/10/2026 về PDP8, TCCT 13/10/2026: https://tapchicongthuong.vn/thu-tuong-yeu-cau-ra-soat-tien-do-cac-du-an-trong-quy-hoach-dien-viii--bao-dam-cung-ung-dien-den-nam-2030-557530.htm
- Than mới 5.300 MW, Tiền Phong 20/10/2026: https://tienphong.vn/truoc-nguy-co-thieu-dien-bo-sung-dien-than-co-kha-thi-post1886782.tpo ; https://tienphong.vn/lo-thieu-nguon-bo-cong-thuong-xoay-sang-dien-mai-nha-dien-than-post1876830.tpo
- LNG: Quỳnh Lập (Vietstock 05/2026): https://en.vietstock.vn/2026/05/nghe-an-launches-infrastructure-works-for-22-billion-lng-power-plant-974-633548.htm ; Cà Ná: https://vietnamfinance.vn/lo-dien-lien-danh-trung-thau-du-an-dien-khi-lng-ca-na-57000-ty-d139475.html ; Hải Phòng LNG (VCCI): https://vcci.com.vn/en/news/tin-hieu-moi-cho-dien-khi-lng ; Vingroup LNG: https://lngprime.com/lng-terminals/vietnams-vingroup-kicks-off-work-on-lng-power-plant/164546/
- ĐGNK: VCCI (14 dự án xin rút): https://vcci.com.vn/tin-tuc/nha-dau-tu-muon-lam-14-du-an-dien-gio-ngoai-khoi-ca-trieu-ty-dong-lai-de-xuat-rut-lui ; Báo Pháp luật (thẩm quyền TTg): https://doanhnhan.baophapluat.vn/trao-tham-quyen-chap-thuan-chu-truong-dau-tu-mo-duong-cho-phat-trien-dien-gio-ngoai-khoi-89676.html
- NQ 361/NQ-CP 10/11/2026: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/11/361_nq-cp_10112026_3-signed.signed.pdf ; Báo Đấu thầu: https://baodauthau.vn/sua-doi-chuong-trinh-hanh-dong-bao-dam-an-ninh-nang-luong-quoc-gia-post212380.html
- NĐ hướng dẫn NQ 253 (PTT: không tạo thêm ưu tiên), TCCT: https://tapchicongthuong.vn/khan-truong-hoan-thien-nghi-dinh-trien-khai-co-che-dac-thu-ve-phat-trien-nang-luong-giai-doan-2026-2030-519271.htm
- Luật Điện lực sửa đổi (UBTVQH 21/09, trình 20/10/2026): https://tapchicongthuong.vn/uy-ban-thuong-vu-quoc-hoi-cho-y-kien-ve-du-an-luat-sua-doi--bo-sung-mot-so-dieu-cua-luat-dien-luc-551777.htm ; https://moit.gov.vn/chuyen-muc/bo-cong-thuong-voi-quoc-hoi-va-cu-tri
- Đầu tư công: VietnamPlus (10T 74,1%): https://www.vietnamplus.vn/10-thang-giai-ngan-von-dau-tu-cong-cua-ca-nuoc-dat-741-ke-hoach-post1146172.vnp ; NQ 27/2026/QH16 (Cần Thơ PBGDPL): https://pbgdpl.cantho.gov.vn/nghi-quyet-cua-quoc-hoi-ve-ke-hoach-dau-tu-cong-trung-han-giai-doan-2026-2030 ; TBTCVN: https://thoibaotaichinhvietnam.vn/dau-tu-cong-5-nam-toi-von-tang-27-lan-du-an-giam-30-196332.html
- Lưới 500kV: Hòa Bình 2–Tây HN (TCCT): https://tapchicongthuong.vn/du-an-duong-day-500kv-tram-cat-hoa-binh-2-tay-ha-noi-evnnpt-duoc-chap-thuan-la-nha-dau-tu-550825.htm ; còn lại xem `sector_read_power_consulting_20261028.md`.
- Thép/công nghiệp: Hoà Phát ray (Đại biểu Nhân dân): https://daibieunhandan.vn/quang-ngai-khoi-cong-nha-may-san-xuat-ray-cao-toc-va-thep-dac-biet-hon-10-000-ty-dong-10401124.html ; Vinmetal: https://vietnamfinance.vn/vingroup-khoi-dong-nha-may-san-xuat-thep-vinmetal-ha-tinh-80000-ty-d137541.html ; Hoà Phát Đắk Lắk: https://www.vcci.com.vn/tin-tuc/hoa-phat-dau-tu-120000-ty-dong-xay-khu-lien-hop-san-xuat-thep-tai-dak-lak
- Thương mại thép Mỹ (WTO Center): https://trungtamwto.vn/tin-tuc/32604-xuat-khau-thep-cua-eu-giam-34-vi-thue-quan-my ; https://vneconomy.vn/doanh-nghiep-xuat-khau-thep-nhom-viet-nam-doi-mat-voi-nguy-co-thue-chong-thue.htm
- Thanh toán/tạm ứng: Báo Đấu thầu 13/11/2026: https://baodauthau.vn/chu-dau-tu-can-xem-xet-thau-dao-truoc-khi-ap-dung-che-tai-voi-nha-thau-post212701.html ; TBTCVN dòng tiền cuối năm: https://thoibaotaichinhvietnam.vn/doanh-nghiep-xay-dung-can-doi-dong-tien-cuoi-nam-204989-204989.html ; NĐ hợp đồng xây dựng (Hải Phòng, 07/2026): https://cdn.haiphong.gov.vn/gov-hpg/6866/tintuc/2026/7/ndhopdong_xaydung.docx639189457498894749.pdf
- Bảng 5 tầng: `sector_read_ngan_hang_quoc_doanh_20261117.md` §1b; `sector_read_phat_dien_20261118.md` §1b.
