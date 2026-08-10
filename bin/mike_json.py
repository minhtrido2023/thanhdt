#!/usr/bin/env python3
"""Tiny JSON helper for the Mike fleet scripts.

Centralizes all JSON building/reading so the shell scripts depend only on python3
(already on the server) — no jq required. Subcommands:

  event <agent_id> <event_type> <topic> <payload> <kb_version>
      -> one JSONL line (adds uuid event_id + UTC ts; payload parsed as JSON or kept as string)
  heartbeat <agent_id> <current_task> <status>
      -> one registry JSON object
  recent <inbox_dir> [limit]
      -> markdown bullets of the latest finding/answer/decision events (newest first)
  format-events <jsonl_file>
      -> markdown bullets for every event in the file (for the KNOWLEDGE.md log)
  cursor-advance <inbox_jsonl> <state_file>
      -> print the not-yet-ingested lines and advance consolidate.sh's cursor. The cursor
         stores the last-read event_id+ts, not just a line count, so a head-prune that
         shifts the file is repaired by content instead of silently skipping events
  fleet-status <registry_dir>
      -> markdown fleet table; status shown as "dead" when last_heartbeat > 30 min old
  settings <hooks_dir> <agent_id>
      -> a child's .claude/settings.json wiring the 3 hooks
  circuit-check <state_dir> <agent_id>
      -> exit 0 (closed) / 1 (open) — per-agent dispatch circuit breaker
  circuit-record <state_dir> <agent_id> <success|fail> [threshold] [cooldown_sec]
      -> updates the counter; exit 1 if this call tripped the breaker
  pending-resume-set <path> <agent_id> <from> <orig_job_id> <resume_at_epoch> <resume_count>
                     [kind] [model] [effort] [max_turns]
      -> writes a bus/pending_resumes/<job_id>.json record; prompt text read from STDIN
         (avoids shell-quoting a large/multiline string as a CLI arg). kind defaults to
         "usage_limit" when omitted (back-compat with the original 6-arg call); the
         max-turns auto-continuation (2026-08-02) passes kind="max_turns" plus the
         model/effort to preserve on resume and the bumped max_turns to resume with.
  job-cancel <jobs_dir> <job_id> [grace_sec]
      -> stop a running job for real: kill its whole process tree, VERIFY it is dead, then
         stamp status=cancelled. Never stamps a status it cannot back up (no pid / survivors
         -> refuses, writes nothing). Front door: bin/jobs.sh cancel <job_id>
  job-field <jobs_dir> <job_id> <field_name>
      -> print one field's raw value (exit 1 if job/field missing) — e.g. discord_thread_id
  job-hb-age <jobs_dir> <job_id>
      -> seconds since the job's last AGENT-written bus event ('-' if none); excludes
         _job_watcher liveness pings — input to dispatch.sh heartbeat-aware deadline
  has-event <bus_dir> <agent_id> <since_iso> <event_type:topic> [...]
      -> exit 0 + print match if agent's inbox (hot+archive) has any of the given
         (event_type, topic) pairs since since_iso; exit 1 otherwise. Generic
         post-condition/"output contract" check for background-dispatch pipelines —
         see mike/kb/dispatch_output_contract.md.
"""
import sys, os, json, uuid, glob, datetime, hashlib, gzip, re, signal, time

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def now_iso():
    return now().strftime(TS_FMT)


def now_epoch():
    return int(now().timestamp())


def out(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(paths):
    """Đọc .jsonl thường VÀ .jsonl.gz (kb_nightly Phase 1b2 archive layout) trong suốt —
    caller chỉ cần đưa đúng đường dẫn, không cần biết file nào nén. Hành vi KHÔNG đổi cho
    caller chỉ truyền .jsonl thường (mọi caller hiện có trước 2026-08-01)."""
    rows = []
    for fp in paths:
        opener = gzip.open if fp.endswith(".gz") else open
        try:
            with opener(fp, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
        except (FileNotFoundError, OSError, EOFError):
            # OSError bắt hầu hết lỗi gzip (vd BadGzipFile ở open() nếu header hỏng); EOFError
            # RIÊNG vì nó KHÔNG phải subclass của OSError — đây là lỗi thật xảy ra khi stream bị
            # cắt cụt GIỮA CHỪNG lúc đang đọc (khác lỗi ở open()), bắt được bằng chính selfcheck
            # (mike_json_archive_selfcheck.py ca 6) khi viết xong, không phải đoán trước — cùng
            # nguyên tắc fail-safe đã dùng ở ops_health_check.sh check #5 (đừng chết cả lệnh vì
            # 1 file archive hỏng).
            pass
    return rows


# 2026-08-01 (audit kiến trúc fleet §14/committee — Fable plan + Opus critique): reader nào
# báo cáo trạng thái CÒN TREO (không chỉ hiển thị hoạt động gần đây) phải quét đủ mọi tầng
# lưu trữ mover có thể đặt dữ liệu vào — xem coding_guidelines.md §17. `cmd_trace` và
# `cmd_verify_coverage` từng chỉ glob hot inbox, mù với `bus/inbox/archive/*.jsonl.gz`
# (kb_nightly Phase 1b2) VÀ `bus/jobs/archive/*.json` (fleet_housekeeping Phase 1b3) — job/
# event nào cũ hơn ngưỡng archive sẽ âm thầm "không tìm thấy" thay vì báo rõ đã bị archive.
def _inbox_files(bus_dir):
    """Mọi file event của MỌI agent, hot + archive, đã sort theo tên (không theo ts — caller
    tự sort theo ts nếu cần thứ tự thời gian, file .jsonl.gz có thể chứa nhiều tháng)."""
    inbox_dir = os.path.join(bus_dir, "inbox")
    return (sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))) +
            sorted(glob.glob(os.path.join(inbox_dir, "archive", "*.jsonl.gz"))))


def _agent_files(bus_dir, agent_id):
    """File event của 1 agent cụ thể, hot + archive. Archive filename = <agent>_<YYYY-MM>.jsonl.gz
    (kb_nightly Phase 1b2) — match bằng prefix để không vô tình khớp agent khác có tên là
    prefix của agent này (vd "Wags" không được khớp "WagsX_2026-07.jsonl.gz")."""
    inbox_dir = os.path.join(bus_dir, "inbox")
    hot = [os.path.join(inbox_dir, agent_id + ".jsonl")]
    pat = re.compile(re.escape(agent_id) + r"_\d{4}-\d{2}\.jsonl\.gz$")
    arch = sorted(f for f in glob.glob(os.path.join(inbox_dir, "archive", "*.jsonl.gz"))
                  if pat.search(os.path.basename(f)))
    return hot + arch


def _job_record_path(bus_dir, job_id):
    """bus/jobs/<id>.json (hot) hoặc bus/jobs/archive/<id>.json (fleet_housekeeping Phase 1b3)
    — trả None nếu không thấy ở cả hai, để caller phân biệt được "archived" vs "chưa từng có"."""
    hot = os.path.join(bus_dir, "jobs", job_id + ".json")
    if os.path.exists(hot):
        return hot, False
    arch = os.path.join(bus_dir, "jobs", "archive", job_id + ".json")
    if os.path.exists(arch):
        return arch, True
    return None, False


# Verdict-prominent rendering for `verification` events (quant-skeptic output). MIKE.md
# codifies "REFUTED/INCONCLUSIVE = KHÔNG wire" as a hard team rule, but until now that verdict
# sat buried inside a raw JSON payload, indistinguishable at a skim from any other event in the
# feed that gets injected into every agent's context. A rule a human has to read carefully to
# not violate is a rule that gets violated under time pressure — surfacing the verdict as the
# first thing visible (not swept in JSON) is the same "ground truth over self-report" principle
# already applied to trading (verify artifact, not job status): don't make the reader dig.
_VERDICT_MARK = {"CONFIRMED": "✅ CONFIRMED", "REFUTED": "❌ REFUTED",
                  "INCONCLUSIVE": "⚠️ INCONCLUSIVE"}


def _verdict_prefix(e):
    if e.get("event_type") != "verification":
        return ""
    p = e.get("payload")
    v = p.get("verdict") if isinstance(p, dict) else None
    return (_VERDICT_MARK[v] + " ") if v in _VERDICT_MARK else ""


def fmt_event(e):
    p = e.get("payload")
    ps = p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)
    return "- [%s] %s/%s — %s%s: %s" % (
        e.get("ts", ""), e.get("agent_id", "?"), e.get("event_type", "?"),
        _verdict_prefix(e), e.get("topic", ""), ps,
    )


# Short one-liner for INJECTION (hooks/context_pack). Payload truncated hard —
# full detail lives in KNOWLEDGE.md. Keeps cross-agent injects ~140 chars/event
# instead of the 1–3 KB raw JSON blobs.
SHORT_CAP = 160


def short(e):
    p = e.get("payload")
    ps = p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)
    ps = " ".join(ps.split())
    if len(ps) > SHORT_CAP:
        ps = ps[:SHORT_CAP] + " …"
    return "- [%s] %s/%s — %s%s: %s" % (
        e.get("ts", "")[:19], e.get("agent_id", "?"), e.get("event_type", "?"),
        _verdict_prefix(e), e.get("topic", ""), ps,
    )


