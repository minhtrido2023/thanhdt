#!/bin/bash
# T2 — THANG NAV (knob TRUC GIAO voi T1). Job Taylor_20260803_045138.
#
# Muc dich: kiem chung CHEO ket luan T1 bang mot knob DOC LAP. T1 doi do cang cua mo hinh fill
# (liquidity_volume_pct); T2 doi KICH CO SO (NAV) — cung mot huong logic: NAV nho => rang buoc
# capacity long hon (moi lenh nho hon so voi ADV) => neu H_B (hien vat capacity) dung thi Delta
# PHAI teo o NAV nho.
# Du doan TIEN DANG KY (README §4.2, cung bo tieu chi T1):
#   H_B tro i : Delta(NAV nho) <= +0.5pp
#   H_A tro i : Delta(NAV nho) >= +2.0pp
# Manipulation check BAT BUOC: abandoned% phai GIAM don dieu khi NAV giam; khong giam => VO HIEU.
#
# Engine = pt_v23_lagcap_research.py (ban sao, khac production DUNG 1 dong da ghi chu — skill §14).
# MOI THU KHAC giu y het T1: snapshot asof20260729_postrestate, LAG_LIQ_PCT=0.20 (goc),
# LAG_ADV_BASIS=close, threads=1, $DNA_PYEXE. Chi doi NAV_TOTAL_B.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
NAV="$1"; LZB="$2"; TAG="$3"
OUT=mike/agents/Taylor/research/lag_fidelity_decomp_20260803
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B="$NAV" ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
LAG_LIQ_PCT=0.20 LIQ_ZERO_BLOCK="$LZB" LAG_ADV_BASIS=close EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_lagcap_research.py v23a none postbull 0 edge \
  > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG nav=${NAV}B lzb=$LZB)" >> "$OUT/$TAG.log"
