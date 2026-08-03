#!/bin/bash
# T1 — THANG CAPACITY (capacity-relaxation ladder). Job Taylor_20260803_021414.
#
# Muc dich: tach "edge that" khoi "hien vat mo hinh fill" bang cach DOI DO CANG cua chinh
# rang buoc capacity (liquidity_volume_pct cua so LAG), giu MOI thu khac y nguyen.
# Du doan TIEN DANG KY (pre-registered), xem research report §4:
#   H_artifact : Delta(L1-L0) PHAI teo ve ~ tac dong truc tiep (~+0.3pp CAGR) khi capacity het rang buoc
#   H_edge     : Delta giu >= ~+2pp o rung long
# Manipulation check BAT BUOC: ty le ABANDONED phai SUP o rung long, neu khong thi phep thu VO HIEU.
#
# Engine = pt_v23_lagcap_research.py (ban sao, khac production DUNG 1 dong da ghi chu — skill §14).
# Production pt_v23_audit_2014.py KHONG bao gio bi sua.
# Snapshot dong cung asof20260729_postrestate = dung vintage pin R3, threads=1, $DNA_PYEXE.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
PCT="$1"; LZB="$2"; TAG="$3"
OUT=mike/agents/Taylor/research/lag_fidelity_decomp_20260803
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
LAG_LIQ_PCT="$PCT" LIQ_ZERO_BLOCK="$LZB" LAG_ADV_BASIS=close EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_lagcap_research.py v23a none postbull 0 edge \
  > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG pct=$PCT lzb=$LZB)" >> "$OUT/$TAG.log"
