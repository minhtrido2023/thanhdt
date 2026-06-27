#!/usr/bin/env bash
# stop.sh — kill the bot. NOTE: cron's */5 start.sh will revive it within 5 min;
# to stop permanently, also comment out the two crontab lines (see README).
PATTERN="/home/trido/thanhdt/discord_bot/venv/bin/python /home/trido/thanhdt/discord_bot/bot.py"
pkill -f "$PATTERN" 2>/dev/null || true
