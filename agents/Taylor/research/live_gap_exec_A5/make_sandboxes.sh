#!/bin/bash
# Luồng A5 (job Taylor_20261113_071030): sandbox = symlink worktree SẠCH + data canonical + ghi đè LAG-family (y A3/A4).
# m = main 7f25febc1 (wt-livegapA4-1113, git status sạch); r = research/live-gap-A5-r-20261113 e9a9aed1a (770393ce2 + 1 dòng A4 đã COMMIT).
set -euo pipefail
A5="$(cd "$(dirname "$0")" && pwd)"; WC=/home/trido/thanhdt/WorkingClaude
P1B=$WC/mike/agents/Taylor/research/live_gap_phase1b_20261112; LA=$WC/mike/agents/Taylor/research/live_gap_exec_A
mk() { local S="$A5/sb/$1" CODE="$2" L="$3"; rm -rf "$S"; mkdir -p "$S/data"
  [ -z "$(git -C "$CODE" status --porcelain)" ] || { echo "worktree $CODE KHÔNG sạch" >&2; exit 7; }
  for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
  for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -sfn "$f" "$S/data/$(basename "$f")"; done
  for f in "$P1B"/frozen_lag/*.pkl "$P1B"/frozen_lag/*.csv; do ln -sfn "$f" "$S/data/$(basename "$f")"; done
  case "$L" in
    vint) for f in earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv; do ln -sfn "$P1B/vintage_20261029/$f" "$S/data/$f"; done;;
    adj) ln -sfn "$P1B/vintage_20261029/earnings_surprise_data.pkl" "$S/data/earnings_surprise_data.pkl"
       for f in earnings_events_classified.csv lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl; do ln -sfn "$LA/lagdata/adjv2_20261110/$f" "$S/data/$f"; done;;
    *) exit 8;; esac
  (cd "$S/data" && md5sum earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl) > "$S/LAG_MD5"
  echo "$1 <- $CODE ($(git -C "$CODE" rev-parse HEAD)) $L"; }
mk m_adj /home/trido/thanhdt/wt-livegapA4-1113/WorkingClaude adj
mk m_vint /home/trido/thanhdt/wt-livegapA4-1113/WorkingClaude vint
mk r_adj /home/trido/thanhdt/wt-livegapA4-1113-r/WorkingClaude adj
mk r_vint /home/trido/thanhdt/wt-livegapA4-1113-r/WorkingClaude vint
