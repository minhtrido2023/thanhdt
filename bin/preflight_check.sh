#!/usr/bin/env bash
# preflight_check.sh — kiểm tra sẵn sàng trước khi bot thực thi lệnh.
# Chạy 08:45 ICT mỗi ngày giao dịch (cron: 45 1 * * 1-5).
# Exit 0 = GREEN (mọi thứ OK). Exit 1 = RED (có vấn đề, bot KHÔNG nên chạy).
# Luôn post kết quả vào Discord trading thread.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"
# Trading Daily — mọi nội dung giao dịch hàng ngày gộp về 1 thread cố định (không phụ thuộc
# session Mike gần nhất mở từ thread nào).
DISCORD_TRADING_THREAD="1521470705563340910"

FAILED=0
LINES=()

_ok()   { LINES+=("✅ $1"); }
_warn() { LINES+=("⚠️  $1"); }
_fail() { LINES+=("❌ $1"); FAILED=1; }

# ── 1. BOT_STOP kill-switch ───────────────────────────────────────────────────
if [ -f "$WORKDIR/data/BOT_STOP" ]; then
  _fail "BOT_STOP tồn tại — bot bị khoá thủ công. Xoá file để mở khoá."
else
  _ok "BOT_STOP: CLEAR"
fi

# ── 2. Plan hôm nay tồn tại + đã approve ─────────────────────────────────────
PLAN_FILE="$WORKDIR/data/trade_plans/plan_SpaceX_${TODAY}.json"
# fallback: plan_<account>_<date>.json nếu tên khác
if [ ! -f "$PLAN_FILE" ]; then
  PLAN_FILE="$(ls -t "$WORKDIR"/data/plan_SpaceX_${TODAY}.json \
                      "$WORKDIR"/data/trade_plans/plan_SpaceX_${TODAY}.json \
                      "$WORKDIR"/data/plan_*_${TODAY}.json 2>/dev/null | head -1 || true)"
fi

if [ -z "${PLAN_FILE:-}" ] || [ ! -f "${PLAN_FILE:-}" ]; then
  _fail "Plan $TODAY KHÔNG TÌM THẤY — DollarBill chưa lập plan hoặc BQ stale."
else
  PLAN_INFO=$(python3 - "$PLAN_FILE" 2>/dev/null <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
approved  = d.get("approved_by") or d.get("approved_by_user")
mafee_ok  = d.get("mafee_authorized", False)
mode      = d.get("mode", "?")
n_orders  = len(d.get("orders", []))
nav_b     = (d.get("nav_basis") or {}).get("account_nav", 0) / 1e9
est_val   = sum(o.get("est_value", 0) for o in d.get("orders", [])) / 1e9
state_nm  = d.get("state_name", d.get("state", "?"))
src       = d.get("state_source", "?")
rc        = d.get("risk_checks", {})
rc_ok     = all("PASS" in str(v) or "CLEAR" in str(v) or "HEALTHY" in str(v) or "VALID" in str(v) or "N/A" in str(v)
                for v in rc.values()) if rc else None
flags = []
if not approved:   flags.append("NOT_APPROVED")
if not mafee_ok:   flags.append("MAFEE_NOT_AUTH")
if mode != "live": flags.append(f"mode={mode}")
if rc_ok is False: flags.append("RISK_CHECK_FAIL")
print(f"{approved}|{mafee_ok}|{mode}|{n_orders}|{est_val:.3f}|{state_nm}|{src}|{'|'.join(flags) if flags else 'OK'}")
PY
  )

  IFS='|' read -r _approved _mafee _mode _n_orders _est _state_nm _src _flags <<< "$PLAN_INFO"

  if [ "$_flags" = "OK" ]; then
    _ok "Plan $TODAY: $_n_orders lệnh, ~${_est}B VND, state=$_state_nm ($_src), approved=$_approved"
  else
    _fail "Plan $TODAY: $_flags — orders=$_n_orders approved=$_approved mafee=$_mafee"
  fi
fi

# ── 3. Macro health ───────────────────────────────────────────────────────────
HEALTH_FILE="$WORKDIR/data/macro_health.json"
if [ ! -f "$HEALTH_FILE" ]; then
  _fail "macro_health.json không tồn tại."
