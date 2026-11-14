# 2026-11-14 — `cron_health_check.py` resolve log tương đối theo CWD của chính nó ⇒ 10 job báo LOG_MISSING giả VÀ không bao giờ được quét lỗi

**Phát hiện:** weekly ops audit 14/11 (job `Mike_20261114_075225`). 12 dòng LOG_MISSING; 10/12 log THẬT tồn tại và tươi
(`intraday_price_watch`, `nav_loss_brake_monitor` ×2, `livermore_trigger`, `commodity_sue_decomp_forward_tracker` ×2,
`dri_buy_gate_watch`, `dcf_rstar_refresh` ×2, `opening_window_l2_poll_$(date)`).

**Nguyên nhân thật (đọc code):** dòng crontab dạng `cd /home/trido/thanhdt/WorkingClaude && … >> mike/logs/x.log 2>&1`
— shell resolve `mike/logs/x.log` theo thư mục của `cd`; `resolve_log_paths()` gọi `os.path.exists("mike/logs/x.log")`
theo CWD của bộ kiểm ⇒ không thấy ⇒ LOG_MISSING. Hệ quả nặng hơn báo giả: các job đó **rơi khỏi `scan_errors()`** — một crash
thật trong `nav_loss_brake_monitor` (phanh lỗ NAV) sẽ không bao giờ hiện ở ERRORS_FOUND.

**Sửa:** `main()` ghép đường tương đối với thư mục của `cd …&&` đầu lệnh (không có `cd` ⇒ `$HOME`, đúng ngữ nghĩa cron).

**Verify (chạy thật):** trước 33 cần chú ý / LOG_MISSING 12; sau 23 / LOG_MISSING 1 (`refresh_deposit_rate_vn.log` — job
tháng ngày 3 chạy đúng 03/11, log thật nằm `data/refresh_deposit_rate_vn_2026-11.log`; file cron-log rỗng không tồn tại — benign).
10 job mới được quét: 0 dòng lỗi (ERRORS_FOUND giữ 11). `dri_buy_gate_watch` nay vào STALE 1,2d — giả do bucket `frequent`
không biết T7/CN (cùng lớp với `bot_heartbeat`/`egg_transfer_alert` đã có sẵn), không phải bug mới.
