#!/usr/bin/env bash
# sync_native_agents.sh — mirror the LIVE native-subagent defs into the fleet repo.
#
# Live (source of truth, read by Claude Code) = ~/.claude/agents/*.md  (outside both git repos).
# Mirror (version-controlled, backed up via mike-fleet) = mike/agents_native/.
# This copies live -> mirror (one direction). Run manually after editing an agent, or let
# fleet_backup.sh call it before each daily push. README.md in the mirror is preserved.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE="$HOME/.claude/agents"
MIRROR="$ROOT/agents_native"
mkdir -p "$MIRROR"

[ -d "$LIVE" ] || { echo "no live agents dir: $LIVE"; exit 0; }
changed=0
for f in "$LIVE"/*.md; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  if ! cmp -s "$f" "$MIRROR/$base" 2>/dev/null; then
    cp "$f" "$MIRROR/$base"
    echo "synced: $base"
    changed=1
  fi
done
# Skill dispatch-routing cũng nằm ngoài cả 2 repo (~/.claude/skills) và chép luật từ
# kb/mike_model_routing.md — gương 1 bản có version để revert/backup được (2026-10-11).
SKILL_LIVE="$HOME/.claude/skills/dispatch-routing/SKILL.md"
SKILL_MIRROR="$MIRROR/skills/dispatch-routing/SKILL.md"
if [ -f "$SKILL_LIVE" ] && ! cmp -s "$SKILL_LIVE" "$SKILL_MIRROR" 2>/dev/null; then
  mkdir -p "$(dirname "$SKILL_MIRROR")"
  cp "$SKILL_LIVE" "$SKILL_MIRROR"
  echo "synced: skills/dispatch-routing/SKILL.md"
  changed=1
fi
[ "$changed" = 0 ] && echo "native agents already in sync"
exit 0
