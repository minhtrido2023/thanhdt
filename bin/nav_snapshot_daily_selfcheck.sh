#!/usr/bin/env bash
# nav_snapshot_daily_selfcheck.sh — hồi quy HÀNH VI cho bin/nav_snapshot_daily.sh (aria-G).
# Chạy bản THẬT của wrapper (copy nguyên file) trong sandbox cây giả: nav_history + dnse_raw giả,
# daily_nav_snapshot.py/notify_thread.sh/trading_bot là stub. KHÔNG gọi DNSE/BQ/Discord.
# Mọi lượt chạy wrapper: `env -u TZ` (§16, host UTC) + shim `date` ghim thời điểm ⇒ không phụ
# thuộc giờ/ngày chạy selfcheck (mặc định T2 2026-09-14 19:50 ICT). Exit 0 = mọi ca PASS.
set -uo pipefail
REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/nav_snapshot_daily.sh"
REAL_DATE="$(command -v date)"
PASS=0; FAIL=0
ok()  { PASS=$((PASS + 1)); echo "  PASS $*"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL $*"; }
epoch() { "$REAL_DATE" -d "$1" +%s; }
CRON_HEALTH="$(dirname "$REAL")/cron_health_check.py"
# Số dòng cron_health_check.py THẬT coi là lỗi (ERROR_RE + BENIGN_SUBSTR import từ chính file đó,
# không tự chế regex — arch-review aria-G vòng 2: dòng có prefix log() không khớp ^\s*❌).
ch_hits() {
  python3 - "$CRON_HEALTH" "$1" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ch", sys.argv[1]); ch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch)
n = sum(1 for l in open(sys.argv[2], encoding="utf-8")
        if ch.ERROR_RE.search(l) and not any(b in l for b in ch.BENIGN_SUBSTR))
print(n)
PY
}

mk_sandbox() {  # $1 = thời điểm UTC ISO (mặc định T2 19:50 ICT)
  SB="$(mktemp -d /tmp/nsd_selfcheck.XXXXXX)"
  FAKE_EPOCH="$(epoch "${1:-2026-09-14T12:50:00Z}")"
  TODAY="$(TZ='Asia/Ho_Chi_Minh' "$REAL_DATE" -d "@$FAKE_EPOCH" +%Y-%m-%d)"
  mkdir -p "$SB/mike/bin" "$SB/mike/state" "$SB/data/execution_logs" "$SB/trading_bot" "$SB/shim"
  printf '#!/usr/bin/env bash\nexec %s -d @%s "$@"\n' "$REAL_DATE" "$FAKE_EPOCH" > "$SB/shim/date"
  chmod +x "$SB/shim/date"
  cp "$REAL" "$SB/mike/bin/nav_snapshot_daily.sh"
  : > "$SB/wc_env.sh"
  : > "$SB/trading_bot/__init__.py"
  cat > "$SB/trading_bot/vn_market.py" <<'EOF'
import os
def is_holiday(d):
    return os.environ.get("FAKE_HOLIDAY") == "1"
EOF
  cat > "$SB/trading_bot/config.py" <<'EOF'
import os
def live_dnse_labels():
    return [] if os.environ.get("FAKE_LABELS_EMPTY") == "1" else ["SpaceX", "ZaloPay"]
EOF
  cat > "$SB/mike/bin/notify_thread.sh" <<'EOF'
#!/usr/bin/env bash
[ "${FAKE_NOTIFY_FAIL:-}" = 1 ] && exit 1
printf '%s\t%s\n' "${2:-}" "$1" >> "$(dirname "$0")/../../notify.log"
EOF
  chmod +x "$SB/mike/bin/notify_thread.sh"
  # Stub: mô phỏng hợp đồng rc của daily_nav_snapshot.py. Token lấy lần lượt từ scenario_<acct>
  # (mặc định 0): số = rc; "hang" = ngủ 30s (để timeout bắn); "norow" = rc 0 không ghi dòng.
  # rc=0 ⇒ NAV = totalCash − totalDebt của bản ghi balances CUỐI trong dnse_raw giả, ghi đè dòng
  # cùng ngày (đúng ngữ nghĩa _write_nav_history thật).
  cat > "$SB/mike/bin/daily_nav_snapshot.py" <<'EOF'
import argparse, csv, json, os, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("--account"); ap.add_argument("--date")
a = ap.parse_args()
sb = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(os.path.join(sb, "calls.log"), "a") as f:
    f.write(f"{a.account} {a.date}\n")
scen = os.path.join(sb, f"scenario_{a.account}")
seq = open(scen).read().split() if os.path.exists(scen) else []
tok = seq.pop(0) if seq else "0"
if os.path.exists(scen):
    open(scen, "w").write(" ".join(seq))
if tok in ("2marker", "2row"):   # rc=2, và trong lúc wrapper ngủ: nav_sync_retry đặt marker / EOD ghi dòng
    ex = os.path.join(sb, "data", "execution_logs")
    if tok == "2marker":
        os.makedirs(os.path.join(sb, "mike", "state", "nav_pending_retry"), exist_ok=True)
        open(os.path.join(sb, "mike", "state", "nav_pending_retry", f"{a.account}_{a.date}.log"), "w").write("x")
    else:
        open(os.path.join(ex, f"nav_history_{a.account}.csv"), "a").write(f"{a.date},111,{a.date}T19:10:36\n")
    sys.exit(2)
if tok == "hang":
    time.sleep(30); sys.exit(0)
if tok == "norow":
    print(f"ℹ️ [{a.date}] Chưa có ngày giao dịch nào cho {a.account} — bỏ qua NAV snapshot."); sys.exit(0)
if tok == "3":   # đúng dạng thật: sanity guard in 🔴 ra STDOUT (không phải ❌)
    print(f"🔴 NAV {a.date} ({a.account}) TỰ CHẶN KHÔNG ĐĂNG: 1 VND (biến động -99.00%/ngày vượt ngưỡng ±15%)"); sys.exit(3)
if tok != "0":
    print(f"❌ [{a.date}] stub rc={tok}", file=sys.stderr); sys.exit(int(tok))
ex = os.path.join(sb, "data", "execution_logs")
bal = None
for line in open(os.path.join(ex, f"dnse_raw_{a.date}.jsonl")):
    r = json.loads(line)
    if r["kind"] == "balances" and r["account_label"] == a.account:
        bal = r
if bal is None:
    print("no balances", file=sys.stderr); sys.exit(2)
nav = bal["payload"]["stock"]["totalCash"] - bal["payload"]["stock"]["totalDebt"]
p = os.path.join(ex, f"nav_history_{a.account}.csv")
rows = list(csv.DictReader(open(p))) if os.path.exists(p) else []
rows = [r for r in rows if r["date"] != a.date] + [{"date": a.date, "nav": str(nav), "balance_ts": bal["ts"]}]
with open(p + ".tmp", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "nav", "balance_ts"]); w.writeheader(); w.writerows(rows)
os.replace(p + ".tmp", p)
print(f"💰 **NAV {a.date}: {nav:,} VND**")
EOF
  for acct in SpaceX ZaloPay; do
    printf 'date,nav,balance_ts\n2026-09-11,900000000,2026-09-11T19:10:07\n' > "$SB/data/execution_logs/nav_history_$acct.csv"
  done
  {
    echo "{\"ts\":\"${TODAY}T19:10:07\",\"kind\":\"balances\",\"account_label\":\"SpaceX\",\"payload\":{\"stock\":{\"totalCash\":500,\"totalDebt\":100}}}"
    echo "{\"ts\":\"${TODAY}T19:10:07\",\"kind\":\"balances\",\"account_label\":\"ZaloPay\",\"payload\":{\"stock\":{\"totalCash\":700,\"totalDebt\":0}}}"
  } > "$SB/data/execution_logs/dnse_raw_${TODAY}.jsonl"
  : > "$SB/calls.log"; : > "$SB/notify.log"
}
run() {  # wrapper dưới env -u TZ + shim date; mặc định không chờ, không ngủ (ca riêng ghi đè env)
  env -u TZ PATH="$SB/shim:$PATH" NAV_SNAPSHOT_RETRY_SLEEP_S="${RS:-0}" NAV_SNAPSHOT_EOD_WAIT_MAX_S="${EW:-0}" \
    NAV_SNAPSHOT_EOD_POLL_S="${EP:-1}" NAV_SNAPSHOT_PY_TIMEOUT_S="${PT:-20}" \
    bash "$SB/mike/bin/nav_snapshot_daily.sh" > "$SB/run.out" 2>&1
}
calls()      { grep -c "^$1 " "$SB/calls.log"; }
rows_today() { grep -c "^$TODAY," "$SB/data/execution_logs/nav_history_$1.csv"; }
hist_sha()   { cat "$SB"/data/execution_logs/nav_history_*.csv | sha256sum | cut -d' ' -f1; }
nfy()        { grep -c "$1" "$SB/notify.log"; }

