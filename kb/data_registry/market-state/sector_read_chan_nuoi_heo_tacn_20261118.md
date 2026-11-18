---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-18. KHÔNG biết giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp chăn nuôi/TACN cụ thể (xem §0 về rò rỉ danh tính).
blind: YES
as_of: 2026-11-18 (snapshot vĩ mô gần nhất có sẵn = 2026-11-17, xem §0; BQ commodity_prices tới 2026-11-17; lãi suất PIT tới 2026-11-16; tin web ≤ 2026-11-12, cộng tiêu đề tin 16-18/11)
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành chăn nuôi heo (heo giống + heo thịt) + sản xuất thức ăn chăn nuôi (TACN) VN, chế biến thịt heo ở mức phụ. Gồm pipeline cầu (tiêu dùng, nhập khẩu thịt, ASF/vaccine, nguyên liệu ngô/đậu tương/cám), cấu trúc cạnh tranh, chu kỳ giá heo hơi + biên TACN, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED 2 tầm, FORECAST khoá trước có ngày chấm, checklist DD.
---

# SECTOR READ: Chăn nuôi heo + TACN Việt Nam, as-of 18/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn: **[DK]** dữ kiện có nguồn + ngày; **[UĐ]** ước đoán /
suy luận của Bobby; **[NỀN]** hiểu biết nền chưa kiểm lại trong lượt này (phải KIỂM trước khi dùng làm số).
File chị em: `sector_read_phan_dam_ure_20261104.md` / `sector_read_fertilizer_dap_20261028.md` (cú sốc vận tải Hormuz lên đầu vào nông nghiệp).

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Snapshot:** caller chỉ định `agents/Taylor/research/dd_DBC_20261118/macro_snapshot_20261118.md`, nhưng **file đó KHÔNG tồn tại** lúc tôi
  đọc (thư mục chỉ có `src/`). Tôi **không mở `src/`**. Dùng snapshot gần nhất cùng pipeline:
  `agents/Taylor/research/dd_VCB_20261117/macro_snapshot_20261117.md` (as-of 17/11, giống hệt byte với bản dd_QTP). Chênh 1 ngày, không có chỉ báo
  nào trong snapshot có ngày quan sát 17-18/11 ngoài FX/lợi suất ⇒ tác động không đáng kể. **Báo cho Taylor: snapshot 18/11 chưa được sinh.**
- **Rò rỉ danh tính (ghi trung thực):** tên thư mục dispatch chứa một chuỗi giống mã chứng khoán và tôi **nhận ra** nó có thể ứng với một tập đoàn
  3F (TACN–trại–thực phẩm) miền Bắc. Tôi không tra mã đó, không mở BCTC/BCTN/báo cáo CTCK/giá cổ phiếu nào. Kết quả tìm kiếm có trả về tiêu đề
  (KHÔNG mở): "[DN đó] báo lãi quý 3 giảm sâu vì giá lợn hơi suy yếu"; "Giá TACN tăng liên tục, lãnh đạo [DN đó] dự báo…"; bài quảng bá vaccine ASF
  của DN đó. Tiêu đề thứ nhất là thông tin về **kết quả quý đã công bố** của DN — tôi ghi nhận là đã thấy, và nó chỉ xác nhận điều cấp ngành đã có
  từ giá heo hơi; tôi **không** dùng nó để định nhãn. Một bài ngành (VnBusiness 07/07/2026) có nêu tên các DN lớn trong danh sách — dùng số liệu
  tổng ngành của bài, không dùng tên.
- **BQ (tự truy vấn 18/11):** `tav2_bq.commodity_prices` — TE `corn`, `soybeans`, `wheat`, `lean_hogs` (daily); WB CMO `corn`, `soybean_meal`
  (monthly); SunSirs `soybean_meal_cny`, `rapeseed_meal`, `live_hog_cny` (daily). Lãi suất PIT: `deposit_rate_vn.effective_deposit_rate('2026-11-18')`,
  `cctg_rate_vn.current_cctg_rate()`, `macro_killswitch_a_status()`. Không dùng `ticker_financial` (sẽ phải chọn DN ⇒ phá blind).
- **Không có số (ghi "không có số", không suy):** tổng đàn lợn cuối T10/2026 (chỉ có cuối T9); tổng đàn nái 2026 mới nhất (chỉ có "~2,5 tr đầu 2026");
  số ổ dịch ASF toàn quốc 2026 sau tháng 4; nhập khẩu thịt lợn 9-10T/2026 (chỉ có 7T); giá bán TACN niêm yết hiện hành từng loại (chỉ có giá bao T7);
  sản lượng TACN công nghiệp 2026; giá thành heo khép kín (chỉ có suy ra từ "lỗ ~1 tr/con"); giá heo giống/heo con; giá cám gạo/DDGS; tỷ lệ tiêm vaccine
  ASF trong nước; series giá heo hơi VN trong BQ (không có — ngành không có nguồn PIT máy đọc được).

## 1. Snapshot vĩ mô + chuỗi giá

