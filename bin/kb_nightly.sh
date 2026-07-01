#!/usr/bin/env bash
# kb_nightly.sh — Nightly KB maintenance (02:00 ICT = 19:00 UTC).
#
# Phases:
#   1. Archive raw consolidation blocks in KNOWLEDGE.md older than KEEP_DAYS.
#   2. Alert if any agent working memory (kb/memory/*.md) exceeds MEM_WARN_KB.
#   3. Commit + backup + Telegram notify.
#   4. On Friday: dispatch Mike headless for LLM editorial review of canonical sections.
#
# "Hippocampal replay": events from episodic buffer → long-term archive.
# LLM reasoning (Friday) = REM phase: compress into structured canonical knowledge.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

KEEP_DAYS="${KB_KEEP_DAYS:-3}"        # hot-tier retention for raw events
MEM_WARN_KB="${KB_MEM_WARN_KB:-5}"    # alert threshold per agent memory file
LOG="$ROOT/logs/kb_nightly.log"
EVENTS_BUFFER="$ROOT/kb/events_buffer.md"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }

log "=== kb_nightly START ==="

# ── Phase 1: archive stale raw events ─────────────────────────────────────────
CUTOFF=$(date -u -d "-${KEEP_DAYS} days" +%Y-%m-%d 2>/dev/null \
      || date -u -v-${KEEP_DAYS}d +%Y-%m-%d 2>/dev/null \
      || python3 -c "import datetime; print((datetime.datetime.utcnow()-datetime.timedelta(days=$KEEP_DAYS)).strftime('%Y-%m-%d'))")

log "Archiving consolidator blocks older than $CUTOFF (keep_days=$KEEP_DAYS)..."

ARCHIVE_DATE=$(date -u +%Y-%m-%d)
ARCHIVE_FILE="$ROOT/kb/archive/${ARCHIVE_DATE}-nightly.md"

python3 - "$EVENTS_BUFFER" "$CUTOFF" "$ARCHIVE_FILE" <<'PYEOF'
import sys, re, pathlib, datetime

knowledge_path = pathlib.Path(sys.argv[1])
cutoff = sys.argv[2]         # YYYY-MM-DD
archive_path = pathlib.Path(sys.argv[3])

lines = knowledge_path.read_text(encoding='utf-8').splitlines(keepends=True)

# Find separator: line containing the consolidator-append footer marker
# Keep canonical (everything before first raw-event block line)
# A raw-event line = "- [2026-" prefixed (consolidator block entries)
EVENT_RE = re.compile(r'^- \[(\d{4}-\d{2}-\d{2})')

canonical = []
to_keep = []     # recent events (< KEEP_DAYS)
to_archive = []  # old events
in_events = False

for line in lines:
    m = EVENT_RE.match(line)
    if m:
        in_events = True
        event_date = m.group(1)
        if event_date < cutoff:
            to_archive.append(line)
        else:
            to_keep.append(line)
    else:
        if in_events:
            # non-event line after events started = continuation or blank between events
            # attach to whichever bucket the last event went to
            if to_archive and not to_keep:
                to_archive.append(line)
            else:
                to_keep.append(line)
        else:
            canonical.append(line)

archived_count = len([l for l in to_archive if EVENT_RE.match(l)])
if archived_count == 0:
    print(f"SKIP: no events older than {cutoff}")
    sys.exit(0)

# Write archive (append if file exists)
archive_path.parent.mkdir(parents=True, exist_ok=True)
with archive_path.open('a', encoding='utf-8') as f:
    if archive_path.stat().st_size == 0 if archive_path.exists() else True:
        f.write(f"# KB nightly archive — {cutoff} cutoff\n\n")
    f.writelines(to_archive)

# Rewrite KNOWLEDGE.md without archived events
knowledge_path.write_text(''.join(canonical + to_keep), encoding='utf-8')
print(f"ARCHIVED: {archived_count} events → {archive_path.name}")
PYEOF

# ── Phase 2: alert on oversized working memories ──────────────────────────────
log "Checking agent working memories..."
OVERSIZE=""
for f in "$ROOT/kb/memory/"*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f" .md)
    kb=$(du -k "$f" | cut -f1)
    if [ "$kb" -gt "$MEM_WARN_KB" ]; then
        log "WARNING: $name.md is ${kb}KB > ${MEM_WARN_KB}KB threshold"
        OVERSIZE="$OVERSIZE $name(${kb}KB)"
    fi
done

# ── Phase 3: commit if changed ────────────────────────────────────────────────
if git -C "$ROOT" diff --quiet && git -C "$ROOT" status --porcelain | grep -q .; then
    :  # new untracked files
fi
CHANGED=$(git -C "$ROOT" status --porcelain kb/ | wc -l)
if [ "$CHANGED" -gt 0 ]; then
    git -C "$ROOT" add kb/
    git -C "$ROOT" commit -m "kb: nightly cleanup $(date -u +%Y-%m-%d) — archive+trim" \
        --author="Mike <mike@fleet>" || true
    log "Git committed."
else
    log "No KB changes to commit."
fi

# Backup
"$ROOT/bin/backup.sh" "kb_nightly $(date -u +%Y-%m-%d)" >> "$LOG" 2>&1 || true

# ── Phase 4: notify ──────────────────────────────────────────────────────────
MSG="🌙 KB nightly done ($(date -u +%Y-%m-%d))"
[ -n "${OVERSIZE:-}" ] && MSG="$MSG — ⚠️ oversized memories:$OVERSIZE"
"$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
_tid="$(cat "$ROOT/agents/Mike/state/ccdb_thread_id" 2>/dev/null || true)"
[ -n "${_tid:-}" ] && "$ROOT/bin/notify_thread.sh" "$MSG" "$_tid" 2>/dev/null || true

# ── Phase 5: Friday = LLM editorial review ──────────────────────────────────
DOW=$(date -u +%u)  # 1=Mon … 7=Sun; 5=Fri
if [ "$DOW" -eq 5 ]; then
    log "Friday → dispatching Mike for LLM editorial review of KNOWLEDGE.md..."
    "$ROOT/bin/dispatch.sh" Mike \
"KB weekly editorial review (automated, Friday nightly).
Bạn đang ở headless mode. Nhiệm vụ: đọc kb/KNOWLEDGE.md, kiểm tra 9 canonical sections có còn đúng không (facts đã outdate, mục nào nên update từ events gần đây trong context_pack.md), viết lại những section cần thiết, commit. KHÔNG xóa archive. Không cần hỏi user — đây là routine maintenance đã được user uỷ quyền. Sau khi xong: ghi sự thay đổi lên bus (append_event.sh Mike decision 'kb-weekly-editorial') và notify Telegram." \
        --timeout 900 >> "$LOG" 2>&1 &
    log "Editorial dispatch launched (background)."
fi

log "=== kb_nightly DONE ==="
