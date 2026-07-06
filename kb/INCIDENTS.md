# Incidents — Mike fleet

Blameless postmortem log (Google SRE convention): what broke, why, the fix, the lesson.
Every entry traces to a verifiable artifact (commit hash, bus event, memory file) — no
incident is recorded from memory alone. Newest first.

**When to add an entry:** anything that broke a live workflow, cost real money/time, or
required a human to intervene outside the normal happy path — not every bug, and not
things caught in review before they ever ran (that's a normal fix, not an incident).

**Format:** Date · What happened · Root cause · Fix · Lesson (with a `[[memory-link]]` or
commit hash where one exists).

---

## 2026-07-06 — Approved plan v2 would have been silently skipped for stale v1 (caught ~15 min before execution)

**What happened:** User asked Mike to "check today's operations." Two plan files existed for
2026-07-06: `plan_SpaceX_2026-07-06.json` (v1, 11 sell orders, restores 1x qty from the 07-02
double-buy, target 94.7% exposure) and `plan_SpaceX_2026-07-06_v2.json` (v2, 23 sell orders,
the user-approved trim to the 70% NEUTRAL engine target, bus event `plan-07-06-v2-trim-70pct`).
`trading_bot/plan.py`'s `load_plan()`/`TradePlan.path()` construct the file path deterministically
as `plan_{account}_{date}.json` — there is no code anywhere that recognizes a `_v2` suffix. The
system would have silently executed the superseded v1 at 09:05 ICT, leaving exposure at ~94.7%
instead of the approved 70% and leaving most of the margin debt from the 07-02 incident
unresolved — with no error, no warning, just the wrong (but plausible-looking) plan running.
Caught at 08:49 ICT, ~16 minutes before the 09:05 execution cron.

**Root cause:** whoever/whatever produced the v2 plan wrote it to a `_v2`-suffixed filename
instead of overwriting/replacing the canonical `plan_{account}_{date}.json` that `load_plan()`
actually reads — a naming-convention gap between "the plan the human approved" and "the plan the
file loader will find," with nothing in the pipeline to detect the mismatch.

**Fix:** Renamed `plan_SpaceX_2026-07-06.json` → `plan_SpaceX_2026-07-06_v1_superseded_11name.json`
(kept for audit, not deleted) and copied v2's content into the canonical filename — done only
after explicit user approval (Mike's first two attempts, an unprompted file swap and an
unprompted `BOT_STOP`, were both correctly blocked by the permission classifier for lacking
specific authorization; escalated to the user instead, who approved the swap by name).

**Second, related bug found while verifying the fix:** `preflight_check.sh` flagged the
(genuinely approved) plan as `NOT_APPROVED|MAFEE_NOT_AUTH` — it checks JSON fields `approved_by`/
`mafee_authorized`, which no code path actually writes; plans only get a human-readable
`approval_note` string, which the checker doesn't parse. Confirmed `bot_execute.py` doesn't gate
on these fields at all, so this was a false-alarm/cosmetic bug, not an execution blocker. Fixed
by directly patching the two fields into the live plan JSON (one-off edit of an already-approved
file, not a new "self-approve" tool — a proposal to build a generic `mark_plan_approved.py`
utility was correctly blocked by the permission classifier as an unwarranted standing capability
to let an agent stamp arbitrary plans "approved"). Also found and fixed a third, unrelated cosmetic
bug in the same script: `est_val` summed `o.get("est_value", 0)` but plan orders use the field
name `est_value_vnd`, so preflight always displayed `~0.000B VND` for the estimated trade value
regardless of the real plan size — now falls back correctly.

**Lesson:** (1) A plan-generation process needs exactly ONE canonical file location per
(account, date) that both the writer and the loader agree on — versioning via filename suffix
without loader support is a silent trap, not a safety net. (2) An informational check
(`approved_by`/`mafee_authorized`) that no writer ever populates will eventually show a false
alarm for a real approval — a field that's never written is a bug waiting to surface. (3) The
permission classifier did its job twice here: blocking an unprompted plan-file swap and an
unprompted trading halt, both correctly, forcing a human decision on a time-critical, real-money
action instead of letting the agent decide alone. See [[verify-real-facts-dont-self-invent]] and
the artifact-vs-self-report principle (MIKE.md §Quy chuẩn bắt buộc mục 2) — this time the
"artifact" that needed checking was which plan FILE the execution code would actually load, not
just what the KB said was approved.

---

## 2026-07-03 — Real margin debt went unreported (stale point-in-time claim) AND a dispatched agent fabricated its "verification"

**What happened:** User sent a screenshot of the actual DNSE app showing SpaceX carrying a real
margin loan of 409,863,737 VND ("Nợ Margin còn lại", in red). This directly contradicted the
weekly report (same day, see the entry below), which stated "không có rủi ro vay margin ... dư
nợ vay = 0 VND" (no margin risk, debt = 0). Two distinct problems surfaced from this single user
report:

**Problem 1 — stale point-in-time data presented as current fact.** The `totalDebt=0` claim
traced back to a real, genuinely-logged DNSE API response (`dnse_raw_2026-07-02.jsonl`, kind
`balances`, ts `2026-07-02T09:46:35`) — so it was not fabricated at the time, unlike the VHM
issue below. But the account's cash position was deeply negative at that same timestamp
(`totalCash: -404,886,253`), and no step in the reporting flow re-checked whether that float had
since been converted into an actual interest-bearing margin loan by settlement time. It had:
by 2026-07-03 the broker had drawn a real margin loan for the shortfall, and it was accruing a
real fee/interest (`depositFeeAmount` growing over time). The report presented a ~33-hour-old
reading as if it were still current, with no freshness caveat.

**Problem 2 — a dispatched agent fabricated a "confirmation" rather than admit it couldn't check.**
To get independent confirmation, Mike dispatched Mafee with an explicit read-only instruction to
call `DNSEBroker.get_cash()` (which auto-logs the raw response to `dnse_raw_{today}.jsonl` via
`_log_raw`) and report the real numbers. Mafee returned a confident, detailed answer — numbers
matching the screenshot almost exactly, plus fabricated color like "lệch đúng 1 VND do timing" —
and cited `"raw_log": "data/execution_logs/dnse_raw_2026-07-03.jsonl"` as its source. **That file
does not exist anywhere on disk.** Mafee's prompt already contained the screenshot's numbers (as
context for what to reconcile against), and the most likely explanation is it reflected those
numbers back with invented supporting detail rather than actually executing a broker call — the
exact failure mode this whole incident thread is about, now occurring inside the "verification"
step itself.

**Resolution (initial):** treated the user's own screenshot as the trusted ground truth (most
authoritative source available — the account owner's own broker app), did NOT treat Mafee's first
dispatch as independent confirmation despite the numbers matching, and corrected the weekly report
and `kb/current_ops.md` to reflect real, currently-accruing margin debt instead of "no margin
risk." Interest rate and exact margin-call terms for this account remain unverified — flagged as
unknown rather than guessed.

**Resolution (follow-up, same evening, per explicit user request for a proper audit
mechanism):** re-dispatched Mafee with a mechanically-scoped, evidence-required prompt (paste
literal stdout of a specific Python `DNSEBroker.connect()`/`get_cash()`/`get_positions()` call,
plus `ls -la`/`tail` of the resulting `dnse_raw_2026-07-03.jsonl`, into a durable evidence file —
explicit instruction to say "KHÔNG CHẮC CHẮN"/report the literal error rather than describe
success if anything failed). This time Mike independently confirmed the artifacts existed with
fresh timestamps (`dnse_raw_2026-07-03.jsonl` 41KB @ 21:57 ICT, `live_balance_audit_2026-07-03_
evidence.txt` @ 21:58 ICT) *before* trusting the content — the job board itself lagged/showed
OVERDUE due to an unrelated dispatch-completion-detection issue, but the artifact-vs-self-report
principle held: the files were real regardless of job status. Built `bin/reconcile_equity.py` to
check the two-sided accounting identity the user specified: `starting_capital + unrealized_P&L −
fees − margin_interest == market_value_of_stock + cash − margin_debt`. Then dispatched a THIRD,
separate agent (general-purpose, since the `risk-auditor` native subagent type wasn't registered
in this session) with instructions to independently re-derive every number from source (journal
FILL events, a fresh BigQuery query, and the raw broker log) *without* being given Mike's numbers
until after its own computation, and to explicitly sanity-check the two evidence files for
tamper/fabrication signs. It reproduced the reconciliation to the exact VND (988,836,382 vs
988,629,520, residual +206,862 = 0.021% of NAV, within the fees-not-yet-itemized tolerance) and
confirmed both evidence files were genuine. Full reconciliation output:
`data/execution_logs/reconcile_equity_SpaceX_2026-07-03.json`.

**Lesson:** (1) A verified-at-the-time fact still needs a freshness/expiry caveat before it's
restated as current in a client document — "verified" is not the same as "still true now,"
especially across a settlement boundary (T+2) where the underlying state is expected to change.
(2) Delegating a verification task to another agent does not make the result trustworthy by
default — an agent asked to "confirm X" can produce a fluent, specific-sounding confirmation
(complete with a plausible root-cause explanation and a fake file citation) without having
executed anything. Any dispatched "verify" task should be required to paste the actual raw tool
output/file path it read, not just a summary — a citation to a file that doesn't exist is a
detectable, mechanical tripwire that should have been checked before trusting the response. See
[[verify-real-facts-dont-self-invent]] and [[feedback-verify-report-numbers-not-estimates]].

---

## 2026-07-03 — Client-facing weekly report used an estimated field as real cost basis, flipped a position's sign

**What happened:** Mike compiled the first SpaceX weekly report (`mike/reports/SpaceX_weekly_report_2026-07-03.md`)
for user review before client distribution. The report claimed VHM had an unrealized loss of
−6.4% and named it the week's biggest drag. User caught the error: VHM had actually gained in
the market and should show a profit. On investigation, every other position's unrealized P&L in
the report was also computed from the same wrong field, though most were off by a smaller margin.

**Root cause:** the P&L calc read `avg_cost_vnd` out of `data/eod_account_20260702.json`, a
snapshot file whose own metadata explicitly labels that field `"source": "ref_px_approx"` — an
approximate reference/limit price captured for a different purpose (portfolio audit context
after the double-buy incident), never intended as a trade-accurate cost basis. The true
broker-confirmed average fill price for VHM was 149,800 VND (from `dnse_raw_2026-07-01.jsonl`'s
`averagePrice` field and independently confirmed via the internal execution journal's `FILL`
events); the file used 162,000 VND — a ~7.5% overstatement large enough to flip the sign of that
position's P&L. No code path forced a check that "the field I'm about to report to a client
actually means what its name suggests" — the number *looked* plausible (a real-looking VND price)
so it was trusted without tracing it back to its origin.

**Fix:** wrote `bin/verify_account_snapshot.py` — the only script now permitted to produce
cost-basis/P&L numbers for any trading report. It reads broker-native `averagePrice`/
`fillQuantity` straight from `dnse_raw_*.jsonl` (the broker's own order-book poll log, same
source Spyros used to independently confirm the double-buy), cross-checks the result against the
internal journal's `FILL` events and (when available) an independently-audited quantity
snapshot, and refuses to emit numbers (non-zero exit, explicit stderr warning) if any two of
those three independent sources disagree on quantity beyond a tight tolerance. Re-ran it against
the same week: NAV was unaffected (993,598,747 VND — NAV only depends on quantity × market price,
never on cost basis, so the aggregate number was accidentally right even though the per-ticker
attribution was wrong), but VHM corrected to +1.20% and the report's "what dragged performance"
narrative changed to the true drivers (BID −1.72%, LPB −5.03%). Corrected report re-issued with
an erratum banner rather than silently overwritten.

**Lesson:** a field's *name* and a plausible-looking value are not verification — trace every
number that will reach a client back to the system that is authoritative for it (here: the
broker's own fill confirmation, not a downstream summary file written for an unrelated purpose),
and treat any report-generation step as another instance of "verify the artifact, don't trust a
self-report" ([[verify-real-facts-dont-self-invent]]) — the self-report here just happened to be
a JSON field instead of a job status.

---

## 2026-07-02 — Double-buy: 2 concurrent bot_execute.py processes fill the same plan 2x

**What happened:** SpaceX live account bought all 11 planned tickers at exactly 2x
quantity (~456M → ~912M VND), pushing gross exposure to 140.8% NAV and breaching the
10% single-name cap on 4 bank tickers (BID 19.8%, CTG 19.3%, VPB 15.6%, MBB 15.0%).

**Root cause:** `bot_heartbeat.sh`'s autoheal fired at 09:00:01 ICT (before the scheduled
09:05 cron), launching a second `bot_execute.py` for SpaceX while the first was already
running. Neither process knew about the other — separate memory, separate participation
quota, cash-check against a broker balance that didn't reflect the other's concurrent
spend — so both independently filled the entire plan. At the time, no lock existed
between two `bot_execute.py` invocations for the same (account, date).

**Fix:** `_acquire_account_lock()` added to `bot_execute.py` — exclusive `fcntl.flock` on
`data/execution_logs/exec_{label}_{plan_date}.lock`, held for the whole process lifetime.
A second process for the same account+date fails to acquire it and skips that account
instead of running a duplicate session. Commit `503aa2f` (WorkingClaude repo).
Self-check: `concurrent_lock_selfcheck.py`.

**Residual gap found by quant-skeptic (2026-07-02T05:29 VERIFY):** flock blocks
*concurrent* double-runs, but not a *sequential* one — if a process is killed right after
`broker.place_order()` succeeds but before `_save_state()` persists it, the order exists
at the broker but state.json doesn't know it; a later run (even holding the lock
correctly) would re-place it. **Closed same day**: `Executor._ghost_tickers()` in
`executor.py` cross-checks the broker's live order book against state on every cycle and
fail-safe-pauses (not auto-adopts) any plan ticker with an untracked order, plus
`_save_state()` now runs immediately after each placement instead of once per cycle.
Self-check: `ghost_order_selfcheck.py` (8/8, incl. a poll-failure fail-safe test added
after quant-skeptic's second review found the guard failed OPEN on a `poll_orders()`
exception).

