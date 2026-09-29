#!/usr/bin/env bash
# extreme_regime_dd_alert.sh — quét journal sau phiên bot, phát alert + email nếu
# EXTREME-regime gate đã fire trên account live hôm nay.
#
# Usage:
#   bin/extreme_regime_dd_alert.sh <account> [<date>]
#
# Idempotent: chỉ gửi 1 email/phiên/account (flag file prevents duplicate).
# Markers tìm: EXTREME_FLOOR_GUARD · EXTREME_PAUSE · EXTREME_DOWN sell-to-floor
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

ACCOUNT="${1:-SpaceX}"
DATE="${2:-$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)}"

JOURNAL="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${DATE}_journal.csv"
FLAG="$WC_ROOT/data/extreme_regime_alerted_${ACCOUNT}_${DATE}.flag"
REPORT_TMP="$ROOT/logs/extreme_regime_alert_${ACCOUNT}_${DATE}.md"

# Idempotency — đã gửi hôm nay thì thoát sạch
if [ -f "$FLAG" ]; then
  exit 0
fi

# Journal chưa có (HOLD day không có giao dịch) — thoát sạch
if [ ! -f "$JOURNAL" ]; then
  exit 0
fi

# Quét EXTREME markers — chỉ lấy cột event (col 2) và ticker (col 4)
# CSV header: ts,event,parent_id,ticker,side,...
EXTREME_LINES="$(awk -F',' '
  NR > 1 && ($2 ~ /^EXTREME_/ || $2 ~ /EXTREME_DOWN/) {
    print $1 "|" $2 "|" $4
  }
' "$JOURNAL" 2>/dev/null || true)"

if [ -z "$EXTREME_LINES" ]; then
  # Không có EXTREME marker nào — không cần alert
  exit 0
fi

# --- Có markers — tạo report và gửi alert ---

DT5G_STATE="UNKNOWN"
DT5G_FILE="$WC_ROOT/deploy_golive_dt5g_v4/golive_state_today.json"
if [ -f "$DT5G_FILE" ]; then
  DT5G_STATE="$(python3 -c "
import json
d = json.load(open('$DT5G_FILE'))
print(d.get('state_name', d.get('state', 'UNKNOWN')))
" 2>/dev/null || echo "UNKNOWN")"
fi

HR_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"

# Deduplicate: ticker → set of trigger types + first timestamp
SUMMARY="$(echo "$EXTREME_LINES" | awk -F'|' '
{
  ts=$1; trig=$2; ticker=$3
  if (!(ticker in first_ts)) first_ts[ticker] = ts
  triggers[ticker][trig] = 1
}
END {
  for (ticker in first_ts) {
    trig_list = ""
    for (t in triggers[ticker]) {
      trig_list = trig_list (trig_list ? ", " : "") t
    }
    print ticker "|" first_ts[ticker] "|" trig_list
  }
}
' 2>/dev/null || echo "$EXTREME_LINES" | head -5)"

N_TICKERS="$(echo "$EXTREME_LINES" | awk -F'|' '{print $3}' | sort -u | wc -l)"

# Tạo markdown report
cat > "$REPORT_TMP" << EOF
# ⚠️ EXTREME-Regime Gate Alert — ${ACCOUNT} ${DATE}

**Thời điểm phát hiện:** ${HR_ICT}
**Account:** ${ACCOUNT}
**DT5G state hôm nay:** ${DT5G_STATE}
**Số mã bị trigger:** ${N_TICKERS}

## Mã bị ảnh hưởng

| Mã | Lần đầu trigger | Loại trigger |
|---|---|---|
EOF

echo "$EXTREME_LINES" | awk -F'|' '
{
  ts=$1; trig=$2; ticker=$3
  if (!(ticker in first_ts)) first_ts[ticker] = ts
  triggers[ticker] = triggers[ticker] (triggers[ticker] ? ", " : "") trig
}
END {
  for (ticker in first_ts) {
    printf "| **%s** | %s | %s |\n", ticker, first_ts[ticker], triggers[ticker]
  }
}
' >> "$REPORT_TMP" 2>/dev/null || true

cat >> "$REPORT_TMP" << 'EOF'

## Ý nghĩa từng trigger

- **EXTREME_FLOOR_GUARD** — Giá bid đang cận sàn giá ngày (≤ 3% trên sàn). Bot đã TẠM DỪNG mua mã đó trong phiên.
- **EXTREME_PAUSE** — Drop ≥ 3-sigma trong cửa sổ 15 phút. Bot đã TẠM DỪNG mua.
- **EXTREME_DOWN sell-to-floor** — Cả hai điều kiện trên xác nhận. Bot đã SELL-TO-FLOOR (bán về giá sàn).

## Hành động đề xuất

Đây là alert tự động — **không phải lệnh bán**. Bot đã xử lý nội bộ (pause/floor).

Anh nên kiểm tra:
1. Nguyên nhân gốc (tin tức, corp-action, dump thị trường hay idiosyncratic?)
2. Vị thế hiện tại còn bao nhiêu (kiểm EOD report hoặc nhắn Mike tra journal)
3. Quyết định giữ/cắt thêm hay hold → nhắn Mike để dispatch DD đầy đủ nếu cần

EOF

# Thêm raw markers để tham khảo
echo "## Raw journal events (top 20)" >> "$REPORT_TMP"
echo "" >> "$REPORT_TMP"
echo '```' >> "$REPORT_TMP"
echo "$EXTREME_LINES" | head -20 >> "$REPORT_TMP"
echo '```' >> "$REPORT_TMP"

# Discord alert ngay
_tid="trading_daily"
"$ROOT/bin/notify_thread.sh" "⚠️ **EXTREME-regime gate fired — ${ACCOUNT} ${DATE}** | ${N_TICKERS} mã bị trigger | DT5G: ${DT5G_STATE} | Chi tiết qua email." "$_tid" 2>/dev/null || true

# Bus event
"$ROOT/bin/append_event.sh" Mike "finding" "extreme-regime-fired-${ACCOUNT}-${DATE}" \
  "{\"account\":\"$ACCOUNT\",\"date\":\"$DATE\",\"n_tickers\":$N_TICKERS,\"dt5g\":\"$DT5G_STATE\"}" 2>/dev/null || true

# Gửi email
cd "$WC_ROOT"
python3 mike/bin/send_report_email.py "$REPORT_TMP" \
  --subject "⚠️ [EXTREME gate] ${ACCOUNT} ${DATE} — ${N_TICKERS} mã cận sàn/drop mạnh" \
  2>/dev/null || true

# Flag idempotency
touch "$FLAG"

echo "[extreme_regime_dd_alert] ${ACCOUNT} ${DATE}: ${N_TICKERS} mã — alert gửi xong."
