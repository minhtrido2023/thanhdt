---
kind: derived-file
status: DERIVED (tổng tín dụng — khớp số NHNN cuối năm 2019-2024 ≤0,4pp) · UNVERIFIED (M2, tín dụng xây dựng, tiền gửi)
source: data/fiinprox_money_credit_monthly_20260914.csv
group: macro
writer: Mike (thủ công qua MCP tool call, KHÔNG có script/cron)
upstream: FiinXMCP `get_economy(metrics=["money_credit"], topic="money_supply_outstanding", data_type="YoY")` — FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_money_credit_monthly` — M2 / tín dụng / tiền gửi YoY theo tháng

161 dòng, 2012-12 + 2013-04→2026-07 (2013-01..03 provider không có; M2/tiền gửi hết 2026-06,
tín dụng tới 2026-07). Cột (% YoY): `m2_yoy_pct`, `credit_yoy_pct`, `credit_construction_yoy_pct`,
`dep_residents_yoy_pct`, `dep_econ_orgs_yoy_pct`. Harvest 2 lệnh (2012-2019, 2020-2026).
Provider còn 8 chuỗi tín dụng theo ngành khác (công nghiệp, thương mại, vận tải, nông nghiệp…) — chưa lấy.

## Đối chiếu
Tín dụng cuối năm vs số NHNN công bố: 2019 13,65 (NHNN 13,65) · 2020 12,17 (12,13) · 2021 13,61
(13,61) · 2023 13,79 (13,71) · 2024 15,09 (15,08) · 2022 14,17 (~14,5). Chưa đối chiếu M2/tiền gửi.

## Bẫy
1. **GÃY CHUỖI TIỀN GỬI từ 2025-10**: `dep_econ_orgs_yoy_pct` nhảy từ +18% (09/2025) xuống −20%,
   `dep_residents_yoy_pct` từ +12,6% lên +46%, M2 tổng thì liền mạch ⇒ gần như chắc chắn là đổi
   phân loại (chuyển nhóm tiền gửi giữa TCKT ↔ dân cư), KHÔNG phải dòng tiền thật. Không dùng 2 cột
   tiền gửi qua mốc này trước khi xác minh nguyên nhân.
2. Đây là tăng trưởng YoY, không phải số dư tuyệt đối (route `data_type="Value"` có, chưa lấy).
3. Không có chuỗi nào trong repo trước đây ⇒ không có đối chiếu nội bộ.

↩ [Về nhóm macro](index.md) · [Về index tổng](../index.md)
