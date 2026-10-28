#!/usr/bin/env bash
# sunday_plan_round.sh — VÒNG PLAN CHỦ NHẬT mùa BCTC (user duyệt option 1, 2026-10-19 00:29 ICT).
#
# VÌ SAO: re-rate 8L/fa_ratings chạy MỖI NGÀY kể cả cuối tuần trong cửa sổ mùa BCTC
# (fa_ratings_earnings_window_daily.sh 17:30+18:15), nhưng chuỗi plan (bq_freshness 19:00 → DollarBill →
# 20:15-20:50 injectors → send_plan_report 21:00) chỉ chạy T2-T6 ⇒ plan thứ Hai được lập tối thứ Sáu và
# rating của BCTC công bố T7/CN không bao giờ vào plan trước phiên sáng thứ Hai. Vòng này chạy MỘT lần
# tối Chủ nhật, KHÔNG sửa hành vi chuỗi T2-T6 (chỉ đặt env opt-in MIKE_MORNING_RUN/FORCE/NOTE_TAIL mà bq_freshness có).
#
# Luồng: recover (lần trước bị kill?) → GATE → STASH plan thứ Sáu → macro_healthcheck (xem ⚠️ dưới) →
#   bq_freshness_check (morning+force) → chờ job DollarBill → XÁC MINH job đã dừng → 3 injector + drift →
#   SO SÁNH/QUYẾT ĐỊNH từng account (so theo phần executor dùng, qua load_plan/PlannedOrder):
#   (a) tập lệnh giống thứ Sáu → khôi phục NGUYÊN file thứ Sáu (trạng thái duyệt in ra từ file thật)
#   (b) khác → giữ plan mới, gỡ dấu duyệt, gửi send_plan_report, post diff
#   (c) không sinh được / hỏng / lỗi / còn dấu hiệu job ghi muộn / thứ Sáu có đề xuất park → khôi phục thứ Sáu + escalate lý do thật (§29)
#
# ⚠️ KHÔNG CHẠY chuỗi park (park_trim 19:30 → jit_unpark 19:40 → merge_park 20:20 — cả ba tự bỏ qua cuối tuần,
# park_trim_daily.sh:37 / merge_park_daily.sh:43) ⇒ plan CN thiếu lệnh bán park mà plan thứ Sáu đã có. Wrapper chạy lại
# đúng 3 injector (compute_active_nav_all 20:15 → inject_discretionary 20:30 → auto_exit_inject 20:40) + drift check 20:50
# như T2-T6, nhưng KHÔNG chạy park: artifact park thứ Sáu có đề xuất qty>0 (hoặc vắng/hỏng) ⇒ ép (c) giữ plan thứ Sáu.
#
# ⚠️ CỔNG CUỐI TUẦN ĐÃ PHÁT HIỆN: get_gated_state() đòi data/macro_health.json < 1440 phút; file đó do
# daily_refresh step [11c] ghi T2-T6 ⇒ Chủ nhật 19:00 nó đã ~48h ⇒ cổng rơi DT4_only (mất macro cap) mà
# KHÔNG ai báo. Wrapper chạy lại ĐÚNG lệnh của step [11c] (macro_healthcheck.py — tự đo lại độ tươi của 4
# nguồn, KHÔNG nới ngưỡng nào) ngay trước bq_freshness. Chi tiết: kb/projects/sunday-plan-round-20261019.md
#
# Chốt chặn cuối đêm: job DollarBill ghi muộn / người ghi plan sau quyết định → `--verify` so NỘI DUNG plan với manifest;
# lệch ⇒ gỡ dấu duyệt + escalate (chạy 23:00 CN trong `--second-chance` và 08:30 T2).
#
# Cron (đề xuất, CHƯA cài; crontab dùng UTC):
#   0 12 * * 0  .../bin/sunday_plan_round.sh >> .../logs/sunday_plan_round.log 2>&1                   # 19:00 ICT CN
#   0 16 * * 0  .../bin/sunday_plan_round.sh --second-chance >> .../logs/sunday_plan_round.log 2>&1   # 23:00 ICT CN: --verify rồi (nếu trong cửa sổ BCTC) send_plan_report --second-chance
#   30 1 * * 1  .../bin/sunday_plan_round.sh --verify >> .../logs/sunday_plan_round.log 2>&1          # 08:30 ICT T2: kiểm cuối trước 08:45 (no-op nếu không có manifest)
#
# Dùng:  sunday_plan_round.sh                     chạy thật (no-op im lặng nếu sai gate)
#        sunday_plan_round.sh --check [YYYY-MM-DD]  chỉ in "RUN <ngày-đích>" / "SKIP: lý do"
#        sunday_plan_round.sh --verify            kiểm nội dung plan == nội dung đã quyết; lệch ⇒ gỡ dấu duyệt + escalate (rc 4)
#        sunday_plan_round.sh --second-chance     --verify, rồi gửi lại báo cáo plan nếu hôm nay đúng gate vòng CN
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
BUS_DIR="${SPR_BUS_DIR:-$ROOT/bus}"
INJ_DIR="${SPR_INJ_DIR:-$HERE}"
BQ_FRESH="${SPR_BQ_FRESHNESS:-$HERE/bq_freshness_check.sh}"
JOBS="${SPR_JOBS:-$HERE/jobs.sh}"
NOTIFY="${SPR_NOTIFY:-$HERE/notify_thread.sh}"
BUS="${SPR_BUS:-$HERE/append_event.sh}"
SEND_PLAN="${SPR_SEND_PLAN:-$HERE/send_plan_report.sh}"
MACRO_HC="${SPR_MACRO_HC:-}"                     # rỗng = chạy macro_healthcheck.py thật
FOR_EACH="${SPR_FOR_EACH:-$HERE/for_each_live_account.sh}"
FRESH_TMO="${SPR_FRESHNESS_TIMEOUT:-1800}"       # trần 30' cho bq_freshness_check (bản thật chạy vài phút)
JOB_TMO="${SPR_JOB_TIMEOUT:-1500}"               # ~25' chờ DollarBill (dispatch.sh mặc định 600s/lần, retry 1)
POLL_S="${SPR_POLL_S:-30}"
INJ_TMO="${SPR_INJ_TIMEOUT:-900}"
CANCEL_TRIES="${SPR_CANCEL_TRIES:-4}"            # job 'retrying' làm cancel no-op; thử lại vài lần chờ nó về 'running'
CANCEL_SLEEP="${SPR_CANCEL_SLEEP:-10}"
KEEP_WEEKS="${SPR_KEEP_WEEKS:-8}"
PY="${DNA_PYEXE:-python3}"

