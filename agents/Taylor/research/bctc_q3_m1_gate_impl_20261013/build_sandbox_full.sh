#!/usr/bin/env bash
# build_sandbox_full.sh <sandbox> <rev repo ngoài> <mike nguồn> — như build_sandbox.sh + bù đầu vào mà 5 selfcheck
# (money_path / freshness_ops / dt5g_chain / freshness_warn / filter_lag_entry_window) cần: agents Winston+Spyros,
# data/_quarantine, và mọi file data/ cấp 1 < 3MB chưa có (BẢN SAO, không symlink → selfcheck ghi không chạm production).
set -euo pipefail
SB="$1"; REV="$2"; MSRC="$3"; CAN=/home/trido/thanhdt/WorkingClaude; HERE="$(cd "$(dirname "$0")" && pwd)"
bash "$HERE/build_sandbox.sh" "$SB" "$REV" "$MSRC" >/dev/null
W="$SB/thanhdt/WorkingClaude"
for a in Winston Spyros Taylor; do mkdir -p "$W/mike/agents/$a"
  for f in "$CAN/mike/agents/$a"/*.py; do b=$(basename "$f")
    if [ -f "$MSRC/agents/$a/$b" ]; then cp -n "$MSRC/agents/$a/$b" "$W/mike/agents/$a/$b"; else cp -n "$f" "$W/mike/agents/$a/$b"; fi; done; done
find "$CAN/data" -maxdepth 1 -type f -size -3M | while read -r f; do [ -e "$W/data/$(basename "$f")" ] || cp -p "$f" "$W/data/"; done
rsync -a --ignore-existing "$CAN/data/_quarantine/" "$W/data/_quarantine/"
grep -rlI "/home/trido/thanhdt/WorkingClaude" "$W/mike/agents" --include=*.py --include=*.sh 2>/dev/null | xargs -r sed -i "s#/home/trido/thanhdt/WorkingClaude#$W#g"
rsync -a --ignore-existing --max-size=3m "$CAN/deploy_golive_dt5g_v4/out/" "$W/deploy_golive_dt5g_v4/out/"
echo "$W"
