---
kind: incident
date: 2026-08-01
topic: shellcheck-precommit-gate
title: >-
  2026-08-01: turned the "escape quotes in dispatch prompts" lesson from prose into a
  pre-commit ShellCheck gate — 4th real instance found and fixed in the process
status: fixed
category: dispatch-orchestration
origin: >-
  coding_guidelines.md kept accumulating narrative lessons with no mechanism to actually
  enforce them — the exact bug class documented earlier today (unescaped "/` in dispatch-
  prompt bash strings) recurred a 4th time in a file nobody had touched yet
recorder: Mike, user mandate ("nghiên cứu chuẩn mực ngành... giải quyết triệt để")
---

# 2026-08-01: ShellCheck pre-commit gate — encoding the quoting lesson as a tool, not prose

**Mandate:** user asked, after today's 3 quoting incidents (daily_retro.sh, kb_nightly.sh ×2),
to research industry standard practice for "pushing old lessons into tooling/linters instead of
prose" and apply it thoroughly, rather than adding a 4th paragraph to `kb/coding_guidelines.md`
that depends on someone remembering to re-read it.

## Research (WebSearch, summarized)

- **Google SRE postmortem culture**: the best postmortem action item is a CI rule that would
  have caught the bug, not a note to remember it — "connection leak in new endpoint" escalates
  from "fix the leak" to "add a CI rule that catches every future leak before it ships."
  Organizations tracking this report repeat-incident rates dropping 45%→12% over 6 months when
  action items systematically escalate to automation instead of documentation.
- **pre-commit framework** (pre-commit.com) is the current (2025-2026) standard mechanism for
  wiring linters into `git commit` itself — ShellCheck and Ruff are the standard picks for
  bash/Python respectively, both distributed as pip packages needing no sudo/system install.
- **Semgrep** is the standard tool for codifying *organization-specific* institutional knowledge
  ("a senior engineer discovers a subtle misuse of an internal API... write a rule that catches
  it everywhere") as opposed to generic language bugs. Explicit guidance: write the rule FROM a
  real incident, test it against real files, and prefer "a rule that fires twice at 100%
  accuracy over one that fires 200 times at 50%" — i.e. don't ship an imprecise rule.

## What got built

**`bin/shellcheck_gate.sh`** + **`.pre-commit-config.yaml`** — `pre-commit install`s a real git
hook (confirmed shared across all worktrees of this repo, verified via `git rev-parse
--git-path hooks/pre-commit` from a second worktree) that runs ShellCheck (`pip install
shellcheck-py`, no sudo) on every changed `.sh` file at `git commit` time.

**Key design decision — curated hard-block list, not "block on any finding":** a raw
`shellcheck bin/*.sh` run across the existing 45-script codebase returns 76 pre-existing
findings (0 error / 23 warning / 49 info / 4 style). Blocking on all of them would stop every
future commit dead pending a full backlog cleanup — not what "prevent recurrence" means in
practice. Instead `HARD_BLOCK_CODES` starts with exactly the 4 codes empirically proven to catch
today's real incidents (tested against the actual historical buggy commits, not synthesized):

| Code | Severity (ShellCheck default) | Incident it catches |
|---|---|---|
| SC1078/SC1079 | warning/info | kb_nightly.sh item 5b — unescaped `"` around "cực kỳ phức tạp" |
| SC2006 | style | kb_nightly.sh item 7 — raw backtick around `` `kb/current_ops.md` `` |
| SC2261 | error | daily_retro.sh — quote break leaves "multiple redirections" |

Everything else ShellCheck finds is printed as non-blocking advisory. New incident classes grow
this list the same way a semgrep rule grows from a real bug: add the SC code in the same commit
as the fix + the `kb/incidents/` entry that names it, never speculatively.

**Tried and dropped: SC2154** (variable referenced but never assigned) — real signal for
daily_retro.sh's `draft_prompt` never getting assigned, but produces false positives across
`hooks/*.sh` where variables are legitimately set via a `source` chain ShellCheck doesn't
auto-follow by default (confirmed via `pre-commit run --all-files`: 4 false blocks on
`hooks/_directives.sh`, `session_start.sh`, `user_prompt_submit.sh`, `stop.sh`, all citing
`SC1091 "Not following"` on the same line). SC2261 alone still catches the daily_retro.sh
incident class without it — dropped rather than accept false positives eroding trust in the gate.

**4th real bug found while validating the gate against the whole repo** (before ever committing
anything): `bin/fleet_housekeeping.sh:51` — an *unquoted* `cat <<EOF` heredoc (needed for `$LOG`
interpolation elsewhere in the same block) containing literal-prose text `` `datacold` `` that
bash silently executed as a command during `--help` output, swallowing the word. Confirmed via
actually running `bash bin/fleet_housekeeping.sh --help` before and after the one-character fix
(`` ` `` → `` \` ``) — same root cause as the other 3, different file, cosmetic impact (only
affects `--help` text) but the exact pattern the gate exists to catch.

**Evaluated and explicitly NOT shipped: a Semgrep rule for §12** (missing `accountNo` filter
when reading the shared `dnse_raw_*.jsonl`, the pattern behind 3 real cross-account-contamination
incidents 2026-07-06→07-21). A naive `pattern-not: for $REC in $ITER: ... $REC.get("accountNo")
...` rule fires on *every* unrelated loop in a file, not just loops reading the shared file —
tested against `bin/verify_account_snapshot.py` (which has the correct filter) and confirmed
too imprecise to ship. This needs dataflow-aware rule engineering (semgrep taint mode or
similar) to reach a usable precision bar, not a quick pattern. `semgrep` (1.172.0) is installed
and available (`pip install --user semgrep`, no `.pre-commit-config.yaml` entry yet since there's
no rule to run) — left as documented future work in `kb/coding_guidelines.md` §12/§15 rather than
shipping something noisy.

## Verification

1. `bash -n` on `bin/shellcheck_gate.sh` — pass.
2. Ran against the two real historical buggy commits (`git show <parent>:bin/daily_retro.sh`,
   `git show <parent>:bin/kb_nightly.sh`) — both correctly blocked with the exact SC codes/lines
   matching the real incidents.
3. Ran against the entire current (already-fixed) `bin/*.sh` — 0 hard-blocks, until the
   `fleet_housekeeping.sh` finding above, which was fixed and re-verified to 0.
4. `pre-commit run --all-files` (broader file set including `hooks/*.sh`) — surfaced the SC2154
   false-positive issue, fixed by dropping that code, re-ran to clean pass.
5. **End-to-end with a real `git commit`** (not just `pre-commit run`): staged a file containing
   the exact reproduced daily_retro.sh bug, ran `git commit` — hook fired, commit correctly
   REJECTED (exit 1, `git log` confirms HEAD unchanged). Repeated from an agent-subdirectory cwd
   (`agents/Taylor/`, via `git -C <path> commit`, matching how `dispatch.sh` invokes git) — same
   result. Test artifacts removed before the real commit.

## Also done

- Added `kb/coding_guidelines.md` §15 documenting the lesson itself (previously it wasn't yet
  one of the 14 numbered lessons — the SRE practice is to write the lesson and its enforcement
  together, not lesson-now/enforcement-later).
- Added a top-of-file "Enforcement policy" note explaining which lessons are mechanized vs.
  intentionally left as prose (process/judgment-call lessons — §7, §10, §11, §13 — don't have a
  clean syntactic pattern to lint and shouldn't be forced into one).
