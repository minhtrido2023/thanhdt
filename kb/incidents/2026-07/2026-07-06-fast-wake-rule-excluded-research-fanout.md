---
kind: incident
date: 2026-07-06
topic: fast-wake-rule-excluded-research-fanout
title: >-
  2026-07-06 — Fast-wake-on-completion rule wrongly excluded long research fan-out chains
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-06 — Fast-wake-on-completion rule wrongly excluded long research fan-out chains

**What happened:** User observed that during the Taylor sector-sweep chain (#17-20:
hog/feed leadlag, construction, SOE, holdco frameworks, 2026-07-05→06), individual
Mike→Taylor dispatch jobs regularly finished in 5-15 minutes, but Mike didn't pick up the
result and dispatch the next step until a much longer `ScheduleWakeup` fallback fired —
wasting real wall-clock time compounding across many sequential hops in one day.

**Root cause:** Not a code bug — the *rule itself* was wrong. MIKE.md's §Quy chuẩn bắt
buộc mục 8 ("fast wake-on-completion") explicitly told Mike to SKIP the fast-wake
`Agent(run_in_background)` wrapper for "fire-and-forget research fan-out, nobody waiting
on a specific hour" — which is exactly what a long sequential sector-sweep chain looks
like from the outside, even though each hop's result *does* determine the next dispatch.
The `ScheduleWakeup` fallback formula (`wrapper_wait_timeout + 300`, ~26 min for default
timeout/retries) was also designed as a single worst-case wait, not a short recurring
poll — so even where used, it was tuned for safety over responsiveness.

**Fix:** MIKE.md mục 8 rewritten (2026-07-06): drop the research-fan-out exception —
default to ALWAYS using the fast-wake wrapper for any dispatch with a dependent next
step (nearly all of them). Replace the long single-wait `ScheduleWakeup` fallback with a
short recurring poll (~240-270s, under the tool's own cache-miss threshold): check
`jobs.sh status`, reschedule another short wakeup if still running, act immediately if
done. Same worst-case coverage, much better common-case latency.

**Lesson:** A rule scoped by *intent* ("is anyone urgently waiting?") missed the real
cost driver, which was *cumulative* idle time across many automated hops, not any single
hop's urgency. For a multi-step autonomous pipeline, treat every hop as if the next step
depends on it — because in a chain, it always does.

**Recurrence same day, deeper root cause found:** the very next `--bg` dispatch after this
fix (`Taylor_20260706_070219`, STRONG-tier calibration) skipped the wrapper AGAIN — Taylor
finished in ~12 min (bus finding posted 07:13:39Z) but Mike only picked it up when the user
manually pinged ~6-18 min later. Cause: MIKE.md's prose was rewritten, but the *literal
reminder text `dispatch.sh` prints after every `--bg` call* (meant to remove reliance on
remembering the rule from context) still said "bỏ qua nếu fire-and-forget" — the exact old
wording — so the live signal Mike actually sees every dispatch kept nudging the old,
now-wrong behavior. Fixed in `bin/dispatch.sh` (commit `3add2e5`): reminder rewritten to
"⚠️ BẮT BUỘC" (mandatory, no skip clause), wording synced to the short-recurring-poll
`ScheduleWakeup` guidance. **Lesson #2:** when a rule changes, the runtime-printed
reminder/prompt text that operationalizes it is a SEPARATE artifact from the docs prose —
grep for the old wording and fix both in the same change, don't assume updating the prose
alone propagates.
