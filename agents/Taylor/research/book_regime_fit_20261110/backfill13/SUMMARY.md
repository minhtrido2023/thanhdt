> ⛔ **SUPERSEDED 2026-11-10** (job Taylor_20261110_103537) — phần 1a/1b ở đây đã bị thay. Xem `SUPERSEDED.md` và `../backfill13_v2/SUMMARY.md`. KHÔNG chạy `--apply`.

# Job Taylor_20261110_100805 — lagcache (1a/1b/1c/3) — PAPER/NON-CANONICAL
Nhánh `session/lagcache-1110` (worktree /home/trido/thanhdt/wt-lagcache-1110): 45148878e (1a) , b161f3242 (3). KHÔNG merge main.
## 1a
refresh_lagged_caches.py: kéo lại cửa sổ K=10 phiên (env LAGCACHE_K), bản mới thắng, cơ sở RAW (Close=Price, Open=Open*Price/Close, ex-date stale→Close) — logic lagged_cache_patch.py; atomic tmp+replace + `.prev`; depth-check (<50% trung vị 60 phiên trước ⇒ cảnh báo, exit 1 CUỐI script ⇒ papertrade_daily.sh `run()` đếm FAIL + notify_fails, các bước sau vẫn chạy).
Selfcheck lagged_cache_patch_selfcheck.py 9/9 PASS dưới `env -u TZ`, Pacific/Kiritimati, America/Los_Angeles. E2E thật trên BẢN SAO data (/tmp/lagcache_e2e): dòng ngoài cửa sổ giống hệt; cửa sổ 7.812 dòng cũ: Close đổi 1 (max 0,17%), +163 dòng bị thiếu được lấp; canonical md5 không đổi.
## 1b
backfill13/{earnings_px,lagged_pos_ov}_bf13.pkl (MD5.txt). md5 TRÙNG engine/*_fixedA.pkl (module mới tái lập đúng logic đã chứng minh). `python build_backfill13.py --apply` = backup .pre_bf13 + os.replace, từ chối nếu canonical đổi md5 — CHỈ chạy sau review.
## 1c  (xem bus finding)
Rebuild (wd_C_full_cache_frame, /tmp/audit_lag) vs hiện hành: mean12 cuối −0,617 → +0,034, NEGATIVE→TROUGH; w_LAG live cả hai = 0,50. Replay w_LAG (ngưỡng 4%, ffill theo known_date, 2014-01→2026-11-09, 3.354 ngày): 114 ngày khác (3,4%), toàn bộ trong 2025-06-13→2026-03-06 (47 ngày từ 2026-01-01). Consumer: pt_v22_dt5g, pt_v23_audit_2014/ddpark/lagcap/lagqual, lag_dnpr_harness, converge_fullharness_test (đọc data/lag_edge_health.csv hoặc EDGE_HEALTH_CSV), + mike/bin compute_active_nav, lag_gate_exit_check, strategy_fit_dashboard, bq_freshness_check. Khuyến nghị: KHÔNG lên lịch rebuild; nếu muốn thì làm có chủ đích như re-pin 1 trục (EDGE_HEALTH_CSV khác) có chân control, vì đổi nhãn verdict/neg_streak (đóng băng entry LAG khi streak≥3) ngoài w_LAG.
## 3
LIQ_LAG += liquidity_require_positive=True. Rerun (liq2, pkl bf13): LAG không còn mua trên ngày ADV<=0 (trước: HTT 07-24 1,934 tỷ); BAL rows md5 trùng; kết quả danh mục 11-09 −6,55% → −5,87% (cascade).
