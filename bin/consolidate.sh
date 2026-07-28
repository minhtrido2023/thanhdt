#!/usr/bin/env bash
# consolidate.sh — mechanical Phase-1 consolidator (no LLM, no BigQuery).
# Runs hourly from cron (:07) AND after every dispatch. Single-writer (flock). Steps:
#   1. Gather NEW events from each child's inbox (content-anchored cursor → no re-ingestion,
#      and no silent skip when kb_nightly.sh prunes lines off the head of a file).
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

# --- 1. gather new events via per-file CONTENT-anchored cursors ---
# Each cursor remembers the event_id+ts of the last line it read, not just a line count, so a
# head-prune by kb_nightly.sh is repaired by relocating that event instead of trusting a number
# the prune invalidated. See mike_json.py:cmd_cursor_advance for the two loss modes this closes
# (stranded cursor AND the silent leapfrog that ate an event on 2026-07-28).
NEW="$(mktemp)"; REPAIRS="$(mktemp)"; trap 'rm -f "$NEW" "$REPAIRS"' EXIT
for f in "$BUS"/inbox/*.jsonl; do
  base="$(basename "$f")"
  python3 "$PY" cursor-advance "$f" "$STATE/$base" >> "$NEW" 2>>"$REPAIRS" \
    || echo "CURSOR-ERROR $base cursor-advance failed (cursor left untouched)" >> "$REPAIRS"
    # field 1=CURSOR-ERROR, field 2=$base, field 3=cursor-advance (the failing subcommand name)
done

# A repaired cursor means events were at risk of being dropped — that MUST reach a human.
# Previously this was an echo into logs/consolidator.log, which nobody reads: the 2026-07-28
# loss ran 9h unnoticed. notify.sh is dedup'd and always exits 0, so this can't break the run.
# Debounced per file (state/cursorwarn/<base>, same shape watchdog.sh uses for stale pipelines):
# a repair that can't self-clear would otherwise alert AND append a bus error on every hourly
# and post-dispatch run — each of those bumps the KB, commits, and posts to Discord, so the
# alarm itself would become the event storm. A CHANGED repair line still alerts immediately.
WARN_DIR="$ROOT/state/cursorwarn"; mkdir -p "$WARN_DIR"
SEEN="$(mktemp)"; trap 'rm -f "$NEW" "$REPAIRS" "$SEEN"' EXIT
if [ -s "$REPAIRS" ]; then
  cat "$REPAIRS"                       # anything unexpected (a traceback) still reaches the log
  while IFS= read -r r; do
    case "$r" in CURSOR-*) ;; *) continue ;; esac   # only our own structured lines alert
    echo "$(date -u +%FT%TZ) $r"
    wbase="$(echo "$r" | awk '{print $2}' | tr -c 'A-Za-z0-9._-' '_')"; wmark="$WARN_DIR/${wbase:-unknown}"
    echo "${wbase:-unknown}" >> "$SEEN"
    # Debounce key = repair KIND (field 3, e.g. resync-ts/resync-id/clamp-legacy; for a
    # CURSOR-ERROR line field 3 is the failing subcommand name, "cursor-advance") PLUS the
    # `recovered=` count, not the whole line — the line also carries prev=/total=, which
    # change on every run of a file still being appended to, so comparing the full line never
    # matched twice and the debounce silently never fired on a busy file (the exact case that
    # matters most: a repair recurring on a hot inbox). Full `$r` still goes to notify.sh below
    # so a human sees the real numbers; only the dedup KEY is stable — same kind AND recovered
    # not growing = suppressed; recovered ESCALATING re-alerts even mid-streak, so a repair
    # that's getting worse can't hide behind the debounce meant for a steady-state one.
    wkind="$(echo "$r" | awk '{print $3}')"
    [ -n "$wkind" ] || wkind="$r"   # malformed/short line (no field 3) -> key is never empty
    wrecovered="$(echo "$r" | sed -n 's/.*recovered=\([0-9]*\).*/\1/p')"; wrecovered="${wrecovered:-0}"
    wold="$(cat "$wmark" 2>/dev/null || true)"
    wold_kind="${wold% recovered=*}"; wold_recovered="${wold##*recovered=}"
    case "$wold_recovered" in ''|*[!0-9]*) wold_recovered=0 ;; esac
    if [ "$wold_kind" = "$wkind" ] && [ "$wrecovered" -le "$wold_recovered" ]; then
      continue   # same kind, not worse than last reported -> already seen, suppressed
    fi
    printf '%s recovered=%s' "$wkind" "$wrecovered" > "$wmark"
    "$ROOT/bin/notify.sh" "⚠️ consolidate.sh CURSOR REPAIR — KB ingestion đã lệch, kiểm tra event có bị bỏ sót:
\`$r\`" >/dev/null 2>&1 || true
    "$ROOT/bin/append_event.sh" Mike error "consolidate-cursor-repair" \
      "$(python3 -c 'import json,sys; print(json.dumps({"detail": sys.argv[1], "note": "cursor state/offsets lech so voi bus/inbox — da tu chua; prev cu nam trong detail de doi chieu neu can khoi phuc tay"}))' "$r")" \
      >/dev/null 2>&1 || true
  done < "$REPAIRS"
fi
# Clear the marker for every file that repaired cleanly this run, so the NEXT occurrence of
# the same repair is reported again instead of being swallowed as "already seen".
for wmark in "$WARN_DIR"/*; do
  [ -e "$wmark" ] || continue
  grep -qxF "$(basename "$wmark")" "$SEEN" 2>/dev/null || rm -f "$wmark"
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
  # Scoped to kb/ (matches kb_nightly.sh's existing `git add kb/`, line ~484) — NOT `-A`.
  # `-A` stages the whole repo (everything `.gitignore` doesn't exclude: bin/, agents/, root
  # docs — bus/state/logs/locks are gitignored, so those were never actually at risk), which
  # means any in-progress edit to a script sitting uncommitted gets silently swept into this
  # hourly/post-dispatch auto-commit under a generic "consolidate KB vNNNN" message — it
  # happened for real 2026-07-28 (twice, mid-session) to a careful safety-critical fix whose
  # detailed rationale got replaced by this one-line message. consolidate.sh only ever WRITES
  # inside kb/ (context_pack.md, events_buffer.md, version.txt, recent_delta.jsonl,
  # fleet_status.md via publish_context.sh + the fleet-status step below) — nothing it does
  # legitimately touches bin/ or the repo root.
  git -C "$ROOT" add kb/ 2>/dev/null || true
  # `-- kb/` on commit too (arch-review round 2, 2026-07-28): `git add kb/` only controls what
  # gets STAGED here — `git commit` with no pathspec commits the WHOLE INDEX. If some other
  # in-flight session had already run `git add bin/foo.sh` (or staged one hunk of it) a moment
  # before this runs, that staged-but-uncommitted file still rides along into "consolidate KB
  # vNNNN" without the pathspec. Reproduced in review; verified this pathspec leaves any such
  # staged file exactly as staged (not committed, not unstaged) afterward.
  git -C "$ROOT" commit -q -m "consolidate $(date -u +%FT%TZ) (KB v$(cat "$KB/version.txt"))" -- kb/ 2>/dev/null || true
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
