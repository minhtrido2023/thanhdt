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
recent="$(python3 "$PY" recent "$KB/recent_delta.jsonl" 8 2>/dev/null || true)"
[ -n "${recent//[[:space:]]/}" ] || recent="(chưa có sự kiện nào)"

# printf '%s' prints $recent literally — no shell interpretation of payload contents.
{
  printf '# Mike fleet — context pack (v%s)\n' "$ver"
  printf '> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.\n\n'
  printf '<!--RECENT-START-->\n'
  printf '## MỚI NHẤT — kết quả gần đây từ toàn fleet\n'
  printf '%s\n' "$recent"
  printf '<!--RECENT-END-->\n\n'
  # Curated canonical knowledge (Mike-edited) — injected into every agent at SessionStart.
  if [ -s "$KB/canonical.md" ]; then
    cat "$KB/canonical.md"
    printf '\n'
  fi
  printf '## Nguồn chuẩn tắc đầy đủ\n'
  printf 'Lịch sử/chi tiết: kb/KNOWLEDGE.md (Mike biên tập). Trạng thái fleet: kb/fleet_status.md.\n'
} > "$KB/context_pack.md"

echo "published context_pack v$ver"
