# fill_timing_monitor — README (job Taylor_20261119_055805)
Monitor cơ học fill-vs-open cho HYBRID (user duyệt 2026-11-19). READ-ONLY production. Không cài cron (Mike cài).

**Chạy:** `. wc_env.sh; $DNA_PYEXE mike/bin/fill_timing_monitor.py` (cờ test: `--today`, `--open-csv`, `--state`, `--notify-cmd`, `--force-weekly`).
**Selfcheck:** `env -u TZ $DNA_PYEXE mike/bin/fill_timing_monitor_selfcheck.py` (28 kiểm; chạy cả TZ=Asia/Tokyo, America/New_York).
**Luật (PREREG.md, md5 trong PREREG.md5):** đủ N mỗi chiều = ≥30 mã-ngày VÀ ≥8 tuần ISO ⇒ CI95 bootstrap khối tuần; chưa đủ ⇒ chỉ "N=x/30, y/8 tuần", không báo mean. BUY HYB_IN_BLOCK đủ N & mean > +22 bps ⇒ cảnh báo "đề xuất rollback — user quyết" (không tự đổi cờ). SELL chỉ mô tả.
**Nguồn ngày bật HYBRID:** 2026-08-26 = ngày commit 9be375a44 (flip 2 gate → False); selfcheck đối chiếu `git show`. Phân loại lệnh = luật `build.py` job 052911 (note journal `hyb:blk`).
**Đầu ra:** thứ Hai 1 dòng tiến độ → `trading_daily`; alert ngay (1 lần/tuần ISO nếu còn chạm); lỗi → "monitor không chạy được vì <lý do thật>". Idempotent theo khoá trong `state/fill_timing_monitor.json`.
**Lịch đề xuất:** 07:40 ICT T2–T6 (sau BQ sync 23:45) — dòng ĐỀ XUẤT ở `kb/cron_registry.md`.
**Đã đo (phiên này):** tái lập job 052911 — BUY HYB_IN_BLOCK 70 lệnh/22 mã-ngày/−56,1 bps; SELL 250/115/−6,1 CI [−17,9; +21,6]; chạy BQ thật hôm nay: BUY 22/30 mã-ngày, 4/8 tuần (chưa đủ N), BQ tới 2026-11-18.
**Giới hạn:** open = ATO không khớp được thật; không có phí/impact; ghi state sau khi post nên kill đúng giữa 2 bước có thể post trùng 1 lần (rất hẹp); lệnh ATC/không-journal không tính (không có nhãn HYB).
