---
kind: derived-file
status: DERIVED có bẫy — tổng năm khớp GSO (2018-2020, 2022-2023 ≤0,2%; 2021/2024 lệch −1,0%/−0,6%); GÃY CHUỖI 2020→2021
source: data/fiinprox_gdp_nominal_quarterly_20260914.csv
group: macro
writer: Mike (thủ công qua MCP tool call, KHÔNG có script/cron)
upstream: FiinXMCP `get_economy(metrics=["gdp_sector"], topic="gdp_by_sector", is_nominal=True, is_value=True)` — FiinPro-X trial
created: 2026-09-14
---

# `fiinprox_gdp_nominal_quarterly` — GDP danh nghĩa theo quý (tỷ VND)

37 dòng: 2015Q1-2017Q1 chỉ có Q1; đủ 4 quý từ 2018Q1→2026Q2 (Q3/Q4-2026 chưa công bố). Giá trị
TỪNG QUÝ (không cộng dồn). Cột: `gdp_bn_vnd`, `real_estate_bn_vnd`, `construction_bn_vnd`,
`finance_bn_vnd`, `series_vintage`. Provider có ~25 ngành cấp 2 — chưa lấy.

Harvest 4 lệnh: provider KHÔNG cross-join `year` list × `quarter` list (chỉ trả quý đầu tiên) ⇒ phải
gọi 1 lệnh / quý.

## Bẫy
1. **GÃY CHUỖI 2020→2021 (+33% danh nghĩa, không thể là tăng trưởng thật)**: 2018-2020 là số GSO
   TRƯỚC khi đánh giá lại quy mô GDP (2020 = 6.293 nghìn tỷ, bản cũ); 2021+ là bản đã đánh giá lại
   (~+25-30%). Cột `series_vintage` đánh dấu. **Không tính tín dụng/GDP, tỷ trọng BĐS/GDP hay tăng
   trưởng danh nghĩa qua mốc 2021** mà không nối chuỗi.
2. Tín dụng/GDP: dùng cùng vintage cả tử lẫn mẫu.

↩ [Về nhóm macro](index.md) · [Về index tổng](../index.md)
