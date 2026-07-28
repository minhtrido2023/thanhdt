---
kind: bigquery-table
status: ARCHIVE
source: tav2_bq.vnindex_5state_staging / _archive_* / _v2g_* / _tam_quan_v31/v33b_clean / _baseline_*
group: market-state
lineage: ew_v1 → dual_v3 → v3.1 → v3.4b → DT5G
see_also: vnindex_5state_registry.md
---

# tav2_bq.vnindex_5state_staging / _archive_* / _v2g_* / _tam_quan_v31/v33b_clean / _baseline_*

**Status: ARCHIVE**

## Là gì
Họ bảng archive/staging của lineage 5-state (ew_v1→dual_v3→v3.1→v3.4b→DT5G).

## Ai ghi / cadence
Đóng băng tại thời điểm archive tương ứng.

## Bẫy
Chỉ để tra lịch sử/forensic (vd `_archive_predeploy_20260711_*` từ vụ EW-leg). KHÔNG dùng làm state
cho backtest mới — xem `vnindex_5state_registry.md` cho lineage đầy đủ.
