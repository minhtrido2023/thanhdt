---
kind: incident
date: 2026-08-01
topic: full-crontab-audit-cron-health-check
title: >-
  2026-08-01: audit toàn bộ 64 dòng crontab (user mandate sau chuỗi sự cố quoting) — 1 bug thật
  mới + 9 log-observability gap + công cụ giám sát thường trực mới (cron_health_check.py)
status: fixed
category: dispatch-orchestration
origin: >-
  thiếu cơ chế mechanical kiểm tra "job đã lên lịch có thật sự chạy đúng không" cho TOÀN BỘ
  crontab — chỉ phát hiện từng job một khi tình cờ đọc log tay (đúng bài học 2 sự cố cùng ngày)
recorder: Mike, theo yêu cầu trực tiếp của user
---

# 2026-08-01: audit toàn bộ crontab — 1 bug thật + 9 gap observability + công cụ mới

**Yêu cầu user (nguyên văn tinh thần):** sau 2 sự cố quoting phát hiện cùng ngày (daily_retro.sh
2 đêm, kb_nightly.sh 2 tuần), kiểm tra lại HẾT mọi cron task xem có đang âm thầm chạy/âm thầm lỗi
không, và dựng 1 nơi để review liên tục — không chờ tình cờ phát hiện nữa.

## Công cụ mới: `bin/cron_health_check.py`

Parse `crontab -l` thật (không phải tài liệu), với mỗi job: phân loại nhịp (frequent/daily/
weekly/monthly) từ 5 trường lịch, tìm log target (`>> ... 2>&1`, kể cả path có `$(date ...)`
động), rồi kiểm mtime (có STALE so ngưỡng theo nhịp không) + quét lỗi trong tail (có
timestamp-aware filter — bỏ qua lỗi cũ >10 ngày để tránh nhiễu từ sự cố lịch sử đã tự phục hồi).
4 trạng thái: `OK` / `ERRORS_FOUND` / `STALE` / `LOG_MISSING` / `NO_LOG_REDIRECT`.

**2 bug trong chính công cụ audit, tự bắt trước khi dùng thật** (đúng tinh thần "verify bằng
chạy thử, không chỉ đọc lại" — bài học ngay từ 2 sự cố sáng nay): (1) regex tách log-path ban đầu
không xử lý được `$(date +\%Y-\%m-\%d)` chứa khoảng trắng bên trong — khiến TOÀN BỘ 4 dòng
`run_bot.sh` (chạm tiền thật) bị báo nhầm `NO_LOG_REDIRECT`; (2) quét lỗi ban đầu đọc "200KB cuối
file" không phân biệt theo NGÀY, khiến 1 lỗi BQ timeout đơn lẻ từ 15 ngày trước (đã tự retry
thành công ngay sau đó) hiện lên như đang "sống" — thêm bộ lọc theo mốc ngày gần nhất tìm thấy
trong log để loại nhiễu lịch sử.

## Bug thật tìm thấy: `kb_nightly.sh:584` gọi sai đường dẫn backup

