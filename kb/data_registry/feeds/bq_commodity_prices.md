---
kind: bq-table
status: CANONICAL-WITH-TRAPS
source: tav2_bq.commodity_prices (TABLE) + tav2_bq.commodity_prices_unified (VIEW) + tav2_bq.commodity_latest (VIEW)
group: feeds
cadence: daily (TE, sunsirs) / monthly (TE, WB) / event (GDT)
writer: bq_admin (user xác nhận 2026-10-26); nguồn TradingEconomics; cron làm mới chưa thấy trong repo
verified: 2026-10-26 chiều (job Winston_20261026_102704, đo trực tiếp BQ; thêm nguồn sunsirs)
---

# `tav2_bq.commodity_prices` (+ 2 view)

**Status: CANONICAL-WITH-TRAPS** — dữ liệu sạch (không trùng khoá, không NULL value) nhưng 3 bẫy chọn nguồn bên dưới. Chưa có consumer nào trong repo (grep `commodity_prices|commodity_latest` toàn `WorkingClaude/`, `tools/`, `discord_bot/`: 0 hit .py/.sh) → chưa wire vào production.

## Schema (đo 2026-10-26)
12 cột: `metric_key` STR · `name_vn` · `name_en` · `observation_date` DATE · `value` FLOAT · `unit` STR · `change_pct` FLOAT · `cadence` STR · `source` STR · `source_url` · `fetched_at` TIMESTAMP · `extra_json` STR.
PARTITION MONTH(`observation_date`) · CLUSTER (`metric_key`, `source`). **343.272 dòng / 134 mã** (sau khi thêm sunsirs 26/10 chiều; trước đó 296.520), 0 NULL `value`.
Khoá duy nhất = (`metric_key`,`source`,`cadence`,`observation_date`) → 343.272/343.272 distinct (kiểm lại 26/10 chiều, dup=0 — khoá còn đúng sau khi thêm sunsirs). ⚠️ KHÔNG gồm `cadence` thì có trùng (281.305 distinct): TE ghi cả dòng daily lẫn monthly cùng ngày (vd phosphorus, silicon, aluminum_alloy 2026-10-22 ×2).
`lastModifiedTime` bảng = 2026-10-25 13:16 UTC.

## 4 nguồn
| source | cadence | số mã | phủ | mới nhất |
|---|---|---|---|---|
| trading_economics | daily | 103 | 2016-10-25 → | 2026-10-23 |
| trading_economics | monthly | 103 | 1912-05 → | 2026-10-22 |
| worldbank_cmo | monthly | 22 | 1960-01 → | 2026-09-01 (nhịp WB bình thường, ra đầu tháng sau) |
| sunsirs | daily | 23 (CNY, spot Trung Quốc; chi tiết mục "Nguồn sunsirs") | 2013-01-07 → (mã sớm nhất) | 2026-10-23 |
| global_dairy_trade | event | 1 (`gdt_milk_powder`) | 2026-04-21 → (13 dòng) | 2026-10-20 |

## View
- `commodity_prices_unified`: giữ dòng `daily` + dòng monthly của (metric_key, tháng) **chưa có dòng daily nào (bất kỳ source)**.
- `commodity_latest`: từ unified, mỗi `metric_key` 1 dòng, `ORDER BY observation_date DESC, fetched_at DESC`. Không có cột báo nguồn thắng ngoài `source` (có cột nhưng không cố định).

## BẪY
0. **(26/10 chiều) sunsirs — xem BẪY 6 bên dưới.** View `unified`/`latest` đã gộp sunsirs (mọi dòng sunsirs là `daily`), 0 mã sunsirs trùng `metric_key` với nguồn khác ⇒ KHÔNG có "nguồn thắng đổi giữa các lần chạy" cho 23 mã này.
1. **Cùng `metric_key`, hai nguồn lệch mức/đơn vị** (đo):
   - `brent` T9/2026: TE daily-avg 100,8 (TE monthly 98,0) vs WB **116,8** (−13,7%). Lưu ý TE spot 2026-10-23 = 116,72 ≈ WB T9 → WB T9 có thể không phải trung bình tháng chuẩn; CHƯA giải thích được. Lịch sử 2016-10→: TE-daily-avg vs WB trung bình |lệch| 1,7%, max 15,9%.
   - `rubber`: TE `USD Cents / Kg` (~254) = hạng **TSR20** (khớp cột tsr20 của rubber_weekly.csv: −0,45% ±1,9%), WB `$/kg` (~2,75) = **RSS3**. Khác loại hàng, không phải khác đơn vị thuần: ÷100 vẫn lệch 13–23% so với RSS3.
   - `urea`: TE-daily-avg vs WB trung bình |lệch| 9,2% (median +4,2%, max 30,9%).
   - `iron_ore`: unit TE `USD/T` vs WB `$/dmtu`; lệch TB 2,0%.
