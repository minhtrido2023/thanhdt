#!/usr/bin/env bash
# prefetch_dnse_statement_selfcheck.sh — sandbox, KHÔNG chạm Gmail/DNSE. Exit 0 = mọi ca PASS.
# `date` ghim 2026-10-22T17:30Z = 00:30 ICT 23/10 ⇒ ngày UTC (22) ≠ ngày ICT (23): bỏ neo TZ ⇒ FAIL
# bất kể giờ chạy selfcheck. Chạy dưới `env -u TZ` (§16).
# Ca: 1 chưa có CSV ⇒ fetch 1 lần đúng --date ICT · 2 CSV đã có ⇒ không gọi · 3 "Không tìm thấy email"
#     ⇒ lành tính (không ❌) · 4 lỗi khác ⇒ ❌ + stderr thật · 5 fetch treo ⇒ cắt <5s, ❌ timeout.
# Mọi ca: exit 0.
set -uo pipefail
REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/prefetch_dnse_statement.sh"
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
pass=0; fail=0
ok()  { echo "  PASS $*"; pass=$((pass+1)); }
bad() { echo "  FAIL $*"; fail=$((fail+1)); }
REAL_DATE="$(command -v date)"
EPOCH="$("$REAL_DATE" -u -d 2026-10-22T17:30:00Z +%s)"
ICT_DMY="23-10-2026"
CSV="$SB/data/execution_logs/dnse_khoplenh_broker_confirm_${ICT_DMY}.csv"
mk() {  # $1 = hành vi fetch giả: write|notfound|oauth|hang
  rm -rf "$SB/data" "$SB/mike" "$SB/shim"; mkdir -p "$SB/data/execution_logs" "$SB/mike/bin" "$SB/shim"; : > "$SB/args.log"
  cp "$REAL" "$SB/mike/bin/prefetch_dnse_statement.sh"
  printf '#!/usr/bin/env bash\nexec %s -d @%s "$@"\n' "$REAL_DATE" "$EPOCH" > "$SB/shim/date"; chmod +x "$SB/shim/date"
  case "$1" in
    write)    body='printf "tieu_khoan,ma\n1,DRI\n" > data/execution_logs/dnse_khoplenh_broker_confirm_'"$ICT_DMY"'.csv' ;;
    notfound) body='echo "❌ Không tìm thấy email DNSE ngày 23/10/2026" >&2; exit 1' ;;
    oauth)    body='echo "Traceback (most recent call last):" >&2; echo "google.auth.exceptions.RefreshError: invalid_grant" >&2; exit 1' ;;
    hang)     body='sleep 30' ;;
  esac
  printf '#!/usr/bin/env bash\necho "$@" >> %s/args.log\n%s\n' "$SB" "$body" > "$SB/shim/python3"; chmod +x "$SB/shim/python3"
}
run() {
  local t0=$SECONDS
  env -u TZ PATH="$SB/shim:$PATH" PREFETCH_WC_ROOT="$SB" PREFETCH_TIMEOUT_S="${T:-5}" bash "$SB/mike/bin/prefetch_dnse_statement.sh" > "$SB/out.txt" 2>&1
  RC=$?; ELAPSED=$((SECONDS - t0))
}

echo "== Ca 1: chưa có CSV ⇒ fetch 1 lần, --date = ngày ICT (không phải ngày UTC)"
mk write; run
[ "$RC" = 0 ] && ok "exit 0" || bad "exit=$RC"
[ "$(wc -l < "$SB/args.log")" = 1 ] && grep -q -- "--date 23/10/2026" "$SB/args.log" && ok "fetch 1 lần, --date 23/10/2026" || bad "args: $(cat "$SB/args.log")"
[ -s "$CSV" ] && grep -q "đã tải" "$SB/out.txt" && ! grep -q "❌" "$SB/out.txt" && ok "CSV có, log nói đã tải" || bad "out: $(cat "$SB/out.txt")"

echo "== Ca 2: CSV đã có ⇒ không gọi fetch"
mk write; printf 'x\n' > "$CSV"; run
[ "$RC" = 0 ] && [ ! -s "$SB/args.log" ] && ok "idempotent: không gọi fetch" || bad "rc=$RC args=$(cat "$SB/args.log")"

echo "== Ca 3: 'Không tìm thấy email' ⇒ lành tính, không ❌"
mk notfound; run
[ "$RC" = 0 ] && [ ! -e "$CSV" ] && grep -q "chưa có email" "$SB/out.txt" && ! grep -q "❌" "$SB/out.txt" && ok "exit 0, lành tính" || bad "rc=$RC out=$(cat "$SB/out.txt")"

echo "== Ca 4: lỗi OAuth ⇒ ❌ + stderr thật, vẫn exit 0"
mk oauth; run
[ "$RC" = 0 ] && grep -q "^❌ prefetch_dnse_statement" "$SB/out.txt" && grep -q "RefreshError: invalid_grant" "$SB/out.txt" && ok "❌ kèm bằng chứng thật" || bad "rc=$RC out=$(cat "$SB/out.txt")"

echo "== Ca 5: fetch treo ⇒ timeout cắt (<8s), ❌ timeout, exit 0"
mk hang; T=1 run
[ "$RC" = 0 ] && [ "$ELAPSED" -lt 8 ] && grep -q "^❌ prefetch_dnse_statement.*quá 1s" "$SB/out.txt" && ok "cắt sau ${ELAPSED}s" || bad "rc=$RC elapsed=${ELAPSED}s out=$(cat "$SB/out.txt")"

echo; echo "kết quả: $pass PASS / $fail FAIL"; [ "$fail" = 0 ]
