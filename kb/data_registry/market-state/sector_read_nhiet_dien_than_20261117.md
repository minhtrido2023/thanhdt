---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-17. KHÔNG biết giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp nhiệt điện than cụ thể (xem §0 về rò rỉ danh tính qua tên thư mục).
blind: YES
as_of: 2026-11-17 (snapshot vĩ mô dd_*_20261117 có áp độ trễ công bố; BQ commodity_prices TE tới 2026-11-13/16; lãi suất PIT tới 2026-11-16; tin web ≤ 2026-11-07)
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành nhiệt điện than VN — nhà máy thuộc công ty cổ phần niêm yết (không phải GENCO lớn), bán điện cho EVN (người mua duy nhất) qua PPA + thị trường phát điện cạnh tranh, than nội (TKV/Đông Bắc) + than nhập pha trộn, chịu chu kỳ thuỷ văn. Gồm pipeline cầu + PDP8, cơ chế giá (PPA 2 thành phần, Qc/FMP/CAN, pass-through nhiên liệu, tỷ giá), phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED 2 tầm, FORECAST khoá trước có ngày chấm, checklist DD.
---

# SECTOR READ: Nhiệt điện than (IPP niêm yết, ngoài GENCO), as-of 17/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán /
suy luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải KIỂM trước khi dùng làm số).
File chị em: `sector_read_than_20261111.md` (cung than TKV, NQ28, nhập khẩu), `sector_read_thuy_dien_20261112.md` (El Niño,
Qc/CfD, FMP/CAN, tài chính EVN), `sector_read_khi_dot_lpg_20261109.md` (giá điện bán lẻ −2%, NĐ 100/2025, Hormuz),
`sector_read_power_consulting_20261028.md` (PDP8 trượt tiến độ, thiếu nguồn 2027-2030). Forecast ở §5 cố ý **nhất quán** với
xác suất đã khoá ở các file đó; mệnh đề trùng thì tôi không khoá lại.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Snapshot:** đọc đúng file caller chỉ định `agents/Taylor/research/dd_QTP_20261117/macro_snapshot_20261117.md`. Trong thư mục
  đó chỉ liệt kê tên (`macro_snapshot_20261117.md`, `src/`); **không mở `src/`**.
- **Rò rỉ danh tính (ghi trung thực):** tên thư mục dispatch chứa một chuỗi giống mã chứng khoán; tôi **nhận ra** nó có thể ứng với
  một DN nhiệt điện than ở Quảng Ninh. Tôi không tra mã đó, không mở BCTC/BCTN/báo cáo CTCK/giá cổ phiếu nào. Hệ quả: một dòng dự
  thảo PDP8 (danh sách nhà máy dừng sau 2030, §2b) nêu tên vùng/nhà máy trùng địa danh — tôi ghi nó như **dữ kiện ngành** và đưa vào
  checklist DD, **không** để nó làm nặng/nhẹ phân loại. Người dùng file nên biết người đọc đã không hoàn toàn mù danh tính.
- **Rò rỉ qua kết quả tìm kiếm (KHÔNG dùng):** tên file báo cáo CTCK quý 2/2026 của một DN cùng chuỗi ký tự; tiêu đề KQKD quý của
  một DN điện khí, một tổng công ty phát điện thuộc EVN, bài "DN nhiệt điện lãi lớn từ của để dành" (chênh lệch tỷ giá). Không mở
  bài nào trong số đó. Dùng duy nhất một chi tiết vận hành: một nhà máy than nhập miền Nam đã chốt hợp đồng 5,1 tr t than nhập cho 2027
  (minh hoạ **thời điểm** ký hợp đồng nhiên liệu, không phải số của DN được hỏi).
- **BQ (tự truy vấn 17/11):** `tav2_bq.commodity_prices` TE `coal` (Newcastle) + `brent` daily. Lãi suất PIT: `deposit_rate_vn.
  effective_deposit_rate('2026-11-17')`, `cctg_rate_vn.current_cctg_rate`, `macro_killswitch_a_status`. Không dùng `ticker_financial`
  (sẽ phải chọn DN ⇒ phá blind).
- **Không có số (ghi "không có số", không suy):** giá than TKV bán cho điện 2026/2027 (biểu nội địa, than pha trộn); tỷ lệ Qc nhiệt
  điện than 2026 (QĐ thị trường điện 2026 — một trích dẫn môi giới nói "80% đối…" bị cắt, không rõ loại hình); FMP/SMP tháng 9-11/2026;
  CAN 2026 cho than; khung giá than >200 MW 2026 (2 số mâu thuẫn, §3); USD/JPY và EUR/VND (snapshot loại có chủ đích); tồn kho than tại
  nhà máy; hạn ngạch phát thải phân bổ riêng cho từng nhà máy than.

