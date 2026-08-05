---
name: deterministic-decision-gate
description: Use when a recurring mistake in the plan/execution pipeline turns out to be a mechanical decision (a date offset, a field lookup, a Σ-vs-cash comparison, a ticker exclusion) that's currently left to an LLM session to remember and re-derive correctly every time — especially when the same rule already lives as prose in a context_*.md file and has caused 2+ real incidents. Also use when applying a reviewed patch to a production trading-fleet file, or when running quant-skeptic verification on an operational/non-alpha finding. Encodes the exact sequence that converted 4 such gaps (A1-A4, 2026-08-04) from recurring incidents to CONFIRMED, live production gates in one day.
---

# Deterministic Decision Gate

A fixed sequence for finding a decision an LLM keeps getting inconsistently right, turning it
into code, and getting it safely into production. Grounded in one real day (2026-08-04) that
closed 4 of these gaps end-to-end — not theory.

## The failure shape this catches

Two different LLM sessions (SpaceX vs ZaloPay plan-writers, same day, same source CSV) computed
a T+1 entry window differently and disagreed. The rule was correct and wasn't missing — it lived
in `context_planning_mini.md` as prose, and "prose the LLM re-reads and re-applies from scratch
every dispatch" is not the same reliability class as "code that computes it once." A user
question ("sao 2 account lại có candidate LAG khác nhau nhỉ?") surfaced this, and a follow-up
audit (`Taylor_20260804_125048`) found **6 more decisions of the same shape**, 4 of which had
already caused real incidents (a 07-21 sizing bug that lost 87.1tr of deployable capital, a
07-23 exclusion that got bought anyway, a 07-24 cash race that shorted a tranche by 0.78M, a
CAPIT reconciliation gate that's been blind on every top-up session since it shipped).

**The filter for "this belongs on the list"**: a decision is in scope when it's a *pure
derivation from data already available* — computing a date offset, reading a boolean field and
filtering on it, looking up a table (sector→formula, ticker→exclusion), comparing a number to an
existing constant. No judgment, no creativity required. "Is this ticker worth buying" is out of
scope; "is this ticker in the window that opens today" is in scope.

## The sequence

**1. Inventory with evidence, not vibes.** For each candidate decision, write one row: what it
is, the file:line where the *rule* currently lives (usually a context_*.md), the file:line of
the *only enforcement mechanism* that exists today (often nothing, or a WARN-only shadow log),
and whether it has caused a real incident (with date + numbers). A decision with zero incident
history and zero existing shadow-log evidence goes lower priority than one with 3 incidents in
15 days — rank by evidence, not by how interesting the fix sounds.

**2. Extract, don't reimplement.** If the correct value is already computed and printed
somewhere (a CSV column, a status.json field, a report string) — as it was for the FLOOR_FAIL
sector-lens case, where the "missing" valuation lens turned out to already be in the CSV cell
the losing session just didn't finish reading — the fix is a script that *extracts* that value
into a decision, not a rewrite of the logic that produced it. Rewriting is a coding_guidelines
§2/§3 violation (duplicated logic, now two places that can drift) and usually means you didn't
finish step 1.

**3. Reuse existing gates instead of re-deriving their math.** A2's cash-race gate needed the
same "how much buying power is already committed" calculation A1's funding gate had just built —
it imported and called A1's function instead of recomputing utilization from scratch. Same
principle for loan-package resolution: call the broker's own `_validate_lever_package()`/
resolution path, don't trust a plan field or re-derive which package applies — quant-skeptic's
first REFUTED verdict this session was exactly a case of trusting a field instead of resolving
it the way `place_order()` actually does.

**4. Choose a source that can't be silently emptied.** Before building a CSV/JSON exclude-list,
check who else reads that file — A4 (IVS/TMG exclusion) rejected two existing mechanisms
precisely because of blast radius: `forensic_flags.csv` feeds the 8L rating table used by 5
backtest engines (wiring a narrow LAG-only exclusion through it would silently move the pinned
R3 backtest number), and `BANNED` feeds the whole universe_pit_quality build (touches every
book, not just LAG). The fix was a new, narrowly-scoped code constant instead — a small correct
mechanism beats a wide one that happens to have room for your case. Also: no silent TTL/auto-
expiry on a decision a user made explicitly (coding_guidelines §20) — an exclusion should expire
only via an explicit code change + review, never on a clock nobody's watching.

**5. Selfcheck the way `verify-before-done` requires — actually run it, TZ-stripped, and let
your own script catch bugs before the reviewer does.** Both A2 and A4's builds report real bugs
their own selfchecks caught before quant-skeptic ever saw them (A2: `check_plan_funding`
returning `SKIPPED` on an empty-orders plan silently misread "no cash needed" as "5M headroom
instead of 40M"; A4: `--live` mode initially globbed the wrong directory and passed *because it
found nothing to check*, not because anything was verified — fixed by asserting `len(files)>=1`
before trusting a "0 problems found" result). A green selfcheck that never found a real file is
not evidence of anything.

**6. quant-skeptic verify — even when most of the standard checks are N/A.** These are
operational/mechanism findings, not alpha claims, so look-ahead/OOS/panel-curation/DSR-PBO
mostly don't apply — say so explicitly rather than skipping the verify step. The two checks that
*are* load-bearing here are **reproducibility** (rerun the cited selfcheck/replay script fresh,
independently, and confirm the exact numbers) and **arithmetic/mechanism** (read the actual
production code path the finding claims about, and confirm the mechanism as a structural fact —
e.g. A3's verifier didn't just trust "the gate is blind on top-up sessions," it read
`golive_recommend_v23.py` and confirmed `capit_targets = {}` is only populated inside
`if capit_signal_today:`, which makes the blindness a code-structural certainty, not an
inference from a small sample).

**6a. Watch for verify_finding.sh's own failure modes on larger findings.** Two hit the same day
this skill was written: (a) two `--bg` verify calls launched within the same wall-clock second
collided on a second-resolution log filename, and the bus event for the second finding turned
out to be a byte-for-byte duplicate of the first — caught only by comparing `finding_topic`
inside the payload against the outer bus `topic`, not by trusting that a verification event
existed. (b) a larger/more complex finding (5 files, 500+ lines) hit `--max-turns 30` with no
parseable verdict, landing as a false `INCONCLUSIVE` — not a real refutation, a resource
exhaustion. Both are now fixed at the script level (unique `$$`-suffixed log names, `--max-turns
50`), but the general lesson holds for any future tooling: an "INCONCLUSIVE" or a duplicate-
looking verdict is itself a signal to check the *verifier's* mechanics before accepting it as a
verdict on the finding.

**7. Applying the patch: `git apply` reporting exit 0 is not proof the file changed.** This bit
twice in one day, on two unrelated files (`bot_execute.py` for A1, then the 5-file A4 patch) —
`git apply`/`git apply --check` returned success with zero stderr and the target file's mtime
and content were provably unchanged. `patch -pN` (the classic tool, different implementation)
applied both correctly on retry. Whichever tool you use, **verify the artifact independently
after every apply**, not just the tool's exit code: mtime changed, `grep` finds new unique
strings from the patch, `git diff --stat` insertion count matches the patch's own stat line,
`ast.parse`/real `importlib` import succeeds (not just parse — A1's patch needed a real import
to catch a scoping issue a syntax check alone wouldn't), and re-run the feature's own selfcheck
against the now-patched file, not the pre-patch copy the build-time selfcheck ran against.

**8. Surface policy calls instead of picking a default.** A CONFIRMED verdict on the *mechanism*
does not resolve a *policy* choice hiding inside it. A2's gate needed to decide which side gives
way when V2.4's plan and the TV1 discretionary injector compete for the same cash — quant-skeptic
confirmed the mechanism was safe either way, but the fleet's original design doctrine said
"TV1 reserve first," and the easiest-to-build direction (gate the injector, which runs second)
silently reverses that. This was written up as an explicit question to the user rather than
resolved by whichever direction was cheaper to implement — the user's answer became load-bearing
context for the wired behavior, not an implementation detail.

**9. Check `git status` for concurrent writers before applying, every time.** A near-miss earlier
the same day (a dispatched job independently editing `trading_rules.json` at nearly the moment a
direct edit was happening) is the reason this is step 9 and not assumed. Cheap, and the cost of
skipping it once is a lost edit.

**10. Known-length chains get one dispatch, not N.** When the list from step 1 has several items
with no cross-item dependency (A2/A3/A4 didn't need each other's output), dispatch them as one
job with an instruction to report each item's bus finding as soon as that item is done — not N
separate dispatches paying N times the fixed per-dispatch overhead (MIKE.md cost-opt #3).

## What this replaces

Before this pattern, the response to "two sessions disagreed" was a one-off KB prose edit — which
is exactly the failure mode being fixed (a rule an LLM has to re-remember, replacing a rule an
LLM had to re-remember). If the fix for a recurring LLM-consistency bug is itself more prose, ask
whether it belongs on this list instead.
