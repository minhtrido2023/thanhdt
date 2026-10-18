#!/usr/bin/env bash
# sunday_plan_round_selfcheck.sh — kiểm bin/sunday_plan_round.sh + sunday_plan_round_lib.py bằng STUB
# (không dispatch DollarBill, không ghi plan thật, không gọi DNSE/BQ/Discord). Mọi plan/bus nằm trong
# thư mục tạm; ngày mô phỏng bằng MIKE_NOW_ICT (§16: chạy lại dưới env -u TZ và TZ ngoại).
#
#   sunday_plan_round_selfcheck.sh            toàn bộ: 3 TZ + mutant   (exit 0 = PASS hết)
#   SC_PHASE=suite sunday_plan_round_selfcheck.sh   chỉ 1 lượt suite dưới env hiện tại
#   SC_SECTIONS="fields park" ...             chỉ chạy vài section (mutant dùng để chạy nhanh)
# Mutant: mỗi mutant PHẢI làm suite FAIL; nếu suite vẫn PASS ⇒ mutant "sống" ⇒ selfcheck FAIL.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAP="${SC_WRAP:-$HERE/sunday_plan_round.sh}"
LIBF="${SC_LIB:-$HERE/sunday_plan_round_lib.py}"
SELF="$HERE/$(basename "${BASH_SOURCE[0]}")"
WC="$(cd "$HERE/../.." && pwd)"
export MIKE_BOT_TEST_MODE=1     # §5b — selfcheck này không dựng Executor, nhưng đặt phòng hờ
SC=""; MD=""
trap 'rm -rf "${SC:-}" "${MD:-}"' EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

PASS=0; FAIL=0
ck() {  # ck "tên" <lệnh kiểm>
  local name="$1"; shift
  if "$@"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); echo "  ✗ FAIL: $name"; [ -n "${FAIL_FAST:-}" ] && { echo "RESULT pass=$PASS fail=$FAIL"; exit 1; }; fi
}
eq()  { [ "$1" = "$2" ]; }
ne()  { [ "$1" != "$2" ]; }
has() { grep -qF -- "$2" "$1" 2>/dev/null; }
hasnt() { ! grep -qF -- "$2" "$1" 2>/dev/null; }
md5of() { md5sum "$1" 2>/dev/null | cut -d' ' -f1; }
sec() { [ -z "${SC_SECTIONS:-}" ] || [[ " $SC_SECTIONS " == *" $1 "* ]]; }

# ── dựng sandbox ────────────────────────────────────────────────────────────────────────────
mk_sandbox() {
  SC="$(mktemp -d /tmp/spr_sc.XXXXXX)"
  mkdir -p "$SC/plans" "$SC/stubs" "$SC/inj" "$SC/state" "$SC/js" "$SC/bus/jobs" "$SC/bus/pending_resumes"
  : >"$SC/notify.log"; : >"$SC/bus.log"; : >"$SC/send.log"; : >"$SC/inj.log"; : >"$SC/cancel.log"
  cat >"$SC/stubs/notify.sh" <<'S'
#!/usr/bin/env bash
printf '%s\n---\n' "$1" >> "$SC/notify.log"
S
  cat >"$SC/stubs/bus.sh" <<'S'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SC/bus.log"
S
  cat >"$SC/stubs/send.sh" <<'S'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SC/send.log"
if [ "${STUB_KILL_AT_SEND:-}" = term ]; then kill -TERM "$(cat "$SC/wrapper.pid")"; sleep 3; fi
S
  cat >"$SC/stubs/macro.sh" <<'S'
#!/usr/bin/env bash
echo macro-ok
S
  cat >"$SC/stubs/foreach.sh" <<'S'
#!/usr/bin/env bash
"$@"
S
  # jobs.sh stub: ĐỌC bản ghi thật bus/jobs/<id>.json, mô phỏng đúng mã thoát + ngữ nghĩa cancel của mike_json.py
  cat >"$SC/stubs/jobs.sh" <<'S'
#!/usr/bin/env python3
import json, os, signal, sys
SC = os.environ["SC"]; cmd, jid = sys.argv[1], sys.argv[2]
fp = f"{SC}/bus/jobs/{jid}.json"
try:
    o = json.load(open(fp))
except Exception:
    print("not-found:", jid); sys.exit(4)
st = o["status"]
if cmd == "status":
    print("job", jid, st)
    if st == "failed": print("job failed: stub error boom")
    sys.exit({"done": 0, "running": 2, "retrying": 2, "usage_limited": 5, "maxturns_pending": 5}.get(st, 1))
if cmd == "cancel":
    open(f"{SC}/cancel.log", "a").write(jid + "\n")
    if os.environ.get("STUB_CANCEL_RC"):          # mô phỏng cancel lỗi (vd rc=5 process sống sót): KHÔNG đổi trạng thái
        print("stub cancel forced rc"); sys.exit(int(os.environ["STUB_CANCEL_RC"]))
    if st != "running":                            # đúng như cmd_job_cancel: !=running (retrying/usage_limited/...) => no-op rc=0
        print(f"job {jid} is already {st} — nothing to cancel"); sys.exit(0)
    pf = f"{SC}/js/{jid}.pid"
    if os.path.exists(pf):
        try: os.kill(int(open(pf).read()), signal.SIGKILL)
        except Exception: pass
    o["status"] = "cancelled"; json.dump(o, open(fp, "w")); print("cancelled"); sys.exit(0)
S
  # writeplan.py <path> <mode> <acct> — dựng plan "DollarBill mới" từ bản thứ Sáu
  cat >"$SC/stubs/writeplan.py" <<'S'
#!/usr/bin/env python3
import json, os, sys
path, mode, acct = sys.argv[1:4]
base = json.load(open(os.environ["SC"] + "/fri_%s.json" % acct))
if mode == "none": sys.exit(0)
if mode == "bad": open(path, "w").write("{not json"); sys.exit(0)
base["created_at"] = "2026-10-18T19:05:00+07:00"
tv1 = lambda b: [o for o in b["orders"] if o["ticker"] == "TV1"][0]
if mode == "wrongdate": base["plan_date"] = "2026-10-20"
if mode in ("diff", "approved_diff", "wrongdate", "late"):
    base["orders"][0]["qty"] += 100
    base["orders"].append({"id": "BUY-NEW", "ticker": "NEW", "side": "buy", "qty": 500, "ref_price": 12340, "order_type": "LO", "limit_price_vnd": 12340})
if mode == "tickjitter":
    for o in base["orders"]: o["ref_price"] = o["ref_price"] + 0.0000001
if mode == "nochg_ordertype":      # chỉ khác phần executor KHÔNG dùng => phải coi là GIỐNG
    for o in base["orders"]: o["order_type"] = "ATC"; o["limit_price_vnd"] = o["limit_price_vnd"] + 777; o["note"] = "khac"
    base["notes"] = ["x"]
if mode == "chg_qty": tv1(base)["qty"] += 100
if mode == "chg_ref": tv1(base)["ref_price"] = 20400
if mode == "chg_urg": tv1(base)["urgency"] = "high"
if mode == "chg_book": tv1(base)["book"] = "BAL"
if mode == "chg_cash": tv1(base)["cash_only"] = True
if mode == "chg_ceil": tv1(base)["hard_no_chase_ceiling_vnd"] = 20500
if mode == "chg_prio": tv1(base)["priority"] = 2
if mode == "chg_state": base["state"] = 2; base["state_name"] = "BEAR"
if mode == "chg_stnum": base["state"] = 2
if mode == "chg_stname": base["state_name"] = "BEAR"
if mode == "chg_sd": base["signal_date"] = "2026-10-15"
if mode not in ("approved_diff", "late"):
    for k in [k for k in base if k.startswith("approv") or k.startswith("mafee")]: del base[k]
    base["requires_user_approval"] = True
json.dump(base, open(path, "w"))
S
  for s in compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh plan_position_drift_check.py; do
    cat >"$SC/inj/$s" <<S
#!/usr/bin/env bash
echo "$s" >> "\$SC/inj.log"
[ "\${STUB_INJ_FAIL:-}" = "$s" ] && { echo "stub injector boom"; exit 1; }
exit 0
S
  done
  # bq_freshness stub: ghi plan theo STUB_ACCT_<A>, tạo bản ghi job thật, in dòng dispatch như bản thật
  cat >"$SC/stubs/bq.sh" <<'S'
#!/usr/bin/env bash
{ echo "stub bq_freshness MIKE_MORNING_RUN=${MIKE_MORNING_RUN:-} FORCE=${MIKE_MORNING_FORCE:-}"
  echo "fd9=$([ -e /proc/self/fd/9 ] && echo open || echo closed)"
  echo "TAIL=${MIKE_MORNING_NOTE_TAIL:-}"; } > "$SC/bq_env.log"
[ -n "${STUB_BREAK_STASH_ZaloPay:-}" ] && rm -f "$SC/state/2026-10-19/stash/plan_ZaloPay_2026-10-19.json"
[ "${STUB_FRESH_RC:-0}" != 0 ] && [ -z "${STUB_DISPATCH_BEFORE_FAIL:-}" ] && { echo "FAIL DT5G publisher-evidence: stub macro boom"; exit "$STUB_FRESH_RC"; }
for A in $SPR_LABELS; do
  echo "--- [pipeline-4] dispatch DollarBill lập plan T+1 cho $A ---"
  eval "mode=\${STUB_ACCT_$A:-same}"; eval "js=\${STUB_JOB_$A:-ok}"; eval "late=\${STUB_LATE_$A:-}"
  echo "DISPATCHED DollarBill (job=JOB_$A pid=1) → log: /dev/null"
  python3 - "$SC" "JOB_$A" "$js" <<'PY'
import json, sys, time, os
sc, jid, js = sys.argv[1:4]
st = {"ok": "done", "fail": "failed", "run": "running", "usage": "usage_limited", "usage_nopend": "usage_limited", "retrying": "retrying"}[js]
json.dump({"job_id": jid, "to": "DollarBill", "status": st, "started_at": str(int(time.time()))}, open(f"{sc}/bus/jobs/{jid}.json", "w"))
if js == "usage": json.dump({"agent": "DollarBill", "orig_job_id": jid, "resume_at": 1}, open(f"{sc}/bus/pending_resumes/{jid}.json", "w"))
PY
  if [ -n "$late" ]; then   # job NỀN còn sống, sẽ ghi plan sau $late giây (kèm dấu duyệt cũ — trường hợp xấu nhất)
    ( setsid bash -c "sleep $late; python3 '$SC/stubs/writeplan.py' '$SPR_PLAN_DIR/plan_${A}_2026-10-19.json' late $A" >/dev/null 2>&1 9>&- & echo $! > "$SC/js/JOB_$A.pid" )
  fi
  python3 "$SC/stubs/writeplan.py" "$SPR_PLAN_DIR/plan_${A}_2026-10-19.json" "$mode" "$A"
done
[ "${STUB_FRESH_RC:-0}" != 0 ] && { echo "FAIL DT5G publisher-evidence: stub macro boom (sau dispatch)"; exit "$STUB_FRESH_RC"; }
case "${STUB_KILL:-}" in
  kill9) for i in $(seq 50); do [ -s "$SC/wrapper.pid" ] && break; sleep 0.1; done; kill -9 "$(cat "$SC/wrapper.pid")"; sleep 1 ;;
  term)  for i in $(seq 50); do [ -s "$SC/wrapper.pid" ] && break; sleep 0.1; done; kill -TERM "$(cat "$SC/wrapper.pid")"; sleep 2 ;;
  termlong) for i in $(seq 50); do [ -s "$SC/wrapper.pid" ] && break; sleep 0.1; done; kill -TERM "$(cat "$SC/wrapper.pid")"; sleep 25 ;;
