---
kind: script-output
status: CANONICAL
source: data/rank_8l.csv, data/rank_8l.md
group: rating-8l
note: OUTPUT tự sinh, KHÔNG phải nguồn dữ liệu ngoài; live snapshot HÔM NAY, không phải lịch sử PIT
writer: rank_8l.py (dòng 202)
---

# data/rank_8l.csv (+ `rank_8l.md`)

**Status: CANONICAL (self-generated output, not an external input)**

## Là gì
Xếp hạng top-N theo composite 8L route-aware (mỗi công ty chấm theo đúng lens của nó rồi quy
về thang 0-100 chung) — output của `rank_8l.py`. Input của chính nó:
`data/unified_screener.csv` + `data/engine_class.csv` (xem entry riêng).

## Ai ghi / cadence
`rank_8l.py`. Cadence: theo pipeline 8L (`pt_8l_daily.sh` / `pt_8l_quarterly.py`) — không cron
riêng biệt, kiểm `trace_8l_deps.py` nếu cần xác nhận thứ tự chạy trong ngày.

## Ai đọc
`bot_8l_commands.py`, `telegram_8l_bot.py`, `dna_report.py`, `rank_8l_daily_alert.py`,
`pt_8l_quarterly.py`, `vn30_8l.py` — nhiều consumer downstream, coi như hub của pipeline hiển thị.

## Bẫy
Live snapshot HÔM NAY — không phải lịch sử PIT, giống `rating_8l.csv` (§ `rating_8l_csv.md`).
Backtest/PIT phải dùng `fa_ratings_8l` as-of, không join file này vào quá khứ.