## 1. Snapshot vĩ mô + chuỗi giá
| Chỉ báo | Giá trị | Δ3T / Δ12T | Đọc cho nhiệt điện than |
|---|---|---|---|
| Sản xuất CN YoY | 15,0% (T10) | +0,5 / +4,6pp | Phụ tải công nghiệp mạnh; T10 sản lượng hệ thống +14,3% |
| GDP YoY | 9,95% (Q3) | +1,14 / +1,70pp | Nền cầu điện ~10%/năm (BCT: 2027 +~10% trên nền cao 2026) |
| PMI SX | 52,3 (T10) | −0,6 / −2,2 | Còn mở rộng, đà chậm nhẹ |
| CPI YoY | 5,09% (T10) | +0,64 / +1,84pp | Lạm phát tăng ⇒ lực cản chính trị lên giá điện bán lẻ (EVN vừa giảm 2% từ 01/11) ⇒ ép biên người mua duy nhất |
| USD/VND | 25.764 (16/11) | −1,68% / **−2,24%** | VND lên giá ⇒ lỗ tỷ giá đánh giá lại nợ USD **giảm**; giá than nhập quy VND nhẹ hơn. **JPY/EUR: không có số** |
| US 10Y / DXY | 5,13% / 103,5 | +0,40pp/+0,99pp; DXY +3,9% 12T | Đô la mạnh + lãi suất USD cao: rủi ro đảo chiều VND là đuôi, chưa là xu hướng |
| Newcastle (TE daily, USD/t) | TB T11 (10 phiên tới 13/11) **143,78**; 13/11: 145,75 | TB T11/2025 110,33 ⇒ **+30% YoY**; T10/2026 150,26 (đỉnh năm); T1 108,8 → T3 138,6 → T7 130,0 → T10 150,3 [DK, BQ] | Qua đỉnh T10 nhưng nảy lại giữa T11 (138,05 ngày 09/11 → 145,75). Quy VND ≈ +27% YoY [UĐ] |
| Than nhập khẩu bình quân VN | **122,3 USD/t** (1/1→15/10/2026) | +22,5% YoY [DK, Hải quan qua cafef/VNS 27/10 & 07/11] | Chậm hơn Newcastle (cơ cấu Indonesia nhiệt trị thấp) |
| Brent (TE) | TB T11 97,06 | T10 107,33; T11/2025 63,49 | Gián tiếp: dầu/khí đắt ⇒ điện khí/dầu xếp sau than trong điều độ |

**Chi phí vốn — bảng 5 tầng** (ngành nợ dài hạn, phần lớn nhà máy cũ vay ngoại tệ ECA/ODA + vay VND thả nổi [NỀN]):
| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (16/11, đi ngang từ 03/10) | Tách online / tại quầy, và 6M: **không có số** (series lưu MAX) |
| B. Bán hành chính | CCTG 12M Big-4 cao nhất | **7,4%** (02/11) | Spread CCTG − tiết kiệm 12M = **+0,6pp**; từng NH, sự kiện mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi ẩn, số NH ≥7% | không có số | |
| D. Thị trường | LNH 3M | **6,33%** (11/11; −1,19pp 3T, +0,03pp 12T) | OMO/tín phiếu, tỷ lệ trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y (chỉ tin Δ) | 4,57 (+0,00pp 3T / **+0,57pp 12T**) | Lãi dài hạn nhích lên trong năm |
| E. Lượng | Tín dụng vs huy động YTD, LDR, văn bản nới LDR | không có số trong lượt này | |

Đồng thuận/phân kỳ [UĐ]: **HƯỚNG** — A, B đi ngang; D ngắn hạn giảm mạnh (liên NH dịu sau đỉnh ~7,5% 3 tháng trước), D dài hạn
tăng nhẹ ⇒ không proxy nào báo chi phí vốn VND đang tăng trong 3-6T. **MỨC** — chi phí biên (CCTG 7,4%) cao hơn số niêm yết ~0,6pp.
Kill-switch A (>7,5%) **CLEAR** (7,4%, age 1 ngày). Với nhà máy than cũ, chi phí lãi VND là biến thứ yếu (nợ đã trả nhiều) — biến
tài chính chính là **tỷ giá trên dư nợ ngoại tệ còn lại** và **khả năng EVN hoàn trả chênh lệch tỷ giá** (§3). Độ tin cậy trung bình
(thiếu tầng C, E).

## 2. Pipeline cầu

### 2a. Huy động than: đang ở đỉnh chu kỳ thuỷ văn xấu, nền cầu STRUCTURAL
- **Hệ thống 10T/2026: 297,4 tỷ kWh (+9,8%), T10 +14,3%; ước cả năm 356,2 tỷ kWh (+10,3%); Pmax 57.537 MW (T6), vượt đỉnh 2025 6,4%;
  Q4/2026 phụ tải dự báo +13% toàn quốc, +14% miền Bắc, một số tỉnh Bắc/Bắc Trung Bộ gần +20%** [DK, BCT/NSMO, VietnamPlus 07/11/2026].
- **Than: 9T 132,6 tỷ kWh (~49%); 10T 147,78 tỷ kWh = 49,7%; H1 93,44 tỷ kWh = 54,5%** [DK, VNS 07/11; VietnamPlus 03-07/11; Tạp chí
  Công Thương]. So 10T/2025 (~124 tỷ kWh, tự tính ở file than) ⇒ **~+19% YoY** [UĐ]. Một nguồn môi giới: kế hoạch vận hành buộc tăng huy
  động than ~22% YoY [DK cấp 2].
- **Thuỷ điện:** dòng về hồ ~**80% TBNN**; cả năm 2026 dự kiến **thấp hơn 2025 ~18,5 tỷ kWh**; hồ phải tích tối đa tới 31/12/2026 và
  giữ tới 31/3/2027; El Niño có thể kéo dài tới ~T6/2027 [DK, BCT 07/11/2026]. KTTV: mưa T11-T12 dưới TBNN; xác suất El Niño rất mạnh
  60-65% cực đại T11/2026-T1/2027 [DK, báo dẫn KTTV T9-T11/2026]. ⇒ BCT chỉ đạo **tăng huy động nhiệt điện từ cuối 2026 để dành nước cho
  mùa khô** [DK, Tạp chí Công Thương 28/07/2026].