echo "== Ca 1: không có plan/state file, 2 account rc=0 ⇒ vẫn ghi, --date = hôm nay ICT"
mk_sandbox
run; rc=$?
[ ! -e "$SB/data/trade_plans" ] && ok "sandbox không có plan file" || bad "sandbox có plan file"
[ "$rc" = 0 ] && ok "exit 0" || bad "exit=$rc"
[ "$(rows_today SpaceX)" = 1 ] && [ "$(rows_today ZaloPay)" = 1 ] && ok "mỗi account đúng 1 dòng $TODAY" || bad "rows SpaceX=$(rows_today SpaceX) ZaloPay=$(rows_today ZaloPay)"
[ "$(grep -c " $TODAY$" "$SB/calls.log")" = 2 ] && ok "--date truyền vào = ngày ICT" || bad "calls: $(cat "$SB/calls.log")"
grep -q "^$TODAY,400," "$SB/data/execution_logs/nav_history_SpaceX.csv" && ok "NAV SpaceX = cash−debt từ dnse_raw giả" || bad "NAV SpaceX sai"
[ "$(nfy '^trading_daily	✅')" = 2 ] && ok "báo Trading Daily ✅ x2" || bad "notify: $(cat "$SB/notify.log")"

echo "== Ca 2: chạy lần 2 liên tiếp ⇒ không gọi lại, nav_history giống hệt từng byte"
sha1="$(hist_sha)"; : > "$SB/calls.log"; : > "$SB/notify.log"
run; rc=$?
[ "$rc" = 0 ] && ok "exit 0" || bad "exit=$rc"
[ ! -s "$SB/calls.log" ] && ok "0 lần gọi daily_nav_snapshot" || bad "calls: $(cat "$SB/calls.log")"
[ "$(hist_sha)" = "$sha1" ] && ok "nav_history byte-identical" || bad "nav_history đổi"
[ ! -s "$SB/notify.log" ] && ok "không spam notify" || bad "notify: $(cat "$SB/notify.log")"
rm -rf "$SB"

