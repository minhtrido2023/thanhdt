#!/usr/bin/env bash
# fund_bench_cron.sh <tên-việc> <lệnh> [đối số...] — vỏ cron cho 3 việc quỹ bước 4 (vnindex_total_return
# --update, nav_sleeve --write, hose_membership_refresh). N-c vòng 2 (arch-review job Taylor_20261014_091148):
# trước đây lỗi chỉ nằm trong logs/*.log, không ai đọc ⇒ chuỗi benchmark đứng im mà báo cáo tuần chỉ thấy
# "chưa có số" vào thứ Bảy.
#
#   rc=0 ⇒ im lặng; riêng dòng '📋 ...' (diff bảng sàn HOSE) thì chuyển nguyên văn lên Trading Daily.
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
  fi
}

if [ "$RC" -ne 0 ]; then
  TAIL="$(tail -n 8 "$OUT")"
  notify "🔴 **Quỹ bước 4 — $JOB lỗi (rc=$RC)** — chuỗi benchmark/bot KHÔNG được cập nhật lần này; bảng 3.2 sẽ in \"chưa có số\" nếu không sửa trước báo cáo tuần. Đầu ra thật (8 dòng cuối):
\`\`\`
${TAIL:-(lệnh không in gì)}
\`\`\`"
else
  DIFF="$(grep -F '📋' "$OUT")"
  if [ -n "$DIFF" ]; then
    notify "$DIFF"
  fi
fi
exit "$RC"
