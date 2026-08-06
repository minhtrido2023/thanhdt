---
kind: local-file
status: CANONICAL
source: data/rubber_alert_state.json
group: feeds
note: state chống alert lặp, không phải chuỗi giá
writer: rubber_weekly.sh, cron 18:35 ICT T2-T6
---

# data/rubber_alert_state.json

**Status: CANONICAL (state)**

## Là gì
State alert cao su tuần. Khoá hiện có (mở rộng 2026-08-06, commit `d2aeb9f`):
`last_tier` / `last_week` / `last_date` (chống bắn lặp trong cùng tuần ISO), cộng thêm
`pending_alert` = ngày quan sát của lần ALERT đầu chưa được xác nhận, và
`last_alert_confirmed` = đợt ALERT hiện tại đã thực sự gửi Telegram/DollarBill hay chưa.

## Ai ghi / cadence
`rubber_weekly.sh`, cron 18:35 ICT T2-T6. Ghi kiểu **merge + atomic** (`tmp` + `os.replace`,
coding_guidelines §5) — `_save_state()` nhận patch và trộn vào state cũ, nên `pending_alert`
sống sót qua `record_fire()` và ngược lại. Đừng đổi thành ghi đè cả file.

## Bẫy
- Là state chống alert lặp, **không phải chuỗi giá** (chuỗi giá:
  [`rubber_weekly_series.md`](rubber_weekly_series.md)).
- `pending_alert` khác `last_tier`: một ALERT đã vượt ngưỡng nhưng **chưa gửi** Telegram/Bill
  (đang chờ phiên thứ 2 xác nhận) vẫn nằm ở `pending_alert`. Đọc `last_tier` một mình sẽ không
  cho biết ai đã thực sự được báo — muốn biết điều đó phải đọc `last_alert_confirmed`.
- Xoá/reset file này = mất chuỗi xác nhận đang chạy: một ALERT đang chờ phiên 2 sẽ bắt đầu lại
  từ đầu, tức chậm thêm 1 phiên cron. Đã reset có chủ đích 1 lần ngày 2026-08-06 để rút lại
  cảnh báo sai 08-04 (xem `_note` trong chính file).
