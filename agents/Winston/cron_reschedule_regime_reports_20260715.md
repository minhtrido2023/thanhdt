# Đề xuất đổi giờ 3 cron report có phần "tình trạng thị trường" (job Winston_20260715_054242)

**Trạng thái: CHỜ XÁC NHẬN — chưa cài.** (Không gấp thời gian → theo ranh giới bình thường.)

## 1. Verify buffer thật sau 19:00 (yêu cầu chính của dispatch)

Đo trên log thật `mike/logs/bq_freshness.log` + mtime artifact, KHÔNG tin comment:

| Bằng chứng | Giá trị |
|---|---|
| `publish_gated_state` (pipeline-1) ghi xong `golive_state_today.json` (07-14) | **19:01:29 ICT** |
| `data/vnindex_5state_dt5g_live.csv` cùng lần chạy | 19:01:18 ICT |
| Toàn pipeline `EOD PIPELINE DONE` — 3 lần chạy ở khung 19:00 (07-10, 07-13, 07-14) | 19:00 / 19:01 / **19:02** |
| Nội dung publish 07-14 | `today: as_of=2026-07-14 state=3 source=DT5G_macro` → state HÔM NAY, đúng |

**Kết luận: 19:10 KHÔNG quá sớm.** Publish (bước sinh regime, chạy đầu tiên trong pipeline) xong
~90 giây sau 19:00 → 19:10 cho buffer **~8,5 phút ≈ 5-6× thời gian quan sát**. n=3 là mỏng, nhưng
biên vẫn rộng kể cả khi publish chậm gấp 3.

**Không cần lùi giờ an toàn hơn** — vì `bq_freshness_check.sh` **không có retry**: nếu 19:00 mà dữ
liệu chưa fresh, script `exit 1` và bỏ hẳn pipeline (`MAX_STATE_LAG=0`). Nên chờ lâu hơn 19:10
không mua thêm được sự an toàn nào; failure mode duy nhất là "không có publish nào cả", và giờ nào
sau đó cũng như nhau. Giữ đúng 3 giờ Mike đề xuất.

## 2. Bốn câu hỏi bắt buộc (§11 coding_guidelines)

| | eod_trading_report.sh | pt_8l_daily.sh | telegram_run_daily.sh |
|---|---|---|---|
| **Đọc gì + vintage** | `state.json` fill (T, có từ ~14:50) + `daily_nav_snapshot.py`; phần thị trường qua `dna_report.build_dt_gate_line()` → **`dt5g_live` BQ live (cần T)** | `dt5g_live` **BQ live** (rating_8l.py:750, cheap_pb_floor.py:65) + `ticker`/`ticker_prune` (ingest ~17:30) | `dt5g_live` **BQ live** (telegram_recommend.py:104) + `golive_state_today.json` cho provenance |
| **Nguồn tươi lúc nào (đo thật)** | 19:01:29 | 19:01:29 | 19:01:29 |
| **Cần T hay T-1** | **T** (đây chính là bug user báo) | **T** | **T** |
| **Ai tiêu thụ + deadline** | user (Discord Trading report) — không có deadline cứng buổi tối | user (Telegram 8L alerts) | user (Telegram BA-system) |

## 3. Crontab diff đề xuất (giờ hệ thống = UTC, ICT = UTC+7)

