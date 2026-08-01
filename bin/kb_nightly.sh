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

# ── Phase 0: cursor/consolidate regression selfcheck ───────────────────────────
# Every phase below (1a/1/1b/1b2/1b3) depends on the content-anchored cursor logic in
# mike_json.py + the flush-order/debounce logic in consolidate.sh being correct — that logic
# has already had 3 rounds of real bugs found by independent review on 2026-07-28 (a same-day
# regression chain, see kb/INCIDENTS.md). Run its regression suite BEFORE touching anything
# tonight: it's offline, isolated (own sandbox dirs), ~1s, and its whole purpose ("so this
# never has to happen again for this pipeline") is not delivered by a test nobody runs — an
# earlier round of this exact fix chain wrote a test, then left it wired to nothing.
SELFCHECK_OK=1
if ! python3 "$ROOT/bin/cursor_advance_selfcheck.py" >> "$LOG" 2>&1; then
    SELFCHECK_OK=0
    log "FAIL: cursor_advance_selfcheck.py — cursor/consolidate pipeline regressed, see $LOG"
    "$ROOT/bin/notify.sh" "🔴 kb_nightly: cursor_advance_selfcheck.py FAILED — KB ingestion pipeline có thể đang mất event âm thầm. Phase 1b/1b2 (prune bus/inbox) SKIPPED đêm nay, KHÔNG tự sửa, cần người kiểm ngay: $LOG" >/dev/null 2>&1 || true
    "$ROOT/bin/append_event.sh" Mike error "cursor-selfcheck-failed" \
      "{\"note\": \"kb_nightly Phase 0 selfcheck FAIL — Phase 1b/1b2 SKIPPED dem nay (fail-safe pause, khong tiep tuc prune bang logic da biet loi)\", \"log\": \"$LOG\"}" \
      >/dev/null 2>&1 || true
fi

# consolidate.sh's git-commit SCOPE (separate concern from the cursor logic above — does NOT
# gate Phase 1b/1b2, which only depend on cursor/offset correctness, not commit scope): a
# repo-wide `git add -A` there twice swept an in-progress code edit into an auto-generated
# "consolidate KB vNNNN" commit message on 2026-07-28 (see kb/INCIDENTS.md), fixed by scoping
# to `-- kb/` on both add and commit. Alert-only (not a gate) — a bad commit message is an
# audit-trail annoyance, not a data-loss risk, so it doesn't warrant pausing tonight's prune.
if ! python3 "$ROOT/bin/consolidate_git_scope_selfcheck.py" >> "$LOG" 2>&1; then
    log "FAIL: consolidate_git_scope_selfcheck.py — consolidate.sh may be sweeping unrelated files into its commits again, see $LOG"
    "$ROOT/bin/notify.sh" "🟡 kb_nightly: consolidate_git_scope_selfcheck.py FAILED — consolidate.sh có thể lại cuốn file không liên quan vào commit KB tự động: $LOG" >/dev/null 2>&1 || true
    "$ROOT/bin/append_event.sh" Mike error "consolidate-git-scope-selfcheck-failed" \
      "{\"note\": \"kb_nightly Phase 0 selfcheck FAIL — consolidate.sh git-commit scope co the da regressed\", \"log\": \"$LOG\"}" \
      >/dev/null 2>&1 || true
fi

# ── Phase 0b: post-condition check của Friday editorial dispatch (Wags audit 2026-07-30, P3)
# Dispatch Friday chạy NỀN (`&` ở cuối, xem Phase 5 dưới) — không exit-code check, không
# artifact check. Đã từng im lặng fail 2 TUẦN LIỀN (06-27→07-09, xem comment ở Phase 5) vì
# self-dispatch guard; nguyên nhân ĐÓ đã fix, nhưng cơ chế thiếu-verify khiến điều tương tự có
# thể tái diễn vì lý do KHÁC (phiên Mike lạc đề/chết im — đúng họ lỗi vừa vá ở daily_retro.sh
# + ops_autofix.sh hôm nay) mà không ai biết cho tới khi tự ý phát hiện. Prompt Friday đã bắt
# buộc kết bằng `append_event.sh Mike decision 'kb-weekly-editorial'` — hợp đồng đầu ra đã có
# sẵn, chỉ thiếu người đọc lại. Kiểm NGAY ở lần chạy kế tiếp (thứ Bảy, cùng biến DOW dùng ở
# Phase 5 dưới) xem event đó có xuất hiện trong ~30h qua không (đủ rộng để không kén giờ chạy
# chính xác, hẹp đủ để không lẫn tuần trước). Không tự sửa gì — chỉ log + notify, giống hệt
# tinh thần leftover-draft staleness check của daily_retro.sh.
DOW_CHECK="$(date -u +%u)"
if [ "$DOW_CHECK" -eq 6 ]; then
    SINCE_ISO="$(date -u -d '30 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
        || date -u -v-30H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
        || python3 -c "import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=30)).strftime('%Y-%m-%dT%H:%M:%SZ'))")"
    FRIDAY_CONFIRMED="$(python3 - "$SINCE_ISO" "$ROOT/bus/inbox/Mike.jsonl" <<'PYEOF' 2>/dev/null || echo no
import json, sys
from datetime import datetime
since_iso, path = sys.argv[1:3]
since = datetime.strptime(since_iso, "%Y-%m-%dT%H:%M:%SZ")
found = False
try:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("topic") != "kb-weekly-editorial" or rec.get("event_type") != "decision":
                continue
            try:
                rts = datetime.strptime(rec.get("ts", ""), "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
            if rts >= since:
                found = True
    print("yes" if found else "no")
except FileNotFoundError:
    print("no")
PYEOF
)"
    if [ "$FRIDAY_CONFIRMED" = "yes" ]; then
        log "Phase 0b: Friday KB editorial post-condition OK (event kb-weekly-editorial tìm thấy trong ~30h qua)."
    else
        log "WARNING Phase 0b: KHÔNG tìm thấy event 'Mike decision kb-weekly-editorial' trong ~30h qua — Friday editorial review tuần này có thể đã lạc đề/chết im, không ai biết."
        "$ROOT/bin/notify.sh" "⚠️ [kb_nightly] Friday KB editorial review tuần này KHÔNG có kết quả xác nhận được (không có bus event 'kb-weekly-editorial' trong ~30h qua) — phiên Mike thứ Sáu có thể đã lạc đề/chết im. Cần người kiểm tra logs/kb_nightly.log của thứ Sáu tuần này." >/dev/null 2>&1 || true
        "$ROOT/bin/append_event.sh" Mike question "kb-weekly-editorial-unconfirmed-$(date -u +%Y-%m-%d)" \
          "{\"reason\":\"khong tim thay event Mike/decision/kb-weekly-editorial trong ~30h truoc lan chay nay\",\"checked_since\":\"$SINCE_ISO\"}" \
          >/dev/null 2>&1 || true
    fi
fi

