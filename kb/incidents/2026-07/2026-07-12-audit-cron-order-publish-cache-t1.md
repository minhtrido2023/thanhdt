---
kind: incident
date: 2026-07-12
topic: audit-cron-order-publish-cache-t1
title: >-
  2026-07-12 — Audit cron-order (Winston_20260712_142100) bắt 2 bug production-blocking cùng lúc: C1 CRITICAL publish DT5G qua cache T-1 thay vì live, H2 HIGH freshness-check miscalibrated
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-12 — Audit cron-order (Winston_20260712_142100) bắt 2 bug production-blocking cùng lúc: C1 CRITICAL publish DT5G qua cache T-1 thay vì live, H2 HIGH freshness-check miscalibrated

**Hiện tượng:** user yêu cầu Mike rà lại thứ tự ~45+ dòng cron. Dispatch Winston (fable)
audit toàn bộ → thứ tự ĐÚNG, nhưng lộ ra 2 bug NỘI DUNG khẩn cấp, cả 2 sẽ tự kích hoạt
trong tuần từ hành động KHÔNG LIÊN QUAN đã làm ngày hôm trước (siết `MAX_STATE_LAG=0`
07-11):

- **C1 CRITICAL** — `deploy_golive_dt5g_v4/publish_gated_state.py` đọc DT5G base qua
  `BQ_LOCAL_CACHE` (luôn T-1, do `wc_env.sh` export biến này toàn cục) thay vì BigQuery
  live, dù comment trong script tự khai "SOURCE OF TRUTH = BigQuery... NOT a local CSV" —
  ý định đúng, code không enforce. Với `MAX_STATE_LAG=0` (mới siết hôm trước), thứ Hai
  07-13 19:00 ICT sẽ FAIL cứng, chặn luôn dispatch DollarBill lập plan T+1 (thứ Ba
  07-14 không có plan).
- **H2 HIGH** — check `shares_outstanding_live` giả định có 1 writer cập nhật
  `updated_at` hàng ngày, nhưng cron thực tế chỉ chạy `--scan` (detection-only, không ghi
  `updated_at`) → check tự BLOCK giả ~thứ Tư 07-15 dù dữ liệu không hề stale thật.

**Root cause C1:** biến môi trường cache được thiết kế cho mọi script MUỐN cache (đa số
script research/backtest) bị kế thừa vô điều kiện vào publish script — script duy nhất
BẮT BUỘC phải đọc live vì nó chính là nguồn công bố cho các consumer khác. Không có bước
nào từng kiểm tra lại "publish script có thực sự đọc live không" cho tới khi ngưỡng gate
bị siết đủ chặt (0 ngày) để biến sai lệch tiềm ẩn (T-1 vs T) thành fail cứng.

**Fix C1:** `os.environ.pop('BQ_LOCAL_CACHE', None)` process-local ngay trước import
`macro_state_live` (commit `4995262`, repo WorkingClaude). Lưu ý vận hành: 2 lần dispatch
Taylor để fix đều timeout (tự mở rộng phạm vi sang backfill C1b không cần thiết) — Mike
tự đọc code, tự sửa, tự commit, rồi dispatch quant-skeptic bằng `--claim` (không có finding
event chính thức từ Taylor vì job không hoàn tất). **quant-skeptic CONFIRMED** (high
confidence, tự tái lập cơ chế bằng Python replica độc lập: pop env → cache branch bypass →
live path; xác nhận process-local, không leak sang sibling process; 1 ghi chú tùy chọn về
`LOCAL_SNAPSHOT_DIR` — hiện vô hại vì biến chưa từng được export).

**Fix H2:** đổi từ BLOCK → WARN cho check `shares_outstanding_live` (commit `6459b6d`,
repo mike, `bin/bq_freshness_check.sh`) — job `Winston_20260712_155038`. **quant-skeptic
CONFIRMED** (3 lần verify độc lập qua `--claim`, chạy `freshness_ops_selfcheck.py` 42/45 —
3 FAIL còn lại đến từ probe khác mới thêm cùng ngày, không liên quan H2).

**Verify:** cả 2 fix đã qua quant-skeptic CONFIRMED trong ngày; còn 3 mục chờ xác nhận
qua lần chạy cron thật thứ Hai 07-13 18:30/19:00 ICT (đã ghi ở `kb/current_ops.md`, không
lặp lại ở đây).

**Bài học:** một publish/production script đọc input qua bất kỳ biến env cache nào kế
thừa từ script dùng chung (`wc_env.sh`) là rủi ro tiềm ẩn — không lộ ra cho tới khi có 1
thay đổi KHÔNG LIÊN QUAN (siết gate) biến nó thành fail cứng. `coding_guidelines.md` §11
đã được thêm cùng ngày để bắt buộc tra `kb/cron_registry.md` (đọc gì+vintage) trước khi
đổi lịch/ngưỡng cron.
