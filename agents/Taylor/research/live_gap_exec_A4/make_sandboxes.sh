#!/bin/bash
# Luồng A3: dựng sb/<fam>_<lagdata> y hệt make_sandboxes.sh Luồng A (code = symlink worktree A3; data = canonical +
# ghi đè LAG-family: nền frozen 12/11 phase1b; vint ⇒ 3 file vintage 10-29; adj ⇒ 4 file adj v2 + pkl surprise vintage).
set -euo pipefail
A3="$(cd "$(dirname "$0")" && pwd)"; WC=/home/trido/thanhdt/WorkingClaude
P1B=$WC/mike/agents/Taylor/research/live_gap_phase1b_20261112; LA=$WC/mike/agents/Taylor/research/live_gap_exec_A
mk() { local S="$A3/sb/$1" CODE="$2" L="$3"; rm -rf "$S"; mkdir -p "$S/data"
  for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
  for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -sfn "$f" "$S/data/$(basename "$f")"; done
  for f in "$P1B"/frozen_lag/*.pkl "$P1B"/frozen_lag/*.csv; do ln -sfn "$f" "$S/data/$(basename "$f")"; done
  case "$L" in
    vint) for f in earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv; do ln -sfn "$P1B/vintage_20261029/$f" "$S/data/$f"; done;;
    adj) ln -sfn "$P1B/vintage_20261029/earnings_surprise_data.pkl" "$S/data/earnings_surprise_data.pkl"
       for f in earnings_events_classified.csv lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl; do ln -sfn "$LA/lagdata/adjv2_20261110/$f" "$S/data/$f"; done;;
    *) exit 8;; esac
  (cd "$S/data" && md5sum earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl) > "$S/LAG_MD5"
  echo "$1 <- $CODE ($(git -C "$CODE" rev-parse --short HEAD)) $L"; }
mk t_adj /home/trido/thanhdt/wt-livegapA4-1113-tb/WorkingClaude adj
for L in adj; do mk m_$L /home/trido/thanhdt/wt-livegapA4-1113/WorkingClaude $L; mk r_$L /home/trido/thanhdt/wt-livegapA4-1113-r/WorkingClaude $L; done
