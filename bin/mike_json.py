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
      -> writes a bus/pending_resumes/<job_id>.json record; prompt text read from STDIN
         (avoids shell-quoting a large/multiline string as a CLI arg)
  job-field <jobs_dir> <job_id> <field_name>
      -> print one field's raw value (exit 1 if job/field missing) — e.g. discord_thread_id
  job-hb-age <jobs_dir> <job_id>
      -> seconds since the job's last AGENT-written bus event ('-' if none); excludes
         _job_watcher liveness pings — input to dispatch.sh heartbeat-aware deadline
"""
import sys, os, json, uuid, glob, datetime, hashlib

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
    rows = []
    for fp in paths:
        try:
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
        except FileNotFoundError:
            pass
    return rows


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
            lines = f.read().splitlines()
    except Exception:
        return
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


def cmd_job_set(a):
    """job-set <jobs_dir> <job_id> key=val [key=val ...] — merge fields, atomic write.
    Values kept as strings; numeric fields are coerced on read."""
    jobs_dir, job_id = a[0], a[1]
    os.makedirs(jobs_dir, exist_ok=True)
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            obj = json.load(f)
    except Exception:
        obj = {}
    for kv in a[2:]:
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        # Sanitize: head -c may cut a multibyte sequence, producing surrogates.
        obj[k] = v.encode("utf-8", errors="replace").decode("utf-8")
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, fp)


def _job_display_status(obj, n):
    """running + past deadline -> OVERDUE (soft flag; the hard timeout lives in dispatch.sh)."""
    st = obj.get("status", "?")
    if st == "running" and _as_int(obj.get("deadline"), 0) and n > _as_int(obj.get("deadline")):
        return "OVERDUE"
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


def _pid_alive(pid):
    """True if the pid is still a live process, False if provably dead, None if unknown
    (no pid recorded — old records predating the pid field)."""
    if not pid:
        return None
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True          # exists, owned by someone else
    except Exception:
        return None


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
        if _pid_alive(o.get("pid")) is True:
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
            cmd_job_set([jobs_dir, job_id, "status=orphaned", "ended_at=%d" % n,
                         "result_summary=reaped by jobs.sh reap: dispatcher died without "
                         "writing a terminal status (%.1fh past deadline, pid dead/absent)"
                         % over_h])
            # watchdog's per-job debounce marker is dead weight once the record is closed
            om = os.path.join(os.path.dirname(jobs_dir.rstrip("/")), "..", "state", "overdue", job_id)
            try:
                os.remove(os.path.normpath(om))
            except Exception:
                pass
    print("%d orphaned job record(s)%s" % (reaped, " (dry-run, not written)" if dry else " closed"))


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
    """trace <bus_dir> <trace_id> — every bus event (any agent's inbox) sharing this
    trace_id (= a dispatch job_id, by convention), sorted chronologically. Prints the
    job record first if bus_dir/jobs/<trace_id>.json exists. Exit 1 if no events found."""
    bus_dir, trace_id = a[0], a[1]
    jobs_fp = os.path.join(bus_dir, "jobs", trace_id + ".json")
    if os.path.exists(jobs_fp):
        try:
            with open(jobs_fp, encoding="utf-8") as f:
                jo = json.load(f)
            print("=== job %s ===" % trace_id)
            for k in ("from", "to", "status", "started_at", "ended_at", "exit_code", "logfile"):
                if k in jo:
                    print("%-12s %s" % (k + ":", jo[k]))
            print()
        except Exception:
            pass
    events = []
    for fn in sorted(glob.glob(os.path.join(bus_dir, "inbox", "*.jsonl"))):
        for ln in open(fn, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                e = json.loads(ln)
            except Exception:
                continue
            if e.get("trace_id") == trace_id:
                events.append(e)
    events.sort(key=lambda e: e.get("ts", ""))
    if not events:
        print("no bus events found with trace_id=%s" % trace_id)
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
    inbox_dir = os.path.join(bus_dir, "inbox")
    agent_fp = os.path.join(inbox_dir, agent_id + ".jsonl")
    if not os.path.exists(agent_fp):
        print("no inbox for agent '%s'" % agent_id)
        return
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime(TS_FMT)
    findings = [e for e in load_jsonl([agent_fp])
                if e.get("event_type") == "finding" and e.get("ts", "") >= cutoff]
    if not findings:
        print("no `finding` events from %s in the last %d days" % (agent_id, days))
        return
    verifications = {}  # trace_id -> verdict
    for fn in sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))):
        for e in load_jsonl([fn]):
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


def cmd_job_get(a):
    """job-get <jobs_dir> <job_id> — print one job; exit code reflects state.
    0=done 2=running 3=overdue 1=failed/timeout 4=not-found."""
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
    sys.exit(1)  # failed / timeout / unknown


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
    <resume_count> — prompt text read from STDIN (avoids shell-quoting a large/multiline
    string as a CLI arg). Atomic write."""
    fp, agent_id, frm, orig_job_id, resume_at, resume_count = a
    prompt = sys.stdin.read()
    obj = {"agent": agent_id, "from": frm, "orig_job_id": orig_job_id,
           "resume_at": _as_int(resume_at), "resume_count": _as_int(resume_count),
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
        "job-reap": cmd_job_reap,
        "job-field": cmd_job_field, "job-hb-age": cmd_job_hb_age,
        "circuit-check": cmd_circuit_check, "circuit-record": cmd_circuit_record,
        "pending-resume-set": cmd_pending_resume_set,
        "settings": cmd_settings, "trace": cmd_trace,
        "verify-coverage": cmd_verify_coverage}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.stderr.write("usage: mike_json.py <%s> ...\n" % "|".join(CMDS))
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
