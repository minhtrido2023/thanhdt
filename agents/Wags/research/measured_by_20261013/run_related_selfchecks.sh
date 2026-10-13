#!/usr/bin/env bash
# Chạy mọi selfcheck trong bin/ có nhắc append_event ở MỘT cây, in "<rc> <file>".
#   run_related_selfchecks.sh <repo_root>
root="$1"; cd "$root" || exit 2
grep -rlE 'append_event(\.sh|_selfcheck)' bin | grep -iE 'selfcheck' | grep -vE 'selfcheck_baseline_diff|selfcheck_weekly_baseline_check' | sort | while read -r f; do
  case "$f" in *.py) cmd=(python3 "$f") ;; *) cmd=(bash "$f") ;; esac
  env -u TZ -u JOB_ID timeout 300 "${cmd[@]}" >/dev/null 2>&1 </dev/null; echo "$? $f"
done
