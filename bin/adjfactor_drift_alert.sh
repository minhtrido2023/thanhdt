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
#   · state de-dup ghi NGUYÊN TỬ (tmp + os.replace, §5) dưới `flock`; state hỏng ⇒ coi như CHƯA
#     cảnh báo. EXIT: 0 = không có gì để báo · 10 = đã xử lý (gửi hoặc de-dup) · 11 = bỏ qua vì một
#     lượt khác đang giữ lock · 2 = sai đối số.
#     (fail-open về phía GỬI) và in lỗi thật.
#
# KHÁC `vendor_mismatch_alert.sh` ở MỘT điểm có chủ ý — KHOÁ DE-DUP:
#   `vendor_mismatch_alert.sh` de-dup theo (file báo cáo, ngày) vì mỗi ngày là một báo cáo MỚI.
#   Ở đây không có báo cáo nào; sự kiện là (mã, ex-date) và nó TỒN TẠI LIÊN TỤC tới khi vendor
#   backfill. Detector chạy hằng ngày với cohort ex-date 30 ngày ⇒ de-dup theo ngày sẽ bắn FPT
#   30 lần. Khoá là `<mã>|<ex-date>` + ngày cảnh báo cuối, nhắc lại sau `RE_ALERT_DAYS`=7 ngày
#   nếu vẫn còn lệch. Im lặng hoàn toàn sau lần đầu cũng sai — một lỗi chưa ai sửa phải còn nhắc.
#
# UNCOMPUTABLE / NODATA: LUÔN được in ra stdout của detector (⇒ vào log cron) và LUÔN nằm trong
# payload bus — không bao giờ im lặng, không bao giờ bị coi là "khớp" (yêu cầu #4 của dispatch).
# Nhưng chỉ mã CÓ THỂ đang nắm (`held` ≠ `none`, tức kể cả `unknown`) mới được nêu tên trên Discord,
# và **có de-dup riêng** theo khoá `<mã>|<ex>|<reason_code>` / `<mã>|nodata`: uncomputable là trạng
# thái BÌNH THƯỜNG của quyền mua cổ đông hiện hữu (26/83 mã cohort control) và của guard ffill
# `Price` trên mã mỏng — bắn Discord mỗi ngày cho nó là dạy người ta bỏ qua đúng cái topic cần đọc.
# (arch-review 2026-09-27 đo được bản đầu gửi CẢ BA lượt liên tiếp trên cùng input vì nhánh này
# không có de-dup và `N_UNCOMP_HELD > 0` luôn phá de-dup của nhánh DRIFT.)
#
# FEED: `ADJFACTOR_FEED|<status>|...` với status ≠ FRESH là hạng cảnh báo RIÊNG, KHÔNG de-dup theo
# (mã, ex) được (nó không thuộc mã nào) và LUÔN lên Discord. `tav2_bq.corporate_action` là bảng TRAP
# có writer NGOÀI repo; feed đứng im ⇒ mọi mã "khớp" ⇒ im lặng không phân biệt được với một tuần
# sạch, đúng lớp lỗi §14/§29.
#
# Exit: 0 = không có gì để cảnh báo · 10 = đã có cảnh báo (hoặc dry-run có nội dung) · 2 = sai đối số.
#   ⚠️ 10 nói về SỰ TỒN TẠI của cảnh báo, KHÔNG hứa "đã gửi được" — Discord hỏng thì in LỖI THẬT ra
#   stderr, KHÔNG ghi de-dup, và vẫn trả 10 (lượt sau của cron sẽ thử lại vì de-dup chưa ghi).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RE_ALERT_DAYS=7
PRUNE_DAYS=90     # dọn khoá de-dup cũ hơn mốc này (xem ghi chú ở bước ghi state)
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
NODATAS="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_NODATA\|' || true)"
FEED="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_FEED\|' | tail -1 || true)"
SCAN="$(printf '%s\n' "$DET_OUT" | grep -E '^ADJFACTOR_SCAN\|' | tail -1 || true)"