# ── Lock: Phase 1a/1 (events_buffer.md) + 1b/1b2 (bus/inbox + offsets) ───────
# consolidate.sh holds locks/consolidator.lock while it appends to the same file, and it
# runs after EVERY dispatch (dispatch.sh, run_bot.sh, verify_finding.sh, fleet_backup.sh)
# — not just the :07 cron. Without this lock an append landing between our read and our
# os.replace is erased whole (reproduced by arch-reviewer 2026-07-28, ~23 ms window).
# Required by kb/cron_registry/_adding-cron-policy.md §"File đọc-sửa-ghi → flock cùng lock".
# Phase 1 had this hole before Phase 1a existed; one lock closes both. Phase 1b/1b2 are inside
# the same region too: they rewrite bus/inbox/*.jsonl AND move consolidate.sh's cursors
# (state/offsets), which must not shift under a consolidate run mid-flight.
# Wait, don't skip (nightly must run); if the lock can't be had, skip ONLY these buffer/bus
# phases — a night of unpruned buffer is cheap, a lost finding is not. Released after Phase 1b2.
#
# ⚠️ SCOPE: this lock only excludes consolidate.sh (the other holder of the same lock). It does
# NOT block append_event.sh, which flocks its own per-agent inbox file and can append while we
# hold this. A line appended between our read and our os.replace is therefore still dropped —
# a pre-existing, known residual race, not something Phase 1b/1b2 introduced. It is survivable
# because the appended line is NEW (above the cursor), so the write-back loses it from
# bus/inbox but consolidate has not yet ingested it either. Closing it properly means
# append_event.sh taking this same lock; deliberately not done here (it would serialise every
# agent's writes fleet-wide behind the nightly).
mkdir -p "$ROOT/locks"
exec 8>"$ROOT/locks/consolidator.lock"
BUFFER_LOCK=0
if flock -w 120 8; then
    BUFFER_LOCK=1
else
    log "WARN: không lấy được locks/consolidator.lock sau 120s → BỎ QUA Phase 1a+1 đêm nay (tránh lost-update với consolidate.sh)"
    PRUNE_WARN="buffer phases SKIPPED (lock busy)"
fi

if [ "$BUFFER_LOCK" = 1 ]; then

# ── Phase 1a: strip heartbeats from events_buffer.md (BEFORE Phase 1 archives it) ──
# Same leak Phase 1b fixed for bus/inbox/*.jsonl, one layer up: consolidate.sh copies
# EVERY new bus event into kb/events_buffer.md hourly (cron :07) and after every dispatch
# with no filter, so the hot
# buffer is ~57% heartbeat noise (measured 2026-07-28: 355/623 lines, 200KB) and Phase 1
# below archives that noise VERBATIM into kb/archive/<date>-nightly.md, making it
# permanent (largest archive seen: 660KB).
# Unlike bus/inbox — where Phase 1b keeps the recent HB_KEEP_DAYS window because jobs.sh/
# trace.sh read it for job triage — NOTHING reads heartbeats out of events_buffer.md
# (liveness comes from bus/inbox + bus/registry), so they are worthless here at ANY age:
# drop them all. Every other event_type and every unrecognised/blank line is kept
# byte-for-byte. Also drops "## Consolidation" headers left with no event (only blocks
# that are ENTIRELY heartbeat produce one — measured 3 over a 24-day buffer, not one per
# block), else such a header sinks into Phase 1's canonical bucket and never leaves.
# Atomic write (tmp + os.replace, coding_guidelines §3) + conservation guard. NOTE the
# guard's exact scope: it re-uses HB_RE, so it validates the header-drop loop only — it
# canNOT certify HB_RE itself. KNOWN LIMITATION of HB_RE: fmt_event (mike_json.py:91-92)
# emits a STRING payload verbatim, so a payload containing a real newline renders as
# several physical lines; a heartbeat line QUOTED inside such a payload would be dropped
# mid-payload. Measured 2026-07-28: 3/1981 bus events have multi-line string payloads,
# 0 of them quote an event line → no live exposure, but keep it in mind when an ops agent
# pastes heartbeat lines into an incident report.
# Guarded so a failure can't abort the nightly. Existing kb/archive/*.md = historical
# record, NOT rewritten.
log "Pruning heartbeat lines from kb/events_buffer.md (all ages; nothing reads them here)..."
PRUNE_OUT="$(python3 - "$EVENTS_BUFFER" 2>&1 <<'PYEOF'
import sys, re, os, pathlib

path = pathlib.Path(sys.argv[1])
if not path.exists():
    print("SKIP: no events_buffer.md")
    sys.exit(0)

lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

# A rendered bus event line (mike_json.fmt_event): "- [<ts>] <agent>/<event_type> — <topic>: <payload>"
HB_RE    = re.compile(r'^- \[\d{4}-\d{2}-\d{2}[^\]]*\] [^/\s]+/heartbeat — ')
EVENT_RE = re.compile(r'^- \[\d{4}-\d{2}-\d{2}')
HDR_RE   = re.compile(r'^## Consolidation ')

survivors = [l for l in lines if not HB_RE.match(l)]
removed = len(lines) - len(survivors)

out, i, dropped_hdr = [], 0, 0
while i < len(survivors):
    if HDR_RE.match(survivors[i]):
        j = i + 1
        while j < len(survivors) and not HDR_RE.match(survivors[j]):
            j += 1
        body = survivors[i + 1:j]
        if any(EVENT_RE.match(b) for b in body):
            out.extend(survivors[i:j])
        else:
            out.extend(b for b in body if b.strip())   # keep any stray non-blank text
            dropped_hdr += 1
        i = j
    else:
        out.append(survivors[i])
        i += 1

if removed == 0 and dropped_hdr == 0:
    print("SKIP: no heartbeat lines in events_buffer.md")
    sys.exit(0)

want = [l for l in lines if not HB_RE.match(l) and not HDR_RE.match(l) and l.strip()]
got  = [l for l in out   if not HDR_RE.match(l) and l.strip()]
if want != got:
    print(f"SKIP: conservation FAIL (want={len(want)} got={len(got)}) — events_buffer.md untouched")
    sys.exit(0)

tmp = str(path) + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    fh.writelines(out)
os.replace(tmp, path)
print(f"EVENTS-BUFFER-PRUNE: removed {removed} heartbeat line(s), {dropped_hdr} empty block header(s)")
PYEOF
)" || PRUNE_OUT="events-buffer-prune: python error (non-fatal, buffer untouched) :: $PRUNE_OUT"
echo "$PRUNE_OUT" | tee -a "$LOG"
# Surface only the ABNORMAL outcomes to Phase 4's notification — a prune that quietly
# stops working (conservation FAIL / python error) would otherwise be discoverable only
# by re-measuring the buffer months later, i.e. exactly how this leak was found.
case "$PRUNE_OUT" in
    *"EVENTS-BUFFER-PRUNE:"*|*"SKIP: no heartbeat"*|*"SKIP: no events_buffer"*) ;;
    *) PRUNE_WARN="events_buffer prune: ${PRUNE_OUT%%$'\n'*}" ;;
esac

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

