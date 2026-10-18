#!/usr/bin/env bash
# sunday_plan_round.sh — VÒNG PLAN CHỦ NHẬT mùa BCTC (user duyệt option 1, 2026-10-19 00:29 ICT).
#
# VÌ SAO: re-rate 8L/fa_ratings chạy MỖI NGÀY kể cả cuối tuần trong cửa sổ mùa BCTC
# (fa_ratings_earnings_window_daily.sh 17:30+18:15), nhưng chuỗi plan (bq_freshness 19:00 → DollarBill →
# 20:15-20:50 injectors → send_plan_report 21:00) chỉ chạy T2-T6 ⇒ plan thứ Hai được lập tối thứ Sáu và
# rating của BCTC công bố T7/CN không bao giờ vào plan trước phiên sáng thứ Hai. Vòng này chạy MỘT lần
# tối Chủ nhật, KHÔNG sửa chuỗi T2-T6 (chỉ đặt env opt-in MIKE_MORNING_RUN/FORCE mà bq_freshness đã có).
#
# Luồng: GATE → recover (lần trước bị kill?) → STASH plan thứ Sáu → macro_healthcheck (xem ⚠️ dưới) →
#   bq_freshness_check (morning+force) → chờ job DollarBill → 4 injector → SO SÁNH/QUYẾT ĐỊNH từng account:
#   (a) tập lệnh giống thứ Sáu → khôi phục NGUYÊN file thứ Sáu (giữ trạng thái duyệt)
#   (b) khác → giữ plan mới, gỡ dấu duyệt, gửi send_plan_report, post diff
#   (c) không sinh được / hỏng / lỗi bất kỳ → khôi phục thứ Sáu + escalate lý do thật (§29)
#
# ⚠️ CỔNG CUỐI TUẦN ĐÃ PHÁT HIỆN: get_gated_state() đòi data/macro_health.json < 1440 phút; file đó do
# daily_refresh step [11c] ghi T2-T6 ⇒ Chủ nhật 19:00 nó đã ~48h ⇒ cổng rơi DT4_only (mất macro cap) mà
# KHÔNG ai báo. Wrapper chạy lại ĐÚNG lệnh của step [11c] (macro_healthcheck.py — tự đo lại độ tươi của 4
# nguồn, KHÔNG nới ngưỡng nào) ngay trước bq_freshness. Chi tiết: kb/projects/sunday-plan-round-20261019.md
#
# Cron (đề xuất, CHƯA cài; crontab dùng UTC):
#   0 12 * * 0 /home/trido/thanhdt/WorkingClaude/mike/bin/sunday_plan_round.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/sunday_plan_round.log 2>&1
#   0 16 * * 0 .../for_each_live_account.sh .../send_plan_report.sh --second-chance >> .../send_plan_report.log 2>&1   # 23:00 ICT CN
#
# Dùng:  sunday_plan_round.sh            chạy thật (no-op im lặng nếu sai gate)
#        sunday_plan_round.sh --check [YYYY-MM-DD]   chỉ in "RUN <ngày-đích>" / "SKIP: lý do"
# Env CHỈ cho selfcheck: MIKE_NOW_ICT, SPR_* (xem khối cấu hình).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
# Neo ICT KHÔNG ĐIỀU KIỆN (§16) — mọi ngày/giờ ở đây là phiên HOSE giờ ICT.
export TZ=Asia/Ho_Chi_Minh
[ -z "${SPR_NO_ENV:-}" ] && [ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
export TZ=Asia/Ho_Chi_Minh

LIB="${SPR_LIB:-$HERE/sunday_plan_round_lib.py}"
PLAN_DIR="${SPR_PLAN_DIR:-$WC_ROOT/data/trade_plans}"
STATE_DIR="${SPR_STATE_DIR:-$ROOT/state/sunday_plan_round}"
INJ_DIR="${SPR_INJ_DIR:-$HERE}"
BQ_FRESH="${SPR_BQ_FRESHNESS:-$HERE/bq_freshness_check.sh}"
JOBS="${SPR_JOBS:-$HERE/jobs.sh}"
NOTIFY="${SPR_NOTIFY:-$HERE/notify_thread.sh}"
BUS="${SPR_BUS:-$HERE/append_event.sh}"
SEND_PLAN="${SPR_SEND_PLAN:-$HERE/send_plan_report.sh}"
MACRO_HC="${SPR_MACRO_HC:-}"                     # rỗng = chạy macro_healthcheck.py thật
FOR_EACH="${SPR_FOR_EACH:-$HERE/for_each_live_account.sh}"
FRESH_TMO="${SPR_FRESHNESS_TIMEOUT:-1800}"       # bq_freshness đo thật ~vài phút; 30' là trần
JOB_TMO="${SPR_JOB_TIMEOUT:-1500}"               # ~25' chờ DollarBill (dispatch.sh mặc định 600s/lần, retry 1)
POLL_S="${SPR_POLL_S:-30}"
INJ_TMO="${SPR_INJ_TIMEOUT:-900}"
PY="${DNA_PYEXE:-python3}"

if [ "${1:-}" = "--check" ]; then python3 "$LIB" gate ${2:+--check "$2"}; exit 0; fi

ts() { TZ=Asia/Ho_Chi_Minh date +'%F %T ICT'; }
note() { "$NOTIFY" "$1" trading_daily >/dev/null 2>&1 || true; }       # bridge tự đóng timestamp
log() { echo "[$(ts)] $*"; }

GATE="$(python3 "$LIB" gate 2>&1)"
case "$GATE" in
  RUN\ *) NTD="${GATE#RUN }" ;;
  *) log "$GATE"; exit 0 ;;