# Feed nguồn KHÔNG tươi là hạng cảnh báo RIÊNG và CAO nhất: `corporate_action` là bảng TRAP có
# writer ngoài repo, feed đứng im ⇒ mọi mã "khớp" ⇒ im lặng không phân biệt được với tuần sạch
# (arch-review 2026-09-27). Phải tới người, không de-dup theo (mã,ex) được vì nó không thuộc mã nào.
FEED_STATUS=""
FEED_REASON=""
if [ -n "$FEED" ]; then
  IFS='|' read -r _ftag FEED_STATUS FEED_ING FEED_PUB FEED_ROWS FEED_AGE FEED_REASON <<< "$FEED"
else
  # THIẾU dòng FEED = FAIL-CLOSED, không phải "feed ổn" (arch-review vòng 2, F5). Bản trước để
  # `FEED_STATUS=""` rồi coi rỗng như FRESH ở cả early-exit lẫn `FEED_BAD`, nên một detector không in
  # được marker (phiên bản cũ, output bị cắt, nhánh lỗi sớm) cho ra IM LẶNG HOÀN TOÀN. Đó đúng là
  # §28 dạng 3: suy "không có vấn đề" từ sự VẮNG MẶT của kênh — mà đây lại chính là kênh duy nhất
  # tồn tại để chống ca feed chết.
  FEED_STATUS="MISSING"
  FEED_REASON="detector KHONG in dong ADJFACTOR_FEED — khong biet feed con song hay khong; coi la DIEM MU, khong phai 'feed on'"
fi

IFS='|' read -r _stag ASOF N_SCANNED N_DRIFT N_UNCOMP N_AGREE N_NODATA <<< "${SCAN:-|?|?|?|?|?|?}"

# Universe RỖNG là điểm mù có rc=11 ở detector, nhưng nó KHÔNG sinh ra marker nào — nên bản trước
# thoát ở early-exit bên dưới TRƯỚC cả bước ghi bus: không Discord, không bus, rc=0. Tức là tài liệu
# §7 ("rc=11 → bus") sai đúng cho ca này (arch-review vòng 2, F2). Cohort 30 ngày rỗng là bất khả về
# cấu trúc ở VN (đo thật 95 mã cho cửa sổ 18 ngày) ⇒ 0 mã = feed/cohort hỏng, phải tới người.
EMPTY_UNIVERSE=0
[ "$N_SCANNED" = "0" ] && EMPTY_UNIVERSE=1

# Chỉ im lặng khi feed ĐÚNG LÀ FRESH, có mã được quét, và không có marker nào. `MISSING` và universe
# rỗng đều KHÔNG lọt qua đây.
[ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ] && [ -z "$NODATAS" ] \
  && [ "$FEED_STATUS" = "FRESH" ] && [ "$EMPTY_UNIVERSE" -eq 0 ] && exit 0

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
STATE="$ROOT/state/adjfactor_drift_alerted.json"
mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

