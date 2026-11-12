#!/bin/bash
# Sandbox PT_WORKDIR cho GĐ1 (job Taylor_20261112_104204). Gốc = code worktree research/live-gap-p1-20261112
# (symlink), data/ = symlink data/ canonical; thêm bq_cache_asof20261111 (bản chép đông cứng data/bq_cache
# verified 2026-11-11T16:59Z). TAG=adj: thay 4 file LAG bằng bản cơ sở-giá-điều-chỉnh v2 của nhánh
# feat/lag-cache-adjusted-20261110 (pkl end 2026-11-09, build_manifest_v2.json). Không ghi gì vào data/ canonical.
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; TAG="$1"
CODE=/home/trido/thanhdt/WorkingClaude/wt-livegap-p1-1112/WorkingClaude
WC=/home/trido/thanhdt/WorkingClaude
LA=$WC/mike/agents/Taylor/wt-mike-lagadj-1110/agents/Taylor/research/lag_cache_adjusted_20261110
S="$R/sandbox_$TAG"; rm -rf "$S"; mkdir -p "$S/data"
for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -s "$f" "$S/data/$(basename "$f")"; done
ln -s "$R/bq_cache_asof20261111" "$S/data/bq_cache_asof20261111"
if [ "$TAG" = adj ]; then
  for f in earnings_events_classified.csv lag_edge_health.csv; do rm "$S/data/$f"; cp "$LA/derived_v2/${f%.csv}_adjv2.csv" "$S/data/$f"; done
  rm "$S/data/earnings_px.pkl" "$S/data/lagged_pos_ov.pkl"
  cp "$LA/v2/earnings_px_adj.pkl" "$S/data/earnings_px.pkl"; cp "$LA/v2/lagged_pos_ov_adj.pkl" "$S/data/lagged_pos_ov.pkl"
fi
md5sum "$S"/data/{earnings_px.pkl,lagged_pos_ov.pkl,earnings_events_classified.csv,lag_edge_health.csv} | sed "s#$S/##"
echo "sandbox $S ready"