ts() { TZ=Asia/Ho_Chi_Minh date +'%F %T ICT'; }
note() { "$NOTIFY" "$1" trading_daily >/dev/null 2>&1 || true; }       # bridge tự đóng timestamp
log() { echo "[$(ts)] $*"; }
bus_err() {  # bus_err <topic> <k=v>... — JSON do json.dumps dựng, không ghép chuỗi
  "$BUS" Taylor error "$1" "$(shift; python3 "$LIB" busjson --kv "$@")" >/dev/null 2>&1 || true
}

if [ "${1:-}" = "--check" ]; then python3 "$LIB" gate ${2:+--check "$2"}; exit 0; fi

# ── khoá: fd 9 CHỈ của wrapper; mọi tiến trình con chạy với 9>&- (không để job nền giữ khoá sau khi wrapper chết) ──
LOCKED=0
take_lock() {  # rc: 0 ok · 1 không tạo được state dir · 2 đang có lượt khác
  [ "$LOCKED" = 1 ] && return 0
  mkdir -p "$STATE_DIR" || return 1
  exec 9>"$STATE_DIR/.lock"
  flock -n 9 || return 2
  LOCKED=1
}

# ── chạy lệnh con ở nền rồi `wait` (trap TERM/INT chạy NGAY, không bị hoãn tới khi lệnh foreground xong) ──
CUR_PID=""
run_wait() {  # run_wait <outfile> <cmd...>   (RW_CD=<dir> để cd trước)
  local out="$1"; shift
  ( if [ -n "${RW_CD:-}" ]; then cd "$RW_CD" || exit 1; fi; exec "$@" ) >"$out" 2>&1 9>&- &
  CUR_PID=$!
  wait "$CUR_PID"; local rc=$?
  CUR_PID=""
  return $rc
}
_on_sig() {
  [ -n "$CUR_PID" ] && kill -TERM "$CUR_PID" 2>/dev/null
  exit "$1"
}