- **Thiếu nguồn 2027:** BCT cảnh báo **thiếu 4.256 MW công suất và 2,9 tỷ kWh năm 2027** nếu nguồn không vào kịp; "nguồn điện nền mới
  chưa kịp đưa vào vận hành"; mục tiêu cắt ≥3.000 MW đỉnh miền Bắc 2027 bằng DR/tiết kiệm (CV 10790/VPCP-CN 22/10/2026) [DK, VNS 07/11,
  VietnamPlus 07/11]. ⇒ [UĐ] Nhà máy than **miền Bắc** (vùng thiếu nguồn nhất) gần như chắc được huy động ở mức khả dụng tối đa suốt
  mùa khô 2027; rủi ro cầu ~0, rủi ro thật là **khả dụng tổ máy** và **than đủ/đúng chất lượng**.
- **Nguồn cạnh tranh mới trong điều độ:** Quảng Trạch I (than, 1.403 MW) đã phát 620 tr kWh, COD 2 tổ trong 2026; Long Phú I (1.200 MW)
  và An Khánh-Bắc Giang (650 MW) có mốc 2027 [DK cấp 2, báo cáo ngành]; Nhơn Trạch 3-4 (LNG) COD 05/01/2026; tái tạo 10T 13,7%; BESS
  đang có khung giá [DK]. ⇒ [UĐ] Tầm 12T, cầu tăng (~35 tỷ kWh/năm) **lớn hơn** phần nguồn mới bổ sung ⇒ không đẩy than cũ ra khỏi điều độ.
  Tầm 24-36T (LNG Hiệp Phước Q4/2028, tái tạo, hạt nhân sau 2030) mới bắt đầu cạnh tranh nhà máy than hiệu suất thấp.
- **Kịch bản H2/2027 [UĐ]:** nếu El Niño tắt giữa 2027 và chuyển trung tính/La Niña, thuỷ điện hồi mạnh mùa lũ 2027 ⇒ huy động than
  H2/2027 có thể **giảm YoY** dù cả năm vẫn cao. Đây là đảo chiều chu kỳ quan trọng nhất cần theo dõi (FMP sẽ giảm theo).

### 2b. Quy hoạch: "không thêm than mới" đang bị đảo một phần
- **PDP8 điều chỉnh (QĐ 768/QĐ-TTg, 15/04/2025):** than tới 2030 **31.055 MW**, gồm 5 dự án đang xây (4.360 MW), **không thêm nhà máy mới**
  [DK, VNS 07/11/2026; thẩm định PDP8 qua báo 2025]. Định hướng: nhà máy **>20 năm chuyển đổi sinh khối/amoniac**, **>40 năm không chuyển
  đổi được thì dừng** [DK cấp 2, VnEconomy — văn bản gốc QĐ 768 chưa đọc]. Một **dự thảo** (2025) nêu ~**4.500 MW** dừng sau 2030 (Phả Lại II,
  Hải Phòng, Quảng Ninh, Na Dương I, Sơn Động, Uông Bí, Formosa Đồng Nai, Vedan) — **dự thảo, chưa chắc là bản cuối** [DK cấp 2, tóm tắt
  tìm kiếm]. QĐ 266/QĐ-TTg (02/2025) — kế hoạch chuyển đổi điện than [DK cấp 2]. Thực tế: chuyển đổi đang **thiếu cơ chế, vốn, công nghệ**
  (amoniac đồng đốt còn thử nghiệm) [DK cấp 2, VnEconomy].
- **Đảo chiều 2026:** BCT đề xuất **bổ sung 5.300 MW than mới** gần trung tâm phụ tải (Quảng Ninh, Hưng Yên, Quảng Trị, Cần Thơ) tới 2030,
  CCS theo giai đoạn; **miễn tạm tới 2030** quy chuẩn nhiệt độ nước làm mát xả cho một số nhà máy miền Bắc khi vận hành khẩn cấp; giữ cơ chế
  khai thác than vượt 15% tới hết 2027; đề xuất chuyển LNG chậm sang 2031-2035 [DK, VNS 07/11/2026; file tư vấn điện]. ⇒ [UĐ] Chính sách
  **kéo dài vai trò than** 2027-2035; nhưng ngày dừng/chuyển đổi của **từng nhà máy cũ** vẫn là văn bản chưa chốt ⇒ ADMIN_GATED.
- **Carbon:** QĐ 263/QĐ-TTg (09/02/2026) tổng hạn ngạch thí điểm 2025-2026 cho 110 cơ sở (34 nhiệt điện, 25 thép, 51 xi măng), ~268,4 tr tCO2e
  cho 2026, **phân bổ miễn phí 100%**, bù trừ tín chỉ ≤30%; sàn carbon thí điểm từ 29/06/2026; **tuân thủ bắt buộc mở rộng từ 2028** [DK, nhiều
  báo T2-T7/2026]. ⇒ [UĐ] Chi phí carbon 2026-27 ~0; từ 2028 là rủi ro chi phí mới mà PPA cũ **chưa có điều khoản pass-through** [NỀN — PHẢI KIỂM].

