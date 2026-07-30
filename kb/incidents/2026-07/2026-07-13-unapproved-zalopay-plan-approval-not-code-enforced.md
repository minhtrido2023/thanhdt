---
kind: incident
date: 2026-07-13
topic: unapproved-zalopay-plan-approval-not-code-enforced
title: >-
  2026-07-13 — Unapproved ZaloPay plan (2 real-money orders) was 35 minutes from executing; approval turned out to be procedure-only, not code-enforced
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-13 — Unapproved ZaloPay plan (2 real-money orders) was 35 minutes from executing; approval turned out to be procedure-only, not code-enforced

**What happened.** Monday 08:20 ops_health_check flagged `Plan ZaloPay 2026-07-13:
NOT_APPROVED|MAFEE_NOT_AUTH — orders=2`. Winston (ops-autofix, job
`Winston_20260713_012007`) verified the plan file: sell VIB 9,200cp (~146.7M) + buy BID
900cp (~36.9M), `requires_user_approval=true`, `approved_by=null`. Then checked what
actually enforces approval at execution time: **nothing**. `bot_execute.py`,
`mike/bin/run_bot.sh`, and `trading_bot/plan.py:load_plan()` contain no approval gate —
at 09:05 the cron would have executed the unapproved plan. Escalated 08:3x via Discord
(Trading Daily + plan channel) + Telegram + bus `question`
(`zalopay-plan-0713-chua-duyet-bot-van-chay`) with options A (approve) / B (BOT_STOP,
harmless today since SpaceX plan = HOLD 0 orders).

**Root cause (2 layers).**
1. *Why unapproved:* Friday 21:00 `send_plan_report.sh` correctly REFUSED to send —
   the plan on disk at that time had the wrong date (07-11, a Saturday; DollarBill
   `next_trading_day` bug). The corrected plan was re-dispatched at 22:17, *after* the
   report hour, and **nobody re-ran send_plan_report** → the user was never shown the
   Monday plan to approve. The escalation path worked; the *recovery* path had no step
   "after fixing the plan, re-send it for approval".
2. *Why it almost executed anyway:* approval (`approved_by`/`mafee_authorized`) is
   checked only by reporting tools (`preflight_check.sh` prints RED) — the execution
   chain never reads those fields. Human-in-the-loop was a convention, not a gate.

**Fix.** Escalation only (both root causes are in Winston's forbidden zone: trade plan
content + executor logic). Proposed follow-up for Taylor + user sign-off: code gate in
`bot_execute.py` — `requires_user_approval=true && approved_by is null && orders>0` →
refuse to execute, alert. Secondary: re-dispatch of a failed T+1 plan must end by
re-running `send_plan_report.sh` for the corrected file.

**Lesson.** A red preflight is only useful if something downstream refuses to proceed on
red. Same shape as 2026-07-06 "approved v2 silently skipped for stale v1": the plan
*file* is the interface between agents and the bot, and every safety property claimed
about it (right version, approved) must be enforced where the file is *consumed*, not
where it is produced or reported on.
