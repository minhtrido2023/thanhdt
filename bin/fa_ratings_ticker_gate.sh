#!/usr/bin/env bash
# fa_ratings_ticker_gate.sh — cổng FAIL-CLOSED số mã `tav2_bq.ticker` cho refresh_fa_ratings_8l.sh
# (job Taylor_20261020_082306, user duyệt phương án A 2026-10-20 15:21 ICT).
#
# Vì sao: rating_8l_history.py đọc ICB_SQL (ICB_Code theo mã) từ tav2_bq.ticker. 2026-10-19 20:51 ICT
# bảng mất 243 mã liền kề (1294→1066 mã) ⇒ mã thiếu bị route sai ⇒ rating/tier lệch hàng nghìn dòng,
# trong khi wrapper chỉ kiểm MIN_ROWS=50000 của fa_ratings_8l (không thấy ticker hỏng).
#
# Đo (KHÔNG dùng độ tươi ngày ⇒ không chặn nhầm cuối tuần/lễ):
#   n_distinct = COUNT(DISTINCT ticker) toàn bảng (đúng thứ ICB_SQL cần: mỗi mã phải còn lịch sử)
#   n_universe = số mã in_universe tại phiên MỚI NHẤT của tav2_mike.universe_pit
#   cov        = (#mã in_universe có giá trong 30 ngày cuối) / n_universe
# Fail khi: truy vấn lỗi/không parse được ∨ n_distinct < GATE_MIN_DISTINCT ∨ n_universe < GATE_MIN_UNIVERSE
#           ∨ cov < GATE_MIN_COV.
# Ngưỡng căn từ đo 2026-10-20 (xem bus finding fa-ratings-ticker-gate-20261020): n_distinct bình thường
# 1294 (time-travel 5 ngày), pin tav2_pin.ticker_pin_202610 = 1294; n_in 68 phiên gần nhất ∈ [342,373].
#
# Exit: 0 PASS · 3 GATE-FAIL (khác exit 1 lỗi thường của wrapper) · 2 dùng sai.
# Cảnh báo Trading Daily + bus event 1 lần/ngày ICT (state file); PASS xoá state ⇒ lỗi lại thì báo lại.
# Bảng khôi phục ⇒ lần chạy kế PASS, tự đi tiếp, không cần tay.
#
# Env (selfcheck/ghi đè): GATE_FAKE_MEASURE="n_distinct,n_universe,n_cov,max_t,univ_date" hoặc "ERROR:<text>",
#   GATE_FAKE_LM (ngày sửa bảng), FA8L_BQ_CMD (thay lệnh `bq`), GATE_BQ_TIMEOUT (s), GATE_STATE_DIR, FA8L_NOTIFY, FA8L_EVENT, GATE_MIN_DISTINCT/COV/UNIVERSE.
set -uo pipefail

ROOT="/home/trido/thanhdt/WorkingClaude"
MIKE="${MIKE_ROOT_OVERRIDE:-$ROOT/mike}"
PROJECT="lithe-record-440915-m9"
MIN_DISTINCT="${GATE_MIN_DISTINCT:-1250}"
MIN_COV="${GATE_MIN_COV:-0.98}"
MIN_UNIVERSE="${GATE_MIN_UNIVERSE:-300}"
STATE_DIR="${GATE_STATE_DIR:-$MIKE/state}"
STATE="$STATE_DIR/fa_ratings_ticker_gate_alerted.txt"
NOTIFY="${FA8L_NOTIFY:-$MIKE/bin/notify_thread.sh}"
EVENT="${FA8L_EVENT:-$MIKE/bin/append_event.sh}"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"

SQL="WITH tk AS (SELECT t.ticker, MAX(t.time) AS last_t FROM tav2_bq.ticker AS t GROUP BY t.ticker),
ud AS (SELECT MAX(u.time) AS d FROM tav2_mike.universe_pit AS u),
un AS (SELECT u.ticker FROM tav2_mike.universe_pit AS u, ud WHERE u.time = ud.d AND u.in_universe)
SELECT (SELECT COUNT(*) FROM tk) AS n_distinct,
       (SELECT COUNT(*) FROM un) AS n_universe,
       (SELECT COUNT(*) FROM un JOIN tk USING (ticker) WHERE tk.last_t >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 30 DAY)) AS n_cov,
       CAST((SELECT MAX(last_t) FROM tk) AS STRING) AS max_t,
       CAST((SELECT d FROM ud) AS STRING) AS univ_date"

if [ -n "${GATE_FAKE_MEASURE:-}" ]; then
  RAW="$GATE_FAKE_MEASURE"
  LM="${GATE_FAKE_LM:-unknown}"
