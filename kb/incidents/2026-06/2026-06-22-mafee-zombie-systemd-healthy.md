---
kind: incident
date: 2026-06-22
topic: mafee-zombie-systemd-healthy
title: >-
  2026-06-22 — Mafee ZOMBIE: systemd reports healthy, agent isn't actually serving
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-06-22 — Mafee ZOMBIE: systemd reports healthy, agent isn't actually serving

**What happened:** `systemctl is-active` reported the Mafee unit as active/healthy, but
the agent wasn't actually serving any session — host process alive, journal said "Ready",
but no live session existed. A plain `systemctl restart` did NOT recover it (verified).

**Root cause:** The remote-control bridge was pinned to a stuck environment via a stale
`bridge-pointer.json` and never reached a real "Ready" state for a new session, even
though the systemd unit itself looked fine from the outside.

**Fix:** `bin/is_serving.py` — a liveness oracle stronger than `systemctl is-active`,
checking for an actual live session record. `bin/watchdog.sh` now detects two distinct
failure modes (DOWN vs ZOMBIE) and, for ZOMBIE, auto-recovers by moving the stale
`bridge-pointer.json` aside (`clear_bridge()`) before restarting — forcing the host to
provision a fresh environment. Verified: plain restart alone did not recover Mafee;
clear_bridge + restart did, serving again in ~10s. Commits `da3c173` (detection),
`4e1c59b` (auto-recovery).

**Lesson:** "The process is running" and "the process is doing its job" are different
claims — a health check that only verifies the former will report false-healthy on a
whole class of failures. Verify the actual deliverable/behavior, not just liveness (same
principle as the artifact-vs-self-report rule from the 2026-07-02 job-watching incident).
