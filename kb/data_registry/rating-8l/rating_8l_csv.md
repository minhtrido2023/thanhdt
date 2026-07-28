---
kind: script-output
status: CANONICAL
source: data/rating_8l.csv (+ rating_8l_top30/_buynow/_screener.csv)
group: rating-8l
note: live snapshot HÔM NAY, KHÔNG phải lịch sử PIT
writer: rating_8l.py, pt_8l_daily.sh step [1], 17:45 ICT hàng ngày
---

# data/rating_8l.csv (+ `rating_8l_top30/_buynow/_screener.csv`)

**Status: CANONICAL (live snapshot)**

## Là gì
Rating 8L HIỆN TẠI (2-axis quality×value, screener).

## Ai ghi / cadence
`rating_8l.py`, `pt_8l_daily.sh` step [1], 17:45 ICT hàng ngày.

## Bẫy
Là snapshot hôm nay, KHÔNG phải lịch sử PIT — backtest phải dùng `fa_ratings_8l` as-of, không được
join CSV này vào quá khứ.