recover_all() {  # → in kết quả; rc của lib (3 = có account không khôi phục được)
  python3 "$LIB" recover --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" 2>&1
}

# ── --verify: chốt chặn lệnh chưa duyệt (không cần gate; no-op nếu không có manifest ntd >= hôm nay) ──
do_verify() {
  [ -d "$STATE_DIR" ] || { log "verify: khong co state dir — khong co vong CN nao de kiem"; return 0; }
  take_lock; case $? in 2) log "verify: dang co mot luot khac chay (lock) — bo qua, se kiem lan sau"; return 0;; 1) return 1;; esac
  local out rc
  out="$(python3 "$LIB" verify --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" 2>&1)"; rc=$?
  [ -n "$out" ] && log "verify rc=$rc:
$out"
  if [ "$rc" -ne 0 ]; then
    note "🔴 Vòng plan CN — KIỂM CUỐI ĐÊM đã SỬA file plan hoặc phát hiện lệch (rc=$rc): khôi phục bản đã quyết / gỡ dấu duyệt / recover vòng bị ngắt — plan cần user xem lại TRƯỚC phiên.
$(printf '%s\n' "$out" | grep -E 'MISMATCH|WARN|RECOVER' | cut -c1-600)"
    bus_err "sunday-plan-round-verify" "status=mismatch" "rc=$rc" "evidence=$(printf '%s' "$out" | grep -E 'MISMATCH|WARN|RECOVER' | head -3 | tr '\n' ' ' | cut -c1-500)" "measured_by=sunday_plan_round_lib.py verify (so content md5 manifest vs dia)"
  fi
  return "$rc"
}

if [ "${1:-}" = "--verify" ]; then do_verify; exit $?; fi

if [ "${1:-}" = "--second-chance" ]; then
  do_verify; vrc=$?
  G="$(python3 "$LIB" gate 2>&1)"
  case "$G" in
    RUN\ *) log "second-chance: gate $G — gui lai bao cao plan (idempotent theo marker)"
            "$FOR_EACH" "$SEND_PLAN" --second-chance 9>&- || log "second-chance send rc=$?" ;;
    *) log "second-chance: $G — khong gui" ;;
  esac
  exit "$vrc"
fi

# ── lượt chính ──
# Lần trước bị kill giữa chừng (SIGKILL/mất điện) → trả plan thứ Sáu về TRƯỚC cổng ngày (§5), nhưng CHỈ manifest ntd >= hôm nay.
if [ -d "$STATE_DIR" ]; then
  take_lock; case $? in 2) log "dang co mot luot khac chay (lock) — thoat"; exit 0;; 1) exit 1;; esac
  REC="$(recover_all)"; rrc=$?
  if [ -n "$REC" ]; then
    log "$REC"
    if [ "$rrc" -eq 0 ]; then
      note "🟡 Vòng plan Chủ nhật: lần chạy trước bị ngắt giữa chừng — đã KHÔI PHỤC plan thứ Sáu từ stash trước khi chạy lại.
$REC"
    else
      note "🔴 Vòng plan Chủ nhật: lần chạy trước bị ngắt và KHÔI PHỤC KHÔNG TRỌN (rc=$rrc) — cần người xem ngay:
$REC"
      bus_err "sunday-plan-round-recover" "status=recover_incomplete" "rc=$rrc" "evidence=$(printf '%s' "$REC" | tr '\n' ' ' | cut -c1-500)" "measured_by=sunday_plan_round_lib.py recover"
    fi
  fi
fi

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

take_lock; case $? in 2) log "dang co mot luot khac chay (lock) — thoat"; exit 0;; 1) exit 1;; esac

RUN_DIR="$STATE_DIR/$NTD"
mkdir -p "$RUN_DIR" || exit 1
START_EPOCH="$(date +%s)"

log "RUN vong plan Chu nhat -> plan dich $NTD, accounts: $LABELS"
note "🔄 Vòng plan Chủ nhật BẮT ĐẦU — plan dành cho thứ Hai $NTD ($LABELS). Có plan thứ Sáu sẽ được stash + so sánh; chỉ khác mới đổi."
# stash IDEMPOTENT: manifest cùng ntd đã có (lần trước bị ngắt) ⇒ giữ stash THỨ SÁU GỐC, không chụp lại từ đĩa.
python3 "$LIB" stash --plan-dir "$PLAN_DIR" --run-dir "$RUN_DIR" --ntd "$NTD" --labels "$LABELS" || { log "FATAL stash loi — dung, chua dong plan nao"; note "🔴 Vòng plan Chủ nhật: STASH lỗi — dừng, chưa động vào plan nào."; exit 1; }

