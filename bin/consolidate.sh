#!/usr/bin/env bash
# consolidate.sh — mechanical Phase-1 consolidator (no LLM, no BigQuery).
# Runs from cron every 30 min. Single-writer (flock). Steps:
#   1. Gather NEW events from each child's inbox (line-offset tracking → no re-ingestion).
#   2. If any new: append them to KNOWLEDGE.md, bump version, rebuild context_pack, commit.
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
  [ -f "$KB/KNOWLEDGE.md" ] || printf '# Mike fleet — KNOWLEDGE (canonical log)\n' > "$KB/KNOWLEDGE.md"
  {
    printf '\n## Consolidation %s\n' "$(date -u +%FT%TZ)"
    python3 "$PY" format-events "$NEW" 2>/dev/null || true
  } >> "$KB/KNOWLEDGE.md"

  ver="$(tr -dc '0-9' < "$KB/version.txt" 2>/dev/null || true)"; ver="${ver:-0}"
  echo "$((ver + 1))" > "$KB/version.txt"
  "$ROOT/bin/publish_context.sh"

  if [ ! -d "$ROOT/.git" ]; then git -C "$ROOT" init -q; fi
  git -C "$ROOT" add -A 2>/dev/null || true
  git -C "$ROOT" commit -q -m "consolidate $(date -u +%FT%TZ) (KB v$(cat "$KB/version.txt"))" 2>/dev/null || true
  echo "$(date -u +%FT%TZ) consolidated new events → KB v$(cat "$KB/version.txt")"
else
  # Ensure context_pack exists even with no events yet.
  [ -f "$KB/context_pack.md" ] || "$ROOT/bin/publish_context.sh"
  echo "$(date -u +%FT%TZ) no new events"
fi

# --- 3. always refresh derived fleet status (dead = no heartbeat > 30 min) ---
python3 "$PY" fleet-status "$BUS/registry" > "$KB/fleet_status.md" 2>/dev/null || true

echo "$(date -u +%FT%TZ) fleet_status refreshed"
