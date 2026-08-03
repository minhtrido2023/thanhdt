#!/bin/bash
# T1-price — THANG CAPACITY chay lai o LAG_ADV_BASIS=price. Job Taylor_20260803_052705.
#
# Vi sao chay lai: toan bo T1/T2/T3 (job Taylor_20260803_021414 / _045138) chay o
# LAG_ADV_BASIS=close nen chan doi chung la 27,24%. Pin CHINH THUC tu 2026-08-03 la
# 28,86% (co so price = mac dinh production tu commit 0062aa0). Ket luan ve HUONG khong
# phu thuoc co so gia, nhung SO TUYET DOI thi co => ghep lai thang cho dung co so pin.
#
# DIEU KIEN HOP LE (dang ky truoc): rung pct=0.20 / L0 PHAI tai lap DUNG
#   Final NAV 1,178.01B  CAGR 28.86%  Sharpe 1.90  MaxDD -17.8%  Calmar 1.62
# (= L2_advprice cua A/B 08-02, engine production). Khong tai lap => toan bo thang VO HIEU.
#
# Engine = pt_v23_lagcap_research.py (ban sao, khac production DUNG 1 dong da ghi chu — skill §14).
# Moi thu khac giu Y HET T1: snapshot asof20260729_postrestate, NAV 50B, threads=1, $DNA_PYEXE.
# CHI doi LAG_ADV_BASIS: close -> price.
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
PCT="$1"; LZB="$2"; TAG="$3"
OUT=mike/agents/Taylor/research/lag_fidelity_decomp_20260803
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 \
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo \
PARK_STATES="3:0.7" AUDIT_END=2026-06-19 \
LAG_LIQ_PCT="$PCT" LIQ_ZERO_BLOCK="$LZB" LAG_ADV_BASIS=price EXP_TAG="$TAG" \
$DNA_PYEXE pt_v23_lagcap_research.py v23a none postbull 0 edge \
  > "$OUT/$TAG.log" 2>&1
echo "EXIT=$? ($TAG pct=$PCT lzb=$LZB adv=price)" >> "$OUT/$TAG.log"
