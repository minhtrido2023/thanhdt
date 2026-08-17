#!/usr/bin/env bash
# claim_reply_selfcheck.sh — kiểm tra `bin/jobs.sh claim-reply` (anti-double-reply, F2 2026-08-17).
#
# Cái nó phải chứng minh, không phải "chạy không lỗi":
#   1. Lần claim ĐẦU trên record chưa reply -> exit 0 + replied_at được ghi.
#   2. Lần claim THỨ HAI -> exit 1, KHÔNG đè replied_at cũ.
#   3. N tiến trình claim ĐỒNG THỜI -> đúng 1 cái exit 0 (đây mới là lý do lệnh này tồn tại;
#      mark-replied + is-replied tách rời không qua nổi ca này).
#   4. Record không tồn tại / hỏng -> exit 2, KHÔNG phải 1 (nếu trả 1, lượt wake sẽ im lặng
#      bỏ qua kết quả job — mất việc, không phải chống trùng).
#   5. mark-replied cũ vẫn ăn khớp: đã mark-replied thì claim-reply trả 1.
#
# Chạy trên sandbox riêng (mktemp -d), KHÔNG đụng bus/jobs thật.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
JOBS="$SB/jobs"
mkdir -p "$JOBS"

FAIL=0
assert() { # assert <mô tả> <thực tế> <mong đợi>
  if [ "$2" = "$3" ]; then
    echo "  ok   $1 ($2)"
  else
    echo "  FAIL $1: được '$2', mong đợi '$3'"; FAIL=1
  fi
}
mkjob() { printf '{"job_id":"%s","status":"done"}' "$1" > "$JOBS/$1.json"; }
claim() {
  python3 "$ROOT/bin/mike_json.py" job-claim-reply "$JOBS" "$1" >/dev/null 2>&1
  echo $?
}

# Cửa trước jobs.sh chốt JOBS_DIR = <root>/bus/jobs, nên dựng 1 ROOT giả bằng symlink để test
# cửa trước mà không đụng bus/jobs thật.
FAKE="$SB/fakeroot"
mkdir -p "$FAKE/bin" "$FAKE/bus/jobs"
ln -s "$ROOT/bin/jobs.sh" "$FAKE/bin/jobs.sh"
ln -s "$ROOT/bin/mike_json.py" "$FAKE/bin/mike_json.py"
claim_front() { "$FAKE/bin/jobs.sh" claim-reply "$1" >/dev/null 2>&1; echo $?; }

echo "== CA 1: claim lần đầu trên record chưa reply"
mkjob J1
assert "exit code" "$(claim J1)" "0"
assert "replied_at đã được ghi" \
  "$(python3 -c 'import json,sys;print("yes" if json.load(open(sys.argv[1])).get("replied_at") else "no")' "$JOBS/J1.json")" \
  "yes"

echo "== CA 2: claim lần hai -> exit 1, không đè dấu thời gian cũ"
FIRST="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["replied_at"])' "$JOBS/J1.json")"
assert "exit code" "$(claim J1)" "1"
assert "replied_at giữ nguyên" \
  "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["replied_at"])' "$JOBS/J1.json")" \
  "$FIRST"

echo "== CA 3: 12 tiến trình claim ĐỒNG THỜI -> đúng 1 cái thắng"
mkjob J2
RC_DIR="$SB/rc"; mkdir -p "$RC_DIR"
for i in $(seq 1 12); do
  ( claim J2 > "$RC_DIR/$i" ) &
done
wait
WINNERS="$(grep -lx 0 "$RC_DIR"/* 2>/dev/null | wc -l | tr -d ' ')"
LOSERS="$(grep -lx 1 "$RC_DIR"/* 2>/dev/null | wc -l | tr -d ' ')"
assert "số tiến trình exit 0" "$WINNERS" "1"
assert "số tiến trình exit 1" "$LOSERS" "11"

echo "== CA 4: record không tồn tại / hỏng -> exit 2 (KHÔNG phải 1)"
assert "record thiếu" "$(claim KHONG_TON_TAI)" "2"
printf 'x' > "$JOBS/J3.json"
assert "record hỏng" "$(claim J3)" "2"
assert "record hỏng KHÔNG bị ghi đè" "$(cat "$JOBS/J3.json")" "x"

echo "== CA 5: back-compat — mark-replied cũ vẫn chặn được claim-reply"
mkjob J4
python3 "$ROOT/bin/mike_json.py" job-set "$JOBS" J4 "replied_at=2026-08-17T00:00:00Z" >/dev/null
assert "claim sau mark-replied" "$(claim J4)" "1"

echo "== CA 6: cửa trước bin/jobs.sh truyền đúng exit code (set -e không được nuốt exit 1)"
printf '{"job_id":"J5","status":"done"}' > "$FAKE/bus/jobs/J5.json"
assert "claim đầu qua jobs.sh" "$(claim_front J5)" "0"
assert "claim lại qua jobs.sh" "$(claim_front J5)" "1"
assert "record thiếu qua jobs.sh" "$(claim_front KHONG_CO)" "2"

echo
if [ "$FAIL" -eq 0 ]; then echo "claim_reply_selfcheck: PASS"; else echo "claim_reply_selfcheck: FAIL"; fi
exit "$FAIL"