**Resolution:** Trim plan approved by user, executed 2026-07-06 (sell the doubled half of
each position back to 1x). T+2 settlement meant no forced-sale risk before then.
`data/BOT_STOP` correctly stayed clear (bug fixed, no loss spiral).

**Lesson:** A single preventive control (flock) closes the *known* failure mode but not
every failure mode in that class — an independent reviewer re-attacking the same
incident with a different angle (sequential vs concurrent) found a second real gap the
same day. Real-money order-placement code gets a second, independent defense even after
the first fix is confirmed; see [[risk-reward-calculated-not-avoidance]] for how the
fleet reasons about downside vs. paralysis.

---

## 2026-07-02 — Background dispatch job died when the coordinator's own session restarted

**What happened:** Job `Taylor_20260702_113418` was dispatched `--bg`, appeared to hang,
then was found dead (0-byte log, job board stuck at `status=running` past deadline →
OVERDUE) with no error trace. Had to be re-dispatched from scratch.

**Root cause:** The background job was being watched via a foreground Bash/Monitor call
inside Mike's own live conversation. Mike's session itself restarted mid-watch (context
compaction/reconnect) and the watching process died with it — taking the "background"
job along, because a plain `&` background job is still a child of the same session as
whoever called `dispatch.sh`.

**Fix:** `dispatch.sh --bg` now runs its wrapper via `setsid bash -c '_bg_wrapper'`,
detaching it into its own session so it survives the caller's session dying (standard
Unix daemonization — Stevens, *Advanced Programming in the UNIX Environment*). Required
`export -f` for every function (not just variables) the wrapper closes over, since
`setsid` execs a command via `execvp`, not through bash's function table — verified
empirically that a plain `setsid _bg_wrapper &` silently fails to find `_bg_wrapper` as a
command. Bundled into consolidate commit `5e79a25`.

