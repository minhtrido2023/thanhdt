#!/usr/bin/env bash
# cron_health_check_daily.sh — daily wrapper around cron_health_check.py.
#
# Standalone (NOT wired into ops_health_check.sh's for_each_live_account.sh loop) on purpose:
# cron_health_check.py audits the crontab, a FLEET-WIDE thing, not per-account — folding it into
# the per-account checker would run it twice a day per account (same trap already documented for
# "Job board:" in ops_health_check.sh, coord-2026-07-22). One job, one run, one report.
#
# Mandate: user, 2026-08-01, sau khi Mike tự tay bắt 2 bug quoting sống 2 tuần/2 đêm mà không cơ
# chế nào phát hiện — "cái gì đã lên lịch chạy phải có một nơi để review lại, không để tình trạng
# âm thầm chạy, âm thầm lỗi không ai xử lý."
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
ARCH_THREAD="1521475726329516122"
TRADING_DAILY_THREAD="1521470705563340910"

OUT="$(python3 "$ROOT/bin/cron_health_check.py" 2>&1)"
RC=$?

BAD_COUNT="$(echo "$OUT" | head -1 | grep -oE '[0-9]+ cần chú ý' | grep -oE '^[0-9]+' || echo 0)"

if [ "$RC" -eq 0 ]; then
  # Quiet-heartbeat: still post, even when clean — silence must never be the only signal alive.
  "$ROOT/bin/notify.sh" "🩺 [cron_health_check] $(date -u +%Y-%m-%d): tất cả job crontab OK (0 cần chú ý)." 2>/dev/null || true
else
  SUMMARY="🩺 [cron_health_check] $(date -u +%Y-%m-%d): ${BAD_COUNT} job cần chú ý — chi tiết:

$OUT"
  "$ROOT/bin/notify_thread.sh" "$SUMMARY" "$ARCH_THREAD" 2>/dev/null \
    || "$ROOT/bin/notify_thread.sh" "$SUMMARY" "$TRADING_DAILY_THREAD" 2>/dev/null || true
  "$ROOT/bin/notify.sh" "🩺 [cron_health_check] ${BAD_COUNT} job crontab cần chú ý hôm nay — xem Architecture channel." 2>/dev/null || true
fi


# incidents/index.md sync (khảo sát vận hành 2026-08-01, item #4 đã duyệt) — trước đây giao cho
# 1 job LLM/tuần (weekly_ops_audit.sh mục 5) cho 1 phép so file cơ học; giờ chạy hàng ngày ở đây
# (cùng khe đã có, không cần cron mới). Việc tài liệu thuần (không rủi ro trading) → tự sửa +
# commit, đúng ranh giới đã xác lập ở nơi mục 5 cũ (index.md lệch → tự sửa, không cần hỏi user).
if ! python3 "$ROOT/bin/incidents_index_sync.py" --check >/tmp/incidents_sync_check.$$ 2>&1; then
  DRIFT="$(cat /tmp/incidents_sync_check.$$)"
  python3 "$ROOT/bin/incidents_index_sync.py" --fix >/dev/null 2>&1 || true
  if git -C "$ROOT" diff --quiet -- kb/incidents/index.md; then
    "$ROOT/bin/notify.sh" "🟡 [cron_health_check] incidents_index_sync phát hiện drift nhưng --fix không đổi gì file — cần người kiểm tay: $DRIFT" 2>/dev/null || true
  else
    git -C "$ROOT" add kb/incidents/index.md
    git -C "$ROOT" commit -q -m "chore(incidents): auto-sync index.md ($(date -u +%Y-%m-%d), cron_health_check_daily.sh)

$DRIFT" 2>/dev/null || true
    "$ROOT/bin/notify.sh" "🩺 [cron_health_check] incidents_index_sync tự sửa drift + commit: $DRIFT" 2>/dev/null || true
  fi
fi
rm -f /tmp/incidents_sync_check.$$

# claude-code-discord-bridge upstream drift (2026-08-02, kb/incidents/2026-08/) — the shared
# Discord bridge ALL Claude sessions depend on sat 115 commits / 3+ weeks behind origin with no
# one watching, including 3 real security fixes. Detect+alert only (never auto-merge — the fix
# needed real judgment on a genuine concurrency-lock conflict). Same "gắn vào nhịp có sẵn" slot.
"$ROOT/bin/ccdb_bridge_drift_check.sh" >/dev/null 2>&1 || true

exit 0  # never fail the cron slot itself — this is a checker, not a gate