declare -A STATUS DETAIL JOBID CANCEL_RC
for a in $LABELS; do STATUS[$a]="nojob"; DETAIL[$a]=""; JOBID[$a]=""; done
FRESH_LOG="$RUN_DIR/freshness.log"

# cancel_live <acct> <jid>: nếu job chưa kết thúc thì `jobs.sh cancel`, LƯU rc THẬT ngay sau lệnh (không `rc=$?` sau phép gán).
cancel_live() {
  local acct="$1" jid="$2" crc st try
  "$JOBS" status "$jid" >/dev/null 2>&1; st=$?
  case "$st" in 0|1) return 0 ;; esac      # done / failed|cancelled|timeout|orphaned: đã kết thúc
  for try in $(seq 1 "$CANCEL_TRIES"); do
    "$JOBS" cancel "$jid" >"$RUN_DIR/job_${acct}.cancel" 2>&1; crc=$?
    CANCEL_RC[$acct]="$crc"
    "$JOBS" status "$jid" >/dev/null 2>&1; st=$?
    case "$st" in 0|1|5) break ;; esac      # kết thúc, hoặc chờ-resume (cancel no-op: settle gỡ bản ghi resume)
    [ "$try" -lt "$CANCEL_TRIES" ] && sleep "$CANCEL_SLEEP"   # running/retrying còn sống: thử lại
  done
}

# settle_jobs <scan 0|1>: parse job id từ freshness.log BẤT KỂ FRESH_RC, cancel job còn sống, rồi XÁC MINH đã kết thúc.
SETTLE_LINES=""
settle_jobs() {
  local scan="$1" acct jid args=()
  if [ -s "$FRESH_LOG" ]; then
    while read -r acct jid; do
      [ -n "$jid" ] || continue
      JOBID[$acct]="$jid"
      cancel_live "$acct" "$jid"
      args+=(--job "$acct=$jid")
    done < <(python3 "$LIB" jobs "$FRESH_LOG" 2>/dev/null)
  fi
  [ "$scan" = 1 ] && args+=(--scan)
  SETTLE_LINES="$(python3 "$LIB" settle --jobs-dir "$BUS_DIR/jobs" --pend-dir "$BUS_DIR/pending_resumes" \
                    --removed-dir "$RUN_DIR/pending_removed" --since "$START_EPOCH" ${args[@]+"${args[@]}"} 2>&1)"
  [ -n "$SETTLE_LINES" ] && log "settle:
$SETTLE_LINES"
}

# Mọi lối thoát (kể cả TERM/INT) mà còn account CHƯA quyết định → dừng job + trả plan thứ Sáu từ stash (§5).
DONE_OK=0
_final_guard() {
  [ "$DONE_OK" = 1 ] && return
  trap - EXIT
  settle_jobs 1
  local r rc unsettled=""
  r="$(recover_all)"; rc=$?
  printf '%s\n' "$SETTLE_LINES" | grep -q 'UNSETTLED' && unsettled="⚠️ KHÔNG xác minh được job DollarBill đã dừng: $(printf '%s' "$SETTLE_LINES" | grep UNSETTLED | head -2 | tr '\n' ' ' | cut -c1-400) — plan có thể bị ghi đè muộn; --verify 23:00/08:30 sẽ kiểm. "
  if [ -z "$r" ]; then
    log "THOAT BAT THUONG — khong co account nao can khoi phuc (moi account da quyet dinh). ${unsettled}"
    note "🟡 Vòng plan Chủ nhật thoát bất thường nhưng KHÔNG có account nào cần khôi phục (đã quyết định hết). ${unsettled}"
  elif [ "$rc" -eq 0 ]; then
    log "THOAT BAT THUONG — $r"
    note "🔴 Vòng plan Chủ nhật bị NGẮT giữa chừng — đã khôi phục plan thứ Sáu từ stash. ${unsettled}${r}"
  else
    log "THOAT BAT THUONG — KHOI PHUC KHONG TRON rc=$rc — $r"
    note "🔴 Vòng plan Chủ nhật bị NGẮT và KHÔI PHỤC KHÔNG TRỌN (rc=$rc) — cần người xem NGAY. ${unsettled}${r}"
    bus_err "sunday-plan-round-guard-$NTD" "plan_date=$NTD" "status=recover_incomplete" "evidence=$(printf '%s' "$r" | tr '\n' ' ' | cut -c1-500)" "measured_by=sunday_plan_round_lib.py recover"
  fi
  if [ -n "$unsettled" ]; then
    bus_err "sunday-plan-round-jobs-$NTD" "plan_date=$NTD" "status=job_unsettled" "evidence=$(printf '%s' "$SETTLE_LINES" | grep UNSETTLED | head -3 | tr '\n' ' ' | cut -c1-500)" "measured_by=$RUN_DIR/freshness.log + jobs settle"
  fi
}
trap _final_guard EXIT
trap '_on_sig 143' TERM
trap '_on_sig 130' INT

