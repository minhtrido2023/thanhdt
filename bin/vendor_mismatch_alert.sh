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
# Exit: 0 = KHÔNG có lệch nguồn nào · 10 = CÓ lệch nguồn · 2 = sai đối số.
#   ⚠️ 10 nói về SỰ TỒN TẠI của lệch nguồn, KHÔNG hứa "đã gửi được cảnh báo" — hai caller
#   (`check_report_cadence.sh:91`, `eod_trading_report.sh:72`) chỉ dùng nó để quy ĐÚNG nguyên
#   nhân/người xử lý (§29), nên nó phải đúng cả khi Discord chết. Gửi hỏng thì in LỖI THẬT ra
#   stderr và KHÔNG ghi de-dup ⇒ lượt sau thử lại.
#
# `state/vendor_mismatch_alerted.json` (de-dup 1 key/file báo cáo/ngày) TĂNG KHÔNG TRẦN, CÓ CHỦ Ý
# — cùng quy ước với `state/report_delivery_incomplete_alerted.json` của check_report_cadence.sh:61
# (cũng không TTL, không chủ dọn). Chấp nhận được vì tốc độ tăng đo thật ~0: K1 2026-09-24 đếm
# **0 lệch nguồn / 62 sự kiện cổ tức 6 tháng** ⇒ key chỉ sinh khi có lệch thật. Không cài cron dọn.
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
# State hỏng/cụt (kill giữa lúc ghi ở bản trước) KHÔNG được làm câm cảnh báo: coi như CHƯA
# cảnh báo (fail-open về phía GỬI) và in LỖI THẬT (§29 — không nuốt stderr rồi đoán).
# Giá trị đi qua ENV chứ không nội suy vào nguồn python: tên file báo cáo là dữ liệu ngoài.
ALREADY="$(STATE="$STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys
try:
    state = json.load(open(os.environ['STATE']))
except Exception as e:
    print('no')
    sys.stderr.write('vendor_mismatch_alert: KHONG doc duoc state de-dup %s — coi nhu CHUA canh bao, VAN gui. Loi that: %s: %s\n'
                     % (os.environ['STATE'], type(e).__name__, e))
    sys.exit(0)
print('yes' if state.get(os.environ['FNAME']) == os.environ['TODAY'] else 'no')
")"
if [ "$ALREADY" = "yes" ]; then
  echo "vendor_mismatch_alert: đã cảnh báo $FNAME hôm nay, bỏ qua (de-dup)." >&2
  exit 10
fi

MSG="⚠️ **LỆCH NGUỒN CỔ TỨC — cần Winston (data-ops)** — \`${FNAME}\`
Tiền cổ tức THẬT về tài khoản (sổ broker) và bảng vendor \`tav2_bq.corporate_action\` đang cho hai số KHÁC nhau:${DETAIL}

**Việc cần làm:** Winston đối soát \`tav2_bq.corporate_action\` với sổ broker cho (mã, ex-date) trên. Chỉ khi hai nguồn khớp lại thì tỉ suất mã đó mới được công bố (§21).
Đây KHÔNG phải lỗi soạn báo cáo và KHÔNG phải sai cơ sở giá — không nới dung sai cổng để gỡ chặn."

PAYLOAD="{\"artifact\":\"${FNAME}\",\"owner\":\"Winston\",\"blocked_report\":${BLOCKED},\"markers\":$(printf '%s\n' "$MARKERS" | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')}"

# BUS = kênh PHỤ. Hỏng thì nêu lỗi thật rồi ĐI TIẾP — không được vì bus mà chặn đường tới user.
if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Mike error "vendor-mismatch-${FNAME}" "$PAYLOAD" 2>&1 >/dev/null)"; then
  echo "vendor_mismatch_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
fi

# DISCORD = kênh CHÍNH và là ĐIỀU KIỆN để ghi de-dup. Trước đây `2>/dev/null || true` + ghi state
# vô điều kiện: ccdb chết/topic sai ⇒ lỗi bị nuốt, state vẫn ghi "đã cảnh báo hôm nay", và ở ca
# rc=0 (mã không công bố) báo cáo ĐÃ giao xong nên sweep hôm sau không quay lại file đó nữa
# ⇒ MẤT CẢNH BÁO VĨNH VIỄN — đúng thứ script này sinh ra để chặn.
if ! NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>&1 >/dev/null)"; then
  echo "vendor_mismatch_alert: notify_thread.sh THAT BAI — KHONG ghi de-dup, luot sau se thu lai. Loi that: ${NOTIFY_ERR}" >&2
  exit 10
fi

# Ghi NGUYÊN TỬ (tmp + os.replace, §5): kill giữa lúc ghi không được để lại JSON cụt cho lượt
# sau `json.load` vấp. State không đọc được thì dựng lại từ {} — thà mất de-dup (cảnh báo lặp)
# còn hơn mất cảnh báo.
STATE="$STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys, tempfile
path = os.environ['STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('vendor_mismatch_alert: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e), file=sys.stderr)
    state = {}
state[os.environ['FNAME']] = os.environ['TODAY']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.vendor_mismatch_alerted.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
"
exit 10
