---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-12. KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp thuỷ điện cụ thể.
blind: YES
as_of: 2026-11-12
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành sản xuất & kinh doanh điện, thuỷ điện vừa và nhỏ (nhà máy khoảng 30-100 MW, miền Bắc / Bắc Trung Bộ, bán cho EVN qua PPA + thị trường phát điện cạnh tranh, một số nhà máy kiêm điều tiết nước/chống lũ). Gồm phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED theo 2 tầm, pipeline cầu, cơ chế giá/người mua duy nhất, đọc snapshot vĩ mô, FORECAST khoá trước có ngày chấm, checklist DD.
---

# SECTOR READ: Thuỷ điện vừa và nhỏ miền Bắc / Bắc Trung Bộ, as-of 12/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn + ngày.
**[UĐ]** là ước đoán hoặc suy luận của Bobby. **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này, phải KIỂM trước khi dùng làm số.
File chị em để đối chiếu: `sector_read_than_20261111.md` (cơ cấu nguồn 10T, El Niño, than cho điện),
`sector_read_khi_dot_lpg_20261109.md` (giá điện bán lẻ −2%, NĐ 100/2025, Qc khí, tài chính EVN),
`sector_read_power_consulting_20261028.md` (PDP8, lưới 500kV, thiếu công suất 2027-2030).

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Snapshot vĩ mô:** file caller chỉ định `agents/Taylor/research/dd_VCP_20261112/macro_snapshot_20261112.md` **KHÔNG TỒN TẠI**
  lúc đọc (12/11). Tôi tự sinh lại bằng đúng script chuẩn `mike/bin/macro_snapshot_asof.py --asof 2026-11-12` (chế độ "live",
  đọc `tav2_bq.macro_indicator`, không chứa forward return), ghi ra `/tmp/bobby_hydro/macro_snapshot_20261112.md`. Tôi không
  ghi vào thư mục của Taylor. Trong thư mục dispatch tôi chỉ liệt kê tên file (thấy tên file BCTC trong `src/`), **không mở file
  nào** và không tra nghĩa chuỗi ký tự trong tên thư mục.
- **Repo:** 3 file chị em ở trên (chỉ grep đoạn về thuỷ điện, PDP8, giá điện). Chuỗi lãi suất PIT gồm `deposit_rate_vn.py`
  (Big-4 12M) và `cctg_rate_vn.py` (CCTG 12M), đọc qua `effective_deposit_rate('2026-11-12')`.
- **Không có trong BQ/snapshot/web lượt này (ghi "không có số", không suy):** sản lượng thuỷ điện theo vùng; mực nước và dung tích
  hồ miền Bắc/Bắc Trung Bộ đầu T11/2026 so với kế hoạch tích nước; FMP/SMP bình quân tháng 9-10/2026 từ NSMO; tỷ lệ Qc thuỷ điện
  2026 (văn bản gốc QĐ 3746); thuế suất tài nguyên nước hiện hành cho thuỷ điện; mức thu tiền cấp quyền (M%) hiện hành.
- **Rò rỉ không chủ ý (ghi trung thực, KHÔNG dùng cho phân loại, forecast hay bảng số):** tóm tắt tìm kiếm có nêu KQKD Q3/2026 của
  2-3 doanh nghiệp thuỷ điện niêm yết (miền Trung, Tây Nguyên), sản lượng 9T của một tổng công ty phát điện thuộc EVN, và tên 6 hồ
  (miền Trung/Nam) đang cao hơn mực nước kế hoạch ngày 14/10. Tôi bỏ hẳn phần doanh nghiệp. Phần hồ chỉ dùng ở mức định tính, và
  các hồ đó không thuộc vùng được hỏi. Trong một prompt WebFetch (trả 404, không có dữ liệu) tôi có liệt kê tên một số hồ ở Thanh
  Hoá/Nghệ An làm ví dụ vùng. Đó là kiến thức địa lý chung, không phải nhận diện doanh nghiệp.

## 1. Snapshot vĩ mô: chỉ báo hợp với ngành này
Bảng ánh xạ ngành ở cuối snapshot **không có dòng "Điện"**. Tôi tự chọn các chỉ báo kéo cầu điện và chi phí vốn:

