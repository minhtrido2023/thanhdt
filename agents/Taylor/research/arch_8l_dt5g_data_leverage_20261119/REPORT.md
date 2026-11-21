# REVIEW KIẾN TRÚC 8L + DT5G và PLAN tận dụng dữ liệu ngành / hàng hoá / logistics / năng lượng / vĩ mô

Job `Taylor_20261119_080508` · 19/11/2026 · **CHỈ ĐỌC + LẬP KẾ HOẠCH**. Không sửa code production, không sửa
`filter.json` / `trading_rules.json` / KB, không wire, không chạy backtest NAV. Mọi số "đo" dưới đây đo trong phiên này
(lệnh ở Phụ lục C); số trích từ nghiên cứu cũ ghi rõ file nguồn. Chỗ nào là suy đoán ghi **giả thuyết**; công sức ghi
**ước lượng**.

---

## 0. KẾT LUẬN (đọc phần này là đủ để quyết)

1. **Nhận định "chưa tận dụng hết dữ liệu" ĐÚNG về mặt kho, nhưng phần lớn dữ liệu nằm không KHÔNG chữa được BAL/LAG.**
   Đo hôm nay: 130 chuỗi giá hàng hoá hằng ngày (103 TE + 27 SunSirs) chỉ có **14 mã TE + 1 mã SunSirs** được ánh xạ
   vào cổ phiếu; 41 series vĩ mô có 28 series được code đọc nhưng **toàn bộ chỉ để hiển thị/đối chiếu**, 0 series
   đi vào tín hiệu, cổng hay sizing; `ticker_foreign_flow` / `ticker_prop_flow` có **0 consumer** và **chỉ 3 mã**
   (FPT, SHS, ROS). Tuy nhiên câu hỏi "dữ liệu hàng hoá có cho tín hiệu GIÁ cổ phiếu
   không" **đã được trả lời 26/10: KHÔNG** — 17 trial đăng ký trước, 0 qua cổng (p Bonferroni nhỏ nhất 0,31; nguồn
   `research/commodity_cycle_te_20261026/REPORT.md`, `commodity_p4_sulfur_20261026/REPORT.md`). Cái hàng hoá dự báo
   được là **KQKD** (IC 0,44 với tăng trưởng doanh thu, 0,45 với LN; cùng nguồn), và thị trường đã định giá phần đó
   trong chính quý.
2. **Nhóm cổ phiếu có dữ liệu hàng hoá KHÔNG phải nơi BAL/LAG suy giảm.** Đo mô tả trên ledger pin0%/park0 (đầu SÀN,
   md5 `537e349b`, 695 lệnh LAG / 299 lệnh BAL): lợi suất TB/lệnh giai đoạn 2024+ của nhóm có ánh xạ hàng hoá vẫn
   **+12,5% (BAL, n=13)** và **+9,95% (LAG, n=12)**, trong khi toàn sổ là +4,2% (BAL, n=91) và +4,5% (LAG, n=149).
   Chỗ tụt là ngân hàng (BAL −1,4% n=10; LAG +0,2% n=8), công nghiệp-xây dựng-vận tải (BAL −1,9% n=14) và chứng
   khoán-bảo hiểm (từ 20–35%/lệnh giai đoạn 2020-23 về 5,6–5,8%). N nhỏ, chỉ mô tả, chưa kiểm định. Hàm ý: ngữ cảnh
   còn thiếu nằm ở **vĩ mô/tín dụng/tiêu dùng** (nơi N chu kỳ độc lập rất ít), không nằm ở hàng hoá.
3. **"Suy giảm" của LAG so với 2020-23 phần lớn là quay về mức IS.** Cùng ledger: LAG 2014-19 +4,9%/lệnh (n=311),
   2020-23 +8,8% (n=235), 2024+ +4,5% (n=149). 2020-23 là giai đoạn bất thường. BAL: 7,4% → 15,2% → 4,2%.
   Phần còn lại đã được quy kết ở các file đã đóng: tín hiệu dựa GIÁ sụp về ~0 quanh 2020 (AMH §7), ~46% nhãn fill
   LAG là fill ảo (bal-lag-live-gap), live chạy hệ khác pin trong tháng 7–8.
4. **8L mù chu kỳ ở đúng một chỗ có thể đo:** bộ định tuyến CYCLICAL là danh sách cứng 27 mã. Trong 30 mã có ánh xạ
   hàng hoá tier A/B hiện có rating, **13 mã đi tuyến COMPOUNDER** (PVS, PVD, PVC, PVB, GAS, BSR, TLH, VOS, HAH, DRC,
   CSM, BMP, NTP), tức không bị trần 2, không bị luật "nợ/vốn >1,5 ⇒ 5", và được hưởng nấc moat (HAH đang rating 1
   nhờ `moat↑1`). Nhưng bằng chứng cũ nói điều này **chưa gây hại đo được** (bẫy value đỉnh chu kỳ: sai dấu, p=0,38)
   ⇒ chỉ đáng một phép đếm rẻ, không đáng sửa rating.
5. **DT5G: dữ liệu vĩ mô mới KHÔNG đủ N để thành cap.** Đếm 2014-01-02 → 2026-11-18 (3.212 phiên, thời gian chết
   126 phiên): tỷ giá 60 phiên ≥ +2,5% có **5 episode**; TPCP 10Y +75bp/60 phiên **4**; liên ngân hàng 3T − lãi điều
   hành ≥ 2,5pp **3** (đều sau 2022); DXY +5%/60 phiên **11**. Với N 3–11 không có kiểm định thống kê nào đứng được
   ⇒ **chỉ sổ cảnh báo (shadow-log), không đụng `macro_state_live.py`**.
6. **Việc đáng làm nhất là hạ tầng dữ liệu, không phải tín hiệu:** (a) `macro_indicator` và `commodity_prices` không
   có vintage (đo: `fetched_at` bị ghi đè) ⇒ mỗi ngày trôi qua là mất một ngày PIT; (b) bảng dòng tiền ngoại/tự
   doanh chỉ 3 mã; (c) lens ngân hàng của 8L thiếu dữ liệu — **10/28 mã BANK đang ở nhánh `bank-nodata`, 9 mã trong
   đó nhận rating 3 mặc định** (qua cổng ≤3 mà không được đánh giá), trong khi ngân hàng chiếm 25,9% thanh khoản
   universe; (d) feed tháng của TE đã dừng từ 25/10.

**Đề xuất 3 việc dispatch đầu tiên** (chi tiết §5, §9): ① Winston — gửi bq_admin danh sách lấp dữ liệu + (nếu user
duyệt) chụp vintage hằng ngày; ② Taylor — đóng băng bản đồ v2 và đo nowcast **KQKD** cho họ mới (không đo giá);
③ Taylor — quy kết suy giảm theo ngành × giai đoạn có CI + đếm số lần cổng ≤3 đổi nếu định tuyến lại 13 mã.

---

## 1. KIỂM KÊ DỮ LIỆU (đo 19/11/2026 ~15:15 ICT, BQ `tav2_bq` + grep code)

"Consumer" = file `.py/.sh/.sql` ngoài `research/` và ngoài worktree có tham chiếu (grep GNU, gồm cả `mike/`).

### 1.1 Bảng BQ

