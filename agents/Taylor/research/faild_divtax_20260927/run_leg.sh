#!/bin/bash
# FAIL-D dividend-tax haircut — A/B MỘT BIẾN trên anchor R3 hiện hành (park 0,30, ledger md5 4707bcbe).
# Env copy NGUYÊN VĂN từ research/repin_park030_20260927/run_pin.sh (lệnh pin canonical);
# **đổi đúng 1 biến**: PARK_DIV_TAX_DRAG_ANNUAL (mặc định "" = 0 ⇒ chân CONTROL phải BYTE-IDENTICAL).
# Engine = BẢN VÁ trong worktree outer-repo (knob env-gated), data/ vẫn là cây MAIN (engine
# os.chdir(WORKDIR) hardcode) ⇒ cùng vintage dữ liệu với pin.
# $1 = EXP_TAG ; rest = extra env assignments (vd PARK_DIV_TAX_DRAG_ANNUAL=0.00141852)
WC=/home/trido/thanhdt/WorkingClaude
ENGINE=$WC/mike/agents/Taylor/wt-divtax-2709/WorkingClaude/pt_v23_audit_2014.py
OUT=$WC/mike/agents/Taylor/wt-divtax-art-2709/agents/Taylor/research/faild_divtax_20260927
TAG="$1"; shift
cd "$WC" || exit 9
export WORKDIR_8L="$WC"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
env "$@" \
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.3" AUDIT_END=2026-06-19 EXP_TAG="$TAG" \
$DNA_PYEXE "$ENGINE" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
