# Đề xuất cron — commodity_sue_decomp_forward_tracker (PREREG-4) — CHƯA CÀI, chờ Mike duyệt

Host cron chạy theo UTC. 14:20 UTC = **21:20 ICT**. Slot gần nhất đang dùng: 14:00 và 14:45 UTC (lệch ≥20').
Chạy cả cuối tuần (cache không sync cuối tuần ⇒ lần chạy đó vô hại, chỉ không có sự kiện mới).

```cron
# commodity SUE decomp forward (PREREG-4, PAPER-ONLY) — 21:20 ICT, cửa sổ BCTC: 10/M1 → 15/M2 sau mỗi quý.
# Sau 19:00 (earnings_surprise_data.pkl writer BQ sống, nguyên tử) và sau 23:45 đêm trước (bq_cache T-1).
# Không ghi bus/Telegram. Verdict chỉ qua commodity_sue_decomp_forward_review.py (từ chối trước 2027-09-01).
20 14 10-31 1,4,7,10 * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && flock -n mike/state/commodity_sue_decomp_forward_tracker.cron.lock timeout 600 $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_tracker.py >> mike/logs/commodity_sue_decomp_forward_tracker.log 2>&1
20 14 1-15 2,5,8,11 * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && flock -n mike/state/commodity_sue_decomp_forward_tracker.cron.lock timeout 600 $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_tracker.py >> mike/logs/commodity_sue_decomp_forward_tracker.log 2>&1
```
BẮT BUỘC `$DNA_PYEXE` (pandas 3: đọc `earnings_surprise_data.pkl`; python3 hệ thống raise `NotImplementedError`).
Thời gian chạy đo 2026-10-26: ~5 s (gồm 1 query BQ TE). Phải sao lưu crontab trước khi cài, cập nhật
`kb/cron_registry.md` + `kb/cron_registry/CHANGELOG.md` cùng commit.

## 4 câu hỏi (kb/cron_registry/_adding-cron-policy.md)
1. **Đọc gì, vintage nào?**
   - BQ SỐNG: `tav2_bq.commodity_prices`, `source='trading_economics' AND cadence='daily'` (bq CLI, không qua cache).
   - Cache T-1 (sync 23:45 ICT): `data/bq_cache/ticker_financial.parquet`, `data/bq_cache/ticker/*.parquet`,
     `data/bq_cache/universe_pit/*.parquet`.
   - File local: `data/earnings_surprise_data.pkl` (writer 15:30 `refresh_lagged_caches.py` không nguyên tử +
     19:00 `refresh_earnings_surprise_pkl.py` nguyên tử) và `data/earnings_events_classified.csv` (15:30), qua
     `lag_live_schedule.live_lag_candidates()`. Chỉ dùng để gắn cờ `lag_qualify` / nhóm NO_COMMODITY.
2. **Tươi lúc nào (artifact)?** TE: bq_admin nạp 23:00 ICT ⇒ dữ liệu tới hôm trước. bq_cache: mtime 23:48 đêm
   trước (đo `ticker_financial.parquet` 2026-10-23 23:48). pkl: mtime 15:30 hằng ngày (đo 2026-10-26 15:30), bản
   19:00 ghi đè nguyên tử. 21:20 nằm sau mọi mốc và xa writer 15:30 không nguyên tử.
3. **Cần T hay T-1?** T-1 là đủ: biến được tính từ BCTC đã công bố + giá TB quý đã khép; sự kiện công bố ngày D
   vào cache đêm D, tracker thấy tối D+1 (≤1 phiên, dưới ngưỡng LATE 10 phiên). post60 chỉ ghi khi t60 ≤ ngày chạy.
4. **Ai tiêu thụ, deadline?** Không ai trong ngày. Consumer duy nhất = `commodity_sue_decomp_forward_review.py` ở
   các mốc 2027-09-01 … 2031-09-01. Lỡ 1 ngày không sao; lỡ >10 phiên sau công bố ⇒ sự kiện đó LATE
   (counts=False) — giám sát qua `cron_health_check` trên log.

## Vì sao cửa sổ đủ
Đo 2022Q1+ (`ticker_financial`): tier A công bố trễ 5–95% phân vị 17–34 ngày sau qend, 0/455 sự kiện >45 ngày,
0,7% <10 ngày (vẫn được thấy ngày 10, cách ≤10 phiên). post60 của sự kiện công bố cuối cửa sổ (~15/M2) chín vào
~giữa M5 ⇒ được tính ở cửa sổ quý sau (giá trị không đổi, chỉ ghi muộn).