## 3. Cấu trúc cạnh tranh & cơ chế giá
- **Người mua duy nhất:** EVN/EPTC [NỀN]. IPP than ngoài GENCO thường do DNNN/TKV/EVN nắm chi phối, vận hành từ 2000s-2010s, vốn vay ECA/ODA
  ngoại tệ [NỀN].
- **PPA 2 thành phần [NỀN — PHẢI KIỂM theo từng hợp đồng]:** (i) **giá cố định (công suất)** = khấu hao + lãi vay + O&M cố định + lợi nhuận
  (ROE) đã thoả thuận — **ADMIN**, giảm khi hết khấu hao/trả hết nợ (đàm phán lại giá cố định giai đoạn sau); (ii) **giá biến đổi** = suất hao
  nhiệt × giá than thực tế theo hợp đồng TKV/Đông Bắc (+ vận chuyển) ⇒ **pass-through nhiên liệu**, rủi ro nằm ở định mức suất hao và việc EVN
  chấp nhận giá than thực tế. Tham chiếu khung giá: **QĐ 2887/QĐ-BCT (30/10/2026), nhà máy than <200 MW: 0-2.230,51 đ/kWh** (chưa VAT), giả
  định giá than **1.726.715 đ/t** (gồm vận chuyển, hao hụt), nhiệt trị 3.784 kcal/kg, suất hao 2.705,41 kcal/kWh ở 85% tải [DK, VietnamPlus
  03/11/2026]. Tự tính [UĐ]: chi phí nhiên liệu ≈ 2.705/3.784 × 1.727 ≈ **1.234 đ/kWh ≈ 55% trần** ⇒ phần còn lại ~1.000 đ/kWh là giá cố định +
  biên. Khung than lớn 2026: một nguồn nói tối đa **2.218,95 đ/kWh** (Tạp chí Công Thương 09/07/2026), Tiền Phong nói "gần 2.220 đ/kWh" cho nhà máy
  DNNN đầu tư bằng vốn CSH — **không rõ cùng loại hình** [DK cấp 2]. Khung là **trần đàm phán**, không phải giá EVN phải mua.
- **Thị trường điện (TT 29/2026/TT-BCT, hiệu lực ~20/07/2026) [DK cấp 2 + NỀN]:** nhà máy trực tiếp tham gia nhận `Qc×Pc + (Qm−Qc)×FMP`
  (+ CAN). **Bất đối xứng THUẬN cho than năm khô** (ngược với thuỷ điện): Qm > Qc, FMP cao ⇒ phần vượt Qc bán theo FMP > chi phí biến đổi ⇒ biên
  tăng. FMP Q1/2026 1.255 đ/kWh; môi giới dự báo FMP tăng từ Q2/2026; một tóm tắt nói 8T ~1.430 (+37%) [DK cấp 2]; **T9-T11: không có số**.
  Tỷ lệ Qc than 2026: **không có số**. ⇒ [UĐ] Upside từ thị trường là **có nhưng bị giới hạn** bởi tỷ lệ Qc cao (đa số sản lượng nằm trong Pc) và
  trần SMP.
- **Tỷ giá:** cơ chế PPA cho phép **thu hồi chênh lệch tỷ giá** khoản vay ngoại tệ, EVN thanh toán **trễ nhiều năm** theo văn bản chấp thuận
  (ví dụ văn bản 8344/EVN-TCKT 27/12/2025 cho phép ghi nhận chênh lệch 2019-2021 của một số nhà máy) [DK, tóm tắt báo]. Ở cấp EVN: còn
  **~17.500 tỷ chênh lệch tỷ giá chưa phân bổ vào giá điện** tính tới hết 2025 (Tuổi Trẻ 11/06/2026); dự thảo sửa NĐ 72/2025 cho phép phân bổ
  chi phí chưa tính đủ vào giá bán lẻ bị BTC phản đối [DK, báo 2025-26]. ⇒ [UĐ] Dòng doanh thu "chênh lệch tỷ giá" của IPP là **ADMIN, lumpy, phụ
  thuộc sức khoẻ EVN** — năm EVN lãi (2025) thì giải ngân, năm EVN bị ép (2026-27) thì có thể chậm lại.
- **Sức khoẻ người mua:** EVN 2025 lãi hợp nhất ~51.881 tỷ, tiền gửi ~152 nghìn tỷ, phải trả IPP+nhiên liệu >118 nghìn tỷ [DK, file thuỷ điện].
  2026: thuỷ điện rẻ −18,5 tỷ kWh, than +~19%, nhiên liệu đắt, **giá bán lẻ −2% từ 01/11/2026 (QĐ 1305/QĐ-EVN)**, NĐ 278/2026 siết thủ tục tăng
  giá [DK, file khí]. ⇒ [UĐ] Biên EVN bị ép 2026-27 ⇒ rủi ro **kéo dài kỳ thu tiền** của IPP tăng từ thấp lên **thấp-vừa**; rủi ro **không thanh
  toán** vẫn thấp nhờ đệm tiền mặt.