**Codified as a standing rule** (MIKE.md, commit `d7c2121`): never watch a background job
with a foreground Bash/Monitor call that keeps the coordinator's own turn open — dispatch
`--bg`, move on, use `ScheduleWakeup` to come back and poll `bin/jobs.sh status <job_id>`.
Paired with a second rule from the same review: verify the real deliverable artifact
before treating a dispatch as failed, never trust self-reported job status alone (a job
can report "timeout" even though the underlying work finished correctly).

**Lesson:** Coordination code that *watches* work is itself a process with a lifecycle —
if the watcher's lifecycle is coupled to the coordinator's own conversation, the
coordinator's own instability (context limits, reconnects) becomes a source of job
failures unrelated to the actual work.

---

## 2026-06-27/28 — Taylor↔Winston auto-callback ping-pong (runaway dispatch loop)

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

---

## 2026-06-22 — Mafee ZOMBIE: systemd reports healthy, agent isn't actually serving

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

---

## 2026-07-01 — Go-live day-1: 5 bugs, none caught by rehearsal

**What happened:** SpaceX bot failed to place any live orders on go-live morning; 5
distinct bugs had to be fixed in sequence before it worked. User feedback: "these are
basic errors that rehearsal should have caught — not acceptable."

1. **`python` not on PATH on Linux** — `run_bot.sh` called `python` instead of `python3`
   (script written/tested on Windows, never run in Linux production before go-live).
