# DT5G production table có WRITER THỨ HAI ngoài luồng — truy ra nguồn (2026-07-29)

Job: `Winston_20260729_110410` · Ưu tiên CAO · Bảng PRODUCTION `tav2_bq.vnindex_5state_dt5g_live`

## TL;DR
Đã **truy ra chính xác nguồn**: pipeline **kaffa_v2 (team dữ liệu — user `hainguyen`, chạy trên CÙNG host này
tại `/workspace/kaffa_v2`)** có 1 Celery task tự tính DT5G **bằng implementation RIÊNG** và **ghi thẳng** vào
`tav2_bq.vnindex_5state_dt5g_live` mỗi lần chạy EOD pipeline (~17:12 ICT hôm nay).

- Script: `/workspace/kaffa_v2/worker/tasks/market_state_tasks.py`
  → task `tasks.market_state_tasks.update_market_regime_state`
  → hàm `_sync_market_state_to_bigquery()` (DELETE `time >= min_time` + APPEND 5 phiên gần nhất).
- Kích hoạt: Celery `pipeline` (EOD) → `update_market_state` → `update_market_regime_state`
  (`worker/tasks/schedule_tasks.py:614`), chạy qua `cron/run.py` của họ, KHÔNG qua crontab của `trido`.
- Bắt đầu từ: commit `c794dd1` **2026-06-08**, tác giả `hainguyen-namiq`
  — *"feat(market_state): auto-sync DT5G state to BigQuery vnindex_5state_dt5g_live"*.
- Lý do họ làm: `tasks/plan.md` ghi rõ *"the table is manually maintained and is stale (latest 2026-06-05 vs
  today 2026-06-08)"* → họ tưởng bảng **không có owner tự động** nên wire auto-sync. **Họ không biết** phía
  `trido` có publisher production `deploy_golive_dt5g_v4/publish_gated_state.py`.

## Bằng chứng khớp thời điểm
| | |
|---|---|
| `dt5g_live.lastModifiedTime` | **2026-07-29 17:12:05.197 ICT** |
| BQ job 17:12:01 (QUERY, 75.216 B xử lý ≈ đúng `numBytes` bảng = 75.240) | = câu `DELETE time >= @min_time` |
| BQ job 17:12:04 → end **17:12:05.263** (LOAD, không có query-stats) | = `append_dataframe` 5 dòng |
| Artifact GCS của kaffa `.../market_state/vnindex_5state_dt5g.csv` mtime | **17:12:00.67 ICT** (ngay trước 2 job) |

Cả 2 job hiện **`<REDACTED>`** trong `bq ls -j --all_jobs` (⇒ principal KHÁC `dtienthanh@gmail.com`;
tài khoản này không có `bigquery.jobs.listAll` nên `INFORMATION_SCHEMA.JOBS_BY_PROJECT` bị từ chối).
Nguồn đã loại trừ: crontab `trido` (không dòng nào), `/etc/cron.d`, systemd timers, tiến trình nền của `trido`.

## Nội dung ghi có SAI không? → **KHÔNG (hôm nay)**
Diff toàn bộ bảng BQ hiện tại vs bản publish chính thức của ta (`data/vnindex_5state_dt5g_live.csv`, ghi
2026-07-28 19:00):
- 3.134 dòng trùng ngày: **0 lệch** `state`, **0 lệch** `state_raw`.
- Chỉ thêm **1 dòng mới `2026-07-29 state=3 state_raw=3`** (3 = **NEUTRAL**, 70% — mapping
  `macro_state_live.py:42` `NEUTRAL,CRISIS,BEAR = 3,1,2`; kaffa dùng cùng mapping 1..5).
- Giá trị này nhiều khả năng **trùng** với bản 19:00 tối nay: base `v34b_clean` mới rời NEUTRAL từ 07-20
  (7 phiên ≤2 tính tới 07-28, trong đó đổi ứng viên 2→1 ngày 07-24), chưa đủ ngưỡng commit của DT 4-gate
  ⇒ DT5G vẫn giữ NEUTRAL. **Phải verify lại sau 19:03.**