def cmd_event(a):
    aid, etype, topic, payload, kbver = a[:5]
    trace_id = a[5] if len(a) > 5 and a[5] else None
    try:
        p = json.loads(payload)
    except Exception:
        p = payload
    try:
        v = int(kbver)
    except Exception:
        v = 0
    e = {"event_id": str(uuid.uuid4()), "ts": now_iso(), "agent_id": aid,
         "event_type": etype, "topic": topic, "payload": p, "kb_version": v}
    if trace_id:
        e["trace_id"] = trace_id  # job_id of the dispatch this event was produced under,
                                   # when known — lets fleet_scout/session_brief follow one
                                   # dispatch chain (caller -> agent -> auto-callback) across
                                   # multiple bus events instead of only prompt_summary text.
    out(e)


def cmd_heartbeat(a):
    aid, task, status = a
    out({"agent_id": aid, "status": status, "current_task": task, "last_heartbeat": now_iso()})


def _as_int(s, default=0):
    try:
        return int(str(s).strip())
    except Exception:
        return default


def cmd_recent(a):
    """recent <delta_jsonl> [limit] — last N already-summarized lines for context_pack."""
    fp = a[0]
    limit = _as_int(a[1], 8) if len(a) > 1 else 8
    for r in load_jsonl([fp])[-limit:]:
        if r.get("line"):
            print(r["line"])


def cmd_delta_append(a):
    """delta-append <new_events_jsonl> <version> — emit {v,line} for each NEW event.
    The consolidator appends this to kb/recent_delta.jsonl, tagged with the version
    that ingested it, so the hook can serve each agent only what it hasn't seen."""
    ver = _as_int(a[1], 0)
    for e in load_jsonl([a[0]]):
        if e.get("event_type") in ("finding", "answer", "decision", "verification"):
            out({"v": ver, "line": short(e)})


def cmd_delta_since(a):
    """delta-since <delta_jsonl> <seen_version> [limit] — TRUE per-agent delta:
    only lines whose ingest-version > seen, chronological, capped."""
    fp = a[0]
    seen = _as_int(a[1], -1)
    limit = _as_int(a[2], 15) if len(a) > 2 else 15
    fresh = [r for r in load_jsonl([fp]) if _as_int(r.get("v"), -1) > seen and r.get("line")]
    for r in fresh[-limit:]:
        print(r["line"])


def cmd_format_events(a):
    for e in load_jsonl([a[0]]):
        print(fmt_event(e))


# ── consolidate.sh ingestion cursor ──────────────────────────────────────────
# A bare line-NUMBER cursor is only valid while the file it indexes never shifts.
# bus/inbox/*.jsonl DO shift: kb_nightly.sh Phase 1b/1b2 delete lines off the head.
# Two ways that loses events, both seen live:
#   (a) cursor left ABOVE the shrunken file -> `total > prev` false forever -> that agent
#       is never ingested again (fleet-wide 2026-07-27, 9/11 offsets stranded);
#   (b) the file REGROWS past the stale cursor before the next consolidate run -> the
#       comparison looks healthy and `tail -n +prev+1` silently LEAPFROGS every event
#       sitting between the new EOF and the stale cursor. That is how the quant-skeptic
#       verification at 2026-07-28T03:46:18Z vanished: prune 100->99 lines with the cursor
#       left at 100, file regrew to 101, so line 100 was never emitted.
# Case (b) is invisible to any pure-number check, so the cursor stores WHAT it last read
# (event_id + ts of that line), not just how many. If the marked event is no longer at the
# recorded line, we relocate it by content instead of trusting the number.
def _line_mark(raw):
    """(anchor, ts) of a raw JSONL line. ts is None when the line isn't parseable JSON.

    The anchor is the event_id when the line has one, else a hash of the raw line. It is
    NEVER None: a cursor anchored on None degrades straight back to a bare number on its
    next read, which is exactly the leapfrog this module exists to close (a handful of old
    bus events carry no event_id, and a torn line has none either)."""
    try:
        e = json.loads(raw)
        eid, ts = e.get("event_id"), e.get("ts")
    except Exception:
        eid, ts = None, None
    if not eid:
        eid = "raw:" + hashlib.sha1(raw.encode("utf-8", "replace")).hexdigest()[:16]
    return eid, ts


def _ambiguous_mark(anchor, lines):
    """True when a hash anchor names more than one line, i.e. the mark cannot identify WHICH
    line the cursor read. Two byte-identical anchor-less lines share their ts as well as their
    anchor, so no equality test can separate them: matching on the pair does NOT close this.
    The caller must refuse the fast path here and fall through to the resync scan, which
    resumes at the FIRST match and raises a repair — duplicates a human can see beat a silent
    skip of everything between the twins. Real event_ids are uuid4, so this only ever scans
    for a `raw:` anchor (a line the bus wrote without an event_id, or a torn one)."""
    if not str(anchor).startswith("raw:"):
        return False
    return sum(1 for raw in lines if _line_mark(raw)[0] == anchor) > 1


