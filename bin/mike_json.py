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
  job-claim-reply <jobs_dir> <job_id>
      -> ATOMIC test-and-set of replied_at under an exclusive lock. exit 0 = THIS caller is
         the first to claim (go post the result); exit 1 = someone already claimed it (stay
         silent); exit 2 = record missing/corrupt (nothing written, decide by hand).
         Front door: bin/jobs.sh claim-reply <job_id>
  job-hb-age <jobs_dir> <job_id>
      -> seconds since the job's last AGENT-written bus event ('-' if none); excludes
         _job_watcher liveness pings — input to dispatch.sh heartbeat-aware deadline
  has-event <bus_dir> <agent_id> <since_iso> <event_type:topic> [...]
      -> exit 0 + print match if agent's inbox (hot+archive) has any of the given
         (event_type, topic) pairs since since_iso; exit 1 otherwise. Generic
         post-condition/"output contract" check for background-dispatch pipelines —
         see mike/kb/dispatch_output_contract.md. EXACT topic match.
  has-event-prefix <bus_dir> <agent_id> <since_iso> <event_type:topic_prefix> [...]
      -> same, but topic matched by PREFIX — for producers told to write a topic
         "starting with X" and free to append their own description (Wags findings).
"""
import sys, os, json, uuid, glob, datetime, hashlib, gzip, re, signal, time, fcntl

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


def _utf8_safe(x):
    """Bỏ mọi surrogate/byte hỏng — ĐỆM CUỐI trước khi ghi vào bus APPEND-ONLY.

    Vì sao ở TẦNG NÀY chứ không chỉ ở caller (arch-review coord-2026-08-16): caller cắt
    chuỗi bằng `cut -c`/`head -c`, mà locale máy này là LANG="C" (/etc/default/locale) nên
    `cut -c` đếm theo BYTE — cắt trúng giữa một ký tự tiếng Việt 3 byte là vỡ chuỗi. Python
    đọc argv bằng surrogateescape nên byte hỏng đi lọt tới tận đây, json.dumps vẫn ra rc=0,
    và dòng hỏng nằm VĨNH VIỄN trong file append-only: từ đó load_jsonl ném
    UnicodeDecodeError cho MỌI consumer của inbox đó (ops_health_check §5, wags_autofix
    bước 1.5...). Một caller ẩu đủ sức làm câm cả kênh escalation của fleet.
    Phép vá y hệt dòng 661 (cmd_job_set) đã dùng từ trước — chỗ đó vá đường job record,
    chỗ này vá đường event; hai đường độc lập, sửa một chỗ KHÔNG che được chỗ kia.
    """
    if isinstance(x, str):
        return x.encode("utf-8", errors="replace").decode("utf-8")
    if isinstance(x, dict):
        return {_utf8_safe(k): _utf8_safe(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_utf8_safe(i) for i in x]
    return x


def cmd_event(a):
    aid, etype, topic, payload, kbver = a[:5]
    trace_id = a[5] if len(a) > 5 and a[5] else None
    try:
        p = json.loads(payload)
    except Exception:
        p = payload
    aid, etype, topic = _utf8_safe(aid), _utf8_safe(etype), _utf8_safe(topic)
    p = _utf8_safe(p)
    trace_id = _utf8_safe(trace_id) if trace_id else trace_id
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

# Every record field that feeds a liveness or death decision. Editing one edits the evidence,
# so cmd_job_set demands the same proof for changing one as for closing the record.
#
# Keep this list in lockstep with _death_evidence and everything it calls. Four rounds of
# audit have now found the bypass in the SAME place every time — a field that had quietly
# become evidence without being named here — so the entry below records what each one decides:
#   pid, dispatcher_pid, logfile, logfile_ino, logfile_err_ino  -> _job_live_pids: which
#       processes are this job's, and whether the file we are looking at is still the file
#       the job opened (rounds 2/3/4, and the decoy in round 5, N5).
#   started_at  -> gates EVIDENCE_GRACE_S. Round 5, K1: it was the one field left that could
#       turn `blind` OFF, so `mv <logfile> x; job-set started_at=<now>; job-set status=failed`
#       reproduced the 2026-08-09 lie verbatim, rc=0, on a provably live worker.
#   to, job_id  -> locate bus/inbox/<to>.jsonl in _hb_age, i.e. the heartbeat that round 4
#       promoted to the independent proof of death. Round 5, K2: `job-set to=Nobody` points it
#       at a file that does not exist, every heartbeat becomes "never seen", and job-cancel
#       then closed a live worker while asserting in result_summary that the agent had gone
#       silent — the guard stating as fact the very thing it had just been blinded to.
#   deadline  -> the reap precondition. `job-set deadline=1` made any record instantly
#       reap-eligible (round 5, N4).
#   pin_source  -> the provenance sentence _death_evidence speaks about its own evidence.
#       Round 8, NICE 5: `job-set <id> pin_source=backfill` returned rc=0 and rewrote what the
#       guard says about where its proof came from — a forged attestation, which is the exact
#       class of defect K4 exists to remove.
EVIDENCE_FIELDS = ("pid", "dispatcher_pid", "logfile", "logfile_ino", "logfile_err_ino",
                   "started_at", "to", "job_id", "deadline", "pin_source")


def _is_evidence_change(field, new, old):
    """Is writing `new` over `old` a change to this job's liveness evidence?

    `deadline` is the one field where the answer depends on the DIRECTION. Only shrinking it
    is evidence: a smaller deadline is what makes a record reap-eligible on demand
    (`job-set <id> deadline=1`, round 5, N4). Growing it is dispatch.sh's own heartbeat-aware
    extension (dispatch.sh:760, `JSET deadline=... hb_extensions=...`), which fires on jobs
    that are BY DEFINITION alive and busy — guarding that direction would refuse the fleet's
    most routine write on exactly the jobs it is meant to protect."""
    if field == "deadline":
        # A record with NO deadline has no reap precondition at all, so writing the first one
        # CREATES it — that is not "growth", it is manufacturing the thing being guarded
        # (round 6, NICE 7). Only a genuine extension of an existing deadline is exempt.
        if _as_int(old, 0) <= 0:
            return True
        return _as_int(new, 0) < _as_int(old, 0)
    return str(new) != str(old or "")


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


def _is_self_or_ancestor(pid, limit=64):
    """True if `pid` is THIS process or one of its ancestors, within `limit` hops.

    Distinguishes the job finalising its OWN record (dispatch.sh's _bg_wrapper runs as
    the recorded pid and JSETs status=done/failed from inside it — mike_json.py is then a
    descendant of that pid) from an OUTSIDE writer stamping a terminal status onto a job
    that is still running. Bounded walk; /proc chains are short."""
    try:
        pid = int(pid)
    except Exception:
        return False
    cur = os.getpid()
    for _ in range(limit + 1):
        if cur == pid:
            return True
        if cur <= 1:
            return False
        nxt = _ppid_of(cur)
        if nxt is None or nxt == cur:
            return False
        cur = nxt
    return False


def cmd_job_set(a, internal=False, stale_proven=False):
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
    # MISSING and UNPARSEABLE are different facts and must not share a branch. Missing = this
    # is a brand-new record, the normal case for every dispatch, nothing to protect. Present
    # but unparseable = the evidence has been destroyed, and `obj = {}` then switched the
    # guard OFF entirely: no recorded status meant the LIVE_STATUSES precondition failed and
    # no recorded fields meant nothing looked like an evidence rewrite. `printf 'x' >
    # bus/jobs/<id>.json` followed by `job-set status=failed` returned rc=0 over a live
    # worker — the same bypass as K1, through the record file instead of the logfile
    # (arch-reviewer round 4, N1).
    obj, unparseable = {}, False
    try:
        with open(fp, encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            obj, unparseable = {}, True
    except FileNotFoundError:
        obj = {}
    except Exception:
        obj, unparseable = {}, True
    if unparseable and not force:
        sys.stderr.write(
            "REFUSED: job record %s exists but is not readable JSON — refusing to write over "
            "it.\n"
            "  A corrupt record is not an empty one: the pid, logfile and dispatcher_pid that "
            "would say whether this job is still running have been destroyed, so NOTHING here "
            "can prove it is safe to close.\n"
            "  Recover the truth first (bin/trace.sh %s, ls -l logs/*%s*), then re-create the "
            "record deliberately with --force if that is really what you want.\n"
            % (fp, job_id, job_id))
        sys.exit(3)
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
    # KNOWN GAP, deliberately still open (round 6, NICE 6): a status change WITHIN the live
    # set is not treated as a claim, so `job-set <id> status=usage_limited` on a running job
    # succeeds and the board then reads PENDING-RESUME about a job nobody paused. Closing it
    # means making live->live transitions ownership-checked, and every production writer of
    # those statuses (dispatch.sh:392/489/1209/1218, all via JSET) does carry the credentials
    # — but that is a code-reading argument, not a demonstration, and the L2 allowlist above
    # it was a deliberate round-S4 decision. Getting it wrong hangs the fleet's retry path,
    # which is the failure this guard must never become, so it wants its own change with its
    # own E2E rather than a ride-along at the end of round 6.
    closing = new_status is not None and new_status not in LIVE_STATUSES
    # Only a REWRITE of an existing pid is suspicious. dispatch.sh:981 stamps pid= onto a
    # record that has none yet (`JSET pid="$BASHPID"`, the very first thing the wrapper does)
    # — guarding that would refuse every --bg job its own pid and hang the whole fleet at
    # status=running. There is nothing to protect when no pid is recorded.
    # EVIDENCE. Every field _job_live_pids reads is evidence, and evidence must not be
    # editable by the writer whose claim it is about. This is stated over the GROUP, not
    # over field names, because naming them one at a time is how the same hole kept
    # reopening: round 2 hardened `pid` (rewrite only), round 3 hardened `dispatcher_pid`,
    # and round 3's audit then walked through the two that were still unguarded — on the
    # exact 08-09 record shape, worker alive, both pairs rc=0:
    #     job-set <id> logfile=/tmp/nowhere.log ; job-set <id> status=failed
    #     job-set <id> pid=<my own>            ; job-set <id> status=failed
    # The second one mattered most: it needs no rewrite at all, because a SYNC record never
    # has a pid to rewrite (JSET pid=$BASHPID lives only in _bg_wrapper) — and sync is the
    # fleet's DEFAULT mode, 85 of the last 400 records on the live board.
    # Note this deliberately covers a FIRST write too. dispatch.sh's own late `pid=` stamp
    # stays legal for the reason that makes it honest: the wrapper writes it before spawning
    # anything, when the job has no live process yet, so `live` is empty and nothing is being
    # asserted over a running worker. An attacker's first write always races a live one.
    exists = obj.get("status") is not None
    changed_evidence = [k for k in EVIDENCE_FIELDS
                        if k in fields and _is_evidence_change(k, fields[k], obj.get(k))]
    repid = exists and bool(changed_evidence)
    live = []
    guarded = False
    # Precondition is "the record still claims to be live", not "== running": a record in
    # retrying/usage_limited is just as live, and keying on 'running' alone left those
    # unprotected (arch-reviewer S4). The process discovery below walks /proc, so it runs
    # ONLY on a close/repid attempt — never on the ordinary field update — and the cheap
    # ancestry test short-circuits the wrapper finalising its own record before that.
    why = ""
    if (closing or repid) and obj.get("status") in LIVE_STATUSES \
            and not _is_self_or_ancestor(obj.get("pid")):
        verdict, live, why, _hbs = _death_evidence(obj)
        # UNKNOWN is not DEAD. An empty `live` on a record whose logfile has been deleted or
        # renamed away means the evidence is gone, not that the worker is — and a rename
        # defeats even the inode match, so `_pids_holding` genuinely cannot tell. Treat it as
        # live: the whole point of this guard is that the board must not report a live writer
        # as stopped, and "I could not check" is not permission to say "stopped"
        # (arch-reviewer round 4, K1). `stale_proven` is the ONE narrow exemption — see
        # cmd_job_reap, which carries an independent proof of death (past deadline + grace AND
        # the agent's own bus heartbeat gone cold) and would otherwise be unable to ever close
        # such a record, turning an anti-lying guard into a permanent board leak.
        blind = verdict == UNKNOWN
        # Only a DEAD verdict — we looked at the job's own logfile and nothing held it — lets
        # an outside writer close the record. ALIVE with an EMPTY pid list is a real case now
        # (evidence gone, agent still heartbeating), so this asks the verdict rather than
        # whether `live` came back non-empty. `stale_proven` remains the ONE exemption, and
        # only over UNKNOWN: see cmd_job_reap, which carries an independent proof the guard
        # cannot see and would otherwise be unable to ever close such a record.
        suspect = verdict != DEAD and not (blind and stale_proven)
        # Three ways to be a legitimate writer, cheapest first: the recorded pid is me or my
        # ancestor (--bg wrapper, tested above), I am one of the job's live processes or a
        # child of one (agent writing its own record), or I am the dispatcher that spawned
        # them (sync dispatch, which records no pid — MIKE_JOB_OWNER, /proc-verified).
        guarded = (suspect and not _writer_belongs_to_job(live)
                   and not _writer_is_job_dispatcher(job_id, obj))
    if guarded and internal:
        # cmd_job_reap calls this in-process; a sys.exit(3) here would abort the whole reap
        # loop and leave every later record unexamined. The caller checks the return value.
        return False
    if guarded and not force:
        if closing:
            what = "stamp status=%s" % new_status
        else:
            what = "change the liveness evidence (" + ", ".join(
                "%s=%s" % (k, fields[k]) for k in changed_evidence) + ")"
        # The pid note must not point at a pid that is not there: on a SYNC record it used
        # to read "the recorded pid None is the _bg_wrapper", which reads as an invitation
        # to supply one — and supplying one WAS the bypass (round 3, O2).
        pidnote = (
            "  NOTE the recorded pid %s is the _bg_wrapper. Killing it does NOT stop the "
            "worker: the worker runs under setsid, gets reparented to init, and keeps "
            "editing the repo — on 2026-08-09 it did so for 33 more minutes.\n"
            % obj.get("pid")) if obj.get("pid") else (
            "  NOTE this record has no pid because it is a SYNC dispatch; the live "
            "process above was found by the job's own logfile. Writing a pid onto the "
            "record does not make the worker stop — it only makes the board agree with "
            "you, which is the failure being prevented.\n")
        # Say WHICH refusal this is, and never claim more than the verdict supports.
        # Reporting "0 process(es) are ALIVE" would be the guard itself stating something it
        # does not know — and stating the unknown as fact is the failure being prevented.
        if not live:
            # ALIVE with no pid list (evidence gone, agent still heartbeating) is a DIFFERENT
            # statement from UNKNOWN, and saying the wrong one is the failure being prevented.
            sys.stderr.write(
                ("REFUSED: job %s still claims status=%s and %s — %srefusing to %s is the "
                 "only answer that is not a guess.\n"
                 % (job_id, obj.get("status"), why,
                    "so whether anything of it is still running CANNOT BE DETERMINED, and "
                    if blind else "so ", what)) +
                "  An absent logfile is not proof of death: a deleted file keeps being "
                "written while its holder lives, and a file that merely occupies the path is "
                "not the job's logfile at all (arch-reviewer rounds 4-5).\n"
                "  Find out first:  bin/trace.sh %s   /   ls -l logs/*%s*\n"
                "  If you have established it really is dead, say so explicitly with "
                "--force and the evidence will be recorded on the record.\n"
                % (job_id, job_id))
            sys.exit(3)
        sys.stderr.write(
            "REFUSED: job %s is still %s and %d process(es) of it are ALIVE right now: %s "
            "— refusing to %s (that is how the board starts lying; incident 2026-08-09).\n"
            "%s"
            "  Stop it properly:  bin/jobs.sh cancel %s   (kills the whole tree, VERIFIES "
            "it is dead, then closes the record)\n"
            "  Just checking:     bin/jobs.sh status %s   (HB_AGE is the real liveness "
            "signal — LOG_AGE is useless while a job runs)\n"
            % (job_id, obj.get("status"), len(live), live, what, pidnote,
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
        # Exactly the liveness the guard uses — one implementation, see _death_evidence. A job
        # whose wrapper died but whose worker still holds the logfile is NOT orphaned, it is
        # running unattended, and stamping it 'orphaned' is the board lying in the other
        # direction. The heartbeat threshold is floored at HB_COLD_S instead of taking the
        # caller's `grace`: `jobs.sh reap 0` used to pass 0 all the way down and reap a record
        # whose agent had heartbeated that same second (round 5, N4).
        hb_floor = max(int(grace), HB_COLD_S)
        verdict, _live, why, hbs = _death_evidence(o, n, hb_cold_s=hb_floor)
        if verdict == ALIVE:
            continue
        blind = verdict == UNKNOWN
        # Only --bg dispatches record a pid; for a sync record keep the extra caution of not
        # reaping while its agent is still writing bus events, even when the logfile is there.
        if not o.get("pid") and hbs[0] == "fresh":
            continue
        # NEVER heartbeated + evidence gone = no evidence of anything. Round 4 closed these at
        # deadline+grace, i.e. watchdog.sh's hourly automatic call stamped 'orphaned' on jobs
        # it knew nothing about. Wait a full day and then say on the record that the closure
        # is unverified — late and honest beats early and wrong, and still no permanent leak.
        unverified = blind and hbs[0] == "never"
        if unverified and n <= dl + max(grace, REAP_UNVERIFIED_S):
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
        print("orphaned %-26s %s->%s  %.1fh past deadline%s" % (
            job_id, o.get("from", "?"), o.get("to", "?"), over_h,
            "  UNVERIFIED (no evidence either way)" if unverified else ""))
        reaped += 1
        if not dry:
            # internal=True: the guard must not sys.exit() out of this loop and leave every
            # later record unexamined. A False return means a process appeared between the
            # check above and this write — then the job is alive and must not be reaped.
            # stale_proven: reap is the one caller allowed past the "logfile gone means
            # UNKNOWN" term, because it has already proved death by an independent route the
            # guard cannot see — past deadline + grace AND the agent's own bus heartbeat gone
            # cold (checked above for exactly this case). Without the exemption a record whose
            # log was deleted could never be closed by ANY command, which is the permanent
            # board leak this guard is supposed to prevent, not cause.
            # Quote the verdict's OWN words for why, instead of a hand-written sentence that
            # has to be kept true separately. Round 6, K4: this line said "logfile gone" for a
            # record whose logfile was sitting right there merely unpinned, and "dispatcher
            # died without writing a terminal status" — a causal claim about an event nobody
            # observed — while `ps` showed the worker running.
            if blind and unverified:
                why_closed = ("; %s — CLOSED UNVERIFIED after %.0fh, nothing here proved it "
                              "stopped" % (why, (n - dl) / 3600.0))
            elif blind:
                why_closed = "; %s — death inferred from that silence, not observed" % why
            else:
                why_closed = "; " + why
            if cmd_job_set([jobs_dir, job_id, "status=orphaned", "ended_at=%d" % n,
                            "result_summary=reaped by jobs.sh reap: no terminal status was "
                            "ever written for this job (%.1fh past deadline, no live process "
                            "found%s)" % (over_h, why_closed)],
                           internal=True, stale_proven=blind) is False:
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


def cmd_job_write_scope_conflict(a):
    """job-write-scope-conflict <jobs_dir> <scope_csv> — print job_ids of LIVE jobs (any
    agent/prompt) whose OWN declared write_scope shares at least one path with `scope_csv`.
    Exit 0 if any were printed (conflict — caller should refuse to dispatch), 1 if none.

    Opt-in only: write_scope is set by the CALLER via dispatch.sh's --write-scope, never
    inferred from the prompt — job-find-dup's own comment on why file-scope can't be guessed
    at dispatch time (the target file often doesn't exist yet) still holds for the general
    case. This only fires when TWO dispatches BOTH explicitly declared overlapping scope,
    which is exactly the shape job-find-dup's exact-prompt-match cannot see: different
    agents, different prompts, same file (coord-2026-08-07 — Mafee + Taylor both editing
    trading_bot/plan_funding_gate.py within a minute, one commit clobbering the other's
    uncommitted work)."""
    jobs_dir, scope_csv = a[0], a[1]
    want = set(p.strip() for p in scope_csv.split(",") if p.strip())
    if not want:
        sys.exit(1)
    n = now_epoch()
    found = 0
    for o in _load_jobs(jobs_dir):
        # Same liveness definition as job-find-dup (round 9, K1): a record closed without
        # verified death still counts as live_enough, then _job_live_pids confirms for real.
        live_enough = o.get("status") in LIVE_STATUSES or str(o.get("death_verified", "")) == "0"
        if not live_enough:
            continue
        other = set(p.strip() for p in str(o.get("write_scope", "")).split(",") if p.strip())
        overlap = want & other
        if not overlap:
            continue
        if not _job_live_pids(o):
            continue
        print("%s (to=%s, dispatched %ds ago by %s, hb_age=%ss, scope=%s)" % (
            o.get("job_id", "?"), o.get("to", "?"), n - _as_int(o.get("started_at"), n),
            o.get("from", "?"), _hb_age(o, n, agent_only=True), ",".join(sorted(overlap))))
        found += 1
    sys.exit(0 if found else 1)


# Paths that belong to NO single job: the fleet's shared coordination surface. A commit
# touching one of these while a coordination job is live is the exact shape that has now
# recurred three times (2026-07-31, 2026-08-02, 2026-08-12) — someone commits from outside
# the running job and the shared git index sweeps that job's staged-but-uncommitted files
# into a commit with the wrong author and the wrong message.
SHARED_TOOLING_PATHS = ("bin/", "hooks/", ".pre-commit-config.yaml", "MIKE.md",
                        "kb/coding_guidelines.md", "kb/coding_guidelines_ext.md")

# Agents whose charter IS the shared tooling above, so a live job of theirs is presumed to
# be writing there even when it declared no --write-scope. Deliberately narrow: measured on
# 14 days of real history, "any live job" covers 56% of hand-authored commits (blocking on
# that would be the permanent-block failure mode that got the worktree pool bounced), while
# "live Wags job + shared-tooling path" covers 13% — and after self-exclusion nearly all of
# that 13% is Wags committing its own work from inside its own job.
SHARED_TOOLING_AGENTS = ("Wags",)


def _ancestor_pids(pid, limit=64):
    """This pid plus every ancestor up to init. Used to answer "is that live job MY OWN
    job?" without trusting an environment variable (dispatch.sh:788 — anyone can export
    one). Verified from inside a real dispatch: the tool-call shell's chain reaches the
    job record's own `pid` (the _bg_wrapper) before hitting systemd, even though the
    worker is setsid'd."""
    out, seen, p = [], set(), _as_int(pid, 0)
    while p > 1 and p not in seen and len(out) < limit:
        seen.add(p)
        out.append(p)
        try:
            with open("/proc/%d/stat" % p, encoding="utf-8") as f:
                st = f.read()
            # comm may contain spaces and parens -> parse after the LAST ')': state, ppid
            p = int(st[st.rindex(")") + 2:].split()[1])
        except Exception:
            break
    return out


