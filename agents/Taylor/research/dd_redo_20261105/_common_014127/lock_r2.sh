#!/usr/bin/env bash
# VONG 2: khoa md5 model_r2_out.json + MOI file upstream (code thuc thi + du lieu doc) TRUOC khi compare_r2 doc gia/ADV.
# Dung: lock_r2.sh <TK> [file upstream rieng cua ma ...]   (duong dan tuong doi tu <TK>/calc)
set -euo pipefail
tk="$1"; shift
here="$(cd "$(dirname "$0")" && pwd)"; calc="$here/../$tk/calc"; wc=/home/trido/thanhdt/WorkingClaude
cd "$calc"
{
  md5sum model_r2_out.json | awk -v p="$PWD/model_r2_out.json" '{print $1, p}'
  for f in model_r2.py "$here/common.py" "$here/common_r2.py" "$here/compare_r2.py" "$here/bq_px_liq_20261104.csv" "$here/../_shared/wpct.py" \
           "$wc/deposit_rate_vn.py" "$wc/data/deposit_rate_vn_events.csv" "$@"; do
    p="$(readlink -f "$f")"; md5sum "$p" | awk '{print $1, $2}'
  done
} | sed "s# $wc/# #" > LOCK_r2_md5.txt
cat LOCK_r2_md5.txt
