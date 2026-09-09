# Mike — working-memory archive (append-only; not auto-loaded)
> Cold storage of closed/old entries moved out of kb/memory/Mike.md by archive_memory.py. Nothing here was deleted from history.

## Archived 2026-08-12 (keep=12 days=0 require_done=False)
- [2026-08-11T21:37:53Z] 2026-08-11 23:xx: User chốt Option 1 cho broker-statement leg3 (đối soát khớp lệnh DNSE trong eod_trading_report.sh) — CHẤP NHẬN đã live (đã vô tình auto-commit qua fleet-backup, quant-skeptic CONFIRMED cao), KHÔNG thêm flag chặn. Điều kiện: 'cần kiểm tra lại mới dùng' — PHẢI tự verify output leg3 lần chạy live ĐẦU TIÊN (cron 19:10 ICT 2026-08-12) trước khi tin dùng cho các báo cáo sau. Việc cần làm 08-12 tối: đọc report EOD sau 19:10 ICT, xác nhận leg3 in đúng số khớp thật (so tay với dnse_raw positions), không có escalation giả.

## Archived 2026-09-09 (keep=12 days=0 require_done=False)
- [2026-09-08T17:48:50Z] P2-③ BQ cache drift XONG 09-09: root cause = chunked delta khong bao gio tai lai nam cu (sync_bq_cache.py:464), upstream ghi de partition cu => drift 909 dong ticker_prune => co AND toan cuc tat CA cache cho moi dispatch. Fix _drifted_years() commit 3ff20579, verified OK 14/14 bang + preflight PASS. Con lai P2: (2) MBB journal 1565 vs 1675 chua dieu tra; (4)(5) nhieu log CLOUD_SDK + vnstock chua dap.
