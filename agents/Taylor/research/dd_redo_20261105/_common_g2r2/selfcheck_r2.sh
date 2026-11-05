#!/usr/bin/env bash
# Tự kiểm vòng 2 (job Taylor_20261105_020018): chạy mỗi model r2 HAI lần, so md5 out.json/out.txt/LOCK (điều 12).
set -euo pipefail
B="$(cd "$(dirname "$0")/.." && pwd)"; PY="${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}"
for T in SIP SCL TV1 TV2; do
  t=$(echo "$T" | tr 'A-Z' 'a-z'); C="$B/$T/calc"
  (cd "$C" && "$PY" -I "model_${t}_r2.py" >/dev/null)
  a=$(md5sum "$C/model_${t}_r2_out.json" "$C/model_${t}_r2_out.txt" "$C/LOCK_r2_md5.txt" | awk '{print $1}' | tr '\n' ' ')
  (cd /tmp && env -u TZ "$PY" -I "$C/model_${t}_r2.py" >/dev/null)
  b=$(md5sum "$C/model_${t}_r2_out.json" "$C/model_${t}_r2_out.txt" "$C/LOCK_r2_md5.txt" | awk '{print $1}' | tr '\n' ' ')
  [ "$a" = "$b" ] && echo "$T r2 reproducible OK ($a)" || { echo "$T MISMATCH $a vs $b"; exit 1; }
done