def _self_job_ids(self_pid, jobs):
    """Job ids that are THIS callsite. A job that commits its own work at the end of its
    run (Wags does, every time) must never gate itself — measured on real history, without
    this the gate would fire on essentially every Wags fix commit."""
    anc = set(_ancestor_pids(self_pid))
    ids = set()
    env_id = os.environ.get("JOB_ID", "").strip()
    if env_id:
        # Weaker signal than ancestry (spoofable), kept as a fallback for the case where the
        # wrapper already exited and this process was reparented off the job's chain. Only
        # ever WIDENS self-exclusion, i.e. the worst a spoof buys is a missing warning —
        # which `--no-verify` already buys for free.
        ids.add(env_id)
    for o in jobs:
        jid = o.get("job_id")
        if not jid:
            continue
        if _as_int(o.get("pid"), 0) in anc or _as_int(o.get("dispatcher_pid"), 0) in anc:
            ids.add(jid)
    return ids


def _path_overlaps(a, b):
    """Same file, or one is a directory containing the other. Segment-aware on purpose:
    plain startswith would make 'bin/jobs.sh' overlap 'bin/jobs.sh.bak'."""
    a, b = a.strip().strip("/"), b.strip().strip("/")
    if not a or not b:
        return False
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def cmd_commit_collision_gate(a):
    """commit-collision-gate <jobs_dir> [--self-pid N] <staged_path>... — for every LIVE job
    that is NOT this callsite, print one classified line:

        <BLOCK|WARN>|<job_id>|<to>|<from>|<age_s>|<why>|<comma-separated overlapping paths>

    Always exits 0 (the CALLER decides what a BLOCK costs — bin/repo_commit_gate.sh does,
    and its override lives in one readable place). Reads job records + /proc only: no git
    state, no new lock file, same principle as job-write-scope-conflict.

    Why this exists next to job-write-scope-conflict rather than inside it: that one is
    OPT-IN (both sides must pass --write-scope to dispatch.sh) and fires at DISPATCH time.
    The 2026-08-12 collision passed straight through it because neither side declared a
    scope and the colliding write was a bare `git commit` by Mike, which never goes near
    dispatch.sh at all. This gate asks the question at the only moment every writer has in
    common — the commit itself — and needs nobody to remember to declare anything.

    Two tiers, because "block whenever any job is live" is unusable here (56% of the last
    14 days of hand-authored commits, measured):
      BLOCK — another live job DECLARED a write_scope overlapping a staged path (hard
              evidence), or a staged path is shared fleet tooling and a live job belongs to
              an agent whose charter is that tooling (SHARED_TOOLING_AGENTS).
      WARN  — some other job is live but nothing points at these paths. Printed, not fatal.
    """
    if not a:
        sys.stderr.write("usage: commit-collision-gate <jobs_dir> [--self-pid N] <path>...\n")
        sys.exit(2)
    jobs_dir, self_pid, paths, i = a[0], os.getpid(), [], 1
    while i < len(a):
        if a[i] == "--self-pid" and i + 1 < len(a):
            self_pid = _as_int(a[i + 1], self_pid)
            i += 2
            continue
        if a[i].strip():
            paths.append(a[i].strip())
        i += 1
    if not paths:
        sys.exit(0)
    # Same liveness definition as job-write-scope-conflict / job-find-dup (round 9, K1):
    # a record closed without verified death still counts as a candidate, then the /proc
    # check decides for real.
    cands = [o for o in _load_jobs(jobs_dir)
             if o.get("status") in LIVE_STATUSES or str(o.get("death_verified", "")) == "0"]
    mine = _self_job_ids(self_pid, cands)
    n = now_epoch()
    for o in cands:
        jid = o.get("job_id", "?")
        if jid in mine or not _job_live_pids(o):
            continue
        scope = [p.strip() for p in str(o.get("write_scope", "")).split(",") if p.strip()]
        hits = sorted({s for s in paths for d in scope if _path_overlaps(s, d)})
        why = "job declared --write-scope covering these paths"
        if not hits and o.get("to") in SHARED_TOOLING_AGENTS:
            hits = sorted(s for s in paths
                          if s.startswith(SHARED_TOOLING_PATHS) or s in SHARED_TOOLING_PATHS)
            why = "shared fleet tooling + live %s job (charter owner, no scope declared)" % o.get("to")
        print("%s|%s|%s|%s|%d|%s|%s" % (
            "BLOCK" if hits else "WARN", jid, o.get("to", "?"), o.get("from", "?"),
            n - _as_int(o.get("started_at"), n),
            why if hits else "live job, no declared or presumed overlap with staged paths",
            ",".join(hits[:8])))
    sys.exit(0)


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
        # A record closed WITHOUT verified death still counts here (round 9, K1). The whole
        # danger of an unverified close is a worker that outlives its record, and the shape it
        # produces is precisely the 2026-08-09 one: the board reads terminal, someone
        # re-dispatches, and the new run collides with the old one that never stopped. Terminal
        # status is only permission to stop WAITING, not evidence that nothing is running.
        live_enough = o.get("status") in LIVE_STATUSES or str(o.get("death_verified", "")) == "0"
        if not live_enough or o.get("to") != to_agent:
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


