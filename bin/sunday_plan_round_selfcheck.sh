#!/usr/bin/env bash
# sunday_plan_round_selfcheck.sh — kiểm bin/sunday_plan_round.sh + sunday_plan_round_lib.py bằng STUB
# (không dispatch DollarBill, không ghi plan thật, không gọi DNSE/BQ/Discord). Mọi plan nằm trong
# thư mục tạm; ngày mô phỏng bằng MIKE_NOW_ICT (§16: chạy lại dưới env -u TZ và TZ ngoại).
#
#   sunday_plan_round_selfcheck.sh            toàn bộ: 3 TZ + mutant   (exit 0 = PASS hết)
#   SC_PHASE=suite sunday_plan_round_selfcheck.sh   chỉ 1 lượt suite dưới env hiện tại
# Mutant: mỗi mutant PHẢI làm suite FAIL; nếu suite vẫn PASS ⇒ mutant "sống" ⇒ selfcheck FAIL.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAP="${SC_WRAP:-$HERE/sunday_plan_round.sh}"
LIBF="${SC_LIB:-$HERE/sunday_plan_round_lib.py}"
SELF="$HERE/$(basename "${BASH_SOURCE[0]}")"
WC="$(cd "$HERE/../.." && pwd)"
export MIKE_BOT_TEST_MODE=1     # §5b — selfcheck này không dựng Executor, nhưng đặt phòng hờ

PASS=0; FAIL=0
ck() {  # ck "tên" <điều kiện bash đã đánh giá rc>
  local name="$1"; shift
  if "$@"; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); echo "  ✗ FAIL: $name"; [ -n "${FAIL_FAST:-}" ] && { echo "RESULT pass=$PASS fail=$FAIL"; exit 1; }; fi
}
eq()  { [ "$1" = "$2" ]; }
has() { grep -qF -- "$2" "$1" 2>/dev/null; }
hasnt() { ! grep -qF -- "$2" "$1" 2>/dev/null; }
md5of() { md5sum "$1" 2>/dev/null | cut -d' ' -f1; }

# ── dựng sandbox ────────────────────────────────────────────────────────────────────────────
mk_sandbox() {
  SC="$(mktemp -d /tmp/spr_sc.XXXXXX)"
  mkdir -p "$SC/plans" "$SC/stubs" "$SC/inj" "$SC/state" "$SC/js"
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
S
  cat >"$SC/stubs/macro.sh" <<'S'
#!/usr/bin/env bash
echo macro-ok
S
  cat >"$SC/stubs/foreach.sh" <<'S'
#!/usr/bin/env bash
"$1"
S
  cat >"$SC/stubs/jobs.sh" <<'S'
#!/usr/bin/env bash
case "$1" in
  status) f="$SC/js/$2"; v="$(cat "$f" 2>/dev/null || echo ok)"
          case "$v" in ok) exit 0;; fail) echo "job $2 FAILED: stub error boom"; exit 1;; run) exit 2;; *) exit 4;; esac ;;
  cancel) echo "$2" >> "$SC/cancel.log"; exit 0 ;;
esac
S
  for s in compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh plan_position_drift_check.py; do
    cat >"$SC/inj/$s" <<S
#!/usr/bin/env bash
echo "$s" >> "\$SC/inj.log"
[ "\${STUB_INJ_FAIL:-}" = "$s" ] && { echo "stub injector boom"; exit 1; }
exit 0
S
  done
  # bq_freshness stub: ghi plan theo STUB_ACCT_<A>, in dòng dispatch như bản thật
  cat >"$SC/stubs/bq.sh" <<'S'
#!/usr/bin/env bash
echo "stub bq_freshness MIKE_MORNING_RUN=${MIKE_MORNING_RUN:-} FORCE=${MIKE_MORNING_FORCE:-}" > "$SC/bq_env.log"
[ "${STUB_FRESH_RC:-0}" != 0 ] && { echo "FAIL DT5G publisher-evidence: stub macro boom"; exit "$STUB_FRESH_RC"; }
for A in $SPR_LABELS; do
  echo "--- [pipeline-4] dispatch DollarBill lập plan T+1 cho $A ---"
  eval "mode=\${STUB_ACCT_$A:-same}"; eval "js=\${STUB_JOB_$A:-ok}"
  echo "$js" > "$SC/js/JOB_$A"
  echo "DISPATCHED DollarBill (job=JOB_$A pid=1) → log: /dev/null"
  python3 - "$SPR_PLAN_DIR/plan_${A}_2026-10-19.json" "$mode" "$A" <<'PY'
