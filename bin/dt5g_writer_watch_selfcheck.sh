#!/usr/bin/env bash
# dt5g_writer_watch_selfcheck.sh — self-check cho monitor bin/dt5g_writer_watch.py
# (job Winston_20260731_014953).
#
# Chạy CHÍNH script monitor thật (không copy logic), trên bảng BQ THẬT, nhưng với sandbox
# WORKDIR_8L: `data/vnindex_5state_dt5g_live.csv` là BẢN SAO đã bịa lệch, và `mike/bin/notify*.sh`
# + `append_event.sh` là STUB ⇒ đường cảnh báo được chạy thật đầu-cuối mà KHÔNG ping
# Discord/Telegram/bus thật. Kiểm tra: đúng tầng (QUIET/WARN/HIGH), đúng số phiên lệch, và
# cơ chế chống-lặp (ping 1 lần/ngày/chữ ký).
#
# GIỚI HẠN ĐÃ BIẾT (nói thẳng, không giả vờ phủ hết): 2 tín hiệu HIGH còn lại — dòng TRÙNG
# `time` và `asof_date NULL trong vùng ĐÃ CHỐT` — KHÔNG test được vì muốn dựng chúng thì phải
# ghi bậy vào chính bảng PRODUCTION. Cả hai đi qua đúng khối tính tier như ca (C) bên dưới.
#
# Usage: bash mike/bin/dt5g_writer_watch_selfcheck.sh   (exit 0 = tất cả ca PASS)
set -uo pipefail

REAL_MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL_WC="$(cd "$REAL_MIKE/.." && pwd)"
REAL_CSV="$REAL_WC/data/vnindex_5state_dt5g_live.csv"
[ -f "$REAL_CSV" ] || { echo "FATAL: không có $REAL_CSV để làm nền so sánh"; exit 1; }
# Selfcheck đọc bảng BQ THẬT (không stub bq). Thiếu `bq` thì monitor rơi vào nhánh fail-safe
# "metadata mù" và mọi ca đều sai vì lý do vô nghĩa ⇒ dừng sớm, nói rõ, đừng để hiểu nhầm là PASS.
command -v bq >/dev/null 2>&1 || { echo "FATAL: không thấy 'bq' trên PATH — source wc_env.sh trước"; exit 1; }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/data" "$SANDBOX/mike/bin"
for n in notify.sh notify_thread.sh append_event.sh; do
  printf '#!/usr/bin/env bash\nprintf "%%s|%%s\\n" "%s" "$*" >> "%s/pings.log"\n' \
    "$n" "$SANDBOX" > "$SANDBOX/mike/bin/$n"
  chmod +x "$SANDBOX/mike/bin/$n"
done

