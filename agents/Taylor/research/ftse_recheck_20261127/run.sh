#!/usr/bin/env bash
# usage: run.sh   -> control (cut 2026-10-12) + now (cut 2026-11-26)
set -u
source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null
H=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/ftse_recheck_20261127
PY=/home/trido/thanhdt/wc_venv/bin/python
for p in control:2026-10-12 now:2026-11-26; do
  d=${p%:*}; mkdir -p "$H/$d"; cd "$H/$d" || exit 1
  END=${p#*:} $PY ../pull.py >out_pull.txt 2>&1 && $PY ../measure.py >out_measure.txt 2>&1 && $PY ../measure_fgn27.py >out_fgn27.txt 2>&1
  echo "$d rc=$?"; tail -n 3 out_pull.txt; tail -n 3 out_measure.txt; head -n 2 out_fgn27.txt
done