import json, sys, os
path, mode, acct = sys.argv[1:4]
base = json.load(open(os.environ["SC"] + "/fri_%s.json" % acct))
if mode == "none": sys.exit(0)
if mode == "bad": open(path, "w").write("{not json"); sys.exit(0)
if mode == "wrongdate": base["plan_date"] = "2026-10-20"
base["created_at"] = "2026-10-18T19:05:00+07:00"
if mode in ("diff", "approved_diff", "wrongdate"):
    base["orders"] = [dict(o) for o in base["orders"]]
    base["orders"][0]["qty"] += 100
    base["orders"].append({"id": "BUY-NEW", "ticker": "NEW", "side": "buy", "qty": 500, "order_type": "LO", "limit_price_vnd": 12340})
if mode != "approved_diff":
    for k in [k for k in base if k.startswith("approv") or k.startswith("mafee")]: del base[k]
    base["requires_user_approval"] = True
if mode == "tickjitter":    # cùng tập lệnh, chỉ khác float dư ở giá → phải coi là GIỐNG
    for o in base["orders"]:
        if o.get("limit_price_vnd"): o["limit_price_vnd"] = o["limit_price_vnd"] + 0.0000001
json.dump(base, open(path, "w"))
PY
done
case "${STUB_KILL:-}" in
  kill9) for i in $(seq 50); do [ -s "$SC/wrapper.pid" ] && break; sleep 0.1; done; kill -9 "$(cat "$SC/wrapper.pid")"; sleep 1 ;;
  term)  for i in $(seq 50); do [ -s "$SC/wrapper.pid" ] && break; sleep 0.1; done; kill -TERM "$(cat "$SC/wrapper.pid")"; sleep 2 ;;