# LOCK quanh toàn bộ đọc-sửa-ghi state (arch-review vòng 2, F9). Từng lần GHI đã nguyên tử
# (`mkstemp` + `os.replace`) nhưng đọc ở đây và ghi ở cuối là hai bước rời nhau: hai lượt chồng nhau
# (cron + một lần chạy tay) đều thấy state CŨ ⇒ cả hai gửi Discord, và khoá của lượt về sau ghi đè
# mất khoá của lượt về trước. Hướng fail là AN TOÀN (gửi thừa, không mất cảnh báo) nên không phải
# lỗi tiền, nhưng §5 đòi idempotence thì phải đúng cả khi chạy song song, không chỉ khi tuần tự.
# `flock` giữ suốt đời tiến trình qua FD 9; hết lock sau khi script thoát, kể cả khi bị kill.
# HAI ca KHÁC NHAU, không được gộp (arch-review vòng 3, R3-4):
#   (a) KHÔNG MỞ được file lock (thư mục read-only, hết inode, quyền sai) — đây là lỗi MÔI TRƯỜNG,
#       không phải tranh chấp. Bản trước gộp cả hai vào một thông điệp khẳng định "một lượt khác đang
#       chạy" + "sau 60s" trong khi nó chờ 0s và KHÔNG có lượt nào khác; bằng chứng thật
#       (`Permission denied`, `Bad file descriptor`) do bash in ra và bị vứt đi — §29 dạng 2, trong
#       code MỚI mà `diagnosis_evidence_gate.py` về cấu trúc không nhìn thấy được.
#       Xử lý: CHẠY TIẾP KHÔNG LOCK. Không có lock chỉ mất tính idempotent khi chạy song song (hướng
#       fail là GỬI THỪA), còn thoát ở đây thì mất CẢ cảnh báo — đúng điều header file này cấm.
#   (b) mở được nhưng KHÔNG giành được trong 60s ⇒ thật sự có lượt khác đang chạy ⇒ bỏ qua để không
#       gửi trùng. Nhưng vẫn phải ghi BUS trước khi thoát (dấu vết audit không được mất).
LOCK_SKIP=0
# ⚠️ THỨ TỰ redirect quan trọng: `$(exec 9>file 2>&1)` KHÔNG bắt được lỗi, vì redirect xử lý từ trái
# sang phải nên `9>file` thất bại trong khi stderr VẪN là stderr ngoài ⇒ `_LOCK_ERR` rỗng và thông
# điệp phải nói "khong ro" — tức lại đúng §29 dạng 1 trong chính bản vá cho §29 dạng 2. Đo thật:
# dạng A cho `captured=[]`, dạng B (2>&1 TRƯỚC) cho đúng dòng "Permission denied".
if _LOCK_ERR="$(exec 2>&1; exec 9>"$STATE.lock")" && [ -z "$_LOCK_ERR" ]; then
  exec 9>"$STATE.lock"
  flock -w 60 9 || LOCK_SKIP=1
else
  echo "adjfactor_drift_alert: KHONG MO duoc file lock $STATE.lock -> chay TIEP KHONG LOCK (chi mat" \
       "tinh idempotent khi chay song song; thoat o day se mat CA canh bao). Loi that: ${_LOCK_ERR}" >&2
fi

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
N_UNKNOWN=0
DETAIL_UNKNOWN=""
N_SKIPPED=0
DETAIL_SKIPPED=""
SEEN_VENDOR=0
SEEN_OURS=0
N_CORR=0
# `_rest` là BIẾN HỨNG bắt buộc (arch-review vòng 3, R3-7): `read` dồn toàn bộ phần còn lại vào
# biến CUỐI, nên nếu thiếu nó, một trường thứ 13 thêm về sau làm `corr` thành "1|extra" ⇒ so
# `= "1"` thất bại ⇒ **mất nhánh cờ đính chính** và dòng đó quay về "vendor THIẾU hệ số" + TODO cho
# Winston, tức tái lập đúng F4 một cách im lặng.
while IFS='|' read -r _tag tk ex r_obs r_pred dev run d0 d1 dir held corr _rest; do
  [ -z "${tk:-}" ] && continue
  key="${tk}|${ex}"
  _is_fresh "$key" && continue
  N_NEW=$((N_NEW + 1))
  NEW_KEYS="${NEW_KEYS}${key}"$'\n'
  # `corr=1` ⇒ NGHI ta đã cộng một bản ĐÍNH CHÍNH như tranche thật ⇒ **chưa quy được cho vendor**.
  # Bản trước chỉ ghi tiêu đề sự kiện vào `notes` (stdout/log) trong khi CÁO BUỘC đi lên Discord, nên
  # ca DIV 500 + "Điều chỉnh … 800" gửi nguyên văn "vendor THIẾU hệ số" + dòng việc cho Winston mà
  # bằng chứng phản bác nằm ở kênh khác (arch-review vòng 2, F4 — §29: caveat phải đi CÙNG lời cáo
  # buộc). Những dòng này KHÔNG bật SEEN_VENDOR.
  if [ "${corr:-0}" = "1" ]; then
    N_CORR=$((N_CORR + 1))
    cause="⚠️ **NGHI BẢN ĐÍNH CHÍNH, CHƯA QUY ĐƯỢC CHO VENDOR** — ex-date này có >1 dòng cùng \`event_code\` trong \`corporate_action\`; nếu một dòng là bản đính chính thì hệ số tự suy của TA sai, không phải vendor (r_obs ${r_obs} vs r_pred ${r_pred}). Đọc chứng từ tiêu đề trong log trước khi giao việc cho ai"
  else
  case "$dir" in
    vendor_missing) SEEN_VENDOR=1
      cause="vendor \`tav2_bq.ticker.Close\` THIẾU hệ số (r_obs ${r_obs} < r_pred ${r_pred})" ;;
    our_table_missing) SEEN_OURS=1
      cause="\`corporate_action\` của TA nghi thiếu một mắt xích (r_obs ${r_obs} > r_pred ${r_pred})" ;;
    *) cause="KHÔNG xác định được chiều lệch (dir=${dir}) — kiểm thủ công, KHÔNG suy đoán bên nào sai" ;;
  esac
  fi
  line="