echo "== Ca 3: EOD đã ghi dòng hôm nay (khác số dnse_raw) ⇒ cron KHÔNG ghi đè"
mk_sandbox
echo "$TODAY,123456789,${TODAY}T19:10:36" >> "$SB/data/execution_logs/nav_history_SpaceX.csv"
run
[ "$(calls SpaceX)" = 0 ] && ok "SpaceX không gọi" || bad "SpaceX calls=$(calls SpaceX)"
grep -q "^$TODAY,123456789," "$SB/data/execution_logs/nav_history_SpaceX.csv" && [ "$(rows_today SpaceX)" = 1 ] && ok "dòng EOD giữ nguyên" || bad "dòng EOD bị đổi"
[ "$(rows_today ZaloPay)" = 1 ] && ok "ZaloPay (thiếu) vẫn được ghi" || bad "ZaloPay không ghi"
rm -rf "$SB"

echo "== Ca 4: rc=2 ⇒ retry tối đa 2 VÒNG (vòng ngoài = lần thử, gộp mọi account)"
mk_sandbox
echo "2 0" > "$SB/scenario_SpaceX"; echo "2 2 2 0" > "$SB/scenario_ZaloPay"
run; rc=$?
[ "$(calls SpaceX)" = 2 ] && [ "$(rows_today SpaceX)" = 1 ] && ok "SpaceX rc=2 rồi 0 ⇒ 2 lần gọi, có dòng" || bad "SpaceX calls=$(calls SpaceX) rows=$(rows_today SpaceX)"
[ "$(calls ZaloPay)" = 3 ] && [ "$(rows_today ZaloPay)" = 0 ] && ok "ZaloPay rc=2 x3 ⇒ dừng ở 3 lần gọi, không dòng" || bad "ZaloPay calls=$(calls ZaloPay) rows=$(rows_today ZaloPay)"
[ "$(grep -c 'retry [12]/2' "$SB/run.out")" = 2 ] && ok "đúng 2 lượt ngủ-retry dù 2 account cùng lỗi vòng đầu" || bad "retry lines=$(grep -c 'retry' "$SB/run.out")"
[ "$(nfy '^trading_daily	🔴 NAV ZaloPay.*rc=2')" = 1 ] && [ "$(nfy '🔴 NAV SpaceX')" = 0 ] && ok "🔴 rc=2 chỉ cho ZaloPay, 1 lần" || bad "notify: $(cat "$SB/notify.log")"
[ "$(ch_hits "$SB/run.out")" -ge 1 ] && ok "cron_health_check THẬT bắt được lỗi trong log" || bad "cron_health không thấy lỗi: $(cat "$SB/run.out")"
[ "$rc" = 1 ] && ok "exit 1 khi còn account thất bại" || bad "exit=$rc"
rm -rf "$SB"

