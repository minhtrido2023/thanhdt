# SELFCHECK — dcf_rate_proxy_20261102 (job Taylor_20261102_012810)
Lệnh: `./selfcheck_tz.sh` (chạy analysis.py 3 lần: TZ mặc định / `env -u TZ` / `TZ=America/New_York`, so md5 out/*.csv, rồi `selfcheck.py` 2 lần). Log: `out/selfcheck_run.txt`, md5: `out/md5_{default,noTZ,NY}.txt`.

Kết quả (đo 02/11/2026):
```
TZ md5 IDENTICAL (default / env -u TZ / America/New_York)
(1) FV analysis.fv vs level.fv (VND/cp) max|Δ| = 0.000e+00
(2) %RẺ (a) 0.659864 vs V0 0.659864; n 147 vs 147
(3) r*: max|median log P/FV| tại r* = 7.83e-06 trên 155 tháng (r* làm tròn 4 số ⇒ dung sai 1e-3)
SELFCHECK PASS
SELFCHECK PASS
```
- (1) FV của analysis.fv ở r=12,25%/g_T 5,5% khớp `dcf_level_rerun_20261102/level.fv` (đường live, s=0,5) — 0 lệch toàn panel (22.988 dòng).
- (2) Kịch bản (a) tháng 10/2026: %RẺ 0,659864, n=147 = đúng V0 production-live của `level_live_impact_20261030.csv`.
- (3) r\* là nghiệm thật: median log(P/FV) tại r\* ≤ 7,8e−6 trên 155 tháng.
- md5 9 nhóm file out/*.csv trùng giữa 3 môi trường TZ.
- Cảnh báo "OSHARES_SOURCE='live' bi EP ve 'fin'" là của `engine.py` (ghim dcf_valuation về fin); analysis dùng cột `os_live` của panel trực tiếp — (1) xác nhận đúng đường live.
- Lỗi đã bắt & sửa trong phiên: `step_to_month` căn index Series ⇒ dep12/refi toàn NaN ở lần chạy 1; sửa bằng np.asarray (chạy lại toàn bộ sau sửa).

Dữ liệu BQ (02/11/2026 ~08:30 ICT):
```
bq query --use_legacy_sql=false --format=csv --max_rows=100000 "SELECT series_key, observation_date d, value, fetched_at FROM tav2_bq.macro_indicator WHERE series_key IN ('vn_bond_10y','vn_interbank_3m','vn_policy_rate','vn_cpi_yoy') AND observation_date>='2012-01-01' ORDER BY 1,2"   # data/te_macro.csv, md5 ea4b2ca1189e75a3ad66efe7fc7400b0
bq query --use_legacy_sql=false --format=csv --max_rows=100000 "SELECT t.time, t.Close, t.VNINDEX_PE FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2012-01-01' ORDER BY t.time"   # data/vnindex_pe.csv, md5 e6d8978981c3830f947ac0934e32cc7e
```
