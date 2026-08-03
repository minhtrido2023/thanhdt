#!/bin/bash
# BUOC D — xac nhan tang ENGINE THAT cho margin trong washout CAPIT.
# job Taylor_20260803_101341 · RESEARCH-ONLY (production pt_v23_audit_2014.py + simulate_holistic_nav.py
# KHONG bi sua; ca hai deu la BAN SAO nghien cuu trong thu muc nay).
#
# Engine  = p5_engine/engine_lever.py = p3/engine_park.py + hunk THEM `CAPIT_LEVER_FORCE`
# Sim     = p5_engine/shn_lever.py    = simulate_holistic_nav.py + hunk THEM forced-borrow ledger
# Ca hai inert khi CAPIT_LEVER_FORCE<=1 => chan control PHAI tai lap dung pin R3.
#
# Vi sao can knob moi (p2 §1.3): voi MGE/FORCE_REAL_LEVER, engine tai tro phan tang them bang tien
# mat/parking nhan roi => chi 5-9% la vay THAT, gross chua bao gio vuot 1,000 => cau hoi don bay
# CHUA TUNG duoc do. `CAPIT_LEVER_FORCE=f` khai bao phan tang them la NO THEO DINH NGHIA: shn_lever
# tinh lai vay tren (f-1)/f cost-basis cua ro CAPIT MOI PHIEN giu, bat ke con tien mat hay khong.
#
# Lenh pin R3 nguyen van (results_registry.md muc 2026-08-03) + snapshot asof20260729_postrestate
# + BQ_CACHE_THREADS=1 + $DNA_PYEXE (pandas 3). MGE=f chi de MO TRAN GROSS cho engine mua duoc
# (khong cong them lop don bay thu hai — da chan bang `and CAPIT_LEVER_FORCE <= 1.0` trong engine).
# EXP_TAG bat buoc de KHONG de canonical CSV (coding_guidelines §8).
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
TAG="$1"; shift
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p5_engine
env "$@" \
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 CAPIT_SIZE_DIAG=1 EXP_TAG="$TAG" \
PYTHONPATH="$OUT" \
$DNA_PYEXE "$OUT/engine_lever.py" v23a none postbull 0 edge > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG $*)" >> "$OUT/$TAG.log"
