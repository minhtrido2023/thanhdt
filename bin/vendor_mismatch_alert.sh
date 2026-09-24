#!/usr/bin/env bash
# vendor_mismatch_alert.sh <artifact_basename> <topic> [--dry-run]   # output cổng qua STDIN
#
# Đưa cảnh báo LỆCH NGUỒN VENDOR tới USER với ĐÚNG nguyên nhân và ĐÚNG người xử lý.
#
# Vì sao tồn tại (arch-review vòng 2, V3): `report_return_gate.py` in khối "⚠️ LỆCH NGUỒN VENDOR"
# ra stdout của nó, `report_delivery_gate.py:105` gọi nó bằng `subprocess.run(check=True)` KHÔNG
# capture ⇒ cả khối chảy vào stdout của cron = FILE LOG. Chỉ rc ra được ngoài. Hệ quả đo thật:
#   · mã lệch nguồn mà báo cáo KHÔNG công bố tỉ suất ⇒ rc=0 ⇒ 0 ký tự tới Discord/user;
#   · mã CÓ công bố ⇒ chặn đúng, nhưng dòng DUY NHẤT user thấy là "Delivery INCOMPLETE … cần
#     Taylor kiểm tra" — SAI nguyên nhân, SAI người (§29 ở tầng ngoài).
# Chỉ đạo user 2026-09-24: "hạ về unverified rồi RAISE WARNING LÊN ĐỂ TÔI KÊU WINSTON xử lý."
#
# Cổng giữ THUẦN (không ghi bus từ trong nó — §5b): việc ghi bus/Discord nằm ở đây, phía shell.
# Parse dòng MÁY ĐỌC `VENDOR_MISMATCH_ALERT|<acct>|<mã>|<ex>|<broker>|<vendor>|<đang công bố>`
# — giá trị đã chuẩn hoá, KHÔNG grep câu văn xuôi (§28).
#
# Exit: 0 = không có lệch nguồn nào · 10 = CÓ (đã alert, hoặc đã alert hôm nay rồi) · 2 = sai đối số.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <artifact_basename> <topic> [--dry-run]   # output cổng qua stdin" >&2
  exit 2
fi
FNAME="$1"
TOPIC="$2"
DRY_RUN=0
[ "${3:-}" = "--dry-run" ] && DRY_RUN=1

GATE_OUT="$(cat)"
MARKERS="$(printf '%s\n' "$GATE_OUT" | grep -E '^VENDOR_MISMATCH_ALERT\|' || true)"
[ -z "$MARKERS" ] && exit 0

DETAIL=""
BLOCKED=0
while IFS='|' read -r _tag acct tk ex broker vendor published; do
  [ -z "${tk:-}" ] && continue
  DETAIL="${DETAIL}
• **${tk}** (${acct}, ex ${ex}): broker giải ${broker}đ/cp vs \`corporate_action\` ${vendor}đ/cp"
  if [ "${published:-0}" = "1" ]; then
    BLOCKED=1
    DETAIL="${DETAIL} — mã này ĐANG công bố tỉ suất ⇒ báo cáo bị CHẶN"
  else
    DETAIL="${DETAIL} — báo cáo vẫn gửi (không công bố tỉ suất mã này), cổ tức đã bị bỏ khỏi kỳ vọng"
  fi
done <<< "$MARKERS"

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
STATE="$ROOT/state/vendor_mismatch_alerted.json"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] topic=$TOPIC file=$FNAME blocked=$BLOCKED"
  echo "[dry-run]$DETAIL"
  exit 10
fi

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"
# De-dup 1 lần/file/ngày — cùng khuôn ALREADY_ALERTED của check_report_cadence.sh:88 (sweep chạy
# lại mỗi ngày cho cùng 1 file kẹt; không de-dup là spam đúng cái topic user đang đọc).
ALREADY="$(python3 -c "
import json
state = json.load(open('$STATE'))
print('yes' if state.get('$FNAME') == '$TODAY' else 'no')
")"
if [ "$ALREADY" = "yes" ]; then
  echo "vendor_mismatch_alert: đã cảnh báo $FNAME hôm nay, bỏ qua (de-dup)." >&2
  exit 10
fi

MSG="⚠️ **LỆCH NGUỒN CỔ TỨC — cần Winston (data-ops)** — \`${FNAME}\`
Tiền cổ tức THẬT về tài khoản (sổ broker) và bảng vendor \`tav2_bq.corporate_action\` đang cho hai số KHÁC nhau:${DETAIL}

**Việc cần làm:** Winston đối soát \`tav2_bq.corporate_action\` với sổ broker cho (mã, ex-date) trên. Chỉ khi hai nguồn khớp lại thì tỉ suất mã đó mới được công bố (§21).
Đây KHÔNG phải lỗi soạn báo cáo và KHÔNG phải sai cơ sở giá — không nới dung sai cổng để gỡ chặn."

"$ROOT/bin/append_event.sh" Mike error "vendor-mismatch-${FNAME}" \
  "{\"artifact\":\"${FNAME}\",\"owner\":\"Winston\",\"blocked_report\":${BLOCKED},\"markers\":$(printf '%s\n' "$MARKERS" | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')}" \
  2>/dev/null || true
"$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>/dev/null || true
python3 -c "
import json
state = json.load(open('$STATE'))
state['$FNAME'] = '$TODAY'
json.dump(state, open('$STATE', 'w'), indent=2, ensure_ascii=False)
"
exit 10