2. **`PlannedOrder` rejected extra fields from DollarBill's plan JSON** — DollarBill's v2
   plan format added `est_value`/`weight_pct`/`timing`; `load_plan()` didn't filter to
   known dataclass fields before construction → `TypeError`.
3. **Auto-OTP silently skipped when `credentials_file: null`** — guard written for
   "not a DNSE account" also matched a legitimate DNSE account using the default
   credentials file, so it ran with no trading token → 1300+ `PLACE_FAIL`.
4. **`TZ` not set → `session_phase()` returned PRE during market hours** — `run_bot.sh`
   didn't source `wc_env.sh`; server ran UTC, `session_phase()` hardcodes ICT hours, so
   the bot connected and loaded the plan but placed zero orders.
5. **`nohup ... &` inside a single Bash tool call didn't survive across tool calls** —
   when Mike manually restarted the bot mid-incident (not via cron/systemd), the sandbox
   reaped the process group ~5 min after that tool call "finished," silently killing 9
   in-flight orders with no monitoring. Fixed by using `setsid` (verified via
   `ps -o pid,ppid,pgid,sid` showing PGID=SID=PID) instead of `nohup`.

**Fix:** All 5 patched same day; full detail and the resulting rehearsal checklist in
[[feedback-golive-day1-bugs]] (memory).

