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
# `VENDOR_LOOKUP_FAILED|<acct>|<mã>|<ex>|<broker>|<had_broker_cash>|<published>` (7 trường — arch-
# review 2026-09-24 vòng 4 R1(e), mở rộng vòng 5 R1-A/R1-B): BQ lỗi hạ tầng, KHÔNG tra được vendor
# — KHÁC "hai nguồn bất đồng số" (không có vendor_ps để so). TAG RIÊNG cố ý, không tái dùng
# VENDOR_MISMATCH_ALERT.
#
# Exit: 0 = KHÔNG có lệch nguồn/lookup_failed nào · 10 = CÓ ít nhất một trong hai · 2 = sai đối số.
#   ⚠️ 10 nói về SỰ TỒN TẠI của lệch nguồn, KHÔNG hứa "đã gửi được cảnh báo" — hai caller
#   (`check_report_cadence.sh:91`, `eod_trading_report.sh:72`) chỉ dùng nó để quy ĐÚNG nguyên
#   nhân/người xử lý (§29), nên nó phải đúng cả khi Discord chết. Gửi hỏng thì in LỖI THẬT ra
#   stderr và KHÔNG ghi de-dup cho file đó (gọi LẠI đúng script/file/ngày này sẽ thử gửi lại).
#
#   ⚠️ ĐÍNH CHÍNH (arch-review vòng 3b, R1 — bản trước khẳng định "⇒ lượt sau thử lại" quá tay):
#   "gọi lại thì thử lại" chỉ đúng Ở CẤP SCRIPT NÀY, không có nghĩa caller thật sự SẼ gọi lại cho
#   đúng file đó. `check_report_cadence.sh:76-81` chỉ chạy lại khối gate+vendor-alert cho 1 file
#   khi `state/report_emailed.json` (EMAILED_STATE — dedup của TOÀN BỘ report, KHÁC de-dup cục bộ
#   ở trên) CHƯA có key file đó. Key này được ghi ngay khi kênh EMAIL của `report_delivery_gate.py`
#   thành công (dòng 266-270); và một khi record đã COMPLETE (đủ artifact_validated + discord +
#   email), `complete(record, sha)` return SỚM ở dòng 238-239 — TRƯỚC bước validate lại — nên với
#   1 báo cáo đã giao trót lọt, sweep KHÔNG BAO GIỜ quay lại đúng file đó nữa, bất kể Discord của
#   vendor_mismatch_alert.sh hôm đó gửi được hay không.
#   Đường phát lại THẬT của SỰ KIỆN lệch nguồn là báo cáo NGÀY KẾ TIẾP — tên file KHÁC nên chạy
#   lại toàn bộ pipeline từ đầu, và `report_return_gate.py` (LOOKBACK_DAYS=120 dòng 60, chỉ giữ
#   sự kiện của mã còn trong vị thế — dòng 186-192) quét lại đúng cặp (mã, ex-date) đó nếu vẫn còn
#   trong cửa sổ VÀ vị thế còn nắm. Hệ quả:
#     (a) MẤT cảnh báo thật chỉ xảy ra khi Discord chết ĐÚNG hôm đó **VÀ** vị thế bị bán hết
#         trước báo cáo kế tiếp (dar._qty_at ⇒ 0 ⇒ event không còn được quét ra nữa, nên không
#         còn "ngày kế tiếp" nào tái tạo lại marker để thử gửi).
#     (b) event `Mike error vendor-mismatch-...` (dòng ~99) KHÔNG phải backstop hành động được:
#         `bin/ops_health_check.sh` chỉ xét `event_type == "question"`, bỏ qua `error` — đo thật
#         2026-09-24: `bus/inbox/Mike.jsonl` có `error/selfcheck-weekly-new-red` lặp lại 5 lần từ
#         09-14 đến 09-23 không ai đóng, cùng lớp "error không có ai xử lý".
#   Không ghi state cục bộ khi Discord hỏng vẫn ĐÚNG phải làm — sổ sách không được nói "đã cảnh
#   báo" khi chưa gửi được gì (§5/§29) — chỉ là nó không mua được "lượt sau thử lại ĐÚNG file này
#   qua caller thật" như bản cũ ngụ ý; nó mua được tính trung thực của bookkeeping + khả năng thử
#   lại NẾU có ai gọi lại chính script này (thủ công/kênh khác).
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

