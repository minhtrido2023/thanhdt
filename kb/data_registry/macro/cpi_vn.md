---
kind: config
status: CANONICAL-PROXY
source: cpi_vn.py (NSO_CPI_YOY_REAL + CPI_ANCHORS)
group: macro
note: 2 tầng — Tier 1 NSO thật (rolling 13 tháng) đè Tier 2 proxy nội suy; CHƯA có cron
writer: fetch tay 1 lần (job Taylor_20260706_105930, 2026-07-06)
---

# `cpi_vn.py` (`NSO_CPI_YOY_REAL` + `CPI_ANCHORS`)

**Status: CANONICAL-PROXY (2 tầng)**

## Là gì
CPI YoY Việt Nam, monthly — **Tier 1 THẬT** (NSO chart-embed slug `cpi`, 2025-06→2026-06, cửa sổ
rolling 13 tháng) đè lên **Tier 2 PROXY** nội suy tuyến tính (2011→2025-05).

## Ai ghi / cadence
Fetch tay **1 lần** (job `Taylor_20260706_105930`, 2026-07-06, parse trực tiếp JSON Highcharts embed
của NSO) — **CHƯA có cron/refresh tự động**, không phải chuỗi tự tươi.

## Bẫy
**KHÔNG PHẢI `Inflation_7` trong `tav2_bq.ticker`** — đó là HẰNG SỐ 7%/năm chiết khấu trading value,
không liên quan CPI thật (xem CLAUDE.md). 3 gotcha: (a) cửa sổ NSO rolling CHỈ 13 tháng — không
refetch định kỳ, Tier 1 tự "trôi ra" theo thời gian mà KHÔNG báo lỗi (đã verify thực nghiệm
2026-07-13: gọi `cpi_monthly_df(end=...)` cho tháng sau 2026-06 vẫn trả SỐ — không NaN — do nội
suy/ngoại suy Tier-2 âm thầm, chỉ phân biệt được qua cột `is_real_nso=False`, dễ tưởng nhầm vẫn là dữ
liệu thật); (b) hôm nay 2026-07-13 đã qua tháng NSO gần nhất công bố (06/2026) — cần refetch để lấy in
tháng 07 khi NSO đăng; (c) consumer hiện tại: `macro_confidence_regime.py` (`merge_cpi`);
**`dcf_valuation.py` + `dcf_backtest.py`** (DCF 2-stage FCFE — CPI làm inflation input cho terminal
growth rate, job Taylor_20260714_051643, research tool, NOT wired production) — KHÔNG phải input Pillar
A/A′/B của DT5G macro gate (Taylor cần chuỗi này CHO Pillar A′ "lãi suất huy động thực" — đã báo tồn
tại, đỡ phải tự tìm/tự dựng lại). Routine tháng có thể gộp chung đề xuất với `deposit_rate_vn.py` (xem
file proposal trên).