- **Than đầu vào:** EVN yêu cầu chốt hợp đồng antraxit 2027 trong T10/2026, nâng tồn kho tối đa tới đầu T3/2027; nhà máy đề nghị ký với TKV
  ~**42 tr t cho 2027**; TKV cho biết khai thác nội ngày càng khó (mỏ sâu, chi phí tăng) nên phải **pha trộn than nhập** (một con số ~11,4 tr t
  nhập phục vụ pha trộn — không rõ năm 2026 hay 2027) [DK, cafef/Tiền Phong 27/10, VNS 07/11]. Giá than cho điện 2026/2027: **không có số**;
  không thấy quyết định điều chỉnh giá than cho điện năm 2026 (file than, tìm 1 lần). ⇒ [UĐ] Rủi ro thật của nhà máy dùng antraxit nội: **chất
  lượng than pha trộn lệch thiết kế lò** (suất hao, sự cố, khả dụng), không phải giá (vì pass-through).
- **Cạnh tranh:** không có cạnh tranh giá theo nghĩa thường — thứ tự điều độ theo giá chào/chi phí biến đổi; than miền Bắc gần mỏ có lợi thế
  vận chuyển [NỀN]. Rào cản gia nhập: tuyệt đối (quy hoạch cấm/hạn chế than mới tới khi PDP8 được sửa).

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1 — nguyên nhân gốc bối cảnh hiện tại:** huy động than cao kỷ lục 2026 = **thời tiết ngoại sinh** (El Niño sau năm La Niña 2025) +
**cú sốc giá năng lượng ngoại sinh** (Hormuz ⇒ khí/LNG đắt, than xếp trước trong điều độ) + **nền cầu cấu trúc** (~10%/năm theo GDP ~10%,
nguồn nền mới trễ). Lạm phát nội tăng (CPI 5,09%) không phải nguồn của cầu điện; nó là **lực cản chính trị** lên giá bán lẻ.
**Trục 2 — containable?** Phần thời tiết tự hết theo lịch tự nhiên (đáy thuỷ điện mùa khô 2027, có thể hồi từ mùa lũ 2027). Phần thiếu nguồn
**không** tự hết trong 24-36T (nguồn nền mới trễ) — đây là lực đỡ dài hơn chu kỳ.

**Nhãn driver lợi nhuận/giá trị của IPP than niêm yết** (xác suất = trọng số "driver CHÍNH", tổng = 1):
| Tầm | ADMIN_GATED | CYCLICAL | STRUCTURAL | Diễn giải |
|---|---|---|---|---|
| **12 tháng** | **0,45** | 0,40 | 0,15 | Sản lượng gần như chắc cao (cyclical El Niño + thiếu nguồn); nhưng **biên** do văn bản quyết: tỷ lệ Qc, giá cố định PPA (đặc biệt bước giảm sau hết khấu hao/trả nợ), EVN chấp nhận giá than thực tế, lịch thanh toán chênh lệch tỷ giá, kỳ thu tiền. Cyclical = FMP/CAN + Qm>Qc. Structural = nền cầu |
| **36 tháng** | **0,50** | 0,20 | 0,30 | Giá trị còn lại do văn bản: PDP8 sửa (than mới / ngày dừng / chuyển đổi 20-40 năm), ETS bắt buộc từ 2028 (pass-through?), Luật Điện lực sửa đổi + thị trường bán lẻ, gia hạn PPA. Structural = thiếu nguồn kéo dài vai trò than + xu hướng khử carbon dài hạn (hai lực ngược chiều) |

**Độ tin cậy: AMBIGUOUS ~60/40.** Nhãn 12T giữa ADMIN và CYCLICAL sát nhau; chênh lệch phụ thuộc biến **không có số** (tỷ lệ Qc than 2026/2027,
FMP T9-T11, cấu trúc giá cố định từng PPA).
**Pha [UĐ]:** khối lượng ở **đỉnh chu kỳ** (Q4/2026 → mùa khô 2027), giá thị trường **giữa→muộn nhịp tăng**, giá than thế giới **vừa qua đỉnh**
(T10) nhưng chưa giảm rõ. Với IPP than **cũ**, chu kỳ thuỷ văn chỉ quyết **lợi nhuận 12T**; **giá trị** quyết bởi đồng hồ PPA/khấu hao/tuổi
nhà máy và văn bản chuyển đổi — tức một DN có thể vừa "lãi kỷ lục" vừa "giá trị cuối đời hữu hạn".

**Falsifiers (sẽ đổi nhãn):** (i) KH vận hành 2027 (BCT, thường ban hành ~cuối T11-T12) giao **Qc than thấp** hoặc huy động than 2027 thấp hơn
2026 ⇒ CYCLICAL 12T giảm; (ii) El Niño tắt trước T3/2027 + thuỷ điện hồi ⇒ đỉnh chu kỳ qua sớm; (iii) PDP8 sửa chính thức chốt lịch dừng/chuyển
đổi nhà máy >20-40 năm ⇒ STRUCTURAL/ADMIN 36T tăng, thời hạn giá trị rút ngắn; (iv) EVN lỗ 2026 + dừng thanh toán chênh lệch tỷ giá ⇒ ADMIN 12T tăng.

