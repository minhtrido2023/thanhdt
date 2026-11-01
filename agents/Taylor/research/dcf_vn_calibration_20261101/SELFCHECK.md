# SELFCHECK — dcf_vn_calibration_20261101 (job Taylor_20261101_155145)

1. **Engine = production, 0 VND.** `engine.py selfcheck`: 400 cặp (ticker, cuối tháng) ngẫu nhiên seed 20261101, so
   `dcf_valuation.fair_value(..., price=Price)` (frame domestic_v2, OShares fin ép bằng `pin_oshares_source_fin`):
   189 ok + 211 NOT_COMPUTED khớp cả hai phía, **mismatch = 0** (dung sai 1e-6 tương đối).
   Chạy 3 môi trường: TZ phiên mặc định (lần đầu), `env -u TZ` (`out/selfcheck_noTZ.txt`, rc=0), `TZ=America/New_York`
   (`out/selfcheck_NY.txt`, rc=0) — cùng kết quả.
2. **Bảng biến thể neo vào engine.** `variants.py` assert V0 == `engine.current_fv` (max lệch tương đối 0,0, in trong
   `out/run_variants.txt`).
3. **Dữ liệu đầu vào**: `data/bq_cache/*` vintage 30/10/2026 (manifest); `data/px_2008_2012.csv.gz` (BQ `tav2_bq.ticker`
   time,ticker,Close,Volume 2008–2012, 539.736 dòng, tải 01/11/2026 23:00 ICT). Nối 2012/2013 kiểm tay VNM/FPT/VNINDEX liên tục
   (`out/run_beta.txt`). Bản .csv.gz == .csv gốc (pandas `equals` True).
4. **md5 artefact chính** (lần chạy cuối): `data/panel_monthly.parquet` 16c49b7cd2538f25a3ff55fd2eb52a87 ·
   `data/fv_variants.parquet` 0b761159343a18f6712fd88e4cf3190b · `out/t_variants_summary.csv` 08b8b5905615f8d9fae085d8a101f04f.
   Parquet trong `data/` không commit (dựng lại bằng `engine.py build` ~5 phút).
5. Không sửa file production nào; không đặt lệnh; không đổi cron. Thứ tự chạy: xem cuối REPORT.md.
6. Giới hạn đã biết: bảng biến thể beta dùng kẹp p5/p95 của lần chạy beta đầu (23 quý: 0,05/2,37) — lần cuối (49 quý) là
   0,03/2,34; không chạy lại vì biến thể đó không được khuyến nghị.
