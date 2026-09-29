#!/usr/bin/env bash
# price_xcheck_alert.sh <artifact_basename> <topic> [--dry-run]   # markers qua STDIN
#
# Đưa cảnh báo LỆCH GIÁ THẬT tới Winston khi `close_repair.price_crosscheck` (Việc nhỏ 3,
# 2026-09-29, job Taylor_20260929_032553) phát hiện hệ số công thức từ `corporate_action` LỆCH
# biến động giá THẬT quanh ex-date quá `close_repair.PRICE_XCHECK_TOL` (20% — xem comment block
# ngay trên `PRICE_XCHECK_TOL` trong close_repair.py để biết bằng chứng hiệu chỉnh và giới hạn đã
# công bố của phương pháp). Đây là chiều lỗi bất biến đơn điệu
# (`paper_entry_adjust._repaired_series_violation`, Việc nhỏ 2) KHÔNG bắt được: corporate_action
# GHI SAI một sự kiện theo hướng làm hệ số CAO hơn thực (LÀM ĐẸP tỉ suất báo cáo), vì hướng này
# không phá vỡ tính đơn điệu của chuỗi đã sửa.
#
# Cùng khuôn với `vendor_mismatch_alert.sh` đã LIVE (Discord = kênh CHÍNH + điều kiện de-dup, bus =
# kênh phụ, ghi state NGUYÊN TỬ tmp+os.replace+fsync, dòng máy đọc riêng, chẩn đoán bám bằng chứng
# §29) nhưng KHÔNG mở rộng thẳng file đó: `vendor_mismatch_alert.sh` so BROKER TIỀN THẬT với
# `corporate_action` (đối soát CỔ TỨC), còn cảnh báo này so CÔNG THỨC corporate_action với GIÁ THỊ
# TRƯỜNG THẬT (không có "broker" nào trong phép so sánh) — khác nguồn dữ liệu, khác ngữ nghĩa "mã
# lý do", nên dùng TAG riêng thay vì tái dùng VENDOR_MISMATCH_ALERT.
#
# Dòng máy đọc kỳ vọng qua STDIN (một hoặc nhiều):
#   PRICE_XCHECK_MISMATCH|<ticker>|<asof>|<ex>|<f_formula>|<r_real>|<dev>
# (giá trị đã chuẩn hoá — không parse câu văn xuôi, §28). Sinh dòng này từ
# `close_repair.PriceCrossCheck` (mỗi phần tử tuple `price_mismatches` trong
# `paper_entry_adjust._repair_close`): `f"PRICE_XCHECK_MISMATCH|{ticker}|{asof}|{xc.ex}|"
# f"{xc.f_formula:.6f}|{xc.r_real:.6f}|{xc.dev:.6f}"`.
#
# ⚠️ CHƯA WIRE vào cron report nào — Việc nhỏ 3 chỉ yêu cầu detection (đã xong, đã qua 3 selfcheck
# + quant-skeptic) và đề xuất cơ chế cảnh báo; gọi script này từ `paper_programs_daily_report.py`
# hay tương đương là quyết định RIÊNG, để Mike/user chốt (cùng tinh thần đề xuất-không-tự-wire của
# Việc nhỏ 1). Test bằng dry-run thủ công, KHÔNG có bộ selfcheck đầy đủ như
# `vendor_mismatch_alert_selfcheck.sh` — tương xứng với việc chưa được gọi từ bất kỳ pipeline sống
# nào.
#
# Exit: 0 = không có marker nào · 10 = có marker (đã cảnh báo hoặc dry-run) · 2 = sai đối số.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <artifact_basename> <topic> [--dry-run]   # markers qua stdin" >&2
  exit 2
fi
FNAME="$1"
TOPIC="$2"
DRY_RUN=0
[ "${3:-}" = "--dry-run" ] && DRY_RUN=1

GATE_OUT="$(cat)"
MARKERS="$(printf '%s\n' "$GATE_OUT" | grep -E '^PRICE_XCHECK_MISMATCH\|' || true)"
[ -z "$MARKERS" ] && exit 0

DETAIL=""
while IFS='|' read -r _tag tk asof ex f_formula r_real dev; do
  [ -z "${tk:-}" ] && continue
  # dev đã là số thập phân (vd -0.437206) — in lại dạng % bằng awk, KHÔNG bash arithmetic (số
  # thực). Bám bằng chứng (§29): câu chẩn đoán chỉ nói "LỆCH ... theo công thức vs giá thật",
  # không đoán corporate_action sai THEO CHIỀU nào — đó là việc Winston tự đối soát.
  dev_pct="$(awk -v d="$dev" 'BEGIN{printf "%.2f", d*100}')"
  DETAIL="${DETAIL}