| Nguồn | Quy mô / phạm vi (đo) | Tần suất · độ tươi | PIT | Consumer hiện có | Xếp loại |
|---|---|---|---|---|---|
| `commodity_prices` | 350.354 dòng; khoá (metric_key, source, cadence, ngày) 350.354 distinct; 0 NULL | xem 4 dòng dưới | `fetched_at` backfill dồn ⇒ **không vintage** | nowcast block (hiển thị trong plan), `dri_buy_gate_watch`, tracker SUE-decomp (paper), freshness monitor | **DÙNG MỘT PHẦN** |
| · TE daily | 103 mã, 239.592 dòng, 2016-10-25 → 2026-11-18 | ngày; chỉ `tea` trễ >7 ngày (19) | như trên | 14/103 mã có ánh xạ tier A/B | ~89 mã nằm không |
| · TE monthly | 103 mã, 42.041 dòng, 1912-05 → **2026-10-22** | **dừng**: lần nạp cuối 2026-10-25; monitor báo 20 khoá STALE (28–31 ngày) | — | không | nằm không + đang chết |
| · WB CMO | 22 mã, 16.539 dòng, 1960-01 → 2026-10-01 | tháng | bản hiện hành | trùng 6 csv local (`*_monthly.csv`) | trùng lặp |
| · SunSirs | 27 mã, 52.167 dòng, 2012-06-11 → 2026-11-18 (CNY) | ngày | như trên | chỉ `yellow_phosphorus` (nowcast block) | **26/27 nằm không** |
| · GDT | 1 mã, 15 dòng, từ 2026-04-21 | sự kiện | — | không | nằm không |
| `commodity_prices_unified`, `commodity_latest` | **VIEW** (numRows=0 là metadata của view, không phải rỗng) | — | — | cấm dùng cho mô hình (trộn nguồn; registry bẫy 2) | bẫy |
| `macro_indicator` | 84.491 dòng, 41 series (VN 26, US 8, CN 6, JP 1) | 9 series ngày (tới 2026-11-18; `vn_interbank_3m` tới 11-13); còn lại tháng/quý/năm | **KHÔNG**: không có ngày công bố; `fetched_at` bị ghi đè (xem dưới) | `dcf_rate_display`, `dna_report` (liên NH, lãi điều hành), `te_macro_crosscheck`, `macro_snapshot_asof` (khối bối cảnh DD), freshness | **28/41 series được đọc, tất cả DISPLAY/đối chiếu; 13 series không ai đọc; 0 series vào tín hiệu** |
| `macro_indicator_latest` | VIEW | — | — | — | — |
| `ticker_foreign_flow` | 10.812 dòng, **3 mã** (FPT 4.966 từ 2006-12-13; SHS 4.344 từ 2009-06-25; ROS 1.502, 2016-09 → 2022-08); 184 NULL ở giá trị ròng | tạo 2026-11-18, nạp một lượt | không | **0** | **NẰM KHÔNG + chưa dùng được** |
| `ticker_prop_flow` | 2.909 dòng, **3 mã** (FPT 1.911 từ 2019-01-02; SHS 381 từ 2022-05-23; ROS 617); 1–2 mã/phiên | như trên | không | **0** | **NẰM KHÔNG + chưa dùng được** |
| `insider_transaction` | 53.889 dòng, 1.606 mã, 2014-12-31 → 2026-11-17; ~4.000–6.300 dòng/năm | ngày | bảng live bị ghi đè `public_date`; PIT qua `tav2_mike.insider_transaction_snapshots` | `insider_flags.py` (WATCH shadow, cron 18:45), `due_diligence.py` | dùng (shadow) |
| `stock_news` | 60.709 dòng, 1.740 mã, 2015-03-02 → 2026-11-17; mã sự kiện: DIV 31.694 · MA 14.167 · ISS 13.653 · BUYBACK 2.392 · AIS 1.839 · SUSP 1.082 · MOVE 186 · NLIS 173 | ngày; 2020–21 dày (~11.200 dòng/năm) so ~4.000 các năm khác | `public_date` | gián tiếp qua view `treasury_news` (monitor buyback) | **chỉ tin SỰ KIỆN DOANH NGHIỆP**, không phải tin tức chung |
| `treasury_news` | VIEW của `stock_news` lọc BUYBACK | — | — | `treasury_buyback_window_monitor.py` | dùng |
| `shares_outstanding_live` | 7 dòng | sự kiện | — | freshness, cổ tức | dùng |
| `vn30f_daily` | 2.188 dòng, 2017-08-10 → **2026-06-08** | **đứng hơn 5 tháng**, không cron | — | 1 script phân tích cũ | **CHẾT** |
| `corporate_action` | 36.672 dòng, 1.800 mã | ngày | bẫy `first_disclosure_datetime` (đã đóng 10-09) | pipeline corp-action | dùng |

**Bằng chứng `fetched_at` của `macro_indicator` bị ghi đè:** registry ngày 05/11 ghi `vn_cpi_yoy` đã có quan sát
2026-10-31 ở lần scrape 04/11; hôm nay `MIN(fetched_at)` của chính dòng đó là **2026-11-18**. Bảng có 15 ngày
`fetched_at` khác nhau (30/10 → 18/11) nhưng không dùng được làm ngày thấy-lần-đầu.

### 1.2 Feed local và snapshot FiinPro-X

| Nguồn | Trạng thái registry | Consumer (grep) | Xếp loại |
|---|---|---|---|
| `data/bdi_daily_real.csv` | CANONICAL; từ 2026-05 | `freight_map.py`; cron 20:05 | dùng (hiển thị) |
| `data/hog_price_vn.csv` | CANONICAL; từ 2019-01 | `sector_lens_monitor`, `hog_feed_spread`, `hog_gpm_leadlag`; cron T2 | dùng (lens) |
| `data/rubber_weekly.csv` | CANONICAL | `rubber_weekly`, `rubber_trend_break`; cron 18:35 | dùng (cảnh báo) |
| ONI/ENSO | CANDIDATE-PARTIAL | chỉ có writer `oni_index_feed.py` (cron ngày 20) | **nằm không** |
| 6 csv WB CMO | CANONICAL | `cyclical_structural`, `unified_screener`, `sector_lens_monitor`, `hog_feed_spread` | dùng (hiển thị); `caustic_soda_monthly.csv` là **SYNTHETIC** |
| FiinPro CPI tháng | DERIVED | `cpi_vn.py` | dùng |
| FiinPro lãi huy động 1T | CANONICAL-PIT | `idle_rate_proxy.py` | dùng (pin1M) |
| FiinPro bank ratios quý (27 NH, 2010Q1 → 2026Q2) | — | `rating_8l_history.py`, `lag_dd_pack.py` | dùng; **không có nguồn nối tiếp sau trial** |
| FiinPro M2/tín dụng, GDP danh nghĩa, tỷ giá tháng, dòng tiền 5 nhóm NĐT, khối ngoại chỉ số | DERIVED/UNVERIFIED | không thấy trong 13 file non-research khớp `fiinprox_` | **nằm không** (chỉ nạp registry Bobby); snapshot một lần, đã hết trial 28/09 |

### 1.3 Độ phủ theo ngành VN (đo trên `tav2_mike.universe_pit` phiên 2026-11-18)

Universe **334 mã**; tổng trung vị GTGD 1 tháng **11.258 tỷ/phiên** (`ticker_1m.Trading_Value_1M_P50`).

| Nhóm ICB (2 chữ số) | Số mã | GTGD (tỷ/phiên) | Dữ liệu sẵn có liên quan | Mức phủ |
|---|---|---|---|---|
| 83 Ngân hàng | 25 | 2.917 | lãi điều hành, liên NH 3T, TPCP 10Y, tỷ giá; NPL/LLR chỉ tới 2026Q2 | vĩ mô có, **chất lượng tài sản đứt** |
| 86 Bất động sản | 53 | 1.978 | `vn_gdp_construction` (quý, tới 2026-06), lãi suất | mỏng; không có doanh số sơ cấp, TPDN |
| 87 Chứng khoán | 32 | 1.545 | thanh khoản thị trường tự tính được từ `ticker` | có (tự dựng) |
| 27 CN, vận tải, cảng | 31 | 818 | BDI, chỉ số container, xuất/nhập khẩu, FDI, IIP | vừa; thiếu cước tàu dầu, sản lượng cảng |
| 35 Thực phẩm, nông nghiệp | 31 | 697 | đường, heo VN (2019+), ngô, khô đậu; thiếu cá tra/tôm | một phần |
| 17 Kim loại, khai khoáng | 20 | 656 | thép cây SHFE, quặng, than cốc, vonfram (từ 2026-06-24) | vừa; thiếu HRC TQ/VN |
| 95 Công nghệ | 4 | 556 | không | không |
| 23 Xây dựng, VLXD | 49 | 443 | PVC, kính, xi măng không có | mỏng |
| 05 Dầu khí | 8 | 395 | Brent, crack spread, LNG, khí | tốt (trừ độ trễ hợp đồng) |
| 53 Bán lẻ | 8 | 289 | `vn_retail_sales_yoy` | có, chưa dùng |
| 13 Hoá chất, cao su | 19 | 229 | cao su, urê, DAP, P4, lưu huỳnh, xút, NH3 | **tốt nhất** |
| 57 Hàng không, du lịch | 4 | 210 | `vn_tourist_arrivals`, nhiên liệu | có, chưa dùng |
| 75 Điện, khí, nước | 14 | 206 | than, khí; **không có sản lượng/giá điện** | mỏng |
| Còn lại (33, 37, 45, 55, 65, 85) | 36 | 319 | bông, sợi, `vn_car_registrations` | rời rạc |