# Phase 1b/1b2 rewrite bus/inbox/*.jsonl AND move consolidate.sh's cursors via cursor_shift —
# exactly the logic Phase 0 just tested. Detecting a regression and pruning with it anyway is
# alert-and-proceed, not fail-safe pause (arch-review round 5, 2026-07-28): a night of
# unpruned bus is cheap, a cursor moved by broken arithmetic is not easily undone.
if [ "${SELFCHECK_OK:-1}" != 1 ]; then
    log "SKIPPED Phase 1b/1b2 (cursor selfcheck failed above) — bus/inbox left untouched tonight"
else

# ── Phase 1b: prune stale heartbeats from bus inbox ───────────────────────────
# Heartbeats are liveness pings — useless once a job ends. They dominate bus/inbox
# (measured 2026-07-27: ~7.2K/8.7K lines fleet-wide, Taylor.jsonl 3MB with 88%
# heartbeat) and inflate every bus read. Drop event_type=="heartbeat" older than
# HB_KEEP_DAYS; keep EVERY other event_type (finding/question/answer/verification/
# decision/error/status/directive) and any unparseable/blank line untouched. Atomic
# per-file write (tmp + os.replace, coding_guidelines §5) so a mid-run kill leaves the
# original intact. Guarded so a prune failure can't abort the nightly commit/backup.
#
# ⚠️ MUST lower state/offsets/<file> by the lines removed BELOW the cursor. consolidate.sh
# reads each inbox from a saved cursor (see its "gather new events" loop); shrinking a file
# without fixing the cursor leaves it past EOF FOREVER, so that agent is never consolidated
# again — exactly what this phase caused fleet-wide on 2026-07-27 (incident found 2026-07-28:
# 9/11 offsets stranded, KB ingestion dead since 07:05Z).
# Do NOT assume every pruned line is inside the already-ingested prefix. It normally is
# (heartbeats older than HB_KEEP_DAYS=3d, consolidate runs hourly at :07 plus after every
# dispatch), but if consolidate has been down longer than HB_KEEP_DAYS the prune reaches
# lines the cursor never read, and subtracting those re-ingests real events as duplicates.
# mike_json.cursor_shift takes the line NUMBERS and counts only those at/below the cursor.
HB_KEEP_DAYS="${KB_HB_KEEP_DAYS:-3}"
HB_CUTOFF=$(python3 -c "import datetime; print((datetime.datetime.utcnow()-datetime.timedelta(days=$HB_KEEP_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
log "Pruning heartbeats older than $HB_CUTOFF (keep_days=$HB_KEEP_DAYS) from bus/inbox/*.jsonl..."
python3 - "$HB_CUTOFF" "$ROOT/bus/inbox" "$ROOT/state/offsets" "$ROOT/bin" <<'PYEOF' 2>&1 | tee -a "$LOG" || log "heartbeat-prune: python error (non-fatal, bus untouched)"
import sys, json, os, glob
cutoff_iso = sys.argv[1]   # ISO-8601 Zulu; ts field is same format → lexicographic compare is valid
inbox_dir = sys.argv[2]
offsets_dir = sys.argv[3]
sys.path.insert(0, sys.argv[4])
import mike_json            # the cursor format has exactly ONE owner — see cursor_shift()


def shift_offset(base, removed_idx):
    """Lower consolidate.sh's cursor by the lines deleted BELOW it. Passing the line
    NUMBERS rather than a bare count is what stops a prune that reaches past the cursor
    from over-subtracting and re-ingesting real events as duplicates."""
    moved = mike_json.cursor_shift(os.path.join(offsets_dir, base), removed_idx)
    if moved:
        print(f"    offset {base}: {moved[0]} → {moved[1]} ({len(removed_idx)} line(s) removed)")


total_removed = 0
for path in sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))):
    removed_idx = []                       # 1-based line numbers in the PRE-prune file
    kept = []
    with open(path, encoding="utf-8") as fh:
        for idx, line in enumerate(fh, 1):
            s = line.strip()
            if not s:
                kept.append(line)          # keep blank lines untouched
                continue
            try:
                ev = json.loads(s)
            except Exception:
                kept.append(line)          # never drop an unparseable line
                continue
            if ev.get("event_type") == "heartbeat":
                ts = ev.get("ts", "")
                if ts and ts < cutoff_iso:  # only drop OLD heartbeats
                    removed_idx.append(idx)
                    continue
            kept.append(line)
    if removed_idx:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as out:
            out.writelines(kept)
        os.replace(tmp, path)              # atomic
        total_removed += len(removed_idx)
        print(f"  {os.path.basename(path)}: pruned {len(removed_idx)} stale heartbeat(s)")
        shift_offset(os.path.basename(path), removed_idx)
print(f"HEARTBEAT-PRUNE: removed {total_removed} stale heartbeat(s) total")
PYEOF

# ── Phase 1b2: archive ALL old bus events (not just heartbeats) ───────────────
# Phase 1b only DROPS stale heartbeats. Everything else (finding/question/answer/decision/
# error/status/verification) accumulates forever in bus/inbox/*.jsonl (measured 2026-07-27:
# Taylor 5781 events / 3MB even after heartbeat prune). Move every event older than
# EVENT_KEEP_DAYS to a compressed, by-month-of-origin archive bus/inbox/archive/<id>_<YYYY-MM>
# .jsonl.gz — gzip members concatenate, so `gzip -dc` reads the whole history back. The hot
# file keeps only the recent window. Same offset rule as Phase 1b: this shrinks the hot file, so
# state/offsets/<file> must come down by the archived count too, else consolidate.sh stops ingesting
# that agent forever (incident 2026-07-28). Loss-safe: per file we assert (kept_events + archived ==
# original_events) and re-read the gz to confirm it decompresses BEFORE atomically replacing
# the hot file; on any mismatch/error that file is left untouched. Guarded so a failure can't
# abort the nightly commit.
EVENT_KEEP_DAYS="${KB_EVENT_KEEP_DAYS:-30}"
EVENT_CUTOFF=$(python3 -c "import datetime; print((datetime.datetime.utcnow()-datetime.timedelta(days=$EVENT_KEEP_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
log "Archiving bus events older than $EVENT_CUTOFF (keep_days=$EVENT_KEEP_DAYS) → bus/inbox/archive/*.jsonl.gz..."
python3 - "$EVENT_CUTOFF" "$ROOT/bus/inbox" "$ROOT/state/offsets" "$ROOT/bin" <<'PYEOF' 2>&1 | tee -a "$LOG" || log "event-archive: python error (non-fatal, bus untouched)"
import sys, json, os, glob, gzip
cutoff_iso = sys.argv[1]          # ISO-8601 Zulu; ts is same format → lexicographic compare valid
inbox_dir = sys.argv[2]
offsets_dir = sys.argv[3]
sys.path.insert(0, sys.argv[4])
import mike_json                  # single owner of the cursor format (see Phase 1b)
arch_dir = os.path.join(inbox_dir, "archive")


def shift_offset(base, removed_idx):
    """Keep consolidate.sh's cursor in step with the shrunken file (see Phase 1b). Same
    at-or-below-the-cursor rule: archiving lines the cursor never reached must not lower it."""
    moved = mike_json.cursor_shift(os.path.join(offsets_dir, base), removed_idx)
    if moved:
        print(f"    offset {base}: {moved[0]} → {moved[1]} ({len(removed_idx)} line(s) removed)")

def is_event(line):
    s = line.strip()
    if not s:
        return False
    try:
        json.loads(s); return True
    except Exception:
        return False

total_archived = 0
for path in sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))):
    base = os.path.basename(path)[:-6]        # strip ".jsonl"
    kept, buckets = [], {}                     # buckets: 'YYYY-MM' -> [raw lines]
    orig_events = 0
    archived_idx = []                          # 1-based line numbers in the PRE-archive file
    with open(path, encoding="utf-8") as fh:
        for idx, line in enumerate(fh, 1):
            if not is_event(line):
                kept.append(line); continue    # blank/unparseable → keep untouched
            orig_events += 1
            ev = json.loads(line)
            ts = ev.get("ts", "")
            if ts and ts < cutoff_iso:
                buckets.setdefault(ts[:7], []).append(line if line.endswith("\n") else line + "\n")
                archived_idx.append(idx)
            else:
                kept.append(line)
    if not buckets:
        continue
    n_arch = sum(len(v) for v in buckets.values())
    kept_events = sum(1 for l in kept if is_event(l))
    if kept_events + n_arch != orig_events:    # conservation guard — never lose
        print(f"  {base}: SKIP conservation FAIL (orig={orig_events} kept={kept_events} arch={n_arch})")
        continue
    os.makedirs(arch_dir, exist_ok=True)
    ok = True
    for ym, lines in sorted(buckets.items()):
        apath = os.path.join(arch_dir, f"{base}_{ym}.jsonl.gz")
        try:
            with gzip.open(apath, "at", encoding="utf-8") as gz:   # append as a new gzip member
                gz.writelines(lines)
            with gzip.open(apath, "rt", encoding="utf-8") as gz:   # verify it decompresses
                sum(1 for _ in gz)
        except Exception as e:
            print(f"  {base}: archive WRITE/VERIFY error on {ym} ({e}) — hot file left intact")
            ok = False; break
    if not ok:
        continue
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as out:
        out.writelines(kept)
    os.replace(tmp, path)                       # atomic hot-file swap
    total_archived += n_arch
    print(f"  {base}: archived {n_arch} event(s) across {len(buckets)} month(s), {kept_events} kept hot")
    shift_offset(os.path.basename(path), archived_idx)
