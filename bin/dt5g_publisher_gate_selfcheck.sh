#!/usr/bin/env bash
# dt5g_publisher_gate_selfcheck.sh — self-check cho DT5G PUBLISHER-EVIDENCE gate
# (khối gate trong bin/bq_freshness_check.sh, job Winston_20260731_014953).
#
# VÌ SAO cần: gate này là thứ DUY NHẤT còn chặn được DollarBill khi publisher DT5G của ta
# chết — `MAX(time)` của bảng `vnindex_5state_dt5g_live` KHÔNG còn chứng minh được điều đó
# nữa vì bảng có writer thứ hai (pipeline kaffa_v2 của team dữ liệu, ~17:12 ICT) vẫn đẩy
# MAX(time)=hôm nay. Gate sai kiểu false-PASS = plan tiền thật lập trên state của engine khác;
# gate sai kiểu false-FAIL = chặn oan DollarBill cả ngày (đặc biệt ngày lễ).
#
# CÁCH TEST (điểm mấu chốt — KHÔNG copy logic): script này TRÍCH NGUYÊN VĂN khối gate ra khỏi
# `bin/bq_freshness_check.sh` bằng dấu mốc dòng rồi `eval` trong sandbox. Sửa gate mà quên sửa
# test ⇒ test chạy trên đúng code mới, không có chuyện test và production trôi khỏi nhau.
# Sandbox: WORKDIR tạm (symlink `trading_bot` sang bản thật để `vn_market` import được) +
# `deploy_golive_dt5g_v4/golive_state_today.json` + `data/vnindex_5state_dt5g_live.csv` bịa
# theo từng ca; `notify.sh`/`notify_thread.sh` là stub ⇒ KHÔNG ping Discord/Telegram thật.
#
# Usage: bash mike/bin/dt5g_publisher_gate_selfcheck.sh   (exit 0 = tất cả ca PASS)
set -uo pipefail

REAL_MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL_WC="$(cd "$REAL_MIKE/.." && pwd)"
SRC="$REAL_MIKE/bin/bq_freshness_check.sh"

START_MARK='# --- DT5G PUBLISHER-EVIDENCE gate'
END_MARK='# Giám sát WRITER LẠ'
s=$(grep -n "$START_MARK" "$SRC" | head -1 | cut -d: -f1)
e=$(grep -n "$END_MARK"   "$SRC" | head -1 | cut -d: -f1)
if [ -z "$s" ] || [ -z "$e" ] || [ "$e" -le "$s" ]; then
  echo "FATAL: không trích được khối gate khỏi $SRC (mốc đầu/cuối đổi?) — sửa selfcheck trước"; exit 1
fi
GATE_SRC="$(sed -n "${s},$((e-1))p" "$SRC")"
echo "Trích khối gate: dòng ${s}..$((e-1)) của bin/bq_freshness_check.sh ($(printf '%s' "$GATE_SRC" | wc -l) dòng)"

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/wc/deploy_golive_dt5g_v4" "$SANDBOX/wc/data" "$SANDBOX/mike/bin"
ln -s "$REAL_WC/trading_bot" "$SANDBOX/wc/trading_bot"
for n in notify.sh notify_thread.sh; do
  printf '#!/usr/bin/env bash\necho "[stub %s] $1" >> "$SANDBOX_LOG"\n' "$n" > "$SANDBOX/mike/bin/$n"
  chmod +x "$SANDBOX/mike/bin/$n"
done