```diff
--- crontab (hiện tại)
+++ crontab (đề xuất)
@@ dòng 10 @@
 # 8L ranking + DNA cards + surprise/PB-floor Telegram alerts (pt_8l_daily.bat)
-45 10 * * 1-5 /home/trido/thanhdt/WorkingClaude/pt_8l_daily.sh           # 17:45 ICT
+20 12 * * 1-5 /home/trido/thanhdt/WorkingClaude/pt_8l_daily.sh           # 19:20 ICT (doi tu 17:45, 2026-07-15 — M3 audit Winston_20260712_142100: doc dt5g_live, chay truoc 18:30 refresh = luon regime HOM QUA; nay sau publish 19:01)
@@ dòng 12 @@
 # 18:00 BA-system Telegram report (telegram_run_daily.bat -> telegram_recommend.py)
-0  11 * * 1-5 /home/trido/thanhdt/WorkingClaude/telegram_run_daily.sh    # 18:00 ICT
+35 12 * * 1-5 /home/trido/thanhdt/WorkingClaude/telegram_run_daily.sh    # 19:35 ICT (doi tu 18:00, 2026-07-15 — cung M3; giu thu tu sau pt_8l_daily de rating_8l.csv tuoi cho cot R)
@@ dòng 67 @@
-0 8 * * 1-5 .../for_each_live_account.sh .../eod_trading_report.sh >> .../eod_trading_report.log 2>&1   # 15:00 ICT — báo cáo tổng kết giao dịch cuối ngày
+10 12 * * 1-5 .../for_each_live_account.sh .../eod_trading_report.sh >> .../eod_trading_report.log 2>&1   # 19:10 ICT (doi tu 15:00, 2026-07-15, user duyet) — bao cao tong ket giao dich cuoi ngay; sau publish DT5G 19:01 de dong "tinh trang thi truong" la regime HOM NAY
```

## 4. Kiểm tra xung đột

- **Slot 19:xx ICT (`12 * * 1-5` UTC)**: hiện chỉ có `bq_freshness_check` @19:00. Sau khi đổi:
  19:00 freshness/publish → **19:10 eod** → **19:20 pt_8l** → **19:35 telegram**. Không trùng phút nào.
- `rubber_weekly.sh` @18:35 (`35 11`) — khác giờ UTC, không đụng.
- **Thứ tự pt_8l → telegram giữ nguyên** (ràng buộc thật: comment đầu `pt_8l_daily.sh` — telegram đọc
  `rating_8l.csv` cho cột R). pt_8l chạy **~35 giây** (đo 5 phiên gần nhất: 07-08→07-14, 31-37s) →
  khoảng cách 15 phút thừa sức.
- `telegram_run_daily.sh` có retry-backoff tối đa ~30 phút khi ISP chặn → xấu nhất kết thúc ~20:05,
  chồng lấn cron 20:00 `fa_ratings_earnings_window_daily.sh`. **Vô hại**: retry chỉ là gửi Telegram,
  không đọc/ghi BQ table nào mà job 20:00 chạm.
- **Vintage fa_ratings không đổi**: pt_8l ở 19:20 vẫn nằm TRƯỚC refresh 20:00, y như 17:45 hiện tại.
- **Không giữ nguyên theo yêu cầu**: `paper_programs_daily_report.sh` (15:20, đọc compare5.csv T-1),
  `dc_book_waterfall_paper.py` (15:05) — đã xác nhận không liên quan.
- **Grep dependency**: không script/cron nào phụ thuộc giờ cũ của 3 dòng này. Các hit còn lại chỉ là
  tài liệu Windows/host khác (`TELEGRAM_SETUP.md`, `DEPLOYMENT.md`, `8L_README.md` — nói về `.bat` +
  Task Scheduler, không phải crontab này) và `freshness_ops_selfcheck.py` (chỉ kiểm tra `pt_8l_daily`
  có alert-on-fail, **không assert giờ chạy**).

## 5. ⚠️ Phát hiện kèm — reschedule KHÔNG sửa hết được (báo, không tự sửa)

`sector_lens_monitor.py` (step [9] của pt_8l_daily) đọc regime qua **BQ_LOCAL_CACHE**:
`read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet')` (dòng 98) — cache sync lúc **23:45**.
→ Dù pt_8l chạy 19:20, step này vẫn đọc state của **hôm qua** (bản sync 23:45 đêm trước). Đổi giờ
sửa được `rating_8l.py` + `cheap_pb_floor.py` (đọc BQ live), **không sửa được step [9]**.

Đây là đúng loại vintage-mismatch mà §11 cảnh báo. Là alert nghiên cứu/monitor, **không chạm trading
production** → không khẩn. Cần 1 quyết định riêng (sửa code đọc live, hay chấp nhận T-1 cho step này)
— ngoài phạm vi job này, không tự sửa.

## 6. Việc còn lại khi được duyệt

1. `crontab -l > backup` → áp 3 dòng → `crontab -l` verify.
2. Cập nhật `mike/kb/cron_registry.md` dòng 35/39/40 (bỏ cờ ⚠️ M3) — **cùng commit** theo §11.
