---
kind: incident
date: 2026-07-06
topic: macro-health-false-sev1-cache-sync-dead
title: >-
  2026-07-06 (đêm) — macro_health false-SEV1: mảnh ghép cuối — cache sync chết âm thầm 2 bug
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 (đêm) — macro_health false-SEV1: mảnh ghép cuối — cache sync chết âm thầm 2 bug

**Follow-up của entry "false SEV1 in the DT5G macro health-check" cùng ngày.** User hỏi lại vì
macro_health vẫn FAILED buổi tối dù Winston đã fix BQ upstream (đúng — BQ thật fresh tới 07-06,
verify trực tiếp). Nguyên nhân phần `bq_ticker_vnindex as_of=2026-06-25` (chiều nay "không tái
hiện được") giờ đã rõ hoàn toàn:

1. **`sync_bq_cache.py` delta bảng `ticker` crash MỖI ĐÊM từ ~06-26**: đọc year-parquet cũ
   (ghi bởi version trước mang dtype `dbdate` của Google) bằng `pd.read_parquet` không có
   `db_dtypes` import → `TypeError: data type 'dbdate' not understood` → cache `ticker` đóng
   băng ở 06-26. Fix: đếm dòng qua `pyarrow.parquet.read_metadata` (không đụng dtype, rẻ hơn)
   + import `db_dtypes` phòng thủ.
2. **Delta các bảng `vnindex_5state*` CHƯA BAO GIỜ chạy được**: SQL gốc của nhóm bảng này
   không có WHERE, code delta nối cứng `" AND t.time > ..."` → SQL sai cú pháp → bq CLI fail
   với stderr TRỐNG (không ai thấy) → các bảng này chỉ fresh vào lần full-download hiếm hoi.
   Fix: joiner `WHERE`/`AND` tùy SQL gốc.
3. Chuỗi nhân quả đầy đủ của false-SEV1: cache thối (bug 1+2) → `papertrade_daily.sh` 15:30
   chạy trong env cache init THÀNH CÔNG → `macro_healthcheck.py` đọc VNINDEX từ cache → tưởng
   stale 7 ngày → FAILED/SEV1 → `get_gated_state()` rơi về DT4_only. Môi trường test tay của
   Mike cache init FAIL → fallback BQ thật → số đúng → "không tái hiện" (chiều nay).
4. Xung đột phụ phát hiện khi resync: chạy sync đúng lúc `daily_refresh_v34b_linux.sh` 23:15
   đang `bq load --replace` chính các bảng vnindex → bq lỗi tạm thời. Không phải bug, chỉ cần
   tránh giờ đó (cron sync 23:45 vốn đã sau refresh — đúng thiết kế).

**Kết quả cuối (sau fix + resync + full re-download ticker_prune):** `Cache verified OK` toàn
bộ 13 bảng, max=2026-07-06; `macro_health.json` **HEALTHY / DT5G_macro** (refresh 23:15 tự
sinh lại bằng checker đã vá). Commit `b26091a` (WorkingClaude). ticker_prune lệch ~5k dòng
ngoài 2026 (Winston backfill/mã mới có lịch sử dài — delta theo năm không bắt được) → full
re-download sạch.

**Bài học:** hai lớp "âm thầm" chồng nhau — checker đọc nguồn sai (entry trước) + nguồn đó
lại được nuôi bởi pipeline sync tự chết mỗi đêm không ai hay (lỗi nuốt stderr, cron log không
ai đọc). Giá trị của `--verify` đã có sẵn trong sync script (nó ĐÃ báo FAIL từ 07-03) nhưng
không ai/không cơ chế nào đọc kết quả verify đó → cân nhắc nối verify-fail vào notify.sh
(mục Open bên dưới).

**Addendum 2026-07-07 (Winston, job Winston_20260707_072729) — hệ quả downstream cuối cùng:**
cùng cache thối này còn làm **các paper-sim trong `papertrade_daily.sh` kẹt ở 06-25** (Taylor
phát hiện sáng 07-07: pt_v22 logs stale). Cơ chế: `refresh_lagged_caches.py` đọc cache thấy
"already current" → `lagged_pos_ov.pkl` đóng băng → `detect_end_date()` (pt_dates.py) trả
END_DATE cũ; đồng thời price panel từ cache `ticker` dừng 06-25 → summary/CSV pt_v22 cắt ở
06-25. Tính chập chờn (07-01→07-03 lại "đúng") = những đêm cache init FAIL → script fallback
BQ thật → data tươi; đêm cache init OK → dùng cache thối. KHÔNG có bug riêng trong pt_v22 —
thuần hệ quả của bug sync đã vá (`b26091a`). Xử lý 07-07: rerun `refresh_lagged_caches.py` +
`pt_v22_dt5g.py` với cache đã lành → toàn bộ artifact (pt_v22/pt_v4/pt_v11/pt_v12) fresh tới
2026-07-06, period header = summary = 07-06. Cron 15:30 cùng ngày chạy lại toàn chuỗi như
verify tự nhiên cuối.
