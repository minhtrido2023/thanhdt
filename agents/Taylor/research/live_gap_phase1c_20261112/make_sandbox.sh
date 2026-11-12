#!/bin/bash
# GĐ1 vòng 3 (job Taylor_20261112_122855). Sandbox ĐÓNG BĂNG: code = symlink worktree p1c (c27fe6823, đã vá mergesort);
# data/ = BẢN CHÉP (cp, không symlink canonical) của đúng các file engine mở (trace phase1b) + 2 bq cache + snapshot CA.
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; S="$R/sb"; WC=/home/trido/thanhdt/WorkingClaude
CODE=$WC/wt-livegap-p1c-1112/WorkingClaude; FZ=$R/../live_gap_phase1b_20261112/frozen_lag
rm -rf "$S"; mkdir -p "$S/data/snapshots"
for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
for b in earnings_events_classified.csv earnings_surprise_data.pkl lag_edge_health.csv earnings_px.pkl lagged_pos_ov.pkl; do cp -p "$FZ/$b" "$S/data/$b"; done
cp -p $WC/data/forensic_flags.csv "$S/data/"
cp -p $WC/data/snapshots/corp_action_share_20260927.parquet "$S/data/snapshots/"
cp -rp $WC/data/bq_cache_asof20260729_postrestate "$S/data/"
cp -rp $R/../live_gap_phase1_20261112/bq_cache_asof20261111 "$S/data/"
chmod -R a-w "$S/data"/*.csv "$S/data"/*.pkl "$S/data/snapshots" "$S/data"/bq_cache_*
(cd "$S/data" && find . -type f | sort | xargs md5sum) > "$R/sandbox_data_md5.txt"
echo "sandbox $S ready"