| Chỉ báo (snapshot, TE UNVERIFIED) | Giá trị | Δ3T / Δ12T | Đọc cho thuỷ điện |
|---|---|---|---|
| Sản xuất CN YoY | 15,0% (T10) | +0,5 / +4,6pp | Phụ tải công nghiệp mạnh, cùng hướng với sản lượng điện T10 +14,3% |
| GDP YoY | 9,95% (Q3) | +1,14 / +1,70pp | Nền cầu điện tăng khoảng 10%/năm |
| PMI SX | 52,3 (T10) | −0,6 / −2,2 | Còn mở rộng, đà chậm lại nhẹ |
| CPI YoY | 5,09% (T10) | +0,64 / +1,84pp | Lạm phát tăng. Đây là lực cản chính trị lên giá điện bán lẻ (đọc cùng việc EVN giảm giá 2% từ 01/11) |
| Tái cấp vốn SBV | 4,50% | 0 / 0 | Lãi điều hành không đổi |
| LNH 3M | 6,39% (09/11) | **−1,36pp** / −0,12pp | Thanh khoản liên ngân hàng dịu đi sau đỉnh khoảng 7,75% 3 tháng trước |
| USD/VND | 25.654 | −1,54% / −2,66% | VND lên giá. Có lợi cho nhà máy còn nợ vay ngoại tệ |
| TPCP 10Y (chỉ tin Δ) | 4,57 | +0,03 / +0,58pp | Lãi suất dài hạn nhích lên trong 12T |
| US 10Y | 4,99% | +0,29 / +0,92pp | Bối cảnh lãi suất toàn cầu cao, ảnh hưởng gián tiếp |

### 1b. Chi phí vốn: bảng 5 tầng (ngành vay dài hạn, thả nổi theo lãi huy động cộng biên [NỀN])
| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (09/11, đi ngang từ 03/10) | Tách online/quầy lượt này: **không có số** (series lưu MAX) |
| A. | Big-4 6M | không có số | |
| B. Bán hành chính | CCTG 12M Big-4 (cao nhất) | **7,4%** (02/11; 7,5% ngày 30/09 là 6M, đã rebase) | Spread CCTG − tiết kiệm 12M = **+0,6pp**. Từng NH và sự kiện mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi "ẩn", số NH ≥7% | không có số | |
| D. Thị trường | LNH 3M | 6,39% (−1,36pp/3T) | OMO/tín phiếu, tỷ lệ trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y | 4,57 (chỉ tin Δ) | |
| E. Lượng | Tín dụng vs huy động YTD, LDR | không có số | |

**Đồng thuận/phân kỳ [UĐ]:** về HƯỚNG, A và B đi ngang, D giảm, nên không proxy nào báo chi phí vốn đang tăng. Về MỨC, chi phí
biên (CCTG 7,4%) cao hơn số niêm yết khoảng 0,6pp. Lãi vay dự án thả nổi của nhà máy thuỷ điện nhiều khả năng neo theo lãi huy động
12M cộng biên khoảng 3-4pp [NỀN]. **Không có tín hiệu chi phí vay sẽ tăng mạnh trong 3-6T tới.** Kill-switch A (>7,5%) đang CLEAR.
Độ tin cậy trung bình, vì thiếu tầng C và E.

## 2. Pipeline cầu
### 2a. Phụ tải: STRUCTURAL, mạnh
- Sản lượng hệ thống **10T/2026: 297,4 tỷ kWh, +9,8%; riêng T10: 31,58 tỷ kWh, +14,3%. NSMO dự báo T11: 28,9 tỷ kWh, +14,4%**
  [DK, EVN qua giaoduc.net.vn và Nhân Dân, 03/11/2026].
- Pmax EVNNPC (miền Bắc) H1/2026 khoảng **+16,9%** YoY. Gần 400 thuỷ điện nhỏ đấu lưới phân phối miền Bắc bổ sung khoảng 1.800-1.900 MW
  lúc phụ tải cao [DK, VOH, 2026]. Theo một báo cáo môi giới, cơ quan quản lý dự báo **thiếu khoảng 4.256 MW công suất toàn quốc
  năm 2027** [DK cấp 2, tóm tắt tìm kiếm, chưa đọc văn bản gốc].
- ⇒ [UĐ] Miền Bắc là vùng **thiếu nguồn**, nên mọi kWh thuỷ điện miền Bắc đều được huy động. Rủi ro cầu đối với nhà máy loại này
  gần bằng 0. Biến số thật là **lượng nước** và **đơn giá**.

### 2b. Cơ cấu nguồn và tỷ trọng thuỷ điện: CYCLICAL theo thuỷ văn, đang đi vào đáy
- Cơ cấu 10T/2026: thuỷ điện **73,39 tỷ kWh = 24,7%**, than 147,78 (49,7%), khí 23,28 (7,8%), tái tạo 40,72 (13,7%; mặt trời 24,04,
  gió 15,37), nhập khẩu 11,77 (4%) [DK, EVN 03/11/2026].
- So với 10T/2025: thuỷ điện chiếm khoảng 32,6% (khoảng 88 tỷ kWh, tự tính) ⇒ **thuỷ điện khoảng −16% YoY** [UĐ, tự tính. Nền 2025 là
  năm La Niña mưa nhiều bất thường: EVN tự nhận "mưa dồi dào cả nước", CGM 2025 bình quân 1.283,4 đ/kWh, −8,7% (ASEANSC, 12/2025)].
- **Q1/2026 thuỷ điện vẫn +7,8%** (14,9 tỷ kWh, La Niña còn) [DK, VnEconomy 19/04/2026]. 10T lại −16%, nên giai đoạn T4-T10 (gồm
  mùa lũ chính miền Bắc) giảm mạnh hơn nhiều, ước khoảng −20% hoặc tệ hơn [UĐ].
