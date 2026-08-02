#!/bin/bash
# Build a symlink OVERLAY of the frozen pinned snapshot with ONE table replaced.
# Never touches data/bq_cache_asof20260729_postrestate (the pinned vintage, §8 discipline).
#   mk_overlay.sh <overlay_dir> <replacement_custom30v_8l.parquet>
set -euo pipefail
SRC=/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate
DST="$1"; REPL="$2"
rm -rf "$DST"; mkdir -p "$DST"
for f in "$SRC"/*; do
  b=$(basename "$f")
  [ "$b" = "custom30v_8l.parquet" ] && continue
  [ "$b" = "manifest.json" ] && continue
  ln -s "$f" "$DST/$b"
done
cp "$SRC/manifest.json" "$DST/manifest.json"
cp "$REPL" "$DST/custom30v_8l.parquet"
echo "overlay ready: $DST (custom30v_8l <- $REPL)"