def _cursor_read(path):
    """-> (n, last_id, last_ts). Accepts the legacy bare-integer file (last_id=None), so an
    existing state/offsets/* keeps working and self-upgrades on its next write."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read().strip()
    except Exception:
        return 0, None, None
    if not raw:
        return 0, None, None
    if raw.startswith("{"):
        try:
            d = json.loads(raw)
            return _as_int(d.get("n"), 0), d.get("last_id"), d.get("last_ts")
        except Exception:
            return 0, None, None
    return _as_int("".join(c for c in raw if c.isdigit()), 0), None, None


def _cursor_write(path, n, last_id, last_ts):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"n": n, "last_id": last_id, "last_ts": last_ts}, f, ensure_ascii=False)
        os.replace(tmp, path)      # atomic — a kill mid-write can't truncate the cursor
    except Exception:
        try:
            os.remove(tmp)         # don't leave a half-written cursor lying in state/offsets
        except OSError:
            pass
        raise


def cursor_shift(state_path, removed_indices):
    """Lower a cursor after lines were DELETED from the file it indexes (kb_nightly.sh
    Phase 1b/1b2 import this — one owner of the cursor format, so a prune can never write
    a shape cursor-advance can't read).

    `removed_indices` are 1-based line numbers IN THE PRE-PRUNE FILE. Only lines the cursor
    had already passed may lower it: subtracting a deletion from BEYOND the cursor charges it
    for an event it never ingested, and the next run re-emits real events as DUPLICATES
    (reproduced 2026-07-28 — happens whenever consolidate has been down longer than
    HB_KEEP_DAYS, so the prune reaches lines the cursor hasn't reached yet).

    The content mark is deliberately left alone: it still names the same event, and if this
    arithmetic is ever wrong anyway, cursor-advance relocates it by id and reports a repair.
    Returns (old_n, new_n) if it moved, else None."""
    n, last_id, last_ts = _cursor_read(state_path)
    if n <= 0:
        return None
    passed = sum(1 for i in removed_indices if i <= n)
    if not passed:
        return None
    _cursor_write(state_path, max(0, n - passed), last_id, last_ts)
    return n, max(0, n - passed)


def cmd_cursor_advance(a):
    """cursor-advance <inbox_jsonl> <state_file>
    Print every line not yet ingested, then advance the cursor to EOF.

    stdout = the new raw JSONL lines (consolidate.sh appends them straight to its batch).
    stderr = one CURSOR-REPAIR line IFF the cursor had to be repaired — consolidate.sh
             turns that into a Discord notify + a bus error event, because the old code
             only echoed a WARN into a log file nobody reads.
    Resolution order, most trustworthy first:
      1. mark still sits at line n           -> fast path, no repair
      2. mark found at another line j        -> resume from j (exact, no loss, no dup)
      3. mark gone (its line was pruned)     -> resume at the first line that is NOT
         provably older than the mark, RE-EMITTING ts ties: a duplicate KB line is noise,
         a lost finding is unrecoverable
      4. legacy bare-int cursor (no mark)    -> trust the number, clamp it to EOF
    """
    inbox, state = a[0], a[1]
    try:
        with open(inbox, encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        return
    lines = raw.splitlines()
    if raw and lines and not raw.endswith("\n"):
        # The last line has no trailing newline: it is not a complete event, it's a write
        # caught mid-flight. append_event.sh's `printf '%s\n' "$line" >&9` is NOT one atomic
        # write() for a large line — strace shows a >4KB event split across two write()
        # syscalls (12288 + remainder) — and cursor-advance takes no lock against that write.
        # 149/2111 live events exceed 4KB; a live race test measured 19 torn reads in 153,676.
        # Drop it rather than anchor the cursor on it (arch-review round 5, 2026-07-28): an
        # anchor with last_ts=None is exactly what makes the resync-ts bound below fall back
        # to trusting `prev`, which is the failure mode this whole file exists to close.
        # Dropping it here means this run simply doesn't see it yet; once the writer finishes
        # (adds the trailing \n) a later run picks it up as a normal new line, no loss.
        lines = lines[:-1]
    total = len(lines)
    prev, last_id, last_ts = _cursor_read(state)
    repair = ""

    if prev <= 0:
        start = 0                                       # fresh file: ingest everything
    elif last_id is None and last_ts is None:
        start = min(prev, total)                        # legacy bare-int cursor: the number
        if prev > total:                                # is genuinely all we have
            repair = "clamp-legacy"
    elif (last_id is not None and prev <= total
          and _line_mark(lines[prev - 1]) == (last_id, last_ts)
          and not _ambiguous_mark(last_id, lines)):
        start = prev                                    # fast path — cursor still true
    else:
        # A cursor with a ts but no id is one an older build wrote before anchors were
        # mandatory; it must NOT fall back to the bare number (that silently reopens the
        # leapfrog), so it resolves by content here like any other stale cursor.
        start = None
        for j, raw in enumerate(lines, 1):              # (2) relocate the marked line
            if last_id is not None and _line_mark(raw)[0] == last_id:
                start = j
                repair = "resync-id"
                break
        if start is None:                               # (3) mark itself was pruned away
            # POSITIONAL scan, not a count: counting "lines older than the mark" treats an
            # unparseable/blank line ANYWHERE as already-read and shifts the resume point
            # past a real unread event (reproduced by arch-reviewer). Stop at the first line
            # that is not provably older — including a torn one, which is re-emitted rather
            # than skipped. This branch exists BECAUSE `prev` can no longer be trusted (the
            # mark it was meant to protect got pruned) — do not reintroduce that trust here.
            #
            # The ONLY situation worth bounding is "no age information at all" (last_ts is
            # None — e.g. a torn last line at cursor-write time), where the scan below would
            # otherwise start comparing from line 0 and replay the entire file (reproduced,
            # 2026-07-28: recovered=30 for a single torn line). Whenever last_ts IS present we
            # keep the full unbounded scan: an earlier version of this fix bounded that case
            # too (`prev` as a floor) and was proven wrong by a second independent review —
            # a prune that runs WITHOUT calling cursor_shift (the exact defect class this
            # whole redesign exists to survive; it is how the 2026-07-27 stranded-offset
            # incident happened) leaves `prev` overstating the true ingested prefix, and
            # trusting it as a lower bound silently skipped 100/150 real events in that repro
            # — with the repair line reporting recovered=0, making the loss invisible even to
            # a human reading it.
            scan_from = (min(prev, total) if prev < total else 0) if not last_ts else 0
            start = scan_from
            for j in range(scan_from, total):
                ts = _line_mark(lines[j])[1]
                if not ts or not last_ts or ts >= last_ts:   # ts="" is not evidence of age
                    start = j
                    break
            repair = "resync-ts"

    for raw in lines[start:]:
        print(raw)

    if repair:
        sys.stderr.write(
            "CURSOR-REPAIR %s %s prev=%s total=%s resume_from=%s recovered=%s\n"
            % (os.path.basename(inbox), repair, prev, total, start, max(0, prev - start)))
    if total != prev or repair or last_id is None:
        nid, nts = _line_mark(lines[-1]) if total else (None, None)
        # Payload MUST hit disk before the cursor advances (arch-review 2026-07-28) — stdout
        # here is redirected into consolidate.sh's $NEW file, block-buffered. Without this
        # flush, a SIGTERM between the print() above and the cursor write leaves the cursor
        # already advanced while $NEW is still empty: the events are gone, silently, with a
        # perfectly self-consistent cursor (no repair, no alert, no recovery). Flushing first
        # restores the old fail-safe direction: killed mid-write re-emits (duplicate, safe),
        # never drops.
        sys.stdout.flush()
        _cursor_write(state, total, nid, nts)


def cmd_fleet_status(a):
    reg_dir = a[0]
    n = now()
    rows = []
    for fp in sorted(glob.glob(os.path.join(reg_dir, "*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                r = json.load(f)
        except Exception:
            continue
        hb = r.get("last_heartbeat", "")
        age, disp = "?", r.get("status", "?")
        try:
            t = datetime.datetime.strptime(hb, TS_FMT).replace(tzinfo=datetime.timezone.utc)
            m = int((n - t).total_seconds() // 60)
            age = str(m)
            if m > 30:
                disp = "dead"
        except Exception:
            pass
        if disp == "dead" and m > 2880:  # hide sessions dead >48h
            continue
        rows.append((r.get("agent_id", "?"), r.get("title", r.get("agent_id", "?")),
                     r.get("kind", "child"), disp, hb, age,
                     r.get("current_task", "")))
    print("# Fleet status — %s UTC\n" % n.strftime("%Y-%m-%dT%H:%M:%S"))
    print("| agent | title (desktop) | kind | status | last_heartbeat | age(min) | current_task |")
    print("|---|---|---|---|---|---|---|")
    for row in rows:
        print("| %s | %s | %s | %s | %s | %s | %s |" % row)


# --- dispatch job board (bus/jobs/<job_id>.json) ---
# One file per dispatched headless job; lifecycle written by dispatch.sh, read by
# jobs.sh. All JSON building/reading stays here so the shell stays jq-free.

def _job_path(jobs_dir, job_id):
    return os.path.join(jobs_dir, job_id + ".json")


# Statuses that mean "this run is over" — used for ARCHIVAL classification only (see the
# terminal-statuses subcommand, which kb_nightly.sh and fleet_housekeeping.sh both read so
# the fleet keeps ONE definition instead of three divergent hardcoded lists).
TERMINAL_STATUSES = ("done", "failed", "timeout", "orphaned", "cancelled",
                     "aborted", "superseded")

# The ONLY statuses an outside writer may set on a job that is still running with a live
# process. Everything else is treated as "you are declaring this run over" and refused.
#
# This is an ALLOWLIST on purpose. The first version of this guard was a denylist of the
# 5 known death words, and arch-reviewer broke it in one try: `status=aborted` sailed
# straight through while the worker was still alive, and cmd_job_get maps every unknown
# word to exit 1 = "failed" to any poller — the exact signal that caused the 2026-08-09
# re-dispatch. That is not hypothetical; the live board already holds 6 hand-stamped
# records of that shape written with words no denylist anticipated: 'aborted' ×3
# (Taylor_20260804_024618, Taylor_20260804_012751, Taylor_20260806_025532), 'superseded'
# (Taylor_20260729_104438), 'cancelled' ×2 (Taylor_20260729_154952, Taylor_20260801_073402).
# Three are MORE RECENT than the incident this guard was written for. The operator's actual
# habit is inventing a status word, so the guard has to bound what is ALLOWED, not guess
# what will be invented.
LIVE_STATUSES = ("running", "retrying", "usage_limited", "provider_fallback",
                 "maxturns_pending")


def _ppid_of(pid):
    """Parent pid from /proc/<pid>/status, or None if unreadable/gone."""
    try:
        with open("/proc/%d/status" % int(pid), encoding="utf-8") as f:
            for line in f:
                if line.startswith("PPid:"):
                    return int(line.split()[1])
    except Exception:
        return None
    return None


def _is_self_or_ancestor(pid):
    """True if `pid` is THIS process or one of its ancestors.

    Distinguishes the job finalising its OWN record (dispatch.sh's _bg_wrapper runs as
    the recorded pid and JSETs status=done/failed from inside it — mike_json.py is then a
    descendant of that pid) from an OUTSIDE writer stamping a terminal status onto a job
    that is still running. Bounded walk; /proc chains are short."""
    try:
        pid = int(pid)
    except Exception:
        return False
    cur = os.getpid()
    for _ in range(64):
        if cur == pid:
            return True
        if cur <= 1:
            return False
        nxt = _ppid_of(cur)
        if nxt is None or nxt == cur:
            return False
        cur = nxt
    return False


def cmd_job_set(a, internal=False):
    """job-set <jobs_dir> <job_id> key=val [key=val ...] [--force] — merge fields, atomic write.
    Values kept as strings; numeric fields are coerced on read.

    REFUSES (exit 3) to stamp a TERMINAL status on a job that is still status=running while
    its recorded pid is provably ALIVE and the caller is not that process. Root cause of
    incident 2026-08-09 (Taylor_20260809_123917, 3rd duplicate-dispatch collision, the last
    one touching executor.py): Mike ran `kill <pid>` — which killed only the _bg_wrapper and
    left the setsid'd claude subtree orphaned but ALIVE — then `job-set status=failed`. The
    board said failed 22s into a 600s budget while the agent kept editing files for another
    33 minutes; Mike read "failed", re-dispatched the same prompt, and the two runs collided
    on the same files. Same anomalous record shape appears 5× in the board's history
    (2026-07-21 ×2, 07-31, 08-09 ×2): terminal status with no ended_at/exit_code.
    The correct way to stop a running job is `bin/jobs.sh cancel <job_id>` (kills the whole
    tree, VERIFIES it is dead, then stamps status=cancelled). --force keeps the escape hatch
    for a genuinely stale record whose pid has been recycled by an unrelated process."""
    force = "--force" in a[2:]
    jobs_dir, job_id = a[0], a[1]
    os.makedirs(jobs_dir, exist_ok=True)
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            obj = json.load(f)
    except Exception:
        obj = {}
    pairs = []
    for kv in a[2:]:
        if kv == "--force" or "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        # Sanitize: head -c may cut a multibyte sequence, producing surrogates.
        pairs.append((k, v.encode("utf-8", errors="replace").decode("utf-8")))
    fields = dict(pairs)
    new_status = fields.get("status")
    # Two ways to make the board lie about a job that is still working:
    #   closing — stamp a status that means "this run is over" (the 2026-08-09 write), or
    #   repid   — rewrite pid= to something dead, which was the 2-command way around the
    #             first version of this guard: `job-set pid=999999` then `job-set
    #             status=failed`, both rc=0 with the worker still alive (arch-reviewer S3).
    closing = new_status is not None and new_status not in LIVE_STATUSES
    # Only a REWRITE of an existing pid is suspicious. dispatch.sh:981 stamps pid= onto a
    # record that has none yet (`JSET pid="$BASHPID"`, the very first thing the wrapper does)
    # — guarding that would refuse every --bg job its own pid and hang the whole fleet at
    # status=running. There is nothing to protect when no pid is recorded.
    # `dispatcher_pid` is guarded alongside `pid` — it is an input to the ownership decision
    # below, so if it could be written on a live job the guard would be a 2-command bypass
    # again (point it at your own shell, then stamp).
    # But it is guarded MORE STRICTLY than `pid`, and the difference is the whole point:
    # `pid` legitimately arrives late (the wrapper stamps its own on a record that has none,
    # dispatch.sh:988), so only a REWRITE is suspicious there. `dispatcher_pid` is written
    # exactly once, by dispatch.sh, in the same job-set call that creates the record — there
    # is no legitimate later first-write. Allowing one would have handed the bypass to every
    # record already on the board, none of which carries the field yet.
    repid = ("pid" in fields and obj.get("pid") not in (None, "")
             and str(fields["pid"]) != str(obj.get("pid")))
    if ("dispatcher_pid" in fields and obj.get("status") is not None
            and str(fields["dispatcher_pid"]) != str(obj.get("dispatcher_pid"))):
        repid = True
    live = []
    guarded = False
    # Precondition is "the record still claims to be live", not "== running": a record in
    # retrying/usage_limited is just as live, and keying on 'running' alone left those
    # unprotected (arch-reviewer S4). The process discovery below walks /proc, so it runs
    # ONLY on a close/repid attempt — never on the ordinary field update — and the cheap
    # ancestry test short-circuits the wrapper finalising its own record before that.
    if (closing or repid) and obj.get("status") in LIVE_STATUSES \
            and not _is_self_or_ancestor(obj.get("pid")):
        live = _job_live_pids(obj)
        # Three ways to be a legitimate writer, cheapest first: the recorded pid is me or my
        # ancestor (--bg wrapper, tested above), I am one of the job's live processes or a
        # child of one (agent writing its own record), or I am the dispatcher that spawned
        # them (sync dispatch, which records no pid — MIKE_JOB_OWNER, /proc-verified).
        guarded = (bool(live) and not _writer_belongs_to_job(live)
                   and not _writer_is_job_dispatcher(job_id, obj))
    if guarded and internal:
        # cmd_job_reap calls this in-process; a sys.exit(3) here would abort the whole reap
        # loop and leave every later record unexamined. The caller checks the return value.
        return False
    if guarded and not force:
        if closing:
            what = "stamp status=%s" % new_status
        else:
            what = "rewrite " + ", ".join(
                "%s=%s" % (k, fields[k]) for k in ("pid", "dispatcher_pid")
                if k in fields and str(fields[k]) != str(obj.get(k)))
        sys.stderr.write(
            "REFUSED: job %s is still %s and %d process(es) of it are ALIVE right now: %s "
            "— refusing to %s (that is how the board starts lying; incident 2026-08-09).\n"
            "  NOTE the recorded pid %s is the _bg_wrapper. Killing it does NOT stop the "
            "worker: the worker runs under setsid, gets reparented to init, and keeps "
            "editing the repo — on 2026-08-09 it did so for 33 more minutes.\n"
            "  Stop it properly:  bin/jobs.sh cancel %s   (kills the whole tree, VERIFIES "
            "it is dead, then closes the record)\n"
            "  Just checking:     bin/jobs.sh status %s   (HB_AGE is the real liveness "
            "signal — LOG_AGE is useless while a job runs)\n"
            % (job_id, obj.get("status"), len(live), live, what, obj.get("pid"),
               job_id, job_id))
        sys.exit(3)
    if guarded and force:
        # --force exists for a genuinely stale record whose pid the OS handed to an
        # unrelated process. It must not be the cheap way to reproduce the very shape this
        # guard exists to stop, so a forced close has to carry the evidence a normal close
        # carries: all 6 anomalous records on the board are terminal-status-with-no-ended_at.
        if not fields.get("ended_at") or not fields.get("result_summary"):
            sys.stderr.write(
                "REFUSED: --force on a live job must also set ended_at= and result_summary= "
                "(say WHY you are overriding). Without them this writes exactly the "
                "terminal-status-without-ended_at record that made the board unreadable.\n"
                "  Example: job-set %s %s status=%s ended_at=$(date +%%s) "
                "result_summary='pid recycled, record stale since <when>' --force\n"
                % (jobs_dir, job_id, new_status or obj.get("status", "?")))
            sys.exit(3)
    for k, v in pairs:
        obj[k] = v
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, fp)
    return True


# Trang thai CHO TIEP TUC: lan chay nay da ket thuc, NHUNG viec chua chet — dispatch.sh da ghi
# bus/pending_resumes/<job>.json va resume_pending.py (cron 10') se dispatch lai thanh job MOI.
# Tach rieng vi truoc 2026-08-03 chung bi map thanh exit 1 = FAILED, khien nguoi/Mike doc job
# board tuong viec chet roi re-dispatch => nhan doi cong viec.
PENDING_RESUME_STATES = ("usage_limited", "maxturns_pending")


def _job_display_status(obj, n):
    """running + past deadline -> OVERDUE (soft flag; the hard timeout lives in dispatch.sh).
    usage_limited/maxturns_pending -> PENDING-RESUME (viec chua chet, se tu chay lai)."""
    st = obj.get("status", "?")
    if st == "running" and _as_int(obj.get("deadline"), 0) and n > _as_int(obj.get("deadline")):
        return "OVERDUE"
    if st in PENDING_RESUME_STATES:
        return "PENDING-RESUME"
    return st


def _log_age(obj, n):
    lf = obj.get("logfile", "")
    try:
        return str(n - int(os.stat(lf).st_mtime))
    except Exception:
        return "-"


def _is_watcher_event(rec):
    """dispatch.sh's _job_watcher appends a liveness ping every 60s with the SAME
    trace_id as the job. That ping only proves the WATCHER is alive — it fires
    unconditionally while the job record says 'running', even when the agent itself
    is hung. Any decision that means 'the agent is actually working' (heartbeat-aware
    deadline extension) must exclude these. Markers: explicit source=watcher (new),
    or the watcher's status=still_running payload shape (pre-marker records)."""
    p = rec.get("payload")
    if not isinstance(p, dict):
        return False
    return p.get("source") == "watcher" or p.get("status") == "still_running"


def _hb_age(obj, n, agent_only=False):
    """Giây từ HEARTBEAT bus cuối cùng của job (agent headless ghi heartbeat mỗi phút vào
    bus/inbox/<agent>.jsonl với trace_id=job_id). Đây mới là tín hiệu liveness ĐÚNG cho
    job đang chạy — LOG_AGE vô dụng khi chạy vì _bg_wrapper chỉ ghi log lúc claude THOÁT
    (log 0-byte suốt thời gian chạy → nhìn như treo dù agent sống; user hỏi 'Winston treo
    rồi phải không?' 2026-07-07 chính vì đọc LOG_AGE). '-' = chưa thấy heartbeat nào.
    agent_only=True: bỏ qua ping của _job_watcher (xem _is_watcher_event) — chỉ tính
    event do CHÍNH agent ghi; dùng cho quyết định gia hạn deadline."""
    job_id = obj.get("job_id", "")
    agent = obj.get("to", "")
    if not job_id or not agent:
        return "-"
    inbox = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "bus", "inbox", agent + ".jsonl")
    last_ts = None
    try:
        with open(inbox, encoding="utf-8") as f:
            for line in f:
                if job_id not in line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("trace_id") == job_id or rec.get("topic") == job_id:
                    if agent_only and _is_watcher_event(rec):
                        continue
                    last_ts = rec.get("ts") or last_ts
    except Exception:
        return "-"
    if not last_ts:
        return "-"
    try:
        import datetime as _dt
        t = _dt.datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        return str(n - int(t.timestamp()))
    except Exception:
        return "-"


def cmd_job_hb_age(a):
    """job-hb-age <jobs_dir> <job_id> — print seconds since the job's last AGENT-written
    bus event ('-' if none). Watcher liveness pings are excluded (see _is_watcher_event) —
    this is the input to dispatch.sh's heartbeat-aware deadline extension, where counting
    the watcher's own 60s ping would keep every hung job looking alive forever."""
    jobs_dir, job_id = a[0], a[1]
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            o = json.load(f)
    except Exception:
        print("-")
        return
    print(_hb_age(o, now_epoch(), agent_only=True))


def _load_jobs(jobs_dir):
    rows = []
    for fp in glob.glob(os.path.join(jobs_dir, "*.json")):
        try:
            with open(fp, encoding="utf-8") as f:
                rows.append(json.load(f))
        except Exception:
            pass
    rows.sort(key=lambda o: _as_int(o.get("started_at"), 0), reverse=True)
    return rows


def _proc_state(pid):
    """Single-letter state from /proc/<pid>/status ('R','S','D','Z','T'...), or None."""
    try:
        with open("/proc/%d/status" % int(pid), encoding="utf-8") as f:
            for line in f:
                if line.startswith("State:"):
                    return line.split()[1]
    except Exception:
        return None
    return None


def _pid_alive(pid):
    """True if the pid is still a live process, False if provably dead, None if unknown
    (no pid recorded — old records predating the pid field).

    A ZOMBIE counts as DEAD. `kill -0` succeeds on a zombie because the pid entry lingers
    until the parent reaps it, but the process has already exited: it holds no files and
    can write nothing. Found by this module's own selfcheck (case G) — without this, a
    wrapper whose parent is slow to wait() would look alive forever and `jobs.sh cancel`
    would refuse to close a job that had genuinely stopped."""
    if pid in (None, ""):
        return None
    try:
        pid = int(pid)
    except Exception:
        return None
    # pid<=0 is never a job: os.kill(0,...) signals THIS PROCESS GROUP and os.kill(-1,...)
    # signals every process the user may signal. Treat as dead so nothing downstream ever
    # takes such a value into a kill (arch-reviewer, 2026-08-10: _job_pids("0") resolved to
    # 146 pids including init, _job_pids("-1") to [-1] — `jobs.sh cancel` on a record with a
    # bad pid would have SIGKILLed the operator's whole session).
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True          # exists, owned by someone else
    except Exception:
        return None
    return _proc_state(pid) != "Z"


def cmd_job_reap(a):
    """job-reap <jobs_dir> [grace_sec] [--dry-run] — close ORPHANED job records.

    A job record stays status=running forever when its dispatcher dies between the
    fork and the completion write (headless `claude -p` caller exits, host restart,
    kill -9). Nobody ever writes the terminal status, so `jobs.sh list` accumulates
    zombies and a genuinely stuck job is invisible in the noise (incident 2026-07-19:
    Wags_20260719_173512 sat 'running' for 2 days unnoticed).

    Reaped only when BOTH hold, so a live-but-slow job is never touched:
      - deadline passed by more than grace_sec (default 3600), AND
      - the recorded pid is provably dead (or no pid was ever recorded).
    Sets status=orphaned + ended_at + result_summary; idempotent. Prints one line per
    reaped job; exit 0 always (report tool)."""
    jobs_dir = a[0]
    rest = [x for x in a[1:] if x != "--dry-run"]
    dry = "--dry-run" in a[1:]
    grace = _as_int(rest[0], 3600) if rest else 3600
    n = now_epoch()
    reaped = 0
    for o in _load_jobs(jobs_dir):
        if o.get("status") != "running":
            continue
        dl = _as_int(o.get("deadline"), 0)
        if not dl or n <= dl + grace:
            continue
        # Same job-level liveness the guard uses: a job whose wrapper died but whose worker
        # is still holding the logfile is NOT orphaned, it is running unattended — stamping
        # it 'orphaned' would be the board lying in the other direction.
        if _job_live_pids(o):
            continue
        # Only --bg dispatches record a pid; a sync dispatch has none, so fall back to the
        # agent's own heartbeat — a job still writing bus events is alive, never reap it.
        if not o.get("pid"):
            hb = _hb_age(o, n, agent_only=True)
            if hb != "-" and _as_int(hb, 10 ** 9) < grace:
                continue
        job_id = o.get("job_id")
        if not job_id:
            continue      # no id -> can't address the record safely; leave it alone
        over_h = (n - dl) / 3600.0
        if not dry:
            # compare-and-set: the snapshot above may be stale by seconds — if the wrapper
            # wrote a terminal status in the meantime, do NOT stamp 'orphaned' over it.
            try:
                with open(_job_path(jobs_dir, job_id), encoding="utf-8") as f:
                    if json.load(f).get("status") != "running":
                        continue
            except Exception:
                continue
        print("orphaned %-26s %s->%s  %.1fh past deadline" % (
            job_id, o.get("from", "?"), o.get("to", "?"), over_h))
        reaped += 1
        if not dry:
            # internal=True: the guard must not sys.exit() out of this loop and leave every
            # later record unexamined. A False return means a process appeared between the
            # check above and this write — then the job is alive and must not be reaped.
            if cmd_job_set([jobs_dir, job_id, "status=orphaned", "ended_at=%d" % n,
                            "result_summary=reaped by jobs.sh reap: dispatcher died without "
                            "writing a terminal status (%.1fh past deadline, pid dead/absent)"
                            % over_h], internal=True) is False:
                continue
            # watchdog's per-job debounce marker is dead weight once the record is closed
            om = os.path.join(os.path.dirname(jobs_dir.rstrip("/")), "..", "state", "overdue", job_id)
            try:
                os.remove(os.path.normpath(om))
            except Exception:
                pass
    print("%d orphaned job record(s)%s" % (reaped, " (dry-run, not written)" if dry else " closed"))


def cmd_terminal_statuses(a):
    """terminal-statuses — print the job statuses that mean "this run is over", one per line.

    ONE definition for the whole fleet. Before 2026-08-10 there were three hardcoded and
    divergent copies (kb_nightly.sh archival, fleet_housekeeping.sh log retention, this
    module), so a status the fleet actually writes — 'orphaned', 26 records on the board —
    was terminal to one consumer and non-terminal to another, and those records were never
    archived. Consumers read this instead of hardcoding a list."""
    for s in TERMINAL_STATUSES:
        print(s)


def cmd_job_find_dup(a):
    """job-find-dup <jobs_dir> <to_agent> <prompt_summary> — print job_ids of jobs to the
    SAME agent that are still status=running WITH A LIVE PID and carry an identical prompt
    summary. Exit 0 if any were printed, 1 if none.

    Advisory only — dispatch.sh warns and continues. This is the cheap, observable signature
    of the duplicate-dispatch pattern: 2 of its 3 collisions (2026-08-09 morning
    filter_lag_entry_window.py, afternoon executor.py) were the SAME prompt dispatched twice
    77s / 59s apart. Matching is exact on the normalized summary, not fuzzy, so a deliberate
    re-run with any edited wording stays silent rather than crying wolf."""
    jobs_dir, to_agent, summary = a[0], a[1], a[2]
    want = " ".join(summary.split()).lower()
    n = now_epoch()
    found = 0
    for o in _load_jobs(jobs_dir):
        if o.get("status") not in LIVE_STATUSES or o.get("to") != to_agent:
            continue
        # Prompt match FIRST: it is a string compare, while the liveness test below walks
        # /proc. This keeps the expensive scan to the handful of records that could actually
        # be a collision, instead of every running job on the board.
        if " ".join(str(o.get("prompt_summary", "")).split()).lower() != want:
            continue
        # Job-level liveness, not the recorded pid: after `kill <wrapper>` the worker is
        # still there and the collision is at its most dangerous (a live writer nobody is
        # pointing at) — reading the recorded pid alone made the warning go silent in
        # exactly that state (arch-reviewer round 2, K1b).
        if not _job_live_pids(o):
            continue
        print("%s (dispatched %ds ago by %s, hb_age=%ss)" % (
            o.get("job_id", "?"), n - _as_int(o.get("started_at"), n),
            o.get("from", "?"), _hb_age(o, n, agent_only=True)))
        found += 1
    sys.exit(0 if found else 1)


def _descendants(pid):
    """Every live descendant pid of `pid`, read from /proc (one pass, then a BFS over the
    parent map). Needed because dispatch.sh's child tree is deliberately detached: the
    _bg_wrapper runs in its own systemd transient scope and _hb_aware_timeout spawns claude
    under `setsid` (its own session + process group). So neither `kill <pid>` nor
    `kill -- -<pid>` from outside reaches the actual worker — killing the wrapper alone
    ORPHANS a claude that keeps editing the repo (incident 2026-08-09)."""
    try:
        pid = int(pid)
    except Exception:
        return []
    if pid <= 1:
        return []          # see _pid_alive: pid<=0 is a signal-group wildcard, 1 is init
    kids = {}
    try:
        entries = os.listdir("/proc")
    except Exception:
        return []
    for entry in entries:
        if not entry.isdigit():
            continue
        p = int(entry)
        pp = _ppid_of(p)
        if pp is not None:
            kids.setdefault(pp, []).append(p)
    out, seen, stack = [], set(), [int(pid)]
    while stack:
        for k in kids.get(stack.pop(), []):
            if k in seen:
                continue
            seen.add(k)
            out.append(k)
            stack.append(k)
    return out


def _pids_holding(path):
    """Pids whose stdout/stderr is `path`, found by reading /proc/<pid>/fd.

    The SECOND way to find a job's worker, and the one that still works after the wrapper
    is gone. dispatch.sh's _bg_wrapper redirects the claude process's stdout+stderr to the
    job's own logfile (`_hb_aware_timeout ... > "$logfile" 2>&1`), so that fd is a reliable
    per-job fingerprint. It matters because the PPid tree is NOT enough on its own: once the
    wrapper dies, its setsid'd claude child is reparented to init and becomes invisible to
    _descendants — which is exactly the state Mike's improvised `kill <pid>` left behind on
    2026-08-09, an orphan that went on editing the repo for 33 minutes with nothing pointing
    at it."""
    if not path:
        return []
    out = []
    try:
        entries = os.listdir("/proc")
    except Exception:
        return []
    me = os.getpid()
    for entry in entries:
        if not entry.isdigit():
            continue
        p = int(entry)
        if p == me:
            continue
        for fd in ("1", "2"):
            try:
                if os.readlink("/proc/%d/fd/%s" % (p, fd)) == path:
                    out.append(p)
                    break
            except Exception:
                continue
    return out


def _job_pids(pid, logfile):
    """Every live process belonging to this job: the wrapper, its descendants, and any
    process still holding the job's logfile (orphans the tree walk cannot see)."""
    seen, out = set(), []
    cands = _descendants(pid) + _pids_holding(logfile)
    if _pid_alive(pid) is True:
        cands.insert(0, int(pid))
    for p in cands:
        if p in seen or p <= 1 or _pid_alive(p) is not True:
            continue
        seen.add(p)
        out.append(p)
    return out


def _job_live_pids(obj):
    """Every live process belonging to this job RECORD (recorded pid + its descendants +
    anything still holding the job's logfile).

    The liveness question has to be asked about the JOB, not about the recorded pid. The
    recorded pid is dispatch.sh's _bg_wrapper; the worker runs under `setsid` and outlives
    it. The 2026-08-09 incident is precisely the composition of those two facts — Mike ran
    `kill <pid>` FIRST, then stamped status=failed — so a guard that reads only the recorded
    pid is asking about the one process the improvisation already killed, and waves the
    stamp through while the worker keeps editing the repo (arch-reviewer round 2, K1)."""
    logfile = obj.get("logfile", "")
    pids = _job_pids(obj.get("pid"), logfile)
    if logfile:
        # A SYNC dispatch pipes the worker's stdout (`... 2>"$logfile.err" | tee "$logfile"`,
        # dispatch.sh:1266), so its fd1 is a PIPE and only fd2 points at a real file. Looking
        # at logfile alone finds nothing for the fleet's DEFAULT dispatch mode (arch-reviewer
        # round 3, N2).
        seen = set(pids)
        for p in _pids_holding(logfile + ".err"):
            if p not in seen and p > 1 and _pid_alive(p) is True:
                seen.add(p)
                pids.append(p)
    return pids


def _writer_belongs_to_job(pids):
    """True if THIS process is one of `pids` or a descendant of one — i.e. the job writing
    its own record, which is always legitimate. Complements _is_self_or_ancestor (which only
    knows the recorded pid) for the case where the wrapper is gone but the worker is not."""
    try:
        want = set(int(p) for p in pids)
    except Exception:
        return False
    cur = os.getpid()
    for _ in range(64):
        if cur in want:
            return True
        if cur <= 1:
            return False
        nxt = _ppid_of(cur)
        if nxt is None or nxt == cur:
            return False
        cur = nxt
    return False


def _writer_is_job_dispatcher(job_id, obj):
    """True if THIS process is running INSIDE the dispatch.sh that owns `job_id` — the one
    writer besides the worker itself that is entitled to close the record.

    Why it is needed at all: the fleet's DEFAULT dispatch mode is SYNCHRONOUS, and a sync
    dispatch records NO pid (`JSET pid=$BASHPID` lives in _bg_wrapper only). So
    `_is_self_or_ancestor(obj["pid"])` has nothing to test; and the worker is a SIBLING of
    this job-set process (dispatch.sh spawns both), which `_writer_belongs_to_job` cannot
    see because it only walks UPWARD. Once _job_live_pids learned to find the sync worker
    through `$logfile.err`, every sync job would have been refused its own final
    status=done/timeout and left stuck at running forever.

    Both halves are required, and NEITHER is taken on trust:
      * `dispatcher_pid` comes off the RECORD, written by dispatch.sh when it created the
        job — before any later writer exists to influence it — and is protected from being
        rewritten on a live job by the same rule that protects `pid` (see `repid` below).
        `_is_self_or_ancestor` then proves against /proc that the caller really is inside
        that process tree. An improvised `job-set` typed into a separate Bash tool call is
        NOT a descendant of that dispatch.sh, so the 2026-08-09 write stays refused.
      * MIKE_JOB_OWNER (env, set at dispatch.sh's JSET call site) must name THIS job. It is
        deliberately NOT evidence on its own — an env var is free to forge, and believing it
        would delete the guard. It is the narrowing term: being somewhere inside a
        dispatcher tree must not become a skeleton key for whatever other live record that
        tree happens to be an ancestor of (nested dispatches make that reachable)."""
    if not job_id or os.environ.get("MIKE_JOB_OWNER") != job_id:
        return False
    dp = obj.get("dispatcher_pid")
    if dp in (None, ""):
        return False
    return _is_self_or_ancestor(dp)


def _boot_epoch():
    """Wall-clock epoch of the last boot, from /proc/stat btime."""
    try:
        with open("/proc/stat", encoding="utf-8") as f:
            for line in f:
                if line.startswith("btime "):
                    return int(line.split()[1])
    except Exception:
        return None
    return None


def _proc_start_epoch(pid):
    """Wall-clock epoch at which `pid` started (field 22 of /proc/<pid>/stat + btime), or
    None if unreadable. comm (field 2) may contain spaces AND ')' so the tail is split from
    the LAST ')' — field 22 is then index 19."""
    b = _boot_epoch()
    if b is None:
        return None
    try:
        with open("/proc/%d/stat" % int(pid), encoding="utf-8") as f:
            data = f.read()
        tail = data[data.rindex(")") + 2:].split()
        return b + int(tail[19]) / float(os.sysconf("SC_CLK_TCK") or 100)
    except Exception:
        return None


def _fmt_ts(ts):
    """UTC 'YYYY-MM-DD HH:MM:SSZ' for an operator-facing message, or '?'. UTC on purpose:
    the fleet's crons run under several TZs and the same record must read identically."""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(float(ts)))
    except Exception:
        return "?"


