#!/usr/bin/env bash
# ai_momentum_cron.sh — wrapper cron cho ai_momentum_daily.py (P1; KHONG tu cai cron — Mike/user cai sau khi duyet).
# Du kien chay lai nhieu moc trong toi (20:00 / 21:30 / 23:00 ICT): idempotent theo event_id, im lang tru khi bat thuong.
#   flock -n (chong 2 luot dong thoi, ke ca chay tay) + timeout tong; ngay hom nay = ICT.
# Exit cua python: 0 ok | 3 khong phai ngay giao dich | 4 BQ chua ve/chua day | 5 loi ha tang M1 (chay lai duoc) |
#                  6 co luot khac dang chay | 1 loi that. Wrapper: rc 3/6 KHONG alert (rc 6 = trung chay tay); rc 4 KHONG alert TRU luot bat dau o moc cuoi (gio ICT >= 23).
# Alert (Discord topic momentum_lab (Momentum Lab)) khi: rc ngoai {0,3,4,6}, hoac rc=4 o moc cuoi 23:00 ICT, hoac timeout tong, hoac M1 FAIL>0, hoac M2 FAIL >=3 dong live lien tiep (CHI khi doi trang thai OK->FAIL, khong lap moi luot).
# Bien test: AI_MOMENTUM_{PY,SCRIPT,LEDGER_DIR,LOCK,LOGDIR,TOTAL_TIMEOUT,NOTIFY,TODAY,HOUR,FINAL_HOUR}.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ=Asia/Ho_Chi_Minh
PY="${AI_MOMENTUM_PY:-python3}"
SCRIPT="${AI_MOMENTUM_SCRIPT:-$ROOT/agents/Taylor/research/ai_momentum_20261115/ai_momentum_daily.py}"
LEDGER_DIR="${AI_MOMENTUM_LEDGER_DIR:-$ROOT/data/ai_momentum}"
LOCK="${AI_MOMENTUM_LOCK:-$ROOT/state/ai_momentum_cron.lock}"
LOGDIR="${AI_MOMENTUM_LOGDIR:-$ROOT/logs/ai_momentum}"
TOTAL_TIMEOUT="${AI_MOMENTUM_TOTAL_TIMEOUT:-5400}"      # 90 phut
NOTIFY="${AI_MOMENTUM_NOTIFY:-$ROOT/bin/notify_thread.sh}"
TOPIC=momentum_lab                                       # ten trong kb/discord_channels.json (Momentum Lab)
TODAY="${AI_MOMENTUM_TODAY:-$(date +%F)}"
START_HOUR="${AI_MOMENTUM_HOUR:-$(date +%H)}"            # gio ICT luc BAT DAU luot (TZ da neo o tren) — khong doi khi luot chay qua nua dem
FINAL_HOUR="${AI_MOMENTUM_FINAL_HOUR:-23}"               # moc cuoi trong toi (23:00 ICT): rc=4 o day = mat ngay, khong con luot sau
mkdir -p "$(dirname "$LOCK")" "$LOGDIR" || exit 1
exec 9>"$LOCK"
if ! flock -n 9; then echo "$(date -Is) ai_momentum_cron: luot khac dang chay (khoa $LOCK) — bo qua" >> "$LOGDIR/cron.log"; exit 0; fi

OUT="$LOGDIR/run_${TODAY}_$(date +%H%M%S).out"; ERR="${OUT%.out}.err"
timeout --kill-after=30 "$TOTAL_TIMEOUT" "$PY" "$SCRIPT" --date "$TODAY" --ledger-dir "$LEDGER_DIR" >"$OUT" 2>"$ERR"
rc=$?
echo "$(date -Is) ai_momentum_cron T=$TODAY rc=$rc out=$OUT" >> "$LOGDIR/cron.log"

alert() { "$NOTIFY" "$1" "$TOPIC" >/dev/null 2>&1 || echo "$(date -Is) NOTIFY FAIL: $1" >> "$LOGDIR/cron.log"; }
_tail() { tail -n 6 "$ERR" 2>/dev/null | cut -c1-300; }

case "$rc" in
  4) if [ "$((10#$START_HOUR))" -ge "$((10#$FINAL_HOUR))" ]; then   # moc cuoi ma BQ van chua day => khong con luot sau, ngay T mat im lang
       alert "ai_momentum T=$TODAY: MOC CUOI ${FINAL_HOUR}:00 ICT van rc=4 (BQ chua ve/chua day) — ngay T KHONG co su kien nao duoc ghi; chay tay --date $TODAY khi BQ day. stderr cuoi: $(_tail)"
     fi
     exit 0 ;;
  3|6) exit 0 ;;                         # khong phai ngay GD / trung luot: im lang
  124|137) alert "ai_momentum T=$TODAY: QUA TRAN TONG ${TOTAL_TIMEOUT}s (rc=$rc) — luot sau chay lai idempotent. stderr cuoi: $(_tail)"; exit "$rc" ;;
  0) ;;
  *) alert "ai_momentum T=$TODAY: rc=$rc (5=ha tang M1, 1=loi that/ledger). stderr cuoi: $(_tail) | stdout: $(tr '\n' ' ' < "$OUT" | cut -c1-400)"; exit "$rc" ;;
esac
# rc=0: doc tom tat JSON; alert neu M1 FAIL>0; M2 FAIL lien tiep >=3 chi alert khi DOI TRANG THAI (khong lap moi luot: trang thai nho o $M2_STATE)
M2_STATE="$LOGDIR/m2_alert.state"
sum="$("$PY" - "$OUT" <<'PY'
import json, sys
try: o = json.load(open(sys.argv[1]))
except Exception as e: print(f"stdout khong phai JSON ({type(e).__name__}) — kiem tra {sys.argv[1]}"); print("STREAK=-1"); sys.exit(0)
print(f"M1 FAIL={o['m1_fail']} (su kien: {o.get('written')})" if o.get("m1_fail", 0) > 0 else "")
print(f"STREAK={int(o.get('m2_fail_streak', 0))}")
PY
)"
msg="$(printf '%s\n' "$sum" | sed -n 1p)"; streak="$(printf '%s\n' "$sum" | sed -n 's/^STREAK=//p' | tail -1)"; streak="${streak:--1}"
[ -n "$msg" ] && alert "ai_momentum T=$TODAY: $msg"
if [ "$streak" -ge 3 ]; then
  if [ "$(cat "$M2_STATE" 2>/dev/null)" != "FAIL" ]; then alert "ai_momentum T=$TODAY: M2 FAIL lien tiep=$streak (bao 1 lan khi doi trang thai; se bao lai khi M2 hoi phuc roi hong tiep)"; echo FAIL > "$M2_STATE"; fi
elif [ "$streak" -ge 0 ]; then echo OK > "$M2_STATE"; fi
exit 0
