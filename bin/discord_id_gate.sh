#!/usr/bin/env bash
# discord_id_gate.sh <file.sh|file.py> [...]
#
# Pre-commit gate — CHẶN CỨNG commit nếu một Discord channel/topic ID viết TRẦN (snowflake
# 18–19 chữ số) xuất hiện trong code, ở ngoài registry kb/discord_channels.json.
#
# WHY (đây là điểm mấu chốt, không phải một quy ước nữa):
# Rò rỉ chéo topic đã tái diễn 4 lần (2026-07-01 DollarBill, 2026-07-06 Taylor multi-topic,
# 2026-07-22 override thành dead-code, 2026-07-22b job-record vs agent-env lệch nhau). Mỗi lần
# đều vá đúng chỗ hỏng rồi vẫn tái phát dưới dạng mới, vì cả 4 lần đều dựa vào CON NGƯỜI NHỚ
# dùng đúng biến/hàm có sẵn. Một ID trần thì KHÔNG KIỂM CHỨNG ĐƯỢC: nhìn một chuỗi 19 chữ số,
# không ai biết tác giả định gửi Trading Daily hay Trading Report, nên
# copy-paste sai là im lặng vĩnh viễn — không test nào bắt, không review nào thấy. Gate này
# biến "nhớ dùng tên" từ quy ước thành ĐIỀU KIỆN CƠ HỌC để commit được.
#
# REGEX: (?<![0-9.])1[0-9]{17,18}(?![0-9.])
#   - Discord snowflake của fleet này là 19 chữ số bắt đầu bằng "15…"; bắt 18–19 chữ số mở đầu
#     bằng 1 là đủ rộng cho ID sinh mới mà không quét trúng số liệu.
#   - Lookaround loại [0-9.] hai đầu: chặn khớp nhầm vào phần thập phân của float dài
#     (vd 0.47273338875796733 trong CSV/nghiên cứu của Taylor) và vào chuỗi số dài hơn.
#   - Đã đo trên toàn repo trước khi chốt: 0 false-positive trong bin/ và hooks/ (mọi khớp
#     đều là ID Discord thật). Cùng kỷ luật "verify trên file thật, đừng đoán" như
#     bin/shellcheck_gate.sh.
#
# PHẠM VI: chỉ code thực thi (bin/*.sh, bin/*.py, hooks/*.sh) — nơi ID quyết định tin nhắn đi
# đâu. Tài liệu (kb/*.md) được phép trích ID để giải thích; chúng không định tuyến gì cả. Giữ
# phạm vi hẹp có chủ đích, theo đúng triết lý "curated, đừng đun sôi đại dương" của
# bin/shellcheck_gate.sh — một rule bắn 2 lần với độ chính xác 100% hơn một rule bắn 200 lần
# với 50%. (Dòng trên KHÔNG được mở đầu bằng "# shellcheck": shellcheck sẽ đọc nhầm thành một
# directive hỏng → SC1072/SC1073 và BỎ LINT cả file này.)
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PATTERN='(?<![0-9.])1[0-9]{17,18}(?![0-9.])'

# File được phép chứa ID trần. Chỉ registry. Thêm entry vào đây là quyết định KIẾN TRÚC —
# phải kèm lý do vì sao chỗ đó không thể dùng tên (và gần như luôn là có thể).
ALLOWLIST=(
  "kb/discord_channels.json"
)

_allowed() {
  local rel="$1" a
  for a in "${ALLOWLIST[@]}"; do [ "$rel" = "$a" ] && return 0; done
  return 1
}

[ "$#" -eq 0 ] && exit 0

BLOCKED=0
for f in "$@"; do
  [ -f "$f" ] || continue
  rel="${f#"$ROOT"/}"
  _allowed "$rel" && continue
  hits="$(grep -PnoH "$PATTERN" "$f" 2>/dev/null || true)"
  [ -z "$hits" ] && continue
  while IFS= read -r h; do
    echo "  🔴 $h  ← Discord ID viết trần [HARD-BLOCK]"
    BLOCKED=$((BLOCKED + 1))
  done <<< "$hits"
done

if [ "$BLOCKED" -gt 0 ]; then
  {
    echo ""
    echo "🔴 discord_id_gate: $BLOCKED chỗ viết Discord ID trần trong code — sửa trước khi commit."
    echo "   Dùng TÊN trong kb/discord_channels.json thay vì ID:"
    echo "     bash : bin/notify_thread.sh \"<msg>\" trading_daily"
    echo "            id=\$(bin/discord_channel.sh trading_daily)"
    echo "     py   : sys.path.insert(0, <bin>); from discord_channels import resolve"
    echo "   Channel mới? Thêm 1 entry vào kb/discord_channels.json rồi dùng tên đó."
    echo "   Lý do gate này tồn tại: kb/incidents/2026-08/2026-08-02-discord-channel-registry.md"
  } >&2
  exit 1
fi
exit 0
