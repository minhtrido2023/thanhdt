---
kind: bq-table
status: CANONICAL-WITH-TRAPS
source: tav2_bq.commodity_prices (TABLE) + tav2_bq.commodity_prices_unified (VIEW) + tav2_bq.commodity_latest (VIEW)
group: feeds
cadence: daily (TE) / monthly (TE, WB) / event (GDT)
writer: bq_admin (user xác nhận 2026-10-26); nguồn TradingEconomics; cron làm mới chưa thấy trong repo
verified: 2026-10-26 (job Winston_20261026_065210, đo trực tiếp BQ)
---

# `tav2_bq.commodity_prices` (+ 2 view)

**Status: CANONICAL-WITH-TRAPS** — dữ liệu sạch (không trùng khoá, không NULL value) nhưng 3 bẫy chọn nguồn bên dưới. Chưa có consumer nào trong repo (grep `commodity_prices|commodity_latest` toàn `WorkingClaude/`, `tools/`, `discord_bot/`: 0 hit .py/.sh) → chưa wire vào production.

## Schema (đo 2026-10-26)
12 cột: `metric_key` STR · `name_vn` · `name_en` · `observation_date` DATE · `value` FLOAT · `unit` STR · `change_pct` FLOAT · `cadence` STR · `source` STR · `source_url` · `fetched_at` TIMESTAMP · `extra_json` STR.
PARTITION MONTH(`observation_date`) · CLUSTER (`metric_key`, `source`). **296.520 dòng**, 0 NULL `value`.
Khoá duy nhất = (`metric_key`,`source`,`cadence`,`observation_date`) → 296.520/296.520 distinct. ⚠️ KHÔNG gồm `cadence` thì có trùng (281.305 distinct): TE ghi cả dòng daily lẫn monthly cùng ngày (vd phosphorus, silicon, aluminum_alloy 2026-10-22 ×2).
`lastModifiedTime` bảng = 2026-10-25 13:16 UTC.

## 3 nguồn
| source | cadence | số mã | phủ | mới nhất |
|---|---|---|---|---|
| trading_economics | daily | 103 | 2016-10-25 → | 2026-10-23 |
| trading_economics | monthly | 103 | 1912-05 → | 2026-10-22 |
| worldbank_cmo | monthly | 22 | 1960-01 → | 2026-09-01 (nhịp WB bình thường, ra đầu tháng sau) |
| global_dairy_trade | event | 1 (`gdt_milk_powder`) | 2026-04-21 → (13 dòng) | 2026-10-20 |

## View
- `commodity_prices_unified`: giữ dòng `daily` + dòng monthly của (metric_key, tháng) **chưa có dòng daily nào (bất kỳ source)**.
- `commodity_latest`: từ unified, mỗi `metric_key` 1 dòng, `ORDER BY observation_date DESC, fetched_at DESC`. Không có cột báo nguồn thắng ngoài `source` (có cột nhưng không cố định).

## BẪY
1. **Cùng `metric_key`, hai nguồn lệch mức/đơn vị** (đo):
   - `brent` T9/2026: TE daily-avg 100,8 (TE monthly 98,0) vs WB **116,8** (−13,7%). Lưu ý TE spot 2026-10-23 = 116,72 ≈ WB T9 → WB T9 có thể không phải trung bình tháng chuẩn; CHƯA giải thích được. Lịch sử 2016-10→: TE-daily-avg vs WB trung bình |lệch| 1,7%, max 15,9%.
   - `rubber`: TE `USD Cents / Kg` (~254) = hạng **TSR20** (khớp cột tsr20 của rubber_weekly.csv: −0,45% ±1,9%), WB `$/kg` (~2,75) = **RSS3**. Khác loại hàng, không phải khác đơn vị thuần: ÷100 vẫn lệch 13–23% so với RSS3.
   - `urea`: TE-daily-avg vs WB trung bình |lệch| 9,2% (median +4,2%, max 30,9%).
   - `iron_ore`: unit TE `USD/T` vs WB `$/dmtu`; lệch TB 2,0%.
