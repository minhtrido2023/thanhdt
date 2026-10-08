#!/bin/bash
# Luật so 1 trục (bin/pin_ledger.py compare) trên kho SANDBOX — KHÔNG đụng data/pinned_ledgers thật.
# job Taylor_20261008_172556. Lệnh khai cho mỗi ledger = env khác nhau của chân (legs.txt) + env chung
# của run_leg.sh (giống hệt mọi chân ⇒ không sinh trục). Xuất logs/compare_<cv>.txt.
set -u
H=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/rerun_groupB_fixed_20261009
PL=/home/trido/thanhdt/WorkingClaude/mike/bin/pin_ledger.py
SB=$(mktemp -d /tmp/n4_pinstore.XXXX); mkdir -p "$SB/data/pinned_ledgers"
export PIN_STORE_WC_ROOT="$SB"
COMMON="BASKET_CA_SNAPSHOT=corp_action_share_20260927 BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19"
ledger() { grep -- "-> " "$H/logs/$1.log" | grep "rows)" | sed 's/.*-> \(.*\)  (.*/\1/'; }
declare -A M
for cv in off 1m; do
  t=dep1m; [ "$cv" = off ] && t=off
  { echo "n4_c70_$cv BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 IDLE_CARRY_TIER=$t"
    grep "_$cv " "$H/legs.txt"; } | while read -r tag rest; do
    f=$(ledger "$tag")
    python3 "$PL" add "$f" --label "$tag" --command "$rest $COMMON" --audit-end 2026-06-19 \
      --no-control "sandbox n4 — chỉ để chạy compare, không phải pin" >/dev/null || echo "ADD FAIL $tag"
  done
done
md5of() { md5sum "$(ledger "$1")" | cut -d' ' -f1; }
for cv in off 1m; do
  {
  for pair in c70:q8 q8:q12 c70:qf8 q8:qf8 c70:secA secA:secB secB:secBx c70:eyonly eyonly:fc30 fc30:fc45 fc45:fc55 c70:l1a l1a:l1b; do
    a=${pair%%:*}; b=${pair##*:}
    echo "################ $a → $b ($cv)"
    python3 "$PL" compare "$(md5of n4_${a}_$cv)" "$(md5of n4_${b}_$cv)"; echo "rc=$?"
  done
  } > "$H/logs/compare_$cv.txt" 2>&1
done
# trục quy ước tiền nhàn rỗi: off → 1m cho từng chân
{ for l in c70 q8 q12 qf8 secA secB secBx eyonly fc30 fc45 fc55 l1a l1b; do
    echo "################ $l off → 1m"; python3 "$PL" compare "$(md5of n4_${l}_off)" "$(md5of n4_${l}_1m)"; echo "rc=$?"
  done; } > "$H/logs/compare_idle.txt" 2>&1
grep -h "rc=" "$H"/logs/compare_*.txt | sort | uniq -c
echo "sandbox=$SB"