# ── 1. macro_healthcheck (cổng cuối tuần, xem ⚠️ đầu file) ──
if [ -n "$MACRO_HC" ]; then run_wait "$RUN_DIR/macro_hc.log" "$MACRO_HC"; hc_rc=$?
else RW_CD="$WC_ROOT" run_wait "$RUN_DIR/macro_hc.log" timeout -k 10 300 "$PY" macro_healthcheck.py; hc_rc=$?; fi
log "macro_healthcheck rc=$hc_rc (0 HEALTHY / 1 DEGRADED / 2 FAILED; cổng fail-closed theo file — không chặn vòng)"
[ "$hc_rc" -ge 2 ] && note "🟡 Vòng plan CN: macro_healthcheck FAILED rc=$hc_rc — cổng trạng thái sẽ rơi DT4_only (fail-closed, đúng thiết kế). Xem $RUN_DIR/macro_hc.log"

# ── 2. bq_freshness_check morning+force (KHÔNG pipe tee — arch-review 10-12 tái hiện treo; chạy nền + wait để TERM không bị hoãn) ──
SUNDAY_TAIL="BẮT BUỘC đặt requires_user_approval=true cho mọi lệnh và nói rõ trong summary rằng đây là plan VÒNG CHỦ NHẬT TỐI (wrapper sunday_plan_round.sh) cho thứ Hai: user duyệt trước 08:45 ICT thứ Hai. Wrapper tự chạy các injector (TV1/auto-exit) và tự gửi báo cáo plan SAU khi bạn ghi xong plan — bạn KHÔNG chạy chúng. Chuỗi park (park_trim/jit_unpark/merge_park) KHÔNG chạy cuối tuần: không tự thêm lệnh bán park."
run_wait "$FRESH_LOG" env MIKE_MORNING_RUN=1 MIKE_MORNING_FORCE=1 "MIKE_MORNING_NOTE_TAIL=$SUNDAY_TAIL" timeout -k 20 "$FRESH_TMO" "$BQ_FRESH"
FRESH_RC=$?
log "bq_freshness_check rc=$FRESH_RC (log: $FRESH_LOG)"
FRESH_WHY="$(grep -E '^(FAIL|FATAL|=== FAILED|⛔|⚠️)|STALE' "$FRESH_LOG" | tail -3 | tr '\n' ' ' | cut -c1-400)"
[ -z "$FRESH_WHY" ] && FRESH_WHY="$(tail -n 3 "$FRESH_LOG" | tr '\n' ' ' | cut -c1-400)"
[ "$FRESH_RC" = 124 ] && FRESH_WHY="timeout ${FRESH_TMO}s: $FRESH_WHY"

# Job id parse từ log BẤT KỂ FRESH_RC (freshness fail/timeout có thể đã dispatch DollarBill rồi mới chết).
while read -r acct jid; do [ -n "$jid" ] && JOBID[$acct]="$jid"; done < <(python3 "$LIB" jobs "$FRESH_LOG" 2>/dev/null)
if [ "$FRESH_RC" -eq 0 ]; then
  for a in $LABELS; do
    if [ -n "${JOBID[$a]}" ]; then STATUS[$a]="pending"
    else DETAIL[$a]="bq_freshness chay xong rc=0 nhung KHONG dispatch DollarBill cho $a ($(grep -E "SKIP|WARN dispatch|\[WARN\] dispatch" "$FRESH_LOG" | tail -1 | cut -c1-160))"; fi
  done
