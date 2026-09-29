#!/bin/bash
# Chay selfcheck duoi 3 TZ (ICT / unset / ngoai lai) — §16 coding_guidelines.
# §8 coding_guidelines: hai instance chay song song TUNG ghi de nhau (quant-skeptic bat 2026-09-27:
# log tron giua 2 process, va check M4 doc levels_sc_*.parquet tu DIA nen co the so artifact cua
# HAI run khac nhau). Hai lop chong: (1) flock doc quyen, (2) SC_RUN = khong gian ten rieng theo PID.
WC=/home/trido/thanhdt/WorkingClaude
O=$WC/mike/agents/Taylor/research/c30v_position_replay_20260927
cd "$WC" || exit 9
PY=/home/trido/thanhdt/wc_venv/bin/python
exec 9>"$O/.selfcheck.lock"
if ! flock -n 9; then echo "ANOTHER run_selfcheck.sh dang chay — thoat de khong ghi de artifact" >&2; exit 8; fi
export SC_RUN="r$$_"
LOG="$O/selfcheck_replay.log"
{
echo "SC_RUN=$SC_RUN  (khong gian ten artifact rieng cho lan chay nay)"
for tz in "Asia/Ho_Chi_Minh" "" "America/New_York"; do
  echo "########## TZ=${tz:-UNSET} ##########"
  if [ -z "$tz" ]; then env -u TZ $PY "$O/selfcheck_replay.py"; else TZ="$tz" $PY "$O/selfcheck_replay.py"; fi
  echo "rc=$?"
done
} > "$LOG" 2>&1
echo DONE >> "$LOG"