def _parse_pin(pin):
    """'<dev>:<ino>' as written by cmd_job_pin_log -> (dev, ino), or None."""
    try:
        dev, ino = str(pin).split(":", 1)
        return (int(dev), int(ino))
    except Exception:
        return None


def _pids_holding(path, pin=None):
    """Pids whose stdout/stderr is `path` (or, better, the PINNED inode), from /proc/<pid>/fd.

    The SECOND way to find a job's worker, and the one that still works after the wrapper
    is gone. dispatch.sh's _bg_wrapper redirects the claude process's stdout+stderr to the
    job's own logfile (`_hb_aware_timeout ... > "$logfile" 2>&1`), so that fd is a reliable
    per-job fingerprint. It matters because the PPid tree is NOT enough on its own: once the
    wrapper dies, its setsid'd claude child is reparented to init and becomes invisible to
    _descendants — which is exactly the state Mike's improvised `kill <pid>` left behind on
    2026-08-09, an orphan that went on editing the repo for 33 minutes with nothing pointing
    at it.

    Matching is by INODE first, string only as a fallback, because the readlink text is not
    stable while the answer must be (arch-reviewer round 4, K1). The kernel rewrites it under
    the job's feet in two ordinary ways, and an `==` compare reads both as "not this job":
        rm  <logfile>   ->  /proc/<pid>/fd/2 -> "/…/x.log.err (deleted)"
        mv  <logfile> b ->  /proc/<pid>/fd/2 -> "/…/b.err"
    Either one made `live` come back empty on a job whose worker was provably alive, and the
    very next `job-set status=failed` was then waved through — the 2026-08-09 lie reachable
    again in one unguarded command that is not even a job-set. `st_dev/st_ino` survives the
    rename (same file, new name) and the unlink (the fd still pins the inode), so it answers
    the question actually being asked: is some process holding THIS FILE.

    `pin` is that same identity taken from the RECORD (cmd_job_pin_log stamps it when the job
    starts), and it is strictly better than stat()ing the path now, because the path is the
    part an outside writer controls. With a pin, `mv <logfile> elsewhere` no longer hides the
    worker at all — the fd still points at the pinned inode, so the holder is found and the
    answer is a definite ALIVE instead of round 4's UNKNOWN. Without it, `mv <logfile> x;
    : > <logfile>` put a decoy at the same path: stat() returned the decoy's fresh inode,
    matched nothing, and "no holder + file present" reads as PROVEN DEAD — rc=0 on a live
    worker through the ordinary close path (round 5, N5)."""
    if not path and pin is None:
        return []
    out = []
    try:
        entries = os.listdir("/proc")
    except Exception:
        return []
    target = _parse_pin(pin)
    if target is None:
        try:
            st = os.stat(path)
            target = (st.st_dev, st.st_ino)
        except Exception:
            target = None   # unlinked or renamed away: fall back to the string forms below
    me = os.getpid()
    for entry in entries:
        if not entry.isdigit():
            continue
        p = int(entry)
        if p == me:
            continue
        for fd in ("1", "2"):
            fdp = "/proc/%d/fd/%s" % (p, fd)
            hit = False
            if target is not None:
                try:
                    fst = os.stat(fdp)          # follows the fd to the file it pins
                    hit = (fst.st_dev, fst.st_ino) == target
                except Exception:
                    hit = False
            if not hit:
                try:
                    link = os.readlink(fdp)
                except Exception:
                    continue
                # " (deleted)" is the kernel's own suffix, not part of any real name.
                hit = link == path or link == path + " (deleted)"
            if hit:
                out.append(p)
                break
    return out


