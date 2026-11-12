#!/bin/bash
# Luồng E (job Taylor_20261112_151839). 2 sandbox ĐÓNG BĂNG, code = symlink worktree E (c27fe6823 + hook PARK_NOJIT/NOSELL_UNTIL):
#  sb/  : data = bản chép data sandbox p1c (frozen LAG 12/11) — md5 phải = p1c sandbox_data_md5.txt
#  sbv/ : như sb/ nhưng 3 file LAG thay bằng vintage 10-29 (pin-era) — cho E3 tie-break
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; WC=/home/trido/thanhdt/WorkingClaude
CODE=$WC/wt-livegap-E-1112/WorkingClaude; P1C=$R/../live_gap_phase1c_20261112; V=$R/../live_gap_phase1b_20261112/vintage_20261029
for S in "$R/sb" "$R/sbv"; do
  [ -d "$S" ] && chmod -R u+w "$S" && rm -rf "$S"; mkdir -p "$S"
  for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
  cp -rp "$P1C/sb/data" "$S/data"; chmod -R u+w "$S/data"
done
for b in earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv; do cp -p "$V/$b" "$R/sbv/data/$b"; done
for S in sb sbv; do chmod -R a-w "$R/$S/data"/*.csv "$R/$S/data"/*.pkl "$R/$S/data/snapshots" "$R/$S/data"/bq_cache_*
  (cd "$R/$S/data" && find . -type f | sort | xargs md5sum) > "$R/${S}_data_md5.txt"; done
diff "$R/sb_data_md5.txt" "$P1C/sandbox_data_md5.txt" && echo "sb data == p1c sandbox (md5)"
echo "sandboxes ready"
