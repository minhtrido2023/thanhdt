# ORB futures sleeve — stop thảm hoạ + probe DNSE (job Taylor_20261116_162132)

- `fetch_tail.py` → `vn30f1m_tail_20260920_20261116.csv` (VCI 1m, cùng nguồn orb_pt.py) nối tape tới 16/11.
- `stop_study.py` → `stop_study_result.json`: MAE + tỉ lệ chạm 6 mức stop (N trial=6), chọn 2,5% theo tiêu chí tần suất ≤3%.
- `probe_dnse_derivative_{1,2,3}.py`: probe CHỈ ĐỌC DNSE phái sinh (không place/cancel). Output 1 lưu `_out.json` (bỏ PII).
- `xfeed_dnse_vs_vci.py` + `dnse_vn30f1m_1m_30d.csv`: DNSE vs VCI 30 phiên — sig 30/30.
Kết luận + số: `kb/projects/orb-futures-sleeve-20261116.md`. Chạy từ thư mục này (đường dẫn tương đối).
