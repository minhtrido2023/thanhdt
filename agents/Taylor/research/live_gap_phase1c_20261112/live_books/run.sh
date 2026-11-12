#!/bin/bash
# vị thế theo book mỗi phiên (park_holdings.py, read-only) — job Taylor_20261112_122855
cd /home/trido/thanhdt/WorkingClaude; source wc_env.sh >/dev/null 2>&1
O=mike/agents/Taylor/research/live_gap_phase1c_20261112/live_books
for a in SpaceX ZaloPay; do for f in data/execution_logs/nav_snapshot_${a}_2026-*.json; do d=$(basename $f .json); d=${d##*_}
  [[ "$d" > "2026-11-11" ]] && continue
  python3 mike/bin/park_holdings.py --account $a --asof $d --json > $O/${a}_$d.json 2>$O/${a}_$d.err || echo "FAIL $a $d"; done; done
echo DONE
