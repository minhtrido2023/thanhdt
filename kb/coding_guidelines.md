# Coding Guidelines — áp dụng cho toàn fleet

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Idempotent Side Effects

**Any script that can be killed mid-run and re-run must not repeat an external action.**

Root cause of the 2026-07-02 double-buy incident: a headless process crashed after
`broker.place_order()` succeeded but before it persisted that fact locally. The next run,
holding the lock correctly, had no way to know the order already existed and placed a
duplicate. A lock (flock/circuit-breaker) only stops two runs from overlapping — it does
nothing for one run dying mid-write. Fixed in `trading_bot/executor.py` (`_ghost_tickers` +
atomic `_save_state`, commit `e1d9b7c`); apply the same reasoning to every new script, not
just that one.

Before writing any script that calls an external system with a side effect (place an order,
send a message, write a shared file, call an API that isn't naturally idempotent):
- Ask: "if this process is killed right after the external call succeeds but before local
  state is saved, what does the next run do?" If the answer is "repeats the action," that's
  a bug, not an edge case.
- Prefer checking the external system's own source of truth (broker's live order book,
  the sent-messages log, etc.) over trusting only local state — local state can lag reality.
- When you can't tell whether an action already happened, **fail-safe pause and flag for a
  human** — do not guess-and-merge into local state, and do not silently proceed as if
  nothing happened. Guessing wrong is worse than stopping.
- Persist "the action happened" as close to the actual external call as possible (write
  immediately after, not batched at the end of a longer loop) — this shrinks the crash
  window rather than closing it, but every bit of shrinkage matters.
- Writes to shared state files must be atomic (`tmp` + `os.replace`/`os.rename`), never a
  direct overwrite — a kill mid-write must never leave a half-written file for the next run
  to trust.

## 6. Verify Report Data Provenance (client-facing numbers)

**A field's name and a plausible-looking value are not verification.** Root cause of the
2026-07-03 weekly-report incident: a P&L calc read `avg_cost_vnd` out of a snapshot file whose
own metadata labeled that field `"source": "ref_px_approx"` (an approximate reference price,
captured for an unrelated audit purpose) and reported it as real cost basis — flipping VHM's
week from a gain to a fabricated −6.4% loss. The number looked like a real VND price, so it went
unchecked into a document meant for clients.

Before any number reaches a report (daily/weekly/monthly, or any client-facing artifact):
- Trace it back to the system that is *authoritative* for that fact — for trade prices/fills,
  that is the broker's own fill confirmation (`dnse_raw_*.jsonl`'s `averagePrice`/
  `fillQuantity`), never a downstream summary file written for a different purpose.
- Cross-check against a second independent source (internal execution journal `FILL` events,
  an already-audited snapshot) before trusting either — see `bin/verify_account_snapshot.py`,
  the only script now permitted to compute cost-basis/P&L for a SpaceX trading report. If two
  independent sources disagree beyond a tight tolerance, fail loudly (non-zero exit) — do not
  silently pick one and proceed.
- Aggregate totals can be accidentally right while per-item attribution is wrong (NAV here only
  depends on quantity × market price, not cost basis, so it happened to survive unscathed) —
  don't let a correct-looking total substitute for verifying the breakdown a client will read.
- This is the same principle as [[verify-real-facts-dont-self-invent]] and the artifact-vs-
  self-report rule (MIKE.md §Quy chuẩn bắt buộc mục 2) applied to report generation: verify the
  artifact, don't trust a field because its value looks plausible.

**Standing pipeline for ALL cadences (daily/weekly/monthly), locked in 2026-07-03:**
1. `bin/verify_account_snapshot.py` — true cost basis per ticker, cross-checked (broker raw log
   vs internal journal vs any audited snapshot).
2. `bin/daily_nav_snapshot.py` — true NAV for one date (MTM stock + real cash − real margin debt
   from a fresh `dnse_raw_*.jsonl` `balances` record), appended to `nav_history_{account}.csv` so
   every cadence reads the same day-by-day series instead of recomputing NAV differently each time.
3. `bin/reconcile_equity.py` — the two-sided identity check (`starting_capital + unrealized_P&L −
   fees − margin_interest == market_value + cash − margin_debt`); confirmed fee rate is
   **0.075%** of true cost basis (not 0.1%, corrected 2026-07-03), and any residual after that
   should be checked against an *estimated* margin-interest accrual (`--margin-rate-annual`,
   12.5%/year per user, unverified against DNSE's actual contract) before being called
   "unexplained" — see the 2026-07-03 report for a worked example (residual matched ~4 days of
   accrued-but-not-yet-posted interest almost exactly).
4. If a number can't be traced through this pipeline, don't put it in the report — say what's
   missing instead of estimating silently.

**Cadence-specific scope** (content depth differs; the verification pipeline above does not):
- **Daily**: keep it short — trades executed today, NAV + day-over-day change, and a margin/risk
  flag if one exists. No attribution, no methodology appendix.
- **Weekly**: full narrative (see `mike/reports/SpaceX_weekly_report_*.md` as the reference
  template) — activity log, incident disclosures, sector/position tables, next-week plan, full
  methodology appendix.
- **Monthly**: apply institutional asset-management conventions on top of the weekly template —
  MTD/QTD/YTD returns, benchmark comparison, sector/name attribution, risk metrics (drawdown,
  volatility — once enough daily NAV history exists), fee/expense summary, compliance
  disclosures, outlook. Same verified-data pipeline underneath; more sections on top.
