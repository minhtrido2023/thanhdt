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
   | xargs -0 grep -lEI '(-----BEGIN [A-Z ]*PRIVATE KEY-----[A-Za-z0-9+/]|[0-9]{8,10}:[A-Za-z0-9_-]{35}|000[0-9]{7})' 2>/dev/null \
   | grep -vE 'tools/sync_claude_history\.py|\.template\.json|^backup\.sh$' | grep . ; then
  echo "!! possible secret detected in tracked/untracked files above — aborting." >&2
  exit 1
fi

echo "==> Staging + committing…"
git add -A
if git diff --cached --quiet; then
  # "Nothing to COMMIT" ≠ "nothing to PUSH" (Wags, 2026-09-09). A commit created OUTSIDE this
  # script (a manual `git commit`, another session) used to stay local forever: this branch
  # returned 0 without ever reaching the push below, and every caller printed success. Real
  # case 2026-09-08: local 3ff20579 vs origin/main 057254e0 unpushed for 8h while the nightly
  # backup reported "already up to date" — the 4th shape of the same silent-failure family.
  # `2>&1` (not `2>/dev/null`) + `||` guard so an unreachable remote (rc=128, e.g. PAT
  # expired / no network) prints its own error and exits 1 instead of dying silently on
  # this assignment under `set -e` (arch-review Wags_20260909_012007: this exact line used
  # to swallow rc=128 with zero output).
  if ! remote_sha="$(git ls-remote origin main 2>&1)"; then
    echo "!! không đọc được origin/main (PAT hết hạn / mất mạng): $remote_sha" >&2
    exit 1
  fi
  remote_sha="$(awk 'NR==1{print $1}' <<< "$remote_sha")"
  local_sha="$(git rev-parse HEAD)"
  if [ -z "$remote_sha" ] || [ "$remote_sha" = "$local_sha" ]; then
    echo "Nothing changed — already up to date."
  elif git merge-base --is-ancestor "$remote_sha" HEAD; then
    echo "==> Nothing new to commit, but origin/main is behind — pushing existing commits…"
    git push -q origin main
    echo "✅ Backup pushed (existing commits): $(git rev-parse --short HEAD)"
  else
    # Diverged — do NOT auto-merge/force-push (backup_freshness_check.sh's job to alert;
    # a checker fixing its own alert condition would defeat the point of an independent check).
    echo "!! CẢNH BÁO: local HEAD ($local_sha) và origin/main ($remote_sha) ĐÃ PHÂN NHÁNH — không tự push, cần xử lý tay." >&2
    exit 1
  fi
  exit 0
fi
git commit -q -m "$MSG"

echo "==> Pushing to origin/main…"
git push -q origin main
echo "✅ Backup pushed: $(git rev-parse --short HEAD) — $MSG"