print(f"EVENT-ARCHIVE: moved {total_archived} old event(s) total")
PYEOF

fi           # end SELFCHECK_OK guard (Phase 1b + 1b2)

exec 8>&-    # release consolidator lock — no phase below touches events_buffer.md or bus/inbox
fi           # end BUFFER_LOCK guard (Phase 1a + 1 + 1b + 1b2)

# ── Phase 1b3: archive old terminal job records ───────────────────────────────
# The dispatch job board (bus/jobs/<job_id>.json) accretes one record per dispatch (1178 as
# of 2026-07-27). Once a job is long finished the record is dead weight that slows every
# job-list/job-reap scan. Move records that are TERMINAL (done/failed/timeout — NOT running/
# orphaned/usage_limited, which may still need a reap or a pending-resume) AND older than
# JOB_KEEP_DAYS into bus/jobs/archive/ (plain .json, greppable/trace-able). jobs.sh list/reap
# glob bus/jobs/*.json non-recursively so the archive/ subdir is invisible to them — active
# jobs are unaffected (verified: mike_json cmd_job_list/reap use "*.json", not os.walk). Age
# uses ended_at (epoch) falling back to started_at. Move = os.rename (atomic, no content
# change; nothing deleted). 0 records qualify today (board starts ~2026-06-27) — this is the
# mechanism for when they age. Guarded non-fatal.
JOB_KEEP_DAYS="${KB_JOB_KEEP_DAYS:-30}"
log "Archiving terminal job records older than ${JOB_KEEP_DAYS}d → bus/jobs/archive/..."
python3 - "$JOB_KEEP_DAYS" "$ROOT/bus/jobs" <<'PYEOF' 2>&1 | tee -a "$LOG" || log "job-archive: python error (non-fatal, board untouched)"
import sys, os, json, glob, datetime
keep_days = int(sys.argv[1]); jobs_dir = sys.argv[2]
cutoff = datetime.datetime.utcnow().timestamp() - keep_days * 86400
arch_dir = os.path.join(jobs_dir, "archive")
TERMINAL = {"done", "failed", "timeout"}
moved = 0
for fp in glob.glob(os.path.join(jobs_dir, "*.json")):   # non-recursive; archive/ not matched
    try:
        j = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue                                          # unparseable → leave in place
    if j.get("status") not in TERMINAL:
        continue
    ts = j.get("ended_at") or j.get("started_at") or ""
    try:
        age_ok = float(ts) < cutoff
    except (TypeError, ValueError):
        continue                                          # no usable timestamp → keep (safe)
    if not age_ok:
        continue
    os.makedirs(arch_dir, exist_ok=True)
    dest = os.path.join(arch_dir, os.path.basename(fp))
    os.replace(fp, dest)                                  # atomic move, same filesystem
    moved += 1
print(f"JOB-ARCHIVE: moved {moved} terminal job record(s) older than {keep_days}d")
PYEOF

# ── Phase 1c: archive closed/old working-memory entries ───────────────────────
# Working memories (kb/memory/<id>.md) are reloaded on EVERY session/dispatch of that
# agent. Left alone they grow into full time-ordered job diaries (measured 2026-07-27:
# Wags 22KB/26 entries, Taylor 24KB) — 95% closed jobs already consolidated to bus/
# INCIDENTS/commits. Move settled episodic entries out to kb/memory/archive/<id>_history.md
# (append-only, NOT auto-loaded); nothing deleted. CONSERVATIVE mode (--require-done): an
# entry is archived ONLY if it is older than MEM_ARCHIVE_DAYS, is NOT among the last
# MEM_ARCHIVE_KEEP, carries a done marker (XONG/DONE/…), AND does NOT match the still-open /
# durable-rule regex baked into archive_memory.py. So only provably-closed old job-logs move;
# open work + standing rules stay hot. This also rescues entries from remember.sh's silent
# 40-bullet cap (which DROPS overflow) by relocating them before the cap is reached. Guarded
# so a failure can't abort the nightly commit/backup.
MEM_ARCHIVE_DAYS="${KB_MEM_ARCHIVE_DAYS:-14}"
MEM_ARCHIVE_KEEP="${KB_MEM_ARCHIVE_KEEP:-6}"
log "Archiving closed working-memory entries (>${MEM_ARCHIVE_DAYS}d, done-marked, keep last ${MEM_ARCHIVE_KEEP})..."
for f in "$ROOT/kb/memory/"*.md; do
    [ -f "$f" ] || continue
    python3 "$ROOT/bin/archive_memory.py" "$f" \
        --keep "$MEM_ARCHIVE_KEEP" --days "$MEM_ARCHIVE_DAYS" --require-done --apply \
        2>&1 | tee -a "$LOG" || log "mem-archive: error on $(basename "$f") (non-fatal, file untouched)"
done

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