- Tài chính + BĐS (83, 85, 86, 87): **115 mã = 34,4% số mã, 6.488 tỷ = 57,6% thanh khoản**. Dữ liệu hàng hoá vô nghĩa
  với nhóm này.
- Mã có ánh xạ hàng hoá tier A/B còn trong universe: **29 mã = 8,7% số mã, 1.079 tỷ = 9,6% thanh khoản**.

---

## 2. REVIEW KIẾN TRÚC 8L (`rating_8l.py`, Composite v3, `VALUE_VERSION=v3_div`)

### 2.1 Tín hiệu lấy từ đâu
- **Trục 1 — rating 1–5 (cái production đọc):** 100% từ BCTC. `core_score` 6 trục, tối đa 12: ROIC3Y, ROIC_Min3Y,
  ROE_Trailing, đòn bẩy vay thật (`STLTDebt_Eq`), CFO/LN TTM, FSCORE. Cộng `redflag` (lỗ TTM, nợ/vốn >3), `eq_flag`
  (LN ngoài cốt lõi), `stability` (CV biên gộp 8 quý, ROE_Trailing/ROE3Y), nấc moat (chỉ khi 5F = WIDE), cờ forensic.
- **Bộ định tuyến:** BANK (lens v3: ROE, NPL, coverage) · POWER (`power_lens.csv`) · INSURANCE · SECURITIES (ROE,
  trần 2) · REALESTATE (ICB 8633, trần 2, sàn 4) · **CYCLICAL = danh sách cứng** `COMMODITY_MAP` (17 mã) + đường +
  xi măng · còn lại COMPOUNDER. Đo trên `data/rating_8l.csv` (794 mã): COMPOUNDER 563, REALESTATE 85, SECURITIES 41,
  POWER 38, BANK 28, **CYCLICAL 27**, INSURANCE 12.
- **Trục 2 — value_score/zone:** 1/PE, 1/PCF, 1/PS, 1/EVEB, cổ tức, xếp hạng **trong tuyến**; phạt đỉnh LN
  (`ROE_Trailing/ROE5Y > 1,5`); tilt ±0,03 theo lãi huy động chỉ ở NEUTRAL. **Không selector production nào đọc trục
  này** — BAL/LAG/custom30V chỉ đọc cổng `rating ≤ 3`.
- **Dữ liệu ngành/hàng hoá/vĩ mô đi vào rating: KHÔNG có gì**, ngoài lãi huy động trong tilt hiển thị. Pha chu kỳ
  hàng hoá chỉ xuất hiện ở công cụ hiển thị (`cyclical_structural.py`, `dna_card.py`, `unified_screener.py`) và các
  công cụ đó đọc csv tháng WB — riêng xút là chuỗi SYNTHETIC.

### 2.2 Ba loại điểm yếu

**(a) Thông tin bị bỏ**
- Giá đầu ra/đầu vào của kỳ hiện tại. Nowcast KQKD từ giá TB quý đã đo được (IC với LN: urê 0,93, BDI 0,63, DAP
  0,53, container 0,49, cao su 0,48, đường 0,43, thép 0,35, dầu 0,03; đầu vào ngược chiều: quặng → HPG −0,49, than
  cốc −0,47; nguồn `commodity_cycle_te_20261026/REPORT.md` §2). Rating chỉ thấy điều này sau khi BCTC ra.
- Chênh lệch đầu ra − đầu vào (thép − quặng − than cốc; heo − TACN; urê − khí): dữ liệu có đủ, chưa có mã nào dùng.
- Chất lượng tài sản ngân hàng: lens v3 ghi `BLOCKED-STALE` ở index registry và `PARTIAL` ở file riêng (NPL/coverage
  chỉ OCR được 9/18 mã ngày 28/08; CAR/CASA không tái lập được). Đo trên `data/rating_8l.csv`: **10/28 mã BANK ở nhánh
  `bank-nodata`** (VAB, KLB, NVB, PGB, SGB, PCB, ABB, BAB, BVB, VBB — đều nhỏ, `liq_bn` 0,02–15,5), 9 mã nhận rating 3
  mặc định; 10 mã khác ở "profitable (AQ-modulated)" = 3. Tức 19/28 mã BANK đứng ở đúng ranh cổng. Ngoài ra STB,
  EIB, SSB đang rating 5 do ROE < 8% — **chưa kiểm** ROE đó là thật hay do dữ liệu lens.

**(b) Nguy cơ double-count / PIT / survivorship**
- `COMMODITY_MAP` khai báo ở 4 file (`cyclical_structural.py`, `dna_card.py`, `build_rating_8l_history.py`,
  `build_value_panel.py`) — lệch nhau là lệch tuyến giữa rating live và rating lịch sử.
- Danh sách CYCLICAL là danh sách **hôm nay** áp cho mọi ngày lịch sử: mã đổi mô hình kinh doanh bị gán tuyến sai
  về trước (ca HHS đã phải thêm override tay).
- `moat_tag` STRONG = biên gộp cao và ổn định 8 quý. Với mã cước/hàng hoá đang giữa chu kỳ lên, 8 quý biên cao là
  **pha chu kỳ**, không phải lợi thế bền — đúng ca HAH (rating 1, `moat↑1`, nowcast container +0,80 ở Q3/2026).
- Nếu sau này đưa nowcast hàng hoá vào value_score thì trùng với phần `ROE_Trailing/ROE5Y` đang phạt đỉnh: cùng một
  thông tin đếm hai lần.

**(c) Rating trễ so với chu kỳ ngành**
- Mọi trục là 3Y hoặc TTM ⇒ chủ đích "xuyên chu kỳ", đổi lại trễ 2–4 quý ở điểm đảo chiều. `stability` chỉ bắt đỉnh
  khi ROE_Trailing đã vượt 1,8 lần ROE3Y, tức sau khi đỉnh đã vào BCTC.
- **13/30 mã hàng hoá tier A/B đi tuyến COMPOUNDER** (đo): DRC, CSM, PVS, PVD, PVC, PVB, GAS, BSR, TLH, VOS, HAH, BMP,
  NTP. Hệ quả cơ học: không trần 2, không luật "nợ/vốn >1,5 ⇒ 5", được nấc moat.
- **Phản chứng phải nêu:** vì cổng là nhị phân ≤3, chỉ các ca cắt qua ranh 3/4 mới chạm NAV. Bằng chứng cũ: lệnh BAL
  vào mã producer ở tercile trên của hàng hoá chỉ kém −1,7pp (n=25); giả thuyết bẫy value đỉnh chu kỳ **sai dấu**
  (+1,3pp, p=0,38); custom30V đỉnh − đáy −2,9pp, CI90 [−11,2; +6,4]. ⇒ điểm yếu kiến trúc có thật, tác hại chưa đo
  được.

### 2.3 Giả thuyết kiểm chứng được
- **H-8L-1:** định tuyến lại 13 mã sang CYCLICAL làm đổi cổng ≤3 ở dưới 30 cặp (mã, quý) trong lịch sử PIT. Nếu đúng
  ⇒ dừng, chỉ hợp nhất danh sách cho nhất quán. (Phép đếm, không cần NAV.)
- **H-8L-2:** với họ có IC nowcast ≥ 0,35, dấu của nowcast quý Q dự báo **hướng đổi rating** ở lần chấm kế tiếp. Đây
  là giả thuyết về KQKD/rating, không phải về giá.
- **H-8L-3 (ngân hàng):** nhánh mặc định `bank-nodata ⇒ 3` là fail-OPEN đối với cổng ≤3 (đã đo: 9 mã). Kiểm tiếp:
  trong 9 mã đó bao nhiêu mã nằm trong `universe_pit` và từng vào sổ LAG/BAL; nếu có, mặc định nên là 4 (fail-closed)
  — đây là thay đổi rating nên phải qua A/B và user duyệt.

---

## 3. REVIEW KIẾN TRÚC DT5G (`macro_state_live.py`, 4 tầng)