# Định dạng số nghìn cho câu Discord — khớp quy ước `{broker_ps:,.0f}` mà report_return_gate.py
# dùng cho chính con số này trong log cron (arch-review vòng 5, mục (d)): trước bản vá này Discord
# in "1200đ/cp" trong khi log in "1,000đ/cp" cho CÙNG một giá trị — không sai, chỉ khác định dạng,
# nhưng khác nhau không lý do giữa hai nơi cùng nói về một con số. Trường máy đọc (payload
# VENDOR_MISMATCH_ALERT/VENDOR_LOOKUP_FAILED) giữ nguyên số THÔ, không qua hàm này.
# Thuần bash (không dùng `printf "%'d"` của awk/C — grouping đó phụ thuộc locale biên dịch, đo
# thật trên host này: LC_ALL=en_US.UTF-8 vẫn in "1200" không có dấu phẩy, im lặng KHÔNG báo lỗi).
_fmt_vnd() {
  local n="${1%%.*}" neg="" out=""
  case "$n" in -*) neg="-"; n="${n#-}" ;; esac
  while [ "${#n}" -gt 3 ]; do
    out=",${n: -3}${out}"
    n="${n%???}"
  done
  printf '%s%s%s' "$neg" "$n" "$out"
}

GATE_OUT="$(cat)"
MARKERS="$(printf '%s\n' "$GATE_OUT" | grep -E '^VENDOR_MISMATCH_ALERT\|' || true)"
# VENDOR_LOOKUP_FAILED (arch-review 2026-09-24 vòng 4, R1(e); mở rộng vòng 5 R1-A/R1-B): TAG
# RIÊNG, 7 trường (tag|acct|mã|ex|broker|had_broker_cash|published — KHÔNG có vendor_ps, BQ lỗi
# hạ tầng nên chưa tra được số thứ hai). `had_broker_cash` phân biệt "broker ĐÃ giải số này (tiền
# thật)" khỏi "đây chỉ là ước lượng tỉ số, CHƯA từng là tiền broker" — rẽ câu Discord ĐÚNG bằng
# chứng thay vì khẳng định "broker đã giải" cho một con số ước lượng (§29). Trường cuối là
# "published" THÔ — KHÔNG PHẢI "blocked" tính sẵn: script tự tính BLOCKED = had_broker_cash AND
# published bên dưới, cùng công thức mà report_return_gate.py dùng để dựng `vendor_fails`, vì
# R1-B chỉ chặn khi lookup_failed thật sự làm MẤT một số đã từng công bố.
# Trước bản vá R1(e) này script chỉ grep VENDOR_MISMATCH_ALERT ⇒ một báo cáo CHẶN THUẦN vì
# lookup_failed (không có mismatch nào) làm MARKERS rỗng ⇒ exit 0 câm lặng, đúng lúc report bị
# CHẶN thật — user chỉ thấy "Delivery INCOMPLETE" chung chung, sai nguyên nhân/người (§29).
LOOKUP_MARKERS="$(printf '%s\n' "$GATE_OUT" | grep -E '^VENDOR_LOOKUP_FAILED\|' || true)"
[ -z "$MARKERS" ] && [ -z "$LOOKUP_MARKERS" ] && exit 0

# Mã lý do đi ở dòng TAG RIÊNG (`VENDOR_MISMATCH_REASON|<acct>|<mã>|<ex>|<reason>|<vendor_stock>`,
# `report_return_gate.py` — hợp đồng 7 trường của dòng ALERT giữ NGUYÊN BYTE, không đọc reason từ
# đó). Ghép bằng khoá acct|mã|ex (arch-review D1b, R1): trước bản vá này script phát MỘT câu cố
# định "hai số KHÁC nhau" / "đối soát cho khớp lại" cho MỌI mã lý do — SAI cho stock_leg_ignored
# (vendor KHÔNG khai chân tiền nào, không có "hai số" nào để so; việc cần làm là tìm chân cổ
# phiếu bị bỏ sót, không phải đối soát tiền) — đúng lớp lỗi §29.
declare -A REASON_MAP
REASON_LINES="$(printf '%s\n' "$GATE_OUT" | grep -E '^VENDOR_MISMATCH_REASON\|' || true)"
while IFS='|' read -r _rtag racct rtk rex rreason _rstock; do
  [ -z "${rtk:-}" ] && continue
  REASON_MAP["${racct}|${rtk}|${rex}"]="$rreason"
done <<< "$REASON_LINES"

DETAIL=""
BLOCKED=0
SEEN_CASH=0
SEEN_STOCK=0
SEEN_UNKNOWN=0
SEEN_LOOKUP=0
while IFS='|' read -r _tag acct tk ex broker vendor published; do
  [ -z "${tk:-}" ] && continue
  reason="${REASON_MAP["${acct}|${tk}|${ex}"]:-}"
  case "$reason" in
    stock_leg_ignored)
      SEEN_STOCK=1
      DETAIL="${DETAIL}
