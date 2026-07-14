#!/bin/bash
# Pha-4 DCF PLACEBO test — job Taylor_20260714_080414
# Same pinned R3 command as Pha 3's runner (data/dcf_exp_logs/runner.sh) — ONLY BASKET_DCF_MODE /
# BASKET_DCF_PLACEBO_SEED differ, so the placebo runs are comparable to ctrl/varA line-for-line.
# §8: every run carries a distinct _exp_ tag (seed folded into the filename) -> canonical R3 CSV is
# never a possible target.
cd /home/trido/thanhdt/WorkingClaude
P=/home/trido/thanhdt/wc_venv/bin/python
BASE='BQ_LOCAL_CACHE=data/bq_cache BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'
L=data/dcf_placebo_logs
mkdir -p $L data/dcf_exp_logs

run() {  # $1=label  $2=extra env
  ( eval "env $BASE $2 $P pt_v23_audit_2014.py v23a none postbull 0 edge" ) > $L/$1.log 2>&1
  echo "$1 exit=$?" >> $L/DONE_MARKS
}

# Regression guard: re-run the OFF/control config. Its CSV must come out byte-identical to Pha 3's
# ctrl CSV — proof that adding the placebo branch did not perturb the shared selection path (if it
# did, every delta-vs-control in this study would be measuring my own edit, not the placebo).
#run ctrl_rerun "EXP_TAG=dcfctrlrerun20260714" &

SEEDS="${SEEDS:-1 2 3 4}"
for s in $SEEDS; do
  run "placebo_seed$s" "BASKET_DCF_MODE=placebo_random BASKET_DCF_PLACEBO_SEED=$s" &
  while [ "$(jobs -rp | wc -l)" -ge 6 ]; do sleep 5; done
done
wait
touch $L/BATCH_DONE_$(echo $SEEDS | tr ' ' '_' | cut -c1-40)