### 3.1 Hiện trạng
| Tầng | Đầu vào | Nhận xét |
|---|---|---|
| 1. Base v3.4b | giá VNINDEX | không dùng vĩ mô |
| 2. DT 4-gate (10/25/25) | chuỗi state | làm mượt bất đối xứng |
| 3. Macro gate | Trụ A: thay đổi 126 phiên của lãi tái cấp vốn SBV (`SBV_REFI_EVENTS`, trễ 5 phiên). Trụ B: VIX + drawdown 1 năm của SPX (T-1). Bypass khi VN bull xác nhận. Cap phải giữ 7 phiên | chỉ 2 họ dữ liệu; toàn bộ edge = 1 lần siết 2023 (docstring module) |
| 4. Breadth guard | % mã trên MA200 trong `universe_pit` | chỉ chặn cap của Trụ B |

### 3.2 Dữ liệu vĩ mô mới có cho tín hiệu CHẶN RỦI RO chưa dùng không?
Về nhân quả thì có ứng viên; về thống kê thì chưa đủ để thành cap. Đếm episode (kích hoạt lần đầu, thời gian chết 126
phiên, 2014-01-02 → 2026-11-18, **không nhìn lợi suất sau đó**; file `appendix_macro_trigger_episode_counts.csv`):

| Trigger ứng viên | Cơ sở nhân quả | N episode | Lúc đó DT5G ≥ NEUTRAL | IS / OOS |
|---|---|---|---|---|
| USD/VND tăng ≥ 2,5% trong 60 phiên | áp lực tỷ giá ⇒ SBV hút thanh khoản, khối ngoại rút | 5 | 4 | 1 / 4 |
| TPCP 10Y tăng ≥ 75bp trong 60 phiên | chi phí vốn dài hạn | 4 | 2 | 1 / 3 |
| Liên NH 3T − lãi điều hành ≥ 2,5pp | căng thanh khoản hệ thống | 3 | 2 | 0 / 3 |
| Liên NH 3T tăng ≥ 150bp trong 60 phiên | như trên, dạng thay đổi | 8 | 6 | 3 / 5 |
| DXY tăng ≥ 5% trong 60 phiên | USD mạnh toàn cầu | 11 | 7 | 5 / 6 |
| US 10Y tăng ≥ 75bp trong 60 phiên | chi phí vốn toàn cầu | 7 | 4 | 1 / 6 |
| USD/CNY tăng ≥ 3% trong 60 phiên | áp lực cạnh tranh tỷ giá khu vực | 11 | 5 | 6 / 5 |

- N = 3–11 và dồn về sau 2020 ⇒ không thể kiểm định IS/OOS đúng nghĩa. Mức `vn_bond_10y` còn lệch VBMA +0,13…+0,21pp
  (chỉ tin Δ). Nghiên cứu D2 (spread thanh khoản dẫn lãi huy động) đã ra **KHÔNG KẾT LUẬN**.
- Giá trị hiện tại (đo): liên NH 3T − lãi điều hành **2,13pp** (quan sát tới 13/11); USD/VND 60 phiên **−1,65%**;
  TPCP 10Y Δ60 phiên **+0,01**.
- **Kết luận tầng 3:** không thêm cap, không đổi tham số. Việc hợp lý duy nhất là mở Làn 3 (F1) của kế hoạch TE đã
  duyệt 04/11 dưới dạng **sổ cảnh báo append-only** + dòng hiển thị, theo đúng khuôn `cap_signal_advisory_log`
  (ngưỡng nâng cấp N cụm ≥ 10).

### 3.3 Vĩ mô/ngành làm bộ lọc regime cho BAL vs LAG?
Đã thử và đã đóng — **không đề xuất lại:**
- 0/6 biến thời điểm (DT5G, dd52 VNINDEX, breadth, drawdown SPX, LAG edge, vol60) qua tiêu chí khai trước; MDE
  14–30pp (IS) / 57–110pp (OOS) (bal-lag-live-gap GĐ3).
- Cổng edge-health theo tháng cho BAL: −2,62pp (pin0%) / −2,76pp (pin1M) CAGR, 18/18 biến thể âm — NO-GO 12/11.
- Lãi tiết kiệm tăng ⇒ lệnh kém: "không kết luận, không bác", N độc lập 1–7.
- Khối ngoại cấp chỉ số: NO-GO hai lần (`foreign_flow_finding.md` 23/07; FiinPro H4 27/09).
- Allocator `w_LAG` {CRISIS 50 / BEAR 0 / còn lại 65, ±10pp}: quyết định 12/07 là không tăng trần. Edge LAG hiện ở
  TROUGH (12T +0,06%/lệnh, win 37%, n=582, phân vị 6, as-of 2026-09-23; `data/edge_health_block.md`) và hệ đã tự
  phản ứng ("không tăng w_LAG").

---

## 4. CHẨN ĐOÁN SUY GIẢM BAL/LAG (đọc số đã pin, không chạy lại backtest)

| Nhóm nguyên nhân | Bằng chứng (nguồn) | Dữ liệu sẵn có bù được? |
|---|---|---|
| **(i) Cấu trúc thị trường** | Tín hiệu dựa GIÁ sụp ~0 quanh 2020: `mom_200` IC NEUTRAL IS +0,164 (t 5,09) → OOS +0,005 (t 0,16) (amh §7). Value mạnh lên: PE −0,054 → −0,117, ROE_Min5Y +0,051 → +0,191 (`edge_health_block.md`, panel tới 2026-08). FTSE: 0/24 đại lượng ngoài dải p5–p95, N=1 sự kiện — **không** được quy là nguyên nhân (ftse §Kết luận). Capacity LAG @50 tỷ: 31% giá trị mua ở ngày Volume=0 (lag-adv) | Không |
| **(ii) Fidelity live vs backtest** | ~46% nhãn LAG fill ảo; bỏ fill ảo −3,96pp DD5 (park 0,3) / −4,17pp (park 0). Sửa chuỗi custom30V −4,48pp. Engine bất tất định: 10 seed CAGR 23,94–25,05%. Live 04/08 → nay BAL+LAG chỉ ~5% NAV; sổ BAL live có đúng 1 lệnh (VPI, −21%) (bal-lag-live-gap; `bal_loss_attribution_20261022`) | Không |
| **(iii) Thiếu ngữ cảnh ngành/chu kỳ/vĩ mô** | 11 file chẩn đoán **không phân tích theo ngành**. Đo bổ sung hôm nay ở bảng dưới | **Chỉ phần này là đất của plan** |

**Đo bổ sung — lợi suất TB/lệnh theo nhóm ngành × giai đoạn** (ledger R3 park0 pin0% đầu SÀN md5 `537e349b`, vintage
07-29; mô tả, chưa kiểm định; đầy đủ ở `appendix_deals_by_sector_era.csv`):

| Sổ | Nhóm | 2014-19 | 2020-23 | 2024+ |
|---|---|---|---|---|
| BAL | Toàn sổ | +7,4% (n=83) | +15,2% (n=125) | **+4,2% (n=91)** |
| BAL | Có ánh xạ hàng hoá | +21,8% (10) | +17,2% (16) | +12,5% (13) |
| BAL | Ngân hàng | — (1) | +6,2% (4) | −1,4% (10) |
| BAL | Chứng khoán + bảo hiểm | — (1) | +34,8% (9) | +5,6% (11) |
| BAL | BĐS | +7,0% (52) | +9,3% (37) | +11,2% (16) |
| BAL | XD, CN, vận tải | +4,6% (7) | +23,5% (22) | −1,9% (14) |
| BAL | Tiêu dùng, dịch vụ | −0,1% (11) | +18,1% (21) | +3,4% (18) |
| LAG | Toàn sổ | +4,9% (n=311) | +8,8% (n=235) | **+4,5% (n=149)** |
| LAG | Có ánh xạ hàng hoá | +11,7% (18) | +9,2% (25) | +10,0% (12) |
| LAG | Ngân hàng | +13,8% (5) | +14,0% (8) | +0,2% (8) |
| LAG | Chứng khoán + bảo hiểm | +2,1% (15) | +20,3% (31) | +5,8% (34) |
| LAG | BĐS | +4,1% (26) | +8,3% (21) | +2,3% (13) |
| LAG | XD, CN, vận tải | +5,9% (110) | +7,4% (50) | +3,5% (26) |
| LAG | Tiêu dùng, dịch vụ | +5,0% (93) | +6,3% (66) | +4,4% (29) |

