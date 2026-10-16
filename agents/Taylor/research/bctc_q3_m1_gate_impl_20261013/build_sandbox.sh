#!/usr/bin/env bash
# build_sandbox.sh <thư mục sandbox> <rev repo ngoài> <thư mục mike nguồn (worktree hoặc canonical)>
# Sandbox CÓ git (clone --shared) để các selfcheck đọc `git show <rev ghim>` chạy được; đường dẫn canonical
# trong *.py/*.sh được sed sang sandbox. secrets + CSV pin = symlink CHỈ ĐỌC; data chưa track = bản sao.
set -euo pipefail
SB="$1"; REV="$2"; MSRC="$3"; CAN=/home/trido/thanhdt/WorkingClaude
rm -rf "$SB"; git clone -q --shared --no-checkout /home/trido/thanhdt "$SB/thanhdt"
git -C "$SB/thanhdt" checkout -q --detach "$REV"
W="$SB/thanhdt/WorkingClaude"; mkdir -p "$W/mike/agents/Winston" "$W/mike/agents/Taylor" "$W/mike/agents/Mafee"
rsync -a --exclude='__pycache__' "$MSRC/bin" "$MSRC/kb" "$MSRC/hooks" "$W/mike/"
for f in agents/Winston/freshness_warn_selfcheck.py agents/Taylor/capit_dd_gate_selfcheck.py agents/Mafee/push_recommend_v23_to_bq.py; do
  [ -f "$MSRC/$f" ] && cp "$MSRC/$f" "$W/mike/$f" || { [ -f "$CAN/mike/$f" ] && cp "$CAN/mike/$f" "$W/mike/$f"; } || true; done
for f in earnings_surprise_data.pkl earnings_events_classified.csv golive_v23_status.json anomaly_flags.json forensic_flags.csv \
         macro_health.json lag_edge_health.csv pt_v22_dt5g_logs.csv; do [ -e "$W/data/$f" ] || cp -p "$CAN/data/$f" "$W/data/" 2>/dev/null || true; done
for f in "$CAN"/data/v23_golive_audit_2014_now_*.csv; do [ -e "$W/data/$(basename "$f")" ] || ln -s "$f" "$W/data/$(basename "$f")"; done
mkdir -p "$W/deploy_golive_dt5g_v4/out"; cp -p "$(ls -1t "$CAN"/deploy_golive_dt5g_v4/out/golive_v23_recommendations_*.csv | head -1)" "$W/deploy_golive_dt5g_v4/out/" 2>/dev/null || true
[ -e "$W/secrets" ] || ln -s "$CAN/secrets" "$W/secrets"
grep -rlI "/home/trido/thanhdt/WorkingClaude" "$W" --include=*.py --include=*.sh 2>/dev/null | xargs -r sed -i "s#/home/trido/thanhdt/WorkingClaude#$W#g"
echo "$W"
