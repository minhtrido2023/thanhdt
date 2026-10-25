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

## Cập nhật 2026-10-25 — `merge_cpi` mặc định `pit=True` (user duyệt A, 25/10 11:25 ICT)
`cpi_vn.merge_cpi()` trước đây gán CPI tháng M ở nhãn M-01 rồi `merge_asof` backward ⇒ phiên đầu tháng M thấy CPI của chính tháng M (GSO công bố cuối M/đầu M+1) = look-ahead. Nay mặc định dịch chuỗi +1 tháng (`pit=True`); `pit=False` tái lập số cũ. Commit WorkingClaude `2cafe5c53` + `c681cb7be` (quant-skeptic CONFIRMED, arch APPROVED, `cpi_vn_tier15_selfcheck` PASS).
- Live 2026-10-23: 4,69 → 4,69 (không đổi, nhánh max NSO). CAPIT lever đang DISABLED.
- Lịch sử 2011-01→2026-10 (3838 phiên): CPI lệch tuyệt đối TB 0,547pp, max 3,617pp; cổng CPI≥6 lật 141 phiên, chỉ 5 phiên trong vùng dd52≤−20% (2012-09: chặn→cho phép).
- ⚠️ Số nghiên cứu `macro_confidence_regime` đã pin trong `data/results_registry.md` là theo `pit=False`; chạy lại sẽ khác. Trích dẫn phải nói rõ quy ước.
- Việc dở không chặn: `NSO_CPI_YOY_REAL` stale từ 2026-06 (FiinPro 08/2026 = 4,89 vs cổng đọc 4,69 — Winston refresh); `engine_2008.py:222-230` cùng look-ahead chép tay (ticket riêng); nếu GSO công bố ngày 6 tháng M+1 thì ngày 1–5 vẫn rò rỉ (0 lật cổng 6%).
