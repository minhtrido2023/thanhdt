---
name: quant-research
description: Use before/during any quant R&D task for the VN trading fleet — testing a new signal, gate, exit rule, or selector change; backtesting a strategy variant; measuring IC of a factor; deciding whether to keep or change a production rule. Also use when Mike is designing a Taylor dispatch prompt for research, or when reviewing a finished research report before reporting it to the user. Encodes the sequence of steps that has repeatedly caught real, expensive mistakes in this fleet (look-ahead leakage, IS-overfit, false-alarm gates, N disguised as significant) — skipping a step here is how those mistakes happened before this skill existed.
---

# Quant Research Discipline

A fixed order of operations for any backtest/finding in this fleet, built from what actually
went wrong (and right) in real jobs — not from theory. Each step below cites the incident that
made it non-optional. If a report skips a step, don't trust its conclusion yet — send it back.

## The order — do these IN THIS ORDER, not whichever feels natural

**1. Scope by reading the real code first, never by assuming.**
Before designing any test, open the actual production function/SQL you're testing and confirm
line-by-line what it does. Two real corrections happened from this in one afternoon
(2026-08-01): a brief assumed a `RETAIL` route existed and that `POWER` used the FSCORE axis —
neither was true, caught only because Taylor re-read `rating_8l.py` instead of trusting the
dispatch prompt. If the person designing the dispatch prompt did their own code read first
(as Mike did before dispatching `Taylor_20260801_082823`), say so and hand over line numbers —
it doesn't replace the agent's own verification, but it catches drift early.