mk_sandbox
echo "2 0" > "$SB/scenario_SpaceX"
run; rc=$?
[ "$rc" = 0 ] && [ "$(rows_today SpaceX)" = 1 ] && [ "$(ch_hits "$SB/run.out")" = 0 ] && ok "rc=2 thoáng qua rồi hồi ⇒ cron_health KHÔNG báo lỗi giả" || bad "rc=$rc hits=$(ch_hits "$SB/run.out"): $(cat "$SB/run.out")"
rm -rf "$SB"

echo "== Ca 4b: giữa 2 vòng retry, marker/dòng xuất hiện ⇒ vòng sau KHÔNG gọi lại, không 🔴"
mk_sandbox
echo "2marker 0" > "$SB/scenario_SpaceX"; echo "2row 0" > "$SB/scenario_ZaloPay"
run; rc=$?
[ "$(calls SpaceX)" = 1 ] && [ "$(rows_today SpaceX)" = 0 ] && ok "SpaceX: marker mới ⇒ nhường, 1 lần gọi" || bad "SpaceX calls=$(calls SpaceX) rows=$(rows_today SpaceX)"
[ "$(calls ZaloPay)" = 1 ] && grep -q "^$TODAY,111," "$SB/data/execution_logs/nav_history_ZaloPay.csv" && ok "ZaloPay: dòng EOD mới ⇒ bỏ qua, không ghi đè" || bad "ZaloPay calls=$(calls ZaloPay)"
[ "$(nfy '🔴')" = 0 ] && [ "$rc" = 0 ] && ok "không 🔴, exit 0" || bad "rc=$rc notify: $(cat "$SB/notify.log")"
rm -rf "$SB"

echo "== Ca 5: python treo quá timeout ⇒ xử lý như rc=2 (retry), không kẹt flock ngày sau"
mk_sandbox
echo "hang 0" > "$SB/scenario_SpaceX"
PT=2 run; rc=$?
[ "$(calls SpaceX)" = 2 ] && [ "$(rows_today SpaceX)" = 1 ] && ok "treo ⇒ timeout ⇒ retry ⇒ có dòng" || bad "calls=$(calls SpaceX) rows=$(rows_today SpaceX) rc=$rc"
[ "$(ch_hits "$SB/run.out")" = 0 ] && ok "treo 1 lần rồi hồi ⇒ cron_health KHÔNG báo lỗi" || bad "báo lỗi giả: $(cat "$SB/run.out")"
rm -rf "$SB"
mk_sandbox
echo "hang hang hang" > "$SB/scenario_SpaceX"
PT=1 run; rc=$?
[ "$rc" = 1 ] && [ "$(nfy '🔴 NAV SpaceX.*rc=124')" = 1 ] && [ "$(ch_hits "$SB/run.out")" -ge 1 ] && ok "treo cả 3 lần ⇒ 🔴 rc=124 + cron_health bắt được" || bad "rc=$rc hits=$(ch_hits "$SB/run.out") notify: $(cat "$SB/notify.log")"
rm -rf "$SB"