else
  # stderr tách riêng (warning của SDK không làm hỏng header); rc≠0/timeout vẫn fail-closed.
  _errf="$(mktemp)"
  _out="$(source "$ROOT/wc_env.sh" 2>/dev/null; timeout "${GATE_BQ_TIMEOUT:-180}" ${FA8L_BQ_CMD:-bq} query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet "$SQL" 2>"$_errf")"
  _rc=$?
  if [ "$_rc" -eq 0 ] && [ "$(printf '%s\n' "$_out" | head -n1)" = "n_distinct,n_universe,n_cov,max_t,univ_date" ]; then
    RAW="$(printf '%s\n' "$_out" | sed -n 2p | tr -d '\r')"
  else
    RAW="ERROR:bq rc=$_rc: $(printf '%s %s' "$_out" "$(cat "$_errf")" | tr '\n' ' ' | cut -c1-300)"
  fi
  rm -f "$_errf"
  LM="$(source "$ROOT/wc_env.sh" 2>/dev/null; ${FA8L_BQ_CMD:-bq} show --format=prettyjson "${PROJECT}:tav2_bq.ticker" 2>/dev/null | python3 -c "
import json,sys,datetime as dt
try: print(dt.datetime.fromtimestamp(int(json.load(sys.stdin)['lastModifiedTime'])/1000, dt.timezone(dt.timedelta(hours=7))).strftime('%F %H:%M ICT'))
except Exception: print('unknown')" 2>/dev/null)"
  LM="${LM:-unknown}"
fi

VERDICT="$(python3 - "$RAW" "$MIN_DISTINCT" "$MIN_COV" "$MIN_UNIVERSE" "$LM" <<'PY'
import sys
raw, min_d, min_c, min_u, lm = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
thr = f"ngưỡng: n_mã≥{min_d}, phủ≥{min_c}, n_universe≥{min_u}"
if raw.startswith("ERROR:"):
    print(f"FAIL|❌ fa_ratings_8l ticker-gate: truy vấn đo số mã LỖI — {raw[6:]} ({thr}; bảng ticker sửa lần cuối {lm})")
    sys.exit(0)
try:
    nd, nu, nc, max_t, ud = raw.split(",")
    nd, nu, nc = int(nd), int(nu), int(nc)
except Exception as e:
    print(f"FAIL|❌ fa_ratings_8l ticker-gate: không parse được số đo '{raw[:120]}' ({type(e).__name__}) ({thr}; bảng ticker sửa lần cuối {lm})")
    sys.exit(0)
cov = (nc / nu) if nu > 0 else 0.0
meas = f"n_mã={nd}, n_universe={nu}@{ud}, phủ={nc}/{nu}={cov:.3f}, max(time)={max_t}"
bad = []
if nd < min_d: bad.append(f"n_mã {nd} < {min_d}")
if nu < min_u: bad.append(f"n_universe {nu} < {min_u}")
if cov < min_c: bad.append(f"phủ {cov:.3f} < {min_c}")
if bad:
    print(f"FAIL|❌ fa_ratings_8l ticker-gate CHẶN refresh: {'; '.join(bad)}. Đo: {meas}. {thr}; bảng ticker sửa lần cuối {lm}")
else:
    print(f"PASS|✅ fa_ratings_8l ticker-gate PASS: {meas}. {thr}")
PY
)"
if [ -z "$VERDICT" ]; then   # Python đánh giá crash ⇒ vẫn chặn, nói rõ "không đo được"
  VERDICT="FAIL|❌ fa_ratings_8l ticker-gate: KHÔNG ĐO ĐƯỢC (bước đánh giá số đo lỗi/không trả kết quả; số đo thô='${RAW:0:120}') — chặn theo fail-closed"
fi
KIND="${VERDICT%%|*}"; MSG="${VERDICT#*|}"
echo "$MSG"

if [ "$KIND" = "PASS" ]; then
  rm -f "$STATE"
  exit 0
fi

# FAIL: cảnh báo + bus tối đa 1 lần/ngày ICT (cron thử lại không spam). State ghi CHỈ khi notify rc=0.
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%F)"
if [ "$(cat "$STATE" 2>/dev/null)" != "$TODAY" ]; then
  if "$NOTIFY" "$MSG — refresh_fa_ratings_8l.sh KHÔNG chạy rating_8l_history.py; tự chạy lại khi bảng khôi phục." trading_daily >/dev/null 2>&1; then
    mkdir -p "$STATE_DIR" && printf '%s' "$TODAY" > "$STATE.tmp" && mv -f "$STATE.tmp" "$STATE"
  else
    echo "WARN: notify thất bại — chưa ghi state, lần sau báo lại"
  fi
  _payload="$(python3 -c 'import json,sys;print(json.dumps({"detail":sys.argv[1],"measured_by":"fa_ratings_ticker_gate.sh query tav2_bq.ticker + tav2_mike.universe_pit"}))' "$MSG")"
  "$EVENT" Winston error "fa-ratings-ticker-gate-blocked" "$_payload" >/dev/null 2>&1 || true
fi
exit 3