2. **`commodity_latest` chọn nguồn ngầm** theo `observation_date` mới nhất. TE daily (10-23) luôn thắng WB monthly (09-01) → giá trị VÀ đơn vị đổi khi TE ngừng cập nhật một mã (tea 23 ngày, salmon 10 ngày tính tới 26/10). Hệ quả nặng hơn: `unified` **xoá dòng WB trong mọi tháng đã có daily TE** (WB brent T9 KHÔNG xuất hiện trong unified/latest). **Luôn truy vấn `commodity_prices` với `source=` tường minh, KHÔNG dùng `commodity_latest` cho số đưa vào mô hình/báo cáo.**
3. **TE không cập nhật đều**: tea (INR/Kgs) mới nhất 2026-10-03, salmon (NOK/KG) 2026-10-16. Kiểm `MAX(observation_date)` theo mã trước khi dùng.
4. `fetched_at` KHÔNG phải độ trễ thật: TE daily backfill một lượt (toàn bộ `fetched_at` cùng 2026-10-25 / 10-24) → không đo được latency từng ngày.

## Quy tắc chọn nguồn đề xuất (Winston, chờ Taylor/Mike xác nhận)
- Chuỗi tháng / lịch sử / nối với các `data/*_monthly.csv` hiện có → **`source='worldbank_cmo'`** (trùng 246/246 tháng với csv brent/urea/iron_ore/dap, lệch 0,00).
- Nowcast trong tháng / tín hiệu daily → **`source='trading_economics', cadence='daily'`**, chỉ dùng ≥2016-10-25, và **không nối** với chuỗi WB thành một series (khác định nghĩa, lệch tới 15–31%).
- Hai nguồn lệch >5% trên cùng tháng → coi là khác series, ghi rõ `source` + `unit` vào output; không trung bình, không ffill chéo nguồn.
- rubber: TE = TSR20, WB = RSS3. Chọn theo hạng hàng cần.

## Ai ghi
**[CẬP NHẬT 2026-10-26, user xác nhận]** Writer = **bq_admin**, lấy từ TradingEconomics: `commodity_prices` = lịch sử, `commodity_latest` = giá mới nhất; tần suất mục tiêu cập nhật theo NGÀY, nhưng KHÔNG phải mọi mã đều có giá hằng ngày. Đo 26/10 trên TE daily (43 phiên gần nhất, 08-26→10-23): 83 mã có ≥38 phiên (gần hằng phiên); 18 mã 37 phiên (~86%: nhóm TQ — aluminum_alloy, silicon, tellurium, germanium, methanol, lithium, neodymium, indium, gallium, manganese, molybden, phosphorus, magnesium, steel, titanium, bitumen, iron_ore_cny, consume_commodity_index); 2 mã rất thưa: tea (5, cuối 10-03), salmon (8, cuối 10-16). Cron/lịch của bq_admin nằm ngoài repo này — hỏi bq_admin nếu cần SLA.

(Ghi chú cũ trước khi biết writer:) **Không tìm ra writer.** Không script/cron nào trong repo, crontab, `tools/`, `discord_bot/` tham chiếu bảng; không đọc được `INFORMATION_SCHEMA.JOBS_BY_PROJECT` (thiếu `bigquery.jobs.listAll`); `bq ls -j` không lộ câu lệnh. Dấu vết: `fetched_at` 2026-10-24 17:07 → 2026-10-25 11:13 (UTC) = nạp theo đợt ngày 24–25/10, bảng tạo 2026-10-25 12:38 UTC. Nghi tạo thủ công/ngoài repo (cùng `dtienthanh@gmail.com`). Lịch làm mới do bq_admin (ngoài repo). Đã xác nhận: bq_admin.

## THIẾU so với nhu cầu fleet
Giá heo hơi VN (đã có `data/hog_price_vn.csv`, ngoài BQ) · thủy sản VN (tôm, cá tra) · hồ tiêu · điều · thép cây nội địa · SCFI/WCI (cước container) · PTA/polyester · potash/amoniac chuỗi ngày (WB có `potassium_chloride` monthly; TE daily chưa kiểm) · chuỗi ngày chỉ từ 2016-10-25.
Đối chiếu sâu: `kb/projects/commodity-tables-eval-20261026.md`.

↩ [Về feeds](index.md)