| Chỉ báo | Giá trị | Δ | Đọc cho chăn nuôi heo / TACN |
|---|---|---|---|
| Bán lẻ YoY (danh nghĩa) | 14,7% (T10) | +0,2 / +7,5pp | Cầu tiêu dùng chung KHÔNG yếu ⇒ giá heo giảm là chuyện **cung**, không phải cầu vĩ mô |
| CPI YoY / lõi | 5,09% (T10) / 4,45% (T9) | +1,84pp 12T | Lạm phát cao nhưng **thịt lợn đang là lực kéo XUỐNG**: CPI thịt lợn T9 −0,96% MoM, **T10 −2,33% MoM** (GSO 28/10/2026) [DK] |
| GDP YoY | 9,95% (Q3) | +1,70pp 12T | Thu nhập tăng ⇒ cầu thịt nền tăng chậm, ổn định [UĐ] |
| USD/VND | 25.764 (16/11) | **−2,24% 12T** | VND lên giá ⇒ ngô/đậu nhập rẻ hơn ~2% quy VND; đồng thời thịt nhập rẻ hơn |
| Lương | 9,2 tr/tháng (T9) | +10% 12T | Chi phí nhân công trại tăng |
| CBOT ngô (TE, US¢/bu) | TB T11 MTD **444,4** (17/11: 449,7) | đỉnh **525,8 T9** ⇒ −15% từ đỉnh; **+3,0% YoY** (T11/2025 431,3) [DK, BQ] | Nguyên liệu chính (~55-60% công thức heo [NỀN]) đã hạ từ đỉnh |
| WB ngô (US Gulf, $/t) | 239,6 (T9) | +21,4% YoY (T9/2025 197,4) | Xác nhận đỉnh Q3/2026 |
| CBOT đậu tương (US¢/bu) | TB T11 MTD 1.208 (17/11: 1.235) | đỉnh 1.310 T9 ⇒ −8%; **+7,2% YoY** | |
| WB khô đậu tương ($/t) | **453 (T10)** | **+27% YoY** (T10/2025 356); T9 447 | Khô đậu ~20-25% công thức [NỀN] — ĐẮT nhất trong nhóm |
| Khô đậu TQ (SunSirs, CNY/t) | TB T11 MTD 3.191 (17/11: 3.152) | đỉnh 3.375 T9 ⇒ −5%; +3,6% YoY | Proxy khô đậu châu Á, phản ứng nhanh hơn WB |
| Lúa mì CBOT (US¢/bu) | TB T11 MTD 596 | đỉnh 721 T9 ⇒ −17%; +11% YoY | Thay thế ngô một phần |
| **Heo hơi TQ (SunSirs, CNY/kg)** | **9,02 TB T11 MTD** (17/11: 9,15) | **−24% YoY** (T11/2025 11,92); T1/2026 12,95 | TQ dư cung tệ nhất ~16 năm [DK VnBusiness 07/07/2026]; ≈ 34-35k đ/kg ⇒ **thấp hơn VN** ⇒ không còn lực hút xuất tiểu ngạch sang TQ, rủi ro chiều ngược |
| Lean hogs Mỹ (TE, US¢/lb) | TB T11 MTD 56,0 | **−30% YoY** (79,6); T7/2026 98,8 | Giá thịt heo toàn cầu đang giảm mạnh (lưu ý: cuộn hợp đồng kỳ hạn mùa đông có thể phóng đại mức giảm) [UĐ] |

**Chỉ số nguyên liệu TACN tự dựng (RMI)** [UĐ, dùng để chấm F7-F8]: `RMI = 0,6 × (CBOT ngô TB tháng / 501,5) + 0,4 × (khô đậu TQ CNY TB tháng / 3.357,1)`,
gốc = TB T9-T10/2026 = 1,00. **T11/2026 MTD = 0,912** (ngô 0,886; khô đậu 0,950) ⇒ chi phí nguyên liệu (giá giao ngay) đã hạ ~9% từ đỉnh Q3.
Có độ trễ tồn kho/hợp đồng ~2-4 tháng [NỀN] ⇒ hạ giá vào giá vốn TACN từ ~Q1/2027.

**Chi phí vốn, bảng 5 tầng** (ngành dùng vốn lưu động lớn: tồn kho nguyên liệu nhập + đàn nái + công nợ đại lý [NỀN]):
| Tầng | Proxy | Số | Ghi chú |
|---|---|---|---|
| A. Niêm yết hành chính | Big-4 12M (cao nhất online/quầy) | **6,8%** (16/11, đi ngang từ 03/10) | Tách online / tại quầy và kỳ 6M: **không có số** (series lưu MAX) |
| B. Bán hành chính | CCTG 12M Big-4 cao nhất | **7,4%** (đợt 02/11) | Spread CCTG − tiết kiệm 12M = **+0,6pp**; từng NH, sự kiện mở/rút kỳ hạn: không có số |
| C. Ngoài Big-4 | 12M NH tư nhân, lãi ẩn | không có số | |
| D. Thị trường | LNH 3M | **6,33%** (11/11; −1,19pp 3T, +0,03pp 12T) | OMO/tín phiếu, trúng thầu TPCP, USD tự do: không có số |
| D. | TPCP 10Y (chỉ tin Δ) | 4,57 (+0,00pp 3T / +0,57pp 12T) | |
| E. Lượng | Tín dụng vs huy động YTD, LDR | không có số trong lượt này | |

Đồng thuận/phân kỳ [UĐ]: **HƯỚNG** — A, B đi ngang; D ngắn hạn dịu mạnh (LNH 3M từ ~7,5% xuống 6,33%) ⇒ không proxy nào báo chi phí vốn VND tăng trong 3-6T.
**MỨC** — chi phí biên (CCTG 7,4%) cao hơn niêm yết ~0,6pp. Kill-switch A (>7,5%) **CLEAR** (7,4%, age 2 ngày). Với ngành này lãi vay là biến thứ yếu so với
giá heo và nguyên liệu; quan trọng hơn là **khả năng vay vốn lưu động của nông hộ/đại lý** (tầng C/E — không có số). Độ tin cậy trung bình.

## 2. Pipeline cầu & cung

### 2a. Chu kỳ giá heo hơi: từ đỉnh 80k (T1) xuống đáy 45-49k (cuối T10-giữa T11)
Đường giá 2026 [DK, tổng hợp từ tin ngày]: ~**80.000 đ/kg** nhiều tỉnh (25/01, cận Tết Bính Ngọ, "vượt đỉnh 2025") → giảm Q1 → hồi Q2 lên **67-68k** (miền
Bắc, 01/07; ~70k tháng 5) → dưới 70k từ đầu T6, 64-68k (07/07) → ~**60k** (T7; 31/08 chỉ còn 3 tỉnh đạt 60k) → bình quân cả nước **48k**, "thấp nhất từ
đầu năm" (VTV/cafef 23/10) → miền Bắc **46-48k** (26/10, −4-5k trong 1 tuần; Hà Tĩnh 45k thấp nhất cả nước) → miền Bắc 46-48k, cả nước 46-49k (10-15/11)
→ tiêu đề tin 16-18/11: cả nước 48-51k, Hà Nội 52k, vài tỉnh Bắc 53k (bật nhẹ). **Đỉnh→đáy ≈ −40%.**

