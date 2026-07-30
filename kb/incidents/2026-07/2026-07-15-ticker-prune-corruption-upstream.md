---
kind: incident
date: 2026-07-15
topic: ticker-prune-corruption-upstream
title: >-
  2026-07-15 — ticker_prune cũng bị corruption upstream (mở rộng sự cố ticker_financial 07-14): rows 07-08→07-14 bị xóa/ghi đè, daily_refresh 07-14 ABORT, DT5G 07-14 là ffill trên base stale
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-15 — ticker_prune cũng bị corruption upstream (mở rộng sự cố ticker_financial 07-14): rows 07-08→07-14 bị xóa/ghi đè, daily_refresh 07-14 ABORT, DT5G 07-14 là ffill trên base stale

**What happened.** Ops-health-check 12:45 flag `macro_health.json` cũ 21.2h (job
`Winston_20260715_054514`). Truy vết: daily_refresh_v34b 18:30 tối 07-14 **ABORT ở precheck**
(đúng thiết kế) — `ticker_prune` chỉ có 10 tickers cho 2026-07-14 sau 6 lần retry (~1.5h, tới
19:45) → không chạy tới bước 14 (macro_healthcheck) → macro_health đóng băng ở bản 15:30 07-14.
Điều tra tiếp lộ blast radius: **ticker_prune hiện chỉ còn 7-10 tickers/ngày cho MỌI ngày từ
2026-07-08** (07-08=7, 07-13=7, 07-14=10; đầy đủ ~225/ngày tới 07-07) — trong khi chính precheck
07-13 18:30 đã đếm được **265 tickers cho 07-13**. Tức là rows bị XÓA/ghi đè retroactive trong
cửa sổ 07-13 18:30 → 07-14 18:30 — **trùng đúng cửa sổ regression của `ticker_financial`**
(MAX lùi 07-08→2026-05-04, phát hiện 07-14, job `Winston_20260714_174411`). Giả thuyết cơ chế
(cho BQ admin): ticker_prune là subset lọc chất lượng cần fundamentals — nếu upstream regenerate
rolling window hàng ngày trên ticker_financial đã hỏng → gần như mọi tên rớt filter → chỉ còn
7-10 tên/ngày. Bảng vẫn đang được ghi tiếp (lastModified 12:48 07-15).

**Hệ quả dây chuyền đã xảy ra.** 19:00 07-14 `bq_freshness_check` báo ALL FRESH (lúc đó VNINDEX
07-14 chưa ingest → gap=0) → pipeline chạy → `publish_gated_state` xuất row DT5G **2026-07-14 =
ffill trên base stale 07-13** (có WARNING trong log nhưng không fail) → gate MAX_STATE_LAG=0
downstream bị vô hiệu vì row ffill tồn tại. Plan 07-15 không bị ảnh hưởng thực chất (0 BAL/0 LAG,
basket-swap từ composition cũ, user đã duyệt biết bối cảnh; 2 phiên 07-15 thực thi bình thường).

**Fix (trong thẩm quyền).** Chạy lại `macro_healthcheck.py` standalone 12:50 → HEALTHY /
DT5G_macro, `macro_health.json` tươi lại (base age 2td < ngưỡng 3). KHÔNG rebuild bảng nguồn,
KHÔNG đổi cron/gate — user đang chờ BQ admin xác nhận upstream rồi mới quyết (context pack 07-15).

**Dự đoán tối 07-15 (để không ai bất ngờ).** 18:30 refresh sẽ ABORT tiếp (prune 07-15 = 7 tên);
19:00 gate sẽ FAIL/block DollarBill NẾU VNINDEX 07-15 ingest kịp trước 19:00 (bảo vệ đúng); nếu
VNINDEX cũng trễ → lại ALL FRESH giả + ffill tiếp. 20:00 fa_ratings wrapper sẽ tự ABORT (bảo vệ
đã chứng minh 07-14). Từ thứ Năm 07-16, base DT4 chạm ngưỡng 3 trading-day → macro_health tự
DEGRADED → `get_gated_state` fail-safe về DT4-only (đúng thiết kế).

**Lesson.** (1) Freshness gate theo MAX(time) không bắt được "ngày tồn tại nhưng thin" — precheck
đếm-số-tên của daily_refresh là lớp bắt được, gate BQ thì không; cân nhắc thêm row-count check khi
sửa gate sau sự cố. (2) `publish_gated_state` ffill-on-stale-base publish row mới làm gate
MAX_STATE_LAG=0 mất tác dụng — cần quyết (sau khi upstream ổn) có nên fail-hard thay vì WARN.
(3) Corruption upstream lan theo dependency: financial hỏng → prune hỏng theo — khi 1 bảng nguồn
regress, phải quét ngay các bảng derived cùng pipeline.

**Addendum (job song song `Winston_20260715_054508`, cùng buổi chiều — mitigations bổ sung).**
(a) **Backup time-travel** trước khi bằng chứng hết hạn (BQ time-travel chỉ giữ 7 ngày):
`tav2_bq.ticker_prune_ttbackup_fresh_20260713` = CLONE `FOR SYSTEM_TIME AS OF 2026-07-13 12:00 UTC`,
verified 912.209 dòng / 265 mã ngày 07-13 / đủ 264-267 mã cho 07-08..07-13 — nguồn khôi phục sẵn
sàng khi user quyết (cùng bộ với `ticker_financial_ttbackup_fresh_20260714`). (b) **Restore cache
local** `data/bq_cache/ticker_prune/2026.parquet` từ clone này (sync 23:45 đêm 07-14 đã mirror bảng
hỏng → cache mất sạch 07-08..07-13; live không ảnh hưởng — gap_ref chỉ bật ở paper `main` — nhưng
paper evidence + DC-book + screener đọc sai). Lưu ý: sync 23:45 tối 07-15 sẽ re-mirror bảng hỏng
nếu upstream chưa sửa. (c) **Đóng lỗ hổng Lesson (1) ngay**: thêm depth-check (COUNT DISTINCT
ticker của ngày mới nhất, ngưỡng 200 — cùng ngưỡng precheck daily_refresh) vào
`bin/bq_freshness_check.sh` (FAIL → block DollarBill, kể cả kịch bản "VNINDEX trễ → ALL FRESH giả"
trong Dự đoán ở trên) và `bin/preflight_check.sh` §5 (WARN rõ ràng thay vì `lag=0d ✓` giả) —
commit `1b66428`, test standalone trên bảng hỏng thật: lag=0/names=8 → bắt đúng.
