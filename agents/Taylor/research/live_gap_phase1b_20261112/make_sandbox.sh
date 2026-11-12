#!/bin/bash
# sandbox cho vòng 2: <name> <code_dir>. data/ = symlink canonical, trừ 5 file LAG-family = bản chép đông cứng frozen_lag/
# (chụp 2026-11-12 ~18:40 ICT). Tuỳ chọn SWAP="file=path ..." thay riêng file đó (control hoán file).
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; NAME="$1"; CODE="$2"; WC=/home/trido/thanhdt/WorkingClaude
S="$R/sb_$NAME"; rm -rf "$S"; mkdir -p "$S/data"
for f in "$CODE"/*; do b=$(basename "$f"); [ "$b" = data ] || ln -s "$f" "$S/$b"; done
for f in "$WC"/data/* "$WC"/data/.[!.]*; do [ -e "$f" ] && ln -s "$f" "$S/data/$(basename "$f")"; done
ln -s /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_phase1_20261112/bq_cache_asof20261111 "$S/data/bq_cache_asof20261111" 2>/dev/null || true
for f in "$R"/frozen_lag/*.pkl "$R"/frozen_lag/*.csv; do b=$(basename "$f"); rm -f "$S/data/$b"; ln -s "$f" "$S/data/$b"; done
for kv in ${SWAP:-}; do k=${kv%%=*}; v=${kv#*=}; rm -f "$S/data/$k"; ln -s "$v" "$S/data/$k"; done
echo "sandbox $S ready (code=$CODE swap=${SWAP:-none})"
