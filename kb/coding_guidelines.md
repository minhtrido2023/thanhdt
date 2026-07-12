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

**Bright-line rule — same-day data: DNSE API, never BigQuery (user directive, 2026-07-09).**
BQ (`tav2_bq.ticker`/`ticker_1m`) only syncs overnight (`sync_bq_cache_daily.sh`, 23:45 ICT) —
any script that runs *before* that sync completes and reads BQ for "today's" price/volume is
reading **yesterday's** close, structurally, every single time (not an occasional staleness —
BQ physically cannot have today's data yet). Concrete incident: 2026-07-09, DollarBill's T+1
plan generator (`bq_freshness_check.sh`, dispatches ~17:30 ICT) priced 2 of 4 orders off BQ
close (one day stale, off by up to +5.7%) while the other 2 happened to use a live DNSE quote
correctly — the inconsistency itself is what let it go unnoticed. Rule going forward:
- Any same-day/live calculation (order sizing, ref prices for a T+1 plan, live NAV/exposure
  checks, anything a report will call "today's" number) MUST read DNSE (`dnse_api.py`
  secdef/latest_trade/positions/balances) — never BQ — regardless of what hour the script runs.
- BQ is fine ONLY for: (a) historical/backtest queries on past trading days, (b) same-day
  queries run AFTER BigQuery's own daily sync has demonstrably completed (verify via
  `bq_freshness_check.sh`'s own freshness gate, not by assuming "it's after 18:00 so it must be
  synced" — confirm the gate passed).
- When adding this constraint to a dispatch prompt (LLM-authored script/plan, e.g. DollarBill),
  state it as an unconditional MUST with a concrete example of the wrong vs right source (see
  `mike/bin/bq_freshness_check.sh`'s DollarBill prompt for the wording already in place) — a
  general "verify your data" reminder does not reliably stop an LLM from reaching for whichever
  source is easiest to query in the moment.

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

## 7. Onboarding a New Account With Legacy/Excluded Holdings

**When an account brought under management already holds positions the bot didn't buy** (e.g.
ZaloPay/0001743768, onboarded 2026-07-06 with a pre-existing 47%-NAV DGC position kept for its
own investment thesis while under an active HOSE trading restriction), don't hand-roll a one-off
workaround — use the general mechanism, since more accounts of this shape are expected
(user, 2026-07-06: "xử lý case này để về sau quản lý nhiều loại tài khoản hơn mà không gặp vấn đề"):

1. **Declare it in config, not code**: set `"excluded_tickers": [...]` on the account's profile
   in `secrets/trading_bot_accounts.json` (field added to `ACCOUNT_DEFAULTS` in
   `trading_bot/config.py`). Empty by default for every other account.
2. **Enforcement lives in ONE place**: `trading_bot.plan.filter_excluded_tickers()`, called from
   `bot_execute.py` immediately after `load_plan()` — this makes it apply no matter how the plan
   was generated (DollarBill's LLM-authored JSON, `bot_prepare_plan.py`'s templated strategy, or
   a hand-edited file), so a plan generator forgetting the exclusion can never actually place a
   forbidden order. Never rely on the plan generator remembering to leave the ticker out.