• **${tk}** (asof ${asof}, ex ${ex}): close_repair đã tự sửa Close (self_computed) nhưng hệ số công thức từ \`corporate_action\` (f=${f_formula}) LỆCH biến động giá THẬT quan sát quanh ex-date (r_real=${r_real}, dev=${dev_pct}%) vượt PRICE_XCHECK_TOL — entry đã bị hạ về REPAIR_PRICE_MISMATCH (giữ giá gốc, không công bố tỉ suất dựa trên số nghi ngờ)"
done <<< "$MARKERS"

MSG="⚠️ **LỆCH GIÁ THẬT TẠI EX-DATE — cần Winston (data-ops)** — \`${FNAME}\`
Cross-check độc lập (Việc nhỏ 3, \`close_repair.price_crosscheck\`) phát hiện hệ số corporate_action không khớp biến động giá thật tại (các) ex-date dưới đây:${DETAIL}

**Việc cần làm:** Winston đối soát lại \`tav2_bq.corporate_action\` cho (mã, ex-date) trên — kiểm tra exercise_ratio/value_per_share có đúng sự kiện thật không (sai/thiếu/trùng tranche). Đây là màn lọc THÔ (PRICE_XCHECK_TOL=20%, hiệu chỉnh thực nghiệm để tránh báo động giả trên nhiễu giao dịch 1 phiên bình thường) — không phải xác nhận chắc chắn có lỗi, chỉ là đủ lệch để đáng kiểm tra thủ công.

Entry liên quan đã tự hạ về REPAIR_PRICE_MISMATCH (giữ giá gốc, không công bố tỉ suất) — không cần gấp gáp gỡ chặn, chỉ cần đối soát đúng nguyên nhân."

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
STATE="$ROOT/state/price_xcheck_alerted.json"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] topic=$TOPIC file=$FNAME"
  echo "[dry-run]$DETAIL"
  exit 10
fi

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"
# De-dup 1 lần/file/ngày — cùng khuôn vendor_mismatch_alert.sh. State hỏng/cụt KHÔNG được làm câm
# cảnh báo: coi như CHƯA cảnh báo (fail-open về phía GỬI), in lỗi thật (§29).
ALREADY="$(STATE="$STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys
try:
    state = json.load(open(os.environ['STATE']))
except Exception as e:
    print('no')
    sys.stderr.write('price_xcheck_alert: KHONG doc duoc state de-dup %s — coi nhu CHUA canh bao, VAN gui. Loi that: %s: %s\n'
                     % (os.environ['STATE'], type(e).__name__, e))
    sys.exit(0)
print('yes' if state.get(os.environ['FNAME']) == os.environ['TODAY'] else 'no')
")"
if [ "$ALREADY" = "yes" ]; then
  echo "price_xcheck_alert: đã cảnh báo $FNAME hôm nay, bỏ qua (de-dup)." >&2
  exit 10
fi

PAYLOAD="{\"artifact\":\"${FNAME}\",\"owner\":\"Winston\",\"markers\":$(printf '%s\n' "$MARKERS" | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')}"

# BUS = kênh PHỤ. Hỏng thì nêu lỗi thật rồi đi tiếp — không được vì bus mà chặn đường tới user.
if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Mike error "price-xcheck-mismatch-${FNAME}" "$PAYLOAD" 2>&1 >/dev/null)"; then
  echo "price_xcheck_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
fi

# DISCORD = kênh CHÍNH và ĐIỀU KIỆN để ghi de-dup — hỏng thì KHÔNG ghi state, lượt sau thử lại.
if ! NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>&1 >/dev/null)"; then
  echo "price_xcheck_alert: notify_thread.sh THAT BAI — KHONG ghi de-dup, luot sau se thu lai. Loi that: ${NOTIFY_ERR}" >&2
  exit 10
fi

STATE="$STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys, tempfile
path = os.environ['STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('price_xcheck_alert: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e), file=sys.stderr)
    state = {}
state[os.environ['FNAME']] = os.environ['TODAY']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.price_xcheck_alerted.', suffix='.tmp')
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