2. **`commodity_latest` chọn nguồn ngầm** theo `observation_date` mới nhất. TE daily (10-23) luôn thắng WB monthly (09-01) → giá trị VÀ đơn vị đổi khi TE ngừng cập nhật một mã (tea 23 ngày, salmon 10 ngày tính tới 26/10). Hệ quả nặng hơn: `unified` **xoá dòng WB trong mọi tháng đã có daily TE** (WB brent T9 KHÔNG xuất hiện trong unified/latest). **Luôn truy vấn `commodity_prices` với `source=` tường minh, KHÔNG dùng `commodity_latest` cho số đưa vào mô hình/báo cáo.**
3. **TE không cập nhật đều**: tea (INR/Kgs) mới nhất 2026-10-03, salmon (NOK/KG) 2026-10-16. Kiểm `MAX(observation_date)` theo mã trước khi dùng — hoặc đọc **`data/commodity_freshness_state.json`** (status theo khoá `metric_key|source|cadence`: OK/STALE/FROZEN_VALUE/LOW_SAMPLE), sinh bởi `mike/bin/commodity_freshness_monitor.py` (từ 2026-10-26; cron CHƯA cài — kiểm `ref_date` trong file trước khi tin).
4. `fetched_at` KHÔNG phải độ trễ thật: TE daily backfill một lượt (toàn bộ `fetched_at` cùng 2026-10-25 / 10-24) → không đo được latency từng ngày.
5. **Bẫy TE mới (user duyệt 2026-10-26; nguồn `agents/Taylor/research/commodity_cycle_te_20261026/REPORT.md` §1 + `te_key_stats.csv`; số dưới đây ĐO LẠI từ BQ `source='trading_economics', cadence='daily'` cùng ngày).** Mã TE tên nghe đúng nhưng hàng khác hàng cổ phiếu VN cần:
   - `phosphorus` (CNY/T): median 1.027,5, khoảng 845–1.125 = **quặng photphat**, KHÔNG phải P4/phốt pho vàng (cỡ 20–30k CNY/t, `ước lượng` theo hiểu biết thị trường). Chỉ từ 2022-08-19, 1.009 phiên nhưng **43 giá trị khác nhau** (94% phiên đứng giá) → vô dụng cho DGC/PAT.
   - `hrc_steel` (USD/T): đỉnh **1.945 ngày 2021-08-31**, median 805 = HRC **Mỹ**, không phải HRC TQ/VN (HPG).
   - `rice` (USD/cwt): median 13,03, 9,2–22,1 = gạo thô CBOT, không phải gạo VN 5%.
   - `coffee` (USd/Lbs): median 161,8, đỉnh 433 = **Arabica**; VN chủ yếu Robusta.
   - `lean_hogs` (USd/Lbs): median 80,7 = CME Mỹ, không đồng pha với heo hơi VN.
   - `soda_ash` (CNY/T): Na2CO3 (median 1.846; 1.025–3.688), KHÔNG phải xút/caustic soda (CSV).
   - `sulfur` (CNY/T): 2020 median 653 → 2026 median 7.392, đỉnh **11.084 (2026-06)**, median 2026/median 2020 = ×11,3 (REPORT ghi "×7" là so đỉnh 11.084 với trung vị toàn kỳ ≈1.477 → ×7,5; hai phép so khác nhau). Đã xác minh 2026-10-26: **THẬT**, không phải đổi đơn vị/series — chi tiết mục "Xác minh sulfur" dưới. Hiện đã hạ về 5.714 (−26%/tháng).