- **El Niño 2026-2027:** đã hình thành, xác suất >95% kéo dài sang 2027 (Cục KTTV, 23/07/2026). Xác suất đạt mức rất mạnh, cực đại
  T11/2026-T1/2027, là **60-65%** (cập nhật T9-T10). Có 2 kịch bản:
  - Kịch bản (1): trung bình đến mạnh, suy yếu từ đầu 2027.
  - Kịch bản (2): rất mạnh, kéo dài tới giữa 2027. Lượng mưa mùa mưa thiếu 20-40%, dòng chảy giảm 20-40%. **Dòng về các hồ lớn hệ thống
    sông Đà có thể giảm mạnh vào T5-T6/2027.** Mùa mưa 2027 có thể đến muộn. Riêng một số hồ vừa và nhỏ có thể xuống dưới mực nước
    thiết kế ngay trong kịch bản (1).

  Thống kê lịch sử: trong các năm El Niño, **100% hồ thuỷ điện không tích đủ nước**, thiếu 7,73-11 tỷ m³ (43 hồ lớn) [DK, VnEconomy
  23/07/2026; Cục QL TN nước qua MAE/Nhân Dân T9-T10/2026].
- **Sắc thái vùng [UĐ + NỀN]:** El Niño tác động mạnh và nhất quán nhất ở Nam Trung Bộ, Tây Nguyên và Nam Bộ. Ở Bắc Bộ và Bắc Trung Bộ
  tác động yếu và ít nhất quán hơn. Tháng 8/2026 miền Bắc có đợt mưa lớn diện rộng: 17-21/8 mưa 150-300 mm ở Bắc Bộ và từ Thanh Hoá
  tới Bắc Quảng Trị, có lũ khẩn cấp ở sông Thanh Hoá/Nghệ An, và mưa lớn Thanh Hoá-Nghệ An ngày 10-15/9 [DK, KTTV/MAE, T8-T9/2026].
  ⇒ Mùa lũ miền Bắc 2026 **không khô đều**. Có thể nhà máy Bắc Trung Bộ đã có các đợt nước tốt trong T8-T9 dù toàn quốc thuỷ điện giảm.
  **Mực nước cuối mùa lũ của hồ miền Bắc/Bắc Trung Bộ: không có số.** EVN chỉ đạo hồ "tích về mực nước dâng bình thường trước
  31/12" (15/10 và 03/11/2026). Đó là mục tiêu, không phải kết quả.
- **Mùa vụ Bắc Trung Bộ [NỀN]:** mùa lũ khoảng T8/T9-T11, muộn hơn Bắc Bộ (T6-T10). Vì vậy đỉnh El Niño (T11-T1) **trùng đúng giai
  đoạn tích nước cuối mùa** của nhà máy Thanh Hoá/Nghệ An. Đây là cửa sổ rủi ro lớn nhất cho sản lượng mùa khô 2027 của nhóm này.

### 2c. Nguồn cạnh tranh trong điều độ: rủi ro thấp
Nguồn cạnh tranh gồm nhập khẩu từ Lào/TQ (4%), mặt trời mái nhà, BESS (EVNNPC đặt mục tiêu 805 MW), Quảng Trạch I than 1.403 MW
(COD 2026), và tái tạo chủ yếu ở miền Trung/Nam. Trong bối cảnh miền Bắc thiếu nguồn, thuỷ điện có chi phí biên thấp nhất nên
**được ưu tiên điều độ**. Rủi ro bị nguồn khác đẩy ra khỏi điều độ: thấp [UĐ].

### 2d. Truyền tải và cắt giảm: thấp ở cấp hệ thống, cục bộ chưa rõ
Lượt này không tìm thấy tin cắt giảm thuỷ điện nhỏ/vừa miền Bắc do quá tải lưới 110-220kV năm 2026 (tìm 1 lần, kết quả âm tính
không có nghĩa là chắc chắn không có). Nghẽn lưới cục bộ vùng núi Tây Bắc mùa lũ có tiền lệ [NỀN]. Với nhà máy 30-100 MW đấu lưới
110/220kV: DD phải kiểm số giờ bị giới hạn công suất.

## 3. Cấu trúc cạnh tranh, cơ chế giá và người mua duy nhất
- **Cơ chế bán điện [DK + NỀN]:** nhà máy **>30 MW phải tham gia trực tiếp** thị trường điện (Thông tư 29/2026/TT-BCT về thị trường
  bán buôn điện cạnh tranh). Doanh thu theo cấu trúc CfD [NỀN, PHẢI KIỂM]: `Qc×Pc + (Qm−Qc)×FMP`, trong đó FMP = SMP + CAN.
  ⇒ **Năm khô: Qm < Qc trong khi FMP cao, nên nhà máy "thiếu hàng" và phải bù chênh lệch theo giá thị trường đắt.** Đây là bất đối
  xứng xấu cho thuỷ điện năm El Niño, trừ khi Qc tháng được NSMO phân bổ lại theo thuỷ văn [NỀN, phải kiểm].
  Theo Thông tư 29/2026, tỷ lệ Qc nằm trong khung 60-100% [DK cấp 2]. Có một nguồn nói Qc thuỷ điện 2026 là 98% (QĐ 3746/QĐ-BCT,
  26/12/2025). **Nguồn này chưa xác thực**, các tóm tắt khác bị cắt trước con số.
