---
kind: incident
date: 2026-07-06
topic: taylor-notification-wrong-topic
title: >-
  2026-07-06 — Taylor's completion notification leaked into whichever topic Mike was in, not the one that asked
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 — Taylor's completion notification leaked into whichever topic Mike was in, not the one that asked

**What happened:** User runs two SEPARATE Discord topics for two research streams ("8L
research" and "vĩ mô" macro research), both dispatching tasks to the SAME agent, Taylor.
When a Taylor job finished, its "✅ xong" notification landed in whatever topic Mike
happened to be active in at completion time — not necessarily the topic that dispatched
that specific job.

**Root cause:** Every notification site in `dispatch.sh` resolved its target thread via
`${DISCORD_THREAD_ID:-$(_agent_thread_override "$id")}`, falling back to
`agents/Mike/state/ccdb_thread_id` — a single GLOBAL "last topic Mike was active in"
pointer, overwritten by `hooks/session_start.sh` every time Mike starts/resumes in ANY
topic. `_agent_thread_override()` (built for the earlier 2026-07-01 DollarBill
thread-leak) only solves the case where an agent's output ALWAYS belongs to ONE fixed
topic — it doesn't help when the SAME agent (Taylor) legitimately serves MULTIPLE
concurrent topics, since there's no per-job memory of which topic asked for THAT
specific piece of work. No durable record existed anywhere of "which topic dispatched
this job" — every read was either a live env var or a clobbered global pointer.

**Fix:** `dispatch.sh` now captures `discord_thread_id` ONCE, at dispatch time, into the
job's own persistent record (`bus/jobs/<job_id>.json`) — the same durable, per-job
source of truth already used for the circuit breaker / idempotency-key / trace_id work.
New helper `_job_thread_id <job_id>` (+ `mike_json.py job-field`) reads it back. Every
notification site (immediate "🚀 nhận việc", `_job_watcher` progress/anomaly pings,
`_bg_wrapper` success/failure, circuit-breaker trip, usage-limit auto-resume) now reads
the job's OWN persisted topic first, falling back to the old env-var/state-file chain
only if that field is somehow missing (e.g. an in-flight job dispatched before this fix).

Verified end-to-end: dispatched a real `--bg` job with a distinguishable fake topic ID,
then overwrote both `DISCORD_THREAD_ID` and the state file to a DIFFERENT fake topic
(simulating Mike becoming active in another topic before the job finished) — confirmed
`_job_thread_id` still resolved to the ORIGINAL dispatch-time topic, ignoring the
simulated "current topic" entirely. Circuit-breaker and job-record regression checks
re-run clean.

**Lesson:** A per-agent static override (`_agent_thread_override`) generalizes badly —
it silently assumes 1 agent ⇒ 1 topic, which breaks the moment a user legitimately runs
that agent from more than one place. The robust fix is always to make the calling
context part of the PERSISTENT RECORD of the work item itself (the job), not something
re-derived live from "whatever's currently true" — the same principle behind the
trace_id and idempotency-key fixes earlier this week.
