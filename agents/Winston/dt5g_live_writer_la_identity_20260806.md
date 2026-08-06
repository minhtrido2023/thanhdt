# DT5G writer lạ 16:21–16:26 ICT (08-03/04/05) — DANH TÍNH: kaffa_v2, KHÔNG phải writer mới

Job: `Winston_20260806_012753` (dispatch từ Wags) · Bảng `tav2_bq.vnindex_5state_dt5g_live`
Chỉ ĐIỀU TRA — không sửa bảng, không đổi quyền, không tắt job nào.

## Kết luận
Writer 16:21–16:26 ICT là **ĐÚNG writer thứ hai đã truy ra ngày 2026-07-29**: pipeline **kaffa_v2**
(team dữ liệu, user OS `hainguyen`, **cùng host này**, `/workspace/kaffa_v2`), Celery task
`tasks.market_state_tasks.update_market_regime_state`. **KHÔNG phải writer mới, KHÔNG phải writer
ngoài fleet-ngoài-host.**

Cái ĐỔI không phải danh tính mà là **GIỜ**: task này là **bước CUỐI** của pipeline EOD, nên giờ ghi
= **giờ pipeline KẾT THÚC**, trôi theo thời lượng chạy — không phải một mốc cố định. Cửa sổ
`KAFFA_WINDOW = 16:30–18:00` trong `mike/bin/dt5g_writer_watch.py` được hiệu chuẩn từ 1 lần chạy
duy nhất (07-29 kết thúc 17:12); 3 ngày qua pipeline chạy nhanh hơn (~51–56 phút thay vì ~1h42)
nên kết thúc SỚM hơn cận dưới cửa sổ vài phút ⇒ `classify()` trả `OTHER` ⇒ WARN.

## Bằng chứng khớp thời điểm (3/3 ngày, sai số 2–7 giây)
Nguồn A = `/workspace/kaffa_v2/cron/cron_update.log` (log JSON, timestamp **UTC**, `Z`): dòng
`Clearing all cache again` = ngay sau khi `cron/run.py` (task `tasks.schedule_tasks.pipeline`) trả về.
Nguồn B = `data/dt5g_writer_watch.csv` cột `lastmod` (đọc `lastModifiedTime` của bảng, ICT tường minh).

| Ngày | Pipeline kaffa BẮT ĐẦU | Pipeline kaffa KẾT THÚC (A) | `dt5g_live.lastModifiedTime` (B) | Lệch |
|---|---|---|---|---|
| 2026-08-03 | 08:30:02 UTC = 15:30:02 ICT | 09:21:07 UTC = **16:21:07 ICT** | **16:21:05 ICT** | 2 s |
| 2026-08-04 | 08:30:02 UTC = 15:30:02 ICT | 09:26:09 UTC = **16:26:09 ICT** | **16:26:02 ICT** | 7 s |
| 2026-08-05 | 08:30:01 UTC = 15:30:01 ICT | 09:25:31 UTC = **16:25:31 ICT** | **16:25:27 ICT** | 4 s |

Ghi bảng luôn xảy ra **vài giây TRƯỚC** khi pipeline trả về ⇒ đúng vị trí "task cuối cùng".

Bằng chứng bổ sung (08-05, độc lập với log):
- Artifact của kaffa `/workspace/kaffa_v2/worker/gcloud_storage/preprocess/market_state/vnindex_5state_dt5g.csv`
  mtime = **2026-08-05 16:25:21.890 ICT** — 6 giây trước `lastModifiedTime` 16:25:27 ICT.
  (Đây chính là file mà `_sync_market_state_to_bigquery()` sinh ra rồi đẩy lên BQ.)
- 2026-08-03: `worker/logs/core_utils.bigquery.log.2026-07-31_09` cho thấy kaffa đang ghi
  `lithe-record-440915-m9.tav2_bq.ticker_prune` liên tục **09:25:21→09:26:10 UTC (16:25–16:26 ICT)**
  — pipeline kaffa chứng minh đang chạy ghi `tav2_bq` đúng khung giờ đó.
- Code vẫn trỏ bảng production: `worker/tasks/market_state_tasks.py:31`
  `MARKET_STATE_BQ_TABLE = os.environ.get("MARKET_STATE_BQ_TABLE", "vnindex_5state_dt5g_live")`
  ⇒ **đề xuất số 1 của báo cáo 07-29 (trỏ sang bảng riêng) CHƯA được thực hiện.**
- Tiến trình Celery đang chạy dưới user `hainguyen` trên host này (`ps -eo user,pid,lstart,cmd`):
  `celery -A celery_app worker -Q orchestrator|vci|celery`, `celery beat`, tmux session `kaffa_v2`.