Đọc được ba điều (đều ở mức mô tả):
1. Nhóm có dữ liệu hàng hoá là nhóm **giữ được** lợi suất ⇒ hàng hoá không phải mảnh ngữ cảnh còn thiếu.
2. LAG 2024+ ≈ LAG 2014-19; cái mất đi là phần vượt trội của 2020-23, tập trung ở chứng khoán-bảo hiểm (PnL LAG
   nhóm này 80,1 tỷ giai đoạn 2020-23 trong sổ backtest).
3. Chỗ tụt thật là ngân hàng và nhóm nhạy tín dụng/đầu tư công — đúng nơi dữ liệu fleet mỏng nhất (đứt NPL, không
   có tín dụng tháng nối tiếp, không có giải ngân đầu tư công).

**Tỷ trọng thật của phần (iii): nhỏ và chưa định lượng được.** Tôi không đưa ra con số pp CAGR nào cho nó.

---

## 5. PLAN — danh sách ưu tiên

Quy ước chung cho mọi hạng mục có kiểm định: universe = `universe_pit` cho cả chân thử và chân đối chứng; KQKD lấy
theo `Release_Date`; không dùng `profit_*`, không dùng `ticker_prune`; IS 2014-19 / OOS 2020+ (họ thiếu lịch sử thì
tách 2023 và ghi rõ); N = đơn vị độc lập (họ × quý, hoặc cụm tháng), không phải số dòng; hiệu chỉnh BH-FDR trên toàn
bộ số trial khai trước; hoán vị dạng dịch vòng (circular shift) hoặc khối tháng — **không hoán vị trong năm**; mọi
số NAV (nếu có về sau) báo đủ cặp pin0% … pin1M. Số trial tích luỹ của dòng nghiên cứu hàng hoá hiện là **17**.

### WAVE A — rẻ, ít rủi ro: lấp dữ liệu + đo (không đổi mô hình)

**A1. Chụp vintage hằng ngày cho `macro_indicator` và `commodity_prices`**
1. *Vì sao:* không có ngày thấy-lần-đầu thì mọi backtest dùng series tháng/quý phải giả định độ trễ; `fetched_at` bị
   ghi đè (đo). Mỗi ngày chưa chụp là một ngày PIT mất hẳn.
2. *Dữ liệu:* bản sao append-only (series_key, observation_date, value, snapshot_date) vào dataset của fleet
   `tav2_mike`, cùng khuôn `insider_transaction_snapshots`.
3. *Tác động:* hạ tầng. Mở đường cho A4, C1 và mọi nghiên cứu vĩ mô sau này.
4. *Kiểm định:* selfcheck — chạy lại cùng ngày không sinh dòng trùng; 0 dòng có snapshot_date < observation_date.
5. *GO/NO-GO:* không áp dụng; cần **user duyệt** (05/11 user không duyệt tạo VIEW trong `tav2_bq`; đây là bảng trong
   dataset của fleet — vẫn phải hỏi).
6. *Công sức (ước lượng):* 1 dispatch Winston, cỡ nhỏ; thêm 1 dòng cron ⇒ theo §11 tra `cron_registry`. Rủi ro: phí
   BQ không đáng kể (bảng 14,5 MB + 60,8 MB).
7. *Rollback:* gỡ dòng cron; bảng snapshot để nguyên.

**A2. Gửi bq_admin danh sách lấp khoảng trống** — nội dung ở §8. Một dispatch Winston soạn, user chuyển tay.

**A3. Đóng băng bản đồ v2 "dữ liệu → ngành → mã"**
1. *Vì sao:* mọi phép đo sau đó phải chạy trên danh sách cố định, nếu không thì chọn mã sau khi thấy kết quả.
2. *Dữ liệu:* `commodity_map_te.csv` (55 dòng, 45 mã) + các khoá SunSirs chưa ánh xạ (§7) + series hoạt động vĩ mô.
   Mỗi dòng: mã, họ, khoá, nguồn, dấu, vai trò (đầu ra / đầu vào / hoạt động), độ trễ PIT giả định, lý do nhân quả
   một câu.
3. *Tác động:* không; là đầu vào của A4, B2, B3.
4–5. *Kiểm định / GO:* md5 + commit **trước** khi chạy A4. Mã nào không viết nổi câu nhân quả thì không vào bản đồ.
6. *Công sức (ước lượng):* nửa ngày Taylor. Rủi ro: đường rẽ (forking path) ⇒ khoá bằng md5.
7. *Rollback:* không có gì để gỡ.

**A4. Mở rộng nowcast KQKD sang họ mới — đo KQKD, KHÔNG đo giá**
1. *Giả thuyết nhân quả:* doanh thu/biên của một số ngành là hàm gần trực tiếp của một đại lượng quan sát được trước
   BCTC khoảng một tháng (đã chứng minh với 8 họ hàng hoá). Mở sang: (a) chênh lệch đầu ra − đầu vào; (b) hàng SunSirs
   mới; (c) hoạt động vĩ mô theo ngành.
2. *Dữ liệu và số trial khai trước (tối đa 12 họ):*

   | # | Họ | Tín hiệu (nguồn tường minh) | Mã | Trễ PIT giả định |
   |---|---|---|---|---|
   | 1 | Biên thép | `steel` − 1,6×`iron_ore_cny` − 0,5×`coke` (TE/SunSirs daily; hệ số là **giả định** định mức, khoá trước) | HPG | quý kết thúc + 2 ngày |
   | 2 | Biên chăn nuôi | `hog_price_vn.csv` − chi phí TACN (`corn`, `soybean_meal_cny`) | DBC, BAF | như trên |
   | 3 | Phốt pho vàng | `yellow_phosphorus` (SunSirs, từ 2018) | DGC, PAT | như trên |
   | 4 | Xút | `caustic_soda` (SunSirs, từ 2023-09) | CSV | như trên; **lịch sử ngắn ⇒ chỉ mô tả** |
   | 5 | Sợi polyester | `polyester_staple_fiber` − `pta` − `ethylene_glycol` | STK | như trên |
   | 6 | Ống nhựa | `polyvinyl` (đầu vào, dấu −) | BMP, NTP | như trên |
   | 7 | Bán lẻ | `vn_retail_sales_yoy` (TB quý) | MWG, FRT, DGW, PNJ, PET | cuối tháng + 10 ngày (**giả định**) |
   | 8 | Môi giới | GTGD toàn thị trường TB quý, tự tính từ `ticker` | SSI, VCI, HCM, VND, SHS, MBS | 0 ngày |
   | 9 | Hàng không, sân bay | `vn_tourist_arrivals` | ACV, SCS, SAS (đo thêm HVN, VJC, gắn cờ banned) | cuối tháng + 10 ngày |
   | 10 | Cảng | `vn_exports` + `vn_imports` | GMD, VSC, PHP | cuối tháng + 15 ngày |
   | 11 | Ô tô | `vn_car_registrations` | VEA, HAX | cuối tháng + 20 ngày |
   | 12 | Ngân hàng (NIM) | `vn_interbank_3m` − `vn_policy_rate`, Δ`vn_bond_10y` | 25 mã ICB 83 | 0 ngày |

3. *Tác động:* (i) họ đạt cổng được thêm vào khối nowcast **hiển thị** trong plan; (ii) đủ điều kiện vào PREREG-5
   (B1); (iii) dữ liệu cho H-8L-2. Không gate, không tilt.
4. *Thiết kế:* y như B2 ngày 26/10 — `c_yoy` → `rev_yoy`, `np_d`, `gpm_d`; N = họ × quý; CI90 moving-block
   bootstrap khối 4 quý; p bằng dịch vòng chung; BH-FDR trên 12 họ × 1 biến đích chính (`np_d`). Chân đối chứng: 8 họ
   tier A cũ phải tái lập IC gộp 0,45 (sai lệch ≤ 0,02) trước khi đọc họ mới. Giới hạn đã biết: BCTC là bản ingest
   mới nhất chứ không phải bản công bố đầu (đo 26/10: NP_P0 đổi >0,5% ở 0,02% dòng trong cửa sổ 3,5 tháng).
