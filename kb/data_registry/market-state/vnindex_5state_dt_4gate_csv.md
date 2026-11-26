---
kind: local-file
status: CANONICAL
source: data/vnindex_5state_dt_4gate.csv
group: market-state
aka: chuỗi DT4 local (base + DT 4-gate, KHÔNG macro)
name_alike_trap: tav2_archive.vnindex_5state_dt_4gate (bản BQ ĐÓNG BĂNG 2026-06-02)
writer: build_dt_4gate.py, step [8] daily 18:30 (non-fatal, advisory-only)
---

# data/vnindex_5state_dt_4gate.csv

**Status: CANONICAL (DT4 local)**

## Là gì
Chuỗi DT4 (base + DT 4-gate, KHÔNG macro) — research/ablation.

## Ai ghi / cadence
`build_dt_4gate.py`, step [8] daily 18:30 (non-fatal, advisory-only).

## Bẫy
**Cặp name-alike với bảng BQ `vnindex_5state_dt_4gate`** — bản BQ ĐÓNG BĂNG từ 2026-06-02, dời
sang `tav2_archive` ngày 2026-11-26; chỉ bản CSV local này còn sống. `bq_cache/` còn giữ bản mirror
cũ đóng băng → đọc DT4 qua cache = đọc dữ liệu chết.
