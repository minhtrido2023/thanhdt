---
kind: incident
date: 2026-07-03
topic: weekly-report-estimated-cost-basis
title: >-
  2026-07-03 — Client-facing weekly report used an estimated field as real cost basis, flipped a position's sign
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-03 — Client-facing weekly report used an estimated field as real cost basis, flipped a position's sign

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