## 5. FORECAST khoá trước (2026-11-17)
Bobby không tự chấm. Mike/người chấm đọc nguồn chính thức (EVN, NSMO, BCT, Chính phủ, QH, KTTV) hoặc BQ tại ngày chấm. Nguồn không công bố trước
ngày chấm ⇒ "không chấm được". **Mệnh đề đã khoá ở file chị em (không khoá lại, chỉ dẫn chiếu):** than ≥49,0% cả năm 2026 P0,65 và điện than
H1/2027 ≥+5% P0,55 (file than F3/F4); giá bán lẻ tăng ≥1 lần 12/11/2026→30/06/2027 P0,40 (file thuỷ điện F7); FMP 2026 ≥1.475 P0,65 (thuỷ điện F3);
El Niño còn hiệu lực T3-T5/2027 P0,45 (thuỷ điện F10); cắt điện luân phiên miền Bắc T5-T6/2027 P0,25 (thuỷ điện F9); CCTG 12M ≤7,4% ngày 2027-05-12
P0,55 (thuỷ điện F11).

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | Sản lượng nhiệt điện than **cả năm 2026 ≥ 175 tỷ kWh** (10T 147,78; T11-T12 hệ thống ~58,8 tỷ kWh, than ~50-55%) | 0,70 | 2027-01-31 | EVN/NSMO tổng kết năm |
| F2 | Điện than **H1/2027 ≥ H1/2026 (93,44 tỷ kWh)** | 0,75 | 2027-07-31 | EVN/NSMO 6 tháng |
| F3 | Điện than **cả năm 2027 ≥ cả năm 2026** (cùng nguồn) | 0,60 | 2028-01-31 | EVN/NSMO tổng kết năm |
| F4 | Điện than **H2/2027 < H2/2026** (cùng nguồn; = chu kỳ thuỷ văn đảo chiều) | 0,40 | 2028-01-31 | EVN/NSMO (tổng năm − H1) |
| F5 | Newcastle TE **TB tháng 3/2027 < 140 USD/t** (TB T11/2026 MTD 143,78) | 0,50 | 2027-04-05 | BQ `commodity_prices` TE `coal` daily |
| F6 | BCT phê duyệt **khung giá phát điện than 2027** (bất kỳ loại hình than) có trần **> trần 2026 cùng loại hình** | 0,55 | 2027-12-31 | moit.gov.vn |
| F7 | TTg ký quyết định **điều chỉnh PDP8 có bổ sung ≥1.000 MW nhiệt điện than MỚI** (ngoài 31.055 MW) | 0,40 | 2027-12-31 | Cổng Chính phủ/BCT |
| F8 | EVN công bố **LNST hợp nhất 2026 > 0** | 0,55 | 2027-07-31 | BCTC kiểm toán/thông cáo EVN |
| F9 | QH **thông qua** Luật sửa đổi, bổ sung một số điều Luật Điện lực tại kỳ họp thứ 2 khoá XVI | 0,70 | 2026-12-31 | quochoi.vn |
| F10 | Có văn bản quy định **hạn ngạch phát thải 2027-2028 KHÔNG miễn phí 100%** (có phần đấu giá) cho nhiệt điện | 0,15 | 2027-12-31 | Cổng Chính phủ/BNNMT |
| F11 | USD/VND (TE, snapshot) ngày 2027-05-17 **≤ 26.300** (≈ +2,1% từ 25.764) | 0,70 | 2027-05-17 | BQ `macro_indicator` vn_usdvnd |
| F12 | Có văn bản chính thức (TTg/BCT) **chốt danh sách/lịch dừng hoặc chuyển đổi nhiên liệu** cụ thể cho nhà máy than hiện hữu (không phải định hướng chung) | 0,25 | 2027-12-31 | Cổng Chính phủ/BCT |
| F13 | KH cung cấp điện & vận hành hệ thống 2027 (BCT) ban hành **trước 2027-01-15** | 0,70 | 2027-01-15 | moit.gov.vn (KH 2026: QĐ 3477 ngày 28/11/2025) |

Lập luận [UĐ]: F1 — Q4 phụ tải +13% và chỉ đạo dành nước ⇒ than Q4 ≥50%. F2 cao hơn F file than (+5%) vì chỉ cần không giảm; Q1/2026 thuỷ điện
còn La Niña (+7,8%) nên nền H1/2026 thuỷ điện cao hơn H1/2027 sẽ có. F3 thấp hơn F2 vì F4: H2/2027 thuỷ điện có thể hồi mạnh. F5 ~0,5: Hormuz +
mùa xuân Bắc bán cầu kéo xuống, nhưng El Niño nóng châu Á + Indonesia cắt hạn ngạch đỡ giá. F6: than đắt + VND quy đổi ⇒ trần tăng, nhưng cơ quan
có thể giữ giả định giá than. F8: 2025 lãi lớn là đệm, nhưng 2026 mất ~18,5 tỷ kWh thuỷ điện rẻ + nhiên liệu đắt + giảm giá bán lẻ ⇒ sát hoà vốn.
F11: VND lên giá 12T dù DXY tăng (thặng dư thương mại 7,3 tỷ USD T10) — đuôi xấu là đô la mạnh tiếp.

## 6. DD cần kiểm gì — nhà máy nhiệt điện than niêm yết (IPP ngoài GENCO)
1. **PPA:** số, ngày ký, **thời hạn còn lại**, các phụ lục sửa đổi; cấu trúc 2 thành phần (giá cố định / biến đổi) theo năm; **lịch giá cố định
   sau khi hết khấu hao/trả hết nợ** (bước giảm bao nhiêu, đã đàm phán xong chưa, có tạm tính không); ROE trong giá; điều khoản pass-through
   carbon/môi trường (có hay không) cho giai đoạn ETS bắt buộc từ 2028.
