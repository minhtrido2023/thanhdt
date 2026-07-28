---
kind: local-file
status: DERIVED
source: data/bq_cache/*.parquet (11 bảng)
group: bq-cache
note: mirror local threads=1 (~100ms vs 5-15s BQ)
writer: sync_bq_cache.py qua sync_bq_cache_daily.sh, cron 23:45 ICT
tables: ticker, ticker_prune, ticker_financial, ticker_1m, vnindex_5state_dt5g_live, vnindex_5state, vnindex_5state_tam_quan_v34b_clean, vnindex_5state_dt_4gate, fa_ratings, fa_ratings_8l, custom30v_8l
---

# `data/bq_cache/*.parquet` (11 bảng: `ticker`, `ticker_prune`, `ticker_financial`, `ticker_1m`, `vnindex_5state_dt5g_live`, `vnindex_5state`, `vnindex_5state_tam_quan_v34b_clean`, `vnindex_5state_dt_4gate`, `fa_ratings`, `fa_ratings_8l`, `custom30v_8l`)

**Status: DERIVED (mirror)**

## Là gì
Cache local threads=1 (~100ms vs 5-15s BQ) cho backtest/sim.

## Ai ghi / cadence
`sync_bq_cache.py` qua `sync_bq_cache_daily.sh`, cron 23:45 ICT.

## Bẫy
3 bẫy: (1) trễ 1 ngày cho mọi script chạy trước 23:45 (sự cố 2026-07-09); (2) **cache mirror CẢ bảng
trap y nguyên tên** — `bq_cache/vnindex_5state.parquet` = v3.4b BASE chứ không phải DT5G, đọc cache
không cứu khỏi đọc nhầm bảng; (3) cache mirror cả bảng FROZEN (`vnindex_5state_dt_4gate` chết 06-02) —
mtime parquet là hôm qua nhưng DATA bên trong đứng yên từ nguồn (`fa_ratings` từng thuộc nhóm này, hết
frozen từ 2026-07-12 khi refresh weekly sống lại). Riêng `fa_ratings`/`fa_ratings_8l`: nguồn refresh
kiểu DELETE+INSERT/re-rank → sync chuyển sang `full_only` (full re-download mỗi đêm kể cả `--delta`,
job Winston_20260713_103213) — delta-append cũ không vớt được row bị rewrite, gây count-mismatch giả
mỗi thứ Bảy. Từng có bug sync `ticker` chết âm thầm ~06-26 (chunk parquet cũ) — đã fix; (4)
**`ticker`/`ticker_prune` là THƯ MỤC chunked theo năm** (`data/bq_cache/ticker_prune/<year>.parquet`,
đọc bằng glob `ticker_prune/*.parquet`) từ 2026-06-26 — file monolith cũ `ticker_prune.parquet` KHÔNG
được sync nữa, đóng băng 06-26, user phát hiện stale 07-13; đã archive sang
`data/archive/ticker_prune_monolith_frozen_20260626.parquet` + sửa hết 28 file .py từng đọc nhầm (27
script research/screen + `trading_bot/executor.py:507`) sang chunked (job Winston_20260713_143546).
Đường dẫn đúng DUY NHẤT giờ là thư mục chunked.
