---
kind: incident
date: 2026-08-02
topic: max-turns-auto-continuation
title: >-
  2026-08-02: 5 job failed "Reached max turns (50)" in one day, all attempt 2/2 with an
  unchanged cap — added effort-scaled defaults + auto-continuation with a bumped ceiling
status: fixed
category: dispatch-orchestration
origin: >-
  dispatch.sh's retry loop treated a max-turns exhaustion the same as any other transient
  failure (retry unchanged) even though it's a deterministic budget signal, not a fluke
recorder: Mike, user-reported ("một số job bị failed vì quá 50 tasks... chạy tới chạy lui")
---

# 2026-08-02: max-turns auto-continuation — stop retrying with the same cap

**User question:** several jobs failing on "over 50 tasks" — is this normal, should the limit
be adjusted to match real task size so we're not running the same heavy task back and forth,
is there a better solution.

**Data first, before designing anything:** grepped `logs/*.log` for "Reached max turns" — 29
occurrences total in fleet history, **5 of them today alone** (`Taylor_20260802_060243`,
`_141725`, `_143541`, `_154231`, `Wags_20260802_160902`). Every one of the 5 was `attempt: 2 /
max_attempts: 2` — i.e. dispatch.sh's own built-in retry (`--retries 1` default) had ALREADY
fired once and failed identically, because the retry reused the exact same `--max-turns 50` as
the first attempt. All 5 were `model=opus effort=high` — genuinely complex multi-step audits
(a same-day "Price/Close adjustment saga," a Discord topic-routing investigation, a chain of
dividend/data-integrity audits), not runaway loops.

**Root cause:** `dispatch.sh` already had a `--max-turns` override (added 2026-07-31 after an
earlier version of this exact problem, `Winston_20260731_062642`) but the fix at the time was
purely *manual* — the caller has to notice in advance and pass a higher value. In practice this
wasn't happening (none of today's 5 failing dispatches passed `--max-turns`), and the retry loop
had no logic to react to a max-turns failure specifically — it just retried with the same
parameters, spending a full second dispatch for zero chance of success once the task genuinely
needs more than 50 turns.

**Answer to "is this normal":** the *mechanism* being a hard cap is normal and correct (a
runaway loop must still be bounded) — the CLI's own `--max-turns` flag doesn't have a "give me
unlimited" option and shouldn't. What was NOT reasonable: (a) the default never adapting to a
task's declared complexity, and (b) the retry not distinguishing "ran out of budget" (a known,
recoverable, deterministic condition) from "something is actually broken" (worth investigating
before blindly repeating).

## Fix — two layers, same shape as the existing usage-limit auto-resume mechanism

**1. Proactive: default `--max-turns` now scales with `--effort`** when the caller omits it —
`high` → 80, `xhigh`/`max` → 120, everything else stays 50. `effort=high/opus` already signals
"this is complex" per MIKE.md's model ladder; reusing that existing signal costs nothing extra
and reduces how often the ceiling is hit at all for tasks that self-identify as heavy.

**2. Reactive: auto-continuation on an actual max-turns failure**, mirroring
`_maybe_schedule_usage_resume`'s proven shape (`bin/dispatch.sh`, `bin/resume_pending.py`,
`bus/pending_resumes/`) but adapted for a different failure signature:
- **In-loop bump**: if a max-turns failure happens and dispatch.sh's own retry loop has an
  attempt left, DOUBLE `--max-turns` (capped at `DISPATCH_MAX_TURNS_CEILING`, default 200) and
  retry immediately — no cron round-trip needed, cheaper than the cross-dispatch path.
- **Cross-dispatch resume**: only once ALL in-loop attempts are exhausted, queue a
  `bus/pending_resumes/` record (`kind: "max_turns"`) that `resume_pending.py` fires almost
  immediately (~30s, no reset-time to wait for, unlike usage-limit) with the ceiling bumped
  again and the original `--model`/`--effort` preserved.
- **Bounded**: `DISPATCH_MAX_TURNS_RESUMES` (default 2) stops the chain and escalates to a
  human/Mike if a task genuinely can't finish even with a much higher ceiling — "the task may be
  too large to auto-split, consider splitting it by hand" rather than looping forever.
- **Companion fix**: `resume_pending.py`'s `fire()` previously dropped `--model`/`--effort` on
  EVERY resume, including usage-limit ones — an opus/high task resuming after a usage-limit
  pause silently fell back to sonnet/medium defaults. Now both resume kinds preserve them.

**Extended, not duplicated:** `bin/mike_json.py pending-resume-set` gained 4 optional trailing
args (`kind`, `model`, `effort`, `max_turns`) with the original 6-arg call staying byte-for-byte
compatible (`kind` defaults to `"usage_limit"` when omitted) — verified both call shapes
directly before touching the caller.

## Verification (ran the whole chain, not just read it)

1. `bash -n` on `dispatch.sh`, syntax check on the two `.py` files, `shellcheck_gate.sh` /
   `pre-commit run --all-files` — clean, no new hard-blocks introduced.
2. **Caught my own bug before testing further**: the new functions/vars are referenced inside
   `_bg_wrapper`, which runs in a `systemd-run --scope` detached child that only inherits
   explicitly `export -f`/`export`ed names (2026-07-09 cgroup-detach mechanism) — had to add
   `_maybe_schedule_maxturns_resume`, `_looks_like_max_turns`, `_bumped_max_turns`,
   `_current_maxturns_resume_count`, `MAXTURNS_CEILING`, `MODEL`, `EFFORT` to the existing
   export lists, or the detached child would fail with "command not found" the first time this
   path actually fired in production.
3. **End-to-end with a real dispatch**, `DISPATCH_CLAUDE_BIN` pointed at a mock `claude` that
   always prints `Error: Reached max turns (50)` and exits 1 (the exact signature copied from
   `logs/dispatch_Taylor_20260802_154231.log`): dispatched a throwaway test agent with
   `--model opus --effort high --timeout 15`. Confirmed: attempt 1 ran at `--max-turns 80`
   (effort-scaled default), attempt 2 (in-loop bump) ran at 160, and after both failed the job
   record showed `status: maxturns_pending`, `result_summary` citing the bump to 200 (capped),
   and a `bus/pending_resumes/` record with `kind: "max_turns"`, `model: "opus"`,
   `effort: "high"`, `max_turns: 200`.
4. Manually fired `resume_pending.fire()` against that pending record (stubbing
   `subprocess.run` to capture the constructed argv instead of spending a real session) —
   confirmed the resumed dispatch call carries `--model opus --effort high --max-turns 200
   --thread <topic>` and the `[RESUME sau max-turns #1, ...]`-prefixed continuation prompt.
   Repeated with an old-format (pre-2026-08-02) 6-arg pending record — correctly defaults to
   `kind="usage_limit"` and produces the original resume prompt with no extra flags, confirming
   backward compatibility.
5. Cleaned up all test artifacts (throwaway agent dir, test job/pending-resume records, log
   files) before committing — none of it is tracked in git.