`"$ROOT/bin/backup.sh"` — file **CHƯA TỪNG TỒN TẠI** trong repo kể từ khi dòng này được thêm
2026-06-30 (commit `044c63ca9`, hơn 1 tháng trước). Lỗi `No such file or directory` xuất hiện
ĐỀU ĐẶN mỗi đêm trong log (`grep backup.sh logs/kb_nightly.log` → 10 lần trong lịch sử log hiện
có), luôn bị `|| true` nuốt im lặng. Đích đúng: script backup top-level workspace
`/home/trido/thanhdt/backup.sh` (nhận message argument, dùng chung bởi `fleet_backup.sh` cron
00:00 ICT) — kb_nightly's intent là backup+push NGAY sau khi tự commit KB trim, thay vì chờ tới
22h sau (cron 00:00 kế tiếp). Fix: đổi thành `"$ROOT/../../backup.sh"` (2 cấp lên từ `mike/`, đã
tự tính nhầm 1 cấp lần đầu — `$ROOT/../backup.sh` trỏ vào `WorkingClaude/backup.sh` không tồn
tại — sửa lại `../../` và verify bằng cách CHẠY THẬT: `history sync CLEAN`, secret gate qua,
"Nothing changed — already up to date" (đúng vì working tree sạch lúc test) — RC=0 hoàn chỉnh.

## 9 script thiếu log-redirect (`NO_LOG_REDIRECT`) — đã thêm

`papertrade_daily.sh`, `pt_8l_daily.sh`, `telegram_run_daily.sh`, `daily_refresh_v34b_linux.sh`,
`auto_update_commodity_wb.sh` (×2 ngày 5+10), `rubber_weekly.sh`, `update_shares_live.sh`,
`fetch_new_listings_daily.sh` — không có `>> logfile 2>&1` trong crontab, output rơi vào cron
mail mặc định. Xác nhận thật: postfix CÓ chạy nhưng **không có mailbox local** (`/var/mail/trido`
không tồn tại, `mailq` rỗng) → output coi như MẤT, không ai đọc được. Hầu hết các script này tự
quản log riêng khá tốt (`data/refresh_v34b_linux_<date>.log` xác nhận đủ 07-01→07-31 không thiếu
ngày nào) nên rủi ro thực tế thấp hơn `kb_nightly.sh`/`daily_retro.sh` — nhưng vẫn thêm redirect
làm lớp phòng thủ THỨ HAI bắt crash SỚM (trước khi script tự log kịp khởi tạo), đúng lớp lỗi vừa
xảy ra hôm nay ở 2 script khác. **Không đổi lịch/logic**, chỉ thêm quan sát. Không đụng
`discord_bot/start.sh` (hệ thống khác, ngoài sở hữu fleet Mike).

## Không phải bug — verify rồi loại (tránh false-positive tương lai)

- `sync_bq_cache_daily.sh`, `eod_trading_report.sh` (Traceback) — lỗi timeout BQ đơn lẻ từ
  2026-07-16, đã tự retry thành công ngay sau đó; lần chạy MỚI NHẤT (07-31) sạch 100%
  ("Cache verified OK", "RESULT: PASS").
- `newdeals_daily_report.py` (Traceback) — nằm ở DÒNG ĐẦU TIÊN của file log (khi mới dựng, không
  có mốc ngày liền kề để lọc), mọi lần chạy 07-26→07-30 đều "sent OK". Checker giữ lại vì
  heuristic "không có context ngày → giữ, không đoán" — false positive đã biết, chấp nhận được.
- `resume_pending.py` STALE (3.6 ngày không đổi log) — script KHÔNG in gì khi hàng đợi resume
  rỗng (trường hợp bình thường), nên mtime không đổi ≠ không chạy. Test chạy tay: RC=0, sạch.
- 4× `LOG_MISSING` (deposit_rate ngày 3, dcf_refresh_gate ngày 11, bq_monthly_pin ngày 1,
  fleet_housekeeping Chủ nhật) — cả 4 cơ chế đều MỚI CÀI (07-13→07-30), lịch định kỳ (tháng/tuần)
  của chúng CHƯA tới lần đến hạn đầu tiên kể từ khi cài (bq_monthly_pin: hôm nay 22:00 ICT tối
  nay; fleet_housekeeping: mai Chủ nhật; 2 cái tháng: 08-03/08-11). Không phải lỗi — chỉ chưa đủ
  thời gian để có bằng chứng lần chạy đầu.

## Chưa giải quyết hẳn — cần theo dõi thêm (không phải lỗi xác nhận, không phải sạch xác nhận)

`bot_heartbeat.sh` STALE (log không đổi ~3 ngày) — code cho thấy khi KHÔNG có event journal mới,
`_notify()` gửi thẳng Discord mà KHÔNG echo ra stdout (nên không ghi vào log local) — im lặng có
thể là ĐÚNG THIẾT KẾ (chống spam) nếu thật sự 07-30/07-31 không có event mới nào, hoặc có thể là
dấu hiệu thật (nhưng chưa đủ bằng chứng để kết luận theo 1 trong 2 hướng trong phạm vi audit hôm
nay). Đề xuất chưa làm: thêm 1 dòng touch/echo tối thiểu mỗi lần chạy (kể cả quiet heartbeat) để
tín hiệu mtime trở nên đáng tin — cần user/Winston quyết có đáng làm không (rủi ro thấp, lợi ích
observability, nhưng đụng vào script chạm tiền thật nên cẩn trọng hơn các fix khác hôm nay).

## Cơ chế thường trực mới (trả lời đúng yêu cầu "phải có nơi để review lại")

1. **`bin/cron_health_check_daily.sh`** — cron MỚI 08:25 ICT T2-T6 (sau `ops_health_check.sh`
   08:20), chạy `cron_health_check.py`, post Architecture channel khi có vấn đề / Telegram
   quiet-heartbeat khi sạch. Cố ý TÁCH KHỎI `ops_health_check.sh` (không nhét vào loop
   `for_each_live_account.sh`) vì cron_health_check là fleet-wide, nhét vào sẽ chạy lặp theo số
   account — đúng bẫy "Job board:" đã ghi nhận trước đó (coord-2026-07-22).
2. **`weekly_ops_audit.sh` item 1** (Sat 03:30 ICT) — cập nhật để dùng `cron_health_check.py` làm
   điểm khởi đầu thay vì grep tay từ đầu, đọc đủ cả 4 nhóm trạng thái.
3. `kb/cron_registry.md` bảng chính + `cron_registry/CHANGELOG.md` — đăng ký đầy đủ, đúng quy tắc
   §11.

**Giới hạn đã biết của `cron_health_check.py`** (ghi nhận minh bạch, không giấu): mtime-based
staleness là tín hiệu YẾU cho bất kỳ script nào chỉ log-khi-có-việc (resume_pending.py,
bot_heartbeat.sh khi quiet) — cần đọc kèm phán đoán con người/LLM (đã làm ở đây), không tự động
báo "hỏng" chỉ từ 1 con số tuổi file. Đây KHÔNG phải gate chặn gì — thuần phát hiện + báo cáo.