# How far a job's process may have started from the job's own started_at and still be
# believed to be that job's process. dispatch.sh forks the wrapper within a second or two of
# writing started_at; 5 minutes is slack for a loaded host, not a real ambiguity.
PID_OWNERSHIP_SLACK = 300


def _pid_owned_by_job(pid, obj):
    """True if `pid` plausibly IS this job's process rather than an unrelated process the
    kernel handed the same number to after the job died.

    Pid recycling is not hypothetical — it is the stated reason `--force` exists. Without
    this check `jobs.sh cancel` signals whatever currently owns the number: arch-reviewer
    measured an unrelated `sleep` SIGKILLed by a cancel on a stale record, and on this host
    that could as easily have been run_bot.sh or the Discord bridge.

    Ownership is accepted on ANY of three signals, cheapest first, and the check FAILS OPEN
    when it cannot see enough to disprove ownership (a refusal that blocks a real cancel is
    also a failure mode)."""
    holders = set(_pids_holding(obj.get("logfile", "")))
    try:
        pid_i = int(pid)
    except Exception:
        return False
    if holders and (pid_i in holders or holders & set(_descendants(pid_i))):
        return True          # holds the job's own logfile, or fathers something that does
    started = _as_int(obj.get("started_at"), 0)
    st = _proc_start_epoch(pid_i)
    if st is None or not started:
        return True          # cannot disprove -> do not block the operator
    return abs(st - started) <= PID_OWNERSHIP_SLACK


