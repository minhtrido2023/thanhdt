---
kind: project
owner: Winston
status: closed
updated: 2026-11-19
title: "ĐỀ XUẤT cron — vintage macro_indicator + commodity_prices (Mike duyệt rồi cài; Winston KHÔNG tự cài)"
---
# ĐỀ XUẤT cron — vintage macro_indicator + commodity_prices (Mike duyệt rồi cài; Winston KHÔNG tự cài)

Job `Winston_20261119_090441`. Script: `mike/bin/snapshot_macro_commodity_vintage.py` (+ `_selfcheck.py`). Host = UTC.

```
20 16 * * * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && flock -n mike/state/macro_vintage.cron.lock timeout 300 python3 mike/bin/snapshot_macro_commodity_vintage.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/snapshot_macro_vintage_$(date +\%Y\%m).log 2>&1
```
= 23:20 ICT hằng ngày, 7 ngày/tuần.

## 4 câu hỏi §11
1. **Đọc gì, vintage nào:** BQ LIVE `tav2_bq.macro_indicator` + `commodity_prices` (script pop `BQ_LOCAL_CACHE`; cache sync không đụng 2 bảng này).
2. **Tươi lúc nào (ĐO THẬT):** `lastModifiedTime` hôm 18/11: macro_indicator 15:01 UTC, commodity_prices 16:04 UTC (= bq_admin nạp 23:00 ICT). 16:20 UTC cách mốc commodity ~16' ⇒ chụp được lượt nạp đêm đó. Nếu một đêm bq_admin nạp trễ hơn 16:20, vintage ngày đó phản ánh lượt nạp đêm trước (không sai nhãn: `source_fetched_at` ghi lượt scrape thật).
3. **Cần T hay T-1:** cần trạng thái bảng nguồn SAU lượt nạp đêm của ngày ICT đó; `snapshot_date` neo ICT (§16, selfcheck pass dưới `env -u TZ` và `TZ=Asia/Tokyo`).
4. **Consumer:** nghiên cứu PIT của Taylor (kế hoạch REPORT §5); không deadline cứng. Lỗi ⇒ Discord topic `architecture` kèm exception thật.

Xung đột: 16:00 (`ai_momentum_cron`, send_plan_report), 16:30 (`late_plan_catchup`), 16:45 (`sync_bq_cache_daily` nặng) — cách ≥10', job ~10 giây, ~42 MB quét (~$0,0005/ngày). Lưu trữ ~75 MB/ngày ⇒ ~27 GB/năm ≈ $0,5/tháng ở cuối năm đầu (ước tính từ `numBytes` nguồn 14,5 + 60,8 MB; chưa đối chiếu billing).

## Dòng đề xuất cho `kb/cron_registry.md`
`| 23:20 ICT hằng ngày (16:20 UTC) — ĐỀ XUẤT 2026-11-19 | snapshot_macro_commodity_vintage.py | BQ live tav2_bq.macro_indicator + commodity_prices | tav2_mike.{macro_indicator,commodity_prices}_vintage (append-only, partition snapshot_date) | Taylor R&D PIT | độc lập; cách sync cache 16:45 ≥25' | vintage đầu = 2026-11-19, KHÔNG phải lịch sử |`

## Đã làm sẵn (ngoài worktree, theo chỉ đạo "chụp vintage đầu tiên")
Chạy tay 19/11 09:09 UTC: 84.491 + 350.354 dòng vào `tav2_mike.*_vintage`, snapshot_date 2026-11-19; chạy lại = SKIP.