6. **Bẫy sunsirs (đo 26/10 chiều, job Winston_20261026_102704).** (a) Đơn vị **CNY/T** (22 mã), `glass` **CNY/m2**, `live_hog_cny` **CNY/kg** — không phải USD của TE; cộng/so với cột TE/WB phải đổi tiền + đơn vị. (b) Tên gần TE nhưng **khác hàng/khác khoá**: `coke` (sunsirs, CNY/T, 2.125) ≠ TE `coking_coal` (USD/T); `wire_rod` (3.365) ≠ TE `steel` (CNY/T) ≠ `hrc_steel` (USD/T HRC Mỹ); `soybean_meal_cny` (3.326 CNY/T) ≠ WB `soybean_meal` ($/mt); `butadiene_rubber` ≈ TE `synthetic_rubber` (corr mức 0,998 trên 89 phiên 2026-06-22→10-23, sunsirs cao hơn ~1% (16.440 vs 16.267 ngày 10-23), KHÔNG phải cùng một chuỗi); `live_hog_cny` ≠ TE `lean_hogs` (USd/Lb, CME). (c) Tên khoá chỉ trùng ý nghĩa, **không có `metric_key` nào trùng** giữa sunsirs và nguồn khác (kiểm bằng query) ⇒ dedup theo khoá không bắt được; chọn nguồn thủ công. (d) `extra_json` rỗng, `source_url` = `sunsirs.com/uk/prodetail-<id>.html`; `change_pct` đã có. (e) Khoảng trống: gap lớn nhất 11 ngày = Tết 2026 (hết 2026-02-24) ở mọi mã; không có khoảng trống nào khác >10 ngày trong 1 năm; `wire_rod` gap toàn lịch sử 46 ngày (cũ). (f) `fetched_at` cả 46.752 dòng = 2026-10-26 09:38:58 UTC (backfill một lượt) ⇒ cùng bẫy số 4. (g) Lần nạp đầu (26/10, T2) dừng ở 2026-10-23 (T6) — độ trễ nạp sunsirs chưa đo được từ 1 lần nạp.

## Nguồn sunsirs (thêm 2026-10-26 16:38 ICT, bq_admin)
`source='sunsirs', cadence='daily'`, 46.752 dòng, 23 mã, tới 2026-10-23. Độ phủ **40/40 phiên** trong cửa sổ 2026-08-21→10-23 cho cả 23 mã (đo; gần hơn TE: nhóm TQ của TE 37/43). Số dòng / lịch sử đầu / đơn vị (đo BQ):

| nhóm | mã (n dòng, từ) |
|---|---|
| dài (2013→) | coke 3.346 · glass 3.344 · pta 3.344 · rapeseed_meal 3.344 · soybean_meal_cny 3.346 · soybean_oil 3.346 · fuel_oil 3.335 · wire_rod 3.322 (đều từ 2013-01-07) |
| trung | ferrosilicon 2.948, silicomanganese 2.948 (2014-08-08) · cotton_yarn 2.223 (2017-08) · ethylene_glycol 1.905 (2018-12) · stainless_steel 1.712 (2019-09) · lpg 1.590 (2020-03) · polyester_staple_fiber 1.462 (2020-10) · live_hog_cny 1.399 (2021-01-08) |
| ngắn | butadiene_rubber 782 (2023-07) · caustic_soda 747 · paraxylene 747 (2023-09) · pet 505 (2024-09) · polysilicon 439 (2024-12) · benzene 314 (2025-07) · propylene 304 (2025-07) |

Monitor `commodity_freshness_monitor.py`: 23/23 sunsirs = **OK** (median_gap 1, p90_gap 3, ngưỡng STALE 5 ngày).

## Quy tắc chọn nguồn đề xuất (Winston, chờ Taylor/Mike xác nhận)
- Chuỗi tháng / lịch sử / nối với các `data/*_monthly.csv` hiện có → **`source='worldbank_cmo'`** (trùng 246/246 tháng với csv brent/urea/iron_ore/dap, lệch 0,00).
- Nowcast trong tháng / tín hiệu daily → **`source='trading_economics', cadence='daily'`**, chỉ dùng ≥2016-10-25, và **không nối** với chuỗi WB thành một series (khác định nghĩa, lệch tới 15–31%).
- Hai nguồn lệch >5% trên cùng tháng → coi là khác series, ghi rõ `source` + `unit` vào output; không trung bình, không ffill chéo nguồn.
- rubber: TE = TSR20, WB = RSS3. Chọn theo hạng hàng cần.