def _kill_tree(pid, logfile, grace):
    """SIGTERM everything belonging to the job, wait up to `grace`, SIGKILL what survives.
    Returns the pids STILL alive afterwards (empty == fully dead).

    Re-collects before every signal pass: a process spawned between listing and signalling
    would be missed by a single pass, and this must not leave a live writer behind — the
    whole point of the command is that the status stamped afterwards is TRUE."""
    still = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for _round in (1, 2):
            for p in reversed(_job_pids(pid, logfile)):   # children first, don't orphan mid-kill
                try:
                    os.kill(p, sig)
                except Exception:
                    pass
        waited = 0.0
        step = 0.5 if sig == signal.SIGKILL else 1.0
        limit = 2.0 if sig == signal.SIGKILL else float(grace)
        while True:
            still = _job_pids(pid, logfile)
            if not still:
                return []
            if waited >= limit:
                break
            time.sleep(step)
            waited += step
    return still


def cmd_job_cancel(a):
    """job-cancel <jobs_dir> <job_id> [grace_sec] — stop a running job FOR REAL.

    Kills the job's whole process tree, VERIFIES every pid is dead, and only then stamps
    status=cancelled. This exists because there was no cancel primitive at all: on
    2026-08-09 Mike improvised `kill <pid>` + `job-set status=failed`, and both halves were
    wrong — the kill hit only the wrapper (the setsid'd claude survived 33 more minutes,
    still editing executor.py), and the status stamp made the board claim a failure that
    never happened, which triggered the re-dispatch that collided with the still-live run.

    Never stamps a status it cannot back up. Exit codes are distinct so a caller can tell a
    typo from a live writer that refused to die:
      0 - cancelled (or already terminal — idempotent)
      3 - cannot act: no pid recorded (sync dispatch), pid<=1, or cancelling own job
      4 - job record not found
      5 - process(es) SURVIVED SIGTERM+SIGKILL; record deliberately left at running"""
    jobs_dir, job_id = a[0], a[1]
    grace = _as_int(a[2], 15) if len(a) > 2 else 15
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            o = json.load(f)
    except Exception:
        print("not-found: %s" % job_id)
        sys.exit(4)
    st = o.get("status", "?")
    if st != "running":
        print("job %s is already %s — nothing to cancel" % (job_id, st))
        sys.exit(0)
    pid = o.get("pid")
    if not pid:
        sys.stderr.write(
            "REFUSED: job %s has no recorded pid (sync dispatch — only --bg records one), "
            "so this command cannot prove it killed anything.\n"
            "  Kill it in the shell that is running it, then: bin/jobs.sh status %s\n"
            % (job_id, job_id))
        sys.exit(3)
    try:
        _pid_int = int(pid)
    except Exception:
        _pid_int = 0
    if _pid_int <= 1:
        sys.stderr.write(
            "REFUSED: job %s has a nonsensical pid (%r). Refusing to run process discovery "
            "on it — pid 0 means 'this process group', a negative pid means 'every process "
            "I may signal', and 1 is init.\n"
            "  Fix the record instead: bin/mike_json.py job-set %s %s status=orphaned "
            "ended_at=$(date +%%s) result_summary='<why>' --force\n"
            % (job_id, pid, jobs_dir, job_id))
        sys.exit(3)
    if _is_self_or_ancestor(pid):
        sys.stderr.write(
            "REFUSED: you are running INSIDE job %s (pid %s is this process or an ancestor) "
            "— cancelling it would kill this very command.\n" % (job_id, pid))
        sys.exit(3)
    # OWNERSHIP, before the first signal and before _descendants() enumerates anything: the
    # kernel recycles pids, and a stale record's number may now belong to an unrelated live
    # process — arch-reviewer measured an innocent process SIGKILLed here, and its children
    # would have gone with it. Only checked when the recorded pid is alive; a dead recorded
    # pid cannot be mistaken for anything, and orphans are found by logfile fd, which IS
    # proof of ownership.
    if _pid_alive(pid) is True and not _pid_owned_by_job(pid, o):
        sys.stderr.write(
            "REFUSED: pid %s is alive but does NOT look like job %s's process — it holds "
            "none of the job's logfile and it started %s, while the job started %s. The "
            "kernel recycles pids; killing this would hit an unrelated process.\n"
            "  If the record really is stale, close it without killing anything:\n"
            "    bin/mike_json.py job-set %s %s status=orphaned ended_at=$(date +%%s) "
            "result_summary='pid recycled, record stale' --force\n"
            % (pid, job_id, _fmt_ts(_proc_start_epoch(pid)),
               _fmt_ts(_as_int(o.get("started_at"), 0)), jobs_dir, job_id))
        sys.exit(3)
    logfile = o.get("logfile", "")
    targets = _job_pids(pid, logfile)
    if targets:
        print("killing %s: %d live process(es) %s" % (job_id, len(targets), targets))
        survivors = _kill_tree(pid, logfile, grace)
        if survivors:
            sys.stderr.write(
                "REFUSED to stamp cancelled: %d process(es) SURVIVED SIGTERM+SIGKILL: %s.\n"
                "  The job record is left at status=running ON PURPOSE — a live writer must "
                "never be reported as stopped.\n" % (len(survivors), survivors))
            sys.exit(5)
        note = "cancelled by operator: %d process(es) killed and verified dead" % len(targets)
    else:
        note = ("cancelled by operator: no live process found (recorded pid %s dead, nothing "
                "holding the job's logfile) — dispatcher died without a terminal status" % pid)
    print(note)
    cmd_job_set([jobs_dir, job_id, "status=cancelled", "ended_at=%d" % now_epoch(),
                 "exit_code=130", "result_summary=" + note])
    # watchdog's per-job OVERDUE debounce marker is dead weight once the record is closed
    om = os.path.join(os.path.dirname(jobs_dir.rstrip("/")), "..", "state", "overdue", job_id)
    try:
        os.remove(os.path.normpath(om))
    except Exception:
        pass


