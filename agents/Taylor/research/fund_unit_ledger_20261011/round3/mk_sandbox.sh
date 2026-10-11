#!/usr/bin/env bash
# Dựng sandbox khép kín /tmp/ar3/WC từ worktree (code) + ảnh dữ liệu của reviewer (/tmp/ar2/WC/data).
# KHÔNG đụng data/ thật. Dùng: mk_sandbox.sh [đích=/tmp/ar3/WC]
set -euo pipefail
WT=/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011
DST="${1:-/tmp/ar3/WC}"
rm -rf "$DST"; mkdir -p "$DST/mike"
cp -r "$WT/bin" "$DST/mike/bin"; cp -r "$WT/kb" "$DST/mike/kb"
[ -d "$WT/templates" ] && cp -r "$WT/templates" "$DST/mike/templates"
cp -r /tmp/ar2/WC/data "$DST/data"; : > "$DST/wc_env.sh"
ln -s /home/trido/thanhdt/WorkingClaude/trading_bot "$DST/trading_bot"
find "$DST" -name __pycache__ -prune -exec rm -rf {} +
echo "sandbox: $DST"