FAILS=0
# run_case <tên> <n_state_mut> <n_raw_mut> <expect_tier> <expect_pings>
run_case() {
  local name="$1" n_state="$2" n_raw="$3" exp_tier="$4" exp_pings="$5"
  rm -f "$SANDBOX/pings.log" "$SANDBOX/data/dt5g_writer_watch.csv"
  python3 - "$REAL_CSV" "$SANDBOX/data/vnindex_5state_dt5g_live.csv" "$n_state" "$n_raw" <<'PY'
import csv, sys
src, dst, n_state, n_raw = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
# Bịa lệch ở ĐẦU chuỗi (2014) = vùng ĐÃ CHỐT chắc chắn, không đụng đuôi 25 phiên chưa chốt.
for r in rows[:n_state]:
    r["state"] = str((int(float(r["state"])) % 5) + 1)
for r in rows[100:100 + n_raw]:
    r["state_raw"] = str((int(float(r["state_raw"])) % 5) + 1)
w = csv.DictWriter(open(dst, "w", newline="", encoding="utf-8"), fieldnames=rows[0].keys())
w.writeheader(); w.writerows(rows)
PY
  local out tier pings
  # `env -u TZ` CỐ Ý: host chạy Etc/UTC, TZ=ICT chỉ có khi caller đã source wc_env.sh. Chạy
  # selfcheck dưới TZ THỪA HƯỞNG sẽ che mất bug "giờ naive" (đúng vụ 2026-07-31: cửa sổ
  # writer lệch -7h ⇒ WARN giả mỗi ngày). Ca A dưới đây chỉ QUIET nếu monitor tự neo ICT.
  out=$(env -u TZ WORKDIR_8L="$SANDBOX" python3 "$REAL_MIKE/bin/dt5g_writer_watch.py" --label selfcheck 2>&1)
  # tier suy ra từ dòng kết luận của monitor
  if   grep -q "^  QUIET:"  <<<"$out"; then tier=QUIET
  elif grep -q "^  \[HIGH\]" <<<"$out"; then tier=HIGH
  elif grep -q "^  \[WARN\]" <<<"$out"; then tier=WARN
  else tier="?"; fi
  pings=$(cat "$SANDBOX/pings.log" 2>/dev/null | wc -l)
  if [ "$tier" = "$exp_tier" ] && [ "$pings" -eq "$exp_pings" ]; then
    printf 'PASS  %-56s tier=%-5s pings=%s\n' "$name" "$tier" "$pings"
  else
    printf 'FAIL  %-56s got tier=%s pings=%s, muốn tier=%s pings=%s\n' \
      "$name" "$tier" "$pings" "$exp_tier" "$exp_pings"
    sed 's/^/        | /' <<<"$out"
    FAILS=$((FAILS + 1))
  fi
  LAST_OUT="$out"
}

echo "=== dt5g_writer_watch selfcheck (bảng BQ thật + CSV nền bịa lệch trong sandbox) ==="
# (A) nền sạch = bản công bố thật → phải QUIET, không ping ai (chống alert-fatigue: kaffa ghi MỖI ngày)
run_case "A. CSV nền = bản công bố thật → QUIET, không ping" 0 0 QUIET 0
# (B) chỉ lệch state_raw (cột audit) → WARN: Discord + bus, KHÔNG Telegram
run_case "B. 2 phiên lệch state_raw → WARN (2 ping: discord+bus)" 0 2 WARN 2
grep -q "2 phiên lệch \`state_raw\`" <<<"$LAST_OUT" \
  || { echo "FAIL  B-chi tiết: không nêu đúng số phiên lệch state_raw"; FAILS=$((FAILS+1)); }
# (C) lệch state ở vùng ĐÃ CHỐT → HIGH: Telegram + Discord + bus
run_case "C. 3 phiên lệch state (vùng đã chốt) → HIGH (3 ping)" 3 0 HIGH 3
grep -q "3 phiên LỆCH \`state\`" <<<"$LAST_OUT" \
  || { echo "FAIL  C-chi tiết: không nêu đúng số phiên lệch state"; FAILS=$((FAILS+1)); }
grep -q "vùng ĐÃ CHỐT" <<<"$LAST_OUT" \
  || { echo "FAIL  C-chi tiết: không nhận ra lệch nằm trong vùng đã chốt"; FAILS=$((FAILS+1)); }

# (D) chống lặp: chạy LẠI ngay ca (C) trên cùng state CSV → không được ping lần hai
echo "--- D. chống lặp (chạy lại cùng sự cố trong cùng ngày) ---"
before=$(wc -l < "$SANDBOX/pings.log")
env -u TZ WORKDIR_8L="$SANDBOX" python3 "$REAL_MIKE/bin/dt5g_writer_watch.py" --label selfcheck --quiet
after=$(wc -l < "$SANDBOX/pings.log")
if [ "$before" -eq "$after" ]; then
  printf 'PASS  %-56s pings vẫn %s (không ping lại)\n' "D. cùng chữ ký trong ngày → im lặng" "$after"
else
  printf 'FAIL  %-56s pings %s → %s (đã ping lại, alert-fatigue)\n' "D. chống lặp" "$before" "$after"
  FAILS=$((FAILS + 1))
fi

echo
if [ "$FAILS" -eq 0 ]; then echo "=== SELFCHECK OK — tất cả ca đúng ==="; exit 0; fi
echo "=== SELFCHECK FAIL — $FAILS ca sai ==="; exit 1