- **Khung giá PPA thuỷ điện 2026: 0-1.110 đ/kWh**, **không đổi so với 2024** (QĐ 1127/QĐ-BCT, 14/05/2026). Khung **chưa gồm** thuế
  tài nguyên nước, tiền DVMTR, tiền cấp quyền khai thác tài nguyên nước và VAT, tức các khoản này được tính riêng [DK]. Khung giá
  đóng băng 3 năm trong khi CPI tăng 5%: giá PPA thực giảm dần [UĐ].
- **Thị trường giao ngay:** trần SMP 2026 là **1.725 đ/kWh (+3%)**. CAN 2026 khoảng **130 đ/kWh** (gấp khoảng 2,7 lần, QĐ 3746 qua
  Vietcap 01/2026). VnEconomy (19/04/2026) lại cho **CAN bình quân Q1/2026 = 160 đ/kWh**. Hai nguồn **lệch nhau**, có thể do khác
  định nghĩa (CAN công bố hay CAN bình quân thực trả). FMP bình quân Q1/2026 là **1.255 đ/kWh (−2%)** [DK]. Một tóm tắt nói **8T/2026
  khoảng 1.430 đ/kWh, +37%**, nguồn là báo cáo môi giới chưa đọc được nên chỉ coi là [DK cấp 2]. Tháng 7-8 có nguồn nói "chỉ khoảng
  1.200" (không rõ đơn vị). **FMP T9-T10: không có số.**
  ⇒ [UĐ] Chiều giá giao ngay là **lên** (thuỷ điện giá rẻ thiếu, than và khí phải lên biên). Phần giá lên này là cái bù một phần cho
  khối lượng giảm, nhưng chỉ cho phần sản lượng nằm ngoài Qc.
- **Người mua duy nhất (EVN/EPTC) và rủi ro thanh toán:**
  - Năm 2025 LNST hợp nhất khoảng **51.881 tỷ**, đã hết lỗ luỹ kế hợp nhất. Công ty mẹ còn lỗ luỹ kế khoảng **5,6 nghìn tỷ**. Tiền gửi
    khoảng 152 nghìn tỷ. Nợ ngắn hạn >227 nghìn tỷ. Phải trả nhà máy ngoài EVN và nhiên liệu >118 nghìn tỷ [DK, báo chí T6/2026].
  - Lãi 2025 đến từ thuỷ điện rẻ (giảm chi phí mua điện ước 16-18 nghìn tỷ) và từ việc giá bán lẻ tăng khoảng 17% giai đoạn 2023-25.
  - Năm 2026 điều ngược lại xảy ra: thuỷ điện −16%, than +19%, giá nhiên liệu cao, mà **giá bán lẻ lại giảm 2% từ 01/11/2026**
    (QĐ 1305/QĐ-EVN).
  - ⇒ [UĐ] Biên của EVN bị ép trong 2026-27. Rủi ro **chậm thanh toán** tăng từ thấp lên **thấp-vừa** trong 2027, nhưng vẫn thấp hơn
    2023-24 nhờ đệm tiền mặt.
  - **Tập trung khách hàng = 100% vào một người mua.** Cải cách (TT 29/2026; Luật Điện lực sửa đổi, dự thảo 09/02/2026; đề xuất tách
    EVNNPT; người dùng chọn đơn vị cấp điện từ 2027) **chỉ đa dạng hoá người mua một cách chậm**, tầm >3 năm [UĐ].
- **Rủi ro tái đàm phán / hết PPA (ADMIN, nặng nhất cho nhà máy cũ):** thuỷ điện nhỏ hết hạn biểu giá chi phí tránh được. Bên mua đề
  xuất **giá tạm khoảng 1/4 giá cũ (khoảng 250 đ/kWh)**, quyết toán sau. Một số nhà máy **dừng phát hơn 2 tháng đến hơn 1 năm**, xả
  tràn bỏ nước. Cục Điện lực xác nhận Thông tư 12/2025/TT-BCT là phương pháp chung, nhưng **giá giai đoạn sau phải theo chi phí từng
  nhà máy**, nên đang nghiên cứu phương pháp mới [DK, Tiền Phong 30/10/2026].
  - Ca này là nhà máy <30 MW, không đúng nhóm đang đọc. Nhưng **cùng logic áp cho nhà máy 30-100 MW** [NỀN, PHẢI KIỂM]: sau khi trả hết
    nợ hoặc hết khấu hao, thành phần giá cố định (khấu hao + lãi vay) trong Pc bị đàm phán giảm. Khi PPA hết hạn, giá mới phụ thuộc hồ
    sơ chi phí và thời gian thẩm định có thể kéo dài nhiều tháng.
