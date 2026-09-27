#!/usr/bin/env bash
# adjfactor_drift_alert.sh <topic> [--dry-run]     # output của detector đi qua STDIN
#
# Đưa cảnh báo LỆCH HỆ SỐ ĐIỀU CHỈNH CORP-ACTION tới user với ĐÚNG nguyên nhân và ĐÚNG người xử lý.
# Đây là LAYER 1 — **DETECT ONLY**: không công bố số nào, không sửa `Close`, không đụng
# `report_return_gate.py` / `dividend_adjusted_return.py`. Chạy SONG SONG với cổng §21 hiện có.
#
# Khuôn tái dùng nguyên vẹn từ `bin/vendor_mismatch_alert.sh` (đã qua 5 vòng arch-review):
#   · cổng/detector giữ THUẦN — không ghi bus từ trong nó (§5b); việc ghi bus/Discord ở đây;
#   · parse DÒNG MÁY ĐỌC với giá trị đã chuẩn hoá, KHÔNG grep văn xuôi (§28);
#   · Discord = kênh CHÍNH và là ĐIỀU KIỆN để ghi de-dup; bus = kênh PHỤ, hỏng thì nêu lỗi thật
#     rồi đi tiếp (§29 — không nuốt stderr);
#   · state de-dup ghi NGUYÊN TỬ (tmp + os.replace, §5); state hỏng ⇒ coi như CHƯA cảnh báo
#     (fail-open về phía GỬI) và in lỗi thật.
#
# KHÁC `vendor_mismatch_alert.sh` ở MỘT điểm có chủ ý — KHOÁ DE-DUP:
#   `vendor_mismatch_alert.sh` de-dup theo (file báo cáo, ngày) vì mỗi ngày là một báo cáo MỚI.
#   Ở đây không có báo cáo nào; sự kiện là (mã, ex-date) và nó TỒN TẠI LIÊN TỤC tới khi vendor
#   backfill. Detector chạy hằng ngày với cohort ex-date 30 ngày ⇒ de-dup theo ngày sẽ bắn FPT
#   30 lần. Khoá là `<mã>|<ex-date>` + ngày cảnh báo cuối, nhắc lại sau `RE_ALERT_DAYS`=7 ngày
#   nếu vẫn còn lệch. Im lặng hoàn toàn sau lần đầu cũng sai — một lỗi chưa ai sửa phải còn nhắc.
#
# UNCOMPUTABLE: LUÔN được in ra stdout của detector (⇒ vào log cron) và LUÔN nằm trong payload bus
# — không bao giờ im lặng, không bao giờ bị coi là "khớp" (yêu cầu #4 của dispatch). Nhưng chỉ mã
# đang NẮM LIVE mới được nêu tên trên Discord: uncomputable là trạng thái BÌNH THƯỜNG của quyền mua
# cổ đông hiện hữu (26/83 mã cohort control) và của guard ffill `Price` trên mã mỏng — bắn Discord
# mỗi ngày cho nó là dạy người ta bỏ qua đúng cái topic cần đọc.
#
# Exit: 0 = không có gì để cảnh báo · 10 = đã có cảnh báo (hoặc dry-run có nội dung) · 2 = sai đối số.
#   ⚠️ 10 nói về SỰ TỒN TẠI của cảnh báo, KHÔNG hứa "đã gửi được" — Discord hỏng thì in LỖI THẬT ra
#   stderr, KHÔNG ghi de-dup, và vẫn trả 10 (lượt sau của cron sẽ thử lại vì de-dup chưa ghi).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RE_ALERT_DAYS=7
# Trần số dòng của khối "mã KHÔNG nắm" trên Discord. `notify_thread.sh` tự chunk ở 1900 ký tự nên
# một tuần 16 mã lệch KHÔNG làm gửi hỏng — nó chia thành 4 tin, và 4 tin cho một việc không phải
# tiền thật là đúng cách để dạy người ta cuộn qua topic. Khối mã ĐANG NẮM LIVE **không bao giờ bị
# cắt** (đó là phần thành tiền); danh sách đầy đủ luôn nằm trong payload bus và stdout của detector.
MAX_OTHER_LINES=6
BT='`'   # §15: backtick trong chuỗi nháy kép là command substitution — dùng biến, không escape

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <topic> [--dry-run]   # output detector qua stdin" >&2
  exit 2
