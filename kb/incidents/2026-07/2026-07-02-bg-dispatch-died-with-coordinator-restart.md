---
kind: incident
date: 2026-07-02
topic: bg-dispatch-died-with-coordinator-restart
title: >-
  2026-07-02 — Background dispatch job died when the coordinator's own session restarted
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-02 — Background dispatch job died when the coordinator's own session restarted

**What happened:** Job `Taylor_20260702_113418` was dispatched `--bg`, appeared to hang,
then was found dead (0-byte log, job board stuck at `status=running` past deadline →
OVERDUE) with no error trace. Had to be re-dispatched from scratch.

**Root cause:** The background job was being watched via a foreground Bash/Monitor call
inside Mike's own live conversation. Mike's session itself restarted mid-watch (context
compaction/reconnect) and the watching process died with it — taking the "background"
job along, because a plain `&` background job is still a child of the same session as
whoever called `dispatch.sh`.

**Fix:** `dispatch.sh --bg` now runs its wrapper via `setsid bash -c '_bg_wrapper'`,
detaching it into its own session so it survives the caller's session dying (standard
Unix daemonization — Stevens, *Advanced Programming in the UNIX Environment*). Required
`export -f` for every function (not just variables) the wrapper closes over, since
`setsid` execs a command via `execvp`, not through bash's function table — verified
empirically that a plain `setsid _bg_wrapper &` silently fails to find `_bg_wrapper` as a
command. Bundled into consolidate commit `5e79a25`.

**Codified as a standing rule** (MIKE.md, commit `d7c2121`): never watch a background job
with a foreground Bash/Monitor call that keeps the coordinator's own turn open — dispatch
`--bg`, move on, use `ScheduleWakeup` to come back and poll `bin/jobs.sh status <job_id>`.
Paired with a second rule from the same review: verify the real deliverable artifact
before treating a dispatch as failed, never trust self-reported job status alone (a job
can report "timeout" even though the underlying work finished correctly).

**Lesson:** Coordination code that *watches* work is itself a process with a lifecycle —
if the watcher's lifecycle is coupled to the coordinator's own conversation, the
coordinator's own instability (context limits, reconnects) becomes a source of job
failures unrelated to the actual work.