**Đây là lần thứ hai liên tiếp cùng một hình dạng** [DK]: 2025 cũng mở năm >70k và rơi >40% về ~48-50k (Hà Nội 48k, 12/11/2025 — nhadautu 13/11/2025);
sau đó **ASF bùng ở nhiều địa phương T9/2025** + mùa Tết ⇒ bật lên ~80k T1/2026. Hệ quả: so cùng kỳ, giá T11/2026 ≈ **ngang** T11/2025; chỉ số giá sản phẩm chăn
nuôi lợn (PPI, GSO) 9T/2026 chỉ **+0,2% YoY**, Q3 +0,7% [DK, GSO 12/10/2026]. ⇒ mặt bằng giá "trung bình năm" 2026 không sụp; cái sụp là **biên** (giá
đầu ra mùa thấp điểm trùng chi phí TACN đỉnh).

### 2b. Cung trong nước: tái đàn mạnh trên nền thấp
- Tổng đàn lợn cuối T9/2026 **+5,4% YoY**; thịt lợn hơi 9T **4,28 tr tấn, +4,4%**; Q3 1,339 tr tấn **+2%** [DK, GSO 12/10/2026; VnEconomy]. GSO tự ghi:
  tăng trên nền thấp do ASF T9/2025 tiêu huỷ nhiều. Cuối T10: **không có số**.
- Đàn nái ~**2,5 tr con** (đầu 2026); 29 DN lớn giữ ~9,58 tr con (**30,5%** tổng đàn), gần 1 tr nái (**31,8%**), xuất chuồng 25,74 tr con năm 2025 (**44,4%**
  sản lượng); chăn nuôi nông hộ còn ~30% sản lượng, mất 15-20pp trong 5 năm [DK, VnBusiness 07/07/2026]. Tăng trưởng đàn chủ yếu từ **trại quy mô lớn mới**,
  "nhiều địa phương và DN cùng đầu tư khi giá còn cao" ⇒ cảnh báo lặp kịch bản dư cung TQ [DK, cùng nguồn].
- BNNMT: sản lượng thịt lợn cả năm ~5 tr tấn; dự kiến nguồn cung cuối năm tăng 20-30% so cùng kỳ (theo tái đàn); "giá khó tăng đột biến đến cuối 2026" [DK,
  trích qua VnBusiness ~T10-11/2026; con số 20-30% là của Bộ, tôi coi là ước lượng chính sách, không phải số thống kê].

### 2c. Nhập khẩu thịt: lực ép biên giá, không phải nguồn cung chính
- 7T/2026: **112.090 tấn** thịt lợn tươi/ướp lạnh/đông lạnh, **+27,1% lượng, −20,9% giá trị** ⇒ đơn giá nhập ~**1.655 USD/t, ≈ −38% YoY** [DK, Hải quan qua
  VietnamNews/Vietstock T9/2026]. 4T chỉ 43,1k t (−3,6%) ⇒ tăng tốc từ T5-T7 [DK, VnBusiness 07/07]. Q2/2026 riêng nhóm thịt 271,1k t (+21,5% QoQ) [DK, Porcinews].
  8T nhóm thịt +26,3% kim ngạch [DK, Hải quan 09/2026]. Nguồn chính: Nga (miễn thuế), Tây Ban Nha, Brazil; thịt nhập rẻ hơn nội 30-40%; giá heo hơi Brazil ≈ ½ VN.
- Quy mô [UĐ]: ~190k t/năm thịt lợn nhập ≈ 4-5% cung thịt xẻ (5 tr t hơi × ~0,75) — nhỏ về lượng nhưng **đặt giá trần** cho kênh chế biến, bếp ăn, HoReCa.
- Chính sách thương mại: Nga 0%, CPTPP (Canada…) 0%; Mỹ đang được hứa giảm thuế trong thoả thuận thương mại 2025 (chi tiết chưa công bố) [DK, tổng hợp
  farms.com/feedstuffs 2025]. Không thấy thay đổi thuế MFN 2026 [DK: không tìm thấy]. Không có rào cản hành chính mới nào đang được đề xuất [UĐ: không tìm thấy].
- Biên giới TQ: giá TQ (~34-35k đ/kg) **thấp hơn** VN (~48k) ⇒ dòng heo tiểu ngạch Việt→TQ (lực đỡ giá miền Bắc 2019-2021) đã đảo; rủi ro thịt/heo lậu chiều
  ngược. Bắt giữ 2026 chỉ thấy quy mô nhỏ (chân giò, xúc xích đông lạnh) [DK, Hải quan Lạng Sơn T1/2026]; **không có số** về heo sống lậu.

### 2d. ASF và vaccine: công tắc cung lớn nhất, hai chiều
- 2026: ~**401 ổ dịch / 321 xã / 25 tỉnh** tính tới ~T4 [DK, văn bản UBND Huế T4/2026]; tiếp diễn T10-11: Lào Cai 418 hộ/36 xã (12/10), Đồng Nai 78 ổ/44 xã
  (cuối T10), Thanh Hoá 26 xã, 8.585 con (05/11), Nghệ An >30 ổ, Đắk Lắk, An Giang [DK, báo địa phương]. Số toàn quốc mới nhất: **không có số**.
- Vaccine: 3 vaccine ASF được cấp phép trong nước; đã dùng ~6 tr liều một sản phẩm (1 tr liều xuất khẩu); Philippines lùi chứng nhận thương mại từ Q1 sang
  sớm nhất Q3/2026; **chủng tái tổ hợp genotype I/II** từ cuối 2023 làm giảm độ tin bảo hộ, vaccine thế hệ mới dự kiến đăng ký 2026; tiêm trong nước còn
  khó ("xuất khẩu thành công, vaccine vẫn khó vào trại lợn Việt") [DK, Lao Động/MAE/foodbusinessmea 2025-2026]. Tỷ lệ tiêm: **không có số**.
