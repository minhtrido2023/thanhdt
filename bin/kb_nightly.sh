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

# ── Phase 1b: prune stale heartbeats from bus inbox ───────────────────────────
# Heartbeats are liveness pings — useless once a job ends. They dominate bus/inbox
# (measured 2026-07-27: ~7.2K/8.7K lines fleet-wide, Taylor.jsonl 3MB with 88%
# heartbeat) and inflate every bus read. Drop event_type=="heartbeat" older than
# HB_KEEP_DAYS; keep EVERY other event_type (finding/question/answer/verification/
# decision/error/status/directive) and any unparseable/blank line untouched. Atomic
# per-file write (tmp + os.replace, coding_guidelines §5) so a mid-run kill leaves the
# original intact. Guarded so a prune failure can't abort the nightly commit/backup.
HB_KEEP_DAYS="${KB_HB_KEEP_DAYS:-3}"
HB_CUTOFF=$(python3 -c "import datetime; print((datetime.datetime.utcnow()-datetime.timedelta(days=$HB_KEEP_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
log "Pruning heartbeats older than $HB_CUTOFF (keep_days=$HB_KEEP_DAYS) from bus/inbox/*.jsonl..."
python3 - "$HB_CUTOFF" "$ROOT/bus/inbox" <<'PYEOF' 2>&1 | tee -a "$LOG" || log "heartbeat-prune: python error (non-fatal, bus untouched)"
import sys, json, os, glob
cutoff_iso = sys.argv[1]   # ISO-8601 Zulu; ts field is same format → lexicographic compare is valid
inbox_dir = sys.argv[2]
total_removed = 0
for path in sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))):
    removed = 0
    kept = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
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
                    removed += 1
                    continue
            kept.append(line)
    if removed:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as out:
            out.writelines(kept)
        os.replace(tmp, path)              # atomic
        total_removed += removed
        print(f"  {os.path.basename(path)}: pruned {removed} stale heartbeat(s)")
print(f"HEARTBEAT-PRUNE: removed {total_removed} stale heartbeat(s) total")
PYEOF