2. **Thị trường điện:** tham gia trực tiếp hay gián tiếp; **tỷ lệ Qc năm 2025-2026 và Qc dự kiến 2027**; doanh thu Pc vs FMP vs CAN theo quý; giờ bị
   giới hạn công suất do lưới; tranh chấp quyết toán thị trường.
3. **Sản lượng & khả dụng:** sản lượng thực phát vs kế hoạch 5 năm; hệ số khả dụng, **số giờ sự cố/tổ máy**, lịch **đại tu** (BCT muốn đại tu T1-T4);
   tuổi từng tổ máy; suất hao nhiệt thực tế vs định mức trong PPA (vượt định mức = EVN không trả).
4. **Than:** hợp đồng 2027 với TKV/Đông Bắc (khối lượng, giá/công thức, **tỷ lệ pha trộn than nhập**, nhiệt trị/tro/lưu huỳnh so thiết kế lò); EVN có
   chấp nhận giá than thực tế đầy đủ vào giá biến đổi không, độ trễ; tồn kho than (ngày đốt) tại 31/12 và 01/03; vận chuyển (cảng, băng tải, sà lan).
5. **Nợ vay & tỷ giá:** dư nợ theo **đồng tiền (USD/JPY/EUR/VND)**, lãi suất cố định/thả nổi, **lịch trả gốc còn lại**; phòng ngừa tỷ giá; chính sách
   kế toán chênh lệch tỷ giá (ghi P&L ngay hay phân bổ); **phải thu chênh lệch tỷ giá từ EVN** (số dư, năm phát sinh, văn bản chấp thuận, đã ghi doanh
   thu hay chưa); độ nhạy ±1% USD/VND, ±10% JPY ⇒ ±? lợi nhuận. (USD/JPY: snapshot không có số — DD phải tự lấy.)
6. **Khấu hao:** năm hết khấu hao từng hạng mục chính; sau hết khấu hao lợi nhuận kế toán tăng nhưng **giá cố định PPA giảm** — phải tách hai hiệu ứng.
7. **Dòng tiền & người mua:** kỳ thu tiền EVN theo quý (2024→2026), nợ quá hạn, lãi chậm trả; tiền gửi/đầu tư tài chính; capex duy trì vs khấu hao.
8. **Cổ tức & cổ đông:** cơ cấu cổ đông chi phối (EVN/TKV/DNNN khác), tỷ lệ chi trả lịch sử, chính sách giữ lại cho chuyển đổi nhiên liệu; khả năng
   thoái vốn/tái cơ cấu của cổ đông nhà nước (file than: đề án tái cơ cấu TKV hạn 27/11/2026).
9. **Môi trường:** bãi thải tro xỉ (dung tích còn lại, năm đầy), **tỷ lệ tiêu thụ tro xỉ** và doanh thu/chi phí; quy chuẩn khí thải, nhiệt độ nước làm
   mát (có thuộc diện miễn tạm tới 2030 không); xử phạt; ký quỹ/hoàn nguyên.
10. **Carbon:** hạn ngạch 2026 được giao vs phát thải thực; dự kiến thiếu/thừa; chi phí tín chỉ; ai chịu chi phí từ 2028.
11. **Tuổi & chuyển đổi:** năm COD từng tổ ⇒ mốc 20 năm (chuyển đổi) và 40 năm (dừng nếu không chuyển đổi); nhà máy có trong **danh sách dự thảo dừng sau
    2030** không (§2b); phương án đồng đốt sinh khối/amoniac, capex, ai trả; **định giá phải dùng vòng đời HỮU HẠN**, không g_T vĩnh viễn.
12. **Thuế & ưu đãi:** ưu đãi TNDN đã hết chưa; thuế tài nguyên nước, phí BVMT; truy thu/thanh tra.
13. **Pháp lý/tranh chấp:** tranh chấp giá với EVN, khiếu nại quyết toán, vụ việc thanh tra (nếu có — chỉ WARNING theo luật user, không cổng chặn).
14. **Độ nhạy bắt buộc ghi số:** ±10% sản lượng; ±100 đ/kWh FMP trên phần vượt Qc; ±5pp tỷ lệ Qc; ±1% tỷ giá; bước giảm giá cố định sau trả nợ.

Định giá (nếu dùng): theo chỉ đạo user, r neo lãi huy động 12T (effective 7,4% hôm nay) + chiết khấu thanh khoản; dòng tiền tách **"giai đoạn PPA hiện
hành" / "sau trả nợ" / "sau mốc chuyển đổi"**; năm chu kỳ thuỷ văn xấu (2026-27) **không** được ngoại suy làm năm chuẩn [UĐ].

## 7. Tự kiểm & giới hạn
- **Tốt hơn tôi nghĩ:** chính sách đang quay lại ủng hộ than (5.300 MW mới đề xuất, miễn quy chuẩn tạm, NQ28 gia hạn) — rủi ro "đóng cửa sớm" tầm 36T
  thấp hơn đọc nền PDP8.
- **Xấu hơn / chưa biết:** không có tỷ lệ Qc than, FMP gần đây, khung giá than lớn 2026 (2 số mâu thuẫn), giá than cho điện; quy tắc 20/40 năm chỉ ở mức
  báo chí; danh sách dừng sau 2030 là dự thảo 2025. Snapshot vĩ mô UNVERIFIED, không vintage.