fi
TOPIC="$1"
DRY_RUN=0
[ "${2:-}" = "--dry-run" ] && DRY_RUN=1

DET_OUT="$(cat)"
DRIFTS="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_DRIFT\|' || true)"
UNCOMPS="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_UNCOMPUTABLE\|' || true)"
SCAN="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_SCAN\|' | tail -1 || true)"
[ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ] && exit 0

IFS='|' read -r _stag ASOF N_SCANNED N_DRIFT N_UNCOMP N_AGREE N_NODATA <<< "${SCAN:-|?|?|?|?|?|?}"

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
STATE="$ROOT/state/adjfactor_drift_alerted.json"
mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

# Khoá nào đã cảnh báo trong vòng RE_ALERT_DAYS ngày ⇒ bỏ khỏi câu Discord (vẫn ở trong bus).
# Giá trị đi qua ENV, không nội suy vào nguồn python (dữ liệu ngoài).
FRESH_KEYS="$(STATE="$STATE" TODAY="$TODAY" DAYS="$RE_ALERT_DAYS" python3 -c "
import datetime, json, os, sys
try:
    state = json.load(open(os.environ['STATE']))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    sys.stderr.write('adjfactor_drift_alert: KHONG doc duoc state de-dup %s — coi nhu CHUA canh bao '
                     'khoa nao, VAN gui. Loi that: %s: %s\n' % (os.environ['STATE'], type(e).__name__, e))
    sys.exit(0)
today = datetime.date.fromisoformat(os.environ['TODAY'])
days = int(os.environ['DAYS'])
for k, v in state.items():
    try:
        age = (today - datetime.date.fromisoformat(str(v))).days
    except ValueError as e:
        sys.stderr.write('adjfactor_drift_alert: khoa %r co ngay %r khong doc duoc (%s) — coi nhu CHUA '
                         'canh bao khoa nay\n' % (k, v, e))
        continue
    if 0 <= age < days:
        print(k)
")"

_is_fresh() {
  printf '%s\n' "$FRESH_KEYS" | grep -Fxq "$1"
}

_pct() { python3 -c "import sys; print('%+.2f%%' % (float(sys.argv[1]) * 100))" "$1"; }

DETAIL_HELD=""
DETAIL_OTHER=""
NEW_KEYS=""
N_NEW=0
N_HELD=0
N_OTHER=0
SEEN_VENDOR=0
SEEN_OURS=0
while IFS='|' read -r _tag tk ex r_obs r_pred dev run d0 d1 dir held; do
  [ -z "${tk:-}" ] && continue
  key="${tk}|${ex}"
  _is_fresh "$key" && continue
  N_NEW=$((N_NEW + 1))
  NEW_KEYS="${NEW_KEYS}${key}"$'\n'
  case "$dir" in
    vendor_missing) SEEN_VENDOR=1
      cause="vendor \`tav2_bq.ticker.Close\` THIẾU hệ số (r_obs ${r_obs} < r_pred ${r_pred})" ;;
    our_table_missing) SEEN_OURS=1
      cause="\`corporate_action\` của TA nghi thiếu một mắt xích (r_obs ${r_obs} > r_pred ${r_pred})" ;;
    *) cause="KHÔNG xác định được chiều lệch (dir=${dir}) — kiểm thủ công, KHÔNG suy đoán bên nào sai" ;;
  esac
  line="
• **${tk}** (ex ${ex}): lệch $(_pct "$dev") liên tục **${run} phiên** ${d0}..${d1} — ${cause}"
  if [ "$held" = "none" ] || [ "$held" = "unknown" ]; then
    N_OTHER=$((N_OTHER + 1))
    if [ "$N_OTHER" -le "$MAX_OTHER_LINES" ]; then
      DETAIL_OTHER="${DETAIL_OTHER}${line}"
    fi
  else
    N_HELD=$((N_HELD + 1))
    DETAIL_HELD="${DETAIL_HELD}${line} — **ĐANG NẮM LIVE: ${held}**"
  fi
done <<< "$DRIFTS"

