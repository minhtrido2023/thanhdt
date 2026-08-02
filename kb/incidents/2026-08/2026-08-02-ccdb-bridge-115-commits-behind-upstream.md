---
kind: incident
date: 2026-08-02
topic: ccdb-bridge-115-commits-behind-upstream
title: >-
  2026-08-02: claude-code-discord-bridge (shared infra, every Claude session on the account)
  found 115 commits / 3+ weeks behind origin, incl. 3 unpatched security fixes — merged + fixed
status: fixed
category: infra
origin: >-
  discovered while investigating whether an uncommitted 1900-line WIP in the bridge repo (found
  during the notify-api-silent-message-loss investigation, same day) should be committed — the
  branch it sat on turned out to be local-only, never pushed, and badly stale against upstream
recorder: Mike, user directive ("nghiên cứu thật kỹ để quyết định giải quyết vấn đề đồng bộ này,
  không để phát sinh trong tương lai nữa")
---

# 2026-08-02: claude-code-discord-bridge upstream sync + standing drift check

## What was found
`/workspace/claude-code-discord-bridge` (the Discord bridge every concurrent Claude session on
this account runs through — `ccdb-mike.service` and others) was checked out on
`feat/mention-only-toggle`, a branch that:
- Existed **only locally** — never pushed to `origin`, no PR, not even a matching remote branch.
- Was based on `beb360f`, **115 commits behind `origin/main`** (last real sync ~2026-07-10, per
  the branch's own last-commit timestamp before this session's work).
- Carried **3 real security fixes** in the gap (`cd5c9ff`/`434f414`/`5642a30` — path-traversal
  containment hardening for `/api/ingest` attachment handling, defense-in-depth against a
  CodeQL-flagged path-injection sink) that production had been running without the whole time.
- Had ~1900 uncommitted lines on top (a token-usage-reporting feature, reviewed and found
  complete/well-tested separately — see the commit `618c14f` message for that review).

No one was watching this repo's relationship to upstream at all — that is the actual root cause,
not any single missed update.

## What was done
1. Reviewed and committed the uncommitted WIP (`618c14f` feat, `ca0fde9` fix — the UTF-8
   exception-handling bug from the companion incident, see
   `2026-08-02-notify-api-silent-message-loss.md`).
2. Investigated the 115-commit gap before merging: 38 chore / 24 fix / 13 feat / 6 docs / 5 build
   / 3 security / 1 ci — no other red flags.
3. Merged in an **isolated git worktree** (`git worktree add /tmp/ccdb-sync-test -b
   sync-test-20260802`), never touching the live checkout mid-resolution. `git merge
   origin/main --no-commit` surfaced 9 conflicting files; resolved by hand (most were additive —
   independent new fields/params on both sides — but 2 were substantive):
   - `backend_factory.py`: adopted upstream's Claude-only gating of `append_system_prompt`/
     `effort` when building a Codex runner. The local side's own comment ("CodexRunner swallows
     unknown kwargs") was true for `include_hook_events` but **wrong for `effort`** —
     `CodexRunner.__init__` takes `effort` as an explicit named parameter (maps to
     `model_reasoning_effort`), so the old code would have applied a Claude-scale effort value
     (e.g. "max") to Codex, which has no such level. A real bug avoided, not a style conflict.
   - `claude_chat.py` `_run_claude`: upstream restructured this into a lock-scoped
     "Phase 1 (atomic evict+register) / Phase 2 (run outside the lock)" design with
     identity-guarded cleanup, closing a genuine race — two near-simultaneous Discord messages in
     the same thread could both pass the "nothing running" check and spawn parallel Claude CLI
     processes (the local side's lock only covered the eviction check, not registration, leaving
     that exact window open — same idempotency-under-concurrency shape as
     `coding_guidelines.md` §5's double-buy incident, different codebase). Adopted upstream's
     structure fully and rewove the local additions (periodic heartbeat ping,
     `minimal_status_reactions`, immediate ACK) into it.
4. Verified before finalizing: full test suite (2038/2039 pass — the 1 failure is a pre-existing,
   unrelated ambient-env leak in `test_backend_factory_api_port.py`, reproducible in any
   ccdb-spawned shell). All touched modules import cleanly.
5. **Process mistake caught by re-verification, not avoided in advance**: 2 test-file edits
   (updating `test_event_processor.py` to monkeypatch the new `_post_engine_status_footer` call
   site instead of the no-longer-called `_post_statusline_footer`) were made in the working tree
   but never `git add`ed before the merge commit. Running the full suite a SECOND time — directly
   in the live checkout after fast-forwarding, not just trusting the worktree's earlier green run
   — caught the gap immediately (matches `~/.claude/skills/verify-before-done/`'s core habit: a
   green run in one place doesn't certify a different copy of the same commit). Fixed with a
   follow-up commit + re-verified.
6. Fast-forwarded the live checkout's branch to the verified merge — a git-only operation, does
   **not** restart the running service (`ccdb-mike.service` stayed at `NRestarts=0`, same PID,
   same start time throughout). The new code is on disk, ready, but not live until an explicit
   restart — deferred per user instruction ("Mike vẫn đang chạy nên chưa restart").

## Standing prevention (the actual ask — "không để phát sinh trong tương lai nữa")
`bin/ccdb_bridge_drift_check.sh` (new), wired into the existing `cron_health_check_daily.sh`
08:25 ICT slot (no new cron entry). `git fetch origin main` + `git rev-list --count
HEAD..origin/main`:
- Alerts (Architecture topic `1521475726329516122`) when **>10 commits behind** OR **any commit
  in the gap is `security:`-labeled** (would have caught this drift at commit ~10-15, not 115).
- Debounced on `origin/main`'s SHA (`state/ccdb_bridge_drift_alerted_sha.txt`) — one alert per
  distinct unresolved gap, not a daily repeat; clears silently on catch-up.
- **Detect + alert only, deliberately not auto-merge** — this session's own merge needed a real
  judgment call on a genuine concurrency bug, not something safe to automate blindly for a repo
  every concurrent session depends on.
- Verified end-to-end: real run (0 behind, quiet), simulated 115-behind via a detached worktree
  (alerted, correctly flagged 3 security commits), debounce (2nd run on same gap stayed quiet),
  catch-up (stamp cleared).
