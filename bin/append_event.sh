#!/usr/bin/env bash
# append_event.sh <agent_id> <event_type> <topic> <payload_json_or_string> [trace_id]
# Appends one JSONL event to bus/inbox/<agent_id>.jsonl (append-only, one file per child).
# event_id is a real UUID; flock guards this child's own file only (no cross-child contention).
#
# trace_id (optional 5th arg): correlates every event produced during ONE dispatch chain
# (caller -> agent -> auto-callback) so a job's full story can be pulled with one grep
# instead of matching on prompt_summary text. Falls back to $JOB_ID if set (dispatch.sh
# exports it into the headless agent's environment) — an agent calling this script with only
# 4 args still gets traced automatically as long as it's running inside a dispatch job.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUS="$ROOT/bus"
PY="$ROOT/bin/mike_json.py"

_ORIG_ARGV=("$@")   # giữ NGUYÊN VĂN arg gốc cho hàng đợi cách ly ở die() bên dưới
id="${1:?usage: append_event.sh <agent_id> <event_type> <topic> <payload> [trace_id]}"
etype="${2:?event_type required (finding|status|question|answer|decision|error)}"
topic="${3:?topic required}"
payload="${4:?payload required (json object/array, or plain string)}"
trace_id="${5:-${JOB_ID:-}}"

# --- Chống WORD-SPLIT im lặng (Wags coord-2026-08-13) ---------------------------------
# Sự cố thật: 13 event / 6 agent trong 1 tháng bị shell cắt payload giữa chừng (payload chứa
# dấu nháy đơn lẻ ⇒ chuỗi '...' của caller đóng sớm). Hậu quả CŨ: phần payload sau chỗ cắt
# thành arg 5 → ghi thẳng vào trace_id ("thêm", "nguoi", "capacity"...), phần còn lại bị vứt
# LẶNG LẼ, và mike_json.py fallback JSON-hỏng→chuỗi nên event vẫn "thành công". Câu hỏi
# question của Mike 2026-08-12 mất nguyên phần đuôi kiểu này. Fail LOUD thay vì ghi rác:
# mất 1 lần gọi (agent thấy lỗi, quote lại rồi gọi lại) rẻ hơn 1 event hỏng vĩnh viễn.
# CÁCH LY, KHÔNG CHỈ KÊU (arch-review coord-2026-08-13 required_change #4): 28/42 call site
# gọi kèm `2>/dev/null || true` (eod_trading_report.sh, ops_health_check.sh, dispatch.sh,
# refresh_fa_ratings.sh…), nên với NHÓM ĐÓ thông điệp fail-loud bị vứt và exit code bị nuốt
# ⇒ thay đổi ròng của các chốt dưới đây là event bị VỨT HẲN thay vì ghi bản degrade — đúng
# hình thái lỗi mà chính chúng sinh ra để diệt. Ghi nguyên văn arg bị chặn vào một file cách
# ly để bằng chứng KHÔNG mất, dù stderr có bị vứt hay không. Đây là hàng đợi pháp y, KHÔNG
# phải hàng đợi retry: không ai tự động phát lại, vì payload đã hỏng thì phát lại vẫn hỏng.
# Bản thân việc cách ly không bao giờ được che lỗi gốc ⇒ mọi thứ bọc `|| true`.
# ĐƯỜNG DẪN nằm ở bus/, KHÔNG phải bus/inbox/ (đổi 2026-08-16): mọi reader của bus glob
# `bus/inbox/*.jsonl` KHÔNG lọc theo tên — consolidate.sh, staleness_watch.py, mike_json
# load_jsonl/verify-coverage. Đã đo thật: cho một bản ghi cách ly vào inbox rồi chạy
# `mike_json.py cursor-advance`, nó nuốt gọn rc=0 và short() render ra `- [ts] ?/? — : null`
# ⇒ bằng chứng pháp y BIẾN MẤT khỏi file (cursor đã nhảy) và KB ăn một dòng rác, tức đúng
# thứ hàng đợi này sinh ra để chống. Tên bắt đầu bằng `_` KHÔNG bảo vệ được gì vì không
# reader nào lọc prefix. Không có bản ghi nào từng tồn tại ở đường cũ (file chưa hề được
# tạo) nên đổi chỗ là zero-migration.
_quarantine() {
  # "$@" ở ĐÂY là lý do bị chặn; arg gốc của script lấy từ _ORIG_ARGV (bên trong die()
  # thì "$@" là các TỪ của thông điệp lỗi, không phải arg gốc — đã suýt ghi nhầm).
  # `python3 -c CODE a b` ⇒ sys.argv == ['-c', 'a', 'b'] — sys.argv[0] là '-c', KHÔNG phải
  # tham số đầu. Bản đầu dùng sys.argv[0] làm đường dẫn nên ghi vào một file tên `-c` ở cwd
  # và hàng đợi cách ly rỗng vĩnh viễn; `|| true` nuốt sạch. Đúng lớp lỗi đang đi sửa.
  python3 -c '
import json, os, sys, datetime
qf, reason, args = sys.argv[1], sys.argv[2], sys.argv[3:]
rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "rejected_by": "append_event.sh", "reason": reason,
       "argc": len(args), "argv": args,
       "caller_pid": os.environ.get("_AE_PPID", ""), "job_id": os.environ.get("JOB_ID", "")}