# How long after `started_at` an absent logfile still reads as "this job has not opened it
# yet" rather than "someone removed it". dispatch.sh writes the job record (dispatch.sh:994)
# BEFORE the pipeline opens `$logfile`/`$logfile.err`, and the wrapper stamps its own `pid=`
# a moment later — measured well under a second, but it is a real window, and treating it as
# "evidence missing" would refuse dispatch.sh its own opening writes and hang every new job
# at status=running. That is a fleet outage, i.e. the failure mode this guard must not become
# (arch-reviewer round 4, race_idempotency). 120s is ~3 orders of magnitude of slack over the
# measured startup, and still far below any window in which a deletion matters.
EVIDENCE_GRACE_S = 120


def _record_is_pinned(obj):
    """Does this record carry a usable logfile identity? Only a pinned record can support a
    DEAD verdict — see _death_evidence (round 6, K1)."""
    return _parse_pin(obj.get("logfile_ino")) is not None or \
        _parse_pin(obj.get("logfile_err_ino")) is not None


def _live_holder_identity(obj):
    """The (dev, ino) that a LIVE process of this job is actually writing to, as {field: pin}.

    At dispatch time the path is trustworthy because the record was created a moment ago and
    no worker exists yet; afterwards it is not, so a pin taken from the path would just launder
    whatever an outside writer put there — round 6's K3, the fix's own command as the attack.

    The candidate processes therefore come from the RECORDED pid and its descendants ONLY.
    Round 7 (K1) got in through exactly the gap that leaves: the first version asked
    `_job_live_pids`, which on an UNPINNED record — the whole population backfill exists for —
    identifies "the job's processes" by stat()ing the PATH. So whoever held the path was the
    job, and one process holding a decoy for a second got its inode written onto the record as
    the job's permanent identity, after which job-set/reap/cancel all closed a live worker with
    rc=0 while citing the pin. Circular: the pin was derived from the very evidence it exists
    to replace.

    `pid` and its process tree are guarded evidence in their own right (EVIDENCE_FIELDS), so
    they are the one route that does not depend on the path. A SYNC record records no pid and
    therefore CANNOT be backfilled at all — that is the honest answer, not a defect: it stays
    UNKNOWN and drains through reap."""
    logfile = obj.get("logfile") or ""
    root = obj.get("pid")
    if not logfile or root in (None, "", 0, "0"):
        return {}
    try:
        root = int(str(root).strip())
    except Exception:
        return {}
    out = {}
    if not _pid_owned_by_job(root, obj):
        # The NUMBER is on the record; the PROCESS may not be the one it named. cmd_job_cancel
        # already refuses to signal a recycled pid for this reason, and backfill must not be the
        # softer door: with a recycled pid an attacker's own children become "the job's tree"
        # and hand over the inode of their choosing (round 8, NICE 6).
        return {}
    candidates = [root] + _descendants(root)
    for p in candidates:
        for fd in ("1", "2"):
            fdp = "/proc/%d/fd/%s" % (p, fd)
            try:
                link = os.readlink(fdp)
            except Exception:
                continue
            for path, field in ((logfile, "logfile_ino"), (logfile + ".err",
                                                           "logfile_err_ino")):
                # Only the EXACT recorded name counts. A "(deleted)" or renamed link tells us
                # the worker's file is no longer reachable at that path, so there is no
                # identity we could pin that a later reader would find again.
                if field in out or link != path:
                    continue
                try:
                    st = os.stat(fdp)           # follows the fd to the file it pins
                except Exception:
                    continue
                out[field] = "%d:%d" % (st.st_dev, st.st_ino)
    return out


def _path_is_pinned_file(path, pin):
    """True if `path` still IS the file the job opened. Without a pin (legacy records) the
    question degrades to mere existence, which is the best such a record can support."""
    if not path:
        return False
    target = _parse_pin(pin)
    if target is None:
        return os.path.exists(path)
    try:
        st = os.stat(path)
    except Exception:
        return False
    return (st.st_dev, st.st_ino) == target


def cmd_job_pin_log(a):
    """job-pin-log <jobs_dir> <job_id> — create the job's logfile+.err if absent and record
    their (dev, inode) on the record. Called once by dispatch.sh right after the record is
    created; exit 0 always, it must never be able to break a dispatch.

    The point is to fix the job's evidence to an IDENTITY at a moment when nothing has yet
    had a chance to interfere with it, instead of re-deriving it later from a path that any
    writer can repoint. Creating the files eagerly is what makes that possible — the pipeline
    that follows (`> "$logfile"`, `2>"$logfile.err"`, `| tee "$logfile"`) truncates these very
    inodes rather than making new ones — and it also removes the startup window in which an
    absent logfile is normal, i.e. the window EVIDENCE_GRACE_S exists to tolerate.

    Refuses to REPLACE an existing pin. A re-pin would be the decoy attack with an official
    command in front of it: point the record at a fresh file, then have the guard agree that
    the fresh file is the evidence.

    TWO modes, because a pin is only evidence if nothing could have interfered with it yet:
      * CREATE (dispatch time) — allowed only to the dispatcher that owns this record, and
        only inside EVIDENCE_GRACE_S of `started_at`, i.e. while no worker exists and the
        path still means what the record says. This is dispatch.sh's call.
      * BACKFILL (anything later, incl. records created before pinning existed) — takes the
        identity from a LIVE process of the job (_live_holder_identity), never from the path,
        and creates nothing. If nothing live holds the path there is no pin to be had and the
        record honestly stays UNKNOWN.
    Round 6, K3: without this split the command created the files itself and pinned them, so
    one official invocation turned the guard's honest UNKNOWN into DEAD on a live worker."""
    jobs_dir, job_id = a[0], a[1]
    fp = _job_path(jobs_dir, job_id)
    try:
        with open(fp, encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            return
    except Exception:
        return
    logfile = obj.get("logfile") or ""
    if not logfile or _record_is_pinned(obj):
        return                                   # nothing to pin, or already pinned
    fresh_record = (now_epoch() - _as_int(obj.get("started_at"), 0)) <= EVIDENCE_GRACE_S
    if fresh_record and _writer_is_job_dispatcher(job_id, obj):
        pins = {}
        for path, field in ((logfile, "logfile_ino"), (logfile + ".err", "logfile_err_ino")):
            try:
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "a", encoding="utf-8"):
                    pass                         # create-if-absent, never truncate
                st = os.stat(path)
                pins[field] = "%d:%d" % (st.st_dev, st.st_ino)
            except Exception:
                continue
        source = "create"
    else:
        pins = _live_holder_identity(obj)
        source = "backfill"
    if pins:
        pins["pin_source"] = source
    if not pins:
        # Say so ON THE RECORD. A pin that silently never happened downgrades the guard to its
        # pre-round-5 strength on that job, and round 6 found the whole board in exactly that
        # state with nothing anywhere reporting it (K2 / NICE 5).
        if obj.get("status") in LIVE_STATUSES and not obj.get("pin_failed"):
            obj["pin_failed"] = 1
            tmp = fp + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False)
            os.replace(tmp, fp)
        return
    obj.pop("pin_failed", None)
    # Compare-and-set: the /proc walk above takes ~40ms, and a worker finishing inside that
    # window would have its terminal write silently reverted by the stale copy read before it
    # (round 7, NICE). Re-read and abort if anything moved — a missed pin costs nothing, an
    # un-finishing job costs the board its truth.
    try:
        with open(fp, encoding="utf-8") as f:
            fresh = json.load(f)
        if not isinstance(fresh, dict) or fresh.get("status") != obj.get("status") \
                or _record_is_pinned(fresh):
            return
        fresh.pop("pin_failed", None)
        obj = fresh
    except Exception:
        return
    # Written in-process, not through cmd_job_set: this is the FIRST write of these fields on
    # a record that has no live worker yet, and routing it through the guard would only ask
    # the guard to approve the creation of the very evidence it reads.
    obj.update(pins)
    tmp = fp + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, fp)


