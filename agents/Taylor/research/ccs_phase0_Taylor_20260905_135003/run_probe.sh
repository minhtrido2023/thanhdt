#!/bin/bash
# CCS Phase 0 — probe run. Engine = COPY of production pt_v23_audit_2014.py + 2 env-gated dump blocks
# (CCS_DUMP_DIR). Command = pinned R3 command verbatim (run_repin.sh 2026-08-03) + same frozen snapshot.
# EXP_TAG=ccsp0 keeps output off every canonical/pinned path (coding_guidelines §8).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
D=mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003
PYTHONPATH=/home/trido/thanhdt/WorkingClaude \
CCS_DUMP_DIR=/home/trido/thanhdt/WorkingClaude/$D/dump \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 EXP_TAG=ccsp0 \
$DNA_PYEXE $D/ccs_probe_engine.py v23a none postbull 0 edge > "$D/probe.log" 2>&1
echo "EXIT=$?" >> "$D/probe.log"
