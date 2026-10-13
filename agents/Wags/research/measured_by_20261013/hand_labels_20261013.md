# Soi tay 24 finding bị cảnh báo (mẫu ngẫu nhiên seed=20261013, luật RULE_VERSION=1)

Nguồn mẫu: `measure_bus_20261013.out` (các dòng `[0]`…`[23]`). Người soi: Wags, đọc payload thật.
Tiêu chí "báo nhầm" (FP): payload KHÔNG chứa đại lượng nào được trình bày như kết quả đo/đếm —
token số chỉ là mã định danh, tham số thiết kế, hoặc mảnh vụn.

| # | Nhãn | Ghi chú |
|---|---|---|
| 0,2,3,4,6,9,10,11,13,14,16,21,22,23 | ĐÚNG | số đo thật: selfcheck PASS/FAIL, diffstat, CAGR, tỉ lệ giá, tiền |
| 12,15,17 | ĐÚNG (yếu) | chỉ có số ĐẾM đơn giản (4 incidents, 25/25, n_orders=0) |
| 1,5,7,19 | ĐÚNG, do SCRIPT ghi | `sbv-weekly-check` `current_rate: 4.5`, không trace_id — số do cron ghi |
| 8 | FP | `wire-confirmed-fixA-fixB`: '2','30' là mảnh của "2fixes"/nhãn, không có số đo |
| 18 | FP | `ops-autofix-done`: 'argc=7', 'idx 24' là mã định danh |
| 20 | FP | đề xuất văn bản luật: 45 ngày / 7,5% là THAM SỐ, không phải số đo |

**FP = 3/24 = 12,5%** (Wilson 95% ≈ 4%–31%, mẫu nhỏ). Do script/cron ghi: 4/24.
Vòng soi trước (luật nháp, 24 ngẫu nhiên + 12 ca ít token): FP 3/24 ngẫu nhiên, 3/12 ở nhóm ≤3 token.
