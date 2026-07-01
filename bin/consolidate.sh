#!/usr/bin/env bash
# consolidate.sh — mechanical Phase-1 consolidator (no LLM, no BigQuery).
# Runs from cron every 30 min. Single-writer (flock). Steps:
#   1. Gather NEW events from each child's inbox (line-offset tracking → no re-ingestion).
#   2. If any new: append them to events_buffer.md (episodic), bump version, rebuild context_pack, commit.
#      NOTE: KNOWLEDGE.md is canonical-only (Mike-edited). Raw events go to events_buffer.md.
#   3. Always refresh kb/fleet_status.md (derived dead-detection; never mutates child files).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB="$ROOT/kb"; BUS="$ROOT/bus"; STATE="$ROOT/state/offsets"
PY="$ROOT/bin/mike_json.py"
mkdir -p "$KB" "$BUS"/inbox "$BUS"/registry "$BUS"/directives "$STATE" "$ROOT/locks" "$ROOT/logs"
shopt -s nullglob

# --- single writer ---
exec 8>"$ROOT/locks/consolidator.lock"
flock -n 8 || { echo "$(date -u +%FT%TZ) another consolidator running, skip"; exit 0; }

# --- 1. gather new events via per-file line offsets ---
NEW="$(mktemp)"; trap 'rm -f "$NEW"' EXIT
for f in "$BUS"/inbox/*.jsonl; do
  base="$(basename "$f")"
  total="$(wc -l < "$f" 2>/dev/null | tr -dc '0-9')"; total="${total:-0}"
  prev="$(cat "$STATE/$base" 2>/dev/null | tr -dc '0-9' || true)"; prev="${prev:-0}"
  if [ "$total" -gt "$prev" ]; then
    tail -n +"$((prev + 1))" "$f" >> "$NEW"
    printf '%s' "$total" > "$STATE/$base"
  fi
done

# --- 2. if new knowledge: log + bump + republish + commit ---
if [ -s "$NEW" ]; then
  [ -f "$KB/events_buffer.md" ] || printf '# events_buffer — episodic buffer (consolidator-managed, do not edit)\n# Archive: kb_nightly.sh moves entries older than KEEP_DAYS to kb/archive/\n\n' > "$KB/events_buffer.md"
  {
    printf '\n## Consolidation %s\n' "$(date -u +%FT%TZ)"
    python3 "$PY" format-events "$NEW" 2>/dev/null || true
  } >> "$KB/events_buffer.md"

  ver="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; ver="${ver:-0}"
  newver=$((ver + 1)); echo "$newver" > "$KB/version.txt"

  # Per-version delta log: append THIS run's new events (summarized, tagged with
  # the version that ingested them) so the hook can serve each agent a TRUE delta.
  python3 "$PY" delta-append "$NEW" "$newver" >> "$KB/recent_delta.jsonl" 2>/dev/null || true
  tail -n 400 "$KB/recent_delta.jsonl" > "$KB/.rd.tmp" 2>/dev/null && mv -f "$KB/.rd.tmp" "$KB/recent_delta.jsonl" || true

  "$ROOT/bin/publish_context.sh"

  if [ ! -d "$ROOT/.git" ]; then git -C "$ROOT" init -q; fi
  git -C "$ROOT" add -A 2>/dev/null || true
  git -C "$ROOT" commit -q -m "consolidate $(date -u +%FT%TZ) (KB v$(cat "$KB/version.txt"))" 2>/dev/null || true
  echo "$(date -u +%FT%TZ) consolidated new events → KB v$(cat "$KB/version.txt")"

  # --- 2b. push new events to Discord #mike channel ---
  discord_summary="$(python3 "$PY" format-events "$NEW" 2>/dev/null | head -n 8 || true)"
  if [ -n "${discord_summary//[[:space:]]/}" ]; then
    has_question="$(grep -c '"event_type":"question"' "$NEW" 2>/dev/null)" || has_question=0
    if [ "$has_question" -gt 0 ]; then
      "$ROOT/bin/notify_discord.sh" "$discord_summary" "CẦN Ý KIẾN — KB v$(cat "$KB/version.txt")" 16711680 || true
    else
      "$ROOT/bin/notify_discord.sh" "$discord_summary" "Fleet Updates — KB v$(cat "$KB/version.txt")" 3447003 || true
    fi
  fi
else
  # Ensure context_pack exists even with no events yet.
  [ -f "$KB/context_pack.md" ] || "$ROOT/bin/publish_context.sh"
  echo "$(date -u +%FT%TZ) no new events"
fi

# --- 3. always refresh derived fleet status (dead = no heartbeat > 30 min) ---
python3 "$PY" fleet-status "$BUS/registry" > "$KB/fleet_status.md" 2>/dev/null || true

echo "$(date -u +%FT%TZ) fleet_status refreshed"
