---
kind: bigquery-table
status: CANONICAL
source: lithe-record-440915-m9.tav2_mike.universe_pit
group: price-volume
production_since: 2026-07-22
writer: Winston — mike/bin/build_universe_pit.py --date $TODAY, pipeline-1b của bq_freshness_check.sh, 19:00 ICT T2-T6
---

# `lithe-record-440915-m9.tav2_mike.universe_pit`

**Status: CANONICAL — PRODUCTION** (2026-07-22)

## Là gì
Universe point-in-time append-only: bảng do đội Mike sở hữu, 1 dòng/ticker/phiên, `in_universe`
flag; tính CHỈ từ cột thô `tav2_bq.ticker` (KHÔNG đọc `ticker_prune`). Dataset `tav2_mike` RIÊNG
(tránh `WRITE_TRUNCATE` từ bq_admin).

## Ai ghi / cadence
**Winston**: `mike/bin/build_universe_pit.py --date $TODAY`, pipeline-1b của `bq_freshness_check.sh`,
19:00 ICT T2-T6, sau ticker FRESH BLOCK.

## Bẫy
**Consumers**: `golive_recommend_v23.py` (panel D1), `custom_basket.py` (custom30V), **(chờ merge
2026-07-29)** `macro_state_live.py` breadth-decoupling guard của DT5G — job `Taylor_20260729_152031`,
patch sẵn ở `mike/agents/Taylor/exp_dt5g_breadth_pit/`, đo 0/3135 phiên đổi state —
assert_universe_covers() sẽ crash nếu thiếu phiên hôm nay. Build idempotent: B8_DUPLICATE nếu đã có →
exit 1 (nhưng pipeline-1b wrapper check BQ count để phân biệt với fail thật). Script đọc BQ LIVE,
KHÔNG qua `BQ_LOCAL_CACHE`.

**`universe_pit_p2_selfcheck.py` T1 FAIL tại rổ 2025-05-05 (điều tra 2026-08-08, Mike) — KHÔNG
phải vi phạm point-in-time, là chênh lệch ĐỘ ĐẦY ĐỦ đã biết giữa 2 nguồn.** Rổ `custom30V` tại
2025-05-05: nguồn `prune` thiếu `BAF` (có `TCM`), nguồn `pit` có `BAF` (không `TCM`) — 7/8 mốc
rebal khác trong cửa sổ test đều byte-identical, kể cả mốc LIVE hiện tại. Xác minh bằng BQ trực
tiếp: `BAF` có **0 dòng trong `tav2_bq.ticker_prune` toàn bộ lịch sử** (chưa từng có, không phải
gap 1 giai đoạn), trong khi `tav2_bq.ticker` có đủ dữ liệu OHLCV liên tục từ 2025-01-02 và thanh
khoản **CAO HƠN TCM** (BAF ~101 tỷ đ/phiên vs TCM ~54 tỷ đ/phiên, trung bình 02/2025→05/2025) —
loại trừ giả thuyết "BAF bị loại vì kém thanh khoản". Kết luận: `ticker_prune` (bảng cũ, tuyển
chọn thủ công hơn) đơn giản là chưa từng có `BAF` — đúng loại lỗ hổng độ đầy đủ mà `universe_pit`
được xây để sửa (cùng lớp với sự cố "58 tên bị rớt âm thầm" 2026-07-29 đã ghi ở `current_ops.md`).
`universe_pit` đang làm ĐÚNG việc của nó. Khuyến nghị: T1 nên coi 1 chênh lệch/8 mốc là PASS có
điều kiện (báo diff, không FAIL cứng) khi nguồn gây lệch là do `prune` thiếu tên có thanh khoản
tốt hơn — byte-identical với 1 bảng đã biết là thiếu tên không phải bar đúng. Chưa sửa
selfcheck (quyết định về ngưỡng test, để Taylor/user quyết).