# ── Phase 2b: nag on stale kb/*.proposed files (coding_guidelines.md §13, 2026-07-30) ─────────
# Reminder only, NOT a gate — a `.proposed` file is inert (no script reads it, consolidate.sh
# never sweeps it into the real file), so a forgotten one costs nothing except staying unapplied.
# mtime of the file itself is the "since when" marker; no separate state file needed.
STALE_PROPOSED=""
while IFS= read -r -d '' f; do
    age_h=$(( ( $(date -u +%s) - $(stat -c %Y "$f") ) / 3600 ))
    if [ "$age_h" -gt 24 ]; then
        STALE_PROPOSED="$STALE_PROPOSED ${f#$ROOT/}(${age_h}h)"
    fi
done < <(find "$ROOT/kb" -name "*.proposed" -print0 2>/dev/null)
if [ -n "$STALE_PROPOSED" ]; then
    log "STALE .proposed files (>24h, chưa áp dụng):$STALE_PROPOSED"
    "$ROOT/bin/notify.sh" "ℹ️ [kb_nightly] File .proposed chờ Mike duyệt >24h, chưa áp dụng:$STALE_PROPOSED — diff + mv nếu OK, hoặc xoá nếu không cần nữa." >/dev/null 2>&1 || true
fi

# ── Phase 3: commit if changed ────────────────────────────────────────────────
if git -C "$ROOT" diff --quiet && git -C "$ROOT" status --porcelain | grep -q .; then
    :  # new untracked files
fi
CHANGED=$(git -C "$ROOT" status --porcelain kb/ | wc -l)
if [ "$CHANGED" -gt 0 ]; then
    git -C "$ROOT" add kb/
    # `-- kb/` on commit too, for consistency with consolidate.sh's same fix (2026-07-28):
    # `add kb/` only controls what's staged HERE — commit with no pathspec commits the whole
    # index, so a file staged (or partially staged) by another in-flight session at the wrong
    # moment would still ride along. Lower-risk here (02:00 ICT, not hourly/post-dispatch),
    # but kept consistent so this isn't miscited as the safe pattern to copy elsewhere.
    git -C "$ROOT" commit -m "kb: nightly cleanup $(date -u +%Y-%m-%d) — archive+trim" \
        --author="Mike <mike@fleet>" -- kb/ || true
    log "Git committed."
else
    log "No KB changes to commit."
fi

# Backup
"$ROOT/bin/backup.sh" "kb_nightly $(date -u +%Y-%m-%d)" >> "$LOG" 2>&1 || true

# ── Phase 4: notify ──────────────────────────────────────────────────────────
MSG="🌙 KB nightly done ($(date -u +%Y-%m-%d))"
[ -n "${OVERSIZE:-}" ] && MSG="$MSG — ⚠️ oversized memories:$OVERSIZE"
[ -n "${PRUNE_WARN:-}" ] && MSG="$MSG — ⚠️ $PRUNE_WARN"
"$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
# Topic CỐ ĐỊNH (Architecture) — trước 2026-07-22 đọc con trỏ global
# state/ccdb_thread_id = "topic Mike mở phiên gần nhất", nên tin bảo trì KB đêm nào cũng
# rơi vào topic user vừa đọc, bất kể topic đó về việc gì.
_tid="1521475726329516122"
"$ROOT/bin/notify_thread.sh" "$MSG" "$_tid" 2>/dev/null || true

# ── Phase 4.5: weekly ops-vs-research spend trend (cost-opt #5, 2026-07-17) ──
# Deterministic, no LLM needed — just appends one row/week to state/spend_history.csv
# so the 4 optimizations made 2026-07-17 (context tiering, risk-tiered arch-review,
# batched research dispatch, model-config smoke-test) can be checked against real
# trend data instead of relying on a one-off manual count staying accurate forever.
python3 "$ROOT/bin/spend_report.py" --days 7 --csv-append "$ROOT/state/spend_history.csv" >> "$LOG" 2>&1 || true

# ── Phase 4.6: SAME-DAY context-bloat check (2026-07-30, user directive) ──────────────────────
# Root cause fixed: the hard-threshold check (context_pack.md 20KB / MIKE.md 40KB) only ran
# inside the Friday block below, so a breach on any other day sat unaddressed up to 6 days.
# Runs EVERY night now. SIMPLIFIED after arch-review NEEDS_CHANGES on the first draft: that
# version auto-dispatched a headless Mike EVERY breached non-Friday night with no post-condition
# check / rc=5(usage-limit) handling / cooldown — and the breach that same night was STRUCTURAL
# (context_pack.md ~38KB vs 20KB even after a careful trim pass, because canonical.md/
# projects/INDEX.md are evergreen must-know content, not compressible narrative) => would have
# treadmilled a real Mike session every non-Friday night indefinitely. This version only
# DETECTS + ESCALATES same-day (Telegram + Architecture topic + 1 bus `question`), debounced to
# one alert per open episode (stamp file, cleared once the breach shape changes or resolves) —
# a human/Mike-in-a-live-session does the actual edit, keeping a reviewer in the loop for the
# single most-injected file in the fleet (this exact file class already produced 2 real fact
# errors in past trims — see kb/INCIDENTS.md).
# POSTSCRIPT (same day, 2026-07-30): user accepted the 20KB context_pack.md target could not be
# hit without cutting real facts (canonical.md/projects/INDEX.md are evergreen, not prose to
# trim) -> threshold RAISED to 45KB below (MIKE.md stays 40KB, unchanged). Deep OKF-restructure
# of canonical.md is a separate follow-up, not required to land this mechanism.
_ctx_kb_or_missing() {  # "MISSING" beats silently reporting 0KB as healthy when the file is gone
    # -s (not -f): publish_context.sh:46 truncates-in-place (no tmp+rename), so a kill mid-write
    # leaves an EMPTY or TRUNCATED file, not a missing one — -f alone would silently treat that
    # as "0KB, healthy" (arch-review catch, 2026-07-30).
    [ -s "$1" ] || { echo "MISSING"; return; }
    echo $(( $(wc -c < "$1") / 1024 ))
}
_CP_KB=$(_ctx_kb_or_missing "$ROOT/kb/context_pack.md")
_MIKE_KB=$(_ctx_kb_or_missing "$ROOT/MIKE.md")
SAME_DAY_BREACH=""       # human-readable, WITH numbers — for the alert text/payload only
_BREACH_KEY=""           # stable membership key, NO numbers — debounce compares THIS
if [ "$_CP_KB" = "MISSING" ]; then
    SAME_DAY_BREACH="${SAME_DAY_BREACH}kb/context_pack.md MẤT/rỗng (publish_context.sh có thể đã chết); "
    _BREACH_KEY="${_BREACH_KEY}CP:MISSING|"
elif [ "$_CP_KB" -gt 45 ]; then
    SAME_DAY_BREACH="${SAME_DAY_BREACH}kb/context_pack.md=${_CP_KB}KB(ngưỡng 45KB); "
    _BREACH_KEY="${_BREACH_KEY}CP:OVER|"
fi
if [ "$_MIKE_KB" = "MISSING" ]; then
    SAME_DAY_BREACH="${SAME_DAY_BREACH}MIKE.md MẤT/rỗng; "
    _BREACH_KEY="${_BREACH_KEY}MIKE:MISSING|"
