---
kind: script-output
status: CANONICAL
source: data/rating_8l_forward_events.csv
group: rating-8l
note: ledger PIT APPEND-ONLY — giá trị lần đầu thấy; KHÔNG phải snapshot hôm nay; dùng được làm rating_prev PIT cho mùa BCTC
writer: bin/rating_8l_forward_tracker.py (cron 11:15 UTC = 18:15 ICT hằng ngày, cài 2026-10-20)
---

# data/rating_8l_forward_events.csv

**Status: CANONICAL (ledger PIT, append-only, PAPER-ONLY)**

## Là gì
Mỗi dòng = 1 sự kiện (ticker, quarter) lần đầu thấy: `rating_prev` (hạng 8L TRƯỚC khi quý mới
re-rate) → `rating_new`, route, nhóm `grp`, cờ `x_null/x_definite/x_early7/excl`, `first_seen`
(timestamp ICT), `prereg_md5`. Header 13 cột: ticker, quarter, eff_date, route, rating_prev,
rating_new, grp, x_null, x_definite, x_early7, excl, first_seen, prereg_md5.

## Ai ghi / cadence (đã verify)
- Writer duy nhất: `mike/bin/rating_8l_forward_tracker.py` (`EVENTS_CSV`, `to_csv(tmp)` +
  `os.replace`, khoá (ticker, quarter): đã có thì KHÔNG ghi lại; header lệch ⇒ dừng, không ghi).
- Cron: `15 11 * * *` (crontab thật, grep 2026-11-17) = 18:15 ICT, `flock` + `timeout 900`;
  dòng cài ghi ở `kb/cron_registry.md`. File nằm trong git repo ngoài (`git ls-files` có, `add -f`).
- mtime 2026-11-16 18:15 ICT; 1.395 dòng = 283 (2026Q2) + 1.112 (2026Q3), 1.167 mã, 0 `rating_prev` NaN
  (đo 2026-11-17, `pd.read_csv`).

## Ai đọc
- `newdeals_season.py::_bootstrap_prev` (mùa đầu chưa có snapshot): rating mùa trước = `rating_prev`
  của (ticker, quarter=mùa). Chỉ đọc; thiếu file ⇒ rating mùa trước rỗng (mọi mã golden hiện tại = VÀO).
- PREREG forward OOS `agents/Taylor/research/rating_8l_forward_bt_20261020/` (futility N≥300; mốc 2027-10-20).

## Bẫy
1. **Không phải rating hiện tại** — rating hiện tại ở `rating_8l.csv`; file này chỉ có hạng quanh sự kiện quý.
2. **Chỉ phủ mã có sự kiện re-rate của quý** (không phải mọi mã mọi quý) ⇒ mã thiếu dòng = không có
   `rating_prev` PIT, không suy ra "chưa xếp hạng".
3. KHÔNG sửa tay / ghi đè: ledger append-only, PREREG md5 gắn vào từng dòng.

↩ [Index nhóm](index.md)