**NHƯNG hai engine KHÔNG bit-identical.** So kaffa artifact (`state_id`) vs series chính thức của ta trên
3.134 phiên chung: **27 phiên lệch `state` (0,86%)** + 1 phiên lệch riêng `state_raw` —
2017-12-05→12-25 (15 phiên), 2018-12-07, 2019-12-10, 2020-01-14, 2020-12-28, 2021-08-23, 2022-06-14,
2022-11-01, 2023-03-17(raw), 2024-01-24, 2025-05-19, 2025-09-17→19.
⇒ Trùng khớp hôm nay là **may**, không có gì bảo đảm về cấu trúc.

## RỦI RO THẬT (đây mới là phần nghiêm trọng)
1. **Gate fail-safe của ta bị vô hiệu hoá.** `mike/bin/bq_freshness_check.sh:207` kiểm tra DT5G bằng
   `MAX(time)` với `MAX_STATE_LAG=0`, và chạy **TRƯỚC** bước publish (`:395 [pipeline-1]`). Kaffa đã đẩy
   `MAX(time)=hôm nay` lúc 17:12 ⇒ **gate luôn PASS dù publisher của ta chết hoàn toàn.**
2. Giả định load-bearing trong code của ta đã **SAI**: `daily_refresh_v34b_linux.sh:59` viết
   *"bq_freshness_check.sh's own gate will BLOCK DollarBill downstream since vnindex_5state_dt5g_live won't
   advance today"* — nay bảng **vẫn advance** nhờ writer ngoài, kể cả khi chuỗi của ta abort vì
   `ticker_prune` thiếu/stale.
3. **Split-brain**: 3 lượt ghi/ngày lên cùng 1 bảng production — kaffa 17:12 (delete+append 5 phiên),
   ta 18:5x (`daily_refresh` step [12]) và 19:0x (`bq_freshness` pipeline-1, `bq load --replace` toàn bảng).
   Cửa sổ **17:12→18:5x** bảng mang giá trị của engine kaffa.
4. Không có `_check_lastmod` (writer-alive) cho `dt5g_live` như các bảng khác ⇒ không phát hiện được.

**Ảnh hưởng tới lệnh đang chờ hôm nay: KHÔNG.** Consumer thật (`golive_recommend`, `pt_v4_dt5g`,
`dna_report`, `recommend_tomorrow`, plan T+1) đều chạy **sau 19:00**; trong cửa sổ 17:12–18:12 chỉ có đúng
các query audit của chính Winston đọc bảng này. Giá trị lại trùng khớp 100%.

## ĐỀ XUẤT (chưa làm gì — chờ Mike/user quyết)
1. **[Cần user/Mike + team dữ liệu]** Đề nghị hainguyen trỏ writer của họ sang bảng riêng —
   **không cần sửa code**, chỉ set env `MARKET_STATE_BQ_TABLE=vnindex_5state_dt5g_kaffa`
   (`market_state_tasks.py:31` đã env-backed). Họ giữ nguyên mirror cho report/webui, ta lấy lại quyền
   sở hữu độc nhất bảng production. **Không tự tắt** — đây là hệ thống của team khác.
2. **[Winston, cần duyệt]** Vá gate cho khỏi bị che: bổ sung vào `bq_freshness_check.sh` một điều kiện
   chứng minh **publisher CỦA TA** đã chạy — `deploy_golive_dt5g_v4/golive_state_today.json` có
   `as_of == hôm nay` (+ mtime `data/vnindex_5state_dt5g_live.csv`). 2 file này chỉ do
   `publish_gated_state.py` ghi ⇒ không giả mạo được bởi writer ngoài.
3. **[Winston, cần duyệt]** Thêm giám sát writer lạ: cảnh báo khi `lastModifiedTime` của `dt5g_live` rơi
   **ngoài** cửa sổ 18:30–19:05 ICT (bắt được cả trường hợp tái diễn lẫn nguồn mới).
4. Ghi `dt5g_live` vào `kb/data_registry/` kèm cảnh báo **"2 writer"** cho tới khi mục 1 xong.

## Đã loại trừ
crontab user `trido` · `/etc/cron.d` + `/etc/crontab` · systemd timers · tiến trình nền/tmux/nohup của
`trido` · script archive `papertrade_daily.sh` bản cũ · `deploy_5state/run_daily.sh` (ghi
`vnindex_5state`, không phải `dt5g_live`, và path `/home/USER/...` chưa từng deploy trên host này).
