# Ghi chú đồng bộ cho `ADDENDUM_5F.md` — **ĐÃ THAY bởi sửa tại chỗ r3c (09/11/2026, job Taylor_20261108_180625)**

Bản r3b của ghi chú này nói `ADDENDUM_5F.md` / `SUMMARY_5F.json` "không sửa vì md5 nằm trong LOCK của DDV/PVT/NT2" (bản JSON ghi DDV/PVP/PVT/NT2 — hai file còn lệch nhau). **Lý do đó SAI**: md5 hiện tại của `ADDENDUM_5F.md` (83131c3e…) và `SUMMARY_5F.json` (af090936…) không nằm trong LOCK nào (`grep -rl <md5>` mọi `LOCK*` dưới `dd_redo_20261105/` trả rỗng, kiểm 09/11). Vì vậy r3c đã **sửa tại chỗ** `ADDENDUM_5F.md:1` và `SUMMARY_5F.json:32` (+ thêm `headline_centre_current`). md5 trước khi sửa ghi ở `calc_r3c/LOCK_r3c_prerun.txt`.

Hiện hành: **r3c** (`REPORT_r3c.md`, `SUMMARY.json`) — tâm 25.165 (cỡ 5 tỷ) / 26.148 (cỡ 40 tr), TRONG ở cả hai cỡ. r3b 24.529 đã bị thay (lỗi khung KTPL cổ phần).