- Đọc [UĐ]: ASF là **cú sốc cung ngẫu nhiên** — dịch lớn ⇒ nông hộ mất đàn, giá bật (đúng mẫu T9/2025→T1/2026). Trại lớn an toàn sinh học **hưởng lợi giá**
  nhưng chịu rủi ro đuôi nếu dịch lọt vào trại nái. Không có cơ chế chính sách nào "giải quyết" ASF trong 12-36T.

### 2e. Cầu tiêu dùng
Thịt heo ~65-70% tiêu dùng thịt [NỀN]; cầu theo thu nhập + mùa (Tết Đinh Mùi **06/02/2027** [NỀN] ⇒ đỉnh cầu T12/2026-T1/2027; thấp điểm sau Tết T2-T4).
GSO nêu nguyên nhân CPI thịt lợn giảm T10: "cung tăng trong khi sức tiêu thụ chưa tương ứng + thịt nhập giá thấp" [DK]. Gia cầm cũng tăng đàn (+3,1%) và giá gà
chạm đáy [DK, avinews] ⇒ không có lực thay thế đẩy cầu sang heo. Cầu vĩ mô (bán lẻ +14,7%) không phải vấn đề [UĐ].

### 2f. Nguyên liệu TACN và giá bán TACN
- VN chỉ tự chủ ~**37%** nguyên liệu TACN [DK, mekongasean]; 4T/2026 nhập 4,44 tr t ngô (+42,7% kim ngạch); >2,6 tỷ USD ngô+lúa mì+đậu tương [DK].
- Giá TACN 2026: **6 lần tăng, 1 lần giảm**, cộng dồn ~**+1.000-1.200 đ/kg** (VnBusiness 26/10) — đợt tăng gần nhất 01/10/2026, phổ biến +300-400 đ/kg
  ("lần thứ 7"), đầu T9 +200 đ/kg; T3-T4 +200-320; T8 +160-200; giảm 200 đ/kg đầu T7 [DK, avinews/DĐDN/mekongasean, đoạn trích]. Bao cám heo thịt
  360-380k/25kg (~14,4-15,2k đ/kg) T7 [DK, TBTCVN 01/07]. Hộ 1.000 con: chi phí cám 715→850 tr/tháng (+19% YoY) cho cùng 65 tấn [DK, VTV 23/10].