echo "== Ca 6: rc=4 ⇒ không ghi, không retry, marker cho nav_sync_retry, không in ❌ raw; lần sau nhường marker"
mk_sandbox
echo "4" > "$SB/scenario_SpaceX"
run; rc=$?
[ "$(calls SpaceX)" = 1 ] && [ "$(rows_today SpaceX)" = 0 ] && ok "1 lần gọi, không dòng" || bad "calls=$(calls SpaceX) rows=$(rows_today SpaceX)"
[ -f "$SB/mike/state/nav_pending_retry/SpaceX_${TODAY}.log" ] && ok "marker SpaceX_${TODAY}.log (định dạng nav_sync_retry)" || bad "không có marker"
grep -qE '^\s*❌' "$SB/run.out" && bad "log có dòng ❌ ⇒ ERRORS_FOUND giả" || ok "log không có dòng ❌"
[ "$(nfy '^trading_daily	⏳ NAV SpaceX')" = 1 ] && ok "báo Trading Daily ⏳" || bad "notify: $(cat "$SB/notify.log")"
[ "$rc" = 0 ] && ok "exit 0 (rc=4 không phải thất bại của cron)" || bad "exit=$rc"
[ "$(ch_hits "$SB/run.out")" = 0 ] && ok "rc=4 ⇒ cron_health KHÔNG báo lỗi" || bad "báo lỗi giả rc=4: $(cat "$SB/run.out")"
: > "$SB/calls.log"; run
[ "$(calls SpaceX)" = 0 ] && ok "lượt 2: nhường marker, không gọi" || bad "lượt 2 calls=$(calls SpaceX)"
mv "$SB/mike/state/nav_pending_retry/SpaceX_${TODAY}.log" "$SB/mike/state/nav_pending_retry/SpaceX_${TODAY}.stuck_${TODAY}"
: > "$SB/calls.log"; run
[ "$(calls SpaceX)" = 0 ] && ok "marker .stuck (đã escalate) cũng nhường" || bad "stuck calls=$(calls SpaceX)"
rm -rf "$SB"

echo "== Ca 7: rc=3 (sanity guard) ⇒ không retry, không ghi, báo 🔴"
mk_sandbox
echo "3" > "$SB/scenario_ZaloPay"
run
[ "$(calls ZaloPay)" = 1 ] && [ "$(rows_today ZaloPay)" = 0 ] && ok "1 lần gọi, không dòng" || bad "calls=$(calls ZaloPay) rows=$(rows_today ZaloPay)"
[ "$(nfy '^trading_daily	🔴 NAV ZaloPay.*rc=3')" = 1 ] && ok "báo Trading Daily 🔴 rc=3" || bad "notify: $(cat "$SB/notify.log")"
[ "$(ch_hits "$SB/run.out")" -ge 1 ] && ok "rc=3 ⇒ cron_health bắt được" || bad "rc=3 không bị bắt: $(cat "$SB/run.out")"
: > "$SB/calls.log"; echo "3" > "$SB/scenario_ZaloPay"
FAKE_NOTIFY_FAIL=1 run
grep -q '^NOTIFY_FAILED: ' "$SB/run.out" && [ "$(ch_hits "$SB/run.out")" -ge 2 ] && ok "notify lỗi ⇒ NOTIFY_FAILED + cron_health bắt được" || bad "run.out: $(cat "$SB/run.out")"
rm -rf "$SB"

echo "== Ca 8: rc=0 nhưng không ghi dòng (account chưa có ngày giao dịch) ⇒ không báo ✅"
mk_sandbox
echo "norow" > "$SB/scenario_SpaceX"
run
[ "$(rows_today SpaceX)" = 0 ] && [ "$(nfy '✅ NAV SpaceX')" = 0 ] && ok "không dòng, không ✅" || bad "rows=$(rows_today SpaceX) notify: $(cat "$SB/notify.log")"
rm -rf "$SB"

echo "== Ca 9: không phải phiên ⇒ không gọi gì (ngày lễ; Thứ Bảy)"
mk_sandbox
FAKE_HOLIDAY=1 run
[ ! -s "$SB/calls.log" ] && ok "ngày lễ: 0 lần gọi" || bad "calls: $(cat "$SB/calls.log")"
rm -rf "$SB"
mk_sandbox 2026-09-12T12:50:00Z
run
[ "$TODAY" = 2026-09-12 ] && [ ! -s "$SB/calls.log" ] && ok "Thứ Bảy $TODAY: 0 lần gọi" || bad "Thứ Bảy calls: $(cat "$SB/calls.log")"
rm -rf "$SB"

echo "== Ca 10 (§16, không phụ thuộc giờ chạy): 01:00 ICT T2 = 18:00 UTC Chủ Nhật ⇒ --date phải là ngày ICT"
mk_sandbox 2026-09-13T18:00:00Z
UTC_D="$(TZ=UTC "$REAL_DATE" -d "@$FAKE_EPOCH" +%Y-%m-%d)"
[ "$TODAY" != "$UTC_D" ] && ok "fixture: ngày ICT ($TODAY) ≠ ngày UTC ($UTC_D)" || bad "fixture hỏng"
run
[ "$(grep -c " $TODAY$" "$SB/calls.log")" = 2 ] && ok "--date = $TODAY (ICT) cho cả 2 account" || bad "calls: $(cat "$SB/calls.log")"
rm -rf "$SB"

