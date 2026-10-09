#!/usr/bin/env bash
# github_pat_expiry_check.sh — cảnh báo TRƯỚC khi GitHub PAT (credential git dùng cho backup) hết hạn.
#
# Vì sao tồn tại (retro-2026-10-08, user duyệt 2026-10-09): backup mike-fleet kẹt 1 lượt push vì
# PAT hết hạn; backup_freshness_check.sh chỉ phát hiện SAU ~8h. Hạn của fine-grained PAT được
# GitHub trả ngay trong header `github-authentication-token-expiration` của MỌI response API
# → đọc nó mỗi ngày là chặn được từ sớm.
#
# Gọi từ bin/backup_freshness_check.sh (cron 08:35 ICT). KHÔNG BAO GIỜ làm fail check chính:
# thoát 0 trong mọi trường hợp; lỗi thật (không lấy được credential / API lỗi) → ghi
# logs/github_pat_expiry.log + stderr (§29: lỗi thật phải thấy được), KHÔNG cảnh báo giả.
#   ≤14 ngày → 1 cảnh báo/ngày vào topic architecture; ≤3 ngày (kể cả đã quá hạn) → 🔴, vẫn mỗi ngày.
#   Không có header (token không hạn) → im lặng. Token KHÔNG bao giờ được in ra log/Discord/argv
#   (đi qua stdin của `curl -K -`).
# BACKUP_FRESHNESS_QUIET=1 ⇒ chỉ in stdout, không gửi Discord, không ghi stamp (test tay).
# Hook test (selfcheck): GITHUB_PAT_HEADERS_CMD = lệnh in ra "response headers" thay cho API thật
# (rc≠0 ⇒ giả lập lỗi mạng); GITHUB_PAT_NOW = epoch giả; GITHUB_PAT_STATE_DIR / _LOG_DIR.
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
STATE_DIR="${GITHUB_PAT_STATE_DIR:-$ROOT/state}"
LOG_DIR="${GITHUB_PAT_LOG_DIR:-$ROOT/logs}"
STAMP="$STATE_DIR/github_pat_expiry_alerted.txt"
WARN_DAYS=14
RED_DAYS=3
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOW="${GITHUB_PAT_NOW:-$(date -u +%s)}"

log_error() {
  mkdir -p "$LOG_DIR" 2>/dev/null
  printf '%s [github_pat_expiry] ERROR: %s\n' "$(date -u +%FT%TZ)" "$1" | tee -a "$LOG_DIR/github_pat_expiry.log" >&2
}

fetch_headers() {   # in response headers của 1 call API; token đi qua stdin, không lên argv
  local cred pass
  # -C $ROOT: credential.helper=store chỉ cấu hình trong .git/config của repo — cron chạy từ $HOME (không phải repo) sẽ rc=128
  cred="$(printf 'protocol=https\nhost=github.com\n\n' | GIT_TERMINAL_PROMPT=0 timeout 20 git -C "$ROOT" credential fill 2>/dev/null)" \
    || { echo "git credential fill thất bại (không lấy được credential github.com)" >&2; return 2; }
  pass="$(printf '%s\n' "$cred" | sed -n 's/^password=//p')"
  [ -n "$pass" ] || { echo "credential github.com không có password" >&2; return 2; }
  printf 'header = "Authorization: Bearer %s"\n' "$pass" \
    | timeout 30 curl -sS -K - -D - -o /dev/null --max-time 25 \
        -H 'Accept: application/vnd.github+json' https://api.github.com/user 2>&1 \
    || return 3
}

if [ -n "${GITHUB_PAT_HEADERS_CMD:-}" ]; then
  HDRS="$(bash -c "$GITHUB_PAT_HEADERS_CMD" 2>&1)"; rc=$?
else
  HDRS="$(fetch_headers 2>&1)"; rc=$?
fi
if [ "$rc" -ne 0 ]; then
  log_error "không đọc được header hạn PAT (rc=$rc): $(printf '%s' "$HDRS" | head -c 200 | tr '\n' ' ' | sed -E 's/(Bearer|token) +[A-Za-z0-9_]+/\1 ***/g')"
  exit 0
fi
HDRS="$(printf '%s\n' "$HDRS" | tr -d '\r')"
STATUS="$(printf '%s\n' "$HDRS" | awk 'toupper($1) ~ /^HTTP/ {s=$2} END{print s}')"
case "$STATUS" in
  200) ;;
  *) log_error "GitHub API trả HTTP '${STATUS:-?}' (không phải 200) — không kết luận được hạn PAT"; exit 0 ;;
esac
EXP_RAW="$(printf '%s\n' "$HDRS" | sed -n 's/^github-authentication-token-expiration: *//Ip' | head -1)"
if [ -z "$EXP_RAW" ]; then
  echo "🔑 [github_pat_expiry] token không có hạn (không có header) — bỏ qua."
  exit 0
fi
EXP_TS="$(date -u -d "$EXP_RAW" +%s 2>/dev/null)" \
  || { log_error "header hạn PAT không parse được: '$EXP_RAW'"; exit 0; }
DAYS=$(( (EXP_TS - NOW) / 86400 ))
[ $(( EXP_TS - NOW )) -lt 0 ] && DAYS=$(( -1 - (NOW - EXP_TS) / 86400 ))   # đã quá hạn ⇒ số âm
EXP_FMT="$(TZ=Asia/Ho_Chi_Minh date -d "@$EXP_TS" '+%Y-%m-%d %H:%M ICT')"
echo "🔑 [github_pat_expiry] PAT còn ${DAYS} ngày (hết hạn ${EXP_FMT})."
[ "$DAYS" -gt "$WARN_DAYS" ] && exit 0

TODAY="$(TZ=Asia/Ho_Chi_Minh date -d "@$NOW" +%F)"
if [ "$DAYS" -le "$RED_DAYS" ]; then ICON="🔴"; LEVEL="**SẮP HẾT HẠN**"; else ICON="🟡"; LEVEL="sắp hết hạn"; fi
MSG="$ICON [github_pat_expiry] GitHub PAT (backup mike-fleet) $LEVEL: hết hạn $EXP_FMT (còn ${DAYS} ngày).
Việc user phải làm: tạo token mới trên GitHub (Settings → Developer settings → PAT) rồi cập nhật ~/.git-credentials (dòng https://<user>:<token>@github.com). Quá hạn ⇒ backup đêm sẽ không push được."
printf '%s\n' "$MSG"
[ "${BACKUP_FRESHNESS_QUIET:-0}" = 1 ] && exit 0
if [ -f "$STAMP" ] && [ "$(cat "$STAMP" 2>/dev/null)" = "$TODAY" ]; then
  echo "(đã cảnh báo hôm nay $TODAY — không gửi lại)"
  exit 0
fi
if "$BIN_DIR/notify_thread.sh" "$MSG" architecture; then
  mkdir -p "$STATE_DIR" && printf '%s\n' "$TODAY" > "$STAMP"
else
  log_error "notify_thread.sh architecture thất bại — cảnh báo hạn PAT KHÔNG tới Discord (không ghi stamp, lần chạy sau thử lại)"
fi
exit 0
