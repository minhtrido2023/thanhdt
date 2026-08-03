---
kind: incident
date: 2026-08-02
topic: notify-api-silent-message-loss
title: >-
  2026-08-02: user noticed "Mike seems to stop / not follow topics" — root cause is /api/notify
  silently dropping ~10 messages/3 days on oversized embeds + malformed UTF-8, both fixed
status: fixed
category: dispatch-orchestration
origin: >-
  user reported a vague feeling that Mike stops abnormally / doesn't follow a Discord topic
  fully; investigation via journalctl -u ccdb-mike found no subprocess crashes or lost-context
  bugs, but did find real silent message loss in the fleet-wide alert pathway
recorder: Mike, user-reported ("Mike ngừng lại bất thường, không follow topic đầy đủ")
---

# 2026-08-02: `/api/notify` silently drops messages — investigated "Mike stops abnormally"

## What was checked and ruled out
- `ccdb-mike.service`: 0 restarts, running continuously since 2026-07-31 15:17 UTC, no OOM/kill.
- No `claude` CLI subprocess crashes in `journalctl -u ccdb-mike` since 2026-07-25.
- Post-compact recovery ("post-compact guardrail"): every real compaction event correctly
  triggers its recovery rerun — the apparent 23-vs-12 log-line mismatch was a benign duplicate
  log line from the rerun itself, not a dropped safety net. Mike's own thread compacted 4× in
  ~5 days (2026-07-28, 07-30 ×2, 08-02), consistent with heavy usage, not a malfunction.
- Discord reaction-cleanup rate-limit warnings (45 over 2026-07-28→08-02): trivial, 0.30s
  self-resolving backoff every time, trending DOWN (28→17→15→11→2/day) — not the cause.
- No other `[ERROR]`/`[CRITICAL]` log classes at all in the bridge over the 4-day window besides
  the two below.

## What was found: real, recurring silent message loss

`POST /api/notify` (used by `bin/notify.sh`/`notify_discord.sh`/`notify_thread.sh` — called by
every cron alert, watchdog, dispatch completion notice, incident escalation) crashed with a
500 and the message was **never posted, no retry, caller never told** — ~10 occurrences across
2026-07-30 → 08-01 (`journalctl --user -u ccdb-mike.service`), two distinct causes:

1. **Embed description over Discord's 4096-char cap** — `discord.errors.HTTPException: 400 Bad
   Request (error code: 50035): Invalid Form Body — In embeds.0.description: Must be 4096 or
   fewer in length.` Fires whenever a long status/report/incident message goes through
   `notify_discord.sh`'s `format: embed` path (which has no length guard, unlike
   `notify_thread.sh`'s `format: text` path, which already chunks at 1900 chars).
2. **Malformed UTF-8 in the raw request body** — `UnicodeDecodeError: 'utf-8' codec can't decode
   byte 0xc4 in position 321: invalid continuation byte`, thrown inside aiohttp's `request.json()`
   before the handler even runs. The two known `mike/bin/` callers both build the payload via
   Python `json.dumps(...).encode()`, which raises loudly on an invalid string rather than
   emitting corrupt bytes — so the actual sender of the bad body is **not yet identified**
   (candidate: some other session/script somewhere on the account hand-rolling a raw `curl -d`
   JSON body without going through Python's UTF-8-safe encoder).

This class of bug matches the user's report well: a status update or escalation silently
vanishing looks exactly like "Mike went quiet on this topic," even though the underlying script
ran to completion on Mike's side with no visible error.

## Fix applied (commit — see `git log -- bin/notify_discord.sh`)

`bin/notify_discord.sh`: truncate the message **character-wise** (Python `str` slicing on an
already-decoded string, never a raw byte cut — avoids reintroducing a UTF-8-corruption bug while
fixing this one) to 4000 chars before building the payload, with a "cắt bớt" marker appended.
Verified live against the running bridge: a 7080-char test message that previously 500'd now
returns 200.

## UnicodeDecodeError — RESOLVED 2026-08-03 (commit `cacbfb9c`)

Root cause found by tracing the actual mechanism, not by finding "who sends bad bytes":
under a minimal locale (cron/systemd env, confirmed via `env -i python3 -c "print(sys.stdout.
encoding, sys.stdout.errors)"` → `utf-8 surrogateescape`), Python decodes argv with
`surrogateescape`. Any invalid UTF-8 byte that ever reaches `$msg` upstream (e.g. Vietnamese
text mangled by a Windows-encoding mismatch somewhere in the fleet — this codebase runs
partly on Windows per `CLAUDE.md`) survives as a lone surrogate codepoint straight through
`json.dumps(message, ensure_ascii=False)` and round-trips back out through `print()`'s
surrogateescape-encoded stdout as the exact same invalid byte. Reproduced live (single bad
byte in argv → identical bad byte in the JSON payload bytes → fails `.decode('utf-8')`).
aiohttp's strict-UTF-8 `request.json()` then 500s and the message is dropped, no retry.

**Fix**: `bin/notify_discord.sh` and `bin/notify_thread.sh` now sanitize `message`/`title`/
`thread_name` by round-tripping `encode('utf-8','surrogateescape').decode('utf-8','replace')`
before building the JSON payload — any corrupt byte becomes a visible U+FFFD instead of an
invalid byte on the wire. This fixes the bug class regardless of which upstream script
introduces bad bytes — no single "sender" needed to be identified. Verified live: a message
with an injected `0xc4` byte now returns HTTP 200 from the real `ccdb-mike` bridge (journalctl
confirms), where it previously would have 500'd.

**Separately discovered, NOT acted on (needs explicit sign-off)**: `/workspace/claude-code-
discord-bridge` (shared infra, used by every concurrent session on the account) already
gained its own defensive fix for this same class of error upstream — commit `ca0fde9`
(2026-08-02 06:01:51 UTC), "catch UnicodeDecodeError alongside JSONDecodeError on all 8
request.json() call sites". But `ccdb-mike.service`'s running process was started
**2026-07-31 15:17:39 UTC — before that fix landed** (`systemctl --user show ccdb-mike.service
-p ActiveEnterTimestamp` confirms no restart since). The live process does not have that fix
loaded. This sender-side fix is independent and closes the hole either way, but the bridge
itself is running stale code; restarting `ccdb-mike.service` affects every concurrent session
on the account right now, so that restart was intentionally left for the user to authorize
rather than done unilaterally.