- **Thuế, phí, quyền:**
  - DVMTR **36 đ/kWh** điện thương phẩm (NĐ 156/2018 Đ59). Không thấy văn bản đổi mức này trong 2025-26 (tìm 1 lần).
  - NĐ 180/2026 (hiệu lực 15/07/2026) về dịch vụ hấp thụ/lưu giữ carbon rừng. Chưa rõ có áp cho thuỷ điện hay không, phải kiểm.
  - **Tiền cấp quyền khai thác TN nước** tính theo T = W × G × M. Ví dụ 2026 ở Tuyên Quang dùng G = 70% × 2.204,0655 đ/kWh =
    1.542,85 đ/kWh [DK, quyết định tỉnh Tuyên Quang 2026]. ⇒ G gắn với giá bán lẻ bình quân, nên giá bán lẻ giảm 2% làm G giảm nhẹ
    [UĐ]. Mức M% hiện hành và văn bản thay NĐ 82/2017 (nghị định hiệu lực 01/07/2024): [NỀN, PHẢI KIỂM].
  - Thuế tài nguyên nước thuỷ điện (thuế suất và giá tính thuế): [NỀN, chưa kiểm].
  - **Điểm mấu chốt:** những khoản này **có được EVN hoàn trả ngoài Pc hay không**. Khung giá loại trừ chúng, nhưng thực thi trong PPA
    từng nhà máy có tranh chấp lịch sử về tiền cấp quyền [NỀN].
- **Đa mục tiêu / chống lũ [NỀN]:** quy trình vận hành liên hồ hoặc đơn hồ bắt hạ mực nước đón lũ trong mùa lũ (mất cột nước và sản
  lượng), bắt xả đổ ải/duy trì dòng hạ du mùa khô bất kể giá, và có rủi ro pháp lý/uy tín khi xả lũ. Một số công trình có phần vốn thuỷ
  lợi nhà nước, nên có câu hỏi về chia sẻ chi phí O&M và nghĩa vụ cấp nước.
- **Thời hạn quyền:** giấy phép khai thác TN nước có thời hạn, gia hạn theo Luật TN nước 2023. Đất có thể thuê hằng năm hay một lần.
  Nhà máy theo BOT phải chuyển giao khi hết hạn [NỀN]. Không có số chung cho ngành.

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1, nguyên nhân gốc của bối cảnh hiện tại:** sản lượng thuỷ điện 2026 giảm và giá thị trường tăng. Nguyên nhân là **thời tiết
ngoại sinh (La Niña 2025 chuyển sang El Niño 2026-27) cộng hiệu ứng nền năm 2025 mưa kỷ lục**, cộng cú sốc giá năng lượng
(Hormuz, xem file khí). Đây **không phải** mất cân đối vĩ mô trong nước. Cầu điện +10% là nền cấu trúc.

**Trục 2, có tự giới hạn không:** có, nhưng theo **lịch của tự nhiên**, không theo một hành động chính sách nào. Kịch bản (1): đáy
sản lượng là mùa khô 2027, hồi từ mùa lũ 2027. Kịch bản (2): đáy kéo tới T6-T7/2027 và mùa mưa 2027 đến muộn. Rủi ro hành chính
(khung giá đóng băng, tái đàm phán PPA, giá bán lẻ bị kìm) thì nằm **trong nước**, nhưng chậm và kéo dài nhiều năm.

| Tầm | CYCLICAL | ADMIN_GATED | STRUCTURAL | Lý do |
|---|---|---|---|---|
| **12 tháng** | **0,55** | 0,35 | 0,10 | Sản lượng (thuỷ văn El Niño) là biến lớn nhất của doanh thu 12T. Admin thể hiện qua Qc/khung giá/FMP trần/thanh toán EVN. Phụ tải mạnh không thêm được kWh cho nhà máy (công suất cố định) |
| **36 tháng** | 0,35 | **0,45** | 0,20 | Thuỷ văn trung bình hoá qua chu kỳ. Giá trị dài hạn do văn bản quyết: Pc sau trả nợ, gia hạn PPA/giấy phép, khung giá, thiết kế thị trường bán buôn, CAN. Structural = thiếu nguồn miền Bắc kéo FMP/CAN lên, nhưng tỷ lệ Qc cao làm thuỷ điện hưởng ít |

**Độ tin cậy: ambiguous khoảng 60/40.** Nhãn 12T nghiêng CYCLICAL khá rõ. Phần còn mơ hồ: sắc thái vùng Bắc/Bắc Trung Bộ (mùa lũ
2026 không khô đều, không có số hồ) và cơ chế Qc thuỷ điện chưa xác thực.
**Pha [UĐ]:** khối lượng thuỷ điện đang đi **từ đỉnh (2025) xuống đáy (mùa khô 2027)**. Giá giao ngay ở **giữa nhịp tăng**. Đây là
nửa xấu của chu kỳ thuỷ văn đối với nhà máy chủ yếu bán theo hợp đồng.

