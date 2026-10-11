#!/bin/bash
# Quét rộng §23 (vòng 2): cùng 27 selfcheck của vòng 1, chạy trên worktree nhánh, env -u TZ.
WT=/home/trido/thanhdt/WorkingClaude/wt-fundunit-1011; OUT="$(cd "$(dirname "$0")" && pwd)"
cd "$WT" || exit 1
: > "$OUT/summary.txt"
for t in $(sed -E 's/^rc=[0-9]+ [0-9]+s //' "$OUT/../../broad_scan/summary.txt"); do
  s=$(date +%s)
  case "$t" in *.sh) env -u TZ timeout 600 bash "bin/$t" > "$OUT/$t.log" 2>&1 ;; *) env -u TZ timeout 600 python3 "bin/$t" > "$OUT/$t.log" 2>&1 ;; esac
  echo "rc=$? $(( $(date +%s) - s ))s $t" >> "$OUT/summary.txt"
done
echo DONE >> "$OUT/summary.txt"
