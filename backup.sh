#!/usr/bin/env bash
# One-command backup: sync scrubbed Claude history, then commit + push everything.
#   ./backup.sh ["commit message"]
# Safe to run any time. Secrets, bulk data, venv, gcloud config are gitignored;
# Claude transcripts/memory are scrubbed by tools/sync_claude_history.py.
set -euo pipefail

REPO="/home/trido/thanhdt"
cd "$REPO"

MSG="${1:-backup $(date +%Y-%m-%d\ %H:%M)}"

echo "==> Syncing scrubbed Claude history…"
if ! python3 tools/sync_claude_history.py; then
  echo "!! history sync reported a secret leak — aborting (nothing committed)." >&2
  exit 1
fi

# Belt-and-suspenders: refuse to commit if a known secret pattern slipped in.
echo "==> Secret gate…"
if git -c core.quotepath=false ls-files -o -c --exclude-standard -z 2>/dev/null \
   | xargs -0 grep -lEI '(-----BEGIN [A-Z ]*PRIVATE KEY-----[A-Za-z0-9+/]|[0-9]{8,10}:[A-Za-z0-9_-]{35})' 2>/dev/null \
   | grep -vE 'tools/sync_claude_history\.py|\.template\.json|^backup\.sh$' | grep . ; then
  echo "!! possible secret detected in tracked/untracked files above — aborting." >&2
  exit 1
fi

echo "==> Staging + committing…"
git add -A
if git diff --cached --quiet; then
  echo "Nothing changed — already up to date."
  exit 0
fi
git commit -q -m "$MSG"

echo "==> Pushing to origin/main…"
git push -q origin main
echo "✅ Backup pushed: $(git rev-parse --short HEAD) — $MSG"
