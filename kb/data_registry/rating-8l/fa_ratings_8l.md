---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.fa_ratings_8l
group: rating-8l
note: as-of 8L, refresh định kỳ, ghi-BQ xác nhận THẬT 2026-07-12
writer: rating_8l_history.py refresh_bq_table() qua mike/bin/refresh_fa_ratings_8l.sh, cron weekly thứ Bảy 08:30 ICT + cron TẠM T3 20:00 ICT đến hết 2026-08-04
---

# tav2_bq.fa_ratings_8l

**Status: CANONICAL (as-of 8L) — refresh định kỳ, ghi-BQ đã xác nhận THẬT 2026-07-12**

## Là gì
Lịch sử point-in-time 8L rating (ticker, time=eff_date, route, rating 1–5, tier) — nguồn cho custom30
builders, `custom_basket.rating_asof`, regime_size overlay, DC-book double-confirm, mọi audit as-of, dự
án re-tune SIGNAL_V11.

## Ai ghi / cadence
`rating_8l_history.py refresh_bq_table()` qua wrapper `mike/bin/refresh_fa_ratings_8l.sh`, cron
**weekly thứ Bảy 08:30 ICT** (Winston proposal + user approved 2026-07-11) + cron TẠM **T3 20:00 ICT
đến hết 2026-08-04** cho mùa BCTC Q2 (job Winston_20260713_103213, guard tự hết hạn — xem
`cron_registry.md`). Bao gồm forensic-exclude override rows (append-at-flag-date, no hindsight).

## Bẫy
Republish làm mọi backtest as-of lệch nhẹ → CSV pinned trong `results_registry.md` mới là chuẩn đối
chứng. Lịch sử identity: test tay 2026-07-11 từng fail (`Access Denied` — wrapper thiếu `source
wc_env.sh`, rơi về service account read-only `bq-reader-8l`); **fix `a9716f6` + test ghi THẬT
2026-07-12 OK: lastModified 06-20→07-12, rows 52.433→52.449, quant-skeptic CONFIRMED** — hết câu hỏi
identity treo, lần scheduled đầu (07-14 T3 tạm / 07-18 T7) chỉ là chạy bình thường (wrapper alert
Trading Daily nếu fail, không im lặng).