5. *GO khai trước (từng họ):* IC(`c_yoy` → `np_d`) ≥ 0,25 **và** CI90 không chứa 0 **và** cùng dấu ở hai nửa mẫu
   **và** BH q < 0,10. Trượt bất kỳ điều nào ⇒ họ đó chỉ được ghi "không đạt", không thử biến thể. Power (ước
   lượng): một họ ~40 quý phát hiện được IC từ khoảng 0,35–0,40 trở lên; họ 4 (xút) không đủ lịch sử.
6. *Công sức (ước lượng):* 1 dispatch Taylor (opus/medium) + quant-skeptic. Rủi ro: 12 trial nâng tổng lên 29; độ trễ
   công bố là giả định tới khi A1 chạy đủ lâu.
7. *Rollback:* không wire gì.

**A5. Quy kết suy giảm theo ngành × giai đoạn, có khoảng tin cậy**
1. *Vì sao:* bảng §4 mới là mô tả. Cần biết chênh lệch "nhóm tụt − nhóm giữ" có vượt nhiễu không trước khi đổ công
   vào dữ liệu ngân hàng/tín dụng.
2. *Dữ liệu:* `features.csv` + `features_pin1M.csv` của `lag_bal_discriminators_20261025` (hai đầu dải).
3. *Tác động:* định hướng ưu tiên dữ liệu; không phải tín hiệu.
4. *Thiết kế:* 7 nhóm ngành cố định như phụ lục; thống kê = hiệu lợi suất TB/lệnh (2024+ trừ 2014-19) theo nhóm;
   bootstrap theo **cụm tháng vào lệnh**; 2 sổ × 7 nhóm = 14 phép so, BH-FDR. Báo cả pin0% và pin1M.
5. *Tiêu chí đọc khai trước:* nhóm nào có CI90 của hiệu nằm hẳn dưới 0 ở **cả hai** đầu dải ⇒ ghi "tụt có ý nghĩa";
   còn lại ghi "không phân biệt được". Không có GO wire.
6. *Công sức (ước lượng):* vài giờ, sonnet. Rủi ro: N nhỏ ở ngân hàng (8–10 lệnh) ⇒ nhiều khả năng "không phân biệt
   được" — vẫn là kết quả dùng được.

### WAVE B — tích hợp 8L / LAG, chỉ sau quant-skeptic

**B1. LAG — tách SUE "đã biết từ dữ liệu ngành" khỏi "bất ngờ thật"**
1. *Giả thuyết:* SUE dương chủ yếu do giá hàng hoá/hoạt động ngành đã công khai không phải bất ngờ; drift sau công bố
   nằm ở phần dư. Post-hoc 30 quý: phần dư t = 1,78, CI90 [0,013; 0,188]; phần hàng hoá OOS t = −2,3. Với đúng biến
   SUE mà LAG live dùng, lịch sử cho ΔIC −0,012 — tức **chưa có bằng chứng** (PREREG-4 §0).
2. *Dữ liệu:* tracker `commodity_sue_decomp_forward_tracker.py` đang chạy cron (124 dòng sự kiện, 27 dòng kết quả,
   hiện toàn `PRE_FREEZE_BACKFILL`); danh sách 25 mã tier A đóng băng.
3. *Tác động tiềm năng:* bộ lọc/tilt lệnh vào LAG cho mã có nowcast. Sớm nhất **2027-09**.
4. *Thiết kế:* giữ nguyên PREREG-4 (md5 `6c5642c1…`), **không sửa**. Nếu A4 có họ đạt cổng ⇒ viết **PREREG-5 riêng**
   cho họ mới, đo forward song song, không gộp ngược vào PREREG-4.
5. *GO:* như PREREG-4 (≥ 2 mùa BCTC, quant-skeptic CONFIRMED, kiểm toán corp-action mốc 2027-09-01).
6. *Công sức (ước lượng):* PREREG-5 nửa ngày. Rủi ro: phủ chỉ 29 mã (8,7% universe) ⇒ kể cả GO, tác động lên NAV LAG
   bị chặn trên bởi tỷ trọng nhóm này (86/1.498 holding LAG trong ledger pin).
7. *Rollback:* tắt cron tracker.

**B2. 8L — đếm tác động của việc định tuyến lại 13 mã chu kỳ (H-8L-1)**
1. *Giả thuyết:* mã có KQKD gắn hàng hoá/cước mà đi tuyến COMPOUNDER được chấm rộng tay ở đỉnh chu kỳ.
2. *Dữ liệu:* `build_rating_8l_history.py` (PIT), danh sách 13 mã ở §2.2c.
3. *Tác động:* rating (cổng ≤3) ⇒ chạm cả BAL, LAG, custom30V nếu đổi.
4. *Thiết kế hai bước:* Bước 1 chỉ **đếm** số cặp (mã, quý) mà cổng ≤3 đổi khi định tuyến lại, 2014 → nay. Bước 2
   (chỉ khi bước 1 vượt ngưỡng) mới A/B NAV có chân control tái lập pin, self-check 0 VND, báo cặp pin0%/pin1M.
5. *GO khai trước:* bước 1 < 30 cặp đổi cổng ⇒ **dừng**, chỉ hợp nhất danh sách (0 thay đổi rating, kiểm
   byte-identical `rating_8l.csv`). Bước 2 chỉ đề xuất wire khi ΔCAGR ≥ 0 ở cả IS và OOS, DD không xấu hơn, DSR ≥ 0,95.
6. *Công sức (ước lượng):* bước 1 vài giờ. Kỳ vọng thẳng: gần 0 (xem phản chứng §2.2c).
7. *Rollback:* danh sách tuyến là hằng số, đổi lại một dòng.

**B3. 8L — cột hiển thị "pha chu kỳ + nowcast" và dọn chuỗi xút SYNTHETIC**
- DISPLAY-ONLY: thêm phân vị giá TB63, R/MA252, `c_yoy` cạnh mã chu kỳ trong screener/DNA card bằng cách tái dùng
  `commodity_nowcast_block.py`; thay `caustic_soda_monthly.csv` (SYNTHETIC) bằng `caustic_soda` SunSirs hoặc in
  "không có dữ liệu". Không kiểm định thống kê; cần arch-review và kiểm `rating_8l.csv` không đổi một byte.
- Rollback: một cờ tắt khối hiển thị.

**B4. 8L — nối lại dữ liệu chất lượng tài sản ngân hàng (H-8L-3)**
- Không phải nghiên cứu, là lỗ dữ liệu: cần nguồn quý NPL / coverage / CAR / CASA sau 2026Q2 (§8 mục 7). Việc rẻ làm
  ngay được: đếm 9 mã `bank-nodata` rating 3 có mã nào trong universe và từng được LAG/BAL mua; xét đổi mặc định sang
  fail-closed (4). Tác động NAV kỳ vọng thấp (FiinPro H1:
  427/1.117 mã-quý đổi rating nhưng 0 lần cổng ≤3 đổi), nên đây là vệ sinh, không phải alpha.

### WAVE C — DT5G / allocator: chỉ cảnh báo

**C1. Sổ cảnh báo căng thẳng vĩ mô (mở Làn 3 / F1 của kế hoạch TE 04/11)**
1. *Giả thuyết nhân quả:* căng thanh khoản nội địa (liên NH − lãi điều hành), áp lực tỷ giá và chi phí vốn dài hạn đi
   trước việc SBV đổi lãi tái cấp vốn — biến duy nhất Trụ A đang nhìn.
2. *Dữ liệu:* `vn_usdvnd`, `vn_bond_10y` (chỉ Δ), `vn_interbank_3m`, `vn_policy_rate`, `us_dxy`; series ngày ⇒ không
   vướng độ trễ công bố; fail-closed khi quan sát cũ hơn 7 ngày.
3. *Tác động:* dòng HIỂN THỊ trong báo cáo regime + sổ append-only. Không cap, không sizing, không đụng
   `macro_state_live.py`, không đổi `w_LAG`.
4. *Thiết kế:* PREREG khoá 4 trigger ở đúng ngưỡng bảng §3.2 (không dò ngưỡng); Bobby phân loại mù từng episode
   (cơ cấu tự cộng dồn hay cú sốc có mục tiêu) **trước** khi ai xem lợi suất sau đó; khung nhân quả vì N nhỏ.
5. *Điều kiện để ĐƯỢC ĐỀ XUẤT cap (khai trước):* tổng số cụm độc lập ≥ 10 **và** ≥ 5 cụm xảy ra khi DT5G ≥ NEUTRAL
   (tức có thông tin gia tăng) **và** quant-skeptic CONFIRMED **và** user duyệt riêng. Hôm nay: 3–5 cụm cho ba trigger
   nội địa ⇒ nhiều năm nữa mới đủ. Chấp nhận trước rằng hạng mục này có thể mãi là hiển thị.