elif [ "$_MIKE_KB" -gt 40 ]; then
    SAME_DAY_BREACH="${SAME_DAY_BREACH}MIKE.md=${_MIKE_KB}KB(ngưỡng 40KB); "
    _BREACH_KEY="${_BREACH_KEY}MIKE:OVER|"
fi
mkdir -p "$ROOT/state"
_CTXBLOAT_STAMP="$ROOT/state/ctxbloat_episode.txt"
if [ -n "$SAME_DAY_BREACH" ]; then
    log "SAME-DAY CONTEXT-BLOAT: $SAME_DAY_BREACH"
    _prev="$(cat "$_CTXBLOAT_STAMP" 2>/dev/null || true)"
    if [ "$_prev" != "$_BREACH_KEY" ]; then
        # Debounce on WHICH FILE(S) breach, not the exact KB number — context_pack.md is
        # rewritten hourly by consolidate.sh and its size drifts a few KB within the same day,
        # so keying on the number would mint a "new" question every run and none would ever
        # resolve each other (ops_health_check.sh's stale-question matcher requires the
        # answer's topic to contain the question's topic verbatim) — arch-review catch.
        printf '%s' "$_BREACH_KEY" > "$_CTXBLOAT_STAMP"
        MSG="⚠️ [kb_nightly] SAME-DAY context-bloat: ${SAME_DAY_BREACH}Cần Mike/user xử lý HÔM NAY (không chờ Thứ Sáu) — xem kb/current_ops.md §Cron quan trọng khác."
        "$ROOT/bin/notify.sh" "$MSG" >/dev/null 2>&1 || true
        "$ROOT/bin/notify_thread.sh" "$MSG" "1521475726329516122" >/dev/null 2>&1 || true
        "$ROOT/bin/append_event.sh" Mike question "context-bloat-same-day" \
"Vượt ngưỡng cứng: ${SAME_DAY_BREACH}Phát hiện NGOÀI Thứ Sáu (kb_nightly.sh Phase 4.6, $(date -u +%Y-%m-%dT%H:%M:%SZ)). Xử lý SAME-DAY: nén thêm (chỉ cắt narrative, KHÔNG cắt fact quyết định — xem kb/coding_guidelines.md, bài học 2 lỗi fact đã lọt qua các lần trim trước). Nếu không xuống được ngưỡng mà không mất fact (đã từng đúng vậy 2026-07-30) — không tự nâng ngưỡng, hỏi user quyết nâng ngưỡng hay OKF-hoá sâu hơn kb/canonical.md." \
            2>/dev/null || true
        log "Escalated (new/changed episode)."
    else
        log "Same breach as last check -- đã escalate 1 lần cho đợt này, giữ im lặng tới khi đổi."
    fi
elif [ -f "$_CTXBLOAT_STAMP" ]; then
    rm -f "$_CTXBLOAT_STAMP"
    log "Context-bloat episode cleared."
fi

# ── Phase 5: Friday = LLM editorial review ──────────────────────────────────
DOW=$(date -u +%u)  # 1=Mon … 7=Sun; 5=Fri
if [ "$DOW" -eq 5 ]; then
    log "Friday → dispatching Mike for LLM editorial review of KNOWLEDGE.md..."
    # ── Context-file hard-threshold check (VIỆC 3, 2026-07-27) ────────────────
    # Deterministic size gate for the two files that load into EVERY Mike turn AND
    # EVERY dispatch. Over threshold → surface a clear warning in the review output
    # (logged + injected into the editorial prompt as an extra item). Do NOT auto-trim
    # — human/Mike decides what to archive. NOTE: MIKE.md is already >40KB as of
    # 2026-07-27, so this flags on the very first run BY DESIGN (wanted, not a bug).
    CTX_BLOAT_WARN=""
    ctx_check() {
        local f="$1" limit_kb="$2" label="$3"
        [ -f "$f" ] || return 0
        local kb=$(( $(wc -c < "$f") / 1024 ))
        if [ "$kb" -gt "$limit_kb" ]; then
            log "CONTEXT-BLOAT WARNING: $label = ${kb}KB > ${limit_kb}KB hard threshold"
            CTX_BLOAT_WARN="${CTX_BLOAT_WARN}
- ⚠️ $label = ${kb}KB (ngưỡng cứng ${limit_kb}KB) — VƯỢT ngưỡng, cần archive bớt."
        fi
    }
    ctx_check "$ROOT/kb/context_pack.md" 45 "kb/context_pack.md"
    ctx_check "$ROOT/MIKE.md" 40 "MIKE.md"
    if [ -n "$CTX_BLOAT_WARN" ]; then
        CTX_BLOAT_WARN="
8. **Context-bloat hard-threshold cảnh báo (VIỆC 3, 2026-07-27)** — các file dưới đây VƯỢT ngưỡng cứng và load vào MỌI turn Mike + MỌI dispatch. Đưa cảnh báo này RÕ RÀNG vào output review; **KHÔNG tự cắt nội dung** — để user/Mike quyết định phần nào archive:${CTX_BLOAT_WARN}"
    fi
    # ── Per-section STALE-by-AGE flag cho kb/current_ops.md (Wags 2026-07-28) ────
    # SONG SONG với ctx_check (ngưỡng cứng theo size) nhưng chiều KHÁC: phát hiện
    # TỪNG mục '## ...' đã im lặng quá lâu, thứ mục 7 (size+narrative chung) không
    # bắt được. Mục 7 GIỮ NGUYÊN — đây là bổ sung, không thay thế.
    # Cơ chế: với mỗi section, lấy NGÀY (YYYY-MM-DD) MỚI NHẤT xuất hiện trong nội
    # dung làm 'lần chạm cuối'. CHỈ tính ngày <= hôm nay: ngày tương lai trong nội
    # dung là DEADLINE/target (vd "tracking đến 2026-09-30", "trần ~2026-10-06"),
    # KHÔNG phải dấu thời gian chạm file — nếu lấy max() thô sẽ ra tuổi âm và che
    # mất mục thật sự cũ. Section KHÔNG có ngày cụ thể nào (Kill-switches, Cron,
    # daemon evergreen) → BỎ QUA, không flag (không phải quyết-định-theo-thời-điểm).
    # CHỈ phát hiện + liệt kê; KHÔNG tự archive — quyết định là judgment của Mike.
    STALE_SECTIONS_WARN=""
    if [ -f "$ROOT/kb/current_ops.md" ]; then
        TODAY_ISO=$(date -u +%Y-%m-%d)
        TODAY_EPOCH=$(date -u -d "$TODAY_ISO" +%s)
        while IFS=$'\t' read -r ldate title; do
            [ -n "$ldate" ] || continue
            d_epoch=$(date -u -d "$ldate" +%s 2>/dev/null) || continue
            age=$(( (TODAY_EPOCH - d_epoch) / 86400 ))
            if [ "$age" -gt 14 ]; then
                log "STALE-SECTION WARNING: current_ops.md '$title' im lặng ${age}d (ngày gần nhất=$ldate)"
                STALE_SECTIONS_WARN="${STALE_SECTIONS_WARN}