else
  for a in $LABELS; do STATUS[$a]="freshness_fail"; DETAIL[$a]="bq_freshness_check rc=$FRESH_RC: $FRESH_WHY"; done
fi

# ── 3. chờ job DollarBill (trần JOB_TMO; quá hạn → cancel_live; settle_jobs xác minh ngay sau) ──
DEADLINE=$(( $(date +%s) + JOB_TMO ))
while :; do
  pend=0
  for a in $LABELS; do
    [ "${STATUS[$a]}" = "pending" ] || continue
    "$JOBS" status "${JOBID[$a]}" >"$RUN_DIR/job_${a}.status" 2>&1 9>&-; rc=$?
    case "$rc" in
      0) STATUS[$a]="ok" ;;
      1|4) STATUS[$a]="job_fail"; DETAIL[$a]="DollarBill job ${JOBID[$a]} status rc=$rc: $(tail -n 2 "$RUN_DIR/job_${a}.status" | tr '\n' ' ' | cut -c1-300)" ;;
      5) STATUS[$a]="job_resume_pending"   # usage_limited/maxturns_pending: resume_pending.py (cron */10) sẽ bắn job MỚI — không chờ hết JOB_TMO, gỡ bản ghi resume ở 3b rồi khôi phục
         DETAIL[$a]="DollarBill job ${JOBID[$a]} o trang thai cho-resume (rc=5): $(tail -n 2 "$RUN_DIR/job_${a}.status" | tr '\n' ' ' | cut -c1-200)" ;;
      *) pend=1 ;;
    esac
  done
  [ "$pend" = 0 ] && break
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    for a in $LABELS; do
      if [ "${STATUS[$a]}" = "pending" ]; then
        cancel_live "$a" "${JOBID[$a]}"
        STATUS[$a]="job_timeout"; DETAIL[$a]="DollarBill job ${JOBID[$a]} chua xong sau ${JOB_TMO}s — da gui lenh huy (jobs.sh cancel rc=${CANCEL_RC[$a]:-?})"
      fi
    done
    break
  fi
  run_wait /dev/null sleep "$POLL_S"
done

# ── 3b. XÁC MINH mọi job DollarBill đã ở trạng thái kết thúc (đọc lại bản ghi), gỡ bản ghi pending_resume; quét thêm job lạ nếu có account hỏng ──
any_bad=0; for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] || any_bad=1; done
settle_jobs "$any_bad"
for a in $LABELS; do
  [ -n "${JOBID[$a]}" ] || continue
  line="$(printf '%s\n' "$SETTLE_LINES" | grep -E "^(UN)?SETTLED $a ${JOBID[$a]} " | head -1)"
  case "$line" in
    UNSETTLED*) STATUS[$a]="job_unsettled"; DETAIL[$a]="${DETAIL[$a]:+${DETAIL[$a]} | }${line#UNSETTLED $a } ";;
    SETTLED*)   case "${STATUS[$a]}" in job_timeout|job_resume_pending) DETAIL[$a]="${DETAIL[$a]} → DA XAC MINH: ${line#SETTLED $a ${JOBID[$a]} }" ;; esac ;;
  esac
done
SCAN_LINE="$(printf '%s\n' "$SETTLE_LINES" | grep -E '^SCAN-UNSETTLED' | head -2 | tr '\n' ' ')"
if [ -n "$SCAN_LINE" ]; then
  for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] || DETAIL[$a]="${DETAIL[$a]} | $SCAN_LINE"; done
  note "🟡 Vòng plan CN: còn job DollarBill lạ đang sống ($SCAN_LINE) — chưa xác minh được nó không ghi plan; --verify cuối đêm sẽ kiểm."
fi

