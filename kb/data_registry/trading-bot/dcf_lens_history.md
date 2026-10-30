---
kind: script-output
status: CANONICAL
source: data/dcf_lens_history.csv
group: trading-bot
note: fresh (mtime 2026-08-28) — append-only log, KHÔNG phải nguồn cron; đăng ký 2026-08-28 sau khi phát hiện chưa có entry (job Taylor_20260828_081256)
writer: trading_bot/strategies.py::log_dcf_history() — gọi từ đường REPORT (send_plan_report / eod_trading_report / dc_book_waterfall_paper), KHÔNG từ V23Strategy
---

# data/dcf_lens_history.csv

**Status: CANONICAL (append-only log, ghi mỗi lần report tính DCF)**

## Là gì
Tích luỹ `fair_value_ps` DCF dự báo + giá thị trường tại thời điểm tính, mỗi lần MỘT REPORT chạy
`dcf_check` (user directive 2026-07-15). Mục đích: sau này đối chiếu với giá thật T+1M/3M/6M để
đánh giá lăng kính DCF có hữu ích không. Thuần là bước GHI DỮ LIỆU — không phân tích/quyết định.

## Ai ghi / cadence
`trading_bot/strategies.py::log_dcf_history()` — append mỗi lần `send_plan_report` /
`eod_trading_report` / `dc_book_waterfall_paper` tính `dcf_check` cho 1 ticker, **KHÔNG** phải cron
riêng và **KHÔNG** phải `dcf_refresh_gate.py` (script đó chỉ gate discount-rate hàng tháng ngày 11,
ghi vào `data/dcf_refresh_state.json`/`data/dcf_refresh_gate.log` — hai file này KHÁC file, đừng
nhầm 2 luồng). Fail-safe: mọi lỗi ghi bị nuốt im lặng (log warning), report không hỏng vì dòng này.

## Bẫy

- **CUTOVER KHUNG DCF 2026-10-30 12:48 ICT (`logged_at` < mốc này = `legacy`; ≥ mốc = `domestic_v2`).** CSV KHÔNG có cột frame ⇒ chuỗi lịch sử TRỘN hai khung: trước mốc r = lãi huy động (tới ~13,9%) + ERP 6,5%, g_T cap = lãi huy động; sau mốc r = 12,25% hằng, g_T cap 5,5%. FV trung vị đổi ~−1,4%, thứ hạng gần như không đổi (tương quan ≥0,9999) nhưng mức MoS tuyệt đối không so thẳng được qua mốc. Khi phân tích chuỗi, cắt tại mốc hoặc tính lại bằng `DCF_RATE_FRAME=legacy`.
- KHÔNG có consumer đọc lại file này trong pipeline sản xuất — hiện tại thuần là log tích luỹ chờ
  phân tích sau; đừng coi việc file không được ai `read_csv` là dấu hiệu file chết.
- Không refresh/tái tạo được — mỗi dòng gắn với 1 lần tính DCF thật tại đúng thời điểm đó
  (`logged_at`, `as_of`); xoá/ghi đè sẽ mất lịch sử không phục hồi được.
