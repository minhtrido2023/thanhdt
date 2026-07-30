---
kind: incident
date: 2026-06-27
topic: taylor-winston-callback-pingpong
title: >-
  2026-06-27/28 — Taylor↔Winston auto-callback ping-pong (runaway dispatch loop)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-06-27/28 — Taylor↔Winston auto-callback ping-pong (runaway dispatch loop)

**What happened:** Two agents auto-callback-notified each other's completion in a loop
with no terminal condition — Taylor's completion triggered a callback dispatch to
Winston, whose own completion (of processing that callback) triggered a callback back to
Taylor, indefinitely.

**Fix:** `dispatch.sh`'s auto-callback logic now guards against callback-of-a-callback: a
job whose prompt is itself `[AUTO-CALLBACK...]` does not spawn another auto-callback — it
is treated as terminal (process the result, stop). See the `GUARD (2026-06-28)` comment
in `bin/dispatch.sh` (`_bg_wrapper`, both the success and failure notification paths).

**Lesson:** Any "notify the caller when done" convenience feature between autonomous
agents needs an explicit termination condition from day one — a bidirectional
notification pattern is a cycle waiting to happen.