## Ai ghi
**[CẬP NHẬT 2026-10-26, user xác nhận]** Writer = **bq_admin**, lấy từ TradingEconomics: `commodity_prices` = lịch sử, `commodity_latest` = giá mới nhất; tần suất mục tiêu cập nhật theo NGÀY, nhưng KHÔNG phải mọi mã đều có giá hằng ngày. Đo 26/10 trên TE daily (43 phiên gần nhất, 08-26→10-23): 83 mã có ≥38 phiên (gần hằng phiên); 18 mã 37 phiên (~86%: nhóm TQ — aluminum_alloy, silicon, tellurium, germanium, methanol, lithium, neodymium, indium, gallium, manganese, molybden, phosphorus, magnesium, steel, titanium, bitumen, iron_ore_cny, consume_commodity_index); 2 mã rất thưa: tea (5, cuối 10-03), salmon (8, cuối 10-16). Cron/lịch của bq_admin nằm ngoài repo này — hỏi bq_admin nếu cần SLA.

(Ghi chú cũ trước khi biết writer:) **Không tìm ra writer.** Không script/cron nào trong repo, crontab, `tools/`, `discord_bot/` tham chiếu bảng; không đọc được `INFORMATION_SCHEMA.JOBS_BY_PROJECT` (thiếu `bigquery.jobs.listAll`); `bq ls -j` không lộ câu lệnh. Dấu vết: `fetched_at` 2026-10-24 17:07 → 2026-10-25 11:13 (UTC) = nạp theo đợt ngày 24–25/10, bảng tạo 2026-10-25 12:38 UTC. Nghi tạo thủ công/ngoài repo (cùng `dtienthanh@gmail.com`). Lịch làm mới do bq_admin (ngoài repo). Đã xác nhận: bq_admin.

## THIẾU so với nhu cầu fleet
**[Cập nhật 26/10 chiều sau sunsirs]** ĐÃ LẤP: PTA/polyester (`pta`, `polyester_staple_fiber`, `pet`, `paraxylene`, `ethylene_glycol` — CNY), xút (`caustic_soda`, CNY/T, từ 2023-09), heo TQ (`live_hog_cny`, từ 2021-01; chỉ xu hướng TQ). VẪN THIẾU so với danh sách xin bq_admin: **vonfram**, **photpho vàng P4** (TE `phosphorus` = quặng photphat, vô dụng), **BDTI**, **HRC Trung Quốc** (`wire_rod`/TE `steel` là thép cây/dây, không phải HRC), **cá tra / thủy sản VN**; cộng các mục cũ: giá heo hơi VN (có csv ngoài BQ), hồ tiêu, điều, SCFI/WCI, potash/amoniac chuỗi ngày.
(Danh sách cũ trước 26/10 chiều:)
Giá heo hơi VN (đã có `data/hog_price_vn.csv`, ngoài BQ) · thủy sản VN (tôm, cá tra) · hồ tiêu · điều · thép cây nội địa · SCFI/WCI (cước container) · PTA/polyester · potash/amoniac chuỗi ngày (WB có `potassium_chloride` monthly; TE daily chưa kiểm) · chuỗi ngày chỉ từ 2016-10-25.
Đối chiếu sâu: `kb/projects/commodity-tables-eval-20261026.md`.

↩ [Về feeds](index.md)