**2. Check `mike/kb/data_registry/` before picking a data source.**
CANONICAL vs TRAP is not guessable from a table name. Confirm the source you're about to use is
the one production actually reads for this exact mechanism (e.g. CAPIT's basket still reads
`ticker_prune`, not `universe_pit` — a plausible-sounding but wrong source would silently test
something production doesn't do).

**3. Pin the environment before running anything.**
Exact BQ snapshot (`bq_cache_asof...`), full config string (`NAV_TOTAL_B`, `ETF_LIQ`,
`BASKET_WT`, `BASKET_SELECT`, `PARK_STATES`, `AUDIT_END`), `threads=1`, and the pinned
interpreter (`$DNA_PYEXE` — not system `python3`, which can't even unpickle some cached data).
If a research question has two parts on different data vintages, say so explicitly and don't
compare numbers across them (2026-08-01 FSCORE report: câu A used the 07-29 post-restate
snapshot, câu B used a frozen 06-19 panel — flagged, not silently mixed).

**4. Declare N honestly — events, not just rows.**
Report the number of *independent* episodes, not observation count. 85 CAPIT "positions" was
really 14 events (BAL/LAG pairs aren't independent, same shock). Say the small-N sentence out
loud before showing any result: "N=14 events, sign test p=0.549 — not significant on frequency."
Never let a big row count in a CSV imply a big independent sample.

**5. Match the statistical tool to N — don't force walk-forward on a handful of events.**
N large (thousands of obs, dozens of quarters): walk-forward IS(2014-19)/OOS(2020+) is
mandatory, and OOS is the tiebreaker, not Full or IS (the `v3latest` selector looked +0.27pp
Full but was IS+1.40/OOS-0.78 — an IS-overfit mirage that would have shipped on a Full-only
read). N small (a dozen or so real events): substitute leave-one-event-out + event-level
bootstrap, and say explicitly that you substituted it and why — an omission and a disclosed
substitution look identical in a table but are not the same thing.

**6. Verify at BOTH the position tier and the full-portfolio tier — they can disagree.**
A sleeve-level return effect (weighted average across flagged positions) is not the same as
what happens to portfolio NAV once redeployed capital, sizing, and cash interactions are in
play. `V3_sectoraware` looked +0.73pp at the basket level but −0.41pp once run through the
full engine — the basket-level number alone would have been the wrong answer. Always run the
full-engine leg (self-check required, see #7) before trusting a basket-only backtest for
anything that could change production.

**7. Self-check 0 VND is non-negotiable, and the control leg must reproduce the pinned number.**
Every engine run needs `cash-flow identity max err = 0 VND` and `final NAV identity err = 0 VND`
in the log. Before trusting ANY treatment leg, confirm the control leg reproduces the currently
pinned registry number (CAGR/Sharpe/MaxDD/Calmar) to the decimal — that's what proves the
harness itself is valid, not just that it ran without crashing.

**8. Point-in-time or it doesn't count.**
Any "as of" join (rating, FSCORE, floor status) must use `Release_Date`/point-in-time
semantics, never fiscal `time` — and confirm the full-exit path routes through the engine's
existing T+1-Open no-look-ahead convention (don't invent a new execution timing for a new
signal; reuse the mechanism TIME/STOP exits already use).

**9. When a ratio or product involves a price column, verify which price basis it's actually on
— don't assume from the column name or a plausible-sounding comment.**
`Close` (retroactively adjusted for dividends/splits/bonuses) and `Price` (raw, point-in-time)
are NOT interchangeable — pairing `Close` with a genuinely point-in-time quantity (`OShares`,
`Volume`, `EPS_ttm`, `Revenue_ttm`) silently injects look-ahead, because the adjustment factor
depends on corporate actions that happen AFTER the date in question. This bit the fleet twice in
one day (2026-08-02): a wrong "PE needs rescaling by Price/Close" premise got wired into
`rating_8l.py`, then refuted, then the SAME bug shape turned up independently in `ps`
(`custom_basket.py`'s `Close*OShares` mktcap) — and both traced back to the identical root
mechanism. Full saga: `kb/incidents/2026-08/2026-08-02-pe-price-close-adjustment-saga.md`.
- **Diagnostic that actually settles it**: within one reporting period the fundamental
  denominator (`EPS_ttm`, `Revenue_ttm`, `BVPS`) is constant, so the CORRECT price basis makes
  the stored ratio itself constant across that period. Test both hypotheses —
  `stored_ratio / Price` constant-in-period vs `stored_ratio / Close` constant-in-period — and
  report the % of periods each one wins. In this fleet's data, the raw-`Price` hypothesis won
  86–100% of periods across PE/PB/PCF/PS/EVEB/DY; `Close` never exceeded ~24%. Hand-verify one
  real ticker-quarter by reconstructing the implied EPS/BVPS/Revenue and comparing to the stored
  fundamental — don't stop at the aggregate percentage.
- **MUST test on OLD data, not recent data.** The adjustment factor (`Price/Close`) drifts
  toward 1.0 as a ticker goes longer without a dividend/split/bonus event — on recent dates the
  two hypotheses become numerically indistinguishable, and a correct observation ("this ratio
  converges toward 1 in recent data") gets misread as evidence for the WRONG hypothesis. This
  exact inference error happened twice in this fleet (`Winston_20260717_063633`, then
  `Taylor_20260802_042110`) before being caught. Deliberately pick a test window where the
  adjustment factor is far from 1 (in this market, ~2007–2016; median factor ran 0.22–2.31 in
  that range vs ~1.00 by 2026).
- **Don't blanket-replace `Close`→`Price` across a file if a real bug is confirmed — split by
  role.** A value feeding a RETURN/momentum calculation (`mcap_t / mcap_t-1`) legitimately needs
  the adjusted price, or an ex-dividend date will look like a price crash. A value used for
  SELECTION or WEIGHTING at one point in time needs the raw point-in-time price. The same file
  can contain both a correct and an incorrect usage side by side (`custom_basket.py` used
  `COALESCE(Price,Close)` correctly for ADV three lines above an unrelated `Close`-based mktcap
  weight that was wrong) — audit every call site individually, don't regex-replace.
- **Two-way self-check specific to this class of fix**: (a) parity on a RECENT date — expect
  ~0 diff, since the adjustment factor is near 1 today; a large diff here means something else
  broke. (b) positive control on an OLD date (far-from-1 factor) — expect a REAL, nonzero diff;
  0 diff here means the "fix" didn't actually do anything and the diagnosis is probably wrong.
  Both directions are required — one alone doesn't distinguish "fixed correctly" from "no-op" or
  "broke something else."

**10. Look for dose-response across variants, not one config.**
When testing a threshold or a family of rule variants, order them by "how much they loosen/
tighten" and check whether damage/benefit moves monotonically. A clean monotonic ladder across
5 variants (2026-08-01 CAPIT floor test: −6.94 → −6.11 → −3.06 → −1.29 → +0.73pp, ordered by
how much each variant loosened the gate) is much stronger evidence at small N than any single
p-value — a noisy parameter doesn't produce a dose-response shape.

**11. Decompose "selection worked" from "sample got smaller/bigger."**
When a filter changes basket size, don't just compare mean returns — split into
kept-by-both vs added-by-loosening (or removed-by-tightening) and test that difference
directly. A smaller basket can look better purely from concentration, not selection quality.

**12. Actively reconcile against adjacent/prior findings — don't let the user spot the conflict.**
If a new finding could look contradictory to an existing one (FSCORE = noise at CAPIT's
time-series exit gate, but a real cross-sectional entry signal in the same fleet, same day) —
explain the mechanism difference yourself in the report. Silence reads as an inconsistency the
next reader has to resolve alone; a report that surfaces and resolves the tension is what
"unusually well-disciplined" verification looks like from the outside.

**13. Multiple-testing discipline — DSR/PBO only when a specific config is being recommended for wire.**
State N_trials (how many configs you actually compared). If the recommendation is "change
nothing," DSR/PBO don't apply — there's no config being selected, say so and skip them. If a
variant wins and you're about to recommend wiring it, DSR/PBO (CSCV) are mandatory before that
recommendation goes out, per `MIKE.md` §Quy chuẩn 5.

**14. Confirm production is untouched.**
`git diff`/`git status` clean on the real production files. Any engine copy used for a
treatment leg should be a clearly-separate file (a `sed`-generated duplicate differing by
exactly one documented line is fine) — never edit the file backtest runs actually import from
production for research purposes.

**15. quant-skeptic gate before anything reaches production — required only when you're
recommending a change.**
A "keep everything as-is" finding does not need quant-skeptic before being reported, but should
still recommend it if the sample is thin or the conclusion could later be cited as license to
act (per `bin/verify_finding.sh`). Any finding recommending an actual production change is
never final until quant-skeptic returns CONFIRMED.

**16. The consumer (Mike, or whoever reads a finished report) verifies the artifact, not the
self-report.**
Before relaying a research conclusion to the user: open the cited log file and confirm the
self-check lines are actually there and the control leg number actually matches; spot-check
one or two cells of a cited CSV against the report's table. A job that crashes right after
writing a complete, correct report (real case, 2026-08-01, exit 143) is still a complete,
correct report — verify the artifact before assuming a non-zero exit code means the work is
worthless, and before assuming a zero exit code means the work is trustworthy.

**17. Write the finding to bus with the trace_id, then a durable KB note with the reasoning,
not just the conclusion.**
The bus finding is for the fleet-wide feed; the KB project-file note is what a future agent or
Mike reads six months later — it needs the mechanism and the "why," not just "keep as-is."

## Compact checklist (paste into a dispatch prompt or a self-review)

- [ ] Read the real code/SQL first — don't design a test from a description
- [ ] Checked `mike/kb/data_registry/` for the data source
- [ ] Pinned snapshot + full config string + `threads=1` + `$DNA_PYEXE`, vintage stated
- [ ] N declared as independent events, not row count; small-N sentence said out loud
- [ ] IS/OOS split if N supports it (OOS is the tiebreaker); LOO+bootstrap if not, with reason
- [ ] Position-tier AND full-engine-tier both checked
- [ ] Self-check 0 VND on every leg; control leg reproduces the pinned number exactly
- [ ] Point-in-time joins; no forward columns (`profit_*`, `O1W..O2Y`) used as a live filter
- [ ] Any price-basis ratio/product verified Price-vs-Close via in-period-constancy test, on OLD
      data; fix (if needed) split by role, not blanket-replaced; two-way self-check (recent ~0
      diff / old-date real diff)
- [ ] Dose-response / monotonicity checked across variants, not one number
- [ ] Kept-vs-added (or removed) decomposed if basket size changed
- [ ] Reconciled against any adjacent/prior finding that could look contradictory
- [ ] N_trials declared; DSR/PBO run only if recommending a specific config for wire
- [ ] `git diff` clean on production files
- [ ] quant-skeptic dispatched if recommending any production change
- [ ] Artifact independently verified (logs/CSVs opened, not just the summary trusted)
- [ ] Bus finding written with trace_id + durable KB note with the reasoning
