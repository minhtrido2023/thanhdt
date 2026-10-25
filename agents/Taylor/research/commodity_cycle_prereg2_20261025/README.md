# PREREG-2 + paper forward (job Taylor_20261025_062825)
- `PREREG-2.md` — thiết kế đóng băng (md5 2962d12f…, commit c71744d03). `commodity_map.csv` — bản đồ đóng băng (md5 cf4bef53…).
- Code: `bin/commodity_cycle_forward_tracker.py` (nhật ký, không in thống kê) · `bin/commodity_cycle_forward_review.py`
  (verdict, cổng ngày 2028-01-31) · `bin/commodity_cycle_forward_tracker_selfcheck.py` (40 assertion + 8 mutant).
- `ledger_initial/` — kết quả chạy khởi tạo 2026-10-25 vào thư mục này (KHÔNG phải data/ production): 3 sự kiện
  PRE_FREEZE_BACKFILL (crude 2026-03, DAP 2026-05, sugar 2026-08), counts=False, 0 sự kiện FORWARD. Không dùng làm bằng chứng.
- Cài đặt (chờ Mike/user): cron hằng ngày ngày 11–25 mỗi tháng `$DNA_PYEXE mike/bin/commodity_cycle_forward_tracker.py`
  (mặc định ghi `data/commodity_cycle_forward_*.csv`); WB cache phải được làm tươi trước đó (cron kéo ngày 5 + 10).
