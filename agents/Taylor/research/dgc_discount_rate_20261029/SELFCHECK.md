# SELFCHECK — dgc_discount_rate_20261029 (job Taylor_20261029_133456)

1. **Tái lập r7 ở Ke gốc 14,9% — lệch 0 đồng ở 7/7 mốc** (assert trong `model_ke.py`, log `run_stdout.txt`):
   A DCF 21.407 / 32.925 / 41.779 · A EV 29.817 · A7 DCF cơ sở 33.072 · A7 EV 32.182 · B7 EV 37.060.
2. `model_ke.py` import nguyên r7 `model.py` (md5 `c8778aae32679c4d08f1b05186fc0d91`, KHÔNG sửa); chỉ thay `ke()` bằng monkeypatch.
   `dcf_decomp()` là bản sao logic `dcf_core` để tách thành phần — assert tổng = `dcf_core` (|lệch| < 1e-6) ở cả 4 Ke.
3. Tất định: chạy dưới `TZ=UTC` và `TZ=Pacific/Kiritimati` ⇒ md5 cả 6 out_*.csv + run_stdout.txt **trùng byte**:
   ```
   76720b8d2e7587ac562a73c3c509720d  out_dcf_decomp.csv
   85f1ab939a4ab440d6d16f275e6eee43  out_g_x_ke.csv
   1a5a1d5af1407cbf382b701741aa4380  out_ke_candidates.csv
   f04bfc1ed3a04cfd4d5080eb47af528f  out_ke_grid.csv
   fe279c7e03cadc7d59b25eee289935eb  out_market_xcheck.csv
   2e7561f8d8cdfbc418e8b6aec7f1bc71  out_rf_candidates.csv
   5ff668dffd152852c9363d9ccc8188bf  run_stdout.txt
   b3d963e3ba1ccbc90329ae538f13e661  model_ke.py
   14e8c7a620fefc2e8401d920a423d5e2  data/tpcp10y_annual.csv
   ```
   Lệnh: `TZ=<x> /home/trido/thanhdt/wc_venv/bin/python model_ke.py` (≈47 s).
4. PREREG commit `19d692087` TRƯỚC khi lấy số rf/ERP/β và trước khi chạy bất kỳ FV nào.
5. β đo bằng BQ trong phiên (5Y tuần 29/10/2021–28/10/2026, Close điều chỉnh, n=259 tuần; peer = `tav2_mike.universe_pit`
   in_universe 28/10/2026 ∩ ICB 13xx, 19 mã có ≥150 tuần — KHÔNG dùng ticker_prune).
6. Giới hạn: chuỗi TPCP 10Y theo năm phần lớn **ước lượng** (xem `data/tpcp10y_annual.csv` cột `kind`); chỉ ảnh hưởng ứng viên (b),
   KHÔNG ảnh hưởng điểm trung tâm (luật PREREG rẽ sang (c) vì chênh 3,05pp ≫ 1pp — chênh vẫn >1pp nếu (b) sai ±2pp).
7. Không có kiểm định thống kê: N năm = 10/15 quan sát tự tương quan cao ⇒ chỉ mô tả.
