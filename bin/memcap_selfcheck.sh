#!/usr/bin/env bash
# selfcheck memcap.sh: (1) vượt trần ⇒ bị giết, (2) dưới trần ⇒ chạy bình thường, (3) tham số sai ⇒ exit 2, (4) mem_slots ≥1.
set -u
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; fail=0
ok(){ echo "PASS $1"; }; ko(){ echo "FAIL $1"; fail=1; }
HOG='b=[];[b.append(bytearray(1<<20)) for _ in range(3000)]'
"$D/memcap.sh" 1 python3 -c "$HOG" >/dev/null 2>&1; rc=$?
[ "$rc" -ne 0 ] && ok "vuot tran 1G bi giet (rc=$rc)" || ko "vuot tran khong bi giet"
"$D/memcap.sh" 1 python3 -c "b=bytearray(50<<20);print('ok')" 2>/dev/null | grep -q ok && ok "duoi tran chay duoc" || ko "duoi tran khong chay"
"$D/memcap.sh" abc true >/dev/null 2>&1; [ "$?" -eq 2 ] && ok "tham so sai exit 2" || ko "tham so sai"
s="$("$D/mem_slots.sh" 3.5)"; [ "${s:-0}" -ge 1 ] && ok "mem_slots=$s" || ko "mem_slots"
exit "$fail"
