#!/bin/bash
# Chay TIEP 2 chan TZ con lai vao CUNG file log (chan ICT + unset da PASS o tren).
# Vi sao can file rieng: parent cua lan chay truoc bi `pkill -f run_selfcheck.sh` cua chinh Taylor
# giet (pattern khop luon command line cua no) — chan TZ#2 van PASS vi python con song sot, nhung
# dong rc= va chan TZ#3 khong bao gio duoc ghi. Ghi ro trong log thay vi va lai im lang.
WC=/home/trido/thanhdt/WorkingClaude
O=$WC/mike/agents/Taylor/research/c30v_position_replay_20260927
cd "$WC" || exit 9
PY=/home/trido/thanhdt/wc_venv/bin/python
exec 9>"$O/.selfcheck.lock"
flock -n 9 || { echo "run khac dang giu lock" >&2; exit 8; }
export SC_RUN="f$$_"
{
echo ""
echo "########## (chay tiep, SC_RUN=$SC_RUN) — parent cua lan truoc bi pkill giet sau khi TZ=UNSET da PASS;"
echo "########## chay lai TZ=UNSET de co dong rc= day du, roi TZ=America/New_York."
for tz in "" "America/New_York"; do
  echo "########## TZ=${tz:-UNSET} ##########"
  if [ -z "$tz" ]; then env -u TZ $PY "$O/selfcheck_replay.py"; else TZ="$tz" $PY "$O/selfcheck_replay.py"; fi
  echo "rc=$?"
done
echo DONE
} >> "$O/selfcheck_replay.log" 2>&1