- BNNMT (T7) dự báo TACN +3-5% H2/2026 — **đã xảy ra** (2 đợt tăng T9-T10) [DK]. Chưa thấy đợt giảm giá nào T11/2026 [DK: không tìm thấy].
- Đọc biên TACN [UĐ]: Q3/2026 nhà TACN chịu nguyên liệu đỉnh (WB khô đậu +27% YoY, ngô +21%), chuyển giá chậm 1 nhịp ⇒ biên gộp **bị ép Q3**, phục hồi
  dần sau 2 đợt tăng T9-T10. Từ T11 nguyên liệu giao ngay hạ ~9% (RMI 0,912) trong khi giá bán chưa giảm ⇒ **biên TACN mở ra Q1-Q2/2027** (mẫu "nguyên liệu
  hạ nhiệt, TACN vẫn đứng giá" đã thấy T12/2025 — Tuổi Trẻ 12/12/2025). Ngược lại, **sản lượng** TACN bán ra có rủi ro giảm nếu nông hộ giảm đàn vì lỗ; và áp lực
  dư luận/BNNMT đòi giảm giá khi người nuôi lỗ.

## 3. Cấu trúc cạnh tranh
- **TACN** [NỀN — kiểm trước khi dùng]: sản lượng TACN công nghiệp ~20+ tr t/năm; khối FDI (Thái, Hà Lan, Mỹ, TQ, Indonesia…) chiếm đa số thị phần (~60%+),
  DN nội lớn chiếm phần còn lại; ngành phân mảnh ở đuôi (~200+ nhà máy). Lợi thế quy mô ở thu mua nguyên liệu nhập (tàu lớn, hợp đồng kỳ hạn, phòng ngừa giá),
  logistics cảng nước sâu, hệ thống đại lý/công nợ. Cạnh tranh giá dữ dội; chuyển giá theo đợt thông báo đồng loạt (6-7 lần/năm 2026) ⇒ hành vi "người dẫn giá"
  của các hãng FDI lớn [UĐ].
- **Tích hợp dọc 3F** (feed–farm–food): xu hướng chủ đạo; DN lớn giữ 31,8% nái, 44,4% sản lượng 2025, tăng nhanh [DK]. TACN nội bộ cho trại riêng = sản lượng
  ổn định nhưng chuyển rủi ro giá heo lên cả chuỗi (biên TACN và biên trại **ngược pha**: nguyên liệu rẻ thường đi cùng dư cung heo toàn cầu) [UĐ].
- **Chăn nuôi gia công** (trại thuê): DN chịu rủi ro giá, nông hộ nhận phí ⇒ lỗ ít hơn nông hộ tự do khi giá đáy [DK, VTV 23/10: "trại gia công lỗ ít hơn"].
- **Chế biến** (mức phụ): thịt mát/thịt chế biến có biên ổn định hơn, hưởng lợi khi heo hơi rẻ nhưng cạnh tranh trực tiếp với thịt nhập đông lạnh giá rẻ
  (−38% YoY đơn giá) [UĐ].
- **Giá thành** [UĐ, suy luận]: ở 48k nông hộ mua giống lỗ ~1 tr/con (VTV) ⇒ giá thành nông hộ mua giống ~57-60k/kg; trại khép kín có nái riêng, FCR tốt hơn ⇒ giá
  thành ước **~48-55k/kg** (không có số công bố). ⇒ giá hiện tại ≈ **hoà vốn/lỗ nhẹ cho khối tích hợp, lỗ rõ cho nông hộ**. Tỷ lệ giá heo/giá cám ≈ 48/14,8 ≈ 3,2
  — thấp [UĐ; ngưỡng hoà vốn nông hộ không có số công bố].

## 4. Phân loại (2 trục + 3 nhãn)
**Trục 1 — nguyên nhân gốc của suy giảm biên hiện tại:** (i) **chu kỳ cung nội địa** — tái đàn sau ASF 2025 + đầu tư trại lớn khi giá cao đầu 2026 (đàn +5,4%);
(ii) **cú sốc chi phí ngoại sinh** — ngô/khô đậu đỉnh Q3/2026 (vận tải Hormuz/Biển Đỏ + giá thế giới), đã bắt đầu hạ; (iii) **giảm phát thịt heo toàn cầu** —
TQ dư cung 16 năm, Mỹ −30%, Brazil ½ giá VN ⇒ thịt nhập rẻ −38%. **Không phải** cầu vĩ mô yếu hay mất cân đối tiền tệ trong nước (bán lẻ +14,7%, CPI chung tăng).
**Trục 2 — containable?** Không có MỘT hành động chính sách nào giải quyết. Phần nội địa tự sửa qua cơ chế chu kỳ (lỗ ⇒ loại nái ⇒ giảm cung sau ~10-12 tháng:
phối giống→xuất chuồng ≈ 114 ngày mang thai + ~6 tháng nuôi [NỀN]). Phần toàn cầu (TQ dư cung) **không theo lịch VN**; TQ đang ép giảm công suất nhưng chưa phá
được chu kỳ [DK, VnBusiness 07/07]. Công tắc ASF có thể rút ngắn chu kỳ bất kỳ lúc nào (ngẫu nhiên).

**Nhãn driver lợi nhuận/giá trị của DN chăn nuôi heo + TACN tích hợp** (xác suất = trọng số "driver CHÍNH", tổng = 1):
| Tầm | CYCLICAL | STRUCTURAL | ADMIN_GATED | Diễn giải |
|---|---|---|---|---|
| **12 tháng** | **0,65** | 0,25 | 0,10 | Lợi nhuận do giá heo hơi (chu kỳ cung + mùa Tết + ASF) và chênh nguyên liệu–giá TACN (hàng hoá toàn cầu). Structural = dịch chuyển thị phần về trại lớn + áp lực thịt nhập dài hạn. Admin = bình ổn giá, thuế/SPS nhập khẩu, quy định môi trường trại — chưa có văn bản nào đang treo đổi được biên 12T |
| **36 tháng** | 0,40 | **0,45** | 0,15 | Structural chiếm ưu thế: (a) tập trung hoá (nông hộ 30% và giảm) ⇒ DN lớn hưởng thị phần nhưng cũng tự tạo dư cung; (b) thịt nhập từ FTA (CPTPP/EVFTA/Nga, có thể Mỹ) đặt trần giá dài hạn; (c) ASF thành đặc hữu + vaccine chưa chắc ⇒ phần bù an toàn sinh học; (d) phụ thuộc 63% nguyên liệu nhập. Admin = cấp phép vaccine, SPS, môi trường/khoảng cách trại [NỀN: Luật Chăn nuôi 2018 + lộ trình di dời trại trong khu dân cư] |

**Độ tin cậy: CLEAN-leaning (~65/35) cho 12T CYCLICAL**; 36T **AMBIGUOUS ~55/45** giữa STRUCTURAL và CYCLICAL.
**Pha [UĐ]:** giá heo hơi ở **đáy mùa + đáy chu kỳ ngắn** (cuối T10-giữa T11), bật theo mùa Tết là gần chắc; nhưng **đàn chưa giảm** (T9 +5,4%) nên nhịp bật
sau Tết có thể yếu (khác 2025-26, khi ASF T9/2025 cắt cung). Nguyên liệu TACN **vừa qua đỉnh** (T9) ⇒ biên TACN ở giai đoạn **mở** trong 2-3 quý tới nếu giá
bán dính. Khối tích hợp: biên trại ở đáy, biên TACN đang lên ⇒ hai mảng bù trừ một phần.

**Falsifiers (sẽ đổi nhãn/pha):** (i) GSO tổng đàn cuối T12/2026 hoặc T3/2027 vẫn ≥ +4% YoY ⇒ chu kỳ chưa tự sửa, đáy kéo dài (giá Q2/2027 dưới 55k); (ii) ASF bùng
diện rộng Q4/2026-Q1/2027 (≥ mức T9/2025) ⇒ giá bật mạnh sớm, CYCLICAL tăng; (iii) ngô CBOT quay lại >500 hoặc khô đậu WB >470 ⇒ biên TACN bị ép lại; (iv) có văn
bản hạn chế nhập khẩu thịt (SPS/hạn ngạch) hoặc ngược lại thuế thịt Mỹ về 0 có hiệu lực ⇒ ADMIN tăng; (v) giá heo TQ vượt ~12 CNY/kg ⇒ dòng xuất tiểu ngạch
trở lại, đỡ giá miền Bắc.

## 5. FORECAST khoá trước (2026-11-18)
Bobby không tự chấm. **Nguồn giá heo hơi VN không có series PIT máy đọc** ⇒ quy ước chấm giá miền Bắc: lấy **trung điểm dải "miền Bắc phổ biến"** trong bản tin
"Giá lợn hơi hôm nay" của báo điện tử (ưu tiên baolaocai.vn; dự phòng VnBusiness/Báo Văn hoá), trung bình **mọi ngày có tin trong tháng** (≥10 ngày; ít hơn ⇒
"không chấm được"). Ví dụ gốc: 12/11/2026 "46.000-48.000" ⇒ 47.000. Mốc tham chiếu as-of: **TB miền Bắc T11/2026 (1-15/11) ≈ 47.000 đ/kg**.

Base case đường giá miền Bắc [UĐ, không phải mệnh đề chấm]: T12/2026 **52-57k** · T1/2027 (trước Tết 06/02) **56-62k** · T3/2027 **50-56k** · T5/2027 **54-60k** ·
T11/2027 **52-62k** (đáy mùa nhưng đàn đã co một phần).

| # | Mệnh đề | P | Ngày chấm | Nguồn chấm |
|---|---|---|---|---|
| F1 | TB giá heo hơi miền Bắc **T1/2027 ≥ 55.000 đ/kg** | 0,65 | 2027-02-05 | Quy ước trên |
| F2 | TB miền Bắc **T1/2027 ≥ 65.000 đ/kg** (lặp đỉnh kiểu T1/2026 cần cú sốc cung) | 0,20 | 2027-02-05 | Quy ước trên |
| F3 | **6 tháng**: TB miền Bắc **T5/2027 ≥ 55.000 đ/kg** | 0,55 | 2027-06-05 | Quy ước trên |
| F4 | **6 tháng**: TB miền Bắc **T5/2027 trong [48.000; 65.000]** | 0,80 | 2027-06-05 | Quy ước trên |
| F5 | **12 tháng**: TB miền Bắc **T11/2027 > TB T11/2026 (47.000) + 5.000 = 52.000 đ/kg** | 0,55 | 2027-12-05 | Quy ước trên |
| F6 | CPI thịt lợn (GSO) **T11/2026 MoM < 0** (TB T11 ~47-50k vs T10 ~50-52k) | 0,65 | 2026-12-10 | GSO thông cáo CPI T11 |
| F7 | CPI thịt lợn (GSO) **T1/2027 MoM > 0** | 0,75 | 2027-02-10 | GSO thông cáo CPI T1 |
| F8 | GSO tổng đàn lợn **cuối T3/2027 ≤ +3,0% YoY** (cuối T9/2026 +5,4%) | 0,55 | 2027-04-15 | GSO báo cáo KT-XH Q1/2027 |
| F9 | GSO tổng đàn lợn **cuối T9/2027 ≤ +1,0% YoY** (chu kỳ tự sửa) | 0,50 | 2027-10-15 | GSO báo cáo KT-XH 9T/2027 |
| F10 | **Biên TACN 6T — nguyên liệu**: RMI TB **T3-T4/2027 ≤ 0,95** (T11 MTD 0,912) | 0,60 | 2027-05-05 | BQ `commodity_prices` TE `corn` + SunSirs `soybean_meal_cny` daily, công thức §1 |
| F11 | **Biên TACN 6T — giá bán dính**: từ 18/11/2026 đến 31/03/2027 **có ≥1 đợt giảm giá TACN heo được báo chí đưa là "đồng loạt"/nhiều DN lớn**, mức ≥100 đ/kg | 0,55 | 2027-04-05 | Báo ngành (avinews, VnBusiness, Nông nghiệp & Môi trường) |
| F12 | **Biên TACN 12T**: RMI TB **T10-T11/2027 ≤ 1,00** (không quay lại đỉnh Q3/2026) | 0,65 | 2027-12-05 | BQ, công thức §1 |
| F13 | WB khô đậu tương **T4/2027 < 453 $/t** (T10/2026) | 0,60 | 2027-05-15 | BQ `commodity_prices` WB CMO `soybean_meal` monthly |
| F14 | Nhập khẩu thịt lợn (tươi/ướp lạnh/đông lạnh) **cả năm 2026 ≥ +15% lượng YoY** (7T +27,1%) | 0,70 | 2027-02-28 | Hải quan / Bộ Công Thương tổng kết 2026 |
| F15 | Heo hơi TQ (SunSirs `live_hog_cny`) **TB T5/2027 > 10,0 CNY/kg** (T11 MTD 9,02) | 0,40 | 2027-06-05 | BQ `commodity_prices` |
| F16 | Có văn bản cấp Bộ/Chính phủ **hạn chế nhập khẩu thịt lợn** (hạn ngạch, tạm dừng, tăng thuế) ban hành trước 2027-11-18 | 0,10 | 2027-11-18 | Cổng Chính phủ / BNNMT / BCT |

**Xu hướng biên TACN (mệnh đề hướng, đọc kèm F10-F13)** [UĐ]: **6T (tới ~T5/2027): MỞ RỘNG** (nguyên liệu −5-10% so đỉnh, giá bán dính, VND không yếu) — độ tin
~0,60; rủi ro chính là sản lượng giảm và áp lực giảm giá. **12T (tới ~T11/2027): TRUNG TÍNH / hồi về trung bình** — biên đã mở phần lớn trong H1/2027, sau đó cạnh
tranh giá và vụ mùa Mỹ/Nam Mỹ 2027 quyết; ~0,55 không ép lại về mức Q3/2026.

Lập luận [UĐ]: F1 — Tết luôn đẩy giá; ngay cả đầu 2025 (không có cú sốc) cũng >70k; nhưng đàn 2026 dồi dào + thịt nhập rẻ ⇒ 55-62k. F2 thấp vì T1/2026 80k có ASF T9/2025
làm nền. F3/F5 ~0,55: chu kỳ cần ≥2 quý lỗ để loại nái; Q4 lỗ, Tết cứu giá, nên loại nái có thể bị hoãn ⇒ tự sửa chậm. F8/F9: nền T3/2026 và T9/2026 đã cao (đàn tái
lập) ⇒ YoY phải co lại cơ học; F9 0,50 vì DN lớn ít giảm đàn hơn nông hộ. F10/F13: ngô và khô đậu đã rời đỉnh T9, vụ Nam Mỹ T2-T5 thường ép giá; đuôi xấu = vận tải
Hormuz + El Niño. F15: TQ đang ép giảm công suất nhưng 2026 chưa thành.

## 6. DD cần kiểm gì — DN chăn nuôi heo + TACN (tích hợp 3F) niêm yết
1. **Tách lợi nhuận theo mảng**: TACN thương mại / TACN nội bộ / heo giống / heo thịt / chế biến / mảng khác (BĐS, gà, trứng…). Doanh thu nội bộ loại trừ ra sao.
   Lợi nhuận một quý xấu/tốt là do mảng nào — **không** suy cả chuỗi từ giá heo.
2. **Đàn nái & năng lực**: số nái (cụ, hậu bị), số heo thịt xuất chuồng/năm, PSY (heo cai sữa/nái/năm), FCR, tỷ lệ chết; **kế hoạch mở trại mới 2026-2028** (DN có
   đang là một phần của làn sóng "cùng đầu tư khi giá cao" không). Capex và ngày vận hành từng trại.
3. **Giá thành heo hơi/kg** (khép kín vs gia công vs mua giống), so với giá bán thực tế bình quân từng quý; độ nhạy **±5.000 đ/kg giá heo ⇒ ±? lợi nhuận**.
4. **ASF**: lịch sử ổ dịch trong trại DN (2019-2026), tổn thất, chính sách bảo hiểm/dự phòng; an toàn sinh học từng trại; **sở hữu/quyền vaccine** — doanh thu vaccine
   thật (trong nước vs xuất khẩu), giấy phép, chứng nhận nước nhập (Philippines lùi lịch), hiệu lực với chủng tái tổ hợp I/II; tránh định giá vaccine theo kịch bản PR.
5. **TACN**: sản lượng bán ngoài (tấn) theo quý và xu hướng; cơ cấu heo/gia cầm/thuỷ sản; **thị phần vùng**; chính sách công nợ đại lý (DSO, nợ xấu đại lý khi nông
   hộ lỗ); lịch điều chỉnh giá bán 2026 so với các hãng FDI dẫn giá.
6. **Nguyên liệu**: tồn kho ngày (ngô, khô đậu, lúa mì) cuối quý; hợp đồng kỳ hạn/giá chốt; độ trễ giá vốn vs RMI; nguồn nhập (Mỹ/Brazil/Argentina); phòng ngừa giá
   và tỷ giá; độ nhạy **±10% ngô / ±10% khô đậu ⇒ ±? biên gộp TACN**.
7. **Vốn lưu động & nợ**: vay ngắn hạn tài trợ tồn kho, lãi suất thực trả (so CCTG 7,4% / LNH 3M 6,33%), nợ USD (nếu có); tài sản sinh học (đàn) và **phương pháp ghi
   nhận/đánh giá lại** — dự phòng giảm giá hàng tồn kho/tài sản sinh học khi giá heo đáy (đã trích chưa, trích đủ chưa).
8. **Chế biến**: công suất giết mổ/chế biến thực dùng, kênh bán (siêu thị, xuất khẩu), biên, cạnh tranh với thịt nhập đông lạnh.
9. **Môi trường & pháp lý trại**: giấy phép môi trường, khoảng cách khu dân cư, xử lý chất thải; lộ trình di dời (nếu có); vi phạm/xử phạt — chỉ WARNING theo luật user.
10. **Mảng ngoài ngành** (nếu tập đoàn đa ngành): BĐS/khác chiếm bao nhiêu lợi nhuận và tài sản; không để nó che hay thổi biên ngành chính.
11. **Cổ tức, phát hành, tăng vốn** trong chu kỳ đầu tư trại (theo luật user: bất kỳ tăng vốn nào ⇒ WARNING).
12. **Định giá (nếu dùng)**: theo chỉ đạo user r neo lãi huy động 12T (effective **7,4%** hôm nay) + chiết khấu thanh khoản; **không ngoại suy** năm đỉnh giá heo (đầu 2026)
    hay năm đáy (Q4/2026) làm năm chuẩn — dùng lợi nhuận **trung bình chu kỳ** (≥1 chu kỳ đầy đủ ~3-4 năm [NỀN]) cho mảng heo; mảng TACN dùng biên/tấn trung bình nhiều
    năm; vaccine định giá riêng, có xác suất.

## 7. Tự kiểm & giới hạn
- **Tốt hơn tôi nghĩ:** mặt bằng giá trung bình năm không sụp (PPI heo 9T +0,2% YoY); nguyên liệu đã qua đỉnh; VND lên giá; cầu vĩ mô mạnh; Tết gần.
- **Xấu hơn / chưa biết:** đàn T9 +5,4% và DN lớn tiếp tục mở trại; giảm phát heo toàn cầu (TQ, Mỹ, Brazil) làm thịt nhập rẻ kéo dài; không có số đàn nái, giá thành
  công bố, sản lượng TACN, ASF toàn quốc sau T4. Giá heo hơi VN không có nguồn PIT máy đọc ⇒ forecast giá phụ thuộc quy ước bản tin báo chí (nhiễu: cùng ngày 11/11 có
  một nguồn báo 64k miền Bắc trái hẳn các nguồn khác — tôi loại là sai nguồn/sai ngày).
- **Blind:** xem §0 — danh tính có thể đã bị nhận ra qua tên thư mục; thấy (không mở) tiêu đề KQKD quý 3 của một DN; mọi số trong file là cấp ngành/hệ thống.

## Nguồn (một số URL có tên DN — người đọc blind sau có thể bỏ qua)
- BQ `tav2_bq.commodity_prices` (TE corn/soybeans/wheat/lean_hogs daily; WB CMO corn, soybean_meal monthly; SunSirs soybean_meal_cny, rapeseed_meal, live_hog_cny daily), truy vấn 2026-11-18; `deposit_rate_vn` / `cctg_rate_vn` PIT 2026-11-18.
- Snapshot: `agents/Taylor/research/dd_VCB_20261117/macro_snapshot_20261117.md` (as-of 2026-11-17; thay cho file 20261118 không tồn tại).
- GSO, "Phát triển ngành chăn nuôi 9 tháng năm 2026…" — 12/10/2026: https://www.nso.gov.vn/?p=62691
- GSO CPI T10/2026 (thịt lợn −2,33% MoM) — 28/10/2026: https://www.nso.gov.vn/wp-content/uploads/2026/11/CPI-chi-so-gia-vang-va-chi-so-gia-do-la-My-thang-Muoi-va-10-thang-nam-2026.pdf ; https://baodauthau.vn/10-thang-dau-nam-2026-cpi-tang-457-post211700.html
- VnEconomy, sản xuất nông nghiệp Q3/2026: https://vneconomy.vn/san-xuat-nong-nghiep-vuot-qua-thien-tai-duy-tri-san-luong.htm
- Báo Lào Cai, "Giá lợn hơi hôm nay 12/11" — 12/11/2026: https://baolaocai.vn/gia-lon-hoi-hom-nay-1211-mien-bac-pho-bien-47000-48000-dongkg-post914254.html ; 10/11: https://baolaocai.vn/gia-lon-hoi-hom-nay-1011-mien-bac-pho-bien-46000-48000-dongkg-post914073.html
- VnBusiness, "Giá lợn hơi giảm sâu trên cả nước, nhiều nơi xuống 45.000 đồng/kg" — 26/10/2026: https://vnbusiness.vn/gia-lon-hoi-giam-sau-tren-ca-nuoc-nhieu-noi-xuong-45000-dongkg.html
- CafeF (VTV), "Giá lợn hơi chạm đáy mới" — 23/10/2026: https://cafef.vn/gia-lon-hoi-cham-day-moi-188261023133651276.chn
- VnBusiness, "Ngành chăn nuôi heo VN trước nguy cơ lặp lại kịch bản dư cung của TQ" — 07/07/2026: https://vnbusiness.vn/nganh-chan-nuoi-heo-viet-nam-truoc-nguy-co-lap-lai-kich-ban-du-cung-cua-trung-quoc.html
- Thời báo Tài chính VN, "Giá thịt lợn, TACN và phân bón đồng loạt chịu áp lực tăng" — 01/07/2026: https://thoibaotaichinhvietnam.vn/gia-thit-lon-thuc-an-chan-nuoi-va-phan-bon-dong-loat-chiu-ap-luc-tang-199971-199971.html
- Nhà Đầu tư, "Giá heo hơi giảm hơn 40% so với đầu năm, heo nhập khẩu tăng vọt" — 13/11/2025: https://nhadautu.vn/gia-heo-hoi-giam-hon-40-so-voi-dau-nam-heo-nhap-khau-tang-vot-d100688.html
- Nhà Đầu tư, "Giá heo hơi neo cao sát Tết, vượt đỉnh 2025" — ~25/01/2026: https://nhadautu.vn/gia-heo-hoi-neo-cao-sat-tet-vuot-dinh-2025-d102545.html
- Việt Nam News, "Cheap imported pork adds pressure on domestic farmers" — 09/2026: https://vietnamnews.vn/economy/1799335/cheap-imported-pork-adds-pressure-on-domestic-farmers.html ; "Việt Nam spends over $4 billion on meat, fishery imports in eight months": https://vietnamnews.vn/economy/1799366/viet-nam-spends-over-4-billion-on-meat-fishery-imports-in-eight-months.html
- Porcinews, "Imported meat surge squeezes Vietnam's livestock sector" (2026): https://porcinews.com/en/imported-meat-surge-squeezes-vietnams-livestock-sector/
- avinews, "Thức ăn chăn nuôi tăng giá lần thứ 7 trong năm 2026" (đoạn trích tìm kiếm, trang trả 403): https://avinews.com/vi/thuc-an-chan-nuoi-tang-gia-lan-thu-7-trong-nam-2026/amp/
- Mekong ASEAN, "Việt Nam chỉ tự chủ được khoảng 37% TACN": https://mekongasean.vn/viet-nam-chi-tu-chu-duoc-khoang-37-thuc-an-chan-nuoi-17637.html ; "Nông nghiệp tháng 10" — 03/11/2026: https://mekongasean.vn/nong-nghiep-thang-10-dien-tich-lua-giam-chan-nuoi-tang-truong-61425.html
- Tuổi Trẻ, "Giá nguyên liệu hạ nhiệt, vì sao TACN vẫn 'đứng giá'?" — 12/12/2025: https://tuoitre.vn/gia-nguyen-lieu-ha-nhiet-vi-sao-thuc-an-chan-nuoi-van-dung-gia-20251212193346566.htm
- ASF địa phương 2026: Huế (T4/2026) https://hue.gov.vn/Portals/0/Uploads/VBPL/Nam2026/Thang4/00.00.H57-12-CT-UBND-2026-PL1_signed.pdf ; Lào Cai https://baolaocai.vn/lao-cai-tang-cuong-cac-bien-phap-phong-chong-dich-ta-lon-chau-phi-post911993.html ; Thanh Hoá https://nhandan.vn/kiem-soat-khong-che-dich-ta-lon-chau-phi-o-thanh-hoa-post1000352.html ; An Giang https://nhandan.vn/an-giang-tang-cuong-phong-chong-dich-ta-lon-chau-phi-post999395.html ; Đắk Lắk https://vov.vn/xa-hoi/dich-ta-lon-chau-phi-dien-bien-phuc-tap-o-dak-lak-post1348607.vov ; Nghệ An https://www.vietnamplus.vn/nghe-an-chan-chinh-trong-phong-chong-benh-dich-ta-lon-chau-phi-post1142600.vnp
- Vaccine ASF: https://news.laodong.vn/y-te/xuat-khau-thanh-cong-vaccine-van-kho-vao-trai-lon-viet-1572385.ldo ; https://www.foodbusinessmea.com/?p=2160734 ; https://en.mae.gov.vn/livestock-production-animal-health/vietnam-exports-340000-doses-of-african-swine-fever-vaccine-to-the-philippines-8997.htm
- Thuế thịt lợn / thoả thuận Mỹ–VN (2025): https://www.feedstuffs.com/policy/vietnam-plans-to-cut-u-s-pork-tariffs-as-trade-tensions-ease ; https://www.foodbusinessmea.com/us-vietnam-reach-trade-agreement-aimed-at-easing-tariffs-expanding-market-access-for-us-pork/