• **${tk}** (ex ${ex}): lệch $(_pct "$dev") liên tục **${run} phiên** ${d0}..${d1} — ${cause}"
  # `unknown` KHÔNG được gộp vào `none`. Bản trước gộp, và arch-review 2026-09-27 đo thật: một mã
  # ĐANG NẮM (VPB, lệch −20,66%) in ra dưới tiêu đề "Mã không nắm (chỉ ảnh hưởng nghiên cứu/
  # backtest)" khi `held_map()` fail-open — một KHẲNG ĐỊNH SAI về mức phơi nhiễm tiền thật (§29
  # dạng 2), và còn bị trần `MAX_OTHER_LINES` cắt mất.
  #
  # `skipped` (người chạy dùng `--no-holdings`) KHÁC `unknown` (tra mà không được) và KHÁC tên tài
  # khoản — nếu để nó rơi vào nhánh `*)` thì Discord in ra "**ĐANG NẮM LIVE: skipped**", một khẳng
  # định sai trắng trợn về vị thế tiền thật. Nó không khẳng định gì về vị thế, nên xếp cùng nhóm
  # "không nêu ưu tiên" và nói rõ là CHƯA TRA.
  case "$held" in
    unknown)
      N_UNKNOWN=$((N_UNKNOWN + 1))
      DETAIL_UNKNOWN="${DETAIL_UNKNOWN}${line} — **KHÔNG TRA ĐƯỢC vị thế, phải coi như CÓ THỂ đang nắm**"
      ;;
    skipped)
      N_SKIPPED=$((N_SKIPPED + 1))
      if [ "$N_SKIPPED" -le "$MAX_OTHER_LINES" ]; then
        DETAIL_SKIPPED="${DETAIL_SKIPPED}${line} — _vị thế CHƯA TRA (\`--no-holdings\`)_"
      fi
      ;;
    none)
      N_OTHER=$((N_OTHER + 1))
      if [ "$N_OTHER" -le "$MAX_OTHER_LINES" ]; then
        DETAIL_OTHER="${DETAIL_OTHER}${line}"
      fi
      ;;
    *)
      N_HELD=$((N_HELD + 1))
      DETAIL_HELD="${DETAIL_HELD}${line} — **ĐANG NẮM LIVE: ${held}**"
      ;;
  esac
done <<< "$DRIFTS"

