#!/usr/bin/env bash
# Daily BQ cache sync — runs after BQ data ingest (~23:15 ICT / 16:15 UTC).
# Delta mode: appends today's new rows to existing parquet files.
# Full re-download of rolling tables (ticker_1m).
# Verifies against BQ, then runs preflight check.
set -euo pipefail
cd /home/trido/thanhdt/WorkingClaude
source wc_env.sh

SYNC_OUT=$(python3 sync_bq_cache.py --delta 2>&1) || true
echo "$SYNC_OUT"
PREFLIGHT_OUT=$(python3 preflight_bq_cache.py 2>&1)
echo "$PREFLIGHT_OUT"

# Tự sửa thay vì log-rồi-bỏ (mandate user 2026-07-07, kb/ops_runbook.md — bài học 07-06:
# verify ĐÃ báo FAILED trong log từ 03/07 nhưng không cơ chế nào đọc → cache thối 10 ngày
# âm thầm → false-SEV1 macro_health). Giờ: verify fail HOẶC bất kỳ bảng FAILED nào →
# notify + dispatch ops_autofix (tự chống lặp, cooldown 1h).
ISSUES=$( (echo "$SYNC_OUT"; echo "$PREFLIGHT_OUT") | grep -E "FAILED|FAIL —|RESULT: FAIL" || true)
if [ -n "$ISSUES" ]; then
  /home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh \
    "[BQ cache] sync/verify có vấn đề đêm nay — ops_autofix đã được kích hoạt. Chi tiết: data/bq_cache/sync.log" 2>/dev/null || true
  /home/trido/thanhdt/WorkingClaude/mike/bin/ops_autofix.sh "bq-cache-sync-verify" \
    "sync_bq_cache_daily.sh phát hiện lỗi sync/verify:
$ISSUES

Log đầy đủ: data/bq_cache/sync.log. Cách xử lý chuẩn: chẩn đoán bảng nào fail vì sao
(dtype/SQL/xung đột giờ refresh 23:15), sửa nếu là bug script, rồi resync đúng bảng đó
(python3 sync_bq_cache.py --delta --tables <bảng>; lệch count ngoài cửa sổ delta → full
re-download bảng đó) và chạy --verify xác nhận OK. Xem kb/INCIDENTS.md 2026-07-06 (đêm)." 2>/dev/null || true
fi
