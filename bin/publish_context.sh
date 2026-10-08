#!/usr/bin/env bash
# publish_context.sh
# Rebuilds kb/context_pack.md from the latest fleet events. The RECENT block (between
# the markers) is what the UserPromptSubmit hook injects as the cross-agent delta.
# Reads the CURRENT version.txt (caller bumps it BEFORE calling this).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"; BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"
mkdir -p "$KB"

ver="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; ver="${ver:-0}"

# RECENT = last 8 already-summarized lines from the per-version delta log (short, not raw JSON).
recent="$(python3 "$PY" recent "$KB/recent_delta.jsonl" 5 2>/dev/null || true)"
[ -n "${recent//[[:space:]]/}" ] || recent="(chưa có sự kiện nào)"

# printf '%s' prints $recent literally — no shell interpretation of payload contents.
{
  printf '# Mike fleet — context pack (v%s)\n' "$ver"
  printf '> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.\n\n'
  printf '<!--RECENT-START-->\n'
  printf '## MỚI NHẤT — kết quả gần đây từ toàn fleet\n'
  printf '%s\n' "$recent"
  printf '<!--RECENT-END-->\n\n'
  # Current operations — tình trạng live hiện tại (Mike-maintained).
  if [ -s "$KB/current_ops.md" ]; then
    cat "$KB/current_ops.md"
    printf '\n'
  fi
  # Canonical knowledge (Mike-edited, single source of truth).
  if [ -s "$KB/canonical.md" ]; then
    cat "$KB/canonical.md"
    printf '\n'
  fi
  # kb/projects/INDEX.md (closed-project index) is NOT in the pack since 2026-10-08 (user duyệt,
  # job Wags_20261008_143309): its OPEN-projects section moved verbatim into current_ops.md; the
  # closed list is retrieved on demand via `bin/kb_recall.sh` (source `projects`, in its defaults)
  # or `grep kb/projects/INDEX.md` — canonical.md carries the rule to do so before R&D proposals.
  printf '## Nguồn chuẩn tắc đầy đủ\n'
  printf 'Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/INDEX.md (KHÔNG nạp sẵn — `bin/kb_recall.sh "<từ khoá>"` hoặc grep). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.\n'
} > "$KB/context_pack.md"

echo "published context_pack v$ver"