# UNCOMPUTABLE / NODATA: chỉ nêu tên trên Discord khi mã có thể đang NẮM (kể cả `unknown` —
# fail-open về phía CẢNH BÁO). Phần còn lại chỉ đếm.
#
# ⚠️ PHẢI de-dup y như DRIFT. Bản trước KHÔNG de-dup nhánh này và `N_UNCOMP_HELD > 0` luôn phá
# de-dup ⇒ arch-review 2026-09-27 chạy 3 lượt cùng input: gửi Discord CẢ BA lượt. Không phải giả
# định: LAYER1.md ghi 5 mã đang nắm đã ở trạng thái này (MBB quyền mua, CTG/VCB/VND/VNM ffill) với
# cửa sổ sự kiện 120 ngày ⇒ cùng một tin mỗi ngày, đúng cái mà header này lập luận chống lại.
# Khoá gồm `code` vì đổi mã lý do là đổi việc phải làm.
DETAIL_UNCOMP=""
N_UNCOMP_HELD=0
N_UNCOMP_OTHER=0
while IFS='|' read -r _tag tk ex code held _rest; do
  [ -z "${tk:-}" ] && continue
  # `skipped` = chưa tra vị thế ⇒ không được nêu như "mã có thể đang nắm"; đếm như `none`.
  if [ "$held" = "none" ] || [ "$held" = "skipped" ]; then
    N_UNCOMP_OTHER=$((N_UNCOMP_OTHER + 1))
    continue
  fi
  key="${tk}|${ex}|${code}"
  _is_fresh "$key" && continue
  N_UNCOMP_HELD=$((N_UNCOMP_HELD + 1))
  NEW_KEYS="${NEW_KEYS}${key}"$'\n'
  hl="$held"
  if [ "$held" = "unknown" ]; then
    hl="KHÔNG TRA ĐƯỢC vị thế"
  fi
  DETAIL_UNCOMP="${DETAIL_UNCOMP}
