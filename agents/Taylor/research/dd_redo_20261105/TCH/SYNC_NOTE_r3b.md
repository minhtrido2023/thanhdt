# TCH — ghi chú đồng bộ văn bản (r3b, 09/11/2026, job Taylor_20261109_003030)

Các dòng sau là số **r2**, đã lạc hậu. Không sửa trực tiếp vì cả hai file có hash trong
`calc_r3/LOCK_md5.txt` (dòng POST); sửa sẽ làm hỏng kiểm khoá r3.

| File:dòng | Đang ghi (r2) | Hiện hành (r3b) |
|---|---|---|
| `SUMMARY_5F.json:45,49` (`current.centre`, `label`) | 13.768, TRONG vùng | 15.864, **DƯỚI vùng** (P10 14.563 / P90 17.325, giá 13.500) |
| `SUMMARY_5F.json:181` (`headline_centre_report_of_record`) | 13.768 | 15.864 |
| `ADDENDUM_5F.md:76` ("Mô hình r2 giữ nguyên… TRONG vùng") | r2 giữ nguyên, TRONG | r2 đã thay bởi r3 (16.244 DƯỚI), rồi r3b (15.864 DƯỚI) |

Nguồn hiện hành: `SUMMARY.json` (round "3b") và `REPORT_r3b.md`. Bản r3 sao lưu ở `SUMMARY_r3.json`
(md5 29509b57…, trùng LOCK r3).