3. **Size the strategy against `active_nav`, not total NAV**: `bin/compute_active_nav.py --account
   <label>` computes `total_nav − market_value(excluded_tickers)` from LIVE broker
   positions/prices (no dependency on our own execution journal, unlike
   `verify_account_snapshot.py`/`daily_nav_snapshot.py` — those need fill history WE recorded,
   which doesn't exist for a position the account already held before bot management). Whoever
   builds the plan (DollarBill, or Mike dispatching it) must use this number as the allocation
   basis — sizing V2.4 targets against total NAV when a third of it is locked in an excluded
   position tries to deploy capital that isn't actually available.
4. **Known gap, not yet closed**: `daily_nav_snapshot.py`'s P&L computation still assumes
   journal-tracked fills for cost basis, so it can't yet produce a correct unrealized-P&L
   breakdown for legacy positions (NAV/active_nav are correct today via
   `compute_active_nav.py`; a P&L-capable version for legacy-position accounts is separate future
   work — needed before any report that compares this account's *return*, not just its NAV,
   against a clean-slate account like SpaceX).
5. **Test it**: `excluded_tickers_selfcheck.py` is the reference — covers empty/None config
   no-op, single/multi-ticker exclusion, the all-excluded edge case, and exact-case-only
   matching (a lowercase config typo must not silently fail to exclude). Extend this file rather
   than writing a parallel one when the mechanism itself changes.

**A test-infrastructure lesson from the same work session:** re-running the full selfcheck suite
after this change (per user's "backtest cẩn thận" instruction) surfaced a real, pre-existing bug
across several *other* selfcheck files: `Executor.__init__` eagerly loads `state.json` from the
DEFAULT `(account, plan_date)` path *before* any test code gets a chance to redirect it to a
tmpdir — so a stale file left by an earlier run (this file's own, or another selfcheck reusing
the literal account tag `"selfcheck"`) silently corrupts the next run's starting state. Every
selfcheck driving `Executor` needs BOTH a unique account tag (not shared across files) AND a
module-load-time cleanup of any stale fixture at the default path — see
`ghost_order_selfcheck.py`'s `TAG` comment for the full pattern. A selfcheck suite that only
passes on a clean checkout and silently flakes on repeated runs is not verifying what it claims
to.

## 8. Never Write Experiment Output to a Canonical / Registry-Pinned Filename

**Root cause of the 2026-07-06 R3-CSV overwrite:** `pt_v23_audit_2014.py` builds its output
filename ONLY from a subset of env knobs (`_capsuf _matsuf _liqsuf _park_tag _wt_tag …`).
Two config axes that materially change the result — **`BASKET_SELECT`** and the
**combination mode** (allocator vs V2.3C static 50/50) — have **no filename suffix**. So an
experiment run with a different `BASKET_SELECT`/combination silently wrote to the exact
canonical R3 path `..._etfliqcustompitg_wtnamecap.csv` (producing CAGR 17.5%, w_lag_tgt blank),
clobbering the registry-pinned production baseline. Same failure mode as the earlier `v3latest`
episode (registry line ~142). A lock wouldn't help — both runs were legitimate, just colliding
on an output name.

Rules when a script's output feeds `data/results_registry.md` or any pinned baseline:

- **Any config axis that changes the numbers MUST change the filename.** If a script derives its
  output path from env vars, every result-affecting knob needs a suffix tag — or the run must
  pass an explicit `OUT_CSV=` override. Before running an experiment variant, check whether your
  changed knob is actually reflected in the output filename; if not, set an explicit distinct
  output path.
- **Experiment/ad-hoc runs write to a clearly non-canonical name** — add an experiment suffix
  (`_exp_<what>`, `_probeNNN`, dispatcher job-id) so a canonical pinned CSV is never a possible
  target. Treat the registry-pinned filenames as read-only artifacts owned by the pinned command.
- **Regenerating a pinned baseline: use the EXACT pinned command AND the pinned interpreter.**
  The registry pins `$DNA_PYEXE` (= `/home/trido/thanhdt/wc_venv/bin/python`, pandas 3), NOT
  system `python3` (pandas 2.3, which cannot unpickle `data/earnings_surprise_data.pkl` — raises
  `NotImplementedError` in `NDArrayBacked.__setstate__`). Copy the command verbatim including
  `$DNA_PYEXE`; don't substitute `python3` even if a prompt writes it that way.
- **After regenerating, verify before trusting**: metric in expected range, `self-check 0 VND`,
  and an independent recompute from the CSV (`extract_peryear.py <CSV>`) matching the print — then
  note the regeneration in the registry so the overwrite episode is auditable.

## 9. Check `mike/kb/data_registry.md` Before Wiring a New Data Source

**Root cause of the 2026-07-11 SIGNAL_V11 base-leak:** four production/canonical consumers
(`golive_recommend_v23.py`, `pt_v4_dt5g.py`, `pt_v22_dt5g.py`, `pt_v23_audit_2014.py`) were all
silently reading `tav2_bq.vnindex_5state` (the v3.4b BASE — no DT-gate, no macro-cap, ~153
transitions) instead of `tav2_bq.vnindex_5state_dt5g_live` (the actual production regime, 49
transitions) — a trap already written up in `CLAUDE.md` ("many research scripts read bare
`vnindex_5state` assuming it is DT5G"). The documentation existed; nothing forced a check
against it before each new script picked a table name that *sounded* right. Concrete damage:
the live paper-trading book `pt_v22_dt5g` entered 6 tickers on a fake BULL(4) signal that a
correctly-sourced read would have shown as NEUTRAL(3).

**Mandatory rule, user directive 2026-07-11:** before reading ANY data source (BQ table, local
CSV/pickle/JSON, published state file) in new research or production code — check
`mike/kb/data_registry.md` first.
- If the source is listed as `CANONICAL` — use it directly.
- If listed as `TRAP` — read the "Bẫy" column before touching it; there is almost always a
  correctly-named sibling table/file to use instead.
- If listed as `DEPRECATED/DEAD` — don't wire it into anything new; it may still exist for
  historical reference only.
- **If the source isn't in the registry at all** — don't assume it's safe by default. Add an
  entry (status verified against real evidence — crontab, file mtime, code that writes it — not
  guessed from the name) before wiring it in, or ask Winston/Mike to verify first.

**Ownership**: Winston (data-ops) keeps the registry current ad-hoc whenever a new source
surfaces in other work. A full periodic audit (re-verify every entry's freshness, sweep the
codebase for sources still missing) is folded into the existing Friday KB editorial review
(`kb_nightly.sh`'s headless Mike dispatch) rather than a separate new cron job.

**When dispatching Taylor (or anyone) for new R&D**: the dispatch prompt should explicitly say
"tra `mike/kb/data_registry.md` trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime"
— matching the same pattern already used for DollarBill's DNSE-vs-BQ rule (§6). A general
"verify your data" reminder does not reliably stop an LLM from reaching for whichever table name
sounds closest to what it needs in the moment; naming the specific registry file does.

## 10. When a File Becomes Canonical, Archive Its Superseded Variants in the Same Pass

**Why this matters (user directive 2026-07-11):** the fa_ratings incident had two separate root
causes on the same day — SIGNAL_V11 read the wrong *table* (§9, a data-source trap), and
`data_registry.md` claimed `fundamental_rating.py`'s builder "had no writer in the codebase" when
the builder was sitting at repo root the whole time, just under a name that didn't match the
`build_fa_ratings_*` pattern this registry was seeded from. Confirming which file is canonical is
only half the fix — the *other* half is that near-identical variant files (`build_fa_ratings_v9.py`,
`build_fa_ratings_pre2014.py`, `fundamental_rating_v5.py`, `fundamental_rating_v8c.py` — all sitting
in the same repo root, all producing a same-shaped rating output under a slightly different name)
are exactly the kind of landmine that caused this confusion in the first place. Leaving them in
place "for reference" is how the next agent (or human) doing a quick grep picks the wrong one.

**Rule: when a script/file is confirmed canonical for a purpose** (a builder is identified as *the*
one that produces a pinned table, a cron is installed pointing at a specific script, a migration
decision names a specific file as the production source) — in the **same commit/session**:
1. **Identify superseded variants** — files with a similar name/purpose that are NOT the confirmed
   canonical one, and grep the whole repo (scripts + crontab) to confirm zero active callers
   reference them. Never archive on a name-similarity guess alone; verify with a real grep.
2. **`git mv` them into an `archive/` subdirectory** (preserving git history, not `rm`) — this is
   reversible and auditable, unlike deletion, but it removes the file from the root namespace where
   a casual `ls`/glob would surface it as a live candidate.
3. **Update `mike/kb/data_registry.md`** to reflect the new archive path and mark the entry
   `DEPRECATED` with a pointer to the confirmed canonical replacement (per §5's obsolete-marking
   rule if this is a data-source migration, or a plain note if it's just script hygiene).
4. **Do NOT apply this to genuine audit-trail artifacts** — rejected-hypothesis backtest CSVs, dry-run
   logs proving a mechanism works, anything already namespaced into an experiment directory per §8
   (`data/*_exp/`, `agents/<id>/probe_*/`). Those are inert data files kept as evidence, not scripts
   that could be run by mistake — archiving them is unnecessary churn, not safety.

**Periodic check**: `bin/data_registry_audit.sh`'s stale-duplicate scan (added 2026-07-11) flags
repo-root files with a name similar to an already-CANONICAL registry entry that are NOT yet under
`archive/` — surfaced in the Friday KB editorial review for a human/Winston decision, not auto-moved.

## 11. Check `mike/kb/cron_registry.md` Before Adding or Changing a Cron Schedule

**Root cause of the 2026-07-12 C1 CRITICAL incident:** `publish_gated_state.py` had been silently
reading the DT5G base state through `BQ_LOCAL_CACHE` (always T-1) instead of live BigQuery for
~2.5 weeks, because `wc_env.sh` exports that env var globally and the script's own comment ("SOURCE
OF TRUTH = BigQuery... NOT a local CSV") stated an intent the code didn't actually enforce. Nobody
had asked "what vintage does this publish step actually read, and does that survive a stricter
freshness gate?" before the gate (`MAX_STATE_LAG`) was tightened to 0 on 2026-07-11 — at which point
the mismatch became a structural, always-fails contradiction (Winston audit `Winston_20260712_142100`,
fixed same day, commit `4995262`, quant-skeptic CONFIRMED).

**Mandatory rule**: before adding a new cron entry or changing an existing one's schedule, read
`mike/kb/cron_registry.md` first — it answers, per job, what it reads (source + vintage T/T-1),
what it writes, who consumes the output, and what buffer/verify-artifact exists downstream. Answer
its "4 câu hỏi bắt buộc" (đọc gì+vintage / nguồn tươi lúc nào — đo thật, không tin comment / cần T
hay T-1 / ai tiêu thụ + deadline) before picking a time slot.

**Update the registry in the SAME commit** as any crontab change (add/remove/reschedule a line) —
same discipline as §9's data registry and §10's archive-on-canonicalize rule. A crontab change
without a matching registry update is exactly how the next agent re-introduces a cache/vintage
mismatch that "looks fine" until a downstream gate tightens.

**A production "publish" script (writes a table/file other production consumers read as the
current-day source of truth) must read its inputs live, never through a process-inherited cache
env** — if the import chain can reach `BQ_LOCAL_CACHE`/`bq_local_cache`, unset it explicitly
(`os.environ.pop(...)`) before the first query, process-locally (never edit `wc_env.sh` itself,
which would break every OTHER script that legitimately wants the cache).
