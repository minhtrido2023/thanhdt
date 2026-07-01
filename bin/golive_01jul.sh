#!/usr/bin/env bash
# golive_01jul.sh — verify SpaceX enabled and send Discord confirm.
# Runs once on 2026-07-01 08:00 ICT (01:00 UTC) via cron, then removes itself.
# NOTE: Bill/Mafee are headless (daemon disabled 2026-06-25).
# Execution is done by run_bot.sh (cron 02:05 UTC = 09:05 ICT).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACCOUNTS="$ROOT/../secrets/trading_bot_accounts.json"

# Verify SpaceX enabled=true (user already did this; idempotent)
python3 - "$ACCOUNTS" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
for acct in d.get("accounts", []):
    if acct.get("label") == "SpaceX":
        if not acct.get("enabled"):
            acct["enabled"] = True
            acct["live_start"] = "2026-07-01"
            json.dump(d, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
            print("SpaceX: enabled=false → flipped to true")
        else:
            print("SpaceX: enabled=true (OK, no change)")
        sys.exit(0)
print("ERROR: SpaceX account not found", file=sys.stderr)
sys.exit(1)
PYEOF

# Notify
"$ROOT/bin/notify.sh" "🚀 GO-LIVE V2.4 — 2026-07-01: SpaceX LIVE. bot_execute sẽ khởi động lúc 09:05 ICT." 2>/dev/null || true

_tid="1521470705563340910"  # Trading Daily thread
"$ROOT/bin/notify_thread.sh" "🚀 **GO-LIVE V2.4** — 2026-07-01 SpaceX LIVE. bot_execute khởi động 09:05 ICT (cron). Theo dõi log: logs/run_bot_SpaceX_2026-07-01.log" "$_tid" 2>/dev/null || true

"$ROOT/bin/append_event.sh" Mike decision "golive-executed-2026-07-01" \
  '{"summary":"SpaceX enabled=true verified, bot_execute via cron 09:05 ICT","account":"0002023347","date":"2026-07-01"}' || true

# Remove self from cron (one-shot)
TMPFILE=$(mktemp)
crontab -l 2>/dev/null | grep -v "golive_01jul" > "$TMPFILE" || true
crontab "$TMPFILE"
rm -f "$TMPFILE"

echo "Go-live preflight complete: $(date)"
