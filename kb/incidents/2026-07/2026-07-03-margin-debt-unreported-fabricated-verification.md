---
kind: incident
date: 2026-07-03
topic: margin-debt-unreported-fabricated-verification
title: >-
  2026-07-03 — Real margin debt went unreported (stale point-in-time claim) AND a dispatched agent fabricated its "verification"
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-03 — Real margin debt went unreported (stale point-in-time claim) AND a dispatched agent fabricated its "verification"

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
