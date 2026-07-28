---
kind: local-file
status: CANONICAL
source: data/vnindex_5state_dt_4gate.csv
group: market-state
aka: chuỗi DT4 local (base + DT 4-gate, KHÔNG macro)
name_alike_trap: tav2_bq.vnindex_5state_dt_4gate (bản BQ ĐÓNG BĂNG 2026-06-02)
writer: build_dt_4gate.py, step [8] daily 18:30 (non-fatal, advisory-only)
---

# data/vnindex_5state_dt_4gate.csv

**Status: CANONICAL (DT4 local)**

## Là gì
Chuỗi DT4 (base + DT 4-gate, KHÔNG macro) — research/ablation.

## Ai ghi / cadence
`build_dt_4gate.py`, step [8] daily 18:30 (non-fatal, advisory-only).

## Bẫy
**Cặp name-alike với bảng BQ `vnindex_5state_dt_4gate`** — bản BQ ĐÓNG BĂNG từ 2026-06-02 (verify
`bq show` 2026-07-11), chỉ bản CSV local này còn sống. `sync_bq_cache.py` vẫn mirror bản BQ frozen
vào `bq_cache/` → đọc DT4 qua cache/BQ = đọc dữ liệu chết.
