# SELFCHECK — erp_domestic_v2_20261030 (job Taylor_20261030_041731)

1. **PREREG v2 `2e67a6de7` commit 11:21:54 ICT, TRƯỚC mọi số v2.** PREREG §0 khai thẳng là không mù và ghi kết quả nhẩm trước (C ≈ 5,4, không bền). Kết quả thật: 5,424, khoảng 5,222–6,150, khớp.
2. **Cửa sổ lịch sử trùng byte vòng 1.** `erp_v2.py` assert G, A, tái định giá, rf TB, N của 3 cửa sổ trùng `../erp_domestic_20261030/out_erp_history.csv` (sai số < 1e-9).
3. **DGC r7 tái lập lệch 0.** 21.407 / 32.925 / 41.779, EV 29.817 (assert trong `erp_v2.py`; dòng `SELFCHECK` trong `run_v2_stdout.txt`).
4. **Tất định 2 múi giờ.** Chạy `TZ=UTC` rồi `TZ=Pacific/Kiritimati`, mỗi lần `erp_v2.py` + `impact_v2.py` (`/home/trido/thanhdt/wc_venv/bin/python`). md5 trùng **14/14**:
```
574f8df37037d4f1905f8ca14834330f  out_imp_asof_per_ticker.csv
25ffe8e04f76d59c9c2308cdad964ed0  out_imp_asof_summary.csv
36724dcea7982dd6aad165f74802b8a1  out_imp_history_quarterly.csv
6933b218c0ada9c4dc8a10f5ceec2598  out_imp_history_summary.csv
8ca2d5ce48dc732a251d3f334839e02f  out_imp_live.csv
5794e796750ccb5d77b9e03b0fc1c598  out_imp_oshares_flags.csv
ebb2c396982d5bbeb577773b20ef540d  out_v2_dgc.csv
4a86ae66bac8835d00264a129ddb9750  out_v2_eps_growth.csv
7d55d34276ffd4da43cca67ee1d008e7  out_v2_erp_choice.csv
1f52053bbf657cc455b92adb7a786986  out_v2_implied.csv
e64e15819202f190e1277bc59f08a987  out_v2_robustness.csv
1662c184a7804e5262fe57f5d16438e2  out_v2_terminal_multiple.csv
b26bdb93f8c5978f34d3a08738844907  run_imp_stdout.txt
85c329512af7c23e2b2b7d52a9b6a572  run_v2_stdout.txt
```
5. **Dữ liệu bất biến** (`fetch_v2.py`, kéo 30/10/2026 khoảng 11:30 ICT; rổ = `tav2_mike.universe_pit` qua cache vòng 1, KHÔNG dùng ticker_prune):
```
8eedaabeecc55b368131b640a9175d9b  data/close_qe.csv
e46fd2da9aed985e570556a268deee76  data/oshares_check.csv
39c8ec294afe320f09923cef1bf597ee  data/fin_snapshot.parquet
```
   - Nguồn local tại lúc chạy: `data/bq_cache/ticker_financial.parquet` 03ee922ef732fe18bbcfbcdc194ea255 · `fa_ratings_8l.parquet` a3b5bb7023a8a14c23218da511c744d0 (route tài chính) · `ticker_1m.parquet` 350b82f75354d8fcb2649383b1f7bc71 (ICB).
   - `deposit_rate_vn`, `cpi_vn`, `gdp_growth_vn` (khung hiện hành) đọc file sống. Tái lập byte chỉ được bảo đảm khi các file nguồn này chưa đổi. Giá trị đã resolve được in trong `run_v2_stdout.txt`: r hiện hành 13,9, lãi huy động 7,4, CPI 5 năm 3,442, GDP 15 năm 6,222.
   - `cpi_vn` in cảnh báo vùng CPI 09–12/2026 chưa có số thật (forward-fill). Cảnh báo này ảnh hưởng CPI 5 năm cho cả khung cũ lẫn mới như nhau.
6. **Patch `f3f756256` (nhánh `session/erp-domestic-dcf-20261030`, worktree `/home/trido/thanhdt/wt-erp-domestic-dcf-20261030`).** `WorkingClaude/dcf_rate_frame_selfcheck.py` PASS ở cả `TZ=UTC` lẫn `TZ=Pacific/Kiritimati`:
   - (a) knob không đặt và `=legacy` ⇒ output 336 mã trùng byte `dcf_valuation.py` của main (md5 4c0cf6e6ee6b267937c793c7dfda9a44).
   - (b) `=domestic_v2` ⇒ MoS (4 chữ số), status, robust khớp mô phỏng `out_imp_asof_per_ticker.csv` 145/145; r = 0,1225 hằng; g_T ≤ 0,055.
   - (c) DGC r7 21.407 / 32.925 / 41.779 / 29.817. Lưu ý: `model_ke.py` không import `dcf_valuation`, nên đây là kiểm "số gốc không bị đụng", KHÔNG phải kiểm knob.
   - (d) knob sai (`domestic`) ⇒ ValueError lúc import.
   - Phạm vi selfcheck (§23): `dcf_valuation.py` là lõi của consumer đường tiền, nhưng patch chỉ thêm nhánh sau knob, và (a) chứng minh nhánh mặc định trùng byte. Các selfcheck CCTG (`cctg_deposit_wiring_selfcheck.py`, `cctg_tier2_series_selfcheck.py`) chạy env mặc định nên không bị ảnh hưởng. Chúng sẽ hỏng nếu bật knob toàn cục; chưa chạy, ghi ở REPORT mục 5.
7. Lệnh kiểm tay số trong REPORT: Ke theo β, MoS DGC nếu OShares ×1,206 = 0,472, khoảng r hiện hành 11,2–14,0%, lệch %RẺ 0…−3,8pp, tương quan hạng min 0,99989. Tất cả là `python3 -c` inline trên các `out_*.csv` trong phiên này.
