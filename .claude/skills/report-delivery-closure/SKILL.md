---
name: report-delivery-closure
description: Enforce and rescue end-to-end delivery of automatic daily, weekly, or monthly reports and other generated client-facing report artifacts. Use when creating, sending, checking cadence, rescuing a stuck/max-turn report, or deciding whether a report job or overdue bus question is complete.
---

# Report Delivery Closure

Treat artifact creation and delivery as separate states. A report is complete only when the exact
artifact hash has passed validation and has durable success evidence for both Discord and email.

## Required workflow

1. Finish the Markdown artifact and any referenced attachments.
2. Run `python3 mike/bin/report_delivery_gate.py <report.md> --topic trading_report`.
3. Accept completion only when the command exits 0 and prints `COMPLETE`.
4. If it exits nonzero, report the failed destination and leave the job/question open. Do not
   replace evidence with a claim that the file exists.
5. On rescue, run the same command. It is hash-bound and idempotent: it retries only a missing
   destination. Do not manually resend a destination already recorded as delivered.

`maxturns_pending`, `usage_limited`, a generated file, and one successful destination are all
incomplete states. `check_report_cadence.sh` is the deterministic backstop and must not close a
`report-cadence-overdue-*` question until the delivery ledger proves both destinations.
