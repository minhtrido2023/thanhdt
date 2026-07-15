#!/bin/bash
# Pha-5 DCF PLACEBO-PE test — job Taylor_20260715_041608
# Same pinned R3 command as Pha 3/4 runners — ONLY BASKET_DCF_MODE differs, so the placebo_pe run
# is comparable to ctrl/varA/placebo_random line-for-line.
# §8: every run carries a distinct _exp_ tag -> canonical R3 CSV is never a possible target.
cd /home/trido/thanhdt/WorkingClaude
P=/home/trido/thanhdt/wc_venv/bin/python
# BQ_LOCAL_CACHE points at the experiment-local PIN (symlinks to data/bq_cache + verified:true
# manifest) — the shared manifest is verified:false since the 07-14 upstream ticker_financial
# incident, which makes a bare data/bq_cache fall back to REAL BQ (whose ticker_financial is the
# CORRUPTED table). The varA byte-identical guard below adjudicates that the pin == the 07-14 data.
BASE='BQ_LOCAL_CACHE=mike/agents/Taylor/dcf_exp/bq_cache_pin20260715 BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 AUDIT_END=2026-06-19'
L=data/dcf_placebo_logs

run() {  # $1=label  $2=extra env
  ( eval "env $BASE $2 $P pt_v23_audit_2014.py v23a none postbull 0 edge" ) > $L/$1.log 2>&1
  echo "$1 exit=$?" >> $L/DONE_MARKS
}

# Regression guard #1: re-run variant A (exclude_rich) under the placebo_pe patch. Its NAV series
# must be identical to the pinned _exp_dcfexrich.csv from 2026-07-14 — proving BOTH that the patch
# left the exclude_rich path untouched AND that the local cache data is still byte-comparable to
# the 07-14 baseline runs (ticker_financial cache = GOOD pre-corruption snapshot, verified).
run varA_rerun_pe_guard "BASKET_DCF_MODE=exclude_rich EXP_TAG=dcfexrichrerun20260715" &

# The test arm: drop n_d highest-PE names per rebal date (n_d measured off the same dcf_at calls).
run placebo_pe "BASKET_DCF_MODE=placebo_pe EXP_TAG=dcfplacebope20260715" &

wait
touch $L/BATCH_PE_DONE