• **${tk}** (${acct}, ex ${ex}): vendor khai THUẦN CỔ PHIẾU (không có chân tiền), nhưng broker giải ra $(_fmt_vnd "$broker")đ/cp TIỀN MẶT mà chưa biết chân cổ phiếu — nghi giá rơi chia tách bị đọc thành cổ tức"
      ;;
    cash_mismatch)
      SEEN_CASH=1
      DETAIL="${DETAIL}
• **${tk}** (${acct}, ex ${ex}): broker giải $(_fmt_vnd "$broker")đ/cp vs \`corporate_action\` $(_fmt_vnd "$vendor")đ/cp — hai nguồn bất đồng số cổ tức"
      ;;
    *)
      SEEN_UNKNOWN=1
      DETAIL="${DETAIL}
• **${tk}** (${acct}, ex ${ex}): LỆCH NGUỒN cổ tức nhưng KHÔNG xác định được mã lý do (broker $(_fmt_vnd "$broker")đ/cp vs vendor $(_fmt_vnd "$vendor")đ/cp) — kiểm thủ công, KHÔNG suy đoán nguyên nhân"
      ;;
  esac
  if [ "${published:-0}" = "1" ]; then
    BLOCKED=1
    DETAIL="${DETAIL} — mã này ĐANG công bố tỉ suất ⇒ báo cáo bị CHẶN"
  else
    DETAIL="${DETAIL} — báo cáo vẫn gửi (không công bố tỉ suất mã này), cổ tức đã bị bỏ khỏi kỳ vọng"
  fi
done <<< "$MARKERS"

# VENDOR_LOOKUP_FAILED — vòng RIÊNG, KHÔNG gộp vào vòng trên: không có REASON_MAP (nhãn này
# KHÔNG có "mã lý do", nó LÀ nguyên nhân) và không có vendor_ps (7 trường, KHÁC 7 trường của ALERT
# — vị trí trường khác nhau, xem header).
while IFS='|' read -r _tag acct tk ex broker hadcash published; do
  [ -z "${tk:-}" ] && continue
  SEEN_LOOKUP=1
  # R1-A: "broker đã giải" chỉ ĐÚNG khi sự kiện TỪNG là CASH_CONFIRMED (had_broker_cash=1) —
  # ngược lại `broker` chỉ là ƯỚC LƯỢNG tỉ số từ giá rơi, CHƯA từng là tiền broker thật.
  if [ "${hadcash:-0}" = "1" ]; then
    moneytxt="broker đã giải $(_fmt_vnd "$broker")đ/cp nhưng chưa đối soát chéo được"
  else
    moneytxt="broker CHƯA giải được số nào (ước lượng từ giá rơi $(_fmt_vnd "$broker")đ/cp, KHÔNG phải tiền broker thật)"
  fi
  DETAIL="${DETAIL}
• **${tk}** (${acct}, ex ${ex}): KHÔNG TRA ĐƯỢC nguồn vendor \`corporate_action\` (lỗi hạ tầng BQ, KHÔNG phải vendor xác nhận 0 sự kiện) — ${moneytxt}"
  # R1-B: CHẶN chỉ khi lookup_failed thật sự làm mất một số đã từng công bố — cùng công thức
  # (hadcash AND published) mà report_return_gate.py dùng để dựng `vendor_fails`. `published`
  # ở đây LÀ trạng thái công bố thô (không gán sẵn), nên khi hadcash=0 mà mã VẪN đang công bố,
  # câu đúng là "vẫn gửi" (không mất số) chứ không phải "không công bố tỉ suất mã này".
  if [ "${hadcash:-0}" = "1" ] && [ "${published:-0}" = "1" ]; then
    BLOCKED=1
    DETAIL="${DETAIL} — mã này ĐANG công bố tỉ suất ⇒ báo cáo bị CHẶN"
  elif [ "${hadcash:-0}" = "1" ]; then
    DETAIL="${DETAIL} — báo cáo vẫn gửi (không công bố tỉ suất mã này), cổ tức đã bị bỏ khỏi kỳ vọng"
  else
    DETAIL="${DETAIL} — không mất số đã công bố (chưa từng là CASH_CONFIRMED), báo cáo vẫn gửi bình thường"
  fi
done <<< "$LOOKUP_MARKERS"

TODO=""
[ "$SEEN_CASH" = "1" ] && TODO="${TODO}
- **Bất đồng số cổ tức:** Winston (data-ops) đối soát \`tav2_bq.corporate_action\` với sổ broker cho (mã, ex-date) trên. Chỉ khi hai nguồn khớp lại thì tỉ suất mã đó mới được công bố (§21)."
[ "$SEEN_STOCK" = "1" ] && TODO="${TODO}
- **Nghi giá rơi chia tách bị đọc thành cổ tức:** Winston xác nhận lại sự kiện CỔ PHIẾU (ISS) với vendor — vì sao chân cổ phiếu chưa được credit vào vị thế. KHÔNG PHẢI đối soát số tiền (vendor không khai chân tiền nào cho sự kiện này)."
[ "$SEEN_UNKNOWN" = "1" ] && TODO="${TODO}
- **Không xác định được mã lý do:** kiểm thủ công (mã lý do bị thiếu/rỗng ở nguồn) — KHÔNG suy đoán nguyên nhân."
[ "$SEEN_LOOKUP" = "1" ] && TODO="${TODO}
- **BQ lỗi hạ tầng (KHÔNG phải bất đồng số liệu):** chạy lại \`report_return_gate.py\` cho báo cáo này SAU KHI BQ khoẻ (kiểm tra bằng \`bin/bq_freshness_check.sh\`); KHÔNG cần đối soát số hay xác nhận sự kiện trừ khi lỗi lặp lại nhiều lượt liên tiếp."

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

# Tiêu đề/câu mở phân biệt ca THUẦN lookup_failed (BQ lỗi hạ tầng — KHÔNG PHẢI hai nguồn bất
# đồng số) khỏi ca có mismatch thật — dùng chung một câu mở cho cả hai sẽ nói "không khớp" cho
# một sự kiện mà thật ra CHƯA đối soát được (§29, arch-review 2026-09-24 vòng 4, R1(e)).
if [ "$SEEN_CASH" = "0" ] && [ "$SEEN_STOCK" = "0" ] && [ "$SEEN_UNKNOWN" = "0" ] && [ "$SEEN_LOOKUP" = "1" ]; then
  MSG="⚠️ **VENDOR LOOKUP THẤT BẠI (lỗi hạ tầng BQ) — cần Winston (data-ops)** — \`${FNAME}\`
Cổng KHÔNG tra được nguồn vendor \`tav2_bq.corporate_action\` cho (các) sự kiện cổ tức dưới đây (lỗi hạ tầng, KHÔNG phải hai nguồn bất đồng số):${DETAIL}

**Việc cần làm:**${TODO}

Đây KHÔNG phải lỗi soạn báo cáo — không nới dung sai cổng để gỡ chặn, thử lại khi BQ khoẻ."
else
  MSG="⚠️ **LỆCH NGUỒN CỔ TỨC — cần Winston (data-ops)** — \`${FNAME}\`
Cổng phát hiện sự kiện cổ tức mà tiền broker thật và bảng vendor \`tav2_bq.corporate_action\` không khớp:${DETAIL}

**Việc cần làm:**${TODO}

Đây KHÔNG phải lỗi soạn báo cáo — không nới dung sai cổng để gỡ chặn, xử lý đúng nguyên nhân ở trên trước."
fi

PAYLOAD="{\"artifact\":\"${FNAME}\",\"owner\":\"Winston\",\"blocked_report\":${BLOCKED},\"markers\":$(printf '%s\n%s\n' "$MARKERS" "$LOOKUP_MARKERS" | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')}"

# BUS = kênh PHỤ. Hỏng thì nêu lỗi thật rồi ĐI TIẾP — không được vì bus mà chặn đường tới user.
if ! BUS_ERR="$("$ROOT/bin/append_event.sh" Mike error "vendor-mismatch-${FNAME}" "$PAYLOAD" 2>&1 >/dev/null)"; then
  echo "vendor_mismatch_alert: append_event.sh THAT BAI (bus la kenh phu, van gui Discord). Loi that: ${BUS_ERR}" >&2
fi

# DISCORD = kênh CHÍNH và là ĐIỀU KIỆN để ghi de-dup CỤC BỘ (vendor_mismatch_alerted.json, KHÁC
# tầng EMAILED_STATE của check_report_cadence.sh — xem ĐÍNH CHÍNH ở header). Trước đây
# `2>/dev/null || true` + ghi state vô điều kiện: ccdb chết/topic sai ⇒ lỗi bị NUỐT (§29) và state
# vẫn ghi "đã cảnh báo hôm nay" dù KHÔNG có gì được gửi — sổ sách nói dối, và nếu có lượt gọi lại
# THẬT cho đúng file/ngày đó thì lượt đó cũng bị khoá oan bởi chính de-dup cục bộ này.
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
