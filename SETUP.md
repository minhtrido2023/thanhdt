# Mike fleet — operator setup (Phase-1 spine)

The file plumbing (bus + hooks + mechanical consolidator + spawn/watchdog) is built and self-tested.
What remains needs you (interactive login / systemd / cron). Run these on **kaffa_v2** as user `trido`.

`MIKE_ROOT = /home/trido/thanhdt/WorkingClaude/mike`

## What's already proven (no action needed)
- A child appends a finding → `consolidate.sh` merges it → another child's next prompt gets the delta
  injected by the `UserPromptSubmit` hook, **without repeating** (version-cache dedup).
- Idempotent consolidation (line-offset tracking → no duplicate ingestion).
- Dead-detection (`fleet_status.md` marks agents with no heartbeat >30 min as `dead`).
- `spawn_child.sh` provisions a child (CLAUDE.md + hooks-wired settings.json + idle registry).
- Zero external dependencies beyond what's on the box: bash, python3, flock, git, systemd, claude.

## 1. Keep user services alive across logout/reboot
```bash
loginctl enable-linger trido
```

## 2. Confirm Remote Control works (interactive — only you can do this)
Remote Control requires a valid **claude.ai OAuth** login (it rejects API keys/tokens).
```bash
claude remote-control --name Test
# → open the Claude mobile app / claude.ai/code, confirm "Test" shows online, chat with it. Ctrl-C when done.
```
If it refuses, run `claude` once interactively and complete the claude.ai login, then retry.
Note the token lifetime — when it expires the bridge drops and you must re-login (see §6 watchdog).

## 3. Install the systemd unit template
```bash
mkdir -p ~/.config/systemd/user
cp "$HOME/thanhdt/WorkingClaude/mike/systemd/mike@.service" ~/.config/systemd/user/
systemctl --user daemon-reload
```

## 4. Spawn Mike + your first child, then start them
```bash
cd ~/thanhdt/WorkingClaude/mike
bin/spawn_child.sh Mike "Orchestrator" "Đầu mối điều phối fleet"      # provisions agents/Mike
bin/spawn_child.sh con-research "Research analyst" "Quét tín hiệu thị trường"

# start as durable remote-control sessions (only after §2 works):
systemctl --user enable --now mike@Mike
systemctl --user enable --now mike@con-research
systemctl --user status mike@Mike --no-pager
```
Both appear by name in the Claude mobile app / claude.ai/code. Talk to either directly.
> Mike's worktree is `agents/Mike`; its CLAUDE.md is the generic template. To give Mike its full
> orchestrator handbook, replace `agents/Mike/CLAUDE.md` with an `@`-import of `../../MIKE.md`
> (or copy MIKE.md's contents in).

## 5. Add the 30-minute consolidator + 10-minute watchdog to cron
`crontab -e` and append (these run alongside your 6 existing jobs; `:07/:37` avoids the 16:15 refresh):
```cron
7,37 * * * * /home/trido/thanhdt/WorkingClaude/mike/bin/consolidate.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/consolidator.log 2>&1
*/10 * * * * /home/trido/thanhdt/WorkingClaude/mike/bin/watchdog.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/watchdog.log 2>&1
```

## 6. (Optional) Wire failure alerts
`watchdog.sh` restarts dead units and, if `mike/bin/notify.sh` exists and is executable, calls it with a
message. Point it at your existing Telegram bot:
```bash
cat > ~/thanhdt/WorkingClaude/mike/bin/notify.sh <<'EOF'
#!/usr/bin/env bash
# notify.sh "<message>" — forward to your Telegram bot (fill in token/chat id or reuse trading_bot).
exit 0
EOF
chmod +x ~/thanhdt/WorkingClaude/mike/bin/notify.sh
```

## Daily use
- **Talk to a child**: open it by name in the app. It auto-reads shared KB (hooks); post durable results
  with `bin/append_event.sh <id> finding "<topic>" '<json>'`.
- **Ask Mike**: it reads `kb/` (+ runs `bin/consolidate.sh` on demand for fresh state) and answers, or
  drops a directive in `bus/directives/<child>.jsonl` for a child to pick up next time you open it.
- **Force an immediate sync**: `bin/consolidate.sh`.
- **Retire a child**: `systemctl --user disable --now mike@<id>` — its knowledge stays in the KB.

## When to move to Phase-2 (only if the spine proves insufficient)
BigQuery KB (SQL history/analytics across many agents), and/or an autonomous LLM consolidator. See the
plan file for the deferred-work notes and the bq-load dedup fix required before adding BigQuery.
