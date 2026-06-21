---
name: mike-fleet
description: Mike multi-agent orchestrator — Phase-1 spine built under WorkingClaude/mike/
metadata: 
  node_type: memory
  type: project
  originSessionId: 840a1a19-944e-438b-a87c-1fa392ececcc
---

"Mike" = orchestrator that creates/coordinates child Claude Code agents on server kaffa_v2, all as
**remote-control** sessions (device-independent: drive from mobile/desktop, runs on server via tmux/systemd).

Phase-1 spine is **built, self-tested, and LIVE** at `WorkingClaude/mike/` (own git repo, isolated from the trading repo).
As of [REDACTED]21: **Mike is running** as systemd user service `mike@Mike` (`claude remote-control --name Mike`,
linger on) — visible in the Claude mobile app. 3 cron jobs added (consolidate :07/:37, watchdog + discover */10)
alongside the 6 existing trading jobs.

Mike monitors **all account sessions except `tri`** via `bin/discover_sessions.py --exclude tri` (inventory →
registry, kind=external) + `bin/session_brief.py <name>` (read transcript, observe). Sessions under
`mike/agents/<id>/` self-label as that child. Discovery is the liveness source (Stop-hook heartbeat only fires
on a turn, so idle sessions would else look dead).
**Retrofit applied** (user opted in): self-identifying hooks (`hooks/_resolve_id.sh` resolves session_id→label
from stdin, self-excludes `tri`) merged into `.claude/settings.local.json` of `/home/trido/thanhdt` and
`/home/trido/thanhdt/WorkingClaude` (permissions preserved; `.bak-mike-*` backups exist). Takes effect on each
session's NEXT start. NOTE: the session the user chats through is `WorkingClaude` (pid varies), NOT `tri`.
Locked decisions ([REDACTED]21):
- **Companion model**: children are interactive remote-control sessions the user drives; Mike routes +
  aggregates; directives are advisory. Mike does NOT autonomously wake idle children (send_message [REDACTED]
  confirms — no unattended dispatch). Autonomous-worker / Hybrid = deferred Phase-3.
- **Git-markdown KB first, no BigQuery** (deferred to Phase-2 only if needed).
- Mechanical cron consolidator only (no autonomous `claude -p` writing shared context).

Architecture: per-child JSONL bus (`bus/inbox/<id>.jsonl`, append-only, flock), atomic heartbeat registry,
`UserPromptSubmit` hook injects the RECENT delta when `kb/version.txt` bumps (version-cache dedup → child
sees other children's results without repeating), `consolidate.sh` (cron :07/:37) merges via line-offset
tracking (idempotent), rebuilds `context_pack.md`, dead-detects >30min, commits.

Implementation note: server has NO `jq` (no sudo; external binary download blocked) → all JSON handled by
`bin/mike_json.py` (python3, already on box). Zero deps beyond bash/python3/flock/git/systemd/claude.
Server CLI = claude v2.1.185 (> 2.1.181 floor). Remaining manual steps in `mike/SETUP.md`: linger, OAuth,
systemd install, cron. See plan: ~/.claude/plans/home-trido-claude-uploads-840a1a19-944e-floofy-island.md.
Related: [[poc-not-live]].
