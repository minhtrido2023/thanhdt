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

# 1b) mirror live native-subagent defs (~/.claude/agents) into the repo so the backup captures them
"$MIKE/bin/sync_native_agents.sh" || echo "WARN: native-agent sync skipped/failed"

# 2) fleet repo (own git) -> github:mike-fleet  (bus/logs/locks/state are gitignored in mike)
echo "==> Fleet repo -> github:mike-fleet"
git -C "$MIKE" add -A
# GitHub HARD-rejects any blob >100MB (GH001) — one such file blocks EVERY later push until
# history is rewritten (incident 2026-11-12: 113MB .pkl in Taylor research via this add -A).
# Unstage oversized files BEFORE they can enter a commit; file stays on disk, loudly reported.
# `git reset` (NOT `git rm --cached`): a tracked file that merely GREW past the limit goes back
# to its HEAD version in the index instead of being staged as a DELETION (arch-review b4d46c33).
# --no-renames: a renamed/copied big blob shows up as plain A, not R/C that --diff-filter=AM misses.
# unstage_oversized() is extracted + tested by bin/fleet_backup_guard_selfcheck.sh — keep it standalone.
unstage_oversized() {
  local repo="$1" limit="${FLEET_BACKUP_MAX_BYTES:-95000000}" f n=0
  while IFS= read -r -d '' f; do
    [ -f "$repo/$f" ] && [ "$(stat -c %s "$repo/$f")" -gt "$limit" ] || continue
    git -C "$repo" reset -q -- "$f" && { echo "   WARN: unstaged >95MB file (GitHub limit 100MB): $f — add to .gitignore"; n=$((n+1)); }
  done < <(git -C "$repo" diff --cached --name-only --no-renames --diff-filter=AM -z)
  return 0
}
unstage_out="$(unstage_oversized "$MIKE")"
if [ -n "$unstage_out" ]; then
  echo "$unstage_out"
  # surface to a channel someone reads (bus -> KB + ops_health), not only backup.log
  "$MIKE/bin/append_event.sh" Wags finding "fleet-backup-unstaged-oversized-$(date -u +%F)" \
    "fleet_backup bỏ khỏi commit file >95MB (còn trên đĩa, cần gitignore): $(echo "$unstage_out" | sed 's/.*limit 100MB): //; s/ — add.*//' | tr '\n' ' ')" >/dev/null 2>&1 || true
fi
if git -C "$MIKE" diff --cached --quiet; then
  echo "   (no fleet changes to commit)"
elif commit_err="$(MIKE_KB_SIZE_GATE=warn git -C "$MIKE" commit -q -m "fleet backup $ts" 2>&1)"; then
  echo "   committed: $(git -C "$MIKE" rev-parse --short HEAD)"
else
  # `|| true` here (arch-review round 2, 2026-08-12): the pre-commit collision gate
  # (bin/repo_commit_gate.sh) can REFUSE this commit — and this one stages the WHOLE index
  # (`git add -A` above), so it is the most likely of the three automatic callers to hit it.
  # Swallowed, the push below still printed "OK fleet pushed: <sha>" — of the OLD head, with
  # today's work left uncommitted and unbacked-up. The push is deliberately still attempted:
  # backing up what IS committed beats skipping the backup entirely.
  echo "   FAIL fleet commit — hôm nay KHÔNG vào backup, push dưới đây chỉ đẩy HEAD CŨ:"
  echo "$commit_err" | sed 's/^/     /'
fi
# stderr is CAPTURED, not discarded: the old 2>/dev/null + fixed "PAT expired?" hint misdiagnosed
# a GH001 large-file rejection as an auth problem for 2 nights (2026-11-10/11).
if push_err="$(git -C "$MIKE" push -q github HEAD:mike-fleet 2>&1)"; then
  echo "   OK fleet pushed: $(git -C "$MIKE" rev-parse --short HEAD)"
else
  if echo "$push_err" | grep -qiE 'GH001|large file|exceeds .*file size limit'; then
    echo "   FAIL fleet push — FILE >100MB trong lịch sử chưa push (KHÔNG phải PAT); cần gỡ khỏi history:"
  elif echo "$push_err" | grep -qiE 'authentication|401|403|invalid username|token'; then
    echo "   FAIL fleet push — lỗi AUTH (PAT hết hạn/sai?) — tạo token mới trong ~/.git-credentials:"
  else
    echo "   FAIL fleet push — lý do khác, xem stderr:"
  fi
  echo "$push_err" | grep -v -iE 'https://[^ ]*:[^ ]*@' | tail -15 | sed 's/^/     /'
fi

# 3) main workspace backup (code, docs, data reports, scrubbed Claude history)
echo "==> Main workspace backup"
/home/trido/thanhdt/backup.sh "auto-backup $ts" || echo "   FAIL main backup"

echo "==================== done $ts ===================="
