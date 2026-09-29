---
kind: script-output
status: CANONICAL
source: data/margin_cycle_detector.csv
group: rating-8l
note: OUTPUT tự sinh, KHÔNG phải nguồn dữ liệu ngoài
writer: margin_cycle_detector.py (dòng 94)
---

# data/margin_cycle_detector.csv

**Status: CANONICAL (self-generated output, not an external input)**

## Là gì
Nhãn GPM-cycle cho doanh nghiệp CONVERTER (input = commodity, có pricing power) — GPM percentile
vs lịch sử chính nó: percentile THẤP = margin bị ép (input đang đỉnh) → có thể mean-revert lên;
percentile CAO = margin đang giãn (input đang đáy) → rủi ro co lại. Output của
`margin_cycle_detector.py`.

## Ai ghi / cadence
`margin_cycle_detector.py`, ad-hoc theo pipeline 8L (không có cron riêng — kiểm
`bin/pt_8l_daily.sh`/`trace_8l_deps.py` nếu cần xác nhận cadence).

## Ai đọc
`rank_8l.py`, `unified_screener.py`, `package_8l_full.py` (đóng gói release).

## Bẫy
Đây là gate PRICING POWER qua ROE xuyên chu kỳ — không dùng cho converter không có moat (chỉ
mãi mãi biên thấp, không có "mean-revert lên" thật). Đọc docstring `margin_cycle_detector.py`
trước khi diễn giải percentile.