esac
exit 0
S
  chmod +x "$SC"/stubs/*.sh "$SC"/inj/*
  for A in SpaceX ZaloPay; do
    python3 - "$SC/fri_$A.json" "$A" <<'PY'
import json, sys
p = {"plan_date": "2026-10-19", "account": sys.argv[2], "requires_user_approval": False,
     "approved_by": "user (Discord 2026-10-16)", "approved_at": "2026-10-16T21:30:00+07:00", "mafee_authorized": True,
     "created_at": "2026-10-16T19:05:00+07:00",
     "orders": [{"id": "SELL-AAA", "ticker": "AAA", "side": "sell", "qty": 300, "order_type": "LO", "limit_price_vnd": 21050},
                {"id": "BUY-TV1", "ticker": "TV1", "side": "buy", "qty": 300, "order_type": "LO",
                 "limit_price_vnd": 19900, "hard_no_chase_ceiling_vnd": 20000}]}
json.dump(p, open(sys.argv[1], "w"))
PY
    cp "$SC/fri_$A.json" "$SC/plans/plan_${A}_2026-10-19.json"
  done
  export SC SPR_PLAN_DIR="$SC/plans" SPR_STATE_DIR="$SC/state" SPR_INJ_DIR="$SC/inj" SPR_BQ_FRESHNESS="$SC/stubs/bq.sh" \
    SPR_JOBS="$SC/stubs/jobs.sh" SPR_NOTIFY="$SC/stubs/notify.sh" SPR_BUS="$SC/stubs/bus.sh" SPR_SEND_PLAN="$SC/stubs/send.sh" \
    SPR_MACRO_HC="$SC/stubs/macro.sh" SPR_FOR_EACH="$SC/stubs/foreach.sh" SPR_LABELS="SpaceX ZaloPay" SPR_POLL_S=1 \
    SPR_JOB_TIMEOUT=20 SPR_NO_ENV=1 SPR_WINDOW_GATE="$HERE/fa_ratings_earnings_window_daily.sh" WORKDIR_8L="$WC" MIKE_NOW_ICT="2026-10-18T19:00:00" SPR_LIB="$LIBF"
  unset STUB_FRESH_RC STUB_ACCT_SpaceX STUB_ACCT_ZaloPay STUB_JOB_SpaceX STUB_JOB_ZaloPay STUB_KILL STUB_INJ_FAIL
}
reset_sb() { rm -rf "$SC"; mk_sandbox; }
run_wrap() { bash "$WRAP" >"$SC/out.log" 2>&1; echo $? >"$SC/rc"; }
rcv() { cat "$SC/rc"; }
P() { echo "$SC/plans/plan_${1}_2026-10-19.json"; }
F() { echo "$SC/fri_${1}.json"; }

suite() {
  local TZNOTE="TZ=${TZ-<unset>}"
  echo "== suite ($TZNOTE) =="
  REAL_BEFORE="$(find "$WC/data/trade_plans" -type f -printf '%p %T@\n' 2>/dev/null | md5sum)"
  mk_sandbox

  # ── GATE (--check): ngày/cửa sổ/thứ Hai là lễ ──
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

  # ── wrapper sai ngày = no-op im lặng ──
  reset_sb; MIKE_NOW_ICT="2026-10-17T19:00:00" run_wrap
  ck "thứ Bảy: rc=0"                       eq "$(rcv)" 0
  ck "thứ Bảy: không notify"               eq "$(wc -c <"$SC/notify.log" | tr -d ' ')" 0
  ck "thứ Bảy: không tạo stash/state"      eq "$(ls "$SC/state" | wc -l | tr -d ' ')" 0
  ck "thứ Bảy: plan nguyên vẹn"            eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "thứ Bảy: 1 dòng log SKIP"            has "$SC/out.log" "SKIP"
  reset_sb; MIKE_NOW_ICT="2026-12-06T19:00:00" run_wrap
  ck "CN ngoài cửa sổ: rc=0, không notify" eq "$(rcv)$(wc -c <"$SC/notify.log" | tr -d ' ')" 00

  # ── (a) cả hai GIỐNG ──
  reset_sb; run_wrap
  ck "A: rc=0"                                   eq "$(rcv)" 0
  ck "A: SpaceX khôi phục NGUYÊN FILE thứ Sáu (md5 gồm dấu duyệt)" eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "A: ZaloPay khôi phục nguyên file thứ Sáu"  eq "$(md5of "$(P ZaloPay)")" "$(md5of "$(F ZaloPay)")"
  ck "A: notify 'không đổi so với thứ Sáu' SpaceX" has "$SC/notify.log" "plan SpaceX khong doi so voi thu Sau"
  ck "A: notify 'không đổi' ZaloPay"             has "$SC/notify.log" "plan ZaloPay khong doi so voi thu Sau"
  ck "A: có thông báo bắt đầu"                   has "$SC/notify.log" "BẮT ĐẦU"
  ck "A: có thông báo kết thúc"                  has "$SC/notify.log" "XONG"
  ck "A: KHÔNG gọi send_plan_report (plan cũ đã gửi)" eq "$(wc -c <"$SC/send.log" | tr -d ' ')" 0
  ck "A: bus không có error"                     eq "$(wc -c <"$SC/bus.log" | tr -d ' ')" 0
  ck "A: bq_freshness nhận MORNING_RUN=1 FORCE=1" has "$SC/bq_env.log" "MIKE_MORNING_RUN=1 FORCE=1"
  ck "A: injector đúng thứ tự cron" eq "$(tr '\n' ' ' <"$SC/inj.log")" "compute_active_nav_all.sh inject_discretionary_orders.sh auto_exit_inject_daily.sh plan_position_drift_check.py "
  ck "A: manifest phase=done"                    has "$SC/state/2026-10-19/manifest.json" '"phase": "done"'

  # ── jitter float ở giá vẫn là GIỐNG (chuẩn hoá bước giá) ──
  reset_sb; STUB_ACCT_SpaceX=tickjitter run_wrap
  ck "jitter giá: vẫn (a) → file thứ Sáu"        eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"

  # ── (b) SpaceX giống, ZaloPay KHÁC (mỗi account riêng) ──
  reset_sb; STUB_ACCT_ZaloPay=diff run_wrap
  ck "B: rc=0"                                   eq "$(rcv)" 0
  ck "B: SpaceX (a) khôi phục thứ Sáu"           eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "B: ZaloPay giữ plan MỚI (≠ thứ Sáu)"       test "$(md5of "$(P ZaloPay)")" != "$(md5of "$(F ZaloPay)")"
  ck "B: ZaloPay chưa có approved_by"            hasnt "$(P ZaloPay)" "approved_by"
  ck "B: ZaloPay chưa có mafee_authorized"       hasnt "$(P ZaloPay)" "mafee_authorized"
  ck "B: ZaloPay requires_user_approval=true"    has "$(P ZaloPay)" '"requires_user_approval": true'
  ck "B: diff nêu mã thêm NEW"                   has "$SC/notify.log" "+ BUY NEW x500"
  ck "B: diff nêu lệnh đổi (−/+ AAA)"            has "$SC/notify.log" "− SELL AAA x300"
  ck "B: send_plan_report CHỈ cho ZaloPay"       eq "$(cat "$SC/send.log")" "--account ZaloPay"
  ck "B: SpaceX có dòng 'không đổi'"             has "$SC/notify.log" "plan SpaceX khong doi"

  # ── (b') plan sửa-tại-chỗ còn dấu duyệt cũ → phải bị gỡ ──
  reset_sb; STUB_ACCT_SpaceX=approved_diff run_wrap
  ck "C: approved_by đã bị gỡ khỏi plan khác"    hasnt "$(P SpaceX)" "approved_by"
  ck "C: mafee_authorized đã bị gỡ"              hasnt "$(P SpaceX)" "mafee_authorized"
  ck "C: approved_at đã bị gỡ"                   hasnt "$(P SpaceX)" "approved_at"

  # ── (c) DollarBill fail một account ──
  reset_sb; STUB_JOB_ZaloPay=fail run_wrap
  ck "D: rc=1 (có (c))"                          eq "$(rcv)" 1
  ck "D: ZaloPay khôi phục thứ Sáu"              eq "$(md5of "$(P ZaloPay)")" "$(md5of "$(F ZaloPay)")"
  ck "D: SpaceX vẫn xử lý riêng (a)"             eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "D: bus error cho ZaloPay"                  has "$SC/bus.log" "sunday-plan-round-ZaloPay-2026-10-19"
  ck "D: bus KHÔNG error cho SpaceX"             hasnt "$SC/bus.log" "sunday-plan-round-SpaceX"
  ck "D: lý do thật trích từ status job (§29)"   has "$SC/notify.log" "stub error boom"
  ck "D: thông báo nói rõ đã khôi phục thứ Sáu"  has "$SC/notify.log" "DA KHOI PHUC plan thu Sau"

  # ── (c) timeout ──
  reset_sb; SPR_JOB_TIMEOUT=2 STUB_JOB_SpaceX=run run_wrap
  ck "E: rc=1"                                   eq "$(rcv)" 1
  ck "E: job quá hạn bị cancel"                  has "$SC/cancel.log" "JOB_SpaceX"
  ck "E: job chạy bình thường KHÔNG bị cancel"   hasnt "$SC/cancel.log" "JOB_ZaloPay"
  ck "E: SpaceX khôi phục thứ Sáu"               eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "E: lý do nêu timeout"                      has "$SC/notify.log" "chua xong sau 2s"

  # ── (c) plan mới KHÔNG sinh ra (job ok nhưng file không đổi byte) ──
  reset_sb; STUB_ACCT_SpaceX=none run_wrap
  ck "F: rc=1"                                   eq "$(rcv)" 1
  ck "F: SpaceX giữ thứ Sáu"                     eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "F: lý do nêu 'khong doi byte'"             has "$SC/notify.log" "khong doi byte"

  # ── (c) JSON hỏng / sai ngày ──
  reset_sb; STUB_ACCT_ZaloPay=bad run_wrap
  ck "G: JSON hỏng → khôi phục thứ Sáu"          eq "$(md5of "$(P ZaloPay)")" "$(md5of "$(F ZaloPay)")"
  ck "G: lý do nêu JSON hong"                    has "$SC/notify.log" "JSON hong"
  reset_sb; STUB_ACCT_SpaceX=wrongdate run_wrap
  ck "G2: plan_date sai → khôi phục thứ Sáu"     eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"

  # ── (c) bq_freshness fail → tất cả (c), KHÔNG chạy injector ──
  reset_sb; STUB_FRESH_RC=1 run_wrap
  ck "H: rc=1"                                   eq "$(rcv)" 1
  ck "H: cả hai khôi phục thứ Sáu"               eq "$(md5of "$(P SpaceX)")$(md5of "$(P ZaloPay)")" "$(md5of "$(F SpaceX)")$(md5of "$(F ZaloPay)")"
  ck "H: không chạy injector nào"                eq "$(wc -c <"$SC/inj.log" | tr -d ' ')" 0
  ck "H: lý do thật từ log freshness (§29)"      has "$SC/notify.log" "stub macro boom"

  # ── không có plan thứ Sáu ──
  reset_sb; rm "$(P ZaloPay)"; STUB_ACCT_ZaloPay=diff run_wrap
  ck "I: không có thứ Sáu + plan mới hợp lệ → (b) giữ plan mới" test -f "$(P ZaloPay)"
  ck "I: thông báo plan MỚI (thứ Sáu không có)"  has "$SC/notify.log" "thu Sau khong co plan"
  ck "I: gửi báo cáo cho ZaloPay"                has "$SC/send.log" "--account ZaloPay"
  reset_sb; rm "$(P ZaloPay)"; STUB_ACCT_ZaloPay=none run_wrap
  ck "I2: không thứ Sáu + không plan mới → (c), không có file" test ! -e "$(P ZaloPay)"
  ck "I2: bus error"                             has "$SC/bus.log" "sunday-plan-round-ZaloPay"
  ck "I2: SpaceX vẫn riêng (a)"                  eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"

  # ── injector lỗi → plan mới bị coi không đáng tin, khôi phục thứ Sáu ──
  reset_sb; STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff STUB_INJ_FAIL=inject_discretionary_orders.sh run_wrap
  ck "J: rc=1"                                   eq "$(rcv)" 1
  ck "J: cả hai khôi phục thứ Sáu"               eq "$(md5of "$(P SpaceX)")$(md5of "$(P ZaloPay)")" "$(md5of "$(F SpaceX)")$(md5of "$(F ZaloPay)")"
  ck "J: lý do nêu injector"                     has "$SC/notify.log" "inject_discretionary_orders.sh rc=1"
  ck "J: vẫn chạy hết các injector còn lại"      has "$SC/inj.log" "auto_exit_inject_daily.sh"
  ck "J: không gửi báo cáo plan"                 eq "$(wc -c <"$SC/send.log" | tr -d ' ')" 0

  # ── kill -9 giữa chừng rồi chạy lại ──
  reset_sb
  ( STUB_KILL=kill9 STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff bash "$WRAP" >"$SC/out1.log" 2>&1 & echo $! >"$SC/wrapper.pid"; wait ) 2>/dev/null
  sleep 1.5
  ck "K: tiền đề — sau kill -9 plan đang là bản MỚI (≠ thứ Sáu)" test "$(md5of "$(P SpaceX)")" != "$(md5of "$(F SpaceX)")"
  ck "K: manifest còn phase=running"             has "$SC/state/2026-10-19/manifest.json" '"phase": "running"'
  : >"$SC/notify.log"
  STUB_FRESH_RC=1 run_wrap
  ck "K: lần chạy sau thông báo đã khôi phục"    has "$SC/notify.log" "KHÔI PHỤC plan thứ Sáu từ stash"
  ck "K: SpaceX về đúng file thứ Sáu"            eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "K: ZaloPay về đúng file thứ Sáu"           eq "$(md5of "$(P ZaloPay)")" "$(md5of "$(F ZaloPay)")"

  # ── TERM giữa chừng: trap tự khôi phục ngay ──
  reset_sb
  ( STUB_KILL=term STUB_ACCT_SpaceX=diff STUB_ACCT_ZaloPay=diff bash "$WRAP" >"$SC/out1.log" 2>&1 & echo $! >"$SC/wrapper.pid"; wait ) 2>/dev/null
  sleep 1
  ck "L: sau TERM, SpaceX về thứ Sáu (trap)"     eq "$(md5of "$(P SpaceX)")" "$(md5of "$(F SpaceX)")"
  ck "L: sau TERM, ZaloPay về thứ Sáu (trap)"    eq "$(md5of "$(P ZaloPay)")" "$(md5of "$(F ZaloPay)")"
  ck "L: thông báo bị ngắt"                      has "$SC/notify.log" "bị NGẮT"

  # ── lock: lượt thứ hai khi lượt đầu còn chạy → thoát ──
  reset_sb
  ( exec 8>"$SC/state/.lock"; flock 8; MIKE_NOW_ICT="$MIKE_NOW_ICT" bash "$WRAP" >"$SC/out.log" 2>&1; echo $? >"$SC/rc" ) 
  ck "M: bị khoá → thoát rc=0 và nêu lock"       eq "$(rcv)" 0
  ck "M: bị khoá → log có chữ lock"              has "$SC/out.log" "lock"

  # ── plan thật không bị đụng ──
  REAL_AFTER="$(find "$WC/data/trade_plans" -type f -printf '%p %T@\n' 2>/dev/null | md5sum)"
  ck "plan THẬT (data/trade_plans) không đổi mtime/ds file" eq "$REAL_BEFORE" "$REAL_AFTER"
  rm -rf "$SC"
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
run_mut() {  # run_mut <tên> <lib|sh> <old> <new>
  local name="$1" kind="$2" old="$3" new="$4"
  local mlib="$LIBF" mwrap="$WRAP"
  if [ "$kind" = lib ]; then mlib="$MD/lib_$name.py"; mutate "$LIBF" "$mlib" "$old" "$new" || { echo "  ✗ $name: không dựng được mutant"; ALIVE=$((ALIVE+1)); return; }
  else mwrap="$MD/wrap_$name.sh"; mutate "$WRAP" "$mwrap" "$old" "$new" || { echo "  ✗ $name: không dựng được mutant"; ALIVE=$((ALIVE+1)); return; }
       # wrapper đột biến phải thấy cùng thư mục với lib/injector thật
       sed -i "s#HERE=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")\" \&\& pwd)\"#HERE=\"$HERE\"#" "$mwrap"; fi
  local out; out="$(env -u TZ SC_PHASE=suite FAIL_FAST=1 SC_WRAP="$mwrap" SC_LIB="$mlib" bash "$SELF" 2>&1)"
  if echo "$out" | grep -q '✗'; then DEAD=$((DEAD+1)); echo "  mutant CHẾT  : $name  ($(echo "$out" | grep '✗' | head -1 | sed 's/^ *✗ FAIL: //' | cut -c1-70))"
  else ALIVE=$((ALIVE+1)); echo "  mutant SỐNG ✗: $name — suite vẫn PASS!"; fi
}
echo "== MUTANT =="
run_mut M1-so-sanh-dao      lib 'if not removed and not added:' 'if removed or added:'
run_mut M2-bo-khoi-phuc-c   lib '        if ent["had_friday"]:
            _restore(plan_dir, ntd, acct, ent)
            return finish("c"' '        if False:
            _restore(plan_dir, ntd, acct, ent)
            return finish("c"'
run_mut M3-gate-CN-dao      lib 'if today.weekday() != 6:' 'if today.weekday() == 6:'
run_mut M4-bo-recover-dau   sh  'REC="$(python3 "$LIB" recover' 'REC="$(: "$LIB" recover'
run_mut M5-khong-go-duyet   lib 'bad = [k for k in plan if k.startswith("approv") or k.startswith("mafee")]' 'bad = []'
run_mut M6-timeout-thanh-ok sh  'STATUS[$a]="job_timeout"' 'STATUS[$a]="ok"'
run_mut M7-bo-gate-cua-so   lib 'elif wg[0] != "RUN":' 'elif False:'
run_mut M8-bo-qua-injector-loi sh 'if [ -n "$INJ_FAIL" ]; then' 'if false; then'
run_mut M9-bo-trap-exit     sh  'trap _final_guard EXIT' 'trap : EXIT'
run_mut M10-a-khong-khoi-phuc lib '            _restore(plan_dir, ntd, acct, ent)
            return finish("a"' '            return finish("a"'
run_mut M11-khong-cancel-job sh '"$JOBS" cancel' ': "$JOBS" cancel'
run_mut M12-bo-stash        sh  'python3 "$LIB" stash --plan-dir' ': "$LIB" stash --plan-dir'
rm -rf "$MD"
echo "== MUTANT: chết=$DEAD sống=$ALIVE =="
[ "$TOTAL_FAIL" = 0 ] && [ "$ALIVE" = 0 ]
