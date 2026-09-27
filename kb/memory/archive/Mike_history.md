# Mike — working-memory archive (append-only; not auto-loaded)
> Cold storage of closed/old entries moved out of kb/memory/Mike.md by archive_memory.py. Nothing here was deleted from history.

## Archived 2026-08-12 (keep=12 days=0 require_done=False)
- [2026-08-11T21:37:53Z] 2026-08-11 23:xx: User chốt Option 1 cho broker-statement leg3 (đối soát khớp lệnh DNSE trong eod_trading_report.sh) — CHẤP NHẬN đã live (đã vô tình auto-commit qua fleet-backup, quant-skeptic CONFIRMED cao), KHÔNG thêm flag chặn. Điều kiện: 'cần kiểm tra lại mới dùng' — PHẢI tự verify output leg3 lần chạy live ĐẦU TIÊN (cron 19:10 ICT 2026-08-12) trước khi tin dùng cho các báo cáo sau. Việc cần làm 08-12 tối: đọc report EOD sau 19:10 ICT, xác nhận leg3 in đúng số khớp thật (so tay với dnse_raw positions), không có escalation giả.

## Archived 2026-09-09 (keep=12 days=0 require_done=False)
- [2026-09-08T17:48:50Z] P2-③ BQ cache drift XONG 09-09: root cause = chunked delta khong bao gio tai lai nam cu (sync_bq_cache.py:464), upstream ghi de partition cu => drift 909 dong ticker_prune => co AND toan cuc tat CA cache cho moi dispatch. Fix _drifted_years() commit 3ff20579, verified OK 14/14 bang + preflight PASS. Con lai P2: (2) MBB journal 1565 vs 1675 chua dieu tra; (4)(5) nhieu log CLOUD_SDK + vnstock chua dap.

## Archived 2026-09-27 (keep=12 days=0 require_done=False)
- [2026-09-26T17:48:06Z] 27/09 00:5x — FiinPro 7 HƯỚNG XONG (commit kb v: kết quả ở kb/projects/fiinprox-data-usage-proposal-20260926.md §6). Không wire gì. CHỜ USER QUYẾT: (1) bus question Taylor/custom30v-index-artifact-pham-vi-re-pin — R3 28,86%→24,38% (−4,48pp) khi bỏ bước nhảy số CP khỏi chuỗi return custom30V (custom_basket.py:220/:1125), quant-skeptic CONFIRMED high — A sửa+re-pin toàn bộ / B chỉ R3 / C TRAP; Taylor khuyên A + kiểm kê park LIVE có mua 30 mã thật không; (2) đóng B.1 production_mechanism_2009_2018 + G4 amh-review; (3) câu hỏi trục breadth-tercile 08-22 trượt 4/4 trên panel H5; (4) H1/H2 wire vệ sinh (giá trị 0/thấp) — có làm không. Đã lưu h5_retail_*.csv + artifact trong git (8acb69d4, aff8940e). Trial FiinPro hết 28/09 — KHÔNG mua.
