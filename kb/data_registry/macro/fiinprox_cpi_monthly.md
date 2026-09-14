---
kind: derived-file
status: DERIVED — headline CPI khớp NSO thật 13/13 tháng (diff 0,00); lõi khớp 13/13; vàng/USD UNVERIFIED
source: data/fiinprox_cpi_monthly_20260914.csv
group: macro
writer: Mike (thủ công qua MCP tool call, KHÔNG có script/cron)
upstream: FiinXMCP `get_economy(metrics=["cpi"], cpi_scope="inflation", data_type="YoY")` — FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_cpi_monthly` — CPI YoY tháng 2008-01→2026-08 (FiinPro-X trial)

224 dòng. Cột: `month, cpi_yoy_pct` (headline) · `core_yoy_pct` (lạm phát cơ bản, từ 2015-04) ·
`gold_idx_yoy_pct` · `usd_idx_yoy_pct` (chỉ số giá vàng / đô la Mỹ của GSO — KHÔNG phải giá SJC
hay tỷ giá). Harvest 2 lệnh (2008-2016, 2017-2026), filter server-side 4 `type_name`.

## Đối chiếu với `cpi_vn.py` (2026-09-14)

| Tầng cpi_vn.py | n | MAE | max lệch | tháng lệch >1pp |
|---|---|---|---|---|
| T1 NSO thật (2025-06→2026-06) | 13 | 0,00 | 0,00 | 0 |
| T2 nội suy tuyến tính (2011-01→2025-05) | 173 | 0,49 | **2,51** | 30 |
| T3 backfill CEIC (2007→2010, phần chồng 2008+) | 36 | 0,31 | **3,01** | 5 |

- 36 **anchor** của T2 khớp FiinPro ≤0,16pp ⇒ anchor đúng; sai số nằm ở ĐOẠN NỘI SUY giữa anchor.
  Tệ nhất 2019-09/10 (proxy 4,5-4,7 vs thật 2,0-2,2) và 2011-02/03, 2012-02/03/08.
  `cpi_yoy_chg3` (hướng 3 tháng) cùng dấu chỉ **77,5%** số tháng T2.
- T3 sai ở 2009-09/10 (backfill 0,68 / −0,02 vs thật 2,42 / 2,99) và 2010-09→11 (lệch 1,3-2,3pp).
  ⇒ "đáy base-effect −0,02% Oct-2009" trong docstring `cpi_vn.py` là SAI; đáy thật 1,97% (2009-08).

## Bẫy
1. **`NSO_CPI_YOY_AVG_REAL` trong `cpi_vn.py` bị gắn nhãn sai**: comment nói "bình quân/YTD",
   nhưng khớp **13/13** với `core_yoy_pct` (lạm phát cơ bản). Không ai import biến này (grep
   2026-09-14) ⇒ không ảnh hưởng production, chỉ đừng trích nó là CPI bình quân.
2. `core_yoy_pct` 2013-12 FiinPro trả `0.0` trơ trọi giữa chuỗi null — đã ghi trống.
3. 2015-09/10 headline = `0` là số thật (giảm phát sát 0), không phải null.
4. Không có cột MoM/nhóm hàng (11 nhóm có sẵn — chưa lấy).

## Nâng status / dùng
- Headline + lõi: DERIVED. Thay T2/T3 của `cpi_vn.py` bằng file này = đổi consumer
  (`macro_confidence_regime.py`, `dcf_valuation.py`, `gdp_growth_vn.py`, golive_recommend_v23…) ⇒
  quyết định riêng, qua quant-skeptic. KHÔNG tự wire.

↩ [Về nhóm macro](index.md) · [Về index tổng](../index.md)