## 5. FORECAST khoá trước (2026-11-12)
Bobby không tự chấm. Mike hoặc người chấm đọc nguồn chính thức (EVN, NSMO, BCT, KTTV) vào ngày chấm. Tiêu chí: ĐÚNG/SAI theo ngưỡng
ghi trong bảng. Nguồn không công bố trước ngày chấm thì chấm "không chấm được", không tính.

| # | Mệnh đề | Ngày chấm | P |
|---|---|---|---|
| F1 | EVN công bố tỷ trọng thuỷ điện **cả năm 2026 ≤ 26,0%** sản lượng hệ thống (10T: 24,7%) | 2027-01-31 | 0,85 |
| F2 | Tỷ trọng thuỷ điện **H1/2027 < 21%** (H1/2026: 21%) | 2027-07-31 | 0,60 |
| F3 | FMP/CGM bình quân **cả năm 2026 ≥ 1.475 đ/kWh** (≥ +15% so với 1.283,4 năm 2025), theo NSMO hoặc báo cáo tổng kết | 2027-03-31 | 0,65 |
| F4 | Trần SMP 2027 (KH vận hành TTĐ 2027) **≥ 1.725 đ/kWh** | 2027-01-31 | 0,75 |
| F5 | CAN 2027 công bố **> CAN 2026** (cùng định nghĩa, cùng nguồn) | 2027-01-31 | 0,60 |
| F6 | Khung giá phát điện thuỷ điện 2027 có **trần > 1.110 đ/kWh** | 2027-07-31 | 0,30 |
| F7 | Giá bán lẻ điện bình quân được **tăng ít nhất 1 lần** trong khoảng 12/11/2026 → 30/06/2027 | 2027-06-30 | 0,40 |
| F8 | Trước 30/06/2027, EVN/NSMO/Bộ báo **≥1 hồ thuỷ điện lớn miền Bắc hoặc Bắc Trung Bộ về/gần mực nước chết hoặc phải ngừng phát** do thiếu nước | 2027-06-30 | 0,45 |
| F9 | Trong T5-T6/2027, EVN/NSMO công bố **cắt điện luân phiên do thiếu nguồn** ở miền Bắc (không tính sự cố lưới đơn lẻ) | 2027-07-15 | 0,25 |
| F10 | Cục KTTV/NOAA ghi nhận El Niño **còn hiệu lực (ONI ≥ +0,5) ở quý T3-T5/2027**, tức kịch bản (2) nghiêng thắng | 2027-06-30 | 0,45 |
| F11 | CCTG 12M Big-4 cao nhất (`cctg_rate_vn`) ngày 2027-05-12 **≤ 7,4%** | 2027-05-12 | 0,55 |
| F12 | Có văn bản (thông tư/hướng dẫn) về **phương pháp giá thuỷ điện sau khi hết PPA/biểu giá chi phí tránh được** ban hành trước 30/09/2027 | 2027-09-30 | 0,40 |

Lập luận [UĐ]:
- F1 dựa trên quán tính 10T. T11-T12 có lũ miền Trung nhưng khó kéo tỷ trọng quá 26%.
- F2 và F10 phụ thuộc kịch bản El Niño. F8 và F9 dùng tiền lệ mùa khô 2023 (hồ Bắc về mực nước chết, cắt điện), nhưng bị giảm xác suất
  vì 2026-27 có thêm than (Quảng Trạch I, nới khai thác than), mạch 500kV mạch 3, BESS và EVN đã chuẩn bị sớm.
- F6 thấp vì khung giá đã giữ nguyên 2024-2026 và giá bán lẻ vừa giảm.

**Điều làm tôi đổi phân loại:**
- (i) Số mực nước hồ miền Bắc/Bắc Trung Bộ cuối T12/2026 ≥ mực nước dâng bình thường ⇒ hạ CYCLICAL 12T xuống khoảng 0,45.
- (ii) Văn bản Qc thuỷ điện cho thấy Qc được điều chỉnh theo thuỷ văn thực ⇒ bất đối xứng CfD ở mục 3 yếu đi.
- (iii) Văn bản phương pháp giá sau PPA (F12), hoặc tin nhà máy >30 MW cũng bị ép giá tạm ⇒ nâng ADMIN 36T lên ≥0,55.

## 6. DD cần kiểm gì: nhà máy thuỷ điện 30-100 MW miền Bắc/Bắc Trung Bộ (kiểm bằng số)
1. **Sản lượng và giờ vận hành:** sản lượng thương phẩm theo tháng ≥5-10 năm, đặc biệt năm El Niño gần nhất (2019-20, 2023) so
   với năm La Niña (2022, 2025). Hệ số công suất = sản lượng ÷ (MW × 8.760), so với sản lượng thiết kế (Eo). Biên độ năm xấu/năm tốt.
