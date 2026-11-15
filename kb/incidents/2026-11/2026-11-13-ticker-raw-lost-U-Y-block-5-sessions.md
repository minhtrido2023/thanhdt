# 2026-11-13 — `tav2_bq.ticker` mất dải mã U*..Y* + VNINDEX 5 phiên (09-13/11) ⇒ DT5G publish abort, không có plan 16/11

status: mitigated (dữ liệu khôi phục 14/11 09:03 ICT); lỗ hổng (3) ĐÃ ĐÓNG ở code, (1) giảm nhẹ, (2) còn mở — daily_refresh wire CHỜ MERGE sau 21:30 ICT 15/11

**Nguồn:** Winston finding `ticker-raw-mat-ma-U-Y-investigation-20261114` (job `Winston_20261114_015908`, khôi phục `Winston_20261114_020203`).

**Cái gì hỏng:** mỗi phiên 09-13/11 mất khối liên tiếp U*..VS* (VNINDEX, VNM, VCB, VIB, VPB…) + W-Y riêng 13/11 — 502 cặp
(ticker,time) ≈ đúng 1 lô `delete_chunk_size=500` của ETL kaffa_v2 (DELETE theo key rồi APPEND theo lô). Giả thuyết (CHƯA xác
nhận, thiếu quyền `jobs.listAll`): 1 lô DELETE commit mà APPEND lỗi. Tái diễn họ sự cố 19/10 (EIN..PHN).

**Ảnh hưởng:** refresh DT5G 18:30 13/11 ABORT đúng ở immutable publish ⇒ `golive_state_today.json` as_of=12/11;
`bq_freshness_check` 19:00 FAIL ⇒ không dispatch DollarBill ⇒ không có `plan_*_2026-11-16.json`, không có
`golive_v23_recommendations_2026-11-13.csv` ⇒ `hit_details_daily` 13/11 bỏ qua (đúng thiết kế, không chạy trên dữ liệu cũ).
NAV 13/11 không ảnh hưởng (nguồn DNSE). Cache local `bq_cache/ticker/2026.parquet` 23:45 13/11 chép bản thủng.

**Khắc phục:** INSERT 503 dòng từ `ticker_1m` (đối chiếu 4051 dòng, lệch 0); cache heal + DT5G republish 14/11 09:56
(as_of 2026-11-13, state 3, `bq_publish_ok=True` — weekly audit 14/11 đọc lại file thật). Plan 16/11 do vòng CN 19:00 dựng.

**CÒN MỞ (chưa cứng hoá):** (1) freshness của `get_gated_state` so MAX(VNINDEX) trên chính raw ticker ⇒ raw thủng thì gate mù;
(2) `fa_ratings_ticker_gate` chỉ đọc `last_t` 30 ngày ⇒ không bắt được thủng 5 phiên; (3) đề xuất gate so đếm raw `ticker` vs
`ticker_1m` theo phiên — chưa làm. RCA ETL thuộc team kaffa_v2 (bq_admin). Dòng trùng VNH 13/11 cần dedupe.

**ĐÃ CỨNG HOÁ (job `Winston_20261115_123354`, arch-review CONFIRMED vòng 2):** `bin/ticker_integrity_precheck.py`
(mike commit 0bbd4f9e7+) đối chiếu `ticker` vs `ticker_1m` 5 phiên, read-only (~186KB/lần): FAIL nếu VNINDEX
vắng ở bất kỳ phiên nào ticker_1m có / MAX VNINDEX < MAX ticker, hoặc >2 mã thanh khoản (ticker_1m ∩ ticker_prune)
vắng trong ticker, hoặc tổng dòng <90% (lưới thảm hoạ). Wire = bước `[0b]` trong `daily_refresh_v34b_linux.sh`
(nhánh `fix/ticker-integrity-precheck-20261115`, worktree `wt-ticker-integrity-1115`): retry 3×10', hết ⇒ notify+thread+bus `error`+die;
bq/precheck lỗi ⇒ fail-open + bus `status`. Đóng (3); giảm nhẹ (1) (raw thủng bị bắt ngay đầu chain thay vì ở publish guard); (2) `fa_ratings_ticker_gate` CHƯA đổi.
**Bài học đo thật:** ngưỡng 97% trên tổng dòng (đề xuất gốc) báo oan 6/19 phiên tự nhiên (95,08–96,97%, đuôi kém thanh khoản
34-43 mã) — đổi sang universe thanh khoản (0 mã prune vắng trong 10-20..11-13). Luật VNINDEX-theo-phiên thêm vì (a)+(b) để lọt lỗ phiên giữa.
Selfcheck 46 case + 9 mutant, PASS dưới `env -u TZ`/Pacific/Kiritimati.
