---
kind: script-output
status: CANONICAL
source: data/rating_8l.csv, data/rating_8l_top30.csv, data/rating_8l_buynow.csv, data/rating_8l_screener.csv, data/rating_8l_NEW.csv
group: rating-8l
note: live snapshot HÔM NAY, KHÔNG phải lịch sử PIT
writer: rating_8l.py, pt_8l_daily.sh step [1], 17:45 ICT hàng ngày
---

# data/rating_8l.csv (+ `rating_8l_top30.csv` / `rating_8l_buynow.csv` / `rating_8l_screener.csv` / `rating_8l_NEW.csv`)

**Status: CANONICAL (live snapshot)**

## Là gì
Rating 8L HIỆN TẠI (2-axis quality×value, screener). Tất cả các file dưới đây là OUTPUT tự
sinh của `rating_8l.py` (không phải input cần đăng ký nguồn ngoài) — liệt kê tường minh để
`data_registry_scan_unregistered.py` (Section E) nhận diện đúng, tránh WARN giả (2026-08-28,
job Taylor_20260828_084735 — 3 file dưới trước đó chỉ được nhắc bằng viết tắt
`rating_8l_top30/_buynow/_screener.csv` trong `source:`, không khớp chuỗi chính xác nên bị
báo WARN dù đã "có tài liệu"):
- `rating_8l_top30.csv` — top-30 theo rating+value (dòng 669).
- `rating_8l_buynow.csv` — danh sách mua-ngay đã lọc (dòng 700).
- `rating_8l_screener.csv` — 2-axis quality×value mặc định (dòng 950), đọc lại bởi
  `bot_8l_commands.py` và `screener_paper_diff.py`.
- `rating_8l_NEW.csv` — **fallback path CHỈ dùng khi `data/rating_8l.csv` bị khoá**
  (`PermissionError`, ví dụ đang mở bằng Excel) — nội dung giống hệt `rating_8l.csv`, không
  phải nguồn dữ liệu riêng biệt (dòng 634-639).

## Ai ghi / cadence
`rating_8l.py`, `pt_8l_daily.sh` step [1], 17:45 ICT hàng ngày.

## Bẫy
Là snapshot hôm nay, KHÔNG phải lịch sử PIT — backtest phải dùng `fa_ratings_8l` as-of, không được
join CSV này vào quá khứ.
