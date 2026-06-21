#!/usr/bin/env bash
# fleet_backup.sh — ONE daily backup of EVERYTHING to GitHub (non-interactive, stored PAT).
#   1) consolidate fleet bus -> KB (best-effort; has its own flock)
#   2) commit + push the mike fleet repo to the 'mike-fleet' branch of minhtrido2023/thanhdt
#   3) run the main workspace backup (~/thanhdt/backup.sh): scrub -> secret-gate -> push main
# Logs each step and reports push failures (e.g. expired PAT) instead of failing silently.
set -uo pipefail
MIKE="/home/trido/thanhdt/WorkingClaude/mike"
ts="$(date -u +%FT%TZ)"
echo "==================== fleet_backup $ts ===================="

# 1) consolidate bus -> KB so the backup captures the latest knowledge
"$MIKE/bin/consolidate.sh" >/dev/null 2>&1 || echo "WARN: consolidate skipped/failed"

# 2) fleet repo (own git) -> github:mike-fleet  (bus/logs/locks/state are gitignored in mike)
echo "==> Fleet repo -> github:mike-fleet"
git -C "$MIKE" add -A
if git -C "$MIKE" diff --cached --quiet; then
  echo "   (no fleet changes to commit)"
else
  git -C "$MIKE" commit -q -m "fleet backup $ts" || true
fi
if git -C "$MIKE" push -q github HEAD:mike-fleet 2>/dev/null; then
  echo "   OK fleet pushed: $(git -C "$MIKE" rev-parse --short HEAD)"
else
  echo "   FAIL fleet push (PAT expired? regenerate token in ~/.git-credentials)"
fi

# 3) main workspace backup (code, docs, data reports, scrubbed Claude history)
echo "==> Main workspace backup"
/home/trido/thanhdt/backup.sh "auto-backup $ts" || echo "   FAIL main backup"

echo "==================== done $ts ===================="
