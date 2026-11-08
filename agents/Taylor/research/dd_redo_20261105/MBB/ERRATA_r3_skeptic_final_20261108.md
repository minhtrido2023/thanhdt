# Errata r3 — MBB (fundamental-skeptic lần cuối 08/11/2026: CONFIRMED)
Không đổi tâm/P10/P90/nhãn. Các file có hash trong LOCK_r3 KHÔNG bị sửa; lỗi văn bản ghi ở đây.

- SUMMARY_5F.json: headline_centre_report_of_record 23.804 → 21.069 (đã sửa); các field center/price_date/price_vs_center khác trong file là số r2 (price_date 04/11, 'REPORT_r2/SUMMARY.json NOT modified').
- SUMMARY.json (không sửa vì hash trong LOCK): key change_reason (:45) còn văn bản r1; center_vs_p50_note (:252) còn 23.804/22.765/24.068; ri_at_ke_145_15 (:261-263) 20.223/18.933 là của r2 — theo r3, Ke 14,5% cho đúng 19.250 (lệch +973). Do `S=dict(old)` ở mbb_r3.py:192 chép key r2. KHÔNG dùng các key này.
- ADDENDUM_5F.md:5,72 gọi 23.804 là 'Hiện hành'/'chờ duyệt' — đọc theo ghi chú đồng bộ ở đầu file.
- Độ nhạy 3c chặt 17.677 còn đo trên base r2 (REPORT_r3.md:60); muốn dùng làm độ nhạy rủi ro phải chạy lại trên base r3 (sửa số, chưa làm).
- LOCK không gồm ADDENDUM_5F.md (nguồn xếp hạng moat NARROW của đính chính #1).