esac

if [ -n "${SPR_LABELS:-}" ]; then LABELS="$SPR_LABELS"
elif ! LABELS="$(cd "$WC_ROOT" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"; then
  log "FATAL: khong doc duoc live_dnse_labels (trading_bot.config loi) — dung"; note "🔴 Vòng plan Chủ nhật: KHÔNG đọc được danh sách account (trading_bot.config lỗi) — chưa làm gì, plan thứ Sáu giữ nguyên."; exit 1
fi
[ -z "$LABELS" ] && { log "khong co account live — khong chay gi"; exit 0; }

mkdir -p "$STATE_DIR" || exit 1
exec 9>"$STATE_DIR/.lock"
flock -n 9 || { log "dang co mot luot khac chay (lock) — thoat"; exit 0; }

# Lần trước bị kill giữa chừng (SIGKILL/mất điện) → trả plan thứ Sáu về TRƯỚC khi làm gì mới (§5).
REC="$(python3 "$LIB" recover --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" 2>&1)"
if [ -n "$REC" ]; then
  log "$REC"
  note "🟡 Vòng plan Chủ nhật: lần chạy trước bị ngắt giữa chừng — đã KHÔI PHỤC plan thứ Sáu từ stash trước khi chạy lại.
$REC"
fi

RUN_DIR="$STATE_DIR/$NTD"
[ -e "$RUN_DIR/manifest.json" ] && mv -f "$RUN_DIR/manifest.json" "$RUN_DIR/manifest.prev.$(date +%s).json"
mkdir -p "$RUN_DIR" || exit 1
START_EPOCH="$(date +%s)"

log "RUN vong plan Chu nhat -> plan dich $NTD, accounts: $LABELS"
note "🔄 Vòng plan Chủ nhật BẮT ĐẦU — plan dành cho thứ Hai $NTD ($LABELS). Có plan thứ Sáu sẽ được stash + so sánh; chỉ khác mới đổi."
python3 "$LIB" stash --plan-dir "$PLAN_DIR" --run-dir "$RUN_DIR" --ntd "$NTD" --labels "$LABELS" || { log "FATAL stash loi — dung, chua dong plan nao"; note "🔴 Vòng plan Chủ nhật: STASH lỗi — dừng, chưa động vào plan nào."; exit 1; }

declare -A STATUS DETAIL JOBID
for a in $LABELS; do STATUS[$a]="nojob"; DETAIL[$a]=""; done

# Mọi lối thoát (kể cả TERM/INT) mà còn account CHƯA quyết định → trả plan thứ Sáu từ stash (§5).
DONE_OK=0
_final_guard() {
  [ "$DONE_OK" = 1 ] && return
  local r; r="$(python3 "$LIB" recover --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" 2>&1)"
  log "THOAT BAT THUONG — $r"
  note "🔴 Vòng plan Chủ nhật bị NGẮT giữa chừng — đã khôi phục plan thứ Sáu từ stash. ${r}"
}
trap _final_guard EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