def cmd_job_list(a):
    """job-list <jobs_dir> [limit] — recent jobs, newest first, with computed ages."""
    jobs_dir = a[0]
    limit = _as_int(a[1], 20) if len(a) > 1 else 20
    n = now_epoch()
    rows = _load_jobs(jobs_dir)[:limit]
    print("%-26s %-18s %-9s %6s %7s %7s %4s" % ("JOB_ID", "FROM->TO", "STATUS", "AGE", "LOG_AGE", "HB_AGE", "ATT"))
    for o in rows:
        age = n - _as_int(o.get("started_at"), n)
        # HB_AGE chỉ có nghĩa cho job đang chạy — job đã kết thúc in '-' cho đỡ tốn I/O.
        hb = _hb_age(o, n) if o.get("status") == "running" else "-"
        print("%-26s %-18s %-9s %5ss %6ss %6ss %2s/%s" % (
            o.get("job_id", "?")[:26],
            ("%s->%s" % (o.get("from", "?"), o.get("to", "?")))[:18],
            _job_display_status(o, n)[:9],
            age, _log_age(o, n), hb,
            o.get("attempt", "?"), o.get("max_attempts", "?"),
        ))


def cmd_trace(a):
    """trace <bus_dir> <trace_id> — every bus event (any agent's inbox, hot HOẶC archive)
    sharing this trace_id (= a dispatch job_id, by convention), sorted chronologically.
    Prints the job record first (hot HOẶC bus/jobs/archive/). Exit 1 if no events found."""
    bus_dir, trace_id = a[0], a[1]
    jobs_fp, jobs_archived = _job_record_path(bus_dir, trace_id)
    if jobs_fp:
        try:
            with open(jobs_fp, encoding="utf-8") as f:
                jo = json.load(f)
            print("=== job %s%s ===" % (trace_id, " (archived)" if jobs_archived else ""))
            for k in ("from", "to", "status", "started_at", "ended_at", "exit_code", "logfile"):
                if k in jo:
                    print("%-12s %s" % (k + ":", jo[k]))
            print()
        except Exception:
            pass
    events = [e for e in load_jsonl(_inbox_files(bus_dir)) if e.get("trace_id") == trace_id]
    events.sort(key=lambda e: e.get("ts", ""))
    if not events:
        print("no bus events found with trace_id=%s (đã quét cả bus/inbox/archive/*.jsonl.gz)"
              % trace_id)
        sys.exit(1)
    for e in events:
        print(fmt_event(e))


