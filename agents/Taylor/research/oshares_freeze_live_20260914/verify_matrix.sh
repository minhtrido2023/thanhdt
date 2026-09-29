#!/usr/bin/env bash
# Ma trận verify trong WORKTREE (không source wc_env.sh). BQBLOCK=1 ⇒ CLOUDSDK_CONFIG giả ⇒ bq CLI lỗi auth.
set -u
WT=/home/trido/thanhdt-wt-oshares-freeze-live/WorkingClaude
PY=/home/trido/thanhdt/wc_venv/bin/python
R=$(cd "$(dirname "$0")" && pwd)
MIKE=/home/trido/thanhdt/WorkingClaude/mike
run() {  # $1=label ; rest = command
  local label=$1; shift
  local out; out=$("$@" 2>&1); local rc=$?
  local last; last=$(printf '%s\n' "$out" | grep -E "PASS [0-9]+/[0-9]+|selfcheck PASS|FAILED|\"ok\": (true|false)|CRASH|Error" | tail -1)
  printf '%-58s rc=%s  %s\n' "$label" "$rc" "${last:0:150}"
}
for tzmode in unset America/New_York; do
  for blk in 0 1; do
    envs=(env)
    [ "$tzmode" = unset ] && envs+=(-u TZ) || envs+=(TZ=$tzmode)
    [ "$blk" = 1 ] && envs+=(CLOUDSDK_CONFIG=/tmp/no_gcloud_cfg_x)
    tag="TZ=$tzmode BQBLOCK=$blk"
    run "$tag oshares_live"   "${envs[@]}" OSH_WT=$WT $PY $R/run_with_wt.py $WT/oshares_live.py --selfcheck
    run "$tag oshares_pit"    "${envs[@]}" OSH_WT=$WT $PY $R/run_with_wt.py $WT/oshares_pit.py
    run "$tag corp_action_lib" "${envs[@]}" OSH_WT=$WT $PY $R/run_with_wt.py $WT/corp_action_lib.py --selfcheck
    run "$tag oshares_wire"   "${envs[@]}" OSH_WT=$WT $PY $R/run_with_wt.py $WT/oshares_wire_selfcheck.py
    run "$tag corp_action_daily_selfcheck" "${envs[@]}" WORKDIR_8L=$WT $PY $MIKE/bin/corp_action_daily_selfcheck.py
    run "$tag GATE gate_driver_wt (gate_selfcheck thật)" "${envs[@]}" OSH_WT=$WT $PY $R/gate_driver_wt.py
  done
done