def _logfile_evidence_missing(obj, now=None):
    """True when the record names a logfile but NEITHER it nor its `.err` sibling is on disk,
    and the job is past the startup window in which that is simply normal.

    Then `_job_live_pids` is not answering "nothing is alive", it is answering "I no longer
    have anything to look at" — and those two must never collapse into the same verdict. A
    rename defeats even the inode match in `_pids_holding` (the old name is gone, so there is
    no inode to compare against), so this is the term that keeps the guard ON when its
    evidence has been removed rather than letting absence read as death (round 4, K1).

    Presence is judged by IDENTITY when the record carries a pin: a file that merely occupies
    the path is not the job's logfile. `mv <logfile> x; : > <logfile>` restored "evidence
    present" while nothing on disk related to the job any more, which is all it took to make
    the close paths believe they had looked and seen nothing (round 5, N5). Records written
    before pinning existed keep the old path test — for them nothing is lost, the pin only
    ever adds a way to say "missing"."""
    logfile = obj.get("logfile") or ""
    if not logfile:
        return False        # nothing was ever claimed; the pid/descendant terms stand alone
    if _path_is_pinned_file(logfile, obj.get("logfile_ino")) or \
            _path_is_pinned_file(logfile + ".err", obj.get("logfile_err_ino")):
        return False
    started = _as_int(obj.get("started_at"), 0)
    if started and (now_epoch() if now is None else now) - started < EVIDENCE_GRACE_S:
        return False       # too young to have a logfile yet — see EVIDENCE_GRACE_S
    return True


def _job_pids(pid, logfile, pin=None):
    """Every live process belonging to this job: the wrapper, its descendants, and any
    process still holding the job's logfile (orphans the tree walk cannot see)."""
    seen, out = set(), []
    cands = _descendants(pid) + _pids_holding(logfile, pin)
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
    pids = _job_pids(obj.get("pid"), logfile, obj.get("logfile_ino"))
    if logfile:
        # A SYNC dispatch pipes the worker's stdout (`... 2>"$logfile.err" | tee "$logfile"`,
        # dispatch.sh:1266), so its fd1 is a PIPE and only fd2 points at a real file. Looking
        # at logfile alone finds nothing for the fleet's DEFAULT dispatch mode (arch-reviewer
        # round 3, N2).
        seen = set(pids)
        for p in _pids_holding(logfile + ".err", obj.get("logfile_err_ino")):
            if p not in seen and p > 1 and _pid_alive(p) is True:
                seen.add(p)
                pids.append(p)
    return pids


# How long the agent's own bus heartbeat must have been SILENT before silence is allowed to
# count as evidence at all. It used to be whatever `grace` the caller of `jobs.sh reap`
# happened to pass, which meant the documented `jobs.sh reap 0` — "close the stale records
# now" — silently set the liveness threshold to zero and closed a record whose agent had
# written a heartbeat that same second (round 5, N4). Agents heartbeat about once a minute,
# so 15 minutes of silence is well outside normal working behaviour and far inside the hour
# that reap's own deadline+grace already requires.
HB_COLD_S = 900

# How long past its deadline a record must sit before reap may close it with NO liveness
# evidence at all — logfile gone AND not one heartbeat ever written. Round 4 let reap close
# these at deadline+grace (1h by default, from watchdog.sh's automatic call), which made the
# fleet's own cron stamp `orphaned` — read as exit 1 = FAILED by every poller, the 2026-08-09
# re-dispatch trigger — onto jobs it had no evidence about; 23 of the last 200 real records
# carry no agent-written bus event, so this was ordinary, not contrived (round 5, K3).
# Closing such a record eventually is still required (a record no command can close is the
# permanent board leak this guard exists to prevent), so the answer is not "never" but "late,
# and said out loud on the record": see the UNVERIFIED wording in cmd_job_reap.
REAP_UNVERIFIED_S = 86400

ALIVE, DEAD, UNKNOWN = "alive", "dead", "unknown"


def _hb_state(obj, now, cold_s=HB_COLD_S):
    """('fresh'|'cold'|'never', age_or_None) from the agent's own bus heartbeats.

    'never' is NOT 'cold'. Round 4 promoted the heartbeat to the independent proof of death
    without noticing that its absence has two completely different causes — an agent that
    fell silent, and an agent that was never observed at all (a job whose agent does not
    heartbeat, a renamed inbox, a record whose `to` was rewritten). Collapsing them made
    "I have never seen this job" argue for closing it."""
    hb = _hb_age(obj, now, agent_only=True)
    if hb == "-":
        return ("never", None)
    age = _as_int(hb, 10 ** 9)
    return ("fresh" if age < cold_s else "cold", age)


def _death_evidence(obj, now=None, hb_cold_s=HB_COLD_S, live=None):
    """Is this job still running? -> (verdict, live_pids, why, hb_state)

    ONE answer for job-set, job-cancel and job-reap. They used to each carry their own
    version of it — three thresholds, three orderings, three opinions about what an absent
    heartbeat meant — and every killer objection of round 5 lived in the gaps between them:
    the heartbeat floor existed in cancel but not in reap, and 'never heartbeated' was
    UNKNOWN to neither. Divergence, not any single line, was the bug.

    Three verdicts, and the middle one is the whole point:
      ALIVE   - something of this job is provably running (holders/descendants), or its agent
                is still writing bus events.
      DEAD    - we could look at the job's own logfile and nothing is holding it.
      UNKNOWN - the evidence itself is gone, so no answer can be given. Callers must NOT
                treat this as DEAD; "I could not check" is not permission to say "stopped".
    """
    n = now_epoch() if now is None else now
    # `live=[]` is how cmd_job_cancel asks the PRE-FLIGHT question: "once my kill has left
    # nothing of this job alive, will the guard let me write the status?" It has to be the same
    # function — round 5's lesson was that divergence between two copies of this reasoning, not
    # any single line, was the bug — so the caller overrides the input rather than reimplementing
    # the tail (round 8, K2).
    if live is None:
        live = _job_live_pids(obj)
    if live:
        return (ALIVE, live, "%d process(es) of the job are alive right now: %s"
                % (len(live), live), ("n/a", None))
    hbs = _hb_state(obj, n, hb_cold_s)
    # DEAD requires the file we looked at to be provably THIS JOB'S file, i.e. a pin.
    # Round 5 fixed the decoy (`mv <logfile> x; : > <logfile>`) by pinning the inode, but left
    # unpinned records falling back to plain path existence — and round 6 measured the cost of
    # that fallback: 0 of 751 records on the live board carried a pin, so the "fixed" attack
    # still closed and reaped a provably live worker with rc=0 on EVERY record that existed.
    # Without a pin, "a file sits at that path and nobody holds it" says nothing about the
    # job: the file may be a decoy planted one second ago. That is UNKNOWN, and the callers
    # already know how to drain UNKNOWN honestly (cold heartbeat -> reap as orphaned; never
    # heartbeated -> REAP_UNVERIFIED_S then closed and MARKED unverified), so refusing to
    # call it DEAD costs no record its eventual closure (round 6, K1).
    if not _logfile_evidence_missing(obj, n) and _record_is_pinned(obj):
        # Say HOW the identity was obtained. "pinned when the job was created" was hardcoded,
        # and false for every backfilled record — the guard overstating the provenance of its
        # own evidence, which is the same failure as overstating the verdict (round 7, K4).
        return (DEAD, [], "the job's own logfile — the exact inode %s — is still on disk and "
                          "no process is holding it"
                          % {"create": "pinned when the job was created",
                              "backfill": "pinned later from the running worker's own file "
                                          "descriptor"}.get(
                                  obj.get("pin_source"),
                                  "on this record (pinned before this field recorded how)"),
                hbs)
    # Two different ways to have no usable logfile evidence, and the guard must say WHICH:
    # claiming the file is GONE when a file is sitting right there is the same species of lie
    # as claiming a heartbeat went cold when none was ever written (round 5, K2 / round 6, K4).
    if _logfile_evidence_missing(obj, n):
        situation = "the job's logfile is GONE (%s)" % (obj.get("logfile") or "?")
    else:
        situation = ("a file occupies %s, but this record carries NO pinned logfile identity, "
                     "so nothing ties that file to this job — it may be a decoy put there "
                     "after the fact" % (obj.get("logfile") or "?"))
    if hbs[0] == "fresh":
        return (ALIVE, [], "%s — but its agent wrote a bus heartbeat %ss ago, it is still "
                           "working" % (situation, hbs[1]), hbs)
    if hbs[0] == "never":
        return (UNKNOWN, [], "%s, and its agent has never written a single heartbeat for it "
                             "— nothing here can tell a finished job from one that is still "
                             "running" % situation, hbs)
    return (UNKNOWN, [], "%s; its agent last wrote a heartbeat %ss ago, which is evidence but "
                         "not proof" % (situation, hbs[1]), hbs)