- **Blind:** xem §0 — danh tính có thể đã bị nhận ra qua tên thư mục; mọi số trong file là cấp ngành/hệ thống, không có số DN.

## Nguồn (một số URL có tên DN/tổ chức — người đọc blind sau có thể bỏ qua)
- BQ `tav2_bq.commodity_prices` (TE `coal`, `brent` daily), truy vấn 2026-11-17; `deposit_rate_vn` / `cctg_rate_vn` PIT 2026-11-17.
- Snapshot: `agents/Taylor/research/dd_QTP_20261117/macro_snapshot_20261117.md` (as-of 2026-11-17).
- VietnamPlus, "BCT đưa ra 8 nhóm giải pháp bảo đảm cung ứng điện 2027-2028" — 07/11/2026: https://www.vietnamplus.vn/bo-cong-thuong-dua-ra-8-nhom-giai-phap-bao-dam-cung-ung-dien-nam-2027-2028-post1146854.vnp
- Việt Nam News, "Government pushes coal-fired power to meet rising electricity demand" — 07/11/2026: https://vietnamnews.vn/economy/1803645/government-pushes-coal-fired-power-to-meet-rising-electricity-demand.html
- VietnamPlus, "BCT phê duyệt khung giá phát điện nhiệt điện than dưới 200 MW" (QĐ 2887/QĐ-BCT 30/10/2026) — 03/11/2026: https://www.vietnamplus.vn/bo-cong-thuong-phe-duyet-khung-gia-phat-dien-nhiet-dien-than-duoi-200-mw-post1145795.vnp ; moit: https://moit.gov.vn/van-ban-phap-luat/quyet-dinh-phe-duyet-khung-gia-phat-dien-nam-2026-doi-voi-loai-hinh-nha-may-nhiet-dien-than-do-doanh-nghiep-nha-nuoc-nam.html
- Tạp chí Công Thương, "Chủ động mọi kịch bản, bảo đảm đủ điện năm 2027" — 28/07/2026: https://tapchicongthuong.vn/bo-truong-bo-cong-thuong-le-manh-hung--chu-dong-moi-kich-ban--bao-dam-du-dien-nam-2027-537682.htm
- CafeF (Tiền Phong), "Chi hơn 7,3 tỷ USD nhập khẩu than…" — 27/10/2026: https://cafef.vn/chi-hon-73-ty-usd-nhap-khau-than-ap-luc-nhien-lieu-cho-nganh-dien-188261027071236886.chn
- Tuổi Trẻ, "Lãi hợp nhất 51.881 tỉ nhưng còn 17.500 tỉ chênh lệch tỉ giá chưa phân bổ" — 11/06/2026: https://tuoitre.vn/phat-dien.html
- VnEconomy, "Thiếu cơ chế để chuyển nhiệt điện than sang điện sạch" (quy tắc 20/40 năm): https://vneconomy.vn/thieu-co-che-de-chuyen-nhiet-dien-than-sang-dien-sach.htm
- PDP8 điều chỉnh QĐ 768/QĐ-TTg 15/04/2025: https://moit.gov.vn/tin-tuc/phat-trien-nang-luong/chinh-thuc-phe-duyet-quy-hoach-dien-viii-dieu-chinh.html ; https://tapchicongthuong.vn/hoi-dong-tham-dinh-nhat-tri-thong-qua-de-an-dieu-chinh-quy-hoach-dien-viii-133322.htm
- Carbon: VietnamFinance "Phân bổ 268 triệu tấn CO₂ cho 110 cơ sở": https://vietnamfinance.vn/cap-han-ngach-phat-thai-khi-nha-kinh-phan-bo-268-trieu-tan-co-cho-110-co-so-d140013.html ; sàn 29/06/2026: https://vietnamfinance.vn/511-trieu-tan-co2e-duoc-giao-dich-tren-san-carbon-vao-ngay-29-6-d146592.html
- Luật Điện lực sửa đổi, thảo luận 20/10/2026: https://vcci.com.vn/tin-tuc/dai-bieu-quoc-hoi-cho-y-kien-ve-du-an-luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-dien-luc ; https://moit.gov.vn/tin-tuc/bo-truong-bo-cong-thuong-le-manh-hung-trinh-bay-to-trinh-du-an-luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-dien-luc.html
- El Niño: VnEconomy "Hai kịch bản rủi ro El Niño 2026-2027": https://vneconomy.vn/hai-kich-ban-rui-ro-va-tac-dong-do-el-nino-2026-2027-tai-viet-nam.htm ; MAE "Ba kịch bản nguồn nước": https://mae.gov.vn/ba-kich-ban-nguon-nuoc-ung-pho-voi-el-nino-22518.htm
- Thị trường điện: TT 29/2026/TT-BCT: https://luatvietnam.vn/dien-luc/thong-tu-29-2026-tt-bct-quy-dinh-van-hanh-thi-truong-ban-buon-dien-canh-tranh-436583-d1.html ; FMP Q1/2026: https://vneconomy.vn/ap-luc-chi-phi-mua-dien-dau-vao-tang-tu-quy-22026.htm
- Hợp đồng than 2027 (minh hoạ thời điểm): https://tapchicongthuong.vn/nhiet-dien-vinh-tan-4-chu-dong-chuan-bi-cho-ke-hoach-phat-dien-nam-2027-547300.htm