# ── Phase 1b2: archive ALL old bus events (not just heartbeats) ───────────────
# Phase 1b only DROPS stale heartbeats. Everything else (finding/question/answer/decision/
# error/status/verification) accumulates forever in bus/inbox/*.jsonl (measured 2026-07-27:
# Taylor 5781 events / 3MB even after heartbeat prune). Move every event older than
# EVENT_KEEP_DAYS to a compressed, by-month-of-origin archive bus/inbox/archive/<id>_<YYYY-MM>
# .jsonl.gz — gzip members concatenate, so `gzip -dc` reads the whole history back. The hot
# file keeps only the recent window. Loss-safe: per file we assert (kept_events + archived ==
# original_events) and re-read the gz to confirm it decompresses BEFORE atomically replacing
# the hot file; on any mismatch/error that file is left untouched. Guarded so a failure can't
# abort the nightly commit.
EVENT_KEEP_DAYS="${KB_EVENT_KEEP_DAYS:-30}"
EVENT_CUTOFF=$(python3 -c "import datetime; print((datetime.datetime.utcnow()-datetime.timedelta(days=$EVENT_KEEP_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
log "Archiving bus events older than $EVENT_CUTOFF (keep_days=$EVENT_KEEP_DAYS) → bus/inbox/archive/*.jsonl.gz..."
python3 - "$EVENT_CUTOFF" "$ROOT/bus/inbox" <<'PYEOF' 2>&1 | tee -a "$LOG" || log "event-archive: python error (non-fatal, bus untouched)"
import sys, json, os, glob, gzip
cutoff_iso = sys.argv[1]          # ISO-8601 Zulu; ts is same format → lexicographic compare valid
inbox_dir = sys.argv[2]
arch_dir = os.path.join(inbox_dir, "archive")

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
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not is_event(line):
                kept.append(line); continue    # blank/unparseable → keep untouched
            orig_events += 1
            ev = json.loads(line)
            ts = ev.get("ts", "")
            if ts and ts < cutoff_iso:
                buckets.setdefault(ts[:7], []).append(line if line.endswith("\n") else line + "\n")
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
print(f"EVENT-ARCHIVE: moved {total_archived} old event(s) total")
PYEOF

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
    ctx_check "$ROOT/kb/context_pack.md" 20 "kb/context_pack.md"
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
2. Chạy '$ROOT/bin/data_registry_audit.sh --bus' (audit correctness+freshness của kb/data_registry.md — user directive 2026-07-11, sau sự cố SIGNAL_V11 base-leak). Đọc output: FAIL = có regression thật (nguồn TRAP/DEAD bị đọc nhầm lại, hoặc writer chết) — PHẢI điều tra + escalate Winston/dispatch fix, KHÔNG bỏ qua. WARN = cần xem xét, ghi chú vào kb/data_registry.md 'Lịch sử' nếu là false-positive đã biết. Cập nhật dòng 'Last full audit: <date>' ở đầu file data_registry.md dù kết quả clean/warn/fail.
3. Rà bất kỳ nguồn nào trong data_registry.md đã đánh dấu Status=DEPRECATED nhưng KHÔNG có dòng ⚠️ SUPERSEDED BY <nguồn mới> ON <date> — nếu thiếu, đó là vi phạm quy trình obsolete (xem 'Nguyên tắc bắt buộc' mục 5 trong file), cần bổ sung hoặc hỏi Winston.
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
có phải phần lớn là audit/fix routine (đáng lẽ Opus) hay thật sự "cực kỳ phức tạp" theo đúng
ladder MIKE.md §Model routing — ghi nhận vào KNOWLEDGE.md nếu lệch, không tự sửa thói quen
dispatch của Mike (đây là hành vi con người, không phải 1 lỗi code có thể fix 1 lần).
6. Role-scoped context drift check (MIKE.md §Context theo vai trò, 2026-07-17): đọc
'$ROOT/kb/context_safety_core.md', 'context_execution_mini.md', 'context_planning_mini.md',
'context_dataops_mini.md' — đối chiếu với KNOWLEDGE.md/current_ops.md mới nhất. Fact nào đã
đổi ở nguồn canonical (account LIVE mới, đổi target NEUTRAL parking, đổi tên bảng DT5G, rule
mới ảnh hưởng thực thi/lập plan/data-ops) nhưng CHƯA lan sang (các) file role-scoped liên quan
→ sửa ngay, đúng file theo bảng trong MIKE.md (đừng sửa nhầm — fact riêng Mafee không thuộc
context_planning_mini.md và ngược lại).
7. **`kb/current_ops.md` bloat check (bài học sự cố context-bloat 2026-07-17 — file này phình
0→36KB trong 3 tuần, đè phí token lên MỌI dispatch qua context_pack.md)**: đọc kích thước file
('wc -c $ROOT/kb/current_ops.md'). Nếu >20KB HOẶC có mục nào mô tả 1 sự cố đã ghi rõ 'FIXED'/
'XONG'/'ĐÃ VÁ' + có pointer 'kb/INCIDENTS.md' nhưng VẪN giữ nguyên narrative đầy đủ (thay vì
rút về 1-2 câu như quy ước ở đầu file current_ops.md) → rút gọn ngay theo đúng mẫu đã làm hôm
07-17 (giữ current-state + pointer INCIDENTS.md, xoá play-by-play đã có nơi khác lưu). CHỈ rút
gọn mục đã XÁC NHẬN đóng — mục còn 'CHỜ USER'/'chưa quyết' GIỮ NGUYÊN, không rút gọn nhầm việc
đang mở thành trông như đã xong.
KHÔNG xóa archive. Không cần hỏi user cho việc 1-6 — đây là routine maintenance đã được user uỷ quyền. Sau khi xong: ghi sự thay đổi lên bus (append_event.sh Mike decision 'kb-weekly-editorial') và notify Telegram.${CTX_BLOAT_WARN}${STALE_SECTIONS_WARN}" \
        --timeout 900 >> "$LOG" 2>&1 &
    log "Editorial dispatch launched (background)."
fi

log "=== kb_nightly DONE ==="