echo "== Ca 11: danh sách account rỗng ⇒ 🔴 + exit 1 (không im lặng exit 0)"
mk_sandbox
FAKE_LABELS_EMPTY=1 run; rc=$?
[ "$rc" = 1 ] && [ "$(nfy '🔴 nav_snapshot_daily')" = 1 ] && [ ! -s "$SB/calls.log" ] && ok "exit 1 + 🔴 + 0 lần gọi" || bad "rc=$rc notify: $(cat "$SB/notify.log")"
[ "$(ch_hits "$SB/run.out")" -ge 1 ] && ok "LABELS rỗng ⇒ cron_health bắt được" || bad "không bị bắt: $(cat "$SB/run.out")"
rm -rf "$SB"

echo "== Ca 12: lượt khác đang giữ lock ⇒ thoát 0, không gọi"
mk_sandbox
flock "$SB/mike/state/nav_snapshot_daily.lock" sleep 5 & LOCKPID=$!
sleep 0.5
run; rc=$?
[ "$rc" = 0 ] && [ ! -s "$SB/calls.log" ] && ok "bị lock ⇒ 0 lần gọi" || bad "rc=$rc calls: $(cat "$SB/calls.log")"
kill "$LOCKPID" 2>/dev/null; wait "$LOCKPID" 2>/dev/null
rm -rf "$SB"

echo "== Ca 13: chờ EOD của CHÍNH cây này (bash <ROOT>/bin/eod… và for_each …), KHÔNG chờ mồi"
mk_sandbox
printf '#!/usr/bin/env bash\nsleep 3\n' > "$SB/mike/bin/eod_trading_report.sh"
printf '#!/usr/bin/env bash\nsleep 3\n' > "$SB/mike/bin/for_each_live_account.sh"
chmod +x "$SB/mike/bin/eod_trading_report.sh" "$SB/mike/bin/for_each_live_account.sh"
mkdir -p "$SB/other/mike/bin"; cp "$SB/mike/bin/eod_trading_report.sh" "$SB/other/mike/bin/"
# (a) EOD thật-dạng (exec trực tiếp qua shebang ⇒ argv "bash <path> --account X")
"$SB/mike/bin/eod_trading_report.sh" --account SpaceX & P1=$!
sleep 0.3
EW=20 run
wait "$P1" 2>/dev/null
grep -q 'đã chờ EOD [1-9]' "$SB/run.out" && [ "$(calls SpaceX)" = 1 ] && ok "(a) chờ EOD đang chạy rồi mới ghi" || bad "(a) run.out: $(tail -3 "$SB/run.out")"
# (b) for_each_live_account đang giữa 2 account
rm -f "$SB"/data/execution_logs/nav_history_*.csv; : > "$SB/calls.log"
"$SB/mike/bin/for_each_live_account.sh" "$SB/mike/bin/eod_trading_report.sh" & P2=$!
sleep 0.3
EW=20 run
wait "$P2" 2>/dev/null
grep -q 'đã chờ EOD [1-9]' "$SB/run.out" && ok "(b) chờ for_each_live_account … eod_trading_report.sh" || bad "(b) run.out: $(tail -3 "$SB/run.out")"
# (c) mồi: prompt nhắc đường dẫn + EOD của cây KHÁC ⇒ không được chờ
rm -f "$SB"/data/execution_logs/nav_history_*.csv; : > "$SB/calls.log"
bash -c 'sleep 4' "claude -p review $SB/mike/bin/eod_trading_report.sh" & D1=$!
python3 -c 'import time; time.sleep(4)' "bash $SB/mike/bin/eod_trading_report.sh" & D2=$!
"$SB/other/mike/bin/eod_trading_report.sh" --account SpaceX & D3=$!
sleep 0.3
EW=20 run
kill "$D1" "$D2" "$D3" 2>/dev/null; wait "$D1" "$D2" "$D3" 2>/dev/null
! grep -q 'đã chờ EOD' "$SB/run.out" && [ "$(calls SpaceX)" = 1 ] && ok "(c) 3 tiến trình mồi không làm wrapper chờ" || bad "(c) run.out: $(tail -3 "$SB/run.out")"
rm -rf "$SB"

echo "== Tổng: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
