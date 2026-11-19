#!/usr/bin/env bash
# fund_bench_cron.sh <tên-việc> <lệnh> [đối số...] — vỏ cron cho 3 việc quỹ bước 4 (vnindex_total_return
# --update, nav_sleeve --write, hose_membership_refresh). N-c vòng 2 (arch-review job Taylor_20261014_091148):
# trước đây lỗi chỉ nằm trong logs/*.log, không ai đọc ⇒ chuỗi benchmark đứng im mà báo cáo tuần chỉ thấy
# "chưa có số" vào thứ Bảy.
#
#   rc=0 ⇒ im lặng; riêng dòng '📋 ...' (diff bảng sàn HOSE) thì chuyển nguyên văn lên Trading Daily,
#          và JSON có khoá "seal_blocked" (seal-guard G1/G4 giữ dòng provisional) ⇒ báo 🔒 kèm bằng chứng.
#   rc≠0 ⇒ báo Trading Daily: tên việc, rc, và 8 dòng CUỐI đầu ra thật của lệnh (§29 — trích bằng chứng,
#          không đoán nguyên nhân). rc=2/3 của --update là "từ chối dựng"/"chưa có số" — vẫn báo, vì chuỗi
#          không tiến lên là việc người đọc phải biết trước thứ Bảy.
# Đầu ra lệnh vẫn đi stdout/stderr như cũ (cron >> log). Gửi Discord lỗi ⇒ in NOTIFY_FAILED ra stderr.
# Selfcheck: fund_bench_cron_selfcheck.py (NOTIFY_CMD trỏ stub, không gửi gì thật).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOTIFY_CMD="${NOTIFY_CMD:-$ROOT/bin/notify_thread.sh}"
CHANNEL="${FUND_BENCH_CHANNEL:-trading_daily}"

if [ "$#" -lt 2 ]; then
  echo "dùng: fund_bench_cron.sh <tên-việc> <lệnh> [đối số...]" >&2
  exit 64
fi
JOB="$1"
shift

OUT="$(mktemp)" || { echo "fund_bench_cron: mktemp lỗi — không chạy $JOB" >&2; exit 70; }
trap 'rm -f "$OUT"' EXIT

"$@" >"$OUT" 2>&1
RC=$?
cat "$OUT"

notify() {
  if ! "$NOTIFY_CMD" "$1" "$CHANNEL"; then
    echo "NOTIFY_FAILED: không gửi được cảnh báo $JOB lên $CHANNEL" >&2
    return 1
  fi
}

# Báo MỘT LẦN/ngày (ICT) cho mỗi tập khoá: alert_once <khoá> <nội dung>. Dấu đã-gửi chỉ ghi khi notify thành công
# (gửi hỏng ⇒ lần cron sau thử lại). Thư mục dấu ghi đè được bằng FUND_BENCH_STATE_DIR (selfcheck).
alert_once() {
  local dir="${FUND_BENCH_STATE_DIR:-$ROOT/state}" day h
  day="$(TZ='Asia/Ho_Chi_Minh' date +%F)"
  h="$(printf '%s' "$1" | md5sum | cut -c1-12)"
  mkdir -p "$dir" 2>/dev/null
  [ -e "$dir/fund_bench_alert_${JOB}_${day}_${h}" ] && return 0
  if notify "$2"; then : >"$dir/fund_bench_alert_${JOB}_${day}_${h}" 2>/dev/null; fi
}

if [ "$RC" -ne 0 ]; then
  TAIL="$(tail -n 8 "$OUT")"
  # Tiêu đề theo họ việc (§29: không gán nguyên nhân/hệ quả của việc khác). Mặc định = chuỗi benchmark quỹ bước 4 (NGUYÊN VĂN
  # như trước); dcf_rstar_* = cache r* của dòng hiển thị DCF.
  case "$JOB" in
    dcf_rstar_*)
      HEAD="🔴 **DCF r* — $JOB lỗi (rc=$RC)** — cache r* của dòng hiển thị DCF không được làm mới/không qua kiểm hạn (display-only, KHÔNG đổi FV/phân loại/lệnh); dòng 'r* thị trường' sẽ in \"không có dữ liệu\" khi cache quá 45 ngày. Đầu ra thật (8 dòng cuối):" ;;
    *)
      HEAD="🔴 **Quỹ bước 4 — $JOB lỗi (rc=$RC)** — chuỗi benchmark/bot KHÔNG được cập nhật lần này; bảng 3.2 sẽ in \"chưa có số\" nếu không sửa trước báo cáo tuần. Đầu ra thật (8 dòng cuối):" ;;
  esac
  notify "${HEAD}
