#!/bin/bash
# Dựng sandbox cho ladder Luồng A: sb/<fam><sort>_<lagdata>. Code = symlink file từ worktree; data/ = symlink
# data canonical, rồi ghi đè 5 file LAG-family: nền = frozen_lag 12/11 (phase1b), vintage ⇒ thay 3 file vintage
# 10-29, adjv2 ⇒ thay thêm 4 file adj v2 (giữ pkl surprise vintage). Usage: make_sandboxes.sh
set -euo pipefail
A="$(cd "$(dirname "$0")" && pwd)"; WC=/home/trido/thanhdt/WorkingClaude
P1B=$WC/mike/agents/Taylor/research/live_gap_phase1b_20261112
mk() { # name codedir lagdata
  local S="$A/sb/$1" CODE="$2" L="$3"; rm -rf "$S"; mkdir -p "$S/data"
  for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
  for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -sfn "$f" "$S/data/$(basename "$f")"; done
  for f in "$P1B"/frozen_lag/*.pkl "$P1B"/frozen_lag/*.csv; do ln -sfn "$f" "$S/data/$(basename "$f")"; done
  case "$L" in
    frozen20261112) ;;
    vintage20261029) for f in earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv; do ln -sfn "$P1B/vintage_20261029/$f" "$S/data/$f"; done;;
    adjv2_20261110) ln -sfn "$P1B/vintage_20261029/earnings_surprise_data.pkl" "$S/data/earnings_surprise_data.pkl"
       for f in earnings_events_classified.csv lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl; do ln -sfn "$A/lagdata/adjv2_20261110/$f" "$S/data/$f"; done;;
    *) echo "LAG_DATA lạ $L" >&2; exit 8;;
  esac
  (cd "$S/data" && md5sum earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl) > "$S/LAG_MD5"
  echo "$1 <- $CODE ($(git -C "$CODE" rev-parse --short HEAD)) $L"
}
B=/home/trido/thanhdt/wt-livegapA-1112
for L in vintage20261029 adjv2_20261110 frozen20261112; do
  mk bq_$L  ${B}-q/WorkingClaude  $L;  mk bm_$L  $B/WorkingClaude     $L;  mk btb_$L ${B}-tb/WorkingClaude $L
  mk rq_$L  ${B}-rq/WorkingClaude $L;  mk rm_$L  ${B}-rm/WorkingClaude $L; mk rtb_$L ${B}-rtb/WorkingClaude $L
done
