---
kind: script-output
status: CANONICAL
source: data/engine_class.csv (+ data/cash_machine_screen.csv, cùng writer)
group: rating-8l
note: OUTPUT tự sinh, KHÔNG phải nguồn dữ liệu ngoài
writer: cash_machine_screen.py (dòng 122-123)
---

# data/engine_class.csv

**Status: CANONICAL (self-generated output, not an external input)**

## Là gì
Nhãn "cash machine" (CFO≥NP bền vững + không pha loãng vốn) cho từng ticker — output của
`cash_machine_screen.py`, cột: `ticker, engine, machine, med_ttm, asset_cagr, roic5y, dilut_3y,
cash_grow`.

## Ai ghi / cadence
`cash_machine_screen.py` ghi cả `data/engine_class.csv` và `data/cash_machine_screen.csv` (bản
đầy đủ hơn) trong cùng lượt chạy. Cadence: chạy thủ công/ad-hoc theo pipeline 8L, không có cron
riêng — kiểm `bin/pt_8l_daily.sh` nếu cần xác nhận có nằm trong daily hay không.

## Ai đọc
`rank_8l.py`, `unified_screener.py` (đọc lại làm input cho lớp lens tiếp theo).

## Bẫy
Không có — file self-contained, sinh lại mỗi lần chạy `cash_machine_screen.py`. Đừng nhầm với
`cash_machine_screen.csv` (bản đầy đủ hơn, cùng script, cùng lượt ghi).
