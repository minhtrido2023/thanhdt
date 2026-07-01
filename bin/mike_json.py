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
  fleet-status <registry_dir>
      -> markdown fleet table; status shown as "dead" when last_heartbeat > 30 min old
  settings <hooks_dir> <agent_id>
      -> a child's .claude/settings.json wiring the 3 hooks
"""
import sys, os, json, uuid, glob, datetime

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


def fmt_event(e):
    p = e.get("payload")
    ps = p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)
    return "- [%s] %s/%s — %s: %s" % (
        e.get("ts", ""), e.get("agent_id", "?"), e.get("event_type", "?"),
        e.get("topic", ""), ps,
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
    return "- [%s] %s/%s — %s: %s" % (
        e.get("ts", "")[:19], e.get("agent_id", "?"), e.get("event_type", "?"),
        e.get("topic", ""), ps,
    )


def cmd_event(a):
    aid, etype, topic, payload, kbver = a
    try:
        p = json.loads(payload)
    except Exception:
        p = payload
    try:
        v = int(kbver)
    except Exception:
        v = 0
    out({"event_id": str(uuid.uuid4()), "ts": now_iso(), "agent_id": aid,
         "event_type": etype, "topic": topic, "payload": p, "kb_version": v})


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


def cmd_job_list(a):
    """job-list <jobs_dir> [limit] — recent jobs, newest first, with computed ages."""
    jobs_dir = a[0]
    limit = _as_int(a[1], 20) if len(a) > 1 else 20
    n = now_epoch()
    rows = _load_jobs(jobs_dir)[:limit]
    print("%-26s %-18s %-9s %6s %7s %4s" % ("JOB_ID", "FROM->TO", "STATUS", "AGE", "LOG_AGE", "ATT"))
    for o in rows:
        age = n - _as_int(o.get("started_at"), n)
        print("%-26s %-18s %-9s %5ss %6ss %2s/%s" % (
            o.get("job_id", "?")[:26],
            ("%s->%s" % (o.get("from", "?"), o.get("to", "?")))[:18],
            _job_display_status(o, n)[:9],
            age, _log_age(o, n),
            o.get("attempt", "?"), o.get("max_attempts", "?"),
        ))


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
              "logfile", "prompt_summary", "result_summary"):
        if k in o:
            print("%-15s %s" % (k + ":", o[k]))
    print("%-15s %s" % ("display:", disp))
    print("%-15s %ss" % ("log_age:", _log_age(o, n)))
    st = o.get("status", "?")
    if disp == "OVERDUE":
        sys.exit(3)
    if st == "done":
        sys.exit(0)
    if st in ("running", "retrying"):
        sys.exit(2)
    sys.exit(1)  # failed / timeout / unknown


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
        "job-set": cmd_job_set, "job-list": cmd_job_list, "job-get": cmd_job_get,
        "settings": cmd_settings}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.stderr.write("usage: mike_json.py <%s> ...\n" % "|".join(CMDS))
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