else
  HEALTH=$(python3 - "$HEALTH_FILE" 2>/dev/null <<'PY'
import json, sys, time, os
d = json.load(open(sys.argv[1]))
status = d.get("status","?")
sev    = d.get("sev","?")
src    = d.get("recommended_state_source","?")
mtime  = os.path.getmtime(sys.argv[1])
age_h  = (time.time() - mtime) / 3600
print(f"{status}|{sev}|{src}|{age_h:.1f}")
PY
  )
  IFS='|' read -r _hstatus _hsev _hsrc _hage <<< "$HEALTH"

  # Chấp nhận HEALTHY hoặc DEGRADED (SEV2); từ chối FAILED (SEV1)
  if [ "$_hstatus" = "FAILED" ]; then
    _fail "macro_health=FAILED (SEV1) — DT5G chạy DT4_only. Kiểm tra data pipeline."
  elif [ "$(echo "$_hage > 20" | bc -l 2>/dev/null)" = "1" ]; then
    _warn "macro_health OK ($_hstatus) nhưng file cũ ${_hage}h — daily_refresh chưa chạy tối qua?"
    _ok  "State source: $_hsrc"
  else
    _ok "macro_health: $_hstatus ($_hsrc, file ${_hage}h tuổi)"
  fi
fi

# ── 4. Gmail OAuth refresh_token ─────────────────────────────────────────────
GMAIL_TOKEN="$WORKDIR/secrets/gmail_oauth_token.json"
if [ ! -f "$GMAIL_TOKEN" ]; then
  _fail "gmail_oauth_token.json không tồn tại — auto-OTP sẽ thất bại."
else
  HAS_REFRESH=$(python3 -c "
import json
d=json.load(open('$GMAIL_TOKEN'))
print('yes' if d.get('refresh_token') else 'no')
" 2>/dev/null)
  if [ "$HAS_REFRESH" = "yes" ]; then
    _ok "Gmail OAuth: có refresh_token (tự refresh khi cần)"
  else
    _warn "Gmail OAuth: KHÔNG có refresh_token — OTP có thể fail nếu access_token hết hạn."
  fi
fi

# ── 5. BQ freshness (nhanh — chỉ check ticker_prune lag) ─────────────────────
BQ_LAG=$(bq query --use_legacy_sql=false --format=csv --quiet \
  --project_id=lithe-record-440915-m9 \
  "SELECT DATE_DIFF(CURRENT_DATE('Asia/Ho_Chi_Minh'), MAX(t.time), DAY) AS lag FROM \`lithe-record-440915-m9.tav2_bq.ticker_prune\` AS t" \
  2>/dev/null | tail -1 | tr -d '[:space:]' || echo "999")

if [ "$BQ_LAG" -le 2 ] 2>/dev/null; then
  _ok "BQ ticker_prune: lag=${BQ_LAG}d ✓"
else
  _warn "BQ ticker_prune: lag=${BQ_LAG}d — giá ref_price trong plan có thể cũ; kiểm tra trước khi đặt lệnh."
fi

# ── Tổng hợp + notify ─────────────────────────────────────────────────────────
echo "=== Preflight $TODAY $NOW_ICT ==="
for line in "${LINES[@]}"; do echo "  $line"; done

if [ "$FAILED" -eq 0 ]; then
  STATUS_ICON="🟢"
  STATUS_TEXT="GREEN — sẵn sàng giao dịch"
else
  STATUS_ICON="🔴"
  STATUS_TEXT="RED — CÓ VẤN ĐỀ, kiểm tra trước khi bot chạy"
fi

MSG="$STATUS_ICON **Preflight $TODAY $NOW_ICT** — $STATUS_TEXT"$'\n'
for line in "${LINES[@]}"; do MSG+="$line"$'\n'; done

"$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true

if [ -n "${DISCORD_TRADING_THREAD:-}" ]; then
  "$ROOT/bin/notify_thread.sh" "$MSG" "$DISCORD_TRADING_THREAD" 2>/dev/null || true
fi

"$ROOT/bin/append_event.sh" Mike status "preflight-$TODAY" \
  "{\"result\":\"$([ $FAILED -eq 0 ] && echo GREEN || echo RED)\",\"checks\":$(python3 -c "import json; print(json.dumps($(printf '[%s]' "$(IFS=,; printf '"%s",' "${LINES[@]}" | sed 's/,$//') ")))" 2>/dev/null || echo '[]')}" \
  2>/dev/null || true

exit "$FAILED"
