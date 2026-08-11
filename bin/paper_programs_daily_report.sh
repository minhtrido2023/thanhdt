#!/usr/bin/env bash
# paper_programs_daily_report.sh [--post] [--email] [--date YYYY-MM-DD]
# Báo cáo paper-trading hợp nhất hàng ngày (registry-driven, xem paper_programs_daily_report.py).
# Mặc định in ra stdout. --post = gửi vào Discord topic "Trading report" (tên registry: trading_report)
# qua notify_thread.sh (tự chunk <2000 chars). --email lưu đúng artifact Markdown đã render
# vào reports/ rồi gửi nó qua Gmail SMTP (HTML body + .md attachment).
# Luôn exit 0 khi render được report (kể cả có sleeve lỗi) — chỉ exit ≠0 khi python chết hẳn.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ="Asia/Ho_Chi_Minh"

TRADING_REPORT_TOPIC="trading_report"
POST=0
EMAIL=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --post) POST=1 ;;
    --email) EMAIL=1 ;;
    *) ARGS+=("$a") ;;
  esac
done

report="$(python3 "$ROOT/bin/paper_programs_daily_report.py" ${ARGS[@]+"${ARGS[@]}"} 2>&1)" || {
  # python chết hẳn (syntax/env) — vẫn báo trung thực thay vì rơi im lặng
  report="📋 Paper Programs Daily Report — LỖI RENDER
❌ paper_programs_daily_report.py không chạy được:
${report:0:800}
→ kiểm tra mike/bin/paper_programs_daily_report.py + registry."
}

echo "$report"
if [ "$POST" = "1" ]; then
  "$ROOT/bin/notify_thread.sh" "$report" "$TRADING_REPORT_TOPIC"
fi

if [ "$EMAIL" = "1" ]; then
  REPORT_DATE="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
  for ((i=0; i<${#ARGS[@]}; i++)); do
    if [ "${ARGS[i]}" = "--date" ] && [ $((i + 1)) -lt ${#ARGS[@]} ]; then
      REPORT_DATE="${ARGS[i + 1]}"
    fi
  done
  REPORT_FILE="$ROOT/reports/paper_programs_daily_report_${REPORT_DATE}.md"
  EMAIL_STATE="$ROOT/state/paper_programs_report_emailed.json"
  tmp="$(mktemp "$ROOT/reports/.paper_programs_daily_report_${REPORT_DATE}.XXXXXX")"
  printf '%s\n' "$report" > "$tmp"
  mv "$tmp" "$REPORT_FILE"

  mkdir -p "$ROOT/state"
  EMAIL_ALREADY="$(EMAIL_STATE="$EMAIL_STATE" REPORT_DATE="$REPORT_DATE" python3 - <<'PY'
import json, os
path = os.environ['EMAIL_STATE']
try:
    with open(path, encoding='utf-8') as f:
        state = json.load(f)
except (OSError, ValueError):
    state = {}
print('yes' if state.get(os.environ['REPORT_DATE']) else 'no')
PY
)"
  if [ "$EMAIL_ALREADY" = "yes" ]; then
    echo "ℹ️ Email paper-program report ${REPORT_DATE} đã gửi trước đó — bỏ qua bản trùng."
    exit 0
  fi

  # Cổng tỉ suất chỉ áp dụng báo cáo NAV/vị thế broker. Paper report không công bố các tỉ suất
  # đó; bỏ qua có nêu lý do tường minh để email không bị chặn oan.
  "$ROOT/bin/send_report_email.py" "$REPORT_FILE" \
    --subject "[Paper Trading] Daily Report — ${REPORT_DATE}" \
    --skip-return-gate "Paper-program report khong cong bo ty suat vi the broker"
  EMAIL_STATE="$EMAIL_STATE" REPORT_DATE="$REPORT_DATE" python3 - <<'PY'
import json, os, tempfile
path = os.environ['EMAIL_STATE']
try:
    with open(path, encoding='utf-8') as f:
        state = json.load(f)
except (OSError, ValueError):
    state = {}
state[os.environ['REPORT_DATE']] = 'sent'
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.paper_programs_report_emailed.')
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
    f.write('\n')
os.replace(tmp, path)
PY
fi
