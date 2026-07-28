---
kind: bigquery-table
status: DEPRECATED
source: tav2_bq.fa_ratings_v5/_v8c/_v9/_ew5/_pre2014
group: rating-8l
note: research variants; builder script đã archive 2026-07-11
alive_alternative: tav2_bq.fa_ratings_8l
---

# tav2_bq.fa_ratings_v5/_v8c/_v9/_ew5/_pre2014

**Status: DEPRECATED (research variants)**

## Là gì
Các biến thể rating thời nghiên cứu (v9 = RE-rebuild, pre2014 = phần mở rộng backtest trước 2014).

## Ai ghi / cadence
Đóng băng (pre2014 lastModified 05-16; các bản khác cũ hơn).

## Bẫy
Chỉ vài script research cũ đọc. KHÔNG dùng cho việc mới — bản sống là `fa_ratings_8l`. **2026-07-11
(Winston, job Winston_20260711_160905, coding_guidelines §10):** 4 builder script variant tương ứng ở
repo root — `build_fa_ratings_v9.py`, `build_fa_ratings_pre2014.py`, `fundamental_rating_v5.py`,
`fundamental_rating_v8c.py` — đã xác nhận KHÔNG có caller active nào (grep toàn repo + `crontab -l`
thật, chỉ có self-reference + audit script + doc mention) và **git-mv vào `archive/`** (giữ nguyên lịch
sử git, không xoá). `mike/bin/data_registry_audit.sh` mục D đã hết WARN cho 4 file này.