FAILS=0
# run_case <tên> <today> <as_of|-> <pub_ok true|false|-> <json_mtime|-> <csv_mtime|-> <expect_FAILED> <expect_WARNED>
run_case() {
  local name="$1" today="$2" as_of="$3" pub_ok="$4" json_mt="$5" csv_mt="$6" exp_f="$7" exp_w="$8"
  local J="$SANDBOX/wc/deploy_golive_dt5g_v4/golive_state_today.json"
  local C="$SANDBOX/wc/data/vnindex_5state_dt5g_live.csv"
  rm -f "$J" "$C"
  if [ "$as_of" != "-" ]; then
    printf '{"as_of": "%s", "state": 3, "bq_publish_ok": %s, "published_at": "%sT19:01:17"}\n' \
      "$as_of" "$pub_ok" "$as_of" > "$J"
    touch -d "$json_mt 19:01:17" "$J"
  fi
  if [ "$csv_mt" != "-" ]; then
    printf 'time,state,state_raw,asof_date\n2026-07-30,3,3,2026-07-30\n' > "$C"
    touch -d "$csv_mt 19:01:17" "$C"
  fi

  local out
  out=$(
    export SANDBOX_LOG="$SANDBOX/notify.log"
    WORKDIR="$SANDBOX/wc"; ROOT="$SANDBOX/mike"; TODAY="$today"
    NOW_ICT="09:00 ICT"; QUIET=""; FAILED=0; WARNED=0
    DISCORD_STALE_CHANNEL="stub-channel"
    eval "$GATE_SRC"
    echo "__RESULT__ FAILED=$FAILED WARNED=$WARNED"
  )
  local got_f got_w
  got_f=$(sed -n 's/.*__RESULT__ FAILED=\([0-9]*\).*/\1/p' <<<"$out")
  got_w=$(sed -n 's/.*__RESULT__ .*WARNED=\([0-9]*\).*/\1/p' <<<"$out")
  if [ "$got_f" = "$exp_f" ] && [ "$got_w" = "$exp_w" ]; then
    printf 'PASS  %-58s FAILED=%s WARNED=%s\n' "$name" "$got_f" "$got_w"
  else
    printf 'FAIL  %-58s got FAILED=%s WARNED=%s, muốn FAILED=%s WARNED=%s\n' \
      "$name" "$got_f" "$got_w" "$exp_f" "$exp_w"
    sed 's/^/        | /' <<<"$out"
    FAILS=$((FAILS + 1))
  fi
}

# 2026-07-30 Thu và 2026-07-31 Fri là phiên giao dịch; 2026-08-02 là Chủ nhật (không giao dịch).
echo
echo "--- Ca THẬT: hôm nay là phiên giao dịch, publisher CỦA TA đã chạy hôm nay ---"
run_case "1. as_of=hôm nay + publish_ok + mtime hôm nay (đường sống)" \
         2026-07-31 2026-07-31 true 2026-07-31 2026-07-31 0 0
run_case "2. như (1) nhưng CSV mirror cũ → WARN, KHÔNG chặn" \
         2026-07-31 2026-07-31 true 2026-07-31 2026-07-30 0 1
run_case "3. như (1) nhưng CSV mirror MẤT → WARN, KHÔNG chặn" \
         2026-07-31 2026-07-31 true 2026-07-31 -          0 1

echo
echo "--- Ca CHÍNH: publisher CỦA TA không chạy, nhưng bảng BQ vẫn tươi nhờ writer kaffa ---"
run_case "4. as_of=hôm qua (publisher ta chết) → PHẢI CHẶN" \
         2026-07-31 2026-07-30 true 2026-07-30 2026-07-30 1 0
run_case "5. as_of hôm nay nhưng mtime=hôm qua (file cũ sót lại) → PHẢI CHẶN" \
         2026-07-31 2026-07-31 true 2026-07-30 2026-07-31 1 0
run_case "6. bq_publish_ok=false (publish BQ hỏng) → PHẢI CHẶN" \
         2026-07-31 2026-07-31 false 2026-07-31 2026-07-31 1 0
run_case "7. golive_state_today.json KHÔNG TỒN TẠI → PHẢI CHẶN" \
         2026-07-31 - -    -          2026-07-31 1 0

echo
echo "--- Ca NGÀY KHÔNG GIAO DỊCH (CN 2026-08-02): không được chặn oan ---"
run_case "8. CN, as_of=phiên gần nhất (Fri 07-31), mtime cũ → PASS" \
         2026-08-02 2026-07-31 true 2026-07-31 2026-07-31 0 0
run_case "9. CN, as_of=07-30 (bỏ lỡ phiên Fri 07-31) → PHẢI CHẶN" \
         2026-08-02 2026-07-30 true 2026-07-30 2026-07-30 1 0

echo
if [ "$FAILS" -eq 0 ]; then
  echo "=== SELFCHECK OK — 9/9 ca đúng ==="
  echo "Không ping thật nào: $(wc -l < "$SANDBOX/notify.log" 2>/dev/null || echo 0) dòng vào stub log (Discord/Telegram thật KHÔNG bị gọi)."
  exit 0
fi
echo "=== SELFCHECK FAIL — $FAILS ca sai ==="
exit 1
