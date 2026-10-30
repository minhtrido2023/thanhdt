# SELFCHECK — erp_domestic_20261030 (job Taylor_20261030_034654)

1. **PREREG commit `f4a6cce0c` TRƯỚC khi tính số** (chỉ đọc schema trước đó). Lệch PREREG đã báo trong REPORT:
   VNINDEX_PE có từ 2007-12-03 ⇒ cửa sổ D3 "dài nhất đo được" = 2011→ (PREREG dự kiến 2016-07→ trong ngoặc); độ nhạy 2016-07→ in kèm (D3' 7,15 ⇒ trung tâm 6,08).
2. **Tái lập DGC tầng A ở Ke 14,9% lệch 0 đồng** (assert trong `erp_domestic.py` part6, dùng lại `../dgc_discount_rate_20261029/model_ke.py`, r7 không sửa):
   DCF 21.407 / 32.925 / 41.779 · EV 29.817 (dòng `SELFCHECK` trong `run_stdout.txt`).
3. **Tất định 2 múi giờ** — `TZ=UTC` và `TZ=Pacific/Kiritimati` chạy `/home/trido/thanhdt/wc_venv/bin/python erp_domestic.py` ⇒ md5 trùng byte:
   ```
   56dfc697068b0d9eab308785d48a7c44  out_dgc_ke.csv
   d0ce271df7a1ba99f1bef3ddef28be31  out_ep_estimators.csv
   2678438f5b2d58657aa12cb9a1933876  out_ep_history_quarterly.csv
   e5a9b5a5e3395f5f1a6469207101ec43  out_erp_choice.csv
   92497c9384e06631a9b892541a747b39  out_erp_history.csv
   d839dbbd1f25eb14149a71094a190ca8  out_icc.csv
   c1d41cc1c5665527983dda6eb81f892a  out_justify_grid.csv
   05f030da0f7d07cacb33181d5c4c1bee  out_rf_proxies.csv
   ```
   (`run_stdout.txt` md5 2cdce7d3… ở lần chạy trước khi sửa nhãn in "D3 (2011→"; số không đổi.)
   Bootstrap seed cố định 20261030 ⇒ tất định.
4. **Dữ liệu bất biến** (`data/`, kéo 30/10/2026 ~10:50 ICT bằng `fetch_data.py` [BQ] + `cache_local.py` [local]):
   ```
   e7ab3ef32701b28799224e42eb87a24e  data/snap_universe_pit_qe.csv   (universe_pit in_universe ∩ ticker, 52 ngày cuối quý 2014Q1→2026-10-29, 18.280 dòng)
   f5478805bfb6017062d4068521cae1e3  data/vnindex_daily.csv          (2007-12-03→2026-10-29, 4.716 phiên)
   2354e2b216b82d9ba431fb479650995b  data/vnindex_tr_daily.csv       (copy data/benchmark, 5 dòng cuối provisional)
   ff831cc1e49bc35cb2281b260741ea50  data/deposit_big4_12m_daily.csv
   9e3bdd662e753af183e28590be7a7993  data/fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv
   4157942c8bdbf081354c1805877d2747  data/tpcp10y_annual.csv         (9/16 điểm chưa kiểm chứng)
   ```
   Rổ = `tav2_mike.universe_pit` (KHÔNG ticker_prune). Point-in-time: rổ + PE (giá thô, PIT theo registry) tại từng ngày; không cột `profit_*`.
5. Kiểm tay: top-10 PE tổng hợp 14,2 vs phần còn lại 10,6 (lệnh inline trong phiên, cùng `data/snap_universe_pit_qe.csv`).
   r−g `dcf_valuation` (13,9−7,4=6,5 ⇒ 15,4×; 11,8−6,75=5,05 ⇒ 19,8×; 11,8−5,5=6,3 ⇒ 15,9×) là tính tay, KHÔNG chạy `dcf_valuation.py`.
6. Không kiểm định p-value: N độc lập ≈ 12–16 năm; bootstrap CI chỉ mô tả.