6. *Công sức (ước lượng):* 1 dispatch Taylor (sonnet) + arch-review. Rủi ro: người đọc coi dòng hiển thị là tín hiệu
   ⇒ gắn nhãn "giả thuyết chưa kiểm" như dòng D1 hiện có.
7. *Rollback:* tắt dòng hiển thị; sổ để nguyên.

**C2. Bộ lọc regime cho BAL/LAG từ vĩ mô — KHÔNG mở** (lý do ở §6). Ngoại lệ duy nhất, để sau và chỉ khi user muốn:
"độ rộng lợi nhuận theo mùa" (tỷ lệ mã có LN tăng so cùng kỳ) làm biến mô tả cho LAG; N ≈ 50 mùa BCTC; đây là dữ
liệu BCTC sẵn có chứ không phải dữ liệu mới, và sẽ là trial thứ 7 trong họ "biến thời điểm" đã 0/6.

---

## 6. NÊN KHÔNG LÀM (và vì sao)

| Không làm | Lý do |
|---|---|
| Momentum hàng hoá → mua cổ phiếu, dưới mọi biến thể | 17 trial, 0 qua cổng; cổ phiếu chạy cùng tháng với hàng hoá (IC 0,23) và không có độ trễ khai thác được (IC 0,04–0,05). Paper PREREG-2 (ô 1,05/3M, cổng 2028-01-31) đang tự trả lời |
| Quét mù series × ngành × độ trễ | Minh hoạ: 152 chuỗi × 19 nhóm ICB × 3 độ trễ = 8.664 ô; ở α = 0,05 kỳ vọng ~433 ô "có ý nghĩa" giả. Bắt buộc đi từ giả thuyết ngành trước, số trial khai trước |
| Thêm cap hoặc chỉnh tham số DT5G từ dữ liệu TE | N = 3–11 episode; luật "đừng re-tune theo lịch sử"; DT5G là bảo hiểm |
| Cổng regime/edge cho BAL, LAG | 0/6 biến thời điểm; cổng tháng NO-GO (−2,6…−2,8pp); BAL edge-gate NO-GO |
| Sổ giao dịch theo ngành | 20 sector sweep, phán quyết đồng nhất LENS not BOOK |
| Dùng `ticker_foreign_flow` / `ticker_prop_flow` lúc này | chỉ 3 mã; cấp chỉ số đã NO-GO hai lần |
| Backtest series tháng/quý của `macro_indicator` không có độ trễ | nhìn trộm tương lai (không PIT) |
| Dùng các mã TE sai hàng | `hrc_steel` (Mỹ), `rice` (CBOT), `coffee` (Arabica), `lean_hogs` (CME), `soda_ash`, `phosphate_rock_cny` |
| Dùng `commodity_latest` / `commodity_prices_unified` | trộn nguồn, đổi đơn vị ngầm |
| Dùng `stock_news` làm "tin tức PIT" để mở lại LAG thoát sớm | bảng chỉ có 8 loại sự kiện doanh nghiệp |
| Đưa nowcast vào value_score | trùng thông tin với phạt đỉnh LN; và không selector nào đọc value_score |
| Đề xuất lại: SUE-tilt, composite v3 làm selector, sector lens cho custom30V, stop-loss LAG | đã NO-GO, có file đóng |

---

## 7. MA TRẬN "DỮ LIỆU → NGÀNH VN → MÃ"

Cột "Bằng chứng": số IC là IC nowcast LN đã đo 26/10 (`commodity_cycle_te_20261026`); "giả thuyết" = chưa đo.

| Dữ liệu (nguồn, từ năm) | Ngành | Hưởng lợi khi giá tăng | Bị hại khi giá tăng | Bằng chứng |
|---|---|---|---|---|
| `rubber` TSR20 (TE, 2016) | Cao su | DRI, PHR, DPR, TRC, GVR | DRC, CSM (lốp) | IC 0,48 |
| `brent` (TE, 2016) | Dầu khí thượng nguồn | PVS, PVD, PVC, PVB, GAS | — | IC 0,03 (độ trễ hợp đồng) |
| `te_crack_spread_index` (TE) | Lọc dầu | BSR | — | IC 0,69 |
| `urea` (TE, 2019-06) | Phân đạm | DPM, DCM | — | IC 0,93 |
| `di_ammonium` (TE, 2019-06) | Phân lân/DAP | DDV, LAS | — | IC 0,53 |
| `sulfur` (TE, 2020) | Hoá chất, lân | — | DDV, LAS, DGC | −0,35 (chỉ LAS đúng dấu ở cấp mã) |
| `yellow_phosphorus` (SunSirs, 2018) | Phốt pho | DGC, PAT | — | IC 0,46–0,50; **gãy từ 2024 (−0,21)** |
| `caustic_soda` (SunSirs, 2023-09) | Xút-clo | CSV | — | giả thuyết; lịch sử ngắn |
| `liquid_ammonia` (SunSirs, 2018) | Phân bón | chỉ báo chiều TQ | DDV (đầu vào; **không** phải giá Tampa) | giả thuyết |
| `sugar` (TE, 2016) | Đường | SBT, LSS, QNS | — | IC 0,43 |
| `steel` thép cây SHFE (TE, 2016) | Thép | HPG, TLH, SMC, (HSG, NKG banned) | — | IC 0,35 |
| `iron_ore`, `coking_coal`, `coke` | Thép | — | HPG | −0,49 / −0,47 |
| `tungsten_apt`, `tungsten_concentrate` (SunSirs, 2026-06-24) | Vonfram | MSR | — | giả thuyết; chỉ 133 quan sát |
| `baltic_dry` (TE, 2016) | Vận tải hàng khô | VOS | — | IC 0,63 |
| `containerized_freight_index` (TE, 2016) | Container | HAH | — | IC 0,49 |
| `polyvinyl` (TE) | Ống nhựa | — | BMP, NTP | −0,29…−0,49 (nhóm đầu vào) |
| `pta`, `polyester_staple_fiber`, `ethylene_glycol`, `cotton_yarn` (SunSirs) | Sợi, dệt | STK (biên) | TCM, MSH (đầu vào) | giả thuyết |
| `hog_price_vn.csv` (2019) + `corn`, `soybean_meal_cny` | Chăn nuôi | DBC, BAF (biên heo − TACN) | — | sweep #17 CONFIRMED ở mức lens |
| `coal` Newcastle (TE) | Than, nhiệt điện | (than TKV: giá điều tiết) | QTP, PPC | giả thuyết yếu |
| `lpg`, `propane` | Khí hoá lỏng | — | — | giả thuyết (biên phân phối) |
| `gold` | Trang sức | — | PNJ (dấu không rõ) | giả thuyết |
| `vn_retail_sales_yoy` | Bán lẻ | MWG, FRT, DGW, PNJ, PET | — | giả thuyết (A4 họ 7) |
| GTGD toàn thị trường (tự tính) | Chứng khoán | SSI, VCI, HCM, VND, SHS, MBS | — | giả thuyết (A4 họ 8) |
| `vn_tourist_arrivals` | Hàng không, sân bay | ACV, SCS, SAS | — | giả thuyết (A4 họ 9) |
| `vn_exports` + `vn_imports` | Cảng | GMD, VSC, PHP | — | giả thuyết (A4 họ 10) |
| `vn_car_registrations` | Ô tô | VEA, HAX | — | giả thuyết (A4 họ 11) |
| `vn_fdi`, `vn_ind_production_yoy`, `vn_mfg_pmi` (PMI chỉ từ 2023-09) | KCN | (ánh xạ lỏng) | — | **không đưa vào A4** — không viết được câu nhân quả trực tiếp |
| `vn_interbank_3m`, `vn_policy_rate`, `vn_bond_10y` | Ngân hàng | — | NIM khi chi phí vốn tăng | giả thuyết (A4 họ 12) |
| `vn_gdp_construction` (quý) | Xây dựng, VLXD | CTD, VCG, HT1 | — | giả thuyết; trễ công bố dài |
| ONI/ENSO | Thuỷ điện, nông sản | — | — | chưa có ánh xạ; **nằm không** |