def _kill_targets_are_identity_backed(obj, targets):
    """Were `targets` identified as this job's processes by IDENTITY, or merely by path?

    This is the question round 8 was decided on. `_kill_tree` returning "no survivors" proves
    only that the pids it happened to enumerate are dead — and on an UNPINNED record those pids
    come from `_pids_holding(path, pin=None)`, i.e. from stat()ing a path an outside writer
    controls. So `mv <logfile> x; sh -c 'exec sleep' > <logfile>; jobs.sh cancel` made cancel
    kill the squatter, report "1 process killed and verified dead", and stamp `cancelled` while
    the real worker kept running: the 2026-08-09 lie, rebuilt out of sanctioned commands, by the
    exemption that was meant to fix the opposite problem.

    A pinned record answers by inode, which no outside write can steer. Failing that, the
    recorded `pid` and its tree are guarded evidence in their own right. Anything else is a
    path match, and a path match must never buy the right to close a record.

    Returns the GRADE, not a yes/no (round 9, K1 — the previous version returned True for both
    of the first two and they are not interchangeable):
      "pinned" — identity by inode. The lookup is COMPLETE: _pids_holding finds every process
                 on that inode, orphans included. "Nothing is alive" is then a fact about the
                 job, and "verified dead" is a sentence this command has earned.
      "tree"   — targets are inside the recorded pid's own tree, ownership checked. Enough to
                 justify the KILL: these really are the job's processes. NOT enough to justify
                 the CLAIM: _descendants is blind to exactly the orphans this guard exists for
                 (see _descendants, and _live_holder_identity's note on the same gap), and this
                 branch is only ever reached with the verdict at UNKNOWN — i.e. just after the
                 other lookup declared itself blind. A job process that left the tree is
                 invisible to BOTH, so "no survivors" is a statement about what was looked at.
      ""       — path match only. No authority at all."""
    if _record_is_pinned(obj):
        return "pinned"
    root = obj.get("pid")
    if root in (None, "", 0, "0"):
        return ""                        # sync dispatch: no independent route exists
    try:
        root = int(str(root).strip())
    except Exception:
        return ""
    if not _pid_owned_by_job(root, obj):
        return ""                        # recycled pid: the number is not the process
    tree = set([root] + _descendants(root))
    return "tree" if (targets and set(int(t) for t in targets) <= tree) else ""


def _cancel_may_close(obj, targets):
    """(may_close, why, verified) — would the guard accept the status write once the kill is
    done, and would the record be allowed to call that death VERIFIED?

    Asked BEFORE anything is killed. Cancel used to do the destructive half and only then
    discover that the bookkeeping half was refused, which left processes dead and the board
    still saying `running` (round 7, K2) — and the fix for THAT handed out a blanket exemption
    that let a decoy close a live job (round 8, K1). Both disappear if the order is simply
    right: find out whether you are allowed to say it, then act.

    `verified` is the round-9 half. Refusing every UNKNOWN outright would refuse ~9 of every 11
    live records on this board (they carry pin_failed=1) and push operators to --force, which
    is no guard at all; so an identity-backed kill may still CLOSE the record — it just may not
    describe the result as verified. Permission to act and permission to assert are different
    permissions, and conflating them is how round 7 became round 8."""
    verdict, _l, why, _hbs = _death_evidence(obj, live=[])
    if verdict == DEAD:
        return (True, why, True)         # provable by the job's own pinned logfile
    if verdict == ALIVE:
        return (False, why, False)       # its agent is still writing events — nothing to claim
    grade = _kill_targets_are_identity_backed(obj, targets)
    return (grade != "", why, grade == "pinned")


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
    return _is_self_or_ancestor(dp, limit=DISPATCHER_HOP_LIMIT)


# How far above the writer dispatch.sh may sit and still be believed to be "me finalising my
# own dispatch". JSET runs python as a DIRECT child of dispatch.sh (1 hop); inside
# _hb_aware_timeout it is one hop further because bash runs the left side of the `| tee`
# pipeline in a subshell (2 hops). 4 is slack for that, not room for a stranger.
# The bound is what stops the grant from leaking DOWNWARD through nested dispatches: peer
# dispatch is routine here, so agent B — sync-dispatched by agent A — runs inside A's
# dispatcher tree and would otherwise be able to stamp A's OWN job failed while A is still
# working (round 3, O5). From B the walk to dispatch.sh(A) is 5+ hops (B's python, B's
# shell, B's claude, A's dispatch.sh...), so the bound refuses it while every real
# dispatch.sh self-write stays inside 2.
DISPATCHER_HOP_LIMIT = 4


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
    holders = set(_pids_holding(obj.get("logfile", ""), obj.get("logfile_ino")))
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


def _within_kill_scope(pid, want):
    """Is `pid` one of the approved pids, or descended from one? A process the worker forks
    during the grace window is the job's and must die with it; a process that merely opened the
    logfile PATH after the pre-flight verdict is not, and was never approved for anything."""
    if want is None:
        return True
    cur = pid
    for _ in range(64):                  # same bounded walk as _writer_belongs_to_job
        if cur in want:
            return True
        if cur <= 1:
            return False
        nxt = _ppid_of(cur)
        if nxt is None or nxt == cur:
            return False
        cur = nxt
    return False


