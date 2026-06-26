#!/usr/bin/env bash
# golive_01jul.sh — flip SpaceX account to enabled=true and restart Bill+Mafee
# Runs once on 2026-07-01 08:00 ICT (01:00 UTC) via cron, then removes itself.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACCOUNTS="$ROOT/../secrets/trading_bot_accounts.json"

# Flip SpaceX enabled=true
python3 - <<'PYEOF'
import json, sys
path = sys.argv[1]
d = json.load(open(path))
changed = False
for acct in d.get("accounts", []):
    if acct.get("label") == "SpaceX":
        acct["enabled"] = True
        acct["live_start"] = "2026-07-01"
        changed = True
if not changed:
    print("ERROR: SpaceX account not found in trading_bot_accounts.json", file=sys.stderr)
    sys.exit(1)
json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
print("SpaceX enabled=true")
PYEOF "$ACCOUNTS"

# Restart Bill and Mafee so they pick up the new config
systemctl --user restart mike@DollarBill mike@Mafee || true

# Notify via Telegram
"$ROOT/bin/notify.sh" "🚀 GO-LIVE V2.4 — 2026-07-01: SpaceX (0002023347) LIVE. Bill+Mafee restarted. Chúc may mắn!" 2>/dev/null || true

# Record to bus
"$ROOT/bin/append_event.sh" Mike decision "golive-executed-2026-07-01" \
  '{"summary":"SpaceX enabled=true, Bill+Mafee restarted, V2.4 LIVE","account":"0002023347","date":"2026-07-01"}' || true

# Remove self from cron (one-shot)
TMPFILE=$(mktemp)
crontab -l 2>/dev/null | grep -v "golive_01jul" > "$TMPFILE" || true
crontab "$TMPFILE"
rm -f "$TMPFILE"

echo "Go-live complete: $(date)"