2. **Thuỷ văn hiện thời:** mực nước hồ và dung tích hữu ích đầu T11 và cuối T12/2026 so với mực nước dâng bình thường và mực nước chết.
   Dòng về tháng 9-11/2026 so với trung bình nhiều năm. Kế hoạch sản lượng 2027 doanh nghiệp tự đặt.
3. **Giá bán bình quân** (doanh thu điện ÷ kWh) tách 3 phần: Pc (giá PPA, năm áp dụng, còn thành phần trả nợ hay không), phần FMP
   (SMP + CAN) và **khoản bù CfD khi Qm < Qc**. Tỷ lệ Qc/Qm theo tháng.
4. **PPA:** ngày ký, ngày hết hạn, điều khoản giá sau khi trả hết nợ, lịch tái đàm phán, tranh chấp đang mở với EVN/EPTC. Đã phát điện
   thị trường bao lâu (>30 MW bắt buộc).
5. **Pass-through:** tiền cấp quyền khai thác TN nước (số tiền/năm, quyết định phê duyệt, **EVN có hoàn trả không**), thuế tài nguyên
   nước, DVMTR 36 đ/kWh, phải thu EVN liên quan các khoản này.
6. **Cấu trúc chi phí:** khấu hao (còn bao nhiêu năm, % giá vốn), O&M, sửa chữa lớn sắp tới. Chi phí cố định/kWh ở năm khô.
7. **Nợ vay:** dư nợ, kỳ hạn, lịch trả gốc 2027-2030, lãi thả nổi (biên trên lãi huy động 12M?), phần ngoại tệ (USD/VND −2,7% 12T),
   DSCR năm El Niño. Lãi vay/EBITDA.
8. **Phải thu EVN:** số ngày phải thu theo quý 2023-2026, lãi chậm trả, dự phòng.
9. **Tập trung khách hàng:** 100% EVN. Có hợp đồng nào khác không (DPPA, bán lẻ khu vực)?
10. **Đa mục tiêu/chống lũ:** quy trình vận hành áp dụng (liên hồ hay đơn hồ), mực nước giới hạn mùa lũ, nghĩa vụ xả hạ du mùa khô,
    sản lượng mất do xả lũ/xả tràn, sự cố hoặc kiện tụng về xả lũ, phần vốn và chi phí của hạng mục thuỷ lợi.
11. **Quyền:** thời hạn giấy phép khai thác TN nước, thời hạn thuê đất (hằng năm hay một lần), BOT/chuyển giao (nếu có), giấy phép
    hoạt động điện lực.
12. **Lưới:** số giờ bị giới hạn công suất hoặc nghẽn 110/220kV, sự cố đường dây đấu nối.
13. **Cổ tức và dòng tiền:** FCF năm El Niño trước đây có đủ trả gốc và cổ tức không.

## 7. Tự kiểm và giới hạn
- **Tốt hơn tôi nghĩ:**
  - Cầu điện miền Bắc rất mạnh (+14% T10-T11) nên không có rủi ro điều độ.
  - Giá giao ngay và CAN đang lên.
  - Chi phí vốn không tăng (LNH 3M −1,36pp).
  - Mùa lũ 2026 ở miền Bắc có mưa lớn T8-T9, không khô đều.
- **Xấu hơn tôi nghĩ / chưa biết:**
  - Không có số mực nước hồ miền Bắc/Bắc Trung Bộ.
  - Cơ chế Qc thuỷ điện chưa xác thực.
  - Hai nguồn CAN lệch nhau (130 và 160).
  - FMP 8T +37% là nguồn cấp 2.
  - 10T/2025 thuỷ điện là số tự tính.
  - Mức thuế/phí tài nguyên nước chưa kiểm.
  - Ca ép giá tạm khi hết PPA mới thấy ở nhà máy <30 MW.
- Snapshot vĩ mô là bản tôi tự sinh lại (UNVERIFIED, không có vintage), vì file caller chỉ định không tồn tại.