• **${tk}** (ex ${ex}, ${hl}): \`${code}\` — KHÔNG tính được hệ số, **không kết luận là khớp**"
done <<< "$UNCOMPS"

N_NODATA_HELD=0
N_NODATA_OTHER=0
while IFS='|' read -r _tag tk held _rest; do
  [ -z "${tk:-}" ] && continue
  if [ "$held" = "none" ] || [ "$held" = "skipped" ]; then
    N_NODATA_OTHER=$((N_NODATA_OTHER + 1))
    continue
  fi
  key="${tk}|nodata"
  _is_fresh "$key" && continue
  N_NODATA_HELD=$((N_NODATA_HELD + 1))
  NEW_KEYS="${NEW_KEYS}${key}"$'\n'
  hl="$held"
  if [ "$held" = "unknown" ]; then
    hl="KHÔNG TRA ĐƯỢC vị thế"
  fi
  DETAIL_UNCOMP="${DETAIL_UNCOMP}
• **${tk}** (${hl}): KHÔNG có dòng giá nào trong cửa sổ — **không kết luận được gì cho mã này**"
done <<< "$NODATAS"

# BUS trước (kênh PHỤ, luôn ghi kể cả khi Discord im vì de-dup) — đây là dấu vết audit đầy đủ:
# mọi DRIFT và mọi UNCOMPUTABLE của lượt quét, không qua bộ lọc de-dup/held nào.
PAYLOAD="$(ASOF="$ASOF" N_SCANNED="$N_SCANNED" N_DRIFT="$N_DRIFT" N_UNCOMP="$N_UNCOMP" \
  N_AGREE="$N_AGREE" N_NODATA="$N_NODATA" N_NEW="$N_NEW" N_HELD="$N_HELD" \
  N_UNKNOWN="$N_UNKNOWN" FEED_STATUS="$FEED_STATUS" FEED_LINE="$FEED" \
  DRIFTS="$DRIFTS" UNCOMPS="$UNCOMPS" NODATAS="$NODATAS" python3 -c "
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
    'drift_holdings_unknown': os.environ['N_UNKNOWN'],
    'corp_action_feed': os.environ['FEED_STATUS'] or 'not_reported',
    'corp_action_feed_marker': os.environ['FEED_LINE'],
    'published_any_number': False,
    'drift_markers': lines('DRIFTS'), 'uncomputable_markers': lines('UNCOMPS'),
    'nodata_markers': lines('NODATAS'),
}, ensure_ascii=False))
")"

# `status`, KHÔNG phải `finding`: lượt quét chạy MỖI NGÀY và consolidator đưa `finding` lên khối
# "MỚI NHẤT" của `kb/context_*_mini.md` (file auto-inject mọi phiên) ⇒ một dòng rác mỗi ngày cho cả
# fleet. `finding` dành cho tri thức BỀN; đây là nhật ký vận hành. (Tiền lệ: `vendor_mismatch_alert.sh`
# dùng `Mike error` cho cùng loại việc.)
if [ "$DRY_RUN" -eq 0 ]; then
  if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Taylor status "adjfactor-drift-scan-${ASOF}" "$PAYLOAD" 2>&1 >/dev/null)"; then
    echo "adjfactor_drift_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
  fi
fi

# Bỏ qua vì lượt khác đang giữ lock — thoát Ở ĐÂY, tức SAU khi bus đã ghi. Thoát trước bước ghi bus
# (bản vòng 3) làm mất CẢ HAI kênh cho một lệch thật, trong khi lý do bỏ qua chỉ là "để không gửi
# trùng" — dấu vết audit không liên quan gì tới việc đó (arch-review vòng 3, R3-4).
if [ "$LOCK_SKIP" -eq 1 ]; then
  echo "adjfactor_drift_alert: mot luot khac dang giu $STATE.lock (cho 60s khong duoc) -> da ghi BUS," \
       "KHONG gui Discord de khong trung. rc=11." >&2
  exit 11
fi

FEED_BAD=0
if [ "$FEED_STATUS" != "FRESH" ]; then
  FEED_BAD=1
fi

# `EMPTY_UNIVERSE` phải nằm trong điều kiện này: nó không sinh khoá de-dup nào (N_NEW=0) nên nếu
# thiếu, ca universe rỗng ghi bus rồi thoát mà KHÔNG gửi Discord — tức vẫn im lặng ở kênh người đọc.
if [ "$N_NEW" -eq 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ] && [ "$N_NODATA_HELD" -eq 0 ] \
   && [ "$FEED_BAD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ]; then
  echo "adjfactor_drift_alert: ${N_DRIFT} lech nhung tat ca da canh bao trong ${RE_ALERT_DAYS} ngay qua," \
       "khong co uncomputable/nodata nao co the dang nam, feed nguon TUOI -> chi ghi bus," \
       "khong gui Discord (de-dup)." >&2
  exit 10
fi

SECTIONS=""
if [ "$EMPTY_UNIVERSE" -eq 1 ]; then
  SECTIONS="${SECTIONS}
__**UNIVERSE RỖNG — 0 mã được quét, đây là ĐIỂM MÙ:**__
• Không một mã nào có ex-date điều chỉnh giá trong cohort. Ở VN điều đó bất khả về cấu trúc (đo thật: 95 mã cho cửa sổ 18 ngày) ⇒ **cohort hoặc feed đang hỏng, KHÔNG phải \"tuần này không có sự kiện\"**.
"
fi
if [ "$FEED_BAD" -eq 1 ]; then
  SECTIONS="${SECTIONS}
__**FEED NGUỒN \`tav2_bq.corporate_action\` KHÔNG TƯƠI — đọc mục này TRƯỚC:**__
• trạng thái \`${FEED_STATUS}\`: ${FEED_REASON:-không có lý do kèm theo}
• nạp gần nhất (ICT) \`${FEED_ING:-?}\` · public_date \`${FEED_PUB:-?}\` · ${FEED_ROWS:-?} dòng · cũ ${FEED_AGE:-?} ngày
• ⚠️ **Mọi kết luận \"khớp\" bên dưới KHÔNG đáng tin khi feed đứng im** — hệ số tự suy lấy từ chính bảng này.
"
fi
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
# Khối `unknown` đặt NGAY SAU khối nắm-LIVE và KHÔNG bao giờ bị cắt: nó có thể là tiền thật.
[ -n "$DETAIL_SKIPPED" ] && SECTIONS="${SECTIONS}
__**Vị thế CHƯA TRA (\`--no-holdings\`) — không kết luận nắm hay không:**__${DETAIL_SKIPPED}
"
[ -n "$DETAIL_UNKNOWN" ] && SECTIONS="${SECTIONS}
__**KHÔNG TRA ĐƯỢC VỊ THẾ (phải coi như có thể đang nắm):**__${DETAIL_UNKNOWN}
"
[ -n "$DETAIL_UNCOMP" ] && SECTIONS="${SECTIONS}
__**KHÔNG KẾT LUẬN ĐƯỢC (fail-closed, mã có thể đang nắm):**__${DETAIL_UNCOMP}
"

TODO=""
[ "$SEEN_VENDOR" = "1" ] && TODO="${TODO}
- **Vendor thiếu hệ số điều chỉnh:** Winston (data-ops) yêu cầu backfill \`tav2_bq.ticker\`/\`ticker_prune\` cho các (mã, ex-date) trên. Chữ ký đã biết: hệ số chỉ chạm **4 phiên cum cuối** (\`SETTLE_RUN=4\`) rồi dừng — nhánh fallback hẹp của ETL chạy, còn bản rewrite toàn cửa sổ (gated \`need_cafef\`) KHÔNG chạy."
[ "$SEEN_OURS" = "1" ] && TODO="${TODO}
- **Nghi \`corporate_action\` của TA thiếu mắt xích:** Taylor đối chiếu sự kiện thật của mã đó (chiều lệch NGƯỢC lại: vendor có hệ số mà ta không suy ra được). Đây là GỢI Ý ĐIỀU HƯỚNG theo dấu của lệch, KHÔNG phải bằng chứng."
[ "$FEED_BAD" -eq 1 ] && TODO="${TODO}
- **Feed \`corporate_action\` không tươi (\`${FEED_STATUS}\`):** Winston (data-ops) kiểm writer NGOÀI repo của bảng TRAP này (\`kb/data_registry/price-volume/corporate_action_bq.md\`). **Cho tới khi feed tươi lại, coi lượt quét này là ĐIỂM MÙ, không phải \"không có lệch\"** — đừng đóng cảnh báo bằng lý do \"đã quét, không thấy gì\"."
[ "$N_UNKNOWN" -gt 0 ] && TODO="${TODO}
- **Không tra được vị thế LIVE:** \`dividend_adjusted_return.broker_qty()\` lỗi ⇒ nhãn nắm/không nắm của lượt này KHÔNG dùng được. Kiểm \`data/execution_logs/dnse_raw_*.jsonl\` rồi chạy lại; trong lúc chờ, coi MỌI mã ở khối trên như có thể đang nắm."
[ "$EMPTY_UNIVERSE" -eq 1 ] && TODO="${TODO}
- **Universe rỗng:** Winston (data-ops) kiểm \`tav2_bq.corporate_action\` còn nhận dòng mới không, và kiểm câu SQL cohort của detector. **Đừng đóng bằng \"đã quét, không thấy gì\"** — lượt này KHÔNG quét được mã nào."
[ "$N_CORR" -gt 0 ] && TODO="${TODO}
- **${N_CORR} mã NGHI bản đính chính (\`corr=1\`):** KHÔNG giao cho Winston và KHÔNG coi là vendor sai. \`corporate_action\` giữ cả tranche thật (phải CỘNG) lẫn bản đính chính của cùng tranche (KHÔNG được cộng), phân biệt bằng \`event_title_vi\` — chỉ đọc hiểu được bằng mắt. Mở log cron, đọc dòng chứng từ \`[>1 dòng cùng event_code ...]\` của mã đó trước khi kết luận."
[ "$N_UNCOMP_HELD" -gt 0 ] && TODO="${TODO}
- **Mã nắm LIVE không tính được hệ số:** \`rights_issue_no_subscription_price\` = giá phát hành không có trong \`corporate_action\` (cột \`ref_price\` NULL toàn bộ từ 2025-01-01) ⇒ Layer 1 KHÔNG kết luận được gì cho mã đó, cổng §21 vẫn là lớp bảo vệ duy nhất. \`price_ffill_suspect\` = \`Price\` phiên cum cuối nằm ngoài band ⇒ Winston kiểm dòng giá đó."

MSG="⚠️ **LỆCH HỆ SỐ ĐIỀU CHỈNH CORP-ACTION (Layer 1 — CHỈ PHÁT HIỆN)** — asof \`${ASOF}\`
Hệ số tự suy từ \`tav2_bq.corporate_action\` không khớp hệ số ẩn trong \`tav2_bq.ticker\` (\`Price\`/\`Close\`), lệch >0,3% kéo dài ≥3 phiên liên tiếp:
${SECTIONS}
**Việc cần làm:**${TODO}

_Quét ${N_SCANNED} mã: ${N_DRIFT} lệch · ${N_UNCOMP} không tính được · ${N_AGREE} khớp · ${N_NODATA} không có dữ liệu · feed nguồn \`${FEED_STATUS:-không báo}\`. ${N_UNCOMP_OTHER} uncomputable + ${N_NODATA_OTHER} nodata của mã KHÔNG nắm chỉ ghi bus, không nêu ở đây._
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

STATE="$STATE" TODAY="$TODAY" NEW_KEYS="$NEW_KEYS" PRUNE_DAYS="$PRUNE_DAYS" python3 -c "
import datetime, json, os, sys, tempfile
path = os.environ['STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('adjfactor_drift_alert: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e),
          file=sys.stderr)
    state = {}
# Don khoa qua cu: mot khoa cu hon PRUNE_DAYS khong con anh huong quyet dinh nao (de-dup chi xet
# trong RE_ALERT_DAYS), nen giu no chi lam file phinh vo han. vendor_mismatch_alert.sh chap nhan
# duoc vi o do khoa chi sinh khi co lech THAT (do 0/62 su kien), con o day moi (ma,ex) cua moi
# cohort deu sinh khoa (~1,2k/nam) va khong ai lam chu viec don.
# (Khong dung backtick trong khoi nay: no nam trong chuoi NHAY KEP cua python3 -c => command
#  substitution that su, khong phai trich dan van xuoi — §15.)
today = datetime.date.fromisoformat(os.environ['TODAY'])
prune = int(os.environ['PRUNE_DAYS'])
for k in list(state):
    try:
        if (today - datetime.date.fromisoformat(str(state[k]))).days > prune:
            del state[k]
    except ValueError:
        del state[k]          # giá trị không đọc được: bỏ, lần sau coi như chưa cảnh báo
for k in os.environ['NEW_KEYS'].splitlines():
    if k.strip():
        state[k.strip()] = os.environ['TODAY']
# Ghi state THẤT BẠI (thư mục read-only, hết đĩa) KHÔNG được bung traceback trần: Discord ĐÃ gửi
# xong ở bước trước, nên hệ quả thật là 'lượt sau sẽ gửi lại' — phải nói ra điều đó kèm LỖI THẬT
# (§29), không phải để người đọc tự dịch một stack trace (arch-review vòng 3).
try:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.adjfactor_drift_alerted.', suffix='.tmp')
except OSError as e:
    sys.stderr.write('adjfactor_drift_alert: KHONG ghi duoc state de-dup %s — Discord DA gui roi, nen '
                     'luot cron sau se GUI LAI dung cac khoa nay (khong mat canh bao, co the trung). '
                     'Loi that: %s: %s\n' % (path, type(e).__name__, e))
    raise SystemExit(0)
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