esac
exit 0
S
  chmod +x "$SC"/stubs/* "$SC"/inj/*
  for A in SpaceX ZaloPay; do
    python3 - "$SC/fri_$A.json" "$A" <<'PY'
import json, sys
p = {"plan_date": "2026-10-19", "signal_date": "2026-10-16", "strategy": "V2.4", "strategy_version": "2.4",
     "state": 3, "state_name": "NEUTRAL", "nav_basis": {}, "account": sys.argv[2], "requires_user_approval": False,
     "approved_by": "user (Discord 2026-10-16)", "approved_at": "2026-10-16T21:30:00+07:00", "mafee_authorized": True,
     "created_at": "2026-10-16T19:05:00+07:00",
     "orders": [{"id": "SELL-AAA", "ticker": "AAA", "side": "sell", "qty": 300, "ref_price": 21050, "book": "BAL", "urgency": "normal",
                 "priority": 1, "order_type": "LO", "limit_price_vnd": 21050},
                {"id": "BUY-TV1", "ticker": "TV1", "side": "buy", "qty": 300, "ref_price": 19900, "book": "LAG", "priority": 5,
                 "order_type": "LO", "limit_price_vnd": 19900, "hard_no_chase_ceiling_vnd": 20000}]}
json.dump(p, open(sys.argv[1], "w"))
PY
    cp "$SC/fri_$A.json" "$SC/plans/plan_${A}_2026-10-19.json"
    # artifact park thứ Sáu RỖNG (cả hai tầng): không cản (b)
    echo '{"decision":"NO_TRIM","orders":[],"blocked":[]}' > "$SC/plans/park_trim_${A}_2026-10-19.json"
    echo '{"decision":"NO_TRIGGER","orders":[],"buy_amendments":[]}' > "$SC/plans/jit_unpark_${A}_2026-10-19.json"
  done
  export SC SPR_PLAN_DIR="$SC/plans" SPR_STATE_DIR="$SC/state" SPR_BUS_DIR="$SC/bus" SPR_INJ_DIR="$SC/inj" SPR_BQ_FRESHNESS="$SC/stubs/bq.sh" \
    SPR_JOBS="$SC/stubs/jobs.sh" SPR_NOTIFY="$SC/stubs/notify.sh" SPR_BUS="$SC/stubs/bus.sh" SPR_SEND_PLAN="$SC/stubs/send.sh" \
    SPR_MACRO_HC="$SC/stubs/macro.sh" SPR_FOR_EACH="$SC/stubs/foreach.sh" SPR_LABELS="SpaceX ZaloPay" SPR_POLL_S=1 \
    SPR_JOB_TIMEOUT=20 SPR_CANCEL_TRIES=2 SPR_CANCEL_SLEEP=0 SPR_NO_ENV=1 SPR_WINDOW_GATE="$HERE/fa_ratings_earnings_window_daily.sh" \
    WORKDIR_8L="$WC" MIKE_NOW_ICT="2026-10-18T19:00:00" SPR_LIB="$LIBF"
  unset STUB_FRESH_RC STUB_ACCT_SpaceX STUB_ACCT_ZaloPay STUB_JOB_SpaceX STUB_JOB_ZaloPay STUB_KILL STUB_INJ_FAIL STUB_LATE_SpaceX STUB_LATE_ZaloPay \
        STUB_DISPATCH_BEFORE_FAIL STUB_CANCEL_RC STUB_BREAK_STASH_ZaloPay STUB_KILL_AT_SEND SPR_FAULT_DECIDE
}
reset_sb() { rm -rf "$SC"; mk_sandbox; }
run_wrap() { bash "$WRAP" "$@" >"$SC/out.log" 2>&1; echo $? >"$SC/rc"; }
rcv() { cat "$SC/rc"; }
P() { echo "$SC/plans/plan_${1}_2026-10-19.json"; }
F() { echo "$SC/fri_${1}.json"; }
sameF() { eq "$(md5of "$(P "$1")")" "$(md5of "$(F "$1")")"; }
notF() { ne "$(md5of "$(P "$1")")" "$(md5of "$(F "$1")")"; }
approved_of() { python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('approved_by','<none>'))" "$1"; }
set_key() { python3 - "$1" "$2" "$3" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); p[sys.argv[2]] = json.loads(sys.argv[3]); json.dump(p, open(sys.argv[1], "w"))
PY
}
# Chạy wrapper nền, in pid ra $SC/wrapper.pid, chờ xong (cho các test kill)
run_bg() { ( "$@" bash "$WRAP" >"$SC/out1.log" 2>&1 & echo $! >"$SC/wrapper.pid"; wait ) 2>/dev/null; }

suite() {
  local TZNOTE="TZ=${TZ-<unset>}"
  echo "== suite ($TZNOTE) =="
  REAL_BEFORE="$(find "$WC/data/trade_plans" -type f -printf '%p %T@\n' 2>/dev/null | md5sum)"
  mk_sandbox

  if sec gate; then
  g() { bash "$WRAP" --check "$1" 2>&1; }
  ck "gate CN trong cửa sổ (10-18) → RUN, đích thứ Hai 10-19"   eq "$(g 2026-10-18)" "RUN 2026-10-19"
  ck "gate CN 10-11 (≥10 tháng 10) → RUN"                      eq "$(g 2026-10-11)" "RUN 2026-10-12"
  ck "gate CN 10-04 (<10 tháng 10) → SKIP"                      eq "$(g 2026-10-04 | cut -c1-4)" "SKIP"
  ck "gate thứ Bảy 10-17 → SKIP (không phải CN)"                eq "$(g 2026-10-17 | cut -c1-4)" "SKIP"
  ck "gate thứ Hai 10-12 → SKIP"                                eq "$(g 2026-10-12 | cut -c1-4)" "SKIP"
  ck "gate CN 11-08 (tháng 2/5/8/11 ngày ≤10) → RUN"            eq "$(g 2026-11-08)" "RUN 2026-11-09"
  ck "gate CN 11-15 (>10) → SKIP"                               eq "$(g 2026-11-15 | cut -c1-4)" "SKIP"
  ck "gate CN 12-06 (ngoài cửa sổ) → SKIP"                      eq "$(g 2026-12-06 | cut -c1-4)" "SKIP"
  ck "gate CN 09-20 (ngoài cửa sổ) → SKIP"                      eq "$(g 2026-09-20 | cut -c1-4)" "SKIP"
  ck "gate CN 2026-01-11 (tháng 1 ≥10) → RUN"                   eq "$(g 2026-01-11)" "RUN 2026-01-12"
  ck "gate thứ Hai là lễ (CN 2029-04-29, T2 30/04+01/05 lễ) → RUN, đích 2029-05-02" eq "$(g 2029-04-29)" "RUN 2029-05-02"
  ck "gate CN chính nó là lễ (2028-04-30) → SKIP"               eq "$(g 2028-04-30 | cut -c1-4)" "SKIP"
  fi

  if sec noop; then
  reset_sb; MIKE_NOW_ICT="2026-10-17T19:00:00" run_wrap
  ck "thứ Bảy: rc=0"                       eq "$(rcv)" 0
  ck "thứ Bảy: không notify"               eq "$(wc -c <"$SC/notify.log" | tr -d ' ')" 0
  ck "thứ Bảy: không tạo stash/state"      eq "$(ls "$SC/state" | wc -l | tr -d ' ')" 0
  ck "thứ Bảy: plan nguyên vẹn"            sameF SpaceX
  ck "thứ Bảy: 1 dòng log SKIP"            has "$SC/out.log" "SKIP"
  reset_sb; MIKE_NOW_ICT="2026-12-06T19:00:00" run_wrap
  ck "CN ngoài cửa sổ: rc=0, không notify" eq "$(rcv)$(wc -c <"$SC/notify.log" | tr -d ' ')" 00
  fi

  # ── (a) cả hai GIỐNG ──
  if sec a; then
  reset_sb; run_wrap
  ck "A: rc=0"                                   eq "$(rcv)" 0
  ck "A: SpaceX khôi phục NGUYÊN FILE thứ Sáu (md5 gồm dấu duyệt)" sameF SpaceX
  ck "A: ZaloPay khôi phục nguyên file thứ Sáu"  sameF ZaloPay
  ck "A: notify 'không đổi' SpaceX"              has "$SC/notify.log" "plan SpaceX khong doi so voi thu Sau"
  ck "A: notify 'không đổi' ZaloPay"             has "$SC/notify.log" "plan ZaloPay khong doi so voi thu Sau"
  ck "A: §29 — in approved_by THẬT đọc từ file"  has "$SC/notify.log" "approved_by='user (Discord 2026-10-16)'"
  ck "A: có thông báo bắt đầu"                   has "$SC/notify.log" "BẮT ĐẦU"
  ck "A: có thông báo kết thúc"                  has "$SC/notify.log" "XONG"
  ck "A: KHÔNG gọi send_plan_report"             eq "$(wc -c <"$SC/send.log" | tr -d ' ')" 0
  ck "A: bus không có error"                     eq "$(wc -c <"$SC/bus.log" | tr -d ' ')" 0
  ck "A: bq_freshness nhận MORNING_RUN=1 FORCE=1" has "$SC/bq_env.log" "MIKE_MORNING_RUN=1 FORCE=1"
  ck "A: bq_freshness nhận NOTE_TAIL của vòng CN" has "$SC/bq_env.log" "VÒNG CHỦ NHẬT TỐI"
  ck "A: injector đúng thứ tự cron" eq "$(tr '\n' ' ' <"$SC/inj.log")" "compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh plan_position_drift_check.py "
  ck "A: manifest phase=done"                    has "$SC/state/2026-10-19/manifest.json" '"phase": "done"'
  # Friday KHÔNG có dấu duyệt: lời nhắn phải nói THẬT là không có (không "giữ trạng thái duyệt" suông)
  reset_sb
  for A in SpaceX ZaloPay; do python3 - "$(F $A)" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
for k in [k for k in p if k.startswith("approv") or k.startswith("mafee")]: del p[k]
p["requires_user_approval"] = True; json.dump(p, open(sys.argv[1], "w"))
PY
    cp "$(F $A)" "$(P $A)"; done
  run_wrap
  ck "A2: thứ Sáu chưa duyệt → nói 'KHONG co approved_by'" has "$SC/notify.log" "KHONG co approved_by"
  ck "A2: không bịa approved_by"                 hasnt "$SC/notify.log" "approved_by='user"
  fi

  if sec fields; then
  # ── so sánh theo phần executor dùng ──
  reset_sb; STUB_ACCT_SpaceX=tickjitter run_wrap
  ck "F0: jitter ref_price dưới bước giá → vẫn (a)"            sameF SpaceX
  reset_sb; STUB_ACCT_SpaceX=nochg_ordertype run_wrap
  ck "F0b: chỉ đổi order_type/limit_price_vnd/note → vẫn (a) (executor không dùng)" sameF SpaceX
  for fld in qty ref urg book cash ceil prio state stnum stname sd; do
    reset_sb; eval "STUB_ACCT_SpaceX=chg_$fld run_wrap"
    ck "F-$fld: đổi $fld của TV1 → (b) giữ plan mới"          notF SpaceX
    ck "F-$fld: (b) đã gỡ approved_by"                         hasnt "$(P SpaceX)" "approved_by"
    ck "F-$fld: ZaloPay (không đổi) vẫn (a)"                   sameF ZaloPay
  done
  fi

  # ── (b) SpaceX giống, ZaloPay KHÁC ──
  if sec b; then
  reset_sb; STUB_ACCT_ZaloPay=diff run_wrap
  ck "B: rc=0"                                   eq "$(rcv)" 0
  ck "B: SpaceX (a) khôi phục thứ Sáu"           sameF SpaceX
  ck "B: ZaloPay giữ plan MỚI (≠ thứ Sáu)"       notF ZaloPay
  ck "B: ZaloPay chưa có approved_by"            hasnt "$(P ZaloPay)" "approved_by"
  ck "B: ZaloPay chưa có mafee_authorized"       hasnt "$(P ZaloPay)" "mafee_authorized"
  ck "B: ZaloPay requires_user_approval=true"    has "$(P ZaloPay)" '"requires_user_approval": true'
  ck "B: diff nêu mã thêm NEW"                   has "$SC/notify.log" "+ BUY NEW x500"
  ck "B: diff nêu lệnh đổi (−/+ AAA)"            has "$SC/notify.log" "− SELL AAA x300"
  ck "B: send_plan_report CHỈ cho ZaloPay"       eq "$(cat "$SC/send.log")" "--account ZaloPay"
  ck "B: SpaceX có dòng 'không đổi'"             has "$SC/notify.log" "plan SpaceX khong doi"
  reset_sb; STUB_ACCT_SpaceX=approved_diff run_wrap
  ck "C: approved_by đã bị gỡ khỏi plan khác"    hasnt "$(P SpaceX)" "approved_by"
  ck "C: mafee_authorized đã bị gỡ"              hasnt "$(P SpaceX)" "mafee_authorized"
  ck "C: approved_at đã bị gỡ"                   hasnt "$(P SpaceX)" "approved_at"
  fi

  if sec c; then
  reset_sb; STUB_JOB_ZaloPay=fail run_wrap
  ck "D: rc=1 (có (c))"                          eq "$(rcv)" 1
  ck "D: ZaloPay khôi phục thứ Sáu"              sameF ZaloPay
  ck "D: SpaceX vẫn xử lý riêng (a)"             sameF SpaceX
  ck "D: bus error cho ZaloPay"                  has "$SC/bus.log" "sunday-plan-round-ZaloPay-2026-10-19"
  ck "D: bus error là JSON hợp lệ (json.dumps)"  python3 -c "import json,sys;[json.loads(l.split(' ',3)[3]) for l in open(sys.argv[1]) if l.strip()]" "$SC/bus.log"
  ck "D: bus KHÔNG error cho SpaceX"             hasnt "$SC/bus.log" "sunday-plan-round-SpaceX"
  ck "D: lý do thật trích từ status job (§29)"   has "$SC/notify.log" "stub error boom"
  ck "D: thông báo nói rõ đã khôi phục thứ Sáu"  has "$SC/notify.log" "DA KHOI PHUC plan thu Sau"
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=run run_wrap
  ck "E: rc=1"                                   eq "$(rcv)" 1
  ck "E: job quá hạn bị cancel"                  has "$SC/cancel.log" "JOB_SpaceX"
  ck "E: job chạy bình thường KHÔNG bị cancel"   hasnt "$SC/cancel.log" "JOB_ZaloPay"
  ck "E: SpaceX khôi phục thứ Sáu"               sameF SpaceX
  ck "E: lý do nêu timeout"                      has "$SC/notify.log" "chua xong sau 2s"
  ck "E: bản ghi job đọc lại = cancelled → 'DA XAC MINH'" has "$SC/notify.log" "DA XAC MINH: status=cancelled"
  reset_sb; STUB_ACCT_SpaceX=none run_wrap
  ck "F: rc=1"                                   eq "$(rcv)" 1
  ck "F: SpaceX giữ thứ Sáu"                     sameF SpaceX
  ck "F: lý do nêu 'khong doi byte'"             has "$SC/notify.log" "khong doi byte"
  reset_sb; STUB_ACCT_ZaloPay=bad run_wrap
  ck "G: JSON hỏng → khôi phục thứ Sáu"          sameF ZaloPay
  ck "G: lý do nêu JSON hong"                    has "$SC/notify.log" "JSON hong"
  reset_sb; STUB_ACCT_SpaceX=wrongdate run_wrap
  ck "G2: plan_date sai → khôi phục thứ Sáu"     sameF SpaceX
  # qty không phải int dương → plan mới không hợp lệ
  reset_sb; STUB_ACCT_SpaceX=diff run_wrap >/dev/null; python3 - "$(P SpaceX)" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); p["orders"][0]["qty"] = "300"; json.dump(p, open(sys.argv[1], "w"))
PY
  ck "G3: validate từ chối qty là chuỗi" python3 - "$LIBF" "$(P SpaceX)" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("l", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
p, err = m.validate_plan(sys.argv[2], "SpaceX", "2026-10-19"); sys.exit(0 if p is None and "qty" in err else 1)
PY
  reset_sb; STUB_FRESH_RC=1 run_wrap
  ck "H: rc=1"                                   eq "$(rcv)" 1
  ck "H: cả hai khôi phục thứ Sáu"               eq "$(md5of "$(P SpaceX)")$(md5of "$(P ZaloPay)")" "$(md5of "$(F SpaceX)")$(md5of "$(F ZaloPay)")"
  ck "H: không chạy injector nào"                eq "$(wc -c <"$SC/inj.log" | tr -d ' ')" 0
  ck "H: lý do thật từ log freshness (§29)"      has "$SC/notify.log" "stub macro boom"
  reset_sb; rm "$(P ZaloPay)"; STUB_ACCT_ZaloPay=diff run_wrap
  ck "I: không có thứ Sáu + plan mới hợp lệ → (b) giữ plan mới" test -f "$(P ZaloPay)"
  ck "I: thông báo plan MỚI (thứ Sáu không có)"  has "$SC/notify.log" "thu Sau khong co plan"
  ck "I: gửi báo cáo cho ZaloPay"                has "$SC/send.log" "--account ZaloPay"
  reset_sb; rm "$(P ZaloPay)"; STUB_ACCT_ZaloPay=none run_wrap
  ck "I2: không thứ Sáu + không plan mới → (c), không có file" test ! -e "$(P ZaloPay)"
  ck "I2: bus error"                             has "$SC/bus.log" "sunday-plan-round-ZaloPay"
  ck "I2: SpaceX vẫn riêng (a)"                  sameF SpaceX
  reset_sb; STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff STUB_INJ_FAIL=inject_discretionary_orders.sh run_wrap
  ck "J: rc=1"                                   eq "$(rcv)" 1
  ck "J: cả hai khôi phục thứ Sáu"               eq "$(md5of "$(P SpaceX)")$(md5of "$(P ZaloPay)")" "$(md5of "$(F SpaceX)")$(md5of "$(F ZaloPay)")"
  ck "J: lý do nêu injector"                     has "$SC/notify.log" "inject_discretionary_orders.sh rc=1"
  ck "J: vẫn chạy hết các injector còn lại"      has "$SC/inj.log" "auto_exit_inject_daily.sh"
  ck "J: không gửi báo cáo plan"                 eq "$(wc -c <"$SC/send.log" | tr -d ' ')" 0
  fi

  # ── HIGH-1/2: job DollarBill ghi muộn / trạng thái chờ-resume ──
  if sec jobs; then
  # (1) quá hạn: cancel thật + writer nền bị giết ⇒ plan KHÔNG bị ghi đè sau khi đã khôi phục
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=run STUB_LATE_SpaceX=6 run_wrap; sleep 8
  ck "J1: job timeout + writer muộn: SpaceX vẫn = thứ Sáu SAU khi writer lẽ ra đã ghi" sameF SpaceX
  ck "J1: cancel rc thật (0) được lưu"            has "$SC/notify.log" "cancel rc=0"
  # (2) freshness FAIL sau khi đã dispatch: vẫn phải cancel job
  reset_sb; STUB_FRESH_RC=1 STUB_DISPATCH_BEFORE_FAIL=1 STUB_JOB_SpaceX=run STUB_JOB_ZaloPay=run STUB_LATE_SpaceX=6 STUB_LATE_ZaloPay=6 run_wrap; sleep 8
  ck "J2: freshness rc≠0 sau dispatch: job SpaceX bị cancel"  has "$SC/cancel.log" "JOB_SpaceX"
  ck "J2: job ZaloPay bị cancel"                   has "$SC/cancel.log" "JOB_ZaloPay"
  ck "J2: SpaceX vẫn = thứ Sáu sau writer muộn"    sameF SpaceX
  ck "J2: ZaloPay vẫn = thứ Sáu sau writer muộn"   sameF ZaloPay
  # (3) rc thật của cancel: process sống sót (rc=5) ⇒ báo rc=5 và KHÔNG báo đã xác minh; ghi bus
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=run STUB_CANCEL_RC=5 run_wrap
  ck "J3: notify nêu cancel rc=5 (không phải 0)"   has "$SC/notify.log" "cancel rc=5"
  ck "J3: job còn sống ⇒ UNSETTLED ⇒ cảnh báo không xác minh" has "$SC/notify.log" "KHONG xac minh duoc job DollarBill da dung"
  ck "J3: bus error nêu job_unsettled"             has "$SC/bus.log" "job_unsettled"
  ck "J3: KHÔNG có câu 'DA XAC MINH'"              hasnt "$SC/notify.log" "DA XAC MINH"
  # (4) usage_limited + còn bản ghi resume: cancel no-op ⇒ gỡ pending_resumes rồi mới coi là dừng
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=usage run_wrap
  ck "J4: bản ghi bus/pending_resumes đã bị gỡ"     test ! -e "$SC/bus/pending_resumes/JOB_SpaceX.json"
  ck "J4: bản ghi gỡ được cất lại làm chứng cứ"     test -e "$SC/state/2026-10-19/pending_removed/JOB_SpaceX.json"
  ck "J4: xác minh ghi 'DA GO ban ghi resume'"      has "$SC/notify.log" "DA GO ban ghi resume"
  ck "J4: SpaceX = thứ Sáu"                         sameF SpaceX
  # (5) usage_limited nhưng bản ghi resume ĐÃ MẤT ⇒ không xác minh được ⇒ escalate, không báo "đã huỷ"
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=usage_nopend run_wrap
  ck "J5: không xác minh được ⇒ job_unsettled trên bus" has "$SC/bus.log" "job_unsettled"
  ck "J5: thông báo nêu resume có thể đã bắn"          has "$SC/notify.log" "resume co the DA ban thanh job moi"
  ck "J5: không nói 'DA XAC MINH'"                     hasnt "$SC/notify.log" "DA XAC MINH"
  ck "J5: plan thứ Sáu vẫn được khôi phục"             sameF SpaceX
  # (6) retrying: cancel là no-op ⇒ job còn sống ⇒ unsettled
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=retrying run_wrap
  ck "J6: retrying còn sống ⇒ job_unsettled"           has "$SC/bus.log" "job_unsettled"
  ck "J6: cancel được thử lại (≥2 lần, SPR_CANCEL_TRIES=2)" test "$(grep -c JOB_SpaceX "$SC/cancel.log")" -ge 2
  # (7) TERM khi job nền còn sống: trap chạy NGAY (không chờ lệnh foreground), cancel job, khôi phục
  reset_sb; T0=$(date +%s)
  run_bg env STUB_KILL=termlong STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff STUB_JOB_SpaceX=run STUB_LATE_SpaceX=6
  T1=$(date +%s)
  ck "J7: wrapper thoát < 12s sau TERM (stub bq ngủ 25s)" test $((T1 - T0)) -lt 12
  ck "J7: guard đã cancel job nền"                     has "$SC/cancel.log" "JOB_SpaceX"
  sleep 7
  ck "J7: SpaceX = thứ Sáu sau writer muộn"             sameF SpaceX
  ck "J7: ZaloPay = thứ Sáu"                            sameF ZaloPay
  ck "J7: thông báo bị NGẮT"                            has "$SC/notify.log" "bị NGẮT"
  # (8) fd khoá không lọt vào tiến trình con
  reset_sb; run_wrap
  ck "J8: fd 9 (flock) ĐÓNG trong bq_freshness"         has "$SC/bq_env.log" "fd9=closed"
  # (9) guard trung thực: thoát bất thường khi mọi account đã quyết định ⇒ KHÔNG nói "đã khôi phục"
  reset_sb; : >"$SC/wrapper.pid"
  run_bg env STUB_KILL_AT_SEND=term STUB_ACCT_ZaloPay=diff
  ck "J9: guard không bịa 'đã khôi phục' khi không còn gì để khôi phục" hasnt "$SC/notify.log" "đã khôi phục plan thứ Sáu từ stash"
  ck "J9: guard nói rõ KHÔNG có account nào cần khôi phục" has "$SC/notify.log" "KHÔNG có account nào cần khôi phục"
  ck "J9: plan (b) của ZaloPay KHÔNG bị guard chép đè"   notF ZaloPay
  fi

  # ── park (MED-5) ──
  if sec park; then
  reset_sb; echo '{"decision":"TRIM","orders":[{"ticker":"E1VFVN30","side":"sell","qty":1300}],"blocked":[]}' > "$SC/plans/park_trim_SpaceX_2026-10-19.json"
  STUB_ACCT_SpaceX=diff run_wrap
  ck "PK1: L1 có qty>0 → ép (c), giữ plan thứ Sáu"       sameF SpaceX
  ck "PK1: lý do thật nêu artifact + tổng qty"          has "$SC/notify.log" "park_trim_SpaceX_2026-10-19.json[orders] co 1 muc, tong qty=1300"
  ck "PK1: nêu chuỗi park bỏ qua cuối tuần"             has "$SC/notify.log" "tu bo qua cuoi tuan"
  ck "PK1: ZaloPay (artifact rỗng) vẫn so sánh bình thường → (a)" sameF ZaloPay
  reset_sb; echo '{"decision":"JIT","orders":[],"buy_amendments":[{"ticker":"X","qty":100}]}' > "$SC/plans/jit_unpark_ZaloPay_2026-10-19.json"
  STUB_ACCT_ZaloPay=diff run_wrap
  ck "PK2: L2 buy_amendments không rỗng → ép (c)"        sameF ZaloPay
  reset_sb; rm "$SC/plans/park_trim_SpaceX_2026-10-19.json"; STUB_ACCT_SpaceX=diff run_wrap
  ck "PK3: artifact L1 VẮNG → ép (c) (không biết)"       sameF SpaceX
  ck "PK3: lý do nêu VANG"                               has "$SC/notify.log" "VANG"
  reset_sb; STUB_ACCT_ZaloPay=diff run_wrap
  ck "PK4: artifact RỖNG → (b) tiếp tục như cũ"           notF ZaloPay
  fi

  # ── MED-3: lỗi cô lập theo account ──
  if sec isolation; then
  reset_sb; SPR_FAULT_DECIDE=SpaceX STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff run_wrap
  ck "ISO1: SpaceX crash → khôi phục RIÊNG thứ Sáu"       sameF SpaceX
  ck "ISO1: thông báo 'DA KHOI PHUC RIENG'"               has "$SC/notify.log" "DA KHOI PHUC RIENG"
  ck "ISO1: ZaloPay KHÔNG bị kéo theo: vẫn giữ plan MỚI (b)" notF ZaloPay
  ck "ISO1: ZaloPay (b) được gửi báo cáo"                 has "$SC/send.log" "--account ZaloPay"
  ck "ISO1: bus error SpaceX"                             has "$SC/bus.log" "sunday-plan-round-SpaceX-2026-10-19"
  # crash mà KHÔNG khôi phục được (stash bị mất) ⇒ RESULT=x, tuyệt đối không nói đã khôi phục
  reset_sb; STUB_BREAK_STASH_ZaloPay=1 STUB_ACCT_ZaloPay=none run_wrap
  ck "ISO2: không khôi phục được ⇒ rc=1"                  eq "$(rcv)" 1
  ck "ISO2: thông báo 'khong khoi phuc duoc'"             has "$SC/notify.log" "khong khoi phuc duoc"
  ck "ISO2: bus decide_crash_unrestored"                  has "$SC/bus.log" "decide_crash_unrestored"
  ck "ISO2: SpaceX không bị ảnh hưởng"                    sameF SpaceX
  # decide của SpaceX chết TRƯỚC khi in RESULT (shim lib): không nuốt output, không recover cả loạt
  reset_sb
  cat >"$SC/stubs/libshim.py" <<'S'
#!/usr/bin/env python3
import os, runpy, sys
if "decide" in sys.argv and "SpaceX" in sys.argv:
    print("Traceback: boom-shim-decide"); sys.exit(1)
sys.argv[0] = os.environ["SPR_REAL_LIB"]
runpy.run_path(os.environ["SPR_REAL_LIB"], run_name="__main__")
S
  SPR_REAL_LIB="$LIBF" SPR_LIB="$SC/stubs/libshim.py" STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff run_wrap
  ck "ISO3: output thật của decide lỗi được báo (không nuốt)" has "$SC/notify.log" "boom-shim-decide"
  ck "ISO3: không khẳng định đã khôi phục SpaceX"          has "$SC/notify.log" "CHƯA khẳng định đã khôi phục"
  ck "ISO3: recover RIÊNG SpaceX → thứ Sáu"               sameF SpaceX
  ck "ISO3: ZaloPay KHÔNG bị recover-cả-loạt: giữ plan mới" notF ZaloPay
  fi

  # ── stash idempotent (MED-2) ──
  if sec stash; then
  reset_sb; STUB_ACCT_ZaloPay=diff run_wrap
  ck "ST0: tiền đề — lượt 1: ZaloPay giữ plan mới (b)"    notF ZaloPay
  run_wrap     # lượt 2 (chạy lại tay): đĩa đang là plan (b) — stash PHẢI vẫn là thứ Sáu gốc
  ck "ST1: lượt 2 in STASH-REUSE"                         has "$SC/out.log" "STASH-REUSE ZaloPay"
  ck "ST1: lượt 2 (stub 'same') → (a) khôi phục thứ Sáu GỐC (không phải plan (b))" sameF ZaloPay
  ck "ST1: stash gốc còn nguyên md5 thứ Sáu"              eq "$(md5of "$SC/state/2026-10-19/stash/plan_ZaloPay_2026-10-19.json")" "$(md5of "$(F ZaloPay)")"
  ck "ST1: manifest lượt 1 được cất thành manifest.prev"  test "$(ls "$SC/state/2026-10-19"/manifest.prev.*.json 2>/dev/null | wc -l)" -ge 1
  # stash gốc hỏng ⇒ DỪNG, không tự chụp lại
  rm -f "$SC/state/2026-10-19/stash/plan_ZaloPay_2026-10-19.json"
  run_wrap
  ck "ST2: stash gốc mất ⇒ wrapper rc=1, không chụp đè"   eq "$(rcv)" 1
  ck "ST2: thông báo STASH lỗi"                           has "$SC/notify.log" "STASH lỗi"
  fi

  # ── kill -9 / recover trước cổng / manifest cũ ──
  if sec recover; then
  reset_sb
  run_bg env STUB_KILL=kill9 STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff
  sleep 1.5
  ck "K: tiền đề — sau kill -9 plan đang là bản MỚI (≠ thứ Sáu)" notF SpaceX
  ck "K: manifest còn phase=running"             has "$SC/state/2026-10-19/manifest.json" '"phase": "running"'
  : >"$SC/notify.log"
  STUB_FRESH_RC=1 run_wrap
  ck "K: lần chạy sau thông báo đã khôi phục"    has "$SC/notify.log" "KHÔI PHỤC plan thứ Sáu từ stash"
  ck "K: SpaceX về đúng file thứ Sáu"            sameF SpaceX
  ck "K: ZaloPay về đúng file thứ Sáu"           sameF ZaloPay
  # MED-1: recover chạy TRƯỚC cổng ngày — thứ Bảy (gate SKIP) vẫn khôi phục manifest ntd>=hôm nay
  reset_sb
  run_bg env STUB_KILL=kill9 STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff
  sleep 1.5
  MIKE_NOW_ICT="2026-10-17T19:00:00" run_wrap
  ck "K2: thứ Bảy (gate SKIP) vẫn khôi phục SpaceX"  sameF SpaceX
  ck "K2: thứ Bảy vẫn khôi phục ZaloPay"             sameF ZaloPay
  ck "K2: log vẫn có SKIP của gate"                  has "$SC/out.log" "SKIP"
  # MED-1: manifest tuần cũ KHÔNG được chép đè plan đã thực thi
  reset_sb; mkdir -p "$SC/state/2026-10-12/stash"
  echo '{"plan_date":"2026-10-12","account":"SpaceX","orders":[]}' > "$SC/state/2026-10-12/stash/plan_SpaceX_2026-10-12.json"
  echo '{"EXECUTED":"plan da thuc thi 10-12"}' > "$SC/plans/plan_SpaceX_2026-10-12.json"
  python3 - "$SC" <<'PY'
import hashlib, json, sys
sc = sys.argv[1]
st = f"{sc}/state/2026-10-12/stash/plan_SpaceX_2026-10-12.json"
md5 = hashlib.md5(open(st, "rb").read()).hexdigest()
json.dump({"ntd": "2026-10-12", "phase": "running", "plan_dir": f"{sc}/plans",
           "accounts": {"SpaceX": {"had_friday": True, "md5": md5, "stash": st, "decided": None}}}, open(f"{sc}/state/2026-10-12/manifest.json", "w"))
PY
  EXEC_MD5="$(md5of "$SC/plans/plan_SpaceX_2026-10-12.json")"
  run_wrap
  ck "K3: manifest tuần cũ: plan đã thực thi KHÔNG bị chép đè" eq "$(md5of "$SC/plans/plan_SpaceX_2026-10-12.json")" "$EXEC_MD5"
  ck "K3: manifest cũ đánh dấu stale_skipped"            has "$SC/state/2026-10-12/manifest.json" "stale_skipped"
  ck "K3: log nêu RECOVER-SKIP"                          has "$SC/out.log" "RECOVER-SKIP"
  ck "K3: vòng tuần này vẫn chạy bình thường"            has "$SC/state/2026-10-19/manifest.json" '"phase": "done"'
  # TERM giữa chừng (job ok): trap tự khôi phục ngay
  reset_sb
  run_bg env STUB_KILL=term STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff
  sleep 1
  ck "L: sau TERM, SpaceX về thứ Sáu (trap)"     sameF SpaceX
  ck "L: sau TERM, ZaloPay về thứ Sáu (trap)"    sameF ZaloPay
  ck "L: thông báo bị ngắt"                      has "$SC/notify.log" "bị NGẮT"
  fi

  # ── lock ──
  if sec lock; then
  reset_sb
  ( exec 8>"$SC/state/.lock"; flock 8; MIKE_NOW_ICT="$MIKE_NOW_ICT" bash "$WRAP" >"$SC/out.log" 2>&1; echo $? >"$SC/rc" )
  ck "M: bị khoá → thoát rc=0 và nêu lock"       eq "$(rcv)" 0
  ck "M: bị khoá → log có chữ lock"              has "$SC/out.log" "lock"
  fi

  # ── kiểm cuối đêm --verify ──
  if sec verify; then
  reset_sb; run_wrap
  : >"$SC/notify.log"; run_wrap --verify
  ck "V0: verify sạch (sau (a)) → rc=0"                  eq "$(rcv)" 0
  ck "V0: verify in VERIFY-OK"                           has "$SC/out.log" "VERIFY-OK SpaceX"
  # plan thứ Sáu đã duyệt bị job muộn ghi đè NỘI DUNG (mang theo dấu duyệt cũ) ⇒ phải gỡ duyệt + rc=4 + escalate
  python3 "$SC/stubs/writeplan.py" "$(P SpaceX)" late SpaceX
  ck "V1: tiền đề — plan bị ghi muộn còn approved_by"    has "$(P SpaceX)" "approved_by"
  run_wrap --verify
  ck "V1: verify rc=4"                                   eq "$(rcv)" 4
  ck "V1: dấu duyệt bị gỡ"                               hasnt "$(P SpaceX)" "approved_by"
  ck "V1: mafee_authorized bị gỡ"                        hasnt "$(P SpaceX)" "mafee_authorized"
  ck "V1: requires_user_approval=true"                   has "$(P SpaceX)" '"requires_user_approval": true'
  ck "V1: nêu approved_by TRƯỚC khi gỡ (đọc thật)"       has "$SC/out.log" "approved_by='user (Discord 2026-10-16)'"
  ck "V1: notify KIỂM CUỐI ĐÊM"                          has "$SC/notify.log" "KIỂM CUỐI ĐÊM"
  ck "V1: bus error sunday-plan-round-verify"            has "$SC/bus.log" "sunday-plan-round-verify"
  ck "V1: ZaloPay (không lệch) không bị đụng"            sameF ZaloPay
  # người dùng duyệt (b) = chỉ đổi trường duyệt ⇒ KHÔNG phải lệch
  reset_sb; STUB_ACCT_ZaloPay=diff run_wrap
  set_key "$(P ZaloPay)" approved_by '"user (Discord 2026-10-19 07:30)"'; set_key "$(P ZaloPay)" requires_user_approval false
  run_wrap --verify
  ck "V2: user duyệt plan (b) sau quyết định → verify rc=0"   eq "$(rcv)" 0
  ck "V2: dấu duyệt của user được GIỮ"                        has "$(P ZaloPay)" "user (Discord 2026-10-19 07:30)"
  # file vắng
  rm -f "$(P SpaceX)"; run_wrap --verify
  ck "V3: file plan biến mất → rc=4"                      eq "$(rcv)" 4
  ck "V3: nêu FILE VANG"                                  has "$SC/out.log" "FILE VANG"
  # không có manifest nào ⇒ no-op
  reset_sb; run_wrap --verify
  ck "V4: không có state → rc=0, không notify"            eq "$(rcv)$(wc -c <"$SC/notify.log" | tr -d ' ')" 00
  # manifest tuần cũ không bị verify
  reset_sb; run_wrap; MIKE_NOW_ICT="2026-10-26T08:30:00" run_wrap --verify
  ck "V5: ntd < hôm nay → bỏ qua, rc=0"                   eq "$(rcv)" 0
  # --second-chance = verify + gửi lại (trong cửa sổ), và NHẢ khi ngoài cửa sổ
  reset_sb; run_wrap; : >"$SC/send.log"; run_wrap --second-chance
  ck "V6: second-chance trong cửa sổ → gọi send_plan_report --second-chance" has "$SC/send.log" "--second-chance"
  : >"$SC/send.log"; MIKE_NOW_ICT="2026-12-06T23:00:00" run_wrap --second-chance
  ck "V7: second-chance ngoài mùa BCTC → KHÔNG gửi"       eq "$(wc -c <"$SC/send.log" | tr -d ' ')" 0
  # manifest còn 'running' (vòng bị ngắt) khi verify chạy ⇒ recover trước
  reset_sb; run_bg env STUB_KILL=kill9 STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff; sleep 1.5
  run_wrap --verify
  ck "V8: manifest running → verify tự recover (SpaceX = thứ Sáu)" sameF SpaceX
  fi

  # ── bq_freshness_check: MORNING_NOTE mặc định KHÔNG đổi byte so với bản gốc d570de2c9 (hành vi T2-T6) ──
  if sec note; then
  note_of() {  # note_of <file-or-git> : chạy riêng dòng gán MORNING_NOTE
    bash -c 'TODAY=2026-10-16; CAL_TODAY=2026-10-18; NEXT_TRADING_DAY=2026-10-19; line="$(grep -n "^  MORNING_NOTE=" "$1" | head -1 | cut -d: -f1)"; eval "$(sed -n "${line}p" "$1")"; printf "%s" "$MORNING_NOTE"' _ "$1"
  }
  if git -C "$HERE/.." cat-file -e d570de2c9:bin/bq_freshness_check.sh 2>/dev/null; then
    git -C "$HERE/.." show d570de2c9:bin/bq_freshness_check.sh >"/tmp/bq_fresh_base.$$"
    ck "N1: MORNING_NOTE mặc định giống HỆT bản gốc d570de2c9" eq "$(note_of "$HERE/bq_freshness_check.sh")" "$(note_of "/tmp/bq_fresh_base.$$")"
    rm -f "/tmp/bq_fresh_base.$$"
  fi
  ck "N2: NOTE_TAIL ghi đè được qua env" eq "$(MIKE_MORNING_NOTE_TAIL=XYZ note_of "$HERE/bq_freshness_check.sh" | grep -c 'CHÍNH ngày 2026-10-19. XYZ')" 1
  fi

  # ── dọn state cũ ──
  if sec prune; then
  reset_sb
  for d in 2026-09-07 2026-09-14 2026-09-21; do mkdir -p "$SC/state/$d"; echo '{"ntd":"'$d'","phase":"done","accounts":{}}' >"$SC/state/$d/manifest.json"; done
  SPR_KEEP_WEEKS=2 run_wrap
  ck "PR1: tuần cũ (done) bị xoá"                         test ! -d "$SC/state/2026-09-07"
  ck "PR1: tuần cũ (done) thứ 2 bị xoá"                   test ! -d "$SC/state/2026-09-14"
  ck "PR1: tuần gần giữ lại"                              test -d "$SC/state/2026-10-19"
  ck "PR1: tuần thứ 2 gần nhất giữ lại (KEEP=2)"          test -d "$SC/state/2026-09-21"
  fi

  REAL_AFTER="$(find "$WC/data/trade_plans" -type f -printf '%p %T@\n' 2>/dev/null | md5sum)"
  ck "plan THẬT (data/trade_plans) không đổi mtime/ds file" eq "$REAL_BEFORE" "$REAL_AFTER"
  rm -rf "$SC"; SC=""
  echo "   $TZNOTE: pass=$PASS fail=$FAIL"
}

# ── mutant ──────────────────────────────────────────────────────────────────────────────────
mutate() {  # mutate <src> <dst> <old> <new>  (old phải xuất hiện đúng 1 lần)
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
old, new = sys.argv[3], sys.argv[4]
if s.count(old) != 1:
    sys.exit(f"mutant sai: '{old[:60]}' xuất hiện {s.count(old)} lần")
open(sys.argv[2], "w", encoding="utf-8").write(s.replace(old, new))
PY
}

if [ "${SC_PHASE:-}" = "suite" ]; then suite; echo "RESULT pass=$PASS fail=$FAIL"; [ "$FAIL" = 0 ]; exit $?; fi

# ── điều phối: 3 TZ (§16) ──
LEAK_BEFORE="$(ls -d /tmp/spr_sc.* /tmp/spr_mut.* 2>/dev/null | wc -l)"
TOTAL_FAIL=0; TOTAL_PASS=0
for tzmode in unset America/Los_Angeles Pacific/Kiritimati; do
  if [ "$tzmode" = unset ]; then out="$(env -u TZ SC_PHASE=suite bash "$SELF" 2>&1)"; else out="$(TZ=$tzmode SC_PHASE=suite bash "$SELF" 2>&1)"; fi
  echo "$out" | grep -E '✗|== suite|pass=' | grep -v '^RESULT'
  p="$(echo "$out" | sed -n 's/^RESULT pass=\([0-9]*\) fail=.*/\1/p')"; f="$(echo "$out" | sed -n 's/^RESULT pass=[0-9]* fail=\([0-9]*\)/\1/p')"
  if [ -z "$f" ]; then f=1; echo "  ✗ suite ($tzmode) không in RESULT:"; echo "$out" | tail -5; fi
  TOTAL_FAIL=$((TOTAL_FAIL + f)); TOTAL_PASS=$((TOTAL_PASS + ${p:-0}))
