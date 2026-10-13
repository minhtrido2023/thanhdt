# Soi tay 24 finding bị cảnh báo (mẫu ngẫu nhiên seed=20261013, luật RULE_VERSION=1)

Nguồn mẫu: `measure_bus_20261013.out` (các dòng `[0]`…`[23]`). Người soi: Wags, đọc payload thật.
Tiêu chí "báo nhầm" (FP): payload KHÔNG chứa đại lượng nào được trình bày như kết quả đo/đếm —
token số chỉ là mã định danh, tham số thiết kế, hoặc mảnh vụn.

| # | Nhãn | Ghi chú |
|---|---|---|
| 0,2,3,4,6,9,10,11,13,14,16,21,22,23 | ĐÚNG | số đo thật: selfcheck PASS/FAIL, diffstat, CAGR, tỉ lệ giá, tiền |
| 8,12,15,17 | ĐÚNG (yếu) | chỉ có số ĐẾM đơn giản (4 incidents, 25/25, n_orders=0; #8: "ca 2 file", "them 2 dong", "~30 shadow copies") |
| 1,5,7,19 | ĐÚNG, do SCRIPT ghi | `sbv-weekly-check` `current_rate: 4.5`, không trace_id — số do cron ghi |
| 18 | FP | `ops-autofix-done`: 'argc=7', 'idx 24' là mã định danh |
| 20 | FP | đề xuất văn bản luật: 45 ngày / 7,5% là THAM SỐ, không phải số đo |

**FP = 2/24 = 8,3%** (mẫu nhỏ, khoảng tin cậy rộng — đừng đọc như số chính xác). Do script/cron ghi: 4/24.

ĐÍNH CHÍNH (arch-review vòng 1): bản đầu gán #8 là FP với lý do "mảnh của 2fixes" — SAI, topic không
được quét; token đến từ payload ("ca 2 file", "them 2 dong") và payload còn có "~30 shadow copies",
đúng mẫu lỗi mục tiêu. Đã đọc lại payload trên bus trước khi sửa nhãn. Mẫu 24 ca không đổi sau khi
sửa luật vòng 2 (so bằng diff danh sách topic).
