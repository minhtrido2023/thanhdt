#!/usr/bin/env bash
# ccdb_bridge_drift_check.sh — alert when /workspace/claude-code-discord-bridge (the shared
# Discord bridge ALL Claude sessions on this account run through) drifts too far behind its own
# upstream (origin/main, github.com/ebibibi/claude-code-discord-bridge).
#
# Root cause this prevents (2026-08-02, kb/incidents/2026-08/): the live checkout sat on a
# local-only branch, never pushed/PR'd, 115 commits (~3+ weeks) behind origin — including 3 real
# security fixes (path-traversal containment hardening for /api/ingest) that production ran
# without the whole time. Nobody was watching because nothing was watching. This check is a
# DETECT+ALERT only — it does NOT auto-merge (that 115-commit merge needed real judgment calls on
# genuine logic conflicts, e.g. a concurrency-lock race fix; blind auto-merge of a bridge every
# concurrent session depends on is not something to automate).
#
# Fires from cron_health_check_daily.sh's existing daily slot (no new cron entry — same
# "gắn vào nhịp có sẵn" principle already used there for incidents_index_sync.py).
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
BRIDGE="${CCDB_BRIDGE_DIR:-/workspace/claude-code-discord-bridge}"
ARCH_THREAD="1521475726329516122"
STAMP="$ROOT/state/ccdb_bridge_drift_alerted_sha.txt"
BEHIND_THRESHOLD=10

[ -e "$BRIDGE/.git" ] || { echo "ccdb_bridge_drift_check: $BRIDGE not a git repo, skip"; exit 0; }

cd "$BRIDGE" || exit 0
git fetch origin main --quiet 2>/dev/null || { echo "ccdb_bridge_drift_check: fetch failed, skip (network?)"; exit 0; }

BEHIND="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
ORIGIN_SHA="$(git rev-parse origin/main 2>/dev/null || echo unknown)"
SECURITY_N="$(git log --oneline HEAD..origin/main 2>/dev/null | grep -icE '^[a-f0-9]+ security' || true)"

mkdir -p "$ROOT/state"

if [ "$BEHIND" -eq 0 ]; then
    if [ -f "$STAMP" ]; then
        rm -f "$STAMP"
        echo "ccdb_bridge_drift_check: caught up with origin/main, cleared alert stamp"
    fi
    echo "ccdb_bridge_drift_check: OK (0 commits behind origin/main)"
    exit 0
fi

if [ "$BEHIND" -lt "$BEHIND_THRESHOLD" ] && [ "$SECURITY_N" -eq 0 ]; then
    echo "ccdb_bridge_drift_check: OK ($BEHIND behind, under threshold $BEHIND_THRESHOLD, no security commits)"
    exit 0
fi

_prev="$(cat "$STAMP" 2>/dev/null || true)"
if [ "$_prev" = "$ORIGIN_SHA" ]; then
    echo "ccdb_bridge_drift_check: same gap already alerted ($ORIGIN_SHA), staying quiet until it changes"
    exit 0
fi

printf '%s' "$ORIGIN_SHA" > "$STAMP"

REASON="${BEHIND} commit(s) behind origin/main"
[ "$SECURITY_N" -gt 0 ] && REASON="${REASON}, ${SECURITY_N} của đó gắn nhãn security:"

MSG="⚠️ [ccdb_bridge_drift] claude-code-discord-bridge (service dùng chung MỌI phiên Claude trên account) đang $REASON. Chi tiết: cd $BRIDGE && git log --oneline HEAD..origin/main. Đây chỉ là cảnh báo — KHÔNG tự merge (lần trước cần xử lý tay 1 race-condition fix thật, không phải việc auto-merge an toàn)."
"$ROOT/bin/notify.sh" "$MSG" >/dev/null 2>&1 || true
"$ROOT/bin/notify_thread.sh" "$MSG" "$ARCH_THREAD" >/dev/null 2>&1 || true
echo "ccdb_bridge_drift_check: ALERTED ($REASON)"