done
echo "== TỔNG 3 TZ: pass=$TOTAL_PASS fail=$TOTAL_FAIL =="

[ -n "${SC_NO_MUTANTS:-}" ] && { [ "$TOTAL_FAIL" = 0 ]; exit $?; }

MD="$(mktemp -d /tmp/spr_mut.XXXXXX)"; ALIVE=0; DEAD=0
run_mut() {  # run_mut <tên> <sections> <lib|sh> <old> <new>   (SC_MUT_ONLY=<regex> chỉ chạy mutant khớp tên)
  local name="$1" sections="$2" kind="$3" old="$4" new="$5"
  [ -n "${SC_MUT_ONLY:-}" ] && ! [[ "$name" =~ $SC_MUT_ONLY ]] && return
  local mlib="$LIBF" mwrap="$WRAP"
  if [ "$kind" = lib ]; then mlib="$MD/lib_$name.py"; mutate "$LIBF" "$mlib" "$old" "$new" || { echo "  ✗ $name: không dựng được mutant"; ALIVE=$((ALIVE+1)); return; }
  else mwrap="$MD/wrap_$name.sh"; mutate "$WRAP" "$mwrap" "$old" "$new" || { echo "  ✗ $name: không dựng được mutant"; ALIVE=$((ALIVE+1)); return; }
       # wrapper đột biến phải thấy cùng thư mục với lib/injector thật
       sed -i "s#HERE=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")\" \&\& pwd)\"#HERE=\"$HERE\"#" "$mwrap"; fi
  local out; out="$(env -u TZ SC_PHASE=suite SC_SECTIONS="$sections" FAIL_FAST=1 SC_WRAP="$mwrap" SC_LIB="$mlib" bash "$SELF" 2>&1)"
  if echo "$out" | grep -q '✗'; then DEAD=$((DEAD+1)); echo "  mutant CHẾT  : $name  ($(echo "$out" | grep '✗' | head -1 | sed 's/^ *✗ FAIL: //' | cut -c1-70))"
  else ALIVE=$((ALIVE+1)); echo "  mutant SỐNG ✗: $name — suite vẫn PASS!"; fi
}
echo "== MUTANT =="
# vòng 1 (cập nhật theo mã mới)
run_mut M1-so-sanh-dao        "a b" lib 'if not removed and not added and not head_diff:' 'if removed or added or head_diff:'
run_mut M2-bo-khoi-phuc-c     "c"   lib '            _restore(plan_dir, ntd, acct, ent, run_dir)
            return finish("c", f"❌ {acct}: KHONG co plan moi' '            return finish("c", f"❌ {acct}: KHONG co plan moi'
run_mut M3-gate-CN-dao        "noop" lib 'if today.weekday() != 6:' 'if today.weekday() == 6:'
run_mut M4-bo-recover-truoc-cong "recover" sh 'REC="$(recover_all)"; rrc=$?' 'REC=""; rrc=0'
run_mut M5-khong-go-duyet     "b"   lib 'bad = [k for k in plan if _is_approval_key(k)]' 'bad = []'
run_mut M6-timeout-thanh-ok   "c"   sh  'STATUS[$a]="job_timeout"' 'STATUS[$a]="ok"'
run_mut M7-bo-gate-cua-so     "gate" lib 'elif wg[0] != "RUN":' 'elif False:'
run_mut M8-bo-qua-injector-loi "c"  sh  'if [ -n "$INJ_FAIL" ]; then' 'if false; then'
run_mut M9-bo-trap-exit       "recover" sh 'trap _final_guard EXIT' 'trap : EXIT'
run_mut M10-a-khong-khoi-phuc "a"   lib '                _restore(plan_dir, ntd, acct, ent, run_dir)
                return finish("a"' '                return finish("a"'
run_mut M11-khong-cancel-job  "jobs" sh '"$JOBS" cancel "$jid"' ': "$JOBS" cancel "$jid"'
run_mut M12-bo-stash          "a"   sh  'python3 "$LIB" stash --plan-dir' ': "$LIB" stash --plan-dir'
# vòng 2
run_mut M13-cancel-rc-luon-0  "jobs" sh 'CANCEL_RC[$acct]="$crc"' 'CANCEL_RC[$acct]=0'
run_mut M14-khong-go-pending  "jobs" lib '        os.replace(pf, os.path.join(removed_dir, f"{jid}.json"))' '        pass'
run_mut M15-bo-xac-minh-job   "jobs" sh 'settle_jobs "$any_bad"' ': "$any_bad"'
run_mut M16-verify-vo-hieu    "verify" lib 'if want == have and have != "CORRUPT":' 'if True:'
run_mut M17-stash-khong-ke-thua "stash" lib '        if pe is not None:' '        if False:'
run_mut M18-recover-khong-loc-tuan "recover" lib 'if str(m.get("ntd")) < today:
            print(f"RECOVER-SKIP' 'if False:
            print(f"RECOVER-SKIP'
run_mut M19-park-guard-tat    "park" lib '            if blocked:' '            if False:'
run_mut M20-fd9-ro-ri         "jobs" sh '>"$out" 2>&1 9>&- &' '>"$out" 2>&1 &'
run_mut M21-guard-noi-doi     "jobs" sh '  if [ -z "$r" ]; then' '  if false; then'
run_mut M22-decide-khong-bao-account "isolation" lib '        return _crash(plan_dir, run_dir, ntd, acct, ent, e)' '        raise'
run_mut M23-recover-ca-loat   "isolation" sh '--state-dir "$STATE_DIR" --account "$a" 2>&1)"' '--state-dir "$STATE_DIR" 2>&1)"'
run_mut M24-trap-bi-hoan      "jobs" sh '( [ -n "${RW_CD:-}" ] && cd "$RW_CD"; exec "$@" ) >"$out" 2>&1 9>&- &
  CUR_PID=$!
  wait "$CUR_PID"; local rc=$?' '( [ -n "${RW_CD:-}" ] && cd "$RW_CD"; exec "$@" ) >"$out" 2>&1 9>&-; local rc=$?'
run_mut M25-bo-prune          "prune" sh 'python3 "$LIB" prune --state-dir' ': "$LIB" prune --state-dir'
run_mut M26-pending-mat-van-ok "jobs" lib '        if not os.path.exists(pf):
            return False, (f"status={st} nhung' '        if False:
            return False, (f"status={st} nhung'
run_mut M27-freshfail-khong-parse-job "jobs" sh 'while read -r acct jid; do [ -n "$jid" ] && JOBID[$acct]="$jid"; done < <(python3 "$LIB" jobs "$FRESH_LOG" 2>/dev/null)
if [ "$FRESH_RC" -eq 0 ]; then' 'if [ "$FRESH_RC" -eq 0 ]; then'
# so sánh theo phần executor dùng: mỗi trường một mutant
run_mut MF1-bo-qty       "fields" lib 'int(o.qty), _tick(o.ref_price, tk)' '0, _tick(o.ref_price, tk)'
run_mut MF2-bo-ref       "fields" lib '_tick(o.ref_price, tk), str(o.urgency)' '0, str(o.urgency)'
run_mut MF3-bo-urgency   "fields" lib 'str(o.urgency)' '"x"'
run_mut MF4-bo-book      "fields" lib 'str(o.book)' '"x"'
run_mut MF5-bo-cash-only "fields" lib 'bool(o.cash_only)' 'False'
run_mut MF6-bo-tran-gia  "fields" lib '_tick(o.hard_no_chase_ceiling_vnd, tk)' 'None'
run_mut MF7-bo-priority  "fields" lib 'int(o.priority)' '0'
run_mut MF8-bo-state     "fields" lib '"state": plan.state,' '"state": 0,'
run_mut MF8b-bo-state-name "fields" lib '"state_name": plan.state_name,' '"state_name": "x",'
run_mut MF9-bo-signal-date "fields" lib '"signal_date": plan.signal_date}' '"signal_date": "x"}'
run_mut MF10-so-order-type "fields" lib 'str(o.urgency), str(o.book),' 'str(o.urgency), str(o.book), str(getattr(o, "note", "")),'
rm -rf "$MD"; MD=""
LEAK_AFTER="$(ls -d /tmp/spr_sc.* /tmp/spr_mut.* 2>/dev/null | wc -l)"
echo "== MUTANT: chết=$DEAD sống=$ALIVE · tmpdir rò rỉ: trước=$LEAK_BEFORE sau=$LEAK_AFTER =="
[ "$TOTAL_FAIL" = 0 ] && [ "$ALIVE" = 0 ] && [ "$LEAK_AFTER" -le "$LEAK_BEFORE" ]
