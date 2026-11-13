#!/bin/bash
# A6 Việc 1 (§23 quét rộng): mọi *selfcheck*.py nhắc simulate_holistic_nav|pt_v23_audit_2014|idle_rate_proxy,
# chạy trong sandbox <sb> (cây code + data symlink), 3 TZ: ICT, env -u TZ, America/New_York. Usage: selfchecks.sh <sb> <out>
SB=$1; OUT=$2; PY=/home/trido/thanhdt/wc_venv/bin/python; cd "$SB" || exit 9; : > "$OUT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh PT_WORKDIR="$SB" WORKDIR_8L=/home/trido/thanhdt/WorkingClaude
for f in $(grep -lE 'simulate_holistic_nav|pt_v23_audit_2014|idle_rate_proxy' *selfcheck*.py | sort); do
  for tz in Asia/Ho_Chi_Minh UNSET America/New_York; do
    S=$(date +%s)
    if [ $tz = UNSET ]; then env -u TZ timeout 600 $PY "$f" > /tmp/a6sc.$$ 2>&1; else TZ=$tz timeout 600 $PY "$f" > /tmp/a6sc.$$ 2>&1; fi
    rc=$?; echo "$f tz=$tz rc=$rc wall=$(( $(date +%s)-S ))s last=$(tail -1 /tmp/a6sc.$$ | cut -c1-140)" >> "$OUT"
  done
done; rm -f /tmp/a6sc.$$; echo DONE >> "$OUT"