# ── 4. injectors đúng như T2-T6 (compute_active_nav_all 20:15 → inject_discretionary 20:30 → auto_exit_inject 20:40; drift 20:50) ──
#      KHÔNG gồm chuỗi park (park_trim/jit_unpark/merge_park tự bỏ qua cuối tuần) — xem park_guard ở lib.
INJ_FAIL=""
any_ok=0; for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] && any_ok=1; done
if [ "$any_ok" = 1 ]; then
  for step in compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh; do
    run_wait "$RUN_DIR/inj_$step.log" timeout -k 20 "$INJ_TMO" "$INJ_DIR/$step"; irc=$?
    log "$step rc=$irc"
    if [ "$irc" -ne 0 ] && [ -z "$INJ_FAIL" ]; then
      INJ_FAIL="$step rc=$irc: $(tail -n 3 "$RUN_DIR/inj_$step.log" | tr '\n' ' ' | cut -c1-300)"
    fi
  done
  # plan_position_drift_check chỉ CỜ/BÁO (CN trả SKIP — không phải phiên); lỗi KHÔNG làm hỏng vòng.
  run_wait "$RUN_DIR/inj_drift.log" timeout -k 20 "$INJ_TMO" "$FOR_EACH" "$INJ_DIR/plan_position_drift_check.py"
  log "plan_position_drift_check rc=$? (chi co/bao)"
  if [ -n "$INJ_FAIL" ]; then
    for a in $LABELS; do [ "${STATUS[$a]}" = "ok" ] && { STATUS[$a]="inject_fail"; DETAIL[$a]="$INJ_FAIL — plan moi co the thieu phan chen (TV1/auto-exit) nen KHONG tin"; }; done
  fi
fi

# ── 5. quyết định từng account (lỗi của account này không được kéo account khác — decide tự bọc, RESULT=x chỉ khi không khôi phục được) ──
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
       bus_err "sunday-plan-round-$a-$NTD" "account=$a" "plan_date=$NTD" "status=${STATUS[$a]}" "restored_friday=true" \
         "evidence=$(printf '%s' "${DETAIL[$a]:-$MSG}" | tr '\n' ' ' | cut -c1-500)" "measured_by=$RUN_DIR/freshness.log + job_*.status + jobs settle" ;;
    x) RC_ALL=1; note "$MSG"
       bus_err "sunday-plan-round-$a-$NTD" "account=$a" "plan_date=$NTD" "status=decide_crash_unrestored" "restored_friday=false" \
         "evidence=$(printf '%s' "$MSG" | tr '\n' ' ' | cut -c1-500)" "measured_by=sunday_plan_round_lib.py decide" ;;
    *) RC_ALL=1
       # decide chết trước khi in RESULT (vd Python không khởi động): KHÔNG nuốt output, KHÔNG recover cả loạt (sẽ chép đè account chưa tới lượt)
       note "🔴 $a: vòng Chủ nhật — decide lỗi không rõ, CHƯA khẳng định đã khôi phục. Output thật: $(printf '%s' "$OUT" | tail -n 5 | tr '\n' ' ' | cut -c1-500)"
       bus_err "sunday-plan-round-$a-$NTD" "account=$a" "plan_date=$NTD" "status=decide_no_result" "restored_friday=unknown" \
         "evidence=$(printf '%s' "$OUT" | tail -n 5 | tr '\n' ' ' | cut -c1-500)" "measured_by=sunday_plan_round_lib.py decide (khong co RESULT=)"
       r2="$(python3 "$LIB" recover --plan-dir "$PLAN_DIR" --state-dir "$STATE_DIR" --account "$a" 2>&1)"; rrc=$?
       log "recover rieng $a rc=$rrc: $r2"
       [ -n "$r2" ] && note "🟠 $a: recover riêng account rc=$rrc: $(printf '%s' "$r2" | tr '\n' ' ' | cut -c1-400)" ;;
  esac
done

# ── 6. gửi báo cáo plan cho account (b): Chủ nhật KHÔNG có cron 21:00 → wrapper tự gọi (idempotent theo marker) ──
for a in $SENT; do
  if [ "${SPR_SEND:-1}" = "1" ]; then
    run_wait "$RUN_DIR/send_${a}.log" "$SEND_PLAN" --account "$a"; log "send_plan_report $a rc=$?"
  fi
done

python3 "$LIB" prune --state-dir "$STATE_DIR" --keep "$KEEP_WEEKS" >/dev/null 2>&1 || true
SUMMARY="$(python3 "$LIB" summary --run-dir "$RUN_DIR" 2>/dev/null)"
DONE_OK=1
note "🏁 Vòng plan Chủ nhật XONG ($NTD): ${SUMMARY:-?} — (a)=giữ thứ Sáu · (b)=plan mới chờ duyệt · (c)=lỗi, đã trả thứ Sáu · (x)=lỗi KHÔNG khôi phục được. Kiểm cuối đêm: --verify 23:00 CN + 08:30 T2."
exit "$RC_ALL"