\`\`\`
${TAIL:-(lệnh không in gì)}
\`\`\`"
else
  DIFF="$(grep -F '📋' "$OUT")"
  if [ -n "$DIFF" ]; then
    notify "$DIFF"
  fi
  # --update rc=0 nhưng seal-guard (G1/G4) giữ dòng ở provisional ⇒ JSON có khoá "seal_blocked" (chỉ xuất
  # hiện khi khác rỗng). Không báo thì chuỗi đứng ở provisional mà không ai biết cần ack/chờ BQ lấp.
  SEAL_LINE="$(grep -F '"seal_blocked"' "$OUT" | head -n 1)"
  if [ -n "$SEAL_LINE" ]; then
    SEAL="$(printf '%s' "$SEAL_LINE" | grep -o '"seal_blocked".*' | cut -c1-900)"
    # Cặp giá trị CẦN ACK (ngày + n_prev/n hoặc mc_prev/mc) đặt LÊN ĐẦU: cắt 900 byte ở cuối có thể làm mất nó.
    PAIRS="$(printf '%s' "$SEAL_LINE" | grep -oP 'G4: \K\d{4}-\d{2}-\d{2}(?=[^"]*\((?:mc_prev|n_prev)=\d+, (?:mc|n)=\d+\))|\((?:mc_prev|n_prev)=\d+, (?:mc|n)=\d+\)' | paste -d' ' - - | tr -d '()')"
    notify "🔒 **Quỹ bước 4 — $JOB: seal bị chặn** — dòng chuỗi benchmark KHÔNG được niêm phong (G1/G4 nổ chưa ack); cần người xác nhận ở vnindex_tr_acks.json (mục G4 / G4_MC, đúng giá trị đã xem) hoặc chờ BQ lấp dữ liệu. Cảnh báo lặp mỗi ngày T3-T7 tới khi dòng được seal hoặc ack.
Cặp cần ack (ngày + giá trị): ${PAIRS:-(không trích được — đọc bằng chứng bên dưới)}
Bằng chứng (cắt 900 ký tự):
\`\`\`
${SEAL}
\`\`\`"
  fi
  # G8_NEW chưa ack ở dòng provisional ("g8_new_open") và/hoặc VERIFY_SEALED lệch rổ ("sealed_drift_warnings"):
  # --update vẫn rc=0 nhưng ô TR sắp/đã thành "chưa có số", hoặc dòng sealed lệch dữ liệu hiện tại. Một tin/ngày/tập
  # mã (alert_once). Nội dung trích từ JSON của --update, không đoán nguyên nhân (§29).
  JSON_LINE="$(grep -E '"(g8_new_open|sealed_drift_warnings)"' "$OUT" | head -n 1)"
  if [ -n "$JSON_LINE" ]; then
    ALERT="$(printf '%s' "$JSON_LINE" | python3 -I -c '
import json, sys
try:
    r = json.loads(sys.stdin.read())
except ValueError:
    sys.exit(0)
key, out = [], []
for e in r.get("g8_new_open") or []:
    key.append("%s:%s" % (e["ticker"], e["cause"]))
    out.append("%s (%s, %s phiên %s→%s)" % (e["ticker"], "OShares rỗng" if e["cause"] == "osh" else "ticker không có dòng", e["sessions"], e["first"], e["last"]))
if out:
    msg = "⚠️ **Quỹ bước 4 — G8_NEW chưa ack:** " + "; ".join(out) + ". Kỳ báo cáo chứa các phiên này in \"chưa có số\" ở ô VN-Index có cổ tức; cần BQ lấp hoặc người xác nhận ở vnindex_tr_acks.json mục G8_NEW. Báo một lần/ngày/tập mã."
else:
    msg = ""
dr = r.get("sealed_drift_warnings") or []
if dr:
    key.append("drift:" + ",".join(w.split(":")[0] for w in dr))
    msg += ("\n" if msg else "") + "⚠️ **Quỹ bước 4 — VERIFY_SEALED lệch rổ (không chặn):** " + " | ".join(dr)[:600]
if key:
    print("\x1f".join(sorted(key)) + "\x1e" + msg)
' 2>/dev/null)"
    if [ -n "$ALERT" ]; then
      alert_once "${ALERT%%$'\x1e'*}" "${ALERT#*$'\x1e'}"
    fi
  fi
fi
exit "$RC"
