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


def cmd_recent(a):
    inbox_dir = a[0]
    limit = int(a[1]) if len(a) > 1 else 20
    evs = load_jsonl(sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))))
    evs = [e for e in evs if e.get("event_type") in ("finding", "answer", "decision")]
    evs.sort(key=lambda e: e.get("ts", ""), reverse=True)
    for e in evs[:limit]:
        print(fmt_event(e))


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
        rows.append((r.get("agent_id", "?"), r.get("kind", "child"), disp, hb, age,
                     r.get("current_task", "")))
    print("# Fleet status — %s UTC\n" % n.strftime("%Y-%m-%dT%H:%M:%S"))
    print("| agent | kind | status | last_heartbeat | age(min) | current_task |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        print("| %s | %s | %s | %s | %s | %s |" % row)


def cmd_settings(a):
    hooks_dir, aid = a
    def hook(name, script):
        return {name: [{"hooks": [{"type": "command",
                                   "command": "%s/%s %s" % (hooks_dir, script, aid)}]}]}
    s = {"hooks": {}}
    s["hooks"].update(hook("SessionStart", "session_start.sh"))
    s["hooks"].update(hook("UserPromptSubmit", "user_prompt_submit.sh"))
    s["hooks"].update(hook("Stop", "stop.sh"))
    print(json.dumps(s, indent=2, ensure_ascii=False))


CMDS = {"event": cmd_event, "heartbeat": cmd_heartbeat, "recent": cmd_recent,
        "format-events": cmd_format_events, "fleet-status": cmd_fleet_status,
        "settings": cmd_settings}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.stderr.write("usage: mike_json.py <%s> ...\n" % "|".join(CMDS))
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