## Vì sao INFORMATION_SCHEMA không thấy (nêu rõ thiếu quyền gì)
- `INFORMATION_SCHEMA.JOBS_BY_PROJECT` (region-asia-southeast1): **Access Denied** — tài khoản
  `dtienthanh@gmail.com` thiếu **`bigquery.jobs.listAll`** ở cấp project. Không truy được `user_email`
  của principal khác bằng đường này.
- `INFORMATION_SCHEMA.JOBS_BY_USER` chạy được nhưng **theo định nghĩa chỉ trả job của chính
  `dtienthanh@gmail.com`**. Kết quả 5 ngày qua, destination = `vnindex_5state_dt5g_live`: đúng
  **2 job MERGE/ngày** lúc **11:37 UTC (18:37 ICT)** và **12:01 UTC (19:01 ICT)** = `daily_refresh_v34b_linux.sh`
  và `publish_gated_state.py` — **không có job nào lúc 09:2x UTC**. Quét toàn bộ job 08:30–11:00 UTC
  ngày 08-03: 6 job (LOAD `custom30_8l`/`custom30v_8l`, 4 SELECT ẩn danh), **không cái nào chạm bảng này**.
  ⇒ Writer 16:2x là **principal KHÁC** — khớp đúng kết luận 07-29 (`bq ls -j --all_jobs` hiện `<REDACTED>`).

Danh tính do đó xác lập bằng **bằng chứng phía host** (log + mtime artifact + code + process owner),
không phải bằng INFORMATION_SCHEMA. Không suy đoán `user_email` cụ thể của service account kaffa vì
không có quyền đọc.

## Nội dung ghi có sai không? → KHÔNG, cả 3 ngày
Theo `data/dt5g_writer_watch.csv` (cột đo tại mẫu `pre-publish-1830` và `bq-freshness-19h`):
`n_state_diff = 0`, `n_raw_diff = 0`, `n_dup_time = 0`, `n_null_sealed = 0` cho cả 08-03/04/05.
Cả 2 engine đều cho `state = 3` (NEUTRAL). Mỗi ngày kaffa thêm đúng 1 dòng mới trước publish của ta
(`n_rows` = `n_common` + 1), rồi 19:0x publisher của ta ghi đè → khớp hoàn toàn.

Lưu ý phụ (không phải do writer lạ): 9 dòng `asof_date IS NULL` = 2026-07-24, 07-27→07-31, 08-03→08-05.
CSV publish của ta (`data/vnindex_5state_dt5g_live.csv`) **không có cột `asof_date`** (header chỉ
`time,state,state_raw`), nên MERGE của ta không điền cột này cho dòng mới. Đây là chuyện của
publisher CỦA TA, không phải dấu vết writer ngoài — nêu ra để không bị quy nhầm.

## Ba rủi ro của báo cáo 07-29 vẫn CÒN NGUYÊN
1. Kaffa vẫn ghi thẳng bảng production (env `MARKET_STATE_BQ_TABLE` chưa được trỏ đi).
2. `MAX(time)` của bảng vẫn được kaffa đẩy lên "hôm nay" lúc 16:2x ⇒ gate `MAX_STATE_LAG=0` trong
   `bq_freshness_check.sh` vẫn có thể PASS dù publisher của ta chết.
3. Split-brain window 16:2x → 18:37 vẫn tồn tại (rộng hơn trước vì kaffa chạy sớm hơn ~45 phút).

## Đề xuất (CHƯA làm gì — cần Mike/user quyết)
1. **Vẫn là việc tồn từ 07-29**: đề nghị team dữ liệu set `MARKET_STATE_BQ_TABLE=vnindex_5state_dt5g_kaffa`.
   Đây là nút thắt thật; mọi thứ khác chỉ là giảm nhiễu.
2. **Sửa `classify()` cho đúng bản chất** (Winston làm được, cần duyệt): cửa sổ cố định là mô hình SAI
   cho một writer mà giờ ghi = giờ pipeline kết thúc. Nới `KAFFA_WINDOW` xuống `15:30–18:00` (chặn dưới =
   giờ pipeline BẮT ĐẦU, quan sát được ổn định 08:30:0x UTC cả 3 ngày) sẽ hết WARN giả mà không mất
   khả năng bắt writer thật sự lạ. Cảnh báo giá trị (`state_diff`/`dup_time`/`null_sealed`) giữ nguyên —
   đó mới là lớp phát hiện có ý nghĩa.
3. Ghi `dt5g_live` vào `kb/data_registry/` kèm cảnh báo "2 writer" (mục 4 của 07-29, chưa xong).

## Cách tái lập
```bash
grep -an "Cron is called." /workspace/kaffa_v2/cron/cron_update.log | tail -6   # lấy số dòng mốc
sed -n "<L>,<L+20>p" /workspace/kaffa_v2/cron/cron_update.log \
  | grep -aoE '"timestamp": "2026-[0-9-]+T[0-9:]+|Updating indicator|Clearing all cache again'
tail -12 /home/trido/thanhdt/WorkingClaude/data/dt5g_writer_watch.csv
```