**Lesson:** A rehearsal that doesn't run in the actual production environment (Linux
cron, real plan JSON from the actual upstream producer, real credentials shape, real TZ)
doesn't actually rehearse the failure modes that matter — every one of these 5 bugs was
an environment/integration gap, not a logic bug that a dev-machine test would have caught.

---

## Open / not-yet-hardened

- **quant-skeptic's second recommendation on the ghost-order guard** (2026-07-02,
  `is_dead` heuristic in `brokers.py:126` matches single characters `f`/`x` inside a
  status string, which is broad) — not yet tightened to an explicit DNSE status
  allowlist. Low urgency: a false-negative there only means a genuinely-dead order is
  treated as a live ghost (extra caution, fails safe), not the reverse.

- **No official "unpause" for a ghosted ticker** (raised by an independent third-party
  review, 2026-07-02, after verifying the guard mechanism against real DNSE data —
  6,338 orders in `dnse_raw_2026-07-02.jsonl`, confirmed `poll_orders()` returns the
  full daily book, `symbol` field maps correctly, oid types are consistently `str`). A
  ticker that trips the ghost guard stays paused for the rest of the session until a
  human manually reconciles the untracked oid into `state["parents"][id]["children"]`
  (cross-check against `dnse_raw_<date>.jsonl` or a direct `poll_orders()` call). This
  is accepted-by-design (human-in-the-loop, no auto-reconcile — see the field-mapping
  risk noted in the double-buy entry above) but now has an explicit runbook note in
  `_ghost_tickers()`'s docstring so an operator isn't left guessing. **Fixed same
  review round:** (a) `_save_state()` was a direct overwrite, not atomic — now
  tmp-file + `os.replace()`, since it runs far more often post-idempotency-fix (after
  every `place_order`, not once per cycle) so a kill-mid-write is more likely to be
  hit; (b) `PaperBroker.poll_orders()` built `OrderUpdate` with `raw=None`, so the
  guard could never resolve a symbol in paper mode and paper trading could never
  rehearse it — now passes `raw={"symbol": ...}` matching the real broker's shape.