def cmd_verify_coverage(a):
    """verify-coverage <bus_dir> <agent_id> [days] — audit report, NOT a gate: every `finding`
    from <agent_id> in the last N days (default 14), and whether a `verification` event with
    the same trace_id exists anywhere on the bus. Deliberately does not guess "importance" —
    that judgment stays with Mike/user (MIKE.md: "finding R&D quan trọng" is reviewed by a
    human, not a keyword classifier); this just makes the coverage visible instead of requiring
    a manual grep across every inbox. Findings predating the 2026-07-03 trace_id fix show
    trace=none (can't be correlated retroactively) rather than being reported as unverified.
    Exit 0 always (report tool, not pass/fail) — read the table."""
    bus_dir, agent_id = a[0], a[1]
    days = _as_int(a[2], 14) if len(a) > 2 else 14
    agent_files = [f for f in _agent_files(bus_dir, agent_id) if os.path.exists(f)]
    if not agent_files:
        print("no inbox for agent '%s' (đã kiểm cả hot + bus/inbox/archive/)" % agent_id)
        return
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime(TS_FMT)
    findings = [e for e in load_jsonl(agent_files)
                if e.get("event_type") == "finding" and e.get("ts", "") >= cutoff]
    if not findings:
        print("no `finding` events from %s in the last %d days" % (agent_id, days))
        return
    verifications = {}  # trace_id -> verdict
    for e in load_jsonl(_inbox_files(bus_dir)):
        if e.get("event_type") == "verification" and e.get("trace_id"):
            p = e.get("payload")
            verifications[e["trace_id"]] = p.get("verdict", "?") if isinstance(p, dict) else "?"
    print("%-20s %-26s %-30s %-12s" % ("ts", "trace_id", "topic", "verified"))
    n_unverified = 0
    for e in sorted(findings, key=lambda e: e.get("ts", "")):
        tid = e.get("trace_id")
        if not tid:
            status = "trace=none"
        elif tid in verifications:
            status = verifications[tid]
        else:
            status = "UNVERIFIED"
            n_unverified += 1
        print("%-20s %-26s %-30s %-12s" % (e.get("ts", "")[:19], (tid or "-")[:26],
                                            e.get("topic", "")[:30], status))
    print("\n%d finding(s), %d with a trace_id but no matching verification" %
          (len(findings), n_unverified))


def cmd_has_event(a):
    """has-event <bus_dir> <agent_id> <since_iso> <event_type:topic> [<event_type:topic> ...]

    Generic "post-condition check": does this agent's inbox (hot + archive) contain ANY of
    the given (event_type, topic) pairs with ts >= since_iso? Exit 0 + print the match if
    yes; exit 1 + print "no match" if not. Generalizes the hand-rolled matcher every
    background-dispatch pipeline was writing separately (ops_autofix.sh's `allowed = {topic:
    type}` dict is the reference this was extracted from) — see mike/kb/
    dispatch_output_contract.md for the pipeline-author-facing doc, coding_guidelines.md for
    the rule. Exact topic match only (no prefix/substring) — same semantics as the
    hand-rolled versions this replaces; construct the exact expected topic string before
    calling (e.g. "wags-fix: %s" % label), same as callers already did by hand.

    Deliberately does NOT default `since_iso` to "N hours ago" — callers must pass the
    actual dispatch start time. A relative-hours cutoff would let a STALE event from an
    earlier, unrelated dispatch with the same topic false-positive; requiring the real
    start timestamp is the same discipline ops_autofix.sh already uses (STARTED_ISO_FILE).
    """
    bus_dir, agent_id, since_iso = a[0], a[1], a[2]
    pairs = []
    for spec in a[3:]:
        if ":" not in spec:
            sys.stderr.write("has-event: bad spec '%s', expected event_type:topic\n" % spec)
            sys.exit(2)
        etype, topic = spec.split(":", 1)
        pairs.append((etype, topic))
    for e in load_jsonl(_agent_files(bus_dir, agent_id)):
        if e.get("ts", "") < since_iso:
            continue
        for etype, topic in pairs:
            if e.get("event_type") == etype and e.get("topic") == topic:
                print("MATCH %s %s/%s at %s" % (agent_id, etype, topic, e.get("ts", "")))
                sys.exit(0)
    print("no match: %s has none of %s since %s (đã quét cả archive)" %
          (agent_id, ["%s:%s" % p for p in pairs], since_iso))
    sys.exit(1)


