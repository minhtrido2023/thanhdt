---
kind: incident
date: 2026-08-01
topic: dispatch-max-turns-export-missing
title: >-
  2026-08-01: MAX_TURNS missing from --bg export list — every background dispatch fleet-wide
  broken for ~1h10m, caught mid-research by Mike, root-caused via bash -x trace, fixed same-turn
status: fixed
category: dispatch-orchestration
origin: >-
  commit c0c85c27 (12:06 UTC) added a --max-turns override, replacing a hardcoded literal inside
  _bg_wrapper with a variable reference, without adding that variable to the export list that
  hands state to the detached _bg_wrapper process
recorder: Mike, caught while dispatching Taylor research (job Taylor_20260801_130227 and 2 retries)
---

# 2026-08-01: `MAX_TURNS` missing from `--bg` export list — every background dispatch fleet-wide broken for ~1h10m

**What happened:** three consecutive Taylor `--bg` dispatches failed instantly (both attempts
each, ~7s runtime) with `error: option '--max-turns <turns>' argument '--model' is invalid.
must be a number`. This was not specific to Taylor or to this prompt — **every `--bg` dispatch
for every agent** issued between 12:06 UTC (commit `c0c85c27`) and 13:17 UTC (fix) would have
failed identically. The circuit breaker correctly tripped for Taylor after 3 real fails.

## Root cause

Commit `c0c85c27` (same day, 12:06 UTC — "feat(dispatch): --max-turns override") replaced the
old hardcoded literal `--max-turns 50` inside `_bg_wrapper`'s body with `--max-turns $MAX_TURNS`,
a variable reference. `_bg_wrapper` is not a plain subshell — the `--bg` path re-execs it in a
genuinely separate process (`bash -c '_bg_wrapper'`, optionally wrapped in `systemd-run --scope`)
via `export -f _bg_wrapper ...` plus an explicit `export VAR1 VAR2 ...` list of every variable
the function body touches. Only *exported* names survive into that fresh process; a plain script
variable does not, regardless of scope in the original process.

The commit added `MAX_TURNS` as a new script variable and wired it into two invocation sites
(`--bg` and sync), but the accompanying `export ROOT JOBS_DIR job_id from id ts TIMEOUT RETRIES
CLAUDE dispatch_prompt logfile prompt CIRCUIT_DIR CIRCUIT_THRESHOLD CIRCUIT_COOLDOWN MODEL_FLAG
EFFORT_FLAG MAX_EXT HB_FRESH_S` list (`bin/dispatch.sh:753-754`) was not updated to include it.
Inside the detached process, `$MAX_TURNS` resolved to empty. Unquoted expansion of an empty
variable vanishes entirely under word-splitting, so the actual argv passed to `claude` became
`... --max-turns --model opus --effort high` — `--max-turns` silently swallowed the literal
string `--model` as its value, and the CLI rejected it as non-numeric.

**Why it worked right up until 12:06 UTC and not after:** the *old* code had the literal `50`
baked directly into the function body text (which IS preserved correctly by `export -f`, since
that exports the function's source, not its runtime variable bindings) — no cross-process
variable dependency existed before this commit. The sync (non-`--bg`) path was never affected —
it runs `_hb_aware_timeout` inline in the same process, so `$MAX_TURNS` was always in scope
there without needing export.

**Why the committing session's own verification missed it:** the commit message states
`--max-turns` validation was unit-tested in isolation ("giá trị sai → exit 1... giá trị đúng →
pass qua validation") — this exercises the arg-parsing/validation code path only, never the
actual `--bg` end-to-end re-exec. `bash -n` and `shellcheck_gate` both passed cleanly because
the bug is a semantic export-list omission, not a syntax or lint-detectable pattern. This is the
same class of gap `.claude/skills/quant-research/SKILL.md` (written the same session, for a
different reason) names generally: **verify by running the real path, not by reading the diff or
testing a narrower unit in isolation.**

## How it was caught

Mike dispatched a Taylor research job 3 times, all failing identically and near-instantly.
Ruled out prompt-content/backtick-quoting corruption (the exact bug class from earlier today,
`kb/coding_guidelines.md` §15) by re-checking the prompt for stray `` ` ``/`"` — none found.
Ruled out prompt-length/content as the trigger via a trivial "ping test" dispatch, which failed
identically. Compared file mtime (`stat`) against the timestamps of two *successful* dispatches
earlier the same session — found `bin/dispatch.sh` was modified at 12:06 UTC, squarely between
the successful and failing dispatches, by a **different concurrent session** (per this repo's
multi-session Discord-thread architecture). `git show c0c85c27` looked correct on read — the
call-site diff (`--max-turns $MAX_TURNS $MODEL_FLAG $EFFORT_FLAG`) is textbook-correct bash.
Manually reproducing the exact same `claude` CLI invocation in isolation (same flags, same
`setsid`+background+redirect pattern) **succeeded every time** — proving the bug wasn't in the
CLI or the flag combination itself. Only `bash -x bin/dispatch.sh ...` full tracing of a real
dispatch (via `DISPATCH_FORCE=1` to bypass the now-tripped circuit breaker for one diagnostic
probe) surfaced the actual final argv reaching `claude`, which showed `--max-turns` correctly
followed by a real value in the *trace of the top-level script* — the empty-variable failure
only manifests inside the *detached* `_bg_wrapper` process, invisible to a trace of the parent.

## Fix

One line: add `MAX_TURNS` to the export list, `bin/dispatch.sh:753-755` (commit `683d533e`).

## Verification

1. `bash -n bin/dispatch.sh` — syntax OK.
2. `DISPATCH_FORCE=1` real `--bg` dispatch with the exact same flags that failed before the fix
   (`Taylor_20260801_131701`) — completed `status=done exit_code=0` on attempt 1, no retry.
3. Circuit breaker for Taylor auto-reset to `{"fails": 0, "tripped_until": 0}` on that success
   (no manual state edit needed).
4. Real research dispatch re-issued through the normal (non-forced) path immediately after —
   ran cleanly past the instant-fail window (confirmed via `jobs.sh status` + fresh heartbeat).

## Lesson

Adding a new script-level variable that a function re-executed in a detached process depends on
requires updating **two separate places that must be kept in sync by hand**: the variable's own
definition/validation, and the `export` list that carries it into that process. This export list
has no compiler/linter that flags "variable used inside an `export -f`'d function body but not
itself in the adjacent `export VAR1 VAR2...` line" — it's a structural gap `shellcheck_gate.sh`
cannot catch (ShellCheck reasons about a single process's scope, not about which variables cross
an `export -f` + re-exec boundary). **Not evaluated for automation this session** (time-boxed
against getting the actual blocked research unblocked) — a plausible future mechanization: a
selfcheck script that greps `bin/dispatch.sh` for every bareword variable referenced inside the
`_bg_wrapper` function body and asserts each one appears in the `export` list a few lines below,
similar in spirit to `ops_health_check_selfcheck.py`'s extract-and-test pattern. Left as a
documented gap, not shipped, per this fleet's convention of not shipping a check nobody has
verified catches the real bug and only the real bug.
