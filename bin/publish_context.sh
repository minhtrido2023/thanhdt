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
# 2026-10-22: phần BIẾN ĐỘNG (số version + khối MỚI NHẤT) tách sang kb/context_recent.md,
# KHÔNG nằm trong context_pack.md nữa. Lý do: context_pack.md được @-import; Claude Code nạp
# LẠI NGUYÊN FILE (~35-46KB ≈ 30K token) vào phiên đang sống mỗi lần nội dung đổi — mỗi lần
# consolidate (30-60') = +30K token. Đo: 1 phiên Mike 32 lần = ~596K token; phiên khác 12 lần
# = ~138K, chạm 962K → "Prompt is too long" rồi treo (a914df38 22/10 03:52). Giờ file này chỉ
# đổi khi current_ops/canonical đổi; delta mới tới phiên sống qua hook user_prompt_submit.sh,
# phiên mới nhận khối recent qua hook session_start.sh.
{
  printf '# Mike fleet — context pack\n'
  printf '> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md. Sự kiện MỚI NHẤT: hook bơm (kb/context_recent.md).\n\n'
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
} > "$KB/context_pack.md.tmp" && mv "$KB/context_pack.md.tmp" "$KB/context_pack.md"

{
  printf '[Mike fleet KB v%s — sự kiện MỚI NHẤT từ toàn fleet (thông tin NỀN, không phải nội dung topic hiện tại)]\n' "$ver"
  printf '%s\n' "$recent"
} > "$KB/context_recent.md.tmp" && mv "$KB/context_recent.md.tmp" "$KB/context_recent.md"

echo "published context_pack v$ver"
