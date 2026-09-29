#!/usr/bin/env bash
# VIEC 2 — bang chung 2 CHIEU: chay tung selfcheck ung vien, so trang thai cay THAT truoc/sau.
# Moi nguon ghi ra FILE RIENG roi noi lai (viet chung 1 pipe lam output cua md5sum va find
# xen vao nhau -> diff nhieu gia; da bi dung 2 lan truoc khi sua).
set -uo pipefail
export LC_ALL=C
cd /home/trido/thanhdt/WorkingClaude
PY=/home/trido/thanhdt/wc_venv/bin/python
OUT=mike/agents/Taylor/research/selfcheck_write_scan_20260927
mkdir -p "$OUT/probe_logs"
snap() {   # $1 = file dich
  local t; t=$(mktemp -d)
  find data/trade_plans data/execution_logs data/discretionary data/state mike/bin mike/kb \
       -type f -print0 2>/dev/null | sort -z | xargs -0 -r md5sum > "$t/a" 2>/dev/null
  find data -maxdepth 1 -type f -printf '%p %s %T@\n' 2>/dev/null | sort > "$t/b"
  find . -maxdepth 1 -type f -printf '%p %s %T@\n' 2>/dev/null | sort > "$t/c"
  sort "$t/a" > "$1"; cat "$t/b" "$t/c" >> "$1"
  rm -rf "$t"
}
for s in "$@"; do
  snap "$OUT/probe_logs/_pre.txt"
  timeout 900 $PY "$s" > "$OUT/probe_logs/$(basename $s .py).log" 2>&1; rc=$?
  snap "$OUT/probe_logs/_post.txt"
  if diff -q "$OUT/probe_logs/_pre.txt" "$OUT/probe_logs/_post.txt" >/dev/null; then
    echo "CLEAN  rc=$rc  $s"
  else
    echo "DIRTY  rc=$rc  $s"
    diff "$OUT/probe_logs/_pre.txt" "$OUT/probe_logs/_post.txt" | grep -E '^[<>]' | head -14 | sed 's/^/      /'
  fi
done
