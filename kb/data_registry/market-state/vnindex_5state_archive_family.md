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

## `_archive_predeploy_<TS>` — 2 họ, đều keep-newest-5
`daily_refresh_v34b_linux.sh` step [9] chụp NGAY TRƯỚC khi ghi đè:
- `vnindex_5state_archive_predeploy_<TS>` — base v3.4b (có từ lâu)
- `vnindex_5state_dt5g_live_archive_predeploy_<TS>` — **PRODUCTION dt5g_live, thêm 2026-07-29**
  (job `Winston_20260729_155830`). Trước đó dt5g_live KHÔNG có snapshot dated nào ⇒ khi lịch sử
  bị viết lại thì không còn gì để so (BQ time-travel vô dụng: upstream `ticker`/`ticker_prune` là
  DROP+CREATE mỗi sáng). Đây là input của restate guard step `[12b]`.

Cả 2 họ đều prune còn 5 bản ⇒ **chỉ lùi được ~5 phiên**. Muốn pin lâu hơn: `tav2_pin`
(`bq_monthly_pin.sh`, mốc tháng, không expiry).