def cmd_job_get(a):
    """job-get <jobs_dir> <job_id> — print one job; exit code reflects state.
    0=done 2=running 3=overdue 5=pending-resume (usage limit/max turns — se tu chay lai)
    1=failed/timeout/unknown 4=not-found."""
    jobs_dir, job_id = a[0], a[1]
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            o = json.load(f)
    except Exception:
        print("not-found: %s" % job_id)
        sys.exit(4)
    n = now_epoch()
    disp = _job_display_status(o, n)
    for k in ("job_id", "from", "to", "status", "attempt", "max_attempts",
              "started_at", "deadline", "ended_at", "exit_code", "pid",
              "logfile", "prompt_summary", "result_summary", "discord_thread_id"):
        if k in o:
            print("%-15s %s" % (k + ":", o[k]))
    print("%-15s %s" % ("display:", disp))
    print("%-15s %ss" % ("log_age:", _log_age(o, n)))
    if o.get("status") == "running":
        hb = _hb_age(o, n)
        print("%-15s %ss  (heartbeat bus cuối — tín hiệu sống ĐÚNG khi đang chạy; "
              "log chỉ ghi lúc kết thúc)" % ("hb_age:", hb))
    st = o.get("status", "?")
    if disp == "OVERDUE":
        sys.exit(3)
    if st == "done":
        sys.exit(0)
    if st in ("running", "retrying"):
        sys.exit(2)
    # 5 = CHO TIEP TUC (usage limit / het turn budget). KHONG phai that bai: resume_pending.py
    # se dispatch lai thanh job MOI. Dung lai dung ma 5 ma dispatch.sh da tra o nhanh dong bo
    # cho cung tinh huong (xem header dispatch.sh "Exit code 5 (sync mode)") — khong bia ma moi.
    # Truoc 2026-08-03 hai trang thai nay roi vao sys.exit(1) ben duoi => `jobs.sh wait` tra ve
    # "failed" ngay lap tuc va vong poll cua Mike ket luan viec chet -> re-dispatch, nhan doi
    # cong viec. Do la lop loi "im lang khong phan biet duoc voi that bai".
    if st in PENDING_RESUME_STATES:
        sys.exit(5)
    # 'cancelled' and 'orphaned' land here too, on purpose — no new exit code. Both are only
    # ever written AFTER it has been proven that no process of the job is alive (job-cancel
    # verifies the kill; job-reap refuses a job with live pids), so "1 = did not finish, safe
    # to run again" is true of them. What made 2026-08-09 dangerous was not the code 1, it was
    # a code 1 on a job whose worker was still running — and that is now refused at the write.
    sys.exit(1)  # failed / timeout / cancelled / orphaned / unknown


def cmd_job_field(a):
    """job-field <jobs_dir> <job_id> <field_name> — print just that field's raw value.
    Exit 1 (empty stdout) if the job or field is missing. For shell code that needs ONE
    value (e.g. discord_thread_id) without parsing the full job-get output."""
    jobs_dir, job_id, field = a[0], a[1], a[2]
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            o = json.load(f)
    except Exception:
        sys.exit(1)
    v = o.get(field, "")
    if not v:
        sys.exit(1)
    print(v)
    sys.exit(0)


# --- circuit breaker (state/circuit/<id>.json) ---
# Per-agent consecutive-failure counter for dispatch.sh. Trips (blocks new dispatches)
# after N consecutive failed/timeout jobs; auto-resets to closed after a cooldown window
# (simple trial-on-expiry, not full half-open — this guards against runaway repeated
# dispatch to a chronically-broken agent, not a high-frequency traffic breaker).

def _circuit_path(state_dir, agent_id):
    return os.path.join(state_dir, agent_id + ".json")


def _circuit_load(state_dir, agent_id):
    try:
        with open(_circuit_path(state_dir, agent_id), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"fails": 0, "tripped_until": 0}


def _circuit_save(state_dir, agent_id, obj):
    os.makedirs(state_dir, exist_ok=True)
    fp = _circuit_path(state_dir, agent_id)
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, fp)


def cmd_circuit_check(a):
    """circuit-check <state_dir> <agent_id> — exit 0 (closed/allowed) or 1 (open/blocked).
    Auto-clears an expired trip (cooldown passed) before checking, allowing a trial dispatch."""
    state_dir, agent_id = a[0], a[1]
    obj = _circuit_load(state_dir, agent_id)
    n = now_epoch()
    tripped_until = _as_int(obj.get("tripped_until"), 0)
    if tripped_until and n >= tripped_until:
        obj = {"fails": 0, "tripped_until": 0}
        _circuit_save(state_dir, agent_id, obj)
        tripped_until = 0
    if tripped_until and n < tripped_until:
        print("OPEN fails=%s tripped_until=%s remaining_s=%s" % (
            obj.get("fails", "?"), tripped_until, tripped_until - n))
        sys.exit(1)
    print("CLOSED fails=%s" % obj.get("fails", 0))
    sys.exit(0)


def cmd_circuit_record(a):
    """circuit-record <state_dir> <agent_id> <success|fail> [threshold] [cooldown_sec]
    -> updates the counter; exit 0 normally, exit 1 if this call TRIPPED the breaker
    (caller should notify on exit 1)."""
    state_dir, agent_id, result = a[0], a[1], a[2]
    threshold = _as_int(a[3], 3) if len(a) > 3 else 3
    cooldown = _as_int(a[4], 1800) if len(a) > 4 else 1800
    obj = _circuit_load(state_dir, agent_id)
    n = now_epoch()
    if result == "success":
        _circuit_save(state_dir, agent_id, {"fails": 0, "tripped_until": 0})
        print("CLOSED fails=0")
        sys.exit(0)
    fails = _as_int(obj.get("fails"), 0) + 1
    if fails >= threshold:
        tripped_until = n + cooldown
        _circuit_save(state_dir, agent_id, {"fails": fails, "tripped_until": tripped_until,
                                            "last_fail_at": n})
        print("TRIPPED fails=%s tripped_until=%s cooldown_s=%s" % (fails, tripped_until, cooldown))
        sys.exit(1)
    _circuit_save(state_dir, agent_id, {"fails": fails, "tripped_until": 0, "last_fail_at": n})
    print("fails=%s/%s" % (fails, threshold))
    sys.exit(0)


# --- usage-limit auto-resume (bus/pending_resumes/<job_id>.json) ---
# See dispatch.sh's _maybe_schedule_usage_resume for when these get written, and
# bin/resume_pending.py (cron) for when they get fired.

def cmd_pending_resume_set(a):
    """pending-resume-set <path> <agent_id> <from> <orig_job_id> <resume_at_epoch>
    <resume_count> [kind] [model] [effort] [max_turns] [provider] — prompt text read from
    STDIN (avoids shell-quoting a large/multiline string as a CLI arg). Atomic write.

    `provider` added 2026-08-03 (multi-CLI). Without it, a resume ALWAYS re-dispatches on
    the default provider (claude) while still passing the ORIGINAL provider's --model —
    e.g. an opencode job resumes as `claude --model opencode/deepseek-v4-flash-free`, which
    dispatch.sh's provider gate rejects (exit 1). Combined with resume_pending.py removing
    the record BEFORE firing, that silently loses the task."""
    fp, agent_id, frm, orig_job_id, resume_at, resume_count = a[:6]
    kind = a[6] if len(a) > 6 and a[6] else "usage_limit"
    model = a[7] if len(a) > 7 and a[7] else None
    effort = a[8] if len(a) > 8 and a[8] else None
    max_turns = a[9] if len(a) > 9 and a[9] else None
    provider = a[10] if len(a) > 10 and a[10] else None
    prompt = sys.stdin.read()
    obj = {"agent": agent_id, "from": frm, "orig_job_id": orig_job_id,
           "resume_at": _as_int(resume_at), "resume_count": _as_int(resume_count),
           "kind": kind, "model": model, "effort": effort,
           "max_turns": _as_int(max_turns) if max_turns else None,
           "provider": provider,
           "prompt": prompt, "created_at": now_iso()}
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, fp)


def cmd_settings(a):
    """settings <hooks_dir> <agent_id> [model] — wires the 3 hooks; sets model when given."""
    hooks_dir, aid = a[0], a[1]
    model = a[2] if len(a) > 2 else None
    def hook(name, script):
        return {name: [{"hooks": [{"type": "command",
                                   "command": "%s/%s %s" % (hooks_dir, script, aid)}]}]}
    s = {"hooks": {}}
    s["hooks"].update(hook("SessionStart", "session_start.sh"))
    s["hooks"].update(hook("UserPromptSubmit", "user_prompt_submit.sh"))
    s["hooks"].update(hook("Stop", "stop.sh"))
    if model:
        s["model"] = model
    print(json.dumps(s, indent=2, ensure_ascii=False))


CMDS = {"event": cmd_event, "heartbeat": cmd_heartbeat, "recent": cmd_recent,
        "delta-append": cmd_delta_append, "delta-since": cmd_delta_since,
        "format-events": cmd_format_events, "fleet-status": cmd_fleet_status,
        "cursor-advance": cmd_cursor_advance,
        "job-set": cmd_job_set, "job-list": cmd_job_list, "job-get": cmd_job_get,
        "job-reap": cmd_job_reap, "job-cancel": cmd_job_cancel,
        "job-find-dup": cmd_job_find_dup, "terminal-statuses": cmd_terminal_statuses,
        "job-field": cmd_job_field, "job-hb-age": cmd_job_hb_age,
        "circuit-check": cmd_circuit_check, "circuit-record": cmd_circuit_record,
        "pending-resume-set": cmd_pending_resume_set,
        "settings": cmd_settings, "trace": cmd_trace,
        "verify-coverage": cmd_verify_coverage, "has-event": cmd_has_event}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.stderr.write("usage: mike_json.py <%s> ...\n" % "|".join(CMDS))
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
