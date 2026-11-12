#!/bin/bash
# Luồng D (job Taylor_20261112_151837): copy make_sandbox phase1b; code=worktree wt-livegap-D-1112 (sb engine + carry knob).
# data/ = symlink canonical, trừ file LAG-family = frozen_lag của phase1b (y hệt sb_liq).
set -euo pipefail
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1b_20261112
D="$(cd "$(dirname "$0")" && pwd)"; NAME="$1"; CODE="$2"; WC=/home/trido/thanhdt/WorkingClaude
S="$D/sb_$NAME"; rm -rf "$S"; mkdir -p "$S/data"
for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -s "$f" "$S/data/$(basename "$f")"; done
ln -s /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1_20261112/bq_cache_asof20261111 "$S/data/bq_cache_asof20261111" 2>/dev/null || true
for f in "$R"/frozen_lag/*.pkl "$R"/frozen_lag/*.csv; do b=$(basename "$f"); rm -f "$S/data/$b"; ln -s "$f" "$S/data/$b"; done
echo "sandbox $S ready (code=$CODE)"