- ⚠️ **${title}** — ${age} ngày không chạm (ngày gần nhất trong mục: ${ldate})"
            fi
        done < <(awk -v today="$TODAY_ISO" '
            function scan(line,   s, d) {
                s = line
                while (match(s, /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/)) {
                    d = substr(s, RSTART, RLENGTH)
                    s = substr(s, RSTART + RLENGTH)
                    if (d <= today && (latest == "" || d > latest)) latest = d
                }
            }
            /^## / {
                if (title != "" && latest != "") print latest "\t" title
                title = substr($0, 4); latest = ""; scan($0); next
            }
            { scan($0) }
            END { if (title != "" && latest != "") print latest "\t" title }
        ' "$ROOT/kb/current_ops.md")
    fi
    if [ -n "$STALE_SECTIONS_WARN" ]; then
        STALE_SECTIONS_WARN="
9. **\`kb/current_ops.md\` — cờ mục IM LẶNG >14 ngày (phát hiện theo TUỔI, Wags 2026-07-28)** — các mục dưới đây có NGÀY GẦN NHẤT trong nội dung cách hôm nay hơn 14 ngày. Đây là danh sách CỜ tự động (chỉ phát hiện, KHÔNG tự archive — bổ sung cho mục 7 theo size). Với TỪNG mục, trả lời TƯỜNG MINH ngay trong review này — **không bỏ trống mục nào** (đoán sai = giấu mất quyết định thật đang treo, tệ hơn phình file): hoặc **'ĐÃ ĐÓNG → archive theo đúng mẫu \`kb/projects/<slug>.md\` + cập nhật \`kb/projects/INDEX.md\`, xoá section khỏi current_ops.md'**, hoặc **'VẪN MỞ → giữ nguyên, không đổi gì'** (mục evergreen/tham chiếu vận hành thường xuyên như workflow/onboarding thường thuộc loại này):${STALE_SECTIONS_WARN}"
    fi
    # DISPATCH_FROM=user required: dispatch.sh blocks any non-user caller from targeting
    # Mike (agents must escalate via a question event instead) AND blocks self-dispatch
    # (from==id). This cron job's default $from is "Mike" (dispatch.sh's own default),
    # which trips BOTH guards — found 2026-07-09 while setting up the daily retro: every
    # Friday since the guard was added (2026-06-27) this dispatch has silently failed
    # with "self-dispatch blocked (Mike -> Mike)" (confirmed in logs/kb_nightly.log,
    # 2026-07-03 run), and nobody noticed because it launches in background with `&`
    # and no exit-code check. DISPATCH_FROM=user is the documented human-override path.
    DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Mike \
"KB weekly editorial review (automated, Friday nightly).
Bạn đang ở headless mode. Nhiệm vụ:
1. Đọc kb/KNOWLEDGE.md, kiểm tra 9 canonical sections có còn đúng không (facts đã outdate, mục nào nên update từ events gần đây trong context_pack.md), viết lại những section cần thiết, commit.
2. Chạy '$ROOT/bin/data_registry_audit.sh --bus' (audit correctness+freshness của kb/data_registry/ — cấu trúc OKF, 1 nguồn = 1 file, migrate 2026-07-28; kb/data_registry.md giờ là stub redirect — user directive 2026-07-11, sau sự cố SIGNAL_V11 base-leak). Đọc output: FAIL = có regression thật (nguồn TRAP/DEAD bị đọc nhầm lại, hoặc writer chết) — PHẢI điều tra + escalate Winston/dispatch fix, KHÔNG bỏ qua. WARN = cần xem xét, ghi chú vào kb/data_registry/CHANGELOG.md nếu là false-positive đã biết. Cập nhật 'last_full_audit: <date>' ở frontmatter kb/data_registry/index.md dù kết quả clean/warn/fail.
3. Rà bất kỳ nguồn nào trong kb/data_registry/ (grep -rl 'status: DEPRECATED') đã đánh dấu status=DEPRECATED nhưng KHÔNG có dòng ⚠️ SUPERSEDED BY <nguồn mới> ON <date> — nếu thiếu, đó là vi phạm quy trình obsolete (xem 'Nguyên tắc bắt buộc' mục 5 trong kb/data_registry/index.md), cần bổ sung hoặc hỏi Winston.
4. Section D của audit script (stale-duplicate scan, coding_guidelines.md §10) liệt kê file variant đã confirm bị thay thế nhưng CHƯA archive — nếu WARN mới xuất hiện (khác danh sách đã biết), dispatch Winston verify + git mv vào archive/ theo đúng quy trình (không tự archive khi đang ở headless review, chỉ dispatch việc đó).
5. Đọc '$ROOT/state/spend_history.csv' (cost-opt #5, mỗi dòng = 1 tuần; cột *_h = giờ
compute thật — chỉ báo spend TỐT HƠN *_jobs, xem bài học sự cố model-drift 2026-07-17 dưới).
Nếu ops_h có xu hướng tăng liên tục qua ≥3 tuần gần nhất so với research_h (không phải 1 tuần
bất thường do sự cố đơn lẻ) — ghi nhận vào KNOWLEDGE.md + cân nhắc đề xuất thêm biện pháp tối
ưu (không tự làm gì thêm, chỉ ghi nhận + đề xuất cho user quyết).
5b. **Model-mix drift check (bài học sự cố 2026-07-17)**: cùng file, cột fable_jobs/(sonnet_
jobs+opus_jobs+fable_jobs+default_jobs). Sự cố thật: job count giảm 76% trong 3 tuần nhưng
compute TĂNG 150% vì %fable đi từ 0%→58% — chỉ đếm job/KB log đã KHÔNG bắt được, chỉ
'$ROOT/bin/spend_report.py' bản có model-mix mới bắt được. Nếu %fable tổng (mọi category)
≥30% ở tuần mới nhất → đọc lại các dispatch fable thật (bus/jobs, field prompt_summary) xem
có phải phần lớn là audit/fix routine (đáng lẽ Opus) hay thật sự \"cực kỳ phức tạp\" theo đúng
ladder MIKE.md §Model routing — ghi nhận vào KNOWLEDGE.md nếu lệch, không tự sửa thói quen
dispatch của Mike (đây là hành vi con người, không phải 1 lỗi code có thể fix 1 lần).
5c. **Opus-drift check (thêm 2026-08-01, user yêu cầu sau khi %fable=0% nhưng %opus âm thầm đi
từ ~14% (07-17) lên ~73% (07-31) — cùng dạng drift, khác tầng)**: cùng file, cột opus_jobs/
(sonnet_jobs+opus_jobs+fable_jobs+default_jobs) MỖI tuần trong toàn bộ file (không chỉ tuần mới
nhất). Flag nếu (a) opus% tuần mới nhất ≥60%, HOẶC (b) opus% tăng ≥20 điểm % so với 3 tuần trước
(drift bền vững, không phải 1 tuần đột biến do 1 việc đơn lẻ). Nếu flag: lấy mẫu 5-8 dispatch
opus gần nhất (bus/jobs/*.json field prompt/prompt_summary), tự hỏi ĐÚNG câu ladder MIKE.md
§Model routing đặt ra — \"task thực sự nặng, cần planning nhiều mới dùng Opus\" (Q2/Q3), hay là
việc cơ học/lookup/fix-1-script đáng lẽ Sonnet (Q1) nhưng bị chọn Opus theo phản xạ \"nghe có vẻ
quan trọng\"? Ghi nhận tỷ lệ lệch vào KNOWLEDGE.md nếu có — cùng nguyên tắc như 5b: đây là hành
vi con người (thói quen dispatch của Mike), không tự sửa thói quen, chỉ đo + báo cáo minh bạch
để Mike tự điều chỉnh. KHÔNG cần ngưỡng cảnh báo riêng cho sonnet/default (2 tầng đó rẻ nhất,
không phải nguồn drift chi phí).
6. Role-scoped context drift check (MIKE.md §Context theo vai trò, 2026-07-17): đọc
'$ROOT/kb/context_safety_core.md', 'context_execution_mini.md', 'context_planning_mini.md',
'context_dataops_mini.md' — đối chiếu với KNOWLEDGE.md/current_ops.md mới nhất. Fact nào đã
đổi ở nguồn canonical (account LIVE mới, đổi target NEUTRAL parking, đổi tên bảng DT5G, rule
mới ảnh hưởng thực thi/lập plan/data-ops) nhưng CHƯA lan sang (các) file role-scoped liên quan
→ sửa ngay, đúng file theo bảng trong MIKE.md (đừng sửa nhầm — fact riêng Mafee không thuộc
context_planning_mini.md và ngược lại).
7. **\`kb/current_ops.md\` bloat check (bài học sự cố context-bloat 2026-07-17 — file này phình
0→36KB trong 3 tuần, đè phí token lên MỌI dispatch qua context_pack.md; ngưỡng nâng 20→28KB
2026-07-30 sau khi context_pack.md tổng cũng nâng 20→45KB, xem kb/current_ops.md đầu file)**:
đọc kích thước file ('wc -c $ROOT/kb/current_ops.md'). Nếu >28KB HOẶC có mục nào mô tả 1 sự cố đã ghi rõ 'FIXED'/
'XONG'/'ĐÃ VÁ' + có pointer 'kb/incidents/' nhưng VẪN giữ nguyên narrative đầy đủ (thay vì
rút về 1-2 câu như quy ước ở đầu file current_ops.md) → rút gọn ngay theo đúng mẫu đã làm hôm
07-17 (giữ current-state + pointer kb/incidents/, xoá play-by-play đã có nơi khác lưu). CHỈ rút
gọn mục đã XÁC NHẬN đóng — mục còn 'CHỜ USER'/'chưa quyết' GIỮ NGUYÊN, không rút gọn nhầm việc
đang mở thành trông như đã xong.
10. **Token-saver skill audit** (thêm 2026-07-29, user yêu cầu): invoke Skill \`token-saver\`
(args: \`audit\`) — chạy đủ 6 mục checklist của nó (size-gate/hardcoded-drift/schedule-drift/
duplicate-content/ownership-scoped-import/fixed-per-call-overhead) trên toàn bộ
agents/*/CLAUDE.md + kb/*.md + bin/kb_nightly.sh + bin/dispatch.sh. Đây LÀ việc 1-9 ở trên
nhìn qua 1 lăng kính khác (không thay thế, bổ sung phát hiện các mục kia có thể bỏ sót — vd
schedule-drift từng lọt qua nhiều tuần vì không mục nào ở trên đối chiếu docs với \`crontab -l\`
thật). Finding có rủi ro cao (chạm 'ranh giới cứng' của skill — có thể làm sai lệch 1 fact
đang backing quyết định thật) → CHỈ báo cáo, KHÔNG tự sửa trong review này, để user/Mike xem lại
riêng; finding rủi ro thấp (đúng dedup/pointer thuần tuý) → sửa luôn như việc 1-6.
11. **Bus-question hygiene weekly accountability report** (thêm 2026-07-31, user mandate — \"đáng
lẽ phải làm hàng ngày, cuối tuần ít nhất phải có kiểm tra báo cáo lại đã hoàn thành chưa, không để
im im không quản lý\"). Daily surfacing ĐÃ có (\`bin/ops_health_check.sh\` check #5, 08:20+12:45,
top-5-cũ-nhất + \"…và N khác\") — việc NÀY là lớp accountability THIẾU: chạy
\`python3 $ROOT/bin/bus_question_audit.py\` (liệt kê ĐẦY ĐỦ, không cắt, quét cả hot inbox lẫn
archive — cùng thuật toán match đã hardening ở check #5, KHÔNG phải bản khác có thể lệch kết quả).
Với MỖI câu hỏi PENDING liệt kê: (a) nếu là quyết định Mike có thể tự quyết dựa trên KB/context
hiện có (không cần thẩm quyền user riêng, ví dụ câu hỏi kỹ thuật đã có đủ thông tin để trả lời) →
tự quyết NGAY trong review này, ghi answer + dispatch xuống agent đã hỏi nếu cần; (b) nếu thật sự
cần user quyết → GIỮ PENDING, liệt kê rõ trong báo cáo cuối kèm tuổi; (c) nếu đã lỗi thời/bị sự
kiện sau vượt qua (vd alert vận hành cho 1 ngày đã qua, plan ngày đó đã chạy xong) → ghi answer
\"SUPERSEDED — <lý do cụ thể>\" để đóng hình thức, KHÔNG bịa lý do nếu không chắc — chỉ đóng khi có
bằng chứng thật (grep KB/git log/bus xác nhận), câu nào không chắc thì để PENDING cho tuần sau.
Báo cáo cuối review PHẢI có: tổng số PENDING đầu review, số đã đóng tuần này (tách tự-quyết/
superseded), số CÒN LẠI kèm tuổi từng câu — post báo cáo này (không chỉ ghi bus) vào Architecture
channel qua \`bash $ROOT/bin/notify_thread.sh \"<báo cáo>\" 1521475726329516122\`. Đây LÀ cơ chế
\"cuối tuần kiểm tra báo cáo lại đã hoàn thành chưa\" user yêu cầu — KHÔNG được bỏ qua mục này dù
các mục 1-10 đã chiếm nhiều thời gian.
KHÔNG xóa archive. Không cần hỏi user cho việc 1-6, 10-11 — đây là routine maintenance đã được user uỷ quyền. Sau khi xong: notify Telegram, VÀ BẮT BUỘC (hợp đồng đầu ra máy đọc được — dispatch này chạy nền, không ai chờ trực tiếp, kb_nightly.sh thứ Bảy tự kiểm event này để phát hiện lạc đề/chết im, đúng NGUYÊN VĂN topic sau, không viết biến thể khác dù có vẻ tương đương): append_event.sh Mike decision 'kb-weekly-editorial' \"<JSON tóm tắt thay đổi>\".${CTX_BLOAT_WARN}${STALE_SECTIONS_WARN}" \
        --timeout 900 >> "$LOG" 2>&1 &
    log "Editorial dispatch launched (background)."
fi

log "=== kb_nightly DONE ==="
