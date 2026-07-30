---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.vnindex_5state_dt5g_live
group: market-state
aka: DT5G production
writer: macro_state_live.py → publish_gated_state.py → state_publish_immutable.py (daily_refresh_v34b_linux.sh, cron 18:30 ICT)
write_contract: APPEND-ONLY + recompute đuôi 25 phiên (BẤT BIẾN, từ 2026-07-30)
columns: time, state, state_raw, asof_date
---

# tav2_bq.vnindex_5state_dt5g_live

**Status: CANONICAL**

## Là gì
Trạng thái thị trường PRODUCTION (DT-gate + macro gate, 49 transitions).

## Ai ghi / cadence
`macro_state_live.py` → `deploy_golive_dt5g_v4/publish_gated_state.py` →
`state_publish_immutable.py`, trong `daily_refresh_v34b_linux.sh` step [12], cron 18:30 ICT
(dời từ 23:15, 2026-07-10).

## HỢP ĐỒNG GHI — BẤT BIẾN (từ 2026-07-30, job `Taylor_20260730_013951`)
**State của một phiên ĐÃ CÔNG BỐ là SỰ KIỆN ĐÃ XẢY RA, không phải ước lượng được cập nhật.**
Publisher chỉ được: (a) append phiên mới; (b) recompute đuôi **25 phiên giao dịch** chưa chốt;
(c) **KHÔNG BAO GIỜ** ghi đè phiên đã chốt (`time <= cutoff`, cutoff = phiên thứ 26 từ cuối).
Bảo đảm là CẤU TRÚC: MERGE có cả 3 nhánh bị chặn bởi `time > cutoff`, + checksum MD5 vùng đã
chốt so trước/sau mỗi lần ghi (lệch ⇒ abort + alert). Trước 2026-07-30 là `bq load --replace`
(đè toàn bộ mỗi đêm) — nguyên nhân 101 phiên lịch sử bị viết lại im lặng ngày 2026-07-29.

- **Cột `asof_date`** = ngày GIÁ TRỊ của dòng đó được ghi/đổi lần cuối (không phải ngày chạm gần
  nhất). Dòng đã chốt giữ `asof_date` vĩnh viễn. Toàn bộ lịch sử hiện có được backfill
  `asof_date = 2026-07-30` = baseline đóng băng tại thời điểm triển khai.
- **Muốn bản tính mới của lịch sử** (sau backfill/restate upstream): chụp **vintage** riêng
  (`snapshot_vintage()` → `vnindex_5state_dt5g_live_vintage_<YYYYMMDD>`), **đừng đè bảng công bố**.
- Telemetry `n_sealed_diff` (số phiên đã chốt mà bản tính mới KHÁC bản công bố — tức số phiên
  `--replace` cũ SẼ âm thầm viết lại) được ĐẾM + alert, KHÔNG áp dụng:
  `data/immutable_publish_history.jsonl`.

## Bẫy
Đây là nguồn ĐÚNG duy nhất cho production state. Hai điểm cần biết:
1. **Vùng đuôi 25 phiên VẪN đổi được** (đúng thiết kế — state chưa chốt vì DT-gate cần `enC/enX`
   = 25 phiên mới commit). Đừng coi giá trị của 25 phiên gần nhất là bất biến.
2. Cột `asof_date` thêm 2026-07-30 ⇒ `SELECT *` giờ trả 4 cột (`sync_bq_cache.py` cache cả 4).
   Consumer nên nêu tên cột tường minh.