# ── 1. macro_healthcheck (cổng cuối tuần, xem ⚠️ đầu file) ──
if [ -n "$MACRO_HC" ]; then "$MACRO_HC" >"$RUN_DIR/macro_hc.log" 2>&1; hc_rc=$?
else (cd "$WC_ROOT" && timeout -k 10 300 "$PY" macro_healthcheck.py) >"$RUN_DIR/macro_hc.log" 2>&1; hc_rc=$?; fi
log "macro_healthcheck rc=$hc_rc (0 HEALTHY / 1 DEGRADED / 2 FAILED; cổng fail-closed theo file — không chặn vòng)"
[ "$hc_rc" -ge 2 ] && note "🟡 Vòng plan CN: macro_healthcheck FAILED rc=$hc_rc — cổng trạng thái sẽ rơi DT4_only (fail-closed, đúng thiết kế). Xem $RUN_DIR/macro_hc.log"

# ── 2. bq_freshness_check morning+force (KHÔNG giữ pipe tee — arch-review 10-12 tái hiện treo) ──
FRESH_LOG="$RUN_DIR/freshness.log"
MIKE_MORNING_RUN=1 MIKE_MORNING_FORCE=1 timeout -k 20 "$FRESH_TMO" "$BQ_FRESH" >"$FRESH_LOG" 2>&1
FRESH_RC=$?
log "bq_freshness_check rc=$FRESH_RC (log: $FRESH_LOG)"
FRESH_WHY="$(grep -E '^(FAIL|FATAL|=== FAILED|⛔|⚠️)|STALE' "$FRESH_LOG" | tail -3 | tr '\n' ' ' | cut -c1-400)"
[ -z "$FRESH_WHY" ] && FRESH_WHY="$(tail -n 3 "$FRESH_LOG" | tr '\n' ' ' | cut -c1-400)"
[ "$FRESH_RC" = 124 ] && FRESH_WHY="timeout ${FRESH_TMO}s: $FRESH_WHY"

if [ "$FRESH_RC" -eq 0 ]; then
  while read -r acct jid; do JOBID[$acct]="$jid"; STATUS[$acct]="pending"; done < <(python3 "$LIB" jobs "$FRESH_LOG")
  for a in $LABELS; do
    [ "${STATUS[$a]}" = "nojob" ] && DETAIL[$a]="bq_freshness chay xong rc=0 nhung KHONG dispatch DollarBill cho $a ($(grep -E "SKIP|WARN dispatch|\[WARN\] dispatch" "$FRESH_LOG" | tail -1 | cut -c1-160))"
  done
else
  for a in $LABELS; do STATUS[$a]="freshness_fail"; DETAIL[$a]="bq_freshness_check rc=$FRESH_RC: $FRESH_WHY"; done
fi

# ── 3. chờ job DollarBill (trần JOB_TMO, có huỷ job khi quá hạn để nó KHÔNG ghi đè sau khi đã khôi phục) ──
DEADLINE=$(( $(date +%s) + JOB_TMO ))
while :; do
  pend=0
  for a in $LABELS; do
    [ "${STATUS[$a]}" = "pending" ] || continue
    "$JOBS" status "${JOBID[$a]}" >"$RUN_DIR/job_${a}.status" 2>&1; rc=$?
    case "$rc" in
      0) STATUS[$a]="ok" ;;
      1|4) STATUS[$a]="job_fail"; DETAIL[$a]="DollarBill job ${JOBID[$a]} status rc=$rc: $(tail -n 2 "$RUN_DIR/job_${a}.status" | tr '\n' ' ' | cut -c1-300)" ;;
      *) pend=1 ;;
    esac
  done
  [ "$pend" = 0 ] && break
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    for a in $LABELS; do
      if [ "${STATUS[$a]}" = "pending" ]; then
        "$JOBS" cancel "${JOBID[$a]}" >"$RUN_DIR/job_${a}.cancel" 2>&1
        STATUS[$a]="job_timeout"; DETAIL[$a]="DollarBill job ${JOBID[$a]} chua xong sau ${JOB_TMO}s — da huy (jobs.sh cancel rc=$?) de khong ghi de sau khi khoi phuc"
      fi
    done
    break
  fi
  sleep "$POLL_S"
done

