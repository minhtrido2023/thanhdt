---
kind: incident
date: 2026-07-08
topic: zalopay-invalid-otp-race-gmail
title: >-
  2026-07-08 — ZaloPay INVALID_OTP lúc 09:05: race Gmail-OTP giữa 2 cron cùng giây, chung login DNSE — bot tự hồi phục qua heartbeat autoheal, nhưng lộ gap "bot-fail không ai tự chẩn đoán"
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-08 — ZaloPay INVALID_OTP lúc 09:05: race Gmail-OTP giữa 2 cron cùng giây, chung login DNSE — bot tự hồi phục qua heartbeat autoheal, nhưng lộ gap "bot-fail không ai tự chẩn đoán"

**Hiện tượng:** cron 09:05:02 ICT khởi động run_bot cho CẢ SpaceX và ZaloPay cùng giây
(crontab dòng 54-55, cùng `5 2 * * 1-5`). SpaceX lấy trading-token OK; ZaloPay chết sau
11 giây với `DNSEError HTTP 500 INVALID_OTP` ("The SMS OTP is invalid; is expired; have
not been requested or have been used") → bus event Mafee/error `bot-fail` 02:05:13Z.
2 lệnh của ZaloPay (SELL TLG 200 + BUY VHM 100) chưa được đặt tại thời điểm đó.

**Tự hồi phục (xác nhận cơ chế thật):** `bot_heartbeat.sh` (cron */5) phát hiện bot chết
→ `_restart_bot()` spawn lại `bot_execute.py --auto-otp` lúc 09:10:01 (log
`run_bot_ZaloPay_autoheal_20260708_091001.log`). Lần này in "[ZaloPay] trading-token còn
hạn — bỏ qua OTP" — vì SpaceX và ZaloPay **chung 1 login DNSE** (cả 2 `credentials_file:
null` → default `secrets/dnse_credentials.json`) nên **chung token cache**
`data/dnse_trading_token.json`: token SpaceX tạo lúc 09:05 dùng được luôn cho ZaloPay.
Cả 2 lệnh FILL đủ, không lệnh kẹt, không cần user can thiệp.

**Root cause (từ log, không suy đoán):** cả 2 process cùng hết token → cùng
`send_email_otp()` gần như đồng thời → cùng poll 1 hộp Gmail với **cùng cutoff**
(`sent_after=1783476243` identical trong 2 log — default `time.time()-60` tính cùng
giây) → cả 2 extract cùng 1 mã ("after 2 poll(s)", age 10-11s, cơ chế dedup
`gmail_otp_last_id.txt` vô hiệu vì cả 2 đọc last_id TRƯỚC khi email nào tới). OTP là
customer-level (chung login): bên submit trước (SpaceX) thắng; bên sau (ZaloPay) dính
"have been used". Chữ "SMS OTP" trong message chỉ là boilerplate server DNSE — kênh thật
vẫn là email OTP (endpoint `/registration/send-email-otp`), không có override kênh theo
account.

**Fix (commit cùng ngày):**
1. `bot_execute.py` — `_otp_flow_lock()`: flock LIÊN TIẾN TRÌNH (key theo credentials
   file, `data/execution_logs/otp_default.lock`) ôm trọn chu trình send→fetch→create;
   sau khi giành khoá thì `_load_token_cache()` lại — bên thua thấy token bên thắng vừa
   tạo (chung login) → bỏ qua OTP hoàn toàn. Kèm `sent_after=thời điểm ngay trước
   send_email_otp - 5s` (đúng khuyến nghị docstring `fetch_dnse_otp`) — loại hẳn email
   OTP cũ/của request khác. Fix nằm ở bot_execute.py nên che luôn đường autoheal của
   heartbeat (gọi thẳng bot_execute.py). Verify: harness 2-process — bên thua chờ khoá,
   reload cache, SKIP-OTP, đúng 1 bên xin OTP.
2. `mike/bin/run_bot.sh` — **vá gap quy trình** (lý do thật khiến user thấy "bot báo lỗi
   không ai tự sửa"): nhánh rc≠0 trước đây chỉ Discord alert + bus event, KHÔNG gọi
   `ops_autofix.sh` (khác ops_health_check.sh/sync_bq_cache_daily.sh đã wire). Giờ mọi
   lần fail tự gọi `ops_autofix.sh "run-bot-fail-<ACCOUNT>-<DATE>" "<chi tiết + tail
   log + checklist autoheal/journal>"` — dispatch --bg không block, cooldown 1h/label
   chống bão. Verify: sandbox stub — rc=7 gọi autofix đúng label/details + giữ nguyên
   exit code; rc=0 không gọi.

**Lưu ý thêm (cosmetic, không sửa):** log `run_bot_*.log` bị NHÂN ĐÔI mọi dòng vì cron
redirect `>> log` trùng đúng file mà run_bot.sh đã `tee -a` vào (crontab = ranh giới
cấm sửa). Đọc log đừng tưởng 2 process.