# UNCOMPUTABLE: chỉ nêu tên trên Discord các mã đang NẮM LIVE (xem header). Phần còn lại chỉ đếm.
DETAIL_UNCOMP=""
N_UNCOMP_HELD=0
N_UNCOMP_OTHER=0
while IFS='|' read -r _tag tk ex code held; do
  [ -z "${tk:-}" ] && continue
  if [ "$held" = "none" ] || [ "$held" = "unknown" ]; then
    N_UNCOMP_OTHER=$((N_UNCOMP_OTHER + 1))
    continue
  fi
  N_UNCOMP_HELD=$((N_UNCOMP_HELD + 1))
  DETAIL_UNCOMP="${DETAIL_UNCOMP}
• **${tk}** (ex ${ex}, ${held}): \`${code}\` — KHÔNG tính được hệ số, **không kết luận là khớp**"
done <<< "$UNCOMPS"

# BUS trước (kênh PHỤ, luôn ghi kể cả khi Discord im vì de-dup) — đây là dấu vết audit đầy đủ:
# mọi DRIFT và mọi UNCOMPUTABLE của lượt quét, không qua bộ lọc de-dup/held nào.
PAYLOAD="$(ASOF="$ASOF" N_SCANNED="$N_SCANNED" N_DRIFT="$N_DRIFT" N_UNCOMP="$N_UNCOMP" \
  N_AGREE="$N_AGREE" N_NODATA="$N_NODATA" N_NEW="$N_NEW" N_HELD="$N_HELD" \
  DRIFTS="$DRIFTS" UNCOMPS="$UNCOMPS" python3 -c "
import json, os
def lines(v):
    return [l.strip() for l in os.environ[v].splitlines() if l.strip()]
print(json.dumps({
    'layer': 'layer1-detect-only',
    'asof': os.environ['ASOF'],
    'scanned': os.environ['N_SCANNED'], 'drift': os.environ['N_DRIFT'],
    'uncomputable': os.environ['N_UNCOMP'], 'agree': os.environ['N_AGREE'],
    'nodata': os.environ['N_NODATA'],
    'new_since_last_alert': os.environ['N_NEW'], 'drift_held_live': os.environ['N_HELD'],
    'published_any_number': False,
    'drift_markers': lines('DRIFTS'), 'uncomputable_markers': lines('UNCOMPS'),
}, ensure_ascii=False))
")"

if [ "$DRY_RUN" -eq 0 ]; then
  if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Taylor finding "adjfactor-drift-scan-${ASOF}" "$PAYLOAD" 2>&1 >/dev/null)"; then
    echo "adjfactor_drift_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
  fi
fi

if [ "$N_NEW" -eq 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ]; then
  echo "adjfactor_drift_alert: ${N_DRIFT} lech nhung tat ca da canh bao trong ${RE_ALERT_DAYS} ngay qua" \
       "va khong co uncomputable nao dang nam LIVE -> chi ghi bus, khong gui Discord (de-dup)." >&2
  exit 10
fi

SECTIONS=""
[ -n "$DETAIL_HELD" ] && SECTIONS="${SECTIONS}
__**Mã ĐANG NẮM LIVE — ưu tiên:**__${DETAIL_HELD}
"
if [ -n "$DETAIL_OTHER" ]; then
  # Detector in dòng DRIFT theo |lệch| GIẢM DẦN ⇒ 6 dòng đầu là 6 mã nặng nhất, không phải 6 mã
  # tình cờ đứng đầu bảng chữ cái.
  more=""
  if [ "$N_OTHER" -gt "$MAX_OTHER_LINES" ]; then
    more="$(printf '\n… và %d mã nữa (lệch nhẹ hơn) — danh sách đầy đủ ở event bus %sadjfactor-drift-scan-%s%s và log cron.' \
      "$((N_OTHER - MAX_OTHER_LINES))" "$BT" "$ASOF" "$BT")"
  fi
  SECTIONS="${SECTIONS}
__**Mã không nắm (chỉ ảnh hưởng nghiên cứu/backtest đọc lịch sử):**__${DETAIL_OTHER}${more}
"
fi
[ -n "$DETAIL_UNCOMP" ] && SECTIONS="${SECTIONS}
__**KHÔNG TÍNH ĐƯỢC hệ số (fail-closed, mã đang nắm):**__${DETAIL_UNCOMP}
"

TODO=""
[ "$SEEN_VENDOR" = "1" ] && TODO="${TODO}
- **Vendor thiếu hệ số điều chỉnh:** Winston (data-ops) yêu cầu backfill \`tav2_bq.ticker\`/\`ticker_prune\` cho các (mã, ex-date) trên. Chữ ký đã biết: hệ số chỉ chạm **4 phiên cum cuối** (\`SETTLE_RUN=4\`) rồi dừng — nhánh fallback hẹp của ETL chạy, còn bản rewrite toàn cửa sổ (gated \`need_cafef\`) KHÔNG chạy."
[ "$SEEN_OURS" = "1" ] && TODO="${TODO}
- **Nghi \`corporate_action\` của TA thiếu mắt xích:** Taylor đối chiếu sự kiện thật của mã đó (chiều lệch NGƯỢC lại: vendor có hệ số mà ta không suy ra được). Đây là GỢI Ý ĐIỀU HƯỚNG theo dấu của lệch, KHÔNG phải bằng chứng."
[ "$N_UNCOMP_HELD" -gt 0 ] && TODO="${TODO}
- **Mã nắm LIVE không tính được hệ số:** \`rights_issue_no_subscription_price\` = giá phát hành không có trong \`corporate_action\` (cột \`ref_price\` NULL toàn bộ từ 2025-01-01) ⇒ Layer 1 KHÔNG kết luận được gì cho mã đó, cổng §21 vẫn là lớp bảo vệ duy nhất. \`price_ffill_suspect\` = \`Price\` phiên cum cuối nằm ngoài band ⇒ Winston kiểm dòng giá đó."

MSG="⚠️ **LỆCH HỆ SỐ ĐIỀU CHỈNH CORP-ACTION (Layer 1 — CHỈ PHÁT HIỆN)** — asof \`${ASOF}\`
Hệ số tự suy từ \`tav2_bq.corporate_action\` không khớp hệ số ẩn trong \`tav2_bq.ticker\` (\`Price\`/\`Close\`), lệch >0,3% kéo dài ≥3 phiên liên tiếp:
${SECTIONS}
**Việc cần làm:**${TODO}

_Quét ${N_SCANNED} mã: ${N_DRIFT} lệch · ${N_UNCOMP} không tính được · ${N_AGREE} khớp · ${N_NODATA} không có dữ liệu. ${N_UNCOMP_OTHER} uncomputable của mã không nắm chỉ ghi bus, không nêu ở đây._
_Layer 1 **KHÔNG công bố và KHÔNG sửa** số nào — cổng §21 (\`report_return_gate\`) vẫn là lớp chặn báo cáo, không thay đổi._"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] topic=$TOPIC asof=$ASOF new=$N_NEW held=$N_HELD uncomp_held=$N_UNCOMP_HELD"
  echo "[dry-run] --- payload bus ---"
  echo "$PAYLOAD"
  echo "[dry-run] --- Discord ---"
  echo "$MSG"
  exit 10
fi

# DISCORD = kênh CHÍNH và là ĐIỀU KIỆN để ghi de-dup. Gửi hỏng ⇒ KHÔNG ghi state (sổ sách không
# được nói "đã cảnh báo" khi chưa gửi được gì) ⇒ lượt cron kế tiếp thử lại đúng các khoá này.
if ! NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>&1 >/dev/null)"; then
  echo "adjfactor_drift_alert: notify_thread.sh THAT BAI — KHONG ghi de-dup, luot sau thu lai. Loi that: ${NOTIFY_ERR}" >&2
  exit 10
fi

STATE="$STATE" TODAY="$TODAY" NEW_KEYS="$NEW_KEYS" python3 -c "
import json, os, sys, tempfile
path = os.environ['STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('adjfactor_drift_alert: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e),
          file=sys.stderr)
    state = {}
for k in os.environ['NEW_KEYS'].splitlines():
    if k.strip():
        state[k.strip()] = os.environ['TODAY']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.adjfactor_drift_alerted.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False, sort_keys=True)
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
