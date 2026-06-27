#!/usr/bin/env bash
# run.sh — the REAL bot process (foreground). start.sh backgrounds this.
# Exec's with ABSOLUTE paths so the cmdline always contains the distinctive
# token "discord_bot/venv/bin/python" that start/restart/stop match on.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

# Optional secrets file. The Discord token lives in config.json today, but if a
# .env is ever added it is sourced here so env changes take effect on restart.
if [ -f "$HERE/.env" ]; then set -a; . "$HERE/.env"; set +a; fi

exec "$HERE/venv/bin/python" "$HERE/bot.py"
