---
name: poc-not-live
description: "The WorkingClaude trading system is POC, not live trading yet"
metadata: 
  node_type: memory
  type: project
  originSessionId: fef38ec9-be6a-47e0-ac13-1222be8cba59
---

The Vietnamese stock trading system in `/home/trido/thanhdt/WorkingClaude` (DNSE/PHS bots, cron jobs, macro_state_live, Telegram reporters) is still **proof-of-concept, not live trading real money** (confirmed by user 2026-06-21).

**Why:** affects how cautious to be about "breaking live systems" — refactors/reorgs that would be high-risk on a live trading system are acceptable here.

**How to apply:** still verify things work after changes (compile/import/smoke-test), but don't block large cleanups out of fear of breaking "live" trading. See [[repo-structure-goal]].