def _kill_tree(obj, grace, allowed=None):
    """SIGTERM everything belonging to the job RECORD, wait up to `grace`, SIGKILL what
    survives. Returns (still_alive, signalled) — `still_alive` empty == fully dead.

    `allowed` bounds WHO may be signalled to the pid set the caller's pre-flight approved, plus
    anything descended from it. Round 9, K2: the pre-flight bounded the DECISION but not the
    KILL SET. Every pass re-collects `_job_live_pids`, which on an unpinned record is a path
    match — so an unrelated process that opened the logfile two seconds AFTER the verdict was
    SIGTERMed and then SIGKILLed inside the grace window, and the record went on to report it
    as one of "N killed". On this host the collateral could have been run_bot.sh or the Discord
    bridge. Survivors are still counted from the FULL enumeration: anything holding the job's
    logfile at the end blocks the stamp whether or not this command was allowed to signal it.
    Fail-closed in both directions — refuse to say it, never kill wider to make it true.

    Takes the record, not (pid, logfile), so it uses the SAME liveness definition as the
    guard — including the `$logfile.err` fd that is the only handle on a sync worker. With
    the old (pid, logfile) form a sync job could be found alive by job-set and yet be
    untouchable by cancel, which left it unclosable by any command at all (round 3, O3).

    Re-collects before every signal pass: a process spawned between listing and signalling
    would be missed by a single pass, and this must not leave a live writer behind — the
    whole point of the command is that the status stamped afterwards is TRUE."""
    want = None
    if allowed is not None:
        try:
            want = set(int(x) for x in allowed)
        except Exception:
            want = set()
    signalled = set()
    still = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for _round in (1, 2):
            for p in reversed(_job_live_pids(obj)):   # children first, don't orphan mid-kill
                if not _within_kill_scope(p, want):
                    continue
                try:
                    os.kill(p, sig)
                    signalled.add(p)
                except Exception:
                    pass
        waited = 0.0
        step = 0.5 if sig == signal.SIGKILL else 1.0
        limit = 2.0 if sig == signal.SIGKILL else float(grace)
        while True:
            still = _job_live_pids(obj)
            if not still:
                return ([], signalled)
            if waited >= limit:
                break
            time.sleep(step)
            waited += step
    return (still, signalled)


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
      3 - cannot act: pid<=1, pid not provably this job's, or cancelling own job
          (a sync record with no pid is NOT in this list any more — see below)
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
        # A SYNC record carries no pid, but that no longer means there is nothing to act on:
        # _job_live_pids finds the worker through the job's own `$logfile.err`, and holding
        # this job's logfile IS proof of ownership (no pid-recycling ambiguity to resolve —
        # that is the only thing the recorded pid was needed for). Before this, such a record
        # could be seen alive by job-set yet refused by cancel and skipped by reap: no
        # command could close it, and the only way out was the --force write this guard
        # exists to prevent (round 3, O3).
        sync_live = _job_live_pids(o)
        if not sync_live:
            # ...but "found nothing" must not be reported as "there is nothing". This branch
            # was a REGRESSION the moment it was written (arch-reviewer round 4, K2): with the
            # logfile deleted, `_job_live_pids` comes back empty on a live worker, and this
            # stamped `cancelled` while asserting in result_summary that no process was
            # holding the logfile — the 2026-08-09 lie with a different verb, reached through
            # the very command the guard's own refusal message recommends. Worse, `job-reap`
            # already refused to stamp such a record while the agent's bus heartbeat was
            # fresh, so cancel was the WEAKER of the two paths to the same write.
            # Both terms are required before an unverified close: the evidence must still
            # exist, and the agent must have stopped heartbeating.
            # Same three-way verdict as job-set and reap (_death_evidence), with cancel's own
            # extra term on top: closing here also requires that the agent be OBSERVED silent.
            # 'never heartbeated' is not silence, it is absence of observation, and round 4
            # spent it as if it were proof — cancel stamped `cancelled` on a live worker while
            # asserting in result_summary that the heartbeat had gone cold (round 5, K3).
            verdict, _l, why, hbs = _death_evidence(o, now_epoch(),
                                                    hb_cold_s=max(int(grace), HB_COLD_S))
            # The heartbeat is a VETO here, not a requirement. A DEAD verdict already means we
            # looked at the job's own logfile — identified by the inode pinned when it was
            # created, so a decoy at the same path does not qualify — and found nobody holding
            # it, which is proof enough for a human asking to close this record. Demanding a
            # heartbeat on top would refuse the 11.5% of real records whose agent never wrote
            # one and push the operator to --force, which is worse than what it prevents.
            if verdict != DEAD or hbs[0] == "fresh":
                sys.stderr.write(
                    "REFUSED: job %s records no pid (sync dispatch) and nothing of it was "
                    "found running — but that is NOT proof it stopped, so this command will "
                    "not stamp one.\n"
                    "  evidence: %s\n"
                    "  agent heartbeat: %s\n"
                    "  Nothing here can be killed and nothing here can be verified dead. "
                    "Establish which it is (bin/trace.sh %s), then close it deliberately:\n"
                    "    bin/jobs.sh reap        (closes it as 'orphaned' once the heartbeat "
                    "has gone cold — the honest status for a dispatcher that died)\n"
                    "    job-set %s status=... --force   (if you have other evidence; it will "
                    "be recorded on the record)\n"
                    % (job_id, why,
                       {"never": "NEVER observed — this job has no heartbeat at all, so its "
                                 "silence says nothing",
                        "fresh": "FRESH (%ss) — the agent is still writing bus events" % hbs[1],
                        "cold": "cold (%ss)" % hbs[1],
                        "n/a": "not consulted"}[hbs[0]],
                       job_id, job_id))
                sys.exit(3)
            # Says what was actually observed. Round 4's fixed wording claimed "the agent's
            # heartbeat has gone cold" even when no heartbeat had ever been seen — the record
            # asserting as fact the one thing nobody had checked (round 5, K3).
            # Round 6, K4: quote the verdict rather than re-describing it, and drop "the
            # dispatcher died" — nobody watched it die; what is known is that no terminal
            # status was ever written.
            note = ("cancelled by operator: no pid recorded (sync dispatch), %s, and %s — no "
                    "terminal status was ever written for this job"
                    % (why,
                       "the agent's heartbeat has been silent for %ss" % hbs[1]
                       if hbs[0] == "cold" else
                       "this job never wrote a heartbeat, so the logfile is the only evidence"))
            print(note)
            cmd_job_set([jobs_dir, job_id, "status=cancelled", "ended_at=%d" % now_epoch(),
                         "exit_code=130", "result_summary=" + note])
            sys.exit(0)
        if _writer_belongs_to_job(sync_live):
            sys.stderr.write(
                "REFUSED: you are running INSIDE job %s — cancelling it would kill this "
                "very command.\n" % job_id)
            sys.exit(3)
        may, why_pre, verified = _cancel_may_close(o, sync_live)
        if not may:
            sys.stderr.write(
                "REFUSED — and NOTHING has been killed: cancelling job %s would leave this "
                "command unable to say so on the record, so it does not start.\n"
                "  evidence: %s\n"
                "  These %d process(es) were found only by the PATH %s, and this record "
                "carries no pinned identity — so killing them would prove nothing about the "
                "job, and stamping 'cancelled' afterwards would be the board asserting a "
                "death nobody established (arch-reviewer round 8).\n"
                "  If the job really is finished, let the honest path close it:\n"
                "    bin/jobs.sh reap        (closes a running record as 'orphaned', marked "
                "UNVERIFIED when nothing proved it stopped)\n"
                "  If you must stop it now, kill it yourself and record what you did:\n"
                "    job-set %s status=cancelled --force ended_at=... result_summary=...\n"
                % (job_id, why_pre, len(sync_live), o.get("logfile") or "?", job_id))
            sys.exit(3)
        print("killing %s: %d live process(es) %s (found via the job's logfile — sync "
              "dispatch records no pid)" % (job_id, len(sync_live), sync_live))
        survivors, signalled = _kill_tree(o, grace, allowed=sync_live)
        if survivors:
            outside = [p for p in survivors if p not in signalled]
            sys.stderr.write(
                "REFUSED to stamp cancelled: %d process(es) SURVIVED SIGTERM+SIGKILL: %s.\n"
                "  The job record is left at status=running ON PURPOSE — a live writer must "
                "never be reported as stopped.\n" % (len(survivors), survivors))
            if outside:
                sys.stderr.write(
                    "  %d of them were never signalled by this command: %s appeared on the "
                    "logfile path after the pre-flight verdict (round 9, K2).\n"
                    % (len(outside), outside))
            sys.exit(5)
        # A sync record carries no pid, so the only way past the pre-flight is a pinned inode
        # (or a DEAD verdict) — `verified` is therefore true here by construction. It is read
        # from the same variable anyway: round 5's lesson is that a second copy of the argument
        # is what drifts, not the argument itself.
        note = ("cancelled by operator: %d process(es) killed and %s (sync dispatch, found by "
                "logfile)" % (len(signalled),
                              "verified dead" if verified else "death NOT VERIFIED"))
        # stale_proven: we did not INFER death here, we caused it and then verified it — proof
        # strictly stronger than the one reap is trusted with. Without passing it, an unpinned
        # record went UNKNOWN and the guard refused the status write AFTER the kill had already
        # happened: processes dead, board still saying `running`, and the record then drifting
        # to `orphaned` hours later, which every poller reads as a failure worth re-dispatching
        # — the very outcome this guard exists to prevent (round 7, K2).
        cmd_job_set([jobs_dir, job_id, "status=cancelled", "ended_at=%d" % now_epoch(),
                     "exit_code=130", "result_summary=" + note], stale_proven=True)
        print(note)                              # only after the write actually landed
        sys.exit(0)
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
    targets = _job_live_pids(o)
    may, why_pre, verified = _cancel_may_close(o, targets)
    if not may:
        # Same pre-flight as the sync branch. Ordering IS the fix: ask whether the truth can be
        # recorded before making it true (round 8, K1/K2).
        sys.stderr.write(
            "REFUSED — and NOTHING has been killed: cancelling job %s would leave this command "
            "unable to say so on the record, so it does not start.\n"
            "  evidence: %s\n"
            "  Either its agent is still writing bus events, or the %d process(es) found are "
            "identified only by a path this record cannot vouch for — killing them would prove "
            "nothing about the job.\n"
            "  bin/jobs.sh reap   closes a running record honestly; job-set --force records a "
            "death you established yourself.\n" % (job_id, why_pre, len(targets)))
        sys.exit(3)
    extra = []
    if targets:
        print("killing %s: %d live process(es) %s" % (job_id, len(targets), targets))
        survivors, signalled = _kill_tree(o, grace, allowed=targets)
        if survivors:
            outside = [p for p in survivors if p not in signalled]
            sys.stderr.write(
                "REFUSED to stamp cancelled: %d process(es) SURVIVED SIGTERM+SIGKILL: %s.\n"
                "  The job record is left at status=running ON PURPOSE — a live writer must "
                "never be reported as stopped.\n" % (len(survivors), survivors))
            if outside:
                sys.stderr.write(
                    "  %d of them were never signalled by this command: %s appeared on the "
                    "logfile path after the pre-flight verdict, so this record cannot vouch "
                    "for them and killing them would prove nothing (round 9, K2).\n"
                    % (len(outside), outside))
            sys.exit(5)
        # Count what was actually signalled, not what the pre-flight listed: the two differ
        # whenever the worker forks during the grace window, and the record should say what
        # this command DID (round 9, NICE).
        if verified:
            note = ("cancelled by operator: %d process(es) killed and verified dead"
                    % len(signalled))
        else:
            # Round 9, K1: the kill was identity-backed (these are the job's own processes),
            # but the record carries no pinned inode, so the lookup that says "nothing is left"
            # is the same one that just came back blind. Close it — leaving it open would only
            # push operators to --force — and say plainly that nobody verified anything.
            note = ("cancelled by operator: %d process(es) killed, death NOT VERIFIED — %s; "
                    "this record has no pinned logfile identity, so a process of this job "
                    "outside the recorded pid's tree would be invisible to this check"
                    % (len(signalled), why_pre))
            extra = ["death_verified=0"]
        killed = True
    else:
        # Round 7, K4: this branch was never given the round-6 treatment. It asserted "nothing
        # holding the job's logfile" without consulting the verdict (true even when the logfile
        # never existed) and "dispatcher died without a terminal status" — a causal claim about
        # an event nobody watched. Quote the verdict, state only what was checked.
        _v, _l, why, _hbs = _death_evidence(o)
        note = ("cancelled by operator: no live process found (recorded pid %s dead); %s — no "
                "terminal status was ever written for this job" % (pid, why))
        killed = False
    # Same reasoning as the sync branch: a verified kill is proof we made, not proof we guessed.
    try:
        cmd_job_set([jobs_dir, job_id, "status=cancelled", "ended_at=%d" % now_epoch(),
                     "exit_code=130", "result_summary=" + note] + extra, stale_proven=killed)
    except SystemExit:
        # The pre-flight said this write would be accepted; if the guard refuses anyway, the
        # state changed under us mid-kill. Say the loud half out loud — the refusal BEFORE the
        # kill announces "NOTHING has been killed", so its twin must not stay silent about the
        # opposite (round 9, NICE).
        if killed:
            sys.stderr.write(
                "  NOTE: the kill ALREADY RAN — %d process(es) of job %s were signalled and "
                "are gone, but the record could not be stamped, so it still says running. "
                "Close it with `bin/jobs.sh reap` or job-set --force; do NOT re-dispatch on "
                "the strength of the record alone.\n" % (len(targets), job_id))
        raise
    print(note)                                  # only after the write actually landed
    # watchdog's per-job OVERDUE debounce marker is dead weight once the record is closed
    om = os.path.join(os.path.dirname(jobs_dir.rstrip("/")), "..", "state", "overdue", job_id)
    try:
        os.remove(os.path.normpath(om))
    except Exception:
        pass


