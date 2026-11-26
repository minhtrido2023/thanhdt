---
kind: bigquery-table
status: ARCHIVE
source: tav2_archive.vnindex_5state_* (15 bảng, dời 2026-11-26) / tav2_bq.vnindex_5state_*_predeploy_*
group: market-state
lineage: ew_v1 → dual_v3 → v3.1 → v3.4b → DT5G
see_also: vnindex_5state_registry.md
---

# tav2_archive.vnindex_5state_* và phần archive/staging còn lại trong tav2_bq

**Status: ARCHIVE**

## Là gì
Họ bảng archive/staging của lineage 5-state (ew_v1→dual_v3→v3.1→v3.4b→DT5G).

## Ai ghi / cadence
Đóng băng tại thời điểm archive tương ứng.

## Dời sang `tav2_archive` (2026-11-26, user duyệt)
15 bảng đóng băng, tên giữ nguyên, bỏ tiền tố `vnindex_5state_`: `dt4_macro`, `tam_quan_stress`,
`tam_quan_v31`, `tam_quan_v31_clean`, `tam_quan_v33b_clean`, `archive_pe3c_raw`, `archive_v2g_old`,
`archive_pre_dt5g_20260602`, `archive_tinh_te_20260525_220329`, `archive_tinh_te_20260525_220509`,
`archive_tinh_te_20260602_094352`, `archive_tinh_te_20260602_213635`,
`v34bclean_archive_predeploy_20260616_010223`, `staging`, `dt_4gate`.
- Khôi phục: `bq cp tav2_archive.<tên> tav2_bq.<tên>`.
- Script research cũ còn trỏ `tav2_bq.<tên>` sẽ báo không tìm thấy bảng khi chạy lại.

`staging` và `dt_4gate` dời đợt sau cùng ngày; script cũ trỏ tới (`ngu_hanh_shadow_tracker.py`,
`deploy_ngu_hanh.py`, nhóm `sim_dt4g_*`…) không nằm trong lịch chạy.

**Còn ở `tav2_bq`:** `taylor_exp_dt5g_recompute_2008_2026_20260825`
(backtest 2008 trong `results_registry.md` đọc), `*_vintage_20260730` (mốc đối chiếu).

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