# ── 4. injectors đúng thứ tự cron T2-T6 (chỉ khi còn ít nhất 1 plan mới) ──
INJ_FAIL=""
any_ok=0; for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] && any_ok=1; done
if [ "$any_ok" = 1 ]; then
  for step in compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh; do
    timeout -k 20 "$INJ_TMO" "$INJ_DIR/$step" >"$RUN_DIR/inj_$step.log" 2>&1; irc=$?
    log "$step rc=$irc"
    if [ "$irc" -ne 0 ] && [ -z "$INJ_FAIL" ]; then
      INJ_FAIL="$step rc=$irc: $(tail -n 3 "$RUN_DIR/inj_$step.log" | tr '\n' ' ' | cut -c1-300)"
    fi
  done
  # plan_position_drift_check chỉ CỜ/BÁO (CN trả SKIP — không phải phiên); lỗi KHÔNG làm hỏng vòng.
  timeout -k 20 "$INJ_TMO" "$FOR_EACH" "$INJ_DIR/plan_position_drift_check.py" >"$RUN_DIR/inj_drift.log" 2>&1
  log "plan_position_drift_check rc=$? (chi co/bao)"
  if [ -n "$INJ_FAIL" ]; then
    for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] && { STATUS[$a]="inject_fail"; DETAIL[$a]="$INJ_FAIL — plan moi co the thieu phan chen (TV1/auto-exit) nen KHONG tin"; }; done
  fi
fi

# ── 5. quyết định từng account ──
RC_ALL=0; SENT=""
for a in $LABELS; do
  OUT="$(python3 "$LIB" decide --plan-dir "$PLAN_DIR" --run-dir "$RUN_DIR" --ntd "$NTD" --account "$a" --status "${STATUS[$a]}" --detail "${DETAIL[$a]}" 2>&1)"
  RES="$(printf '%s\n' "$OUT" | sed -n 's/^RESULT=//p' | head -1)"
  MSG="$(printf '%s\n' "$OUT" | grep -v '^RESULT=')"
  log "[$a] RESULT=${RES:-?}: $(printf '%s' "$MSG" | head -1)"
  case "$RES" in
    a) note "$MSG" ;;
    b) note "$MSG"; SENT="$SENT $a" ;;
    c) RC_ALL=1; note "$MSG"
       "$BUS" Taylor error "sunday-plan-round-$a-$NTD" "{\"account\":\"$a\",\"plan_date\":\"$NTD\",\"status\":\"${STATUS[$a]}\",\"restored_friday\":true,\"evidence\":\"$(printf '%s' "${DETAIL[$a]:-$MSG}" | tr '"\n' "' " | cut -c1-500)\",\"measured_by\":\"$RUN_DIR/freshness.log + job_*.status\"}" >/dev/null 2>&1 || true ;;
    *) RC_ALL=1; note "🔴 $a: vòng Chủ nhật — decide lỗi không rõ: $(printf '%s' "$OUT" | tail -n 3 | tr '\n' ' ' | cut -c1-300). Chạy: python3 $LIB recover để trả plan thứ Sáu."
       python3 "$LIB" recover --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" >/dev/null 2>&1 ;;
  esac
done

# ── 6. gửi báo cáo plan cho account (b): Chủ nhật KHÔNG có cron 21:00 → wrapper tự gọi (idempotent theo marker) ──
for a in $SENT; do
  if [ "${SPR_SEND:-1}" = "1" ]; then
    "$SEND_PLAN" --account "$a" >"$RUN_DIR/send_${a}.log" 2>&1; log "send_plan_report $a rc=$?"
  fi
done

DONE_OK=1
python3 - "$RUN_DIR/manifest.json" <<'PY' 2>/dev/null || true
import json, sys
m = json.load(open(sys.argv[1]))
if all(e["decided"] for e in m["accounts"].values()) and m["phase"] != "done":
    m["phase"] = "done"; json.dump(m, open(sys.argv[1], "w"), indent=2)
PY
note "🏁 Vòng plan Chủ nhật XONG ($NTD): $(for a in $LABELS; do printf '%s=%s ' "$a" "$(python3 -c "import json;print(json.load(open('$RUN_DIR/manifest.json'))['accounts']['$a']['decided'])" 2>/dev/null)"; done) — (a)=giữ thứ Sáu · (b)=plan mới chờ duyệt · (c)=lỗi, đã trả thứ Sáu."
exit "$RC_ALL"