def cmd_job_live_pids(a):
    """job-live-pids <jobs_dir> <job_id> — print the job's live pids, one line, space
    separated (empty output = nothing of this job is running).

    Exposes the guard's own liveness definition to shell callers so they stop reinventing a
    weaker one. dispatch.sh's sync TERM trap uses it to VERIFY the worker really died before
    it stamps a terminal status — `kill` followed by an unverified stamp is exactly the
    2026-08-09 shape."""
    try:
        with open(_job_path(a[0], a[1]), encoding="utf-8") as f:
            obj = json.load(f)
    except Exception:
        sys.exit(4)
    pids = _job_live_pids(obj)
    if pids:
        print(" ".join(str(p) for p in pids))


def cmd_job_list(a):
    """job-list <jobs_dir> [limit] — recent jobs, newest first, with computed ages."""
    jobs_dir = a[0]
    limit = _as_int(a[1], 20) if len(a) > 1 else 20
    n = now_epoch()
    all_jobs = _load_jobs(jobs_dir)
    rows = all_jobs[:limit]
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
    # Pin coverage, as a FOOTER (adding a column would break every parser of the table above).
    # Round 6, K2: the whole board was running unpinned — the guard silently in its weaker,
    # pre-round-5 mode on every record — and nothing anywhere would ever have said so. An
    # unpinned live job is not broken, it just cannot be proven dead; say it out loud.
    # Over EVERY live record, not just the `limit` rows printed above: a job stuck live since
    # last month is exactly the one that scrolls off the default view, and "unpinned" is a
    # property of the board, not of the page being looked at.
    unpinned = [o for o in all_jobs if o.get("status") in LIVE_STATUSES
                and not _record_is_pinned(o)]
    if unpinned:
        # Name the command that ACTUALLY applies. Pointing at `jobs.sh reap` was wrong for
        # every record it listed: reap only touches status=running, and these were all
        # usage_limited/maxturns_pending, which reap skips and cancel declines — the footer
        # sending the operator somewhere that does nothing (round 7, NICE).
        reapable = [o for o in unpinned if o.get("status") == "running"]
        stuck = [o for o in unpinned if o.get("status") != "running"]
        print("\n%d live job(s) with NO pinned logfile identity — cannot be proven dead, so "
              "close paths answer UNKNOWN: %s"
              % (len(unpinned), ", ".join(o.get("job_id", "?") for o in unpinned[:5])
                 + (" …" if len(unpinned) > 5 else "")))
        if reapable:
            print("  %d of them are status=running -> `bin/jobs.sh reap` closes those."
                  % len(reapable))
        if stuck:
            print("  %d are %s — reap SKIPS these (it only handles 'running') and cancel "
                  "declines them; they need --force or the status-classification fix."
                  % (len(stuck), "/".join(sorted({o.get("status", "?") for o in stuck}))))


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


def cmd_has_event_prefix(a):
    """has-event-prefix <bus_dir> <agent_id> <since_iso> <event_type:topic_prefix> [...]

    Same contract as has-event, EXCEPT the topic is matched by PREFIX instead of exact
    equality. Use this — not has-event — whenever the producing agent is instructed to
    write "topic starting with X" and is free to append its own description after X.

    Why it exists (incident 2026-08-04→2026-08-11, kb/coding_guidelines.md §26):
    wags_autofix.sh asks Wags for a topic *beginning with* "wags-fix: <label>", Wags always
    appends a short human-readable summary ("wags-fix: coord-2026-08-11 — gate state_source
    ..."), and the post-condition check used exact has-event — so it NEVER matched, and the
    pipeline reported a perfectly good fix as not-confirmed once a day for a week. Exact
    match is still right for the callers whose producer emits a fixed topic string
    (weekly_ops_audit.sh, fearbuy_weekly_scan.sh, eod_trading_report.sh) — hence a separate
    subcommand rather than loosening cmd_has_event under them.

    Same since_iso discipline as has-event: pass the real dispatch start time, never a
    relative "N hours ago" (a prefix match is BROADER than exact, so a stale event from an
    earlier run with the same label would false-positive even more easily).
    """
    bus_dir, agent_id, since_iso = a[0], a[1], a[2]
    pairs = []
    for spec in a[3:]:
        if ":" not in spec:
            sys.stderr.write("has-event-prefix: bad spec '%s', expected event_type:topic_prefix\n" % spec)
            sys.exit(2)
        etype, topic = spec.split(":", 1)
        pairs.append((etype, topic))
    for e in load_jsonl(_agent_files(bus_dir, agent_id)):
        if e.get("ts", "") < since_iso:
            continue
        for etype, prefix in pairs:
            if e.get("event_type") == etype and e.get("topic", "").startswith(prefix):
                print("MATCH %s %s/%s at %s" % (agent_id, etype, e.get("topic", ""), e.get("ts", "")))
                sys.exit(0)
    print("no match: %s has no event with topic starting with %s since %s (đã quét cả archive)" %
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


def cmd_job_claim_reply(a):
    """job-claim-reply <jobs_dir> <job_id> — ATOMIC test-and-set of replied_at.

    exit 0 = replied_at was EMPTY and this call stamped it -> this caller is the FIRST and
             ONLY one allowed to post the job's result.
    exit 1 = replied_at was already set (its value goes to stdout) -> someone already
             replied; stay silent.
    exit 2 = record missing or unreadable -> NOTHING was written; do not treat as "already
             replied" (that would silently swallow the result) and do not treat as "mine"
             either. Investigate.

    Why this exists next to mark-replied/is-replied: those are two separate processes, so
    two wakeup turns racing on the same job can BOTH read "not replied" before either
    writes, and both post. That gap is exactly the double-answer this guard is for. Here the
    read and the write happen under one flock on <job>.json.lock, so exactly one caller of
    any number of concurrent ones gets exit 0.

    Caveat, stated rather than pretended away: job-set does NOT take this lock (it has its
    own read-modify-write), so a job-set landing in the same millisecond can still drop the
    replied_at stamp. The wakeup callers all go through claim-reply, and dispatch.sh's
    lifecycle writes do not race those turns in practice — the mutual exclusion that matters
    (claim vs claim) is the one enforced.
    """
    jobs_dir, job_id = a[0], a[1]
    fp = _job_path(jobs_dir, job_id)
    os.makedirs(jobs_dir, exist_ok=True)
    lock_fd = os.open(fp + ".lock", os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            with open(fp, encoding="utf-8") as f:
                obj = json.load(f)
            if not isinstance(obj, dict):
                raise ValueError("job record is not a JSON object")
        except FileNotFoundError:
            sys.stderr.write(
                "REFUSED: no job record at %s — cannot claim a reply for a job the board "
                "does not know about. This is NOT 'already replied': check the job id.\n" % fp)
            sys.exit(2)
        except Exception as e:
            sys.stderr.write(
                "REFUSED: job record %s is unreadable (%s) — refusing to write over it.\n"
                % (fp, e))
            sys.exit(2)
        prior = obj.get("replied_at", "")
        if prior:
            print(prior)
            sys.exit(1)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        obj["replied_at"] = stamp
        tmp = fp + ".claim.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        os.replace(tmp, fp)
        print(stamp)
        sys.exit(0)
    finally:
        os.close(lock_fd)


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


def cmd_circuit_tripped(a):
    """circuit-tripped <state_dir> — in ra cac agent DANG THUC SU bi chan, moi dong
    "<agent> <remaining_s>". READ-ONLY: khong sua/khong xoa state (viec don trip het han
    la cua circuit-check, tren duong dispatch).

    Vi sao can lenh rieng thay vi doc thang file: `tripped_until` KHONG bao gio duoc don
    khi het han neu khong co dispatch moi toi agent do — circuit-check don LAZY, chi luc
    dispatch. Nen mot checker doc file va test truthiness (`if c["tripped_until"]:`) se
    bao TRIPPED VINH VIEN cho moi agent tung trip roi khong duoc dispatch lai. Do la
    su co that 2026-08-19: breaker Taylor het han 05:43:03Z, ops_health_check 05:45:07Z
    van bao TRIPPED -> dot mot job Wags(Opus) cho trang thai da tu khoi phuc. Cung ho loi
    voi QUESTION_GRACE_MIN (2026-08-17): quyet dinh escalate tu mot co TUC THOI ma khong
    xet no CON HIEU LUC hay khong."""
    state_dir = a[0]
    n = now_epoch()
    rows = []
    for fp in sorted(glob.glob(os.path.join(state_dir, "*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        tripped_until = _as_int(obj.get("tripped_until"), 0)
        if tripped_until and n < tripped_until:
            agent = os.path.basename(fp)[:-len(".json")]
            rows.append((agent, tripped_until - n))
    for agent, remaining in rows:
        print("%s %d" % (agent, remaining))


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
        "job-live-pids": cmd_job_live_pids, "job-pin-log": cmd_job_pin_log,
        "job-find-dup": cmd_job_find_dup,
        "job-write-scope-conflict": cmd_job_write_scope_conflict,
        "commit-collision-gate": cmd_commit_collision_gate,
        "terminal-statuses": cmd_terminal_statuses,
        "job-field": cmd_job_field, "job-hb-age": cmd_job_hb_age,
        "job-claim-reply": cmd_job_claim_reply,
        "circuit-check": cmd_circuit_check, "circuit-record": cmd_circuit_record,
        "circuit-tripped": cmd_circuit_tripped,
        "pending-resume-set": cmd_pending_resume_set,
        "settings": cmd_settings, "trace": cmd_trace,
        "verify-coverage": cmd_verify_coverage, "has-event": cmd_has_event,
        "has-event-prefix": cmd_has_event_prefix}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.stderr.write("usage: mike_json.py <%s> ...\n" % "|".join(CMDS))
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