with open(qf, "a", encoding="utf-8") as f:
    # ensure_ascii=True, KHÔNG phải False (arch-review round 3, killer objection). Arg vào
    # đây qua surrogateescape — chính lớp lỗi byte-vs-char mà hàng đợi này sinh ra để bắt.
    # ensure_ascii=False + encoding="utf-8" STRICT ⇒ UnicodeEncodeError ("surrogates not
    # allowed") NGAY tại f.write ⇒ `2>/dev/null || true` nuốt sạch ⇒ file cách ly 0 BYTE
    # trong khi stderr vẫn khẳng định "arg bị chặn đã lưu vào ...", và §5b (người đọc mới)
    # im lặng tuyệt đối vì không có bản ghi nào = BÁO YÊN GIẢ. 28/42 call site vứt stderr
    # nên không còn dấu vết nào khác. ensure_ascii=True escape surrogate thành "\udcxx"
    # thuần ASCII: ghi được, đọc lại được, và giữ nguyên byte gốc cho việc pháp y.
    f.write(json.dumps(rec, ensure_ascii=True) + "\n")
' "$BUS/_rejected.jsonl" "$1" "${_ORIG_ARGV[@]}" 2>/dev/null || true
}
die() {
  mkdir -p "$BUS" 2>/dev/null || true
  _AE_PPID="$PPID" _quarantine "$*"
  echo "append_event.sh: $*" >&2
  echo "append_event.sh: arg bị chặn đã lưu vào $BUS/_rejected.jsonl (stderr có thể bị caller vứt)." >&2
  exit 1
}

if [ "$#" -gt 5 ]; then
  die "nhận $# tham số (tối đa 5) — payload gần như chắc chắn bị shell word-split.
  Thừa: $(printf '%q ' "${@:6}")
  Sửa: bọc payload trong nháy ĐƠN và escape mọi \"'\" bên trong, hoặc bỏ hẳn nháy đơn khỏi text."
fi

# Chốt trace_id: ENFORCE ĐÚNG HÌNH DẠNG mà thông điệp lỗi đã hứa, không chỉ whitelist ký tự.
# Bản whitelist (2026-08-13) để lọt 7/8 giá trị rác trong chính danh sách sự cố của nó —
# `hom`, `nguoi`, `du`, `capacity`, `khoan`, `lai`, `con` đều exit 0 (arch-review
# coord-2026-08-13 required_change #2, tự replay). Kiểm kê bus thật 2026-08-16: 2875/2888
# trace_id đã đúng hình dạng này; 13 cái còn lại CHÍNH LÀ các ca hỏng đang nói tới.
# Vẫn FATAL (không drop im lặng): caller trực tiếp luôn quote lại được. Riêng đường
# PROPAGATE từ dữ liệu bus cũ bất biến thì không quote lại được — nên nó được làm sạch tại
# nguồn ở bin/verify_finding.sh, chứ không nới lỏng chốt này.
case "$trace_id" in
  "" ) : ;;                       # không có trace_id là hợp lệ
  *[[:space:]]* ) die "trace_id chứa khoảng trắng: $(printf '%q' "$trace_id") — dấu hiệu word-split." ;;
esac
if [ -n "$trace_id" ] && ! printf '%s' "$trace_id" \
     | grep -qE '^[A-Za-z0-9_.:-]+_[0-9]{8}_[0-9]{6}$'; then
  die "trace_id SAI HÌNH DẠNG: $(printf '%q' "$trace_id") — phải là <Agent>_<YYYYMMDD>_<HHMMSS>
  (vd Wags_20260816_090511). Giá trị 1 từ như 'nguoi'/'capacity' là dấu hiệu payload bị
  shell word-split và mảnh đuôi rơi vào tham số 5."
fi

# Payload mở đầu bằng { hoặc [ mà không parse được = JSON cụt (bị cắt), KHÔNG phải chuỗi thường.
case "$payload" in
  \{*|\[* )
    python3 -c 'import json,sys; json.loads(sys.argv[1])' "$payload" 2>/dev/null \
      || die "payload bắt đầu bằng '{' hoặc '[' nhưng KHÔNG phải JSON hợp lệ — nhiều khả năng bị cắt cụt.
  Đuôi payload nhận được: ...$(printf '%s' "${payload: -60}")
  Muốn ghi chuỗi thường thì đừng mở đầu bằng { hoặc [." ;;
esac

kbver="$(tr -dc '0-9' < "$ROOT/kb/version.txt" 2>/dev/null || true)"; kbver="${kbver:-0}"
line="$(python3 "$PY" event "$id" "$etype" "$topic" "$payload" "$kbver" "$trace_id")"

mkdir -p "$BUS/inbox"
exec 9>>"$BUS/inbox/$id.jsonl"
flock 9
printf '%s\n' "$line" >&9
echo "appended $etype/$topic for $id"