**[bq_admin phản hồi 2026-10-26 14:1x, qua user]** Cập nhật **mỗi ngày lúc 23:00 ICT**; giá hằng ngày thay đổi theo realtime (snapshot lúc nạp). bq_admin **KHÔNG có cơ chế phát hiện mã ngưng cập nhật** — cadence không có quy luật chung: bảng lấy từ nhiều nguồn, có nguồn 1 tháng/lần, có nguồn 2 tuần/lần; riêng TE thì có mã cập nhật theo ngày, có mã theo tuần. ⇒ (1) dữ liệu 'hôm nay' chỉ có SAU 23:00 ICT, KHÔNG dùng cho tính toán trong ngày (đúng bright-line §6: same-day = DNSE, không BQ); (2) mã đứng giá ≠ giá không đổi: consumer phải tự kiểm `observation_date` của từng mã so với kỳ vọng cadence, KHÔNG tin 'dòng mới nhất' là tươi; (3) **ĐÃ CÓ monitor theo mã (2026-10-26, job Winston_20261026_073850)**: `mike/bin/commodity_freshness_monitor.py` (+ `_selfcheck.py`) → `data/commodity_freshness_state.json`. Luật STALE age > max(3×median_gap, p90_gap+2) + allowance lễ theo mùa; FROZEN_VALUE theo run giá đứng. Backtest 12 tháng 0,21 báo giả/tuần; chi tiết + trade-off: `kb/projects/commodity-freshness-monitor-20261026.md`. **Cron chưa cài** (chờ user).

## Xác minh sulfur TE 2026 (Winston, 2026-10-26) — kết luận: **THẬT**
- Series đi **liên tục**: median tháng 2025-06 2.346 → 2025-12 3.877 → 2026-03 4.805 → 04 6.369 → 05 7.232 → 06 9.007 (đỉnh ngày 11.084) → 09 8.010 → 10 (17 phiên) 6.921; phiên cuối 2026-10-23 = 5.714 (TE ghi −25,97%/tháng, +80,96% YoY). Không có bước nhảy đơn vị: biến động 1 phiên lớn nhất toàn chuỗi chỉ ×0,754 (2022-07-15) và ×0,856/×1,145 trong 2026 (06-17, 06-08).
- Đơn vị `CNY/T` nhất quán cả chuỗi; không đổi hợp đồng nhìn thấy được. Điểm TE 2026-04-07 = 6.733 (theo trang TE) khớp khoảng BQ tháng 4 (5.950–6.800).
- Tin thị trường: xung đột Trung Đông/đóng eo Hormuz (~½ cung lưu huỳnh toàn cầu), TQ nhập ~½ trong 9,6 tr t (2025) từ khu vực này; Mysteel: giá cảng Dương Tử 8.400 CNY/t (+13,2%/tuần), thắt cung, dầu khí nhà nước ưu tiên cấp cho phân bón. Argus lưu ý đà tăng đã có từ 2024-25 (nhu cầu niken Indonesia). Nguồn: [TE sulfur](https://tradingeconomics.com/commodity/sulfur), [Argus](https://www.argusmedia.com/en/news-and-insights/latest-market-news/2803156-sulphur-s-rally-pre-empts-middle-east-price-spike), [Mysteel](https://www.mysteel.net/news/5126917-sulfur-prices-soar-1321-on-tighter-supply-and-sales-restriction-policies), [SunSirs](https://www.sunsirs.com/uk/detail_news-31029.html). Chỉ đọc tiêu đề/tóm tắt, không đọc đầy đủ bài.
- Đối chiếu chuỗi liên quan trong bảng: WB không có lưu huỳnh; `dap` WB 583 (2025-01) → 801 (2026-09) = +37%; `phosphate_rock` WB 152,5 → 170 (+11%, WB đứng giá nhiều tháng); `urea` WB đỉnh 726 ở 2026-03 rồi về 408. ⇒ chi phí đầu vào lưu huỳnh tăng nhiều lần nhưng giá DAP chỉ tăng vừa → biên nhà sản xuất DAP/lân bị ép, hoặc chưa truyền hết (CHƯA đo).
- **Hệ quả cost (dữ kiện, không phải tín hiệu):** lưu huỳnh là nguyên liệu axit sunfuric cho chế biến lân. DDV, LAS (axit sunfuric/supe lân) và DGC (chuỗi photpho-hoá chất) có thể chịu chi phí đầu vào cao hơn rõ rệt giai đoạn 2026-03→09; mức độ truyền vào giá vốn từng mã CHƯA đo, cần đối chiếu BCTC Q2-Q3/2026. Giá đang rút (−26%/tháng) → áp lực cost giảm dần nếu kéo dài. Chưa suy ra tín hiệu mua/bán.