---

## 8. KHOẢNG TRỐNG DỮ LIỆU — yêu cầu cụ thể cho bq_admin (xếp theo ưu tiên)

1. **`ticker_foreign_flow`, `ticker_prop_flow`:** hiện chỉ FPT, SHS, ROS. Cần toàn bộ mã trong universe (334 mã ở
   phiên 18/11) cộng dòng cấp chỉ số VNINDEX/VN30; lịch sử từ 2014; `fetched_at` không ghi đè.
2. **`macro_indicator`:** thêm cột ngày công bố hoặc `first_seen_at` không bị ghi đè (hiện `fetched_at` đổi mỗi lần
   scrape). Nếu không làm được, fleet tự chụp (A1).
3. **TE monthly:** dừng nạp từ 2026-10-25 (20 khoá STALE). Xác nhận chủ ý hay lỗi; nếu chủ ý thì xoá hẳn để tránh
   đọc nhầm.
4. **`vn30f_daily`:** đứng từ 2026-06-08. Nối lại hoặc đánh dấu bỏ.
5. **Chuỗi hàng hoá còn thiếu** (đã xin 26/10, vẫn chưa có): cước tàu dầu BDTI/BCTI (PVT, VIP, GSP) · HRC Trung
   Quốc/VN (HPG) · cá tra, tôm (VHC, ANV, IDI) · Robusta, tiêu, điều, gạo VN 5% theo ngày · NH3 Tampa CFR · kali
   theo ngày · lịch sử vonfram trước 2026-06.
6. **Hoạt động ngành chưa có trong DB:** tín dụng và huy động toàn hệ thống theo tháng (snapshot FiinPro dừng
   2026-07, chuỗi tiền gửi gãy 10/2025) · giải ngân đầu tư công tháng · sản lượng điện, giá thị trường điện, cơ cấu
   huy động thuỷ điện/nhiệt điện (38 mã tuyến POWER) · sản lượng container qua cảng · doanh số căn hộ sơ cấp, phát
   hành và chậm trả TPDN · dư nợ margin toàn thị trường.
7. **Ngân hàng:** NPL, bao phủ nợ xấu, CAR, CASA theo quý sau 2026Q2 (lens ngân hàng 8L đang BLOCKED-STALE).
8. **Tin tức chung theo mã** (nếu user muốn theo đuổi hướng "feature ngoài giá" cho LAG): `stock_news` hiện chỉ có
   8 loại sự kiện doanh nghiệp.

---

## 9. CÂU HỎI CẦN USER QUYẾT

1. **A1 — duyệt chụp vintage hằng ngày** `macro_indicator` + `commodity_prices` vào dataset của fleet (`tav2_mike`)?
   Đây là bảng mới trong dataset của fleet, không phải view trong `tav2_bq`. Khuyến nghị: duyệt; việc này có hạn theo
   thời gian vì PIT không lấy lại được.
2. **A2 — chuyển danh sách §8 cho bq_admin?** Ưu tiên mục 1, 2, 7.
3. **A4 — duyệt ngân sách 12 trial** đo nowcast KQKD (không đo giá)? Tổng trial của dòng nghiên cứu lên 29.
4. **C1 — mở sổ cảnh báo vĩ mô** (Làn 3 chờ từ 05/11), chấp nhận trước rằng có thể mãi chỉ là hiển thị?
5. **Kỳ vọng:** bằng chứng hiện có nói dữ liệu ngành/hàng hoá sẽ **không** nhanh chóng vá BAL/LAG; giá trị gần nhất
   là hiển thị, soát plan và sleeve discretionary/DD. Nếu user muốn một sleeve MỚI chạy bằng nowcast ngành thì điều đó
   đi ngược phán quyết LENS not BOOK của 20 sector sweep — cần chỉ đạo rõ.

**Ba việc nên dispatch đầu tiên**
1. **Winston (sonnet/medium):** soạn yêu cầu bq_admin theo §8; nếu câu 1 được duyệt thì dựng snapshot + selfcheck.
2. **Taylor (opus/medium) → quant-skeptic:** A3 đóng băng bản đồ v2 rồi A4 đo nowcast KQKD 12 họ theo PREREG.
3. **Taylor (sonnet/medium):** A5 quy kết theo ngành × giai đoạn có CI ở cả pin0% và pin1M, kèm bước 1 của B2 (đếm số
   lần cổng ≤3 đổi).

---

## Phụ lục A — file trong thư mục này
- `appendix_commodity_keys.csv` — 256 dòng (khoá × nguồn × cadence): đơn vị, số dòng, ngày đầu/cuối, tuổi, số giá
  trị khác nhau 90 ngày.
- `appendix_deals_by_sector_era.csv` — lệnh LAG/BAL theo nhóm ngành × giai đoạn (n, số tháng, TB, trung vị, win, PnL).
- `appendix_macro_trigger_episode_counts.csv` — số episode từng trigger, ngày kích hoạt, state DT5G lúc đó.

## Phụ lục B — những gì CHƯA kiểm trong phiên này
- Chưa đọc nguyên văn `vnindex_5state_registry.md` và `rating_8l_criteria.md`; review DT5G dựa trên docstring + tham
  số trong `macro_state_live.py` và CLAUDE.md.
- "28/41 series vĩ mô được đọc" là đếm tên series xuất hiện trong 5 file consumer (grep), chưa lần theo từng đường
  gọi. Chưa kiểm 10 mã `bank-nodata` có mã nào trong `universe_pit`; chưa kiểm ROE của STB/EIB/SSB trong lens.
- Bảng §4 không có khoảng tin cậy (để dành A5) và dựa trên ledger backtest, không phải lệnh live.
- Bảng §3.2 gióng series theo ngày quan sát, chưa áp độ trễ; chỉ để đếm N, không phải kiểm định.
- Bản đồ consumer (§1) do sub-agent grep, tôi không tự chạy lại từng pattern; 11 file chẩn đoán ở §4 do sub-agent
  trích, tôi đối chiếu chéo với các REPORT gốc đã tự đọc ở phần hàng hoá và discriminators.
- `srcwalk`: chỉ dùng outline để điều hướng; không rút kết luận "không ai gọi" từ nó.

## Phụ lục C — lệnh tái lập (đều chỉ đọc)
```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh; P=lithe-record-440915-m9
# 1.1 quy mô bảng
bq query --use_legacy_sql=false --project_id=$P 'SELECT table_id,row_count,TIMESTAMP_MILLIS(last_modified_time) FROM `lithe-record-440915-m9.tav2_bq.__TABLES__`'
bq query --use_legacy_sql=false --project_id=$P 'SELECT source,cadence,COUNT(DISTINCT metric_key),COUNT(*),MIN(observation_date),MAX(observation_date),MAX(fetched_at) FROM tav2_bq.commodity_prices GROUP BY 1,2'
bq query --use_legacy_sql=false --project_id=$P 'SELECT ticker,COUNT(*),MIN(time),MAX(time) FROM tav2_bq.ticker_foreign_flow GROUP BY 1'   # tương tự ticker_prop_flow
bq query --use_legacy_sql=false --project_id=$P 'SELECT code,COUNT(*) FROM tav2_bq.stock_news, UNNEST(SPLIT(matched_event_codes,",")) code GROUP BY 1'
bq query --use_legacy_sql=false --project_id=$P 'SELECT series_key,observation_date,MIN(DATE(fetched_at)) FROM tav2_bq.macro_indicator WHERE country="VN" AND observation_date>="2026-09-30" GROUP BY 1,2'
# 1.3 universe theo ICB: join tav2_mike.universe_pit (MAX(time), in_universe) với tav2_bq.ticker_1m (MAX(time))
# 2.2 tuyến 8L của mã hàng hoá: data/rating_8l.csv  x  research/commodity_cycle_te_20261026/commodity_map_te.csv (tier A,B)
# 3.2 episode: macro_indicator (8 series ngày, từ 2012) gióng lên lịch tav2_bq.vnindex_5state_dt5g_live, ffill,
#     kích hoạt lần đầu + thời gian chết 126 phiên
# 4   lệnh theo ngành: research/lag_bal_discriminators_20261025/features.csv, lọc abandoned==0 & mtm==0
#     độ tươi: data/commodity_freshness_state.json (ref_date 2026-11-19: 236 OK / 20 STALE)
```
