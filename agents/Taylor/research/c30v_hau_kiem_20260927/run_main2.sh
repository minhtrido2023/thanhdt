#!/bin/bash
# Pin R3 reproduction ON MAIN CANONICAL after merge a808a613.
# Verbatim pinned env from research/c30v_retleg_repin_20260927/run_leg.sh, except:
#  - tree = CANONICAL /home/trido/thanhdt/WorkingClaude (fix is merged; pt_v23_audit_2014.py's
#    hardcoded WORKDIR now points at the FIXED custom_basket.py, so NO wrapper is needed)
#  - EXP_TAG is non-canonical per coding_guidelines §8 (never write onto a pinned filename)
# $1 = EXP_TAG ; rest = extra env assignments
WT=/home/trido/thanhdt/WorkingClaude
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_hau_kiem_20260927
TAG="$1"; shift
cd "$WT" || exit 9
export WORKDIR_8L="$WT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
AUDIT_END=2026-06-19 EXP_TAG="$TAG" "$@" \
$DNA_PYEXE "$WT/pt_v23_audit_2014.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
# run_main2.sh vs run_main.sh: the pinned block in run_main.sh ends with PARK_STATES="3:0.7",
# which OVERRIDES anything passed in "$@" (later assignment wins in `env`). That made the first
# no-park attempt a SILENT no-op (log line "parking policy {3: 0.7}", output byte-identical to
# c30vmain). Here "$@" comes LAST so an override actually takes effect; PARK_STATES must then be
# supplied by the caller (pass PARK_STATES=3:0.7 to reproduce the pin).