## Nguồn (một số URL có tên DN/tổ chức trong đường dẫn — người đọc blind sau có thể bỏ qua)
- Snapshot: `mike/bin/macro_snapshot_asof.py --asof 2026-11-12` (BQ `tav2_bq.macro_indicator`), sinh 12/11/2026. Lãi suất: `deposit_rate_vn.effective_deposit_rate('2026-11-12')` (Big-4 6,8% @09/11; CCTG 12M 7,4% @02/11).
- EVN, KQ SXKD T10 và nhiệm vụ T11/2026, 03/11/2026: https://giaoduc.net.vn/hoat-dong-kinh-doanh-thang-10-va-muc-tieu-nhiem-vu-cong-tac-thang-112026-cua-tap-doan-dien-luc-vn-post263797.gd ; Nhân Dân 03/11/2026: https://nhandan.vn/post-999892.html
- EVN làm việc với EVNGENCO1 về mùa khô 2026-2027, 15/10/2026: https://tapchicongthuong.vn/lanh-dao-evn-lam-viec-voi-evngenco1-ve-ke-hoach-van-hanh--bao-dam-cung-cap-dien-mua-kho-2026-2027-557963.htm
- VnEconomy "Hai kịch bản rủi ro … El Niño 2026-2027", 23/07/2026: https://vneconomy.vn/hai-kich-ban-rui-ro-va-tac-dong-do-el-nino-2026-2027-tai-viet-nam.htm ; MAE: https://mae.gov.vn/chu-dong-giu-nguon-nuoc-truoc-el-nio-20262027-22889.htm ; Nhân Dân: https://nhandan.vn/el-nino-de-doa-nguon-nuoc-nhieu-luu-vuc-song-mua-kho-2027-post988918.html ; hatinh.gov.vn: https://hatinh.gov.vn/vi/bai-viet/hai-kich-ban-el-nino-tac-dong-den-viet-nam
- VnEconomy "Áp lực chi phí mua điện đầu vào tăng từ quý 2/2026", 19/04/2026 (FMP Q1 1.255, CAN Q1 160, thuỷ điện Q1 +7,8%): https://vneconomy.vn/ap-luc-chi-phi-mua-dien-dau-vao-tang-tu-quy-22026.htm
- Báo Đấu thầu, nhiệt điện 9T/2026: https://baodauthau.vn/doanh-nghiep-nhiet-dien-vao-nhip-tang-truong-cao-post210793.html
- Khung giá thuỷ điện 2026 (QĐ 1127/QĐ-BCT, 14/05/2026): https://tapchicongthuong.vn/bo-cong-thuong-phe-duyet-khung-gia-phat-dien-cho-thuy-dien-nam-2026-518752.htm ; https://moit.gov.vn/van-ban-phap-luat/quyet-dinh-phe-duyet-khung-gia-phat-dien-loai-hinh-nha-may-thuy-dien-nam-2026.html
- Thông tư 29/2026/TT-BCT (thị trường bán buôn điện cạnh tranh): https://moit.gov.vn/tin-tuc/bo-cong-thuong-ban-hanh-thong-tu-moi-quy-dinh-chi-tiet-van-hanh-thi-truong-dien.html ; https://luatvietnam.vn/dien-luc/thong-tu-29-2026-tt-bct-quy-dinh-van-hanh-thi-truong-ban-buon-dien-canh-tranh-436583-d1.html
- CAN/SMP 2026 (QĐ 3746, 26/12/2025, qua Vietcap 12/01/2026, cấp 2): https://pub-ab53b1eb21cf4bde977a49303cac98b3.r2.dev/sector/Utilities/Utilities-20260112-VCI-BCNganhNhietdien-Bao-cao-Nganh-Nhiet-dien-Gia-cong-suat-thi-truong-CAN-nam-20.pdf ; Vietcap 10/12/2025: https://www.vietcap.com.vn/en/research-center/thermal-power-sector-update-strong-power-demand-to-lift-2026-cgm-price-26-yoy ; ASEANSC triển vọng 2026 (CGM 2025): https://www.aseansc.com.vn/wp-content/uploads/2025/12/TRIEN-VONG-NGANH-DIEN-2026_WEB-1.pdf
- Tiền Phong "Vướng đàm phán giá, một số nhà máy nhỏ phải dừng phát điện", 30/10/2026: https://tienphong.vn/vuong-dam-phan-gia-mot-so-nha-may-nho-phai-dung-phat-dien-post1889871.tpo
- EVN tài chính 2025: https://daibieunhandan.vn/evn-thong-tin-lam-ro-ve-loi-nhuan-nam-2025-va-so-du-tien-gui-ngan-hang-10419578.html ; https://tienphong.vn/evn-len-tieng-ve-khoan-tien-gui-ngan-hang-dau-tu-tai-chinh-152000-ty-dong-post1849635.tpo
- DVMTR 36 đ/kWh (NĐ 156/2018 Đ59): https://hethongphapluat.com/nghi-dinh-156-2018-nd-cp-huong-dan-luat-lam-nghiep/dieu-59 ; tiền cấp quyền: https://nongnghiepmoitruong.vn/quy-dinh-tinh-tien-cap-quyen-khai-thac-tai-nguyen-nuoc-i825468.html ; https://khodulieu.sohoa.tuyenquang.gov.vn/congthongtin/media/ab389342f0c0473cd1c98216b49f1102.pdf
- Thuỷ điện nhỏ miền Bắc / Pmax EVNNPC: https://voh.com.vn/kinh-te/gan-400-thuy-dien-nho-giam-ap-luc-phu-tai-mien-bac-658634.html
- Mưa lũ Bắc Bộ/Thanh Hoá-Nghệ An T8-T9/2026: https://mae.gov.vn/canh-bao-lu-len-tren-cac-song-o-bac-bo-va-thanh-hoa-22944.htm ; bản tin KTTV (kttv.gov.vn, T8/2026)
- Giá điện bán lẻ −2% từ 01/11/2026 (QĐ 1305/QĐ-EVN): qua `sector_read_khi_dot_lpg_20261109.md`.
