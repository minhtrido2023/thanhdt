#!/usr/bin/env bash
# remember.sh — an agent's curated WORKING MEMORY (current priorities / open threads / who
# it's waiting on / next steps). Stored at kb/memory/<id>.md and injected at that agent's
# SessionStart. Unlike the auto-recap (raw tail of the previous transcript), this is durable
# and survives ANY number of restarts — the agent keeps it current on purpose.
#
# Usage:
#   remember.sh <id> "<note>"     append a timestamped bullet (keeps last $MIKE_MEMORY_CAP=12
#                                 hot; phần tràn ĐẨY sang kb/memory/archive/, không xoá)
#   remember.sh <id> --set        replace the whole memory body with stdin (full rewrite)
#   remember.sh <id> --clear      empty it
#   remember.sh <id> --show       print it
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEM="$ROOT/kb/memory"
mkdir -p "$MEM"

id="${1:?usage: remember.sh <agent_id> <note|--set|--clear|--show>}"
shift || true
f="$MEM/$id.md"
# 12, không phải 40 (đổi 2026-08-10). 40 được chọn khi phần tràn bị XOÁ nên phải giữ rộng cho
# an toàn; giờ phần tràn sang archive nên giữ hẹp là an toàn. Taylor ghi ~6 entry/ngày ⇒ 40 =
# gần 1 tuần nhật ký bơm vào MỌI dispatch. 12 ≈ 2 ngày gần nhất, đủ để nối mạch việc.
CAP="${MIKE_MEMORY_CAP:-12}"
header() { printf '# Working memory — %s\n> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của %s.\n\n' "$id" "$id"; }

case "${1:-}" in
  --show)  [ -s "$f" ] && cat "$f" || echo "(working memory trống cho $id)"; exit 0 ;;
  --clear) header > "$f"; echo "cleared working memory for $id"; exit 0 ;;
  --set)
    tmp="$(mktemp)"; { header; cat; printf '\n'; } > "$tmp"; mv -f "$tmp" "$f"
    echo "set working memory for $id"; exit 0 ;;
  "")      echo "usage: remember.sh <agent_id> <note|--set|--clear|--show>" >&2; exit 2 ;;
esac

note="$*"
ts="$(date -u +%FT%TZ)"
[ -s "$f" ] || header > "$f"
printf -- '- [%s] %s\n' "$ts" "$note" >> "$f"

# Cap: giữ file là sổ tay, không thành nhật ký. Ủy quyền cho archive_memory.py — ĐỪNG tự cắt
# tại chỗ (bản cũ làm vậy và sai 2 đường, sửa 2026-08-10):
#   1) `grep '^- ' | tail -n CAP` XOÁ THẲNG phần tràn. Mất vĩnh viễn, không ai biết. Taylor
#      đứng đúng 40/40 nhiều ngày ⇒ mỗi lần ghi là mất 1 dòng cũ, im lặng.
#   2) Nó dựng lại header bằng hàm header() và CHỈ giữ dòng bắt đầu '- ' ⇒ xoá sạch phần HEAD
#      biên tập tay (khối quy tắc / "việc còn treo") và mọi dòng nối tiếp của bullet. Trái
#      ngược hẳn archive_memory.py vốn cam kết "HEAD is ALWAYS preserved verbatim" — hai công
#      cụ cùng sửa một file mà một cái giữ, một cái phá.
# archive_memory.py đúng theo cấu tạo: HEAD nguyên vẹn, entry tràn ĐẨY SANG archive (append-only).
#   --days 0     = entry HÔM NAY luôn ở lại (đang làm dở thì đừng đụng)
#   --keep-open  = '(?!)' regex không bao giờ khớp ⇒ tại đây cap là cap, không có ngoại lệ
#                  "còn mở" (chế độ nới tay đó dành cho cron đêm, xem kb_nightly.sh Phase 1c).
# Fail thì KHÔNG làm gì: file phình thêm là chuyện xử lý được, xoá nhầm thì không.
nb="$(grep -c '^- \[' "$f" 2>/dev/null || echo 0)"
if [ "${nb:-0}" -gt "$CAP" ]; then
  python3 "$ROOT/bin/archive_memory.py" "$f" --keep "$CAP" --days 0 --keep-open '(?!)' --apply \
    >/dev/null 2>&1 || echo "remember.sh: canh bao — khong archive duoc phan tran cua $id (file giu nguyen)" >&2
fi
echo "remembered for $id"
